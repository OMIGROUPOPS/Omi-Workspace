#!/usr/bin/env python3
"""ATP_MAIN pyramid: per-cent EV / hit% / ROI% across exit targets, with the
conservative EV-shoulder (>=70% of positive-exit peak EV, clamped >0) marked.
Two panels: underdog (10-44c) and leader (55-89c). Shows every dimension so the
shoulder placement is eyeballable."""
import json
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

s = json.load(open("data/durable/exit_atlas_v1/atp_main_pooled_surface_v3.json"))
gE = defaultdict(dict); gH = defaultdict(dict); gR = defaultdict(dict)
for cell in s["cells"]:
    gE[cell["c"]][cell["R"]] = cell["ev"]
    gH[cell["c"]][cell["R"]] = cell["hit"]
    gR[cell["c"]][cell["R"]] = cell["roi"]

THR = 0.70

def shoulder(c):
    # R IS the exit offset (+X) directly; R ranges 1..(99-c)
    g = gE[c]
    if not g:
        return None
    peak = max(g.values())
    if peak <= 0:
        return None
    R = min(R for R, ev in g.items() if ev >= THR * peak)  # lowest offset keeping 70% of peak EV
    return {"X": R, "R": R, "ev": g[R], "hit": gH[c][R], "roi": gR[c][R],
            "ppeak": peak}

def panel(ax, cents, title):
    ax.set_facecolor("#0e1116")
    n = len(cents)
    for i, c in enumerate(cents):
        sh = shoulder(c)
        x0 = i
        if sh is None:
            ax.add_patch(Rectangle((x0 + 0.05, 0.0), 0.9, 1.0, facecolor="#3a1d1d"))
            ax.text(x0 + 0.5, 0.5, "SKIP", ha="center", va="center",
                    color="#ffc9c9", fontsize=9, fontweight="bold", rotation=90)
            ax.text(x0 + 0.5, -0.06, f"{c}\u00a2", ha="center", va="top",
                    color="#8b98a5", fontsize=8.5)
            continue
        # three mini-bars: hit (0-100%), roi (0-50%), ev (0-7). Each normalized to
        # its own scale so favorites (low ROI) and underdogs (high ROI) both read.
        hit = sh["hit"]; roi = sh["roi"]; ev = sh["ev"]
        ax.add_patch(Rectangle((x0 + 0.05, 0.0), 0.9, 1.0, facecolor="#161d27",
                               edgecolor="#222c38", linewidth=0.8))
        bw = 0.26
        ax.add_patch(Rectangle((x0 + 0.08, 0.12), bw, 0.74 * (hit / 100.0),
                               facecolor="#4ea3ff"))      # hit%
        ax.add_patch(Rectangle((x0 + 0.08 + bw + 0.02, 0.12), bw, 0.74 * (min(roi, 50) / 50.0),
                               facecolor="#52c98c"))      # roi%
        ax.add_patch(Rectangle((x0 + 0.08 + 2 * (bw + 0.02), 0.12), bw, 0.74 * (min(ev, 7) / 7.0),
                               facecolor="#ffd166"))      # ev
        # exit target label on top
        ax.text(x0 + 0.5, 0.965, f"+{sh['X']}", ha="center", va="top",
                color="#eafff5", fontsize=10, fontweight="bold")
        ax.text(x0 + 0.5, -0.06, f"{c}\u00a2", ha="center", va="top",
                color="#cdd9e5", fontsize=8.5)
        # tiny numeric readout: hit% / roi%
        ax.text(x0 + 0.5, 0.05, f"{hit:.0f}/{roi:.0f}", ha="center", va="center",
                color="#9aa7b4", fontsize=6.5)
    ax.set_xlim(0, n); ax.set_ylim(-0.16, 1.0)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(title, color="#e8eef5", fontsize=14, fontweight="bold",
                 loc="left", pad=8)

fig, axes = plt.subplots(2, 1, figsize=(18, 8.5), facecolor="#0e1116")
fig.suptitle("ATP_MAIN  \u00b7  conservative EV-shoulder per cent  (70% of peak, positive exits)",
             color="#e8eef5", fontsize=18, fontweight="bold", y=0.99)
fig.text(0.5, 0.945, "top number = exit offset (+\u00a2)   \u00b7   bars per cent: hit% (blue, /100)   ROI% (green, /50)   EV (gold, /7)   \u00b7   small text = hit%/ROI%",
         ha="center", color="#8b98a5", fontsize=11)
panel(axes[0], list(range(10, 45)), "underdog (longshot)  \u00b7  entry 10\u201344\u00a2")
panel(axes[1], list(range(55, 90)), "leader (favorite)  \u00b7  entry 55\u201389\u00a2")
plt.subplots_adjust(left=0.02, right=0.98, top=0.91, bottom=0.04, hspace=0.28)
plt.savefig("analysis/pyramid_atp_main.png", dpi=125, facecolor="#0e1116")
print("wrote analysis/pyramid_atp_main.png")
