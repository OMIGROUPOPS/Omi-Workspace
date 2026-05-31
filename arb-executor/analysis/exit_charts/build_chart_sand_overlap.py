"""
build_chart_sand_overlap.py — SAND / OVERLAP heatmap.

Proves neighbor-pooling is legitimate: the same physical price paths are recovered
from multiple sample points, so pooling cell c with c±1 (etc.) does not invent data.

Instrument (PINNED — grain-mass, option b):
    value(c, k) = (minute-grains spent at cell c whose ticker ALSO visits cell c+k)
                  / (total minute-grains spent at cell c)
    A "grain" is one minute a ticker spends at cell c (= round(100*yes_bid_close)).
    "Visits c+k" = that same ticker has >=1 grain at c+k anywhere in its life.
    k = 0 is 1.0 by construction. Expect ~97-100% at k=+-1 decaying outward.

Usage:
    python build_chart_sand_overlap.py [--input PATH] [--category ATP_MAIN] [--out FILE]
PATH may be a parquet file, a directory, or a glob — swap it to re-run on the full universe.
"""
from __future__ import annotations
import argparse
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

import chart_common as cc

OFFSETS = list(range(-5, 6))  # k = -5 .. +5


def grain_mass_overlap(df: pd.DataFrame):
    """Returns (cells, matrix[len(cells) x len(OFFSETS)], counts[c], n_tickers[c])."""
    sub = df[df["cell"].notna()].copy()
    sub["cell"] = sub["cell"].astype(int)

    # grains[(ticker, cell)] = minutes that ticker spent at that cell
    grains = sub.groupby(["ticker", "cell"]).size()
    # set of cells each ticker ever visits
    visits = sub.groupby("ticker")["cell"].apply(lambda s: set(s.unique())).to_dict()

    cells = list(range(cc.CELL_MIN, cc.CELL_MAX + 1))
    mat = np.full((len(cells), len(OFFSETS)), np.nan)
    total_mass = {c: 0 for c in cells}
    n_tickers = {c: 0 for c in cells}

    # pre-aggregate grain mass per (cell -> {ticker: mass})
    by_cell: dict[int, dict[str, int]] = {}
    for (tk, c), m in grains.items():
        by_cell.setdefault(int(c), {})[tk] = int(m)
        if int(c) in total_mass:
            total_mass[int(c)] += int(m)
    for c in cells:
        n_tickers[c] = len(by_cell.get(c, {}))

    for ci, c in enumerate(cells):
        tk_mass = by_cell.get(c, {})
        tot = sum(tk_mass.values())
        if tot == 0:
            continue
        for kj, k in enumerate(OFFSETS):
            nbr = c + k
            num = sum(m for tk, m in tk_mass.items() if nbr in visits.get(tk, ()))
            mat[ci, kj] = num / tot
    return cells, mat, total_mass, n_tickers


def build(df: pd.DataFrame, out_html: str, category: str):
    cells, mat, total_mass, n_tickers = grain_mass_overlap(df)

    # hover text with the full stack
    text = [[
        f"cell c={c}  k={OFFSETS[kj]:+d} -> c+k={c+OFFSETS[kj]}<br>"
        f"grain-mass overlap: {mat[ci,kj]*100:.1f}%<br>"
        f"grains at c: {total_mass[c]}  | tickers at c: {n_tickers[c]}"
        if not np.isnan(mat[ci, kj]) else f"cell c={c}  k={OFFSETS[kj]:+d}<br>no grains at c"
        for kj in range(len(OFFSETS))
    ] for ci, c in enumerate(cells)]

    fig = go.Figure(go.Heatmap(
        z=mat * 100.0,
        x=[f"{k:+d}" for k in OFFSETS],
        y=cells,
        colorscale="YlGnBu",
        zmin=0, zmax=100,
        colorbar=dict(title="overlap %"),
        text=text, hoverinfo="text",
        xgap=1, ygap=0,
    ))
    # summary numbers at +-1
    k_pos = {k: OFFSETS.index(k) for k in OFFSETS}
    m1 = np.nanmean([mat[ci, k_pos[1]] for ci in range(len(cells))])
    mm1 = np.nanmean([mat[ci, k_pos[-1]] for ci in range(len(cells))])
    fig.update_layout(
        title=(f"SAND / OVERLAP — grain-mass neighbor recovery ({category}, "
               f"{df.ticker.nunique()} tickers)<br>"
               f"<sub>mean overlap k=+1: {m1*100:.1f}%   k=-1: {mm1*100:.1f}%   "
               f"(c = round(100*yes_bid_close); neighbor-pooling proven legitimate where ~100%)</sub>"),
        xaxis_title="neighbor offset k (cells)",
        yaxis_title="cost-basis cell c (cents)",
        yaxis=dict(autorange="reversed", dtick=5),
        width=720, height=1100, template="plotly_dark",
    )
    fig.write_html(out_html, include_plotlyjs="cdn")
    return {"mean_overlap_k+1": float(m1), "mean_overlap_k-1": float(mm1),
            "n_cells": len(cells), "out": out_html}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=cc.DEFAULT_INPUT)
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "chart_sand_overlap.html"))
    args = ap.parse_args()
    df = cc.load_universe(args.input, args.category)
    summary = build(df, args.out, args.category)
    print("SAND/OVERLAP:", summary)


if __name__ == "__main__":
    main()
