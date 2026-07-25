from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round2_capability_proof as proof  # noqa: E402
import window1_round3_instrument as round3  # noqa: E402
import window1_round3_prerun_builder as builder  # noqa: E402


def bind_book_receipts(event: dict) -> dict:
    for leg in event["legs"]:
        for index, row in enumerate(leg["observations"]):
            if row["kind"] == "book":
                row.setdefault(
                    "source_receipt_identity",
                    f"{leg['ticker']}|book|{row['ts']}|{index}",
                )
    return event


def run(
    event: dict,
    candidate_id: str = "r3_full_os__walk_park__hold",
):
    spec = round3.load_candidate_spec(ROOT)
    policy = round3.candidate_policy(spec, candidate_id)
    return round3.Round3Instrument(
        proof.synthetic_surfaces(), policy
    ).run(bind_book_receipts(event))


def decisions(result: dict) -> list[dict]:
    return builder.decision_signature(result)


def test_grid_is_exactly_eight_and_has_no_free_parameters():
    spec = round3.load_candidate_spec(ROOT)
    assert len(spec["candidate_ids"]) == 8
    assert len(set(spec["candidate_ids"])) == 8
    assert spec["free_numeric_parameters"] == []
    for candidate_id in spec["candidate_ids"]:
        policy = round3.candidate_policy(spec, candidate_id)
        assert policy["ablations"] == []


def test_both_legs_place_from_their_own_first_causal_bbo():
    event = proof.timing_event()
    event["legs"][1]["observations"][0]["ts"] += 30
    result = run(event, "r3_pair_presence__park_join__hold")
    first_place = {}
    first_book = {}
    for leg in event["legs"]:
        first_book[leg["leg_id"]] = min(
            row["ts"] for row in leg["observations"]
            if row["kind"] == "book"
            and row.get("bids")
            and row.get("asks")
        )
    for row in result["order_stream"]:
        if row["action"] == "place":
            first_place.setdefault(row["leg_id"], row["ts"])
    assert first_place == first_book
    assert len(set(first_place.values())) == 2


def test_fitted_tdeep_is_advisory_not_an_eligibility_gate():
    result = run(
        proof.timing_event(), "r3_pair_presence__park_join__hold"
    )
    macros = [
        row for row in result["order_stream"]
        if row["action"] == "macro_bind"
    ]
    assert macros
    assert all(
        row["advisory_tdeep_is_hard_gate"] is False
        and row["eligible_ts"] < row["advisory_tdeep_ts"]
        for row in macros
    )
    first_places = {
        row["leg_id"]: row["ts"] for row in result["order_stream"]
        if row["action"] == "place"
    }
    assert all(
        first_places[row["leg_id"]] == row["eligible_ts"]
        for row in macros
    )


def test_book_cell_change_is_latent_and_preserves_queue_without_print():
    event = proof.timing_event()
    for leg in event["legs"]:
        first = next(
            row for row in leg["observations"] if row["kind"] == "book"
        )
        later = copy.deepcopy(first)
        later["ts"] = float(first["ts"]) + 10
        later["bids"][0][0] = int(later["bids"][0][0]) - 20
        leg["observations"].append(later)
        leg["observations"].sort(key=lambda row: row["ts"])
    result = run(event, "r3_pair_presence__park_join__hold")
    latent = [
        row for row in result["order_stream"]
        if row["action"] == "latent_pair_recut"
    ]
    assert latent
    assert all(row["order_changed"] is False for row in latent)
    assert not any(
        row["action"] in {"cancel", "reprice"}
        and row["reason"].startswith("causal_book_updates_cell")
        for row in result["order_stream"]
    )


@pytest.mark.parametrize("bad_size", [0, None, "malformed"])
def test_zero_null_or_malformed_print_cannot_trigger_round3_surfaces(
    bad_size,
):
    event = proof.base_event()
    for row in event["legs"][0]["observations"]:
        if row.get("trade_id") == "A-DIVOT":
            row["size"] = bad_size
    result = run(event, "r3_pair_presence__park_join__hold")
    leg = result["leg_streams"]["A"]
    assert any(
        row["action"] == "print_excluded"
        and row.get("trade_id") == "A-DIVOT"
        for row in leg
    )
    assert not any(
        row["action"] in {
            "micro_divot",
            "sibling_reaim_applied",
            "top5_pressure_order_effect",
        }
        and row.get("trade_id") == "A-DIVOT"
        for row in leg
    )


def test_zero_size_walk_chain_cannot_trigger_walk():
    event = proof.base_event()
    for row in event["legs"][0]["observations"]:
        if row["kind"] == "print":
            row["size"] = 0
    result = run(event, "r3_full_os__walk_park__hold")
    assert not any(
        row["action"] == "reprice"
        and row["reason"] == "verified_nonself_chain_exact_one_cent"
        for row in result["leg_streams"]["A"]
    )


def test_first_positive_fill_arms_later_sibling_plus_one_action():
    event = proof.reaim_event()
    hold = run(event, "r3_full_os__walk_park__hold")
    reaim = run(event, "r3_full_os__walk_park__reaim")
    armed = next(
        row for row in reaim["order_stream"]
        if row["action"] == "sibling_reaim_armed"
    )
    applied = next(
        row for row in reaim["order_stream"]
        if row["action"] == "sibling_reaim_applied"
    )
    assert applied["ts"] > armed["ts"]
    assert applied["exact_reaim_difference_cents"] == 1
    assert applied["reaim_sibling_order_cents"] == (
        applied["base_sibling_order_cents"] + 1
    )
    assert [
        row for row in decisions(hold) if row["ts"] < applied["ts"]
    ] == [
        row for row in decisions(reaim) if row["ts"] < applied["ts"]
    ]
    assert not any(
        row["leg_id"] == armed["leg_id"]
        and row["ts"] == armed["ts"]
        and row["action"] in {"place", "reprice", "cancel"}
        for row in reaim["order_stream"]
    )


def test_partial_first_fill_also_arms_response_chain():
    event = proof.reaim_event()
    first_leg = event["legs"][0]
    first_fill_print = next(
        row for row in first_leg["observations"]
        if row.get("trade_id") == "A-FILL"
    )
    first_fill_print["size"] = 1
    result = run(event, "r3_full_os__walk_park__reaim")
    armed = [
        row for row in result["order_stream"]
        if row["action"] == "sibling_reaim_armed"
    ]
    assert len(armed) == 1
    assert armed[0]["first_leg_fill_ts"] == first_fill_print["ts"]


def test_reaim_no_later_evidence_is_no_call_not_censor():
    event = proof.base_event()
    event["legs"][1]["observations"] = [
        row for row in event["legs"][1]["observations"]
        if float(row["ts"]) <= 1007300.0
    ]
    result = run(
        event, "r3_full_os__walk_park__reaim"
    )
    no_calls = [
        row for row in result["order_stream"]
        if row["action"] == "sibling_reaim_no_call"
    ]
    assert no_calls
    assert all(row["underlying_policy_continues"] for row in no_calls)
    assert result["event_terminal"] != "censored_feature"


def test_cohort_no_call_never_erases_underlying_pair_orders():
    surfaces = proof.synthetic_surfaces()
    surfaces.cohort["rows"].clear()
    spec = round3.load_candidate_spec(ROOT)
    policy = round3.candidate_policy(
        spec, "r3_causal_steer__park_join__hold"
    )
    result = round3.Round3Instrument(
        surfaces, policy
    ).run(bind_book_receipts(proof.base_event()))
    assert any(
        row["action"] == "cohort_no_call"
        and row["underlying_policy_continues"] is True
        for row in result["order_stream"]
    )
    assert any(
        row["action"] == "place" for row in result["order_stream"]
    )


def test_missing_required_feature_is_named_censor_not_nonfill():
    event = proof.missing_feature_event()
    event["legs"][0]["feature_availability"]["causal_role"] = False
    result = run(event)
    assert result["event_terminal"] == "censored_feature"
    assert any(
        row["action"] == "feature_censor"
        for row in result["order_stream"]
    )
    assert any(
        row["leg_id"] == "A"
        and row["action"] == "terminal"
        and row["reason"] == "censored_feature"
        for row in result["order_stream"]
    )


def test_policy_truth_and_holdout_are_hard_refused():
    event = proof.base_event()
    event["evaluation_real_start_ts"] = event["policy_anchor_ts"]
    with pytest.raises(
        round3.InstrumentError, match="evaluation truth is inaccessible"
    ):
        run(event)
    holdout = proof.base_event()
    holdout["event_date"] = "2026-07-24"
    with pytest.raises(round3.InstrumentError, match="sealed holdout"):
        run(holdout)


def test_candidate_allowlist_and_ablations_fail_closed():
    spec = round3.load_candidate_spec(ROOT)
    with pytest.raises(round3.InstrumentError, match="not frozen"):
        round3.candidate_policy(spec, "r3_not_frozen")
    with pytest.raises(
        round3.InstrumentError, match="no post-freeze ablation"
    ):
        round3.candidate_policy(
            spec, spec["candidate_ids"][0], ablations=["anything"]
        )


def test_duplicate_print_and_book_receipts_contribute_zero():
    event = bind_book_receipts(proof.base_event())
    duplicate_book = copy.deepcopy(event["legs"][0]["observations"][0])
    duplicate_book["ts"] += 1
    duplicate_print = copy.deepcopy(next(
        row for row in event["legs"][0]["observations"]
        if row.get("trade_id") == "A-DIVOT"
    ))
    duplicate_print["ts"] += 1
    event["legs"][0]["observations"].extend(
        [duplicate_book, duplicate_print]
    )
    event["legs"][0]["observations"].sort(
        key=lambda row: (row["ts"], row["kind"])
    )
    result = run(event)
    excluded = [
        row for row in result["leg_streams"]["A"]
        if row["action"] in {"book_excluded", "print_excluded"}
    ]
    assert any(
        row["reason"] == "duplicate_book_receipt_identity"
        for row in excluded
    )
    assert any(
        row["reason"] == "duplicate_print_receipt_identity"
        for row in excluded
    )


def test_same_timestamp_distinct_book_content_gets_distinct_receipts():
    event = bind_book_receipts(proof.base_event())
    leg = event["legs"][0]
    original = leg["observations"][0]
    changed = copy.deepcopy(original)
    changed["bids"][0][0] -= 1
    del original["source_receipt_identity"]
    del changed["source_receipt_identity"]
    leg["observations"].insert(1, changed)
    builder.bind_round3_book_receipts(event)
    identities = [
        row["source_receipt_identity"]
        for row in leg["observations"][:2]
    ]
    assert len(set(identities)) == 2


def test_stream_is_byte_deterministic_and_never_scored():
    event = proof.base_event()
    first = run(event)
    second = run(copy.deepcopy(event))
    assert json.dumps(
        first, sort_keys=True, separators=(",", ":")
    ) == json.dumps(
        second, sort_keys=True, separators=(",", ":")
    )
    assert first["scored"] is False
    assert first["metrics"] is None
    assert first["holdout_queried"] is False


def test_real_capability_freeze_has_eight_distinct_unscored_candidates():
    receipt = json.loads((
        ROOT / ".claude/window1_round3_prerun_20260725/"
        "ROUND3_REAL_CAPABILITY.json"
    ).read_text(encoding="utf-8"))
    assert receipt["D"] == 804
    assert receipt["candidate_count"] == 8
    assert receipt["candidate_event_stream_count"] == 6432
    assert receipt["candidate_scoring_performed"] is False
    assert receipt["holdout_opened"] is False
    assert receipt["holdout_queried"] is False
    assert len({
        row["aggregate_order_decision_sha256"]
        for row in receipt["candidate_summaries"]
    }) == 8
    assert all(
        row["eligible_event_count"] > 0
        and row["censored_event_count"] < 804
        and row["events_distinct_from_declared_reference"] > 0
        for row in receipt["candidate_summaries"]
    )
    assert len(receipt["base_reaim_pair_proof"]) == 4
    assert all(
        row["real_event_order_change_count"] > 0
        and row["all_exact_plus_one"] is True
        and row["all_earlier_decisions_byte_identical"] is True
        for row in receipt["base_reaim_pair_proof"]
    )


def test_prerun_manifest_freezes_scope_without_authorizing_scoring():
    manifest = json.loads((
        ROOT / ".claude/window1_round3_prerun_20260725/"
        "ROUND3_PRE_RUN_MANIFEST.json"
    ).read_text(encoding="utf-8"))
    scope = manifest["development_scope"]
    assert scope["D"] == 804
    assert scope["leg_identities"] == 1608
    assert scope["candidate_count"] == 8
    assert scope["candidate_event_streams"] == 6432
    assert manifest["benchmark_execution_authorized"] is False
    assert manifest["benchmark_execution_command"] is None
    assert manifest["candidate_scoring_performed"] is False
    assert manifest["performance_metrics_computed"] is False
    assert manifest["holdout_opened"] is False
    assert manifest["holdout_queried"] is False
    assert manifest["live_or_production_access"] is False
