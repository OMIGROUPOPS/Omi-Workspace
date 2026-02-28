#!/usr/bin/env python3
"""
pnl_forensics.py — Trace every dollar: deposits, settlements, fees, unwinds, open positions.

Realized P&L = (settled profits) - (total fees) - (unwind losses)
Unrealized P&L = (open position mark-to-market) - (open position cost basis)
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from arb_executor_v7 import KalshiAPI, PolymarketUSAPI
from polymarket_us import AsyncPolymarketUS
import aiohttp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _extract_cost(raw):
    if isinstance(raw, dict):
        return float(raw.get('amount', raw.get('value', 0)))
    try:
        return float(raw)
    except (ValueError, TypeError):
        return 0.0


async def main():
    kalshi_key = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
    with open(os.path.join(BASE_DIR, 'kalshi.pem')) as f:
        kalshi_pk = f.read()
    kalshi_api = KalshiAPI(kalshi_key, kalshi_pk)

    pm_key = os.getenv('PM_US_API_KEY')
    pm_secret = os.getenv('PM_US_SECRET_KEY') or os.getenv('PM_US_SECRET')
    pm_api = PolymarketUSAPI(pm_key, pm_secret)
    pm_sdk = AsyncPolymarketUS(key_id=pm_key, secret_key=pm_secret)

    async with aiohttp.ClientSession() as session:
        # ═══════════════════════════════════════════════════════════════
        # 1. KALSHI SETTLEMENTS — every settled market
        # ═══════════════════════════════════════════════════════════════
        print("Fetching Kalshi settlements (all pages)...")
        k_settlements = []
        cursor = None
        page = 0
        while True:
            path = '/trade-api/v2/portfolio/settlements?limit=100'
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
            except Exception as e:
                print(f"  Error: {e}")
                break
            items = data.get('settlements', [])
            if not items:
                break
            k_settlements.extend(items)
            cursor = data.get('cursor')
            page += 1
            if not cursor or page > 50:
                break
        print(f"  Got {len(k_settlements)} settlement records")

        # ═══════════════════════════════════════════════════════════════
        # 2. KALSHI FILLS — every trade with fees
        # ═══════════════════════════════════════════════════════════════
        print("Fetching Kalshi fills (all pages)...")
        k_fills_raw = []
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
            except Exception as e:
                print(f"  Error: {e}")
                break
            items = data.get('fills', [])
            if not items:
                break
            k_fills_raw.extend(items)
            cursor = data.get('cursor')
            page += 1
            if not cursor or page > 50:
                break
        print(f"  Got {len(k_fills_raw)} fill records")

        # ═══════════════════════════════════════════════════════════════
        # 3. KALSHI BALANCE
        # ═══════════════════════════════════════════════════════════════
        k_balance_raw = None
        path = '/trade-api/v2/portfolio/balance'
        try:
            async with session.get(
                f'{kalshi_api.BASE_URL}{path}',
                headers=kalshi_api._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    k_balance_raw = await r.json()
        except Exception:
            pass

        # ═══════════════════════════════════════════════════════════════
        # 4. KALSHI CURRENT POSITIONS
        # ═══════════════════════════════════════════════════════════════
        k_positions = await kalshi_api.get_positions(session) or {}

        # ═══════════════════════════════════════════════════════════════
        # 5. PM POSITIONS (open)
        # ═══════════════════════════════════════════════════════════════
        pm_positions = {}
        try:
            pm_resp = await pm_sdk.portfolio.positions()
            for slug, pos in pm_resp.get('positions', {}).items():
                net = int(pos.get('netPosition', 0))
                if net != 0:
                    pm_positions[slug] = pos
        except Exception as e:
            print(f"  PM SDK error: {e}")

        # PM balance
        pm_balance = None
        try:
            pm_balance = await pm_api.get_balance(session)
        except Exception:
            pass

        # ═══════════════════════════════════════════════════════════════
        # 6. TRADES.JSON
        # ═══════════════════════════════════════════════════════════════
        trades_path = os.path.join(BASE_DIR, 'trades.json')
        trades = []
        if os.path.exists(trades_path):
            with open(trades_path) as f:
                trades = json.load(f)

        # ═══════════════════════════════════════════════════════════════
        # 7. KALSHI ORDERBOOK for open positions (mark-to-market)
        # ═══════════════════════════════════════════════════════════════
        print("Fetching orderbooks for open K positions...")
        k_mtm = {}
        for ticker in k_positions:
            path = f'/trade-api/v2/markets/{ticker}/orderbook'
            try:
                async with session.get(
                    f'{kalshi_api.BASE_URL}{path}',
                    headers=kalshi_api._headers('GET', path),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        ob = data.get('orderbook', {})
                        yes_bids = ob.get('yes', [])
                        no_bids = ob.get('no', [])
                        k_mtm[ticker] = {
                            'yes_bid': yes_bids[0][0] if yes_bids else None,
                            'no_bid': no_bids[0][0] if no_bids else None,
                        }
            except Exception:
                pass

    # ═══════════════════════════════════════════════════════════════════════
    # ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════

    print(f"\n{'='*80}")
    print(f"  P&L FORENSICS — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*80}")

    # ─── A. KALSHI FEES ───
    k_total_fees = 0
    k_total_buy_cost = 0  # cents spent buying
    k_total_sell_revenue = 0  # cents received selling
    k_fill_count = 0
    for fl in k_fills_raw:
        count = int(fl.get('count', 0))
        side = fl.get('side', '')
        action = fl.get('action', '')
        yes_price = int(fl.get('yes_price', 0))
        no_price = int(fl.get('no_price', 100 - yes_price))
        # Kalshi charges taker fee on each fill
        # Fee is typically 2c per contract but check the 'fee' field if present
        fee = float(fl.get('fee', 0))
        if fee == 0:
            fee = count * 2  # 2c per contract default
        k_total_fees += fee
        k_fill_count += count

        if action == 'buy':
            price = yes_price if side == 'yes' else no_price
            k_total_buy_cost += count * price
        else:  # sell
            price = yes_price if side == 'yes' else no_price
            k_total_sell_revenue += count * price

    # ─── B. KALSHI SETTLEMENTS ───
    k_settled_revenue = 0
    k_settled_cost = 0
    k_settled_fees = 0
    k_settlements_with_position = 0
    settlement_details = []
    for s in k_settlements:
        revenue = int(s.get('revenue', 0))
        yes_count = int(float(s.get('yes_count_fp', s.get('yes_count', 0))))
        no_count = int(float(s.get('no_count_fp', s.get('no_count', 0))))
        yes_cost = int(s.get('yes_total_cost', 0))
        no_cost = int(s.get('no_total_cost', 0))
        fee = float(s.get('fee_cost', 0))
        market_result = s.get('market_result', '')
        ticker = s.get('market_ticker', s.get('event_ticker', ''))

        if yes_count > 0 or no_count > 0:
            k_settlements_with_position += 1
            net_pnl = revenue - yes_cost - no_cost
            k_settled_revenue += revenue
            k_settled_cost += yes_cost + no_cost
            k_settled_fees += fee
            # Extract team abbrev from ticker
            team = ticker.split('-')[-1] if '-' in ticker else ticker
            settlement_details.append({
                'ticker': ticker,
                'team': team,
                'result': market_result,
                'yes_count': yes_count,
                'no_count': no_count,
                'yes_cost': yes_cost,
                'no_cost': no_cost,
                'revenue': revenue,
                'fee': fee,
                'net_pnl': net_pnl,
                'settled': s.get('settled_time', ''),
            })

    k_settlement_pnl = k_settled_revenue - k_settled_cost

    # ─── C. TRADES.JSON ANALYSIS ───
    total_unwind_loss = 0
    unwind_details = []
    successful_trades = []
    failed_trades = []
    for t in trades:
        status = t.get('status', '')
        unwind_loss = t.get('unwind_loss_cents')
        unwind_pnl = t.get('unwind_pnl_cents')

        if unwind_loss is not None and unwind_loss > 0:
            total_unwind_loss += unwind_loss
            unwind_details.append({
                'team': t.get('team', '?'),
                'loss_cents': unwind_loss,
                'pnl_cents': unwind_pnl,
                'fill_price': t.get('unwind_fill_price'),
                'qty': t.get('unwind_qty', 0),
                'status': status,
                'time': t.get('timestamp', ''),
            })
        elif unwind_pnl is not None and unwind_pnl < 0:
            loss = abs(unwind_pnl)
            total_unwind_loss += loss
            unwind_details.append({
                'team': t.get('team', '?'),
                'loss_cents': loss,
                'pnl_cents': unwind_pnl,
                'fill_price': t.get('unwind_fill_price'),
                'qty': t.get('unwind_qty', 0),
                'status': status,
                'time': t.get('timestamp', ''),
            })

        if status in ('SUCCESS', 'HEDGED', 'LIVE', 'K_FIRST_SUCCESS'):
            successful_trades.append(t)
        elif status == 'PM_NO_FILL':
            failed_trades.append(t)

    # ─── D. PM FEES (from trades.json PM fills) ───
    # PM US fee rate is 0.1% per contract
    pm_total_fees_cents = 0
    for t in successful_trades:
        pm_fill = t.get('pm_fill', 0)
        pm_price = t.get('pm_price', 0)
        if pm_fill > 0 and pm_price > 0:
            # PM fee = 0.1% of notional (price × qty)
            pm_fee = pm_price * pm_fill * 0.001 * 100  # convert to cents
            pm_total_fees_cents += pm_fee

    # ─── E. OPEN POSITIONS VALUATION ───
    # Build fills-by-ticker for entry prices
    fills_by_ticker = defaultdict(lambda: {
        "yes_entry_qty": 0, "yes_entry_cost": 0,
        "no_entry_qty": 0, "no_entry_cost": 0,
        "yes_exit_qty": 0, "yes_exit_cost": 0,
        "no_exit_qty": 0, "no_exit_cost": 0,
    })
    for fl in k_fills_raw:
        ticker = fl.get('ticker', '')
        if not ticker:
            continue
        side = fl.get('side', '')
        action = fl.get('action', '')
        count = int(fl.get('count', 0))
        yes_price = int(fl.get('yes_price', 0))
        no_price = int(fl.get('no_price', 100 - yes_price))
        entry = fills_by_ticker[ticker]
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

    k_open_cost_cents = 0
    k_open_mtm_cents = 0
    k_open_details = []
    for ticker, pos in k_positions.items():
        qty = abs(pos.position)
        is_yes = pos.position > 0
        fills = fills_by_ticker.get(ticker, {})
        if is_yes:
            entry_vwap = fills.get('yes_entry_cost', 0) / fills.get('yes_entry_qty', 1) if fills.get('yes_entry_qty', 0) > 0 else 50
            cost = entry_vwap * qty
            prices = k_mtm.get(ticker, {})
            bid = prices.get('yes_bid')
            mtm = (bid * qty) if bid is not None else cost
        else:
            no_all_qty = fills.get('no_entry_qty', 0) + fills.get('no_exit_qty', 0)
            no_all_cost = fills.get('no_entry_cost', 0) + fills.get('no_exit_cost', 0)
            if fills.get('yes_exit_qty', 0) > 0:
                avg_yes_sell = fills['yes_exit_cost'] / fills['yes_exit_qty']
                no_all_qty += fills['yes_exit_qty']
                no_all_cost += fills['yes_exit_qty'] * (100 - avg_yes_sell)
            entry_vwap = no_all_cost / no_all_qty if no_all_qty > 0 else 50
            cost = entry_vwap * qty
            prices = k_mtm.get(ticker, {})
            bid = prices.get('no_bid')
            mtm = (bid * qty) if bid is not None else cost

        k_open_cost_cents += cost
        k_open_mtm_cents += mtm
        team = ticker.split('-')[-1] if '-' in ticker else ticker
        k_open_details.append({
            'ticker': ticker,
            'team': team,
            'side': 'YES' if is_yes else 'NO',
            'qty': qty,
            'entry': round(entry_vwap, 1),
            'bid': bid,
            'cost_cents': round(cost, 1),
            'mtm_cents': round(mtm, 1),
            'unrealized': round(mtm - cost, 1),
        })

    # PM open positions
    pm_open_cost_cents = 0
    pm_open_mtm_cents = 0
    pm_open_details = []
    for slug, pos in pm_positions.items():
        net = int(pos.get('netPosition', 0))
        qty = abs(net)
        cost = _extract_cost(pos.get('cost', 0))
        cash_value = _extract_cost(pos.get('cashValue', 0))
        cost_cents = cost * 100
        mtm_cents = (cash_value * 100) if cash_value > 0 else cost_cents
        pm_open_cost_cents += cost_cents
        pm_open_mtm_cents += mtm_cents
        meta = pos.get('marketMetadata', {})
        team_info = meta.get('team', {})
        team = team_info.get('abbreviation', slug[:10]).upper()
        pm_open_details.append({
            'slug': slug,
            'team': team,
            'qty': qty,
            'cost_usd': round(cost, 4),
            'cashValue_usd': round(cash_value, 4),
            'cost_cents': round(cost_cents, 1),
            'mtm_cents': round(mtm_cents, 1),
            'unrealized': round(mtm_cents - cost_cents, 1),
        })

    # ═══════════════════════════════════════════════════════════════════════
    # PRINT REPORT
    # ═══════════════════════════════════════════════════════════════════════

    # ─── 1. CURRENT BALANCES ───
    k_cash = k_balance_raw.get('balance', 0) / 100 if k_balance_raw else 0
    k_port_val = k_balance_raw.get('portfolio_value', 0) / 100 if k_balance_raw else 0
    pm_cash = pm_balance if pm_balance else 0

    print(f"\n  1. CURRENT BALANCES")
    print(f"  {'─'*70}")
    print(f"  Kalshi:  cash=${k_cash:.2f}  portfolio_value=${k_port_val:.2f}  total=${k_cash + k_port_val:.2f}")
    print(f"  PM:      cash=${pm_cash:.2f}  positions=${pm_open_mtm_cents/100:.2f}  total=${pm_cash + pm_open_mtm_cents/100:.2f}")
    print(f"  COMBINED: ${k_cash + k_port_val + pm_cash + pm_open_mtm_cents/100:.2f}")

    # ─── 2. DEPOSITS (from deposits.json) ───
    deposits_path = os.path.join(BASE_DIR, 'deposits.json')
    deposits_data = {}
    if os.path.exists(deposits_path):
        with open(deposits_path) as f:
            deposits_data = json.load(f)

    print(f"\n  2. DEPOSITS & WITHDRAWALS")
    print(f"  {'─'*70}")
    starting = deposits_data.get('starting_balances', {})
    print(f"  Starting ({starting.get('date', '?')}): K=${starting.get('kalshi', 0):.2f}  PM=${starting.get('polymarket', 0):.2f}  total=${starting.get('total', 0):.2f}")
    total_deposits = 0
    for d in deposits_data.get('deposits', []):
        print(f"  Deposit {d['date']}: {d['platform']} +${d['amount']:.2f}  ({d.get('note', '')})")
        total_deposits += d['amount']
    total_withdrawals = 0
    for w in deposits_data.get('withdrawals', []):
        print(f"  Withdrawal {w['date']}: {w['platform']} -${w['amount']:.2f}  ({w.get('note', '')})")
        total_withdrawals += w['amount']
    total_capital_in = starting.get('total', 0) + total_deposits - total_withdrawals
    print(f"  Total Capital In: ${total_capital_in:.2f}")

    # ─── 3. KALSHI SETTLED TRADES ───
    print(f"\n  3. KALSHI SETTLEMENTS (realized)")
    print(f"  {'─'*70}")
    # Sort by net_pnl to show winners and losers
    settlement_details.sort(key=lambda x: x['net_pnl'], reverse=True)
    settled_winners = 0
    settled_losers = 0
    for s in settlement_details:
        pnl = s['net_pnl']
        marker = '✓' if pnl >= 0 else '✗'
        pos_str = f"YES×{s['yes_count']}" if s['yes_count'] > 0 else f"NO×{s['no_count']}"
        result_str = s['result'].upper()
        date = s['settled'][:10] if s['settled'] else '?'
        print(f"  {marker} {s['team']:<8s} {pos_str:<8s} result={result_str:<3s} "
              f"cost={s['yes_cost']+s['no_cost']:>5d}c  rev={s['revenue']:>5d}c  "
              f"pnl={pnl:>+5d}c  fee={s['fee']:.0f}c  [{date}]")
        if pnl >= 0:
            settled_winners += 1
        else:
            settled_losers += 1

    print(f"\n  Kalshi settled: {k_settlements_with_position} trades | "
          f"{settled_winners} winners, {settled_losers} losers")
    print(f"  Total cost: {k_settled_cost}c  Total revenue: {k_settled_revenue}c")
    print(f"  Kalshi settlement P&L: {k_settlement_pnl:+d}c (${k_settlement_pnl/100:+.2f})")
    print(f"  Kalshi settlement fees: {k_settled_fees:.0f}c (${k_settled_fees/100:.2f})")

    # ─── 4. FEES ───
    print(f"\n  4. TOTAL FEES")
    print(f"  {'─'*70}")
    print(f"  Kalshi fill fees (from fills): {k_total_fees:.0f}c (${k_total_fees/100:.2f})")
    print(f"  Kalshi settlement fees:        {k_settled_fees:.0f}c (${k_settled_fees/100:.2f})")
    print(f"  PM fees (est 0.1% of notional): {pm_total_fees_cents:.0f}c (${pm_total_fees_cents/100:.2f})")
    all_fees = k_total_fees + pm_total_fees_cents
    print(f"  TOTAL FEES: {all_fees:.0f}c (${all_fees/100:.2f})")

    # ─── 5. UNWIND LOSSES ───
    print(f"\n  5. UNWIND LOSSES (failed hedges)")
    print(f"  {'─'*70}")
    if unwind_details:
        for u in unwind_details:
            date = u['time'][:10] if u['time'] else '?'
            print(f"  {u['team']:<8s} loss={u['loss_cents']:.1f}c  pnl={u['pnl_cents']}c  "
                  f"fill@{u['fill_price']}  qty={u['qty']}  [{u['status']}] [{date}]")
    else:
        print(f"  No unwind losses recorded")
    print(f"  Total unwind losses: {total_unwind_loss:.1f}c (${total_unwind_loss/100:.2f})")

    # ─── 6. OPEN K POSITIONS (unrealized) ───
    print(f"\n  6. OPEN KALSHI POSITIONS (unrealized)")
    print(f"  {'─'*70}")
    for d in k_open_details:
        bid_str = f"{d['bid']}c" if d['bid'] is not None else 'N/A'
        print(f"  {d['team']:<8s} {d['side']}×{d['qty']:<3d} entry={d['entry']:.0f}c  "
              f"bid={bid_str:<5s}  cost={d['cost_cents']:.0f}c  mtm={d['mtm_cents']:.0f}c  "
              f"unrealized={d['unrealized']:+.0f}c")
    print(f"  K open cost: {k_open_cost_cents:.0f}c (${k_open_cost_cents/100:.2f})")
    print(f"  K open MTM:  {k_open_mtm_cents:.0f}c (${k_open_mtm_cents/100:.2f})")
    print(f"  K unrealized: {k_open_mtm_cents - k_open_cost_cents:+.0f}c (${(k_open_mtm_cents - k_open_cost_cents)/100:+.2f})")

    # ─── 7. OPEN PM POSITIONS (unrealized) ───
    print(f"\n  7. OPEN PM POSITIONS (unrealized)")
    print(f"  {'─'*70}")
    for d in pm_open_details:
        print(f"  {d['team']:<8s} qty={d['qty']:<3d} cost=${d['cost_usd']:.2f}  "
              f"cashValue=${d['cashValue_usd']:.2f}  "
              f"unrealized={d['unrealized']:+.0f}c")
    print(f"  PM open cost: {pm_open_cost_cents:.0f}c (${pm_open_cost_cents/100:.2f})")
    print(f"  PM open MTM:  {pm_open_mtm_cents:.0f}c (${pm_open_mtm_cents/100:.2f})")
    print(f"  PM unrealized: {pm_open_mtm_cents - pm_open_cost_cents:+.0f}c (${(pm_open_mtm_cents - pm_open_cost_cents)/100:+.2f})")

    # ─── 8. TRADE SUMMARY ───
    print(f"\n  8. TRADE SUMMARY (from trades.json)")
    print(f"  {'─'*70}")
    print(f"  Total trades attempted: {len(trades)}")
    print(f"  Successful (hedged):    {len(successful_trades)}")
    print(f"  PM no-fill:             {len(failed_trades)}")
    with_unwind = [t for t in trades if t.get('unwind_loss_cents') or (t.get('unwind_pnl_cents') and t['unwind_pnl_cents'] < 0)]
    print(f"  With unwind loss:       {len(with_unwind)}")
    k_first = [t for t in trades if t.get('tier') == 'K_FIRST_SUCCESS' or t.get('status') == 'K_FIRST_SUCCESS']
    print(f"  K-first success:        {len(k_first)}")

    # ─── 9. FINAL P&L RECONCILIATION ───
    print(f"\n{'='*80}")
    print(f"  FINAL P&L RECONCILIATION")
    print(f"{'='*80}")

    # Realized = Kalshi settlement P&L (already includes entry cost vs payout)
    # Note: K settlement revenue already accounts for what we paid vs what we got back
    # But we also need PM side of settled trades
    # Since PM settled positions are gone, we can only infer from trades.json
    realized_k_cents = k_settlement_pnl

    # PM realized: for trades where PM has settled, the PM P&L is embedded in the PM cash balance
    # We can compute it from trades.json: for settled hedged trades, PM profit = 100 - pm_entry (if winner) or -pm_entry (if loser)
    # But we don't have per-trade PM settlement data.
    #
    # SIMPLER: True P&L = current portfolio value - total capital in
    # But user wants component breakdown, so:

    combined_current = k_cash + k_port_val + pm_cash + pm_open_mtm_cents/100
    true_pnl = combined_current - total_capital_in

    k_unrealized = (k_open_mtm_cents - k_open_cost_cents) / 100
    pm_unrealized = (pm_open_mtm_cents - pm_open_cost_cents) / 100
    total_unrealized = k_unrealized + pm_unrealized

    # Realized = True P&L - Unrealized
    implied_realized = true_pnl - total_unrealized

    print(f"\n  Portfolio approach (top-down):")
    print(f"    Current portfolio:    ${combined_current:.2f}")
    print(f"    Total capital in:   - ${total_capital_in:.2f}")
    print(f"    ─────────────────────────────")
    pnl_sign = '+' if true_pnl >= 0 else ''
    print(f"    TRUE P&L:             {pnl_sign}${true_pnl:.2f}  ({true_pnl/total_capital_in*100:+.1f}%)")

    print(f"\n  Component breakdown:")
    print(f"    K settlement P&L:     {realized_k_cents:+d}c (${realized_k_cents/100:+.2f})")
    print(f"    K unrealized:         ${k_unrealized:+.2f}")
    print(f"    PM unrealized:        ${pm_unrealized:+.2f}")
    print(f"    Unwind losses:      - ${total_unwind_loss/100:.2f}")
    print(f"    K fees (fills):     - ${k_total_fees/100:.2f}")
    print(f"    PM fees (est):      - ${pm_total_fees_cents/100:.2f}")

    # Implied PM settled P&L = true P&L - K settlement P&L - unrealized - unwind + fees
    # (fees are already embedded in balances, so this is approximate)
    pm_implied_realized = true_pnl - realized_k_cents/100 - total_unrealized
    print(f"    PM settled P&L (implied): ${pm_implied_realized:+.2f}")

    print(f"\n  Kalshi fills: {k_fill_count} contracts across {len(k_fills_raw)} fills")
    print(f"  Total bought: {k_total_buy_cost}c (${k_total_buy_cost/100:.2f})")
    print(f"  Total sold:   {k_total_sell_revenue}c (${k_total_sell_revenue/100:.2f})")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    asyncio.run(main())
