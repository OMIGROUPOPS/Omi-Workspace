#!/usr/bin/env python3
"""Visual ATP_MAIN scorecard: every cent, all dimensions. Per cell shows exit
offset (top), then four bars: hit% (blue), ROI% (green), daily PnL (gold),
fills/day (violet). Numeric readout: EV/trade and daily ROI%. Fixed 10c sizing."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
matplotlib.rcParams["text.parse_math"] = False  # treat $ literally

d = json.load(open("analysis/scorecard_atp_main.json"))
# scales for normalization (use robust maxima across both panels)
allc = [x for x in d["underdog"] + d["leader"] if not x.get("skip")]
MAXdp = max(x["daily_pnl_c"] for x in allc)
MAXfp = max(x["fills_per_day"] for x in allc)

def panel(ax, arr, title):
    ax.set_facecolor("#0e1116")
    n = len(arr)
    for i, x in enumerate(arr):
        x0 = i
        if x.get("skip"):
            ax.add_patch(Rectangle((x0 + 0.05, 0), 0.9, 1, facecolor="#3a1d1d"))
            ax.text(x0 + 0.5, 0.5, "SKIP", ha="center", va="center", rotation=90,
                    color="#ffc9c9", fontsize=8, fontweight="bold")
            ax.text(x0 + 0.5, -0.07, f"{x['c']}\u00a2", ha="center", va="top",
                    color="#8b98a5", fontsize=8)
            continue
        ax.add_patch(Rectangle((x0 + 0.05, 0), 0.9, 1, facecolor="#161d27",
                               edgecolor="#222c38", linewidth=0.7))
        bars = [
            (x["hit_pct"] / 100.0, "#4ea3ff"),
            (min(x["roi_pct"], 50) / 50.0, "#52c98c"),
            (x["daily_pnl_c"] / MAXdp, "#ffd166"),
            (x["fills_per_day"] / MAXfp, "#b18cff"),
        ]
        bw = 0.195
        for j, (h, col) in enumerate(bars):
            ax.add_patch(Rectangle((x0 + 0.07 + j * (bw + 0.005), 0.12),
                                   bw, 0.72 * max(h, 0), facecolor=col))
        ax.text(x0 + 0.5, 0.97, f"+{x['exit_offset']}", ha="center", va="top",
                color="#eafff5", fontsize=9.5, fontweight="bold")
        ax.text(x0 + 0.5, -0.07, f"{x['c']}\u00a2", ha="center", va="top",
                color="#cdd9e5", fontsize=8)
        ax.text(x0 + 0.5, 0.05, f"{x['ev_per_trade_c']:.1f}", ha="center",
                va="center", color="#9aa7b4", fontsize=6.3)
    ax.set_xlim(0, n); ax.set_ylim(-0.18, 1.0)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(title, color="#e8eef5", fontsize=13.5, fontweight="bold",
                 loc="left", pad=8)

fig, axes = plt.subplots(2, 1, figsize=(18, 9), facecolor="#0e1116")
fig.suptitle(f"ATP_MAIN  \u00b7  per-cent scorecard  (shoulder@70%, fixed 10\u00a2 size, {d['span_days']}d tape)",
             color="#e8eef5", fontsize=17, fontweight="bold", y=0.99)

# per-side totals in subtitle
def tot(a):
    t = [x for x in a if not x.get("skip")]
    return (sum(x["daily_pnl_c"] for x in t), sum(x["total_pnl_c"] for x in t) / 100.0,
            np.mean([x["hit_pct"] for x in t]), np.mean([x["roi_pct"] for x in t]))
du = tot(d["underdog"]); dl = tot(d["leader"])
fig.text(0.5, 0.945,
         f"UNDERDOG engine: {du[0]:.0f}\u00a2/day  \u00b7  ${du[1]:.0f} total  \u00b7  hit {du[2]:.0f}%  \u00b7  ROI {du[3]:.0f}%      |      "
         f"LEADER ballast: {dl[0]:.0f}\u00a2/day  \u00b7  ${dl[1]:.0f} total  \u00b7  hit {dl[2]:.0f}%  \u00b7  ROI {dl[3]:.0f}%",
         ha="center", color="#cdd9e5", fontsize=11)
fig.text(0.5, 0.915,
         "top = exit offset (+\u00a2)   \u00b7   bars: hit% (blue)  ROI% (green)  daily PnL (gold)  fills/day (violet)   \u00b7   small text = EV/trade (\u00a2)",
         ha="center", color="#8b98a5", fontsize=10)

panel(axes[0], d["underdog"], "underdog (longshot)  \u00b7  entry 10\u201344\u00a2  \u00b7  the engine")
panel(axes[1], d["leader"], "leader (favorite)  \u00b7  entry 55\u201389\u00a2  \u00b7  the ballast (stability for 2-N holds)")

leg = [Patch(facecolor="#4ea3ff", label="hit %"),
       Patch(facecolor="#52c98c", label="ROI %"),
       Patch(facecolor="#ffd166", label="daily PnL"),
       Patch(facecolor="#b18cff", label="fills/day")]
fig.legend(handles=leg, loc="lower center", ncol=4, frameon=False, fontsize=11,
           labelcolor="#cdd9e5", bbox_to_anchor=(0.5, 0.0))
plt.subplots_adjust(left=0.02, right=0.98, top=0.89, bottom=0.05, hspace=0.30)
plt.savefig("analysis/scorecard_atp_main.png", dpi=125, facecolor="#0e1116")
print("wrote analysis/scorecard_atp_main.png")
