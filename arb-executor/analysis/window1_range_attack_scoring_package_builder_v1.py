#!/usr/bin/env python3
"""Deterministically build the unexecuted Range-Attack scoring package."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping


IMPLEMENTATION_PARENT = "851346343eecbff64bd836992876592784874c86"
CONTROLLING_PASS_AUDIT = "5579b93774267779ae916eb9cb46766de66a9efe"
AUDIT_REPORT_PATH = (
    ".claude/audit_20260726_window1_range_attack_v2_strict_ask/"
    "AUDIT_REPORT.md"
)
AUDIT_CENSUS_PATH = (
    ".claude/audit_20260726_window1_range_attack_v2_strict_ask/"
    "CAUSAL_VS_GUARDED_STRICT_ASK_CENSUS.json"
)
PACKAGE_REL = (
    ".claude/window1_range_attack_scoring_package_prerun_20260726"
)
EXECUTION_ID = "w1-range-attack-v2-dev-20260712-20260720-grid1"
RESULTS_DIRECTORY = (
    ".claude/window1_range_attack_results_"
    "w1-range-attack-v2-dev-20260712-20260720-grid1"
)
CANDIDATES = [
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
]
DEVELOPMENT_DATES = [
    f"2026-07-{day:02d}" for day in range(12, 21)
]
SEALED_DATES = [
    f"2026-07-{day:02d}" for day in range(24, 27)
]
SOURCE_PATHS = [
    "arb-executor/analysis/window1_range_attack_guarded_fill_adapter_v1.py",
    "arb-executor/analysis/window1_range_attack_reference_adapter_v1.py",
    "arb-executor/analysis/window1_range_attack_scorer_v1.py",
    "arb-executor/analysis/window1_range_attack_scoring_runner_v1.py",
    "arb-executor/analysis/window1_range_attack_scoring_package_builder_v1.py",
    "arb-executor/analysis/window1_range_attack_scoring_package_freeze_v1.py",
    "arb-executor/docs/research/window1/WINDOW1_RANGE_ATTACK_SCORER_CONTRACT_V1.json",
    "arb-executor/tests/test_window1_range_attack_scoring_package_v1.py",
]
FROZEN_INPUT_PATHS = [
    "arb-executor/docs/research/window1/WINDOW1_RANGE_ATTACK_CANDIDATES_V2_STRICT_ASK.json",
    "arb-executor/docs/research/window1/WINDOW1_OS_FAMILY_METRIC_CONTRACT_V1.json",
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/PRICE_FILLABILITY_RECEIPTS.jsonl.gz",
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/WINDOW1_RANGE_ATTACK_V2_PRE_RUN_MANIFEST.json",
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/ARTIFACT_HASH_MANIFEST.json",
    ".claude/window1_round2_prerun_v2_20260724/ROUND2_DATA_BINDING_MANIFEST.json",
    ".claude/window1_round2_final_prerun_20260724/GUARDED_CUTOFF_PROVENANCE.json",
    ".claude/window1_start_guard_corrected_20260724/REAL_START_LEDGER_V5.jsonl",
]


class PackageBuildError(RuntimeError):
    """Raised when a frozen source receipt cannot be reproduced."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode:
        raise PackageBuildError(
            f"git {' '.join(args)} failed: {process.stderr.strip()}"
        )
    return process.stdout.strip()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def source_row(repo: Path, relative: str) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise PackageBuildError(f"missing source: {relative}")
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "git_blob_oid": git(repo, "hash-object", str(path)),
    }


def audit_blob(repo: Path, relative: str) -> dict[str, Any]:
    oid = git(
        repo, "rev-parse", f"{CONTROLLING_PASS_AUDIT}:{relative}"
    )
    raw = subprocess.run(
        ["git", "cat-file", "blob", oid],
        cwd=repo,
        check=True,
        capture_output=True,
    ).stdout
    return {
        "audit_commit": CONTROLLING_PASS_AUDIT,
        "path": relative,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_oid": oid,
    }


def _event_leg_identities(repo: Path) -> list[dict[str, Any]]:
    path = repo / (
        ".claude/window1_start_guard_corrected_20260724/"
        "REAL_START_LEDGER_V5.jsonl"
    )
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            boundary = json.loads(line)
            for leg in boundary.get("legs") or []:
                rows.append({
                    "event_id": str(boundary["event_id"]),
                    "event_date": str(boundary["event_date"]),
                    "category": str(boundary["category"]),
                    "leg_id": str(leg["leg"]),
                    "ticker": str(leg["ticker"]),
                })
    rows.sort(key=lambda row: (
        row["event_id"], row["leg_id"], row["ticker"]
    ))
    if len(rows) != 1608 or len({
        (row["event_id"], row["leg_id"]) for row in rows
    }) != 1608:
        raise PackageBuildError("V5 ledger does not conserve 1,608 legs")
    if len({row["event_id"] for row in rows}) != 804:
        raise PackageBuildError("V5 ledger does not conserve D=804")
    if {row["event_date"] for row in rows} - set(DEVELOPMENT_DATES):
        raise PackageBuildError("V5 ledger contains an outside date")
    return rows


def _fill_source_census(repo: Path) -> dict[str, Any]:
    path = repo / FROZEN_INPUT_PATHS[2]
    rows = 0
    fillable = 0
    evidence = {"PRICE_REACHED": 0, "STRICT_ASK_CERTAIN_FILL": 0}
    boundary_unprovable_fillable = 0
    after_right_fillable = 0
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            rows += 1
            if row.get("FILLABLE_AT_X") is not True:
                continue
            fillable += 1
            kind = str(row.get("FILLABLE_AT_X_evidence_type") or "")
            if kind not in evidence:
                raise PackageBuildError("unsupported guarded fill type")
            evidence[kind] += 1
            boundary = row.get("boundary") or {}
            if boundary.get("positive_window1_provable") is not True:
                boundary_unprovable_fillable += 1
            proof = row.get("FILLABLE_AT_X_evidence") or {}
            if float(proof.get("ts") or 0) > float(
                row.get("evaluated_right_ts") or 0
            ) + 1e-6:
                after_right_fillable += 1
    if evidence["STRICT_ASK_CERTAIN_FILL"] != 26:
        raise PackageBuildError("guarded strict-ask census changed from 26")
    if boundary_unprovable_fillable or after_right_fillable:
        raise PackageBuildError("unguarded fillability leaked into source")
    return {
        "rows": rows,
        "fillable_rows": fillable,
        "evidence_type_counts": evidence,
        "boundary_unprovable_fillable_rows": boundary_unprovable_fillable,
        "after_evaluated_right_fillable_rows": after_right_fillable,
        "raw_causal_strict_ask_action_count": 362,
        "guarded_strict_ask_rows_eligible": 26,
        "after_right_strict_ask_actions_ineligible": 283,
        "boundary_unprovable_strict_ask_actions_ineligible": 53,
    }


def build(repo: Path, output: Path) -> list[str]:
    if output.exists() and any(output.iterdir()):
        raise PackageBuildError("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    head = git(repo, "rev-parse", "HEAD")
    if head != IMPLEMENTATION_PARENT and git(
        repo, "rev-parse", "HEAD^"
    ) != IMPLEMENTATION_PARENT:
        raise PackageBuildError(
            "builder must run from the exact parent or its sole package child"
        )
    spec = read_json(repo / FROZEN_INPUT_PATHS[0])
    if spec.get("candidate_ids") != CANDIDATES:
        raise PackageBuildError("V2 candidate order changed")
    if spec.get("D") != 804 or spec.get("performance_metrics") != {
        "C": None, "PC": None, "S": None, "IC": None
    }:
        raise PackageBuildError("V2 population/null-metric law changed")
    metric = read_json(repo / FROZEN_INPUT_PATHS[1])
    if (
        metric.get("D") != 804
        or metric.get("target_count") != 603
        or "negative combined" not in metric["definitions"]["PC"]
        or "below 100" not in metric["definitions"]["S"]
    ):
        raise PackageBuildError("authoritative metric contract changed")
    data_manifest = read_json(repo / FROZEN_INPUT_PATHS[5])
    cache = data_manifest["input_records"]["per_leg_market_streams"]
    event_input = data_manifest["input_records"]["immutable_event_ledger"]
    cache_files = cache["event_file_receipts"]
    if len(cache_files) != 804:
        raise PackageBuildError("guarded-cache hash set changed")

    identities = _event_leg_identities(repo)
    identity_receipt = {
        "schema_version": "window1-range-attack-event-leg-identities-v1",
        "D": 804,
        "leg_identities": 1608,
        "development_dates": DEVELOPMENT_DATES,
        "sealed_holdout_dates": SEALED_DATES,
        "rows": identities,
        "rows_canonical_sha256": canonical_sha256(identities),
    }
    write_json(output / "FROZEN_EVENT_LEG_IDENTITIES.json", identity_receipt)

    cache_hash_set = {
        "schema_version": "window1-guarded-cache-v3-hash-set-v1",
        "cache_version": cache["cache_version"],
        "cache_key": cache["cache_key"],
        "aggregate_sha256": cache["content_sha256"],
        "bytes": cache["bytes"],
        "event_count": 804,
        "ticker_count": 1608,
        "date_range": cache["date_range"],
        "holdout_dates_present": cache["holdout_dates_present"],
        "event_files": cache_files,
        "event_files_canonical_sha256": canonical_sha256(cache_files),
    }
    write_json(output / "GUARDED_CACHE_V3_HASH_SET.json", cache_hash_set)

    fill_census = _fill_source_census(repo)
    fill_receipt = {
        "schema_version": "window1-range-attack-guarded-fill-source-v1",
        "sole_scoring_fill_source": FROZEN_INPUT_PATHS[2],
        "source": source_row(repo, FROZEN_INPUT_PATHS[2]),
        "guarded_census": fill_census,
        "accepted_evidence_types": [
            "PRICE_REACHED", "STRICT_ASK_CERTAIN_FILL"
        ],
        "raw_causal_policy_state_is_a_role": False,
        "candidate_order_stream_is_a_role": False,
        "all_362_causal_strict_ask_actions_countable": False,
        "only_26_guarded_strict_ask_receipts_countable": True,
        "metrics": None,
        "scored": False,
    }
    write_json(output / "GUARDED_FILL_SOURCE_RECEIPT.json", fill_receipt)

    reference_receipt = {
        "schema_version": "window1-range-attack-reference-source-v1",
        "reference_law_source": source_row(repo, FROZEN_INPUT_PATHS[1]),
        "start_ledger": source_row(repo, FROZEN_INPUT_PATHS[7]),
        "guarded_cutoff_provenance": source_row(repo, FROZEN_INPUT_PATHS[6]),
        "data_binding_manifest": source_row(repo, FROZEN_INPUT_PATHS[5]),
        "true_print_streams": {
            "path": "../OMI-Window1-private/fit-local/guarded-cache-v3",
            "aggregate_sha256": cache["content_sha256"],
            "bytes": cache["bytes"],
            "event_files": 804,
            "positive_size_print_rows": cache["counts"][
                "positive_size_print_rows"
            ],
            "hash_set": (
                f"{PACKAGE_REL}/GUARDED_CACHE_V3_HASH_SET.json"
            ),
        },
        "derivation": (
            "last positive-size exchange-identified deduplicated true print "
            "at or before V5 guarded cutoff and at or after T-8h"
        ),
        "precomputed_reference_values_accepted": False,
        "schedule_as_reference_allowed": False,
        "future_print_allowed": False,
        "metrics": None,
        "scored": False,
    }
    write_json(output / "REFERENCE_SOURCE_RECEIPT.json", reference_receipt)

    output_schema = {
        "schema_version": "window1-range-attack-expected-output-schema-v1",
        "candidate_event_rows": 1608,
        "row_required_fields": [
            "candidate_id", "event_id", "event_date", "category", "legs",
            "boundary_status", "boundary_source_class", "guarded_cutoff_ts",
            "boundary_guard_id", "boundary_guard_seconds",
            "combined_entry_cost_cents", "combined_delta_cents",
            "individual_deltas_cents", "C", "PC", "S", "IC",
            "classification", "censor_or_error_reason",
        ],
        "leg_required_fields": [
            "leg_id", "ticker", "fillable", "evidence_type",
            "evidence_receipt", "evidence_timestamp",
            "accounting_fill_price_cents", "accounting_quantity",
            "window1_close_cents", "reference_timestamp",
            "reference_receipt", "individual_delta_cents",
        ],
        "aggregate_required": [
            "D", "C", "PC", "S", "IC", "PC_over_D", "PC_over_C",
            "C_over_D", "S_over_C", "IC_over_D", "IC_over_C",
            "PC_shortfall_from_603", "fill_evidence_decomposition",
            "completed_pair_decomposition", "distributions",
            "by_date", "by_category", "by_boundary_source_class",
            "naked_single", "no_fill", "censored", "reference_missing",
        ],
        "ranking_or_selection_allowed": False,
    }
    write_json(output / "EXPECTED_OUTPUT_SCHEMA.json", output_schema)

    gate = {
        "schema_version": "window1-range-attack-execution-gate-v1",
        "execution_authorized_now": False,
        "future_independent_PASS_audit_required": True,
        "future_audit_must_bind": [
            "exact package commit SHA",
            "execution ID",
            "input-bundle SHA-256",
            "exact execution command",
        ],
        "execution_id": EXECUTION_ID,
        "results_directory": RESULTS_DIRECTORY,
        "one_attempt_only": True,
        "retry_or_resume_allowed": False,
        "command_template": (
            "python -B arb-executor/analysis/"
            "window1_range_attack_scoring_runner_v1.py --repo . --package "
            f"{PACKAGE_REL}/SCORING_INPUT_MANIFEST.json --mode execute "
            "--authorization-commit {FUTURE_PASS_AUDIT_SHA} "
            "--authorization-report {FUTURE_AUDIT_REPORT_PATH}"
        ),
        "real_execution_invoked": False,
    }
    write_json(output / "EXECUTION_AUTHORIZATION_GATE.json", gate)

    committed_inputs = [
        source_row(repo, relative)
        for relative in SOURCE_PATHS + FROZEN_INPUT_PATHS
    ]
    audit_rows = [
        audit_blob(repo, AUDIT_REPORT_PATH),
        audit_blob(repo, AUDIT_CENSUS_PATH),
    ]
    private_inputs = [
        {
            "role": "immutable_event_ledger",
            "path": "../OMI-Window1-private/joined/events.jsonl",
            "bytes": event_input["bytes"],
            "sha256": event_input["content_sha256"],
            "events": 804,
            "tickers": 1608,
            "date_range": event_input["date_range"],
            "holdout_dates_present": 0,
        },
        {
            "role": "guarded_cache_v3_directory",
            "path": "../OMI-Window1-private/fit-local/guarded-cache-v3",
            "bytes": cache["bytes"],
            "sha256": cache["content_sha256"],
            "events": 804,
            "tickers": 1608,
            "date_range": cache["date_range"],
            "holdout_dates_present": 0,
            "per_file_hash_set": (
                f"{PACKAGE_REL}/GUARDED_CACHE_V3_HASH_SET.json"
            ),
        },
    ]
    source_manifest = {
        "schema_version": "window1-range-attack-source-hash-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_pass_audit": CONTROLLING_PASS_AUDIT,
        "audit_artifacts": audit_rows,
        "committed_inputs": committed_inputs,
        "private_inputs": private_inputs,
        "guarded_cache_v3_hash_set_sha256": canonical_sha256(cache_hash_set),
        "event_leg_identity_sha256": identity_receipt[
            "rows_canonical_sha256"
        ],
        "holdout_inputs": 0,
    }
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)

    roles = {
        "scorer_contract": (
            "arb-executor/docs/research/window1/"
            "WINDOW1_RANGE_ATTACK_SCORER_CONTRACT_V1.json"
        ),
        "candidate_definitions": FROZEN_INPUT_PATHS[0],
        "metric_contract": FROZEN_INPUT_PATHS[1],
        "guarded_fillability_receipts": FROZEN_INPUT_PATHS[2],
        "start_ledger": FROZEN_INPUT_PATHS[7],
        "data_binding_manifest": FROZEN_INPUT_PATHS[5],
        "event_ledger": "../OMI-Window1-private/joined/events.jsonl",
        "guarded_cache_directory": (
            "../OMI-Window1-private/fit-local/guarded-cache-v3"
        ),
        "event_leg_identities": (
            f"{PACKAGE_REL}/FROZEN_EVENT_LEG_IDENTITIES.json"
        ),
        "guarded_cache_hash_set": (
            f"{PACKAGE_REL}/GUARDED_CACHE_V3_HASH_SET.json"
        ),
        "guarded_fill_source_receipt": (
            f"{PACKAGE_REL}/GUARDED_FILL_SOURCE_RECEIPT.json"
        ),
        "reference_source_receipt": (
            f"{PACKAGE_REL}/REFERENCE_SOURCE_RECEIPT.json"
        ),
        "expected_output_schema": (
            f"{PACKAGE_REL}/EXPECTED_OUTPUT_SCHEMA.json"
        ),
        "authorization_gate": (
            f"{PACKAGE_REL}/EXECUTION_AUTHORIZATION_GATE.json"
        ),
        "source_hash_manifest": (
            f"{PACKAGE_REL}/SOURCE_HASH_MANIFEST.json"
        ),
    }
    bundle_payload = {
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_pass_audit": CONTROLLING_PASS_AUDIT,
        "candidate_ids": CANDIDATES,
        "D": 804,
        "leg_identities": 1608,
        "development_dates": DEVELOPMENT_DATES,
        "sealed_holdout_dates": SEALED_DATES,
        "roles": roles,
        "committed_source_receipts": [
            {
                "path": row["path"],
                "bytes": row["bytes"],
                "sha256": row["sha256"],
                "git_blob_oid": row["git_blob_oid"],
            }
            for row in committed_inputs
        ],
        "private_source_receipts": private_inputs,
        "guarded_cache_event_hash_set_sha256": canonical_sha256(cache_files),
        "event_leg_identities_sha256": identity_receipt[
            "rows_canonical_sha256"
        ],
    }
    package = {
        "schema_version": "window1-range-attack-scoring-input-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_pass_audit": CONTROLLING_PASS_AUDIT,
        "controlling_audit_report_blob_oid": audit_rows[0]["git_blob_oid"],
        "controlling_audit_report_sha256": audit_rows[0]["sha256"],
        "candidate_ids": CANDIDATES,
        "D": 804,
        "target_PC": 603,
        "execution_id": EXECUTION_ID,
        "results_directory": RESULTS_DIRECTORY,
        "roles": roles,
        "input_bundle_payload": bundle_payload,
        "input_bundle_sha256": canonical_sha256(bundle_payload),
        "future_independent_pass_required": True,
        "execution_authorized_now": False,
        "outstanding_audit_note": (
            "Independently verify V2 deterministic regeneration during the "
            "scoring-package audit if no completed audit addendum exists."
        ),
        "forbidden_scoring_roles": [
            "causal_policy_fill_state_by_leg",
            "raw strict_ask_certain_fill actions",
            "candidate order-stream fill state",
            "raw post-cutoff policy actions",
        ],
        "metrics": None,
        "performance": None,
        "scored": False,
    }
    write_json(output / "SCORING_INPUT_MANIFEST.json", package)
    write_json(output / "VALIDATION_ONLY_RECEIPT.json", {
        "schema_version": (
            "window1-range-attack-scoring-package-validation-only-v1"
        ),
        "implementation_parent": IMPLEMENTATION_PARENT,
        "controlling_pass_audit": CONTROLLING_PASS_AUDIT,
        "candidate_ids": CANDIDATES,
        "D": 804,
        "input_bundle_sha256": package["input_bundle_sha256"],
        "complete_grid_dispatch_schema_loaded": True,
        "real_population_loaded": False,
        "fill_adapter_invoked": False,
        "reference_adapter_invoked": False,
        "scorer_invoked": False,
        "execution_authorized": False,
        "future_independent_PASS_required": True,
        "performance_metrics": {
            "C": None, "PC": None, "S": None, "IC": None
        },
        "gate_pass": True,
    })

    no_execution = {
        "schema_version": "window1-range-attack-no-execution-v1",
        "real_population_loaded_by_package_builder": False,
        "scorer_imported_by_package_builder": False,
        "scorer_invoked": False,
        "candidate_performance_calculated": False,
        "benchmark_executed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
        "results_directory_exists": (
            (repo / RESULTS_DIRECTORY).exists()
        ),
        "C": None,
        "PC": None,
        "S": None,
        "IC": None,
        "performance": None,
    }
    if no_execution["results_directory_exists"]:
        raise PackageBuildError("future results directory already exists")
    write_json(output / "NO_EXECUTION_NO_METRICS_RECEIPT.json", no_execution)

    report = f"""# Window-1 Range-Attack scoring package PRE-RUN

This additions-only package freezes a deterministic scorer and execution
surface for the two V2 Range-Attack candidates. It does **not** authorize or
perform development scoring.

- Parent V2 PRE-RUN: `{IMPLEMENTATION_PARENT}`
- Controlling PASS audit: `{CONTROLLING_PASS_AUDIT}`
- Candidates: `{CANDIDATES[0]}`, `{CANDIDATES[1]}`
- D per candidate: 804
- Target PC: 603
- Input-bundle SHA-256: `{package['input_bundle_sha256']}`
- Sole fill source: guarded V2 `PRICE_FILLABILITY_RECEIPTS`
- Guarded strict-ask eligibility: 26; raw causal strict-ask actions are not a role
- Reference: last deduplicated positive true print in `[T-8h, V5 guarded cutoff]`
- Ranking/selection: forbidden
- C / PC / S / IC: null
- Execution: not authorized and not performed

A future execute invocation requires a new independent PASS audit commit that
explicitly binds the package commit, execution ID, bundle hash, and exact
command. The unresolved audit note about independently confirming V2
regeneration is preserved in `SCORING_INPUT_MANIFEST.json`.
"""
    (output / "PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    return sorted(path.name for path in output.iterdir())


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
    files = build(repo, output)
    print(json.dumps({"files": files}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
