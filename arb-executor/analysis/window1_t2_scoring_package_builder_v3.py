#!/usr/bin/env python3
"""Build the score-free Window-1 T2 execution-readiness package V3."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping

from window1_range_attack_scoring_runner_v1 import _event_legs
from window1_t2_reference_boundary_v3 import (
    NORMALIZED_SHA256,
    RAW_V5_SHA256,
    adapt_frozen_reference_rows,
    canonical_sha256,
    derive_reference_rows,
    iter_gzip,
    read_jsonl,
    reconcile_boundaries,
    sha256_file,
)
from window1_t2_scoring_adapter_v1 import adapt_t2_unique_fill_rows


VERSION = "window1-t2-scoring-package-builder-v3"
IMPLEMENTATION_PARENT = "b73679edc9186eb72236cd1bee5f886ac141cac4"
V2_PACKAGE_COMMIT = "b73679edc9186eb72236cd1bee5f886ac141cac4"
FAILED_RESULTS_COMMIT = "3f8fa0fb372c9e89fa97f89fd26156892745afe1"
CONSUMED_AUTHORIZATION = "e4e57baca0c2172244e63f45b2086f2ef4df53e9"
AUTHORIZATION_PARENT = "3f415f3697b0983925923444f5688ef35865c1bd"
T2_PRERUN = "87ac9382c23b586f536cf457883c507ebf366ba3"
T2_PASS = "8743939745e25f090d69dfd4d56906a93671f331"
V1_PACKAGE = Path(".claude/window1_t2_scoring_package_prerun_20260728")
V2_PACKAGE = Path(".claude/window1_t2_scoring_package_v2_prerun_20260728")
V3_PACKAGE = Path(".claude/window1_t2_scoring_package_v3_prerun_20260728")
RAW_V5 = Path(
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
NORMALIZED = V1_PACKAGE / "GUARDED_BOUNDARY_LEDGER.jsonl"
CONTRACT = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_T2_SCORING_EXECUTION_READINESS_CONTRACT_V3.json"
)
REFERENCE_MODULE = Path(
    "arb-executor/analysis/window1_t2_reference_boundary_v3.py"
)
RUNNER = Path("arb-executor/analysis/window1_t2_scoring_runner_v3.py")
BUILDER = Path(
    "arb-executor/analysis/window1_t2_scoring_package_builder_v3.py"
)
FREEZER = Path(
    "arb-executor/analysis/window1_t2_scoring_package_freeze_v3.py"
)
TEST = Path("arb-executor/tests/test_window1_t2_scoring_package_v3.py")
EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v3"
)
V2_EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v2"
)
RESULTS_DIRECTORY = (
    ".claude/window1_t2_results_" + EXECUTION_ID
)
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
COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/window1_t2_scoring_runner_v3.py "
    f"--repo . --package {V3_PACKAGE.as_posix()}/"
    "SCORING_INPUT_MANIFEST.json --mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
FAILURE_DIR = (
    ".claude/window1_t2_results_"
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v2"
)
FAILURE_HASHES = {
    "EXECUTION_FAILURE.json": (
        "d17d8a3e6119cea681d62d0636d8d93ea2ae75e0a6b3c9877708f2deec5d767e"
    ),
    "EXECUTION_START_RECEIPT.json": (
        "f73c6e4fa4bae8ac71f08b599c84285f173e2141f9fdb16a90b941473d0ff931"
    ),
    "OUTPUT_HASH_MANIFEST.json": (
        "785ce8f15c46a34c5fe2b13768a8cb63421989630c86bff08b84f8e64030d976"
    ),
    "PROGRESS.log": (
        "cdc2dd8f3c99f0549ee4d057d27df1cfecaca132a358478a1394c179930b9a15"
    ),
    "STDERR.log": (
        "208974e1b83651fce6ffff5c8ed022a12d29313090baf71670c381999591f81f"
    ),
}
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}
NULL_FIELDS = {
    "C", "PC", "IC", "S", "frontier", "regret", "performance",
    "ranking", "selection", "result", "results",
}


class BuildError(RuntimeError):
    """The V3 package could not be frozen without scoring."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def gzip_jsonl(rows: Iterable[Mapping[str, Any]]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(
        fileobj=output, mode="wb", filename="", mtime=0
    ) as zipped:
        for row in rows:
            zipped.write((compact(row) + "\n").encode("utf-8"))
    return output.getvalue()


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
        "path": (V3_PACKAGE / path.relative_to(output)).as_posix(),
        "working_tree_bytes": len(raw),
        "identity_bytes": len(identity),
        "sha256": hashlib.sha256(identity).hexdigest(),
        "git_blob_oid": git_blob_oid(identity),
    }


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


def _failure_binding(repo: Path) -> dict[str, Any]:
    if git(repo, "cat-file", "-t", FAILED_RESULTS_COMMIT) != "commit":
        raise BuildError("failed-results commit is not a Git commit")
    if git(repo, "rev-parse", f"{FAILED_RESULTS_COMMIT}^") != V2_PACKAGE_COMMIT:
        raise BuildError("failed-results commit parent changed")
    file_rows = []
    parsed: dict[str, Any] = {}
    for name, expected in FAILURE_HASHES.items():
        path = f"{FAILURE_DIR}/{name}"
        raw = git_show_bytes(repo, FAILED_RESULTS_COMMIT, path)
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected:
            raise BuildError(f"consumed failure hash changed: {name}")
        file_rows.append({
            "path": path,
            "sha256": digest,
            "bytes": len(raw),
            "git_blob_oid": git(repo, "rev-parse", f"{FAILED_RESULTS_COMMIT}:{path}"),
        })
        if name.endswith(".json"):
            parsed[name] = json.loads(raw)
    failure = parsed["EXECUTION_FAILURE.json"]
    start = parsed["EXECUTION_START_RECEIPT.json"]
    if (
        failure.get("exit_code") != 1
        or failure.get("error")
        != "ReferenceError: positive boundary lacks V5 guard artifact"
        or start.get("scorer_invocations") != 0
        or start.get("retry_count") != 0
        or start.get("authorization_commit") != CONSUMED_AUTHORIZATION
        or start.get("execution_id") != V2_EXECUTION_ID
    ):
        raise BuildError("consumed failure semantic identity changed")
    return {
        "schema_version": VERSION + "-consumed-failure-binding-v1",
        "V2_package_commit": V2_PACKAGE_COMMIT,
        "consumed_authorization_commit": CONSUMED_AUTHORIZATION,
        "failed_results_commit": FAILED_RESULTS_COMMIT,
        "failed_results_parent": V2_PACKAGE_COMMIT,
        "invocation_count": 1,
        "retry_count": 0,
        "exit_code": 1,
        "scorer_invocations": 0,
        "error": failure["error"],
        "files": file_rows,
        "output_manifest_sha256": FAILURE_HASHES["OUTPUT_HASH_MANIFEST.json"],
        "failure_receipt_sha256": FAILURE_HASHES["EXECUTION_FAILURE.json"],
        "performance_result_produced": False,
        "selection_or_ranking_performed": False,
        "holdout_opened": False,
        "live_or_trading_access": False,
        "authorization_consumed": True,
        "authorization_reusable": False,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "performance": None,
    }


def _timestamp_discrepancy(repo: Path) -> dict[str, Any]:
    if git(repo, "cat-file", "-t", CONSUMED_AUTHORIZATION) != "commit":
        raise BuildError("consumed authorization is not a Git commit")
    parent = git(repo, "rev-parse", f"{CONSUMED_AUTHORIZATION}^")
    commit_time = git(
        repo, "show", "-s", "--format=%cI", CONSUMED_AUTHORIZATION
    )
    report_path = (
        ".claude/audit_20260729_t2_scoring_package/"
        "ONE_EXECUTION_AUTHORIZATION.md"
    )
    report = git_show_bytes(
        repo, CONSUMED_AUTHORIZATION, report_path
    ).decode("utf-8")
    printed = "Issued: 10:43 PM ET, Tuesday, July 28, 2026"
    if (
        parent != AUTHORIZATION_PARENT
        or commit_time != "2026-07-28T18:44:29-04:00"
        or printed not in report
    ):
        raise BuildError("authorization timestamp evidence changed")
    return {
        "schema_version": VERSION + "-authorization-time-discrepancy-v1",
        "authorization_commit": CONSUMED_AUTHORIZATION,
        "authorization_parent": parent,
        "authorization_report_path": report_path,
        "document_printed_time": "2026-07-28T22:43:00-04:00",
        "document_printed_label": "10:43 PM ET",
        "git_commit_metadata_time": commit_time,
        "execution_started_at_utc": "2026-07-28T22:53:49.591444+00:00",
        "execution_started_at_eastern": "2026-07-28T18:53:49.591444-04:00",
        "authorization_preceded_execution": True,
        "operator_facing_eastern_time_law_satisfied": False,
        "discrepancy": (
            "authorization document printed 10:43 PM ET; Git metadata "
            "records 6:44:29 PM ET and execution began 6:53:49 PM ET"
        ),
        "consumed_authorization_amended": False,
    }


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
            raise BuildError(f"guarded-cache hash mismatch: {row['file']}")
        total += path.stat().st_size
    return {
        "event_file_count": len(rows),
        "total_bytes": total,
        "hash_set_path": hash_set_path.as_posix(),
        "hash_set_sha256": sha256_file(repo / hash_set_path),
        "all_files_verified": True,
    }


def _real_input_readiness(
    *,
    repo: Path,
    references: list[dict[str, Any]],
    cache_verification: Mapping[str, Any],
) -> dict[str, Any]:
    v2 = read_json(repo / V2_PACKAGE / "SCORING_INPUT_MANIFEST.json")
    roles = v2["roles"]
    events = read_jsonl(repo / Path(roles["event_ledger"]))
    expected_legs = _event_legs(events)
    starts = {
        str(row["event_id"]): row
        for row in read_jsonl(repo / NORMALIZED)
    }
    adapted_references = adapt_frozen_reference_rows(
        references,
        expected_legs=expected_legs,
        normalized_boundaries=starts,
    )
    fills = adapt_t2_unique_fill_rows(
        iter_gzip(repo / Path(roles["unique_T2_fill_ledger"])),
        expected_candidates=frozenset(CANDIDATES),
        expected_legs=expected_legs,
    )
    floors = {
        (str(row["event_id"]), str(row["leg_id"])): row
        for row in iter_gzip(
            repo / Path(roles["oracle_leg_floor_ledger"])
        )
    }
    chains = {
        (
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        ): row
        for row in iter_gzip(
            repo / Path(roles["regret_chain_input_ledger"])
        )
    }
    provenance = {
        (
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        ): row
        for row in iter_gzip(
            repo / Path(roles["target_authority_d2_provenance_ledger"])
        )
    }
    expected_candidate_legs = {
        (candidate, event_id, leg_id)
        for candidate in CANDIDATES
        for event_id, leg_id in expected_legs
    }
    fit_post = read_json(repo / Path(roles["fit_postfit_ledger"]))
    claim = read_json(repo / Path(roles["claim_fence_manifest"]))
    required_claim_counts = {
        "BOUND": 12, "PROXIED": 10, "ABSENT": 4, "RETRACTED": 8,
    }
    mechanisms = claim.get("mechanism_status_counts") or claim.get(
        "classification_totals"
    )
    if mechanisms is not None and mechanisms != required_claim_counts:
        raise BuildError("claim-fence mechanism counts changed")
    checks = {
        "events": len(events) == 804,
        "event_legs": len(expected_legs) == 1608,
        "boundaries": len(starts) == 804,
        "references": (
            len(adapted_references) == 1608
            and set(adapted_references) == set(expected_legs)
        ),
        "floors": len(floors) == 1608 and set(floors) == set(expected_legs),
        "regret_chains": (
            len(chains) == 12_864
            and set(chains) == expected_candidate_legs
        ),
        "authority_d2": (
            len(provenance) == 4_170
            and set(provenance).issubset(expected_candidate_legs)
            and set(provenance).issubset(set(chains))
        ),
        "fit_postfit": (
            len(fit_post["rows"]) == 804
            and sum(row["slice"] == "fit" for row in fit_post["rows"]) == 525
            and sum(
                row["slice"] == "post_fit" for row in fit_post["rows"]
            ) == 279
        ),
        "private_hashes": cache_verification["all_files_verified"] is True,
        "results_directory_absent": not (repo / RESULTS_DIRECTORY).exists(),
    }
    if not all(checks.values()):
        raise BuildError(
            "execution-readiness join failure: "
            + ",".join(name for name, ok in checks.items() if not ok)
        )
    if any(
        row.get("metrics") is not None or row.get("performance") is not None
        for row in list(chains.values()) + list(provenance.values())
    ):
        raise BuildError("real preflight input contains populated metrics")
    first_event = str(events[0]["event_id"])
    if first_event != "KXATPCHALLENGERMATCH-26JUL12ALVVAN":
        raise BuildError("first V2 failure event identity changed")
    return {
        "schema_version": VERSION + "-execution-readiness-no-score-v1",
        "execution_id": EXECUTION_ID,
        "real_development_population_loaded": True,
        "pre_scorer_stages_completed": [
            "package_identity_inputs",
            "private_guarded_cache_hashes",
            "event_identity_adapter",
            "raw_v5_boundary_compatibility",
            "unique_guarded_fill_adapter",
            "oracle_floor_adapter",
            "frozen_reference_adapter",
            "regret_chain_adapter",
            "authority_d2_adapter",
            "fit_postfit_membership",
            "claim_fences",
            "null_result_fields",
            "results_directory_absence",
        ],
        "first_v2_failure_event": first_event,
        "first_v2_failure_event_reference_legs_validated": 2,
        "event_rows": len(events),
        "event_leg_keys_joined": len(expected_legs),
        "candidate_event_leg_keys_joined": len(expected_candidate_legs),
        "boundary_rows_validated": len(starts),
        "reference_rows_derived_and_validated": len(adapted_references),
        "fill_rows_validated": len(fills),
        "floor_rows_validated": len(floors),
        "regret_chain_rows_validated": len(chains),
        "authority_d2_rows_validated": len(provenance),
        "authority_d2_rows_are_lawful_subset": True,
        "fit_rows": 525,
        "post_fit_rows": 279,
        "private_cache_files_hash_verified": 804,
        "every_expected_key_joined": True,
        "reference_derivation_whole_population_completed": True,
        "scorer_boundary_reached": True,
        "scorer_invocations": 0,
        "results_directory_created": False,
        "result_fields_null": True,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "frontier": None,
        "regret": None,
        "performance": None,
        "ranking": None,
        "selection": None,
        "holdout_opened": False,
        "live_or_production_access": False,
        "network_or_trading_access": False,
        "gate_pass": True,
    }


def _expected_schema() -> dict[str, Any]:
    return {
        "schema_version": "window1-t2-scoring-output-schema-v3",
        "execution_id": EXECUTION_ID,
        "candidate_count": 8,
        "candidate_ids": list(CANDIDATES),
        "D_per_candidate": 804,
        "reference_input": {
            "role": "frozen_reference_ledger",
            "schema": "window1-close-reference-ledger-v3",
            "runtime_raw_v5_derivation": False,
            "normalized_boundary_passed_to_raw_adapter": False,
        },
        "performance_outputs": {
            "C": None, "PC": None, "IC": None, "S": None,
            "frontier": None, "regret": None, "performance": None,
            "ranking": None, "selection": None,
        },
        "output_files_after_future_authorized_execution": [
            "EXECUTION_START_RECEIPT.json",
            "T2_EVENT_RESULTS.jsonl.gz",
            "T2_CANDIDATE_SUMMARY.json",
            "OUTPUT_HASH_MANIFEST.json",
            "PROGRESS.log",
            "FORBIDDEN_ACCESS_RECEIPT.json",
        ],
    }


def _blind_audit_instruction() -> str:
    return """# Independent V3 PRE-RUN audit instruction

Audit the score-free Window-1 T2 scoring-package V3 as a blind,
execution-readiness repair. Do not run the scorer and do not authorize it.

1. Hash and parse the raw V5 boundary ledger before opening any V3 expected
   summary. Independently derive `boundary_contract(raw)` and
   `guarded_cutoff(raw)` for all 804 events.
2. Independently derive all 1,608 Window-1-close references from the full raw
   V5 rows and guarded-cache true prints using the audited V2 reference law.
   Freeze your counts, hashes, mismatch identities, availability, tie, and
   ambiguity census before opening V3 compatibility/reference summaries.
3. Independently run the real-input path only through the boundary immediately
   before the first scorer call. Require zero scorer invocations and no results
   directory.
4. Only after the independent receipt is immutable, compare it with
   `REFERENCE_BOUNDARY_COMPATIBILITY_RECEIPT.json`,
   `REFERENCE_LEDGER_CENSUS.json`, and
   `EXECUTION_READINESS_NO_SCORE_RECEIPT.json`.
5. Any mismatch is BLOCK. Do not reconcile post hoc to an expected value.
6. Verify the V2 failure binding, the Eastern-time discrepancy, rejection of
   the consumed authorization/execution ID, additions-only lineage, two-build
   determinism, null metrics, sealed holdout, and forbidden-access claims.

Return PASS or BLOCK. A PASS is package-readiness evidence only; execution
still requires a new separately bound one-use authorization.
"""


def _pre_run_report(
    reference_census: Mapping[str, Any],
    compatibility: Mapping[str, Any],
    readiness: Mapping[str, Any],
) -> str:
    return f"""# Window-1 T2 scoring-package V3 PRE-RUN

Status: **SCORE-FREE / NOT AUTHORIZED / NOT EXECUTED**

V3 preserves every V1/V2 package byte and repairs only the execution-readiness
boundary/reference path that consumed the V2 authorization. The recorded V2
attempt remains immutable at `{FAILED_RESULTS_COMMIT}`: one invocation, zero
retries, exit code 1, zero scorer invocations, and
`ReferenceError: positive boundary lacks V5 guard artifact`.

## Repair

- Raw V5 ledger: `{RAW_V5_SHA256}`.
- Derived normalized boundary: `{NORMALIZED_SHA256}`.
- Raw/normalized events reconciled: {compatibility['events_compared']}.
- Compatibility mismatches: {compatibility['field_mismatch_count']}.
- Frozen event-leg references: {reference_census['event_leg_row_count']}.
- Available references: {reference_census['available_count']}.
- Unavailable references: {reference_census['unavailable_count']}.
- Differing-price latest-timestamp ambiguities:
  {reference_census['latest_timestamp_differing_price_ambiguity_count']}.

The future runner consumes only the strict frozen-reference adapter. It never
passes the flattened normalized boundary to the raw V5 reference adapter.

## Real-input no-score readiness

- Events: {readiness['event_rows']}.
- Event-leg joins: {readiness['event_leg_keys_joined']}.
- Candidate-event-leg joins:
  {readiness['candidate_event_leg_keys_joined']}.
- First formerly failing event validated:
  `{readiness['first_v2_failure_event']}`.
- Scorer boundary reached: {str(readiness['scorer_boundary_reached']).lower()}.
- Scorer invocations: 0.
- Results directory created: false.

All C/PC/IC/S, frontier, regret, performance, ranking, and selection fields
remain null. July 24-26 stayed sealed. No live, production, network, order,
position, exit, settlement, DCA, deployment, scoring, tuning, selection, or
authorization action occurred.
"""


def build(*, repo: Path, output: Path) -> dict[str, Any]:
    repo = repo.resolve()
    if output.exists():
        raise BuildError("V3 output already exists")
    if git(repo, "rev-parse", "HEAD") != IMPLEMENTATION_PARENT:
        raise BuildError("V3 build HEAD differs from exact parent")
    if sha256_file(repo / RAW_V5) != RAW_V5_SHA256:
        raise BuildError("raw V5 hash differs from frozen identity")
    if sha256_file(repo / NORMALIZED) != NORMALIZED_SHA256:
        raise BuildError("normalized boundary hash differs from frozen identity")
    output.mkdir(parents=True)

    compatibility = reconcile_boundaries(repo / RAW_V5, repo / NORMALIZED)
    v2_manifest = read_json(
        repo / V2_PACKAGE / "SCORING_INPUT_MANIFEST.json"
    )
    events = read_jsonl(
        repo / Path(v2_manifest["roles"]["event_ledger"])
    )
    raw_boundaries = read_jsonl(repo / RAW_V5)
    cache_root = (repo / Path(
        v2_manifest["roles"]["guarded_cache_directory"]
    )).resolve()
    hash_set_path = Path(
        v2_manifest["roles"]["guarded_cache_hash_set"]
    )
    cache_verification = _verify_private_cache(
        repo, cache_root, hash_set_path
    )
    references, reference_census = derive_reference_rows(
        events=events,
        raw_boundaries=raw_boundaries,
        cache_root=cache_root,
    )
    readiness = _real_input_readiness(
        repo=repo,
        references=references,
        cache_verification=cache_verification,
    )
    failure = _failure_binding(repo)
    timestamp = _timestamp_discrepancy(repo)

    (output / "FROZEN_WINDOW1_CLOSE_REFERENCE_LEDGER.jsonl.gz").write_bytes(
        gzip_jsonl(references)
    )
    write_json(
        output / "REFERENCE_BOUNDARY_COMPATIBILITY_RECEIPT.json",
        compatibility,
    )
    write_json(output / "REFERENCE_LEDGER_CENSUS.json", reference_census)
    write_json(
        output / "EXECUTION_READINESS_NO_SCORE_RECEIPT.json", readiness
    )
    write_json(output / "CONSUMED_V2_FAILURE_BINDING.json", failure)
    write_json(
        output / "AUTHORIZATION_TIMESTAMP_DISCREPANCY_RECEIPT.json",
        timestamp,
    )
    write_json(output / "EXPECTED_OUTPUT_SCHEMA_V3.json", _expected_schema())
    (output / "INDEPENDENT_AUDIT_INSTRUCTION.md").write_text(
        _blind_audit_instruction(), encoding="utf-8", newline="\n"
    )
    (output / "PRE_RUN_REPORT.md").write_text(
        _pre_run_report(reference_census, compatibility, readiness),
        encoding="utf-8",
        newline="\n",
    )
    write_json(output / "FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden-access-v1",
        "scorer_imported_by_builder": False,
        "scorer_invocations": 0,
        "results_directory_created": False,
        "holdout_dates_opened": [],
        "live_or_production_access": False,
        "network_or_trading_access": False,
        "order_or_position_access": False,
        "exit_settlement_DCA_or_Window2_access": False,
        "tuning_ranking_selection_or_authorization": False,
        "C": None, "PC": None, "IC": None, "S": None,
        "performance": None,
    })
    write_json(output / "V1_V2_BYTE_IDENTITY_RECEIPT.json", {
        "schema_version": VERSION + "-inherited-byte-identity-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "V1_package_path": V1_PACKAGE.as_posix(),
        "V2_package_path": V2_PACKAGE.as_posix(),
        "inherited_files_modified": 0,
        "inherited_files_deleted": 0,
        "V3_additions_only": True,
        "V2_failure_commit_separate_from_V3_parent": True,
    })

    inherited_sources = [
        (
            Path("arb-executor/analysis/window1_range_attack_reference_adapter_v1.py"),
            "raw_V5_guarded_cutoff_law",
        ),
        (
            Path("arb-executor/analysis/window1_range_attack_reference_adapter_v2.py"),
            "audited_sequence_honest_reference_law",
        ),
        (
            Path("arb-executor/analysis/window1_t2_scoring_adapter_v1.py"),
            "audited_exact_integer_fill_adapter",
        ),
        (
            Path("arb-executor/analysis/window1_t2_frontier_regret_scorer_v1.py"),
            "frozen_T2_scorer",
        ),
        (
            Path("arb-executor/analysis/window1_t2_scoring_correction_v2.py"),
            "frozen_V2_authority_d2_correction",
        ),
    ]
    v3_sources = [
        (REFERENCE_MODULE, "V3_boundary_reference_adapter"),
        (RUNNER, "V3_stdout_safe_runner"),
        (BUILDER, "V3_package_builder"),
        (FREEZER, "V3_two_clean_build_freezer"),
        (TEST, "V3_tests"),
        (CONTRACT, "V3_execution_readiness_contract"),
    ]
    committed_sources = [
        source_identity(repo, path, role)
        for path, role in inherited_sources + v3_sources
    ]
    inherited_binary_roles = dict(v2_manifest["roles"])
    inherited_binary_roles.pop("guarded_cache_directory", None)
    binary_rows = [
        binary_identity(repo, RAW_V5, "full_raw_V5_boundary_ledger"),
        binary_identity(repo, NORMALIZED, "normalized_boundary_contract"),
    ]
    for role, path_value in sorted(inherited_binary_roles.items()):
        path = Path(path_value)
        if path in (RAW_V5, NORMALIZED):
            continue
        binary_rows.append(binary_identity(repo, path, f"inherited_{role}"))
    prior_source = read_json(
        repo / V2_PACKAGE / "SOURCE_HASH_MANIFEST.json"
    )
    source_manifest = {
        "schema_version": VERSION + "-source-hash-manifest-v1",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "T2_prerun": T2_PRERUN,
        "T2_independent_PASS": T2_PASS,
        "V2_package_commit": V2_PACKAGE_COMMIT,
        "consumed_failure_commit": FAILED_RESULTS_COMMIT,
        "committed_source_inputs": committed_sources,
        "frozen_binary_inputs": binary_rows,
        "private_runtime_inputs": prior_source["private_runtime_inputs"],
        "private_cache_verification": cache_verification,
        "holdout_opened": False,
        "live_or_production_access": False,
        "scorer_invocations": 0,
    }
    write_json(output / "SOURCE_HASH_MANIFEST.json", source_manifest)

    roles = dict(v2_manifest["roles"])
    roles.update({
        "raw_v5_boundary_ledger": RAW_V5.as_posix(),
        "normalized_boundary_ledger": NORMALIZED.as_posix(),
        "start_ledger": NORMALIZED.as_posix(),
        "frozen_reference_ledger": (
            V3_PACKAGE / "FROZEN_WINDOW1_CLOSE_REFERENCE_LEDGER.jsonl.gz"
        ).as_posix(),
        "reference_boundary_compatibility_receipt": (
            V3_PACKAGE / "REFERENCE_BOUNDARY_COMPATIBILITY_RECEIPT.json"
        ).as_posix(),
        "reference_ledger_census": (
            V3_PACKAGE / "REFERENCE_LEDGER_CENSUS.json"
        ).as_posix(),
        "execution_readiness_no_score_receipt": (
            V3_PACKAGE / "EXECUTION_READINESS_NO_SCORE_RECEIPT.json"
        ).as_posix(),
        "consumed_v2_failure_binding": (
            V3_PACKAGE / "CONSUMED_V2_FAILURE_BINDING.json"
        ).as_posix(),
        "authorization_timestamp_discrepancy": (
            V3_PACKAGE / "AUTHORIZATION_TIMESTAMP_DISCREPANCY_RECEIPT.json"
        ).as_posix(),
        "expected_output_schema": (
            V3_PACKAGE / "EXPECTED_OUTPUT_SCHEMA_V3.json"
        ).as_posix(),
        "source_hash_manifest": (
            V3_PACKAGE / "SOURCE_HASH_MANIFEST.json"
        ).as_posix(),
        "execution_readiness_contract_v3": CONTRACT.as_posix(),
    })
    critical = {}
    for role, relative in sorted(roles.items()):
        if role == "guarded_cache_directory":
            continue
        path = repo / Path(relative)
        if str(relative).startswith(V3_PACKAGE.as_posix()):
            path = output / Path(relative).relative_to(V3_PACKAGE)
        raw = identity_bytes(path)
        critical[role] = {
            "path": str(relative),
            "identity_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    payload = {
        "schema_version": "window1-t2-scoring-input-bundle-v3",
        "implementation_parent": IMPLEMENTATION_PARENT,
        "T2_prerun": T2_PRERUN,
        "T2_PASS": T2_PASS,
        "controlling_T2_PASS": T2_PASS,
        "audited_scorer_commit": (
            "e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd"
        ),
        "V2_package_commit": V2_PACKAGE_COMMIT,
        "consumed_V2_failure_commit": FAILED_RESULTS_COMMIT,
        "consumed_authorization_rejected": CONSUMED_AUTHORIZATION,
        "execution_id": EXECUTION_ID,
        "D": 804,
        "fit_D": 525,
        "post_fit_D": 279,
        "candidate_ids": list(CANDIDATES),
        "roles": roles,
        "critical_role_identities": critical,
        "command_template_literal": COMMAND_TEMPLATE,
    }
    manifest = {
        **payload,
        "schema_version": "window1-t2-scoring-input-manifest-v3",
        "input_bundle_payload": payload,
        "input_bundle_sha256": canonical_sha256(payload),
        "future_independent_PASS_required": True,
        "future_authorization_required": True,
        "scored": False,
        "C": None, "PC": None, "IC": None, "S": None,
        "frontier": None, "regret": None, "performance": None,
        "ranking": None, "selection": None,
    }
    write_json(output / "SCORING_INPUT_MANIFEST.json", manifest)
    write_json(output / "NULL_METRIC_NO_EXECUTION_RECEIPT.json", {
        "schema_version": VERSION + "-null-no-execution-v1",
        "execution_id": EXECUTION_ID,
        "all_committed_performance_fields_null": True,
        "real_scorer_invocations": 0,
        "results_directory": RESULTS_DIRECTORY,
        "results_directory_exists": False,
        "future_independent_PASS_required": True,
        "future_separate_authorization_required": True,
        "consumed_authorization_rejected": CONSUMED_AUTHORIZATION,
        "C": None, "PC": None, "IC": None, "S": None,
        "frontier": None, "regret": None, "performance": None,
        "ranking": None, "selection": None,
    })

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
        if path.suffix in {".json", ".jsonl"}:
            assert_score_free(read_json(path))
    if (repo / RESULTS_DIRECTORY).exists():
        raise BuildError("V3 results directory exists")
    return {
        "schema_version": VERSION + "-build-receipt-v1",
        "input_bundle_sha256": manifest["input_bundle_sha256"],
        "reference_rows": len(references),
        "reference_available": reference_census["available_count"],
        "reference_unavailable": reference_census["unavailable_count"],
        "boundary_mismatches": compatibility["field_mismatch_count"],
        "real_input_preflight_pass": readiness["gate_pass"],
        "scorer_invocations": 0,
        "file_count": len([path for path in output.iterdir() if path.is_file()]),
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
