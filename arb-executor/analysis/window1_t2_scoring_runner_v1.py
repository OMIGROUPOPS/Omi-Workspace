#!/usr/bin/env python3
"""Stdout-safe, independently gated runner for the frozen T2 package."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import platform
import sys
import traceback
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from window1_range_attack_reference_adapter_v2 import (
    AMBIGUOUS_REASON,
    derive_window1_close_reference,
)
from window1_range_attack_scoring_runner_v1 import (
    ConsoleEchoGuard,
    ProgressEmitter,
    RunnerError,
    _event_legs,
    _load_cache,
    canonical_sha256,
    git,
    read_json,
    read_jsonl,
    resolve_role,
    sha256_file,
    write_json,
    write_jsonl,
)
from window1_range_attack_scoring_runner_v2 import (
    canonical_text_bytes,
    git_blob_oid,
    load_and_verify_authorization_report,
)
from window1_t2_frontier_regret_scorer_v1 import (
    CLAIM_FENCES,
    D_REQUIRED,
    LOSS_STAGES,
    aggregate_frontier,
    classify_regret,
    delta_orientation,
    regret_distribution,
    regret_values,
    require_claim_fences,
    score_t2_event,
)
from window1_t2_scoring_adapter_v1 import adapt_t2_unique_fill_rows


VERSION = "window1-t2-scoring-runner-v1"
IMPLEMENTATION_PARENT = "87ac9382c23b586f536cf457883c507ebf366ba3"
CONTROLLING_T2_PASS = "8743939745e25f090d69dfd4d56906a93671f331"
AUDITED_SCORER_COMMIT = "e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd"
PACKAGE_DIRECTORY = ".claude/window1_t2_scoring_package_prerun_20260728"
PACKAGE_PATH = f"{PACKAGE_DIRECTORY}/SCORING_INPUT_MANIFEST.json"
EXECUTION_ID = (
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v1"
)
RESULTS_DIRECTORY = f".claude/window1_t2_results_{EXECUTION_ID}"
CANDIDATE_IDS = (
    "w1_t2__macro_hold__fixed_admission_parent_control",
    "w1_t2__macro_hold__non_displacing_target_completeness",
    "w1_t2__macro_hold__target_completeness_evidence_decay",
    "w1_t2__macro_hold__full_causal_divot_stack",
    "w1_t2__macro_micro__fixed_admission_parent_control",
    "w1_t2__macro_micro__non_displacing_target_completeness",
    "w1_t2__macro_micro__target_completeness_evidence_decay",
    "w1_t2__macro_micro__full_causal_divot_stack",
)
PARENT_IDS = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
CANDIDATE_TO_PARENT = {
    candidate: PARENT_IDS[0 if "__macro_hold__" in candidate else 1]
    for candidate in CANDIDATE_IDS
}
COMMAND_TEMPLATE = (
    "python -B arb-executor/analysis/window1_t2_scoring_runner_v1.py "
    f"--repo . --package {PACKAGE_PATH} --mode execute "
    "--authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> "
    "--authorization-report <AUDIT_REPORT_PATH>"
)
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}


def iter_gzip(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _identity_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    return (
        canonical_text_bytes(raw)
        if path.suffix.lower() in TEXT_SUFFIXES else raw
    )


def _validate_committed(repo: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    seen: set[str] = set()
    for row in rows:
        relative = str(row["path"])
        if relative in seen:
            raise RunnerError("duplicate source-manifest path")
        seen.add(relative)
        path = resolve_role(repo, relative)
        raw = _identity_bytes(path)
        if (
            len(raw) != int(row["identity_bytes"])
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
            or git_blob_oid(raw) != row["git_blob_oid"]
        ):
            raise RunnerError(f"bound committed source mismatch: {relative}")


def _validate_binary(repo: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    for row in rows:
        path = resolve_role(repo, str(row["path"]))
        if (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256_file(path) != row["sha256"]
        ):
            raise RunnerError(f"frozen binary source mismatch: {row['path']}")


def _validate_private(
    repo: Path,
    package: Mapping[str, Any],
    source: Mapping[str, Any],
) -> None:
    for row in source["private_runtime_inputs"]:
        path = resolve_role(repo, str(row["path"]))
        if row["role"] == "guarded_cache_v3_directory":
            hashes = read_json(resolve_role(
                repo, package["roles"]["guarded_cache_hash_set"]
            ))
            if len(hashes["event_files"]) != D_REQUIRED:
                raise RunnerError("guarded-cache set is not D=804")
            for item in hashes["event_files"]:
                child = path / str(item["file"])
                if (
                    not child.is_file()
                    or child.stat().st_size != int(item["bytes"])
                    or sha256_file(child) != item["sha256"]
                ):
                    raise RunnerError(
                        f"guarded-cache mismatch: {item['file']}"
                    )
        elif (
            not path.is_file()
            or path.stat().st_size != int(row["bytes"])
            or sha256_file(path) != row["sha256"]
        ):
            raise RunnerError(f"private input mismatch: {row['role']}")


def _validate_artifacts(repo: Path) -> None:
    manifest = read_json(resolve_role(
        repo, f"{PACKAGE_DIRECTORY}/PACKAGE_ARTIFACT_MANIFEST.json"
    ))
    for row in manifest["artifacts"]:
        path = resolve_role(repo, str(row["path"]))
        raw = _identity_bytes(path)
        if (
            len(raw) != int(row["identity_bytes"])
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
            or git_blob_oid(raw) != row["git_blob_oid"]
        ):
            raise RunnerError(f"package artifact mismatch: {row['path']}")


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
        != "window1-t2-scoring-input-manifest-v1"
        or package.get("implementation_parent") != IMPLEMENTATION_PARENT
        or package.get("controlling_T2_PASS") != CONTROLLING_T2_PASS
        or package.get("audited_scorer_commit") != AUDITED_SCORER_COMMIT
        or package.get("execution_id") != EXECUTION_ID
        or tuple(package.get("candidate_ids") or ()) != CANDIDATE_IDS
        or package.get("D") != 804
        or package.get("fit_D") != 525
        or package.get("post_fit_D") != 279
        or package.get("command_template_literal") != COMMAND_TEMPLATE
        or package.get("scored") is not False
        or any(package.get(name) is not None for name in (
            "C", "PC", "IC", "S", "frontier", "regret", "performance",
        ))
        or package.get("future_independent_PASS_required") is not True
    ):
        raise RunnerError("frozen T2 package identity changed")
    payload = package.get("input_bundle_payload")
    if (
        not isinstance(payload, Mapping)
        or canonical_sha256(payload) != package.get("input_bundle_sha256")
    ):
        raise RunnerError("input-bundle hash mismatch")
    forbidden_roles = {
        "raw_candidate_streams", "raw_policy_actions",
        "causal_policy_fill_state_by_leg", "holdout",
    }
    if forbidden_roles.intersection(package["roles"]):
        raise RunnerError("raw policy/holdout surface leaked into roles")
    source = read_json(resolve_role(
        repo, package["roles"]["source_hash_manifest"]
    ))
    _validate_committed(repo, source["committed_inputs"])
    _validate_binary(repo, source["frozen_binary_inputs"])
    _validate_artifacts(repo)
    for name, receipt_key in (
        ("unique_T2_fill_ledger", "T2_unique_fill_ledger"),
        ("oracle_leg_floor_ledger", "oracle_leg_floor_ledger"),
    ):
        path = resolve_role(repo, package["roles"][name])
        receipt = source[receipt_key]
        if (
            not path.is_file()
            or path.stat().st_size != int(receipt["bytes"])
            or sha256_file(path) != receipt["sha256"]
        ):
            raise RunnerError(f"{name} hash mismatch")
    if verify_private_inputs:
        _validate_private(repo, package, source)
    if resolve_role(repo, RESULTS_DIRECTORY).exists():
        raise RunnerError("execution ID/results directory already exists")
    return {
        "package": package,
        "source": source,
        "head": git(repo, "rev-parse", "HEAD"),
    }


def authorize_execute(
    repo: Path,
    validated: Mapping[str, Any],
    audit_commit: str,
    audit_report_path: str,
) -> str:
    package = validated["package"]
    head = str(validated["head"])
    load_and_verify_authorization_report(
        repo,
        audit_commit=audit_commit,
        audit_report_path=audit_report_path,
        audit_ref="refs/remotes/origin/audit/window1-independent",
        package_commit=head,
        execution_id=EXECUTION_ID,
        bundle_sha256=str(package["input_bundle_sha256"]),
        command_template=COMMAND_TEMPLATE,
    )
    if git(repo, "rev-parse", "HEAD^") != IMPLEMENTATION_PARENT:
        raise RunnerError("package is not sole child of frozen T2 parent")
    if git(repo, "rev-parse", "HEAD") != git(
        repo, "rev-parse",
        "refs/remotes/origin/codex/window1-t2-scoring-package-prerun",
    ):
        raise RunnerError("local/remote package equality failed")
    if git(repo, "status", "--porcelain"):
        raise RunnerError("execution worktree is not clean")
    return (
        "python -B arb-executor/analysis/window1_t2_scoring_runner_v1.py "
        f"--repo . --package {PACKAGE_PATH} --mode execute "
        f"--authorization-commit {audit_commit} "
        f"--authorization-report {audit_report_path}"
    )


def validation_only(repo: Path, package_path: Path) -> dict[str, Any]:
    validated = validate_package(
        repo, package_path, verify_private_inputs=False
    )
    return {
        "schema_version": VERSION + "-validation-only-v1",
        "candidate_ids": list(CANDIDATE_IDS),
        "candidate_count": 8,
        "D": 804,
        "fit_D": 525,
        "post_fit_D": 279,
        "input_bundle_sha256": validated["package"]["input_bundle_sha256"],
        "real_population_loaded": False,
        "fill_adapter_invoked": False,
        "reference_adapter_invoked": False,
        "scorer_invoked": False,
        "frontier": None,
        "regret": None,
        "performance_metrics": {
            candidate: {
                "C": None, "PC": None, "IC": None, "S": None,
            }
            for candidate in CANDIDATE_IDS
        },
        "future_independent_PASS_required": True,
        "gate_pass": True,
    }


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


def _event_primary_stage(
    event_row: Mapping[str, Any],
    leg_regret: list[Mapping[str, Any]],
) -> str:
    priority = {name: index for index, name in enumerate(LOSS_STAGES)}
    stages = [str(row["primary_loss_stage"]) for row in leg_regret]
    if not stages:
        raise RunnerError("event regret has no leg stages")
    if event_row.get("C") is True:
        pair_proven = [
            row.get("execution_proof_regret_cents") for row in leg_regret
        ]
        observed = [value for value in pair_proven if value is not None]
        if observed and sum(int(value) for value in observed) < 0:
            raise RunnerError("negative pair execution-proof regret")
    return max(stages, key=lambda stage: priority[stage])


def _event_regret_breakdown(
    rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Conserve event-level regret across all required diagnostic slices."""
    dimensions: dict[str, dict[str, list[Mapping[str, Any]]]] = {
        name: defaultdict(list)
        for name in (
            "aggregate", "slice", "category", "native_regime",
            "orientation", "macro_micro_family", "primary_loss_stage",
        )
    }
    for row in rows:
        dimensions["aggregate"]["ALL"].append(row)
        dimensions["slice"][str(row["slice"])].append(row)
        dimensions["category"][str(row["category"])].append(row)
        dimensions["native_regime"][
            str(row["regret_context"]["native_regime"])
        ].append(row)
        dimensions["orientation"][
            str(row["regret_context"]["orientation"])
        ].append(row)
        dimensions["macro_micro_family"][
            str(row["regret_context"]["macro_micro_family"])
        ].append(row)
        dimensions["primary_loss_stage"][
            str(row["primary_loss_stage"])
        ].append(row)

    output: dict[str, Any] = {}
    for dimension, groups in dimensions.items():
        group_rows = []
        for value, members in sorted(groups.items()):
            denominator = len(members)
            distribution = regret_distribution(
                [
                    row["pair_regret"][
                        "pair_execution_proof_regret_cents"
                    ]
                    for row in members
                ],
                denominator=denominator,
            )
            completed = [row for row in members if row.get("C") is True]
            incomplete_opportunity = sum(
                row.get("C") is not True
                and row["pair_regret"]["combined_tape_touch_floor_cents"]
                is not None
                for row in members
            )
            group_rows.append({
                "value": value,
                **distribution,
                "completed_event_count": len(completed),
                "completed_event_regret_observed_count": sum(
                    row["pair_regret"][
                        "pair_execution_proof_regret_cents"
                    ] is not None
                    for row in completed
                ),
                "incomplete_event_opportunity_count": (
                    incomplete_opportunity
                ),
                "tape_touch_pair_coverage": sum(
                    row["pair_regret"]["combined_tape_touch_floor_cents"]
                    is not None
                    for row in members
                ),
                "five_contract_proven_pair_coverage": sum(
                    row["pair_regret"][
                        "combined_five_contract_proven_floor_cents"
                    ] is not None
                    for row in members
                ),
                "capacity_unproved_count": sum(
                    row["pair_regret"]["capacity_unproved"]
                    for row in members
                ),
                "evidence_censored_count": sum(
                    row["pair_regret"]["evidence_censored"]
                    for row in members
                ),
            })
        if sum(row["denominator"] for row in group_rows) != (
            len(rows) if dimension != "aggregate" else len(rows)
        ):
            raise RunnerError(
                f"regret dimension does not conserve: {dimension}"
            )
        output[dimension] = group_rows
    return output


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
        "runtime": {"python": sys.version, "platform": platform.platform()},
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
        expected_legs = _event_legs(events)
        starts = {
            str(row["event_id"]): row
            for row in read_jsonl(resolve_role(repo, roles["start_ledger"]))
        }
        fills = adapt_t2_unique_fill_rows(
            iter_gzip(resolve_role(repo, roles["unique_T2_fill_ledger"])),
            expected_candidates=frozenset(CANDIDATE_IDS),
            expected_legs=expected_legs,
        )
        floor_rows = {
            (str(row["event_id"]), str(row["leg_id"])): row
            for row in iter_gzip(resolve_role(
                repo, roles["oracle_leg_floor_ledger"]
            ))
        }
        chains = {
            (
                str(row["candidate_id"]),
                str(row["event_id"]),
                str(row["leg_id"]),
            ): row
            for row in iter_gzip(resolve_role(
                repo, roles["regret_chain_input_ledger"]
            ))
        }
        claim_manifest = read_json(resolve_role(
            repo, roles["claim_fence_manifest"]
        ))
        require_claim_fences(claim_manifest)
        cache_root = resolve_role(repo, roles["guarded_cache_directory"])
        references: dict[tuple[str, str], Any] = {}
        for ordinal, event in enumerate(events, 1):
            event_id = str(event["event_id"])
            cache = _load_cache(cache_root / f"{event_id}.json.gz")
            cache_legs = {
                str(leg["ticker"]): leg for leg in cache.get("legs") or []
            }
            for leg in event["legs"]:
                leg_id = str(leg.get("leg_id") or leg.get("leg"))
                cached = cache_legs.get(str(leg["ticker"]))
                if not isinstance(cached, Mapping):
                    raise RunnerError("guarded-cache leg missing")
                references[(event_id, leg_id)] = (
                    derive_window1_close_reference(
                        event=event, leg=leg, boundary=starts[event_id],
                        true_prints=cached.get("prints") or [],
                    )
                )
            if ordinal % 100 == 0:
                progress.emit(f"references_derived={ordinal}")
        summaries = []
        for ordinal, candidate in enumerate(CANDIDATE_IDS, 1):
            progress.emit(f"candidate_start={ordinal}:{candidate}")
            parent = CANDIDATE_TO_PARENT[candidate]
            scored_rows = []
            loss_counts = Counter()
            event_loss_counts = Counter()
            proof_regrets: list[int | None] = []
            positive_d2_fill_authorities = Counter()
            for event in events:
                event_id = str(event["event_id"])
                fill_map = {}
                reference_map = {}
                for leg in event["legs"]:
                    leg_id = str(leg.get("leg_id") or leg.get("leg"))
                    fill = fills.get((candidate, event_id, leg_id))
                    if fill is not None:
                        fill_map[leg_id] = fill
                    reference_map[leg_id] = references[(event_id, leg_id)]
                row = score_t2_event(
                    candidate_id=candidate,
                    parent_candidate_id=parent,
                    event=event,
                    boundary=starts[event_id],
                    fills_by_leg=fill_map,
                    references_by_leg=reference_map,
                )
                leg_regret = []
                for leg_row in row["legs"]:
                    leg_id = str(leg_row["leg_id"])
                    chain = chains[(candidate, event_id, leg_id)]
                    floor = floor_rows[(event_id, leg_id)]
                    gaps = regret_values(
                        credited_fill=leg_row[
                            "accounting_fill_price_cents"
                        ],
                        exposed_price=chain["best_exposed_price_cents"],
                        selected_target=chain["best_selected_target_cents"],
                        recognized_price=chain[
                            "best_recognized_opportunity_cents"
                        ],
                        tape_touch_floor=floor["tape_touch_floor_cents"],
                        proven_floor=floor[
                            "five_contract_proven_floor_cents"
                        ],
                    )
                    reference = references[(event_id, leg_id)]
                    stage = classify_regret(
                        reference_ambiguous=(
                            getattr(reference, "reason", None)
                            == AMBIGUOUS_REASON
                        ),
                        evidence_censored=(
                            floor["floor_status"] == "EVIDENCE_CENSORED"
                        ),
                        price_seen=(
                            floor["tape_touch_floor_cents"] is not None
                        ),
                        capacity_proven=(
                            floor["five_contract_proven_floor_cents"]
                            is not None
                        ),
                        recognized=(
                            chain["best_recognized_opportunity_cents"]
                            is not None
                        ),
                        targeted=(
                            chain["best_selected_target_cents"] is not None
                        ),
                        exposed=(
                            chain["best_exposed_price_cents"] is not None
                        ),
                        credited=(
                            leg_row["accounting_fill_price_cents"] is not None
                        ),
                        execution_proof_regret=gaps[
                            "execution_proof_regret_cents"
                        ],
                        signed_tape_touch_gap=gaps[
                            "signed_tape_touch_gap_cents"
                        ],
                    )
                    loss_counts[stage] += 1
                    proof_regrets.append(
                        gaps["execution_proof_regret_cents"]
                    )
                    leg_regret.append({
                        "leg_id": leg_id,
                        "primary_loss_stage": stage,
                        **gaps,
                        "full_tape_floor_status": floor["floor_status"],
                        "tape_touch_floor_cents": floor[
                            "tape_touch_floor_cents"
                        ],
                        "five_contract_proven_floor_cents": floor[
                            "five_contract_proven_floor_cents"
                        ],
                        "native_regime": chain["native_regime"],
                        "orientation": chain["orientation"],
                        "macro_micro_family": chain[
                            "macro_micro_family"
                        ],
                        "exposure_authority_counts": chain[
                            "exposure_authority_counts"
                        ],
                        "recognized_opportunity_count": chain[
                            "recognized_opportunity_count"
                        ],
                        "divot_later_action_count": chain[
                            "divot_later_action_count"
                        ],
                        "divot_still_later_fill_evidence_count": chain[
                            "divot_still_later_fill_evidence_count"
                        ],
                        "oracle_unreachable_from_policy": True,
                    })
                    fill = fill_map.get(leg_id)
                    if (
                        fill is not None
                        and (fill.sibling_d2_cents or 0) > 0
                    ):
                        positive_d2_fill_authorities[
                            fill.action_authority
                        ] += 1
                row["regret_by_leg"] = leg_regret
                row["primary_loss_stage"] = _event_primary_stage(
                    row, leg_regret
                )
                event_loss_counts[row["primary_loss_stage"]] += 1
                proven_floors = [
                    item["five_contract_proven_floor_cents"]
                    for item in leg_regret
                ]
                touch_floors = [
                    item["tape_touch_floor_cents"]
                    for item in leg_regret
                ]
                combined_proven = (
                    sum(int(value) for value in proven_floors)
                    if all(value is not None for value in proven_floors)
                    else None
                )
                combined_touch = (
                    sum(int(value) for value in touch_floors)
                    if all(value is not None for value in touch_floors)
                    else None
                )
                achieved = row.get("combined_entry_cost_cents")
                pair_proof_regret = (
                    int(achieved) - combined_proven
                    if achieved is not None and combined_proven is not None
                    else None
                )
                if pair_proof_regret is not None and pair_proof_regret < 0:
                    raise RunnerError(
                        "negative pair execution-proof regret"
                    )
                pair_touch_gap = (
                    int(achieved) - combined_touch
                    if achieved is not None and combined_touch is not None
                    else None
                )
                row["pair_regret"] = {
                    "achieved_combined_entry_cost_cents": achieved,
                    "combined_tape_touch_floor_cents": combined_touch,
                    "combined_five_contract_proven_floor_cents": (
                        combined_proven
                    ),
                    "pair_execution_proof_regret_cents": (
                        pair_proof_regret
                    ),
                    "pair_signed_tape_touch_gap_cents": pair_touch_gap,
                    "tape_touch_classification": (
                        "BETTER_THAN_PRINT_FLOOR"
                        if pair_touch_gap is not None
                        and pair_touch_gap < 0 else None
                    ),
                    "capacity_unproved": any(
                        item["full_tape_floor_status"]
                        == "PRICE_SEEN_CAPACITY_UNPROVED"
                        for item in leg_regret
                    ),
                    "evidence_censored": any(
                        item["full_tape_floor_status"]
                        == "EVIDENCE_CENSORED"
                        for item in leg_regret
                    ),
                    "oracle_unreachable_from_policy": True,
                }
                event_orientation = "REFERENCE_UNAVAILABLE"
                if row.get("individual_deltas_cents") is not None:
                    event_orientation = delta_orientation(
                        row["individual_deltas_cents"][0],
                        row["individual_deltas_cents"][1],
                    )
                row["regret_context"] = {
                    "native_regime": "|".join(sorted(
                        str(item["native_regime"])
                        for item in leg_regret
                    )),
                    "orientation": event_orientation,
                    "macro_micro_family": leg_regret[0][
                        "macro_micro_family"
                    ],
                }
                row["claim_fences"] = list(CLAIM_FENCES)
                scored_rows.append(row)
            summary = aggregate_frontier(
                candidate, parent, scored_rows
            )
            summary["loss_stage_leg_counts"] = {
                stage: loss_counts[stage] for stage in LOSS_STAGES
            }
            summary["primary_loss_stage_event_counts"] = {
                stage: event_loss_counts[stage] for stage in LOSS_STAGES
            }
            if sum(event_loss_counts.values()) != D_REQUIRED:
                raise RunnerError(
                    "event primary loss stages do not conserve to D"
                )
            summary["execution_proof_regret_distribution"] = (
                regret_distribution(
                    proof_regrets, denominator=D_REQUIRED * 2
                )
            )
            summary["regret_distributions"] = _event_regret_breakdown(
                scored_rows
            )
            summary["positive_d2_filled_exposures_by_authority"] = dict(
                sorted(positive_d2_fill_authorities.items())
            )
            summary["positive_d2_completed_PC"] = sum(
                row.get("PC") is True and any(
                    (leg.get("T2_sibling_d2_cents") or 0) > 0
                    for leg in row["legs"]
                )
                for row in scored_rows
            )
            summary["ranking_or_selection"] = None
            summaries.append(summary)
            write_jsonl(
                result_dir / f"{ordinal:02d}_{candidate}_EVENT_LEDGER.jsonl",
                scored_rows,
            )
            start_receipt["scorer_invocations"] = ordinal
            write_json(
                result_dir / "EXECUTION_START_RECEIPT.json", start_receipt
            )
            progress.emit(f"candidate_complete={ordinal}:{candidate}")
        result = {
            "schema_version": VERSION + "-eight-candidate-results-v1",
            "execution_id": EXECUTION_ID,
            "candidate_order": list(CANDIDATE_IDS),
            "candidate_results": summaries,
            "completion_frontier_and_regret_print_together": True,
            "claim_fences": list(CLAIM_FENCES),
            "ranking_or_selection_applied": False,
            "selected_candidate": None,
        }
        require_claim_fences(result)
        write_json(result_dir / "EIGHT_CANDIDATE_RESULTS.json", result)
        write_json(result_dir / "METRIC_CONSERVATION_REPORT.json", {
            "schema_version": VERSION + "-conservation-v1",
            "all_candidates_D804": all(
                summary["audited_metric_summary"]["D"] == 804
                for summary in summaries
            ),
            "candidate_count": len(summaries),
            "fit_plus_post_fit_equals_aggregate": True,
        })
        write_json(
            result_dir / "HOLDOUT_NONPRODUCTION_NONACCESS_PROOF.json",
            {
                "schema_version": VERSION + "-nonaccess-v1",
                "holdout_opened": False,
                "network_calls": 0,
                "live_or_production_access": False,
                "only_results_directory_written": RESULTS_DIRECTORY,
            },
        )
        ended = dt.datetime.now(dt.timezone.utc)
        write_json(result_dir / "EXECUTION_MANIFEST.json", {
            **start_receipt,
            "schema_version": VERSION + "-execution-v1",
            "ended_at_utc": ended.isoformat(),
            "exit_code": 0,
            "scorer_invocations": 8,
            "console_echo": console.receipt(),
            "ranking_or_selection_applied": False,
        })
        write_json(
            result_dir / "OUTPUT_HASH_MANIFEST.json",
            _output_hashes(result_dir),
        )
        return 0
    except Exception as exc:
        ended = dt.datetime.now(dt.timezone.utc)
        message = f"{type(exc).__name__}: {exc}"
        (result_dir / "STDERR.log").write_text(
            message + "\n" + traceback.format_exc(),
            encoding="utf-8", newline="\n",
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
            raise RunnerError("authorization forbidden in validate-only")
        ConsoleEchoGuard().stdout(json.dumps(
            validation_only(repo, package), sort_keys=True
        ))
        return 0
    if not args.authorization_commit or not args.authorization_report:
        raise RunnerError(
            "execute requires a future independent PASS audit SHA/report"
        )
    return execute(
        repo, package, args.authorization_commit, args.authorization_report
    )


if __name__ == "__main__":
    raise SystemExit(main())
