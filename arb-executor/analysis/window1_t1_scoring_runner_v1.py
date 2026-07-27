#!/usr/bin/env python3
"""Stdout-safe, independently gated runner for the frozen T1 package."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import sys
import traceback
from pathlib import Path
from typing import Any, Mapping

from window1_range_attack_reference_adapter_v2 import (
    derive_window1_close_reference,
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
from window1_range_attack_scoring_runner_v2 import (
    canonical_text_bytes,
    git_blob_oid,
    load_and_verify_authorization_report,
)
from window1_t1_scoring_adapter_v1 import (
    CLASSIFICATIONS,
    D_REQUIRED,
    T1ScoringAdapterError,
    adapt_t1_unique_fill_rows,
    aggregate_t1_candidate,
    score_t1_event,
)


VERSION = "window1-t1-scoring-runner-v1"
IMPLEMENTATION_PARENT = "88b0eae8620172f41e2f5d45320408357de24c6f"
CONTROLLING_T1_PASS = "de2f627e53885bd1a44a42b92f23b5b93a391a47"
AUDITED_SCORER_COMMIT = "e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd"
PACKAGE_DIRECTORY = ".claude/window1_t1_scoring_package_prerun_20260727"
PACKAGE_PATH = f"{PACKAGE_DIRECTORY}/SCORING_INPUT_MANIFEST.json"
EXECUTION_ID = "w1-t1-dev-20260712-20260720-grid1-scorepkg-v1"
RESULTS_DIRECTORY = f".claude/window1_t1_results_{EXECUTION_ID}"
CANDIDATE_IDS = (
    "w1_t1__macro_hold__response_only",
    "w1_t1__macro_hold__target_completeness_only",
    "w1_t1__macro_hold__persistence_only",
    "w1_t1__macro_hold__full_stack",
    "w1_t1__macro_micro__response_only",
    "w1_t1__macro_micro__target_completeness_only",
    "w1_t1__macro_micro__persistence_only",
    "w1_t1__macro_micro__full_stack",
)
PARENT_IDS = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
CANDIDATE_TO_PARENT = {
    candidate: PARENT_IDS[0 if "__macro_hold__" in candidate else 1]
    for candidate in CANDIDATE_IDS
}
COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/window1_t1_scoring_runner_v1.py "
    f"--repo . --package {PACKAGE_PATH} --mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}


def _identity_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    return (
        canonical_text_bytes(raw)
        if path.suffix.lower() in TEXT_SUFFIXES else raw
    )


def _validate_rows(repo: Path, rows: list[Mapping[str, Any]]) -> None:
    seen: set[str] = set()
    for row in rows:
        relative = str(row.get("path") or "")
        if relative in seen:
            raise RunnerError("duplicate source-manifest path")
        seen.add(relative)
        path = resolve_role(repo, relative)
        if not path.is_file():
            raise RunnerError(f"bound source missing: {relative}")
        raw = _identity_bytes(path)
        if (
            len(raw) != int(row.get("identity_bytes") or -1)
            or hashlib.sha256(raw).hexdigest() != row.get("sha256")
            or git_blob_oid(raw) != row.get("git_blob_oid")
        ):
            raise RunnerError(f"bound source hash mismatch: {relative}")


def _validate_private(
    repo: Path,
    package: Mapping[str, Any],
    source: Mapping[str, Any],
) -> None:
    for row in source.get("private_runtime_inputs") or []:
        role = str(row["role"])
        path = resolve_role(repo, str(row["path"]))
        if role == "guarded_cache_v3_directory":
            hashes = read_json(resolve_role(
                repo, package["roles"]["guarded_cache_hash_set"]
            ))
            if len(hashes["event_files"]) != D_REQUIRED:
                raise RunnerError("guarded-cache set is not D=804")
            for item in hashes["event_files"]:
                child = path / str(item["file"])
                if (
                    not child.is_file()
                    or child.stat().st_size != int(item["bytes"])
                    or sha256_file(child) != item["sha256"]
                ):
                    raise RunnerError(
                        f"guarded-cache hash mismatch: {item['file']}"
                    )
        elif (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256_file(path) != row["sha256"]
        ):
            raise RunnerError(f"private input mismatch: {role}")


def _validate_artifacts(repo: Path) -> None:
    manifest = read_json(resolve_role(
        repo, f"{PACKAGE_DIRECTORY}/PACKAGE_ARTIFACT_MANIFEST.json"
    ))
    for row in manifest.get("artifacts") or []:
        path = resolve_role(repo, str(row["path"]))
        raw = _identity_bytes(path) if path.is_file() else b""
        if (
            not path.is_file()
            or len(raw) != int(row["identity_bytes"])
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
            or git_blob_oid(raw) != row["git_blob_oid"]
        ):
            raise RunnerError(f"package artifact mismatch: {row['path']}")


def validate_package(
    repo: Path, package_path: Path, *, verify_private_inputs: bool
) -> dict[str, Any]:
    if package_path.resolve() != resolve_role(repo, PACKAGE_PATH):
        raise RunnerError("package path differs from frozen path")
    package = read_json(package_path)
    if (
        package.get("schema_version")
        != "window1-t1-scoring-input-manifest-v1"
        or package.get("implementation_parent") != IMPLEMENTATION_PARENT
        or package.get("controlling_T1_PASS") != CONTROLLING_T1_PASS
        or package.get("audited_scorer_commit") != AUDITED_SCORER_COMMIT
        or package.get("execution_id") != EXECUTION_ID
        or tuple(package.get("candidate_ids") or ()) != CANDIDATE_IDS
        or tuple(package.get("parent_reference_candidate_ids") or ())
        != PARENT_IDS
        or package.get("D") != D_REQUIRED
        or package.get("command_template_literal") != COMMAND_TEMPLATE
        or package.get("metrics") is not None
        or package.get("performance") is not None
        or package.get("scored") is not False
        or package.get("future_independent_PASS_required") is not True
    ):
        raise RunnerError("frozen T1 package identity changed")
    payload = package.get("input_bundle_payload")
    if (
        not isinstance(payload, Mapping)
        or canonical_sha256(payload) != package.get("input_bundle_sha256")
    ):
        raise RunnerError("input-bundle hash mismatch")
    forbidden_roles = {
        "T1_overlays", "raw_policy_actions",
        "causal_policy_fill_state_by_leg", "candidate_order_streams",
    }
    if forbidden_roles.intersection(package["roles"]):
        raise RunnerError("raw policy surface leaked into runtime roles")
    source = read_json(resolve_role(
        repo, package["roles"]["source_hash_manifest"]
    ))
    _validate_rows(repo, source["committed_inputs"])
    _validate_artifacts(repo)
    unique = source["T1_unique_runtime_fill_ledger"]
    unique_path = resolve_role(
        repo, package["roles"]["unique_T1_fill_ledger"]
    )
    if (
        not unique_path.is_file()
        or unique_path.stat().st_size != int(unique["bytes"])
        or sha256_file(unique_path) != unique["sha256"]
    ):
        raise RunnerError("T1 unique fill ledger hash mismatch")
    if verify_private_inputs:
        _validate_private(repo, package, source)
    if resolve_role(repo, RESULTS_DIRECTORY).exists():
        raise RunnerError("execution ID/results directory already exists")
    return {
        "package": package,
        "source_manifest": source,
        "head": git(repo, "rev-parse", "HEAD"),
    }


def authorize_execute(
    repo: Path,
    validated: Mapping[str, Any],
    audit_commit: str,
    audit_report_path: str,
) -> str:
    package = validated["package"]
    head = str(validated["head"])
    load_and_verify_authorization_report(
        repo,
        audit_commit=audit_commit,
        audit_report_path=audit_report_path,
        audit_ref="refs/remotes/origin/audit/window1-independent",
        package_commit=head,
        execution_id=EXECUTION_ID,
        bundle_sha256=str(package["input_bundle_sha256"]),
        command_template=COMMAND_TEMPLATE,
    )
    if git(repo, "rev-parse", "HEAD^") != IMPLEMENTATION_PARENT:
        raise RunnerError("package is not the sole child of frozen parent")
    if git(repo, "rev-parse", "HEAD") != git(
        repo, "rev-parse", "refs/remotes/origin/codex/window1-definition"
    ):
        raise RunnerError("local/remote package equality failed")
    if git(repo, "status", "--porcelain"):
        raise RunnerError("execution worktree is not clean")
    return (
        "python -B arb-executor/analysis/window1_t1_scoring_runner_v1.py "
        f"--repo . --package {PACKAGE_PATH} --mode execute "
        f"--authorization-commit {audit_commit} "
        f"--authorization-report {audit_report_path}"
    )


def validation_only(repo: Path, package_path: Path) -> dict[str, Any]:
    validated = validate_package(
        repo, package_path, verify_private_inputs=False
    )
    return {
        "schema_version": VERSION + "-validation-only-v1",
        "candidate_ids": list(CANDIDATE_IDS),
        "D": D_REQUIRED,
        "input_bundle_sha256": validated["package"]["input_bundle_sha256"],
        "real_population_loaded": False,
        "fill_adapter_invoked": False,
        "reference_adapter_invoked": False,
        "scorer_invoked": False,
        "performance_metrics": {
            candidate: {"C": None, "PC": None, "IC": None, "S": None}
            for candidate in CANDIDATE_IDS
        },
        "future_independent_PASS_required": True,
        "gate_pass": True,
    }


def _parent_rows(repo: Path, binding: Mapping[str, Any]) -> dict[
    tuple[str, str], Mapping[str, Any]
]:
    rows: dict[tuple[str, str], Mapping[str, Any]] = {}
    for receipt in binding["audited_parent_result_ledgers"]:
        relative = str(receipt["path"])
        for row in read_jsonl(resolve_role(repo, relative)):
            key = (str(row["candidate_id"]), str(row["event_id"]))
            if key in rows:
                raise RunnerError("duplicate parent reference event row")
            rows[key] = row
    if len(rows) != 2 * D_REQUIRED:
        raise RunnerError("parent reference event set changed")
    return rows


def _changed_from_parent(
    row: Mapping[str, Any], parent: Mapping[str, Any]
) -> bool:
    def signature(value: Mapping[str, Any]) -> tuple[Any, ...]:
        prices = tuple(
            leg.get("accounting_fill_price_cents")
            for leg in value.get("legs") or []
        )
        return (
            value.get("classification"), value.get("C"), value.get("PC"),
            value.get("IC"), value.get("S"), prices,
        )
    return signature(row) != signature(parent)


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
            repo, roles["unique_T1_fill_ledger"]
        ))
        fills = adapt_t1_unique_fill_rows(
            unique_rows,
            expected_candidates=frozenset(CANDIDATE_IDS),
            candidate_to_parent=CANDIDATE_TO_PARENT,
            expected_legs=expected_legs,
        )
        parent_binding = read_json(resolve_role(
            repo, roles["parent_reference_binding"]
        ))
        parent_rows = _parent_rows(repo, parent_binding)
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
                    raise RunnerError("guarded-cache leg missing")
                references[(event_id, leg_id)] = (
                    derive_window1_close_reference(
                        event=event, leg=leg, boundary=starts[event_id],
                        true_prints=cached.get("prints") or [],
                    )
                )
            if ordinal % 100 == 0:
                progress.emit(f"references_derived={ordinal}")
        summaries = []
        for ordinal, candidate_id in enumerate(CANDIDATE_IDS, 1):
            progress.emit(f"candidate_start={ordinal}:{candidate_id}")
            candidate_rows = []
            parent_id = CANDIDATE_TO_PARENT[candidate_id]
            change_count = 0
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
                row = score_t1_event(
                    candidate_id=candidate_id,
                    parent_candidate_id=parent_id,
                    event=event,
                    boundary=starts[event_id],
                    fills_by_leg=fill_map,
                    references_by_leg=reference_map,
                )
                change_count += _changed_from_parent(
                    row, parent_rows[(parent_id, event_id)]
                )
                candidate_rows.append(row)
            summary = aggregate_t1_candidate(
                candidate_id=candidate_id,
                parent_candidate_id=parent_id,
                rows=candidate_rows,
            )
            summary["candidate_versus_parent_event_level_change_count"] = (
                change_count
            )
            summaries.append(summary)
            write_jsonl(
                result_dir / f"{ordinal:02d}_{candidate_id}_EVENT_LEDGER.jsonl",
                candidate_rows,
            )
            start_receipt["scorer_invocations"] = ordinal
            write_json(
                result_dir / "EXECUTION_START_RECEIPT.json", start_receipt
            )
            progress.emit(f"candidate_complete={ordinal}:{candidate_id}")
        write_json(result_dir / "EIGHT_CANDIDATE_RESULTS.json", {
            "schema_version": VERSION + "-eight-candidate-results-v1",
            "execution_id": EXECUTION_ID,
            "candidate_order": list(CANDIDATE_IDS),
            "candidate_results": summaries,
            "parent_reference_candidates": list(PARENT_IDS),
            "ranking_or_selection_applied": False,
            "selected_candidate": None,
        })
        conservation = [
            {
                "candidate_id": summary["candidate_id"],
                "D": summary["D"],
                "classification_total": (
                    summary["classification_conservation"]["total"]
                ),
                "gate_pass": (
                    summary["classification_conservation"]["equals_D804"]
                ),
            }
            for summary in summaries
        ]
        write_json(result_dir / "METRIC_CONSERVATION_REPORT.json", {
            "schema_version": VERSION + "-conservation-v1",
            "candidate_rows": conservation,
            "all_candidates_conserve_D804": all(
                row["gate_pass"] for row in conservation
            ),
        })
        write_json(
            result_dir / "HOLDOUT_NONPRODUCTION_NONACCESS_PROOF.json",
            {
                "schema_version": VERSION + "-nonaccess-v1",
                "execution_id": EXECUTION_ID,
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
            "scorer_invocations": 8,
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
            raise RunnerError("authorization forbidden in validate-only")
        ConsoleEchoGuard().stdout(json.dumps(
            validation_only(repo, package), sort_keys=True
        ))
        return 0
    if not args.authorization_commit or not args.authorization_report:
        raise RunnerError(
            "execute requires a future independent PASS audit SHA/report"
        )
    return execute(
        repo, package, args.authorization_commit, args.authorization_report
    )


if __name__ == "__main__":
    raise SystemExit(main())
