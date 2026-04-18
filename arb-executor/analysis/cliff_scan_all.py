#!/usr/bin/env python3
"""Apply 3 changes + cliff scan all remaining cells."""
import csv, json, os
from pathlib import Path
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
TICKS_DIR = "/root/Omi-Workspace/arb-executor/analysis/match_ticks_full"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
DAYS = 28; CT = 10

config = json.load(open(CONFIG_PATH))

# Apply 3 changes
print("=== APPLYING 3 CHANGES ===")

# 1
config["active_cells"]["WTA_MAIN_underdog_35-39"]["exit_cents"] = 26
print("  WTA_MAIN_underdog_35-39: +27c -> +26c")

# 2
config["active_cells"]["WTA_MAIN_underdog_40-44"]["exit_cents"] = 48
print("  WTA_MAIN_underdog_40-44: +49c -> +48c")

# 3
del config["active_cells"]["ATP_MAIN_leader_60-64"]
config["disabled_cells"].append("ATP_MAIN_leader_60-64")
config["disabled_cells"].sort()
print("  ATP_MAIN_leader_60-64: DISABLED")

with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=2)
print("Saved.\n")

# Load facts
facts_by_cell = defaultdict(list)
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        entry = float(r["entry_mid"])
        bucket = int(entry / 5) * 5
        cell = "%s_%s_%d-%d" % (r["category"], r["side"], bucket, bucket + 4)
        facts_by_cell[cell].append({
            "max_bounce": float(r["max_bounce_from_entry"]),
            "result": r["match_result"], "entry_mid": entry,
        })

def hit_rate_at(matches, ex):
    if not matches:
        return 0
    return sum(1 for m in matches if m["max_bounce"] >= ex) / len(matches)

def ev_at(matches, ex):
    if not matches:
        return 0
    total = 0
    for m in matches:
        if m["max_bounce"] >= ex:
            total += ex
        else:
            settle = 99.5 if m["result"] == "win" else 0.5
            total += (settle - m["entry_mid"])
    return total / len(matches)

def dpd_at(matches, ex):
    return ev_at(matches, ex) * CT / 100.0 * len(matches) / DAYS

# Already analyzed cells (skip)
already_done = {
    "ATP_CHALL_underdog_40-44", "ATP_MAIN_underdog_35-39",
    "WTA_MAIN_underdog_35-39", "WTA_MAIN_underdog_40-44",
    "ATP_MAIN_leader_60-64", "ATP_CHALL_leader_65-69",
}

print("=== CLIFF SCAN: ALL REMAINING ACTIVE CELLS ===\n")
print("%-35s %4s %4s %6s %6s %6s %6s %s" % (
    "CELL", "N", "EXIT", "HR-1", "HR_CUR", "HR+1", "$/DAY", "STATUS"))
print("-" * 100)

cliff_cells = []

for cell_name, cfg in sorted(config["active_cells"].items()):
    if cell_name in already_done:
        continue
    matches = facts_by_cell.get(cell_name, [])
    if not matches:
        continue
    n = len(matches)
    ex = cfg["exit_cents"]

    hr_minus = hit_rate_at(matches, ex - 1) if ex > 5 else 0
    hr_cur = hit_rate_at(matches, ex)
    hr_plus = hit_rate_at(matches, ex + 1)

    dpd = dpd_at(matches, ex)
    dpd_minus = dpd_at(matches, ex - 1) if ex > 5 else 0
    dpd_plus = dpd_at(matches, ex + 1)

    # Cliff detection: current hit rate significantly lower than ex-1
    cliff_drop = hr_minus - hr_cur
    is_cliff = cliff_drop > 0.04  # >4% drop stepping from ex-1 to ex

    status = ""
    if is_cliff:
        # Check if stepping back 1c improves $/day
        if dpd_minus > dpd:
            status = "CLIFF! step back +%dc->+%dc ($%.2f->$%.2f)" % (ex, ex-1, dpd, dpd_minus)
            cliff_cells.append((cell_name, ex, ex-1, dpd, dpd_minus, cliff_drop))
        else:
            status = "cliff edge but $/day ok"
    elif hr_cur < hr_plus:
        status = "inverted (ex+1 has higher HR)"

    print("%-35s %4d +%3dc %4.0f%% %5.0f%% %4.0f%% $%+5.2f %s" % (
        cell_name[:35], n, ex,
        100*hr_minus, 100*hr_cur, 100*hr_plus, dpd, status))

print("\n=== CLIFF CELLS REQUIRING ADJUSTMENT ===")
if cliff_cells:
    for cell, old, new, old_dpd, new_dpd, drop in cliff_cells:
        print("  %-35s +%dc -> +%dc  HR drops %.0f%% at current  $%.2f -> $%.2f" % (
            cell, old, new, 100*drop, old_dpd, new_dpd))
        config["active_cells"][cell]["exit_cents"] = new

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print("\nApplied %d cliff adjustments. Saved." % len(cliff_cells))
else:
    print("  None found. All cells are off cliff edges.")

# Final aggregate
print("\n=== FINAL V4 AGGREGATE ===")
total_dpd = 0
total_n = 0
total_cap = 0
for cell_name, cfg in config["active_cells"].items():
    matches = facts_by_cell.get(cell_name, [])
    if not matches:
        continue
    n = len(matches)
    ex = cfg["exit_cents"]
    dpd = dpd_at(matches, ex)
    avg_entry = sum(m["entry_mid"] for m in matches) / n
    total_dpd += dpd
    total_n += n
    total_cap += avg_entry * CT / 100.0 * n / DAYS

active_count = len(config["active_cells"])
disabled_count = len(config["disabled_cells"])
daily_roi = 100 * total_dpd / total_cap if total_cap else 0

print("Active cells:   %d" % active_count)
print("Disabled cells: %d" % disabled_count)
print("Projected $/day: $%.2f" % total_dpd)
print("Daily capital:   $%.2f" % total_cap)
print("Daily ROI:       %.1f%%" % daily_roi)
print("Matches in dataset: %d" % total_n)

print("\nDisabled cells:")
for d in config["disabled_cells"]:
    print("  %s" % d)

print("\nDONE")
