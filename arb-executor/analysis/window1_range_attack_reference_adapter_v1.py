#!/usr/bin/env python3
"""Evaluation-only Window-1-close reference adapter for Range-Attack."""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping


VERSION = "window1-range-attack-reference-adapter-v1"
DEVELOPMENT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(12, 21)
)
SEALED_HOLDOUT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(24, 27)
)
POSITIVE_CLASSES = frozenset({
    "official_exact",
    "clean_causal_interval",
    "quantized_late_detection_proxy",
})
NONPOSITIVE_CLASSES = frozenset({
    "schedule_only",
    "live_by_only",
    "contradictory",
})


class ReferenceError(RuntimeError):
    """Raised when reference evidence violates the frozen metric contract."""


def parse_timestamp(value: Any, field: str = "timestamp") -> float:
    if isinstance(value, bool):
        raise ReferenceError(f"{field} is boolean")
    if isinstance(value, (int, float)):
        result = float(value)
    elif isinstance(value, str) and value.strip():
        try:
            result = dt.datetime.fromisoformat(
                value.replace("Z", "+00:00")
            ).timestamp()
        except ValueError as exc:
            raise ReferenceError(f"{field} is invalid") from exc
    else:
        raise ReferenceError(f"{field} is missing")
    if not math.isfinite(result):
        raise ReferenceError(f"{field} is not finite")
    return result


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ReferenceError(f"{field} is boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ReferenceError(f"{field} is not numeric") from exc
    if not math.isfinite(result):
        raise ReferenceError(f"{field} is not finite")
    return result


def _identity(value: Any, field: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ReferenceError(f"{field} is missing")
    return result


def _same(left: float, right: float) -> bool:
    return abs(float(left) - float(right)) <= 1e-6


def guarded_cutoff(boundary: Mapping[str, Any]) -> dict[str, Any]:
    """Derive the authoritative V5 cutoff without a realized-start oracle."""
    source_class = _identity(
        boundary.get("start_source_class"), "start source class"
    )
    event_id = _identity(boundary.get("event_id"), "boundary event id")
    if source_class in NONPOSITIVE_CLASSES:
        if source_class == "contradictory":
            return {
                "event_id": event_id,
                "status": "contradictory",
                "source_class": source_class,
                "cutoff_ts": None,
                "guard_id": None,
                "guard_seconds": None,
            }
        if boundary.get("positive_window1_provable") is not False:
            raise ReferenceError(
                f"{source_class} cannot prove a positive boundary"
            )
        return {
            "event_id": event_id,
            "status": "censored",
            "source_class": source_class,
            "cutoff_ts": None,
            "guard_id": None,
            "guard_seconds": None,
        }
    if source_class not in POSITIVE_CLASSES:
        raise ReferenceError("unknown V5 start source class")
    if boundary.get("positive_window1_provable") is not True:
        if not str(boundary.get("guard_censor_reason") or "").strip():
            raise ReferenceError("unprovable boundary lacks named censor")
        return {
            "event_id": event_id,
            "status": "censored",
            "source_class": source_class,
            "cutoff_ts": None,
            "guard_id": None,
            "guard_seconds": None,
            "censor_reason": str(boundary["guard_censor_reason"]),
        }
    guard = boundary.get("guard_band")
    if not isinstance(guard, Mapping):
        raise ReferenceError("positive boundary lacks V5 guard artifact")
    guard_id = _identity(guard.get("guard_id"), "guard id")
    seconds = _finite(
        guard.get("positive_guard_seconds"), "positive guard seconds"
    )
    if source_class == "official_exact":
        expected_id = "official-point-strict-60s-v1"
        expected_seconds = 60.0
        anchor = parse_timestamp(
            boundary.get("exact_start_utc"), "exact start"
        )
    elif source_class == "clean_causal_interval":
        expected_id = "causal-interval-strict-60s-v1"
        expected_seconds = 60.0
        interval = boundary.get("start_interval_utc")
        if not isinstance(interval, Mapping):
            raise ReferenceError("clean interval lacks lower bound")
        anchor = parse_timestamp(
            interval.get("lower_inclusive"), "interval lower bound"
        )
    else:
        expected_id = "te-calibration-central-93pct-asymmetric-v1"
        expected_seconds = 900.0
        anchor = parse_timestamp(
            boundary.get("proxy_clock_utc"), "proxy clock"
        )
        if not _same(
            _finite(
                guard.get("negative_guard_seconds"),
                "proxy negative guard",
            ),
            600.0,
        ):
            raise ReferenceError("proxy asymmetric guard changed")
    if guard_id != expected_id or not _same(seconds, expected_seconds):
        raise ReferenceError("V5 positive guard changed")
    cutoff = anchor - seconds
    if source_class == "quantized_late_detection_proxy":
        committed = parse_timestamp(
            guard.get("strict_window1_completion_lte_utc"),
            "committed proxy cutoff",
        )
        if not _same(cutoff, committed):
            raise ReferenceError("proxy guard directionality changed")
    return {
        "event_id": event_id,
        "status": "positive",
        "source_class": source_class,
        "cutoff_ts": cutoff,
        "cutoff_utc": dt.datetime.fromtimestamp(
            cutoff, tz=dt.timezone.utc
        ).isoformat(),
        "guard_id": guard_id,
        "guard_seconds": int(seconds),
        "direction": "anchor_minus_positive_guard",
    }


@dataclass(frozen=True)
class Window1CloseReference:
    event_id: str
    event_date: str
    leg_id: str
    ticker: str
    available: bool
    window1_close_cents: int | None
    reference_ts: float | None
    reference_receipt: str | None
    reference_source: str
    t8_floor_ts: float
    guarded_cutoff_ts: float | None
    boundary_source_class: str
    boundary_guard_id: str | None
    reason: str | None

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
        size = _finite(row.get("size"), "true-print size")
        if size <= 0:
            continue
        if row.get("synthetic_transition") is True:
            continue
        if row.get("self_evidence") is True or row.get("own_order") is True:
            continue
        normalized = {
            "receipt": receipt,
            "ts": parse_timestamp(row.get("ts"), "true-print timestamp"),
            "price": int(_finite(row.get("price"), "true-print price")),
            "size": size,
        }
        prior = by_receipt.get(receipt)
        if prior is not None and prior != normalized:
            raise ReferenceError("conflicting duplicate true-print receipt")
        by_receipt[receipt] = normalized
    return sorted(
        by_receipt.values(),
        key=lambda row: (row["ts"], row["receipt"]),
    )

def derive_window1_close_reference(
    *,
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    boundary: Mapping[str, Any],
    true_prints: Iterable[Mapping[str, Any]],
) -> Window1CloseReference:
    """Derive one evaluation-only reference from frozen public prints."""
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
    if cutoff["status"] != "positive":
        return Window1CloseReference(
            event_id=event_id,
            event_date=event_date,
            leg_id=leg_id,
            ticker=ticker,
            available=False,
            window1_close_cents=None,
            reference_ts=None,
            reference_receipt=None,
            reference_source=(
                "frozen_guarded_cache_v3_true_prints_evaluation_only"
            ),
            t8_floor_ts=t8_floor,
            guarded_cutoff_ts=None,
            boundary_source_class=cutoff["source_class"],
            boundary_guard_id=None,
            reason=f"boundary_{cutoff['status']}",
        )
    cutoff_ts = float(cutoff["cutoff_ts"])
    admitted = [
        row for row in _deduplicated_true_prints(
            true_prints, ticker=ticker
        )
        if t8_floor <= float(row["ts"]) <= cutoff_ts
    ]
    if not admitted:
        return Window1CloseReference(
            event_id=event_id,
            event_date=event_date,
            leg_id=leg_id,
            ticker=ticker,
            available=False,
            window1_close_cents=None,
            reference_ts=None,
            reference_receipt=None,
            reference_source=(
                "frozen_guarded_cache_v3_true_prints_evaluation_only"
            ),
            t8_floor_ts=t8_floor,
            guarded_cutoff_ts=cutoff_ts,
            boundary_source_class=cutoff["source_class"],
            boundary_guard_id=cutoff["guard_id"],
            reason="no_positive_true_print_between_T8h_and_guarded_cutoff",
        )
    chosen = admitted[-1]
    return Window1CloseReference(
        event_id=event_id,
        event_date=event_date,
        leg_id=leg_id,
        ticker=ticker,
        available=True,
        window1_close_cents=int(chosen["price"]),
        reference_ts=float(chosen["ts"]),
        reference_receipt=str(chosen["receipt"]),
        reference_source=(
            "last_exchange_identified_deduplicated_positive_true_print_"
            "between_T8h_and_guarded_cutoff"
        ),
        t8_floor_ts=t8_floor,
        guarded_cutoff_ts=cutoff_ts,
        boundary_source_class=cutoff["source_class"],
        boundary_guard_id=cutoff["guard_id"],
        reason=None,
    )
