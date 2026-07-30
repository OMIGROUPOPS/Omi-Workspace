#!/usr/bin/env python3
"""Measure four live_v4 repairs alone and together on the fixed five games."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter
from pathlib import Path

from window1_live_v4_replay import (
    FILL_MODEL,
    PRINTS,
    build_print_index,
    load_scope,
    replay_one,
)


REPO = Path(__file__).resolve().parents[2]
SELECTION = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "delta_objective_20260729"
    / "FIVE_GAME_SELECTION.json"
)

FIXES = (
    "clock_contract_fixed",
    "field_contract_fixed",
    "contention_drop_fixed",
    "fill_poll_fixed",
)
PROFILES = {
    "four_defect_control": {key: False for key in FIXES},
    **{
        key.replace("_fixed", "") + "_only": {
            item: item == key for item in FIXES
        }
        for key in FIXES
    },
    "all_four_fixed": {key: True for key in FIXES},
}
CHURN_EVENTS = (
    "authority_foreign_order_flag",
    "authority_mismatch_defect",
    "authority_reanchor",
    "authority_retreat",
    "paper_order_cancelled",
    "order_cancelled",
    "entry_cancelled",
    "unbooked_fill_defect",
    "naked_leg_defect",
    "naked_tooth_heal",
    "reconcile_v4_adopted",
    "bulk_fill_receipt",
    "paper_stale_order_status_injected",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    return parser.parse_args()


def summarize_result(result: dict) -> dict:
    counts = Counter(row["event"] for row in result["trace"])
    fill_lags = []
    for leg, position in result["positions"].items():
        paper = next(
            (
                row
                for row in result["trace"]
                if row["event"] == "paper_fill" and row.get("leg") == leg
            ),
            None,
        )
        booked = next(
            (
                row
                for row in result["trace"]
                if row["event"] == "entry_filled"
                and row.get("leg") == leg
                and paper is not None
                and row["ts"] >= paper["ts"]
            ),
            None,
        )
        if paper and booked:
            fill_lags.append(round(booked["ts"] - paper["ts"], 3))
    churn = {event: counts[event] for event in CHURN_EVENTS if counts[event]}
    return {
        "event": result["event"],
        "category": result["category"],
        "pair_completed": bool(result["pair_completed"]),
        "legs_filled": sum(
            bool(row["filled"]) for row in result["positions"].values()
        ),
        "engine_booking_lag_seconds": fill_lags,
        "max_engine_booking_lag_seconds": max(fill_lags, default=None),
        "churn": churn,
        "churn_actions": sum(
            counts[event]
            for event in (
                "authority_reanchor",
                "authority_retreat",
                "paper_order_cancelled",
                "order_cancelled",
                "entry_cancelled",
                "naked_tooth_heal",
            )
        ),
        "defect_signals": sum(
            counts[event]
            for event in (
                "authority_foreign_order_flag",
                "authority_mismatch_defect",
                "unbooked_fill_defect",
                "naked_leg_defect",
            )
        ),
        "first_input_break": result["first_input_break"],
    }


async def main_async() -> int:
    args = parse_args()
    args.raw_out.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    event_ids = [
        row["event_id"]
        for row in json.loads(SELECTION.read_text(encoding="utf-8"))["games"]
    ]
    games = {event: load_scope(event)[0] for event in event_ids}
    ranges = build_print_index(
        PRINTS, args.raw_out / "_input_index" / "prints_by_ticker.json"
    )

    profile_rows = {}
    for profile_name, base_profile in PROFILES.items():
        rows = []
        profile = {**base_profile, "inject_fill_poll_miss": True}
        for index, event in enumerate(event_ids, 1):
            print(
                f"[{profile_name} {index}/5] {event}",
                flush=True,
            )
            result = await replay_one(
                games[event],
                ranges,
                args.raw_out / profile_name,
                defect_profile=profile,
                write_trace=False,
            )
            row = summarize_result(result)
            if row["first_input_break"] is not None:
                raise RuntimeError(
                    f"{profile_name}/{event}: {row['first_input_break']}"
                )
            rows.append(row)
            del result
        totals = Counter()
        for row in rows:
            totals.update(row["churn"])
        profile_rows[profile_name] = {
            "profile": profile,
            "pair_completions_out_of_5": sum(
                row["pair_completed"] for row in rows
            ),
            "legs_filled_out_of_10": sum(row["legs_filled"] for row in rows),
            "churn_actions": sum(row["churn_actions"] for row in rows),
            "defect_signals": sum(row["defect_signals"] for row in rows),
            "max_engine_booking_lag_seconds": max(
                (
                    row["max_engine_booking_lag_seconds"]
                    for row in rows
                    if row["max_engine_booking_lag_seconds"] is not None
                ),
                default=None,
            ),
            "event_counts": dict(sorted(totals.items())),
            "games": rows,
        }

    control = profile_rows["four_defect_control"]
    for name, row in profile_rows.items():
        row["versus_control"] = {
            "pair_completions": (
                row["pair_completions_out_of_5"]
                - control["pair_completions_out_of_5"]
            ),
            "legs_filled": (
                row["legs_filled_out_of_10"]
                - control["legs_filled_out_of_10"]
            ),
            "churn_actions": row["churn_actions"] - control["churn_actions"],
            "defect_signals": row["defect_signals"] - control["defect_signals"],
            "max_booking_lag_seconds": (
                None
                if row["max_engine_booking_lag_seconds"] is None
                or control["max_engine_booking_lag_seconds"] is None
                else round(
                    row["max_engine_booking_lag_seconds"]
                    - control["max_engine_booking_lag_seconds"],
                    3,
                )
            ),
        }

    payload = {
        "schema_version": "window1-live-defect-replay-v1",
        "fill_model": FILL_MODEL,
        "selection": str(SELECTION),
        "events": event_ids,
        "fault_model": (
            "single-order status remains stale after an actual paper fill; "
            "account fill receipts and positions remain current"
        ),
        "profiles": profile_rows,
    }
    args.summary_out.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(
        {
            name: {
                key: row[key]
                for key in (
                    "pair_completions_out_of_5",
                    "legs_filled_out_of_10",
                    "churn_actions",
                    "defect_signals",
                    "max_engine_booking_lag_seconds",
                    "versus_control",
                )
            }
            for name, row in profile_rows.items()
        },
        indent=2,
    ))
    return 0


def main() -> int:
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
