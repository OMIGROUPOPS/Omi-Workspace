#!/usr/bin/env python3
"""Prepare and freeze the additive Round-2 one-shot execution package."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

import window1_round2_grid_runner as runner
import window1_round2_instrument as instrument
import window1_round2_real_capability as capability


VERSION = "window1-round2-stdout-safe-execution-packager-v2"
PARENT = "4b243babee97fe251bde21fa6a1197dfbba5387d"
AUDIT = "2ac4a2f49b55a5284cc1a9146047c3f42ea7561e"
FORENSIC_REPORT = (
    ".claude/forensic_20260725_w1r2_stdout_failure/FORENSIC_REPORT.md"
)
FORENSIC_REPORT_BLOB_OID = "b587b24173eb7e3605fa00b0fd06666b88b14442"
OUTPUT = Path(
    ".claude/window1_round2_stdout_safe_execution_package_20260725"
)
BUNDLE = OUTPUT / "SCORING_INPUT_BUNDLE.json"
PRIOR_PACKAGE = Path(".claude/window1_round2_execution_package_20260724")
PRIOR_BUNDLE = PRIOR_PACKAGE / "SCORING_INPUT_BUNDLE.json"
STREAM_BUNDLE = (
    PRIOR_PACKAGE / "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
)
VALIDATION = OUTPUT / "VALIDATION_ONLY_RECEIPT.json"
ORIGINAL_FREEZE = Path(
    ".claude/window1_round2_final_prerun_20260724"
)
ORIGINAL_MANIFEST = PRIOR_PACKAGE / "PRE_RUN_MANIFEST.json"
ORIGINAL_ARTIFACTS = PRIOR_PACKAGE / "ARTIFACT_MANIFEST.json"
CONTRACT = ORIGINAL_FREEZE / "SCORER_FREEZE_CONTRACT.json"
CAPABILITY = ORIGINAL_FREEZE / "ROUND2_REAL_CAPABILITY.json"
PAIR_PROOF = ORIGINAL_FREEZE / "ROUND2_REAIM_PAIR_PROOF.json"
DATA_MANIFEST = Path(
    ".claude/window1_round2_prerun_v2_20260724/"
    "ROUND2_DATA_BINDING_MANIFEST.json"
)
RUNNER_SOURCE = Path(
    "arb-executor/analysis/window1_round2_grid_runner.py"
)
PACKAGER_SOURCE = Path(
    "arb-executor/analysis/window1_round2_execution_packager.py"
)
TEST_SOURCE = Path(
    "arb-executor/tests/test_window1_round2_grid_runner.py"
)
STDOUT_TEST_SOURCE = Path(
    "arb-executor/tests/test_window1_round2_stdout_safe.py"
)

RUNTIME_GIT_INPUTS = [
    STREAM_BUNDLE,
    RUNNER_SOURCE,
    Path("arb-executor/analysis/window1_round2_instrument.py"),
    Path("arb-executor/analysis/window1_round2_real_capability.py"),
    Path("arb-executor/analysis/window1_round2_data_binding.py"),
    Path("arb-executor/analysis/window1_round2_scorer.py"),
    Path(
        "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND2_CANDIDATES_V1.json"
    ),
    Path(
        "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND2_EXECUTION_ADAPTER_V1.json"
    ),
    Path(
        "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json"
    ),
    Path(
        "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND2_SCORER_CONTRACT_V1.json"
    ),
    CONTRACT,
    CAPABILITY,
    PAIR_PROOF,
    DATA_MANIFEST,
    Path(
        ".claude/window1_start_guard_corrected_20260724/"
        "REAL_START_LEDGER_V5.jsonl"
    ),
    Path(".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl"),
    Path(".claude/entrysurface_20260717/band_map_v1.json"),
    Path(".claude/entrysurface_20260717/divot_tables_v1.json"),
    Path(".claude/entrysurface_20260717/drift_surfaces_v1.json"),
    Path(".claude/seqfloor_20260708/recut_cells.json"),
    Path(".claude/trendpath/ORIENT_V1.json"),
    Path(".claude/master_20260709/cohort.json"),
]


class PackagingError(RuntimeError):
    """Raised when the execution package cannot be frozen exactly."""


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
                    raise PackagingError(f"JSONL object required: {path}")
                rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
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
        raise PackagingError(
            f"git {' '.join(args)} failed: "
            + result.stderr.decode(errors="replace").strip()
        )
    return result.stdout


def verify_forensic_binding(repo: Path) -> None:
    commit = git(repo, "rev-parse", f"{AUDIT}^{{commit}}").decode().strip()
    blob = git(repo, "rev-parse", f"{AUDIT}:{FORENSIC_REPORT}").decode().strip()
    if commit != AUDIT or blob != FORENSIC_REPORT_BLOB_OID:
        raise PackagingError("controlling forensic commit/report binding changed")


def _path(value: Path) -> str:
    return str(value).replace("\\", "/")


def head_receipt(repo: Path, path: Path, role: str) -> dict[str, Any]:
    relative = _path(path)
    oid = git(repo, "rev-parse", f"HEAD:{relative}").decode().strip()
    data = git(repo, "cat-file", "blob", oid)
    return {
        "path": relative,
        "role": role,
        "bytes": len(data),
        "git_blob_oid": oid,
        "sha256": sha256_bytes(data),
        "availability": "available",
    }


def worktree_receipt(repo: Path, path: Path, role: str) -> dict[str, Any]:
    relative = _path(path)
    data = (repo / path).read_bytes()
    oid = git(
        repo, "hash-object", f"--path={relative}", relative
    ).decode().strip()
    return {
        "path": relative,
        "role": role,
        "bytes": len(data),
        "git_blob_oid": oid,
        "sha256": sha256_bytes(data),
        "availability": "available",
    }


def index_receipt(repo: Path, path: Path, role: str) -> dict[str, Any]:
    relative = _path(path)
    oid = git(repo, "rev-parse", f":{relative}").decode().strip()
    data = git(repo, "cat-file", "blob", oid)
    working_oid = git(
        repo, "hash-object", f"--path={relative}", relative
    ).decode().strip()
    if oid != working_oid:
        raise PackagingError(f"unstaged package change: {relative}")
    return {
        "path": relative,
        "role": role,
        "bytes": len(data),
        "git_blob_oid": oid,
        "sha256": sha256_bytes(data),
        "availability": "available",
    }


def external_receipt(
    record: Mapping[str, Any],
    *,
    path: str,
    role: str,
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


def _load_cache(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise PackagingError(f"cache object required: {path}")
    return value


def materialize_frozen_streams(repo: Path, output: Path) -> None:
    """Materialize, without scoring, the already-receipted frozen streams."""
    contract = read_json(repo / CONTRACT)
    events = read_jsonl(
        (repo / "../OMI-Window1-private/joined/events.jsonl").resolve()
    )
    runner.validate_dates(events)
    features = [
        row for row in read_jsonl(
            repo / ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl"
        )
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in features
    }
    if len(feature_map) != 1608:
        raise PackagingError("T8 feature identity count changed")
    spec = instrument.load_candidate_spec(repo)
    if spec["candidate_ids"] != runner.FROZEN_CANDIDATES:
        raise PackagingError("candidate order changed during stream materialization")
    policies = {
        candidate_id: instrument.candidate_policy(spec, candidate_id)
        for candidate_id in runner.FROZEN_CANDIDATES
    }
    surfaces = instrument.load_surfaces(repo)
    corridor = float(
        spec["common_parameters"]["policy_corridor_seconds_after_anchor"]
    )
    receipts = contract["candidate_stream_receipts"]
    cache_root = (
        repo / "../OMI-Window1-private/fit-local/guarded-cache-v3"
    ).resolve()
    stream_path = output / STREAM_BUNDLE.name
    count = 0
    raw = stream_path.open("wb")
    compressed = gzip.GzipFile(
        filename="",
        mode="wb",
        compresslevel=9,
        fileobj=raw,
        mtime=0,
    )
    with raw, compressed, io.TextIOWrapper(
        compressed, encoding="utf-8", newline="\n"
    ) as handle:
        for position, event in enumerate(events, 1):
            event_id = str(event["event_id"])
            cache = _load_cache(cache_root / f"{event_id}.json.gz")
            normalized = capability.normalize_event(
                event, cache, feature_map, corridor_seconds=corridor
            )
            for candidate_id in runner.FROZEN_CANDIDATES:
                stream = instrument.CausalInstrument(
                    surfaces, policies[candidate_id]
                ).run(normalized)
                expected = receipts[candidate_id][event_id]
                if (
                    stream["stream_sha256"] != expected
                    or stream.get("scored") is not False
                    or stream.get("metrics") is not None
                    or stream.get("evaluation_truth_present") is not False
                    or stream.get("holdout_queried") is not False
                ):
                    raise PackagingError(
                        "materialized stream differs from frozen receipt: "
                        f"{candidate_id}:{event_id}"
                    )
                handle.write(compact({
                    "candidate_id": candidate_id,
                    "event_id": event_id,
                    "stream": stream,
                }) + "\n")
                count += 1
            if position % 100 == 0 or position == len(events):
                print(compact({
                    "stage": "materialize_frozen_streams",
                    "events_complete": position,
                    "stream_rows_complete": count,
                    "scored": False,
                }), flush=True)
    if count != 6432:
        raise PackagingError("frozen stream bundle row count changed")


def build_package(repo: Path) -> dict[str, Any]:
    if git(repo, "rev-parse", "HEAD").decode().strip() != PARENT:
        raise PackagingError("prepare requires exact authorized parent")
    verify_forensic_binding(repo)
    prior_bundle = read_json(repo / PRIOR_BUNDLE)
    contract = read_json(repo / CONTRACT)
    capability = read_json(repo / CAPABILITY)
    pair = read_json(repo / PAIR_PROOF)
    data_manifest = read_json(repo / DATA_MANIFEST)
    records = data_manifest["input_records"]
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
        raise PackagingError("inherited freeze changed")
    role_by_path = {
        _path(STREAM_BUNDLE): "frozen_candidate_event_stream_bundle",
        _path(RUNNER_SOURCE): "deterministic_grid_runner",
        "arb-executor/analysis/window1_round2_instrument.py": (
            "frozen_candidate_stream_generator"
        ),
        "arb-executor/analysis/window1_round2_real_capability.py": (
            "frozen_normalization_adapter"
        ),
        "arb-executor/analysis/window1_round2_data_binding.py": (
            "frozen_input_validator"
        ),
        "arb-executor/analysis/window1_round2_scorer.py": "frozen_scorer",
        _path(CONTRACT): "frozen_scorer_contract",
        _path(CAPABILITY): "frozen_candidate_stream_receipt_ledger",
        _path(PAIR_PROOF): "frozen_base_reaim_changed_order_receipts",
        _path(DATA_MANIFEST): "immutable_data_binding_manifest",
        (
            ".claude/window1_start_guard_corrected_20260724/"
            "REAL_START_LEDGER_V5.jsonl"
        ): "frozen_start_boundary_ledger",
        ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl": (
            "frozen_leg_identity_and_feature_ledger"
        ),
    }
    git_inputs = []
    for path in RUNTIME_GIT_INPUTS:
        role = role_by_path.get(_path(path), "frozen_policy_surface_or_contract")
        git_inputs.append(
            worktree_receipt(repo, path, role)
            if path == RUNNER_SOURCE
            else head_receipt(repo, path, role)
        )
    stream_container = next(
        row for row in git_inputs
        if row["role"] == "frozen_candidate_event_stream_bundle"
    )
    stream_rows = read_jsonl(repo / STREAM_BUNDLE)
    if len(stream_rows) != 6432:
        raise PackagingError("candidate stream bundle is not 6,432 rows")
    event_ids = list(
        contract["candidate_stream_receipts"][
            runner.FROZEN_CANDIDATES[0]
        ]
    )
    expected_pairs = [
        (candidate_id, event_id)
        for event_id in event_ids
        for candidate_id in runner.FROZEN_CANDIDATES
    ]
    stream_inputs = []
    for ordinal, (row, expected_pair) in enumerate(
        zip(stream_rows, expected_pairs, strict=True), 1
    ):
        candidate_id = str(row.get("candidate_id") or "")
        event_id = str(row.get("event_id") or "")
        stream = row.get("stream")
        line_bytes = (compact(row) + "\n").encode()
        expected_sha = contract["candidate_stream_receipts"][
            candidate_id
        ][event_id]
        if (
            (candidate_id, event_id) != expected_pair
            or not isinstance(stream, Mapping)
            or stream.get("stream_sha256") != expected_sha
            or canonical_sha256(stream.get("order_stream")) != expected_sha
        ):
            raise PackagingError(
                "candidate stream bundle order/content mismatch"
            )
        stream_inputs.append({
            "ordinal": ordinal,
            "candidate_id": candidate_id,
            "event_id": event_id,
            "path": f"{_path(STREAM_BUNDLE)}#L{ordinal}",
            "role": "frozen_candidate_event_order_stream",
            "bytes": len(line_bytes),
            "git_blob_oid": stream_container["git_blob_oid"],
            "sha256": sha256_bytes(line_bytes),
            "container_sha256": stream_container["sha256"],
            "stream_sha256": expected_sha,
            "availability": "available",
        })
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
            "role": "per_event_public_print_and_top5_stream",
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
    changed_ids = {
        str(row["reaim_candidate_id"]): list(row["changed_event_ids"])
        for row in pair["pairs"]
    }
    package = {
        "schema_version": runner.PACKAGE_SCHEMA,
        "execution_id": runner.EXECUTION_ID,
        "authorized_parent": PARENT,
        "authorization_audit": AUDIT,
        "controlling_forensic": {
            "commit": AUDIT,
            "report_path": FORENSIC_REPORT,
            "report_blob_oid": FORENSIC_REPORT_BLOB_OID,
            "verdict": "CATEGORY_A_OUTPUT_ONLY_INFRASTRUCTURE_FAILURE",
        },
        "retired_execution_id": runner.RETIRED_EXECUTION_ID,
        "retired_result_directory": runner.RETIRED_RESULT_DIRECTORY,
        "retired_attempt_consumed_as_input": False,
        "exact_execution_command": runner.EXACT_EXECUTION_COMMAND,
        "exact_validation_command": runner.EXACT_VALIDATION_COMMAND,
        "required_working_directory": "repository root",
        "result_directory": runner.RESULT_DIRECTORY,
        "validation_receipt_path": runner.VALIDATION_RECEIPT_PATH,
        "D": 804,
        "target_PC": 603,
        "development_dates": runner.DEV_DATES,
        "sealed_holdout_dates": runner.HOLDOUT_DATES,
        "candidate_ids": runner.FROZEN_CANDIDATES,
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
        "candidate_event_stream_inputs": stream_inputs,
        "frozen_event_leg_identities": contract[
            "frozen_event_leg_identities"
        ],
        "frozen_event_leg_identities_sha256": contract[
            "frozen_event_leg_identities_sha256"
        ],
        "leg_identity_count": 1608,
        "base_reaim_changed_order_event_ids": changed_ids,
        "git_inputs": sorted(git_inputs, key=lambda row: row["path"]),
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
            "event_ledger": (
                "../OMI-Window1-private/joined/events.jsonl"
            ),
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
                ".claude/window1_20260721/"
                "WINDOW1_FEATURE_MATRIX.jsonl"
            ),
            "start_ledger": (
                ".claude/window1_start_guard_corrected_20260724/"
                "REAL_START_LEDGER_V5.jsonl"
            ),
            "candidate_definitions": (
                "arb-executor/docs/research/window1/"
                "WINDOW1_ROUND2_CANDIDATES_V1.json"
            ),
            "candidate_event_streams": _path(STREAM_BUNDLE),
            "candidate_event_stream_receipts": _path(CONTRACT),
            "scorer_source": (
                "arb-executor/analysis/window1_round2_scorer.py"
            ),
            "scorer_contract": _path(CONTRACT),
            "metric_contract": (
                "arb-executor/docs/research/window1/"
                "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json"
            ),
            "data_binding_manifest": _path(DATA_MANIFEST),
        },
        "scorer_source_sha256": next(
            row["sha256"] for row in git_inputs
            if row["role"] == "frozen_scorer"
        ),
        "scorer_contract_sha256": next(
            row["sha256"] for row in git_inputs
            if row["role"] == "frozen_scorer_contract"
        ),
        "runner_source_sha256": next(
            row["sha256"] for row in git_inputs
            if row["role"] == "deterministic_grid_runner"
        ),
        "metric_law": contract["metric_definitions"],
        "guarded_cutoff_law": contract["guarded_cutoff_contract"],
        "selection_law": {
            "status": "absent_in_frozen_PRE_RUN",
            "runner_action": "report_all_candidates_unranked",
            "selection_or_ranking_permitted": False,
        },
        "reconstruction_law": {
            "candidate_stream_content": (
                "read the materialized frozen candidate-event stream bundle; "
                "require its Git blob, file SHA-256, 6,432 per-row byte "
                "receipts, and frozen per-event stream SHA-256 identities"
            ),
            "fill_evidence": (
                "receipt-identified positive-size public print observations "
                "from the frozen cache"
            ),
            "window1_close_reference": (
                "last receipt-identified positive-size public true print "
                "at or before the authoritative guarded cutoff"
            ),
            "feature_classification": (
                "frozen instrument terminal and named NO_CALL actions"
            ),
            "policy_or_metric_changes": False,
        },
        "write_law": {
            "only_result_directory": runner.RESULT_DIRECTORY,
            "overwrite": False,
            "resume": False,
            "retry": False,
            "partial_failure_log_preserved": True,
            "authoritative_progress": "PROGRESS.log",
            "progress_file_flushed_before_console_echo": True,
            "stdout_stderr_echo_nonfatal": True,
            "console_failure_rebinds_to_os_devnull": True,
        },
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "ranking_performed": False,
        "ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
    }
    current_non_runner = [
        row for row in package["git_inputs"]
        if row["role"] != "deterministic_grid_runner"
    ]
    prior_non_runner = [
        row for row in prior_bundle["git_inputs"]
        if row["role"] != "deterministic_grid_runner"
    ]
    parity_checks = {
        "non_runner_git_inputs": current_non_runner == prior_non_runner,
        "external_inputs": (
            package["external_inputs"] == prior_bundle["external_inputs"]
        ),
        "market_cache_files": (
            package["market_cache_files"]
            == prior_bundle["market_cache_files"]
        ),
        "market_cache_aggregate": (
            package["market_cache_aggregate"]
            == prior_bundle["market_cache_aggregate"]
        ),
        "candidate_event_stream_inputs": (
            package["candidate_event_stream_inputs"]
            == prior_bundle["candidate_event_stream_inputs"]
        ),
        "candidate_event_stream_receipts": (
            package["candidate_event_stream_receipts"]
            == prior_bundle["candidate_event_stream_receipts"]
        ),
        "frozen_event_leg_identities": (
            package["frozen_event_leg_identities"]
            == prior_bundle["frozen_event_leg_identities"]
        ),
        "metric_law": package["metric_law"] == prior_bundle["metric_law"],
        "guarded_cutoff_law": (
            package["guarded_cutoff_law"]
            == prior_bundle["guarded_cutoff_law"]
        ),
        "candidate_ids": (
            package["candidate_ids"] == prior_bundle["candidate_ids"]
        ),
        "D": package["D"] == prior_bundle["D"] == 804,
    }
    if (
        len(current_non_runner) != 21
        or not all(parity_checks.values())
    ):
        raise PackagingError("frozen non-runner surface parity failed")
    package["frozen_surface_parity"] = {
        "baseline_PRE_RUN": PARENT,
        "non_runner_git_input_count": 21,
        "non_runner_git_inputs_sha256": canonical_sha256(
            current_non_runner
        ),
        "external_inputs_sha256": canonical_sha256(
            package["external_inputs"]
        ),
        "market_cache_files_sha256": canonical_sha256(
            package["market_cache_files"]
        ),
        "candidate_event_stream_inputs_sha256": canonical_sha256(
            package["candidate_event_stream_inputs"]
        ),
        "candidate_event_stream_receipts_sha256": package[
            "candidate_event_stream_receipts_sha256"
        ],
        "frozen_event_leg_identities_sha256": package[
            "frozen_event_leg_identities_sha256"
        ],
        "checks": parity_checks,
        "all_checks_pass": True,
    }
    package["input_bundle_sha256"] = canonical_sha256(package)
    return package


def prepare(repo: Path, output: Path) -> None:
    if output != (repo / OUTPUT).resolve():
        raise PackagingError("execution package output path must be exact")
    if output.exists() and any(output.iterdir()):
        allowed = {
            BUNDLE.name,
            STREAM_BUNDLE.name,
            VALIDATION.name,
            "PRE_RUN_MANIFEST.json",
            "PRE_RUN_REPORT.md",
            "ARTIFACT_MANIFEST.json",
        }
        present = {path.name for path in output.iterdir() if path.is_file()}
        if present - allowed:
            raise PackagingError("execution package output already populated")
    output.mkdir(parents=True, exist_ok=True)
    for stale in (
        BUNDLE,
        VALIDATION,
        OUTPUT / "PRE_RUN_MANIFEST.json",
        OUTPUT / "PRE_RUN_REPORT.md",
        OUTPUT / "ARTIFACT_MANIFEST.json",
    ):
        target = repo / stale
        if target.exists():
            target.unlink()
    if not (repo / STREAM_BUNDLE).is_file():
        raise PackagingError(
            "frozen 4b243bab stream bundle missing; rematerialization refused"
        )
    write_json(output / BUNDLE.name, build_package(repo))


BOUND_PATHS = [
    RUNNER_SOURCE,
    PACKAGER_SOURCE,
    TEST_SOURCE,
    STDOUT_TEST_SOURCE,
    BUNDLE,
    STREAM_BUNDLE,
    VALIDATION,
    PRIOR_BUNDLE,
    ORIGINAL_MANIFEST,
    ORIGINAL_ARTIFACTS,
    CONTRACT,
    CAPABILITY,
    PAIR_PROOF,
    DATA_MANIFEST,
]


def freeze(repo: Path, output: Path) -> None:
    if output != (repo / OUTPUT).resolve():
        raise PackagingError("execution package output path must be exact")
    if (
        git(repo, "branch", "--show-current").decode().strip()
        != "codex/window1-definition"
        or git(repo, "rev-parse", "HEAD").decode().strip() != PARENT
    ):
        raise PackagingError("freeze requires exact parent and branch")
    verify_forensic_binding(repo)
    if git(repo, "diff", "--name-only").strip():
        raise PackagingError("freeze refuses unstaged package changes")
    receipts = {
        _path(path): index_receipt(repo, path, "bound_PRE_RUN_input")
        for path in BOUND_PATHS
    }
    package = read_json(repo / BUNDLE)
    material = dict(package)
    package_hash = material.pop("input_bundle_sha256")
    validation = read_json(repo / VALIDATION)
    original = read_json(repo / ORIGINAL_MANIFEST)
    if (
        canonical_sha256(material) != package_hash
        or package_hash != package["input_bundle_sha256"]
        or package["execution_id"] != runner.EXECUTION_ID
        or package["exact_execution_command"]
        != runner.EXACT_EXECUTION_COMMAND
        or package["candidate_ids"] != runner.FROZEN_CANDIDATES
        or package["candidate_event_stream_count"] != 6432
        or package["leg_identity_count"] != 1608
        or package.get("controlling_forensic", {}).get("commit") != AUDIT
        or package.get("controlling_forensic", {}).get(
            "report_blob_oid"
        ) != FORENSIC_REPORT_BLOB_OID
        or package.get("retired_execution_id")
        != runner.RETIRED_EXECUTION_ID
        or package.get("frozen_surface_parity", {}).get(
            "all_checks_pass"
        ) is not True
        or validation.get("gate_pass") is not True
        or validation.get("scorer_invocations") != 0
        or validation.get("performance_results_produced") is not False
        or validation.get("candidate_event_streams_loaded") != 6432
        or original.get("candidate_scoring_performed") is not False
        or (repo / runner.RESULT_DIRECTORY).exists()
    ):
        raise PackagingError("execution package freeze gate failed")
    preserved = {
        row["path"]: row
        for row in package["git_inputs"]
        if row["role"] != "deterministic_grid_runner"
    }
    manifest = {
        "schema_version": VERSION + "-prerun-v1",
        "freeze_status": "frozen_not_scored",
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "branch": "codex/window1-definition",
        "exact_ancestry": {
            "parent": PARENT,
            "superseding_commit": "this_manifest_commit",
            "commit_count_after_parent": 1,
        },
        "authorization_audit": AUDIT,
        "controlling_forensic": {
            "commit": AUDIT,
            "report_path": FORENSIC_REPORT,
            "report_blob_oid": FORENSIC_REPORT_BLOB_OID,
            "verdict": "CATEGORY_A_OUTPUT_ONLY_INFRASTRUCTURE_FAILURE",
        },
        "retired_execution": {
            "execution_id": runner.RETIRED_EXECUTION_ID,
            "result_directory": runner.RETIRED_RESULT_DIRECTORY,
            "permanently_inadmissible": True,
            "consumed_as_package_input": False,
            "retry_or_resume_permitted": False,
        },
        "execution_id": runner.EXECUTION_ID,
        "exact_execution_command": runner.EXACT_EXECUTION_COMMAND,
        "exact_validation_command": runner.EXACT_VALIDATION_COMMAND,
        "result_directory": runner.RESULT_DIRECTORY,
        "input_bundle": {
            "path": _path(BUNDLE),
            "canonical_sha256": package_hash,
            "receipt": receipts[_path(BUNDLE)],
        },
        "deterministic_grid_runner": {
            "path": _path(RUNNER_SOURCE),
            "receipt": receipts[_path(RUNNER_SOURCE)],
            "candidate_order": runner.FROZEN_CANDIDATES,
            "scorer_invocations_per_candidate": 1,
            "total_scorer_invocations": 8,
        },
        "stdout_safe_fixture_proof": {
            "test_path": _path(STDOUT_TEST_SOURCE),
            "receipt": receipts[_path(STDOUT_TEST_SOURCE)],
            "synthetic_candidates_only": True,
            "real_D804_bundle_consumed": False,
            "scorer_invocations": 0,
            "required_cases": [
                "pipe_reader_disappears_after_initial_success",
                "detached_non_console_stdout",
                "explicitly_closed_stdout",
                "ValueError_from_closed_text_stream",
                "exit_time_flush_after_pipe_failure",
                "all_fixture_candidates_and_final_receipts_continue",
                "equivalent_nonfatal_stderr_guard",
            ],
        },
        "validation_only": validation,
        "D": 804,
        "target_PC": 603,
        "development_dates": runner.DEV_DATES,
        "sealed_holdout_dates": runner.HOLDOUT_DATES,
        "candidate_ids": runner.FROZEN_CANDIDATES,
        "candidate_event_stream_count": 6432,
        "candidate_event_stream_bundle": {
            "path": _path(STREAM_BUNDLE),
            "receipt": receipts[_path(STREAM_BUNDLE)],
            "per_stream_input_receipts": 6432,
        },
        "candidate_event_stream_receipts_sha256": package[
            "candidate_event_stream_receipts_sha256"
        ],
        "leg_identity_count": 1608,
        "frozen_event_leg_identities_sha256": package[
            "frozen_event_leg_identities_sha256"
        ],
        "frozen_surface_parity": package["frozen_surface_parity"],
        "preserved_inherited_blobs": preserved,
        "package_source_code_receipts": receipts,
        "selection_status": "UNRANKED_FROZEN_SELECTION_RULE_ABSENT",
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "ranking_performed": False,
        "ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
        "invariants": {
            "parent_exact_4b243bab": True,
            "controlling_forensic_commit_and_blob_bound": True,
            "retired_grid1_not_reused_or_consumed": True,
            "new_result_directory_refuses_existing": True,
            "execution_id_frozen": True,
            "one_exact_execution_command": True,
            "complete_input_bundle_hash_bound": True,
            "eight_candidate_order_exact": True,
            "all_6432_stream_receipts_preserved": True,
            "all_6432_stream_contents_materialized_and_bound": True,
            "all_1608_leg_identities_preserved": True,
            "frozen_scorer_and_metric_unchanged": True,
            "all_21_non_runner_git_inputs_byte_identical": True,
            "guard_law_unchanged": True,
            "development_dates_only": True,
            "holdout_hard_refused": True,
            "overwrite_resume_retry_refused": True,
            "validation_only_zero_scorer_invocations": True,
            "stdout_stderr_console_echo_nonfatal": True,
            "progress_log_authoritative_and_flushed_first": True,
            "benchmark_not_executed": True,
        },
    }
    write_json(output / "PRE_RUN_MANIFEST.json", manifest)
    (output / "PRE_RUN_REPORT.md").write_text(
        "\n".join([
            "# Round-2 stdout-safe deterministic execution-package PRE-RUN",
            "",
            "Status: **FROZEN, VALIDATED, NOT SCORED.**",
            "",
            f"- Parent: `{PARENT}`",
            f"- Controlling forensic: `{AUDIT}`",
            f"- Forensic report blob: `{FORENSIC_REPORT_BLOB_OID}`",
            f"- Execution ID: `{runner.EXECUTION_ID}`",
            f"- Input-bundle SHA-256: `{package_hash}`",
            f"- Exact command: `{runner.EXACT_EXECUTION_COMMAND}`",
            "- Eight candidates dispatch in the existing frozen order.",
            "- All 6,432 frozen candidate-event streams are materialized and "
            "hash-bound as scorer inputs.",
            "- The frozen scorer is invoked exactly once per candidate.",
            "- `PROGRESS.log` is authoritative; stdout/stderr echo is nonfatal.",
            "- Seven synthetic output-handle fixture cases are bound in tests.",
            "- Retired grid1 evidence is excluded and never consumed.",
            "- Validation-only loaded all receipts with zero scorer calls.",
            "- No benchmark, ranking, tuning, ablation, or holdout ran.",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    artifacts = {}
    for path in sorted(output.iterdir()):
        if (
            not path.is_file()
            or path.name == "ARTIFACT_MANIFEST.json"
        ):
            continue
        data = path.read_bytes()
        artifacts[path.name] = {
            "bytes": len(data),
            "sha256": sha256_bytes(data),
        }
    write_json(output / "ARTIFACT_MANIFEST.json", {
        "schema_version": VERSION + "-artifacts-v1",
        "parent": PARENT,
        "controlling_forensic_commit": AUDIT,
        "controlling_forensic_report_blob_oid": (
            FORENSIC_REPORT_BLOB_OID
        ),
        "execution_id": runner.EXECUTION_ID,
        "artifacts": artifacts,
        "candidate_scoring_performed": False,
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
