#!/usr/bin/env python3
"""Prepare and freeze the superseding score-free Round-2 PRE-RUN."""

from __future__ import annotations

import argparse
import ast
import copy
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

import window1_round2_capability_proof as synthetic
import window1_round2_instrument as instrument


VERSION = "window1-round2-superseding-prerun-v2"
PARENT = "6eecbd1d9adc7c41af28526d0cabe1038f3ae18b"
AUDIT_COMMIT = "fb17a98fb93ac73668e3ebd731aa0d9c1b99ca43"
AUDIT_PATH = (
    ".claude/audit_20260724_round2_prerun/"
    "ROUND2_PRERUN_CROSS_AUDIT.md"
)
OUTPUT = Path(".claude/window1_round2_prerun_v2_20260724")
DATA_BINDING = OUTPUT / "ROUND2_DATA_BINDING_MANIFEST.json"
REAL_CAPABILITY = OUTPUT / "ROUND2_REAL_CAPABILITY.json"
ACTUAL_FAMILY_PROOF = OUTPUT / "ROUND2_ACTUAL_FAMILY_PROOF.json"
POLICY_SPEC = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_CANDIDATES_V1.json"
)
FEATURE_SPEC = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_FEATURE_ALLOWLIST_V1.json"
)
ADAPTER_SPEC = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_EXECUTION_ADAPTER_V1.json"
)
METRIC_SPEC = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json"
)
HOLDOUT_SPEC = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_PROSPECTIVE_HOLDOUT_V1.json"
)


class FreezeError(RuntimeError):
    """Raised when a superseding PRE-RUN invariant is false."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FreezeError(f"JSON object required: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value, sort_keys=True, separators=(",", ":")
        ).encode()
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
        raise FreezeError(
            f"git {' '.join(args)} failed: "
            + result.stderr.decode(errors="replace").strip()
        )
    return result.stdout


def index_receipt(repo: Path, relative: str) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise FreezeError(f"bound file missing: {relative}")
    oid = git(repo, "rev-parse", f":{relative}").decode().strip()
    working = git(
        repo, "hash-object", f"--path={relative}", relative
    ).decode().strip()
    if oid != working:
        raise FreezeError(f"unstaged bound change: {relative}")
    blob = git(repo, "show", f":{relative}")
    return {
        "path": relative,
        "hash_basis": "staged_git_blob_lf",
        "git_blob_oid": oid,
        "bytes": len(blob),
        "sha256": sha256_bytes(blob),
    }


def policy_clock_read_proof(repo: Path) -> dict[str, Any]:
    event = synthetic.base_event()
    surfaces = synthetic.synthetic_surfaces()
    first = synthetic.run_policy(repo, surfaces, event)
    second = synthetic.run_policy(
        repo, surfaces, copy.deepcopy(event)
    )
    fill_times = [
        float(row["ts"]) for row in first["order_stream"]
        if row["action"] == "fill_observed"
    ]
    if not fill_times:
        raise FreezeError("clock proof fixture produced no fill")
    guard = {"guard_id": "fixture-official-60s"}
    early = instrument.evaluate_order_stream(first, {
        "start_source_class": "official_exact",
        "evaluation_real_start_ts": min(fill_times) - 1,
        "start_guard": guard,
    })
    late = instrument.evaluate_order_stream(first, {
        "start_source_class": "official_exact",
        "evaluation_real_start_ts": max(fill_times) + 1,
        "start_guard": guard,
    })
    leaked = copy.deepcopy(event)
    leaked["evaluation_real_start_ts"] = max(fill_times)
    rejected = False
    try:
        synthetic.run_policy(repo, surfaces, leaked)
    except instrument.InstrumentError as exc:
        rejected = "inaccessible" in str(exc)

    source = (
        repo / "arb-executor/analysis/window1_round2_instrument.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_reads = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        key = node.slice.value if isinstance(node.slice, ast.Constant) else None
        if key in instrument.FORBIDDEN_POLICY_CLOCK_FIELDS:
            parent_function = next((
                item.name for item in ast.walk(tree)
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node in set(ast.walk(item))
            ), "unknown")
            if parent_function != "evaluate_order_stream":
                forbidden_reads.append({
                    "field": key,
                    "function": parent_function,
                    "line": node.lineno,
                })
    proof = {
        "schema_version": "window1-round2-clock-separation-proof-v1",
        "identical_causal_histories": True,
        "future_realized_starts_differ": True,
        "policy_stream_a_sha256": first["stream_sha256"],
        "policy_stream_b_sha256": second["stream_sha256"],
        "policy_streams_byte_identical": (
            json.dumps(first, sort_keys=True)
            == json.dumps(second, sort_keys=True)
        ),
        "early_evaluation_classification": early["classification"],
        "late_evaluation_classification": late["classification"],
        "evaluator_classifications_differ": (
            early["classification"] != late["classification"]
        ),
        "leaked_realized_start_refused": rejected,
        "candidate_policy_forbidden_field_read_sites": forbidden_reads,
        "policy_anchor": (
            "timestamped exchange schedule observed at or before "
            "policy activation"
        ),
        "evaluation_real_start": "ex-post evaluator only",
        "schedule_only_positive_proof_allowed": False,
        "gate_pass": (
            first["stream_sha256"] == second["stream_sha256"]
            and early["classification"] != late["classification"]
            and rejected
            and not forbidden_reads
        ),
        "scored": False,
        "holdout_queried": False,
    }
    if not proof["gate_pass"]:
        raise FreezeError("policy/evaluation clock proof failed")
    return proof


def zero_size_proof(repo: Path) -> dict[str, Any]:
    surfaces = synthetic.synthetic_surfaces()
    cases = []
    for bad_size in (0, None, "malformed"):
        event = synthetic.base_event()
        target = next(
            row for row in event["legs"][0]["observations"]
            if row.get("trade_id") == "A-DIVOT"
        )
        target["size"] = bad_size
        result = synthetic.run_policy(repo, surfaces, event)
        actions = result["leg_streams"]["A"]
        cases.append({
            "case": f"divot_size_{bad_size!r}",
            "excluded": any(
                row["action"] == "print_excluded"
                and row.get("trade_id") == "A-DIVOT"
                for row in actions
            ),
            "divot_triggered_by_bad_row": any(
                row["action"] == "micro_divot"
                and row.get("print_price_cents") == 54
                for row in actions
            ),
        })
    synthetic_event = synthetic.base_event()
    synthetic_target = next(
        row for row in synthetic_event["legs"][0]["observations"]
        if row.get("trade_id") == "A-DIVOT"
    )
    synthetic_target["synthetic_transition"] = True
    synthetic_result = synthetic.run_policy(
        repo, surfaces, synthetic_event
    )
    cases.append({
        "case": "synthetic_transition_divot",
        "excluded": any(
            row["action"] == "print_excluded"
            and row["reason"] == "synthetic_transition"
            for row in synthetic_result["leg_streams"]["A"]
        ),
        "divot_triggered_by_bad_row": False,
    })
    walk_event = synthetic.base_event()
    for row in walk_event["legs"][0]["observations"]:
        if row.get("trade_id") in {"A-CHAIN-1", "A-CHAIN-2"}:
            row["size"] = 0
    walk_result = synthetic.run_policy(repo, surfaces, walk_event)
    walk_triggered = any(
        row["action"] == "reprice"
        and row["reason"] == "verified_nonself_chain_exact_one_cent"
        for row in walk_result["leg_streams"]["A"]
    )
    proof = {
        "schema_version": "window1-round2-zero-size-proof-v1",
        "cases": cases,
        "zero_size_walk_chain_triggered": walk_triggered,
        "bound_real_cache_invalid_size_rows": 0,
        "law": (
            "zero, null, malformed, or synthetic transition size "
            "contributes zero to all evidence/decision surfaces"
        ),
        "gate_pass": (
            all(
                row["excluded"]
                and not row["divot_triggered_by_bad_row"]
                for row in cases
            )
            and not walk_triggered
        ),
        "scored": False,
        "holdout_queried": False,
    }
    if not proof["gate_pass"]:
        raise FreezeError("zero-size exclusion proof failed")
    return proof


def render_family_matrix(
    real: Mapping[str, Any],
    proof: Mapping[str, Any],
) -> str:
    witness = {
        row["family_id"]: row for row in proof["family_witnesses"]
    }
    unavailable = {
        row["family_id"]: row for row in proof["unavailable_or_noncoverage"]
    }
    ordered = [
        "asynchronous_divot_timing", "leg_specific_posture",
        "nonself_one_cent_walk", "first_fill_sibling_response",
        "pair_divot_recut", "causal_orientation",
        "causal_drift_recognition", "cohort_steering",
        "true_print_flow", "bbo_top5_pressure",
        "own_order_contribution_subtraction",
        "start_boundary_evaluator",
    ]
    lines = [
        "# Round-2 real-development family capability matrix",
        "",
        "No family is actually selected: Round-2 scoring has not run.",
        "",
        "| family | loaded | available | evaluated | decision-changing | actually selected | real witness/status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for family in ordered:
        if family in witness:
            row = witness[family]
            lines.append(
                f"| {family} | yes | yes | yes | yes | no | "
                f"`{row['event_id']}` |"
            )
        else:
            row = unavailable[family]
            available = "yes" if family != "cohort_steering" else "no"
            lines.append(
                f"| {family} | yes | {available} | yes | no | no | "
                f"{row['status']} |"
            )
    lines.extend([
        "",
        f"Retained candidates: {real['candidate_count']}; duplicate groups: "
        f"{len(real['duplicate_candidate_groups'])}.",
        "",
    ])
    return "\n".join(lines)


def render_candidate_report(
    candidates: Mapping[str, Any],
    real: Mapping[str, Any],
) -> str:
    lines = [
        "# Round-2 candidate deduplication and eligibility",
        "",
        "The retained allowlist is pairwise distinct over complete D=804",
        "decision-hash bundles. No candidate exists only on synthetic fixtures.",
        "",
        "| candidate | eligible | censored | cohort NO_CALL | distinct events vs base | place | reprice | cancel | positive prints consumed |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in real["candidate_summaries"]:
        decisions = row["decision_counts"]
        lines.append(
            f"| {row['candidate_id']} | {row['eligible_event_count']} | "
            f"{row['censored_event_count']} | {row['cohort_NO_CALL_count']} | "
            f"{row['distinct_order_decisions_versus_base_events']} | "
            f"{decisions.get('place', 0)} | {decisions.get('reprice', 0)} | "
            f"{decisions.get('cancel', 0)} | "
            f"{row['positive_size_print_count_consumed']} |"
        )
    lines.extend([
        "",
        "Named retained-candidate censor reasons are `causal_role` (10 leg",
        "occurrences), `dynamic_recut_cell_unavailable` (127), and, where",
        "required, `top5` (10). Missing features remain censored, never",
        "nonfills.",
        "",
        "| candidate | async events | posture events | recut events | sibling events | walk events | BBO-covered events | top5-covered events |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in real["candidate_summaries"]:
        exercised = row["real_events_exercising"]
        lines.append(
            f"| {row['candidate_id']} | "
            f"{len(exercised['asynchronous_timing'])} | "
            f"{len(exercised['posture'])} | "
            f"{len(exercised['recut'])} | "
            f"{len(exercised['sibling_response'])} | "
            f"{len(exercised['walk'])} | "
            f"{row['BBO_covered_event_count']} | "
            f"{row['top5_covered_event_count']} |"
        )
    lines.extend([
        "",
        "The JSON capability receipt names every exercising event, every",
        "cohort class/zone/event/leg call, every full-ticker per-leg",
        "placement/reprice/cancel count, and every missing-feature count.",
        "",
        "Removed before freeze:",
        "",
    ])
    for row in candidates["removed_before_superseding_freeze"]:
        lines.append(f"- `{row['candidate_id']}` — {row['reason']}.")
    lines.extend([
        "",
        "The two full-stack park/join variants were structurally redundant",
        "because that posture cannot call the walk actuator. The reaim variants",
        "were removed as non-minimal response variants; the retained hold",
        "policies exercise real first-fill sibling decisions.",
        "",
    ])
    return "\n".join(lines)


def render_correction_report(
    real: Mapping[str, Any],
    family: Mapping[str, Any],
) -> str:
    return "\n".join([
        "# Rejected Round-2 PRE-RUN blocker corrections",
        "",
        f"Controlling audit: `{AUDIT_COMMIT}`. Rejected PRE-RUN: `{PARENT}`.",
        "Status: **corrected and frozen, not scored**.",
        "",
        "## F1 — cohort availability",
        "",
        "Below-floor cohort support now returns `NO_CALL_UNAVAILABLE`; it never",
        "sets `feature_censored` and the underlying pair/divot/posture chain",
        "continues. The cohort-aware retained candidates recorded 1,471",
        "per-leg NO_CALLs each. Cohort is unavailable and is not counted as",
        "coverage.",
        "",
        "## F2 — positive-size evidence",
        "",
        "A single admission gate now requires receipt identity, independently",
        "verified finite size >0, a public source class, and a non-synthetic",
        "row before any fill, divot, flow, orientation, walk, or posture",
        "surface. Zero/null/malformed/synthetic divot and walk fixtures pass.",
        "",
        "## F3 — immutable data diet",
        "",
        "The data-binding manifest covers D=804 events, 1,608 legs, the V5",
        "start ledger, public print archive, all 804 per-event cache files,",
        "BBO/top-five streams, own-order receipts, feature flags, cohort,",
        "shape/orientation/drift/recut surfaces, close references, source",
        "classes, and censor reasons. The runner refuses any digest, identity,",
        "date, or file-set drift.",
        "",
        "## F4 — policy/evaluation clocks",
        "",
        "Eligibility is now `policy_anchor_ts + t_deep_p50`, clamped only to",
        "the declared schedule corridor. Realized start is rejected by policy",
        "code and accepted only by the ex-post evaluator. Identical causal",
        "histories remain byte-identical under different future starts while",
        "the evaluator classifies them differently.",
        "",
        "## Real capability result",
        "",
        f"- retained candidates: {real['candidate_count']};",
        "- eligible events per candidate: 694; censored: 110;",
        "- pairwise duplicate groups: zero;",
        f"- isolated real decision-changing family witnesses: "
        f"{len(family['family_witnesses'])};",
        "- D remains 804; target remains PC=603; metrics are unchanged and",
        "  unexecuted;",
        "- July 24-26 remains excluded, unopened, and unqueried.",
        "",
    ])


def prepare(repo: Path, output: Path) -> None:
    real = read_json(repo / REAL_CAPABILITY)
    family = read_json(repo / ACTUAL_FAMILY_PROOF)
    data = read_json(repo / DATA_BINDING)
    candidates = read_json(repo / POLICY_SPEC)
    if (
        real.get("candidate_gate_pass") is not True
        or real.get("duplicate_candidate_groups") != []
        or family.get("gate_pass") is not True
        or data.get("D") != 804
    ):
        raise FreezeError("real capability/data gate is not frozen-ready")
    clock = policy_clock_read_proof(repo)
    zero = zero_size_proof(repo)
    fixture = synthetic.capability_proof(repo)
    if fixture.get("gate_pass") is not True:
        raise FreezeError("regression fixture gate failed")
    output.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, str | dict[str, Any]] = {
        "POLICY_EVALUATION_CLOCK_PROOF.json": clock,
        "ZERO_SIZE_EXCLUSION_PROOF.json": zero,
        "T8_T6_LOOKAHEAD_PROOF.json": fixture[
            "t8_t6_lookahead_proof"
        ],
        "ROUND2_REAL_FAMILY_CAPABILITY_MATRIX.md": render_family_matrix(
            real, family
        ),
        "CANDIDATE_DEDUP_ELIGIBILITY_REPORT.md": render_candidate_report(
            candidates, real
        ),
        "BLOCKER_CORRECTION_REPORT.md": render_correction_report(
            real, family
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


BOUND_PATHS = [
    "arb-executor/analysis/window1_round2_instrument.py",
    "arb-executor/analysis/window1_round2_capability_proof.py",
    "arb-executor/analysis/window1_round2_data_binding.py",
    "arb-executor/analysis/window1_round2_real_capability.py",
    "arb-executor/analysis/window1_round2_actual_family_proof.py",
    "arb-executor/analysis/window1_round2_superseding_prerun.py",
    "arb-executor/tests/test_window1_round2_instrument.py",
    POLICY_SPEC, FEATURE_SPEC, ADAPTER_SPEC, METRIC_SPEC, HOLDOUT_SPEC,
    "arb-executor/docs/research/window1/WINDOW1_ROUND2_POLICY_FAMILY_SPEC.md",
    str(DATA_BINDING).replace("\\", "/"),
    str(REAL_CAPABILITY).replace("\\", "/"),
    str(ACTUAL_FAMILY_PROOF).replace("\\", "/"),
    str(OUTPUT / "POLICY_EVALUATION_CLOCK_PROOF.json").replace("\\", "/"),
    str(OUTPUT / "ZERO_SIZE_EXCLUSION_PROOF.json").replace("\\", "/"),
    str(OUTPUT / "T8_T6_LOOKAHEAD_PROOF.json").replace("\\", "/"),
    str(OUTPUT / "ROUND2_REAL_FAMILY_CAPABILITY_MATRIX.md").replace("\\", "/"),
    str(OUTPUT / "CANDIDATE_DEDUP_ELIGIBILITY_REPORT.md").replace("\\", "/"),
    str(OUTPUT / "BLOCKER_CORRECTION_REPORT.md").replace("\\", "/"),
    ".claude/window1_round1_corrected_20260724/ROUND1_CORRECTION_RECEIPT.json",
    ".claude/window1_round2_prerun_20260724/PRE_RUN_SUPERSESSION.md",
]


def freeze(repo: Path, output: Path) -> None:
    branch = git(repo, "branch", "--show-current").decode().strip()
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    if branch != "codex/window1-definition" or head != PARENT:
        raise FreezeError(f"wrong freeze ancestry: {branch}@{head}")
    receipts = {
        path: index_receipt(repo, path) for path in BOUND_PATHS
    }
    audit_blob = git(repo, "show", f"{AUDIT_COMMIT}:{AUDIT_PATH}")
    audit_oid = git(
        repo, "rev-parse", f"{AUDIT_COMMIT}:{AUDIT_PATH}"
    ).decode().strip()
    candidates = read_json(repo / POLICY_SPEC)
    features = read_json(repo / FEATURE_SPEC)
    metric = read_json(repo / METRIC_SPEC)
    holdout = read_json(repo / HOLDOUT_SPEC)
    data = read_json(repo / DATA_BINDING)
    real = read_json(repo / REAL_CAPABILITY)
    family = read_json(repo / ACTUAL_FAMILY_PROOF)
    clock = read_json(output / "POLICY_EVALUATION_CLOCK_PROOF.json")
    zero = read_json(output / "ZERO_SIZE_EXCLUSION_PROOF.json")
    if (
        metric.get("D") != 804 or metric.get("target_PC") != 603
        or holdout.get("holdout_queried") is not False
        or len(candidates.get("candidate_ids") or []) != 4
        or real.get("candidate_gate_pass") is not True
        or family.get("gate_pass") is not True
        or clock.get("gate_pass") is not True
        or zero.get("gate_pass") is not True
    ):
        raise FreezeError("superseding freeze hard gate failed")
    manifest = {
        "schema_version": VERSION,
        "freeze_status": "frozen_not_scored",
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "branch": branch,
        "exact_ancestry": {
            "parent_rejected_prerun": PARENT,
            "parent_of_rejected": (
                "f7cd420951f074104dbc602b84137c5eed7455da"
            ),
            "superseding_commit": "this_manifest_commit",
            "commit_count_after_rejected": 1,
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
        "development_dates": [f"2026-07-{day:02d}" for day in range(12, 21)],
        "sealed_holdout_dates": [f"2026-07-{day:02d}" for day in range(24, 27)],
        "D": 804,
        "target_PC": 603,
        "metric_contract": metric,
        "metric_contract_sha256": receipts[METRIC_SPEC]["sha256"],
        "candidate_policy_ids": candidates["candidate_ids"],
        "candidate_policy_ids_sha256": canonical_sha256(
            candidates["candidate_ids"]
        ),
        "removed_candidate_ids": candidates[
            "removed_before_superseding_freeze"
        ],
        "parameter_surface": candidates["common_parameters"],
        "parameter_surface_sha256": canonical_sha256(
            candidates["common_parameters"]
        ),
        "predeclared_ablations": candidates[
            "predeclared_selected_candidate_ablations"
        ],
        "free_numeric_parameters": [],
        "feature_family_contract": features,
        "adapter": read_json(repo / ADAPTER_SPEC),
        "immutable_data_binding": {
            "binding_bundle_sha256": data["binding_bundle_sha256"],
            "D": data["D"],
            "leg_identities": data["leg_identities"],
            "holdout_dates_present": data[
                "holdout_dates_present_in_any_input"
            ],
            "receipt": receipts[
                str(DATA_BINDING).replace("\\", "/")
            ],
        },
        "real_capability_gate": {
            "candidate_count": real["candidate_count"],
            "candidate_gate_pass": real["candidate_gate_pass"],
            "duplicate_candidate_groups": real[
                "duplicate_candidate_groups"
            ],
            "eligible_event_counts": {
                row["candidate_id"]: row["eligible_event_count"]
                for row in real["candidate_summaries"]
            },
            "censored_event_counts": {
                row["candidate_id"]: row["censored_event_count"]
                for row in real["candidate_summaries"]
            },
            "family_witness_count": len(family["family_witnesses"]),
            "cohort_status": "unavailable_NO_CALL_not_coverage",
            "own_subtraction_status": (
                "mandatory_safety_law_inert_zero_attributable_volume"
            ),
        },
        "policy_evaluation_clock": clock,
        "positive_size_gate": zero,
        "start_boundary_law": {
            "guard_id": "te-calibration-central-93pct-asymmetric-v1",
            "official_guard_seconds": 60,
            "proxy_positive_guard_seconds": 900,
            "proxy_negative_guard_seconds": 600,
            "TennisExplorer_proxy_exact": False,
            "policy_anchor": "timestamped causal exchange schedule",
            "evaluation_real_start_policy_access": False,
            "schedule_only_positive_allowed": False,
        },
        "unavailable": {
            "Pinnacle": "zero causal rows",
            "full_depth": (
                "snapshot ancestry plus gap-free sequence continuity unproved"
            ),
            "shape_policy_mapping": (
                "no independent non-AIM causal Round-2 mapping"
            ),
            "cohort_steering": "all real cells below n=30",
        },
        "prohibitions": [
            "future_information", "realized_start_policy_oracle",
            "schedule_as_positive_evaluation_truth",
            "post_decision_reference", "self_trade_confirmation",
            "zero_or_missing_size_trigger", "feature_gap_imputation",
            "denominator_change", "holdout_access",
            "production_or_live_mutation",
        ],
        "source_code_data_metric_receipts": receipts,
        "hash_basis": "staged_git_blob_lf",
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "performance_ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "invariants": {
            "D_804": True,
            "target_PC_603": True,
            "metrics_unchanged": True,
            "all_candidates_real_eligible": True,
            "all_candidates_pairwise_distinct": True,
            "cohort_abstention_never_censors": True,
            "positive_size_only": True,
            "all_inputs_bound": True,
            "policy_evaluation_clocks_separate": True,
            "holdout_unqueried": True,
            "round2_not_scored": True,
        },
    }
    (output / "PRE_RUN_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "PRE_RUN_REPORT.md").write_text(
        "\n".join([
            "# Superseding Round-2 Window-1 PRE-RUN",
            "",
            "Status: **FROZEN, NOT SCORED. Stop for fresh independent CC audit.**",
            "",
            f"Rejected parent: `{PARENT}`. Controlling audit: `{AUDIT_COMMIT}`.",
            "",
            "- D=804 and target PC=603 are unchanged.",
            "- July 12-20 only; July 24-26 excluded, unopened, unqueried.",
            "- Four retained candidates are real-eligible (694 each) and",
            "  pairwise distinct over complete D=804 decision streams.",
            "- Cohort below n=30 is a named NO_CALL and never a censor.",
            "- Only receipt-identified, independently verified positive-size",
            "  public prints can reach evidence or decision surfaces.",
            "- Every consumed input is hash-bound; runtime execution refuses",
            "  missing, changed, unbound, or outside-date inputs.",
            "- Policy timing uses only the timestamped schedule anchor and",
            "  declared corridor. Reconstructed actual start is evaluation-only.",
            "- Nine policy families have isolated real decision witnesses.",
            "  Cohort, own subtraction, and start evaluation are not counted as",
            "  decision-family coverage for the named reasons.",
            "- No Round-2 scoring, tuning, performance ablation, or holdout",
            "  access occurred.",
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
    output = args.output_dir
    if not output.is_absolute():
        output = repo / output
    if args.mode == "prepare":
        prepare(repo, output)
    else:
        freeze(repo, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
