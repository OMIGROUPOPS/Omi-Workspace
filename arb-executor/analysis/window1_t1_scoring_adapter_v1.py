#!/usr/bin/env python3
"""T1 ledger adapter over the byte-identical audited Range-Attack V2 scorer.

This module does not define a metric.  It validates the construction-frozen
T1 unique credited-fill ledger, translates its identities into the exact
input objects accepted by the audited V2 scorer, and restores the T1
candidate identity on the scorer's output.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from window1_range_attack_guarded_fill_adapter_v2 import (
    GuardedFill,
    GuardedFillError,
    exact_integer,
    finite_number,
)
from window1_range_attack_scorer_v2 import (
    aggregate_candidate as audited_aggregate_candidate,
    score_event as audited_score_event,
)


VERSION = "window1-t1-scoring-adapter-v1"
SCHEMA = "window1-t1-unique-credited-fill-v1"
LOT = 5
TARGET_PC = 603
D_REQUIRED = 804
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
CLASSIFICATIONS = (
    "completed_PC",
    "completed_non_PC",
    "completed_reference_missing_or_ambiguous",
    "naked_single",
    "no_fill",
    "censored_or_boundary_unprovable",
)


class T1ScoringAdapterError(RuntimeError):
    """Raised when a T1 ledger fact leaves the frozen causal contract."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def _identity(value: Any, field: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise T1ScoringAdapterError(f"{field} is missing")
    return result


def _sha256(value: Any, field: str) -> str:
    result = _identity(value, field).lower()
    if len(result) != 64 or any(
        char not in "0123456789abcdef" for char in result
    ):
        raise T1ScoringAdapterError(f"{field} is not SHA-256")
    return result


def _exact_cent(value: Any, field: str) -> int:
    try:
        return exact_integer(value, field, minimum=1, maximum=99)
    except GuardedFillError as exc:
        raise T1ScoringAdapterError(str(exc)) from exc


def _exact_lot(value: Any, field: str) -> int:
    try:
        return exact_integer(value, field, minimum=LOT, maximum=LOT)
    except GuardedFillError as exc:
        raise T1ScoringAdapterError(str(exc)) from exc


def _finite(value: Any, field: str) -> float:
    try:
        return finite_number(value, field)
    except GuardedFillError as exc:
        raise T1ScoringAdapterError(str(exc)) from exc


def _optional_exact_integer(value: Any, field: str) -> int | None:
    if value is None:
        return None
    try:
        return exact_integer(value, field)
    except GuardedFillError as exc:
        raise T1ScoringAdapterError(str(exc)) from exc


@dataclass(frozen=True)
class T1CreditedFill(GuardedFill):
    base_candidate_id: str
    fill_role: str
    action_timestamp: float
    action_trigger_receipt: str
    action_trigger_receipts: tuple[str, ...]
    fill_receipt: str
    fill_book_receipt: str
    first_filled_leg: str | None
    first_fill_timestamp: float | None
    realized_first_leg_d1_cents: int | None
    b2_max_cents: int | None
    sibling_d2_cents: int | None
    strict_combined_budget_passed: bool | None
    source_overlay_sha256: str
    source_overlay_shard_sha256: str
    persistence_participated: bool
    self_trigger_fill: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def adapt_t1_unique_fill_row(
    row: Mapping[str, Any],
    *,
    expected_candidates: frozenset[str] | set[str],
    candidate_to_parent: Mapping[str, str],
    expected_legs: Mapping[tuple[str, str], str],
) -> T1CreditedFill:
    """Validate one construction-frozen T1 fill without raw policy input."""
    forbidden = {
        "causal_policy_fill_state_by_leg",
        "post_first_effective_actions",
        "order_intervals_by_leg",
        "raw_policy_actions",
    }
    if forbidden.intersection(row):
        raise T1ScoringAdapterError("raw T1 causal state is forbidden at runtime")
    if row.get("schema_version") != SCHEMA:
        raise T1ScoringAdapterError("wrong T1 unique-fill schema")
    if row.get("scored") is not False or row.get("metrics") is not None:
        raise T1ScoringAdapterError("T1 ledger is not score-free")
    if row.get("lawful_guarded_credited_fill") is not True:
        raise T1ScoringAdapterError("row is not a lawful guarded credited fill")

    candidate_id = _identity(row.get("candidate_id"), "candidate id")
    base_candidate = _identity(
        row.get("base_candidate_id"), "base candidate id"
    )
    event_id = _identity(row.get("event_id"), "event id")
    event_date = _identity(row.get("event_date"), "event date")
    leg_id = _identity(row.get("leg_id"), "leg id")
    ticker = _identity(row.get("ticker"), "ticker")
    if candidate_id not in expected_candidates:
        raise T1ScoringAdapterError("candidate outside frozen T1 allowlist")
    if candidate_to_parent.get(candidate_id) != base_candidate:
        raise T1ScoringAdapterError("T1/base candidate binding changed")
    if event_date in SEALED_HOLDOUT_DATES:
        raise T1ScoringAdapterError("sealed July 24-26 input refused")
    if event_date not in DEVELOPMENT_DATES:
        raise T1ScoringAdapterError("non-development date refused")
    if expected_legs.get((event_id, leg_id)) != ticker:
        raise T1ScoringAdapterError("unknown event/leg/ticker identity")

    quantity = _exact_lot(row.get("quantity"), "credited quantity")
    exposed_x = _exact_cent(row.get("exposed_X_cents"), "exposed X")
    fill_price = _exact_cent(row.get("fill_price_cents"), "fill price")
    if exposed_x != fill_price:
        raise T1ScoringAdapterError("fill price differs from exposed X")
    evidence_type = _identity(row.get("fill_evidence_type"), "evidence type")
    if evidence_type not in SUPPORTED_EVIDENCE:
        raise T1ScoringAdapterError("unsupported fill evidence")
    evidence = row.get("fill_evidence")
    if not isinstance(evidence, Mapping):
        raise T1ScoringAdapterError("fill evidence receipt is missing")
    evidence_ts = _finite(row.get("evidence_timestamp"), "evidence timestamp")
    action_ts = _finite(row.get("action_timestamp"), "action timestamp")
    if evidence_ts + 1e-6 < action_ts:
        raise T1ScoringAdapterError("fill precedes its action")
    fill_receipt = _identity(row.get("fill_receipt"), "fill receipt")
    if evidence_type == "PRICE_REACHED":
        if _identity(
            evidence.get("print_receipt"), "print receipt"
        ) != fill_receipt:
            raise T1ScoringAdapterError("print receipt identity mismatch")
        print_ts = _finite(
            evidence.get("print_timestamp"), "print timestamp"
        )
        print_price = _exact_cent(
            evidence.get("print_price_cents"), "print price"
        )
        print_size = _finite(evidence.get("print_size"), "print size")
        if (
            abs(print_ts - evidence_ts) > 1e-6
            or print_price > exposed_x
            or print_size <= 0
        ):
            raise T1ScoringAdapterError(
                "print is not positive-size at/below exposed X"
            )
    else:
        if _identity(
            evidence.get("book_receipt"), "strict-ask book receipt"
        ) != fill_receipt:
            raise T1ScoringAdapterError("strict-ask receipt mismatch")
        book_ts = _finite(
            evidence.get("book_timestamp"), "strict-ask timestamp"
        )
        ask = _exact_cent(
            evidence.get("external_ask_cents"), "strict external ask"
        )
        if abs(book_ts - evidence_ts) > 1e-6 or ask >= exposed_x:
            raise T1ScoringAdapterError(
                "strict ask is not strictly below exposed X"
            )
    trigger_receipts = tuple(
        sorted({
            _identity(value, "action trigger receipt")
            for value in (row.get("action_trigger_receipts") or [])
        })
    )
    trigger = _identity(row.get("action_trigger_receipt"), "trigger receipt")
    if trigger not in trigger_receipts:
        raise T1ScoringAdapterError("primary trigger absent from trigger set")
    self_trigger = fill_receipt in trigger_receipts
    if self_trigger or row.get("self_trigger_fill") is not False:
        raise T1ScoringAdapterError("new action used its own trigger as a fill")

    boundary = row.get("boundary")
    if not isinstance(boundary, Mapping):
        raise T1ScoringAdapterError("boundary receipt missing")
    if boundary.get("positive_window1_provable") is not True:
        raise T1ScoringAdapterError("unprovable boundary in fill ledger")
    if boundary.get("schedule_can_prove_positive") is not False:
        raise T1ScoringAdapterError("schedule cannot prove a positive fill")
    cutoff = _finite(
        boundary.get("guarded_cutoff_ts"), "guarded cutoff timestamp"
    )
    evaluated_right = _finite(
        row.get("evaluated_right_ts"), "evaluated right timestamp"
    )
    if evidence_ts > cutoff + 1e-6 or evidence_ts > evaluated_right + 1e-6:
        raise T1ScoringAdapterError("post-right fill entered unique ledger")

    fill_role = _identity(row.get("fill_role"), "fill role")
    if fill_role not in {"first_leg", "sibling"}:
        raise T1ScoringAdapterError("unknown fill role")
    first_leg = row.get("first_filled_leg")
    first_ts = row.get("first_fill_timestamp")
    d1 = _optional_exact_integer(
        row.get("realized_first_leg_d1_cents"), "first-leg d1"
    )
    b2_max = _optional_exact_integer(row.get("b2_max_cents"), "b2 max")
    d2 = _optional_exact_integer(row.get("sibling_d2_cents"), "sibling d2")
    strict = row.get("strict_combined_budget_passed")
    if fill_role == "sibling":
        if not first_leg or first_ts is None or d1 is None:
            raise T1ScoringAdapterError("sibling fill lacks first-fill state")
        first_ts = _finite(first_ts, "first-fill timestamp")
        if evidence_ts <= first_ts:
            raise T1ScoringAdapterError("sibling fill is not strictly later")
        if b2_max != math.floor(-d1 - FEE_CENTS - 1):
            raise T1ScoringAdapterError("b2_max arithmetic changed")
        reference_bid = _exact_cent(
            evidence.get("action_external_bid_cents"),
            "sibling action-time external bid",
        )
        if d2 != exposed_x - reference_bid:
            raise T1ScoringAdapterError(
                "sibling d2 differs from contemporaneous BBO"
            )
        expected_strict = d1 + d2 + FEE_CENTS < 0
        if strict is not expected_strict:
            raise T1ScoringAdapterError(
                "sibling strict-budget verdict is inconsistent"
            )
        if d2 > 0 and not expected_strict:
            raise T1ScoringAdapterError(
                "positive-d2 sibling fill violates combined budget"
            )
    elif strict is not None or d2 is not None:
        raise T1ScoringAdapterError("first-leg row contains sibling budget truth")

    selector_hash = _sha256(
        row.get("selector_receipt_sha256"), "selector receipt SHA-256"
    )
    return T1CreditedFill(
        candidate_id=candidate_id,
        event_id=event_id,
        event_date=event_date,
        category=str(row.get("category") or ""),
        leg_id=leg_id,
        ticker=ticker,
        order_interval_id=_identity(
            row.get("exposure_interval_id"), "exposure interval"
        ),
        evidence_type=evidence_type,
        evidence_receipt=fill_receipt,
        evidence_timestamp=evidence_ts,
        exposed_price_cents=exposed_x,
        accounting_fill_price_cents=fill_price,
        accounting_quantity=quantity,
        evaluated_right_ts=evaluated_right,
        guarded_cutoff_ts=cutoff,
        boundary_source_class=_identity(
            boundary.get("start_source_class"), "boundary source class"
        ),
        boundary_guard_id=_identity(
            boundary.get("guard_id"), "boundary guard id"
        ),
        boundary_guard_seconds=exact_integer(
            boundary.get("guard_seconds"), "guard seconds", minimum=0
        ),
        selector_receipt_sha256=selector_hash,
        selection_basis=_identity(
            row.get("selection_basis"), "selection basis"
        ),
        base_candidate_id=base_candidate,
        fill_role=fill_role,
        action_timestamp=action_ts,
        action_trigger_receipt=trigger,
        action_trigger_receipts=trigger_receipts,
        fill_receipt=fill_receipt,
        fill_book_receipt=_identity(
            row.get("fill_book_receipt"), "fill book receipt"
        ),
        first_filled_leg=str(first_leg) if first_leg is not None else None,
        first_fill_timestamp=(
            _finite(first_ts, "first-fill timestamp")
            if first_ts is not None else None
        ),
        realized_first_leg_d1_cents=d1,
        b2_max_cents=b2_max,
        sibling_d2_cents=d2,
        strict_combined_budget_passed=(
            bool(strict) if strict is not None else None
        ),
        source_overlay_sha256=_sha256(
            row.get("source_overlay_sha256"), "source overlay SHA-256"
        ),
        source_overlay_shard_sha256=_sha256(
            row.get("source_overlay_shard_sha256"),
            "source overlay shard SHA-256",
        ),
        persistence_participated=bool(row.get("persistence_participated")),
        self_trigger_fill=False,
    )


def adapt_t1_unique_fill_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    expected_candidates: frozenset[str] | set[str],
    candidate_to_parent: Mapping[str, str],
    expected_legs: Mapping[tuple[str, str], str],
) -> dict[tuple[str, str, str], T1CreditedFill]:
    fills: dict[tuple[str, str, str], T1CreditedFill] = {}
    causal_identities: dict[str, tuple[str, str, str]] = {}
    for row in rows:
        fill = adapt_t1_unique_fill_row(
            row,
            expected_candidates=expected_candidates,
            candidate_to_parent=candidate_to_parent,
            expected_legs=expected_legs,
        )
        key = (fill.candidate_id, fill.event_id, fill.leg_id)
        if key in fills:
            raise T1ScoringAdapterError(
                "multiple credited fills for one candidate/event/leg"
            )
        causal_identity = _identity(
            row.get("causal_fill_identity"), "causal fill identity"
        )
        prior = causal_identities.get(causal_identity)
        if prior is not None and prior != key:
            raise T1ScoringAdapterError(
                "one causal fill identity credits multiple legs"
            )
        causal_identities[causal_identity] = key
        fills[key] = fill
    return fills


def _parent_fill(fill: T1CreditedFill) -> GuardedFill:
    fields = {
        name: getattr(fill, name)
        for name in GuardedFill.__dataclass_fields__
    }
    fields["candidate_id"] = fill.base_candidate_id
    return GuardedFill(**fields)


def score_t1_event(
    *,
    candidate_id: str,
    parent_candidate_id: str,
    event: Mapping[str, Any],
    boundary: Mapping[str, Any],
    fills_by_leg: Mapping[str, T1CreditedFill],
    references_by_leg: Mapping[str, Any],
) -> dict[str, Any]:
    """Call the audited scorer exactly, then normalize report-only labels."""
    translated = {
        leg_id: _parent_fill(fill) for leg_id, fill in fills_by_leg.items()
    }
    row = audited_score_event(
        candidate_id=parent_candidate_id,
        event=event,
        boundary=boundary,
        fills_by_leg=translated,
        references_by_leg=references_by_leg,
    )
    row["candidate_id"] = candidate_id
    for leg in row["legs"]:
        fill = fills_by_leg.get(str(leg["leg_id"]))
        leg["t1_fill_role"] = fill.fill_role if fill else None
        leg["t1_realized_first_leg_d1_cents"] = (
            fill.realized_first_leg_d1_cents if fill else None
        )
        leg["t1_b2_max_cents"] = fill.b2_max_cents if fill else None
        leg["t1_sibling_d2_cents"] = fill.sibling_d2_cents if fill else None
        leg["t1_strict_combined_budget_passed"] = (
            fill.strict_combined_budget_passed if fill else None
        )
        leg["t1_persistence_participated"] = (
            fill.persistence_participated if fill else False
        )
    if row["classification"] == "completed_reference_missing":
        row["classification"] = (
            "completed_reference_missing_or_ambiguous"
        )
        row["PC"] = None
        row["IC"] = None
    elif row["classification"] == "censored_boundary":
        row["classification"] = "censored_or_boundary_unprovable"
    return row


def aggregate_t1_candidate(
    *,
    candidate_id: str,
    parent_candidate_id: str,
    rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Report T1 rows using audited aggregates without changing metrics."""
    if len(rows) != D_REQUIRED:
        raise T1ScoringAdapterError("D must remain exactly 804")
    shadow = []
    for source in rows:
        row = dict(source)
        row["candidate_id"] = parent_candidate_id
        if row["classification"] == (
            "completed_reference_missing_or_ambiguous"
        ):
            row["classification"] = "completed_reference_missing"
            row["PC"] = False
            row["IC"] = False
        elif row["classification"] == "censored_or_boundary_unprovable":
            row["classification"] = "censored_boundary"
        shadow.append(row)
    audited = audited_aggregate_candidate(parent_candidate_id, shadow)
    raw = audited["raw_integers_before_percentages"]
    census = Counter(str(row["classification"]) for row in rows)
    if set(census) - set(CLASSIFICATIONS):
        raise T1ScoringAdapterError("unknown T1 classification")
    if sum(census.values()) != D_REQUIRED:
        raise T1ScoringAdapterError("six-class conservation failed")
    completed_known = [
        row for row in rows
        if row["classification"] in {"completed_PC", "completed_non_PC"}
    ]
    pc_but_not_ic = sum(
        row.get("PC") is True and row.get("IC") is False
        for row in completed_known
    )
    positive_d2_pc = sum(
        row.get("PC") is True
        and any(
            (leg.get("t1_sibling_d2_cents") or 0) > 0
            for leg in row["legs"]
        )
        for row in completed_known
    )
    persistence = sum(
        any(bool(leg.get("t1_persistence_participated")) for leg in row["legs"])
        for row in rows
    )
    c_count = int(raw["C"])
    return {
        "schema_version": VERSION + "-candidate-summary-v1",
        "candidate_id": candidate_id,
        "parent_reference_candidate_id": parent_candidate_id,
        "D": D_REQUIRED,
        "C": c_count,
        "C_over_D": c_count / D_REQUIRED,
        "PC": int(raw["PC"]),
        "PC_over_D": int(raw["PC"]) / D_REQUIRED,
        "PC_shortfall_from_603": max(0, TARGET_PC - int(raw["PC"])),
        "IC": int(raw["IC"]),
        "IC_over_D": int(raw["IC"]) / D_REQUIRED,
        "S": int(raw["S"]),
        "S_over_D": int(raw["S"]) / D_REQUIRED,
        "official_target_metric": "PC_over_D",
        "completion_conditioned_diagnostics": {
            "PC_over_C": int(raw["PC"]) / c_count if c_count else None,
            "IC_over_C": int(raw["IC"]) / c_count if c_count else None,
            "S_over_C": int(raw["S"]) / c_count if c_count else None,
            "official_target_metrics": False,
        },
        "classification_conservation": {
            **{name: census.get(name, 0) for name in CLASSIFICATIONS},
            "total": sum(census.values()),
            "equals_D804": sum(census.values()) == D_REQUIRED,
        },
        "PC_but_not_IC": pc_but_not_ic,
        "positive_d2_completed_PC": positive_d2_pc,
        "persistence_participation_event_count": persistence,
        "fill_evidence_decomposition": audited[
            "fill_evidence_decomposition"
        ],
        "distributions": audited["distributions"],
        "breakdowns": audited["breakdowns"],
        "ranking_or_selection_applied": False,
    }
