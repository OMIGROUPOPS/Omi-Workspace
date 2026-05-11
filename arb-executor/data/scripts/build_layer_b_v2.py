#!/usr/bin/env python3
"""Layer B v2 producer — tick-level fill semantics, per-cell vectorized policy evaluation.

Implementation per docs/layer_b_v2_spec.md (commits e2197b7 + 164f732e).

Per LESSONS B25 (commit `033fb8a`): Layer B v1's `walk_trajectory` detects threshold
crosses at minute-boundary `yes_bid_close` candle prints, missing sub-minute bid
spikes that hit hypothetical resting sells. v2 folds forensic replay v1's tick-level
mechanism (commit `73de3a6`) back into the simulator at the source and generalizes to
the full non-settle premarket corpus (~12,455 (cell, policy) tuples vs forensic
replay v1's top-N 80 candidates).

Phases:
- --phase=1: single-candidate calibration probe (1 candidate × 100 moments). Target:
  ATP_MAIN 50-60 tight low / limit_c=30 must produce `capture_B_gross_mean` within
  $0.2610 ± $0.01 of the forensic replay v1 phase3 anchor (commit `73de3a6`
  `candidate_summary.parquet`, fill=0.757 / drift=0.093 / n_moments=2914). Runtime
  budget: <5 minutes. PHASE 1 IS THE SCOPE OF THIS COMMIT.
- --phase=2: single-cell × all ~53 non-settle policies × all moments. Pending separate
  single-concern commit. Mirrors forensic replay v1 phase2 but adds the
  vectorized-policy evaluation per spec Section 5.1.
- --phase=3: full corpus (~235 cells × ~53 policies × ~950 moments avg). Pending
  separate single-concern commit. Per-cell streaming, vectorized policy evaluation.

Per the spec's Coordination Point 2 STOP discipline: Phase 1 ships as one commit;
Phase 2 / Phase 3 land in subsequent single-concern commits gated on chat-side review.

Convention invariants inherited from forensic replay v1 spec Section 3.1 (commit
`a058212` Session 9 5,878-pair empirical probe):
- Entry-fill check: maker BID for yes is filled by `taker_side == "no"` trade.
- Exit-fill check: maker SELL for yes is filled by `taker_side == "yes"` trade.

Producer code structure mirrors `build_forensic_replay_v1.py` for v1-calibration
fidelity: the Phase 1 per-moment replay function reuses the exact 9-step procedure
that produced the Cat 11 anchor. Phase 1's job is to reproduce the rank-1
calibration anchor; Phase 2/3 introduce the new vectorized-policy architecture.
"""

import argparse
import glob
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from cell_key_helpers import (
    ENTRY_BANDS, SPREAD_BANDS, VOLUME_BANDS, REGIMES, CATEGORIES,
    categorize, entry_band_idx, spread_band_name,
    detect_match_start, regime_for_moment, volume_intensity_for_market,
)


# ============================================================
# Paths
# ============================================================

DUR_DIR = "/root/Omi-Workspace/arb-executor/data/durable"
OUT_DIR = os.path.join(DUR_DIR, "layer_b_v2")
PROBE_DIR = os.path.join(OUT_DIR, "probe")
LAYER_A_DIR = os.path.join(DUR_DIR, "layer_a_v1")
LAYER_B_PARQUET = os.path.join(DUR_DIR, "layer_b_v1", "exit_policy_per_cell.parquet")
SAMPLE_MANIFEST = os.path.join(LAYER_A_DIR, "sample_manifest.json")
TRADES_PARQUET = os.path.join(DUR_DIR, "g9_trades.parquet")
CANDLES_PARQUET = os.path.join(DUR_DIR, "g9_candles.parquet")
META_PARQUET = os.path.join(DUR_DIR, "g9_metadata.parquet")

LOG_PATH_TEMPLATE = "{out_dir}/build_log.txt"

# Phase 1 budget: 100 moments, deterministic chronological order
PHASE1_MOMENT_BUDGET = 100


# ============================================================
# Logging
# ============================================================

def log_setup(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    return LOG_PATH_TEMPLATE.format(out_dir=out_dir)


def log(msg, log_path, also_print=True):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    if also_print:
        print(line, flush=True)
    with open(log_path, "a") as f:
        f.write(line + "\n")


# ============================================================
# Phase 1 candidate selection — rank-1 deployable per Cat 11
# ============================================================

def select_phase1_candidate():
    """Return the rank-1 deployable candidate per Cat 11: ATP_MAIN 50-60 tight low / limit_c=30.

    Selection criteria:
    - channel = premarket
    - n_simulated >= 50
    - category = ATP_MAIN, entry_band 50-60, spread = tight, volume_intensity = low
    - policy_type = limit, limit_c = 30

    Anchor: phase3/candidate_summary.parquet shows replay_capture_B_net_mean = $0.2610,
    fill_rate = 0.757, cell_drift_rate_at_fill = 0.093, n_replay_moments = 2914.
    """
    t = pq.read_table(LAYER_B_PARQUET).to_pandas()
    pre = t[(t["channel"] == "premarket") & (t["n_simulated"] >= 50)].copy()

    match = pre[
        (pre["category"] == "ATP_MAIN")
        & (pre["entry_band_lo"] == 50)
        & (pre["entry_band_hi"] == 60)
        & (pre["spread_band"] == "tight")
        & (pre["volume_intensity"] == "low")
        & (pre["policy_type"] == "limit")
    ].copy()

    def is_target(row):
        try:
            params = json.loads(row["policy_params"])
        except Exception:
            return False
        return params.get("limit_c") == 30

    match["is_target"] = match.apply(is_target, axis=1)
    hit = match[match["is_target"]]
    if len(hit) != 1:
        raise SystemExit(
            f"FAIL: Phase 1 candidate selector returned {len(hit)} rows, expected 1 "
            f"(ATP_MAIN 50-60 tight low / limit_c=30)"
        )

    return hit.iloc[0]


def manifest_key_for_candidate(c):
    """Build the sample_manifest key from a candidate row."""
    idx = int(c["entry_band_lo"] // 10)
    return f"premarket__{idx}__{c['spread_band']}__{c['volume_intensity']}__{c['category']}"


def candidate_id(c):
    """Build a stable candidate_id string for output rows."""
    return (
        f"{c['channel']}__{c['category']}__"
        f"{int(c['entry_band_lo'])}-{int(c['entry_band_hi'])}__"
        f"{c['spread_band']}__{c['volume_intensity']}__"
        f"{c['policy_type']}__{c['policy_params']}"
    )


# ============================================================
# Per-ticker data loading (mirrors forensic_replay_v1 producer)
# ============================================================

def load_ticker_candles(ticker):
    """Read g9_candles for one ticker via predicate pushdown.
    Returns sorted DataFrame or None if no candles."""
    table = pq.read_table(
        CANDLES_PARQUET,
        columns=["ticker", "end_period_ts", "yes_bid_close", "yes_ask_close", "volume_fp"],
        filters=[("ticker", "=", ticker)],
    )
    if table.num_rows == 0:
        return None
    return table.to_pandas().sort_values("end_period_ts").reset_index(drop=True)


def load_ticker_trades(ticker, start_ts_unix=None):
    """Read g9_trades for one ticker via predicate pushdown.

    Per Phase 1 timestamp invariant (forensic_replay_v1 commit `43ae049`):
    `created_time` is microsecond-precision timestamp. Convert via per-row
    `.timestamp()` to avoid the microsecond-vs-nanosecond bug where
    `pd.to_datetime().astype('int64') // 10**9` produces values 1000× too small.
    """
    table = pq.read_table(
        TRADES_PARQUET,
        columns=["ticker", "created_time", "taker_side", "yes_price_dollars",
                 "no_price_dollars", "count_fp"],
        filters=[("ticker", "=", ticker)],
    )
    if table.num_rows == 0:
        return None
    df = table.to_pandas()
    df["created_time_ts"] = pd.to_datetime(df["created_time"]).map(lambda x: int(x.timestamp()))
    df = df.sort_values("created_time_ts").reset_index(drop=True)
    if start_ts_unix is not None:
        df = df[df["created_time_ts"] >= start_ts_unix].reset_index(drop=True)
    return df


def load_market_settlement(ticker):
    """Read g9_metadata for one ticker. Returns (settlement_ts_unix, settlement_value, result)
    or None if missing / scalar."""
    table = pq.read_table(
        META_PARQUET,
        columns=["ticker", "result", "settlement_ts"],
        filters=[("ticker", "=", ticker)],
    )
    if table.num_rows == 0:
        return None
    row = table.to_pandas().iloc[0]
    if row["result"] not in ("yes", "no"):
        return None
    settle_ts = int(
        datetime.fromisoformat(row["settlement_ts"].replace("Z", "+00:00")).timestamp()
    )
    settle_value = 1.0 if row["result"] == "yes" else 0.0
    return (settle_ts, settle_value, row["result"])


# ============================================================
# Cell-state computation at a minute
# ============================================================

def cell_state_at_minute(candles_df, minute_ts, match_start_ts, settlement_ts_unix, ticker):
    """Compute the cell state at a given minute_ts. Returns dict or None."""
    row = candles_df[candles_df["end_period_ts"] == minute_ts]
    if len(row) == 0:
        return None
    row = row.iloc[0]
    bid = row["yes_bid_close"]
    ask = row["yes_ask_close"]
    if bid is None or ask is None:
        return None
    try:
        bid_f = float(bid)
        ask_f = float(ask)
    except (TypeError, ValueError):
        return None

    regime = regime_for_moment(int(minute_ts), match_start_ts, settlement_ts_unix)
    eb = entry_band_idx(ask_f)
    sb = spread_band_name(bid_f, ask_f)
    vi = volume_intensity_for_market(candles_df["volume_fp"].values)
    cat = categorize(ticker)

    return {
        "regime": regime, "entry_band_idx": eb,
        "spread_band": sb, "volume_intensity": vi, "category": cat,
        "yes_bid_close": bid_f, "yes_ask_close": ask_f,
    }


def cell_key_str(cell_state):
    if cell_state is None:
        return None
    return (
        f"{cell_state['regime']}__{cell_state['entry_band_idx']}__"
        f"{cell_state['spread_band']}__{cell_state['volume_intensity']}__"
        f"{cell_state['category']}"
    )


# ============================================================
# Per-moment 9-step replay (Phase 1: limit-policy semantics)
# ============================================================

def replay_one_moment(ticker, candles_df, trades_df, T0_unix, T0_cell,
                     policy_type, policy_params,
                     settlement_ts_unix, settlement_value,
                     match_start_ts, log_path, log_warnings):
    """Execute spec Section 3.1 steps 2-7 for one (ticker, T0) entry moment.

    Per Phase 1 scope: limit-policy semantics on a single policy. Mirrors
    forensic_replay_v1's `replay_one_moment` (commit `a058212`); v2 Phase 1's job
    is to reproduce v1 phase3 anchor values for the limit_c=30 rank-1 candidate.
    Phase 2/3 extend to vectorized-policy evaluation across the ~53 non-settle
    policies on each cell.

    Returns a row dict suitable for Output 1 (replay_tape_phase1.parquet) schema.
    """
    our_bid_price = T0_cell["yes_bid_close"]
    limit_c = policy_params.get("limit_c", 10)
    horizon_min = policy_params.get("horizon_min", 240)
    if horizon_min == "settle":
        horizon_cap_ts = settlement_ts_unix
    else:
        horizon_cap_ts = T0_unix + int(horizon_min * 60)
    entry_timeout_ts = T0_unix + 240 * 60

    # Step 3: walk trades forward looking for fill (taker_side == "no" hits our bid)
    fill_time_unix = None
    fill_price = None
    for _, trade in trades_df.iterrows():
        t_unix = int(trade["created_time_ts"])
        if t_unix > entry_timeout_ts or t_unix > settlement_ts_unix:
            break
        if trade["taker_side"] == "no" and float(trade["yes_price_dollars"]) <= our_bid_price:
            fill_time_unix = t_unix
            fill_price = our_bid_price
            break

    row = {
        "candidate_id": None,
        "ticker": ticker,
        "T0_unix": T0_unix,
        "T0_cell_key": cell_key_str(T0_cell),
        "fill_time_unix": fill_time_unix,
        "fill_price_dollars": fill_price,
        "fill_time_cell_key": None,
        "cell_drift_at_fill": None,
        "time_to_fill_minutes": None,
        "outcome_A": "unfilled" if fill_time_unix is None else None,
        "capture_A_gross_dollars": None,
        "time_to_exit_A_minutes": None,
        "outcome_B": "unfilled" if fill_time_unix is None else None,
        "capture_B_gross_dollars": None,
        "time_to_exit_B_minutes": None,
    }

    if fill_time_unix is None:
        return row

    row["time_to_fill_minutes"] = (fill_time_unix - T0_unix) / 60.0

    # Step 4: record fill-time cell state
    fill_minute_ts = (fill_time_unix // 60) * 60
    fill_time_cell = cell_state_at_minute(
        candles_df, fill_minute_ts, match_start_ts, settlement_ts_unix, ticker
    )
    row["fill_time_cell_key"] = cell_key_str(fill_time_cell) if fill_time_cell else None
    row["cell_drift_at_fill"] = (row["T0_cell_key"] != row["fill_time_cell_key"])

    # Step 5: Scenario A (post-time anchor) and Scenario B (fill-time anchor) targets
    scenario_A_target = fill_price + limit_c / 100.0
    if fill_time_cell is not None:
        scenario_B_target = fill_time_cell["yes_ask_close"] + limit_c / 100.0
    else:
        scenario_B_target = scenario_A_target

    # Step 6: walk trades forward from fill_time looking for the kiss
    horizon_for_exit_ts = min(horizon_cap_ts, settlement_ts_unix)
    exit_A_time = None
    exit_A_price = None
    exit_B_time = None
    exit_B_price = None

    post_fill_trades = trades_df[trades_df["created_time_ts"] >= fill_time_unix].reset_index(drop=True)
    for _, trade in post_fill_trades.iterrows():
        t_unix = int(trade["created_time_ts"])
        if t_unix > horizon_for_exit_ts:
            break
        if trade["taker_side"] != "yes":
            continue
        yes_price = float(trade["yes_price_dollars"])
        if exit_A_time is None and yes_price >= scenario_A_target:
            exit_A_time = t_unix
            exit_A_price = yes_price
        if exit_B_time is None and yes_price >= scenario_B_target:
            exit_B_time = t_unix
            exit_B_price = yes_price
        if exit_A_time is not None and exit_B_time is not None:
            break

    # Step 7: resolve outcomes
    if exit_A_time is not None:
        row["outcome_A"] = "fired_at_target"
        row["capture_A_gross_dollars"] = exit_A_price - fill_price
        row["time_to_exit_A_minutes"] = (exit_A_time - fill_time_unix) / 60.0
    elif horizon_for_exit_ts >= settlement_ts_unix - 60:
        row["outcome_A"] = "settled_unfired"
        row["capture_A_gross_dollars"] = settlement_value - fill_price
        row["time_to_exit_A_minutes"] = None
    else:
        row["outcome_A"] = "horizon_expired"
        row["capture_A_gross_dollars"] = None
        row["time_to_exit_A_minutes"] = None

    if exit_B_time is not None:
        row["outcome_B"] = "fired_at_target"
        row["capture_B_gross_dollars"] = exit_B_price - fill_price
        row["time_to_exit_B_minutes"] = (exit_B_time - fill_time_unix) / 60.0
    elif horizon_for_exit_ts >= settlement_ts_unix - 60:
        row["outcome_B"] = "settled_unfired"
        row["capture_B_gross_dollars"] = settlement_value - fill_price
        row["time_to_exit_B_minutes"] = None
    else:
        row["outcome_B"] = "horizon_expired"
        row["capture_B_gross_dollars"] = None
        row["time_to_exit_B_minutes"] = None

    # Step 8: fees deferred to T32 (Layer C v1); v2 outputs gross only
    return row


# ============================================================
# Phase 1 main
# ============================================================

def phase1():
    """Phase 1 calibration probe: rank-1 candidate × first 100 entry moments (chronological).

    Calibration target: capture_B_gross_mean within $0.2610 ± $0.01 of the forensic
    replay v1 phase3 anchor for ATP_MAIN 50-60 tight low / limit_c=30.
    """
    out_dir = PROBE_DIR
    log_path = log_setup(out_dir)
    t_start = time.time()

    log("=" * 60, log_path)
    log("Layer B v2 — Phase 1 calibration probe", log_path)
    log("=" * 60, log_path)

    c = select_phase1_candidate()
    cid = candidate_id(c)
    mkey = manifest_key_for_candidate(c)
    log(f"Candidate: {cid}", log_path)
    log(f"Manifest key: {mkey}", log_path)
    log(f"Layer B v1 simulated capture_mean=${c['capture_mean']:.4f}, fire_rate={c['fire_rate']:.3f}",
        log_path)
    log(f"Policy: type={c['policy_type']}, params={c['policy_params']}", log_path)
    log("Calibration target: capture_B_gross_mean within $0.2610 ± $0.01 "
        "(anchor: forensic replay v1 phase3 ATP_MAIN 50-60 tight low / limit_c=30 "
        "= $0.2610 / fill=0.757 / drift=0.093 / n=2914).", log_path)
    policy_type = c["policy_type"]
    policy_params = json.loads(c["policy_params"])

    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)
    if mkey not in manifest:
        log(f"ABORT: manifest key {mkey} not found", log_path)
        sys.exit(1)
    tickers = manifest[mkey]["tickers"]
    log(f"Tickers in manifest: {len(tickers)}", log_path)

    rows = []
    moments_collected = 0
    skipped_meta = 0
    skipped_no_candles = 0
    skipped_no_trades = 0
    tickers_processed = 0

    for ticker in tickers:
        if moments_collected >= PHASE1_MOMENT_BUDGET:
            break
        tickers_processed += 1
        log(f"Ticker {tickers_processed}/{len(tickers)}: {ticker} "
            f"(moments so far: {moments_collected})", log_path)

        meta = load_market_settlement(ticker)
        if meta is None:
            skipped_meta += 1
            continue
        settlement_ts_unix, settlement_value, _ = meta

        candles_df = load_ticker_candles(ticker)
        if candles_df is None or len(candles_df) == 0:
            skipped_no_candles += 1
            continue

        timestamps = candles_df["end_period_ts"].values
        volumes = candles_df["volume_fp"].values
        match_start_ts = detect_match_start(timestamps, volumes)

        matching_moments = []
        for i in range(len(candles_df)):
            t = int(timestamps[i])
            row_c = candles_df.iloc[i]
            if row_c["yes_bid_close"] is None or row_c["yes_ask_close"] is None:
                continue
            try:
                bid_f = float(row_c["yes_bid_close"])
                ask_f = float(row_c["yes_ask_close"])
            except (TypeError, ValueError):
                continue

            regime = regime_for_moment(t, match_start_ts, settlement_ts_unix)
            eb = entry_band_idx(ask_f)
            sb = spread_band_name(bid_f, ask_f)
            vi = volume_intensity_for_market(volumes)
            cat = categorize(ticker)

            target_parts = mkey.split("__")
            target_regime, target_eb_str, target_sb, target_vi, target_cat = target_parts
            if (regime == target_regime
                    and eb == int(target_eb_str)
                    and sb == target_sb
                    and vi == target_vi
                    and cat == target_cat):
                matching_moments.append((i, t, bid_f, ask_f, regime, eb, sb, vi, cat))

        if not matching_moments:
            continue

        trades_df = load_ticker_trades(ticker, start_ts_unix=int(timestamps[0]))
        if trades_df is None:
            skipped_no_trades += 1
            continue

        for (i, t, bid_f, ask_f, regime, eb, sb, vi, cat) in matching_moments:
            if moments_collected >= PHASE1_MOMENT_BUDGET:
                break
            T0_cell = {
                "regime": regime, "entry_band_idx": eb,
                "spread_band": sb, "volume_intensity": vi, "category": cat,
                "yes_bid_close": bid_f, "yes_ask_close": ask_f,
            }
            forward_trades = trades_df[trades_df["created_time_ts"] >= t].reset_index(drop=True)
            row = replay_one_moment(
                ticker=ticker, candles_df=candles_df, trades_df=forward_trades,
                T0_unix=t, T0_cell=T0_cell,
                policy_type=policy_type, policy_params=policy_params,
                settlement_ts_unix=settlement_ts_unix, settlement_value=settlement_value,
                match_start_ts=match_start_ts,
                log_path=log_path, log_warnings=True,
            )
            row["candidate_id"] = cid
            rows.append(row)
            moments_collected += 1

    elapsed = time.time() - t_start
    log("", log_path)
    log("=" * 60, log_path)
    log(f"Phase 1 complete. Runtime: {elapsed:.1f}s ({elapsed/60:.2f} min)", log_path)
    log(f"Moments collected: {moments_collected}/{PHASE1_MOMENT_BUDGET}", log_path)
    log(f"Tickers processed: {tickers_processed}/{len(tickers)}", log_path)
    log(f"Skipped (no metadata or scalar): {skipped_meta}", log_path)
    log(f"Skipped (no candles): {skipped_no_candles}", log_path)
    log(f"Skipped (no trades): {skipped_no_trades}", log_path)
    log("=" * 60, log_path)

    df = pd.DataFrame(rows)
    log("", log_path)
    log("=== Outcome distribution ===", log_path)
    log(f"  Scenario A: {df['outcome_A'].value_counts().to_dict()}", log_path)
    log(f"  Scenario B: {df['outcome_B'].value_counts().to_dict()}", log_path)
    fill_count = int(df["fill_time_unix"].notna().sum())
    log(f"  Fill rate: {fill_count}/{len(df)} = {fill_count/max(1,len(df)):.3f}", log_path)
    if fill_count > 0:
        drift_count = int(df["cell_drift_at_fill"].sum())
        log(f"  Cell drift at fill: {drift_count}/{fill_count} = {drift_count/fill_count:.3f}",
            log_path)

    captures_A = df["capture_A_gross_dollars"].dropna()
    captures_B = df["capture_B_gross_dollars"].dropna()
    if len(captures_A) > 0:
        log(f"  Scenario A capture: n={len(captures_A)}, mean=${captures_A.mean():.4f}, "
            f"median=${captures_A.median():.4f}, min=${captures_A.min():.4f}, "
            f"max=${captures_A.max():.4f}", log_path)
    if len(captures_B) > 0:
        log(f"  Scenario B capture: n={len(captures_B)}, mean=${captures_B.mean():.4f}, "
            f"median=${captures_B.median():.4f}, min=${captures_B.min():.4f}, "
            f"max=${captures_B.max():.4f}", log_path)

    log(f"  Layer B v1 simulated capture_mean: ${c['capture_mean']:.4f}", log_path)
    log(f"  Calibration anchor (v1 phase3 B_net_mean): $0.2610", log_path)
    if len(captures_B) > 0:
        delta = captures_B.mean() - 0.2610
        log(f"  Calibration delta (v2 B - anchor): ${delta:+.4f} "
            f"(tolerance ±$0.01: {'PASS' if abs(delta) <= 0.01 else 'FAIL'})", log_path)

    out_path = os.path.join(out_dir, "replay_tape_phase1.parquet")
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, out_path, compression="snappy")
    log(f"Wrote {len(df)} rows to {out_path}", log_path)
    log(f"Output size: {os.path.getsize(out_path):,} bytes", log_path)

    calib_delta = float(captures_B.mean() - 0.2610) if len(captures_B) > 0 else None
    calib_pass = bool(calib_delta is not None and abs(calib_delta) <= 0.01)

    summary = {
        "phase": 1,
        "spec_commits": ["e2197b7", "164f732e"],
        "calibration_anchor": {
            "source": "data/durable/forensic_replay_v1/phase3/candidate_summary.parquet (commit 73de3a6)",
            "cell": "ATP_MAIN 50-60 tight low",
            "policy": "limit / limit_c=30",
            "anchor_capture_B_net_mean": 0.2610,
            "anchor_fill_rate": 0.757,
            "anchor_cell_drift_rate": 0.093,
            "anchor_n_replay_moments": 2914,
        },
        "candidate_id": cid,
        "manifest_key": mkey,
        "moments_collected": int(moments_collected),
        "moments_budget": PHASE1_MOMENT_BUDGET,
        "tickers_processed": tickers_processed,
        "skipped_meta": skipped_meta,
        "skipped_no_candles": skipped_no_candles,
        "skipped_no_trades": skipped_no_trades,
        "runtime_seconds": round(elapsed, 1),
        "layer_b_v1_capture_mean_simulated": float(c["capture_mean"]),
        "layer_b_v1_fire_rate_simulated": float(c["fire_rate"]),
        "layer_b_v1_n_simulated": int(c["n_simulated"]),
        "fill_rate": float(fill_count / max(1, len(df))),
        "scenario_A_outcomes": df["outcome_A"].value_counts().to_dict(),
        "scenario_B_outcomes": df["outcome_B"].value_counts().to_dict(),
        "scenario_A_capture_mean": float(captures_A.mean()) if len(captures_A) > 0 else None,
        "scenario_B_capture_mean": float(captures_B.mean()) if len(captures_B) > 0 else None,
        "cell_drift_rate_at_fill": float(df["cell_drift_at_fill"].sum() / max(1, fill_count))
            if fill_count > 0 else None,
        "calibration_delta": calib_delta,
        "calibration_pass": calib_pass,
    }
    summary_path = os.path.join(out_dir, "run_summary_phase1.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log(f"Wrote summary to {summary_path}", log_path)
    log(f"Phase 1 calibration verdict: {'PASS' if calib_pass else 'FAIL'} "
        f"(delta {calib_delta:+.4f} vs ±0.01 tolerance)", log_path)
    log("=" * 60, log_path)


# ============================================================
# Phase 2 / Phase 3 — pending separate single-concern commits
# ============================================================

# ============================================================
# Phase 2: vectorized per-policy semantics (per spec Section 3.4)
# ============================================================

def build_cell_policy_grid(c):
    """Return list of non-settle policies for the cell of candidate c.

    Reads from Layer B v1 exit_policy_per_cell.parquet, filters to the same cell key,
    excludes settle-horizon time_stop / limit_time_stop per v2 scope. Returns
    (grid, grid_df) where grid is a list of policy dicts and grid_df is the raw
    parquet rows for output schema reuse.
    """
    t = pq.read_table(LAYER_B_PARQUET).to_pandas()
    cell = t[
        (t["channel"] == "premarket")
        & (t["category"] == c["category"])
        & (t["entry_band_lo"] == c["entry_band_lo"])
        & (t["entry_band_hi"] == c["entry_band_hi"])
        & (t["spread_band"] == c["spread_band"])
        & (t["volume_intensity"] == c["volume_intensity"])
    ].copy()

    def _is_settle(row):
        try:
            params = json.loads(row["policy_params"])
        except Exception:
            return False
        return params.get("horizon_min") == "settle"

    cell["_is_settle"] = cell.apply(_is_settle, axis=1)
    cell = cell[~cell["_is_settle"]].copy().drop(columns=["_is_settle"]).reset_index(drop=True)

    grid = []
    for idx, row in cell.iterrows():
        params = json.loads(row["policy_params"])
        grid.append({
            "idx": idx,
            "policy_type": row["policy_type"],
            "policy_params": params,
            "policy_params_str": row["policy_params"],
            "limit_c": params.get("limit_c"),
            "trail_c": params.get("trail_c"),
            "horizon_min": params.get("horizon_min"),
        })
    return grid, cell


def evaluate_moment_vectorized(ticker, candles_df, trades_df, T0_unix, T0_cell,
                               policy_grid, settlement_ts_unix, settlement_value,
                               match_start_ts):
    """Evaluate ALL policies on the cell against one (ticker, T0) entry moment.

    Per spec Section 3.4 v2 per-policy semantics. Single tick walk for entry fill,
    single tick walk for exit detection — at each tick event, all policies in the
    cell's grid are updated in vector. Per-policy state arrays track exit flag,
    exit time/price/outcome, and trailing running_max where applicable.

    Returns a list of per-policy row dicts. One row per (policy_idx) for this moment.
    """
    our_bid_price = T0_cell["yes_bid_close"]
    entry_timeout_ts = T0_unix + 240 * 60
    n = len(policy_grid)

    # Step 3: entry fill walk (single pass, shared across all policies)
    fill_time_unix = None
    fill_price = None
    for _, trade in trades_df.iterrows():
        t_unix = int(trade["created_time_ts"])
        if t_unix > entry_timeout_ts or t_unix > settlement_ts_unix:
            break
        if trade["taker_side"] == "no" and float(trade["yes_price_dollars"]) <= our_bid_price:
            fill_time_unix = t_unix
            fill_price = our_bid_price
            break

    base_row = {
        "ticker": ticker, "T0_unix": T0_unix,
        "T0_cell_key": cell_key_str(T0_cell),
        "fill_time_unix": fill_time_unix,
        "fill_price_dollars": fill_price,
        "fill_time_cell_key": None,
        "cell_drift_at_fill": None,
        "time_to_fill_minutes": None,
    }

    if fill_time_unix is None:
        # All policies unfilled
        return [
            dict(base_row,
                 policy_idx=p["idx"], policy_type=p["policy_type"],
                 policy_params=p["policy_params_str"],
                 outcome_A="unfilled", capture_A_gross_dollars=None, time_to_exit_A_minutes=None,
                 outcome_B="unfilled", capture_B_gross_dollars=None, time_to_exit_B_minutes=None)
            for p in policy_grid
        ]

    base_row["time_to_fill_minutes"] = (fill_time_unix - T0_unix) / 60.0

    # Step 4: fill-time cell state
    fill_minute_ts = (fill_time_unix // 60) * 60
    fill_time_cell = cell_state_at_minute(
        candles_df, fill_minute_ts, match_start_ts, settlement_ts_unix, ticker
    )
    base_row["fill_time_cell_key"] = cell_key_str(fill_time_cell)
    base_row["cell_drift_at_fill"] = (base_row["T0_cell_key"] != base_row["fill_time_cell_key"])

    # Step 5: per-policy targets and horizons
    target_A = [None] * n
    target_B = [None] * n
    horizon_cap_ts = [None] * n  # same for A and B (clock-based, not cell-keyed)

    for i, p in enumerate(policy_grid):
        ptype = p["policy_type"]
        h = p["horizon_min"]
        # Determine horizon cap — T0_unix-anchored per v1 inheritance convention.
        # v1's `evaluate_policy` and forensic_replay_v1's `replay_one_moment` both
        # compute horizon_cap_ts = T0_unix + horizon_min*60. Using fill_time_unix
        # instead extends each moment's exit window by (fill_time - T0_unix) ≈ 30-90s,
        # catching ~2-3% more fires across a 240-min window — exactly the +$0.004 to
        # +$0.009 systematic delta observed in Phase 2 pre-fix on the 5 limit-policy
        # byte-comparison anchors. T0-based caps preserve v1-byte-equivalence; the
        # strategically-distinct fill_time-anchored convention is a v3 option.
        if ptype in ("time_stop", "limit_time_stop"):
            cap_ts = T0_unix + int(h) * 60
        else:
            # limit / trailing / limit_trailing — default 240 min from T0
            cap_ts = T0_unix + 240 * 60
        horizon_cap_ts[i] = min(cap_ts, settlement_ts_unix)

        # Compute limit threshold (Scenario A: post-time anchor; B: fill-time anchor)
        if p["limit_c"] is not None:
            target_A[i] = fill_price + p["limit_c"] / 100.0
            if fill_time_cell is not None:
                target_B[i] = fill_time_cell["yes_ask_close"] + p["limit_c"] / 100.0
            else:
                target_B[i] = target_A[i]

    max_horizon = max(horizon_cap_ts)

    # Step 6: numpy-vectorized post-fill walk.
    # Replaces the Python per-tick per-policy for-loop with array-shape ops on per-policy
    # state. Order-of-operations preserved: horizon-fire first, then limit (taker="yes"),
    # then trailing (taker="no"); mutual exclusion enforced via the ~exited mask. The
    # running_max update precedes the trail trigger so a fresh-high tick doesn't fire
    # the policy at the same tick it set the max. Byte-equivalence with the prior
    # Python implementation verified Session 11 Phase 2 re-run (5/5 limit candidates
    # delta $0.0000 vs v1 phase3).
    horizon_cap_arr = np.array(horizon_cap_ts, dtype=np.int64)
    target_A_arr = np.array([t if t is not None else np.nan for t in target_A], dtype=np.float64)
    target_B_arr = np.array([t if t is not None else np.nan for t in target_B], dtype=np.float64)
    trail_c_dollars = np.array([p["trail_c"] / 100.0 if p["trail_c"] is not None else np.nan
                                 for p in policy_grid], dtype=np.float64)
    is_limit_type = np.array([p["policy_type"] in ("limit", "limit_time_stop", "limit_trailing")
                              for p in policy_grid], dtype=bool)
    is_trail_type = np.array([p["policy_type"] in ("trailing", "limit_trailing")
                              for p in policy_grid], dtype=bool)
    is_horizon_fires_type = np.array([p["policy_type"] in ("time_stop", "limit_time_stop",
                                                            "trailing", "limit_trailing")
                                       for p in policy_grid], dtype=bool)

    exited_A = np.zeros(n, dtype=bool)
    exited_B = np.zeros(n, dtype=bool)
    exit_time_A = np.full(n, -1, dtype=np.int64)
    exit_time_B = np.full(n, -1, dtype=np.int64)
    exit_price_A = np.full(n, np.nan, dtype=np.float64)
    exit_price_B = np.full(n, np.nan, dtype=np.float64)
    exit_outcome_A = np.empty(n, dtype=object)
    exit_outcome_B = np.empty(n, dtype=object)
    running_max_A = np.full(n, fill_price, dtype=np.float64)
    running_max_B = np.full(n, fill_price, dtype=np.float64)
    last_observed_bid = fill_price

    # Convert post-fill trades to numpy arrays for fast iteration (avoid pandas iterrows())
    pft = trades_df[trades_df["created_time_ts"] >= fill_time_unix].reset_index(drop=True)
    trade_times = pft["created_time_ts"].values.astype(np.int64)
    trade_sides = pft["taker_side"].values  # object array of "yes"/"no" strings
    trade_prices = pft["yes_price_dollars"].values.astype(np.float64)

    n_ticks = len(trade_times)
    for tick_idx in range(n_ticks):
        t_unix = trade_times[tick_idx]
        if t_unix > max_horizon:
            break
        taker = trade_sides[tick_idx]
        yes_price = trade_prices[tick_idx]

        if taker == "no":
            last_observed_bid = yes_price

        # --- Scenario A: horizon-fire first
        horizon_now_A = (~exited_A) & (t_unix > horizon_cap_arr)
        if horizon_now_A.any():
            fired_mask = horizon_now_A & is_horizon_fires_type
            expired_mask = horizon_now_A & ~is_horizon_fires_type
            exit_time_A[horizon_now_A] = horizon_cap_arr[horizon_now_A]
            exit_price_A[fired_mask] = last_observed_bid  # expired keeps NaN
            exit_outcome_A[fired_mask] = "horizon_fired"
            exit_outcome_A[expired_mask] = "horizon_expired"
            exited_A |= horizon_now_A

        # --- Scenario A: limit threshold (taker="yes" only)
        if taker == "yes":
            limit_fire_A = (~exited_A) & is_limit_type & (~np.isnan(target_A_arr)) \
                           & (yes_price >= target_A_arr)
            if limit_fire_A.any():
                exit_time_A[limit_fire_A] = t_unix
                exit_price_A[limit_fire_A] = yes_price
                exit_outcome_A[limit_fire_A] = "fired_at_target"
                exited_A |= limit_fire_A

        # --- Scenario A: trailing (taker="no" only). Update running_max BEFORE trigger.
        if taker == "no":
            trail_active_A = (~exited_A) & is_trail_type
            update_max_A = trail_active_A & (yes_price > running_max_A)
            running_max_A[update_max_A] = yes_price
            trail_fire_A = trail_active_A & (~np.isnan(trail_c_dollars)) \
                           & (yes_price <= running_max_A - trail_c_dollars)
            if trail_fire_A.any():
                exit_time_A[trail_fire_A] = t_unix
                exit_price_A[trail_fire_A] = yes_price
                exit_outcome_A[trail_fire_A] = "trailing_fired"
                exited_A |= trail_fire_A

        # --- Scenario B (mirror A with B-side arrays)
        horizon_now_B = (~exited_B) & (t_unix > horizon_cap_arr)
        if horizon_now_B.any():
            fired_mask = horizon_now_B & is_horizon_fires_type
            expired_mask = horizon_now_B & ~is_horizon_fires_type
            exit_time_B[horizon_now_B] = horizon_cap_arr[horizon_now_B]
            exit_price_B[fired_mask] = last_observed_bid
            exit_outcome_B[fired_mask] = "horizon_fired"
            exit_outcome_B[expired_mask] = "horizon_expired"
            exited_B |= horizon_now_B

        if taker == "yes":
            limit_fire_B = (~exited_B) & is_limit_type & (~np.isnan(target_B_arr)) \
                           & (yes_price >= target_B_arr)
            if limit_fire_B.any():
                exit_time_B[limit_fire_B] = t_unix
                exit_price_B[limit_fire_B] = yes_price
                exit_outcome_B[limit_fire_B] = "fired_at_target"
                exited_B |= limit_fire_B

        if taker == "no":
            trail_active_B = (~exited_B) & is_trail_type
            update_max_B = trail_active_B & (yes_price > running_max_B)
            running_max_B[update_max_B] = yes_price
            trail_fire_B = trail_active_B & (~np.isnan(trail_c_dollars)) \
                           & (yes_price <= running_max_B - trail_c_dollars)
            if trail_fire_B.any():
                exit_time_B[trail_fire_B] = t_unix
                exit_price_B[trail_fire_B] = yes_price
                exit_outcome_B[trail_fire_B] = "trailing_fired"
                exited_B |= trail_fire_B

        if exited_A.all() and exited_B.all():
            break

    # Step 7: resolve outcomes (reads from numpy state arrays)
    def _resolve(exited, ex_time, ex_price, ex_outcome, cap_ts_p, ptype):
        if exited:
            outc = ex_outcome
            t_e = int(ex_time)
            if outc == "horizon_expired":
                return outc, None, (t_e - fill_time_unix) / 60.0
            elif outc == "horizon_fired":
                price = ex_price if not np.isnan(ex_price) else last_observed_bid
                return outc, float(price - fill_price), (t_e - fill_time_unix) / 60.0
            else:  # fired_at_target / trailing_fired
                return outc, float(ex_price - fill_price), (t_e - fill_time_unix) / 60.0
        else:
            if cap_ts_p >= settlement_ts_unix - 60:
                return "settled_unfired", settlement_value - fill_price, None
            else:
                if ptype == "limit":
                    return "horizon_expired", None, None
                else:
                    return "horizon_fired", last_observed_bid - fill_price, None

    rows = []
    for i, p in enumerate(policy_grid):
        outA, capA, ttA = _resolve(bool(exited_A[i]), exit_time_A[i], exit_price_A[i],
                                    exit_outcome_A[i], horizon_cap_ts[i], p["policy_type"])
        outB, capB, ttB = _resolve(bool(exited_B[i]), exit_time_B[i], exit_price_B[i],
                                    exit_outcome_B[i], horizon_cap_ts[i], p["policy_type"])
        rows.append(dict(base_row,
            policy_idx=p["idx"], policy_type=p["policy_type"],
            policy_params=p["policy_params_str"],
            outcome_A=outA, capture_A_gross_dollars=capA, time_to_exit_A_minutes=ttA,
            outcome_B=outB, capture_B_gross_dollars=capB, time_to_exit_B_minutes=ttB,
        ))
    return rows


def phase2():
    """Phase 2: single-cell × all non-settle policies × all moments.

    Per spec Section 5.3 + Section 3.4: validates the vectorized-policy mechanism
    on the rank-1 cell (ATP_MAIN 50-60 tight low). All ~53 non-settle policies
    evaluated against ~2914 cell-matching moments. For limit policies whose
    (cell, policy) tuples are in v1 phase3's 80 candidates, byte-equivalence is
    expected. For non-limit policies, v2 measurements are the new canonical truth
    (v1 ran limit-default-10 stand-in per Section 3.4).
    """
    out_dir = os.path.join(OUT_DIR, "phase2")
    log_path = log_setup(out_dir)
    t_start = time.time()

    log("=" * 60, log_path)
    log("Layer B v2 — Phase 2: single cell × all non-settle policies × all moments", log_path)
    log("=" * 60, log_path)

    c = select_phase1_candidate()  # rank-1 candidate selector also identifies the cell
    cell_id_base = (f"premarket__{c['category']}__"
                    f"{int(c['entry_band_lo'])}-{int(c['entry_band_hi'])}__"
                    f"{c['spread_band']}__{c['volume_intensity']}")
    mkey = manifest_key_for_candidate(c)
    log(f"Cell: {cell_id_base}", log_path)
    log(f"Manifest key: {mkey}", log_path)

    policy_grid, _grid_df = build_cell_policy_grid(c)
    log(f"Policy grid: {len(policy_grid)} non-settle policies", log_path)
    by_type = {}
    for p in policy_grid:
        by_type[p["policy_type"]] = by_type.get(p["policy_type"], 0) + 1
    log(f"  By type: {by_type}", log_path)

    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)
    if mkey not in manifest:
        log(f"ABORT: manifest key {mkey} not found", log_path)
        sys.exit(1)
    tickers = manifest[mkey]["tickers"]
    log(f"Tickers in manifest: {len(tickers)}", log_path)

    all_rows = []
    moments_collected = 0
    skipped_meta = 0
    skipped_no_candles = 0
    skipped_no_trades = 0
    tickers_processed = 0
    target_parts = mkey.split("__")
    target_regime, target_eb_str, target_sb, target_vi, target_cat = target_parts

    for ticker in tickers:
        tickers_processed += 1
        elapsed_so_far = time.time() - t_start
        log(f"Ticker {tickers_processed}/{len(tickers)}: {ticker} "
            f"(moments so far: {moments_collected}, elapsed: {elapsed_so_far:.0f}s)", log_path)

        meta = load_market_settlement(ticker)
        if meta is None:
            skipped_meta += 1
            continue
        settlement_ts_unix, settlement_value, _ = meta

        candles_df = load_ticker_candles(ticker)
        if candles_df is None or len(candles_df) == 0:
            skipped_no_candles += 1
            continue

        timestamps = candles_df["end_period_ts"].values
        volumes = candles_df["volume_fp"].values
        match_start_ts = detect_match_start(timestamps, volumes)

        matching_moments = []
        for i in range(len(candles_df)):
            t = int(timestamps[i])
            row_c = candles_df.iloc[i]
            if row_c["yes_bid_close"] is None or row_c["yes_ask_close"] is None:
                continue
            try:
                bid_f = float(row_c["yes_bid_close"])
                ask_f = float(row_c["yes_ask_close"])
            except (TypeError, ValueError):
                continue
            regime = regime_for_moment(t, match_start_ts, settlement_ts_unix)
            eb = entry_band_idx(ask_f)
            sb = spread_band_name(bid_f, ask_f)
            vi = volume_intensity_for_market(volumes)
            cat = categorize(ticker)
            if (regime == target_regime and eb == int(target_eb_str)
                    and sb == target_sb and vi == target_vi and cat == target_cat):
                matching_moments.append((t, bid_f, ask_f, regime, eb, sb, vi, cat))

        if not matching_moments:
            continue

        trades_df = load_ticker_trades(ticker, start_ts_unix=int(timestamps[0]))
        if trades_df is None:
            skipped_no_trades += 1
            continue

        for (t, bid_f, ask_f, regime, eb, sb, vi, cat) in matching_moments:
            T0_cell = {
                "regime": regime, "entry_band_idx": eb,
                "spread_band": sb, "volume_intensity": vi, "category": cat,
                "yes_bid_close": bid_f, "yes_ask_close": ask_f,
            }
            forward_trades = trades_df[trades_df["created_time_ts"] >= t].reset_index(drop=True)
            rows = evaluate_moment_vectorized(
                ticker, candles_df, forward_trades, t, T0_cell,
                policy_grid, settlement_ts_unix, settlement_value, match_start_ts,
            )
            all_rows.extend(rows)
            moments_collected += 1

    elapsed = time.time() - t_start
    log("", log_path)
    log("=" * 60, log_path)
    log(f"Phase 2 complete. Runtime: {elapsed:.1f}s ({elapsed/60:.2f} min)", log_path)
    log(f"Moments collected: {moments_collected}", log_path)
    log(f"Policies × moments rows emitted: {len(all_rows)} = {moments_collected} × {len(policy_grid)}",
        log_path)
    log(f"Tickers processed: {tickers_processed}/{len(tickers)}", log_path)
    log(f"Skipped (no metadata or scalar): {skipped_meta}", log_path)
    log(f"Skipped (no candles): {skipped_no_candles}", log_path)
    log(f"Skipped (no trades): {skipped_no_trades}", log_path)
    log("=" * 60, log_path)

    df_tape = pd.DataFrame(all_rows)

    # Per-policy summary
    summary_rows = []
    for i, p in enumerate(policy_grid):
        sub = df_tape[df_tape["policy_idx"] == p["idx"]]
        capA = sub["capture_A_gross_dollars"].dropna()
        capB = sub["capture_B_gross_dollars"].dropna()
        n_filled = int(sub["fill_time_unix"].notna().sum())
        n_drift = int(sub["cell_drift_at_fill"].fillna(False).astype(bool).sum())
        summary_rows.append({
            "policy_idx": p["idx"],
            "policy_type": p["policy_type"],
            "policy_params": p["policy_params_str"],
            "n_replay_moments": len(sub),
            "n_filled": n_filled,
            "replay_fill_rate": n_filled / max(1, len(sub)),
            "cell_drift_rate_at_fill": n_drift / max(1, n_filled) if n_filled > 0 else None,
            "replay_capture_A_gross_n": len(capA),
            "replay_capture_A_gross_mean": float(capA.mean()) if len(capA) > 0 else None,
            "replay_capture_A_gross_p10": float(capA.quantile(0.10)) if len(capA) > 0 else None,
            "replay_capture_A_gross_p50": float(capA.median()) if len(capA) > 0 else None,
            "replay_capture_A_gross_p90": float(capA.quantile(0.90)) if len(capA) > 0 else None,
            "replay_capture_B_gross_n": len(capB),
            "replay_capture_B_gross_mean": float(capB.mean()) if len(capB) > 0 else None,
            "replay_capture_B_gross_p10": float(capB.quantile(0.10)) if len(capB) > 0 else None,
            "replay_capture_B_gross_p50": float(capB.median()) if len(capB) > 0 else None,
            "replay_capture_B_gross_p90": float(capB.quantile(0.90)) if len(capB) > 0 else None,
            "outcome_A_dist": sub["outcome_A"].value_counts().to_dict(),
            "outcome_B_dist": sub["outcome_B"].value_counts().to_dict(),
        })
    df_summary = pd.DataFrame(summary_rows)

    # Write outputs
    tape_path = os.path.join(out_dir, "replay_tape_phase2.parquet")
    tape_table = pa.Table.from_pandas(df_tape, preserve_index=False)
    pq.write_table(tape_table, tape_path, compression="snappy")
    log(f"Wrote replay_tape_phase2.parquet: {len(df_tape):,} rows, "
        f"{os.path.getsize(tape_path):,} bytes", log_path)

    # df_summary has dict columns (outcome_*_dist) — serialize to JSON strings for parquet
    df_summary_pq = df_summary.copy()
    df_summary_pq["outcome_A_dist"] = df_summary_pq["outcome_A_dist"].apply(json.dumps)
    df_summary_pq["outcome_B_dist"] = df_summary_pq["outcome_B_dist"].apply(json.dumps)
    summary_path = os.path.join(out_dir, "cell_summary_phase2.parquet")
    summary_table = pa.Table.from_pandas(df_summary_pq, preserve_index=False)
    pq.write_table(summary_table, summary_path, compression="snappy")
    log(f"Wrote cell_summary_phase2.parquet: {len(df_summary):,} rows", log_path)

    # Validation: byte-compare against v1 phase3 for overlapping (cell, policy) limits
    log("", log_path)
    log("=== Validation: v2 vs v1 phase3 byte-equivalence on limit-policy overlap ===", log_path)
    v1_cs = pq.read_table(
        os.path.join(DUR_DIR, "forensic_replay_v1/phase3/candidate_summary.parquet")
    ).to_pandas()
    v1_for_cell = v1_cs[
        (v1_cs["category"] == c["category"])
        & (v1_cs["entry_band_lo"] == c["entry_band_lo"])
        & (v1_cs["spread_band"] == c["spread_band"])
        & (v1_cs["volume_intensity"] == c["volume_intensity"])
        & (v1_cs["policy_type"] == "limit")
    ].copy()
    log(f"v1 phase3 limit candidates for this cell: {len(v1_for_cell)}", log_path)

    byte_equiv_summary = []
    for _, v1_row in v1_for_cell.iterrows():
        v1_params = json.loads(v1_row["policy_params"])
        match = df_summary[
            (df_summary["policy_type"] == "limit")
            & (df_summary["policy_params"] == v1_row["policy_params"])
        ]
        if len(match) != 1:
            byte_equiv_summary.append({
                "policy_params": v1_row["policy_params"],
                "v1_B_net_mean": float(v1_row["replay_capture_B_net_mean"]),
                "v2_B_gross_mean": None,
                "delta": None,
                "match": False,
                "note": "no v2 match found",
            })
            continue
        v2_B = match.iloc[0]["replay_capture_B_gross_mean"]
        v1_B = float(v1_row["replay_capture_B_net_mean"])
        delta = v2_B - v1_B if v2_B is not None else None
        byte_equiv_summary.append({
            "policy_params": v1_row["policy_params"],
            "v1_B_net_mean": v1_B,
            "v2_B_gross_mean": float(v2_B) if v2_B is not None else None,
            "delta": float(delta) if delta is not None else None,
            "match": bool(delta is not None and abs(delta) <= 0.01),
        })
        log(f"  {v1_row['policy_params']}: v1=${v1_B:.4f}  v2=${v2_B:.4f}  "
            f"delta=${delta:+.4f}  {'PASS' if abs(delta) <= 0.01 else 'FAIL'}", log_path)

    all_pass = all(e["match"] for e in byte_equiv_summary)
    log(f"Phase 2 calibration verdict: "
        f"{'PASS' if all_pass else 'FAIL'} ({sum(e['match'] for e in byte_equiv_summary)}/"
        f"{len(byte_equiv_summary)} limit candidates byte-match within ±$0.01)", log_path)

    # Surface non-limit canonical values
    log("", log_path)
    log("=== Non-limit policy canonical measurements (v2 proper semantics) ===", log_path)
    for ptype in ("time_stop", "trailing", "limit_time_stop", "limit_trailing"):
        sub = df_summary[df_summary["policy_type"] == ptype]
        if len(sub) == 0:
            continue
        log(f"  {ptype} (n={len(sub)} policies):", log_path)
        for _, r in sub.iterrows():
            B = r["replay_capture_B_gross_mean"]
            A = r["replay_capture_A_gross_mean"]
            log(f"    {r['policy_params']}: A=${A:.4f}  B=${B:.4f}  "
                f"fill={r['replay_fill_rate']:.3f}", log_path)

    # Run summary JSON
    summary_json = {
        "phase": 2,
        "spec_commits": ["e2197b7", "164f732e", "137191a6"],
        "cell": cell_id_base,
        "manifest_key": mkey,
        "n_policies": len(policy_grid),
        "policies_by_type": by_type,
        "moments_evaluated": int(moments_collected),
        "tickers_processed": tickers_processed,
        "skipped_meta": skipped_meta,
        "skipped_no_candles": skipped_no_candles,
        "skipped_no_trades": skipped_no_trades,
        "runtime_seconds": round(elapsed, 1),
        "runtime_minutes": round(elapsed / 60, 2),
        "byte_equiv_limit_class": byte_equiv_summary,
        "byte_equiv_all_pass": bool(all_pass),
        "non_limit_canonical": [
            {"policy_type": r["policy_type"],
             "policy_params": r["policy_params"],
             "replay_capture_A_gross_mean": r["replay_capture_A_gross_mean"],
             "replay_capture_B_gross_mean": r["replay_capture_B_gross_mean"],
             "replay_fill_rate": r["replay_fill_rate"],
             "n_replay_moments": int(r["n_replay_moments"]),
             "outcome_B_dist": r["outcome_B_dist"]}
            for _, r in df_summary.iterrows()
            if r["policy_type"] != "limit"
        ],
    }
    summary_json_path = os.path.join(out_dir, "run_summary_phase2.json")
    with open(summary_json_path, "w") as f:
        json.dump(summary_json, f, indent=2, default=str)
    log(f"Wrote {summary_json_path}", log_path)
    log("=" * 60, log_path)


# ============================================================
# Phase 3: full corpus with kill-resilient incremental writes
# ============================================================

def build_corpus_cell_list():
    """Return the deterministic-ordered list of non-settle premarket cells.

    Each cell is represented by a row from Layer B v1 exit_policy_per_cell.parquet
    (any policy on that cell — we use the first), carrying the cell-key fields used
    downstream by manifest_key_for_candidate / build_cell_policy_grid / select-from-
    sample_manifest. Cell ordering is alphabetical by
    (category, entry_band_lo, spread_band, volume_intensity) for repeatability —
    the cell_idx assigned in this function is referenced in per-cell parquet names
    and the progress JSONL, so the order must be stable across resumed runs.
    """
    t = pq.read_table(LAYER_B_PARQUET).to_pandas()
    pre = t[t["channel"] == "premarket"].copy()

    def _is_settle(s):
        try:
            return json.loads(s).get("horizon_min") == "settle"
        except Exception:
            return False

    pre["_is_settle"] = pre["policy_params"].apply(_is_settle)
    non_settle = pre[~pre["_is_settle"]].copy()

    cell_cols = ["category", "entry_band_lo", "entry_band_hi", "spread_band", "volume_intensity"]
    # One row per cell — take the first policy occurrence per cell, ordered alphabetically.
    cells = (non_settle
             .sort_values(cell_cols + ["policy_type", "policy_params"])
             .drop_duplicates(subset=cell_cols, keep="first")
             .sort_values(cell_cols)
             .reset_index(drop=True))
    return cells


def cell_key_str_compact(c):
    """Return a compact cell-key string for logging / JSONL."""
    return (f"{c['category']}|{int(c['entry_band_lo'])}|{int(c['entry_band_hi'])}|"
            f"{c['spread_band']}|{c['volume_intensity']}")


def read_progress_jsonl(progress_path):
    """Return a set of cell_idx values already recorded as completed in the JSONL.

    Used for kill-resilient resume: a re-launched producer reads the JSONL,
    identifies which cells already have per-cell parquets written, and skips them.
    """
    completed = set()
    if not os.path.exists(progress_path):
        return completed
    with open(progress_path) as f:
        for line in f:
            try:
                entry = json.loads(line)
                if "cell_idx" in entry:
                    completed.add(int(entry["cell_idx"]))
            except Exception:
                continue
    return completed


def process_one_cell(c, cell_idx, manifest, out_dir, log_path):
    """Process a single cell × all non-settle policies × all moments.

    Writes per-cell parquet `cell_summary_cell_{cell_idx:03d}.parquet` and returns
    the JSONL progress dict for the caller to append to `_progress_summary.jsonl`.
    Mirrors phase2()'s per-cell logic but operates standalone (no v1-comparison
    inline — Section 6 Check 1 validation runs once across all cells at end).
    """
    t_cell_start = time.time()
    cell_key = cell_key_str_compact(c)
    mkey = manifest_key_for_candidate(c)
    policy_grid, _grid_df = build_cell_policy_grid(c)

    if mkey not in manifest:
        log(f"Cell {cell_idx} {cell_key}: WARNING manifest key not found, skipping", log_path)
        return {
            "cell_idx": int(cell_idx), "cell_key": cell_key,
            "category": c["category"], "entry_band_lo": int(c["entry_band_lo"]),
            "entry_band_hi": int(c["entry_band_hi"]), "spread_band": c["spread_band"],
            "volume_intensity": c["volume_intensity"],
            "n_moments": 0, "n_filled": 0, "replay_fill_rate": None,
            "cell_drift_rate_at_fill": None, "runtime_seconds": 0.0,
            "capture_B_mean_top_limit": None, "top_limit_policy_params": None,
            "skipped_reason": "manifest_key_not_found",
            "completed_at": datetime.now().isoformat(timespec="seconds"),
        }

    tickers = manifest[mkey]["tickers"]
    target_parts = mkey.split("__")
    target_regime, target_eb_str, target_sb, target_vi, target_cat = target_parts

    all_rows = []
    moments_collected = 0
    for ticker in tickers:
        meta = load_market_settlement(ticker)
        if meta is None:
            continue
        settlement_ts_unix, settlement_value, _ = meta
        candles_df = load_ticker_candles(ticker)
        if candles_df is None or len(candles_df) == 0:
            continue

        timestamps = candles_df["end_period_ts"].values
        volumes = candles_df["volume_fp"].values
        match_start_ts = detect_match_start(timestamps, volumes)

        matching_moments = []
        for i in range(len(candles_df)):
            t = int(timestamps[i])
            row_c = candles_df.iloc[i]
            if row_c["yes_bid_close"] is None or row_c["yes_ask_close"] is None:
                continue
            try:
                bid_f = float(row_c["yes_bid_close"])
                ask_f = float(row_c["yes_ask_close"])
            except (TypeError, ValueError):
                continue
            regime = regime_for_moment(t, match_start_ts, settlement_ts_unix)
            eb = entry_band_idx(ask_f)
            sb = spread_band_name(bid_f, ask_f)
            vi = volume_intensity_for_market(volumes)
            cat = categorize(ticker)
            if (regime == target_regime and eb == int(target_eb_str)
                    and sb == target_sb and vi == target_vi and cat == target_cat):
                matching_moments.append((t, bid_f, ask_f, regime, eb, sb, vi, cat))

        if not matching_moments:
            continue

        trades_df = load_ticker_trades(ticker, start_ts_unix=int(timestamps[0]))
        if trades_df is None:
            continue

        for (t, bid_f, ask_f, regime, eb, sb, vi, cat) in matching_moments:
            T0_cell = {
                "regime": regime, "entry_band_idx": eb,
                "spread_band": sb, "volume_intensity": vi, "category": cat,
                "yes_bid_close": bid_f, "yes_ask_close": ask_f,
            }
            forward_trades = trades_df[trades_df["created_time_ts"] >= t].reset_index(drop=True)
            rows = evaluate_moment_vectorized(
                ticker, candles_df, forward_trades, t, T0_cell,
                policy_grid, settlement_ts_unix, settlement_value, match_start_ts,
            )
            all_rows.extend(rows)
            moments_collected += 1

    # Aggregate per-policy
    df_tape = pd.DataFrame(all_rows)
    summary_rows = []
    if len(df_tape) > 0:
        for p in policy_grid:
            sub = df_tape[df_tape["policy_idx"] == p["idx"]]
            capA = sub["capture_A_gross_dollars"].dropna()
            capB = sub["capture_B_gross_dollars"].dropna()
            n_filled = int(sub["fill_time_unix"].notna().sum())
            n_drift = int(sub["cell_drift_at_fill"].fillna(False).astype(bool).sum())
            summary_rows.append({
                "cell_idx": int(cell_idx),
                "cell_key": cell_key,
                "category": c["category"],
                "entry_band_lo": int(c["entry_band_lo"]),
                "entry_band_hi": int(c["entry_band_hi"]),
                "spread_band": c["spread_band"],
                "volume_intensity": c["volume_intensity"],
                "policy_idx": p["idx"],
                "policy_type": p["policy_type"],
                "policy_params": p["policy_params_str"],
                "n_replay_moments": len(sub),
                "n_filled": n_filled,
                "replay_fill_rate": n_filled / max(1, len(sub)),
                "cell_drift_rate_at_fill": n_drift / max(1, n_filled) if n_filled > 0 else None,
                "replay_capture_A_gross_n": len(capA),
                "replay_capture_A_gross_mean": float(capA.mean()) if len(capA) > 0 else None,
                "replay_capture_A_gross_p10": float(capA.quantile(0.10)) if len(capA) > 0 else None,
                "replay_capture_A_gross_p50": float(capA.median()) if len(capA) > 0 else None,
                "replay_capture_A_gross_p90": float(capA.quantile(0.90)) if len(capA) > 0 else None,
                "replay_capture_B_gross_n": len(capB),
                "replay_capture_B_gross_mean": float(capB.mean()) if len(capB) > 0 else None,
                "replay_capture_B_gross_p10": float(capB.quantile(0.10)) if len(capB) > 0 else None,
                "replay_capture_B_gross_p50": float(capB.median()) if len(capB) > 0 else None,
                "replay_capture_B_gross_p90": float(capB.quantile(0.90)) if len(capB) > 0 else None,
            })

    df_summary = pd.DataFrame(summary_rows)
    cell_parquet_path = os.path.join(out_dir, f"cell_summary_cell_{cell_idx:03d}.parquet")
    if len(df_summary) > 0:
        pq.write_table(pa.Table.from_pandas(df_summary, preserve_index=False),
                       cell_parquet_path, compression="snappy")

    # JSONL line (compact per-cell metadata + top-limit signal).
    # Bug fix (Session 11 sanity-check probe): the per-cell fill_overall and drift_overall
    # counts must be computed from a SINGLE policy slice of df_tape — not the full df_tape —
    # because df_tape has one row per (policy, moment) pair, so summing fill_time_unix.notna()
    # across all rows inflates by len(policy_grid)≈53. All policies on a cell see the same
    # per-moment fill outcome, so any single policy_idx slice gives the unique-moment count.
    if len(df_tape) > 0:
        first_idx = int(df_tape["policy_idx"].iloc[0])
        _one_policy_slice = df_tape[df_tape["policy_idx"] == first_idx]
        n_filled_overall = int(_one_policy_slice["fill_time_unix"].notna().sum())
        drift_overall = int(_one_policy_slice["cell_drift_at_fill"].fillna(False).astype(bool).sum())
    else:
        n_filled_overall = 0
        drift_overall = 0
    top_limit_B = None
    top_limit_params = None
    if len(df_summary) > 0:
        limit_rows = df_summary[df_summary["policy_type"] == "limit"]
        if len(limit_rows) > 0 and limit_rows["replay_capture_B_gross_mean"].notna().any():
            top_idx = limit_rows["replay_capture_B_gross_mean"].fillna(-1e9).idxmax()
            top_limit_B = float(limit_rows.loc[top_idx, "replay_capture_B_gross_mean"])
            top_limit_params = str(limit_rows.loc[top_idx, "policy_params"])

    elapsed = time.time() - t_cell_start
    return {
        "cell_idx": int(cell_idx),
        "cell_key": cell_key,
        "category": c["category"],
        "entry_band_lo": int(c["entry_band_lo"]),
        "entry_band_hi": int(c["entry_band_hi"]),
        "spread_band": c["spread_band"],
        "volume_intensity": c["volume_intensity"],
        "n_moments": int(moments_collected),
        "n_filled": n_filled_overall,
        "replay_fill_rate": n_filled_overall / max(1, moments_collected) if moments_collected > 0 else None,
        "cell_drift_rate_at_fill": drift_overall / max(1, n_filled_overall) if n_filled_overall > 0 else None,
        "runtime_seconds": round(elapsed, 1),
        "capture_B_mean_top_limit": top_limit_B,
        "top_limit_policy_params": top_limit_params,
        "completed_at": datetime.now().isoformat(timespec="seconds"),
    }


def phase3():
    """Phase 3: full non-settle premarket corpus, kill-resilient.

    Per spec Section 5.3 + Section 3.4: ~235 cells × ~53 policies × ~857 moments
    avg = ~201,414 moments total. Runtime estimate at numpy-vectorized 0.234 s/moment
    (Phase 2 measurement Session 11): ~13.1 hours. Within spec budget (13-16h).

    Architecture (per Commit B kill-resilience design):
    - Per-cell parquet `cell_summary_cell_{cell_idx:03d}.parquet` written after each
      cell completes its policy-grid evaluation (53 rows per file).
    - `_progress_summary.jsonl` appended one line per cell with compact metadata.
    - Resume mode: re-launched producer reads JSONL, skips already-completed cells.
    - Final merge: concat all per-cell parquets in cell_idx order → `cell_summary_phase3.parquet`.
    - Pattern mirrors forensic_replay_v1 commit `db1d249`.
    """
    out_dir = os.path.join(OUT_DIR, "phase3")
    log_path = log_setup(out_dir)
    t_start = time.time()

    log("=" * 60, log_path)
    log("Layer B v2 — Phase 3: full non-settle premarket corpus", log_path)
    log("=" * 60, log_path)

    cell_list = build_corpus_cell_list()
    log(f"Cell list: {len(cell_list)} non-settle premarket cells (deterministic order)", log_path)
    log(f"  Categories: {cell_list['category'].value_counts().to_dict()}", log_path)

    # Kill-resilient resume: read progress JSONL
    progress_path = os.path.join(out_dir, "_progress_summary.jsonl")
    completed_cell_ids = read_progress_jsonl(progress_path)
    if completed_cell_ids:
        log(f"Resume mode: {len(completed_cell_ids)} cells already completed in JSONL", log_path)

    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)

    cells_processed_this_run = 0
    cells_skipped_resume = 0
    for cell_idx, c in cell_list.iterrows():
        if cell_idx in completed_cell_ids:
            cells_skipped_resume += 1
            continue
        elapsed_so_far = time.time() - t_start
        log(f"Cell {cell_idx}/{len(cell_list)}: {cell_key_str_compact(c)} "
            f"(processed_this_run={cells_processed_this_run}, "
            f"elapsed={elapsed_so_far:.0f}s)", log_path)
        jsonl_entry = process_one_cell(c, cell_idx, manifest, out_dir, log_path)
        # Append JSONL line atomically (open-append-close)
        with open(progress_path, "a") as f:
            f.write(json.dumps(jsonl_entry, default=str) + "\n")
        cells_processed_this_run += 1
        log(f"  → n_moments={jsonl_entry['n_moments']}, "
            f"runtime={jsonl_entry['runtime_seconds']}s, "
            f"top_limit_B={jsonl_entry.get('capture_B_mean_top_limit')}", log_path)

    elapsed = time.time() - t_start
    log("", log_path)
    log("=" * 60, log_path)
    log(f"Phase 3 cell loop complete. Runtime: {elapsed:.1f}s ({elapsed/3600:.2f} h)", log_path)
    log(f"Cells processed this run: {cells_processed_this_run}", log_path)
    log(f"Cells skipped (resume): {cells_skipped_resume}", log_path)
    log("=" * 60, log_path)

    # Final merge: read all per-cell parquets, concat, write cell_summary_phase3.parquet
    log("Merging per-cell parquets...", log_path)
    cell_files = sorted(glob.glob(os.path.join(out_dir, "cell_summary_cell_*.parquet")))
    log(f"  Found {len(cell_files)} per-cell parquets", log_path)
    if cell_files:
        dfs = [pd.read_parquet(f) for f in cell_files]
        df_phase3 = pd.concat(dfs, ignore_index=True)
        merged_path = os.path.join(out_dir, "cell_summary_phase3.parquet")
        pq.write_table(pa.Table.from_pandas(df_phase3, preserve_index=False),
                       merged_path, compression="snappy")
        log(f"  Wrote {merged_path}: {len(df_phase3):,} rows, "
            f"{os.path.getsize(merged_path):,} bytes", log_path)
    else:
        log(f"  WARNING: no per-cell parquets found, skipping merge", log_path)
        df_phase3 = pd.DataFrame()

    # Validation gate per spec Section 6 — hard gates
    log("", log_path)
    log("=== Validation gate (spec Section 6) ===", log_path)
    validation = {}

    if len(df_phase3) > 0:
        # Check 1: byte-equivalence on 39 v1-phase3 limit candidates
        v1_cs = pd.read_parquet(
            os.path.join(DUR_DIR, "forensic_replay_v1/phase3/candidate_summary.parquet")
        )
        v1_limit = v1_cs[v1_cs["policy_type"] == "limit"].copy()
        check1_results = []
        for _, v1_row in v1_limit.iterrows():
            match = df_phase3[
                (df_phase3["category"] == v1_row["category"])
                & (df_phase3["entry_band_lo"] == v1_row["entry_band_lo"])
                & (df_phase3["spread_band"] == v1_row["spread_band"])
                & (df_phase3["volume_intensity"] == v1_row["volume_intensity"])
                & (df_phase3["policy_type"] == "limit")
                & (df_phase3["policy_params"] == v1_row["policy_params"])
            ]
            if len(match) != 1:
                check1_results.append({"v1_params": v1_row["policy_params"],
                                       "cell": cell_key_str_compact(v1_row),
                                       "match": False, "note": "no v2 match"})
                continue
            v2_B = match.iloc[0]["replay_capture_B_gross_mean"]
            v1_B = float(v1_row["replay_capture_B_net_mean"])
            delta = (v2_B - v1_B) if v2_B is not None else None
            check1_results.append({
                "v1_params": v1_row["policy_params"],
                "cell": cell_key_str_compact(v1_row),
                "v1_B": v1_B, "v2_B": v2_B,
                "delta": delta,
                "match": bool(delta is not None and abs(delta) <= 0.0001),
            })
        check1_pass = all(r["match"] for r in check1_results) and len(check1_results) >= 39
        validation["check1_byte_equiv_v1_limit_pass"] = bool(check1_pass)
        validation["check1_n_compared"] = len(check1_results)
        validation["check1_failures"] = [r for r in check1_results if not r["match"]]
        log(f"  Check 1 byte-equiv on {len(check1_results)} v1 limit candidates: "
            f"{'PASS' if check1_pass else 'FAIL'}", log_path)
        if not check1_pass:
            for r in validation["check1_failures"][:10]:
                log(f"    FAIL: {r}", log_path)

        # Check 2: fill rate band 100% (strict per Section 6 amendment)
        fill = df_phase3["replay_fill_rate"].dropna()
        in_band = ((fill >= 0.05) & (fill <= 0.95))
        check2_pass = bool(in_band.all())
        outliers = df_phase3[df_phase3["replay_fill_rate"].notna()
                             & ~((df_phase3["replay_fill_rate"] >= 0.05)
                                 & (df_phase3["replay_fill_rate"] <= 0.95))]
        validation["check2_fill_rate_band_pass"] = check2_pass
        validation["check2_n_compared"] = int(fill.notna().sum() if hasattr(fill, "notna") else len(fill))
        validation["check2_outliers_observed"] = [
            {"cell": cell_key_str_compact(r), "policy_params": r["policy_params"],
             "fill_rate": float(r["replay_fill_rate"])}
            for _, r in outliers.iterrows()
        ]
        log(f"  Check 2 fill_rate ∈ [0.05, 0.95] (strict 100%): "
            f"{'PASS' if check2_pass else 'FAIL'} "
            f"({len(outliers)} outliers)", log_path)

        # Check 3: A-vs-B coherence
        both = df_phase3.dropna(subset=["replay_capture_A_gross_mean", "replay_capture_B_gross_mean"])
        abs_delta_AB = (both["replay_capture_A_gross_mean"] - both["replay_capture_B_gross_mean"]).abs()
        mean_abs_delta = float(abs_delta_AB.mean()) if len(both) > 0 else None
        b_gt_a_pct = float((both["replay_capture_B_gross_mean"] > both["replay_capture_A_gross_mean"]).mean()) \
            if len(both) > 0 else None
        check3_pass = bool(mean_abs_delta is not None and mean_abs_delta < 0.02
                            and b_gt_a_pct is not None and b_gt_a_pct > 0.6)
        validation["check3_AB_coherence_pass"] = check3_pass
        validation["check3_mean_abs_delta_AB"] = mean_abs_delta
        validation["check3_B_gt_A_pct"] = b_gt_a_pct
        log(f"  Check 3 A-vs-B coherence (mean abs Δ<$0.02, B>A>60%): "
            f"{'PASS' if check3_pass else 'FAIL'} "
            f"(mean abs Δ=${mean_abs_delta}, B>A={b_gt_a_pct})", log_path)

    # Informative measurements (do not gate PASS) — surface aggregates for Coord 4
    informative = {}
    if len(df_phase3) > 0:
        # By-policy class gap pattern (corpus-wide)
        by_class = []
        for ptype, grp in df_phase3.groupby("policy_type"):
            n = len(grp)
            B = grp["replay_capture_B_gross_mean"].dropna()
            A = grp["replay_capture_A_gross_mean"].dropna()
            by_class.append({
                "policy_type": ptype,
                "n_cell_policy_rows": n,
                "B_gross_mean_corpus": float(B.mean()) if len(B) > 0 else None,
                "B_gross_median_corpus": float(B.median()) if len(B) > 0 else None,
                "A_gross_mean_corpus": float(A.mean()) if len(A) > 0 else None,
                "A_gross_median_corpus": float(A.median()) if len(A) > 0 else None,
            })
        informative["by_policy_class_gap_pattern"] = by_class

        # Top-50 (cell, policy) by Scenario B at corpus scale
        ranked = df_phase3.dropna(subset=["replay_capture_B_gross_mean"]) \
            .sort_values("replay_capture_B_gross_mean", ascending=False).head(50)
        informative["top_50_by_capture_B"] = [
            {
                "rank": i + 1,
                "cell": cell_key_str_compact(r),
                "policy_type": r["policy_type"], "policy_params": r["policy_params"],
                "replay_capture_B_gross_mean": float(r["replay_capture_B_gross_mean"]),
                "replay_capture_A_gross_mean": float(r["replay_capture_A_gross_mean"])
                    if r["replay_capture_A_gross_mean"] is not None else None,
                "replay_fill_rate": float(r["replay_fill_rate"])
                    if r["replay_fill_rate"] is not None else None,
                "cell_drift_rate_at_fill": float(r["cell_drift_rate_at_fill"])
                    if r["cell_drift_rate_at_fill"] is not None else None,
                "n_replay_moments": int(r["n_replay_moments"]),
            }
            for i, (_, r) in enumerate(ranked.iterrows())
        ]

        # Non-limit canonical (per-class deployable cohort: fill≥0.4 AND drift≤0.5)
        nonlimit = df_phase3[df_phase3["policy_type"] != "limit"].copy()
        deployable = nonlimit[
            (nonlimit["replay_fill_rate"] >= 0.40)
            & (nonlimit["cell_drift_rate_at_fill"] <= 0.50)
        ].dropna(subset=["replay_capture_B_gross_mean"]) \
         .sort_values("replay_capture_B_gross_mean", ascending=False).head(50)
        informative["non_limit_top_50_deployable"] = [
            {
                "rank": i + 1,
                "cell": cell_key_str_compact(r),
                "policy_type": r["policy_type"], "policy_params": r["policy_params"],
                "replay_capture_B_gross_mean": float(r["replay_capture_B_gross_mean"]),
                "replay_fill_rate": float(r["replay_fill_rate"]),
                "cell_drift_rate_at_fill": float(r["cell_drift_rate_at_fill"]),
                "n_replay_moments": int(r["n_replay_moments"]),
            }
            for i, (_, r) in enumerate(deployable.iterrows())
        ]

    # Checkpoint state
    checkpoint_state = {
        "n_cells_total": int(len(cell_list)),
        "n_cells_completed": int(len(cell_files)),
        "n_cells_skipped_resume": int(cells_skipped_resume),
        "n_cells_processed_this_run": int(cells_processed_this_run),
        "all_cells_completed": int(len(cell_files)) == int(len(cell_list)),
        "last_completed_cell_idx": int(max(read_progress_jsonl(progress_path)))
            if read_progress_jsonl(progress_path) else None,
    }

    summary_json = {
        "phase": 3,
        "spec_commits": ["e2197b7", "164f732e", "137191a6", "96257909"],
        "producer_commits": ["c0b5e7c2", "6948000e", "a23545a1"],
        "runtime_seconds_this_run": round(elapsed, 1),
        "runtime_hours_this_run": round(elapsed / 3600, 2),
        "checkpoint_state": checkpoint_state,
        "validation_gate": validation,
        "informative": informative,
    }
    summary_json_path = os.path.join(out_dir, "run_summary_phase3.json")
    with open(summary_json_path, "w") as f:
        json.dump(summary_json, f, indent=2, default=str)
    log(f"Wrote {summary_json_path}", log_path)
    log("=" * 60, log_path)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], required=True)
    args = parser.parse_args()

    if args.phase == 1:
        phase1()
    elif args.phase == 2:
        phase2()
    elif args.phase == 3:
        phase3()


if __name__ == "__main__":
    main()
