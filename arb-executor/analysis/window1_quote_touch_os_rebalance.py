#!/usr/bin/env python3
"""Repack completed OS re-score rows into balanced resume shards."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from window1_live_v4_replay import (
    INSTANT_TOUCH_FILL_MODEL,
    load_scope,
)
from window1_quote_touch_os_rescore import (
    MODES,
    REQUESTED_FILL_MODELS,
    save_shard,
)


def key(row: dict) -> tuple[str, str, str]:
    return (
        row["fill_model_id"],
        row["mode"],
        row["event_id"],
    )


def canonical_work() -> list[tuple[str, str, dict]]:
    games = load_scope(None, allow_unresolved_boundary=True)
    work = [
        (fill_model, mode, game)
        for fill_model in REQUESTED_FILL_MODELS
        for mode in MODES
        for game in games
    ]
    work.extend(
        (INSTANT_TOUCH_FILL_MODEL, "ORIENTATION", game)
        for game in games
    )
    return work


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    args = parser.parse_args()
    if args.shard_count < 1:
        parser.error("shard count must be positive")

    completed = {}
    paths = sorted(
        args.source.glob("shards/shard_*_of_*/OS_RESCORE.json")
    )
    if not paths:
        raise RuntimeError("source OS re-score checkpoints are absent")
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload.get("events") or []:
            completed[key(row)] = row

    work = canonical_work()
    if len(work) != 20_904:
        raise RuntimeError(
            f"canonical work has {len(work)} rows, expected 20904"
        )
    started = time.monotonic()
    seeded = 0
    for shard_index in range(args.shard_count):
        selected = [
            item
            for index, item in enumerate(work)
            if index % args.shard_count == shard_index
        ]
        rows = [
            completed[item_key]
            for fill_model, mode, game in selected
            if (
                item_key := (
                    fill_model,
                    mode,
                    game["event"],
                )
            )
            in completed
        ]
        seeded += len(rows)
        receipt = (
            args.out
            / "shards"
            / (
                f"shard_{shard_index:02d}_of_"
                f"{args.shard_count:02d}"
            )
            / "OS_RESCORE.json"
        )
        save_shard(
            receipt,
            rows,
            shard_index=shard_index,
            shard_count=args.shard_count,
            selected_count=len(selected),
            started=started,
        )
    print(json.dumps({
        "source_checkpoint_files": len(paths),
        "seeded_unique_rows": seeded,
        "canonical_rows": len(work),
        "remaining_rows": len(work) - seeded,
        "new_shard_count": args.shard_count,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
