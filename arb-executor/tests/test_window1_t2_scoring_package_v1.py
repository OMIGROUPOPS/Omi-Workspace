from __future__ import annotations

import math
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_t2_frontier_regret_scorer_v1 import (
    CLAIM_FENCES,
    LOSS_STAGES,
    T2ScoringError,
    aggregate_frontier,
    classify_regret,
    regret_values,
    require_claim_fences,
    score_t2_event,
    tier_admits,
)
from window1_t2_scoring_adapter_v1 import (
    T2ScoringAdapterError,
    adapt_t2_unique_fill_row,
)
from window1_t2_scoring_runner_v1 import CANDIDATE_IDS


PARENT_HOLD = "w1_range_attack__macro_hold__combined_headroom"
CANDIDATE = "w1_t2__macro_hold__full_causal_divot_stack"


def boundary(event_id: str = "E") -> dict:
    return {
        "event_id": event_id,
        "positive_window1_provable": True,
        "schedule_can_prove_positive": False,
        "guarded_cutoff_ts": 200.0,
        "start_source_class": "official_exact",
        "exact_start_utc": "1970-01-01T00:04:20+00:00",
        "guard_band": {
            "guard_id": "official-point-strict-60s-v1",
            "positive_guard_seconds": 60.0,
        },
        "guard_id": "g",
        "guard_seconds": 0,
    }


def event(date: str = "2026-07-12") -> dict:
    return {
        "event_id": "E",
        "event_date": date,
        "category": "ATP_MAIN",
        "legs": [
            {"leg_id": "A", "ticker": "E-A"},
            {"leg_id": "B", "ticker": "E-B"},
        ],
    }


def fill(leg: str, price: int, ts: float) -> SimpleNamespace:
    return SimpleNamespace(
        candidate_id=CANDIDATE,
        event_id="E",
        event_date="2026-07-12",
        category="ATP_MAIN",
        leg_id=leg,
        ticker=f"E-{leg}",
        evidence_type="PRICE_REACHED",
        evidence_receipt=f"r-{leg}",
        evidence_timestamp=ts,
        accounting_fill_price_cents=price,
        accounting_quantity=5,
        order_interval_id=f"i-{leg}",
    )


def reference(leg: str, price: int | None) -> SimpleNamespace:
    return SimpleNamespace(
        event_id="E",
        event_date="2026-07-12",
        leg_id=leg,
        ticker=f"E-{leg}",
        available=price is not None,
        window1_close_cents=price,
        reference_ts=190.0 if price is not None else None,
        reference_receipt=f"close-{leg}" if price is not None else None,
        reference_source="frozen",
        t8_floor_ts=0.0,
        reason=None if price is not None else "missing",
        reference_supporting_receipts=(),
        latest_timestamp_tie_count=1 if price is not None else 0,
        latest_timestamp_distinct_prices=(price,) if price is not None else (),
        authoritative_sequence_available=False,
    )


def score(
    prices: tuple[int, int],
    closes: tuple[int | None, int | None],
) -> dict:
    return score_t2_event(
        candidate_id=CANDIDATE,
        parent_candidate_id=PARENT_HOLD,
        event=event(),
        boundary=boundary(),
        fills_by_leg={
            "A": fill("A", prices[0], 100.0),
            "B": fill("B", prices[1], 110.0),
        },
        references_by_leg={
            "A": reference("A", closes[0]),
            "B": reference("B", closes[1]),
        },
    )


@pytest.mark.parametrize(
    ("cost", "tiers"),
    [
        (93, {"LE_93", "LE_95", "LE_97", "LT_100", "ANY_PRICE"}),
        (94, {"LE_95", "LE_97", "LT_100", "ANY_PRICE"}),
        (95, {"LE_95", "LE_97", "LT_100", "ANY_PRICE"}),
        (96, {"LE_97", "LT_100", "ANY_PRICE"}),
        (97, {"LE_97", "LT_100", "ANY_PRICE"}),
        (98, {"LT_100", "ANY_PRICE"}),
        (99, {"LT_100", "ANY_PRICE"}),
        (100, {"ANY_PRICE"}),
    ],
)
def test_exact_frontier_boundaries(cost, tiers):
    observed = {
        name for name in ("LE_93", "LE_95", "LE_97", "LT_100", "ANY_PRICE")
        if tier_admits(cost, name)
    }
    assert observed == tiers


def test_fractional_cost_never_truncated():
    with pytest.raises(T2ScoringError):
        tier_admits(99.9, "LT_100")


def test_pc_can_pass_without_ic_and_positive_d2():
    row = score((40, 55), (45, 54))
    assert row["individual_deltas_cents"] == [-5, 1]
    assert row["combined_delta_cents"] == -4
    assert row["PC"] is True
    assert row["IC"] is False


def test_combined_zero_is_not_pc():
    row = score((40, 55), (45, 50))
    assert row["combined_delta_cents"] == 0
    assert row["PC"] is False


def test_fee_treatment_is_exact_zero():
    row = score((40, 55), (45, 54))
    assert row["fee_cents"] == 0


def test_reference_missing_preserves_completion_and_s():
    row = score((40, 55), (45, None))
    assert row["C"] is True
    assert row["S"] is True
    assert row["PC"] is False
    assert row["IC"] is False
    assert row["reference_status"] == "MISSING_OR_AMBIGUOUS"


def test_asynchronous_fill_times_are_lawful():
    row = score((40, 55), (45, 54))
    assert row["legs"][0]["evidence_timestamp"] == 100.0
    assert row["legs"][1]["evidence_timestamp"] == 110.0
    assert row["C"] is True


def test_strict_ask_better_than_print_floor_is_named():
    values = regret_values(
        credited_fill=40,
        exposed_price=40,
        selected_target=40,
        recognized_price=41,
        tape_touch_floor=41,
        proven_floor=40,
    )
    assert values["execution_proof_regret_cents"] == 0
    assert values["signed_tape_touch_gap_cents"] == -1
    assert classify_regret(
        reference_ambiguous=False,
        evidence_censored=False,
        price_seen=True,
        capacity_proven=True,
        recognized=True,
        targeted=True,
        exposed=True,
        credited=True,
        execution_proof_regret=0,
        signed_tape_touch_gap=-1,
    ) == "BETTER_THAN_PRINT_FLOOR"


def test_price_seen_capacity_unproved_is_not_market_absent():
    assert classify_regret(
        reference_ambiguous=False,
        evidence_censored=False,
        price_seen=True,
        capacity_proven=False,
        recognized=False,
        targeted=False,
        exposed=False,
        credited=False,
        execution_proof_regret=None,
        signed_tape_touch_gap=None,
    ) == "PRICE_SEEN_CAPACITY_UNPROVED"


def test_fully_censored_evidence_is_named():
    assert classify_regret(
        reference_ambiguous=False,
        evidence_censored=True,
        price_seen=False,
        capacity_proven=False,
        recognized=False,
        targeted=False,
        exposed=False,
        credited=False,
        execution_proof_regret=None,
        signed_tape_touch_gap=None,
    ) == "EVIDENCE_CENSORED"


def test_incomplete_event_has_no_fabricated_penalty():
    values = regret_values(
        credited_fill=None,
        exposed_price=None,
        selected_target=None,
        recognized_price=None,
        tape_touch_floor=30,
        proven_floor=31,
    )
    assert values["execution_proof_regret_cents"] is None
    assert values["signed_tape_touch_gap_cents"] is None


def test_negative_execution_proof_regret_is_hard_failure():
    with pytest.raises(T2ScoringError):
        regret_values(
            credited_fill=30,
            exposed_price=30,
            selected_target=30,
            recognized_price=30,
            tape_touch_floor=31,
            proven_floor=31,
        )


def test_negative_tape_touch_gap_is_allowed():
    values = regret_values(
        credited_fill=30,
        exposed_price=30,
        selected_target=30,
        recognized_price=31,
        tape_touch_floor=31,
        proven_floor=30,
    )
    assert values["signed_tape_touch_gap_cents"] == -1


def _synthetic_rows() -> list[dict]:
    rows = []
    dates = ["2026-07-12"] * 525 + ["2026-07-18"] * 279
    for index, date in enumerate(dates):
        rows.append({
            "candidate_id": CANDIDATE,
            "event_id": f"E{index:03d}",
            "event_date": date,
            "category": "ATP_MAIN",
            "boundary_source_class": "official_exact",
            "classification": "completed_PC",
            "C": True,
            "PC": True,
            "IC": index % 2 == 0,
            "S": True,
            "combined_entry_cost_cents": 93 + index % 8,
            "combined_delta_cents": -1,
            "individual_deltas_cents": [-2, 1],
            "reference_status": "AVAILABLE",
            "legs": [],
            "fee_cents": 0,
        })
    return rows


def test_aggregate_fit_postfit_and_frontier_monotonicity():
    summary = aggregate_frontier(CANDIDATE, PARENT_HOLD, _synthetic_rows())
    assert summary["frontier"]["aggregate"]["ANY_PRICE"]["C"] == 804
    assert summary["frontier"]["fit"]["ANY_PRICE"]["denominator"] == 525
    assert summary["frontier"]["post_fit"]["ANY_PRICE"]["denominator"] == 279
    counts = [
        summary["frontier"]["aggregate"][tier]["C"]
        for tier in ("LE_93", "LE_95", "LE_97", "LT_100", "ANY_PRICE")
    ]
    assert counts == sorted(counts)


def test_frontier_s_survives_missing_reference():
    rows = _synthetic_rows()
    rows[0] = {
        **rows[0],
        "classification": "completed_reference_missing",
        "PC": False,
        "IC": False,
        "individual_deltas_cents": None,
        "combined_delta_cents": None,
        "reference_status": "MISSING_OR_AMBIGUOUS",
    }
    summary = aggregate_frontier(CANDIDATE, PARENT_HOLD, rows)
    any_price = summary["frontier"]["aggregate"]["ANY_PRICE"]
    assert any_price["reference_missing_completions"] == 1
    assert any_price["S"] == 804
    assert any_price["S_over_D"] == 1.0


def fill_row(**changes):
    row = {
        "schema_version": "window1-t2-unique-credited-fill-v1",
        "candidate_id": CANDIDATE,
        "base_candidate_id": PARENT_HOLD,
        "event_id": "E",
        "event_date": "2026-07-12",
        "category": "ATP_MAIN",
        "leg_id": "A",
        "ticker": "E-A",
        "lawful_guarded_credited_fill": True,
        "quantity": 5,
        "exposed_X_cents": 40,
        "fill_price_cents": 40,
        "fill_evidence_type": "PRICE_REACHED",
        "fill_receipt": "print",
        "fill_book_receipt": "book-fill",
        "fill_evidence": {
            "print_receipt": "print",
            "print_timestamp": 110.0,
            "print_price_cents": 40,
            "print_size": 0.25,
            "action_external_bid_cents": 40,
        },
        "exposure_interval_id": "interval",
        "action_authority": "NATIVE_MACRO_TARGET",
        "action_timestamp": 100.0,
        "action_trigger_receipt": "book-action",
        "evidence_timestamp": 110.0,
        "evaluated_right_ts": 200.0,
        "boundary": boundary(),
        "fill_role": "first_leg",
        "first_filled_leg": "A",
        "first_fill_timestamp": 110.0,
        "realized_first_leg_d1_cents": 0,
        "b2_max_cents": -1,
        "sibling_d2_cents": None,
        "fee_cents": 0,
        "strict_combined_budget_passed": None,
        "self_trigger_fill": False,
        "selection_basis": "frozen",
        "causal_fill_identity": "a" * 64,
        "selector_receipt_sha256": "b" * 64,
        "source_stream_sha256": "c" * 64,
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    row.update(changes)
    return row


def test_exact_integer_adapter_accepts_subfive_print_size():
    adapted = adapt_t2_unique_fill_row(
        fill_row(),
        expected_candidates={CANDIDATE},
        expected_legs={("E", "A"): "E-A"},
    )
    assert adapted.accounting_quantity == 5


@pytest.mark.parametrize("value", [True, 5.9, 5.0001, math.nan, math.inf])
def test_exact_integer_adapter_rejects_noninteger_quantity(value):
    with pytest.raises(T2ScoringAdapterError):
        adapt_t2_unique_fill_row(
            fill_row(quantity=value),
            expected_candidates={CANDIDATE},
            expected_legs={("E", "A"): "E-A"},
        )


@pytest.mark.parametrize("field", ["exposed_X_cents", "fill_price_cents"])
def test_exact_integer_adapter_rejects_fractional_contract_prices(field):
    with pytest.raises(T2ScoringAdapterError):
        adapt_t2_unique_fill_row(
            fill_row(**{field: 40.9}),
            expected_candidates={CANDIDATE},
            expected_legs={("E", "A"): "E-A"},
        )


def test_exact_integer_adapter_rejects_fractional_print_price():
    row = fill_row()
    row["fill_evidence"] = {
        **row["fill_evidence"],
        "print_price_cents": 40.9,
    }
    with pytest.raises(T2ScoringAdapterError):
        adapt_t2_unique_fill_row(
            row,
            expected_candidates={CANDIDATE},
            expected_legs={("E", "A"): "E-A"},
        )


def test_holdout_rejected():
    with pytest.raises(T2ScoringAdapterError):
        adapt_t2_unique_fill_row(
            fill_row(event_date="2026-07-24"),
            expected_candidates={CANDIDATE},
            expected_legs={("E", "A"): "E-A"},
        )


def test_all_eight_candidate_identities_frozen():
    assert len(CANDIDATE_IDS) == 8
    assert len(set(CANDIDATE_IDS)) == 8
    assert all(candidate.startswith("w1_t2__") for candidate in CANDIDATE_IDS)


def test_loss_stage_allowlist_closed():
    assert len(LOSS_STAGES) == 10
    assert len(set(LOSS_STAGES)) == 10


def test_claim_fence_omission_is_fatal():
    with pytest.raises(T2ScoringError):
        require_claim_fences({"report": "partial"})
    require_claim_fences({"claim_fences": list(CLAIM_FENCES)})
