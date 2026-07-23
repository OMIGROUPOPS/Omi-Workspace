#!/usr/bin/env python3
"""Build a sanitized immutable manifest for Window-1 Spaces objects.

The caller produces read-only `rclone lsjson --recursive --hash` receipts.
This tool performs no network requests and emits no credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


D = 804
REQUIRED_TICKERS = 1608
VERSION = "window1-spaces-object-manifest-v1"


class ManifestError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    output = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ManifestError(f"non-object {path}:{line_number}")
            output.append(row)
    return output


def load_lsjson(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or any(
        not isinstance(row, dict) for row in value
    ):
        raise ManifestError(f"rclone lsjson array required: {path}")
    return value


def ticker_from_path(value: Any) -> str:
    name = Path(str(value or "")).name
    for suffix in (".csv.gz", ".csv"):
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return ""


def canonical_object(prefix: str, row: dict[str, Any]) -> dict[str, Any]:
    path = str(row.get("Path") or row.get("Name") or "")
    hashes = row.get("Hashes") or {}
    if not isinstance(hashes, dict):
        hashes = {}
    return {
        "source": "spaces:omi-tick-archive",
        "prefix": prefix,
        "path": prefix + "/" + path.lstrip("/"),
        "size_bytes": int(row.get("Size") or 0),
        "modified_utc": row.get("ModTime"),
        "content_hashes": {
            str(key).lower(): str(value)
            for key, value in sorted(hashes.items())
            if value not in (None, "")
        },
        "mime_type": row.get("MimeType"),
        "tier": row.get("Tier"),
    }


def run(args: argparse.Namespace) -> int:
    events_path = Path(args.events).resolve()
    events = read_jsonl(events_path)
    if len(events) != D:
        raise ManifestError(f"immutable D changed: {len(events)}")
    event_for_ticker = {}
    for event in events:
        for leg in event.get("legs") or []:
            ticker = str(leg.get("ticker") or "")
            if not ticker or ticker in event_for_ticker:
                raise ManifestError(f"duplicate/missing ticker: {ticker}")
            event_for_ticker[ticker] = str(event["event_id"])
    required = set(event_for_ticker)
    if len(required) != REQUIRED_TICKERS:
        raise ManifestError(
            f"required ticker count changed: {len(required)}"
        )
    input_paths = {
        "ticks": Path(args.ticks_lsjson).resolve(),
        "trades": Path(args.trades_lsjson).resolve(),
        "ws_depth": Path(args.ws_depth_lsjson).resolve(),
    }
    selected: dict[str, list[dict[str, Any]]] = defaultdict(list)
    ticker_sources: dict[str, set[str]] = defaultdict(set)
    for prefix in ("ticks", "trades"):
        for row in load_lsjson(input_paths[prefix]):
            ticker = ticker_from_path(row.get("Path") or row.get("Name"))
            if ticker not in required:
                continue
            item = canonical_object(prefix, row)
            item.update({
                "event_id": event_for_ticker[ticker],
                "ticker": ticker,
                "source_class": (
                    ["BBO", "TOP5_DEPTH"] if prefix == "ticks"
                    else ["PUBLIC_WS_PRINT_ARCHIVE"]
                ),
            })
            selected[prefix].append(item)
            ticker_sources[ticker].add(prefix)
    for row in load_lsjson(input_paths["ws_depth"]):
        name = Path(str(row.get("Path") or row.get("Name") or "")).name
        if not (
            name.startswith("ws_202607")
            and "ws_20260712_" <= name <= "ws_20260720_zz"
        ):
            continue
        item = canonical_object("ws_depth", row)
        item.update({
            "event_id": None,
            "ticker": None,
            "source_class": ["RAW_WS_DELTA"],
            "reconstructed_full_depth": False,
            "full_depth_precondition": (
                "requires a ladder-bearing snapshot followed by a "
                "gap-free sequence epoch"
            ),
        })
        selected["ws_depth"].append(item)
    tape_manifest = json.loads(
        Path(args.public_tape_manifest).resolve().read_text(encoding="utf-8")
    )
    pagination = tape_manifest.get("pagination") or {}
    if not (
        pagination.get("all_terminal_cursors_empty") is True
        and pagination.get("failed_ticker_count") == 0
    ):
        raise ManifestError("public-tape pagination is incomplete")
    zero_public = set(
        (tape_manifest.get("coverage") or {}).get(
            "tickers_with_zero_trades", []
        )
    )
    missing_trade_tickers = sorted(
        ticker for ticker in required
        if "trades" not in ticker_sources[ticker]
    )
    print_absence = [{
        "event_id": event_for_ticker[ticker],
        "ticker": ticker,
        "spaces_trade_object_present": False,
        "complete_public_endpoint_has_trades": ticker not in zero_public,
        "ruling": (
            "spaces_trade_archive_ingestion_gap"
            if ticker not in zero_public
            else "genuinely_zero_trade_after_complete_public_pagination"
        ),
    } for ticker in missing_trade_tickers]
    all_objects = (
        sorted(selected["ticks"], key=lambda row: row["path"])
        + sorted(selected["trades"], key=lambda row: row["path"])
        + sorted(selected["ws_depth"], key=lambda row: row["path"])
    )
    ledger_path = Path(args.ledger_output).resolve()
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in all_objects:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")
    absence_path = Path(args.print_absence_output).resolve()
    with absence_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in print_absence:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")
    ticks_tickers = {
        row["ticker"] for row in selected["ticks"]
    }
    trades_tickers = {
        row["ticker"] for row in selected["trades"]
    }
    event_tick_coverage = Counter(
        event_for_ticker[ticker] for ticker in ticks_tickers
    )
    summary = {
        "schema_version": VERSION,
        "D": D,
        "required_tickers": REQUIRED_TICKERS,
        "source_audit_commit": (
            "ff0f336f45fde9d54ca2948949689172e8203aff"
        ),
        "object_counts": {
            key: len(selected[key])
            for key in ("ticks", "trades", "ws_depth")
        },
        "ticker_counts": {
            "ticks": len(ticks_tickers),
            "trades": len(trades_tickers),
            "missing_spaces_trades": len(missing_trade_tickers),
        },
        "event_counts": {
            "both_legs_ticks": sum(
                event_tick_coverage[event["event_id"]] == 2
                for event in events
            ),
        },
        "print_absence_rulings": dict(Counter(
            row["ruling"] for row in print_absence
        )),
        "source_classes": {
            "ticks": ["BBO", "TOP5_DEPTH"],
            "trades": ["PUBLIC_WS_PRINT_ARCHIVE"],
            "ws_depth": ["RAW_WS_DELTA"],
            "reconstructed_full_depth": (
                "not asserted by the object manifest"
            ),
        },
        "hash_law": (
            "content_hashes are the hashes returned by read-only rclone "
            "lsjson --hash; input receipt files and outputs are SHA-256 pinned"
        ),
        "input_receipts": {
            key: {
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for key, path in input_paths.items()
        },
        "outputs": {
            "object_ledger_sha256": sha256_file(ledger_path),
            "print_absence_sha256": sha256_file(absence_path),
        },
        "events_sha256": sha256_file(events_path),
        "public_tape_manifest_sha256": sha256_file(
            Path(args.public_tape_manifest).resolve()
        ),
        "credentials_or_private_identifiers_in_output": False,
    }
    Path(args.summary_output).resolve().write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "D": D,
        "ticks_tickers": len(ticks_tickers),
        "trades_tickers": len(trades_tickers),
        "both_legs_ticks": summary["event_counts"]["both_legs_ticks"],
        "print_absence_rulings": summary["print_absence_rulings"],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--ticks-lsjson", required=True)
    result.add_argument("--trades-lsjson", required=True)
    result.add_argument("--ws-depth-lsjson", required=True)
    result.add_argument("--public-tape-manifest", required=True)
    result.add_argument("--ledger-output", required=True)
    result.add_argument("--print-absence-output", required=True)
    result.add_argument("--summary-output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
