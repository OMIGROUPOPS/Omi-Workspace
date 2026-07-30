#!/usr/bin/env python3
"""Audit Window-1 timing coordinates without changing any OS dial.

The live Atlas stores a lead time to a fitted, volume-derived ``-0k`` onset.
This audit keeps that coordinate distinct from:

* the exchange schedule used to open policy Window 1,
* the selected exact/guarded start evidence used by the evaluator, and
* the policy window's left edge.

It also reports the exact-start schedule-slip distribution needed to bridge a
bell-fitted surface into a live system that initially knows only a schedule.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import json
from pathlib import Path
import statistics
import subprocess
from typing import Any, Iterable, Mapping


FULL_LAWFUL = (
    ".claude/window1_t2_iteration_history/"
    "WINDOW1_FULL_LAWFUL_CEILING.json"
)
FIVE_REPORT = (
    ".claude/window1_live_v4_replay/delta_objective_20260729/"
    "FIVE_GAME_DELTA_REPLAYS.json"
)
START_LEDGER = (
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
EVENTS = r"C:\Users\omigr\OMI-Window1-private\joined\events.jsonl"
CACHE_ROOT = (
    r"C:\Users\omigr\OMI-Window1-private\fit-local\guarded-cache-v3"
)
ATLAS = (
    ".claude/window1_live_v4_replay/vps_inputs_20260729/"
    "trendpath/ATLAS_V1.json"
)
LIBRARY = (
    ".claude/window1_live_v4_replay/vps_inputs_20260729/"
    "trendpath/LIBRARY_V1.json"
)
OUTPUT = (
    ".claude/window1_live_v4_replay/"
    "timing_anchor_20260729"
)


class TimingAuditError(RuntimeError):
    """An input contract failed to reconcile."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TimingAuditError(
                    f"object required: {path}:{line_number}"
                )
            rows.append(value)
    return rows


def epoch(value: str | int | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def quantile(values: Iterable[float], fraction: float) -> float | None:
    rows = sorted(float(value) for value in values)
    if not rows:
        return None
    return rows[min(len(rows) - 1, int(len(rows) * fraction))]


def distribution(values: Iterable[float]) -> dict[str, float | int | None]:
    rows = [float(value) for value in values]
    return {
        "count": len(rows),
        "min": min(rows) if rows else None,
        "p10": quantile(rows, 0.10),
        "median": statistics.median(rows) if rows else None,
        "mean": statistics.mean(rows) if rows else None,
        "p90": quantile(rows, 0.90),
        "max": max(rows) if rows else None,
    }


def onset_of(volume_minutes: Mapping[int, int]) -> int | None:
    """Literal copy of trendpath_build.py's -0k onset law."""
    keys = sorted(volume_minutes)
    if not keys:
        return None
    base60 = sum(
        volume_minutes[minute]
        for minute in keys
        if minute < keys[0] + 3600
    )
    need = max(8, 3.0 * base60 / 4.0)
    for minute in keys:
        trailing = sum(
            volume_minutes.get(key, 0)
            for key in range(minute - 14 * 60, minute + 60, 60)
        )
        active = sum(
            1
            for key in range(minute - 14 * 60, minute + 60, 60)
            if key in volume_minutes
        )
        forward = sum(
            volume_minutes.get(key, 0)
            for key in range(minute + 60, minute + 31 * 60, 60)
        )
        if active >= 5 and trailing >= need and forward >= need:
            return minute
    return None


def replay_onsets(cache_path: Path) -> dict[str, int | None]:
    with gzip.open(cache_path, "rt", encoding="utf-8") as handle:
        event = json.load(handle)
    result = {}
    for leg in event["legs"]:
        per_minute: dict[int, float] = defaultdict(float)
        for trade in leg.get("prints") or []:
            minute = int(float(trade["ts"]) // 60) * 60
            per_minute[minute] += float(trade.get("size") or 0)
        volume = {
            minute: max(1, int(size))
            for minute, size in per_minute.items()
            if size
        }
        result[str(leg["leg"])] = onset_of(volume)
    return result


def git_fact(repo: Path, commit: str) -> dict[str, str]:
    output = subprocess.check_output(
        [
            "git",
            "show",
            "-s",
            "--date=iso-strict",
            "--format=%H%n%ad%n%s",
            commit,
        ],
        cwd=repo,
        text=True,
        encoding="utf-8",
    ).splitlines()
    return {"commit": output[0], "date": output[1], "subject": output[2]}


def round_numbers(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 3)
    if isinstance(value, list):
        return [round_numbers(item) for item in value]
    if isinstance(value, dict):
        return {key: round_numbers(item) for key, item in value.items()}
    return value


def signed(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value > 0:
        return f"+{value:.1f}"
    if value < 0:
        return f"−{abs(value):.1f}"
    return "0.0"


def t_label(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 0:
        return f"T−{value:.1f}"
    return f"T+{abs(value):.1f}"


def build(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.resolve()
    full = read_json(repo / args.full_lawful)
    five = read_json(repo / args.five_report)
    starts = {
        str(row["event_id"]): row
        for row in read_jsonl(repo / args.start_ledger)
    }
    events = {
        str(row["event_id"]): row
        for row in read_jsonl(args.events)
    }
    full_by_event = {
        str(row["event_id"]): row for row in full["events"]
    }
    atlas = read_json(repo / args.atlas)
    library = read_json(repo / args.library)

    five_rows = []
    event_rows = []
    for event in five["events"]:
        event_id = str(event["event_id"])
        start = starts[event_id]
        catalog = events[event_id]
        lawful = full_by_event[event_id]
        schedule_ts = epoch(catalog["scheduled_start_exchange_ts"])
        bell_ts = epoch(start["exact_start_utc"])
        cutoff_ts = float(lawful["evaluator_right_ts"])
        left_ts = float(lawful["selected_left_ts"])
        if schedule_ts is None or bell_ts is None:
            raise TimingAuditError(
                f"five-game exact row lacks schedule/bell: {event_id}"
            )
        guard_seconds = float(
            (start.get("guard_band") or {}).get(
                "negative_guard_seconds", 0
            )
        )
        if abs((bell_ts - guard_seconds) - cutoff_ts) > 1e-6:
            raise TimingAuditError(
                f"guarded cutoff does not derive from exact bell: {event_id}"
            )
        onsets = replay_onsets(
            args.cache_root / f"{event_id}.json.gz"
        )
        event_rows.append({
            "event_id": event_id,
            "category": event["category"],
            "scheduled_start_ts": schedule_ts,
            "exact_bell_ts": bell_ts,
            "guarded_cutoff_ts": cutoff_ts,
            "window_left_ts": left_ts,
            "bell_minus_schedule_minutes": (
                bell_ts - schedule_ts
            ) / 60.0,
            "guard_seconds": guard_seconds,
            "selected_start_source": start["selected_source"],
            "selected_start_source_family": (
                start["selected_source_family"]
            ),
        })
        for prop in event["legs"].items():
            leg_id, leg = prop
            low_ts = float(leg["actual_low"]["ts"])
            atlas_lead = float(
                leg["atlas"]["predicted_bottom_minute"]
            )
            onset_ts = onsets.get(leg_id)
            actual_tminus_schedule = (schedule_ts - low_ts) / 60.0
            actual_tminus_bell = (bell_ts - low_ts) / 60.0
            actual_from_left = (low_ts - left_ts) / 60.0

            # These are deliberately three different anchor hypotheses.
            # Error is predicted wall-clock time minus actual wall-clock
            # time: positive = predicted later; negative = predicted earlier.
            schedule_error = actual_tminus_schedule - atlas_lead
            bell_error = actual_tminus_bell - atlas_lead
            left_error = atlas_lead - actual_from_left
            onset_lead = (
                (float(onset_ts) - low_ts) / 60.0
                if onset_ts is not None else None
            )
            onset_error = (
                onset_lead - atlas_lead
                if onset_lead is not None else None
            )
            native_comparable = (
                onset_lead is not None and onset_lead > 0
            )
            five_rows.append({
                "event_id": event_id,
                "category": event["category"],
                "leg_id": leg_id,
                "atlas_page": leg["atlas"]["page"],
                "atlas_stored_lead_minutes_before_minus_0k_onset": (
                    atlas_lead
                ),
                "actual_low_ts": low_ts,
                "actual_low_tminus_scheduled_start_minutes": (
                    actual_tminus_schedule
                ),
                "actual_low_tminus_exact_bell_minutes": (
                    actual_tminus_bell
                ),
                "actual_low_minutes_from_window_left": actual_from_left,
                "schedule_anchor_hypothesis_error_minutes": (
                    schedule_error
                ),
                "exact_bell_anchor_hypothesis_error_minutes": bell_error,
                "window_left_anchor_hypothesis_error_minutes": left_error,
                "reconstructed_minus_0k_onset_ts": onset_ts,
                "actual_low_tminus_reconstructed_minus_0k_minutes": (
                    onset_lead
                ),
                "native_minus_0k_axis_error_minutes": onset_error,
                "native_axis_low_is_pre_onset": native_comparable,
                "native_axis_error_is_target_comparable": native_comparable,
            })

    official = []
    source_counts = Counter()
    family_counts = Counter()
    for event_id, start in starts.items():
        if start.get("start_source_class") != "official_exact":
            continue
        catalog = events.get(event_id)
        if not catalog:
            raise TimingAuditError(
                f"official exact event absent from joined schedule: {event_id}"
            )
        schedule_ts = epoch(catalog["scheduled_start_exchange_ts"])
        bell_ts = epoch(start["exact_start_utc"])
        if schedule_ts is None or bell_ts is None:
            raise TimingAuditError(
                f"official exact event lacks schedule/bell: {event_id}"
            )
        slip = (bell_ts - schedule_ts) / 60.0
        official.append({
            "event_id": event_id,
            "category": start["category"],
            "schedule_ts": schedule_ts,
            "bell_ts": bell_ts,
            "bell_minus_schedule_minutes": slip,
            "selected_source": start["selected_source"],
            "selected_source_family": start["selected_source_family"],
        })
        source_counts[str(start["selected_source"])] += 1
        family_counts[str(start["selected_source_family"])] += 1
    if len(official) != 234:
        raise TimingAuditError(
            f"expected 234 official exact rows, got {len(official)}"
        )
    by_category = {}
    for category in sorted({row["category"] for row in official}):
        rows = [
            row["bell_minus_schedule_minutes"]
            for row in official
            if row["category"] == category
        ]
        by_category[category] = {
            **distribution(rows),
            "bell_earlier_than_schedule_count": sum(v < 0 for v in rows),
            "bell_equal_schedule_count": sum(v == 0 for v in rows),
            "bell_later_than_schedule_count": sum(v > 0 for v in rows),
            "live_bridge": {
                "formula": (
                    "predicted_Tminus_schedule = "
                    "fitted_Tminus_actual_bell - forecast_bell_slip"
                ),
                "median_slip_minutes_for_category": (
                    statistics.median(rows)
                ),
                "warning": (
                    "median-only translation discards the reported "
                    "slip distribution and is not a deterministic bell"
                ),
            },
        }

    atlas_pages = [
        page for page in atlas["pages"].values()
        if page.get("verdict") == "PATH"
    ]
    atlas_by_brand = {}
    for brand in sorted({page.get("branded") for page in atlas_pages}):
        pages = [
            page for page in atlas_pages if page.get("branded") == brand
        ]
        atlas_by_brand[str(brand)] = {
            "path_page_count": len(pages),
            "timing_gun_present_count": sum(
                page.get("timing_gun") is not None for page in pages
            ),
        }
    selected_categories = {
        "ATP_CHALL", "ATP_MAIN", "WTA_CHALL", "WTA_MAIN"
    }
    selected_library_cells = [
        value
        for key, value in library["cells"].items()
        if key.split("|", 1)[0] in selected_categories
    ]

    hypothesis_abs = {
        "schedule": distribution(
            abs(row["schedule_anchor_hypothesis_error_minutes"])
            for row in five_rows
        ),
        "exact_bell": distribution(
            abs(row["exact_bell_anchor_hypothesis_error_minutes"])
            for row in five_rows
        ),
        "window_left": distribution(
            abs(row["window_left_anchor_hypothesis_error_minutes"])
            for row in five_rows
        ),
        "native_minus_0k": distribution(
            abs(row["native_minus_0k_axis_error_minutes"])
            for row in five_rows
            if row["native_axis_error_is_target_comparable"]
        ),
    }

    result = {
        "schema_version": "window1-timing-anchor-audit-v1",
        "ruling": {
            "prior_five_game_timing_table_valid": False,
            "why": (
                "it treated Atlas bottom_t_med_min as minutes from the "
                "policy-window left edge; the stored variable is minutes "
                "before a volume-derived -0k onset"
            ),
            "atlas_timing_surface_survives_as_actual_bell_fit": False,
            "depth_calibration_run": False,
            "depth_calibration_hold_reason": (
                "operator required timing to survive first; no selected "
                "tour Atlas page or selected-category cohort cell has a "
                "bell/evidence-gun timing fit"
            ),
            "five_leg_native_target_comparable_count": sum(
                row["native_axis_error_is_target_comparable"]
                for row in five_rows
            ),
            "five_leg_full_window_low_after_native_onset_count": sum(
                row["reconstructed_minus_0k_onset_ts"] is not None
                and not row["native_axis_low_is_pre_onset"]
                for row in five_rows
            ),
            "five_leg_native_onset_unresolved_count": sum(
                row["reconstructed_minus_0k_onset_ts"] is None
                for row in five_rows
            ),
        },
        "coordinate_contract": {
            "atlas_stored_axis": (
                "minutes before per-leg -0k flow-step onset"
            ),
            "atlas_is_window_fraction": False,
            "atlas_is_minutes_from_window_left": False,
            "atlas_is_tminus_scheduled_start": False,
            "live_v4_consumer_defect": (
                "dip_timing subtracts bottom_t_med_min from schedule/honest "
                "tts_min, and shadow_range_shape selects an onset-axis path "
                "slice using schedule/honest tts_min"
            ),
            "signed_error_convention": (
                "predicted wall-clock low minus actual wall-clock low; "
                "positive means predicted late, negative means predicted early"
            ),
        },
        "lineage": {
            "atlas_introduced": git_fact(repo, "7338fef7"),
            "cohort_timing_introduced": git_fact(repo, "ebdb03c9"),
            "evidence_gun_recut": git_fact(repo, "c070a158"),
            "honest_clock_history_restamp": git_fact(repo, "dea47904"),
            "classification": (
                "Atlas and cohort target variables predate the corpus-wide "
                "honest-clock migration; later rebuilds preserved the same "
                "-0k target"
            ),
        },
        "surface_census": {
            "atlas": {
                "path_page_count": len(atlas_pages),
                "timing_gun_present_count": sum(
                    page.get("timing_gun") is not None
                    for page in atlas_pages
                ),
                "by_brand": atlas_by_brand,
                "five_game_page_count": len({
                    row["atlas_page"] for row in five_rows
                }),
                "five_game_timing_gun_present_count": sum(
                    atlas["pages"][row["atlas_page"]].get("timing_gun")
                    is not None
                    for row in {
                        row["atlas_page"]: row for row in five_rows
                    }.values()
                ),
            },
            "library": {
                "selected_category_cell_count": len(
                    selected_library_cells
                ),
                "selected_category_gun_axis_present_count": sum(
                    cell.get("gun_axis") is not None
                    for cell in selected_library_cells
                ),
                "metadata_timing_axis": library["meta"]["timing_axis"],
                "metadata_tts_axis": library["meta"]["tts_axis"],
            },
        },
        "five_game_events": event_rows,
        "five_game_timing_rows": five_rows,
        "five_game_anchor_hypothesis_absolute_error_minutes": hypothesis_abs,
        "official_exact_schedule_to_bell": {
            "all": {
                **distribution(
                    row["bell_minus_schedule_minutes"]
                    for row in official
                ),
                "bell_earlier_than_schedule_count": sum(
                    row["bell_minus_schedule_minutes"] < 0
                    for row in official
                ),
                "bell_equal_schedule_count": sum(
                    row["bell_minus_schedule_minutes"] == 0
                    for row in official
                ),
                "bell_later_than_schedule_count": sum(
                    row["bell_minus_schedule_minutes"] > 0
                    for row in official
                ),
            },
            "by_category": by_category,
            "selected_source_counts": dict(sorted(source_counts.items())),
            "selected_source_family_counts": dict(
                sorted(family_counts.items())
            ),
            "rows": official,
        },
        "stored_clock_fields": {
            "joined_event_schedule": {
                "fields": [
                    "scheduled_start_exchange_ts",
                    "schedule_observed_exchange_ts",
                    "schedule_source",
                ],
                "source": (
                    "exchange_catalog_occurrence_datetime_current_snapshot"
                ),
                "limitation": (
                    "one observed catalog snapshot per event; not a complete "
                    "history of schedule revisions"
                ),
                "partial_revision_evidence": (
                    "milestone_shadow.remote.jsonl retains point-in-time "
                    "sched_ep values for a subset, but it is not a complete "
                    "or canonical 804-event schedule-update ledger"
                ),
            },
            "exact_bell_ledger": {
                "fields": [
                    "exact_start_utc",
                    "selected_source",
                    "selected_source_family",
                    "candidate_sources",
                    "guard_band",
                ],
                "official_exact_count": len(official),
                "use": (
                    "evaluator cutoff = exact_start_utc minus each row's "
                    "negative guard"
                ),
            },
            "market_close_and_settlement": {
                "joined_804_store": "not retained in joined/events.jsonl",
                "tape_close": (
                    "window1_close_cents/reference_timestamp is the last "
                    "lawful true print, not Kalshi close_time or settlement"
                ),
            },
        },
        "bridge_ruling": {
            "can_read_bell_fit_directly_on_schedule_clock": False,
            "required_live_inputs": [
                "current scheduled start and its observation timestamp",
                "any subsequent schedule revision available before decision",
                "category-conditioned forecast distribution for "
                "bell-minus-current-schedule",
            ],
            "formula": (
                "if delta = actual_bell - current_schedule and a fitted low "
                "is L minutes before actual bell, its schedule-clock target "
                "is Tminus (L - delta)"
            ),
            "practical_consequence": (
                "without a slip forecast/update feed, a bell-fitted table "
                "must be read probabilistically; it cannot promise a single "
                "wall-clock low from the original schedule"
            ),
        },
    }
    return round_numbers(result)


def render(result: Mapping[str, Any]) -> str:
    rows = result["five_game_timing_rows"]
    lines = [
        "# Window-1 timing-anchor audit",
        "",
        "## Ruling",
        "",
        "**The prior five-game timing table is invalid.** Atlas "
        "`bottom_t_med_min` is a lead time to a per-leg, volume-derived "
        "“−0k onset.” It was treated as minutes after the policy-window "
        "left edge. Those are different clocks.",
        "",
        "The four tour categories have no bell-anchored timing column: all "
        "five-game Atlas pages have `timing_gun = null`, and all selected-"
        "category cohort cells have `gun_axis = null`. The depth pass is "
        "therefore held exactly as directed; the timing surface did not "
        "survive.",
        "",
        "There is a second target mismatch: Atlas fits the lowest price "
        "**before −0k onset**, while the evaluator reports the lowest price "
        "through the guarded bell. In this sample, only "
        f"{result['ruling']['five_leg_native_target_comparable_count']}/10 "
        "full-window lows are even before a reconstructable −0k onset; "
        f"{result['ruling']['five_leg_full_window_low_after_native_onset_count']} "
        "are after it and "
        f"{result['ruling']['five_leg_native_onset_unresolved_count']} legs "
        "have no −0k onset under the builder law.",
        "",
        "Signed error below is predicted wall-clock low minus actual "
        "wall-clock low: positive means the prediction was late; negative "
        "means it was early.",
        "",
        "## Five games on T-minus scheduled start",
        "",
        "| Event | Leg | Atlas stored lead (really T−0k) | Actual low vs "
        "schedule | If misread as T−schedule: error |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['event_id']} | {row['leg_id']} | "
            f"T−{row['atlas_stored_lead_minutes_before_minus_0k_onset']:.1f} "
            f"| {t_label(row['actual_low_tminus_scheduled_start_minutes'])} "
            f"| {signed(row['schedule_anchor_hypothesis_error_minutes'])}m |"
        )
    lines += [
        "",
        "The Atlas value is printed in the requested T-minus layout so the "
        "coordinate mismatch is visible; it is **not** a valid scheduled-"
        "start prediction.",
        "",
        "## Three candidate anchors",
        "",
        "| Event | Leg | schedule-anchor error | exact-bell-anchor error | "
        "left-edge error (old table) | native −0k error |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['event_id']} | {row['leg_id']} | "
            f"{signed(row['schedule_anchor_hypothesis_error_minutes'])} | "
            f"{signed(row['exact_bell_anchor_hypothesis_error_minutes'])} | "
            f"{signed(row['window_left_anchor_hypothesis_error_minutes'])} | "
            f"{signed(row['native_minus_0k_axis_error_minutes'])} |"
        )
    summaries = result[
        "five_game_anchor_hypothesis_absolute_error_minutes"
    ]
    lines += [
        "",
        "Median absolute error by anchor hypothesis: schedule "
        f"{summaries['schedule']['median']:.1f}m; exact bell "
        f"{summaries['exact_bell']['median']:.1f}m; left edge "
        f"{summaries['window_left']['median']:.1f}m; native −0k "
        f"{summaries['native_minus_0k']['median']:.1f}m on the "
        f"{summaries['native_minus_0k']['count']} target-comparable legs.",
        "",
        "Changing the anchor collapses much of the old 405-minute headline, "
        "but no candidate anchor makes the surface valid. Its literal "
        "training target is −0k onset, and live_v4 compares it to a start "
        "clock.",
        "",
        "## Lineage",
        "",
        "| Surface/change | Commit date | Relation to honest-clock migration |",
        "|---|---:|---|",
    ]
    lineage = result["lineage"]
    for label, key in (
        ("Atlas timing", "atlas_introduced"),
        ("Cohort timing", "cohort_timing_introduced"),
        ("Evidence-gun recut", "evidence_gun_recut"),
        ("Historical honest-clock restamp", "honest_clock_history_restamp"),
    ):
        item = lineage[key]
        lines.append(
            f"| {label} | {item['date']} (`{item['commit'][:8]}`) | "
            f"{item['subject']} |"
        )
    lines += [
        "",
        "Atlas and cohort timing were fitted before the July 17 historical "
        "clock migration. Later artifact refreshes did not change the "
        "builder target from −0k onset.",
        "",
        "## Exact bell versus stored schedule (234 games)",
        "",
        "| Category | n | median bell slip | p10 | p90 | min | max | "
        "earlier / later |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    slip = result["official_exact_schedule_to_bell"]
    for category, row in slip["by_category"].items():
        lines.append(
            f"| {category} | {row['count']} | {signed(row['median'])}m | "
            f"{signed(row['p10'])}m | {signed(row['p90'])}m | "
            f"{signed(row['min'])}m | {signed(row['max'])}m | "
            f"{row['bell_earlier_than_schedule_count']} / "
            f"{row['bell_later_than_schedule_count']} |"
        )
    overall = slip["all"]
    lines += [
        "",
        f"Overall: median {signed(overall['median'])}m, p10 "
        f"{signed(overall['p10'])}m, p90 {signed(overall['p90'])}m, "
        f"range {signed(overall['min'])}m to "
        f"{signed(overall['max'])}m.",
        "",
        "The evaluator’s earlier −91-minute median was the **guarded "
        "cutoff**, not the bell. Exact rows use a 60-second negative guard, "
        "so the actual-bell median is one minute later.",
        "",
        "Selected exact-start sources:",
        "",
    ]
    for source, count in slip["selected_source_counts"].items():
        lines.append(f"- `{source}`: {count}")
    lines += [
        "",
        "## What Kalshi and the local corpus actually store",
        "",
        "The current Kalshi Market object exposes `occurrence_datetime`, "
        "`open_time`, `close_time`, `expected_expiration_time`, "
        "`latest_expiration_time`, deprecated `expiration_time`, "
        "`updated_time`, and `settlement_ts`. These do not all mean match "
        "start: `close_time` is trading close and "
        "`expected_expiration_time` is expected resolution.",
        "",
        "For this 804-game corpus, `joined/events.jsonl` retained only one "
        "`scheduled_start_exchange_ts`, its "
        "`schedule_observed_exchange_ts`, and source "
        "`exchange_catalog_occurrence_datetime_current_snapshot`. It did "
        "not retain a complete revision history, market close time, or "
        "settlement time. `window1_close_cents` is the last lawful true "
        "print—not a Kalshi lifecycle close.",
        "",
        "`milestone_shadow.remote.jsonl` has point-in-time `sched_ep` values "
        "for a subset of events, so some schedule revisions can be seen "
        "forensically. It is not complete enough to serve as the 804-game "
        "updated-schedule feed.",
        "",
        "The 234 exact games use `exact_start_utc` selected from the sources "
        "listed above. Their evaluator boundary is that exact bell minus "
        "the row’s guard (60 seconds for this class).",
        "",
        "## Reading a bell fit live",
        "",
        "Let `δ = actual bell − current schedule`. A low fitted at `L` "
        "minutes before the actual bell maps to schedule time as:",
        "",
        "`T-minus schedule = L − δ`",
        "",
        "Because δ is broad and category-dependent, the OS needs the "
        "current schedule plus schedule updates and a conditional slip "
        "distribution. With only the original snapshot, the translation is "
        "probabilistic. There is no honest deterministic bridge.",
        "",
        "## Work intentionally not done",
        "",
        "No depth calibration, aim frontier, dial change, package, audit, "
        "holdout read, or live action was performed. The requested "
        "precondition failed: the existing timing surface is not fitted on "
        "the actual bell.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--full-lawful", type=Path, default=Path(FULL_LAWFUL))
    parser.add_argument("--five-report", type=Path, default=Path(FIVE_REPORT))
    parser.add_argument("--start-ledger", type=Path, default=Path(START_LEDGER))
    parser.add_argument("--events", type=Path, default=Path(EVENTS))
    parser.add_argument("--cache-root", type=Path, default=Path(CACHE_ROOT))
    parser.add_argument("--atlas", type=Path, default=Path(ATLAS))
    parser.add_argument("--library", type=Path, default=Path(LIBRARY))
    parser.add_argument("--output", type=Path, default=Path(OUTPUT))
    args = parser.parse_args()
    result = build(args)
    output = args.repo.resolve() / args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / "TIMING_ANCHOR_AUDIT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "TIMING_ANCHOR_AUDIT.md").write_text(
        render(result),
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(output),
        "five_leg_count": len(result["five_game_timing_rows"]),
        "official_exact_count": (
            result["official_exact_schedule_to_bell"]["all"]["count"]
        ),
        "prior_table_valid": (
            result["ruling"]["prior_five_game_timing_table_valid"]
        ),
        "timing_surface_survives": (
            result["ruling"][
                "atlas_timing_surface_survives_as_actual_bell_fit"
            ]
        ),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
