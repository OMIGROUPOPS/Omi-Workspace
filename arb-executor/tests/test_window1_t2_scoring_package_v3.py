from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_range_attack_reference_adapter_v1 import (
    ReferenceError,
    guarded_cutoff,
)
from window1_t2_reference_boundary_v3 import (
    BoundaryCompatibilityError,
    adapt_frozen_reference_rows,
    read_jsonl,
    reconcile_boundaries,
)
from window1_t2_scoring_runner_v3 import (
    CONSUMED_AUTHORIZATION,
    CONSUMED_EXECUTION_ID,
    EXECUTION_ID,
    RESULTS_DIRECTORY,
    RunnerError,
    authorize_execute,
    execution_readiness_no_score,
    validate_package,
)


PACKAGE = (
    ROOT
    / ".claude"
    / "window1_t2_scoring_package_v3_prerun_20260728"
)
RAW_V5 = (
    ROOT
    / ".claude"
    / "window1_start_guard_corrected_20260724"
    / "REAL_START_LEDGER_V5.jsonl"
)
NORMALIZED = (
    ROOT
    / ".claude"
    / "window1_t2_scoring_package_prerun_20260728"
    / "GUARDED_BOUNDARY_LEDGER.jsonl"
)
EVENTS = (
    ROOT
    / ".claude"
    / "window1_t2_scoring_package_prerun_20260728"
    / "IMMUTABLE_EVENT_LEDGER.jsonl"
)


def read(name: str) -> dict:
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


def references() -> list[dict]:
    path = PACKAGE / "FROZEN_WINDOW1_CLOSE_REFERENCE_LEDGER.jsonl.gz"
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def expected_legs() -> dict[tuple[str, str], str]:
    return {
        (
            str(event["event_id"]),
            str(leg.get("leg_id") or leg.get("leg")),
        ): str(leg["ticker"])
        for event in read_jsonl(EVENTS)
        for leg in event["legs"]
    }


def test_flattened_boundary_reproduces_consumed_failure() -> None:
    flattened = read_jsonl(NORMALIZED)[0]
    with pytest.raises(
        ReferenceError,
        match="positive boundary lacks V5 guard artifact",
    ):
        guarded_cutoff(flattened)


def test_full_raw_v5_boundary_succeeds_for_first_failed_event() -> None:
    raw = read_jsonl(RAW_V5)[0]
    result = guarded_cutoff(raw)
    assert raw["event_id"] == "KXATPCHALLENGERMATCH-26JUL12ALVVAN"
    assert result["status"] == "positive"
    assert result["cutoff_ts"] == 1783846800.0


def test_raw_to_normalized_boundary_conservation() -> None:
    receipt = reconcile_boundaries(RAW_V5, NORMALIZED)
    assert receipt["events_compared"] == 804
    assert receipt["field_mismatch_count"] == 0
    assert receipt["package_blocked"] is False


def test_frozen_compatibility_receipt_has_zero_mismatches() -> None:
    receipt = read("REFERENCE_BOUNDARY_COMPATIBILITY_RECEIPT.json")
    assert receipt["raw_v5_ledger"]["row_count"] == 804
    assert receipt["normalized_boundary_ledger"]["row_count"] == 804
    assert receipt["field_mismatch_count"] == 0
    assert receipt["mismatch_event_ids"] == []


def test_all_frozen_reference_rows_validate() -> None:
    starts = {
        row["event_id"]: row for row in read_jsonl(NORMALIZED)
    }
    result = adapt_frozen_reference_rows(
        references(),
        expected_legs=expected_legs(),
        normalized_boundaries=starts,
    )
    assert len(result) == 1608


def test_first_real_failure_event_has_two_frozen_references() -> None:
    rows = [
        row for row in references()
        if row["event_id"] == "KXATPCHALLENGERMATCH-26JUL12ALVVAN"
    ]
    assert {row["leg_id"] for row in rows} == {"ALV", "VAN"}
    assert all(row["raw_v5_boundary_ledger_sha256"] for row in rows)


def test_missing_reference_never_fabricates_price() -> None:
    for row in references():
        if row["available"] is False:
            assert row["window1_close_cents"] is None
            assert row["reference_receipt"] is None
            assert row["reason"]


def test_reference_ledger_is_exactly_one_row_per_event_leg() -> None:
    rows = references()
    keys = {(row["event_id"], row["leg_id"]) for row in rows}
    assert len(rows) == len(keys) == 1608


def test_real_input_preflight_reaches_scorer_boundary_without_scorer() -> None:
    receipt = execution_readiness_no_score(
        ROOT, PACKAGE / "SCORING_INPUT_MANIFEST.json"
    )
    assert receipt["scorer_boundary_reached"] is True
    assert receipt["scorer_invocations"] == 0
    assert receipt["event_leg_keys_joined"] == 1608
    assert receipt["candidate_event_leg_keys_joined"] == 12864
    assert receipt["C"] is receipt["PC"] is receipt["IC"] is receipt["S"] is None


def test_frozen_readiness_receipt_matches_real_preflight() -> None:
    frozen = read("EXECUTION_READINESS_NO_SCORE_RECEIPT.json")
    replay = execution_readiness_no_score(
        ROOT, PACKAGE / "SCORING_INPUT_MANIFEST.json"
    )
    for field in (
        "event_rows",
        "event_leg_keys_joined",
        "candidate_event_leg_keys_joined",
        "boundary_rows_validated",
        "floor_rows_validated",
        "regret_chain_rows_validated",
        "authority_d2_rows_validated",
        "scorer_invocations",
    ):
        expected = frozen[
            "reference_rows_derived_and_validated"
            if field == "reference_rows_validated" else field
        ] if field == "reference_rows_validated" else frozen[field]
        assert replay[field] == expected


def test_consumed_authorization_is_rejected_before_report_validation() -> None:
    with pytest.raises(RunnerError, match="consumed V2 authorization"):
        authorize_execute(
            ROOT,
            {"package": {}, "head": "0" * 40},
            CONSUMED_AUTHORIZATION,
            "does-not-matter",
        )


def test_v3_identity_does_not_reuse_v2_execution_id() -> None:
    assert EXECUTION_ID.endswith("scorepkg-v3")
    assert CONSUMED_EXECUTION_ID.endswith("scorepkg-v2")
    assert EXECUTION_ID != CONSUMED_EXECUTION_ID
    contract = json.loads(
        (
            ROOT
            / "arb-executor"
            / "docs"
            / "research"
            / "window1"
            / "WINDOW1_T2_SCORING_EXECUTION_READINESS_CONTRACT_V3.json"
        ).read_text(encoding="utf-8")
    )
    assert contract["execution_id"] == EXECUTION_ID
    assert contract["authorization"]["consumed_v2_authorization_rejected"]


def test_v3_results_directory_is_fresh_and_absent() -> None:
    assert RESULTS_DIRECTORY.endswith("scorepkg-v3")
    assert not (ROOT / RESULTS_DIRECTORY).exists()


def test_package_requires_future_authorization() -> None:
    validated = validate_package(
        ROOT,
        PACKAGE / "SCORING_INPUT_MANIFEST.json",
        verify_private_inputs=False,
    )
    manifest = validated["package"]
    assert manifest["future_independent_PASS_required"] is True
    assert manifest["future_authorization_required"] is True
    assert manifest["scored"] is False


def test_reference_adapter_fails_closed_on_duplicate_key() -> None:
    rows = references()
    with pytest.raises(
        BoundaryCompatibilityError,
        match="duplicate/unknown",
    ):
        adapt_frozen_reference_rows(
            rows + [dict(rows[0])],
            expected_legs=expected_legs(),
            normalized_boundaries=None,
        )


def test_failure_binding_is_exact_and_score_free() -> None:
    receipt = read("CONSUMED_V2_FAILURE_BINDING.json")
    assert receipt["failed_results_commit"] == (
        "3f8fa0fb372c9e89fa97f89fd26156892745afe1"
    )
    assert receipt["invocation_count"] == 1
    assert receipt["retry_count"] == 0
    assert receipt["exit_code"] == 1
    assert receipt["scorer_invocations"] == 0
    assert receipt["performance_result_produced"] is False


def test_authorization_time_discrepancy_is_preserved_not_amended() -> None:
    receipt = read("AUTHORIZATION_TIMESTAMP_DISCREPANCY_RECEIPT.json")
    assert receipt["document_printed_label"] == "10:43 PM ET"
    assert receipt["git_commit_metadata_time"] == (
        "2026-07-28T18:44:29-04:00"
    )
    assert receipt["execution_started_at_eastern"].startswith(
        "2026-07-28T18:53:49"
    )
    assert receipt["authorization_preceded_execution"] is True
    assert receipt["operator_facing_eastern_time_law_satisfied"] is False
    assert receipt["consumed_authorization_amended"] is False
