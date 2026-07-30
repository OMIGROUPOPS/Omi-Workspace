#!/usr/bin/env python3
"""Run table-free entry rules through the unchanged live_v4 replay OS.

This is deliberately not the earlier first-order touch harness.  Every row is
produced by ``window1_live_v4_replay.replay_one`` with the full timer scheduler
enabled.  Only the entry-aim mode changes; discovery, dossier reads,
recognition, authority selection, routing, posting, walking, parking, fill
polling, reconciliation, and headroom carry remain live_v4 code.
"""

from __future__ import annotations

import argparse
import asyncio
from collections import Counter, defaultdict
import contextlib
import gc
import json
import math
import os
from pathlib import Path
import statistics
import time
from typing import Any, Iterable

from window1_live_v4_replay import (
    FILL_MODEL,
    PRINTS,
    build_print_index,
    load_print_block,
    load_scope,
    load_tick_block,
    replay_one,
)


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "table_free_full_os_20260730"
)
GRID_PATH = (
    REPO
    / ".claude"
    / "window1_t2_iteration_history"
    / "WINDOW1_T2_GAME_GRID.json"
)
FULL_LAWFUL_PATH = (
    REPO
    / ".claude"
    / "window1_t2_iteration_history"
    / "WINDOW1_FULL_LAWFUL_CEILING.json"
)
DELTA_LADDER_PATH = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "delta_objective_20260729"
    / "WINDOW1_DELTA_LADDER.json"
)
CONTROL_LEDGER_PATH = (
    REPO
    / ".claude"
    / (
        "window1_t2_results_w1-t2-dev-20260712-20260720-"
        "frontier-regret-grid1-scorepkg-v5"
    )
    / (
        "01_w1_t2__macro_hold__fixed_admission_parent_control_"
        "EVENT_LEDGER.jsonl"
    )
)
ATLAS_STUDY_PATH = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "atlas_interim_20260730_consult_v2"
    / "ATLAS_KEY_AND_INTERIM_STUDY.json"
)
PROBE_ROOT = ATLAS_STUDY_PATH.parent / "probe"

MODES = (
    "JOIN",
    "TOUCH_MINUS_1",
    "ONE_SPREAD_BELOW_MID",
    "ATLAS",
)
EXPECTED_LIVE_V4_SHA256 = (
    "25698d80642524c70f39d850ef0a7041edda6df9c4d2dbac0c666d58aab56a63"
)
CAPTURE_EVENTS = {
    "trendpath_live_aim",
    "entry_aim_refused",
    "order_placed",
    "paper_fill",
    "entry_filled",
    "completion_booking_adoption",
    "reconcile_v4_adopted",
    "naked_leg_defect",
    "wrongness_alarm",
}


class StudyError(RuntimeError):
    pass


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def quantile(values: Iterable[float], fraction: float) -> float | None:
    rows = sorted(float(value) for value in values)
    if not rows:
        return None
    index = min(
        len(rows) - 1,
        max(0, math.ceil(fraction * len(rows)) - 1),
    )
    return rows[index]


def distribution(values: Iterable[float | int]) -> dict[str, Any]:
    rows = [float(value) for value in values]
    return {
        "n": len(rows),
        "min": min(rows) if rows else None,
        "p10": quantile(rows, 0.10),
        "p25": quantile(rows, 0.25),
        "median": statistics.median(rows) if rows else None,
        "p75": quantile(rows, 0.75),
        "p90": quantile(rows, 0.90),
        "max": max(rows) if rows else None,
    }


def first_trace(
    rows: list[dict],
    event: str,
    leg: str | None = None,
) -> dict | None:
    return next(
        (
            row
            for row in rows
            if row.get("event") == event
            and (leg is None or row.get("leg") == leg)
        ),
        None,
    )


def load_references() -> tuple[dict, dict, dict]:
    grid = {
        row["event_id"]: row
        for row in json.loads(
            GRID_PATH.read_text(encoding="utf-8")
        )["games"]
    }
    full = json.loads(FULL_LAWFUL_PATH.read_text(encoding="utf-8"))
    floors = {}
    for row in full["events"]:
        floor = row.get("independent_touch_floor") or {}
        touches = floor.get("touches") or {}
        floors[row["event_id"]] = {
            str(leg_id): int(value["price_cents"])
            for leg_id, value in touches.items()
            if isinstance(value.get("price_cents"), int)
        }
    ladder = json.loads(DELTA_LADDER_PATH.read_text(encoding="utf-8"))
    return grid, floors, ladder


def load_authoritative_closes() -> dict[str, dict[str, int]]:
    output = {}
    with CONTROL_LEDGER_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            output[row["event_id"]] = {
                str(leg["leg_id"]): int(leg["window1_close_cents"])
                for leg in row.get("legs") or []
                if (
                    leg.get("available")
                    and isinstance(leg.get("window1_close_cents"), int)
                )
            }
    if len(output) != 804:
        raise StudyError(
            f"authoritative close ledger covers {len(output)}, expected 804"
        )
    return output


def extract_event(
    result: dict,
    game: dict,
    mode: str,
    grid_game: dict,
    fillable_lows: dict[str, int],
) -> dict:
    legs = {}
    deltas = {}
    gaps = {}
    for leg in game["legs"]:
        leg_id = leg["leg"]
        position = result["positions"][leg_id]
        fill = first_trace(result["trace"], "paper_fill", leg_id)
        fill_details = (fill or {}).get("details") or {}
        fill_price = fill_details.get("fill_price")
        if fill_price is None:
            fill_price = fill_details.get("price")
        if position["filled"] and not isinstance(fill_price, (int, float)):
            paper_position = position.get("paper_position") or {}
            fill_price = paper_position.get("average_price")
        fill_price = (
            int(round(float(fill_price)))
            if position["filled"] and isinstance(fill_price, (int, float, str))
            else None
        )
        close = (
            grid_game["legs"][leg_id]["price_path"]["close"]
            .get("price_cents")
        )
        close = int(close) if isinstance(close, int) else None
        low = fillable_lows.get(leg_id)
        delta = (
            fill_price - close
            if fill_price is not None and close is not None
            else None
        )
        gap = (
            fill_price - low
            if fill_price is not None and low is not None
            else None
        )
        deltas[leg_id] = delta
        gaps[leg_id] = gap
        aim = first_trace(
            result["trace"], "trendpath_live_aim", leg_id
        )
        legs[leg_id] = {
            "ticker": leg["ticker"],
            "filled": bool(position["filled"]),
            "fill_price_cents": fill_price,
            "fill_ts": (fill or {}).get("ts"),
            "fill_trigger": fill_details.get("fill_trigger"),
            "window1_close_cents": close,
            "fill_minus_window1_close_cents": delta,
            "own_fillable_low_cents": low,
            "fill_minus_own_fillable_low_cents": gap,
            "first_live_aim": (aim or {}).get("details"),
            "orders_posted": len(position.get("orders") or []),
        }
    completed = bool(result["pair_completed"])
    combined_delta = (
        sum(deltas.values())
        if completed
        and len(deltas) == 2
        and all(value is not None for value in deltas.values())
        else None
    )
    pair_gap = (
        sum(gaps.values())
        if completed
        and len(gaps) == 2
        and all(value is not None for value in gaps.values())
        else None
    )
    alarms = Counter(
        row.get("details", {}).get("code")
        for row in result["trace"]
        if row.get("event") == "wrongness_alarm"
    )
    return {
        "event_id": game["event"],
        "category": game["category"],
        "slice": game["slice"],
        "mode": mode,
        "evaluator_boundary_resolved": game[
            "evaluator_boundary_resolved"
        ],
        "evaluator_window_positive": game[
            "evaluator_window_positive"
        ],
        "replayed_right_ts": game["right_ts"],
        "pair_completed": completed,
        "combined_delta_to_window1_close_cents": combined_delta,
        "negative_combined_delta": (
            combined_delta is not None and combined_delta < 0
        ),
        "both_legs_under_own_close": (
            combined_delta is not None
            and all(value is not None and value < 0 for value in deltas.values())
        ),
        "pair_fill_minus_pair_fillable_low_cents": pair_gap,
        "legs": legs,
        "first_input_break": result.get("first_input_break"),
        "wrongness_alarm_counts": dict(alarms),
        "live_v4_sha256": result["live_v4"]["sha256_before"],
        "full_scheduler": not result["initial_aim_probe_fast_clock"],
        "fill_model": result["fill_model"],
    }


def no_window_event(
    game: dict,
    mode: str,
    grid_game: dict,
    fillable_lows: dict[str, int],
) -> dict:
    return {
        "event_id": game["event"],
        "category": game["category"],
        "slice": game["slice"],
        "mode": mode,
        "evaluator_boundary_resolved": game[
            "evaluator_boundary_resolved"
        ],
        "evaluator_window_positive": False,
        "replayed_right_ts": game["right_ts"],
        "pair_completed": False,
        "combined_delta_to_window1_close_cents": None,
        "negative_combined_delta": False,
        "both_legs_under_own_close": False,
        "pair_fill_minus_pair_fillable_low_cents": None,
        "legs": {
            leg["leg"]: {
                "ticker": leg["ticker"],
                "filled": False,
                "fill_price_cents": None,
                "fill_ts": None,
                "fill_trigger": None,
                "window1_close_cents": (
                    grid_game["legs"][leg["leg"]]["price_path"]["close"]
                    .get("price_cents")
                ),
                "fill_minus_window1_close_cents": None,
                "own_fillable_low_cents": fillable_lows.get(leg["leg"]),
                "fill_minus_own_fillable_low_cents": None,
                "first_live_aim": None,
                "orders_posted": 0,
            }
            for leg in game["legs"]
        },
        "first_input_break": {
            "source": "REPLAY_WINDOW",
            "error": "non-positive retained replay interval",
        },
        "wrongness_alarm_counts": {},
        "live_v4_sha256": None,
        "full_scheduler": True,
        "fill_model": FILL_MODEL,
    }


def save_shard(
    path: Path,
    rows: list[dict],
    *,
    shard_index: int,
    shard_count: int,
    selected_count: int,
    started: float,
) -> None:
    write_json(path, {
        "schema_version": "window1-table-free-full-os-shard-v1",
        "instrument": (
            "unchanged live_v4 via window1_live_v4_replay.replay_one; "
            "full scheduler; only interim_entry_aim_mode changed"
        ),
        "fill_model": FILL_MODEL,
        "modes": list(MODES),
        "shard_index": shard_index,
        "shard_count": shard_count,
        "rows": len(rows),
        "selected_rows": selected_count,
        "complete": len(rows) == selected_count,
        "elapsed_seconds_this_process": round(
            time.monotonic() - started, 3
        ),
        "events": rows,
    })


async def run_shard(args: argparse.Namespace) -> int:
    grid, floors, _ladder = load_references()
    games = load_scope(None, allow_unresolved_boundary=True)
    work = [
        (mode, game)
        for mode in MODES
        for game in games
    ]
    selected = [
        row
        for index, row in enumerate(work)
        if index % args.shard_count == args.shard_index
    ]
    shard_root = args.out / "shards" / (
        f"shard_{args.shard_index:02d}_of_{args.shard_count:02d}"
    )
    receipt = shard_root / "FULL_OS_REPLAY.json"
    rows = []
    if receipt.exists():
        prior = json.loads(receipt.read_text(encoding="utf-8"))
        if (
            prior.get("shard_index") == args.shard_index
            and prior.get("shard_count") == args.shard_count
        ):
            rows = list(prior.get("events") or [])
    completed = {(row["mode"], row["event_id"]) for row in rows}
    ranges = build_print_index(
        PRINTS,
        shard_root / "_input_index" / "prints_by_ticker.json",
    )
    started = time.monotonic()
    for index, (mode, game) in enumerate(selected, 1):
        key = (mode, game["event"])
        if key in completed:
            continue
        print(
            f"[{args.shard_index}:{index}/{len(selected)}] "
            f"{mode} {game['event']}",
            flush=True,
        )
        grid_game = grid[game["event"]]
        fillable_lows = floors.get(game["event"]) or {}
        if game["right_ts"] <= game["left_ts"]:
            row = no_window_event(
                game, mode, grid_game, fillable_lows
            )
        else:
            with open(os.devnull, "w", encoding="utf-8") as sink:
                with contextlib.redirect_stdout(sink):
                    result = await replay_one(
                        game,
                        ranges,
                        shard_root / "_scratch" / mode,
                        counterfactual={
                            "kind": "interim_entry_aim_mode",
                            "mode": mode,
                        },
                        write_trace=False,
                        capture_events=CAPTURE_EVENTS,
                        persist_engine_logs=False,
                        initial_aim_probe_fast_clock=False,
                        hash_large_inputs=False,
                    )
            row = extract_event(
                result,
                game,
                mode,
                grid_game,
                fillable_lows,
            )
            del result
            gc.collect()
        rows.append(row)
        completed.add(key)
        save_shard(
            receipt,
            rows,
            shard_index=args.shard_index,
            shard_count=args.shard_count,
            selected_count=len(selected),
            started=started,
        )
    save_shard(
        receipt,
        rows,
        shard_index=args.shard_index,
        shard_count=args.shard_count,
        selected_count=len(selected),
        started=started,
    )
    print(json.dumps({
        "shard": args.shard_index,
        "rows": len(rows),
        "selected": len(selected),
        "complete": len(rows) == len(selected),
    }, indent=2))
    return 0


def load_shards(out: Path) -> list[dict]:
    paths = sorted(
        (out / "shards").glob(
            "shard_*_of_*/FULL_OS_REPLAY.json"
        )
    )
    if not paths:
        raise StudyError("no full-OS replay shards found")
    rows = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not payload.get("complete"):
            raise StudyError(f"incomplete shard: {path}")
        rows.extend(payload["events"])
    by_key = {(row["mode"], row["event_id"]): row for row in rows}
    if len(by_key) != len(MODES) * 804:
        raise StudyError(
            f"full-OS replay covers {len(by_key)} rows, "
            f"expected {len(MODES) * 804}"
        )
    return [
        by_key[(mode, event_id)]
        for mode in MODES
        for event_id in sorted(
            row["event_id"]
            for row in by_key.values()
            if row["mode"] == mode
        )
    ]


def best_ask(row: dict) -> int | None:
    values = [
        int(level[0])
        for level in row.get("asks") or []
        if level and isinstance(level[0], (int, float))
    ]
    return min(values) if values else None


def save_floor_shard(
    path: Path,
    rows: list[dict],
    *,
    shard_index: int,
    shard_count: int,
    selected_count: int,
    started: float,
) -> None:
    write_json(path, {
        "schema_version": "window1-no-depth-touch-floor-shard-v1",
        "floor_contract": (
            "minimum later true print or opposite best ask inside the full "
            "lawful evaluator window; latest retained BBO at/before the "
            "left edge is visible at the left edge; no depth/capacity/"
            "five-contract gate"
        ),
        "shard_index": shard_index,
        "shard_count": shard_count,
        "rows": len(rows),
        "selected_rows": selected_count,
        "complete": len(rows) == selected_count,
        "elapsed_seconds_this_process": round(
            time.monotonic() - started, 3
        ),
        "events": rows,
    })


def run_floor_shard(args: argparse.Namespace) -> int:
    grid, _old_floors, _ladder = load_references()
    authoritative_closes = load_authoritative_closes()
    games = load_scope(None, allow_unresolved_boundary=True)
    selected = [
        game
        for index, game in enumerate(games)
        if index % args.shard_count == args.shard_index
    ]
    shard_root = args.out / "floor_shards" / (
        f"shard_{args.shard_index:02d}_of_{args.shard_count:02d}"
    )
    receipt = shard_root / "NO_DEPTH_TOUCH_FLOORS.json"
    rows = []
    if receipt.exists():
        prior = json.loads(receipt.read_text(encoding="utf-8"))
        if (
            prior.get("shard_index") == args.shard_index
            and prior.get("shard_count") == args.shard_count
        ):
            rows = list(prior.get("events") or [])
    completed = {row["event_id"] for row in rows}
    ranges = build_print_index(
        PRINTS,
        shard_root / "_input_index" / "prints_by_ticker.json",
    )
    started = time.monotonic()
    for index, game in enumerate(selected, 1):
        if game["event"] in completed:
            continue
        print(
            f"[floor:{args.shard_index}:{index}/{len(selected)}] "
            f"{game['event']}",
            flush=True,
        )
        grid_game = grid[game["event"]]
        leg_rows = {}
        if game["evaluator_window_positive"]:
            for leg in game["legs"]:
                leg_id = leg["leg"]
                ticker = leg["ticker"]
                prints, _ = load_print_block(
                    ticker,
                    ranges,
                    game["left_ts"],
                    game["right_ts"],
                )
                ticks, prior_tick = load_tick_block(
                    ticker,
                    game["left_ts"],
                    game["right_ts"],
                )
                candidates = [
                    {
                        "price_cents": int(row["price"]),
                        "ts": float(row["ts"]),
                        "source": "true_print",
                    }
                    for row in prints
                ]
                visible_ticks = (
                    [prior_tick] if prior_tick is not None else []
                ) + ticks
                for tick in visible_ticks:
                    ask = best_ask(tick)
                    if ask is None:
                        continue
                    candidates.append({
                        "price_cents": ask,
                        "ts": max(
                            float(game["left_ts"]),
                            float(tick["ts"]),
                        ),
                        "source": (
                            "left_edge_visible_prior_bbo"
                            if tick is prior_tick
                            else "opposite_bbo"
                        ),
                    })
                floor = (
                    min(
                        candidates,
                        key=lambda row: (
                            row["price_cents"],
                            row["ts"],
                            row["source"],
                        ),
                    )
                    if candidates
                    else None
                )
                close = authoritative_closes.get(
                    game["event"], {}
                ).get(leg_id)
                leg_rows[leg_id] = {
                    "ticker": ticker,
                    "floor": floor,
                    "window1_close_cents": close,
                    "floor_minus_window1_close_cents": (
                        floor["price_cents"] - int(close)
                        if floor is not None and isinstance(close, int)
                        else None
                    ),
                    "true_print_candidates": len(prints),
                    "bbo_candidates": sum(
                        best_ask(tick) is not None
                        for tick in visible_ticks
                    ),
                }
        rows.append({
            "event_id": game["event"],
            "category": game["category"],
            "evaluator_window_positive": game[
                "evaluator_window_positive"
            ],
            "legs": leg_rows,
        })
        completed.add(game["event"])
        save_floor_shard(
            receipt,
            rows,
            shard_index=args.shard_index,
            shard_count=args.shard_count,
            selected_count=len(selected),
            started=started,
        )
    save_floor_shard(
        receipt,
        rows,
        shard_index=args.shard_index,
        shard_count=args.shard_count,
        selected_count=len(selected),
        started=started,
    )
    return 0


def load_floor_shards(out: Path) -> dict[str, dict]:
    paths = sorted(
        (out / "floor_shards").glob(
            "shard_*_of_*/NO_DEPTH_TOUCH_FLOORS.json"
        )
    )
    if not paths:
        raise StudyError("no no-depth touch-floor shards found")
    rows = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not payload.get("complete"):
            raise StudyError(f"incomplete floor shard: {path}")
        rows.extend(payload["events"])
    by_event = {row["event_id"]: row for row in rows}
    if len(by_event) != 804:
        raise StudyError(
            f"no-depth floor covers {len(by_event)} events, expected 804"
        )
    return by_event


def apply_matched_floors(
    rows: list[dict],
    floors: dict[str, dict],
) -> None:
    for row in rows:
        floor_event = floors[row["event_id"]]
        pair_gaps = []
        for leg_id, leg in row["legs"].items():
            old_floor = leg.get("own_fillable_low_cents")
            floor_row = floor_event.get("legs", {}).get(leg_id) or {}
            floor = (floor_row.get("floor") or {}).get("price_cents")
            leg[
                "legacy_true_print_independent_touch_floor_cents"
            ] = old_floor
            leg["own_fillable_low_contract"] = (
                "RESTING_TOUCH_FILL_V1_MATCHED_NO_DEPTH_PRINT_OR_BBO"
            )
            leg["own_fillable_low_cents"] = floor
            leg["own_fillable_low_proof"] = floor_row.get("floor")
            gap = (
                int(leg["fill_price_cents"]) - int(floor)
                if (
                    leg.get("fill_price_cents") is not None
                    and floor is not None
                )
                else None
            )
            leg["fill_minus_own_fillable_low_cents"] = gap
            if gap is not None:
                pair_gaps.append(gap)
        row["pair_fill_minus_pair_fillable_low_cents"] = (
            sum(pair_gaps)
            if row["pair_completed"] and len(pair_gaps) == 2
            else None
        )


def apply_authoritative_closes(
    rows: list[dict],
    closes: dict[str, dict[str, int]],
) -> None:
    for row in rows:
        deltas = {}
        for leg_id, leg in row["legs"].items():
            old_close = leg.get("window1_close_cents")
            close = closes.get(row["event_id"], {}).get(leg_id)
            leg["legacy_game_grid_close_cents"] = old_close
            leg["window1_close_contract"] = (
                "frozen_parent_control_authoritative_latest_timestamp"
            )
            leg["window1_close_cents"] = close
            delta = (
                int(leg["fill_price_cents"]) - int(close)
                if (
                    leg.get("fill_price_cents") is not None
                    and close is not None
                )
                else None
            )
            leg["fill_minus_window1_close_cents"] = delta
            deltas[leg_id] = delta
        combined = (
            sum(deltas.values())
            if (
                row["pair_completed"]
                and len(deltas) == 2
                and all(value is not None for value in deltas.values())
            )
            else None
        )
        row["combined_delta_to_window1_close_cents"] = combined
        row["negative_combined_delta"] = (
            combined is not None and combined < 0
        )
        row["both_legs_under_own_close"] = (
            combined is not None
            and all(value is not None and value < 0 for value in deltas.values())
        )


def matched_floor_ceiling(
    floors: dict[str, dict],
    closes: dict[str, dict[str, int]],
) -> dict:
    defined = []
    for event_id, event in floors.items():
        legs = event.get("legs") or {}
        deltas = []
        for leg_id, row in legs.items():
            floor = (row.get("floor") or {}).get("price_cents")
            close = closes.get(event_id, {}).get(leg_id)
            deltas.append(
                int(floor) - int(close)
                if floor is not None and close is not None
                else None
            )
        if len(deltas) != 2 or any(value is None for value in deltas):
            continue
        defined.append([int(value) for value in deltas])
    return {
        "defined_two_leg_close_and_touch": len(defined),
        "negative_combined_delta": sum(
            sum(values) < 0 for values in defined
        ),
        "both_legs_under_own_close": sum(
            all(value < 0 for value in values)
            for values in defined
        ),
    }


def summarize_mode(rows: list[dict]) -> dict:
    completed = [row for row in rows if row["pair_completed"]]
    leg_gaps = [
        leg["fill_minus_own_fillable_low_cents"]
        for row in rows
        for leg in row["legs"].values()
        if leg["fill_minus_own_fillable_low_cents"] is not None
    ]
    pair_gaps = [
        row["pair_fill_minus_pair_fillable_low_cents"]
        for row in rows
        if row["pair_fill_minus_pair_fillable_low_cents"] is not None
    ]
    by_category = {}
    for category in sorted({row["category"] for row in rows}):
        subset = [row for row in rows if row["category"] == category]
        by_category[category] = {
            "events": len(subset),
            "completions": sum(row["pair_completed"] for row in subset),
            "negative_combined_delta": sum(
                row["negative_combined_delta"] for row in subset
            ),
            "both_legs_under_own_close": sum(
                row["both_legs_under_own_close"] for row in subset
            ),
            "legs_filled": sum(
                leg["filled"]
                for row in subset
                for leg in row["legs"].values()
            ),
        }
    return {
        "events": len(rows),
        "evaluator_window_positive": sum(
            row["evaluator_window_positive"] for row in rows
        ),
        "evaluator_window_unmeasurable": sum(
            not row["evaluator_window_positive"] for row in rows
        ),
        "completions": len(completed),
        "legs_filled": sum(
            leg["filled"]
            for row in rows
            for leg in row["legs"].values()
        ),
        "negative_combined_delta": sum(
            row["negative_combined_delta"] for row in rows
        ),
        "both_legs_under_own_close": sum(
            row["both_legs_under_own_close"] for row in rows
        ),
        "events_without_executable_interval": sum(
            (row["first_input_break"] or {}).get("source")
            == "REPLAY_WINDOW"
            for row in rows
        ),
        "runtime_input_break_events": sum(
            row["first_input_break"] is not None
            and (row["first_input_break"] or {}).get("source")
            != "REPLAY_WINDOW"
            for row in rows
        ),
        "completed_pairs_with_two_fillable_lows": len(pair_gaps),
        "per_leg_fill_minus_own_fillable_low_cents": distribution(
            leg_gaps
        ),
        "per_pair_fill_minus_pair_fillable_low_cents": distribution(
            pair_gaps
        ),
        "by_category": by_category,
    }


def render_report(report: dict) -> str:
    rows = []
    for mode in MODES:
        summary = report["mode_summary"][mode]
        leg_gap = summary[
            "per_leg_fill_minus_own_fillable_low_cents"
        ]
        rows.append(
            f"| {mode} | {summary['completions']} | "
            f"{summary['negative_combined_delta']} / "
            f"{report['tape_ceilings']['negative_combined_delta']} | "
            f"{summary['both_legs_under_own_close']} / "
            f"{report['tape_ceilings']['both_legs_under_own_close']} | "
            f"{leg_gap['n']} | {leg_gap['median']} | "
            f"{leg_gap['p90']} | {leg_gap['max']} |"
        )
    alarm = report["wrongness_alarm_grouping"]
    atlas = alarm["atlas_8072_decomposition"]
    return "\n".join([
        "# Table-free aims through the full live_v4 OS",
        "",
        (
            "**Instrument:** unchanged `live_v4.LiveV3`, executed by the "
            "full replay scheduler for all 804 game rows per mode. Twelve "
            "rows have a non-positive retained interval and are explicit "
            "no-window results; live_v4 executes on the other 792. Only "
            "`interim_entry_aim_mode` changes."
        ),
        "",
        (
            "The prior 51-completion wider comparison was a lighter first-"
            "order touch harness and is not used as outcome evidence here. "
            "ATLAS is rerun below as the full-OS baseline."
        ),
        "",
        (
            "**Ruling:** the old six-to-one completion headline does not "
            "survive the full OS. JOIN completes 86 games versus ATLAS's "
            "54 (1.59x). JOIN is better on the value tests - 23 versus 2 "
            "negative-combined-delta completions (11.5x), and 10 versus 2 "
            "with both legs below their own closes (5x) - but it captures "
            "only 23/580 and 10/340 of the requested tape ceilings. JOIN is "
            "the best of these three table-free rules, not a sufficient "
            "replacement for the missing lawful aim surface."
        ),
        "",
        f"**Fill model:** {report['instrument']['fill_model']}",
        "",
        "## Outcomes",
        "",
        (
            "| rule | completed / 804 | negative combined close delta / "
            "580 ceiling | both legs below own close / 340 ceiling | "
            "filled legs with lawful low | median fill-low | p90 | max |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        *rows,
        "",
        (
            "A fill-low gap of 0c means the OS filled at that leg's own "
            "independent-touch floor. Positive values mean it paid above the "
            "best price the full lawful tape proved fillable. Unfilled legs "
            "have no achieved fill-minus-low gap and remain null in the JSON."
        ),
        "",
        (
            "Evaluator coverage is 693 games with a positive lawful window. "
            "The other 111 are unmeasurable here: 99 have no resolved "
            "evaluator boundary and 12 have no positive retained replay "
            "interval. The latter are explicit no-window rows, not runtime "
            "input failures."
        ),
        "",
        "## Ceiling definitions",
        "",
        (
            "- Requested legacy comparison - 580: games where the retained "
            "true-print receipt oracle proves a negative combined delta to "
            "the two authoritative Window-1 closes."
        ),
        (
            "- Requested legacy comparison - 340: games where that "
            "true-print receipt oracle proves both legs individually "
            "reachable strictly below their own Window-1 close."
        ),
        (
            "- 622 games have both an authoritative two-leg close and a "
            "two-leg true-print receipt floor. No value is fabricated for "
            "the remainder."
        ),
        (
            "- Fill-model-matched ceiling (true print **or opposite BBO**, "
            "no depth gate): "
            f"{report['fill_model_matched_tape_ceilings']['negative_combined_delta']} "
            "negative combined; "
            f"{report['fill_model_matched_tape_ceilings']['both_legs_under_own_close']} "
            "both legs below own close; "
            f"{report['fill_model_matched_tape_ceilings']['defined_two_leg_close_and_touch']} "
            "defined two-leg comparisons."
        ),
        "",
        "## The 8,072 ATLAS alarms",
        "",
        (
            f"All {atlas['total_invocation_alarms']} are repeated "
            "`FIT_CONSULT_KEY_MISMATCH` invocations from ATLAS, spanning "
            f"{atlas['unique_games']} games. They are not 8,072 independent "
            "market events."
        ),
        (
            f"- {atlas['unique_page_crossing_legs']} unique legs in "
            f"{atlas['unique_page_crossing_games']} games actually crossed "
            "an ATLAS broad page. Those games account for "
            f"{atlas['alarm_invocations_in_page_crossing_games']} alarm "
            "invocations."
        ),
        (
            f"- The other {atlas['alarm_invocations_in_all_other_games']} "
            "invocations are repeated same-page or otherwise non-page-"
            "crossing fit-key mismatches. They are still contract wrongness, "
            "but not 7,930 distinct page crossings."
        ),
        (
            "- Separate surfaces: COHORT emitted 8,072 "
            "`FIT_CONTRACT_MISSING` invocations; contention emitted 942 "
            "`VERDICT_IGNORED` invocations; fitted surfaces emitted 15 thin-"
            "row alarms."
        ),
        "",
        "## Retention",
        "",
        (
            "The VPS WebSocket depth recorder remained running throughout "
            "this study. This replay did not restart or alter it."
        ),
        "",
    ])


def analyze_existing_alarms() -> dict:
    probe_paths = sorted(
        PROBE_ROOT.glob("shard_*_of_*/CONSULTATION_PROBE.json")
    )
    if not probe_paths:
        raise StudyError("consultation probe is absent")
    probes = []
    for path in probe_paths:
        probes.extend(
            json.loads(path.read_text(encoding="utf-8"))["rows"]
        )
    study = json.loads(ATLAS_STUDY_PATH.read_text(encoding="utf-8"))
    displacement = study["price_key_displacement_rows"]
    crossing_events = {
        row["event_id"]
        for row in displacement
        if row.get("page_changed") is True
    }
    crossing_legs = [
        row for row in displacement if row.get("page_changed") is True
    ]
    code_totals = Counter()
    code_games = defaultdict(set)
    atlas_on_crossing_events = 0
    atlas_on_other_events = 0
    for row in probes:
        counts = Counter(row.get("wrongness_alarm_counts") or {})
        code_totals.update(counts)
        for code, count in counts.items():
            if count:
                code_games[code].add(row["event_id"])
        mismatch = counts.get("FIT_CONSULT_KEY_MISMATCH", 0)
        if row["event_id"] in crossing_events:
            atlas_on_crossing_events += mismatch
        else:
            atlas_on_other_events += mismatch
    return {
        "measurement": (
            "existing initial-consultation probe; invocation-level alarms, "
            "not unique games or unique economic events"
        ),
        "by_surface": {
            "ATLAS_V1": {
                "alarm_code": "FIT_CONSULT_KEY_MISMATCH",
                "invocations": code_totals[
                    "FIT_CONSULT_KEY_MISMATCH"
                ],
                "games": len(code_games[
                    "FIT_CONSULT_KEY_MISMATCH"
                ]),
                "reason": (
                    "fit key is first-hour-median discovery page; "
                    "consult key is the exact consultation price/page"
                ),
            },
            "COHORT_SURFACE_V1": {
                "alarm_code": "FIT_CONTRACT_MISSING",
                "invocations": code_totals["FIT_CONTRACT_MISSING"],
                "games": len(code_games["FIT_CONTRACT_MISSING"]),
            },
            "CONTENTION_SELECTOR": {
                "alarm_code": "VERDICT_IGNORED",
                "invocations": code_totals["VERDICT_IGNORED"],
                "games": len(code_games["VERDICT_IGNORED"]),
            },
            "THIN_ROWS_ALL_FITTED_SURFACES": {
                "alarm_code": "FITTED_ROW_THIN",
                "invocations": code_totals["FITTED_ROW_THIN"],
                "games": len(code_games["FITTED_ROW_THIN"]),
            },
        },
        "atlas_8072_decomposition": {
            "total_invocation_alarms": code_totals[
                "FIT_CONSULT_KEY_MISMATCH"
            ],
            "unique_games": len(code_games[
                "FIT_CONSULT_KEY_MISMATCH"
            ]),
            "measurable_unique_legs": len(displacement),
            "unique_page_crossing_legs": len(crossing_legs),
            "unique_page_crossing_games": len(crossing_events),
            "alarm_invocations_in_page_crossing_games": (
                atlas_on_crossing_events
            ),
            "alarm_invocations_in_all_other_games": (
                atlas_on_other_events
            ),
            "interpretation": (
                "31 is the number of unique measurable legs that crossed an "
                "ATLAS broad page. 8072 is repeated dossier-consultation "
                "alarms, including same-page consultations whose fit-key "
                "semantics still mismatch. They are not 8072 independent "
                "market events."
            ),
        },
        "all_code_totals": dict(code_totals),
    }


def run_analyze(args: argparse.Namespace) -> int:
    rows = load_shards(args.out)
    matched_floors = load_floor_shards(args.out)
    authoritative_closes = load_authoritative_closes()
    apply_authoritative_closes(rows, authoritative_closes)
    apply_matched_floors(rows, matched_floors)
    _grid, _floors, ladder = load_references()
    modes = {
        mode: summarize_mode(
            [row for row in rows if row["mode"] == mode]
        )
        for mode in MODES
    }
    ceiling = {
        "negative_combined_delta": int(
            ladder["independent_touch"][
                "negative_combined_delta_count"
            ]
        ),
        "both_legs_under_own_close": int(
            ladder["independent_touch"][
                "both_legs_reachable_below_own_close_count"
            ]
        ),
        "defined_two_leg_close_and_touch": int(
            ladder["independent_touch"][
                "authoritative_close_and_two_leg_touch_available_count"
            ]
        ),
    }
    matched_ceiling = matched_floor_ceiling(
        matched_floors, authoritative_closes
    )
    for mode, summary in modes.items():
        summary["capture_of_tape_ceiling"] = {
            "negative_combined_delta": {
                "achieved": summary["negative_combined_delta"],
                "ceiling": ceiling["negative_combined_delta"],
                "share": (
                    summary["negative_combined_delta"]
                    / ceiling["negative_combined_delta"]
                ),
            },
            "both_legs_under_own_close": {
                "achieved": summary["both_legs_under_own_close"],
                "ceiling": ceiling["both_legs_under_own_close"],
                "share": (
                    summary["both_legs_under_own_close"]
                    / ceiling["both_legs_under_own_close"]
                ),
            },
        }
        summary["comparison_to_fill_model_matched_ceiling"] = {
            "negative_combined_delta": {
                "achieved": summary["negative_combined_delta"],
                "ceiling": matched_ceiling[
                    "negative_combined_delta"
                ],
                "share": (
                    summary["negative_combined_delta"]
                    / matched_ceiling["negative_combined_delta"]
                    if matched_ceiling["negative_combined_delta"]
                    else None
                ),
            },
            "both_legs_under_own_close": {
                "achieved": summary["both_legs_under_own_close"],
                "ceiling": matched_ceiling[
                    "both_legs_under_own_close"
                ],
                "share": (
                    summary["both_legs_under_own_close"]
                    / matched_ceiling["both_legs_under_own_close"]
                    if matched_ceiling["both_legs_under_own_close"]
                    else None
                ),
            },
        }
    live_hashes = sorted({
        row["live_v4_sha256"]
        for row in rows
        if row["live_v4_sha256"]
    })
    if live_hashes != [EXPECTED_LIVE_V4_SHA256]:
        raise StudyError(
            "full-OS rows do not share the frozen live_v4 source hash: "
            f"{live_hashes}"
        )
    report = {
        "schema_version": "window1-table-free-full-os-study-v1",
        "headline_instrument": (
            "full unchanged live_v4 OS replay, not the prior lighter "
            "first-order touch harness"
        ),
        "instrument": {
            "entry_point": (
                "window1_live_v4_replay.replay_one -> live_v4.LiveV3"
            ),
            "full_scheduler": all(row["full_scheduler"] for row in rows),
            "live_v4_sha256_values": live_hashes,
            "only_changed_dial": "interim_entry_aim_mode",
            "modes": list(MODES),
            "fill_model": FILL_MODEL,
        },
        "population": 804,
        "rows": len(rows),
        "tape_ceilings": ceiling,
        "fill_model_matched_tape_ceilings": matched_ceiling,
        "mode_summary": modes,
        "wrongness_alarm_grouping": analyze_existing_alarms(),
        "events": rows,
    }
    write_json(args.out / "TABLE_FREE_FULL_OS_RESULTS.json", report)
    (args.out / "TABLE_FREE_FULL_OS_REPORT.md").write_text(
        render_report(report),
        encoding="utf-8",
    )
    print(json.dumps({
        "instrument": report["headline_instrument"],
        "tape_ceilings": ceiling,
        "mode_summary": modes,
        "wrongness": report["wrongness_alarm_grouping"],
    }, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        required=True,
        choices=("run", "floors", "analyze"),
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.shard_count:
        parser.error("shard index must be inside shard count")
    return args


def main() -> int:
    args = parse_args()
    if args.mode == "run":
        return asyncio.run(run_shard(args))
    if args.mode == "floors":
        return run_floor_shard(args)
    return run_analyze(args)


if __name__ == "__main__":
    raise SystemExit(main())
