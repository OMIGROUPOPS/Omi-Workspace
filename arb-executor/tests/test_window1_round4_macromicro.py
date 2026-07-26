from __future__ import annotations

import copy
import gzip
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round2_capability_proof as proof  # noqa: E402
import window1_round3_prerun_builder as r3builder  # noqa: E402
import window1_round4_macromicro_instrument as r4m  # noqa: E402


BASE = "r4m_climb_decay__last_trade_chain__causal_headroom"
FLOW = "r4m_climb_decay__last_trade_chain_flow__causal_headroom"
OUTPUT = ROOT / ".claude/window1_round4_macromicro_prerun_20260725"


def run(event: dict, candidate: str = BASE) -> dict:
    r3builder.bind_round3_book_receipts(event)
    spec = r4m.load_candidate_spec(ROOT)
    return r4m.Round4MacroMicroInstrument(
        proof.synthetic_surfaces(),
        r4m.candidate_policy(spec, candidate),
        atlas={},
        source_receipts={"recut": "r" * 64},
    ).run(event)


def test_exact_frozen_candidate_allowlist_and_no_free_grid():
    spec = r4m.load_candidate_spec(ROOT)
    assert spec["candidate_ids"] == [BASE, FLOW]
    assert spec["free_numeric_parameters"] == []
    assert spec["benchmark_execution_authorized"] is False
    assert spec["performance_metrics"] is None


def test_last_trade_preservation_has_honest_carried_provenance():
    normalized = {
        "policy_left_ts": 10.0,
        "policy_decision_horizon_ts": 20.0,
        "legs": [{
            "ticker": "A",
            "observations": [{
                "kind": "book", "ts": 12.0,
                "bids": [[40, 2]], "asks": [[42, 3]],
            }],
        }],
    }
    cache = {"legs": [{
        "ticker": "A",
        "snapshots": [{
            "ts": 12.0, "last_trade": 41,
            "bids": [[40, 2]], "asks": [[42, 3]],
        }],
        "prints": [],
    }]}
    census = r4m.preserve_last_trade(normalized, cache)
    book = normalized["legs"][0]["observations"][0]
    assert book["last_trade_cents"] == 41
    assert book["last_trade_observed_at"] == 12.0
    assert book["last_trade_execution_at"] is None
    assert book["last_trade_provenance"] == r4m.CARRIED_UNKNOWN
    assert book["last_trade_is_fill_volume"] is False
    assert census["last_trade_created_print_count"] == 0


def test_last_trade_can_bind_a_real_prior_print_timestamp():
    normalized = {
        "policy_left_ts": 10.0,
        "policy_decision_horizon_ts": 20.0,
        "legs": [{
            "ticker": "A",
            "observations": [{
                "kind": "book", "ts": 14.0,
                "bids": [[40, 2]], "asks": [[42, 3]],
            }],
        }],
    }
    cache = {"legs": [{
        "ticker": "A",
        "snapshots": [{
            "ts": 14.0, "last_trade": 41,
            "bids": [[40, 2]], "asks": [[42, 3]],
        }],
        "prints": [{
            "ts": 13.0, "price": 41, "size": 1,
            "trade_id": "t1", "taker_side": "yes",
        }],
    }]}
    census = r4m.preserve_last_trade(normalized, cache)
    book = normalized["legs"][0]["observations"][0]
    assert book["last_trade_execution_at"] == 13.0
    assert book["last_trade_provenance"] == r4m.VERIFIED_PRINT
    assert census["verified_print_timestamp_count"] == 1


def test_last_trade_never_substitutes_for_missing_bbo():
    event = proof.base_event()
    for leg in event["legs"]:
        leg["observations"] = [{
            "kind": "book", "ts": event["policy_left_ts"] + 1,
            "bids": [], "asks": [], "last_trade_cents": 50,
            "last_trade_observed_at": event["policy_left_ts"] + 1,
            "last_trade_execution_at": None,
            "last_trade_provenance": r4m.CARRIED_UNKNOWN,
            "source_receipt_identity": leg["leg_id"] + "|book",
        }]
    result = run(event)
    assert not any(
        row["action"] == "place" for row in result["order_stream"]
    )


def test_role_swap_cannot_select_macro_posture_or_price():
    event = proof.base_event()
    before = run(copy.deepcopy(event))
    for leg in event["legs"]:
        leg["role"] = (
            "underdog" if leg["role"] == "favorite" else "favorite"
        )
    after = run(event)
    select = lambda result: [
        (row["leg_id"], row["action"], row.get("price_cents"),
         row.get("posture"))
        for row in result["order_stream"]
        if row["action"] in {"place", "reprice", "cancel"}
    ]
    assert select(before) == select(after)


def test_coherent_pair_read_precedes_both_initial_placements():
    result = run(proof.base_event())
    actions = result["order_stream"]
    compose_ts = {
        row["ts"] for row in actions
        if row["action"] == "pair_macro_micro_compose"
    }
    places = [row for row in actions if row["action"] == "place"]
    assert len(compose_ts) == 1
    assert len(places) == 2
    assert all(row["ts"] >= min(compose_ts) for row in places)
    assert len({
        row["pair_decision_receipt"]["pair_read_id"] for row in places
    }) == 1


def test_every_order_decision_has_macro_micro_and_pair_receipts():
    result = run(proof.base_event(), FLOW)
    decisions = [
        row for row in result["order_stream"]
        if row["action"] in {"place", "reprice", "cancel"}
    ]
    assert decisions
    assert all(
        row["composed_macro_micro"] is True
        and row["macro_decision_receipt"]
        and row["micro_decision_receipt"]
        and row["pair_decision_receipt"]
        for row in decisions
    )


def test_fitted_cell_edge_changes_target_without_midpoint():
    spec = r4m.load_candidate_spec(ROOT)
    instance = r4m.Round4MacroMicroInstrument(
        proof.synthetic_surfaces(),
        r4m.candidate_policy(spec, BASE),
        atlas={},
    )
    state = {
        "current_book": {
            "bids": [[60, 5]], "asks": [[64, 5]],
            "own_bid_size_by_price": {},
        },
        "macro_edge_p50_cents": 1,
        "sibling_bias_cents": 0,
    }
    assert instance._target_price(state) == 59
    state["macro_edge_p50_cents"] = 3
    assert instance._target_price(state) == 57
    assert instance._target_price(state) != 62


def test_last_trade_and_top5_perturbations_change_flow_confirmation():
    spec = r4m.load_candidate_spec(ROOT)
    instance = r4m.Round4MacroMicroInstrument(
        proof.synthetic_surfaces(),
        r4m.candidate_policy(spec, FLOW),
        atlas={},
    )
    instance.left = 0.0
    instance.event = {"category": "ATP_MAIN"}
    state = {
        "actions": [], "event_id": "E", "candidate_id": FLOW,
        "leg_id": "A", "ticker": "A", "macro_side": "CLIMB_SIDE",
        "last_trade_no_call_emitted": False,
        "top5_no_call_emitted": False,
        "last_positive_print_taker_side": "no",
        "current_book": {
            "ts": 1.0, "last_trade_cents": 59,
            "chain_state": {
                "nonself_best_bid_cents": 60,
                "top5_bids": [[60, 10]], "top5_asks": [[62, 1]],
                "top5_pressure_sign": "BID",
            },
        },
    }
    assert instance._book_micro_allows_reprice(state)[0] is True
    state["current_book"]["last_trade_cents"] = 61
    assert instance._book_micro_allows_reprice(state)[0] is False
    state["current_book"]["last_trade_cents"] = 59
    state["current_book"]["chain_state"]["top5_pressure_sign"] = "ASK"
    assert instance._book_micro_allows_reprice(state)[0] is False


def test_missing_optional_top5_is_named_no_call_not_censor():
    spec = r4m.load_candidate_spec(ROOT)
    instance = r4m.Round4MacroMicroInstrument(
        proof.synthetic_surfaces(),
        r4m.candidate_policy(spec, FLOW),
        atlas={},
    )
    instance.left = 0.0
    instance.event = {"category": "ATP_MAIN"}
    state = {
        "actions": [], "event_id": "E", "candidate_id": FLOW,
        "leg_id": "A", "ticker": "A", "macro_side": "CLIMB_SIDE",
        "last_trade_no_call_emitted": False,
        "top5_no_call_emitted": False,
        "last_positive_print_taker_side": None,
        "current_book": {
            "ts": 1.0, "last_trade_cents": 59,
            "chain_state": {
                "nonself_best_bid_cents": 60,
                "top5_bids": [], "top5_asks": [],
            },
        },
    }
    allowed, reason = instance._book_micro_allows_reprice(state)
    assert allowed is True
    assert reason == "top5_no_call_base_chain"
    assert state["actions"][-1]["reason"] == r4m.TOP5_NO_CALL


def test_headroom_and_primary_fill_laws_are_inherited_unchanged():
    assert r4m.v2.headroom_b2_max(-7, 0) == 6
    assert r4m.v2.strict_pair_budget(-7, 6, 0) is True
    assert r4m.v2.strict_pair_budget(-7, 7, 0) is False
    spec = r4m.load_candidate_spec(ROOT)
    assert spec["fill_contract"]["queue_clearance_gate"] is False
    assert spec["headroom_contract"]["IC_gate"] is False
    assert spec["headroom_contract"]["S_gate"] is False


def test_prerun_artifacts_are_unscored_and_conserve_population():
    if not OUTPUT.exists():
        return
    capability = json.loads(
        (OUTPUT / "ROUND4_MACROMICRO_REAL_CAPABILITY.json").read_text()
    )
    assert capability["D"] == 804
    assert capability["candidate_event_stream_count"] == 1608
    assert capability["all_metrics_null"] is True
    rows = []
    for path in sorted(OUTPUT.glob(
        "FROZEN_MACROMICRO_CANDIDATE_EVENT_STREAMS_*.jsonl.gz"
    )):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            rows.extend(
                json.loads(line) for line in handle if line.strip()
            )
    assert len(rows) == 1608
    assert all(
        row["stream"]["metrics"] is None
        and row["stream"]["scored"] is False
        for row in rows
    )
