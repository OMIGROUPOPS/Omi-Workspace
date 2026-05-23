#!/usr/bin/env python3
"""
Archive book_prices from tennis.db to durable parquet under data/durable/fv_history/.

Modes:
  --mode initial:     full snapshot of current book_prices content (run once)
  --mode incremental: append rows newer than the latest polled_at already archived (daily cron)

Output layout:
  data/durable/fv_history/by_month/YYYY-MM.parquet  (partitioned monthly, append-only)
  data/durable/fv_history/state.json  (archive state: last_archived_ts, total_rows, runs)

Single concern: archive, no transformation. Columns preserved exactly as in book_prices
(TEXT -> string, REAL -> float64; values byte-faithful).

MEMORY-SAFE WRITE PATH (deviation from the originally-drafted producer, documented in
run_summary_initial.json and MANIFEST): the source has a ~10M-row month (2026-05). Buffering
a whole month in a Python list before flushing — or read-concat-rewrite appends — would exceed
the VPS RAM (~1.47 GB free) and OOM. Instead we stream the SQLite cursor in bounded batches and
write straight through a per-month pyarrow ParquetWriter (C28 incremental-writer discipline).
For incremental appends to an existing month file, we stream-merge: copy the existing file's
row groups one at a time into a temp writer, append the new delta, then atomically rename.
Peak memory is bounded by one batch + one row group, not by month size.
"""

import argparse
import json
import os
import resource
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # data/scripts/ -> arb-executor/
DB_PATH = REPO_ROOT / "tennis.db"
ARCHIVE_DIR = REPO_ROOT / "data" / "durable" / "fv_history"
BY_MONTH_DIR = ARCHIVE_DIR / "by_month"
STATE_PATH = ARCHIVE_DIR / "state.json"

SCHEMA_COLS = [
    "event_ticker", "book_key", "player1_name", "player2_name",
    "book_p1_fv_cents", "book_p2_fv_cents",
    "raw_odds_p1", "raw_odds_p2", "vig_pct",
    "sport_key", "commence_time", "polled_at",
]

# Explicit arrow schema mirroring book_prices column types (TEXT->string, REAL->float64).
# Pinned so every batch/writer shares an identical schema (no per-batch type inference drift,
# e.g. an all-null REAL batch inferring null type).
SCHEMA = pa.schema([
    ("event_ticker", pa.string()),
    ("book_key", pa.string()),
    ("player1_name", pa.string()),
    ("player2_name", pa.string()),
    ("book_p1_fv_cents", pa.float64()),
    ("book_p2_fv_cents", pa.float64()),
    ("raw_odds_p1", pa.float64()),
    ("raw_odds_p2", pa.float64()),
    ("vig_pct", pa.float64()),
    ("sport_key", pa.string()),
    ("commence_time", pa.string()),
    ("polled_at", pa.string()),
])

POLLED_IDX = SCHEMA_COLS.index("polled_at")
BATCH_SIZE = 100_000


def _rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def load_state():
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"last_archived_ts": None, "total_rows_archived": 0, "runs": []}


def save_state(state):
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def fetch_rows(conn, since_ts=None, batch_size=BATCH_SIZE):
    """Stream rows from book_prices, optionally polled_at > since_ts. Ordered by polled_at."""
    cols_sql = ", ".join(SCHEMA_COLS)
    if since_ts is None:
        query = f"SELECT {cols_sql} FROM book_prices ORDER BY polled_at"
        params = ()
    else:
        query = f"SELECT {cols_sql} FROM book_prices WHERE polled_at > ? ORDER BY polled_at"
        params = (since_ts,)
    cursor = conn.execute(query, params)
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch


def rows_to_table(rows):
    """list-of-tuples -> pyarrow Table with the pinned schema (column order preserved)."""
    arrays = [pa.array([row[i] for row in rows], type=SCHEMA.field(i).type)
              for i in range(len(SCHEMA_COLS))]
    return pa.Table.from_arrays(arrays, schema=SCHEMA)


def archive_stream(conn, since_ts, by_month_dir):
    """Stream rows to per-month parquet via incremental ParquetWriter. Memory-safe.

    For a month whose file already exists (incremental append), the existing row groups are
    streamed into the temp writer first (one group at a time), then the new delta appended,
    then atomic-rename. Peak RAM bounded by one batch + one row group.
    """
    by_month_dir.mkdir(parents=True, exist_ok=True)
    writers, temps, finals, rows_per_month = {}, {}, {}, {}
    max_written = None  # high-water-mark = max polled_at actually archived

    def get_writer(month):
        if month in writers:
            return writers[month]
        final = by_month_dir / f"{month}.parquet"
        tmp = by_month_dir / f"{month}.parquet.building"
        w = pq.ParquetWriter(tmp, SCHEMA, compression="snappy")
        if final.exists():
            pf = pq.ParquetFile(final)
            for i in range(pf.metadata.num_row_groups):
                w.write_table(pf.read_row_group(i).cast(SCHEMA))
        writers[month] = w
        temps[month] = tmp
        finals[month] = final
        rows_per_month[month] = 0
        return w

    for batch in fetch_rows(conn, since_ts):
        bym = {}
        for row in batch:
            bym.setdefault(row[POLLED_IDX][:7], []).append(row)
        for month, rws in bym.items():
            get_writer(month).write_table(rows_to_table(rws))
            rows_per_month[month] += len(rws)
        # query is ORDER BY polled_at ascending -> last row of the batch is the running max
        bmax = batch[-1][POLLED_IDX]
        if max_written is None or bmax > max_written:
            max_written = bmax

    for month, w in writers.items():
        w.close()
        os.replace(temps[month], finals[month])

    total = sum(rows_per_month.values())
    return total, rows_per_month, max_written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["initial", "incremental"], required=True)
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} not found", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    if args.mode == "initial" and state["last_archived_ts"] is not None:
        print(f"ERROR: --mode initial but state shows prior archive at {state['last_archived_ts']}. Use --mode incremental.", file=sys.stderr)
        sys.exit(1)
    if args.mode == "incremental" and state["last_archived_ts"] is None:
        print("ERROR: --mode incremental but no prior archive exists. Use --mode initial first.", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    since_ts = state["last_archived_ts"] if args.mode == "incremental" else None

    run_start = datetime.now(timezone.utc).isoformat()
    rows_written, rows_per_month, archived_max = archive_stream(conn, since_ts, BY_MONTH_DIR)

    # db_max is for reporting only. The high-water-mark MUST be the max polled_at actually
    # archived (archived_max), NOT a separate SELECT MAX(): on a live DB the streamed SELECT
    # sees a consistent snapshot as of query-start, while a later MAX() races ahead, which would
    # leave an un-archivable gap (incremental uses polled_at > last_archived_ts).
    db_max = conn.execute("SELECT MAX(polled_at) FROM book_prices").fetchone()[0]
    conn.close()

    # if nothing was written (empty incremental delta) keep the previous high-water-mark
    new_max = archived_max if archived_max is not None else state["last_archived_ts"]
    state["last_archived_ts"] = new_max
    state["total_rows_archived"] += rows_written
    state["runs"].append({
        "ts": run_start,
        "mode": args.mode,
        "rows_written": rows_written,
        "rows_per_month": rows_per_month,
        "new_last_archived_ts": new_max,
        "db_max_polled_at_at_close": db_max,
        "wall_clock_seconds": round(time.time() - t0, 1),
        "peak_rss_mb": round(_rss_mb(), 1),
    })
    save_state(state)

    print(f"OK: mode={args.mode}, rows_written={rows_written}, rows_per_month={rows_per_month}, "
          f"new_last_archived_ts={new_max}, db_max_at_close={db_max}, "
          f"total_archived={state['total_rows_archived']}, "
          f"wall_clock_s={time.time()-t0:.1f}, peak_rss_mb={_rss_mb():.0f}")


if __name__ == "__main__":
    main()
