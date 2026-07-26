"""Focused contracts for the score-free Window-1 range-attack freeze."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
ANALYSIS = REPO / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

import window1_range_attack_instrument as attack  # noqa: E402
import window1_range_attack_prerun_builder as builder  # noqa: E402


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


def trade(
    ts: float, price: int, size: float, receipt: str,
    taker_side: str = "no",
) -> dict:
    return {
        "kind": "print",
        "ts": ts,
        "price": price,
        "size": size,
        "trade_id": receipt,
        "receipt_id": receipt,
        "source_receipt_identity": receipt,
        "taker_side": taker_side,
        "own_order_fingerprint": False,
        "size_verified": True,
        "source": "normalized_public_true_print",
    }


def event(observations_a: list[dict], observations_b: list[dict]) -> dict:
    return {
        "event_id": "KXATPCHALLENGERMATCH-26JUL12TESTAA",
        "event_date": "2026-07-12",
        "category": "ATP_CHALL",
        "policy_anchor_ts": 9000.0,
        "policy_anchor_observed_at_ts": 500.0,
        "policy_anchor_source": "timestamped_schedule_snapshot",
        "policy_left_ts": 1000.0,
        "policy_decision_horizon_ts": 9000.0,
        "legs": [
            {
                "leg_id": "AAA",
                "ticker": "TEST-AA",
                "feature_availability": {},
                "observations": observations_a,
            },
            {
                "leg_id": "BBB",
                "ticker": "TEST-BB",
                "feature_availability": {},
                "observations": observations_b,
            },
        ],
    }


def sources() -> tuple[dict, dict, dict, dict, dict]:
    atlas = {
        "pages": {
            "ATP_CHALL|underdog|26_50": {
                "verdict": "PATH",
                "n": 44,
                "branded": "g9",
                "bottom": {"depth_p50": 5, "t_deep_p50_min": 40},
            },
            "ATP_CHALL|leader|51_75": {
                "verdict": "PATH",
                "n": 44,
                "branded": "g9",
                "bottom": {"depth_p50": 5, "t_deep_p50_min": 40},
            },
        }
    }
    guidebook = {
        "pages": {
            "ATP_CHALL|40": {"depth_p25_of_w1s": 8},
            "ATP_CHALL|60": {"depth_p25_of_w1s": 8},
        }
    }
    recut = {"ATP_CHALL": {"40": {"edge_p50": 2}}}
    reach = {"law": {}}
    hashes = {"atlas": "a" * 64}
    return atlas, guidebook, recut, reach, hashes


def simulator(candidate: str) -> attack.RangeAttackSimulator:
    atlas, guidebook, recut, reach, hashes = sources()
    spec = attack.load_candidate_spec(REPO)
    return attack.RangeAttackSimulator(
        attack.candidate_policy(spec, candidate),
        atlas=atlas,
        guidebook=guidebook,
        recut=recut,
        taker_reach=reach,
        source_hashes=hashes,
    )


def boundary(cutoff: float = 9000.0) -> dict:
    return {
        "event_id": "KXATPCHALLENGERMATCH-26JUL12TESTAA",
        "start_source_class": "official_exact",
        "positive_window1_provable": True,
        "guard_seconds": 60,
        "guarded_cutoff_ts": cutoff,
        "boundary_law": "fixture",
        "guard_id": "fixture",
        "conflict_status": "none",
        "guard_censor_reason": None,
        "schedule_can_prove_positive": False,
        "source_record_sha256": "b" * 64,
    }


def interval(price: int = 40) -> dict:
    return {
        "order_interval_id": "fixture-1",
        "opened_ts": 1100.0,
        "closed_ts": 2000.0,
        "limit_price_cents": price,
    }


def leg(observations: list[dict]) -> dict:
    return {
        "leg_id": "AAA",
        "ticker": "TEST-AA",
        "observations": observations,
    }


def test_candidate_family_is_exactly_two_and_frozen() -> None:
    spec = attack.load_candidate_spec(REPO)
    assert spec["candidate_ids"] == [
        "w1_range_attack__macro_hold__combined_headroom",
        "w1_range_attack__macro_micro__combined_headroom",
    ]
    assert spec["free_numeric_parameters"] == []
    assert spec["candidate_additions_after_freeze_allowed"] is False


def test_one_contract_touch_is_primary_price_reached() -> None:
    row = builder.evaluate_interval(
        candidate_id="fixture",
        event=event([], []),
        leg=leg([
            book(1100, 39, 41, "b1"),
            trade(1200, 40, 1.0, "p1"),
        ]),
        interval=interval(),
        boundary=boundary(),
        taker_reach={"law": {}},
    )
    assert row["PRICE_REACHED"] is True
    assert row["accounting_quantity_if_later_scored"] == 5
    assert row["cumulative_size_five_would_false_negative"] is True
    assert row["cumulative_printed_size_required"] is False


def test_exact_touch_and_strict_trade_through_are_distinct() -> None:
    exact = builder.evaluate_interval(
        candidate_id="fixture",
        event=event([], []),
        leg=leg([book(1100, 39, 40, "b1"), trade(1200, 40, 1, "p1")]),
        interval=interval(),
        boundary=boundary(),
        taker_reach={"law": {}},
    )
    strict = builder.evaluate_interval(
        candidate_id="fixture",
        event=event([], []),
        leg=leg([book(1100, 38, 41, "b1"), trade(1200, 39, 1, "p1")]),
        interval=interval(),
        boundary=boundary(),
        taker_reach={"law": {}},
    )
    assert exact["EXACT_TOUCH"] and not exact["CERTAIN_FILL"]
    assert strict["PRICE_REACHED"] and strict["CERTAIN_FILL"]


def test_unknown_queue_and_display_lt_five_do_not_block_reach() -> None:
    row = builder.evaluate_interval(
        candidate_id="fixture",
        event=event([], []),
        leg=leg([book(1100, 40, 42, "b1"), trade(1200, 40, .25, "p1")]),
        interval=interval(),
        boundary=boundary(),
        taker_reach={"law": {}},
    )
    assert row["PRICE_REACHED"]
    assert row["queue_clearance_required"] is False
    assert row["displayed_depth_five_required"] is False
    assert row["single_five_print_required"] is False


def test_schedule_only_cannot_prove_positive() -> None:
    no_proof = boundary()
    no_proof.update({
        "start_source_class": "schedule_only",
        "positive_window1_provable": False,
        "guard_seconds": None,
        "guarded_cutoff_ts": None,
        "schedule_can_prove_positive": False,
    })
    row = builder.evaluate_interval(
        candidate_id="fixture",
        event=event([], []),
        leg=leg([trade(1200, 1, 100, "p1")]),
        interval=interval(),
        boundary=no_proof,
        taker_reach={"law": {}},
    )
    assert row["PRICE_REACHED"] is False
    assert row["accounting_quantity_if_later_scored"] == 0


def test_guarded_cutoff_excludes_later_touch() -> None:
    row = builder.evaluate_interval(
        candidate_id="fixture",
        event=event([], []),
        leg=leg([trade(1200, 40, 10, "p1")]),
        interval=interval(),
        boundary=boundary(1150),
        taker_reach={"law": {}},
    )
    assert row["PRICE_REACHED"] is False


def test_strict_pair_headroom_arithmetic() -> None:
    assert attack.headroom_b2_max(-7, 0) == 6
    assert attack.headroom_b2_max(1, 0) == -2
    assert attack.strict_pair_budget(-7, 6, 0)
    assert not attack.strict_pair_budget(-7, 7, 0)
    assert attack.strict_pair_budget(-7, 2, 0)


def test_liveaim_mapping_is_source_recorded_mapping() -> None:
    assert attack.liveaim_mapping(
        category="ATP_CHALL", print_count=16, signature="rising",
        depth_trend=-10, spread_cents=5,
    )["verdict"] == "NO_BID_CHASE_GUARD"
    assert attack.liveaim_mapping(
        category="ATP_CHALL", print_count=16, signature="falling",
        depth_trend=1, spread_cents=2,
    )["verdict"] == "AIM_DEEP"
    assert attack.liveaim_mapping(
        category="ITF_M", print_count=1, signature="flat",
        depth_trend=1, spread_cents=4,
    )["verdict"] == "AIM_SHALLOW"
    assert attack.liveaim_mapping(
        category="ATP_MAIN", print_count=100, signature="falling",
        depth_trend=-10, spread_cents=10,
    )["verdict"] == "GAUGE_OFF_AIM_PRIOR"


def test_policy_refuses_realized_start_oracle() -> None:
    fixture = event([], [])
    fixture["evaluation_real_start_ts"] = 5000.0
    with pytest.raises(attack.RangeAttackError, match="oracle"):
        simulator(
            "w1_range_attack__macro_hold__combined_headroom"
        ).run(fixture)


def test_policy_refuses_holdout() -> None:
    fixture = event([], [])
    fixture["event_date"] = "2026-07-24"
    with pytest.raises(attack.RangeAttackError, match="holdout"):
        simulator(
            "w1_range_attack__macro_hold__combined_headroom"
        ).run(fixture)


def test_no_bbo_yields_no_placement_and_named_no_call() -> None:
    result = simulator(
        "w1_range_attack__macro_hold__combined_headroom"
    ).run(event(
        [trade(1200, 40, 1, "a1")],
        [trade(1200, 60, 1, "b1")],
    ))
    actions = result["order_stream"]
    assert not any(row["action"] == "place" for row in actions)
    assert sum(
        row["action"] == "feature_no_call"
        and row["reason"] == "MARKET_EVIDENCE_NO_CALL"
        for row in actions
    ) == 2
    assert result["metrics"] is None


def test_target_freezes_and_does_not_follow_later_bid() -> None:
    first_hour_a = [
        book(1000, 38, 41, "ab0"),
        trade(1100, 40, 1, "ap0"),
        trade(2000, 40, 1, "ap1"),
        trade(3000, 40, 1, "ap2"),
        book(4800, 50, 52, "ab1"),
        book(5000, 60, 62, "ab2"),
    ]
    first_hour_b = [
        book(1000, 58, 61, "bb0"),
        trade(1100, 60, 1, "bp0"),
        trade(2000, 60, 1, "bp1"),
        trade(3000, 60, 1, "bp2"),
        book(4800, 55, 58, "bb1"),
    ]
    result = simulator(
        "w1_range_attack__macro_hold__combined_headroom"
    ).run(event(first_hour_a, first_hour_b))
    aaa = [
        row for row in result["order_stream"]
        if row["leg_id"] == "AAA"
    ]
    selections = [
        row for row in aaa if row["action"] == "macro_target_selected"
    ]
    assert selections
    assert selections[0]["target_raw_cents"] == 35
    assert not any(
        row["action"] == "reprice"
        and row.get("reprice_direction") == "UP"
        and row["primary_authority"] != "CAUSAL_PAIR_HEADROOM"
        for row in aaa
    )


def test_policy_output_is_byte_deterministic_and_metrics_null() -> None:
    fixture = event(
        [book(1000, 38, 41, "ab0"), trade(1200, 38, 1, "ap0")],
        [book(1000, 58, 61, "bb0"), trade(1200, 58, 1, "bp0")],
    )
    candidate = "w1_range_attack__macro_hold__combined_headroom"
    left = simulator(candidate).run(fixture)
    right = simulator(candidate).run(fixture)
    assert attack.compact(left) == attack.compact(right)
    assert left["metrics"] is None
    assert left["pair_state"]["C"] is None
    assert left["pair_state"]["PC"] is None
    assert left["pair_state"]["S"] is None
    assert left["pair_state"]["IC"] is None


def test_blocked_strategy_and_quarantine_modules_are_not_imported() -> None:
    source = (ANALYSIS / "window1_range_attack_instrument.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "window1_round4_macromicro_instrument_v2" not in imports
    assert "window1_round4_macromicro_prerun_builder_v2" not in imports
    assert "window1_round4_macromicro_instrument" in imports


def test_candidate_spec_contains_no_combined_cost_or_ic_gate() -> None:
    text = (
        REPO / attack.CANDIDATE_SPEC_PATH
    ).read_text(encoding="utf-8")
    assert "first_fill_sibling_max_combined_cost_cents" not in text
    assert "maximum_pair_order_cost_cents" not in text
    spec = json.loads(text)
    assert spec["combined_headroom_contract"]["IC_gate"] is False
    assert spec["combined_headroom_contract"]["S_gate"] is False


def test_source_has_no_universal_50_climb_or_moving_bid_edge() -> None:
    source = (ANALYSIS / "window1_range_attack_instrument.py").read_text(
        encoding="utf-8"
    )
    assert "current external bid - edge_p50" not in source
    assert "current_bid_minus_edge" not in source
    assert "last_trade<=bid" not in source
    assert "last_trade>=bid" not in source


def test_boundary_contract_uses_frozen_guard_classes() -> None:
    official = builder.boundary_contract({
        "event_id": "x",
        "start_source_class": "official_exact",
        "positive_window1_provable": True,
        "exact_start_utc": "2026-07-12T12:00:00+00:00",
        "guard_band": {"guard_id": "o"},
        "conflict_status": "none",
        "schedule_can_prove_positive": False,
    })
    proxy = builder.boundary_contract({
        "event_id": "y",
        "start_source_class": "quantized_late_detection_proxy",
        "positive_window1_provable": True,
        "guard_band": {
            "guard_id": "p",
            "strict_window1_completion_lte_utc":
                "2026-07-12T11:45:00+00:00",
        },
        "conflict_status": "none",
        "schedule_can_prove_positive": False,
    })
    assert official["guard_seconds"] == 60
    assert proxy["guard_seconds"] == 900
    assert official["guarded_cutoff_ts"] > proxy["guarded_cutoff_ts"]


def test_quarantined_draft_hash_fixture_is_not_modified_by_tests() -> None:
    expected = {
        "window1_round4_macromicro_instrument_v2.py":
            "7191339fa68431479e023b9070402503389ee08a42d9ba10adf4ba25ed7df517",
        "window1_round4_macromicro_prerun_builder_v2.py":
            "15cb9e67cf0394c649eb4e621a99323d6a29cd885e3c4a97478b472e2592dfc5",
    }
    for name, digest in expected.items():
        path = ANALYSIS / name
        if path.exists():
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
