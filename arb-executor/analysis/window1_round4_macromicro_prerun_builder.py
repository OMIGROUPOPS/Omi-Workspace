#!/usr/bin/env python3
"""Build deterministic score-free Round-4 macro×micro PRE-RUN streams."""

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
import window1_round4_macromicro_instrument as r4m
import window1_round4_instrument_v2 as v2


VERSION = "window1-round4-macromicro-real-capability-v1"
OUTPUT_FILENAMES = {
    "streams_01": "FROZEN_MACROMICRO_CANDIDATE_EVENT_STREAMS_01.jsonl.gz",
    "streams_02": "FROZEN_MACROMICRO_CANDIDATE_EVENT_STREAMS_02.jsonl.gz",
    "streams_03": "FROZEN_MACROMICRO_CANDIDATE_EVENT_STREAMS_03.jsonl.gz",
    "streams_04": "FROZEN_MACROMICRO_CANDIDATE_EVENT_STREAMS_04.jsonl.gz",
    "capability": "ROUND4_MACROMICRO_REAL_CAPABILITY.json",
    "differences": "ROUND4_MACROMICRO_ORDER_DIFFERENCES.jsonl",
    "headroom": "ROUND4_MACROMICRO_HEADROOM_RECEIPTS.jsonl.gz",
    "last_trade": "LAST_TRADE_PRESERVATION_CENSUS.json",
    "consumption": "FIELD_CONSUMPTION_RECEIPTS.jsonl.gz",
    "five_event": "FIVE_EVENT_NO_CALL_D_MEMBERSHIP_PROOF.json",
}
DECISIONS = {"place", "reprice", "cancel"}
FIVE_NO_BBO = {
    "KXATPCHALLENGERMATCH-26JUL19KRUCAS",
    "KXATPCHALLENGERMATCH-26JUL20CREMAT",
    "KXWTAMATCH-26JUL13TAUTOM",
    "KXWTAMATCH-26JUL14PUTJEA",
    "KXWTAMATCH-26JUL20KUDKOR",
}
HOLDOUT_DATES = {"2026-07-24", "2026-07-25", "2026-07-26"}


class PreRunError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def decision_signature(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    fields = (
        "leg_id", "ts", "action", "reason", "price_cents", "quantity",
        "remaining_quantity", "posture", "composed_macro_micro",
        "macro_decision_receipt", "micro_decision_receipt",
        "pair_decision_receipt",
    )
    return [
        {field: row.get(field) for field in fields}
        for row in result["order_stream"]
        if row["action"] in DECISIONS
    ]


def _first_difference(
    left: Sequence[Mapping[str, Any]],
    right: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    for index in range(max(len(left), len(right))):
        a = left[index] if index < len(left) else None
        b = right[index] if index < len(right) else None
        if a != b:
            return {
                "first_difference_index": index,
                "candidate_decision": a,
                "reference_decision": b,
            }
    raise PreRunError("identical streams have no difference")


def _process_chunk(
    repo_text: str,
    cache_text: str,
    indexed_events: Sequence[tuple[int, Mapping[str, Any]]],
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    candidate_ids: Sequence[str],
    corridor_seconds: float,
    source_receipts: Mapping[str, str],
) -> dict[str, Any]:
    repo, cache_root = Path(repo_text), Path(cache_text)
    spec = r4m.load_candidate_spec(repo)
    policies = {
        candidate: r4m.candidate_policy(spec, candidate)
        for candidate in candidate_ids
    }
    surfaces = r2.load_surfaces(repo)
    rows, censuses = [], []
    for event_index, event in indexed_events:
        event_id = str(event["event_id"])
        cache = r2cap.load_cache(cache_root / f"{event_id}.json.gz")
        normalized, census = r4m.normalize_event(
            event,
            cache,
            feature_map,
            corridor_seconds=corridor_seconds,
        )
        census.update({
            "event_id": event_id,
            "event_date": str(event["event_date"]),
        })
        censuses.append(census)
        for candidate_index, candidate in enumerate(candidate_ids):
            result = r4m.Round4MacroMicroInstrument(
                surfaces,
                policies[candidate],
                atlas={},
                source_receipts=source_receipts,
            ).run(normalized)
            if result["metrics"] is not None or result["scored"] is not False:
                raise PreRunError("performance result entered PRE-RUN")
            decisions = decision_signature(result)
            rows.append({
                "event_index": event_index,
                "candidate_index": candidate_index,
                "candidate_id": candidate,
                "event_id": event_id,
                "event_date": str(event["event_date"]),
                "category": str(event["category"]),
                "stream": result,
                "decision_signature": decisions,
                "decision_sha256": sha256_json(decisions),
            })
    return {"rows": rows, "censuses": censuses}


def _aggregate_census(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    fields = [
        "raw_snapshot_count",
        "raw_positive_last_trade_count",
        "normalized_book_count",
        "normalized_positive_last_trade_count",
        "verified_print_timestamp_count",
        "carried_execution_time_unknown_count",
        "carried_before_first_window1_print_count",
        "legs_with_carried_state_and_no_window1_print_count",
        "last_trade_created_print_count",
    ]
    return {
        "schema_version": "round4-last-trade-census-v1",
        "event_count": len(rows),
        **{
            field: sum(int(row[field]) for row in rows)
            for field in fields
        },
        "event_receipts": list(rows),
        "provenance_classes": [
            r4m.VERIFIED_PRINT,
            r4m.CARRIED_UNKNOWN,
        ],
        "last_trade_is_BBO_authority": False,
        "last_trade_is_fill_volume": False,
        "carried_observation_claims_new_execution": False,
        "constructed_midpoint_used": False,
        "metrics": None,
        "scored": False,
    }


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
    if any(str(row["event_date"]) in HOLDOUT_DATES for row in events):
        raise PreRunError("holdout date present")
    features = [
        row for row in read_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in features
    }
    if len(feature_map) != 1608:
        raise PreRunError("frozen 1,608 leg identities changed")
    spec = r4m.load_candidate_spec(repo)
    candidate_ids = list(spec["candidate_ids"])
    corridor = 0.0
    source_receipts = {
        "recut": sha256_path(repo / r4m.RECUT_PATH),
        "climb_spec": sha256_path(repo / r4m.CLIMB_SPEC_PATH),
        "granularity": sha256_path(repo / r4m.GRANULARITY_PATH),
        "expression": sha256_path(repo / r4m.EXPRESSION_PATH),
    }
    indexed = list(enumerate(events))
    worker_count = max(1, min(int(workers), len(indexed)))
    chunks = [indexed[index::worker_count] for index in range(worker_count)]
    if worker_count == 1:
        groups = [_process_chunk(
            str(repo), str(cache_root), chunks[0], feature_map,
            candidate_ids, corridor, source_receipts,
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
            groups = [future.result() for future in futures]
    rows = [row for group in groups for row in group["rows"]]
    rows.sort(key=lambda row: (
        int(row["event_index"]), int(row["candidate_index"])
    ))
    censuses = [row for group in groups for row in group["censuses"]]
    censuses.sort(key=lambda row: str(row["event_id"]))
    if len(rows) != 1608 or len(censuses) != 804:
        raise PreRunError("candidate/event conservation failed")
    identities = [
        (str(row["candidate_id"]), str(row["event_id"])) for row in rows
    ]
    if len(set(identities)) != 1608:
        raise PreRunError("candidate/event identity duplicated")
    if any(
        row["candidate_id"] != candidate_ids[row["candidate_index"]]
        for row in rows
    ):
        raise PreRunError("candidate order changed")

    by_candidate: dict[str, dict[str, Mapping[str, Any]]] = {
        candidate: {} for candidate in candidate_ids
    }
    for row in rows:
        by_candidate[row["candidate_id"]][row["event_id"]] = row
    differences = []
    base, flow = candidate_ids
    for event in events:
        event_id = str(event["event_id"])
        before = by_candidate[base][event_id]["decision_signature"]
        after = by_candidate[flow][event_id]["decision_signature"]
        if before == after:
            continue
        differences.append({
            "schema_version": "round4-macromicro-order-difference-v1",
            "event_id": event_id,
            "event_date": str(event["event_date"]),
            "candidate_id": flow,
            "reference_candidate_id": base,
            "candidate_decision_sha256": sha256_json(after),
            "reference_decision_sha256": sha256_json(before),
            **_first_difference(after, before),
            "metrics": None,
            "scored": False,
        })
    if not differences:
        raise PreRunError("composed candidates are behaviorally identical")

    candidate_summaries = []
    for candidate in candidate_ids:
        current = [
            row for row in rows if row["candidate_id"] == candidate
        ]
        actions = [
            action
            for row in current
            for action in row["stream"]["order_stream"]
        ]
        decisions = [
            action for action in actions if action["action"] in DECISIONS
        ]
        if any(
            not action.get("composed_macro_micro")
            or not action.get("macro_decision_receipt")
            or not action.get("micro_decision_receipt")
            or not action.get("pair_decision_receipt")
            for action in decisions
        ):
            raise PreRunError("decision missing composed receipts")
        candidate_summaries.append({
            "candidate_id": candidate,
            "D": 804,
            "candidate_event_stream_count": 804,
            "eligible_D_membership_count": 804,
            "decision_count": len(decisions),
            "place_count": sum(
                action["action"] == "place" for action in decisions
            ),
            "reprice_count": sum(
                action["action"] == "reprice" for action in decisions
            ),
            "cancel_count": sum(
                action["action"] == "cancel" for action in decisions
            ),
            "composed_receipt_count": len(decisions),
            "last_trade_NO_CALL_count": sum(
                action.get("reason") == r4m.LAST_TRADE_NO_CALL
                for action in actions
            ),
            "top5_NO_CALL_count": sum(
                action.get("reason") == r4m.TOP5_NO_CALL
                for action in actions
            ),
            "top20_NO_CALL_count": sum(
                action.get("reason") == r4m.TOP20_NO_CALL
                for action in actions
            ),
            "feature_censor_event_count": sum(
                row["stream"]["event_terminal"] == "censored_feature"
                for row in current
            ),
            "events_distinct_from_other_candidate": len(differences),
            "aggregate_decision_sha256": sha256_json([
                {
                    "event_id": row["event_id"],
                    "decisions": row["decision_signature"],
                }
                for row in current
            ]),
            "C": None, "PC": None, "S": None, "IC": None,
            "metrics": None, "scored": False,
        })

    consumption = []
    for row in rows:
        for action in row["stream"]["order_stream"]:
            if action["action"] not in DECISIONS:
                continue
            consumption.append({
                "candidate_id": row["candidate_id"],
                "event_id": row["event_id"],
                "leg_id": action["leg_id"],
                "action": action["action"],
                "timestamp": action["ts"],
                "macro": action["macro_decision_receipt"],
                "micro": action["micro_decision_receipt"],
                "pair": action["pair_decision_receipt"],
                "metrics": None,
                "scored": False,
            })
    five_event = []
    for row in rows:
        if row["event_id"] not in FIVE_NO_BBO:
            continue
        actions = row["stream"]["order_stream"]
        five_event.append({
            "candidate_id": row["candidate_id"],
            "event_id": row["event_id"],
            "D_member": True,
            "placement_count": sum(
                action["action"] == "place" for action in actions
            ),
            "market_evidence_NO_CALL_count": sum(
                action.get("reason") == v2_market_no_call()
                for action in actions
            ),
            "terminal_censored": (
                row["stream"]["event_terminal"] == "censored_feature"
            ),
            "metrics": None,
        })
    if len(five_event) != 10 or any(
        row["placement_count"] != 0
        or row["market_evidence_NO_CALL_count"] != 2
        or row["terminal_censored"]
        for row in five_event
    ):
        raise PreRunError("five-event no-BBO contract changed")

    headroom = [{
        "candidate_id": row["candidate_id"],
        "event_id": row["event_id"],
        **action,
    } for row in rows for action in row["stream"]["order_stream"]
    if action["action"] in {
        "headroom_partial_arm", "headroom_exact5_arm",
        "headroom_decision", "headroom_no_call",
        "causal_exact5_reference",
    }]
    return {
        "schema_version": VERSION,
        "D": 804,
        "leg_identity_count": 1608,
        "candidate_count": 2,
        "candidate_event_stream_count": 1608,
        "candidate_ids": candidate_ids,
        "development_dates": list(binding.DEV_DATES),
        "candidate_rows": rows,
        "candidate_summaries": candidate_summaries,
        "order_differences": differences,
        "headroom_receipts": headroom,
        "field_consumption_receipts": consumption,
        "last_trade_census": _aggregate_census(censuses),
        "five_event_proof": five_event,
        "source_receipts": source_receipts,
        "all_metrics_null": True,
        "scorer_imported_or_invoked": False,
        "ranking_selection_or_tuning": False,
        "holdout_opened_or_queried": False,
        "live_or_production_access": False,
    }


def v2_market_no_call() -> str:
    return v2.MARKET_EVIDENCE_NO_CALL


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
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
    value = build(
        repo=repo,
        events_path=args.events.resolve(),
        cache_root=args.market_cache.resolve(),
        workers=args.workers,
    )
    frozen_rows = [{
        "candidate_id": row["candidate_id"],
        "event_id": row["event_id"],
        "stream": row["stream"],
    } for row in value["candidate_rows"]]
    shard_size = len(frozen_rows) // 4
    if shard_size * 4 != len(frozen_rows):
        raise PreRunError("stream corpus cannot be split into four fixed shards")
    for index in range(4):
        write_gzip_jsonl(
            output / OUTPUT_FILENAMES[f"streams_{index + 1:02d}"],
            frozen_rows[index * shard_size:(index + 1) * shard_size],
        )
    write_json(output / OUTPUT_FILENAMES["capability"], {
        key: item for key, item in value.items()
        if key not in {
            "candidate_rows", "order_differences", "headroom_receipts",
            "field_consumption_receipts", "last_trade_census",
            "five_event_proof",
        }
    })
    write_jsonl(
        output / OUTPUT_FILENAMES["differences"],
        value["order_differences"],
    )
    write_gzip_jsonl(
        output / OUTPUT_FILENAMES["headroom"],
        value["headroom_receipts"],
    )
    write_json(
        output / OUTPUT_FILENAMES["last_trade"],
        value["last_trade_census"],
    )
    write_gzip_jsonl(
        output / OUTPUT_FILENAMES["consumption"],
        value["field_consumption_receipts"],
    )
    write_json(output / OUTPUT_FILENAMES["five_event"], {
        "schema_version": "round4-five-event-proof-v1",
        "rows": value["five_event_proof"],
        "row_count": len(value["five_event_proof"]),
        "all_D_members": True,
        "all_zero_placements": True,
        "all_named_market_evidence_NO_CALL": True,
        "metrics": None,
        "scored": False,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
