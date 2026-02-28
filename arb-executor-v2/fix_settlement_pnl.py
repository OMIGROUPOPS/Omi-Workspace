#!/usr/bin/env python3
"""One-time fix: recompute settlement_pnl for all EXITED trades in trades.json.

The old settle_positions.py used:
    settlement_pnl = round(-ulc / 100, 4)

where `unwind_loss_cents` is always positive (abs() in executor_core.py).
This made ALL exited trades show as losses, even profitable unwinds.

Fix: use the same 3-priority cascade as settle_positions.py now uses:
  1. unwind_pnl_cents (signed) → /100
  2. Recompute from unwind_fill_price + pm_price + direction
  3. Fall back to -abs(unwind_loss_cents) / 100 (always loss)

Usage:
    python fix_settlement_pnl.py          # dry run (print only)
    python fix_settlement_pnl.py --apply  # actually write changes
"""

import json
import os
import sys
import shutil
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRADES_FILE = os.path.join(SCRIPT_DIR, "trades.json")


def norm_pm(pm_price):
    if pm_price is None:
        return 0
    if isinstance(pm_price, (int, float)) and pm_price < 1 and pm_price > 0:
        return pm_price * 100
    return pm_price


def compute_correct_pnl(t: dict) -> float:
    """3-priority cascade for EXITED trade P&L."""
    qty = t.get("contracts_filled", 0) or t.get("contracts_intended", 0) or 0

    # Priority 1: signed unwind_pnl_cents
    upc = t.get("unwind_pnl_cents")
    if upc is not None:
        return round(upc / 100, 4)

    # Priority 2: recompute from fill price
    ufp = t.get("unwind_fill_price")
    pm_cents = norm_pm(t.get("pm_price", 0))
    if ufp is not None and pm_cents > 0 and qty > 0:
        direction = t.get("direction", "")
        if direction == "BUY_PM_SELL_K":
            pnl_cents = ((ufp * 100) - pm_cents) * qty
        else:
            pnl_cents = (pm_cents - (ufp * 100)) * qty
        return round(pnl_cents / 100, 4)

    # Priority 3: old unsigned field (always loss)
    ulc = t.get("unwind_loss_cents")
    if ulc is not None and ulc != 0:
        return round(-abs(ulc) / 100, 4)

    return 0.0


def main():
    apply = "--apply" in sys.argv

    if not os.path.exists(TRADES_FILE):
        print(f"Error: {TRADES_FILE} not found")
        sys.exit(1)

    with open(TRADES_FILE, "r") as f:
        trades = json.load(f)

    # Find all EXITED trades (by status or settlement_source)
    fixes = []
    for i, t in enumerate(trades):
        status = t.get("status", "")
        tier = t.get("tier", "")
        ss = t.get("settlement_source", "")

        is_exited = (
            status == "EXITED"
            or tier in ("TIER2_EXIT", "TIER3_UNWIND")
            or ss == "unwind"
        )
        if not is_exited:
            continue

        old_pnl = t.get("settlement_pnl")
        new_pnl = compute_correct_pnl(t)

        if old_pnl != new_pnl:
            fixes.append((i, t, old_pnl, new_pnl))

    if not fixes:
        print("No EXITED trades need fixing.")
        print(f"(Checked {len(trades)} total trades)")
        return

    print(f"Found {len(fixes)} EXITED trade(s) to fix:\n")
    total_old = 0.0
    total_new = 0.0
    for idx, t, old, new in fixes:
        team = t.get("team", "?")
        upc = t.get("unwind_pnl_cents")
        ulc = t.get("unwind_loss_cents")
        ufp = t.get("unwind_fill_price")
        src = "upc" if upc is not None else ("recomp" if ufp else "ulc")
        old_str = f"${old:+.4f}" if old is not None else "None"
        new_str = f"${new:+.4f}"
        print(f"  [{idx}] {team}: {old_str} → {new_str}  (src={src}, upc={upc}, ulc={ulc}, ufp={ufp})")
        total_old += old or 0
        total_new += new

    print(f"\n  Total P&L change: ${total_old:+.4f} → ${total_new:+.4f} (delta: ${total_new - total_old:+.4f})")

    if not apply:
        print("\nDry run — pass --apply to write changes")
        return

    # Backup before writing
    backup_path = os.path.join(SCRIPT_DIR, f"trades_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    shutil.copy2(TRADES_FILE, backup_path)
    print(f"\nBackup saved to {backup_path}")

    for idx, t, old, new in fixes:
        trades[idx]["settlement_pnl"] = new

    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=2)

    print(f"Updated {len(fixes)} trade(s) in {TRADES_FILE}")


if __name__ == "__main__":
    main()
