#!/usr/bin/env python3
"""Forensic replay v1 producer — tick-level realized economics per (cell, policy).

Implementation per arb-executor/docs/forensic_replay_v1_spec.md (commits 40db959 + 3b62039).

Per SIMONS_MODE.md Section 6: replays top-N (cell, policy) candidates from Layer B v1
against tick-level g9_trades reality. v1 disposition: premarket-only; phased rollout
with hard runtime gates.

Phases:
- --phase=1: single-candidate calibration probe (1 candidate x 100 moments). Smoke-test
  the 9-step procedure end-to-end. Runtime budget: <5 minutes.
- --phase=2: single-candidate full run (1 candidate x all moments). NOT YET IMPLEMENTED.
- --phase=3: full run (80 candidates). NOT YET IMPLEMENTED.

Phase 1 candidate: rank-7 non-settle premarket cell — ATP_CHALL 80-90 tight low,
limit policy with limit_c=10. fire_rate=96.4% (densely exercises fill-and-exit
pipeline; smoke-test discipline favors producer-correctness over alpha-signal).
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
OUT_DIR = os.path.join(DUR_DIR, "forensic_replay_v1")
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
# Phase 1 candidate selection
# ============================================================

def select_phase1_candidate():
    """Return the rank-7 non-settle premarket candidate per Phase 1 design.

    Selection criteria:
    - channel = premarket
    - n_simulated >= 50
    - policy_type = limit (NOT settle-horizon time_stop — that collapses A/B scenarios)
    - rank by capture_mean descending
    - return rank-7 specifically: ATP_CHALL 80-90 tight low / limit / limit_c=10

    This selection is hard-coded for Phase 1 reproducibility. Phase 3 will iterate
    over the top-N from a query function.
    """
    t = pq.read_table(LAYER_B_PARQUET).to_pandas()
    pre = t[(t["channel"] == "premarket") & (t["n_simulated"] >= 50)].copy()

    # Filter to the exact Phase 1 candidate
    match = pre[
        (pre["category"] == "ATP_CHALL")
        & (pre["entry_band_lo"] == 80)
        & (pre["entry_band_hi"] == 90)
        & (pre["spread_band"] == "tight")
        & (pre["volume_intensity"] == "low")
        & (pre["policy_type"] == "limit")
    ].copy()

    def is_target(row):
        try:
            params = json.loads(row["policy_params"])
        except Exception:
            return False
        return params.get("limit_c") == 10

    match["is_target"] = match.apply(is_target, axis=1)
    hit = match[match["is_target"]]
    if len(hit) != 1:
        raise SystemExit(f"FAIL: Phase 1 candidate selector returned {len(hit)} rows, expected 1")

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
# Per-ticker data loading
# ============================================================

def load_ticker_candles(ticker):
    """Read g9_candles for one ticker via predicate pushdown. Return sorted DataFrame.
    Returns None if the ticker has no candles (skipped marker)."""
    table = pq.read_table(
        CANDLES_PARQUET,
        columns=["ticker", "end_period_ts", "yes_bid_close", "yes_ask_close", "volume_fp"],
        filters=[("ticker", "=", ticker)],
    )
    if table.num_rows == 0:
        return None
    df = table.to_pandas().sort_values("end_period_ts").reset_index(drop=True)
    return df


def load_ticker_trades(ticker, start_ts_unix=None):
    """Read g9_trades for one ticker via predicate pushdown.
    If start_ts_unix is provided, filter to created_time >= that timestamp.
    Returns sorted DataFrame or None if no trades."""
    filters = [("ticker", "=", ticker)]
    table = pq.read_table(
        TRADES_PARQUET,
        columns=["ticker", "created_time", "taker_side", "yes_price_dollars", "no_price_dollars", "count_fp"],
        filters=filters,
    )
    if table.num_rows == 0:
        return None
    df = table.to_pandas()

    # created_time is microsecond-precision timestamp (per Session 9 schema probe).
    # Convert to unix seconds for arithmetic with end_period_ts.
    # Per-row .timestamp() is precision-agnostic — avoids the microsecond-vs-nanosecond
    # footgun where pd.to_datetime() of microsecond-precision ISO strings produces datetime64[us]
    # arrays whose .astype("int64") returns microseconds (not nanoseconds), making // 10**9 yield
    # values 1000x too small. The bug surfaced in Phase 1 as fill_rate=0% (every trade timestamp
    # ~1.77e6 vs candle timestamp ~1.77e9, no overlap, so the forward-walk never matched).
    df["created_time_ts"] = pd.to_datetime(df["created_time"]).map(lambda x: int(x.timestamp()))
    df = df.sort_values("created_time_ts").reset_index(drop=True)

    if start_ts_unix is not None:
        df = df[df["created_time_ts"] >= start_ts_unix].reset_index(drop=True)

    return df


def load_market_settlement(ticker):
    """Read g9_metadata for one ticker. Returns (settlement_ts_unix, settlement_value_dollars, result)
    or None if the ticker is not in metadata or result is scalar."""
    table = pq.read_table(
        META_PARQUET,
        columns=["ticker", "result", "settlement_ts"],
        filters=[("ticker", "=", ticker)],
    )
    if table.num_rows == 0:
        return None
    row = table.to_pandas().iloc[0]
    if row["result"] not in ("yes", "no"):
        return None  # scalar markets excluded per spec
    settle_ts = int(
        datetime.fromisoformat(row["settlement_ts"].replace("Z", "+00:00")).timestamp()
    )
    settle_value = 1.0 if row["result"] == "yes" else 0.0
    return (settle_ts, settle_value, row["result"])


# ============================================================
# Cell-state computation at a moment
# ============================================================

def cell_state_at_minute(candles_df, minute_ts, match_start_ts, settlement_ts_unix, ticker):
    """Compute the cell state at a given minute_ts.

    Returns dict {regime, entry_band_idx, spread_band, volume_intensity, category}
    or None if the candle at that minute is missing / has null bid/ask.
    """
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
    vi = volume_intensity_for_market(candles_df["volume_fp"].values)  # NaN-safe per spec
    cat = categorize(ticker)

    return {
        "regime": regime,
        "entry_band_idx": eb,
        "spread_band": sb,
        "volume_intensity": vi,
        "category": cat,
        "yes_bid_close": bid_f,
        "yes_ask_close": ask_f,
    }


def cell_key_str(cell_state):
    """Build a cell-key string for comparison."""
    if cell_state is None:
        return None
    return (
        f"{cell_state['regime']}__{cell_state['entry_band_idx']}__"
        f"{cell_state['spread_band']}__{cell_state['volume_intensity']}__"
        f"{cell_state['category']}"
    )


def matches_target(cell_state, target_key):
    """Check whether a cell_state matches a target manifest key."""
    if cell_state is None:
        return False
    return cell_key_str(cell_state) == target_key


# ============================================================
# Per-moment 9-step replay
# ============================================================

def replay_one_moment(ticker, candles_df, trades_df, T0_unix, T0_cell,
                      policy_type, policy_params,
                      settlement_ts_unix, settlement_value,
                      match_start_ts, log_path, log_warnings):
    """Execute spec Section 3.1 steps 2-7 for one (ticker, T0) entry moment.

    Per Phase 1 scope: limit policy with limit_c=10. Scenarios A and B both apply.

    Returns a row dict suitable for Output 1 (replay_tape.parquet) schema.
    """
    our_bid_price = T0_cell["yes_bid_close"]
    limit_c = policy_params.get("limit_c", 10)
    horizon_min = policy_params.get("horizon_min", 240)  # default 240 per Layer B
    if horizon_min == "settle":
        horizon_cap_ts = settlement_ts_unix
    else:
        horizon_cap_ts = T0_unix + int(horizon_min * 60)
    entry_timeout_ts = T0_unix + 240 * 60  # 240 min default per spec

    # Step 3: walk trades forward looking for fill
    fill_time_unix = None
    fill_price = None
    for _, trade in trades_df.iterrows():
        t_unix = int(trade["created_time_ts"])
        if t_unix > entry_timeout_ts or t_unix > settlement_ts_unix:
            break
        if trade["taker_side"] == "yes" and float(trade["yes_price_dollars"]) <= our_bid_price:
            fill_time_unix = t_unix
            fill_price = our_bid_price
            break

    row = {
        "candidate_id": None,  # filled by caller
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
        "capture_A_net_dollars": None,
        "time_to_exit_A_minutes": None,
        "outcome_B": "unfilled" if fill_time_unix is None else None,
        "capture_B_gross_dollars": None,
        "capture_B_net_dollars": None,
        "time_to_exit_B_minutes": None,
        "entry_fee_dollars": 0.0,
        "exit_fee_A_dollars": None,
        "exit_fee_B_dollars": None,
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

    # Step 5: compute scenario A and B exit targets
    # Scenario A: exit_target = fill_price + limit_c/100 (anchored to entry; mirrors Layer B's evaluate_policy)
    scenario_A_target = fill_price + limit_c / 100.0
    # Scenario B: exit_target = fill_time_cell.yes_ask_close + limit_c/100
    # (re-evaluate the policy as if a fresh entry at fill_time using fill_time's cell)
    if fill_time_cell is not None:
        scenario_B_target = fill_time_cell["yes_ask_close"] + limit_c / 100.0
    else:
        # Fall back to A if no fill_time cell — A and B converge
        scenario_B_target = scenario_A_target

    # Step 6: walk forward from fill_time looking for kiss
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
        if trade["taker_side"] != "no":
            continue  # only taker-sells fill our resting sell
        yes_price = float(trade["yes_price_dollars"])
        if exit_A_time is None and yes_price >= scenario_A_target:
            exit_A_time = t_unix
            exit_A_price = yes_price
        if exit_B_time is None and yes_price >= scenario_B_target:
            exit_B_time = t_unix
            exit_B_price = yes_price
        if exit_A_time is not None and exit_B_time is not None:
            break

    # Resolve scenario A outcome
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
        row["capture_A_gross_dollars"] = None  # no exit price observed
        row["time_to_exit_A_minutes"] = None

    # Resolve scenario B outcome
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

    # Step 8: fees
    # Phase 1 placeholder: zero fees on entry+exit. Cat 2 fee table integration is Phase 2.
    # Documented in spec Section 3.1 step 8: producer applies per-(is_taker, price_bucket) lookup.
    row["entry_fee_dollars"] = 0.0
    row["exit_fee_A_dollars"] = 0.0 if exit_A_time is not None else None
    row["exit_fee_B_dollars"] = 0.0 if exit_B_time is not None else None
    row["capture_A_net_dollars"] = (
        row["capture_A_gross_dollars"] if row["capture_A_gross_dollars"] is not None else None
    )
    row["capture_B_net_dollars"] = (
        row["capture_B_gross_dollars"] if row["capture_B_gross_dollars"] is not None else None
    )

    return row


# ============================================================
# Phase 1 main
# ============================================================

def phase1():
    """Phase 1 calibration probe: 1 candidate × first 100 entry moments (chronological)."""
    out_dir = PROBE_DIR
    log_path = log_setup(out_dir)
    t_start = time.time()

    log("=" * 60, log_path)
    log("Forensic replay v1 — Phase 1 calibration probe", log_path)
    log("=" * 60, log_path)

    # Step 1: select candidate
    c = select_phase1_candidate()
    cid = candidate_id(c)
    mkey = manifest_key_for_candidate(c)
    log(f"Candidate: {cid}", log_path)
    log(f"Manifest key: {mkey}", log_path)
    log(f"Layer B simulated capture_mean=${c['capture_mean']:.4f}, fire_rate={c['fire_rate']:.3f}", log_path)
    log(f"Policy: type={c['policy_type']}, params={c['policy_params']}", log_path)
    policy_type = c["policy_type"]
    policy_params = json.loads(c["policy_params"])

    # Step 2: load tickers from manifest
    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)
    if mkey not in manifest:
        log(f"ABORT: manifest key {mkey} not found", log_path)
        sys.exit(1)
    tickers = manifest[mkey]["tickers"]
    log(f"Tickers in manifest: {len(tickers)}", log_path)

    # Step 3: enumerate moments across tickers, chronologically, until 100 collected
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
        log(f"Ticker {tickers_processed}/{len(tickers)}: {ticker} (moments collected so far: {moments_collected})", log_path)

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

        # Identify cell-matching moments (Section 3.1 step 1)
        matching_moments = []
        for i in range(len(candles_df)):
            t = int(timestamps[i])
            row = candles_df.iloc[i]
            if row["yes_bid_close"] is None or row["yes_ask_close"] is None:
                continue
            try:
                bid_f = float(row["yes_bid_close"])
                ask_f = float(row["yes_ask_close"])
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

        # Load trades once for this ticker (predicate pushdown)
        trades_df = load_ticker_trades(ticker, start_ts_unix=int(timestamps[0]))
        if trades_df is None:
            skipped_no_trades += 1
            continue

        # Process moments chronologically until budget hit or ticker exhausted
        for (i, t, bid_f, ask_f, regime, eb, sb, vi, cat) in matching_moments:
            if moments_collected >= PHASE1_MOMENT_BUDGET:
                break

            T0_cell = {
                "regime": regime, "entry_band_idx": eb,
                "spread_band": sb, "volume_intensity": vi, "category": cat,
                "yes_bid_close": bid_f, "yes_ask_close": ask_f,
            }
            # Trades from T0 forward only
            forward_trades = trades_df[trades_df["created_time_ts"] >= t].reset_index(drop=True)
            row = replay_one_moment(
                ticker=ticker,
                candles_df=candles_df,
                trades_df=forward_trades,
                T0_unix=t,
                T0_cell=T0_cell,
                policy_type=policy_type,
                policy_params=policy_params,
                settlement_ts_unix=settlement_ts_unix,
                settlement_value=settlement_value,
                match_start_ts=match_start_ts,
                log_path=log_path,
                log_warnings=True,
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

    # Outcome distribution
    df = pd.DataFrame(rows)
    log("", log_path)
    log("=== Outcome distribution ===", log_path)
    log(f"  Scenario A: {df['outcome_A'].value_counts().to_dict()}", log_path)
    log(f"  Scenario B: {df['outcome_B'].value_counts().to_dict()}", log_path)
    fill_count = df["fill_time_unix"].notna().sum()
    log(f"  Fill rate: {fill_count}/{len(df)} = {fill_count/len(df):.3f}", log_path)
    if fill_count > 0:
        log(f"  Cell drift at fill: {df['cell_drift_at_fill'].sum()}/{fill_count} = {df['cell_drift_at_fill'].sum()/fill_count:.3f}", log_path)

    captures_A = df["capture_A_net_dollars"].dropna()
    captures_B = df["capture_B_net_dollars"].dropna()
    if len(captures_A) > 0:
        log(f"  Scenario A capture: n={len(captures_A)}, mean=${captures_A.mean():.4f}, median=${captures_A.median():.4f}, min=${captures_A.min():.4f}, max=${captures_A.max():.4f}", log_path)
    if len(captures_B) > 0:
        log(f"  Scenario B capture: n={len(captures_B)}, mean=${captures_B.mean():.4f}, median=${captures_B.median():.4f}, min=${captures_B.min():.4f}, max=${captures_B.max():.4f}", log_path)

    log(f"  Layer B simulated capture_mean: ${c['capture_mean']:.4f}", log_path)

    # Write replay_tape parquet
    out_path = os.path.join(out_dir, "replay_tape_phase1.parquet")
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, out_path, compression="snappy")
    log(f"Wrote {len(df)} rows to {out_path}", log_path)
    log(f"Output size: {os.path.getsize(out_path):,} bytes", log_path)

    # Run summary
    summary = {
        "phase": 1,
        "candidate_id": cid,
        "manifest_key": mkey,
        "moments_collected": int(moments_collected),
        "moments_budget": PHASE1_MOMENT_BUDGET,
        "tickers_processed": tickers_processed,
        "skipped_meta": skipped_meta,
        "skipped_no_candles": skipped_no_candles,
        "skipped_no_trades": skipped_no_trades,
        "runtime_seconds": round(elapsed, 1),
        "layer_b_capture_mean": float(c["capture_mean"]),
        "layer_b_fire_rate": float(c["fire_rate"]),
        "layer_b_n_simulated": int(c["n_simulated"]),
        "fill_rate": float(fill_count / max(1, len(df))),
        "scenario_A_outcomes": df["outcome_A"].value_counts().to_dict(),
        "scenario_B_outcomes": df["outcome_B"].value_counts().to_dict(),
        "scenario_A_capture_mean": float(captures_A.mean()) if len(captures_A) > 0 else None,
        "scenario_B_capture_mean": float(captures_B.mean()) if len(captures_B) > 0 else None,
        "cell_drift_rate_at_fill": float(df["cell_drift_at_fill"].sum() / max(1, fill_count)) if fill_count > 0 else None,
        "spec_commits": ["40db959", "3b62039"],
    }
    summary_path = os.path.join(out_dir, "run_summary_phase1.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log(f"Wrote summary to {summary_path}", log_path)
    log("=" * 60, log_path)


# ============================================================
# Phase 2 main
# ============================================================

def phase2():
    """Phase 2 single-candidate full run: 1 candidate × ALL entry moments.

    Per spec Section 5.2: confirms per-candidate runtime estimate scales linearly
    with moment count, validates memory profile under realistic load. Output to
    data/durable/forensic_replay_v1/phase2/. Gating for Phase 3.

    Same candidate as Phase 1 (rank-7 non-settle premarket: ATP_CHALL 80-90 tight
    low / limit / limit_c=10) so that Phase 2 distributions are directly
    comparable to Phase 1's 100-moment subset.
    """
    out_dir = os.path.join(OUT_DIR, "phase2")
    log_path = log_setup(out_dir)
    t_start = time.time()

    log("=" * 60, log_path)
    log("Forensic replay v1 - Phase 2 single-candidate full run", log_path)
    log("=" * 60, log_path)

    c = select_phase1_candidate()
    cid = candidate_id(c)
    mkey = manifest_key_for_candidate(c)
    log(f"Candidate: {cid}", log_path)
    log(f"Manifest key: {mkey}", log_path)
    log(f"Layer B simulated capture_mean=${c['capture_mean']:.4f}, fire_rate={c['fire_rate']:.3f}, n_simulated={int(c['n_simulated'])}", log_path)
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

    # Phase 2: NO MOMENT BUDGET - process ALL cell-matching moments across ALL tickers
    for ticker in tickers:
        tickers_processed += 1
        log(f"Ticker {tickers_processed}/{len(tickers)}: {ticker} (cumulative moments: {moments_collected})", log_path)

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
            row = candles_df.iloc[i]
            if row["yes_bid_close"] is None or row["yes_ask_close"] is None:
                continue
            try:
                bid_f = float(row["yes_bid_close"])
                ask_f = float(row["yes_ask_close"])
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
            T0_cell = {
                "regime": regime, "entry_band_idx": eb,
                "spread_band": sb, "volume_intensity": vi, "category": cat,
                "yes_bid_close": bid_f, "yes_ask_close": ask_f,
            }
            forward_trades = trades_df[trades_df["created_time_ts"] >= t].reset_index(drop=True)
            row = replay_one_moment(
                ticker=ticker,
                candles_df=candles_df,
                trades_df=forward_trades,
                T0_unix=t,
                T0_cell=T0_cell,
                policy_type=policy_type,
                policy_params=policy_params,
                settlement_ts_unix=settlement_ts_unix,
                settlement_value=settlement_value,
                match_start_ts=match_start_ts,
                log_path=log_path,
                log_warnings=False,
            )
            row["candidate_id"] = cid
            rows.append(row)
            moments_collected += 1

    elapsed = time.time() - t_start
    log("", log_path)
    log("=" * 60, log_path)
    log(f"Phase 2 complete. Runtime: {elapsed:.1f}s ({elapsed/60:.2f} min)", log_path)
    log(f"Moments collected: {moments_collected}", log_path)
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
    fill_count = df["fill_time_unix"].notna().sum()
    log(f"  Fill rate: {fill_count}/{len(df)} = {fill_count/max(1,len(df)):.4f}", log_path)
    if fill_count > 0:
        log(f"  Cell drift at fill: {df['cell_drift_at_fill'].sum()}/{fill_count} = {df['cell_drift_at_fill'].sum()/fill_count:.4f}", log_path)

    captures_A = df["capture_A_net_dollars"].dropna()
    captures_B = df["capture_B_net_dollars"].dropna()
    if len(captures_A) > 0:
        log(f"  Scenario A capture: n={len(captures_A)}, mean=${captures_A.mean():.4f}, p10=${captures_A.quantile(0.1):.4f}, p50=${captures_A.median():.4f}, p90=${captures_A.quantile(0.9):.4f}, min=${captures_A.min():.4f}, max=${captures_A.max():.4f}", log_path)
    if len(captures_B) > 0:
        log(f"  Scenario B capture: n={len(captures_B)}, mean=${captures_B.mean():.4f}, p10=${captures_B.quantile(0.1):.4f}, p50=${captures_B.median():.4f}, p90=${captures_B.quantile(0.9):.4f}, min=${captures_B.min():.4f}, max=${captures_B.max():.4f}", log_path)
    log(f"  Layer B simulated capture_mean: ${c['capture_mean']:.4f}", log_path)
    if len(captures_A) > 0:
        log(f"  Realized A vs simulated delta: ${captures_A.mean() - c['capture_mean']:.4f} ({100*(captures_A.mean()-c['capture_mean'])/c['capture_mean']:+.1f}%)", log_path)

    paired = df.dropna(subset=["capture_A_net_dollars", "capture_B_net_dollars"])
    if len(paired) > 0:
        delta_AB = paired["capture_A_net_dollars"] - paired["capture_B_net_dollars"]
        log(f"  A vs B paired delta: n={len(paired)}, mean=${delta_AB.mean():.4f}, |median|=${delta_AB.abs().median():.4f}", log_path)
        try:
            from scipy.stats import spearmanr
            rho, pval = spearmanr(paired["capture_A_net_dollars"], paired["capture_B_net_dollars"])
            log(f"  A vs B Spearman rho: {rho:.4f} (p={pval:.4g})", log_path)
        except ImportError:
            log(f"  scipy not available - skipping Spearman; using pandas .corr() instead", log_path)
            rho = paired["capture_A_net_dollars"].corr(paired["capture_B_net_dollars"], method="spearman")
            log(f"  A vs B Spearman rho (pandas): {rho:.4f}", log_path)

    phase1_summary_path = os.path.join(OUT_DIR, "probe", "run_summary_phase1.json")
    if os.path.exists(phase1_summary_path):
        with open(phase1_summary_path) as f:
            p1 = json.load(f)
        log("", log_path)
        log("=== Phase 1 vs Phase 2 stability ===", log_path)
        log(f"  Phase 1: n=100, fill_rate={p1['fill_rate']:.4f}, cell_drift={p1.get('cell_drift_rate_at_fill')}, capture_A_mean=${p1.get('scenario_A_capture_mean'):.4f}", log_path)
        log(f"  Phase 2: n={len(df)}, fill_rate={fill_count/max(1,len(df)):.4f}, cell_drift={df['cell_drift_at_fill'].sum()/max(1,fill_count):.4f}, capture_A_mean=${captures_A.mean():.4f}", log_path)

    out_path = os.path.join(out_dir, "replay_tape_phase2.parquet")
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, out_path, compression="snappy")
    log(f"Wrote {len(df)} rows to {out_path}", log_path)
    log(f"Output size: {os.path.getsize(out_path):,} bytes", log_path)

    summary = {
        "phase": 2,
        "candidate_id": cid,
        "manifest_key": mkey,
        "moments_collected": int(moments_collected),
        "tickers_processed": tickers_processed,
        "skipped_meta": skipped_meta,
        "skipped_no_candles": skipped_no_candles,
        "skipped_no_trades": skipped_no_trades,
        "runtime_seconds": round(elapsed, 1),
        "layer_b_capture_mean": float(c["capture_mean"]),
        "layer_b_fire_rate": float(c["fire_rate"]),
        "layer_b_n_simulated": int(c["n_simulated"]),
        "fill_rate": float(fill_count / max(1, len(df))),
        "scenario_A_outcomes": df["outcome_A"].value_counts().to_dict(),
        "scenario_B_outcomes": df["outcome_B"].value_counts().to_dict(),
        "scenario_A_capture_mean": float(captures_A.mean()) if len(captures_A) > 0 else None,
        "scenario_A_capture_p10": float(captures_A.quantile(0.1)) if len(captures_A) > 0 else None,
        "scenario_A_capture_p50": float(captures_A.quantile(0.5)) if len(captures_A) > 0 else None,
        "scenario_A_capture_p90": float(captures_A.quantile(0.9)) if len(captures_A) > 0 else None,
        "scenario_B_capture_mean": float(captures_B.mean()) if len(captures_B) > 0 else None,
        "scenario_B_capture_p10": float(captures_B.quantile(0.1)) if len(captures_B) > 0 else None,
        "scenario_B_capture_p50": float(captures_B.quantile(0.5)) if len(captures_B) > 0 else None,
        "scenario_B_capture_p90": float(captures_B.quantile(0.9)) if len(captures_B) > 0 else None,
        "cell_drift_rate_at_fill": float(df["cell_drift_at_fill"].sum() / max(1, fill_count)) if fill_count > 0 else None,
        "spec_commits": ["40db959", "3b62039"],
        "producer_commit_at_run": "43ae049_or_later",
    }
    summary_path = os.path.join(out_dir, "run_summary_phase2.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log(f"Wrote summary to {summary_path}", log_path)
    log("=" * 60, log_path)


# ============================================================
# Phase 3: candidate selection
# ============================================================

def select_top_n_candidates(n_per_cat=20):
    """Top N non-settle premarket candidates per category by Layer B capture_mean.

    Per spec Section 2 Decision 1:
    - channel=premarket, n_simulated>=50, exclude settle-horizon time_stops.
    - Rank within each (channel, category); return top n_per_cat per category.
    - 4 categories x n_per_cat -> N candidates total (default 80).
    """
    t = pq.read_table(LAYER_B_PARQUET).to_pandas()
    pre = t[(t["channel"] == "premarket") & (t["n_simulated"] >= 50)].copy()

    def is_settle(row):
        if row["policy_type"] not in ("time_stop", "limit_time_stop"):
            return False
        try:
            params = json.loads(row["policy_params"])
        except Exception:
            return False
        return params.get("horizon_min") == "settle"

    pre["is_settle"] = pre.apply(is_settle, axis=1)
    non_settle = pre[~pre["is_settle"]].copy()

    selected_rows = []
    for cat in ("ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"):
        cat_df = non_settle[non_settle["category"] == cat]
        top = cat_df.sort_values("capture_mean", ascending=False).head(n_per_cat)
        selected_rows.append(top)
    return pd.concat(selected_rows, ignore_index=True)


# ============================================================
# Phase 3 main
# ============================================================

def phase3(n_per_cat=20):
    """Full forensic replay: top-N per (channel, category) candidates evaluated end-to-end.

    Outputs to data/durable/forensic_replay_v1/phase3/:
    - replay_tape.parquet (per-moment, spec Output 1)
    - candidate_summary.parquet (one row per candidate, spec Output 2)
    - scenario_comparison.parquet (per-candidate A/B, spec Output 3)
    - cell_drift_per_minute.parquet (per-candidate per-5min drift, spec Output 4)
    - run_summary.json (with embedded validation gate per spec Section 6)
    """
    out_dir = os.path.join(OUT_DIR, "phase3")
    log_path = log_setup(out_dir)
    t_start = time.time()

    log("=" * 60, log_path)
    log(f"Forensic replay v1 - Phase 3 (top {n_per_cat} per category)", log_path)
    log("=" * 60, log_path)

    candidates = select_top_n_candidates(n_per_cat=n_per_cat)
    log(f"Selected {len(candidates)} candidates across 4 categories", log_path)
    cat_counts = candidates["category"].value_counts().to_dict()
    for cat in ("ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"):
        n = cat_counts.get(cat, 0)
        cat_df = candidates[candidates["category"] == cat]
        if len(cat_df) > 0:
            log(f"  {cat}: {n}, capture_mean ${cat_df['capture_mean'].min():.4f} to ${cat_df['capture_mean'].max():.4f}", log_path)
        else:
            log(f"  {cat}: 0 candidates", log_path)

    with open(SAMPLE_MANIFEST) as f:
        manifest = json.load(f)

    # Per-candidate incremental writes — produces partial-recoverable output.
    # If the run is killed mid-loop, every candidate completed so far has its own
    # replay_tape_cand_NNN.parquet and its row appended to the aggregate JSONL.
    candidate_summary_rows = []
    scenario_comparison_rows = []
    cell_drift_rows = []
    # Per-candidate replay_tape parquets are written incrementally per-candidate, then merged at end.
    summary_jsonl_path = os.path.join(out_dir, "_progress_summary.jsonl")
    open(summary_jsonl_path, "w").close()  # reset

    for cidx in range(len(candidates)):
        cand_t_start = time.time()
        c = candidates.iloc[cidx]
        cid = candidate_id(c)
        mkey = manifest_key_for_candidate(c)
        log("", log_path)
        log(f"--- Candidate {cidx+1}/{len(candidates)}: {cid} ---", log_path)
        log(f"    mkey={mkey}, sim_mean=${c['capture_mean']:.4f}, sim_fire={c['fire_rate']:.3f}, n_sim={int(c['n_simulated'])}", log_path)

        if mkey not in manifest:
            log(f"    SKIP: manifest key not found", log_path)
            continue

        policy_type = c["policy_type"]
        policy_params = json.loads(c["policy_params"])
        tickers = manifest[mkey]["tickers"]

        cand_rows = []
        moments_collected = 0
        skipped_meta = 0
        skipped_no_candles = 0
        skipped_no_trades = 0
        drift_per_minute = {m: [0, 0] for m in range(0, 241, 5)}

        for ticker in tickers:
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
                cat_ck = categorize(ticker)
                tp = mkey.split("__")
                target_regime, target_eb_str, target_sb, target_vi, target_cat = tp
                if (regime == target_regime and eb == int(target_eb_str)
                    and sb == target_sb and vi == target_vi and cat_ck == target_cat):
                    matching_moments.append((i, t, bid_f, ask_f, regime, eb, sb, vi, cat_ck))

            if not matching_moments:
                continue

            trades_df = load_ticker_trades(ticker, start_ts_unix=int(timestamps[0]))
            if trades_df is None:
                skipped_no_trades += 1
                continue

            for (i, t, bid_f, ask_f, regime, eb, sb, vi, cat_ck) in matching_moments:
                T0_cell = {
                    "regime": regime, "entry_band_idx": eb, "spread_band": sb,
                    "volume_intensity": vi, "category": cat_ck,
                    "yes_bid_close": bid_f, "yes_ask_close": ask_f,
                }
                forward_trades = trades_df[trades_df["created_time_ts"] >= t].reset_index(drop=True)
                row = replay_one_moment(
                    ticker=ticker, candles_df=candles_df, trades_df=forward_trades,
                    T0_unix=t, T0_cell=T0_cell,
                    policy_type=policy_type, policy_params=policy_params,
                    settlement_ts_unix=settlement_ts_unix, settlement_value=settlement_value,
                    match_start_ts=match_start_ts, log_path=log_path, log_warnings=False,
                )
                row["candidate_id"] = cid
                cand_rows.append(row)
                moments_collected += 1

                T0_cell_key = cell_key_str(T0_cell)
                for offset in range(0, 241, 5):
                    minute_ts = ((t + offset * 60) // 60) * 60
                    state = cell_state_at_minute(candles_df, minute_ts, match_start_ts, settlement_ts_unix, ticker)
                    if state is not None:
                        drift_per_minute[offset][0] += 1
                        if cell_key_str(state) == T0_cell_key:
                            drift_per_minute[offset][1] += 1

        cand_elapsed = time.time() - cand_t_start

        df = pd.DataFrame(cand_rows)
        n = len(df)
        fill_count = int(df["fill_time_unix"].notna().sum()) if n > 0 else 0
        captures_A = df["capture_A_net_dollars"].dropna() if n > 0 else pd.Series(dtype=float)
        captures_B = df["capture_B_net_dollars"].dropna() if n > 0 else pd.Series(dtype=float)
        win_rate_A = float((captures_A > 0).mean()) if len(captures_A) > 0 else None
        win_rate_B = float((captures_B > 0).mean()) if len(captures_B) > 0 else None
        cell_drift_rate = float(df["cell_drift_at_fill"].sum() / max(1, fill_count)) if fill_count > 0 else None
        ttf_p50 = float(df["time_to_fill_minutes"].median()) if n > 0 and df["time_to_fill_minutes"].notna().any() else None
        tta_p50 = float(df["time_to_exit_A_minutes"].median()) if n > 0 and df["time_to_exit_A_minutes"].notna().any() else None
        ttb_p50 = float(df["time_to_exit_B_minutes"].median()) if n > 0 and df["time_to_exit_B_minutes"].notna().any() else None

        summary_row = {
            "candidate_id": cid,
            "channel": c["channel"], "category": c["category"],
            "entry_band_lo": int(c["entry_band_lo"]), "entry_band_hi": int(c["entry_band_hi"]),
            "spread_band": c["spread_band"], "volume_intensity": c["volume_intensity"],
            "policy_type": c["policy_type"], "policy_params": c["policy_params"],
            "n_simulated": int(c["n_simulated"]),
            "fire_rate_simulated": float(c["fire_rate"]),
            "capture_mean_simulated": float(c["capture_mean"]),
            "capture_p10_simulated": float(c.get("capture_p10", float("nan"))),
            "capture_p50_simulated": float(c.get("capture_p50", float("nan"))),
            "capture_p90_simulated": float(c.get("capture_p90", float("nan"))),
            "n_replay_moments": n,
            "replay_fill_rate": float(fill_count / max(1, n)),
            "replay_capture_A_net_mean": float(captures_A.mean()) if len(captures_A) > 0 else None,
            "replay_capture_A_net_p10": float(captures_A.quantile(0.10)) if len(captures_A) > 0 else None,
            "replay_capture_A_net_p50": float(captures_A.quantile(0.50)) if len(captures_A) > 0 else None,
            "replay_capture_A_net_p90": float(captures_A.quantile(0.90)) if len(captures_A) > 0 else None,
            "replay_capture_B_net_mean": float(captures_B.mean()) if len(captures_B) > 0 else None,
            "replay_capture_B_net_p10": float(captures_B.quantile(0.10)) if len(captures_B) > 0 else None,
            "replay_capture_B_net_p50": float(captures_B.quantile(0.50)) if len(captures_B) > 0 else None,
            "replay_capture_B_net_p90": float(captures_B.quantile(0.90)) if len(captures_B) > 0 else None,
            "replay_win_rate_A": win_rate_A, "replay_win_rate_B": win_rate_B,
            "replay_time_to_fill_p50": ttf_p50,
            "replay_time_to_exit_A_p50": tta_p50, "replay_time_to_exit_B_p50": ttb_p50,
            "cell_drift_rate_at_fill": cell_drift_rate,
            "simulated_vs_realized_delta_A": (float(c["capture_mean"]) - float(captures_A.mean())) if len(captures_A) > 0 else None,
            "simulated_vs_realized_delta_B": (float(c["capture_mean"]) - float(captures_B.mean())) if len(captures_B) > 0 else None,
            "candidate_runtime_seconds": round(cand_elapsed, 1),
            "skipped_meta": skipped_meta,
            "skipped_no_candles": skipped_no_candles,
            "skipped_no_trades": skipped_no_trades,
        }
        candidate_summary_rows.append(summary_row)

        paired = df.dropna(subset=["capture_A_net_dollars", "capture_B_net_dollars"]) if n > 0 else pd.DataFrame()
        if len(paired) > 1:
            try:
                from scipy.stats import spearmanr
                rho, pval = spearmanr(paired["capture_A_net_dollars"], paired["capture_B_net_dollars"])
            except Exception:
                rho = paired["capture_A_net_dollars"].corr(paired["capture_B_net_dollars"], method="spearman")
                pval = None
            mean_delta = float((paired["capture_A_net_dollars"] - paired["capture_B_net_dollars"]).mean())
        else:
            rho, pval, mean_delta = None, None, None

        cells_diverged_count = int(df["cell_drift_at_fill"].sum()) if n > 0 else 0
        scenario_comparison_rows.append({
            "candidate_id": cid,
            "n_paired_moments": int(len(paired)),
            "corr_A_B_spearman": float(rho) if rho is not None else None,
            "corr_A_B_pval": float(pval) if pval is not None else None,
            "mean_delta_A_minus_B": mean_delta,
            "cells_diverged_count": cells_diverged_count,
            "cells_diverged_pct": float(cells_diverged_count / max(1, fill_count)),
        })

        for minute_offset, (n_total, n_match) in drift_per_minute.items():
            cell_drift_rows.append({
                "candidate_id": cid, "minutes_since_T0": minute_offset,
                "n_moments_total": n_total, "n_moments_cell_still_matches": n_match,
                "pct_still_matches": float(n_match / max(1, n_total)),
            })

        # Per-candidate replay_tape write — incremental, on disk
        if cand_rows:
            tape_path = os.path.join(out_dir, f"replay_tape_cand_{cidx:03d}.parquet")
            df_cand = pd.DataFrame(cand_rows)
            pq.write_table(pa.Table.from_pandas(df_cand, preserve_index=False), tape_path, compression="snappy")
            del df_cand

        # Per-candidate summary append to progress JSONL — survives kill
        with open(summary_jsonl_path, "a") as fjl:
            fjl.write(json.dumps(summary_row, default=str) + "\n")

        a_mean_str = f"{float(captures_A.mean()):.4f}" if len(captures_A) > 0 else "nan"
        b_mean_str = f"{float(captures_B.mean()):.4f}" if len(captures_B) > 0 else "nan"
        delta_a_str = f"{(float(c['capture_mean']) - float(captures_A.mean())):.4f}" if len(captures_A) > 0 else "nan"
        log(f"    done: n={n}, fill_rate={fill_count/max(1,n):.3f}, A_mean=${a_mean_str}, B_mean=${b_mean_str}, sim_delta_A=${delta_a_str}, runtime={cand_elapsed:.1f}s", log_path)

        del df, cand_rows, captures_A, captures_B, paired

        if (cidx + 1) % 10 == 0:
            elapsed_total = time.time() - t_start
            log(f"    [memsnap cand {cidx+1}/{len(candidates)}, elapsed={elapsed_total:.0f}s]", log_path)
            try:
                with open("/proc/meminfo") as f:
                    for ml in f:
                        if ml.startswith(("MemTotal", "MemFree", "MemAvailable", "Buffers", "Cached", "SwapFree")):
                            log(f"      {ml.strip()}", log_path)
            except Exception:
                pass

    elapsed_total = time.time() - t_start
    log("", log_path)
    log("=" * 60, log_path)
    total_moments = sum(int(s.get("n_replay_moments", 0)) for s in candidate_summary_rows)
    log(f"Phase 3 candidate-loop done. runtime={elapsed_total:.1f}s ({elapsed_total/60:.2f} min)", log_path)
    log(f"Candidates processed: {len(candidate_summary_rows)}/{len(candidates)}", log_path)
    log(f"Total replay moments: {total_moments}", log_path)
    log("=" * 60, log_path)

    log("Merging per-candidate replay_tape parquets ...", log_path)
    import glob
    cand_tape_paths = sorted(glob.glob(os.path.join(out_dir, "replay_tape_cand_*.parquet")))
    log(f"  found {len(cand_tape_paths)} per-candidate tape parquets", log_path)
    if cand_tape_paths:
        merged_dfs = []
        for tp in cand_tape_paths:
            d = pq.read_table(tp).to_pandas()
            merged_dfs.append(d)
        merged = pd.concat(merged_dfs, ignore_index=True)
        out_path = os.path.join(out_dir, "replay_tape.parquet")
        pq.write_table(pa.Table.from_pandas(merged, preserve_index=False), out_path, compression="snappy")
        log(f"  wrote merged {len(merged)} rows, {os.path.getsize(out_path):,} bytes", log_path)
        del merged, merged_dfs
        # Per-candidate intermediates kept on disk for diagnostic / resume use.
    else:
        log(f"  no per-candidate tapes found - empty replay", log_path)

    log("Writing candidate_summary.parquet ...", log_path)
    df_summary = pd.DataFrame(candidate_summary_rows)
    out_path = os.path.join(out_dir, "candidate_summary.parquet")
    pq.write_table(pa.Table.from_pandas(df_summary, preserve_index=False), out_path, compression="snappy")
    log(f"  wrote {len(df_summary)} rows, {os.path.getsize(out_path):,} bytes", log_path)

    log("Writing scenario_comparison.parquet ...", log_path)
    df_scen = pd.DataFrame(scenario_comparison_rows)
    out_path = os.path.join(out_dir, "scenario_comparison.parquet")
    pq.write_table(pa.Table.from_pandas(df_scen, preserve_index=False), out_path, compression="snappy")
    log(f"  wrote {len(df_scen)} rows, {os.path.getsize(out_path):,} bytes", log_path)

    log("Writing cell_drift_per_minute.parquet ...", log_path)
    df_drift = pd.DataFrame(cell_drift_rows)
    out_path = os.path.join(out_dir, "cell_drift_per_minute.parquet")
    pq.write_table(pa.Table.from_pandas(df_drift, preserve_index=False), out_path, compression="snappy")
    log(f"  wrote {len(df_drift)} rows, {os.path.getsize(out_path):,} bytes", log_path)

    log("", log_path)
    log("=== Validation gate (spec Section 6) ===", log_path)

    check1_count = int((df_summary["n_replay_moments"] >= 50).sum())
    check1_pass = bool(check1_count == len(df_summary))
    log(f"  Check 1 (n_replay_moments >= 50): {check1_count}/{len(df_summary)} {'PASS' if check1_pass else 'FAIL'}", log_path)

    check2_in_band = ((df_summary["replay_fill_rate"] >= 0.05) & (df_summary["replay_fill_rate"] <= 0.95))
    check2_pass = bool(check2_in_band.all())
    log(f"  Check 2 (fill_rate in [0.05,0.95]): {int(check2_in_band.sum())}/{len(df_summary)} {'PASS' if check2_pass else 'FAIL'}", log_path)
    if not check2_pass:
        outliers = df_summary[~check2_in_band][["candidate_id","replay_fill_rate"]].head(5)
        log(f"    outliers head: {outliers.to_dict('records')}", log_path)

    deltas = df_summary["replay_capture_A_net_mean"] - df_summary["replay_capture_B_net_mean"]
    deltas_clean = deltas.dropna()
    if len(deltas_clean) > 0:
        mean_abs_delta = float(deltas_clean.abs().mean())
        directional = float((deltas_clean < 0).mean())
        check3_pass = bool((mean_abs_delta < 0.01) or (directional > 0.7) or (directional < 0.3))
        log(f"  Check 3 (A/B coherence): mean|A-B|=${mean_abs_delta:.4f}, B>A in {directional:.1%} {'PASS' if check3_pass else 'FAIL'}", log_path)
    else:
        check3_pass, mean_abs_delta, directional = False, None, None
        log(f"  Check 3: no paired data, FAIL", log_path)

    sim_vs_real_A = (df_summary["replay_capture_A_net_mean"] <= df_summary["capture_mean_simulated"])
    sim_vs_real_A_clean = sim_vs_real_A.dropna()
    check4_pct = float(sim_vs_real_A_clean.mean()) if len(sim_vs_real_A_clean) > 0 else 0.0
    check4_pass = bool(check4_pct >= 0.90)
    log(f"  Check 4 (realized<=simulated): {check4_pct:.1%} {'PASS' if check4_pass else 'FAIL'}", log_path)

    paired_summary = df_summary.dropna(subset=["capture_mean_simulated", "replay_capture_A_net_mean"])
    if len(paired_summary) >= 5:
        try:
            from scipy.stats import spearmanr
            rho_sim, pval_sim = spearmanr(paired_summary["capture_mean_simulated"], paired_summary["replay_capture_A_net_mean"])
            check5_pass = bool(rho_sim is not None and rho_sim >= 0.75)
            log(f"  Check 5 (Spearman sim vs real): rho={rho_sim:.4f} p={pval_sim:.4g} n={len(paired_summary)} {'PASS' if check5_pass else 'FAIL'}", log_path)
        except Exception as e:
            rho_sim = paired_summary["capture_mean_simulated"].corr(paired_summary["replay_capture_A_net_mean"], method="spearman")
            pval_sim = None
            check5_pass = bool(rho_sim is not None and rho_sim >= 0.75)
            log(f"  Check 5 (Spearman pandas fallback): rho={rho_sim} {'PASS' if check5_pass else 'FAIL'}", log_path)
    else:
        check5_pass, rho_sim, pval_sim = False, None, None
        log(f"  Check 5: insufficient data n={len(paired_summary)}, FAIL", log_path)

    drift_t30 = df_drift[df_drift["minutes_since_T0"] == 30]
    median_drift_t30 = float(drift_t30["pct_still_matches"].median()) if len(drift_t30) > 0 else None
    log(f"  Check 6 (informative): median pct_still_matches at T+30 = {median_drift_t30}", log_path)

    overall_pass = check1_pass and check2_pass and check3_pass and check4_pass and check5_pass
    log("", log_path)
    log(f"=== OVERALL Phase 3 verdict: {'PASS' if overall_pass else 'FAIL'} ===", log_path)
    log("=" * 60, log_path)

    summary = {
        "phase": 3,
        "n_per_cat": n_per_cat,
        "candidates_total": int(len(candidates)),
        "candidates_processed": int(len(candidate_summary_rows)),
        "total_replay_moments": int(total_moments),
        "runtime_seconds": round(elapsed_total, 1),
        "runtime_minutes": round(elapsed_total / 60, 2),
        "spec_commits": ["40db959", "3b62039"],
        "validation_gate": {
            "check1_n_moments_50_pass": check1_pass,
            "check1_count": check1_count,
            "check2_fill_rate_band_pass": check2_pass,
            "check2_in_band_count": int(check2_in_band.sum()),
            "check3_AB_coherence_pass": check3_pass,
            "check3_mean_abs_delta": mean_abs_delta,
            "check3_B_gt_A_pct": directional,
            "check4_realized_le_simulated_pass": check4_pass,
            "check4_pct_satisfied": check4_pct,
            "check5_spearman_rank_pass": check5_pass,
            "check5_rho": float(rho_sim) if rho_sim is not None else None,
            "check5_pval": float(pval_sim) if pval_sim is not None else None,
            "check6_median_drift_t30": median_drift_t30,
            "OVERALL_PASS": overall_pass,
        },
    }
    summary_path = os.path.join(out_dir, "run_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log(f"Wrote run_summary.json", log_path)


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
    else:
        print(f"Phase {args.phase} not implemented.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
