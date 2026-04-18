#!/usr/bin/env python3
"""Re-optimize exits for coin-flip range cells (35-65c entry)."""
import csv, json, os
from pathlib import Path
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
DAYS = 28
CONTRACTS = 10

config = json.load(open(CONFIG_PATH))

facts_by_cell = defaultdict(list)
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        cat = r["category"]; side = r["side"]; entry = float(r["entry_mid"])
        bucket = int(entry / 5) * 5
        cell = "%s_%s_%d-%d" % (cat, side, bucket, bucket + 4)
        facts_by_cell[cell].append({
            "max_bounce": float(r["max_bounce_from_entry"]),
            "result": r["match_result"],
            "entry_mid": entry,
        })

# Cells in 35-65c range
target_cells = [
    "ATP_MAIN_underdog_40-44",
    "ATP_MAIN_underdog_35-39",
    "ATP_CHALL_underdog_40-44",
    "WTA_MAIN_underdog_35-39",
    "WTA_MAIN_underdog_40-44",
    "WTA_MAIN_leader_50-54",
    "WTA_MAIN_leader_60-64",
    "WTA_MAIN_leader_55-59",
    # Also check other 35-65c cells
    "ATP_CHALL_underdog_35-39",
    "ATP_MAIN_leader_60-64",
    "ATP_CHALL_leader_60-64",
    "ATP_CHALL_leader_65-69",
    "WTA_MAIN_underdog_45-49",
    "WTA_MAIN_leader_65-69",
]

# Deduplicate and filter to cells that exist
target_cells = sorted(set(c for c in target_cells if c in facts_by_cell and len(facts_by_cell[c]) >= 5))

print("=" * 100)
print("COIN-FLIP RANGE EXIT RE-OPTIMIZATION (35-65c entry cells)")
print("=" * 100)

changes = []

for cell in target_cells:
    matches = facts_by_cell[cell]
    n = len(matches)
    avg_entry = sum(m["entry_mid"] for m in matches) / n
    current_cfg = config["active_cells"].get(cell, {})
    current_exit = current_cfg.get("exit_cents", 0)
    is_disabled = cell in config.get("disabled_cells", [])

    print("\n--- %s (N=%d, avg_entry=%.0fc, current=+%dc%s) ---" % (
        cell, n, avg_entry, current_exit, " DISABLED" if is_disabled else ""))
    print("%-5s %5s %7s %7s %7s" % ("EXIT", "HITS", "HIT%", "EV/tr", "$/DAY"))

    best_ev = -999
    best_exit = 0
    best_hit = 0
    best_dpd = 0
    all_exits = []

    for ex in range(5, 31):
        hits = sum(1 for m in matches if m["max_bounce"] >= ex)
        hit_rate = hits / n
        total_pnl = 0
        for m in matches:
            if m["max_bounce"] >= ex:
                total_pnl += ex
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                total_pnl += (settle - m["entry_mid"])
        ev = total_pnl / n
        tpd = n / DAYS
        dpd = ev * CONTRACTS / 100.0 * tpd

        marker = ""
        if ex == current_exit:
            marker = " <<<< CURRENT"
        if ev > best_ev:
            best_ev = ev
            best_exit = ex
            best_hit = hit_rate
            best_dpd = dpd

        all_exits.append((ex, hits, hit_rate, ev, dpd))
        print("+%3dc %4d %5.0f%% %+6.1fc $%+5.2f%s" % (ex, hits, 100*hit_rate, ev, dpd, marker))

    # Also show wide exits for comparison
    for ex in [35, 40, 45, 50, 55, 58, 60]:
        if ex <= 30:
            continue
        hits = sum(1 for m in matches if m["max_bounce"] >= ex)
        hit_rate = hits / n
        total_pnl = 0
        for m in matches:
            if m["max_bounce"] >= ex:
                total_pnl += ex
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                total_pnl += (settle - m["entry_mid"])
        ev = total_pnl / n
        dpd = ev * CONTRACTS / 100.0 * n / DAYS
        marker = " <<<< CURRENT" if ex == current_exit else ""
        print("+%3dc %4d %5.0f%% %+6.1fc $%+5.2f%s" % (ex, hits, 100*hit_rate, ev, dpd, marker))

    # Decision
    print()
    if current_exit > 30 and best_exit <= 30:
        # Tight exit beats wide
        # But also check: does current wide exit have higher EV?
        current_ev = 0
        for m in matches:
            if m["max_bounce"] >= current_exit:
                current_ev += current_exit
            else:
                settle = 99.5 if m["result"] == "win" else 0.5
                current_ev += (settle - m["entry_mid"])
        current_ev /= n

        if best_ev > current_ev:
            print("  >>> SWITCH: +%dc (EV=%.1fc, hit=%d%%) beats +%dc (EV=%.1fc)" % (
                best_exit, best_ev, 100*best_hit, current_exit, current_ev))
            changes.append((cell, current_exit, best_exit, current_ev, best_ev, best_hit))
        else:
            print("  KEEP +%dc: EV=%.1fc > tight best +%dc EV=%.1fc" % (
                current_exit, current_ev, best_exit, best_ev))
    elif current_exit <= 30:
        if best_exit != current_exit:
            current_ev_check = 0
            for m in matches:
                if m["max_bounce"] >= current_exit:
                    current_ev_check += current_exit
                else:
                    settle = 99.5 if m["result"] == "win" else 0.5
                    current_ev_check += (settle - m["entry_mid"])
            current_ev_check /= n
            if best_ev > current_ev_check + 0.5:
                print("  >>> ADJUST: +%dc -> +%dc (EV %.1fc -> %.1fc)" % (
                    current_exit, best_exit, current_ev_check, best_ev))
                changes.append((cell, current_exit, best_exit, current_ev_check, best_ev, best_hit))
            else:
                print("  KEEP +%dc (close to optimal)" % current_exit)
        else:
            print("  KEEP +%dc (already optimal)" % current_exit)
    elif is_disabled:
        if best_ev > 0:
            print("  >>> ACTIVATE at +%dc (EV=%.1fc, hit=%d%%)" % (best_exit, best_ev, 100*best_hit))
            changes.append((cell, 0, best_exit, 0, best_ev, best_hit))
        else:
            print("  STAY DISABLED (best EV=%.1fc)" % best_ev)

# Summary
print("\n" + "=" * 100)
print("PROPOSED CHANGES")
print("=" * 100)
print("%-35s %6s %6s %8s %8s %6s" % ("CELL", "OLD", "NEW", "OLD_EV", "NEW_EV", "HIT%"))
for cell, old, new, old_ev, new_ev, hit in changes:
    print("%-35s +%3dc +%3dc %+7.1fc %+7.1fc %5.0f%%" % (cell, old, new, old_ev, new_ev, 100*hit))

# Apply changes
for cell, old, new, old_ev, new_ev, hit in changes:
    if cell in config["active_cells"]:
        config["active_cells"][cell]["exit_cents"] = new
    elif cell in config.get("disabled_cells", []):
        # Activate
        config["disabled_cells"].remove(cell)
        config["active_cells"][cell] = {"strategy": "noDCA", "exit_cents": new}

with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=2)
print("\nSaved: %s" % CONFIG_PATH)

# Before/after summary
print("\n" + "=" * 80)
print("BEFORE vs AFTER (35-65c range cells only)")
print("=" * 80)
for cell, old, new, old_ev, new_ev, hit in changes:
    old_dpd = old_ev * CONTRACTS / 100.0 * len(facts_by_cell[cell]) / DAYS
    new_dpd = new_ev * CONTRACTS / 100.0 * len(facts_by_cell[cell]) / DAYS
    print("  %-35s +%dc->+%dc  $%.2f->$%.2f/day  hit %d%%" % (
        cell, old, new, old_dpd, new_dpd, 100*hit))

print("\nDONE")
