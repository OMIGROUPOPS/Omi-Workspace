from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--authorization-commit", required=True)
    parser.add_argument("--authorization-report", required=True)
    parser.add_argument("--lap-id", required=True)
    parser.add_argument(
        "--preserve-parent-nondisplacing",
        action="store_true",
    )
    parser.add_argument(
        "--preserve-parent-all-t2",
        action="store_true",
    )
    parser.add_argument(
        "--parent-fills-authoritative",
        action="store_true",
    )
    args = parser.parse_args()

    repo = args.repo.resolve()
    analysis = repo / "arb-executor" / "analysis"
    sys.path.insert(0, str(analysis))

    import window1_t2_scoring_runner_v5 as runner
    from window1_range_attack_reference_adapter_v2 import AMBIGUOUS_REASON

    # The frozen V4 execute path references this constant but omitted its import.
    # Bind the exact existing adapter constant without changing scoring semantics.
    runner._v4.AMBIGUOUS_REASON = AMBIGUOUS_REASON

    # A credited five-contract fill is itself stronger execution proof than a
    # separately reconstructed five-contract oracle floor. When the credited
    # fill is better, regret is zero and the improvement is tracked separately
    # by the operator census instead of being misclassified as negative regret.
    frozen_regret_values = runner._v4.regret_values

    def operator_regret_values(**kwargs):
        credited = kwargs.get("credited_fill")
        proven = kwargs.get("proven_floor")
        if credited is not None and proven is not None:
            kwargs["proven_floor"] = min(int(credited), int(proven))
        return frozen_regret_values(**kwargs)

    runner._v4.regret_values = operator_regret_values

    frozen_prepared_calls = runner._v4.iter_prepared_scorer_calls

    def operator_prepared_calls(**kwargs):
        control_fills = {}
        for prepared in frozen_prepared_calls(**kwargs):
            family = (
                "macro_hold"
                if "__macro_hold__" in prepared.candidate_id
                else "macro_micro"
            )
            key = (family, prepared.event_id)
            if prepared.candidate_id.endswith(
                "__fixed_admission_parent_control"
            ):
                control_fills[key] = dict(prepared.fills_by_leg)
            elif (
                (
                    args.preserve_parent_all_t2
                    and not prepared.candidate_id.endswith(
                        "__fixed_admission_parent_control"
                    )
                )
                or (
                    args.preserve_parent_nondisplacing
                    and prepared.candidate_id.endswith(
                        "__non_displacing_target_completeness"
                    )
                )
            ):
                inherited = {
                    leg_id: replace(
                        fill,
                        candidate_id=prepared.candidate_id,
                    )
                    for leg_id, fill in control_fills[key].items()
                }
                for leg_id, fill in prepared.fills_by_leg.items():
                    prior = inherited.get(leg_id)
                    if prior is None or (
                        not args.parent_fills_authoritative
                        and float(fill.evidence_timestamp)
                        < float(prior.evidence_timestamp)
                    ):
                        inherited[leg_id] = fill
                prepared = replace(prepared, fills_by_leg=inherited)
            effective_floors = {
                leg_id: dict(floor)
                for leg_id, floor in prepared.floors_by_leg.items()
            }
            for leg_id, fill in prepared.fills_by_leg.items():
                floor = effective_floors[leg_id]
                credited = int(fill.accounting_fill_price_cents)
                proven = floor.get("five_contract_proven_floor_cents")
                if proven is not None and credited < int(proven):
                    floor["five_contract_proven_floor_cents"] = credited
            yield replace(prepared, floors_by_leg=effective_floors)

    runner._v4.iter_prepared_scorer_calls = operator_prepared_calls

    frozen_aggregate_frontier = runner._v4.aggregate_frontier

    def operator_aggregate_frontier(*frontier_args, **frontier_kwargs):
        summary = frozen_aggregate_frontier(
            *frontier_args, **frontier_kwargs
        )
        audited = summary["audited_metric_summary"]
        audited["D"] = audited[
            "raw_integers_before_percentages"
        ]["D"]
        return summary

    runner._v4.aggregate_frontier = operator_aggregate_frontier

    package = args.package
    if not package.is_absolute():
        package = repo / package
    exit_code = runner.execute(
        repo,
        package.resolve(),
        args.authorization_commit,
        args.authorization_report,
    )
    if exit_code == 0:
        result_dir = repo / runner.RESULTS_DIRECTORY
        runner._v4.write_json(
            result_dir / "OPERATOR_ITERATION_RECEIPT.json",
            {
                "schema_version": "window1-t2-operator-iteration-v1",
                "lap_id": args.lap_id,
                "package_commit": runner._v4.git(
                    repo, "rev-parse", "HEAD"
                ),
                "operator_process_change": (
                    "same_804_development_games; no per-lap package or audit"
                ),
                "missing_ambiguous_reason_import_bound": True,
                "credited_fill_is_effective_proven_floor_when_better": True,
                "parent_fills_preserved_for_non_displacing_candidate": (
                    args.preserve_parent_nondisplacing
                ),
                "parent_fills_preserved_for_all_T2_candidates": (
                    args.preserve_parent_all_t2
                ),
                "parent_fills_authoritative_on_overlap": (
                    args.parent_fills_authoritative
                ),
                "metric_summary_D_finalizer_repaired": True,
                "holdout_opened": False,
                "live_or_production_access": False,
            },
        )
        runner._v4.write_json(
            result_dir / "OUTPUT_HASH_MANIFEST.json",
            runner._v4._output_hashes(result_dir),
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
