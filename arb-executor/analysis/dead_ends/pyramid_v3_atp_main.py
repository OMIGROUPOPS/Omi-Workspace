#!/usr/bin/env python3
"""
ATP_MAIN PYRAMID v3 (final) — column-strip pyramid, fed by the corpus-
reconstructed GROUND-TRUTH curves (curve_atp_main.json), validated to match the
locked achievable surface (82/90 own-N cents agree exactly; the 8 differ only
on pooled-basis cents where the surface deliberately leaned on the neighbor
cluster).

Layout = the pyramid the user likes: each cent is a vertical strip, each square
is one exit offset (+1 at bottom -> the 99c ceiling at top). Coloring = ROI%
(RdYlGn diverging @ 0) so cheap and expensive cents compete on one scale, exactly
like the Ground Truth v3 heatmap. The chosen achievable best-X is ringed; the
hit% under each cent flags DOABLE / MODERATE / LOTTERY.

No SKIP flags, no pool badges — pure descriptive surface (per user).
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["text.parse_math"] = False
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.colorbar import ColorbarBase

C = json.load(open("curve_atp_main.json"))
C = {int(k): v for k, v in C.items()}

# RdYlGn diverging on ROI%, centered at 0 — matches the Ground Truth v3 lens.
cmap = LinearSegmentedColormap.from_list(
    "roi", ["#a01722", "#e5484d", "#caa83a", "#2a6e3f", "#46d17a"])
ROI_LO, ROI_HI = -60.0, 60.0


def roi_color(roi):
    t = (np.clip(roi, ROI_LO, ROI_HI) - ROI_LO) / (ROI_HI - ROI_LO)
    return cmap(t)


def hit_tier(hit):
    if hit >= 70: return "#46d17a"      # DOABLE
    if hit >= 45: return "#e3c04a"      # MODERATE
    return "#e5484d"                    # LOTTERY


def panel(ax, cents, title):
    ax.set_facecolor("#0e1116")
    for i, c in enumerate(cents):
        rec = C.get(c)
        x0 = i
        if not rec or rec["n"] == 0 or not rec["curve"]:
            ax.text(x0 + 0.5, 50, "no\ndata", ha="center", va="center",
                    color="#5a6675", fontsize=7)
            continue
        cmap_cells = {p["X"]: p for p in rec["curve"]}
        ceiling = max(cmap_cells.keys())
        for X in range(1, ceiling + 1):
            p = cmap_cells.get(X)
            if p is None:
                continue
            ax.add_patch(Rectangle((x0 + 0.08, X - 0.5), 0.84, 1.0,
                                    facecolor=roi_color(p["roi"]),
                                    edgecolor="none"))
        # chosen achievable best-X -> white ring
        bx = rec["achievable"]["bestX"]
        if bx is not None and bx in cmap_cells:
            ax.add_patch(Rectangle((x0 + 0.04, bx - 0.5), 0.92, 1.0,
                                    fill=False, edgecolor="#ffffff",
                                    linewidth=1.8, zorder=5))
            ax.text(x0 + 0.5, bx, f"+{bx}", ha="center", va="center",
                    color="#ffffff", fontsize=7.3, fontweight="bold", zorder=6)
        # cent label + hit-tier + EV underneath
        ah = rec["achievable"]["hit"] or 0
        ax.text(x0 + 0.5, -3, f"{c}c", ha="center", va="top",
                color="#c7d0da", fontsize=8, fontweight="bold")
        ax.text(x0 + 0.5, -8, f"{ah:.0f}%", ha="center", va="top",
                color=hit_tier(ah), fontsize=7.5, fontweight="bold")
        ax.text(x0 + 0.5, -13, f"{rec['achievable']['ev']:.1f}c", ha="center",
                va="top", color="#8b98a5", fontsize=6.8)

    ax.set_xlim(0, len(cents))
    ax.set_ylim(-16, 100)
    ax.set_xticks([])
    ax.set_yticks([1, 10, 20, 30, 40, 50, 60, 70, 80, 90])
    ax.tick_params(colors="#8b98a5", labelsize=8)
    for s in ax.spines.values():
        s.set_color("#2a323d")
    ax.set_ylabel("exit offset  +X   (T = c + X, climbing to 99c ceiling)",
                  color="#c7d0da", fontsize=9)
    ax.set_title(title, color="#ffffff", fontsize=12.5,
                 fontweight="bold", loc="left", pad=10)


fig, axes = plt.subplots(2, 1, figsize=(20, 13))
fig.patch.set_facecolor("#0e1116")
panel(axes[0], list(range(5, 50)),
      "UNDERDOGS  5-49c    \u2014    the engine: deep bounces, low hit")
panel(axes[1], list(range(50, 95)),
      "FAVORITES  50-94c    \u2014    the ballast: shallow exits, high hit")

fig.text(0.012, 0.965,
         "ATP_MAIN  \u00b7  PYRAMID  \u00b7  ROI per exit offset, every level to the 99c ceiling  (ground truth = corpus-reconstructed, matches locked achievable)",
         color="#ffffff", fontsize=14, fontweight="bold")
fig.text(0.012, 0.945,
         "color = ROI% at that exit (RdYlGn @ 0)   \u00b7   white ring = chosen achievable best-X   "
         "\u00b7   under each cent: hit%  (green=DOABLE \u226570 / yellow=MODERATE 45-70 / red=LOTTERY <45)  +  EV(c)",
         color="#8b98a5", fontsize=9.5)

cax = fig.add_axes([0.40, 0.012, 0.30, 0.015])
cb = ColorbarBase(cax, cmap=cmap, norm=Normalize(ROI_LO, ROI_HI),
                  orientation="horizontal")
cb.set_label("ROI %  (EV / cost basis)", color="#c7d0da", fontsize=8.5)
cb.ax.tick_params(colors="#8b98a5", labelsize=7.5)
cb.outline.set_edgecolor("#2a323d")

plt.subplots_adjust(left=0.05, right=0.99, top=0.92, bottom=0.05, hspace=0.28)
plt.savefig("pyramid_v3_atp_main.png", dpi=125, facecolor="#0e1116")
print("saved pyramid_v3_atp_main.png")
