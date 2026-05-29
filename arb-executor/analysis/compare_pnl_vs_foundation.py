#!/usr/bin/env python3
"""
Head-to-head: OG Druids Foundation G9 @ T-20 baseline  vs  v3 pooled best-X surface.

Both measured on the SAME 4,137-N ATP_MAIN Foundation corpus (raw_max peak,
size_qual_max_250 IGNORED). PnL convention = per_n_pnl (Kalshi 1c fee: winners
settle 99, losers 0; if peak reaches the posted exit target T you fill at T).

Three strategies, all entering at each N's OWN T-20 anchor cent:

  A) HOLD-TO-SETTLE         : no exit, settle 99/0. The "do nothing" floor.
  B) OG FOUNDATION best-X   : per-cent own-N hindsight-optimal exit (the raw
                              Druids Foundation read -- each cent's own tape
                              argmax, NO neighbor pooling). This is the
                              "ground truth from its own tapes" baseline.
  C) v3 POOLED best-X       : the deployed surface's exit per cent (BETTER of
                              own-raw and neighbor-pooled).

For each N we look up its anchor cent c, read that strategy's chosen exit X(c),
and apply per_n_pnl(c, peak_N, win_N, c+X). We then aggregate corpus-wide.
"""
import json
import numpy as np
import pandas as pd
import exit_chain_core as ec

CORPUS = "../data/durable/spike_volatility_map/atp_main_spike_perN.parquet"
SURFACE = "../data/durable/exit_atlas_v1/atp_main_pooled_surface_v3.json"

df = ec.load_corpus(CORPUS)
N = len(df)
cents = np.arange(ec.C_MIN, ec.C_MAX + 1)

# ---- per-cent own-N hindsight-optimal exit (OG Foundation best-X) -----------
own_bestX = {}
for c in cents:
    sub = df[df.c == c]
    if len(sub) == 0:
        continue
    pk = sub["peak"].to_numpy()
    wn = sub["win"].to_numpy()
    best = None
    for T in range(int(c) + 1, 100):
        pnl = np.where(pk >= T, T - c,
                       np.where(wn == 1, ec.SETTLE_WIN - c, -c)).astype(float)
        ev = pnl.mean()
        if best is None or ev > best[1]:
            best = (T - int(c), float(ev))
    own_bestX[int(c)] = best[0] if best else None

# ---- v3 pooled best-X per cent (from the deployed surface) ------------------
S = json.load(open(SURFACE))
pooled_bestX = {}
for r in S["rows"]:
    a = r.get("achievable") or {}
    if a.get("bestX") is not None and (a.get("ev") or 0) > 0:
        pooled_bestX[int(r["c"])] = int(a["bestX"])
    else:
        pooled_bestX[int(r["c"])] = None  # no profitable exit -> hold


def apply_strategy(get_X):
    """Apply a per-cent exit rule across all N. Returns (total_pnl, total_cost,
    pnl_per_n, roi_pct, win_share_filled)."""
    pnls = np.empty(N)
    costs = df["c"].to_numpy().astype(float)
    cs = df["c"].to_numpy()
    pks = df["peak"].to_numpy()
    wns = df["win"].to_numpy()
    for i in range(N):
        c = int(cs[i])
        X = get_X(c)
        if X is None:                      # hold to settle
            pnls[i] = (ec.SETTLE_WIN - c) if wns[i] == 1 else (-c)
        else:
            T = c + X
            pnls[i] = ec.per_n_pnl(c, int(pks[i]), int(wns[i]), T)
    total = pnls.sum()
    cost = costs.sum()
    return total, cost, total / N, 100.0 * total / cost, pnls


# A) hold-to-settle
a_tot, a_cost, a_ppn, a_roi, a_pnls = apply_strategy(lambda c: None)
# B) OG Foundation own-N best-X
b_tot, b_cost, b_ppn, b_roi, b_pnls = apply_strategy(lambda c: own_bestX.get(c))
# C) v3 pooled best-X
c_tot, c_cost, c_ppn, c_roi, c_pnls = apply_strategy(lambda c: pooled_bestX.get(c))

print(f"Corpus: {N} N (ATP_MAIN T-20 Foundation, raw_max peak)\n")
hdr = f"{'strategy':<28}{'total PnL (c)':>14}{'PnL / N (c)':>14}{'ROI %':>10}{'win N':>8}"
print(hdr); print("-" * len(hdr))
for name, tot, ppn, roi, pnls in [
    ("A) Hold-to-settle", a_tot, a_ppn, a_roi, a_pnls),
    ("B) OG Foundation best-X", b_tot, b_ppn, b_roi, b_pnls),
    ("C) v3 Pooled best-X", c_tot, c_ppn, c_roi, c_pnls),
]:
    print(f"{name:<28}{tot:>14,.0f}{ppn:>14.3f}{roi:>10.2f}{int((pnls>0).sum()):>8}")

print(f"\nDeltas vs OG Foundation (B):")
print(f"  Pooled total PnL : {c_tot - b_tot:+,.0f} c   ({100*(c_tot-b_tot)/abs(b_tot):+.2f}%)")
print(f"  Pooled PnL / N   : {c_ppn - b_ppn:+.3f} c")
print(f"  Pooled ROI       : {c_roi - b_roi:+.2f} pts")

print(f"\nDeltas vs Hold-to-settle (A):")
print(f"  OG Foundation    : {b_tot - a_tot:+,.0f} c PnL  ({b_roi - a_roi:+.2f} ROI pts)")
print(f"  v3 Pooled        : {c_tot - a_tot:+,.0f} c PnL  ({c_roi - a_roi:+.2f} ROI pts)")

# how many cents does pooled change the exit on?
changed = [c for c in cents if pooled_bestX.get(int(c)) != own_bestX.get(int(c))]
print(f"\nCents where pooled exit differs from OG Foundation: {len(changed)}")
print(" ", changed)
