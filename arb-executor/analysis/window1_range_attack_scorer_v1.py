#!/usr/bin/env python3
"""Pure deterministic scorer for frozen Window-1 Range-Attack V2 receipts."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping, Sequence

from window1_range_attack_guarded_fill_adapter_v1 import GuardedFill
from window1_range_attack_reference_adapter_v1 import (
    Window1CloseReference,
    guarded_cutoff,
)


VERSION = "window1-range-attack-deterministic-scorer-v1"
D_REQUIRED = 804
LOT = 5
TARGET_PC = 603
FEE_CENTS = 0
CANDIDATE_IDS = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
CLASSIFICATIONS = (
    "completed_PC",
    "completed_non_PC",
    "completed_reference_missing",
    "naked_single",
    "no_fill",
    "censored_boundary",
)


class RangeAttackScoringError(RuntimeError):
    """Raised when a frozen metric or population invariant is violated."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def _leg_id(leg: Mapping[str, Any]) -> str:
    value = str(leg.get("leg_id") or leg.get("leg") or "").strip()
    if not value:
        raise RangeAttackScoringError("event leg identity is missing")
    return value


def _fill_dict(fill: GuardedFill | None) -> dict[str, Any]:
    if fill is None:
        return {
            "fillable": False,
            "evidence_type": None,
            "evidence_receipt": None,
            "evidence_timestamp": None,
            "accounting_fill_price_cents": None,
            "accounting_quantity": 0,
            "order_interval_id": None,
        }
    return {
        "fillable": True,
        "evidence_type": fill.evidence_type,
        "evidence_receipt": fill.evidence_receipt,
        "evidence_timestamp": fill.evidence_timestamp,
        "accounting_fill_price_cents": fill.accounting_fill_price_cents,
        "accounting_quantity": fill.accounting_quantity,
        "order_interval_id": fill.order_interval_id,
    }

def _reference_dict(
    reference: Window1CloseReference | None,
) -> dict[str, Any]:
    if reference is None:
        return {
            "available": False,
            "window1_close_cents": None,
            "reference_timestamp": None,
            "reference_receipt": None,
            "reference_reason": "reference_record_missing",
        }
    return {
        "available": reference.available,
        "window1_close_cents": reference.window1_close_cents,
        "reference_timestamp": reference.reference_ts,
        "reference_receipt": reference.reference_receipt,
        "reference_reason": reference.reason,
        "reference_source": reference.reference_source,
        "t8_floor_ts": reference.t8_floor_ts,
    }


def score_event(
    *,
    candidate_id: str,
    event: Mapping[str, Any],
    boundary: Mapping[str, Any],
    fills_by_leg: Mapping[str, GuardedFill],
    references_by_leg: Mapping[str, Window1CloseReference],
) -> dict[str, Any]:
    """Score one candidate/event using adapted receipts only."""
    if candidate_id not in CANDIDATE_IDS:
        raise RangeAttackScoringError("candidate is outside frozen pair")
    event_id = str(event.get("event_id") or "").strip()
    event_date = str(event.get("event_date") or "").strip()
    category = str(event.get("category") or "")
    legs = list(event.get("legs") or [])
    if not event_id or len(legs) != 2:
        raise RangeAttackScoringError("event must have two identified legs")
    leg_ids = [_leg_id(leg) for leg in legs]
    if len(set(leg_ids)) != 2:
        raise RangeAttackScoringError("duplicate event leg identity")
    cutoff = guarded_cutoff(boundary)
    base = {
        "candidate_id": candidate_id,
        "event_id": event_id,
        "event_date": event_date,
        "category": category,
        "boundary_status": cutoff["status"],
        "boundary_source_class": cutoff["source_class"],
        "guarded_cutoff_ts": cutoff.get("cutoff_ts"),
        "boundary_guard_id": cutoff.get("guard_id"),
        "boundary_guard_seconds": cutoff.get("guard_seconds"),
        "fee_cents": FEE_CENTS,
        "C": False,
        "PC": False,
        "S": False,
        "IC": False,
        "combined_entry_cost_cents": None,
        "combined_delta_cents": None,
        "individual_deltas_cents": None,
        "censor_or_error_reason": None,
    }
    if cutoff["status"] != "positive":
        return {
            **base,
            "classification": "censored_boundary",
            "censor_or_error_reason": (
                f"start_boundary_{cutoff['status']}:"
                f"{cutoff['source_class']}"
            ),
            "legs": [
                {
                    "leg_id": _leg_id(leg),
                    "ticker": str(leg.get("ticker") or ""),
                    **_fill_dict(None),
                    **_reference_dict(None),
                    "individual_delta_cents": None,
                }
                for leg in legs
            ],
        }

    leg_rows = []
    for leg in legs:
        leg_id = _leg_id(leg)
        ticker = str(leg.get("ticker") or "").strip()
        fill = fills_by_leg.get(leg_id)
        reference = references_by_leg.get(leg_id)
        if fill is not None and (
            fill.event_id != event_id
            or fill.candidate_id != candidate_id
            or fill.ticker != ticker
            or fill.leg_id != leg_id
        ):
            raise RangeAttackScoringError("adapted fill identity mismatch")
        if reference is not None and (
            reference.event_id != event_id
            or reference.ticker != ticker
            or reference.leg_id != leg_id
        ):
            raise RangeAttackScoringError("reference identity mismatch")
        fill_data = _fill_dict(fill)
        reference_data = _reference_dict(reference)
        fill_price = fill_data["accounting_fill_price_cents"]
        close = reference_data["window1_close_cents"]
        delta = (
            int(fill_price) - int(close)
            if fill_price is not None and close is not None else None
        )
        leg_rows.append({
            "leg_id": leg_id,
            "ticker": ticker,
            **fill_data,
            **reference_data,
            "individual_delta_cents": delta,
        })

    fill_count = sum(row["fillable"] for row in leg_rows)
    completed = (
        fill_count == 2
        and all(row["accounting_quantity"] == LOT for row in leg_rows)
    )
    if fill_count == 1:
        classification = "naked_single"
    elif fill_count == 0:
        classification = "no_fill"
    else:
        classification = "completed_reference_missing"
    combined_cost = (
        sum(int(row["accounting_fill_price_cents"]) for row in leg_rows)
        if completed else None
    )
    references_complete = completed and all(
        row["window1_close_cents"] is not None for row in leg_rows
    )
    deltas = (
        [int(row["individual_delta_cents"]) for row in leg_rows]
        if references_complete else None
    )
    combined_delta = sum(deltas) + FEE_CENTS if deltas is not None else None
    pc = bool(completed and combined_delta is not None and combined_delta < 0)
    ic = bool(
        completed
        and deltas is not None
        and all(delta < 0 for delta in deltas)
    )
    s_metric = bool(completed and combined_cost is not None and combined_cost < 100)
    if completed and references_complete:
        classification = "completed_PC" if pc else "completed_non_PC"
    reason = (
        "window1_close_reference_missing"
        if completed and not references_complete else None
    )
    return {
        **base,
        "classification": classification,
        "censor_or_error_reason": reason,
        "C": completed,
        "PC": pc,
        "S": s_metric,
        "IC": ic,
        "combined_entry_cost_cents": combined_cost,
        "combined_delta_cents": combined_delta,
        "individual_deltas_cents": deltas,
        "legs": leg_rows,
    }


def _percentile(sorted_values: Sequence[float], fraction: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    position = fraction * (len(sorted_values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(sorted_values[lower])
    weight = position - lower
    return (
        float(sorted_values[lower]) * (1 - weight)
        + float(sorted_values[upper]) * weight
    )


def distribution(values: Iterable[float | int | None]) -> dict[str, Any]:
    admitted = sorted(float(value) for value in values if value is not None)
    return {
        "count": len(admitted),
        "min": admitted[0] if admitted else None,
        "p25": _percentile(admitted, 0.25),
        "p50": _percentile(admitted, 0.50),
        "p75": _percentile(admitted, 0.75),
        "p90": _percentile(admitted, 0.90),
        "max": admitted[-1] if admitted else None,
        "mean": sum(admitted) / len(admitted) if admitted else None,
    }


def _group(rows: Sequence[Mapping[str, Any]], field: str) -> list[dict[str, Any]]:
    buckets: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row.get(field) or "UNKNOWN")].append(row)
    return [
        {
            field: key,
            "D": len(bucket),
            "C": sum(bool(row["C"]) for row in bucket),
            "PC": sum(bool(row["PC"]) for row in bucket),
            "S": sum(bool(row["S"]) for row in bucket),
            "IC": sum(bool(row["IC"]) for row in bucket),
        }
        for key, bucket in sorted(buckets.items())
    ]


def aggregate_candidate(
    candidate_id: str,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Aggregate exactly one D=804 candidate without ranking."""
    if candidate_id not in CANDIDATE_IDS:
        raise RangeAttackScoringError("candidate is outside frozen pair")
    if len(rows) != D_REQUIRED:
        raise RangeAttackScoringError("D must remain exactly 804")
    keys = [(str(row["candidate_id"]), str(row["event_id"])) for row in rows]
    if len(set(keys)) != D_REQUIRED or any(key[0] != candidate_id for key in keys):
        raise RangeAttackScoringError("candidate/event identity conservation failed")
    census = Counter(str(row["classification"]) for row in rows)
    if set(census) - set(CLASSIFICATIONS):
        raise RangeAttackScoringError("unknown event classification")
    if sum(census.values()) != D_REQUIRED:
        raise RangeAttackScoringError("classification census does not conserve D")
    raw = {
        "D": D_REQUIRED,
        "C": sum(bool(row["C"]) for row in rows),
        "PC": sum(bool(row["PC"]) for row in rows),
        "S": sum(bool(row["S"]) for row in rows),
        "IC": sum(bool(row["IC"]) for row in rows),
    }
    evidence_pairs = Counter()
    for row in rows:
        if not row["C"]:
            continue
        types = tuple(leg["evidence_type"] for leg in row["legs"])
        evidence_pairs["/".join(types)] += 1
    completed = [row for row in rows if row["C"]]
    completed_decomposition = {
        "IC": sum(bool(row["IC"]) for row in completed),
        "PC_but_not_IC": sum(
            bool(row["PC"]) and not bool(row["IC"]) for row in completed
        ),
        "non_PC": sum(not bool(row["PC"]) for row in completed),
    }
    if sum(completed_decomposition.values()) != raw["C"]:
        raise RangeAttackScoringError("completed-pair decomposition failed")
    individual = [
        delta
        for row in rows
        for delta in (row["individual_deltas_cents"] or [])
    ]
    rates = {
        "PC_over_D": raw["PC"] / D_REQUIRED,
        "PC_over_C": raw["PC"] / raw["C"] if raw["C"] else None,
        "C_over_D": raw["C"] / D_REQUIRED,
        "S_over_C": raw["S"] / raw["C"] if raw["C"] else None,
        "IC_over_D": raw["IC"] / D_REQUIRED,
        "IC_over_C": raw["IC"] / raw["C"] if raw["C"] else None,
    }
    return {
        "schema_version": VERSION + "-candidate-summary-v1",
        "candidate_id": candidate_id,
        "raw_integers_before_percentages": {
            **raw,
            "target_PC": TARGET_PC,
            "PC_shortfall_from_603": max(0, TARGET_PC - raw["PC"]),
        },
        "rates": rates,
        "classification_conservation": {
            **{name: census.get(name, 0) for name in CLASSIFICATIONS},
            "total": sum(census.values()),
            "equals_D804": sum(census.values()) == D_REQUIRED,
        },
        "fill_evidence_decomposition": {
            "print/print": evidence_pairs.get("PRICE_REACHED/PRICE_REACHED", 0),
            "print/strict-ask": evidence_pairs.get(
                "PRICE_REACHED/STRICT_ASK_CERTAIN_FILL", 0
            ),
            "strict-ask/print": evidence_pairs.get(
                "STRICT_ASK_CERTAIN_FILL/PRICE_REACHED", 0
            ),
            "strict-ask/strict-ask": evidence_pairs.get(
                "STRICT_ASK_CERTAIN_FILL/STRICT_ASK_CERTAIN_FILL", 0
            ),
        },
        "completed_pair_decomposition": completed_decomposition,
        "distributions": {
            "combined_entry_cost_cents": distribution(
                row["combined_entry_cost_cents"] for row in rows
            ),
            "combined_delta_cents": distribution(
                row["combined_delta_cents"] for row in rows
            ),
            "individual_delta_cents": distribution(individual),
        },
        "breakdowns": {
            "by_date": _group(rows, "event_date"),
            "by_category": _group(rows, "category"),
            "by_boundary_source_class": _group(
                rows, "boundary_source_class"
            ),
        },
        "named_counts": {
            "naked_single": census.get("naked_single", 0),
            "no_fill": census.get("no_fill", 0),
            "censored": census.get("censored_boundary", 0),
            "reference_missing": census.get(
                "completed_reference_missing", 0
            ),
        },
        "selection_or_ranking_applied": False,
    }
