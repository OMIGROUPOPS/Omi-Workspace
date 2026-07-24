from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round2_capability_proof as proof  # noqa: E402
import window1_round2_instrument as round2  # noqa: E402
import window1_round2_prerun as prerun  # noqa: E402


def test_frozen_grid_has_no_free_numeric_parameters():
    spec = round2.load_candidate_spec(ROOT)
    assert len(spec["candidate_ids"]) == 10
    assert spec["free_numeric_parameters"] == []
    assert len(spec["predeclared_selected_candidate_ablations"]) == 9
    for candidate_id in spec["candidate_ids"]:
        policy = round2.candidate_policy(spec, candidate_id)
        assert policy["candidate_id"] == candidate_id
        assert policy["posture_by_role"].keys() == {
            "favorite", "underdog"
        }


def test_every_advertised_family_changes_an_eligible_decision():
    result = proof.capability_proof(ROOT)
    assert result["gate_pass"] is True
    assert result["failed_or_inert_families"] == []
    assert result["advertised_family_count"] == 12
    assert all(
        row["decision_changing"] is True
        for row in result["family_capability_matrix"]
    )


def test_independent_async_leg_clocks_produce_different_place_times():
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), proof.timing_event()
    )
    first_place = {}
    for row in result["order_stream"]:
        if row["action"] == "place":
            first_place.setdefault(row["leg_id"], row["ts"])
    assert set(first_place) == {"A", "B"}
    assert first_place["A"] != first_place["B"]


def test_walk_is_exactly_one_cent_and_uses_nonself_chain():
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), proof.base_event()
    )
    stream = result["leg_streams"]["A"]
    walks = [
        row for row in stream
        if row["action"] == "reprice"
        and row["reason"] == "verified_nonself_chain_exact_one_cent"
    ]
    assert walks
    walk = walks[0]
    prior_cancel = next(
        row for row in reversed(stream[:stream.index(walk)])
        if row["action"] == "cancel"
        and row["reason"] == "verified_nonself_chain_walk_cancel"
    )
    assert walk["price_cents"] == prior_cancel["price_cents"] + 1


def test_first_fill_reaim_changes_only_unfilled_sibling():
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), proof.base_event()
    )
    reaims = [
        row for row in result["order_stream"]
        if row["action"] == "sibling_reaim_decision"
    ]
    assert len(reaims) == 1
    assert reaims[0]["leg_id"] == "B"
    assert reaims[0]["first_filled_leg"] == "A"


def test_t8_actions_are_invariant_to_future_t6_recognition_mapping():
    result = proof.capability_proof(ROOT)["t8_t6_lookahead_proof"]
    assert result["pre_T6_decisions_identical"] is True
    assert result["post_T6_decisions_differ"] is True
    assert result["future_information_used_before_T6"] is False


def test_own_fingerprint_is_excluded_from_signal_and_fill_evidence():
    event = proof.base_event()
    left = float(event["left_ts"])
    event["legs"][0]["observations"].append(
        proof.trade(
            left + 5000,
            1,
            size=100,
            trade_id="OWN-PRINT",
            own=True,
        )
    )
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), event
    )
    excluded = [
        row for row in result["leg_streams"]["A"]
        if row["action"] == "contributed_volume_excluded"
        and row.get("trade_id") == "OWN-PRINT"
    ]
    fills = [
        row for row in result["leg_streams"]["A"]
        if row["action"] == "fill_observed"
        and row.get("trade_id") == "OWN-PRINT"
    ]
    assert len(excluded) == 1
    assert fills == []


def test_schedule_only_never_creates_positive_stream():
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), proof.schedule_only_event()
    )
    assert result["event_terminal"] == "censored_start_boundary"
    assert not any(
        row["action"] in {"place", "reprice", "fill_observed"}
        for row in result["order_stream"]
    )


def test_missing_feature_is_censored_not_nonfill():
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), proof.missing_feature_event()
    )
    assert result["event_terminal"] == "censored_feature"
    assert any(
        row["action"] == "terminal"
        and row["reason"] == "censored_feature"
        for row in result["order_stream"]
    )


def test_zero_length_window_is_separate_from_nonfill():
    event = proof.base_event()
    event["event_id"] = "FIXTURE-ZERO-WINDOW"
    event["strict_positive_cutoff_ts"] = event["left_ts"]
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), event
    )
    assert result["event_terminal"] == "zero_length_window1_opportunity"
    assert {
        row["reason"] for row in result["order_stream"]
        if row["action"] == "terminal"
    } == {"zero_length_window1_opportunity"}


def test_every_candidate_emits_both_leg_streams_without_scoring():
    spec = round2.load_candidate_spec(ROOT)
    event = proof.base_event()
    for candidate_id in spec["candidate_ids"]:
        result = proof.run_policy(
            ROOT,
            proof.synthetic_surfaces(),
            event,
            candidate_id,
        )
        assert set(result["leg_streams"]) == {"A", "B"}
        assert all(
            rows[-1]["action"] == "terminal"
            for rows in result["leg_streams"].values()
        )
        assert result["scored"] is False
        assert result["metrics"] is None
        assert result["holdout_queried"] is False


def test_holdout_event_is_hard_refused():
    event = proof.base_event()
    event["event_date"] = "2026-07-24"
    with pytest.raises(round2.InstrumentError, match="sealed holdout"):
        proof.run_policy(ROOT, proof.synthetic_surfaces(), event)


def test_candidate_and_ablation_allowlists_fail_closed():
    spec = round2.load_candidate_spec(ROOT)
    with pytest.raises(round2.InstrumentError, match="not frozen"):
        round2.candidate_policy(spec, "not-a-candidate")
    with pytest.raises(round2.InstrumentError, match="unfrozen ablation"):
        round2.candidate_policy(
            spec,
            spec["candidate_ids"][0],
            ablations=["without_made_up_family"],
        )


def test_stream_is_deterministic():
    event = proof.base_event()
    first = proof.run_policy(ROOT, proof.synthetic_surfaces(), event)
    second = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), copy.deepcopy(event)
    )
    assert first["stream_sha256"] == second["stream_sha256"]
    assert json.dumps(first, sort_keys=True) == json.dumps(
        second, sort_keys=True
    )


def test_prerun_contracts_validate_without_scoring_or_holdout():
    contracts = prerun.validate_contracts(ROOT)
    assert contracts["metric"]["D"] == 804
    assert contracts["metric"]["target_PC"] == 603
    assert contracts["holdout"]["holdout_opened"] is False
    assert contracts["holdout"]["holdout_queried"] is False
    assert contracts["holdout"]["round2_scoring_performed"] is False
    assert contracts["adapter"]["scoring_implemented"] is False
    assert contracts["proof"]["gate_pass"] is True
