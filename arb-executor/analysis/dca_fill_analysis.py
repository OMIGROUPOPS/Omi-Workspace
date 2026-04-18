#!/usr/bin/env python3
"""Realistic DCA fill analysis for V4 config."""
import csv, json, os
from pathlib import Path
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
TICKS_DIR = "/root/Omi-Workspace/arb-executor/analysis/match_ticks_full"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
DAYS = 28
ENTRY_CT = 10
DCA_CT = 5
DCA_FLOOR = 10

config = json.load(open(CONFIG_PATH))

facts_by_cell = defaultdict(list)
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        cat = r["category"]; side = r["side"]; entry = float(r["entry_mid"])
        bucket = int(entry / 5) * 5
        cell = "%s_%s_%d-%d" % (cat, side, bucket, bucket + 4)
        facts_by_cell[cell].append({
            "ticker": r["ticker_id"],
            "max_bounce": float(r["max_bounce_from_entry"]),
            "max_dip": float(r["max_dip_from_entry"]),
            "result": r["match_result"],
            "entry_mid": entry,
        })

def load_ticks(ticker):
    path = os.path.join(TICKS_DIR, "%s.csv" % ticker)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                rows.append(float(row[3]))
    return rows

print("=" * 100)
print("REALISTIC DCA FILL ANALYSIS — V4 (32 active cells)")
print("=" * 100)

cell_results = []

for cell_name, cfg in sorted(config["active_cells"].items()):
    matches = facts_by_cell.get(cell_name, [])
    if not matches:
        continue
    n = len(matches)
    ex = cfg["exit_cents"]
    dca_offset = cfg.get("dca_trigger_cents", 0)
    avg_entry = sum(m["entry_mid"] for m in matches) / n

    # Per-match scenario analysis
    scenario_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    total_pnl_no_dca = 0
    total_pnl_with_dca = 0
    dca_fills = 0

    for m in matches:
        entry = m["entry_mid"]
        dca_price = entry - dca_offset
        exit_target = entry + ex
        settle = 99.5 if m["result"] == "win" else 0.5

        exit_hits = m["max_bounce"] >= ex
        dca_hit = dca_offset > 0 and dca_price >= DCA_FLOOR and m["max_dip"] >= dca_offset

        # But we need to check ORDER: did DCA fill BEFORE exit?
        # Use tick data for precise sequencing
        ticks = load_ticks(m["ticker"])
        dca_filled_first = False
        exit_fired = False
        dca_fired = False

        if ticks and dca_offset > 0 and dca_price >= DCA_FLOOR:
            entry_tick = ticks[0]
            for mid in ticks:
                if not dca_fired and mid <= dca_price:
                    dca_fired = True
                if mid >= exit_target:
                    exit_fired = True
                    break
            if dca_fired:
                dca_fills += 1
        elif ticks:
            for mid in ticks:
                if mid >= exit_target:
                    exit_fired = True
                    break

        # Scenario classification
        if exit_fired and not dca_fired:
            scenario = "A"
            pnl_entry = ex * ENTRY_CT
            pnl_total = pnl_entry
        elif not exit_fired and not dca_fired:
            scenario = "B"
            pnl_entry = (settle - entry) * ENTRY_CT
            pnl_total = pnl_entry
        elif exit_fired and dca_fired:
            scenario = "C"
            pnl_entry = ex * ENTRY_CT
            pnl_dca = (exit_target - dca_price) * DCA_CT
            pnl_total = pnl_entry + pnl_dca
        else:  # dca_fired but not exit_fired
            scenario = "D"
            pnl_entry = (settle - entry) * ENTRY_CT
            pnl_dca = (settle - dca_price) * DCA_CT
            pnl_total = pnl_entry + pnl_dca

        scenario_counts[scenario] += 1

        # No-DCA baseline
        if exit_hits:
            pnl_no_dca = ex * ENTRY_CT
        else:
            pnl_no_dca = (settle - entry) * ENTRY_CT

        total_pnl_no_dca += pnl_no_dca
        total_pnl_with_dca += pnl_total

    dca_fill_rate = dca_fills / n if n > 0 else 0
    ev_no_dca = total_pnl_no_dca / n / 100.0  # dollars per match
    ev_with_dca = total_pnl_with_dca / n / 100.0
    tpd = n / DAYS
    dpd_no_dca = ev_no_dca * tpd
    dpd_with_dca = ev_with_dca * tpd
    dca_uplift = dpd_with_dca - dpd_no_dca

    cell_results.append({
        "cell": cell_name, "n": n, "exit": ex, "dca_offset": dca_offset,
        "dca_fill_rate": dca_fill_rate,
        "scenarios": scenario_counts,
        "ev_no_dca": ev_no_dca, "ev_with_dca": ev_with_dca,
        "dpd_no_dca": dpd_no_dca, "dpd_with_dca": dpd_with_dca,
        "dca_uplift": dca_uplift, "tpd": tpd, "avg_entry": avg_entry,
    })

# Sort by DCA uplift
cell_results.sort(key=lambda x: -x["dca_uplift"])

print("\n--- PER-CELL DCA ANALYSIS ---")
print("%-35s %4s %4s %5s %5s %5s %5s %5s %7s %7s %7s" % (
    "CELL", "N", "DCA", "FILL%", "A", "B", "C", "D",
    "NO_DCA", "W_DCA", "UPLIFT"))
print("-" * 100)

tot_no_dca = 0
tot_with_dca = 0

for r in cell_results:
    s = r["scenarios"]
    print("%-35s %4d  -%2d %4.0f%% %4d %4d %4d %4d $%+5.2f $%+5.2f $%+5.2f" % (
        r["cell"][:35], r["n"], r["dca_offset"],
        100*r["dca_fill_rate"],
        s["A"], s["B"], s["C"], s["D"],
        r["dpd_no_dca"], r["dpd_with_dca"], r["dca_uplift"]))
    tot_no_dca += r["dpd_no_dca"]
    tot_with_dca += r["dpd_with_dca"]

print("-" * 100)
print("AGGREGATE:")
print("  No-DCA projection:       $%.2f/day" % tot_no_dca)
print("  Empirical DCA projection: $%.2f/day" % tot_with_dca)
print("  DCA uplift:              $%.2f/day" % (tot_with_dca - tot_no_dca))

# DCA valuable vs dead
print("\n--- TOP 10: DCA MOST VALUABLE ---")
for r in cell_results[:10]:
    print("  %-35s uplift=$%+.2f/day  fill_rate=%d%%  DCA=-%dc" % (
        r["cell"], r["dca_uplift"], 100*r["dca_fill_rate"], r["dca_offset"]))

print("\n--- BOTTOM 10: DCA LEAST VALUABLE ---")
for r in cell_results[-10:]:
    print("  %-35s uplift=$%+.2f/day  fill_rate=%d%%  DCA=-%dc" % (
        r["cell"], r["dca_uplift"], 100*r["dca_fill_rate"], r["dca_offset"]))

# Refine: switch cells with negative DCA uplift to noDCA
print("\n--- DCA REFINEMENT ---")
refined = json.load(open(CONFIG_PATH))
switched = 0
for r in cell_results:
    if r["dca_uplift"] < 0.01:
        cell = r["cell"]
        if cell in refined["active_cells"]:
            old_dca = refined["active_cells"][cell].get("dca_trigger_cents", 0)
            if old_dca > 0:
                refined["active_cells"][cell]["strategy"] = "noDCA"
                if "dca_trigger_cents" in refined["active_cells"][cell]:
                    del refined["active_cells"][cell]["dca_trigger_cents"]
                switched += 1
                print("  %-35s DCA=-%dc -> noDCA (uplift=$%.2f)" % (cell, old_dca, r["dca_uplift"]))

print("\nSwitched %d cells from DCA-A to noDCA" % switched)

# Save
with open(CONFIG_PATH, "w") as f:
    json.dump(refined, f, indent=2)
print("Saved: %s" % CONFIG_PATH)

# Final aggregate
dca_cells = sum(1 for c in refined["active_cells"].values() if c.get("strategy") == "DCA-A")
nodca_cells = sum(1 for c in refined["active_cells"].values() if c.get("strategy") == "noDCA")

# Capital requirements
total_entry_cap = sum(r["avg_entry"] * ENTRY_CT / 100.0 * r["tpd"] for r in cell_results)
total_dca_cap = sum(
    (r["avg_entry"] - r["dca_offset"]) * DCA_CT / 100.0 * r["tpd"] * r["dca_fill_rate"]
    for r in cell_results if refined["active_cells"].get(r["cell"], {}).get("strategy") == "DCA-A"
)

print("\n" + "=" * 80)
print("FINAL V4 SUMMARY")
print("=" * 80)
print("Active cells:        %d (%d DCA-A, %d noDCA)" % (
    len(refined["active_cells"]), dca_cells, nodca_cells))
print("Disabled cells:      %d" % len(refined["disabled_cells"]))
print("Trades/day:          %.1f" % sum(r["tpd"] for r in cell_results))
print("$/day (realistic):   $%.2f" % tot_with_dca)
print("  Entry capital/day: $%.2f" % total_entry_cap)
print("  DCA capital/day:   $%.2f (avg, when fills)" % total_dca_cap)
print("  Total capital/day: $%.2f" % (total_entry_cap + total_dca_cap))
print("  Daily ROI:         %.1f%%" % (100 * tot_with_dca / (total_entry_cap + total_dca_cap)
      if (total_entry_cap + total_dca_cap) > 0 else 0))

print("\nDONE")
