#!/usr/bin/env python3
"""Build Round-4 V2 score-free streams and prove the exact V1 delta."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

import window1_round4_instrument_v2 as r4v2
import window1_round4_prerun_builder as v1builder


VERSION = "window1-round4-real-capability-v2"
V1_STREAMS = (
    ".claude/window1_round4_prerun_20260725/"
    "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
)
REPAIRED_EVENTS = {
    "KXATPCHALLENGERMATCH-26JUL19KRUCAS",
    "KXATPCHALLENGERMATCH-26JUL20CREMAT",
    "KXWTAMATCH-26JUL13TAUTOM",
    "KXWTAMATCH-26JUL14PUTJEA",
    "KXWTAMATCH-26JUL20KUDKOR",
}
_V1_PROCESS_CHUNK = v1builder._process_chunk


class V2PreRunError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def _process_chunk_v2(*args: Any) -> list[dict[str, Any]]:
    original = v1builder.r4
    v1builder.r4 = r4v2
    try:
        return _V1_PROCESS_CHUNK(*args)
    finally:
        v1builder.r4 = original


def _identity_receipt(
    repo: Path, rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(rows) != 1608:
        raise V2PreRunError("candidate-event stream count changed")
    changed = []
    unchanged = 0
    with gzip.open(
        repo / V1_STREAMS, "rt", encoding="utf-8"
    ) as before_handle:
        for ordinal, row in enumerate(rows, start=1):
            line = before_handle.readline()
            if not line:
                raise V2PreRunError("V1 corpus ended early")
            before = json.loads(line)
            after = {
                "candidate_id": row["candidate_id"],
                "event_id": row["event_id"],
                "stream": row["stream"],
            }
            identity = (
                str(after["candidate_id"]), str(after["event_id"])
            )
            if identity != (
                str(before["candidate_id"]), str(before["event_id"])
            ):
                raise V2PreRunError("candidate-event order changed")
            before_bytes = compact(before).encode("utf-8")
            after_bytes = compact(after).encode("utf-8")
            if before_bytes == after_bytes:
                unchanged += 1
                continue
            actions = after["stream"]["order_stream"]
            changed.append({
                "ordinal": ordinal,
                "candidate_id": identity[0],
                "event_id": identity[1],
                "v1_wrapper_sha256": hashlib.sha256(
                    before_bytes
                ).hexdigest(),
                "v2_wrapper_sha256": hashlib.sha256(
                    after_bytes
                ).hexdigest(),
                "v1_stream_sha256": before["stream"]["stream_sha256"],
                "v2_stream_sha256": after["stream"]["stream_sha256"],
                "v1_event_terminal": before["stream"]["event_terminal"],
                "v2_event_terminal": after["stream"]["event_terminal"],
                "causal_role_NO_CALL_count": sum(
                    action["action"] == "feature_no_call"
                    and action["reason"] == r4v2.CAUSAL_ROLE_NO_CALL
                    for action in actions
                ),
                "market_evidence_NO_CALL_count": sum(
                    action["action"] == "feature_no_call"
                    and action["reason"] == r4v2.MARKET_EVIDENCE_NO_CALL
                    for action in actions
                ),
                "placement_count": sum(
                    action["action"] == "place" for action in actions
                ),
                "D_membership_continues": True,
                "metrics": None,
                "scored": False,
            })
        if before_handle.readline():
            raise V2PreRunError("V1 corpus has extra rows")
    expected = {
        (candidate, event_id)
        for candidate in r4v2.load_candidate_spec(repo)["candidate_ids"]
        for event_id in REPAIRED_EVENTS
    }
    if unchanged != 1598 or len(changed) != 10:
        raise V2PreRunError(
            f"wrong V1 delta: unchanged={unchanged} changed={len(changed)}"
        )
    if {
        (row["candidate_id"], row["event_id"]) for row in changed
    } != expected:
        raise V2PreRunError("changed-stream identity set is not exact")
    if any(
        row["v2_event_terminal"] == "censored_feature"
        or row["causal_role_NO_CALL_count"] != 2
        or row["market_evidence_NO_CALL_count"] != 2
        or row["placement_count"] != 0
        for row in changed
    ):
        raise V2PreRunError("amended Item-5 stream contract failed")
    return {
        "schema_version": "window1-round4-v1-v2-stream-identity-v2",
        "V1_prerun": (
            "4f65344672430adc51fe0a5a7e8c9279b2b354ed"
        ),
        "controlling_amendment": (
            "abe543e33bf40cf6cca14e046c40904d2de5e878"
        ),
        "candidate_event_stream_count": 1608,
        "byte_identical_to_V1_count": unchanged,
        "changed_from_V1_count": len(changed),
        "changed_streams": changed,
        "metrics": None,
        "scored": False,
    }


def build(
    *,
    repo: Path,
    events_path: Path,
    cache_root: Path,
    workers: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    original_r4 = v1builder.r4
    original_process = v1builder._process_chunk
    v1builder.r4 = r4v2
    v1builder._process_chunk = _process_chunk_v2
    try:
        value = v1builder.build(
            repo=repo,
            events_path=events_path,
            cache_root=cache_root,
            workers=workers,
        )
    finally:
        v1builder.r4 = original_r4
        v1builder._process_chunk = original_process
    value["schema_version"] = VERSION
    identity = _identity_receipt(repo, value["candidate_rows"])
    if any(
        row["eligible_event_count"] != 804
        or row["censored_event_count"] != 0
        for row in value["candidate_summaries"]
    ):
        raise V2PreRunError("D=804 actionable population failed")
    return value, identity


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    output.mkdir(parents=True, exist_ok=False)
    value, identity = build(
        repo=repo,
        events_path=args.events.resolve(),
        cache_root=args.market_cache.resolve(),
        workers=args.workers,
    )
    v1builder.write_gzip_jsonl(
        output / "FROZEN_CANDIDATE_EVENT_STREAMS_V2.jsonl.gz",
        [
            {
                "candidate_id": row["candidate_id"],
                "event_id": row["event_id"],
                "stream": row["stream"],
            }
            for row in value["candidate_rows"]
        ],
    )
    v1builder.write_json(
        output / "ROUND4_V2_REAL_CAPABILITY.json",
        {
            key: item for key, item in value.items()
            if key not in {
                "candidate_rows",
                "candidate_order_differences",
                "headroom_decision_receipts",
            }
        },
    )
    v1builder.write_jsonl(
        output / "ROUND4_V2_CANDIDATE_ORDER_DIFFERENCES.jsonl",
        value["candidate_order_differences"],
    )
    v1builder.write_gzip_jsonl(
        output / "ROUND4_V2_HEADROOM_DECISION_RECEIPTS.jsonl.gz",
        value["headroom_decision_receipts"],
    )
    v1builder.write_json(
        output / "ROUND4_V1_V2_STREAM_IDENTITY_RECEIPT.json",
        identity,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
