#!/usr/bin/env python3
"""Reconcile archived WS trades with the complete public true-print tape.

The public endpoint export is already receipt-deduplicated by exchange
trade_id.  This instrument proves whether every recovered WS trade is the
same exchange receipt at the same ticker, millisecond, price, and size.  It
does not infer fills or build depth from deltas.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
import sqlite3
import zlib
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence


VERSION = "window1-ws-public-trade-reconcile-v1"


class TradeReconcileError(RuntimeError):
    """A causal trade-stream contract failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TradeReconcileError(f"{path} is not a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TradeReconcileError(
                    f"{path}:{line_number} is not an object"
                )
            rows.append(value)
    return rows


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def decimal_text(value: Any) -> str:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TradeReconcileError(
            f"invalid exchange size {value!r}"
        ) from exc
    if not parsed.is_finite():
        raise TradeReconcileError("non-finite exchange size")
    return format(parsed.normalize(), "f")


def price_cents(value: Any) -> int:
    try:
        parsed = Decimal(str(value)) * Decimal("100")
    except (InvalidOperation, ValueError) as exc:
        raise TradeReconcileError(
            f"invalid exchange price {value!r}"
        ) from exc
    integral = parsed.to_integral_value()
    if parsed != integral:
        raise TradeReconcileError(
            f"exchange price is not whole cents: {value!r}"
        )
    return int(integral)


def epoch_ms(value: Any) -> int:
    if isinstance(value, (int, float)):
        number = float(value)
        return int(number if number > 10_000_000_000 else number * 1000)
    try:
        parsed = dt.datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise TradeReconcileError(
            f"invalid exchange timestamp {value!r}"
        ) from exc
    if parsed.tzinfo is None:
        raise TradeReconcileError("exchange timestamp lacks timezone")
    return int(parsed.timestamp() * 1000)


def event_tickers(events: Sequence[Mapping[str, Any]]) -> set[str]:
    tickers: set[str] = set()
    if len(events) != 804:
        raise TradeReconcileError("D is not 804")
    for event in events:
        legs = event.get("legs") or []
        if len(legs) != 2:
            raise TradeReconcileError("event does not have two legs")
        for leg in legs:
            ticker = str(leg.get("ticker") or "")
            if not ticker or ticker in tickers:
                raise TradeReconcileError("required ticker set is invalid")
            tickers.add(ticker)
    if len(tickers) != 1608:
        raise TradeReconcileError("required ticker count is not 1,608")
    return tickers


def scan_ws_file(
    task: tuple[str, frozenset[str]],
) -> dict[str, Any]:
    path_text, required = task
    path = Path(path_text)
    rows: list[tuple[str, str, int, int, str, str]] = []
    physical = trade_rows = irrelevant = zero_size = parse_errors = 0
    error_class = None
    try:
        with gzip.open(path, "rb") as handle:
            for raw in handle:
                physical += 1
                if b'"type":"trade"' not in raw:
                    continue
                try:
                    outer = json.loads(raw)
                    wrapper = outer.get("m") or {}
                    message = wrapper.get("msg") or {}
                    ticker = str(message.get("market_ticker") or "")
                    if ticker not in required:
                        irrelevant += 1
                        continue
                    trade_id = str(message.get("trade_id") or "")
                    if not trade_id:
                        raise TradeReconcileError(
                            "WS trade lacks exchange trade_id"
                        )
                    size = decimal_text(
                        message.get("count_fp")
                        if message.get("count_fp") is not None
                        else message.get("count")
                    )
                    if Decimal(size) <= 0:
                        zero_size += 1
                    rows.append((
                        trade_id,
                        ticker,
                        epoch_ms(
                            message.get("ts_ms")
                            if message.get("ts_ms") is not None
                            else message.get("ts")
                        ),
                        price_cents(message.get("yes_price_dollars")),
                        size,
                        path.name,
                    ))
                    trade_rows += 1
                except (
                    json.JSONDecodeError,
                    KeyError,
                    TypeError,
                    TradeReconcileError,
                ):
                    parse_errors += 1
    except (EOFError, OSError, zlib.error) as exc:
        error_class = type(exc).__name__
    return {
        "file": path.name,
        "physical_rows": physical,
        "required_trade_rows": trade_rows,
        "irrelevant_trade_rows": irrelevant,
        "zero_size_trade_rows": zero_size,
        "parse_errors": parse_errors,
        "read_error_class": error_class,
        "rows": rows,
    }


def configure_database(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA journal_mode=OFF;
        PRAGMA synchronous=OFF;
        PRAGMA temp_store=MEMORY;
        PRAGMA locking_mode=EXCLUSIVE;
        PRAGMA cache_size=-262144;
        """
    )


def load_public(
    connection: sqlite3.Connection,
    path: Path,
    required: set[str],
) -> dict[str, int]:
    connection.execute(
        """
        CREATE TABLE public_print (
            trade_id TEXT PRIMARY KEY,
            ticker TEXT NOT NULL,
            ts_ms INTEGER NOT NULL,
            price_cents INTEGER NOT NULL,
            size_text TEXT NOT NULL
        ) WITHOUT ROWID
        """
    )
    statement = (
        "INSERT INTO public_print VALUES (?, ?, ?, ?, ?)"
    )
    batch: list[tuple[str, str, int, int, str]] = []
    row_count = zero_size = outside_D = 0
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            ticker = str(row.get("ticker") or "")
            if ticker not in required:
                outside_D += 1
                continue
            if row.get("true_print") is not True:
                raise TradeReconcileError(
                    f"public row {line_number} is not a true print"
                )
            trade_id = str(
                row.get("trade_id") or row.get("receipt_id") or ""
            )
            if not trade_id:
                raise TradeReconcileError(
                    f"public row {line_number} lacks trade identity"
                )
            size = decimal_text(row.get("size"))
            if Decimal(size) <= 0:
                zero_size += 1
            batch.append((
                trade_id,
                ticker,
                epoch_ms(row.get("exchange_ts")),
                int(row.get("price_cents")),
                size,
            ))
            row_count += 1
            if len(batch) >= 20_000:
                try:
                    connection.executemany(statement, batch)
                except sqlite3.IntegrityError as exc:
                    raise TradeReconcileError(
                        "public tape repeats an exchange trade identity"
                    ) from exc
                batch.clear()
    if batch:
        try:
            connection.executemany(statement, batch)
        except sqlite3.IntegrityError as exc:
            raise TradeReconcileError(
                "public tape repeats an exchange trade identity"
            ) from exc
    connection.commit()
    return {
        "rows": row_count,
        "zero_size_rows": zero_size,
        "outside_D_rows": outside_D,
    }


def scalar(connection: sqlite3.Connection, query: str) -> int:
    value = connection.execute(query).fetchone()
    return int(value[0]) if value else 0


def reconciliation_gate_pass(
    mismatch_total: int,
    public_tickers_with_prints: int,
    proven_zero_trade_ticker_count: int,
    union_rows: int,
    public_rows: int,
) -> bool:
    return (
        mismatch_total == 0
        and public_tickers_with_prints
        + proven_zero_trade_ticker_count == 1608
        and union_rows == public_rows
    )


def run(args: argparse.Namespace) -> int:
    events_path = Path(args.events)
    public_path = Path(args.public_prints)
    public_manifest_path = Path(args.public_manifest)
    ws_dir = Path(args.ws_dir)
    ws_summary_path = Path(args.ws_summary)
    database_path = Path(args.private_database)
    output_path = Path(args.output)

    events = read_jsonl(events_path)
    required = event_tickers(events)
    public_manifest = read_json(public_manifest_path)
    ws_summary = read_json(ws_summary_path)
    expected_public_hash = (
        (public_manifest.get("artifacts") or {})
        .get("normalized_true_prints", {})
        .get("sha256")
    )
    public_hash = sha256_file(public_path)
    if not expected_public_hash or public_hash != expected_public_hash:
        raise TradeReconcileError(
            "public true-print hash does not match its receipt"
        )
    if (
        (public_manifest.get("pagination") or {})
        .get("all_terminal_cursors_empty") is not True
        or int(
            (public_manifest.get("pagination") or {})
            .get("failed_ticker_count") or 0
        ) != 0
    ):
        raise TradeReconcileError("public tape pagination is incomplete")
    if ws_summary.get("ws_depth", {}).get("all_objects_exact") is not True:
        raise TradeReconcileError("WS source objects are not exact")

    files = sorted(ws_dir.glob("ws_*.jsonl.gz"))
    expected_file_count = int(
        ws_summary.get("ws_depth", {}).get("file_count") or 0
    )
    if len(files) != expected_file_count:
        raise TradeReconcileError(
            "WS local file count differs from frozen source receipt"
        )

    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    connection = sqlite3.connect(database_path)
    configure_database(connection)
    public_stats = load_public(connection, public_path, required)
    expected_public_rows = int(
        (public_manifest.get("records") or {})
        .get("canonical_true_print_rows") or 0
    )
    if public_stats["rows"] != expected_public_rows:
        raise TradeReconcileError(
            "public true-print row count differs from its receipt"
        )

    connection.execute(
        """
        CREATE TABLE ws_raw (
            trade_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            ts_ms INTEGER NOT NULL,
            price_cents INTEGER NOT NULL,
            size_text TEXT NOT NULL,
            source_file TEXT NOT NULL
        )
        """
    )
    insert_ws = "INSERT INTO ws_raw VALUES (?, ?, ?, ?, ?, ?)"
    tasks = [(str(path), frozenset(required)) for path in files]
    file_summaries = []
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=args.workers
    ) as executor:
        futures = [executor.submit(scan_ws_file, task) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            rows = result.pop("rows")
            if rows:
                connection.executemany(insert_ws, rows)
            file_summaries.append(result)
    connection.commit()
    file_summaries.sort(key=lambda row: row["file"])

    connection.executescript(
        """
        CREATE INDEX ws_raw_id ON ws_raw(trade_id);
        CREATE TABLE ws_unique AS
        SELECT
            trade_id,
            MIN(ticker) AS ticker,
            MIN(ts_ms) AS ts_ms,
            MIN(price_cents) AS price_cents,
            MIN(size_text) AS size_text
        FROM ws_raw
        GROUP BY trade_id;
        CREATE UNIQUE INDEX ws_unique_id ON ws_unique(trade_id);
        """
    )
    connection.commit()

    ws_raw_rows = scalar(connection, "SELECT COUNT(*) FROM ws_raw")
    ws_unique_rows = scalar(connection, "SELECT COUNT(*) FROM ws_unique")
    conflicting = scalar(
        connection,
        """
        SELECT COUNT(*) FROM (
            SELECT trade_id
            FROM ws_raw
            GROUP BY trade_id
            HAVING
                MIN(ticker) <> MAX(ticker)
                OR MIN(ts_ms) <> MAX(ts_ms)
                OR MIN(price_cents) <> MAX(price_cents)
                OR MIN(size_text) <> MAX(size_text)
        )
        """,
    )
    ws_missing_public = scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM ws_unique w
        LEFT JOIN public_print p USING (trade_id)
        WHERE p.trade_id IS NULL
        """,
    )
    ticker_mismatch = scalar(
        connection,
        """
        SELECT COUNT(*) FROM ws_unique w
        JOIN public_print p USING (trade_id)
        WHERE w.ticker <> p.ticker
        """,
    )
    timestamp_mismatch = scalar(
        connection,
        """
        SELECT COUNT(*) FROM ws_unique w
        JOIN public_print p USING (trade_id)
        WHERE w.ts_ms <> p.ts_ms
        """,
    )
    price_mismatch = scalar(
        connection,
        """
        SELECT COUNT(*) FROM ws_unique w
        JOIN public_print p USING (trade_id)
        WHERE w.price_cents <> p.price_cents
        """,
    )
    size_mismatch = scalar(
        connection,
        """
        SELECT COUNT(*) FROM ws_unique w
        JOIN public_print p USING (trade_id)
        WHERE CAST(w.size_text AS REAL) <> CAST(p.size_text AS REAL)
        """,
    )
    matched = scalar(
        connection,
        """
        SELECT COUNT(*) FROM ws_unique w
        JOIN public_print p USING (trade_id)
        WHERE
            w.ticker = p.ticker
            AND w.ts_ms = p.ts_ms
            AND w.price_cents = p.price_cents
            AND CAST(w.size_text AS REAL) = CAST(p.size_text AS REAL)
        """,
    )
    public_ticker_count = scalar(
        connection, "SELECT COUNT(DISTINCT ticker) FROM public_print"
    )
    ws_ticker_count = scalar(
        connection, "SELECT COUNT(DISTINCT ticker) FROM ws_unique"
    )
    connection.close()

    read_errors = [
        {
            "file": row["file"],
            "error_class": row["read_error_class"],
        }
        for row in file_summaries if row["read_error_class"]
    ]
    parse_errors = sum(row["parse_errors"] for row in file_summaries)
    zero_ws = sum(row["zero_size_trade_rows"] for row in file_summaries)
    union_rows = public_stats["rows"] + ws_missing_public
    proven_zero_trade_tickers = sorted(
        str(value)
        for value in (
            (public_manifest.get("coverage") or {})
            .get("tickers_with_zero_trades") or []
        )
    )
    mismatch_total = (
        conflicting
        + ws_missing_public
        + ticker_mismatch
        + timestamp_mismatch
        + price_mismatch
        + size_mismatch
        + parse_errors
        + zero_ws
        + public_stats["zero_size_rows"]
    )
    summary = {
        "schema_version": VERSION,
        "D": 804,
        "required_legs": 1608,
        "gate_pass": reconciliation_gate_pass(
            mismatch_total,
            public_ticker_count,
            len(proven_zero_trade_tickers),
            union_rows,
            public_stats["rows"],
        ),
        "canonical_true_print_stream": {
            "source": "complete_public_tape_after_WS_identity_reconciliation",
            "path_is_private": True,
            "sha256": public_hash,
            "rows": public_stats["rows"],
            "union_rows": union_rows,
            "identity": "exchange_trade_id",
            "timestamp": "exchange timestamp; WS compared at its ms precision",
            "zero_size_rows": public_stats["zero_size_rows"],
            "required_tickers": 1608,
            "tickers_with_true_prints": public_ticker_count,
            "proven_zero_trade_tickers": proven_zero_trade_tickers,
            "public_pagination_complete": True,
        },
        "archived_ws_trade_stream": {
            "files": len(files),
            "physical_rows": sum(
                row["physical_rows"] for row in file_summaries
            ),
            "required_trade_receipt_rows": ws_raw_rows,
            "unique_exchange_trade_ids": ws_unique_rows,
            "duplicate_receipt_rows_deduplicated": (
                ws_raw_rows - ws_unique_rows
            ),
            "conflicting_duplicate_identities": conflicting,
            "required_tickers": 1608,
            "tickers_with_trade_receipts": ws_ticker_count,
            "tickers_without_trade_receipts": 1608 - ws_ticker_count,
            "zero_size_rows": zero_ws,
            "parse_errors": parse_errors,
            "read_errors": read_errors,
            "read_error_count": len(read_errors),
            "read_errors_are_coverage_censoring": True,
        },
        "identity_reconciliation": {
            "exact_matches": matched,
            "WS_identities_absent_from_public_tape": ws_missing_public,
            "ticker_mismatches": ticker_mismatch,
            "exchange_timestamp_ms_mismatches": timestamp_mismatch,
            "YES_price_mismatches": price_mismatch,
            "size_mismatches": size_mismatch,
            "mismatch_total": mismatch_total,
        },
        "market_depth_law": {
            "raw_ws_delta_available": True,
            "full_depth_available": False,
            "full_depth_reason": (
                "zero required tickers have a ladder-bearing snapshot "
                "inside a recorder-started, sequence-valid epoch"
            ),
            "full_depth_features_censored": True,
        },
        "execution_law": {
            "true_print_requires_exchange_identity": True,
            "zero_size_promoted_to_fill": False,
            "public_or_WS_duplicate_receipt_promoted_twice": False,
            "touch_without_print_is_fill": False,
        },
        "input_hashes": {
            "events": sha256_file(events_path),
            "public_manifest": sha256_file(public_manifest_path),
            "public_prints": public_hash,
            "ws_summary": sha256_file(ws_summary_path),
        },
        "private_work_database": {
            "retained_outside_git": True,
            "path_included": False,
        },
    }
    write_json(output_path, summary)
    print(json.dumps({
        "gate_pass": summary["gate_pass"],
        "public_rows": public_stats["rows"],
        "ws_raw_rows": ws_raw_rows,
        "ws_unique_rows": ws_unique_rows,
        "mismatch_total": mismatch_total,
        "read_error_count": len(read_errors),
    }, sort_keys=True))
    return 0 if summary["gate_pass"] else 2


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--public-prints", required=True)
    result.add_argument("--public-manifest", required=True)
    result.add_argument("--ws-dir", required=True)
    result.add_argument("--ws-summary", required=True)
    result.add_argument("--private-database", required=True)
    result.add_argument("--output", required=True)
    result.add_argument("--workers", type=int, default=8)
    return result


def main() -> int:
    return run(parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
