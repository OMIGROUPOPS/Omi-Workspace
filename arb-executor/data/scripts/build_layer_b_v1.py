#!/usr/bin/env python3
"""Layer B v1 producer — exit-policy parameter sweep against Layer A v1 cells.

Implementation per arb-executor/docs/layer_b_spec.md (T31a, commits 0915d92 +
7ea70b1 + 6001d62).

Foundation pointers:
- T28 ea84e74 — G9 parquets
- T29 1398c39 — Layer A v1 producer (cell-key logic now in cell_key_helpers)
- T29 37a5216 — MANIFEST sha256 for cell_stats.parquet + sample_manifest.json
- T29 cf31903 — ANALYSIS_LIBRARY entry
- T21 faf51d9 — Layer A v1 PASS verdict
- 8174ec0 — cell_key_helpers refactor

Modes:
- --dry-run: load inputs, build policy grid, print work plan, exit. T31b-alpha.
- --test-cell KEY: run trajectory walk + policy evaluation on a single cell.
  Prints results, no parquet write. T31b-beta (NOT YET IMPLEMENTED).
- (no flag): full run across all substantial cells, write
  exit_policy_per_cell.parquet + visuals. T31b-gamma (NOT YET IMPLEMENTED).
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

import numpy as np
import pyarrow.parquet as pq

# Cell-key classification logic — single-sourced shared module per refactor 8174ec0.
from cell_key_helpers import (
    ENTRY_BANDS, SPREAD_BANDS, VOLUME_BANDS, REGIMES, CATEGORIES,
    categorize, entry_band_idx, spread_band_name,
    detect_match_start, regime_for_moment, volume_intensity_for_market,
)


# ============================================================
# Paths
# ============================================================

DUR_DIR = "/root/Omi-Workspace/arb-executor/data/durable"
LAYER_A_DIR = os.path.join(DUR_DIR, "layer_a_v1")
OUT_DIR = os.path.join(DUR_DIR, "layer_b_v1")
os.makedirs(OUT_DIR, exist_ok=True)

CELL_STATS_PATH = os.path.join(LAYER_A_DIR, "cell_stats.parquet")
SAMPLE_MANIFEST_PATH = os.path.join(LAYER_A_DIR, "sample_manifest.json")
CANDLES_PATH = os.path.join(DUR_DIR, "g9_candles.parquet")
META_PATH = os.path.join(DUR_DIR, "g9_metadata.parquet")

OUT_PARQUET = os.path.join(OUT_DIR, "exit_policy_per_cell.parquet")
LOG_PATH = os.path.join(OUT_DIR, "build_layer_b_v1.log")


# ============================================================
# Configuration
# ============================================================

# Cell scope thresholds per spec
MIN_N_MARKETS = 20          # T21 substantial-cell threshold
MIN_TRAJECTORIES_PER_CELL = 50   # Per-cell secondary threshold per spec Decision 2

# Settlement-zone exclusion per spec scope (T31a)
EXCLUDED_REGIMES = {"settlement_zone"}

# Scalar-market exclusion per T31a-patch (spec Decision 5 + Out-of-scope)
ALLOWED_RESULTS = {"yes", "no"}


# ============================================================
# Logging
# ============================================================

def log(msg, also_print=True):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    if also_print:
        print(line, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


# ============================================================
# Cell-key parsing
# ============================================================

def parse_cell_key(key):
    """Parse sample_manifest.json key into structured cell info.

    Format: {regime}__{entry_band_idx}__{spread_band}__{volume_intensity}__{category}
    Returns dict with regime, entry_band_idx, entry_band_lo, entry_band_hi,
    spread_band, volume_intensity, category. Returns None if malformed.
    """
    parts = key.split("__")
    if len(parts) != 5:
        return None
    regime, idx_str, spread_band, volume_intensity, category = parts
    try:
        idx = int(idx_str)
    except ValueError:
        return None
    if idx < 0 or idx >= len(ENTRY_BANDS):
        return None
    lo, hi = ENTRY_BANDS[idx]
    return {
        "regime": regime,
        "entry_band_idx": idx,
        "entry_band_lo": lo,
        "entry_band_hi": hi,
        "spread_band": spread_band,
        "volume_intensity": volume_intensity,
        "category": category,
    }


def channel_for_regime(regime):
    """Map regime to channel ('premarket' or 'in_match'). settlement_zone excluded per spec."""
    if regime in EXCLUDED_REGIMES:
        return None
    if regime == "premarket":
        return "premarket"
    if regime == "in_match":
        return "in_match"
    return None  # any other regime not in scope


# ============================================================
# Policy parameter grid
# ============================================================

# Per spec Decision 4
LIMIT_THRESHOLDS = [1, 2, 3, 5, 7, 10, 15, 20, 30]   # cents
TIME_STOPS = [0.5, 1, 5, 15, 30, 60, 120, 240]       # minutes; "settle" handled separately
TRAILING_OFFSETS = [1, 2, 3, 5, 7, 10, 15, 20]       # cents
LIMIT_TIMESTOP_THRESHOLDS = [3, 5, 10, 15, 20]       # cents
LIMIT_TIMESTOP_HORIZONS = [15, 30, 60, 120]          # minutes
LIMIT_TRAILING_THRESHOLDS = [5, 10, 15]              # cents
LIMIT_TRAILING_OFFSETS = [3, 5, 10]                  # cents


def build_policy_grid():
    """Build the full 55-policy parameter grid per spec Decision 4."""
    policies = []

    # Limit-exit (9)
    for thr in LIMIT_THRESHOLDS:
        policies.append({"type": "limit", "params": {"limit_c": thr}})

    # Time-stop (9: 8 finite horizons + settle)
    for hz in TIME_STOPS:
        policies.append({"type": "time_stop", "params": {"horizon_min": hz}})
    policies.append({"type": "time_stop", "params": {"horizon_min": "settle"}})

    # Trailing-stop (8)
    for off in TRAILING_OFFSETS:
        policies.append({"type": "trailing", "params": {"trail_c": off}})

    # Limit + time-stop (20)
    for thr in LIMIT_TIMESTOP_THRESHOLDS:
        for hz in LIMIT_TIMESTOP_HORIZONS:
            policies.append({"type": "limit_time_stop",
                             "params": {"limit_c": thr, "horizon_min": hz}})

    # Limit + trailing (9)
    for thr in LIMIT_TRAILING_THRESHOLDS:
        for off in LIMIT_TRAILING_OFFSETS:
            policies.append({"type": "limit_trailing",
                             "params": {"limit_c": thr, "trail_c": off}})

    return policies


# ============================================================
# Policy evaluation (T31b-beta — stubbed for alpha)
# ============================================================

def evaluate_policy(policy, forward_window_bid, forward_window_ask, settlement_value):
    """Evaluate a single policy against a forward window trajectory.

    NOT YET IMPLEMENTED in T31b-alpha — lands in T31b-beta with single-cell test.

    Args:
        policy: dict with 'type' and 'params'
        forward_window_bid: array of yes_bid_close from t+1 onward
        forward_window_ask: array of yes_ask_close from t+1 onward
        settlement_value: 1.0 (yes), 0.0 (no), or None if no settlement reached

    Returns:
        dict with 'outcome' ('fired'/'horizon_expired'/'settled_unfired'),
        'capture' (cents), 'time_to_fire' (minutes or None)
    """
    raise NotImplementedError("evaluate_policy: T31b-beta scope")


def walk_trajectory(ticker, candles_df, metadata_row, policies):
    """Walk forward windows for all moments in a ticker, evaluate all policies.

    NOT YET IMPLEMENTED in T31b-alpha — lands in T31b-beta with single-cell test.
    """
    raise NotImplementedError("walk_trajectory: T31b-beta scope")


# ============================================================
# Aggregation (T31b-gamma — stubbed for alpha)
# ============================================================

def aggregate_cell_results(cell_info, per_policy_results):
    """Aggregate per-trajectory policy outcomes into per-(cell, policy) summary rows.

    NOT YET IMPLEMENTED in T31b-alpha — lands in T31b-gamma with full run.
    """
    raise NotImplementedError("aggregate_cell_results: T31b-gamma scope")


def write_output_parquet(rows):
    """Write final exit_policy_per_cell.parquet.

    NOT YET IMPLEMENTED in T31b-alpha — lands in T31b-gamma with full run.
    """
    raise NotImplementedError("write_output_parquet: T31b-gamma scope")


def generate_visuals():
    """Generate per-(channel, category) summary PNGs.

    NOT YET IMPLEMENTED in T31b-alpha — lands in T31b-gamma with full run.
    """
    raise NotImplementedError("generate_visuals: T31b-gamma scope")


# ============================================================
# Dry-run: print work plan
# ============================================================

def dry_run():
    """Load inputs, build plan, print, exit. No g9_candles reads, no writes."""
    log("=" * 60)
    log("Layer B v1 producer — DRY-RUN mode (T31b-alpha)")
    log("=" * 60)

    # Load cell_stats
    log(f"Loading cell_stats from {CELL_STATS_PATH}")
    cell_stats = pq.read_table(CELL_STATS_PATH).to_pandas()
    log(f"  {len(cell_stats)} cells, {len(cell_stats.columns)} columns")

    # Load sample_manifest
    log(f"Loading sample_manifest from {SAMPLE_MANIFEST_PATH}")
    with open(SAMPLE_MANIFEST_PATH) as f:
        manifest = json.load(f)
    log(f"  {len(manifest)} cell entries")

    # Load metadata for result-column filtering
    log(f"Loading g9_metadata from {META_PATH}")
    meta_df = pq.read_table(META_PATH, columns=["ticker", "result"]).to_pandas()
    result_counts = meta_df["result"].value_counts(dropna=False).to_dict()
    log(f"  {len(meta_df)} markets, result counts: {result_counts}")

    # Build allowed-ticker set (yes/no only, scalars excluded)
    allowed_tickers = set(meta_df[meta_df["result"].isin(ALLOWED_RESULTS)]["ticker"].tolist())
    excluded_count = len(meta_df) - len(allowed_tickers)
    log(f"  Allowed tickers (result in {ALLOWED_RESULTS}): {len(allowed_tickers)}")
    log(f"  Excluded tickers (scalar or other): {excluded_count}")

    # Filter substantial cells
    sub_cells = cell_stats[cell_stats["n_markets"] >= MIN_N_MARKETS].copy()
    log(f"\nSubstantial cells (n_markets >= {MIN_N_MARKETS}): {len(sub_cells)}")

    # Filter substantial cells by channel scope (exclude settlement_zone)
    in_scope_cells = sub_cells[~sub_cells["regime"].isin(EXCLUDED_REGIMES)].copy()
    log(f"In-scope cells (excl. {EXCLUDED_REGIMES}): {len(in_scope_cells)}")

    # Per-channel breakdown
    log("\nPer-channel cell counts (in-scope, substantial):")
    by_channel = in_scope_cells.groupby("regime").size()
    for regime, n in by_channel.items():
        log(f"  {regime}: {n} cells")

    # Per-(channel, category) breakdown
    log("\nPer-(channel, category) cell counts:")
    by_cat = in_scope_cells.groupby(["regime", "category"]).size()
    for (regime, cat), n in by_cat.items():
        log(f"  {regime:18s} x {cat:10s}: {n}")

    # Build policy grid
    policies = build_policy_grid()
    log(f"\nPolicy grid: {len(policies)} policies")
    by_type = {}
    for p in policies:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    for ptype, n in by_type.items():
        log(f"  {ptype}: {n} policies")

    # Total (cell, policy) tuples
    total_tuples = len(in_scope_cells) * len(policies)
    log(f"\nTotal (cell, policy) tuples to evaluate: {total_tuples:,}")

    # Trajectory count estimate from sample_manifest
    log("\nTrajectory count estimate (from sample_manifest, in-scope cells only):")
    total_trajectories = 0
    cells_with_manifest = 0
    cells_below_threshold = 0
    cells_missing_manifest = 0
    cells_with_scalar_skips = 0

    for _, row in in_scope_cells.iterrows():
        # Reconstruct manifest key from cell_stats row
        # entry_band_idx = (entry_band_lo // 10) since bands are 10c wide starting at 0
        idx = row["entry_band_lo"] // 10
        key = f"{row['regime']}__{idx}__{row['spread_band']}__{row['volume_intensity']}__{row['category']}"
        if key not in manifest:
            cells_missing_manifest += 1
            continue
        cells_with_manifest += 1
        cell_tickers = manifest[key].get("tickers", [])
        # Filter to allowed-result tickers (excludes scalars per spec)
        allowed_in_cell = [t for t in cell_tickers if t in allowed_tickers]
        if len(allowed_in_cell) < len(cell_tickers):
            cells_with_scalar_skips += 1
        total_trajectories += len(allowed_in_cell)
        if len(allowed_in_cell) < MIN_TRAJECTORIES_PER_CELL:
            cells_below_threshold += 1

    log(f"  Cells with manifest match: {cells_with_manifest} / {len(in_scope_cells)}")
    log(f"  Cells missing from manifest: {cells_missing_manifest}")
    log(f"  Cells affected by scalar-ticker exclusion: {cells_with_scalar_skips}")
    log(f"  Cells below {MIN_TRAJECTORIES_PER_CELL}-trajectory threshold: {cells_below_threshold}")
    log(f"  Total trajectories (allowed only) across in-scope cells: {total_trajectories:,}")
    log(f"  Approx trajectory-policy evaluations: {total_trajectories * len(policies):,}")

    log("\n" + "=" * 60)
    log("DRY-RUN complete. No g9_candles reads, no parquet writes.")
    log("Next: T31b-beta single-cell test mode for trajectory-walk verification.")
    log("=" * 60)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Layer B v1 exit-policy parameter sweep")
    parser.add_argument("--dry-run", action="store_true", help="T31b-alpha: load inputs, print work plan, exit")
    parser.add_argument("--test-cell", type=str, default=None, help="T31b-beta: run on single cell (NOT YET IMPLEMENTED)")
    args = parser.parse_args()

    # Truncate log file at start of run
    open(LOG_PATH, "w").close()

    if args.dry_run:
        dry_run()
        return 0
    elif args.test_cell:
        log("--test-cell NOT YET IMPLEMENTED (T31b-beta scope)")
        return 1
    else:
        log("Full-run mode NOT YET IMPLEMENTED (T31b-gamma scope)")
        log("Use --dry-run for T31b-alpha work-plan output.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
