#!/usr/bin/env python3
"""Daily recap script for arb executor P&L reporting.

Usage:
    python daily_recap.py                    # yesterday
    python daily_recap.py --date 2026-02-25  # specific date
    python daily_recap.py --today            # today so far
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRADES_FILE = os.path.join(SCRIPT_DIR, "trades.json")
BALANCES_FILE = os.path.join(SCRIPT_DIR, "balances.json")
RECAPS_DIR = os.path.join(SCRIPT_DIR, "recaps")

STARTING_BALANCE = 910.31  # Feb 26 starting point (reset after +$300 deposits)


# ── Opponent extraction (matches dashboard_push.py logic) ─────────────────

def extract_opponent(trade: dict) -> str:
    ck = trade.get("cache_key", "")
    team = trade.get("team", "")
    if not ck or not team:
        return ""
    parts = ck.split(":")
    if len(parts) < 2:
        return ""
    teams = parts[1].split("-")
    for t in teams:
        if t != team:
            return t
    return ""


# ── P&L computation (mirrors frontend tradePnl) ──────────────────────────

def norm_pm(pm_price):
    """Normalize pm_price: if < 1, it's in decimal (0.50 = 50c), multiply by 100."""
    if pm_price is None:
        return 0
    if isinstance(pm_price, (int, float)) and pm_price < 1 and pm_price > 0:
        return pm_price * 100
    return pm_price


def is_open_trade(t: dict) -> bool:
    tier = t.get("tier", "")
    if tier in ("TIER3A_HOLD", "TIER3_OPPOSITE_HEDGE", "TIER3_OPPOSITE_OVERWEIGHT"):
        return True
    if t.get("status") == "UNHEDGED" and tier != "TIER3_UNWIND":
        return True
    return False


def compute_unwind_pnl(t: dict, qty: int):
    """Compute signed unwind P&L in dollars. Returns None if insufficient data."""
    # Priority 1: New signed field
    upc = t.get("unwind_pnl_cents")
    if upc is not None:
        return upc / 100

    # Priority 2: Recompute from direction + prices
    ufp = t.get("unwind_fill_price")
    pm_price = norm_pm(t.get("pm_price", 0))
    if ufp is not None and pm_price > 0 and qty > 0:
        if t.get("direction") == "BUY_PM_SELL_K":
            return ((ufp * 100) - pm_price) * qty / 100
        else:
            return (pm_price - (ufp * 100)) * qty / 100

    # Priority 3: Old unsigned field
    ulc = t.get("unwind_loss_cents")
    if ulc is not None and ulc != 0:
        return -(abs(ulc) / 100)

    return None


def trade_pnl(t: dict) -> float | None:
    """Compute total P&L in dollars for a single trade. Returns None if unknown."""
    qty = t.get("contracts_filled", 0) or t.get("contracts_intended", 0) or 0

    # Settlement P&L takes priority
    sp = t.get("settlement_pnl")
    if sp is not None:
        return sp

    if is_open_trade(t):
        return None

    status = t.get("status", "")
    tier = t.get("tier", "")

    # EXITED / TIER3_UNWIND
    if status == "EXITED" or tier == "TIER3_UNWIND":
        return compute_unwind_pnl(t, qty)

    # SUCCESS / TIER1_HEDGE
    if status == "SUCCESS" or tier == "TIER1_HEDGE":
        apnl = t.get("actual_pnl")
        if apnl and isinstance(apnl, dict):
            npd = apnl.get("net_profit_dollars")
            if npd is not None:
                return npd
        enpc = t.get("estimated_net_profit_cents")
        if enpc is not None:
            return (enpc * qty) / 100

    # TIER2_EXIT
    if tier == "TIER2_EXIT":
        apnl = t.get("actual_pnl")
        if apnl and isinstance(apnl, dict):
            npd = apnl.get("net_profit_dollars")
            if npd is not None:
                return npd
        return compute_unwind_pnl(t, qty)

    return None


# ── Load data ─────────────────────────────────────────────────────────────

def load_trades() -> list:
    if not os.path.exists(TRADES_FILE):
        print(f"Error: {TRADES_FILE} not found", file=sys.stderr)
        sys.exit(1)
    with open(TRADES_FILE, "r") as f:
        return json.load(f)


def load_balances() -> dict | None:
    if not os.path.exists(BALANCES_FILE):
        return None
    try:
        with open(BALANCES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def filter_by_date(trades: list, target_date: str) -> list:
    """Filter trades to those whose timestamp starts with YYYY-MM-DD."""
    return [t for t in trades if t.get("timestamp", "")[:10] == target_date]


# ── Formatting ────────────────────────────────────────────────────────────

def format_trade_line(t: dict, pnl_val: float | None) -> str:
    ts = t.get("timestamp", "")
    time_str = ts[11:16] if len(ts) >= 16 else ts
    team = t.get("team", "?")
    opponent = extract_opponent(t) or "?"
    matchup = f"{team} vs {opponent}"

    direction = t.get("direction", "")
    pm_price = norm_pm(t.get("pm_price", 0))
    k_price = t.get("k_price", 0) or 0

    if direction == "BUY_PM_SELL_K":
        k_opp_cost = 100 - k_price if k_price > 0 else 0
        total_cost = pm_price + k_opp_cost
        spread = 100 - total_cost
        legs = f"PM: {team} @{pm_price:.0f}c  K: {opponent} @{k_opp_cost:.0f}c"
    else:
        total_cost = k_price + pm_price
        spread = 100 - total_cost
        legs = f"K: {team} @{k_price}c  PM: {opponent} @{pm_price:.0f}c"

    cost_str = f"[{total_cost:.0f}c\u2192{spread:.0f}c]"
    qty = t.get("contracts_filled", 0) or t.get("contracts_intended", 0) or 0
    pnl_str = f"${pnl_val:+.4f}" if pnl_val is not None else "OPEN"
    status_icon = "\u2713" if pnl_val is not None and pnl_val >= 0 else "\u2717" if pnl_val is not None else " "

    return f"  {time_str}  {status_icon} {matchup:<18} | {legs}  {cost_str:<12} | {qty:>2}x | {pnl_str}"


def generate_recap(target_date: str) -> str:
    all_trades = load_trades()
    day_trades = filter_by_date(all_trades, target_date)
    balances = load_balances()

    lines = []
    lines.append("=" * 72)
    lines.append(f"  ARB EXECUTOR DAILY RECAP — {target_date}")
    lines.append("=" * 72)
    lines.append("")

    # ── SUMMARY ───────────────────────────────────────────────────────────
    total_attempts = len(day_trades)
    fills = [t for t in day_trades if (t.get("contracts_filled") or 0) > 0]
    successes = [t for t in day_trades if t.get("status") == "SUCCESS"]
    exited = [t for t in day_trades if t.get("status") == "EXITED" or t.get("tier") == "TIER2_EXIT"]
    unhedged = [t for t in day_trades if t.get("status") == "UNHEDGED"]
    no_fills = [t for t in day_trades if t.get("status") == "PM_NO_FILL"]
    skipped = [t for t in day_trades if t.get("status") == "SKIPPED"]

    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Total attempts:   {total_attempts}")
    lines.append(f"  Fills:            {len(fills)}")
    lines.append(f"  Successes:        {len(successes)}")
    lines.append(f"  Exited/Unwind:    {len(exited)}")
    lines.append(f"  Unhedged:         {len(unhedged)}")
    lines.append(f"  No-fills:         {len(no_fills)}")
    lines.append(f"  Skipped:          {len(skipped)}")
    lines.append("")

    # ── P&L ───────────────────────────────────────────────────────────────
    pnl_entries = []
    for t in day_trades:
        pv = trade_pnl(t)
        pnl_entries.append((t, pv))

    realized = [(t, p) for t, p in pnl_entries if p is not None]
    open_trades = [(t, p) for t, p in pnl_entries if p is None and is_open_trade(t)]

    total_realized = sum(p for _, p in realized)
    wins = [(t, p) for t, p in realized if p > 0]
    losses = [(t, p) for t, p in realized if p < 0]
    total_fees = sum((t.get("pm_fee") or 0) + (t.get("k_fee") or 0) for t in day_trades)
    total_contracts = sum(t.get("contracts_filled", 0) for t in day_trades)

    reconciled = [t for t in day_trades if t.get("settlement_source") == "kalshi_reconciled"]
    estimated = [t for t, p in realized if t.get("settlement_source") != "kalshi_reconciled"]

    lines.append("P&L")
    lines.append("-" * 40)
    lines.append(f"  Realized P&L:     ${total_realized:+.4f}")
    lines.append(f"  Wins:             {len(wins)}")
    lines.append(f"  Losses:           {len(losses)}")
    lines.append(f"  Open positions:   {len(open_trades)}")
    lines.append(f"  Total fees:       ${total_fees:.4f}")
    lines.append(f"  Total contracts:  {total_contracts}")
    if reconciled:
        lines.append(f"  Reconciled (K):   {len(reconciled)} trades (Kalshi ground truth)")
    if estimated:
        lines.append(f"  Estimated:        {len(estimated)} trades (not yet reconciled)")
    if wins:
        best = max(wins, key=lambda x: x[1])
        lines.append(f"  Best trade:       ${best[1]:+.4f} ({best[0].get('team', '?')})")
    if losses:
        worst = min(losses, key=lambda x: x[1])
        lines.append(f"  Worst trade:      ${worst[1]:+.4f} ({worst[0].get('team', '?')})")
    lines.append("")

    # ── BALANCES ──────────────────────────────────────────────────────────
    lines.append("BALANCES")
    lines.append("-" * 40)
    if balances:
        k_port = balances.get("k_portfolio", 0)
        pm_port = balances.get("pm_portfolio", 0)
        total_port = k_port + pm_port
        alltime_pnl = total_port - STARTING_BALANCE
        updated = balances.get("updated_at", "N/A")
        lines.append(f"  Kalshi:           ${k_port:.2f} (cash: ${balances.get('k_cash', 0):.2f})")
        lines.append(f"  Polymarket:       ${pm_port:.2f} (cash: ${balances.get('pm_cash', 0):.2f})")
        lines.append(f"  Total portfolio:  ${total_port:.2f}")
        lines.append(f"  Starting balance: ${STARTING_BALANCE:.2f}")
        lines.append(f"  All-time P&L:     ${alltime_pnl:+.2f}")
        lines.append(f"  Last updated:     {updated}")
    else:
        lines.append("  Balances unavailable (balances.json not found)")
    lines.append("")

    # ── TRADES ────────────────────────────────────────────────────────────
    lines.append("TRADES")
    lines.append("-" * 72)
    if not day_trades:
        lines.append("  No trades on this date.")
    else:
        # Sort by timestamp
        sorted_trades = sorted(day_trades, key=lambda t: t.get("timestamp", ""))
        for t in sorted_trades:
            pv = trade_pnl(t)
            lines.append(format_trade_line(t, pv))
    lines.append("")

    # ── HOURLY ACTIVITY ───────────────────────────────────────────────────
    lines.append("HOURLY ACTIVITY")
    lines.append("-" * 40)
    hourly: dict[str, list] = defaultdict(list)
    for t in day_trades:
        ts = t.get("timestamp", "")
        if len(ts) >= 13:
            hour = ts[11:13]
            hourly[hour].append(t)
    for h in sorted(hourly.keys()):
        trades_in_hour = hourly[h]
        hour_pnl = sum(trade_pnl(t) or 0 for t in trades_in_hour)
        hour_fills = sum(1 for t in trades_in_hour if (t.get("contracts_filled") or 0) > 0)
        lines.append(f"  {h}:00  {len(trades_in_hour):>3} attempts  {hour_fills:>2} fills  ${hour_pnl:+.4f}")
    lines.append("")

    # ── BY SPORT ──────────────────────────────────────────────────────────
    lines.append("BY SPORT")
    lines.append("-" * 40)
    by_sport: dict[str, list] = defaultdict(list)
    for t in day_trades:
        by_sport[t.get("sport", "unknown")].append(t)
    for sport in sorted(by_sport.keys()):
        sport_trades = by_sport[sport]
        sport_pnl = sum(trade_pnl(t) or 0 for t in sport_trades)
        sport_fills = sum(1 for t in sport_trades if (t.get("contracts_filled") or 0) > 0)
        lines.append(f"  {sport.upper():<6}  {len(sport_trades):>3} attempts  {sport_fills:>2} fills  ${sport_pnl:+.4f}")
    lines.append("")
    lines.append("=" * 72)

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Arb executor daily recap")
    parser.add_argument("--date", type=str, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--today", action="store_true", help="Show today's recap so far")
    args = parser.parse_args()

    if args.today:
        target = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    elif args.date:
        target = args.date
    else:
        target = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    recap = generate_recap(target)

    # Print to stdout
    print(recap)

    # Save to file
    os.makedirs(RECAPS_DIR, exist_ok=True)
    out_path = os.path.join(RECAPS_DIR, f"{target}.txt")
    with open(out_path, "w") as f:
        f.write(recap)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
