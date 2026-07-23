#!/usr/bin/env python3
"""Exhaustive July 12-20 Window-1 source and per-ticker coverage census.

The census never treats an empty normalized bundle as source absence.  It
maps the immutable 804-game ledger against local recorders, verified Spaces
twins recovered into the private research area, the consolidated print store,
the immutable volume database, exchange-trade-identified public tape, and raw
ws_depth archives.  Output contains counts/timestamps only, never credentials
or private account identifiers.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
import math
import re
import sqlite3
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo


VERSION = "window1-source-coverage-v1"
ET = ZoneInfo("America/New_York")
D = 804


class CoverageError(RuntimeError):
    pass


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise CoverageError(f"non-object {path}:{line_number}")
            rows.append(value)
    return rows


def parse_iso(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        if number > 10_000_000_000:
            number /= 1000.0
        return number if math.isfinite(number) else None
    text = str(value).replace("Z", "+00:00")
    try:
        stamp = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    return stamp.timestamp()


def parse_et(value: Any) -> float | None:
    text = str(value or "")
    for pattern in ("%Y-%m-%d %I:%M:%S %p", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(text, pattern).replace(
                tzinfo=ET
            ).timestamp()
        except ValueError:
            pass
    return None


def iso_utc(value: float | None) -> str | None:
    return (
        dt.datetime.fromtimestamp(value, dt.timezone.utc).isoformat()
        if value is not None else None
    )


def finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def choose_file(
    ticker: str, primary: Path, recovered: Path,
) -> tuple[Path | None, str | None]:
    for suffix in (".csv.gz", ".csv"):
        path = primary / (ticker + suffix)
        if path.is_file():
            return path, "production_local"
    for suffix in (".csv.gz", ".csv"):
        path = recovered / (ticker + suffix)
        if path.is_file():
            return path, "spaces_recovered_private"
    return None, None


def open_text(path: Path):
    return (
        gzip.open(path, "rt", encoding="utf-8", errors="strict", newline="")
        if path.suffix == ".gz"
        else path.open(encoding="utf-8", errors="strict", newline="")
    )


def scan_recorder_csv(
    path: Path | None, kind: str,
) -> dict[str, Any]:
    if path is None:
        return {
            "available": False,
            "row_count": 0,
            "first_local_receipt_ts": None,
            "last_local_receipt_ts": None,
        }
    count = 0
    positive = 0
    bbo = 0
    first = None
    last = None
    parse_errors = 0
    if path.suffix == ".gz":
        prefix = b""
        tail = b""
        newline_count = 0
        last_byte = b""
        with gzip.open(path, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                newline_count += block.count(b"\n")
                last_byte = block[-1:]
                if prefix.count(b"\n") < 2:
                    prefix += block
                    if len(prefix) > 2 * 1024 * 1024:
                        raise CoverageError(
                            f"recorder row too large: {path.name}"
                        )
                tail = (tail + block)[-2 * 1024 * 1024:]
        prefix_lines = prefix.splitlines()
        tail_lines = tail.splitlines()
        if not prefix_lines:
            raise CoverageError(f"empty recorder file: {path.name}")
        header = prefix_lines[0].decode("utf-8").split(",")
        positions = {value.strip(): index for index, value in enumerate(
            header
        )}
        required_fields = (
            {"ts_et", "bid_1", "ask_1"}
            if kind == "top5" else {"ts_et", "count"}
        )
        if not required_fields.issubset(positions):
            raise CoverageError(
                f"{kind} recorder schema changed: {path.name}"
            )
        physical_lines = newline_count + (last_byte != b"\n")
        count = max(0, physical_lines - 1)
        required_positions = [positions[value] for value in required_fields]
        endpoint_parse_errors = 0

        def endpoint_values(
            lines: list[bytes], reverse: bool = False,
        ) -> list[str]:
            nonlocal endpoint_parse_errors
            candidates = reversed(lines) if reverse else iter(lines)
            for raw in candidates:
                try:
                    values = raw.decode("utf-8").split(",")
                except UnicodeDecodeError:
                    endpoint_parse_errors += 1
                    continue
                if not raw.strip() or len(values) <= max(required_positions):
                    endpoint_parse_errors += 1
                    continue
                if parse_et(values[positions["ts_et"]]) is None:
                    endpoint_parse_errors += 1
                    continue
                return values
            return []

        first_values = endpoint_values(prefix_lines[1:])
        # The retained tail can begin in the middle of a row.  Search
        # backwards for the last complete, timestamped data row rather than
        # assuming the terminal physical line is complete.
        last_values = endpoint_values(tail_lines, reverse=True)
        parse_errors = endpoint_parse_errors
        first = (
            parse_et(first_values[positions["ts_et"]])
            if first_values else None
        )
        last = (
            parse_et(last_values[positions["ts_et"]])
            if last_values else None
        )
        if kind == "top5":
            observed = any(
                values and finite(values[positions["bid_1"]]) > 0
                and finite(values[positions["ask_1"]]) > 0
                for values in (first_values, last_values)
            )
        else:
            observed = any(
                values and finite(values[positions["count"]]) > 0
                for values in (first_values, last_values)
            )
        return {
            "available": True,
            "bytes": path.stat().st_size,
            "row_count": count,
            "positive_size_rows": None,
            "positive_size_observed_at_endpoint": (
                observed if kind == "trades" else None
            ),
            "valid_bbo_rows": None,
            "valid_bbo_observed_at_endpoint": (
                observed if kind == "top5" else None
            ),
            "first_local_receipt_ts": iso_utc(first),
            "last_local_receipt_ts": iso_utc(last),
            "parse_error_count": parse_errors,
            "parse_error_scope": (
                "first/last retained endpoint rows only; interior rows were "
                "not parsed in the fast gzip census"
            ),
            "scan_mode": (
                "exact_physical_row_count_plus_first_last_endpoints"
            ),
            "timestamp_semantics": (
                "local_recorder_receipt_et; not exchange ordering authority"
            ),
            "source_class": (
                "raw_top5_snapshot" if kind == "top5"
                else "raw_ws_trade_recorder_without_receipt_identity"
            ),
        }

    def positive_text(value: str) -> bool:
        text = value.strip()
        return text not in {"", "0", "0.0", "0.00", "0.000"}

    with open_text(path) as handle:
        header_line = handle.readline()
        header = [value.strip() for value in header_line.rstrip(
            "\r\n"
        ).split(",")]
        positions = {value: index for index, value in enumerate(header)}
        required_fields = (
            {"ts_et", "bid_1", "ask_1"}
            if kind == "top5" else {"ts_et", "count"}
        )
        if not required_fields.issubset(positions):
            raise CoverageError(
                f"{kind} recorder schema changed: {path.name}"
            )
        for line in handle:
            values = line.rstrip("\r\n").split(",")
            if len(values) != len(header):
                parse_errors += 1
                continue
            count += 1
            timestamp_text = values[positions["ts_et"]]
            # Recorder files are append-only and chronological.  Parsing
            # every timestamp dominated the multi-gigabyte census, so retain
            # the first and last physical receipt and parse those only.
            if first is None:
                first = parse_et(timestamp_text)
                if first is None:
                    parse_errors += 1
            last_text = timestamp_text
            if kind == "top5":
                if (
                    positive_text(values[positions["bid_1"]])
                    and positive_text(values[positions["ask_1"]])
                ):
                    bbo += 1
            else:
                if positive_text(values[positions["count"]]):
                    positive += 1
        if count:
            last = parse_et(last_text)
            if last is None:
                parse_errors += 1
    return {
        "available": True,
        "bytes": path.stat().st_size,
        "row_count": count,
        "positive_size_rows": positive if kind == "trades" else None,
        "valid_bbo_rows": bbo if kind == "top5" else None,
        "first_local_receipt_ts": iso_utc(first),
        "last_local_receipt_ts": iso_utc(last),
        "parse_error_count": parse_errors,
        "timestamp_semantics": (
            "local_recorder_receipt_et; not exchange ordering authority"
        ),
        "source_class": (
            "raw_top5_snapshot" if kind == "top5"
            else "raw_ws_trade_recorder_without_receipt_identity"
        ),
    }


def load_public_print_coverage(
    path: Path | None,
) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "row_count": 0,
        "positive_size_rows": 0,
        "first": None,
        "last": None,
    })
    if path is None or not path.is_file():
        return {}
    seen: set[int] = set()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise CoverageError(
                    f"non-object public print {path}:{line_number}"
                )
            identity = str(
                row.get("trade_id") or row.get("receipt_id") or ""
            )
            if not identity:
                continue
            try:
                identity_key = uuid.UUID(identity).int
            except ValueError as exc:
                raise CoverageError(
                    f"non-UUID public trade identity at row {line_number}"
                ) from exc
            if identity_key in seen:
                continue
            seen.add(identity_key)
            ticker = str(row.get("ticker") or "")
            timestamp = parse_iso(row.get("exchange_ts"))
            if not ticker or timestamp is None:
                continue
            item = stats[ticker]
            item["row_count"] += 1
            item["positive_size_rows"] += finite(row.get("size")) > 0
            item["first"] = (
                timestamp if item["first"] is None
                else min(item["first"], timestamp)
            )
            item["last"] = (
                timestamp if item["last"] is None
                else max(item["last"], timestamp)
            )
    return {
        ticker: {
            "available": True,
            "row_count": item["row_count"],
            "positive_size_rows": item["positive_size_rows"],
            "first_exchange_ts": iso_utc(item["first"]),
            "last_exchange_ts": iso_utc(item["last"]),
            "timestamp_semantics": "exchange_created_time",
            "source_class": "raw_public_exchange_trade",
            "public_trade_identity_available": True,
            "private_order_or_fill_receipt_required": False,
        }
        for ticker, item in stats.items()
    }


def validate_public_tape_manifest(
    path: Path,
    prints_path: Path,
    required: set[str],
) -> tuple[set[str], dict[str, Any]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    denominator = manifest.get("immutable_denominator") or {}
    pagination = manifest.get("pagination") or {}
    artifact = (
        (manifest.get("artifacts") or {})
        .get("normalized_true_prints") or {}
    )
    if denominator.get("D") != D:
        raise CoverageError("public tape manifest D changed")
    if denominator.get("required_leg_tickers") != len(required):
        raise CoverageError(
            "public tape manifest required ticker grain changed"
        )
    if not (
        pagination.get("ticker_queries") == len(required)
        and pagination.get("failed_ticker_count") == 0
        and pagination.get("all_terminal_cursors_empty") is True
    ):
        raise CoverageError(
            "public tape pagination/source exhaustion is incomplete"
        )
    expected_hash = str(artifact.get("sha256") or "")
    actual_hash = sha256_file(prints_path)
    if not expected_hash or expected_hash != actual_hash:
        raise CoverageError(
            "public tape bytes disagree with the immutable manifest"
        )
    zero_tickers = {
        str(value) for value in (
            (manifest.get("coverage") or {})
            .get("tickers_with_zero_trades") or []
        )
    }
    if not zero_tickers <= required:
        raise CoverageError(
            "public tape zero-trade list contains a ticker outside D"
        )
    return zero_tickers, {
        "manifest_sha256": sha256_file(path),
        "normalized_prints_sha256": actual_hash,
        "complete_ticker_queries": pagination["ticker_queries"],
        "failed_ticker_queries": pagination["failed_ticker_count"],
        "terminal_cursors_empty": True,
        "proven_zero_trade_tickers": sorted(zero_tickers),
    }


def subsecond_coverage(
    path: Path, required: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    connection = sqlite3.connect(
        "file:" + str(path) + "?mode=ro&immutable=1", uri=True
    )
    by_ticker: dict[str, dict[str, Any]] = defaultdict(dict)
    try:
        columns = [
            row[1] for row in connection.execute(
                "pragma table_info(prints)"
            ).fetchall()
        ]
        if columns != ["event", "ticker", "ts", "price", "size", "src"]:
            raise CoverageError("subsecond_store prints schema changed")
        aggregate: dict[tuple[str, str], dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0, "first": None, "last": None, "positive": 0,
            }
        )
        physical_rows = 0
        # Stream instead of GROUP BY: the 6 GB store previously exhausted
        # root scratch when SQLite built a temporary grouping B-tree.
        rows = connection.execute("SELECT ticker, src, ts, size FROM prints")
        for ticker, source, timestamp, size in rows:
            physical_rows += 1
            if ticker not in required:
                continue
            item = aggregate[(str(ticker), str(source))]
            item["count"] += 1
            if timestamp is not None:
                timestamp = float(timestamp)
                item["first"] = (
                    timestamp if item["first"] is None
                    else min(item["first"], timestamp)
                )
                item["last"] = (
                    timestamp if item["last"] is None
                    else max(item["last"], timestamp)
                )
            item["positive"] += finite(size) > 0
            if physical_rows % 5_000_000 == 0:
                print(
                    f"subsecond_rows={physical_rows}", flush=True
                )
        source_counts = Counter()
        for (ticker, source), item in aggregate.items():
            by_ticker[ticker][source] = {
                "row_count": item["count"],
                "positive_size_rows": item["positive"],
                "first_ts": iso_utc(item["first"]),
                "last_ts": iso_utc(item["last"]),
                "source_class": (
                    "derived_transition"
                    if source == "book_transition"
                    else "consolidated_raw_source"
                ),
                "receipt_identity_available": False,
            }
            source_counts[source] += item["count"]
        ingest = connection.execute(
            "SELECT src, COUNT(*), SUM(rows) FROM ingest_log GROUP BY src"
        ).fetchall()
    finally:
        connection.close()
    return dict(by_ticker), {
        "schema": columns,
        "physical_rows_streamed": physical_rows,
        "required_ticker_rows_by_source": dict(source_counts),
        "ingest_log": [
            {"source": source, "files": files, "rows": rows}
            for source, files, rows in ingest
        ],
        "known_contract_defects": [
            "prints table has no trade/receipt identity",
            "ws_log timestamps are local engine receipt timestamps",
            "book_transition rows have manufactured-size prohibition and size zero",
        ],
    }


def tennis_bbo_coverage(
    path: Path, required: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    connection = sqlite3.connect(
        "file:" + str(path) + "?mode=ro&immutable=1", uri=True
    )
    output = {}
    try:
        aggregate: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "first": None, "last": None, "valid": 0}
        )
        rows = connection.execute(
            """SELECT ticker, bid_cents, ask_cents, polled_at
               FROM kalshi_price_snapshots
               WHERE polled_at >= '2026-07-11'
                 AND polled_at < '2026-07-22'"""
        )
        physical_rows = 0
        for ticker, bid, ask, polled_at in rows:
            physical_rows += 1
            if ticker not in required:
                continue
            item = aggregate[str(ticker)]
            item["count"] += 1
            item["first"] = (
                polled_at if item["first"] is None
                else min(item["first"], polled_at)
            )
            item["last"] = (
                polled_at if item["last"] is None
                else max(item["last"], polled_at)
            )
            item["valid"] += bid is not None and ask is not None
        for ticker, item in aggregate.items():
            output[ticker] = {
                    "available": True,
                    "row_count": item["count"],
                    "valid_bbo_rows": item["valid"],
                    "first_local_poll_et": item["first"],
                    "last_local_poll_et": item["last"],
                    "timestamp_semantics": "local_poll_et",
                    "source_class": "derived_poll_bbo",
                }
        observed_count = connection.execute(
            """SELECT COUNT(*) FROM observed_starts
               WHERE first_inplay_at >= '2026-07-12'
                 AND first_inplay_at < '2026-07-21'"""
        ).fetchone()[0]
    finally:
        connection.close()
    return output, {
        "required_ticker_count": len(output),
        "physical_rows_streamed": physical_rows,
        "observed_start_rows_in_period": int(observed_count),
    }


def scan_depth_recorder(
    directory: Path, required: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "rows": 0, "first": None, "last": None, "max_levels": 0,
    })
    files = [
        path for path in sorted(directory.glob("depth_202607*.jsonl.gz"))
        if "depth_20260712_" <= path.name <= "depth_20260720_zz"
    ]
    physical = 0
    parse_errors = 0
    for index, path in enumerate(files, 1):
        try:
            with gzip.open(path, "rb") as handle:
                for line in handle:
                    physical += 1
                    ticker_match = re.search(
                        rb'"ticker"\s*:\s*"([^"]+)"', line
                    )
                    if ticker_match is None:
                        continue
                    ticker = ticker_match.group(1).decode(
                        "utf-8", errors="replace"
                    )
                    if ticker not in required:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        parse_errors += 1
                        continue
                    timestamp = parse_iso(row.get("ts_epoch"))
                    if timestamp is None:
                        parse_errors += 1
                        continue
                    item = stats[ticker]
                    item["rows"] += 1
                    item["first"] = (
                        timestamp if item["first"] is None
                        else min(item["first"], timestamp)
                    )
                    item["last"] = (
                        timestamp if item["last"] is None
                        else max(item["last"], timestamp)
                    )
                    item["max_levels"] = max(
                        item["max_levels"],
                        len(row.get("bids") or []),
                        len(row.get("asks") or []),
                    )
        except (OSError, EOFError, gzip.BadGzipFile):
            parse_errors += 1
        if index % 25 == 0 or index == len(files):
            print(
                f"depth_files={index}/{len(files)} rows={physical}",
                flush=True,
            )
    return {
        ticker: {
            "available": True,
            "row_count": item["rows"],
            "first_local_receipt_ts": iso_utc(item["first"]),
            "last_local_receipt_ts": iso_utc(item["last"]),
            "max_levels_per_side": item["max_levels"],
            "source_class": "raw_snapshot_top20_change_deduplicated",
            "timestamp_semantics": "local_recorder_receipt_epoch",
            "sequence_numbers_available": False,
            "full_depth": False,
        }
        for ticker, item in stats.items()
    }, {
        "file_count": len(files),
        "physical_rows": physical,
        "parse_errors": parse_errors,
        "required_ticker_count": len(stats),
    }


def snapshot_has_ladder(message: Mapping[str, Any]) -> bool:
    for key in (
        "yes", "no", "yes_dollars", "no_dollars",
        "bids", "asks", "orderbook",
    ):
        value = message.get(key)
        if isinstance(value, (list, dict)) and len(value) > 0:
            return True
    return False


WS_TS_MS_PATTERN = re.compile(
    rb'"ts_ms"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)"?'
)
WS_TS_PATTERN = re.compile(
    rb'"ts"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)"?'
)


def ws_timestamp_from_line(line: bytes) -> float | None:
    """Extract exchange time without JSON-decoding high-volume deltas."""
    match = WS_TS_MS_PATTERN.search(line)
    if match is not None:
        return parse_iso(float(match.group(1)))
    match = WS_TS_PATTERN.search(line)
    if match is not None:
        return parse_iso(float(match.group(1)))
    return None


def scan_ws_depth(
    directory: Path, required: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "delta_rows": 0,
        "trade_rows": 0,
        "positive_trade_rows": 0,
        "snapshot_rows": 0,
        "full_snapshot_rows": 0,
        "full_snapshot_epochs": set(),
        "first_exchange": None,
        "last_exchange": None,
        "epochs": set(),
        "live_transition_rows": 0,
        "first_live_transition": None,
        "first_live_transition_basis": None,
    })
    files = [
        path for path in sorted(directory.glob("ws_202607*.jsonl.gz"))
        if "ws_20260712_" <= path.name <= "ws_20260720_zz"
    ]
    epoch = 0
    epoch_complete_start: dict[int, bool] = {0: False}
    epoch_gaps: Counter[int] = Counter()
    prior_sequence: dict[tuple[int, int], int] = {}
    physical = 0
    parse_errors = 0
    corrupt_files = []
    message_types = Counter()
    ticker_pattern = re.compile(
        rb'"(?:market_ticker|ticker)"\s*:\s*"([^"]+)"'
    )
    sequence_pattern = re.compile(rb'"seq"\s*:\s*(\d+)')
    sid_pattern = re.compile(rb'"sid"\s*:\s*(\d+)')
    type_pattern = re.compile(rb'"type"\s*:\s*"([^"]+)"')
    for file_index, path in enumerate(files, 1):
        try:
            with gzip.open(path, "rb") as handle:
                for line in handle:
                    physical += 1
                    if b'"ev"' in line and b"recorder_start" in line:
                        epoch += 1
                        epoch_complete_start[epoch] = True
                        continue
                    sequence_match = sequence_pattern.search(line)
                    sid_match = sid_pattern.search(line)
                    if sequence_match and sid_match:
                        sid = int(sid_match.group(1))
                        sequence = int(sequence_match.group(1))
                        key = (epoch, sid)
                        prior = prior_sequence.get(key)
                        if prior is not None and sequence != prior + 1:
                            epoch_gaps[epoch] += 1
                        prior_sequence[key] = sequence
                    type_match = type_pattern.search(line)
                    if type_match:
                        message_types[
                            type_match.group(1).decode(
                                "utf-8", errors="replace"
                            )
                        ] += 1
                    ticker_match = ticker_pattern.search(line)
                    if ticker_match is None:
                        continue
                    ticker = ticker_match.group(1).decode(
                        "utf-8", errors="replace"
                    )
                    if ticker not in required:
                        continue
                    item = stats[ticker]
                    item["epochs"].add(epoch)
                    message_type = (
                        type_match.group(1).decode(
                            "utf-8", errors="replace"
                        )
                        if type_match else ""
                    )
                    timestamp = ws_timestamp_from_line(line)
                    if timestamp is not None:
                        item["first_exchange"] = (
                            timestamp if item["first_exchange"] is None
                            else min(item["first_exchange"], timestamp)
                        )
                        item["last_exchange"] = (
                            timestamp if item["last_exchange"] is None
                            else max(item["last_exchange"], timestamp)
                        )
                    if message_type == "orderbook_delta":
                        item["delta_rows"] += 1
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        parse_errors += 1
                        continue
                    wrapper = row.get("m")
                    if not isinstance(wrapper, dict):
                        continue
                    message = wrapper.get("msg")
                    if not isinstance(message, dict):
                        continue
                    if message_type == "orderbook_snapshot":
                        item["snapshot_rows"] += 1
                        has_ladder = snapshot_has_ladder(message)
                        item["full_snapshot_rows"] += has_ladder
                        if has_ladder:
                            item["full_snapshot_epochs"].add(epoch)
                    elif message_type == "trade":
                        item["trade_rows"] += 1
                        item["positive_trade_rows"] += (
                            finite(message.get("count_fp"),
                                   finite(message.get("count"))) > 0
                        )
                    elif message_type == "market_lifecycle_v2":
                        status = str(message.get("status") or "")
                        event_type = str(message.get("event_type") or "")
                        if status in {"live", "P"} or event_type in {
                            "market_started", "live", "in_play"
                        }:
                            item["live_transition_rows"] += 1
                            outer = parse_iso(row.get("t"))
                            transition = timestamp or outer
                            if transition is not None:
                                if (
                                    item["first_live_transition"] is None
                                    or transition
                                    < item["first_live_transition"]
                                ):
                                    item["first_live_transition"] = transition
                                    item[
                                        "first_live_transition_basis"
                                    ] = (
                                        "exchange_payload_timestamp"
                                        if timestamp is not None
                                        else "local_ws_recorder_receipt_utc"
                                    )
        except (OSError, EOFError, gzip.BadGzipFile) as exc:
            corrupt_files.append({
                "file": path.name,
                "error_class": type(exc).__name__,
            })
        if file_index % 12 == 0 or file_index == len(files):
            print(
                f"ws_files={file_index}/{len(files)} rows={physical} "
                f"epochs={epoch + 1} gaps={sum(epoch_gaps.values())}",
                flush=True,
            )
    output = {}
    for ticker, item in stats.items():
        valid_epochs = [
            value for value in item["epochs"]
            if epoch_complete_start.get(value, False)
            and epoch_gaps[value] == 0
            and value in item["full_snapshot_epochs"]
        ]
        output[ticker] = {
            "available": True,
            "orderbook_delta_rows": item["delta_rows"],
            "trade_rows": item["trade_rows"],
            "positive_size_trade_rows": item["positive_trade_rows"],
            "snapshot_rows": item["snapshot_rows"],
            "snapshot_rows_with_ladders": item["full_snapshot_rows"],
            "first_exchange_ts": iso_utc(item["first_exchange"]),
            "last_exchange_ts": iso_utc(item["last_exchange"]),
            "epoch_count": len(item["epochs"]),
            "sequence_valid_full_ladder_epoch_count": len(valid_epochs),
            "full_depth_usable": bool(valid_epochs),
            "live_transition_rows": item["live_transition_rows"],
            "first_live_transition_ts": iso_utc(
                item["first_live_transition"]
            ),
            "first_live_transition_timestamp_basis": item[
                "first_live_transition_basis"
            ],
            "source_class": "raw_websocket_delta_and_trade",
        }
    return output, {
        "file_count": len(files),
        "bytes": sum(path.stat().st_size for path in files),
        "physical_rows": physical,
        "parse_errors": parse_errors,
        "corrupt_files": corrupt_files,
        "epoch_count": epoch + 1,
        "epoch_gap_count": sum(epoch_gaps.values()),
        "epochs_with_gaps": sum(value > 0 for value in epoch_gaps.values()),
        "complete_start_epochs": sum(epoch_complete_start.values()),
        "message_types": dict(message_types),
        "required_ticker_count": len(stats),
        "required_tickers_with_full_depth": sum(
            row["full_depth_usable"] for row in output.values()
        ),
    }


def load_spaces_names(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("["):
        value = json.loads(text)
        if not isinstance(value, list):
            raise CoverageError(f"Spaces lsjson array required: {path}")
        return {
            Path(str(row.get("Path") or row.get("Name") or "")).name
            for row in value if isinstance(row, dict)
            and (row.get("Path") or row.get("Name"))
        }
    return {
        Path(line.strip()).name for line in text.splitlines()
        if line.strip()
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_precomputed_ws_depth(
    ledger_path: Path,
    summary_path: Path,
    required: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Load a receipted offline WS census without rescanning raw archives."""
    receipt = json.loads(summary_path.read_text(encoding="utf-8"))
    summary = receipt.get("ws_depth")
    if not isinstance(summary, dict):
        raise CoverageError("precomputed WS summary has no ws_depth object")
    expected = {
        "D": D,
        "required_tickers": len(required),
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise CoverageError(
                f"precomputed WS {field} changed: "
                f"{receipt.get(field)!r} != {value!r}"
            )
    if summary.get("file_count") != 215:
        raise CoverageError(
            "precomputed WS immutable object count changed: "
            f"{summary.get('file_count')!r}"
        )
    if summary.get("all_objects_exact") is not True:
        raise CoverageError(
            "precomputed WS did not prove every immutable object"
        )
    actual_hash = sha256_file(ledger_path)
    if receipt.get("ledger_sha256") != actual_hash:
        raise CoverageError(
            "precomputed WS ledger hash disagrees with its receipt"
        )
    rows = read_jsonl(ledger_path)
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        ticker = str(row.get("ticker") or "")
        if not ticker or ticker in output:
            raise CoverageError(
                f"invalid/duplicate precomputed WS ticker: {ticker!r}"
            )
        output[ticker] = {
            key: value for key, value in row.items()
            if key not in {"ticker", "schema_version"}
        }
    if set(output) != required:
        missing = len(required - set(output))
        extra = len(set(output) - required)
        raise CoverageError(
            "precomputed WS ticker grain changed: "
            f"missing={missing} extra={extra}"
        )
    if summary.get("required_ticker_count") != len(required):
        raise CoverageError(
            "precomputed WS summary ticker count changed: "
            f"{summary.get('required_ticker_count')!r}"
        )
    return output, {
        **summary,
        "precomputed_receipt_sha256": sha256_file(summary_path),
        "precomputed_ledger_sha256": actual_hash,
        "scan_reused": True,
    }


def run(args: argparse.Namespace) -> int:
    events = read_jsonl(Path(args.events).resolve())
    if len(events) != D:
        raise CoverageError(f"immutable D changed: {len(events)}")
    required = {
        str(leg["ticker"]) for event in events for leg in event["legs"]
    }
    if len(required) != 1608:
        raise CoverageError(f"required ticker count changed: {len(required)}")

    spaces_ticks = load_spaces_names(Path(args.spaces_ticks).resolve())
    spaces_trades = load_spaces_names(Path(args.spaces_trades).resolve())
    spaces_ws = load_spaces_names(Path(args.spaces_ws_depth).resolve())
    top5: dict[str, dict[str, Any]] = {}
    recorder_trades: dict[str, dict[str, Any]] = {}
    def scan_ticker(
        ticker: str,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        path, location = choose_file(
            ticker, Path(args.premarket_dir).resolve(),
            Path(args.recovered_ticks_dir).resolve(),
        )
        ticker_top5 = scan_recorder_csv(path, "top5")
        ticker_top5["selected_location"] = location
        ticker_top5["spaces_twin_available"] = (
            ticker + ".csv.gz" in spaces_ticks
            or ticker + ".csv" in spaces_ticks
        )
        path, location = choose_file(
            ticker, Path(args.trades_dir).resolve(),
            Path(args.recovered_trades_dir).resolve(),
        )
        ticker_trades = scan_recorder_csv(path, "trades")
        ticker_trades["selected_location"] = location
        ticker_trades["spaces_twin_available"] = (
            ticker + ".csv.gz" in spaces_trades
            or ticker + ".csv" in spaces_trades
        )
        return ticker, ticker_top5, ticker_trades

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.csv_workers
    ) as executor:
        futures = [
            executor.submit(scan_ticker, ticker)
            for ticker in sorted(required)
        ]
        for index, future in enumerate(
            concurrent.futures.as_completed(futures), 1
        ):
            ticker, ticker_top5, ticker_trades = future.result()
            top5[ticker] = ticker_top5
            recorder_trades[ticker] = ticker_trades
            if index % 100 == 0 or index == len(required):
                print(f"csv_tickers={index}/{len(required)}", flush=True)

    public_path = (
        Path(args.public_prints).resolve()
        if args.public_prints else None
    )
    public = load_public_print_coverage(public_path)
    public_receipt: dict[str, Any] = {
        "complete_ticker_queries": 0,
        "proven_zero_trade_tickers": [],
    }
    proven_zero_trade: set[str] = set()
    if args.public_tape_manifest:
        if public_path is None:
            raise CoverageError(
                "public prints are required with a tape manifest"
            )
        proven_zero_trade, public_receipt = (
            validate_public_tape_manifest(
                Path(args.public_tape_manifest).resolve(),
                public_path,
                required,
            )
        )
        for ticker in proven_zero_trade:
            public[ticker] = {
                "available": True,
                "row_count": 0,
                "positive_size_rows": 0,
                "first_exchange_ts": None,
                "last_exchange_ts": None,
                "timestamp_semantics": "exchange_created_time",
                "source_class": "raw_public_exchange_trade",
                "public_trade_identity_available": True,
                "private_order_or_fill_receipt_required": False,
                "complete_zero_trade_query": True,
            }
    subsecond, subsecond_summary = subsecond_coverage(
        Path(args.subsecond_db).resolve(), required
    )
    tennis_bbo, tennis_summary = tennis_bbo_coverage(
        Path(args.tennis_db).resolve(), required
    )
    depth, depth_summary = scan_depth_recorder(
        Path(args.depth_recorder_dir).resolve(), required
    )
    if args.ws_precomputed_ledger or args.ws_precomputed_summary:
        if not (
            args.ws_precomputed_ledger
            and args.ws_precomputed_summary
        ):
            raise CoverageError(
                "both precomputed WS ledger and summary are required"
            )
        ws, ws_summary = load_precomputed_ws_depth(
            Path(args.ws_precomputed_ledger).resolve(),
            Path(args.ws_precomputed_summary).resolve(),
            required,
        )
    else:
        if not args.ws_depth_dir:
            raise CoverageError(
                "ws-depth-dir or a receipted precomputed WS scan is required"
            )
        ws, ws_summary = scan_ws_depth(
            Path(args.ws_depth_dir).resolve(), required
        )

    ledger = []
    for event in events:
        legs = []
        for leg in event["legs"]:
            ticker = str(leg["ticker"])
            print_tape_complete = ticker in public
            positive_exchange_prints = (
                (public.get(ticker) or {}).get(
                    "positive_size_rows", 0
                ) > 0
            )
            bbo_available = (
                top5[ticker].get("valid_bbo_observed_at_endpoint") is True
                or (top5[ticker].get("valid_bbo_rows") or 0) > 0
                or (tennis_bbo.get(ticker) or {}).get(
                    "valid_bbo_rows", 0
                ) > 0
            )
            join_failures = []
            if not bbo_available:
                join_failures.append("no_causal_bbo_source_joined")
            if not print_tape_complete:
                join_failures.append(
                    "no_source_exhaustive_exchange_timestamped_print_tape"
                )
            if not (ws.get(ticker) or {}).get("full_depth_usable", False):
                join_failures.append(
                    "no_sequence_valid_full_ladder_epoch"
                )
            legs.append({
                "leg": leg.get("leg"),
                "ticker": ticker,
                "sources": {
                    "premarket_ticks_top5": top5[ticker],
                    "analysis_trades": recorder_trades[ticker],
                    "exchange_trade_identified_public_tape": public.get(
                        ticker, {"available": False, "row_count": 0}
                    ),
                    "depth_recorder_top20": depth.get(
                        ticker, {"available": False, "row_count": 0}
                    ),
                    "ws_depth": ws.get(
                        ticker, {"available": False}
                    ),
                    "subsecond_store": subsecond.get(ticker, {}),
                    "tennis_db_bbo": tennis_bbo.get(
                        ticker, {"available": False}
                    ),
                },
                "minimum_bbo_plus_print_instrument_available": (
                    bbo_available and print_tape_complete
                ),
                "positive_size_true_print_observed": (
                    positive_exchange_prints
                ),
                "complete_zero_trade_tape": (
                    ticker in proven_zero_trade
                ),
                "join_failures": join_failures,
            })
        ledger.append({
            "coverage_version": VERSION,
            "event_id": event["event_id"],
            "event_date": event["event_date"],
            "category": event["category"],
            "scheduled_start_exchange_ts": event.get(
                "scheduled_start_exchange_ts"
            ),
            "event_mapping": "exact_event_id_and_exact_leg_ticker",
            "legs": legs,
            "both_legs_minimum_instrument_available": all(
                row["minimum_bbo_plus_print_instrument_available"]
                for row in legs
            ),
            "full_depth_is_eligibility_gate": False,
        })

    output_path = Path(args.ledger_output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in ledger:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")
    summary = {
        "coverage_version": VERSION,
        "D": D,
        "required_tickers": len(required),
        "normalized_empty_bundle_interpretation": (
            "pipeline/source-join failure; not source absence"
        ),
        "event_counts": {
            "both_legs_minimum_instrument": sum(
                row["both_legs_minimum_instrument_available"]
                for row in ledger
            ),
            "any_leg_missing_minimum_instrument": sum(
                not row["both_legs_minimum_instrument_available"]
                for row in ledger
            ),
        },
        "ticker_counts": {
            "top5_available": sum(row["available"] for row in top5.values()),
            "top5_spaces_twin": sum(
                row["spaces_twin_available"] for row in top5.values()
            ),
            "analysis_trade_available": sum(
                row["available"] for row in recorder_trades.values()
            ),
            "analysis_trade_spaces_twin": sum(
                row["spaces_twin_available"]
                for row in recorder_trades.values()
            ),
            "exchange_trade_identified_public_print_available": len(public),
            "depth_top20_available": len(depth),
            "ws_any_available": len(ws),
            "ws_full_depth_usable": sum(
                row["full_depth_usable"] for row in ws.values()
            ),
            "subsecond_any_available": len(subsecond),
            "tennis_db_bbo_available": len(tennis_bbo),
        },
        "spaces": {
            "ticks_object_count": len(spaces_ticks),
            "trades_object_count": len(spaces_trades),
            "ws_depth_object_count": len(spaces_ws),
            "required_tick_twin_count": sum(
                ticker + ".csv.gz" in spaces_ticks
                or ticker + ".csv" in spaces_ticks
                for ticker in required
            ),
            "required_trade_twin_count": sum(
                ticker + ".csv.gz" in spaces_trades
                or ticker + ".csv" in spaces_trades
                for ticker in required
            ),
            "development_ws_hour_count": sum(
                any(f"ws_202607{day:02d}_" in name
                    for day in range(12, 21))
                for name in spaces_ws
            ),
        },
        "subsecond_store": subsecond_summary,
        "tennis_db": tennis_summary,
        "public_tape": public_receipt,
        "depth_recorder": depth_summary,
        "ws_depth": ws_summary,
        "source_laws": {
            "premarket_ticks": (
                "top-five local-receipt snapshots; not full chain"
            ),
            "analysis_trades": (
                "real size/direction, local receipt time, no trade identity"
            ),
            "public_tape": (
                "trade identity, verified size, exchange timestamp"
            ),
            "depth_recorder": (
                "top-20 snapshot/change-deduplicated; not full chain"
            ),
            "ws_depth": (
                "raw deltas/trades/sequences; full depth only after a "
                "ladder-bearing snapshot inside a gap-free epoch"
            ),
            "missing_full_depth": "never removes an event from D",
        },
    }
    Path(args.summary_output).resolve().write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "D": D,
        "event_counts": summary["event_counts"],
        "ticker_counts": summary["ticker_counts"],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--premarket-dir", required=True)
    result.add_argument("--trades-dir", required=True)
    result.add_argument("--recovered-ticks-dir", required=True)
    result.add_argument("--recovered-trades-dir", required=True)
    result.add_argument("--depth-recorder-dir", required=True)
    result.add_argument("--ws-depth-dir")
    result.add_argument("--ws-precomputed-ledger")
    result.add_argument("--ws-precomputed-summary")
    result.add_argument("--subsecond-db", required=True)
    result.add_argument("--tennis-db", required=True)
    result.add_argument("--public-prints")
    result.add_argument("--public-tape-manifest")
    result.add_argument("--csv-workers", type=int, default=4)
    result.add_argument("--spaces-ticks", required=True)
    result.add_argument("--spaces-trades", required=True)
    result.add_argument("--spaces-ws-depth", required=True)
    result.add_argument("--ledger-output", required=True)
    result.add_argument("--summary-output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
