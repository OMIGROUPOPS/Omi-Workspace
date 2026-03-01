#!/usr/bin/env python3
"""
position_report.py — Clean position table with hedge verification and portfolio tracking.

Shows all open positions across Kalshi and PM with:
- Hedge status (hedged, same-side, orphan, size mismatch)
- Entry prices (VWAP from fills for K, SDK cost for PM)
- Gross and net P&L per position
- Full portfolio valuation (cash + position mark-to-market)
- Net P&L since starting balance

Run standalone: python3 position_report.py
Run via executor: python3 arb_executor_ws.py --audit
Cron mode: python3 position_report.py --cron
"""
import asyncio
import json
import os
import sys
import argparse
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from arb_executor_v7 import KalshiAPI, PolymarketUSAPI
from polymarket_us import AsyncPolymarketUS
import aiohttp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORTFOLIO_LOG_PATH = os.path.join(BASE_DIR, 'portfolio_log.json')
DEPOSITS_PATH = os.path.join(BASE_DIR, 'deposits.json')
KALSHI_FEE_CENTS = 2  # per contract per side


def load_deposit_history():
    """Load deposit/withdrawal history from deposits.json.
    Returns (starting_total, net_deposits) where net_deposits = deposits - withdrawals."""
    try:
        with open(DEPOSITS_PATH) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return 317.77, 600.00  # Hardcoded fallback

    starting = data.get('starting_balances', {}).get('total', 317.77)
    deposits = sum(d.get('amount', 0) for d in data.get('deposits', []))
    withdrawals = sum(w.get('amount', 0) for w in data.get('withdrawals', []))
    return starting, deposits - withdrawals


def _extract_cost(raw):
    """Extract float from PM cost field (can be dict or scalar)."""
    if isinstance(raw, dict):
        return float(raw.get('amount', raw.get('value', 0)))
    try:
        return float(raw)
    except (ValueError, TypeError):
        return 0.0


async def fetch_kalshi_fills(kalshi_api, session):
    """Fetch all Kalshi fills and compute VWAP entry prices per ticker."""
    fills_by_ticker = defaultdict(lambda: {
        "fills": [],
        "yes_entry_qty": 0, "yes_entry_cost": 0,
        "no_entry_qty": 0, "no_entry_cost": 0,
        "yes_exit_qty": 0, "yes_exit_cost": 0,
        "no_exit_qty": 0, "no_exit_cost": 0,
    })

    cursor = None
    page = 0
    while True:
        path = '/trade-api/v2/portfolio/fills?limit=100'
        if cursor:
            path += f'&cursor={cursor}'
        try:
            async with session.get(
                f'{kalshi_api.BASE_URL}{path}',
                headers=kalshi_api._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status != 200:
                    break
                data = await r.json()
        except Exception:
            break

        fills = data.get('fills', [])
        if not fills:
            break

        for fl in fills:
            ticker = fl.get('ticker', '')
            if not ticker:
                continue
            side = fl.get('side', '')
            action = fl.get('action', '')
            count = int(fl.get('count', 0))
            yes_price = int(fl.get('yes_price', 0))
            no_price = int(fl.get('no_price', 100 - yes_price))

            entry = fills_by_ticker[ticker]
            entry["fills"].append({"side": side, "action": action, "count": count,
                                   "yes_price": yes_price, "no_price": no_price})

            if side == 'yes':
                if action == 'buy':
                    entry["yes_entry_qty"] += count
                    entry["yes_entry_cost"] += count * yes_price
                else:
                    entry["yes_exit_qty"] += count
                    entry["yes_exit_cost"] += count * yes_price
            elif side == 'no':
                if action == 'buy':
                    entry["no_entry_qty"] += count
                    entry["no_entry_cost"] += count * no_price
                else:
                    entry["no_exit_qty"] += count
                    entry["no_exit_cost"] += count * no_price

        cursor = data.get('cursor', None)
        page += 1
        if not cursor or page > 20:
            break

    result = {}
    for ticker, entry in fills_by_ticker.items():
        if not entry["fills"]:
            continue
        yes_vwap = entry["yes_entry_cost"] / entry["yes_entry_qty"] if entry["yes_entry_qty"] > 0 else 0
        no_all_qty = entry["no_entry_qty"] + entry["no_exit_qty"]
        no_all_cost = entry["no_entry_cost"] + entry["no_exit_cost"]
        if entry["yes_exit_qty"] > 0:
            avg_yes_sell = entry["yes_exit_cost"] / entry["yes_exit_qty"]
            no_all_qty += entry["yes_exit_qty"]
            no_all_cost += entry["yes_exit_qty"] * (100 - avg_yes_sell)
        no_vwap = no_all_cost / no_all_qty if no_all_qty > 0 else 0
        result[ticker] = {"yes_vwap": round(yes_vwap, 1), "no_vwap": round(no_vwap, 1),
                          "yes_entry_qty": entry["yes_entry_qty"], "no_entry_qty": no_all_qty}
    return result


async def fetch_kalshi_orderbook(kalshi_api, session, ticker):
    """Fetch current best bid/ask for a Kalshi ticker."""
    path = f'/trade-api/v2/markets/{ticker}/orderbook'
    try:
        async with session.get(
            f'{kalshi_api.BASE_URL}{path}',
            headers=kalshi_api._headers('GET', path),
            timeout=aiohttp.ClientTimeout(total=5)
        ) as r:
            if r.status != 200:
                return None, None
            data = await r.json()
            ob = data.get('orderbook', {})
            yes_bids = ob.get('yes', [])
            no_bids = ob.get('no', [])
            best_yes_bid = yes_bids[0][0] if yes_bids else None
            best_no_bid = no_bids[0][0] if no_bids else None
            return best_yes_bid, best_no_bid
    except Exception:
        return None, None


async def run_report(quiet=False):
    """Run position report and return structured result."""
    log = lambda *a, **kw: (print(*a, **kw) if not quiet else None)

    # Init APIs
    kalshi_key = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
    try:
        with open(os.path.join(BASE_DIR, 'kalshi.pem')) as f:
            kalshi_pk = f.read()
    except FileNotFoundError:
        log("[ERROR] kalshi.pem not found")
        return None

    pm_key = os.getenv('PM_US_API_KEY')
    pm_secret = os.getenv('PM_US_SECRET_KEY') or os.getenv('PM_US_SECRET')
    if not pm_key or not pm_secret:
        log("[ERROR] Missing PM US credentials")
        return None

    kalshi_api = KalshiAPI(kalshi_key, kalshi_pk)
    pm_sdk = AsyncPolymarketUS(key_id=pm_key, secret_key=pm_secret)

    async with aiohttp.ClientSession() as session:
        # 1. Fetch all data in parallel where possible
        k_positions = await kalshi_api.get_positions(session) or {}
        k_fills = await fetch_kalshi_fills(kalshi_api, session)
        k_balance = await kalshi_api.get_balance(session)

        # PM positions via SDK
        pm_positions = {}
        try:
            pm_resp = await pm_sdk.portfolio.positions()
            for slug, pos in pm_resp.get('positions', {}).items():
                net = int(pos.get('netPosition', 0))
                if net != 0:
                    pm_positions[slug] = pos
        except Exception as e:
            log(f"[ERROR] PM SDK positions failed: {e}")

        # PM balance
        pm_balance = None
        try:
            pm_api_fallback = PolymarketUSAPI(pm_key, pm_secret)
            pm_balance = await pm_api_fallback.get_balance(session)
        except Exception:
            pass

        # Load trades.json
        trades_path = os.path.join(BASE_DIR, 'trades.json')
        trades = []
        if os.path.exists(trades_path):
            with open(trades_path) as f:
                trades = json.load(f)

        active_trades = [t for t in trades if t.get('status') in ('SUCCESS', 'HEDGED', 'LIVE', 'K_FIRST_SUCCESS')
                         or (t.get('raw_status') in ('SUCCESS', 'HEDGED', 'K_FIRST_SUCCESS')
                             and t.get('hedged', False))]

        # Fetch K orderbook prices for position valuation (batch)
        k_market_prices = {}
        for ticker in k_positions:
            yes_bid, no_bid = await fetch_kalshi_orderbook(kalshi_api, session, ticker)
            k_market_prices[ticker] = {'yes_bid': yes_bid, 'no_bid': no_bid}

    # ═════════════════════════════════════════════════════════════════
    # BUILD POSITION TABLE
    # ═════════════════════════════════════════════════════════════════
    rows = []
    flags = {"same_side": [], "orphan": [], "size_mismatch": []}
    total_locked_gross = 0
    total_locked_net = 0
    total_unhedged_cents = 0
    k_position_value = 0
    pm_position_value = 0

    # Track which K/PM positions are matched via trades.json
    matched_k_tickers = set()
    matched_pm_slugs = set()

    for t in active_trades:
        k_ticker = t.get('kalshi_ticker', '')
        pm_slug_t = t.get('pm_slug', '')
        team = t.get('team', '???')
        direction = t.get('direction', '')

        k_pos = k_positions.get(k_ticker)
        pm_pos_data = pm_positions.get(pm_slug_t)

        if not k_pos and not pm_pos_data:
            continue  # Both settled

        matched_k_tickers.add(k_ticker)
        matched_pm_slugs.add(pm_slug_t)

        # K side info
        k_side = ''
        k_qty = 0
        k_entry = 0
        if k_pos:
            k_qty = abs(k_pos.position)
            k_side = 'YES' if k_pos.position > 0 else 'NO'
            fill_data = k_fills.get(k_ticker, {})
            if k_side == 'YES' and fill_data.get('yes_vwap', 0) > 0:
                k_entry = fill_data['yes_vwap']
            elif k_side == 'NO' and fill_data.get('no_vwap', 0) > 0:
                k_entry = fill_data['no_vwap']
            else:
                k_entry = k_pos.market_exposure / k_qty if k_qty > 0 else 0

        # PM side info
        pm_side = ''
        pm_qty = 0
        pm_entry = 0
        if pm_pos_data:
            net = int(pm_pos_data.get('netPosition', 0))
            pm_qty = abs(net)
            cost = _extract_cost(pm_pos_data.get('cost', 0))
            pm_entry = round(cost / pm_qty * 100, 1) if pm_qty > 0 else 0
            # Resolve PM YES team from trade record (not SDK metadata)
            _t_dir = t.get('direction', '')
            _t_ck = t.get('cache_key', '')
            if _t_dir and ':' in _t_ck:
                _cache_teams = _t_ck.split(':')[1].split('-') if ':' in _t_ck else []
                if _t_dir == 'BUY_PM_SELL_K' and len(_cache_teams) == 2:
                    pm_side = team  # PM YES same team
                elif _t_dir == 'BUY_K_SELL_PM' and len(_cache_teams) == 2:
                    pm_side = _cache_teams[1] if _cache_teams[0] == team else _cache_teams[0]
                else:
                    meta = pm_pos_data.get('marketMetadata', {})
                    team_info = meta.get('team', {})
                    pm_side = team_info.get('abbreviation', '')[:6].upper() or team
            else:
                meta = pm_pos_data.get('marketMetadata', {})
                team_info = meta.get('team', {})
                pm_side = team_info.get('abbreviation', '')[:6].upper() or team

        # Hedge analysis
        hedged = False
        hedge_label = ''
        gross_cents = 0
        net_cents = 0

        if k_pos and pm_pos_data and k_entry and pm_entry:
            combined = k_entry + pm_entry
            gross_cents = (100 - combined) * min(k_qty, pm_qty)
            fee_total = KALSHI_FEE_CENTS * min(k_qty, pm_qty) * 2
            net_cents = gross_cents - fee_total

            if combined < 90:
                hedge_label = 'SAME!'
                flags["same_side"].append(team)
            elif combined > 102:
                hedge_label = 'NEG'
                flags["same_side"].append(team)
            else:
                hedge_label = 'YES'
                hedged = True
                total_locked_gross += gross_cents
                total_locked_net += net_cents

            if k_qty != pm_qty:
                flags["size_mismatch"].append(f"{team}(K{k_qty}/PM{pm_qty})")
        elif k_pos and not pm_pos_data:
            hedge_label = 'K-ONLY'
            total_unhedged_cents += k_entry * k_qty if k_entry else 0
        elif pm_pos_data and not k_pos:
            hedge_label = 'PM-ONLY'
            total_unhedged_cents += pm_entry * pm_qty if pm_entry else 0

        size_match = 'YES' if k_qty == pm_qty and k_qty > 0 else ('—' if not k_pos or not pm_pos_data else 'NO')

        rows.append({
            'team': team,
            'k_side': k_side or '—',
            'k_qty': k_qty,
            'k_entry': k_entry,
            'pm_side': pm_side or '—',
            'pm_qty': pm_qty,
            'pm_entry': pm_entry,
            'hedged': hedge_label,
            'size_match': size_match,
            'gross': gross_cents,
            'net': net_cents,
        })

    # Orphan detection: positions not in trades.json
    for ticker, pos in k_positions.items():
        if ticker not in matched_k_tickers:
            k_qty = abs(pos.position)
            k_side = 'YES' if pos.position > 0 else 'NO'
            fill_data = k_fills.get(ticker, {})
            k_entry = fill_data.get('yes_vwap', 0) if k_side == 'YES' else fill_data.get('no_vwap', 0)
            short_ticker = ticker.split('-')[-1] if '-' in ticker else ticker
            flags["orphan"].append(f"K:{short_ticker}")
            total_unhedged_cents += k_entry * k_qty if k_entry else 0
            rows.append({
                'team': short_ticker[:6],
                'k_side': k_side, 'k_qty': k_qty, 'k_entry': k_entry,
                'pm_side': '—', 'pm_qty': 0, 'pm_entry': 0,
                'hedged': 'ORPHAN', 'size_match': '—',
                'gross': 0, 'net': 0,
            })

    for slug, pos in pm_positions.items():
        if slug not in matched_pm_slugs:
            net = int(pos.get('netPosition', 0))
            pm_qty = abs(net)
            cost = _extract_cost(pos.get('cost', 0))
            pm_entry = round(cost / pm_qty * 100, 1) if pm_qty > 0 else 0
            meta = pos.get('marketMetadata', {})
            team_info = meta.get('team', {})
            pm_side = team_info.get('abbreviation', slug[:6]).upper()
            flags["orphan"].append(f"PM:{pm_side}")
            total_unhedged_cents += pm_entry * pm_qty if pm_entry else 0
            rows.append({
                'team': pm_side[:6],
                'k_side': '—', 'k_qty': 0, 'k_entry': 0,
                'pm_side': pm_side, 'pm_qty': pm_qty, 'pm_entry': pm_entry,
                'hedged': 'ORPHAN', 'size_match': '—',
                'gross': 0, 'net': 0,
            })

    # ═════════════════════════════════════════════════════════════════
    # PORTFOLIO VALUATION
    # ═════════════════════════════════════════════════════════════════
    # K position value: mark-to-market using current orderbook
    for ticker, pos in k_positions.items():
        prices = k_market_prices.get(ticker, {})
        qty = abs(pos.position)
        if pos.position > 0:  # YES position — value at best bid
            bid = prices.get('yes_bid')
            if bid is not None:
                k_position_value += bid * qty  # cents
            else:
                fill_data = k_fills.get(ticker, {})
                k_position_value += fill_data.get('yes_vwap', 50) * qty
        else:  # NO position — value at best no bid (100 - yes ask approximated)
            bid = prices.get('no_bid')
            if bid is not None:
                k_position_value += bid * qty
            else:
                fill_data = k_fills.get(ticker, {})
                k_position_value += fill_data.get('no_vwap', 50) * qty

    k_position_value_dollars = k_position_value / 100

    # PM position value: qty × cost-based entry (SDK doesn't expose live bid easily)
    for slug, pos in pm_positions.items():
        net = int(pos.get('netPosition', 0))
        qty = abs(net)
        cash_value = _extract_cost(pos.get('cashValue', 0))
        if cash_value > 0:
            pm_position_value += cash_value  # already in dollars
        else:
            cost = _extract_cost(pos.get('cost', 0))
            pm_position_value += cost  # fallback to cost basis

    k_cash = k_balance if k_balance is not None else 0
    pm_cash = pm_balance if pm_balance is not None else 0
    k_total = k_cash + k_position_value_dollars
    pm_total = pm_cash + pm_position_value
    combined_portfolio = k_total + pm_total

    # True P&L = current portfolio - starting balance - net deposits
    starting_balance, net_deposits = load_deposit_history()
    total_capital_in = starting_balance + net_deposits
    net_pnl = combined_portfolio - total_capital_in

    # ═════════════════════════════════════════════════════════════════
    # PRINT REPORT
    # ═════════════════════════════════════════════════════════════════
    if not quiet:
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        print(f"\n{'='*95}")
        print(f"  POSITION REPORT — {now}")
        print(f"{'='*95}")

        # Table header
        print(f"  {'Game':<7s} {'K Side':<7s} {'K Qty':>5s} {'K Entry':>8s} {'PM YES':<8s} "
              f"{'PM Qty':>6s} {'PM Entry':>8s} {'Hedged?':<8s} {'Match?':<7s} {'Gross':>6s} {'Net':>6s}")
        print(f"  {'─'*7} {'─'*7} {'─'*5} {'─'*8} {'─'*8} {'─'*6} {'─'*8} {'─'*8} {'─'*7} {'─'*6} {'─'*6}")

        for r in rows:
            k_entry_str = f"{r['k_entry']:.0f}c" if r['k_entry'] else '—'
            pm_entry_str = f"{r['pm_entry']:.0f}c" if r['pm_entry'] else '—'
            gross_str = f"{r['gross']:.0f}c" if r['gross'] != 0 else '—'
            net_str = f"{r['net']:.0f}c" if r['net'] != 0 else '—'
            print(f"  {r['team']:<7s} {r['k_side']:<7s} {r['k_qty']:>5d} {k_entry_str:>8s} "
                  f"{r['pm_side']:<8s} {r['pm_qty']:>6d} {pm_entry_str:>8s} "
                  f"{r['hedged']:<8s} {r['size_match']:<7s} {gross_str:>6s} {net_str:>6s}")

        # Flags
        print(f"\n  {'─'*90}")
        flag_parts = []
        if flags["same_side"]:
            flag_parts.append(f"!! SAME-SIDE: {', '.join(flags['same_side'])}")
        if flags["orphan"]:
            flag_parts.append(f"!! ORPHAN: {', '.join(flags['orphan'])}")
        if flags["size_mismatch"]:
            flag_parts.append(f"!! SIZE-MISMATCH: {', '.join(flags['size_mismatch'])}")
        if flag_parts:
            for fp in flag_parts:
                print(f"  {fp}")
        else:
            print(f"  No flags — all positions clean")

        # Portfolio summary
        print(f"\n  {'─'*90}")
        print(f"  K Cash: ${k_cash:.2f}   K Positions: ${k_position_value_dollars:.2f}   K Total: ${k_total:.2f}")
        print(f"  PM Cash: ${pm_cash:.2f}  PM Positions: ${pm_position_value:.2f}   PM Total: ${pm_total:.2f}")
        print(f"  Combined Portfolio: ${combined_portfolio:.2f}")
        print(f"  Starting Balance (Feb 15): ${starting_balance:.2f}")
        print(f"  Total Deposits: ${net_deposits:.2f}   Total Capital In: ${total_capital_in:.2f}")
        pnl_sign = '+' if net_pnl >= 0 else ''
        print(f"  True P&L: {pnl_sign}${net_pnl:.2f}  ({net_pnl/total_capital_in*100:+.1f}%)")
        print(f"  Locked Profit: ${total_locked_gross/100:.2f}   "
              f"Net After Fees: ${total_locked_net/100:.2f}   "
              f"Unhedged Exposure: ${total_unhedged_cents/100:.2f}")
        print(f"{'='*95}\n")

    # Build result dict
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "positions": rows,
        "flags": flags,
        "portfolio": {
            "k_cash": round(k_cash, 2),
            "k_positions": round(k_position_value_dollars, 2),
            "k_total": round(k_total, 2),
            "pm_cash": round(pm_cash, 2),
            "pm_positions": round(pm_position_value, 2),
            "pm_total": round(pm_total, 2),
            "combined": round(combined_portfolio, 2),
            "starting_balance": round(starting_balance, 2),
            "net_deposits": round(net_deposits, 2),
            "total_capital_in": round(total_capital_in, 2),
            "net_pnl": round(net_pnl, 2),
        },
        "locked_profit_cents": round(total_locked_gross, 1),
        "locked_net_cents": round(total_locked_net, 1),
        "unhedged_exposure_cents": round(total_unhedged_cents, 1),
    }

    return result


def save_portfolio_log(result):
    """Append portfolio snapshot to portfolio_log.json (capped at 500 entries)."""
    if not result:
        return
    entry = {
        "timestamp": result["timestamp"],
        **result["portfolio"],
        "locked_profit_cents": result["locked_profit_cents"],
        "unhedged_exposure_cents": result["unhedged_exposure_cents"],
        "position_count": len(result["positions"]),
        "flags": {k: len(v) for k, v in result["flags"].items()},
    }

    log = []
    if os.path.exists(PORTFOLIO_LOG_PATH):
        try:
            with open(PORTFOLIO_LOG_PATH) as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []

    log.append(entry)
    if len(log) > 500:
        log = log[-500:]

    with open(PORTFOLIO_LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)


async def main_async(args):
    result = await run_report(quiet=args.cron)
    if result:
        save_portfolio_log(result)
        if args.json:
            print(json.dumps(result, indent=2))
        if args.cron:
            # Exit code 2 if any same-side or orphan flags
            flag_count = len(result["flags"].get("same_side", [])) + len(result["flags"].get("orphan", []))
            if flag_count > 0:
                sys.exit(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Position Report — hedge status + portfolio valuation')
    parser.add_argument('--cron', action='store_true', help='Cron mode: quiet output, save JSON log')
    parser.add_argument('--json', action='store_true', help='Print JSON result to stdout')
    args = parser.parse_args()

    asyncio.run(main_async(args))
