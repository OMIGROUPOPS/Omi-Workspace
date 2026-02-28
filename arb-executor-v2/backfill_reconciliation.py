#!/usr/bin/env python3
"""
One-time backfill: reconcile ALL filled trades against Kalshi API ground truth.

Unlike settle_positions.py (which only reconciles trades that already have settlement_pnl),
this script runs on every filled trade with a kalshi_ticker, regardless of current state.

Usage:
    python backfill_reconciliation.py          # dry run (print only)
    python backfill_reconciliation.py --apply  # write changes to trades.json
"""
import asyncio
import json
import os
import shutil
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRADES_FILE = os.path.join(SCRIPT_DIR, 'trades.json')


async def main():
    apply = '--apply' in sys.argv

    # Import reconciler
    sys.path.insert(0, SCRIPT_DIR)
    from kalshi_reconciler import (
        get_fills_and_settlements, get_fill_cost_by_ticker,
        get_settlement_by_ticker, compute_kalshi_pnl,
    )

    # Load trades
    if not os.path.exists(TRADES_FILE):
        print('No trades.json found')
        return

    with open(TRADES_FILE) as f:
        trades = json.load(f)

    print(f'Total trades: {len(trades)}')

    # Pull Kalshi data (force refresh)
    print('Pulling Kalshi fills and settlements...')
    fills, settlements = await get_fills_and_settlements(force_refresh=True)
    print(f'  Fills: {len(fills)}, Settlements: {len(settlements)}')

    fill_map = get_fill_cost_by_ticker(fills)
    settle_map = get_settlement_by_ticker(settlements)

    # Process each filled trade
    reconciled = 0
    skipped_no_ticker = 0
    skipped_no_fill = 0
    skipped_not_settled = 0
    skipped_no_contracts = 0
    total_old_pnl = 0.0
    total_new_pnl = 0.0

    print()
    print(f'{"TEAM":>8} {"STATUS":>10} {"OLD_PNL":>10} {"NEW_PNL":>10} {"K_PNL":>9} {"PM_PNL":>9} {"DELTA":>9}')
    print('=' * 75)

    for idx, t in enumerate(trades):
        filled = t.get('contracts_filled', 0) or 0
        if filled == 0:
            skipped_no_contracts += 1
            continue

        ticker = t.get('kalshi_ticker', '')
        if not ticker:
            skipped_no_ticker += 1
            continue

        k_fill = fill_map.get(ticker)
        if not k_fill:
            skipped_no_fill += 1
            team = t.get('team', '?')
            print(f'{team:>8} {"NO_K_FILL":>10} {"---":>10} {"---":>10} {"---":>9} {"---":>9} {"---":>9}  {ticker}')
            continue

        k_settle = settle_map.get(ticker)
        if not k_settle:
            skipped_not_settled += 1
            team = t.get('team', '?')
            print(f'{team:>8} {"NOT_SETTL":>10} {"---":>10} {"---":>10} {"---":>9} {"---":>9} {"---":>9}  {ticker}')
            continue

        # Kalshi-side P&L
        k_pnl = compute_kalshi_pnl(k_fill, k_settle)

        # PM-side P&L from settlement outcome
        pm_raw = t.get('pm_price', 0)
        pm_cents = pm_raw * 100 if (isinstance(pm_raw, (int, float)) and pm_raw < 1 and pm_raw > 0) else pm_raw
        is_short = t.get('pm_is_buy_short')
        if is_short is None:
            # Infer from direction: BUY_K_SELL_PM → PM is sell (short)
            is_short = 'SELL_PM' in t.get('direction', '')
        qty = filled
        pm_fee = t.get('pm_fee', 0) or 0

        # Use settlement result directly for PM P&L
        result = k_settle['result']  # 'yes' or 'no'

        if not is_short:
            # Bought YES on PM → wins if result=yes
            if result == 'yes':
                pm_pnl = (100 - pm_cents) * qty / 100
            else:
                pm_pnl = -pm_cents * qty / 100
        else:
            # Sold YES on PM (short) → wins if result=no
            if result == 'no':
                pm_pnl = pm_cents * qty / 100
            else:
                pm_pnl = -(100 - pm_cents) * qty / 100

        pm_pnl -= pm_fee

        new_pnl = round(k_pnl + pm_pnl, 4)

        # Get old P&L for comparison
        old_pnl = t.get('settlement_pnl')
        if old_pnl is None:
            apnl = t.get('actual_pnl')
            if apnl and isinstance(apnl, dict):
                old_pnl = apnl.get('net_profit_dollars', 0)
            else:
                est = t.get('estimated_net_profit_cents', 0) or 0
                old_pnl = est * qty / 100

        delta = new_pnl - (old_pnl or 0)
        total_old_pnl += (old_pnl or 0)
        total_new_pnl += new_pnl

        team = t.get('team', '?')
        status = t.get('status', '?')
        print(f'{team:>8} {status:>10} {old_pnl or 0:>+10.4f} {new_pnl:>+10.4f} {k_pnl:>+9.4f} {pm_pnl:>+9.4f} {delta:>+9.4f}')

        if apply:
            trades[idx]['settlement_pnl'] = new_pnl
            trades[idx]['settlement_source'] = 'kalshi_reconciled'
            trades[idx]['k_actual_cost'] = k_fill['net_cost_cents']
            trades[idx]['k_actual_fee'] = round(k_fill['fee_dollars'] + k_settle['fee_dollars'], 4)

        reconciled += 1

    print('=' * 75)
    print(f'{"TOTAL":>8} {"":>10} {total_old_pnl:>+10.4f} {total_new_pnl:>+10.4f} {"":>9} {"":>9} {total_new_pnl - total_old_pnl:>+9.4f}')

    print(f'\nReconciled: {reconciled}')
    print(f'Skipped (no contracts): {skipped_no_contracts}')
    print(f'Skipped (no ticker): {skipped_no_ticker}')
    print(f'Skipped (no Kalshi fill): {skipped_no_fill}')
    print(f'Skipped (not settled): {skipped_not_settled}')

    if apply and reconciled > 0:
        # Backup first
        backup = TRADES_FILE + f'.pre_reconcile_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copy2(TRADES_FILE, backup)
        print(f'\nBackup: {backup}')

        with open(TRADES_FILE, 'w') as f:
            json.dump(trades, f, indent=2)
        print(f'Wrote {reconciled} reconciled trades to trades.json')
    elif reconciled > 0 and not apply:
        print(f'\nDRY RUN — pass --apply to write changes')


if __name__ == '__main__':
    asyncio.run(main())
