#!/usr/bin/env python3
"""Build the inspectable 804-game Window-1 T2 grid.

This is a development-only reader.  It joins already-frozen ledgers, the
frozen Range-Attack streams and ladders, and the guarded V5 market cache.  It
does not create orders, execute a scorer, open holdout data, or access a
network.

The output deliberately keeps money units explicit:

* market prices and references are cents per contract;
* maker fees are cents for the five-contract order;
* pair totals are cents for all five pairs;
* per-contract equivalents are separate fields.
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
import sys
from typing import Any, Iterable, Mapping


VERSION = "window1-t2-game-grid-v1"
POPULATION = 804
QUANTITY = 5
BASE_CANDIDATE = "w1_range_attack__macro_hold__combined_headroom"
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
TARGET_JSON = (
    ".claude/window1_t2_iteration_history/"
    "WINDOW1_T2_SEQUENTIAL_ORACLE_AND_TARGET_LAP.json"
)
PRERUN_DIR = (
    ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"
)
RANGE_LADDERS = tuple(
    f"{PRERUN_DIR}/WINDOW1_PRICE_RANGE_LADDER_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)
STREAMS = tuple(
    f"{PRERUN_DIR}/UNSCORED_CANDIDATE_EVENT_STREAMS_{part:02d}.jsonl.gz"
    for part in range(1, 5)
)


class GridError(RuntimeError):
    """Fail-closed grid contract violation."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise GridError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise GridError(f"object required: {path}:{line_number}")
            rows.append(row)
    return rows


def gzip_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise GridError(f"object required: {path}:{line_number}")
            yield row


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def maker_fee_cents(price_cents: int) -> int:
    """Published maker formula; result is total cents for five contracts."""
    if not 1 <= int(price_cents) <= 99:
        raise GridError(f"invalid maker price: {price_cents}")
    price = int(price_cents)
    return math.ceil(
        7 * QUANTITY * price * (100 - price) / 40000
    )


def load_market(cache: Path, event_id: str) -> dict[str, Any]:
    path = cache / f"{event_id}.json.gz"
    if not path.is_file():
        raise GridError(f"market cache missing: {event_id}")
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if value.get("cache_version") != "window1-guarded-event-market-cache-v3":
        raise GridError(f"market cache contract changed: {event_id}")
    return value


def load_ladders(repo: Path) -> dict[tuple[str, str], dict[str, Any]]:
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for relative in RANGE_LADDERS:
        for row in gzip_jsonl(repo / relative):
            key = (str(row["event_id"]), str(row["leg_id"]))
            if key in output:
                raise GridError(f"duplicate range-ladder leg: {key}")
            output[key] = {
                "event_id": key[0],
                "leg_id": key[1],
                "ticker": str(row["ticker"]),
                "left_ts": float(row["policy_left_ts"]),
                "policy_horizon_ts": float(row["policy_horizon_ts"]),
                "guarded_cutoff_ts": (
                    float(row["boundary"]["guarded_cutoff_ts"])
                    if row["boundary"].get("guarded_cutoff_ts") is not None
                    else None
                ),
                "right_ts": float(row["range_right_ts"]),
                "positive": bool(
                    row.get("positive_range_outcomes_provable")
                    and row["boundary"].get("positive_window1_provable")
                ),
                "boundary_status": (
                    "positive"
                    if row["boundary"].get("positive_window1_provable")
                    else (
                        "contradictory"
                        if row["boundary"].get("conflict_status")
                        == "contradictory"
                        else "censored"
                    )
                ),
                "policy_right_law": (
                    "min(policy_horizon_ts, guarded_cutoff_ts)"
                ),
            }
    if len(output) != POPULATION * 2:
        raise GridError(f"expected 1608 ladder legs, found {len(output)}")
    return output


def compact_target(action: Mapping[str, Any], right: float) -> dict[str, Any]:
    timestamp = float(action["ts"])
    return {
        "ts": timestamp,
        "leg_id": str(action["leg_id"]),
        "price_cents": int(action["price_cents"]),
        "raw_target_cents": (
            int(action["complete_raw_target_cents"])
            if action.get("complete_raw_target_cents") is not None
            else None
        ),
        "expressed_price_cents": (
            int(action["final_expressed_price_cents"])
            if action.get("final_expressed_price_cents") is not None
            else None
        ),
        "authority": str(action.get("primary_authority") or ""),
        "reason": str(action.get("reason") or ""),
        "order_interval_id": str(action.get("order_interval_id") or ""),
        "inside_frozen_policy_window": timestamp <= right + 1e-6,
    }


def compact_interval(
    interval: Mapping[str, Any],
    right: float,
) -> dict[str, Any]:
    opened = float(interval["opened_ts"])
    closed = float(interval["closed_ts"])
    return {
        "leg_id": str(interval["leg_id"]),
        "opened_ts": opened,
        "closed_ts": closed,
        "limit_price_cents": int(interval["limit_price_cents"]),
        "raw_target_cents": (
            int(interval["raw_target_cents"])
            if interval.get("raw_target_cents") is not None
            else None
        ),
        "authority": str(interval.get("authority") or ""),
        "open_reason": str(interval.get("open_reason") or ""),
        "close_reason": str(interval.get("close_reason") or ""),
        "order_interval_id": str(interval["order_interval_id"]),
        "opened_inside_frozen_policy_window": opened <= right + 1e-6,
        "extends_past_frozen_policy_window": closed > right + 1e-6,
        "lawful_closed_ts": min(closed, right),
    }


def load_streams(
    repo: Path,
    ladders: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for relative in STREAMS:
        for wrapper in gzip_jsonl(repo / relative):
            if str(wrapper["candidate_id"]) != BASE_CANDIDATE:
                continue
            event_id = str(wrapper["event_id"])
            if event_id in output:
                raise GridError(f"duplicate control stream: {event_id}")
            stream = wrapper["stream"]
            targets = []
            for action in stream.get("order_stream") or []:
                if action.get("action") != "place":
                    continue
                leg_id = str(action["leg_id"])
                right = float(ladders[(event_id, leg_id)]["right_ts"])
                targets.append(compact_target(action, right))
            intervals: dict[str, list[dict[str, Any]]] = {}
            for leg_id, values in (
                stream.get("order_intervals_by_leg") or {}
            ).items():
                right = float(ladders[(event_id, str(leg_id))]["right_ts"])
                intervals[str(leg_id)] = [
                    compact_interval(row, right) for row in values
                ]
            evidence = {
                str(row["leg_id"]): {
                    "divot_count": int(row.get("divot_count") or 0),
                    "headroom_trigger_count": int(
                        row.get("headroom_trigger_count") or 0
                    ),
                    "target_change_count": int(
                        row.get("target_change_count") or 0
                    ),
                    "macro_target_raw": row.get("macro_target_raw"),
                    "macro_target_source": row.get("macro_target_source"),
                    "native_regime": row.get("discovery_page_key"),
                }
                for row in stream.get("evidence_census_by_leg") or []
            }
            output[event_id] = {
                "targets": targets,
                "exposures_by_leg": intervals,
                "evidence_by_leg": evidence,
            }
    if len(output) != POPULATION:
        raise GridError(f"expected 804 control streams, found {len(output)}")
    return output


def true_prints(
    leg: Mapping[str, Any],
    left: float,
    right: float,
) -> list[dict[str, Any]]:
    by_receipt: dict[str, dict[str, Any]] = {}
    for row in leg.get("prints") or []:
        timestamp = float(row["ts"])
        if not left <= timestamp <= right:
            continue
        receipt = str(row.get("trade_id") or "")
        size = float(row.get("size") or 0)
        if not receipt or size <= 0:
            continue
        normalized = {
            "ts": timestamp,
            "price_cents": int(row["price"]),
            "size": size,
            "receipt": receipt,
        }
        prior = by_receipt.get(receipt)
        if prior is not None and prior != normalized:
            raise GridError("conflicting duplicate true-print receipt")
        by_receipt[receipt] = normalized
    return sorted(
        by_receipt.values(),
        key=lambda row: (row["ts"], row["receipt"]),
    )


def five_minute_path(
    prints: list[dict[str, Any]],
    left: float,
) -> list[list[float | int]]:
    buckets: dict[int, list[dict[str, Any]]] = {}
    for row in prints:
        bucket = int((float(row["ts"]) - left) // 300)
        buckets.setdefault(bucket, []).append(row)
    output: list[list[float | int]] = []
    for bucket, rows in sorted(buckets.items()):
        prices = [int(row["price_cents"]) for row in rows]
        output.append([
            left + bucket * 300,
            prices[0],
            max(prices),
            min(prices),
            prices[-1],
            len(rows),
            round(sum(float(row["size"]) for row in rows), 4),
        ])
    return output


def close_reference(prints: list[dict[str, Any]]) -> dict[str, Any]:
    if not prints:
        return {
            "available": False,
            "price_cents": None,
            "timestamp": None,
            "reason": "no_true_print_inside_frozen_policy_window",
            "tie_count": 0,
            "distinct_prices": [],
        }
    latest_ts = max(float(row["ts"]) for row in prints)
    latest = [row for row in prints if float(row["ts"]) == latest_ts]
    prices = sorted({int(row["price_cents"]) for row in latest})
    if len(prices) != 1:
        return {
            "available": False,
            "price_cents": None,
            "timestamp": latest_ts,
            "reason": "latest_timestamp_distinct_price_ambiguity",
            "tie_count": len(latest),
            "distinct_prices": prices,
        }
    return {
        "available": True,
        "price_cents": prices[0],
        "timestamp": latest_ts,
        "reason": None,
        "tie_count": len(latest),
        "distinct_prices": prices,
    }


def floor_proof(
    leg: Mapping[str, Any],
    prints: list[dict[str, Any]],
    floor_price: int | None,
    left: float,
    right: float,
) -> dict[str, Any] | None:
    if floor_price is None:
        return None
    candidates: list[tuple[float, int, str, str]] = []
    volume = 0.0
    for row in prints:
        if int(row["price_cents"]) <= int(floor_price):
            volume += float(row["size"])
            if volume >= QUANTITY:
                candidates.append((
                    float(row["ts"]),
                    1,
                    "CUMULATIVE_TRUE_PRINT_CAPACITY",
                    str(row["receipt"]),
                ))
                break
    for snapshot in leg.get("snapshots") or []:
        timestamp = float(snapshot["ts"])
        asks = snapshot.get("asks") or []
        if (
            left <= timestamp <= right
            and asks
            and int(asks[0][0]) < int(floor_price)
        ):
            candidates.append((timestamp, 0, "STRICT_ASK", ""))
            break
    if not candidates:
        return {
            "price_cents": int(floor_price),
            "proof_ts": None,
            "proof_type": "FROZEN_LEDGER_PROOF_TIME_NOT_RECONSTRUCTED",
            "receipt": None,
        }
    timestamp, _, proof_type, receipt = min(
        candidates, key=lambda value: (value[0], value[1])
    )
    return {
        "price_cents": int(floor_price),
        "proof_ts": timestamp,
        "proof_type": proof_type,
        "receipt": receipt or None,
    }


def leg_path(
    *,
    market_leg: Mapping[str, Any],
    window: Mapping[str, Any],
    floor_price: int | None,
) -> dict[str, Any]:
    left = float(window["left_ts"])
    right = float(window["right_ts"])
    prints = true_prints(market_leg, left, right)
    close = close_reference(prints)
    if prints:
        low_price = min(int(row["price_cents"]) for row in prints)
        low = next(
            row for row in prints if int(row["price_cents"]) == low_price
        )
        open_row = prints[0]
    else:
        low = None
        open_row = None
    proof = floor_proof(
        market_leg, prints, floor_price, left, right
    )
    open_price = (
        int(open_row["price_cents"]) if open_row is not None else None
    )
    close_price = close["price_cents"]
    low_price = int(low["price_cents"]) if low is not None else None
    duration = max(1.0, right - left)
    return {
        "window": dict(window),
        "open": {
            "price_cents": open_price,
            "timestamp": (
                float(open_row["ts"]) if open_row is not None else None
            ),
        },
        "tape_low": {
            "price_cents": low_price,
            "timestamp": float(low["ts"]) if low is not None else None,
        },
        "close": close,
        "five_contract_proven_floor": proof,
        "shape": {
            "open_to_low_cents": (
                open_price - low_price
                if open_price is not None and low_price is not None
                else None
            ),
            "low_to_close_cents": (
                close_price - low_price
                if close_price is not None and low_price is not None
                else None
            ),
            "low_minutes_from_window_open": (
                (float(low["ts"]) - left) / 60.0
                if low is not None else None
            ),
            "low_fraction_of_window": (
                (float(low["ts"]) - left) / duration
                if low is not None else None
            ),
            "true_print_count": len(prints),
            "true_print_volume": round(
                sum(float(row["size"]) for row in prints), 4
            ),
        },
        "five_minute_true_print_path": five_minute_path(prints, left),
    }


def compact_fill(
    leg: Mapping[str, Any],
    right: float,
) -> dict[str, Any] | None:
    if leg.get("accounting_fill_price_cents") is None:
        return None
    price = int(leg["accounting_fill_price_cents"])
    timestamp = float(leg["evidence_timestamp"])
    return {
        "price_cents": price,
        "quantity": int(leg["accounting_quantity"]),
        "timestamp": timestamp,
        "evidence_type": leg.get("evidence_type"),
        "evidence_receipt": leg.get("evidence_receipt"),
        "order_interval_id": leg.get("order_interval_id"),
        "inside_frozen_policy_window": timestamp <= right + 1e-6,
        "maker_fee_cents_for_five_contract_order": maker_fee_cents(price),
    }


def physical_stage(
    *,
    boundary_status: str,
    fills: int,
    lawful_targets: int,
    lawful_exposures: int,
    recognized: bool,
) -> str:
    if boundary_status != "positive":
        return "CENSORED_BOUNDARY"
    if fills == 2:
        return "COMPLETED"
    if fills == 1:
        return "ONE_LEG_FILLED_SECOND_MISSED"
    if lawful_exposures:
        return "EXPOSED_NOT_CREDITED"
    if lawful_targets:
        return "TARGETED_NOT_EXPOSED"
    if recognized:
        return "RECOGNIZED_NOT_TARGETED"
    return "NEVER_RECOGNIZED"


def sequence_summary(sequence: Mapping[str, Any] | None) -> dict[str, Any]:
    if sequence is None:
        return {
            "lawful": False,
            "chosen_order": None,
            "other_order_lawful": False,
            "maker_under_par": False,
        }
    minimums = sequence.get("ordering_minimums") or {}
    return {
        "lawful": True,
        "chosen_order": sequence["orientation"],
        "other_order_lawful": len(minimums) == 2,
        "both_orderings_tested": bool(sequence["both_orderings_tested"]),
        "ordering_minimums": minimums,
        "first_leg_id": sequence["first_leg_id"],
        "second_leg_id": sequence["second_leg_id"],
        "first_target_cents": int(sequence["first"]["target_cents"]),
        "second_target_cents": int(sequence["second"]["target_cents"]),
        "first_floor_ts": float(sequence["first"]["fill_proof_ts"]),
        "second_floor_ts": float(sequence["second"]["fill_proof_ts"]),
        "minutes_between_floor_proofs": float(
            sequence["floor_time_gap_minutes"]
        ),
        "maker_fee_total_cents_for_five_contract_pair": int(
            sequence["maker_fee_total_cents_for_five_contract_pair"]
        ),
        "maker_cost_total_cents_for_five_contract_pair": int(
            sequence["maker_cost_total_cents_for_five_contract_pair"]
        ),
        "maker_cost_cents_per_contract": float(
            sequence["maker_cost_cents_per_contract"]
        ),
        "maker_under_par": (
            int(sequence[
                "maker_cost_total_cents_for_five_contract_pair"
            ]) < 100 * QUANTITY
        ),
    }


def target_bridge_by_event(target: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(row["event_id"]): {
            "selected": bool(row["selected_target"]),
            "selected_both_legs": bool(row["selected_both_legs"]),
            "legs": row["selected_legs"],
        }
        for row in target.get("events") or []
    }


def reference_money(
    *,
    fills: list[dict[str, Any]],
    ledger_references: list[int | None],
) -> dict[str, Any]:
    if len(fills) != 2:
        return {
            "combined_entry_price_cents_per_contract": None,
            "combined_entry_cost_cents_for_five_pairs_before_fees": None,
            "maker_fee_total_cents_for_five_contract_pair": None,
            "combined_entry_cost_cents_for_five_pairs_after_maker_fees": None,
            "combined_entry_cost_cents_per_contract_after_maker_fees": None,
            "ledger_reference_sum_cents_per_contract": (
                sum(int(value) for value in ledger_references)
                if all(value is not None for value in ledger_references)
                else None
            ),
            "delta_vs_ledger_reference_total_cents_for_five_pairs": None,
            "delta_vs_ledger_reference_cents_per_contract": None,
        }
    price_sum = sum(int(row["price_cents"]) for row in fills)
    fee_sum = sum(
        int(row["maker_fee_cents_for_five_contract_order"])
        for row in fills
    )
    before_fee = price_sum * QUANTITY
    after_fee = before_fee + fee_sum
    ledger_sum = (
        sum(int(value) for value in ledger_references)
        if all(value is not None for value in ledger_references)
        else None
    )
    return {
        "combined_entry_price_cents_per_contract": price_sum,
        "combined_entry_cost_cents_for_five_pairs_before_fees": before_fee,
        "maker_fee_total_cents_for_five_contract_pair": fee_sum,
        "combined_entry_cost_cents_for_five_pairs_after_maker_fees": after_fee,
        "combined_entry_cost_cents_per_contract_after_maker_fees": (
            after_fee / QUANTITY
        ),
        "ledger_reference_sum_cents_per_contract": ledger_sum,
        "delta_vs_ledger_reference_total_cents_for_five_pairs": (
            after_fee - ledger_sum * QUANTITY
            if ledger_sum is not None else None
        ),
        "delta_vs_ledger_reference_cents_per_contract": (
            after_fee / QUANTITY - ledger_sum
            if ledger_sum is not None else None
        ),
    }


def safe_median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def sweep_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [row for row in rows if row["outcome"] == "completed"]
    changed_reference_legs = [
        (row["event_id"], leg_id)
        for row in rows
        for leg_id, leg in row["legs"].items()
        if (
            leg["frozen_reference"]["price_cents"]
            != leg["price_path"]["close"]["price_cents"]
            or leg["frozen_reference"]["available"]
            != leg["price_path"]["close"]["available"]
        )
    ]
    reference_after_right = [
        (row["event_id"], leg_id)
        for row in rows
        for leg_id, leg in row["legs"].items()
        if (
            leg["frozen_reference"]["timestamp"] is not None
            and float(leg["frozen_reference"]["timestamp"])
            > float(leg["price_path"]["window"]["right_ts"]) + 1e-6
        )
    ]
    credited_fills_after_right = [
        (row["event_id"], leg_id)
        for row in rows
        for leg_id, leg in row["legs"].items()
        if leg["fill"] is not None
        and not leg["fill"]["inside_frozen_policy_window"]
    ]
    target_actions_after_right = [
        (row["event_id"], action["leg_id"], action["ts"])
        for row in rows
        for action in row["control_targets"]
        if not action["inside_frozen_policy_window"]
    ]
    exposure_opens_after_right = [
        (row["event_id"], leg_id, interval["opened_ts"])
        for row in rows
        for leg_id, leg in row["legs"].items()
        for interval in leg["exposures"]
        if not interval["opened_inside_frozen_policy_window"]
    ]
    exposure_extends_after_right = [
        (row["event_id"], leg_id, interval["closed_ts"])
        for row in rows
        for leg_id, leg in row["legs"].items()
        for interval in leg["exposures"]
        if interval["extends_past_frozen_policy_window"]
    ]
    recognition_after_right = [
        (row["event_id"], leg_id, leg["recognition"]["recognition_ts"])
        for row in rows
        for leg_id, leg in row["legs"].items()
        if (
            leg["recognition"] is not None
            and leg["recognition"]["recognition_ts"] is not None
            and not leg["recognition"]["inside_frozen_policy_window"]
        )
    ]
    floor_mismatches = [
        (row["event_id"], leg_id)
        for row in rows
        for leg_id, leg in row["legs"].items()
        if (
            leg["five_contract_floor_cents"] is not None
            and leg["price_path"]["five_contract_proven_floor"] is not None
            and leg["price_path"]["five_contract_proven_floor"][
                "proof_ts"
            ] is None
        )
    ]

    original_pc = sum(row["control_metrics"]["PC"] is True for row in completed)
    original_ic = sum(row["control_metrics"]["IC"] is True for row in completed)
    corrected_prefee_pc_ids = []
    corrected_prefee_ic_ids = []
    frozen_maker_pc_ids = []
    frozen_maker_ic_ids = []
    corrected_maker_pc_ids = []
    corrected_maker_ic_ids = []
    delta_changed_ids = []
    for row in completed:
        fills = [
            leg["fill"] for leg in row["legs"].values()
            if leg["fill"] is not None
        ]
        if len(fills) != 2:
            raise GridError("completed row lacks two fills")
        fill_prices = [int(value["price_cents"]) for value in fills]
        fees = [
            int(value["maker_fee_cents_for_five_contract_order"])
            for value in fills
        ]
        corrected = [
            leg["price_path"]["close"]["price_cents"]
            for leg in row["legs"].values()
        ]
        frozen = [
            leg["frozen_reference"]["price_cents"]
            for leg in row["legs"].values()
        ]
        event_id = str(row["event_id"])
        if all(value is not None for value in corrected):
            d = [
                fill_prices[index] - int(corrected[index])
                for index in range(2)
            ]
            if sum(d) < 0:
                corrected_prefee_pc_ids.append(event_id)
            if all(value < 0 for value in d):
                corrected_prefee_ic_ids.append(event_id)
            if sum(
                d[index] * QUANTITY + fees[index]
                for index in range(2)
            ) < 0:
                corrected_maker_pc_ids.append(event_id)
            if all(
                d[index] * QUANTITY + fees[index] < 0
                for index in range(2)
            ):
                corrected_maker_ic_ids.append(event_id)
        if all(value is not None for value in frozen):
            d = [
                fill_prices[index] - int(frozen[index])
                for index in range(2)
            ]
            if sum(
                d[index] * QUANTITY + fees[index]
                for index in range(2)
            ) < 0:
                frozen_maker_pc_ids.append(event_id)
            if all(
                d[index] * QUANTITY + fees[index] < 0
                for index in range(2)
            ):
                frozen_maker_ic_ids.append(event_id)
        old = row["control_metrics"]["combined_delta_cents"]
        new_refs = (
            sum(int(value) for value in corrected)
            if all(value is not None for value in corrected)
            else None
        )
        entry = row["pair_money"][
            "combined_entry_price_cents_per_contract"
        ]
        new = (
            entry - new_refs
            if entry is not None and new_refs is not None else None
        )
        if old != new:
            delta_changed_ids.append(event_id)

    strict_under_par = [
        row["event_id"] for row in rows
        if row["strict_sequential_oracle"]["maker_under_par"]
    ]
    recognition_late_events = sorted({
        event_id for event_id, _, _ in recognition_after_right
    })
    return {
        "population": len(rows),
        "frozen_window_right_law": (
            "min(policy_horizon_ts, guarded_cutoff_ts), inclusive"
        ),
        "horizon": {
            "reference_legs_after_frozen_right_count": len(
                reference_after_right
            ),
            "reference_legs_changed_by_right_bound_count": len(
                changed_reference_legs
            ),
            "completed_event_deltas_changed_count": len(
                set(delta_changed_ids)
            ),
            "credited_fill_legs_after_frozen_right_count": len(
                credited_fills_after_right
            ),
            "target_actions_after_frozen_right_count": len(
                target_actions_after_right
            ),
            "exposure_opens_after_frozen_right_count": len(
                exposure_opens_after_right
            ),
            "exposures_extending_after_frozen_right_count": len(
                exposure_extends_after_right
            ),
            "recognition_legs_after_frozen_right_count": len(
                recognition_after_right
            ),
            "recognition_events_affected_count": len(
                recognition_late_events
            ),
            "lawful_floor_proof_reconstruction_mismatch_count": len(
                floor_mismatches
            ),
            "event_ids": {
                "reference_changed": sorted({
                    event_id for event_id, _ in changed_reference_legs
                }),
                "completed_delta_changed": sorted(set(delta_changed_ids)),
                "credited_fill_after_right": sorted({
                    event_id for event_id, _ in credited_fills_after_right
                }),
                "recognition_after_right": recognition_late_events,
            },
        },
        "delta_metrics": {
            "completed_count": len(completed),
            "frozen_prefee_PC_count": original_pc,
            "corrected_horizon_prefee_PC_count": len(
                corrected_prefee_pc_ids
            ),
            "frozen_prefee_IC_count": original_ic,
            "corrected_horizon_prefee_IC_count": len(
                corrected_prefee_ic_ids
            ),
            "frozen_reference_maker_PC_count": len(frozen_maker_pc_ids),
            "corrected_horizon_maker_PC_count": len(
                corrected_maker_pc_ids
            ),
            "frozen_reference_maker_IC_count": len(frozen_maker_ic_ids),
            "corrected_horizon_maker_IC_count": len(
                corrected_maker_ic_ids
            ),
        },
        "fee_units": {
            "strict_sequential_maker_under_par_all_804": len(
                strict_under_par
            ),
            "ranking_bug_effect": (
                "The old second-leg ranking compared per-contract target "
                "cents with a five-contract order fee total. The corrected "
                "ranking compares target*5 + fee."
            ),
            "price_unit": "cents_per_contract",
            "fee_unit": "total_cents_for_five_contract_order",
            "pair_total_unit": "total_cents_for_five_pairs",
        },
        "floor_metrics": {
            "floor_price_changes_from_horizon_correction": 0,
            "reason": (
                "The frozen five-contract floors already came from the "
                "range ladder bounded by min(policy horizon, guarded cutoff)."
            ),
        },
    }


def build_row(
    *,
    control_row: Mapping[str, Any],
    stream: Mapping[str, Any],
    market: Mapping[str, Any],
    ladders: Mapping[tuple[str, str], Mapping[str, Any]],
    recognition_event: Mapping[str, Any] | None,
    target_bridge: Mapping[str, Any] | None,
    sequence: Mapping[str, Any] | None,
) -> dict[str, Any]:
    event_id = str(control_row["event_id"])
    market_legs = {str(row["leg"]): row for row in market["legs"]}
    control_legs = {
        str(row["leg_id"]): row for row in control_row["legs"]
    }
    regret_legs = {
        str(row["leg_id"]): row for row in control_row["regret_by_leg"]
    }
    recognition_legs = {
        str(row["leg_id"]): row
        for row in (recognition_event or {}).get("legs") or []
    }
    legs: dict[str, dict[str, Any]] = {}
    fills: list[dict[str, Any]] = []
    floor_times: list[float] = []
    frozen_references: list[int | None] = []
    for leg_id in sorted(control_legs):
        window = ladders[(event_id, leg_id)]
        ledger_leg = control_legs[leg_id]
        regret = regret_legs[leg_id]
        floor_price = regret.get("five_contract_proven_floor_cents")
        path = leg_path(
            market_leg=market_legs[leg_id],
            window=window,
            floor_price=(
                int(floor_price) if floor_price is not None else None
            ),
        )
        fill = compact_fill(ledger_leg, float(window["right_ts"]))
        if fill is not None:
            fills.append(fill)
        proof = path["five_contract_proven_floor"]
        if proof is not None and proof["proof_ts"] is not None:
            floor_times.append(float(proof["proof_ts"]))
        frozen_ref = {
            "available": bool(ledger_leg.get("available")),
            "price_cents": ledger_leg.get("window1_close_cents"),
            "timestamp": ledger_leg.get("reference_timestamp"),
            "reason": ledger_leg.get("reference_reason"),
            "source": ledger_leg.get("reference_source"),
        }
        frozen_references.append(frozen_ref["price_cents"])
        recognition = recognition_legs.get(leg_id)
        compact_recognition = None
        if recognition is not None:
            recognition_ts = recognition.get("recognition_ts")
            compact_recognition = {
                "recognition_ts": recognition_ts,
                "inside_frozen_policy_window": (
                    recognition_ts is None
                    or float(recognition_ts)
                    <= float(window["right_ts"]) + 1e-6
                ),
                "source": recognition.get("recognition_source"),
                "signals": recognition.get("signals") or [],
                "current_bid_cents": recognition.get(
                    "current_bid_cents"
                ),
                "current_ask_cents": recognition.get(
                    "current_ask_cents"
                ),
            }
        exposures = list(
            stream["exposures_by_leg"].get(leg_id) or []
        )
        fill_gap = (
            int(fill["price_cents"]) - int(floor_price)
            if fill is not None and floor_price is not None else None
        )
        legs[leg_id] = {
            "ticker": str(ledger_leg["ticker"]),
            "price_path": path,
            "five_contract_floor_cents": floor_price,
            "frozen_reference": frozen_ref,
            "recognition": compact_recognition,
            "exposures": exposures,
            "fill": fill,
            "fill_minus_proven_floor_cents_per_contract": fill_gap,
            "control_regret": {
                "execution_gap_cents": regret.get("execution_gap_cents"),
                "exposure_gap_cents": regret.get("exposure_gap_cents"),
                "recognition_gap_cents": regret.get(
                    "recognition_gap_cents"
                ),
                "target_selection_gap_cents": regret.get(
                    "target_selection_gap_cents"
                ),
            },
            "instrument_shape": stream["evidence_by_leg"].get(
                leg_id, {}
            ),
        }
    money = reference_money(
        fills=fills,
        ledger_references=frozen_references,
    )
    fill_times = [float(row["timestamp"]) for row in fills]
    floor_prices = [
        leg["five_contract_floor_cents"] for leg in legs.values()
    ]
    fill_price_sum = (
        sum(int(row["price_cents"]) for row in fills)
        if len(fills) == 2 else None
    )
    floor_sum = (
        sum(int(value) for value in floor_prices)
        if all(value is not None for value in floor_prices)
        else None
    )
    lawful_targets = [
        row for row in stream["targets"]
        if row["inside_frozen_policy_window"]
    ]
    lawful_exposures = [
        interval
        for leg in legs.values()
        for interval in leg["exposures"]
        if interval["opened_inside_frozen_policy_window"]
    ]
    recognized = bool(
        recognition_event and recognition_event.get("recognized")
    )
    boundary_status = str(control_row["boundary_status"])
    fill_count = len(fills)
    outcome = (
        "completed" if fill_count == 2
        else "one_leg" if fill_count == 1
        else "censored" if boundary_status != "positive"
        else "nothing"
    )
    last_lawful_close = max(
        (
            float(interval["lawful_closed_ts"])
            for interval in lawful_exposures
        ),
        default=None,
    )
    missing_legs = [
        leg_id for leg_id, leg in legs.items() if leg["fill"] is None
    ]
    close_gap = None
    if outcome == "one_leg" and len(missing_legs) == 1:
        missing = legs[missing_legs[0]]
        exposed_prices = [
            int(row["limit_price_cents"])
            for row in missing["exposures"]
            if row["opened_inside_frozen_policy_window"]
        ]
        if (
            exposed_prices
            and missing["five_contract_floor_cents"] is not None
        ):
            close_gap = (
                min(exposed_prices)
                - int(missing["five_contract_floor_cents"])
            )
    sequence_value = sequence_summary(sequence)
    right_view = (
        outcome == "completed"
        and all(
            leg["fill_minus_proven_floor_cents_per_contract"]
            is not None
            and 0 <= leg[
                "fill_minus_proven_floor_cents_per_contract"
            ] <= 4
            for leg in legs.values()
        )
    )
    wrong_view = (
        outcome == "nothing"
        and sequence_value["maker_under_par"]
    )
    close_view = (
        outcome == "one_leg"
        and close_gap is not None
        and 0 <= close_gap <= 5
    )
    return {
        "event_id": event_id,
        "event_date": control_row["event_date"],
        "category": control_row["category"],
        "slice": control_row["slice"],
        "boundary_status": boundary_status,
        "outcome": outcome,
        "scorer_stage": control_row["primary_loss_stage"],
        "physical_stage": physical_stage(
            boundary_status=boundary_status,
            fills=fill_count,
            lawful_targets=len(lawful_targets),
            lawful_exposures=len(lawful_exposures),
            recognized=recognized,
        ),
        "control_metrics": {
            "C": control_row["C"],
            "PC": control_row["PC"],
            "IC": control_row["IC"],
            "S": control_row["S"],
            "classification": control_row["classification"],
            "combined_delta_cents": control_row[
                "combined_delta_cents"
            ],
        },
        "recognized_by_instrument_lap": recognized,
        "recognition_target_bridge": target_bridge,
        "control_targets": stream["targets"],
        "legs": legs,
        "strict_sequential_oracle": sequence_value,
        "pair_money": money,
        "gaps": {
            "fill_minus_proven_floor_cents_per_leg": {
                leg_id: leg[
                    "fill_minus_proven_floor_cents_per_contract"
                ]
                for leg_id, leg in legs.items()
            },
            "fill_minus_proven_floor_cents_per_pair": (
                fill_price_sum - floor_sum
                if fill_price_sum is not None and floor_sum is not None
                else None
            ),
            "minutes_between_independent_floor_moments": (
                abs(floor_times[1] - floor_times[0]) / 60.0
                if len(floor_times) == 2 else None
            ),
            "minutes_between_our_fills": (
                abs(fill_times[1] - fill_times[0]) / 60.0
                if len(fill_times) == 2 else None
            ),
        },
        "views": {
            "right": right_view,
            "wrong": wrong_view,
            "close": close_view,
        },
        "close_view_detail": {
            "missing_leg_id": (
                missing_legs[0] if len(missing_legs) == 1 else None
            ),
            "best_exposed_minus_floor_cents": close_gap,
            "gave_up_ts": last_lawful_close,
        },
    }


def render_sweep(sweep: Mapping[str, Any]) -> str:
    horizon = sweep["horizon"]
    delta = sweep["delta_metrics"]
    fee = sweep["fee_units"]
    return "\n".join([
        "# Window-1 T2 scoring-chain unit and horizon sweep",
        "",
        "This is a source-and-data sweep, not a new package or audit.",
        "",
        "## Result",
        "",
        (
            f"- The extra live fee-unit error was in second-leg oracle "
            f"ranking. The corrected all-804 strict maker-under-par count "
            f"is **{fee['strict_sequential_maker_under_par_all_804']}**."
        ),
        (
            f"- **{horizon['reference_legs_after_frozen_right_count']}** "
            "frozen reference legs were read after the actual frozen "
            "`min(policy_horizon, guarded_cutoff)` right edge."
        ),
        (
            f"- Rebinding reference reads changes "
            f"**{horizon['reference_legs_changed_by_right_bound_count']}** "
            f"leg references and **"
            f"{horizon['completed_event_deltas_changed_count']}** completed-"
            "event deltas."
        ),
        (
            f"- Credited fills after the actual right edge: **"
            f"{horizon['credited_fill_legs_after_frozen_right_count']}**."
        ),
        (
            f"- Frozen floor-price changes: **"
            f"{sweep['floor_metrics']['floor_price_changes_from_horizon_correction']}"
            "**. The floor builder already used the correct minimum right "
            "edge."
        ),
        "",
        "## Delta movement",
        "",
        "| metric | frozen reference | corrected horizon reference |",
        "|---|---:|---:|",
        (
            f"| pre-fee PC | {delta['frozen_prefee_PC_count']} | "
            f"{delta['corrected_horizon_prefee_PC_count']} |"
        ),
        (
            f"| pre-fee IC | {delta['frozen_prefee_IC_count']} | "
            f"{delta['corrected_horizon_prefee_IC_count']} |"
        ),
        (
            f"| maker-fee PC | {delta['frozen_reference_maker_PC_count']} | "
            f"{delta['corrected_horizon_maker_PC_count']} |"
        ),
        (
            f"| maker-fee IC | {delta['frozen_reference_maker_IC_count']} | "
            f"{delta['corrected_horizon_maker_IC_count']} |"
        ),
        "",
        "## Every active occurrence in this scoring chain",
        "",
        "### Fee units",
        "",
        (
            "1. `window1_t2_target_laps.py::strict_sequential_floor`: "
            "previously fixed pair comparison now uses "
            "`(target1+target2)*5 + fee1+fee2 < 500`."
        ),
        (
            "2. `window1_t2_target_laps.py::cheapest_fill_after`: found in "
            "this sweep and fixed. It had ranked `target + five-contract "
            "fee`; it now ranks `target*5 + fee`."
        ),
        (
            "3. `window1_t2_maker_fee_reconciliation.py`: correct. It "
            "converts each five-contract fee back to a per-contract "
            "equivalent only when comparing with per-contract prices."
        ),
        (
            "4. `window1_t2_control_reconciliation.py`: unit conversion is "
            "correct, but its schedule is taker rather than maker and is "
            "therefore superseded."
        ),
        (
            "5. `window1_range_attack_scorer_v1.py` and the V2/T2 scorer "
            "delegation path: `FEE_CENTS` is added to per-contract delta. "
            "It is frozen at integer zero, so no frozen number moves, but "
            "the field is semantically per-contract and cannot accept a "
            "five-contract order total."
        ),
        (
            "6. `window1_t2_scoring_adapter_v1.py`, "
            "`window1_range_attack_instrument.py`, its V2 wrapper, and "
            "`window1_t2_causal_divot_instrument.py`: headroom uses "
            "`d1+d2+fee` in per-contract cents. Fee is frozen at zero, so "
            "there is no current arithmetic movement; a nonzero order-total "
            "fee would be a unit error."
        ),
        "",
        "### Frozen policy right edge",
        "",
        (
            "1. `window1_range_attack_prerun_builder.py`: correct source of "
            "`range_right = min(policy horizon, guarded cutoff)`; range "
            "floors are already bounded here."
        ),
        (
            "2. `window1_range_attack_reference_adapter_v1.py` and V2: "
            "active defect. They read through guarded cutoff without "
            "taking the shorter policy horizon. This flows into the Range-"
            "Attack scorers, T2 reference boundary, and V1-V5 T2 runners."
        ),
        (
            "3. `window1_t2_scoring_package_builder_v1.py::_derive_unique_"
            "fills`: checks guarded cutoff but not the shorter policy "
            "horizon. The data census above shows whether that admitted a "
            "late credited fill."
        ),
        (
            "4. `window1_t2_recognition_laps.py`: active analysis defect. "
            "It passes guarded cutoff as the recognition read edge instead "
            "of the frozen range right."
        ),
        (
            "5. `window1_t2_target_laps.py`: corrected before this grid. It "
            "now consumes the range-ladder right edge, includes the lawful "
            "right endpoint, and tests both leg orderings."
        ),
        "",
        "## Additional horizon census",
        "",
        (
            f"- Target actions after right edge: "
            f"{horizon['target_actions_after_frozen_right_count']}"
        ),
        (
            f"- Exposure opens after right edge: "
            f"{horizon['exposure_opens_after_frozen_right_count']}"
        ),
        (
            f"- Exposures extending after right edge: "
            f"{horizon['exposures_extending_after_frozen_right_count']}"
        ),
        (
            f"- Recognition legs after right edge: "
            f"{horizon['recognition_legs_after_frozen_right_count']} across "
            f"{horizon['recognition_events_affected_count']} events"
        ),
        "",
        "Holdout stayed sealed. Live and network access stayed off.",
        "",
    ])


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    cache = Path(args.market_cache).resolve()
    output_json = (repo / args.output_json).resolve()
    output_html = (repo / args.output_html).resolve()

    analysis_dir = Path(__file__).resolve().parent
    if str(analysis_dir) not in sys.path:
        sys.path.insert(0, str(analysis_dir))
    import window1_t2_target_laps as target_laps

    control_path = repo / CONTROL_LEDGER
    recognition_path = repo / RECOGNITION_JSON
    target_path = repo / TARGET_JSON
    control_rows = read_jsonl(control_path)
    if len(control_rows) != POPULATION:
        raise GridError(f"expected 804 control rows, found {len(control_rows)}")
    control = {str(row["event_id"]): row for row in control_rows}
    if len(control) != POPULATION:
        raise GridError("duplicate control event")
    ladders = load_ladders(repo)
    streams = load_streams(repo, ladders)
    recognition = read_json(recognition_path)
    recognition_events = {
        str(row["event_id"]): row
        for row in recognition["recognition"]["events"]
    }
    target = read_json(target_path)
    bridges = target_bridge_by_event(target)
    target_windows = {
        key: {
            "left": float(value["left_ts"]),
            "right": float(value["right_ts"]),
            "positive": bool(value["positive"]),
        }
        for key, value in ladders.items()
    }

    rows: list[dict[str, Any]] = []
    for index, event_id in enumerate(sorted(control), 1):
        market = load_market(cache, event_id)
        sequence = target_laps.strict_sequential_floor(
            control[event_id], market, target_windows
        )
        rows.append(build_row(
            control_row=control[event_id],
            stream=streams[event_id],
            market=market,
            ladders=ladders,
            recognition_event=recognition_events.get(event_id),
            target_bridge=bridges.get(event_id),
            sequence=sequence,
        ))
        if index % 50 == 0 or index == POPULATION:
            print(f"grid_events={index}/{POPULATION}", flush=True)

    view_counts = {
        name: sum(row["views"][name] for row in rows)
        for name in ("right", "wrong", "close")
    }
    outcome_counts = dict(sorted(Counter(
        row["outcome"] for row in rows
    ).items()))
    result = {
        "schema_version": VERSION,
        "scope": {
            "development_population": POPULATION,
            "holdout_opened": False,
            "live_accessed": False,
            "network_accessed": False,
            "orders_created": False,
            "scorer_executed": False,
        },
        "units": {
            "price_and_reference": "cents_per_contract",
            "maker_fee": "total_cents_for_five_contract_order",
            "pair_money_total": "total_cents_for_five_pairs",
            "quantity": QUANTITY,
            "path_bucket_columns": [
                "bucket_start_ts", "open_cents", "high_cents",
                "low_cents", "close_cents", "print_count",
                "executed_volume",
            ],
        },
        "summary": {
            "row_count": len(rows),
            "outcome_counts": outcome_counts,
            "view_counts": view_counts,
            "strict_sequential_under_par_count": sum(
                row["strict_sequential_oracle"]["maker_under_par"]
                for row in rows
            ),
            "completed_count": sum(
                row["outcome"] == "completed" for row in rows
            ),
            "tape_proven_floor_count": sum(
                all(
                    leg["five_contract_floor_cents"] is not None
                    for leg in row["legs"].values()
                )
                for row in rows
            ),
        },
        "view_definitions": {
            "right": (
                "completed; both credited fills are 0-4 cents above their "
                "lawful five-contract proven floors"
            ),
            "wrong": (
                "no credited fill; strict sequential five-contract maker "
                "oracle is lawful and under par"
            ),
            "close": (
                "exactly one credited fill; best lawful second-leg exposure "
                "was 0-5 cents above its proven floor"
            ),
        },
        "input_receipts": {
            "control_ledger": {
                "path": CONTROL_LEDGER,
                "sha256": sha256_file(control_path),
            },
            "recognition": {
                "path": RECOGNITION_JSON,
                "sha256": sha256_file(recognition_path),
            },
            "target_lap": {
                "path": TARGET_JSON,
                "sha256": sha256_file(target_path),
            },
            "range_ladders": {
                relative: sha256_file(repo / relative)
                for relative in RANGE_LADDERS
            },
            "control_streams": {
                relative: sha256_file(repo / relative)
                for relative in STREAMS
            },
            "market_cache": {
                "path_redacted": True,
                "cache_version": "window1-guarded-event-market-cache-v3",
                "events_read": POPULATION,
            },
        },
        "games": rows,
    }
    if len(result["games"]) != POPULATION:
        raise GridError("grid row count changed")
    if len({row["event_id"] for row in rows}) != POPULATION:
        raise GridError("grid event identity is not one-to-one")

    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    template = (analysis_dir / "window1_t2_game_grid_template.html").read_text(
        encoding="utf-8"
    )
    with output_html.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(template)
    print(json.dumps({
        "rows": len(rows),
        "outcomes": outcome_counts,
        "views": view_counts,
        "strict_under_par": result["summary"][
            "strict_sequential_under_par_count"
        ],
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
            "WINDOW1_T2_GAME_GRID.json"
        ),
    )
    result.add_argument(
        "--output-html",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_T2_GAME_GRID.html"
        ),
    )
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
