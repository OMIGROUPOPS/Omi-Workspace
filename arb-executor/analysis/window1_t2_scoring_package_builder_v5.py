#!/usr/bin/env python3
"""Build the score-free Window-1 T2 test-honesty package V5."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from window1_t2_reference_boundary_v3 import canonical_sha256
from window1_t2_scoring_package_builder_v4 import (
    artifact_identity as v4_artifact_identity,
    assert_score_free,
    binary_identity,
    git_blob_oid,
    identity_bytes,
    read_json,
    source_identity,
    write_json,
)
from window1_t2_scoring_runtime_v4 import no_score_seam_probe


VERSION = "window1-t2-scoring-package-builder-v5"
IMPLEMENTATION_PARENT = "9cc8f1cc7b0693e00ce0f537532d41aab0a5ef7c"
PACKAGE_DIRECTORY = (
    ".claude/window1_t2_scoring_package_v5_prerun_20260729"
)
EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v5"
)
RESULTS_DIRECTORY = f".claude/window1_t2_results_{EXECUTION_ID}"
RETIRED_V4_EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v4"
)
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
COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/window1_t2_scoring_runner_v5.py "
    f"--repo . --package {PACKAGE_DIRECTORY}/SCORING_INPUT_MANIFEST.json "
    "--mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
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
V4_PACKAGE_COMMIT = IMPLEMENTATION_PARENT
V4_PACKAGE = Path(
    ".claude/window1_t2_scoring_package_v4_prerun_20260729"
)
V5_PACKAGE = Path(PACKAGE_DIRECTORY)
V4_BUNDLE = (
    "bb9cf97b7b4d80e758f943df20ca3fa0aacdcaedc436f58e2928024c01356c2e"
)
V4_TEST = Path(
    "arb-executor/tests/test_window1_t2_scoring_package_v4.py"
)
V5_RUNNER = Path(
    "arb-executor/analysis/window1_t2_scoring_runner_v5.py"
)
V5_BUILDER = Path(
    "arb-executor/analysis/window1_t2_scoring_package_builder_v5.py"
)
V5_FREEZER = Path(
    "arb-executor/analysis/window1_t2_scoring_package_freeze_v5.py"
)
V5_TEST = Path(
    "arb-executor/tests/test_window1_t2_scoring_package_v5.py"
)
V5_CONTRACT = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_T2_SCORING_TEST_HONESTY_CONTRACT_V5.json"
)
TEXT_SUFFIXES = {
    ".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml",
}
NULL_FIELDS = {
    "C", "PC", "IC", "S", "frontier", "regret", "attribution",
    "performance", "ranking", "selection", "result", "results",
}


class BuildError(RuntimeError):
    """The V5 score-free correction could not be frozen honestly."""


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def git_show_bytes(repo: Path, commit: str, path: Path) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path.as_posix()}"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def artifact_identity(path: Path, output: Path) -> dict[str, Any]:
    row = v4_artifact_identity(path, output)
    row["path"] = (
        V5_PACKAGE / path.relative_to(output)
    ).as_posix()
    return row


def _canonical_test_identity(raw: bytes) -> dict[str, Any]:
    canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return {
        "working_tree_bytes": len(raw),
        "identity_bytes": len(canonical),
        "sha256": hashlib.sha256(canonical).hexdigest(),
        "git_blob_oid": git_blob_oid(canonical),
        "newline_identity": "canonical_LF",
    }


def _test_source_correction(repo: Path) -> dict[str, Any]:
    old_raw = git_show_bytes(repo, IMPLEMENTATION_PARENT, V4_TEST)
    new_raw = (repo / V4_TEST).read_bytes()
    old = _canonical_test_identity(old_raw)
    new = _canonical_test_identity(new_raw)
    old["committed_blob"] = git(
        repo, "rev-parse", f"{IMPLEMENTATION_PARENT}:{V4_TEST.as_posix()}"
    )
    if old["git_blob_oid"] != old["committed_blob"]:
        raise BuildError("V4 test committed blob/canonical bytes disagree")
    if old["sha256"] == new["sha256"]:
        raise BuildError("V4 test honesty correction is absent")
    return {
        "schema_version": VERSION + "-test-source-correction-v1",
        "path": V4_TEST.as_posix(),
        "permitted_inherited_modification": True,
        "old_parent": IMPLEMENTATION_PARENT,
        "old": old,
        "new": new,
        "runtime_files_modified": [],
        "V4_package_artifacts_modified": [],
        "semantic_scope": "construction_test_inputs_and_claim_honesty_only",
    }


def _v4_activity_correction(
    source_correction: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": VERSION + "-V4-test-activity-correction-v1",
        "V4_package_commit": V4_PACKAGE_COMMIT,
        "corrected_test_path": V4_TEST.as_posix(),
        "old_test_blob": source_correction["old"]["committed_blob"],
        "old_test_sha256": source_correction["old"]["sha256"],
        "real_development_scorer_call_attempts": 3,
        "completed_in_memory_event_rows": 1,
        "completed_candidates": 0,
        "persisted_result_rows": 0,
        "aggregate_frontier_regret_output_rows": 0,
        "holdout_access": False,
        "live_or_trading_access": False,
        "V4_authorization_exists": False,
        "V4_execute_mode_invoked": False,
        "V4_results_directory_created": False,
        "false_claim": "zero real-population scorer attempts",
        "correction_method": (
            "additive V5 receipt; frozen V4 artifacts are not amended"
        ),
        "V4_artifacts_amended": False,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "attribution": None,
        "performance": None,
        "ranking": None,
        "selection": None,
    }


def _test_honesty_receipt(
    repo: Path,
    seam: Mapping[str, Any],
) -> dict[str, Any]:
    path = repo / V4_TEST
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    direct_score_nodes = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "score_t2_event"
    ]
    guarded_calls = source.count("call(**kwargs)")
    if (
        len(direct_score_nodes) != 1
        or guarded_calls != 3
        or "if event_id in development_event_ids:" not in source
        or "direct scorer received frozen development event_id" not in source
        or "def synthetic_score_kwargs" not in source
    ):
        raise BuildError("V5 direct-scorer guard/source census changed")
    event_ledger = repo / (
        read_json(repo / V4_PACKAGE / "SCORING_INPUT_MANIFEST.json")
        ["roles"]["event_ledger"]
    )
    event_ids = {
        str(json.loads(line)["event_id"])
        for line in event_ledger.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    if len(event_ids) != 804:
        raise BuildError("development event guard is not D=804")
    return {
        "schema_version": VERSION + "-test-honesty-receipt-v1",
        "frozen_development_event_id_count": len(event_ids),
        "direct_score_t2_event_call_sites": 1,
        "direct_call_site_location": (
            "guarded_direct_scorer.call after development-ID rejection"
        ),
        "synthetic_direct_scorer_calls_expected": guarded_calls,
        "real_development_scorer_call_attempts_expected": 0,
        "synthetic_event_boundary_fill_reference_inputs": True,
        "guard_wraps_every_direct_scorer_test": True,
        "guard_failure_law": (
            "event_id in frozen development ledger raises before scorer import"
        ),
        "scorer_import_is_after_guard": True,
        "real_prepared_calls_inspected": seam["prepared_scorer_calls"],
        "real_prepared_calls_scored": 0,
        "full_raw_V5_prepared_calls": seam[
            "full_raw_V5_boundary_count"
        ],
        "normalized_scorer_boundaries": seam[
            "normalized_boundary_selected_count"
        ],
        "no_score_seam_scorer_call_attempts": seam[
            "scorer_call_attempts"
        ],
        "results_directory_created": False,
        "V4_runtime_semantics_changed": False,
    }


def _expected_schema() -> dict[str, Any]:
    return {
        "schema_version": "window1-t2-scoring-output-schema-v5",
        "execution_id": EXECUTION_ID,
        "candidate_count": 8,
        "D_per_candidate": 804,
        "runtime_semantics": "byte-identical V4 runtime",
        "performance_outputs": {
            "C": None,
            "PC": None,
            "IC": None,
            "S": None,
            "frontier": None,
            "regret": None,
            "attribution": None,
            "performance": None,
            "ranking": None,
            "selection": None,
        },
    }


def _audit_instruction() -> str:
    return """# Independent Window-1 T2 scoring-package V5 audit

Do not authorize or execute V5.

1. Before opening expected V5 summaries, independently inspect the parent V4
   test blob and establish its three real-development `score_t2_event`
   attempts, one completed in-memory event row, zero completed candidates,
   zero persisted result rows, and zero aggregate/frontier/regret output.
2. Freeze that independent receipt, then compare it to
   `V4_CONSTRUCTION_TEST_ACTIVITY_CORRECTION.json`. Any mismatch is BLOCK;
   no post-hoc reconciliation is allowed.
3. Inspect the corrected V4 test source independently. Enumerate every direct
   scorer call. Prove all event, boundary, fill, and reference inputs are
   synthetic and a frozen-development-event-ID guard runs before scorer import.
4. Instrument the corrected V4 and V5 test runs. Require zero development
   scorer attempts, exactly three guarded synthetic scorer calls, 6,432 real
   prepared calls inspected without scoring, and no V5 results directory.
5. Recompute the sole inherited-file old/new blobs and hashes. Prove every V4
   package artifact and runtime source is byte-identical and V5 changes no
   scoring semantic.
6. Recompute all manifests, bundle identity, null scans, authorization/ID
   rejection, complete test collection with zero omissions/deselections, and
   both clean deterministic builds.

A PASS certifies a score-free V5 PRE-RUN only. It is not authorization.
"""


def _report(
    bundle: str,
    seam: Mapping[str, Any],
    correction: Mapping[str, Any],
) -> str:
    return f"""# Window-1 T2 scoring-package V5 PRE-RUN

Status: **SCORE-FREE / NOT AUTHORIZED / NOT EXECUTED**

V5 corrects construction-test honesty only. The frozen V4 runtime semantics
and every V4 package artifact remain unchanged. The sole inherited-file edit
is `{V4_TEST.as_posix()}`.

The V4 construction tests made three real-development scorer-call attempts,
completed one in-memory event row, completed zero candidates, and persisted
zero result rows. V5 records that truth additively; V4 is not amended.

The corrected tests use three synthetic scorer calls and reject all 804 frozen
development event IDs before importing the scorer. The real population is
limited to {seam['prepared_scorer_calls']} prepared-call inspections through
the shared V4 no-score seam, with zero scorer calls.

Input-bundle SHA-256: `{bundle}`.

No V5 authorization or results directory exists. C/PC/IC/S, frontier, regret,
attribution, ranking, selection, and performance remain null. No holdout,
live, network-runtime, Kalshi, or trading surface was accessed.
"""


def _merge_source_manifest(
    repo: Path,
    v4_source: Mapping[str, Any],
) -> dict[str, Any]:
    replacements = {
        V4_TEST.as_posix(): source_identity(
            repo, V4_TEST, "corrected_V4_synthetic_only_tests"
        ),
    }
    rows = []
    for row in v4_source["committed_source_inputs"]:
        rows.append(replacements.get(str(row["path"]), dict(row)))
    existing = {str(row["path"]) for row in rows}
    additions = (
        (V5_RUNNER, "V5_identity_runner"),
        (V5_BUILDER, "V5_package_builder"),
        (V5_FREEZER, "V5_two_clean_build_freezer"),
        (V5_TEST, "V5_test_honesty_tests"),
        (V5_CONTRACT, "V5_test_honesty_contract"),
    )
    for path, role in additions:
        if path.as_posix() in existing:
            raise BuildError(f"duplicate V5 source path: {path}")
        rows.append(source_identity(repo, path, role))
    rows.sort(key=lambda row: str(row["path"]))
    return {
        "schema_version": VERSION + "-source-hash-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "V4_package_commit": V4_PACKAGE_COMMIT,
        "V4_runtime_semantics_changed": False,
        "committed_source_inputs": rows,
        "frozen_binary_inputs": v4_source["frozen_binary_inputs"],
        "private_runtime_inputs": v4_source["private_runtime_inputs"],
        "private_cache_verification": v4_source[
            "private_cache_verification"
        ],
        "scorer_call_attempts": 0,
        "holdout_opened": False,
        "live_or_production_access": False,
    }


def build(*, repo: Path, output: Path) -> dict[str, Any]:
    repo = repo.resolve()
    if output.exists():
        raise BuildError("V5 output already exists")
    if git(repo, "rev-parse", "HEAD") != IMPLEMENTATION_PARENT:
        raise BuildError("V5 HEAD differs from exact V4 parent")
    if (repo / RESULTS_DIRECTORY).exists():
        raise BuildError("V5 results directory exists")
    v4_manifest = read_json(
        repo / V4_PACKAGE / "SCORING_INPUT_MANIFEST.json"
    )
    if (
        v4_manifest.get("input_bundle_sha256") != V4_BUNDLE
        or v4_manifest.get("schema_version")
        != "window1-t2-scoring-input-manifest-v4"
    ):
        raise BuildError("frozen V4 package binding changed")
    output.mkdir(parents=True)

    seam = no_score_seam_probe(
        repo=repo,
        roles=v4_manifest["roles"],
        candidate_ids=CANDIDATE_IDS,
        candidate_to_parent=CANDIDATE_TO_PARENT,
        results_directory=RESULTS_DIRECTORY,
    )
    correction = _test_source_correction(repo)
    activity = _v4_activity_correction(correction)
    honesty = _test_honesty_receipt(repo, seam)
    write_json(output / "TEST_SOURCE_CORRECTION_RECEIPT.json", correction)
    write_json(
        output / "V4_CONSTRUCTION_TEST_ACTIVITY_CORRECTION.json",
        activity,
    )
    write_json(output / "TEST_HONESTY_RECEIPT.json", honesty)
    write_json(output / "RUNTIME_SEAM_PROBE_RECEIPT.json", {
        **seam,
        "schema_version": VERSION + "-runtime-seam-probe-v1",
        "real_prepared_calls_inspected_without_scoring": (
            seam["prepared_scorer_calls"]
        ),
        "real_development_scorer_call_attempts": 0,
    })
    write_json(output / "EXECUTION_READINESS_NO_SCORE_RECEIPT.json", {
        **seam,
        "schema_version": VERSION + "-execution-readiness-no-score-v1",
        "shared_V4_runtime": True,
        "real_development_population_loaded_for_inspection": True,
        "real_development_population_scored": False,
        "synthetic_test_scorer_calls": 3,
        "scorer_call_attempts": 0,
        "completed_event_rows": 0,
        "completed_candidates": 0,
        "results_directory_absent": True,
        "holdout_opened": False,
        "live_or_production_access": False,
        "network_or_trading_access": False,
    })
    write_json(output / "EXPECTED_OUTPUT_SCHEMA_V5.json", _expected_schema())
    (output / "INDEPENDENT_AUDIT_INSTRUCTION.md").write_text(
        _audit_instruction(), encoding="utf-8", newline="\n"
    )

    v4_source = read_json(
        repo / V4_PACKAGE / "SOURCE_HASH_MANIFEST.json"
    )
    source_manifest = _merge_source_manifest(repo, v4_source)
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden-access-v1",
        "authorization_issued": False,
        "execute_mode_invoked": False,
        "real_development_scorer_call_attempts": 0,
        "results_directory_created": False,
        "holdout_access": False,
        "live_network_runtime_Kalshi_or_trading_access": False,
        "order_position_exit_settlement_DCA_Window2_access": False,
        "tuning_ranking_selection_deployment": False,
    })

    roles = dict(v4_manifest["roles"])
    roles.update({
        "test_source_correction_receipt": (
            V5_PACKAGE / "TEST_SOURCE_CORRECTION_RECEIPT.json"
        ).as_posix(),
        "v4_construction_test_activity_correction": (
            V5_PACKAGE / "V4_CONSTRUCTION_TEST_ACTIVITY_CORRECTION.json"
        ).as_posix(),
        "test_honesty_receipt": (
            V5_PACKAGE / "TEST_HONESTY_RECEIPT.json"
        ).as_posix(),
        "runtime_seam_probe_receipt": (
            V5_PACKAGE / "RUNTIME_SEAM_PROBE_RECEIPT.json"
        ).as_posix(),
        "execution_readiness_no_score_receipt": (
            V5_PACKAGE / "EXECUTION_READINESS_NO_SCORE_RECEIPT.json"
        ).as_posix(),
        "expected_output_schema": (
            V5_PACKAGE / "EXPECTED_OUTPUT_SCHEMA_V5.json"
        ).as_posix(),
        "source_hash_manifest": (
            V5_PACKAGE / "SOURCE_HASH_MANIFEST.json"
        ).as_posix(),
        "test_honesty_contract_v5": V5_CONTRACT.as_posix(),
    })
    critical = {}
    for role, relative in sorted(roles.items()):
        if role == "guarded_cache_directory":
            continue
        relative_path = Path(relative)
        path = repo / relative_path
        if str(relative).startswith(V5_PACKAGE.as_posix()):
            path = output / relative_path.relative_to(V5_PACKAGE)
        raw = identity_bytes(path)
        critical[role] = {
            "path": str(relative),
            "identity_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    payload = {
        "schema_version": "window1-t2-scoring-input-bundle-v5",
        "package_revision": "V5_TEST_HONESTY_CORRECTION",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "V4_package_commit": V4_PACKAGE_COMMIT,
        "V4_input_bundle_sha256": V4_BUNDLE,
        "V4_runtime_semantics_changed": False,
        "retired_execution_id": RETIRED_V4_EXECUTION_ID,
        "consumed_authorizations_rejected": [
            CONSUMED_V2_AUTHORIZATION,
            CONSUMED_V3_AUTHORIZATION,
        ],
        "consumed_execution_ids_rejected": [
            CONSUMED_V2_EXECUTION_ID,
            CONSUMED_V3_EXECUTION_ID,
            RETIRED_V4_EXECUTION_ID,
        ],
        "execution_id": EXECUTION_ID,
        "D": 804,
        "fit_D": 525,
        "post_fit_D": 279,
        "candidate_ids": list(CANDIDATE_IDS),
        "roles": roles,
        "critical_role_identities": critical,
        "command_template_literal": COMMAND_TEMPLATE,
        "controlling_T2_PASS": v4_manifest["controlling_T2_PASS"],
        "audited_scorer_commit": v4_manifest["audited_scorer_commit"],
        "T2_prerun": v4_manifest["T2_prerun"],
        "T2_PASS": v4_manifest["T2_PASS"],
    }
    bundle = canonical_sha256(payload)
    manifest = {
        **payload,
        "schema_version": "window1-t2-scoring-input-manifest-v5",
        "input_bundle_payload": payload,
        "input_bundle_sha256": bundle,
        "future_independent_PASS_required": True,
        "future_authorization_required": True,
        "scored": False,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "attribution": None,
        "performance": None,
        "ranking": None,
        "selection": None,
    }
    write_json(output / "SCORING_INPUT_MANIFEST.json", manifest)
    write_json(output / "NULL_METRIC_NO_EXECUTION_RECEIPT.json", {
        "schema_version": VERSION + "-null-no-execution-v1",
        "execution_id": EXECUTION_ID,
        "input_bundle_sha256": bundle,
        "all_committed_performance_fields_null": True,
        "V4_runtime_semantics_changed": False,
        "real_development_scorer_call_attempts": 0,
        "synthetic_test_scorer_calls": 3,
        "completed_event_rows": 0,
        "completed_candidates": 0,
        "results_directory": RESULTS_DIRECTORY,
        "results_directory_exists": False,
        "authorization_exists": False,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "attribution": None,
        "performance": None,
        "ranking": None,
        "selection": None,
    })
    (output / "PRE_RUN_REPORT.md").write_text(
        _report(bundle, seam, correction),
        encoding="utf-8",
        newline="\n",
    )

    artifacts = [
        artifact_identity(path, output)
        for path in sorted(output.iterdir())
        if path.is_file()
        and path.name not in {
            "ARTIFACT_HASH_MANIFEST.json",
            "DETERMINISTIC_REGENERATION_RECEIPT.json",
        }
    ]
    write_json(output / "ARTIFACT_HASH_MANIFEST.json", {
        "schema_version": VERSION + "-artifact-hash-manifest-v1",
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "manifest_self_excluded": True,
        "determinism_receipt_excluded": True,
    })
    for path in output.iterdir():
        if path.suffix == ".json":
            assert_score_free(read_json(path))
    if (repo / RESULTS_DIRECTORY).exists():
        raise BuildError("V5 results directory appeared during build")
    return {
        "schema_version": VERSION + "-build-receipt-v1",
        "input_bundle_sha256": bundle,
        "prepared_scorer_calls_inspected": seam["prepared_scorer_calls"],
        "real_development_scorer_call_attempts": 0,
        "synthetic_test_scorer_calls": 3,
        "file_count": len([p for p in output.iterdir() if p.is_file()]),
        "output": str(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir.resolve()
        if args.output_dir.is_absolute()
        else (repo / args.output_dir).resolve()
    )
    print(json.dumps(build(repo=repo, output=output), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
