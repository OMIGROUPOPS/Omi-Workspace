#!/usr/bin/env python3
"""Re-run live_v4 OS outcomes under explicit print/quote-dwell fill laws."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import gc
import hashlib
import json
import os
import shutil
import time
from collections import Counter
from pathlib import Path
from typing import Any

from window1_live_v4_replay import (
    FILL_MODEL,
    INSTANT_TOUCH_FILL_MODEL,
    LIVE_V4,
    PRINTS,
    PRINT_ONLY_FILL_MODEL,
    QUOTE_DWELL_FILL_MODELS,
    build_print_index,
    load_scope,
    replay_one,
)
from window1_table_free_full_os_study import (
    CAPTURE_EVENTS,
    EXPECTED_LIVE_V4_SHA256,
    extract_event,
    load_authoritative_closes,
    load_references,
    no_window_event,
    apply_authoritative_closes,
)


REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "quote_touch_os_rescore_20260730"
)
EXISTING_INSTANT_RESULTS = (
    REPO
    / ".claude"
    / "window1_live_v4_replay"
    / "table_free_full_os_20260730"
    / "TABLE_FREE_FULL_OS_RESULTS.json"
)
MODES = (
    "ATLAS",
    "ORIENTATION",
    "JOIN",
    "TOUCH_MINUS_1",
    "ONE_SPREAD_BELOW_MID",
)
REQUESTED_FILL_MODELS = (
    PRINT_ONLY_FILL_MODEL,
    *QUOTE_DWELL_FILL_MODELS,
)
MODEL_LABELS = {
    PRINT_ONLY_FILL_MODEL: "PRINT_ONLY",
    INSTANT_TOUCH_FILL_MODEL: "INSTANT_QUOTE_OR_PRINT",
    **{
        model: f"QUOTE_OR_PRINT_DWELL_{seconds}"
        for model, seconds in QUOTE_DWELL_FILL_MODELS.items()
    },
}


class RescoreError(RuntimeError):
    pass


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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
        "schema_version": "window1-quote-touch-os-rescore-shard-v1",
        "instrument": (
            "unchanged live_v4 OS and full replay scheduler; only initial "
            "aim mode and replay fill law vary"
        ),
        "modes": list(MODES),
        "requested_fill_models": list(REQUESTED_FILL_MODELS),
        "shard_index": shard_index,
        "shard_count": shard_count,
        "rows": len(rows),
        "selected_rows": selected_count,
        "complete": len(rows) == selected_count,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "events": rows,
    })


async def run_shard(args: argparse.Namespace) -> int:
    grid, floors, _ladder = load_references()
    games = load_scope(None, allow_unresolved_boundary=True)
    work = [
        (fill_model, mode, game)
        for fill_model in REQUESTED_FILL_MODELS
        for mode in MODES
        for game in games
    ]
    # The four table-free modes already have full-804 instant-touch results.
    # Only orientation needs an instant-touch run to complete that baseline.
    work.extend(
        (INSTANT_TOUCH_FILL_MODEL, "ORIENTATION", game)
        for game in games
    )
    selected = [
        row
        for index, row in enumerate(work)
        if index % args.shard_count == args.shard_index
    ]
    shard_root = args.out / "shards" / (
        f"shard_{args.shard_index:02d}_of_{args.shard_count:02d}"
    )
    receipt = shard_root / "OS_RESCORE.json"
    rows = []
    if receipt.exists():
        prior = json.loads(receipt.read_text(encoding="utf-8"))
        if (
            prior.get("shard_index") == args.shard_index
            and prior.get("shard_count") == args.shard_count
        ):
            rows = list(prior.get("events") or [])
    completed = {
        (
            row["fill_model_id"],
            row["mode"],
            row["event_id"],
        )
        for row in rows
    }
    ranges = build_print_index(
        PRINTS,
        shard_root / "_input_index" / "prints_by_ticker.json",
    )
    started = time.monotonic()
    scratch = shard_root / "_scratch"
    for position, (fill_model, mode, game) in enumerate(
        selected, 1
    ):
        key = (fill_model, mode, game["event"])
        if key in completed:
            continue
        print(
            f"[os:{args.shard_index}:{position}/{len(selected)}] "
            f"{MODEL_LABELS[fill_model]} {mode} {game['event']}",
            flush=True,
        )
        grid_game = grid[game["event"]]
        fillable_lows = floors.get(game["event"]) or {}
        if game["right_ts"] <= game["left_ts"]:
            row = no_window_event(
                game, mode, grid_game, fillable_lows
            )
            row["fill_model"] = fill_model
        else:
            with open(os.devnull, "w", encoding="utf-8") as sink:
                with contextlib.redirect_stdout(sink):
                    result = await replay_one(
                        game,
                        ranges,
                        scratch,
                        counterfactual={
                            "kind": "interim_entry_aim_mode",
                            "mode": mode,
                        },
                        write_trace=False,
                        capture_events=CAPTURE_EVENTS,
                        persist_engine_logs=False,
                        initial_aim_probe_fast_clock=False,
                        hash_large_inputs=False,
                        replay_fill_model=fill_model,
                    )
            row = extract_event(
                result,
                game,
                mode,
                grid_game,
                fillable_lows,
            )
            run_dir = scratch / "runs" / game["event"]
            if run_dir.exists():
                shutil.rmtree(run_dir)
            del result
            gc.collect()
        row["fill_model_id"] = fill_model
        row["fill_model_label"] = MODEL_LABELS[fill_model]
        rows.append(row)
        completed.add(key)
        if len(rows) % 20 == 0:
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


def load_new_rows(out: Path) -> list[dict]:
    paths = sorted(
        (out / "shards").glob("shard_*_of_*/OS_RESCORE.json")
    )
    if not paths:
        raise RescoreError("OS rescore shards are absent")
    rows = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not payload.get("complete"):
            raise RescoreError(f"incomplete OS rescore shard: {path}")
        rows.extend(payload["events"])
    expected = len(REQUESTED_FILL_MODELS) * len(MODES) * 804 + 804
    by_key = {
        (
            row["fill_model_id"],
            row["mode"],
            row["event_id"],
        ): row
        for row in rows
    }
    if len(by_key) != expected:
        raise RescoreError(
            f"OS rescore covers {len(by_key)} rows, expected {expected}"
        )
    return list(by_key.values())


def load_existing_instant_rows() -> list[dict]:
    payload = json.loads(
        EXISTING_INSTANT_RESULTS.read_text(encoding="utf-8")
    )
    rows = []
    for row in payload["events"]:
        copied = dict(row)
        copied["fill_model_id"] = INSTANT_TOUCH_FILL_MODEL
        copied["fill_model_label"] = MODEL_LABELS[
            INSTANT_TOUCH_FILL_MODEL
        ]
        rows.append(copied)
    expected = 4 * 804
    if len(rows) != expected:
        raise RescoreError(
            f"existing instant results contain {len(rows)}, "
            f"expected {expected}"
        )
    return rows


def summarize(rows: list[dict]) -> dict:
    completed = [row for row in rows if row["pair_completed"]]
    triggers = Counter(
        leg.get("fill_trigger") or "NO_FILL"
        for row in rows
        for leg in row["legs"].values()
    )
    return {
        "events": len(rows),
        "positive_evaluator_window": sum(
            row["evaluator_window_positive"] for row in rows
        ),
        "legs_filled": sum(
            leg["filled"]
            for row in rows
            for leg in row["legs"].values()
        ),
        "pairs_completed": len(completed),
        "negative_combined_delta": sum(
            row["negative_combined_delta"] for row in rows
        ),
        "both_legs_under_own_close": sum(
            row["both_legs_under_own_close"] for row in rows
        ),
        "fill_trigger_counts": dict(triggers),
        "by_category": {
            category: {
                "events": len(subset),
                "legs_filled": sum(
                    leg["filled"]
                    for row in subset
                    for leg in row["legs"].values()
                ),
                "pairs_completed": sum(
                    row["pair_completed"] for row in subset
                ),
                "negative_combined_delta": sum(
                    row["negative_combined_delta"] for row in subset
                ),
                "both_legs_under_own_close": sum(
                    row["both_legs_under_own_close"]
                    for row in subset
                ),
            }
            for category in sorted({
                row["category"] for row in rows
            })
            if (
                subset := [
                    row
                    for row in rows
                    if row["category"] == category
                ]
            )
        },
    }


def run_analyze(args: argparse.Namespace) -> int:
    rows = load_new_rows(args.out)
    closes = load_authoritative_closes()
    apply_authoritative_closes(rows, closes)
    requested_rows = [
        row
        for row in rows
        if row["fill_model_id"] in REQUESTED_FILL_MODELS
    ]
    current_instant_orientation = [
        row
        for row in rows
        if (
            row["fill_model_id"] == INSTANT_TOUCH_FILL_MODEL
            and row["mode"] == "ORIENTATION"
        )
    ]
    by_key = {
        (
            row["fill_model_id"],
            row["mode"],
            row["event_id"],
        ): row
        for row in requested_rows
    }
    expected = len(REQUESTED_FILL_MODELS) * len(MODES) * 804
    if len(by_key) != expected:
        raise RescoreError(
            f"combined OS rescore covers {len(by_key)}, expected {expected}"
        )
    live_hashes = sorted({
        row["live_v4_sha256"]
        for row in by_key.values()
        if row.get("live_v4_sha256")
    })
    current_live_hash = hashlib.sha256(
        LIVE_V4.read_bytes()
    ).hexdigest()
    if live_hashes != [current_live_hash]:
        raise RescoreError(
            "requested replay rows do not all match the current committed "
            f"live_v4 bytes: rows={live_hashes}, current={current_live_hash}"
        )
    historical_instant_rows = load_existing_instant_rows()
    historical_instant_hashes = sorted({
        row["live_v4_sha256"]
        for row in historical_instant_rows
        if row.get("live_v4_sha256")
    })
    ordered_models = REQUESTED_FILL_MODELS
    matrix = {
        MODEL_LABELS[model]: {
            mode: summarize([
                row
                for row in by_key.values()
                if row["fill_model_id"] == model
                and row["mode"] == mode
            ])
            for mode in MODES
        }
        for model in ordered_models
    }
    report = {
        "schema_version": "window1-quote-touch-os-rescore-v1",
        "population": 804,
        "instrument": {
            "os": "unchanged live_v4.LiveV3",
            "full_scheduler": True,
            "live_v4_sha256": live_hashes[0],
            "modes": list(MODES),
            "fill_models": {
                MODEL_LABELS[
                    INSTANT_TOUCH_FILL_MODEL
                ]: (
                    "diagnostic only: later true print or instantaneous "
                    "opposite BBO touch/pass; the historical four-mode "
                    "baseline is excluded from the comparable matrix "
                    "because it used different live_v4 bytes"
                ),
                MODEL_LABELS[PRINT_ONLY_FILL_MODEL]: (
                    "later true print at/through limit only"
                ),
                **{
                    MODEL_LABELS[model]: (
                        "later true print at/through limit immediately, or "
                        "opposite BBO at/through limit continuously for "
                        f"{seconds} seconds; when an order is posted into "
                        "an already-qualifying book, dwell starts at the "
                        "order's post timestamp"
                    )
                    for model, seconds in QUOTE_DWELL_FILL_MODELS.items()
                },
            },
            "decision_path": (
                "Every row executes unchanged live_v4 through the full "
                "scheduler. Only the named replay fill law and the already "
                "declared entry-aim mode vary."
            ),
        },
        "finding_before_recompute": (
            "The evaluator used for today's full-OS table-free results was "
            "not print-only: live_v4.PaperFillSimulator evaluated BBO crosses "
            "on every book update. This rescore adds sustained dwell and a "
            "true print-only comparator."
        ),
        "identity_separation": {
            "comparable_matrix_live_v4_sha256": current_live_hash,
            "historical_instant_baseline_live_v4_sha256": (
                historical_instant_hashes
            ),
            "historical_instant_baseline_merged": False,
            "reason": (
                "The historical instantaneous-touch file and this causal "
                "replay used different committed live_v4 bytes. Mixing them "
                "would manufacture a same-OS comparison."
            ),
            "current_bytes_instant_orientation_diagnostic": summarize(
                current_instant_orientation
            ),
        },
        "matrix": matrix,
        "events": [
            by_key[key]
            for key in sorted(
                by_key,
                key=lambda value: (
                    ordered_models.index(value[0]),
                    MODES.index(value[1]),
                    value[2],
                ),
            )
        ],
    }
    write_json(
        args.out / "WINDOW1_QUOTE_TOUCH_OS_RESCORE.json",
        report,
    )
    print(json.dumps({
        "population": 804,
        "live_v4_sha256": live_hashes[0],
        "matrix": matrix,
    }, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("run", "analyze"),
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
    if args.mode == "run":
        return asyncio.run(run_shard(args))
    return run_analyze(args)


if __name__ == "__main__":
    raise SystemExit(main())
