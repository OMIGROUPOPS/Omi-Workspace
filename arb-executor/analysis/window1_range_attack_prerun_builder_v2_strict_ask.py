#!/usr/bin/env python3
"""Build the score-free strict-ask V2 range-attack streams.

The V1 builder remains immutable.  This wrapper substitutes only the V2
instrument, the FILLABLE_AT_X accounting union, and pair-opportunity lookup by
that union.  It still joins guarded boundaries only after policy generation,
never imports a scorer, and leaves C/PC/S/IC null.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import window1_range_attack_instrument_v2 as attack
import window1_range_attack_prerun_builder as v1
import window1_round4_macromicro_instrument as passed_normalizer
import window1_round2_real_capability as capability


VERSION = "window1-range-mastery-attack-prerun-v2-strict-ask"
OUTPUT_DIR = ".claude/window1_range_attack_prerun_v2_strict_ask_20260725"
FILES = v1.FILES
FreezeError = v1.FreezeError
compact = v1.compact
write_json = v1.write_json
write_jsonl_gzip = v1.write_jsonl_gzip


def _strict_ask_detail(
    leg: Mapping[str, Any],
    *,
    opened: float,
    right: float,
    target: int,
    positive: bool,
) -> dict[str, Any] | None:
    if not positive or opened > right:
        return None
    books = v1._books(leg.get("observations") or [], opened, right)
    for row in books:
        asks = row.get("asks") or []
        if asks and int(asks[0][0]) < target:
            return {
                "ts": float(row["ts"]),
                "receipt": str(row["receipt"]),
                "external_ask_price_cents": int(asks[0][0]),
                "target_price_cents": target,
            }
    return None


def evaluate_interval(
    *,
    candidate_id: str,
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    interval: Mapping[str, Any],
    boundary: Mapping[str, Any],
    taker_reach: Mapping[str, Any],
) -> dict[str, Any]:
    row = v1.evaluate_interval(
        candidate_id=candidate_id,
        event=event,
        leg=leg,
        interval=interval,
        boundary=boundary,
        taker_reach=taker_reach,
    )
    strict_ask = _strict_ask_detail(
        leg,
        opened=float(row["opened_ts"]),
        right=float(row["evaluated_right_ts"]),
        target=int(row["target_price_cents"]),
        positive=bool(boundary["positive_window1_provable"]),
    )
    print_reached = bool(row["PRICE_REACHED"])
    strict_ask_fill = strict_ask is not None
    fillable = print_reached or strict_ask_fill
    print_receipt = row.get("PRICE_REACHED_receipt")
    evidence_candidates = []
    if print_receipt is not None:
        evidence_candidates.append((
            float(print_receipt["ts"]), 1, "PRICE_REACHED", print_receipt
        ))
    if strict_ask is not None:
        # Book observations have frozen precedence over prints at equal time.
        evidence_candidates.append((
            float(strict_ask["ts"]), 0,
            "STRICT_ASK_CERTAIN_FILL", strict_ask,
        ))
    evidence_candidates.sort(key=lambda value: (value[0], value[1]))
    primary_evidence = evidence_candidates[0] if evidence_candidates else None
    row.update({
        "schema_version": VERSION + "-price-fillability-v1",
        "STRICT_ASK_CERTAIN_FILL": strict_ask_fill,
        "STRICT_ASK_CERTAIN_FILL_receipt": strict_ask,
        "FILLABLE_AT_X": fillable,
        "FILLABLE_AT_X_evidence_type": (
            primary_evidence[2] if primary_evidence else None
        ),
        "FILLABLE_AT_X_evidence": (
            primary_evidence[3] if primary_evidence else None
        ),
        "deterministic_same_timestamp_precedence": (
            "BOOK_STRICT_ASK_BEFORE_PRINT"
        ),
        "primary_price_fillability_assigns_five": fillable,
        "accounting_quantity_if_later_scored": 5 if fillable else 0,
        "accounting_fill_price_if_later_scored": (
            int(row["target_price_cents"]) if fillable else None
        ),
        "strict_ask_requires_cumulative_volume": False,
        "strict_ask_requires_displayed_depth": False,
        "strict_ask_requires_queue_clearance": False,
    })
    return row


def _process_chunk(
    repo_text: str,
    cache_text: str,
    rows: Sequence[tuple[int, Mapping[str, Any]]],
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    boundaries: Mapping[str, Mapping[str, Any]],
    candidate_ids: Sequence[str],
    source_hashes: Mapping[str, str],
) -> dict[str, Any]:
    repo = Path(repo_text)
    cache_root = Path(cache_text)
    spec = attack.load_candidate_spec(repo)
    policies = {
        candidate: attack.candidate_policy(spec, candidate)
        for candidate in candidate_ids
    }
    atlas = json.loads((repo / attack.ATLAS_PATH).read_text(encoding="utf-8"))
    guidebook = json.loads(
        (repo / attack.GUIDEBOOK_PATH).read_text(encoding="utf-8")
    )
    recut = json.loads((repo / attack.RECUT_PATH).read_text(encoding="utf-8"))
    reach = json.loads(
        (repo / attack.TAKER_REACH_PATH).read_text(encoding="utf-8")
    )
    streams, ladders, fillability, censuses = [], [], [], []
    for event_index, event in rows:
        event_id = str(event["event_id"])
        cache = capability.load_cache(cache_root / f"{event_id}.json.gz")
        normalized, census = passed_normalizer.normalize_event(
            event, cache, feature_map, corridor_seconds=0.0
        )
        census["event_id"] = event_id
        censuses.append(census)
        boundary = boundaries[event_id]
        for leg_index, leg in enumerate(normalized["legs"]):
            sibling = normalized["legs"][1 - leg_index]
            ladder = v1.build_leg_range_ladder(
                event=normalized,
                leg=leg,
                sibling=sibling,
                boundary=boundary,
            )
            ladder["event_index"] = event_index
            ladder["leg_index"] = leg_index
            ladders.append(ladder)
        for candidate_index, candidate in enumerate(candidate_ids):
            result = attack.RangeAttackSimulator(
                policies[candidate],
                atlas=atlas,
                guidebook=guidebook,
                recut=recut,
                taker_reach=reach,
                source_hashes=source_hashes,
            ).run(normalized)
            if result["metrics"] is not None or result["scored"]:
                raise FreezeError("performance metric entered policy stream")
            streams.append({
                "event_index": event_index,
                "candidate_index": candidate_index,
                "candidate_id": candidate,
                "event_id": event_id,
                "event_date": str(event["event_date"]),
                "category": str(event["category"]),
                "stream": result,
            })
            by_leg = {
                str(leg["leg_id"]): leg for leg in normalized["legs"]
            }
            for leg_id, intervals in result["order_intervals_by_leg"].items():
                for interval in intervals:
                    fillability.append(evaluate_interval(
                        candidate_id=candidate,
                        event=normalized,
                        leg=by_leg[leg_id],
                        interval=interval,
                        boundary=boundary,
                        taker_reach=reach,
                    ))
    return {
        "streams": streams,
        "ladders": ladders,
        "fillability": fillability,
        "censuses": censuses,
    }


def _fillable_ts(row: Mapping[str, Any]) -> float:
    evidence = row.get("FILLABLE_AT_X_evidence") or {}
    return float(evidence["ts"])


def _pair_opportunities(
    streams: Sequence[Mapping[str, Any]],
    fillability: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str], list[Mapping[str, Any]]] = {}
    for row in fillability:
        key = (
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        )
        by_key.setdefault(key, []).append(row)
    output = []
    for envelope in streams:
        result = envelope["stream"]
        leg_ids = list(result["order_intervals_by_leg"])
        firsts = {}
        for leg_id in leg_ids:
            rows = [
                row for row in by_key.get((
                    envelope["candidate_id"],
                    envelope["event_id"],
                    leg_id,
                ), [])
                if row["FILLABLE_AT_X"]
            ]
            rows.sort(key=lambda value: (
                _fillable_ts(value), str(value["order_interval_id"])
            ))
            firsts[leg_id] = rows[0] if rows else None
        both = all(firsts.values())
        distinct = bool(
            both and _fillable_ts(firsts[leg_ids[0]])
            != _fillable_ts(firsts[leg_ids[1]])
        )
        headroom = [
            row for row in result["order_stream"]
            if row["action"] in {"headroom_armed", "headroom_decision"}
        ]
        output.append({
            "schema_version": VERSION + "-pair-opportunity-v1",
            "candidate_id": envelope["candidate_id"],
            "event_id": envelope["event_id"],
            "event_date": envelope["event_date"],
            "category": envelope["category"],
            "D_member": True,
            "leg_fillable_at_x_opportunity": {
                leg_id: firsts[leg_id] for leg_id in leg_ids
            },
            "both_legs_have_FILLABLE_AT_X": both,
            "separately_timed_price_opportunities": distinct,
            "first_leg_identity": (
                min(
                    (leg_id for leg_id in leg_ids if firsts[leg_id]),
                    key=lambda leg_id: _fillable_ts(firsts[leg_id]),
                    default=None,
                )
            ),
            "headroom_activation_count": sum(
                row["action"] == "headroom_armed" for row in headroom
            ),
            "headroom_decision_count": sum(
                row["action"] == "headroom_decision" for row in headroom
            ),
            "accepted_sibling_headroom_count": sum(
                row.get("action_taken") is True for row in headroom
            ),
            "sibling_opportunity_inside_remaining_budget_count": sum(
                row.get("strict_guard_passed") is True
                for row in headroom if row["action"] == "headroom_decision"
            ),
            "C": None,
            "PC": None,
            "S": None,
            "IC": None,
            "metrics": None,
            "scored": False,
        })
    return output


def build(
    *,
    repo: Path,
    events_path: Path,
    cache_root: Path,
    workers: int,
) -> dict[str, Any]:
    old_attack = v1.attack
    old_process = v1._process_chunk
    old_pair = v1._pair_opportunities
    try:
        v1.attack = attack
        v1._process_chunk = _process_chunk
        v1._pair_opportunities = _pair_opportunities
        value = v1.build(
            repo=repo,
            events_path=events_path,
            cache_root=cache_root,
            workers=workers,
        )
    finally:
        v1.attack = old_attack
        v1._process_chunk = old_process
        v1._pair_opportunities = old_pair
    value["diagnostics"]["schema_version"] = VERSION + "-diagnostics-v1"
    for candidate in value["candidate_ids"]:
        rows = [
            row for row in value["fillability"]
            if row["candidate_id"] == candidate
        ]
        value["diagnostics"]["price_fillability_counts"][candidate].update({
            "STRICT_ASK_CERTAIN_FILL": sum(
                row["STRICT_ASK_CERTAIN_FILL"] for row in rows
            ),
            "FILLABLE_AT_X": sum(row["FILLABLE_AT_X"] for row in rows),
        })
    value["diagnostics"].update({
        "strict_ask_credit_before_maker_safety": True,
        "accounting_fill_union": (
            "PRICE_REACHED OR STRICT_ASK_CERTAIN_FILL"
        ),
        "all_C_PC_S_IC_null": True,
        "benchmark_or_scorer_invoked": False,
    })
    v1._assert_metrics_null(value)
    return value


def emit(output: Path, value: Mapping[str, Any]) -> None:
    v1.emit(output, value)
    write_json(output / "STRICT_ASK_ACCOUNTING_SUMMARY.json", {
        "schema_version": VERSION + "-accounting-summary-v1",
        "candidate_ids": value["candidate_ids"],
        "D_per_candidate": {
            candidate: 804 for candidate in value["candidate_ids"]
        },
        "price_fillability_counts": value["diagnostics"][
            "price_fillability_counts"
        ],
        "accounting_union": (
            "PRICE_REACHED OR STRICT_ASK_CERTAIN_FILL"
        ),
        "credit_before_maker_safety": True,
        "metrics": None,
        "scored": False,
    })


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
    output = args.output_dir if args.output_dir.is_absolute() else (
        repo / args.output_dir
    )
    value = build(
        repo=repo,
        events_path=args.events.resolve(),
        cache_root=args.market_cache.resolve(),
        workers=args.workers,
    )
    emit(output, value)
    print(compact({
        "status": "PASS_SCORE_FREE_STRICT_ASK_V2_PRE_RUN",
        "output_dir": str(output),
        "D": 804,
        "candidate_event_stream_count": 1608,
        "candidate_ids": value["candidate_ids"],
        "metrics": None,
        "scored": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

