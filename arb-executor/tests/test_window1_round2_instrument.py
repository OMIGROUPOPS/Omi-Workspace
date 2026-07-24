from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round2_capability_proof as proof  # noqa: E402
import window1_round2_data_binding as binding  # noqa: E402
import window1_round2_instrument as round2  # noqa: E402


def test_frozen_grid_has_no_free_numeric_parameters():
    spec = round2.load_candidate_spec(ROOT)
    assert len(spec["candidate_ids"]) == 8
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
    assert result["advertised_family_count"] == 11
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


def test_first_fill_hold_changes_only_unfilled_sibling():
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), proof.base_event()
    )
    holds = [
        row for row in result["order_stream"]
        if row["action"] == "sibling_hold"
    ]
    assert len(holds) == 1
    assert holds[0]["leg_id"] == "B"
    assert holds[0]["first_filled_leg"] == "A"


def test_reaim_waits_for_siblings_later_trigger_and_changes_order_by_one():
    event = proof.reaim_event()
    surfaces = proof.synthetic_surfaces()
    hold = proof.run_policy(
        ROOT, surfaces, event, "r2_full_os__walk_park__hold"
    )
    reaim = proof.run_policy(
        ROOT, surfaces, event, "r2_full_os__walk_park__reaim"
    )
    armed = next(
        row for row in reaim["order_stream"]
        if row["action"] == "sibling_reaim_armed"
    )
    applied = next(
        row for row in reaim["order_stream"]
        if row["action"] == "sibling_reaim_applied"
    )
    assert applied["ts"] > armed["ts"]
    assert applied["ts"] >= armed["sibling_eligible_ts"]
    assert applied["reaim_sibling_order_cents"] == (
        applied["base_sibling_order_cents"] + 1
    )
    assert proof.decision_signature(
        hold, before=applied["ts"]
    ) == proof.decision_signature(
        reaim, before=applied["ts"]
    )
    assert not any(
        row["leg_id"] == armed["leg_id"]
        and row["ts"] == armed["ts"]
        and row["action"] in {"place", "reprice", "cancel"}
        for row in reaim["order_stream"]
    )


def test_reaim_without_later_sibling_evidence_is_no_call_not_censor():
    result = proof.run_policy(
        ROOT,
        proof.synthetic_surfaces(),
        proof.base_event(),
        "r2_full_os__walk_park__reaim",
    )
    no_calls = [
        row for row in result["order_stream"]
        if row["action"] == "sibling_reaim_no_call"
    ]
    assert no_calls
    assert all(
        row["response_status"] == "NO_CALL_UNAVAILABLE"
        and row["underlying_policy_continues"] is True
        for row in no_calls
    )
    assert result["event_terminal"] != "censored_feature"


def test_reaim_guard_abstention_cannot_create_sibling_book_reprice():
    event = proof.reaim_event()
    surfaces = proof.synthetic_surfaces()
    spec = round2.load_candidate_spec(ROOT)
    hold_policy = round2.candidate_policy(
        spec, "r2_full_os__walk_park__hold"
    )
    reaim_policy = round2.candidate_policy(
        spec, "r2_full_os__walk_park__reaim"
    )
    reaim_policy["parameters"][
        "first_fill_sibling_max_combined_cost_cents"
    ] = 1
    hold = round2.CausalInstrument(
        surfaces, hold_policy
    ).run(event)
    reaim = round2.CausalInstrument(
        surfaces, reaim_policy
    ).run(event)
    assert not any(
        row["action"] == "sibling_reaim_applied"
        for row in reaim["order_stream"]
    )
    assert proof.decision_signature(hold) == proof.decision_signature(
        reaim
    )
    assert any(
        row["action"] == "sibling_reaim_no_call"
        for row in reaim["order_stream"]
    )


def test_t8_actions_are_invariant_to_future_t6_recognition_mapping():
    result = proof.capability_proof(ROOT)["t8_t6_lookahead_proof"]
    assert result["pre_T6_decisions_identical"] is True
    assert result["post_T6_decisions_differ"] is True
    assert result["future_information_used_before_T6"] is False


def test_own_fingerprint_is_excluded_from_signal_and_fill_evidence():
    event = proof.base_event()
    left = float(event["policy_left_ts"])
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


def test_schedule_only_anchor_can_run_policy_but_never_proves_positive():
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), proof.schedule_only_event()
    )
    evaluated = round2.evaluate_order_stream(result, {
        "start_source_class": "schedule_only",
        "evaluation_real_start_ts": None,
    })
    assert result["evaluation_truth_present"] is False
    assert evaluated["classification"] == "censored_start_boundary"
    assert evaluated["positive_window1_proved"] is False


def test_policy_rejects_realized_start_or_guarded_cutoff_fields():
    event = proof.base_event()
    event["evaluation_real_start_ts"] = (
        event["policy_anchor_ts"] + 300
    )
    with pytest.raises(
        round2.InstrumentError, match="evaluation truth is inaccessible"
    ):
        proof.run_policy(ROOT, proof.synthetic_surfaces(), event)


def test_different_future_realized_starts_leave_policy_bytes_identical():
    event = proof.base_event()
    first = proof.run_policy(ROOT, proof.synthetic_surfaces(), event)
    second = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), copy.deepcopy(event)
    )
    assert json.dumps(first, sort_keys=True) == json.dumps(
        second, sort_keys=True
    )
    fill_times = [
        float(row["ts"]) for row in first["order_stream"]
        if row["action"] == "fill_observed"
    ]
    assert fill_times
    guard = {"guard_id": "fixture-official-60s"}
    early = round2.evaluate_order_stream(first, {
        "start_source_class": "official_exact",
        "evaluation_real_start_ts": min(fill_times) - 1,
        "start_guard": guard,
    })
    late = round2.evaluate_order_stream(first, {
        "start_source_class": "official_exact",
        "evaluation_real_start_ts": max(fill_times) + 1,
        "start_guard": guard,
    })
    assert early["classification"] != late["classification"]


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


def test_cohort_below_floor_is_named_no_call_and_policy_continues():
    surfaces = proof.synthetic_surfaces()
    surfaces.cohort["rows"].clear()
    result = proof.run_policy(
        ROOT, surfaces, proof.base_event(),
        "r2_causal_steer__park_join__hold",
    )
    no_calls = [
        row for row in result["order_stream"]
        if row["action"] == "cohort_no_call"
    ]
    assert no_calls
    assert all(row["underlying_policy_continues"] for row in no_calls)
    assert result["event_terminal"] != "censored_feature"
    assert any(
        row["action"] in {"place", "reprice"}
        for row in result["order_stream"]
    )


@pytest.mark.parametrize("bad_size", [0, None, "malformed"])
def test_zero_missing_or_malformed_size_cannot_trigger_divot(bad_size):
    event = proof.base_event()
    target = next(
        row for row in event["legs"][0]["observations"]
        if row.get("trade_id") == "A-DIVOT"
    )
    target["size"] = bad_size
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), event
    )
    actions = result["leg_streams"]["A"]
    assert any(
        row["action"] == "print_excluded"
        and row.get("trade_id") == "A-DIVOT"
        for row in actions
    )
    assert not any(
        row["action"] == "micro_divot"
        and row.get("print_price_cents") == 54
        for row in actions
    )


def test_zero_size_walk_chain_link_cannot_advance_walk():
    event = proof.base_event()
    for row in event["legs"][0]["observations"]:
        if row.get("trade_id") in {"A-CHAIN-1", "A-CHAIN-2"}:
            row["size"] = 0
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), event
    )
    assert not any(
        row["action"] == "reprice"
        and row["reason"] == "verified_nonself_chain_exact_one_cent"
        for row in result["leg_streams"]["A"]
    )


def test_synthetic_transition_cannot_trigger_any_micro_surface():
    event = proof.base_event()
    target = next(
        row for row in event["legs"][0]["observations"]
        if row.get("trade_id") == "A-DIVOT"
    )
    target["synthetic_transition"] = True
    result = proof.run_policy(
        ROOT, proof.synthetic_surfaces(), event
    )
    assert any(
        row["action"] == "print_excluded"
        and row["reason"] == "synthetic_transition"
        for row in result["leg_streams"]["A"]
    )


def test_zero_null_or_malformed_book_sizes_contribute_zero():
    book = {
        "bids": [[60, 0], [59, None], [58, "bad"], [57, 4]],
        "asks": [[61, 0], [62, None], [63, "bad"], [64, 3]],
        "own_bid_size_by_price": {"57": None},
    }
    assert round2.external_bids(book, True) == [(57, 4.0)]
    assert round2.asks(book) == [(64, 3.0)]
    assert round2.book_pressure_ratio(book, True) == 0.75


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


def test_superseding_binding_is_unscored_and_holdout_sealed():
    manifest = json.loads((
        ROOT / ".claude/window1_round2_prerun_v2_20260724/"
        "ROUND2_DATA_BINDING_MANIFEST.json"
    ).read_text(encoding="utf-8"))
    assert manifest["D"] == 804
    assert manifest["leg_identities"] == 1608
    assert manifest["holdout_opened"] is False
    assert manifest["holdout_queried"] is False
    assert manifest["candidate_scoring_performed"] is False
    assert manifest["holdout_dates_present_in_any_input"] == 0
    assert all(
        "rows" in row["counts"]
        and "events" in row["counts"]
        and "tickers" in row["counts"]
        for row in manifest["input_records"].values()
    )


def test_binding_validator_rejects_changed_manifest_before_execution(tmp_path):
    source = (
        ROOT / ".claude/window1_round2_prerun_v2_20260724/"
        "ROUND2_DATA_BINDING_MANIFEST.json"
    )
    manifest = json.loads(source.read_text(encoding="utf-8"))
    manifest["D"] = 803
    changed = tmp_path / "changed.json"
    changed.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(binding.BindingError, match="envelope changed"):
        binding.validate_bound_inputs(
            ROOT,
            changed,
            events_path=tmp_path / "events.jsonl",
            prints_path=tmp_path / "prints.jsonl",
            tape_manifest_path=tmp_path / "tape_manifest.json",
            cache_root=tmp_path / "cache",
        )


def test_real_capability_candidates_are_eligible_distinct_and_unscored():
    receipt = json.loads((
        ROOT / ".claude/window1_round2_final_prerun_20260724/"
        "ROUND2_REAL_CAPABILITY.json"
    ).read_text(encoding="utf-8"))
    assert receipt["D"] == 804
    assert receipt["candidate_count"] == 8
    assert receipt["candidate_gate_pass"] is True
    assert receipt["duplicate_candidate_groups"] == []
    assert receipt["candidate_scoring_performed"] is False
    assert all(
        row["eligible_event_count"] > 0
        and row["censored_event_count"] < 804
        for row in receipt["candidate_summaries"]
    )
    assert all(
        "-" in key
        for row in receipt["candidate_summaries"]
        for key in row["per_leg_place_reprice_cancel"]
    )


def test_actual_family_proof_counts_only_real_decision_witnesses():
    receipt = json.loads((
        ROOT / ".claude/window1_round2_final_prerun_20260724/"
        "ROUND2_ACTUAL_FAMILY_PROOF.json"
    ).read_text(encoding="utf-8"))
    assert receipt["gate_pass"] is True
    assert len(receipt["family_witnesses"]) == 9
    assert all(
        row["decision_changing"] is True
        and row["event_id"].startswith("KX")
        for row in receipt["family_witnesses"]
    )
    unavailable = {
        row["family_id"]: row
        for row in receipt["unavailable_or_noncoverage"]
    }
    assert unavailable["cohort_steering"]["counted_as_coverage"] is False
    assert unavailable[
        "own_order_contribution_subtraction"
    ]["counted_as_coverage"] is False


def test_all_four_reaim_pairs_have_real_later_trigger_order_witnesses():
    receipt = json.loads((
        ROOT / ".claude/window1_round2_final_prerun_20260724/"
        "ROUND2_REAIM_PAIR_PROOF.json"
    ).read_text(encoding="utf-8"))
    assert receipt["gate_pass"] is True
    assert receipt["candidate_pair_count"] == 4
    assert receipt[
        "sibling_hold_bookkeeping_counted_as_order_witness"
    ] is False
    assert all(
        row["real_D804_events_with_order_change"] > 0
        and row["witness"]["exact_reaim_difference_cents"] == 1
        and row["witness"][
            "earlier_order_decisions_byte_identical"
        ] is True
        for row in receipt["pairs"]
    )
