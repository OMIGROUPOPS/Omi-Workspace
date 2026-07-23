#!/usr/bin/env python3
"""Game/leg-grain validation for the Window-1 benchmark.

This research-only validator collapses churned order ids by the engine's
conception/trade lineage while preserving every private identifier in a
private output.  It never queries Kalshi and never reads exit economics.

Actual fills come only from the complete paginated private fills export.
An unfilled lifecycle is exact only when every accepted order is closed by an
official zero-fill terminal receipt or an exact successful cancellation log,
there is no private fill, no engine entry-fill attribution, no unmatched
position-increase proxy, and no unmatched settlement.  All other cases are
explicitly censored.  Censoring does not remove a game from D.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


SCHEMA_VERSION = "window1-lifecycle-validation-v1"
REQUIRED_LOT = 5.0
TERMINAL_ZERO_FILL = {"canceled", "cancelled", "expired", "rejected"}
LOG_EVENTS = {"order_placed", "order_cancelled", "entry_filled", "settled"}


class LifecycleError(RuntimeError):
    """A fail-closed lifecycle validation error."""


def json_dump(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LifecycleError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        handle = path.open(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise LifecycleError(f"cannot read JSONL {path}: {exc}") from exc
    with handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise LifecycleError(
                    f"{path}:{line_number}: malformed JSON") from exc
            if not isinstance(row, dict):
                raise LifecycleError(
                    f"{path}:{line_number}: JSON object required")
            rows.append(row)
    return rows


def write_json(path: Path, value: Any, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.chmod(path, mode)


def write_jsonl(
    path: Path, rows: Iterable[Mapping[str, Any]], mode: int = 0o644,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json_dump(dict(row)) + "\n")
    os.chmod(path, mode)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def evidence_ref(value: Any) -> str:
    """One-way identifier reference suitable for sanitized mismatch rows."""
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:20]


def number(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise LifecycleError(f"invalid numeric value: {value!r}") from exc
    if not math.isfinite(result):
        raise LifecycleError(f"non-finite numeric value: {value!r}")
    return result


def parse_ts(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("Z", "+00:00")
    try:
        return float(text)
    except ValueError:
        pass
    try:
        stamp = dt.datetime.fromisoformat(text)
    except ValueError as exc:
        raise LifecycleError(f"invalid timestamp: {value!r}") from exc
    if stamp.tzinfo is None:
        raise LifecycleError(f"timezone-free timestamp: {value!r}")
    return stamp.timestamp()


def iso_utc(value: float | None) -> str | None:
    if value is None:
        return None
    return dt.datetime.fromtimestamp(
        value, dt.timezone.utc).isoformat().replace("+00:00", "Z")


def leg_tickers(event: Mapping[str, Any]) -> list[str]:
    out = []
    for leg in event.get("legs") or []:
        if isinstance(leg, dict) and leg.get("ticker"):
            out.append(str(leg["ticker"]))
    return out


def validation_edge(event: Mapping[str, Any]) -> float:
    actual = parse_ts(event.get("actual_start_exchange_ts"))
    if actual is not None and event.get("actual_start_verified") is True:
        return actual
    scheduled = parse_ts(event.get("scheduled_start_exchange_ts"))
    if scheduled is None:
        raise LifecycleError(
            f"event {event.get('event_id')} lacks a schedule")
    return scheduled + 60 * 60


def official_order_quantity(order: Mapping[str, Any]) -> float:
    """Prefer exchange initial quantity over a normalized local quantity."""
    value = order.get("exchange_initial_count")
    if value not in (None, ""):
        return number(value)
    return number(order.get("quantity"))


def fill_price_cents(fill: Mapping[str, Any]) -> float:
    value = fill.get("yes_price_dollars")
    if value in (None, ""):
        raise LifecycleError("private fill lacks yes_price_dollars")
    return round(number(value) * 100.0, 10)


def fill_timestamp(fill: Mapping[str, Any]) -> float:
    value = parse_ts(fill.get("created_time"))
    if value is None:
        raise LifecycleError("private fill lacks created_time")
    return value


def fill_identity(fill: Mapping[str, Any]) -> str:
    identity = str(fill.get("fill_id") or fill.get("trade_id") or "")
    if not identity:
        raise LifecycleError("private fill lacks fill_id/trade_id")
    return identity


def validate_export_receipt(
    manifest: Mapping[str, Any],
    fills_path: Path,
) -> dict[str, Any]:
    pagination = manifest.get("pagination_proof") or {}
    hashes = manifest.get("private_file_hashes") or {}
    expected = (hashes.get("api_fills") or {}).get("sha256")
    actual = sha256_file(fills_path)
    errors = []
    if manifest.get("complete") is not True:
        errors.append("export manifest is not complete")
    if pagination.get("complete") is not True:
        errors.append("private-fill pagination is incomplete")
    if int(pagination.get("request_errors") or 0) != 0:
        errors.append("private-fill export has request errors")
    if not expected or str(expected) != actual:
        errors.append("private-fill SHA-256 does not match export manifest")
    return {
        "complete": not errors,
        "errors": errors,
        "api_fills_sha256": actual,
        "export_started_utc": manifest.get("export_started_utc"),
        "export_completed_utc": manifest.get("export_completed_utc"),
        "causal_time_bounds": manifest.get("causal_time_bounds"),
        "pagination_proof": pagination,
    }


def canonical_private_fills(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: dict[str, dict[str, Any]] = {}
    mismatches: list[dict[str, Any]] = []
    for row in rows:
        try:
            identity = fill_identity(row)
            canonical = {
                "fill_id": identity,
                "order_id": str(row.get("order_id") or ""),
                "ticker": str(
                    row.get("ticker") or row.get("market_ticker") or ""),
                "action": str(row.get("action") or "").lower(),
                "quantity": number(row.get("count_fp")),
                "price_cents": fill_price_cents(row),
                "exchange_ts": fill_timestamp(row),
                "is_taker": bool(row.get("is_taker")),
            }
        except LifecycleError as exc:
            mismatches.append({
                "mismatch_type": "private_fill_contract",
                "detail": str(exc),
            })
            continue
        if (not canonical["order_id"] or not canonical["ticker"]
                or canonical["quantity"] <= 0):
            mismatches.append({
                "mismatch_type": "private_fill_contract",
                "fill_ref": evidence_ref(identity),
                "detail": "fill lacks order/ticker or positive quantity",
            })
            continue
        prior = accepted.get(identity)
        if prior is None:
            accepted[identity] = canonical
        elif prior != canonical:
            mismatches.append({
                "mismatch_type": "private_fill_duplicate_conflict",
                "fill_ref": evidence_ref(identity),
                "detail": "duplicate fill identity has conflicting fields",
            })
    result = sorted(
        accepted.values(),
        key=lambda row: (row["exchange_ts"], row["fill_id"]),
    )
    return result, mismatches


def iter_log_lines(
    log_dir: Path,
    active_log_name: str,
    active_prefix_bytes: int,
) -> Iterator[tuple[str, bytes]]:
    for path in sorted(log_dir.glob("live_v3_2026071[2-9]*.jsonl.gz")):
        with gzip.open(path, "rb") as handle:
            for line in handle:
                yield path.name, line
    active = log_dir / active_log_name
    if not active.is_file():
        raise LifecycleError(f"active byte-pinned log missing: {active}")
    with active.open("rb") as handle:
        while handle.tell() < active_prefix_bytes:
            line = handle.readline()
            if not line:
                break
            yield active.name, line


@dataclass
class LogEvidence:
    placements: dict[str, list[dict[str, Any]]]
    cancellations: dict[str, list[dict[str, Any]]]
    entry_fills: dict[str, list[dict[str, Any]]]
    settlements: dict[str, list[dict[str, Any]]]
    physical_rows: int
    selected_rows: int
    parse_errors: int


def scan_logs(
    log_dir: Path,
    active_log_name: str,
    active_prefix_bytes: int,
    order_ids: set[str],
    required_tickers: set[str],
) -> LogEvidence:
    placements: dict[str, list[dict[str, Any]]] = (
        collections.defaultdict(list))
    cancellations: dict[str, list[dict[str, Any]]] = (
        collections.defaultdict(list))
    entry_fills: dict[str, list[dict[str, Any]]] = (
        collections.defaultdict(list))
    settlements: dict[str, list[dict[str, Any]]] = (
        collections.defaultdict(list))
    physical = selected = parse_errors = 0
    needles = tuple(f'"{event}"'.encode() for event in LOG_EVENTS)
    for file_name, raw in iter_log_lines(
            log_dir, active_log_name, active_prefix_bytes):
        physical += 1
        if not any(needle in raw for needle in needles):
            continue
        try:
            row = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            parse_errors += 1
            continue
        event_type = str(row.get("event") or "")
        if event_type not in LOG_EVENTS:
            continue
        details = row.get("details") or {}
        timestamp = parse_ts(row.get("ts_epoch"))
        ticker = str(row.get("ticker") or "")
        if event_type == "order_placed":
            order_id = str(details.get("order_id") or "")
            if order_id not in order_ids:
                continue
            selected += 1
            placements[order_id].append({
                "order_id": order_id,
                "client_order_id": str(
                    details.get("client_order_id") or ""),
                "trade_id": str(details.get("trade_id") or ""),
                "ticker": ticker,
                "action": str(details.get("action") or "").lower(),
                "side": str(details.get("side") or "").lower(),
                "price_cents": number(details.get("price")),
                "quantity": number(details.get("count")),
                "response_status": str(
                    details.get("response_status") or ""),
                "local_logged_ts": timestamp,
                "source_file": file_name,
            })
            continue
        if event_type == "order_cancelled":
            order_id = str(details.get("order_id") or "")
            if order_id not in order_ids:
                continue
            selected += 1
            cancellations[order_id].append({
                "success": details.get("success") is True,
                "label": str(details.get("label") or ""),
                "local_logged_ts": timestamp,
                "ticker": ticker,
                "source_file": file_name,
            })
            continue
        lineage = str(details.get("trade_id") or "")
        if not lineage or ticker not in required_tickers:
            continue
        selected += 1
        receipt = {
            "local_logged_ts": timestamp,
            "ticker": ticker,
            "source_file": file_name,
        }
        if event_type == "entry_filled":
            receipt.update({
                "qty": number(details.get("qty")),
                "new_fills": number(details.get("new_fills")),
                "fill_price_cents": number(details.get("fill_price")),
                "kalshi_status": str(details.get("kalshi_status") or ""),
            })
            entry_fills[lineage].append(receipt)
        else:
            receipt.update({
                "settled_qty": number(details.get("settled_qty")),
                "settled_ts": parse_ts(details.get("settled_ts")),
            })
            settlements[lineage].append(receipt)
    for bucket in (placements, cancellations, entry_fills, settlements):
        for rows in bucket.values():
            rows.sort(key=lambda row: (
                row.get("local_logged_ts") is None,
                row.get("local_logged_ts") or 0,
            ))
    return LogEvidence(
        dict(placements), dict(cancellations), dict(entry_fills),
        dict(settlements),
        physical, selected, parse_errors,
    )


def recover_unmapped_fill_orders(
    fills: Sequence[Mapping[str, Any]],
    known_order_ids: set[str],
    event_map: Mapping[str, Mapping[str, Any]],
    logs: LogEvidence,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Recover exact order/lineage mapping from preserved order_placed rows.

    The join key is the private fill's literal order_id.  No ticker-only or
    nearest-time match is admitted.
    """
    recovered: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    target_order_ids = {
        str(fill["order_id"]) for fill in fills
        if fill.get("action") == "buy"
        and str(fill["order_id"]) not in known_order_ids
        and str(fill["ticker"]).rsplit("-", 1)[0] in event_map
    }
    for order_id in sorted(target_order_ids):
        receipts = logs.placements.get(order_id, [])
        if len(receipts) != 1:
            fill = next(
                row for row in fills if str(row["order_id"]) == order_id)
            ticker = str(fill["ticker"])
            gaps.append({
                "event_id": ticker.rsplit("-", 1)[0],
                "ticker": ticker,
                "gap_type": "unmapped_private_fill_order",
                "order_ref": evidence_ref(order_id),
                "placement_receipt_count": len(receipts),
                "detail": (
                    "private buy fill order_id lacks one unique preserved "
                    "order_placed receipt"),
            })
            continue
        receipt = receipts[0]
        ticker = str(receipt["ticker"])
        event_id = ticker.rsplit("-", 1)[0]
        if event_id not in event_map:
            gaps.append({
                "event_id": event_id,
                "ticker": ticker,
                "gap_type": "unmapped_private_fill_order",
                "order_ref": evidence_ref(order_id),
                "detail": "exact placement receipt maps outside D",
            })
            continue
        if ticker != next(
                str(row["ticker"]) for row in fills
                if str(row["order_id"]) == order_id):
            gaps.append({
                "event_id": event_id,
                "ticker": ticker,
                "gap_type": "unmapped_private_fill_order",
                "order_ref": evidence_ref(order_id),
                "detail": "exact placement and private fill ticker disagree",
            })
            continue
        lineage = str(receipt.get("trade_id") or "")
        if not lineage:
            gaps.append({
                "event_id": event_id,
                "ticker": ticker,
                "gap_type": "unmapped_private_fill_order",
                "order_ref": evidence_ref(order_id),
                "detail": "exact placement receipt lacks conception trade_id",
            })
            continue
        recovered.append({
            "event_id": event_id,
            "ticker": ticker,
            "leg": ticker.rsplit("-", 1)[-1],
            "trade_id": lineage,
            "order_id": order_id,
            "client_order_id": receipt.get("client_order_id"),
            "accepted": True,
            "purpose": "entry",
            "action": "buy",
            "price_cents": receipt.get("price_cents"),
            "quantity": receipt.get("quantity"),
            "local_logged_ts": receipt.get("local_logged_ts"),
            "exchange_created_ts": None,
            "exchange_status": None,
            "exchange_fill_count": None,
            "exchange_initial_count": receipt.get("quantity"),
            "exchange_remaining_count": None,
            "mapping_source": "exact_private_fill_order_id_to_order_placed",
        })
    return recovered, gaps


def unattributed_fill_lifecycles(
    fills: Sequence[Mapping[str, Any]],
    mapped_fill_ids: set[str],
    event_map: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Preserve real position increases whose entry lineage is unavailable.

    These are never promoted to a Window-1 fill.  They become explicit
    censored lifecycles at the public event/leg grain.
    """
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = (
        collections.defaultdict(list))
    for fill in fills:
        ticker = str(fill.get("ticker") or "")
        event_id = ticker.rsplit("-", 1)[0]
        if (fill.get("action") != "buy" or event_id not in event_map
                or str(fill.get("fill_id")) in mapped_fill_ids):
            continue
        grouped[(ticker, str(fill["order_id"]))].append(fill)
    rows = []
    for (ticker, order_id), group in sorted(grouped.items()):
        event_id = ticker.rsplit("-", 1)[0]
        group = sorted(group, key=lambda row: float(row["exchange_ts"]))
        quantity = sum(number(row["quantity"]) for row in group)
        cost = sum(
            number(row["quantity"]) * number(row["price_cents"])
            for row in group)
        rows.append({
            "event_id": event_id,
            "ticker": ticker,
            "lineage": "unattributed:" + evidence_ref(order_id),
            "status": "censored_unattributed_private_fill",
            "official_fill_quantity": quantity,
            "official_fill_vwap_cents": cost / quantity,
            "first_fill_exchange_ts": group[0]["exchange_ts"],
            "completion_exchange_ts": next((
                row["exchange_ts"] for index, row in enumerate(group)
                if sum(number(item["quantity"]) for item in group[:index + 1])
                >= REQUIRED_LOT), None),
            "accepted_order_ids": [order_id],
            "failed_attempts": 0,
            "official_fill_ids": [str(row["fill_id"]) for row in group],
            "cancellation_evidence": {},
            "entry_fill_receipts": [],
            "entry_fill_receipts_after_validation_edge": 0,
            "corroboration_warnings": [],
            "settlement_receipts": [],
            "censor_reasons": ["private_fill_lacks_entry_lineage"],
            "_orders": [],
        })
    return rows


def lifecycle_key(order: Mapping[str, Any]) -> tuple[str, str, str]:
    event_id = str(order.get("event_id") or "")
    ticker = str(order.get("ticker") or "")
    lineage = str(order.get("trade_id") or "")
    if not lineage:
        lineage = "attempt:" + str(
            order.get("attempt_id") or order.get("order_id") or
            evidence_ref(json_dump(order)))
    return event_id, ticker, lineage


def first_five_vwap(fills: Sequence[Mapping[str, Any]]) -> float | None:
    needed = REQUIRED_LOT
    cost = 0.0
    taken = 0.0
    for fill in sorted(fills, key=lambda row: float(row["exchange_ts"])):
        use = min(needed, number(fill.get("quantity")))
        cost += use * number(fill.get("price_cents"))
        taken += use
        needed -= use
        if needed <= 1e-9:
            return cost / taken
    return None


def exact_zero_fill_closure(
    order: Mapping[str, Any],
    cancellations: Sequence[Mapping[str, Any]],
) -> tuple[bool, str]:
    status = str(order.get("exchange_status") or "").lower()
    fill_count = order.get("exchange_fill_count")
    if status in TERMINAL_ZERO_FILL and (
            fill_count in (None, "") or math.isclose(
                number(fill_count), 0.0, abs_tol=1e-9)):
        return True, "official_zero_fill_terminal"
    successful = [row for row in cancellations
                  if row.get("success") is True]
    if successful:
        return True, "exact_successful_delete"
    if cancellations:
        return False, "cancellation_failed_or_unconfirmed"
    if status:
        return False, f"nonzero_or_nonterminal_status:{status}"
    return False, "terminal_or_cancellation_evidence_missing"


def classify_lifecycle(
    key: tuple[str, str, str],
    orders: Sequence[Mapping[str, Any]],
    fills_by_order: Mapping[str, Sequence[Mapping[str, Any]]],
    log_evidence: LogEvidence,
    unmatched_buy_fills_by_ticker: Mapping[
        str, Sequence[Mapping[str, Any]]],
    edge: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    event_id, ticker, lineage = key
    mismatches: list[dict[str, Any]] = []
    accepted = [row for row in orders if row.get("accepted") is not False]
    failed = [row for row in orders if row.get("accepted") is False]
    order_ids = [str(row.get("order_id") or "")
                 for row in accepted if row.get("order_id")]
    official_fills = [
        fill for order_id in order_ids
        for fill in fills_by_order.get(order_id, ())
        if fill.get("action") == "buy"
        and float(fill["exchange_ts"]) <= edge
    ]
    official_fills.sort(
        key=lambda row: (float(row["exchange_ts"]), str(row["fill_id"])))
    official_quantity = sum(
        number(row["quantity"]) for row in official_fills)
    official_cost = sum(
        number(row["quantity"]) * number(row["price_cents"])
        for row in official_fills)
    official_vwap = (
        official_cost / official_quantity if official_quantity > 0 else None)
    engine_fills_all = log_evidence.entry_fills.get(lineage, [])
    engine_fills = [
        row for row in engine_fills_all
        if row.get("local_logged_ts") is None
        or float(row["local_logged_ts"]) <= edge
    ]
    settlements = log_evidence.settlements.get(lineage, [])

    # Every engine-booked fill must have official private-fill support.
    times = [parse_ts(row.get("local_logged_ts")) for row in accepted]
    starts = [value for value in times if value is not None]
    start = min(starts) if starts else None
    unmatched_position_increase = [
        row for row in unmatched_buy_fills_by_ticker.get(ticker, ())
        if (start is None or float(row["exchange_ts"]) >= start)
        and float(row["exchange_ts"]) <= edge
    ]

    if (engine_fills and official_quantity <= 0
            and not unmatched_position_increase):
        mismatches.append({
            "event_id": event_id,
            "ticker": ticker,
            "mismatch_type": "entry_fill_without_private_fill",
            "lineage_ref": evidence_ref(lineage),
            "detail": "engine entry_filled exists but complete private fills have none",
        })
    corroboration_warnings = []
    if engine_fills and official_quantity > 0:
        logged_qty = max(number(row.get("qty")) for row in engine_fills)
        if not math.isclose(
                logged_qty, official_quantity, rel_tol=0.0, abs_tol=1e-9):
            corroboration_warnings.append({
                "warning_type": "engine_fill_quantity_differs_from_private",
                "official_quantity": official_quantity,
                "logged_quantity": logged_qty,
            })
        logged_prices = {
            number(row.get("fill_price_cents")) for row in engine_fills
            if row.get("fill_price_cents") not in (None, "")
        }
        if (official_vwap is not None and logged_prices
                and not any(math.isclose(
                    value, official_vwap, rel_tol=0.0, abs_tol=1e-9)
                    for value in logged_prices)):
            corroboration_warnings.append({
                "warning_type": "engine_fill_price_differs_from_private_vwap",
                "official_vwap_cents": official_vwap,
                "logged_price_values": sorted(logged_prices),
            })

    if official_quantity > 0:
        status = (
            "exact_filled_five" if math.isclose(
                official_quantity, REQUIRED_LOT,
                rel_tol=0.0, abs_tol=1e-9)
            else "exact_filled_other_quantity")
        return {
            "event_id": event_id,
            "ticker": ticker,
            "lineage": lineage,
            "status": status,
            "official_fill_quantity": official_quantity,
            "official_fill_vwap_cents": official_vwap,
            "first_fill_exchange_ts": (
                official_fills[0]["exchange_ts"] if official_fills else None),
            "completion_exchange_ts": next((
                row["exchange_ts"] for index, row in enumerate(official_fills)
                if sum(number(item["quantity"])
                       for item in official_fills[:index + 1])
                >= REQUIRED_LOT), None),
            "accepted_order_ids": order_ids,
            "failed_attempts": len(failed),
            "official_fill_ids": [
                str(row["fill_id"]) for row in official_fills],
            "cancellation_evidence": {
                order_id: log_evidence.cancellations.get(order_id, [])
                for order_id in order_ids
            },
            "entry_fill_receipts": engine_fills,
            "entry_fill_receipts_after_validation_edge": (
                len(engine_fills_all) - len(engine_fills)),
            "corroboration_warnings": corroboration_warnings,
            "settlement_receipts": settlements,
            "censor_reasons": [],
        }, mismatches

    closure_reasons = []
    all_closed = bool(accepted)
    for order in accepted:
        order_id = str(order.get("order_id") or "")
        closed, reason = exact_zero_fill_closure(
            order, log_evidence.cancellations.get(order_id, ()))
        closure_reasons.append({
            "order_id": order_id,
            "closed": closed,
            "reason": reason,
        })
        all_closed = all_closed and closed

    censor_reasons = []
    if not accepted:
        censor_reasons.append("no_accepted_order")
    if not all_closed:
        censor_reasons.append("accepted_order_not_exactly_closed")
    if engine_fills:
        censor_reasons.append("entry_fill_attribution_without_private_fill")
    if unmatched_position_increase:
        censor_reasons.append("unmatched_position_increase_proxy")
    if settlements:
        censor_reasons.append("unmatched_settlement")
    if failed and not accepted:
        censor_reasons.append("failed_attempt_exchange_clock_not_recovered")
    status = "exact_nonfill" if not censor_reasons else "censored"
    return {
        "event_id": event_id,
        "ticker": ticker,
        "lineage": lineage,
        "status": status,
        "official_fill_quantity": 0.0,
        "official_fill_vwap_cents": None,
        "first_fill_exchange_ts": None,
        "completion_exchange_ts": None,
        "accepted_order_ids": order_ids,
        "failed_attempts": len(failed),
        "official_fill_ids": [],
        "closure_receipts": closure_reasons,
        "cancellation_evidence": {
            order_id: log_evidence.cancellations.get(order_id, [])
            for order_id in order_ids
        },
        "entry_fill_receipts": engine_fills,
        "entry_fill_receipts_after_validation_edge": (
            len(engine_fills_all) - len(engine_fills)),
        "corroboration_warnings": corroboration_warnings,
        "settlement_receipts": settlements,
        "unmatched_buy_fill_ids": [
            str(row["fill_id"]) for row in unmatched_position_increase],
        "censor_reasons": censor_reasons,
    }, mismatches


def sanitize_lifecycle(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": row["event_id"],
        "ticker": row["ticker"],
        "lineage_ref": evidence_ref(row["lineage"]),
        "status": row["status"],
        "accepted_order_count": len(row.get("accepted_order_ids") or []),
        "failed_attempts": row.get("failed_attempts", 0),
        "official_fill_count": len(row.get("official_fill_ids") or []),
        "official_fill_quantity": row.get("official_fill_quantity"),
        "official_fill_vwap_cents": row.get("official_fill_vwap_cents"),
        "first_fill_exchange_ts": iso_utc(row.get("first_fill_exchange_ts")),
        "completion_exchange_ts": iso_utc(
            row.get("completion_exchange_ts")),
        "successful_cancellation_count": sum(
            receipt.get("success") is True
            for receipts in (row.get("cancellation_evidence") or {}).values()
            for receipt in receipts
        ),
        "entry_fill_receipt_count": len(
            row.get("entry_fill_receipts") or []),
        "entry_fill_receipt_after_edge_count": int(
            row.get("entry_fill_receipts_after_validation_edge") or 0),
        "corroboration_warning_count": len(
            row.get("corroboration_warnings") or []),
        "settlement_receipt_count": len(
            row.get("settlement_receipts") or []),
        "censor_reasons": sorted(set(row.get("censor_reasons") or [])),
        "private_identifiers_included": False,
    }


def leg_row(
    event: Mapping[str, Any],
    ticker: str,
    lifecycles: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    attributable = [
        row for row in lifecycles
        if row.get("status") != "censored_unattributed_private_fill"
    ]
    unattributed = [
        row for row in lifecycles
        if row.get("status") == "censored_unattributed_private_fill"
    ]
    quantity = sum(number(row.get("official_fill_quantity"))
                   for row in attributable)
    vwap_numerator = sum(
        number(row.get("official_fill_quantity"))
        * number(row.get("official_fill_vwap_cents"))
        for row in attributable
        if row.get("official_fill_vwap_cents") is not None)
    vwap = vwap_numerator / quantity if quantity > 0 else None
    if unattributed:
        status = "censored"
    elif math.isclose(quantity, REQUIRED_LOT, rel_tol=0.0, abs_tol=1e-9):
        status = "exact_filled_five"
    elif quantity > 0:
        status = "exact_filled_other_quantity"
    elif lifecycles and all(
            row.get("status") == "exact_nonfill" for row in lifecycles):
        status = "exact_nonfill"
    elif not lifecycles and decisions:
        status = "exact_nonfill"
    else:
        status = "censored"
    censor_reasons = sorted({
        reason for row in lifecycles
        for reason in row.get("censor_reasons") or []
    })
    if unattributed:
        censor_reasons.append("private_fill_lacks_entry_lineage")
    if status == "censored" and not lifecycles and not decisions:
        censor_reasons.append("required_leg_decision_unobserved")
    possible_five = (
        status == "exact_filled_five"
        or (status == "censored" and (
            sum(official_order_quantity(order)
                for row in lifecycles
                for order in row.get("_orders") or []) >= REQUIRED_LOT
            or not lifecycles))
    )
    leg_name = ticker.rsplit("-", 1)[-1] if "-" in ticker else ticker
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": str(event["event_id"]),
        "event_date": str(event["event_date"]),
        "category": str(event["category"]),
        "ticker": ticker,
        "leg": leg_name,
        "status": status,
        "official_fill_quantity": quantity,
        "official_fill_vwap_cents": vwap,
        "lifecycle_count": len(lifecycles),
        "accepted_order_count": sum(
            len(row.get("accepted_order_ids") or []) for row in lifecycles),
        "failed_attempt_count": sum(
            int(row.get("failed_attempts") or 0) for row in lifecycles),
        "causal_nonplacement_receipt_count": len(decisions),
        "censor_reasons": sorted(set(censor_reasons)),
        "possible_five_contract_upper_bound": possible_five,
        "provenance": {
            "fill_truth": "complete_paginated_private_fills_export",
            "nonfill_truth": (
                "official_zero_fill_terminal_or_exact_successful_delete"
                if status == "exact_nonfill" else None),
            "lineage": "engine_trade_id_conception_lineage",
            "order_ids_retained_private": True,
        },
    }


def build_event_bounds(
    events: Sequence[Mapping[str, Any]],
    legs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    by_event: dict[str, list[Mapping[str, Any]]] = (
        collections.defaultdict(list))
    for row in legs:
        by_event[str(row["event_id"])].append(row)
    lower = best = censored_events = 0
    observed_exact_five = 0
    for event in events:
        rows = by_event.get(str(event["event_id"]), [])
        exact = len(rows) == 2 and all(
            row.get("status") == "exact_filled_five" for row in rows)
        possible = len(rows) == 2 and all(
            row.get("possible_five_contract_upper_bound") for row in rows)
        if exact:
            lower += 1
            observed_exact_five += 1
        if possible:
            best += 1
        if any(row.get("status") == "censored" for row in rows):
            censored_events += 1
    return {
        "D": len(events),
        "worst_case_dual_five": lower,
        "observed_exact_dual_five": observed_exact_five,
        "best_case_dual_five": best,
        "censored_event_count": censored_events,
        "not_a_policy_result": True,
    }


def run(args: argparse.Namespace) -> int:
    events_path = Path(args.events).resolve()
    orders_path = Path(args.orders).resolve()
    fills_path = Path(args.private_fills).resolve()
    manifest_path = Path(args.export_manifest).resolve()
    decisions_path = Path(args.decisions).resolve()
    log_dir = Path(args.log_dir).resolve()
    private_output = Path(args.private_output).resolve()
    public_output = Path(args.public_output).resolve()
    private_output.mkdir(parents=True, exist_ok=True)
    public_output.mkdir(parents=True, exist_ok=True)
    os.chmod(private_output, 0o700)

    events = read_jsonl(events_path)
    if len(events) != 804:
        raise LifecycleError(f"D changed: expected 804 events, got {len(events)}")
    event_map = {str(row["event_id"]): row for row in events}
    if len(event_map) != 804:
        raise LifecycleError("event ledger contains duplicate event ids")
    required_tickers = {
        ticker for event in events for ticker in leg_tickers(event)}
    if len(required_tickers) != 1608:
        raise LifecycleError(
            f"required-leg count changed: expected 1608, got {len(required_tickers)}")

    all_orders = read_jsonl(orders_path)
    orders = [
        row for row in all_orders
        if str(row.get("event_id") or "") in event_map
        and row.get("purpose") == "entry"
        and row.get("action") == "buy"
    ]
    decisions = [
        row for row in read_jsonl(decisions_path)
        if str(row.get("event_id") or "") in event_map
    ]
    export_receipt = validate_export_receipt(
        read_json(manifest_path), fills_path)
    raw_fills = read_jsonl(fills_path)
    fills, mismatches = canonical_private_fills(raw_fills)

    orders_by_id = {
        str(row.get("order_id") or ""): row for row in orders
        if row.get("order_id")
    }
    fills_by_order: dict[str, list[dict[str, Any]]] = (
        collections.defaultdict(list))
    for fill in fills:
        fills_by_order[str(fill["order_id"])].append(fill)
    mapped_fill_ids = {
        str(fill["fill_id"]) for order_id, rows in fills_by_order.items()
        if order_id in orders_by_id for fill in rows
    }
    unmatched_buy_fills_by_ticker: dict[str, list[dict[str, Any]]] = (
        collections.defaultdict(list))
    for fill in fills:
        if (fill["action"] == "buy"
                and fill["ticker"] in required_tickers
                and str(fill["fill_id"]) not in mapped_fill_ids):
            unmatched_buy_fills_by_ticker[str(fill["ticker"])].append(fill)

    order_ids = set(orders_by_id)
    order_ids.update(
        str(fill["order_id"]) for fill in fills
        if fill.get("action") == "buy"
        and str(fill["ticker"]).rsplit("-", 1)[0] in event_map
    )
    logs = scan_logs(
        log_dir, args.active_log_name, args.active_log_prefix_bytes,
        order_ids, required_tickers)
    recovered_orders, recovery_gaps = recover_unmapped_fill_orders(
        fills, set(orders_by_id), event_map, logs)
    orders.extend(recovered_orders)
    for row in recovered_orders:
        orders_by_id[str(row["order_id"])] = row

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = (
        collections.defaultdict(list))
    for order in orders:
        grouped[lifecycle_key(order)].append(order)

    mapped_fill_ids = {
        str(fill["fill_id"]) for order_id, rows in fills_by_order.items()
        if order_id in orders_by_id for fill in rows
    }
    unmatched_buy_fills_by_ticker = collections.defaultdict(list)
    for fill in fills:
        if (fill["action"] == "buy"
                and fill["ticker"] in required_tickers
                and str(fill["fill_id"]) not in mapped_fill_ids):
            unmatched_buy_fills_by_ticker[str(fill["ticker"])].append(fill)

    private_lifecycles = []
    for key in sorted(grouped):
        event = event_map[key[0]]
        row, row_mismatches = classify_lifecycle(
            key, grouped[key], fills_by_order, logs,
            unmatched_buy_fills_by_ticker, validation_edge(event))
        row["_orders"] = grouped[key]
        private_lifecycles.append(row)
        mismatches.extend(row_mismatches)
    private_lifecycles.extend(unattributed_fill_lifecycles(
        fills, mapped_fill_ids, event_map))

    decisions_by_leg: dict[tuple[str, str], list[dict[str, Any]]] = (
        collections.defaultdict(list))
    for row in decisions:
        decisions_by_leg[(
            str(row.get("event_id") or ""),
            str(row.get("ticker") or ""),
        )].append(row)
    lifecycle_by_leg: dict[tuple[str, str], list[dict[str, Any]]] = (
        collections.defaultdict(list))
    for row in private_lifecycles:
        lifecycle_by_leg[(row["event_id"], row["ticker"])].append(row)

    leg_rows = []
    for event in sorted(
            events, key=lambda row: (row["event_date"], row["event_id"])):
        tickers = leg_tickers(event)
        if len(tickers) != 2:
            mismatches.append({
                "event_id": event.get("event_id"),
                "mismatch_type": "event_leg_contract",
                "detail": "event does not have exactly two legs",
            })
            continue
        for ticker in tickers:
            leg_rows.append(leg_row(
                event, ticker,
                lifecycle_by_leg.get((str(event["event_id"]), ticker), ()),
                decisions_by_leg.get((str(event["event_id"]), ticker), ()),
            ))
    if len(leg_rows) != 1608:
        mismatches.append({
            "mismatch_type": "ledger",
            "detail": f"expected 1608 leg rows, got {len(leg_rows)}",
        })

    if not export_receipt["complete"]:
        for detail in export_receipt["errors"]:
            mismatches.append({
                "mismatch_type": "private_fill_pagination",
                "detail": detail,
            })
    if logs.parse_errors:
        mismatches.append({
            "mismatch_type": "engine_log_parse",
            "detail": f"{logs.parse_errors} selected engine log rows malformed",
        })

    # Position reconciliation is complete at bounded grain: every private buy
    # fill is either identity-mapped to a lineage or represented by an explicit
    # censored lifecycle.  Unattributed fills are never called nonfills/fills.
    unattributed_lifecycles = [
        row for row in private_lifecycles
        if row.get("status") == "censored_unattributed_private_fill"]
    represented_unattributed_ids = {
        fill_id for row in unattributed_lifecycles
        for fill_id in row.get("official_fill_ids") or []}
    expected_unattributed_ids = {
        str(fill["fill_id"]) for rows in unmatched_buy_fills_by_ticker.values()
        for fill in rows}
    position_complete = (
        represented_unattributed_ids == expected_unattributed_ids)
    if not position_complete:
        mismatches.append({
            "mismatch_type": "position_reconciliation",
            "detail": (
                "unattributed private buy fills were not fully represented "
                "as censored lifecycles"),
        })

    day_rows: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in leg_rows:
        day_rows[str(row["event_date"])].append(row)
    day_closure = {
        day: {
            "event_count": len(rows) // 2,
            "required_leg_count": len(rows),
            "private_fill_pagination_complete": export_receipt["complete"],
            "position_reconciliation_complete": position_complete,
            "day_closed": (
                export_receipt["complete"] and position_complete
                and not any(
                    mismatch.get("event_id") in {
                        row["event_id"] for row in rows}
                    for mismatch in mismatches)
            ),
        }
        for day, rows in sorted(day_rows.items())
    }

    private_path = private_output / "LIFECYCLE_VALIDATION.private.jsonl"
    private_clean = []
    for row in private_lifecycles:
        row = dict(row)
        row.pop("_orders", None)
        private_clean.append(row)
    write_jsonl(private_path, private_clean, mode=0o600)
    sanitized_lifecycles = [
        sanitize_lifecycle(row) for row in private_lifecycles]
    write_jsonl(
        public_output / "LIFECYCLE_VALIDATION.sanitized.jsonl",
        sanitized_lifecycles,
    )
    write_jsonl(
        public_output / "EVENT_LEG_LIFECYCLE_LEDGER.jsonl", leg_rows)
    sanitized_mismatches = []
    for row in mismatches:
        sanitized_mismatches.append({
            key: value for key, value in row.items()
            if key not in {"order_id", "fill_id", "trade_id", "client_order_id"}
        })
    write_jsonl(
        public_output / "LIFECYCLE_MISMATCHES.sanitized.jsonl",
        sanitized_mismatches,
    )
    bounds = build_event_bounds(events, leg_rows)
    mismatch_types = collections.Counter(
        str(row.get("mismatch_type") or "unknown")
        for row in sanitized_mismatches)
    leg_status = collections.Counter(
        str(row.get("status") or "unknown") for row in leg_rows)
    lifecycle_status = collections.Counter(
        str(row.get("status") or "unknown")
        for row in private_lifecycles)
    gate_pass = (
        export_receipt["complete"]
        and position_complete
        and not sanitized_mismatches
        and len(leg_rows) == 1608
    )
    summary = {
        "schema_version": SCHEMA_VERSION,
        "D": 804,
        "required_legs": 1608,
        "gate_pass": gate_pass,
        "validation_unit": "event_leg_conception_trade_lineage",
        "lifecycle_rows": len(private_lifecycles),
        "lifecycle_status_counts": dict(sorted(lifecycle_status.items())),
        "leg_status_counts": dict(sorted(leg_status.items())),
        "censored_leg_count": leg_status["censored"],
        "mismatch_count": len(sanitized_mismatches),
        "mismatch_types": dict(sorted(mismatch_types.items())),
        "actual_completion_bounds": bounds,
        "day_closure": day_closure,
        "private_fill_export": export_receipt,
        "engine_log_scan": {
            "physical_rows": logs.physical_rows,
            "selected_rows": logs.selected_rows,
            "parse_errors": logs.parse_errors,
            "active_log_name": args.active_log_name,
            "active_log_prefix_bytes": args.active_log_prefix_bytes,
        },
        "position_reconciliation": {
            "complete_with_censoring": position_complete,
            "unattributed_private_buy_fill_rows": len(
                expected_unattributed_ids),
            "unattributed_private_buy_order_lifecycles": len(
                unattributed_lifecycles),
            "recovered_by_exact_order_id_placement": len(recovered_orders),
            "unrecovered_entry_lineage_gaps": len(recovery_gaps),
            "all_unrecovered_fills_preserved_as_censored": (
                position_complete),
        },
        "mapping_recovery_gaps": [{
            key: value for key, value in row.items()
            if key not in {"order_id", "fill_id", "trade_id", "client_order_id"}
        } for row in recovery_gaps],
        "private_lifecycle_sha256": sha256_file(private_path),
        "public_event_leg_ledger_sha256": sha256_file(
            public_output / "EVENT_LEG_LIFECYCLE_LEDGER.jsonl"),
        "private_identifiers_in_public_outputs": False,
        "strategy_scoring_permitted": gate_pass,
        "D_changed": False,
        "window2_exit_settlement_policy_or_dca_used": False,
    }
    write_json(public_output / "LIFECYCLE_VALIDATION_SUMMARY.json", summary)
    print(json.dumps({
        "D": 804,
        "required_legs": 1608,
        "gate_pass": gate_pass,
        "lifecycle_status_counts": dict(sorted(lifecycle_status.items())),
        "leg_status_counts": dict(sorted(leg_status.items())),
        "mismatch_types": dict(sorted(mismatch_types.items())),
        "private_identifiers_printed": False,
    }, sort_keys=True))
    return 0 if gate_pass else 3


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--events", required=True)
    root.add_argument("--orders", required=True)
    root.add_argument("--decisions", required=True)
    root.add_argument("--private-fills", required=True)
    root.add_argument("--export-manifest", required=True)
    root.add_argument("--log-dir", required=True)
    root.add_argument("--active-log-name", default="live_v3_20260720.jsonl")
    root.add_argument("--active-log-prefix-bytes", type=int, required=True)
    root.add_argument("--private-output", required=True)
    root.add_argument("--public-output", required=True)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return run(args)
    except LifecycleError as exc:
        print(f"WINDOW1-LIFECYCLE-BLOCKED: {exc}", file=os.sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
