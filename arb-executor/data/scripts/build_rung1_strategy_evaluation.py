"""
Rung 1 producer: per-cell optimized-exit-target strategy evaluation.

Spec: docs/rung1_strategy_evaluation_spec.md v0.3.2 (commit 3bbac375).
Input: data/durable/rung0_cell_economics/cell_economics.parquet
       (sha256 6fdd019d..., commit 5ca2d89c).

v0.3.2 two-artifact continuous design (the v0.1 8-point grid is superseded
per spec v0.2/v0.3/v0.3.1; the cell is the fixed T-20m entry, the EXIT axis
is continuous 1..98c):

  Artifact A -- strategy_evaluation_curve.parquet (28 cols, keyed
    (cell_key, exit_line_cents)); the dense per-cell exit curve =
    72 x 98 = 7,056 rows at full corpus. The evidence.

  Artifact B -- strategy_evaluation_optimum.parquet (32 cols, keyed
    cell_key); 72 rows; the per-cell data-derived optimal exit line
    separately for cents / ROI / Sharpe per A39, each with that line's
    metrics/CIs + a deterministic curve_shape_note. A PURE deterministic
    read of Artifact A (no new bootstrap) -- consistency-gated (gate 7).

Statistics are real (v0.1's three stubs removed): closed-form Wilson score
intervals for proportions; BCa bootstrap (n=1000, jackknife acceleration,
percentile fallback with a tracked fallback rate) for mean_realized_cents /
mean_realized_roi_pct; ratio-direct BCa for Sharpe-like / Sortino-like per
spec Section 4. std / median are emitted as point estimates on the dense
curve (spec Section 3.2 Artifact A note -- CI only on the decision-load-
bearing metrics to keep 7,056 x 1000 tractable).

C37 discipline: write BOTH .new parquets, reload BOTH from disk, run the 7
hard gates (Section 6.1) plus gate 8 soft against the on-disk bytes
(gate 7 cross-checks Artifact B against the reloaded Artifact A),
os.replace BOTH only on all-7-hard-pass; else halt with both .new
preserved and a halt log.

Usage:
    python build_rung1_strategy_evaluation.py [--input PATH] [--output-dir PATH] [--phase {1,2,3}]

Phases (mirrors Rung 0 producer rollout discipline):
    Phase 1: one cell x all 98 exit lines. Visual inspection. <60s.
    Phase 2: <=10 cells stratified by category x all 98 exit lines.
    Phase 3: full 72 cells x 98 exit lines = 7,056 Artifact-A rows
             (App/VPS job; 15-45 min single-threaded per spec Section 7.3).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# pandas 3.0 + pyarrow 24 compat patch
# ---------------------------------------------------------------------------
# pyarrow.pandas_compat.make_datetimetz calls pa.lib.string_to_tzinfo() which
# returns a pytz.tzfile object. pandas 3.0's DatetimeTZDtype constructor calls
# timezones.tz_standardize() which no longer accepts pytz objects directly,
# raising AttributeError("'NoneType' object has no attribute 'timezone'").
# We patch make_datetimetz to pass the tz STRING straight to DatetimeTZDtype,
# which pandas 3.0 accepts cleanly. Same fix as Rung 0 producer commit 52edf132.
def _install_pandas3_pyarrow_compat_patch():
    try:
        import pyarrow.pandas_compat as _papc
        from pandas.core.dtypes.dtypes import DatetimeTZDtype as _DTZD
        def _patched_make_datetimetz(unit, tz):
            return _DTZD(unit=unit, tz=tz)
        _papc.make_datetimetz = _patched_make_datetimetz
    except Exception:
        pass

_install_pandas3_pyarrow_compat_patch()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ET = ZoneInfo("America/New_York")

DEFAULT_INPUT = Path("data/durable/rung0_cell_economics/cell_economics.parquet")
DEFAULT_OUTPUT_DIR = Path("data/durable/rung1_strategy_evaluation")
CURVE_FILE = "strategy_evaluation_curve.parquet"      # Artifact A
OPTIMUM_FILE = "strategy_evaluation_optimum.parquet"  # Artifact B
DEFAULT_REPORT_FILE = "validation_report.md"
DEFAULT_META_FILE = "strategy_evaluation.meta.json"
DEFAULT_LOG_DIR = Path("data/durable/rung1_strategy_evaluation/logs")

# Continuous exit-line axis: 1..98c at 1c step, per spec Section 2.2 / 3.2.
# (The v0.1 locked 8-point grid is superseded -- A39/E32(e).)
EXIT_LINES_CENTS = list(range(1, 99))  # 1..98

N_RESAMPLES = 1000     # spec Section 4: row-level bootstrap n=1000
BOOTSTRAP_BASE_SEED = 20260519  # deterministic; per-(cell,line,metric) offset

# Artifact A schema -- 28 cols, EXACT order per spec Section 3.2 table.
ARTIFACT_A_COLUMNS = [
    "cell_key",
    "category",
    "price_band",
    "exit_line_cents",
    "threshold_hit_rate",
    "threshold_hit_rate_ci_lower",
    "threshold_hit_rate_ci_upper",
    "mean_realized_cents",
    "mean_realized_cents_ci_lower",
    "mean_realized_cents_ci_upper",
    "mean_realized_roi_pct",
    "mean_realized_roi_pct_ci_lower",
    "mean_realized_roi_pct_ci_upper",
    "median_realized_cents",
    "median_realized_roi_pct",
    "std_realized_cents",
    "std_realized_roi_pct",
    "downside_std_realized_cents",
    "sharpe_like_roi",
    "sortino_like_roi",
    "observations_n",
    "unique_match_count",
    "low_n_flag",
    "weak_ci_flag",
    "b13_ceiling_bind_flag",
    "mean_entry_price_cents",
    "daily_opportunity_rate",
    "expected_cents_per_dollar_capital_day",
]

# Artifact B schema -- 32 cols, EXACT order per spec Section 3.2 table.
ARTIFACT_B_COLUMNS = [
    "cell_key",
    "category",
    "price_band",
    "observations_n",
    "unique_match_count",
    "low_n_flag",
    "mean_entry_price_cents",
    "daily_opportunity_rate",
    "opt_cents_exit_line",
    "opt_cents_mean_realized_cents",
    "opt_cents_mean_realized_cents_ci_lower",
    "opt_cents_mean_realized_cents_ci_upper",
    "opt_cents_hit_rate",
    "opt_cents_hit_rate_ci_lower",
    "opt_cents_hit_rate_ci_upper",
    "opt_cents_mean_realized_roi_pct",
    "opt_cents_weak_ci_flag",
    "opt_roi_exit_line",
    "opt_roi_mean_realized_roi_pct",
    "opt_roi_mean_realized_roi_pct_ci_lower",
    "opt_roi_mean_realized_roi_pct_ci_upper",
    "opt_roi_hit_rate",
    "opt_roi_hit_rate_ci_lower",
    "opt_roi_hit_rate_ci_upper",
    "opt_roi_mean_realized_cents",
    "opt_roi_weak_ci_flag",
    "opt_sharpe_exit_line",
    "opt_sharpe_value",
    "opt_sharpe_mean_realized_roi_pct",
    "curve_shape_note",
    "opt_cents_expected_cents_per_dollar_capital_day",
    "opt_roi_expected_cents_per_dollar_capital_day",
]

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %Z",
)
log = logging.getLogger("rung1_producer")

# Force ET on log timestamps per G21.
os.environ["TZ"] = "America/New_York"

# Module-level bootstrap fallback tracking (spec Section 6.2 informative:
# >5% percentile fallback -> flag in validation_report).
_BOOT_STATS = {"calls": 0, "fallbacks": 0}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class GateResult:
    name: str
    passed: bool
    n_violations: int
    detail: str = ""


@dataclass
class ProducerResult:
    artifact_a_rows: int
    artifact_b_rows: int
    cells_covered: int
    exit_lines_covered: int
    gate_results: list[GateResult] = field(default_factory=list)
    curve_sha256: Optional[str] = None
    optimum_sha256: Optional[str] = None
    curve_bytes: Optional[int] = None
    optimum_bytes: Optional[int] = None
    run_started_at_et: Optional[str] = None
    run_completed_at_et: Optional[str] = None
    input_sha256: Optional[str] = None
    producer_commit: Optional[str] = None
    bootstrap_fallback_rate: float = 0.0


# ---------------------------------------------------------------------------
# Per-row realized derivation (spec Section 2.3) -- REUSED verbatim from the
# v0.1 skeleton; already continuous in the exit line (the >= test is the
# load-bearing primitive). Only the parameter is generalized from a locked
# threshold to a continuous exit line; the math is byte-identical.
# ---------------------------------------------------------------------------


def compute_per_row_realized(rung0: pd.DataFrame, exit_line_cents: int) -> pd.DataFrame:
    """
    Per spec Section 2.3 (continuous in the exit line L by construction):
      peak_bounce_cents = peak_bid_bounce_pre_resolution * 100
      entry_price_cents = t20m_trade_price * 100
      realized_at_settlement_cents = realized_at_settlement * 100  (signed)

      hit = peak_bounce_cents >= L
      if hit:  realized_cents = L
      else:    realized_cents = realized_at_settlement_cents  (E32 no-stop)

      realized_roi = realized_cents / entry_price_cents  (cents/cents)
      realized_roi_pct = realized_roi * 100

    Returns a copy of rung0 augmented with: hit, realized_cents,
    realized_roi_pct, entry_price_cents.
    """
    out = rung0.copy()
    peak_bounce_cents = out["peak_bid_bounce_pre_resolution"] * 100.0
    entry_price_cents = out["t20m_trade_price"] * 100.0
    realized_at_settlement_cents = out["realized_at_settlement"] * 100.0

    hit = peak_bounce_cents >= float(exit_line_cents)
    realized_cents = np.where(hit, float(exit_line_cents), realized_at_settlement_cents)
    # Guard: avoid divide-by-zero on the unlikely entry_price=0 edge.
    # Under spec the band-exclusion gate guarantees entry_price >= 0.05 dollars
    # (5c band lower bound), so entry_price_cents >= 5. Defensive code kept.
    realized_roi_pct = np.where(
        entry_price_cents > 0,
        100.0 * realized_cents / entry_price_cents,
        np.nan,
    )

    out["hit"] = hit.astype(bool)
    out["realized_cents"] = realized_cents
    out["realized_roi_pct"] = realized_roi_pct
    out["entry_price_cents"] = entry_price_cents
    return out


# ---------------------------------------------------------------------------
# Real statistics (spec Section 4) -- the v0.1 stubs are removed.
# ---------------------------------------------------------------------------

try:
    from scipy.stats import norm as _scipy_norm  # type: ignore
    _HAVE_SCIPY = True
except Exception:
    _scipy_norm = None
    _HAVE_SCIPY = False


def _norm_cdf(x: float) -> float:
    if _HAVE_SCIPY:
        return float(_scipy_norm.cdf(x))
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    """Inverse standard-normal CDF. scipy if present, else Acklam's algorithm."""
    if _HAVE_SCIPY:
        return float(_scipy_norm.ppf(p))
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return math.inf
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow = 0.02425
    phigh = 1.0 - plow
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5]) * q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
            ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)


def wilson_ci(successes: int, n: int, z: float = 1.959963984540054):
    """Closed-form Wilson score interval for a binomial proportion (95%).

    Proportions get Wilson, not bootstrap (spec Section 4). n==0 -> (0,0).
    """
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def _statistic(values: np.ndarray, kind: str) -> float:
    if kind == "mean":
        return float(np.mean(values))
    if kind == "median":
        return float(np.median(values))
    if kind == "std":
        return float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    if kind == "downside_std":
        neg = values[values < 0]
        return float(np.std(neg, ddof=1)) if len(neg) > 1 else 0.0
    raise ValueError(f"unknown statistic: {kind}")


def _boot_stat(samples: np.ndarray, kind: str) -> np.ndarray:
    """Vectorized statistic over a (R, n) resample matrix -> (R,) array."""
    if kind == "mean":
        return samples.mean(axis=1)
    if kind == "median":
        return np.median(samples, axis=1)
    if kind == "std":
        return samples.std(axis=1, ddof=1)
    if kind == "downside_std":
        mask = samples < 0
        k = mask.sum(axis=1).astype(float)
        s = np.where(mask, samples, 0.0).sum(axis=1)
        ss = np.where(mask, samples * samples, 0.0).sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            var = (ss - (s * s) / np.where(k > 0, k, np.nan)) / np.where(k > 1, k - 1.0, np.nan)
        out = np.sqrt(np.where(var > 0, var, np.nan))
        return out
    raise ValueError(f"unknown statistic: {kind}")


def _jackknife(values: np.ndarray, kind: str) -> np.ndarray:
    """Closed-form leave-one-out statistic, O(n), for BCa acceleration."""
    n = len(values)
    v = values.astype(float)
    if kind == "mean":
        S = v.sum()
        return (S - v) / (n - 1)
    if kind == "median":
        # O(n log n) leave-one-out medians -- only used if a non-mean stat is
        # ever bootstrapped; the Artifact-A hot path is 'mean'.
        out = np.empty(n)
        order = np.argsort(v)
        for i in range(n):
            out[i] = np.median(np.delete(v, i))
        return out
    if kind == "std":
        if n < 3:
            return np.full(n, np.nan)
        S = v.sum()
        SS = (v * v).sum()
        m_i = (S - v) / (n - 1)
        var_i = (SS - v * v - (n - 1) * m_i * m_i) / (n - 2)
        return np.sqrt(np.where(var_i > 0, var_i, 0.0))
    if kind == "downside_std":
        neg_mask = v < 0
        neg = v[neg_mask]
        k = len(neg)
        full = float(np.std(neg, ddof=1)) if k > 1 else np.nan
        out = np.full(n, full, dtype=float)  # leaving out a non-negative: unchanged
        if k >= 3:
            Sn = neg.sum()
            SSn = (neg * neg).sum()
            idx = np.where(neg_mask)[0]
            ki = k - 1
            mneg_i = (Sn - v[idx]) / ki
            var_i = (SSn - v[idx] * v[idx] - ki * mneg_i * mneg_i) / (ki - 1)
            out[idx] = np.sqrt(np.where(var_i > 0, var_i, 0.0))
        else:
            out[neg_mask] = np.nan
        return out
    raise ValueError(f"unknown statistic: {kind}")


def _bca_from_boot(boot: np.ndarray, point: float, jack: np.ndarray):
    """Shared BCa core: returns (lo, hi, used_fallback)."""
    boot = boot[np.isfinite(boot)]
    if len(boot) < 2:
        return (point, point, True)
    prop = float(np.mean(boot < point))
    eps = 1.0 / (len(boot) + 1.0)
    if prop <= 0.0 or prop >= 1.0:
        prop = min(max(prop, eps), 1.0 - eps)
    z0 = _norm_ppf(prop)
    jack = jack[np.isfinite(jack)]
    if len(jack) < 2:
        lo, hi = np.quantile(boot, [0.025, 0.975])
        return (float(lo), float(hi), True)
    jbar = jack.mean()
    num = np.sum((jbar - jack) ** 3)
    den = 6.0 * (np.sum((jbar - jack) ** 2) ** 1.5)
    if den == 0.0 or not np.isfinite(num) or not np.isfinite(den):
        lo, hi = np.quantile(boot, [0.025, 0.975])
        return (float(lo), float(hi), True)
    a = num / den
    z_lo = _norm_ppf(0.025)
    z_hi = _norm_ppf(0.975)
    if not (np.isfinite(z0) and np.isfinite(a)):
        lo, hi = np.quantile(boot, [0.025, 0.975])
        return (float(lo), float(hi), True)
    a1 = _norm_cdf(z0 + (z0 + z_lo) / (1.0 - a * (z0 + z_lo)))
    a2 = _norm_cdf(z0 + (z0 + z_hi) / (1.0 - a * (z0 + z_hi)))
    if not (np.isfinite(a1) and np.isfinite(a2)) or not (0.0 < a1 < 1.0) or not (0.0 < a2 < 1.0):
        lo, hi = np.quantile(boot, [0.025, 0.975])
        return (float(lo), float(hi), True)
    lo = float(np.quantile(boot, min(a1, a2)))
    hi = float(np.quantile(boot, max(a1, a2)))
    return (lo, hi, False)


def bca_bootstrap(values: np.ndarray, statistic: str,
                  n_resamples: int = N_RESAMPLES, seed: Optional[int] = None):
    """BCa bootstrap with percentile fallback. Returns (point, lo, hi).

    statistic in {'mean','median','std','downside_std'}. Degenerate samples
    (len<2, or downside_std with <2 negatives) -> (point, point, point).
    """
    _BOOT_STATS["calls"] += 1
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    n = len(values)
    if n == 0:
        return (0.0, 0.0, 0.0)
    point = _statistic(values, statistic)
    if n < 2:
        return (point, point, point)
    if statistic == "downside_std" and int((values < 0).sum()) < 2:
        return (point, point, point)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_resamples, n))
    samples = values[idx]
    boot = _boot_stat(samples, statistic)
    jack = _jackknife(values, statistic)
    lo, hi, used_fallback = _bca_from_boot(boot, point, jack)
    if used_fallback:
        _BOOT_STATS["fallbacks"] += 1
    return (point, lo, hi)


def _ratio_point(values: np.ndarray, kind: str):
    m = float(np.mean(values))
    if kind == "sharpe":
        sd = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    elif kind == "sortino":
        neg = values[values < 0]
        sd = float(np.std(neg, ddof=1)) if len(neg) > 1 else 0.0
    else:
        raise ValueError(f"unknown ratio kind: {kind}")
    if sd == 0.0 or not np.isfinite(sd):
        return None
    return m / sd


def _ratio_jackknife(values: np.ndarray, kind: str) -> np.ndarray:
    n = len(values)
    v = values.astype(float)
    S = v.sum()
    m_i = (S - v) / (n - 1)
    if kind == "sharpe":
        sd_i = _jackknife(v, "std")
    else:
        sd_i = _jackknife(v, "downside_std")
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.where((sd_i > 0) & np.isfinite(sd_i), m_i / sd_i, np.nan)
    return r


def ratio_bca_bootstrap(values: np.ndarray, kind: str,
                        n_resamples: int = N_RESAMPLES, seed: Optional[int] = None):
    """Ratio-direct BCa for Sharpe-like / Sortino-like (spec Section 4: the
    ratio is recomputed per resample, NOT numerator/denominator separately).

    Degenerate denominator on the full sample -> (None, None, None).
    Returns (point|None, lo|None, hi|None).
    """
    _BOOT_STATS["calls"] += 1
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    n = len(values)
    if n < 2:
        return (None, None, None)
    point = _ratio_point(values, kind)
    if point is None:
        return (None, None, None)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_resamples, n))
    samples = values[idx]
    m = samples.mean(axis=1)
    if kind == "sharpe":
        sd = samples.std(axis=1, ddof=1)
    else:
        sd = _boot_stat(samples, "downside_std")
    with np.errstate(invalid="ignore", divide="ignore"):
        boot = np.where((sd > 0) & np.isfinite(sd), m / sd, np.nan)
    jack = _ratio_jackknife(values, kind)
    lo, hi, used_fallback = _bca_from_boot(boot, point, jack)
    if used_fallback:
        _BOOT_STATS["fallbacks"] += 1
    return (point, lo, hi)


# ---------------------------------------------------------------------------
# Artifact A -- the dense per-(cell, exit_line) curve (spec Section 3.2)
# ---------------------------------------------------------------------------


def build_artifact_a(rung0: pd.DataFrame, corpus_active_days: int) -> pd.DataFrame:
    """For each cell, for each exit line in 1..98c, compute the Section 3.1
    metrics. Cell-level quantities computed once per cell; CIs only on the
    decision-load-bearing metrics (spec Section 3.2 Artifact A note)."""
    log.info(f"Artifact A: {rung0['cell_key'].nunique()} cells x "
             f"{len(EXIT_LINES_CENTS)} exit lines")
    rows = []
    cell_idx = 0
    for cell_key, group in rung0.groupby("cell_key", sort=True):
        category = group["category"].iloc[0]
        price_band = group["price_band"].iloc[0]
        n = len(group)
        observations_n = n
        unique_match_count = int(group["event_ticker"].nunique())
        low_n_flag = bool(n < 30)
        mean_entry_cents = float(group["t20m_trade_price"].mean() * 100.0) if n > 0 else 0.0
        daily_opp_rate = n / corpus_active_days if corpus_active_days > 0 else 0.0

        for li, exit_line in enumerate(EXIT_LINES_CENTS):
            aug = compute_per_row_realized(group, exit_line)
            successes = int(aug["hit"].sum())
            rc = aug["realized_cents"].to_numpy()
            roi = aug["realized_roi_pct"].to_numpy()
            roi = roi[np.isfinite(roi)]

            hit_rate = successes / n if n > 0 else 0.0
            hr_lo, hr_hi = wilson_ci(successes, n)

            seed_base = BOOTSTRAP_BASE_SEED + cell_idx * 100000 + exit_line * 10
            mean_cents, mc_lo, mc_hi = bca_bootstrap(rc, "mean", seed=seed_base + 1)
            mean_roi, mr_lo, mr_hi = bca_bootstrap(roi, "mean", seed=seed_base + 2)

            median_cents = float(np.median(rc)) if len(rc) else 0.0
            median_roi = float(np.median(roi)) if len(roi) else 0.0
            std_cents = float(np.std(rc, ddof=1)) if len(rc) > 1 else 0.0
            std_roi = float(np.std(roi, ddof=1)) if len(roi) > 1 else 0.0
            neg_cents = rc[rc < 0]
            downside_std_cents = float(np.std(neg_cents, ddof=1)) if len(neg_cents) > 1 else 0.0
            n_neg_cents = int((rc < 0).sum())

            sharpe_pt, _sh_lo, _sh_hi = ratio_bca_bootstrap(roi, "sharpe", seed=seed_base + 3)
            sortino_pt, _so_lo, _so_hi = ratio_bca_bootstrap(roi, "sortino", seed=seed_base + 4)

            b13 = bool(exit_line >= (99.0 - mean_entry_cents - 1.0))

            # weak_ci_flag (spec Section 3.1 metric 14): mean_roi BCa CI
            # crosses zero OR hit_rate Wilson CI width > 0.20 OR low_n_flag;
            # plus metric 8: <2 negatives -> downside_std=0 flagged weak.
            roi_ci_crosses_zero = (mr_lo is not None and mr_hi is not None
                                   and mr_lo < 0.0 < mr_hi)
            hit_rate_ci_wide = (hr_hi - hr_lo) > 0.20
            downside_degenerate = n_neg_cents < 2
            weak_ci_flag = bool(low_n_flag or roi_ci_crosses_zero
                                or hit_rate_ci_wide or downside_degenerate)

            if mean_entry_cents > 0:
                expected_cpd = (mean_cents * daily_opp_rate) / mean_entry_cents
            else:
                expected_cpd = 0.0

            rows.append({
                "cell_key": cell_key,
                "category": category,
                "price_band": price_band,
                "exit_line_cents": np.int16(exit_line),
                "threshold_hit_rate": hit_rate,
                "threshold_hit_rate_ci_lower": hr_lo,
                "threshold_hit_rate_ci_upper": hr_hi,
                "mean_realized_cents": mean_cents,
                "mean_realized_cents_ci_lower": mc_lo,
                "mean_realized_cents_ci_upper": mc_hi,
                "mean_realized_roi_pct": mean_roi,
                "mean_realized_roi_pct_ci_lower": mr_lo,
                "mean_realized_roi_pct_ci_upper": mr_hi,
                "median_realized_cents": median_cents,
                "median_realized_roi_pct": median_roi,
                "std_realized_cents": std_cents,
                "std_realized_roi_pct": std_roi,
                "downside_std_realized_cents": downside_std_cents,
                "sharpe_like_roi": sharpe_pt,
                "sortino_like_roi": sortino_pt,
                "observations_n": np.int32(observations_n),
                "unique_match_count": np.int32(unique_match_count),
                "low_n_flag": low_n_flag,
                "weak_ci_flag": weak_ci_flag,
                "b13_ceiling_bind_flag": b13,
                "mean_entry_price_cents": mean_entry_cents,
                "daily_opportunity_rate": daily_opp_rate,
                "expected_cents_per_dollar_capital_day": expected_cpd,
            })
        cell_idx += 1
        log.info(f"  cell {cell_key}: {len(EXIT_LINES_CENTS)} lines done "
                 f"(n={n})")

    df_a = pd.DataFrame(rows, columns=ARTIFACT_A_COLUMNS)
    log.info(f"Artifact A built: {len(df_a)} rows x {len(df_a.columns)} cols")
    return df_a


# ---------------------------------------------------------------------------
# Artifact B -- pure deterministic read of Artifact A (spec Section 3.2,
# gate 7). No new bootstrap.
# ---------------------------------------------------------------------------


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return 0.0
    if _HAVE_SCIPY:
        try:
            from scipy.stats import spearmanr  # type: ignore
            rho = spearmanr(x, y).statistic
            return float(rho) if np.isfinite(rho) else 0.0
        except Exception:
            pass
    rx = pd.Series(x).rank().to_numpy()
    ry = pd.Series(y).rank().to_numpy()
    if np.std(rx) == 0 or np.std(ry) == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])


def _curve_shape_note(cell_rows: pd.DataFrame, low_n_flag: bool) -> str:
    """Deterministic classifier EXACTLY per spec Section 5.3."""
    if low_n_flag:
        return "weak_low_n"
    total = len(cell_rows)  # 98 at full sweep
    n_b13 = int(cell_rows["b13_ceiling_bind_flag"].astype(bool).sum())
    if total > 0 and (n_b13 / total) > 0.5:
        return "ceiling_truncated"
    nb = cell_rows[~cell_rows["b13_ceiling_bind_flag"].astype(bool)].sort_values(
        "exit_line_cents")
    if len(nb) < 2:
        return "flat_ridge"
    el = nb["exit_line_cents"].to_numpy().astype(float)
    mc = nb["mean_realized_cents"].to_numpy().astype(float)
    rho = _spearman(el, mc)
    if abs(rho) >= 0.9:
        return "monotone"
    argmax_pos = int(np.argmax(mc))  # first max -> smallest exit_line on tie
    vmax = float(mc[argmax_pos])
    lstar = int(el[argmax_pos])
    v_lowline = float(mc[0])  # value at the lowest non-B13 exit line
    line_to_val = {int(e): float(m) for e, m in zip(el, mc)}
    conds = [vmax - v_lowline >= 1.0]
    left = line_to_val.get(lstar - 10)
    right = line_to_val.get(lstar + 10)
    if left is not None:
        conds.append(vmax - left >= 1.0)
    if right is not None:
        conds.append(vmax - right >= 1.0)
    if all(conds):
        return "clean_peak"
    return "flat_ridge"


def _argmax_nonb13(cell_rows: pd.DataFrame, metric: str, ignore_none: bool = False):
    """Return the row (Series) maximizing `metric` over non-B13 lines; tie ->
    smallest exit_line (rows are sorted ascending so first max wins)."""
    nb = cell_rows[~cell_rows["b13_ceiling_bind_flag"].astype(bool)].sort_values(
        "exit_line_cents")
    if len(nb) == 0:
        nb = cell_rows.sort_values("exit_line_cents")
    vals = nb[metric].to_numpy()
    if ignore_none:
        finite = np.array([v is not None and np.isfinite(v) for v in vals])
        if not finite.any():
            return None
        masked = np.where(finite, vals.astype(float), -np.inf)
        pos = int(np.argmax(masked))
    else:
        arr = nb[metric].to_numpy().astype(float)
        if not np.isfinite(arr).any():
            return None
        arr = np.where(np.isfinite(arr), arr, -np.inf)
        pos = int(np.argmax(arr))
    return nb.iloc[pos]


def build_artifact_b(df_a: pd.DataFrame) -> pd.DataFrame:
    """Pure deterministic read of Artifact A -- argmax + copy, no bootstrap."""
    rows = []
    for cell_key, cell_rows in df_a.groupby("cell_key", sort=True):
        cell_rows = cell_rows.sort_values("exit_line_cents")
        first = cell_rows.iloc[0]
        low_n_flag = bool(first["low_n_flag"])

        rc = _argmax_nonb13(cell_rows, "mean_realized_cents")
        rr = _argmax_nonb13(cell_rows, "mean_realized_roi_pct")
        rs = _argmax_nonb13(cell_rows, "sharpe_like_roi", ignore_none=True)

        row = {
            "cell_key": cell_key,
            "category": first["category"],
            "price_band": first["price_band"],
            "observations_n": np.int32(int(first["observations_n"])),
            "unique_match_count": np.int32(int(first["unique_match_count"])),
            "low_n_flag": low_n_flag,
            "mean_entry_price_cents": float(first["mean_entry_price_cents"]),
            "daily_opportunity_rate": float(first["daily_opportunity_rate"]),
            "opt_cents_exit_line": np.int16(int(rc["exit_line_cents"])),
            "opt_cents_mean_realized_cents": float(rc["mean_realized_cents"]),
            "opt_cents_mean_realized_cents_ci_lower": float(rc["mean_realized_cents_ci_lower"]),
            "opt_cents_mean_realized_cents_ci_upper": float(rc["mean_realized_cents_ci_upper"]),
            "opt_cents_hit_rate": float(rc["threshold_hit_rate"]),
            "opt_cents_hit_rate_ci_lower": float(rc["threshold_hit_rate_ci_lower"]),
            "opt_cents_hit_rate_ci_upper": float(rc["threshold_hit_rate_ci_upper"]),
            "opt_cents_mean_realized_roi_pct": float(rc["mean_realized_roi_pct"]),
            "opt_cents_weak_ci_flag": bool(rc["weak_ci_flag"]),
            "opt_roi_exit_line": np.int16(int(rr["exit_line_cents"])),
            "opt_roi_mean_realized_roi_pct": float(rr["mean_realized_roi_pct"]),
            "opt_roi_mean_realized_roi_pct_ci_lower": float(rr["mean_realized_roi_pct_ci_lower"]),
            "opt_roi_mean_realized_roi_pct_ci_upper": float(rr["mean_realized_roi_pct_ci_upper"]),
            "opt_roi_hit_rate": float(rr["threshold_hit_rate"]),
            "opt_roi_hit_rate_ci_lower": float(rr["threshold_hit_rate_ci_lower"]),
            "opt_roi_hit_rate_ci_upper": float(rr["threshold_hit_rate_ci_upper"]),
            "opt_roi_mean_realized_cents": float(rr["mean_realized_cents"]),
            "opt_roi_weak_ci_flag": bool(rr["weak_ci_flag"]),
            "opt_sharpe_exit_line": np.int16(int(rs["exit_line_cents"])) if rs is not None else np.int16(0),
            "opt_sharpe_value": (float(rs["sharpe_like_roi"]) if rs is not None
                                 and rs["sharpe_like_roi"] is not None else None),
            "opt_sharpe_mean_realized_roi_pct": (float(rs["mean_realized_roi_pct"])
                                                 if rs is not None else None),
            "curve_shape_note": _curve_shape_note(cell_rows, low_n_flag),
            "opt_cents_expected_cents_per_dollar_capital_day":
                float(rc["expected_cents_per_dollar_capital_day"]),
            "opt_roi_expected_cents_per_dollar_capital_day":
                float(rr["expected_cents_per_dollar_capital_day"]),
        }
        rows.append(row)
    df_b = pd.DataFrame(rows, columns=ARTIFACT_B_COLUMNS)
    log.info(f"Artifact B built: {len(df_b)} rows x {len(df_b.columns)} cols")
    return df_b


# ---------------------------------------------------------------------------
# Pipeline scaffold -- REUSED verbatim from the v0.1 skeleton.
# ---------------------------------------------------------------------------


def load_rung0(path: Path) -> pd.DataFrame:
    """Load Rung 0 corpus. Validates expected columns are present."""
    if not path.exists():
        raise FileNotFoundError(f"Rung 0 corpus not found at {path}")
    df = pd.read_parquet(path)
    required = {
        "cell_key", "category", "price_band",
        "peak_bid_bounce_pre_resolution",
        "t20m_trade_price",
        "realized_at_settlement",
        "event_ticker",
        "match_start_ts",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Rung 0 corpus missing required columns: {missing}")
    return df


def compute_corpus_active_days(rung0: pd.DataFrame) -> int:
    """Count distinct dates of match_start_ts in the corpus (spec Section 3.1)."""
    return rung0["match_start_ts"].dt.date.nunique()


def filter_by_phase(rung0: pd.DataFrame, phase: int) -> pd.DataFrame:
    """
    Phase 1: one cell (the first cell_key alphabetically with n>=50)
    Phase 2: <=10 cells stratified by category (top-2-by-N per category)
    Phase 3: full corpus
    """
    if phase == 3:
        return rung0
    elif phase == 1:
        counts = rung0.groupby("cell_key").size().reset_index(name="n")
        eligible = counts[counts["n"] >= 50].sort_values("cell_key")
        if len(eligible) == 0:
            raise RuntimeError("Phase 1: no cell has n>=50")
        chosen = eligible.iloc[0]["cell_key"]
        log.info(f"Phase 1: filtering to cell_key={chosen}")
        return rung0[rung0["cell_key"] == chosen].copy()
    elif phase == 2:
        counts = rung0.groupby(["category", "cell_key"]).size().reset_index(name="n")
        top_per_cat = counts.sort_values(
            ["category", "n"], ascending=[True, False]).groupby("category").head(2)
        chosen_cells = top_per_cat["cell_key"].tolist()
        log.info(f"Phase 2: filtering to {len(chosen_cells)} cells: {chosen_cells}")
        return rung0[rung0["cell_key"].isin(chosen_cells)].copy()
    else:
        raise ValueError(f"phase must be 1, 2, or 3 -- got {phase}")


# ---------------------------------------------------------------------------
# C37 hard gates (spec Section 6.1) -- run against on-disk .new bytes
# ---------------------------------------------------------------------------


def gate1_curve_row_count(df_a: pd.DataFrame, expected_cells: int) -> GateResult:
    expected = expected_cells * len(EXIT_LINES_CENTS)
    actual = len(df_a)
    return GateResult("gate1_curve_row_count", actual == expected,
                      abs(actual - expected),
                      f"expected {expected} (={expected_cells}x{len(EXIT_LINES_CENTS)}), got {actual}")


def gate2_curve_coverage(df_a: pd.DataFrame, expected_cells: list) -> GateResult:
    keys = list(zip(df_a["cell_key"], df_a["exit_line_cents"].astype(int)))
    expected_keys = {(c, e) for c in expected_cells for e in EXIT_LINES_CENTS}
    actual_keys = set(keys)
    missing = expected_keys - actual_keys
    extras = actual_keys - expected_keys
    dupes = len(keys) - len(actual_keys)
    v = len(missing) + len(extras) + dupes
    return GateResult("gate2_curve_coverage", v == 0, v,
                      f"missing={len(missing)} extras={len(extras)} dupes={dupes}")


def gate3_hit_rate_monotonicity(df_a: pd.DataFrame) -> GateResult:
    violations = 0
    parts = []
    for cell_key, g in df_a.groupby("cell_key"):
        hr = g.sort_values("exit_line_cents")["threshold_hit_rate"].to_numpy()
        cv = int(np.sum(np.diff(hr) > 1e-9))
        if cv > 0:
            violations += cv
            parts.append(f"{cell_key}={cv}")
    return GateResult("gate3_hit_rate_monotonicity", violations == 0, violations,
                      "; ".join(parts[:5]) if parts else "OK")


def gate4_realized_cents_bounds(df_a: pd.DataFrame, rung0: pd.DataFrame) -> GateResult:
    upper_v = int(np.sum(
        df_a["mean_realized_cents"] > df_a["exit_line_cents"].astype(float) + 1e-9))
    r = rung0[["cell_key", "realized_at_settlement"]].copy()
    r["ras_cents"] = r["realized_at_settlement"] * 100.0
    floor_by_cell = r.groupby("cell_key")["ras_cents"].min().to_dict()
    floor_v = 0
    parts = []
    for _, row in df_a.iterrows():
        floor = floor_by_cell.get(row["cell_key"], 0.0)
        if row["mean_realized_cents"] < floor - 1e-9:
            floor_v += 1
            if len(parts) < 5:
                parts.append(f"{row['cell_key']}@L{int(row['exit_line_cents'])}: "
                             f"mean={row['mean_realized_cents']:.2f}<floor={floor:.2f}")
    total = upper_v + floor_v
    return GateResult("gate4_realized_cents_bounds", total == 0, total,
                      f"upper={upper_v} floor={floor_v}; " + "; ".join(parts))


def _ci_violations(df: pd.DataFrame, triples: list) -> tuple:
    violations = 0
    parts = []
    for pt, lo, hi in triples:
        if pt not in df.columns:
            continue
        mask = df[pt].notna() & df[lo].notna() & df[hi].notna()
        if mask.sum() == 0:
            continue
        sub = df[mask]
        bad = sub[(sub[lo] > sub[pt] + 1e-9) | (sub[pt] > sub[hi] + 1e-9)]
        if len(bad) > 0:
            violations += len(bad)
            parts.append(f"{pt}={len(bad)}")
    return violations, parts


def gate5_ci_ordering(df_a: pd.DataFrame, df_b: pd.DataFrame) -> GateResult:
    a_triples = [
        ("threshold_hit_rate", "threshold_hit_rate_ci_lower", "threshold_hit_rate_ci_upper"),
        ("mean_realized_cents", "mean_realized_cents_ci_lower", "mean_realized_cents_ci_upper"),
        ("mean_realized_roi_pct", "mean_realized_roi_pct_ci_lower", "mean_realized_roi_pct_ci_upper"),
    ]
    b_triples = [
        ("opt_cents_mean_realized_cents", "opt_cents_mean_realized_cents_ci_lower",
         "opt_cents_mean_realized_cents_ci_upper"),
        ("opt_cents_hit_rate", "opt_cents_hit_rate_ci_lower", "opt_cents_hit_rate_ci_upper"),
        ("opt_roi_mean_realized_roi_pct", "opt_roi_mean_realized_roi_pct_ci_lower",
         "opt_roi_mean_realized_roi_pct_ci_upper"),
        ("opt_roi_hit_rate", "opt_roi_hit_rate_ci_lower", "opt_roi_hit_rate_ci_upper"),
    ]
    va, pa = _ci_violations(df_a, a_triples)
    vb, pb = _ci_violations(df_b, b_triples)
    v = va + vb
    return GateResult("gate5_ci_ordering", v == 0, v,
                      f"A:[{';'.join(pa)}] B:[{';'.join(pb)}]" if v else "OK")


def gate6_sample_quality_consistency(df_a: pd.DataFrame, df_b: pd.DataFrame) -> GateResult:
    bad_a = df_a[(df_a["low_n_flag"]) & (~df_a["weak_ci_flag"])]
    bad_b = df_b[(df_b["low_n_flag"]) &
                 ((~df_b["opt_cents_weak_ci_flag"]) | (~df_b["opt_roi_weak_ci_flag"]))]
    v = len(bad_a) + len(bad_b)
    return GateResult("gate6_sample_quality_consistency", v == 0, v,
                      f"A={len(bad_a)} B={len(bad_b)} (low_n implies weak_ci)")


def gate7_summary_derivation(df_a: pd.DataFrame, df_b: pd.DataFrame) -> GateResult:
    """Load-bearing: Artifact B is a pure read of Artifact A. Recompute the
    argmax independently from the reloaded Artifact A and assert B matches at
    exactly that (cell, opt exit_line) row. Zero tolerance (1e-9 float)."""
    violations = 0
    parts = []
    b_by_cell = {r["cell_key"]: r for _, r in df_b.iterrows()}
    for cell_key, cell_rows in df_a.groupby("cell_key"):
        cell_rows = cell_rows.sort_values("exit_line_cents")
        if cell_key not in b_by_cell:
            violations += 1
            parts.append(f"{cell_key}:missing_in_B")
            continue
        b = b_by_cell[cell_key]

        rc = _argmax_nonb13(cell_rows, "mean_realized_cents")
        if int(b["opt_cents_exit_line"]) != int(rc["exit_line_cents"]):
            violations += 1
            parts.append(f"{cell_key}:cents_line {int(b['opt_cents_exit_line'])}!="
                         f"{int(rc['exit_line_cents'])}")
        else:
            for bcol, acol in [
                ("opt_cents_mean_realized_cents", "mean_realized_cents"),
                ("opt_cents_mean_realized_cents_ci_lower", "mean_realized_cents_ci_lower"),
                ("opt_cents_mean_realized_cents_ci_upper", "mean_realized_cents_ci_upper"),
                ("opt_cents_hit_rate", "threshold_hit_rate"),
                ("opt_cents_hit_rate_ci_lower", "threshold_hit_rate_ci_lower"),
                ("opt_cents_hit_rate_ci_upper", "threshold_hit_rate_ci_upper"),
                ("opt_cents_mean_realized_roi_pct", "mean_realized_roi_pct"),
                ("opt_cents_expected_cents_per_dollar_capital_day",
                 "expected_cents_per_dollar_capital_day"),
            ]:
                if abs(float(b[bcol]) - float(rc[acol])) > 1e-9:
                    violations += 1
                    parts.append(f"{cell_key}:{bcol}")

        rr = _argmax_nonb13(cell_rows, "mean_realized_roi_pct")
        if int(b["opt_roi_exit_line"]) != int(rr["exit_line_cents"]):
            violations += 1
            parts.append(f"{cell_key}:roi_line")
        else:
            for bcol, acol in [
                ("opt_roi_mean_realized_roi_pct", "mean_realized_roi_pct"),
                ("opt_roi_mean_realized_roi_pct_ci_lower", "mean_realized_roi_pct_ci_lower"),
                ("opt_roi_mean_realized_roi_pct_ci_upper", "mean_realized_roi_pct_ci_upper"),
                ("opt_roi_hit_rate", "threshold_hit_rate"),
                ("opt_roi_mean_realized_cents", "mean_realized_cents"),
                ("opt_roi_expected_cents_per_dollar_capital_day",
                 "expected_cents_per_dollar_capital_day"),
            ]:
                if abs(float(b[bcol]) - float(rr[acol])) > 1e-9:
                    violations += 1
                    parts.append(f"{cell_key}:{bcol}")

        rs = _argmax_nonb13(cell_rows, "sharpe_like_roi", ignore_none=True)
        if rs is not None and int(b["opt_sharpe_exit_line"]) != int(rs["exit_line_cents"]):
            violations += 1
            parts.append(f"{cell_key}:sharpe_line")

    return GateResult("gate7_summary_derivation_consistency", violations == 0,
                      violations, "; ".join(parts[:6]) if parts else "OK")


def gate8_soft_mean_vs_median(df_a: pd.DataFrame) -> GateResult:
    bad = df_a[df_a["mean_realized_cents"] < df_a["median_realized_cents"] - 1e-9]
    return GateResult("gate8_soft_mean_vs_median", len(bad) == 0, len(bad),
                      f"mean<median in {len(bad)} rows (SOFT -- not blocking)")


def run_all_gates(curve_path: Path, optimum_path: Path,
                  rung0: pd.DataFrame, expected_cells: list) -> list:
    """C37: reload BOTH .new parquets from disk; gate 7 cross-checks the
    reloaded Artifact B against the reloaded Artifact A."""
    log.info(f"Reloading {curve_path} and {optimum_path} for gate validation")
    df_a = pd.read_parquet(curve_path)
    df_b = pd.read_parquet(optimum_path)
    log.info(f"On-disk Artifact A {df_a.shape}; Artifact B {df_b.shape}")
    return [
        gate1_curve_row_count(df_a, len(expected_cells)),
        gate2_curve_coverage(df_a, expected_cells),
        gate3_hit_rate_monotonicity(df_a),
        gate4_realized_cents_bounds(df_a, rung0),
        gate5_ci_ordering(df_a, df_b),
        gate6_sample_quality_consistency(df_a, df_b),
        gate7_summary_derivation(df_a, df_b),
        gate8_soft_mean_vs_median(df_a),
    ]


# ---------------------------------------------------------------------------
# Output I/O + sidecars
# ---------------------------------------------------------------------------


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def write_meta_sidecar(meta_path: Path, result: ProducerResult) -> None:
    meta = {
        "spec": "docs/rung1_strategy_evaluation_spec.md v0.3.2",
        "spec_commit": "3bbac375",
        "producer_commit": result.producer_commit,
        "rung0_input_commit": "5ca2d89c",
        "input_sha256": result.input_sha256,
        "curve_sha256": result.curve_sha256,
        "optimum_sha256": result.optimum_sha256,
        "curve_bytes": result.curve_bytes,
        "optimum_bytes": result.optimum_bytes,
        "artifact_a_rows": result.artifact_a_rows,
        "artifact_b_rows": result.artifact_b_rows,
        "cells_covered": result.cells_covered,
        "exit_lines_covered": result.exit_lines_covered,
        "bootstrap_fallback_rate": result.bootstrap_fallback_rate,
        "run_started_at_et": result.run_started_at_et,
        "run_completed_at_et": result.run_completed_at_et,
        "gates": [
            {"name": g.name, "passed": g.passed,
             "n_violations": g.n_violations, "detail": g.detail}
            for g in result.gate_results
        ],
    }
    meta_path.write_text(json.dumps(meta, indent=2, default=str))


def write_validation_report(report_path: Path, df_a: pd.DataFrame,
                            df_b: pd.DataFrame, result: ProducerResult) -> None:
    """Spec Section 5.1-5.5."""
    lines = [
        "# Rung 1 Strategy Evaluation -- Validation Report",
        "",
        "**Spec:** docs/rung1_strategy_evaluation_spec.md v0.3.2 (commit 3bbac375)",
        f"**Producer commit:** {result.producer_commit}",
        f"**Run completed:** {result.run_completed_at_et}",
        f"**Rung 0 input sha256:** {result.input_sha256}",
        f"**Artifact A (curve) sha256:** {result.curve_sha256} "
        f"({result.artifact_a_rows} rows)",
        f"**Artifact B (optimum) sha256:** {result.optimum_sha256} "
        f"({result.artifact_b_rows} rows)",
        f"**Bootstrap percentile-fallback rate:** "
        f"{result.bootstrap_fallback_rate:.2%}"
        + ("  **>5% -- numerical-stability flag (Section 6.2)**"
           if result.bootstrap_fallback_rate > 0.05 else ""),
        "",
        "## Gate results",
        "",
        "| Gate | Passed | N violations | Detail |",
        "|---|---|---|---|",
    ]
    for g in result.gate_results:
        lines.append(f"| {g.name} | {'PASS' if g.passed else 'FAIL'} "
                     f"| {g.n_violations} | {g.detail} |")

    b = df_b.copy()
    # 5.1 Top-20 by cents-optimal realized cents
    lines += ["", "## 5.1 Top-20 cells by cents-optimal realized cents", "",
              "| cell_key | obs_n | opt_cents_exit_line | cents [CI] | xview ROI "
              "| low_n | weak_ci | curve_shape |", "|---|---|---|---|---|---|---|---|"]
    for _, r in b.sort_values("opt_cents_mean_realized_cents",
                              ascending=False).head(20).iterrows():
        lines.append(
            f"| {r['cell_key']} | {int(r['observations_n'])} "
            f"| {int(r['opt_cents_exit_line'])} "
            f"| {r['opt_cents_mean_realized_cents']:.2f} "
            f"[{r['opt_cents_mean_realized_cents_ci_lower']:.2f}, "
            f"{r['opt_cents_mean_realized_cents_ci_upper']:.2f}] "
            f"| {r['opt_cents_mean_realized_roi_pct']:.2f} "
            f"| {bool(r['low_n_flag'])} | {bool(r['opt_cents_weak_ci_flag'])} "
            f"| {r['curve_shape_note']} |")

    # 5.2 Top-20 by ROI-optimal realized ROI
    lines += ["", "## 5.2 Top-20 cells by ROI-optimal realized ROI", "",
              "| cell_key | obs_n | opt_roi_exit_line | ROI%% [CI] | xview cents "
              "| low_n | weak_ci | curve_shape |", "|---|---|---|---|---|---|---|---|"]
    for _, r in b.sort_values("opt_roi_mean_realized_roi_pct",
                              ascending=False).head(20).iterrows():
        lines.append(
            f"| {r['cell_key']} | {int(r['observations_n'])} "
            f"| {int(r['opt_roi_exit_line'])} "
            f"| {r['opt_roi_mean_realized_roi_pct']:.2f} "
            f"[{r['opt_roi_mean_realized_roi_pct_ci_lower']:.2f}, "
            f"{r['opt_roi_mean_realized_roi_pct_ci_upper']:.2f}] "
            f"| {r['opt_roi_mean_realized_cents']:.2f} "
            f"| {bool(r['low_n_flag'])} | {bool(r['opt_roi_weak_ci_flag'])} "
            f"| {r['curve_shape_note']} |")

    # 5.3 Curve-shape classifier table
    lines += ["", "## 5.3 Curve-shape classifier (per cell)", "",
              "| cell_key | curve_shape | opt_cents_exit_line | peak_prominence |",
              "|---|---|---|---|"]
    for cell_key, cr in df_a.groupby("cell_key"):
        nb = cr[~cr["b13_ceiling_bind_flag"].astype(bool)]
        mc = nb["mean_realized_cents"].to_numpy() if len(nb) else np.array([0.0])
        prominence = float(mc.max() - mc.mean()) if len(mc) else 0.0
        brow = b[b["cell_key"] == cell_key].iloc[0]
        lines.append(f"| {cell_key} | {brow['curve_shape_note']} "
                     f"| {int(brow['opt_cents_exit_line'])} | {prominence:.2f} |")

    # 5.4 Per-cell recommended exit (the deliverable headline)
    lines += ["", "## 5.4 Per-cell recommended exit", "",
              "| cell_key | opt_cents (cents[CI]) | opt_roi (ROI%%[CI]) "
              "| opt_sharpe | curve_shape | low_n | weak_ci(c/r) |",
              "|---|---|---|---|---|---|---|"]
    for _, r in b.sort_values("cell_key").iterrows():
        lines.append(
            f"| {r['cell_key']} "
            f"| L{int(r['opt_cents_exit_line'])} {r['opt_cents_mean_realized_cents']:.2f}"
            f"[{r['opt_cents_mean_realized_cents_ci_lower']:.2f},"
            f"{r['opt_cents_mean_realized_cents_ci_upper']:.2f}] "
            f"| L{int(r['opt_roi_exit_line'])} {r['opt_roi_mean_realized_roi_pct']:.2f}"
            f"[{r['opt_roi_mean_realized_roi_pct_ci_lower']:.2f},"
            f"{r['opt_roi_mean_realized_roi_pct_ci_upper']:.2f}] "
            f"| L{int(r['opt_sharpe_exit_line'])} "
            f"| {r['curve_shape_note']} | {bool(r['low_n_flag'])} "
            f"| {bool(r['opt_cents_weak_ci_flag'])}/{bool(r['opt_roi_weak_ci_flag'])} |")

    # 5.5 Sample-quality summary
    shape_counts = b["curve_shape_note"].value_counts().to_dict()
    lines += ["", "## 5.5 Sample-quality summary", "",
              f"- Cells total: {len(b)}",
              f"- low_n_flag cells: {int(b['low_n_flag'].sum())}",
              f"- curve_shape_note distribution: {shape_counts}",
              ""]
    by_cat = (b.groupby("category")["curve_shape_note"]
              .apply(lambda s: int((s == 'clean_peak').sum())).to_dict())
    lines.append(f"- clean_peak cells by category: {by_cat}")
    lines += ["",
              f"- Bootstrap percentile-fallback rate: "
              f"{result.bootstrap_fallback_rate:.2%} "
              f"({_BOOT_STATS['fallbacks']}/{_BOOT_STATS['calls']} calls)"]
    report_path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Rung 1 producer (v0.3.2)")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--phase", type=int, default=3, choices=[1, 2, 3])
    args = parser.parse_args()

    started_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")
    log.info(f"Rung 1 producer (v0.3.2) starting at {started_at}; phase {args.phase}")

    rung0_full = load_rung0(args.input)
    input_sha = sha256_of_file(args.input)
    log.info(f"Loaded Rung 0: {len(rung0_full)} N's, sha256 {input_sha[:16]}...")

    # corpus_active_days ONCE on the FULL unfiltered corpus (G22-aligned spec
    # Section 3.1) -- the operational total-span denominator for N's-per-day.
    corpus_active_days = compute_corpus_active_days(rung0_full)
    log.info(f"Full-corpus active days: {corpus_active_days}")

    rung0 = filter_by_phase(rung0_full, args.phase)
    expected_cells = sorted(rung0["cell_key"].unique().tolist())
    log.info(f"Filtered to {len(rung0)} N's, {len(expected_cells)} cells")

    df_a = build_artifact_a(rung0, corpus_active_days)
    df_b = build_artifact_b(df_a)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    curve_final = args.output_dir / CURVE_FILE
    optimum_final = args.output_dir / OPTIMUM_FILE
    curve_new = args.output_dir / f"{CURVE_FILE}.new"
    optimum_new = args.output_dir / f"{OPTIMUM_FILE}.new"
    log.info(f"Writing {curve_new} and {optimum_new}")
    df_a.to_parquet(curve_new, compression="snappy", index=False)
    df_b.to_parquet(optimum_new, compression="snappy", index=False)

    # C37: reload BOTH from disk; run gates against the on-disk bytes.
    gate_results = run_all_gates(curve_new, optimum_new, rung0, expected_cells)
    for g in gate_results:
        log.info(f"  {g.name}: {'PASS' if g.passed else 'FAIL'} "
                 f"(n={g.n_violations}) {g.detail}")

    hard = [g for g in gate_results if not g.name.startswith("gate8_soft")]
    all_hard_pass = all(g.passed for g in hard)

    if not all_hard_pass:
        log.error(f"HARD GATE FAILURE -- halting; both .new preserved "
                  f"({curve_new}, {optimum_new})")
        DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        halt = DEFAULT_LOG_DIR / f"halted_{datetime.now(ET).strftime('%Y%m%dT%H%M%S')}.log"
        halt.write_text("\n".join(
            f"{g.name}: passed={g.passed} n={g.n_violations} detail={g.detail}"
            for g in gate_results) + "\n")
        log.error(f"Halt log: {halt}")
        return 1

    log.info("All 7 hard gates PASS -- os.replace BOTH artifacts")
    os.replace(curve_new, curve_final)
    os.replace(optimum_new, optimum_final)

    fallback_rate = (_BOOT_STATS["fallbacks"] / _BOOT_STATS["calls"]
                     if _BOOT_STATS["calls"] else 0.0)
    completed_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")
    result = ProducerResult(
        artifact_a_rows=len(df_a),
        artifact_b_rows=len(df_b),
        cells_covered=len(expected_cells),
        exit_lines_covered=len(EXIT_LINES_CENTS),
        gate_results=gate_results,
        curve_sha256=sha256_of_file(curve_final),
        optimum_sha256=sha256_of_file(optimum_final),
        curve_bytes=curve_final.stat().st_size,
        optimum_bytes=optimum_final.stat().st_size,
        run_started_at_et=started_at,
        run_completed_at_et=completed_at,
        input_sha256=input_sha,
        producer_commit=_git_commit(),
        bootstrap_fallback_rate=fallback_rate,
    )
    write_meta_sidecar(args.output_dir / DEFAULT_META_FILE, result)
    write_validation_report(args.output_dir / DEFAULT_REPORT_FILE, df_a, df_b, result)

    log.info(f"v0.3.2 complete. Artifact A {len(df_a)} rows "
             f"sha {result.curve_sha256[:16]}...; Artifact B {len(df_b)} rows "
             f"sha {result.optimum_sha256[:16]}...; "
             f"bootstrap fallback {fallback_rate:.2%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
