#!/usr/bin/env python3
"""Sequence-honest evaluation-only Window-1-close reference adapter."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from window1_range_attack_guarded_fill_adapter_v2 import exact_integer
from window1_range_attack_reference_adapter_v1 import (
    DEVELOPMENT_DATES,
    SEALED_HOLDOUT_DATES,
    ReferenceError,
    guarded_cutoff,
    parse_timestamp,
)


VERSION = "window1-range-attack-reference-adapter-v2"
AMBIGUOUS_REASON = (
    "ambiguous_latest_timestamp_multiple_prices_no_authoritative_sequence"
)


def _identity(value: Any, field: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ReferenceError(f"{field} is missing")
    return result


def _finite_positive(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceError(f"{field} is not numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ReferenceError(f"{field} is not finite")
    if result <= 0:
        raise ReferenceError(f"{field} is not positive")
    return result


def _exact_price(value: Any, field: str) -> int:
    try:
        return exact_integer(value, field, minimum=1, maximum=99)
    except RuntimeError as exc:
        raise ReferenceError(str(exc)) from exc


@dataclass(frozen=True)
class Window1CloseReferenceV2:
    event_id: str
    event_date: str
    leg_id: str
    ticker: str
    available: bool
    window1_close_cents: int | None
    reference_ts: float | None
    reference_receipt: str | None
    reference_supporting_receipts: tuple[str, ...]
    reference_source: str
    t8_floor_ts: float
    guarded_cutoff_ts: float | None
    boundary_source_class: str
    boundary_guard_id: str | None
    reason: str | None
    latest_timestamp_tie_count: int
    latest_timestamp_distinct_prices: tuple[int, ...]
    authoritative_sequence_available: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _deduplicated_true_prints(
    rows: Iterable[Mapping[str, Any]],
    *,
    ticker: str,
) -> list[dict[str, Any]]:
    by_receipt: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_ticker = str(row.get("ticker") or ticker)
        if row_ticker != ticker:
            continue
        receipt = _identity(
            row.get("trade_id") or row.get("receipt_id"),
            "true-print receipt",
        )
        size = _finite_positive(row.get("size"), "true-print size")
        if row.get("synthetic_transition") is True:
            continue
        if row.get("self_evidence") is True or row.get("own_order") is True:
            continue
        normalized = {
            "receipt": receipt,
            "ts": parse_timestamp(row.get("ts"), "true-print timestamp"),
            "price": _exact_price(row.get("price"), "true-print price"),
            "size": size,
        }
        prior = by_receipt.get(receipt)
        if prior is not None and prior != normalized:
            raise ReferenceError("conflicting duplicate true-print receipt")
        by_receipt[receipt] = normalized
    return list(by_receipt.values())


def derive_window1_close_reference(
    *,
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    boundary: Mapping[str, Any],
    true_prints: Iterable[Mapping[str, Any]],
) -> Window1CloseReferenceV2:
    """Derive a close without receipt UUID, price, or volume tie-breaking."""
    event_id = _identity(event.get("event_id"), "event id")
    event_date = _identity(event.get("event_date"), "event date")
    leg_id = _identity(leg.get("leg_id") or leg.get("leg"), "leg id")
    ticker = _identity(leg.get("ticker"), "ticker")
    if event_date in SEALED_HOLDOUT_DATES:
        raise ReferenceError("July 24-26 holdout input refused")
    if event_date not in DEVELOPMENT_DATES:
        raise ReferenceError("non-development date refused")
    if str(boundary.get("event_id") or "") != event_id:
        raise ReferenceError("boundary/event identity mismatch")
    scheduled = parse_timestamp(
        event.get("scheduled_start_exchange_ts"), "scheduled start"
    )
    t8_floor = scheduled - 8 * 60 * 60
    cutoff = guarded_cutoff(boundary)
    source = "frozen_guarded_cache_v3_true_prints_evaluation_only"

    def unavailable(reason: str) -> Window1CloseReferenceV2:
        return Window1CloseReferenceV2(
            event_id=event_id,
            event_date=event_date,
            leg_id=leg_id,
            ticker=ticker,
            available=False,
            window1_close_cents=None,
            reference_ts=None,
            reference_receipt=None,
            reference_supporting_receipts=(),
            reference_source=source,
            t8_floor_ts=t8_floor,
            guarded_cutoff_ts=cutoff.get("cutoff_ts"),
            boundary_source_class=cutoff["source_class"],
            boundary_guard_id=cutoff.get("guard_id"),
            reason=reason,
            latest_timestamp_tie_count=0,
            latest_timestamp_distinct_prices=(),
            authoritative_sequence_available=False,
        )

    if cutoff["status"] != "positive":
        return unavailable(
            "contradictory_boundary"
            if cutoff["status"] == "contradictory"
            else "boundary_not_positive"
        )
    eligible = [
        row for row in _deduplicated_true_prints(true_prints, ticker=ticker)
        if t8_floor <= row["ts"] <= float(cutoff["cutoff_ts"])
    ]
    if not eligible:
        return unavailable("window1_close_reference_missing")
    latest_ts = max(row["ts"] for row in eligible)
    latest = [
        row for row in eligible if row["ts"] == latest_ts
    ]
    prices = tuple(sorted({int(row["price"]) for row in latest}))
    receipts = tuple(sorted(str(row["receipt"]) for row in latest))
    if len(prices) != 1:
        value = unavailable(AMBIGUOUS_REASON)
        return Window1CloseReferenceV2(
            **{
                **asdict(value),
                "reference_ts": latest_ts,
                "reference_supporting_receipts": receipts,
                "latest_timestamp_tie_count": len(latest),
                "latest_timestamp_distinct_prices": prices,
            }
        )
    return Window1CloseReferenceV2(
        event_id=event_id,
        event_date=event_date,
        leg_id=leg_id,
        ticker=ticker,
        available=True,
        window1_close_cents=prices[0],
        reference_ts=latest_ts,
        reference_receipt=receipts[0] if len(receipts) == 1 else None,
        reference_supporting_receipts=receipts,
        reference_source=source,
        t8_floor_ts=t8_floor,
        guarded_cutoff_ts=float(cutoff["cutoff_ts"]),
        boundary_source_class=cutoff["source_class"],
        boundary_guard_id=cutoff.get("guard_id"),
        reason=None,
        latest_timestamp_tie_count=len(latest),
        latest_timestamp_distinct_prices=prices,
        authoritative_sequence_available=False,
    )
