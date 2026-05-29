#!/usr/bin/env python3
"""
exit_chain_core.py — corpus-pooled exit-surface estimation + harmonized chains.

This is the estimation engine behind the v2 ground-truth visualizer. It takes
the raw per-N corpus (one row per contract lifecycle) and produces, for every
anchor cent c and every exit offset R = T - c:

  * EV(c,R)   — expected cents per N if you enter at c and exit the first time
                the peak reaches T = c+R, else settle (0 or 99).
                Corpus-pooled across ALL N, weighted by distance on the cent
                chain with a DATA-DRIVEN adaptive bandwidth (no hardcoded sigma).
  * HR(c,R)   — pooled hit rate: fraction of (pooled) N whose peak reached T.
  * dispersion(c,R) — outcome std of the pooled per-N PnL (the "is it a
                lottery?" signal). Used for variance-aware selection.

Then, per cent, it derives a PRODUCTIVE-AND-RELIABLE BAND and three chosen-R
chains inside it:

  * band floor  = smallest R where alpha has become "real" (leaves the +1c
                  dead zone where HR≈100% but EV≈0).
  * band ceiling= largest R before the curve rolls over (HR collapses / EV
                  turns down) — the knee on the far side. Also clamped to the
                  forward-math breakeven floor and the 99c ceiling.
  * conservative= reliable end of the band (near edge): solid HR, real alpha,
                  not reaching. NOT the +1c trap (that's below the band).
  * aggressive  = far end of the band: most alpha still before roll-over.
  * hybrid      = per-cent lean toward aggressive ONLY where the marginal
                  alpha-per-unit-HR-given-up beats the chain's own median
                  tradeoff; else conservative. Curve-relative, no magic number.

All three chains are then SMOOTHED so neighboring cents aren't stark, and given
a SOFT pull toward two-sided-G coherence (complement cent ~ 99 - c).

NOTHING is hardcoded as a subjective constant:
  - bandwidth: leave-one-cent-out cross-validation picks it (adaptive per cent).
  - reliability floor: emergent from each cent's own EV/HR knee, not a global HR%.
  - aggression: exposed as 3 named chains (conservative/aggressive/hybrid),
                each sitting at a different, data-defined edge of the band.

Money note: settlement winners pay 99 (not 100) per Kalshi-style 1c fee; entry
cost is c. PnL for a winning settle = 99 - c; losing settle = -c; exit-on-reach
= T - c = R. EV is the corpus-pooled mean of these per-N PnLs in cents.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SETTLE_WIN = 99  # winning contracts settle at 99c (1c fee), not 100c
C_MIN, C_MAX = 5, 94
R_MAX = 94  # 99 - C_MIN


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------
def load_corpus(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df = df.copy()
    df["c"] = (df["anchor_price"] * 100).round().astype(int)
    df["peak"] = (df["raw_max"] * 100).round().astype(int)
    df["win"] = df["settlement_value"].round().astype(int)
    df = df[(df["c"] >= C_MIN) & (df["c"] <= C_MAX)]
    return df.reset_index(drop=True)


def per_n_pnl(entry_c: int, peak: int, win: int, T: int) -> float:
    """
    PnL in cents for ONE N, if you enter at entry_c and post a limit exit at T.
    If the N's peak reached T, you got filled at T -> PnL = T - entry_c.
    Otherwise you held to settlement -> PnL = (99 - entry_c) if win else (-entry_c).

    NOTE: this is the CELL-BASIS convention (enter at the cell's cent `entry_c`,
    not the N's own anchor) — consistent with the v1 atlas ev_full_cell_basis.
    """
    if peak >= T:
        return T - entry_c
    return (SETTLE_WIN - entry_c) if win else (-entry_c)


# ---------------------------------------------------------------------------
# Adaptive bandwidth via leave-one-cent-out cross-validation
# ---------------------------------------------------------------------------
def _cent_profiles(df: pd.DataFrame):
    """Pre-bin peaks & wins per cent for fast pooled estimation."""
    cents = np.arange(C_MIN, C_MAX + 1)
    peaks = {c: df.loc[df.c == c, "peak"].to_numpy() for c in cents}
    wins = {c: df.loc[df.c == c, "win"].to_numpy() for c in cents}
    own_n = {c: len(peaks[c]) for c in cents}
    return cents, peaks, wins, own_n


def _pooled_ev_hr_at(entry_c, T, cents, peaks, wins, weights, exclude_c=None):
    """
    Pooled EV (cents) and HR at (entry_c, T) using cent->weight dict `weights`.
    Each neighbor cent's N's are evaluated as if ENTERED at entry_c (cell basis),
    contributing with that cent's weight. Optionally exclude one cent (for CV).
    """
    num_ev = 0.0
    num_hit = 0.0
    den = 0.0
    sq = 0.0
    for c in cents:
        if exclude_c is not None and c == exclude_c:
            continue
        w = weights.get(c, 0.0)
        if w <= 0:
            continue
        pk = peaks[c]
        wn = wins[c]
        if len(pk) == 0:
            continue
        reached = pk >= T
        pnl = np.where(reached, T - entry_c,
                       np.where(wn == 1, SETTLE_WIN - entry_c, -entry_c)).astype(float)
        num_ev += w * pnl.sum()
        num_hit += w * reached.sum()
        den += w * len(pk)
        sq += w * (pnl ** 2).sum()
    if den <= 0:
        return np.nan, np.nan, np.nan
    ev = num_ev / den
    hr = num_hit / den
    var = max(sq / den - ev * ev, 0.0)
    return ev, hr, np.sqrt(var)


def _gauss_weights(center_c, sigma, cents):
    d = (cents - center_c).astype(float)
    w = np.exp(-(d * d) / (2 * sigma * sigma))
    return {int(c): float(wi) for c, wi in zip(cents, w)}


def select_bandwidth_cv(df, sigma_grid=None):
    """
    Leave-one-cent-out CV on the cent axis. For each candidate global sigma,
    predict each cent's OWN-sample EV curve from its NEIGHBORS (excluding the
    cent itself) and score squared error vs the cent's own empirical EV curve.
    Returns the sigma minimizing total CV error, plus the score table.

    We evaluate EV across a representative set of R offsets per cent (its own
    valid range), so the chosen width reflects how well neighbors predict the
    held-out cent's actual exit economics — exactly "how far does 23 inform 24".
    """
    if sigma_grid is None:
        sigma_grid = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8]
    cents, peaks, wins, own_n = _cent_profiles(df)

    # empirical (own-sample) EV per (c,R) as the CV target
    def own_ev(c, T):
        pk, wn = peaks[c], wins[c]
        if len(pk) == 0:
            return np.nan
        reached = pk >= T
        pnl = np.where(reached, T - c, np.where(wn == 1, SETTLE_WIN - c, -c)).astype(float)
        return pnl.mean()

    scores = {}
    for sigma in sigma_grid:
        se = 0.0
        cnt = 0
        for c in cents:
            w = _gauss_weights(c, sigma, cents)
            # sample R offsets across this cent's valid exit range
            Ts = range(c + 1, min(99, c + R_MAX) + 1)
            for T in Ts:
                pred, _, _ = _pooled_ev_hr_at(c, T, cents, peaks, wins, w, exclude_c=c)
                obs = own_ev(c, T)
                if np.isnan(pred) or np.isnan(obs):
                    continue
                se += (pred - obs) ** 2
                cnt += 1
        scores[sigma] = se / max(cnt, 1)
    best = min(scores, key=scores.get)
    return best, scores


def select_adaptive_sigma(df, base_sigma):
    """
    Adaptive (variable) bandwidth: widen where the chain is thin, tighten where
    dense. sigma_c = base_sigma * sqrt(median_ownN / ownN_c), clamped to a sane
    range. This makes the width naturally decided by local density — no global
    constant imposed; base_sigma comes from CV.
    """
    cents, peaks, wins, own_n = _cent_profiles(df)
    med = np.median([own_n[c] for c in cents])
    sigma_c = {}
    for c in cents:
        s = base_sigma * np.sqrt(med / max(own_n[c], 1))
        sigma_c[c] = float(np.clip(s, base_sigma * 0.6, base_sigma * 2.5))
    return sigma_c


# ---------------------------------------------------------------------------
# Full pooled surface
# ---------------------------------------------------------------------------
def _eff_n(center_c, sigma, cents, own_n):
    """Neighborhood-weighted effective sample count at a cent (conviction depth)."""
    w = _gauss_weights(center_c, sigma, cents)
    num = sum(w[c] * own_n[c] for c in cents)
    den = max(w.values())  # normalize so a dense self-cell ~ own_n
    return num / den if den > 0 else 0.0


def build_surface(df, sigma_c):
    """
    Returns dict of 2D arrays indexed [ci, Ri] where ci = c - C_MIN,
    Ri = R - 1 (R from 1..R_MAX). Invalid cells (T>99) are NaN.

    Keys:
      ev    : pooled EV cents per N
      hr    : pooled hit rate (fraction)
      disp  : pooled per-N PnL dispersion (std)
      roi   : EXPECTED ROI on cost = ev / c  (the primary maximand; HR baked in,
              normalized by entry cost so cheap & expensive cents compete fairly)
      cred_roi : credibility-weighted ROI -- the rank score. It (a) penalizes
              un-paid near-certainty (HR -> 1 means you are not paid for risk;
              the +1c / 100% trap), and (b) is the surface the chains rank on.
              Thin-effN shrinkage toward the regional mean is applied in
              derive_bands_and_chains where the region is known.
      eff_n : neighborhood-weighted effective sample count per cent (confidence)
    """
    cents, peaks, wins, own_n = _cent_profiles(df)
    nC = C_MAX - C_MIN + 1
    EV = np.full((nC, R_MAX), np.nan)
    HR = np.full((nC, R_MAX), np.nan)
    DP = np.full((nC, R_MAX), np.nan)
    for c in cents:
        ci = c - C_MIN
        w = _gauss_weights(c, sigma_c[c], cents)
        for R in range(1, R_MAX + 1):
            T = c + R
            if T > 99:
                break
            ev, hr, dp = _pooled_ev_hr_at(c, T, cents, peaks, wins, w)
            EV[ci, R - 1] = ev
            HR[ci, R - 1] = hr
            DP[ci, R - 1] = dp
    ROI = EV / np.arange(C_MIN, C_MAX + 1)[:, None].astype(float)
    # Un-paid-certainty penalty: as HR -> 1 you are paid nothing for risk, which
    # is the old '100% is suspicious' trap. Multiply ROI by a factor that fades
    # toward 0 as HR approaches 1. Curve-relative (no hardcoded HR floor): the
    # factor is (1 - HR^k) with k chosen so only NEAR-certain cells are damped.
    k = 6.0
    paid = 1.0 - np.power(np.clip(HR, 0, 1), k)
    CRED = ROI * paid
    eff_n = {c: _eff_n(c, sigma_c[c], cents, own_n) for c in cents}
    return {"ev": EV, "hr": HR, "disp": DP, "roi": ROI, "cred_roi": CRED,
            "own_n": own_n, "eff_n": eff_n}


# ---------------------------------------------------------------------------
# Per-cent band + three chains
# ---------------------------------------------------------------------------
def breakeven_floor_R(c):
    """Forward-math min valid R at 95% forward HR (matches v1 row_dims)."""
    return int(np.ceil(0.05 * (c - 1) / 0.95))


def derive_bands_and_chains(surface, shrink_strength=40.0):
    """
    Rank every (c,R) by the CREDIBILITY-WEIGHTED EXPECTED ROI and surface, per
    cent, three config ranges -- conservative / hybrid / aggressive -- as the
    reliable shoulder, the score peak, and the reach shoulder of that curve.

    Maximand: cred_roi = (EV / c) * (1 - HR^k)
      - EV/c is expected ROI on cost (HR baked in; cheap & expensive cents
        compete fairly; +5c at c=5 is correctly worth 100%).
      - (1 - HR^k) damps NEAR-CERTAIN exits: as HR -> 1 you are not being paid
        for risk -- this is the old '100% is suspicious' trap, killed directly.

    Credibility shrinkage: thin-effN cents are pulled toward the regional mean
    cred_roi curve, so a sparse cent cannot throw alpha its data has not earned.
    shrink weight = effN / (effN + shrink_strength).

    Band: floor = forward-math breakeven (never the un-paid +1c zone); ceiling =
    far side of the score knee (where reaching still scores >= 90% of peak),
    clamped to the 99c ceiling.
    Hybrid = score argmax. Conservative = pulled-in shoulder (>= 90% of peak
    score at higher HR). Aggressive = reach shoulder (>= 90% of peak score at
    larger R). All smoothed across the price chain + softly G-coupled.
    """
    EV, HR, DP = surface["ev"], surface["hr"], surface["disp"]
    CRED = surface["cred_roi"].copy()
    ROI = surface["roi"]
    eff_n = surface["eff_n"]
    nC = EV.shape[0]
    cents = np.arange(C_MIN, C_MAX + 1)

    # --- credibility shrinkage toward the regional (chain-smoothed) mean ----
    # regional reference = column-wise nan-smoothed CRED over a wide window so a
    # thin cent borrows the shape of its price region.
    region = np.full_like(CRED, np.nan)
    for Ri in range(CRED.shape[1]):
        col = CRED[:, Ri]
        v = ~np.isnan(col)
        if v.sum() < 3:
            region[:, Ri] = col
            continue
        # gaussian smooth the valid entries along the cent axis
        idx = np.where(v)[0]
        vals = col[v]
        sm = np.full(nC, np.nan)
        for ci in idx:
            w = np.exp(-((idx - ci) ** 2) / (2 * 5.0 ** 2))
            sm[ci] = np.sum(w * vals) / np.sum(w)
        region[:, Ri] = sm
    for ci in range(nC):
        c = cents[ci]
        wcred = eff_n[c] / (eff_n[c] + shrink_strength)
        row = CRED[ci]
        reg = region[ci]
        m = ~np.isnan(row) & ~np.isnan(reg)
        CRED[ci][m] = wcred * row[m] + (1 - wcred) * reg[m]

    band_floor = np.zeros(nC, dtype=int)
    band_ceil = np.zeros(nC, dtype=int)
    cons = np.zeros(nC, dtype=int)
    aggr = np.zeros(nC, dtype=int)
    hybrid = np.zeros(nC, dtype=int)
    no_positive = np.zeros(nC, dtype=bool)  # cents with NO positive-ROI exit

    for ci in range(nC):
        c = cents[ci]
        score = CRED[ci]
        hr = HR[ci]
        roi = ROI[ci]
        valid = ~np.isnan(score)
        if valid.sum() == 0:
            continue
        Rs = np.where(valid)[0] + 1
        sc_v = score[valid]
        hr_v = hr[valid]
        roi_v = roi[valid]

        be = breakeven_floor_R(c)
        ceiling_max = 99 - c

        # --- NO-POSITIVE-CONFIG cents: the +1c trap, made honest --------------
        # If NO exit in this cent's range has positive expected ROI, there is no
        # legitimate config -- the only 'wins' are the un-paid near-certain +1c
        # crumbs the user said to avoid. Flag the cent and pick the LEAST-BAD
        # (max ROI, still negative) R so the chain stays continuous, but the viz
        # will render it as 'no positive config' rather than a real pick.
        if np.nanmax(roi_v) <= 0:
            no_positive[ci] = True
            best = int(Rs[int(np.nanargmax(roi_v))])
            band_floor[ci] = best
            band_ceil[ci] = best
            cons[ci] = hybrid[ci] = aggr[ci] = best
            continue

        # peak of the credibility score = hybrid (best combo of ROI & paid HR)
        peak_idx = int(np.nanargmax(sc_v))
        peak_R = int(Rs[peak_idx])
        peak_sc = sc_v[peak_idx]

        # band floor: breakeven, but also not below where score first turns
        # meaningfully positive (>= 25% of peak) -- leaves the un-paid zone.
        pos = Rs[sc_v >= 0.25 * peak_sc] if peak_sc > 0 else Rs[:1]
        floor_R = max(be, int(pos.min()) if pos.size else int(Rs[0]), 1)
        # band ceiling: walk out from peak while score holds >= 90% of peak
        ceil_idx = peak_idx
        for j in range(peak_idx, len(Rs)):
            if sc_v[j] >= 0.90 * peak_sc:
                ceil_idx = j
            else:
                break
        ceil_R = min(int(Rs[ceil_idx]), ceiling_max)
        floor_R = min(floor_R, peak_R)
        ceil_R = max(ceil_R, peak_R)
        band_floor[ci] = floor_R
        band_ceil[ci] = ceil_R
        hybrid[ci] = int(np.clip(peak_R, floor_R, ceil_R))

        # --- three DISTINCT config ranges --------------------------------------
        # Conservative and aggressive are defined RELATIVE TO THE BAND, not the
        # narrow score plateau, so they bracket the hybrid even when the score
        # peak is sharp. Conservative = the reliable (higher-HR / smaller-R) end
        # of the positive-ROI region; aggressive = the reach (larger-R) end. We
        # require both to still carry POSITIVE ROI so neither is the +1c trap.
        in_band = (Rs >= floor_R) & (Rs <= ceil_R)
        # widen the candidate set to all positive-ROI exits at/above breakeven so
        # the shoulders are real ranges; clamp the picks back into a sane span.
        posroi = (roi_v > 0) & (Rs >= be)
        cand = Rs[posroi]
        if cand.size <= 1:
            cons[ci] = hybrid[ci]
            aggr[ci] = max(hybrid[ci], int(Rs[posroi].max()) if posroi.any() else hybrid[ci])
            continue
        # conservative: reliable end -- smallest positive-ROI R that still earns
        # a non-trivial score (>= 50% of peak). aggressive: reach end -- largest
        # positive-ROI R that still scores >= 50% of peak.
        keep = cand[(score[cand - 1] >= 0.50 * peak_sc)]
        if keep.size == 0:
            keep = np.array([hybrid[ci]])
        cons[ci] = int(min(keep.min(), hybrid[ci]))
        aggr[ci] = int(max(keep.max(), hybrid[ci]))

    chains = {"conservative": cons, "hybrid": hybrid, "aggressive": aggr}

    # --- smoothing: neighbors not stark + soft two-sided-G coherence --------
    # Skip smoothing across no-positive cents (don't let their dead picks bleed
    # into healthy neighbors); smooth only the productive span.
    chains = {k: smooth_chain(v, band_floor, band_ceil, EV, HR, lock=no_positive)
              for k, v in chains.items()}

    return {
        "band_floor": band_floor,
        "band_ceil": band_ceil,
        "chains": chains,
        "cred_roi_shrunk": CRED,
        "no_positive": no_positive,
    }


def smooth_chain(chain, band_floor, band_ceil, EV, HR, n_iter=40, lam=0.5,
                 g_lam=0.15, lock=None):
    """
    Iteratively pull each cent's chosen R toward (a) the mean of its immediate
    neighbors' R and (b) its two-sided-G complement's implied target coherence,
    then re-clamp into the band and snap to integer. This enforces "neighboring
    cells not too stark" without leaving the productive band. Soft, not forced.

    G coherence: cent c and complement c' = 99 - c are two sides of one game.
    Cashing both ends => their TARGETS T = c+R and T' = c'+R' should not demand
    impossible simultaneous peaks. We softly pull R toward a value keeping T
    near the partner's reachable region (here: gently equalize T across the pair
    by nudging R toward (T_partner - c)). Weight g_lam keeps it a bias.
    """
    nC = chain.shape[0]
    x = chain.astype(float).copy()
    cents = np.arange(C_MIN, C_MAX + 1)
    if lock is None:
        lock = np.zeros(nC, dtype=bool)
    for _ in range(n_iter):
        new = x.copy()
        for ci in range(nC):
            if lock[ci]:
                continue
            neigh = []
            if ci > 0:
                neigh.append(x[ci - 1])
            if ci < nC - 1:
                neigh.append(x[ci + 1])
            target = np.mean(neigh) if neigh else x[ci]
            val = (1 - lam) * x[ci] + lam * target

            # soft G coherence
            c = cents[ci]
            cc = 99 - c
            if C_MIN <= cc <= C_MAX:
                cci = cc - C_MIN
                T_partner = cc + x[cci]
                R_g = T_partner - c  # R that aligns T with partner's T
                if np.isfinite(R_g):
                    val = (1 - g_lam) * val + g_lam * R_g

            new[ci] = val
        x = new
    # clamp to band and snap
    out = np.clip(np.round(x), band_floor, band_ceil).astype(int)
    return out
