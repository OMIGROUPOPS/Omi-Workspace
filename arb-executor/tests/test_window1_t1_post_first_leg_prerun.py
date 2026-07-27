"""Focused causal contracts for the score-free Window-1 T1 PRE-RUN."""

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

import window1_t1_post_first_leg_instrument as t1  # noqa: E402
import window1_t1_post_first_leg_prerun as freeze  # noqa: E402


PACKAGE = REPO / ".claude/window1_t1_post_first_leg_prerun_20260727"


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
        "last_trade_provenance": t1.passed.CARRIED_UNKNOWN,
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


def boundary(cutoff: float = 1500.0) -> dict:
    return {
        "event_id": "KXATPCHALLENGERMATCH-26JUL12TESTAA",
        "start_source_class": "official_exact",
        "positive_window1_provable": True,
        "guard_seconds": 60,
        "guarded_cutoff_ts": cutoff,
        "boundary_law": "fixture_guarded_cutoff",
        "guard_id": "fixture",
        "conflict_status": "none",
        "guard_censor_reason": None,
        "schedule_can_prove_positive": False,
        "source_record_sha256": "b" * 64,
    }


def sources() -> tuple[dict, dict, dict, dict, dict]:
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
    return (
        atlas,
        {"pages": {}},
        {},
        {"law": {}},
        {"atlas": "a" * 64},
    )


def simulator(candidate: str) -> t1.T1Simulator:
    atlas, guidebook, recut, reach, hashes = sources()
    spec = t1.load_candidate_spec(REPO)
    return t1.T1Simulator(
        t1.candidate_policy(REPO, spec, candidate),
        boundary=boundary(),
        atlas=atlas,
        guidebook=guidebook,
        recut=recut,
        taker_reach=reach,
        source_hashes=hashes,
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


def test_candidate_family_exactly_eight_and_switches_frozen() -> None:
    spec = t1.load_candidate_spec(REPO)
    assert tuple(spec["candidate_ids"]) == t1.CANDIDATES
    assert len(spec["candidate_ids"]) == 8
    assert spec["free_numeric_parameters"] == []
    assert spec["candidate_additions_after_freeze_allowed"] is False


def test_post_fill_arming_and_strictly_later_response() -> None:
    result = run(
        "w1_t1__macro_hold__response_only",
        [trade(1100, 70, 1, "same"), trade(1200, 70, 1, "later")],
    )
    armed = actions(result, "headroom_armed")
    decisions = actions(result, "t1_episode_keyed_decision")
    assert len(armed) == 1
    assert decisions
    assert all(row["ts"] > 1100 for row in decisions)
    assert not any(row.get("trigger_receipt") == "same" for row in decisions)


def test_new_action_cannot_fill_on_its_trigger_receipt() -> None:
    result = run(
        "w1_t1__macro_hold__response_only",
        [trade(1200, 70, 1, "trigger")],
    )
    decision = next(
        row for row in actions(result, "t1_episode_keyed_decision")
        if row["trigger_receipt"] == "trigger"
    )
    assert decision["new_action_fill_eligible_on_trigger_receipt"] is False
    assert not any(
        row["ts"] == 1200
        and row["leg_id"] == "BBB"
        and row["action"] in {
            "price_reached_policy_tape", "strict_ask_certain_fill"
        }
        for row in result["order_stream"]
    )


def test_positive_d2_combined_headroom_target_is_lawful() -> None:
    value = t1.construct_headroom_target(
        bid=40, ask=45, d1=-7, b2_max=6, fee=0,
        existing_raw_target=38,
    )
    assert value["selected_X_cents"] == 41
    assert value["selected_d2_cents"] == 1
    assert value["strict_combined_negative"] is True


def test_exact_target_formula_and_integer_arithmetic() -> None:
    assert t1.construct_headroom_target(
        bid=40, ask=41, d1=-3, b2_max=2, fee=0,
        existing_raw_target=None,
    )["X_headroom_cents"] == 40
    assert t1.construct_headroom_target(
        bid=40, ask=50, d1=1, b2_max=-2, fee=0,
        existing_raw_target=None,
    )["X_headroom_cents"] == 38
    with pytest.raises(t1.T1Error):
        t1.construct_headroom_target(
            bid=40.9, ask=50, d1=-3, b2_max=2, fee=0,
            existing_raw_target=None,
        )


def test_missing_BBO_is_NO_CALL_and_print_is_not_substituted() -> None:
    sim = simulator("w1_t1__macro_hold__target_completeness_only")
    state = {
        "current_book": book(1200, None, None, "empty"),
        "headroom_d1_cents": -5,
        "headroom_b2_max_cents": 4,
    }
    assert sim._current_target_construction(
        state, existing_raw_target=40
    ) is None


def test_one_active_five_contract_sibling_order() -> None:
    result = run(
        "w1_t1__macro_hold__full_stack",
        [trade(1200, 70, 1, "b1"), trade(1250, 70, 1, "b2")],
    )
    intervals = result["order_intervals_by_leg"]["BBB"]
    for timestamp in (1200, 1250):
        active = [
            row for row in intervals
            if row["opened_ts"] <= timestamp
            and (row["closed_ts"] is None or row["closed_ts"] >= timestamp)
        ]
        assert len(active) <= 1


def test_strict_ask_credit_precedes_T1_cancel_or_reprice() -> None:
    result = run(
        "w1_t1__macro_hold__full_stack",
        [book(1200, 58, 59, "strict")],
    )
    at_time = [
        row for row in result["order_stream"]
        if row["leg_id"] == "BBB" and row["ts"] == 1200
    ]
    assert any(row["action"] == "strict_ask_certain_fill" for row in at_time)
    assert not any(row["action"] in {"cancel", "reprice"} for row in at_time)


def test_persistence_holds_lawful_price_despite_headroom_suggestion() -> None:
    result = run(
        "w1_t1__macro_hold__persistence_only",
        [trade(1200, 70, 1, "headroom")],
    )
    holds = actions(result, "t1_persistence_hold")
    assert holds
    assert holds[0]["price_cents"] == 60
    assert holds[0]["proposed_replacement_X_cents"] == 61
    assert holds[0]["queue_preserved"] is True


def test_guarded_cutoff_overrides_shorter_post_fill_horizon() -> None:
    result = run(
        "w1_t1__macro_hold__persistence_only",
        [book(1400, 60, 70, "after-short-horizon")],
    )
    assert result["policy_clock"]["baseline_policy_decision_horizon_ts"] == 1300
    assert result["policy_clock"]["post_first_terminal_ts"] == 1500
    assert any(
        row.get("decision")
        == "EXTEND_SIBLING_PERSISTENCE_TO_GUARDED_CUTOFF"
        for rows in result["t1_persistence_receipts_by_leg"].values()
        for row in rows
    )


def test_maker_unsafe_change_has_receipt_backed_reason() -> None:
    result = run(
        "w1_t1__macro_hold__persistence_only",
        [book(1200, 58, 60, "equal-ask")],
    )
    assert any(
        row["action"] in {"cancel", "reprice"}
        and row["ts"] == 1200
        and row["reason"].startswith("maker_safety_external_ask_move")
        for row in result["order_stream"]
    )


def test_no_IC_or_S_gate_in_source() -> None:
    tree = ast.parse((REPO / t1.__file__).read_text(encoding="utf-8"))
    names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    assert "IC" not in names
    assert "S" not in names
    assert t1.construct_headroom_target(
        bid=70, ask=75, d1=-7, b2_max=6, fee=0,
        existing_raw_target=72,
    )["selected_X_cents"] == 71


def test_metrics_null_and_forbidden_imports() -> None:
    source = (REPO / freeze.BUILDER_REL).read_text(encoding="utf-8")
    assert "window1_range_attack_scorer" not in source
    assert "window1_range_attack_scoring" not in source
    spec = json.loads((REPO / freeze.SPEC_REL).read_text(encoding="utf-8"))
    freeze.assert_metrics_null(spec)


def test_full_package_fixture_counts_when_frozen() -> None:
    path = PACKAGE / "CAUSAL_FIXTURE_MIGRATION_RECEIPT.json"
    if not path.exists():
        pytest.skip("full T1 package not frozen during unit phase")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert receipt["variant_acceptance_counts"] == {
        "capacity_unproved": 2,
        "persistence_fixture_variant_rows_passed": 34,
        "response_fixture_variant_rows_passed": 48,
        "target_fixture_variant_rows_passed": 8,
    }


def test_D_first_leg_nofill_and_five_no_BBO_when_frozen() -> None:
    path = PACKAGE / "D_CONSERVATION_RECEIPT.json"
    if not path.exists():
        pytest.skip("full T1 package not frozen during unit phase")
    d = json.loads(path.read_text(encoding="utf-8"))
    assert set(d["D_per_candidate"].values()) == {804}
    first = json.loads(
        (PACKAGE / "FIRST_LEG_SEMANTIC_IDENTITY_RECEIPT.json").read_text()
    )
    nofill = json.loads(
        (PACKAGE / "NOFILL_SEMANTIC_IDENTITY_RECEIPT.json").read_text()
    )
    five = json.loads(
        (PACKAGE / "FIVE_NO_BBO_D_MEMBERSHIP_PROOF.json").read_text()
    )
    assert first["mismatch_count"] == 0
    assert nofill["mismatch_count"] == 0
    assert five["row_count"] == 40
    assert five["all_zero_orders"] is True


def test_artifact_hashes_and_determinism_when_frozen() -> None:
    path = PACKAGE / "ARTIFACT_HASH_MANIFEST.json"
    if not path.exists():
        pytest.skip("full T1 package not frozen during unit phase")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for row in manifest["artifacts"]:
        artifact = PACKAGE / row["path"]
        assert artifact.stat().st_size == row["bytes"]
        assert freeze.sha256_file(artifact) == row["sha256"]
    deterministic = json.loads(
        (PACKAGE / "DETERMINISTIC_REGENERATION_RECEIPT.json").read_text()
    )
    assert deterministic["clean_regeneration_count"] == 2
    assert deterministic["byte_identical"] is True


def test_all_gzip_rows_keep_performance_null_when_frozen() -> None:
    if not PACKAGE.exists():
        pytest.skip("full T1 package not frozen during unit phase")
    for path in PACKAGE.glob("*.jsonl.gz"):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                freeze.assert_metrics_null(json.loads(line))

