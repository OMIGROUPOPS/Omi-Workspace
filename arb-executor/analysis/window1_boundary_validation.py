#!/usr/bin/env python3
"""Apply repaired real-start truth to the passed actual lifecycle census.

This remains actual-trade reproduction, not counterfactual policy scoring.
PC/NC/IC overlap inside C; X is reported independently and may overlap C when
completion is exact but the frozen close reference is not recoverable.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


VERSION = "window1-boundary-validation-v1"
D = 804
LOT = 5.0
PAR = 100.0


class ValidationError(RuntimeError):
    pass


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    output = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValidationError(f"non-object {path}:{line_number}")
            output.append(row)
    return output


def parse_epoch(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
        if result > 10_000_000_000:
            result /= 1000.0
        return result if math.isfinite(result) else None
    try:
        stamp = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    return stamp.timestamp()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_prints(
    path: Path,
    bounds_by_ticker: dict[str, tuple[float, float]],
) -> dict[str, list[tuple[float, int, float, str]]]:
    output: dict[str, list[tuple[float, int, float, str]]] = defaultdict(list)
    seen = set()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            identity = str(
                row.get("trade_id") or row.get("receipt_id") or ""
            )
            ticker = str(row.get("ticker") or "")
            timestamp = parse_epoch(row.get("exchange_ts"))
            try:
                price = int(row.get("price_cents"))
                size = float(row.get("size") or 0)
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    f"bad public print row {line_number}"
                ) from exc
            if (
                not identity or not ticker or timestamp is None
                or row.get("true_print") is not True
                or not 1 <= price <= 99 or size < 0
            ):
                raise ValidationError(
                    f"invalid public print row {line_number}"
                )
            bounds = bounds_by_ticker.get(ticker)
            if (
                bounds is None or timestamp < bounds[0]
                or timestamp > bounds[1]
            ):
                continue
            if identity in seen:
                continue
            seen.add(identity)
            if (
                size > 0
            ):
                output[ticker].append(
                    (timestamp, price, size, identity)
                )
    for rows in output.values():
        rows.sort()
    return output


def final_reference(
    prints: list[tuple[float, int, float, str]],
    left: float,
    right: float,
) -> int | None:
    result = None
    for timestamp, price, _size, _identity in prints:
        if timestamp < left:
            continue
        if timestamp > right:
            break
        result = price
    return result


def effective_safe_cutoff(start: dict[str, Any]) -> float | None:
    cutoff = parse_epoch(start.get("safe_prestart_cutoff_utc"))
    if (
        cutoff is not None
        and start.get("safe_prestart_cutoff_inclusive") is False
    ):
        return math.nextafter(cutoff, -math.inf)
    return cutoff


def classify_leg(
    lifecycle: dict[str, Any],
    start: dict[str, Any],
    left_edge: float,
) -> dict[str, Any]:
    status = str(lifecycle["status"])
    completion = parse_epoch(lifecycle.get("completion_exchange_ts"))
    first_fill = parse_epoch(lifecycle.get("first_fill_exchange_ts"))
    exact_start = parse_epoch(start.get("verified_start_utc"))
    safe_cutoff = effective_safe_cutoff(start)
    known_live_by = parse_epoch(start.get("known_live_by_utc"))
    if status == "exact_nonfill":
        ruling = "exact_window1_nonfill"
        possible = False
    elif status == "exact_filled_five":
        if safe_cutoff is not None:
            if (
                first_fill is not None and completion is not None
                and first_fill >= left_edge
                and completion <= safe_cutoff
            ):
                ruling = "proven_window1_fill_five"
                possible = True
            elif completion is not None and completion < left_edge:
                ruling = "exact_pre_window_inventory_not_window1"
                possible = False
            elif (
                first_fill is not None and completion is not None
                and first_fill < left_edge <= completion <= safe_cutoff
            ):
                ruling = "censored_quantity_crosses_left_edge"
                possible = True
            else:
                ruling = "exact_post_start_noncompletion"
                possible = False
        elif (
            known_live_by is not None and completion is not None
            and completion >= known_live_by
        ):
            ruling = "exact_not_complete_before_known_live_bound"
            possible = False
        else:
            ruling = "censored_start_boundary"
            possible = True
    elif status == "exact_filled_other_quantity":
        ruling = "exact_quantity_not_five"
        possible = False
    else:
        ruling = "censored_lifecycle"
        possible = bool(
            lifecycle.get("possible_five_contract_upper_bound", True)
        )
    return {
        "event_id": lifecycle["event_id"],
        "ticker": lifecycle["ticker"],
        "source_lifecycle_status": status,
        "window1_ruling": ruling,
        "proven_window1_fill_five": (
            ruling == "proven_window1_fill_five"
        ),
        "possible_window1_fill_five": possible,
        "official_fill_quantity": lifecycle.get("official_fill_quantity"),
        "official_fill_vwap_cents": lifecycle.get(
            "official_fill_vwap_cents"
        ),
        "first_fill_exchange_ts": lifecycle.get(
            "first_fill_exchange_ts"
        ),
        "completion_exchange_ts": lifecycle.get(
            "completion_exchange_ts"
        ),
        "start_state": start["start_state"],
        "verified_start_utc": start.get("verified_start_utc"),
        "verified_start_time_basis": start.get(
            "verified_start_time_basis"
        ),
        "known_live_by_utc": start.get("known_live_by_utc"),
        "known_live_by_time_basis": start.get(
            "known_live_by_time_basis"
        ),
        "safe_prestart_cutoff_utc": start.get(
            "safe_prestart_cutoff_utc"
        ),
        "safe_prestart_cutoff_time_basis": start.get(
            "safe_prestart_cutoff_time_basis"
        ),
        "boundary_censored": start["boundary_censored"],
        "first_fill_precedes_exact_start": (
            first_fill < exact_start
            if first_fill is not None and exact_start is not None else None
        ),
        "first_fill_at_or_after_left_edge": (
            first_fill >= left_edge if first_fill is not None else None
        ),
    }


def run(args: argparse.Namespace) -> int:
    lifecycle_path = Path(args.lifecycle_ledger).resolve()
    lifecycle_summary = json.loads(
        Path(args.lifecycle_summary).resolve().read_text(encoding="utf-8")
    )
    start_path = Path(args.start_ledger).resolve()
    prints_path = Path(args.public_prints).resolve()
    if (
        lifecycle_summary.get("gate_pass") is not True
        or lifecycle_summary.get("D") != D
    ):
        raise ValidationError("pre-existing lifecycle gate did not pass")
    lifecycle = read_jsonl(lifecycle_path)
    starts = read_jsonl(start_path)
    if len(lifecycle) != 1608 or len(starts) != D:
        raise ValidationError("immutable lifecycle/start grain changed")
    by_event_start = {row["event_id"]: row for row in starts}
    if len(by_event_start) != D:
        raise ValidationError("duplicate start ledger event")
    reference_bounds = {}
    for start in starts:
        exact = effective_safe_cutoff(start)
        scheduled = parse_epoch(start.get("scheduled_start_exchange_ts"))
        if exact is None or scheduled is None:
            continue
        bounds = (
            scheduled - args.left_edge_hours_before_schedule * 3600,
            exact,
        )
        for leg in start["legs"]:
            reference_bounds[str(leg["ticker"])] = bounds
    prints = load_prints(prints_path, reference_bounds)
    legs_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    leg_rows = []
    for row in lifecycle:
        start = by_event_start.get(row["event_id"])
        if start is None:
            raise ValidationError(
                f"missing start row: {row['event_id']}"
            )
        scheduled = parse_epoch(start.get("scheduled_start_exchange_ts"))
        if scheduled is None:
            raise ValidationError(
                f"missing scheduled start: {row['event_id']}"
            )
        left_edge = (
            scheduled - args.left_edge_hours_before_schedule * 3600
        )
        result = classify_leg(row, start, left_edge)
        legs_by_event[row["event_id"]].append(result)
        leg_rows.append(result)

    event_rows = []
    for start in starts:
        event_id = start["event_id"]
        legs = legs_by_event[event_id]
        if len(legs) != 2:
            raise ValidationError(f"event leg count changed: {event_id}")
        exact_c = all(row["proven_window1_fill_five"] for row in legs)
        possible_c = all(row["possible_window1_fill_five"] for row in legs)
        combined = None
        references = []
        deltas = []
        if exact_c:
            prices = [
                float(row["official_fill_vwap_cents"]) for row in legs
            ]
            combined = sum(prices)
            exact_start = effective_safe_cutoff(start)
            scheduled = parse_epoch(
                start["scheduled_start_exchange_ts"]
            )
            if exact_start is None:
                raise ValidationError(
                    "exact C lacks exact start by construction"
                )
            for index, row in enumerate(legs):
                reference = final_reference(
                    prints.get(row["ticker"], []),
                    scheduled
                    - args.left_edge_hours_before_schedule * 3600,
                    exact_start,
                )
                references.append(reference)
                deltas.append(
                    float(row["official_fill_vwap_cents"]) - reference
                    if reference is not None else None
                )
        PC = exact_c and combined is not None and combined < PAR
        NC = (
            exact_c and deltas and all(value is not None for value in deltas)
            and sum(deltas) < 0
        )
        IC = (
            exact_c and deltas and all(value is not None for value in deltas)
            and all(value < 0 for value in deltas)
        )
        lifecycle_censored = any(
            row["window1_ruling"].startswith("censored")
            for row in legs
        )
        reference_censored = exact_c and any(
            value is None for value in references
        )
        event_rows.append({
            "schema_version": VERSION,
            "event_id": event_id,
            "event_date": start["event_date"],
            "category": start["category"],
            "C": exact_c,
            "PC": PC,
            "NC": NC,
            "IC": IC,
            "X": lifecycle_censored or reference_censored,
            "possible_C": possible_c,
            "combined_entry_cost_cents": combined,
            "combined_vs_par_delta_cents": (
                combined - PAR if combined is not None else None
            ),
            "individual_leg_reference_cents": references,
            "individual_leg_deltas_cents": deltas,
            "combined_reference_delta_cents": (
                sum(deltas)
                if deltas and all(value is not None for value in deltas)
                else None
            ),
            "lifecycle_censored": lifecycle_censored,
            "reference_censored": reference_censored,
            "start_state": start["start_state"],
            "legs": legs,
        })
    raw = {
        "D": D,
        "C": sum(row["C"] for row in event_rows),
        "PC": sum(row["PC"] for row in event_rows),
        "NC": sum(row["NC"] for row in event_rows),
        "IC": sum(row["IC"] for row in event_rows),
        "X": sum(row["X"] for row in event_rows),
    }
    pair_deltas = [
        row["combined_reference_delta_cents"] for row in event_rows
        if row["combined_reference_delta_cents"] is not None
    ]
    leg_deltas = [
        value for row in event_rows
        for value in row["individual_leg_deltas_cents"]
        if value is not None
    ]
    summary = {
        "schema_version": VERSION,
        "status": "actual_reproduction_with_repaired_start_grain",
        "performance_or_ceiling_verdict": False,
        "D": D,
        "gate_pass": True,
        "raw": raw,
        "denominators": {
            "C_over_D": [raw["C"], D],
            "PC_over_C": [raw["PC"], raw["C"]],
            "PC_over_D": [raw["PC"], D],
            "NC_over_C": [raw["NC"], raw["C"]],
            "NC_over_D": [raw["NC"], D],
            "IC_over_C": [raw["IC"], raw["C"]],
            "IC_over_D": [raw["IC"], D],
            "X_over_D": [raw["X"], D],
        },
        "bounds": {
            "C": {
                "worst": raw["C"],
                "observed": raw["C"],
                "best": sum(row["possible_C"] for row in event_rows),
            },
            "PC": {
                "worst": raw["PC"],
                "observed": raw["PC"],
                "best": raw["PC"] + sum(
                    row["possible_C"] and not row["C"]
                    for row in event_rows
                ),
            },
            "NC": {
                "worst": raw["NC"],
                "observed": raw["NC"],
                "best": raw["NC"] + sum(
                    row["possible_C"] and not row["C"]
                    for row in event_rows
                ),
            },
            "IC": {
                "worst": raw["IC"],
                "observed": raw["IC"],
                "best": raw["IC"] + sum(
                    row["possible_C"] and not row["C"]
                    for row in event_rows
                ),
            },
        },
        "metric_law": {
            "PC_NC_IC_relationship": (
                "overlapping subsets of C; not partitions"
            ),
            "X_relationship": (
                "reported independently; can overlap exact C only when "
                "the frozen reference is unavailable"
            ),
            "combined_cost": "sum of two actual entry VWAPs",
            "combined_vs_par": "combined entry cost minus 100",
            "leg_delta": (
                "actual leg VWAP minus that leg's final verified-size public "
                "print at or before the exact observed Window-1 close"
            ),
            "pair_delta": "sum of the two individual leg deltas",
            "left_edge_hours_before_schedule": (
                args.left_edge_hours_before_schedule
            ),
        },
        "start_state_counts": dict(Counter(
            row["start_state"] for row in event_rows
        )),
        "leg_ruling_counts": dict(Counter(
            row["window1_ruling"] for row in leg_rows
        )),
        "combined_reference_delta": {
            "n": len(pair_deltas),
            "mean": statistics.mean(pair_deltas) if pair_deltas else None,
            "median": statistics.median(pair_deltas) if pair_deltas else None,
            "negative_count": sum(value < 0 for value in pair_deltas),
        },
        "individual_leg_delta": {
            "n": len(leg_deltas),
            "mean": statistics.mean(leg_deltas) if leg_deltas else None,
            "median": statistics.median(leg_deltas) if leg_deltas else None,
            "negative_count": sum(value < 0 for value in leg_deltas),
            "negative_rate": (
                sum(value < 0 for value in leg_deltas) / len(leg_deltas)
                if leg_deltas else None
            ),
        },
        "input_hashes": {
            "lifecycle_ledger": sha256_file(lifecycle_path),
            "start_ledger": sha256_file(start_path),
            "public_prints": sha256_file(prints_path),
        },
    }
    event_output = Path(args.event_output).resolve()
    leg_output = Path(args.leg_output).resolve()
    event_output.parent.mkdir(parents=True, exist_ok=True)
    with event_output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in event_rows:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")
    with leg_output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in leg_rows:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")
    summary["output_hashes"] = {
        "event_ledger": sha256_file(event_output),
        "leg_ledger": sha256_file(leg_output),
    }
    Path(args.summary_output).resolve().write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "raw": raw,
        "bounds": summary["bounds"],
        "performance_or_ceiling_verdict": False,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--lifecycle-ledger", required=True)
    result.add_argument("--lifecycle-summary", required=True)
    result.add_argument("--start-ledger", required=True)
    result.add_argument("--public-prints", required=True)
    result.add_argument(
        "--left-edge-hours-before-schedule", type=int, required=True
    )
    result.add_argument("--event-output", required=True)
    result.add_argument("--leg-output", required=True)
    result.add_argument("--summary-output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
