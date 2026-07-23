#!/usr/bin/env python3
"""Export a complete, exchange-trade-identified public tape for Window-1.

The exporter is deliberately unauthenticated.  It reads the immutable event
catalog, queries each required leg ticker independently, follows every cursor,
and writes both the raw endpoint responses and one canonical true-print file
outside Git.  The companion manifest contains hashes and completeness counts
but no private account data.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
import os
import random
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


EXPORT_VERSION = "window1-public-tape-v1"
DEFAULT_ENDPOINT = (
    "https://api.elections.kalshi.com/trade-api/v2/markets/trades"
)


class ExportError(RuntimeError):
    """A fail-closed public-tape export error."""


def json_compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_iso_utc(value: Any, field: str) -> tuple[float, str]:
    text = str(value or "").strip().replace("Z", "+00:00")
    if not text:
        raise ExportError(f"missing {field}")
    try:
        stamp = dt.datetime.fromisoformat(text)
    except ValueError as exc:
        raise ExportError(f"invalid {field}: {value!r}") from exc
    if stamp.tzinfo is None:
        raise ExportError(f"timezone-free {field}: {value!r}")
    stamp = stamp.astimezone(dt.timezone.utc)
    return stamp.timestamp(), stamp.isoformat().replace("+00:00", "Z")


def dollars_to_cents(value: Any, field: str) -> int:
    try:
        cents = int(round(float(value) * 100))
    except (TypeError, ValueError) as exc:
        raise ExportError(f"invalid {field}: {value!r}") from exc
    if not 1 <= cents <= 99:
        raise ExportError(f"out-of-range {field}: {value!r}")
    return cents


def nonnegative_size(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    try:
        size = float(value)
    except (TypeError, ValueError) as exc:
        raise ExportError(f"invalid count_fp: {value!r}") from exc
    if size < 0 or size != size or size == float("inf"):
        raise ExportError(f"invalid count_fp: {value!r}")
    return size


def canonical_trade(row: Mapping[str, Any], requested_ticker: str) -> dict[str, Any]:
    identity = str(row.get("trade_id") or "").strip()
    if not identity:
        raise ExportError("public trade lacks trade_id")
    ticker = str(row.get("ticker") or "").strip()
    if ticker != requested_ticker:
        raise ExportError(
            f"ticker mismatch: requested={requested_ticker} returned={ticker}"
        )
    _, exchange_ts = parse_iso_utc(row.get("created_time"), "created_time")
    if row.get("yes_price_dollars") not in (None, ""):
        price = dollars_to_cents(row.get("yes_price_dollars"),
                                 "yes_price_dollars")
    else:
        try:
            price = int(row.get("yes_price"))
        except (TypeError, ValueError) as exc:
            raise ExportError("public trade lacks a valid YES price") from exc
        if not 1 <= price <= 99:
            raise ExportError(f"out-of-range yes_price: {price}")
    size = nonnegative_size(
        row.get("count_fp") if "count_fp" in row else row.get("count")
    )
    return {
        "receipt_id": identity,
        "trade_id": identity,
        "ticker": ticker,
        "exchange_ts": exchange_ts,
        "price_cents": price,
        "size": size,
        "source": "kalshi_public_trade",
        "true_print": True,
        "taker_side": row.get("taker_side"),
        "taker_outcome_side": row.get("taker_outcome_side"),
        "taker_book_side": row.get("taker_book_side"),
        "is_block_trade": bool(row.get("is_block_trade", False)),
    }


def load_tickers(events_path: Path) -> tuple[list[str], dict[str, str]]:
    tickers: set[str] = set()
    ticker_days: dict[str, str] = {}
    event_count = 0
    with events_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ExportError(
                    f"malformed event JSONL line {line_number}: {exc}"
                ) from exc
            event_count += 1
            day = str(row.get("event_date") or "")
            legs = row.get("legs")
            if not isinstance(legs, list) or len(legs) != 2:
                raise ExportError(
                    f"event {row.get('event_id')} does not have two legs"
                )
            for leg in legs:
                ticker = str((leg or {}).get("ticker") or "").strip()
                if not ticker:
                    raise ExportError(
                        f"event {row.get('event_id')} has a missing ticker"
                    )
                if ticker in ticker_days and ticker_days[ticker] != day:
                    raise ExportError(f"ticker reused across event dates: {ticker}")
                tickers.add(ticker)
                ticker_days[ticker] = day
    if event_count != 804 or len(tickers) != 1608:
        raise ExportError(
            f"immutable denominator violated: events={event_count}, "
            f"tickers={len(tickers)}"
        )
    return sorted(tickers), ticker_days


def request_json(
    url: str,
    *,
    attempts: int,
    timeout_seconds: float,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": f"omi-window1-research/{EXPORT_VERSION}",
            },
            method="GET",
        )
        try:
            with opener(request, timeout=timeout_seconds) as response:
                payload = response.read()
                value = json.loads(payload)
                if not isinstance(value, dict):
                    raise ExportError("endpoint returned non-object JSON")
                return value
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                json.JSONDecodeError, ExportError) as exc:
            last_error = exc
            retryable = not isinstance(exc, urllib.error.HTTPError) or (
                exc.code == 429 or 500 <= exc.code < 600
            )
            if not retryable or attempt + 1 == attempts:
                break
            retry_after = None
            if isinstance(exc, urllib.error.HTTPError):
                retry_after = exc.headers.get("Retry-After")
            delay = (
                float(retry_after)
                if retry_after and retry_after.replace(".", "", 1).isdigit()
                else min(20.0, (2 ** attempt) + random.random())
            )
            time.sleep(delay)
    raise ExportError(f"GET failed after {attempts} attempts: {last_error}")


def fetch_ticker(
    ticker: str,
    endpoint: str,
    raw_dir: Path,
    *,
    page_limit: int,
    attempts: int,
    timeout_seconds: float,
    resume: bool,
) -> dict[str, Any]:
    raw_path = raw_dir / f"{ticker}.json.gz"
    if resume and raw_path.is_file():
        try:
            with gzip.open(raw_path, "rt", encoding="utf-8") as handle:
                raw_pages = json.load(handle)
            if not isinstance(raw_pages, list) or not raw_pages:
                raise ExportError("resumed raw file has no pages")
            trade_count = 0
            zero_size_count = 0
            for expected_page, page in enumerate(raw_pages, 1):
                if not isinstance(page, dict) or page.get("page") != expected_page:
                    raise ExportError("resumed raw page numbering is invalid")
                request = page.get("request") or {}
                response = page.get("response") or {}
                if request.get("ticker") != ticker:
                    raise ExportError("resumed raw ticker does not match")
                if not isinstance(response.get("trades"), list):
                    raise ExportError("resumed raw page lacks trades[]")
                for row in response["trades"]:
                    canonical = canonical_trade(row, ticker)
                    trade_count += 1
                    zero_size_count += canonical["size"] == 0
            if str(raw_pages[-1]["response"].get("cursor") or "").strip():
                raise ExportError("resumed raw file lacks terminal empty cursor")
            return {
                "ticker": ticker,
                "trade_count": trade_count,
                "zero_size_count": zero_size_count,
                "page_count": len(raw_pages),
                "terminal_cursor_empty": True,
                "raw_path": raw_path,
                "raw_sha256": sha256_file(raw_path),
                "raw_bytes": raw_path.stat().st_size,
                "resumed": True,
            }
        except (OSError, gzip.BadGzipFile, json.JSONDecodeError,
                ExportError, TypeError, ValueError) as exc:
            raise ExportError(
                f"existing resume artifact failed validation: {exc}"
            ) from exc
    cursor = ""
    page_number = 0
    raw_pages: list[dict[str, Any]] = []
    trades: list[dict[str, Any]] = []
    seen_cursors: set[str] = set()
    while True:
        params = {"ticker": ticker, "limit": str(page_limit)}
        if cursor:
            params["cursor"] = cursor
        url = endpoint + "?" + urllib.parse.urlencode(params)
        payload = request_json(
            url, attempts=attempts, timeout_seconds=timeout_seconds
        )
        page_number += 1
        page_trades = payload.get("trades")
        if not isinstance(page_trades, list):
            raise ExportError(f"{ticker} page {page_number} lacks trades[]")
        canonical = [canonical_trade(row, ticker) for row in page_trades]
        trades.extend(canonical)
        next_cursor = str(payload.get("cursor") or "").strip()
        raw_pages.append({
            "page": page_number,
            "request": {
                "ticker": ticker,
                "limit": page_limit,
                "cursor": cursor,
            },
            "response": payload,
        })
        if not next_cursor:
            break
        if next_cursor in seen_cursors or next_cursor == cursor:
            raise ExportError(f"{ticker} cursor loop at page {page_number}")
        seen_cursors.add(next_cursor)
        cursor = next_cursor
    with gzip.open(raw_path, "wt", encoding="utf-8", newline="\n") as handle:
        json.dump(raw_pages, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")
    os.chmod(raw_path, stat.S_IRUSR | stat.S_IWUSR)
    return {
        "ticker": ticker,
        "trade_count": len(trades),
        "zero_size_count": sum(row["size"] == 0 for row in trades),
        "page_count": page_number,
        "terminal_cursor_empty": True,
        "raw_path": raw_path,
        "raw_sha256": sha256_file(raw_path),
        "raw_bytes": raw_path.stat().st_size,
        "resumed": False,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def verify_duplicate_rows(
    results: Iterable[Mapping[str, Any]],
    duplicate_identities: set[str],
) -> None:
    """Re-scan only when duplicate IDs exist and prove identical payloads."""
    if not duplicate_identities:
        return
    canonical_by_identity: dict[str, str] = {}
    for result in results:
        with gzip.open(
            result["raw_path"], "rt", encoding="utf-8"
        ) as raw_handle:
            for page in json.load(raw_handle):
                for raw_trade in page["response"]["trades"]:
                    identity = str(raw_trade.get("trade_id") or "")
                    if identity not in duplicate_identities:
                        continue
                    canonical_line = json_compact(
                        canonical_trade(raw_trade, result["ticker"])
                    )
                    prior = canonical_by_identity.setdefault(
                        identity, canonical_line
                    )
                    if prior != canonical_line:
                        raise ExportError(
                            f"conflicting duplicate trade_id: {identity}"
                        )


def run(args: argparse.Namespace) -> int:
    events_path = Path(args.events).resolve()
    raw_dir = Path(args.raw_dir).resolve()
    normalized_path = Path(args.normalized_output).resolve()
    manifest_path = Path(args.manifest_output).resolve()
    tickers, ticker_days = load_tickers(events_path)
    raw_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(raw_dir, stat.S_IRWXU)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(normalized_path.parent, stat.S_IRWXU)

    results: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.workers
    ) as executor:
        futures = {
            executor.submit(
                fetch_ticker,
                ticker,
                args.endpoint,
                raw_dir,
                page_limit=args.page_limit,
                attempts=args.attempts,
                timeout_seconds=args.timeout_seconds,
                resume=args.resume,
            ): ticker
            for ticker in tickers
        }
        for completed, future in enumerate(
            concurrent.futures.as_completed(futures), 1
        ):
            ticker = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # the manifest must retain every failure
                failures.append({"ticker": ticker, "error": str(exc)})
            if completed % 100 == 0 or completed == len(tickers):
                print(
                    f"completed={completed}/{len(tickers)} "
                    f"failures={len(failures)}",
                    flush=True,
                )

    if failures:
        failure_path = manifest_path.with_name(
            manifest_path.stem + ".failures.json"
        )
        write_json(failure_path, {
            "export_version": EXPORT_VERSION,
            "failures": failures,
        })
        raise ExportError(
            f"public tape export incomplete: {len(failures)} ticker failures"
        )

    # Exact UUID integers avoid retaining millions of duplicate Python UUID
    # strings.  Duplicate payload comparison is deferred to a second pass
    # only if an exact UUID recurs.
    by_identity: set[int] = set()
    duplicate_identities: set[str] = set()
    duplicate_rows = 0
    canonical_count = 0
    zero_size_count = 0
    first_timestamp: float | None = None
    last_timestamp: float | None = None
    with normalized_path.open("w", encoding="utf-8", newline="\n") as handle:
        for result in sorted(results, key=lambda item: item["ticker"]):
            with gzip.open(
                result["raw_path"], "rt", encoding="utf-8"
            ) as raw_handle:
                raw_pages = json.load(raw_handle)
            for page in raw_pages:
                for raw_trade in page["response"]["trades"]:
                    row = canonical_trade(raw_trade, result["ticker"])
                    identity = row["trade_id"]
                    try:
                        identity_key = uuid.UUID(identity).int
                    except ValueError as exc:
                        raise ExportError(
                            f"non-UUID public trade_id: {identity}"
                        ) from exc
                    canonical_line = json_compact(row)
                    if identity_key in by_identity:
                        duplicate_identities.add(identity)
                        duplicate_rows += 1
                        continue
                    by_identity.add(identity_key)
                    handle.write(canonical_line + "\n")
                    canonical_count += 1
                    zero_size_count += row["size"] == 0
                    timestamp, _ = parse_iso_utc(
                        row["exchange_ts"], "exchange_ts"
                    )
                    first_timestamp = (
                        timestamp if first_timestamp is None
                        else min(first_timestamp, timestamp)
                    )
                    last_timestamp = (
                        timestamp if last_timestamp is None
                        else max(last_timestamp, timestamp)
                    )
    os.chmod(normalized_path, stat.S_IRUSR | stat.S_IWUSR)
    verify_duplicate_rows(results, duplicate_identities)

    per_day = Counter(ticker_days[result["ticker"]] for result in results)
    records_per_event_day = Counter()
    for result in results:
        records_per_event_day[ticker_days[result["ticker"]]] += int(
            result["trade_count"]
        )
    manifest = {
        "export_version": EXPORT_VERSION,
        "exported_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "endpoint": args.endpoint,
        "authentication": "none_public_endpoint",
        "immutable_denominator": {
            "D": 804,
            "required_leg_tickers": len(tickers),
            "event_ledger_sha256": sha256_file(events_path),
        },
        "pagination": {
            "limit": args.page_limit,
            "ticker_queries": len(results),
            "page_count": sum(row["page_count"] for row in results),
            "all_terminal_cursors_empty": all(
                row["terminal_cursor_empty"] for row in results
            ),
            "failed_ticker_count": 0,
            "resumed_ticker_count": sum(
                bool(row["resumed"]) for row in results
            ),
            "newly_queried_ticker_count": sum(
                not row["resumed"] for row in results
            ),
        },
        "records": {
            "raw_rows_before_receipt_dedup": sum(
                int(row["trade_count"]) for row in results
            ),
            "canonical_true_print_rows": canonical_count,
            "exact_duplicate_rows_removed": duplicate_rows,
            "zero_size_rows_retained_as_zero": zero_size_count,
            "ticker_query_counts_by_event_day": dict(sorted(per_day.items())),
            "trade_rows_by_event_day": dict(
                sorted(records_per_event_day.items())
            ),
        },
        "coverage": {
            "first_exchange_ts": (
                dt.datetime.fromtimestamp(first_timestamp, dt.timezone.utc)
                .isoformat() if first_timestamp is not None else None
            ),
            "last_exchange_ts": (
                dt.datetime.fromtimestamp(last_timestamp, dt.timezone.utc)
                .isoformat() if last_timestamp is not None else None
            ),
            "tickers_with_zero_trades": sorted(
                row["ticker"] for row in results
                if int(row["trade_count"]) == 0
            ),
        },
        "artifacts": {
            "normalized_true_prints": {
                "sha256": sha256_file(normalized_path),
                "bytes": normalized_path.stat().st_size,
            },
            "raw_ticker_file_count": len(results),
            "raw_total_bytes": sum(row["raw_bytes"] for row in results),
            "raw_hash_set_sha256": hashlib.sha256(
                "\n".join(
                    f'{row["ticker"]} {row["raw_sha256"]}'
                    for row in sorted(results, key=lambda item: item["ticker"])
                ).encode("utf-8")
            ).hexdigest(),
        },
        "contract": {
            "true_print_identity": "trade_id",
            "exchange_clock": "created_time",
            "size": "count_fp_or_count; zero_or_missing_is_zero",
            "economic_direction": "YES price cents",
            "synthetic_transitions_accepted": False,
        },
    }
    write_json(manifest_path, manifest)
    print(json.dumps({
        "ticker_count": len(tickers),
        "page_count": manifest["pagination"]["page_count"],
        "true_print_rows": canonical_count,
        "zero_trade_tickers": len(
            manifest["coverage"]["tickers_with_zero_trades"]
        ),
        "manifest": str(manifest_path),
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--raw-dir", required=True)
    result.add_argument("--normalized-output", required=True)
    result.add_argument("--manifest-output", required=True)
    result.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    result.add_argument("--workers", type=int, default=4)
    result.add_argument("--page-limit", type=int, default=1000)
    result.add_argument("--attempts", type=int, default=8)
    result.add_argument("--timeout-seconds", type=float, default=30)
    result.add_argument("--resume", action="store_true")
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
