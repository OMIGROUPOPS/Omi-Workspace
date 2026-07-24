#!/usr/bin/env python3
"""Find real-development decision witnesses for each Round-2 family."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import window1_round2_data_binding as binding
import window1_round2_instrument as instrument
import window1_round2_real_capability as capability


VERSION = "window1-round2-actual-family-proof-v1"
PROVABLE_FAMILIES = [
    "asynchronous_divot_timing",
    "leg_specific_posture",
    "nonself_one_cent_walk",
    "first_fill_sibling_response",
    "pair_divot_recut",
    "causal_orientation",
    "causal_drift_recognition",
    "true_print_flow",
    "bbo_top5_pressure",
]


class ProofError(RuntimeError):
    """Raised when a claimed family has no real decision witness."""


def _disabled_policy(
    spec: dict[str, Any],
    candidate_id: str,
    family: str,
) -> dict[str, Any]:
    ablation = f"without_{family}"
    if ablation in spec["predeclared_selected_candidate_ablations"]:
        return instrument.candidate_policy(
            spec, candidate_id, ablations=[ablation]
        )
    if family != "true_print_flow":
        raise ProofError(f"no proof-only disable path: {family}")
    policy = copy.deepcopy(
        instrument.candidate_policy(spec, candidate_id)
    )
    policy["candidate_id"] = candidate_id + "__proof_without_true_print_flow"
    policy["enabled_families"] = [
        value for value in policy["enabled_families"]
        if value != "true_print_flow"
    ]
    policy["ablations"] = ["proof_without_true_print_flow"]
    return policy


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.resolve()
    binding.validate_bound_inputs(
        repo,
        args.binding_manifest.resolve(),
        events_path=args.events.resolve(),
        prints_path=args.prints.resolve(),
        tape_manifest_path=args.tape_manifest.resolve(),
        cache_root=args.market_cache.resolve(),
    )
    prior = json.loads(
        args.capability_receipt.read_text(encoding="utf-8")
    )
    if (
        prior.get("D") != binding.D_REQUIRED
        or prior.get("candidate_gate_pass") is not True
        or prior.get("candidate_scoring_performed") is not False
    ):
        raise ProofError("real capability receipt is not a lawful base")
    events = capability.read_jsonl(args.events.resolve())
    seed_source = None
    if args.witness_seed is not None:
        seeded = json.loads(
            args.witness_seed.read_text(encoding="utf-8")
        )
        seed_ids = [
            str(row["event_id"])
            for row in seeded.get("family_witnesses") or []
        ]
        if set(seed_ids):
            by_id = {str(row["event_id"]): row for row in events}
            if not set(seed_ids).issubset(by_id):
                raise ProofError("witness seed event is outside D=804")
            ordered_ids = list(dict.fromkeys(seed_ids))
            events = [by_id[event_id] for event_id in ordered_ids] + [
                row for row in events
                if str(row["event_id"]) not in set(ordered_ids)
            ]
            seed_source = {
                "receipt": str(args.witness_seed),
                "event_ids": ordered_ids,
                "role": "capability witness replay only",
                "performance_outcomes_used": False,
            }
    features = [
        row for row in capability.read_jsonl(
            repo / binding.FEATURE_LEDGER
        )
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in features
    }
    spec = instrument.load_candidate_spec(repo)
    candidate_id = "r2_full_os__walk_park__hold"
    if candidate_id not in spec["candidate_ids"]:
        raise ProofError("full-stack witness candidate not retained")
    base_policy = instrument.candidate_policy(spec, candidate_id)
    disabled = {
        family: _disabled_policy(spec, candidate_id, family)
        for family in PROVABLE_FAMILIES
    }
    surfaces = instrument.load_surfaces(repo)
    corridor = float(
        spec["common_parameters"]["policy_corridor_seconds_after_anchor"]
    )
    witnesses: dict[str, dict[str, Any]] = {}
    for index, event in enumerate(events, 1):
        event_id = str(event["event_id"])
        normalized = capability.normalize_event(
            event,
            capability.load_cache(
                args.market_cache.resolve() / f"{event_id}.json.gz"
            ),
            feature_map,
            corridor_seconds=corridor,
        )
        base = instrument.CausalInstrument(
            surfaces, base_policy
        ).run(normalized)
        base_signature = capability.decision_signature(base)
        for family in PROVABLE_FAMILIES:
            if family in witnesses:
                continue
            contrast = instrument.CausalInstrument(
                surfaces, disabled[family]
            ).run(normalized)
            contrast_signature = capability.decision_signature(contrast)
            if base_signature != contrast_signature:
                witnesses[family] = {
                    "family_id": family,
                    "event_id": event_id,
                    "event_date": event["event_date"],
                    "candidate_id": candidate_id,
                    "proof_mode": (
                        "same_real_causal_history_isolated_family_disable"
                    ),
                    "enabled_decision_sha256": (
                        instrument.sha256_json(base_signature)
                    ),
                    "disabled_decision_sha256": (
                        instrument.sha256_json(contrast_signature)
                    ),
                    "enabled_decision_count": len(base_signature),
                    "disabled_decision_count": len(contrast_signature),
                    "decision_changing": True,
                    "scored": False,
                }
        if len(witnesses) == len(PROVABLE_FAMILIES):
            break
        if index % 50 == 0:
            print(json.dumps({
                "events_examined": index,
                "proved_families": sorted(witnesses),
                "scored": False,
            }, sort_keys=True), flush=True)
    missing = sorted(set(PROVABLE_FAMILIES) - set(witnesses))
    if missing:
        raise ProofError(
            "advertised real family is inert/unproved: "
            + ",".join(missing)
        )
    return {
        "schema_version": VERSION,
        "D": binding.D_REQUIRED,
        "candidate_id": candidate_id,
        "events_examined_until_all_witnesses": index,
        "witness_seed": seed_source,
        "family_witnesses": [
            witnesses[family] for family in PROVABLE_FAMILIES
        ],
        "unavailable_or_noncoverage": [
            {
                "family_id": "cohort_steering",
                "status": "unavailable_NO_CALL",
                "decision_changing": False,
                "counted_as_coverage": False,
                "reason": (
                    "all real cohort cells remain below frozen n=30; "
                    "underlying policy continues"
                ),
            },
            {
                "family_id": "own_order_contribution_subtraction",
                "status": "safety_law_inert_on_development",
                "decision_changing": False,
                "counted_as_coverage": False,
                "reason": (
                    "all 1,608 T8 receipts report zero attributable "
                    "own volume; subtraction remains mandatory if present"
                ),
            },
            {
                "family_id": "start_boundary_evaluator",
                "status": "evaluation_only",
                "decision_changing": False,
                "counted_as_coverage": False,
                "reason": "realized start is inaccessible to policy code",
            },
        ],
        "gate_pass": True,
        "candidate_scoring_performed": False,
        "performance_ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--binding-manifest", type=Path, required=True)
    parser.add_argument("--capability-receipt", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--prints", type=Path, required=True)
    parser.add_argument("--tape-manifest", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--witness-seed", type=Path)
    args = parser.parse_args()
    value = run(args)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "output": str(args.output),
        "family_witnesses": len(value["family_witnesses"]),
        "events_examined": value["events_examined_until_all_witnesses"],
        "gate_pass": value["gate_pass"],
        "scored": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
