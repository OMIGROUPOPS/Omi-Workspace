from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument(
        "--candidate",
        default="w1_t2__macro_hold__fixed_admission_parent_control",
    )
    parser.add_argument(
        "--event",
        default="KXATPCHALLENGERMATCH-26JUL12FEAWAL",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo / "arb-executor" / "analysis"))

    import window1_t2_scoring_runner_v5 as runner
    from window1_t2_frontier_regret_scorer_v1 import score_t2_event
    from window1_t2_scoring_runtime_v4 import iter_prepared_scorer_calls

    package_path = args.package
    if not package_path.is_absolute():
        package_path = repo / package_path
    package = json.loads(package_path.read_text(encoding="utf-8"))
    prepared = next(
        call
        for call in iter_prepared_scorer_calls(
            repo=repo,
            roles=package["roles"],
            candidate_ids=runner.CANDIDATE_IDS,
            candidate_to_parent=runner.CANDIDATE_TO_PARENT,
        )
        if call.candidate_id == args.candidate
        and call.event_id == args.event
    )
    scored = score_t2_event(**prepared.score_kwargs)
    diagnostic = {
        "candidate_id": prepared.candidate_id,
        "event_id": prepared.event_id,
        "legs": [],
    }
    for leg in scored["legs"]:
        leg_id = str(leg["leg_id"])
        floor = prepared.floors_by_leg[leg_id]
        diagnostic["legs"].append(
            {
                "leg_id": leg_id,
                "accounting_fill_price_cents": leg[
                    "accounting_fill_price_cents"
                ],
                "tape_touch_floor_cents": floor[
                    "tape_touch_floor_cents"
                ],
                "five_contract_proven_floor_cents": floor[
                    "five_contract_proven_floor_cents"
                ],
                "floor_status": floor["floor_status"],
                "fill_binding": prepared.fills_by_leg.get(leg_id),
                "reference_binding": prepared.references_by_leg.get(leg_id),
            }
        )
    print(json.dumps(diagnostic, default=str, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
