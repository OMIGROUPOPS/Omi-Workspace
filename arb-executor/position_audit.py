#!/usr/bin/env python3
"""
position_audit.py — Cross-reference positions across Kalshi, PM, and trades.json.
Flags unhedged legs, phantom positions, and missing records.

Runs standalone or as a cron job (--cron flag suppresses console output,
writes JSON to audit_log.json).
"""
import asyncio
import json
import os
import sys
import argparse
from datetime import datetime, timezone

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

        # ── 2. Fetch Kalshi balance ──
        k_balance = await kalshi_api.get_balance(session)

        # ── 3. Fetch PM positions via SDK ──
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

        # ── 4. Fetch PM balance ──
        pm_balance = None
        try:
            pm_api_fallback = PolymarketUSAPI(pm_key, pm_secret)
            pm_balance = await pm_api_fallback.get_balance(session)
        except Exception:
            pass

        # ── 5. Load trades.json ──
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

    # Kalshi positions structured
    k_list = []
    k_total_exposure = 0
    for ticker, pos in sorted(k_positions.items()):
        side = "YES" if pos.position > 0 else "NO"
        qty = abs(pos.position)
        exposure = pos.market_exposure / 100
        k_total_exposure += exposure
        k_list.append({"ticker": ticker, "side": side, "qty": qty, "exposure": round(exposure, 2)})

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
        pm_list.append({
            "slug": slug, "outcome": outcome, "net": net,
            "cost": round(cost, 3), "cash_value": round(cash_val, 3),
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
        "kalshi_total_exposure": round(k_total_exposure, 2),
        "pm_positions": pm_list,
        "pm_total_cost": round(pm_total_cost, 3),
        "active_trades": len(active_trades),
        "issues": issues,
        "live_issue_count": len(live_issues),
        "summary": {
            "k_count": len(k_positions),
            "pm_count": len(pm_positions),
            "trades_active": len(active_trades),
            "total_issues": len(issues),
            "live_issues": len(live_issues),
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
        print(f"  KALSHI POSITIONS ({len(k_positions)})")
        print(f"{'─'*40}")
        for entry in k_list:
            print(f"  {entry['ticker']:<30s}  {entry['side']:>3s} x{entry['qty']:<3d}  exposure=${entry['exposure']:.2f}")
        if not k_list:
            print("  (none)")
        print(f"  {'':30s}  TOTAL exposure=${k_total_exposure:.2f}")

        print(f"\n{'─'*40}")
        print(f"  PM POSITIONS ({len(pm_positions)})")
        print(f"{'─'*40}")
        for entry in pm_list:
            slug_display = entry['slug'][:45]
            print(f"  {slug_display:<45s}  {entry['outcome']:>5s} x{entry['net']:<3s}  cost=${entry['cost']:.3f}  cash=${entry['cash_value']:.3f}")
            if entry['team']:
                print(f"    team={entry['team']}")
        if not pm_list:
            print("  (none)")
        print(f"  {'':45s}  TOTAL cost=${pm_total_cost:.3f}")

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
        print(f"  Kalshi positions:  {len(k_positions)}")
        print(f"  PM positions:      {len(pm_positions)}")
        print(f"  trades.json active: {len(active_trades)}")
        print(f"  Issues found:      {len(issues)} ({len(live_issues)} live)")
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
