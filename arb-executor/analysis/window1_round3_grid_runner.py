#!/usr/bin/env python3
"""Deterministic one-shot Round-3 Window-1 grid execution package.

This additive runner does not define policy, metric, guard, ranking, or
selection law.  It reads the eight already-frozen counterfactual stream sets
from the hash-bound scoring-input bundle, verifies every stream against the
PRE-RUN receipt set, and invokes the already-frozen scorer exactly once per
candidate.

The ``validate-only`` mode performs receipt/date/order/dispatch validation
only.  It never runs a candidate instrument or scorer and never emits
performance data.
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
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import window1_round2_data_binding as data_binding
import window1_round2_real_capability as capability
import window1_round2_scorer as scorer


VERSION = "window1-round3-deterministic-grid-runner-stdout-safe-v1"
PACKAGE_SCHEMA = "window1-round3-execution-package-stdout-safe-v1"
EXECUTION_ID = (
    "w1r3-dev-20260712-20260720-14e0e846-grid1-stdoutsafe"
)
AUTHORIZED_PARENT = "14e0e846e8922da98f656aef1f43d2c48da96ee7"
ROUND2_RESULTS = "10ac6dbc68d65cb21ab3718e118ff34d7220ad87"
ROUND2_RESULTS_AUDIT = "807e2c865c3cf7384757c54a3b879518568dec4f"
ROUND2_AUDIT_REPORT_PATH = (
    ".claude/audit_20260725_grid2_results/AUDIT_REPORT.md"
)
ROUND2_AUDIT_REPORT_BLOB_OID = "9bb51a3dc19fd055156ee958a6f208b1a725cbc4"
ROUND3_PRERUN_AUDIT = "b415a98e2430642242f8e0205fb9b5edfee841b5"
ROUND3_AUDIT_REPORT_PATH = (
    ".claude/audit_20260725_round3_prerun/AUDIT_REPORT.md"
)
ROUND3_AUDIT_REPORT_BLOB_OID = "e4b32d218f3e4e1feeb3043ff4f4b3ba36033ac0"
AUTHORIZED_AUDIT = ROUND3_PRERUN_AUDIT
PACKAGE_PATH = (
    ".claude/window1_round3_execution_package_20260725/"
    "SCORING_INPUT_BUNDLE.json"
)
RESULT_DIRECTORY = (
    ".claude/window1_round3_results_"
    "w1r3-dev-20260712-20260720-14e0e846-grid1-stdoutsafe"
)
VALIDATION_RECEIPT_PATH = (
    ".claude/window1_round3_execution_package_20260725/"
    "VALIDATION_ONLY_RECEIPT.json"
)
STREAM_BUNDLE_PATH = (
    ".claude/window1_round3_prerun_20260725/"
    "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
)
EXACT_EXECUTION_COMMAND = (
    "python -B arb-executor/analysis/window1_round3_grid_runner.py "
    "--repo . --package "
    ".claude/window1_round3_execution_package_20260725/"
    "SCORING_INPUT_BUNDLE.json --mode execute"
)
EXACT_VALIDATION_COMMAND = (
    "python -B arb-executor/analysis/window1_round3_grid_runner.py "
    "--repo . --package "
    ".claude/window1_round3_execution_package_20260725/"
    "SCORING_INPUT_BUNDLE.json --mode validate-only"
)
FROZEN_CANDIDATES = [
    "r3_pair_presence__park_join__hold",
    "r3_pair_presence__park_join__reaim",
    "r3_pair_presence__touch_park__hold",
    "r3_pair_presence__touch_park__reaim",
    "r3_causal_steer__park_join__hold",
    "r3_causal_steer__park_join__reaim",
    "r3_full_os__walk_park__hold",
    "r3_full_os__walk_park__reaim",
]
FROZEN_PAIRS = [
    (FROZEN_CANDIDATES[index], FROZEN_CANDIDATES[index + 1])
    for index in range(0, len(FROZEN_CANDIDATES), 2)
]
DEV_DATES = [f"2026-07-{day:02d}" for day in range(12, 21)]
HOLDOUT_DATES = [f"2026-07-{day:02d}" for day in range(24, 27)]
FROZEN_GIT_INPUT_PATHS = sorted([
    STREAM_BUNDLE_PATH,
    ".claude/entrysurface_20260717/band_map_v1.json",
    ".claude/entrysurface_20260717/divot_tables_v1.json",
    ".claude/entrysurface_20260717/drift_surfaces_v1.json",
    ".claude/master_20260709/cohort.json",
    ".claude/seqfloor_20260708/recut_cells.json",
    ".claude/trendpath/ORIENT_V1.json",
    ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl",
    (
        ".claude/window1_round3_prerun_20260725/"
        "ROUND3_REAIM_ORDER_DIFFERENCES.jsonl"
    ),
    (
        ".claude/window1_round3_prerun_20260725/"
        "ROUND3_REAL_CAPABILITY.json"
    ),
    (
        ".claude/window1_round3_execution_package_20260725/"
        "SCORER_FREEZE_CONTRACT.json"
    ),
    (
        ".claude/window1_round2_prerun_v2_20260724/"
        "ROUND2_DATA_BINDING_MANIFEST.json"
    ),
    (
        ".claude/window1_start_guard_corrected_20260724/"
        "REAL_START_LEDGER_V5.jsonl"
    ),
    "arb-executor/analysis/window1_round2_data_binding.py",
    "arb-executor/analysis/window1_round3_grid_runner.py",
    "arb-executor/analysis/window1_round3_instrument.py",
    "arb-executor/analysis/window1_round2_real_capability.py",
    "arb-executor/analysis/window1_round2_scorer.py",
    (
        "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND3_CANDIDATES_V1.json"
    ),
    (
        "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json"
    ),
    (
        "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND2_SCORER_CONTRACT_V1.json"
    ),
])
FROZEN_EXTERNAL_INPUT_PATHS = [
    "../OMI-Window1-private/joined/events.jsonl",
    "../OMI-Window1-private/fit-local/prints.jsonl",
    (
        "../OMI-Window1-private/fit-local/"
        "PUBLIC_TAPE_MANIFEST.sanitized.json"
    ),
]
PRIMARY_CENSUS = [
    "exact_five",
    "partial",
    "other_quantity",
    "genuine_nonfill",
    "naked_single_leg",
    "zero_length_window",
    "contradictory",
    "censored",
]
OUTPUT_FILENAMES = [
    "EXECUTION_START_RECEIPT.json",
    "EIGHT_CANDIDATE_RESULTS.json",
    "METRIC_CONSERVATION_REPORT.json",
    "BASE_REAIM_COMPARISON.json",
    "WINDOW1_ROUND3_DEVELOPMENT_REPORT.md",
    "HOLDOUT_NONPRODUCTION_NONACCESS_PROOF.json",
    "PROGRESS.log",
    "STDOUT.log",
    "STDERR.log",
    "EXECUTION_MANIFEST.json",
    "OUTPUT_HASH_MANIFEST.json",
]


def expected_progress_sequence() -> list[str]:
    return [
        f"execution_id={EXECUTION_ID}",
        "git_sha={RESULT_COMMIT_SHA}",
        *[
            line
            for ordinal, candidate_id in enumerate(FROZEN_CANDIDATES, 1)
            for line in (
                f"candidate_start={ordinal}:{candidate_id}",
                f"candidate_complete={ordinal}:{candidate_id}",
            )
        ],
        "final_receipt_publication_started",
        "output_hash_manifest_pending",
    ]


def expected_output_inventory() -> list[str]:
    candidate_ledgers = [
        f"{ordinal:02d}_{candidate_id}_EVENT_LEDGER.jsonl"
        for ordinal, candidate_id in enumerate(FROZEN_CANDIDATES, 1)
    ]
    return sorted([*OUTPUT_FILENAMES, *candidate_ledgers])


class GridExecutionError(RuntimeError):
    """Raised when a frozen grid execution or receipt contract is violated."""


class ConsoleEchoGuard:
    """Keep cosmetic console failures outside the authoritative run path."""

    def __init__(self) -> None:
        self.stdout_enabled = True
        self.stderr_enabled = True
        self.stdout_failure: str | None = None
        self.stderr_failure: str | None = None
        self._devnull_handles: list[Any] = []

    def _disable(self, stream_name: str, exc: BaseException) -> None:
        if stream_name == "stdout":
            self.stdout_enabled = False
            self.stdout_failure = f"{type(exc).__name__}: {exc}"
        else:
            self.stderr_enabled = False
            self.stderr_failure = f"{type(exc).__name__}: {exc}"
        devnull = open(os.devnull, "w", encoding="utf-8")
        self._devnull_handles.append(devnull)
        setattr(sys, stream_name, devnull)

    def echo_stdout(self, message: str) -> None:
        if not self.stdout_enabled:
            return
        try:
            print(message, file=sys.stdout, flush=True)
        except (OSError, ValueError) as exc:
            self._disable("stdout", exc)

    def echo_stderr(self, message: str) -> None:
        if not self.stderr_enabled:
            return
        try:
            print(message, file=sys.stderr, flush=True)
        except (OSError, ValueError) as exc:
            self._disable("stderr", exc)

    def receipt(self) -> dict[str, Any]:
        return {
            "stdout_enabled": self.stdout_enabled,
            "stdout_failure": self.stdout_failure,
            "stderr_enabled": self.stderr_enabled,
            "stderr_failure": self.stderr_failure,
            "stdout_rebound_to_devnull": not self.stdout_enabled,
            "stderr_rebound_to_devnull": not self.stderr_enabled,
        }


class ProgressEmitter:
    """Append authoritative progress before attempting cosmetic stdout."""

    def __init__(
        self,
        progress_path: Path,
        stdout_lines: list[str],
        console: ConsoleEchoGuard,
    ) -> None:
        self.progress_path = progress_path
        self.stdout_lines = stdout_lines
        self.console = console

    def __call__(self, message: str) -> None:
        if "\n" in message or "\r" in message:
            raise GridExecutionError("progress event must be exactly one line")
        with self.progress_path.open(
            "a", encoding="utf-8", newline="\n"
        ) as handle:
            handle.write(message + "\n")
            handle.flush()
        self.stdout_lines.append(message)
        self.console.echo_stdout(message)


class FrozenScorerDispatcher:
    """Enforce one scorer call per candidate in the frozen order."""

    def __init__(
        self,
        score_fn: Callable[
            [Mapping[str, Any], Mapping[str, Any]], dict[str, Any]
        ] = scorer.score_population,
    ) -> None:
        self._score_fn = score_fn
        self._next = 0
        self._counts = {
            candidate_id: 0 for candidate_id in FROZEN_CANDIDATES
        }

    @property
    def counts(self) -> dict[str, int]:
        return dict(self._counts)

    def invoke(
        self,
        candidate_id: str,
        bundle: Mapping[str, Any],
        contract: Mapping[str, Any],
    ) -> dict[str, Any]:
        if self._next >= len(FROZEN_CANDIDATES):
            raise GridExecutionError("additional scorer invocation refused")
        expected = FROZEN_CANDIDATES[self._next]
        if candidate_id != expected:
            raise GridExecutionError(
                f"reordered scorer invocation refused: "
                f"expected {expected}, got {candidate_id}"
            )
        if self._counts[candidate_id] != 0:
            raise GridExecutionError(
                f"duplicate scorer invocation refused: {candidate_id}"
            )
        result = self._score_fn(bundle, contract)
        self._counts[candidate_id] = 1
        self._next += 1
        return result

    def assert_complete(self) -> None:
        if (
            self._next != len(FROZEN_CANDIDATES)
            or any(value != 1 for value in self._counts.values())
        ):
            raise GridExecutionError(
                "missing frozen candidate scorer invocation"
            )


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GridExecutionError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    opener = (
        gzip.open(path, "rt", encoding="utf-8")
        if path.suffix == ".gz"
        else path.open(encoding="utf-8")
    )
    with opener as handle:
        for line in handle:
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise GridExecutionError(f"JSONL object required: {path}")
                rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text(
        "".join(compact(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise GridExecutionError(
            f"git {' '.join(args)} failed: "
            + result.stderr.decode(errors="replace").strip()
        )
    return result.stdout


def resolve_fixed(repo: Path, value: str) -> Path:
    path = Path(value)
    resolved = path.resolve() if path.is_absolute() else (repo / path).resolve()
    return resolved


def assert_exact_candidate_order(candidate_ids: Sequence[str]) -> None:
    values = list(candidate_ids)
    if values != FROZEN_CANDIDATES:
        if len(values) != len(set(values)):
            reason = "duplicated"
        elif set(values) != set(FROZEN_CANDIDATES):
            reason = "missing or additional"
        else:
            reason = "reordered"
        raise GridExecutionError(f"{reason} candidate grid refused")


def assert_exact_input_paths(
    actual: Sequence[str],
    expected: Sequence[str],
    label: str,
) -> None:
    values = list(actual)
    frozen = list(expected)
    if values != frozen:
        if len(values) != len(set(values)):
            reason = "duplicated"
        elif set(values) != set(frozen):
            reason = "missing or additional"
        else:
            reason = "reordered"
        raise GridExecutionError(f"{reason} {label} input refused")


def unexpected_worktree_status(repo: Path) -> list[str]:
    """Return every worktree change; Round-3 execution requires exact cleanliness."""
    return git(repo, "status", "--porcelain").decode().splitlines()


def validate_dates(rows: Sequence[Mapping[str, Any]]) -> None:
    if len(rows) != 804:
        raise GridExecutionError("D=804 event ledger required")
    event_ids = [str(row.get("event_id") or "") for row in rows]
    if len(set(event_ids)) != 804 or any(not value for value in event_ids):
        raise GridExecutionError("event identities are not exact D=804")
    dates = [str(row.get("event_date") or "") for row in rows]
    if any(value in HOLDOUT_DATES for value in dates):
        raise GridExecutionError("July 24-26 holdout hard-refused")
    if set(dates) - set(DEV_DATES):
        raise GridExecutionError("non-development date hard-refused")


def validate_result_directory_absent(repo: Path, package: Mapping[str, Any]) -> Path:
    result_dir = resolve_fixed(repo, str(package["result_directory"]))
    expected = resolve_fixed(repo, RESULT_DIRECTORY)
    if result_dir != expected:
        raise GridExecutionError("result directory differs from frozen path")
    if result_dir.exists():
        raise GridExecutionError("execution ID already exists; overwrite/resume refused")
    return result_dir


def _verify_git_input(
    repo: Path, row: Mapping[str, Any], *, git_ref: str,
) -> None:
    path = str(row["path"])
    spec = f":{path}" if git_ref == "INDEX" else f"HEAD:{path}"
    oid = git(repo, "rev-parse", spec).decode().strip()
    data = git(repo, "cat-file", "blob", oid)
    if (
        oid != row.get("git_blob_oid")
        or len(data) != row.get("bytes")
        or sha256_bytes(data) != row.get("sha256")
    ):
        raise GridExecutionError(f"Git input receipt mismatch: {path}")


def _verify_external_input(repo: Path, row: Mapping[str, Any]) -> None:
    path = resolve_fixed(repo, str(row["path"]))
    if not path.is_file():
        raise GridExecutionError(f"external input missing: {row['path']}")
    if (
        path.stat().st_size != row.get("bytes")
        or sha256_file(path) != row.get("sha256")
    ):
        raise GridExecutionError(f"external input receipt mismatch: {row['path']}")


def _load_frozen_stream_bundle(
    repo: Path,
    package: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, dict[str, dict[str, Any]]]:
    path_text = str(package["roles"]["candidate_event_streams"])
    if path_text != STREAM_BUNDLE_PATH:
        raise GridExecutionError("candidate stream bundle path changed")
    path = resolve_fixed(repo, path_text)
    rows = read_jsonl(path)
    inputs = package.get("candidate_event_stream_inputs") or []
    if len(rows) != 6432 or len(inputs) != 6432:
        raise GridExecutionError(
            "candidate stream bundle must contain exactly 6,432 rows"
        )
    expected_receipts = contract.get("candidate_stream_receipts") or {}
    event_ids = list((expected_receipts.get(FROZEN_CANDIDATES[0]) or {}))
    expected_pairs = [
        (candidate_id, event_id)
        for event_id in event_ids
        for candidate_id in FROZEN_CANDIDATES
    ]
    streams = {
        candidate_id: {} for candidate_id in FROZEN_CANDIDATES
    }
    container = next(
        (
            row for row in package.get("git_inputs") or []
            if row.get("role") == "frozen_candidate_event_stream_bundle"
        ),
        None,
    )
    if not isinstance(container, Mapping):
        raise GridExecutionError("candidate stream bundle receipt missing")
    for ordinal, (row, receipt, expected_pair) in enumerate(
        zip(rows, inputs, expected_pairs, strict=True), 1
    ):
        candidate_id = str(row.get("candidate_id") or "")
        event_id = str(row.get("event_id") or "")
        if (candidate_id, event_id) != expected_pair:
            raise GridExecutionError(
                "candidate stream rows missing, additional, duplicated, "
                "or reordered"
            )
        stream = row.get("stream")
        if not isinstance(stream, Mapping):
            raise GridExecutionError("candidate event stream object missing")
        line_bytes = (compact(row) + "\n").encode()
        expected_stream_sha = expected_receipts[candidate_id][event_id]
        if (
            receipt.get("ordinal") != ordinal
            or receipt.get("candidate_id") != candidate_id
            or receipt.get("event_id") != event_id
            or receipt.get("path") != f"{STREAM_BUNDLE_PATH}#L{ordinal}"
            or receipt.get("role")
            != "frozen_candidate_event_order_stream"
            or receipt.get("bytes") != len(line_bytes)
            or receipt.get("sha256") != sha256_bytes(line_bytes)
            or receipt.get("git_blob_oid") != container.get("git_blob_oid")
            or receipt.get("container_sha256") != container.get("sha256")
            or receipt.get("stream_sha256") != expected_stream_sha
            or stream.get("candidate_id") != candidate_id
            or stream.get("event_id") != event_id
            or stream.get("stream_sha256") != expected_stream_sha
            or canonical_sha256(stream.get("order_stream"))
            != expected_stream_sha
            or stream.get("scored") is not False
            or stream.get("metrics") is not None
            or stream.get("evaluation_truth_present") is not False
            or stream.get("holdout_queried") is not False
        ):
            raise GridExecutionError(
                f"candidate event stream input mismatch: "
                f"{candidate_id}:{event_id}"
            )
        streams[candidate_id][event_id] = dict(stream)
    assert_exact_candidate_order(list(streams))
    if any(len(value) != 804 for value in streams.values()):
        raise GridExecutionError("candidate stream event count changed")
    return streams


def validate_package(
    repo: Path,
    package_path: Path,
    *,
    require_result_absent: bool = True,
    mode: str = "execute",
) -> dict[str, Any]:
    package = read_json(package_path)
    if package.get("schema_version") != PACKAGE_SCHEMA:
        raise GridExecutionError("execution package schema changed")
    expected_hash = package.get("input_bundle_sha256")
    material = dict(package)
    material.pop("input_bundle_sha256", None)
    if canonical_sha256(material) != expected_hash:
        raise GridExecutionError("execution input-bundle hash changed")
    if (
        package.get("execution_id") != EXECUTION_ID
        or package.get("authorized_parent") != AUTHORIZED_PARENT
        or package.get("authorization_audit") != AUTHORIZED_AUDIT
        or package.get("exact_execution_command") != EXACT_EXECUTION_COMMAND
        or package.get("exact_validation_command") != EXACT_VALIDATION_COMMAND
        or package.get("result_directory") != RESULT_DIRECTORY
    ):
        raise GridExecutionError("execution identity/command contract changed")
    if package.get("controlling_identities") != {
        "round3_prerun": AUTHORIZED_PARENT,
        "round2_results": ROUND2_RESULTS,
        "round2_results_audit": {
            "commit": ROUND2_RESULTS_AUDIT,
            "report_path": ROUND2_AUDIT_REPORT_PATH,
            "report_blob_oid": ROUND2_AUDIT_REPORT_BLOB_OID,
        },
        "round3_prerun_audit": {
            "commit": ROUND3_PRERUN_AUDIT,
            "report_path": ROUND3_AUDIT_REPORT_PATH,
            "report_blob_oid": ROUND3_AUDIT_REPORT_BLOB_OID,
        },
    }:
        raise GridExecutionError("controlling identity/audit binding changed")
    assert_exact_candidate_order(package.get("candidate_ids") or [])
    if (
        package.get("D") != 804
        or package.get("target_PC") != 603
        or package.get("development_dates") != DEV_DATES
        or package.get("sealed_holdout_dates") != HOLDOUT_DATES
    ):
        raise GridExecutionError("denominator/date/target contract changed")
    if (
        package.get("expected_progress_sequence")
        != expected_progress_sequence()
        or package.get("expected_progress_sequence_sha256")
        != canonical_sha256(expected_progress_sequence())
        or package.get("expected_output_inventory")
        != expected_output_inventory()
        or package.get("expected_output_inventory_sha256")
        != canonical_sha256(expected_output_inventory())
    ):
        raise GridExecutionError("expected progress/output contract changed")
    branch = git(repo, "branch", "--show-current").decode().strip()
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    if mode == "execute":
        parent = git(repo, "rev-parse", "HEAD^").decode().strip()
        if (
            branch != "codex/window1-definition"
            or parent != AUTHORIZED_PARENT
        ):
            raise GridExecutionError(
                "execution must run from sole PRE-RUN child"
            )
        if unexpected_worktree_status(repo):
            raise GridExecutionError(
                "execution requires a clean worktree except retired grid1"
            )
        git_ref = "HEAD"
    elif mode == "validate-only":
        if branch not in ("", "codex/window1-definition"):
            raise GridExecutionError(
                "validation-only requires Codex branch or detached PRE-RUN"
            )
        if head == AUTHORIZED_PARENT:
            if git(repo, "diff", "--name-only").strip():
                raise GridExecutionError(
                    "validation-only refuses unstaged package changes"
                )
            git_ref = "INDEX"
        else:
            parent = git(repo, "rev-parse", "HEAD^").decode().strip()
            if parent != AUTHORIZED_PARENT:
                raise GridExecutionError(
                    "validation-only requires sole PRE-RUN child"
                )
            if unexpected_worktree_status(repo):
                raise GridExecutionError(
                    "committed validation-only requires clean worktree"
                )
            git_ref = "HEAD"
    else:
        raise GridExecutionError(f"unknown validation mode: {mode}")
    git_inputs = package.get("git_inputs") or []
    external_inputs = package.get("external_inputs") or []
    assert_exact_input_paths(
        [str(row.get("path") or "") for row in git_inputs],
        FROZEN_GIT_INPUT_PATHS,
        "Git",
    )
    assert_exact_input_paths(
        [str(row.get("path") or "") for row in external_inputs],
        FROZEN_EXTERNAL_INPUT_PATHS,
        "external",
    )
    if any(
        row.get("availability") != "available"
        or row.get("holdout_dates_present") != 0
        for row in external_inputs
    ):
        raise GridExecutionError("unavailable or holdout external input refused")
    for row in git_inputs:
        _verify_git_input(repo, row, git_ref=git_ref)
    source_receipts = package.get("frozen_source_receipts") or []
    if (
        len(source_receipts) != len({
            str(row.get("path") or "") for row in source_receipts
        })
        or canonical_sha256(source_receipts)
        != package.get("frozen_source_receipts_sha256")
    ):
        raise GridExecutionError("frozen source receipt set changed")
    for row in source_receipts:
        _verify_git_input(repo, row, git_ref=git_ref)
    for row in external_inputs:
        _verify_external_input(repo, row)
    cache_rows = package.get("market_cache_files") or []
    if len(cache_rows) != 804:
        raise GridExecutionError("market cache must contain exactly 804 receipts")
    cache_event_ids = [str(row.get("event_id") or "") for row in cache_rows]
    cache_dates = [str(row.get("event_date") or "") for row in cache_rows]
    if (
        len(set(cache_event_ids)) != 804
        or any(not value for value in cache_event_ids)
        or any(value in HOLDOUT_DATES for value in cache_dates)
        or set(cache_dates) - set(DEV_DATES)
        or any(
            row.get("availability") != "available"
            or row.get("holdout_dates_present") != 0
            for row in cache_rows
        )
    ):
        raise GridExecutionError(
            "missing, duplicated, outside-date, holdout, or unavailable "
            "market cache input refused"
        )
    for row in cache_rows:
        _verify_external_input(repo, row)
    contract = read_json(resolve_fixed(
        repo, str(package["roles"]["scorer_contract"])
    ))
    candidate_receipts = contract.get("candidate_stream_receipts") or {}
    if (
        len(candidate_receipts) != len(FROZEN_CANDIDATES)
        or set(candidate_receipts) != set(FROZEN_CANDIDATES)
    ):
        raise GridExecutionError(
            "missing, additional, or duplicated candidate receipt set"
        )
    if (
        sum(len(value) for value in candidate_receipts.values()) != 6432
        or canonical_sha256(candidate_receipts)
        != package.get("candidate_event_stream_receipts_sha256")
        or candidate_receipts
        != package.get("candidate_event_stream_receipts")
    ):
        raise GridExecutionError("6,432 candidate-event stream receipts changed")
    identities = contract.get("frozen_event_leg_identities") or []
    if (
        len(identities) != 1608
        or canonical_sha256(identities)
        != package.get("frozen_event_leg_identities_sha256")
        or identities != package.get("frozen_event_leg_identities")
    ):
        raise GridExecutionError("1,608 frozen leg identities changed")
    events = read_jsonl(resolve_fixed(
        repo, str(package["roles"]["event_ledger"])
    ))
    validate_dates(events)
    event_ids = {str(row["event_id"]) for row in events}
    if any(set(receipts) != event_ids for receipts in candidate_receipts.values()):
        raise GridExecutionError("stream receipt event set differs from D=804")
    candidate_streams = _load_frozen_stream_bundle(
        repo, package, contract
    )
    if require_result_absent:
        validate_result_directory_absent(repo, package)
    return {
        "package": package,
        "contract": contract,
        "events": events,
        "head": head,
        "branch": branch,
        "candidate_dispatch_order": list(FROZEN_CANDIDATES),
        "candidate_streams": candidate_streams,
        "input_bundle_sha256": expected_hash,
    }


def validation_only(repo: Path, package_path: Path) -> dict[str, Any]:
    validated = validate_package(
        repo, package_path, mode="validate-only"
    )
    package = validated["package"]
    return {
        "schema_version": VERSION + "-validation-only-v1",
        "mode": "validate-only",
        "execution_id": EXECUTION_ID,
        "authorized_parent": AUTHORIZED_PARENT,
        "authorization_audit": AUTHORIZED_AUDIT,
        "controlling_identities": package["controlling_identities"],
        "git_state_contract": (
            "authorized_parent_precommit_or_clean_sole_PRE_RUN_child"
        ),
        "input_bundle_sha256": validated["input_bundle_sha256"],
        "D": 804,
        "candidate_count": 8,
        "candidate_dispatch_order": validated["candidate_dispatch_order"],
        "dispatch_plan": [
            {
                "ordinal": index + 1,
                "candidate_id": candidate_id,
                "scorer_invocation_count_if_executed": 1,
            }
            for index, candidate_id in enumerate(FROZEN_CANDIDATES)
        ],
        "candidate_instrument_invocations": 0,
        "scorer_invocations": 0,
        "performance_results_produced": False,
        "result_directory_created": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
        "all_git_inputs_verified": len(package["git_inputs"]),
        "all_external_inputs_verified": len(package["external_inputs"]),
        "all_market_cache_files_verified": len(package["market_cache_files"]),
        "candidate_event_stream_receipts_verified": 6432,
        "candidate_event_streams_loaded": 6432,
        "leg_identities_verified": 1608,
        "gate_pass": True,
    }


def _load_cache(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise GridExecutionError(f"cache object required: {path}")
    return value


def _event_evidence(
    event: Mapping[str, Any],
    normalized: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for leg in normalized["legs"]:
        for row in leg["observations"]:
            if row["kind"] != "print":
                continue
            rows.append({
                "event_id": event["event_id"],
                "ticker": leg["ticker"],
                "ts": row["ts"],
                "price": row["price"],
                "size": row["size"],
                "taker_side": row["taker_side"],
                "trade_id": row["trade_id"],
                "receipt_id": row["receipt_id"],
                "source": row["source"],
                "size_verified": row["size_verified"],
                "synthetic_transition": row["synthetic_transition"],
            })
    rows.sort(key=lambda row: (
        float(row["ts"]), str(row["ticker"]), str(row["trade_id"])
    ))
    return rows


def _event_references(
    event: Mapping[str, Any],
    cache: Mapping[str, Any],
    boundary: Mapping[str, Any],
) -> dict[str, Any]:
    derived = scorer.strict_cutoff(boundary)
    if derived["status"] != "positive":
        return {}
    cutoff = float(derived["boundary_timestamp"])
    by_ticker = {str(row["ticker"]): row for row in cache["legs"]}
    output = {}
    for raw_leg in event["legs"]:
        ticker = str(raw_leg["ticker"])
        admitted = [
            row for row in by_ticker[ticker].get("prints") or []
            if float(row.get("ts") or 0) <= cutoff
            and float(row.get("size") or 0) > 0
            and str(row.get("trade_id") or "")
        ]
        admitted.sort(key=lambda row: (
            float(row["ts"]), str(row["trade_id"])
        ))
        if admitted:
            row = admitted[-1]
            output[ticker] = {
                "available": True,
                "window1_close_cents": float(row["price"]),
                "reference_ts": float(row["ts"]),
                "trade_id": str(row["trade_id"]),
                "source": "last_bound_positive_public_true_print_lte_guarded_cutoff",
                "guarded_cutoff_ts": cutoff,
            }
        else:
            output[ticker] = {
                "available": False,
                "window1_close_cents": None,
                "reason": "no_bound_positive_public_true_print_lte_guarded_cutoff",
                "guarded_cutoff_ts": cutoff,
            }
    return output


def _feature_classification(result: Mapping[str, Any]) -> dict[str, Any]:
    actions = result["order_stream"]
    missing = sorted({
        str(value)
        for row in actions if row["action"] == "feature_censor"
        for value in (row.get("missing_features") or [row["reason"]])
    })
    censored = result["event_terminal"] == "censored_feature"
    return {
        "censored": censored,
        "censor_reasons": (
            [f"required_feature:{value}" for value in missing]
            if censored else []
        ),
        "feature_unavailable": missing,
        "cohort_NO_CALL_count": sum(
            row["action"] == "cohort_no_call" for row in actions
        ),
        "reaim_NO_CALL_count": sum(
            row["action"] == "sibling_reaim_no_call" for row in actions
        ),
    }


def _canonical_receipts(
    sections: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        name: {
            "canonical_sha256": scorer.canonical_sha256(value),
            "source_sha256": contract["frozen_source_receipts"][name],
        }
        for name, value in sections.items()
    }


def _distribution(values: Iterable[float | None]) -> dict[str, Any]:
    ordered = sorted(float(value) for value in values if value is not None)
    if not ordered:
        return {
            "count": 0, "min": None, "p25": None, "median": None,
            "p75": None, "max": None, "mean": None,
        }

    def percentile(fraction: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        position = fraction * (len(ordered) - 1)
        lower = int(position)
        upper = min(lower + 1, len(ordered) - 1)
        weight = position - lower
        return ordered[lower] * (1 - weight) + ordered[upper] * weight

    return {
        "count": len(ordered),
        "min": ordered[0],
        "p25": percentile(0.25),
        "median": percentile(0.5),
        "p75": percentile(0.75),
        "max": ordered[-1],
        "mean": sum(ordered) / len(ordered),
    }


def _raw_for_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "events": len(rows),
        "C": sum(bool(row["C"]) for row in rows),
        "PC": sum(bool(row["PC"]) for row in rows),
        "S": sum(bool(row["S"]) for row in rows),
        "IC": sum(bool(row["IC"]) for row in rows),
        **{
            key: sum(row["classification"] == key for row in rows)
            for key in PRIMARY_CENSUS
        },
    }


def _breakdown(
    rows: Sequence[Mapping[str, Any]],
    event_meta: Mapping[str, Mapping[str, Any]],
    key_fn: Callable[[Mapping[str, Any], Mapping[str, Any]], str],
) -> list[dict[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        meta = event_meta[str(row["event_id"])]
        key = key_fn(row, meta)
        groups.setdefault(key, []).append(row)
    return [
        {"group": key, **_raw_for_rows(groups[key])}
        for key in sorted(groups)
    ]


def _candidate_summary(
    result: Mapping[str, Any],
    event_meta: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    rows = result["event_results"]
    raw = dict(result["raw_integer_metrics_before_percentages"])
    raw["target_PC"] = 603
    raw["distance_from_603"] = 603 - int(raw["PC"])
    completed = [row for row in rows if row["C"]]
    leg_deltas = [
        delta
        for row in completed
        for delta in (
            row["individual_leg_window1_close_delta_cents"] or []
        )
    ]
    summary = {
        "candidate_id": result["candidate_id"],
        "raw_integers_before_percentages": raw,
        "rates": {
            **result["rates_after_raw_integers"],
            "S_over_D": raw["S"] / 804,
        },
        "distributions": {
            "combined_entry_cost_cents": _distribution(
                row["combined_entry_cost_cents"] for row in completed
            ),
            "combined_window1_close_delta_cents": _distribution(
                row["combined_window1_close_delta_cents"]
                for row in completed
            ),
            "individual_leg_window1_close_delta_cents": _distribution(
                leg_deltas
            ),
            "leg_A_window1_close_delta_cents": _distribution(
                (
                    row["individual_leg_window1_close_delta_cents"] or
                    [None, None]
                )[0] for row in completed
            ),
            "leg_B_window1_close_delta_cents": _distribution(
                (
                    row["individual_leg_window1_close_delta_cents"] or
                    [None, None]
                )[1] for row in completed
            ),
        },
        "breakdowns": {
            "utc_date": _breakdown(
                rows, event_meta,
                lambda row, meta: str(row["event_date"]),
            ),
            "tournament_class": _breakdown(
                rows, event_meta,
                lambda row, meta: str(meta["category"]),
            ),
            "start_source_class": _breakdown(
                rows, event_meta,
                lambda row, meta: str(meta["start_source_class"]),
            ),
            "policy_boundary_class": _breakdown(
                rows, event_meta,
                lambda row, meta: str(meta["policy_boundary_class"]),
            ),
        },
        "result_sha256": result["result_sha256"],
    }
    if sum(raw[key] for key in PRIMARY_CENSUS) != 804:
        raise GridExecutionError(
            f"classification conservation failed: {result['candidate_id']}"
        )
    return summary


def _base_reaim_comparison(
    results: Mapping[str, Mapping[str, Any]],
    package: Mapping[str, Any],
) -> dict[str, Any]:
    changed = package["base_reaim_changed_order_event_ids"]
    rows = []
    for base_id, reaim_id in FROZEN_PAIRS:
        base = {
            str(row["event_id"]): row
            for row in results[base_id]["event_results"]
        }
        reaim = {
            str(row["event_id"]): row
            for row in results[reaim_id]["event_results"]
        }
        event_ids = sorted(base)
        dual_gained = [
            event_id for event_id in event_ids
            if not base[event_id]["C"] and reaim[event_id]["C"]
        ]
        dual_lost = [
            event_id for event_id in event_ids
            if base[event_id]["C"] and not reaim[event_id]["C"]
        ]
        single_to_dual = [
            event_id for event_id in event_ids
            if base[event_id]["classification"] == "naked_single_leg"
            and reaim[event_id]["C"]
        ]
        paired_duals = [
            event_id for event_id in event_ids
            if base[event_id]["C"] and reaim[event_id]["C"]
        ]
        cost_changes = [
            reaim[event_id]["combined_entry_cost_cents"]
            - base[event_id]["combined_entry_cost_cents"]
            for event_id in paired_duals
        ]
        delta_changes = [
            reaim[event_id]["combined_window1_close_delta_cents"]
            - base[event_id]["combined_window1_close_delta_cents"]
            for event_id in paired_duals
        ]
        changes = {
            metric: sum(bool(reaim[event_id][metric]) for event_id in event_ids)
            - sum(bool(base[event_id][metric]) for event_id in event_ids)
            for metric in ("C", "PC", "S", "IC")
        }
        completion_improved = changes["C"] > 0
        quality_improved = (
            changes["PC"] > 0
            or changes["IC"] > 0
            or (
                delta_changes
                and sum(delta_changes) / len(delta_changes) < 0
            )
        )
        rows.append({
            "base_candidate_id": base_id,
            "reaim_candidate_id": reaim_id,
            "changed_order_event_count": len(changed[reaim_id]),
            "changed_order_event_ids": changed[reaim_id],
            "metric_changes_reaim_minus_base": changes,
            "fills_gained_dual_completion": len(dual_gained),
            "fills_gained_event_ids": dual_gained,
            "fills_lost_dual_completion": len(dual_lost),
            "fills_lost_event_ids": dual_lost,
            "singles_converted_to_duals": len(single_to_dual),
            "single_to_dual_event_ids": single_to_dual,
            "duals_lost": len(dual_lost),
            "paired_dual_count": len(paired_duals),
            "combined_cost_change_cents": _distribution(cost_changes),
            "combined_delta_change_cents": _distribution(delta_changes),
            "improvement_class": (
                "both" if completion_improved and quality_improved
                else "completion" if completion_improved
                else "quality" if quality_improved
                else "neither"
            ),
        })
    return {
        "schema_version": VERSION + "-base-reaim-v1",
        "pairs": rows,
        "ranking_or_selection_applied": False,
    }


def _render_report(
    summaries: Sequence[Mapping[str, Any]],
    comparisons: Mapping[str, Any],
) -> str:
    lines = [
        "# Window-1 Round-2 development benchmark",
        "",
        "Development result for the frozen eight-candidate Round-2 family.",
        "This is not a market ceiling and does not generalize to all OS policies.",
        "",
        "| candidate | D | C | PC | S | IC | target | distance | conservation |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        raw = summary["raw_integers_before_percentages"]
        conservation = sum(raw[key] for key in PRIMARY_CENSUS)
        lines.append(
            f"| {summary['candidate_id']} | {raw['D']} | {raw['C']} | "
            f"{raw['PC']} | {raw['S']} | {raw['IC']} | 603 | "
            f"{raw['distance_from_603']} | {conservation} |"
        )
    lines.extend([
        "",
        "No frozen selection or ranking rule exists; candidates remain unranked.",
        "S and IC are reported separately and are not substitutes for PC.",
        "",
        "Unavailable machinery remains unavailable: Pinnacle, proved full depth,",
        "and lawful independent shape mapping were not inferred.",
        "",
        "Base/reaim comparisons are in `BASE_REAIM_COMPARISON.json`.",
        "The event ledgers and all breakdown tables are machine-readable artifacts.",
        "",
    ])
    return "\n".join(lines)


def _write_output_hashes(result_dir: Path) -> dict[str, Any]:
    rows = {}
    for path in sorted(result_dir.iterdir()):
        if (
            not path.is_file()
            or path.name == "OUTPUT_HASH_MANIFEST.json"
        ):
            continue
        rows[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    value = {
        "schema_version": VERSION + "-output-hashes-v1",
        "execution_id": EXECUTION_ID,
        "outputs": rows,
    }
    write_json(result_dir / "OUTPUT_HASH_MANIFEST.json", value)
    return value


def _runtime_versions() -> dict[str, Any]:
    return {
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
    }


def execute_grid(repo: Path, package_path: Path) -> int:
    validated = validate_package(repo, package_path, mode="execute")
    package = validated["package"]
    contract = validated["contract"]
    result_dir = validate_result_directory_absent(repo, package)
    result_dir.mkdir(parents=True, exist_ok=False)
    started = dt.datetime.now(dt.timezone.utc)
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    console = ConsoleEchoGuard()
    emit = ProgressEmitter(
        result_dir / "PROGRESS.log", stdout_lines, console
    )

    start_receipt = {
        "schema_version": VERSION + "-start-v1",
        "execution_id": EXECUTION_ID,
        "exact_command": EXACT_EXECUTION_COMMAND,
        "git_sha": validated["head"],
        "authorized_parent": AUTHORIZED_PARENT,
        "authorization_audit": AUTHORIZED_AUDIT,
        "controlling_identities": package["controlling_identities"],
        "started_at_utc": started.isoformat(),
        "runtime_versions": _runtime_versions(),
        "input_bundle_sha256": package["input_bundle_sha256"],
        "scorer_source_sha256": package["scorer_source_sha256"],
        "scorer_contract_sha256": package["scorer_contract_sha256"],
        "candidate_dispatch_order": list(FROZEN_CANDIDATES),
        "candidate_scorer_invocations_completed": 0,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
    }
    write_json(result_dir / "EXECUTION_START_RECEIPT.json", start_receipt)
    try:
        emit(f"execution_id={EXECUTION_ID}")
        emit(f"git_sha={validated['head']}")
        roles = package["roles"]
        events = validated["events"]
        starts = {
            str(row["event_id"]): row
            for row in read_jsonl(resolve_fixed(
                repo, str(roles["start_ledger"])
            ))
        }
        if set(starts) != {str(row["event_id"]) for row in events}:
            raise GridExecutionError("start ledger event set changed")
        features = [
            row for row in read_jsonl(resolve_fixed(
                repo, str(roles["leg_ledger"])
            ))
            if int(row["boundary_hours_before_schedule"]) == 8
        ]
        feature_map = {
            (str(row["event_id"]), str(row["ticker"])): row
            for row in features
        }
        if len(feature_map) != 1608:
            raise GridExecutionError("T8 leg feature identity count changed")
        spec = read_json(resolve_fixed(
            repo, str(roles["candidate_definitions"])
        ))
        assert_exact_candidate_order(spec["candidate_ids"])
        corridor = float(
            spec["common_parameters"][
                "policy_corridor_seconds_after_anchor"
            ]
        )
        cache_root = resolve_fixed(
            repo, str(roles["market_cache_directory"])
        )
        normalized_events: dict[str, dict[str, Any]] = {}
        caches: dict[str, dict[str, Any]] = {}
        evidence: dict[str, list[dict[str, Any]]] = {}
        references: dict[str, dict[str, Any]] = {}
        event_meta: dict[str, dict[str, Any]] = {}
        for event in events:
            event_id = str(event["event_id"])
            cache = _load_cache(cache_root / f"{event_id}.json.gz")
            normalized = capability.normalize_event(
                event, cache, feature_map,
                corridor_seconds=corridor,
            )
            normalized_events[event_id] = normalized
            caches[event_id] = cache
            evidence[event_id] = _event_evidence(event, normalized)
            references[event_id] = _event_references(
                event, cache, starts[event_id]
            )
            boundary = scorer.strict_cutoff(starts[event_id])
            event_meta[event_id] = {
                "event_date": event["event_date"],
                "category": event["category"],
                "start_source_class": starts[event_id][
                    "start_source_class"
                ],
                "policy_boundary_class": (
                    "zero_length"
                    if (
                        boundary["status"] == "positive"
                        and float(boundary["boundary_timestamp"])
                        <= max(
                            float(normalized["policy_left_ts"]),
                            float(
                                normalized[
                                    "policy_anchor_observed_at_ts"
                                ]
                            ),
                        )
                    )
                    else boundary["status"]
                ),
            }
        data_manifest = read_json(resolve_fixed(
            repo, str(roles["data_binding_manifest"])
        ))
        results: dict[str, dict[str, Any]] = {}
        summaries = []
        dispatcher = FrozenScorerDispatcher()
        frozen_streams = validated["candidate_streams"]
        for ordinal, candidate_id in enumerate(FROZEN_CANDIDATES, 1):
            emit(f"candidate_start={ordinal}:{candidate_id}")
            streams: dict[str, dict[str, Any]] = {}
            classifications: dict[str, dict[str, Any]] = {}
            for event in events:
                event_id = str(event["event_id"])
                stream = frozen_streams[candidate_id][event_id]
                expected = package[
                    "candidate_event_stream_receipts"
                ][candidate_id][event_id]
                if stream["stream_sha256"] != expected:
                    raise GridExecutionError(
                        "candidate-event stream mismatch: "
                        f"{candidate_id}:{event_id}"
                    )
                streams[event_id] = stream
                classifications[event_id] = _feature_classification(stream)
            sections = {
                "event_ledger": events,
                "candidate_order_streams": streams,
                "fill_evidence": evidence,
                "start_boundaries": starts,
                "references": references,
                "feature_classifications": classifications,
                "data_binding_manifest": data_manifest,
            }
            bundle = {
                "candidate_id": candidate_id,
                "freeze_lineage": contract["freeze_lineage"],
                "source_receipts": contract["frozen_source_receipts"],
                "sections": sections,
                "section_receipts": _canonical_receipts(
                    sections, contract
                ),
            }
            # Exactly one frozen scorer invocation for this candidate.
            result = dispatcher.invoke(candidate_id, bundle, contract)
            results[candidate_id] = result
            write_jsonl(
                result_dir / f"{ordinal:02d}_{candidate_id}_EVENT_LEDGER.jsonl",
                result["event_results"],
            )
            summaries.append(_candidate_summary(result, event_meta))
            start_receipt["candidate_scorer_invocations_completed"] = ordinal
            write_json(
                result_dir / "EXECUTION_START_RECEIPT.json",
                start_receipt,
            )
            emit(f"candidate_complete={ordinal}:{candidate_id}")
        dispatcher.assert_complete()
        comparison = _base_reaim_comparison(results, package)
        all_results = {
            "schema_version": VERSION + "-eight-candidate-results-v1",
            "execution_id": EXECUTION_ID,
            "D": 804,
            "target_PC": 603,
            "candidate_order": list(FROZEN_CANDIDATES),
            "candidate_results": summaries,
            "selection_status": (
                "UNRANKED_FROZEN_SELECTION_RULE_ABSENT"
            ),
            "selected_candidate_receipt_emitted": False,
            "development_result_only": True,
            "market_ceiling_claimed": False,
            "all_possible_OS_policies_claimed": False,
        }
        write_json(
            result_dir / "EIGHT_CANDIDATE_RESULTS.json",
            all_results,
        )
        conservation = {
            "schema_version": VERSION + "-conservation-v1",
            "execution_id": EXECUTION_ID,
            "candidate_rows": [
                {
                    "candidate_id": row["candidate_id"],
                    "D": 804,
                    "classification_total": sum(
                        row["raw_integers_before_percentages"][key]
                        for key in PRIMARY_CENSUS
                    ),
                    "gate_pass": sum(
                        row["raw_integers_before_percentages"][key]
                        for key in PRIMARY_CENSUS
                    ) == 804,
                }
                for row in summaries
            ],
            "all_candidates_conserve_to_D804": True,
        }
        if not all(row["gate_pass"] for row in conservation["candidate_rows"]):
            raise GridExecutionError("candidate conservation failure")
        write_json(
            result_dir / "METRIC_CONSERVATION_REPORT.json",
            conservation,
        )
        write_json(
            result_dir / "BASE_REAIM_COMPARISON.json",
            comparison,
        )
        emit("final_receipt_publication_started")
        (result_dir / "WINDOW1_ROUND3_DEVELOPMENT_REPORT.md").write_text(
            _render_report(summaries, comparison),
            encoding="utf-8",
            newline="\n",
        )
        nonaccess = {
            "schema_version": VERSION + "-nonaccess-v1",
            "execution_id": EXECUTION_ID,
            "development_dates_only": DEV_DATES,
            "sealed_holdout_dates": HOLDOUT_DATES,
            "input_manifest_holdout_rows": 0,
            "holdout_paths_opened": [],
            "holdout_opened": False,
            "holdout_queried": False,
            "network_calls": 0,
            "live_exchange_calls": 0,
            "production_paths_written": [],
            "live_v4_paths_written": [],
            "configuration_paths_written": [],
            "orders_positions_window2_exits_settlement_DCA_written": [],
            "only_result_directory_written": RESULT_DIRECTORY,
            "gate_pass": True,
        }
        write_json(
            result_dir / "HOLDOUT_NONPRODUCTION_NONACCESS_PROOF.json",
            nonaccess,
        )
        emit("output_hash_manifest_pending")
        ended = dt.datetime.now(dt.timezone.utc)
        stdout_text = "\n".join(stdout_lines) + "\n"
        (result_dir / "STDOUT.log").write_text(
            stdout_text, encoding="utf-8", newline="\n"
        )
        (result_dir / "STDERR.log").write_text(
            "", encoding="utf-8", newline="\n"
        )
        execution_manifest = {
            "schema_version": VERSION + "-execution-v1",
            "execution_id": EXECUTION_ID,
            "exact_command": EXACT_EXECUTION_COMMAND,
            "git_sha": validated["head"],
            "authorized_parent": AUTHORIZED_PARENT,
            "authorization_audit": AUTHORIZED_AUDIT,
            "controlling_identities": package["controlling_identities"],
            "started_at_utc": started.isoformat(),
            "ended_at_utc": ended.isoformat(),
            "exit_code": 0,
            "runtime_versions": _runtime_versions(),
            "input_bundle_sha256": package["input_bundle_sha256"],
            "scorer_source_sha256": package["scorer_source_sha256"],
            "scorer_contract_sha256": package["scorer_contract_sha256"],
            "candidate_dispatch_order": list(FROZEN_CANDIDATES),
            "scorer_invocations": {
                candidate_id: dispatcher.counts[candidate_id]
                for candidate_id in FROZEN_CANDIDATES
            },
            "total_scorer_invocations": 8,
            "stdout_sha256": sha256_bytes(stdout_text.encode()),
            "stderr_sha256": sha256_bytes(b""),
            "selection_status": (
                "UNRANKED_FROZEN_SELECTION_RULE_ABSENT"
            ),
            "authoritative_progress_path": "PROGRESS.log",
            "console_echo": console.receipt(),
            "holdout_opened": False,
            "holdout_queried": False,
            "live_or_production_access": False,
        }
        write_json(
            result_dir / "EXECUTION_MANIFEST.json",
            execution_manifest,
        )
        _write_output_hashes(result_dir)
        actual_outputs = sorted(
            path.name for path in result_dir.iterdir() if path.is_file()
        )
        if actual_outputs != expected_output_inventory():
            raise GridExecutionError(
                "final output inventory differs from frozen contract"
            )
        return 0
    except Exception as exc:
        ended = dt.datetime.now(dt.timezone.utc)
        message = f"{type(exc).__name__}: {exc}"
        stderr_lines.extend([message, traceback.format_exc()])
        (result_dir / "STDOUT.log").write_text(
            "\n".join(stdout_lines) + ("\n" if stdout_lines else ""),
            encoding="utf-8",
            newline="\n",
        )
        (result_dir / "STDERR.log").write_text(
            "\n".join(stderr_lines) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        write_json(result_dir / "EXECUTION_FAILURE.json", {
            "schema_version": VERSION + "-failure-v1",
            "execution_id": EXECUTION_ID,
            "exact_command": EXACT_EXECUTION_COMMAND,
            "git_sha": validated["head"],
            "started_at_utc": started.isoformat(),
            "ended_at_utc": ended.isoformat(),
            "exit_code": 1,
            "error": message,
            "retry_permitted": False,
            "partial_log_preserved": True,
            "authoritative_progress_path": "PROGRESS.log",
            "console_echo": console.receipt(),
            "controlling_identities": package["controlling_identities"],
            "holdout_opened": False,
            "holdout_queried": False,
            "live_or_production_access": False,
        })
        _write_output_hashes(result_dir)
        console.echo_stderr(message)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument(
        "--mode", choices=("validate-only", "execute"), required=True
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    package_path = (
        args.package.resolve()
        if args.package.is_absolute()
        else (repo / args.package).resolve()
    )
    if args.mode == "validate-only":
        value = validation_only(repo, package_path)
        receipt_path = resolve_fixed(repo, VALIDATION_RECEIPT_PATH)
        if receipt_path.exists():
            if read_json(receipt_path) != value:
                raise GridExecutionError(
                    "validation-only receipt differs from frozen replay"
                )
        else:
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            write_json(receipt_path, value)
        ConsoleEchoGuard().echo_stdout(
            json.dumps(value, indent=2, sort_keys=True)
        )
        return 0
    return execute_grid(repo, package_path)


if __name__ == "__main__":
    raise SystemExit(main())
