"""Production-path contracts for the narrow strict-ask V2 overlay."""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
ANALYSIS = REPO / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import window1_range_attack_instrument_v2 as attack  # noqa: E402
import window1_range_attack_prerun_builder_v2_strict_ask as builder  # noqa: E402


CANDIDATE = "w1_range_attack__macro_hold__combined_headroom"
ARTIFACT = REPO / ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"


def book(ts: float, bid: int, ask: int, receipt: str) -> dict:
    return {
        "kind": "book",
        "ts": ts,
        "receipt_id": receipt,
        "source_receipt_identity": receipt,
        "bids": [[bid, 1.0], [bid - 1, 2.0]],
        "asks": [[ask, 1.0], [ask + 1, 2.0]],
        "last_trade_cents": bid,
        "last_trade_provenance": attack.CARRIED_UNKNOWN,
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


def event(a: list[dict], b: list[dict]) -> dict:
    return {
        "event_id": "KXATPCHALLENGERMATCH-26JUL12TESTAA",
        "event_date": "2026-07-12",
        "category": "ATP_CHALL",
        "policy_anchor_ts": 9000.0,
        "policy_anchor_observed_at_ts": 500.0,
        "policy_anchor_source": "timestamped_schedule_snapshot",
        "policy_left_ts": 900.0,
        "policy_decision_horizon_ts": 9000.0,
        "legs": [
            {"leg_id": "AAA", "ticker": "TEST-AA",
             "feature_availability": {}, "observations": a},
            {"leg_id": "BBB", "ticker": "TEST-BB",
             "feature_availability": {}, "observations": b},
        ],
    }


def simulator() -> attack.RangeAttackSimulator:
    spec = attack.load_candidate_spec(REPO)
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
    return attack.RangeAttackSimulator(
        attack.candidate_policy(spec, CANDIDATE),
        atlas=atlas,
        guidebook={"pages": {}},
        recut={},
        taker_reach={"law": {}},
        source_hashes={"atlas": "a" * 64},
    )


def run(a_tail: list[dict], b_tail: list[dict] | None = None) -> dict:
    a = [book(1000, 40, 50, "a0"), *a_tail]
    b = [book(1000, 60, 70, "b0"), *(b_tail or [])]
    return simulator().run(event(a, b))


def fill_actions(result: dict, leg_id: str = "AAA") -> list[dict]:
    return [
        row for row in result["order_stream"]
        if row["leg_id"] == leg_id
        and row["action"] in {
            "strict_ask_certain_fill", "price_reached_policy_tape"
        }
    ]


def test_strict_ask_below_x_credits_five_at_original_x() -> None:
    result = run([book(1100, 38, 39, "a1")])
    fill = result["causal_policy_fill_state_by_leg"]["AAA"]
    assert fill["simulated_accounting_quantity"] == 5
    assert fill["simulated_fill_price"] == 40
    assert fill["simulated_fill_evidence_type"] == "STRICT_ASK_CERTAIN_FILL"
    assert fill["simulated_fill_external_ask_cents"] == 39


def test_credit_precedes_and_suppresses_maker_safety() -> None:
    result = run([book(1100, 38, 39, "a1")])
    at_ts = [
        row for row in result["order_stream"]
        if row["leg_id"] == "AAA" and row["ts"] == 1100
    ]
    assert any(row["action"] == "strict_ask_certain_fill" for row in at_ts)
    assert not any(
        row["reason"].startswith("maker_safety_external_ask_move")
        for row in at_ts
    )


def test_ask_equal_x_is_context_only_not_auto_credit() -> None:
    result = run([book(1100, 38, 40, "a1")])
    fill = result["causal_policy_fill_state_by_leg"]["AAA"]
    assert fill["simulated_accounting_quantity"] == 0
    assert not fill_actions(result)


def test_print_exactly_at_x_credits_price_reached() -> None:
    result = run([trade(1100, 40, 1.0, "p1")])
    fill = result["causal_policy_fill_state_by_leg"]["AAA"]
    assert fill["simulated_accounting_quantity"] == 5
    assert fill["simulated_fill_evidence_type"] == "PRICE_REACHED"
    assert fill_actions(result)[0]["action"] == "price_reached_policy_tape"


def test_sub_five_print_volume_still_credits() -> None:
    result = run([trade(1100, 40, 0.25, "p1")])
    action = fill_actions(result)[0]
    assert action["simulated_accounting_quantity"] == 5
    assert action["print_size"] == 0.25
    assert action["cumulative_five_required"] is False


def test_same_timestamp_book_and_print_assign_once_at_original_x() -> None:
    result = run([
        book(1100, 39, 40, "a-equal-first"),
        book(1100, 38, 39, "a1"),
        trade(1100, 39, 1.0, "p1"),
    ])
    fills = fill_actions(result)
    assert len(fills) == 1
    assert fills[0]["action"] == "strict_ask_certain_fill"
    assert fills[0]["limit_price_cents"] == 40


def test_strict_ask_first_fill_arms_later_sibling_headroom() -> None:
    result = run(
        [book(1100, 45, 39, "a1")],
        [trade(1200, 70, 1.0, "bp1")],
    )
    armed = [
        row for row in result["order_stream"]
        if row["action"] == "headroom_armed"
    ]
    decisions = [
        row for row in result["order_stream"]
        if row["action"] == "headroom_decision"
    ]
    assert len(armed) == 1
    assert armed[0]["first_fill_evidence_type"] == "STRICT_ASK_CERTAIN_FILL"
    assert armed[0]["d1_cents"] == -5
    assert armed[0]["b2_max_cents"] == 4
    assert decisions and decisions[0]["ts"] == 1200


def test_no_same_timestamp_sibling_headroom_action() -> None:
    result = run(
        [book(1100, 45, 39, "a1")],
        [trade(1100, 70, 1.0, "bp0"),
         trade(1200, 70, 1.0, "bp1")],
    )
    decisions = [
        row for row in result["order_stream"]
        if row["action"] == "headroom_decision"
    ]
    assert decisions
    assert all(row["ts"] > 1100 for row in decisions)


def test_evaluator_uses_union_and_equal_ask_does_not_credit() -> None:
    boundary = {
        "positive_window1_provable": True,
        "guarded_cutoff_ts": 2000.0,
    }
    base_event = event([], [])
    interval = {
        "order_interval_id": "x",
        "opened_ts": 1000.0,
        "closed_ts": 1500.0,
        "limit_price_cents": 40,
    }
    strict = builder.evaluate_interval(
        candidate_id=CANDIDATE, event=base_event,
        leg={"leg_id": "AAA", "ticker": "T",
             "observations": [book(1100, 38, 39, "b")]},
        interval=interval, boundary=boundary, taker_reach={"law": {}},
    )
    equal = builder.evaluate_interval(
        candidate_id=CANDIDATE, event=base_event,
        leg={"leg_id": "AAA", "ticker": "T",
             "observations": [book(1100, 38, 40, "b")]},
        interval=interval, boundary=boundary, taker_reach={"law": {}},
    )
    assert strict["FILLABLE_AT_X"] is True
    assert strict["accounting_quantity_if_later_scored"] == 5
    assert equal["FILLABLE_AT_X"] is False
    assert equal["EXACT_TOUCH"] is True


def test_all_26_audited_rows_have_committed_migrations() -> None:
    path = ARTIFACT / "STRICT_ASK_V1_TO_V2_MIGRATION_RECEIPT.json"
    if not path.exists():
        pytest.skip("full frozen migration artifact generated after unit phase")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert receipt["audited_row_count"] == 26
    assert receipt["migrated_row_count"] == 26
    assert receipt["maker_safety_evasions_removed"] == 26
    assert receipt["audited_first_fill_position_count"] == 20
    assert all(row["V2_accounting_state"]["credited_quantity"] == 5
               for row in receipt["rows"])
