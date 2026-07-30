#!/usr/bin/env python3
"""Fit Window-1 low timing/depth on actual-bell games only."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import json
from pathlib import Path
import statistics
from typing import Iterable

from window1_live_v4_replay import build_print_index, load_print_block


DEFAULT_EVENTS = Path(r"C:\Users\omigr\OMI-Window1-private\joined\events.jsonl")
DEFAULT_PRINTS = Path(
    r"C:\Users\omigr\OMI-Window1-private\fit-local\prints.jsonl"
)
DEFAULT_PRINT_INDEX = Path(
    r"C:\tmp\window1-actual-bell-refit\prints_by_ticker.json"
)
DEFAULT_SHADOW = Path(
    r"C:\Users\omigr\OMI-Window1-private"
    r"\start-recovery-v2\milestone_shadow.remote.jsonl"
)
STARTS = Path(
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
FULL = Path(
    ".claude/window1_t2_iteration_history/WINDOW1_FULL_LAWFUL_CEILING.json"
)
DEFAULT_OUT = Path(
    ".claude/window1_live_v4_replay/actual_bell_refit_20260729"
)
THIN_N = 20


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def epoch(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def q(values: Iterable[float], fraction: float) -> float | None:
    rows = sorted(float(value) for value in values)
    if not rows:
        return None
    index = min(len(rows) - 1, max(0, int(len(rows) * fraction)))
    return rows[index]


def distribution(values: Iterable[float]) -> dict:
    rows = [float(value) for value in values]
    return {
        "n": len(rows),
        "min": min(rows) if rows else None,
        "p10": q(rows, 0.10),
        "p25": q(rows, 0.25),
        "median": statistics.median(rows) if rows else None,
        "p75": q(rows, 0.75),
        "p90": q(rows, 0.90),
        "max": max(rows) if rows else None,
    }


def pcell(price: float) -> str:
    return (
        "le25"
        if price <= 25
        else "26_50"
        if price <= 50
        else "51_75"
        if price <= 75
        else "ge75"
    )


def summarize(rows: list[dict], key: str) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    result = {}
    for name, members in sorted(groups.items()):
        games = {row["event_id"] for row in members}
        result[name] = {
            "n_legs": len(members),
            "n_games": len(games),
            "fit_status": (
                "FIT" if len(members) >= THIN_N else "TOO_FEW_EXACT_BELLS"
            ),
            "thin_threshold_n_legs": THIN_N,
            "low_arrival_tminus_actual_bell_minutes": distribution(
                row["low_tminus_actual_bell_minutes"] for row in members
            ),
            "dip_depth_cents_below_window1_close": distribution(
                row["depth_below_window1_close_cents"] for row in members
            ),
        }
    return result


def recency_bucket(minutes: float) -> str:
    if minutes < 0:
        return "observed_after_scheduled_time"
    if minutes <= 60:
        return "within_1h"
    if minutes <= 360:
        return "1_to_6h"
    if minutes <= 1440:
        return "6_to_24h"
    if minutes <= 4320:
        return "1_to_3d"
    return "over_3d"


def round_floats(value):
    if isinstance(value, float):
        return round(value, 3)
    if isinstance(value, list):
        return [round_floats(item) for item in value]
    if isinstance(value, dict):
        return {key: round_floats(item) for key, item in value.items()}
    return value


def shadow_census(path: Path, event_ids: set[str]) -> dict:
    if not path.exists():
        return {
            "present": False,
            "conclusion": "no historical shadow log is available",
        }
    parsed = []
    parse_failures = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                parsed.append(json.loads(line))
            except json.JSONDecodeError:
                parse_failures += 1
    rows = [
        row for row in parsed
        if str(row.get("event") or "") in event_ids
    ]
    by_event = defaultdict(list)
    for row in rows:
        by_event[str(row["event"])].append(row)
    with_schedule = {
        event: sorted(
            members, key=lambda row: float(row.get("ts") or 0)
        )
        for event, members in by_event.items()
        if any(row.get("sched_ep") is not None for row in members)
    }
    distinct = {}
    transitions = {}
    for event, members in with_schedule.items():
        states = [
            float(row["sched_ep"])
            for row in members
            if row.get("sched_ep") is not None
        ]
        unique = []
        for state in states:
            if not unique or state != unique[-1]:
                unique.append(state)
        distinct[event] = len(set(states))
        transitions[event] = max(0, len(unique) - 1)
    return {
        "present": True,
        "path": str(path),
        "rows_for_804": len(rows),
        "malformed_rows_excluded": parse_failures,
        "events_for_804": len(by_event),
        "events_with_any_sched_ep": len(with_schedule),
        "events_with_multiple_distinct_sched_ep": sum(
            count > 1 for count in distinct.values()
        ),
        "observed_sched_ep_transitions": sum(transitions.values()),
        "coverage_fraction_of_804": len(with_schedule) / 804.0,
        "conclusion": (
            "The shadow can recover the sampled sched_ep states and observed "
            "changes counted here. It cannot prove the first state, the last "
            "state, or revisions between polls, so it is not a complete "
            "revision history."
        ),
    }


def build(args: argparse.Namespace) -> dict:
    repo = args.repo.resolve()
    starts = {
        row["event_id"]: row
        for row in read_jsonl(repo / STARTS)
        if row.get("start_source_class") == "official_exact"
    }
    if len(starts) != 234:
        raise RuntimeError(f"expected 234 exact-bell games, found {len(starts)}")
    full = {
        row["event_id"]: row
        for row in json.loads((repo / FULL).read_text(encoding="utf-8"))[
            "events"
        ]
    }
    events = {
        row["event_id"]: row for row in read_jsonl(args.events)
    }
    print_ranges = build_print_index(args.prints, args.print_index)

    legs = []
    skipped = []
    event_clock_rows = []
    for event_id, start in sorted(starts.items()):
        lawful = full[event_id]
        catalog = events[event_id]
        bell = epoch(start["exact_start_utc"])
        schedule = epoch(catalog["scheduled_start_exchange_ts"])
        observed = epoch(catalog["schedule_observed_exchange_ts"])
        selected_left = float(lawful["selected_left_ts"])
        # Once the target is actual-bell anchored, its Window 1 is the eight
        # hours before that bell.  Reusing schedule-minus-eight here would
        # reintroduce the same moving-zero defect and allow T-minus > 480.
        left = bell - 8 * 3600
        right = float(lawful["evaluator_right_ts"])
        if bell is None or schedule is None or observed is None:
            raise RuntimeError(f"missing clock on exact event {event_id}")
        event_clock_rows.append({
            "event_id": event_id,
            "category": start["category"],
            "actual_bell_minus_schedule_minutes": (bell - schedule) / 60.0,
            "snapshot_observed_minutes_before_schedule": (
                schedule - observed
            ) / 60.0,
            "snapshot_recency_bucket": recency_bucket(
                (schedule - observed) / 60.0
            ),
        })

        for leg in catalog["legs"]:
            ticker = str(leg["ticker"])
            prints, _prior = load_print_block(
                ticker, print_ranges, left, right
            )
            if not prints:
                skipped.append({
                    "event_id": event_id,
                    "leg_id": leg["leg"],
                    "reason": "no_true_print_inside_actual_bell_window",
                })
                continue
            low_price = min(row["price"] for row in prints)
            low = next(row for row in prints if row["price"] == low_price)
            close = prints[-1]
            first_hour_right = prints[0]["ts"] + 3600
            first_hour = [
                row for row in prints if row["ts"] < first_hour_right
            ]
            discovery = statistics.median(
                row["price"] for row in first_hour
            )
            role = "leader" if discovery >= 50 else "underdog"
            bucket = pcell(discovery)
            legs.append({
                "event_id": event_id,
                "category": start["category"],
                "leg_id": str(leg["leg"]),
                "ticker": ticker,
                "exact_bell_ts": bell,
                "window_left_ts": left,
                "original_schedule_anchored_left_ts": selected_left,
                "guarded_right_ts": right,
                "open_price_cents": prints[0]["price"],
                "low_price_cents": low_price,
                "low_ts": low["ts"],
                "close_price_cents": close["price"],
                "close_ts": close["ts"],
                "low_tminus_actual_bell_minutes": (bell - low["ts"]) / 60.0,
                "depth_below_window1_close_cents": (
                    close["price"] - low_price
                ),
                "discovery_first_hour_median_cents": discovery,
                "first_hour_volume": sum(row["size"] for row in first_hour),
                "pcell": bucket,
                "role": role,
                "atlas_cell": "|".join(
                    (start["category"], role, bucket)
                ),
            })

    # Refit volume terciles on exact-bell legs only; no legacy cohort cut is
    # carried into the new target.
    volume_cuts = {}
    for category in sorted({row["category"] for row in legs}):
        values = sorted(
            row["first_hour_volume"]
            for row in legs
            if row["category"] == category
        )
        volume_cuts[category] = {
            "low_mid_cut": q(values, 1 / 3),
            "mid_high_cut": q(values, 2 / 3),
            "n_legs": len(values),
        }
    for row in legs:
        cuts = volume_cuts[row["category"]]
        volume_band = (
            "lo"
            if row["first_hour_volume"] <= cuts["low_mid_cut"]
            else "mid"
            if row["first_hour_volume"] <= cuts["mid_high_cut"]
            else "hi"
        )
        row["volume_band_exact_fit"] = volume_band
        row["cohort_cell"] = "|".join(
            (row["category"], row["pcell"], volume_band)
        )

    slip_by_category = summarize_clock(event_clock_rows, "category")
    slip_by_recency = summarize_clock(
        event_clock_rows, "category_and_snapshot_recency"
    )
    result = {
        "schema_version": "window1-actual-bell-refit-v1",
        "target_contract": {
            "fit_population": "official_exact actual-bell games only",
            "exact_games": len(starts),
            "proxy_clock_games_blended": 0,
            "timing_axis": "T-minus actual bell",
            "depth_axis": "cents below last true print in full lawful Window 1",
            "window_definition": (
                "actual bell minus eight hours through actual bell minus the "
                "frozen negative guard"
            ),
            "minus_0k_onset_target": "DROPPED",
            "low_definition": (
                "earliest true print at the minimum price between selected "
                "actual-bell-minus-eight-hours and exact bell minus its "
                "frozen guard"
            ),
            "tape_source": str(args.prints),
        },
        "coverage": {
            "exact_games_requested": len(starts),
            "leg_rows_fitted": len(legs),
            "skipped_rows": skipped,
        },
        "volume_cuts_refit_on_exact_population": volume_cuts,
        "by_category": summarize(legs, "category"),
        "by_atlas_cell": summarize(legs, "atlas_cell"),
        "by_cohort_cell": summarize(legs, "cohort_cell"),
        "leg_rows": legs,
        "schedule_bridge": {
            "true_schedule_revision_recency_available": False,
            "why": (
                "joined/events.jsonl retains one catalog occurrence value and "
                "the time that snapshot was observed; it does not retain the "
                "exchange's schedule-field update timestamp or revision chain"
            ),
            "proxy_reported_instead": (
                "snapshot observation lead to scheduled start; this is not "
                "called schedule-update recency"
            ),
            "formula": (
                "live Tminus schedule target = fitted Tminus actual bell "
                "- forecast(actual bell - current schedule)"
            ),
            "by_category": slip_by_category,
            "by_category_and_snapshot_recency": slip_by_recency,
            "tradeability": {
                category: {
                    "schedule_only_timing_tradeable": (
                        row["p90_minus_p10_minutes"] <= 120
                    ),
                    "reason": (
                        "p10-to-p90 schedule-slip span is "
                        f"{row['p90_minus_p10_minutes']:.1f} minutes"
                    ),
                }
                for category, row in slip_by_category.items()
            },
        },
        "shadow_revision_recovery": shadow_census(
            args.shadow, set(full)
        ),
        "forward_revision_capture": {
            "required": [
                "append one immutable row on every catalog poll per event",
                "store observed_at, market/event id, occurrence_datetime, "
                "open_time, expected_expiration_time, status and raw payload hash",
                "emit a change row whenever any schedule field differs from "
                "the previous observed row",
                "never overwrite history; retain source response and poll errors",
                "join every live decision to the latest revision visible at "
                "that decision timestamp",
            ],
            "service_change_required_now": False,
            "vps_written": False,
        },
    }
    return round_floats(result)


def summarize_clock(rows: list[dict], mode: str) -> dict:
    groups = defaultdict(list)
    for row in rows:
        key = (
            row["category"]
            if mode == "category"
            else "|".join(
                (row["category"], row["snapshot_recency_bucket"])
            )
        )
        groups[key].append(row["actual_bell_minus_schedule_minutes"])
    result = {}
    for key, values in sorted(groups.items()):
        dist = distribution(values)
        result[key] = {
            **dist,
            "p90_minus_p10_minutes": dist["p90"] - dist["p10"],
            "bell_earlier_count": sum(value < 0 for value in values),
            "bell_equal_count": sum(value == 0 for value in values),
            "bell_later_count": sum(value > 0 for value in values),
        }
    return result


def fmt_tminus(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"T-{value:.1f}" if value >= 0 else f"T+{abs(value):.1f}"


def render(result: dict) -> str:
    lines = [
        "# Actual-bell Window-1 timing/depth refit",
        "",
        "**Fit population: 234 exact-bell games only. Proxy-clock games: "
        "zero. The -0k onset target is dropped.**",
        "",
        "Timing is T-minus actual bell. Depth is the true-print low relative "
        "to the last true print inside the full lawful window. A granular "
        "cell with fewer than 20 exact-bell legs is descriptive only.",
        "",
        "## Category fits",
        "",
        "| Category | n legs | Low T-minus bell p25 / median / p75 | "
        "Depth below W1 close p25 / median / p75 |",
        "|---|---:|---:|---:|",
    ]
    for key, row in result["by_category"].items():
        timing = row["low_arrival_tminus_actual_bell_minutes"]
        depth = row["dip_depth_cents_below_window1_close"]
        lines.append(
            f"| {key} | {row['n_legs']} | "
            f"{fmt_tminus(timing['p25'])} / "
            f"{fmt_tminus(timing['median'])} / "
            f"{fmt_tminus(timing['p75'])} | "
            f"{depth['p25']:.1f}c / {depth['median']:.1f}c / "
            f"{depth['p75']:.1f}c |"
        )
    lines += [
        "",
        "## Exact-bell cohort cells",
        "",
        "| Cell | n | status | low median | depth median |",
        "|---|---:|---|---:|---:|",
    ]
    for key, row in result["by_cohort_cell"].items():
        timing = row["low_arrival_tminus_actual_bell_minutes"]
        depth = row["dip_depth_cents_below_window1_close"]
        lines.append(
            f"| {key} | {row['n_legs']} | {row['fit_status']} | "
            f"{fmt_tminus(timing['median'])} | {depth['median']:.1f}c |"
        )
    lines += [
        "",
        "## Schedule-to-bell bridge",
        "",
        "The archive does **not** contain schedule-update recency. It contains "
        "one schedule snapshot and when that snapshot was observed. The "
        "conditioned table below uses that observation lead only and does "
        "not relabel it as an update timestamp.",
        "",
        "| Category | n | median bell-schedule | p10 | p90 | span | "
        "schedule-only timing? |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for key, row in result["schedule_bridge"]["by_category"].items():
        trade = result["schedule_bridge"]["tradeability"][key]
        lines.append(
            f"| {key} | {row['n']} | {row['median']:+.1f}m | "
            f"{row['p10']:+.1f}m | {row['p90']:+.1f}m | "
            f"{row['p90_minus_p10_minutes']:.1f}m | "
            f"{'yes' if trade['schedule_only_timing_tradeable'] else 'no'} |"
        )
    shadow = result["shadow_revision_recovery"]
    lines += [
        "",
        "### Conditioned on snapshot observation lead (not update recency)",
        "",
        "| Category / observation bucket | n | median | p10 | p90 | span |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, row in result["schedule_bridge"][
        "by_category_and_snapshot_recency"
    ].items():
        lines.append(
            f"| {key} | {row['n']} | {row['median']:+.1f}m | "
            f"{row['p10']:+.1f}m | {row['p90']:+.1f}m | "
            f"{row['p90_minus_p10_minutes']:.1f}m |"
        )
    lines += [
        "",
        "ATP Main is not timing-tradeable from the retained schedule alone "
        "if its reported p10-to-p90 span remains this wide. A +30-minute "
        "median does not rescue a multi-day upper tail.",
        "",
        "## Revision history",
        "",
        f"Shadow rows cover {shadow.get('events_with_any_sched_ep', 0)}/804 "
        "events with any sampled schedule value and show "
        f"{shadow.get('observed_sched_ep_transitions', 0)} observed changes. "
        f"{shadow.get('conclusion')}",
        "",
        "Going forward, capture every catalog poll as an append-only revision "
        "row, hash the raw response, emit explicit field-change rows, and join "
        "each decision to the latest revision visible at that decision time.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--prints", type=Path, default=DEFAULT_PRINTS)
    parser.add_argument(
        "--print-index", type=Path, default=DEFAULT_PRINT_INDEX
    )
    parser.add_argument("--shadow", type=Path, default=DEFAULT_SHADOW)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build(args)
    out = (args.repo / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "ACTUAL_BELL_REFIT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out / "ACTUAL_BELL_REFIT.md").write_text(
        render(result), encoding="utf-8"
    )
    print(json.dumps({
        "exact_games": result["target_contract"]["exact_games"],
        "leg_rows": result["coverage"]["leg_rows_fitted"],
        "category_fits": {
            key: {
                "n": row["n_legs"],
                "tminus_median": row[
                    "low_arrival_tminus_actual_bell_minutes"
                ]["median"],
                "depth_median": row[
                    "dip_depth_cents_below_window1_close"
                ]["median"],
            }
            for key, row in result["by_category"].items()
        },
        "shadow": result["shadow_revision_recovery"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
