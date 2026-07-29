from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_range_attack_reference_adapter_v1 import ReferenceError
from window1_t2_frontier_regret_scorer_v1 import score_t2_event
from window1_t2_scoring_runner_v4 import (
    CANDIDATE_IDS,
    CANDIDATE_TO_PARENT,
    CONSUMED_V2_AUTHORIZATION,
    CONSUMED_V2_EXECUTION_ID,
    CONSUMED_V3_AUTHORIZATION,
    CONSUMED_V3_EXECUTION_ID,
    EXECUTION_ID,
    RESULTS_DIRECTORY,
    RunnerError,
    authorize_execute,
    execution_readiness_no_score,
    validate_package,
)
from window1_t2_scoring_runtime_v4 import (
    ScoreAccounting,
    invoke_prepared_score,
    iter_prepared_scorer_calls,
    no_score_seam_probe,
)


PACKAGE = (
    ROOT
    / ".claude"
    / "window1_t2_scoring_package_v4_prerun_20260729"
)


def read(name: str) -> dict:
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest() -> dict:
    return read("SCORING_INPUT_MANIFEST.json")


@pytest.fixture(scope="module")
def first_prepared(manifest: dict):
    iterator = iter_prepared_scorer_calls(
        repo=ROOT,
        roles=manifest["roles"],
        candidate_ids=CANDIDATE_IDS,
        candidate_to_parent=CANDIDATE_TO_PARENT,
    )
    return next(iterator)


def test_V3_flattened_boundary_preserves_exact_error(
    first_prepared,
) -> None:
    kwargs = first_prepared.score_kwargs
    kwargs["boundary"] = first_prepared.normalized_boundary_contract
    with pytest.raises(
        ReferenceError,
        match="positive boundary lacks V5 guard artifact",
    ):
        score_t2_event(**kwargs)


def test_equivalent_full_raw_V5_shaped_boundary_passes_seam(
    first_prepared,
) -> None:
    kwargs = first_prepared.score_kwargs
    kwargs["boundary"] = dict(first_prepared.raw_v5_boundary)
    row = score_t2_event(**kwargs)
    assert row["event_id"] == first_prepared.event_id
    assert row["boundary_status"] == "positive"


def test_shared_preparation_uses_raw_for_first_failure_event(
    first_prepared,
) -> None:
    assert first_prepared.event_id == (
        "KXATPCHALLENGERMATCH-26JUL12ALVVAN"
    )
    assert first_prepared.score_kwargs["boundary"] is (
        first_prepared.raw_v5_boundary
    )
    assert first_prepared.score_kwargs["boundary"] is not (
        first_prepared.normalized_boundary_contract
    )
    assert "guard_band" in first_prepared.score_kwargs["boundary"]


def test_replacing_shared_raw_with_normalized_fails_regression(
    first_prepared,
) -> None:
    kwargs = first_prepared.score_kwargs
    kwargs["boundary"] = first_prepared.normalized_boundary_contract
    with pytest.raises(ReferenceError):
        score_t2_event(**kwargs)


def test_attempt_accounting_survives_injected_scorer_exception(
    first_prepared,
) -> None:
    accounting = ScoreAccounting()
    snapshots: list[dict] = []

    def persist(value: ScoreAccounting) -> None:
        snapshots.append(dict(value.to_dict()))

    def explode(**_: object) -> dict:
        raise RuntimeError("injected scorer failure")

    with pytest.raises(RuntimeError, match="injected scorer failure"):
        invoke_prepared_score(
            prepared=first_prepared,
            scorer=explode,
            accounting=accounting,
            persist=persist,
        )
    assert accounting.scorer_call_attempts == 1
    assert accounting.completed_event_rows == 0
    assert accounting.completed_candidates == 0
    assert snapshots == [{
        "scorer_call_attempts": 1,
        "completed_event_rows": 0,
        "completed_candidates": 0,
        "active_candidate_id": first_prepared.candidate_id,
        "active_event_id": first_prepared.event_id,
    }]


def test_success_accounting_completes_only_after_return(
    first_prepared,
) -> None:
    accounting = ScoreAccounting()
    snapshots: list[dict] = []

    def scorer(**_: object) -> dict:
        assert accounting.scorer_call_attempts == 1
        assert accounting.completed_event_rows == 0
        return {"ok": True}

    result = invoke_prepared_score(
        prepared=first_prepared,
        scorer=scorer,
        accounting=accounting,
        persist=lambda value: snapshots.append(dict(value.to_dict())),
    )
    assert result == {"ok": True}
    assert accounting.scorer_call_attempts == 1
    assert accounting.completed_event_rows == 1
    assert len(snapshots) == 2


def test_no_score_seam_covers_all_exact_calls(manifest: dict) -> None:
    receipt = no_score_seam_probe(
        repo=ROOT,
        roles=manifest["roles"],
        candidate_ids=CANDIDATE_IDS,
        candidate_to_parent=CANDIDATE_TO_PARENT,
        results_directory=RESULTS_DIRECTORY,
    )
    assert receipt["prepared_scorer_calls"] == 6432
    assert receipt["full_raw_V5_boundary_count"] == 6432
    assert receipt["normalized_boundary_selected_count"] == 0
    assert receipt["guarded_cutoff_success_count"] == 6432
    assert receipt["scorer_call_attempts"] == 0


def test_runner_preflight_reuses_shared_seam_without_score() -> None:
    receipt = execution_readiness_no_score(
        ROOT, PACKAGE / "SCORING_INPUT_MANIFEST.json"
    )
    assert receipt["prepared_scorer_calls"] == 6432
    assert receipt["scorer_call_attempts"] == 0
    assert receipt["completed_event_rows"] == 0
    assert receipt["completed_candidates"] == 0
    assert receipt["results_directory_absent"] is True


@pytest.mark.parametrize(
    "authorization",
    [CONSUMED_V2_AUTHORIZATION, CONSUMED_V3_AUTHORIZATION],
)
def test_consumed_authorizations_rejected_before_report(
    authorization: str,
) -> None:
    with pytest.raises(RunnerError, match="consumed V2/V3"):
        authorize_execute(
            ROOT,
            {"package": {}, "head": "0" * 40},
            authorization,
            "does-not-matter",
        )


def test_consumed_execution_ids_are_not_V4() -> None:
    assert EXECUTION_ID not in {
        CONSUMED_V2_EXECUTION_ID, CONSUMED_V3_EXECUTION_ID,
    }
    assert EXECUTION_ID.endswith("scorepkg-v4")


def test_consumed_V3_failure_binding_is_complete() -> None:
    receipt = read("CONSUMED_V3_FAILURE_BINDING.json")
    assert receipt["V3_failure_commit"] == (
        "9cd2bea5487d8e558c42c8950263b44179054a68"
    )
    assert receipt["runner_invocation_count"] == 1
    assert receipt["reconstructed_scorer_call_attempts"] == 1
    assert receipt["completed_event_rows"] == 0
    assert receipt["completed_candidates"] == 0
    assert receipt["completed_result_row_files"] == 0
    assert len(receipt["files"]) == 5
    assert "window1_t2_scoring_runner_v3.py" in receipt["exact_stack_trace"]


def test_correction_receipt_does_not_claim_V3_boundary_pass() -> None:
    receipt = read("TRANSITIVE_BOUNDARY_CORRECTION_RECEIPT.json")
    assert receipt["V3_AST_subset_proof_was_insufficient"] is True
    assert receipt["V3_reached_scorer_call_entry"] is True
    assert receipt["V3_passed_scorer_boundary"] is False
    assert receipt["normalized_selected_count"] == 0


def test_package_identity_and_nulls() -> None:
    validated = validate_package(
        ROOT,
        PACKAGE / "SCORING_INPUT_MANIFEST.json",
        verify_private_inputs=False,
    )
    package = validated["package"]
    assert package["schema_version"] == (
        "window1-t2-scoring-input-manifest-v4"
    )
    assert package["D"] == 804
    assert len(package["candidate_ids"]) == 8
    for key in (
        "C", "PC", "IC", "S", "frontier", "regret",
        "attribution", "performance", "ranking", "selection",
    ):
        assert package[key] is None


def test_V4_results_and_authorization_absent() -> None:
    assert not (ROOT / RESULTS_DIRECTORY).exists()
    package = read("SCORING_INPUT_MANIFEST.json")
    assert package["future_independent_PASS_required"] is True
    assert package["future_authorization_required"] is True
    assert package["scored"] is False
