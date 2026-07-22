#!/usr/bin/env python3
"""Build a count/schema-only census of canonical Window-1 context sources."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any


DATE_RE = re.compile(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}")
SQLITE_TABLES = (
    "historical_events", "matches", "kalshi_price_snapshots",
    "fills", "orders_ledger",
)
LIVE_LARGE_TABLES = {"kalshi_price_snapshots"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sqlite_census(path: Path, logical_name: str, with_hash: bool) -> dict:
    uri = f"file:{path.as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True, timeout=60)
    con.execute("PRAGMA temp_store=MEMORY")
    available = {
        row[0] for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")
    }
    tables = {}
    for table in SQLITE_TABLES:
        if table not in available:
            continue
        info = list(con.execute(f"PRAGMA table_info({table})"))
        columns = [str(row[1]) for row in info]
        if table in LIVE_LARGE_TABLES:
            tables[table] = {
                "rows": None,
                "columns": columns,
                "count_status": (
                    "omitted: unindexed full-table count intentionally not "
                    "repeated on the live machine"),
            }
            continue
        row_count = int(con.execute(
            f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        entry: dict[str, Any] = {
            "rows": row_count,
            "columns": columns,
        }
        exact_aggregates = row_count <= 1_000_000
        if not exact_aggregates:
            entry["large_table_aggregates_skipped"] = (
                "unindexed group/distinct scan intentionally omitted on "
                "the live machine")
        for key in ("category", "series_ticker", "day"):
            if key in columns and exact_aggregates:
                entry[f"rows_by_{key}"] = {
                    str(value): int(count)
                    for value, count in con.execute(
                        f"SELECT {key}, COUNT(*) FROM {table} "
                        f"GROUP BY {key} ORDER BY {key}")
                }
        for key in ("ticker", "event_ticker"):
            if key in columns and exact_aggregates:
                entry[f"distinct_{key}s"] = int(con.execute(
                    f"SELECT COUNT(DISTINCT {key}) FROM {table}"
                ).fetchone()[0])
        for key in ("first_ts", "last_ts", "ts", "created_time"):
            if key in columns:
                low, high = con.execute(
                    f"SELECT MIN({key}), MAX({key}) FROM {table}"
                ).fetchone()
                entry[f"{key}_range"] = [low, high]
        tables[table] = entry
    con.close()
    result = {
        "logical_name": logical_name,
        "bytes": path.stat().st_size,
        "tables": tables,
    }
    if with_hash:
        result["sha256"] = sha256_file(path)
    return result


def jsonl_census(path: Path, logical_name: str, with_hash: bool) -> dict:
    rows = 0
    malformed = 0
    keys = collections.Counter()
    categories = collections.Counter()
    dates: list[str] = []
    leg_objects = 0
    shaped_legs = 0
    tickers = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except ValueError:
                malformed += 1
                continue
            if not isinstance(row, dict):
                malformed += 1
                continue
            rows += 1
            keys.update(row.keys())
            category = row.get("category") or row.get("cat")
            if category:
                categories[str(category)] += 1
            for key in ("ticker", "event_ticker", "event_id", "event"):
                if row.get(key):
                    tickers.add(str(row[key]))
            legs = row.get("legs")
            if isinstance(legs, list):
                leg_values = legs
            elif isinstance(legs, dict):
                leg_values = list(legs.values())
            else:
                leg_values = []
            leg_objects += len(leg_values)
            shaped_legs += sum(
                isinstance(leg, dict) and bool(leg.get("shape"))
                for leg in leg_values)
            match = DATE_RE.search(line)
            if match:
                dates.append(match.group(0))
            else:
                for key in ("sched_honest", "sched", "right_edge"):
                    value = row.get(key)
                    if isinstance(value, (int, float)) and value > 0:
                        dates.append(dt.datetime.fromtimestamp(
                            value, dt.timezone.utc).date().isoformat())
                        break
    result = {
        "logical_name": logical_name,
        "bytes": path.stat().st_size,
        "rows": rows,
        "malformed_rows": malformed,
        "top_level_field_presence": dict(sorted(keys.items())),
        "rows_by_category": dict(sorted(categories.items())),
        "distinct_public_tickers": len(tickers),
        "date_range": [min(dates), max(dates)] if dates else [None, None],
        "leg_objects": leg_objects,
        "shaped_leg_objects": shaped_legs,
    }
    if with_hash:
        result["sha256"] = sha256_file(path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tennis-db", required=True)
    parser.add_argument("--fund-db", required=True)
    parser.add_argument("--corpus-events", required=True)
    parser.add_argument("--range-spectrum", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--hash-large", action="store_true")
    args = parser.parse_args()
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    report = {
        "schema_version": "window1-canonical-source-census-v1",
        "started_utc": started,
        "contains_private_rows_or_identifiers": False,
        "sources": {
            "tennis_db": sqlite_census(
                Path(args.tennis_db), "$PROD_REPO/arb-executor/tennis.db",
                args.hash_large),
            "fund_equity_db": sqlite_census(
                Path(args.fund_db),
                "$PROD_REPO/arb-executor/state/fund_equity.db", True),
            "corpus_events_v2": jsonl_census(
                Path(args.corpus_events),
                "$PROD_REPO/arb-executor/state/corpus_events_v2.jsonl",
                True),
            "range_spectrum_v1": jsonl_census(
                Path(args.range_spectrum),
                "$PROD_REPO/arb-executor/state/range_spectrum_v1.jsonl",
                True),
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + chr(10),
        encoding="utf-8",
    )
    print(json.dumps({
        name: (
            source.get("rows")
            or sum(
                table.get("rows") or 0
                for table in source.get("tables", {}).values())
        )
        for name, source in report["sources"].items()
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
