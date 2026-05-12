#!/usr/bin/env python3
"""Per-minute universe producer.

Implementation per docs/per_minute_universe_spec.md (commit 87e8e9a2).

Phase 1 (this commit): single-ticker mode.
  - Phase 1 ticker: KXATPMATCH-25JUN18RUNMCD-RUN
  - Output: data/durable/per_minute_universe/probe/per_minute_universe_phase1.parquet
  - Runtime budget: <2 min
  - PASS criteria: spec Section 5 Checks 1, 2, 4 + visual inspection vs operator-uploaded chart
Phase 2 and Phase 3 deferred to separate single-concern commits per spec Section 3.3.
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

DUR_DIR = "/root/Omi-Workspace/arb-executor/data/durable"
TRADES_PARQUET = os.path.join(DUR_DIR, "g9_trades.parquet")
CANDLES_PARQUET = os.path.join(DUR_DIR, "g9_candles.parquet")
META_PARQUET = os.path.join(DUR_DIR, "g9_metadata.parquet")
OUT_DIR = os.path.join(DUR_DIR, "per_minute_universe")
PROBE_DIR = os.path.join(OUT_DIR, "probe")

PHASE1_TICKER = "KXATPMATCH-25JUN18RUNMCD-RUN"
FORMATION_WINDOW_MIN_DEFAULT = 120  # per spec Section 2.6
MATCH_START_K_DEFAULT = 3  # K consecutive minutes per LESSONS A35 amended v3
MATCH_START_M_DEFAULT = 5  # M min trade_count per side per LESSONS A35 amended v3

# Forward-label horizons in seconds (spec Section 2.8)
HORIZONS = {
    "5min": 300,
    "15min": 900,
    "30min": 1800,
    "60min": 3600,
}


def log(msg, log_path=None):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    if log_path:
        with open(log_path, "a") as f:
            f.write(line + "\n")


# ============================================================
# Per-ticker data loading
# ============================================================

def load_ticker_metadata(ticker):
    """Return one g9_metadata row for the ticker, or None."""
    t = pq.read_table(META_PARQUET, filters=[("ticker", "=", ticker)]).to_pandas()
    if len(t) == 0:
        return None
    return t.iloc[0]


def load_ticker_candles(ticker):
    """Return g9_candles for ticker, sorted by end_period_ts."""
    t = pq.read_table(
        CANDLES_PARQUET,
        columns=["ticker", "end_period_ts",
                 "yes_bid_open", "yes_bid_high", "yes_bid_low", "yes_bid_close",
                 "yes_ask_open", "yes_ask_high", "yes_ask_low", "yes_ask_close",
                 "price_close", "price_open", "price_high", "price_low",
                 "price_mean", "price_previous",
                 "volume_fp", "open_interest_fp"],
        filters=[("ticker", "=", ticker)],
    )
    if t.num_rows == 0:
        return None
    return t.to_pandas().sort_values("end_period_ts").reset_index(drop=True)


def load_ticker_trades(ticker):
    """Return g9_trades for ticker with ISO8601-parsed created_time_ts (unix seconds)."""
    t = pq.read_table(
        TRADES_PARQUET,
        columns=["ticker", "created_time", "taker_side", "yes_price_dollars",
                 "no_price_dollars", "count_fp", "trade_id"],
        filters=[("ticker", "=", ticker)],
    )
    if t.num_rows == 0:
        return pd.DataFrame()
    df = t.to_pandas()
    df["created_time_ts"] = pd.to_datetime(df["created_time"], format="ISO8601").map(
        lambda x: int(x.timestamp())
    )
    return df.sort_values("created_time_ts").reset_index(drop=True)


# ============================================================
# Derived fields
# ============================================================

def parse_iso_ts(s):
    """Parse ISO8601 string with optional Z suffix to unix int seconds."""
    if s is None or pd.isna(s) or s == "":
        return None
    try:
        return int(datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp())
    except Exception:
        return None


def derive_match_start_ts(minute_ts_arr, own_trade_count_arr, partner_trade_count_arr,
                           K=MATCH_START_K_DEFAULT, M=MATCH_START_M_DEFAULT):
    """Derive match_start_ts via both-sides-simultaneous trade-density signal per
    LESSONS A35 amended v3 (spec Section 2.5).

    Signal: first minute in a sustained run of K consecutive minutes where BOTH
    own.trade_count_in_minute ≥ M AND partner.trade_count_in_minute ≥ M.

    Rationale: real match-start events produce simultaneous trader reaction on both
    paired-leg sides; sporadic premarket activity is one-sided. M=5 filters out
    single-trade noise.

    Returns (match_start_ts, method).
    method ∈ {"both_sides_trade_density", "expected_expiration_fallback", "unknown"}.

    Partner trade-count array must be aligned to own minute_ts_arr (same length,
    same minutes). Missing partner minutes are treated as count=0 by caller.
    """
    n = len(minute_ts_arr)
    if n < K:
        return None, "unknown"
    for i in range(n - K + 1):
        if all(
            own_trade_count_arr[i + j] >= M and partner_trade_count_arr[i + j] >= M
            for j in range(K)
        ):
            return int(minute_ts_arr[i]), "both_sides_trade_density"
    return None, "unknown"


def classify_regime(minute_ts, match_start_ts, settlement_ts):
    """Per spec Section 2.6."""
    if settlement_ts is not None and minute_ts >= (settlement_ts - 300):
        return "settlement_zone"
    if match_start_ts is not None and minute_ts >= match_start_ts:
        return "in_match"
    return "premarket"


def classify_premarket_phase(minute_ts, open_time_ts, regime, formation_window_min):
    """Per spec Section 2.6."""
    if regime != "premarket":
        return None
    if open_time_ts is None:
        return None
    minutes_since_open = (minute_ts - open_time_ts) / 60.0
    if minutes_since_open < formation_window_min:
        return "formation"
    return "stable"


def safe_div(num, den):
    if den is None or den == 0 or pd.isna(den):
        return None
    return num / den


# ============================================================
# Per-minute trade aggregation
# ============================================================

def aggregate_trades_per_minute(candles_df, trades_df):
    """For each minute_ts in candles_df, compute:
      - trade_count_in_minute
      - taker_yes_count_in_minute, taker_no_count_in_minute
      - vwap_in_minute
    Window is [minute_ts - 60, minute_ts) (half-open, ending at minute close).
    """
    n_candles = len(candles_df)
    out = {
        "trade_count_in_minute": np.zeros(n_candles, dtype=np.int32),
        "taker_yes_count_in_minute": np.zeros(n_candles, dtype=np.float64),
        "taker_no_count_in_minute": np.zeros(n_candles, dtype=np.float64),
        "vwap_in_minute": np.full(n_candles, np.nan, dtype=np.float64),
    }
    if len(trades_df) == 0:
        return out

    trade_ts = trades_df["created_time_ts"].values.astype(np.int64)
    trade_side = trades_df["taker_side"].values
    trade_count = trades_df["count_fp"].values.astype(np.float64)
    trade_price = trades_df["yes_price_dollars"].values.astype(np.float64)
    minute_ts_arr = candles_df["end_period_ts"].values.astype(np.int64)

    # For each candle minute, find trades in [minute_ts - 60, minute_ts)
    for i, m_ts in enumerate(minute_ts_arr):
        window_start = m_ts - 60
        window_end = m_ts
        idx_lo = np.searchsorted(trade_ts, window_start, side="left")
        idx_hi = np.searchsorted(trade_ts, window_end, side="left")
        if idx_lo == idx_hi:
            continue
        win_side = trade_side[idx_lo:idx_hi]
        win_count = trade_count[idx_lo:idx_hi]
        win_price = trade_price[idx_lo:idx_hi]
        out["trade_count_in_minute"][i] = idx_hi - idx_lo
        out["taker_yes_count_in_minute"][i] = win_count[win_side == "yes"].sum()
        out["taker_no_count_in_minute"][i] = win_count[win_side == "no"].sum()
        tot = win_count.sum()
        if tot > 0:
            out["vwap_in_minute"][i] = (win_price * win_count).sum() / tot
    return out


# ============================================================
# Forward-looking labels (spec Section 2.8)
# ============================================================

def compute_forward_labels(candles_df, match_start_ts, settlement_ts):
    """For each row, compute max yes_bid_high and min yes_ask_low looking forward
    over each horizon defined in HORIZONS, plus to_match_start and to_settlement.
    Returns dict of np arrays keyed by label.
    """
    n = len(candles_df)
    minute_ts_arr = candles_df["end_period_ts"].values.astype(np.int64)
    yes_bid_high = candles_df["yes_bid_high"].astype(np.float64).values
    yes_ask_low = candles_df["yes_ask_low"].astype(np.float64).values

    out = {}
    for label, h_sec in HORIZONS.items():
        max_bid = np.full(n, np.nan, dtype=np.float64)
        min_ask = np.full(n, np.nan, dtype=np.float64)
        for i in range(n):
            window_end_ts = minute_ts_arr[i] + h_sec
            # j_max is exclusive end of window where minute_ts[j] <= window_end_ts
            j_max = np.searchsorted(minute_ts_arr, window_end_ts, side="right")
            if j_max > i + 1:
                bid_slice = yes_bid_high[i + 1:j_max]
                ask_slice = yes_ask_low[i + 1:j_max]
                if len(bid_slice) > 0 and not np.all(np.isnan(bid_slice)):
                    max_bid[i] = np.nanmax(bid_slice)
                if len(ask_slice) > 0 and not np.all(np.isnan(ask_slice)):
                    min_ask[i] = np.nanmin(ask_slice)
        out[f"max_yes_bid_forward_{label}"] = max_bid
        out[f"min_yes_ask_forward_{label}"] = min_ask

    # to_match_start
    max_bid_ms = np.full(n, np.nan, dtype=np.float64)
    min_ask_ms = np.full(n, np.nan, dtype=np.float64)
    if match_start_ts is not None:
        for i in range(n):
            if minute_ts_arr[i] >= match_start_ts:
                continue
            j_max = np.searchsorted(minute_ts_arr, match_start_ts, side="right")
            if j_max > i + 1:
                bid_slice = yes_bid_high[i + 1:j_max]
                ask_slice = yes_ask_low[i + 1:j_max]
                if len(bid_slice) > 0 and not np.all(np.isnan(bid_slice)):
                    max_bid_ms[i] = np.nanmax(bid_slice)
                if len(ask_slice) > 0 and not np.all(np.isnan(ask_slice)):
                    min_ask_ms[i] = np.nanmin(ask_slice)
    out["max_yes_bid_forward_to_match_start"] = max_bid_ms
    out["min_yes_ask_forward_to_match_start"] = min_ask_ms

    # to_settlement
    max_bid_se = np.full(n, np.nan, dtype=np.float64)
    min_ask_se = np.full(n, np.nan, dtype=np.float64)
    if settlement_ts is not None:
        for i in range(n):
            j_max = np.searchsorted(minute_ts_arr, settlement_ts, side="right")
            if j_max > i + 1:
                bid_slice = yes_bid_high[i + 1:j_max]
                ask_slice = yes_ask_low[i + 1:j_max]
                if len(bid_slice) > 0 and not np.all(np.isnan(bid_slice)):
                    max_bid_se[i] = np.nanmax(bid_slice)
                if len(ask_slice) > 0 and not np.all(np.isnan(ask_slice)):
                    min_ask_se[i] = np.nanmin(ask_slice)
    out["max_yes_bid_forward_to_settlement"] = max_bid_se
    out["min_yes_ask_forward_to_settlement"] = min_ask_se

    return out


# ============================================================
# Paired-leg partner discovery + observables (spec Section 2.9)
# ============================================================

def find_partner_ticker(event_ticker, own_ticker):
    """For a given event_ticker (which pairs the two players in a match), return
    the ticker that is NOT own_ticker. Returns None if no partner exists."""
    if event_ticker is None:
        return None
    t = pq.read_table(
        META_PARQUET, columns=["ticker"],
        filters=[("event_ticker", "=", event_ticker)],
    ).to_pandas()
    others = [tk for tk in t["ticker"].tolist() if tk != own_ticker]
    if not others:
        return None
    return others[0]


def build_partner_observables(partner_ticker):
    """Return {minute_ts → dict-of-partner-observables} per spec Section 2.9.

    Lighter-weight than build_ticker_rows: only the columns needed for paired-leg
    emission. Reuses aggregate_trades_per_minute for trade-derived columns.
    """
    if partner_ticker is None:
        return {}
    candles = load_ticker_candles(partner_ticker)
    if candles is None or len(candles) == 0:
        return {}
    trades = load_ticker_trades(partner_ticker)
    aggs = aggregate_trades_per_minute(candles, trades)
    oi_raw = candles["open_interest_fp"].astype(np.float64).values
    oi_ffill = pd.Series(oi_raw).ffill().values
    n = len(candles)
    out = {}
    for i in range(n):
        m_ts = int(candles["end_period_ts"].iloc[i])
        bid_v = candles["yes_bid_close"].iloc[i]
        ask_v = candles["yes_ask_close"].iloc[i]
        bid_c = float(bid_v) if pd.notna(bid_v) else None
        ask_c = float(ask_v) if pd.notna(ask_v) else None
        spread = (ask_c - bid_c) if (bid_c is not None and ask_c is not None) else None
        vol_v = candles["volume_fp"].iloc[i]
        vol_f = float(vol_v) if pd.notna(vol_v) else None
        oi_f = float(oi_ffill[i]) if not np.isnan(oi_ffill[i]) else None
        flow = float(aggs["taker_yes_count_in_minute"][i] - aggs["taker_no_count_in_minute"][i])
        out[m_ts] = {
            "partner_yes_bid_close": bid_c,
            "partner_yes_ask_close": ask_c,
            "partner_spread_close": spread,
            "partner_volume_in_minute": vol_f,
            "partner_trade_count_in_minute": int(aggs["trade_count_in_minute"][i]),
            "partner_taker_flow_in_minute": flow,
            "partner_open_interest_ffill": oi_f,
        }
    return out


def compute_paired_columns(own_bid, own_ask, own_mid, own_vol, partner_obs):
    """Build the 7 paired-leg derived columns (paired_yes_bid_sum, paired_yes_ask_sum,
    paired_mid_sum, paired_arb_gap_maker, paired_arb_gap_taker, partner_volume_ratio)
    plus partner_mid_close derived inline."""
    p_bid = partner_obs.get("partner_yes_bid_close")
    p_ask = partner_obs.get("partner_yes_ask_close")
    p_vol = partner_obs.get("partner_volume_in_minute")
    paired_yes_bid_sum = (own_bid + p_bid) if (own_bid is not None and p_bid is not None) else None
    paired_yes_ask_sum = (own_ask + p_ask) if (own_ask is not None and p_ask is not None) else None
    partner_mid = (p_bid + p_ask) / 2.0 if (p_bid is not None and p_ask is not None) else None
    paired_mid_sum = (own_mid + partner_mid) if (own_mid is not None and partner_mid is not None) else None
    paired_arb_gap_maker = (1.0 - paired_yes_bid_sum) if paired_yes_bid_sum is not None else None
    paired_arb_gap_taker = (paired_yes_ask_sum - 1.0) if paired_yes_ask_sum is not None else None
    partner_vol_ratio = None
    if own_vol is not None and p_vol is not None and (own_vol + p_vol) > 0:
        partner_vol_ratio = own_vol / (own_vol + p_vol)
    return {
        "paired_yes_bid_sum": paired_yes_bid_sum,
        "paired_yes_ask_sum": paired_yes_ask_sum,
        "paired_mid_sum": paired_mid_sum,
        "paired_arb_gap_maker": paired_arb_gap_maker,
        "paired_arb_gap_taker": paired_arb_gap_taker,
        "partner_volume_ratio": partner_vol_ratio,
    }


# ============================================================
# Per-ticker row builder
# ============================================================

def build_ticker_rows(ticker, formation_window_min=FORMATION_WINDOW_MIN_DEFAULT):
    """Produce per-minute rows for one ticker. Returns DataFrame."""
    meta = load_ticker_metadata(ticker)
    if meta is None:
        return None
    candles_df = load_ticker_candles(ticker)
    if candles_df is None or len(candles_df) == 0:
        return None
    trades_df = load_ticker_trades(ticker)

    # Metadata-derived constants
    event_ticker = meta.get("event_ticker")
    settlement_value = float(meta["settlement_value_dollars"]) if meta.get("settlement_value_dollars") not in (None, "") else None
    result = meta.get("result")
    open_time_ts = parse_iso_ts(meta.get("open_time"))
    expected_expiration_ts = parse_iso_ts(meta.get("expected_expiration_time"))
    close_time_ts = parse_iso_ts(meta.get("close_time"))
    settlement_ts = parse_iso_ts(meta.get("settlement_ts"))

    # Extract player UUID from custom_strike JSON
    player_uuid = None
    cs = meta.get("custom_strike")
    if isinstance(cs, str):
        try:
            csd = json.loads(cs)
            player_uuid = csd.get("tennis_competitor")
        except Exception:
            player_uuid = None
    elif isinstance(cs, dict):
        player_uuid = cs.get("tennis_competitor")

    # Partner ticker discovery + observables (spec Section 2.9)
    partner_ticker = find_partner_ticker(event_ticker, ticker)
    partner_obs_map = build_partner_observables(partner_ticker) if partner_ticker else {}

    n = len(candles_df)
    minute_ts_arr = candles_df["end_period_ts"].astype(np.int64).values

    # Trade aggregation for own ticker
    trade_aggs = aggregate_trades_per_minute(candles_df, trades_df)

    # Build partner trade-count array aligned to own minute_ts_arr (v3 signal needs
    # both sides). Minutes where partner has no candle → count=0 (treated as not
    # trading on the partner side).
    partner_trade_count_aligned = np.zeros(n, dtype=np.int64)
    for idx_i in range(n):
        m_ts_i = int(minute_ts_arr[idx_i])
        p_obs_i = partner_obs_map.get(m_ts_i, {})
        partner_trade_count_aligned[idx_i] = int(p_obs_i.get("partner_trade_count_in_minute", 0))

    # Match-start derivation via v3 both-sides-simultaneous trade-density signal
    # (spec Section 2.5 amended v3): first K consecutive minutes where BOTH
    # own.trade_count ≥ M AND partner.trade_count ≥ M.
    match_start_ts, match_start_method = derive_match_start_ts(
        minute_ts_arr,
        trade_aggs["trade_count_in_minute"],
        partner_trade_count_aligned,
    )
    if match_start_ts is None and expected_expiration_ts is not None:
        # Fallback per spec Section 2.5
        if settlement_ts is not None and expected_expiration_ts < settlement_ts:
            match_start_ts = expected_expiration_ts
            match_start_method = "expected_expiration_fallback"
        else:
            match_start_method = "unknown"

    # Forward-fill open_interest
    oi_raw = candles_df["open_interest_fp"].astype(np.float64).values
    oi_ffill = pd.Series(oi_raw).ffill().values
    oi_delta = np.full(n, np.nan, dtype=np.float64)
    oi_delta[1:] = oi_ffill[1:] - oi_ffill[:-1]

    # Derived BBO columns
    yes_bid_close = candles_df["yes_bid_close"].astype(np.float64).values
    yes_ask_close = candles_df["yes_ask_close"].astype(np.float64).values
    yes_bid_high = candles_df["yes_bid_high"].astype(np.float64).values
    yes_bid_low = candles_df["yes_bid_low"].astype(np.float64).values
    yes_ask_high = candles_df["yes_ask_high"].astype(np.float64).values
    yes_ask_low_arr = candles_df["yes_ask_low"].astype(np.float64).values

    spread_close = yes_ask_close - yes_bid_close
    mid_close = (yes_ask_close + yes_bid_close) / 2.0
    bid_range_intra_min = yes_bid_high - yes_bid_low
    ask_range_intra_min = yes_ask_high - yes_ask_low_arr

    # Regime + premarket_phase + cell-key features per minute
    cat = categorize(ticker)
    volumes_full = candles_df["volume_fp"].fillna(0).values

    regimes = []
    premarket_phases = []
    eb_lo_arr = np.full(n, -1, dtype=np.int64)
    eb_hi_arr = np.full(n, -1, dtype=np.int64)
    spread_band_arr = np.empty(n, dtype=object)
    volume_intensity_arr = np.empty(n, dtype=object)
    time_to_match_start_min = np.full(n, np.nan, dtype=np.float64)
    time_to_close_min = np.full(n, np.nan, dtype=np.float64)
    time_to_settlement_min = np.full(n, np.nan, dtype=np.float64)
    minutes_since_open_arr = np.full(n, np.nan, dtype=np.float64)

    vi_overall = volume_intensity_for_market(volumes_full)

    for i in range(n):
        m_ts = int(minute_ts_arr[i])
        bid_f = float(yes_bid_close[i]) if not np.isnan(yes_bid_close[i]) else None
        ask_f = float(yes_ask_close[i]) if not np.isnan(yes_ask_close[i]) else None

        rg = classify_regime(m_ts, match_start_ts, settlement_ts)
        regimes.append(rg)
        premarket_phases.append(classify_premarket_phase(m_ts, open_time_ts, rg, formation_window_min))

        if ask_f is not None:
            eb_idx = entry_band_idx(ask_f)
            eb_lo_arr[i] = eb_idx * 10
            eb_hi_arr[i] = (eb_idx + 1) * 10
        if bid_f is not None and ask_f is not None:
            spread_band_arr[i] = spread_band_name(bid_f, ask_f)
        else:
            spread_band_arr[i] = None
        volume_intensity_arr[i] = vi_overall

        if match_start_ts is not None:
            time_to_match_start_min[i] = (match_start_ts - m_ts) / 60.0
        if close_time_ts is not None:
            time_to_close_min[i] = (close_time_ts - m_ts) / 60.0
        if settlement_ts is not None:
            time_to_settlement_min[i] = (settlement_ts - m_ts) / 60.0
        if open_time_ts is not None:
            minutes_since_open_arr[i] = (m_ts - open_time_ts) / 60.0

    # Forward labels
    fwd = compute_forward_labels(candles_df, match_start_ts, settlement_ts)
    bounces = {}
    for label in ["5min", "15min", "30min", "60min"]:
        bounces[f"bounce_{label}"] = fwd[f"max_yes_bid_forward_{label}"] - yes_ask_close
    bounces["bounce_to_match_start"] = fwd["max_yes_bid_forward_to_match_start"] - yes_ask_close
    bounces["bounce_to_settlement"] = fwd["max_yes_bid_forward_to_settlement"] - yes_ask_close

    # Assemble per-row dicts
    rows = []
    for i in range(n):
        # Paired-leg lookup for this minute
        m_ts_i = int(minute_ts_arr[i])
        p_obs = partner_obs_map.get(m_ts_i, {})
        own_bid_f = float(yes_bid_close[i]) if not np.isnan(yes_bid_close[i]) else None
        own_ask_f = float(yes_ask_close[i]) if not np.isnan(yes_ask_close[i]) else None
        own_mid_f = float(mid_close[i]) if not np.isnan(mid_close[i]) else None
        own_vol_raw = candles_df["volume_fp"].iloc[i]
        own_vol_f = float(own_vol_raw) if pd.notna(own_vol_raw) else None
        paired_cols = compute_paired_columns(own_bid_f, own_ask_f, own_mid_f, own_vol_f, p_obs)

        r = {
            # Identity
            "ticker": ticker,
            "event_ticker": event_ticker,
            "minute_ts": m_ts_i,
            "category": cat,
            "player_competitor_uuid": player_uuid,
            # BBO range
            "yes_bid_open": float(candles_df["yes_bid_open"].iloc[i]) if pd.notna(candles_df["yes_bid_open"].iloc[i]) else None,
            "yes_bid_high": float(yes_bid_high[i]) if not np.isnan(yes_bid_high[i]) else None,
            "yes_bid_low": float(yes_bid_low[i]) if not np.isnan(yes_bid_low[i]) else None,
            "yes_bid_close": float(yes_bid_close[i]) if not np.isnan(yes_bid_close[i]) else None,
            "yes_ask_open": float(candles_df["yes_ask_open"].iloc[i]) if pd.notna(candles_df["yes_ask_open"].iloc[i]) else None,
            "yes_ask_high": float(yes_ask_high[i]) if not np.isnan(yes_ask_high[i]) else None,
            "yes_ask_low": float(yes_ask_low_arr[i]) if not np.isnan(yes_ask_low_arr[i]) else None,
            "yes_ask_close": float(yes_ask_close[i]) if not np.isnan(yes_ask_close[i]) else None,
            "spread_close": float(spread_close[i]) if not np.isnan(spread_close[i]) else None,
            "mid_close": float(mid_close[i]) if not np.isnan(mid_close[i]) else None,
            "bid_range_intra_minute": float(bid_range_intra_min[i]) if not np.isnan(bid_range_intra_min[i]) else None,
            "ask_range_intra_minute": float(ask_range_intra_min[i]) if not np.isnan(ask_range_intra_min[i]) else None,
            # Trade activity
            "price_close": float(candles_df["price_close"].iloc[i]) if pd.notna(candles_df["price_close"].iloc[i]) else None,
            "price_open": float(candles_df["price_open"].iloc[i]) if pd.notna(candles_df["price_open"].iloc[i]) else None,
            "price_high": float(candles_df["price_high"].iloc[i]) if pd.notna(candles_df["price_high"].iloc[i]) else None,
            "price_low": float(candles_df["price_low"].iloc[i]) if pd.notna(candles_df["price_low"].iloc[i]) else None,
            "price_mean": float(candles_df["price_mean"].iloc[i]) if pd.notna(candles_df["price_mean"].iloc[i]) else None,
            "price_previous": float(candles_df["price_previous"].iloc[i]) if pd.notna(candles_df["price_previous"].iloc[i]) else None,
            "volume_in_minute": float(candles_df["volume_fp"].iloc[i]) if pd.notna(candles_df["volume_fp"].iloc[i]) else None,
            "trade_count_in_minute": int(trade_aggs["trade_count_in_minute"][i]),
            "minute_has_trade": bool(trade_aggs["trade_count_in_minute"][i] > 0),
            "taker_yes_count_in_minute": float(trade_aggs["taker_yes_count_in_minute"][i]),
            "taker_no_count_in_minute": float(trade_aggs["taker_no_count_in_minute"][i]),
            "taker_flow_in_minute": float(
                trade_aggs["taker_yes_count_in_minute"][i] - trade_aggs["taker_no_count_in_minute"][i]
            ),
            "vwap_in_minute": float(trade_aggs["vwap_in_minute"][i]) if not np.isnan(trade_aggs["vwap_in_minute"][i]) else None,
            # Open interest
            "open_interest_at_minute_end": float(oi_raw[i]) if not np.isnan(oi_raw[i]) else None,
            "open_interest_ffill": float(oi_ffill[i]) if not np.isnan(oi_ffill[i]) else None,
            "open_interest_delta_from_prior_minute": float(oi_delta[i]) if not np.isnan(oi_delta[i]) else None,
            # Match-lifecycle
            "open_time_ts": open_time_ts,
            "expected_expiration_ts": expected_expiration_ts,
            "close_time_ts": close_time_ts,
            "settlement_ts": settlement_ts,
            "match_start_ts": match_start_ts,
            "match_start_method": match_start_method,
            "time_to_match_start_min": float(time_to_match_start_min[i]) if not np.isnan(time_to_match_start_min[i]) else None,
            "time_to_close_min": float(time_to_close_min[i]) if not np.isnan(time_to_close_min[i]) else None,
            "time_to_settlement_min": float(time_to_settlement_min[i]) if not np.isnan(time_to_settlement_min[i]) else None,
            "minutes_since_open": float(minutes_since_open_arr[i]) if not np.isnan(minutes_since_open_arr[i]) else None,
            # Regime / phase
            "regime": regimes[i],
            "premarket_phase": premarket_phases[i],
            # Cell-key features
            "entry_band_lo": int(eb_lo_arr[i]) if eb_lo_arr[i] >= 0 else None,
            "entry_band_hi": int(eb_hi_arr[i]) if eb_hi_arr[i] >= 0 else None,
            "spread_band": spread_band_arr[i],
            "volume_intensity": volume_intensity_arr[i],
            # Forward labels
            "max_yes_bid_forward_5min": _f(fwd["max_yes_bid_forward_5min"][i]),
            "max_yes_bid_forward_15min": _f(fwd["max_yes_bid_forward_15min"][i]),
            "max_yes_bid_forward_30min": _f(fwd["max_yes_bid_forward_30min"][i]),
            "max_yes_bid_forward_60min": _f(fwd["max_yes_bid_forward_60min"][i]),
            "max_yes_bid_forward_to_match_start": _f(fwd["max_yes_bid_forward_to_match_start"][i]),
            "max_yes_bid_forward_to_settlement": _f(fwd["max_yes_bid_forward_to_settlement"][i]),
            "min_yes_ask_forward_5min": _f(fwd["min_yes_ask_forward_5min"][i]),
            "min_yes_ask_forward_15min": _f(fwd["min_yes_ask_forward_15min"][i]),
            "min_yes_ask_forward_30min": _f(fwd["min_yes_ask_forward_30min"][i]),
            "min_yes_ask_forward_60min": _f(fwd["min_yes_ask_forward_60min"][i]),
            "min_yes_ask_forward_to_match_start": _f(fwd["min_yes_ask_forward_to_match_start"][i]),
            "min_yes_ask_forward_to_settlement": _f(fwd["min_yes_ask_forward_to_settlement"][i]),
            "bounce_5min": _f(bounces["bounce_5min"][i]),
            "bounce_15min": _f(bounces["bounce_15min"][i]),
            "bounce_30min": _f(bounces["bounce_30min"][i]),
            "bounce_60min": _f(bounces["bounce_60min"][i]),
            "bounce_to_match_start": _f(bounces["bounce_to_match_start"][i]),
            "bounce_to_settlement": _f(bounces["bounce_to_settlement"][i]),
            "settlement_value": settlement_value,
            "result": result,
            # Paired-leg (spec Section 2.9, 14 columns)
            "partner_ticker": partner_ticker,
            "partner_yes_bid_close": p_obs.get("partner_yes_bid_close"),
            "partner_yes_ask_close": p_obs.get("partner_yes_ask_close"),
            "partner_spread_close": p_obs.get("partner_spread_close"),
            "partner_volume_in_minute": p_obs.get("partner_volume_in_minute"),
            "partner_trade_count_in_minute": int(p_obs["partner_trade_count_in_minute"])
                if "partner_trade_count_in_minute" in p_obs else None,
            "partner_taker_flow_in_minute": p_obs.get("partner_taker_flow_in_minute"),
            "partner_open_interest_ffill": p_obs.get("partner_open_interest_ffill"),
            "paired_yes_bid_sum": paired_cols["paired_yes_bid_sum"],
            "paired_yes_ask_sum": paired_cols["paired_yes_ask_sum"],
            "paired_mid_sum": paired_cols["paired_mid_sum"],
            "paired_arb_gap_maker": paired_cols["paired_arb_gap_maker"],
            "paired_arb_gap_taker": paired_cols["paired_arb_gap_taker"],
            "partner_volume_ratio": paired_cols["partner_volume_ratio"],
        }
        rows.append(r)
    return pd.DataFrame(rows)


def _f(x):
    """Convert numpy nan-bearing float to None for parquet null."""
    if x is None: return None
    try:
        if np.isnan(x): return None
    except (TypeError, ValueError):
        return x
    return float(x)


# ============================================================
# Phase 1 main
# ============================================================

def phase1(ticker=PHASE1_TICKER, formation_window_min=FORMATION_WINDOW_MIN_DEFAULT):
    os.makedirs(PROBE_DIR, exist_ok=True)
    log_path = os.path.join(PROBE_DIR, "build_log_phase1.txt")
    if os.path.exists(log_path):
        os.remove(log_path)
    t_start = time.time()

    log("=" * 60, log_path)
    log(f"Per-minute universe — Phase 1 (single-ticker mode)", log_path)
    log(f"Ticker: {ticker}", log_path)
    log(f"formation_window_min: {formation_window_min}", log_path)
    log("=" * 60, log_path)

    df = build_ticker_rows(ticker, formation_window_min=formation_window_min)
    if df is None:
        log(f"ABORT: ticker {ticker} not found in metadata or no candles", log_path)
        sys.exit(1)
    elapsed = time.time() - t_start

    log(f"Rows produced: {len(df)}", log_path)
    log(f"Columns: {len(df.columns)}", log_path)
    log(f"Runtime: {elapsed:.1f}s", log_path)

    # ----- Hard gates per spec Section 5 -----
    log("", log_path)
    log("=== HARD GATES (spec Section 5) ===", log_path)

    # Check 1: row count parity with g9_candles for this ticker
    candles_ticker_rows = pq.read_table(
        CANDLES_PARQUET, columns=["ticker"], filters=[("ticker", "=", ticker)]
    ).num_rows
    check1_pass = len(df) == candles_ticker_rows
    log(f"Check 1 (row count parity with g9_candles[ticker]): "
        f"per_minute={len(df)} g9_candles={candles_ticker_rows} "
        f"→ {'PASS' if check1_pass else 'FAIL'}", log_path)

    # Check 2: 100% population on always-populated columns
    always_pop_cols = ["yes_bid_close", "yes_ask_close", "spread_close", "mid_close",
                       "ticker", "minute_ts", "regime"]
    null_counts = {c: int(df[c].isna().sum()) for c in always_pop_cols}
    check2_pass = all(v == 0 for v in null_counts.values())
    log(f"Check 2 (always-populated column null counts): {null_counts} "
        f"→ {'PASS' if check2_pass else 'FAIL'}", log_path)

    # Check 4: forward-label monotonicity
    monotonic_violations_bid = 0
    monotonic_violations_ask = 0
    for i in range(len(df)):
        b5, b15, b30, b60 = (
            df["max_yes_bid_forward_5min"].iloc[i],
            df["max_yes_bid_forward_15min"].iloc[i],
            df["max_yes_bid_forward_30min"].iloc[i],
            df["max_yes_bid_forward_60min"].iloc[i],
        )
        # Skip if any is None — monotonicity undefined
        if any(pd.isna(x) for x in [b5, b15, b30, b60]):
            continue
        if not (b60 >= b30 >= b15 >= b5):
            monotonic_violations_bid += 1
        a5, a15, a30, a60 = (
            df["min_yes_ask_forward_5min"].iloc[i],
            df["min_yes_ask_forward_15min"].iloc[i],
            df["min_yes_ask_forward_30min"].iloc[i],
            df["min_yes_ask_forward_60min"].iloc[i],
        )
        if any(pd.isna(x) for x in [a5, a15, a30, a60]):
            continue
        if not (a60 <= a30 <= a15 <= a5):
            monotonic_violations_ask += 1
    check4_pass = monotonic_violations_bid == 0 and monotonic_violations_ask == 0
    log(f"Check 4 (forward-label monotonicity): "
        f"bid violations={monotonic_violations_bid}, ask violations={monotonic_violations_ask} "
        f"→ {'PASS' if check4_pass else 'FAIL'}", log_path)

    # Schema dump
    log("", log_path)
    log("=== SCHEMA (column → dtype, sample value, null count) ===", log_path)
    for col in df.columns:
        dt = df[col].dtype
        nn = df[col].notna().sum()
        nc = df[col].isna().sum()
        sample = df[col].iloc[0] if df[col].notna().any() else "(all null)"
        sample_str = str(sample)[:60]
        log(f"  {col:42s} dtype={str(dt):12s} non_null={nn:>4d}/{len(df)} null={nc:>4d} sample={sample_str}", log_path)

    # Regime distribution
    log("", log_path)
    log("=== regime distribution ===", log_path)
    log(f"  {dict(df['regime'].value_counts())}", log_path)
    log(f"=== premarket_phase distribution ===", log_path)
    log(f"  {dict(df['premarket_phase'].value_counts(dropna=False))}", log_path)
    log(f"=== match_start_method ===", log_path)
    log(f"  {dict(df['match_start_method'].value_counts())}", log_path)
    log(f"  match_start_ts = {df['match_start_ts'].iloc[0]}", log_path)

    # Write output parquet
    out_path = os.path.join(PROBE_DIR, "per_minute_universe_phase1.parquet")
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), out_path, compression="snappy")
    log("", log_path)
    log(f"Wrote {out_path}: {len(df)} rows, {os.path.getsize(out_path):,} bytes", log_path)

    # Write run summary
    summary = {
        "phase": 1,
        "spec_commit": "87e8e9a2",
        "ticker": ticker,
        "formation_window_min": formation_window_min,
        "n_rows": int(len(df)),
        "n_columns": int(len(df.columns)),
        "runtime_seconds": round(elapsed, 2),
        "validation_gate": {
            "check1_row_count_parity_pass": bool(check1_pass),
            "check1_per_minute_rows": int(len(df)),
            "check1_g9_candles_rows": int(candles_ticker_rows),
            "check2_always_populated_pass": bool(check2_pass),
            "check2_null_counts": null_counts,
            "check4_forward_monotonicity_pass": bool(check4_pass),
            "check4_bid_violations": int(monotonic_violations_bid),
            "check4_ask_violations": int(monotonic_violations_ask),
            "check3_DEFERRED": "regression vs L Bv2 cell_summary_phase3 requires corpus; runs at T37b Phase 3 / T37c",
        },
        "regime_distribution": dict(df["regime"].value_counts()),
        "premarket_phase_distribution": {str(k): int(v) for k, v in df["premarket_phase"].value_counts(dropna=False).items()},
        "match_start_method": dict(df["match_start_method"].value_counts()),
        "match_start_ts": int(df["match_start_ts"].iloc[0]) if pd.notna(df["match_start_ts"].iloc[0]) else None,
    }
    summary_path = os.path.join(PROBE_DIR, "run_summary_phase1.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    log(f"Wrote {summary_path}", log_path)
    log("=" * 60, log_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], required=True)
    parser.add_argument("--ticker", type=str, default=PHASE1_TICKER,
                        help="Ticker to process in Phase 1 (default: KXATPMATCH-25JUN18RUNMCD-RUN)")
    parser.add_argument("--formation-window-min", type=int, default=FORMATION_WINDOW_MIN_DEFAULT)
    args = parser.parse_args()
    if args.phase == 1:
        phase1(ticker=args.ticker, formation_window_min=args.formation_window_min)
    else:
        raise NotImplementedError(f"Phase {args.phase} not yet implemented; pending separate single-concern commit.")


if __name__ == "__main__":
    main()
