#!/usr/bin/env python3
"""Build and freeze the additions-only Round-3 execution package.

This utility never invokes the scorer or a candidate instrument.  It binds the
already committed Round-3 order streams and the unchanged Round-2 scorer and
metric law into a deterministic one-shot execution package.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

import window1_round3_grid_runner as runner


VERSION = "window1-round3-execution-packager-v1"
PARENT = "14e0e846e8922da98f656aef1f43d2c48da96ee7"
ROUND2_RESULTS = "10ac6dbc68d65cb21ab3718e118ff34d7220ad87"
ROUND2_AUDIT = "807e2c865c3cf7384757c54a3b879518568dec4f"
ROUND3_AUDIT = "b415a98e2430642242f8e0205fb9b5edfee841b5"
ROUND2_AUDIT_REPORT = (
    ".claude/audit_20260725_grid2_results/AUDIT_REPORT.md"
)
ROUND2_AUDIT_BLOB = "9bb51a3dc19fd055156ee958a6f208b1a725cbc4"
ROUND3_AUDIT_REPORT = (
    ".claude/audit_20260725_round3_prerun/AUDIT_REPORT.md"
)
ROUND3_AUDIT_BLOB = "e4b32d218f3e4e1feeb3043ff4f4b3ba36033ac0"

OUTPUT = Path(".claude/window1_round3_execution_package_20260725")
BUNDLE = OUTPUT / "SCORING_INPUT_BUNDLE.json"
CONTRACT = OUTPUT / "SCORER_FREEZE_CONTRACT.json"
VALIDATION = OUTPUT / "VALIDATION_ONLY_RECEIPT.json"
EXPECTED_PROGRESS = OUTPUT / "EXPECTED_PROGRESS_SEQUENCE.json"
EXPECTED_OUTPUTS = OUTPUT / "EXPECTED_OUTPUT_INVENTORY.json"
TEST_RECEIPT = OUTPUT / "PACKAGING_TEST_RECEIPT.json"
REFUSAL_RECEIPT = OUTPUT / "REFUSAL_FIXTURE_RESULTS.json"
MANIFEST = OUTPUT / "PRE_RUN_MANIFEST.json"
REPORT = OUTPUT / "PRE_RUN_REPORT.md"
ARTIFACTS = OUTPUT / "ARTIFACT_MANIFEST.json"

R3_MANIFEST = Path(
    ".claude/window1_round3_prerun_20260725/ROUND3_PRE_RUN_MANIFEST.json"
)
R3_STREAMS = Path(
    ".claude/window1_round3_prerun_20260725/"
    "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
)
R3_CAPABILITY = Path(
    ".claude/window1_round3_prerun_20260725/ROUND3_REAL_CAPABILITY.json"
)
R3_REAIM = Path(
    ".claude/window1_round3_prerun_20260725/"
    "ROUND3_REAIM_ORDER_DIFFERENCES.jsonl"
)
R2_CONTRACT = Path(
    ".claude/window1_round2_final_prerun_20260724/"
    "SCORER_FREEZE_CONTRACT.json"
)
DATA_MANIFEST = Path(
    ".claude/window1_round2_prerun_v2_20260724/"
    "ROUND2_DATA_BINDING_MANIFEST.json"
)
RUNNER_SOURCE = Path(
    "arb-executor/analysis/window1_round3_grid_runner.py"
)
PACKAGER_SOURCE = Path(
    "arb-executor/analysis/window1_round3_execution_packager.py"
)
RUNNER_TEST = Path(
    "arb-executor/tests/test_window1_round3_grid_runner.py"
)
STDOUT_TEST = Path(
    "arb-executor/tests/test_window1_round3_stdout_safe.py"
)


class PackagingError(RuntimeError):
    """Raised when an exact package invariant fails."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PackagingError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    opener = (
        gzip.open(path, "rt", encoding="utf-8")
        if path.suffix == ".gz"
        else path.open(encoding="utf-8")
    )
    with opener as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    if not all(isinstance(row, dict) for row in rows):
        raise PackagingError(f"JSONL objects required: {path}")
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def path_text(path: Path) -> str:
    return str(path).replace("\\", "/")


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise PackagingError(
            f"git {' '.join(args)} failed: "
            + result.stderr.decode(errors="replace").strip()
        )
    return result.stdout


def commit_blob(repo: Path, commit: str, path: str) -> str:
    return git(repo, "rev-parse", f"{commit}:{path}").decode().strip()


def verify_lineage_and_audits(repo: Path) -> None:
    identities = {
        PARENT: PARENT,
        ROUND2_RESULTS: ROUND2_RESULTS,
        ROUND2_AUDIT: ROUND2_AUDIT,
        ROUND3_AUDIT: ROUND3_AUDIT,
    }
    for reference, expected in identities.items():
        actual = git(
            repo, "rev-parse", f"{reference}^{{commit}}"
        ).decode().strip()
        if actual != expected:
            raise PackagingError(f"commit identity mismatch: {reference}")
    parent = git(repo, "rev-parse", f"{PARENT}^").decode().strip()
    if parent != ROUND2_RESULTS:
        raise PackagingError("Round-3 PRE-RUN exact parent changed")
    if (
        commit_blob(repo, ROUND2_AUDIT, ROUND2_AUDIT_REPORT)
        != ROUND2_AUDIT_BLOB
        or commit_blob(repo, ROUND3_AUDIT, ROUND3_AUDIT_REPORT)
        != ROUND3_AUDIT_BLOB
    ):
        raise PackagingError("audit report commit/blob binding changed")


def receipt_from_ref(
    repo: Path, path: str, role: str, *, ref: str = "HEAD",
) -> dict[str, Any]:
    oid = git(repo, "rev-parse", f"{ref}:{path}").decode().strip()
    data = git(repo, "cat-file", "blob", oid)
    return {
        "path": path,
        "role": role,
        "bytes": len(data),
        "git_blob_oid": oid,
        "sha256": sha256_bytes(data),
        "availability": "available",
    }


def receipt_from_worktree(
    repo: Path, path: Path, role: str,
) -> dict[str, Any]:
    relative = path_text(path)
    oid = git(
        repo, "hash-object", "-w", f"--path={relative}", relative
    ).decode().strip()
    data = git(repo, "cat-file", "blob", oid)
    return {
        "path": relative,
        "role": role,
        "bytes": len(data),
        "git_blob_oid": oid,
        "sha256": sha256_bytes(data),
        "availability": "available",
    }


def receipt_from_index(
    repo: Path, path: Path, role: str,
) -> dict[str, Any]:
    relative = path_text(path)
    oid = git(repo, "rev-parse", f":{relative}").decode().strip()
    data = git(repo, "cat-file", "blob", oid)
    working_oid = git(
        repo, "hash-object", f"--path={relative}", relative
    ).decode().strip()
    if working_oid != oid:
        raise PackagingError(f"unstaged change: {relative}")
    return {
        "path": relative,
        "role": role,
        "bytes": len(data),
        "git_blob_oid": oid,
        "sha256": sha256_bytes(data),
        "availability": "available",
    }


def external_receipt(
    record: Mapping[str, Any], *, path: str, role: str,
) -> dict[str, Any]:
    return {
        "path": path,
        "role": role,
        "bytes": int(record["bytes"]),
        "git_blob_oid": None,
        "sha256": str(record["content_sha256"]),
        "availability": str(record["availability"]),
        "date_range": record.get("date_range"),
        "holdout_dates_present": int(record["holdout_dates_present"]),
    }


def round3_receipts(
    manifest: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    by_candidate: dict[str, dict[str, str]] = {
        candidate_id: {} for candidate_id in runner.FROZEN_CANDIDATES
    }
    for row in manifest["candidate_event_stream_receipts"]:
        candidate_id = str(row["candidate_id"])
        if candidate_id not in by_candidate:
            raise PackagingError("unknown Round-3 stream candidate")
        by_candidate[candidate_id][str(row["event_id"])] = str(
            row["stream_sha256"]
        )
    if [*by_candidate] != runner.FROZEN_CANDIDATES:
        raise PackagingError("Round-3 candidate order changed")
    if any(len(rows) != 804 for rows in by_candidate.values()):
        raise PackagingError("Round-3 stream receipt count changed")
    return by_candidate, canonical_sha256(by_candidate)


def build_scorer_contract(repo: Path) -> dict[str, Any]:
    """Rebind unchanged scorer law to committed Round-3 inputs."""
    base = read_json(repo / R2_CONTRACT)
    r3 = read_json(repo / R3_MANIFEST)
    receipts, receipts_hash = round3_receipts(r3)
    spec_sha = next(
        row["sha256"]
        for row in r3["source_and_contract_receipts"]
        if row["path"].endswith("WINDOW1_ROUND3_CANDIDATES_V1.json")
    )
    instrument_sha = next(
        row["sha256"]
        for row in r3["source_and_contract_receipts"]
        if row["path"].endswith("window1_round3_instrument.py")
    )
    contract = dict(base)
    contract["candidate_ids"] = list(runner.FROZEN_CANDIDATES)
    contract["candidate_stream_receipts"] = receipts
    contract["candidate_stream_receipts_sha256"] = receipts_hash
    contract["freeze_lineage"] = {
        **base["freeze_lineage"],
        "candidate_spec": spec_sha,
        "instrument": instrument_sha,
        "round3_prerun": PARENT,
        "round3_stream_bundle": (
            "db61cb7a70326d991a5e8a89cae21920e7d0ed594b0e7ae5ad540184461ced96"
        ),
        "round2_results": ROUND2_RESULTS,
        "round2_results_audit": ROUND2_AUDIT,
        "round3_prerun_audit": ROUND3_AUDIT,
    }
    contract["frozen_source_receipts"] = {
        **base["frozen_source_receipts"],
        "candidate_order_streams": (
            "db61cb7a70326d991a5e8a89cae21920e7d0ed594b0e7ae5ad540184461ced96"
        ),
        "feature_classifications": (
            "496e44421f3158f920f7e094a47d6dc64ef621347a586f2dc9877ae68ed05547"
        ),
    }
    contract["candidate_stream_contract"] = {
        "source": path_text(R3_STREAMS),
        "candidate_count": 8,
        "events_per_candidate": 804,
        "stream_count": 6432,
        "ordering": "event-ledger order then frozen candidate order",
        "policy_regeneration_permitted": False,
        "scorer_invocations_during_packaging": 0,
    }
    contract["candidate_scoring_performed"] = False
    contract["tuning_performed"] = False
    contract["performance_ablation_performed"] = False
    contract["holdout_opened"] = False
    contract["holdout_queried"] = False
    return contract


def frozen_source_receipts(
    repo: Path, manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    paths: dict[str, str] = {}
    for field, role in (
        ("artifact_receipts", "round3_frozen_artifact"),
        ("source_and_contract_receipts", "round3_frozen_source_or_contract"),
        ("bound_git_data_receipts", "round3_frozen_data_surface"),
    ):
        for row in manifest[field]:
            paths[str(row["path"])] = role
    paths[path_text(R3_MANIFEST)] = "round3_prerun_manifest"
    rows = [
        receipt_from_ref(repo, path, role)
        for path, role in sorted(paths.items())
    ]
    return rows


def runtime_git_receipts(repo: Path) -> list[dict[str, Any]]:
    roles = {
        runner.STREAM_BUNDLE_PATH: "frozen_candidate_event_stream_bundle",
        path_text(CONTRACT): "frozen_scorer_contract",
        path_text(RUNNER_SOURCE): "deterministic_grid_runner",
        "arb-executor/analysis/window1_round3_instrument.py": (
            "frozen_round3_candidate_instrument"
        ),
        "arb-executor/analysis/window1_round2_scorer.py": "frozen_scorer",
        "arb-executor/analysis/window1_round2_real_capability.py": (
            "frozen_normalization_adapter"
        ),
        "arb-executor/analysis/window1_round2_data_binding.py": (
            "frozen_input_validator"
        ),
        path_text(DATA_MANIFEST): "immutable_data_binding_manifest",
        ".claude/window1_start_guard_corrected_20260724/"
        "REAL_START_LEDGER_V5.jsonl": "frozen_start_boundary_ledger",
        ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl": (
            "frozen_leg_identity_and_feature_ledger"
        ),
    }
    worktree_paths = {path_text(RUNNER_SOURCE), path_text(CONTRACT)}
    rows = []
    for path in runner.FROZEN_GIT_INPUT_PATHS:
        role = roles.get(path, "frozen_policy_surface_or_contract")
        rows.append(
            receipt_from_worktree(repo, Path(path), role)
            if path in worktree_paths
            else receipt_from_ref(repo, path, role)
        )
    return rows


def stream_inputs(
    repo: Path,
    contract: Mapping[str, Any],
    container: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows = read_jsonl(repo / R3_STREAMS)
    if len(rows) != 6432:
        raise PackagingError("Round-3 stream bundle is not 6,432 rows")
    event_ids = list(
        contract["candidate_stream_receipts"][
            runner.FROZEN_CANDIDATES[0]
        ]
    )
    expected = [
        (candidate_id, event_id)
        for event_id in event_ids
        for candidate_id in runner.FROZEN_CANDIDATES
    ]
    output = []
    for ordinal, (row, pair) in enumerate(
        zip(rows, expected, strict=True), 1
    ):
        candidate_id = str(row.get("candidate_id") or "")
        event_id = str(row.get("event_id") or "")
        stream = row.get("stream")
        line = (compact(row) + "\n").encode()
        expected_sha = contract["candidate_stream_receipts"][
            candidate_id
        ][event_id]
        if (
            (candidate_id, event_id) != pair
            or not isinstance(stream, Mapping)
            or stream.get("stream_sha256") != expected_sha
            or canonical_sha256(stream.get("order_stream")) != expected_sha
            or stream.get("scored") is not False
            or stream.get("metrics") is not None
            or stream.get("evaluation_truth_present") is not False
            or stream.get("holdout_queried") is not False
        ):
            raise PackagingError(
                f"frozen stream mismatch: {candidate_id}:{event_id}"
            )
        output.append({
            "ordinal": ordinal,
            "candidate_id": candidate_id,
            "event_id": event_id,
            "path": f"{path_text(R3_STREAMS)}#L{ordinal}",
            "role": "frozen_candidate_event_order_stream",
            "bytes": len(line),
            "git_blob_oid": container["git_blob_oid"],
            "sha256": sha256_bytes(line),
            "container_sha256": container["sha256"],
            "stream_sha256": expected_sha,
            "availability": "available",
        })
    return output


def build_package(repo: Path) -> dict[str, Any]:
    if git(repo, "rev-parse", "HEAD").decode().strip() != PARENT:
        raise PackagingError("prepare requires exact Round-3 PRE-RUN")
    verify_lineage_and_audits(repo)
    if (repo / runner.RESULT_DIRECTORY).exists():
        raise PackagingError("new execution result directory already exists")
    contract = read_json(repo / CONTRACT)
    r3_manifest = read_json(repo / R3_MANIFEST)
    capability = read_json(repo / R3_CAPABILITY)
    if (
        contract["candidate_ids"] != runner.FROZEN_CANDIDATES
        or capability["candidate_ids"] != runner.FROZEN_CANDIDATES
        or contract["D"] != 804
        or len(contract["frozen_event_leg_identities"]) != 1608
        or sum(
            len(value)
            for value in contract["candidate_stream_receipts"].values()
        ) != 6432
    ):
        raise PackagingError("Round-3 frozen population changed")
    git_inputs = runtime_git_receipts(repo)
    stream_container = next(
        row for row in git_inputs
        if row["role"] == "frozen_candidate_event_stream_bundle"
    )
    data_manifest = read_json(repo / DATA_MANIFEST)
    records = data_manifest["input_records"]
    external_inputs = [
        external_receipt(
            records["immutable_event_ledger"],
            path="../OMI-Window1-private/joined/events.jsonl",
            role="immutable_D804_event_ledger",
        ),
        external_receipt(
            records["public_print_archive"],
            path="../OMI-Window1-private/fit-local/prints.jsonl",
            role="frozen_public_fill_evidence_archive",
        ),
        external_receipt(
            records["public_tape_manifest"],
            path=(
                "../OMI-Window1-private/fit-local/"
                "PUBLIC_TAPE_MANIFEST.sanitized.json"
            ),
            role="frozen_public_tape_manifest",
        ),
    ]
    cache_record = records["per_leg_market_streams"]
    cache_files = [
        {
            "path": (
                "../OMI-Window1-private/fit-local/guarded-cache-v3/"
                + str(row["file"])
            ),
            "role": "per_event_content_bound_public_book_print_stream",
            "event_id": str(row["event_id"]),
            "event_date": str(row["event_date"]),
            "bytes": int(row["bytes"]),
            "git_blob_oid": None,
            "sha256": str(row["sha256"]),
            "availability": "available",
            "holdout_dates_present": 0,
        }
        for row in cache_record["event_file_receipts"]
    ]
    changed: dict[str, list[str]] = defaultdict(list)
    for row in read_jsonl(repo / R3_REAIM):
        changed[str(row["reaim_candidate_id"])].append(
            str(row["event_id"])
        )
    source_receipts = frozen_source_receipts(repo, r3_manifest)
    expected_progress = runner.expected_progress_sequence()
    expected_outputs = runner.expected_output_inventory()
    package = {
        "schema_version": runner.PACKAGE_SCHEMA,
        "execution_id": runner.EXECUTION_ID,
        "authorized_parent": PARENT,
        "authorization_audit": ROUND3_AUDIT,
        "controlling_identities": {
            "round3_prerun": PARENT,
            "round2_results": ROUND2_RESULTS,
            "round2_results_audit": {
                "commit": ROUND2_AUDIT,
                "report_path": ROUND2_AUDIT_REPORT,
                "report_blob_oid": ROUND2_AUDIT_BLOB,
            },
            "round3_prerun_audit": {
                "commit": ROUND3_AUDIT,
                "report_path": ROUND3_AUDIT_REPORT,
                "report_blob_oid": ROUND3_AUDIT_BLOB,
            },
        },
        "exact_execution_command": runner.EXACT_EXECUTION_COMMAND,
        "exact_validation_command": runner.EXACT_VALIDATION_COMMAND,
        "required_working_directory": "repository root",
        "result_directory": runner.RESULT_DIRECTORY,
        "validation_receipt_path": runner.VALIDATION_RECEIPT_PATH,
        "D": 804,
        "target_PC": 603,
        "development_dates": runner.DEV_DATES,
        "sealed_holdout_dates": runner.HOLDOUT_DATES,
        "candidate_ids": list(runner.FROZEN_CANDIDATES),
        "candidate_count": 8,
        "scorer_invocations_per_candidate": 1,
        "total_scorer_invocations": 8,
        "candidate_event_stream_receipts": contract[
            "candidate_stream_receipts"
        ],
        "candidate_event_stream_receipts_sha256": contract[
            "candidate_stream_receipts_sha256"
        ],
        "candidate_event_stream_count": 6432,
        "candidate_event_stream_inputs": stream_inputs(
            repo, contract, stream_container
        ),
        "frozen_event_leg_identities": contract[
            "frozen_event_leg_identities"
        ],
        "frozen_event_leg_identities_sha256": contract[
            "frozen_event_leg_identities_sha256"
        ],
        "leg_identity_count": 1608,
        "base_reaim_changed_order_event_ids": {
            candidate_id: sorted(changed.get(candidate_id, []))
            for candidate_id in runner.FROZEN_CANDIDATES
            if candidate_id.endswith("__reaim")
        },
        "git_inputs": git_inputs,
        "frozen_source_receipts": source_receipts,
        "frozen_source_receipts_sha256": canonical_sha256(source_receipts),
        "external_inputs": external_inputs,
        "market_cache_files": sorted(
            cache_files, key=lambda row: row["event_id"]
        ),
        "market_cache_aggregate": {
            "path": "../OMI-Window1-private/fit-local/guarded-cache-v3",
            "role": "frozen_per_event_market_stream_directory",
            "bytes": int(cache_record["bytes"]),
            "git_blob_oid": None,
            "sha256": str(cache_record["content_sha256"]),
            "file_count": 804,
            "holdout_dates_present": 0,
        },
        "roles": {
            "event_ledger": "../OMI-Window1-private/joined/events.jsonl",
            "public_print_archive": (
                "../OMI-Window1-private/fit-local/prints.jsonl"
            ),
            "public_tape_manifest": (
                "../OMI-Window1-private/fit-local/"
                "PUBLIC_TAPE_MANIFEST.sanitized.json"
            ),
            "market_cache_directory": (
                "../OMI-Window1-private/fit-local/guarded-cache-v3"
            ),
            "leg_ledger": (
                ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl"
            ),
            "start_ledger": (
                ".claude/window1_start_guard_corrected_20260724/"
                "REAL_START_LEDGER_V5.jsonl"
            ),
            "candidate_definitions": (
                "arb-executor/docs/research/window1/"
                "WINDOW1_ROUND3_CANDIDATES_V1.json"
            ),
            "candidate_event_streams": path_text(R3_STREAMS),
            "candidate_event_stream_receipts": path_text(CONTRACT),
            "scorer_source": (
                "arb-executor/analysis/window1_round2_scorer.py"
            ),
            "scorer_contract": path_text(CONTRACT),
            "metric_contract": (
                "arb-executor/docs/research/window1/"
                "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json"
            ),
            "data_binding_manifest": path_text(DATA_MANIFEST),
        },
        "scorer_source_sha256": next(
            row["sha256"]
            for row in git_inputs
            if row["role"] == "frozen_scorer"
        ),
        "scorer_contract_sha256": next(
            row["sha256"]
            for row in git_inputs
            if row["role"] == "frozen_scorer_contract"
        ),
        "runner_source_sha256": next(
            row["sha256"]
            for row in git_inputs
            if row["role"] == "deterministic_grid_runner"
        ),
        "metric_law": contract["metric_definitions"],
        "guarded_cutoff_law": contract["guarded_cutoff_contract"],
        "expected_progress_sequence": expected_progress,
        "expected_progress_sequence_sha256": canonical_sha256(
            expected_progress
        ),
        "expected_output_inventory": expected_outputs,
        "expected_output_inventory_sha256": canonical_sha256(
            expected_outputs
        ),
        "selection_law": {
            "status": "absent_in_frozen_PRE_RUN",
            "runner_action": "report_all_candidates_unranked",
            "selection_or_ranking_permitted": False,
        },
        "round3_mechanics": {
            "independent_per_leg_first_lawful_BBO_presence": True,
            "t_deep": "advisory_only",
            "postures": ["touch", "join", "park"],
            "recut_print_law": (
                "positive-size receipt-identified deduplicated public prints"
            ),
            "queue_preservation": True,
            "first_partial_or_complete_fill_arms_one_later_sibling_plus_one": True,
            "named_NO_CALL_and_censor_semantics": True,
            "sealed_dual_divot": (
                "unavailable_censored_unproxied_not_a_candidate"
            ),
        },
        "write_law": {
            "only_result_directory": runner.RESULT_DIRECTORY,
            "overwrite": False,
            "resume": False,
            "retry": False,
            "partial_artifact_reuse": False,
            "authoritative_progress": "PROGRESS.log",
            "append_flush_close_before_console_echo": True,
            "stdout_stderr_echo_nonfatal": True,
            "failed_stream_rebound_to_retained_devnull": True,
        },
        "candidate_scoring_performed": False,
        "scorer_invocations_during_packaging": 0,
        "performance_results_produced": False,
        "tuning_performed": False,
        "ranking_performed": False,
        "ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
    }
    package["input_bundle_sha256"] = canonical_sha256(package)
    return package


def prepare(repo: Path, output: Path) -> None:
    if output != (repo / OUTPUT).resolve():
        raise PackagingError("package output path must be exact")
    if git(repo, "rev-parse", "HEAD").decode().strip() != PARENT:
        raise PackagingError("prepare requires exact parent")
    verify_lineage_and_audits(repo)
    if (repo / runner.RESULT_DIRECTORY).exists():
        raise PackagingError("execution ID/result directory already exists")
    output.mkdir(parents=True, exist_ok=True)
    allowed = {
        CONTRACT.name,
        BUNDLE.name,
        VALIDATION.name,
        EXPECTED_PROGRESS.name,
        EXPECTED_OUTPUTS.name,
        TEST_RECEIPT.name,
        REFUSAL_RECEIPT.name,
        MANIFEST.name,
        REPORT.name,
        ARTIFACTS.name,
    }
    present = {path.name for path in output.iterdir() if path.is_file()}
    if present - allowed:
        raise PackagingError("unexpected package file exists")
    for path in (CONTRACT, BUNDLE, VALIDATION, MANIFEST, REPORT, ARTIFACTS):
        target = repo / path
        if target.exists():
            target.unlink()
    write_json(repo / CONTRACT, build_scorer_contract(repo))
    write_json(repo / EXPECTED_PROGRESS, {
        "schema_version": VERSION + "-expected-progress-v1",
        "execution_id": runner.EXECUTION_ID,
        "sequence": runner.expected_progress_sequence(),
        "sequence_sha256": canonical_sha256(
            runner.expected_progress_sequence()
        ),
        "authoritative_file": "PROGRESS.log",
        "scoring_performed": False,
    })
    write_json(repo / EXPECTED_OUTPUTS, {
        "schema_version": VERSION + "-expected-output-inventory-v1",
        "execution_id": runner.EXECUTION_ID,
        "successful_output_files": runner.expected_output_inventory(),
        "inventory_sha256": canonical_sha256(
            runner.expected_output_inventory()
        ),
        "outputs_created_during_packaging": 0,
        "scoring_performed": False,
    })
    write_json(repo / BUNDLE, build_package(repo))


BOUND_PATHS = [
    RUNNER_SOURCE,
    PACKAGER_SOURCE,
    RUNNER_TEST,
    STDOUT_TEST,
    CONTRACT,
    BUNDLE,
    VALIDATION,
    EXPECTED_PROGRESS,
    EXPECTED_OUTPUTS,
    TEST_RECEIPT,
    REFUSAL_RECEIPT,
    R3_MANIFEST,
    R3_STREAMS,
    DATA_MANIFEST,
]


def freeze(repo: Path, output: Path) -> None:
    if output != (repo / OUTPUT).resolve():
        raise PackagingError("package output path must be exact")
    branch = git(repo, "branch", "--show-current").decode().strip()
    if (
        branch not in ("", "codex/window1-definition")
        or git(repo, "rev-parse", "HEAD").decode().strip() != PARENT
    ):
        raise PackagingError("freeze requires exact parent")
    verify_lineage_and_audits(repo)
    if git(repo, "diff", "--name-only").strip():
        raise PackagingError("freeze refuses unstaged package changes")
    receipts = {
        path_text(path): receipt_from_index(
            repo, path, "bound_round3_execution_package_input"
        )
        for path in BOUND_PATHS
    }
    package = read_json(repo / BUNDLE)
    material = dict(package)
    bundle_hash = material.pop("input_bundle_sha256")
    validation = read_json(repo / VALIDATION)
    tests = read_json(repo / TEST_RECEIPT)
    refusals = read_json(repo / REFUSAL_RECEIPT)
    if (
        canonical_sha256(material) != bundle_hash
        or package["candidate_ids"] != runner.FROZEN_CANDIDATES
        or package["candidate_event_stream_count"] != 6432
        or package["leg_identity_count"] != 1608
        or package["controlling_identities"]["round3_prerun_audit"][
            "commit"
        ] != ROUND3_AUDIT
        or validation.get("gate_pass") is not True
        or validation.get("scorer_invocations") != 0
        or validation.get("performance_results_produced") is not False
        or tests.get("all_tests_passed") is not True
        or refusals.get("all_refusal_fixtures_passed") is not True
        or (repo / runner.RESULT_DIRECTORY).exists()
    ):
        raise PackagingError("Round-3 package freeze gate failed")
    manifest = {
        "schema_version": VERSION + "-prerun-v1",
        "freeze_status": "FROZEN_VALIDATED_NOT_SCORED",
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "exact_ancestry": {
            "parent": PARENT,
            "parent_of_parent": ROUND2_RESULTS,
            "package_commit": "this_manifest_commit",
            "commit_count_after_parent": 1,
        },
        "controlling_identities": package["controlling_identities"],
        "execution_id": runner.EXECUTION_ID,
        "result_directory": runner.RESULT_DIRECTORY,
        "exact_execution_command": runner.EXACT_EXECUTION_COMMAND,
        "exact_validation_command": runner.EXACT_VALIDATION_COMMAND,
        "input_bundle_sha256": bundle_hash,
        "input_bundle_receipt": receipts[path_text(BUNDLE)],
        "runner_receipt": receipts[path_text(RUNNER_SOURCE)],
        "scorer_source_sha256": package["scorer_source_sha256"],
        "scorer_contract_sha256": package["scorer_contract_sha256"],
        "metric_contract_sha256": (
            "19795e4d8bc7b6920e9fe93f7fa60bd1c051df94dade31de4c7909b40953cb76"
        ),
        "D": 804,
        "target_PC": 603,
        "candidate_ids": runner.FROZEN_CANDIDATES,
        "candidate_event_stream_count": 6432,
        "candidate_event_stream_receipts_sha256": package[
            "candidate_event_stream_receipts_sha256"
        ],
        "leg_identity_count": 1608,
        "frozen_event_leg_identities_sha256": package[
            "frozen_event_leg_identities_sha256"
        ],
        "development_dates": runner.DEV_DATES,
        "sealed_holdout_dates": runner.HOLDOUT_DATES,
        "expected_progress_sequence": package[
            "expected_progress_sequence"
        ],
        "expected_progress_sequence_sha256": package[
            "expected_progress_sequence_sha256"
        ],
        "expected_output_inventory": package[
            "expected_output_inventory"
        ],
        "expected_output_inventory_sha256": package[
            "expected_output_inventory_sha256"
        ],
        "frozen_source_receipts_sha256": package[
            "frozen_source_receipts_sha256"
        ],
        "bound_package_receipts": receipts,
        "validation_only_receipt": validation,
        "test_receipt": tests,
        "refusal_fixture_receipt": refusals,
        "candidate_scoring_performed": False,
        "scorer_invocations": 0,
        "performance_results_produced": False,
        "tuning_performed": False,
        "ranking_performed": False,
        "ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
        "invariants": {
            "additions_only_child": True,
            "frozen_candidates_and_streams_not_regenerated": True,
            "unchanged_scorer_metric_guard": True,
            "all_6432_streams_bound": True,
            "all_1608_leg_identities_bound": True,
            "new_execution_id_and_absent_result_directory": True,
            "one_attempt_no_retry_resume_overwrite": True,
            "stdout_stderr_safe_file_first_progress": True,
            "validation_only_zero_scorer_invocations": True,
            "holdout_and_prohibited_surfaces_inaccessible": True,
            "benchmark_not_executed": True,
        },
    }
    write_json(repo / MANIFEST, manifest)
    (repo / REPORT).write_text(
        "\n".join([
            "# Round-3 deterministic execution-package PRE-RUN",
            "",
            "Status: **FROZEN, VALIDATED, NOT SCORED.**",
            "",
            f"- Parent: `{PARENT}`",
            f"- Round-2 results audit: `{ROUND2_AUDIT}`",
            f"- Round-3 PRE-RUN audit: `{ROUND3_AUDIT}`",
            f"- Execution ID: `{runner.EXECUTION_ID}`",
            f"- Input-bundle SHA-256: `{bundle_hash}`",
            f"- Runner SHA-256: `{package['runner_source_sha256']}`",
            f"- Scorer SHA-256: `{package['scorer_source_sha256']}`",
            f"- Scorer contract SHA-256: `{package['scorer_contract_sha256']}`",
            f"- Exact unexecuted command: `{runner.EXACT_EXECUTION_COMMAND}`",
            "- Eight candidates and 6,432 committed streams are inputs in "
            "their frozen order; no stream was regenerated.",
            "- `PROGRESS.log` is authoritative and file-first; cosmetic "
            "stdout/stderr loss is nonfatal.",
            "- Validation-only loaded the package with zero scorer calls.",
            "- No benchmark, score, tuning, ranking, ablation, or holdout "
            "access occurred.",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    artifact_rows = {}
    for path in sorted(output.iterdir()):
        if not path.is_file() or path.name == ARTIFACTS.name:
            continue
        data = path.read_bytes()
        artifact_rows[path.name] = {
            "bytes": len(data),
            "sha256": sha256_bytes(data),
        }
    write_json(repo / ARTIFACTS, {
        "schema_version": VERSION + "-artifacts-v1",
        "parent": PARENT,
        "execution_id": runner.EXECUTION_ID,
        "artifacts": artifact_rows,
        "candidate_scoring_performed": False,
        "scorer_invocations": 0,
        "holdout_queried": False,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "freeze"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir.resolve()
        if args.output_dir.is_absolute()
        else (repo / args.output_dir).resolve()
    )
    if args.mode == "prepare":
        prepare(repo, output)
    else:
        freeze(repo, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
