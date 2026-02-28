#!/usr/bin/env python3
"""
position_audit.py — Cross-reference positions across Kalshi, PM, and trades.json.
Flags unhedged legs, phantom positions, and missing records.
"""
import asyncio
import json
import os
import sys

# Add parent dir for imports
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from arb_executor_v7 import KalshiAPI, PolymarketUSAPI
import aiohttp


async def main():
    # ── Init APIs (same pattern as arb_executor_ws.py) ──
    kalshi_key = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
    try:
        with open(os.path.join(os.path.dirname(__file__), 'kalshi.pem')) as f:
            kalshi_pk = f.read()
    except FileNotFoundError:
        print("[ERROR] kalshi.pem not found")
        return

    pm_key = os.getenv('PM_US_API_KEY')
    pm_secret = os.getenv('PM_US_SECRET_KEY') or os.getenv('PM_US_SECRET')
    if not pm_key or not pm_secret:
        print("[ERROR] Missing PM US credentials")
        return

    kalshi_api = KalshiAPI(kalshi_key, kalshi_pk)
    pm_api = PolymarketUSAPI(pm_key, pm_secret)

    async with aiohttp.ClientSession() as session:
        # ── 1. Fetch Kalshi positions ──
        print("Fetching Kalshi positions...")
        k_positions = await kalshi_api.get_positions(session)
        if k_positions is None:
            k_positions = {}

        # ── 2. Fetch Kalshi balance ──
        k_balance = await kalshi_api.get_balance(session)

        # ── 3. Fetch PM positions ──
        print("Fetching PM positions...")
        pm_raw = await pm_api.get_positions(session)
        # pm_raw is a list or dict of position objects
        pm_positions = {}
        if isinstance(pm_raw, list):
            for p in pm_raw:
                slug = p.get('market', p.get('slug', p.get('marketSlug', '???')))
                qty = p.get('size', p.get('quantity', 0))
                if qty and float(qty) != 0:
                    pm_positions[slug] = p
        elif isinstance(pm_raw, dict):
            for key, p in pm_raw.items():
                if isinstance(p, dict):
                    qty = p.get('size', p.get('quantity', 0))
                    if qty and float(qty) != 0:
                        pm_positions[key] = p
                elif isinstance(p, list):
                    for item in p:
                        slug = item.get('market', item.get('slug', '???'))
                        qty = item.get('size', item.get('quantity', 0))
                        if qty and float(qty) != 0:
                            pm_positions[slug] = item

        # ── 4. Fetch PM balance ──
        pm_balance = await pm_api.get_balance(session)

        # ── 5. Load trades.json ──
        trades_path = os.path.join(os.path.dirname(__file__), 'trades.json')
        trades = []
        if os.path.exists(trades_path):
            with open(trades_path) as f:
                trades = json.load(f)

        # Filter to SUCCESS/HEDGED trades with fills
        active_trades = [t for t in trades if t.get('status') in ('SUCCESS', 'HEDGED', 'LIVE', 'K_FIRST_SUCCESS')
                         or (t.get('raw_status') in ('SUCCESS', 'HEDGED', 'K_FIRST_SUCCESS')
                             and t.get('hedged', False))]

    # ═══════════════════════════════════════════════════════════════
    # REPORT
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("  POSITION AUDIT REPORT")
    print("=" * 80)

    # ── Balances ──
    print(f"\n{'─'*40}")
    print(f"  BALANCES")
    print(f"{'─'*40}")
    print(f"  Kalshi:      ${k_balance:.2f}" if k_balance else "  Kalshi:      (error)")
    print(f"  Polymarket:  ${pm_balance:.2f}" if pm_balance else "  Polymarket:  (error)")
    if k_balance and pm_balance:
        print(f"  Total:       ${k_balance + pm_balance:.2f}")

    # ── Kalshi Positions ──
    print(f"\n{'─'*40}")
    print(f"  KALSHI POSITIONS ({len(k_positions)})")
    print(f"{'─'*40}")
    k_total_exposure = 0
    for ticker, pos in sorted(k_positions.items()):
        side = "YES" if pos.position > 0 else "NO"
        qty = abs(pos.position)
        exposure = pos.market_exposure / 100  # cents to dollars
        k_total_exposure += exposure
        print(f"  {ticker:<30s}  {side:>3s} x{qty:<3d}  exposure=${exposure:.2f}")
    if not k_positions:
        print("  (none)")
    print(f"  {'':30s}  TOTAL exposure=${k_total_exposure:.2f}")

    # ── PM Positions ──
    print(f"\n{'─'*40}")
    print(f"  PM POSITIONS ({len(pm_positions)})")
    print(f"{'─'*40}")
    pm_total_exposure = 0
    for slug, pos in sorted(pm_positions.items()):
        side = pos.get('side', pos.get('outcome', '?'))
        qty = pos.get('size', pos.get('quantity', 0))
        avg_price = pos.get('avgPrice', pos.get('averagePrice', pos.get('avg_price', '?')))
        cur_price = pos.get('curPrice', pos.get('currentPrice', pos.get('price', '?')))
        market_value = pos.get('pnl', pos.get('value', pos.get('marketValue', 0)))
        try:
            cost = float(qty) * float(avg_price) if avg_price != '?' else 0
            pm_total_exposure += cost
        except (ValueError, TypeError):
            cost = 0
        slug_display = slug[:45] if len(slug) > 45 else slug
        print(f"  {slug_display:<45s}  {side:>5s} x{qty:<5s}  avg={avg_price}  cur={cur_price}")
    if not pm_positions:
        print("  (none)")
    print(f"  {'':45s}  TOTAL cost~=${pm_total_exposure:.2f}")

    # ── trades.json Active Trades ──
    print(f"\n{'─'*40}")
    print(f"  TRADES.JSON ACTIVE ({len(active_trades)})")
    print(f"{'─'*40}")
    for t in active_trades:
        team = t.get('team', '?')
        direction = t.get('direction', '?')
        k_ticker = t.get('kalshi_ticker', '?')
        pm_slug_t = t.get('pm_slug', '?')
        k_fill = t.get('kalshi_fill', 0)
        pm_fill = t.get('pm_fill', 0)
        k_price = t.get('k_price', '?')
        pm_price = t.get('pm_price', '?')
        status = t.get('status', '?')
        tier = t.get('tier', '')
        ts = t.get('timestamp', '?')[:19]
        print(f"  {ts}  {team:<8s}  {direction:<15s}  K:{k_ticker} x{k_fill}@{k_price}c  PM:x{pm_fill}@{pm_price}c  [{status}] {tier}")
    if not active_trades:
        print("  (none)")

    # ═══════════════════════════════════════════════════════════════
    # RECONCILIATION
    # ═══════════════════════════════════════════════════════════════
    print(f"\n{'='*80}")
    print("  RECONCILIATION")
    print(f"{'='*80}")

    issues = []

    # Build lookup sets
    trades_k_tickers = {t.get('kalshi_ticker') for t in active_trades if t.get('kalshi_ticker')}
    trades_pm_slugs = {t.get('pm_slug') for t in active_trades if t.get('pm_slug')}

    # Kalshi positions not in trades.json
    for ticker in k_positions:
        if ticker not in trades_k_tickers:
            pos = k_positions[ticker]
            side = "YES" if pos.position > 0 else "NO"
            issues.append(f"  [PHANTOM-K] {ticker} ({side} x{abs(pos.position)}) — on Kalshi but NOT in trades.json")

    # trades.json K entries not on Kalshi
    for t in active_trades:
        k_ticker = t.get('kalshi_ticker')
        if k_ticker and k_ticker not in k_positions:
            issues.append(f"  [MISSING-K] {k_ticker} — in trades.json but NOT on Kalshi (settled or closed?)")

    # PM positions not in trades.json
    for slug in pm_positions:
        if slug not in trades_pm_slugs:
            issues.append(f"  [PHANTOM-PM] {slug[:50]} — on PM but NOT in trades.json")

    # trades.json PM entries not on PM
    for t in active_trades:
        pm_slug_t = t.get('pm_slug')
        if pm_slug_t and pm_slug_t not in pm_positions:
            issues.append(f"  [MISSING-PM] {pm_slug_t[:50]} — in trades.json but NOT on PM (settled or closed?)")

    # Unhedged legs: K position without matching PM (via trades.json linkage)
    for t in active_trades:
        k_ticker = t.get('kalshi_ticker')
        pm_slug_t = t.get('pm_slug')
        has_k = k_ticker in k_positions
        has_pm = pm_slug_t in pm_positions
        if has_k and not has_pm:
            issues.append(f"  [UNHEDGED-K] {k_ticker} — K position exists but PM leg missing ({pm_slug_t[:40]})")
        if has_pm and not has_k:
            issues.append(f"  [UNHEDGED-PM] {pm_slug_t[:40]} — PM position exists but K leg missing ({k_ticker})")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("  All positions reconciled. No issues found.")

    print(f"\n{'─'*40}")
    print(f"  SUMMARY")
    print(f"{'─'*40}")
    print(f"  Kalshi positions:  {len(k_positions)}")
    print(f"  PM positions:      {len(pm_positions)}")
    print(f"  trades.json active: {len(active_trades)}")
    print(f"  Issues found:      {len(issues)}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    asyncio.run(main())
