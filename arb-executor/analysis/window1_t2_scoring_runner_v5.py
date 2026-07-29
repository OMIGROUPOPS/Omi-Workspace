#!/usr/bin/env python3
"""Test-honest identity wrapper for the frozen T2 scoring runner V4.

The scoring, shared runtime preparation, adapters, and output construction are
the exact V4 implementations.  V5 changes package/execution identities and
authorization binding only; it does not change a scoring semantic.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

import window1_t2_scoring_runner_v4 as _v4


VERSION = "window1-t2-scoring-runner-v5"
IMPLEMENTATION_PARENT = "9cc8f1cc7b0693e00ce0f537532d41aab0a5ef7c"
PACKAGE_DIRECTORY = (
    ".claude/window1_t2_scoring_package_v5_prerun_20260729"
)
PACKAGE_PATH = f"{PACKAGE_DIRECTORY}/SCORING_INPUT_MANIFEST.json"
EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v5"
)
RESULTS_DIRECTORY = f".claude/window1_t2_results_{EXECUTION_ID}"
RETIRED_V4_EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v4"
)
COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/window1_t2_scoring_runner_v5.py "
    f"--repo . --package {PACKAGE_PATH} --mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
REMOTE_PACKAGE_REF = (
    "refs/remotes/origin/"
    "codex/window1-t2-scoring-package-v5-prerun"
)

RunnerError = _v4.RunnerError
CANDIDATE_IDS = _v4.CANDIDATE_IDS
CANDIDATE_TO_PARENT = _v4.CANDIDATE_TO_PARENT
CONSUMED_V2_AUTHORIZATION = _v4.CONSUMED_V2_AUTHORIZATION
CONSUMED_V3_AUTHORIZATION = _v4.CONSUMED_V3_AUTHORIZATION
CONSUMED_V2_EXECUTION_ID = _v4.CONSUMED_V2_EXECUTION_ID
CONSUMED_V3_EXECUTION_ID = _v4.CONSUMED_V3_EXECUTION_ID


_ORIGINAL_READ_JSON = _v4.read_json
_ORIGINAL_VALIDATE_PACKAGE = _v4.validate_package
_ORIGINAL_EXECUTE = _v4.execute
_ORIGINAL_VALIDATION_ONLY = _v4.validation_only
_ORIGINAL_READINESS = _v4.execution_readiness_no_score
_ORIGINAL_MAIN = _v4.main


def _install_v5_identity() -> None:
    """Bind the unchanged V4 implementation to the frozen V5 identities."""
    _v4.VERSION = VERSION
    _v4.IMPLEMENTATION_PARENT = IMPLEMENTATION_PARENT
    _v4.PACKAGE_DIRECTORY = PACKAGE_DIRECTORY
    _v4.PACKAGE_PATH = PACKAGE_PATH
    _v4.EXECUTION_ID = EXECUTION_ID
    _v4.RESULTS_DIRECTORY = RESULTS_DIRECTORY
    _v4.COMMAND_TEMPLATE = COMMAND_TEMPLATE


def validate_package(
    repo: Path,
    package_path: Path,
    *,
    verify_private_inputs: bool,
) -> dict[str, Any]:
    """Run the V4 validator with only the versioned manifest tag adapted."""
    _install_v5_identity()
    package = _ORIGINAL_READ_JSON(package_path)
    if (
        package.get("schema_version")
        != "window1-t2-scoring-input-manifest-v5"
        or package.get("package_revision")
        != "V5_TEST_HONESTY_CORRECTION"
        or package.get("V4_runtime_semantics_changed") is not False
        or package.get("retired_execution_id") != RETIRED_V4_EXECUTION_ID
    ):
        raise RunnerError("frozen T2 V5 package identity changed")

    def compatible_read_json(path: Path) -> Any:
        value = _ORIGINAL_READ_JSON(path)
        if path.resolve() == package_path.resolve():
            value = copy.deepcopy(value)
            value["schema_version"] = (
                "window1-t2-scoring-input-manifest-v4"
            )
        return value

    _v4.read_json = compatible_read_json
    try:
        validated = _ORIGINAL_VALIDATE_PACKAGE(
            repo,
            package_path,
            verify_private_inputs=verify_private_inputs,
        )
    finally:
        _v4.read_json = _ORIGINAL_READ_JSON
    validated["package"] = package
    return validated


def authorize_execute(
    repo: Path,
    validated: Mapping[str, Any],
    audit_commit: str,
    audit_report_path: str,
) -> str:
    """Require a new V5 audit/authorization and exact V5 package branch."""
    _install_v5_identity()
    if audit_commit in {
        CONSUMED_V2_AUTHORIZATION,
        CONSUMED_V3_AUTHORIZATION,
    }:
        raise RunnerError(
            "consumed V2/V3 authorization is rejected by V5"
        )
    package = validated["package"]
    head = str(validated["head"])
    _v4.load_and_verify_authorization_report(
        repo,
        audit_commit=audit_commit,
        audit_report_path=audit_report_path,
        audit_ref="refs/remotes/origin/audit/window1-independent",
        package_commit=head,
        execution_id=EXECUTION_ID,
        bundle_sha256=str(package["input_bundle_sha256"]),
        command_template=COMMAND_TEMPLATE,
    )
    if _v4.git(repo, "rev-parse", "HEAD^") != IMPLEMENTATION_PARENT:
        raise RunnerError("package is not sole child of frozen V4 parent")
    if _v4.git(repo, "rev-parse", "HEAD") != _v4.git(
        repo, "rev-parse", REMOTE_PACKAGE_REF
    ):
        raise RunnerError("local/remote V5 package equality failed")
    if _v4.git(repo, "status", "--porcelain"):
        raise RunnerError("execution worktree is not clean")
    return (
        "python -B arb-executor/analysis/window1_t2_scoring_runner_v5.py "
        f"--repo . --package {PACKAGE_PATH} --mode execute "
        f"--authorization-commit {audit_commit} "
        f"--authorization-report {audit_report_path}"
    )


_install_v5_identity()
_v4.validate_package = validate_package
_v4.authorize_execute = authorize_execute


def validation_only(repo: Path, package_path: Path) -> dict[str, Any]:
    _install_v5_identity()
    return _ORIGINAL_VALIDATION_ONLY(repo, package_path)


def execution_readiness_no_score(
    repo: Path,
    package_path: Path,
) -> dict[str, Any]:
    _install_v5_identity()
    return _ORIGINAL_READINESS(repo, package_path)


def execute(
    repo: Path,
    package_path: Path,
    authorization_commit: str,
    authorization_report: str,
) -> int:
    _install_v5_identity()
    return _ORIGINAL_EXECUTE(
        repo,
        package_path,
        authorization_commit,
        authorization_report,
    )


def main() -> int:
    _install_v5_identity()
    return _ORIGINAL_MAIN()


if __name__ == "__main__":
    raise SystemExit(main())
