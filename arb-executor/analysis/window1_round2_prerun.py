#!/usr/bin/env python3
"""Prepare and freeze the score-free Round-2 Window-1 PRE-RUN artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

import window1_round2_capability_proof as capability


VERSION = "window1-round2-prerun-v1"
PARENT_COMMIT = "f7cd420951f074104dbc602b84137c5eed7455da"
AUDIT_COMMIT = "024f03bb5b1944bae39ad5afef6ee019ef5dc06d"
AUDIT_PATH = (
    ".claude/audit_20260724_osfamily/"
    "OS_FAMILY_RESULT_CROSS_AUDIT.md"
)
OUTPUT_RELATIVE = ".claude/window1_round2_prerun_20260724"

DEVELOPMENT_DATES = [f"2026-07-{day:02d}" for day in range(12, 21)]
HOLDOUT_DATES = [f"2026-07-{day:02d}" for day in range(24, 27)]

POLICY_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_CANDIDATES_V1.json"
)
FEATURE_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_FEATURE_ALLOWLIST_V1.json"
)
METRIC_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_METRIC_CONTRACT_V1.json"
)
HOLDOUT_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_PROSPECTIVE_HOLDOUT_V1.json"
)
ADAPTER_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_EXECUTION_ADAPTER_V1.json"
)
SPEC_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND2_POLICY_FAMILY_SPEC.md"
)

BOUND_PATHS = [
    POLICY_PATH,
    FEATURE_PATH,
    METRIC_PATH,
    HOLDOUT_PATH,
    ADAPTER_PATH,
    SPEC_PATH,
    "arb-executor/analysis/window1_round2_instrument.py",
    "arb-executor/analysis/window1_round2_capability_proof.py",
    "arb-executor/analysis/window1_round2_prerun.py",
    "arb-executor/analysis/window1_round1_audit_correction.py",
    "arb-executor/tests/test_window1_round2_instrument.py",
    "arb-executor/tests/test_window1_round1_audit_correction.py",
    ".claude/window1_round1_corrected_20260724/"
    "ROUND1_CORRECTION_RECEIPT.json",
    ".claude/window1_round1_corrected_20260724/"
    "WINDOW1_ROUND1_CORRECTED_REPORT.md",
    ".claude/window1_os_family_results_20260724/"
    "WINDOW1_OS_FAMILY_REPORT.md",
    f"{OUTPUT_RELATIVE}/ROUND2_CAPABILITY_PROOF.json",
    f"{OUTPUT_RELATIVE}/ROUND2_FAMILY_CAPABILITY_MATRIX.md",
    f"{OUTPUT_RELATIVE}/T8_T6_LOOKAHEAD_PROOF.json",
    ".claude/entrysurface_20260717/band_map_v1.json",
    ".claude/entrysurface_20260717/divot_tables_v1.json",
    ".claude/entrysurface_20260717/drift_surfaces_v1.json",
    ".claude/seqfloor_20260708/recut_cells.json",
    ".claude/trendpath/ORIENT_V1.json",
    ".claude/master_20260709/cohort.json",
    ".claude/window1_start_guard_calibration_20260724/"
    "START_GUARD_CALIBRATION.json",
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl",
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_SUMMARY_V5.json",
    ".claude/window1_start_guard_corrected_20260724/"
    "HISTORICAL_WITNESSES_GUARDED.json",
    ".claude/window1_20260721/SOURCE_COVERAGE_SUMMARY.json",
    ".claude/window1_20260721/WINDOW1_FEATURE_COVERAGE.json",
    ".claude/window1_20260721/WS_DEPTH_COVERAGE_SUMMARY.json",
    ".claude/window1_20260721/LIFECYCLE_VALIDATION_SUMMARY.json",
    ".claude/window1_20260721/MACRO_PROJECTION_RECEIPT.json",
    "arb-executor/docs/LIVING_VAULT.md",
    "arb-executor/docs/research/window1/WINDOW1_SPEC.md",
    ".claude/proof_20260709/PROOF_OS_BUILD.md",
    ".claude/rulings/RULING_PAIR_ECONOMICS.md",
    ".claude/rulings/RULING_COMBINED_PRICE_CLAUSE.md",
    ".claude/seqfloor_20260708/SEQFLOOR_RECUT.md",
    ".claude/entrysurface_20260717/DIVOT_TABLES.md",
    ".claude/entrysurface_20260717/DRIFT_SURFACES.md",
    ".claude/entrymech_20260717/ACCEPTANCE_WALK.md",
    ".claude/backwalk_20260720/BACKWALK_WALLS_V1.md",
    ".claude/proof_20260717/PROOF_PAIR_INVARIANT.md",
    ".claude/proof_20260720/PROOF_DUAL_DIVOT_SEAL.md",
]


class FreezeError(RuntimeError):
    """Raised when PRE-RUN invariants are not satisfied."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(
    repo: Path, *args: str, input_bytes: bytes | None = None,
) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise FreezeError(
            f"git {' '.join(args)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return completed.stdout


def index_receipt(repo: Path, relative: str) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise FreezeError(f"bound path missing: {relative}")
    index_oid = git(repo, "rev-parse", f":{relative}").decode().strip()
    working_oid = git(
        repo, "hash-object", f"--path={relative}", relative
    ).decode().strip()
    if index_oid != working_oid:
        raise FreezeError(
            f"bound working file differs from staged blob: {relative}"
        )
    blob = git(repo, "show", f":{relative}")
    return {
        "path": relative,
        "hash_basis": "staged_git_blob_lf",
        "git_blob_oid": index_oid,
        "bytes": len(blob),
        "sha256": sha256_bytes(blob),
    }


def audit_receipt(repo: Path) -> dict[str, Any]:
    blob = git(repo, "show", f"{AUDIT_COMMIT}:{AUDIT_PATH}")
    oid = git(
        repo, "rev-parse", f"{AUDIT_COMMIT}:{AUDIT_PATH}"
    ).decode().strip()
    return {
        "commit": AUDIT_COMMIT,
        "path": AUDIT_PATH,
        "git_blob_oid": oid,
        "bytes": len(blob),
        "sha256": sha256_bytes(blob),
        "merged_wholesale": False,
        "role": "controlling independent audit of Round-1 results",
    }


def render_capability_matrix(proof: Mapping[str, Any]) -> str:
    lines = [
        "# Round-2 per-family capability matrix",
        "",
        "All rows use synthetic causal fixtures only. `decision-changing` passes",
        "only when the paired lawful order-decision hashes differ. Strategy",
        "families use frozen ablations; true-flow and own-volume safety laws use",
        "the same policy under two source-proven causal inputs.",
        "",
        "| family | loaded | available | evaluated | decision-changing | selected |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in proof["family_capability_matrix"]:
        lines.append(
            f"| {row['family_id']} | true | true | true | "
            f"{str(row['decision_changing']).lower()} | not-yet-scored |"
        )
    lines.extend([
        "",
        "No Round-2 family is actually selected because scoring has not run.",
        "`available=true` means the frozen instrument has a lawful source and",
        "actuator path; per-event development coverage has not been scored and",
        "any absent required input remains censored.",
        "A family that failed this gate would be labeled unavailable or inert and",
        "removed from the advertised allowlist before freeze.",
        "",
        "Unavailable outside the advertised matrix: Pinnacle, full depth, shape",
        "without an independent non-AIM mapping, the uncommitted sealed pair",
        "policy, and the disarmed riser actuator.",
        "",
    ])
    return "\n".join(lines)


def prepare(repo: Path, output: Path) -> None:
    result = capability.capability_proof(repo)
    if result.get("gate_pass") is not True:
        raise FreezeError(
            "family capability gate failed: "
            f"{result.get('failed_or_inert_families')}"
        )
    output.mkdir(parents=True, exist_ok=True)
    (output / "ROUND2_CAPABILITY_PROOF.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "T8_T6_LOOKAHEAD_PROOF.json").write_text(
        json.dumps(
            result["t8_t6_lookahead_proof"],
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "ROUND2_FAMILY_CAPABILITY_MATRIX.md").write_text(
        render_capability_matrix(result),
        encoding="utf-8",
        newline="\n",
    )


def validate_contracts(repo: Path) -> dict[str, Any]:
    candidates = read_json(repo / POLICY_PATH)
    features = read_json(repo / FEATURE_PATH)
    metric = read_json(repo / METRIC_PATH)
    holdout = read_json(repo / HOLDOUT_PATH)
    adapter = read_json(repo / ADAPTER_PATH)
    correction = read_json(
        repo / ".claude/window1_round1_corrected_20260724/"
        "ROUND1_CORRECTION_RECEIPT.json"
    )
    guard = read_json(
        repo / ".claude/window1_start_guard_calibration_20260724/"
        "START_GUARD_CALIBRATION.json"
    )
    start_summary = read_json(
        repo / ".claude/window1_start_guard_corrected_20260724/"
        "REAL_START_SUMMARY_V5.json"
    )
    proof = read_json(
        repo / OUTPUT_RELATIVE / "ROUND2_CAPABILITY_PROOF.json"
    )
    if metric.get("D") != 804 or metric.get("target_PC") != 603:
        raise FreezeError("D/target metric contract changed")
    if holdout.get("development_dates_utc") != DEVELOPMENT_DATES:
        raise FreezeError("development dates changed")
    if holdout.get("sealed_holdout_dates_utc") != HOLDOUT_DATES:
        raise FreezeError("holdout dates changed")
    if any(
        bool(holdout.get(field))
        for field in (
            "holdout_opened", "holdout_queried",
            "round2_scoring_performed",
        )
    ):
        raise FreezeError("holdout/scoring declaration is not sealed")
    if candidates.get("free_numeric_parameters") != []:
        raise FreezeError("free parameter appeared")
    if len(candidates.get("candidate_ids") or []) != 10:
        raise FreezeError("candidate allowlist changed")
    if len(candidates.get("predeclared_selected_candidate_ablations") or []) != 9:
        raise FreezeError("ablation allowlist changed")
    if len(features.get("allowed") or []) != 12:
        raise FreezeError("feature-family allowlist changed")
    if adapter.get("scoring_implemented") is not False:
        raise FreezeError("adapter unexpectedly implements scoring")
    if adapter.get("network_interface") is not False:
        raise FreezeError("adapter unexpectedly exposes network")
    if correction.get("selected_metrics") != {
        "D": 804, "C": 10, "PC": 9, "S": 9, "IC": 4
    }:
        raise FreezeError("Round-1 corrected metrics changed")
    split = correction["failure_decomposition"]["corrected"]
    if split != {
        "genuine_zero_fill": 582,
        "naked_single_leg_fill": 84,
        "zero_length_window1_opportunity": 12,
    }:
        raise FreezeError("Round-1 corrected failure split changed")
    if start_summary.get("D") != 804:
        raise FreezeError("start ledger denominator changed")
    if start_summary.get("source_conservation") != {
        "start_clock": 687,
        "clean_interval": 31,
        "contradictory": 14,
        "schedule_only": 20,
        "live_by_only": 52,
    }:
        raise FreezeError("start source conservation changed")
    if start_summary.get("start_clock_decomposition") != {
        "official_exact": 234,
        "quantized_late_detection_proxy": 453,
    }:
        raise FreezeError("start clock decomposition changed")
    if proof.get("gate_pass") is not True:
        raise FreezeError("capability proof failed")
    lookahead = proof["t8_t6_lookahead_proof"]
    if not (
        lookahead.get("pre_T6_decisions_identical") is True
        and lookahead.get("post_T6_decisions_differ") is True
        and lookahead.get("future_information_used_before_T6") is False
    ):
        raise FreezeError("T8/T6 causal proof failed")
    return {
        "candidates": candidates,
        "features": features,
        "metric": metric,
        "holdout": holdout,
        "adapter": adapter,
        "guard": guard,
        "start_summary": start_summary,
        "proof": proof,
    }


def render_report(manifest: Mapping[str, Any]) -> str:
    guard = manifest["start_boundary_law"]
    return "\n".join([
        "# Round-2 Window-1 PRE-RUN freeze",
        "",
        "Status: **FROZEN, NOT SCORED. Stop for independent CC review.**",
        "",
        "## Immutable scope",
        "",
        "- development: July 12-20, 2026 UTC only;",
        "- unopened holdout: July 24-26, 2026 UTC;",
        "- D=804; primary target PC=603;",
        "- exact lot: five contracts per leg;",
        "- no production, live_v4, configuration, orders, positions, Window 2,",
        "  exits, settlement, or DCA interface.",
        "",
        "## Start boundary",
        "",
        f"- guard: `{guard['guard_id']}`;",
        f"- proxy interval: {guard['actual_start_interval']};",
        "- TennisExplorer clocks remain quantized late-detection proxies, never",
        "  exact starts;",
        "- schedule-only, live-by-only, and contradictory rows cannot produce a",
        "  positive stream;",
        "- the one-sided stronger-causal-bound precedence law remains frozen.",
        "",
        "## Grid and capability",
        "",
        f"- candidate IDs: {len(manifest['candidate_policy_ids'])};",
        f"- predeclared selected-candidate ablations: "
        f"{len(manifest['predeclared_ablations'])};",
        "- free numeric parameters: zero;",
        "- every advertised family changed at least one eligible order decision",
        "  in a causal fixture;",
        "- no family is actually selected because Round-2 scoring has not run.",
        "",
        "## T8/T6 defect proof",
        "",
        "Two fixture runs differed only in the future T6 recognition mapping.",
        "Their complete pre-T6 decision hashes are identical; their post-T6",
        "decision hashes differ. No T8 price accepts a recognition band.",
        "",
        "## Missing and unavailable",
        "",
        "- missing required features are censored, never nonfills;",
        "- full depth unavailable (ancestry + continuous sequence unproved);",
        "- Pinnacle unavailable; shape unavailable without non-AIM mapping;",
        "- bookmaker/FV conditional but unused by the v1 candidate grid;",
        "- own fingerprints subtract contributed volume only and never confirm",
        "  a market signal.",
        "",
        "Round-2 scoring, tuning, ablation evaluation, and holdout access have not",
        "occurred.",
        "",
    ])


def freeze(repo: Path, output: Path) -> None:
    branch = git(repo, "branch", "--show-current").decode().strip()
    if branch != "codex/window1-definition":
        raise FreezeError(f"wrong branch: {branch}")
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    if head != PARENT_COMMIT:
        raise FreezeError(f"unexpected PRE-RUN parent: {head}")
    contracts = validate_contracts(repo)
    receipts = {
        relative: index_receipt(repo, relative)
        for relative in BOUND_PATHS
    }
    guard = contracts["guard"]["derived_guard"]
    start = contracts["start_summary"]
    candidates = contracts["candidates"]
    features = contracts["features"]
    metric = contracts["metric"]
    proof = contracts["proof"]
    manifest = {
        "schema_version": VERSION,
        "freeze_status": "frozen_not_scored",
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "branch": branch,
        "parent_commit": head,
        "controlling_round1_audit": audit_receipt(repo),
        "round1_correction": {
            "selected_metrics": {
                "D": 804, "C": 10, "PC": 9, "S": 9, "IC": 4
            },
            "nonfill_replacement": {
                "genuine_zero_fill": 582,
                "naked_single_leg_fill": 84,
                "zero_length_window1_opportunity": 12,
            },
            "pair_divot_core_rows_struck": 4,
        },
        "development_dates_utc": DEVELOPMENT_DATES,
        "sealed_holdout_dates_utc": HOLDOUT_DATES,
        "holdout_opened": False,
        "holdout_queried": False,
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "ablation_scoring_performed": False,
        "D": 804,
        "target_PC": 603,
        "adapter": {
            "adapter_id": contracts["adapter"]["adapter_id"],
            "adapter_schema_version": contracts["adapter"]["schema_version"],
            "instrument_version": contracts["adapter"]["instrument_version"],
            "receipt": receipts[ADAPTER_PATH],
        },
        "candidate_policy_ids": list(candidates["candidate_ids"]),
        "candidate_policy_ids_sha256": canonical_sha256(
            candidates["candidate_ids"]
        ),
        "predeclared_ablations": list(
            candidates["predeclared_selected_candidate_ablations"]
        ),
        "predeclared_ablations_sha256": canonical_sha256(
            candidates["predeclared_selected_candidate_ablations"]
        ),
        "parameter_surface": candidates["common_parameters"],
        "parameter_surface_sha256": canonical_sha256(
            candidates["common_parameters"]
        ),
        "free_numeric_parameters": [],
        "allowed_feature_families": list(features["allowed"]),
        "allowed_feature_families_sha256": canonical_sha256(
            features["allowed"]
        ),
        "metric_contract": metric,
        "metric_contract_sha256": receipts[METRIC_PATH]["sha256"],
        "delta_reference_law": metric["definitions"],
        "start_boundary_law": {
            **guard,
            "one_sided_conflict_law": start["one_sided_conflict_law"],
            "source_conservation": start["source_conservation"],
            "official_exact": 234,
            "quantized_late_detection_proxy": 453,
            "positive_capable_before_named_censors": 718,
            "positive_capable_after_named_censors": 705,
            "schedule_only_positive_allowed": False,
            "proxy_promotable_to_exact": False,
        },
        "capability_gate": {
            "gate_pass": True,
            "advertised_family_count": proof["advertised_family_count"],
            "failed_or_inert_families": [],
            "receipt": receipts[
                f"{OUTPUT_RELATIVE}/ROUND2_CAPABILITY_PROOF.json"
            ],
        },
        "t8_t6_lookahead_proof": proof["t8_t6_lookahead_proof"],
        "unavailable": {
            "pinnacle": "zero causal rows",
            "full_depth": (
                "snapshot ancestry plus gap-free sequence-continuous "
                "reconstruction not proved"
            ),
            "shape": "no independent non-AIM causal cell mapping",
            "sealed_pair_policy": "uncommitted source; not reconstructed",
            "riser_actuator": "lawfully disarmed",
        },
        "prohibitions": [
            "schedule_as_start",
            "future_information",
            "post_decision_reference",
            "self_trade_confirmation",
            "narrow_proxy_substitution",
            "feature_gap_imputation",
            "denominator_change",
            "holdout_access",
            "production_or_live_mutation",
        ],
        "source_and_code_receipts": receipts,
        "hash_basis": "staged_git_blob_lf",
        "invariants": {
            "D_immutable": True,
            "target_PC_603": True,
            "all_candidates_complete_two_leg_stream": True,
            "per_leg_independent_timestamps": True,
            "schedule_only_positive_prohibited": True,
            "missing_feature_censored": True,
            "future_information_prohibited": True,
            "own_activity_never_confirms_market": True,
            "holdout_unopened": True,
            "round2_not_scored": True,
        },
    }
    manifest_path = output / "PRE_RUN_MANIFEST.json"
    report_path = output / "PRE_RUN_REPORT.md"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report_path.write_text(
        render_report(manifest), encoding="utf-8", newline="\n"
    )
    artifacts = {}
    for path in sorted(output.iterdir()):
        if path.name == "ARTIFACT_MANIFEST.json" or not path.is_file():
            continue
        raw = path.read_bytes()
        artifacts[path.name] = {
            "bytes": len(raw),
            "sha256": sha256_bytes(raw),
        }
    (output / "ARTIFACT_MANIFEST.json").write_text(
        json.dumps(
            {
                "schema_version": "window1-round2-prerun-artifacts-v1",
                "artifacts": artifacts,
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "freeze"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument(
        "--output-dir", type=Path, default=Path(OUTPUT_RELATIVE)
    )
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
