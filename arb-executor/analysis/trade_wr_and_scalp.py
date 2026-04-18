#!/usr/bin/env python3
"""Task 1: Trade-level win rate. Task 2: Scalp reclassification test."""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict

FACTS_PATH = "/root/Omi-Workspace/arb-executor/analysis/match_facts.csv"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
DAYS = 28; CT = 10

config = json.load(open(CONFIG_PATH))

facts_by_cell = defaultdict(list)
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        entry = float(r["entry_mid"])
        bucket = int(entry / 5) * 5
        cell = "%s_%s_%d-%d" % (r["category"], r["side"], bucket, bucket + 4)
        facts_by_cell[cell].append({
            "max_bounce": float(r["max_bounce_from_entry"]),
            "max_dip": float(r["max_dip_from_entry"]),
            "result": r["match_result"], "entry_mid": entry,
        })

def sim_cell(matches, ex):
    wins = 0; losses = 0; win_pnls = []; loss_pnls = []
    for m in matches:
        entry = m["entry_mid"]
        if m["max_bounce"] >= ex and entry + ex <= 99:
            pnl = ex * CT / 100.0
            wins += 1; win_pnls.append(pnl)
        else:
            settle = 99.5 if m["result"] == "win" else 0.5
            pnl = (settle - entry) * CT / 100.0
            if pnl > 0:
                wins += 1; win_pnls.append(pnl)
            else:
                losses += 1; loss_pnls.append(pnl)
    n = wins + losses
    trade_wr = wins / n if n else 0
    avg_win = sum(win_pnls) / len(win_pnls) if win_pnls else 0
    avg_loss = sum(loss_pnls) / len(loss_pnls) if loss_pnls else 0
    ev = (sum(win_pnls) + sum(loss_pnls)) / n if n else 0
    rr = abs(avg_win / avg_loss) if avg_loss != 0 else 999
    tpd = n / DAYS
    dpd = ev * tpd
    return {"n": n, "trade_wr": trade_wr, "avg_win": avg_win, "avg_loss": avg_loss,
            "ev": ev, "rr": rr, "dpd": dpd, "tpd": tpd}

# ============================================================
# TASK 1: Trade-level win rate
# ============================================================
print("=" * 130)
print("TASK 1: TRADE-LEVEL WIN RATE (all 32 active cells)")
print("=" * 130)

rows = []
for cell_name, cfg in config["active_cells"].items():
    matches = facts_by_cell.get(cell_name, [])
    if not matches:
        continue
    ex = cfg["exit_cents"]
    avg_entry = sum(m["entry_mid"] for m in matches) / len(matches)
    r = sim_cell(matches, ex)
    r["cell"] = cell_name
    r["exit"] = ex
    r["avg_entry"] = avg_entry
    rows.append(r)

rows.sort(key=lambda x: -x["dpd"])

print("%-32s %3s %5s %5s %7s %7s %6s %4s %6s %s" % (
    "CELL", "N", "T_WR%", "EXIT", "W_AVG", "L_AVG", "EV", "R/R", "$/DAY", "FLAGS"))
print("-" * 130)

for r in rows:
    flags = []
    if r["trade_wr"] < 0.70:
        flags.append("WR<70%")
    flag_str = " ".join(flags)
    print("%-32s %3d %4.0f%% +%3dc $%+5.2f $%+5.2f $%+4.2f %3.1f $%+5.2f %s" % (
        r["cell"][:32], r["n"], 100*r["trade_wr"], r["exit"],
        r["avg_win"], r["avg_loss"], r["ev"], r["rr"], r["dpd"], flag_str))

tot_dpd = sum(r["dpd"] for r in rows)
print("-" * 130)
print("TOTAL: $%.2f/day" % tot_dpd)

# ============================================================
# TASK 2: Scalp reclassification
# ============================================================
print("\n" + "=" * 130)
print("TASK 2: SCALP RECLASSIFICATION TEST (MID/WIDE/HOLD cells)")
print("=" * 130)

test_cells = [
    ("WTA_MAIN_leader_70-74", "HOLD"),
    ("ATP_MAIN_leader_60-64", "HOLD"),
    ("WTA_MAIN_leader_80-84", "HOLD"),
    ("ATP_CHALL_underdog_40-44", "WIDE"),
    ("ATP_MAIN_underdog_35-39", "MID"),
    ("WTA_MAIN_underdog_35-39", "MID"),
    ("WTA_MAIN_underdog_40-44", "WIDE"),
    ("ATP_CHALL_leader_75-79", "HOLD"),
    ("ATP_CHALL_leader_80-84", "HOLD"),
    ("ATP_MAIN_leader_75-79", "HOLD"),
    ("WTA_MAIN_leader_60-64", "HOLD"),
    ("WTA_MAIN_leader_85-89", "HOLD"),
    ("ATP_CHALL_leader_65-69", "MID"),
    ("WTA_MAIN_leader_50-54", "SCALP"),
]

changes = []

for cell_name, current_type in test_cells:
    cfg = config["active_cells"].get(cell_name)
    if not cfg:
        continue
    matches = facts_by_cell.get(cell_name, [])
    if not matches:
        continue
    n = len(matches)
    avg_entry = sum(m["entry_mid"] for m in matches) / n
    current_exit = cfg["exit_cents"]
    current = sim_cell(matches, current_exit)

    print("\n--- %s (N=%d, avg=%.0fc, current=+%dc %s) ---" % (
        cell_name, n, avg_entry, current_exit, current_type))
    print("%-6s %5s %5s %7s %7s %6s %4s %7s" % (
        "EXIT", "T_WR%", "HIT%", "W_AVG", "L_AVG", "EV", "R/R", "$/DAY"))

    best_scalp_ex = 0
    best_scalp_dpd = -999

    for ex in range(5, min(current_exit + 1, 31)):
        r = sim_cell(matches, ex)
        hits = sum(1 for m in matches if m["max_bounce"] >= ex)
        hit_rate = hits / n
        marker = " <<<CURRENT" if ex == current_exit else ""
        print("+%3dc %4.0f%% %4.0f%% $%+5.2f $%+5.2f $%+4.2f %3.1f $%+5.2f%s" % (
            ex, 100*r["trade_wr"], 100*hit_rate,
            r["avg_win"], r["avg_loss"], r["ev"], r["rr"], r["dpd"], marker))
        if ex <= 20 and r["dpd"] > best_scalp_dpd:
            best_scalp_dpd = r["dpd"]
            best_scalp_ex = ex

    # Also show current wide
    if current_exit > 20:
        r_cur = sim_cell(matches, current_exit)
        hits_cur = sum(1 for m in matches if m["max_bounce"] >= current_exit)
        print("+%3dc %4.0f%% %4.0f%% $%+5.2f $%+5.2f $%+4.2f %3.1f $%+5.2f <<<CURRENT" % (
            current_exit, 100*r_cur["trade_wr"], 100*hits_cur/n,
            r_cur["avg_win"], r_cur["avg_loss"], r_cur["ev"], r_cur["rr"], r_cur["dpd"]))

    # Decision
    print()
    cur_dpd = current["dpd"]
    if best_scalp_dpd > cur_dpd and best_scalp_ex > 0:
        print("  >>> SWITCH to +%dc scalp: $%.2f/day vs $%.2f/day (current)" % (
            best_scalp_ex, best_scalp_dpd, cur_dpd))
        changes.append((cell_name, current_exit, best_scalp_ex, cur_dpd, best_scalp_dpd))
    else:
        print("  KEEP +%dc: $%.2f/day >= best scalp +%dc $%.2f/day" % (
            current_exit, cur_dpd, best_scalp_ex, best_scalp_dpd))

# ============================================================
# STEP 3: Apply findings
# ============================================================
print("\n" + "=" * 100)
print("STEP 3: PROPOSED CHANGES")
print("=" * 100)

if changes:
    for cell, old, new, old_dpd, new_dpd in changes:
        print("  %-32s +%dc -> +%dc  $%.2f -> $%.2f/day" % (cell, old, new, old_dpd, new_dpd))
        config["active_cells"][cell]["exit_cents"] = new

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print("\nSaved %d changes to %s" % (len(changes), CONFIG_PATH))
else:
    print("  No changes — all non-scalp cells correctly classified")

# Final aggregate
print("\n" + "=" * 80)
print("FINAL V4 AGGREGATE")
print("=" * 80)

scalp_dpd = 0; scalp_n = 0
nonscalp_dpd = 0; nonscalp_n = 0
tot = 0

for cell_name, cfg in config["active_cells"].items():
    matches = facts_by_cell.get(cell_name, [])
    if not matches:
        continue
    ex = cfg["exit_cents"]
    r = sim_cell(matches, ex)
    avg_entry = sum(m["entry_mid"] for m in matches) / len(matches)
    hits = sum(1 for m in matches if m["max_bounce"] >= ex)
    hit_rate = hits / len(matches)
    if hit_rate >= 0.80 or ex <= 15:
        scalp_dpd += r["dpd"]; scalp_n += 1
    else:
        nonscalp_dpd += r["dpd"]; nonscalp_n += 1
    tot += r["dpd"]

print("Total $/day:       $%.2f" % tot)
print("Scalp cells:       %d ($%.2f/day)" % (scalp_n, scalp_dpd))
print("Non-scalp cells:   %d ($%.2f/day)" % (nonscalp_n, nonscalp_dpd))
cap = sum(sum(m["entry_mid"] for m in facts_by_cell.get(c, [])) / max(len(facts_by_cell.get(c, [])),1)
          * CT / 100.0 * len(facts_by_cell.get(c, [])) / DAYS
          for c in config["active_cells"])
print("Daily capital:     $%.2f" % cap)
print("Daily ROI:         %.1f%%" % (100 * tot / cap if cap else 0))

print("\nDONE")
