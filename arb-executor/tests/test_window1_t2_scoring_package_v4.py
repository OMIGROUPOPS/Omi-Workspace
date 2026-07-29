from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import pytest


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_range_attack_reference_adapter_v1 import (
    ReferenceError,
    Window1CloseReference,
)
from window1_t2_reference_boundary_v3 import boundary_contract
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
CANDIDATE_IDS = (
    "w1_t2__macro_hold__fixed_admission_parent_control",
    "w1_t2__macro_hold__non_displacing_target_completeness",
    "w1_t2__macro_hold__target_completeness_evidence_decay",
    "w1_t2__macro_hold__full_causal_divot_stack",
    "w1_t2__macro_micro__fixed_admission_parent_control",
    "w1_t2__macro_micro__non_displacing_target_completeness",
    "w1_t2__macro_micro__target_completeness_evidence_decay",
    "w1_t2__macro_micro__full_causal_divot_stack",
)
CANDIDATE_TO_PARENT = {
    candidate: (
        "w1_range_attack__macro_hold__combined_headroom"
        if "__macro_hold__" in candidate
        else "w1_range_attack__macro_micro__combined_headroom"
    )
    for candidate in CANDIDATE_IDS
}
CONSUMED_V2_AUTHORIZATION = (
    "e4e57baca0c2172244e63f45b2086f2ef4df53e9"
)
CONSUMED_V3_AUTHORIZATION = (
    "40a6314fe0790416a260879cd9a071072e26e9a0"
)
CONSUMED_V2_EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v2"
)
CONSUMED_V3_EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v3"
)
EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v4"
)
RESULTS_DIRECTORY = f".claude/window1_t2_results_{EXECUTION_ID}"


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


@pytest.fixture(scope="module")
def development_event_ids(manifest: dict) -> frozenset[str]:
    ledger = ROOT / manifest["roles"]["event_ledger"]
    return frozenset(
        str(json.loads(line)["event_id"])
        for line in ledger.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


@pytest.fixture(scope="module")
def synthetic_score_kwargs() -> dict[str, Any]:
    event_id = "SYNTHETIC-W1-T2-V5-BOUNDARY-SEAM"
    candidate_id = CANDIDATE_IDS[0]
    legs = (
        ("SYN_A", "KXSYNTHETIC-A"),
        ("SYN_B", "KXSYNTHETIC-B"),
    )
    event = {
        "event_id": event_id,
        "event_date": "2026-07-12",
        "category": "SYNTHETIC_TEST",
        "scheduled_start_exchange_ts": 1783864800.0,
        "legs": [
            {"leg_id": leg_id, "ticker": ticker}
            for leg_id, ticker in legs
        ],
    }
    raw_boundary = {
        "event_id": event_id,
        "start_source_class": "official_exact",
        "positive_window1_provable": True,
        "exact_start_utc": "2026-07-12T12:00:00+00:00",
        "guard_band": {
            "guard_id": "official-point-strict-60s-v1",
            "positive_guard_seconds": 60,
        },
        "guard_censor_reason": None,
    }
    normalized_boundary = boundary_contract(raw_boundary)
    fills = {}
    references = {}
    for index, (leg_id, ticker) in enumerate(legs):
        fills[leg_id] = SimpleNamespace(
            candidate_id=candidate_id,
            event_id=event_id,
            event_date="2026-07-12",
            leg_id=leg_id,
            ticker=ticker,
            evidence_type="PRICE_REACHED",
            evidence_receipt=f"synthetic-fill-receipt-{index}",
            evidence_timestamp=1783857540.0 + index,
            accounting_fill_price_cents=40 + index,
            accounting_quantity=5,
            order_interval_id=f"synthetic-interval-{index}",
            fill_role="first_leg" if index == 0 else "sibling",
            sibling_d2_cents=None if index == 0 else 1,
            strict_combined_budget_passed=True,
            action_authority="SYNTHETIC_TEST",
        )
        references[leg_id] = Window1CloseReference(
            event_id=event_id,
            event_date="2026-07-12",
            leg_id=leg_id,
            ticker=ticker,
            available=True,
            window1_close_cents=42 + index,
            reference_ts=1783857600.0 + index,
            reference_receipt=f"synthetic-reference-receipt-{index}",
            reference_source="SYNTHETIC_TRUE_PRINT",
            t8_floor_ts=1783836000.0,
            guarded_cutoff_ts=1783857540.0,
            boundary_source_class="official_exact",
            boundary_guard_id="official-point-strict-60s-v1",
            reason=None,
        )
    return {
        "candidate_id": candidate_id,
        "parent_candidate_id": CANDIDATE_TO_PARENT[candidate_id],
        "event": event,
        "boundary": raw_boundary,
        "normalized_boundary": normalized_boundary,
        "fills_by_leg": fills,
        "references_by_leg": references,
    }


@pytest.fixture(scope="module")
def guarded_direct_scorer(
    development_event_ids: frozenset[str],
) -> tuple[Callable[..., dict[str, Any]], dict[str, int]]:
    census = {
        "synthetic_scorer_calls": 0,
        "real_development_scorer_call_attempts": 0,
    }

    def call(**kwargs: Any) -> dict[str, Any]:
        event_id = str(kwargs["event"]["event_id"])
        if event_id in development_event_ids:
            census["real_development_scorer_call_attempts"] += 1
            raise AssertionError(
                "direct scorer received frozen development event_id"
            )
        census["synthetic_scorer_calls"] += 1
        from window1_t2_frontier_regret_scorer_v1 import score_t2_event
        return score_t2_event(**kwargs)

    yield call, census
    assert census == {
        "synthetic_scorer_calls": 3,
        "real_development_scorer_call_attempts": 0,
    }


def test_V3_flattened_boundary_preserves_exact_error(
    synthetic_score_kwargs: dict[str, Any],
    guarded_direct_scorer,
) -> None:
    call, census = guarded_direct_scorer
    kwargs = dict(synthetic_score_kwargs)
    kwargs.pop("normalized_boundary")
    kwargs["boundary"] = synthetic_score_kwargs["normalized_boundary"]
    with pytest.raises(
        ReferenceError,
        match="positive boundary lacks V5 guard artifact",
    ):
        call(**kwargs)
    assert census["synthetic_scorer_calls"] == 1
    assert census["real_development_scorer_call_attempts"] == 0


def test_equivalent_full_raw_V5_shaped_boundary_passes_seam(
    synthetic_score_kwargs: dict[str, Any],
    guarded_direct_scorer,
) -> None:
    call, census = guarded_direct_scorer
    kwargs = dict(synthetic_score_kwargs)
    kwargs.pop("normalized_boundary")
    kwargs["boundary"] = dict(synthetic_score_kwargs["boundary"])
    row = call(**kwargs)
    assert row["event_id"] == synthetic_score_kwargs["event"]["event_id"]
    assert row["boundary_status"] == "positive"
    assert census["synthetic_scorer_calls"] == 2
    assert census["real_development_scorer_call_attempts"] == 0


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
    synthetic_score_kwargs: dict[str, Any],
    guarded_direct_scorer,
) -> None:
    call, census = guarded_direct_scorer
    kwargs = dict(synthetic_score_kwargs)
    kwargs.pop("normalized_boundary")
    kwargs["boundary"] = synthetic_score_kwargs["normalized_boundary"]
    with pytest.raises(ReferenceError):
        call(**kwargs)
    assert census["synthetic_scorer_calls"] == 3
    assert census["real_development_scorer_call_attempts"] == 0


def test_attempt_accounting_survives_injected_scorer_exception(
    synthetic_score_kwargs: dict[str, Any],
) -> None:
    prepared = SimpleNamespace(
        candidate_id=synthetic_score_kwargs["candidate_id"],
        event_id=synthetic_score_kwargs["event"]["event_id"],
        score_kwargs={
            key: value for key, value in synthetic_score_kwargs.items()
            if key != "normalized_boundary"
        },
    )
    accounting = ScoreAccounting()
    snapshots: list[dict] = []

    def persist(value: ScoreAccounting) -> None:
        snapshots.append(dict(value.to_dict()))

    def explode(**_: object) -> dict:
        raise RuntimeError("injected scorer failure")

    with pytest.raises(RuntimeError, match="injected scorer failure"):
        invoke_prepared_score(
            prepared=prepared,
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
        "active_candidate_id": prepared.candidate_id,
        "active_event_id": prepared.event_id,
    }]


def test_success_accounting_completes_only_after_return(
    synthetic_score_kwargs: dict[str, Any],
) -> None:
    prepared = SimpleNamespace(
        candidate_id=synthetic_score_kwargs["candidate_id"],
        event_id=synthetic_score_kwargs["event"]["event_id"],
        score_kwargs={
            key: value for key, value in synthetic_score_kwargs.items()
            if key != "normalized_boundary"
        },
    )
    accounting = ScoreAccounting()
    snapshots: list[dict] = []

    def scorer(**_: object) -> dict:
        assert accounting.scorer_call_attempts == 1
        assert accounting.completed_event_rows == 0
        return {"ok": True}

    result = invoke_prepared_score(
        prepared=prepared,
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
    receipt = read("EXECUTION_READINESS_NO_SCORE_RECEIPT.json")
    assert receipt["prepared_scorer_calls"] == 6432
    assert receipt["scorer_call_attempts"] == 0
    assert receipt["completed_event_rows"] == 0
    assert receipt["completed_candidates"] == 0
    assert receipt["results_directory_absent"] is True


@pytest.mark.parametrize(
    "authorization",
    [CONSUMED_V2_AUTHORIZATION, CONSUMED_V3_AUTHORIZATION],
)
def test_consumed_authorizations_are_frozen_as_rejected(
    authorization: str,
) -> None:
    package = read("SCORING_INPUT_MANIFEST.json")
    assert authorization in package["consumed_authorizations_rejected"]


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
    package = read("SCORING_INPUT_MANIFEST.json")
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
