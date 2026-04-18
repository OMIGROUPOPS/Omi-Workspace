#!/usr/bin/env python3
"""V4 cell heatmap: ASCII + PNG."""
import json, os, csv, math
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

config = json.load(open(CONFIG_PATH))

# Load optimizer results for N, hit_rate, ev
facts_by_cell = defaultdict(list)
with open(FACTS_PATH) as f:
    for r in csv.DictReader(f):
        cat = r["category"]
        side = r["side"]
        entry = float(r["entry_mid"])
        bucket = int(entry / 5) * 5
        cell = "%s_%s_%d-%d" % (cat, side, bucket, bucket + 4)
        facts_by_cell[cell].append({
            "max_bounce": float(r["max_bounce_from_entry"]),
            "result": r["match_result"],
            "entry_mid": entry,
        })

def compute_metrics(cell_name):
    matches = facts_by_cell.get(cell_name, [])
    n = len(matches)
    cfg = config["active_cells"].get(cell_name)
    disabled = cell_name in config.get("disabled_cells", [])
    if not cfg:
        return {"n": n, "status": "disabled" if disabled else "no_data",
                "exit": 0, "dca": 0, "hit_rate": 0, "dpd": 0, "ev": 0}
    ex = cfg["exit_cents"]
    dca = cfg.get("dca_trigger_cents", 0)
    hits = sum(1 for m in matches if m["max_bounce"] >= ex)
    hit_rate = hits / n if n > 0 else 0
    total_pnl = 0
    for m in matches:
        if m["max_bounce"] >= ex:
            total_pnl += ex
        else:
            settle = 99.5 if m["result"] == "win" else 0.5
            total_pnl += (settle - m["entry_mid"])
    ev = total_pnl / n if n > 0 else 0
    dpd = total_pnl * 10 / 100.0 / 28
    return {"n": n, "status": "active", "exit": ex, "dca": dca,
            "hit_rate": hit_rate, "dpd": dpd, "ev": ev}

BUCKETS = list(range(5, 95, 5))  # 5-9 through 90-94
SIDES = ["underdog", "leader"]
TOURS = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]

# ============================================================
# ASCII heatmaps
# ============================================================
def ascii_heatmap(tour):
    print("\n" + "=" * 72)
    print("  %s HEATMAP" % tour)
    print("=" * 72)
    print("%-10s | %-30s | %-30s" % ("BUCKET", "UNDERDOG", "LEADER"))
    print("-" * 72)
    for b in BUCKETS:
        row = "%-10s |" % ("%d-%dc" % (b, b+4))
        for side in SIDES:
            cell = "%s_%s_%d-%d" % (tour, side, b, b+4)
            m = compute_metrics(cell)
            if m["status"] == "active" and m["n"] > 0:
                txt = "+%d/-%d %d%% $%.2f N=%d" % (
                    m["exit"], m["dca"], 100*m["hit_rate"], m["dpd"], m["n"])
                if m["n"] < 10:
                    txt += "*"
            elif m["status"] == "disabled":
                txt = "DISABLED (N=%d)" % m["n"]
            elif m["n"] > 0:
                txt = "no cfg (N=%d)" % m["n"]
            else:
                txt = "-"
            row += " %-30s|" % txt
        print(row)

for tour in TOURS:
    ascii_heatmap(tour)

# Cross-tour aggregate
print("\n" + "=" * 72)
print("  CROSS-TOUR AGGREGATE (sum $/day across all tours)")
print("=" * 72)
print("%-10s | %-30s | %-30s" % ("BUCKET", "UNDERDOG", "LEADER"))
print("-" * 72)
for b in BUCKETS:
    row = "%-10s |" % ("%d-%dc" % (b, b+4))
    for side in SIDES:
        total_dpd = 0
        total_n = 0
        active_count = 0
        for tour in TOURS:
            cell = "%s_%s_%d-%d" % (tour, side, b, b+4)
            m = compute_metrics(cell)
            if m["status"] == "active":
                total_dpd += m["dpd"]
                active_count += 1
            total_n += m["n"]
        if active_count > 0:
            txt = "$%.2f (%d tours, N=%d)" % (total_dpd, active_count, total_n)
        elif total_n > 0:
            txt = "disabled (N=%d)" % total_n
        else:
            txt = "-"
        row += " %-30s|" % txt
    print(row)

# ============================================================
# Flags table
# ============================================================
print("\n" + "=" * 72)
print("  FLAGS: LOW CONFIDENCE CELLS")
print("=" * 72)
print("%-35s %4s %6s %6s %s" % ("CELL", "N", "EV", "DCA", "FLAGS"))

for cell_name in sorted(config["active_cells"].keys()):
    m = compute_metrics(cell_name)
    flags = []
    if m["n"] < 10:
        flags.append("N<%d" % m["n"])
    if m["dca"] >= 25:
        flags.append("DCA>=-25c")
    if m["dpd"] < 0.10:
        flags.append("$/d<$0.10")
    # Check runner-up exit margin
    matches = facts_by_cell.get(cell_name, [])
    if matches:
        ex = m["exit"]
        best_ev = m["ev"]
        for alt in range(max(5, ex-3), min(61, ex+4)):
            if alt == ex:
                continue
            alt_pnl = 0
            for mm in matches:
                if mm["max_bounce"] >= alt:
                    alt_pnl += alt
                else:
                    settle = 99.5 if mm["result"] == "win" else 0.5
                    alt_pnl += (settle - mm["entry_mid"])
            alt_ev = alt_pnl / len(matches)
            if best_ev - alt_ev < 3:
                flags.append("margin<3c(+%d=%.1f)" % (alt, alt_ev))
                break
    if flags:
        print("%-35s %4d %+5.1fc %4dc  %s" % (cell_name, m["n"], m["ev"], m["dca"], ", ".join(flags)))

# ============================================================
# PNG heatmaps
# ============================================================
def make_png(tour, out_path):
    fig, ax = plt.subplots(figsize=(10, 14))
    data = np.full((len(BUCKETS), 2), np.nan)
    annotations = []

    for i, b in enumerate(BUCKETS):
        row_ann = []
        for j, side in enumerate(SIDES):
            cell = "%s_%s_%d-%d" % (tour, side, b, b+4)
            m = compute_metrics(cell)
            if m["status"] == "active" and m["n"] > 0:
                data[i, j] = m["dpd"]
                txt = "+%d/-%d\n%d%%\n$%.2f\nN=%d" % (
                    m["exit"], m["dca"], 100*m["hit_rate"], m["dpd"], m["n"])
            elif m["status"] == "disabled":
                data[i, j] = -0.5
                txt = "DIS\nN=%d" % m["n"]
            elif m["n"] > 0:
                data[i, j] = -1
                txt = "no cfg\nN=%d" % m["n"]
            else:
                txt = ""
            row_ann.append(txt)
        annotations.append(row_ann)

    cmap = mcolors.LinearSegmentedColormap.from_list("ev",
        [(0, "#d32f2f"), (0.15, "#ff9800"), (0.3, "#ffeb3b"),
         (0.5, "#4caf50"), (1.0, "#1b5e20")])
    cmap.set_bad(color='#e0e0e0')

    vmin, vmax = -0.5, max(3, np.nanmax(data))
    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Underdog", "Leader"], fontsize=12)
    ax.set_yticks(range(len(BUCKETS)))
    ax.set_yticklabels(["%d-%dc" % (b, b+4) for b in BUCKETS], fontsize=9)
    ax.set_title("%s V4 Cell Heatmap ($/day @10ct)" % tour, fontsize=14, pad=15)

    for i in range(len(BUCKETS)):
        for j in range(2):
            txt = annotations[i][j]
            if txt:
                color = "white" if data[i, j] > 1.5 or data[i, j] < 0 else "black"
                ax.text(j, i, txt, ha="center", va="center", fontsize=7, color=color)

    plt.colorbar(im, ax=ax, label="$/day", shrink=0.6)
    plt.tight_layout()
    plt.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close()
    print("Saved: %s" % out_path)

for tour in TOURS:
    make_png(tour, os.path.join(ANALYSIS, "v4_heatmap_%s.png" % tour))

# Aggregate heatmap
fig, ax = plt.subplots(figsize=(10, 14))
data = np.full((len(BUCKETS), 2), np.nan)
for i, b in enumerate(BUCKETS):
    for j, side in enumerate(SIDES):
        total = 0
        any_active = False
        for tour in TOURS:
            cell = "%s_%s_%d-%d" % (tour, side, b, b+4)
            m = compute_metrics(cell)
            if m["status"] == "active":
                total += m["dpd"]
                any_active = True
        if any_active:
            data[i, j] = total

cmap2 = mcolors.LinearSegmentedColormap.from_list("ev2",
    [(0, "#ffeb3b"), (0.3, "#4caf50"), (1.0, "#1b5e20")])
cmap2.set_bad(color='#e0e0e0')
im = ax.imshow(data, cmap=cmap2, vmin=0, vmax=max(8, np.nanmax(data)), aspect='auto')
ax.set_xticks([0, 1])
ax.set_xticklabels(["Underdog", "Leader"], fontsize=12)
ax.set_yticks(range(len(BUCKETS)))
ax.set_yticklabels(["%d-%dc" % (b, b+4) for b in BUCKETS], fontsize=9)
ax.set_title("V4 AGGREGATE $/day by Bucket × Side (all tours)", fontsize=14, pad=15)
for i in range(len(BUCKETS)):
    for j in range(2):
        if not np.isnan(data[i, j]):
            ax.text(j, i, "$%.2f" % data[i, j], ha="center", va="center",
                    fontsize=9, color="white" if data[i, j] > 3 else "black")
plt.colorbar(im, ax=ax, label="$/day", shrink=0.6)
plt.tight_layout()
agg_path = os.path.join(ANALYSIS, "v4_heatmap_aggregate.png")
plt.savefig(agg_path, dpi=100, bbox_inches='tight')
plt.close()
print("Saved: %s" % agg_path)

print("\nDONE")
