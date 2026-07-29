from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "arb-executor" / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from window1_t2_scoring_runner_v5 import (
    CANDIDATE_IDS,
    CONSUMED_V2_AUTHORIZATION,
    CONSUMED_V3_AUTHORIZATION,
    EXECUTION_ID,
    RESULTS_DIRECTORY,
    RETIRED_V4_EXECUTION_ID,
    RunnerError,
    authorize_execute,
    validate_package,
)


PACKAGE = (
    ROOT
    / ".claude"
    / "window1_t2_scoring_package_v5_prerun_20260729"
)
V4_PACKAGE = (
    ROOT
    / ".claude"
    / "window1_t2_scoring_package_v4_prerun_20260729"
)
MANIFEST = PACKAGE / "SCORING_INPUT_MANIFEST.json"
CORRECTED_TEST = (
    ROOT / "arb-executor/tests/test_window1_t2_scoring_package_v4.py"
)


def read(name: str) -> dict:
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def test_V5_package_identity_and_runtime_semantics() -> None:
    validated = validate_package(
        ROOT, MANIFEST, verify_private_inputs=False
    )
    package = validated["package"]
    assert package["schema_version"] == (
        "window1-t2-scoring-input-manifest-v5"
    )
    assert package["package_revision"] == "V5_TEST_HONESTY_CORRECTION"
    assert package["V4_runtime_semantics_changed"] is False
    assert package["D"] == 804
    assert tuple(package["candidate_ids"]) == CANDIDATE_IDS


def test_V4_activity_is_corrected_additively() -> None:
    row = read("V4_CONSTRUCTION_TEST_ACTIVITY_CORRECTION.json")
    assert row["real_development_scorer_call_attempts"] == 3
    assert row["completed_in_memory_event_rows"] == 1
    assert row["completed_candidates"] == 0
    assert row["persisted_result_rows"] == 0
    assert row["aggregate_frontier_regret_output_rows"] == 0
    assert row["V4_artifacts_amended"] is False
    assert row["V4_authorization_exists"] is False
    assert row["V4_execute_mode_invoked"] is False


def test_only_permitted_inherited_test_source_changed() -> None:
    row = read("TEST_SOURCE_CORRECTION_RECEIPT.json")
    assert row["path"] == (
        "arb-executor/tests/test_window1_t2_scoring_package_v4.py"
    )
    assert row["old"]["git_blob_oid"] == (
        "ad314242d0e6339dabfbf6a1748d26570c483ad0"
    )
    assert row["old"]["sha256"] == (
        "d9516b9794330da5721c4da5cb5f005f61829b7bde691e38fa306813544496c2"
    )
    assert row["new"]["sha256"] != row["old"]["sha256"]
    assert row["runtime_files_modified"] == []
    assert row["V4_package_artifacts_modified"] == []


def test_direct_scorer_source_is_synthetic_and_guarded() -> None:
    source = CORRECTED_TEST.read_text(encoding="utf-8")
    tree = ast.parse(source)
    direct = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "score_t2_event"
    ]
    assert len(direct) == 1
    assert source.count("call(**kwargs)") == 3
    assert "if event_id in development_event_ids:" in source
    assert "def synthetic_score_kwargs" in source
    assert source.index("if event_id in development_event_ids:") < (
        source.index(
            "from window1_t2_frontier_regret_scorer_v1 "
            "import score_t2_event"
        )
    )


def test_real_prepared_calls_are_inspection_only() -> None:
    row = read("TEST_HONESTY_RECEIPT.json")
    assert row["frozen_development_event_id_count"] == 804
    assert row["synthetic_direct_scorer_calls_expected"] == 3
    assert row["real_development_scorer_call_attempts_expected"] == 0
    assert row["real_prepared_calls_inspected"] == 6432
    assert row["real_prepared_calls_scored"] == 0
    assert row["no_score_seam_scorer_call_attempts"] == 0


def test_builder_and_real_preparation_do_not_import_scorer() -> None:
    for relative in (
        "arb-executor/analysis/window1_t2_scoring_package_builder_v5.py",
        "arb-executor/analysis/window1_t2_scoring_runtime_v4.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            str(node.module)
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        assert "window1_t2_frontier_regret_scorer_v1" not in imports
        assert "window1_t2_scoring_runner_v4" not in imports
        assert "window1_t2_scoring_runner_v5" not in imports


def test_V5_real_input_readiness_stays_no_score() -> None:
    row = read("EXECUTION_READINESS_NO_SCORE_RECEIPT.json")
    assert row["prepared_scorer_calls"] == 6432
    assert row["full_raw_V5_boundary_count"] == 6432
    assert row["normalized_boundary_selected_count"] == 0
    assert row["scorer_call_attempts"] == 0
    assert row["results_directory_absent"] is True


@pytest.mark.parametrize(
    "authorization",
    [CONSUMED_V2_AUTHORIZATION, CONSUMED_V3_AUTHORIZATION],
)
def test_consumed_authorizations_rejected(
    authorization: str,
) -> None:
    with pytest.raises(RunnerError, match="consumed V2/V3"):
        authorize_execute(
            ROOT,
            {"package": {}, "head": "0" * 40},
            authorization,
            "does-not-matter",
        )


def test_V4_execution_identity_is_retired() -> None:
    assert RETIRED_V4_EXECUTION_ID.endswith("scorepkg-v4")
    assert EXECUTION_ID.endswith("scorepkg-v5")
    manifest = read("SCORING_INPUT_MANIFEST.json")
    assert RETIRED_V4_EXECUTION_ID in (
        manifest["consumed_execution_ids_rejected"]
    )


def test_V4_package_artifacts_remain_parent_bytes() -> None:
    for path in sorted(V4_PACKAGE.iterdir()):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        parent = subprocess.run(
            ["git", "show", f"9cc8f1cc:{relative}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
        assert hashlib.sha256(path.read_bytes()).digest() == (
            hashlib.sha256(parent).digest()
        )


def test_metrics_null_and_no_results_or_authorization() -> None:
    package = read("SCORING_INPUT_MANIFEST.json")
    for key in (
        "C", "PC", "IC", "S", "frontier", "regret",
        "attribution", "performance", "ranking", "selection",
    ):
        assert package[key] is None
    assert package["scored"] is False
    assert package["future_independent_PASS_required"] is True
    assert package["future_authorization_required"] is True
    assert not (ROOT / RESULTS_DIRECTORY).exists()
    assert read("FORBIDDEN_ACCESS_RECEIPT.json")[
        "authorization_issued"
    ] is False


def test_artifact_manifest_and_bundle_recompute() -> None:
    artifact = read("ARTIFACT_HASH_MANIFEST.json")
    assert artifact["artifact_count"] == len(artifact["artifacts"])
    for row in artifact["artifacts"]:
        path = ROOT / row["path"]
        raw = path.read_bytes().replace(b"\r\n", b"\n").replace(
            b"\r", b"\n"
        )
        assert len(raw) == row["identity_bytes"]
        assert hashlib.sha256(raw).hexdigest() == row["sha256"]
    package = read("SCORING_INPUT_MANIFEST.json")
    compact = json.dumps(
        package["input_bundle_payload"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    assert hashlib.sha256(compact).hexdigest() == (
        package["input_bundle_sha256"]
    )


def test_determinism_receipt_is_two_clean_builds() -> None:
    row = read("DETERMINISTIC_REGENERATION_RECEIPT.json")
    assert row["clean_build_count"] == 2
    assert row["A_equals_B"] is True
    assert row["A_equals_frozen"] is True
    assert row["real_development_scorer_call_attempts"] == 0
    assert row["results_directory_created"] is False
