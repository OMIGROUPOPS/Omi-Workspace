#!/usr/bin/env python3
"""Measure ATLAS key displacement and table-free interim entry aims.

The consultation probe executes unchanged live_v4 decision code under the
existing replay seams and retains only the first signed ATLAS decision for
each leg.  The wider counterfactual then rests one initial order at that exact
decision timestamp and applies the replay's named touch-fill model through the
full guarded Window 1.
"""

from __future__ import annotations

import argparse
import asyncio
from collections import Counter, defaultdict
import contextlib
import gc
import gzip
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
ATLAS_PATH = REPO / ".claude" / "trendpath" / "ATLAS_V1.json"
GRID_PATH = (
    REPO
    / ".claude"
    / "window1_t2_iteration_history"
    / "WINDOW1_T2_GAME_GRID.json"
)
FIVE_SELECTION = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "delta_objective_20260729"
    / "FIVE_GAME_SELECTION.json"
)
DEFAULT_RANGE_STREAM_DIR = Path(
    os.environ.get(
        "W1_RANGE_ATTACK_PRERUN_ROOT",
        (
            r"C:\Users\omigr\OMI-Workspace-codex-w1-recognition-laps"
            r"\.claude\window1_range_attack_prerun_20260725"
        ),
    )
)
DEFAULT_OUT = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "atlas_interim_20260730"
)
CAPTURE_EVENTS = {
    "entry_dossier",
    "trendpath_live_aim",
    "order_placed",
    "wrongness_alarm",
    "entry_aim_refused",
    "no_path_page_refused",
    "paper_fill",
    "entry_filled",
}
INTERIM_MODES = (
    "ATLAS",
    "JOIN",
    "TOUCH_MINUS_1",
    "ONE_SPREAD_BELOW_MID",
)
BUCKETS = ("le25", "26_50", "51_75", "ge75")


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


def distribution(values: Iterable[float]) -> dict[str, Any]:
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


def first_trace(rows: list[dict], event: str, leg: str) -> dict | None:
    return next(
        (
            row
            for row in rows
            if row.get("event") == event and row.get("leg") == leg
        ),
        None,
    )


def extract_probe_event(result: dict, game: dict) -> dict:
    rows = result["trace"]
    legs = {}
    for leg in game["legs"]:
        leg_id = leg["leg"]
        aim = first_trace(rows, "trendpath_live_aim", leg_id)
        dossier = next(
            (
                row
                for row in rows
                if (
                    row.get("event") == "entry_dossier"
                    and row.get("leg") == leg_id
                )
            ),
            None,
        )
        order = next(
            (
                row
                for row in rows
                if (
                    row.get("event") == "order_placed"
                    and row.get("leg") == leg_id
                    and row.get("details", {}).get("action") == "buy"
                )
            ),
            None,
        )
        lineage = (
            ((dossier or {}).get("details") or {})
            .get("surfaces", {})
            .get("consultation_lineage")
            or {}
        )
        atlas_read = (
            ((dossier or {}).get("details") or {})
            .get("surfaces", {})
            .get("atlas_page")
            or {}
        )
        atlas_depths = atlas_read.get("bottom_p25_50_75") or []
        atlas_depth = (
            atlas_depths[1] if len(atlas_depths) >= 2 else None
        )
        live_page = (
            (aim or {}).get("details", {}).get("page")
            or atlas_read.get("page")
        )
        live_page_n = (
            (aim or {}).get("details", {}).get("page_n")
            if aim
            else atlas_read.get("n")
        )
        consulted = bool(dossier and lineage and live_page)
        signed = bool(aim and order)
        implied_aim = (
            int(round(
                float(lineage["anchor_price_cents"])
                - float(atlas_depth)
            ))
            if (
                consulted
                and isinstance(
                    lineage.get("anchor_price_cents"), (int, float)
                )
                and isinstance(atlas_depth, (int, float))
            )
            else None
        )
        legs[leg_id] = {
            "leg_id": leg_id,
            "ticker": leg["ticker"],
            "status": (
                "SIGNED"
                if signed
                else "CONSULTED_NOT_SIGNED"
                if consulted
                else "NOT_CONSULTED"
            ),
            "consultation": lineage or None,
            "live_page_key": live_page,
            "live_page_n": live_page_n,
            "live_atlas_depth_cents": (
                ((aim or {}).get("details", {}).get("aim_contract") or {})
                .get("atlas_depth_cents", atlas_depth)
            ),
            "atlas_implied_aim_cents": implied_aim,
            "live_path_aim_cents": (
                (aim or {}).get("details", {}).get("path_aim")
            ),
            "posted_price_cents": (
                (order or {}).get("details", {}).get("price")
            ),
            "aim_ts": (aim or {}).get("ts"),
            "order_ts": (order or {}).get("ts"),
        }
    alarms = [
        row
        for row in rows
        if row.get("event") == "wrongness_alarm"
    ]
    return {
        "event_id": game["event"],
        "category": game["category"],
        "slice": game["slice"],
        "left_ts": game["left_ts"],
        "right_ts": game["right_ts"],
        "evaluator_boundary_resolved": game[
            "evaluator_boundary_resolved"
        ],
        "evaluator_window_positive": game["evaluator_window_positive"],
        "stopped_after_initial_atlas_aims": result[
            "stopped_after_initial_atlas_aims"
        ],
        "stopped_after_initial_atlas_consultations": result[
            "stopped_after_initial_atlas_consultations"
        ],
        "initial_aim_probe_fast_clock": result[
            "initial_aim_probe_fast_clock"
        ],
        "replay_end_ts": result["replay_end_ts"],
        "first_input_break": result["first_input_break"],
        "wrongness_alarm_counts": dict(Counter(
            row.get("details", {}).get("code") for row in alarms
        )),
        "legs": legs,
    }


def no_window_probe_event(game: dict) -> dict:
    """Represent a game whose retained replay interval is non-positive."""
    return {
        "event_id": game["event"],
        "category": game["category"],
        "slice": game["slice"],
        "left_ts": game["left_ts"],
        "right_ts": game["right_ts"],
        "evaluator_boundary_resolved": game[
            "evaluator_boundary_resolved"
        ],
        "evaluator_window_positive": game["evaluator_window_positive"],
        "stopped_after_initial_atlas_aims": False,
        "stopped_after_initial_atlas_consultations": False,
        "initial_aim_probe_fast_clock": True,
        "replay_end_ts": game["left_ts"],
        "first_input_break": {
            "ts": game["left_ts"],
            "source": "REPLAY_WINDOW",
            "error": "non-positive retained replay interval",
        },
        "wrongness_alarm_counts": {},
        "legs": {
            leg["leg"]: {
                "leg_id": leg["leg"],
                "ticker": leg["ticker"],
                "status": "NO_REPLAY_WINDOW",
                "consultation": None,
                "live_page_key": None,
                "live_page_n": None,
                "live_atlas_depth_cents": None,
                "atlas_implied_aim_cents": None,
                "live_path_aim_cents": None,
                "posted_price_cents": None,
                "aim_ts": None,
                "order_ts": None,
            }
            for leg in game["legs"]
        },
    }


async def run_probe(args: argparse.Namespace) -> int:
    games = load_scope(None, allow_unresolved_boundary=True)
    if args.event:
        games = [game for game in games if game["event"] == args.event]
        if not games:
            raise StudyError(f"event not in 804-game scope: {args.event}")
    selected = [
        game
        for index, game in enumerate(games)
        if index % args.shard_count == args.shard_index
    ]
    shard_root = args.out / "probe" / (
        f"shard_{args.shard_index:02d}_of_{args.shard_count:02d}"
    )
    ranges = build_print_index(
        PRINTS,
        shard_root / "_input_index" / "prints_by_ticker.json",
    )
    receipt_path = shard_root / "CONSULTATION_PROBE.json"
    output = []
    if receipt_path.exists():
        prior = json.loads(receipt_path.read_text(encoding="utf-8"))
        if (
            prior.get("shard_index") == args.shard_index
            and prior.get("shard_count") == args.shard_count
        ):
            output = list(prior.get("rows") or [])
    completed = {row["event_id"] for row in output}
    started = time.monotonic()
    for index, game in enumerate(selected, 1):
        if game["event"] in completed:
            continue
        print(
            f"[{args.shard_index}:{index}/{len(selected)}] "
            f"{game['event']}",
            flush=True,
        )
        if game["right_ts"] <= game["left_ts"]:
            output.append(no_window_probe_event(game))
        else:
            with open(os.devnull, "w", encoding="utf-8") as sink:
                with contextlib.redirect_stdout(sink):
                    result = await replay_one(
                        game,
                        ranges,
                        shard_root / "_scratch",
                        write_trace=False,
                        capture_events=CAPTURE_EVENTS,
                        persist_engine_logs=False,
                    stop_after_initial_atlas_aims=True,
                    stop_after_initial_atlas_consultations=True,
                        initial_aim_probe_fast_clock=True,
                        hash_large_inputs=False,
                    )
            output.append(extract_probe_event(result, game))
            del result
            gc.collect()
        # Each game is expensive because it imports the real OS.  Preserve
        # completed measurements so an external timeout never erases a shard.
        payload = {
            "schema_version": "window1-atlas-consultation-probe-v1",
            "fill_model": FILL_MODEL,
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
            "events": len(output),
            "complete": len(output) == len(selected),
            "elapsed_seconds_this_process": round(
                time.monotonic() - started, 3
            ),
            "rows": output,
        }
        write_json(receipt_path, payload)
    payload = {
        "schema_version": "window1-atlas-consultation-probe-v1",
        "fill_model": FILL_MODEL,
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "events": len(output),
        "complete": len(output) == len(selected),
        "elapsed_seconds_this_process": round(
            time.monotonic() - started, 3
        ),
        "rows": output,
    }
    write_json(receipt_path, payload)
    print(json.dumps({
        "events": len(output),
        "elapsed_seconds_this_process": payload[
            "elapsed_seconds_this_process"
        ],
        "signed_legs": sum(
            leg["status"] == "SIGNED"
            for row in output
            for leg in row["legs"].values()
        ),
    }, indent=2))
    return 0


def load_probe_rows(out: Path) -> list[dict]:
    paths = sorted((out / "probe").glob(
        "shard_*_of_*/CONSULTATION_PROBE.json"
    ))
    if not paths:
        raise StudyError("no consultation probe shards found")
    rows = []
    for path in paths:
        rows.extend(json.loads(path.read_text(encoding="utf-8"))["rows"])
    by_event = {row["event_id"]: row for row in rows}
    if len(by_event) != 804:
        raise StudyError(
            f"consultation probe covers {len(by_event)} events, expected 804"
        )
    return [by_event[key] for key in sorted(by_event)]


def load_native_discovery(stream_dir: Path) -> dict[tuple[str, str], dict]:
    paths = sorted(stream_dir.glob(
        "UNSCORED_CANDIDATE_EVENT_STREAMS_*.jsonl.gz"
    ))
    if len(paths) != 4:
        raise StudyError(
            f"expected four frozen range-attack stream shards: {stream_dir}"
        )
    output = {}
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if row.get("candidate_id") != (
                    "w1_range_attack__macro_hold__combined_headroom"
                ):
                    continue
                event_id = row["event_id"]
                for leg in row["stream"]["evidence_census_by_leg"]:
                    output[(event_id, leg["leg_id"])] = {
                        "event_id": event_id,
                        "category": row["category"],
                        "leg_id": leg["leg_id"],
                        "ticker": leg["ticker"],
                        "discovery_status": leg.get("discovery_status"),
                        "fit_discovery_price_cents": leg.get(
                            "discovery_price"
                        ),
                        "fit_page_key": leg.get("discovery_page_key"),
                        "fit_macro_target_cents": leg.get(
                            "macro_target_raw"
                        ),
                    }
    if len(output) != 1608:
        raise StudyError(
            f"native discovery covers {len(output)} legs, expected 1608"
        )
    return output


def page_bucket(page: str | None) -> str | None:
    if not page:
        return None
    bucket = page.rsplit("|", 1)[-1]
    return bucket if bucket in BUCKETS else None


def page_role(page: str | None) -> str | None:
    if not page:
        return None
    parts = page.split("|")
    return parts[1] if len(parts) == 3 else None


def atlas_page_for_price(category: str, price: float) -> str:
    """Mirror live_v4._selector_verdict's observable page-key arithmetic."""
    side = "leader" if price >= 50 else "underdog"
    bucket = (
        "le25" if price <= 25
        else "26_50" if price <= 50
        else "51_75" if price <= 75
        else "ge75"
    )
    return f"{category}|{side}|{bucket}"


def summarize_key_rows(rows: list[dict]) -> dict:
    def group(field: str) -> dict:
        grouped = defaultdict(list)
        for row in rows:
            grouped[str(row.get(field))].append(row)
        return {
            key: {
                "legs": len(values),
                "signed_order_legs": sum(
                    value["signed_order"] for value in values
                ),
                "consult_minus_fit_price_cents": distribution(
                    value["consult_minus_fit_price_cents"]
                    for value in values
                ),
                "absolute_price_distance_cents": distribution(
                    value["absolute_price_distance_cents"]
                    for value in values
                ),
                "live_minus_fit_depth_cents": distribution(
                    value["live_minus_fit_depth_cents"]
                    for value in values
                ),
                "live_aim_minus_native_target_cents": distribution(
                    value["live_aim_minus_native_target_cents"]
                    for value in values
                ),
                "page_changed_count": sum(
                    value["page_changed"] for value in values
                ),
                "role_changed_count": sum(
                    value["role_changed"] for value in values
                ),
            }
            for key, values in sorted(grouped.items())
        }

    return {
        "all": {
            "legs": len(rows),
            "signed_order_legs": sum(
                row["signed_order"] for row in rows
            ),
            "consult_minus_fit_price_cents": distribution(
                row["consult_minus_fit_price_cents"] for row in rows
            ),
            "absolute_price_distance_cents": distribution(
                row["absolute_price_distance_cents"] for row in rows
            ),
            "live_minus_fit_depth_cents": distribution(
                row["live_minus_fit_depth_cents"] for row in rows
            ),
            "live_aim_minus_native_target_cents": distribution(
                row["live_aim_minus_native_target_cents"] for row in rows
            ),
            "page_changed_count": sum(row["page_changed"] for row in rows),
            "role_changed_count": sum(row["role_changed"] for row in rows),
        },
        "by_category": group("category"),
        "by_fit_page": group("fit_page_key"),
        "by_live_page": group("live_page_key"),
    }


def build_price_displacement_census(
    probes: list[dict],
    native: dict[tuple[str, str], dict],
    atlas: dict,
) -> tuple[dict, list[dict]]:
    """Measure price-key displacement before imposing page/target joins."""
    rows = []
    status = Counter()
    for probe in probes:
        for leg_id, live in probe["legs"].items():
            status["LEGS"] += 1
            status[live["status"]] += 1
            fit = native[(probe["event_id"], leg_id)]
            consultation = live.get("consultation") or {}
            consult_price = consultation.get("anchor_price_cents")
            fit_price = fit.get("fit_discovery_price_cents")
            if not isinstance(consult_price, (int, float)):
                status["CONSULT_PRICE_MISSING"] += 1
                continue
            if not isinstance(fit_price, (int, float)):
                status["FIT_DISCOVERY_PRICE_MISSING"] += 1
                continue
            native_fit_page = fit.get("fit_page_key")
            fit_page = atlas_page_for_price(
                probe["category"], float(fit_price)
            )
            live_page = live.get("live_page_key")
            fit_depth = (
                (atlas.get(fit_page, {}).get("bottom") or {})
                .get("depth_p50")
            )
            live_depth = (
                (atlas.get(live_page, {}).get("bottom") or {})
                .get("depth_p50")
            )
            depth_error = (
                float(live_depth) - float(fit_depth)
                if (
                    isinstance(live_depth, (int, float))
                    and isinstance(fit_depth, (int, float))
                )
                else None
            )
            implied_aim_error = (
                (
                    float(consult_price) - float(live_depth)
                ) - (
                    float(fit_price) - float(fit_depth)
                )
                if depth_error is not None
                else None
            )
            fit_cell = int(round(float(fit_price)))
            live_cell = int(round(float(consult_price)))
            rows.append({
                "event_id": probe["event_id"],
                "category": probe["category"],
                "leg_id": leg_id,
                "ticker": live["ticker"],
                "signed_order": live["status"] == "SIGNED",
                "fit_discovery_price_cents": fit_price,
                "consult_price_cents": consult_price,
                "fit_one_cent_cell": fit_cell,
                "live_one_cent_cell": live_cell,
                "fit_cell_key": f"{probe['category']}|{fit_cell:02d}",
                "live_cell_key": f"{probe['category']}|{live_cell:02d}",
                "consult_minus_fit_price_cents": (
                    float(consult_price) - float(fit_price)
                ),
                "absolute_price_distance_cents": abs(
                    float(consult_price) - float(fit_price)
                ),
                "one_cent_cell_distance": live_cell - fit_cell,
                "native_fit_page_key": native_fit_page,
                "derived_fit_atlas_page_key": fit_page,
                "fit_page_key": fit_page,
                "live_page_key": live_page,
                "page_changed": (
                    fit_page != live_page
                    if fit_page is not None and live_page is not None
                    else None
                ),
                "fit_depth_p50_cents": fit_depth,
                "live_depth_p50_cents": live_depth,
                "live_minus_fit_depth_cents": depth_error,
                "implied_aim_error_cents": implied_aim_error,
            })
            status["PRICE_DISTANCE_MEASURED"] += 1
            if depth_error is not None:
                status["DEPTH_ERROR_MEASURED"] += 1

    def summary(values: list[dict]) -> dict:
        depth = [
            row["live_minus_fit_depth_cents"]
            for row in values
            if row["live_minus_fit_depth_cents"] is not None
        ]
        aim = [
            row["implied_aim_error_cents"]
            for row in values
            if row["implied_aim_error_cents"] is not None
        ]
        return {
            "legs": len(values),
            "signed_order_legs": sum(
                row["signed_order"] for row in values
            ),
            "consult_minus_fit_price_cents": distribution(
                row["consult_minus_fit_price_cents"] for row in values
            ),
            "absolute_price_distance_cents": distribution(
                row["absolute_price_distance_cents"] for row in values
            ),
            "one_cent_cell_distance": distribution(
                row["one_cent_cell_distance"] for row in values
            ),
            "page_changed_count": sum(
                row["page_changed"] is True for row in values
            ),
            "page_comparable_legs": sum(
                row["page_changed"] is not None for row in values
            ),
            "live_minus_fit_depth_cents": distribution(depth),
            "implied_aim_error_cents": distribution(aim),
        }

    def grouped(field: str) -> dict:
        groups = defaultdict(list)
        for row in rows:
            groups[str(row.get(field))].append(row)
        return {
            key: summary(values)
            for key, values in sorted(groups.items())
        }

    return {
        "status": dict(status),
        "all": summary(rows),
        "by_category": grouped("category"),
        "by_fit_one_cent_cell": grouped("fit_cell_key"),
        "by_live_one_cent_cell": grouped("live_cell_key"),
        "by_fit_atlas_page": grouped("fit_page_key"),
    }, rows


def table_free_target(mode: str, consultation: dict) -> int | None:
    bid = consultation.get("best_bid_cents")
    ask = consultation.get("best_ask_cents")
    if not isinstance(bid, int) or not isinstance(ask, int):
        return None
    spread = ask - bid
    if bid <= 0 or ask >= 100 or spread <= 0:
        return None
    if mode == "JOIN":
        value = bid
    elif mode == "TOUCH_MINUS_1":
        value = bid - 1
    elif mode == "ONE_SPREAD_BELOW_MID":
        value = math.floor((bid + ask) / 2.0 - spread)
    else:
        raise KeyError(mode)
    return max(1, int(value))


def first_touch(
    target: int,
    consultation_ts: float,
    prints: list[dict],
    ticks: list[dict],
) -> dict | None:
    candidates = []
    for row in prints:
        if row["ts"] >= consultation_ts and row["price"] <= target:
            candidates.append({
                "ts": row["ts"],
                "trigger": "trade_print",
                "observed_price_cents": row["price"],
            })
            break
    for row in ticks:
        asks = row.get("asks") or []
        best_ask = min((int(level[0]) for level in asks), default=None)
        if (
            row["ts"] >= consultation_ts
            and best_ask is not None
            and best_ask <= target
        ):
            candidates.append({
                "ts": row["ts"],
                "trigger": "book_cross",
                "observed_price_cents": best_ask,
            })
            break
    if not candidates:
        return None
    return min(candidates, key=lambda row: row["ts"])


def evaluate_wider(
    probes: list[dict],
    native: dict[tuple[str, str], dict],
    out: Path,
) -> dict:
    games = {
        game["event"]: game
        for game in load_scope(None, allow_unresolved_boundary=True)
    }
    ranges = build_print_index(
        PRINTS,
        out / "_input_index" / "prints_by_ticker.json",
    )
    grid = {
        game["event_id"]: game
        for game in json.loads(GRID_PATH.read_text(encoding="utf-8"))["games"]
    }
    event_rows = []
    mode_totals = {
        mode: Counter() for mode in INTERIM_MODES
    }
    for probe in probes:
        event_id = probe["event_id"]
        game = games[event_id]
        grid_game = grid[event_id]
        tape = {}
        for leg in game["legs"]:
            ticker = leg["ticker"]
            prints, _ = load_print_block(
                ticker,
                ranges,
                game["left_ts"],
                game["right_ts"],
            )
            ticks, _ = load_tick_block(
                ticker,
                game["left_ts"],
                game["right_ts"],
            )
            tape[leg["leg"]] = (prints, ticks)
        modes = {}
        for mode in INTERIM_MODES:
            if not probe["evaluator_window_positive"]:
                modes[mode] = {
                    "status": "UNMEASURABLE_EVALUATOR_WINDOW",
                    "targets": {},
                    "no_target_legs": sorted(probe["legs"]),
                    "fills": {},
                    "pair_completed": False,
                    "deltas_to_window1_close_cents": {},
                    "combined_delta_to_window1_close_cents": None,
                }
                mode_totals[mode]["events"] += 1
                mode_totals[mode]["unmeasurable_window"] += 1
                continue
            ordered = sorted(
                probe["legs"].values(),
                key=lambda row: (
                    row.get("order_ts") or float("inf"),
                    row["leg_id"],
                ),
            )
            targets = {}
            no_target = []
            for row in ordered:
                if row["status"] not in {
                    "SIGNED", "CONSULTED_NOT_SIGNED"
                }:
                    no_target.append(row["leg_id"])
                    continue
                if mode == "ATLAS":
                    target = row.get("atlas_implied_aim_cents")
                else:
                    target = table_free_target(
                        mode, row.get("consultation") or {}
                    )
                    if target is not None and targets:
                        target = min(
                            target,
                            97 - next(iter(targets.values())),
                        )
                if target is None or not 5 <= int(target) <= 95:
                    no_target.append(row["leg_id"])
                    continue
                targets[row["leg_id"]] = int(target)
            fills = {}
            deltas = {}
            for leg_id, target in targets.items():
                consultation = probe["legs"][leg_id]["consultation"]
                touch = first_touch(
                    target,
                    float(consultation["consulted_at_ts"]),
                    *tape[leg_id],
                )
                fills[leg_id] = {
                    "filled": touch is not None,
                    "target_cents": target,
                    "touch": touch,
                }
                close = (
                    grid_game["legs"][leg_id]["price_path"]["close"]
                    .get("price_cents")
                )
                deltas[leg_id] = (
                    target - int(close)
                    if touch is not None and isinstance(close, int)
                    else None
                )
            completed = (
                len(fills) == 2
                and all(row["filled"] for row in fills.values())
            )
            combined_delta = (
                sum(deltas.values())
                if completed and all(
                    value is not None for value in deltas.values()
                )
                else None
            )
            modes[mode] = {
                "targets": targets,
                "no_target_legs": no_target,
                "fills": fills,
                "pair_completed": completed,
                "deltas_to_window1_close_cents": deltas,
                "combined_delta_to_window1_close_cents": combined_delta,
            }
            total = mode_totals[mode]
            total["events"] += 1
            total["measurable_both_legs"] += int(len(targets) == 2)
            total["legs_targeted"] += len(targets)
            total["legs_filled"] += sum(
                row["filled"] for row in fills.values()
            )
            total["pair_completions"] += int(completed)
            total["negative_combined_delta_completions"] += int(
                combined_delta is not None and combined_delta < 0
            )
            total["both_legs_negative_close_delta"] += int(
                completed
                and len(deltas) == 2
                and all(
                    value is not None and value < 0
                    for value in deltas.values()
                )
            )
        event_rows.append({
            "event_id": event_id,
            "category": probe["category"],
            "modes": modes,
        })
    return {
        "fill_model": FILL_MODEL,
        "pair_cap_cents": 97,
        "scope_events": 804,
        "summary": {
            mode: dict(total)
            for mode, total in mode_totals.items()
        },
        "events": event_rows,
    }


def build_key_census(
    probes: list[dict],
    native: dict[tuple[str, str], dict],
    atlas: dict,
) -> tuple[dict, list[dict]]:
    rows = []
    live_status = Counter()
    join_status = Counter()
    incomplete_reasons = Counter()
    alarm_counts = Counter()
    for probe in probes:
        alarm_counts.update(probe["wrongness_alarm_counts"])
        for leg_id, live in probe["legs"].items():
            fit = native[(probe["event_id"], leg_id)]
            live_status[live["status"]] += 1
            if live["status"] not in {
                "SIGNED", "CONSULTED_NOT_SIGNED"
            }:
                join_status["NO_CONSULTATION"] += 1
                continue
            consult = live.get("consultation") or {}
            consult_price = consult.get("anchor_price_cents")
            fit_price = fit.get("fit_discovery_price_cents")
            fit_page = fit.get("fit_page_key")
            live_page = live.get("live_page_key")
            failures = []
            if not isinstance(consult_price, (int, float)):
                failures.append("CONSULT_PRICE_MISSING")
            if not isinstance(fit_price, (int, float)):
                failures.append("FIT_DISCOVERY_PRICE_MISSING")
            if fit_page not in atlas:
                failures.append("FIT_PAGE_NOT_IN_ATLAS")
            if live_page not in atlas:
                failures.append("LIVE_PAGE_NOT_IN_ATLAS")
            if not isinstance(
                live.get("atlas_implied_aim_cents"), (int, float)
            ):
                failures.append("ATLAS_IMPLIED_AIM_MISSING")
            if not isinstance(
                fit.get("fit_macro_target_cents"), (int, float)
            ):
                failures.append("FIT_MACRO_TARGET_MISSING")
            if failures:
                join_status["INCOMPLETE_JOIN"] += 1
                incomplete_reasons.update(failures)
                continue
            fit_depth = atlas[fit_page]["bottom"]["depth_p50"]
            live_depth = atlas[live_page]["bottom"]["depth_p50"]
            fit_bucket = page_bucket(fit_page)
            live_bucket = page_bucket(live_page)
            bucket_distance = (
                BUCKETS.index(live_bucket) - BUCKETS.index(fit_bucket)
                if fit_bucket in BUCKETS and live_bucket in BUCKETS
                else None
            )
            row = {
                **fit,
                "consulted_at_ts": consult.get("consulted_at_ts"),
                "consult_anchor_source": consult.get("anchor_source"),
                "consult_price_cents": consult_price,
                "consult_bid_cents": consult.get("best_bid_cents"),
                "consult_ask_cents": consult.get("best_ask_cents"),
                "live_page_key": live_page,
                "live_page_n": live.get("live_page_n"),
                "live_path_aim_cents": live.get("live_path_aim_cents"),
                "atlas_implied_aim_cents": live.get(
                    "atlas_implied_aim_cents"
                ),
                "posted_price_cents": live.get("posted_price_cents"),
                "signed_order": live["status"] == "SIGNED",
                "fit_depth_p50_cents": fit_depth,
                "live_depth_p50_cents": live_depth,
                "consult_minus_fit_price_cents": (
                    consult_price - float(fit_price)
                ),
                "absolute_price_distance_cents": abs(
                    consult_price - float(fit_price)
                ),
                "live_minus_fit_depth_cents": (
                    float(live_depth) - float(fit_depth)
                ),
                "live_aim_minus_native_target_cents": (
                    int(live["atlas_implied_aim_cents"])
                    - int(fit["fit_macro_target_cents"])
                ),
                "page_changed": live_page != fit_page,
                "role_changed": (
                    page_role(live_page) != page_role(fit_page)
                ),
                "bucket_distance": bucket_distance,
            }
            rows.append(row)
            join_status["MEASURED"] += 1
    return {
        "scope": {
            "events": len(probes),
            "legs": sum(len(row["legs"]) for row in probes),
            "live_status": dict(live_status),
            "join_status": dict(join_status),
            "incomplete_reason_counts": dict(incomplete_reasons),
        },
        "wrongness_alarm_counts_during_probe": dict(alarm_counts),
        "distributions": summarize_key_rows(rows),
        "bucket_distance_counts": dict(Counter(
            str(row["bucket_distance"]) for row in rows
        )),
    }, rows


async def run_five(args: argparse.Namespace) -> int:
    selection = json.loads(FIVE_SELECTION.read_text(encoding="utf-8"))
    grid = {
        game["event_id"]: game
        for game in json.loads(GRID_PATH.read_text(encoding="utf-8"))["games"]
    }
    event_ids = [
        row["event_id"]
        for row in selection.get("games", selection.get("events", []))
    ]
    if not event_ids:
        event_ids = list(selection.get("event_ids") or [])
    ranges = build_print_index(
        PRINTS,
        args.out / "five_game_exact" / "_input_index"
        / "prints_by_ticker.json",
    )
    results = {}
    started = time.monotonic()
    for mode in INTERIM_MODES:
        mode_rows = []
        for index, event_id in enumerate(event_ids, 1):
            print(
                f"[five:{mode}:{index}/{len(event_ids)}] {event_id}",
                flush=True,
            )
            game = load_scope(event_id)[0]
            with open(os.devnull, "w", encoding="utf-8") as sink:
                with contextlib.redirect_stdout(sink):
                    result = await replay_one(
                        game,
                        ranges,
                        args.out / "five_game_exact" / mode,
                        counterfactual={
                            "kind": "interim_entry_aim_mode",
                            "mode": mode,
                        },
                        write_trace=False,
                        capture_events=CAPTURE_EVENTS,
                        persist_engine_logs=False,
                        hash_large_inputs=False,
                    )
            legs = {}
            leg_deltas = {}
            for leg in game["legs"]:
                leg_id = leg["leg"]
                position = result["positions"][leg_id]
                aim = first_trace(
                    result["trace"], "trendpath_live_aim", leg_id
                )
                order = first_trace(
                    result["trace"], "order_placed", leg_id
                )
                fill = first_trace(
                    result["trace"], "paper_fill", leg_id
                )
                fill_details = (fill or {}).get("details") or {}
                fill_price = fill_details.get("fill_price")
                if fill_price is None:
                    fill_price = fill_details.get("price")
                close = (
                    grid[event_id]["legs"][leg_id]["price_path"]["close"]
                    .get("price_cents")
                )
                delta = (
                    int(fill_price) - int(close)
                    if (
                        position["filled"]
                        and isinstance(fill_price, (int, float))
                        and isinstance(close, (int, float))
                    )
                    else None
                )
                leg_deltas[leg_id] = delta
                legs[leg_id] = {
                    "aim": (aim or {}).get("details"),
                    "order": (order or {}).get("details"),
                    "fill": fill_details or None,
                    "filled": position["filled"],
                    "window1_close_cents": close,
                    "fill_minus_window1_close_cents": delta,
                }
            combined_delta = (
                sum(leg_deltas.values())
                if result["pair_completed"]
                and all(value is not None for value in leg_deltas.values())
                else None
            )
            mode_rows.append({
                "event_id": event_id,
                "category": game["category"],
                "pair_completed": result["pair_completed"],
                "combined_delta_to_window1_close_cents": combined_delta,
                "both_legs_negative_close_delta": (
                    combined_delta is not None
                    and all(value < 0 for value in leg_deltas.values())
                ),
                "legs": legs,
                "wrongness_alarm_counts": dict(Counter(
                    row.get("details", {}).get("code")
                    for row in result["trace"]
                    if row.get("event") == "wrongness_alarm"
                )),
            })
        results[mode] = {
            "events": mode_rows,
            "pair_completions": sum(
                row["pair_completed"] for row in mode_rows
            ),
            "legs_filled": sum(
                leg["filled"]
                for row in mode_rows
                for leg in row["legs"].values()
            ),
            "negative_combined_delta_completions": sum(
                row["combined_delta_to_window1_close_cents"] is not None
                and row["combined_delta_to_window1_close_cents"] < 0
                for row in mode_rows
            ),
            "both_legs_negative_close_delta": sum(
                row["both_legs_negative_close_delta"]
                for row in mode_rows
            ),
        }
    payload = {
        "schema_version": "window1-atlas-interim-five-exact-v1",
        "fill_model": FILL_MODEL,
        "events": event_ids,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "modes": results,
    }
    write_json(
        args.out / "five_game_exact" / "FIVE_GAME_INTERIM_REPLAY.json",
        payload,
    )
    print(json.dumps({
        mode: {
            "pair_completions": row["pair_completions"],
            "legs_filled": row["legs_filled"],
        }
        for mode, row in results.items()
    }, indent=2))
    return 0


def run_analyze(args: argparse.Namespace) -> int:
    probes = load_probe_rows(args.out)
    native = load_native_discovery(args.range_stream_dir)
    atlas_payload = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    census, rows = build_key_census(
        probes, native, atlas_payload["pages"]
    )
    price_census, price_rows = build_price_displacement_census(
        probes, native, atlas_payload["pages"]
    )
    wider = evaluate_wider(probes, native, args.out)
    report = {
        "schema_version": "window1-atlas-key-and-interim-study-v1",
        "fill_model": FILL_MODEL,
        "atlas_fit_contract": atlas_payload.get("meta"),
        "key_mismatch_census": census,
        "key_mismatch_rows": rows,
        "price_key_displacement_census": price_census,
        "price_key_displacement_rows": price_rows,
        "interim_wider_replay": wider,
    }
    write_json(args.out / "ATLAS_KEY_AND_INTERIM_STUDY.json", report)
    print(json.dumps({
        "measured_key_rows": len(rows),
        "key_distributions": census["distributions"]["all"],
        "wrongness": census[
            "wrongness_alarm_counts_during_probe"
        ],
        "interim_summary": wider["summary"],
    }, indent=2))
    return 0


def run_keyonly(args: argparse.Namespace) -> int:
    report_path = args.out / "ATLAS_KEY_AND_INTERIM_STUDY.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    probes = load_probe_rows(args.out)
    native = load_native_discovery(args.range_stream_dir)
    atlas_payload = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    price_census, price_rows = build_price_displacement_census(
        probes, native, atlas_payload["pages"]
    )
    report["price_key_displacement_census"] = price_census
    report["price_key_displacement_rows"] = price_rows
    write_json(report_path, report)
    print(json.dumps({
        "status": price_census["status"],
        "all": price_census["all"],
    }, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        required=True,
        choices=("probe", "analyze", "keyonly", "five"),
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--range-stream-dir",
        type=Path,
        default=DEFAULT_RANGE_STREAM_DIR,
    )
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument(
        "--event",
        help="probe one event for a bounded diagnostic/benchmark",
    )
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.shard_count:
        parser.error("shard index must be inside shard count")
    return args


def main() -> int:
    args = parse_args()
    if args.mode == "probe":
        return asyncio.run(run_probe(args))
    if args.mode == "five":
        return asyncio.run(run_five(args))
    if args.mode == "keyonly":
        return run_keyonly(args)
    return run_analyze(args)


if __name__ == "__main__":
    raise SystemExit(main())
