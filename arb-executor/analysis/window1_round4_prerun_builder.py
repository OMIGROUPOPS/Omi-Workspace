#!/usr/bin/env python3
"""Build the score-free Round-4 real-input PRE-RUN stream freeze.

The builder consumes the already bound July 12-20 D=804 development evidence,
emits exactly two candidate streams in manifest order, and proves real-event
decision distinctness.  It never imports or invokes a scorer.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

import window1_round2_data_binding as binding
import window1_round2_instrument as r2
import window1_round2_real_capability as r2cap
import window1_round3_prerun_builder as r3builder
import window1_round4_instrument as r4


VERSION = "window1-round4-real-capability-v1"
DECISION_ACTIONS = {"place", "reprice", "cancel"}


class PreRunError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(compact(value).encode("utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def decision_signature(
    result: Mapping[str, Any],
) -> list[dict[str, Any]]:
    fields = (
        "leg_id",
        "ts",
        "action",
        "reason",
        "price_cents",
        "quantity",
        "remaining_quantity",
        "queue_ahead",
    )
    return [
        {field: row.get(field) for field in fields}
        for row in result["order_stream"]
        if row["action"] in DECISION_ACTIONS
    ]


def _first_difference(
    left: Sequence[Mapping[str, Any]],
    right: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    count = max(len(left), len(right))
    for index in range(count):
        a = left[index] if index < len(left) else None
        b = right[index] if index < len(right) else None
        if a != b:
            return {
                "first_difference_index": index,
                "candidate_decision": a,
                "reference_decision": b,
            }
    raise PreRunError("difference requested for identical decisions")


def summarize_stream(
    result: Mapping[str, Any],
    normalized_event: Mapping[str, Any],
) -> dict[str, Any]:
    actions = list(result["order_stream"])
    action_counts = Counter(str(row["action"]) for row in actions)
    reason_counts = Counter(str(row["reason"]) for row in actions)
    terminals = [
        row for row in actions if row["action"] == "terminal"
    ]
    censors = sorted({
        str(value)
        for row in actions
        if row["action"] == "feature_censor"
        for value in (
            row.get("missing_features") or [row.get("reason")]
        )
    })
    return {
        "event_id": str(result["event_id"]),
        "event_date": str(result["event_date"]),
        "category": str(normalized_event["category"]),
        "eligible": result["event_terminal"] != "censored_feature",
        "feature_censors": censors,
        "decision_count": len(decision_signature(result)),
        "decision_sha256": sha256_json(decision_signature(result)),
        "stream_sha256": str(result["stream_sha256"]),
        "action_counts": dict(sorted(action_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "both_legs_present": len({
            row["leg_id"] for row in actions if row["action"] == "place"
        }) == 2,
        "headroom_exact5_arm_count": int(
            action_counts["headroom_exact5_arm"]
        ),
        "headroom_decision_count": int(
            action_counts["headroom_decision"]
        ),
        "headroom_action_count": sum(
            row["action"] == "headroom_decision"
            and row.get("action_taken") is True
            for row in actions
        ),
        "partial_arm_count": int(action_counts["headroom_partial_arm"]),
        "cohort_no_call_count": int(action_counts["cohort_no_call"]),
        "feature_no_call_count": int(action_counts["feature_no_call"]),
        "microdivot_count": int(action_counts["micro_divot"]),
        "positive_size_print_count_consumed": sum(
            int(row.get("positive_prints_consumed") or 0)
            for row in result.get("evidence_census_by_leg") or []
        ),
        "BBO_covered_legs": sum(
            any(
                observation["kind"] == "book"
                for observation in leg["observations"]
            )
            for leg in normalized_event["legs"]
        ),
        "top5_covered_legs": sum(
            leg["feature_availability"].get("top5") is True
            for leg in normalized_event["legs"]
        ),
        "terminal_classes": dict(sorted(Counter(
            str(row["reason"]) for row in terminals
        ).items())),
        "metrics": None,
        "scored": False,
    }


def _process_chunk(
    repo_text: str,
    cache_text: str,
    indexed_events: Sequence[tuple[int, Mapping[str, Any]]],
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    candidate_ids: Sequence[str],
    corridor_seconds: float,
    source_receipts: Mapping[str, str],
) -> list[dict[str, Any]]:
    repo = Path(repo_text)
    cache_root = Path(cache_text)
    spec = r4.load_candidate_spec(repo)
    policies = {
        candidate: r4.candidate_policy(spec, candidate)
        for candidate in candidate_ids
    }
    surfaces = r2.load_surfaces(repo)
    atlas = r4.load_atlas(repo)
    output: list[dict[str, Any]] = []
    for event_index, event in indexed_events:
        event_id = str(event["event_id"])
        cache = r2cap.load_cache(cache_root / f"{event_id}.json.gz")
        normalized = r2cap.normalize_event(
            event,
            cache,
            feature_map,
            corridor_seconds=corridor_seconds,
        )
        r3builder.bind_round3_book_receipts(normalized)
        for candidate_index, candidate in enumerate(candidate_ids):
            result = r4.Round4Instrument(
                surfaces,
                policies[candidate],
                atlas=atlas,
                source_receipts=source_receipts,
            ).run(normalized)
            if result["scored"] or result["metrics"] is not None:
                raise PreRunError("policy stream unexpectedly scored")
            output.append({
                "event_index": event_index,
                "candidate_index": candidate_index,
                "candidate_id": candidate,
                "event_id": event_id,
                "stream": result,
                "summary": summarize_stream(result, normalized),
            })
    return output


def build(
    *,
    repo: Path,
    events_path: Path,
    cache_root: Path,
    workers: int,
) -> dict[str, Any]:
    events = read_jsonl(events_path)
    if len(events) != binding.D_REQUIRED:
        raise PreRunError(f"D changed: {len(events)}")
    dates = sorted({str(row["event_date"]) for row in events})
    if dates != list(binding.DEV_DATES):
        raise PreRunError(f"development dates changed: {dates}")
    if any(str(row["event_date"]).startswith("2026-07-2") and str(
        row["event_date"]
    ) not in binding.DEV_DATES for row in events):
        raise PreRunError("non-development or holdout date present")

    features = [
        row for row in read_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in features
    }
    if len(feature_map) != 2 * binding.D_REQUIRED:
        raise PreRunError("1,608 frozen leg identities not found")

    spec = r4.load_candidate_spec(repo)
    candidate_ids = list(map(str, spec["candidate_ids"]))
    if candidate_ids != [
        "r4_pair_presence__park_join__causal_headroom_ladder",
        "r4_full_drift_stack__causal_headroom_ladder",
    ]:
        raise PreRunError("Round-4 candidate order changed")
    corridor = float(
        spec["common_parameters"]["policy_corridor_seconds_after_anchor"]
    )
    source_receipts = {
        "drift": sha256_path(repo / r4.DRIFT_PATH),
        "atlas": sha256_path(repo / r4.ATLAS_PATH),
    }

    indexed = list(enumerate(events))
    worker_count = max(1, min(int(workers), len(indexed)))
    chunks = [indexed[index::worker_count] for index in range(worker_count)]
    if worker_count == 1:
        outputs = [_process_chunk(
            str(repo),
            str(cache_root),
            chunks[0],
            feature_map,
            candidate_ids,
            corridor,
            source_receipts,
        )]
    else:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=worker_count
        ) as executor:
            futures = [
                executor.submit(
                    _process_chunk,
                    str(repo),
                    str(cache_root),
                    chunk,
                    feature_map,
                    candidate_ids,
                    corridor,
                    source_receipts,
                )
                for chunk in chunks
            ]
            outputs = [future.result() for future in futures]
    rows = [row for group in outputs for row in group]
    rows.sort(key=lambda row: (
        int(row["event_index"]), int(row["candidate_index"])
    ))
    expected = binding.D_REQUIRED * len(candidate_ids)
    if len(rows) != expected:
        raise PreRunError(
            f"candidate-event conservation failed: {len(rows)} != {expected}"
        )
    if any(
        row["candidate_id"]
        != candidate_ids[int(row["candidate_index"])]
        for row in rows
    ):
        raise PreRunError("candidate ordering changed")
    identities = [
        (str(row["candidate_id"]), str(row["event_id"])) for row in rows
    ]
    if len(set(identities)) != expected:
        raise PreRunError("candidate-event identity duplicated")

    streams: dict[str, dict[str, Mapping[str, Any]]] = {
        candidate: {} for candidate in candidate_ids
    }
    summaries: dict[str, list[Mapping[str, Any]]] = {
        candidate: [] for candidate in candidate_ids
    }
    for row in rows:
        candidate = str(row["candidate_id"])
        event_id = str(row["event_id"])
        streams[candidate][event_id] = row["stream"]
        summaries[candidate].append(row["summary"])

    aggregate_hashes = {
        candidate: sha256_json([
            {
                "event_id": event_id,
                "decisions": decision_signature(
                    streams[candidate][event_id]
                ),
            }
            for event_id in sorted(streams[candidate])
        ])
        for candidate in candidate_ids
    }
    if len(set(aggregate_hashes.values())) != 2:
        raise PreRunError("Round-4 candidates are duplicate/inert")

    differences = []
    base, full = candidate_ids
    for event in events:
        event_id = str(event["event_id"])
        base_decisions = decision_signature(streams[base][event_id])
        full_decisions = decision_signature(streams[full][event_id])
        if base_decisions == full_decisions:
            continue
        differences.append({
            "schema_version": "window1-round4-order-difference-v1",
            "event_id": event_id,
            "event_date": str(event["event_date"]),
            "candidate_id": full,
            "reference_candidate_id": base,
            "candidate_decision_sha256": sha256_json(full_decisions),
            "reference_decision_sha256": sha256_json(base_decisions),
            **_first_difference(full_decisions, base_decisions),
            "expected_order_action_difference": True,
            "metrics": None,
            "scored": False,
        })
    if not differences:
        raise PreRunError(
            "full drift stack has no real development decision difference"
        )

    candidate_summaries = []
    for candidate in candidate_ids:
        current = summaries[candidate]
        actions: Counter[str] = Counter()
        for row in current:
            actions.update(row["action_counts"])
        candidate_summaries.append({
            "candidate_id": candidate,
            "eligible_event_count": sum(
                bool(row["eligible"]) for row in current
            ),
            "censored_event_count": sum(
                not row["eligible"] for row in current
            ),
            "censor_reasons": dict(sorted(Counter(
                reason
                for row in current
                for reason in row["feature_censors"]
            ).items())),
            "both_legs_present_event_count": sum(
                bool(row["both_legs_present"]) for row in current
            ),
            "order_decision_count": sum(
                int(row["decision_count"]) for row in current
            ),
            "place_count": int(actions["place"]),
            "reprice_count": int(actions["reprice"]),
            "cancel_count": int(actions["cancel"]),
            "partial_arm_count": int(actions["headroom_partial_arm"]),
            "headroom_exact5_arm_count": int(
                actions["headroom_exact5_arm"]
            ),
            "headroom_decision_count": int(
                actions["headroom_decision"]
            ),
            "headroom_order_change_count": sum(
                int(row["headroom_action_count"]) for row in current
            ),
            "cohort_NO_CALL_count": int(actions["cohort_no_call"]),
            "feature_NO_CALL_count": int(actions["feature_no_call"]),
            "positive_size_print_count_consumed": sum(
                int(row["positive_size_print_count_consumed"])
                for row in current
            ),
            "BBO_covered_event_count": sum(
                int(row["BBO_covered_legs"]) == 2 for row in current
            ),
            "top5_covered_event_count": sum(
                int(row["top5_covered_legs"]) == 2 for row in current
            ),
            "events_distinct_from_other_candidate": len(differences),
            "aggregate_order_decision_sha256": aggregate_hashes[candidate],
            "metrics": None,
            "scored": False,
        })
    if any(
        row["eligible_event_count"] == 0
        or row["order_decision_count"] == 0
        for row in candidate_summaries
    ):
        raise PreRunError("Round-4 real-input capability gate failed")

    headroom_receipts = [
        {
            "candidate_id": row["candidate_id"],
            "event_id": row["event_id"],
            **action,
        }
        for row in rows
        for action in row["stream"]["order_stream"]
        if action["action"] in {
            "headroom_partial_arm",
            "headroom_exact5_arm",
            "headroom_decision",
            "headroom_no_call",
            "causal_exact5_reference",
        }
    ]
    return {
        "schema_version": VERSION,
        "D": binding.D_REQUIRED,
        "leg_identity_count": 2 * binding.D_REQUIRED,
        "candidate_ids": candidate_ids,
        "candidate_count": 2,
        "candidate_event_stream_count": expected,
        "development_dates": list(binding.DEV_DATES),
        "candidate_rows": rows,
        "candidate_summaries": candidate_summaries,
        "candidate_distinctness_witness": differences[0],
        "candidate_order_differences": differences,
        "headroom_decision_receipts": headroom_receipts,
        "source_receipts": source_receipts,
        "policy_clock": {
            "evaluation_real_start_access": False,
            "window1_close_access": False,
            "statistical_tdeep_is_hard_gate": False,
            "corridor_seconds_after_anchor": corridor,
        },
        "metric_contract_changed": False,
        "candidate_scoring_performed": False,
        "performance_metrics_computed": False,
        "ranking_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "live_or_production_access": False,
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact(row) + "\n")


def write_gzip_jsonl(
    path: Path, rows: Sequence[Mapping[str, Any]],
) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0
        ) as zipped:
            with io.TextIOWrapper(
                zipped, encoding="utf-8", newline="\n"
            ) as handle:
                for row in rows:
                    handle.write(compact(row) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze score-free Round-4 real-input streams."
    )
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir
        if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    output.mkdir(parents=True, exist_ok=False)
    value = build(
        repo=repo,
        events_path=args.events.resolve(),
        cache_root=args.market_cache.resolve(),
        workers=args.workers,
    )
    write_gzip_jsonl(
        output / "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz",
        [
            {
                "candidate_id": row["candidate_id"],
                "event_id": row["event_id"],
                "stream": row["stream"],
            }
            for row in value["candidate_rows"]
        ],
    )
    write_json(
        output / "ROUND4_REAL_CAPABILITY.json",
        {
            key: item for key, item in value.items()
            if key not in {
                "candidate_rows",
                "candidate_order_differences",
                "headroom_decision_receipts",
            }
        },
    )
    write_jsonl(
        output / "ROUND4_CANDIDATE_ORDER_DIFFERENCES.jsonl",
        value["candidate_order_differences"],
    )
    write_gzip_jsonl(
        output / "ROUND4_HEADROOM_DECISION_RECEIPTS.jsonl.gz",
        value["headroom_decision_receipts"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
