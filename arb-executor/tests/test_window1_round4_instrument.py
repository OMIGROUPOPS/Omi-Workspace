from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round2_capability_proof as proof  # noqa: E402
import window1_round3_prerun_builder as r3builder  # noqa: E402
import window1_round4_instrument as round4  # noqa: E402


PAIR = "r4_pair_presence__park_join__causal_headroom_ladder"
FULL = "r4_full_drift_stack__causal_headroom_ladder"


def bind(event: dict) -> dict:
    r3builder.bind_round3_book_receipts(event)
    return event


def atlas() -> dict:
    pages = {}
    for role in ("leader", "underdog"):
        for cell in ("le25", "26_50", "51_75", "ge75"):
            pages[f"ATP_MAIN|{role}|{cell}"] = {
                "n": 40,
                "bottom": {"depth_p50": 4, "t_med_min": 30},
            }
    return {"pages": pages}


def run(event: dict, candidate: str = PAIR) -> dict:
    spec = round4.load_candidate_spec(ROOT)
    return round4.Round4Instrument(
        proof.synthetic_surfaces(),
        round4.candidate_policy(spec, candidate),
        atlas=atlas(),
        source_receipts={"atlas": "a" * 64, "drift": "d" * 64},
    ).run(bind(event))


def headroom_event(*, first_fill_size: float = 20) -> dict:
    event = proof.base_event()
    event["event_id"] = "FIXTURE-R4-HEADROOM"
    left = float(event["policy_left_ts"])
    event["legs"][0]["observations"] = [
        proof.book(left + 10, 60, 62),
        proof.book(left + 100, 64, 66),
        proof.trade(
            left + 200,
            57,
            size=first_fill_size,
            trade_id="A-EXACT5",
        ),
    ]
    event["legs"][1]["observations"] = [
        proof.book(left + 10, 40, 42),
        proof.book(left + 210, 40, 50),
        proof.trade(
            left + 220, 45, size=1, trade_id="B-LATER-TRIGGER-1"
        ),
        proof.trade(
            left + 230, 46, size=1, trade_id="B-LATER-TRIGGER-2"
        ),
    ]
    return event


def test_candidate_set_is_exactly_two_and_has_no_free_surface():
    spec = round4.load_candidate_spec(ROOT)
    assert spec["candidate_ids"] == [PAIR, FULL]
    assert spec["free_numeric_parameters"] == []
    for candidate in spec["candidate_ids"]:
        assert round4.candidate_policy(spec, candidate)["ablations"] == []
    fill = spec["primary_fill_contract"]
    assert fill["order_quantity_per_leg"] == 5
    assert "executed trade volume" in fill["authority"]
    assert "estimated or unobservable ahead-queue clearance" in fill[
        "not_required"
    ]
    assert "never changes" in fill["queue_treatment"]


def test_required_headroom_arithmetic_fixtures():
    assert round4.headroom_b2_max(-7, 0) == 6
    assert round4.headroom_b2_max(+1, 0) == -2
    assert round4.strict_pair_budget(-7, 6, 0)
    assert round4.strict_pair_budget(-7, 7, 0) is False
    assert round4.strict_pair_budget(-7, 2, 0)  # positive sibling delta


def test_partial_fill_arms_but_does_not_create_or_spend_headroom():
    result = run(headroom_event(first_fill_size=1))
    assert any(
        row["action"] == "headroom_partial_arm"
        and row["headroom_balance_created"] is False
        for row in result["order_stream"]
    )
    assert not any(
        row["action"] in {"headroom_exact5_arm", "headroom_decision"}
        for row in result["order_stream"]
    )


def test_primary_fill_accumulates_prints_and_ignores_estimated_queue():
    event = proof.base_event()
    left = float(event["policy_left_ts"])
    initial = proof.book(
        left + 10,
        60,
        62,
        own={"60": 5},
        bid_size=5,
        second_bid=(59, 10),
    )
    initial["bids"].append([57, 100])
    event["legs"][0]["observations"] = [
        initial,
        proof.trade(
            left + 20, 57, size=2, trade_id="A-PRIMARY-PARTIAL"
        ),
        proof.trade(
            left + 30, 57, size=3, trade_id="A-PRIMARY-COMPLETE"
        ),
    ]
    result = run(event)
    fills = [
        row for row in result["leg_streams"]["A"]
        if row["action"] == "fill_observed"
    ]
    assert [row["fill_quantity"] for row in fills] == [2, 3]
    assert [row["cumulative_quantity"] for row in fills] == [2, 5]
    assert fills[-1]["complete"] is True
    assert all(
        row["estimated_queue_applied_to_primary"] is False
        and row["displayed_depth_required"] is False
        and row["one_print_five_contracts_required"] is False
        for row in fills
    )
    assert fills[-1]["queue_sensitivity_diagnostic_only"][
        "estimated_queue_after"
    ] == 95
    assert fills[-1]["queue_sensitivity_diagnostic_only"][
        "same_print_volume_after_estimated_queue"
    ] == 0
    assert fills[-1]["queue_sensitivity_diagnostic_only"][
        "alters_primary_fill"
    ] is False


def test_print_above_limit_does_not_fill_but_better_price_does():
    event = proof.base_event()
    left = float(event["policy_left_ts"])
    event["legs"][0]["observations"] = [
        proof.book(
            left + 10,
            60,
            62,
            own={"60": 5},
            bid_size=5,
            second_bid=(59, 10),
        ),
        proof.trade(
            left + 20, 58, size=5, trade_id="A-ABOVE-LIMIT"
        ),
        proof.trade(
            left + 30, 56, size=5, trade_id="A-BETTER-PRICE"
        ),
    ]
    result = run(event)
    fills = [
        row for row in result["leg_streams"]["A"]
        if row["action"] == "fill_observed"
    ]
    assert len(fills) == 1
    assert fills[0]["trade_id"] == "A-BETTER-PRICE"
    assert fills[0]["fill_quantity"] == 5


def test_unknown_queue_never_defaults_primary_fill_to_nonfill():
    spec = round4.load_candidate_spec(ROOT)
    instance = round4.Round4Instrument(
        proof.synthetic_surfaces(),
        round4.candidate_policy(spec, PAIR),
        atlas=atlas(),
    )
    state = {
        "event_id": "FIXTURE-UNKNOWN-QUEUE",
        "candidate_id": PAIR,
        "leg_id": "A",
        "ticker": "FIXTURE-A",
        "actions": [],
        "active_order": {
            "price": 40,
            "remaining": 5.0,
            "queue_ahead": None,
        },
        "quantity": 0.0,
        "cost": 0.0,
    }
    completed = instance._fill_from_print(
        state,
        proof.trade(
            100, 40, size=5, trade_id="UNKNOWN-QUEUE-PRINT"
        ),
    )
    assert completed is True
    assert state["quantity"] == 5
    receipt = state["actions"][-1]
    assert receipt["estimated_queue_applied_to_primary"] is False
    assert receipt["queue_sensitivity_diagnostic_only"][
        "queue_unknown"
    ] is True


def test_exact_five_freezes_b1_then_later_trigger_moves_only_one_cent():
    result = run(headroom_event())
    arm = next(
        row for row in result["order_stream"]
        if row["action"] == "headroom_exact5_arm"
    )
    moves = [
        row for row in result["order_stream"]
        if row["action"] == "headroom_decision"
        and row["action_taken"]
    ]
    assert arm["b1_cents"] == -6
    assert arm["b2_max_cents"] == 5
    assert len(moves) == 2
    assert all(
        row["proposed_price_cents"]
        == row["prior_order_price_cents"] + 1
        for row in moves
    )
    assert all(row["strict_combined_guard"] for row in moves)
    assert moves[0]["ts"] > arm["ts"]


def test_queue_is_preserved_on_refusal_and_accounted_on_reprice():
    result = run(headroom_event())
    decisions = [
        row for row in result["order_stream"]
        if row["action"] == "headroom_decision"
    ]
    assert decisions
    assert all(
        row["queue_surrendered"] is row["action_taken"]
        and row["queue_retained"] is (not row["action_taken"])
        for row in decisions
    )
    for row in decisions:
        if row["action_taken"]:
            assert row["queue_ahead_after"] is not None


def test_budget_reducing_correction_waits_for_positive_print_trigger():
    event = headroom_event()
    event["legs"][1]["observations"][1]["bids"][0][0] = 30
    result = run(event)
    correction = next(
        row for row in result["order_stream"]
        if row["action"] == "headroom_decision"
        and row.get("movement_kind") == "budget_reducing_correction"
    )
    assert correction["trigger_receipt"] == "B-LATER-TRIGGER-1"
    assert correction["action_taken"] is True
    assert correction["proposed_price_cents"] < (
        correction["prior_order_price_cents"]
    )
    assert correction["strict_combined_guard"] is True


def test_every_headroom_decision_has_the_required_causal_receipt():
    result = run(headroom_event())
    required = {
        "event_id",
        "candidate_id",
        "leg_id",
        "trigger_receipt",
        "trigger_ts",
        "first_leg_exact5_vwap_cents",
        "R1_cents",
        "R1_ts",
        "R1_source",
        "b1_cents",
        "fee_cents",
        "R2_cents",
        "R2_ts",
        "R2_source",
        "proposed_price_cents",
        "b2_cents",
        "b2_max_cents",
        "macro_state",
        "micro_state",
        "prior_order_price_cents",
        "queue_ahead_before",
        "queue_ahead_after",
        "action_taken",
        "reason",
        "queue_retained",
        "queue_surrendered",
    }
    decisions = [
        row for row in result["order_stream"]
        if row["action"] == "headroom_decision"
    ]
    assert decisions
    assert all(required <= set(row) for row in decisions)


def test_combined_cost_and_individual_delta_never_gate_policy():
    event = headroom_event()
    result = run(event)
    instrument = next(
        row for row in result["order_stream"]
        if row["action"] == "headroom_decision"
    )
    assert instrument["action_taken"] is True
    spec = round4.load_candidate_spec(ROOT)
    policy = round4.candidate_policy(spec, PAIR)
    instance = round4.Round4Instrument(
        proof.synthetic_surfaces(), policy, atlas=atlas()
    )
    instance.states = [
        {"active_order": {"price": 70}},
        {"active_order": {"price": 45}},
    ]
    assert instance._pair_cost_passes(instance.states[0], 70) == (
        True,
        115.0,
    )
    # PC true / IC false and S false is a lawful diagnostic combination.
    d1, d2, combined_cost = -7, 2, 101
    assert d1 + d2 < 0
    assert not (d1 < 0 and d2 < 0)
    assert not combined_cost < 100


def test_macro_no_call_never_suppresses_presence():
    surfaces = proof.synthetic_surfaces()
    surfaces.cohort["rows"].clear()
    surfaces.drift["bands"] = {}
    spec = round4.load_candidate_spec(ROOT)
    result = round4.Round4Instrument(
        surfaces,
        round4.candidate_policy(spec, FULL),
        atlas={"pages": {}},
    ).run(bind(proof.base_event()))
    assert any(
        row["action"] in {"cohort_no_call", "feature_no_call"}
        and row.get("underlying_policy_continues") is True
        for row in result["order_stream"]
    )
    assert {
        row["leg_id"] for row in result["order_stream"]
        if row["action"] == "place"
    } == {"A", "B"}


@pytest.mark.parametrize("candidate", [PAIR, FULL])
def test_missing_recut_cell_is_no_call_not_presence_or_fill_gate(
    candidate,
):
    surfaces = proof.synthetic_surfaces()
    surfaces.recut["ATP_MAIN"] = {}
    spec = round4.load_candidate_spec(ROOT)
    result = round4.Round4Instrument(
        surfaces,
        round4.candidate_policy(spec, candidate),
        atlas=atlas(),
    ).run(bind(proof.base_event()))
    assert any(
        row["action"] == "feature_no_call"
        and row["reason"]
        == "dynamic_recut_cell_unavailable_pair_presence_continues"
        and row["underlying_policy_continues"] is True
        for row in result["order_stream"]
    )
    assert not any(
        row["action"] == "feature_censor"
        and row["reason"] == "dynamic_recut_cell_unavailable"
        for row in result["order_stream"]
    )
    assert {
        row["leg_id"] for row in result["order_stream"]
        if row["action"] == "place"
    } == {"A", "B"}


def test_drift_and_orientation_change_latent_posture_not_clock_orders():
    result = run(proof.base_event(), FULL)
    macro = [
        row for row in result["order_stream"]
        if row["action"] in {
            "orientation_observed", "drift_recognition_observed"
        }
    ]
    assert macro
    assert all(
        row["order_changed"] is False
        and row["movement_requires_later_positive_print"] is True
        for row in macro
    )
    macro_times = {row["ts"] for row in macro}
    assert not any(
        row["action"] in {"cancel", "reprice"}
        and row["ts"] in macro_times
        for row in result["order_stream"]
    )
    recalls = [
        row for row in result["order_stream"]
        if row["action"] == "drift_recognition_recall"
    ]
    assert recalls
    assert all(
        row["trigger_is_positive_size_nonself_print"] is True
        and row["order_changed"] is False
        and row["movement_uses_current_print_trigger"] is True
        for row in recalls
    )


@pytest.mark.parametrize("bad_size", [0, None, "malformed"])
def test_nonpositive_or_malformed_print_cannot_trigger_headroom(bad_size):
    event = headroom_event()
    event["legs"][1]["observations"][-1]["size"] = bad_size
    result = run(event)
    bad_id = event["legs"][1]["observations"][-1]["trade_id"]
    assert any(
        row["action"] == "print_excluded"
        and row.get("trade_id") == bad_id
        for row in result["order_stream"]
    )


def test_no_post_horizon_trigger_can_create_a_positive_action():
    event = headroom_event()
    event["legs"][1]["observations"][-1]["ts"] = float(
        event["policy_decision_horizon_ts"]
    ) + 1
    result = run(event)
    assert not any(
        row["action"] == "headroom_decision"
        and row.get("trigger_receipt") == "B-LATER-TRIGGER-2"
        for row in result["order_stream"]
    )


def test_policy_refuses_oracle_truth_and_holdout():
    leaked = proof.base_event()
    leaked["window1_close_reference_cents"] = 50
    with pytest.raises(
        round4.InstrumentError, match="evaluation truth is inaccessible"
    ):
        run(leaked)
    nested = proof.base_event()
    nested["legs"][0]["window1_close_reference_cents"] = 50
    with pytest.raises(
        round4.InstrumentError, match="evaluation truth is inaccessible"
    ):
        run(nested)
    holdout = proof.base_event()
    holdout["event_date"] = "2026-07-24"
    with pytest.raises(round4.InstrumentError, match="sealed holdout"):
        run(holdout)


def test_policy_module_cannot_import_diagnostic_or_scorer_code():
    path = ROOT / "arb-executor/analysis/window1_round4_instrument.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any(
        "diagnostic" in name or "scorer" in name for name in imports
    )


def test_exact_five_and_score_free_contract_are_byte_deterministic():
    event = headroom_event()
    first = run(event)
    second = run(copy.deepcopy(event))
    assert json.dumps(
        first, sort_keys=True, separators=(",", ":")
    ) == json.dumps(
        second, sort_keys=True, separators=(",", ":")
    )
    assert first["scored"] is False
    assert first["metrics"] is None
    assert all(
        row.get("quantity", 0) <= 5
        for row in first["order_stream"]
        if row["action"] in {"place", "reprice"}
    )
