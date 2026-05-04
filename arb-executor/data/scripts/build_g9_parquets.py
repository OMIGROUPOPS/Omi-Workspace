#!/usr/bin/env python3
"""
build_g9_parquets.py

Consolidate G9 dataset (60K small CSVs + JSONs) into 3 parquets for fast Layer A access.

Inputs:
- /root/Omi-Workspace/arb-executor/data/historical_pull/candlesticks/*.csv (19,687 files)
- /root/Omi-Workspace/arb-executor/data/historical_pull/trades/*.csv (20,018 files)
- /root/Omi-Workspace/arb-executor/data/historical_pull/market_metadata/*.json (20,110 files)

Outputs:
- /root/Omi-Workspace/arb-executor/data/durable/g9_candles.parquet
- /root/Omi-Workspace/arb-executor/data/durable/g9_trades.parquet
- /root/Omi-Workspace/arb-executor/data/durable/g9_metadata.parquet

Schema normalization (per LESSONS F29):
- 2025-era markets use bare names (price_close, yes_bid_close, yes_ask_close, etc.)
- 2026-era markets use _dollars-suffixed names (price_close_dollars, yes_bid_close_dollars, etc.)
- Normalized to bare names as canonical.

Memory strategy: streaming append in chunks of N markets to avoid OOM on 1.9GB VPS.
Writes parquet incrementally via pyarrow ParquetWriter.

Per ROADMAP T17, gated by T18 (candles-semantics confirmed G18: candles ARE BBO snapshots).
"""

import os
import sys
import csv
import json
import glob
import time
from datetime import datetime, timezone
import pyarrow as pa
import pyarrow.parquet as pq

HP_DIR = "/root/Omi-Workspace/arb-executor/data/historical_pull"
OUT_DIR = "/root/Omi-Workspace/arb-executor/data/durable"
LOG_PATH = "/root/Omi-Workspace/arb-executor/data/durable/g9_parquet_build.log"

CHUNK_SIZE_MARKETS = 500  # markets per chunk for streaming write

CANDLE_COLS_CANONICAL = [
    "ticker",
    "end_period_ts", "open_interest_fp",
    "price_close", "price_high", "price_low", "price_mean", "price_open", "price_previous",
    "volume_fp",
    "yes_ask_close", "yes_ask_high", "yes_ask_low", "yes_ask_open",
    "yes_bid_close", "yes_bid_high", "yes_bid_low", "yes_bid_open",
]
TRADE_COLS_CANONICAL = [
    "count_fp", "created_time", "no_price_dollars", "taker_side",
    "ticker", "trade_id", "yes_price_dollars",
]


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def normalize_candle_row(row, ticker):
    out = {"ticker": ticker}
    for col in CANDLE_COLS_CANONICAL[1:]:
        val = row.get(col, row.get(col + "_dollars"))
        out[col] = val
    return out


def normalize_trade_row(row):
    return {col: row.get(col) for col in TRADE_COLS_CANONICAL}


def parse_floatish(s):
    if s is None or s == "":
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def parse_intish(s):
    if s is None or s == "":
        return None
    try:
        return int(s)
    except (TypeError, ValueError):
        try:
            return int(float(s))
        except (TypeError, ValueError):
            return None


def candle_pyarrow_schema():
    return pa.schema([
        ("ticker", pa.string()),
        ("end_period_ts", pa.int64()),
        ("open_interest_fp", pa.int64()),
        ("price_close", pa.float64()),
        ("price_high", pa.float64()),
        ("price_low", pa.float64()),
        ("price_mean", pa.float64()),
        ("price_open", pa.float64()),
        ("price_previous", pa.float64()),
        ("volume_fp", pa.int64()),
        ("yes_ask_close", pa.float64()),
        ("yes_ask_high", pa.float64()),
        ("yes_ask_low", pa.float64()),
        ("yes_ask_open", pa.float64()),
        ("yes_bid_close", pa.float64()),
        ("yes_bid_high", pa.float64()),
        ("yes_bid_low", pa.float64()),
        ("yes_bid_open", pa.float64()),
    ])


def trade_pyarrow_schema():
    return pa.schema([
        ("count_fp", pa.int64()),
        ("created_time", pa.string()),
        ("no_price_dollars", pa.float64()),
        ("taker_side", pa.string()),
        ("ticker", pa.string()),
        ("trade_id", pa.string()),
        ("yes_price_dollars", pa.float64()),
    ])


def build_candles():
    log("=== Starting candles parquet build ===")
    candle_files = sorted(glob.glob(os.path.join(HP_DIR, "candlesticks", "*.csv")))
    n_files = len(candle_files)
    log(f"Found {n_files} candle files")

    out_path = os.path.join(OUT_DIR, "g9_candles.parquet")
    schema = candle_pyarrow_schema()
    writer = pq.ParquetWriter(out_path, schema, compression="snappy")

    era_2025_count = 0
    era_2026_count = 0
    rows_written = 0
    files_processed = 0
    files_failed = 0
    start = time.time()

    chunk_buffer = {col: [] for col in CANDLE_COLS_CANONICAL}

    for fi, fpath in enumerate(candle_files):
        ticker = os.path.basename(fpath).replace(".csv", "")
        try:
            with open(fpath) as f:
                reader = csv.DictReader(f)
                if "price_close_dollars" in reader.fieldnames:
                    era_2026_count += 1
                else:
                    era_2025_count += 1
                for row in reader:
                    norm = normalize_candle_row(row, ticker)
                    chunk_buffer["ticker"].append(norm["ticker"])
                    chunk_buffer["end_period_ts"].append(parse_intish(norm["end_period_ts"]))
                    chunk_buffer["open_interest_fp"].append(parse_intish(norm["open_interest_fp"]))
                    for col in ["price_close", "price_high", "price_low", "price_mean", "price_open", "price_previous"]:
                        chunk_buffer[col].append(parse_floatish(norm[col]))
                    chunk_buffer["volume_fp"].append(parse_intish(norm["volume_fp"]))
                    for col in ["yes_ask_close", "yes_ask_high", "yes_ask_low", "yes_ask_open",
                                "yes_bid_close", "yes_bid_high", "yes_bid_low", "yes_bid_open"]:
                        chunk_buffer[col].append(parse_floatish(norm[col]))
                    rows_written += 1
            files_processed += 1
        except Exception as e:
            files_failed += 1
            log(f"FAILED candle file {fpath}: {e}")

        if (fi + 1) % CHUNK_SIZE_MARKETS == 0 or (fi + 1) == n_files:
            try:
                tbl = pa.table(chunk_buffer, schema=schema)
                writer.write_table(tbl)
                chunk_buffer = {col: [] for col in CANDLE_COLS_CANONICAL}
                elapsed = time.time() - start
                rate = (fi + 1) / elapsed if elapsed > 0 else 0
                eta_sec = (n_files - fi - 1) / rate if rate > 0 else 0
                log(f"Candles: {fi+1}/{n_files} markets, {rows_written:,} rows, "
                    f"era25={era_2025_count}, era26={era_2026_count}, "
                    f"failed={files_failed}, elapsed={elapsed:.0f}s, ETA={eta_sec:.0f}s")
            except Exception as e:
                log(f"FAILED to write chunk at file {fi+1}: {e}")
                raise

    writer.close()
    log(f"=== Candles done. {rows_written:,} rows, era25={era_2025_count}, era26={era_2026_count}, failed={files_failed} ===")
    log(f"Output size: {os.path.getsize(out_path) / 1024 / 1024:.1f} MB")
    return rows_written


def build_trades():
    log("=== Starting trades parquet build ===")
    trade_files = sorted(glob.glob(os.path.join(HP_DIR, "trades", "*.csv")))
    n_files = len(trade_files)
    log(f"Found {n_files} trade files")

    out_path = os.path.join(OUT_DIR, "g9_trades.parquet")
    schema = trade_pyarrow_schema()
    writer = pq.ParquetWriter(out_path, schema, compression="snappy")

    rows_written = 0
    files_processed = 0
    files_failed = 0
    start = time.time()

    chunk_buffer = {col: [] for col in TRADE_COLS_CANONICAL}

    for fi, fpath in enumerate(trade_files):
        try:
            with open(fpath) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    chunk_buffer["count_fp"].append(parse_intish(row.get("count_fp")))
                    chunk_buffer["created_time"].append(row.get("created_time"))
                    chunk_buffer["no_price_dollars"].append(parse_floatish(row.get("no_price_dollars")))
                    chunk_buffer["taker_side"].append(row.get("taker_side"))
                    chunk_buffer["ticker"].append(row.get("ticker"))
                    chunk_buffer["trade_id"].append(row.get("trade_id"))
                    chunk_buffer["yes_price_dollars"].append(parse_floatish(row.get("yes_price_dollars")))
                    rows_written += 1
            files_processed += 1
        except Exception as e:
            files_failed += 1
            log(f"FAILED trade file {fpath}: {e}")

        if (fi + 1) % CHUNK_SIZE_MARKETS == 0 or (fi + 1) == n_files:
            try:
                tbl = pa.table(chunk_buffer, schema=schema)
                writer.write_table(tbl)
                chunk_buffer = {col: [] for col in TRADE_COLS_CANONICAL}
                elapsed = time.time() - start
                rate = (fi + 1) / elapsed if elapsed > 0 else 0
                eta_sec = (n_files - fi - 1) / rate if rate > 0 else 0
                log(f"Trades: {fi+1}/{n_files} markets, {rows_written:,} rows, "
                    f"failed={files_failed}, elapsed={elapsed:.0f}s, ETA={eta_sec:.0f}s")
            except Exception as e:
                log(f"FAILED to write trade chunk at file {fi+1}: {e}")
                raise

    writer.close()
    log(f"=== Trades done. {rows_written:,} rows, failed={files_failed} ===")
    log(f"Output size: {os.path.getsize(out_path) / 1024 / 1024:.1f} MB")
    return rows_written


def build_metadata():
    log("=== Starting metadata parquet build ===")
    meta_files = sorted(glob.glob(os.path.join(HP_DIR, "market_metadata", "*.json")))
    n_files = len(meta_files)
    log(f"Found {n_files} metadata files")

    rows = []
    files_failed = 0
    start = time.time()
    all_keys = set()

    for fi, fpath in enumerate(meta_files):
        try:
            with open(fpath) as f:
                d = json.load(f)
            if isinstance(d, dict):
                rows.append(d)
                all_keys.update(d.keys())
        except Exception as e:
            files_failed += 1
            log(f"FAILED metadata file {fpath}: {e}")
        if (fi + 1) % 5000 == 0:
            log(f"Metadata pass 1: {fi+1}/{n_files} files read")

    log(f"Metadata: {len(rows)} rows collected, {len(all_keys)} unique keys, failed={files_failed}")

    for r in rows:
        for k in all_keys:
            if k not in r:
                r[k] = None
            elif isinstance(r[k], (dict, list)):
                r[k] = json.dumps(r[k])

    out_path = os.path.join(OUT_DIR, "g9_metadata.parquet")
    tbl = pa.Table.from_pylist(rows)
    pq.write_table(tbl, out_path, compression="snappy")
    log(f"=== Metadata done. {len(rows)} rows, {len(all_keys)} columns ===")
    log(f"Output size: {os.path.getsize(out_path) / 1024 / 1024:.1f} MB")
    return len(rows)


def main():
    log("=" * 60)
    log("build_g9_parquets.py STARTED")
    log("=" * 60)
    overall_start = time.time()

    n_candles = build_candles()
    n_trades = build_trades()
    n_meta = build_metadata()

    elapsed = time.time() - overall_start
    log("=" * 60)
    log(f"ALL DONE. candles={n_candles:,} rows, trades={n_trades:,} rows, metadata={n_meta:,} rows")
    log(f"Total elapsed: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    log("=" * 60)


if __name__ == "__main__":
    main()
