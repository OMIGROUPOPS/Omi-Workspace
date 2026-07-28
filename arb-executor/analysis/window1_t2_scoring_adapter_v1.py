#!/usr/bin/env python3
"""Exact-integer adapter for the frozen T2 unique credited-fill ledger."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from window1_range_attack_guarded_fill_adapter_v2 import (
    GuardedFill,
    GuardedFillError,
    exact_integer,
    finite_number,
)


VERSION = "window1-t2-scoring-adapter-v1"
SCHEMA = "window1-t2-unique-credited-fill-v1"
LOT = 5
FEE_CENTS = 0
DEVELOPMENT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(12, 21)
)
SEALED_HOLDOUT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(24, 27)
)
SUPPORTED_EVIDENCE = frozenset({
    "PRICE_REACHED",
    "STRICT_ASK_CERTAIN_FILL",
})
FORBIDDEN_RAW_KEYS = frozenset({
    "causal_policy_fill_state_by_leg",
    "order_intervals_by_leg",
    "order_stream",
    "raw_policy_actions",
    "strict_ask_certain_fill_actions",
})


class T2ScoringAdapterError(RuntimeError):
    """A T2 fill row left the frozen exact-integer guarded contract."""


def _identity(value: Any, field: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise T2ScoringAdapterError(f"{field} is missing")
    return result


def _exact(
    value: Any,
    field: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    try:
        return exact_integer(
            value, field, minimum=minimum, maximum=maximum
        )
    except GuardedFillError as exc:
        raise T2ScoringAdapterError(str(exc)) from exc


def _finite(value: Any, field: str) -> float:
    try:
        return finite_number(value, field)
    except GuardedFillError as exc:
        raise T2ScoringAdapterError(str(exc)) from exc


def _optional_exact(value: Any, field: str) -> int | None:
    return None if value is None else _exact(value, field)


def _contains_forbidden(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) in FORBIDDEN_RAW_KEYS:
                found.add(str(key))
            found.update(_contains_forbidden(child))
    elif isinstance(value, (list, tuple)):
        for child in value:
            found.update(_contains_forbidden(child))
    return found


@dataclass(frozen=True)
class T2CreditedFill(GuardedFill):
    base_candidate_id: str
    fill_role: str
    action_authority: str
    action_timestamp: float
    action_trigger_receipt: str
    fill_receipt: str
    fill_book_receipt: str
    first_filled_leg: str | None
    first_fill_timestamp: float | None
    realized_first_leg_d1_cents: int | None
    b2_max_cents: int | None
    sibling_d2_cents: int | None
    strict_combined_budget_passed: bool | None
    source_stream_sha256: str
    self_trigger_fill: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def adapt_t2_unique_fill_row(
    row: Mapping[str, Any],
    *,
    expected_candidates: set[str] | frozenset[str],
    expected_legs: Mapping[tuple[str, str], str],
) -> T2CreditedFill:
    forbidden = _contains_forbidden(row)
    if forbidden:
        raise T2ScoringAdapterError(
            "raw T2 causal state is forbidden: " + ",".join(sorted(forbidden))
        )
    if row.get("schema_version") != SCHEMA:
        raise T2ScoringAdapterError("wrong T2 unique-fill schema")
    if (
        row.get("lawful_guarded_credited_fill") is not True
        or row.get("scored") is not False
        or row.get("metrics") is not None
        or row.get("performance") is not None
    ):
        raise T2ScoringAdapterError("T2 fill row is not score-free/admissible")

    candidate = _identity(row.get("candidate_id"), "candidate id")
    event = _identity(row.get("event_id"), "event id")
    date = _identity(row.get("event_date"), "event date")
    leg = _identity(row.get("leg_id"), "leg id")
    ticker = _identity(row.get("ticker"), "ticker")
    if candidate not in expected_candidates:
        raise T2ScoringAdapterError("candidate outside frozen T2 allowlist")
    if date in SEALED_HOLDOUT_DATES:
        raise T2ScoringAdapterError("sealed July 24-26 input refused")
    if date not in DEVELOPMENT_DATES:
        raise T2ScoringAdapterError("non-development date refused")
    if expected_legs.get((event, leg)) != ticker:
        raise T2ScoringAdapterError("unknown event/leg/ticker identity")

    quantity = _exact(row.get("quantity"), "quantity", LOT, LOT)
    exposed = _exact(row.get("exposed_X_cents"), "exposed X", 1, 99)
    fill_price = _exact(row.get("fill_price_cents"), "fill price", 1, 99)
    if exposed != fill_price:
        raise T2ScoringAdapterError("fill price differs from exposed X")
    evidence_type = _identity(
        row.get("fill_evidence_type"), "fill evidence type"
    )
    if evidence_type not in SUPPORTED_EVIDENCE:
        raise T2ScoringAdapterError("unsupported fill evidence type")
    evidence = row.get("fill_evidence")
    if not isinstance(evidence, Mapping):
        raise T2ScoringAdapterError("fill evidence is missing")
    evidence_ts = _finite(
        row.get("evidence_timestamp"), "evidence timestamp"
    )
    action_ts = _finite(row.get("action_timestamp"), "action timestamp")
    if evidence_ts < action_ts - 1e-6:
        raise T2ScoringAdapterError("fill precedes action")
    receipt = _identity(row.get("fill_receipt"), "fill receipt")
    trigger = _identity(
        row.get("action_trigger_receipt"), "action trigger receipt"
    )
    if receipt == trigger or row.get("self_trigger_fill") is not False:
        raise T2ScoringAdapterError("action trigger self-filled new exposure")

    if evidence_type == "PRICE_REACHED":
        if (
            _identity(evidence.get("print_receipt"), "print receipt")
            != receipt
            or _finite(evidence.get("print_timestamp"), "print timestamp")
            != evidence_ts
            or _exact(evidence.get("print_price_cents"), "print price", 1, 99)
            > exposed
            or _finite(evidence.get("print_size"), "print size") <= 0
        ):
            raise T2ScoringAdapterError("invalid positive-size print fill")
    else:
        if (
            _identity(evidence.get("book_receipt"), "book receipt") != receipt
            or _finite(evidence.get("book_timestamp"), "book timestamp")
            != evidence_ts
            or _exact(
                evidence.get("external_ask_cents"), "external ask", 1, 99
            ) >= exposed
        ):
            raise T2ScoringAdapterError("invalid strict-ask fill")

    boundary = row.get("boundary")
    if not isinstance(boundary, Mapping):
        raise T2ScoringAdapterError("boundary receipt missing")
    if (
        boundary.get("positive_window1_provable") is not True
        or boundary.get("schedule_can_prove_positive") is not False
    ):
        raise T2ScoringAdapterError("boundary is not positively provable")
    cutoff = _finite(
        boundary.get("guarded_cutoff_ts"), "guarded cutoff"
    )
    right = _finite(row.get("evaluated_right_ts"), "evaluated right")
    if evidence_ts > cutoff + 1e-6 or evidence_ts > right + 1e-6:
        raise T2ScoringAdapterError("post-right fill entered T2 ledger")

    role = _identity(row.get("fill_role"), "fill role")
    if role not in {"first_leg", "sibling"}:
        raise T2ScoringAdapterError("unknown fill role")
    first_leg = row.get("first_filled_leg")
    first_ts = row.get("first_fill_timestamp")
    d1 = _optional_exact(row.get("realized_first_leg_d1_cents"), "d1")
    b2 = _optional_exact(row.get("b2_max_cents"), "b2_max")
    d2 = _optional_exact(row.get("sibling_d2_cents"), "d2")
    strict = row.get("strict_combined_budget_passed")
    if role == "sibling":
        if first_leg is None or first_ts is None or d1 is None:
            raise T2ScoringAdapterError("sibling lacks first-fill state")
        first_ts = _finite(first_ts, "first-fill timestamp")
        if evidence_ts <= first_ts:
            raise T2ScoringAdapterError("sibling fill is not strictly later")
        if b2 != math.floor(-d1 - FEE_CENTS - 1):
            raise T2ScoringAdapterError("b2_max arithmetic changed")
        bid = _exact(
            evidence.get("action_external_bid_cents"),
            "action external bid", 1, 99,
        )
        if d2 != exposed - bid:
            raise T2ScoringAdapterError("sibling d2 differs from action BBO")
        expected = d1 + d2 + FEE_CENTS < 0
        if strict is not expected:
            raise T2ScoringAdapterError("strict combined budget inconsistent")
        if d2 > 0 and not expected:
            raise T2ScoringAdapterError("positive d2 violates pair budget")
    elif d2 is not None or strict is not None:
        raise T2ScoringAdapterError("first leg contains sibling budget fields")

    selector = _identity(
        row.get("selector_receipt_sha256"), "selector SHA-256"
    )
    source_hash = _identity(
        row.get("source_stream_sha256"), "source stream SHA-256"
    )
    for value, field in ((selector, "selector"), (source_hash, "source")):
        if len(value) != 64 or any(
            char not in "0123456789abcdef" for char in value.lower()
        ):
            raise T2ScoringAdapterError(f"{field} is not SHA-256")

    return T2CreditedFill(
        candidate_id=candidate,
        event_id=event,
        event_date=date,
        category=str(row.get("category") or ""),
        leg_id=leg,
        ticker=ticker,
        order_interval_id=_identity(
            row.get("exposure_interval_id"), "exposure interval"
        ),
        evidence_type=evidence_type,
        evidence_receipt=receipt,
        evidence_timestamp=evidence_ts,
        exposed_price_cents=exposed,
        accounting_fill_price_cents=fill_price,
        accounting_quantity=quantity,
        evaluated_right_ts=right,
        guarded_cutoff_ts=cutoff,
        boundary_source_class=_identity(
            boundary.get("start_source_class"), "boundary source class"
        ),
        boundary_guard_id=_identity(
            boundary.get("guard_id"), "boundary guard id"
        ),
        boundary_guard_seconds=_exact(
            boundary.get("guard_seconds"), "guard seconds", 0
        ),
        selector_receipt_sha256=selector,
        selection_basis=_identity(
            row.get("selection_basis"), "selection basis"
        ),
        base_candidate_id=_identity(
            row.get("base_candidate_id"), "base candidate"
        ),
        fill_role=role,
        action_authority=_identity(
            row.get("action_authority"), "action authority"
        ),
        action_timestamp=action_ts,
        action_trigger_receipt=trigger,
        fill_receipt=receipt,
        fill_book_receipt=_identity(
            row.get("fill_book_receipt"), "fill book receipt"
        ),
        first_filled_leg=(
            str(first_leg) if first_leg is not None else None
        ),
        first_fill_timestamp=(
            _finite(first_ts, "first-fill timestamp")
            if first_ts is not None else None
        ),
        realized_first_leg_d1_cents=d1,
        b2_max_cents=b2,
        sibling_d2_cents=d2,
        strict_combined_budget_passed=(
            bool(strict) if strict is not None else None
        ),
        source_stream_sha256=source_hash,
        self_trigger_fill=False,
    )


def adapt_t2_unique_fill_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    expected_candidates: set[str] | frozenset[str],
    expected_legs: Mapping[tuple[str, str], str],
) -> dict[tuple[str, str, str], T2CreditedFill]:
    result: dict[tuple[str, str, str], T2CreditedFill] = {}
    identities: dict[str, tuple[str, str, str]] = {}
    for row in rows:
        fill = adapt_t2_unique_fill_row(
            row,
            expected_candidates=expected_candidates,
            expected_legs=expected_legs,
        )
        key = (fill.candidate_id, fill.event_id, fill.leg_id)
        causal = _identity(
            row.get("causal_fill_identity"), "causal fill identity"
        )
        prior = result.get(key)
        if prior is not None:
            if prior == fill and identities.get(causal) == key:
                continue
            raise T2ScoringAdapterError(
                "conflicting multiple fills for candidate/event/leg"
            )
        if causal in identities:
            raise T2ScoringAdapterError("causal fill identity reused")
        result[key] = fill
        identities[causal] = key
    return result
