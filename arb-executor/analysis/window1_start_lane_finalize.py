#!/usr/bin/env python3
"""Publish the final receipts for the start-gated Window-1 development lane."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


VERSION = "window1-start-gated-development-lane-v1"
D = 804
TARGET = 603


class FinalizeError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FinalizeError(f"expected object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def assemble(
    start: Mapping[str, Any],
    historical: Mapping[str, Any],
    correction: Mapping[str, Any],
    preflight: Mapping[str, Any],
) -> dict[str, Any]:
    if (
        start.get("D") != D
        or historical.get("D") != D
        or correction.get("D") != D
        or int(start.get("provable_positive_population") or 0) >= TARGET
        or start.get("start_gate_pass") is not False
        or (preflight.get("start_gate") or {}).get("pass") is not False
        or preflight.get("candidate_scoring_performed") is not False
        or preflight.get("candidate_results_opened") is not False
    ):
        raise FinalizeError("start-gated stop law changed")
    classes = {
        key: int(start.get(key) or 0)
        for key in (
            "exact_starts",
            "clean_intervals",
            "live_by_only",
            "contradictory",
            "schedule_only",
            "unresolved",
        )
    }
    if sum(classes.values()) != D:
        raise FinalizeError("start denominator changed")
    return {
        "schema_version": VERSION,
        "scope": "July 12-20 development only; no candidate scoring",
        "D": D,
        "start_gate": {
            **classes,
            "provable_positive_population": start[
                "provable_positive_population"
            ],
            "required": TARGET,
            "missing": start["missing_from_start_gate"],
            "pass": False,
            "ledger_sha256": start["ledger_sha256"],
            "evidence_blocker": start["evidence_blocker"],
        },
        "historical_re_adjudication": {
            "dual_exact_five_witnesses": historical[
                "historical_dual_exact_five_events"
            ],
            "dual_witnesses_with_proven_post_start_leg": historical[
                "historical_dual_events_with_receipt_proven_post_start_leg"
            ],
            "permanently_post_start_filled_legs": historical[
                "permanently_post_start_filled_legs"
            ],
            "permanently_post_start_fill_events": historical[
                "permanently_post_start_fill_events"
            ],
            "newly_recovered_strict_window1_duals": historical[
                "newly_recovered_historical_strict_window1_duals"
            ],
            "ten_contract_overfill_outside_exact_five": historical[
                "ten_contract_overfill_outside_exact_five"
            ],
            "ruling_counts": historical["ruling_counts"],
        },
        "corrected_historical_bound": {
            "published_preserved": True,
            "published_upper": correction[
                "published_optimistic_upper_bound"
            ],
            "corrected_receipts_only_upper": correction[
                "corrected_receipts_only_optimistic_upper_bound"
            ],
            "corrected_rate_over_D": correction[
                "corrected_rate_over_D"
            ],
            "distance_from_target": correction[
                "distance_from_75_percent_target"
            ],
            "strict_lower": correction["strict_lower_bound"],
        },
        "development_candidate_preflight": {
            "contract_validation": preflight["contract_validation"],
            "family_count": preflight["family_count"],
            "policy_count": preflight["policy_count"],
            "candidate_spec_hash": preflight["freeze"][
                "candidate_spec_hash"
            ],
            "adapter_hash": preflight["freeze"]["adapter_hash"],
            "feature_allowlist_hash": preflight["freeze"][
                "causal_feature_allowlist_hash"
            ],
            "fill_kernel_hash": preflight["freeze"][
                "fill_kernel_hash"
            ],
            "metric_contract_hash": preflight["freeze"][
                "metric_contract_hash"
            ],
            "holdout_declaration_hash": preflight["freeze"][
                "prospective_holdout_declaration_hash"
            ],
            "code_commit": preflight["freeze"]["code_commit"],
            "aim_v2_excluded": preflight["aim_v2_excluded"],
            "candidate_scoring_performed": False,
            "candidate_results_opened": False,
            "holdout_opened": False,
            "stop_reason": preflight["stop_reason"],
        },
        "verdict_law": {
            "historical_replay_rejected_frozen_behavior_only": True,
            "market_ceiling_claimed": False,
            "full_os_family_failure_claimed": False,
            "strategy_75_percent_verdict_issued": False,
            "reason": "start gate below 603",
        },
    }


def report(result: Mapping[str, Any], start: Mapping[str, Any]) -> str:
    gate = result["start_gate"]
    hist = result["historical_re_adjudication"]
    bound = result["corrected_historical_bound"]
    preflight = result["development_candidate_preflight"]
    public = start["source_receipts"]["public_milestones"]
    shadow = start["source_receipts"]["raw_milestone_shadow"]
    return f"""# Window-1 receipt correction and official-start gate

## Start gate — FAIL

- D = {D}
- exact starts = {gate['exact_starts']}
- clean causal intervals = {gate['clean_intervals']}
- live-by-only = {gate['live_by_only']}
- contradictory = {gate['contradictory']}
- schedule-only = {gate['schedule_only']}
- unresolved = {gate['unresolved']}
- positive-Window-1-provable population = {gate['provable_positive_population']}
- required = {gate['required']}
- shortfall = {gate['missing']}

Only exact starts and clean causal intervals can prove a positive Window-1
dual.  The remaining {D - gate['provable_positive_population']} events are
blocked by timing: {gate['live_by_only']} have only a live-by upper bound,
{gate['contradictory']} have conflicting causal bounds, and
{gate['schedule_only']} have only a schedule bound.  Passing requires
{gate['missing']} additional event-resolved official starts or clean
two-sided causal intervals.

The complete official-provider export queried all {public['rows']} D events:
{public['accepted_exact']} produced accepted exact starts.  The raw milestone
shadow contributed {shadow['accepted_exact']} exact candidate records; after
source precedence and deduplication, four events selected that source.
Schedule was never promoted to an exact start.

## Historical re-adjudication

- historical dual exact-five witnesses = {hist['dual_exact_five_witnesses']}
- witnesses with a receipt-proven post-start leg = {hist['dual_witnesses_with_proven_post_start_leg']}
- permanently post-start filled legs/events = {hist['permanently_post_start_filled_legs']} / {hist['permanently_post_start_fill_events']}
- newly recovered strict Window-1 historical duals = {hist['newly_recovered_strict_window1_duals']}
- ten-contract overfill outside exact-five = {hist['ten_contract_overfill_outside_exact_five']}

No placement, cancellation, fill, price, or quantity was changed.

## Corrected historical receipt bound

The published 240-event upper bound remains preserved as prior evidence.
The corrected receipts-only upper bound is {bound['corrected_receipts_only_upper']}
of {D} ({bound['corrected_rate_over_D']:.6%}), with strict lower bound
{bound['strict_lower']}; it is {bound['distance_from_target']} events below
603.  This rejects the frozen historical behavior only.  It is not a market
ceiling or a full-OS-family result.

## Development candidate preflight

The chronological OS-family contracts validate: {preflight['family_count']}
families and {preflight['policy_count']} mechanically allowlisted policy IDs,
with no free numeric parameters.  AIM_V2, Pinnacle, unproven reconstructed
full depth, future information, proxy substitution, Window 2, exits,
settlement, and DCA are excluded.  Raw non-LATCHCAL shape-corpus observations
retain their independent pre-AIM derivation lineage; all AIM_V2-derived
cells, offsets, targets, and fallback tables remain excluded.

No candidate result was opened, no scoring or tuning ran, and no holdout was
opened.  The preflight stops mechanically because the start gate is below
603.  The July 24–26 baseline holdout remains preserved and unopened; no new
prospective dates have been selected.
"""


def run(args: argparse.Namespace) -> int:
    output = Path(args.output).resolve()
    inputs = {
        "start_summary": Path(args.start_summary).resolve(),
        "historical_summary": Path(args.historical_summary).resolve(),
        "receipt_correction": Path(args.receipt_correction).resolve(),
        "tuning_preflight": Path(args.tuning_preflight).resolve(),
    }
    values = {name: read_json(path) for name, path in inputs.items()}
    result = assemble(
        values["start_summary"],
        values["historical_summary"],
        values["receipt_correction"],
        values["tuning_preflight"],
    )
    result["input_receipts"] = {
        name: {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for name, path in inputs.items()
    }
    final_json = output / "FINAL_RESULTS.json"
    final_report = output / "FINAL_REPORT.md"
    write_json(final_json, result)
    final_report.write_text(
        report(result, values["start_summary"]),
        encoding="utf-8",
        newline="\n",
    )
    artifacts = {}
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "ARTIFACT_MANIFEST.json":
            artifacts[path.name] = {
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
    write_json(output / "ARTIFACT_MANIFEST.json", {
        "schema_version": VERSION,
        "D": D,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "candidate_scoring_performed": False,
        "holdout_opened": False,
    })
    print(json.dumps({
        "gate": result["start_gate"]["pass"],
        "provable": result["start_gate"][
            "provable_positive_population"
        ],
        "corrected_upper": result["corrected_historical_bound"][
            "corrected_receipts_only_upper"
        ],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--start-summary", required=True)
    result.add_argument("--historical-summary", required=True)
    result.add_argument("--receipt-correction", required=True)
    result.add_argument("--tuning-preflight", required=True)
    result.add_argument("--output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
