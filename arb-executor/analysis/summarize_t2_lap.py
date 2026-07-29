from __future__ import annotations

import argparse
import json
from pathlib import Path

ALIASES = {
    "w1_t2__macro_hold__fixed_admission_parent_control": "hold/control",
    "w1_t2__macro_hold__non_displacing_target_completeness": "hold/non-displacing",
    "w1_t2__macro_hold__target_completeness_evidence_decay": "hold/decay",
    "w1_t2__macro_hold__full_causal_divot_stack": "hold/full-divot",
    "w1_t2__macro_micro__fixed_admission_parent_control": "micro/control",
    "w1_t2__macro_micro__non_displacing_target_completeness": "micro/non-displacing",
    "w1_t2__macro_micro__target_completeness_evidence_decay": "micro/decay",
    "w1_t2__macro_micro__full_causal_divot_stack": "micro/full-divot",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.results.read_text(encoding="utf-8"))
    rows = []
    for candidate in data["candidate_results"]:
        metrics = candidate["audited_metric_summary"]
        raw = metrics["raw_integers_before_percentages"]
        frontier = candidate["frontier"]
        aggregate = frontier["aggregate"]
        regret = candidate["execution_proof_regret_distribution"]
        stage_regret = {
            row["value"]: {
                "events": row["completed_event_count"],
                "observed": row["observed_count"],
                "cents": row["total_cents_left_on_table"],
            }
            for row in candidate["regret_distributions"][
                "primary_loss_stage"
            ]
        }
        authority = candidate[
            "authority_omitted_d2_loss_attribution"
        ]["aggregate"]
        rows.append(
            {
                "candidate": ALIASES[candidate["candidate_id"]],
                "candidate_id": candidate["candidate_id"],
                "aggregate": {
                    key: {
                        metric: aggregate[key][metric]
                        for metric in ("C", "PC", "IC", "S")
                    }
                    for key in (
                        "LE_93",
                        "LE_95",
                        "LE_97",
                        "LT_100",
                        "ANY_PRICE",
                    )
                },
                "overall": {
                    key: raw[key] for key in ("D", "C", "PC", "IC", "S")
                },
                "fit_any": {
                    key: frontier["fit"]["ANY_PRICE"][key]
                    for key in ("C", "PC", "IC", "S")
                },
                "post_fit_any": {
                    key: frontier["post_fit"]["ANY_PRICE"][key]
                    for key in ("C", "PC", "IC", "S")
                },
                "regret": {
                    key: regret[key]
                    for key in (
                        "observed_count",
                        "null_or_censored_count",
                        "median",
                        "p75",
                        "p90",
                        "total_cents_left_on_table",
                        "zero_regret_count",
                    )
                },
                "regret_by_primary_stage": stage_regret,
                "authority_omitted_d2": {
                    "partition_target_count": authority[
                        "partition_target_count"
                    ],
                    "target_level_source_count": authority[
                        "target_level_source_count"
                    ],
                    "partitions": authority["partitions"],
                },
                "positive_d2_completed_PC": candidate[
                    "positive_d2_completed_PC"
                ],
                "positive_d2_filled_exposures_by_authority": candidate[
                    "positive_d2_filled_exposures_by_authority"
                ],
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
