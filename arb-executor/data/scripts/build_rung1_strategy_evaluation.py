"""
Rung 1 producer: per-band optimized-exit-target strategy evaluation.

Phase A SKELETON — architecture and C37 discipline. Statistical metrics are
stubbed; Phase B (separate commit) fills in Wilson CIs, BCa bootstrap,
downside std, and risk-adjusted ratios.

Spec: docs/rung1_strategy_evaluation_spec.md v0.1 (commit 92198d64).
Input: data/durable/rung0_cell_economics/cell_economics.parquet
       (sha256 6fdd019d…, commit 5ca2d89c).
Output: data/durable/rung1_strategy_evaluation/strategy_evaluation.parquet
        plus validation_report.md and .meta.json sidecar.

C37 discipline: write .new, reload from disk, run all 6 hard gates against
on-disk bytes, os.replace only on all-pass. Halt with .new preserved on any
hard-gate failure.

Usage:
    python build_rung1_strategy_evaluation.py [--input PATH] [--output PATH] [--phase {1,2,3}]

Phases (mirrors Rung 0 producer rollout discipline):
    Phase 1: one cell × all 8 thresholds. Visual inspection. <30s.
    Phase 2: 10 cells stratified by category × all thresholds. <2 min.
    Phase 3: full 72 cells × 8 thresholds = 576 rows. <5 min skeleton (will be
             5-20 min once Phase B bootstrap is in).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
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
DEFAULT_OUTPUT_FILE = "strategy_evaluation.parquet"
DEFAULT_REPORT_FILE = "validation_report.md"
DEFAULT_META_FILE = "strategy_evaluation.meta.json"
DEFAULT_LOG_DIR = Path("data/durable/rung1_strategy_evaluation/logs")

# Locked threshold grid per spec Section 2.2 (operator-locked v0.1).
THRESHOLD_GRID_CENTS = [5, 10, 15, 20, 25, 30, 40, 50]

# Output schema columns in exact order (41 cols per spec Section 3.2).
SCHEMA_COLUMNS = [
    "cell_key",
    "category",
    "price_band",
    "threshold_cents",
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
    "median_realized_cents_ci_lower",
    "median_realized_cents_ci_upper",
    "median_realized_roi_pct",
    "median_realized_roi_pct_ci_lower",
    "median_realized_roi_pct_ci_upper",
    "std_realized_cents",
    "std_realized_cents_ci_lower",
    "std_realized_cents_ci_upper",
    "std_realized_roi_pct",
    "std_realized_roi_pct_ci_lower",
    "std_realized_roi_pct_ci_upper",
    "downside_std_realized_cents",
    "downside_std_realized_cents_ci_lower",
    "downside_std_realized_cents_ci_upper",
    "sharpe_like_roi",
    "sharpe_like_roi_ci_lower",
    "sharpe_like_roi_ci_upper",
    "sortino_like_roi",
    "sortino_like_roi_ci_lower",
    "sortino_like_roi_ci_upper",
    "observations_n",
    "unique_match_count",
    "low_n_flag",
    "weak_ci_flag",
    "mean_entry_price_cents",
    "daily_opportunity_rate",
    "expected_cents_per_dollar_capital_day",
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
    rows_emitted: int
    cells_covered: int
    thresholds_covered: int
    gate_results: list[GateResult] = field(default_factory=list)
    output_sha256: Optional[str] = None
    output_bytes: Optional[int] = None
    run_started_at_et: Optional[str] = None
    run_completed_at_et: Optional[str] = None
    input_sha256: Optional[str] = None


# ---------------------------------------------------------------------------
# Per-row realized derivation (spec Section 2.3)
# ---------------------------------------------------------------------------


def compute_per_row_realized(rung0: pd.DataFrame, threshold_cents: int) -> pd.DataFrame:
    """
    Per spec Section 2.3:
      peak_bounce_cents = peak_bid_bounce_pre_resolution * 100
      entry_price_cents = t20m_trade_price * 100
      realized_at_settlement_cents = realized_at_settlement * 100  (signed)

      hit = peak_bounce_cents >= threshold_cents
      if hit:  realized_cents = threshold_cents
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

    hit = peak_bounce_cents >= float(threshold_cents)
    realized_cents = np.where(hit, float(threshold_cents), realized_at_settlement_cents)
    # Guard: avoid divide-by-zero on the unlikely entry_price=0 edge.
    # Under spec the band-exclusion gate guarantees entry_price >= 0.05 dollars
    # (5c band lower bound), so entry_price_cents >= 5. But keep defensive code.
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
# Metric stubs (Phase B will replace these with real Wilson / BCa logic)
# ---------------------------------------------------------------------------


def wilson_ci_stub(successes: int, n: int) -> tuple[float, float]:
    """STUB. Phase B replaces with real Wilson interval."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    # Conservative placeholder: ±0.05 around point estimate, clipped to [0,1].
    return (max(0.0, p - 0.05), min(1.0, p + 0.05))


def bca_bootstrap_stub(values: np.ndarray, statistic: str) -> tuple[float, float, float]:
    """STUB. Phase B replaces with real BCa bootstrap n=1000.

    Returns (point_estimate, ci_lower, ci_upper).
    statistic is one of: 'mean', 'median', 'std', 'downside_std'.
    """
    if len(values) == 0:
        return (0.0, 0.0, 0.0)

    if statistic == "mean":
        point = float(np.mean(values))
    elif statistic == "median":
        point = float(np.median(values))
    elif statistic == "std":
        point = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    elif statistic == "downside_std":
        neg = values[values < 0]
        point = float(np.std(neg, ddof=1)) if len(neg) > 1 else 0.0
    else:
        raise ValueError(f"unknown statistic: {statistic}")

    # Stub CI: ±10% of |point|, or ±1.0 if point is near zero. Phase B replaces.
    half_width = max(abs(point) * 0.10, 1.0)
    return (point, point - half_width, point + half_width)


def ratio_bootstrap_stub(
    numerator_values: np.ndarray, denominator_values: np.ndarray
) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """STUB. Phase B replaces with real BCa bootstrap on ratio.

    For Sharpe/Sortino: numerator_values is the realized distribution,
    denominator_values is the same distribution (Phase B will compute the
    ratio per resample).
    """
    if len(numerator_values) == 0:
        return (None, None, None)

    mean_num = float(np.mean(numerator_values))
    if len(denominator_values) > 1:
        denom = float(np.std(denominator_values, ddof=1))
    else:
        denom = 0.0

    if denom == 0.0:
        return (None, None, None)

    point = mean_num / denom
    half_width = max(abs(point) * 0.10, 0.1)
    return (point, point - half_width, point + half_width)


# ---------------------------------------------------------------------------
# Group aggregation (spec Section 3)
# ---------------------------------------------------------------------------


def aggregate_cell_threshold_group(
    group: pd.DataFrame,
    cell_key: str,
    category: str,
    price_band: str,
    threshold_cents: int,
    corpus_active_days: int,
) -> dict:
    """
    For one (cell_key, threshold) group, compute all 16 metrics + CIs +
    helpers. Returns a dict matching SCHEMA_COLUMNS exactly.

    Phase A: metrics 1, 11, 12, 13, 15 are real (no statistics needed).
    Bootstrapped metrics (2-10) use stubs that return reasonable placeholder
    values. weak_ci_flag is computed from the stub CIs.
    """
    n = len(group)
    successes = int(group["hit"].sum())
    realized_cents = group["realized_cents"].to_numpy()
    realized_roi_pct = group["realized_roi_pct"].to_numpy()

    # Metric 1: threshold_hit_rate (real, no stats needed beyond Wilson stub)
    hit_rate = successes / n if n > 0 else 0.0
    hit_rate_lo, hit_rate_hi = wilson_ci_stub(successes, n)

    # Metric 2: mean_realized_cents (stub bootstrap)
    mean_cents, mean_cents_lo, mean_cents_hi = bca_bootstrap_stub(
        realized_cents, "mean"
    )

    # Metric 3: mean_realized_roi_pct (stub bootstrap)
    # Filter NaNs from divide-by-zero guard.
    roi_finite = realized_roi_pct[np.isfinite(realized_roi_pct)]
    mean_roi, mean_roi_lo, mean_roi_hi = bca_bootstrap_stub(roi_finite, "mean")

    # Metric 4: median_realized_cents (stub)
    median_cents, median_cents_lo, median_cents_hi = bca_bootstrap_stub(
        realized_cents, "median"
    )

    # Metric 5: median_realized_roi_pct (stub)
    median_roi, median_roi_lo, median_roi_hi = bca_bootstrap_stub(roi_finite, "median")

    # Metric 6: std_realized_cents (stub)
    std_cents, std_cents_lo, std_cents_hi = bca_bootstrap_stub(realized_cents, "std")

    # Metric 7: std_realized_roi_pct (stub)
    std_roi, std_roi_lo, std_roi_hi = bca_bootstrap_stub(roi_finite, "std")

    # Metric 8: downside_std_realized_cents (stub; negatives-only)
    ds_cents, ds_cents_lo, ds_cents_hi = bca_bootstrap_stub(
        realized_cents, "downside_std"
    )

    # Metric 9: sharpe_like_roi (stub ratio)
    sharpe_pt, sharpe_lo, sharpe_hi = ratio_bootstrap_stub(roi_finite, roi_finite)

    # Metric 10: sortino_like_roi (stub ratio; uses downside std on ROI)
    # For the stub: feed the negative-only ROI subset as denominator source.
    neg_roi = roi_finite[roi_finite < 0]
    sortino_pt, sortino_lo, sortino_hi = ratio_bootstrap_stub(roi_finite, neg_roi)

    # Metrics 11, 12: observations_n, unique_match_count
    observations_n = n
    unique_match_count = int(group["event_ticker"].nunique())

    # Metrics 13, 14: low_n_flag, weak_ci_flag
    low_n_flag = bool(n < 30)
    roi_ci_crosses_zero = (mean_roi_lo is not None and mean_roi_hi is not None
                          and mean_roi_lo < 0 < mean_roi_hi)
    hit_rate_ci_wide = (hit_rate_hi - hit_rate_lo) > 0.20
    weak_ci_flag = bool(low_n_flag or roi_ci_crosses_zero or hit_rate_ci_wide)

    # Metric 15: mean_entry_price_cents
    mean_entry_cents = float(group["entry_price_cents"].mean()) if n > 0 else 0.0

    # Helper: daily_opportunity_rate (cell-level — same for every threshold within cell)
    daily_opp_rate = n / corpus_active_days if corpus_active_days > 0 else 0.0

    # Metric 16: expected_cents_per_dollar_capital_day
    if mean_entry_cents > 0:
        expected_cpd = (mean_cents * daily_opp_rate) / mean_entry_cents
    else:
        expected_cpd = 0.0

    return {
        "cell_key": cell_key,
        "category": category,
        "price_band": price_band,
        "threshold_cents": np.int8(threshold_cents),
        "threshold_hit_rate": hit_rate,
        "threshold_hit_rate_ci_lower": hit_rate_lo,
        "threshold_hit_rate_ci_upper": hit_rate_hi,
        "mean_realized_cents": mean_cents,
        "mean_realized_cents_ci_lower": mean_cents_lo,
        "mean_realized_cents_ci_upper": mean_cents_hi,
        "mean_realized_roi_pct": mean_roi,
        "mean_realized_roi_pct_ci_lower": mean_roi_lo,
        "mean_realized_roi_pct_ci_upper": mean_roi_hi,
        "median_realized_cents": median_cents,
        "median_realized_cents_ci_lower": median_cents_lo,
        "median_realized_cents_ci_upper": median_cents_hi,
        "median_realized_roi_pct": median_roi,
        "median_realized_roi_pct_ci_lower": median_roi_lo,
        "median_realized_roi_pct_ci_upper": median_roi_hi,
        "std_realized_cents": std_cents,
        "std_realized_cents_ci_lower": std_cents_lo,
        "std_realized_cents_ci_upper": std_cents_hi,
        "std_realized_roi_pct": std_roi,
        "std_realized_roi_pct_ci_lower": std_roi_lo,
        "std_realized_roi_pct_ci_upper": std_roi_hi,
        "downside_std_realized_cents": ds_cents,
        "downside_std_realized_cents_ci_lower": ds_cents_lo,
        "downside_std_realized_cents_ci_upper": ds_cents_hi,
        "sharpe_like_roi": sharpe_pt,
        "sharpe_like_roi_ci_lower": sharpe_lo,
        "sharpe_like_roi_ci_upper": sharpe_hi,
        "sortino_like_roi": sortino_pt,
        "sortino_like_roi_ci_lower": sortino_lo,
        "sortino_like_roi_ci_upper": sortino_hi,
        "observations_n": np.int32(observations_n),
        "unique_match_count": np.int32(unique_match_count),
        "low_n_flag": low_n_flag,
        "weak_ci_flag": weak_ci_flag,
        "mean_entry_price_cents": mean_entry_cents,
        "daily_opportunity_rate": daily_opp_rate,
        "expected_cents_per_dollar_capital_day": expected_cpd,
    }


# ---------------------------------------------------------------------------
# Producer pipeline
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
    Phase 1: one cell (the first cell_key alphabetically with n>=50, for stability)
    Phase 2: 10 cells stratified by category (top-2-by-N per category if available)
    Phase 3: full corpus
    """
    if phase == 3:
        return rung0
    elif phase == 1:
        # Pick one cell with n>=50 for visible distributional structure
        counts = rung0.groupby("cell_key").size().reset_index(name="n")
        eligible = counts[counts["n"] >= 50].sort_values("cell_key")
        if len(eligible) == 0:
            raise RuntimeError("Phase 1: no cell has n>=50")
        chosen = eligible.iloc[0]["cell_key"]
        log.info(f"Phase 1: filtering to cell_key={chosen}")
        return rung0[rung0["cell_key"] == chosen].copy()
    elif phase == 2:
        # Top-2-by-N per category, total <=10 cells
        counts = rung0.groupby(["category", "cell_key"]).size().reset_index(name="n")
        top_per_cat = counts.sort_values(["category", "n"], ascending=[True, False]).groupby("category").head(2)
        chosen_cells = top_per_cat["cell_key"].tolist()
        log.info(f"Phase 2: filtering to {len(chosen_cells)} cells: {chosen_cells}")
        return rung0[rung0["cell_key"].isin(chosen_cells)].copy()
    else:
        raise ValueError(f"phase must be 1, 2, or 3 — got {phase}")


def build_output(rung0: pd.DataFrame, corpus_active_days: int) -> pd.DataFrame:
    """
    Main pipeline. For each threshold, compute per-row realized values.
    Then groupby cell_key and aggregate. Result: 72×8 = 576 rows (or fewer in
    phase 1/2).

    corpus_active_days is passed in from caller — must be computed on the FULL
    unfiltered Rung 0 corpus (per spec Section 3.1, G22-aligned), NOT on the
    phase-filtered slice. The denominator measures N's-per-day across the
    operational total span regardless of which cells the current phase is
    processing (LESSONS G22: N = market / unit-of-observation; ct = sizing unit).
    """
    log.info(f"Corpus active days (full-corpus denominator for N's-per-day): {corpus_active_days}")
    log.info(f"Rung 0 N's this phase: {len(rung0)}; cells: {rung0['cell_key'].nunique()}")

    rows = []
    for threshold_cents in THRESHOLD_GRID_CENTS:
        log.info(f"Processing threshold +{threshold_cents}c")
        rung0_aug = compute_per_row_realized(rung0, threshold_cents)
        for cell_key, group in rung0_aug.groupby("cell_key", sort=True):
            category = group["category"].iloc[0]
            price_band = group["price_band"].iloc[0]
            row = aggregate_cell_threshold_group(
                group,
                cell_key=cell_key,
                category=category,
                price_band=price_band,
                threshold_cents=threshold_cents,
                corpus_active_days=corpus_active_days,
            )
            rows.append(row)

    df_out = pd.DataFrame(rows, columns=SCHEMA_COLUMNS)
    log.info(f"Built output: {len(df_out)} rows × {len(df_out.columns)} cols")
    return df_out


# ---------------------------------------------------------------------------
# C37 hard gates (spec Section 6.1) — run against on-disk .new bytes
# ---------------------------------------------------------------------------


def gate1_row_count(df: pd.DataFrame, expected_cells: int) -> GateResult:
    """Output must have exactly expected_cells × 8 = N rows."""
    expected = expected_cells * len(THRESHOLD_GRID_CENTS)
    actual = len(df)
    return GateResult(
        name="gate1_row_count",
        passed=(actual == expected),
        n_violations=abs(actual - expected),
        detail=f"expected {expected} (={expected_cells}×{len(THRESHOLD_GRID_CENTS)}), got {actual}",
    )


def gate2_cell_coverage(df: pd.DataFrame, expected_cells: list[str]) -> GateResult:
    """Every (cell_key, threshold) combination appears exactly once."""
    keys = list(zip(df["cell_key"], df["threshold_cents"]))
    expected_keys = {(c, t) for c in expected_cells for t in THRESHOLD_GRID_CENTS}
    actual_keys = set(keys)
    missing = expected_keys - actual_keys
    extras = actual_keys - expected_keys
    dupes = len(keys) - len(actual_keys)
    violations = len(missing) + len(extras) + dupes
    return GateResult(
        name="gate2_cell_coverage",
        passed=(violations == 0),
        n_violations=violations,
        detail=f"missing={len(missing)} extras={len(extras)} dupes={dupes}",
    )


def gate3_hit_rate_monotonicity(df: pd.DataFrame) -> GateResult:
    """For each cell, threshold_hit_rate must be monotonically non-increasing as threshold rises."""
    violations = 0
    detail_parts = []
    for cell_key, group in df.groupby("cell_key"):
        sorted_g = group.sort_values("threshold_cents")
        hr = sorted_g["threshold_hit_rate"].to_numpy()
        # Allow tiny floating-point slack (e.g., 1e-9) but not real inversions.
        diffs = np.diff(hr)
        cell_violations = int(np.sum(diffs > 1e-9))
        if cell_violations > 0:
            violations += cell_violations
            detail_parts.append(f"{cell_key}={cell_violations}")
    return GateResult(
        name="gate3_hit_rate_monotonicity",
        passed=(violations == 0),
        n_violations=violations,
        detail="; ".join(detail_parts[:5]) if detail_parts else "OK",
    )


def gate4_realized_cents_bounds(df: pd.DataFrame, rung0: pd.DataFrame) -> GateResult:
    """
    mean_realized_cents <= threshold_cents (since hit rows contribute exactly
    threshold; miss rows under E32 contribute <=0).
    Also: mean_realized_cents >= worst possible realized_at_settlement among
    contributing rows (i.e., not below the floor).
    """
    upper_violations = int(
        np.sum(df["mean_realized_cents"] > df["threshold_cents"].astype(float) + 1e-9)
    )

    # Floor check: per-cell, worst realized_at_settlement * 100 sets the floor.
    rung0_cents = rung0[["cell_key", "realized_at_settlement"]].copy()
    rung0_cents["ras_cents"] = rung0_cents["realized_at_settlement"] * 100.0
    floor_by_cell = rung0_cents.groupby("cell_key")["ras_cents"].min().to_dict()

    floor_violations = 0
    detail_parts = []
    for _, row in df.iterrows():
        floor = floor_by_cell.get(row["cell_key"], 0.0)
        if row["mean_realized_cents"] < floor - 1e-9:
            floor_violations += 1
            if len(detail_parts) < 5:
                detail_parts.append(
                    f"{row['cell_key']}@+{int(row['threshold_cents'])}c: "
                    f"mean={row['mean_realized_cents']:.2f} < floor={floor:.2f}"
                )

    total = upper_violations + floor_violations
    return GateResult(
        name="gate4_realized_cents_bounds",
        passed=(total == 0),
        n_violations=total,
        detail=f"upper={upper_violations} floor={floor_violations}; "
               + "; ".join(detail_parts),
    )


def gate5_ci_ordering(df: pd.DataFrame) -> GateResult:
    """For every metric with CI bounds, ci_lower <= point_estimate <= ci_upper."""
    pairs = [
        ("threshold_hit_rate", "threshold_hit_rate_ci_lower", "threshold_hit_rate_ci_upper"),
        ("mean_realized_cents", "mean_realized_cents_ci_lower", "mean_realized_cents_ci_upper"),
        ("mean_realized_roi_pct", "mean_realized_roi_pct_ci_lower", "mean_realized_roi_pct_ci_upper"),
        ("median_realized_cents", "median_realized_cents_ci_lower", "median_realized_cents_ci_upper"),
        ("median_realized_roi_pct", "median_realized_roi_pct_ci_lower", "median_realized_roi_pct_ci_upper"),
        ("std_realized_cents", "std_realized_cents_ci_lower", "std_realized_cents_ci_upper"),
        ("std_realized_roi_pct", "std_realized_roi_pct_ci_lower", "std_realized_roi_pct_ci_upper"),
        ("downside_std_realized_cents", "downside_std_realized_cents_ci_lower", "downside_std_realized_cents_ci_upper"),
        ("sharpe_like_roi", "sharpe_like_roi_ci_lower", "sharpe_like_roi_ci_upper"),
        ("sortino_like_roi", "sortino_like_roi_ci_lower", "sortino_like_roi_ci_upper"),
    ]
    violations = 0
    detail_parts = []
    for pt_col, lo_col, hi_col in pairs:
        # For ratio metrics with possible nulls, only check rows where all three are present.
        mask = df[pt_col].notna() & df[lo_col].notna() & df[hi_col].notna()
        if mask.sum() == 0:
            continue
        sub = df[mask]
        bad = sub[(sub[lo_col] > sub[pt_col] + 1e-9) | (sub[pt_col] > sub[hi_col] + 1e-9)]
        if len(bad) > 0:
            violations += len(bad)
            detail_parts.append(f"{pt_col}={len(bad)}")
    return GateResult(
        name="gate5_ci_ordering",
        passed=(violations == 0),
        n_violations=violations,
        detail="; ".join(detail_parts) if detail_parts else "OK",
    )


def gate6_sample_quality_consistency(df: pd.DataFrame) -> GateResult:
    """Where low_n_flag is TRUE, weak_ci_flag must also be TRUE."""
    bad = df[(df["low_n_flag"]) & (~df["weak_ci_flag"])]
    return GateResult(
        name="gate6_sample_quality_consistency",
        passed=(len(bad) == 0),
        n_violations=len(bad),
        detail=f"low_n=True but weak_ci=False in {len(bad)} rows",
    )


def soft_gate_mean_vs_median(df: pd.DataFrame) -> GateResult:
    """Soft gate: mean_realized_cents >= median_realized_cents for positive-skewed groups.
    Logged but does NOT block os.replace."""
    bad = df[df["mean_realized_cents"] < df["median_realized_cents"] - 1e-9]
    return GateResult(
        name="soft_gate_mean_vs_median",
        passed=(len(bad) == 0),
        n_violations=len(bad),
        detail=f"mean<median in {len(bad)} rows (SOFT — not blocking)",
    )


def run_all_gates(
    on_disk_path: Path,
    rung0: pd.DataFrame,
    expected_cells: list[str],
) -> list[GateResult]:
    """
    C37 discipline: reload the .new parquet from disk and validate against
    the bytes that actually landed.
    """
    log.info(f"Reloading {on_disk_path} from disk for gate validation")
    df_disk = pd.read_parquet(on_disk_path)
    log.info(f"On-disk shape: {df_disk.shape}")

    gates = [
        gate1_row_count(df_disk, len(expected_cells)),
        gate2_cell_coverage(df_disk, expected_cells),
        gate3_hit_rate_monotonicity(df_disk),
        gate4_realized_cents_bounds(df_disk, rung0),
        gate5_ci_ordering(df_disk),
        gate6_sample_quality_consistency(df_disk),
        soft_gate_mean_vs_median(df_disk),
    ]
    return gates


# ---------------------------------------------------------------------------
# Output I/O + sidecars
# ---------------------------------------------------------------------------


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_meta_sidecar(meta_path: Path, result: ProducerResult) -> None:
    meta = {
        "output_sha256": result.output_sha256,
        "output_bytes": result.output_bytes,
        "input_sha256": result.input_sha256,
        "rows_emitted": result.rows_emitted,
        "cells_covered": result.cells_covered,
        "thresholds_covered": result.thresholds_covered,
        "run_started_at_et": result.run_started_at_et,
        "run_completed_at_et": result.run_completed_at_et,
        "phase": "A_SKELETON",
        "spec": "docs/rung1_strategy_evaluation_spec.md v0.1",
        "spec_commit": "92198d64",
        "rung0_input_commit": "5ca2d89c",
        "gates": [
            {"name": g.name, "passed": g.passed, "n_violations": g.n_violations, "detail": g.detail}
            for g in result.gate_results
        ],
    }
    meta_path.write_text(json.dumps(meta, indent=2, default=str))


def write_validation_report(
    report_path: Path,
    df_out: pd.DataFrame,
    result: ProducerResult,
) -> None:
    """
    Phase A: minimal validation report. Phase B will fill in the headline
    top-10s, per-cell recommendations, threshold curves, sample-quality
    summary (spec Section 5).
    """
    lines = [
        "# Rung 1 Strategy Evaluation — Validation Report",
        "",
        f"**Phase:** A (skeleton with stub statistics)",
        f"**Run completed:** {result.run_completed_at_et}",
        f"**Spec:** docs/rung1_strategy_evaluation_spec.md v0.1 (commit 92198d64)",
        f"**Rung 0 input:** sha256 {result.input_sha256}",
        f"**Output sha256:** {result.output_sha256}",
        f"**Output bytes:** {result.output_bytes}",
        "",
        "## Gate results",
        "",
        "| Gate | Passed | N violations | Detail |",
        "|---|---|---|---|",
    ]
    for g in result.gate_results:
        passed_mark = "PASS" if g.passed else "FAIL"
        lines.append(f"| {g.name} | {passed_mark} | {g.n_violations} | {g.detail} |")

    lines += [
        "",
        "## Counts",
        "",
        f"- Rows emitted: {result.rows_emitted}",
        f"- Cells covered: {result.cells_covered}",
        f"- Thresholds covered: {result.thresholds_covered}",
        "",
        "## Phase A note",
        "",
        "This is the Phase A skeleton run. Statistical metrics (mean/median/std/Sharpe/Sortino "
        "and their CIs) are computed with placeholder logic. Real Wilson CIs and BCa bootstrap "
        "will replace the stubs in Phase B. The architecture and C37 discipline are validated by "
        "this run; gate passes here confirm the pipeline is structurally sound and ready for the "
        "statistics layer.",
    ]
    report_path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Rung 1 producer (Phase A skeleton)")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--phase", type=int, default=3, choices=[1, 2, 3])
    args = parser.parse_args()

    started_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")
    log.info(f"Rung 1 producer (Phase A SKELETON) starting at {started_at}")
    log.info(f"Phase: {args.phase}")

    # Load Rung 0
    rung0_full = load_rung0(args.input)
    input_sha = sha256_of_file(args.input)
    log.info(f"Loaded Rung 0: {len(rung0_full)} N's, sha256 {input_sha[:16]}…")

    # Compute corpus_active_days ONCE on the FULL unfiltered corpus per G22-aligned
    # spec Section 3.1. This is the operational total span denominator for
    # daily_opportunity_rate (N's-per-day) — must NOT be recomputed on filtered slices.
    corpus_active_days = compute_corpus_active_days(rung0_full)
    log.info(f"Full-corpus active days: {corpus_active_days} (denominator for N's-per-day)")

    # Phase filter
    rung0 = filter_by_phase(rung0_full, args.phase)
    expected_cells = sorted(rung0["cell_key"].unique().tolist())
    log.info(f"Filtered to {len(rung0)} N's, {len(expected_cells)} cells")

    # Build output
    df_out = build_output(rung0, corpus_active_days)

    # Write .new
    args.output_dir.mkdir(parents=True, exist_ok=True)
    final_path = args.output_dir / DEFAULT_OUTPUT_FILE
    new_path = args.output_dir / f"{DEFAULT_OUTPUT_FILE}.new"
    log.info(f"Writing .new to {new_path}")
    df_out.to_parquet(new_path, compression="snappy", index=False)

    # C37: reload .new from disk and run gates
    gate_results = run_all_gates(new_path, rung0, expected_cells)
    for g in gate_results:
        marker = "PASS" if g.passed else "FAIL"
        log.info(f"  Gate {g.name}: {marker} (n_violations={g.n_violations}) {g.detail}")

    # Decide os.replace
    hard_gates = [g for g in gate_results if not g.name.startswith("soft_")]
    all_hard_pass = all(g.passed for g in hard_gates)

    if not all_hard_pass:
        log.error("HARD GATE FAILURE — halting; .new preserved at " + str(new_path))
        DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        halt_log = DEFAULT_LOG_DIR / f"phaseA_halted_{datetime.now(ET).strftime('%Y%m%dT%H%M%SZ')}.log"
        halt_log.write_text("\n".join(
            f"{g.name}: passed={g.passed} n_violations={g.n_violations} detail={g.detail}"
            for g in gate_results
        ) + "\n")
        log.error(f"Halt log written to {halt_log}")
        return 1

    # All hard gates pass → atomic replace
    log.info(f"All hard gates PASS — performing os.replace({new_path} → {final_path})")
    os.replace(new_path, final_path)

    # Build sidecars from on-disk final
    output_sha = sha256_of_file(final_path)
    output_bytes = final_path.stat().st_size
    completed_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")

    result = ProducerResult(
        rows_emitted=len(df_out),
        cells_covered=len(expected_cells),
        thresholds_covered=len(THRESHOLD_GRID_CENTS),
        gate_results=gate_results,
        output_sha256=output_sha,
        output_bytes=output_bytes,
        run_started_at_et=started_at,
        run_completed_at_et=completed_at,
        input_sha256=input_sha,
    )

    write_meta_sidecar(args.output_dir / DEFAULT_META_FILE, result)
    write_validation_report(args.output_dir / DEFAULT_REPORT_FILE, df_out, result)

    log.info(f"Phase A complete. Output sha256: {output_sha}")
    log.info(f"Output: {final_path} ({output_bytes} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
