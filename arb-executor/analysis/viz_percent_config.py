#!/usr/bin/env python3
"""Visual: best config per cent. Each cell = one entry cent; the big value is its
exit offset (+c) or HOLD/SKIP; color = realized EV per N. Gold border = pooled
basis (thin cent, blend leaned on neighbors). EV shown via color only (legend
colorbar) to keep cells uncluttered and readable."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch, Rectangle

rows = json.load(open("analysis/percent_config_dump.json"))
idx = {(r["cat"], r["dir"], r["cent"]): r for r in rows}
CATS = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]
LEAD = list(range(55, 90))   # 35 cents
DOG = list(range(10, 45))    # 35 cents

evs = [r["ev"] for r in rows if r["ev"] and r["ev"] > 0]
EVMAX = float(np.percentile(evs, 90))
cmap = LinearSegmentedColormap.from_list(
    "ev", ["#0c3326", "#15623f", "#249b63", "#52c98c", "#9fe9c4"])

# Each category gets its own figure-row containing two stacked strips
# (leader, underdog). Strips are TALL so 2 text lines breathe. Figure is wide.
fig, axes = plt.subplots(8, 1, figsize=(20, 22), facecolor="#0e1116")
fig.suptitle("Best exit config per cent  \u2014  v3 pooled-surface blend",
             color="#e8eef5", fontsize=24, fontweight="bold", y=0.997)
fig.text(0.5, 0.978, "each cell = one entry cent   \u00b7   big number = exit offset (+\u00a2) above entry  ·  HOLD / SKIP  ·  cell color = realized EV per N (greener = richer)   \u00b7   gold border = pooled basis (thin cent)",
         ha="center", color="#8b98a5", fontsize=12.5)


def strip(ax, cat, direction, cents, label):
    n = len(cents)
    ax.set_facecolor("#0e1116")
    ax.set_xlim(0, n)
    ax.set_ylim(0, 1)
    for i, c in enumerate(cents):
        r = idx.get((cat, direction, c))
        x0 = i
        if r is None or r["ev"] is None or r["ev"] <= 0:   # SKIP
            ax.add_patch(Rectangle((x0 + 0.04, 0.04), 0.92, 0.92,
                                   facecolor="#3a1d1d",
                                   edgecolor="#7a3030", linewidth=1.0))
            ax.text(x0 + 0.5, 0.62, "SKIP", ha="center", va="center",
                    color="#ffc9c9", fontsize=11.5, fontweight="bold")
            ax.text(x0 + 0.5, 0.27, f"{c}\u00a2", ha="center", va="center",
                    color="#e0b3b3", fontsize=10.5, fontweight="bold")
            continue
        ev = r["ev"]
        lum = min(ev, EVMAX) / EVMAX
        face = cmap(lum)
        pooled = r["basis"] == "pooled"
        ax.add_patch(Rectangle((x0 + 0.04, 0.04), 0.92, 0.92, facecolor=face,
                               edgecolor=("#ffd166" if pooled else "#1b2430"),
                               linewidth=(3.0 if pooled else 1.0), zorder=2))
        exit_lab = "HOLD" if r["exit"] is None else f"+{r['exit']}"
        # dark text on light/green cells, light text on dark cells
        txt = "#08231a" if lum > 0.5 else "#eafff5"
        ax.text(x0 + 0.5, 0.62, exit_lab, ha="center", va="center",
                color=txt, fontsize=13.5, fontweight="bold", zorder=3)
        ax.text(x0 + 0.5, 0.27, f"{c}\u00a2", ha="center", va="center",
                color=txt, fontsize=10.5, zorder=3, alpha=1.0, fontweight="bold")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(f"{cat}   \u00b7   {label}", color="#e8eef5", fontsize=14.5,
                 fontweight="bold", loc="left", pad=6)


order = []
for cat in CATS:
    order.append((cat, "leader", LEAD, "leader (favorite)   entry 55\u201389\u00a2"))
    order.append((cat, "underdog", DOG, "underdog (longshot)   entry 10\u201344\u00a2"))

for ax, (cat, d, cents, lab) in zip(axes, order):
    strip(ax, cat, d, cents, lab)

# compact horizontal EV gradient legend (own inset axis, bottom-left)
cax = fig.add_axes([0.045, 0.022, 0.16, 0.009])
grad = np.linspace(0, 1, 256).reshape(1, -1)
cax.imshow(grad, aspect="auto", cmap=cmap)
cax.set_xticks([0, 255]); cax.set_xticklabels(["low EV", f"\u2265{EVMAX:.0f}\u00a2"],
                                              color="#8b98a5", fontsize=9)
cax.set_yticks([])
cax.text(128, 3.2, "realized EV per N (cell color)", ha="center", va="top",
         color="#cdd9e5", fontsize=10, transform=cax.transData)
for s in cax.spines.values():
    s.set_visible(False)

leg = [
    Patch(facecolor="#249b63", edgecolor="#1b2430", label="own-N basis  (cent trusts its own tapes)"),
    Patch(facecolor="#249b63", edgecolor="#ffd166", linewidth=3.0, label="pooled basis  (thin cent \u2014 blend leans on neighbors)"),
    Patch(facecolor="#3a1d1d", edgecolor="#7a3030", label="SKIP  (achievable EV \u2264 0 \u2014 no profitable exit)"),
]
fig.legend(handles=leg, loc="lower center", ncol=3, frameon=False,
           fontsize=12.5, labelcolor="#cdd9e5", bbox_to_anchor=(0.60, 0.004))

plt.subplots_adjust(left=0.015, right=0.985, top=0.965, bottom=0.045, hspace=0.42)
plt.savefig("analysis/percent_config_v3.png", dpi=120, facecolor="#0e1116")
print("wrote analysis/percent_config_v3.png")
