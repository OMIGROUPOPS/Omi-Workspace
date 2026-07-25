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
import window1_round4_instrument as v1  # noqa: E402
import window1_round4_instrument_v2 as v2  # noqa: E402


PAIR = "r4_pair_presence__park_join__causal_headroom_ladder"
FULL = "r4_full_drift_stack__causal_headroom_ladder"
OUTPUT = ROOT / ".claude/window1_round4_prerun_v2_20260725"
NAMED_EVENTS = {
    "KXATPCHALLENGERMATCH-26JUL19KRUCAS",
    "KXATPCHALLENGERMATCH-26JUL20CREMAT",
    "KXWTAMATCH-26JUL13TAUTOM",
    "KXWTAMATCH-26JUL14PUTJEA",
    "KXWTAMATCH-26JUL20KUDKOR",
}


def atlas() -> dict:
    pages = {}
    for role in ("leader", "underdog"):
        for cell in ("le25", "26_50", "51_75", "ge75"):
            pages[f"ATP_MAIN|{role}|{cell}"] = {
                "n": 40,
                "bottom": {"depth_p50": 4, "t_med_min": 30},
            }
    return {"pages": pages}


def run(module, event: dict, candidate: str = PAIR) -> dict:
    r3builder.bind_round3_book_receipts(event)
    spec = module.load_candidate_spec(ROOT)
    instrument = (
        module.Round4Instrument
        if module is v1 else module.Round4InstrumentV2
    )
    return instrument(
        proof.synthetic_surfaces(),
        module.candidate_policy(spec, candidate),
        atlas=atlas(),
        source_receipts={"atlas": "a" * 64, "drift": "d" * 64},
    ).run(event)


def test_v2_exact_candidates_and_retired_fields_absent():
    spec = v2.load_candidate_spec(ROOT)
    assert spec["candidate_ids"] == [PAIR, FULL]
    assert not v2.FORBIDDEN_INERT_PARAMETERS.intersection(
        spec["common_parameters"]
    )
    for candidate in spec["candidate_ids"]:
        assert not v2.FORBIDDEN_INERT_PARAMETERS.intersection(
            v2.candidate_policy(spec, candidate)["parameters"]
        )


def test_missing_role_and_missing_bbo_are_nonterminal_named_no_calls():
    event = proof.base_event()
    for leg in event["legs"]:
        leg["feature_availability"]["causal_role"] = False
        leg["observations"] = []
    result = run(v2, event)
    actions = result["order_stream"]
    assert result["event_terminal"] == "complete_counterfactual_stream"
    assert sum(
        row["action"] == "feature_no_call"
        and row["reason"] == v2.CAUSAL_ROLE_NO_CALL
        for row in actions
    ) == 2
    assert sum(
        row["action"] == "feature_no_call"
        and row["reason"] == v2.MARKET_EVIDENCE_NO_CALL
        for row in actions
    ) == 2
    assert not any(row["action"] == "place" for row in actions)
    assert not any(row["action"] == "feature_censor" for row in actions)
    terminals = [
        row for row in actions if row["action"] == "terminal"
    ]
    assert len(terminals) == 2
    assert all(
        row["reason"] == "market_evidence_unavailable_no_call"
        and row["D_membership_continues"] is True
        for row in terminals
    )


def test_missing_role_with_lawful_bbo_uses_neutral_external_bid():
    event = proof.base_event()
    for leg in event["legs"]:
        leg["feature_availability"]["causal_role"] = False
    result = run(v2, event)
    first = {}
    for row in result["order_stream"]:
        if row["action"] == "place":
            first.setdefault(row["leg_id"], row)
    assert set(first) == {"A", "B"}
    assert first["A"]["price_cents"] == 59
    assert first["B"]["price_cents"] == 40
    assert all(
        row["posture"] == "join_external_best_bid"
        for row in first.values()
    )


def test_available_role_stream_remains_byte_identical_to_v1():
    event = proof.base_event()
    before = run(v1, copy.deepcopy(event))
    after = run(v2, copy.deepcopy(event))
    assert json.dumps(
        before, sort_keys=True, separators=(",", ":")
    ) == json.dumps(after, sort_keys=True, separators=(",", ":"))


def test_s_ic_and_combined_cost_never_gate():
    spec = v2.load_candidate_spec(ROOT)
    instance = v2.Round4InstrumentV2(
        proof.synthetic_surfaces(),
        v2.candidate_policy(spec, PAIR),
        atlas=atlas(),
    )
    state = {"active_order": {"price": 65}}
    sibling = {"active_order": {"price": 40}}
    instance.states = [state, sibling]
    passed, combined = instance._pair_cost_passes(state, 65)
    assert passed is True
    assert combined == 105
    assert spec["combined_entry_cost_is_diagnostic_only"] is True
    assert spec["individual_delta_is_diagnostic_only"] is True
    assert v2.strict_pair_budget(-7, 6, 0) is True
    assert v2.strict_pair_budget(-7, 7, 0) is False


def test_real_stream_identity_and_metrics_contract():
    receipt = json.loads(
        (
            OUTPUT / "ROUND4_V1_V2_STREAM_IDENTITY_RECEIPT.json"
        ).read_text(encoding="utf-8")
    )
    assert receipt["byte_identical_to_V1_count"] == 1598
    assert receipt["changed_from_V1_count"] == 10
    assert {
        row["event_id"] for row in receipt["changed_streams"]
    } == NAMED_EVENTS
    assert all(
        row["placement_count"] == 0
        and row["v2_event_terminal"] != "censored_feature"
        and row["metrics"] is None
        for row in receipt["changed_streams"]
    )
    with gzip.open(
        OUTPUT / "FROZEN_CANDIDATE_EVENT_STREAMS_V2.jsonl.gz",
        "rt",
        encoding="utf-8",
    ) as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    assert len(rows) == 1608
    assert all(
        row["stream"]["metrics"] is None
        and row["stream"]["scored"] is False
        for row in rows
    )


def test_five_real_events_have_no_orders_and_both_no_call_classes():
    selected = []
    with gzip.open(
        OUTPUT / "FROZEN_CANDIDATE_EVENT_STREAMS_V2.jsonl.gz",
        "rt",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            row = json.loads(line)
            if row["event_id"] in NAMED_EVENTS:
                selected.append(row)
    assert len(selected) == 10
    for wrapper in selected:
        actions = wrapper["stream"]["order_stream"]
        assert not any(row["action"] == "place" for row in actions)
        assert sum(
            row["action"] == "feature_no_call"
            and row["reason"] == v2.CAUSAL_ROLE_NO_CALL
            for row in actions
        ) == 2
        assert sum(
            row["action"] == "feature_no_call"
            and row["reason"] == v2.MARKET_EVIDENCE_NO_CALL
            for row in actions
        ) == 2
        assert wrapper["stream"]["event_terminal"] != "censored_feature"


def test_primary_fill_and_headroom_contracts_unchanged():
    spec = v2.load_candidate_spec(ROOT)
    fill = spec["primary_fill_contract"]
    assert "executed trade volume" in fill["authority"]
    assert "estimated or unobservable ahead-queue clearance" in fill[
        "not_required"
    ]
    assert "never changes" in fill["queue_treatment"]
    assert spec["headroom_contract"]["strict_guard"] == (
        "b1 + b2 + fee_cents < 0"
    )
