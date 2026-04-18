#!/usr/bin/env python3
"""Honest exit analysis: tight vs mid vs hold-to-settlement."""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
DAYS = 28
CT = 10

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

# All cells with avg entry 35-65c
coinflip_cells = []
for cell in sorted(config["active_cells"].keys()):
    matches = facts_by_cell.get(cell, [])
    if not matches:
        continue
    avg = sum(m["entry_mid"] for m in matches) / len(matches)
    if 35 <= avg <= 65:
        coinflip_cells.append(cell)

# Also check disabled cells in this range
for cell in config.get("disabled_cells", []):
    matches = facts_by_cell.get(cell, [])
    if not matches:
        continue
    avg = sum(m["entry_mid"] for m in matches) / len(matches)
    if 35 <= avg <= 65:
        coinflip_cells.append(cell)

coinflip_cells = sorted(set(coinflip_cells))

# ============================================================
# FLAG: Invalid exit configs (entry + exit > 99)
# ============================================================
print("=" * 100)
print("INVALID EXIT CONFIGS (entry + exit_cents > 99)")
print("=" * 100)

invalid = []
for cell in sorted(config["active_cells"].keys()):
    cfg = config["active_cells"][cell]
    matches = facts_by_cell.get(cell, [])
    if not matches:
        continue
    avg = sum(m["entry_mid"] for m in matches) / len(matches)
    exit_price = avg + cfg["exit_cents"]
    if exit_price > 99:
        invalid.append((cell, avg, cfg["exit_cents"], exit_price))
        print("  %-35s avg=%.0fc + %dc = %.0fc > 99  *** EFFECTIVELY HOLD-TO-SETTLE ***" % (
            cell, avg, cfg["exit_cents"], exit_price))

if not invalid:
    print("  None found")

# ============================================================
# Per-cell analysis
# ============================================================
print("\n" + "=" * 100)
print("THREE-STRATEGY COMPARISON FOR COIN-FLIP CELLS (35-65c entry)")
print("=" * 100)

def sim_strategy(matches, exit_cents):
    """Returns (pnls_list, hit_count)."""
    pnls = []
    hits = 0
    for m in matches:
        entry = m["entry_mid"]
        exit_price = entry + exit_cents
        if exit_price > 99:
            # Can't post this exit — effectively hold to settlement
            settle = 99.5 if m["result"] == "win" else 0.5
            pnls.append((settle - entry) * CT / 100.0)
        elif m["max_bounce"] >= exit_cents:
            pnls.append(exit_cents * CT / 100.0)
            hits += 1
        else:
            settle = 99.5 if m["result"] == "win" else 0.5
            pnls.append((settle - entry) * CT / 100.0)
    return pnls, hits

def hold_to_settle(matches):
    pnls = []
    for m in matches:
        settle = 99.5 if m["result"] == "win" else 0.5
        pnls.append((settle - m["entry_mid"]) * CT / 100.0)
    return pnls

def stats(pnls, n_total, label=""):
    n = len(pnls)
    ev = sum(pnls) / n if n else 0
    var = sum((p - ev)**2 for p in pnls) / n if n else 0
    std = math.sqrt(var)
    tpd = n / DAYS
    dpd = ev * tpd
    # Worst 3 consecutive
    worst3 = 0
    for i in range(len(pnls) - 2):
        s = sum(pnls[i:i+3])
        if s < worst3:
            worst3 = s
    return ev, std, dpd, worst3

TIGHT = [5, 8, 10, 12, 15, 20]
MID = [25, 30, 35, 40, 45]

summary_rows = []

for cell in coinflip_cells:
    matches = facts_by_cell.get(cell, [])
    if len(matches) < 5:
        continue
    n = len(matches)
    avg_entry = sum(m["entry_mid"] for m in matches) / n
    win_rate = sum(1 for m in matches if m["result"] == "win") / n
    v4_cfg = config["active_cells"].get(cell, {})
    v4_exit = v4_cfg.get("exit_cents", 0)
    is_disabled = cell in config.get("disabled_cells", [])

    print("\n--- %s (N=%d, avg=%.0fc, WR=%.0f%%, V4=+%dc%s) ---" % (
        cell, n, avg_entry, 100*win_rate, v4_exit, " DISABLED" if is_disabled else ""))

    # Strategy C: hold to settlement
    c_pnls = hold_to_settle(matches)
    c_ev, c_std, c_dpd, c_worst3 = stats(c_pnls, n)

    print("%-8s %5s %5s %7s %6s %7s %8s" % (
        "STRAT", "EXIT", "HIT%", "EV/tr", "STD", "$/DAY", "WORST3"))
    print("-" * 55)

    best_a = (0, 0, -999, 0, 0, 0)
    best_b = (0, 0, -999, 0, 0, 0)

    for ex in TIGHT:
        ep = avg_entry + ex
        if ep > 99:
            label = "A+%d*" % ex
        else:
            label = "A+%d" % ex
        pnls, hits = sim_strategy(matches, ex)
        hit_rate = hits / n
        ev, std, dpd, w3 = stats(pnls, n)
        note = " <<<V4" if ex == v4_exit else ""
        print("%-8s +%3dc %4.0f%% $%+5.3f $%.3f $%+5.2f $%+5.2f%s" % (
            label, ex, 100*hit_rate, ev, std, dpd, w3, note))
        if ev > best_a[2]:
            best_a = (ex, hit_rate, ev, std, dpd, w3)

    for ex in MID:
        ep = avg_entry + ex
        if ep > 99:
            label = "B+%d*" % ex  # * = capped at 99, effectively hold
        else:
            label = "B+%d" % ex
        pnls, hits = sim_strategy(matches, ex)
        hit_rate = hits / n
        ev, std, dpd, w3 = stats(pnls, n)
        note = " <<<V4" if ex == v4_exit else ""
        print("%-8s +%3dc %4.0f%% $%+5.3f $%.3f $%+5.2f $%+5.2f%s" % (
            label, ex, 100*hit_rate, ev, std, dpd, w3, note))
        if ev > best_b[2]:
            best_b = (ex, hit_rate, ev, std, dpd, w3)

    # Strategy C
    note = " <<<V4" if v4_exit > 50 or (avg_entry + v4_exit > 99) else ""
    print("%-8s %5s %5s $%+5.3f $%.3f $%+5.2f $%+5.2f%s" % (
        "C:HOLD", "n/a", "n/a", c_ev, c_std, c_dpd, c_worst3, note))

    # Winner
    candidates = [
        ("A:+%dc" % best_a[0], best_a[0], best_a[1], best_a[2], best_a[3], best_a[4], best_a[5]),
        ("B:+%dc" % best_b[0], best_b[0], best_b[1], best_b[2], best_b[3], best_b[4], best_b[5]),
        ("C:HOLD", 0, 0, c_ev, c_std, c_dpd, c_worst3),
    ]
    candidates.sort(key=lambda x: -x[3])
    winner = candidates[0]
    runner = candidates[1]

    cell_type = ""
    if winner[0].startswith("C"):
        cell_type = "LOTTERY"
    elif winner[0].startswith("A"):
        cell_type = "SCALP"
    else:
        cell_type = "MID-EXIT"

    print()
    print("  WINNER: %s (EV=$%.3f, std=$%.3f)" % (winner[0], winner[3], winner[4]))
    print("  Runner: %s (EV=$%.3f)" % (runner[0], runner[3]))
    print("  Type: %s" % cell_type)

    # Check V4 honesty
    if v4_exit > 0 and avg_entry + v4_exit > 99:
        print("  *** V4 exit +%dc is HOLD-TO-SETTLE (entry %.0f + %d = %.0f > 99)" % (
            v4_exit, avg_entry, v4_exit, avg_entry + v4_exit))

    summary_rows.append({
        "cell": cell, "n": n, "avg_entry": avg_entry, "wr": win_rate,
        "v4_exit": v4_exit, "disabled": is_disabled,
        "best_a": best_a, "best_b": best_b, "c_ev": c_ev,
        "winner": winner[0], "winner_ev": winner[3], "winner_dpd": winner[4],
        "cell_type": cell_type,
    })

# ============================================================
# Summary comparison table
# ============================================================
print("\n" + "=" * 120)
print("COMPARISON TABLE — ALL COIN-FLIP CELLS")
print("=" * 120)
print("%-32s %4s %3s %-10s %7s %-10s %7s %-10s %7s %4s %-10s %s" % (
    "CELL", "N", "WR", "BEST_A", "EV_A", "BEST_B", "EV_B", "HOLD_C", "EV_C", "V4", "WINNER", "TYPE"))
print("-" * 120)

for r in summary_rows:
    a = r["best_a"]
    b = r["best_b"]
    print("%-32s %4d %2.0f%% A:+%dc(%d%%) $%+.3f B:+%dc(%d%%) $%+.3f C:HOLD    $%+.3f +%dc %-10s %s" % (
        r["cell"][:32], r["n"], 100*r["wr"],
        a[0], 100*a[1], a[2],
        b[0], 100*b[1], b[2],
        r["c_ev"],
        r["v4_exit"], r["winner"], r["cell_type"]))

# Aggregate by strategy type
print("\n" + "=" * 80)
print("AGGREGATE BY CELL TYPE")
print("=" * 80)

types = defaultdict(lambda: {"cells": 0, "dpd": 0})
for r in summary_rows:
    t = types[r["cell_type"]]
    t["cells"] += 1
    t["dpd"] += r["winner_dpd"]

for ct in ["SCALP", "MID-EXIT", "LOTTERY"]:
    t = types.get(ct, {"cells": 0, "dpd": 0})
    if t["cells"]:
        print("  %-12s %2d cells  $%+.2f/day" % (ct, t["cells"], t["dpd"]))

total = sum(t["dpd"] for t in types.values())
print("  %-12s %2d cells  $%+.2f/day" % ("TOTAL", sum(t["cells"] for t in types.values()), total))

# Proposed changes
print("\n" + "=" * 80)
print("PROPOSED V4 CHANGES FOR COIN-FLIP CELLS")
print("=" * 80)

changes = []
for r in summary_rows:
    if r["disabled"]:
        continue
    old = r["v4_exit"]
    winner = r["winner"]
    new_exit = 0
    if winner.startswith("A:"):
        new_exit = r["best_a"][0]
    elif winner.startswith("B:"):
        new_exit = r["best_b"][0]
    else:
        new_exit = 99 - int(r["avg_entry"])  # max possible exit

    # Check if V4's current is effectively hold-to-settle
    old_is_hold = r["avg_entry"] + old > 98
    new_is_hold = winner.startswith("C:")

    if old != new_exit and not (old_is_hold and new_is_hold):
        old_ev = 0
        pnls, _ = sim_strategy(facts_by_cell[r["cell"]], old)
        old_ev = sum(pnls) / len(pnls) if pnls else 0
        changes.append((r["cell"], old, new_exit, old_ev, r["winner_ev"], r["cell_type"]))
        print("  %-32s +%dc -> +%dc  EV $%.3f -> $%.3f  (%s)" % (
            r["cell"], old, new_exit, old_ev, r["winner_ev"], r["cell_type"]))

if not changes:
    print("  No changes needed — V4 exits already align with winners")

print("\nDONE")
