#!/usr/bin/env python3
"""Full V4 cell performance table with WR vs Hit Rate insight."""
import csv, json, os
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

rows = []
for cell_name, cfg in config["active_cells"].items():
    matches = facts_by_cell.get(cell_name, [])
    n = len(matches)
    if n == 0:
        continue
    ex = cfg["exit_cents"]
    dca = cfg.get("dca_trigger_cents", 0)
    strategy_label = cfg.get("strategy", "noDCA")
    avg_entry = sum(m["entry_mid"] for m in matches) / n

    # Win rate (side won at settlement)
    wins = sum(1 for m in matches if m["result"] == "win")
    wr = wins / n

    # Hit rate (exit fired)
    exit_price = avg_entry + ex
    hits = sum(1 for m in matches if m["max_bounce"] >= ex)
    hit_rate = hits / n

    # EV
    total_pnl = 0
    for m in matches:
        if m["max_bounce"] >= ex:
            total_pnl += ex
        else:
            settle = 99.5 if m["result"] == "win" else 0.5
            total_pnl += (settle - m["entry_mid"])
    ev_cents = total_pnl / n
    ev_dollars = ev_cents * CT / 100.0
    entry_cost = avg_entry * CT / 100.0
    roi = 100 * ev_dollars / entry_cost if entry_cost > 0 else 0
    tpd = n / DAYS
    dpd = ev_dollars * tpd
    daily_capital = entry_cost * tpd
    daily_roi = 100 * dpd / daily_capital if daily_capital > 0 else 0

    # Strategy type
    if exit_price >= 95:
        stype = "HOLD"
    elif hit_rate >= 0.80:
        stype = "SCALP"
    elif ex >= 40:
        stype = "WIDE"
    elif ex >= 20:
        stype = "MID"
    else:
        stype = "SCALP"

    # Flags
    flags = []
    if wr < 0.40:
        flags.append("WR<40%")
    if abs(hit_rate - wr) < 0.05 and hit_rate < 0.80:
        flags.append("HR~WR(hold)")
    if wr < 0.40 and hit_rate < 0.50:
        flags.append("DANGER")

    dca_str = "-%dc" % dca if dca > 0 else "noDCA"

    rows.append({
        "cell": cell_name, "n": n, "wr": wr, "exit": ex, "dca_str": dca_str,
        "hit_rate": hit_rate, "ev_cents": ev_cents, "ev_dollars": ev_dollars,
        "roi": roi, "dpd": dpd, "daily_roi": daily_roi, "stype": stype,
        "flags": flags, "avg_entry": avg_entry, "tpd": tpd,
    })

rows.sort(key=lambda x: -x["dpd"])

# Aggregates
tot_n = sum(r["n"] for r in rows)
tot_tpd = sum(r["tpd"] for r in rows)
tot_dpd = sum(r["dpd"] for r in rows)
tot_cap = sum(r["avg_entry"] * CT / 100.0 * r["tpd"] for r in rows)
avg_ev = sum(r["ev_cents"] * r["n"] for r in rows) / tot_n if tot_n else 0
tot_roi = 100 * tot_dpd / tot_cap if tot_cap else 0

print("=" * 145)
print("V4 FULL CELL PERFORMANCE TABLE — 32 Active Cells")
print("=" * 145)
print("AGGREGATE: %d cells | %d matches | %.1f trades/day | $%.2f/day | avg EV=%.1fc | ROI=%.1f%%" % (
    len(rows), tot_n, tot_tpd, tot_dpd, avg_ev, tot_roi))
print("=" * 145)

print("%-32s %3s %4s %4s %6s %5s %6s %6s %6s %6s %6s %6s %s" % (
    "CELL", "N", "WR%", "EXIT", "DCA", "HIT%", "EV_c", "EV_$", "ROI%", "TR/D", "$/DAY", "TYPE", "FLAGS"))
print("-" * 145)

for r in rows:
    flag_str = " ".join(r["flags"]) if r["flags"] else ""
    print("%-32s %3d %3.0f%% +%3dc %6s %4.0f%% %+5.1fc $%+5.3f %+5.1f%% %4.2f $%+5.2f %-6s %s" % (
        r["cell"][:32], r["n"], 100*r["wr"], r["exit"], r["dca_str"],
        100*r["hit_rate"], r["ev_cents"], r["ev_dollars"],
        r["roi"], r["tpd"], r["dpd"], r["stype"], flag_str))

print("-" * 145)
print("%-32s %3d %4s %4s %6s %5s %+5.1fc %6s %6s %4.1f $%+5.2f" % (
    "TOTAL/AVG", tot_n, "", "", "", "", avg_ev, "", "", tot_tpd, tot_dpd))

# WR vs Hit Rate insight table
print("\n" + "=" * 100)
print("WR% vs HIT RATE INSIGHT")
print("=" * 100)
print("%-32s %4s %5s %5s %4s %s" % ("CELL", "WR%", "HIT%", "DIFF", "TYPE", "INTERPRETATION"))
print("-" * 100)

for r in sorted(rows, key=lambda x: x["hit_rate"] - x["wr"], reverse=True):
    diff = r["hit_rate"] - r["wr"]
    if diff > 0.30:
        interp = "EXIT captures bounces well beyond WR"
    elif diff > 0.10:
        interp = "EXIT adds moderate value over hold"
    elif diff > -0.05:
        interp = "EXIT ~ WR (near hold-to-settle)"
    elif diff > -0.20:
        interp = "EXIT fires less than WR (tighter than needed?)"
    else:
        interp = "EXIT much tighter than WR — pure scalp"
    print("%-32s %3.0f%% %4.0f%% %+4.0f%% %-6s %s" % (
        r["cell"][:32], 100*r["wr"], 100*r["hit_rate"], 100*diff, r["stype"], interp))

# Strategy type breakdown
print("\n" + "=" * 80)
print("STRATEGY TYPE BREAKDOWN")
print("=" * 80)

type_stats = defaultdict(lambda: {"cells": 0, "dpd": 0, "wr_sum": 0, "n": 0})
for r in rows:
    t = type_stats[r["stype"]]
    t["cells"] += 1
    t["dpd"] += r["dpd"]
    t["wr_sum"] += r["wr"] * r["n"]
    t["n"] += r["n"]

print("%-8s %5s %8s %8s %6s" % ("TYPE", "CELLS", "$/DAY", "AVG_WR", "SHARE"))
for stype in ["SCALP", "MID", "WIDE", "HOLD"]:
    t = type_stats.get(stype)
    if not t or t["cells"] == 0:
        continue
    avg_wr = t["wr_sum"] / t["n"] if t["n"] else 0
    share = 100 * t["dpd"] / tot_dpd if tot_dpd else 0
    print("%-8s %5d $%+6.2f %6.0f%% %5.0f%%" % (stype, t["cells"], t["dpd"], 100*avg_wr, share))

print("\nDONE")
