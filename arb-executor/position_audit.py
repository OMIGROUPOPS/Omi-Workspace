#!/usr/bin/env python3
"""
position_audit.py — Cross-reference positions across Kalshi, PM, and trades.json.
Flags unhedged legs, phantom positions, and missing records.

Uses Kalshi fills endpoint for actual execution prices (not market_exposure).
Runs standalone or as a cron job (--cron flag suppresses console output,
writes JSON to audit_log.json).
"""
import asyncio
import json
import os
import sys
import argparse
from datetime import datetime, timezone
from collections import defaultdict

# Add parent dir for imports
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from arb_executor_v7 import KalshiAPI, PolymarketUSAPI
from polymarket_us import AsyncPolymarketUS
import aiohttp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIT_LOG_PATH = os.path.join(BASE_DIR, 'audit_log.json')


def _extract_cost(raw):
    """Extract float from cost field (can be dict or scalar)."""
    if isinstance(raw, dict):
        return float(raw.get('amount', raw.get('value', 0)))
    try:
        return float(raw)
    except (ValueError, TypeError):
        return 0.0


async def fetch_kalshi_fills(kalshi_api, session, log):
    """
    Fetch all fills from Kalshi /trade-api/v2/portfolio/fills.

    Kalshi fill fields:
      - side: 'yes' or 'no' — which side of the contract
      - action: 'buy' or 'sell' — whether you bought or sold that side
      - yes_price: price of YES side in cents
      - no_price: price of NO side (= 100 - yes_price)

    Position sign convention:
      position > 0  = holding YES  (entered via: buy yes)
      position < 0  = holding NO   (entered via: sell yes OR buy no? — Kalshi uses sell,side=no)

    From raw fill data:
      side=yes, action=buy  -> bought YES at yes_price  -> +position (YES entry)
      side=yes, action=sell -> sold YES at yes_price     -> -position (closing YES or opening NO)
      side=no,  action=buy  -> bought NO at no_price     -> -position (NO entry)
      side=no,  action=sell -> sold NO at no_price       -> +position (closing NO)

    We track entries per-side and compute VWAP based on the current position direction.
    """
    fills_by_ticker = defaultdict(lambda: {
        "fills": [],
        # YES-side entries (buy yes): qty, total_cost in yes_price
        "yes_entry_qty": 0, "yes_entry_cost": 0,
        # NO-side entries (buy no OR sell yes): qty, total_cost in no_price
        "no_entry_qty": 0, "no_entry_cost": 0,
        # Exit tracking
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
                    text = await r.text()
                    log(f"  [WARN] Fills API returned {r.status}: {text[:200]}")
                    break
                data = await r.json()
        except Exception as e:
            log(f"  [WARN] Fills fetch error: {e}")
            break

        fills = data.get('fills', [])
        if not fills:
            break

        for fl in fills:
            ticker = fl.get('ticker', '')
            if not ticker:
                continue
            side = fl.get('side', '')          # 'yes' or 'no'
            action = fl.get('action', '')      # 'buy' or 'sell'
            count = int(fl.get('count', 0))
            yes_price = int(fl.get('yes_price', 0))
            no_price = int(fl.get('no_price', 100 - yes_price))

            entry = fills_by_ticker[ticker]
            entry["fills"].append({
                "side": side,
                "action": action,
                "count": count,
                "yes_price": yes_price,
                "no_price": no_price,
                "created": fl.get('created_time', ''),
                "trade_id": fl.get('trade_id', ''),
            })

            # Kalshi fill semantics:
            #   side=yes, action=buy  -> you bought YES contracts  (YES position +)
            #   side=yes, action=sell -> you sold YES contracts    (YES position -)
            #   side=no,  action=buy  -> you bought NO contracts   (NO position +)
            #   side=no,  action=sell -> you sold NO contracts     (NO position -)
            #
            # But position convention: positive = YES, negative = NO
            # A "sell, side=no" fill with negative position means:
            #   Kalshi recorded it as selling NO, but you HOLD NO (position < 0)
            #   This is actually how Kalshi records entering a NO position on some events.
            #
            # Simple approach: track ALL fills per side with their prices.
            # YES entries = buy yes; YES exits = sell yes
            # NO entries  = buy no OR sell no (if it results in NO position)
            #
            # Since we can't determine entry vs exit from action alone on the NO side,
            # just track all fills per side and compute VWAP of ALL fills on that side.
            if side == 'yes':
                if action == 'buy':
                    entry["yes_entry_qty"] += count
                    entry["yes_entry_cost"] += count * yes_price
                else:  # sell
                    entry["yes_exit_qty"] += count
                    entry["yes_exit_cost"] += count * yes_price
            elif side == 'no':
                # For NO side: both buy and sell can be entries depending on market structure
                # Track all NO-side fills; the position direction will tell us what's an entry
                if action == 'buy':
                    entry["no_entry_qty"] += count
                    entry["no_entry_cost"] += count * no_price
                else:  # sell — on Kalshi this IS how NO positions get entered
                    entry["no_exit_qty"] += count
                    entry["no_exit_cost"] += count * no_price

        cursor = data.get('cursor', None)
        page += 1
        if not cursor or page > 20:
            break

    # Compute VWAP entry price per ticker
    # The key insight: for a given ticker, ALL fills on the same side contribute
    # to the entry price, because Kalshi can record entries as either buy or sell
    # depending on the contract structure.
    #
    # For YES positions: yes_entry (buy yes) is the entry
    # For NO positions: BOTH no_entry (buy no) AND no_exit (sell no) fills
    #   may be entries — plus YES sells create NO exposure at (100 - yes_price)
    #
    # Simplest correct approach: compute VWAP from ALL fills that could create
    # the current position, by collecting all cost on each side.
    result = {}
    for ticker, entry in fills_by_ticker.items():
        total_fills = len(entry["fills"])
        if total_fills == 0:
            continue

        # YES VWAP: from YES buys
        yes_vwap = 0
        yes_total_qty = entry["yes_entry_qty"]
        if yes_total_qty > 0:
            yes_vwap = entry["yes_entry_cost"] / yes_total_qty

        # NO VWAP: from ALL NO-side fills (both buy and sell)
        # PLUS YES sells that create NO exposure
        no_all_qty = entry["no_entry_qty"] + entry["no_exit_qty"]
        no_all_cost = entry["no_entry_cost"] + entry["no_exit_cost"]

        # YES sells also create NO exposure at no_price (100 - yes_price)
        if entry["yes_exit_qty"] > 0:
            avg_yes_sell_price = entry["yes_exit_cost"] / entry["yes_exit_qty"]
            no_via_yes_sell_price = 100 - avg_yes_sell_price
            no_all_qty += entry["yes_exit_qty"]
            no_all_cost += entry["yes_exit_qty"] * no_via_yes_sell_price

        no_vwap = 0
        if no_all_qty > 0:
            no_vwap = no_all_cost / no_all_qty

        result[ticker] = {
            "yes_entry_qty": yes_total_qty,
            "yes_vwap": round(yes_vwap, 1),
            "no_entry_qty": no_all_qty,
            "no_vwap": round(no_vwap, 1),
            "fills_count": total_fills,
            "fills": entry["fills"],
        }

    return result


async def run_audit(quiet=False):
    """Run full audit and return structured result dict."""
    log = lambda *a, **kw: (print(*a, **kw) if not quiet else None)

    # ── Init APIs ──
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
        # ── 1. Fetch Kalshi positions ──
        log("Fetching Kalshi positions...")
        k_positions = await kalshi_api.get_positions(session)
        if k_positions is None:
            k_positions = {}

        # ── 2. Fetch Kalshi fills (actual execution prices) ──
        log("Fetching Kalshi fills...")
        k_fills = await fetch_kalshi_fills(kalshi_api, session, log)
        log(f"  Got fills for {len(k_fills)} tickers")

        # ── 3. Fetch Kalshi balance ──
        k_balance = await kalshi_api.get_balance(session)

        # ── 4. Fetch PM positions via SDK ──
        log("Fetching PM positions via SDK...")
        pm_positions = {}
        try:
            pm_resp = await pm_sdk.portfolio.positions()
            raw_positions = pm_resp.get('positions', {})
            for slug, pos in raw_positions.items():
                net = int(pos.get('netPosition', 0))
                if net != 0:
                    pm_positions[slug] = pos
            log(f"  SDK returned {len(raw_positions)} total, {len(pm_positions)} with net != 0")
        except Exception as e:
            log(f"[ERROR] PM SDK portfolio.positions() failed: {e}")

        # ── 5. Fetch PM balance ──
        pm_balance = None
        try:
            pm_api_fallback = PolymarketUSAPI(pm_key, pm_secret)
            pm_balance = await pm_api_fallback.get_balance(session)
        except Exception:
            pass

        # ── 6. Load trades.json ──
        trades_path = os.path.join(BASE_DIR, 'trades.json')
        trades = []
        if os.path.exists(trades_path):
            with open(trades_path) as f:
                trades = json.load(f)

        active_trades = [t for t in trades if t.get('status') in ('SUCCESS', 'HEDGED', 'LIVE', 'K_FIRST_SUCCESS')
                         or (t.get('raw_status') in ('SUCCESS', 'HEDGED', 'K_FIRST_SUCCESS')
                             and t.get('hedged', False))]

    # ═══════════════════════════════════════════════════════════════
    # BUILD STRUCTURED RESULT
    # ═══════════════════════════════════════════════════════════════

    # Kalshi positions structured — now with fill-based entry prices
    k_list = []
    k_total_cost = 0
    k_total_exposure = 0
    for ticker, pos in sorted(k_positions.items()):
        side = "YES" if pos.position > 0 else "NO"
        qty = abs(pos.position)
        exposure = pos.market_exposure / 100
        k_total_exposure += exposure

        # Get actual entry price from fills — pick VWAP matching position side
        fill_data = k_fills.get(ticker, {})
        fills_count = fill_data.get("fills_count", 0)
        if side == "YES":
            entry_cents = fill_data.get("yes_vwap", 0)
            entry_qty = fill_data.get("yes_entry_qty", 0)
        else:
            entry_cents = fill_data.get("no_vwap", 0)
            entry_qty = fill_data.get("no_entry_qty", 0)
        cost_dollars = (entry_cents * qty) / 100 if entry_cents else exposure
        k_total_cost += cost_dollars

        k_list.append({
            "ticker": ticker,
            "side": side,
            "qty": qty,
            "entry_cents": entry_cents,
            "exposure": round(exposure, 2),
            "cost": round(cost_dollars, 2),
            "fills_count": fills_count,
        })

    # PM positions structured
    pm_list = []
    pm_total_cost = 0
    for slug, pos in sorted(pm_positions.items()):
        net = pos.get('netPosition', '0')
        cost = _extract_cost(pos.get('cost', 0))
        pm_total_cost += cost
        meta = pos.get('marketMetadata', {})
        outcome = meta.get('outcome', '?')
        team_abbr = meta.get('team', {}).get('abbreviation', '')
        cash_val = _extract_cost(pos.get('cashValue', 0))
        # PM cost is total cost — derive per-contract entry
        net_int = abs(int(net)) if net else 0
        entry_cents = round(cost / net_int * 100, 1) if net_int > 0 else 0
        pm_list.append({
            "slug": slug, "outcome": outcome, "net": net,
            "cost": round(cost, 3), "cash_value": round(cash_val, 3),
            "entry_cents": entry_cents,
            "team": team_abbr,
        })

    # Reconciliation
    issues = []
    trades_k_tickers = {t.get('kalshi_ticker') for t in active_trades if t.get('kalshi_ticker')}
    trades_pm_slugs = {t.get('pm_slug') for t in active_trades if t.get('pm_slug')}

    for ticker in k_positions:
        if ticker not in trades_k_tickers:
            pos = k_positions[ticker]
            side = "YES" if pos.position > 0 else "NO"
            issues.append({"type": "PHANTOM_K", "ticker": ticker, "side": side, "qty": abs(pos.position)})

    for t in active_trades:
        k_ticker = t.get('kalshi_ticker')
        if k_ticker and k_ticker not in k_positions:
            issues.append({"type": "MISSING_K", "ticker": k_ticker})

    for slug in pm_positions:
        if slug not in trades_pm_slugs:
            issues.append({"type": "PHANTOM_PM", "slug": slug})

    for t in active_trades:
        pm_slug_t = t.get('pm_slug')
        if pm_slug_t and pm_slug_t not in pm_positions:
            issues.append({"type": "MISSING_PM", "slug": pm_slug_t})

    for t in active_trades:
        k_ticker = t.get('kalshi_ticker')
        pm_slug_t = t.get('pm_slug')
        has_k = k_ticker in k_positions
        has_pm = pm_slug_t in pm_positions
        if has_k and not has_pm:
            issues.append({"type": "UNHEDGED_K", "ticker": k_ticker, "pm_slug": pm_slug_t})
        if has_pm and not has_k:
            issues.append({"type": "UNHEDGED_PM", "slug": pm_slug_t, "k_ticker": k_ticker})

    # Price cross-check: compare fill entry price vs trades.json k_price
    # NOTE: trades.json k_price is ALWAYS the YES-side price on Kalshi,
    # regardless of direction. For BUY_PM_SELL_K (selling K), k_price is
    # the YES price they sold at. So always compare against yes_vwap.
    price_mismatches = []
    for t in active_trades:
        k_ticker = t.get('kalshi_ticker')
        if not k_ticker or k_ticker not in k_fills:
            continue
        trades_price = t.get('k_price')
        if trades_price is None:
            continue
        fill_data = k_fills[k_ticker]
        fill_entry = fill_data.get('yes_vwap', 0)
        if fill_entry == 0:
            continue
        if abs(float(trades_price) - fill_entry) >= 1.0:
            price_mismatches.append({
                "ticker": k_ticker,
                "trades_json_price": float(trades_price),
                "fill_price": fill_entry,
                "delta": round(fill_entry - float(trades_price), 1),
            })

    # Count only live issues (skip MISSING which are settled)
    live_issues = [i for i in issues if i['type'] not in ('MISSING_K', 'MISSING_PM')]

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "balances": {
            "kalshi": round(k_balance, 2) if k_balance else None,
            "polymarket": round(pm_balance, 2) if pm_balance else None,
            "total": round((k_balance or 0) + (pm_balance or 0), 2),
        },
        "kalshi_positions": k_list,
        "kalshi_total_cost": round(k_total_cost, 2),
        "kalshi_total_exposure": round(k_total_exposure, 2),
        "pm_positions": pm_list,
        "pm_total_cost": round(pm_total_cost, 3),
        "active_trades": len(active_trades),
        "issues": issues,
        "price_mismatches": price_mismatches,
        "live_issue_count": len(live_issues),
        "summary": {
            "k_count": len(k_positions),
            "pm_count": len(pm_positions),
            "trades_active": len(active_trades),
            "total_issues": len(issues),
            "live_issues": len(live_issues),
            "price_mismatches": len(price_mismatches),
        }
    }

    # ═══════════════════════════════════════════════════════════════
    # CONSOLE REPORT (unless quiet)
    # ═══════════════════════════════════════════════════════════════
    if not quiet:
        print("\n" + "=" * 80)
        print("  POSITION AUDIT REPORT")
        print("=" * 80)

        print(f"\n{'─'*40}")
        print(f"  BALANCES")
        print(f"{'─'*40}")
        print(f"  Kalshi:      ${k_balance:.2f}" if k_balance else "  Kalshi:      (error)")
        print(f"  Polymarket:  ${pm_balance:.2f}" if pm_balance else "  Polymarket:  (error)")
        if k_balance and pm_balance:
            print(f"  Total:       ${k_balance + pm_balance:.2f}")

        print(f"\n{'─'*40}")
        print(f"  KALSHI POSITIONS ({len(k_positions)}) — entry from fills API")
        print(f"{'─'*40}")
        for entry in k_list:
            entry_str = f"entry={entry['entry_cents']:.0f}c" if entry['entry_cents'] else "entry=?"
            print(f"  {entry['ticker']:<40s} {entry['side']:>3s} x{entry['qty']:<3d} {entry_str:<12s} cost=${entry['cost']:.2f}")
        if not k_list:
            print("  (none)")
        print(f"  {'':40s} TOTAL cost=${k_total_cost:.2f}  exposure=${k_total_exposure:.2f}")

        print(f"\n{'─'*40}")
        print(f"  PM POSITIONS ({len(pm_positions)}) — entry from SDK cost")
        print(f"{'─'*40}")
        for entry in pm_list:
            slug_display = entry['slug'][:40]
            entry_str = f"entry={entry['entry_cents']:.0f}c" if entry['entry_cents'] else "entry=?"
            print(f"  {slug_display:<40s} {entry['outcome']:>12s} x{entry['net']:<4s} {entry_str:<12s} cost=${entry['cost']:.3f}")
        if not pm_list:
            print("  (none)")
        print(f"  {'':40s} TOTAL cost=${pm_total_cost:.3f}")

        # ── ENTRY PRICE CROSS-CHECK ──
        print(f"\n{'─'*40}")
        print(f"  ENTRY PRICE CROSS-CHECK (fills vs trades.json)")
        print(f"{'─'*40}")
        checked = 0
        for t in active_trades:
            k_ticker = t.get('kalshi_ticker')
            if not k_ticker or k_ticker not in k_fills:
                continue
            trades_price = t.get('k_price')
            if trades_price is None:
                continue
            fill_data = k_fills[k_ticker]
            # k_price in trades.json is always the YES-side price
            fill_entry = fill_data.get('yes_vwap', 0)
            if fill_entry == 0:
                continue
            checked += 1
            delta = fill_entry - float(trades_price)
            flag = " *** MISMATCH" if abs(delta) >= 1.0 else ""
            print(f"  {k_ticker:<40s}  trades={trades_price}c  fills={fill_entry:.0f}c  delta={delta:+.1f}c{flag}")
        if checked == 0:
            print("  (no tickers to cross-check)")
        if price_mismatches:
            print(f"\n  WARNING: {len(price_mismatches)} price mismatches detected!")
            for pm in price_mismatches:
                print(f"    {pm['ticker']}: trades.json={pm['trades_json_price']}c, actual fill={pm['fill_price']}c ({pm['delta']:+.1f}c)")
        elif checked > 0:
            print(f"\n  All {checked} prices match within 1c tolerance.")

        # ── PAIRED POSITION VIEW ──
        print(f"\n{'─'*40}")
        print(f"  PAIRED POSITIONS (K + PM hedge view)")
        print(f"{'─'*40}")
        # Build PM lookup by trades.json linkage
        for t in active_trades:
            k_ticker = t.get('kalshi_ticker', '')
            pm_slug_t = t.get('pm_slug', '')
            if not k_ticker:
                continue
            k_pos = k_positions.get(k_ticker)
            pm_pos_data = pm_positions.get(pm_slug_t)
            if not k_pos and not pm_pos_data:
                continue  # Both settled

            # K side
            k_side = "?"
            k_qty = 0
            k_entry = 0
            if k_pos:
                k_side = "YES" if k_pos.position > 0 else "NO"
                k_qty = abs(k_pos.position)
                k_fill_data = k_fills.get(k_ticker, {})
                if k_side == "YES":
                    k_entry = k_fill_data.get('yes_vwap', 0)
                else:
                    k_entry = k_fill_data.get('no_vwap', 0)

            # PM side
            pm_outcome = "?"
            pm_net = "0"
            pm_entry = 0
            if pm_pos_data:
                meta = pm_pos_data.get('marketMetadata', {})
                pm_outcome = meta.get('outcome', '?')
                pm_net = pm_pos_data.get('netPosition', '0')
                pm_cost = _extract_cost(pm_pos_data.get('cost', 0))
                net_int = abs(int(pm_net)) if pm_net else 0
                pm_entry = round(pm_cost / net_int * 100, 1) if net_int > 0 else 0

            # Combined cost — simple addition
            # pm_entry from SDK = actual cash outlay: buy price (longs) or collateral (shorts)
            # k_entry from fills = actual entry price (YES or NO VWAP)
            # For a valid arb (opposite sides): combined ~96-100c, payout=100c, gross=0-4c
            # If combined < 90c → likely same-side double (NOT an arb)
            # If combined > 100c → negative arb (overpaid)
            if k_entry and pm_entry:
                combined = k_entry + pm_entry
                payout = 100
                gross_profit = payout - combined
                status_str = "LOCKED" if k_pos and pm_pos_data else ("K-ONLY" if k_pos else "PM-ONLY")
                flag = ""
                if combined < 90:
                    flag = " !! SAME-SIDE?"
                elif combined > 100:
                    flag = " !! NEG-ARB"
                print(f"  {t.get('team', '?'):<6s} K:{k_side}@{k_entry:.0f}c + PM:{pm_outcome[:6]}@{pm_entry:.0f}c = {combined:.0f}c/{payout}c  gross={gross_profit:.0f}c  [{status_str}]{flag}")
            elif k_pos:
                print(f"  {t.get('team', '?'):<6s} K:{k_side}@{k_entry:.0f}c + PM:SETTLED  [K-ONLY]")
            elif pm_pos_data:
                print(f"  {t.get('team', '?'):<6s} K:SETTLED + PM:{pm_outcome[:6]}@{pm_entry:.0f}c  [PM-ONLY]")

        print(f"\n{'─'*40}")
        print(f"  TRADES.JSON ACTIVE ({len(active_trades)})")
        print(f"{'─'*40}")
        for t in active_trades:
            team = t.get('team', '?')
            direction = t.get('direction', '?')
            k_ticker = t.get('kalshi_ticker', '?')
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

        print(f"\n{'='*80}")
        print("  RECONCILIATION")
        print(f"{'='*80}")
        if issues:
            for issue in issues:
                itype = issue['type']
                if itype == 'PHANTOM_K':
                    print(f"  [PHANTOM-K] {issue['ticker']} ({issue['side']} x{issue['qty']}) -- on Kalshi but NOT in trades.json")
                elif itype == 'MISSING_K':
                    print(f"  [MISSING-K] {issue['ticker']} -- in trades.json but NOT on Kalshi (settled?)")
                elif itype == 'PHANTOM_PM':
                    print(f"  [PHANTOM-PM] {issue['slug'][:50]} -- on PM but NOT in trades.json")
                elif itype == 'MISSING_PM':
                    print(f"  [MISSING-PM] {issue['slug'][:50]} -- in trades.json but NOT on PM (settled?)")
                elif itype == 'UNHEDGED_K':
                    print(f"  [UNHEDGED-K] {issue['ticker']} -- K position exists but PM leg missing ({issue['pm_slug'][:40]})")
                elif itype == 'UNHEDGED_PM':
                    print(f"  [UNHEDGED-PM] {issue['slug'][:40]} -- PM position exists but K leg missing ({issue['k_ticker']})")
        else:
            print("  All positions reconciled. No issues found.")

        print(f"\n{'─'*40}")
        print(f"  SUMMARY")
        print(f"{'─'*40}")
        print(f"  Kalshi positions:   {len(k_positions)}")
        print(f"  PM positions:       {len(pm_positions)}")
        print(f"  trades.json active: {len(active_trades)}")
        print(f"  Issues found:       {len(issues)} ({len(live_issues)} live)")
        print(f"  Price mismatches:   {len(price_mismatches)}")
        print(f"{'='*80}\n")

    return result


def save_audit_log(result):
    """Append result to audit_log.json (rolling list, max 500 entries)."""
    log = []
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH) as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []

    log.append(result)
    # Keep last 500 entries
    if len(log) > 500:
        log = log[-500:]

    with open(AUDIT_LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)


async def main():
    parser = argparse.ArgumentParser(description='Position Audit')
    parser.add_argument('--cron', action='store_true', help='Cron mode: quiet output, save JSON log')
    parser.add_argument('--json', action='store_true', help='Print JSON result to stdout')
    args = parser.parse_args()

    result = await run_audit(quiet=args.cron)
    if result is None:
        sys.exit(1)

    # Always save to audit log
    save_audit_log(result)

    if args.json:
        print(json.dumps(result, indent=2))

    # Return exit code based on live issues
    if result['live_issue_count'] > 0 and args.cron:
        sys.exit(2)  # Signal issues to cron


if __name__ == '__main__':
    asyncio.run(main())
