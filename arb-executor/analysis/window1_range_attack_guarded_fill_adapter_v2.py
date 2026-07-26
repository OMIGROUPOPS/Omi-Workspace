#!/usr/bin/env python3
"""Strict adapter for the frozen unique Range-Attack fill ledger.

Runtime scoring accepts only the construction-time UNIQUE_GUARDED_FILL_LEDGER.
Raw policy streams and raw interval-level fillability receipts are forbidden.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping


VERSION = "window1-range-attack-guarded-fill-adapter-v2"
UNIQUE_LEDGER_SCHEMA = "window1-range-attack-unique-guarded-fill-v2"
LOT = 5
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
POSITIVE_BOUNDARY_CLASSES = frozenset({
    "official_exact",
    "clean_causal_interval",
    "quantized_late_detection_proxy",
})
FORBIDDEN_RAW_SURFACES = frozenset({
    "causal_policy_fill_state_by_leg",
    "candidate_order_stream",
    "candidate_order_streams",
    "order_stream",
    "raw_causal_fill_state",
    "raw_policy_actions",
    "strict_ask_certain_fill_actions",
})


class GuardedFillError(RuntimeError):
    """Raised when fill accounting leaves the frozen guarded receipt law."""


def exact_integer(
    value: Any,
    field: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    """Accept an exact integer representation; never truncate.

    Integer-valued floats are accepted because JSON decoders may represent
    source numeric fields that way. Booleans, strings, fractional values and
    non-finite values are rejected.
    """
    if isinstance(value, bool):
        raise GuardedFillError(f"{field} is boolean")
    if isinstance(value, int):
        result = value
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise GuardedFillError(f"{field} is not finite")
        if not value.is_integer():
            raise GuardedFillError(f"{field} is not an exact integer")
        result = int(value)
    else:
        raise GuardedFillError(f"{field} is not an exact integer")
    if minimum is not None and result < minimum:
        raise GuardedFillError(f"{field} is below {minimum}")
    if maximum is not None and result > maximum:
        raise GuardedFillError(f"{field} is above {maximum}")
    return result


def finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise GuardedFillError(f"{field} is boolean")
    if not isinstance(value, (int, float)):
        raise GuardedFillError(f"{field} is not numeric")
    result = float(value)
    if not math.isfinite(result):
        raise GuardedFillError(f"{field} is not finite")
    return result


def _identity(value: Any, field: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise GuardedFillError(f"{field} is missing")
    return result


def _forbidden_keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) in FORBIDDEN_RAW_SURFACES:
                found.add(str(key))
            found.update(_forbidden_keys(child))
    elif isinstance(value, (list, tuple)):
        for child in value:
            found.update(_forbidden_keys(child))
    return found


@dataclass(frozen=True)
class GuardedFill:
    candidate_id: str
    event_id: str
    event_date: str
    category: str
    leg_id: str
    ticker: str
    order_interval_id: str
    evidence_type: str
    evidence_receipt: str
    evidence_timestamp: float
    exposed_price_cents: int
    accounting_fill_price_cents: int
    accounting_quantity: int
    evaluated_right_ts: float
    guarded_cutoff_ts: float
    boundary_source_class: str
    boundary_guard_id: str
    boundary_guard_seconds: int
    selector_receipt_sha256: str
    selection_basis: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def adapt_unique_fill_row(
    row: Mapping[str, Any],
    *,
    expected_candidates: set[str] | frozenset[str],
    expected_legs: Mapping[tuple[str, str], str],
) -> GuardedFill:
    """Adapt exactly one construction-frozen unique guarded fill."""
    forbidden = sorted(_forbidden_keys(row))
    if forbidden:
        raise GuardedFillError(
            "raw causal-state input is forbidden: " + ",".join(forbidden)
        )
    if row.get("schema_version") != UNIQUE_LEDGER_SCHEMA:
        raise GuardedFillError("runtime input is not the unique fill ledger")
    if row.get("FILLABLE_AT_X") is not True:
        raise GuardedFillError("unique ledger contains a non-fillable row")
    if row.get("scored") is not False or row.get("metrics") is not None:
        raise GuardedFillError("unique fill ledger is not score-free")

    candidate_id = _identity(row.get("candidate_id"), "candidate_id")
    event_id = _identity(row.get("event_id"), "event_id")
    event_date = _identity(row.get("event_date"), "event_date")
    leg_id = _identity(row.get("leg_id"), "leg_id")
    ticker = _identity(row.get("ticker"), "ticker")
    if candidate_id not in expected_candidates:
        raise GuardedFillError("candidate is outside the frozen allowlist")
    if event_date in SEALED_HOLDOUT_DATES:
        raise GuardedFillError("July 24-26 holdout input refused")
    if event_date not in DEVELOPMENT_DATES:
        raise GuardedFillError("non-development date refused")
    if expected_legs.get((event_id, leg_id)) != ticker:
        raise GuardedFillError("unknown event or leg identity")

    boundary = row.get("boundary")
    if not isinstance(boundary, Mapping):
        raise GuardedFillError("fillable row lacks boundary provenance")
    if boundary.get("positive_window1_provable") is not True:
        raise GuardedFillError("unprovable or censored boundary refused")
    if boundary.get("schedule_can_prove_positive") is not False:
        raise GuardedFillError("schedule evidence cannot prove positive fill")
    source_class = _identity(
        boundary.get("start_source_class"), "boundary source class"
    )
    if source_class not in POSITIVE_BOUNDARY_CLASSES:
        raise GuardedFillError("unsupported positive boundary class")
    if str(boundary.get("event_id") or event_id) != event_id:
        raise GuardedFillError("boundary event identity mismatch")

    evidence_type = _identity(
        row.get("FILLABLE_AT_X_evidence_type"), "fill evidence type"
    )
    if evidence_type not in SUPPORTED_EVIDENCE:
        raise GuardedFillError("unsupported fill evidence type")
    evidence = row.get("FILLABLE_AT_X_evidence")
    if not isinstance(evidence, Mapping):
        raise GuardedFillError("fillable row lacks evidence object")
    evidence_receipt = _identity(
        evidence.get("receipt"), "fill evidence receipt"
    )
    evidence_ts = finite_number(
        evidence.get("ts"), "fill evidence timestamp"
    )
    opened_ts = finite_number(row.get("opened_ts"), "order opened timestamp")
    evaluated_right = finite_number(
        row.get("evaluated_right_ts"), "evaluated right timestamp"
    )
    guarded_cutoff = finite_number(
        boundary.get("guarded_cutoff_ts"), "guarded cutoff timestamp"
    )
    if evidence_ts < opened_ts:
        raise GuardedFillError("evidence precedes the exposed interval")
    if evidence_ts > evaluated_right + 1e-6:
        raise GuardedFillError("fill evidence is after evaluated right")
    if evidence_ts > guarded_cutoff + 1e-6:
        raise GuardedFillError("fill evidence is after guarded cutoff")

    target = exact_integer(
        row.get("target_price_cents"), "target price",
        minimum=1, maximum=99,
    )
    fill_price = exact_integer(
        row.get("accounting_fill_price_if_later_scored"),
        "accounting fill price", minimum=1, maximum=99,
    )
    quantity = exact_integer(
        row.get("accounting_quantity_if_later_scored"),
        "accounting quantity", minimum=LOT, maximum=LOT,
    )
    if fill_price != target:
        raise GuardedFillError("target/fill-price mismatch")
    if row.get("primary_price_fillability_assigns_five") is not True:
        raise GuardedFillError("fillable row lacks five-share accounting flag")

    if evidence_type == "PRICE_REACHED":
        if row.get("PRICE_REACHED") is not True:
            raise GuardedFillError("print evidence lacks PRICE_REACHED truth")
        price = exact_integer(
            evidence.get("price"), "print evidence price",
            minimum=1, maximum=99,
        )
        size = finite_number(evidence.get("size"), "print evidence size")
        if price > target or size <= 0:
            raise GuardedFillError("print is not positive-size at/below X")
    else:
        if row.get("STRICT_ASK_CERTAIN_FILL") is not True:
            raise GuardedFillError(
                "strict-ask evidence lacks strict-ask truth"
            )
        ask = exact_integer(
            evidence.get("external_ask_price_cents"),
            "strict external ask", minimum=1, maximum=99,
        )
        evidence_target = exact_integer(
            evidence.get("target_price_cents"),
            "strict-ask evidence target", minimum=1, maximum=99,
        )
        if evidence_target != target or ask >= target:
            raise GuardedFillError("strict ask is not strictly below X")

    selector = row.get("unique_selection_receipt")
    if not isinstance(selector, Mapping):
        raise GuardedFillError("unique selection receipt is missing")
    selector_hash = _identity(
        selector.get("selector_receipt_sha256"),
        "selector receipt SHA-256",
    )
    if len(selector_hash) != 64 or any(
        char not in "0123456789abcdef" for char in selector_hash.lower()
    ):
        raise GuardedFillError("selector receipt SHA-256 is invalid")

    return GuardedFill(
        candidate_id=candidate_id,
        event_id=event_id,
        event_date=event_date,
        category=str(row.get("category") or ""),
        leg_id=leg_id,
        ticker=ticker,
        order_interval_id=_identity(
            row.get("order_interval_id"), "order interval identity"
        ),
        evidence_type=evidence_type,
        evidence_receipt=evidence_receipt,
        evidence_timestamp=evidence_ts,
        exposed_price_cents=target,
        accounting_fill_price_cents=fill_price,
        accounting_quantity=quantity,
        evaluated_right_ts=evaluated_right,
        guarded_cutoff_ts=guarded_cutoff,
        boundary_source_class=source_class,
        boundary_guard_id=_identity(
            boundary.get("guard_id"), "boundary guard id"
        ),
        boundary_guard_seconds=exact_integer(
            boundary.get("guard_seconds"), "boundary guard seconds",
            minimum=0,
        ),
        selector_receipt_sha256=selector_hash,
        selection_basis=_identity(
            selector.get("selection_basis"), "selection basis"
        ),
    )


def adapt_unique_fill_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    expected_candidates: set[str] | frozenset[str],
    expected_legs: Mapping[tuple[str, str], str],
) -> dict[tuple[str, str, str], GuardedFill]:
    """Adapt the frozen unique ledger and reject duplicate leg credit."""
    fills: dict[tuple[str, str, str], GuardedFill] = {}
    evidence_identities: set[tuple[str, str, str, str]] = set()
    for row in rows:
        fill = adapt_unique_fill_row(
            row,
            expected_candidates=expected_candidates,
            expected_legs=expected_legs,
        )
        key = (fill.candidate_id, fill.event_id, fill.leg_id)
        if key in fills:
            raise GuardedFillError(
                "multiple unique-ledger fills for one candidate/event/leg"
            )
        evidence_key = (*key, fill.evidence_receipt)
        if evidence_key in evidence_identities:
            raise GuardedFillError(
                "duplicate fill evidence cannot inflate quantity"
            )
        evidence_identities.add(evidence_key)
        fills[key] = fill
    return fills

