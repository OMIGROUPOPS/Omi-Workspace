#!/usr/bin/env python3
"""Strict sequential oracle and first target-layer lap for Window-1 T2.

Development data only.  This script neither opens holdout data nor creates
orders/exposures.  It answers two separate questions:

1. What can a strictly sequenced, five-contract, maker-fee oracle prove?
2. What happens when the recognized depth is finally mapped to the existing
   resting-target expression?
"""

from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Any, Mapping

import numpy as np

from window1_evaluator_boundary import full_lawful_right


VERSION = "window1-t2-sequential-oracle-target-lap-v2"
D_REQUIRED = 804
TAPE_OPPORTUNITY_REQUIRED = 692
CONTROL_COMPLETIONS_REQUIRED = 131
FROZEN_RECOGNIZED_INPUT_REQUIRED = 501
INITIAL_RECOGNIZED_REQUIRED = 500
BASELINE_NEVER_RECOGNIZED_REQUIRED = 510
QUANTITY = 5
CONTROL_LEDGER = (
    ".claude/"
    "window1_t2_results_w1-t2-dev-20260712-20260720-"
    "frontier-regret-grid1-scorepkg-v5/"
    "01_w1_t2__macro_hold__fixed_admission_parent_control_"
    "EVENT_LEDGER.jsonl"
)
RECOGNITION_JSON = (
    ".claude/window1_t2_iteration_history/"
    "WINDOW1_T2_RECOGNITION_LAPS.json"
)
RANGE_LADDER_FILES = tuple(
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725/"
    f"WINDOW1_PRICE_RANGE_LADDER_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)


class TargetLapError(RuntimeError):
    """Fail-closed contract violation."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TargetLapError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise TargetLapError(
                        f"JSONL object required: {path}:{line_number}"
                    )
                rows.append(value)
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def maker_fee_cents(price_cents: int, quantity: int = QUANTITY) -> int:
    """Published maker formula, rounded up to the next cent."""
    if not 1 <= price_cents <= 99:
        raise TargetLapError(f"invalid maker price: {price_cents}")
    return math.ceil(
        7 * quantity * price_cents * (100 - price_cents) / 40000
    )


def nearest_int(value: float) -> int:
    """Match window1_round2_instrument.nearest_int."""
    return int(math.floor(float(value) + 0.5))


def load_market(cache: Path, event_id: str) -> dict[str, Any]:
    path = cache / f"{event_id}.json.gz"
    if not path.is_file():
        raise TargetLapError(f"market cache missing: {event_id}")
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if value.get("cache_version") != "window1-guarded-event-market-cache-v3":
        raise TargetLapError(f"market cache contract failed: {event_id}")
    return value


def load_lawful_windows(
    repo: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for relative in RANGE_LADDER_FILES:
        path = repo / relative
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                key = (str(row["event_id"]), str(row["leg_id"]))
                if key in output:
                    raise TargetLapError(
                        f"duplicate lawful range-ladder leg: {key}"
                    )
                positive = bool(
                    row.get("positive_range_outcomes_provable")
                    and row["boundary"].get(
                        "positive_window1_provable"
                    )
                )
                cutoff = row["boundary"].get("guarded_cutoff_ts")
                try:
                    evaluator_right = full_lawful_right(
                        policy_right_ts=float(row["range_right_ts"]),
                        guarded_cutoff_ts=(
                            float(cutoff) if cutoff is not None else None
                        ),
                        positive_window1_provable=positive,
                    )
                except ValueError as exc:
                    raise TargetLapError(f"{key}: {exc}") from exc
                output[key] = {
                    "left": float(row["policy_left_ts"]),
                    "right": (
                        float(evaluator_right)
                        if evaluator_right is not None
                        else float(row["range_right_ts"])
                    ),
                    "policy_right": float(row["range_right_ts"]),
                    "positive": positive,
                }
    if len(output) != D_REQUIRED * 2:
        raise TargetLapError("lawful range-ladder window count changed")
    return output


def prepare_leg(
    leg: Mapping[str, Any],
    left: float,
    right: float,
) -> dict[str, Any]:
    snapshots = [
        row for row in (leg.get("snapshots") or [])
        if left <= float(row["ts"]) <= right and row.get("asks")
    ]
    prints = [
        row for row in (leg.get("prints") or [])
        if left <= float(row["ts"]) <= right
    ]
    return {
        "left": left,
        "right": right,
        "snapshot_ts": np.array(
            [float(row["ts"]) for row in snapshots], dtype=np.float64
        ),
        "asks": np.array(
            [int(row["asks"][0][0]) for row in snapshots], dtype=np.int16
        ),
        "print_ts": np.array(
            [float(row["ts"]) for row in prints], dtype=np.float64
        ),
        "print_price": np.array(
            [int(row["price"]) for row in prints], dtype=np.int16
        ),
        "print_size": np.array(
            [float(row["size"]) for row in prints], dtype=np.float64
        ),
        "snapshots": snapshots,
        "prints": prints,
    }


def fill_proof_by_target(
    leg: Mapping[str, Any],
    *,
    after_ts: float,
    strictly_later_placement: bool,
) -> dict[int, dict[str, Any]]:
    """Return earliest five-contract proof for every lawful resting target."""
    snapshot_ts = leg["snapshot_ts"]
    asks = leg["asks"]
    print_ts = leg["print_ts"]
    print_price = leg["print_price"]
    print_size = leg["print_size"]
    placement_index = int(np.searchsorted(
        snapshot_ts,
        after_ts,
        side="right" if strictly_later_placement else "left",
    ))
    if placement_index >= len(snapshot_ts):
        return {}
    placement_ts = float(snapshot_ts[placement_index])
    maker_ceiling = int(asks[placement_index]) - 1
    if maker_ceiling < 1:
        return {}

    later_snapshot_index = int(np.searchsorted(
        snapshot_ts, placement_ts, side="right"
    ))
    later_print_index = int(np.searchsorted(
        print_ts, placement_ts, side="right"
    ))
    output: dict[int, dict[str, Any]] = {}
    for target in range(1, maker_ceiling + 1):
        candidates: list[tuple[float, int, str, Mapping[str, Any]]] = []
        if later_snapshot_index < len(snapshot_ts):
            hits = np.flatnonzero(
                asks[later_snapshot_index:] < target
            )
            if len(hits):
                index = later_snapshot_index + int(hits[0])
                candidates.append((
                    float(snapshot_ts[index]),
                    0,
                    "STRICT_ASK",
                    leg["snapshots"][index],
                ))
        if later_print_index < len(print_ts):
            eligible_volume = np.where(
                print_price[later_print_index:] <= target,
                print_size[later_print_index:],
                0.0,
            )
            cumulative = np.cumsum(eligible_volume)
            hits = np.flatnonzero(cumulative >= QUANTITY)
            if len(hits):
                relative = int(hits[0])
                index = later_print_index + relative
                candidates.append((
                    float(print_ts[index]),
                    1,
                    "CUMULATIVE_TRUE_PRINT_CAPACITY",
                    leg["prints"][index],
                ))
        if not candidates:
            continue
        proof_ts, _, proof_type, raw = min(
            candidates, key=lambda value: (value[0], value[1])
        )
        output[target] = {
            "target_cents": target,
            "maker_fee_cents": maker_fee_cents(target),
            "placement_ts": placement_ts,
            "fill_proof_ts": proof_ts,
            "proof_type": proof_type,
            "proof_receipt": str(
                raw.get("receipt") or raw.get("trade_id") or ""
            ),
        }
    return output


def cheapest_fill_after(
    leg: Mapping[str, Any],
    first_fill_ts: float,
) -> dict[str, Any] | None:
    proofs = fill_proof_by_target(
        leg,
        after_ts=first_fill_ts,
        strictly_later_placement=True,
    )
    if not proofs:
        return None
    return min(
        proofs.values(),
        key=lambda row: (
            row["target_cents"] * QUANTITY
            + row["maker_fee_cents"],
            row["fill_proof_ts"],
            row["target_cents"],
        ),
    )


def strict_sequential_floor(
    control_row: Mapping[str, Any],
    market: Mapping[str, Any],
    lawful_windows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any] | None:
    event_id = str(control_row["event_id"])
    market_legs = {str(row["leg"]): row for row in market["legs"]}
    control_legs = {
        str(row["leg_id"]): row for row in control_row["legs"]
    }
    leg_ids = sorted(control_legs)
    if len(leg_ids) != 2 or set(leg_ids) != set(market_legs):
        raise TargetLapError(
            f"pair identity mismatch: {control_row['event_id']}"
        )
    windows = {
        leg_id: lawful_windows[(event_id, leg_id)]
        for leg_id in leg_ids
    }
    if not all(window["positive"] for window in windows.values()):
        return None
    prepared = {
        leg_id: prepare_leg(
            market_legs[leg_id],
            float(windows[leg_id]["left"]),
            float(windows[leg_id]["right"]),
        )
        for leg_id in leg_ids
    }
    candidates: list[dict[str, Any]] = []
    for first_leg_id, second_leg_id in (
        (leg_ids[0], leg_ids[1]),
        (leg_ids[1], leg_ids[0]),
    ):
        first_leg = prepared[first_leg_id]
        second_leg = prepared[second_leg_id]
        first_proofs = fill_proof_by_target(
            first_leg,
            after_ts=float(first_leg["left"]),
            strictly_later_placement=False,
        )
        second_cache: dict[float, dict[str, Any] | None] = {}
        for first in first_proofs.values():
            first_fill_ts = float(first["fill_proof_ts"])
            if first_fill_ts not in second_cache:
                second_cache[first_fill_ts] = cheapest_fill_after(
                    second_leg, first_fill_ts
                )
            second = second_cache[first_fill_ts]
            if second is None:
                continue
            second_placement_ts = float(second["placement_ts"])
            second_fill_ts = float(second["fill_proof_ts"])
            if not (
                float(first_leg["left"])
                <= float(first["placement_ts"])
                < first_fill_ts
                <= float(first_leg["right"])
            ):
                raise TargetLapError("first-leg Window-1 sequence failed")
            if not (
                float(second_leg["left"])
                <= second_placement_ts
                < second_fill_ts
                <= float(second_leg["right"])
            ):
                raise TargetLapError("second-leg Window-1 sequence failed")
            if not (
                first_fill_ts < second_placement_ts < second_fill_ts
            ):
                raise TargetLapError(
                    "second leg did not start strictly after first fill"
                )
            target_sum = (
                int(first["target_cents"])
                + int(second["target_cents"])
            )
            fee_sum = (
                int(first["maker_fee_cents"])
                + int(second["maker_fee_cents"])
            )
            reference_values = [
                control_legs[first_leg_id].get("window1_close_cents"),
                control_legs[second_leg_id].get("window1_close_cents"),
            ]
            reference_sum = (
                sum(int(value) for value in reference_values)
                if all(value is not None for value in reference_values)
                else None
            )
            pair_total_cents = target_sum * QUANTITY + fee_sum
            net_per_contract = pair_total_cents / QUANTITY
            candidates.append({
                "orientation": (
                    f"{first_leg_id}__then__{second_leg_id}"
                ),
                "first_leg_id": first_leg_id,
                "second_leg_id": second_leg_id,
                "first_leg_lawful_window": {
                    "left_ts": float(first_leg["left"]),
                    "right_ts": float(first_leg["right"]),
                },
                "second_leg_lawful_window": {
                    "left_ts": float(second_leg["left"]),
                    "right_ts": float(second_leg["right"]),
                },
                "first": first,
                "second": second,
                "target_sum_cents": target_sum,
                "maker_fee_total_cents_for_five_contract_pair": fee_sum,
                "maker_cost_total_cents_for_five_contract_pair": (
                    pair_total_cents
                ),
                "maker_cost_cents_per_contract": net_per_contract,
                "reference_sum_cents": reference_sum,
                "maker_cost_minus_reference_total_cents": (
                    pair_total_cents - reference_sum * QUANTITY
                    if reference_sum is not None else None
                ),
                "maker_cost_minus_reference_cents_per_contract": (
                    net_per_contract - reference_sum
                    if reference_sum is not None else None
                ),
                "floor_time_gap_minutes": (
                    second_fill_ts - first_fill_ts
                ) / 60.0,
            })
    if not candidates:
        return None
    best_by_orientation: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        orientation = str(candidate["orientation"])
        prior = best_by_orientation.get(orientation)
        if prior is None or (
            candidate["maker_cost_total_cents_for_five_contract_pair"],
            candidate["second"]["fill_proof_ts"],
        ) < (
            prior["maker_cost_total_cents_for_five_contract_pair"],
            prior["second"]["fill_proof_ts"],
        ):
            best_by_orientation[orientation] = candidate
    best = min(
        candidates,
        key=lambda row: (
            row["maker_cost_total_cents_for_five_contract_pair"],
            row["second"]["fill_proof_ts"],
            row["floor_time_gap_minutes"],
            row["orientation"],
        ),
    )
    best["ordering_minimums"] = {
        orientation: {
            "maker_cost_total_cents_for_five_contract_pair": row[
                "maker_cost_total_cents_for_five_contract_pair"
            ],
            "maker_cost_cents_per_contract": row[
                "maker_cost_cents_per_contract"
            ],
            "maker_under_par": (
                row["maker_cost_total_cents_for_five_contract_pair"]
                < 100 * QUANTITY
            ),
        }
        for orientation, row in sorted(best_by_orientation.items())
    }
    best["both_orderings_tested"] = True
    return best


def target_leg(state: Mapping[str, Any]) -> dict[str, Any] | None:
    actionable = [
        signal for signal in (state.get("signals") or [])
        if signal.get("instrument") != "reach_law"
        and signal.get("depth_cents") is not None
    ]
    if not actionable:
        return None
    bid = int(state["current_bid_cents"])
    ask = int(state["current_ask_cents"])
    depth = max(float(row["depth_cents"]) for row in actionable)
    selected = max(1, min(ask - 1, bid - nearest_int(depth)))
    sources = sorted(
        str(row["instrument"])
        for row in actionable
        if float(row["depth_cents"]) == depth
    )
    return {
        "leg_id": state["leg_id"],
        "ticker": state["ticker"],
        "selected_target_cents": selected,
        "selected_depth_cents": depth,
        "depth_sources": sources,
        "decision_bid_cents": bid,
        "decision_ask_cents": ask,
        "maker_safe": selected < ask,
        "target_expression": (
            "max(1, min(current_ask-1, "
            "current_bid-nearest_int(max_recognized_depth)))"
        ),
    }


def median_or_none(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def render_report(result: Mapping[str, Any]) -> str:
    oracle = result["strict_sequential_oracle"]
    reconciliation = result["oracle_reconciliation"]
    target = result["target_lap"]
    removals = reconciliation["removals_full_population_chain"]
    ordering = oracle["under_par_ordering_counts"]
    durations = oracle["under_par_gap_counts"]
    lines = [
        "# Window-1 T2 strict sequential oracle and target lap",
        "",
        (
            "**Corrections:** the prior 41 count was invalid. It added "
            "each leg's five-contract fee total directly to a "
            "per-contract price. This report compares total five-contract "
            "cost with the $5.00 pair payout. A second unit error in "
            "second-leg ranking is also fixed: it now ranks "
            "`target_cents*5 + maker_fee_cents`. The frozen range right is "
            "inclusive, matching the ladder builder."
        ),
        "",
        "## Target lap",
        "",
        (
            f"completions: **{target['completions_out_of_804']}/804**, "
            f"and **{target['completions_out_of_692']}/692** the tape proves"
        ),
        "",
        (
            "how many of the 510 we now see: "
            f"**{target['recognized_of_510']}/510**"
        ),
        "",
        (
            "what changed since last lap: one bridge now maps recognized "
            "depth to the existing maker target expression. "
            f"It selected an event target for "
            f"**{target['targeted_event_count']}/"
            f"{oracle['recognized_population']}** recognized events "
            f"({target['targeted_both_legs_count']} on both legs). "
            "Exposure was not changed, so completions were not expected "
            "to move."
        ),
        "",
        (
            "Why the old layer refused the recognized population: the scorer populated "
            "`best_selected_target_cents` only from pre-existing action "
            "rows. Recognition emitted no action row, so null selection "
            "was guaranteed by construction--not by an economic veto."
        ),
        "",
        (
            "## Strict sequential oracle over the "
            f"{oracle['recognized_population']}"
        ),
        "",
        (
            f"- Any strict sequential five-contract proof: "
            f"**{oracle['any_sequential_floor_count']}/"
            f"{oracle['recognized_population']}**"
        ),
        (
            f"- Maker-fee combined floor under par: "
            f"**{oracle['maker_under_par_count']}/"
            f"{oracle['recognized_population']}**"
        ),
        (
            f"- Negative against available Window-1 reference: "
            f"**{oracle['negative_vs_reference_count']}/"
            f"{oracle['recognized_population']}** "
            f"({oracle['negative_vs_reference_count']}/"
            f"{oracle['reference_available_sequential_count']} among "
            "strict sequential proofs with reference; "
            f"{oracle['reference_missing_sequential_count']} sequential "
            "proof lacks reference)"
        ),
        (
            f"- Complete within two hours: "
            f"**{durations['within_2_hours']}/"
            f"{oracle['maker_under_par_count']}**"
        ),
        (
            f"- Complete within four hours: "
            f"**{durations['within_4_hours']}/"
            f"{oracle['maker_under_par_count']}**"
        ),
        (
            f"- Complete within eight hours: "
            f"**{durations['within_8_hours']}/"
            f"{oracle['maker_under_par_count']}**"
        ),
        (
            f"- Take more than eight hours: "
            f"**{durations['over_8_hours']}/"
            f"{oracle['maker_under_par_count']}**"
        ),
        (
            f"- Median gap, all strict sequential proofs: "
            f"**{oracle['median_gap_minutes_all']:.2f} minutes**"
        ),
        (
            f"- Median gap, maker-under-par subset: "
            f"**{oracle['median_gap_minutes_under_par']:.2f} minutes**"
        ),
        (
            f"- Median gap, negative-vs-reference subset: "
            f"**{oracle['median_gap_minutes_negative_reference']:.2f} "
            "minutes**"
        ),
        (
            "- Strict-sequence median by category: "
            + ", ".join(
                f"{category} {row['median_gap_minutes']:.2f}m "
                f"(n={row['count']})"
                for category, row in sorted(
                    oracle["gap_by_category"].items()
                )
            )
        ),
        "",
        "## Both ordering directions",
        "",
        (
            "Every event evaluates leg A then leg B and leg B then leg A "
            "before choosing the cheaper lawful path."
        ),
        "",
        (
            f"- Both directions under par: "
            f"**{ordering.get('both_directions_under_par', 0)}**"
        ),
        (
            f"- Exactly one direction under par: "
            f"**{ordering.get('exactly_one_direction_under_par', 0)}**"
        ),
        "",
        "## Reconciliation of 437 versus the strict oracle",
        "",
        "| successive constraint | survivors | removed at this step |",
        "|---|---:|---:|",
        (
            "| development population | "
            f"{reconciliation['same_tape_population']} | - |"
        ),
        (
            "| two independent five-contract floors exist | "
            f"{reconciliation['independent_five_contract_floor_any_price']} "
            f"| {removals['missing_or_censored_independent_five_contract_proof']} |"
        ),
        (
            "| independent floors sum below par, pre-fee | "
            f"{reconciliation['independent_floor_prefee_under_par']} "
            f"| {removals['independent_floor_not_under_par_before_fees']} |"
        ),
        (
            "| independent floors remain below $5.00 with maker fees | "
            f"{reconciliation['independent_floor_maker_under_par']} "
            f"| {removals['maker_fees']} |"
        ),
        (
            "| any strict post-first-fill sequence exists | "
            f"{reconciliation['prior_364_with_any_strict_sequence']} "
            f"| {removals['no_post_first_fill_sequence']} |"
        ),
        (
            "| strict sequence still costs below $5.00 | "
            f"{reconciliation['strict_sequential_survivors_from_prior_364']} "
            f"| {removals['sequential_path_no_longer_under_par']} |"
        ),
        (
            "| also belongs to the right-bounded recognized scope | "
            f"{reconciliation['strict_sequential_maker_under_par_in_recognized_501']} "
            f"| {removals['recognized_501_scope_filter']} |"
        ),
        "",
        (
            f"After binding the raw-V5 reader to the frozen range-ladder "
            f"window, it finds "
            f"{reconciliation['strict_raw_v5_additions_outside_prior_364']} "
            "under-par paths outside the earlier independent-floor "
            "contract."
        ),
        "",
        (
            "The 437 oracle is asynchronous but independent: it adds each "
            "leg's best five-contract floor even when those moments cannot "
            "form a post-first-fill path. The strict oracle adds maker "
            "fees, waits for leg one's five-contract proof, places leg two "
            "only afterward, and then applies the separate right-bounded "
            "recognition scope."
        ),
        "",
        (
            "Sequencing is enforced: the first leg must have a lawful "
            "five-contract fill proof inside its Window 1; only then is "
            "the second resting target placed at the first later BBO, "
            "and its proof must occur later still inside its own Window 1."
        ),
        "",
        (
            "The vault's 41-62 minute figure measured the gap between "
            "independently deepest leg moments. This stricter "
            "place-after-first-fill oracle is a different estimator, so "
            "the gap is not expected to reproduce that range."
        ),
        "",
        (
            "The negative-reference count can exceed the under-par count "
            "because the event-specific two-leg Window-1 reference is not "
            "fixed at par; some reference sums are above 100 cents."
        ),
        "",
        (
            "This is not a completion plateau. Recognition moved the "
            "loss from never-seen to seen-not-targeted; this lap moves it "
            "again to targeted-not-exposed. Exposure is the next layer."
        ),
        "",
        "Holdout stayed sealed. Live and network access stayed off.",
        "",
    ]
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    cache = Path(args.market_cache).resolve()
    control_path = repo / CONTROL_LEDGER
    recognition_path = repo / RECOGNITION_JSON
    output_json = (repo / args.output_json).resolve()
    output_report = (repo / args.output_report).resolve()

    control_rows = read_jsonl(control_path)
    control = {str(row["event_id"]): row for row in control_rows}
    recognition = read_json(recognition_path)
    lawful_windows = load_lawful_windows(repo)
    frozen_initial_ids = list(
        recognition["recognition"]["lap_1_recognized_event_ids"]
    )
    recognition_events = {
        str(row["event_id"]): row
        for row in recognition["recognition"]["events"]
    }
    excluded_after_frozen_right: list[str] = []
    initial_ids: list[str] = []
    for event_id in frozen_initial_ids:
        event = recognition_events[str(event_id)]
        late = any(
            state.get("recognition_ts") is not None
            and float(state["recognition_ts"])
            > float(lawful_windows[
                (str(event_id), str(state["leg_id"]))
            ]["right"]) + 1e-6
            for state in event["legs"]
        )
        if late:
            excluded_after_frozen_right.append(str(event_id))
        else:
            initial_ids.append(str(event_id))
    if len(control_rows) != D_REQUIRED or len(control) != D_REQUIRED:
        raise TargetLapError("development control is not exactly 804")
    tape_opportunities = [
        row for row in control_rows
        if row["pair_regret"][
            "combined_five_contract_proven_floor_cents"
        ] is not None
    ]
    completions = [row for row in control_rows if row["C"] is True]
    baseline_never = [
        row for row in tape_opportunities
        if row["C"] is not True
        and row["primary_loss_stage"] == "NEVER_RECOGNIZED"
    ]
    if len(tape_opportunities) != TAPE_OPPORTUNITY_REQUIRED:
        raise TargetLapError("full-tape opportunity count changed")
    if len(completions) != CONTROL_COMPLETIONS_REQUIRED:
        raise TargetLapError("completion count changed")
    if len(baseline_never) != BASELINE_NEVER_RECOGNIZED_REQUIRED:
        raise TargetLapError("510 never-recognized census changed")
    if len(frozen_initial_ids) != FROZEN_RECOGNIZED_INPUT_REQUIRED:
        raise TargetLapError("frozen recognition input set is not 501")
    if len(initial_ids) != INITIAL_RECOGNIZED_REQUIRED:
        raise TargetLapError("right-bounded recognition set is not 500")
    if excluded_after_frozen_right != [
        "KXATPCHALLENGERMATCH-26JUL20CREMAT"
    ]:
        raise TargetLapError(
            "right-bounded recognition exclusion set changed"
        )
    if len(set(initial_ids)) != len(initial_ids):
        raise TargetLapError("duplicate initial recognition event")

    event_rows: list[dict[str, Any]] = []
    proof_types: Counter[str] = Counter()
    targeted_event_count = 0
    targeted_both_count = 0
    target_leg_count = 0
    for index, event_id in enumerate(sorted(initial_ids), 1):
        control_row = control[event_id]
        market = load_market(cache, event_id)
        sequential = strict_sequential_floor(
            control_row, market, lawful_windows
        )
        if sequential is not None:
            proof_types[sequential["first"]["proof_type"]] += 1
            proof_types[sequential["second"]["proof_type"]] += 1
        recognized_event = recognition_events[event_id]
        selected_legs = [
            selected
            for state in recognized_event["legs"]
            if (selected := target_leg(state)) is not None
        ]
        if selected_legs:
            targeted_event_count += 1
        if len(selected_legs) == 2:
            targeted_both_count += 1
        target_leg_count += len(selected_legs)
        if not all(row["maker_safe"] for row in selected_legs):
            raise TargetLapError(f"non-maker target: {event_id}")
        event_rows.append({
            "event_id": event_id,
            "category": control_row["category"],
            "recognized": True,
            "selected_target": bool(selected_legs),
            "selected_both_legs": len(selected_legs) == 2,
            "loss_stage_before": "RECOGNIZED_NOT_TARGETED",
            "loss_stage_after": (
                "TARGETED_NOT_EXPOSED"
                if selected_legs else "RECOGNIZED_NOT_TARGETED"
            ),
            "selected_legs": selected_legs,
            "strict_sequential_floor": sequential,
        })
        if index % 50 == 0 or index == len(initial_ids):
            print(f"target_events={index}/{len(initial_ids)}", flush=True)

    sequential_by_event = {
        str(row["event_id"]): row["strict_sequential_floor"]
        for row in event_rows
    }
    remaining_ids = sorted(set(control) - set(initial_ids))
    for index, event_id in enumerate(remaining_ids, 1):
        sequential_by_event[event_id] = strict_sequential_floor(
            control[event_id],
            load_market(cache, event_id),
            lawful_windows,
        )
        if index % 50 == 0 or index == len(remaining_ids):
            print(
                f"reconciliation_events={index}/{len(remaining_ids)}",
                flush=True,
            )

    sequential_values = [
        row["strict_sequential_floor"]
        for row in event_rows
        if row["strict_sequential_floor"] is not None
    ]
    under_par = [
        row for row in sequential_values
        if row["maker_cost_total_cents_for_five_contract_pair"]
        < 100 * QUANTITY
    ]
    reference_available = [
        row for row in sequential_values
        if row["maker_cost_minus_reference_total_cents"] is not None
    ]
    negative_reference = [
        row for row in reference_available
        if row["maker_cost_minus_reference_total_cents"] < 0
    ]
    recognized_id_set = set(initial_ids)
    independent_prefee_ids: set[str] = set()
    independent_maker_ids: set[str] = set()
    for row in tape_opportunities:
        event_id = str(row["event_id"])
        floors = [
            leg["five_contract_proven_floor_cents"]
            for leg in row["regret_by_leg"]
        ]
        if len(floors) != 2 or any(value is None for value in floors):
            raise TargetLapError(
                f"independent floor legs missing: {event_id}"
            )
        prices = [int(value) for value in floors]
        if sum(prices) != row["pair_regret"][
            "combined_five_contract_proven_floor_cents"
        ]:
            raise TargetLapError(
                f"independent pair/leg floor mismatch: {event_id}"
            )
        if sum(prices) < 100:
            independent_prefee_ids.add(event_id)
        if (
            sum(prices) * QUANTITY
            + sum(maker_fee_cents(price) for price in prices)
            < 100 * QUANTITY
        ):
            independent_maker_ids.add(event_id)
    strict_maker_ids = {
        event_id
        for event_id, sequential in sequential_by_event.items()
        if sequential is not None
        and sequential["maker_cost_total_cents_for_five_contract_pair"]
        < 100 * QUANTITY
    }
    strict_any_ids = {
        event_id
        for event_id, sequential in sequential_by_event.items()
        if sequential is not None
    }
    strict_survivors_from_prior_ids = (
        strict_maker_ids & independent_maker_ids
    )
    strict_raw_v5_additions = strict_maker_ids - independent_maker_ids
    recognized_strict_maker_ids = (
        strict_maker_ids & recognized_id_set
    )
    if len(recognized_strict_maker_ids) != len(under_par):
        raise TargetLapError(
            "right-bounded recognition strict under-par crosswalk mismatch"
        )

    ordering_counts: Counter[str] = Counter()
    for event_row in event_rows:
        sequential = event_row["strict_sequential_floor"]
        if (
            sequential is None
            or sequential[
                "maker_cost_total_cents_for_five_contract_pair"
            ] >= 100 * QUANTITY
        ):
            continue
        under_par_directions = sum(
            minimum["maker_under_par"]
            for minimum in sequential["ordering_minimums"].values()
        )
        if under_par_directions == 2:
            ordering_counts["both_directions_under_par"] += 1
        elif under_par_directions == 1:
            ordering_counts["exactly_one_direction_under_par"] += 1
        else:
            raise TargetLapError(
                f"unclassified under-par ordering: "
                f"{event_row['event_id']}:{under_par_directions}"
            )

    duration_counts = {
        "within_2_hours": sum(
            row["floor_time_gap_minutes"] <= 120
            for row in under_par
        ),
        "within_4_hours": sum(
            row["floor_time_gap_minutes"] <= 240
            for row in under_par
        ),
        "within_8_hours": sum(
            row["floor_time_gap_minutes"] <= 480
            for row in under_par
        ),
        "over_8_hours": sum(
            row["floor_time_gap_minutes"] > 480
            for row in under_par
        ),
    }
    reconciliation = {
        "same_tape_population": D_REQUIRED,
        "independent_five_contract_floor_any_price": len(
            tape_opportunities
        ),
        "independent_floor_prefee_under_par": len(
            independent_prefee_ids
        ),
        "independent_floor_maker_under_par": len(
            independent_maker_ids
        ),
        "strict_sequential_maker_under_par_all_804": len(
            strict_maker_ids
        ),
        "strict_sequential_survivors_from_prior_364": len(
            strict_survivors_from_prior_ids
        ),
        "strict_raw_v5_additions_outside_prior_364": len(
            strict_raw_v5_additions
        ),
        "strict_sequential_maker_under_par_in_recognized_501": len(
            recognized_strict_maker_ids
        ),
        "strict_sequential_any_price_all_804": sum(
            value is not None for value in sequential_by_event.values()
        ),
        "prior_364_with_any_strict_sequence": len(
            independent_maker_ids & strict_any_ids
        ),
        "removals_full_population_chain": {
            "missing_or_censored_independent_five_contract_proof": (
                D_REQUIRED - len(tape_opportunities)
            ),
            "independent_floor_not_under_par_before_fees": (
                len(tape_opportunities) - len(independent_prefee_ids)
            ),
            "maker_fees": (
                len(independent_prefee_ids)
                - len(independent_maker_ids)
            ),
            "no_post_first_fill_sequence": (
                len(independent_maker_ids)
                - len(independent_maker_ids & strict_any_ids)
            ),
            "sequential_path_no_longer_under_par": (
                len(independent_maker_ids & strict_any_ids)
                - len(strict_survivors_from_prior_ids)
            ),
            "recognized_501_scope_filter": (
                len(strict_survivors_from_prior_ids)
                - len(recognized_strict_maker_ids)
            ),
        },
        "recognized_501_chain": {
            "population": len(initial_ids),
            "independent_prefee_under_par": len(
                independent_prefee_ids & recognized_id_set
            ),
            "independent_maker_under_par": len(
                independent_maker_ids & recognized_id_set
            ),
            "any_strict_sequence": len(
                independent_maker_ids
                & recognized_id_set
                & strict_any_ids
            ),
            "strict_sequential_maker_under_par": len(
                recognized_strict_maker_ids
            ),
            "removed_by_independent_floor_at_or_above_par": (
                len(initial_ids)
                - len(independent_prefee_ids & recognized_id_set)
            ),
            "removed_by_maker_fees": (
                len(independent_prefee_ids & recognized_id_set)
                - len(independent_maker_ids & recognized_id_set)
            ),
            "removed_by_no_post_first_fill_sequence": (
                len(independent_maker_ids & recognized_id_set)
                - len(
                    independent_maker_ids
                    & recognized_id_set
                    & strict_any_ids
                )
            ),
            "removed_by_sequential_path_no_longer_under_par": (
                len(
                    independent_maker_ids
                    & recognized_id_set
                    & strict_any_ids
                )
                - len(recognized_strict_maker_ids)
            ),
        },
        "event_ids": {
            "independent_prefee_under_par": sorted(
                independent_prefee_ids
            ),
            "independent_maker_under_par": sorted(
                independent_maker_ids
            ),
            "strict_sequential_maker_under_par_all_804": sorted(
                strict_maker_ids
            ),
            "strict_sequential_any_price_all_804": sorted(
                strict_any_ids
            ),
            "strict_sequential_survivors_from_prior_364": sorted(
                strict_survivors_from_prior_ids
            ),
            "strict_raw_v5_additions_outside_prior_364": sorted(
                strict_raw_v5_additions
            ),
            "strict_sequential_maker_under_par_in_recognized_501": sorted(
                recognized_strict_maker_ids
            ),
        },
    }
    sequential_by_category: dict[str, list[dict[str, Any]]] = {}
    for event_row in event_rows:
        sequential = event_row["strict_sequential_floor"]
        if sequential is not None:
            sequential_by_category.setdefault(
                str(event_row["category"]), []
            ).append(sequential)
    oracle = {
        "recognized_population": len(initial_ids),
        "any_sequential_floor_count": len(sequential_values),
        "maker_under_par_count": len(under_par),
        "reference_available_sequential_count": len(reference_available),
        "reference_missing_sequential_count": (
            len(sequential_values) - len(reference_available)
        ),
        "no_sequential_floor_count": (
            len(initial_ids) - len(sequential_values)
        ),
        "negative_vs_reference_count": len(negative_reference),
        "under_par_gap_counts": duration_counts,
        "under_par_ordering_counts": dict(sorted(
            ordering_counts.items()
        )),
        "frontier": {
            "le_93": sum(
                row["maker_cost_total_cents_for_five_contract_pair"]
                <= 93 * QUANTITY
                for row in sequential_values
            ),
            "le_95": sum(
                row["maker_cost_total_cents_for_five_contract_pair"]
                <= 95 * QUANTITY
                for row in sequential_values
            ),
            "le_97": sum(
                row["maker_cost_total_cents_for_five_contract_pair"]
                <= 97 * QUANTITY
                for row in sequential_values
            ),
            "lt_100": len(under_par),
            "any": len(sequential_values),
        },
        "median_gap_minutes_all": median_or_none([
            row["floor_time_gap_minutes"] for row in sequential_values
        ]),
        "median_gap_minutes_under_par": median_or_none([
            row["floor_time_gap_minutes"] for row in under_par
        ]),
        "median_gap_minutes_negative_reference": median_or_none([
            row["floor_time_gap_minutes"] for row in negative_reference
        ]),
        "gap_by_category": {
            category: {
                "count": len(rows),
                "median_gap_minutes": median_or_none([
                    row["floor_time_gap_minutes"] for row in rows
                ]),
            }
            for category, rows in sorted(
                sequential_by_category.items()
            )
        },
        "proof_leg_counts": dict(sorted(proof_types.items())),
        "sequence_contract": {
            "first_leg_order_placed_at_first_bbo_in_own_window1": True,
            "first_leg_five_contract_proof_inside_own_window1": True,
            "second_leg_placement_strictly_after_first_fill_proof": True,
            "second_leg_five_contract_proof_after_placement": True,
            "second_leg_proof_inside_own_window1": True,
            "maker_target_strictly_below_ask_at_placement": True,
            "both_leg_orderings_evaluated_for_every_event": True,
            "quantity": QUANTITY,
        },
    }
    if targeted_event_count != INITIAL_RECOGNIZED_REQUIRED:
        raise TargetLapError(
            "target bridge did not act on the full right-bounded "
            "recognized population"
        )
    result = {
        "schema_version": VERSION,
        "scope": {
            "development_population": D_REQUIRED,
            "holdout_opened": False,
            "live_accessed": False,
            "network_accessed": False,
            "orders_created": False,
            "exposures_created": False,
            "completions_changed": False,
            "frozen_recognized_input_count": len(frozen_initial_ids),
            "right_bounded_recognized_count": len(initial_ids),
            "recognition_events_excluded_after_frozen_right": (
                excluded_after_frozen_right
            ),
        },
        "input_receipts": {
            "control_ledger": {
                "path": CONTROL_LEDGER,
                "bytes": control_path.stat().st_size,
                "sha256": sha256_file(control_path),
            },
            "recognition_laps": {
                "path": RECOGNITION_JSON,
                "bytes": recognition_path.stat().st_size,
                "sha256": sha256_file(recognition_path),
            },
            "lawful_range_ladders": {
                relative: sha256_file(repo / relative)
                for relative in RANGE_LADDER_FILES
            },
            "market_cache": {
                "path_redacted": True,
                "cache_version": (
                    "window1-guarded-event-market-cache-v3"
                ),
                "events_read": len(initial_ids),
            },
        },
        "strict_sequential_oracle": oracle,
        "oracle_reconciliation": reconciliation,
        "target_lap": {
            "completions_out_of_804": len(completions),
            "completions_out_of_692": sum(
                row["C"] is True for row in tape_opportunities
            ),
            "recognized_of_510": len(initial_ids),
            "targeted_event_count": targeted_event_count,
            "targeted_both_legs_count": targeted_both_count,
            "selected_leg_count": target_leg_count,
            "new_exposure_count": 0,
            "loss_stage_transfer": {
                "from": "RECOGNIZED_NOT_TARGETED",
                "to": "TARGETED_NOT_EXPOSED",
                "event_count": targeted_event_count,
            },
            "refusal_cause": (
                "best_selected_target_cents is derived only from relevant "
                "action rows; the recognition harness deliberately emitted "
                "no action row, so selection remained null by construction"
            ),
            "one_change": (
                "map the maximum actionable recognized depth through the "
                "existing maker-safe bid-minus-depth target expression"
            ),
        },
        "events": event_rows,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with output_report.open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(render_report(result))
    print(json.dumps({
        "sequential_any": len(sequential_values),
        "maker_under_par": len(under_par),
        "reference_available": len(reference_available),
        "negative_vs_reference": len(negative_reference),
        "median_gap_minutes": oracle["median_gap_minutes_all"],
        "targeted_events": targeted_event_count,
        "targeted_both_legs": targeted_both_count,
        "completions": len(completions),
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    result.add_argument("--market-cache", required=True)
    result.add_argument(
        "--output-json",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_T2_SEQUENTIAL_ORACLE_AND_TARGET_LAP.json"
        ),
    )
    result.add_argument(
        "--output-report",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_T2_SEQUENTIAL_ORACLE_AND_TARGET_LAP.md"
        ),
    )
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
