#!/usr/bin/env python3
"""Causal Window-1 fit benchmark over the immutable July 12-20 denominator.

This runner is intentionally separate from actual-fill validation.  It uses
exchange-trade-identified public prints for execution evidence, top-five
BBO/depth
snapshots for causal placement, optional top-20 snapshots for feature context,
and a fixed pre-July shape prior.  Full depth is never inferred from either
snapshot source.  Same-price queue uncertainty produces lower/upper bounds;
trade-through by a sell-YES taker is exact when public-tape pagination is
complete.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import datetime as dt
import gzip
import hashlib
import json
import math
import os
import sqlite3
import statistics
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo


RUNNER_VERSION = "window1-causal-fit-v1"
D_REQUIRED = 804
LOT = 5.0
PAR = 100.0
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
_CACHE_WORKER_CONTEXT: dict[str, Any] = {}


class FitError(RuntimeError):
    """A fail-closed fit contract violation."""


class PrintArchive:
    """Seekable, ticker-grouped view of the immutable public print JSONL.

    The normalized public export is written one complete ticker query at a
    time.  Building byte ranges keeps the complete hash/completeness contract
    while avoiding a multi-gigabyte in-memory dictionary on the VPS.
    """

    def __init__(self, path: Path, expected_sha256: str) -> None:
        self.path = path
        self.expected_sha256 = expected_sha256
        self.ranges: dict[str, tuple[int, int, int]] = {}
        self.sha256 = ""
        self._index()

    @staticmethod
    def _ticker(raw: bytes, line_number: int) -> str:
        marker = b'"ticker":"'
        start = raw.find(marker)
        if start < 0:
            raise FitError(
                f"public print lacks compact ticker field at row "
                f"{line_number}"
            )
        start += len(marker)
        end = raw.find(b'"', start)
        if end < 0:
            raise FitError(
                f"public print has unterminated ticker at row {line_number}"
            )
        try:
            return raw[start:end].decode("ascii")
        except UnicodeDecodeError as exc:
            raise FitError(
                f"public print ticker is not ASCII at row {line_number}"
            ) from exc

    def _index(self) -> None:
        digest = hashlib.sha256()
        current: str | None = None
        group_start = 0
        group_rows = 0
        closed: set[str] = set()
        line_number = 0
        with self.path.open("rb") as handle:
            while True:
                offset = handle.tell()
                raw = handle.readline()
                if not raw:
                    break
                line_number += 1
                digest.update(raw)
                ticker = self._ticker(raw, line_number)
                if current is None:
                    current = ticker
                    group_start = offset
                    group_rows = 1
                elif ticker == current:
                    group_rows += 1
                else:
                    self.ranges[current] = (
                        group_start, offset, group_rows
                    )
                    closed.add(current)
                    if ticker in closed:
                        raise FitError(
                            "public print archive is not ticker-contiguous: "
                            f"{ticker}"
                        )
                    current = ticker
                    group_start = offset
                    group_rows = 1
            if current is not None:
                self.ranges[current] = (
                    group_start, handle.tell(), group_rows
                )
        self.sha256 = digest.hexdigest()
        if self.sha256 != self.expected_sha256:
            raise FitError("normalized public tape hash mismatch")

    def load(
        self, ticker: str, earliest: float, latest: float,
    ) -> list[dict[str, Any]]:
        byte_range = self.ranges.get(ticker)
        if byte_range is None:
            return []
        start, end, expected_rows = byte_range
        rows: list[dict[str, Any]] = []
        seen: dict[str, tuple[Any, ...]] = {}
        physical_rows = 0
        with self.path.open("rb") as handle:
            handle.seek(start)
            while handle.tell() < end:
                raw = handle.readline()
                if not raw:
                    break
                physical_rows += 1
                row = json.loads(raw)
                identity = str(
                    row.get("trade_id") or row.get("receipt_id") or ""
                )
                row_ticker = str(row.get("ticker") or "")
                if (
                    not identity or row_ticker != ticker
                    or row.get("true_print") is not True
                ):
                    raise FitError(
                        "invalid true print in ticker range "
                        f"{ticker}:{physical_rows}"
                    )
                timestamp = parse_utc(
                    row.get("exchange_ts"), "print.exchange_ts"
                )
                if not earliest <= timestamp <= latest:
                    continue
                price = int(row.get("price_cents"))
                size = finite_number(row.get("size"), 0)
                if not 1 <= price <= 99 or size < 0:
                    raise FitError(
                        "invalid public print price/size in "
                        f"{ticker}:{physical_rows}"
                    )
                canonical = (
                    ticker, timestamp, price, size, row.get("taker_side")
                )
                prior = seen.get(identity)
                if prior is not None and prior != canonical:
                    raise FitError(
                        f"conflicting trade identity: {identity}"
                    )
                if prior is not None:
                    continue
                seen[identity] = canonical
                rows.append({
                    "trade_id": identity,
                    "ts": timestamp,
                    "price": price,
                    "size": size,
                    "taker_side": str(row.get("taker_side") or ""),
                })
        if physical_rows != expected_rows:
            raise FitError(
                f"public print byte-range row drift for {ticker}: "
                f"{physical_rows} != {expected_rows}"
            )
        rows.sort(key=lambda row: (row["ts"], row["trade_id"]))
        return rows


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FitError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", errors="strict") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise FitError(f"non-object JSONL {path}:{line_number}")
            rows.append(value)
    return rows


def parse_utc(value: Any, field: str) -> float:
    text = str(value or "").replace("Z", "+00:00")
    try:
        stamp = dt.datetime.fromisoformat(text)
    except ValueError as exc:
        raise FitError(f"invalid {field}: {value!r}") from exc
    if stamp.tzinfo is None:
        raise FitError(f"timezone-free {field}: {value!r}")
    return stamp.timestamp()


def parse_top5_et(value: str) -> float:
    try:
        stamp = dt.datetime.strptime(value, "%Y-%m-%d %I:%M:%S %p")
    except ValueError as exc:
        raise FitError(f"invalid premarket_ticks ts_et: {value!r}") from exc
    return stamp.replace(tzinfo=ET).timestamp()


def parse_top5_et_fast(
    value: str, midnight_cache: dict[str, float],
) -> float:
    """Parse the fixed recorder timestamp without per-row strptime."""
    if len(value) < 22:
        return parse_top5_et(value)
    day = value[:10]
    midnight = midnight_cache.get(day)
    if midnight is None:
        try:
            midnight = dt.datetime(
                int(value[0:4]), int(value[5:7]), int(value[8:10]),
                tzinfo=ET,
            ).timestamp()
        except (TypeError, ValueError):
            return parse_top5_et(value)
        midnight_cache[day] = midnight
    try:
        hour = int(value[11:13]) % 12
        if value[20:22] == "PM":
            hour += 12
        return (
            midnight + hour * 3600 + int(value[14:16]) * 60
            + int(value[17:19])
        )
    except (TypeError, ValueError):
        return parse_top5_et(value)


def finite_number(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise FitError(f"invalid numeric value: {value!r}") from exc
    if not math.isfinite(number):
        raise FitError(f"non-finite numeric value: {value!r}")
    return number


def percentile(values: Sequence[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1,
                       int(round((len(ordered) - 1) * fraction))))
    return ordered[index]


def load_events(path: Path) -> list[dict[str, Any]]:
    events = read_jsonl(path)
    if len(events) != D_REQUIRED:
        raise FitError(f"immutable D changed: {len(events)}")
    seen: set[str] = set()
    tickers: set[str] = set()
    for event in events:
        event_id = str(event.get("event_id") or "")
        if not event_id or event_id in seen:
            raise FitError(f"duplicate/missing event_id: {event_id}")
        seen.add(event_id)
        if not "2026-07-12" <= str(event.get("event_date")) <= "2026-07-20":
            raise FitError(f"event outside frozen fit period: {event_id}")
        legs = event.get("legs")
        if not isinstance(legs, list) or len(legs) != 2:
            raise FitError(f"event lacks two legs: {event_id}")
        for leg in legs:
            ticker = str((leg or {}).get("ticker") or "")
            if not ticker or ticker in tickers:
                raise FitError(f"duplicate/missing leg ticker: {ticker}")
            tickers.add(ticker)
    if len(tickers) != 1608:
        raise FitError(f"required leg count changed: {len(tickers)}")
    return sorted(events, key=lambda row: (
        str(row["event_date"]), str(row["event_id"])
    ))


def load_prints(
    path: Path,
    ticker_bounds: Mapping[str, tuple[float, float]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    by_ticker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: dict[str, tuple[Any, ...]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            identity = str(
                row.get("trade_id") or row.get("receipt_id") or ""
            )
            ticker = str(row.get("ticker") or "")
            if (
                not identity or not ticker
                or row.get("true_print") is not True
            ):
                raise FitError(
                    f"invalid true print at normalized row {line_number}"
                )
            timestamp = parse_utc(
                row.get("exchange_ts"), "print.exchange_ts"
            )
            if ticker_bounds is not None:
                bounds = ticker_bounds.get(ticker)
                if bounds is None or not bounds[0] <= timestamp <= bounds[1]:
                    continue
            price = int(row.get("price_cents"))
            size = finite_number(row.get("size"), 0)
            if not 1 <= price <= 99 or size < 0:
                raise FitError(
                    f"invalid price/size at normalized row {line_number}"
                )
            canonical = (
                ticker, timestamp, price, size, row.get("taker_side")
            )
            prior = seen.get(identity)
            if prior is not None and prior != canonical:
                raise FitError(f"conflicting trade identity: {identity}")
            if prior is not None:
                continue
            seen[identity] = canonical
            by_ticker[ticker].append({
                "trade_id": identity,
                "ts": timestamp,
                "price": price,
                "size": size,
                "taker_side": str(row.get("taker_side") or ""),
            })
    for rows in by_ticker.values():
        rows.sort(key=lambda row: (row["ts"], row["trade_id"]))
    return by_ticker


def parse_ladder(row: Mapping[str, Any], side: str) -> list[tuple[int, float]]:
    levels: list[tuple[int, float]] = []
    for index in range(1, 6):
        price_value = row.get(f"{side}_{index}")
        if price_value in (None, ""):
            continue
        price = int(float(price_value))
        size = max(0.0, finite_number(row.get(f"{side}_{index}_sz"), 0))
        if not 1 <= price <= 99:
            raise FitError(f"invalid {side} ladder price: {price}")
        levels.append((price, size))
    return sorted(levels, reverse=(side == "bid"))


def load_top5(
    path: Path,
    ticker: str,
    earliest: float,
    latest: float,
) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with gzip.open(path, "rt", encoding="utf-8", errors="strict",
                   newline="") as handle:
        header = handle.readline().rstrip("\r\n").split(",")
        positions = {
            value.strip(): index for index, value in enumerate(header)
        }
        expected = {"ts_et", "ticker", "bid_1", "ask_1"}
        if not expected.issubset(positions):
            raise FitError(f"premarket_ticks schema mismatch: {path}")
        midnight_cache: dict[str, float] = {}
        prior_state = None
        for line in handle:
            values = line.rstrip("\r\n").split(",")
            if len(values) != len(header):
                raise FitError(f"malformed premarket row: {path}")
            timestamp = parse_top5_et_fast(
                values[positions["ts_et"]], midnight_cache
            )
            if timestamp < earliest:
                continue
            if timestamp > latest:
                break
            if values[positions["ticker"]] != ticker:
                raise FitError(f"premarket ticker mismatch in {path}")
            bids = []
            asks = []
            for side, destination in (("bid", bids), ("ask", asks)):
                for index in range(1, 6):
                    price_position = positions.get(f"{side}_{index}")
                    if price_position is None:
                        continue
                    value = values[price_position]
                    if value == "":
                        continue
                    price = int(float(value))
                    size_position = positions.get(f"{side}_{index}_sz")
                    size = (
                        max(0.0, finite_number(
                            values[size_position], 0
                        ))
                        if size_position is not None else 0.0
                    )
                    destination.append((price, size))
            bids.sort(reverse=True)
            asks.sort()
            if not bids or not asks:
                continue
            state = (tuple(bids), tuple(asks))
            if state == prior_state:
                continue
            prior_state = state
            last_trade_position = positions.get("last_trade")
            last_trade_value = (
                values[last_trade_position]
                if last_trade_position is not None else ""
            )
            rows.append({
                "ts": timestamp,
                "bids": bids,
                "asks": asks,
                "best_bid": bids[0][0],
                "best_ask": asks[0][0],
                "last_trade": (
                    int(float(last_trade_value))
                    if last_trade_value not in (None, "") else None
                ),
                "source": "premarket_ticks_top5",
            })
    rows.sort(key=lambda row: row["ts"])
    deduped: list[dict[str, Any]] = []
    for row in rows:
        if deduped and row["ts"] == deduped[-1]["ts"]:
            deduped[-1] = row
        else:
            deduped.append(row)
    return deduped


def cache_path(cache_root: Path, event_id: str) -> Path:
    if not event_id or any(
        character not in
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        for character in event_id
    ):
        raise FitError(f"unsafe event cache identity: {event_id!r}")
    return cache_root / f"{event_id}.json.gz"


def load_event_market_data(
    event: Mapping[str, Any],
    archive: PrintArchive,
    premarket_dir: Path,
    recovered_premarket_dir: Path,
    starts_by_event: Mapping[str, Mapping[str, Any]],
    starts: Sequence[int],
    max_corridor: int,
    cache_root: Path,
    cache_key: str,
) -> list[dict[str, Any]]:
    """Load one event's bounded market evidence, caching outside Git."""
    event_id = str(event["event_id"])
    path = cache_path(cache_root, event_id)
    if path.is_file():
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            cached = json.load(handle)
        if (
            not isinstance(cached, dict)
            or cached.get("cache_key") != cache_key
            or cached.get("event_id") != event_id
            or not isinstance(cached.get("legs"), list)
            or len(cached["legs"]) != 2
        ):
            raise FitError(
                f"event cache receipt mismatch; preserve and use a new "
                f"cache root: {path}"
            )
        return list(cached["legs"])

    scheduled = parse_utc(
        event["scheduled_start_exchange_ts"],
        "scheduled_start_exchange_ts",
    )
    earliest = scheduled - max(starts) * 3600 - 301
    start_row = starts_by_event[event_id]
    horizons = [scheduled + max_corridor * 60]
    for field in (
        "verified_start_utc", "known_live_by_utc",
        "safe_prestart_cutoff_utc",
    ):
        if start_row.get(field):
            horizons.append(parse_utc(start_row[field], field))
    latest = max(horizons) + 301
    legs = []
    for leg in event["legs"]:
        ticker = str(leg["ticker"])
        top5_path = premarket_dir / f"{ticker}.csv.gz"
        if not top5_path.is_file():
            top5_path = recovered_premarket_dir / f"{ticker}.csv.gz"
        legs.append({
            "ticker": ticker,
            "leg": leg.get("leg"),
            "snapshots": load_top5(
                top5_path, ticker, earliest, latest,
            ),
            "prints": archive.load(ticker, earliest, latest),
        })
    cache_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(cache_root, 0o700)
    except OSError:
        pass
    payload = {
        "cache_version": RUNNER_VERSION + "-event-market-v1",
        "cache_key": cache_key,
        "event_id": event_id,
        "earliest_utc": dt.datetime.fromtimestamp(
            earliest, UTC
        ).isoformat(),
        "latest_utc": dt.datetime.fromtimestamp(latest, UTC).isoformat(),
        "legs": legs,
    }
    with gzip.open(path, "wt", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return legs


def initialize_event_cache_worker(
    print_path: str,
    print_ranges: dict[str, tuple[int, int, int]],
    premarket_dir: str,
    recovered_premarket_dir: str,
    starts_by_event: dict[str, dict[str, Any]],
    starts: tuple[int, ...],
    max_corridor: int,
    cache_root: str,
    cache_key: str,
) -> None:
    """Initialize a process with a prevalidated, seek-only tape view."""
    archive = object.__new__(PrintArchive)
    archive.path = Path(print_path)
    archive.expected_sha256 = ""
    archive.ranges = print_ranges
    archive.sha256 = ""
    _CACHE_WORKER_CONTEXT.clear()
    _CACHE_WORKER_CONTEXT.update({
        "archive": archive,
        "premarket_dir": Path(premarket_dir),
        "recovered_premarket_dir": Path(recovered_premarket_dir),
        "starts_by_event": starts_by_event,
        "starts": starts,
        "max_corridor": max_corridor,
        "cache_root": Path(cache_root),
        "cache_key": cache_key,
    })


def prebuild_event_cache_worker(
    event: dict[str, Any],
) -> tuple[str, int, int]:
    context = _CACHE_WORKER_CONTEXT
    legs = load_event_market_data(
        event,
        context["archive"],
        context["premarket_dir"],
        context["recovered_premarket_dir"],
        context["starts_by_event"],
        context["starts"],
        context["max_corridor"],
        context["cache_root"],
        context["cache_key"],
    )
    return (
        str(event["event_id"]),
        sum(len(row["snapshots"]) for row in legs),
        sum(len(row["prints"]) for row in legs),
    )


def prebuild_event_caches(
    events: Sequence[Mapping[str, Any]],
    archive: PrintArchive,
    premarket_dir: Path,
    recovered_premarket_dir: Path,
    starts_by_event: Mapping[str, Mapping[str, Any]],
    starts: Sequence[int],
    max_corridor: int,
    cache_root: Path,
    cache_key: str,
    workers: int,
) -> None:
    """Populate the existing immutable event-cache contract in parallel."""
    if workers <= 1:
        return
    cache_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    event_rows = [dict(event) for event in events]
    completed = 0
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=workers,
        initializer=initialize_event_cache_worker,
        initargs=(
            str(archive.path),
            archive.ranges,
            str(premarket_dir),
            str(recovered_premarket_dir),
            {
                str(key): dict(value)
                for key, value in starts_by_event.items()
            },
            tuple(int(value) for value in starts),
            int(max_corridor),
            str(cache_root),
            cache_key,
        ),
    ) as executor:
        futures = [
            executor.submit(prebuild_event_cache_worker, event)
            for event in event_rows
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()
            completed += 1
            if completed % 25 == 0 or completed == len(futures):
                print(
                    f"event_cache={completed}/{len(futures)}",
                    flush=True,
                )


def snapshot_after(
    snapshots: Sequence[Mapping[str, Any]], timestamp: float, right: float,
) -> Mapping[str, Any] | None:
    index = bisect_left(
        snapshots, timestamp, key=lambda row: float(row["ts"])
    )
    if index >= len(snapshots) or float(snapshots[index]["ts"]) > right:
        return None
    return snapshots[index]


def snapshot_before(
    snapshots: Sequence[Mapping[str, Any]], timestamp: float,
) -> Mapping[str, Any] | None:
    index = bisect_right(
        snapshots, timestamp, key=lambda row: float(row["ts"])
    ) - 1
    return snapshots[index] if index >= 0 else None


def level_quantity(snapshot: Mapping[str, Any], price: int) -> float:
    return sum(float(size) for level, size in snapshot["bids"]
               if int(level) == price)


def weighted_imbalance(
    bids: Sequence[tuple[int, float]],
    asks: Sequence[tuple[int, float]],
    ticks: int,
) -> float | None:
    if not bids or not asks:
        return None
    bb, ba = bids[0][0], asks[0][0]
    bid_weight = sum(
        size / (1 + bb - price)
        for price, size in bids if bb - price < ticks
    )
    ask_weight = sum(
        size / (1 + price - ba)
        for price, size in asks if price - ba < ticks
    )
    total = bid_weight + ask_weight
    return (bid_weight - ask_weight) / total if total else None


def depth_features(
    snapshot: Mapping[str, Any],
    history: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    bids = list(snapshot["bids"])
    asks = list(snapshot["asks"])
    bid_total = sum(size for _, size in bids)
    ask_total = sum(size for _, size in asks)
    prior = [row for row in history
             if float(snapshot["ts"]) - 300 <= float(row["ts"])
             <= float(snapshot["ts"])]
    spread_values = [
        float(row["best_ask"]) - float(row["best_bid"]) for row in prior
    ]
    imbalance_values = [
        weighted_imbalance(row["bids"], row["asks"], 5) for row in prior
    ]
    imbalance_values = [value for value in imbalance_values
                        if value is not None]
    additions = 0.0
    removals = 0.0
    replenishments = 0
    depletions = 0
    for before, after in zip(prior, prior[1:]):
        old = {("b", p): q for p, q in before["bids"]}
        old.update({("a", p): q for p, q in before["asks"]})
        new = {("b", p): q for p, q in after["bids"]}
        new.update({("a", p): q for p, q in after["asks"]})
        for key in old.keys() | new.keys():
            change = new.get(key, 0) - old.get(key, 0)
            if change > 0:
                additions += change
                replenishments += 1
            elif change < 0:
                removals += -change
                depletions += 1
    best_bid = int(snapshot["best_bid"])
    best_ask = int(snapshot["best_ask"])
    bid_wall = max(bids, key=lambda item: item[1])
    ask_wall = max(asks, key=lambda item: item[1])
    wall_bid_presence = (
        sum(any(price == bid_wall[0] and size >= bid_wall[1] * 0.5
                for price, size in row["bids"]) for row in prior)
        / len(prior) if prior else None
    )
    wall_ask_presence = (
        sum(any(price == ask_wall[0] and size >= ask_wall[1] * 0.5
                for price, size in row["asks"]) for row in prior)
        / len(prior) if prior else None
    )
    return {
        "best_bid_cents": best_bid,
        "best_ask_cents": best_ask,
        "spread_cents": best_ask - best_bid,
        "spread_change_5m": (
            spread_values[-1] - spread_values[0]
            if len(spread_values) >= 2 else None
        ),
        "bid_depth_top5": bid_total,
        "ask_depth_top5": ask_total,
        "ask_over_bid_top5": ask_total / bid_total if bid_total else None,
        "imbalance_1tick": weighted_imbalance(bids, asks, 1),
        "imbalance_3tick": weighted_imbalance(bids, asks, 3),
        "imbalance_5tick": weighted_imbalance(bids, asks, 5),
        "pressure_change_5m": (
            imbalance_values[-1] - imbalance_values[0]
            if len(imbalance_values) >= 2 else None
        ),
        "bid_slope_top5": (
            (bids[-1][1] - bids[0][1]) / max(1, len(bids) - 1)
            if len(bids) >= 2 else None
        ),
        "ask_slope_top5": (
            (asks[-1][1] - asks[0][1]) / max(1, len(asks) - 1)
            if len(asks) >= 2 else None
        ),
        "bid_wall_price": bid_wall[0],
        "bid_wall_size": bid_wall[1],
        "ask_wall_price": ask_wall[0],
        "ask_wall_size": ask_wall[1],
        "bid_floor_persistence_5m": wall_bid_presence,
        "ask_ceiling_persistence_5m": wall_ask_presence,
        "book_additions_5m": additions,
        "book_removals_5m": removals,
        "replenishment_events_5m": replenishments,
        "depletion_events_5m": depletions,
        "five_contract_bid_depth": bid_total >= LOT,
        "five_contract_ask_depth": ask_total >= LOT,
        "extreme_ask_over_bid": bool(
            bid_total and ask_total / bid_total >= 4.0
        ),
        "source": "premarket_ticks_top5",
        "top5_only": True,
    }


def trade_features(
    prints: Sequence[Mapping[str, Any]], timestamp: float,
) -> dict[str, Any]:
    recent = [row for row in prints
              if timestamp - 300 <= float(row["ts"]) <= timestamp
              and float(row["size"]) > 0]
    sell_size = sum(float(row["size"]) for row in recent
                    if row["taker_side"] == "no")
    buy_size = sum(float(row["size"]) for row in recent
                   if row["taker_side"] == "yes")
    last_minute = sum(float(row["size"]) for row in recent
                      if float(row["ts"]) >= timestamp - 60)
    prior_four = sum(float(row["size"]) for row in recent
                     if float(row["ts"]) < timestamp - 60)
    return {
        "true_print_count_5m": len(recent),
        "true_print_size_5m": sum(float(row["size"]) for row in recent),
        "sell_yes_size_5m": sell_size,
        "buy_yes_size_5m": buy_size,
        "signed_yes_flow_5m": buy_size - sell_size,
        "print_acceleration_1m_vs_prior4m": (
            last_minute - prior_four / 4.0
        ),
    }


def complement_normalized_features(
    own: Mapping[str, Any],
    sibling: Mapping[str, Any],
) -> dict[str, Any]:
    """Map sibling YES quotes into the current leg's economic YES direction."""
    own_bid = int(own["best_bid"])
    own_ask = int(own["best_ask"])
    sibling_bid = int(sibling["best_bid"])
    sibling_ask = int(sibling["best_ask"])
    implied_bid = 100 - sibling_ask
    implied_ask = 100 - sibling_bid
    normalized_bid = max(own_bid, implied_bid)
    normalized_ask = min(own_ask, implied_ask)
    own_mid = (own_bid + own_ask) / 2.0
    sibling_mid = (sibling_bid + sibling_ask) / 2.0
    return {
        "economic_direction": "this_leg_yes",
        "sibling_yes_mapped_as": "this_leg_no",
        "implied_yes_bid_from_sibling_ask": implied_bid,
        "implied_yes_ask_from_sibling_bid": implied_ask,
        "normalized_economic_best_bid": normalized_bid,
        "normalized_economic_best_ask": normalized_ask,
        "normalized_economic_spread": normalized_ask - normalized_bid,
        "direct_plus_sibling_mid_minus_par": (
            own_mid + sibling_mid - PAR
        ),
        "complement_books_crossed": normalized_bid > normalized_ask,
        "complement_books_locked": normalized_bid == normalized_ask,
        "fill_queue_uses_direct_contract_only": True,
    }


def limited_depth_features(
    history: Sequence[Mapping[str, Any]],
    target_timestamp: float,
) -> dict[str, Any]:
    causal = [
        row for row in history
        if target_timestamp - 300 <= float(row["ts"]) <= target_timestamp
    ]
    if not causal:
        return {
            "top20_snapshot_available": False,
            "top20_missing_reason": (
                "no causal depth_recorder snapshot within five minutes"
            ),
        }
    snapshot = causal[-1]
    bids = list(snapshot["bids"])
    asks = list(snapshot["asks"])
    bid_total = sum(size for _, size in bids)
    ask_total = sum(size for _, size in asks)
    additions = 0.0
    removals = 0.0
    for before, after in zip(causal, causal[1:]):
        old = {("b", p): q for p, q in before["bids"]}
        old.update({("a", p): q for p, q in before["asks"]})
        new = {("b", p): q for p, q in after["bids"]}
        new.update({("a", p): q for p, q in after["asks"]})
        for key in old.keys() | new.keys():
            change = new.get(key, 0) - old.get(key, 0)
            if change > 0:
                additions += change
            elif change < 0:
                removals += -change
    bid_near = sum(size for _, size in bids[:5])
    ask_near = sum(size for _, size in asks[:5])
    bid_wall = max(bids, key=lambda value: value[1]) if bids else None
    ask_wall = max(asks, key=lambda value: value[1]) if asks else None
    return {
        "top20_snapshot_available": True,
        "top20_snapshot_utc": float(snapshot["ts"]),
        "top20_timestamp_basis": "local_recorder_receipt_epoch",
        "top20_snapshot_lag_seconds": (
            target_timestamp - float(snapshot["ts"])
        ),
        "top20_source": (
            "depth_recorder_snapshot_top20_change_deduplicated"
        ),
        "top20_sequence_valid": False,
        "top20_is_full_causal_chain": False,
        "bid_depth_top20": bid_total,
        "ask_depth_top20": ask_total,
        "bid_depth_below_top5": bid_total - bid_near,
        "ask_depth_below_top5": ask_total - ask_near,
        "ask_over_bid_limited_top20": (
            ask_total / bid_total if bid_total else None
        ),
        "limited_imbalance_1tick": weighted_imbalance(bids, asks, 1),
        "limited_imbalance_3tick": weighted_imbalance(bids, asks, 3),
        "limited_imbalance_5tick": weighted_imbalance(bids, asks, 5),
        "limited_bid_slope": (
            (bids[-1][1] - bids[0][1]) / max(1, len(bids) - 1)
            if len(bids) >= 2 else None
        ),
        "limited_ask_slope": (
            (asks[-1][1] - asks[0][1]) / max(1, len(asks) - 1)
            if len(asks) >= 2 else None
        ),
        "limited_bid_convexity": (
            bids[0][1] - 2 * bids[len(bids) // 2][1] + bids[-1][1]
            if len(bids) >= 3 else None
        ),
        "limited_ask_convexity": (
            asks[0][1] - 2 * asks[len(asks) // 2][1] + asks[-1][1]
            if len(asks) >= 3 else None
        ),
        "limited_bid_wall_price": bid_wall[0] if bid_wall else None,
        "limited_bid_wall_size": bid_wall[1] if bid_wall else None,
        "limited_ask_wall_price": ask_wall[0] if ask_wall else None,
        "limited_ask_wall_size": ask_wall[1] if ask_wall else None,
        "limited_additions_5m": additions,
        "limited_removals_5m": removals,
    }


def apply_top20_features(
    feature_rows: Sequence[dict[str, Any]],
    depth_recorder_dir: Path,
) -> dict[str, Any]:
    targets: dict[str, list[tuple[float, dict[str, Any]]]] = defaultdict(list)
    for feature in feature_rows:
        timestamp = feature.get("causal_post_utc")
        if timestamp is not None:
            targets[str(feature["ticker"])].append(
                (float(timestamp), feature)
            )
    histories: dict[tuple[str, float], list[dict[str, Any]]] = defaultdict(list)
    files = []
    for path in sorted(depth_recorder_dir.glob("depth_202607*.jsonl.gz")):
        digits = path.name.removeprefix("depth_")[:8]
        if digits.isdigit() and "20260712" <= digits <= "20260720":
            files.append(path)
    physical_rows = 0
    relevant_rows = 0
    parse_errors = 0
    for file_index, path in enumerate(files, 1):
        with gzip.open(path, "rt", encoding="utf-8", errors="strict") as handle:
            for line in handle:
                physical_rows += 1
                try:
                    raw = json.loads(line)
                    ticker = str(raw.get("ticker") or "")
                    target_rows = targets.get(ticker)
                    if not target_rows:
                        continue
                    timestamp = finite_number(raw.get("ts_epoch"))
                    bids = [
                        (int(level[0]), max(0.0, finite_number(level[1])))
                        for level in (raw.get("bids") or [])
                        if isinstance(level, list) and len(level) == 2
                    ]
                    asks = [
                        (int(level[0]), max(0.0, finite_number(level[1])))
                        for level in (raw.get("asks") or [])
                        if isinstance(level, list) and len(level) == 2
                    ]
                    bids.sort(reverse=True)
                    asks.sort()
                    if not bids or not asks:
                        continue
                except (json.JSONDecodeError, FitError, TypeError, ValueError):
                    parse_errors += 1
                    continue
                matched = False
                for target, _ in target_rows:
                    if target - 300 <= timestamp <= target:
                        histories[(ticker, target)].append({
                            "ts": timestamp,
                            "bids": bids,
                            "asks": asks,
                        })
                        matched = True
                if matched:
                    relevant_rows += 1
        if file_index % 25 == 0 or file_index == len(files):
            print(
                f"top20_files={file_index}/{len(files)} "
                f"physical_rows={physical_rows} relevant={relevant_rows}",
                flush=True,
            )
    for ticker, target_rows in targets.items():
        for target, feature in target_rows:
            history = histories.get((ticker, target), [])
            history.sort(key=lambda row: float(row["ts"]))
            feature.update(limited_depth_features(history, target))
    return {
        "file_count": len(files),
        "physical_rows": physical_rows,
        "relevant_rows": relevant_rows,
        "parse_errors": parse_errors,
    }


def shape_context(
    table: Mapping[str, Any],
    category: str,
    leg_mid: float,
    sibling_mid: float,
    minutes_to_start: float,
    role_override: str | None = None,
) -> dict[str, Any]:
    favorite_mid = max(leg_mid, sibling_mid)
    role = (
        role_override
        if role_override in {"favorite", "underdog"}
        else "favorite" if leg_mid >= sibling_mid else "underdog"
    )
    tbin = min(48, int(max(0.0, minutes_to_start) // 10))
    cell_key = (
        f"{category}|{min(4, max(0, int(favorite_mid) // 20))}|{tbin}"
    )
    cell = table.get(cell_key)
    if not isinstance(cell, dict) or cell.get("null_reason"):
        return {
            "role": role,
            "shape_cell": cell_key,
            "shape_cell_available": False,
            "shape_aim50_cents": None,
            "shape_prior_source": None,
            "shape_dip_admissible": None,
        }
    prefix = "f" if role == "favorite" else "d"
    dip50 = cell.get(prefix + "dip50")
    aim = (
        max(1.0, leg_mid + float(dip50))
        if dip50 is not None else None
    )
    return {
        "role": role,
        "shape_cell": cell_key,
        "shape_cell_available": True,
        "shape_aim50_cents": aim,
        "shape_prior_source": cell.get("source"),
        "shape_borrowed_from": cell.get("borrowed_from"),
        "shape_drift_cents": cell.get(prefix + "d"),
        "shape_dip50_cents": dip50,
        "shape_residual_sd": cell.get(prefix + "_sd"),
        "shape_dip_admissible": cell.get("dip_admissible"),
    }


def normalized_person_name(value: Any) -> str:
    return "".join(
        character for character in str(value or "").casefold()
        if character.isalnum()
    )


def person_surname(value: Any) -> str:
    words = [
        "".join(character for character in word.casefold()
                if character.isalnum())
        for word in str(value or "").split()
    ]
    return words[-1] if words else ""


def participant_side(
    connection: sqlite3.Connection,
    ticker: str,
    player1_name: Any,
    player2_name: Any,
) -> tuple[int | None, str]:
    """Resolve a ticker to the named bookmaker participant, never its role.

    A favorite/underdog match is not an identity match: bookmaker and Kalshi
    economic roles can disagree.  The three-character exchange code is used
    only when it uniquely matches a participant surname prefix.  Otherwise a
    unique players-table name is required.
    """
    code = str(ticker).rsplit("-", 1)[-1].upper()
    p1_surname = person_surname(player1_name)
    p2_surname = person_surname(player2_name)
    code_matches = [
        side for side, surname in ((1, p1_surname), (2, p2_surname))
        if surname and surname[:3].upper() == code[:3]
    ]
    if len(code_matches) == 1:
        return code_matches[0], "ticker_code_unique_surname_prefix"

    try:
        rows = connection.execute(
            """SELECT name FROM players
               WHERE UPPER(kalshi_code)=? AND name IS NOT NULL""",
            (code,),
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    names = {
        normalized_person_name(row[0]) for row in rows
        if normalized_person_name(row[0])
    }
    sides: set[int] = set()
    for name in names:
        for side, book_name in (
            (1, normalized_person_name(player1_name)),
            (2, normalized_person_name(player2_name)),
        ):
            if name == book_name or (
                len(name) >= 5 and len(book_name) >= 5
                and (name in book_name or book_name in name)
            ):
                sides.add(side)
    if len(sides) == 1:
        return next(iter(sides)), "players_table_unique_name"
    return None, (
        "participant_identity_ambiguous"
        if code_matches or sides else "participant_identity_unresolved"
    )


def macro_book_context(
    connection: sqlite3.Connection,
    event_id: str,
    ticker: str,
    timestamp: float,
    market_mid: float,
) -> dict[str, Any]:
    et_text = (
        dt.datetime.fromtimestamp(timestamp, ET).strftime("%Y-%m-%d %H:%M:%S")
    )
    rows = connection.execute(
        """SELECT book_key, player1_name, player2_name,
                  book_p1_fv_cents, book_p2_fv_cents, polled_at
           FROM book_prices
           WHERE event_ticker=? AND polled_at<=?
           ORDER BY polled_at DESC
           LIMIT 100""",
        (event_id, et_text),
    ).fetchall()
    latest: dict[str, tuple[float, str, str]] = {}
    mapping_reasons: set[str] = set()
    mapped_sides: set[int] = set()
    for book_key, p1_name, p2_name, p1, p2, polled_at in rows:
        if book_key in latest or p1 is None or p2 is None:
            continue
        side, reason = participant_side(
            connection, ticker, p1_name, p2_name
        )
        mapping_reasons.add(reason)
        if side is None:
            continue
        mapped_sides.add(side)
        latest[str(book_key)] = (
            float(p1 if side == 1 else p2),
            str(polled_at),
            reason,
        )
    if not latest:
        return {
            "bookmaker_available": False,
            "book_count": 0,
            "pinnacle_available": False,
            "book_blend_cents": None,
            "book_market_divergence_cents": None,
            "participant_mapping": sorted(mapping_reasons),
        }
    if len(mapped_sides) != 1:
        return {
            "bookmaker_available": False,
            "book_count": 0,
            "pinnacle_available": False,
            "book_blend_cents": None,
            "book_market_divergence_cents": None,
            "participant_mapping": [
                "contradictory_participant_side_across_book_rows"
            ],
        }
    participant_values = [value[0] for value in latest.values()]
    blend = statistics.mean(participant_values)
    pinnacle = latest.get("pinnacle")
    pinnacle_value = pinnacle[0] if pinnacle else None
    return {
        "bookmaker_available": True,
        "book_count": len(latest),
        "pinnacle_available": pinnacle is not None,
        "book_blend_cents": blend,
        "pinnacle_cents": pinnacle_value,
        "book_dispersion_cents": (
            statistics.pstdev(participant_values)
            if len(participant_values) >= 2 else 0
        ),
        "book_market_divergence_cents": blend - market_mid,
        "book_latest_polled_at_et": max(value[1]
                                         for value in latest.values()),
        "participant_mapping": sorted(
            {value[2] for value in latest.values()}
        ),
        "participant_side": next(iter(mapped_sides)),
    }


def price_for_policy(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    feature: Mapping[str, Any],
    snapshot: Mapping[str, Any],
) -> int | None:
    best_bid = int(snapshot["best_bid"])
    maker_ceiling = int(snapshot["best_ask"]) - 1
    rule = str(policy.get("placement_rule") or "touch")
    if rule in {"touch", "walk_law"}:
        price = best_bid
    elif rule == "depth_support":
        depth = int(policy.get("max_depth_cents", 5))
        eligible = [
            level for level in snapshot["bids"]
            if int(level[0]) >= best_bid - depth
        ]
        if not eligible:
            return None
        price = max(eligible, key=lambda value: (value[1], value[0]))[0]
    elif rule == "category_offset":
        offsets = policy.get("category_offsets") or {}
        price = best_bid - int(offsets.get(str(event["category"]), 0))
    elif rule == "shape_cell_offset":
        aim = feature.get("shape_aim50_cents")
        price = (
            min(best_bid, int(round(float(aim))))
            if aim is not None and feature.get("shape_dip_admissible")
            else best_bid
        )
    elif rule == "backwalk":
        price = best_bid - int(policy.get("initial_depth_cents", 2))
    elif rule == "pressure_aware":
        ratio = (
            feature.get("ask_over_bid_limited_top20")
            if policy.get("use_top20_pressure", True)
            and not policy.get("ablate_pressure")
            and feature.get("top20_snapshot_available")
            else feature.get("ask_over_bid_top5")
        )
        pressure_depth = (
            int(policy.get("high_ask_pressure_depth_cents", 2))
            if ratio is not None
            and float(ratio) >= float(policy.get("ask_over_bid_threshold", 1.5))
            else int(policy.get("base_depth_cents", 0))
        )
        price = best_bid - pressure_depth
    elif rule == "causal_stack":
        price = best_bid - int(policy.get("base_depth_cents", 1))
        aim = feature.get("shape_aim50_cents")
        if (aim is not None and feature.get("shape_dip_admissible")
                and not policy.get("ablate_macrostructure")):
            price = min(price, int(round(float(aim))))
        ratio = (
            feature.get("ask_over_bid_limited_top20")
            if policy.get("use_top20_pressure", True)
            and not policy.get("ablate_pressure")
            and feature.get("top20_snapshot_available")
            else feature.get("ask_over_bid_top5")
        )
        if (ratio is not None
                and float(ratio) >= float(
                    policy.get("ask_over_bid_threshold", 1.5))
                and not policy.get("ablate_pressure")):
            price -= int(policy.get("pressure_extra_depth_cents", 1))
        divergence = feature.get("book_market_divergence_cents")
        if (divergence is not None and float(divergence) <= -3
                and not policy.get("ablate_macrostructure")):
            price -= 1
    else:
        raise FitError(f"unknown placement rule: {rule}")
    return max(1, min(maker_ceiling, int(price)))


def build_actions(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    feature: Mapping[str, Any],
    snapshots: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    not_before: float,
    right: float,
    scheduled: float,
) -> list[dict[str, Any]]:
    first = snapshot_after(snapshots, not_before, right)
    if first is None:
        return []
    price = price_for_policy(policy, event, feature, first)
    if price is None:
        return []
    actions = [{
        "ts": float(first["ts"]),
        "price": price,
        "queue_ahead": level_quantity(first, price),
        "reason": "initial_post",
    }]
    rule = str(policy.get("placement_rule") or "")
    if rule not in {"walk_law", "backwalk"}:
        return actions
    current = price
    last_action = float(first["ts"])
    max_moves = int(policy.get("max_moves", 2))
    move_step = int(policy.get("move_step_cents", 1))
    backwalk_start = scheduled - int(
        policy.get("backwalk_start_minutes_before_schedule", 120)
    ) * 60
    print_index = bisect_right(
        prints, last_action, key=lambda row: float(row["ts"])
    )
    causal_print_since_action = False
    for snapshot in snapshots:
        timestamp = float(snapshot["ts"])
        if timestamp <= last_action or timestamp > right:
            continue
        while (print_index < len(prints)
               and float(prints[print_index]["ts"]) <= timestamp):
            trade = prints[print_index]
            if (
                trade["taker_side"] == "no"
                and float(trade["size"]) > 0
                and int(trade["price"]) <= current
            ):
                causal_print_since_action = True
            print_index += 1
        if len(actions) - 1 >= max_moves:
            break
        best_bid = int(snapshot["best_bid"])
        if best_bid <= current:
            continue
        if rule == "walk_law":
            if not causal_print_since_action:
                continue
            target = min(best_bid, int(snapshot["best_ask"]) - 1)
        else:
            if timestamp < backwalk_start:
                continue
            imbalance = weighted_imbalance(
                snapshot["bids"], snapshot["asks"], 5
            )
            if imbalance is None or imbalance < float(
                    policy.get("move_imbalance_min", 0)):
                continue
            target = min(
                current + move_step, best_bid, int(snapshot["best_ask"]) - 1
            )
        if target <= current:
            continue
        current = target
        last_action = timestamp
        actions.append({
            "ts": timestamp,
            "price": current,
            "queue_ahead": level_quantity(snapshot, current),
            "reason": rule + "_causal_move",
        })
        causal_print_since_action = False
    return actions


def simulate_actions(
    actions: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    right: float,
    queue_case: str,
    *,
    initial_quantity: float = 0.0,
    initial_cost: float = 0.0,
) -> dict[str, Any]:
    quantity = initial_quantity
    cost = initial_cost
    first_fill: float | None = None
    completion: float | None = None
    if not actions:
        return {
            "status": "missing_placement_evidence",
            "quantity": quantity,
            "cost": cost,
            "first_fill_ts": None,
            "completion_ts": None,
        }
    for index, action in enumerate(actions):
        start = float(action["ts"])
        stop = (
            float(actions[index + 1]["ts"])
            if index + 1 < len(actions) else right
        )
        if start >= stop or quantity >= LOT:
            continue
        price = int(action["price"])
        first_index = bisect_right(
            prints, start, key=lambda row: float(row["ts"])
        )
        last_index = bisect_right(
            prints, stop, key=lambda row: float(row["ts"])
        )
        eligible = [
            row for row in prints[first_index:last_index]
            if row["taker_side"] == "no"
            and float(row["size"]) > 0
            and int(row["price"]) <= price
        ]
        same_cumulative = 0.0
        queue = (
            float(action["queue_ahead"]) if queue_case == "lower" else 0.0
        )
        credited_same = 0.0
        for trade in eligible:
            timestamp = float(trade["ts"])
            if int(trade["price"]) < price:
                add = LOT - quantity
            else:
                same_cumulative += float(trade["size"])
                new_credit = max(0.0, same_cumulative - queue)
                add = min(
                    LOT - quantity,
                    max(0.0, new_credit - credited_same),
                )
                credited_same = new_credit
            if add <= 0:
                continue
            if first_fill is None:
                first_fill = timestamp
            quantity += add
            cost += add * price
            if quantity >= LOT - 1e-9:
                quantity = LOT
                completion = timestamp
                break
        if completion is not None:
            break
    return {
        "status": "filled" if quantity >= LOT else "not_filled",
        "quantity": quantity,
        "cost": cost,
        "vwap": cost / quantity if quantity else None,
        "first_fill_ts": first_fill,
        "completion_ts": completion,
    }


def truncate_actions(
    actions: Sequence[Mapping[str, Any]], cutoff: float,
) -> list[dict[str, Any]]:
    return [dict(action) for action in actions
            if float(action["ts"]) < cutoff]


def w1_reference(
    prints: Sequence[Mapping[str, Any]], left: float, right: float,
) -> int | None:
    first_index = bisect_left(
        prints, left, key=lambda row: float(row["ts"])
    )
    last_index = bisect_right(
        prints, right, key=lambda row: float(row["ts"])
    )
    eligible = [
        row for row in prints[first_index:last_index]
        if float(row["size"]) > 0
    ]
    return int(eligible[-1]["price"]) if eligible else None


def initial_action_plan(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    leg_contexts: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
    scheduled: float,
) -> list[list[dict[str, Any]]] | None:
    sequence = str(policy.get("sequence_rule") or "simultaneous")
    not_before = [left, left]
    if sequence == "favorite_first":
        favorite_index = next(
            (index for index, context in enumerate(leg_contexts)
            if context["feature"].get("role") == "favorite"),
            None,
        )
        if favorite_index is None:
            return None
        not_before[1 - favorite_index] += int(
            policy.get("sibling_delay_seconds", 30)
        )
    actions = []
    for index, context in enumerate(leg_contexts):
        actions.append(build_actions(
            policy, event, context["feature"], context["snapshots"],
            context["prints"], not_before[index], right, scheduled,
        ))
    return actions


def evaluate_queue_case(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    leg_contexts: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
    scheduled: float,
    queue_case: str,
    action_plan: Sequence[Sequence[Mapping[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    actions = (
        [list(rows) for rows in action_plan]
        if action_plan is not None
        else initial_action_plan(
            policy, event, leg_contexts, left, right, scheduled
        )
    )
    if actions is None:
        return [{"status": "missing_role"} for _ in leg_contexts]
    initial: list[dict[str, Any]] = []
    for index, context in enumerate(leg_contexts):
        initial.append(simulate_actions(
            actions[index], context["prints"], right, queue_case
        ))
    response = str(policy.get("first_fill_response") or "hold")
    completed = [
        (index, row) for index, row in enumerate(initial)
        if row.get("completion_ts") is not None
    ]
    if response == "hold" or not completed:
        return initial
    first_index, first_result = min(
        completed, key=lambda item: float(item[1]["completion_ts"])
    )
    sibling_index = 1 - first_index
    cutoff = float(first_result["completion_ts"])
    if initial[sibling_index].get("completion_ts") is not None and float(
            initial[sibling_index]["completion_ts"]
    ) <= cutoff:
        return initial
    sibling = leg_contexts[sibling_index]
    prior = simulate_actions(
        truncate_actions(actions[sibling_index], cutoff),
        sibling["prints"], cutoff, queue_case,
    )
    response_policy = dict(policy)
    response_policy["max_moves"] = 0
    response_policy["placement_rule"] = (
        "touch" if response == "reaim_touch" else "depth_support"
    )
    response_actions = build_actions(
        response_policy, event, sibling["feature"], sibling["snapshots"],
        sibling["prints"], cutoff, right, scheduled,
    )
    initial[sibling_index] = simulate_actions(
        response_actions, sibling["prints"], right, queue_case,
        initial_quantity=float(prior["quantity"]),
        initial_cost=float(prior["cost"]),
    )
    initial[sibling_index]["first_leg_response_at"] = cutoff
    return initial


def event_candidate_outcome(
    candidate_id: str,
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    contexts: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
    scheduled: float,
) -> dict[str, Any]:
    action_plan = initial_action_plan(
        policy, event, contexts, left, right, scheduled
    )
    lower = evaluate_queue_case(
        policy, event, contexts, left, right, scheduled, "lower",
        action_plan,
    )
    upper = evaluate_queue_case(
        policy, event, contexts, left, right, scheduled, "upper",
        action_plan,
    )
    references = [
        w1_reference(context["prints"], left, right) for context in contexts
    ]
    exact_complete = all(row.get("status") == "filled" for row in lower)
    upper_complete_known = all(
        row.get("status") == "filled" for row in upper
    )
    missing_statuses = {"missing_placement_evidence", "missing_role"}
    missing = any(
        row.get("status") in missing_statuses
        for row in lower + upper
    )
    possible_complete = all(
        row.get("status") == "filled"
        or row.get("status") in missing_statuses
        for row in upper
    )

    def metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
        if not all(row.get("status") == "filled" for row in rows):
            return None
        prices = [float(row["vwap"]) for row in rows]
        if any(reference is None for reference in references):
            return {
                "combined_cost": sum(prices),
                "PC": sum(prices) < PAR,
                "reference_available": False,
                "leg_deltas": None,
                "pair_delta": None,
                "NC": None,
                "IC": None,
            }
        deltas = [
            prices[index] - float(references[index])
            for index in range(2)
        ]
        return {
            "combined_cost": sum(prices),
            "PC": sum(prices) < PAR,
            "reference_available": True,
            "leg_deltas": deltas,
            "pair_delta": sum(deltas),
            "NC": sum(deltas) < 0,
            "IC": all(delta < 0 for delta in deltas),
        }

    lower_metrics = metrics(lower)
    upper_metrics = metrics(upper)
    censored = (
        missing
        or exact_complete != possible_complete
        or (upper_complete_known and not exact_complete)
        or (exact_complete and lower_metrics
            and not lower_metrics["reference_available"])
    )
    return {
        "candidate_id": candidate_id,
        "event_id": event["event_id"],
        "event_date": event["event_date"],
        "category": event["category"],
        "shape_cell": contexts[0]["feature"].get("shape_cell"),
        "lower_complete": exact_complete,
        "observed_complete": exact_complete,
        "upper_complete": possible_complete,
        "upper_complete_with_known_price": upper_complete_known,
        "censored": censored,
        "lower_metrics": lower_metrics,
        "upper_metrics": upper_metrics,
        "leg_references_cents": references,
        "lower_leg_results": lower,
        "upper_leg_results": upper,
    }


def aggregate_candidate(
    candidate: Mapping[str, Any],
    outcomes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if len(outcomes) != D_REQUIRED:
        raise FitError(f"candidate changed D: {candidate['candidate_id']}")
    exact = [row for row in outcomes if row["lower_complete"]]
    best = [row for row in outcomes if row["upper_complete"]]
    exact_metric = [
        row["lower_metrics"] for row in exact if row["lower_metrics"]
    ]
    best_metric = [
        row["upper_metrics"] for row in outcomes
        if row["upper_complete_with_known_price"] and row["upper_metrics"]
    ]
    raw = {
        "D": D_REQUIRED,
        "C": len(exact),
        "PC": sum(bool(row["PC"]) for row in exact_metric),
        "NC": sum(row["NC"] is True for row in exact_metric),
        "IC": sum(row["IC"] is True for row in exact_metric),
        "X": sum(bool(row["censored"]) for row in outcomes),
        "censored": sum(bool(row["censored"]) for row in outcomes),
    }
    bounds = {
        "C": {"worst": len(exact), "observed": len(exact),
              "best": len(best)},
        "PC": {
            "worst": raw["PC"],
            "observed": raw["PC"],
            "best_known_price": sum(bool(row["PC"]) for row in best_metric),
            "best_including_unpriced_censoring": (
                sum(bool(row["PC"]) for row in best_metric)
                + sum(row["upper_complete"]
                      and not row["upper_complete_with_known_price"]
                      for row in outcomes)
            ),
        },
        "NC": {
            "worst": raw["NC"],
            "observed": raw["NC"],
            "best_known_reference": sum(row["NC"] is True
                                        for row in best_metric),
            "best_including_unreferenced_censoring": (
                sum(row["NC"] is True for row in best_metric)
                + sum(row["upper_complete"] and (
                    not row["upper_complete_with_known_price"]
                    or not (row["upper_metrics"] or {}).get(
                        "reference_available", False)
                ) for row in outcomes)
            ),
        },
        "IC": {
            "worst": raw["IC"],
            "observed": raw["IC"],
            "best_known_reference": sum(row["IC"] is True
                                        for row in best_metric),
            "best_including_unreferenced_censoring": (
                sum(row["IC"] is True for row in best_metric)
                + sum(row["upper_complete"] and (
                    not row["upper_complete_with_known_price"]
                    or not (row["upper_metrics"] or {}).get(
                        "reference_available", False)
                ) for row in outcomes)
            ),
        },
    }
    pair_deltas = [
        float(row["pair_delta"]) for row in exact_metric
        if row.get("pair_delta") is not None
    ]
    combined_costs = [
        float(row["combined_cost"]) for row in exact_metric
    ]
    leg_deltas = [
        float(delta) for row in exact_metric
        if row.get("leg_deltas") for delta in row["leg_deltas"]
    ]
    by_date = Counter(row["event_date"] for row in exact)
    by_category = Counter(row["category"] for row in exact)
    by_cell = Counter(
        str(row.get("shape_cell") or "missing") for row in exact
    )
    def summarize_group(group_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        group_rows = [row for row in group_rows if row.get("lower_metrics")]
        group_deltas = [
            float(row["lower_metrics"]["pair_delta"]) for row in group_rows
            if row["lower_metrics"].get("pair_delta") is not None
        ]
        group_costs = [
            float(row["lower_metrics"]["combined_cost"])
            for row in group_rows
        ]
        return {
            "C": len(group_rows),
            "PC": sum(bool(row["lower_metrics"]["PC"])
                     for row in group_rows),
            "NC": sum(row["lower_metrics"]["NC"] is True
                     for row in group_rows),
            "IC": sum(row["lower_metrics"]["IC"] is True
                     for row in group_rows),
            "mean_combined_cost_cents": (
                statistics.mean(group_costs) if group_costs else None
            ),
            "mean_pair_delta_cents": (
                statistics.mean(group_deltas) if group_deltas else None
            ),
        }
    group_metrics: dict[str, dict[str, Any]] = {}
    for category in sorted({str(row["category"]) for row in outcomes}):
        group_metrics[category] = summarize_group([
            row for row in exact if str(row["category"]) == category
        ])
    cell_metrics: dict[str, dict[str, Any]] = {}
    for cell in sorted({str(row.get("shape_cell") or "missing")
                        for row in outcomes}):
        cell_metrics[cell] = summarize_group([
            row for row in exact
            if str(row.get("shape_cell") or "missing") == cell
        ])
    failures = Counter()
    for row in outcomes:
        if row["lower_complete"]:
            continue
        leg_states = tuple(sorted(
            str(leg.get("status")) for leg in row["lower_leg_results"]
        ))
        failures["+".join(leg_states)] += 1
    result = {
        "runner_version": RUNNER_VERSION,
        "candidate_id": candidate["candidate_id"],
        "boundary_id": candidate["boundary_id"],
        "policy_id": candidate["policy"]["policy_id"],
        "window": candidate["window"],
        "policy": candidate["policy"],
        "raw": raw,
        "percentages": {
            "C_over_D": raw["C"] / D_REQUIRED,
            "PC_over_D": raw["PC"] / D_REQUIRED,
            "PC_over_C": raw["PC"] / raw["C"] if raw["C"] else None,
            "NC_over_D": raw["NC"] / D_REQUIRED,
            "NC_over_C": raw["NC"] / raw["C"] if raw["C"] else None,
            "IC_over_D": raw["IC"] / D_REQUIRED,
            "IC_over_C": raw["IC"] / raw["C"] if raw["C"] else None,
        },
        "bounds": bounds,
        "combined_cost_cents": {
            "n": len(combined_costs),
            "mean": statistics.mean(combined_costs)
            if combined_costs else None,
            "median": statistics.median(combined_costs)
            if combined_costs else None,
            "p25": percentile(combined_costs, .25),
            "p75": percentile(combined_costs, .75),
        },
        "combined_reference_delta_cents": {
            "n": len(pair_deltas),
            "mean": statistics.mean(pair_deltas) if pair_deltas else None,
            "median": statistics.median(pair_deltas) if pair_deltas else None,
            "p25": percentile(pair_deltas, .25),
            "p75": percentile(pair_deltas, .75),
            "negative_count": sum(value < 0 for value in pair_deltas),
        },
        "individual_leg_reference_delta_cents": {
            "n": len(leg_deltas),
            "mean": statistics.mean(leg_deltas) if leg_deltas else None,
            "median": statistics.median(leg_deltas) if leg_deltas else None,
            "p25": percentile(leg_deltas, .25),
            "p75": percentile(leg_deltas, .75),
            "negative_count": sum(value < 0 for value in leg_deltas),
            "negative_rate": (
                sum(value < 0 for value in leg_deltas) / len(leg_deltas)
                if leg_deltas else None
            ),
        },
        "pairs_by_date": dict(sorted(by_date.items())),
        "pairs_per_day": len(exact) / 9,
        "pairs_by_category": dict(sorted(by_category.items())),
        "pairs_by_shape_cell": dict(sorted(by_cell.items())),
        "metrics_by_category": group_metrics,
        "metrics_by_shape_cell": cell_metrics,
        "failure_funnel": dict(failures.most_common()),
        "distance_from_75pct_negative_pair_target": {
            "required_count": math.ceil(.75 * D_REQUIRED),
            "observed_bound_NC_shortfall": max(
                0, math.ceil(.75 * D_REQUIRED) - raw["NC"]
            ),
            "best_bound_NC_shortfall": max(
                0,
                math.ceil(.75 * D_REQUIRED)
                - bounds["NC"]["best_including_unreferenced_censoring"],
            ),
            "verdict": (
                "supported"
                if raw["NC"] >= math.ceil(.75 * D_REQUIRED)
                else (
                    "not_supported"
                    if bounds["NC"][
                        "best_including_unreferenced_censoring"
                    ] < math.ceil(.75 * D_REQUIRED)
                    else "unresolved_bounds_straddle_target"
                )
            ),
            "not_an_empirical_ceiling_when_X_positive": raw["X"] > 0,
        },
    }
    return result


def candidate_grid(spec: Mapping[str, Any]) -> list[dict[str, Any]]:
    grid = spec.get("boundary_grid") or {}
    starts = grid.get("left_edge_hours_before_schedule") or []
    corridors = grid.get("schedule_only_corridor_minutes") or []
    policies = spec.get("policies") or []
    candidates = []
    for hours in starts:
        for corridor in corridors:
            boundary_id = f"tminus_{int(hours)}h__corridor_{int(corridor)}m"
            for policy in policies:
                policy_id = str(policy.get("policy_id") or "")
                candidates.append({
                    "candidate_id": f"{boundary_id}__{policy_id}",
                    "boundary_id": boundary_id,
                    "window": {
                        "left_edge_hours_before_schedule": int(hours),
                        "schedule_only_corridor_minutes": int(corridor),
                        "left_edge_authority": (
                            "contemporaneous_exchange_catalog_schedule"
                        ),
                        "right_edge_authority": (
                            "exact REAL_START_LEDGER point where verified; "
                            f"otherwise schedule_plus_{int(corridor)}m_or_"
                            "known-live best-case bound with X censoring"
                        ),
                    },
                    "policy": dict(policy),
                })
    if not candidates:
        raise FitError("empty candidate grid")
    return candidates


def select_candidate(
    results: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    # Pre-declared conservative objective: maximize proven negative-pair
    # capture, then proven completion, then both-negative legs, then under-par.
    return min(
        results,
        key=lambda row: (
            -int(row["raw"]["NC"]),
            -int(row["raw"]["C"]),
            -int(row["raw"]["IC"]),
            -int(row["raw"]["PC"]),
            int(row["raw"]["censored"]),
            str(row["candidate_id"]),
        ),
    )


def ablation_candidates(
    selected: Mapping[str, Any],
) -> list[dict[str, Any]]:
    base_policy = dict(selected["policy"])
    families = [
        "macrostructure",
        "limited_depth_pressure",
        "true_print_decision_flow",
        "first_leg_fill_state",
        "own_order_decision_attribution",
        "full_depth_sequence",
    ]
    out = []
    for family in families:
        policy = dict(base_policy)
        if family == "macrostructure":
            policy["ablate_macrostructure"] = True
            if policy["placement_rule"] == "shape_cell_offset":
                policy["placement_rule"] = "touch"
        elif family == "limited_depth_pressure":
            policy["ablate_pressure"] = True
            if policy["placement_rule"] in {
                "depth_support", "pressure_aware"
            }:
                policy["placement_rule"] = "touch"
        elif family == "true_print_decision_flow":
            policy["max_moves"] = 0
        elif family == "first_leg_fill_state":
            policy["first_fill_response"] = "hold"
        elif family in {
            "own_order_decision_attribution", "full_depth_sequence"
        }:
            # These families are not decision-active where exact attribution
            # or sequence-valid full depth is unavailable.  Physical queue
            # evidence remains mandatory and is never ablated.
            policy["inactive_ablation_reason"] = (
                "family_not_decision_active_in_july_instrument"
            )
        policy["policy_id"] = (
            str(base_policy["policy_id"]) + "__without__" + family
        )
        out.append({
            "candidate_id": (
                str(selected["candidate_id"]) + "__without__" + family
            ),
            "boundary_id": selected["boundary_id"],
            "window": dict(selected["window"]),
            "policy": policy,
            "ablation_family": family,
        })
    return out


def instrument_stage_candidates(
    selected: Mapping[str, Any],
    causal_template: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Hold mechanics/boundary fixed while adding feature tiers."""
    stages = []
    definitions = [
        (
            "bbo_prints_baseline",
            {"ablate_macrostructure": True, "ablate_pressure": True},
        ),
        (
            "top5_pressure_enhancement",
            {
                "ablate_macrostructure": True,
                "ablate_pressure": False,
                "use_top20_pressure": False,
            },
        ),
        (
            "limited_top20_pressure_enhancement",
            {
                "ablate_macrostructure": True,
                "ablate_pressure": False,
                "use_top20_pressure": True,
            },
        ),
        (
            "full_causal_stack",
            {
                "ablate_macrostructure": False,
                "ablate_pressure": False,
                "use_top20_pressure": True,
            },
        ),
    ]
    for stage, overrides in definitions:
        policy = dict(causal_template)
        policy.update(overrides)
        # Keep the sibling response on BBO touch so the feature-stage
        # comparison does not silently introduce top-five support selection.
        policy["first_fill_response"] = "reaim_touch"
        policy["policy_id"] = (
            str(causal_template["policy_id"]) + "__stage__" + stage
        )
        stages.append({
            "candidate_id": (
                str(selected["boundary_id"]) + "__stage__" + stage
            ),
            "boundary_id": selected["boundary_id"],
            "window": dict(selected["window"]),
            "policy": policy,
            "instrument_stage": stage,
        })
    return stages


def build_contexts(
    events: Sequence[Mapping[str, Any]],
    prints: Mapping[str, Sequence[Mapping[str, Any]]],
    premarket_dir: Path,
    recovered_premarket_dir: Path,
    starts_by_event: Mapping[str, Mapping[str, Any]],
    shape_table: Mapping[str, Any],
    connection: sqlite3.Connection,
    starts: Sequence[int],
    max_corridor: int,
    depth_recorder_dir: Path,
    feature_output: Path,
) -> tuple[
    dict[tuple[str, int], list[dict[str, Any]]],
    dict[str, Any],
]:
    result: dict[tuple[str, int], list[dict[str, Any]]] = {}
    feature_rows: list[dict[str, Any]] = []
    for event_index, event in enumerate(events, 1):
        scheduled = parse_utc(
            event["scheduled_start_exchange_ts"],
            "scheduled_start_exchange_ts",
        )
        earliest = scheduled - max(starts) * 3600 - 301
        start_row = starts_by_event[str(event["event_id"])]
        start_horizons = [scheduled + max_corridor * 60]
        for field in (
            "verified_start_utc", "known_live_by_utc",
            "safe_prestart_cutoff_utc",
        ):
            if start_row.get(field):
                start_horizons.append(
                    parse_utc(start_row[field], field)
                )
        latest = max(start_horizons)
        leg_data = []
        for leg in event["legs"]:
            ticker = str(leg["ticker"])
            top5_path = premarket_dir / f"{ticker}.csv.gz"
            if not top5_path.is_file():
                top5_path = recovered_premarket_dir / f"{ticker}.csv.gz"
            snapshots = load_top5(
                top5_path, ticker, earliest, latest,
            )
            leg_data.append({
                "ticker": ticker,
                "leg": leg.get("leg"),
                "snapshots": snapshots,
                "prints": list(prints.get(ticker, [])),
            })
        for hours in starts:
            left = scheduled - hours * 3600
            first = [
                snapshot_after(
                    context["snapshots"], left,
                    scheduled + max_corridor * 60,
                )
                for context in leg_data
            ]
            mids = [
                (float(row["best_bid"]) + float(row["best_ask"])) / 2
                if row else None for row in first
            ]
            favorite_index = (
                0 if mids[0] is not None and mids[1] is not None
                and float(mids[0]) >= float(mids[1]) else 1
            )
            contexts: list[dict[str, Any]] = []
            for leg_index, context in enumerate(leg_data):
                snapshot = first[leg_index]
                feature: dict[str, Any] = {
                    "event_id": event["event_id"],
                    "event_date": event["event_date"],
                    "category": event["category"],
                    "ticker": context["ticker"],
                    "leg": context["leg"],
                    "boundary_hours_before_schedule": hours,
                    "schedule_source": event.get("schedule_source"),
                    "schedule_confidence": (
                        "catalog_snapshot_observed_before_window"
                        if parse_utc(
                            event["schedule_observed_exchange_ts"],
                            "schedule_observed_exchange_ts",
                        ) <= left else "catalog_snapshot_observed_after_left"
                    ),
                    "full_depth_sequence_valid": False,
                    "full_depth_missing_reason": (
                        "development ws archive requires separate "
                        "sequence/snapshot coverage gate"
                    ),
                    "top20_snapshot_available": False,
                    "own_historical_order_volume_attributable": False,
                    "hypothetical_own_posted_quantity": LOT,
                }
                if snapshot is None or mids[0] is None or mids[1] is None:
                    feature.update({
                        "top5_available": False,
                        "causal_post_utc": None,
                        "causal_post_time_basis": (
                            "local_premarket_ticks_receipt_et"
                        ),
                        "missing_reason": (
                            "no causal top5 snapshot at/after left edge"
                        ),
                    })
                else:
                    timestamp = float(snapshot["ts"])
                    feature.update({
                        "top5_available": True,
                        "causal_post_utc": timestamp,
                        "causal_post_time_basis": (
                            "local_premarket_ticks_receipt_et"
                        ),
                        "minutes_to_scheduled_start": (
                            scheduled - timestamp
                        ) / 60,
                        "market_mid_cents": mids[leg_index],
                        "sibling_mid_cents": mids[1 - leg_index],
                    })
                    feature.update(depth_features(
                        snapshot, context["snapshots"]
                    ))
                    feature.update(complement_normalized_features(
                        snapshot, first[1 - leg_index]
                    ))
                    feature.update(trade_features(
                        context["prints"], timestamp
                    ))
                    feature.update(shape_context(
                        shape_table,
                        str(event["category"]),
                        float(mids[leg_index]),
                        float(mids[1 - leg_index]),
                        (scheduled - timestamp) / 60,
                        (
                            "favorite" if leg_index == favorite_index
                            else "underdog"
                        ),
                    ))
                    feature.update(macro_book_context(
                        connection,
                        str(event["event_id"]),
                        context["ticker"],
                        timestamp,
                        float(mids[leg_index]),
                    ))
                contexts.append({
                    **context,
                    "feature": feature,
                })
                feature_rows.append(feature)
            result[(str(event["event_id"]), hours)] = contexts
        if event_index % 50 == 0 or event_index == len(events):
            print(
                f"feature_contexts={event_index}/{len(events)}",
                flush=True,
            )
    top20_scan = apply_top20_features(feature_rows, depth_recorder_dir)
    feature_output.parent.mkdir(parents=True, exist_ok=True)
    with feature_output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in feature_rows:
            handle.write(compact(row) + "\n")
    return result, top20_scan


def event_feature_rows(
    event: Mapping[str, Any],
    leg_data: Sequence[Mapping[str, Any]],
    shape_table: Mapping[str, Any],
    connection: sqlite3.Connection,
    starts: Sequence[int],
    max_corridor: int,
) -> list[dict[str, Any]]:
    """Build compact causal feature rows for one event."""
    scheduled = parse_utc(
        event["scheduled_start_exchange_ts"],
        "scheduled_start_exchange_ts",
    )
    output: list[dict[str, Any]] = []
    for hours in starts:
        left = scheduled - hours * 3600
        first = [
            snapshot_after(
                context["snapshots"], left,
                scheduled + max_corridor * 60,
            )
            for context in leg_data
        ]
        mids = [
            (float(row["best_bid"]) + float(row["best_ask"])) / 2
            if row else None for row in first
        ]
        favorite_index = (
            0 if mids[0] is not None and mids[1] is not None
            and float(mids[0]) >= float(mids[1]) else 1
        )
        for leg_index, context in enumerate(leg_data):
            snapshot = first[leg_index]
            feature: dict[str, Any] = {
                "event_id": event["event_id"],
                "event_date": event["event_date"],
                "category": event["category"],
                "ticker": context["ticker"],
                "leg": context["leg"],
                "boundary_hours_before_schedule": hours,
                "schedule_source": event.get("schedule_source"),
                "schedule_confidence": (
                    "catalog_snapshot_observed_before_window"
                    if parse_utc(
                        event["schedule_observed_exchange_ts"],
                        "schedule_observed_exchange_ts",
                    ) <= left else "catalog_snapshot_observed_after_left"
                ),
                "full_depth_sequence_valid": False,
                "full_depth_missing_reason": (
                    "no ladder-bearing snapshot plus gap-free sequence "
                    "epoch in the recovered July ws_depth archive"
                ),
                "top20_snapshot_available": False,
                "own_historical_order_volume_attributable": False,
                "hypothetical_own_posted_quantity": LOT,
            }
            if snapshot is None or mids[0] is None or mids[1] is None:
                feature.update({
                    "top5_available": False,
                    "causal_post_utc": None,
                    "causal_post_time_basis": (
                        "local_premarket_ticks_receipt_et"
                    ),
                    "missing_reason": (
                        "no causal top5 snapshot at/after left edge"
                    ),
                })
            else:
                timestamp = float(snapshot["ts"])
                feature.update({
                    "top5_available": True,
                    "causal_post_utc": timestamp,
                    "causal_post_time_basis": (
                        "local_premarket_ticks_receipt_et"
                    ),
                    "minutes_to_scheduled_start": (
                        scheduled - timestamp
                    ) / 60,
                    "market_mid_cents": mids[leg_index],
                    "sibling_mid_cents": mids[1 - leg_index],
                })
                feature.update(depth_features(
                    snapshot, context["snapshots"]
                ))
                feature.update(complement_normalized_features(
                    snapshot, first[1 - leg_index]
                ))
                feature.update(trade_features(
                    context["prints"], timestamp
                ))
                feature.update(shape_context(
                    shape_table,
                    str(event["category"]),
                    float(mids[leg_index]),
                    float(mids[1 - leg_index]),
                    (scheduled - timestamp) / 60,
                    (
                        "favorite" if leg_index == favorite_index
                        else "underdog"
                    ),
                ))
                feature.update(macro_book_context(
                    connection,
                    str(event["event_id"]),
                    context["ticker"],
                    timestamp,
                    float(mids[leg_index]),
                ))
            output.append(feature)
    return output


def build_feature_matrix_streamed(
    events: Sequence[Mapping[str, Any]],
    archive: PrintArchive,
    premarket_dir: Path,
    recovered_premarket_dir: Path,
    starts_by_event: Mapping[str, Mapping[str, Any]],
    shape_table: Mapping[str, Any],
    connection: sqlite3.Connection,
    starts: Sequence[int],
    max_corridor: int,
    depth_recorder_dir: Path,
    feature_output: Path,
    cache_root: Path,
    cache_key: str,
) -> tuple[dict[tuple[str, int, str], dict[str, Any]], dict[str, Any]]:
    feature_rows: list[dict[str, Any]] = []
    for event_index, event in enumerate(events, 1):
        leg_data = load_event_market_data(
            event, archive, premarket_dir, recovered_premarket_dir,
            starts_by_event, starts, max_corridor, cache_root, cache_key,
        )
        feature_rows.extend(event_feature_rows(
            event, leg_data, shape_table, connection, starts, max_corridor
        ))
        if event_index % 25 == 0 or event_index == len(events):
            print(
                f"feature_events={event_index}/{len(events)}",
                flush=True,
            )
    top20_scan = apply_top20_features(
        feature_rows, depth_recorder_dir
    )
    feature_output.parent.mkdir(parents=True, exist_ok=True)
    with feature_output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in feature_rows:
            handle.write(compact(row) + "\n")
    feature_map = {
        (
            str(row["event_id"]),
            int(row["boundary_hours_before_schedule"]),
            str(row["ticker"]),
        ): row
        for row in feature_rows
    }
    if len(feature_map) != len(events) * len(starts) * 2:
        raise FitError("streamed feature key cardinality changed")
    return feature_map, top20_scan


def contexts_for_event(
    event: Mapping[str, Any],
    leg_data: Sequence[Mapping[str, Any]],
    starts: Sequence[int],
    feature_map: Mapping[
        tuple[str, int, str], Mapping[str, Any]
    ],
) -> dict[int, list[dict[str, Any]]]:
    output: dict[int, list[dict[str, Any]]] = {}
    event_id = str(event["event_id"])
    for hours in starts:
        rows = []
        for context in leg_data:
            ticker = str(context["ticker"])
            feature = feature_map.get((event_id, int(hours), ticker))
            if feature is None:
                raise FitError(
                    f"missing streamed feature: {event_id}/{hours}/{ticker}"
                )
            rows.append({
                **context,
                "feature": feature,
            })
        output[int(hours)] = rows
    return output


def evaluate_candidate_event_with_start(
    candidate: Mapping[str, Any],
    event: Mapping[str, Any],
    contexts: Sequence[Mapping[str, Any]],
    start: Mapping[str, Any],
) -> dict[str, Any]:
    hours = int(
        candidate["window"]["left_edge_hours_before_schedule"]
    )
    corridor = int(
        candidate["window"]["schedule_only_corridor_minutes"]
    )
    scheduled = parse_utc(
        event["scheduled_start_exchange_ts"],
        "scheduled_start_exchange_ts",
    )
    left = scheduled - hours * 3600
    exact_right = (
        parse_utc(start["verified_start_utc"], "verified_start_utc")
        if start.get("verified_start_utc") else None
    )
    safe_right = (
        parse_utc(
            start["safe_prestart_cutoff_utc"],
            "safe_prestart_cutoff_utc",
        )
        if start.get("safe_prestart_cutoff_utc") else None
    )
    known_live_by = (
        parse_utc(start["known_live_by_utc"], "known_live_by_utc")
        if start.get("known_live_by_utc") else None
    )
    boundary_exact = (
        exact_right is not None
        and start.get("boundary_censored") is False
    )
    boundary_safe = (
        safe_right is not None
        and start.get("contradiction") is not True
    )
    safe_inclusive = start.get("safe_prestart_cutoff_inclusive")
    right = (
        (
            safe_right
            if safe_inclusive is not False
            else math.nextafter(safe_right, -math.inf)
        ) if boundary_safe
        else (known_live_by or scheduled + corridor * 60)
    )
    if boundary_safe and left >= right:
        empty_legs = [
            {
                "status": "window_left_not_before_real_start",
                "quantity": 0.0,
                "cost": 0.0,
                "vwap": None,
                "first_fill_ts": None,
                "completion_ts": None,
            }
            for _ in event["legs"]
        ]
        outcome = {
            "candidate_id": str(candidate["candidate_id"]),
            "event_id": str(event["event_id"]),
            "event_date": event["event_date"],
            "category": event["category"],
            "shape_cell": contexts[0]["feature"].get("shape_cell"),
            "lower_complete": False,
            "observed_complete": False,
            "upper_complete": False,
            "upper_complete_with_known_price": False,
            "censored": False,
            "lower_metrics": None,
            "upper_metrics": None,
            "leg_references_cents": [None, None],
            "lower_leg_results": empty_legs,
            "upper_leg_results": empty_legs,
        }
    else:
        outcome = event_candidate_outcome(
            str(candidate["candidate_id"]),
            candidate["policy"],
            event,
            contexts,
            left, right, scheduled,
        )
    outcome["start_state"] = start["start_state"]
    outcome["boundary_exact"] = boundary_exact
    outcome["boundary_safe_prestart"] = boundary_safe
    outcome["right_edge_utc"] = dt.datetime.fromtimestamp(
        right, UTC
    ).isoformat()
    outcome["right_edge_time_basis"] = (
        start.get("safe_prestart_cutoff_time_basis")
        if boundary_safe else (
            start.get("known_live_by_time_basis")
            or "schedule_plus_declared_corridor"
        )
    )
    outcome["right_edge_inclusive"] = (
        True if not boundary_safe else safe_inclusive is not False
    )
    if not boundary_safe:
        # A fill conditional on a one-sided/schedule bound is an upper
        # bound only. It cannot enter observed C/NC/IC.
        outcome["conditional_lower_queue_complete"] = outcome[
            "lower_complete"
        ]
        outcome["conditional_lower_metrics"] = outcome["lower_metrics"]
        outcome["lower_complete"] = False
        outcome["observed_complete"] = False
        outcome["lower_metrics"] = None
        outcome["censored"] = True
        if outcome.get("upper_metrics"):
            upper = dict(outcome["upper_metrics"])
            upper.update({
                "reference_available": False,
                "leg_deltas": None,
                "pair_delta": None,
                "NC": None,
                "IC": None,
            })
            outcome["upper_metrics"] = upper
    return outcome


def evaluate_candidates(
    candidates: Sequence[Mapping[str, Any]],
    events: Sequence[Mapping[str, Any]],
    contexts: Mapping[tuple[str, int], Sequence[Mapping[str, Any]]],
    starts_by_event: Mapping[str, Mapping[str, Any]],
    detail_output: Path,
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    summaries: list[dict[str, Any]] = []
    outcome_map: dict[str, list[dict[str, Any]]] = {}
    detail_output.parent.mkdir(parents=True, exist_ok=True)
    with detail_output.open("w", encoding="utf-8", newline="\n") as handle:
        for candidate_index, candidate in enumerate(candidates, 1):
            hours = int(
                candidate["window"]["left_edge_hours_before_schedule"]
            )
            outcomes = []
            for event in events:
                event_id = str(event["event_id"])
                start = starts_by_event.get(event_id)
                if start is None:
                    raise FitError(f"missing real-start row: {event_id}")
                outcome = evaluate_candidate_event_with_start(
                    candidate, event, contexts[(event_id, hours)], start
                )
                outcomes.append(outcome)
                handle.write(compact(outcome) + "\n")
            summary = aggregate_candidate(candidate, outcomes)
            summaries.append(summary)
            outcome_map[str(candidate["candidate_id"])] = outcomes
            print(
                f"candidate={candidate_index}/{len(candidates)} "
                f"id={candidate['candidate_id']} "
                f"C={summary['raw']['C']} NC={summary['raw']['NC']} "
                f"censored={summary['raw']['censored']}",
                flush=True,
            )
    return summaries, outcome_map


def evaluate_candidates_streamed(
    candidates: Sequence[Mapping[str, Any]],
    events: Sequence[Mapping[str, Any]],
    archive: PrintArchive,
    premarket_dir: Path,
    recovered_premarket_dir: Path,
    starts_by_event: Mapping[str, Mapping[str, Any]],
    starts: Sequence[int],
    max_corridor: int,
    feature_map: Mapping[
        tuple[str, int, str], Mapping[str, Any]
    ],
    cache_root: Path,
    cache_key: str,
    detail_output: Path,
) -> list[dict[str, Any]]:
    """Evaluate event-major and aggregate candidate-major from disk shards."""
    detail_output.parent.mkdir(parents=True, exist_ok=True)
    shard_root = detail_output.with_name(
        detail_output.name + ".by_candidate"
    )
    shard_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(shard_root, 0o700)
    except OSError:
        pass
    shard_paths = [
        shard_root / f"{index:04d}.jsonl"
        for index in range(len(candidates))
    ]
    existing = [path for path in shard_paths if path.exists()]
    if existing:
        raise FitError(
            "candidate detail shards already exist; preserve them and "
            "choose a new detail output"
        )
    shard_handles = [
        path.open("w", encoding="utf-8", newline="\n")
        for path in shard_paths
    ]
    combined = detail_output.open("w", encoding="utf-8", newline="\n")
    try:
        for event_index, event in enumerate(events, 1):
            event_id = str(event["event_id"])
            start = starts_by_event.get(event_id)
            if start is None:
                raise FitError(f"missing real-start row: {event_id}")
            leg_data = load_event_market_data(
                event, archive, premarket_dir, recovered_premarket_dir,
                starts_by_event, starts, max_corridor, cache_root,
                cache_key,
            )
            contexts = contexts_for_event(
                event, leg_data, starts, feature_map
            )
            event_outcome_cache: dict[
                tuple[int, str, int | None], dict[str, Any]
            ] = {}
            for index, candidate in enumerate(candidates):
                hours = int(
                    candidate["window"][
                        "left_edge_hours_before_schedule"
                    ]
                )
                # Corridor variants are mathematically identical when an
                # exact/safe cutoff or a one-sided known-live bound supplies
                # the right edge.  Cache that identity rather than replaying
                # the same snapshots and prints four times.
                corridor_discriminator = corridor_cache_discriminator(
                    candidate, start
                )
                outcome_key = (
                    hours,
                    compact(candidate["policy"]),
                    corridor_discriminator,
                )
                cached = event_outcome_cache.get(outcome_key)
                if cached is None:
                    outcome = evaluate_candidate_event_with_start(
                        candidate, event, contexts[hours], start
                    )
                    event_outcome_cache[outcome_key] = copy.deepcopy(
                        outcome
                    )
                else:
                    outcome = copy.deepcopy(cached)
                    outcome["candidate_id"] = str(
                        candidate["candidate_id"]
                    )
                line = compact(outcome) + "\n"
                combined.write(line)
                shard_handles[index].write(line)
            if event_index % 10 == 0 or event_index == len(events):
                print(
                    f"candidate_events={event_index}/{len(events)} "
                    f"candidates={len(candidates)}",
                    flush=True,
                )
    finally:
        combined.close()
        for handle in shard_handles:
            handle.close()
    for path in [detail_output, *shard_paths]:
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    summaries = []
    for index, (candidate, path) in enumerate(
        zip(candidates, shard_paths), 1
    ):
        outcomes = read_jsonl(path)
        summary = aggregate_candidate(candidate, outcomes)
        summaries.append(summary)
        print(
            f"candidate={index}/{len(candidates)} "
            f"id={candidate['candidate_id']} "
            f"C={summary['raw']['C']} NC={summary['raw']['NC']} "
            f"censored={summary['raw']['censored']}",
            flush=True,
        )
    manifest = {
        "schema_version": RUNNER_VERSION + "-candidate-shards-v1",
        "candidate_count": len(candidates),
        "D_per_candidate": D_REQUIRED,
        "combined_detail": str(detail_output.name),
        "combined_detail_sha256": sha256_file(detail_output),
        "shards": [
            {
                "candidate_id": str(candidate["candidate_id"]),
                "file": path.name,
                "sha256": sha256_file(path),
            }
            for candidate, path in zip(candidates, shard_paths)
        ],
    }
    manifest_path = shard_root / "MANIFEST.json"
    write_json(manifest_path, manifest)
    try:
        os.chmod(manifest_path, 0o600)
    except OSError:
        pass
    return summaries


def corridor_cache_discriminator(
    candidate: Mapping[str, Any],
    start: Mapping[str, Any],
) -> int | None:
    """Return a corridor only when it actually supplies the right edge."""
    has_safe_right = (
        start.get("safe_prestart_cutoff_utc") is not None
        and start.get("contradiction") is not True
    )
    has_known_live_right = start.get("known_live_by_utc") is not None
    if has_safe_right or has_known_live_right:
        return None
    return int(
        candidate["window"]["schedule_only_corridor_minutes"]
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> int:
    events_path = Path(args.events).resolve()
    validation_path = Path(args.validation_summary).resolve()
    tape_manifest_path = Path(args.tape_manifest).resolve()
    prints_path = Path(args.prints).resolve()
    start_ledger_path = Path(args.start_ledger).resolve()
    source_coverage_path = Path(args.source_coverage_summary).resolve()
    materialization_path = Path(
        args.spaces_materialization_summary
    ).resolve()
    candidate_spec_path = Path(args.candidate_spec).resolve()
    shape_prior_path = Path(args.shape_prior).resolve()
    feature_output = Path(args.feature_output).resolve()
    detail_output = Path(args.detail_output).resolve()
    summary_output = Path(args.summary_output).resolve()
    ablation_output = Path(args.ablation_output).resolve()
    coverage_output = Path(args.coverage_output).resolve()
    event_cache_base = Path(args.event_cache_dir).resolve()

    validation = load_json(validation_path)
    if validation.get("gate_pass") is not True or validation.get("D") != 804:
        raise FitError("lifecycle validation gate did not pass at D=804")
    tape_manifest = load_json(tape_manifest_path)
    if not (
        tape_manifest.get("pagination", {}).get(
            "all_terminal_cursors_empty"
        ) is True
        and tape_manifest.get("pagination", {}).get(
            "failed_ticker_count"
        ) == 0
        and tape_manifest.get("immutable_denominator", {}).get(
            "required_leg_tickers"
        ) == 1608
    ):
        raise FitError("public tape pagination/source gate failed")
    events = load_events(events_path)
    starts = read_jsonl(start_ledger_path)
    if len(starts) != D_REQUIRED:
        raise FitError(f"real-start D changed: {len(starts)}")
    starts_by_event = {
        str(row.get("event_id") or ""): row for row in starts
    }
    if len(starts_by_event) != D_REQUIRED:
        raise FitError("duplicate/missing real-start event ids")
    if {
        str(row["event_id"]) for row in events
    } != set(starts_by_event):
        raise FitError("real-start ledger event set changed")
    source_coverage = load_json(source_coverage_path)
    if (
        source_coverage.get("D") != D_REQUIRED
        or source_coverage.get("required_tickers") != 1608
    ):
        raise FitError("source coverage gate changed D/ticker count")
    materialization = load_json(materialization_path)
    if not (
        materialization.get("all_exact") is True
        and materialization.get("prefix") == "ticks"
        and materialization.get("object_count") == 1608
        and materialization.get("states") == {
            "exact_spaces_object": 1608
        }
    ):
        raise FitError("Spaces top-five materialization gate failed")
    spec = load_json(candidate_spec_path)
    starts = [
        int(value) for value in
        spec["boundary_grid"]["left_edge_hours_before_schedule"]
    ]
    corridors = [
        int(value) for value in
        spec["boundary_grid"]["schedule_only_corridor_minutes"]
    ]
    expected_print_hash = tape_manifest["artifacts"][
        "normalized_true_prints"
    ]["sha256"]
    archive = PrintArchive(prints_path, expected_print_hash)
    shape_prior = load_json(shape_prior_path)
    shape_table = shape_prior.get("table")
    if not isinstance(shape_table, dict):
        raise FitError("shape prior lacks table")
    database_uri = (
        "file:" + str(Path(args.database).resolve())
        + "?mode=ro&immutable=1"
    )
    database_projection_receipt = None
    if args.database_projection_receipt:
        projection_path = Path(
            args.database_projection_receipt
        ).resolve()
        database_projection_receipt = load_json(projection_path)
        if (
            (database_projection_receipt.get("event_ledger") or {})
            .get("sha256") != sha256_file(events_path)
            or (database_projection_receipt.get("projection") or {})
            .get("sha256")
            != sha256_file(Path(args.database).resolve())
            or (database_projection_receipt.get("event_ledger") or {})
            .get("D") != D_REQUIRED
        ):
            raise FitError(
                "database projection receipt/input binding failed"
            )
    cache_receipt = {
        "runner_version": RUNNER_VERSION,
        "events_sha256": sha256_file(events_path),
        "public_prints_sha256": archive.sha256,
        "start_ledger_sha256": sha256_file(start_ledger_path),
        "source_coverage_sha256": sha256_file(source_coverage_path),
        "spaces_materialization_sha256": sha256_file(
            materialization_path
        ),
        "candidate_spec_sha256": sha256_file(candidate_spec_path),
        "database_projection_receipt_sha256": (
            sha256_file(projection_path)
            if database_projection_receipt is not None else None
        ),
    }
    cache_key = hashlib.sha256(
        compact(cache_receipt).encode()
    ).hexdigest()
    event_cache_root = event_cache_base / cache_key
    prebuild_event_caches(
        events,
        archive,
        Path(args.premarket_dir).resolve(),
        Path(args.recovered_premarket_dir).resolve(),
        starts_by_event,
        starts,
        max(corridors),
        event_cache_root,
        cache_key,
        args.cache_workers,
    )
    connection = sqlite3.connect(database_uri, uri=True)
    try:
        feature_map, top20_scan = build_feature_matrix_streamed(
            events, archive, Path(args.premarket_dir).resolve(),
            Path(args.recovered_premarket_dir).resolve(),
            starts_by_event, shape_table, connection, starts,
            max(corridors),
            Path(args.depth_recorder_dir).resolve(),
            feature_output,
            event_cache_root,
            cache_key,
        )
    finally:
        connection.close()

    candidates = candidate_grid(spec)
    summaries = evaluate_candidates_streamed(
        candidates, events, archive,
        Path(args.premarket_dir).resolve(),
        Path(args.recovered_premarket_dir).resolve(),
        starts_by_event, starts, max(corridors), feature_map,
        event_cache_root, cache_key, detail_output,
    )
    selected = select_candidate(summaries)
    selected_candidate = next(
        candidate for candidate in candidates
        if candidate["candidate_id"] == selected["candidate_id"]
    )
    ablations = ablation_candidates(selected_candidate)
    causal_template = next(
        candidate["policy"] for candidate in candidates
        if candidate["boundary_id"] == selected["boundary_id"]
        and candidate["policy"]["policy_id"]
        == "causal_stack_simultaneous_reaim"
    )
    stage_candidates = instrument_stage_candidates(
        selected, causal_template
    )
    diagnostic_candidates = [*ablations, *stage_candidates]
    diagnostic_detail = detail_output.with_name(
        detail_output.stem + ".diagnostics.jsonl"
    )
    diagnostic_summaries = evaluate_candidates_streamed(
        diagnostic_candidates, events, archive,
        Path(args.premarket_dir).resolve(),
        Path(args.recovered_premarket_dir).resolve(),
        starts_by_event, starts, max(corridors), feature_map,
        event_cache_root, cache_key, diagnostic_detail,
    )
    ablation_summaries = diagnostic_summaries[:len(ablations)]
    for row, candidate in zip(ablation_summaries, ablations):
        row["ablation_family"] = candidate["ablation_family"]
        row["change_vs_selected"] = {
            key: row["raw"][key] - selected["raw"][key]
            for key in ("C", "PC", "NC", "IC", "censored")
        }
    stage_detail = detail_output.with_name(
        detail_output.stem + ".instrument_stages.jsonl"
    )
    stage_summaries = diagnostic_summaries[len(ablations):]
    # The combined diagnostic output is authoritative.  The legacy stage
    # path is a small receipt that points at it rather than duplicating raw
    # outcome evidence.
    write_json(stage_detail, {
        "schema_version": RUNNER_VERSION + "-stage-detail-pointer-v1",
        "combined_diagnostic_detail": diagnostic_detail.name,
        "combined_diagnostic_sha256": sha256_file(diagnostic_detail),
        "stage_candidate_ids": [
            row["candidate_id"] for row in stage_candidates
        ],
    })
    baseline_raw = stage_summaries[0]["raw"]
    for row, candidate in zip(stage_summaries, stage_candidates):
        row["instrument_stage"] = candidate["instrument_stage"]
        row["change_vs_bbo_prints_baseline"] = {
            key: row["raw"][key] - baseline_raw[key]
            for key in ("C", "PC", "NC", "IC", "censored")
        }

    feature_rows = list(feature_map.values())
    usable_full_depth = int(
        source_coverage.get("ticker_counts", {}).get(
            "ws_full_depth_usable", 0
        )
    )
    if usable_full_depth:
        raise FitError(
            "sequence-valid full-depth evidence exists but the full-depth "
            "enhancement has not been implemented in this runner"
        )
    coverage = {
        "runner_version": RUNNER_VERSION,
        "D": 804,
        "required_legs": 1608,
        "feature_rows": len(feature_rows),
        "boundary_left_edge_count": len(starts),
        "top5_available_rows": sum(
            row.get("top5_available") is True for row in feature_rows
        ),
        "top5_missing_rows": sum(
            row.get("top5_available") is not True for row in feature_rows
        ),
        "bookmaker_available_rows": sum(
            row.get("bookmaker_available") is True for row in feature_rows
        ),
        "shape_cell_available_rows": sum(
            row.get("shape_cell_available") is True for row in feature_rows
        ),
        "full_depth_sequence_valid_rows": 0,
        "development_ws_depth_file_count": source_coverage.get(
            "ws_depth", {}
        ).get("file_count", 0),
        "top20_snapshot_available_rows": sum(
            row.get("top20_snapshot_available") is True
            for row in feature_rows
        ),
        "full_depth_enhancement_status": (
            "unavailable; no July12-20 sequence-valid ws_depth epoch"
        ),
        "top20_status": (
            "causal snapshot/change-deduplicated limited-depth enhancement; "
            "not treated as full depth or sequence-continuous"
        ),
        "top20_scan": top20_scan,
        "public_tape_tickers_with_zero_trades": len(
            tape_manifest.get("coverage", {}).get(
                "tickers_with_zero_trades", []
            )
        ),
        "source_hashes": {
            "events": sha256_file(events_path),
            "validation": sha256_file(validation_path),
            "public_tape_manifest": sha256_file(tape_manifest_path),
            "public_prints": archive.sha256,
            "candidate_spec": sha256_file(candidate_spec_path),
            "shape_prior": sha256_file(shape_prior_path),
            "start_ledger": sha256_file(start_ledger_path),
            "source_coverage": sha256_file(source_coverage_path),
            "spaces_materialization": sha256_file(
                materialization_path
            ),
            "database": sha256_file(Path(args.database).resolve()),
            "database_projection_receipt": (
                sha256_file(projection_path)
                if database_projection_receipt is not None else None
            ),
            "event_cache_key": cache_key,
        },
    }
    output = {
        "runner_version": RUNNER_VERSION,
        "status": "fit_complete",
        "selection_rule": [
            "maximize observed/proven NC",
            "maximize observed/proven C",
            "maximize observed/proven IC",
            "maximize observed/proven PC",
            "minimize censored",
            "lexicographic candidate_id",
        ],
        "metric_definitions": {
            "D": "all 804 immutable floor-passing July12-20 games",
            "C": "both legs complete exactly five contracts",
            "PC": "C pair with combined entry VWAP strictly below 100",
            "leg_delta": (
                "leg entry VWAP minus that leg's final positive-size true "
                "print in the frozen Window-1 interval"
            ),
            "NC": "C pair with sum of two leg deltas strictly below zero",
            "IC": "C pair where both individual leg deltas are below zero",
            "censored": (
                "queue bound changes completion, source placement is "
                "unobserved, or completed pair lacks a frozen reference"
            ),
            "X": (
                "games censored by start, queue, source placement, or "
                "missing frozen reference; X remains in D"
            ),
            "subset_law": (
                "PC, NC and IC overlap inside C; they do not partition D"
            ),
        },
        "selected_candidate_id": selected["candidate_id"],
        "selected_result": selected,
        "candidate_count": len(summaries),
        "candidates": summaries,
        "inputs": coverage["source_hashes"],
        "holdout": {
            "viewed": False,
            "reason": (
                "forward dates may be registered only in the committed fit "
                "freeze after this fit result"
            ),
        },
    }
    write_json(summary_output, output)
    write_json(ablation_output, {
        "runner_version": RUNNER_VERSION,
        "selected_candidate_id": selected["candidate_id"],
        "ablations": ablation_summaries,
        "instrument_stages": stage_summaries,
    })
    write_json(coverage_output, coverage)
    print(json.dumps({
        "selected_candidate_id": selected["candidate_id"],
        "raw": selected["raw"],
        "target": selected["distance_from_75pct_negative_pair_target"],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--validation-summary", required=True)
    result.add_argument("--tape-manifest", required=True)
    result.add_argument("--prints", required=True)
    result.add_argument(
        "--event-cache-dir",
        required=True,
        help="owner-only derived event cache outside Git",
    )
    result.add_argument("--cache-workers", type=int, default=1)
    result.add_argument("--start-ledger", required=True)
    result.add_argument("--source-coverage-summary", required=True)
    result.add_argument(
        "--spaces-materialization-summary", required=True
    )
    result.add_argument("--candidate-spec", required=True)
    result.add_argument("--shape-prior", required=True)
    result.add_argument("--premarket-dir", required=True)
    result.add_argument("--recovered-premarket-dir", required=True)
    result.add_argument("--depth-recorder-dir", required=True)
    result.add_argument("--ws-depth-dir", required=True)
    result.add_argument("--database", required=True)
    result.add_argument("--database-projection-receipt")
    result.add_argument("--feature-output", required=True)
    result.add_argument("--detail-output", required=True)
    result.add_argument("--summary-output", required=True)
    result.add_argument("--ablation-output", required=True)
    result.add_argument("--coverage-output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
