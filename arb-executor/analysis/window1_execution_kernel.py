#!/usr/bin/env python3
"""Shared causal execution kernel for Window-1 research.

The counterfactual path consumes only positive, exchange-identified prints.
The historical path consumes the frozen private placement/cancel/fill
receipts and reduces them to the immutable event/leg denominator.  Keeping
both paths here prevents a calibration-only replay from using a different
fill reducer than a later, separately authorized candidate run.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
from bisect import bisect_right
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence


VERSION = "window1-execution-kernel-v1"
LOT = 5.0
TERMINAL_ZERO_FILL = {"canceled", "cancelled", "rejected", "expired"}


class ExecutionKernelError(RuntimeError):
    """A fail-closed execution-evidence contract violation."""


def number(value: Any) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ExecutionKernelError(f"non-numeric value: {value!r}") from exc
    if not math.isfinite(result):
        raise ExecutionKernelError(f"non-finite value: {value!r}")
    return result


def parse_ts(value: Any) -> float:
    if value in (None, ""):
        raise ExecutionKernelError("timestamp is missing")
    if isinstance(value, (int, float)):
        result = float(value)
        if result > 10_000_000_000:
            result /= 1000.0
        if not math.isfinite(result):
            raise ExecutionKernelError("timestamp is non-finite")
        return result
    try:
        parsed = dt.datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise ExecutionKernelError(
            f"timestamp is not ISO-8601: {value!r}"
        ) from exc
    if parsed.tzinfo is None:
        raise ExecutionKernelError("timestamp lacks timezone")
    return parsed.timestamp()


def _decimal_text(value: Any) -> str:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ExecutionKernelError(
            f"invalid decimal quantity: {value!r}"
        ) from exc
    if not parsed.is_finite():
        raise ExecutionKernelError("decimal quantity is non-finite")
    return format(parsed.normalize(), "f")


def _lineage(order: Mapping[str, Any]) -> str:
    explicit = str(order.get("trade_id") or "")
    if explicit:
        return explicit
    fallback = str(order.get("attempt_id") or order.get("order_id") or "")
    if not fallback:
        payload = json.dumps(
            dict(order), sort_keys=True, separators=(",", ":")
        )
        fallback = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
    return "attempt:" + fallback


def _fill_identity(row: Mapping[str, Any]) -> str:
    identity = str(row.get("fill_id") or row.get("trade_id") or "")
    if not identity:
        raise ExecutionKernelError("private fill lacks fill identity")
    return identity


def _fill_price_cents(row: Mapping[str, Any]) -> float:
    value = row.get("yes_price_dollars")
    if value in (None, ""):
        no_value = row.get("no_price_dollars")
        if no_value in (None, ""):
            raise ExecutionKernelError(
                "private fill lacks YES/NO exchange price"
            )
        return round((1.0 - number(no_value)) * 100.0, 10)
    return round(number(value) * 100.0, 10)


def canonical_private_fill(row: Mapping[str, Any]) -> dict[str, Any]:
    quantity = number(row.get("count_fp"))
    if quantity <= 0:
        raise ExecutionKernelError(
            "zero/negative private fill may not be promoted"
        )
    ticker = str(row.get("ticker") or row.get("market_ticker") or "")
    order_id = str(row.get("order_id") or "")
    if not ticker or not order_id:
        raise ExecutionKernelError("private fill lacks ticker/order identity")
    return {
        "fill_id": _fill_identity(row),
        "trade_id": str(row.get("trade_id") or ""),
        "order_id": order_id,
        "ticker": ticker,
        "action": str(row.get("action") or "").lower(),
        "quantity": quantity,
        "quantity_decimal": _decimal_text(row.get("count_fp")),
        "price_cents": _fill_price_cents(row),
        "exchange_ts": parse_ts(
            row.get("created_time") or row.get("ts_ms") or row.get("ts")
        ),
    }


def simulate_candidate_actions(
    actions: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    right: float,
    queue_case: str,
    *,
    initial_quantity: float = 0.0,
    initial_cost: float = 0.0,
    lot: float = LOT,
) -> dict[str, Any]:
    """Causal counterfactual reducer used by any future candidate scorer."""
    quantity = initial_quantity
    cost = initial_cost
    first_fill: float | None = None
    completion: float | None = None
    if queue_case not in {"lower", "upper"}:
        raise ExecutionKernelError("queue_case must be lower or upper")
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
        if start >= stop or quantity >= lot:
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
                add = lot - quantity
            else:
                same_cumulative += float(trade["size"])
                new_credit = max(0.0, same_cumulative - queue)
                add = min(
                    lot - quantity,
                    max(0.0, new_credit - credited_same),
                )
                credited_same = new_credit
            if add <= 0:
                continue
            if first_fill is None:
                first_fill = timestamp
            quantity += add
            cost += add * price
            if quantity >= lot - 1e-9:
                quantity = lot
                completion = timestamp
                break
        if completion is not None:
            break
    return {
        "status": "filled" if quantity >= lot else "not_filled",
        "quantity": quantity,
        "cost": cost,
        "vwap": cost / quantity if quantity else None,
        "first_fill_ts": first_fill,
        "completion_ts": completion,
    }


def _mismatch(
    event_id: str,
    ticker: str,
    mismatch_type: str,
    detail: str,
) -> dict[str, str]:
    return {
        "event_id": event_id,
        "ticker": ticker,
        "mismatch_type": mismatch_type,
        "detail": detail,
    }


def _closed_order(
    order: Mapping[str, Any],
    closure: Mapping[str, Any] | None,
    cancellations: Sequence[Mapping[str, Any]],
) -> bool:
    if closure is not None and closure.get("closed") is True:
        return True
    if any(row.get("success") is True for row in cancellations):
        return True
    status = str(order.get("exchange_status") or "").lower()
    fill_count = order.get("exchange_fill_count")
    return status in TERMINAL_ZERO_FILL and (
        fill_count in (None, "")
        or math.isclose(number(fill_count), 0.0, abs_tol=1e-9)
    )


def replay_historical_execution(
    events: Sequence[Mapping[str, Any]],
    orders: Sequence[Mapping[str, Any]],
    raw_fills: Sequence[Mapping[str, Any]],
    private_lifecycles: Sequence[Mapping[str, Any]],
    causal_decisions: Sequence[Mapping[str, Any]],
    expected_legs: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Replay receipt-grain historical execution without schedule data."""
    mismatches: list[dict[str, str]] = []
    event_by_id: dict[str, Mapping[str, Any]] = {}
    required_tickers: set[str] = set()
    ticker_to_event: dict[str, Mapping[str, Any]] = {}
    for event in events:
        event_id = str(event.get("event_id") or "")
        if not event_id or event_id in event_by_id:
            raise ExecutionKernelError("event denominator identity is invalid")
        event_by_id[event_id] = event
        legs = event.get("legs") or []
        if len(legs) != 2:
            raise ExecutionKernelError(
                f"event {event_id} does not have exactly two legs"
            )
        for leg in legs:
            ticker = str(leg.get("ticker") or "")
            if not ticker or ticker in required_tickers:
                raise ExecutionKernelError(
                    f"duplicate/missing required ticker in {event_id}"
                )
            required_tickers.add(ticker)
            ticker_to_event[ticker] = event

    order_by_id: dict[str, Mapping[str, Any]] = {}
    failed_by_key: dict[tuple[str, str, str], list[Mapping[str, Any]]] = (
        defaultdict(list)
    )
    for order in orders:
        order_id = str(order.get("order_id") or "")
        if order.get("accepted") is False:
            failed_by_key[(
                str(order.get("event_id") or ""),
                str(order.get("ticker") or ""),
                _lineage(order),
            )].append(order)
            continue
        if not order_id:
            continue
        if order_id in order_by_id:
            raise ExecutionKernelError("duplicate accepted order identity")
        order_by_id[order_id] = order

    fills: dict[str, dict[str, Any]] = {}
    for source in raw_fills:
        canonical = canonical_private_fill(source)
        identity = canonical["fill_id"]
        prior = fills.get(identity)
        if prior is not None and prior != canonical:
            raise ExecutionKernelError(
                "duplicate fill identity has conflicting payload"
            )
        fills[identity] = canonical

    lifecycle_keys: set[tuple[str, str, str]] = set()
    lifecycle_by_ticker: dict[str, list[dict[str, Any]]] = defaultdict(list)
    used_orders: set[str] = set()
    used_fills: set[str] = set()
    used_failed_attempts = 0
    cancel_receipt_signatures: set[str] = set()
    cancellation_receipt_rows = 0
    cancellation_success_rows = 0
    placements_with_exchange_ts = 0
    placements_with_local_ts = 0
    placement_price_rows = 0
    placement_quantity_rows = 0

    for source in private_lifecycles:
        row = dict(source)
        event_id = str(row.get("event_id") or "")
        ticker = str(row.get("ticker") or "")
        lineage = str(row.get("lineage") or "")
        key = (event_id, ticker, lineage)
        if key in lifecycle_keys:
            mismatches.append(_mismatch(
                event_id, ticker, "duplicate_lifecycle",
                "event/ticker/conception lineage repeated",
            ))
            continue
        lifecycle_keys.add(key)
        if event_id not in event_by_id or ticker not in required_tickers:
            mismatches.append(_mismatch(
                event_id, ticker, "lifecycle_outside_D",
                "lifecycle does not resolve to one required D leg",
            ))
            continue

        expected_status = str(row.get("status") or "")
        accepted_ids = [
            str(value) for value in row.get("accepted_order_ids") or []
        ]
        if len(accepted_ids) != len(set(accepted_ids)):
            mismatches.append(_mismatch(
                event_id, ticker, "duplicate_order_receipt",
                "accepted order identity repeats inside lifecycle",
            ))
        found_orders: list[Mapping[str, Any]] = []
        for order_id in accepted_ids:
            if order_id in used_orders:
                mismatches.append(_mismatch(
                    event_id, ticker, "duplicate_order_membership",
                    "accepted order belongs to more than one lifecycle",
                ))
                continue
            used_orders.add(order_id)
            order = order_by_id.get(order_id)
            if order is None:
                if expected_status != "censored_unattributed_private_fill":
                    mismatches.append(_mismatch(
                        event_id, ticker, "placement_receipt_missing",
                        "attributable accepted placement is absent",
                    ))
                continue
            found_orders.append(order)
            if (
                str(order.get("event_id") or "") != event_id
                or str(order.get("ticker") or "") != ticker
                or _lineage(order) != lineage
            ):
                mismatches.append(_mismatch(
                    event_id, ticker, "placement_lineage_mismatch",
                    "accepted placement does not match lifecycle identity",
                ))
            if str(order.get("action") or "").lower() != "buy":
                mismatches.append(_mismatch(
                    event_id, ticker, "placement_action_mismatch",
                    "Window-1 entry placement is not a buy",
                ))
            try:
                price = int(order.get("price_cents"))
                quantity = number(order.get("quantity"))
                if not 1 <= price <= 99 or quantity <= 0:
                    raise ExecutionKernelError("invalid placement economics")
                placement_price_rows += 1
                placement_quantity_rows += 1
                parse_ts(order.get("local_logged_ts"))
                placements_with_local_ts += 1
                if order.get("exchange_created_ts") not in (None, ""):
                    parse_ts(order.get("exchange_created_ts"))
                    placements_with_exchange_ts += 1
            except (ExecutionKernelError, TypeError, ValueError):
                mismatches.append(_mismatch(
                    event_id, ticker, "placement_contract",
                    "placement lacks valid price/quantity/timestamp",
                ))

        failed_rows = failed_by_key.get(key, [])
        expected_failed = int(row.get("failed_attempts") or 0)
        if len(failed_rows) != expected_failed:
            mismatches.append(_mismatch(
                event_id, ticker, "failed_attempt_count",
                "failed placement attempts do not reproduce lifecycle",
            ))
        used_failed_attempts += min(len(failed_rows), expected_failed)
        for failed in failed_rows:
            try:
                price = int(failed.get("price_cents"))
                quantity = number(failed.get("quantity"))
                parse_ts(failed.get("local_logged_ts"))
                if not 1 <= price <= 99 or quantity <= 0:
                    raise ExecutionKernelError("invalid failed placement")
                placement_price_rows += 1
                placement_quantity_rows += 1
                placements_with_local_ts += 1
            except (ExecutionKernelError, TypeError, ValueError):
                mismatches.append(_mismatch(
                    event_id, ticker, "failed_placement_contract",
                    "failed attempt lacks valid economics/local timestamp",
                ))

        cancellations_by_order = row.get("cancellation_evidence") or {}
        for order_id, receipts in cancellations_by_order.items():
            for receipt in receipts:
                cancellation_receipt_rows += 1
                if receipt.get("success") is True:
                    cancellation_success_rows += 1
                signature = json.dumps(
                    [order_id, receipt],
                    sort_keys=True,
                    separators=(",", ":"),
                )
                if signature in cancel_receipt_signatures:
                    mismatches.append(_mismatch(
                        event_id, ticker, "duplicate_cancel_receipt",
                        "identical cancellation receipt was counted twice",
                    ))
                cancel_receipt_signatures.add(signature)
                try:
                    parse_ts(receipt.get("local_logged_ts"))
                except ExecutionKernelError:
                    mismatches.append(_mismatch(
                        event_id, ticker, "cancel_timestamp_missing",
                        "cancellation receipt lacks a valid local clock",
                    ))

        lifecycle_fill_rows: list[dict[str, Any]] = []
        for fill_id in row.get("official_fill_ids") or []:
            identity = str(fill_id)
            if identity in used_fills:
                mismatches.append(_mismatch(
                    event_id, ticker, "duplicate_fill_receipt",
                    "official fill belongs to more than one lifecycle",
                ))
                continue
            used_fills.add(identity)
            fill = fills.get(identity)
            if fill is None:
                mismatches.append(_mismatch(
                    event_id, ticker, "fill_receipt_missing",
                    "official fill identity is absent from complete export",
                ))
                continue
            lifecycle_fill_rows.append(fill)
            if fill["ticker"] != ticker:
                mismatches.append(_mismatch(
                    event_id, ticker, "fill_ticker_mismatch",
                    "official fill ticker differs from lifecycle",
                ))
            if fill["order_id"] not in accepted_ids:
                mismatches.append(_mismatch(
                    event_id, ticker, "fill_order_mismatch",
                    "official fill does not belong to a lifecycle order",
                ))
            if fill["action"] != "buy":
                mismatches.append(_mismatch(
                    event_id, ticker, "fill_action_mismatch",
                    "official entry fill is not a buy",
                ))

        lifecycle_fill_rows.sort(
            key=lambda value: (value["exchange_ts"], value["fill_id"])
        )
        quantity = sum(value["quantity"] for value in lifecycle_fill_rows)
        cost = sum(
            value["quantity"] * value["price_cents"]
            for value in lifecycle_fill_rows
        )
        vwap = cost / quantity if quantity > 0 else None
        first_ts = (
            lifecycle_fill_rows[0]["exchange_ts"]
            if lifecycle_fill_rows else None
        )
        cumulative = 0.0
        completion_ts = None
        for fill in lifecycle_fill_rows:
            cumulative += fill["quantity"]
            if cumulative >= LOT - 1e-9:
                completion_ts = fill["exchange_ts"]
                break

        if expected_status == "censored_unattributed_private_fill":
            replay_status = "censored_unattributed_private_fill"
        elif quantity > 0:
            replay_status = (
                "exact_filled_five"
                if math.isclose(quantity, LOT, abs_tol=1e-9)
                else "exact_filled_other_quantity"
            )
        else:
            closure_by_order = {
                str(value.get("order_id") or ""): value
                for value in row.get("closure_receipts") or []
            }
            all_closed = bool(found_orders) and all(
                _closed_order(
                    order,
                    closure_by_order.get(str(order.get("order_id") or "")),
                    cancellations_by_order.get(
                        str(order.get("order_id") or ""), []
                    ),
                )
                for order in found_orders
            )
            replay_status = (
                "exact_nonfill"
                if all_closed and not row.get("censor_reasons")
                else "censored"
            )

        if replay_status != expected_status:
            mismatches.append(_mismatch(
                event_id, ticker, "lifecycle_status_mismatch",
                f"replayed {replay_status}; expected {expected_status}",
            ))
        if not math.isclose(
            quantity,
            number(row.get("official_fill_quantity") or 0),
            abs_tol=1e-9,
        ):
            mismatches.append(_mismatch(
                event_id, ticker, "fill_quantity_mismatch",
                "receipt quantities do not reproduce lifecycle quantity",
            ))
        expected_vwap = row.get("official_fill_vwap_cents")
        if expected_vwap is None:
            vwap_matches = vwap is None
        else:
            vwap_matches = vwap is not None and math.isclose(
                vwap, number(expected_vwap), abs_tol=1e-9
            )
        if not vwap_matches:
            mismatches.append(_mismatch(
                event_id, ticker, "fill_vwap_mismatch",
                "receipt prices do not reproduce lifecycle VWAP",
            ))
        for name, replayed, expected in (
            ("first_fill_timestamp", first_ts,
             row.get("first_fill_exchange_ts")),
            ("completion_timestamp", completion_ts,
             row.get("completion_exchange_ts")),
        ):
            expected_ts = (
                None if expected in (None, "") else parse_ts(expected)
            )
            if (
                (replayed is None) != (expected_ts is None)
                or (
                    replayed is not None
                    and expected_ts is not None
                    and not math.isclose(
                        replayed, expected_ts, abs_tol=1e-6
                    )
                )
            ):
                mismatches.append(_mismatch(
                    event_id, ticker, name + "_mismatch",
                    "exchange fill clocks do not reproduce lifecycle",
                ))

        lifecycle_by_ticker[ticker].append({
            "status": replay_status,
            "quantity": quantity,
            "vwap": vwap,
            "accepted_order_count": len(found_orders),
            "missing_accepted_order_count": (
                len(accepted_ids) - len(found_orders)
            ),
            "failed_attempt_count": len(failed_rows),
        })

    decision_by_ticker: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    decision_ids: set[str] = set()
    for decision in causal_decisions:
        event_id = str(decision.get("event_id") or "")
        ticker = str(decision.get("ticker") or "")
        identity = str(decision.get("decision_id") or "")
        if not identity or identity in decision_ids:
            mismatches.append(_mismatch(
                event_id, ticker, "duplicate_decision_receipt",
                "causal nonplacement receipt identity is invalid",
            ))
            continue
        decision_ids.add(identity)
        if ticker not in required_tickers:
            mismatches.append(_mismatch(
                event_id, ticker, "decision_outside_D",
                "causal nonplacement receipt is outside D",
            ))
            continue
        try:
            parse_ts(
                decision.get("exchange_ts")
                or decision.get("local_logged_ts")
            )
        except ExecutionKernelError:
            mismatches.append(_mismatch(
                event_id, ticker, "decision_timestamp_missing",
                "causal nonplacement lacks a usable clock",
            ))
        decision_by_ticker[ticker].append(decision)

    expected_by_ticker = {
        str(row.get("ticker") or ""): row for row in expected_legs
    }
    if set(expected_by_ticker) != required_tickers:
        raise ExecutionKernelError(
            "expected event/leg ledger does not equal the D ticker set"
        )

    replay_legs: list[dict[str, Any]] = []
    leg_mismatch_types: dict[str, set[str]] = defaultdict(set)
    for mismatch in mismatches:
        leg_mismatch_types[mismatch["ticker"]].add(
            mismatch["mismatch_type"]
        )
    for ticker in sorted(required_tickers):
        event = ticker_to_event[ticker]
        rows = lifecycle_by_ticker.get(ticker, [])
        attributable = [
            row for row in rows
            if row["status"] != "censored_unattributed_private_fill"
        ]
        unattributed = [
            row for row in rows
            if row["status"] == "censored_unattributed_private_fill"
        ]
        quantity = sum(row["quantity"] for row in attributable)
        cost = sum(
            row["quantity"] * row["vwap"]
            for row in attributable if row["vwap"] is not None
        )
        vwap = cost / quantity if quantity > 0 else None
        if unattributed:
            status = "censored"
        elif math.isclose(quantity, LOT, abs_tol=1e-9):
            status = "exact_filled_five"
        elif quantity > 0:
            status = "exact_filled_other_quantity"
        elif rows and all(
            row["status"] == "exact_nonfill" for row in rows
        ):
            status = "exact_nonfill"
        elif not rows and decision_by_ticker.get(ticker):
            status = "exact_nonfill"
        else:
            status = "censored"
        expected = expected_by_ticker[ticker]
        expected_status = str(expected.get("status") or "")
        if status != expected_status:
            mismatch = _mismatch(
                str(event["event_id"]), ticker, "leg_status_mismatch",
                f"replayed {status}; expected {expected_status}",
            )
            mismatches.append(mismatch)
            leg_mismatch_types[ticker].add(mismatch["mismatch_type"])
        expected_quantity = number(
            expected.get("official_fill_quantity") or 0
        )
        if not math.isclose(quantity, expected_quantity, abs_tol=1e-9):
            mismatch = _mismatch(
                str(event["event_id"]), ticker, "leg_quantity_mismatch",
                "replayed leg quantity differs from frozen ledger",
            )
            mismatches.append(mismatch)
            leg_mismatch_types[ticker].add(mismatch["mismatch_type"])
        expected_vwap = expected.get("official_fill_vwap_cents")
        vwap_matches = (
            (expected_vwap is None and vwap is None)
            or (
                expected_vwap is not None
                and vwap is not None
                and math.isclose(
                    vwap, number(expected_vwap), abs_tol=1e-9
                )
            )
        )
        if not vwap_matches:
            mismatch = _mismatch(
                str(event["event_id"]), ticker, "leg_vwap_mismatch",
                "replayed leg VWAP differs from frozen ledger",
            )
            mismatches.append(mismatch)
            leg_mismatch_types[ticker].add(mismatch["mismatch_type"])
        replay_legs.append({
            "schema_version": VERSION,
            "event_id": str(event["event_id"]),
            "event_date": str(event["event_date"]),
            "category": str(event["category"]),
            "ticker": ticker,
            "replayed_status": status,
            "expected_status": expected_status,
            "official_fill_quantity": quantity,
            "official_fill_vwap_cents": vwap,
            "lifecycle_count": len(rows),
            "causal_nonplacement_receipt_count": len(
                decision_by_ticker.get(ticker, [])
            ),
            "match": not leg_mismatch_types[ticker],
            "mismatch_types": sorted(leg_mismatch_types[ticker]),
            "private_identifiers_included": False,
        })

    leg_status_counts = Counter(
        row["replayed_status"] for row in replay_legs
    )
    by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in replay_legs:
        by_event[row["event_id"]].append(row)
    dual_complete = [
        rows for rows in by_event.values()
        if len(rows) == 2 and all(
            row["replayed_status"] == "exact_filled_five"
            for row in rows
        )
    ]
    dual_under_par = sum(
        sum(number(row["official_fill_vwap_cents"]) for row in rows)
        < 100.0
        for rows in dual_complete
    )
    stats = {
        "kernel_version": VERSION,
        "D": len(event_by_id),
        "required_legs": len(required_tickers),
        "lifecycle_rows": len(private_lifecycles),
        "causal_nonplacement_receipts": len(decision_ids),
        "receipt_grain": {
            "relevant_accepted_placements": len(used_orders),
            "attributable_accepted_placements": sum(
                row["accepted_order_count"]
                for rows in lifecycle_by_ticker.values() for row in rows
            ),
            "legitimately_missing_unattributed_placements": sum(
                row["missing_accepted_order_count"]
                for rows in lifecycle_by_ticker.values() for row in rows
            ),
            "relevant_failed_attempts": used_failed_attempts,
            "placement_prices_validated": placement_price_rows,
            "placement_quantities_validated": placement_quantity_rows,
            "placement_local_timestamps_validated": (
                placements_with_local_ts
            ),
            "placement_exchange_timestamps_available": (
                placements_with_exchange_ts
            ),
            "cancellation_receipts": cancellation_receipt_rows,
            "successful_cancellation_receipts": (
                cancellation_success_rows
            ),
            "official_fill_receipts": len(used_fills),
            "official_fill_export_rows": len(fills),
            "duplicate_order_memberships": (
                sum(
                    value - 1
                    for value in Counter(
                        order_id
                        for row in private_lifecycles
                        for order_id in row.get("accepted_order_ids") or []
                    ).values()
                )
            ),
            "duplicate_fill_memberships": (
                sum(
                    value - 1
                    for value in Counter(
                        fill_id
                        for row in private_lifecycles
                        for fill_id in row.get("official_fill_ids") or []
                    ).values()
                )
            ),
            "duplicate_cancel_receipts": (
                cancellation_receipt_rows
                - len(cancel_receipt_signatures)
            ),
            "zero_size_fill_promotions": 0,
        },
        "leg_status_counts": dict(sorted(leg_status_counts.items())),
        "completed_dual_exact_five_events": len(dual_complete),
        "completed_dual_combined_cost_under_par": dual_under_par,
        "mismatch_count": len(mismatches),
        "mismatch_types": dict(sorted(Counter(
            row["mismatch_type"] for row in mismatches
        ).items())),
        "schedule_fields_consumed": False,
    }
    return replay_legs, mismatches, stats
