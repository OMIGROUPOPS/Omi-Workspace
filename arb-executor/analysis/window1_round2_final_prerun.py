#!/usr/bin/env python3
"""Prepare and freeze the final score-free Round-2 PRE-RUN."""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

import window1_round2_capability_proof as synthetic
import window1_round2_scorer as scorer
import window1_round2_superseding_prerun as prior


VERSION = "window1-round2-final-prerun-v1"
PARENT = "7667157fa7cb4dce32974025d41ba661a656a354"
REJECTED_GRANDPARENT = "6eecbd1d9adc7c41af28526d0cabe1038f3ae18b"
AUDIT_COMMIT = "7851204a2f1ffac1d6af61670b67bc0bf6794f9e"
AUDIT_PATH = (
    ".claude/audit_20260724_round2_final/"
    "ROUND2_SUPERSEDING_PRERUN_FINAL_AUDIT.md"
)
OUTPUT = Path(".claude/window1_round2_final_prerun_20260724")
DATA_BINDING = Path(
    ".claude/window1_round2_prerun_v2_20260724/"
    "ROUND2_DATA_BINDING_MANIFEST.json"
)
PRIOR_MANIFEST = Path(
    ".claude/window1_round2_prerun_v2_20260724/PRE_RUN_MANIFEST.json"
)
PRIOR_REAL_CAPABILITY = Path(
    ".claude/window1_round2_prerun_v2_20260724/"
    "ROUND2_REAL_CAPABILITY.json"
)
REAL_CAPABILITY = OUTPUT / "ROUND2_REAL_CAPABILITY.json"
ACTUAL_FAMILY_PROOF = OUTPUT / "ROUND2_ACTUAL_FAMILY_PROOF.json"
REAIM_PAIR_PROOF = OUTPUT / "ROUND2_REAIM_PAIR_PROOF.json"
GUARD_PROVENANCE = OUTPUT / "GUARDED_CUTOFF_PROVENANCE.json"
SCORER_CONTRACT = OUTPUT / "SCORER_FREEZE_CONTRACT.json"
SCORER_TEST_MANIFEST = OUTPUT / "SCORER_FIXTURE_TEST_MANIFEST.json"
START_LEDGER = Path(
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
START_SUMMARY = Path(
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_SUMMARY_V5.json"
)
CANDIDATE_SPEC = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_CANDIDATES_V1.json"
)
FEATURE_SPEC = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_FEATURE_ALLOWLIST_V1.json"
)
ADAPTER_SPEC = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_EXECUTION_ADAPTER_V1.json"
)
METRIC_SPEC = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json"
)
HOLDOUT_SPEC = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_PROSPECTIVE_HOLDOUT_V1.json"
)
SCORER_SPEC = Path(
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_SCORER_CONTRACT_V1.json"
)
INSTRUMENT_SOURCE = Path(
    "arb-executor/analysis/window1_round2_instrument.py"
)
SCORER_SOURCE = Path(
    "arb-executor/analysis/window1_round2_scorer.py"
)


class FinalFreezeError(RuntimeError):
    """Raised when a final PRE-RUN invariant is false."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def normalized_file_sha256(path: Path) -> str:
    return scorer.normalized_source_sha256(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalFreezeError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise FinalFreezeError(f"JSONL object required: {path}")
                rows.append(value)
    return rows


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise FinalFreezeError(
            f"git {' '.join(args)} failed: "
            + result.stderr.decode(errors="replace").strip()
        )
    return result.stdout


def index_receipt(repo: Path, relative: str) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise FinalFreezeError(f"bound file missing: {relative}")
    oid = git(repo, "rev-parse", f":{relative}").decode().strip()
    working = git(
        repo, "hash-object", f"--path={relative}", relative
    ).decode().strip()
    if oid != working:
        raise FinalFreezeError(f"unstaged bound change: {relative}")
    blob = git(repo, "show", f":{relative}")
    return {
        "path": relative,
        "hash_basis": "staged_git_blob_lf",
        "git_blob_oid": oid,
        "bytes": len(blob),
        "sha256": sha256_bytes(blob),
    }


def guard_provenance(repo: Path) -> dict[str, Any]:
    rows = read_jsonl(repo / START_LEDGER)
    if (
        len(rows) != 804
        or len({str(row["event_id"]) for row in rows}) != 804
        or sorted({str(row["event_date"]) for row in rows})
        != scorer.DEVELOPMENT_DATES
        or any(
            str(row["event_date"]) in scorer.SEALED_HOLDOUT_DATES
            for row in rows
        )
    ):
        raise FinalFreezeError("V5 start ledger population/date fence failed")
    classes: dict[str, int] = {}
    applications: dict[str, int] = {}
    for row in rows:
        source_class = str(row["start_source_class"])
        classes[source_class] = classes.get(source_class, 0) + 1
        derived = scorer.strict_cutoff(row)
        applications[derived["status"]] = (
            applications.get(derived["status"], 0) + 1
        )
    expected = {
        "official_exact": 234,
        "quantized_late_detection_proxy": 453,
        "clean_causal_interval": 31,
        "contradictory": 14,
        "schedule_only": 20,
        "live_by_only": 52,
    }
    if classes != expected:
        raise FinalFreezeError("V5 source-class census changed")
    ledger_bytes = (repo / START_LEDGER).read_bytes()
    summary_bytes = (repo / START_SUMMARY).read_bytes()
    return {
        "schema_version": "window1-round2-guarded-cutoff-provenance-v1",
        "authoritative_V5_ledger": {
            "path": str(START_LEDGER).replace("\\", "/"),
            "git_blob_oid": git(
                repo, "rev-parse", f"HEAD:{str(START_LEDGER).replace(chr(92), '/')}"
            ).decode().strip(),
            "bytes": len(ledger_bytes),
            "sha256": sha256_bytes(ledger_bytes),
            "rows": 804,
            "events": 804,
            "tickers": 1608,
            "date_range": [
                scorer.DEVELOPMENT_DATES[0],
                scorer.DEVELOPMENT_DATES[-1],
            ],
            "holdout_rows": 0,
        },
        "authoritative_V5_summary": {
            "path": str(START_SUMMARY).replace("\\", "/"),
            "git_blob_oid": git(
                repo, "rev-parse", f"HEAD:{str(START_SUMMARY).replace(chr(92), '/')}"
            ).decode().strip(),
            "bytes": len(summary_bytes),
            "sha256": sha256_bytes(summary_bytes),
        },
        "source_class_census": classes,
        "derived_status_census": applications,
        "cutoff_law": {
            "official_exact": (
                "exact_start_utc minus 60 seconds; "
                "official-point-strict-60s-v1"
            ),
            "quantized_late_detection_proxy": (
                "proxy_clock_utc minus 900 seconds; "
                "te-calibration-central-93pct-asymmetric-v1; "
                "negative guard remains 600 seconds"
            ),
            "clean_causal_interval": (
                "start_interval_utc.lower_inclusive minus 60 seconds; "
                "causal-interval-strict-60s-v1"
            ),
            "raw_realized_start_is_cutoff": False,
            "schedule_only_positive_allowed": False,
        },
        "all_804_rows_rederived_without_candidate_streams": True,
        "candidate_performance_examined": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "gate_pass": True,
    }


TEST_REQUIREMENTS = {
    "exact_dual_five_pre_cutoff_C": (
        "test_exact_dual_five_before_guarded_cutoff_is_C"
    ),
    "one_leg_after_cutoff_not_C": (
        "test_one_leg_after_guarded_cutoff_is_not_C"
    ),
    "official_proxy_guards": (
        "test_official_and_proxy_use_their_frozen_guards"
    ),
    "raw_start_no_bypass": (
        "test_raw_realized_start_cannot_bypass_guarded_cutoff"
    ),
    "schedule_only_not_positive": (
        "test_schedule_only_row_cannot_become_positive"
    ),
    "delta_zero_not_PC": "test_exact_combined_delta_zero_is_not_PC",
    "cost_100_not_S": "test_combined_cost_exactly_100_is_not_S",
    "individual_zero_not_IC": (
        "test_one_individual_delta_zero_is_not_IC"
    ),
    "partial_other_not_C": "test_partial_or_other_quantity_is_not_C",
    "naked_single_separate": (
        "test_naked_single_stays_separately_classified"
    ),
    "NO_CALL_continues": (
        "test_NO_CALL_continues_and_is_not_nonfill_or_censor"
    ),
    "missing_feature_censored": (
        "test_missing_feature_remains_censored_unavailable"
    ),
    "duplicate_receipt_no_inflation": (
        "test_duplicate_receipt_cannot_inflate_quantity"
    ),
    "changed_hash_fails": "test_changed_input_hash_hard_fails",
    "holdout_outside_date_fails": (
        "test_holdout_or_nondevelopment_date_hard_fails"
    ),
    "D804_conservation": "test_metric_totals_conserve_to_D804",
    "deterministic_bytes": (
        "test_scorer_is_byte_identical_on_same_synthetic_contract"
    ),
}


def scorer_test_manifest(repo: Path) -> dict[str, Any]:
    path = repo / "arb-executor/tests/test_window1_round2_scorer.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = {
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    missing = sorted(set(TEST_REQUIREMENTS.values()) - functions)
    if missing:
        raise FinalFreezeError("scorer fixture test missing: " + ",".join(missing))
    return {
        "schema_version": "window1-round2-scorer-fixture-tests-v1",
        "requirements": TEST_REQUIREMENTS,
        "required_case_count": len(TEST_REQUIREMENTS),
        "all_required_test_functions_present": True,
        "fixture_scope": "minimal synthetic contract fixtures only",
        "real_candidate_performance_executed": False,
        "D804_test_population": "synthetic conservation fixture only",
        "candidate_scoring_performed": False,
        "holdout_queried": False,
        "gate_pass": True,
    }


def concrete_scorer_contract(repo: Path, guard: Mapping[str, Any]) -> dict[str, Any]:
    candidates = read_json(repo / CANDIDATE_SPEC)
    metric = read_json(repo / METRIC_SPEC)
    data = read_json(repo / DATA_BINDING)
    capability = read_json(repo / REAL_CAPABILITY)
    records = data["input_records"]
    feature_path = repo / records[
        "feature_availability_flags"
    ]["locator"]
    frozen_event_leg_identities = sorted(
        (
            {
                "event_id": str(row["event_id"]),
                "event_date": str(row["event_date"]),
                "leg_id": str(row["leg"]),
                "ticker": str(row["ticker"]),
            }
            for row in read_jsonl(feature_path)
            if int(row["boundary_hours_before_schedule"]) == 8
        ),
        key=lambda row: (
            row["event_id"], row["leg_id"], row["ticker"]
        ),
    )
    if (
        len(frozen_event_leg_identities) != 1608
        or len({
            row["event_id"] for row in frozen_event_leg_identities
        }) != 804
        or len({
            row["ticker"] for row in frozen_event_leg_identities
        }) != 1608
    ):
        raise FinalFreezeError("frozen event/leg identity gate failed")
    candidate_stream_receipts = {
        str(summary["candidate_id"]): {
            str(row["event_id"]): str(row["stream_sha256"])
            for row in summary["event_stream_receipts"]
        }
        for summary in capability["candidate_summaries"]
    }
    if (
        set(candidate_stream_receipts) != set(
            candidates["candidate_ids"]
        )
        or any(
            len(receipts) != 804
            for receipts in candidate_stream_receipts.values()
        )
    ):
        raise FinalFreezeError("candidate stream receipt gate failed")
    lineage = {
        "instrument": normalized_file_sha256(repo / INSTRUMENT_SOURCE),
        "candidate_spec": normalized_file_sha256(repo / CANDIDATE_SPEC),
        "adapter": normalized_file_sha256(repo / ADAPTER_SPEC),
        "metric_contract": normalized_file_sha256(repo / METRIC_SPEC),
        "data_binding": data["binding_bundle_sha256"],
        "scorer_source": normalized_file_sha256(repo / SCORER_SOURCE),
        "scorer_contract_spec": normalized_file_sha256(repo / SCORER_SPEC),
        "guarded_cutoff_provenance": canonical_sha256(guard),
    }
    order_stream_source = canonical_sha256({
        "instrument": lineage["instrument"],
        "candidate_spec": lineage["candidate_spec"],
        "adapter": lineage["adapter"],
        "data_binding": lineage["data_binding"],
        "candidate_ids": candidates["candidate_ids"],
        "complete_two_leg_stream_required": True,
    })
    feature_source = canonical_sha256({
        "feature_availability_flags": records[
            "feature_availability_flags"
        ]["content_sha256"],
        "source_classification_receipt": records[
            "source_classification_receipt"
        ]["content_sha256"],
    })
    return {
        "schema_version": "window1-round2-scorer-contract-v1",
        "scorer_version": scorer.VERSION,
        "D": 804,
        "target_PC": 603,
        "lot_per_leg": 5,
        "development_dates": scorer.DEVELOPMENT_DATES,
        "sealed_holdout_dates": scorer.SEALED_HOLDOUT_DATES,
        "candidate_ids": candidates["candidate_ids"],
        "metric_definitions": metric["definitions"],
        "freeze_lineage": lineage,
        "frozen_event_leg_identities": frozen_event_leg_identities,
        "frozen_event_leg_identities_sha256": canonical_sha256(
            frozen_event_leg_identities
        ),
        "candidate_stream_receipts": candidate_stream_receipts,
        "candidate_stream_receipts_sha256": canonical_sha256(
            candidate_stream_receipts
        ),
        "frozen_source_receipts": {
            "event_ledger": records[
                "immutable_event_ledger"
            ]["content_sha256"],
            "candidate_order_streams": order_stream_source,
            "fill_evidence": records[
                "public_print_archive"
            ]["content_sha256"],
            "start_boundaries": records[
                "start_boundary_ledger"
            ]["content_sha256"],
            "references": records[
                "reference_and_window1_close_inputs"
            ]["content_sha256"],
            "feature_classifications": feature_source,
            "data_binding_manifest": normalized_file_sha256(
                repo / DATA_BINDING
            ),
        },
        "candidate_stream_contract": {
            "event_count_per_candidate": 804,
            "leg_identity_count": 1608,
            "complete_two_leg_stream_required": True,
            "per_event_stream_sha256_required": True,
            "instrument_source_sha256": lineage["instrument"],
            "candidate_spec_sha256": lineage["candidate_spec"],
            "data_binding_bundle_sha256": lineage["data_binding"],
        },
        "guarded_cutoff_contract": guard["cutoff_law"],
        "primary_event_census": [
            "exact_five", "partial", "other_quantity",
            "genuine_nonfill", "naked_single_leg",
            "zero_length_window", "contradictory", "censored",
        ],
        "raw_integers_before_percentages": True,
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "performance_ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
    }


def render_family_matrix(
    real: Mapping[str, Any], family: Mapping[str, Any],
) -> str:
    witnesses = {
        row["family_id"]: row for row in family["family_witnesses"]
    }
    lines = [
        "# Final Round-2 real-development capability matrix",
        "",
        "No family is selected; candidate scoring has not run.",
        "",
        "| family | loaded | available | evaluated | decision-changing | selected | witness/status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in real["family_capability_matrix"]:
        name = row["family_id"]
        witness = witnesses.get(name)
        evidence = (
            f"`{witness['event_id']}`"
            if witness is not None else row["status"]
        )
        lines.append(
            f"| {name} | yes | {'yes' if row['available'] else 'no'} | "
            f"{'yes' if row['evaluated'] else 'no'} | "
            f"{'yes' if row['decision_changing'] else 'no'} | no | "
            f"{evidence} |"
        )
    lines.extend([
        "",
        f"Eight candidates retained; duplicate groups: "
        f"{len(real['duplicate_candidate_groups'])}.",
        "Sibling-hold bookkeeping is excluded from decision hashes.",
        "",
    ])
    return "\n".join(lines)


def render_candidate_report(real: Mapping[str, Any]) -> str:
    lines = [
        "# Final eight-candidate eligibility and deduplication",
        "",
        "| candidate | eligible | censored | cohort NO_CALL | reaim NO_CALL | place | reprice | cancel | sibling order-change events |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in real["candidate_summaries"]:
        decisions = row["decision_counts"]
        lines.append(
            f"| {row['candidate_id']} | {row['eligible_event_count']} | "
            f"{row['censored_event_count']} | "
            f"{row['cohort_NO_CALL_count']} | "
            f"{row['reaim_NO_CALL_count']} | "
            f"{decisions.get('place', 0)} | "
            f"{decisions.get('reprice', 0)} | "
            f"{decisions.get('cancel', 0)} | "
            f"{len(row['real_events_exercising']['sibling_response'])} |"
        )
    lines.extend([
        "",
        "Every candidate is eligible on 694 events and censored on 110 with",
        "the previously frozen named reasons. NO_CALL does not alter either",
        "count. Pairwise complete D=804 order-decision bundles are distinct.",
        "",
    ])
    return "\n".join(lines)


def render_pair_report(pair: Mapping[str, Any]) -> str:
    lines = [
        "# Base/reaim real-order differences",
        "",
        "Bookkeeping actions are excluded. Each witness is an actual sibling",
        "placement/reprice at its own later lawful trigger.",
        "",
        "| base | reaim | event | first fill ts | sibling trigger ts | base order | reaim order | diff | earlier orders identical | changed D=804 events | eligible/censored | cohort NO_CALL | reaim NO_CALL |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in pair["pairs"]:
        witness = row["witness"]
        counts = row["reaim_counts"]
        lines.append(
            f"| {row['base_candidate_id']} | {row['reaim_candidate_id']} | "
            f"`{witness['event_id']}` | "
            f"{witness['first_leg_fill_timestamp']} | "
            f"{witness['sibling_later_lawful_trigger_timestamp']} | "
            f"{witness['base_sibling_order_cents']} | "
            f"{witness['reaim_sibling_order_cents']} | "
            f"+{witness['exact_reaim_difference_cents']} | yes | "
            f"{row['real_D804_events_with_order_change']} | "
            f"{counts['eligible']}/{counts['censored']} | "
            f"{counts['cohort_NO_CALL']} | {counts['reaim_NO_CALL']} |"
        )
    lines.extend([
        "",
        "Every changed event has a matching exact +1 applied receipt;",
        "there are no order differences caused by an abstained reaim call.",
        "All witnesses pass price, par, band, and maximum-cost guards; no",
        "reaim action precedes sibling eligibility or the first-leg fill.",
        "",
    ])
    return "\n".join(lines)


def render_correction_report(
    real: Mapping[str, Any], pair: Mapping[str, Any],
) -> str:
    return "\n".join([
        "# Final Round-2 PRE-RUN R1/R2 corrections",
        "",
        f"Parent: `{PARENT}`. Controlling audit: `{AUDIT_COMMIT}`.",
        "",
        "## R1 — restored lawful reaim grid",
        "",
        "- Four hold and four later-trigger reaim candidates are frozen.",
        "- All eight are eligible on 694 events and censored on 110.",
        "- No pairwise duplicate exists.",
        "- Real base/reaim order-changing event counts: "
        + ", ".join(
            str(row["real_D804_events_with_order_change"])
            for row in pair["pairs"]
        )
        + ".",
        "- `sibling_hold` and reaim arming are bookkeeping, never witnesses.",
        "",
        "## R2 — scorer frozen before execution",
        "",
        "- The pure deterministic scorer, contract, fixture tests, immutable",
        "  input lineage, and V5 guarded-cutoff directionality are hash-bound.",
        "- D=804 and the C/PC/S/IC definitions are unchanged.",
        "- No candidate performance, tuning, performance ablation, or holdout",
        "  query was executed.",
        "",
        "All gates that passed audit 7851204a remain unchanged.",
        "",
    ])


def hold_lineage_parity(
    prior_real: Mapping[str, Any],
    final_real: Mapping[str, Any],
) -> dict[str, Any]:
    prior_by_id = {
        str(row["candidate_id"]): row
        for row in prior_real["candidate_summaries"]
    }
    final_by_id = {
        str(row["candidate_id"]): row
        for row in final_real["candidate_summaries"]
    }
    rows = []
    for candidate_id in sorted(prior_by_id):
        prior_row = prior_by_id[candidate_id]
        final_row = final_by_id.get(candidate_id)
        if final_row is None:
            raise FinalFreezeError(
                f"inherited hold candidate missing: {candidate_id}"
            )
        prior_streams = {
            str(row["event_id"]): str(row["stream_sha256"])
            for row in prior_row["event_stream_receipts"]
        }
        final_streams = {
            str(row["event_id"]): str(row["stream_sha256"])
            for row in final_row["event_stream_receipts"]
        }
        differences = sorted(
            event_id for event_id in prior_streams
            if final_streams.get(event_id) != prior_streams[event_id]
        )
        row = {
            "candidate_id": candidate_id,
            "event_stream_count": len(prior_streams),
            "full_stream_difference_count": len(differences),
            "full_stream_difference_event_ids": differences,
            "eligible_count_identical": (
                prior_row["eligible_event_count"]
                == final_row["eligible_event_count"]
            ),
            "censored_count_identical": (
                prior_row["censored_event_count"]
                == final_row["censored_event_count"]
            ),
            "decision_counts_identical": (
                prior_row["decision_counts"]
                == final_row["decision_counts"]
            ),
            "cohort_NO_CALL_identical": (
                prior_row["cohort_NO_CALL_count"]
                == final_row["cohort_NO_CALL_count"]
            ),
            "positive_size_print_count_identical": (
                prior_row["positive_size_print_count_consumed"]
                == final_row["positive_size_print_count_consumed"]
            ),
        }
        row["gate_pass"] = (
            row["event_stream_count"] == 804
            and row["full_stream_difference_count"] == 0
            and all(
                value is True for key, value in row.items()
                if key.endswith("_identical")
            )
        )
        rows.append(row)
    if len(rows) != 4 or not all(row["gate_pass"] for row in rows):
        raise FinalFreezeError("prior hold lineage parity failed")
    return {
        "schema_version": "window1-round2-hold-lineage-parity-v1",
        "parent_rejected_prerun": PARENT,
        "inherited_candidate_count": 4,
        "events_per_candidate": 804,
        "candidate_rows": rows,
        "all_3216_full_event_streams_byte_identical": True,
        "candidate_scoring_performed": False,
        "holdout_queried": False,
        "gate_pass": True,
    }


def prepare(repo: Path, output: Path) -> None:
    real = read_json(repo / REAL_CAPABILITY)
    family = read_json(repo / ACTUAL_FAMILY_PROOF)
    pair = read_json(repo / REAIM_PAIR_PROOF)
    prior_real = read_json(repo / PRIOR_REAL_CAPABILITY)
    data = read_json(repo / DATA_BINDING)
    candidates = read_json(repo / CANDIDATE_SPEC)
    if (
        data.get("D") != 804
        or data.get("binding_bundle_sha256")
        != "4a56deea7651970717df54d450da2ab3c453696963f1196c6a44ae0233af3a9b"
        or real.get("candidate_count") != 8
        or real.get("candidate_gate_pass") is not True
        or real.get("duplicate_candidate_groups") != []
        or real.get("candidate_scoring_performed") is not False
        or real.get("metrics") is not None
        or family.get("gate_pass") is not True
        or pair.get("gate_pass") is not True
        or len(pair.get("pairs") or []) != 4
        or len(candidates.get("candidate_ids") or []) != 8
    ):
        raise FinalFreezeError("final capability/data gate failed")
    fixture = synthetic.capability_proof(repo)
    if fixture.get("gate_pass") is not True:
        raise FinalFreezeError("synthetic instrument regression failed")
    guard = guard_provenance(repo)
    tests = scorer_test_manifest(repo)
    output.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, Any] = {
        "GUARDED_CUTOFF_PROVENANCE.json": guard,
        "SCORER_FIXTURE_TEST_MANIFEST.json": tests,
        "POLICY_EVALUATION_CLOCK_PROOF.json": (
            prior.policy_clock_read_proof(repo)
        ),
        "ZERO_SIZE_EXCLUSION_PROOF.json": prior.zero_size_proof(repo),
        "T8_T6_LOOKAHEAD_PROOF.json": fixture[
            "t8_t6_lookahead_proof"
        ],
        "ROUND2_REAL_FAMILY_CAPABILITY_MATRIX.md": (
            render_family_matrix(real, family)
        ),
        "CANDIDATE_DEDUP_ELIGIBILITY_REPORT.md": (
            render_candidate_report(real)
        ),
        "ROUND2_REAIM_PAIR_DIFFERENCE_REPORT.md": (
            render_pair_report(pair)
        ),
        "FINAL_CORRECTION_REPORT.md": (
            render_correction_report(real, pair)
        ),
        "PRIOR_HOLD_LINEAGE_PARITY_PROOF.json": (
            hold_lineage_parity(prior_real, real)
        ),
    }
    for name, value in artifacts.items():
        text = (
            json.dumps(value, indent=2, sort_keys=True) + "\n"
            if isinstance(value, dict) else value
        )
        (output / name).write_text(
            text, encoding="utf-8", newline="\n"
        )
    contract = concrete_scorer_contract(repo, guard)
    (output / "SCORER_FREEZE_CONTRACT.json").write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


BOUND_PATHS = [
    "arb-executor/analysis/window1_round2_instrument.py",
    "arb-executor/analysis/window1_round2_capability_proof.py",
    "arb-executor/analysis/window1_round2_data_binding.py",
    "arb-executor/analysis/window1_round2_real_capability.py",
    "arb-executor/analysis/window1_round2_actual_family_proof.py",
    "arb-executor/analysis/window1_round2_reaim_pair_proof.py",
    "arb-executor/analysis/window1_round2_scorer.py",
    "arb-executor/analysis/window1_round2_final_prerun.py",
    "arb-executor/tests/test_window1_round2_instrument.py",
    "arb-executor/tests/test_window1_round2_scorer.py",
    str(CANDIDATE_SPEC).replace("\\", "/"),
    str(FEATURE_SPEC).replace("\\", "/"),
    str(ADAPTER_SPEC).replace("\\", "/"),
    str(METRIC_SPEC).replace("\\", "/"),
    str(HOLDOUT_SPEC).replace("\\", "/"),
    str(SCORER_SPEC).replace("\\", "/"),
    "arb-executor/docs/research/window1/WINDOW1_ROUND2_POLICY_FAMILY_SPEC.md",
    str(DATA_BINDING).replace("\\", "/"),
    str(PRIOR_MANIFEST).replace("\\", "/"),
    str(PRIOR_REAL_CAPABILITY).replace("\\", "/"),
    str(START_LEDGER).replace("\\", "/"),
    str(START_SUMMARY).replace("\\", "/"),
    str(REAL_CAPABILITY).replace("\\", "/"),
    str(ACTUAL_FAMILY_PROOF).replace("\\", "/"),
    str(REAIM_PAIR_PROOF).replace("\\", "/"),
    str(GUARD_PROVENANCE).replace("\\", "/"),
    str(SCORER_CONTRACT).replace("\\", "/"),
    str(SCORER_TEST_MANIFEST).replace("\\", "/"),
    str(OUTPUT / "POLICY_EVALUATION_CLOCK_PROOF.json").replace("\\", "/"),
    str(OUTPUT / "ZERO_SIZE_EXCLUSION_PROOF.json").replace("\\", "/"),
    str(OUTPUT / "T8_T6_LOOKAHEAD_PROOF.json").replace("\\", "/"),
    str(OUTPUT / "ROUND2_REAL_FAMILY_CAPABILITY_MATRIX.md").replace("\\", "/"),
    str(OUTPUT / "CANDIDATE_DEDUP_ELIGIBILITY_REPORT.md").replace("\\", "/"),
    str(OUTPUT / "ROUND2_REAIM_PAIR_DIFFERENCE_REPORT.md").replace("\\", "/"),
    str(OUTPUT / "FINAL_CORRECTION_REPORT.md").replace("\\", "/"),
    str(
        OUTPUT / "PRIOR_HOLD_LINEAGE_PARITY_PROOF.json"
    ).replace("\\", "/"),
    ".claude/window1_round2_prerun_v2_20260724/FINAL_SUPERSESSION.md",
    ".claude/window1_round1_corrected_20260724/ROUND1_CORRECTION_RECEIPT.json",
]


def freeze(repo: Path, output: Path) -> None:
    branch = git(repo, "branch", "--show-current").decode().strip()
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    if branch != "codex/window1-definition" or head != PARENT:
        raise FinalFreezeError(f"wrong final ancestry: {branch}@{head}")
    receipts = {
        path: index_receipt(repo, path) for path in BOUND_PATHS
    }
    audit_blob = git(repo, "show", f"{AUDIT_COMMIT}:{AUDIT_PATH}")
    audit_oid = git(
        repo, "rev-parse", f"{AUDIT_COMMIT}:{AUDIT_PATH}"
    ).decode().strip()
    real = read_json(repo / REAL_CAPABILITY)
    family = read_json(repo / ACTUAL_FAMILY_PROOF)
    pair = read_json(repo / REAIM_PAIR_PROOF)
    data = read_json(repo / DATA_BINDING)
    metric = read_json(repo / METRIC_SPEC)
    holdout = read_json(repo / HOLDOUT_SPEC)
    contract = read_json(repo / SCORER_CONTRACT)
    guard = read_json(repo / GUARD_PROVENANCE)
    tests = read_json(repo / SCORER_TEST_MANIFEST)
    parity = read_json(
        repo / OUTPUT / "PRIOR_HOLD_LINEAGE_PARITY_PROOF.json"
    )
    expected_lineage = {
        "instrument": receipts[
            str(INSTRUMENT_SOURCE).replace("\\", "/")
        ]["sha256"],
        "candidate_spec": receipts[
            str(CANDIDATE_SPEC).replace("\\", "/")
        ]["sha256"],
        "adapter": receipts[
            str(ADAPTER_SPEC).replace("\\", "/")
        ]["sha256"],
        "metric_contract": receipts[
            str(METRIC_SPEC).replace("\\", "/")
        ]["sha256"],
        "data_binding": data["binding_bundle_sha256"],
        "scorer_source": receipts[
            str(SCORER_SOURCE).replace("\\", "/")
        ]["sha256"],
        "scorer_contract_spec": receipts[
            str(SCORER_SPEC).replace("\\", "/")
        ]["sha256"],
        "guarded_cutoff_provenance": canonical_sha256(guard),
    }
    if contract.get("freeze_lineage") != expected_lineage:
        raise FinalFreezeError("concrete scorer lineage is not staged state")
    if (
        metric.get("D") != 804
        or metric.get("target_PC") != 603
        or holdout.get("holdout_queried") is not False
        or real.get("candidate_count") != 8
        or real.get("candidate_gate_pass") is not True
        or real.get("duplicate_candidate_groups") != []
        or any(
            row["eligible_event_count"] != 694
            or row["censored_event_count"] != 110
            for row in real["candidate_summaries"]
        )
        or family.get("gate_pass") is not True
        or len(family.get("family_witnesses") or []) != 9
        or pair.get("gate_pass") is not True
        or any(
            row["real_D804_events_with_order_change"] <= 0
            or row[
                "every_changed_event_has_exact_plus_one_applied_receipt"
            ] is not True
            or row["witness"][
                "earlier_order_decisions_byte_identical"
            ] is not True
            or row["witness"]["exact_reaim_difference_cents"] != 1
            for row in pair["pairs"]
        )
        or guard.get("gate_pass") is not True
        or tests.get("gate_pass") is not True
        or parity.get("gate_pass") is not True
        or parity.get(
            "all_3216_full_event_streams_byte_identical"
        ) is not True
        or len(contract.get("frozen_event_leg_identities") or []) != 1608
        or canonical_sha256(
            contract.get("frozen_event_leg_identities") or []
        ) != contract.get("frozen_event_leg_identities_sha256")
        or set(contract.get("candidate_stream_receipts") or {})
        != set(contract["candidate_ids"])
        or any(
            len(receipts) != 804
            for receipts in (
                contract.get("candidate_stream_receipts") or {}
            ).values()
        )
        or canonical_sha256(
            contract.get("candidate_stream_receipts") or {}
        ) != contract.get("candidate_stream_receipts_sha256")
    ):
        raise FinalFreezeError("final PRE-RUN hard gate failed")
    manifest = {
        "schema_version": VERSION,
        "freeze_status": "frozen_not_scored",
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "branch": branch,
        "exact_ancestry": {
            "parent_rejected_prerun": PARENT,
            "rejected_grandparent": REJECTED_GRANDPARENT,
            "results_lineage": (
                "f7cd420951f074104dbc602b84137c5eed7455da"
            ),
            "superseding_commit": "this_manifest_commit",
            "commit_count_after_parent": 1,
        },
        "controlling_audit": {
            "branch": "origin/audit/window1-independent",
            "commit": AUDIT_COMMIT,
            "path": AUDIT_PATH,
            "git_blob_oid": audit_oid,
            "bytes": len(audit_blob),
            "sha256": sha256_bytes(audit_blob),
            "merged_wholesale": False,
        },
        "prior_passed_gates_preserved": {
            "ancestry_and_immutable_freeze": True,
            "data_binding": True,
            "cohort_NO_CALL": True,
            "positive_size": True,
            "policy_evaluation_clock": True,
            "missingness_censoring": True,
            "metric_denominator_holdout": True,
            "four_hold_candidate_streams_byte_identical": True,
            "prior_manifest_receipt": receipts[
                str(PRIOR_MANIFEST).replace("\\", "/")
            ],
        },
        "development_dates": scorer.DEVELOPMENT_DATES,
        "sealed_holdout_dates": scorer.SEALED_HOLDOUT_DATES,
        "D": 804,
        "target_PC": 603,
        "candidate_policy_ids": contract["candidate_ids"],
        "candidate_count": 8,
        "real_capability": {
            "candidate_gate_pass": True,
            "duplicate_candidate_groups": [],
            "eligible_event_counts": {
                row["candidate_id"]: row["eligible_event_count"]
                for row in real["candidate_summaries"]
            },
            "censored_event_counts": {
                row["candidate_id"]: row["censored_event_count"]
                for row in real["candidate_summaries"]
            },
            "reaim_pair_order_change_counts": {
                row["reaim_candidate_id"]: (
                    row["real_D804_events_with_order_change"]
                )
                for row in pair["pairs"]
            },
            "order_affecting_family_witness_count": 9,
            "sibling_hold_is_order_witness": False,
        },
        "immutable_data_binding": {
            "binding_bundle_sha256": data["binding_bundle_sha256"],
            "D": data["D"],
            "leg_identities": data["leg_identities"],
            "holdout_dates_present": (
                data["holdout_dates_present_in_any_input"]
            ),
            "receipt": receipts[
                str(DATA_BINDING).replace("\\", "/")
            ],
        },
        "deterministic_scorer": {
            "implemented": True,
            "executed_on_candidate_performance": False,
            "source_receipt": receipts[
                str(SCORER_SOURCE).replace("\\", "/")
            ],
            "contract_receipt": receipts[
                str(SCORER_CONTRACT).replace("\\", "/")
            ],
            "contract": contract,
            "fixture_test_manifest": tests,
            "guarded_cutoff_provenance": guard,
        },
        "metric_contract": metric,
        "parameter_surface": read_json(repo / CANDIDATE_SPEC)[
            "common_parameters"
        ],
        "free_numeric_parameters": [],
        "source_code_data_metric_receipts": receipts,
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "performance_ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "invariants": {
            "D_804": True,
            "target_PC_603": True,
            "metrics_unchanged": True,
            "eight_candidates": True,
            "inherited_hold_streams_byte_identical": True,
            "all_candidates_real_eligible": True,
            "all_candidates_pairwise_distinct": True,
            "four_reaim_pairs_real_order_changing": True,
            "reaim_later_sibling_trigger_only": True,
            "reaim_exact_plus_one": True,
            "sibling_hold_not_order_witness": True,
            "cohort_NO_CALL_not_censor": True,
            "positive_size_only": True,
            "all_inputs_bound": True,
            "all_1608_leg_identities_bound": True,
            "all_6432_candidate_event_streams_bound": True,
            "policy_evaluation_clocks_separate": True,
            "scorer_complete_before_execution": True,
            "V5_guard_directionality_frozen": True,
            "scorer_not_executed": True,
            "holdout_unqueried": True,
        },
    }
    (output / "PRE_RUN_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "PRE_RUN_REPORT.md").write_text(
        "\n".join([
            "# Final superseding Round-2 Window-1 PRE-RUN",
            "",
            "Status: **FROZEN, NOT SCORED. Stop for short CC delta audit.**",
            "",
            f"Parent `{PARENT}`; controlling audit `{AUDIT_COMMIT}`.",
            "",
            "- D=804, target PC=603, and metric definitions are unchanged.",
            "- Eight real-eligible, pairwise-distinct candidates are frozen.",
            "- Four reaim variants change real sibling orders only at later",
            "  sibling-owned triggers, by exactly +1, with earlier orders",
            "  byte-identical to their hold counterpart.",
            "- The deterministic V5-guarded scorer and all input/code receipts",
            "  are frozen. Candidate performance has not been executed.",
            "- July 24-26 remains excluded, unopened, and unqueried.",
            "- No scoring, tuning, performance ablation, or live mutation ran.",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    artifact_rows = {}
    for path in sorted(output.iterdir()):
        if path.name == "ARTIFACT_MANIFEST.json" or not path.is_file():
            continue
        artifact_rows[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    (output / "ARTIFACT_MANIFEST.json").write_text(
        json.dumps({
            "schema_version": VERSION + "-artifacts-v1",
            "parent_rejected_prerun": PARENT,
            "controlling_audit": AUDIT_COMMIT,
            "artifacts": artifact_rows,
            "candidate_scoring_performed": False,
            "holdout_queried": False,
        }, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "freeze"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir
        if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    if args.mode == "prepare":
        prepare(repo, output)
    else:
        freeze(repo, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
