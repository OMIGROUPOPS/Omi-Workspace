#!/usr/bin/env python3
"""Investigate ALA-TENN PM entry price and UFC negative-arb positions."""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from polymarket_us import AsyncPolymarketUS

BASE = os.path.dirname(os.path.abspath(__file__))


async def main():
    pm_key = os.getenv('PM_US_API_KEY')
    pm_secret = os.getenv('PM_US_SECRET_KEY') or os.getenv('PM_US_SECRET')
    sdk = AsyncPolymarketUS(key_id=pm_key, secret_key=pm_secret)

    print("=" * 70)
    print("  INVESTIGATION: ALA-TENN PM ENTRY + UFC NEGATIVE ARB")
    print("=" * 70)

    # ══════════════════════════════════════════════════════════════
    # 1. ALA-TENN: Pull PM position details + order history
    # ══════════════════════════════════════════════════════════════
    print("\n[1] ALA-TENN PM POSITION")
    print("-" * 50)
    slug = "aec-cbb-ala-tenn-2026-02-28"

    resp = await sdk.portfolio.positions()
    pos = resp.get("positions", {}).get(slug, {})
    if pos:
        meta = pos.get("marketMetadata", {})
        cost_raw = pos.get("cost", {})
        cost_val = float(cost_raw.get("value", 0)) if isinstance(cost_raw, dict) else float(cost_raw)
        net = pos.get("netPosition", "0")
        net_int = abs(int(net))
        per_contract = cost_val / net_int * 100 if net_int > 0 else 0
        print(f"  Slug: {slug}")
        print(f"  Outcome: {meta.get('outcome', '?')}")
        print(f"  Team: {meta.get('team', {}).get('safeName', '?')}")
        print(f"  Net Position: {net}")
        print(f"  Qty Bought: {pos.get('qtyBought')}")
        print(f"  Qty Sold: {pos.get('qtySold')}")
        print(f"  Total Cost: ${cost_val:.4f}")
        print(f"  Per-contract entry: {per_contract:.1f}c")
        print(f"  Cash Value: {pos.get('cashValue')}")
    else:
        print(f"  {slug} NOT FOUND in portfolio")

    # Pull PM order history for this slug
    print("\n[1b] PM ORDER HISTORY for ALA-TENN")
    print("-" * 50)
    try:
        # Try portfolio.orders or orders.list with market filter
        orders = await sdk.orders.list(market=slug)
        if isinstance(orders, dict):
            order_list = orders.get("orders", orders.get("results", []))
        elif isinstance(orders, list):
            order_list = orders
        else:
            order_list = []
        print(f"  Found {len(order_list)} orders")
        for o in order_list:
            print(f"  ---")
            print(f"  Order ID: {o.get('id', '?')[:20]}")
            print(f"  State: {o.get('state', '?')}")
            print(f"  Side: {o.get('side', '?')}")
            print(f"  Price: {o.get('price', '?')}")
            print(f"  Size: {o.get('size', o.get('originalSize', '?'))}")
            print(f"  Filled: {o.get('cumQuantity', o.get('filledSize', '?'))}")
            print(f"  Avg Price: {o.get('avgPx', '?')}")
            print(f"  Created: {o.get('createdAt', o.get('created_at', '?'))}")
            print(f"  Type: {o.get('type', '?')}  TIF: {o.get('timeInForce', '?')}")
            # Show executions if present
            execs = o.get('executions', [])
            if execs:
                for ex in execs:
                    print(f"    Execution: price={ex.get('price', '?')} qty={ex.get('quantity', '?')}")
    except Exception as e:
        print(f"  Orders API error: {type(e).__name__}: {e}")

    # Also check trades.json for ALA entry
    print("\n[1c] TRADES.JSON ALA ENTRIES")
    print("-" * 50)
    with open(os.path.join(BASE, 'trades.json')) as f:
        trades = json.load(f)
    ala_trades = [t for t in trades if t.get('team') == 'ALA' or 'ALATENN' in t.get('kalshi_ticker', '')]
    for t in ala_trades:
        print(f"  timestamp: {t.get('timestamp', '?')[:19]}")
        print(f"  direction: {t.get('direction')}")
        print(f"  K: {t.get('kalshi_ticker')} x{t.get('kalshi_fill')}@{t.get('k_price')}c")
        print(f"  PM: {t.get('pm_slug')} x{t.get('pm_fill')}@{t.get('pm_price')}c")
        print(f"  spread: {t.get('spread_cents')}c")
        print(f"  status: {t.get('status')} / raw: {t.get('raw_status')}")
        if t.get('actual_pnl'):
            pnl = t['actual_pnl']
            pc = pnl.get('per_contract', {})
            print(f"  P&L: k_cost={pc.get('k_cost')}c pm_cost={pc.get('pm_cost')}c total={pc.get('total_cost')}c payout={pc.get('payout')}c net={pc.get('net')}c")
        print(f"  ---")

    # ══════════════════════════════════════════════════════════════
    # 2. UFC POSITIONS: Check for settlement_pnl = -999
    # ══════════════════════════════════════════════════════════════
    print("\n[2] UFC POSITIONS — NEGATIVE ARB CHECK")
    print("-" * 50)
    ufc_tickers = [
        "KXUFCFIGHT-26FEB28VERMAR-VER",
        "KXUFCFIGHT-26FEB28LUNPAC-PAC",
        "KXUFCFIGHT-26FEB28MORKAV-MOR",
        "KXUFCFIGHT-26FEB28ZELGRE-GRE",
    ]
    ufc_trades = [t for t in trades if t.get('kalshi_ticker', '') in ufc_tickers]
    print(f"  Found {len(ufc_trades)} UFC trades in trades.json")
    for t in ufc_trades:
        team = t.get('team', '?')
        direction = t.get('direction', '?')
        k_price = t.get('k_price', '?')
        pm_price = t.get('pm_price', '?')
        spread = t.get('spread_cents', '?')
        status = t.get('status', '?')
        tier = t.get('tier', '?')
        settlement_pnl = t.get('settlement_pnl', 'NOT SET')
        actual_pnl = t.get('actual_pnl')

        print(f"\n  {team} ({direction})")
        print(f"    K: x{t.get('kalshi_fill')}@{k_price}c  PM: x{t.get('pm_fill')}@{pm_price}c")
        print(f"    Spread: {spread}c  Status: {status}  Tier: {tier}")
        print(f"    settlement_pnl: {settlement_pnl}")

        if actual_pnl:
            pc = actual_pnl.get('per_contract', {})
            print(f"    actual_pnl.net: {pc.get('net', '?')}c")
            print(f"    actual_pnl.k_cost: {pc.get('k_cost', '?')}c  pm_cost: {pc.get('pm_cost', '?')}c  total: {pc.get('total_cost', '?')}c")
            print(f"    profitable: {actual_pnl.get('is_profitable', '?')}")
        else:
            print(f"    actual_pnl: NOT SET")

        # Check all pnl-related fields
        for key in ['settlement_pnl', 'unwind_pnl_cents', 'nofill_reason']:
            val = t.get(key)
            if val is not None:
                print(f"    {key}: {val}")

    # Show the paired view math
    print("\n[2b] UFC PAIRED POSITION MATH")
    print("-" * 50)
    # The audit showed these gross values. Let's recompute with trades.json data
    for t in ufc_trades:
        team = t.get('team', '?')
        direction = t.get('direction', '?')
        k_price = t.get('k_price', 0)
        pm_price = t.get('pm_price', 0)
        if direction == 'BUY_K_SELL_PM':
            # Bought K YES at k_price, sold PM at pm_price
            # K entry = k_price (YES), PM entry = 100 - pm_price (NO side on PM)
            k_cost = k_price
            pm_cost = 100 - pm_price  # selling PM = they buy from us at pm_price, our cost = 100-pm_price
            # Actually in arb: buy K YES at k_price + buy PM NO at (100-pm_price)
            # But PM uses different pricing. pm_price is what PM showed.
            # For BUY_K_SELL_PM: we buy K YES at k_price, sell PM opposite at pm_price
            # Combined cost = k_price + (100 - pm_price) if both are YES-equivalent
            # OR k_price + pm_price if PM price is the NO side cost
            print(f"  {team}: BUY_K@{k_price}c + SELL_PM@{pm_price}c")
            print(f"    If pm_price is YES side sell: combined = {k_price}c + {100-pm_price}c = {k_price + 100 - pm_price}c")
            print(f"    If pm_price is NO side cost:  combined = {k_price}c + {pm_price}c = {k_price + pm_price}c")
        else:
            print(f"  {team}: SELL_K@{k_price}c + BUY_PM@{pm_price}c")
            print(f"    K NO entry = {100-k_price}c, PM YES entry = {pm_price}c")
            print(f"    Combined = {100-k_price}c + {pm_price}c = {100-k_price+pm_price}c")


asyncio.run(main())
