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
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], required=True)
    args = parser.parse_args()

    if args.phase == 1:
        phase1()
    else:
        print(f"Phase {args.phase} not yet implemented. Phase 1 only for this commit.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
