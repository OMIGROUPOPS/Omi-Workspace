#!/usr/bin/env python3
"""Full Window-1 quote-touch reachability and quote-divot census.

This measures the 804-game development population without changing the live
OS. A retained top quote is effective until the next retained change on that
side. For a resting YES bid at P, quote reach requires best ask <= P
continuously for the named dwell threshold. True-print reach is reported as a
separate model.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from window1_live_v4_replay import (
    PRINTS,
    build_print_index,
    load_print_block,
    load_scope,
    load_tick_block,
)
from window1_table_free_full_os_study import (
    GRID_PATH,
    load_authoritative_closes,
)


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "quote_reachability_20260730"
)
DWELL_THRESHOLDS = (10, 30, 60, 300)
DELTA_RUNG_CENTS = (1, 2, 3, 5, 10, 15, 20)


class CensusError(RuntimeError):
    pass


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def quantile(values: Iterable[float], probability: float) -> float | None:
    rows = sorted(float(value) for value in values)
    if not rows:
        return None
    position = (len(rows) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return rows[lower]
    return rows[lower] + (
        rows[upper] - rows[lower]
    ) * (position - lower)


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


def best_side(row: dict, side: str) -> int | None:
    values = [
        int(level[0])
        for level in row.get(f"{side}s") or []
        if level and isinstance(level[0], (int, float))
    ]
    if not values:
        return None
    return max(values) if side == "bid" else min(values)


def top_states(
    *,
    ticks: list[dict],
    prior_tick: dict | None,
    left_ts: float,
    right_ts: float,
) -> list[dict]:
    source = []
    if prior_tick is not None:
        source.append({
            "ts": left_ts,
            "bid": best_side(prior_tick, "bid"),
            "ask": best_side(prior_tick, "ask"),
            "source": "left_edge_visible_prior_bbo",
        })
    source.extend({
        "ts": max(left_ts, float(tick["ts"])),
        "bid": best_side(tick, "bid"),
        "ask": best_side(tick, "ask"),
        "source": "retained_bbo",
    } for tick in ticks)
    source.sort(key=lambda row: row["ts"])
    states = []
    for row in source:
        if row["ts"] > right_ts:
            continue
        if (
            states
            and states[-1]["bid"] == row["bid"]
            and states[-1]["ask"] == row["ask"]
        ):
            states[-1]["raw_rows"] += 1
            continue
        states.append({**row, "raw_rows": 1})
    for index, state in enumerate(states):
        state["end_ts"] = (
            states[index + 1]["ts"]
            if index + 1 < len(states)
            else right_ts
        )
        state["duration_seconds"] = max(
            0.0, state["end_ts"] - state["ts"]
        )
    return states


def quote_floor(
    states: list[dict],
    dwell_seconds: int,
) -> dict | None:
    """Lowest bid limit whose ask-touch condition holds continuously."""
    candidates = sorted({
        int(row["ask"])
        for row in states
        if isinstance(row.get("ask"), int)
    })
    for limit in candidates:
        spans = []
        current = None
        for row in states:
            ask = row.get("ask")
            qualifying = (
                isinstance(ask, int)
                and ask <= limit
                and row["duration_seconds"] >= 0
            )
            if not qualifying:
                if current is not None:
                    spans.append(current)
                    current = None
                continue
            if current is None:
                current = {
                    "start_ts": row["ts"],
                    "end_ts": row["end_ts"],
                    "min_ask_cents": ask,
                    "max_ask_cents": ask,
                    "state_count": 1,
                }
            else:
                current["end_ts"] = row["end_ts"]
                current["min_ask_cents"] = min(
                    current["min_ask_cents"], ask
                )
                current["max_ask_cents"] = max(
                    current["max_ask_cents"], ask
                )
                current["state_count"] += 1
        if current is not None:
            spans.append(current)
        qualifying_spans = [
            {
                **span,
                "duration_seconds": (
                    span["end_ts"] - span["start_ts"]
                ),
            }
            for span in spans
            if span["end_ts"] - span["start_ts"] >= dwell_seconds
        ]
        if qualifying_spans:
            first = min(
                qualifying_spans,
                key=lambda row: (row["start_ts"], row["end_ts"]),
            )
            longest = max(
                qualifying_spans,
                key=lambda row: (
                    row["duration_seconds"],
                    -row["start_ts"],
                ),
            )
            return {
                "resting_bid_limit_cents": limit,
                "dwell_threshold_seconds": dwell_seconds,
                "first_qualifying_span": first,
                "longest_qualifying_span": longest,
                "qualifying_span_count": len(qualifying_spans),
            }
    return None


def side_changes(states: list[dict], side: str) -> list[dict]:
    changes = []
    for state in states:
        price = state.get(side)
        if not isinstance(price, int):
            continue
        if changes and changes[-1]["price"] == price:
            continue
        changes.append({"ts": state["ts"], "price": price})
    return changes


def time_cluster(tminus_scheduled: float) -> str:
    if tminus_scheduled > 360:
        return "T_MINUS_GT_360"
    if tminus_scheduled > 240:
        return "T_MINUS_360_TO_240"
    if tminus_scheduled > 120:
        return "T_MINUS_240_TO_120"
    if tminus_scheduled >= 0:
        return "T_MINUS_120_TO_0"
    return "POST_SCHEDULE"


def down_resume_episodes(
    *,
    event_id: str,
    category: str,
    leg_id: str,
    ticker: str,
    leg_direction: str,
    side: str,
    states: list[dict],
    scheduled_ts: float,
    evaluator_right_ts: float,
) -> list[dict]:
    changes = side_changes(states, side)
    episodes = []
    index = 1
    while index < len(changes):
        if changes[index]["price"] >= changes[index - 1]["price"]:
            index += 1
            continue
        peak = changes[index - 1]
        trough = changes[index]
        cursor = index + 1
        while (
            cursor < len(changes)
            and changes[cursor]["price"] < changes[cursor - 1]["price"]
        ):
            if changes[cursor]["price"] < trough["price"]:
                trough = changes[cursor]
            cursor += 1
        if (
            cursor >= len(changes)
            or changes[cursor]["price"] <= changes[cursor - 1]["price"]
        ):
            index += 1
            continue
        resume = changes[cursor]
        recovery = next(
            (
                row
                for row in changes[cursor:]
                if row["price"] >= peak["price"]
            ),
            None,
        )
        scheduled_tminus = (
            scheduled_ts - trough["ts"]
        ) / 60.0
        evaluator_tminus = (
            evaluator_right_ts - trough["ts"]
        ) / 60.0
        episodes.append({
            "event_id": event_id,
            "category": category,
            "leg_id": leg_id,
            "ticker": ticker,
            "leg_direction": leg_direction,
            "side": side,
            "peak_price_cents": peak["price"],
            "trough_price_cents": trough["price"],
            "resume_price_cents": resume["price"],
            "depth_cents": peak["price"] - trough["price"],
            "peak_ts": peak["ts"],
            "trough_ts": trough["ts"],
            "resume_ts": resume["ts"],
            "seconds_peak_to_trough": (
                trough["ts"] - peak["ts"]
            ),
            "seconds_at_trough_before_resume": (
                resume["ts"] - trough["ts"]
            ),
            "seconds_peak_to_resume": (
                resume["ts"] - peak["ts"]
            ),
            "full_recovery_ts": (
                recovery["ts"] if recovery else None
            ),
            "tminus_scheduled_at_trough_minutes": scheduled_tminus,
            "tminus_evaluator_cutoff_at_trough_minutes": (
                evaluator_tminus
            ),
            "tminus_cluster": time_cluster(scheduled_tminus),
        })
        index = cursor + 1
    signatures = Counter(
        (
            row["side"],
            row["peak_price_cents"],
            row["trough_price_cents"],
            row["resume_price_cents"],
        )
        for row in episodes
    )
    for row in episodes:
        signature = (
            row["side"],
            row["peak_price_cents"],
            row["trough_price_cents"],
            row["resume_price_cents"],
        )
        row["repeat_count_same_leg_side_shape"] = signatures[signature]
    return episodes


def leg_direction(
    open_price: int | None,
    close_price: int | None,
) -> str:
    if not isinstance(open_price, int) or not isinstance(close_price, int):
        return "UNKNOWN"
    if close_price > open_price:
        return "CLIMBING"
    if close_price < open_price:
        return "FALLING"
    return "FLAT"


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
        "schema_version": "window1-quote-reachability-shard-v1",
        "quote_dwell_law": (
            "A retained top quote is effective until the next retained "
            "best-quote change on that leg. A resting YES bid at P is "
            "quote-reachable after best ask <= P continuously for the named "
            "threshold. No depth or size proof."
        ),
        "dwell_thresholds_seconds": list(DWELL_THRESHOLDS),
        "shard_index": shard_index,
        "shard_count": shard_count,
        "rows": len(rows),
        "selected_rows": selected_count,
        "complete": len(rows) == selected_count,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "events": rows,
    })


def run_shard(args: argparse.Namespace) -> int:
    grid = {
        row["event_id"]: row
        for row in json.loads(
            GRID_PATH.read_text(encoding="utf-8")
        )["games"]
    }
    closes = load_authoritative_closes()
    games = load_scope(None, allow_unresolved_boundary=True)
    selected = [
        game
        for index, game in enumerate(games)
        if index % args.shard_count == args.shard_index
    ]
    shard_root = args.out / "shards" / (
        f"shard_{args.shard_index:02d}_of_{args.shard_count:02d}"
    )
    receipt = shard_root / "QUOTE_REACHABILITY.json"
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
    for position, game in enumerate(selected, 1):
        if game["event"] in completed:
            continue
        print(
            f"[quote:{args.shard_index}:{position}/{len(selected)}] "
            f"{game['event']}",
            flush=True,
        )
        event_grid = grid[game["event"]]
        event_legs = {}
        event_episodes = []
        measurable = bool(game["evaluator_window_positive"])
        for leg in game["legs"]:
            leg_id = leg["leg"]
            ticker = leg["ticker"]
            close = closes.get(game["event"], {}).get(leg_id)
            grid_leg = event_grid["legs"][leg_id]
            open_price = (
                grid_leg.get("price_path", {})
                .get("open", {})
                .get("price_cents")
            )
            direction = leg_direction(open_price, close)
            if not measurable:
                event_legs[leg_id] = {
                    "ticker": ticker,
                    "available": False,
                    "reason": (
                        "unresolved evaluator boundary"
                        if not game["evaluator_boundary_resolved"]
                        else "non-positive evaluator window"
                    ),
                    "window1_open_cents": open_price,
                    "window1_close_cents": close,
                    "leg_direction": direction,
                    "print_only_floor": None,
                    "quote_touch_floors": {
                        str(value): None
                        for value in DWELL_THRESHOLDS
                    },
                    "episodes": {
                        "bid": 0,
                        "ask": 0,
                        "total": 0,
                    },
                }
                continue
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
            states = top_states(
                ticks=ticks,
                prior_tick=prior_tick,
                left_ts=game["left_ts"],
                right_ts=game["right_ts"],
            )
            print_floor = (
                min(
                    prints,
                    key=lambda row: (
                        int(row["price"]),
                        float(row["ts"]),
                    ),
                )
                if prints
                else None
            )
            quote_floors = {
                str(value): quote_floor(states, value)
                for value in DWELL_THRESHOLDS
            }
            leg_episodes = []
            for side in ("bid", "ask"):
                leg_episodes.extend(down_resume_episodes(
                    event_id=game["event"],
                    category=game["category"],
                    leg_id=leg_id,
                    ticker=ticker,
                    leg_direction=direction,
                    side=side,
                    states=states,
                    scheduled_ts=game["scheduled_start_ts"],
                    evaluator_right_ts=game["right_ts"],
                ))
            event_episodes.extend(leg_episodes)
            event_legs[leg_id] = {
                "ticker": ticker,
                "available": True,
                "reason": None,
                "left_ts": game["left_ts"],
                "right_ts": game["right_ts"],
                "scheduled_start_ts": game["scheduled_start_ts"],
                "window1_open_cents": open_price,
                "window1_close_cents": close,
                "leg_direction": direction,
                "raw_bbo_rows": len(ticks),
                "distinct_top_states": len(states),
                "true_print_rows": len(prints),
                "print_only_floor": (
                    {
                        "price_cents": int(print_floor["price"]),
                        "ts": float(print_floor["ts"]),
                    }
                    if print_floor
                    else None
                ),
                "quote_touch_floors": quote_floors,
                "episodes": {
                    "bid": sum(
                        row["side"] == "bid"
                        for row in leg_episodes
                    ),
                    "ask": sum(
                        row["side"] == "ask"
                        for row in leg_episodes
                    ),
                    "total": len(leg_episodes),
                    "repeat_signature_max": max(
                        (
                            row[
                                "repeat_count_same_leg_side_shape"
                            ]
                            for row in leg_episodes
                        ),
                        default=0,
                    ),
                },
            }
        rows.append({
            "event_id": game["event"],
            "category": game["category"],
            "slice": game["slice"],
            "evaluator_boundary_resolved": game[
                "evaluator_boundary_resolved"
            ],
            "evaluator_window_positive": measurable,
            "left_ts": game["left_ts"],
            "right_ts": game["right_ts"],
            "scheduled_start_ts": game["scheduled_start_ts"],
            "legs": event_legs,
            "episodes": event_episodes,
        })
        completed.add(game["event"])
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
    return 0


def load_shards(out: Path) -> list[dict]:
    paths = sorted(
        (out / "shards").glob(
            "shard_*_of_*/QUOTE_REACHABILITY.json"
        )
    )
    if not paths:
        raise CensusError("quote census shards are absent")
    rows = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not payload.get("complete"):
            raise CensusError(f"incomplete quote shard: {path}")
        rows.extend(payload["events"])
    by_event = {row["event_id"]: row for row in rows}
    if len(by_event) != 804:
        raise CensusError(
            f"quote census covers {len(by_event)} events, expected 804"
        )
    return [by_event[key] for key in sorted(by_event)]


def price_for_model(leg: dict, model: str) -> int | None:
    if model == "print_only":
        row = leg.get("print_only_floor") or {}
        value = row.get("price_cents")
        return int(value) if isinstance(value, int) else None

    union_with_print = model.startswith("quote_or_print_")
    quote_key = (
        model.removeprefix("quote_or_print_")
        if union_with_print
        else model.removeprefix("quote_only_")
    )
    if not quote_key.isdigit():
        raise CensusError(f"unknown reachability model: {model}")
    quote_row = (
        leg.get("quote_touch_floors", {}).get(quote_key)
        or {}
    )
    quote_value = quote_row.get("resting_bid_limit_cents")
    if not union_with_print:
        return (
            int(quote_value)
            if isinstance(quote_value, int)
            else None
        )
    print_row = leg.get("print_only_floor") or {}
    print_value = print_row.get("price_cents")
    available = [
        int(value)
        for value in (print_value, quote_value)
        if isinstance(value, int)
    ]
    if not available:
        return None
    return min(available)


def ladder_for_model(
    events: list[dict],
    model: str,
) -> dict:
    defined = []
    by_category = defaultdict(list)
    for event in events:
        deltas = []
        prices = {}
        closes = {}
        for leg_id, leg in event["legs"].items():
            price = price_for_model(leg, model)
            close = leg.get("window1_close_cents")
            if price is None or not isinstance(close, int):
                deltas = []
                break
            prices[leg_id] = price
            closes[leg_id] = close
            deltas.append(price - close)
        if len(deltas) != 2:
            continue
        row = {
            "event_id": event["event_id"],
            "category": event["category"],
            "prices": prices,
            "closes": closes,
            "leg_deltas": deltas,
            "combined_delta": sum(deltas),
        }
        defined.append(row)
        by_category[event["category"]].append(row)

    def summarize(rows: list[dict]) -> dict:
        combined = [row["combined_delta"] for row in rows]
        return {
            "available_count": len(rows),
            "negative_combined_delta_count": sum(
                value < 0 for value in combined
            ),
            "both_legs_reachable_below_own_close_count": sum(
                all(value < 0 for value in row["leg_deltas"])
                for row in rows
            ),
            "combined_delta_zero_count": sum(
                value == 0 for value in combined
            ),
            "combined_delta_positive_count": sum(
                value > 0 for value in combined
            ),
            "delta_ladder": {
                f"combined_delta_le_minus_{rung}_count": sum(
                    value <= -rung for value in combined
                )
                for rung in DELTA_RUNG_CENTS
            },
            "both_legs_ladder": {
                f"both_legs_delta_le_minus_{rung}_count": sum(
                    all(value <= -rung for value in row["leg_deltas"])
                    for row in rows
                )
                for rung in (1, 2, 3, 5, 10)
            },
        }

    result = summarize(defined)
    result["by_category"] = {
        category: summarize(rows)
        for category, rows in sorted(by_category.items())
    }
    result["event_rows"] = defined
    return result


def episode_summary(episodes: list[dict]) -> dict:
    def summarize(rows: list[dict]) -> dict:
        return {
            "episodes": len(rows),
            "unique_events": len({
                row["event_id"] for row in rows
            }),
            "unique_legs": len({
                row["ticker"] for row in rows
            }),
            "depth_cents": distribution(
                row["depth_cents"] for row in rows
            ),
            "trough_dwell_seconds": distribution(
                row["seconds_at_trough_before_resume"]
                for row in rows
            ),
            "repeat_count_same_leg_side_shape": distribution(
                row["repeat_count_same_leg_side_shape"]
                for row in rows
            ),
            "at_or_above_dwell_threshold": {
                f"{threshold}s": {
                    "episodes": len(subset),
                    "unique_events": len({
                        row["event_id"] for row in subset
                    }),
                    "unique_legs": len({
                        row["ticker"] for row in subset
                    }),
                    "depth_cents": distribution(
                        row["depth_cents"] for row in subset
                    ),
                    "tminus_scheduled_at_trough_minutes": distribution(
                        row["tminus_scheduled_at_trough_minutes"]
                        for row in subset
                    ),
                    "by_tminus_cluster": {
                        cluster: {
                            "episodes": len(cluster_rows),
                            "unique_legs": len({
                                row["ticker"]
                                for row in cluster_rows
                            }),
                        }
                        for cluster in (
                            "T_MINUS_GT_360",
                            "T_MINUS_360_TO_240",
                            "T_MINUS_240_TO_120",
                            "T_MINUS_120_TO_0",
                            "POST_SCHEDULE",
                        )
                        for cluster_rows in [[
                            row
                            for row in subset
                            if row["tminus_cluster"] == cluster
                        ]]
                    },
                }
                for threshold in DWELL_THRESHOLDS
                for subset in [[
                    row
                    for row in rows
                    if (
                        row["seconds_at_trough_before_resume"]
                        >= threshold
                    )
                ]]
            },
            "tminus_scheduled_at_trough_minutes": distribution(
                row["tminus_scheduled_at_trough_minutes"]
                for row in rows
            ),
            "tminus_evaluator_cutoff_at_trough_minutes": distribution(
                row[
                    "tminus_evaluator_cutoff_at_trough_minutes"
                ]
                for row in rows
            ),
            "by_tminus_cluster": {
                cluster: {
                    "episodes": len(subset),
                    "unique_legs": len({
                        row["ticker"] for row in subset
                    }),
                    "depth_cents": distribution(
                        row["depth_cents"] for row in subset
                    ),
                    "trough_dwell_seconds": distribution(
                        row[
                            "seconds_at_trough_before_resume"
                        ]
                        for row in subset
                    ),
                }
                for cluster in (
                    "T_MINUS_GT_360",
                    "T_MINUS_360_TO_240",
                    "T_MINUS_240_TO_120",
                    "T_MINUS_120_TO_0",
                    "POST_SCHEDULE",
                )
                if (
                    subset := [
                        row
                        for row in rows
                        if row["tminus_cluster"] == cluster
                    ]
                )
            },
        }

    by_side = {}
    for side in ("bid", "ask"):
        side_rows = [row for row in episodes if row["side"] == side]
        by_side[side] = summarize(side_rows)
        by_side[side]["by_leg_direction"] = {
            direction: summarize([
                row
                for row in side_rows
                if row["leg_direction"] == direction
            ])
            for direction in (
                "CLIMBING",
                "FALLING",
                "FLAT",
                "UNKNOWN",
            )
        }
        by_side[side]["by_category"] = {
            category: summarize([
                row
                for row in side_rows
                if row["category"] == category
            ])
            for category in sorted({
                row["category"] for row in side_rows
            })
        }
    return {
        "definition": (
            "An episode is an uninterrupted sequence of declining prices "
            "on one top-of-book side ending at the first subsequent increase. "
            "Trough dwell is trough timestamp to that first increase. Initial "
            "market-formation states are retained and separately identifiable "
            "by their extreme depth."
        ),
        "all": summarize(episodes),
        "by_side": by_side,
    }


def flatten_leg_reachability(events: list[dict]) -> list[dict]:
    rows = []
    for event in events:
        for leg_id, leg in sorted(event["legs"].items()):
            print_floor = leg.get("print_only_floor") or {}
            row = {
                "event_id": event["event_id"],
                "category": event["category"],
                "slice": event["slice"],
                "leg": leg_id,
                "ticker": leg["ticker"],
                "evaluator_window_positive": event[
                    "evaluator_window_positive"
                ],
                "left_ts": event["left_ts"],
                "right_ts": event["right_ts"],
                "scheduled_start_ts": event["scheduled_start_ts"],
                "window1_open_cents": leg.get(
                    "window1_open_cents"
                ),
                "window1_close_cents": leg.get(
                    "window1_close_cents"
                ),
                "leg_direction": leg.get("leg_direction"),
                "raw_bbo_rows": leg.get("raw_bbo_rows"),
                "distinct_top_states": leg.get(
                    "distinct_top_states"
                ),
                "true_print_rows": leg.get("true_print_rows"),
                "print_floor_cents": print_floor.get("price_cents"),
                "print_floor_ts": print_floor.get("ts"),
                "reason": leg.get("reason"),
            }
            for threshold in DWELL_THRESHOLDS:
                floor = (
                    leg.get("quote_touch_floors", {})
                    .get(str(threshold))
                    or {}
                )
                first = floor.get("first_qualifying_span") or {}
                longest = (
                    floor.get("longest_qualifying_span") or {}
                )
                prefix = f"quote_{threshold}s"
                row[f"{prefix}_floor_limit_cents"] = floor.get(
                    "resting_bid_limit_cents"
                )
                row[f"{prefix}_first_touch_ts"] = first.get(
                    "start_ts"
                )
                row[f"{prefix}_first_span_seconds"] = first.get(
                    "duration_seconds"
                )
                row[f"{prefix}_first_span_min_ask_cents"] = first.get(
                    "min_ask_cents"
                )
                row[f"{prefix}_first_span_max_ask_cents"] = first.get(
                    "max_ask_cents"
                )
                row[f"{prefix}_longest_span_seconds"] = longest.get(
                    "duration_seconds"
                )
                row[f"{prefix}_qualifying_span_count"] = floor.get(
                    "qualifying_span_count"
                )
            rows.append(row)
    return rows


def run_analyze(args: argparse.Namespace) -> int:
    events = load_shards(args.out)
    episodes = [
        episode
        for event in events
        for episode in event.pop("episodes")
    ]
    ladders = {
        "print_only": ladder_for_model(events, "print_only"),
        **{
            f"quote_only_{value}s": ladder_for_model(
                events,
                f"quote_only_{value}",
            )
            for value in DWELL_THRESHOLDS
        },
        **{
            f"quote_or_print_{value}s": ladder_for_model(
                events,
                f"quote_or_print_{value}",
            )
            for value in DWELL_THRESHOLDS
        },
    }
    reachability = {
        "schema_version": "window1-quote-reachability-census-v1",
        "population": 804,
        "measurable_positive_window": sum(
            row["evaluator_window_positive"] for row in events
        ),
        "unmeasurable": sum(
            not row["evaluator_window_positive"] for row in events
        ),
        "dwell_thresholds_seconds": list(DWELL_THRESHOLDS),
        "quote_dwell_law": (
            "A retained top quote is effective until the next retained "
            "best-quote change. For a resting YES bid at P, reach requires "
            "best ask <= P continuously for the named threshold. No depth "
            "or size proof."
        ),
        "events": events,
    }
    ladder_payload = {
        "schema_version": "window1-quote-touch-delta-ladders-v1",
        "population": 804,
        "models": {
            "print_only": (
                "minimum true print inside the measurable lawful window"
            ),
            **{
                f"quote_only_{value}s": (
                    "minimum resting bid whose opposite best ask is at or "
                    f"through it continuously for {value} seconds"
                )
                for value in DWELL_THRESHOLDS
            },
            **{
                f"quote_or_print_{value}s": (
                    "minimum of the true-print floor and the resting-bid "
                    "limit whose opposite best ask is at or through it "
                    f"continuously for {value} seconds; this is the "
                    "maker-fill union used by the corrected evaluator"
                )
                for value in DWELL_THRESHOLDS
            },
        },
        "ladders": ladders,
    }
    episode_payload = {
        "schema_version": "window1-quote-divot-census-v1",
        "population": 804,
        "episodes": len(episodes),
        "summary": episode_summary(episodes),
    }
    write_json(
        args.out / "WINDOW1_QUOTE_REACHABILITY_CENSUS.json",
        reachability,
    )
    write_json(
        args.out / "WINDOW1_QUOTE_TOUCH_LADDERS.json",
        ladder_payload,
    )
    write_json(
        args.out / "WINDOW1_QUOTE_DIVOT_CENSUS.json",
        episode_payload,
    )
    write_csv(
        args.out / "WINDOW1_QUOTE_REACHABILITY_LEGS.csv",
        flatten_leg_reachability(events),
    )
    write_csv(
        args.out / "WINDOW1_QUOTE_DIVOT_EPISODES.csv",
        episodes,
    )
    print(json.dumps({
        "population": 804,
        "measurable": reachability[
            "measurable_positive_window"
        ],
        "episodes": len(episodes),
        "ladders": {
            model: {
                key: value
                for key, value in rows.items()
                if key != "event_rows"
            }
            for model, rows in ladders.items()
        },
    }, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("shard", "analyze"),
        required=True,
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
    if args.mode == "shard":
        return run_shard(args)
    return run_analyze(args)


if __name__ == "__main__":
    raise SystemExit(main())
