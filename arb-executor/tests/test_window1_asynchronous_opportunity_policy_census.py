from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest


ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_asynchronous_opportunity_policy_census import (  # noqa: E402
    TERMINAL_CLASSES,
    _book_context,
    classify_orientation,
    first_lawful_observation,
    headroom_d2_max,
    orientation_ids,
    strict_combined_budget,
    strictly_later,
)


def later_opportunity(
    *,
    exposed: bool = False,
    credited: bool = False,
    capacity: bool = False,
    moved: bool = False,
) -> dict:
    return {
        "price_reached": True,
        "strict_ask_certain_fill": False,
        "five_contract_capacity_proven": capacity,
        "policy_exposed_at_X": exposed,
        "policy_credited_fill": credited,
        "policy_moved_away_before_observation": moved,
    }


def test_price_reach_survives_when_five_contract_capacity_is_unproved() -> None:
    observation = first_lawful_observation(
        {
            "first_true_print_at_or_below": {
                "receipt": "print-1",
                "ts": 101.0,
                "price": 44,
                "size": 0.25,
            },
            "first_ask_strictly_below": None,
        }
    )
    assert observation == {
        "evidence_type": "PRICE_AT_X",
        "timestamp": 101.0,
        "receipt": "print-1",
        "price_cents": 44,
        "executed_size": 0.25,
    }
    terminal, reason = classify_orientation(
        boundary_available=True,
        d1_available=True,
        completed_by_policy=False,
        later_opportunities=[later_opportunity(capacity=False)],
        potential_exposures_without_evidence=0,
    )
    assert terminal == "price_reached_five_contract_capacity_unproved"
    assert reason == "price_reach_preserved_capacity_remains_unproved"


def test_positive_sibling_delta_is_lawful_inside_combined_headroom() -> None:
    assert headroom_d2_max(-7, 0) == 6
    assert strict_combined_budget(-7, 6, 0) is True
    assert strict_combined_budget(-7, 7, 0) is False


def test_same_timestamp_sibling_evidence_is_rejected() -> None:
    assert strictly_later(1_000.0, 1_000.0) is False


def test_strictly_later_sibling_evidence_is_accepted() -> None:
    assert strictly_later(1_000.0, 1_000.000001) is True


def test_both_first_leg_orientations_are_retained() -> None:
    assert orientation_ids(("A", "B")) == (("A", "B"), ("B", "A"))


def test_absent_bbo_is_named_unavailable_and_never_fabricated() -> None:
    context = _book_context([], [], 1_000.0, 40)
    assert context["available"] is False
    assert context["reason"] == "market_evidence_unavailable_no_lawful_BBO"
    assert context["nonself_best_bid_cents"] is None
    assert context["nonself_best_ask_cents"] is None
    assert context["top5_bids"] == []
    assert context["top5_asks"] == []


def test_policy_no_fill_is_not_relabelled_market_no_opportunity() -> None:
    terminal, reason = classify_orientation(
        boundary_available=True,
        d1_available=True,
        completed_by_policy=False,
        later_opportunities=[later_opportunity(capacity=True)],
        potential_exposures_without_evidence=0,
    )
    assert terminal == "lawful_in_budget_opportunity_policy_never_exposed"
    assert reason == "policy_never_exposed_at_lawful_X"
    assert terminal != "no_lawful_in_budget_later_sibling_opportunity_observed"


def test_exposed_price_with_proved_execution_is_not_silently_nonfill() -> None:
    terminal, _ = classify_orientation(
        boundary_available=True,
        d1_available=True,
        completed_by_policy=False,
        later_opportunities=[later_opportunity(exposed=True, capacity=True)],
        potential_exposures_without_evidence=0,
    )
    assert terminal == "policy_exposed_execution_or_strict_ask_proved_not_credited"


def test_exposure_without_execution_proof_remains_separate() -> None:
    terminal, _ = classify_orientation(
        boundary_available=True,
        d1_available=True,
        completed_by_policy=False,
        later_opportunities=[],
        potential_exposures_without_evidence=1,
    )
    assert terminal == "policy_exposed_without_execution_proof"


def test_missing_boundary_or_causal_reference_is_evidence_unavailable() -> None:
    terminal, _ = classify_orientation(
        boundary_available=False,
        d1_available=True,
        completed_by_policy=False,
        later_opportunities=[],
        potential_exposures_without_evidence=0,
    )
    assert terminal == "evidence_unavailable"


def test_terminal_classification_vocabulary_is_exact_and_mutually_exclusive() -> None:
    assert len(TERMINAL_CLASSES) == len(set(TERMINAL_CLASSES)) == 7
    assert set(TERMINAL_CLASSES) == {
        "completed_by_policy",
        "lawful_in_budget_opportunity_policy_never_exposed",
        "policy_exposed_execution_or_strict_ask_proved_not_credited",
        "policy_exposed_without_execution_proof",
        "price_reached_five_contract_capacity_unproved",
        "evidence_unavailable",
        "no_lawful_in_budget_later_sibling_opportunity_observed",
    }


def test_strict_ask_wins_same_timestamp_tie_without_erasing_print_fact() -> None:
    observation = first_lawful_observation(
        {
            "first_true_print_at_or_below": {
                "receipt": "print-1",
                "ts": 101.0,
                "price": 44,
                "size": 1,
            },
            "first_ask_strictly_below": {
                "receipt": "book-1",
                "ts": 101.0,
            },
        }
    )
    assert observation is not None
    assert observation["evidence_type"] == "STRICT_ASK_CERTAIN_FILL"
    assert observation["receipt"] == "book-1"


def test_module_has_no_scorer_import() -> None:
    source = (
        ANALYSIS / "window1_asynchronous_opportunity_policy_census.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not [name for name in imported if "scorer" in name.lower()]


@pytest.mark.parametrize("d2", [-20, -1, 0, 1, 6])
def test_headroom_accepts_all_strictly_combined_negative_deltas(d2: int) -> None:
    assert strict_combined_budget(-7, d2, 0) is True
