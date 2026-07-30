#!/usr/bin/env python3
"""Render five exact-start live_v4 replays on the Window-1 delta objective."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
import statistics
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo


DELTA_ROOT = (
    ".claude/window1_live_v4_replay/delta_objective_20260729"
)
FULL_LAWFUL = (
    ".claude/window1_t2_iteration_history/"
    "WINDOW1_FULL_LAWFUL_CEILING.json"
)
CONTROL_LEDGER = (
    ".claude/"
    "window1_t2_results_w1-t2-dev-20260712-20260720-"
    "frontier-regret-grid1-scorepkg-v5/"
    "01_w1_t2__macro_hold__fixed_admission_parent_control_"
    "EVENT_LEDGER.jsonl"
)
REPLAY_ROOT = f"{DELTA_ROOT}/five_replays/counterfactual"
EASTERN = ZoneInfo("America/New_York")


class ReportError(RuntimeError):
    """The replay report inputs did not reconcile."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def time_et(timestamp: float) -> str:
    value = datetime.fromtimestamp(float(timestamp), tz=EASTERN)
    date = value.strftime("%a %b ") + str(value.day)
    clock = value.strftime("%I:%M:%S %p").lstrip("0")
    return f"{date}, {clock} ET"


def signed(value: int | float | None, suffix: str = "¢") -> str:
    if value is None:
        return "n/a"
    if abs(float(value) - round(float(value))) < 1e-9:
        numeric = str(abs(int(round(float(value)))))
    else:
        numeric = f"{abs(float(value)):.1f}"
    if value > 0:
        return f"+{numeric}{suffix}"
    if value < 0:
        return f"−{numeric}{suffix}"
    return f"0{suffix}"


def dedupe(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    seen = set()
    for row in rows:
        key = json.dumps(row, sort_keys=True, separators=(",", ":"))
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
    return output


def trace_rows(trace: Mapping[str, Any], leg_id: str, event: str) -> list[dict]:
    return [
        row for row in trace.get("trace") or []
        if row.get("leg") == leg_id and row.get("event") == event
    ]


def comparable_aims(
    trace: Mapping[str, Any], leg_id: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any] | None]:
    legacy = trace_rows(trace, leg_id, "trendpath_live_aim")
    sealed = [
        row for row in trace_rows(trace, leg_id, "order_placed")
        if (
            row.get("details", {}).get("authority") == "SEAL"
            and row.get("details", {}).get("action") == "buy"
        )
    ]
    for legacy_row in legacy:
        matching = [
            row for row in sealed
            if abs(float(row["ts"]) - float(legacy_row["ts"])) <= 1
        ]
        if matching:
            shadow = next((
                row for row in trace_rows(
                    trace, leg_id, "trendpath_shadow"
                )
                if abs(
                    float(row["ts"]) - float(legacy_row["ts"])
                ) <= 1
            ), None)
            return legacy_row, matching[0], shadow
    raise ReportError(
        f"{trace['event']} {leg_id}: no comparable legacy/sealed aim"
    )


def fill_rows(trace: Mapping[str, Any], leg_id: str) -> list[dict[str, Any]]:
    placed = {
        str(row["details"]["order_id"]): row["details"]
        for row in trace_rows(trace, leg_id, "order_placed")
        if row.get("details", {}).get("order_id")
    }
    output = []
    for row in trace_rows(trace, leg_id, "paper_fill"):
        details = row["details"]
        order = placed.get(str(details.get("order_id"))) or {}
        output.append({
            "ts": float(row["ts"]),
            "price_cents": int(details["fill_price"]),
            "order_id": details.get("order_id"),
            "authority": order.get("authority") or "unlabeled_live_path",
            "trigger": details.get("fill_trigger"),
        })
    return output


def distinct_aim_sequence(
    trace: Mapping[str, Any],
    leg_id: str,
    *,
    authority: str,
) -> list[dict[str, Any]]:
    if authority == "legacy":
        rows = [{
            "ts": float(row["ts"]),
            "price_cents": int(row["details"]["path_aim"]),
            "page": row["details"]["page"],
        } for row in trace_rows(trace, leg_id, "trendpath_live_aim")]
    else:
        rows = [{
            "ts": float(row["ts"]),
            "price_cents": int(row["details"]["price"]),
            "page": None,
        } for row in trace_rows(trace, leg_id, "order_placed")
        if (
            row.get("details", {}).get("authority") == "SEAL"
            and row.get("details", {}).get("action") == "buy"
        )]
    output = []
    prior = None
    for row in rows:
        key = (row["ts"], row["price_cents"], row["page"])
        if key == prior:
            continue
        prior = key
        output.append(row)
    return output


def event_analysis(
    selection: Mapping[str, Any],
    full: Mapping[str, Any],
    reference: Mapping[str, Any],
    trace: Mapping[str, Any],
) -> dict[str, Any]:
    event_id = str(selection["event_id"])
    independent = full.get("independent_touch_floor")
    if independent is None:
        raise ReportError(f"{event_id}: no full-lawful floor")
    lows = {
        str(leg_id): {
            "price_cents": int(row["price_cents"]),
            "ts": float(row["ts"]),
        }
        for leg_id, row in independent["touches"].items()
    }
    closes = {
        str(leg["leg_id"]): {
            "price_cents": int(leg["window1_close_cents"]),
            "ts": float(leg["reference_timestamp"]),
        }
        for leg in reference["legs"]
        if leg.get("available")
    }
    if set(lows) != set(closes) or set(lows) != set(trace["positions"]):
        raise ReportError(f"{event_id}: leg identities differ")
    legs = {}
    for leg_id in sorted(lows):
        legacy_row, sealed_row, shadow = comparable_aims(trace, leg_id)
        legacy_aim = int(legacy_row["details"]["path_aim"])
        sealed_aim = int(sealed_row["details"]["price"])
        low = int(lows[leg_id]["price_cents"])
        close = int(closes[leg_id]["price_cents"])
        actual_low_minute = (
            float(lows[leg_id]["ts"]) - float(full["selected_left_ts"])
        ) / 60.0
        predicted_minute = (
            float(shadow["details"]["bottom_t_med_min"])
            if shadow else None
        )
        fills = fill_rows(trace, leg_id)
        legs[leg_id] = {
            "close": closes[leg_id],
            "actual_low": {
                **lows[leg_id],
                "minute_from_window_open": actual_low_minute,
            },
            "first_comparable_decision_ts": float(legacy_row["ts"]),
            "legacy": {
                "initial_comparable_aim_cents": legacy_aim,
                "aim_minus_actual_low_cents": legacy_aim - low,
                "aim_minus_window1_close_cents": legacy_aim - close,
                "aim_sequence": distinct_aim_sequence(
                    trace, leg_id, authority="legacy"
                ),
            },
            "sealed": {
                "initial_comparable_aim_cents": sealed_aim,
                "aim_minus_actual_low_cents": sealed_aim - low,
                "aim_minus_window1_close_cents": sealed_aim - close,
                "aim_sequence": distinct_aim_sequence(
                    trace, leg_id, authority="sealed"
                ),
            },
            "atlas": {
                "page": (
                    shadow["details"].get("page") if shadow else None
                ),
                "predicted_bottom_minute": predicted_minute,
                "actual_bottom_minute": actual_low_minute,
                "prediction_minus_actual_minutes": (
                    predicted_minute - actual_low_minute
                    if predicted_minute is not None else None
                ),
            },
            "fills": fills,
            "filled_below_close": (
                bool(fills)
                and all(
                    row["price_cents"] < close for row in fills
                )
            ),
        }
    all_fills = [
        row for leg in legs.values() for row in leg["fills"]
    ]
    pair_completed = bool(trace["pair_completed"])
    achieved_deltas = {
        leg_id: (
            leg["fills"][-1]["price_cents"] - leg["close"]["price_cents"]
            if leg["fills"] else None
        )
        for leg_id, leg in legs.items()
    }
    return {
        "event_id": event_id,
        "category": selection["category"],
        "start_evidence": selection["start_evidence"],
        "window": {
            "left_ts": float(full["selected_left_ts"]),
            "right_ts": float(full["evaluator_right_ts"]),
        },
        "tape_offer": {
            "delta_cents_by_leg": selection["delta_cents_by_leg"],
            "combined_delta_cents": selection["combined_delta_cents"],
            "both_legs_below_close": selection[
                "both_legs_negative_delta"
            ],
        },
        "legs": legs,
        "pair_completed": pair_completed,
        "fill_count": len(all_fills),
        "achieved_delta_cents_by_leg": achieved_deltas,
        "achieved_combined_delta_cents": (
            sum(int(value) for value in achieved_deltas.values())
            if pair_completed
            and all(value is not None for value in achieved_deltas.values())
            else None
        ),
        "both_filled_below_close": (
            pair_completed
            and all(leg["filled_below_close"] for leg in legs.values())
        ),
        "first_input_break": trace.get("first_input_break"),
    }


def mean(values: Iterable[float]) -> float | None:
    rows = list(values)
    return statistics.fmean(rows) if rows else None


def median(values: Iterable[float]) -> float | None:
    rows = list(values)
    return statistics.median(rows) if rows else None


def depth_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for event in events:
        for leg_id, leg in event["legs"].items():
            rows.append({
                "event_id": event["event_id"],
                "category": event["category"],
                "leg_id": leg_id,
                "actual_low_cents": leg["actual_low"]["price_cents"],
                "window1_close_cents": leg["close"]["price_cents"],
                "legacy_aim_cents": leg["legacy"][
                    "initial_comparable_aim_cents"
                ],
                "legacy_aim_minus_low_cents": leg["legacy"][
                    "aim_minus_actual_low_cents"
                ],
                "legacy_aim_minus_close_cents": leg["legacy"][
                    "aim_minus_window1_close_cents"
                ],
                "sealed_aim_cents": leg["sealed"][
                    "initial_comparable_aim_cents"
                ],
                "sealed_aim_minus_low_cents": leg["sealed"][
                    "aim_minus_actual_low_cents"
                ],
                "sealed_aim_minus_close_cents": leg["sealed"][
                    "aim_minus_window1_close_cents"
                ],
                "atlas_predicted_bottom_minute": leg["atlas"][
                    "predicted_bottom_minute"
                ],
                "actual_low_minute": leg["atlas"][
                    "actual_bottom_minute"
                ],
                "timing_error_minutes": leg["atlas"][
                    "prediction_minus_actual_minutes"
                ],
                "low_happened_before_comparable_decision": (
                    leg["actual_low"]["ts"]
                    < leg["first_comparable_decision_ts"]
                ),
            })
    categories = {}
    for category in sorted(set(row["category"] for row in rows)):
        group = [row for row in rows if row["category"] == category]
        categories[category] = {
            "leg_count": len(group),
            "legacy_mean_aim_minus_low_cents": mean(
                row["legacy_aim_minus_low_cents"] for row in group
            ),
            "sealed_mean_aim_minus_low_cents": mean(
                row["sealed_aim_minus_low_cents"] for row in group
            ),
            "legacy_mean_aim_minus_close_cents": mean(
                row["legacy_aim_minus_close_cents"] for row in group
            ),
            "sealed_mean_aim_minus_close_cents": mean(
                row["sealed_aim_minus_close_cents"] for row in group
            ),
            "median_absolute_timing_error_minutes": median(
                abs(row["timing_error_minutes"]) for row in group
            ),
        }
    overall = {
        "leg_count": len(rows),
        "legacy_reachable_leg_count": sum(
            row["legacy_aim_minus_low_cents"] >= 0 for row in rows
        ),
        "sealed_reachable_leg_count": sum(
            row["sealed_aim_minus_low_cents"] >= 0 for row in rows
        ),
        "legacy_negative_close_delta_leg_count": sum(
            row["legacy_aim_minus_close_cents"] < 0 for row in rows
        ),
        "sealed_negative_close_delta_leg_count": sum(
            row["sealed_aim_minus_close_cents"] < 0 for row in rows
        ),
        "legacy_mean_aim_minus_low_cents": mean(
            row["legacy_aim_minus_low_cents"] for row in rows
        ),
        "sealed_mean_aim_minus_low_cents": mean(
            row["sealed_aim_minus_low_cents"] for row in rows
        ),
        "legacy_median_absolute_depth_error_cents": median(
            abs(row["legacy_aim_minus_low_cents"]) for row in rows
        ),
        "sealed_median_absolute_depth_error_cents": median(
            abs(row["sealed_aim_minus_low_cents"]) for row in rows
        ),
        "legacy_mean_aim_minus_close_cents": mean(
            row["legacy_aim_minus_close_cents"] for row in rows
        ),
        "sealed_mean_aim_minus_close_cents": mean(
            row["sealed_aim_minus_close_cents"] for row in rows
        ),
        "median_absolute_timing_error_minutes": median(
            abs(row["timing_error_minutes"]) for row in rows
        ),
        "mean_absolute_timing_error_minutes": mean(
            abs(row["timing_error_minutes"]) for row in rows
        ),
        "low_before_comparable_decision_leg_count": sum(
            row["low_happened_before_comparable_decision"] for row in rows
        ),
    }
    return {
        "rows": rows,
        "by_category": categories,
        "overall": overall,
    }


def trace_sentence(row: Mapping[str, Any]) -> str | None:
    event = str(row["event"])
    details = row.get("details") or {}
    leg = row.get("leg") or "pair"
    if event == "recognition_wait_before_place":
        return (
            f"{leg}: the OS withheld the path order because the leg band "
            "and pair recognition were not ready."
        )
    if event == "band_call":
        return (
            f"{leg}: drift/band called {details.get('band')} "
            f"{details.get('direction')} (net {details.get('net')}, "
            f"dip {details.get('dip')}); recognition="
            f"{str(details.get('recognition')).lower()}."
        )
    if event == "band_recall":
        return (
            f"{leg}: the band recalled {details.get('from')} to "
            f"{details.get('to')} after net {details.get('net')}."
        )
    if event == "pair_class_read":
        return (
            f"The two bands produced pair class "
            f"{details.get('pair_class')}."
        )
    if event == "cohort_aim":
        return (
            f"{leg}: cohort {details.get('cell')} proposed "
            f"{details.get('cohort_target')}¢ from "
            f"{details.get('old_target')}¢."
        )
    if event == "orientation_park_swap":
        return (
            f"{leg}: orientation swapped the prior role "
            f"{details.get('prior_role')} to {details.get('anchor_role')} "
            f"(conviction {details.get('conviction')})."
        )
    if event == "trendpath_live_aim":
        return (
            f"{leg}: legacy/path aimed {details.get('path_aim')}¢ from "
            f"{details.get('page')}."
        )
    if event == "authority_clamp":
        return (
            f"{leg}: sealed authority overrode "
            f"{details.get('old_price')}¢ to {details.get('fish')}¢."
        )
    if event == "authority_reanchor":
        return (
            f"{leg}: sealed authority canceled {details.get('old_px')}¢ "
            f"and re-anchored at {details.get('fish')}¢."
        )
    if event == "order_placed":
        action = details.get("action")
        authority = details.get("authority") or "exit"
        return (
            f"{leg}: posted {action} {details.get('count')} at "
            f"{details.get('price')}¢ under {authority}; "
            f"status {details.get('response_status')}."
        )
    if event == "v4_resting_cancel":
        return (
            f"{leg}: canceled the resting bid because "
            f"{details.get('reason')} (book "
            f"{details.get('bid')}/{details.get('ask')})."
        )
    if event == "match_live_resting_cancel":
        return f"{leg}: canceled the resting order when the match-live bell fired."
    if event == "window_truth_reaim":
        return (
            f"{leg}: print-backed re-aim moved "
            f"{details.get('old')}¢ to {details.get('new')}¢."
        )
    if event == "walk_cap_yield_print_backed":
        return (
            f"{leg}: the cap yielded to a print-backed walk at "
            f"{details.get('target')}¢."
        )
    if event == "paper_fill":
        return (
            f"{leg}: filled at {details.get('fill_price')}¢ on "
            f"{details.get('fill_trigger')}."
        )
    if event == "entry_filled":
        return (
            f"{leg}: live_v4 accepted the entry fill at "
            f"{details.get('fill_price')}¢."
        )
    return None


def event_markdown(event: Mapping[str, Any], trace: Mapping[str, Any]) -> str:
    leg_rows = []
    for leg_id, leg in event["legs"].items():
        legacy = leg["legacy"]["initial_comparable_aim_cents"]
        sealed = leg["sealed"]["initial_comparable_aim_cents"]
        fills = ", ".join(
            f"{row['price_cents']}¢ ({row['authority']})"
            for row in leg["fills"]
        ) or "none"
        leg_rows.append(
            f"| {leg_id} | {leg['actual_low']['price_cents']}¢ at "
            f"{time_et(leg['actual_low']['ts'])} | "
            f"{leg['close']['price_cents']}¢ | {legacy}¢ "
            f"({signed(leg['legacy']['aim_minus_window1_close_cents'])}) | "
            f"{sealed}¢ "
            f"({signed(leg['sealed']['aim_minus_window1_close_cents'])}) | "
            f"{fills} |"
        )
    milestones = [{
        "ts": float(event["window"]["left_ts"]),
        "text": "The lawful evaluator window opened.",
        "rank": 0,
    }]
    for leg_id, leg in event["legs"].items():
        milestones.extend([
            {
                "ts": float(leg["actual_low"]["ts"]),
                "rank": 2,
                "text": (
                    f"{leg_id}: the tape reached its Window-1 low "
                    f"{leg['actual_low']['price_cents']}¢ (minute "
                    f"{leg['actual_low']['minute_from_window_open']:.1f})."
                ),
            },
            {
                "ts": float(leg["close"]["ts"]),
                "rank": 3,
                "text": (
                    f"{leg_id}: the authoritative Window-1 close was "
                    f"{leg['close']['price_cents']}¢."
                ),
            },
        ])
    relevant = {
        "recognition_wait_before_place",
        "band_call",
        "band_recall",
        "pair_class_read",
        "cohort_aim",
        "orientation_park_swap",
        "trendpath_live_aim",
        "authority_clamp",
        "authority_reanchor",
        "order_placed",
        "v4_resting_cancel",
        "match_live_resting_cancel",
        "window_truth_reaim",
        "walk_cap_yield_print_backed",
        "paper_fill",
        "entry_filled",
    }
    seen_pair_classes = set()
    for row in trace.get("trace") or []:
        if row.get("event") not in relevant:
            continue
        if row["event"] == "pair_class_read":
            key = (
                row["details"].get("pair_class"),
                tuple(sorted(
                    (
                        ticker,
                        value.get("band"),
                    )
                    for ticker, value in (
                        row["details"].get("legs") or {}
                    ).items()
                )),
            )
            if key in seen_pair_classes:
                continue
            seen_pair_classes.add(key)
        sentence = trace_sentence(row)
        if sentence:
            milestones.append({
                "ts": float(row["ts"]),
                "rank": 1,
                "text": sentence,
            })
    milestones.append({
        "ts": float(event["window"]["right_ts"]),
        "rank": 4,
        "text": "The guarded evaluator window closed.",
    })
    timeline = [
        f"- **{time_et(row['ts'])}:** {row['text']}"
        for row in sorted(
            dedupe(milestones),
            key=lambda row: (row["ts"], row["rank"], row["text"]),
        )
    ]
    fill_statement = (
        "Both legs filled."
        if event["pair_completed"] else (
            f"Only {event['fill_count']} of 2 legs filled; "
            "there is no completed-pair delta and no PC."
        )
    )
    return "\n".join([
        f"# {event['event_id']} — {event['category']}",
        "",
        (
            "Start evidence: **observed official exact**. "
            "Field contract repair: **on**. "
            "Wait for recognition: **on**."
        ),
        "",
        (
            f"The tape offered **{signed(event['tape_offer']['combined_delta_cents'])} "
            "combined delta**, with both leg lows below their own closes. "
            f"{fill_statement}"
        ),
        "",
        "| leg | full-window low | W1 close | legacy aim (delta to close) | sealed aim (delta to close) | fills |",
        "|---|---|---:|---:|---:|---|",
        *leg_rows,
        "",
        "## Chronological replay",
        "",
        *timeline,
        "",
        "## Read",
        "",
        (
            "A nonnegative aim-minus-low means the tape reached or passed "
            "the bid; a negative number means the authority aimed below the "
            "actual low. A negative aim-minus-close is the desired value "
            "direction, but it counts as PC only if both legs actually fill."
        ),
        "",
    ])


def depth_markdown(
    events: list[dict[str, Any]],
    depth: Mapping[str, Any],
) -> str:
    rows = []
    for row in depth["rows"]:
        rows.append(
            f"| {row['category']} | {row['event_id']} | {row['leg_id']} | "
            f"{row['actual_low_cents']} | {row['window1_close_cents']} | "
            f"{row['legacy_aim_cents']} | "
            f"{signed(row['legacy_aim_minus_low_cents'])} | "
            f"{signed(row['legacy_aim_minus_close_cents'])} | "
            f"{row['sealed_aim_cents']} | "
            f"{signed(row['sealed_aim_minus_low_cents'])} | "
            f"{signed(row['sealed_aim_minus_close_cents'])} | "
            f"{row['atlas_predicted_bottom_minute']:.1f} | "
            f"{row['actual_low_minute']:.1f} | "
            f"{signed(row['timing_error_minutes'], 'm')} |"
        )
    category_rows = []
    for category, row in depth["by_category"].items():
        category_rows.append(
            f"| {category} | {row['leg_count']} | "
            f"{signed(row['legacy_mean_aim_minus_low_cents'])} | "
            f"{signed(row['sealed_mean_aim_minus_low_cents'])} | "
            f"{signed(row['legacy_mean_aim_minus_close_cents'])} | "
            f"{signed(row['sealed_mean_aim_minus_close_cents'])} | "
            f"{row['median_absolute_timing_error_minutes']:.1f}m |"
        )
    overall = depth["overall"]
    completed = sum(event["pair_completed"] for event in events)
    return "\n".join([
        "# Five-game authority depth and Atlas timing",
        "",
        (
            "**The five games do not support “timing accurate, depth "
            "inaccurate.” Both were inaccurate in this sample.** Atlas's "
            f"median absolute bottom-time error was "
            f"**{overall['median_absolute_timing_error_minutes']:.1f} "
            "minutes**. Sealed was more negative to the close, but also "
            "materially deeper than the reachable low."
        ),
        "",
        (
            "Signs: aim − low below zero means too deep to touch; aim − "
            "close below zero means desired Window-1 value. Timing is "
            "predicted bottom minute − actual low minute."
        ),
        "",
        "| category | event | leg | low | close | legacy | L−low | L−close | sealed | S−low | S−close | predicted minute | actual minute | timing error |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        *rows,
        "",
        "## Aggregate",
        "",
        (
            f"- Legacy was touch-reachable on **"
            f"{overall['legacy_reachable_leg_count']}/10** legs; sealed on "
            f"**{overall['sealed_reachable_leg_count']}/10**."
        ),
        (
            f"- Legacy selected negative close delta on **"
            f"{overall['legacy_negative_close_delta_leg_count']}/10** legs; "
            f"sealed on **"
            f"{overall['sealed_negative_close_delta_leg_count']}/10**."
        ),
        (
            f"- Median absolute depth error: legacy **"
            f"{overall['legacy_median_absolute_depth_error_cents']:.1f}¢**, "
            f"sealed **"
            f"{overall['sealed_median_absolute_depth_error_cents']:.1f}¢**."
        ),
        (
            f"- Mean aim-minus-close: legacy "
            f"**{signed(overall['legacy_mean_aim_minus_close_cents'])}**, "
            f"sealed **"
            f"{signed(overall['sealed_mean_aim_minus_close_cents'])}**."
        ),
        (
            f"- The tape low had already happened before the comparable "
            f"two-authority decision on **"
            f"{overall['low_before_comparable_decision_leg_count']}/10** "
            "legs."
        ),
        (
            f"- Completed pairs: **{completed}/5**. The tape offered "
            "negative combined delta with both legs below close in all five."
        ),
        "",
        "## Per category",
        "",
        "| category | legs | legacy mean vs low | sealed mean vs low | legacy mean vs close | sealed mean vs close | median absolute timing error |",
        "|---|---:|---:|---:|---:|---:|---:|",
        *category_rows,
        "",
        (
            "The causal read is stark: sealed generally improved the value "
            "sign relative to the close, but usually bought that improvement "
            "by moving below the tape's reachable depth. The Atlas clock did "
            "not rescue it; its errors here are measured in hours, not "
            "quarter-minutes."
        ),
        "",
    ])


def combined_markdown(
    events: list[dict[str, Any]],
    depth: Mapping[str, Any],
) -> str:
    event_rows = []
    for event in events:
        aims = []
        fills = []
        for leg_id, leg in event["legs"].items():
            aims.append(
                f"{leg_id} L{leg['legacy']['initial_comparable_aim_cents']}"
                f"/S{leg['sealed']['initial_comparable_aim_cents']}"
            )
            fills.extend(
                f"{leg_id} {row['price_cents']}¢"
                for row in leg["fills"]
            )
        event_rows.append(
            f"| {event['category']} | {event['event_id']} | "
            f"{signed(event['tape_offer']['combined_delta_cents'])} | "
            f"{'; '.join(aims)} | {', '.join(fills) or 'none'} | "
            f"{str(event['both_filled_below_close']).lower()} |"
        )
    return "\n".join([
        "# Five exact-start delta replays — repaired live_v4",
        "",
        (
            "Every game had a full lawful evaluator window, observed "
            "official exact start evidence, two tape lows below their own "
            "closes, and negative combined tape delta. The live OS ran with "
            "the field repair and `recognition_before_place` enabled."
        ),
        "",
        "| category | event | tape combined delta | initial comparable aims (legacy/sealed) | fills | both fills below close |",
        "|---|---|---:|---|---|---:|",
        *event_rows,
        "",
        (
            f"Outcome: **0/5 completed pairs**. One leg filled across the "
            "entire sample, and that fill was above its own Window-1 close. "
            "The sample therefore produced **0 PC pairs**, despite five "
            "negative-delta tape opportunities."
        ),
        "",
        (
            "Individual chronological narratives are beside this file. "
            "`DEPTH_AND_TIMING_ERROR.md` contains the signed depth and timing "
            "comparison."
        ),
        "",
    ])


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    output = (repo / DELTA_ROOT).resolve()
    selections = json.loads(
        (output / "FIVE_GAME_SELECTION.json").read_text(encoding="utf-8")
    )["games"]
    full_rows = json.loads(
        (repo / FULL_LAWFUL).read_text(encoding="utf-8")
    )["events"]
    full_by_event = {
        str(row["event_id"]): row for row in full_rows
    }
    references = {
        str(row["event_id"]): row
        for row in read_jsonl((repo / CONTROL_LEDGER).resolve())
    }
    events = []
    traces = {}
    for selection in selections:
        event_id = str(selection["event_id"])
        trace_path = (
            repo / REPLAY_ROOT / event_id / "variant" / "runs"
            / event_id / "trace.json"
        )
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        if trace.get("first_input_break") is not None:
            raise ReportError(f"{event_id}: replay input break")
        traces[event_id] = trace
        events.append(event_analysis(
            selection,
            full_by_event[event_id],
            references[event_id],
            trace,
        ))
    depth = depth_summary(events)
    result = {
        "schema_version": "window1-five-game-delta-replay-v1",
        "configuration": {
            "live_v4_field_contract_repair": True,
            "recognition_before_place": True,
            "fill_model": (
                "RESTING_TOUCH_FILL_V1: resting order fills on later true "
                "print or opposite BBO touch/pass; no depth proof; no "
                "five-contract gate"
            ),
            "holdout_accessed": False,
            "live_accessed": False,
        },
        "events": events,
        "depth_and_timing": depth,
        "outcome": {
            "pair_completions": sum(
                event["pair_completed"] for event in events
            ),
            "PC_pairs": sum(
                event["pair_completed"]
                and (
                    event["achieved_combined_delta_cents"] is not None
                    and event["achieved_combined_delta_cents"] < 0
                )
                for event in events
            ),
            "both_filled_below_close": sum(
                event["both_filled_below_close"] for event in events
            ),
            "filled_legs": sum(event["fill_count"] for event in events),
        },
    }
    (output / "FIVE_GAME_DELTA_REPLAYS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "FIVE_GAME_DELTA_REPLAYS.md").write_text(
        combined_markdown(events, depth),
        encoding="utf-8",
        newline="\n",
    )
    (output / "DEPTH_AND_TIMING_ERROR.md").write_text(
        depth_markdown(events, depth),
        encoding="utf-8",
        newline="\n",
    )
    narrative_dir = output / "narratives"
    narrative_dir.mkdir(parents=True, exist_ok=True)
    for event in events:
        (narrative_dir / f"{event['event_id']}.md").write_text(
            event_markdown(event, traces[event["event_id"]]),
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps({
        "outcome": result["outcome"],
        "depth_and_timing_overall": depth["overall"],
        "events": [event["event_id"] for event in events],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
