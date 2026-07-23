#!/usr/bin/env python3
"""Parallel, offline census of immutable Window-1 ws_depth archives.

The high-volume orderbook delta path is parsed without manufacturing book
state.  Full depth is usable only when a non-empty ladder snapshot seeds a
recorder-started, gap-free sequence epoch.  Output is public market metadata;
raw archives remain outside Git.
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
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping


VERSION = "window1-ws-depth-parallel-v1"
TICKER_PATTERN = re.compile(
    rb'"(?:market_ticker|ticker)"\s*:\s*"([^"]+)"'
)
SEQUENCE_PATTERN = re.compile(rb'"seq"\s*:\s*(\d+)')
SID_PATTERN = re.compile(rb'"sid"\s*:\s*(\d+)')
TYPE_PATTERN = re.compile(rb'"type"\s*:\s*"([^"]+)"')
TS_MS_PATTERN = re.compile(
    rb'"ts_ms"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)"?'
)
TS_PATTERN = re.compile(
    rb'"ts"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)"?'
)


class WsCensusError(RuntimeError):
    """The immutable WS census contract failed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_epoch(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        if number > 10_000_000_000:
            number /= 1000.0
        return number if math.isfinite(number) else None
    try:
        stamp = dt.datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    return stamp.timestamp()


def iso_utc(value: float | None) -> str | None:
    return (
        dt.datetime.fromtimestamp(
            value, dt.timezone.utc
        ).isoformat()
        if value is not None else None
    )


def finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def timestamp_from_line(line: bytes) -> float | None:
    marker = b'"ts_ms":'
    start = line.find(marker)
    if start >= 0:
        start += len(marker)
        if start < len(line) and line[start] == 34:
            start += 1
        end = start
        while end < len(line) and (
            48 <= line[end] <= 57 or line[end] == 46
        ):
            end += 1
        if end > start:
            return parse_epoch(float(line[start:end]))
    match = TS_MS_PATTERN.search(line)
    if match is not None:
        return parse_epoch(float(match.group(1)))
    marker = b'"ts":"'
    start = line.find(marker)
    if start >= 0:
        start += len(marker)
        end = line.find(b'"', start)
        if end > start:
            return parse_epoch(line[start:end].decode("ascii"))
    match = TS_PATTERN.search(line)
    if match is not None:
        return parse_epoch(float(match.group(1)))
    return None


def fast_quoted(
    line: bytes, marker: bytes, fallback: re.Pattern[bytes],
) -> bytes | None:
    start = line.find(marker)
    if start >= 0:
        start += len(marker)
        end = line.find(b'"', start)
        if end > start:
            return line[start:end]
    match = fallback.search(line)
    return match.group(1) if match is not None else None


def fast_uint(
    line: bytes, marker: bytes, fallback: re.Pattern[bytes],
) -> int | None:
    start = line.find(marker)
    if start >= 0:
        start += len(marker)
        end = start
        while end < len(line) and 48 <= line[end] <= 57:
            end += 1
        if end > start:
            return int(line[start:end])
    match = fallback.search(line)
    return int(match.group(1)) if match is not None else None


def snapshot_has_ladder(message: Mapping[str, Any]) -> bool:
    for key in (
        "yes", "no", "yes_dollars", "no_dollars",
        "bids", "asks", "orderbook",
    ):
        value = message.get(key)
        if isinstance(value, (list, dict)) and len(value) > 0:
            return True
    return False


def new_ticker_stats() -> dict[str, Any]:
    return {
        "delta_rows": 0,
        "trade_rows": 0,
        "positive_trade_rows": 0,
        "snapshot_rows": 0,
        "full_snapshot_rows": 0,
        "first_exchange": None,
        "last_exchange": None,
        "segments": set(),
        "full_snapshot_segments": set(),
        "live_transition_rows": 0,
        "first_live_transition": None,
        "first_live_transition_basis": None,
    }


def new_segment(started: bool) -> dict[str, Any]:
    return {
        "started_by_recorder": started,
        "first_by_sid": {},
        "last_by_sid": {},
        "gap_count": 0,
    }


def scan_file(
    task: tuple[str, str, int, str, set[str]],
) -> dict[str, Any]:
    path_text, expected_md5, expected_size, expected_name, required = task
    path = Path(path_text)
    result: dict[str, Any] = {
        "file": path.name,
        "expected_name": expected_name,
        "bytes": path.stat().st_size if path.is_file() else None,
        "md5": md5_file(path) if path.is_file() else None,
        "exact_object": False,
        "physical_rows": 0,
        "parse_errors": 0,
        "corrupt_error_class": None,
        "message_types": {},
        "segments": [],
        "tickers": {},
    }
    result["exact_object"] = (
        path.is_file()
        and path.name == expected_name
        and result["bytes"] == expected_size
        and result["md5"] == expected_md5
    )
    if not result["exact_object"]:
        return result
    segments = [new_segment(False)]
    prior: dict[int, int] = {}
    stats: dict[str, dict[str, Any]] = defaultdict(new_ticker_stats)
    message_types: Counter[str] = Counter()
    try:
        with gzip.open(path, "rb") as handle:
            for line in handle:
                result["physical_rows"] += 1
                if b'"ev"' in line and b"recorder_start" in line:
                    segments.append(new_segment(True))
                    prior = {}
                    continue
                segment_index = len(segments) - 1
                sequence = fast_uint(
                    line, b'"seq":', SEQUENCE_PATTERN
                )
                sid = fast_uint(line, b'"sid":', SID_PATTERN)
                if sequence is not None and sid is not None:
                    segment = segments[segment_index]
                    segment["first_by_sid"].setdefault(sid, sequence)
                    before = prior.get(sid)
                    if before is not None and sequence != before + 1:
                        segment["gap_count"] += 1
                    prior[sid] = sequence
                    segment["last_by_sid"][sid] = sequence
                type_value = fast_quoted(
                    line, b'"type":"', TYPE_PATTERN
                )
                message_type = (
                    type_value.decode(
                        "utf-8", errors="replace"
                    )
                    if type_value is not None else ""
                )
                if message_type:
                    message_types[message_type] += 1
                ticker_value = fast_quoted(
                    line, b'"market_ticker":"', TICKER_PATTERN
                )
                if ticker_value is None:
                    continue
                ticker = ticker_value.decode(
                    "utf-8", errors="replace"
                )
                if ticker not in required:
                    continue
                item = stats[ticker]
                item["segments"].add(segment_index)
                timestamp = timestamp_from_line(line)
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
                    result["parse_errors"] += 1
                    continue
                wrapper = row.get("m")
                message = (
                    wrapper.get("msg")
                    if isinstance(wrapper, dict) else None
                )
                if not isinstance(message, dict):
                    continue
                if message_type == "orderbook_snapshot":
                    item["snapshot_rows"] += 1
                    if snapshot_has_ladder(message):
                        item["full_snapshot_rows"] += 1
                        item["full_snapshot_segments"].add(segment_index)
                elif message_type == "trade":
                    item["trade_rows"] += 1
                    item["positive_trade_rows"] += (
                        finite(
                            message.get(
                                "count_fp", message.get("count")
                            )
                        ) > 0
                    )
                elif message_type == "market_lifecycle_v2":
                    status = str(message.get("status") or "")
                    event_type = str(message.get("event_type") or "")
                    if status in {"live", "P"} or event_type in {
                        "market_started", "live", "in_play"
                    }:
                        item["live_transition_rows"] += 1
                        outer = parse_epoch(row.get("t"))
                        transition = timestamp or outer
                        if (
                            transition is not None
                            and (
                                item["first_live_transition"] is None
                                or transition
                                < item["first_live_transition"]
                            )
                        ):
                            item["first_live_transition"] = transition
                            item["first_live_transition_basis"] = (
                                "exchange_payload_timestamp"
                                if timestamp is not None
                                else "local_ws_recorder_receipt_utc"
                            )
    except (OSError, EOFError, gzip.BadGzipFile, zlib.error) as exc:
        result["corrupt_error_class"] = type(exc).__name__
    result["message_types"] = dict(message_types)
    result["segments"] = segments
    result["tickers"] = {
        ticker: {
            **item,
            "segments": sorted(item["segments"]),
            "full_snapshot_segments": sorted(
                item["full_snapshot_segments"]
            ),
        }
        for ticker, item in stats.items()
    }
    return result


def read_events(path: Path) -> set[str]:
    tickers = set()
    events = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            events += 1
            for leg in row.get("legs") or []:
                tickers.add(str(leg.get("ticker") or ""))
    if events != 804 or len(tickers) != 1608 or "" in tickers:
        raise WsCensusError(
            f"immutable event/ticker grain changed: {events}/{len(tickers)}"
        )
    return tickers


def manifest_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("prefix") == "ws_depth":
                rows.append(row)
    if len(rows) != 215:
        raise WsCensusError(
            f"immutable ws_depth object count changed: {len(rows)}"
        )
    return sorted(rows, key=lambda row: str(row["path"]))


def merge_results(
    results: list[dict[str, Any]],
    required: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    aggregate: dict[str, dict[str, Any]] = defaultdict(new_ticker_stats)
    message_types: Counter[str] = Counter()
    epoch_complete: dict[int, bool] = {}
    epoch_gaps: Counter[int] = Counter()
    current_epoch = -1
    prior_by_sid: dict[int, int] = {}
    physical = 0
    parse_errors = 0
    corrupt_files = []
    for file_index, result in enumerate(results):
        physical += int(result["physical_rows"])
        parse_errors += int(result["parse_errors"])
        message_types.update(result["message_types"])
        if result.get("corrupt_error_class"):
            corrupt_files.append({
                "file": result["file"],
                "error_class": result["corrupt_error_class"],
            })
        local_to_global: dict[int, int] = {}
        for local_index, segment in enumerate(result["segments"]):
            starts_new = (
                current_epoch < 0
                or segment["started_by_recorder"] is True
            )
            if starts_new:
                current_epoch += 1
                prior_by_sid = {}
                epoch_complete[current_epoch] = bool(
                    segment["started_by_recorder"]
                )
            local_to_global[local_index] = current_epoch
            epoch_gaps[current_epoch] += int(segment["gap_count"])
            for sid, first in segment["first_by_sid"].items():
                sid = int(sid)
                before = prior_by_sid.get(sid)
                if before is not None and int(first) != before + 1:
                    epoch_gaps[current_epoch] += 1
            for sid, last in segment["last_by_sid"].items():
                prior_by_sid[int(sid)] = int(last)
        if result.get("corrupt_error_class") and current_epoch >= 0:
            epoch_gaps[current_epoch] += 1
        for ticker, item in result["tickers"].items():
            if ticker not in required:
                raise WsCensusError(
                    f"worker emitted ticker outside D: {ticker}"
                )
            target = aggregate[ticker]
            for field in (
                "delta_rows", "trade_rows", "positive_trade_rows",
                "snapshot_rows", "full_snapshot_rows",
                "live_transition_rows",
            ):
                target[field] += int(item[field])
            for field, reducer in (
                ("first_exchange", min),
                ("last_exchange", max),
                ("first_live_transition", min),
            ):
                value = item.get(field)
                if value is not None:
                    target[field] = (
                        value if target[field] is None
                        else reducer(target[field], value)
                    )
            if (
                item.get("first_live_transition") is not None
                and target["first_live_transition"]
                == item["first_live_transition"]
            ):
                target["first_live_transition_basis"] = item.get(
                    "first_live_transition_basis"
                )
            target["segments"].update(
                local_to_global[value] for value in item["segments"]
            )
            target["full_snapshot_segments"].update(
                local_to_global[value]
                for value in item["full_snapshot_segments"]
            )
    output = {}
    for ticker in sorted(required):
        item = aggregate[ticker]
        valid_epochs = [
            epoch for epoch in item["segments"]
            if epoch_complete.get(epoch, False)
            and epoch_gaps[epoch] == 0
            and epoch in item["full_snapshot_segments"]
        ]
        output[ticker] = {
            "available": bool(item["segments"]),
            "orderbook_delta_rows": item["delta_rows"],
            "trade_rows": item["trade_rows"],
            "positive_size_trade_rows": item["positive_trade_rows"],
            "snapshot_rows": item["snapshot_rows"],
            "snapshot_rows_with_ladders": item["full_snapshot_rows"],
            "first_exchange_ts": iso_utc(item["first_exchange"]),
            "last_exchange_ts": iso_utc(item["last_exchange"]),
            "epoch_count": len(item["segments"]),
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
    summary = {
        "file_count": len(results),
        "bytes": sum(int(row["bytes"] or 0) for row in results),
        "physical_rows": physical,
        "parse_errors": parse_errors,
        "corrupt_files": corrupt_files,
        "epoch_count": current_epoch + 1,
        "epoch_gap_count": sum(epoch_gaps.values()),
        "epochs_with_gaps": sum(
            value > 0 for value in epoch_gaps.values()
        ),
        "complete_start_epochs": sum(epoch_complete.values()),
        "message_types": dict(message_types),
        "required_ticker_count": len(output),
        "required_tickers_with_full_depth": sum(
            row["full_depth_usable"] for row in output.values()
        ),
        "all_objects_exact": all(
            row["exact_object"] for row in results
        ),
        "all_archives_readable": not corrupt_files,
    }
    return output, summary


def run(args: argparse.Namespace) -> int:
    events_path = Path(args.events).resolve()
    manifest_path = Path(args.object_manifest).resolve()
    directory = Path(args.ws_depth_dir).resolve()
    ledger_path = Path(args.ledger_output).resolve()
    summary_path = Path(args.summary_output).resolve()
    required = read_events(events_path)
    manifest = manifest_rows(manifest_path)
    tasks = []
    for row in manifest:
        name = Path(str(row["path"])).name
        tasks.append((
            str(directory / name),
            str((row.get("content_hashes") or {}).get("md5") or ""),
            int(row.get("size_bytes") or -1),
            name,
            required,
        ))
    # Largest-first dynamic scheduling avoids leaving one multi-million-row
    # hour as the serial tail after smaller archives have drained.
    tasks.sort(key=lambda task: task[2], reverse=True)
    results = []
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=args.workers
    ) as executor:
        futures = [
            executor.submit(scan_file, task) for task in tasks
        ]
        for index, future in enumerate(
            concurrent.futures.as_completed(futures), 1
        ):
            results.append(future.result())
            if index == 1 or index % 12 == 0 or index == len(futures):
                print(
                    f"ws_files={index}/{len(futures)}",
                    flush=True,
                )
    by_name = {row["file"]: row for row in results}
    results = [by_name[Path(str(row["path"])).name] for row in manifest]
    output, summary = merge_results(results, required)
    if not summary["all_objects_exact"]:
        raise WsCensusError("one or more WS objects failed size/hash proof")
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8", newline="\n") as handle:
        for ticker, row in sorted(output.items()):
            handle.write(json.dumps({
                "schema_version": VERSION,
                "ticker": ticker,
                **row,
            }, sort_keys=True, separators=(",", ":")) + "\n")
    receipt = {
        "schema_version": VERSION,
        "D": 804,
        "required_tickers": 1608,
        "source_object_manifest_sha256": sha256_file(manifest_path),
        "events_sha256": sha256_file(events_path),
        "ledger_sha256": sha256_file(ledger_path),
        "ws_depth": summary,
        "source_law": (
            "RAW_WS_DELTA unless a non-empty ladder snapshot precedes "
            "deltas inside a recorder-started, gap-free sequence epoch"
        ),
        "privacy": {
            "credentials_or_account_data_emitted": False,
            "raw_archives_outside_git": True,
        },
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "ticker_count": len(output),
        "ledger_sha256": receipt["ledger_sha256"],
        "ws_depth": summary,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--object-manifest", required=True)
    result.add_argument("--ws-depth-dir", required=True)
    result.add_argument("--workers", type=int, default=8)
    result.add_argument("--ledger-output", required=True)
    result.add_argument("--summary-output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
