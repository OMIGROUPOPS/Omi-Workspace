#!/usr/bin/env python3
"""
build_pooled_surface.py — neighbor-pooled ground-truth surface for the v2 viz.

This is deliberately simple. It takes the raw per-N corpus and, for EVERY cent c
and EVERY exit R out to that cent's ceiling (T = c+R <= 99), computes the
neighbor-pooled EV, hit-rate, and ROI-on-cost. "Neighbor-pooled" means each
cell borrows N from its neighboring cents with a Gaussian weight (sigma chosen
by leave-one-cent-out CV — sigma=5 for ATP_MAIN), so a cent is no longer judged
off its thin own-N count. The data is one smooth spectrum.

NO optimized pick. NO chains. NO filters. The full surface is emitted, exactly
like v1, plus the per-cell pooling metadata the hover exposes:
  - ownN            : this cent's own sample count
  - effN            : effective sample count after borrowing from neighbors
  - neighbors[]     : {c, ownN, weight, pct} — who feeds this cell and how much
  - complementC     : the two-sided-G partner cent (~99 - c)

Money convention matches v1 / exit_chain_core: enter at the cell's cent c
(cell basis); if the N's peak reached T you exit at T (PnL = T - c); else hold
to settlement (PnL = 99 - c if win, -c if loss). EV is the pooled mean PnL in
cents; ROI = EV / c.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import exit_chain_core as ec

HERE = Path(__file__).resolve().parent
ARB_ROOT = HERE.parent
CORPUS = ARB_ROOT / "data" / "durable" / "spike_volatility_map" / "atp_main_spike_perN.parquet"
OUT_JSON = ARB_ROOT / "data" / "durable" / "exit_atlas_v1" / "atp_main_pooled_surface.json"

C_MIN, C_MAX = ec.C_MIN, ec.C_MAX
SETTLE_WIN = ec.SETTLE_WIN


def _clean(x):
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def build():
    df = ec.load_corpus(str(CORPUS))
    base, scores = ec.select_bandwidth_cv(df)
    sigma_c = ec.select_adaptive_sigma(df, base)
    surf = ec.build_surface(df, sigma_c)

    EV, HR, ROI = surf["ev"], surf["hr"], surf["roi"]
    own_n, eff_n = surf["own_n"], surf["eff_n"]
    cents = np.arange(C_MIN, C_MAX + 1)

    # ---- cells: every valid (c, R) up to the ceiling -----------------------
    cells = []
    for c in cents:
        ci = c - C_MIN
        for R in range(1, ec.R_MAX + 1):
            T = c + R
            if T > 99:
                break
            ev = EV[ci, R - 1]
            if np.isnan(ev):
                continue
            cells.append({
                "c": int(c),
                "R": int(R),
                "ev": _clean(ev),
                "hit": _clean(HR[ci, R - 1] * 100.0),
                "roi": _clean(ROI[ci, R - 1] * 100.0),
            })

    # ---- per-cent pooling metadata -----------------------------------------
    rows = []
    for c in cents:
        sigma = sigma_c[c]
        w = ec._gauss_weights(c, sigma, cents)
        # neighbor breakdown: top contributors by weight*ownN (the real N pulled)
        contrib = []
        for nc in cents:
            wi = w[int(nc)]
            if wi <= 0.01:
                continue
            contrib.append({
                "c": int(nc),
                "ownN": int(own_n[int(nc)]),
                "weight": _clean(wi),
                "mass": _clean(wi * own_n[int(nc)]),  # effective N contributed
            })
        total_mass = sum(x["mass"] for x in contrib) or 1.0
        for x in contrib:
            x["pct"] = _clean(100.0 * x["mass"] / total_mass)
        # keep the meaningful contributors (>= 1% of pooled mass), sorted near->far
        contrib = [x for x in contrib if x["pct"] is not None and x["pct"] >= 1.0]
        contrib.sort(key=lambda x: abs(x["c"] - int(c)))

        comp = 99 - int(c)
        comp = comp if C_MIN <= comp <= C_MAX else None

        rows.append({
            "c": int(c),
            "ownN": int(own_n[int(c)]),
            "effN": _clean(eff_n[int(c)]),
            "sigma": _clean(sigma),
            "breakevenFloorR": int(ec.breakeven_floor_R(int(c))),
            "ceilingMaxR": int(99 - int(c)),
            "complementC": comp,
            "neighbors": contrib,
        })

    ev_vals = [d["ev"] for d in cells if d["ev"] is not None]
    hit_vals = [d["hit"] for d in cells if d["hit"] is not None]
    roi_vals = [d["roi"] for d in cells if d["roi"] is not None]
    ev_abs = max(abs(min(ev_vals)), abs(max(ev_vals)))
    roi_abs = max(abs(min(roi_vals)), abs(max(roi_vals)))

    payload = {
        "meta": {
            "nTotal": int(len(df)),
            "cMin": C_MIN, "cMax": C_MAX, "rMax": int(ec.R_MAX),
            "sigmaBase": _clean(base),
            "evMin": min(ev_vals), "evMax": max(ev_vals), "evAbsMax": ev_abs,
            "hitMin": min(hit_vals), "hitMax": max(hit_vals),
            "roiMin": min(roi_vals), "roiMax": max(roi_vals), "roiAbsMax": roi_abs,
            "validCells": len(cells),
        },
        "cells": cells,
        "rows": rows,
    }
    return payload, scores


def main():
    payload, scores = build()
    OUT_JSON.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    m = payload["meta"]
    print(f"wrote {OUT_JSON}")
    print(f"  corpus N    : {m['nTotal']}")
    print(f"  CV sigma    : {m['sigmaBase']}  (scores: " +
          ", ".join(f"{k}:{v:.2f}" for k, v in sorted(scores.items())) + ")")
    print(f"  valid cells : {m['validCells']}")
    print(f"  EV range    : {m['evMin']:.3f}..{m['evMax']:.3f}  (|max|={m['evAbsMax']:.3f})")
    print(f"  ROI range   : {m['roiMin']:.1f}%..{m['roiMax']:.1f}%")
    print(f"  hit range   : {m['hitMin']:.2f}..{m['hitMax']:.2f}")
    print(f"  size        : {OUT_JSON.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
