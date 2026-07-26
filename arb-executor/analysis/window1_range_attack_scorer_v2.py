#!/usr/bin/env python3
"""Range-Attack scorer V2 with sequence-honest reference receipts."""

from __future__ import annotations

from typing import Any, Mapping

from window1_range_attack_scorer_v1 import (
    D_REQUIRED,
    LOT,
    TARGET_PC,
    RangeAttackScoringError,
    aggregate_candidate as _aggregate_candidate_v1,
    score_event as _score_event_v1,
)


VERSION = "window1-range-attack-scorer-v2"


def score_event(
    *,
    candidate_id: str,
    event: Mapping[str, Any],
    boundary: Mapping[str, Any],
    fills_by_leg: Mapping[str, Any],
    references_by_leg: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the unchanged metric law and retain all tie-support receipts."""
    row = _score_event_v1(
        candidate_id=candidate_id,
        event=event,
        boundary=boundary,
        fills_by_leg=fills_by_leg,
        references_by_leg=references_by_leg,
    )
    for leg_row in row["legs"]:
        reference = references_by_leg[str(leg_row["leg_id"])]
        leg_row["reference_supporting_receipts"] = list(
            getattr(reference, "reference_supporting_receipts", ())
        )
        leg_row["reference_latest_timestamp_tie_count"] = int(
            getattr(reference, "latest_timestamp_tie_count", 0)
        )
        leg_row["reference_latest_timestamp_distinct_prices"] = list(
            getattr(reference, "latest_timestamp_distinct_prices", ())
        )
        leg_row["reference_authoritative_sequence_available"] = bool(
            getattr(reference, "authoritative_sequence_available", False)
        )
    return row


def aggregate_candidate(
    candidate_id: str,
    rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Preserve the frozen aggregate law; add no ranking or selection."""
    return _aggregate_candidate_v1(candidate_id, rows)

