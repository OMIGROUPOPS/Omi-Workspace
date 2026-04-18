#!/usr/bin/env python3
"""V4 final heatmap with DCA visibility."""
import csv, json, os, math
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

ANALYSIS = "/root/Omi-Workspace/arb-executor/analysis"
CONFIG_PATH = "/root/Omi-Workspace/arb-executor/config/deploy_v4.json"
FACTS_PATH = os.path.join(ANALYSIS, "match_facts.csv")
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
            "result": r["match_result"], "entry_mid": entry,
        })

BUCKETS = list(range(5, 95, 5))
SIDES = ["underdog", "leader"]
TOURS = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]

def metrics(cell_name):
    matches = facts_by_cell.get(cell_name, [])
    n = len(matches)
    cfg = config["active_cells"].get(cell_name)
    disabled = cell_name in config.get("disabled_cells", [])
    if not cfg or n == 0:
        return {"n": n, "active": False, "disabled": disabled}
    ex = cfg["exit_cents"]
    dca = cfg.get("dca_trigger_cents", 0)
    strategy = cfg.get("strategy", "noDCA")
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
    dpd = ev * CT / 100.0 * n / DAYS
    dca_str = "-%dc" % dca if dca > 0 else "none"
    return {"n": n, "active": True, "disabled": False, "exit": ex, "dca": dca,
            "dca_str": dca_str, "strategy": strategy, "hit_rate": hit_rate, "dpd": dpd}

# ASCII heatmaps
for tour in TOURS:
    print("\n" + "=" * 76)
    print("  %s" % tour)
    print("=" * 76)
    print("%-8s | %-32s | %-32s" % ("BUCKET", "UNDERDOG", "LEADER"))
    print("-" * 76)
    for b in BUCKETS:
        row = "%d-%dc  |" % (b, b+4)
        for side in SIDES:
            cell = "%s_%s_%d-%d" % (tour, side, b, b+4)
            m = metrics(cell)
            if m["active"]:
                flag = "*" if m["n"] < 10 else ""
                dca_part = "/ %s" % m["dca_str"]
                txt = "+%d %s %d%% $%.2f N=%d%s" % (
                    m["exit"], dca_part, 100*m["hit_rate"], m["dpd"], m["n"], flag)
            elif m["disabled"]:
                txt = "DISABLED (N=%d)" % m["n"]
            elif m["n"] > 0:
                txt = "- (N=%d)" % m["n"]
            else:
                txt = "-"
            row += " %-32s|" % txt
        print(row)

# Cross-tour aggregate
print("\n" + "=" * 76)
print("  CROSS-TOUR AGGREGATE")
print("=" * 76)
print("%-8s | %-32s | %-32s" % ("BUCKET", "UNDERDOG", "LEADER"))
print("-" * 76)
for b in BUCKETS:
    row = "%d-%dc  |" % (b, b+4)
    for side in SIDES:
        total_dpd = 0; total_n = 0; active_count = 0
        for tour in TOURS:
            cell = "%s_%s_%d-%d" % (tour, side, b, b+4)
            m = metrics(cell)
            if m["active"]:
                total_dpd += m["dpd"]; active_count += 1
            total_n += m["n"]
        if active_count > 0:
            txt = "$%.2f (%dt, N=%d)" % (total_dpd, active_count, total_n)
        elif total_n > 0:
            txt = "- (N=%d)" % total_n
        else:
            txt = "-"
        row += " %-32s|" % txt
    print(row)

# PNGs
def make_png(tour, out_path):
    fig, ax = plt.subplots(figsize=(10, 14))
    data = np.full((len(BUCKETS), 2), np.nan)
    annotations = []
    for i, b in enumerate(BUCKETS):
        row_ann = []
        for j, side in enumerate(SIDES):
            cell = "%s_%s_%d-%d" % (tour, side, b, b+4)
            m = metrics(cell)
            if m["active"]:
                data[i, j] = m["dpd"]
                dca_part = "/ %s" % m["dca_str"]
                txt = "+%d %s\n%d%%\n$%.2f\nN=%d" % (
                    m["exit"], dca_part, 100*m["hit_rate"], m["dpd"], m["n"])
            elif m["disabled"]:
                data[i, j] = -0.5
                txt = "DIS\nN=%d" % m["n"]
            elif m["n"] > 0:
                data[i, j] = -1
                txt = "-\nN=%d" % m["n"]
            else:
                txt = ""
            row_ann.append(txt)
        annotations.append(row_ann)
    cmap = mcolors.LinearSegmentedColormap.from_list("ev",
        [(0, "#d32f2f"), (0.05, "#ff9800"), (0.15, "#ffeb3b"),
         (0.3, "#8bc34a"), (0.5, "#4caf50"), (1.0, "#1b5e20")])
    cmap.set_bad(color='#e0e0e0')
    vmax = max(3, np.nanmax(data))
    im = ax.imshow(data, cmap=cmap, vmin=-0.5, vmax=vmax, aspect='auto')
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Underdog", "Leader"], fontsize=12)
    ax.set_yticks(range(len(BUCKETS)))
    ax.set_yticklabels(["%d-%dc" % (b, b+4) for b in BUCKETS], fontsize=9)
    ax.set_title("%s V4 Final ($/day @10ct)" % tour, fontsize=14, pad=15)
    for i in range(len(BUCKETS)):
        for j in range(2):
            if annotations[i][j]:
                color = "white" if (not np.isnan(data[i,j]) and (data[i,j] > 1.5 or data[i,j] < 0)) else "black"
                ax.text(j, i, annotations[i][j], ha="center", va="center", fontsize=6, color=color)
    plt.colorbar(im, ax=ax, label="$/day", shrink=0.6)
    plt.tight_layout()
    plt.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close()

for tour in TOURS:
    p = os.path.join(ANALYSIS, "v4_heatmap_%s.png" % tour)
    make_png(tour, p)
    print("Saved: %s" % p)

# Summary
print("\n" + "=" * 60)
print("FINAL V4 SUMMARY")
print("=" * 60)

nodca_dpd = 0; nodca_n = 0
dca_dpd = 0; dca_n = 0
for cell, cfg in config["active_cells"].items():
    m = metrics(cell)
    if not m["active"]:
        continue
    if cfg.get("strategy") == "DCA-A":
        dca_dpd += m["dpd"]; dca_n += 1
    else:
        nodca_dpd += m["dpd"]; nodca_n += 1

total_dpd = nodca_dpd + dca_dpd
cap = sum(sum(mm["entry_mid"] for mm in facts_by_cell.get(c, [])) / max(len(facts_by_cell.get(c,[])),1)
          * CT / 100.0 * len(facts_by_cell.get(c,[])) / DAYS
          for c in config["active_cells"])

print("\nActive cells: %d" % (nodca_n + dca_n))
print("  noDCA: %d ($%.2f/day)" % (nodca_n, nodca_dpd))
print("  DCA-A: %d ($%.2f/day)" % (dca_n, dca_dpd))
print("Aggregate $/day: $%.2f" % total_dpd)
print("Daily capital: $%.2f" % cap)
print("Daily ROI: %.1f%%" % (100 * total_dpd / cap if cap else 0))
print("\nDisabled cells: %d" % len(config["disabled_cells"]))
for d in sorted(config["disabled_cells"]):
    print("  %s" % d)

# Concerns
print("\nRemaining config concerns:")
concerns = []
for cell, cfg in config["active_cells"].items():
    m = metrics(cell)
    if not m["active"]:
        continue
    if m["n"] < 10:
        concerns.append("  %s: N=%d (low sample)" % (cell, m["n"]))
    avg = sum(mm["entry_mid"] for mm in facts_by_cell[cell]) / m["n"]
    if avg + cfg["exit_cents"] > 99:
        concerns.append("  %s: entry %.0f + exit %d = %.0f > 99 (invalid)" % (cell, avg, cfg["exit_cents"], avg + cfg["exit_cents"]))
    if m["dpd"] < 0.05:
        concerns.append("  %s: $/day=$%.2f (marginal)" % (cell, m["dpd"]))
if concerns:
    for c in concerns:
        print(c)
else:
    print("  None")

print("\nDONE")
