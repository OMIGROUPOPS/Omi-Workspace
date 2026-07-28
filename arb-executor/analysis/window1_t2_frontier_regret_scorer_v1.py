#!/usr/bin/env python3
"""Frontier and regret reporting over the audited Window-1 metric scorer.

This module does not alter the settled C/PC/IC/S implementation.  It calls
the audited Range-Attack V2 event scorer, then presents those immutable facts
through cumulative completion-cost tiers and a separately supplied ex-post
oracle ledger.  Oracle facts are evaluation-only and never enter a policy
decision, target, exposure, or fill.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from types import SimpleNamespace
from typing import Any, Iterable, Mapping, Sequence

from window1_range_attack_scorer_v2 import (
    aggregate_candidate as audited_aggregate_candidate,
    score_event as audited_score_event,
)


VERSION = "window1-t2-frontier-regret-scorer-v1"
D_REQUIRED = 804
TARGET_PC = 603
FEE_CENTS = 0
FIT_DATES = frozenset(f"2026-07-{day:02d}" for day in range(12, 18))
POST_FIT_DATES = frozenset(f"2026-07-{day:02d}" for day in range(18, 21))
DEVELOPMENT_DATES = FIT_DATES | POST_FIT_DATES
SEALED_HOLDOUT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(24, 27)
)
TIERS: tuple[tuple[str, int | None, bool], ...] = (
    ("LE_93", 93, True),
    ("LE_95", 95, True),
    ("LE_97", 97, True),
    ("LT_100", 100, False),
    ("ANY_PRICE", None, True),
)
LOSS_STAGES = (
    "ZERO_REGRET",
    "BETTER_THAN_PRINT_FLOOR",
    "NEVER_RECOGNIZED",
    "RECOGNIZED_NOT_TARGETED",
    "TARGETED_NOT_EXPOSED",
    "EXPOSED_NOT_CREDITED",
    "COMPLETED_OVER_PROVEN_FLOOR",
    "PRICE_SEEN_CAPACITY_UNPROVED",
    "EVIDENCE_CENSORED",
    "REFERENCE_AMBIGUOUS",
)
CLAIM_FENCES = (
    "orientation is hash-bound but unconsumed",
    "volume, pressure and last trade are stored evidence, not candidate gates",
    "drift/band/recut/LIBRARY surfaces are not consumed",
    "depth claims are limited to bound top five",
    "Pinnacle and authoritative bookmaker/FV are absent",
    "historical divot tables are replaced by the bound native causal print-divot mechanism",
    "results describe these eight T2 candidate families, not the complete OS or a market ceiling",
)


class T2ScoringError(RuntimeError):
    """A frozen metric, frontier, oracle, or conservation law was violated."""


def _exact_int(
    value: Any,
    field: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool):
        raise T2ScoringError(f"{field} is boolean")
    if isinstance(value, int):
        result = value
    elif isinstance(value, float) and math.isfinite(value) and value.is_integer():
        result = int(value)
    else:
        raise T2ScoringError(f"{field} is not an exact integer")
    if minimum is not None and result < minimum:
        raise T2ScoringError(f"{field} is below {minimum}")
    if maximum is not None and result > maximum:
        raise T2ScoringError(f"{field} is above {maximum}")
    return result


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        raise T2ScoringError("rate denominator is not positive")
    return numerator / denominator


def tier_admits(cost: Any, tier_id: str) -> bool:
    """Apply exact tier endpoints; <100 never aliases <=100."""
    cents = _exact_int(cost, "combined entry cost", minimum=2, maximum=198)
    rule = next((row for row in TIERS if row[0] == tier_id), None)
    if rule is None:
        raise T2ScoringError(f"unknown frontier tier: {tier_id}")
    _, bound, inclusive = rule
    if bound is None:
        return True
    return cents <= bound if inclusive else cents < bound


def delta_orientation(delta1: Any, delta2: Any) -> str:
    d1 = _exact_int(delta1, "leg-1 delta")
    d2 = _exact_int(delta2, "leg-2 delta")
    if d1 < 0 and d2 < 0:
        return "BOTH_NEGATIVE"
    if d1 < 0 <= d2:
        return "LEG1_NEGATIVE_LEG2_NONNEGATIVE"
    if d1 >= 0 > d2:
        return "LEG1_NONNEGATIVE_LEG2_NEGATIVE"
    return "BOTH_NONNEGATIVE"


def score_t2_event(
    *,
    candidate_id: str,
    parent_candidate_id: str,
    event: Mapping[str, Any],
    boundary: Mapping[str, Any],
    fills_by_leg: Mapping[str, Any],
    references_by_leg: Mapping[str, Any],
) -> dict[str, Any]:
    """Delegate all settled metric mechanics to the audited V2 scorer."""
    audited_fills: dict[str, Any] = {}
    for leg_id, fill in fills_by_leg.items():
        if hasattr(fill, "to_dict"):
            payload = dict(fill.to_dict())
        else:
            payload = dict(vars(fill))
        payload["candidate_id"] = parent_candidate_id
        audited_fills[leg_id] = SimpleNamespace(**payload)
    row = audited_score_event(
        candidate_id=parent_candidate_id,
        event=event,
        boundary=boundary,
        fills_by_leg=audited_fills,
        references_by_leg=references_by_leg,
    )
    if row.get("D_member") is not True:
        # The settled scorer encodes D by emitting one row per event and does
        # not carry a D_member field.  A present row is the immutable D fact.
        if row.get("event_id") != event.get("event_id"):
            raise T2ScoringError("audited scorer changed event identity")
    row["candidate_id"] = candidate_id
    row["audited_parent_candidate_id"] = parent_candidate_id
    row["reference_status"] = (
        "AVAILABLE"
        if row.get("C") is True
        and row.get("individual_deltas_cents") is not None
        else (
            "MISSING_OR_AMBIGUOUS"
            if row.get("C") is True else "NOT_APPLICABLE"
        )
    )
    row["slice"] = (
        "fit" if row["event_date"] in FIT_DATES else "post_fit"
    )
    for leg_row in row["legs"]:
        fill = fills_by_leg.get(str(leg_row["leg_id"]))
        leg_row["T2_fill_role"] = (
            getattr(fill, "fill_role", None) if fill else None
        )
        leg_row["T2_sibling_d2_cents"] = (
            getattr(fill, "sibling_d2_cents", None) if fill else None
        )
        leg_row["T2_strict_combined_budget_passed"] = (
            getattr(fill, "strict_combined_budget_passed", None)
            if fill else None
        )
        leg_row["T2_action_authority"] = (
            getattr(fill, "action_authority", None) if fill else None
        )
    row["claim_fences"] = list(CLAIM_FENCES)
    return row


def classify_regret(
    *,
    reference_ambiguous: bool,
    evidence_censored: bool,
    price_seen: bool,
    capacity_proven: bool,
    recognized: bool,
    targeted: bool,
    exposed: bool,
    credited: bool,
    execution_proof_regret: int | None,
    signed_tape_touch_gap: int | None,
) -> str:
    """Assign exactly one primary loss stage in a fail-closed order."""
    if reference_ambiguous:
        return "REFERENCE_AMBIGUOUS"
    if evidence_censored:
        return "EVIDENCE_CENSORED"
    if price_seen and not capacity_proven:
        return "PRICE_SEEN_CAPACITY_UNPROVED"
    if not recognized:
        return "NEVER_RECOGNIZED"
    if not targeted:
        return "RECOGNIZED_NOT_TARGETED"
    if not exposed:
        return "TARGETED_NOT_EXPOSED"
    if not credited:
        return "EXPOSED_NOT_CREDITED"
    if execution_proof_regret is not None and execution_proof_regret < 0:
        raise T2ScoringError("execution-proof regret is negative")
    if signed_tape_touch_gap is not None and signed_tape_touch_gap < 0:
        return "BETTER_THAN_PRINT_FLOOR"
    if execution_proof_regret == 0:
        return "ZERO_REGRET"
    return "COMPLETED_OVER_PROVEN_FLOOR"


def regret_values(
    *,
    credited_fill: Any | None,
    exposed_price: Any | None,
    selected_target: Any | None,
    recognized_price: Any | None,
    tape_touch_floor: Any | None,
    proven_floor: Any | None,
) -> dict[str, int | None]:
    """Calculate signed gaps without fabricating penalties for missing facts."""
    def cent(value: Any | None, field: str) -> int | None:
        return None if value is None else _exact_int(
            value, field, minimum=1, maximum=99
        )

    fill = cent(credited_fill, "credited fill")
    exposed = cent(exposed_price, "exposed price")
    selected = cent(selected_target, "selected target")
    recognized = cent(recognized_price, "recognized opportunity")
    touch = cent(tape_touch_floor, "tape-touch floor")
    proven = cent(proven_floor, "five-contract-proven floor")
    execution_proof = (
        fill - proven if fill is not None and proven is not None else None
    )
    if execution_proof is not None and execution_proof < 0:
        raise T2ScoringError("execution-proof regret is negative")
    return {
        "execution_proof_regret_cents": execution_proof,
        "signed_tape_touch_gap_cents": (
            fill - touch if fill is not None and touch is not None else None
        ),
        "recognition_gap_cents": (
            recognized - touch
            if recognized is not None and touch is not None else None
        ),
        "target_selection_gap_cents": (
            selected - recognized
            if selected is not None and recognized is not None else None
        ),
        "exposure_gap_cents": (
            exposed - selected
            if exposed is not None and selected is not None else None
        ),
        "execution_gap_cents": (
            fill - exposed
            if fill is not None and exposed is not None else None
        ),
    }


def _percentile(values: Sequence[int], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _frontier_for_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    denominator: int,
) -> dict[str, Any]:
    if len(rows) != denominator:
        raise T2ScoringError("frontier row count differs from denominator")
    result: dict[str, Any] = {}
    previous_c = -1
    for tier_id, _, _ in TIERS:
        admitted = [
            row for row in rows
            if row.get("C") is True
            and tier_admits(row["combined_entry_cost_cents"], tier_id)
        ]
        orientations = Counter()
        pc = 0
        ic = 0
        s = 0
        pc_not_ic_orientations = Counter()
        missing = 0
        for row in admitted:
            # S depends only on the immutable entry prices, so a missing or
            # ambiguous reference cannot suppress it.
            s += int(row.get("S") is True)
            if row.get("reference_status") != "AVAILABLE":
                missing += 1
                continue
            orientation = delta_orientation(
                row["individual_deltas_cents"][0],
                row["individual_deltas_cents"][1],
            )
            orientations[orientation] += 1
            pc += int(row.get("PC") is True)
            ic += int(row.get("IC") is True)
            if row.get("PC") is True and row.get("IC") is False:
                pc_not_ic_orientations[orientation] += 1
        c_count = len(admitted)
        if c_count < previous_c:
            raise T2ScoringError("frontier tiers are not cumulative")
        previous_c = c_count
        result[tier_id] = {
            "denominator": denominator,
            "C": c_count,
            "C_over_D": _rate(c_count, denominator),
            "PC": pc,
            "PC_over_D": _rate(pc, denominator),
            "PC_shortfall_from_603": TARGET_PC - pc,
            "both_legs_negative": orientations["BOTH_NEGATIVE"],
            "leg1_negative_leg2_nonnegative": orientations[
                "LEG1_NEGATIVE_LEG2_NONNEGATIVE"
            ],
            "leg1_nonnegative_leg2_negative": orientations[
                "LEG1_NONNEGATIVE_LEG2_NEGATIVE"
            ],
            "both_legs_nonnegative": orientations["BOTH_NONNEGATIVE"],
            "reference_missing_completions": missing,
            "S": s,
            "S_over_D": _rate(s, denominator),
            "IC": ic,
            "IC_over_D": _rate(ic, denominator),
            "PC_but_not_IC": max(0, pc - ic),
            "PC_but_not_IC_leg1_negative_leg2_nonnegative": (
                pc_not_ic_orientations[
                    "LEG1_NEGATIVE_LEG2_NONNEGATIVE"
                ]
            ),
            "PC_but_not_IC_leg1_nonnegative_leg2_negative": (
                pc_not_ic_orientations[
                    "LEG1_NONNEGATIVE_LEG2_NEGATIVE"
                ]
            ),
        }
    return result


def aggregate_frontier(
    candidate_id: str,
    parent_candidate_id: str,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Publish aggregate, fit, and post-fit frontiers side by side."""
    if len(rows) != D_REQUIRED:
        raise T2ScoringError("candidate D changed from 804")
    dates = {str(row["event_date"]) for row in rows}
    if dates - DEVELOPMENT_DATES:
        raise T2ScoringError("non-development date entered frontier")
    fit = [row for row in rows if row["event_date"] in FIT_DATES]
    post = [row for row in rows if row["event_date"] in POST_FIT_DATES]
    if len(fit) != 525 or len(post) != 279:
        raise T2ScoringError("fit/post-fit conservation failed")
    audited_rows = [
        {**row, "candidate_id": parent_candidate_id} for row in rows
    ]
    audited = audited_aggregate_candidate(
        parent_candidate_id, audited_rows
    )
    audited["candidate_id"] = candidate_id
    audited["audited_parent_candidate_id"] = parent_candidate_id
    return {
        "candidate_id": candidate_id,
        "audited_metric_summary": audited,
        "frontier": {
            "aggregate": _frontier_for_rows(rows, denominator=804),
            "fit": _frontier_for_rows(fit, denominator=525),
            "post_fit": _frontier_for_rows(post, denominator=279),
        },
        "primary_objective": "maximize LT_100 completion-discount frontier",
        "minimum_floor": "PC >= 603 of D=804",
        "claim_fences": list(CLAIM_FENCES),
        "ranking_or_selection": None,
    }


def regret_distribution(
    values: Iterable[int | None],
    *,
    denominator: int,
) -> dict[str, Any]:
    rows = list(values)
    observed = [int(value) for value in rows if value is not None]
    if len(rows) != denominator:
        raise T2ScoringError("regret denominator conservation failed")
    return {
        "denominator": denominator,
        "observed_count": len(observed),
        "null_or_censored_count": denominator - len(observed),
        "median": _percentile(observed, 0.50),
        "p75": _percentile(observed, 0.75),
        "p90": _percentile(observed, 0.90),
        "zero_regret_count": sum(value == 0 for value in observed),
        "zero_regret_rate_over_D": _rate(
            sum(value == 0 for value in observed), denominator
        ),
        "total_cents_left_on_table": sum(observed),
    }


def require_claim_fences(report: Mapping[str, Any]) -> None:
    text = str(report)
    missing = [fence for fence in CLAIM_FENCES if fence not in text]
    if missing:
        raise T2ScoringError(
            "report template omitted claim fences: " + "; ".join(missing)
        )
