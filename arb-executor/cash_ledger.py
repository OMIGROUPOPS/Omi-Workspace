#!/usr/bin/env python3
"""Cash ledger: ground-truth accounting for arb executor.

Commands:
    python cash_ledger.py snapshot              # save current balances
    python cash_ledger.py reconcile             # compute reconciled_pnl on all filled trades
    python cash_ledger.py reconcile --dry-run   # show what would change without writing
    python cash_ledger.py report                # print portfolio summary
    python cash_ledger.py report --date 2026-02-17  # report for a specific date
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRADES_FILE = os.path.join(SCRIPT_DIR, "trades.json")
BALANCES_FILE = os.path.join(SCRIPT_DIR, "balances.json")
SNAPSHOTS_FILE = os.path.join(SCRIPT_DIR, "balance_snapshots.json")

STARTING_BALANCE = {
    "kalshi": 188.83,
    "pm": 128.94,
    "total": 317.77,
    "date": "2026-02-15",
}

# Import Kalshi auth from kalshi_reconciler
from kalshi_reconciler import (
    _load_private_key,
    _headers,
    pull_balance,
    KALSHI_BASE_URL,
)


# ── Balance snapshot ──────────────────────────────────────────────────────

async def _fetch_kalshi_balance() -> dict:
    """Fetch Kalshi balance from API. Returns {balance, portfolio_value} in cents."""
    private_key = _load_private_key()
    async with aiohttp.ClientSession() as session:
        return await pull_balance(session, private_key)


def _load_pm_balance() -> dict:
    """Load PM balance from balances.json (written by executor)."""
    if not os.path.exists(BALANCES_FILE):
        return {}
    with open(BALANCES_FILE, "r") as f:
        return json.load(f)


def snapshot():
    """Save current balance snapshot."""
    # Kalshi
    try:
        k_data = asyncio.run(_fetch_kalshi_balance())
        k_balance = k_data.get("balance", 0) / 100  # cents → dollars
        k_portfolio = k_data.get("portfolio_value", k_data.get("balance", 0)) / 100
    except Exception as e:
        print(f"Warning: Could not fetch Kalshi balance: {e}")
        k_balance = 0
        k_portfolio = 0

    # PM from balances.json
    pm_data = _load_pm_balance()
    pm_cash = pm_data.get("pm_cash", 0)
    pm_portfolio = pm_data.get("pm_portfolio", 0)

    snap = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kalshi_cash": round(k_balance, 2),
        "kalshi_portfolio": round(k_portfolio, 2),
        "pm_cash": round(pm_cash, 2),
        "pm_portfolio": round(pm_portfolio, 2),
        "total_portfolio": round(k_portfolio + pm_portfolio, 2),
        "cash_pnl": round(k_portfolio + pm_portfolio - STARTING_BALANCE["total"], 2),
    }

    # Append to snapshots file
    snapshots = []
    if os.path.exists(SNAPSHOTS_FILE):
        with open(SNAPSHOTS_FILE, "r") as f:
            snapshots = json.load(f)
    snapshots.append(snap)
    with open(SNAPSHOTS_FILE, "w") as f:
        json.dump(snapshots, f, indent=2)

    print(f"Balance snapshot saved:")
    print(f"  Kalshi:    ${snap['kalshi_portfolio']:.2f} (cash: ${snap['kalshi_cash']:.2f})")
    print(f"  PM:        ${snap['pm_portfolio']:.2f} (cash: ${snap['pm_cash']:.2f})")
    print(f"  Total:     ${snap['total_portfolio']:.2f}")
    print(f"  Cash P&L:  ${snap['cash_pnl']:+.2f} (vs ${STARTING_BALANCE['total']:.2f} start)")
    return snap


# ── Trade reconciliation ──────────────────────────────────────────────────

def _norm_pm(pm_price):
    """Normalize pm_price: if < 1, it's decimal (0.50 = 50c), multiply by 100."""
    if pm_price is None:
        return 0
    if isinstance(pm_price, (int, float)) and 0 < pm_price < 1:
        return pm_price * 100
    return pm_price


def reconcile_trade_pnl(t: dict) -> float | None:
    """Compute reconciled P&L for a single trade using formula-based approach.

    Formula:
        k_cost = k_price if BUY_K else (100 - k_price)
        pm_cost = (100 - pm_price) if is_short else pm_price
        spread = 100 - k_cost - pm_cost
        pnl = spread * qty / 100 - fees
    """
    filled = t.get("contracts_filled", 0) or 0
    if filled == 0:
        return None

    status = t.get("status", "")
    tier = t.get("tier", "")

    # Only reconcile completed trades
    if status not in ("SUCCESS", "EXITED") and tier not in ("TIER1_HEDGE", "TIER2_EXIT", "TIER3_UNWIND"):
        # For unhedged/open, skip
        if status == "UNHEDGED" and tier not in ("TIER3_UNWIND",):
            return None

    direction = t.get("direction", "")
    k_price = t.get("k_price", 0) or 0
    pm_price = _norm_pm(t.get("pm_price", 0))

    if k_price == 0 or pm_price == 0:
        return None

    # Determine costs
    if direction == "BUY_K_SELL_PM":
        k_cost = k_price
    else:  # BUY_PM_SELL_K
        k_cost = 100 - k_price

    # Infer PM side from direction
    is_short = t.get("pm_is_buy_short")
    if is_short is None:
        is_short = "SELL_PM" in direction

    if is_short:
        pm_cost = 100 - pm_price
    else:
        pm_cost = pm_price

    spread = 100 - k_cost - pm_cost

    # Fees
    pm_fee = t.get("pm_fee", 0) or 0
    k_fee = t.get("k_fee", 0) or 0
    total_fees = (pm_fee + k_fee) * filled / 100  # cents → dollars

    pnl = (spread * filled / 100) - total_fees

    return round(pnl, 4)


def reconcile(dry_run: bool = False):
    """Reconcile all filled trades and write reconciled_pnl."""
    if not os.path.exists(TRADES_FILE):
        print(f"Error: {TRADES_FILE} not found")
        sys.exit(1)

    with open(TRADES_FILE, "r") as f:
        trades = json.load(f)

    updated = 0
    skipped = 0
    total_pnl = 0.0

    print(f"{'DRY RUN - ' if dry_run else ''}Reconciling {len(trades)} trades...")
    print()

    for t in trades:
        filled = t.get("contracts_filled", 0) or 0
        if filled == 0:
            skipped += 1
            continue

        pnl = reconcile_trade_pnl(t)
        if pnl is None:
            skipped += 1
            continue

        old_pnl = t.get("reconciled_pnl")
        team = t.get("team", "?")
        ts = t.get("timestamp", "")[:16]

        if old_pnl != pnl:
            arrow = f"${old_pnl:+.4f} → " if old_pnl is not None else ""
            print(f"  {ts} {team:<6} {filled}x  {arrow}${pnl:+.4f}")
            if not dry_run:
                t["reconciled_pnl"] = pnl
            updated += 1
        else:
            print(f"  {ts} {team:<6} {filled}x  ${pnl:+.4f} (unchanged)")

        total_pnl += pnl

    print()
    print(f"Summary: {updated} updated, {skipped} skipped")
    print(f"Total reconciled P&L: ${total_pnl:+.4f}")

    if not dry_run and updated > 0:
        # Backup
        backup_path = TRADES_FILE + f".pre_cash_reconcile_{int(time.time())}"
        with open(backup_path, "w") as f:
            json.dump(trades, f, indent=2)
        print(f"Backup: {backup_path}")

        with open(TRADES_FILE, "w") as f:
            json.dump(trades, f, indent=2)
        print(f"Written to {TRADES_FILE}")
    elif dry_run:
        print("(dry run — no changes written)")


# ── Report ────────────────────────────────────────────────────────────────

def report(target_date: str | None = None):
    """Print portfolio summary report."""
    if not os.path.exists(TRADES_FILE):
        print(f"Error: {TRADES_FILE} not found")
        sys.exit(1)

    with open(TRADES_FILE, "r") as f:
        trades = json.load(f)

    # Filter by date if specified
    if target_date:
        trades = [t for t in trades if t.get("timestamp", "")[:10] == target_date]

    # Compute P&L from reconciled_pnl, settlement_pnl, or formula
    total_reconciled = 0.0
    total_settlement = 0.0
    total_estimated = 0.0
    reconciled_count = 0
    settlement_count = 0
    estimated_count = 0

    for t in trades:
        filled = t.get("contracts_filled", 0) or 0
        if filled == 0:
            continue

        rp = t.get("reconciled_pnl")
        sp = t.get("settlement_pnl")

        if rp is not None:
            total_reconciled += rp
            reconciled_count += 1
        elif sp is not None:
            total_settlement += sp
            settlement_count += 1
        else:
            # Compute on the fly
            pnl = reconcile_trade_pnl(t)
            if pnl is not None:
                total_estimated += pnl
                estimated_count += 1

    total_pnl = total_reconciled + total_settlement + total_estimated

    # Current balances
    pm_data = _load_pm_balance()
    pm_portfolio = pm_data.get("pm_portfolio", 0)
    k_portfolio = pm_data.get("k_portfolio", 0)
    total_portfolio = pm_portfolio + k_portfolio
    cash_pnl = total_portfolio - STARTING_BALANCE["total"]

    date_label = target_date or "All Time"
    print("=" * 60)
    print(f"  PORTFOLIO REPORT — {date_label}")
    print("=" * 60)
    print()
    print(f"  Cash P&L (headline):  ${cash_pnl:+.2f}")
    print(f"    Portfolio now:      ${total_portfolio:.2f}")
    print(f"    Starting balance:   ${STARTING_BALANCE['total']:.2f}")
    print()
    print(f"  Trade P&L breakdown:")
    print(f"    Reconciled:  ${total_reconciled:+.4f}  ({reconciled_count} trades)")
    print(f"    Settled:     ${total_settlement:+.4f}  ({settlement_count} trades)")
    print(f"    Estimated:   ${total_estimated:+.4f}  ({estimated_count} trades)")
    print(f"    Total:       ${total_pnl:+.4f}")
    print()
    gap = cash_pnl - total_pnl
    if abs(gap) > 0.01:
        print(f"  GAP: ${gap:+.2f} (cash_pnl - trade_pnl)")
        print(f"  (Unexplained by individual trade accounting)")
    print("=" * 60)


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "snapshot":
        snapshot()

    elif cmd == "reconcile":
        dry_run = "--dry-run" in sys.argv
        reconcile(dry_run=dry_run)

    elif cmd == "report":
        target_date = None
        if "--date" in sys.argv:
            idx = sys.argv.index("--date")
            if idx + 1 < len(sys.argv):
                target_date = sys.argv[idx + 1]
        report(target_date)

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
