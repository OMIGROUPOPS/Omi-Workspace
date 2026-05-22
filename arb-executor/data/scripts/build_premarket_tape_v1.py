#!/usr/bin/env python3
"""Build premarket_tape_v1: per-(ticker,minute) tape over T-4h to T-20m from per_minute_features.

Track 1 descriptive substrate (microstructure-only premarket dynamics). No FV anchor join.
Read-only against the foundation source; streams row-group-by-row-group per LESSONS C28
(VPS RAM ~1.9 GiB; never loads the full 9.3M-row foundation into memory).

Filter: regime == 'premarket' AND time_to_match_start_min in [20, 240].
Output: data/durable/per_minute_universe/probe/premarket_tape_v1_probe.parquet (promote after validation).
"""

import os, time, json, resource
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc

SRC = "data/durable/per_minute_universe/per_minute_features.parquet"
PROBE_OUT = "data/durable/per_minute_universe/probe/premarket_tape_v1_probe.parquet"

WIN_LO = 20.0    # T-20m
WIN_HI = 240.0   # T-4h


def main():
    t0 = time.time()
    pf = pq.ParquetFile(SRC)
    nrg = pf.metadata.num_row_groups
    print(f"source: {SRC}  rows={pf.metadata.num_rows}  row_groups={nrg}  cols={pf.metadata.num_columns}", flush=True)

    os.makedirs(os.path.dirname(PROBE_OUT), exist_ok=True)
    writer = None
    out_rows = 0
    src_rows_seen = 0
    all_tickers = set()
    kept_tickers = set()

    for rg in range(nrg):
        tbl = pf.read_row_group(rg)
        src_rows_seen += tbl.num_rows
        # track all source tickers (for skip accounting)
        all_tickers.update(pc.unique(tbl.column("ticker")).to_pylist())

        ttm = tbl.column("time_to_match_start_min")
        regime = tbl.column("regime")
        mask = pc.and_(
            pc.equal(regime, "premarket"),
            pc.and_(pc.greater_equal(ttm, WIN_LO), pc.less_equal(ttm, WIN_HI)),
        )
        mask = pc.fill_null(mask, False)
        sub = tbl.filter(mask)
        if sub.num_rows == 0:
            if (rg + 1) % 10 == 0:
                print(f"  rg {rg+1}/{nrg}  out_rows={out_rows}  rss={_rss_mb():.0f}MB", flush=True)
            continue

        sttm = sub.column("time_to_match_start_min")
        ttm_minus = pc.subtract(sttm, WIN_LO)                       # time_to_t20m_min (float64)
        pmi = pc.cast(pc.round(ttm_minus, ndigits=0), pa.int64())   # premarket_minute_index
        in_4h2h = pc.and_(pc.greater_equal(sttm, 120.0), pc.less_equal(sttm, 240.0))
        in_2h20m = pc.and_(pc.greater_equal(sttm, WIN_LO), pc.less_equal(sttm, 120.0))

        sub = sub.append_column("premarket_minute_index", pmi)
        sub = sub.append_column("time_to_t20m_min", pc.cast(ttm_minus, pa.float64()))
        sub = sub.append_column("in_t4h_t2h_subwindow", pc.cast(in_4h2h, pa.bool_()))
        sub = sub.append_column("in_t2h_t20m_subwindow", pc.cast(in_2h20m, pa.bool_()))

        kept_tickers.update(pc.unique(sub.column("ticker")).to_pylist())

        if writer is None:
            writer = pq.ParquetWriter(PROBE_OUT, sub.schema, compression="snappy")
        writer.write_table(sub)
        out_rows += sub.num_rows
        if (rg + 1) % 10 == 0:
            print(f"  rg {rg+1}/{nrg}  out_rows={out_rows}  kept_tickers={len(kept_tickers)}  rss={_rss_mb():.0f}MB", flush=True)

    if writer is not None:
        writer.close()

    tickers_processed = len(kept_tickers)
    tickers_total = len(all_tickers)
    tickers_skipped = tickers_total - tickers_processed
    sz = os.path.getsize(PROBE_OUT) if os.path.exists(PROBE_OUT) else 0
    elapsed = time.time() - t0
    peak = _rss_mb()
    print("=== SUMMARY ===", flush=True)
    print(f"  src_rows_seen={src_rows_seen}", flush=True)
    print(f"  tickers_total={tickers_total}", flush=True)
    print(f"  tickers_processed (>=1 premarket-window minute)={tickers_processed}", flush=True)
    print(f"  tickers_skipped_no_premarket_window={tickers_skipped}", flush=True)
    print(f"  out_rows={out_rows}", flush=True)
    print(f"  output_size_bytes={sz}  ({sz/1e9:.3f} GB)", flush=True)
    print(f"  wall_clock_seconds={elapsed:.1f}", flush=True)
    print(f"  peak_rss_mb={peak:.0f}", flush=True)
    print("DONE_MARKER", flush=True)


def _rss_mb():
    # ru_maxrss is in KB on Linux
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


if __name__ == "__main__":
    main()
