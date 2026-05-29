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
import os
from pathlib import Path

import numpy as np

import exit_chain_core as ec

HERE = Path(__file__).resolve().parent
ARB_ROOT = HERE.parent
# Category-parameterized (default ATP_MAIN). Pass CATEGORY=atp_chall|wta_main|wta_chall.
CAT = os.environ.get("CATEGORY", "atp_main").lower()
_SVM = ARB_ROOT / "data" / "durable" / "spike_volatility_map"
CORPUS = _SVM / f"{CAT}_spike_perN.parquet"
# Canonical hindsight-optimal exit-or-hold map (per-cell, own-N, fill-realistic).
# This is the LOCKED ground truth from <CAT>_LOCKED_DOWN.md / descriptive_1c.
LOCKED = _SVM / f"{CAT}_descriptive_1c.parquet"
OUT_JSON = ARB_ROOT / "data" / "durable" / "exit_atlas_v1" / f"{CAT}_pooled_surface_v3.json"

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


def load_achievable():
    """Read the LOCKED per-cell best-X (achievable / hindsight-optimal) map.

    Each cent c carries the canonical exit-or-hold result: best_exit_X (the X
    that maximizes realized PnL under kiss-the-target hit + hold-to-settle
    fallback), the hit rate at that X, ROI %, and the rule string. These are
    DESCRIPTIVE / hindsight numbers (not predictive) -- the achievable ceiling
    each cell actually printed on the tape, fill-realism applied.
    """
    import pandas as pd
    df = pd.read_parquet(str(LOCKED))
    df["c"] = df["cell_id"].astype(int)
    ach = {}
    for _, r in df.iterrows():
        c = int(r["c"])
        ach[c] = {
            "c": c,
            "N": int(r["N"]),
            "bestX": int(r["best_exit_X"]),
            "bestT": c + int(r["best_exit_X"]),
            "hit": _clean(float(r["hit_rate_at_best"]) * 100.0),
            "roi": _clean(float(r["roi_pct"])),
            "bestSumPerCt": _clean(float(r["best_sum_per_ct_c"])),
            "holdSum": _clean(float(r["hold_to_settle_sum"])),
            "bestSum": _clean(float(r["best_sum"])),
            "reachableXMax": int(r["reachable_X_max"]),
            "rule": str(r["rule"]),
        }
    return ach


def build_pooled_achievable(df):
    """v3 achievable map: per-cent CV-selected POOLED best-X (neighbor-weighted),
    with an own-N contamination fallback. Each cent pools as wide as its own
    leave-one-cent-out CV error supports (wide where cheap, tight in the favorite
    zone), uses its full effective-N rather than the thin own-N count, and falls
    back to its own tape only when neighbors were dragging it negative.

    Carries basis ('pooled' | 'own-N') and the effective sigma per cent so the
    viz can show exactly how wide each cell's feed is. Descriptive / hindsight,
    not predictive.
    """
    sigma_c, err_c = ec.select_per_cent_sigma(df)
    bx = ec.pooled_best_x(df, sigma_c)
    out = {}
    for c, d in bx.items():
        out[int(c)] = {
            "c": int(c),
            "bestX": int(d["bestX"]),
            "bestT": int(d["bestT"]),
            "ev": _clean(d["ev"]),
            "roi": _clean(d["roi"]),
            "hit": _clean(d["hit"]),
            "holdEv": _clean(d["holdEv"]),
            "sigma": _clean(d["sigma"]),
            "basis": d["basis"],
            "rule": d["rule"],
            "cvErr": _clean(err_c.get(int(c))),
        }
    return out


def build():
    df = ec.load_corpus(str(CORPUS))
    achievable = build_pooled_achievable(df)       # v3: pooled best-X (primary)
    achievable_locked = load_achievable()          # own-N locked reference
    base, scores = ec.select_bandwidth_cv(df)
    sigma_c = ec.select_adaptive_sigma(df, base)
    surf = ec.build_surface(df, sigma_c)
    # dual-layered finest config per cell (own-N actual value + eff-N pooled depth)
    sigma_pc, _err_pc = ec.select_per_cent_sigma(df)
    finest = {int(k): v for k, v in ec.finest_config(df, sigma_pc).items()}

    EV, HR, ROI = surf["ev"], surf["hr"], surf["roi"]
    own_n, eff_n = surf["own_n"], surf["eff_n"]
    cents = np.arange(C_MIN, C_MAX + 1)

    # ---- cells: every valid (c, R) up to the ceiling -----------------------
    # CONVERTED basis (oranges -> apples): each per-R cell is scored on the SAME
    # relative-trajectory pooling the achievable read uses, so the inspector's
    # R-by-R table AGREES with the cell color instead of showing the stale
    # absolute-basis numbers. Reach is the neighbor's RELATIVE move (pk - ownc)
    # mapped onto this cell; PnL is priced at THIS cell's own entry cost (carry
    # preserved: +Xc at 94 settles 99/-94, not the same as +Xc at 86).
    cprof = ec._cent_profiles(df)
    cents_arr, peaks, wins, _own_n, ownc = cprof
    cells = []
    for c in cents:
        w = ec._gauss_weights(c, sigma_c[c], cents_arr)
        for R in range(1, ec.R_MAX + 1):
            T = c + R
            if T > 99:
                break
            ev, hr, _ = ec._pooled_ev_hr_at(int(c), int(T), cents_arr, peaks,
                                            wins, w, ownc=ownc, relative=True)
            if ev is None or np.isnan(ev):
                continue
            cells.append({
                "c": int(c),
                "R": int(R),
                "ev": _clean(ev),
                "hit": _clean(hr * 100.0),
                "roi": _clean(ev / c * 100.0),
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

        # Breakeven floor is a forward-math APPROXIMATION (assumes a flat 95%
        # hit). For favorites the real hit is 97-100%, so a profitable exit can
        # genuinely exist BELOW the formula's guess -- and the empirical best-X
        # tick then lands left of the floor line, which reads as a bug. Ground
        # truth wins: clamp the floor so it never sits above ANY profitable
        # best-X that is actually DRAWN/REFERENCED on the surface. Both the
        # achievable tick (the cyan Best-X overlay) AND the finest-config tick
        # are visible reads, so the floor must yield below the LOWER of the two
        # whenever that tick is genuinely profitable. The line means 'below
        # here, no proven profit'; proven profit lower => floor descends to it.
        be_raw = int(ec.breakeven_floor_R(int(c)))
        proven_xs = []
        _a = achievable.get(int(c))          # cyan Best-X tick that is DRAWN
        if _a and _a.get("bestX") is not None and (_a.get("ev") or 0) > 0:
            proven_xs.append(int(_a["bestX"]))
        _fin = finest.get(int(c))            # finest-config tick (eff-N best)
        if _fin and _fin.get("bestX") is not None and _fin.get("effEv", 0) > 0:
            proven_xs.append(int(_fin["bestX"]))
        be_eff = min([be_raw] + proven_xs)

        rows.append({
            "c": int(c),
            "ownN": int(own_n[int(c)]),
            "effN": _clean(eff_n[int(c)]),
            "sigma": _clean(sigma),
            "breakevenFloorR": int(be_eff),
            "breakevenFloorForwardR": be_raw,
            "ceilingMaxR": int(99 - int(c)),
            "complementC": comp,
            "neighbors": contrib,
            "achievable": achievable.get(int(c)),
            "achievableLocked": achievable_locked.get(int(c)),
        })

    ev_vals = [d["ev"] for d in cells if d["ev"] is not None]
    hit_vals = [d["hit"] for d in cells if d["hit"] is not None]
    roi_vals = [d["roi"] for d in cells if d["roi"] is not None]
    ev_abs = max(abs(min(ev_vals)), abs(max(ev_vals)))
    roi_abs = max(abs(min(roi_vals)), abs(max(roi_vals)))

    payload = {
        "meta": {
            "category": CAT.upper(),
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
        "achievable": achievable,
        "achievableLocked": achievable_locked,
        "finest": finest,
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
