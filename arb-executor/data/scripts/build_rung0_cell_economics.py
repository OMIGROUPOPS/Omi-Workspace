#!/usr/bin/env python3
"""Rung 0 producer v1.1 — canonical exit-optimized cell economics.

Spec: docs/rung0_cell_economics_spec.md commit 87103d0d.
Output: data/durable/rung0_cell_economics/cell_economics.parquet (36 cols).

Phases:
  --phase 1 --ticker T  : single ticker (Phase 1)
  --phase 2             : stratified 160-ticker sample (Phase 2)
  --phase 3             : full binary-outcome corpus (Phase 3)

Per-ticker procedure: read metadata + per_minute_features + g9_trades slice;
find T-20m anchor trade (±2min); walk trades T-20m → settlement_ts; compute
dual peak (full + pre-resolution at first 99¢/1¢ touch); emit 36-column row.

Disciplines:
  - C36: trade tape canonical; count_fp > 0 filter for trade-count aggregates
  - C37: pre-replace validation gate on Phase 3
  - G21: ET on operator-facing surfaces; UTC at raw-bytes layer only
  - F29: defensive column-name normalization on trade tape (yes_price_dollars
         vs yes_price); T17 normalized to _dollars uniform but probe defensive
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from zoneinfo import ZoneInfo


# ============================================================
# pandas 3.0 + pyarrow 24 compat patch
# ------------------------------------------------------------
# pyarrow.pandas_compat.make_datetimetz calls pa.lib.string_to_tzinfo() which
# returns a pytz.tzfile object. pandas 3.0's DatetimeTZDtype constructor calls
# timezones.tz_standardize() which no longer accepts pytz objects directly,
# raising AttributeError("'NoneType' object has no attribute 'timezone'").
# We patch make_datetimetz to pass the tz STRING straight to DatetimeTZDtype,
# which pandas 3.0 accepts cleanly.
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

# ============================================================
# Constants
# ============================================================
DUR = "/root/Omi-Workspace/arb-executor/data/durable"
PMF = f"{DUR}/per_minute_universe/per_minute_features.parquet"
TRADES = f"{DUR}/g9_trades.parquet"
META = f"{DUR}/g9_metadata.parquet"
OUT_DIR = f"{DUR}/rung0_cell_economics"
PARTIAL_DIR = f"{OUT_DIR}/_partial"
PROBE_DIR = f"{OUT_DIR}/probe"

T20M_OFFSET_SEC = 20 * 60  # 1200
ANCHOR_TOLERANCE_SEC = 120  # ±2min
ANCHOR_EXACT_SEC = 5  # ±5s for "exact"
EXTREME_HIGH = 0.99
EXTREME_LOW = 0.01
PHASE2_SAMPLE_SEED = 42
PHASE2_N_MATCHES_TARGET = 80  # 80 × 2 sides = 160 tickers
PHASE2_BATCH_SIZE = 500  # for partial-write kill-resilience
PHASE3_BATCH_SIZE = 2000

CATEGORIES = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"]
PHASE_LABELS = [
    "PHASE_1_FORMATION", "PHASE_2_STABLE_PREMATCH",
    "PHASE_3_PREMATCH_SURGE", "PHASE_4_IN_MATCH",
]

# Pandas 3.x rejects pytz timezone objects in tz_convert; use string for pandas
# ops and ZoneInfo for stdlib datetime ops.
ET_TZ_STR = "America/New_York"
UTC_TZ_STR = "UTC"
ET_TZ = ZoneInfo("America/New_York")
UTC_TZ = ZoneInfo("UTC")


def log(msg):
    """Log with ET timestamp."""
    t = datetime.now(ET_TZ).strftime("%Y-%m-%d %H:%M:%S ET")
    print(f"[{t}] {msg}", flush=True)


def utc_int_to_et(unix_sec):
    """Convert int64 Unix seconds (UTC) → tz-aware datetime in ET."""
    if unix_sec is None or (isinstance(unix_sec, float) and np.isnan(unix_sec)):
        return None
    return datetime.fromtimestamp(int(unix_sec), tz=UTC_TZ).astimezone(ET_TZ)


def iso_to_et(iso_str):
    """Convert ISO 8601 UTC string → tz-aware datetime in ET."""
    if iso_str is None or (isinstance(iso_str, float) and np.isnan(iso_str)):
        return None
    return pd.to_datetime(iso_str, format="ISO8601").tz_convert(ET_TZ_STR)


def price_band_5c(price):
    """Return 5¢ band label '0.30-0.35' for price in [0, 1]; None if extreme."""
    if price is None or np.isnan(price):
        return None
    if price < 0.05 or price >= 0.95:
        # 0.00-0.05 (price < 0.05) or 0.95-1.00 (price >= 0.95) — extreme
        if price >= 0.95:
            return "EXTREME_HIGH"
        return "EXTREME_LOW"
    idx = int(price * 20)  # 0..19
    lo = idx * 0.05
    hi = lo + 0.05
    return f"{lo:.2f}-{hi:.2f}"


# ============================================================
# F29-defensive trade-tape column normalization
# ============================================================
def normalize_trades_df(df):
    """If yes_price_dollars / no_price_dollars present, return as-is. If only
    bare names present (yes_price / no_price), rename. Raise if neither."""
    if "yes_price_dollars" in df.columns and "no_price_dollars" in df.columns:
        return df
    rename = {}
    if "yes_price_dollars" not in df.columns and "yes_price" in df.columns:
        rename["yes_price"] = "yes_price_dollars"
    if "no_price_dollars" not in df.columns and "no_price" in df.columns:
        rename["no_price"] = "no_price_dollars"
    if rename:
        log(f"  F29 normalization: renaming {rename}")
        return df.rename(columns=rename)
    cols = ", ".join(df.columns)
    raise ValueError(f"F29: neither *_dollars nor bare-name price columns found. cols=[{cols}]")


# ============================================================
# v0.2 phase_state classifier (inline implementation)
# ============================================================
def compute_phase_state_at_t20m(pmf_ticker, target_mts):
    """Per per_minute_universe_spec.md §7 v0.2:
      - PHASE_4_IN_MATCH if regime == "in_match"
      - PHASE_1_FORMATION if premarket_phase == "formation"
      - PHASE_3_PREMATCH_SURGE if premarket & trades_z >= 3.0 (high-activity
        cohort, baseline = central 50% of premarket trade_count)
      - PHASE_2_STABLE_PREMATCH otherwise (premarket & stable)
      - None if settlement_zone or no row at target_mts
    """
    if len(pmf_ticker) == 0:
        return None
    row = pmf_ticker[pmf_ticker["minute_ts"] == target_mts]
    if len(row) == 0:
        # find nearest within ±120s
        diffs = (pmf_ticker["minute_ts"] - target_mts).abs()
        if diffs.min() > 120:
            return None
        row = pmf_ticker.iloc[[diffs.idxmin()]]
    row = row.iloc[0]
    regime = row["regime"]
    if regime == "in_match":
        return "PHASE_4_IN_MATCH"
    if regime == "settlement_zone":
        return None
    # regime == "premarket"
    pm_phase = row["premarket_phase"]
    if pm_phase == "formation":
        return "PHASE_1_FORMATION"
    # premarket_phase == "stable" or None — check PHASE_3 surge
    pm = pmf_ticker[pmf_ticker["regime"] == "premarket"]
    if len(pm) < 4:
        return "PHASE_2_STABLE_PREMATCH"
    tc = pm["trade_count_in_minute"]
    p25 = tc.quantile(0.25)
    p75 = tc.quantile(0.75)
    iqr_mask = (tc >= p25) & (tc <= p75)
    if iqr_mask.sum() < 2:
        return "PHASE_2_STABLE_PREMATCH"
    p2_mean = tc[iqr_mask].mean()
    p2_std = tc[iqr_mask].std(ddof=0)
    if p2_std is None or np.isnan(p2_std) or p2_std == 0:
        return "PHASE_2_STABLE_PREMATCH"
    tc_at_target = row["trade_count_in_minute"]
    trades_z = (tc_at_target - p2_mean) / p2_std
    if trades_z >= 3.0:
        return "PHASE_3_PREMATCH_SURGE"
    return "PHASE_2_STABLE_PREMATCH"


# ============================================================
# Per-ticker processing
# ============================================================
def read_trades_for_ticker(ticker):
    """Pushdown read of g9_trades for one ticker, sorted by created_time.
    Returns DataFrame with ET-converted trade_ts column. Empty DF if no trades."""
    t = pq.read_table(
        TRADES,
        columns=["created_time", "count_fp", "taker_side", "yes_price_dollars", "no_price_dollars"],
        filters=[("ticker", "=", ticker)],
    )
    if t.num_rows == 0:
        return pd.DataFrame()
    df = t.to_pandas()
    df = normalize_trades_df(df)
    # Parse created_time UTC → ET (tz-aware)
    df["trade_ts_et"] = pd.to_datetime(df["created_time"], format="ISO8601", utc=True).dt.tz_convert(ET_TZ_STR)
    df = df.sort_values("trade_ts_et").reset_index(drop=True)
    return df


def read_pmf_for_ticker(ticker):
    """Pushdown read of per_minute_features for one ticker."""
    t = pq.read_table(
        PMF,
        columns=[
            "ticker", "minute_ts", "category", "match_start_ts", "settlement_ts",
            "open_time_ts", "event_ticker", "partner_ticker",
            "regime", "premarket_phase",
            "trade_count_in_minute",
            "open_interest_ffill", "bbo_bid_size_at_minute_end", "bbo_ask_size_at_minute_end",
            "spread_close", "pair_gap_abs",
        ] if False else None,  # fallback: read all cols, filter is cheap by ticker
        filters=[("ticker", "=", ticker)],
    )
    if t.num_rows == 0:
        return pd.DataFrame()
    return t.to_pandas()


def read_metadata_dataframe():
    """Load g9_metadata as a DataFrame (small, ~20k rows, fits in mem)."""
    df = pq.read_table(META).to_pandas()
    return df


def find_t20m_anchor(trades_df, target_ts_et):
    """Find nearest trade to target within ±2min. Returns
    (anchor_trade_row | None, method, offset_sec_signed)."""
    if len(trades_df) == 0:
        return None, None, None
    diffs = (trades_df["trade_ts_et"] - target_ts_et).dt.total_seconds()
    idx_nearest = diffs.abs().idxmin()
    # Float precision throughout: gate's float arithmetic must agree with the
    # producer's boundary check. Earlier int() truncation accepted offsets in
    # [120.0, 121.0) (e.g., 120.913 → int 120 → passed) that the gate then
    # flagged. Compare as float against an explicit float threshold.
    offset_sec = float(diffs.loc[idx_nearest])
    if abs(offset_sec) > 120.0:
        return None, None, None
    method = "exact" if abs(offset_sec) <= float(ANCHOR_EXACT_SEC) else "nearest_within_2min"
    return trades_df.loc[idx_nearest], method, offset_sec


def walk_peaks(trades_df, t20m_ts_et, settlement_ts_et):
    """Walk trades from t20m through settlement. Compute dual peak + first extreme.

    Returns dict with:
      peak_bid_price_full, peak_bid_price_pre_resolution,
      peak_bid_ts_pre_resolution, peak_bid_ts_full,
      peak_trade_price_full, peak_trade_price_pre_resolution,
      first_extreme_touch_ts
    """
    # Window: t20m_ts_et < trade_ts_et <= settlement_ts_et
    # (Note: t20m anchor trade itself is the entry; peak window is strictly AFTER it)
    mask = (trades_df["trade_ts_et"] > t20m_ts_et) & (trades_df["trade_ts_et"] <= settlement_ts_et)
    window = trades_df[mask]

    # first_extreme_touch_ts
    extreme_mask = (window["yes_price_dollars"] >= EXTREME_HIGH) | (window["yes_price_dollars"] <= EXTREME_LOW)
    first_extreme_ts = None
    if extreme_mask.any():
        first_extreme_ts = window.loc[extreme_mask.idxmax(), "trade_ts_et"]
    # pre_resolution window: trade_ts < first_extreme_ts (strict)
    if first_extreme_ts is not None:
        pre_mask = window["trade_ts_et"] < first_extreme_ts
        pre_window = window[pre_mask]
    else:
        pre_window = window

    # peak_bid (taker_side == "no" reveals bid)
    bid_full_mask = (window["taker_side"] == "no")
    bid_pre_mask = (pre_window["taker_side"] == "no")
    if bid_full_mask.any():
        idx = window.loc[bid_full_mask, "yes_price_dollars"].idxmax()
        peak_bid_price_full = float(window.loc[idx, "yes_price_dollars"])
        peak_bid_ts_full = window.loc[idx, "trade_ts_et"]
    else:
        peak_bid_price_full = None
        peak_bid_ts_full = None
    if bid_pre_mask.any():
        idx = pre_window.loc[bid_pre_mask, "yes_price_dollars"].idxmax()
        peak_bid_price_pre = float(pre_window.loc[idx, "yes_price_dollars"])
        peak_bid_ts_pre = pre_window.loc[idx, "trade_ts_et"]
    else:
        peak_bid_price_pre = peak_bid_price_full
        peak_bid_ts_pre = peak_bid_ts_full

    # peak_trade (any side)
    if len(window) > 0:
        idx = window["yes_price_dollars"].idxmax()
        peak_trade_price_full = float(window.loc[idx, "yes_price_dollars"])
    else:
        peak_trade_price_full = None
    if len(pre_window) > 0:
        idx = pre_window["yes_price_dollars"].idxmax()
        peak_trade_price_pre = float(pre_window.loc[idx, "yes_price_dollars"])
    else:
        peak_trade_price_pre = peak_trade_price_full

    return {
        "peak_bid_price_full": peak_bid_price_full,
        "peak_bid_price_pre_resolution": peak_bid_price_pre,
        "peak_bid_ts_pre_resolution": peak_bid_ts_pre,
        "peak_bid_ts_full": peak_bid_ts_full,
        "peak_trade_price_full": peak_trade_price_full,
        "peak_trade_price_pre_resolution": peak_trade_price_pre,
        "first_extreme_touch_ts": first_extreme_ts,
    }


def process_ticker(ticker, meta_row, t_start_overall):
    """Process one ticker. Returns (row_dict, dropout_reason).
    row_dict is None if dropped; dropout_reason is None if emitted.
    """
    # 1. Extract metadata
    result = meta_row.get("result")
    if result == "scalar":
        return None, "scalar"

    settlement_value_str = meta_row.get("settlement_value_dollars")
    if settlement_value_str is None or settlement_value_str == "" or pd.isna(settlement_value_str):
        return None, "no_settlement_value"
    try:
        settlement_value_dollars = float(settlement_value_str)
    except (TypeError, ValueError):
        return None, "bad_settlement_value"

    category = None  # filled from per_minute_features (more authoritative for tennis bucketing)

    # 2. Read per_minute_features for this ticker
    pmf = read_pmf_for_ticker(ticker)
    if len(pmf) == 0:
        return None, "no_pmf_rows"

    pmf_first = pmf.iloc[0]
    category = pmf_first["category"]
    if category not in CATEGORIES:
        return None, "unknown_category"
    match_start_ts_int = pmf_first["match_start_ts"]
    settlement_ts_int = pmf_first["settlement_ts"]
    open_time_ts_int = pmf_first["open_time_ts"]
    event_ticker = pmf_first["event_ticker"]
    partner_ticker = pmf_first["partner_ticker"]

    if match_start_ts_int is None or pd.isna(match_start_ts_int):
        return None, "no_match_start"

    match_start_et = utc_int_to_et(int(match_start_ts_int))
    settlement_et = utc_int_to_et(int(settlement_ts_int)) if not pd.isna(settlement_ts_int) else None
    open_time_et = utc_int_to_et(int(open_time_ts_int)) if not pd.isna(open_time_ts_int) else None

    target_ts_et = match_start_et - timedelta(seconds=T20M_OFFSET_SEC)
    target_mts_int = int(match_start_ts_int) - T20M_OFFSET_SEC  # for minute-grid lookups

    # 3. Read trades
    trades = read_trades_for_ticker(ticker)
    if len(trades) == 0:
        return None, "no_trades"

    # 4. Find T-20m anchor
    anchor_row, method, offset = find_t20m_anchor(trades, target_ts_et)
    if anchor_row is None:
        return None, "no_trade_near_t20m"
    t20m_ts_et = anchor_row["trade_ts_et"]
    t20m_price = float(anchor_row["yes_price_dollars"])

    # 5. Price band
    band = price_band_5c(t20m_price)
    if band in ("EXTREME_LOW", "EXTREME_HIGH"):
        return None, f"extreme_band_excluded_{band.lower()}"
    if band is None:
        return None, "bad_t20m_price"

    # 6. Walk peaks
    if settlement_et is None:
        return None, "no_settlement_ts"
    peaks = walk_peaks(trades, t20m_ts_et, settlement_et)

    # Floor peaks at t20m_price (gate 3 enforcement; if no peak observed, peak = entry)
    pbf = peaks["peak_bid_price_full"]
    pbpr = peaks["peak_bid_price_pre_resolution"]
    ptf = peaks["peak_trade_price_full"]
    ptpr = peaks["peak_trade_price_pre_resolution"]
    if pbf is None or pbf < t20m_price:
        pbf = t20m_price
    if pbpr is None or pbpr < t20m_price:
        pbpr = t20m_price
    if ptf is None or ptf < t20m_price:
        ptf = t20m_price
    if ptpr is None or ptpr < t20m_price:
        ptpr = t20m_price

    # 7. Derive bounces, premarket flag, minutes-after-entry
    peak_bid_in_premarket = None
    peak_bid_min_after = None
    pb_ts_pre = peaks["peak_bid_ts_pre_resolution"]
    pb_ts_full = peaks["peak_bid_ts_full"]
    if pb_ts_pre is not None:
        peak_bid_in_premarket = bool(pb_ts_pre < match_start_et)
        peak_bid_min_after = float((pb_ts_pre - t20m_ts_et).total_seconds() / 60.0)

    realized_at_settlement = float(settlement_value_dollars - t20m_price)

    # 8. Read context from per_minute_features at T-20m minute
    target_row = pmf[pmf["minute_ts"] == target_mts_int]
    if len(target_row) == 0:
        # nearest minute within ±120s
        diffs_mts = (pmf["minute_ts"] - target_mts_int).abs()
        if diffs_mts.min() <= 120:
            target_row = pmf.iloc[[diffs_mts.idxmin()]]
    if len(target_row) > 0:
        tr = target_row.iloc[0]
        oi_at_t20m = tr.get("open_interest_ffill")
        if oi_at_t20m is not None and pd.notna(oi_at_t20m):
            try:
                oi_at_t20m = int(oi_at_t20m)
            except (ValueError, TypeError):
                oi_at_t20m = None
        else:
            oi_at_t20m = None
        # BBO sizes may not be in per_minute_features schema — fall back to None
        bbo_bid_size = None
        bbo_ask_size = None
    else:
        oi_at_t20m = None
        bbo_bid_size = None
        bbo_ask_size = None

    # phase_state via inline v0.2 classifier
    phase_state = compute_phase_state_at_t20m(pmf, target_mts_int)

    # 9. Premarket-context columns
    n_minutes_premarket = float((match_start_et - open_time_et).total_seconds() / 60.0) if open_time_et else None
    if n_minutes_premarket is not None:
        n_minutes_premarket = int(round(n_minutes_premarket))

    pre_t20m_mask = trades["trade_ts_et"] < t20m_ts_et
    pre_t20m_trades = trades[pre_t20m_mask]
    pre_t20m_pos = pre_t20m_trades[pre_t20m_trades["count_fp"] > 0]
    if len(pre_t20m_pos) > 0:
        first_trade_ts = pre_t20m_pos["trade_ts_et"].min()
    else:
        first_trade_ts = None
    n_trades_pre_t20m = int(len(pre_t20m_pos))

    # 10. Volume columns (Section 4.1)
    pre_match_mask = trades["trade_ts_et"] < match_start_et
    pre_match_pos = trades[pre_match_mask & (trades["count_fp"] > 0)]
    total_premarket_volume = int(pre_match_pos["count_fp"].sum())
    total_premarket_trade_count = int(len(pre_match_pos))

    # Build row
    row = {
        "ticker": ticker,
        "event_ticker": event_ticker,
        "paired_event_partner_ticker": partner_ticker,
        "category": category,
        "match_start_ts": match_start_et,
        "settlement_ts": settlement_et,
        "settlement_value_dollars": float(settlement_value_dollars),
        "t20m_trade_ts": t20m_ts_et,
        "t20m_trade_price": float(t20m_price),
        "t20m_anchor_method": method,
        "price_band": band,
        "cell_key": f"{category}__{band}",
        "band_n_count": -1,  # populated in second pass
        "phase_state_at_t20m": phase_state,
        "peak_bid_price_full": float(pbf),
        "peak_bid_price_pre_resolution": float(pbpr),
        "peak_bid_bounce_full": float(pbf - t20m_price),
        "peak_bid_bounce_pre_resolution": float(pbpr - t20m_price),
        "peak_bid_ts_pre_resolution": pb_ts_pre,
        "peak_bid_ts_full": pb_ts_full,
        "peak_bid_in_premarket": peak_bid_in_premarket,
        "peak_bid_minutes_after_entry": peak_bid_min_after,
        "peak_trade_price_full": float(ptf),
        "peak_trade_price_pre_resolution": float(ptpr),
        "peak_trade_bounce_full": float(ptf - t20m_price),
        "peak_trade_bounce_pre_resolution": float(ptpr - t20m_price),
        "first_extreme_touch_ts": peaks["first_extreme_touch_ts"],
        "realized_at_settlement": realized_at_settlement,
        "total_premarket_volume": total_premarket_volume,
        "total_premarket_trade_count": total_premarket_trade_count,
        "oi_at_t20m": oi_at_t20m,
        "bbo_bid_size_at_t20m": bbo_bid_size,
        "bbo_ask_size_at_t20m": bbo_ask_size,
        "n_minutes_premarket": n_minutes_premarket,
        "first_trade_ts": first_trade_ts,
        "n_trades_pre_t20m": n_trades_pre_t20m,
    }
    return row, None


# ============================================================
# 36-column ordering (spec §5)
# ============================================================
SCHEMA_COLUMNS = [
    "ticker", "event_ticker", "paired_event_partner_ticker", "category",
    "match_start_ts", "settlement_ts", "settlement_value_dollars",
    "t20m_trade_ts", "t20m_trade_price", "t20m_anchor_method",
    "price_band", "cell_key", "band_n_count", "phase_state_at_t20m",
    "peak_bid_price_full", "peak_bid_price_pre_resolution",
    "peak_bid_bounce_full", "peak_bid_bounce_pre_resolution",
    "peak_bid_ts_pre_resolution", "peak_bid_ts_full",
    "peak_bid_in_premarket", "peak_bid_minutes_after_entry",
    "peak_trade_price_full", "peak_trade_price_pre_resolution",
    "peak_trade_bounce_full", "peak_trade_bounce_pre_resolution",
    "first_extreme_touch_ts", "realized_at_settlement",
    "total_premarket_volume", "total_premarket_trade_count",
    "oi_at_t20m", "bbo_bid_size_at_t20m", "bbo_ask_size_at_t20m",
    "n_minutes_premarket", "first_trade_ts", "n_trades_pre_t20m",
]
assert len(SCHEMA_COLUMNS) == 36, f"schema column count = {len(SCHEMA_COLUMNS)} != 36"


# ============================================================
# Hard gates (spec §6)
# ============================================================
def run_hard_gates(df):
    """Return dict of gate results. Each value is (passed: bool, detail: str)."""
    results = {}

    # Gate 1: anchor consistency — t20m_trade_ts within ±2min of (match_start_ts - 20min)
    target = df["match_start_ts"] - pd.Timedelta(minutes=20)
    diff_sec = (df["t20m_trade_ts"] - target).dt.total_seconds().abs()
    g1_viol = int((diff_sec > ANCHOR_TOLERANCE_SEC).sum())
    results["gate1_anchor_consistency"] = (g1_viol == 0, f"violations: {g1_viol}")

    # Gate 2: band exclusion
    g2_viol = int(df["price_band"].isin(["EXTREME_LOW", "EXTREME_HIGH", "0.00-0.05", "0.95-1.00"]).sum())
    results["gate2_band_exclusion"] = (g2_viol == 0, f"violations: {g2_viol}")

    # Gate 3: peak monotonicity
    g3a = int((df["peak_bid_price_full"] < df["t20m_trade_price"] - 1e-9).sum())
    g3b = int((df["peak_bid_price_pre_resolution"] < df["t20m_trade_price"] - 1e-9).sum())
    g3c = int((df["peak_trade_price_full"] < df["t20m_trade_price"] - 1e-9).sum())
    g3d = int((df["peak_trade_price_pre_resolution"] < df["t20m_trade_price"] - 1e-9).sum())
    g3e = int((df["peak_bid_price_full"] < df["peak_bid_price_pre_resolution"] - 1e-9).sum())
    g3f = int((df["peak_trade_price_full"] < df["peak_trade_price_pre_resolution"] - 1e-9).sum())
    g3_total = g3a + g3b + g3c + g3d + g3e + g3f
    results["gate3_peak_monotonicity"] = (g3_total == 0,
        f"violations: bid_full<entry={g3a}, bid_pre<entry={g3b}, "
        f"trade_full<entry={g3c}, trade_pre<entry={g3d}, "
        f"bid_full<bid_pre={g3e}, trade_full<trade_pre={g3f}")

    # Gate 4: settlement consistency
    expected = df["settlement_value_dollars"] - df["t20m_trade_price"]
    diff4 = (df["realized_at_settlement"] - expected).abs()
    g4_viol = int((diff4 > 1e-9).sum())
    results["gate4_settlement_consistency"] = (g4_viol == 0, f"violations: {g4_viol}")

    # Gate 5: TZ correctness — all timestamp columns must be tz-aware
    ts_cols = [
        "match_start_ts", "settlement_ts", "t20m_trade_ts",
        "peak_bid_ts_pre_resolution", "peak_bid_ts_full",
        "first_extreme_touch_ts", "first_trade_ts",
    ]
    g5_failed_cols = []
    for c in ts_cols:
        if c not in df.columns:
            continue
        # tz-aware if dtype is datetime64[ns, tz] OR every value is tz-aware datetime
        d = df[c].dropna()
        if len(d) == 0:
            continue
        # Check first value
        sample = d.iloc[0]
        if not (hasattr(sample, "tzinfo") and sample.tzinfo is not None):
            g5_failed_cols.append(c)
    results["gate5_tz_correctness"] = (len(g5_failed_cols) == 0,
        f"non-tz-aware columns: {g5_failed_cols}" if g5_failed_cols else "all tz-aware ET")

    return results


def all_gates_pass(gate_results):
    return all(passed for passed, _ in gate_results.values())


def fmt_gates(gate_results):
    lines = []
    for name, (passed, detail) in gate_results.items():
        lines.append(f"  {name}: {'PASS' if passed else 'FAIL'} ({detail})")
    return "\n".join(lines)


# ============================================================
# DataFrame → parquet with explicit schema (tz-aware timestamps)
# ============================================================
def write_parquet(df, path):
    """Write with explicit TZ-aware timestamp schema and proper col order."""
    df = df.reindex(columns=SCHEMA_COLUMNS)
    # Convert timestamps to pandas datetime[us, ET]
    ts_cols = [
        "match_start_ts", "settlement_ts", "t20m_trade_ts",
        "peak_bid_ts_pre_resolution", "peak_bid_ts_full",
        "first_extreme_touch_ts", "first_trade_ts",
    ]
    for c in ts_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, path, compression="snappy")


# ============================================================
# Phase orchestration
# ============================================================
def get_binary_outcome_tickers(meta_df):
    """Return list of binary-outcome (result in {yes, no}) tickers."""
    mask = meta_df["result"].isin(["yes", "no"])
    return sorted(meta_df.loc[mask, "ticker"].tolist())


def select_phase2_matches(meta_df, pmf_categories_match_start_per_ticker, n_per_stratum=5):
    """Mirror T37 Phase 2 sampling: 4 categories × 4 premarket-length quartiles
    × ~5 matches per stratum. Returns list of tickers."""
    # Build a per-event_ticker dict: list of (ticker, category, premarket_min)
    # Premarket length = (match_start_ts - open_time_ts) / 60
    # We have match_start_ts per ticker but the operator's spec sampling key is by MATCH (paired event).
    binary_tickers = get_binary_outcome_tickers(meta_df)
    btset = set(binary_tickers)
    meta_b = meta_df[meta_df["ticker"].isin(btset)].copy()
    # Premarket length: need match_start_ts (from pmf) and open_time (from metadata)
    # Use pmf-derived match_start_ts mapping
    meta_b["match_start_ts"] = meta_b["ticker"].map(pmf_categories_match_start_per_ticker)
    meta_b = meta_b[meta_b["match_start_ts"].notna()].copy()
    # Convert open_time to Unix sec
    meta_b["open_time_unix"] = pd.to_datetime(meta_b["open_time"], format="ISO8601", utc=True, errors="coerce").astype("int64") // 10**9
    meta_b["match_start_unix"] = meta_b["match_start_ts"].astype("int64")
    meta_b["premarket_min"] = (meta_b["match_start_unix"] - meta_b["open_time_unix"]) / 60.0
    # Get category from pmf, not metadata (more authoritative)
    cat_map = {}
    cat_df = pq.read_table(PMF, columns=["ticker", "category"]).to_pandas().drop_duplicates(subset=["ticker"])
    for _, r in cat_df.iterrows():
        cat_map[r["ticker"]] = r["category"]
    meta_b["category"] = meta_b["ticker"].map(cat_map)
    meta_b = meta_b[meta_b["category"].isin(CATEGORIES)].copy()
    # Per (category, quartile): sample n_per_stratum MATCHES, take both sides
    rng = np.random.default_rng(PHASE2_SAMPLE_SEED)
    selected_tickers = []
    for cat in CATEGORIES:
        sub = meta_b[meta_b["category"] == cat].copy()
        # Quartile by premarket_min
        try:
            sub["pm_q"] = pd.qcut(sub["premarket_min"], q=4, labels=False, duplicates="drop")
        except ValueError:
            sub["pm_q"] = 0
        for q in sorted(sub["pm_q"].dropna().unique()):
            stratum = sub[sub["pm_q"] == q]
            # Group by event_ticker — both sides of paired event
            events = stratum["event_ticker"].dropna().unique().tolist()
            if len(events) <= n_per_stratum:
                chosen = events
            else:
                chosen = rng.choice(events, size=n_per_stratum, replace=False).tolist()
            for evt in chosen:
                paired = stratum[stratum["event_ticker"] == evt]["ticker"].tolist()
                selected_tickers.extend(paired)
    return sorted(set(selected_tickers))


def run_phase(phase, tickers, output_path, meta_df, batch_size=None):
    """Run producer on a list of tickers. Returns (df, dropouts dict, runtimes list)."""
    log(f"phase {phase}: starting; n_tickers={len(tickers)}")
    rows = []
    dropouts = defaultdict(int)
    runtimes = []
    meta_by_ticker = meta_df.set_index("ticker")
    t_start = time.time()
    n_done = 0
    for i, tk in enumerate(tickers):
        t_tk = time.time()
        try:
            if tk in meta_by_ticker.index:
                meta_row = meta_by_ticker.loc[tk].to_dict() if isinstance(meta_by_ticker.loc[tk], pd.Series) else meta_by_ticker.loc[tk].iloc[0].to_dict()
            else:
                dropouts["no_metadata"] += 1
                continue
            row, dropout = process_ticker(tk, meta_row, t_start)
            if row is not None:
                rows.append(row)
                runtimes.append(time.time() - t_tk)
            else:
                dropouts[dropout or "unknown"] += 1
        except Exception as e:
            dropouts[f"exception:{type(e).__name__}"] += 1
            log(f"  ticker {tk}: exception {type(e).__name__}: {e}")
        n_done += 1
        if n_done % 200 == 0 or n_done == len(tickers):
            elapsed = time.time() - t_start
            log(f"  progress {n_done}/{len(tickers)}  emitted={len(rows)}  "
                f"dropouts={sum(dropouts.values())}  elapsed={elapsed:.1f}s")
    elapsed_total = time.time() - t_start
    log(f"phase {phase}: producer loop complete in {elapsed_total:.1f}s; "
        f"emitted={len(rows)}, dropouts={dict(dropouts)}")
    if len(rows) == 0:
        log(f"  WARN: zero rows emitted")
        return pd.DataFrame(columns=SCHEMA_COLUMNS), dict(dropouts), runtimes
    df = pd.DataFrame(rows)
    # band_n_count pass
    counts = df.groupby("cell_key").size().to_dict()
    df["band_n_count"] = df["cell_key"].map(counts).astype(int)
    # Write
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    write_parquet(df, output_path)
    log(f"  wrote {output_path} ({os.path.getsize(output_path):,} bytes)")
    return df, dict(dropouts), runtimes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, required=True, choices=[1, 2, 3])
    parser.add_argument("--ticker", type=str, default=None, help="Phase 1 ticker")
    parser.add_argument("--out", type=str, default=None, help="Output path override")
    args = parser.parse_args()

    log(f"Rung 0 producer v1.1 — phase {args.phase}")
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(PARTIAL_DIR, exist_ok=True)
    os.makedirs(PROBE_DIR, exist_ok=True)

    log("Loading g9_metadata …")
    meta_df = read_metadata_dataframe()
    log(f"  metadata rows: {len(meta_df):,}")

    if args.phase == 1:
        ticker = args.ticker or "KXATPMATCH-25JUN18RUNMCD-RUN"
        output_path = args.out or f"{PROBE_DIR}/cell_economics_phase1.parquet"
        df, dropouts, runtimes = run_phase(1, [ticker], output_path, meta_df)
    elif args.phase == 2:
        log("Building Phase 2 sample …")
        pmf_msts = pq.read_table(PMF, columns=["ticker", "match_start_ts"]).to_pandas().drop_duplicates(subset=["ticker"])
        msts_map = dict(zip(pmf_msts["ticker"], pmf_msts["match_start_ts"]))
        tickers = select_phase2_matches(meta_df, msts_map, n_per_stratum=5)
        log(f"  Phase 2 ticker list: {len(tickers)} (target ~160)")
        output_path = args.out or f"{PROBE_DIR}/cell_economics_phase2.parquet"
        df, dropouts, runtimes = run_phase(2, tickers, output_path, meta_df)
    else:  # phase 3
        binary_tickers = get_binary_outcome_tickers(meta_df)
        log(f"  full binary-outcome tickers: {len(binary_tickers):,}")
        output_path = args.out or f"{OUT_DIR}/cell_economics.parquet.new"
        df, dropouts, runtimes = run_phase(3, binary_tickers, output_path, meta_df)

    # Run hard gates
    log("")
    log("Running hard gates …")
    if len(df) == 0:
        log("  empty output; gates skipped")
        return
    gates = run_hard_gates(df)
    log(fmt_gates(gates))

    # Per-phase informative output
    if len(runtimes) > 0:
        rt = np.asarray(runtimes)
        log("")
        log(f"Per-ticker runtime: n={len(rt)}, median={np.median(rt):.3f}s, "
            f"p90={np.percentile(rt, 90):.3f}s, max={rt.max():.3f}s")
    log("")
    log(f"Dropouts: {dropouts}")
    log(f"Emitted: {len(df)} rows")

    # Save dropout log + gate report alongside the output
    side = {
        "phase": args.phase,
        "emitted": int(len(df)),
        "dropouts": dropouts,
        "runtime_median_sec": float(np.median(runtimes)) if runtimes else None,
        "runtime_p90_sec": float(np.percentile(runtimes, 90)) if runtimes else None,
        "runtime_max_sec": float(max(runtimes)) if runtimes else None,
        "gates": {k: {"passed": p, "detail": d} for k, (p, d) in gates.items()},
        "all_gates_pass": all_gates_pass(gates),
    }
    side_path = output_path + ".meta.json"
    with open(side_path, "w") as f:
        json.dump(side, f, indent=2, default=str)
    log(f"Wrote {side_path}")

    if all_gates_pass(gates):
        log("ALL HARD GATES PASS.")
        sys.exit(0)
    else:
        log("ONE OR MORE HARD GATES FAILED. .new preserved for forensics.")
        sys.exit(1)


if __name__ == "__main__":
    main()
