#!/usr/bin/env python3
"""Stdout-safe deterministic runner for Range-Attack scoring package V2.

The real execution remains gated and is not invoked by package construction.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import platform
import sys
import traceback
from pathlib import Path
from typing import Any, Mapping

from window1_range_attack_guarded_fill_adapter_v2 import (
    GuardedFillError,
    adapt_unique_fill_rows,
)
from window1_range_attack_reference_adapter_v1 import ReferenceError
from window1_range_attack_reference_adapter_v2 import (
    derive_window1_close_reference,
)
from window1_range_attack_scorer_v1 import RangeAttackScoringError
from window1_range_attack_scorer_v2 import (
    aggregate_candidate,
    score_event,
)
from window1_range_attack_scoring_runner_v1 import (
    ConsoleEchoGuard,
    ProgressEmitter,
    RunnerError,
    _event_legs,
    _load_cache,
    canonical_sha256,
    git,
    read_json,
    read_jsonl,
    resolve_role,
    sha256_file,
    write_json,
    write_jsonl,
)


VERSION = "window1-range-attack-scoring-runner-v2"
IMPLEMENTATION_PARENT = "f774d9060acc70efd4a80d48bfa7d4c6b1b9daf1"
CONTROLLING_AUDIT = "3811a772aea381767a763af90320a1af91475816"
STRICT_ASK_INSTRUMENT = "d413f23125d5931a56077c70f475d8815ffe36c0"
PACKAGE_PATH = (
    ".claude/window1_range_attack_scoring_package_v2_prerun_20260726/"
    "SCORING_INPUT_MANIFEST.json"
)
PACKAGE_DIRECTORY = (
    ".claude/window1_range_attack_scoring_package_v2_prerun_20260726"
)
EXECUTION_ID = (
    "w1-range-attack-v2-dev-20260712-20260720-grid2-scorepkg-v2"
)
RESULTS_DIRECTORY = f".claude/window1_range_attack_results_{EXECUTION_ID}"
CANDIDATE_IDS = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
D_REQUIRED = 804
COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/"
    "window1_range_attack_scoring_runner_v2.py --repo . --package "
    f"{PACKAGE_PATH} --mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
TEXT_SUFFIXES = {
    ".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml",
}


def canonical_text_bytes(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def git_blob_oid(raw: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(raw)}\0".encode("ascii") + raw
    ).hexdigest()


def _identity_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return canonical_text_bytes(raw)
    return raw


def _validate_source_rows(repo: Path, rows: list[Mapping[str, Any]]) -> None:
    seen: set[str] = set()
    for row in rows:
        relative = str(row.get("path") or "")
        if relative in seen:
            raise RunnerError("duplicate source/hash manifest path")
        seen.add(relative)
        path = resolve_role(repo, relative)
        if not path.is_file():
            raise RunnerError(f"missing bound input: {relative}")
        identity = _identity_bytes(path)
        if len(identity) != int(row.get("identity_bytes") or -1):
            raise RunnerError(f"canonical byte length mismatch: {relative}")
        if hashlib.sha256(identity).hexdigest() != row.get("sha256"):
            raise RunnerError(f"SHA-256 mismatch: {relative}")
        if git_blob_oid(identity) != row.get("git_blob_oid"):
            raise RunnerError(f"Git blob mismatch: {relative}")


def _validate_private_sources(
    repo: Path,
    package: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
) -> None:
    rows = source_manifest.get("private_runtime_inputs")
    if not isinstance(rows, list):
        raise RunnerError("private runtime input receipts missing")
    for row in rows:
        role = str(row.get("role") or "")
        path = resolve_role(repo, str(row.get("path") or ""))
        if role == "guarded_cache_v3_directory":
            hash_set = read_json(resolve_role(
                repo, str(package["roles"]["guarded_cache_hash_set"])
            ))
            if len(hash_set["event_files"]) != D_REQUIRED:
                raise RunnerError("guarded-cache hash set is not 804 files")
            for item in hash_set["event_files"]:
                child = path / str(item["file"])
                if (
                    not child.is_file()
                    or child.stat().st_size != int(item["bytes"])
                    or sha256_file(child) != item["sha256"]
                ):
                    raise RunnerError(
                        f"guarded-cache receipt mismatch: {item['file']}"
                    )
        elif (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256_file(path) != row["sha256"]
        ):
            raise RunnerError(f"private input mismatch: {role}")


def _validate_package_artifacts(repo: Path) -> None:
    manifest_path = resolve_role(
        repo, f"{PACKAGE_DIRECTORY}/PACKAGE_ARTIFACT_MANIFEST.json"
    )
    manifest = read_json(manifest_path)
    for row in manifest.get("artifacts") or []:
        path = resolve_role(repo, str(row["path"]))
        identity = _identity_bytes(path) if path.is_file() else b""
        if (
            not path.is_file()
            or len(identity) != int(row["identity_bytes"])
            or hashlib.sha256(identity).hexdigest() != row["sha256"]
            or git_blob_oid(identity) != row["git_blob_oid"]
        ):
            raise RunnerError(f"package artifact mismatch: {row['path']}")


def validate_package(
    repo: Path,
    package_path: Path,
    *,
    verify_private_inputs: bool,
) -> dict[str, Any]:
    if package_path.resolve() != resolve_role(repo, PACKAGE_PATH):
        raise RunnerError("package path differs from frozen path")
    package = read_json(package_path)
    if (
        package.get("schema_version")
        != "window1-range-attack-scoring-input-manifest-v2"
        or package.get("implementation_parent") != IMPLEMENTATION_PARENT
        or package.get("controlling_audit") != CONTROLLING_AUDIT
        or package.get("strict_ask_instrument") != STRICT_ASK_INSTRUMENT
        or package.get("execution_id") != EXECUTION_ID
        or tuple(package.get("candidate_ids") or ()) != CANDIDATE_IDS
        or package.get("D") != D_REQUIRED
        or package.get("metrics") is not None
        or package.get("performance") is not None
        or package.get("scored") is not False
    ):
        raise RunnerError("frozen package identity or null-metric law changed")
    payload = package.get("input_bundle_payload")
    if (
        not isinstance(payload, Mapping)
        or canonical_sha256(payload) != package.get("input_bundle_sha256")
    ):
        raise RunnerError("input-bundle hash mismatch")
    if set(package["roles"]) & {
        "guarded_fillability_receipts",
        "candidate_order_streams",
        "raw_causal_fill_state",
    }:
        raise RunnerError("raw construction source leaked into runtime roles")
    source_manifest = read_json(resolve_role(
        repo, str(package["roles"]["source_hash_manifest"])
    ))
    _validate_source_rows(repo, source_manifest["committed_inputs"])
    _validate_package_artifacts(repo)
    unique = source_manifest["unique_runtime_fill_ledger"]
    unique_path = resolve_role(
        repo, str(package["roles"]["unique_guarded_fill_ledger"])
    )
    if (
        not unique_path.is_file()
        or unique_path.stat().st_size != int(unique["bytes"])
        or sha256_file(unique_path) != unique["sha256"]
    ):
        raise RunnerError("unique guarded-fill ledger hash mismatch")
    if verify_private_inputs:
        _validate_private_sources(repo, package, source_manifest)
    if package.get("future_independent_pass_required") is not True:
        raise RunnerError("future independent PASS gate is not frozen")
    if resolve_role(repo, RESULTS_DIRECTORY).exists():
        raise RunnerError("execution ID/results directory already exists")
    return {
        "package": package,
        "source_manifest": source_manifest,
        "head": git(repo, "rev-parse", "HEAD"),
    }


def _full_sha(value: str, field: str) -> str:
    result = str(value or "").lower()
    if len(result) != 40 or any(
        char not in "0123456789abcdef" for char in result
    ):
        raise RunnerError(f"{field} must be a full 40-character SHA")
    return result


def verify_authorization_report_text(
    report: str,
    *,
    package_commit: str,
    execution_id: str,
    bundle_sha256: str,
    command_template: str,
) -> None:
    """Verify finite report bindings without an audit-SHA self-reference."""
    required = (
        "PASS",
        package_commit,
        execution_id,
        bundle_sha256,
        command_template,
    )
    if any(value not in report for value in required):
        raise RunnerError(
            "independent report does not authorize exact package, "
            "execution ID, bundle, and frozen command template"
        )


def load_and_verify_authorization_report(
    repo: Path,
    *,
    audit_commit: str,
    audit_report_path: str,
    audit_ref: str,
    package_commit: str,
    execution_id: str,
    bundle_sha256: str,
    command_template: str,
) -> str:
    """Read the report blob from the separately supplied exact commit."""
    audit_commit = _full_sha(audit_commit, "future audit SHA")
    git(repo, "cat-file", "-e", f"{audit_commit}^{{commit}}")
    if git(
        repo, "merge-base", "--is-ancestor", audit_commit, audit_ref
    ) != "":
        raise RunnerError("unexpected merge-base output")
    report = git(repo, "show", f"{audit_commit}:{audit_report_path}")
    verify_authorization_report_text(
        report,
        package_commit=package_commit,
        execution_id=execution_id,
        bundle_sha256=bundle_sha256,
        command_template=command_template,
    )
    return report


def authorize_execute(
    repo: Path,
    validated: Mapping[str, Any],
    audit_commit: str,
    audit_report_path: str,
) -> str:
    audit_commit = _full_sha(audit_commit, "future audit SHA")
    remote_audit = "refs/remotes/origin/audit/window1-independent"
    package = validated["package"]
    head = _full_sha(validated["head"], "package commit")
    load_and_verify_authorization_report(
        repo,
        audit_commit=audit_commit,
        audit_report_path=audit_report_path,
        audit_ref=remote_audit,
        package_commit=head,
        execution_id=EXECUTION_ID,
        bundle_sha256=str(package["input_bundle_sha256"]),
        command_template=COMMAND_TEMPLATE,
    )
    if git(repo, "rev-parse", "HEAD^") != IMPLEMENTATION_PARENT:
        raise RunnerError("execution package is not the sole parent child")
    if git(repo, "status", "--porcelain"):
        raise RunnerError("execution worktree is not clean")
    return (
        "python -B arb-executor/analysis/"
        "window1_range_attack_scoring_runner_v2.py --repo . --package "
        f"{PACKAGE_PATH} --mode execute "
        f"--authorization-commit {audit_commit} "
        f"--authorization-report {audit_report_path}"
    )


def validation_only(repo: Path, package_path: Path) -> dict[str, Any]:
    validated = validate_package(
        repo, package_path, verify_private_inputs=False
    )
    package = validated["package"]
    return {
        "schema_version": VERSION + "-validation-only-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_audit": CONTROLLING_AUDIT,
        "candidate_ids": list(CANDIDATE_IDS),
        "D": D_REQUIRED,
        "unique_fill_rows": 991,
        "input_bundle_sha256": package["input_bundle_sha256"],
        "future_independent_pass_required": True,
        "real_population_loaded": False,
        "unique_fill_adapter_invoked": False,
        "reference_adapter_invoked": False,
        "scorer_invoked": False,
        "performance_metrics": {
            "C": None, "PC": None, "S": None, "IC": None
        },
        "gate_pass": True,
    }


def _output_hashes(result_dir: Path) -> dict[str, Any]:
    return {
        "schema_version": VERSION + "-output-hashes-v1",
        "execution_id": EXECUTION_ID,
        "outputs": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in sorted(result_dir.iterdir())
            if path.is_file() and path.name != "OUTPUT_HASH_MANIFEST.json"
        },
    }


def execute(
    repo: Path,
    package_path: Path,
    audit_commit: str,
    audit_report_path: str,
) -> int:
    """Execute only after a future independent authorization."""
    validated = validate_package(
        repo, package_path, verify_private_inputs=True
    )
    exact_command = authorize_execute(
        repo, validated, audit_commit, audit_report_path
    )
    package = validated["package"]
    roles = package["roles"]
    result_dir = resolve_role(repo, RESULTS_DIRECTORY)
    result_dir.mkdir(parents=True, exist_ok=False)
    started = dt.datetime.now(dt.timezone.utc)
    console = ConsoleEchoGuard()
    progress = ProgressEmitter(result_dir / "PROGRESS.log", console)
    start_receipt = {
        "schema_version": VERSION + "-execution-start-v1",
        "execution_id": EXECUTION_ID,
        "exact_command": exact_command,
        "package_commit": validated["head"],
        "authorization_commit": audit_commit,
        "authorization_report": audit_report_path,
        "input_bundle_sha256": package["input_bundle_sha256"],
        "started_at_utc": started.isoformat(),
        "runtime": {"python": sys.version, "platform": platform.platform()},
        "scorer_invocations": 0,
        "retry_count": 0,
        "holdout_opened": False,
        "live_or_production_access": False,
    }
    write_json(result_dir / "EXECUTION_START_RECEIPT.json", start_receipt)
    try:
        progress.emit(f"execution_id={EXECUTION_ID}")
        events = read_jsonl(resolve_role(repo, roles["event_ledger"]))
        if len(events) != D_REQUIRED:
            raise RunnerError("D=804 event ledger changed")
        event_ids = [str(event["event_id"]) for event in events]
        if len(set(event_ids)) != D_REQUIRED:
            raise RunnerError("event identities are not unique")
        expected_legs = _event_legs(events)
        starts = {
            str(row["event_id"]): row
            for row in read_jsonl(resolve_role(repo, roles["start_ledger"]))
        }
        if set(starts) != set(event_ids):
            raise RunnerError("V5 boundary event set changed")
        unique_rows = read_jsonl(resolve_role(
            repo, roles["unique_guarded_fill_ledger"]
        ))
        fills = adapt_unique_fill_rows(
            unique_rows,
            expected_candidates=frozenset(CANDIDATE_IDS),
            expected_legs=expected_legs,
        )
        if len(fills) != 991:
            raise RunnerError("unique guarded-fill row count changed")
        cache_root = resolve_role(repo, roles["guarded_cache_directory"])
        references: dict[tuple[str, str], Any] = {}
        for ordinal, event in enumerate(events, 1):
            event_id = str(event["event_id"])
            cache = _load_cache(cache_root / f"{event_id}.json.gz")
            cache_legs = {
                str(leg["ticker"]): leg for leg in cache.get("legs") or []
            }
            for leg in event["legs"]:
                leg_id = str(leg.get("leg_id") or leg.get("leg"))
                ticker = str(leg["ticker"])
                cached = cache_legs.get(ticker)
                if not isinstance(cached, Mapping):
                    raise RunnerError("guarded-cache leg identity missing")
                references[(event_id, leg_id)] = (
                    derive_window1_close_reference(
                        event=event, leg=leg,
                        boundary=starts[event_id],
                        true_prints=cached.get("prints") or [],
                    )
                )
            if ordinal % 100 == 0:
                progress.emit(f"references_derived={ordinal}")
        summaries = []
        for ordinal, candidate_id in enumerate(CANDIDATE_IDS, 1):
            progress.emit(f"candidate_start={ordinal}:{candidate_id}")
            rows = []
            for event in events:
                event_id = str(event["event_id"])
                fill_map: dict[str, Any] = {}
                reference_map: dict[str, Any] = {}
                for leg in event["legs"]:
                    leg_id = str(leg.get("leg_id") or leg.get("leg"))
                    fill = fills.get((candidate_id, event_id, leg_id))
                    if fill is not None:
                        fill_map[leg_id] = fill
                    reference_map[leg_id] = references[(event_id, leg_id)]
                rows.append(score_event(
                    candidate_id=candidate_id,
                    event=event,
                    boundary=starts[event_id],
                    fills_by_leg=fill_map,
                    references_by_leg=reference_map,
                ))
            summary = aggregate_candidate(candidate_id, rows)
            summaries.append(summary)
            write_jsonl(
                result_dir / f"{ordinal:02d}_{candidate_id}_EVENT_LEDGER.jsonl",
                rows,
            )
            start_receipt["scorer_invocations"] = ordinal
            write_json(
                result_dir / "EXECUTION_START_RECEIPT.json", start_receipt
            )
            progress.emit(f"candidate_complete={ordinal}:{candidate_id}")
        write_json(result_dir / "TWO_CANDIDATE_RESULTS.json", {
            "schema_version": VERSION + "-two-candidate-results-v1",
            "execution_id": EXECUTION_ID,
            "candidate_order": list(CANDIDATE_IDS),
            "candidate_results": summaries,
            "ranking_or_selection_applied": False,
            "selected_candidate": None,
        })
        write_json(result_dir / "METRIC_CONSERVATION_REPORT.json", {
            "schema_version": VERSION + "-conservation-v1",
            "execution_id": EXECUTION_ID,
            "candidate_rows": [
                {
                    "candidate_id": summary["candidate_id"],
                    "D": summary["raw_integers_before_percentages"]["D"],
                    "classification_total":
                        summary["classification_conservation"]["total"],
                    "gate_pass":
                        summary["classification_conservation"]["equals_D804"],
                }
                for summary in summaries
            ],
            "all_candidates_conserve_D804": all(
                summary["classification_conservation"]["equals_D804"]
                for summary in summaries
            ),
        })
        write_json(
            result_dir / "HOLDOUT_NONPRODUCTION_NONACCESS_PROOF.json",
            {
                "schema_version": VERSION + "-nonaccess-v1",
                "execution_id": EXECUTION_ID,
                "development_dates": [
                    f"2026-07-{day:02d}" for day in range(12, 21)
                ],
                "sealed_dates": [
                    f"2026-07-{day:02d}" for day in range(24, 27)
                ],
                "holdout_opened": False,
                "holdout_queried": False,
                "network_calls": 0,
                "live_or_production_access": False,
                "prohibited_surface_writes": [],
                "only_results_directory_written": RESULTS_DIRECTORY,
            },
        )
        ended = dt.datetime.now(dt.timezone.utc)
        write_json(result_dir / "EXECUTION_MANIFEST.json", {
            **start_receipt,
            "schema_version": VERSION + "-execution-v1",
            "ended_at_utc": ended.isoformat(),
            "exit_code": 0,
            "scorer_invocations": 2,
            "console_echo": console.receipt(),
            "ranking_or_selection_applied": False,
        })
        write_json(
            result_dir / "OUTPUT_HASH_MANIFEST.json",
            _output_hashes(result_dir),
        )
        return 0
    except Exception as exc:
        ended = dt.datetime.now(dt.timezone.utc)
        message = f"{type(exc).__name__}: {exc}"
        (result_dir / "STDERR.log").write_text(
            message + "\n" + traceback.format_exc(),
            encoding="utf-8", newline="\n",
        )
        write_json(result_dir / "EXECUTION_FAILURE.json", {
            "schema_version": VERSION + "-failure-v1",
            "execution_id": EXECUTION_ID,
            "started_at_utc": started.isoformat(),
            "ended_at_utc": ended.isoformat(),
            "exit_code": 1,
            "error": message,
            "retry_or_resume_permitted": False,
            "partial_artifacts_preserved": True,
        })
        write_json(
            result_dir / "OUTPUT_HASH_MANIFEST.json",
            _output_hashes(result_dir),
        )
        console.stderr(message)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument(
        "--mode", choices=("validate-only", "execute"), required=True
    )
    parser.add_argument("--authorization-commit")
    parser.add_argument("--authorization-report")
    args = parser.parse_args()
    repo = args.repo.resolve()
    package = (
        args.package.resolve()
        if args.package.is_absolute()
        else (repo / args.package).resolve()
    )
    if args.mode == "validate-only":
        if args.authorization_commit or args.authorization_report:
            raise RunnerError("authorization arguments forbidden in validation")
        ConsoleEchoGuard().stdout(json.dumps(
            validation_only(repo, package), sort_keys=True
        ))
        return 0
    if not args.authorization_commit or not args.authorization_report:
        raise RunnerError(
            "execute mode requires a future independent PASS audit SHA/report"
        )
    return execute(
        repo, package,
        args.authorization_commit, args.authorization_report,
    )


if __name__ == "__main__":
    raise SystemExit(main())
