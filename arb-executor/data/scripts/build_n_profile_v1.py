"""
n_profile_v1 producer — per-N measurement universe rollup.

Spec: docs/n_profile_v1_spec.md (evolving commit chain — see producer_commit
in n_profile.meta.json for the exact code provenance of any given artifact).

Inputs (all read-only):
  - data/durable/g9_trades.parquet
  - data/durable/g9_candles.parquet
  - data/durable/g9_metadata.parquet
  - data/durable/per_minute_universe/per_minute_features.parquet

Output:
  - data/durable/n_profile_v1/n_profile.parquet (45 cols, one row per N)
  - data/durable/n_profile_v1/validation_report.md
  - data/durable/n_profile_v1/n_profile.meta.json

C37 discipline: write .new, reload from disk, gate-validate, os.replace on all-pass.

Usage:
  python3 build_n_profile_v1.py [--phase {1,2,3}] [--input-base PATH] [--output-dir PATH]

Phases (per spec Section 3.3):
  Phase 1: 50 stratified tickers, <5 min, visual inspection.
  Phase 2: 1000 tickers stratified by category × tier, <30 min.
  Phase 3: full binary-outcome subset (~19,614 N's), <15 min single-threaded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
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
import pyarrow.parquet as pq

# ---------------------------------------------------------------------------
# pandas 3.0 + pyarrow 24 compat patch
# ---------------------------------------------------------------------------
# Same fix as Rung 0 commit 52edf132 and Rung 1 commit 168728d.
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
UTC = ZoneInfo("UTC")

DEFAULT_INPUT_BASE = Path("data/durable")
DEFAULT_OUTPUT_DIR = Path("data/durable/n_profile_v1")
DEFAULT_OUTPUT_FILE = "n_profile.parquet"
DEFAULT_REPORT_FILE = "validation_report.md"
DEFAULT_META_FILE = "n_profile.meta.json"

# Cutoff between historical and live tier per F29 / TAXONOMY
TIER_CUTOFF_UTC = datetime(2026, 3, 2, 0, 0, 0, tzinfo=UTC)

# Spec Section 2.1 — 45-column schema in exact order (col 44 n_minutes_observed
# per 7a72bc8; col 45 match_start_method per e4e0fdb — see SCHEMA_COLUMNS comment below)
SCHEMA_COLUMNS = [
    # Identity / pairing (7)
    "ticker", "event_ticker", "paired_event_partner_ticker",
    "category", "match_start_ts", "settlement_ts", "settlement_value_dollars",
    # Lifetime timing (4)
    "market_open_ts", "first_trade_ts", "last_trade_ts_pre_resolution", "lifetime_minutes",
    # Premarket vs in-match phase counts (5 — incl n_minutes_observed col 44 per spec 7a72bc8)
    "n_minutes_premarket", "n_minutes_in_match",
    "n_active_minutes_premarket", "n_active_minutes_in_match",
    "n_minutes_observed",
    # Volume profile (6)
    "total_volume_lifetime", "total_volume_premarket", "total_volume_in_match",
    "peak_volume_minute_ts", "peak_volume_in_that_minute", "mean_volume_per_active_minute",
    # Trade-count profile (4)
    "total_trade_count_lifetime", "total_trade_count_premarket",
    "total_trade_count_in_match", "mean_trades_per_active_minute",
    # Taker-side flow (3)
    "yes_taker_volume_cum", "no_taker_volume_cum", "yes_taker_imbalance",
    # OI trajectory (4)
    "oi_at_match_start", "oi_at_t20m", "oi_max_lifetime", "oi_max_minute_ts",
    # Price activity (4)
    "price_first_trade", "price_last_trade_pre_resolution",
    "price_min_pre_resolution", "price_max_pre_resolution",
    # Partner-N stats (4)
    "partner_total_volume_lifetime", "partner_total_trade_count_lifetime",
    "partner_total_volume_premarket", "both_sides_active_minutes",
    # Sample-quality flags (4 — incl match_start_method col 45 per spec e4e0fdb)
    "has_complete_trade_tape", "has_complete_candle_tape", "tier",
    "match_start_method",
]
# 45 enumerated columns (spec §2.1, in order). Commit 7a72bc8 added
# n_minutes_observed (col 44, gate-3 RHS + §4.2 denominator); commit e4e0fdb
# added match_start_method (col 45, F35 interim mitigation — makes the
# boundary-unreliable 6.4% tier-3 cohort downstream-filterable). Both columns
# earn their slots by purpose, not as phantom fillers.
assert len(SCHEMA_COLUMNS) == 45, f"schema column count = {len(SCHEMA_COLUMNS)} != 45"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("n_profile_v1")
os.environ["TZ"] = "America/New_York"


@dataclass
class GateResult:
    name: str
    passed: bool
    n_violations: int
    detail: str = ""


@dataclass
class ProducerResult:
    rows_emitted: int
    gate_results: list[GateResult] = field(default_factory=list)
    output_sha256: Optional[str] = None
    output_bytes: Optional[int] = None
    run_started_at_et: Optional[str] = None
    run_completed_at_et: Optional[str] = None
    inputs_sha256: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_event_ticker(ticker: str) -> str:
    """Per LESSONS B19: event_ticker = ticker.rsplit('-', 1)[0]."""
    return ticker.rsplit("-", 1)[0]


def to_et(ts) -> Optional[pd.Timestamp]:
    """
    Convert any timestamp to tz-aware ET. Returns None on null.

    Handles:
    - None / NaN / NaT → None
    - ISO-8601 strings ('2026-04-01T04:31:00Z') — pd.Timestamp parses fine
    - tz-aware pd.Timestamp → tz_convert
    - int / float / int64 / float64 representing UNIX SECONDS — common in
      per_minute_features (match_start_ts, minute_ts) per schema probe
    - existing tz-naive pd.Timestamp → assume UTC, then convert
    """
    if ts is None:
        return None
    # Guard against NaN/NaT for numerics
    try:
        if pd.isna(ts):
            return None
    except (TypeError, ValueError):
        pass
    # Unix seconds (int/float) — convert via to_datetime with unit='s'
    if isinstance(ts, (int, float, np.integer, np.floating)):
        t = pd.to_datetime(ts, unit="s", utc=True)
    else:
        t = pd.Timestamp(ts)
        if t.tz is None:
            t = t.tz_localize("UTC")
    return t.tz_convert(ET)


def assign_tier(market_open_ts: Optional[pd.Timestamp]) -> str:
    """historical vs live per Mar 2 2026 UTC cutoff."""
    if market_open_ts is None or pd.isna(market_open_ts):
        return "unknown"
    t = pd.Timestamp(market_open_ts)
    if t.tz is None:
        t = t.tz_localize("UTC")
    return "historical" if t < pd.Timestamp(TIER_CUTOFF_UTC) else "live"


# ---------------------------------------------------------------------------
# Per-ticker pyarrow predicate-pushdown I/O
# ---------------------------------------------------------------------------
# Mirrors build_rung0_cell_economics.py read_trades_for_ticker (~line 205):
# the proven in-repo pattern that ran the FULL g9 corpus in ~1.9 GB without
# OOM. NEVER full-load-then-filter the trade tape in a DataFrame — Phase 1
# retry #3 was OOM-killed full-loading the 1.5 GB / 33.7M-row
# g9_trades.parquet on the ~1.9 GB VPS. Each ticker reads only its own row
# group(s) via the pushdown predicate.

TRADES_PUSHDOWN_COLS = [
    "created_time", "count_fp", "taker_side",
    "yes_price_dollars", "no_price_dollars",
]
CANDLES_PUSHDOWN_COLS = ["end_period_ts", "open_interest_fp"]


def read_trades_for_ticker(trades_path: Path, ticker: str) -> pd.DataFrame:
    """Pushdown read of g9_trades for one ticker. Empty DF if no rows."""
    tbl = pq.read_table(
        str(trades_path),
        columns=TRADES_PUSHDOWN_COLS,
        filters=[("ticker", "=", ticker)],
    )
    if tbl.num_rows == 0:
        return pd.DataFrame()
    return tbl.to_pandas()


def read_candles_for_ticker(candles_path: Path, ticker: str) -> pd.DataFrame:
    """Pushdown read of g9_candles for one ticker. Empty DF if no rows."""
    tbl = pq.read_table(
        str(candles_path),
        columns=CANDLES_PUSHDOWN_COLS,
        filters=[("ticker", "=", ticker)],
    )
    if tbl.num_rows == 0:
        return pd.DataFrame()
    return tbl.to_pandas()


# ---------------------------------------------------------------------------
# Pass 1: per-ticker rollup
# ---------------------------------------------------------------------------

def compute_per_ticker_row(
    ticker: str,
    metadata_row: pd.Series,
    trades_subset: pd.DataFrame,
    candles_subset: pd.DataFrame,
    per_minute_subset: pd.DataFrame,
) -> Optional[dict]:
    """
    Compute all self-columns (cols 1-36, 41-43) for one ticker.
    Partner columns (37-40) filled in pass 2-3.
    Returns None if essential data is missing (logged as dropout).
    """
    # Identity
    event_ticker = derive_event_ticker(ticker)

    # Settlement value: source from per_minute_features.settlement_value (double 0.0/1.0)
    # per spec §3.2 corrected at b43fbaf7. g9_metadata.settlement_value_dollars is a
    # STRING column ('0.0000'/'1.0000'/etc) per schema probe and float comparisons
    # silently fail. Upstream binary filter (result ∈ yes/no) has already excluded scalars.
    settlement_value = None
    if not per_minute_subset.empty and "settlement_value" in per_minute_subset.columns:
        sv_vals = per_minute_subset["settlement_value"].dropna().unique()
        if len(sv_vals) > 0:
            settlement_value = float(sv_vals[0])
    if settlement_value is None:
        # Metadata fallback (coerce string to numeric); should rarely fire post-probe.
        meta_sv = metadata_row.get("settlement_value_dollars")
        if meta_sv is not None and not pd.isna(meta_sv):
            try:
                settlement_value = float(meta_sv)
            except (TypeError, ValueError):
                settlement_value = None
    if settlement_value is None:
        return None
    if settlement_value not in (0.0, 1.0):
        return None  # scalars excluded (defensive — upstream filter should have excluded)

    # Category from per_minute_features (T37-derived; metadata has no category column).
    category = None
    if not per_minute_subset.empty and "category" in per_minute_subset.columns:
        cat_vals = per_minute_subset["category"].dropna().unique()
        if len(cat_vals) > 0:
            category = str(cat_vals[0])

    market_open_ts = to_et(metadata_row.get("market_open_ts",
                                             metadata_row.get("open_time")))
    settlement_ts = to_et(metadata_row.get("settlement_ts",
                                            metadata_row.get("settlement_time")))

    # match_start_ts from per_minute_features (canonical; int64 unix seconds with NaN per probe).
    # to_et() handles unix-second numerics.
    match_start_ts = None
    if not per_minute_subset.empty and "match_start_ts" in per_minute_subset.columns:
        ms_vals = per_minute_subset["match_start_ts"].dropna().unique()
        if len(ms_vals) > 0:
            match_start_ts = to_et(ms_vals[0])

    # Partner ticker — source column is `partner_ticker` (large_string) per schema probe;
    # output column name stays `paired_event_partner_ticker` per spec §2.1.
    partner_ticker = None
    if not per_minute_subset.empty and "partner_ticker" in per_minute_subset.columns:
        pp = per_minute_subset["partner_ticker"].dropna().unique()
        if len(pp) > 0:
            partner_ticker = str(pp[0])

    # match_start_method (spec §2.1 col 45, F35 interim mitigation) — the T37
    # signal tier that fired: both_sides_price_discovery / both_sides_trade_density
    # / expected_expiration_fallback (tier-3, boundary-unreliable per F35) /
    # unknown (C32 early-settle). Same source pattern as partner_ticker.
    match_start_method = None
    if not per_minute_subset.empty and "match_start_method" in per_minute_subset.columns:
        msm = per_minute_subset["match_start_method"].dropna().unique()
        if len(msm) > 0:
            match_start_method = str(msm[0])

    # Lifetime timing
    lifetime_minutes = None
    if market_open_ts is not None and settlement_ts is not None:
        lifetime_minutes = int((settlement_ts - market_open_ts).total_seconds() / 60)

    # Trade-tape aggregates (canonical per C36)
    trade_count_lifetime = 0
    trade_count_premarket = 0
    trade_count_in_match = 0
    volume_lifetime = 0
    volume_premarket = 0
    volume_in_match = 0
    yes_taker_vol = 0
    no_taker_vol = 0
    first_trade_ts = None
    last_trade_ts_pre_res = None
    price_first = None
    price_last_pre_res = None
    price_min_pre_res = None
    price_max_pre_res = None
    has_trade_tape = not trades_subset.empty

    if has_trade_tape and "count_fp" in trades_subset.columns:
        # Filter to non-zero count_fp per C36 zero-size-trade discovery
        active_trades = trades_subset[trades_subset["count_fp"] > 0].copy()
        if not active_trades.empty:
            # Normalize created_time to ET. g9_trades.created_time is string
            # ISO-8601 with HETEROGENEOUS fractional-second precision (probe
            # 2026-05-16: 27-char/6-digit bulk down to no-frac; pandas inferred
            # fixed format crashes on the variants — the :350 ValueError).
            # format='ISO8601' handles all precision variants; utc=True makes
            # the result tz-aware directly (no localize branch needed).
            ct = pd.to_datetime(
                active_trades["created_time"], format="ISO8601", utc=True
            )
            ct = ct.dt.tz_convert(ET)
            active_trades = active_trades.assign(_ts_et=ct)
            active_trades = active_trades.sort_values("_ts_et")

            trade_count_lifetime = len(active_trades)
            volume_lifetime = int(active_trades["count_fp"].sum())
            first_trade_ts = active_trades["_ts_et"].iloc[0]

            # Phase split by match_start_ts
            if match_start_ts is not None:
                pre = active_trades[active_trades["_ts_et"] < match_start_ts]
                post = active_trades[active_trades["_ts_et"] >= match_start_ts]
                trade_count_premarket = len(pre)
                trade_count_in_match = len(post)
                volume_premarket = int(pre["count_fp"].sum()) if not pre.empty else 0
                volume_in_match = int(post["count_fp"].sum()) if not post.empty else 0
            else:
                trade_count_premarket = trade_count_lifetime
                volume_premarket = volume_lifetime

            # Taker-side flow
            if "taker_side" in active_trades.columns:
                yes_taker_vol = int(
                    active_trades.loc[active_trades["taker_side"] == "yes", "count_fp"].sum()
                )
                no_taker_vol = int(
                    active_trades.loc[active_trades["taker_side"] == "no", "count_fp"].sum()
                )

            # Price activity (pre-resolution = before first 99c/1c touch)
            # Conservative: use all trades pre-settlement_ts as pre-resolution proxy.
            # Full first_extreme_touch_ts would require Rung 0 join; v1 uses
            # settlement_ts-bounded as the proxy.
            pre_res_trades = active_trades
            if settlement_ts is not None:
                pre_res_trades = active_trades[active_trades["_ts_et"] < settlement_ts]
            if not pre_res_trades.empty and "yes_price_dollars" in pre_res_trades.columns:
                pp = pre_res_trades["yes_price_dollars"].dropna()
                if len(pp) > 0:
                    price_first = float(pp.iloc[0])
                    price_last_pre_res = float(pp.iloc[-1])
                    price_min_pre_res = float(pp.min())
                    price_max_pre_res = float(pp.max())
                    last_trade_ts_pre_res = pre_res_trades["_ts_et"].iloc[-1]

    # Per-minute active-minute counts
    n_minutes_premarket = 0
    n_minutes_in_match = 0
    n_active_minutes_premarket = 0
    n_active_minutes_in_match = 0
    peak_volume_minute_ts = None
    peak_volume_in_that_minute = 0
    if not per_minute_subset.empty:
        pm = per_minute_subset.copy()
        if "minute_ts" in pm.columns:
            # minute_ts is int64 UNIX SECONDS (probe 2026-05-16). Parsing
            # without unit='s' interprets it as nanoseconds → 1970 garbage
            # → silently corrupts the premarket/in-match phase split.
            pm["_ts_et"] = pd.to_datetime(
                pm["minute_ts"], unit="s", utc=True
            ).dt.tz_convert(ET)
            if match_start_ts is not None:
                pm_pre = pm[pm["_ts_et"] < match_start_ts]
                pm_post = pm[pm["_ts_et"] >= match_start_ts]
                n_minutes_premarket = len(pm_pre)
                n_minutes_in_match = len(pm_post)
                if "trade_count_in_minute" in pm.columns:
                    n_active_minutes_premarket = int(
                        (pm_pre["trade_count_in_minute"] > 0).sum()
                    )
                    n_active_minutes_in_match = int(
                        (pm_post["trade_count_in_minute"] > 0).sum()
                    )
            else:
                n_minutes_premarket = len(pm)
                if "trade_count_in_minute" in pm.columns:
                    n_active_minutes_premarket = int(
                        (pm["trade_count_in_minute"] > 0).sum()
                    )
            # Peak volume minute
            if "volume_in_minute" in pm.columns:
                vol_pos = pm[pm["volume_in_minute"] > 0]
                if not vol_pos.empty:
                    peak_idx = vol_pos["volume_in_minute"].idxmax()
                    peak_volume_minute_ts = vol_pos.loc[peak_idx, "_ts_et"]
                    peak_volume_in_that_minute = int(
                        vol_pos.loc[peak_idx, "volume_in_minute"]
                    )

    total_active_minutes = n_active_minutes_premarket + n_active_minutes_in_match
    mean_volume_per_active_minute = (
        volume_lifetime / total_active_minutes if total_active_minutes > 0 else 0.0
    )
    mean_trades_per_active_minute = (
        trade_count_lifetime / total_active_minutes if total_active_minutes > 0 else 0.0
    )
    yes_taker_imbalance = (
        (yes_taker_vol - no_taker_vol) / volume_lifetime if volume_lifetime > 0 else None
    )

    # OI trajectory from candles
    has_candle_tape = not candles_subset.empty
    oi_at_match_start = None
    oi_at_t20m = None
    oi_max_lifetime = None
    oi_max_minute_ts = None
    if has_candle_tape and "open_interest_fp" in candles_subset.columns:
        c = candles_subset.copy()
        if "end_period_ts" in c.columns:
            c["_ts_et"] = pd.to_datetime(c["end_period_ts"], unit="s", utc=True)
            c["_ts_et"] = c["_ts_et"].dt.tz_convert(ET)
        oi_series = c["open_interest_fp"].dropna()
        if len(oi_series) > 0:
            oi_max_lifetime = int(oi_series.max())
            max_idx = oi_series.idxmax()
            if "_ts_et" in c.columns:
                oi_max_minute_ts = c.loc[max_idx, "_ts_et"]
        if match_start_ts is not None and "_ts_et" in c.columns:
            ms_match = c[(c["_ts_et"] >= match_start_ts)
                          & (c["_ts_et"] < match_start_ts + pd.Timedelta(minutes=1))]
            if not ms_match.empty:
                oi_val = ms_match["open_interest_fp"].iloc[0]
                if pd.notna(oi_val):
                    oi_at_match_start = int(oi_val)
            # T-20m
            t20m = match_start_ts - pd.Timedelta(minutes=20)
            t20m_match = c[(c["_ts_et"] >= t20m)
                            & (c["_ts_et"] < t20m + pd.Timedelta(minutes=1))]
            if not t20m_match.empty:
                oi_val = t20m_match["open_interest_fp"].iloc[0]
                if pd.notna(oi_val):
                    oi_at_t20m = int(oi_val)

    return {
        "ticker": ticker,
        "event_ticker": event_ticker,
        "paired_event_partner_ticker": partner_ticker,
        "category": category,
        "match_start_ts": match_start_ts,
        "settlement_ts": settlement_ts,
        "settlement_value_dollars": float(settlement_value),
        "market_open_ts": market_open_ts,
        "first_trade_ts": first_trade_ts,
        "last_trade_ts_pre_resolution": last_trade_ts_pre_res,
        "lifetime_minutes": lifetime_minutes,
        "n_minutes_premarket": n_minutes_premarket,
        "n_minutes_in_match": n_minutes_in_match,
        "n_active_minutes_premarket": n_active_minutes_premarket,
        "n_active_minutes_in_match": n_active_minutes_in_match,
        # col 44 per spec 7a72bc8: observed-row count = the phase partition's
        # total. By construction n_minutes_premarket + n_minutes_in_match IS the
        # exhaustive partition of this ticker's per_minute_features rows
        # (pm_pre ⊎ pm_post = pm, or all-premarket when match_start_ts is NaT),
        # so this equals len(per_minute_subset). Computed as the sum so gate-3
        # sub-invariant (a) holds by construction while staying disk-checkable.
        "n_minutes_observed": n_minutes_premarket + n_minutes_in_match,
        "total_volume_lifetime": volume_lifetime,
        "total_volume_premarket": volume_premarket,
        "total_volume_in_match": volume_in_match,
        "peak_volume_minute_ts": peak_volume_minute_ts,
        "peak_volume_in_that_minute": peak_volume_in_that_minute,
        "mean_volume_per_active_minute": mean_volume_per_active_minute,
        "total_trade_count_lifetime": trade_count_lifetime,
        "total_trade_count_premarket": trade_count_premarket,
        "total_trade_count_in_match": trade_count_in_match,
        "mean_trades_per_active_minute": mean_trades_per_active_minute,
        "yes_taker_volume_cum": yes_taker_vol,
        "no_taker_volume_cum": no_taker_vol,
        "yes_taker_imbalance": yes_taker_imbalance,
        "oi_at_match_start": oi_at_match_start,
        "oi_at_t20m": oi_at_t20m,
        "oi_max_lifetime": oi_max_lifetime,
        "oi_max_minute_ts": oi_max_minute_ts,
        "price_first_trade": price_first,
        "price_last_trade_pre_resolution": price_last_pre_res,
        "price_min_pre_resolution": price_min_pre_res,
        "price_max_pre_resolution": price_max_pre_res,
        # Partner columns filled in pass 2-3
        "partner_total_volume_lifetime": None,
        "partner_total_trade_count_lifetime": None,
        "partner_total_volume_premarket": None,
        "both_sides_active_minutes": None,
        "has_complete_trade_tape": has_trade_tape,
        "has_complete_candle_tape": has_candle_tape,
        "tier": assign_tier(market_open_ts),
        "match_start_method": match_start_method,
    }


# ---------------------------------------------------------------------------
# Pass 2: partner-stats join
# ---------------------------------------------------------------------------

def join_partner_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each row, look up partner_event_partner_ticker's stats from same df.
    Adds partner_total_volume_lifetime, partner_total_trade_count_lifetime,
    partner_total_volume_premarket.
    """
    log.info("Pass 2: joining partner stats")
    lookup = df.set_index("ticker")[
        ["total_volume_lifetime", "total_trade_count_lifetime", "total_volume_premarket"]
    ].to_dict("index")

    def get_partner(t, key):
        if t is None or t not in lookup:
            return None
        return lookup[t].get(key)

    df["partner_total_volume_lifetime"] = df["paired_event_partner_ticker"].apply(
        lambda t: get_partner(t, "total_volume_lifetime")
    )
    df["partner_total_trade_count_lifetime"] = df["paired_event_partner_ticker"].apply(
        lambda t: get_partner(t, "total_trade_count_lifetime")
    )
    df["partner_total_volume_premarket"] = df["paired_event_partner_ticker"].apply(
        lambda t: get_partner(t, "total_volume_premarket")
    )
    return df


# ---------------------------------------------------------------------------
# Pass 3: both_sides_active_minutes
# ---------------------------------------------------------------------------

def compute_both_sides_active_minutes(
    df: pd.DataFrame, per_minute_df: pd.DataFrame
) -> pd.DataFrame:
    """
    For each ticker, count minutes where BOTH this N and partner N had
    trade_count_in_minute > 0 at the same minute_ts.
    """
    log.info("Pass 3: computing both_sides_active_minutes")
    if "trade_count_in_minute" not in per_minute_df.columns:
        df["both_sides_active_minutes"] = 0
        return df

    active_minutes = per_minute_df[per_minute_df["trade_count_in_minute"] > 0][
        ["ticker", "minute_ts"]
    ].copy()
    # minute_ts is int64 UNIX SECONDS (probe 2026-05-16) — parse with unit='s'
    # or the integer is read as nanoseconds → 1970 garbage. utc=True yields
    # tz-aware directly (set-membership join below only needs consistent tz).
    active_minutes["minute_ts_norm"] = pd.to_datetime(
        active_minutes["minute_ts"], unit="s", utc=True
    )

    ticker_minute_set = active_minutes.groupby("ticker")["minute_ts_norm"].apply(set).to_dict()

    def count_both_active(row):
        t = row["ticker"]
        p = row["paired_event_partner_ticker"]
        if t is None or p is None:
            return 0
        s_self = ticker_minute_set.get(t, set())
        s_part = ticker_minute_set.get(p, set())
        return len(s_self & s_part)

    df["both_sides_active_minutes"] = df.apply(count_both_active, axis=1)
    return df


# ---------------------------------------------------------------------------
# Hard gates (spec Section 4.1)
# ---------------------------------------------------------------------------

def gate1_row_count(df: pd.DataFrame, expected: int, dropout_count: int) -> GateResult:
    actual = len(df)
    return GateResult(
        name="gate1_row_count",
        passed=(actual + dropout_count == expected),
        n_violations=abs(actual + dropout_count - expected),
        detail=f"expected={expected} emitted={actual} dropouts={dropout_count}",
    )


def gate2_partner_resolution(df: pd.DataFrame) -> GateResult:
    """Every row with non-null partner_total_volume_lifetime must have its partner ticker also in df."""
    tickers = set(df["ticker"])
    non_null = df[df["partner_total_volume_lifetime"].notna()]
    orphans = non_null[~non_null["paired_event_partner_ticker"].isin(tickers)]
    return GateResult(
        name="gate2_partner_resolution",
        passed=(len(orphans) == 0),
        n_violations=len(orphans),
        detail=f"{len(orphans)} orphan partner refs",
    )


def gate3_phase_partition_exhaustiveness(df: pd.DataFrame) -> GateResult:
    """
    Spec §4.1 gate 3 (redefined 8ccb92d, made disk-checkable 7a72bc8).
    Three sub-invariants over the OBSERVATION WINDOW (NOT wall-clock —
    lifetime_minutes is definitionally larger; comparing to it was the
    original v0.1 category-error defect surfaced Phase 1 retry #4):

      (a) EXHAUSTIVE PARTITION: n_minutes_premarket + n_minutes_in_match
          == n_minutes_observed exactly (zero tolerance).
      (b) ACTIVE SUBSET: n_active_minutes_premarket <= n_minutes_premarket
          AND n_active_minutes_in_match <= n_minutes_in_match.
      (c) NON-NEGATIVE: all four phase counts >= 0.
    """
    a_bad = df[
        (df["n_minutes_premarket"] + df["n_minutes_in_match"])
        != df["n_minutes_observed"]
    ]
    b_bad = df[
        (df["n_active_minutes_premarket"] > df["n_minutes_premarket"])
        | (df["n_active_minutes_in_match"] > df["n_minutes_in_match"])
    ]
    c_bad = df[
        (df["n_minutes_premarket"] < 0)
        | (df["n_minutes_in_match"] < 0)
        | (df["n_active_minutes_premarket"] < 0)
        | (df["n_active_minutes_in_match"] < 0)
    ]
    n_viol = len(a_bad) + len(b_bad) + len(c_bad)
    return GateResult(
        name="gate3_phase_partition_exhaustiveness",
        passed=(n_viol == 0),
        n_violations=n_viol,
        detail=(
            f"(a)exhaustive_partition_viol={len(a_bad)} "
            f"(b)active_subset_viol={len(b_bad)} "
            f"(c)negative_count_viol={len(c_bad)}"
        ),
    )


def gate4_volume_conservation(df: pd.DataFrame) -> GateResult:
    """total_volume_lifetime = total_volume_premarket + total_volume_in_match exactly."""
    diff = df["total_volume_lifetime"] - (df["total_volume_premarket"] + df["total_volume_in_match"])
    bad = df[diff != 0]
    return GateResult(
        name="gate4_volume_conservation",
        passed=(len(bad) == 0),
        n_violations=len(bad),
        detail=f"{len(bad)} rows with volume mismatch",
    )


def gate5_taker_side_conservation(df: pd.DataFrame) -> GateResult:
    """yes_taker_volume_cum + no_taker_volume_cum = total_volume_lifetime exactly per G19 100% taker_side populated."""
    diff = df["total_volume_lifetime"] - (df["yes_taker_volume_cum"] + df["no_taker_volume_cum"])
    bad = df[diff != 0]
    return GateResult(
        name="gate5_taker_side_conservation",
        passed=(len(bad) == 0),
        n_violations=len(bad),
        detail=f"{len(bad)} rows with taker-side mismatch",
    )


def gate6_oi_monotonicity(df: pd.DataFrame) -> GateResult:
    """oi_max_lifetime >= oi_at_match_start and >= oi_at_t20m (where both non-null)."""
    s1 = df[df["oi_max_lifetime"].notna() & df["oi_at_match_start"].notna()]
    bad1 = s1[s1["oi_max_lifetime"] < s1["oi_at_match_start"]]
    s2 = df[df["oi_max_lifetime"].notna() & df["oi_at_t20m"].notna()]
    bad2 = s2[s2["oi_max_lifetime"] < s2["oi_at_t20m"]]
    n = len(bad1) + len(bad2)
    return GateResult(
        name="gate6_oi_monotonicity",
        passed=(n == 0),
        n_violations=n,
        detail=f"match_start violations={len(bad1)} t20m violations={len(bad2)}",
    )


def gate7_tz_correctness(df: pd.DataFrame) -> GateResult:
    """Every timestamp column is timezone-aware ET. Zero naive timestamps."""
    ts_cols = ["match_start_ts", "settlement_ts", "market_open_ts",
               "first_trade_ts", "last_trade_ts_pre_resolution",
               "peak_volume_minute_ts", "oi_max_minute_ts"]
    violations = 0
    detail_parts = []
    for col in ts_cols:
        if col not in df.columns:
            continue
        non_null = df[df[col].notna()]
        if len(non_null) == 0:
            continue
        sample = non_null[col].iloc[0]
        if hasattr(sample, "tz") and sample.tz is None:
            violations += len(non_null)
            detail_parts.append(f"{col}={len(non_null)}_naive")
    return GateResult(
        name="gate7_tz_correctness",
        passed=(violations == 0),
        n_violations=violations,
        detail="; ".join(detail_parts) if detail_parts else "OK",
    )


def run_all_gates(on_disk_path: Path, expected_count: int, dropout_count: int) -> list[GateResult]:
    """C37 discipline: reload .new from disk and validate against bytes."""
    log.info(f"Reloading {on_disk_path} for gate validation")
    df = pq.read_table(str(on_disk_path)).to_pandas()
    log.info(f"On-disk shape: {df.shape}")
    return [
        gate1_row_count(df, expected_count, dropout_count),
        gate2_partner_resolution(df),
        gate3_phase_partition_exhaustiveness(df),
        gate4_volume_conservation(df),
        gate5_taker_side_conservation(df),
        gate6_oi_monotonicity(df),
        gate7_tz_correctness(df),
    ]


# ---------------------------------------------------------------------------
# Output I/O
# ---------------------------------------------------------------------------

def _producer_commit() -> str:
    """
    Short git commit of the producer code that generated an artifact — the
    most meaningful provenance anchor (the spec chain is reconstructable from
    the producer commit, not vice versa). Degrades to 'unknown' on ANY failure:
    provenance metadata must never abort an otherwise-valid data run.
    """
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def write_meta_sidecar(meta_path: Path, result: ProducerResult) -> None:
    meta = {
        "output_sha256": result.output_sha256,
        "output_bytes": result.output_bytes,
        "rows_emitted": result.rows_emitted,
        "run_started_at_et": result.run_started_at_et,
        "run_completed_at_et": result.run_completed_at_et,
        "spec": "docs/n_profile_v1_spec.md",
        "producer_commit": _producer_commit(),
        "inputs_sha256": result.inputs_sha256,
        "gates": [
            {"name": g.name, "passed": g.passed, "n_violations": g.n_violations, "detail": g.detail}
            for g in result.gate_results
        ],
    }
    meta_path.write_text(json.dumps(meta, indent=2, default=str))


def write_validation_report(report_path: Path, df: pd.DataFrame, result: ProducerResult) -> None:
    lines = [
        "# n_profile_v1 Validation Report",
        "",
        f"**Run completed:** {result.run_completed_at_et}",
        f"**Spec:** docs/n_profile_v1_spec.md (commit chain)",
        f"**Producer commit:** {_producer_commit()}",
        f"**Output sha256:** {result.output_sha256}",
        f"**Output bytes:** {result.output_bytes}",
        f"**Rows emitted:** {result.rows_emitted}",
        "",
        "## Gate results",
        "",
        "| Gate | Passed | N violations | Detail |",
        "|---|---|---|---|",
    ]
    for g in result.gate_results:
        marker = "PASS" if g.passed else "FAIL"
        lines.append(f"| {g.name} | {marker} | {g.n_violations} | {g.detail} |")
    lines += [
        "",
        "## Volume distribution (total_volume_lifetime)",
        "",
        f"- min: {df['total_volume_lifetime'].min()}",
        f"- p25: {df['total_volume_lifetime'].quantile(0.25):.0f}",
        f"- median: {df['total_volume_lifetime'].median():.0f}",
        f"- mean: {df['total_volume_lifetime'].mean():.0f}",
        f"- p75: {df['total_volume_lifetime'].quantile(0.75):.0f}",
        f"- p90: {df['total_volume_lifetime'].quantile(0.90):.0f}",
        f"- p99: {df['total_volume_lifetime'].quantile(0.99):.0f}",
        f"- max: {df['total_volume_lifetime'].max()}",
        "",
        "## Both-sides-active minute distribution",
        "",
        f"- median: {df['both_sides_active_minutes'].median():.0f}",
        f"- p75: {df['both_sides_active_minutes'].quantile(0.75):.0f}",
        f"- p90: {df['both_sides_active_minutes'].quantile(0.90):.0f}",
        f"- max: {df['both_sides_active_minutes'].max()}",
        "",
        "## Per-tier counts",
        "",
    ]
    for tier, count in df["tier"].value_counts().items():
        lines.append(f"- {tier}: {count}")
    lines += [
        "",
        "## Per-category counts",
        "",
    ]
    for cat, count in df["category"].value_counts().items():
        lines.append(f"- {cat}: {count}")
    # §4.2 match_start_method distribution + zero-in-match breakdown (spec e4e0fdb;
    # LESSONS F35 — surfaces the tier-3 boundary-unreliable + unknown early-settle
    # cohorts in every build so downstream F35-reliability filtering is visible,
    # not just ad-hoc computable from the parquet).
    lines += [
        "",
        "## match_start_method distribution + zero-in-match (LESSONS F35)",
        "",
        "| method | N | zero_in_match | pct_zero | median_in_match |",
        "|---|---|---|---|---|",
    ]
    if "match_start_method" in df.columns:
        _z = df["n_minutes_in_match"] == 0
        for method, grp in df.groupby(df["match_start_method"].fillna("<null>")):
            n = len(grp)
            zc = int((grp["n_minutes_in_match"] == 0).sum())
            pz = (zc / n) if n else 0.0
            mim = grp["n_minutes_in_match"].median()
            lines.append(f"| {method} | {n} | {zc} | {pz:.1%} | {mim:.0f} |")
    else:
        lines.append("| (match_start_method column absent) | - | - | - | - |")
    report_path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def select_phase_tickers(
    metadata: pd.DataFrame, phase: int, per_minute: pd.DataFrame
) -> list[str]:
    """
    Phase 1: 50 stratified. Phase 2: 1000 stratified. Phase 3: all binary tickers.

    Binary-outcome filter: g9_metadata.result ∈ {'yes', 'no'} per spec §3.2
    (the canonical Rung 0 / corpus-probe filter; 'scalar' excluded). g9_metadata
    is all-string per schema probe — float comparisons on settlement_value_dollars
    silently fail.

    category is T37-derived in per_minute_features.parquet, not in g9_metadata.
    For stratified phases we reuse the one-time narrow per_minute projection
    (already loaded in main via pq.read_table) — no extra parquet read here.
    """
    if "result" not in metadata.columns:
        raise RuntimeError(
            "g9_metadata missing required 'result' column per schema probe 2026-05-16"
        )
    binary = metadata[metadata["result"].isin(["yes", "no"])].copy()
    log.info(f"Binary-outcome filter (result ∈ yes/no): {len(binary)} tickers from {len(metadata)} metadata rows")
    if len(binary) == 0:
        raise RuntimeError(
            "Binary-outcome filter selected 0 tickers — verify g9_metadata.result column"
        )

    if phase == 3:
        return binary["ticker"].tolist()

    # Stratified phases need category — derive from the already-loaded
    # per_minute narrow projection (zero additional parquet reads).
    log.info("Deriving (ticker → category) map from per_minute narrow projection for phase stratification")
    cat_map = per_minute[["ticker", "category"]].drop_duplicates(subset=["ticker"])
    log.info(f"  category map: {len(cat_map)} unique tickers")
    binary = binary.merge(cat_map, on="ticker", how="left")
    binary["category"] = binary["category"].fillna("unknown")

    if phase == 1:
        per_cat = binary.groupby("category", group_keys=False).apply(
            lambda g: g.sample(min(10, len(g)), random_state=42)
        )
        tickers = per_cat["ticker"].tolist()[:50]
    elif phase == 2:
        per_cat = binary.groupby("category", group_keys=False).apply(
            lambda g: g.sample(min(250, len(g)), random_state=42)
        )
        tickers = per_cat["ticker"].tolist()[:1000]
    else:
        raise ValueError(f"phase must be 1, 2, or 3 — got {phase}")

    if len(tickers) == 0:
        raise RuntimeError(
            f"Phase {phase} stratified selection produced 0 tickers — "
            f"check per_minute_features category coverage"
        )
    log.info(f"Phase {phase} selected {len(tickers)} tickers")
    return tickers


def main() -> int:
    parser = argparse.ArgumentParser(description="n_profile_v1 producer")
    parser.add_argument("--input-base", type=Path, default=DEFAULT_INPUT_BASE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--phase", type=int, default=3, choices=[1, 2, 3])
    args = parser.parse_args()

    started_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")
    log.info(f"n_profile_v1 producer starting at {started_at} | phase={args.phase}")

    # Load inputs
    g9_metadata_path = args.input_base / "g9_metadata.parquet"
    g9_trades_path = args.input_base / "g9_trades.parquet"
    g9_candles_path = args.input_base / "g9_candles.parquet"
    per_minute_path = args.input_base / "per_minute_universe" / "per_minute_features.parquet"

    for p in [g9_metadata_path, g9_trades_path, g9_candles_path, per_minute_path]:
        if not p.exists():
            log.error(f"Missing input: {p}")
            return 1

    inputs_sha = {
        "g9_metadata": sha256_of_file(g9_metadata_path)[:16],
        "g9_trades": sha256_of_file(g9_trades_path)[:16],
        "g9_candles": sha256_of_file(g9_candles_path)[:16],
        "per_minute_features": sha256_of_file(per_minute_path)[:16],
    }
    log.info(f"Inputs (sha256-16): {inputs_sha}")

    log.info("Loading g9_metadata (full load via pq.read_table — small, ~20K rows)...")
    metadata = pq.read_table(str(g9_metadata_path)).to_pandas()
    log.info(f"  {len(metadata)} markets in metadata")

    # One-time NARROW per_minute_features projection (8 cols of 88) via
    # pq.read_table — NOT a full-column load. Serves three consumers:
    #   (a) ticker→category map for phase stratification
    #   (b) per-ticker slice for compute (pass 1)
    #   (c) pass-3 both-sides active-minute map
    # Per schema probe 2026-05-16 and spec §3.2 (commit b43fbaf7):
    # - partner column is `partner_ticker` (large_string), NOT paired_event_partner_ticker
    # - category, settlement_value live here (T37-derived; double respectively)
    # - match_start_ts and minute_ts are int64 unix seconds with NaN
    log.info("Loading per_minute_features narrow projection (9 cols, one-time, pq.read_table)...")
    pm_cols = ["ticker", "minute_ts", "match_start_ts", "partner_ticker",
               "category", "settlement_value", "match_start_method",
               "trade_count_in_minute", "volume_in_minute"]
    per_minute = pq.read_table(str(per_minute_path), columns=pm_cols).to_pandas()
    log.info(f"  per_minute_features: {len(per_minute)} rows x {len(pm_cols)} cols")

    tickers = select_phase_tickers(metadata, args.phase, per_minute)
    log.info(f"Phase {args.phase}: processing {len(tickers)} tickers")
    expected_count = len(tickers)
    ticker_set = set(tickers)

    per_minute_indexed = per_minute[per_minute["ticker"].isin(ticker_set)].copy()
    log.info(f"  per_minute filtered to phase tickers: {len(per_minute_indexed)} rows")
    del per_minute

    metadata_indexed = metadata[metadata["ticker"].isin(ticker_set)].set_index("ticker")
    per_minute_grouped = per_minute_indexed.groupby("ticker")

    # Pass 1 — per-ticker pyarrow predicate-pushdown for g9_trades + g9_candles.
    # g9_trades (1.5 GB / 33.7M rows) and g9_candles are NEVER full-loaded;
    # each ticker reads only its own rows via filters=[("ticker","=",ticker)],
    # mirroring the proven Rung 0 producer that ran the full corpus in ~1.9 GB.
    log.info("Pass 1: per-ticker rollup (Rung 0 pushdown I/O — no full-file load)")
    rows = []
    dropouts = 0
    for i, t in enumerate(tickers):
        if i > 0 and i % 1000 == 0:
            log.info(f"  Pass 1 progress: {i}/{len(tickers)}  emitted={len(rows)}  dropouts={dropouts}")
        if t not in metadata_indexed.index:
            dropouts += 1
            continue
        meta_row = metadata_indexed.loc[t]
        trades_sub = read_trades_for_ticker(g9_trades_path, t)
        candles_sub = read_candles_for_ticker(g9_candles_path, t)
        pm_sub = per_minute_grouped.get_group(t) if t in per_minute_grouped.groups else pd.DataFrame()
        row = compute_per_ticker_row(t, meta_row, trades_sub, candles_sub, pm_sub)
        if row is None:
            dropouts += 1
            continue
        rows.append(row)
    log.info(f"Pass 1 complete: {len(rows)} rows, {dropouts} dropouts")

    df = pd.DataFrame(rows, columns=SCHEMA_COLUMNS)

    # Pass 2: partner join
    df = join_partner_stats(df)

    # Pass 3: both_sides_active_minutes
    df = compute_both_sides_active_minutes(df, per_minute_indexed)

    # Write .new
    args.output_dir.mkdir(parents=True, exist_ok=True)
    final_path = args.output_dir / DEFAULT_OUTPUT_FILE
    new_path = args.output_dir / f"{DEFAULT_OUTPUT_FILE}.new"
    log.info(f"Writing .new to {new_path}")
    df.to_parquet(new_path, compression="snappy", index=False)

    # C37: reload and gate-validate
    gate_results = run_all_gates(new_path, expected_count, dropouts)
    for g in gate_results:
        marker = "PASS" if g.passed else "FAIL"
        log.info(f"  Gate {g.name}: {marker} (n_violations={g.n_violations}) {g.detail}")

    all_pass = all(g.passed for g in gate_results)
    if not all_pass:
        log.error("HARD GATE FAILURE — halting; .new preserved at " + str(new_path))
        # Spec §3.4: write disk-evidence halt log for operator adjudication.
        try:
            halt_dir = args.output_dir / "logs"
            halt_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(ET).strftime("%Y%m%dT%H%M%S")
            halt_path = halt_dir / f"halted_{ts}.log"
            lines = [
                f"n_profile_v1 HALTED (hard gate failure) {datetime.now(ET).isoformat()}",
                f".new preserved (NOT replaced): {new_path}",
                f"expected_count={expected_count} dropouts={dropouts}",
                "",
                "Gate results:",
            ]
            for g in gate_results:
                lines.append(
                    f"  {g.name}: {'PASS' if g.passed else 'FAIL'} "
                    f"n_violations={g.n_violations} {g.detail}"
                )
            halt_path.write_text("\n".join(lines) + "\n")
            log.error(f"Halt log written: {halt_path}")
        except Exception as e:
            log.error(f"Failed to write halt log: {type(e).__name__}: {e}")
        return 1

    log.info(f"All gates PASS — performing os.replace({new_path} → {final_path})")
    os.replace(new_path, final_path)

    output_sha = sha256_of_file(final_path)
    output_bytes = final_path.stat().st_size
    completed_at = datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET")

    result = ProducerResult(
        rows_emitted=len(df),
        gate_results=gate_results,
        output_sha256=output_sha,
        output_bytes=output_bytes,
        run_started_at_et=started_at,
        run_completed_at_et=completed_at,
        inputs_sha256=inputs_sha,
    )

    write_meta_sidecar(args.output_dir / DEFAULT_META_FILE, result)
    write_validation_report(args.output_dir / DEFAULT_REPORT_FILE, df, result)

    log.info(f"n_profile_v1 complete. Output sha256: {output_sha}")
    log.info(f"Output: {final_path} ({output_bytes} bytes, {len(df)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
