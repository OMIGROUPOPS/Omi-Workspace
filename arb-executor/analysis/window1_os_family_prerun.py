#!/usr/bin/env python3
"""Build the mandatory code/data/metric PRE-RUN freeze."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


VERSION = "window1-os-family-prerun-v2"
D_REQUIRED = 804
TARGET = 603
DEV_DATES = [f"2026-07-{day:02d}" for day in range(12, 21)]
HOLDOUT_DATES = [f"2026-07-{day:02d}" for day in range(24, 27)]
PROHIBITED_SHA256 = (
    "6183ddec56eaab2ad48432aa7c802ea6265e608fa26cdd960aa1dde866824356"
)


class PreRunError(RuntimeError):
    """A mandatory PRE-RUN invariant failed."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def directory_receipt(path: Path) -> dict[str, Any]:
    files = sorted(path.glob("*.json.gz"), key=lambda item: item.name)
    if len(files) != D_REQUIRED:
        raise PreRunError(
            f"market-cache event count changed: {len(files)}"
        )
    rows = [{
        "name": item.name,
        "bytes": item.stat().st_size,
        "sha256": sha256_file(item),
    } for item in files]
    with gzip.open(files[0], "rt", encoding="utf-8") as handle:
        sample = json.load(handle)
    return {
        "files": len(files),
        "bytes": sum(row["bytes"] for row in rows),
        "hash_set_sha256": canonical_hash(rows),
        "cache_version": sample.get("cache_version"),
        "cache_key": sample.get("cache_key"),
    }


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PreRunError(f"JSON object required: {path}")
    return value


def git_head(repo: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def receipt(repo: Path, locator: str) -> dict[str, Any]:
    path = (repo / locator).resolve()
    if not path.is_file():
        raise PreRunError(f"missing frozen input: {locator}")
    if not str(path).startswith(str(repo.resolve())):
        raise PreRunError(f"frozen input outside repository: {locator}")
    return {
        "locator": locator.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        raise PreRunError(f"refusing to overwrite: {output}")

    candidate_path = repo / args.candidates
    allowlist_path = repo / args.feature_allowlist
    adapter_path = repo / args.adapter
    metric_path = repo / args.metric_contract
    holdout_path = repo / args.holdout
    start_summary_path = repo / args.start_summary
    start_ledger_path = repo / args.start_ledger
    candidates = read_json(candidate_path)
    allowlist = read_json(allowlist_path)
    adapter = read_json(adapter_path)
    metric = read_json(metric_path)
    holdout = read_json(holdout_path)
    start_summary = read_json(start_summary_path)

    development = candidates.get("development_period") or {}
    if (
        development.get("start") != DEV_DATES[0]
        or development.get("end") != DEV_DATES[-1]
        or development.get("D") != D_REQUIRED
    ):
        raise PreRunError("development period/D is not July 12-20 / 804")
    if (
        holdout.get("holdout_dates") != HOLDOUT_DATES
        or holdout.get("holdout_opened") is not False
        or holdout.get("holdout_queried") is not False
    ):
        raise PreRunError("July 24-26 holdout is not frozen unopened")
    if (
        metric.get("D") != D_REQUIRED
        or metric.get("target_count") != TARGET
        or metric.get("primary_objective_raw") != "PC >= 603"
    ):
        raise PreRunError("metric D/target changed")
    if start_summary.get("D") != D_REQUIRED:
        raise PreRunError("corrected start D changed")
    if start_summary.get("source_conservation") != {
        "clean_interval": 31,
        "contradictory": 14,
        "live_by_only": 52,
        "schedule_only": 20,
        "start_clock": 687,
    }:
        raise PreRunError("start source conservation changed")
    if (
        start_summary.get("positive_capable_after_named_censors") != 705
        or (start_summary.get("guard") or {}).get(
            "positive_guard_seconds"
        ) != 900.0
        or (start_summary.get("guard") or {}).get(
            "negative_guard_seconds"
        ) != 600.0
    ):
        raise PreRunError("corrected start gate/guard changed")

    permitted = candidates.get("permitted_policy_ids") or []
    if len(permitted) != 24 or len(set(permitted)) != 24:
        raise PreRunError("policy allowlist is not exactly 24 unique ids")
    expected = []
    for family in candidates.get("families") or []:
        family_id = str(family["family_id"])
        for posture in ("park", "walk"):
            for response in ("hold", "reaim"):
                expected.append(
                    f"{family_id}__{posture}__{response}"
                )
    if permitted != expected:
        raise PreRunError("policy allowlist/order differs from grid")
    if (
        candidates.get("parameter_ranges", {}).get(
            "free_numeric_parameters"
        ) != []
        or candidates.get("selection_law", {}).get(
            "target_count"
        ) != TARGET
    ):
        raise PreRunError("candidate parameters/selection law changed")
    constants = candidates.get("frozen_numeric_constants") or {}
    if (
        constants.get("walk_max_moves") != 2
        or constants.get("recognition_hour") != 6
        or constants.get("recognition_min_purity") != 0.5
        or constants.get("pressure_ratio_threshold") != 1.5
    ):
        raise PreRunError("frozen numeric constants changed")

    hard_exclusions = set(candidates.get("hard_exclusions") or [])
    required_exclusions = {
        "aim_v2", "pinnacle", "unproven_reconstructed_full_depth",
        "future_information", "window2", "exits", "settlement", "dca",
        "narrow_walk_law_proxy_substitution",
        "post_result_feature_or_parameter",
    }
    if not required_exclusions.issubset(hard_exclusions):
        raise PreRunError("candidate exclusion set is incomplete")
    if allowlist.get("proxy_substitution_allowed") is not False:
        raise PreRunError("proxy substitution is not forbidden")
    if allowlist.get("feature_gap_imputation_allowed") is not False:
        raise PreRunError("feature-gap imputation is not forbidden")
    if (
        adapter.get("adapter_id")
        != "chronological-window1-os-family-development-adapter-v2"
        or adapter.get("real_start") != args.start_ledger
    ):
        raise PreRunError("adapter/start-ledger binding changed")

    repository_locators = [
        args.candidates,
        args.feature_allowlist,
        args.adapter,
        args.metric_contract,
        args.holdout,
        args.start_summary,
        args.start_ledger,
        args.feature_matrix,
        args.source_coverage,
        args.spaces_materialization,
        "arb-executor/analysis/window1_os_family_prerun.py",
        "arb-executor/analysis/window1_os_family_search.py",
        "arb-executor/analysis/window1_start_guard.py",
        "arb-executor/analysis/window1_fit_benchmark.py",
        "arb-executor/analysis/window1_execution_kernel.py",
        "arb-executor/tests/test_window1_os_family_search.py",
        ".claude/entrysurface_20260717/band_map_v1.json",
        ".claude/entrysurface_20260717/entry_tables_sealed_v1.json",
        ".claude/entrysurface_20260717/divot_tables_v1.json",
        ".claude/entrysurface_20260717/drift_surfaces_v1.json",
        ".claude/master_20260709/cohort.json",
        ".claude/trendpath/ORIENT_V1.json",
        ".claude/seqfloor_20260708/recut_cells.json",
        ".claude/trendpath/ATLAS_V1.json",
        ".claude/takerreach/LAW.json",
        "arb-executor/data/shape_corpus/manifest.json",
        ".claude/loop8_20260720/SEAL_CEREMONY_20260720.md",
        ".claude/proof_20260720/PROOF_DUAL_DIVOT_SEAL.md",
    ]
    receipts = {
        locator: receipt(repo, locator)
        for locator in repository_locators
    }
    if PROHIBITED_SHA256 in {
        row["sha256"] for row in receipts.values()
    }:
        raise PreRunError("prohibited AIM_V2 blob entered freeze")

    events_path = Path(args.events).resolve()
    prints_path = Path(args.prints).resolve()
    tape_manifest_path = Path(args.tape_manifest).resolve()
    market_cache_path = Path(args.market_cache_source).resolve()
    market_cache_receipt = directory_receipt(market_cache_path)
    event_ids = {
        str(json.loads(line)["event_id"])
        for line in events_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    cache_event_ids = {
        item.name[:-8]
        for item in market_cache_path.glob("*.json.gz")
    }
    if len(event_ids) != D_REQUIRED or cache_event_ids != event_ids:
        raise PreRunError("market-cache/event identity set differs")
    private_receipts = {
        "development_events": {
            "bytes": events_path.stat().st_size,
            "sha256": sha256_file(events_path),
            "D": D_REQUIRED,
            "dates": DEV_DATES,
        },
        "normalized_true_prints": {
            "bytes": prints_path.stat().st_size,
            "sha256": sha256_file(prints_path),
        },
        "public_tape_manifest": {
            "bytes": tape_manifest_path.stat().st_size,
            "sha256": sha256_file(tape_manifest_path),
        },
        "validated_event_market_cache": market_cache_receipt,
    }
    tape_manifest = read_json(tape_manifest_path)
    expected_print_hash = (
        tape_manifest.get("artifacts", {})
        .get("normalized_true_prints", {})
        .get("sha256")
    )
    if (
        expected_print_hash
        != private_receipts["normalized_true_prints"]["sha256"]
    ):
        raise PreRunError("true-print file differs from tape manifest")

    freeze = {
        "schema_version": VERSION,
        "git_head_before_prerun_commit": git_head(repo),
        "branch": args.branch,
        "execution_order": {
            "candidate_scoring_performed": False,
            "candidate_results_opened": False,
            "pre_run_commit_and_push_required_before_scoring": True,
        },
        "development": {
            "dates": DEV_DATES,
            "D": D_REQUIRED,
            "target_PC": TARGET,
        },
        "holdout": {
            "dates": HOLDOUT_DATES,
            "opened": False,
            "queried": False,
        },
        "start_boundary": {
            "guard_id": "te-calibration-central-93pct-asymmetric-v1",
            "official_guard_seconds": 60,
            "proxy_positive_guard_seconds": 900,
            "proxy_negative_guard_seconds": 600,
            "ambiguous": "censored",
            "named_proxy_censors": 13,
            "positive_capable_after_named_censors": 705,
        },
        "adapter_id": adapter["adapter_id"],
        "candidate_policy_ids": permitted,
        "candidate_policy_ids_sha256": canonical_hash(permitted),
        "candidate_generation_sha256": canonical_hash(
            candidates["candidate_generation"]
        ),
        "parameter_ranges_sha256": canonical_hash(
            candidates["parameter_ranges"]
        ),
        "execution_parameters_sha256": canonical_hash(
            candidates["execution_parameters"]
        ),
        "frozen_numeric_constants": constants,
        "frozen_numeric_constants_sha256": canonical_hash(constants),
        "predeclared_ablations": candidates[
            "predeclared_ablations"
        ],
        "predeclared_ablations_sha256": canonical_hash(
            candidates["predeclared_ablations"]
        ),
        "allowed_feature_families": allowlist["allowed"],
        "allowed_feature_families_sha256": canonical_hash(
            allowlist["allowed"]
        ),
        "metric_contract_sha256": receipts[
            args.metric_contract
        ]["sha256"],
        "delta_reference_law": metric["reference_law"],
        "prohibitions": {
            "schedule_as_start": True,
            "future_information": True,
            "narrow_proxy_substitution": True,
            "feature_gap_imputation": True,
            "aim_v2": True,
            "pinnacle": True,
            "unproven_full_depth": True,
            "window2_exits_settlement_dca": True,
        },
        "repository_input_receipts": receipts,
        "private_development_input_receipts": private_receipts,
        "source_hash_bundle_sha256": canonical_hash({
            **{key: value["sha256"] for key, value in receipts.items()},
            **{
                key: (
                    value.get("sha256")
                    or value.get("hash_set_sha256")
                )
                for key, value in private_receipts.items()
            },
        }),
        "independent_audit_provenance": {
            "branch": "origin/audit/window1-independent",
            "commit": (
                "9919de9462f3df4a0bd33239b7e8f648b71e20fb"
            ),
            "artifact": "START_LEDGER_V4_CROSS_REVIEW.md",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(freeze, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(output),
        "D": D_REQUIRED,
        "policies": len(permitted),
        "candidate_scoring_performed": False,
        "holdout_opened": False,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", default=Path(__file__).parents[2])
    result.add_argument("--branch", default="codex/window1-definition")
    result.add_argument(
        "--candidates",
        default=(
            "arb-executor/docs/research/window1/"
            "WINDOW1_OS_FAMILY_CANDIDATES_V1.json"
        ),
    )
    result.add_argument(
        "--feature-allowlist",
        default=(
            "arb-executor/docs/research/window1/"
            "WINDOW1_OS_FAMILY_FEATURE_ALLOWLIST_V1.json"
        ),
    )
    result.add_argument(
        "--adapter",
        default=(
            "arb-executor/docs/research/window1/"
            "WINDOW1_OS_FAMILY_ADAPTER_V1.json"
        ),
    )
    result.add_argument(
        "--metric-contract",
        default=(
            "arb-executor/docs/research/window1/"
            "WINDOW1_OS_FAMILY_METRIC_CONTRACT_V1.json"
        ),
    )
    result.add_argument(
        "--holdout",
        default=(
            "arb-executor/docs/research/window1/"
            "WINDOW1_OS_FAMILY_PROSPECTIVE_HOLDOUT_V1.json"
        ),
    )
    result.add_argument(
        "--start-summary",
        default=(
            ".claude/window1_start_guard_corrected_20260724/"
            "REAL_START_SUMMARY_V5.json"
        ),
    )
    result.add_argument(
        "--start-ledger",
        default=(
            ".claude/window1_start_guard_corrected_20260724/"
            "REAL_START_LEDGER_V5.jsonl"
        ),
    )
    result.add_argument(
        "--feature-matrix",
        default=".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl",
    )
    result.add_argument("--tape-manifest", required=True)
    result.add_argument("--market-cache-source", required=True)
    result.add_argument(
        "--source-coverage",
        default=(
            ".claude/window1_20260721/SOURCE_COVERAGE_SUMMARY.json"
        ),
    )
    result.add_argument(
        "--spaces-materialization",
        default=(
            ".claude/window1_20260721/"
            "SPACES_MATERIALIZATION_SUMMARY.json"
        ),
    )
    result.add_argument("--events", required=True)
    result.add_argument("--prints", required=True)
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
