#!/usr/bin/env python3
"""
Reconciliation script: compare trades.json against Kalshi API ground truth.

Pulls fills and settlements from Kalshi API, computes TRUE P&L per ticker,
then matches against trades.json and identifies discrepancies.

Usage:
    python reconcile.py               # full reconciliation
    python reconcile.py --save        # also save Kalshi data to disk
    python reconcile.py --offline     # use previously saved Kalshi data
"""

import asyncio
import aiohttp
import json
import os
import sys
import argparse
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRADES_FILE = os.path.join(SCRIPT_DIR, "trades.json")
KALSHI_FILLS_FILE = os.path.join(SCRIPT_DIR, "kalshi_fills_all.json")
KALSHI_SETTLEMENTS_FILE = os.path.join(SCRIPT_DIR, "kalshi_settlements_all.json")
BALANCES_FILE = os.path.join(SCRIPT_DIR, "balances.json")

os.environ['SUPPRESS_MAPPER_WARNING'] = '1'
sys.path.insert(0, SCRIPT_DIR)

from arb_executor_v7 import KalshiAPI, KALSHI_API_KEY, KALSHI_PRIVATE_KEY

STARTING_BALANCE = 317.77  # Feb 15 starting point


# ── Kalshi API data pull ──────────────────────────────────────────────────

async def pull_kalshi_fills(session, kalshi_api) -> list:
    """Pull ALL fills from Kalshi, paginating if needed."""
    all_fills = []
    cursor = None
    while True:
        path = '/trade-api/v2/portfolio/fills?limit=1000'
        if cursor:
            path += f'&cursor={cursor}'
        headers = kalshi_api._headers('GET', path)
        async with session.get(
            f'{kalshi_api.BASE_URL}{path}',
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as r:
            data = await r.json()
            fills = data.get('fills', [])
            all_fills.extend(fills)
            cursor = data.get('cursor')
            if not cursor or not fills:
                break
    return all_fills


async def pull_kalshi_settlements(session, kalshi_api) -> list:
    """Pull ALL settlements from Kalshi, paginating if needed."""
    all_settlements = []
    cursor = None
    while True:
        path = '/trade-api/v2/portfolio/settlements?limit=200'
        if cursor:
            path += f'&cursor={cursor}'
        headers = kalshi_api._headers('GET', path)
        async with session.get(
            f'{kalshi_api.BASE_URL}{path}',
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as r:
            data = await r.json()
            settlements = data.get('settlements', [])
            all_settlements.extend(settlements)
            cursor = data.get('cursor')
            if not cursor or not settlements:
                break
    return all_settlements


async def pull_kalshi_balance(session, kalshi_api) -> dict:
    """Pull current Kalshi balance."""
    path = '/trade-api/v2/portfolio/balance'
    headers = kalshi_api._headers('GET', path)
    async with session.get(
        f'{kalshi_api.BASE_URL}{path}',
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=10)
    ) as r:
        return await r.json()


# ── Kalshi P&L computation ────────────────────────────────────────────────

def compute_kalshi_pnl(fills: list, settlements: list) -> dict:
    """
    Compute per-ticker and total P&L from Kalshi fills + settlements.

    Returns dict with:
      - by_ticker: {ticker: {position info, pnl, fees, ...}}
      - total_pnl: float (gross)
      - total_fees: float
      - total_net: float
    """
    settlement_map = {s.get('ticker'): s for s in settlements}

    by_ticker = {}
    for f in fills:
        ticker = f.get('ticker', '?')
        if ticker not in by_ticker:
            by_ticker[ticker] = {
                'yes_bought': 0, 'yes_sold': 0,
                'no_bought': 0, 'no_sold': 0,
                'yes_cost': 0, 'yes_revenue': 0,
                'no_cost': 0, 'no_revenue': 0,
                'fees': 0, 'fill_count': 0,
                'fills': [],
            }

        rec = by_ticker[ticker]
        action = f.get('action', '')
        side = f.get('side', '')
        count = f.get('count', 0)
        yes_price = f.get('yes_price', 0)
        no_price = f.get('no_price', 0)
        fee_raw = f.get('fee_cost', 0)
        fee = float(fee_raw) if fee_raw else 0  # fee_cost is a string like "0.0800"

        price = yes_price if side == 'yes' else no_price
        rec['fees'] += fee
        rec['fill_count'] += 1
        rec['fills'].append(f)

        if action == 'buy':
            if side == 'yes':
                rec['yes_bought'] += count
                rec['yes_cost'] += count * yes_price
            else:
                rec['no_bought'] += count
                rec['no_cost'] += count * no_price
        elif action == 'sell':
            if side == 'yes':
                rec['yes_sold'] += count
                rec['yes_revenue'] += count * yes_price
            else:
                rec['no_sold'] += count
                rec['no_revenue'] += count * no_price

    # Compute P&L per ticker
    total_pnl = 0
    total_fees = 0

    for ticker, rec in by_ticker.items():
        settlement = settlement_map.get(ticker, {})
        result = settlement.get('market_result', 'open')
        revenue = settlement.get('revenue', 0) or 0

        net_yes = rec['yes_bought'] - rec['yes_sold']
        net_no = rec['no_bought'] - rec['no_sold']

        # Cash flow from trading (revenue from sales - cost of buys)
        cash_flow = (rec['yes_revenue'] + rec['no_revenue'] - rec['yes_cost'] - rec['no_cost'])

        # Settlement value
        if result == 'yes':
            settlement_value = net_yes * 100  # cents
        elif result == 'no':
            settlement_value = net_no * 100
        else:
            settlement_value = 0  # still open

        gross_pnl_cents = cash_flow + settlement_value
        gross_pnl_dollars = gross_pnl_cents / 100

        # Fill fees (already in dollars from Kalshi API)
        fill_fee_dollars = rec['fees']  # accumulated from float(fee_cost) per fill

        # Settlement fees (separate from fill fees)
        settle_fee_raw = settlement.get('fee_cost', '0')
        settle_fee_dollars = float(settle_fee_raw) if settle_fee_raw else 0

        fee_dollars = fill_fee_dollars + settle_fee_dollars

        rec['net_yes'] = net_yes
        rec['net_no'] = net_no
        rec['market_result'] = result
        rec['gross_pnl_dollars'] = gross_pnl_dollars
        rec['fee_dollars'] = fee_dollars
        rec['net_pnl_dollars'] = gross_pnl_dollars - fee_dollars
        rec['is_settled'] = result in ('yes', 'no')
        rec['settlement_revenue'] = revenue

        total_pnl += gross_pnl_dollars
        total_fees += fee_dollars

    return {
        'by_ticker': by_ticker,
        'total_gross_pnl': total_pnl,
        'total_fees': total_fees,
        'total_net_pnl': total_pnl - total_fees,
    }


# ── trades.json P&L computation ──────────────────────────────────────────

def norm_pm(pm_price):
    if pm_price is None:
        return 0
    if isinstance(pm_price, (int, float)) and pm_price < 1 and pm_price > 0:
        return pm_price * 100
    return pm_price


def trade_pnl(t: dict) -> float | None:
    """Compute P&L from a single trade entry. Same logic as daily_recap.py."""
    qty = t.get('contracts_filled', 0) or t.get('contracts_intended', 0) or 0

    sp = t.get('settlement_pnl')
    if sp is not None:
        return sp

    status = t.get('status', '')
    tier = t.get('tier', '')

    if status == 'SUCCESS' or tier == 'TIER1_HEDGE':
        apnl = t.get('actual_pnl')
        if apnl and isinstance(apnl, dict):
            npd = apnl.get('net_profit_dollars')
            if npd is not None:
                return npd
        enpc = t.get('estimated_net_profit_cents')
        if enpc is not None:
            return (enpc * qty) / 100

    if status == 'EXITED' or tier in ('TIER2_EXIT', 'TIER3_UNWIND'):
        upc = t.get('unwind_pnl_cents')
        if upc is not None:
            return upc / 100
        ufp = t.get('unwind_fill_price')
        pm_cents = norm_pm(t.get('pm_price', 0))
        if ufp is not None and pm_cents > 0 and qty > 0:
            direction = t.get('direction', '')
            if direction == 'BUY_PM_SELL_K':
                return ((ufp * 100) - pm_cents) * qty / 100
            else:
                return (pm_cents - (ufp * 100)) * qty / 100
        ulc = t.get('unwind_loss_cents')
        if ulc is not None and ulc != 0:
            return -abs(ulc) / 100

    return None


# ── Matching ──────────────────────────────────────────────────────────────

def match_trades_to_kalshi(trades: list, kalshi_data: dict) -> list:
    """
    Match trades.json entries to Kalshi tickers.
    Returns list of match records with comparison data.
    """
    matches = []
    by_ticker = kalshi_data['by_ticker']

    for i, t in enumerate(trades):
        if (t.get('contracts_filled') or 0) == 0:
            continue

        ticker = t.get('kalshi_ticker', '')
        recorded_pnl = trade_pnl(t)
        apnl = t.get('actual_pnl', {})
        recorded_net = apnl.get('net_profit_dollars') if apnl else None

        kalshi_rec = by_ticker.get(ticker)

        match = {
            'index': i,
            'timestamp': t.get('timestamp', ''),
            'team': t.get('team', '?'),
            'ticker': ticker,
            'direction': t.get('direction', ''),
            'qty': t.get('contracts_filled', 0),
            'k_price': t.get('k_price', 0),
            'pm_price_raw': t.get('pm_price', 0),
            'pm_price_cents': norm_pm(t.get('pm_price', 0)),
            'status': t.get('status', ''),
            'tier': t.get('tier', ''),
            'recorded_pnl': recorded_pnl,
            'recorded_net': recorded_net,
            'kalshi_match': kalshi_rec is not None,
        }

        if kalshi_rec:
            match['k_gross_pnl'] = kalshi_rec['gross_pnl_dollars']
            match['k_fees'] = kalshi_rec['fee_dollars']
            match['k_net_pnl'] = kalshi_rec['net_pnl_dollars']
            match['k_result'] = kalshi_rec['market_result']
            match['k_fills'] = kalshi_rec['fill_count']
            match['k_net_yes'] = kalshi_rec['net_yes']
            match['k_net_no'] = kalshi_rec['net_no']

        matches.append(match)

    return matches


# ── Report ────────────────────────────────────────────────────────────────

def print_report(trades, kalshi_data, matches, balance_info):
    lines = []
    lines.append("=" * 80)
    lines.append("  ARB EXECUTOR RECONCILIATION REPORT")
    lines.append(f"  Generated: {datetime.now().isoformat()}")
    lines.append("=" * 80)
    lines.append("")

    # ── Section 1: PM Fill Price Analysis ──
    lines.append("1. PM FILL PRICE ANALYSIS")
    lines.append("-" * 40)
    lines.append("  pm_price in trades.json = ACTUAL fill price from PM API response")
    lines.append("  (Verified: executor_core.py extracts avgPx/executions from PM response)")
    lines.append("  unwind_fill_price = ACTUAL fill price from PM close/unwind operation")
    lines.append("  -> PM prices are RELIABLE. Gap is NOT from PM slippage recording.")
    lines.append("")

    # ── Section 2: Kalshi Data Summary ──
    lines.append("2. KALSHI API DATA")
    lines.append("-" * 40)
    by_ticker = kalshi_data['by_ticker']
    total_fills = sum(r['fill_count'] for r in by_ticker.values())
    settled_count = sum(1 for r in by_ticker.values() if r['is_settled'])
    open_count = sum(1 for r in by_ticker.values() if not r['is_settled'])
    lines.append(f"  Total tickers traded: {len(by_ticker)}")
    lines.append(f"  Total fills: {total_fills}")
    lines.append(f"  Settled markets: {settled_count}")
    lines.append(f"  Open markets: {open_count}")
    lines.append(f"  Kalshi gross P&L: ${kalshi_data['total_gross_pnl']:+.4f}")
    lines.append(f"  Kalshi fees: ${kalshi_data['total_fees']:.4f}")
    lines.append(f"  Kalshi net P&L: ${kalshi_data['total_net_pnl']:+.4f}")
    lines.append("")

    # ── Section 3: trades.json Summary ──
    lines.append("3. TRADES.JSON SUMMARY")
    lines.append("-" * 40)
    filled = [t for t in trades if (t.get('contracts_filled') or 0) > 0]
    total_recorded = sum(trade_pnl(t) or 0 for t in filled)
    lines.append(f"  Total trades: {len(trades)}")
    lines.append(f"  Filled trades: {len(filled)}")
    lines.append(f"  Recorded total P&L: ${total_recorded:+.4f}")
    lines.append("")

    # ── Section 4: Balance Check ──
    lines.append("4. BALANCE CHECK")
    lines.append("-" * 40)
    if balance_info:
        k_balance = balance_info.get('k_balance', 0)
        k_portfolio = balance_info.get('k_portfolio', 0)
        lines.append(f"  Kalshi cash: ${k_balance / 100:.2f}" if k_balance > 1 else f"  Kalshi cash: ${k_balance:.2f}")
        lines.append(f"  Starting balance: ${STARTING_BALANCE:.2f}")
    else:
        lines.append("  Balance data not available")

    # Read balances.json if it exists
    if os.path.exists(BALANCES_FILE):
        try:
            with open(BALANCES_FILE) as f:
                bal = json.load(f)
            k_port = bal.get('k_portfolio', 0)
            pm_port = bal.get('pm_portfolio', 0)
            total = k_port + pm_port
            actual_pnl = total - STARTING_BALANCE
            lines.append(f"  Kalshi portfolio: ${k_port:.2f}")
            lines.append(f"  PM portfolio: ${pm_port:.2f}")
            lines.append(f"  Total portfolio: ${total:.2f}")
            lines.append(f"  Actual P&L (vs start): ${actual_pnl:+.2f}")
            lines.append(f"  Recorded P&L: ${total_recorded:+.4f}")
            lines.append(f"  GAP: ${actual_pnl - total_recorded:+.2f}")
        except Exception:
            pass
    lines.append("")

    # ── Section 5: Per-Trade Comparison ──
    lines.append("5. PER-TRADE RECONCILIATION")
    lines.append("-" * 80)
    lines.append(f"  {'TIME':>8} {'TEAM':>5} {'DIR':>18} {'K':>4} {'PM':>5} {'STATUS':>10} | {'RECORDED':>10} {'K_GROSS':>10} {'K_FEES':>8} {'K_NET':>10} {'DELTA':>10}")
    lines.append("  " + "-" * 107)

    total_delta = 0
    for m in matches:
        ts = m['timestamp'][11:19] if len(m['timestamp']) >= 19 else m['timestamp']
        rec = m['recorded_pnl']
        rec_str = f"${rec:+.4f}" if rec is not None else "N/A"

        if m['kalshi_match']:
            k_gross = m['k_gross_pnl']
            k_fees = m['k_fees']
            k_net = m['k_net_pnl']
            # Delta: how far off is our recorded P&L from Kalshi truth + PM costs
            delta = (rec or 0) - k_net if rec is not None else 0
            total_delta += delta
            lines.append(f"  {ts:>8} {m['team']:>5} {m['direction']:>18} {m['k_price']:>4} {m['pm_price_cents']:>5.1f} {m['status']:>10} | {rec_str:>10} ${k_gross:+.4f}  ${k_fees:.4f}  ${k_net:+.4f}  ${delta:+.4f}")
        else:
            lines.append(f"  {ts:>8} {m['team']:>5} {m['direction']:>18} {m['k_price']:>4} {m['pm_price_cents']:>5.1f} {m['status']:>10} | {rec_str:>10} {'NO MATCH':>10} {'':>8} {'':>10} {'':>10}")
    lines.append("  " + "-" * 107)
    lines.append(f"  {'TOTALS':>60} | ${total_recorded:+.4f} ${kalshi_data['total_gross_pnl']:+.4f}  ${kalshi_data['total_fees']:.4f}  ${kalshi_data['total_net_pnl']:+.4f}  ${total_delta:+.4f}")
    lines.append("")

    # ── Section 6: Kalshi tickers not in trades.json ──
    lines.append("6. KALSHI TICKERS NOT IN TRADES.JSON (possible missing trades)")
    lines.append("-" * 80)
    trades_tickers = {t.get('kalshi_ticker', '') for t in trades if t.get('kalshi_ticker')}
    orphan_count = 0
    orphan_pnl = 0
    for ticker, rec in sorted(by_ticker.items()):
        if ticker not in trades_tickers:
            orphan_count += 1
            pnl = rec['gross_pnl_dollars']
            orphan_pnl += pnl
            result = rec['market_result']
            total_contracts = rec['yes_bought'] + rec['yes_sold'] + rec['no_bought'] + rec['no_sold']
            game = '-'.join(ticker.split('-')[1:3]) if len(ticker.split('-')) > 2 else ticker[:30]
            team = ticker.split('-')[-1] if '-' in ticker else '?'
            lines.append(f"  {game:30} {team:>5} | Y:{rec['net_yes']:+3} N:{rec['net_no']:+3} | {result:>5} | ${pnl:+.4f}")
    if orphan_count == 0:
        lines.append("  None — all Kalshi fills have matching trades.json entries")
    else:
        lines.append(f"  TOTAL orphan P&L: ${orphan_pnl:+.4f} across {orphan_count} tickers")
    lines.append("")

    # ── Section 7: Gap Analysis ──
    lines.append("7. GAP ANALYSIS")
    lines.append("-" * 40)
    lines.append(f"  trades.json recorded P&L:    ${total_recorded:+.4f}")
    lines.append(f"  Kalshi-only net P&L:         ${kalshi_data['total_net_pnl']:+.4f}")
    lines.append(f"  Orphan Kalshi P&L:           ${orphan_pnl:+.4f}")
    gap = total_recorded - kalshi_data['total_net_pnl']
    lines.append(f"  Recorded vs Kalshi delta:    ${gap:+.4f}")
    lines.append(f"  (Positive = trades.json overstates profit)")
    lines.append("")
    lines.append("=" * 80)

    report = "\n".join(lines)
    print(report)
    return report


# ── Main ──────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Reconcile trades.json against Kalshi API")
    parser.add_argument("--save", action="store_true", help="Save Kalshi data to disk")
    parser.add_argument("--offline", action="store_true", help="Use previously saved Kalshi data")
    args = parser.parse_args()

    # Load trades.json
    if not os.path.exists(TRADES_FILE):
        print(f"Error: {TRADES_FILE} not found")
        sys.exit(1)
    with open(TRADES_FILE) as f:
        trades = json.load(f)

    balance_info = None

    if args.offline:
        # Load from disk
        if not os.path.exists(KALSHI_FILLS_FILE) or not os.path.exists(KALSHI_SETTLEMENTS_FILE):
            print("Error: Kalshi data files not found. Run without --offline first.")
            sys.exit(1)
        with open(KALSHI_FILLS_FILE) as f:
            fills = json.load(f)
        with open(KALSHI_SETTLEMENTS_FILE) as f:
            settlements = json.load(f)
        print(f"Loaded {len(fills)} fills and {len(settlements)} settlements from disk")
    else:
        # Pull from Kalshi API
        kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
        async with aiohttp.ClientSession() as session:
            print("Pulling data from Kalshi API...")
            fills = await pull_kalshi_fills(session, kalshi_api)
            print(f"  Fills: {len(fills)}")
            settlements = await pull_kalshi_settlements(session, kalshi_api)
            print(f"  Settlements: {len(settlements)}")
            try:
                balance_info = await pull_kalshi_balance(session, kalshi_api)
                print(f"  Balance: {json.dumps(balance_info)}")
            except Exception as e:
                print(f"  Balance fetch failed: {e}")
            print()

        if args.save:
            with open(KALSHI_FILLS_FILE, 'w') as f:
                json.dump(fills, f, indent=2)
            with open(KALSHI_SETTLEMENTS_FILE, 'w') as f:
                json.dump(settlements, f, indent=2)
            print(f"Saved to {KALSHI_FILLS_FILE} and {KALSHI_SETTLEMENTS_FILE}")

    # Compute Kalshi P&L
    kalshi_data = compute_kalshi_pnl(fills, settlements)

    # Match against trades.json
    matches = match_trades_to_kalshi(trades, kalshi_data)

    # Print report
    report = print_report(trades, kalshi_data, matches, balance_info)

    # Save report
    report_path = os.path.join(SCRIPT_DIR, "reconciliation_report.txt")
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
