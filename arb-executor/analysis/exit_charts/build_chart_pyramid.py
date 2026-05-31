"""
build_chart_pyramid.py — PYRAMID exit-opportunity chart.

Geometry IS the message. Rows = cost-basis cell c (5-94), even line (c=50) centred.
Row c has exactly 99-c exit-offset slots (X = 1..99-c, reaching c+1 .. 99). So the
apex (high c) is narrow — 95c has only 4 slots (+1..+4 -> 96/97/98/99) — and the
base (low c) is wide — 5c has 94 slots. Row WIDTH = opportunity space: 95c geometry
shows it isn't worth much. 99 = the lock / ceiling.

Fill metric = CORRECTED, skip-inclusive:
    fill(c,X) = mean[ max(forward price_high of ticker) >= (c+X)/100 ]
Two color layers (toggle):
    (i)  fill rate %
    (ii) ROI-on-cost = (X/c) * fill_rate
Optimal block per row = argmax_X [ fill_rate * ROI-on-cost ]  (NOT max fill alone).
Optima should trace a diagonal: far-right (big X) in wide underdog rows -> hard-left
(small X) in narrow favorite rows. Off-diagonal optima are FLAGGED (magenta).
Every optimal block surfaces its FULL variable stack on hover: fill%, ROI-on-cost,
miss/comeback behaviour, N (band density), mirror-check (partner favorite reflected
down-excursion / level-sum) — never a single-number verdict.

Usage: python build_chart_pyramid.py [--input PATH] [--category ATP_MAIN] [--out FILE]
"""
from __future__ import annotations
import argparse
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

import chart_common as cc


def per_block_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (c, X) with fill, roi, score, miss/comeback, N, mirror-check."""
    rows = []
    sub = df[df["cell"].notna()]
    for c, g in sub.groupby("cell"):
        c = int(c)
        ft = g["fwd_max_traded"].to_numpy() * 100.0  # cents; NaN where nothing traded forward
        n = len(g)
        reached_cost = ft >= c                         # recovered at least to cost basis
        # mirror-check (in-row, verified instrument): favorite partner level + bid-sum
        mc_partner = float(np.nanmean(g["partner_yes_bid_close"].to_numpy()) * 100)
        mc_sum = float(np.nanmean(g["paired_yes_bid_sum"].to_numpy()))
        for X in range(1, cc.LOCK - c + 1):            # reach up to 99
            tgt = c + X
            fill_mask = ft >= tgt
            fill = float(np.nanmean(fill_mask.astype(float)))
            miss = 1.0 - fill
            non_fill = ~fill_mask & ~np.isnan(ft)
            # comeback: of the misses, how many at least recovered to cost basis (c) but fell short of target
            cb = float(np.mean(reached_cost[non_fill])) if non_fill.any() else 0.0
            roi = (X / c) * fill
            rows.append({
                "c": c, "X": X, "target": tgt, "N": n,
                "fill": fill, "roi_on_cost": roi, "score": fill * roi,
                "miss": miss, "comeback_of_miss": cb,
                "mc_partner_at_entry": mc_partner, "mc_bid_sum": mc_sum,
            })
    t = pd.DataFrame(rows)
    t["band"] = t["c"].apply(cc.band_of)
    return t


def optimal_per_row(t: pd.DataFrame) -> pd.DataFrame:
    """argmax score per cell, then flag off-diagonal optima.

    Expected: optimal X decreases monotonically as c increases (diagonal). We fit a
    robust monotone reference (rolling median of opt-X over c) and flag any row whose
    optimal X deviates by > FLAG_TOL from that reference.
    """
    idx = t.groupby("c")["score"].idxmax()
    opt = t.loc[idx].sort_values("c").reset_index(drop=True)
    ref = opt["X"].rolling(7, center=True, min_periods=3).median()
    FLAG_TOL = 12
    opt["ref_X"] = ref
    opt["off_diagonal"] = (opt["X"] - ref).abs() > FLAG_TOL
    return opt


# pyramid x-position of slot X in row of width W (centred on 0)
def slot_x(X: int, W: int) -> float:
    return X - (W + 1) / 2.0


def build(df: pd.DataFrame, out_html: str, category: str):
    t = per_block_table(df)
    opt = optimal_per_row(t)
    opt_keys = set(zip(opt["c"], opt["X"]))
    offdiag_keys = set(zip(opt.loc[opt.off_diagonal, "c"], opt.loc[opt.off_diagonal, "X"]))

    # geometry
    t["W"] = cc.LOCK - t["c"]
    t["xpos"] = [slot_x(X, W) for X, W in zip(t["X"], t["W"])]
    t["ypos"] = t["c"]  # y axis reversed so high c (apex) is on top

    hov = [
        f"<b>cost c={r.c}c  →  exit +{r.X}c (sell @ {r.target}c)</b><br>"
        f"fill rate: {r.fill*100:.1f}%<br>"
        f"ROI-on-cost: {r.roi_on_cost*100:.1f}%  (= {r.X}/{r.c} × fill)<br>"
        f"miss: {r.miss*100:.1f}%  · of misses recovered-to-cost: {r.comeback_of_miss*100:.1f}%<br>"
        f"N (band density): {r.N}<br>"
        f"mirror-check: favorite ≈ {r.mc_partner_at_entry:.0f}c at entry · bid-sum {r.mc_bid_sum:.3f}"
        + ("<br><b>★ OPTIMAL (max fill×ROI)</b>" if (r.c, r.X) in opt_keys else "")
        + ("  ⚑ OFF-DIAGONAL" if (r.c, r.X) in offdiag_keys else "")
        for r in t.itertuples()
    ]

    msize = 7
    fig = go.Figure()
    # layer (i): fill %
    fig.add_trace(go.Scatter(
        x=t.xpos, y=t.ypos, mode="markers", name="fill %",
        marker=dict(symbol="square", size=msize, color=t.fill * 100, colorscale="YlGnBu",
                    cmin=0, cmax=100, colorbar=dict(title="fill %"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=True,
    ))
    # layer (ii): ROI-on-cost %
    fig.add_trace(go.Scatter(
        x=t.xpos, y=t.ypos, mode="markers", name="ROI-on-cost %",
        marker=dict(symbol="square", size=msize, color=t.roi_on_cost * 100, colorscale="Plasma",
                    cmin=0, cmax=float(np.nanpercentile(t.roi_on_cost * 100, 99)),
                    colorbar=dict(title="ROI-on-cost %"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=False,
    ))
    # optimal highlight (always on): white outlined squares; magenta if off-diagonal
    ot = t[[(c, X) in opt_keys for c, X in zip(t.c, t.X)]].copy()
    ocolors = ["#ff2bd6" if (c, X) in offdiag_keys else "#ffffff" for c, X in zip(ot.c, ot.X)]
    fig.add_trace(go.Scatter(
        x=ot.xpos, y=ot.ypos, mode="markers", name="optimal (fill×ROI)",
        marker=dict(symbol="square-open", size=msize + 4,
                    color="rgba(0,0,0,0)", line=dict(width=2, color=ocolors)),
        text=[h for h, keep in zip(hov, [(c, X) in opt_keys for c, X in zip(t.c, t.X)]) if keep],
        hoverinfo="text", visible=True,
    ))

    n_off = int(opt.off_diagonal.sum())
    fig.update_layout(
        title=(f"PYRAMID — {category} exit opportunity ({df.ticker.nunique()} tickers)<br>"
               f"<sub>row width = opportunity space (99−c slots) · CORRECTED price_high fill · "
               f"★ optimal = argmax(fill×ROI) · ⚑ {n_off} off-diagonal optima flagged</sub>"),
        xaxis=dict(title="exit offset slots (centred; left=+1 … right=+(99−c) reaching the 99 lock)",
                   zeroline=False, showgrid=False),
        yaxis=dict(title="cost-basis cell c (cents) — apex 94c (narrow) top, base 5c (wide) bottom",
                   autorange="reversed", dtick=5, showgrid=False),
        template="plotly_dark", width=1400, height=1150, plot_bgcolor="#0a0a0a",
        updatemenus=[dict(
            type="buttons", direction="right", x=0.0, y=1.06, xanchor="left",
            buttons=[
                dict(label="fill %", method="update",
                     args=[{"visible": [True, False, True]}]),
                dict(label="ROI-on-cost %", method="update",
                     args=[{"visible": [False, True, True]}]),
            ],
        )],
    )
    fig.write_html(out_html, include_plotlyjs="cdn")

    # console summary: the optima diagonal
    return {
        "n_blocks": int(len(t)), "n_off_diagonal": n_off,
        "optima": [{"c": int(r.c), "X": int(r.X), "fill": round(r.fill, 3),
                    "roi_on_cost": round(r.roi_on_cost, 3), "off_diagonal": bool(r.off_diagonal)}
                   for r in opt.itertuples()],
        "out": out_html,
    }, t, opt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=cc.DEFAULT_INPUT)
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "chart_pyramid.html"))
    ap.add_argument("--dump", default=os.path.join(os.path.dirname(__file__), "pyramid_blocks.csv"))
    args = ap.parse_args()
    df = cc.load_universe(args.input, args.category)
    summary, t, opt = build(df, args.out, args.category)
    t.to_csv(args.dump, index=False)
    print("PYRAMID:", {k: v for k, v in summary.items() if k != "optima"})
    print("optima diagonal (c -> X@fill):")
    for o in summary["optima"]:
        flag = " <<OFF-DIAG" if o["off_diagonal"] else ""
        print(f"  c={o['c']:2d}  +{o['X']:2d}  fill={o['fill']*100:5.1f}%  roi={o['roi_on_cost']*100:6.1f}%{flag}")


if __name__ == "__main__":
    main()
