from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo / "arb-executor" / "analysis"))

    import window1_t2_scoring_runner_v5 as runner
    from window1_t2_scoring_runtime_v4 import iter_prepared_scorer_calls

    package_path = args.package
    if not package_path.is_absolute():
        package_path = repo / package_path
    manifest = json.loads(
        package_path.read_text(encoding="utf-8")
    )
    rows: list[dict[str, object]] = []
    comparable = 0
    for prepared in iter_prepared_scorer_calls(
        repo=repo,
        roles=manifest["roles"],
        candidate_ids=runner.CANDIDATE_IDS,
        candidate_to_parent=runner.CANDIDATE_TO_PARENT,
    ):
        for leg_id, fill in prepared.fills_by_leg.items():
            floor = prepared.floors_by_leg[leg_id]
            proven = floor["five_contract_proven_floor_cents"]
            if proven is None:
                continue
            comparable += 1
            credited = int(fill.accounting_fill_price_cents)
            proven_i = int(proven)
            if credited >= proven_i:
                continue
            rows.append(
                {
                    "candidate_id": prepared.candidate_id,
                    "event_id": prepared.event_id,
                    "event_date": prepared.event_date,
                    "slice": (
                        "fit"
                        if prepared.event_date <= "2026-07-17"
                        else "post_fit"
                    ),
                    "leg_id": leg_id,
                    "credited_fill_cents": credited,
                    "proven_floor_cents": proven_i,
                    "better_by_cents": proven_i - credited,
                    "tape_touch_floor_cents": floor[
                        "tape_touch_floor_cents"
                    ],
                }
            )
    by_candidate = collections.Counter(
        str(row["candidate_id"]) for row in rows
    )
    by_slice = collections.Counter(str(row["slice"]) for row in rows)
    by_gap = collections.Counter(int(row["better_by_cents"]) for row in rows)
    print(
        json.dumps(
            {
                "comparable_fill_floor_bindings": comparable,
                "negative_execution_proof_rows": len(rows),
                "unique_event_legs": len(
                    {
                        (row["event_id"], row["leg_id"])
                        for row in rows
                    }
                ),
                "by_candidate": dict(sorted(by_candidate.items())),
                "by_slice": dict(sorted(by_slice.items())),
                "by_better_by_cents": {
                    str(key): value for key, value in sorted(by_gap.items())
                },
                "total_better_by_cents": sum(
                    int(row["better_by_cents"]) for row in rows
                ),
                "examples": rows[:20],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
