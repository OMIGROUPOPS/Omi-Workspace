#!/usr/bin/env python3
"""Strict, fail-closed Window-1 research benchmark.

This instrument is deliberately separate from the live engine.  It consumes a
normalized evidence bundle, builds the denominator before simulation, validates
the queue/print replay against every official entry order (fills *and*
non-fills), and only then permits fit scoring.  Holdout scoring is a separate,
one-shot command which requires a fit-only freeze receipt.

The normalized schemas and command sequence are documented in
``docs/research/window1/REPRODUCTION.md``.  No exit or Window-2 field is read.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


SCHEMA_VERSION = "window1-normalized-v1"
BENCHMARK_VERSION = "window1-benchmark-v1"
BIG4 = {"ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"}
REQUIRED_LOT = 5
PAR_CENTS = 100.0
LEGACY_SUCCESS_CENTS = 97.0
TRUE_PRINT_SOURCES = {
    "public_tape",
    "kalshi_public_trade",
    "exchange_trade",
}
FULL_BOOK_SOURCE = "ws_depth"
DEVELOPMENT_START = "2026-07-12"
DEVELOPMENT_END = "2026-07-20"
FORWARD_HOLDOUT_DAYS = 3
ALLOWED_FLOOR_EXCLUSION = "verified_pre_window_cancel_or_void"
FORBIDDEN_OUTCOME_KEYS = {
    "exit",
    "exit_price",
    "exit_pnl",
    "realized_pnl",
    "settlement",
    "settlement_value",
    "window2",
    "window_2",
    "w2",
}


class BenchmarkError(RuntimeError):
    """A named, user-correctable benchmark contract failure."""


def json_dump(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json_dump(dict(row)) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    if not path.is_file():
        return rows, [{"mismatch_type": "missing_file", "path": str(path)}]
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append({
                    "mismatch_type": "malformed_jsonl",
                    "path": str(path),
                    "line": line_number,
                    "error": str(exc),
                })
                continue
            if not isinstance(value, dict):
                errors.append({
                    "mismatch_type": "non_object_jsonl",
                    "path": str(path),
                    "line": line_number,
                })
                continue
            value["_line"] = line_number
            rows.append(value)
    return rows, errors


def forbidden_outcome_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in FORBIDDEN_OUTCOME_KEYS:
                paths.append(path)
            paths.extend(forbidden_outcome_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(forbidden_outcome_paths(child, f"{prefix}[{index}]"))
    return paths


def parse_exchange_ts(value: Any, field: str) -> float:
    if value is None or value == "":
        raise BenchmarkError(f"missing exchange timestamp: {field}")
    if isinstance(value, (int, float)):
        if not math.isfinite(float(value)):
            raise BenchmarkError(f"non-finite exchange timestamp: {field}")
        return float(value)
    text = str(value).strip().replace("Z", "+00:00")
    try:
        stamp = dt.datetime.fromisoformat(text)
    except ValueError as exc:
        raise BenchmarkError(f"invalid exchange timestamp {field}: {value}") from exc
    if stamp.tzinfo is None:
        raise BenchmarkError(f"timezone-free exchange timestamp: {field}")
    return stamp.timestamp()


def iso_utc(timestamp: float | None) -> str | None:
    if timestamp is None:
        return None
    return dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).isoformat()


def event_day(row: Mapping[str, Any]) -> str:
    day = str(row.get("event_date") or "")
    try:
        return dt.date.fromisoformat(day).isoformat()
    except ValueError as exc:
        raise BenchmarkError(
            f"event {row.get('event_id')} lacks ISO event_date") from exc


def period_for_day(
    day: str,
    forward_holdout_dates: Sequence[str] = (),
) -> str:
    """Classify a day without pretending inspected history is untouched."""
    if DEVELOPMENT_START <= day <= DEVELOPMENT_END:
        return "fit"
    if day in set(forward_holdout_dates):
        return "holdout"
    return "outside_operational_period"


def next_complete_utc_dates(freeze_timestamp: dt.datetime) -> list[str]:
    """Return the three whole UTC dates strictly after the freeze date."""
    if freeze_timestamp.tzinfo is None:
        raise BenchmarkError("freeze timestamp must be timezone-aware")
    anchor = freeze_timestamp.astimezone(dt.timezone.utc).date()
    return [
        (anchor + dt.timedelta(days=offset)).isoformat()
        for offset in range(1, FORWARD_HOLDOUT_DAYS + 1)
    ]


def load_holdout_declaration(
    path: Path,
    freeze: Mapping[str, Any],
    freeze_path: Path,
) -> dict[str, Any]:
    """Validate the external receipt proving freeze/dates were committed."""
    try:
        declaration = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"cannot read holdout declaration: {exc}") from exc
    if not isinstance(declaration, dict):
        raise BenchmarkError("holdout declaration must be a JSON object")
    expected_dates = (freeze.get("forward_holdout") or {}).get("dates")
    if declaration.get("holdout_dates") != expected_dates:
        raise BenchmarkError("holdout declaration changed the frozen dates")
    if declaration.get("source_freeze_sha256") != sha256_file(freeze_path):
        raise BenchmarkError("holdout declaration does not match the freeze receipt")
    commit_sha = str(declaration.get("git_commit_sha") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit_sha):
        raise BenchmarkError("holdout declaration lacks a full committed Git SHA")
    receipt_path = str(declaration.get("freeze_receipt_repo_path") or "")
    receipt_parts = receipt_path.split("/")
    if (not receipt_path or receipt_path.startswith("/")
            or chr(92) in receipt_path or ".." in receipt_parts):
        raise BenchmarkError("holdout declaration has an unsafe freeze receipt path")
    repo_root = Path(__file__).resolve().parents[2]
    committed = subprocess.run(
        ["git", "-C", str(repo_root), "show",
         f"{commit_sha}:{receipt_path}"],
        check=False, capture_output=True)
    if committed.returncode != 0:
        raise BenchmarkError(
            "declared Git commit does not contain the freeze receipt")
    committed_sha256 = hashlib.sha256(committed.stdout).hexdigest()
    if committed_sha256 != declaration.get("source_freeze_sha256"):
        raise BenchmarkError(
            "committed freeze receipt does not match the external freeze")
    if declaration.get("freeze_and_dates_committed_before_holdout") is not True:
        raise BenchmarkError("freeze and holdout dates were not committed before holdout")
    return declaration


def ledger_subset_sha256(
    rows: Sequence[Mapping[str, Any]],
    period: str,
) -> str:
    """Hash one period so future holdout rows cannot rewrite development."""
    normalized = []
    for row in rows:
        if row.get("period") != period:
            continue
        normalized.append({key: value for key, value in row.items()
                           if key != "_line"})
    normalized.sort(key=lambda row: (str(row.get("event_date") or ""),
                                     str(row.get("event_id") or "")))
    digest = hashlib.sha256()
    for row in normalized:
        digest.update(json_dump(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def resolve_window_end(event: Mapping[str, Any], corridor_minutes: int) -> tuple[float, str]:
    """Return a causal right edge; schedule-only rows always get a corridor."""
    if corridor_minutes <= 0:
        raise BenchmarkError("schedule-only corridor must be positive")
    actual = event.get("actual_start_exchange_ts")
    if actual not in (None, ""):
        if not event.get("actual_start_verified"):
            raise BenchmarkError("actual start is present but not independently verified")
        source = str(event.get("actual_start_source") or "")
        if source not in {"sportradar_milestone", "official_start_feed",
                          "exchange_status"}:
            raise BenchmarkError(f"unapproved actual-start source: {source}")
        return parse_exchange_ts(actual, "actual_start_exchange_ts"), source
    scheduled = parse_exchange_ts(event.get("scheduled_start_exchange_ts"),
                                  "scheduled_start_exchange_ts")
    return scheduled + corridor_minutes * 60, f"schedule_plus_{corridor_minutes}m_corridor"


def normalized_size(value: Any) -> float:
    """Missing and zero size are zero.  They are never promoted to one."""
    if value in (None, ""):
        return 0.0
    try:
        size = float(value)
    except (TypeError, ValueError) as exc:
        raise BenchmarkError(f"invalid print size: {value!r}") from exc
    if not math.isfinite(size) or size < 0:
        raise BenchmarkError(f"invalid print size: {value!r}")
    return size


def canonical_true_prints(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Source-filter and receipt-deduplicate true prints.

    A shared exchange trade/receipt id is required.  Timestamp/price buckets
    are not identities and therefore cannot deduplicate overlapping feeds.
    """
    accepted: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []
    for row in rows:
        source = str(row.get("source") or "")
        if source not in TRUE_PRINT_SOURCES or row.get("true_print") is not True:
            errors.append({
                "mismatch_type": "source",
                "receipt_id": row.get("receipt_id") or row.get("trade_id"),
                "detail": "row is not an allowlisted true print",
                "source": source,
            })
            continue
        identity = str(row.get("receipt_id") or row.get("trade_id") or "")
        if not identity:
            errors.append({
                "mismatch_type": "source",
                "detail": "true print lacks receipt/trade identity",
                "ticker": row.get("ticker"),
            })
            continue
        if row.get("exchange_ts") in (None, ""):
            errors.append({
                "mismatch_type": "clock",
                "receipt_id": identity,
                "detail": "local receipt time cannot replace exchange time",
            })
            continue
        try:
            timestamp = parse_exchange_ts(row.get("exchange_ts"), "print.exchange_ts")
            price = int(row.get("price_cents"))
            size = normalized_size(row.get("size"))
        except (BenchmarkError, TypeError, ValueError) as exc:
            errors.append({
                "mismatch_type": "source",
                "receipt_id": identity,
                "detail": str(exc),
            })
            continue
        if not 1 <= price <= 99:
            errors.append({
                "mismatch_type": "price",
                "receipt_id": identity,
                "detail": f"out-of-range price {price}",
            })
            continue
        canonical = {
            "receipt_id": identity,
            "ticker": str(row.get("ticker") or ""),
            "exchange_ts": timestamp,
            "price_cents": price,
            "size": size,
            "source": source,
        }
        prior = accepted.get(identity)
        if prior is None:
            accepted[identity] = canonical
        elif any(prior[key] != canonical[key]
                 for key in ("ticker", "exchange_ts", "price_cents", "size")):
            errors.append({
                "mismatch_type": "source",
                "receipt_id": identity,
                "detail": "conflicting duplicate receipt across feeds",
            })
    result = sorted(accepted.values(),
                    key=lambda row: (row["exchange_ts"], row["receipt_id"]))
    return result, errors


def ladder_at_price(row: Mapping[str, Any], side: str, price: int) -> float:
    value = row.get(side)
    if not isinstance(value, list):
        raise BenchmarkError(f"book {side} is not a ladder")
    for level in value:
        if not isinstance(level, list) or len(level) != 2:
            raise BenchmarkError(f"malformed {side} level")
        if int(level[0]) == price:
            return normalized_size(level[1])
    return 0.0


def valid_full_book(row: Mapping[str, Any]) -> tuple[bool, str | None]:
    source = str(row.get("source") or "")
    depth = row.get("capture_depth")
    if source == "premarket_ticks" or depth in (5, "top5"):
        return False, "premarket_ticks is top-five only"
    if source == "depth_recorder" or depth in (20, "top20"):
        return False, "depth_recorder is snapshot/top-20 and change-deduplicated"
    if source != FULL_BOOK_SOURCE or depth != "full":
        return False, "not a full ws_depth ladder"
    if row.get("corrupt"):
        return False, "corrupt ws_depth interval"
    if row.get("gap_before") or row.get("reconnect"):
        return False, "ws_depth reconnect/sequence gap"
    if row.get("sequence_valid") is not True or not row.get("epoch_id"):
        return False, "ws_depth epoch is not causally reconstructable"
    if row.get("exchange_ts") in (None, ""):
        return False, "book lacks exchange timestamp"
    return True, None


@dataclass(frozen=True)
class ReplayResult:
    status: str
    predicted_fill_qty: float
    first_fill_earliest: float | None
    first_fill_latest: float | None
    completion_earliest: float | None
    completion_latest: float | None
    mismatch_type: str | None = None
    detail: str | None = None


def replay_resting_buy(
    order: Mapping[str, Any],
    prints: Sequence[Mapping[str, Any]],
    books: Sequence[Mapping[str, Any]],
) -> ReplayResult:
    """Bound FIFO fillability using full-book queue and verified prints.

    Level decreases after placement have unknown ownership.  The optimistic
    bound assigns all such cancellations ahead of us; the pessimistic bound
    assigns none.  A fill is exact only when even the pessimistic bound fills.
    A non-fill is exact only when even the optimistic bound does not fill.
    Everything between those bounds is an explicit queue mismatch.
    """
    try:
        order_id = str(order["order_id"])
        ticker = str(order["ticker"])
        price = int(order["price_cents"])
        quantity = normalized_size(order["quantity"])
        placed = parse_exchange_ts(order.get("exchange_created_ts"),
                                   "order.exchange_created_ts")
    except (KeyError, BenchmarkError, TypeError, ValueError) as exc:
        return ReplayResult("unknown", 0, None, None, None, None,
                            "order_identity", str(exc))
    if not order_id or not order.get("client_order_id"):
        return ReplayResult("unknown", 0, None, None, None, None,
                            "order_identity",
                            "exact engine order/client fingerprints required")
    if quantity <= 0:
        return ReplayResult("unknown", 0, None, None, None, None,
                            "quantity", "non-positive order quantity")
    if not 1 <= price <= 99:
        return ReplayResult("unknown", 0, None, None, None, None,
                            "price", "order price outside 1..99")
    end_value = (order.get("exchange_cancelled_ts")
                 or order.get("exchange_expired_ts")
                 or order.get("evaluation_end_exchange_ts"))
    try:
        end = parse_exchange_ts(end_value, "order.evaluation_end_exchange_ts")
    except BenchmarkError as exc:
        return ReplayResult("unknown", 0, None, None, None, None,
                            "clock", str(exc))
    relevant_books: list[tuple[float, Mapping[str, Any]]] = []
    invalid_reason: str | None = None
    for row in books:
        if str(row.get("ticker") or "") != ticker:
            continue
        timestamp = None
        if row.get("exchange_ts") not in (None, ""):
            try:
                timestamp = parse_exchange_ts(row.get("exchange_ts"),
                                              "book.exchange_ts")
            except BenchmarkError as exc:
                invalid_reason = str(exc)
        ok, reason = valid_full_book(row)
        if not ok:
            invalid_reason = reason
            if (str(row.get("source") or "") == FULL_BOOK_SOURCE
                    and timestamp is not None and placed <= timestamp <= end):
                return ReplayResult("unknown", 0, None, None, None, None,
                                    "book", reason)
            continue
        if timestamp is None:
            continue
        if timestamp <= end:
            relevant_books.append((timestamp, row))
    before = [(timestamp, row) for timestamp, row in relevant_books
              if timestamp <= placed]
    if not before:
        return ReplayResult("unknown", 0, None, None, None, None, "book",
                            invalid_reason or "no valid full book at placement")
    before.sort(key=lambda item: item[0])
    placement_ts, placement_book = before[-1]
    if placement_book.get("epoch_id") is None:
        return ReplayResult("unknown", 0, None, None, None, None, "book",
                            "placement book lacks epoch")
    epoch = placement_book["epoch_id"]
    if any(row.get("epoch_id") != epoch
           for timestamp, row in relevant_books
           if placed < timestamp <= end):
        return ReplayResult("unknown", 0, None, None, None, None, "book",
                            "ws_depth epoch changed inside order lifetime")
    after = sorted(
        (timestamp, row) for timestamp, row in relevant_books
        if placed < timestamp <= end and row.get("epoch_id") == epoch
    )
    if any(row.get("gap_before") or row.get("reconnect") for _, row in after):
        return ReplayResult("unknown", 0, None, None, None, None, "book",
                            "gap/reconnect inside order lifetime")
    try:
        sequences = [int(placement_book["sequence"])] + [
            int(row["sequence"]) for _, row in after]
    except (KeyError, TypeError, ValueError):
        return ReplayResult("unknown", 0, None, None, None, None, "book",
                            "ws_depth sequence is missing or invalid")
    if any(later <= earlier for earlier, later in zip(sequences, sequences[1:])):
        return ReplayResult("unknown", 0, None, None, None, None, "book",
                            "ws_depth sequence is not strictly increasing")
    try:
        initial_ahead = ladder_at_price(placement_book, "bids", price)
    except BenchmarkError as exc:
        return ReplayResult("unknown", 0, None, None, None, None, "book",
                            str(exc))
    # The snapshot was captured no later than exchange order creation, so its
    # entire displayed level is ahead of this newly acknowledged order.
    queue_min = initial_ahead
    queue_max = initial_ahead
    own_min = quantity
    own_max = quantity
    first_earliest = first_latest = None
    complete_earliest = complete_latest = None
    prior_level = initial_ahead
    timeline: list[tuple[float, int, str, Mapping[str, Any]]] = []
    for timestamp, row in after:
        timeline.append((timestamp, 1, "book", row))
    for row in prints:
        if str(row.get("ticker") or "") != ticker:
            continue
        timestamp = float(row["exchange_ts"])
        if placed <= timestamp <= end and int(row["price_cents"]) <= price:
            timeline.append((timestamp, 0, "print", row))
    timeline.sort(key=lambda item: (item[0], item[1]))
    for timestamp, _, kind, row in timeline:
        if kind == "book":
            try:
                level = ladder_at_price(row, "bids", price)
            except BenchmarkError as exc:
                return ReplayResult("unknown", 0, None, None, None, None,
                                    "book", str(exc))
            if level < prior_level:
                # Optimistic only: every unattributed cancellation was ahead.
                queue_min = max(0.0, queue_min - (prior_level - level))
            prior_level = level
            continue
        volume = normalized_size(row.get("size"))
        if volume <= 0:
            continue
        before_min = own_min
        before_max = own_max
        take_min = min(queue_min, volume)
        queue_min -= take_min
        rem_min = volume - take_min
        own_min = max(0.0, own_min - rem_min)
        take_max = min(queue_max, volume)
        queue_max -= take_max
        rem_max = volume - take_max
        own_max = max(0.0, own_max - rem_max)
        if first_earliest is None and own_min < quantity:
            first_earliest = timestamp
        if first_latest is None and own_max < quantity:
            first_latest = timestamp
        if complete_earliest is None and before_min > 0 and own_min <= 0:
            complete_earliest = timestamp
        if complete_latest is None and before_max > 0 and own_max <= 0:
            complete_latest = timestamp
    if complete_latest is not None:
        return ReplayResult("filled", quantity, first_earliest, first_latest,
                            complete_earliest, complete_latest)
    if complete_earliest is None:
        return ReplayResult("not_filled", quantity - own_min,
                            first_earliest, first_latest, None, None)
    return ReplayResult("unknown", quantity - own_min, first_earliest,
                        first_latest, complete_earliest, None, "queue",
                        "cancellation ownership leaves fill outcome ambiguous")


def build_event_ledger(
    events: Sequence[Mapping[str, Any]],
    forward_holdout_dates: Sequence[str] = (),
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ledger: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for event in events:
        event_id = str(event.get("event_id") or "")
        if not event_id or event_id in seen:
            errors.append({
                "event_id": event_id or None,
                "mismatch_type": "event_identity",
                "detail": "missing or duplicate event_id",
            })
            continue
        seen.add(event_id)
        category = str(event.get("category") or "")
        if category not in BIG4:
            continue
        try:
            day = event_day(event)
        except BenchmarkError as exc:
            errors.append({"event_id": event_id,
                           "mismatch_type": "schedule", "detail": str(exc)})
            continue
        period = period_for_day(day, forward_holdout_dates)
        if period == "outside_operational_period":
            continue
        exclusion = event.get("floor_exclusion")
        floor_pass = True
        floor_reason = "all_big4_games_pass_by_default"
        floor_evidence = event.get("floor_evidence_receipt_id")
        if exclusion:
            if exclusion != ALLOWED_FLOOR_EXCLUSION or not floor_evidence:
                errors.append({
                    "event_id": event_id,
                    "mismatch_type": "floor_law",
                    "detail": "unapproved or unsupported floor exclusion",
                })
            else:
                floor_pass = False
                floor_reason = ALLOWED_FLOOR_EXCLUSION
        legs = event.get("legs")
        leg_tickers: list[str] = []
        if isinstance(legs, list):
            for leg in legs:
                if isinstance(leg, dict) and leg.get("ticker"):
                    leg_tickers.append(str(leg["ticker"]))
                elif isinstance(leg, str):
                    leg_tickers.append(leg)
        data_state = "ready" if len(set(leg_tickers)) == 2 else "unknown_missing_leg_map"
        ledger.append({
            "schema_version": SCHEMA_VERSION,
            "event_id": event_id,
            "category": category,
            "event_date": day,
            "period": period,
            "floor_pass": floor_pass,
            "floor_reason": floor_reason,
            "floor_evidence_receipt_id": floor_evidence,
            "required_lot_per_leg": REQUIRED_LOT,
            "leg_tickers": sorted(set(leg_tickers)),
            "data_state": data_state,
        })
    ledger.sort(key=lambda row: (row["event_date"], row["event_id"]))
    return ledger, errors


def actual_order_result(
    order: Mapping[str, Any], fills: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    order_id = str(order.get("order_id") or "")
    order_fills = [row for row in fills
                   if str(row.get("order_id") or "") == order_id]
    normalized: list[tuple[float, float, int]] = []
    for fill in order_fills:
        timestamp = parse_exchange_ts(fill.get("exchange_ts"),
                                      "fill.exchange_ts")
        quantity = normalized_size(fill.get("quantity"))
        price = int(fill.get("price_cents"))
        normalized.append((timestamp, quantity, price))
    normalized.sort()
    quantity = sum(row[1] for row in normalized)
    vwap = (sum(row[1] * row[2] for row in normalized) / quantity
            if quantity else None)
    required = normalized_size(order.get("quantity"))
    cumulative = 0.0
    completion = None
    first = normalized[0][0] if normalized else None
    for timestamp, size, _ in normalized:
        cumulative += size
        if completion is None and cumulative >= required:
            completion = timestamp
    return {
        "status": "filled" if completion is not None else "not_filled",
        "filled_quantity": quantity,
        "first_fill_exchange_ts": first,
        "completion_exchange_ts": completion,
        "fill_vwap_cents": vwap,
    }


def validate_replay(
    ledger: Sequence[Mapping[str, Any]],
    orders: Sequence[Mapping[str, Any]],
    fills: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    books: Sequence[Mapping[str, Any]],
    inherited_errors: Sequence[Mapping[str, Any]] = (),
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    mismatches: list[dict[str, Any]] = [dict(row) for row in inherited_errors]
    passing_events = {str(row["event_id"]) for row in ledger if row["floor_pass"]}
    entry_attempts = [row for row in orders
                      if str(row.get("event_id") or "") in passing_events
                      and row.get("purpose") == "entry"
                      and row.get("action") == "buy"]
    failed_attempts = [row for row in entry_attempts
                       if row.get("accepted") is False]
    entry_orders = [row for row in entry_attempts
                    if row.get("accepted") is not False]
    orders_by_event: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for order in entry_attempts:
        orders_by_event[str(order.get("event_id"))].append(order)
    for event_id in sorted(passing_events):
        event_orders = orders_by_event.get(event_id, [])
        if not event_orders:
            mismatches.append({
                "event_id": event_id,
                "mismatch_type": "policy",
                "detail": "floor-passing event has no exact live entry order receipts",
            })
            continue
        tickers = {str(order.get("ticker") or "") for order in event_orders}
        if len(tickers) < 2:
            mismatches.append({
                "event_id": event_id,
                "mismatch_type": "policy",
                "detail": "live receipt set does not cover both event legs",
            })
    compared = 0
    matched_failed_attempts = 0
    matched_fills = 0
    matched_nonfills = 0
    for attempt in failed_attempts:
        attempt_identity = (attempt.get("attempt_id")
                            or attempt.get("attempt_receipt_id")
                            or attempt.get("order_id"))
        base = {
            "event_id": str(attempt.get("event_id") or ""),
            "ticker": attempt.get("ticker"),
            "leg": attempt.get("leg"),
            "attempt_receipt_id": attempt_identity,
            "posted_price_cents": attempt.get("price_cents"),
            "ordered_quantity": attempt.get("quantity"),
        }
        if not attempt_identity:
            mismatches.append({
                **base,
                "mismatch_type": "order_identity",
                "detail": "failed entry attempt lacks a stable attempt receipt",
            })
            continue
        try:
            parse_exchange_ts(attempt.get("exchange_rejected_ts"),
                              "order.exchange_rejected_ts")
        except BenchmarkError as exc:
            mismatches.append({
                **base,
                "mismatch_type": "clock",
                "detail": str(exc),
            })
            continue
        if not attempt.get("exchange_rejection_code"):
            mismatches.append({
                **base,
                "mismatch_type": "source",
                "detail": "failed entry attempt lacks exchange rejection code",
            })
            continue
        matched_failed_attempts += 1
    for order in entry_orders:
        compared += 1
        event_id = str(order.get("event_id") or "")
        order_id = str(order.get("order_id") or "")
        base = {
            "event_id": event_id,
            "ticker": order.get("ticker"),
            "leg": order.get("leg"),
            "order_id": order_id or None,
            "posted_price_cents": order.get("price_cents"),
            "ordered_quantity": order.get("quantity"),
        }
        try:
            actual = actual_order_result(order, fills)
        except (BenchmarkError, TypeError, ValueError) as exc:
            mismatches.append({**base, "mismatch_type": "fill_receipt",
                               "detail": str(exc)})
            continue
        replay = replay_resting_buy(order, prints, books)
        if replay.status == "unknown":
            mismatches.append({
                **base,
                "mismatch_type": replay.mismatch_type or "unknown",
                "detail": replay.detail,
                "actual_status": actual["status"],
            })
            continue
        if replay.status != actual["status"]:
            mismatches.append({
                **base,
                "mismatch_type": "fill" if actual["status"] == "filled" else "nonfill",
                "detail": "replay and official receipt outcome disagree",
                "actual_status": actual["status"],
                "replay_status": replay.status,
            })
            continue
        if actual["status"] == "filled":
            required = normalized_size(order.get("quantity"))
            if actual["filled_quantity"] < required:
                mismatches.append({**base, "mismatch_type": "quantity",
                                   "detail": "official fills do not reach required lot"})
                continue
            if actual["fill_vwap_cents"] != float(order.get("price_cents")):
                mismatches.append({
                    **base,
                    "mismatch_type": "price",
                    "detail": "official VWAP differs from resting limit",
                    "actual_fill_vwap_cents": actual["fill_vwap_cents"],
                })
                continue
            actual_completion = actual["completion_exchange_ts"]
            if (replay.completion_earliest is None
                    or replay.completion_latest is None
                    or replay.completion_earliest != replay.completion_latest
                    or actual_completion != replay.completion_earliest):
                mismatches.append({
                    **base,
                    "mismatch_type": "clock" if replay.completion_earliest == replay.completion_latest else "queue",
                    "detail": "exact exchange completion time was not reproduced",
                    "actual_completion_exchange_ts": iso_utc(actual_completion),
                    "replay_earliest_exchange_ts": iso_utc(replay.completion_earliest),
                    "replay_latest_exchange_ts": iso_utc(replay.completion_latest),
                })
                continue
            matched_fills += 1
        else:
            matched_nonfills += 1
    gate_pass = bool(entry_attempts) and not mismatches
    summary = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "gate_pass": gate_pass,
        "pass_rule": "100_percent_exact_fills_and_nonfills",
        "floor_passing_events": len(passing_events),
        "entry_attempts_compared": len(entry_attempts),
        "orders_compared": compared,
        "failed_attempts_compared": len(failed_attempts),
        "matched_failed_attempts": matched_failed_attempts,
        "matched_fills": matched_fills,
        "matched_nonfills": matched_nonfills,
        "mismatch_count": len(mismatches),
        "mismatch_types": dict(sorted(Counter(
            str(row.get("mismatch_type") or "unknown")
            for row in mismatches).items())),
        "strategy_scoring_permitted": gate_pass,
    }
    return summary, mismatches


def percentile(values: Sequence[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(fraction * (len(ordered) - 1))))
    return ordered[index]


def score_outcomes(
    ledger: Sequence[Mapping[str, Any]],
    outcomes: Sequence[Mapping[str, Any]],
    *,
    period: str,
    candidate_id: str,
) -> dict[str, Any]:
    denominator = [row for row in ledger
                   if row.get("floor_pass") and row.get("period") == period]
    expected_ids = {str(row["event_id"]) for row in denominator}
    selected = {str(row.get("event_id")): row for row in outcomes
                if row.get("candidate_id") == candidate_id
                and row.get("period") == period}
    completed: list[dict[str, Any]] = []
    unknown: list[str] = []
    leg_deltas: dict[str, list[float]] = defaultdict(list)
    by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_day: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in denominator:
        event_id = str(event["event_id"])
        outcome = selected.get(event_id)
        if outcome is None or outcome.get("status") in {
            "missing", "error", "unknown", "thin", "corrupt"
        }:
            unknown.append(event_id)
            continue
        legs = outcome.get("legs")
        if not isinstance(legs, list) or len(legs) != 2:
            unknown.append(event_id)
            continue
        complete = True
        costs: list[float] = []
        refs: list[float] = []
        for index, leg in enumerate(legs):
            if not isinstance(leg, dict):
                complete = False
                break
            required = normalized_size(leg.get("required_quantity", REQUIRED_LOT))
            filled = normalized_size(leg.get("filled_quantity"))
            if filled < required or leg.get("fill_vwap_cents") is None:
                complete = False
                break
            cost = float(leg["fill_vwap_cents"])
            costs.append(cost)
            reference = leg.get("w1_close_reference_cents")
            if reference is not None:
                delta = cost - float(reference)
                refs.append(delta)
                leg_name = str(leg.get("leg") or f"leg_{index + 1}")
                leg_deltas[leg_name].append(delta)
        if not complete:
            continue
        cost = sum(costs)
        row = {
            "event_id": event_id,
            "category": event["category"],
            "event_date": event["event_date"],
            "combined_entry_cost_cents": cost,
            "combined_vs_par_delta_cents": cost - PAR_CENTS,
            "pair_reference_delta_cents": sum(refs) if len(refs) == 2 else None,
        }
        completed.append(row)
        by_class[str(event["category"])].append(row)
        by_day[str(event["event_date"])].append(row)
    d_count = len(denominator)
    c_count = len(completed)
    under_par = [row for row in completed
                 if row["combined_entry_cost_cents"] < PAR_CENTS]
    s_count = len(under_par)
    combined_delta = [row["combined_vs_par_delta_cents"] for row in completed]
    pair_reference = [row["pair_reference_delta_cents"] for row in completed
                      if row["pair_reference_delta_cents"] is not None]

    def ratio(numerator: int, denominator_count: int) -> float | None:
        return numerator / denominator_count if denominator_count else None

    def group_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        under = sum(row["combined_entry_cost_cents"] < PAR_CENTS for row in rows)
        cents = [row["combined_vs_par_delta_cents"] for row in rows]
        return {
            "completed": len(rows),
            "under_par": under,
            "under_par_share": ratio(under, len(rows)),
            "mean_combined_vs_par_delta_cents": statistics.fmean(cents) if cents else None,
            "median_combined_vs_par_delta_cents": statistics.median(cents) if cents else None,
        }

    leg_summary = {}
    for leg, values in sorted(leg_deltas.items()):
        leg_summary[leg] = {
            "n": len(values),
            "negative_n": sum(value < 0 for value in values),
            "negative_share": ratio(sum(value < 0 for value in values), len(values)),
            "mean_fill_minus_w1_close_cents": statistics.fmean(values) if values else None,
            "median_fill_minus_w1_close_cents": statistics.median(values) if values else None,
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "period": period,
        "D": d_count,
        "C": c_count,
        "S": s_count,
        "C_over_D": ratio(c_count, d_count),
        "S_over_C": ratio(s_count, c_count),
        "S_over_D": ratio(s_count, d_count),
        "mean_combined_vs_par_delta_cents": statistics.fmean(combined_delta) if combined_delta else None,
        "median_combined_vs_par_delta_cents": statistics.median(combined_delta) if combined_delta else None,
        "negative_combined_vs_par_n": sum(value < 0 for value in combined_delta),
        "negative_combined_vs_par_share": ratio(sum(value < 0 for value in combined_delta), c_count),
        "combined_vs_par_delta_distribution": {
            "p10": percentile(combined_delta, 0.10),
            "p25": percentile(combined_delta, 0.25),
            "p50": percentile(combined_delta, 0.50),
            "p75": percentile(combined_delta, 0.75),
            "p90": percentile(combined_delta, 0.90),
        },
        "pair_reference_delta": {
            "definition": "sum(fill_vwap_minus_frozen_w1_close_reference) across the two legs",
            "n": len(pair_reference),
            "mean_cents": statistics.fmean(pair_reference) if pair_reference else None,
            "median_cents": statistics.median(pair_reference) if pair_reference else None,
            "negative_n": sum(value < 0 for value in pair_reference),
            "negative_share": ratio(sum(value < 0 for value in pair_reference), len(pair_reference)),
        },
        "individual_leg_reference_delta": leg_summary,
        "legacy_le_97_tier_n": sum(
            row["combined_entry_cost_cents"] <= LEGACY_SUCCESS_CENTS
            for row in completed),
        "unknown_missing_error_thin_corrupt_n": len(unknown),
        "unknown_event_ids": sorted(unknown),
        "unexpected_outcome_event_ids": sorted(set(selected) - expected_ids),
        "by_class": {key: group_metrics(rows)
                     for key, rows in sorted(by_class.items())},
        "by_day": {key: group_metrics(rows)
                   for key, rows in sorted(by_day.items())},
        "exits_or_window2_fields_consumed": False,
    }


def selection_key(result: Mapping[str, Any]) -> tuple[float, float, float]:
    completion = float(result.get("C_over_D") or 0.0)
    capture = float(result.get("S_over_D") or 0.0)
    mean_delta = result.get("mean_combined_vs_par_delta_cents")
    efficiency = -float(mean_delta) if mean_delta is not None else -10_000.0
    return completion, capture, efficiency


def require_gate(output_dir: Path) -> dict[str, Any]:
    path = output_dir / "validation_summary.json"
    if not path.is_file():
        raise BenchmarkError("validation_summary.json is missing")
    summary = json.loads(path.read_text(encoding="utf-8"))
    if summary.get("gate_pass") is not True:
        raise BenchmarkError("validation gate failed; strategy scoring is forbidden")
    return summary


def command_manifest(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    required = ["events.jsonl", "orders.jsonl", "fills.jsonl",
                "prints.jsonl", "books.jsonl"]
    files = []
    missing = []
    for name in required:
        path = input_dir / name
        if not path.is_file():
            missing.append(name)
            files.append({"name": name, "present": False})
            continue
        rows, errors = read_jsonl(path)
        files.append({
            "name": name,
            "present": True,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "parseable_rows": len(rows),
            "parse_errors": len(errors),
        })
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "input_dir": str(input_dir),
        "required_files": files,
        "missing_files": missing,
        "complete": not missing and all(row.get("parse_errors") == 0
                                        for row in files),
    }
    write_json(output_dir / "input_manifest.json", manifest)
    print(json.dumps(manifest, indent=2))
    return 0 if manifest["complete"] else 2


def command_ledger(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    events, parse_errors = read_jsonl(input_dir / "events.jsonl")
    holdout_dates: Sequence[str] = ()
    declaration_path = getattr(args, "holdout_declaration", None)
    if declaration_path:
        declaration = json.loads(
            Path(declaration_path).read_text(encoding="utf-8"))
        holdout_dates = declaration.get("holdout_dates") or ()
        if (not isinstance(holdout_dates, list)
                or len(holdout_dates) != FORWARD_HOLDOUT_DAYS):
            raise BenchmarkError("ledger holdout declaration must name three dates")
    ledger, ledger_errors = build_event_ledger(events, holdout_dates)
    path = output_dir / "candidate_event_ledger.jsonl"
    write_jsonl(path, ledger)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "immutable": True,
        "sha256": sha256_file(path),
        "rows": len(ledger),
        "development_period": [DEVELOPMENT_START, DEVELOPMENT_END],
        "forward_holdout_dates": list(holdout_dates),
        "D_fit": sum(row["floor_pass"] and row["period"] == "fit" for row in ledger),
        "D_holdout": sum(row["floor_pass"] and row["period"] == "holdout" for row in ledger),
        "excluded": sum(not row["floor_pass"] for row in ledger),
        "errors": parse_errors + ledger_errors,
        "floor_law": {
            "default": "every big-4 game passes",
            "only_exclusion": ALLOWED_FLOOR_EXCLUSION,
            "missing_data_is_exclusion": False,
        },
    }
    write_json(output_dir / "candidate_event_ledger.summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if not summary["errors"] else 2


def load_ledger(output_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    path = output_dir / "candidate_event_ledger.jsonl"
    rows, errors = read_jsonl(path)
    summary_path = output_dir / "candidate_event_ledger.summary.json"
    if not summary_path.is_file():
        errors.append({"mismatch_type": "ledger",
                       "detail": "ledger summary/hash is missing"})
        return rows, errors
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("sha256") != sha256_file(path):
        errors.append({"mismatch_type": "ledger",
                       "detail": "immutable ledger hash changed"})
    return rows, errors


def command_validate(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    ledger, ledger_errors = load_ledger(output_dir)
    orders, order_errors = read_jsonl(input_dir / "orders.jsonl")
    fills, fill_errors = read_jsonl(input_dir / "fills.jsonl")
    raw_prints, print_parse_errors = read_jsonl(input_dir / "prints.jsonl")
    books, book_errors = read_jsonl(input_dir / "books.jsonl")
    prints, print_errors = canonical_true_prints(raw_prints)
    inherited = (ledger_errors + order_errors + fill_errors
                 + print_parse_errors + book_errors + print_errors)
    summary, mismatches = validate_replay(
        ledger, orders, fills, prints, books, inherited)
    write_json(output_dir / "validation_summary.json", summary)
    write_jsonl(output_dir / "validation_mismatch_ledger.jsonl", mismatches)
    print(json.dumps(summary, indent=2))
    return 0 if summary["gate_pass"] else 3


def command_fit(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).resolve()
    require_gate(output_dir)
    ledger, ledger_errors = load_ledger(output_dir)
    if ledger_errors:
        raise BenchmarkError("immutable ledger failed hash/parse validation")
    outcomes_path = Path(args.fit_outcomes).resolve()
    outcomes, errors = read_jsonl(outcomes_path)
    if errors:
        raise BenchmarkError(f"fit outcome parse errors: {len(errors)}")
    forbidden = sorted({path for row in outcomes
                        for path in forbidden_outcome_paths(row)})
    if forbidden:
        raise BenchmarkError(
            "fit input contains Window-2/exit/settlement fields: "
            + ", ".join(forbidden[:10]))
    if any(row.get("period") != "fit" for row in outcomes):
        raise BenchmarkError("fit input contains a non-fit row")
    primary_outcomes = [row for row in outcomes
                        if not row.get("feature_removed")]
    boundary_candidate_ids = sorted({
        str(row.get("candidate_id")) for row in primary_outcomes
        if row.get("experiment_kind") == "boundary"
    })
    if len(boundary_candidate_ids) != 16:
        raise BenchmarkError(
            "fit input must contain all 16 boundary baseline candidates")
    boundary_results = [score_outcomes(
        ledger, primary_outcomes, period="fit", candidate_id=candidate_id)
        for candidate_id in boundary_candidate_ids]
    # Candidate ids are sorted, so max preserves the lowest id on an exact
    # metric tie and makes the final tie-break deterministic.
    selected_boundary = max(boundary_results, key=selection_key)
    selected_boundary_id = next(
        str(row.get("boundary_id")) for row in primary_outcomes
        if row.get("candidate_id") == selected_boundary["candidate_id"])
    write_json(output_dir / "boundary_sensitivity_fit.json", {
        "fit_only": True,
        "candidate_grid_required": {
            "left_edge_hours_before_schedule": [8, 6, 4, 2],
            "schedule_only_corridor_minutes": [15, 30, 45, 60],
        },
        "results": boundary_results,
        "complete": True,
        "selected_boundary_candidate_id": selected_boundary["candidate_id"],
        "selected_boundary_id": selected_boundary_id,
    })
    policy_candidate_ids = sorted({
        str(row.get("candidate_id")) for row in primary_outcomes
        if row.get("experiment_kind") == "policy"
        and row.get("boundary_id") == selected_boundary_id
    })
    if not policy_candidate_ids:
        raise BenchmarkError(
            "fit input has no policy candidates for the selected boundary")
    policy_results = [score_outcomes(
        ledger, primary_outcomes, period="fit", candidate_id=candidate_id)
        for candidate_id in policy_candidate_ids]
    selected = max(policy_results, key=selection_key)
    write_json(output_dir / "candidate_results_fit.json", {
        "selected_boundary_id": selected_boundary_id,
        "selection_law": ["maximize C/D", "then maximize S/D",
                          "then minimize mean combined-vs-par delta",
                          "then candidate_id for deterministic tie-break"],
        "results": policy_results,
        "selected_candidate_id": selected["candidate_id"],
    })
    ablations = [row for row in outcomes if row.get("feature_removed")
                 and row.get("boundary_id") == selected_boundary_id]
    ablation_ids = sorted({str(row["candidate_id"]) for row in ablations})
    write_json(output_dir / "ablation_results_fit.json", {
        "results": [score_outcomes(ledger, ablations, period="fit",
                                   candidate_id=candidate_id)
                    for candidate_id in ablation_ids],
    })
    freeze_created = dt.datetime.now(dt.timezone.utc)
    forward_dates = next_complete_utc_dates(freeze_created)
    freeze = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "status": "frozen_after_fit_only",
        "selected_candidate_id": selected["candidate_id"],
        "selected_window_definition": next(
            (row.get("window_definition") for row in primary_outcomes
             if row.get("candidate_id") == selected["candidate_id"]), None),
        "selected_policy_definition": next(
            (row.get("policy_definition") for row in primary_outcomes
             if row.get("candidate_id") == selected["candidate_id"]), None),
        "fit_outcomes_sha256": sha256_file(outcomes_path),
        "event_ledger_sha256": sha256_file(
            output_dir / "candidate_event_ledger.jsonl"),
        "freeze_created_utc": freeze_created.isoformat(),
        "fit_period": [DEVELOPMENT_START, DEVELOPMENT_END],
        "fit_role": "development_backwalk_inspected_history",
        "development_event_ledger_sha256": ledger_subset_sha256(
            ledger, "fit"),
        "forward_holdout": {
            "dates": forward_dates,
            "selection_rule": (
                "first three complete UTC dates strictly after the UTC date "
                "containing the fit freeze"),
            "evaluation_count_allowed": 1,
            "freeze_and_dates_must_be_committed_before_evaluation": True,
        },
        "required_lot_per_leg": REQUIRED_LOT,
        "par_cents": PAR_CENTS,
        "legacy_le_97_reported_separately": True,
        "holdout_viewed": False,
    }
    write_json(output_dir / "window1_freeze.json", freeze)
    print(json.dumps(freeze, indent=2))
    return 0


def command_ablate(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).resolve()
    require_gate(output_dir)
    ledger, ledger_errors = load_ledger(output_dir)
    if ledger_errors:
        raise BenchmarkError("immutable ledger failed hash/parse validation")
    freeze_path = output_dir / "window1_freeze.json"
    if not freeze_path.is_file():
        raise BenchmarkError("fit-only Window-1 freeze is missing")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze.get("holdout_viewed") is True:
        raise BenchmarkError("ablation cannot run after holdout was viewed")
    if freeze.get("event_ledger_sha256") != sha256_file(
            output_dir / "candidate_event_ledger.jsonl"):
        raise BenchmarkError("denominator changed after fit freeze")
    outcomes_path = Path(args.fit_outcomes).resolve()
    outcomes, errors = read_jsonl(outcomes_path)
    if errors:
        raise BenchmarkError(f"ablation parse errors: {len(errors)}")
    forbidden = sorted({path for row in outcomes
                        for path in forbidden_outcome_paths(row)})
    if forbidden:
        raise BenchmarkError(
            "ablation input contains Window-2/exit/settlement fields: "
            + ", ".join(forbidden[:10]))
    if any(row.get("period") != "fit" for row in outcomes):
        raise BenchmarkError("ablation input contains a non-fit row")
    if any(not row.get("feature_removed") for row in outcomes):
        raise BenchmarkError("every ablation row must name feature_removed")
    selected_window = freeze.get("selected_window_definition") or {}
    if any(row.get("boundary_id") != selected_window.get("boundary_id")
           for row in outcomes):
        raise BenchmarkError("ablation changed the frozen boundary")
    candidate_ids = sorted({str(row.get("candidate_id") or "")
                            for row in outcomes if row.get("candidate_id")})
    results = [score_outcomes(ledger, outcomes, period="fit",
                              candidate_id=candidate_id)
               for candidate_id in candidate_ids]
    candidate_path = output_dir / "candidate_results_fit.json"
    if not candidate_path.is_file():
        raise BenchmarkError("fit candidate results are missing")
    candidate_doc = json.loads(candidate_path.read_text(encoding="utf-8"))
    baseline = next((row for row in candidate_doc.get("results", [])
                     if row.get("candidate_id")
                     == freeze.get("selected_candidate_id")), None)
    if baseline is None:
        raise BenchmarkError("selected fit baseline result is missing")
    for result in results:
        family = next(str(row.get("feature_removed")) for row in outcomes
                      if row.get("candidate_id") == result["candidate_id"])
        result["feature_removed"] = family
        result["delta_C_vs_selected_fit"] = result["C"] - baseline["C"]
        result["delta_S_vs_selected_fit"] = result["S"] - baseline["S"]
        result["delta_C_over_D_vs_selected_fit"] = (
            (result["C_over_D"] or 0) - (baseline["C_over_D"] or 0))
        result["delta_S_over_D_vs_selected_fit"] = (
            (result["S_over_D"] or 0) - (baseline["S_over_D"] or 0))
    write_json(output_dir / "ablation_results_fit.json", {
        "fit_only": True,
        "selected_candidate_id": freeze.get("selected_candidate_id"),
        "selected_boundary_id": selected_window.get("boundary_id"),
        "ablation_outcomes_sha256": sha256_file(outcomes_path),
        "results": results,
    })
    print(json.dumps({"ablations": len(results),
                      "selected_candidate_id": freeze.get(
                          "selected_candidate_id")}, indent=2))
    return 0


def command_holdout(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).resolve()
    require_gate(output_dir)
    result_path = output_dir / "untouched_holdout_result.json"
    if result_path.exists():
        raise BenchmarkError(
            "holdout result already exists; exactly one evaluation is allowed")
    freeze_path = output_dir / "window1_freeze.json"
    if not freeze_path.is_file():
        raise BenchmarkError("fit-only Window-1 freeze is missing")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if not args.holdout_declaration:
        raise BenchmarkError(
            "--holdout-declaration is required; freeze and dates must be committed")
    declaration = load_holdout_declaration(
        Path(args.holdout_declaration).resolve(), freeze, freeze_path)
    ledger, ledger_errors = load_ledger(output_dir)
    if ledger_errors:
        raise BenchmarkError("immutable ledger failed hash/parse validation")
    if freeze.get("development_event_ledger_sha256") != ledger_subset_sha256(
            ledger, "fit"):
        raise BenchmarkError("development denominator changed after fit freeze")
    holdout_dates = set(declaration["holdout_dates"])
    if any(row.get("period") == "holdout"
           and row.get("event_date") not in holdout_dates for row in ledger):
        raise BenchmarkError("holdout ledger contains an unregistered date")
    outcomes_path = Path(args.holdout_outcomes).resolve()
    outcomes, errors = read_jsonl(outcomes_path)
    if errors:
        raise BenchmarkError(f"holdout outcome parse errors: {len(errors)}")
    forbidden = sorted({path for row in outcomes
                        for path in forbidden_outcome_paths(row)})
    if forbidden:
        raise BenchmarkError(
            "holdout contains Window-2/exit/settlement fields: "
            + ", ".join(forbidden[:10]))
    if any(row.get("period") != "holdout" for row in outcomes):
        raise BenchmarkError("holdout input contains a non-holdout row")
    selected = str(freeze["selected_candidate_id"])
    if any(str(row.get("candidate_id") or "") != selected for row in outcomes):
        raise BenchmarkError("holdout contains a candidate not frozen on fit")
    result = score_outcomes(ledger, outcomes, period="holdout",
                            candidate_id=selected)
    result["target_C_over_D_at_least_0_75"] = (
        result["C_over_D"] is not None and result["C_over_D"] >= 0.75)
    result["combined_entry_cost_target"] = "strictly_below_100_cents"
    result["holdout_outcomes_sha256"] = sha256_file(outcomes_path)
    result["holdout_dates"] = declaration["holdout_dates"]
    result["freeze_and_dates_commit_sha"] = declaration["git_commit_sha"]
    result["stability_note"] = (
        "fixed three-UTC-date forward sample; do not extend after viewing")
    result["one_shot"] = True
    write_json(result_path, result)
    freeze["holdout_viewed"] = True
    freeze["holdout_outcomes_sha256"] = sha256_file(outcomes_path)
    write_json(freeze_path, freeze)
    print(json.dumps(result, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    for name, handler in (("manifest", command_manifest),
                          ("ledger", command_ledger),
                          ("validate", command_validate)):
        command = sub.add_parser(name)
        command.add_argument("--input-dir", required=True)
        command.add_argument("--output-dir", required=True)
        if name == "ledger":
            command.add_argument("--holdout-declaration")
        command.set_defaults(handler=handler)
    fit = sub.add_parser("fit")
    fit.add_argument("--fit-outcomes", required=True)
    fit.add_argument("--output-dir", required=True)
    fit.set_defaults(handler=command_fit)
    ablate = sub.add_parser("ablate")
    ablate.add_argument("--fit-outcomes", required=True)
    ablate.add_argument("--output-dir", required=True)
    ablate.set_defaults(handler=command_ablate)
    holdout = sub.add_parser("holdout")
    holdout.add_argument("--holdout-outcomes", required=True)
    holdout.add_argument("--output-dir", required=True)
    holdout.add_argument("--holdout-declaration", required=True)
    holdout.set_defaults(handler=command_holdout)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except BenchmarkError as exc:
        print(f"WINDOW1-BLOCKED: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
