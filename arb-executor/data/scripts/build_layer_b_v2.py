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

def phase2():
    """Phase 2: single-cell × all ~53 non-settle policies × all moments.

    Per spec Section 5.3: validates vectorized-policy correctness at full per-cell
    moment scale. Reproduces forensic replay v1's 5 candidates for ATP_MAIN 50-60
    tight low (limit_c ∈ {7, 10, 15, 20, 30}) within ±$0.01 each. Pending separate
    single-concern commit per Coordination Point 2 STOP discipline.
    """
    raise NotImplementedError(
        "Phase 2 not yet implemented. Pending separate single-concern commit "
        "after Phase 1 chat-side review (Coordination Point 2 STOP per "
        "docs/SESSION10_HANDOFF.md)."
    )


def phase3():
    """Phase 3: full corpus (~12,455 non-settle premarket (cell, policy) tuples).

    Per spec Section 5.3: per-cell streaming, vectorized policy evaluation, kill-
    resilient incremental writes. Runtime budget <20 hours. Pending separate
    single-concern commit gated on Phase 2 PASS.
    """
    raise NotImplementedError(
        "Phase 3 not yet implemented. Pending Phase 2 PASS + separate single-concern commit."
    )


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
