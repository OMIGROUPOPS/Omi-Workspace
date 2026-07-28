"""Focused causal contracts for the score-free Window-1 T2 PRE-RUN."""

from __future__ import annotations

import ast
import gzip
import json
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
ANALYSIS = REPO / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import window1_t2_causal_divot_instrument as t2  # noqa: E402
import window1_t2_causal_divot_prerun as freeze  # noqa: E402


PACKAGE = REPO / ".claude/window1_t2_causal_divot_prerun_20260727"


def book(
    ts: float, bid: int | None, ask: int | None, receipt: str,
) -> dict:
    return {
        "kind": "book",
        "ts": ts,
        "receipt_id": receipt,
        "source_receipt_identity": receipt,
        "bids": [] if bid is None else [[bid, 2.0], [bid - 1, 2.0]],
        "asks": [] if ask is None else [[ask, 2.0], [ask + 1, 2.0]],
        "last_trade_cents": bid,
        "last_trade_provenance": t2.passed.CARRIED_UNKNOWN,
        "last_trade_observed_at": ts,
        "last_trade_execution_at": None,
        "chain_state": {"transitions": {}},
    }


def trade(ts: float, price: int, size: float, receipt: str) -> dict:
    return {
        "kind": "print",
        "ts": ts,
        "price": price,
        "size": size,
        "trade_id": receipt,
        "receipt_id": receipt,
        "source_receipt_identity": receipt,
        "taker_side": "no",
        "own_order_fingerprint": False,
        "size_verified": True,
        "source": "normalized_public_true_print",
    }


def event(a: list[dict], b: list[dict], horizon: float = 1300.0) -> dict:
    return {
        "event_id": "KXATPCHALLENGERMATCH-26JUL12TESTAA",
        "event_date": "2026-07-12",
        "category": "ATP_CHALL",
        "policy_anchor_ts": horizon,
        "policy_anchor_observed_at_ts": 500.0,
        "policy_anchor_source": "timestamped_schedule_snapshot",
        "policy_left_ts": 900.0,
        "policy_decision_horizon_ts": horizon,
        "legs": [
            {
                "leg_id": "AAA", "ticker": "TEST-AA",
                "feature_availability": {}, "observations": a,
            },
            {
                "leg_id": "BBB", "ticker": "TEST-BB",
                "feature_availability": {}, "observations": b,
            },
        ],
    }


def boundary() -> dict:
    return {
        "event_id": "KXATPCHALLENGERMATCH-26JUL12TESTAA",
        "start_source_class": "official_exact",
        "positive_window1_provable": True,
        "guard_seconds": 60,
        "guarded_cutoff_ts": 1500.0,
        "boundary_law": "fixture_guarded_cutoff",
        "guard_id": "fixture",
        "conflict_status": "none",
        "guard_censor_reason": None,
        "schedule_can_prove_positive": False,
        "source_record_sha256": "b" * 64,
    }


def simulator(candidate: str) -> t2.T2Simulator:
    atlas = {
        "pages": {
            "ATP_CHALL|underdog|26_50": {
                "verdict": "PATH", "n": 44, "branded": "g9",
                "bottom": {"depth_p50": 5, "t_deep_p50_min": 40},
            },
            "ATP_CHALL|leader|51_75": {
                "verdict": "PATH", "n": 44, "branded": "g9",
                "bottom": {"depth_p50": 5, "t_deep_p50_min": 40},
            },
        }
    }
    spec = t2.load_candidate_spec(REPO)
    return t2.T2Simulator(
        t2.candidate_policy(REPO, spec, candidate),
        boundary=boundary(),
        atlas=atlas,
        guidebook={"pages": {}},
        recut={},
        taker_reach={"law": {}},
        source_hashes={"atlas": "a" * 64},
    )


def run(candidate: str, extra_b: list[dict]) -> dict:
    a = [
        book(1000, 40, 50, "a0"),
        book(1050, 45, 50, "a1"),
        trade(1100, 40, 0.25, "a-fill"),
    ]
    b = [book(1000, 60, 70, "b0"), *extra_b]
    return simulator(candidate).run(event(a, b))


def actions(result: dict, action: str) -> list[dict]:
    return [
        row for row in result["order_stream"] if row["action"] == action
    ]


def test_exact_eight_candidate_matrix_and_no_free_parameters() -> None:
    spec = t2.load_candidate_spec(REPO)
    assert tuple(spec["candidate_ids"]) == t2.CANDIDATES
    assert len(spec["candidate_ids"]) == 8
    assert spec["free_numeric_parameters"] == []
    assert "persistence_only" not in t2.CANDIDATES
    assert "response_only" not in t2.CANDIDATES


def test_fixed_control_emits_no_T2_decisions() -> None:
    result = run(
        "w1_t2__macro_hold__fixed_admission_parent_control",
        [trade(1200, 70, 1, "later")],
    )
    assert not actions(result, "t2_episode_keyed_decision")


def test_full_response_is_strictly_post_first_and_executable() -> None:
    result = run(
        "w1_t2__macro_hold__full_causal_divot_stack",
        [trade(1100, 70, 1, "same"), trade(1200, 70, 1, "later")],
    )
    decisions = actions(result, "t2_episode_keyed_decision")
    assert decisions
    assert all(row["ts"] > 1100 for row in decisions)
    assert not any(row["trigger_receipt"] == "same" for row in decisions)
    assert all(row["t2_decision"] in {
        "HOLD", "PLACE", "REPRICE", "PARK", "NO_CALL",
    } for row in decisions)


def test_action_trigger_cannot_fill_new_order() -> None:
    result = run(
        "w1_t2__macro_hold__full_causal_divot_stack",
        [trade(1200, 70, 0.1, "trigger")],
    )
    decisions = actions(result, "t2_episode_keyed_decision")
    assert decisions
    assert all(
        row["new_action_fill_eligible_on_trigger_receipt"] is False
        for row in decisions
    )
    assert not any(
        row["action"] in {
            "price_reached_policy_tape", "strict_ask_certain_fill"
        }
        and row.get("print_receipt") == "trigger"
        and row["ts"] == 1200
        and row["leg_id"] == "BBB"
        for row in result["order_stream"]
    )


def test_positive_d2_is_lawful_inside_combined_budget() -> None:
    sim = simulator(
        "w1_t2__macro_hold__non_displacing_target_completeness"
    )
    target = sim._lawful_candidate(
        source="BID_PLUS_ONE_FALLBACK_NOT_PREFERRED",
        x=41, bid=40, ask=45, d1=-7, b2_max=6, fee=0,
        source_receipts=["bbo"], observed_support={},
    )
    assert target["d2_cents"] == 1
    assert target["lawful"] is True
    assert target["checks"]["strict_combined_negative"] is True


def test_combined_zero_is_never_lawful() -> None:
    sim = simulator(
        "w1_t2__macro_hold__non_displacing_target_completeness"
    )
    target = sim._lawful_candidate(
        source="CURRENT_EXTERNAL_BID",
        x=40, bid=40, ask=45, d1=0, b2_max=-1, fee=0,
        source_receipts=["bbo"], observed_support={},
    )
    assert target["d2_cents"] == 0
    assert target["lawful"] is False


def test_positive_d2_is_not_preferred_over_existing_source_authority() -> None:
    sim = simulator(
        "w1_t2__macro_hold__non_displacing_target_completeness"
    )
    surface = {
        "targets": [
            {
                "source": "CURRENT_EXTERNAL_BID", "X_cents": 40,
                "lawful": True, "d2_cents": 0,
            },
            {
                "source": "BID_PLUS_ONE_FALLBACK_NOT_PREFERRED",
                "X_cents": 41, "lawful": True, "d2_cents": 1,
            },
        ]
    }
    selected = sim._select_target(
        surface, active_price=None, allow_recurrence=False,
        allow_decay=False,
    )
    assert selected["X_cents"] == 40


def test_current_true_print_X_is_retained_when_maker_guard_rejects_it() -> None:
    result = run(
        "w1_t2__macro_hold__non_displacing_target_completeness",
        [book(1150, 63, 64, "at-ask-book"), trade(1200, 64, 1, "at-ask")],
    )
    surfaces = [
        row
        for row in result["t2_target_surfaces_by_leg"]["BBB"]
        if row["trigger_receipt"] == "at-ask"
    ]
    assert len(surfaces) == 1
    contextual = [
        target for target in surfaces[0]["targets"]
        if target["source"] == "CURRENT_TRUE_PRINT_REACH_CONTEXT"
    ]
    assert len(contextual) == 1
    assert contextual[0]["X_cents"] == 64
    assert contextual[0]["checks"]["strict_combined_negative"] is True
    assert contextual[0]["checks"]["maker_safe"] is False
    assert contextual[0]["lawful"] is False
    assert simulator(
        "w1_t2__macro_hold__non_displacing_target_completeness"
    )._select_target(
        {"targets": [{
            **contextual[0],
            "lawful": True,
        }]},
        active_price=None,
        allow_recurrence=False,
        allow_decay=False,
    ) is None


def test_non_displacing_variant_holds_active_parent_exposure() -> None:
    result = run(
        "w1_t2__macro_hold__non_displacing_target_completeness",
        [trade(1200, 70, 1, "later")],
    )
    decisions = actions(result, "t2_episode_keyed_decision")
    assert decisions
    assert any(row["t2_decision"] == "HOLD" for row in decisions)
    assert not any(
        row["action"] == "reprice"
        and row["reason"] == "t2_receipt_keyed_sibling_target"
        for row in result["order_stream"]
    )


def test_missing_BBO_yields_named_NO_CALL_and_no_print_substitution() -> None:
    result = run(
        "w1_t2__macro_hold__full_causal_divot_stack",
        [book(1150, None, None, "empty"), trade(1200, 55, 1, "print")],
    )
    surfaces = [
        row for rows in result["t2_target_surfaces_by_leg"].values()
        for row in rows
    ]
    assert any(
        row["status"] == "MARKET_EVIDENCE_NO_CALL" for row in surfaces
    )


def test_one_active_five_contract_sibling_order() -> None:
    result = run(
        "w1_t2__macro_hold__full_causal_divot_stack",
        [trade(1200, 70, 1, "p1"), trade(1250, 70, 1, "p2")],
    )
    intervals = result["order_intervals_by_leg"]["BBB"]
    for timestamp in (1200, 1250):
        active = [
            row for row in intervals
            if row["opened_ts"] <= timestamp
            and (
                row["closed_ts"] is None
                or row["closed_ts"] >= timestamp
            )
        ]
        assert len(active) <= 1


def test_strict_ask_credit_precedes_any_T2_reprice() -> None:
    result = run(
        "w1_t2__macro_micro__full_causal_divot_stack",
        [book(1200, 58, 59, "strict")],
    )
    rows = [
        row for row in result["order_stream"]
        if row["leg_id"] == "BBB" and row["ts"] == 1200
    ]
    assert any(row["action"] == "strict_ask_certain_fill" for row in rows)
    assert not any(row["action"] in {"cancel", "reprice"} for row in rows)


def test_divot_recognition_cannot_be_its_own_recurrence() -> None:
    sim = simulator("w1_t2__macro_hold__full_causal_divot_stack")
    state = {
        "t2_latest_divot_by_price": {
            40: {
                "recognized_X_cents": 40,
                "recognition_ts": 1200.0,
                "recognition_receipt": "recognize",
            },
        },
        "t2_divot_recurrences": [],
        "t2_divot_chronology": [],
        "event_id": "E", "candidate_id": "C", "leg_id": "L",
    }
    assert sim._current_recurrences(
        state, trade(1200, 40, 1, "recognize")
    ) == []
    recurrences = sim._current_recurrences(
        state, trade(1201, 40, 1, "later")
    )
    assert len(recurrences) == 1
    assert recurrences[0]["recurrence_receipt_can_fill_new_action"] is False


def test_replacement_requires_named_decay_authority() -> None:
    source = (REPO / t2.__file__).read_text(encoding="utf-8")
    assert "NO_NAMED_RECEIPT_BACKED_EVIDENCE_DECAY" in source
    assert "T1_bid_plus_one_rule_retracted_after_zero_of_82_fills" in source
    assert "lawful_persistence" in source
    spec = t2.load_candidate_spec(REPO)
    assert spec["inherited_t1_persistence"] == "RETRACTED"


def test_causal_rolling_flow_matches_passed_exact_statistics() -> None:
    rolling = t2._RollingFlow()
    rows = [
        {"ts": 1000.0, "price": 40, "size": 0.5, "receipt": "p1"},
        {"ts": 1100.0, "price": 42, "size": 1.5, "receipt": "p2"},
        {"ts": 1300.0, "price": 41, "size": 2.0, "receipt": "p3"},
        {"ts": 2900.0, "price": 43, "size": 3.0, "receipt": "p4"},
    ]
    rolling.sync(rows[:3], 1300.0)
    assert rolling.upper_price_median() == 41
    assert rolling.gaps.median() == t2.passed.v1.median_cadence(rows[:3])
    rolling.sync(rows, 2900.0)
    expected = [row for row in rows if row["ts"] >= 1100.0]
    assert rolling.upper_price_median() == sorted(
        row["price"] for row in expected
    )[len(expected) // 2]
    assert rolling.gaps.median() == t2.passed.v1.median_cadence(expected)
    assert rolling.volume == sum(row["size"] for row in expected)


def test_no_IC_S_or_result_metric_gate_in_instrument_ast() -> None:
    tree = ast.parse((REPO / t2.__file__).read_text(encoding="utf-8"))
    names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    assert "IC" not in names
    assert "S" not in names
    assert "PC" not in names


def test_builder_has_no_scorer_or_execution_interface() -> None:
    source = (REPO / freeze.BUILDER_REL).read_text(encoding="utf-8")
    assert "window1_range_attack_scorer" not in source
    assert "scoring_runner" not in source
    assert "--mode execute" not in source
    freeze.assert_metrics_null(
        json.loads((REPO / freeze.SPEC_REL).read_text(encoding="utf-8"))
    )


def test_frozen_package_D_controls_and_five_no_BBO() -> None:
    if not PACKAGE.exists():
        pytest.skip("full T2 package not frozen during unit phase")
    d = json.loads(
        (PACKAGE / "D_CONSERVATION_RECEIPT.json").read_text()
    )
    assert set(d["D_per_candidate"].values()) == {804}
    control = json.loads(
        (PACKAGE / "FIXED_ADMISSION_PARENT_IDENTITY_RECEIPT.json").read_text()
    )
    assert control["candidate_normalized_semantic_mismatch_count"] == 0
    assert control["former_boundary_artifact_count"] == 3
    five = json.loads(
        (PACKAGE / "FIVE_NO_BBO_D_MEMBERSHIP_PROOF.json").read_text()
    )
    assert five["row_count"] == 40
    assert five["fabricated_order_count"] == 0


def test_frozen_fixture_migration_24_4_17() -> None:
    if not PACKAGE.exists():
        pytest.skip("full T2 package not frozen during unit phase")
    receipt = json.loads(
        (PACKAGE / "CAUSAL_FIXTURE_MIGRATION_TABLE.json").read_text()
    )
    assert receipt["source_fixture_counts"] == {
        "missing_episode_keyed_decision": 24,
        "omitted_lawful_target": 4,
        "moved_away": 17,
        "capacity_unproved_diagnostic_only": 2,
    }
    assert receipt["all_acceptance_checks_passed"] is True


def test_frozen_invariants_and_mechanism_status() -> None:
    if not PACKAGE.exists():
        pytest.skip("full T2 package not frozen during unit phase")
    receipt = json.loads(
        (PACKAGE / "INVARIANT_RECEIPT.json").read_text()
    )
    for key, value in receipt.items():
        if key.endswith("_paths") or key.endswith("_admissions"):
            assert value == 0
    mechanisms = json.loads(
        (PACKAGE / "MECHANISM_STATUS_TABLE.json").read_text()
    )
    status = {
        row["mechanism"]: row["status"]
        for row in mechanisms["mechanisms"]
    }
    assert status["LIVE_AIM_mapping"] == "BOUND"
    assert status["Pinnacle"] == "ABSENT"
    assert status["T1_unconditional_persistence"] == "RETRACTED"


def test_artifact_hashes_and_two_build_determinism() -> None:
    if not PACKAGE.exists():
        pytest.skip("full T2 package not frozen during unit phase")
    manifest = json.loads(
        (PACKAGE / "ARTIFACT_HASH_MANIFEST.json").read_text()
    )
    for row in manifest["artifacts"]:
        artifact = PACKAGE / row["path"]
        assert artifact.stat().st_size == row["bytes"]
        assert row["bytes"] < 100_000_000
        assert freeze.sha256_file(artifact) == row["sha256"]
    assert len(freeze.TARGET_SELECTION_SHARDS) == 16
    assert all(
        (PACKAGE / name).is_file()
        for name in freeze.TARGET_SELECTION_SHARDS
    )
    deterministic = json.loads(
        (PACKAGE / "DETERMINISTIC_REGENERATION_RECEIPT.json").read_text()
    )
    assert deterministic["clean_regeneration_count"] == 2
    assert deterministic["byte_identical"] is True


def test_all_frozen_rows_keep_metrics_null() -> None:
    if not PACKAGE.exists():
        pytest.skip("full T2 package not frozen during unit phase")
    for path in PACKAGE.glob("*.json"):
        freeze.assert_metrics_null(json.loads(path.read_text()))
    for path in PACKAGE.glob("*.jsonl.gz"):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                freeze.assert_metrics_null(json.loads(line))
