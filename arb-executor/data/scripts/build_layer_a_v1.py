#!/usr/bin/env python3
"""
build_layer_a_v1.py — Layer A v1 visual + tabular producer

Per LESSONS C27 (analytical-foundation discipline). Foundation: T28 commit ea84e74.
Per LESSONS B16 (Layer A separation): pure market-property measurement, no exit
logic, no fees, no fills, no P&L.

REFACTOR (T29 pre-launch, per LESSONS C28): stream-aggregate moments into per-cell
running stats with bounded reservoir for percentile estimation. Eliminates the
O(total_moments) cell_moments dict accumulation that risked OOM at 5M+ moments.

Inputs:
- arb-executor/data/durable/g9_candles.parquet (T28 verified)
- arb-executor/data/durable/g9_metadata.parquet (T28 verified)

Outputs:
- arb-executor/data/durable/layer_a_v1/cell_stats.parquet
- arb-executor/data/durable/layer_a_v1/visual_<CATEGORY>_<REGIME>.png (12 PNGs)
- arb-executor/data/durable/layer_a_v1/sample_manifest.json
- arb-executor/data/durable/layer_a_v1/build_layer_a_v1.log

Cell schema: (regime, entry_band, spread_band, volume_intensity, category)
Forward-horizons: 5, 15, 30, 60 min
"""

import os
import sys
import json
import time
import random
from collections import defaultdict
from datetime import datetime
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DUR_DIR = "/root/Omi-Workspace/arb-executor/data/durable"
OUT_DIR = os.path.join(DUR_DIR, "layer_a_v1")
os.makedirs(OUT_DIR, exist_ok=True)
LOG_PATH = os.path.join(OUT_DIR, "build_layer_a_v1.log")

CANDLES_PATH = os.path.join(DUR_DIR, "g9_candles.parquet")
META_PATH = os.path.join(DUR_DIR, "g9_metadata.parquet")

ENTRY_BANDS = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50),
               (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
SPREAD_BANDS = [("tight", 0, 0.02), ("medium", 0.02, 0.05), ("wide", 0.05, 1.0)]
VOLUME_BANDS = ["low", "mid", "high"]
REGIMES = ["premarket", "in_match", "settlement_zone"]
CATEGORIES = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL", "OTHER"]

FORWARD_HORIZONS = [5, 15, 30, 60]
SAMPLE_PER_CELL = 30
MIN_MARKETS_FOR_VISUAL = 5
RESERVOIR_CAP = 10000

random.seed(42)


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


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


class CellAggregator:
    """Stream-aggregator: holds running count + reservoir of recent samples per cell.
    Memory: O(RESERVOIR_CAP * 8 bytes * n_horizons * 2 [bounce+dd]) per cell.
    With ~360 cells and 4 horizons: 360 * 4 * 2 * 10000 * 8 = 230 MB worst case."""

    def __init__(self):
        self.markets = set()
        self.n_moments = 0
        self.reservoirs = {
            f"bounce_{h}min": [] for h in FORWARD_HORIZONS
        }
        self.reservoirs.update({
            f"drawdown_{h}min": [] for h in FORWARD_HORIZONS
        })

    def add_moment(self, ticker, moment):
        self.markets.add(ticker)
        self.n_moments += 1
        for h in FORWARD_HORIZONS:
            for prefix in ["bounce", "drawdown"]:
                k = f"{prefix}_{h}min"
                v = moment.get(k)
                if v is None:
                    continue
                res = self.reservoirs[k]
                if len(res) < RESERVOIR_CAP:
                    res.append(v)
                else:
                    j = random.randint(0, self.n_moments - 1)
                    if j < RESERVOIR_CAP:
                        res[j] = v

    def to_stats_row(self, regime, eb, sb, vi, cat):
        row = {
            "regime": regime,
            "entry_band_lo": ENTRY_BANDS[eb][0],
            "entry_band_hi": ENTRY_BANDS[eb][1],
            "spread_band": sb,
            "volume_intensity": vi,
            "category": cat,
            "n_moments": self.n_moments,
            "n_markets": len(self.markets),
        }
        for h in FORWARD_HORIZONS:
            for prefix in ["bounce", "drawdown"]:
                k = f"{prefix}_{h}min"
                arr = np.array(self.reservoirs[k]) if self.reservoirs[k] else np.array([])
                if len(arr) > 0:
                    row[f"{k}_n"] = len(arr)
                    row[f"{k}_mean"] = float(np.mean(arr))
                    row[f"{k}_median"] = float(np.median(arr))
                    row[f"{k}_p25"] = float(np.percentile(arr, 25))
                    row[f"{k}_p75"] = float(np.percentile(arr, 75))
                    row[f"{k}_p95"] = float(np.percentile(arr, 95))
                    if prefix == "bounce":
                        for thresh_c in [1, 2, 5, 10, 20]:
                            thresh = thresh_c / 100
                            row[f"{k}_frac_ge_{thresh_c}c"] = float(np.mean(arr >= thresh))
                else:
                    row[f"{k}_n"] = 0
                    for stat in ["mean", "median", "p25", "p75", "p95"]:
                        row[f"{k}_{stat}"] = None
                    if prefix == "bounce":
                        for thresh_c in [1, 2, 5, 10, 20]:
                            row[f"{k}_frac_ge_{thresh_c}c"] = None
        return row


def process_market(rows, settlement_ts):
    if len(rows) < 5:
        return None

    timestamps = np.array([r["end_period_ts"] for r in rows])
    yes_bid = np.array([r["yes_bid_close"] if r["yes_bid_close"] is not None else np.nan for r in rows])
    yes_ask = np.array([r["yes_ask_close"] if r["yes_ask_close"] is not None else np.nan for r in rows])
    volumes = [r["volume_fp"] for r in rows]

    ticker = rows[0]["ticker"]
    category = categorize(ticker)
    match_start = detect_match_start(timestamps, volumes)
    vol_int = volume_intensity_for_market(volumes)

    moments = []
    n = len(timestamps)
    for i in range(n - 1):
        ts = timestamps[i]
        bid_t = yes_bid[i]
        ask_t = yes_ask[i]
        if np.isnan(bid_t) or np.isnan(ask_t):
            continue
        if bid_t == 0 or ask_t >= 1.0:
            continue
        if ask_t - bid_t > 0.30:
            continue

        eb = entry_band_idx(ask_t)
        sb = spread_band_name(bid_t, ask_t)
        if eb is None or sb is None:
            continue

        regime = regime_for_moment(ts, match_start, settlement_ts)

        moment = {
            "regime": regime,
            "entry_band": eb,
            "spread_band": sb,
            "volume_intensity": vol_int,
            "category": category,
        }
        for h in FORWARD_HORIZONS:
            window_end = i + 1 + h
            if window_end > n:
                window_end = n
            if i + 1 >= window_end:
                continue
            window_ask = yes_ask[i+1:window_end]
            valid = ~np.isnan(window_ask)
            if not valid.any():
                continue
            window_ask_valid = window_ask[valid]
            moment[f"bounce_{h}min"] = float(np.max(window_ask_valid) - ask_t)
            moment[f"drawdown_{h}min"] = float(ask_t - np.min(window_ask_valid))

        moments.append(moment)

    return moments, ticker, match_start, timestamps, yes_ask


def main():
    log("=" * 60)
    log("build_layer_a_v1.py STARTED (refactored: stream-aggregate)")
    log("=" * 60)
    overall_start = time.time()

    log("Loading metadata...")
    meta_tbl = pq.read_table(META_PATH, columns=["ticker", "settlement_ts"])
    meta_tickers = meta_tbl["ticker"].to_pylist()
    meta_settle = meta_tbl["settlement_ts"].to_pylist()
    settle_map = {}
    for t, s in zip(meta_tickers, meta_settle):
        if t is None:
            continue
        ts_int = None
        if s is not None and s != "":
            try:
                from datetime import datetime as _dt
                ts_str = s.replace("Z", "+00:00") if s.endswith("Z") else s
                ts_int = int(_dt.fromisoformat(ts_str).timestamp())
            except Exception:
                ts_int = None
        settle_map[t] = ts_int
    log(f"Loaded {len(settle_map)} metadata rows")

    log("Streaming candles parquet...")
    pf = pq.ParquetFile(CANDLES_PATH)
    log(f"Candles parquet: {pf.num_row_groups} row groups, {pf.metadata.num_rows:,} rows total")

    cell_aggs = defaultdict(CellAggregator)
    cell_ticker_pool = defaultdict(list)
    market_trajectories = {}

    current_ticker = None
    current_rows = []
    markets_processed = 0
    moments_total = 0
    last_log_time = time.time()

    def flush_market(ticker, rows):
        nonlocal markets_processed, moments_total
        if ticker is None or not rows:
            return
        settle_ts = settle_map.get(ticker)
        result = process_market(rows, settle_ts)
        if result is None:
            return
        moments, _t, match_start, timestamps, yes_ask = result
        if not moments:
            return
        market_trajectories[ticker] = (timestamps.astype(np.int64),
                                       yes_ask.astype(np.float32),
                                       match_start)
        for m in moments:
            key = (m["regime"], m["entry_band"], m["spread_band"],
                   m["volume_intensity"], m["category"])
            cell_aggs[key].add_moment(ticker, m)
            cell_ticker_pool[key].append(ticker)
            moments_total += 1
        markets_processed += 1

    for rg_idx in range(pf.num_row_groups):
        batch = pf.read_row_group(rg_idx, columns=[
            "ticker", "end_period_ts", "yes_bid_close", "yes_ask_close", "volume_fp"
        ])
        tickers_b = batch["ticker"].to_pylist()
        ts_b = batch["end_period_ts"].to_pylist()
        bid_b = batch["yes_bid_close"].to_pylist()
        ask_b = batch["yes_ask_close"].to_pylist()
        vol_b = batch["volume_fp"].to_pylist()
        for i in range(len(tickers_b)):
            t = tickers_b[i]
            if t != current_ticker:
                flush_market(current_ticker, current_rows)
                current_ticker = t
                current_rows = []
            current_rows.append({
                "ticker": t,
                "end_period_ts": ts_b[i],
                "yes_bid_close": bid_b[i],
                "yes_ask_close": ask_b[i],
                "volume_fp": vol_b[i],
            })

        now = time.time()
        if now - last_log_time > 30:
            elapsed = now - overall_start
            rate = markets_processed / elapsed if elapsed > 0 else 0
            log(f"  RG {rg_idx+1}/{pf.num_row_groups}, markets={markets_processed:,}, "
                f"moments={moments_total:,}, cells_populated={len(cell_aggs):,}, "
                f"elapsed={elapsed:.0f}s, rate={rate:.0f} markets/s")
            last_log_time = now

    flush_market(current_ticker, current_rows)
    log(f"Streaming done. Markets: {markets_processed:,}, moments: {moments_total:,}, "
        f"cells: {len(cell_aggs):,}, trajectories cached: {len(market_trajectories):,}")

    log("Building cell_stats.parquet from aggregators...")
    cell_stats_rows = []
    for (regime, eb, sb, vi, cat), agg in cell_aggs.items():
        row = agg.to_stats_row(regime, eb, sb, vi, cat)
        cell_stats_rows.append(row)
    cell_stats_path = os.path.join(OUT_DIR, "cell_stats.parquet")
    cell_stats_tbl = pa.Table.from_pylist(cell_stats_rows)
    pq.write_table(cell_stats_tbl, cell_stats_path, compression="snappy")
    log(f"cell_stats.parquet written: {len(cell_stats_rows)} rows, "
        f"{os.path.getsize(cell_stats_path)/1024:.1f} KB")

    log("Sampling tickers per cell...")
    sample_manifest = {}
    cell_samples = {}
    for key, tickers in cell_ticker_pool.items():
        unique_tickers = sorted(set(tickers))
        sampled = random.sample(unique_tickers, min(SAMPLE_PER_CELL, len(unique_tickers)))
        cell_samples[key] = sampled
        sample_manifest["__".join(str(x) for x in key)] = {
            "n_total": len(unique_tickers),
            "n_sampled": len(sampled),
            "tickers": sampled,
        }
    with open(os.path.join(OUT_DIR, "sample_manifest.json"), "w") as f:
        json.dump(sample_manifest, f, indent=2)
    log(f"sample_manifest.json written: {len(sample_manifest)} cells")

    log("Building per-category-per-regime visual grids...")
    for cat in CATEGORIES:
        for regime in REGIMES:
            log(f"  Visual: {cat} / {regime}")
            fig, axes = plt.subplots(
                len(ENTRY_BANDS), len(SPREAD_BANDS),
                figsize=(15, 30),
                squeeze=False,
            )
            fig.suptitle(f"Layer A v1 — {cat} — regime: {regime}", fontsize=16, y=0.995)
            for eb_idx, (lo, hi) in enumerate(ENTRY_BANDS):
                for sb_idx, (sb_name, _, _) in enumerate(SPREAD_BANDS):
                    ax = axes[eb_idx][sb_idx]
                    pooled_tickers = []
                    pooled_n = 0
                    for vi in VOLUME_BANDS:
                        key = (regime, eb_idx, sb_name, vi, cat)
                        if key in cell_samples:
                            pooled_tickers.extend(cell_samples[key])
                        if key in cell_aggs:
                            pooled_n += cell_aggs[key].n_moments
                    pooled_tickers = list(dict.fromkeys(pooled_tickers))[:SAMPLE_PER_CELL]

                    if len(pooled_tickers) < MIN_MARKETS_FOR_VISUAL:
                        ax.text(0.5, 0.5, f"n={len(pooled_tickers)}\ninsufficient",
                                ha="center", va="center", transform=ax.transAxes,
                                color="gray", fontsize=8)
                        ax.set_xticks([])
                        ax.set_yticks([])
                    else:
                        for tk in pooled_tickers:
                            traj = market_trajectories.get(tk)
                            if traj is None:
                                continue
                            ts_arr, ask_arr, ms = traj
                            t0 = ts_arr[0]
                            mins = (ts_arr - t0) / 60.0
                            ax.plot(mins, ask_arr, color="steelblue", alpha=0.15, linewidth=0.5)
                            if ms is not None:
                                ms_min = (ms - t0) / 60.0
                                ax.axvline(ms_min, color="orange", alpha=0.2, linewidth=0.3)
                        ax.set_ylim(0, 1.0)
                        ax.set_title(f"{lo}-{hi}c, {sb_name}, n={len(pooled_tickers)}, "
                                    f"moments={pooled_n:,}",
                                    fontsize=8)
                        ax.tick_params(labelsize=7)
                        ax.grid(alpha=0.2)
                    if sb_idx == 0:
                        ax.set_ylabel(f"{lo}-{hi}c", fontsize=8)
                    if eb_idx == len(ENTRY_BANDS) - 1:
                        ax.set_xlabel(f"min from open\n({sb_name})", fontsize=8)

            plt.tight_layout(rect=[0, 0, 1, 0.99])
            png_path = os.path.join(OUT_DIR, f"visual_{cat}_{regime}.png")
            plt.savefig(png_path, dpi=80, bbox_inches="tight")
            plt.close(fig)
            log(f"    Saved {png_path} ({os.path.getsize(png_path)/1024:.0f} KB)")

    elapsed = time.time() - overall_start
    log("=" * 60)
    log(f"DONE. Markets={markets_processed:,}, moments={moments_total:,}, cells={len(cell_aggs):,}")
    log(f"Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    log("=" * 60)


if __name__ == "__main__":
    main()
