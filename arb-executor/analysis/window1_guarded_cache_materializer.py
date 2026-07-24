#!/usr/bin/env python3
"""Materialize guarded Window-1 market evidence without scoring policies.

The prior causal-fit cache remains useful when it spans the corrected guarded
right edge.  Events whose right edge moved are rebuilt from the frozen public
print tape and the causal top-five recorder files.  This program never imports
or evaluates candidate policies.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

import window1_fit_benchmark as fit
from window1_start_guard import strict_positive_cutoff


VERSION = "window1-guarded-event-market-cache-v3"
UTC = dt.timezone.utc
EXPECTED_D = 804


class MaterializationError(RuntimeError):
    """The evidence cache could not be materialized lawfully."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise MaterializationError(
                    f"JSON object required: {path}:{line_number}"
                )
            rows.append(row)
    return rows


def read_cache(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise MaterializationError(f"cache object required: {path}")
    return value


def write_cache(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0
        ) as zipped:
            zipped.write((compact(value) + "\n").encode())
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def source_receipt(path: Path) -> dict[str, Any]:
    files = sorted(path.glob("*.json.gz"), key=lambda item: item.name)
    if len(files) != EXPECTED_D:
        raise MaterializationError(
            f"base cache count changed: {len(files)}"
        )
    rows = [{
        "name": item.name,
        "bytes": item.stat().st_size,
        "sha256": sha256_file(item),
    } for item in files]
    return {
        "files": len(rows),
        "bytes": sum(row["bytes"] for row in rows),
        "hash_set_sha256": hashlib.sha256(
            compact(rows).encode()
        ).hexdigest(),
    }


def validate_print(
    row: Mapping[str, Any],
    ticker: str,
    seen: dict[str, tuple[Any, ...]],
) -> dict[str, Any] | None:
    identity = str(
        row.get("trade_id") or row.get("receipt_id") or ""
    )
    if (
        not identity
        or row.get("ticker") != ticker
        or row.get("true_print") is not True
    ):
        raise MaterializationError(
            f"invalid true print in frozen tape: {ticker}"
        )
    timestamp = fit.parse_utc(
        row.get("exchange_ts"), "print.exchange_ts"
    )
    price = int(row.get("price_cents"))
    size = fit.finite_number(row.get("size"), 0)
    if not 1 <= price <= 99 or size < 0:
        raise MaterializationError(
            f"invalid print price/size: {ticker}:{identity}"
        )
    canonical = (
        ticker, timestamp, price, size, row.get("taker_side")
    )
    prior = seen.get(identity)
    if prior is not None and prior != canonical:
        raise MaterializationError(
            f"conflicting trade identity: {identity}"
        )
    if prior is not None:
        return None
    seen[identity] = canonical
    return {
        "trade_id": identity,
        "ts": timestamp,
        "price": price,
        "size": size,
        "taker_side": str(row.get("taker_side") or ""),
    }


def run(args: argparse.Namespace) -> int:
    events_path = Path(args.events).resolve()
    starts_path = Path(args.start_ledger).resolve()
    prints_path = Path(args.prints).resolve()
    base_root = Path(args.base_cache).resolve()
    ticks_root = Path(args.top5).resolve()
    output_root = Path(args.output).resolve()
    if output_root.exists():
        raise MaterializationError(
            f"refusing to overwrite cache directory: {output_root}"
        )
    print(compact({
        "stage": "verify_public_tape_hash",
        "bytes": prints_path.stat().st_size,
    }), flush=True)
    if sha256_file(prints_path) != args.expected_print_sha256:
        raise MaterializationError("normalized public print hash changed")
    print(compact({
        "stage": "public_tape_hash_verified",
        "sha256": args.expected_print_sha256,
    }), flush=True)

    events = fit.load_events(events_path)
    starts_rows = read_jsonl(starts_path)
    starts = {str(row["event_id"]): row for row in starts_rows}
    if len(starts) != EXPECTED_D:
        raise MaterializationError("corrected start ledger D changed")
    print(compact({"stage": "verify_base_cache"}), flush=True)
    base_receipt = source_receipt(base_root)
    print(compact({
        "stage": "base_cache_verified",
        **base_receipt,
    }), flush=True)

    desired: dict[str, tuple[float, float]] = {}
    rebuild_ids: set[str] = set()
    ticker_bounds: dict[str, tuple[float, float]] = {}
    for event in events:
        event_id = str(event["event_id"])
        path = base_root / f"{event_id}.json.gz"
        payload = read_cache(path)
        if payload.get("event_id") != event_id:
            raise MaterializationError(
                f"base cache event mismatch: {event_id}"
            )
        scheduled = fit.parse_utc(
            event["scheduled_start_exchange_ts"],
            "scheduled_start_exchange_ts",
        )
        cutoff = strict_positive_cutoff(starts[event_id])
        left = scheduled - 8 * 3600
        if cutoff is None:
            desired[event_id] = (
                fit.parse_utc(payload["earliest_utc"], "earliest_utc"),
                fit.parse_utc(payload["latest_utc"], "latest_utc"),
            )
            continue
        earliest = left - 301
        latest = cutoff + 301
        desired[event_id] = (earliest, latest)
        base_earliest = fit.parse_utc(
            payload["earliest_utc"], "earliest_utc"
        )
        base_latest = fit.parse_utc(
            payload["latest_utc"], "latest_utc"
        )
        if base_earliest > left or base_latest < cutoff:
            rebuild_ids.add(event_id)
            for leg in event["legs"]:
                ticker = str(leg["ticker"])
                ticker_bounds[ticker] = (earliest, latest)

    print(
        compact({
            "stage": "extension_plan",
            "D": len(events),
            "events_rebuilt": len(rebuild_ids),
            "tickers_rebuilt": len(ticker_bounds),
        }),
        flush=True,
    )

    prints_by_ticker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_by_ticker: dict[str, dict[str, tuple[Any, ...]]] = defaultdict(dict)
    with prints_path.open("rb") as handle:
        for line_number, raw in enumerate(handle, 1):
            ticker = fit.PrintArchive._ticker(raw, line_number)
            bounds = ticker_bounds.get(ticker)
            if bounds is not None:
                row = json.loads(raw)
                parsed = validate_print(
                    row, ticker, seen_by_ticker[ticker]
                )
                if (
                    parsed is not None
                    and
                    bounds[0] <= float(parsed["ts"]) <= bounds[1]
                ):
                    prints_by_ticker[ticker].append(parsed)
            if line_number % 2_000_000 == 0:
                print(
                    compact({
                        "stage": "public_tape_scan",
                        "physical_rows": line_number,
                    }),
                    flush=True,
                )
    for rows in prints_by_ticker.values():
        rows.sort(key=lambda row: (row["ts"], row["trade_id"]))

    cache_key = hashlib.sha256(compact({
        "version": VERSION,
        "events_sha256": sha256_file(events_path),
        "start_ledger_sha256": sha256_file(starts_path),
        "prints_sha256": args.expected_print_sha256,
        "base_cache_hash_set_sha256": (
            base_receipt["hash_set_sha256"]
        ),
        "rebuilt_event_ids": sorted(rebuild_ids),
    }).encode()).hexdigest()

    for index, event in enumerate(events, 1):
        event_id = str(event["event_id"])
        earliest, latest = desired[event_id]
        base = read_cache(base_root / f"{event_id}.json.gz")
        if event_id in rebuild_ids:
            legs = []
            for leg in event["legs"]:
                ticker = str(leg["ticker"])
                top5_path = ticks_root / f"{ticker}.csv.gz"
                legs.append({
                    "ticker": ticker,
                    "leg": leg.get("leg"),
                    "snapshots": fit.load_top5(
                        top5_path, ticker, earliest, latest
                    ),
                    "prints": prints_by_ticker.get(ticker, []),
                })
        else:
            legs = base["legs"]
            earliest = fit.parse_utc(
                base["earliest_utc"], "earliest_utc"
            )
            latest = fit.parse_utc(
                base["latest_utc"], "latest_utc"
            )
        write_cache(output_root / f"{event_id}.json.gz", {
            "cache_version": VERSION,
            "cache_key": cache_key,
            "event_id": event_id,
            "earliest_utc": dt.datetime.fromtimestamp(
                earliest, UTC
            ).isoformat(),
            "latest_utc": dt.datetime.fromtimestamp(
                latest, UTC
            ).isoformat(),
            "legs": legs,
        })
        if index % 100 == 0:
            print(
                compact({
                    "stage": "cache_write",
                    "events_written": index,
                }),
                flush=True,
            )

    print(compact({
        "stage": "complete",
        "cache_key": cache_key,
        "events": len(events),
        "events_rebuilt": len(rebuild_ids),
        "tickers_rebuilt": len(ticker_bounds),
        "base_cache_receipt": base_receipt,
    }), flush=True)
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--start-ledger", required=True)
    result.add_argument("--prints", required=True)
    result.add_argument("--expected-print-sha256", required=True)
    result.add_argument("--base-cache", required=True)
    result.add_argument("--top5", required=True)
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
