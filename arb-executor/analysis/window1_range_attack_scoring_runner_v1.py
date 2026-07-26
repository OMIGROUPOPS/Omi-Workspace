#!/usr/bin/env python3
"""Stdout-safe deterministic runner for the frozen Range-Attack scorer.

Packaging and validation do not invoke the scorer.  Execute mode is locked
behind a later independent PASS audit commit and an exact authorization report.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Iterable, Mapping


ANALYSIS_DIR = Path(__file__).resolve().parent
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))

from window1_range_attack_guarded_fill_adapter_v1 import (  # noqa: E402
    GuardedFillError,
    adapt_fillability_rows,
)
from window1_range_attack_reference_adapter_v1 import (  # noqa: E402
    ReferenceError,
    derive_window1_close_reference,
)
from window1_range_attack_scorer_v1 import (  # noqa: E402
    CANDIDATE_IDS,
    D_REQUIRED,
    RangeAttackScoringError,
    aggregate_candidate,
    canonical_sha256,
    score_event,
)


VERSION = "window1-range-attack-stdout-safe-runner-v1"
IMPLEMENTATION_PARENT = "851346343eecbff64bd836992876592784874c86"
CONTROLLING_PASS_AUDIT = "5579b93774267779ae916eb9cb46766de66a9efe"
EXECUTION_ID = "w1-range-attack-v2-dev-20260712-20260720-grid1"
PACKAGE_PATH = (
    ".claude/window1_range_attack_scoring_package_prerun_20260726/"
    "SCORING_INPUT_MANIFEST.json"
)
RESULTS_DIRECTORY = (
    ".claude/window1_range_attack_results_"
    "w1-range-attack-v2-dev-20260712-20260720-grid1"
)
EXECUTION_COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/"
    "window1_range_attack_scoring_runner_v1.py --repo . --package "
    f"{PACKAGE_PATH} --mode execute --authorization-commit "
    "{FUTURE_PASS_AUDIT_SHA} --authorization-report "
    "{FUTURE_AUDIT_REPORT_PATH}"
)


class RunnerError(RuntimeError):
    """Raised when package, authorization, or execution invariants fail."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact(row) + "\n")


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode:
        raise RunnerError(
            f"git {' '.join(args)} failed: {process.stderr.strip()}"
        )
    return process.stdout.strip()


def resolve_role(repo: Path, relative: str) -> Path:
    if not relative or "\x00" in relative:
        raise RunnerError("invalid frozen role path")
    lowered = relative.replace("\\", "/").lower()
    if any(token in lowered for token in (
        "2026-07-24", "2026-07-25", "2026-07-26", "holdout"
    )):
        raise RunnerError("holdout role path refused")
    path = (repo / relative).resolve()
    permitted = {
        repo.resolve(),
        (repo / "../OMI-Window1-private").resolve(),
    }
    if not any(path == root or root in path.parents for root in permitted):
        raise RunnerError("role escapes frozen repo/private roots")
    return path


class ConsoleEchoGuard:
    """Make cosmetic stdout/stderr loss nonfatal and exit-flush safe."""

    def __init__(self) -> None:
        self.stdout_enabled = True
        self.stderr_enabled = True
        self._devnull_handles: list[Any] = []

    def _disable(self, name: str) -> None:
        handle = open(os.devnull, "w", encoding="utf-8")
        self._devnull_handles.append(handle)
        setattr(sys, name, handle)
        setattr(self, f"{name}_enabled", False)

    def stdout(self, line: str) -> None:
        if not self.stdout_enabled:
            return
        try:
            print(line, flush=True)
        except (OSError, ValueError):
            self._disable("stdout")

    def stderr(self, line: str) -> None:
        if not self.stderr_enabled:
            return
        try:
            print(line, file=sys.stderr, flush=True)
        except (OSError, ValueError):
            self._disable("stderr")

    def receipt(self) -> dict[str, Any]:
        return {
            "stdout_enabled_at_end": self.stdout_enabled,
            "stderr_enabled_at_end": self.stderr_enabled,
            "devnull_handles_retained": len(self._devnull_handles),
            "console_authoritative": False,
        }


class ProgressEmitter:
    """Persist each complete progress line before cosmetic console echo."""

    def __init__(self, path: Path, console: ConsoleEchoGuard) -> None:
        self.path = path
        self.console = console

    def emit(self, line: str) -> None:
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line.rstrip("\r\n") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.console.stdout(line)


def _expected_git_blob(repo: Path, path: Path) -> str:
    return git(repo, "hash-object", str(path))


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
        if path.stat().st_size != int(row.get("bytes") or -1):
            raise RunnerError(f"byte length mismatch: {relative}")
        if sha256_file(path) != row.get("sha256"):
            raise RunnerError(f"SHA-256 mismatch: {relative}")
        blob = row.get("git_blob_oid")
        if blob is not None and _expected_git_blob(repo, path) != blob:
            raise RunnerError(f"Git blob mismatch: {relative}")


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
        != "window1-range-attack-scoring-input-manifest-v1"
        or package.get("implementation_parent") != IMPLEMENTATION_PARENT
        or package.get("controlling_pass_audit") != CONTROLLING_PASS_AUDIT
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
    source_manifest = read_json(resolve_role(
        repo, str(package["roles"]["source_hash_manifest"])
    ))
    _validate_source_rows(repo, source_manifest["committed_inputs"])
    if verify_private_inputs:
        _validate_private_sources(repo, package, source_manifest)
    if package.get("future_independent_pass_required") is not True:
        raise RunnerError("future independent PASS gate is not frozen")
    if Path(resolve_role(repo, RESULTS_DIRECTORY)).exists():
        raise RunnerError("execution ID/results directory already exists")
    return {
        "package": package,
        "source_manifest": source_manifest,
        "head": git(repo, "rev-parse", "HEAD"),
    }


def _validate_private_sources(
    repo: Path,
    package: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
) -> None:
    private = source_manifest.get("private_inputs")
    if not isinstance(private, list):
        raise RunnerError("private input receipts missing")
    for row in private:
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
        else:
            if (
                not path.is_file()
                or path.stat().st_size != int(row["bytes"])
                or sha256_file(path) != row["sha256"]
            ):
                raise RunnerError(f"private input mismatch: {role}")


def authorize_execute(
    repo: Path,
    validated: Mapping[str, Any],
    audit_commit: str,
    audit_report_path: str,
) -> str:
    if len(audit_commit) != 40 or any(
        char not in "0123456789abcdef" for char in audit_commit.lower()
    ):
        raise RunnerError("future audit SHA must be a full 40-character SHA")
    if git(
        repo, "merge-base", "--is-ancestor",
        audit_commit, "refs/remotes/origin/audit/window1-independent",
    ) != "":
        raise RunnerError("unexpected merge-base output")
    report = git(repo, "show", f"{audit_commit}:{audit_report_path}")
    package = validated["package"]
    head = validated["head"]
    exact_command = EXECUTION_COMMAND_TEMPLATE.format(
        FUTURE_PASS_AUDIT_SHA=audit_commit,
        FUTURE_AUDIT_REPORT_PATH=audit_report_path,
    )
    required = (
        "PASS",
        head,
        EXECUTION_ID,
        str(package["input_bundle_sha256"]),
        exact_command,
    )
    if any(value not in report for value in required):
        raise RunnerError(
            "future independent report does not authorize exact package, "
            "execution ID, bundle, and command"
        )
    if git(repo, "rev-parse", "HEAD^") != IMPLEMENTATION_PARENT:
        raise RunnerError("execution package is not the sole parent child")
    if git(repo, "status", "--porcelain"):
        raise RunnerError("execution worktree is not clean")
    return exact_command


def validation_only(repo: Path, package_path: Path) -> dict[str, Any]:
    validated = validate_package(
        repo, package_path, verify_private_inputs=False
    )
    package = validated["package"]
    return {
        "schema_version": VERSION + "-validation-only-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_pass_audit": CONTROLLING_PASS_AUDIT,
        "candidate_ids": list(CANDIDATE_IDS),
        "D": D_REQUIRED,
        "input_bundle_sha256": package["input_bundle_sha256"],
        "future_independent_pass_required": True,
        "real_population_loaded": False,
        "fill_adapter_invoked": False,
        "reference_adapter_invoked": False,
        "scorer_invoked": False,
        "performance_metrics": {
            "C": None, "PC": None, "S": None, "IC": None
        },
        "gate_pass": True,
    }


def _event_legs(events: list[Mapping[str, Any]]) -> dict[tuple[str, str], str]:
    output: dict[tuple[str, str], str] = {}
    for event in events:
        event_id = str(event["event_id"])
        for leg in event["legs"]:
            leg_id = str(leg.get("leg_id") or leg.get("leg"))
            ticker = str(leg["ticker"])
            key = (event_id, leg_id)
            if key in output or ticker in output.values():
                raise RunnerError("duplicate event/leg/ticker identity")
            output[key] = ticker
    if len(output) != 1608:
        raise RunnerError("1,608 leg identity law changed")
    return output


def _load_cache(path: Path) -> Mapping[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


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
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
        },
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
        fill_rows = read_jsonl(resolve_role(
            repo, roles["guarded_fillability_receipts"]
        ))
        fills = adapt_fillability_rows(
            fill_rows,
            expected_candidates=frozenset(CANDIDATE_IDS),
            expected_legs=expected_legs,
        )
        cache_root = resolve_role(repo, roles["guarded_cache_directory"])
        references: dict[tuple[str, str], Any] = {}
        for ordinal, event in enumerate(events, 1):
            event_id = str(event["event_id"])
            cache = _load_cache(cache_root / f"{event_id}.json.gz")
            if str(cache.get("event_id")) != event_id:
                raise RunnerError("guarded-cache event identity changed")
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
                        event=event,
                        leg=leg,
                        boundary=starts[event_id],
                        true_prints=cached.get("prints") or [],
                    )
                )
            if ordinal % 100 == 0:
                progress.emit(f"references_derived={ordinal}")

        all_summaries = []
        for candidate_ordinal, candidate_id in enumerate(CANDIDATE_IDS, 1):
            progress.emit(
                f"candidate_start={candidate_ordinal}:{candidate_id}"
            )
            rows = []
            for event in events:
                event_id = str(event["event_id"])
                fill_map = {}
                reference_map = {}
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
            all_summaries.append(summary)
            write_jsonl(
                result_dir / (
                    f"{candidate_ordinal:02d}_{candidate_id}_EVENT_LEDGER.jsonl"
                ),
                rows,
            )
            start_receipt["scorer_invocations"] = candidate_ordinal
            write_json(
                result_dir / "EXECUTION_START_RECEIPT.json", start_receipt
            )
            progress.emit(
                f"candidate_complete={candidate_ordinal}:{candidate_id}"
            )
        write_json(result_dir / "TWO_CANDIDATE_RESULTS.json", {
            "schema_version": VERSION + "-two-candidate-results-v1",
            "execution_id": EXECUTION_ID,
            "candidate_order": list(CANDIDATE_IDS),
            "candidate_results": all_summaries,
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
                    "classification_total": summary[
                        "classification_conservation"
                    ]["total"],
                    "gate_pass": summary[
                        "classification_conservation"
                    ]["equals_D804"],
                }
                for summary in all_summaries
            ],
            "all_candidates_conserve_D804": all(
                summary["classification_conservation"]["equals_D804"]
                for summary in all_summaries
            ),
        })
        write_json(result_dir / "HOLDOUT_NONPRODUCTION_NONACCESS_PROOF.json", {
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
        })
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
    except (
        GuardedFillError,
        ReferenceError,
        RangeAttackScoringError,
        RunnerError,
        Exception,
    ) as exc:
        ended = dt.datetime.now(dt.timezone.utc)
        message = f"{type(exc).__name__}: {exc}"
        (result_dir / "STDERR.log").write_text(
            message + "\n" + traceback.format_exc(),
            encoding="utf-8",
            newline="\n",
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
        value = validation_only(repo, package)
        ConsoleEchoGuard().stdout(json.dumps(value, sort_keys=True))
        return 0
    if not args.authorization_commit or not args.authorization_report:
        raise RunnerError(
            "execute mode requires a future independent PASS audit SHA/report"
        )
    return execute(
        repo,
        package,
        args.authorization_commit,
        args.authorization_report,
    )


if __name__ == "__main__":
    raise SystemExit(main())
