"""Cell-key classification helpers shared between Layer A and Layer B producers.

Extracted from build_layer_a_v1.py (T29 producer commit 1398c39) per LESSONS C27 +
ROADMAP T31b prep (Session 6 Phase 5-v). Both build_layer_a_v1.py and
build_layer_b_v1.py import from this module to ensure cell-key logic is
single-sourced - preventing drift between Layer A's aggregation and Layer B's
trajectory walk.

Constants:
- ENTRY_BANDS, SPREAD_BANDS, VOLUME_BANDS, REGIMES, CATEGORIES

Functions:
- categorize(ticker) -> category
- entry_band_idx(price) -> band index
- spread_band_name(bid, ask) -> 'tight' | 'medium' | 'wide'
- detect_match_start(timestamps, volumes) -> match_start_ts
- regime_for_moment(ts, match_start_ts, settlement_ts) -> 'premarket' | 'in_match' | 'settlement_zone'
- volume_intensity_for_market(volumes) -> 'low' | 'mid' | 'high'

DO NOT modify these in isolation. Any change here affects both Layer A and Layer B.
"""

import numpy as np


# ============================================================
# Constants
# ============================================================

ENTRY_BANDS = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
               (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
SPREAD_BANDS = [("tight", 0, 0.02), ("medium", 0.02, 0.05), ("wide", 0.05, 1.0)]
VOLUME_BANDS = ["low", "mid", "high"]
REGIMES = ["premarket", "in_match", "settlement_zone"]
CATEGORIES = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL", "OTHER"]


# ============================================================
# Cell-key classifiers
# ============================================================

def categorize(ticker):
    if ticker.startswith("KXATPMATCH"):
        return "ATP_MAIN"
    elif ticker.startswith("KXATPCHALLENGER") or ticker.startswith("KXATPCHALL"):
        return "ATP_CHALL"
    elif ticker.startswith("KXWTAMATCH"):
        return "WTA_MAIN"
    elif ticker.startswith("KXWTACHALL") or ticker.startswith("KXWTAITF"):
        return "WTA_CHALL"
    else:
        return "OTHER"


def entry_band_idx(price):
    if price is None or np.isnan(price):
        return None
    cents = price * 100
    for i, (lo, hi) in enumerate(ENTRY_BANDS):
        if lo <= cents < hi:
            return i
    if cents >= 90:
        return 9
    return None


def spread_band_name(bid, ask):
    if bid is None or ask is None or np.isnan(bid) or np.isnan(ask):
        return None
    sp = ask - bid
    if sp < 0:
        return None
    for name, lo, hi in SPREAD_BANDS:
        if lo <= sp < hi:
            return name
    return "wide"


def detect_match_start(timestamps, volumes):
    if len(timestamps) == 0:
        return None
    vol_arr = np.array([v if v is not None else 0 for v in volumes])
    n = len(vol_arr)
    for i in range(n):
        if vol_arr[i] > 0:
            window = vol_arr[i:i+5]
            if np.sum(window > 0) >= 3:
                return timestamps[i]
    return None


def regime_for_moment(ts, match_start_ts, settlement_ts):
    if settlement_ts is not None and ts >= (settlement_ts - 300):
        return "settlement_zone"
    if match_start_ts is None:
        return "premarket"
    if ts < match_start_ts:
        return "premarket"
    return "in_match"


def volume_intensity_for_market(volumes):
    non_null = sum(1 for v in volumes if v is not None and v > 0)
    if non_null < 5:
        return "low"
    elif non_null < 30:
        return "mid"
    else:
        return "high"
