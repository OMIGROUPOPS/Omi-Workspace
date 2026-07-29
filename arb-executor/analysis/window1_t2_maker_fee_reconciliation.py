from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


TIERS = (93, 95, 97)
QTY = 5


def transaction_fee_cents(price_cents: int, quantity: int) -> int:
    """Kalshi maker fee: ceil(1.75 * quantity * p * (1-p)) cents."""
    numerator = 7 * quantity * price_cents * (100 - price_cents)
    return (numerator + 39_999) // 40_000


def frontier(values: list[float]) -> dict[str, int]:
    return {
        "LE_93": sum(value <= 93 for value in values),
        "LE_95": sum(value <= 95 for value in values),
        "LE_97": sum(value <= 97 for value in values),
        "LT_100": sum(value < 100 for value in values),
        "ANY_PRICE": len(values),
    }


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def control_reconciliation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [row for row in rows if row["C"]]
    tape_covered = [
        row
        for row in rows
        if row["pair_regret"]["combined_five_contract_proven_floor_cents"]
        is not None
    ]

    policy_prefee = [row["combined_entry_cost_cents"] for row in completed]
    policy_net: list[float] = []
    policy_fee_cents: list[int] = []
    completed_detail: list[dict[str, Any]] = []
    for row in completed:
        legs = row["legs"]
        quantities = {leg["accounting_quantity"] for leg in legs}
        if quantities != {QTY}:
            raise ValueError(
                f"{row['event_id']}: expected both quantities to equal {QTY}, "
                f"got {sorted(quantities)}"
            )
        fees = [
            transaction_fee_cents(
                int(leg["accounting_fill_price_cents"]),
                int(leg["accounting_quantity"]),
            )
            for leg in legs
        ]
        total_fee = sum(fees)
        net_cost = row["combined_entry_cost_cents"] + total_fee / QTY
        references_complete = all(
            leg["window1_close_cents"] is not None for leg in legs
        )
        net_leg_deltas_total_cents = [
            (
                (
                    int(leg["accounting_fill_price_cents"])
                    - int(leg["window1_close_cents"])
                )
                * QTY
                + fee
            )
            for leg, fee in zip(legs, fees)
        ] if references_complete else []
        actual_fee_pc = bool(
            references_complete
            and sum(net_leg_deltas_total_cents) < 0
        )
        actual_fee_ic = bool(
            references_complete
            and all(delta < 0 for delta in net_leg_deltas_total_cents)
        )
        actual_fee_s = row["combined_entry_cost_cents"] * QTY + total_fee < 500
        policy_net.append(net_cost)
        policy_fee_cents.append(total_fee)
        completed_detail.append(
            {
                "event_id": row["event_id"],
                "slice": row["slice"],
                "fill_prices_cents": [
                    leg["accounting_fill_price_cents"] for leg in legs
                ],
                "combined_prefee_cents_per_contract": row[
                    "combined_entry_cost_cents"
                ],
                "fee_cents_total_for_five_contract_pair": total_fee,
                "combined_net_cents_per_contract": net_cost,
                "prefee_subpar": row["combined_entry_cost_cents"] < 100,
                "net_subpar": net_cost < 100,
                "prefee_PC": row["PC"],
                "prefee_IC": row["IC"],
                "prefee_S": row["S"],
                "actual_fee_PC": actual_fee_pc,
                "actual_fee_IC": actual_fee_ic,
                "actual_fee_S": actual_fee_s,
            }
        )

    tape_prefee: list[float] = []
    tape_net: list[float] = []
    for row in tape_covered:
        floors = [
            regret["five_contract_proven_floor_cents"]
            for regret in row["regret_by_leg"]
        ]
        if len(floors) != 2 or any(value is None for value in floors):
            raise ValueError(
                f"{row['event_id']}: pair floor exists without two leg floors"
            )
        prefee = sum(floors)
        if prefee != row["pair_regret"][
            "combined_five_contract_proven_floor_cents"
        ]:
            raise ValueError(f"{row['event_id']}: pair/leg floor mismatch")
        fees = [transaction_fee_cents(int(value), QTY) for value in floors]
        tape_prefee.append(prefee)
        tape_net.append(prefee + sum(fees) / QTY)

    opportunity_by_tier: dict[str, dict[str, int]] = {}
    tier_predicates = {
        "LE_93": lambda value: value <= 93,
        "LE_95": lambda value: value <= 95,
        "LE_97": lambda value: value <= 97,
        "LT_100": lambda value: value < 100,
        "ANY_PRICE": lambda value: True,
    }
    for tier, predicate in tier_predicates.items():
        eligible = [
            row
            for row in tape_covered
            if predicate(
                row["pair_regret"][
                    "combined_five_contract_proven_floor_cents"
                ]
            )
        ]
        completed_events = [row for row in eligible if row["C"]]
        achieved_at_tier = [
            row
            for row in completed_events
            if predicate(row["combined_entry_cost_cents"])
        ]
        opportunity_by_tier[tier] = {
            "tape_proven": len(eligible),
            "policy_completed_event_any_price": len(completed_events),
            "policy_achieved_at_same_tier": len(achieved_at_tier),
            "policy_completed_above_tier": (
                len(completed_events) - len(achieved_at_tier)
            ),
            "policy_missed_entirely": len(eligible) - len(completed_events),
        }

    missed = [row for row in tape_covered if not row["C"]]
    completed_pair_regrets = [
        row["pair_regret"]["pair_execution_proof_regret_cents"]
        for row in completed
        if row["pair_regret"]["pair_execution_proof_regret_cents"] is not None
    ]
    leg_regrets = [
        leg["execution_proof_regret_cents"]
        for row in rows
        for leg in row["regret_by_leg"]
        if leg["execution_proof_regret_cents"] is not None
    ]

    miss_by_slice_classification: dict[str, Counter[str]] = defaultdict(Counter)
    for row in missed:
        miss_by_slice_classification[row["slice"]][row["classification"]] += 1

    regret_map = {
        "tape_proven_opportunities": len(tape_covered),
        "policy_completions": len(completed),
        "proven_opportunities_missed": len(missed),
        "capture_rate_over_tape_proven": len(completed) / len(tape_covered),
        "opportunity_by_tier_prefee": opportunity_by_tier,
        "missed_by_classification": dict(
            sorted(Counter(row["classification"] for row in missed).items())
        ),
        "missed_by_primary_loss_stage": dict(
            sorted(Counter(row["primary_loss_stage"] for row in missed).items())
        ),
        "missed_by_slice_and_classification": {
            key: dict(sorted(value.items()))
            for key, value in sorted(miss_by_slice_classification.items())
        },
        "completed_pair_execution_regret": {
            "observed_count": len(completed_pair_regrets),
            "total_cents_per_contract": sum(completed_pair_regrets),
            "zero_count": sum(value == 0 for value in completed_pair_regrets),
            "positive_count": sum(value > 0 for value in completed_pair_regrets),
        },
        "leg_execution_regret": {
            "observed_count": len(leg_regrets),
            "total_cents_per_contract": sum(leg_regrets),
            "zero_count": sum(value == 0 for value in leg_regrets),
            "positive_count": sum(value > 0 for value in leg_regrets),
        },
    }

    prefee_subpar = [item for item in completed_detail if item["prefee_subpar"]]
    net_subpar = [item for item in completed_detail if item["net_subpar"]]
    return {
        "population": len(rows),
        "fee_law": {
            "schedule": "Kalshi maker",
            "formula": (
                "ceil(1.75 * quantity * p * (1-p)) cents per transaction"
            ),
            "p": "fill_price_cents / 100",
            "quantity": QTY,
            "published_rate_dollars": 0.0175,
        },
        "policy": {
            "completed_any_price": len(completed),
            "prefee_PC_IC_S": {
                "PC": sum(row["PC"] is True for row in completed),
                "IC": sum(row["IC"] is True for row in completed),
                "S": sum(row["S"] is True for row in completed),
            },
            "actual_fee_PC_IC_S": {
                "PC": sum(
                    item["actual_fee_PC"] for item in completed_detail
                ),
                "IC": sum(
                    item["actual_fee_IC"] for item in completed_detail
                ),
                "S": sum(
                    item["actual_fee_S"] for item in completed_detail
                ),
            },
            "prefee_frontier": frontier(policy_prefee),
            "actual_fee_frontier": frontier(policy_net),
            "prefee_subpar_count": len(prefee_subpar),
            "actual_fee_subpar_survivor_count": len(net_subpar),
            "subpar_lost_to_fees": len(prefee_subpar) - len(net_subpar),
            "total_fees_cents_for_completed_five_contract_pairs": sum(
                policy_fee_cents
            ),
            "completed_detail": completed_detail,
        },
        "full_tape_opportunity": {
            "proven_any_price": len(tape_covered),
            "evidence_censored_or_unproved": len(rows) - len(tape_covered),
            "prefee_frontier": frontier(tape_prefee),
            "actual_fee_frontier": frontier(tape_net),
        },
        "regret_map": regret_map,
    }


def render_markdown(result: dict[str, Any], ledger: Path) -> str:
    policy = result["policy"]
    tape = result["full_tape_opportunity"]
    regret = result["regret_map"]
    tiers = ("LE_93", "LE_95", "LE_97", "LT_100", "ANY_PRICE")
    lines = [
        "# Window-1 T2 hold-control maker-fee reconciliation",
        "",
        f"Source: `{ledger.name}`. Development sample only; D={result['population']}.",
        "Holdout sealed. No live, exchange, or trading-system access.",
        "",
        "## Fee-adjusted control frontier",
        "",
        "| basis | <=93 | <=95 | <=97 | <100 | any price |",
        "|---|---:|---:|---:|---:|---:|",
        "| policy, pre-fee | "
        + " | ".join(str(policy["prefee_frontier"][tier]) for tier in tiers)
        + " |",
        "| policy, maker fee curve | "
        + " | ".join(
            str(policy["actual_fee_frontier"][tier]) for tier in tiers
        )
        + " |",
        "| full-tape five-contract opportunity, pre-fee | "
        + " | ".join(str(tape["prefee_frontier"][tier]) for tier in tiers)
        + " |",
        "| full-tape five-contract opportunity, maker fee curve | "
        + " | ".join(str(tape["actual_fee_frontier"][tier]) for tier in tiers)
        + " |",
        "",
        (
            f"Of the {policy['prefee_subpar_count']} pre-fee sub-par policy "
            f"completions, {policy['actual_fee_subpar_survivor_count']} survive "
            f"the maker fee curve; {policy['subpar_lost_to_fees']} do not."
        ),
        "",
        (
            "PC/IC/S, pre-fee: "
            f"**{policy['prefee_PC_IC_S']['PC']}/"
            f"{policy['prefee_PC_IC_S']['IC']}/"
            f"{policy['prefee_PC_IC_S']['S']}**. "
            "PC/IC/S, maker fee curve: "
            f"**{policy['actual_fee_PC_IC_S']['PC']}/"
            f"{policy['actual_fee_PC_IC_S']['IC']}/"
            f"{policy['actual_fee_PC_IC_S']['S']}**."
        ),
        "",
        (
            f"Policy any-price completions: **{policy['completed_any_price']}**. "
            f"Full-tape proven any-price opportunities: "
            f"**{tape['proven_any_price']}**. Evidence censored/unproved: "
            f"**{tape['evidence_censored_or_unproved']}**."
        ),
        "",
        "## Control regret map",
        "",
        (
            f"The tape proves {regret['tape_proven_opportunities']} opportunities; "
            f"the policy completed {regret['policy_completions']} and missed "
            f"{regret['proven_opportunities_missed']} "
            f"({regret['capture_rate_over_tape_proven']:.2%} capture)."
        ),
        "",
        (
            "| tape floor | tape-proven | achieved at same tier | "
            "completed above tier | never completed |"
        ),
        "|---|---:|---:|---:|---:|",
    ]
    for tier in tiers:
        row = regret["opportunity_by_tier_prefee"][tier]
        lines.append(
            f"| {tier} | {row['tape_proven']} | "
            f"{row['policy_achieved_at_same_tier']} | "
            f"{row['policy_completed_above_tier']} | "
            f"{row['policy_missed_entirely']} |"
        )
    lines.extend(
        [
            "",
            "Misses by policy outcome: "
            + ", ".join(
                f"{key}={value}"
                for key, value in regret["missed_by_classification"].items()
            )
            + ".",
            "",
            (
                "Execution-price regret on completed pairs: "
                f"{regret['completed_pair_execution_regret']['total_cents_per_contract']} "
                "cents per-contract summed across "
                f"{regret['completed_pair_execution_regret']['observed_count']} "
                "observed completed pairs."
            ),
            "",
            (
                "Execution-price regret on observed legs: "
                f"{regret['leg_execution_regret']['total_cents_per_contract']} "
                "cents per-contract summed across "
                f"{regret['leg_execution_regret']['observed_count']} legs."
            ),
            "",
            "The full machine-readable map, including fit/post-fit splits and "
            "per-completion fees, is in the adjacent JSON receipt.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-ledger", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    args = parser.parse_args()

    result = control_reconciliation(load_rows(args.event_ledger))
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        with args.json_out.open(
            "w", encoding="utf-8", newline="\n"
        ) as stream:
            stream.write(encoded)
    else:
        print(encoded)
    if args.markdown_out:
        with args.markdown_out.open(
            "w", encoding="utf-8", newline="\n"
        ) as stream:
            stream.write(render_markdown(result, args.event_ledger))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
