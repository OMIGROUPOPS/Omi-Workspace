#!/usr/bin/env python3
"""Validate and freeze the score-free Round-3 Window-1 PRE-RUN.

This module hashes policy inputs and already-generated counterfactual order
streams.  It never imports or invokes the scorer and has no benchmark mode.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import window1_round2_data_binding as binding
import window1_round2_instrument as r2
import window1_round3_instrument as r3


VERSION = "window1-round3-score-free-prerun-v1"
RESULTS_COMMIT = "10ac6dbc68d65cb21ab3718e118ff34d7220ad87"
AUDIT_COMMIT = "807e2c865c3cf7384757c54a3b879518568dec4f"
AUTHORIZED_ROUND2_PRERUN = (
    "47bfbd4335a435a30054be9007c5029331252eee"
)
AUDIT_REPORT_PATH = (
    ".claude/audit_20260725_grid2_results/AUDIT_REPORT.md"
)
AUDIT_REPORT_BLOB = "9bb51a3dc19fd055156ee958a6f208b1a725cbc4"
R2_BUNDLE_PATH = (
    ".claude/window1_round2_stdout_safe_execution_package_20260725/"
    "SCORING_INPUT_BUNDLE.json"
)
EVENTS_PATH = "../OMI-Window1-private/joined/events.jsonl"
CACHE_ROOT = "../OMI-Window1-private/fit-local/guarded-cache-v3"
CAPABILITY_DIR = ".claude/window1_round3_prerun_20260725"
FORENSIC_DIR = ".claude/window1_round3_forensic_20260725"
STREAM_PATH = (
    CAPABILITY_DIR + "/FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
)

SOURCE_PATHS = [
    "arb-executor/analysis/window1_round3_instrument.py",
    "arb-executor/analysis/window1_round3_prerun_builder.py",
    "arb-executor/analysis/window1_round3_starvation_forensic.py",
    "arb-executor/analysis/window1_round3_freeze.py",
    "arb-executor/tests/test_window1_round3_instrument.py",
    "arb-executor/analysis/window1_round2_instrument.py",
    "arb-executor/analysis/window1_round2_real_capability.py",
    "arb-executor/analysis/window1_round2_data_binding.py",
    "arb-executor/analysis/window1_round2_scorer.py",
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND3_CANDIDATES_V1.json",
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json",
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_SCORER_CONTRACT_V1.json",
    "arb-executor/docs/LIVING_VAULT.md",
    "arb-executor/docs/LIFECYCLE.md",
    "arb-executor/docs/THE_DAILY_STANDARD.md",
    "arb-executor/docs/OPERATOR_CONSTRAINTS.md",
    "arb-executor/docs/MODEL_REGISTRY.md",
    "arb-executor/docs/research/window1/"
    "WINDOW1_OS_FAMILY_ADAPTER_V1.json",
    "arb-executor/docs/research/window1/"
    "WINDOW1_OS_FAMILY_FEATURE_ALLOWLIST_V1.json",
]

BOUND_GIT_DATA_PATHS = [
    *r2.SURFACE_PATHS.values(),
    binding.FEATURE_LEDGER,
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl",
    ".claude/window1_start_guard_corrected_20260724/"
    "ARTIFACT_MANIFEST.json",
    ".claude/window1_round2_prerun_v2_20260724/"
    "ROUND2_DATA_BINDING_MANIFEST.json",
]

ARTIFACT_PATHS = [
    f"{FORENSIC_DIR}/PARTNER_LEG_STARVATION_LEDGER.jsonl",
    f"{FORENSIC_DIR}/PARTNER_LEG_STARVATION_COUNTS.json",
    f"{FORENSIC_DIR}/BASE_REAIM_ORDER_DIFFERENCE_LEDGER.jsonl",
    f"{FORENSIC_DIR}/ROUND2_CANDIDATE_DECISION_PROOF.json",
    f"{FORENSIC_DIR}/ROUND2_ROOT_CAUSE_FORENSIC.json",
    f"{FORENSIC_DIR}/ROUND2_ROOT_CAUSE_FORENSIC.md",
    f"{FORENSIC_DIR}/OS_LINEAGE_RECONCILIATION.md",
    STREAM_PATH,
    f"{CAPABILITY_DIR}/ROUND3_REAL_CAPABILITY.json",
    f"{CAPABILITY_DIR}/ROUND3_CANDIDATE_ORDER_DIFFERENCES.jsonl",
    f"{CAPABILITY_DIR}/ROUND3_REAIM_ORDER_DIFFERENCES.jsonl",
    f"{CAPABILITY_DIR}/ROUND3_POLICY_FAMILY_SPEC.md",
    f"{CAPABILITY_DIR}/ROUND3_REAL_CAPABILITY_REPORT.md",
]


class FreezeError(RuntimeError):
    """Raised when a frozen identity or score-free gate fails."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def git_blob(repo: Path, path: Path) -> str:
    return git(repo, "hash-object", "--", str(path))


def receipt(repo: Path, relative: str, role: str) -> dict[str, Any]:
    path = (repo / relative).resolve()
    if not path.is_file():
        raise FreezeError(f"missing bound file: {relative}")
    size, digest = hash_file(path)
    return {
        "role": role,
        "path": relative.replace("\\", "/"),
        "bytes": size,
        "sha256": digest,
        "git_blob_oid": git_blob(repo, path),
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def verify_commit_bindings(repo: Path) -> dict[str, Any]:
    for commit in (
        RESULTS_COMMIT, AUDIT_COMMIT, AUTHORIZED_ROUND2_PRERUN
    ):
        if git(repo, "cat-file", "-t", commit) != "commit":
            raise FreezeError(f"missing controlling commit: {commit}")
    parent = git(repo, "show", "-s", "--format=%P", RESULTS_COMMIT)
    if parent != AUTHORIZED_ROUND2_PRERUN:
        raise FreezeError("result commit ancestry changed")
    audit_entry = git(
        repo, "ls-tree", AUDIT_COMMIT, AUDIT_REPORT_PATH
    ).split()
    if len(audit_entry) < 3 or audit_entry[2] != AUDIT_REPORT_BLOB:
        raise FreezeError("audit report blob identity changed")
    audit_text = git(
        repo, "show", f"{AUDIT_COMMIT}:{AUDIT_REPORT_PATH}"
    )
    for identity in (
        RESULTS_COMMIT, AUTHORIZED_ROUND2_PRERUN
    ):
        if identity[:8] not in audit_text:
            raise FreezeError(
                f"audit report does not bind controlling SHA: {identity}"
            )
    return {
        "results_commit": RESULTS_COMMIT,
        "results_parent": parent,
        "authorized_round2_prerun": AUTHORIZED_ROUND2_PRERUN,
        "independent_audit_commit": AUDIT_COMMIT,
        "independent_audit_report_path": AUDIT_REPORT_PATH,
        "independent_audit_report_blob_oid": AUDIT_REPORT_BLOB,
    }


def verify_events(repo: Path) -> tuple[dict[str, Any], list[str]]:
    path = (repo / EVENTS_PATH).resolve()
    rows = read_jsonl(path)
    if len(rows) != binding.D_REQUIRED:
        raise FreezeError(f"D changed: {len(rows)}")
    dates = sorted({str(row["event_date"]) for row in rows})
    if dates != binding.DEV_DATES:
        raise FreezeError(f"development dates changed: {dates}")
    event_ids = [str(row["event_id"]) for row in rows]
    if len(set(event_ids)) != binding.D_REQUIRED:
        raise FreezeError("duplicate D=804 event identity")
    leg_ids = [
        f"{row['event_id']}|{leg['leg']}|{leg['ticker']}"
        for row in rows for leg in row["legs"]
    ]
    if len(leg_ids) != 1608 or len(set(leg_ids)) != 1608:
        raise FreezeError("1,608 leg identity conservation failed")
    raw = path.read_bytes()
    return ({
        "role": "immutable_D804_event_ledger",
        "path": EVENTS_PATH,
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "git_blob_oid": None,
        "rows": len(rows),
        "events": len(event_ids),
        "legs": len(leg_ids),
        "tickers": len({
            str(leg["ticker"]) for row in rows for leg in row["legs"]
        }),
        "date_range": [dates[0], dates[-1]],
        "causal_timestamp_fields": [
            "scheduled_start_exchange_ts",
            "schedule_observed_exchange_ts",
        ],
        "holdout_dates_present": 0,
    }, leg_ids)


def verify_cache(
    repo: Path, event_ids: Iterable[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    old_bundle = json.loads(
        (repo / R2_BUNDLE_PATH).read_text(encoding="utf-8")
    )
    frozen = list(old_bundle["market_cache_files"])
    expected_ids = set(event_ids)
    if len(frozen) != binding.D_REQUIRED:
        raise FreezeError("cache receipt count changed")
    output = []
    for prior in frozen:
        relative = str(prior["path"])
        event_id = Path(relative).name.removesuffix(".json.gz")
        if event_id not in expected_ids:
            raise FreezeError(f"cache event outside D=804: {event_id}")
        path = (repo / relative).resolve()
        size, digest = hash_file(path)
        if (
            size != int(prior["bytes"])
            or digest != str(prior["sha256"])
        ):
            raise FreezeError(f"cache receipt changed: {relative}")
        output.append({
            "event_id": event_id,
            "path": relative,
            "bytes": size,
            "sha256": digest,
            "date_scope": "2026-07-12..2026-07-20",
            "causal_timestamp_field": "ts",
            "holdout": False,
        })
    if {row["event_id"] for row in output} != expected_ids:
        raise FreezeError("cache/event identity mismatch")
    aggregate = dict(old_bundle["market_cache_aggregate"])
    if aggregate["path"] != CACHE_ROOT:
        raise FreezeError("cache root changed")
    aggregate.update({
        "verified_file_count": len(output),
        "holdout_dates_present": 0,
    })
    return aggregate, output


def verify_streams(
    repo: Path,
    event_ids: list[str],
    candidate_ids: list[str],
) -> tuple[list[dict[str, Any]], str]:
    receipts: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    path = repo / STREAM_PATH
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            row = json.loads(line)
            candidate_id = str(row["candidate_id"])
            event_id = str(row["event_id"])
            expected_event = event_ids[index // len(candidate_ids)]
            expected_candidate = candidate_ids[index % len(candidate_ids)]
            if (
                event_id != expected_event
                or candidate_id != expected_candidate
            ):
                raise FreezeError("candidate/event ordering changed")
            key = (candidate_id, event_id)
            if key in seen:
                raise FreezeError("duplicate candidate/event stream")
            seen.add(key)
            stream = row["stream"]
            if (
                stream["scored"] is not False
                or stream["metrics"] is not None
                or stream["holdout_queried"] is not False
                or stream["evaluation_truth_present"] is not False
            ):
                raise FreezeError("performance/evaluation truth leaked")
            if str(stream["event_date"]) not in binding.DEV_DATES:
                raise FreezeError("stream date outside development scope")
            receipts.append({
                "candidate_id": candidate_id,
                "event_id": event_id,
                "stream_sha256": str(stream["stream_sha256"]),
            })
    required = binding.D_REQUIRED * len(candidate_ids)
    if len(receipts) != required or len(seen) != required:
        raise FreezeError("6,432 stream conservation failed")
    return receipts, sha256_bytes(
        compact(receipts).encode("utf-8")
    )


def build(repo: Path) -> dict[str, Any]:
    identities = verify_commit_bindings(repo)
    spec = r3.load_candidate_spec(repo)
    candidate_ids = list(map(str, spec["candidate_ids"]))
    if len(candidate_ids) != 8 or len(set(candidate_ids)) != 8:
        raise FreezeError("candidate set changed")
    event_receipt, leg_ids = verify_events(repo)
    event_ids = [
        row["event_id"]
        for row in read_jsonl((repo / EVENTS_PATH).resolve())
    ]
    cache_aggregate, cache_files = verify_cache(repo, event_ids)
    stream_receipts, stream_receipt_hash = verify_streams(
        repo, event_ids, candidate_ids
    )
    source_receipts = [
        receipt(repo, path, "source_or_contract")
        for path in SOURCE_PATHS
    ]
    data_receipts = [
        receipt(repo, path, "bound_git_data")
        for path in BOUND_GIT_DATA_PATHS
    ]
    artifact_receipts = [
        receipt(repo, path, "sanitized_prerun_artifact")
        for path in ARTIFACT_PATHS
    ]
    leg_identity_hash = sha256_bytes(
        compact(sorted(leg_ids)).encode("utf-8")
    )
    return {
        "schema_version": VERSION,
        "controlling_identities": identities,
        "development_scope": {
            "dates": binding.DEV_DATES,
            "D": binding.D_REQUIRED,
            "leg_identities": len(leg_ids),
            "leg_identity_sha256": leg_identity_hash,
            "candidate_count": len(candidate_ids),
            "candidate_ids_in_frozen_order": candidate_ids,
            "candidate_event_streams": len(stream_receipts),
            "target_PC": 603,
        },
        "metric_contract": {
            "unchanged_from_round2": True,
            "D": 804,
            "C": (
                "both legs filled exactly five contracts inside lawful "
                "guarded Window 1"
            ),
            "PC": "C and combined close delta strictly negative",
            "S": "C and combined entry cost strictly below 100",
            "IC": "C and both individual close deltas strictly negative",
            "official_exact_guard_seconds": 60,
            "proxy_guard_seconds": 900,
        },
        "policy_clock": {
            "policy_anchor": (
                "timestamped exchange schedule observed at decision time"
            ),
            "evaluation_real_start_access": False,
            "schedule_only_positive_proof": False,
            "statistical_tdeep_is_hard_gate": False,
        },
        "external_inputs": {
            "event_ledger": event_receipt,
            "market_cache_aggregate": cache_aggregate,
            "market_cache_files": cache_files,
        },
        "source_and_contract_receipts": source_receipts,
        "bound_git_data_receipts": data_receipts,
        "artifact_receipts": artifact_receipts,
        "candidate_event_stream_receipts": stream_receipts,
        "candidate_event_stream_receipts_sha256": stream_receipt_hash,
        "capability_build_command": (
            "python -B arb-executor/analysis/"
            "window1_round3_prerun_builder.py --repo . "
            "--events ..\\OMI-Window1-private\\joined\\events.jsonl "
            "--market-cache ..\\OMI-Window1-private\\fit-local\\"
            "guarded-cache-v3 --output-dir .claude\\"
            "window1_round3_prerun_20260725 --workers 4"
        ),
        "forensic_build_command": (
            "python -B arb-executor/analysis/"
            "window1_round3_starvation_forensic.py --repo . "
            "--output-dir .claude\\window1_round3_forensic_20260725"
        ),
        "execution_id": None,
        "benchmark_execution_command": None,
        "benchmark_execution_authorized": False,
        "candidate_scoring_performed": False,
        "performance_metrics_computed": False,
        "ranking_performed": False,
        "tuning_performed": False,
        "ablation_performed": False,
        "holdout_dates": ["2026-07-24", "2026-07-25", "2026-07-26"],
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
        "prohibited_surface_changes": False,
    }


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze the score-free Round-3 PRE-RUN."
    )
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output if args.output.is_absolute()
        else repo / args.output
    )
    if output.exists():
        raise FreezeError("PRE-RUN manifest already exists")
    manifest = build(repo)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
