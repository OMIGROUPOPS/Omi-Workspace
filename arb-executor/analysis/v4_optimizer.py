#!/usr/bin/env python3
"""
V4 cell optimizer. Single-entry, EV-optimal exit + DCA per cell.
Uses full 808-match dataset with tick-level max_bounce data.
"""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
TICKS_DIR = "/root/Omi-Workspace/arb-executor/analysis/match_ticks_full"
DAYS = 28
CONTRACTS = 10
DCA_QTY = 5
DCA_FLOOR = 10
MIN_N = 5

# Load all facts
facts = []
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        facts.append(r)

def get_cell(cat, side, mid):
    bucket = int(mid / 5) * 5
    return "%s_%s_%d-%d" % (cat, side, bucket, bucket + 4)

def load_dip(ticker):
    """Load max dip below entry from tick data."""
    path = os.path.join(TICKS_DIR, "%s.csv" % ticker)
    if not os.path.exists(path):
        return 0
    mids = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                mids.append(float(row[3]))
    if not mids:
        return 0
    return mids[0] - min(mids)

# Group by cell
cell_matches = defaultdict(list)
for r in facts:
    cat = r["category"]
    side = r["side"]
    entry_mid = float(r["entry_mid"])
    max_bounce = float(r["max_bounce_from_entry"])
    max_dip = float(r["max_dip_from_entry"])
    result = r["match_result"]
    cell = get_cell(cat, side, entry_mid)

    # Get event ticker for mirror analysis
    tk = r["ticker_id"]
    parts = tk.rsplit("-", 1)
    event = parts[0] if len(parts) == 2 else tk

    cell_matches[cell].append({
        "ticker": tk, "event": event,
        "entry_mid": entry_mid, "max_bounce": max_bounce,
        "max_dip": max_dip, "result": result,
        "category": cat, "side": side,
    })

# Map events to their cells (for mirror analysis)
event_cells = defaultdict(set)
for cell, matches in cell_matches.items():
    for m in matches:
        event_cells[m["event"]].add(cell)

# ============================================================
# Optimize each cell
# ============================================================
results = []

all_cells = sorted(cell_matches.keys())
print("Optimizing %d cells..." % len(all_cells), flush=True)

for cell in all_cells:
    matches = cell_matches[cell]
    n = len(matches)
    if n < MIN_N:
        continue

    cat_side = cell.rsplit("_", 1)
    avg_entry = sum(m["entry_mid"] for m in matches) / n

    # STEP 1: Exit optimization (1c granularity)
    best_ev = -9999
    best_exit = 0
    best_hit_rate = 0

    for ex in range(5, 61):
        total_pnl = 0
        hits = 0
        for m in matches:
            if m["max_bounce"] >= ex:
                total_pnl += ex
                hits += 1
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                total_pnl += (settle - m["entry_mid"])
        ev = total_pnl / n
        if ev > best_ev:
            best_ev = ev
            best_exit = ex
            best_hit_rate = hits / n

    # STEP 2: DCA optimization
    best_dca = 0  # 0 = noDCA
    best_dca_ev = best_ev

    for dca_drop in range(5, 36):
        dca_price = avg_entry - dca_drop
        if dca_price < DCA_FLOOR:
            continue

        total_pnl = 0
        for m in matches:
            entry = m["entry_mid"]
            dca_p = entry - dca_drop
            if dca_p < DCA_FLOOR:
                # Can't DCA this match, treat as noDCA
                if m["max_bounce"] >= best_exit:
                    total_pnl += best_exit * CONTRACTS
                else:
                    settle = 99.5 if m["result"] == "win" else 0.5
                    total_pnl += (settle - entry) * CONTRACTS
                continue

            dca_fills = m["max_dip"] >= dca_drop
            exit_target = entry + best_exit

            if m["max_bounce"] >= best_exit:
                # Exit hit on entry position
                pnl_entry = best_exit * CONTRACTS
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                pnl_entry = (settle - entry) * CONTRACTS

            if dca_fills:
                # DCA filled at dca_p, exit at entry + best_exit
                if exit_target <= 99:
                    # Check if exit_target was reached AFTER dca fill
                    # Approximate: if max_bounce >= best_exit, exit hit for DCA too
                    if m["max_bounce"] >= best_exit:
                        pnl_dca = (exit_target - dca_p) * DCA_QTY
                    else:
                        settle = 99.5 if m["result"] == "win" else 0.5
                        pnl_dca = (settle - dca_p) * DCA_QTY
                else:
                    settle = 99.5 if m["result"] == "win" else 0.5
                    pnl_dca = (settle - dca_p) * DCA_QTY
                total_pnl += pnl_entry + pnl_dca
            else:
                total_pnl += pnl_entry

        ev_with_dca = total_pnl / n / CONTRACTS  # normalize back to per-contract
        if ev_with_dca > best_dca_ev:
            best_dca_ev = ev_with_dca
            best_dca = dca_drop

    # STEP 3: Mirror frequency
    mirror_active_count = 0
    for m in matches:
        event_cell_set = event_cells.get(m["event"], set())
        other_cells = event_cell_set - {cell}
        if other_cells:
            mirror_active_count += 1
    mirror_freq = mirror_active_count / n

    # Compute final metrics
    strategy = "DCA-A" if best_dca > 0 else "noDCA"
    ev_cents = best_dca_ev if best_dca > 0 else best_ev
    ev_dollars = ev_cents * CONTRACTS / 100.0
    entry_cost = avg_entry * CONTRACTS / 100.0
    roi_per_trade = 100 * ev_dollars / entry_cost if entry_cost > 0 else 0
    trades_per_day = n / DAYS
    dpd = ev_cents * CONTRACTS / 100.0 * trades_per_day
    daily_roi = roi_per_trade * trades_per_day / 100 if entry_cost > 0 else 0

    # Status
    status = "ACTIVE" if ev_cents > 0 else "DISABLED"

    results.append({
        "cell": cell,
        "category": cell.split("_")[0] + "_" + cell.split("_")[1],
        "side": cell.split("_")[2],
        "bucket": cell.split("_")[-1],
        "exit": best_exit,
        "dca": best_dca,
        "strategy": strategy,
        "n": n,
        "hit_rate": best_hit_rate,
        "ev_cents": round(ev_cents, 1),
        "ev_dollars": round(ev_dollars, 4),
        "roi_pct": round(roi_per_trade, 1),
        "mirror_freq": round(100 * mirror_freq),
        "trades_day": round(trades_per_day, 2),
        "dpd": round(dpd, 2),
        "daily_roi": round(daily_roi, 2),
        "status": status,
        "avg_entry": round(avg_entry, 1),
    })

# Sort: active by $/day desc, then disabled
active = sorted([r for r in results if r["status"] == "ACTIVE"], key=lambda x: -x["dpd"])
disabled = sorted([r for r in results if r["status"] == "DISABLED"], key=lambda x: x["cell"])

# ============================================================
# STEP 4: Output table
# ============================================================
print("\n" + "=" * 140)
print("V4 CELL OPTIMIZATION RESULTS")
print("=" * 140)
print("%-35s %4s %4s %4s %5s %5s %7s %6s %6s %6s %5s %7s %7s %s" % (
    "CELL", "EXIT", "DCA", "N", "HIT%", "EV_c", "EV_$", "ROI%", "MIR%", "TR/D", "$/D", "D_ROI%", "STRAT", "STATUS"))
print("-" * 140)

for r in active:
    print("%-35s +%3d %4s %4d %4.0f%% %+5.1f $%+5.3f %+5.1f%% %4d%% %5.2f $%+5.2f %+5.1f%% %-6s ACTIVE" % (
        r["cell"], r["exit"],
        "-%d" % r["dca"] if r["dca"] > 0 else "-",
        r["n"], 100*r["hit_rate"], r["ev_cents"], r["ev_dollars"],
        r["roi_pct"], r["mirror_freq"], r["trades_day"], r["dpd"], r["daily_roi"],
        r["strategy"]))

print("-" * 140)
for r in disabled:
    print("%-35s +%3d %4s %4d %4.0f%% %+5.1f $%+5.3f %+5.1f%% %4d%% %5.2f $%+5.2f %+5.1f%% %-6s DISABLED" % (
        r["cell"], r["exit"],
        "-%d" % r["dca"] if r["dca"] > 0 else "-",
        r["n"], 100*r["hit_rate"], r["ev_cents"], r["ev_dollars"],
        r["roi_pct"], r["mirror_freq"], r["trades_day"], r["dpd"], r["daily_roi"],
        r["strategy"]))

# ============================================================
# STEP 5: Aggregate summary
# ============================================================
print("\n" + "=" * 80)
print("AGGREGATE SUMMARY")
print("=" * 80)

total_active = len(active)
total_dpd = sum(r["dpd"] for r in active)
total_trades = sum(r["trades_day"] for r in active)
avg_ev = sum(r["ev_cents"] * r["n"] for r in active) / sum(r["n"] for r in active) if active else 0
total_capital_day = sum(r["avg_entry"] * r["n"] / DAYS * CONTRACTS / 100.0 for r in active)
total_daily_roi = 100 * total_dpd / total_capital_day if total_capital_day > 0 else 0

# Double-entry frequency
all_events = set()
double_events = 0
for r in facts:
    tk = r["ticker_id"]
    event = tk.rsplit("-", 1)[0]
    all_events.add(event)
double_events = sum(1 for ev, cells in event_cells.items()
                    if sum(1 for c in cells if any(a["cell"] == c for a in active)) >= 2)
double_pct = 100 * double_events / len(all_events) if all_events else 0

print("\nActive cells:          %d" % total_active)
print("Disabled cells:        %d" % len(disabled))
print("Total trades/day:      %.1f" % total_trades)
print("Total $/day @10ct:     $%.2f" % total_dpd)
print("Total capital/day:     $%.2f" % total_capital_day)
print("Daily ROI:             %.1f%%" % total_daily_roi)
print("Avg per-trade EV:      %.1fc" % avg_ev)
print("Double-entry matches:  %d/%d = %.0f%%" % (double_events, len(all_events), double_pct))

# ============================================================
# STEP 6: Generate deploy_v4.json
# ============================================================
v4_config = {
    "sizing": {"entry_contracts": 10, "dca_contracts": 5},
    "dca_fill_floor_cents": 10,
    "active_cells": {},
    "disabled_cells": [],
}

for r in active:
    entry = {"strategy": r["strategy"], "exit_cents": r["exit"]}
    if r["strategy"] == "DCA-A":
        entry["dca_trigger_cents"] = r["dca"]
    v4_config["active_cells"][r["cell"]] = entry

for r in disabled:
    v4_config["disabled_cells"].append(r["cell"])

v4_path = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
with open(v4_path, "w") as f:
    json.dump(v4_config, f, indent=2)
print("\nSaved: %s" % v4_path)

# Also print the JSON
print("\n" + "=" * 80)
print("deploy_v4.json")
print("=" * 80)
print(json.dumps(v4_config, indent=2))

print("\nDONE")
