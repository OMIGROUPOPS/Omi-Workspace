#!/usr/bin/env python3
"""Sweep Window-1 T2 fee units and frozen-right enforcement.

This development-only diagnostic reads committed/frozen artifacts and the
already-built 804-game grid.  It does not execute a scorer, open holdout data,
create orders, or access a network.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import gzip
import json
import math
from pathlib import Path
import subprocess
from typing import Any, Iterable, Mapping


VERSION = "window1-t2-scoring-chain-sweep-v1"
QUANTITY = 5
GRID = (
    ".claude/window1_t2_iteration_history/WINDOW1_T2_GAME_GRID.json"
)
TARGET = (
    ".claude/window1_t2_iteration_history/"
    "WINDOW1_T2_SEQUENTIAL_ORACLE_AND_TARGET_LAP.json"
)
ASYNC_DIR = (
    ".claude/window1_asynchronous_opportunity_policy_census_v2_20260726"
)
DECISION_LEDGER = (
    ".claude/window1_decision_layer_attribution_prerun_20260727/"
    "DECISION_LAYER_EVENT_LEDGER.jsonl.gz"
)
T2_DIR = ".claude/window1_t2_causal_divot_prerun_20260727"


class SweepError(RuntimeError):
    """Fail-closed sweep error."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SweepError(f"JSON object required: {path}")
    return value


def gzip_rows(paths: Iterable[Path]) -> Iterable[dict[str, Any]]:
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise SweepError(f"object required: {path}:{line_number}")
                yield row


def maker_fee(price: int) -> int:
    return math.ceil(
        7 * QUANTITY * int(price) * (100 - int(price)) / 40000
    )


def historical_target(repo: Path, commit: str) -> dict[str, Any]:
    value = subprocess.check_output(
        [
            "git", "show",
            f"{commit}:{TARGET}",
        ],
        cwd=repo,
        text=True,
        encoding="utf-8",
    )
    return json.loads(value)


def set_changes(
    old_values: set[str],
    new_values: set[str],
) -> dict[str, Any]:
    return {
        "old_count": len(old_values),
        "new_count": len(new_values),
        "lost_count": len(old_values - new_values),
        "gained_count": len(new_values - old_values),
        "lost_event_ids": sorted(old_values - new_values),
        "gained_event_ids": sorted(new_values - old_values),
    }


def metric_sets(
    rows: list[Mapping[str, Any]],
    reference_kind: str,
) -> dict[str, set[str]]:
    output = {
        "prefee_PC": set(),
        "prefee_IC": set(),
        "maker_PC": set(),
        "maker_IC": set(),
    }
    for row in rows:
        if row["outcome"] != "completed":
            continue
        legs = list(row["legs"].values())
        fills = [int(leg["fill"]["price_cents"]) for leg in legs]
        if reference_kind == "ledger":
            references = [
                leg["frozen_reference"]["price_cents"] for leg in legs
            ]
        else:
            references = [
                leg["price_path"]["close"]["price_cents"] for leg in legs
            ]
        if not all(value is not None for value in references):
            continue
        deltas = [
            fills[index] - int(references[index])
            for index in range(2)
        ]
        fees = [maker_fee(price) for price in fills]
        event_id = str(row["event_id"])
        if sum(deltas) < 0:
            output["prefee_PC"].add(event_id)
        if all(value < 0 for value in deltas):
            output["prefee_IC"].add(event_id)
        if sum(
            deltas[index] * QUANTITY + fees[index]
            for index in range(2)
        ) < 0:
            output["maker_PC"].add(event_id)
        if all(
            deltas[index] * QUANTITY + fees[index] < 0
            for index in range(2)
        ):
            output["maker_IC"].add(event_id)
    return output


def horizon_reference(
    rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    after, changed, price_changed = [], [], []
    became_unavailable, became_available = [], []
    individual_delta_changed = []
    combined_delta_changed = []
    for row in rows:
        if row["boundary_status"] != "positive":
            continue
        event_id = str(row["event_id"])
        for leg_id, leg in row["legs"].items():
            old = leg["frozen_reference"]
            new = leg["price_path"]["close"]
            right = float(leg["price_path"]["window"]["right_ts"])
            if (
                old["timestamp"] is not None
                and float(old["timestamp"]) > right + 1e-6
            ):
                after.append((event_id, leg_id))
            if (
                old["price_cents"] != new["price_cents"]
                or bool(old["available"]) != bool(new["available"])
            ):
                changed.append((event_id, leg_id))
                if old["available"] and not new["available"]:
                    became_unavailable.append((event_id, leg_id))
                elif not old["available"] and new["available"]:
                    became_available.append((event_id, leg_id))
                else:
                    price_changed.append((event_id, leg_id))
            if row["outcome"] == "completed":
                fill = leg["fill"]
                old_delta = (
                    int(fill["price_cents"]) - int(old["price_cents"])
                    if old["price_cents"] is not None else None
                )
                new_delta = (
                    int(fill["price_cents"]) - int(new["price_cents"])
                    if new["price_cents"] is not None else None
                )
                if old_delta != new_delta:
                    individual_delta_changed.append({
                        "event_id": event_id,
                        "leg_id": leg_id,
                        "ledger_delta_cents_per_contract": old_delta,
                        "corrected_delta_cents_per_contract": new_delta,
                    })
        if row["outcome"] == "completed":
            legs = list(row["legs"].values())
            fill_sum = sum(
                int(leg["fill"]["price_cents"]) for leg in legs
            )
            old_refs = [
                leg["frozen_reference"]["price_cents"] for leg in legs
            ]
            new_refs = [
                leg["price_path"]["close"]["price_cents"] for leg in legs
            ]
            old_delta = (
                fill_sum - sum(int(value) for value in old_refs)
                if all(value is not None for value in old_refs) else None
            )
            new_delta = (
                fill_sum - sum(int(value) for value in new_refs)
                if all(value is not None for value in new_refs) else None
            )
            if old_delta != new_delta:
                combined_delta_changed.append({
                    "event_id": event_id,
                    "ledger_combined_delta_cents_per_contract": old_delta,
                    "corrected_combined_delta_cents_per_contract": new_delta,
                })
    old_sets = metric_sets(rows, "ledger")
    new_sets = metric_sets(rows, "right")
    return {
        "positive_event_count": sum(
            row["boundary_status"] == "positive" for row in rows
        ),
        "positive_leg_count": 2 * sum(
            row["boundary_status"] == "positive" for row in rows
        ),
        "ledger_reference_after_frozen_right_leg_count": len(after),
        "reference_value_or_availability_changed_leg_count": len(changed),
        "reference_changed_event_count": len({
            event_id for event_id, _ in changed
        }),
        "reference_price_changed_leg_count": len(price_changed),
        "reference_became_unavailable_leg_count": len(became_unavailable),
        "reference_became_available_leg_count": len(became_available),
        "completed_individual_delta_changed_leg_count": len(
            individual_delta_changed
        ),
        "completed_individual_delta_changed_event_count": len({
            row["event_id"] for row in individual_delta_changed
        }),
        "completed_combined_delta_changed_event_count": len(
            combined_delta_changed
        ),
        "completed_individual_delta_changes": individual_delta_changed,
        "completed_combined_delta_changes": combined_delta_changed,
        "metric_changes": {
            metric: set_changes(old_sets[metric], new_sets[metric])
            for metric in old_sets
        },
    }


def recognition_horizon(
    rows: list[Mapping[str, Any]],
    target_ids: set[str],
) -> dict[str, Any]:
    late_legs = []
    affected = set()
    for row in rows:
        if row["event_id"] not in target_ids:
            continue
        for leg_id, leg in row["legs"].items():
            recognition = leg["recognition"]
            if (
                recognition is not None
                and recognition["recognition_ts"] is not None
                and not recognition["inside_frozen_policy_window"]
            ):
                late_legs.append({
                    "event_id": row["event_id"],
                    "leg_id": leg_id,
                    "recognition_ts": recognition["recognition_ts"],
                    "right_ts": leg["price_path"]["window"]["right_ts"],
                })
                affected.add(str(row["event_id"]))
    return {
        "target_lap_population_before": len(target_ids),
        "late_recognition_leg_count": len(late_legs),
        "affected_event_count": len(affected),
        "affected_event_ids": sorted(affected),
        "target_lap_population_after": len(target_ids - affected),
        "late_recognition_legs": late_legs,
    }


def async_horizon(
    repo: Path,
    right: Mapping[tuple[str, str], float],
) -> dict[str, Any]:
    paths = [
        Path(path) for path in glob.glob(
            str(repo / ASYNC_DIR / "QUALIFYING_EPISODE_LEDGER_*.jsonl.gz")
        )
    ]
    total = 0
    late = 0
    events: set[str] = set()
    by_candidate: Counter[str] = Counter()
    max_late = 0.0
    for row in gzip_rows(sorted(paths)):
        total += 1
        excess = float(row["timestamp"]) - right[(
            str(row["event_id"]), str(row["sibling_leg_id"])
        )]
        if excess > 1e-6:
            late += 1
            events.add(str(row["event_id"]))
            by_candidate[str(row["candidate_id"])] += 1
            max_late = max(max_late, excess)
    return {
        "qualifying_episode_count": total,
        "after_frozen_right_episode_count": late,
        "after_frozen_right_event_count": len(events),
        "after_frozen_right_event_ids": sorted(events),
        "after_frozen_right_by_candidate": dict(sorted(by_candidate.items())),
        "maximum_seconds_after_frozen_right": max_late,
    }


def decision_horizon(
    repo: Path,
    right: Mapping[tuple[str, str], float],
) -> dict[str, Any]:
    total = 0
    earliest_late = []
    for row in gzip_rows([repo / DECISION_LEDGER]):
        total += 1
        opportunity = row.get("earliest_lawful_opportunity")
        if not opportunity:
            continue
        excess = float(opportunity["timestamp"]) - right[(
            str(row["event_id"]), str(row["sibling_leg_id"])
        )]
        if excess > 1e-6:
            earliest_late.append({
                "event_id": row["event_id"],
                "candidate_id": row["candidate_id"],
                "attributed_layer": row["attributed_layer"],
                "seconds_after_frozen_right": excess,
                "episode_id": opportunity["episode_id"],
            })
    return {
        "decision_attribution_row_count": total,
        "earliest_opportunity_after_frozen_right_row_count": len(
            earliest_late
        ),
        "affected_event_count": len({
            row["event_id"] for row in earliest_late
        }),
        "affected_event_ids": sorted({
            row["event_id"] for row in earliest_late
        }),
        "rows": earliest_late,
    }


def credited_fill_horizon(
    repo: Path,
    right: Mapping[tuple[str, str], float],
) -> dict[str, Any]:
    path = (
        repo
        / ".claude/window1_t2_scoring_package_prerun_20260728/"
        "T2_UNIQUE_CREDITED_FILL_LEDGER.jsonl.gz"
    )
    total = 0
    late = 0
    events: set[str] = set()
    candidates: Counter[str] = Counter()
    for row in gzip_rows([path]):
        total += 1
        if (
            float(row["evidence_timestamp"])
            > right[(str(row["event_id"]), str(row["leg_id"]))] + 1e-6
        ):
            late += 1
            events.add(str(row["event_id"]))
            candidates[str(row["candidate_id"])] += 1
    return {
        "all_candidate_credited_fill_count": total,
        "after_frozen_right_credited_fill_count": late,
        "after_frozen_right_event_count": len(events),
        "after_frozen_right_event_ids": sorted(events),
        "after_frozen_right_by_candidate": dict(sorted(candidates.items())),
    }


def t2_surface_horizon(
    repo: Path,
    right: Mapping[tuple[str, str], float],
) -> dict[str, Any]:
    paths = sorted((repo / T2_DIR).glob(
        "SIBLING_X_OPPORTUNITY_LEDGER_*.jsonl.gz"
    ))
    rows = late_rows = targets = late_targets = 0
    lawful_targets = late_lawful_targets = 0
    first_fill_late_rows = 0
    events: set[str] = set()
    candidates: Counter[str] = Counter()
    for index, row in enumerate(gzip_rows(paths), 1):
        rows += 1
        event_id = str(row["event_id"])
        leg_id = str(row["leg_id"])
        values = list(row.get("targets") or [])
        targets += len(values)
        lawful_targets += sum(bool(value.get("lawful")) for value in values)
        row_late = float(row["timestamp"]) > right[
            (event_id, leg_id)
        ] + 1e-6
        if row_late:
            late_rows += 1
            late_targets += len(values)
            late_lawful_targets += sum(
                bool(value.get("lawful")) for value in values
            )
            events.add(event_id)
            candidates[str(row["candidate_id"])] += 1
        first_leg_value = row.get("first_filled_leg")
        first_fill_value = row.get("first_fill_timestamp")
        if first_leg_value is not None and first_fill_value is not None:
            first_leg = str(first_leg_value)
            if (
                float(first_fill_value)
                > right[(event_id, first_leg)] + 1e-6
            ):
                first_fill_late_rows += 1
        if index % 250_000 == 0:
            print(f"t2_surface_rows={index}", flush=True)
    return {
        "surface_row_count": rows,
        "surface_target_entry_count": targets,
        "surface_lawful_target_entry_count": lawful_targets,
        "after_frozen_right_surface_row_count": late_rows,
        "after_frozen_right_target_entry_count": late_targets,
        "after_frozen_right_lawful_target_entry_count": late_lawful_targets,
        "after_frozen_right_event_count": len(events),
        "after_frozen_right_event_ids": sorted(events),
        "after_frozen_right_rows_by_candidate": dict(
            sorted(candidates.items())
        ),
        "rows_with_first_fill_after_frozen_right": first_fill_late_rows,
    }


def fee_transitions(
    repo: Path,
    grid: Mapping[str, Any],
    current_target: Mapping[str, Any],
    target_ids: set[str],
) -> dict[str, Any]:
    first = historical_target(repo, "e6f9ec90")
    corrected_pair = historical_target(repo, "42c45c8e")
    grid_rows = grid["games"]
    inclusive_ids = {
        str(row["event_id"]) for row in grid_rows
        if row["strict_sequential_oracle"]["maker_under_par"]
    }
    endpoint_added_ids = set()
    for row in grid_rows:
        sequence = row["strict_sequential_oracle"]
        if not sequence["maker_under_par"]:
            continue
        first_leg = sequence["first_leg_id"]
        second_leg = sequence["second_leg_id"]
        first_right = float(
            row["legs"][first_leg]["price_path"]["window"]["right_ts"]
        )
        second_right = float(
            row["legs"][second_leg]["price_path"]["window"]["right_ts"]
        )
        if (
            abs(float(sequence["first_floor_ts"]) - first_right) <= 1e-6
            or abs(float(sequence["second_floor_ts"]) - second_right) <= 1e-6
        ):
            endpoint_added_ids.add(str(row["event_id"]))
    preinclusive_ids = inclusive_ids - endpoint_added_ids
    inclusive_501 = inclusive_ids & target_ids
    preinclusive_501 = preinclusive_ids & target_ids
    committed_ids = set(
        corrected_pair["oracle_reconciliation"]["event_ids"][
            "strict_sequential_maker_under_par_all_804"
        ]
    )
    return {
        "pair_total_unit_fix": {
            "before_recognized_under_par": first[
                "strict_sequential_oracle"
            ]["maker_under_par_count"],
            "after_recognized_under_par": corrected_pair[
                "strict_sequential_oracle"
            ]["maker_under_par_count"],
            "before_negative_vs_reference": first[
                "strict_sequential_oracle"
            ]["negative_vs_reference_count"],
            "after_negative_vs_reference": corrected_pair[
                "strict_sequential_oracle"
            ]["negative_vs_reference_count"],
        },
        "second_leg_ranking_unit_fix": {
            "before_recognized_under_par": corrected_pair[
                "strict_sequential_oracle"
            ]["maker_under_par_count"],
            "after_recognized_under_par": len(preinclusive_501),
            "before_all_804_under_par": corrected_pair[
                "oracle_reconciliation"
            ]["strict_sequential_maker_under_par_all_804"],
            "after_all_804_under_par": len(preinclusive_ids),
            "gained_event_ids": sorted(
                preinclusive_ids - committed_ids
            ),
        },
        "inclusive_frozen_right_endpoint_fix": {
            "before_recognized_under_par": len(preinclusive_501),
            "after_recognized_under_par": len(inclusive_501),
            "before_all_804_under_par": len(preinclusive_ids),
            "after_all_804_under_par": len(inclusive_ids),
            "gained_event_ids": sorted(endpoint_added_ids),
        },
        "delta_and_floor_unit_sweep": {
            "additional_nonzero_fee_unit_mixups_in_completed_delta": 0,
            "additional_nonzero_fee_unit_mixups_in_five_contract_floor": 0,
            "frozen_zero_fee_per_contract_arithmetic_sites": [
                "arb-executor/analysis/window1_range_attack_scorer_v1.py:220",
                "arb-executor/analysis/window1_t2_scoring_adapter_v1.py:225",
                "arb-executor/analysis/window1_t2_scoring_adapter_v1.py:233",
                "arb-executor/analysis/window1_range_attack_instrument.py:248-253",
                "arb-executor/analysis/window1_t2_causal_divot_instrument.py:738-760",
            ],
            "zero_fee_effect": (
                "No current number moves because every one of these sites "
                "receives the frozen integer 0. They require an explicit "
                "per-contract fee unit if ever made nonzero."
            ),
        },
    }


def sequence_reference_counts(
    rows: list[Mapping[str, Any]],
    target_ids: set[str],
    removed_recognition_ids: set[str],
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    scopes = {
        "all_804": rows,
        "target_501_before_horizon_fix": [
            row for row in rows if row["event_id"] in target_ids
        ],
        "target_500_after_horizon_fix": [
            row for row in rows
            if row["event_id"] in target_ids
            and row["event_id"] not in removed_recognition_ids
        ],
    }
    for scope, values in scopes.items():
        result = {}
        for reference_kind in ("ledger", "corrected_frozen_right"):
            available = 0
            negative = 0
            for row in values:
                sequence = row["strict_sequential_oracle"]
                if not sequence["lawful"]:
                    continue
                if reference_kind == "ledger":
                    references = [
                        leg["frozen_reference"]["price_cents"]
                        for leg in row["legs"].values()
                    ]
                else:
                    references = [
                        leg["price_path"]["close"]["price_cents"]
                        for leg in row["legs"].values()
                    ]
                if not all(value is not None for value in references):
                    continue
                available += 1
                negative += (
                    int(sequence[
                        "maker_cost_total_cents_for_five_contract_pair"
                    ])
                    - sum(int(value) for value in references) * QUANTITY
                    < 0
                )
            result[reference_kind] = {
                "reference_available": available,
                "negative_vs_reference": negative,
            }
        output[scope] = result
    return output


def source_findings() -> list[dict[str, Any]]:
    return [
        {
            "kind": "fee_unit",
            "status": "fixed_active",
            "path": "arb-executor/analysis/window1_t2_target_laps.py",
            "site": "strict_sequential_floor pair total",
            "finding": (
                "A five-contract fee total had been added to a per-contract "
                "pair price. The comparison is now total-to-total."
            ),
        },
        {
            "kind": "fee_unit",
            "status": "fixed_active",
            "path": "arb-executor/analysis/window1_t2_target_laps.py",
            "site": "cheapest_fill_after ranking",
            "finding": (
                "The target price was per contract while maker_fee_cents was "
                "for the five-contract order. Ranking now uses target*5+fee."
            ),
        },
        {
            "kind": "fee_unit",
            "status": "correct",
            "path": (
                "arb-executor/analysis/"
                "window1_t2_maker_fee_reconciliation.py"
            ),
            "site": "control and tape maker-fee reconciliation",
            "finding": (
                "All comparisons either divide total fee by five before "
                "joining per-contract prices or multiply price/delta by five "
                "before joining order-total fees."
            ),
        },
        {
            "kind": "fee_unit",
            "status": "correct_unit_wrong_schedule_superseded",
            "path": (
                "arb-executor/analysis/"
                "window1_t2_control_reconciliation.py"
            ),
            "site": "control fee reconciliation",
            "finding": (
                "The unit conversion is correct; the formula is taker, not "
                "maker, and the maker reconciliation supersedes it."
            ),
        },
        {
            "kind": "fee_unit",
            "status": "latent_zero_only",
            "path": "arb-executor/analysis/window1_range_attack_scorer_v1.py",
            "site": "combined_delta = sum(deltas) + FEE_CENTS",
            "finding": (
                "This expression is per contract. Frozen FEE_CENTS is 0, so "
                "no number moves. A future order-total fee would be invalid."
            ),
        },
        {
            "kind": "fee_unit",
            "status": "latent_zero_only",
            "path": (
                "arb-executor/analysis/window1_t2_scoring_adapter_v1.py; "
                "window1_range_attack_instrument.py; "
                "window1_range_attack_instrument_v2.py; "
                "window1_t2_causal_divot_instrument.py"
            ),
            "site": "b2_max and d1+d2+fee headroom",
            "finding": (
                "d1 and d2 are per-contract cents. Fee is frozen integer 0. "
                "No current number moves, but the contract lacks an explicit "
                "per-contract unit."
            ),
        },
        {
            "kind": "fee_unit",
            "status": "unused_constant",
            "path": (
                "arb-executor/analysis/"
                "window1_t2_frontier_regret_scorer_v1.py"
            ),
            "site": "FEE_CENTS = 0",
            "finding": "The constant is declared but not used by this module.",
        },
        {
            "kind": "horizon",
            "status": "correct",
            "path": (
                "arb-executor/analysis/"
                "window1_range_attack_prerun_builder.py"
            ),
            "site": "range ladder and interval evaluation",
            "finding": (
                "Uses inclusive min(policy_decision_horizon, guarded_cutoff); "
                "the five-contract floors and fillability rows are correct."
            ),
        },
        {
            "kind": "horizon",
            "status": "correct",
            "path": (
                "arb-executor/analysis/"
                "window1_range_attack_guarded_fill_adapter_v1.py and v2"
            ),
            "site": "credited fill validation",
            "finding": (
                "Enforces evaluated_right_ts as well as guarded cutoff. No "
                "credited fill in the control ledger is after frozen right."
            ),
        },
        {
            "kind": "horizon",
            "status": "active_defect",
            "path": (
                "arb-executor/analysis/"
                "window1_range_attack_reference_adapter_v1.py and v2"
            ),
            "site": "Window-1 close reference",
            "finding": (
                "Reads through guarded cutoff without min with scheduled "
                "policy horizon. This propagates through Range-Attack runners, "
                "T2 runners V1-V5, and window1_t2_reference_boundary_v3."
            ),
        },
        {
            "kind": "horizon",
            "status": "active_defect",
            "path": (
                "arb-executor/analysis/"
                "window1_asynchronous_opportunity_policy_census_v2.py"
            ),
            "site": "raw sibling episode preparation and qualification",
            "finding": (
                "Uses boundary guarded_cutoff_ts as right instead of the "
                "shorter frozen range right."
            ),
        },
        {
            "kind": "horizon",
            "status": "downstream_contamination",
            "path": (
                "arb-executor/analysis/"
                "window1_decision_layer_attribution.py"
            ),
            "site": "fixed witness resolution",
            "finding": (
                "Consumes the contaminated V2 episode ledger and independently "
                "reads raw books/prints through guarded cutoff."
            ),
        },
        {
            "kind": "horizon",
            "status": "downstream_contamination",
            "path": (
                "arb-executor/analysis/"
                "window1_t2_causal_divot_prerun.py and "
                "window1_t2_causal_divot_instrument.py"
            ),
            "site": "T2 sibling opportunity and target surfaces",
            "finding": (
                "Consumes decision-layer attribution and emits trigger/target "
                "surfaces after frozen right; exact census is in this report."
            ),
        },
        {
            "kind": "horizon",
            "status": "secondary_validation_gap_no_observed_late_credit",
            "path": (
                "arb-executor/analysis/"
                "window1_t2_scoring_package_builder_v1.py"
            ),
            "site": "_derive_unique_fills",
            "finding": (
                "Rechecks guarded cutoff but not evaluated_right_ts. Upstream "
                "fill facts were already bounded, and the control census finds "
                "zero credited fills after frozen right."
            ),
        },
        {
            "kind": "horizon",
            "status": "active_defect",
            "path": (
                "arb-executor/analysis/window1_t2_recognition_laps.py"
            ),
            "site": "recognition event cutoff",
            "finding": (
                "Passes control guarded_cutoff_ts instead of frozen range "
                "right; one target-lap event is recognized after its horizon."
            ),
        },
        {
            "kind": "horizon",
            "status": "fixed_active",
            "path": "arb-executor/analysis/window1_t2_target_laps.py",
            "site": "raw V5 oracle reader",
            "finding": (
                "Now uses frozen range_right_ts and treats the frozen right "
                "endpoint as inclusive, matching the ladder builder."
            ),
        },
    ]


def render_report(result: Mapping[str, Any]) -> str:
    fee = result["fee_units"]
    reference = result["horizon"]["reference_and_delta"]
    recognition = result["horizon"]["recognition"]
    asynchronous = result["horizon"]["asynchronous_census"]
    decision = result["horizon"]["decision_attribution"]
    surface = result["horizon"]["t2_target_surfaces"]
    credited_fills = result["horizon"]["credited_fills"]
    metric = reference["metric_changes"]
    endpoint = fee["inclusive_frozen_right_endpoint_fix"]
    ranking = fee["second_leg_ranking_unit_fix"]
    pair = fee["pair_total_unit_fix"]
    lines = [
        "# Window-1 T2 scoring-chain unit and horizon sweep",
        "",
        "**This is a separate post-grid diagnostic. It is not a package or audit.**",
        "",
        "## What moved",
        "",
        (
            f"- First fee-unit correction already made: recognized strict "
            f"under-par **{pair['before_recognized_under_par']} -> "
            f"{pair['after_recognized_under_par']}**."
        ),
        (
            f"- Additional fee-unit correction found by this sweep: "
            f"recognized **{ranking['before_recognized_under_par']} -> "
            f"{ranking['after_recognized_under_par']}**; all 804 **"
            f"{ranking['before_all_804_under_par']} -> "
            f"{ranking['after_all_804_under_par']}**."
        ),
        (
            f"- Inclusive frozen-right endpoint: recognized **"
            f"{endpoint['before_recognized_under_par']} -> "
            f"{endpoint['after_recognized_under_par']}**; all 804 **"
            f"{endpoint['before_all_804_under_par']} -> "
            f"{endpoint['after_all_804_under_par']}**."
        ),
        (
            f"- Close-reference horizon correction changes **"
            f"{reference['reference_value_or_availability_changed_leg_count']}"
            f"** leg references across **"
            f"{reference['reference_changed_event_count']}** events."
        ),
        (
            f"- Among the 131 completed games, **"
            f"{reference['completed_individual_delta_changed_leg_count']}** "
            f"leg deltas across **"
            f"{reference['completed_individual_delta_changed_event_count']}** "
            f"events change; **"
            f"{reference['completed_combined_delta_changed_event_count']}** "
            "combined deltas change."
        ),
        (
            f"- Recognition target scope **"
            f"{recognition['target_lap_population_before']} -> "
            f"{recognition['target_lap_population_after']}** because "
            f"{', '.join(recognition['affected_event_ids'])} is read after "
            "its frozen right."
        ),
        (
            f"- Frozen five-contract floor prices move **0**. Their ladder "
            "already used the correct right edge."
        ),
        "",
        "## Completed-game metric movement",
        "",
        "| metric | ledger reference | corrected right-bound reference | lost | gained |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("prefee_PC", "prefee_IC", "maker_PC", "maker_IC"):
        row = metric[name]
        lines.append(
            f"| {name} | {row['old_count']} | {row['new_count']} | "
            f"{row['lost_count']} | {row['gained_count']} |"
        )
    lines.extend([
        "",
        "## Upstream horizon contamination",
        "",
        (
            f"- Asynchronous sibling episodes: **"
            f"{asynchronous['after_frozen_right_episode_count']}/"
            f"{asynchronous['qualifying_episode_count']}** are after frozen "
            f"right, across **{asynchronous['after_frozen_right_event_count']}** "
            "events."
        ),
        (
            f"- Decision attribution: **"
            f"{decision['earliest_opportunity_after_frozen_right_row_count']}/"
            f"{decision['decision_attribution_row_count']}** rows choose an "
            f"earliest opportunity after frozen right, across **"
            f"{decision['affected_event_count']}** events."
        ),
        (
            f"- T2 sibling target surfaces: **"
            f"{surface['after_frozen_right_surface_row_count']}/"
            f"{surface['surface_row_count']}** surface rows and **"
            f"{surface['after_frozen_right_lawful_target_entry_count']}/"
            f"{surface['surface_lawful_target_entry_count']}** lawful target "
            "entries are after frozen right."
        ),
        (
            f"- Final credited fills across all candidates: **"
            f"{credited_fills['after_frozen_right_credited_fill_count']}/"
            f"{credited_fills['all_candidate_credited_fill_count']}** are "
            "after frozen right."
        ),
        "",
        "## Every source occurrence",
        "",
        "| kind | status | source | finding |",
        "|---|---|---|---|",
    ])
    for finding in result["source_findings"]:
        lines.append(
            f"| {finding['kind']} | {finding['status']} | "
            f"`{finding['path']}`; {finding['site']} | "
            f"{finding['finding']} |"
        )
    lines.extend([
        "",
        "No additional nonzero fee-unit error was found in completed delta "
        "or in the five-contract floor. The delta does move because the "
        "reference reader crossed the frozen horizon; the floor does not.",
        "",
        "Holdout stayed sealed. Live and network access stayed off.",
        "",
    ])
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    grid = read_json(repo / GRID)
    current_target = read_json(repo / TARGET)
    rows = list(grid["games"])
    if len(rows) != 804:
        raise SweepError("grid population changed")
    right = {
        (str(row["event_id"]), str(leg_id)): float(
            leg["price_path"]["window"]["right_ts"]
        )
        for row in rows
        for leg_id, leg in row["legs"].items()
    }
    target_ids = {
        str(row["event_id"]) for row in current_target["events"]
    }
    excluded_recognition_ids = {
        str(event_id) for event_id in current_target["scope"][
            "recognition_events_excluded_after_frozen_right"
        ]
    }
    frozen_target_ids = target_ids | excluded_recognition_ids
    reference = horizon_reference(rows)
    recognition = recognition_horizon(rows, frozen_target_ids)
    if (
        set(recognition["affected_event_ids"])
        != excluded_recognition_ids
        or recognition["target_lap_population_after"] != len(target_ids)
    ):
        raise SweepError(
            "recognition horizon crosswalk disagrees with target-lap scope"
        )
    asynchronous = async_horizon(repo, right)
    decision = decision_horizon(repo, right)
    surface = t2_surface_horizon(repo, right)
    credited_fills = credited_fill_horizon(repo, right)
    fee = fee_transitions(repo, grid, current_target, target_ids)
    sequence = sequence_reference_counts(
        rows,
        frozen_target_ids,
        set(recognition["affected_event_ids"]),
    )
    credited_late = sum(
        leg["fill"] is not None
        and not leg["fill"]["inside_frozen_policy_window"]
        for row in rows
        for leg in row["legs"].values()
    )
    result = {
        "schema_version": VERSION,
        "scope": {
            "development_population": len(rows),
            "holdout_opened": False,
            "live_accessed": False,
            "network_accessed": False,
            "scorer_executed": False,
            "orders_created": False,
        },
        "frozen_right_law": (
            "inclusive min(policy_decision_horizon_ts, guarded_cutoff_ts)"
        ),
        "fee_units": fee,
        "horizon": {
            "reference_and_delta": reference,
            "recognition": recognition,
            "asynchronous_census": asynchronous,
            "decision_attribution": decision,
            "t2_target_surfaces": surface,
            "credited_fills": credited_fills,
            "control_credited_fill_legs_after_frozen_right": credited_late,
            "five_contract_floor_price_changes": 0,
            "strict_sequence_reference_counts": sequence,
        },
        "source_findings": source_findings(),
    }
    output_json = (repo / args.output_json).resolve()
    output_report = (repo / args.output_report).resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with output_report.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_report(result))
    print(json.dumps({
        "fee": fee,
        "reference": {
            key: value for key, value in reference.items()
            if not key.endswith("_changes")
        },
        "recognition": recognition,
        "async": asynchronous,
        "decision": {
            key: value for key, value in decision.items()
            if key != "rows"
        },
        "surface": surface,
        "credited_fills": credited_fills,
        "control_credited_late": credited_late,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    result.add_argument(
        "--output-json",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_T2_SCORING_CHAIN_SWEEP.json"
        ),
    )
    result.add_argument(
        "--output-report",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_T2_SCORING_CHAIN_SWEEP.md"
        ),
    )
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
