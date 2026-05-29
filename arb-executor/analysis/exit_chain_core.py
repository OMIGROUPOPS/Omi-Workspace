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
    """Pre-bin peaks & wins per cent for fast pooled estimation.

    Also pre-bins each tape's OWN anchor cent so pooled scoring can use the
    neighbor's RELATIVE trajectory (move from its own anchor) instead of
    re-pricing the neighbor's absolute outcome at the borrowing cell's basis.
    """
    cents = np.arange(C_MIN, C_MAX + 1)
    peaks = {c: df.loc[df.c == c, "peak"].to_numpy() for c in cents}
    wins = {c: df.loc[df.c == c, "win"].to_numpy() for c in cents}
    # the neighbor's own anchor cent, aligned 1:1 with peaks[c]/wins[c]
    ownc = {c: df.loc[df.c == c, "c"].to_numpy() for c in cents}
    own_n = {c: len(peaks[c]) for c in cents}
    return cents, peaks, wins, own_n, ownc


def _pooled_ev_hr_at(entry_c, T, cents, peaks, wins, weights, exclude_c=None,
                     ownc=None, relative=True):
    """
    Pooled EV (cents) and HR at (entry_c, T) using cent->weight dict `weights`.
    Optionally exclude one cent (for CV).

    RELATIVE basis (default, the fix for top-cell contamination)
    ------------------------------------------------------------
    A neighbor anchored at its own cent `nc` that ran to peak `pk` made a
    RELATIVE move of (pk - nc) cents above its own entry. We borrow that
    *trajectory shape*, not the neighbor's absolute price level. Mapped onto
    the borrowing cell at entry_c, the target X = T - entry_c is "kissed" iff
    the neighbor's relative move (pk - nc) >= X. PnL is then scored at the
    borrowing cell's own basis: kiss -> +X; else settle (win -> 99-entry_c,
    loss -> -entry_c).

    This removes the artifact where a cheap-anchor neighbor's loss was
    re-priced as a full -entry_c (e.g. an 84c loser booked as -88c) and where
    a cheap anchor's huge absolute headroom let it "kiss" high absolute T's it
    never could at the borrowing basis. Strong favorite neighbors (relative
    move to ~99 on their own basis) now correctly support the favorite cell.

    relative=False restores the legacy absolute-basis behavior (kept for the
    EV/ROI exploration lenses, which describe absolute (c,R) outcomes).
    """
    num_ev = 0.0
    num_hit = 0.0
    den = 0.0
    sq = 0.0
    X = T - entry_c
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
        if relative and ownc is not None:
            # relative reach: did this neighbor move at least X above ITS anchor?
            rel_move = pk - ownc[c]
            reached = rel_move >= X
        else:
            reached = pk >= T
        pnl = np.where(reached, X if (relative and ownc is not None) else (T - entry_c),
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
    # sigma -> 0 means OWN-CENT ONLY (the tightest, most basis-faithful pool):
    # the cent uses only the N that actually traded at it, no neighbor borrow.
    if sigma <= 0:
        return {int(c): (1.0 if int(c) == int(center_c) else 0.0) for c in cents}
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
    cents, peaks, wins, own_n, ownc = _cent_profiles(df)

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
                pred, _, _ = _pooled_ev_hr_at(c, T, cents, peaks, wins, w,
                                              exclude_c=c, ownc=ownc, relative=True)
                obs = own_ev(c, T)
                if np.isnan(pred) or np.isnan(obs):
                    continue
                se += (pred - obs) ** 2
                cnt += 1
        scores[sigma] = se / max(cnt, 1)
    best = min(scores, key=scores.get)
    return best, scores


def select_per_cent_sigma(df, sigma_grid=None):
    """
    PER-CENT leave-one-cent-out CV: for each cent c independently, pick the sigma
    that best lets its NEIGHBORS (cent c held out) reproduce c's own empirical EV
    curve. This is the honest, data-driven bandwidth: each cent pools exactly as
    wide as its own data supports.

    Why this matters for the favorite zone: a global sigma (chosen by averaging
    CV error across ALL cents) is dominated by the cheap end, where wide pooling
    helps, and it badly over-smooths the favorites (c>=70). Those high cents,
    when pooled wide, borrow from cheaper cents whose losers are catastrophic
    when re-entered at the favorite's entry cost -- dragging the favorite zone
    spuriously negative. Per-cent CV picks a TIGHT sigma there (typically 0.5-1),
    so favorites use only the cents that genuinely traded near them, and their
    true positive economics survive. Cheap cents keep their wide, data-earned
    pool. No global constant is imposed.

    Returns {c: sigma_c} and {c: cv_error_at_chosen}.
    """
    # NOTE: sigma=0 (own-cent only) is NOT a CV candidate -- with the cent held
    # out it has no neighbors to predict from, so it cannot be CV-scored. Own-N
    # enters instead as an explicit, documented fallback in pooled_best_x: when
    # the CV-pooled best-X is non-positive but the cent's OWN-N best-X is
    # positive, the neighbors were contaminating it and we trust its own tape.
    if sigma_grid is None:
        sigma_grid = [0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 6]
    cents, peaks, wins, own_n, ownc = _cent_profiles(df)

    def own_ev(c, T):
        pk, wn = peaks[c], wins[c]
        if len(pk) == 0:
            return np.nan
        reached = pk >= T
        pnl = np.where(reached, T - c, np.where(wn == 1, SETTLE_WIN - c, -c)).astype(float)
        return pnl.mean()

    sigma_c = {}
    err_c = {}
    for c in cents:
        Ts = range(c + 1, min(99, c + R_MAX) + 1)
        best_s, best_e = None, None
        for sigma in sigma_grid:
            w = _gauss_weights(c, sigma, cents)
            se = 0.0
            cnt = 0
            for T in Ts:
                pred, _, _ = _pooled_ev_hr_at(c, T, cents, peaks, wins, w,
                                              exclude_c=c, ownc=ownc, relative=True)
                obs = own_ev(c, T)
                if np.isnan(pred) or np.isnan(obs):
                    continue
                se += (pred - obs) ** 2
                cnt += 1
            e = se / max(cnt, 1)
            if best_e is None or e < best_e:
                best_e, best_s = e, sigma
        sigma_c[int(c)] = float(best_s)
        err_c[int(c)] = float(best_e)
    return sigma_c, err_c


def pooled_best_x(df, sigma_c):
    """
    Per-cent POOLED best-X (the neighbor-weighted achievable read).

    For each cent c, sweep every reachable absolute target T = c+1..99, compute
    the neighbor-pooled EV at (c, T) using c's own CV-selected sigma, and take
    the X = T-c that maximizes pooled EV (exit-or-hold is already baked into the
    per-N PnL: reach T -> +X, else settle). The pool uses each cent's full
    neighbor-weighted N (effN, often hundreds) rather than the thin own-N count,
    while the basis stays correct (PnL scored at c's own entry cost).

    Returns {c: {bestX, bestT, ev, roi, hit, holdEv, effSupport}} where roi is
    pooled EV / c in percent, hit is the pooled reach fraction at best-X, and
    holdEv is the pooled hold-to-settle EV (the no-exit baseline).
    """
    cents, peaks, wins, own_n, ownc = _cent_profiles(df)
    out = {}
    for c in cents:
        w = _gauss_weights(c, sigma_c[int(c)], cents)
        # hold-to-settle baseline (no exit): pooled mean of (99-c if win else -c)
        hnum = 0.0
        hden = 0.0
        for nc in cents:
            wi = w.get(int(nc), 0.0)
            if wi <= 0:
                continue
            wn = wins[nc]
            if len(wn) == 0:
                continue
            hpnl = np.where(wn == 1, SETTLE_WIN - c, -c).astype(float)
            hnum += wi * hpnl.sum()
            hden += wi * len(wn)
        hold_ev = (hnum / hden) if hden > 0 else np.nan

        best = None  # (X, ev, hit, T)
        for T in range(c + 1, 100):
            # CONVERTED basis: translate each neighbor's RELATIVE trajectory onto
            # this cell (oranges -> apples) before measuring reach, instead of
            # pricing a cheap-anchor neighbor's absolute peak at this cell's cost.
            ev, hr, _ = _pooled_ev_hr_at(c, T, cents, peaks, wins, w,
                                         ownc=ownc, relative=True)
            if ev is None or np.isnan(ev):
                continue
            if best is None or ev > best[1]:
                best = (T - c, float(ev), float(hr), T)
        if best is None:
            continue
        X, ev, hit, T = best
        basis = "pooled"
        eff_sigma = float(sigma_c[int(c)])

        # --- Foundation-true own-N read (the fix for top-cell false negatives) -
        # The locked descriptive_1c map carried false negatives at several top
        # cells (77, 80, 81, 93) where its rule was NOT the true argmax of the
        # raw Foundation tapes. So we ALWAYS recompute this cent's best exit
        # directly from its own raw T-20 tapes (Druids Foundation), and take the
        # BETTER of pooled-vs-raw. Neighbor pooling may only ENRICH a thin cell
        # upward -- it can never drag a Foundation-positive cell into the red.
        # This is the operator's directive: rely on neighbor N to help configure
        # cells to their best exit, never to invent a false negative.
        pk_o, wn_o = peaks[int(c)], wins[int(c)]
        if len(pk_o) > 0:
            obest = None
            for To in range(c + 1, 100):
                reached = pk_o >= To
                pnl = np.where(reached, To - c,
                               np.where(wn_o == 1, SETTLE_WIN - c, -c)).astype(float)
                evo = float(pnl.mean())
                if obest is None or evo > obest[1]:
                    obest = (To - c, evo, float(reached.mean()), To)
            # Use the raw own-N read whenever it beats the pooled read. Pooling
            # only wins when it genuinely lifts a thin cell ABOVE its own tape.
            if obest is not None and obest[1] > ev:
                X, ev, hit, T = obest
                basis = "own-N"
                eff_sigma = 0.0

        # if holding beats every exit, the rule is hold-to-settle
        rule = f"exit at +{X}c"
        if not np.isnan(hold_ev) and hold_ev >= ev:
            ev = float(hold_ev)
            X = 99 - c
            T = 99
            hit = float('nan')
            rule = "hold to 99c on winners, 1c on losers"
        out[int(c)] = {
            "c": int(c),
            "bestX": int(X),
            "bestT": int(T),
            "ev": float(ev),
            "roi": float(ev / c * 100.0),
            "hit": (None if (hit is None or np.isnan(hit)) else float(hit * 100.0)),
            "holdEv": (None if np.isnan(hold_ev) else float(hold_ev)),
            "sigma": eff_sigma,
            "basis": basis,
            "rule": rule,
        }
    return out


def finest_config(df, sigma_c):
    """
    DUAL-LAYERED finest config per cell -- the operator's single best exit X.

    Two layers are measured INDEPENDENTLY for every cell, then reconciled:

      Layer A -- OWN-N (actual cell value): the cell's own raw T-20 Foundation
        tape. What it literally printed. Truth, but thin conviction.
      Layer B -- EFF-N (pooled depth): the converted-basis neighbor-weighted
        read (oranges->apples relative trajectory). Deep/confident, but borrowed.

    Why both: own-N alone is too thin to trust a single X; eff-N alone is
    borrowed and can drift off the cell's true character. The finest config is
    only CONFIDENT when both layers point the same direction.

    Selection score (NOT raw EV, NOT pure stability -- both extremes are wrong):
      score(X) = EV_X / (dispersion_X + EPS)  *  (1 - hit_X**k)
      - EV/dispersion is risk-adjusted edge (Sharpe-like): rewards the STABILITY
        the favorite zone earns -- tight, near-certain outcomes score high even
        at small EV; wide-dispersion lottery exits must earn real EV to win.
      - (1 - hit**k) damps the un-paid +1c near-certainty trap (a 100%-hit +1c
        crumb has tiny dispersion but you're paid nothing for risk -> killed).
      EV itself must be > 0 to be eligible (no 'least-bad negative' configs).

    The X is chosen on the EFF-N score (depth), but the OWN-N layer is scored at
    that same X and reported alongside. confidence:
      'confident' -- own-N EV and eff-N EV both > 0 at the chosen X (agree)
      'thin'      -- eff-N positive but own-N flat/negative (borrowed, unproven)
      'own-only'  -- own-N positive but eff-N couldn't support it (rare; trust tape)
    Returns {c: {...both layers..., confidence}}.
    """
    cents, peaks, wins, own_n, ownc = _cent_profiles(df)
    EPS = 1.0  # cents; dispersion floor so a zero-noise crumb can't divide to inf
    K = 6.0
    out = {}
    for c in cents:
        c = int(c)
        w = _gauss_weights(c, sigma_c[c], cents)
        pk_o, wn_o = peaks[c], wins[c]

        def own_at(T):
            if len(pk_o) == 0:
                return np.nan, np.nan, np.nan
            reached = pk_o >= T
            pnl = np.where(reached, T - c,
                           np.where(wn_o == 1, SETTLE_WIN - c, -c)).astype(float)
            ev = float(pnl.mean())
            hr = float(reached.mean())
            disp = float(pnl.std())
            return ev, hr, disp

        best = None  # (score, X, T, evB, hrB, dispB, evA, hrA, dispA)
        for T in range(c + 1, 100):
            evB, hrB, dispB = _pooled_ev_hr_at(c, T, cents, peaks, wins, w,
                                               ownc=ownc, relative=True)
            if evB is None or np.isnan(evB) or evB <= 0:
                continue
            score = (evB / (dispB + EPS)) * (1.0 - hrB ** K)
            if best is None or score > best[0]:
                evA, hrA, dispA = own_at(T)
                best = (score, T - c, T, evB, hrB, dispB, evA, hrA, dispA)
        if best is None:
            continue
        _, X, T, evB, hrB, dispB, evA, hrA, dispA = best

        if not np.isnan(evA) and evA > 0 and evB > 0:
            confidence = "confident"
        elif evB > 0 and (np.isnan(evA) or evA <= 0):
            confidence = "thin"
        else:
            confidence = "own-only"

        out[c] = {
            "c": c,
            "bestX": int(X),
            "bestT": int(T),
            # eff-N pooled depth layer (the selection layer)
            "effEv": float(evB),
            "effRoi": float(evB / c * 100.0),
            "effHit": float(hrB * 100.0),
            "effDisp": float(dispB),
            "effSharpe": float(evB / (dispB + EPS)),
            # own-N actual-value layer (the truth layer)
            "ownEv": (None if np.isnan(evA) else float(evA)),
            "ownRoi": (None if np.isnan(evA) else float(evA / c * 100.0)),
            "ownHit": (None if np.isnan(hrA) else float(hrA * 100.0)),
            "ownDisp": (None if np.isnan(dispA) else float(dispA)),
            "ownN": int(own_n[c]),
            "sigma": float(sigma_c[c]),
            "confidence": confidence,
            "rule": f"exit at +{int(X)}c (T={int(T)}c)",
        }
    return out


def select_adaptive_sigma(df, base_sigma):
    """
    Adaptive (variable) bandwidth: widen where the chain is thin, tighten where
    dense. sigma_c = base_sigma * sqrt(median_ownN / ownN_c), clamped to a sane
    range. This makes the width naturally decided by local density — no global
    constant imposed; base_sigma comes from CV.
    """
    cents, peaks, wins, own_n, ownc = _cent_profiles(df)
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
    cents, peaks, wins, own_n, ownc = _cent_profiles(df)
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
