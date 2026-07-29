#!/usr/bin/env python3
"""Build the score-free Window-1 T2 transitive-boundary package V4."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

from window1_t2_reference_boundary_v3 import canonical_sha256, sha256_file
from window1_t2_scoring_runtime_v4 import no_score_seam_probe


VERSION = "window1-t2-scoring-package-builder-v4"
IMPLEMENTATION_PARENT = "a758279184ab0f367a3ce74a69da851608645e19"
V3_PACKAGE_COMMIT = "a758279184ab0f367a3ce74a69da851608645e19"
V3_FAILURE_COMMIT = "9cd2bea5487d8e558c42c8950263b44179054a68"
V3_AUTHORIZATION = "40a6314fe0790416a260879cd9a071072e26e9a0"
V2_AUTHORIZATION = "e4e57baca0c2172244e63f45b2086f2ef4df53e9"
T2_PRERUN = "87ac9382c23b586f536cf457883c507ebf366ba3"
T2_PASS = "8743939745e25f090d69dfd4d56906a93671f331"
V3_PACKAGE = Path(
    ".claude/window1_t2_scoring_package_v3_prerun_20260728"
)
V4_PACKAGE = Path(
    ".claude/window1_t2_scoring_package_v4_prerun_20260729"
)
RUNTIME = Path(
    "arb-executor/analysis/window1_t2_scoring_runtime_v4.py"
)
RUNNER = Path(
    "arb-executor/analysis/window1_t2_scoring_runner_v4.py"
)
BUILDER = Path(
    "arb-executor/analysis/window1_t2_scoring_package_builder_v4.py"
)
FREEZER = Path(
    "arb-executor/analysis/window1_t2_scoring_package_freeze_v4.py"
)
TEST = Path(
    "arb-executor/tests/test_window1_t2_scoring_package_v4.py"
)
CONTRACT = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_T2_SCORING_TRANSITIVE_BOUNDARY_CONTRACT_V4.json"
)
EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v4"
)
V2_EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v2"
)
V3_EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v3"
)
RESULTS_DIRECTORY = ".claude/window1_t2_results_" + EXECUTION_ID
CANDIDATES = (
    "w1_t2__macro_hold__fixed_admission_parent_control",
    "w1_t2__macro_hold__non_displacing_target_completeness",
    "w1_t2__macro_hold__target_completeness_evidence_decay",
    "w1_t2__macro_hold__full_causal_divot_stack",
    "w1_t2__macro_micro__fixed_admission_parent_control",
    "w1_t2__macro_micro__non_displacing_target_completeness",
    "w1_t2__macro_micro__target_completeness_evidence_decay",
    "w1_t2__macro_micro__full_causal_divot_stack",
)
PARENTS = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
CANDIDATE_TO_PARENT = {
    candidate: PARENTS[0 if "__macro_hold__" in candidate else 1]
    for candidate in CANDIDATES
}
COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/window1_t2_scoring_runner_v4.py "
    f"--repo . --package {V4_PACKAGE.as_posix()}/"
    "SCORING_INPUT_MANIFEST.json --mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
V3_FAILURE_DIRECTORY = (
    ".claude/window1_t2_results_"
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v3"
)
V3_FAILURE_HASHES = {
    "EXECUTION_FAILURE.json": (
        "d7652395adf8e1b7d2560d5de2768084fcdd32d01db66d49a34c5a6eec184f07"
    ),
    "EXECUTION_START_RECEIPT.json": (
        "e81933e73025391643b3a0d0bc412c9e2f0e2c2e8a0440555ff4885cd895d0b3"
    ),
    "OUTPUT_HASH_MANIFEST.json": (
        "f862f1c79b635c9b6c6b90de27e784a18e1fce0797a5e586a4eb44d389909fa6"
    ),
    "PROGRESS.log": (
        "da2d8d7d122e3bf7514a584af65f3c02a2711487e2d0ead688ec1c806c9c0b47"
    ),
    "STDERR.log": (
        "235b93ff3c8c4c0d92dd45976856d44f1ea89d70e2d1bd59ea2dca18edc64c3c"
    ),
}
TEXT_SUFFIXES = {
    ".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml",
}
NULL_FIELDS = {
    "C", "PC", "IC", "S", "frontier", "regret", "attribution",
    "performance", "ranking", "selection", "result", "results",
}


class BuildError(RuntimeError):
    """The V4 PRE-RUN could not be frozen without scoring."""


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def git_show_bytes(repo: Path, commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def git_blob_oid(raw: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(raw)}\0".encode("ascii") + raw
    ).hexdigest()


def identity_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    return (
        raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if path.suffix.lower() in TEXT_SUFFIXES else raw
    )


def source_identity(repo: Path, relative: Path, role: str) -> dict[str, Any]:
    path = repo / relative
    raw = path.read_bytes()
    identity = identity_bytes(path)
    return {
        "path": relative.as_posix(),
        "role": role,
        "working_tree_bytes": len(raw),
        "identity_bytes": len(identity),
        "sha256": hashlib.sha256(identity).hexdigest(),
        "git_blob_oid": git_blob_oid(identity),
        "newline_identity": "canonical_LF",
    }


def binary_identity(repo: Path, relative: Path, role: str) -> dict[str, Any]:
    path = repo / relative
    return {
        "path": relative.as_posix(),
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def artifact_identity(path: Path, output: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    identity = identity_bytes(path)
    return {
        "path": (V4_PACKAGE / path.relative_to(output)).as_posix(),
        "working_tree_bytes": len(raw),
        "identity_bytes": len(identity),
        "sha256": hashlib.sha256(identity).hexdigest(),
        "git_blob_oid": git_blob_oid(identity),
    }


def assert_score_free(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            current = f"{path}.{key}"
            if str(key) in NULL_FIELDS and child is not None:
                raise BuildError(f"populated score field at {current}")
            assert_score_free(child, current)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_score_free(child, f"{path}[{index}]")


def _consumed_v3_failure(repo: Path) -> dict[str, Any]:
    if git(repo, "cat-file", "-t", V3_FAILURE_COMMIT) != "commit":
        raise BuildError("V3 failure identity is not a commit")
    parent = git(repo, "rev-parse", f"{V3_FAILURE_COMMIT}^")
    if parent != V3_PACKAGE_COMMIT:
        raise BuildError("V3 failure parent changed")
    rows = []
    parsed: dict[str, Any] = {}
    raw_files: dict[str, str] = {}
    for name, expected in V3_FAILURE_HASHES.items():
        relative = f"{V3_FAILURE_DIRECTORY}/{name}"
        raw = git_show_bytes(repo, V3_FAILURE_COMMIT, relative)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected:
            raise BuildError(f"V3 failure artifact changed: {name}")
        rows.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": digest,
            "git_blob_oid": git(
                repo, "rev-parse", f"{V3_FAILURE_COMMIT}:{relative}"
            ),
        })
        raw_files[name] = raw.decode("utf-8")
        if name.endswith(".json"):
            parsed[name] = json.loads(raw)
    failure = parsed["EXECUTION_FAILURE.json"]
    start = parsed["EXECUTION_START_RECEIPT.json"]
    progress = raw_files["PROGRESS.log"]
    stack = raw_files["STDERR.log"]
    required_stack = (
        'window1_t2_scoring_runner_v3.py", line 713, in execute',
        'window1_t2_frontier_regret_scorer_v1.py", line 138, '
        "in score_t2_event",
        'window1_range_attack_scorer_v1.py", line 122, in score_event',
        'ReferenceError("positive boundary lacks V5 guard artifact")',
    )
    if (
        failure.get("exit_code") != 1
        or failure.get("error")
        != "ReferenceError: positive boundary lacks V5 guard artifact"
        or start.get("authorization_commit") != V3_AUTHORIZATION
        or start.get("execution_id") != V3_EXECUTION_ID
        or start.get("retry_count") != 0
        or progress.count("execution_id=") != 1
        or progress.count("candidate_start=") != 1
        or not all(text in stack for text in required_stack)
    ):
        raise BuildError("V3 failure semantics/stack changed")
    tree_paths = git(
        repo, "diff-tree", "--no-commit-id", "--name-only", "-r",
        V3_FAILURE_COMMIT,
    ).splitlines()
    if (
        len(tree_paths) != 5
        or any(
            not path.startswith(V3_FAILURE_DIRECTORY + "/")
            for path in tree_paths
        )
    ):
        raise BuildError("V3 failure commit contains non-results paths")
    return {
        "schema_version": VERSION + "-consumed-V3-failure-binding-v1",
        "V3_package_commit": V3_PACKAGE_COMMIT,
        "consumed_V3_authorization": V3_AUTHORIZATION,
        "V3_failure_commit": V3_FAILURE_COMMIT,
        "V3_failure_parent": parent,
        "execution_id": V3_EXECUTION_ID,
        "runner_invocation_count": 1,
        "retry_count": 0,
        "exit_code": 1,
        "V3_preserved_receipt_scorer_invocations": (
            start.get("scorer_invocations")
        ),
        "reconstructed_scorer_call_attempts": 1,
        "completed_event_rows": 0,
        "completed_candidates": 0,
        "performance_result_produced": False,
        "completed_result_row_files": 0,
        "error": failure["error"],
        "exact_stack_trace": stack,
        "files": rows,
        "failure_receipt_sha256": V3_FAILURE_HASHES[
            "EXECUTION_FAILURE.json"
        ],
        "output_manifest_sha256": V3_FAILURE_HASHES[
            "OUTPUT_HASH_MANIFEST.json"
        ],
        "preserved_failure_amended": False,
        "authorization_consumed": True,
        "authorization_reusable": False,
        "holdout_opened": False,
        "live_network_or_trading_access": False,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "performance": None,
    }


def _correction_receipt(seam: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": VERSION + "-transitive-boundary-correction-v1",
        "defect": {
            "runner": (
                "window1_t2_scoring_runner_v3.py:713 supplied "
                "normalized starts[event_id]"
            ),
            "transitive_consumer": (
                "window1_range_attack_scorer_v1.py:122 guarded_cutoff"
            ),
            "preserved_error": (
                "ReferenceError: positive boundary lacks V5 guard artifact"
            ),
        },
        "V3_AST_subset_proof_was_insufficient": True,
        "why_AST_subset_was_insufficient": (
            "V3 compared top-level role loads and validated frozen reference "
            "derivation, but did not validate the transitive boundary type "
            "consumed by guarded_cutoff inside the inherited metric scorer."
        ),
        "V3_reached_scorer_call_entry": True,
        "V3_passed_scorer_boundary": False,
        "V3_scorer_call_attempts": 1,
        "V3_completed_event_rows": 0,
        "V3_completed_candidates": 0,
        "V4_shared_preparation_function": "iter_prepared_scorer_calls",
        "V4_scorer_boundary_role": "full_raw_V5_boundary",
        "V4_normalized_boundary_role": "cross_check_only",
        "prepared_call_count": seam["prepared_scorer_calls"],
        "raw_V5_prepared_count": seam["full_raw_V5_boundary_count"],
        "normalized_selected_count": (
            seam["normalized_boundary_selected_count"]
        ),
        "future_attempt_accounting": {
            "increment": "immediately_before_score_t2_event",
            "persist": "before_entering_score_t2_event",
            "event_completion": "only_after_successful_return",
            "candidate_completion": "only_after_804_successful_rows",
        },
        "scorer_call_attempts": 0,
        "completed_event_rows": 0,
        "completed_candidates": 0,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "performance": None,
    }


def _expected_schema() -> dict[str, Any]:
    return {
        "schema_version": "window1-t2-scoring-output-schema-v4",
        "execution_id": EXECUTION_ID,
        "candidate_count": 8,
        "D_per_candidate": 804,
        "scorer_boundary_role": "full_raw_V5_boundary",
        "accounting_fields": [
            "scorer_call_attempts",
            "completed_event_rows",
            "completed_candidates",
            "active_candidate_id",
            "active_event_id",
        ],
        "performance_outputs": {
            "C": None, "PC": None, "IC": None, "S": None,
            "frontier": None, "regret": None, "attribution": None,
            "performance": None, "ranking": None, "selection": None,
        },
    }


def _audit_instruction() -> str:
    return """# Independent Window-1 T2 scoring-package V4 audit

Do not run or authorize the scorer. Blindly verify before opening expected
receipts:

1. Recompute the V3 failure commit, its parent, all five artifact hashes, exact
   stack, one runner invocation, one scorer-call attempt, zero completed event
   rows, and zero completed candidates.
2. Independently load all raw V5 and normalized boundary rows. For every event,
   compare `boundary_contract(raw)` to normalized and compare
   `guarded_cutoff(raw)` to the operative normalized status/cutoff/guard.
3. Iterate `iter_prepared_scorer_calls` for all 6,432 candidate-event calls.
   Freeze hashes/counts before opening V4 summaries. Prove each exact
   `score_kwargs["boundary"]` is the full raw V5 row, never normalized.
4. Independently inject a scorer exception and prove attempt count persistence
   precedes entry while completed row/candidate counts remain zero.
5. Compare only after freezing independent receipts. Any mismatch is BLOCK;
   no post-hoc reconciliation is permitted.
6. Verify additions-only lineage, consumed V2/V3 authorization rejection,
   null metrics, results-directory absence, holdout/non-live fences, complete
   tests, and two-build determinism.

A PASS certifies a score-free PRE-RUN only. V4 execution requires a new,
separately bound one-use authorization.
"""


def _report(
    failure: Mapping[str, Any],
    seam: Mapping[str, Any],
    bundle: str,
) -> str:
    return f"""# Window-1 T2 scoring-package V4 PRE-RUN

Status: **SCORE-FREE / NOT AUTHORIZED / NOT EXECUTED**

V4 preserves V1/V2/V3 byte-for-byte and binds the consumed V3 failure at
`{failure['V3_failure_commit']}`. V3 made one scorer-call attempt and completed
zero event rows and zero candidates; its preserved receipt is not amended.

The shared V4 runtime preparation generated {seam['prepared_scorer_calls']}
exact candidate-event call objects. All use full raw V5 boundary rows;
normalized scorer-boundary selections are zero. `guarded_cutoff` succeeded for
all prepared calls, including the first V2/V3 failure event.

Input-bundle SHA-256: `{bundle}`.

No scorer was imported by the package builder or invoked by the seam probe.
No V4 results directory or authorization exists. C/PC/IC/S, frontier, regret,
attribution, ranking, selection, and performance remain null. July 24-26
remained sealed and no live/network/trading surface was accessed.
"""


def _verify_private_cache(
    repo: Path,
    cache_root: Path,
    hash_set_path: Path,
) -> dict[str, Any]:
    hashes = read_json(repo / hash_set_path)
    rows = hashes["event_files"]
    if len(rows) != 804:
        raise BuildError("guarded-cache hash set is not D=804")
    total = 0
    for row in rows:
        path = cache_root / str(row["file"])
        if (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256_file(path) != row["sha256"]
        ):
            raise BuildError(f"guarded-cache mismatch: {row['file']}")
        total += path.stat().st_size
    return {
        "event_files": 804,
        "bytes": total,
        "hash_set_sha256": sha256_file(repo / hash_set_path),
        "all_files_verified": True,
    }


def build(*, repo: Path, output: Path) -> dict[str, Any]:
    repo = repo.resolve()
    if output.exists():
        raise BuildError("V4 output already exists")
    if git(repo, "rev-parse", "HEAD") != IMPLEMENTATION_PARENT:
        raise BuildError("V4 HEAD differs from exact parent")
    if (repo / RESULTS_DIRECTORY).exists():
        raise BuildError("V4 results directory exists")
    output.mkdir(parents=True)
    v3 = read_json(repo / V3_PACKAGE / "SCORING_INPUT_MANIFEST.json")
    if (
        v3.get("schema_version")
        != "window1-t2-scoring-input-manifest-v3"
        or v3.get("input_bundle_sha256")
        != "92c8992bfe72529ed9b1229d1e67fd762aee6ba67463020f88e3ac44b4952996"
    ):
        raise BuildError("V3 package binding changed")
    cache_root = (
        repo / Path(v3["roles"]["guarded_cache_directory"])
    ).resolve()
    cache_verification = _verify_private_cache(
        repo,
        cache_root,
        Path(v3["roles"]["guarded_cache_hash_set"]),
    )
    seam = no_score_seam_probe(
        repo=repo,
        roles=v3["roles"],
        candidate_ids=CANDIDATES,
        candidate_to_parent=CANDIDATE_TO_PARENT,
        results_directory=RESULTS_DIRECTORY,
    )
    failure = _consumed_v3_failure(repo)
    correction = _correction_receipt(seam)
    readiness = {
        **seam,
        "schema_version": VERSION + "-execution-readiness-no-score-v1",
        "real_development_population_loaded": True,
        "shared_with_future_execute": True,
        "exact_score_kwargs_iterated": True,
        "scorer_boundary_reached": False,
        "scorer_call_seam_reached": True,
        "scorer_call_attempts": 0,
        "completed_event_rows": 0,
        "completed_candidates": 0,
        "results_directory_absent": True,
        "holdout_opened": False,
        "live_or_production_access": False,
        "network_or_trading_access": False,
    }
    write_json(output / "CONSUMED_V3_FAILURE_BINDING.json", failure)
    write_json(
        output / "TRANSITIVE_BOUNDARY_CORRECTION_RECEIPT.json", correction
    )
    write_json(output / "RUNTIME_SEAM_PROBE_RECEIPT.json", seam)
    write_json(
        output / "EXECUTION_READINESS_NO_SCORE_RECEIPT.json", readiness
    )
    write_json(output / "EXPECTED_OUTPUT_SCHEMA_V4.json", _expected_schema())
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden-access-v1",
        "scorer_imported_by_builder": False,
        "scorer_call_attempts": 0,
        "results_directory_created": False,
        "authorization_issued": False,
        "holdout_opened": False,
        "live_network_Kalshi_or_trading_access": False,
        "order_position_exit_settlement_DCA_Window2_access": False,
        "tuning_ranking_selection_deployment": False,
        "C": None, "PC": None, "IC": None, "S": None,
        "frontier": None, "regret": None, "attribution": None,
        "performance": None, "ranking": None, "selection": None,
    })
    write_json(output / "V1_V2_V3_BYTE_IDENTITY_RECEIPT.json", {
        "schema_version": VERSION + "-inherited-byte-identity-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "V3_package_path": V3_PACKAGE.as_posix(),
        "inherited_files_modified": 0,
        "inherited_files_deleted": 0,
        "V3_failure_branch_merged": False,
        "V4_additions_only": True,
    })
    (output / "INDEPENDENT_AUDIT_INSTRUCTION.md").write_text(
        _audit_instruction(), encoding="utf-8", newline="\n"
    )

    source_paths = [
        (RUNTIME, "shared_V4_runtime_preparation"),
        (RUNNER, "V4_stdout_safe_runner"),
        (BUILDER, "V4_package_builder"),
        (FREEZER, "V4_two_clean_build_freezer"),
        (TEST, "V4_tests"),
        (CONTRACT, "V4_transitive_boundary_contract"),
        (
            Path(
                "arb-executor/analysis/"
                "window1_range_attack_reference_adapter_v1.py"
            ),
            "raw_V5_guarded_cutoff",
        ),
        (
            Path(
                "arb-executor/analysis/"
                "window1_t2_frontier_regret_scorer_v1.py"
            ),
            "inherited_T2_scorer",
        ),
        (
            Path(
                "arb-executor/analysis/"
                "window1_range_attack_scorer_v1.py"
            ),
            "transitive_boundary_consumer",
        ),
    ]
    v3_source = read_json(repo / V3_PACKAGE / "SOURCE_HASH_MANIFEST.json")
    inherited_binary_roles = dict(v3["roles"])
    inherited_binary_roles.pop("guarded_cache_directory", None)
    binary_rows = [
        binary_identity(repo, Path(relative), f"inherited_{role}")
        for role, relative in sorted(inherited_binary_roles.items())
    ]
    source_manifest = {
        "schema_version": VERSION + "-source-hash-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "T2_prerun": T2_PRERUN,
        "T2_independent_PASS": T2_PASS,
        "V3_package_commit": V3_PACKAGE_COMMIT,
        "V3_failure_commit": V3_FAILURE_COMMIT,
        "committed_source_inputs": [
            source_identity(repo, path, role)
            for path, role in source_paths
        ],
        "frozen_binary_inputs": binary_rows,
        "private_runtime_inputs": v3_source["private_runtime_inputs"],
        "private_cache_verification": cache_verification,
        "holdout_opened": False,
        "live_or_production_access": False,
        "scorer_call_attempts": 0,
    }
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)

    roles = dict(v3["roles"])
    roles.update({
        "consumed_v3_failure_binding": (
            V4_PACKAGE / "CONSUMED_V3_FAILURE_BINDING.json"
        ).as_posix(),
        "transitive_boundary_correction_receipt": (
            V4_PACKAGE / "TRANSITIVE_BOUNDARY_CORRECTION_RECEIPT.json"
        ).as_posix(),
        "runtime_seam_probe_receipt": (
            V4_PACKAGE / "RUNTIME_SEAM_PROBE_RECEIPT.json"
        ).as_posix(),
        "execution_readiness_no_score_receipt": (
            V4_PACKAGE / "EXECUTION_READINESS_NO_SCORE_RECEIPT.json"
        ).as_posix(),
        "expected_output_schema": (
            V4_PACKAGE / "EXPECTED_OUTPUT_SCHEMA_V4.json"
        ).as_posix(),
        "source_hash_manifest": (
            V4_PACKAGE / "SOURCE_HASH_MANIFEST.json"
        ).as_posix(),
        "transitive_boundary_contract_v4": CONTRACT.as_posix(),
    })
    critical = {}
    for role, relative in sorted(roles.items()):
        if role == "guarded_cache_directory":
            continue
        path = repo / Path(relative)
        if str(relative).startswith(V4_PACKAGE.as_posix()):
            path = output / Path(relative).relative_to(V4_PACKAGE)
        raw = identity_bytes(path)
        critical[role] = {
            "path": str(relative),
            "identity_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    payload = {
        "schema_version": "window1-t2-scoring-input-bundle-v4",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "T2_prerun": T2_PRERUN,
        "T2_PASS": T2_PASS,
        "controlling_T2_PASS": T2_PASS,
        "audited_scorer_commit": (
            "e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd"
        ),
        "V3_package_commit": V3_PACKAGE_COMMIT,
        "consumed_V3_failure_commit": V3_FAILURE_COMMIT,
        "consumed_authorizations_rejected": [
            V2_AUTHORIZATION, V3_AUTHORIZATION,
        ],
        "consumed_execution_ids_rejected": [
            V2_EXECUTION_ID, V3_EXECUTION_ID,
        ],
        "execution_id": EXECUTION_ID,
        "D": 804,
        "fit_D": 525,
        "post_fit_D": 279,
        "candidate_ids": list(CANDIDATES),
        "roles": roles,
        "critical_role_identities": critical,
        "command_template_literal": COMMAND_TEMPLATE,
    }
    bundle = canonical_sha256(payload)
    manifest = {
        **payload,
        "schema_version": "window1-t2-scoring-input-manifest-v4",
        "input_bundle_payload": payload,
        "input_bundle_sha256": bundle,
        "future_independent_PASS_required": True,
        "future_authorization_required": True,
        "scored": False,
        "C": None, "PC": None, "IC": None, "S": None,
        "frontier": None, "regret": None, "attribution": None,
        "performance": None, "ranking": None, "selection": None,
    }
    write_json(output / "SCORING_INPUT_MANIFEST.json", manifest)
    write_json(output / "NULL_METRIC_NO_EXECUTION_RECEIPT.json", {
        "schema_version": VERSION + "-null-no-execution-v1",
        "execution_id": EXECUTION_ID,
        "input_bundle_sha256": bundle,
        "all_committed_result_performance_fields_null": True,
        "scorer_call_attempts": 0,
        "completed_event_rows": 0,
        "completed_candidates": 0,
        "results_directory": RESULTS_DIRECTORY,
        "results_directory_exists": False,
        "authorization_exists": False,
        "future_independent_PASS_required": True,
        "C": None, "PC": None, "IC": None, "S": None,
        "frontier": None, "regret": None, "attribution": None,
        "performance": None, "ranking": None, "selection": None,
    })
    (output / "PRE_RUN_REPORT.md").write_text(
        _report(failure, seam, bundle), encoding="utf-8", newline="\n"
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
        raise BuildError("V4 results directory appeared during build")
    return {
        "schema_version": VERSION + "-build-receipt-v1",
        "input_bundle_sha256": bundle,
        "prepared_scorer_calls": seam["prepared_scorer_calls"],
        "raw_V5_boundary_calls": seam["full_raw_V5_boundary_count"],
        "normalized_boundary_calls": seam[
            "normalized_boundary_selected_count"
        ],
        "scorer_call_attempts": 0,
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
