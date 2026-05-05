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

def evaluate_policy(policy, forward_bids_dollars, forward_asks_dollars,
                    forward_ts_unix, entry_ask_dollars, entry_ts_unix,
                    settlement_value_dollars, settlement_ts_unix):
    """Walk a forward window and determine policy outcome.

    Per spec Decision 3-5 (layer_b_spec.md). All price inputs in dollars (float64).
    Policy params come in cents; converted to dollars at function entry.

    Args:
        policy: dict with keys {type, params}. params is a dict whose
                threshold/offset values are integer cents and time values are int minutes.
        forward_bids_dollars: list/array of yes_bid_close values for minutes after entry,
                              indexed [0..N-1] where index 0 is the minute immediately
                              after entry_ts_unix.
        forward_asks_dollars: list/array of yes_ask_close values for the same minutes.
        forward_ts_unix: list/array of end_period_ts values for those minutes.
        entry_ask_dollars: yes_ask_close at entry minute (cross-the-spread entry).
        entry_ts_unix: end_period_ts at entry minute.
        settlement_value_dollars: 1.00 if result=='yes', 0.00 if result=='no'.
        settlement_ts_unix: settlement timestamp in unix seconds.

    Returns:
        dict with keys:
            outcome: 'fired' | 'horizon_expired' | 'settled_unfired'
            capture_dollars: realized capture in dollars (can be negative)
            time_to_fire_min: minutes from entry to fire (None if not fired)
    """
    ptype = policy['type']
    params = policy['params']

    DEFAULT_HORIZON_MIN = 240

    if ptype == 'time_stop':
        horizon_min = params['horizon_min']
    elif ptype == 'limit_time_stop':
        horizon_min = params['horizon_min']
    else:
        horizon_min = DEFAULT_HORIZON_MIN

    if horizon_min == 'settle' or horizon_min is None:
        horizon_cap_ts = settlement_ts_unix
    else:
        horizon_cap_ts = entry_ts_unix + int(horizon_min) * 60

    final_cap_ts = min(horizon_cap_ts, settlement_ts_unix)

    limit_dollars = params.get('limit_c', 0) / 100.0 if 'limit_c' in params else None
    trail_dollars = params.get('trail_c', 0) / 100.0 if 'trail_c' in params else None

    running_max_bid = entry_ask_dollars
    n = len(forward_bids_dollars)
    last_walked_idx = -1

    for i in range(n):
        t_i = forward_ts_unix[i]
        if t_i > final_cap_ts:
            break
        last_walked_idx = i

        bid_i = forward_bids_dollars[i]
        ask_i = forward_asks_dollars[i]

        if bid_i is None or ask_i is None:
            continue

        if bid_i > running_max_bid:
            running_max_bid = bid_i

        if limit_dollars is not None and ptype in ('limit', 'limit_time_stop', 'limit_trailing'):
            if bid_i >= entry_ask_dollars + limit_dollars:
                return {
                    'outcome': 'fired',
                    'capture_dollars': bid_i - entry_ask_dollars,
                    'time_to_fire_min': (t_i - entry_ts_unix) / 60.0,
                }

        if trail_dollars is not None and ptype in ('trailing', 'limit_trailing'):
            if bid_i <= running_max_bid - trail_dollars:
                return {
                    'outcome': 'fired',
                    'capture_dollars': bid_i - entry_ask_dollars,
                    'time_to_fire_min': (t_i - entry_ts_unix) / 60.0,
                }

        if ptype in ('time_stop', 'limit_time_stop'):
            if horizon_min != 'settle' and t_i >= entry_ts_unix + int(horizon_min) * 60:
                return {
                    'outcome': 'fired',
                    'capture_dollars': bid_i - entry_ask_dollars,
                    'time_to_fire_min': (t_i - entry_ts_unix) / 60.0,
                }

    if final_cap_ts >= settlement_ts_unix - 60:
        return {
            'outcome': 'settled_unfired',
            'capture_dollars': settlement_value_dollars - entry_ask_dollars,
            'time_to_fire_min': None,
        }
    else:
        if last_walked_idx >= 0:
            capture = forward_bids_dollars[last_walked_idx] - entry_ask_dollars
        else:
            capture = 0.0
        return {
            'outcome': 'horizon_expired',
            'capture_dollars': capture,
            'time_to_fire_min': None,
        }


def walk_trajectory(ticker, candles_df, metadata_row, target_cell_key,
                    policies, helpers):
    """Walk all moments in a ticker, identify cell-matching moments, evaluate all policies.

    Args:
        ticker: ticker string (for logging).
        candles_df: pandas DataFrame with columns
                    [end_period_ts, yes_bid_close, yes_ask_close, volume_fp]
                    sorted ascending by end_period_ts.
        metadata_row: pandas Series with fields {result, settlement_ts}. result must be 'yes' or 'no'.
        target_cell_key: cell key string in format
                         'regime__entry_band_idx__spread_band__volume_intensity__category'.
        policies: list of policy dicts.
        helpers: cell_key_helpers module.

    Returns:
        list of (moment_idx, policy_idx, outcome_dict) tuples for moments matching the target cell.
    """
    from datetime import datetime

    timestamps = candles_df['end_period_ts'].values
    volumes = candles_df['volume_fp'].values

    match_start_ts = helpers.detect_match_start(timestamps, volumes)
    volume_intensity = helpers.volume_intensity_for_market(volumes)
    category = helpers.categorize(ticker)

    settlement_ts_unix = int(
        datetime.fromisoformat(metadata_row['settlement_ts'].replace('Z', '+00:00')).timestamp()
    )
    settlement_value_dollars = 1.0 if metadata_row['result'] == 'yes' else 0.0

    target_parts = target_cell_key.split('__')
    if len(target_parts) != 5:
        raise ValueError(f'Bad target_cell_key shape: {target_cell_key!r}')
    target_regime, target_eb_str, target_sb, target_vi, target_cat = target_parts
    target_eb = int(target_eb_str)

    if category != target_cat or volume_intensity != target_vi:
        return []

    bids = candles_df['yes_bid_close'].values
    asks = candles_df['yes_ask_close'].values

    results = []
    n_moments = len(candles_df)

    for i in range(n_moments):
        t = int(timestamps[i])
        bid = bids[i]
        ask = asks[i]

        if bid is None or ask is None:
            continue
        try:
            bid_f = float(bid)
            ask_f = float(ask)
        except (TypeError, ValueError):
            continue

        regime = helpers.regime_for_moment(t, match_start_ts, settlement_ts_unix)
        eb = helpers.entry_band_idx(ask_f)
        sb = helpers.spread_band_name(bid_f, ask_f)

        if regime != target_regime or eb != target_eb or sb != target_sb:
            continue

        forward_bids = bids[i+1:]
        forward_asks = asks[i+1:]
        forward_ts = timestamps[i+1:]

        for p_idx, policy in enumerate(policies):
            outcome = evaluate_policy(
                policy=policy,
                forward_bids_dollars=forward_bids,
                forward_asks_dollars=forward_asks,
                forward_ts_unix=forward_ts,
                entry_ask_dollars=ask_f,
                entry_ts_unix=t,
                settlement_value_dollars=settlement_value_dollars,
                settlement_ts_unix=settlement_ts_unix,
            )
            results.append((i, p_idx, outcome))

    return results


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
    log(f"  Cells below {MIN_TRAJECTORIES_PER_CELL}-TICKER threshold: {cells_below_threshold}")
    log(f"    NOTE: This is the ticker-level proxy. The actual 50-TRAJECTORY threshold (per (ticker, entry_moment) tuple)")
    log(f"    is computed in T31b-beta after g9_candles reads. Per spec patch 3, threshold-check deferred from dry-run.")
    log(f"  Total trajectories (allowed only) across in-scope cells: {total_trajectories:,}")
    log(f"  Approx trajectory-policy evaluations: {total_trajectories * len(policies):,}")

    log("\n" + "=" * 60)
    log("DRY-RUN complete. No g9_candles reads, no parquet writes.")
    log("Next: T31b-beta single-cell test mode for trajectory-walk verification.")
    log("=" * 60)


# ============================================================
# Main
# ============================================================


def test_cell_mode(test_cell_key):
    """T31b-beta single-cell test mode. No parquet write, no visuals.

    Loads target cell from sample_manifest, walks all sampled tickers,
    aggregates per-policy outcomes, prints summary distribution + samples.
    """
    import json
    import sys
    import statistics
    from pathlib import Path
    import pyarrow.parquet as pq
    sys.path.insert(0, str(Path(__file__).parent))
    import cell_key_helpers as ckh

    log(f'=== T31b-beta test mode: cell {test_cell_key!r} ===')

    manifest_path = Path('data/durable/layer_a_v1/sample_manifest.json')
    with open(manifest_path) as f:
        manifest = json.load(f)
    if test_cell_key not in manifest:
        log(f'ABORT: cell {test_cell_key!r} not in sample_manifest')
        return
    entry = manifest[test_cell_key]
    tickers = entry['tickers']
    log(f'Cell n_total={entry["n_total"]} n_sampled={entry["n_sampled"]} '
        f'tickers_in_manifest={len(tickers)}')

    policies = build_policy_grid()
    log(f'Policy grid: {len(policies)} policies')

    meta_table = pq.read_table(
        'data/durable/g9_metadata.parquet',
        columns=['ticker', 'result', 'settlement_ts'],
        filters=[('ticker', 'in', tickers)],
    )
    meta_df = meta_table.to_pandas().set_index('ticker')

    per_policy_outcomes = {p_idx: [] for p_idx in range(len(policies))}
    skipped_scalar = 0
    skipped_missing_meta = 0
    skipped_empty_candles = 0
    total_entry_moments = 0

    for ticker in tickers:
        if ticker not in meta_df.index:
            skipped_missing_meta += 1
            continue
        meta_row = meta_df.loc[ticker]
        if meta_row['result'] not in ('yes', 'no'):
            skipped_scalar += 1
            continue

        candles_table = pq.read_table(
            'data/durable/g9_candles.parquet',
            columns=['ticker', 'end_period_ts', 'yes_bid_close', 'yes_ask_close', 'volume_fp'],
            filters=[('ticker', '=', ticker)],
        )
        candles_df = candles_table.to_pandas()
        if len(candles_df) == 0:
            skipped_empty_candles += 1
            continue
        candles_df = candles_df.sort_values('end_period_ts').reset_index(drop=True)

        ticker_results = walk_trajectory(
            ticker=ticker,
            candles_df=candles_df,
            metadata_row=meta_row,
            target_cell_key=test_cell_key,
            policies=policies,
            helpers=ckh,
        )

        moments_this_ticker = len(set(r[0] for r in ticker_results))
        total_entry_moments += moments_this_ticker
        log(f'  {ticker}: {moments_this_ticker} entry moments, '
            f'{len(ticker_results)} (moment, policy) pairs')

        for moment_idx, p_idx, outcome in ticker_results:
            per_policy_outcomes[p_idx].append(outcome)

    log(f'')
    log(f'=== Aggregate ===')
    log(f'Total entry moments across all tickers: {total_entry_moments}')
    log(f'Skipped scalar tickers: {skipped_scalar}')
    log(f'Skipped missing-metadata tickers: {skipped_missing_meta}')
    log(f'Skipped empty-candles tickers: {skipped_empty_candles}')
    log(f'')
    log(f'Trajectory threshold check (>= 50 moments): '
        f'{"PASS" if total_entry_moments >= 50 else "FAIL"}')
    log(f'')

    log(f'=== Per-policy capture distribution ===')
    log(f'{"policy":<40} {"n":>4} {"fire%":>6} {"hexp%":>6} {"sett%":>6} '
        f'{"cap_p10":>8} {"cap_p50":>8} {"cap_p90":>8} {"cap_max":>8}')

    for p_idx, policy in enumerate(policies):
        outcomes = per_policy_outcomes[p_idx]
        if not outcomes:
            continue
        n = len(outcomes)
        n_fired = sum(1 for o in outcomes if o['outcome'] == 'fired')
        n_hexp = sum(1 for o in outcomes if o['outcome'] == 'horizon_expired')
        n_sett = sum(1 for o in outcomes if o['outcome'] == 'settled_unfired')
        captures = sorted(o['capture_dollars'] for o in outcomes)

        def pct(vals, q):
            if not vals: return float('nan')
            i = int(q * (len(vals) - 1))
            return vals[i]

        cap_p10 = pct(captures, 0.10)
        cap_p50 = pct(captures, 0.50)
        cap_p90 = pct(captures, 0.90)
        cap_max = captures[-1] if captures else float('nan')

        label = f'{policy["type"]}:{policy["params"]}'[:38]
        log(f'{label:<40} {n:>4} '
            f'{100*n_fired/n:>5.1f}% {100*n_hexp/n:>5.1f}% {100*n_sett/n:>5.1f}% '
            f'{cap_p10:>+8.4f} {cap_p50:>+8.4f} {cap_p90:>+8.4f} {cap_max:>+8.4f}')

    log(f'')
    log(f'=== Sample fired/expired/settled outcomes from limit_c=5 policy ===')
    for p_idx, policy in enumerate(policies):
        if policy['type'] == 'limit' and policy['params'].get('limit_c') == 5:
            outcomes = per_policy_outcomes[p_idx]
            for label, target_outcome in [('fired', 'fired'),
                                          ('horizon_expired', 'horizon_expired'),
                                          ('settled_unfired', 'settled_unfired')]:
                samples = [o for o in outcomes if o['outcome'] == target_outcome][:3]
                log(f'  {label} samples (up to 3): {samples}')
            break


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
        test_cell_mode(args.test_cell)
        return
    
    else:
        log("Full-run mode NOT YET IMPLEMENTED (T31b-gamma scope)")
        log("Use --dry-run for T31b-alpha work-plan output.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
