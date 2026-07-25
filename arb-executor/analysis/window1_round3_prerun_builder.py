#!/usr/bin/env python3
"""Build the score-free Round-3 real-input capability freeze.

The builder emits policy order streams and order-decision capability receipts
for the immutable July 12-20 D=804 population.  It intentionally never imports
or invokes the scorer and never reads evaluation-real-start truth.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import window1_round2_data_binding as binding
import window1_round2_instrument as r2
import window1_round2_real_capability as r2cap
import window1_round3_instrument as r3


VERSION = "window1-round3-real-capability-v1"
DECISION_ACTIONS = {"place", "reprice", "cancel"}
REFERENCE_BY_CANDIDATE = {
    "r3_pair_presence__park_join__hold": (
        "r3_pair_presence__touch_park__hold"
    ),
    "r3_pair_presence__park_join__reaim": (
        "r3_pair_presence__park_join__hold"
    ),
    "r3_pair_presence__touch_park__hold": (
        "r3_pair_presence__park_join__hold"
    ),
    "r3_pair_presence__touch_park__reaim": (
        "r3_pair_presence__touch_park__hold"
    ),
    "r3_causal_steer__park_join__hold": (
        "r3_pair_presence__park_join__hold"
    ),
    "r3_causal_steer__park_join__reaim": (
        "r3_causal_steer__park_join__hold"
    ),
    "r3_full_os__walk_park__hold": (
        "r3_causal_steer__park_join__hold"
    ),
    "r3_full_os__walk_park__reaim": (
        "r3_full_os__walk_park__hold"
    ),
}


class PreRunError(RuntimeError):
    """Raised when the Round-3 pre-run capability gate fails."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def bind_round3_book_receipts(
    normalized_event: Mapping[str, Any],
) -> None:
    """Bind distinct same-timestamp public books by their frozen content.

    The Round-2 adapter used ticker+timestamp, which aliases lawful
    same-second BBO transitions. Round 3 hashes the bound public snapshot
    content: exact duplicates share an identity and contribute zero, while
    distinct same-second books remain distinct causal receipts.
    """
    for leg in normalized_event["legs"]:
        ticker = str(leg["ticker"])
        for row in leg["observations"]:
            if row["kind"] != "book":
                continue
            content = {
                "ticker": ticker,
                "ts": float(row["ts"]),
                "source": str(row.get("source") or ""),
                "bids": row.get("bids") or [],
                "asks": row.get("asks") or [],
            }
            row["source_receipt_identity"] = (
                f"{ticker}|book|{float(row['ts']):.6f}|"
                f"{sha256_json(content)}"
            )


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
        "posture",
        "base_sibling_order_cents",
        "reaim_sibling_order_cents",
        "exact_reaim_difference_cents",
    )
    return [
        {field: row.get(field) for field in fields}
        for row in result["order_stream"]
        if row["action"] in DECISION_ACTIONS
    ]


def summarize_stream(
    result: Mapping[str, Any],
    normalized_event: Mapping[str, Any],
) -> dict[str, Any]:
    actions = list(result["order_stream"])
    action_counts = Counter(str(row["action"]) for row in actions)
    reason_counts = Counter(str(row["reason"]) for row in actions)
    feature_censors = sorted({
        str(value)
        for row in actions
        if row["action"] == "feature_censor"
        for value in (
            row.get("missing_features") or [row.get("reason")]
        )
    })
    decisions = decision_signature(result)
    macros = [
        row for row in actions if row["action"] == "macro_bind"
    ]
    timing_values = {
        float(row["eligible_ts"]) for row in macros
        if row.get("eligible_ts") is not None
    }
    return {
        "event_id": str(result["event_id"]),
        "event_date": str(result["event_date"]),
        "category": str(normalized_event["category"]),
        "eligible": result["event_terminal"] != "censored_feature",
        "feature_censors": feature_censors,
        "decision_count": len(decisions),
        "decision_sha256": sha256_json(decisions),
        "stream_sha256": str(result["stream_sha256"]),
        "action_counts": dict(sorted(action_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "asynchronous_presence_exercised": len(timing_values) > 1,
        "positive_print_divot_recut_exercised": any(
            row["action"] == "reprice"
            and row["reason"] == "positive_print_divot_recut"
            for row in actions
        ),
        "sibling_response_exercised": any(
            row["action"] == "sibling_reaim_applied"
            and row.get("exact_reaim_difference_cents") == 1
            for row in actions
        ),
        "walk_exercised": any(
            row["action"] == "reprice"
            and row["reason"]
            == "verified_nonself_chain_exact_one_cent"
            for row in actions
        ),
        "orientation_order_change": sum(
            row["action"] == "reprice"
            and row["reason"] == "causal_orientation_reaim"
            for row in actions
        ),
        "drift_order_change": sum(
            row["action"] == "reprice"
            and row["reason"] == "causal_T6_drift_recognition"
            for row in actions
        ),
        "cohort_call_count": int(action_counts["cohort_steer"]),
        "cohort_no_call_count": int(action_counts["cohort_no_call"]),
        "top5_no_call_count": sum(
            row["action"] == "feature_no_call"
            and row.get("family_id") == "bbo_top5_pressure"
            for row in actions
        ),
        "top5_order_change": int(
            action_counts["top5_pressure_order_effect"]
        ),
        "positive_size_print_count_consumed": sum(
            int(row.get("positive_prints_consumed") or 0)
            for row in result.get("evidence_census_by_leg") or []
        ),
        "bbo_covered_legs": sum(
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
    }


def _process_chunk(
    repo_text: str,
    cache_text: str,
    indexed_events: Sequence[tuple[int, Mapping[str, Any]]],
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    candidate_ids: Sequence[str],
    corridor_seconds: float,
) -> list[dict[str, Any]]:
    repo = Path(repo_text)
    cache_root = Path(cache_text)
    spec = r3.load_candidate_spec(repo)
    policies = {
        candidate_id: r3.candidate_policy(spec, candidate_id)
        for candidate_id in candidate_ids
    }
    surfaces = r2.load_surfaces(repo)
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
        bind_round3_book_receipts(normalized)
        for candidate_index, candidate_id in enumerate(candidate_ids):
            result = r3.Round3Instrument(
                surfaces, policies[candidate_id]
            ).run(normalized)
            output.append({
                "event_index": event_index,
                "candidate_index": candidate_index,
                "candidate_id": candidate_id,
                "event_id": event_id,
                "stream": result,
                "summary": summarize_stream(result, normalized),
            })
    return output


def _first_difference(
    left: Sequence[Mapping[str, Any]],
    right: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    width = max(len(left), len(right))
    for index in range(width):
        left_row = left[index] if index < len(left) else None
        right_row = right[index] if index < len(right) else None
        if left_row != right_row:
            return {
                "decision_ordinal": index,
                "candidate_decision": left_row,
                "reference_decision": right_row,
            }
    raise PreRunError("distinct decision streams lacked a first difference")


def _reaim_pair_proof(
    candidate_ids: Sequence[str],
    streams: Mapping[str, Mapping[str, Mapping[str, Any]]],
    events: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    event_by_id = {
        str(event["event_id"]): event for event in events
    }
    for reaim_id in (
        value for value in candidate_ids if value.endswith("__reaim")
    ):
        base_id = reaim_id.rsplit("__", 1)[0] + "__hold"
        pair_rows: list[dict[str, Any]] = []
        for event_id in sorted(streams[reaim_id]):
            reaim_stream = streams[reaim_id][event_id]
            base_stream = streams[base_id][event_id]
            applied_actions = [
                row for row in reaim_stream["order_stream"]
                if row["action"] == "sibling_reaim_applied"
            ]
            if not applied_actions:
                continue
            applied = applied_actions[0]
            timestamp = float(applied["ts"])
            leg_id = str(applied["leg_id"])
            reaim_order = next(
                (
                    row for row in reaim_stream["order_stream"]
                    if row["action"] == "reprice"
                    and row["leg_id"] == leg_id
                    and float(row["ts"]) == timestamp
                    and row["reason"]
                    == "first_fill_sibling_reaim_later_trigger"
                ),
                None,
            )
            if reaim_order is None:
                raise PreRunError(
                    "reaim bookkeeping lacked a real sibling order change"
                )
            base_before = [
                row for row in decision_signature(base_stream)
                if float(row["ts"]) < timestamp
            ]
            reaim_before = [
                row for row in decision_signature(reaim_stream)
                if float(row["ts"]) < timestamp
            ]
            exact_difference = int(
                applied["reaim_sibling_order_cents"]
            ) - int(applied["base_sibling_order_cents"])
            row = {
                "schema_version": (
                    "window1-round3-real-reaim-order-proof-v1"
                ),
                "base_candidate_id": base_id,
                "reaim_candidate_id": reaim_id,
                "event_id": event_id,
                "event_date": str(
                    event_by_id[event_id]["event_date"]
                ),
                "first_leg_fill_ts": float(
                    applied["first_leg_fill_ts"]
                ),
                "sibling_later_lawful_trigger_ts": timestamp,
                "sibling_leg_id": leg_id,
                "base_sibling_order_cents": int(
                    applied["base_sibling_order_cents"]
                ),
                "reaim_sibling_order_cents": int(
                    applied["reaim_sibling_order_cents"]
                ),
                "actual_reaim_order_cents": int(
                    reaim_order["price_cents"]
                ),
                "exact_reaim_difference_cents": exact_difference,
                "earlier_order_decisions_byte_identical": (
                    base_before == reaim_before
                ),
                "base_earlier_decisions_sha256": sha256_json(
                    base_before
                ),
                "reaim_earlier_decisions_sha256": sha256_json(
                    reaim_before
                ),
                "real_later_sibling_order_change": True,
                "scored": False,
            }
            if (
                exact_difference != 1
                or row["actual_reaim_order_cents"]
                != row["reaim_sibling_order_cents"]
                or not row["earlier_order_decisions_byte_identical"]
            ):
                raise PreRunError("reaim causal/order proof failed")
            pair_rows.append(row)
            rows.append(row)
        if not pair_rows:
            raise PreRunError(
                f"reaim candidate lacks a real order witness: {reaim_id}"
            )
        pairs.append({
            "base_candidate_id": base_id,
            "reaim_candidate_id": reaim_id,
            "real_event_order_change_count": len(pair_rows),
            "all_exact_plus_one": all(
                row["exact_reaim_difference_cents"] == 1
                for row in pair_rows
            ),
            "all_earlier_decisions_byte_identical": all(
                row["earlier_order_decisions_byte_identical"]
                for row in pair_rows
            ),
            "witness": pair_rows[0],
            "scored": False,
        })
    return pairs, rows


def _family_matrix(
    candidate_ids: Sequence[str],
    summaries: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    aggregate = {
        candidate_id: Counter(
            {
                key: sum(int(row.get(key) or 0) for row in rows)
                for key in (
                    "orientation_order_change",
                    "drift_order_change",
                    "cohort_call_count",
                    "cohort_no_call_count",
                    "top5_no_call_count",
                    "top5_order_change",
                )
            }
        )
        for candidate_id, rows in summaries.items()
    }
    return [
        {
            "family_id": "independent_pair_presence",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": True,
            "actually_selected": True,
            "status": "both legs place from independent first causal BBO",
        },
        {
            "family_id": "advisory_asynchronous_divot_timing",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": False,
            "actually_selected": False,
            "coverage_credit": False,
            "status": (
                "INERT_DIAGNOSTIC; t_deep is retained only as an advisory "
                "receipt and never controls eligibility or an order"
            ),
        },
        {
            "family_id": "leg_specific_touch_join_park_posture",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": True,
            "actually_selected": True,
            "status": "candidate posture pairs produce distinct real orders",
        },
        {
            "family_id": "positive_print_divot_recut",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": any(
                row["positive_print_divot_recut_exercised"]
                for rows in summaries.values() for row in rows
            ),
            "actually_selected": True,
            "status": "latent book cell changes hold queue; print trigger may act",
        },
        {
            "family_id": "first_fill_sibling_response",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": any(
                row["sibling_response_exercised"]
                for candidate_id, rows in summaries.items()
                if candidate_id.endswith("__reaim")
                for row in rows
            ),
            "actually_selected": True,
            "status": "first positive fill arms later sibling +1 action",
        },
        {
            "family_id": "nonself_one_cent_walk",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": any(
                row["walk_exercised"]
                for candidate_id, rows in summaries.items()
                if candidate_id.startswith("r3_full_os")
                for row in rows
            ),
            "actually_selected": True,
            "status": "positive-size nonself chain only",
        },
        {
            "family_id": "causal_orientation",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": sum(
                values["orientation_order_change"]
                for candidate_id, values in aggregate.items()
                if candidate_id.startswith(("r3_causal", "r3_full"))
            ) > 0,
            "actually_selected": True,
            "status": "causal checkpoint; NO_CALL where thin",
        },
        {
            "family_id": "causal_drift_recognition",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": sum(
                values["drift_order_change"]
                for candidate_id, values in aggregate.items()
                if candidate_id.startswith(("r3_causal", "r3_full"))
            ) > 0,
            "actually_selected": True,
            "status": "T6 history-through-decision only",
        },
        {
            "family_id": "cohort_steering",
            "loaded": True,
            "available": False,
            "evaluated": True,
            "decision_changing": False,
            "actually_selected": False,
            "status": "NO_CALL_UNAVAILABLE below frozen n=30",
            "call_count": sum(
                values["cohort_call_count"]
                for values in aggregate.values()
            ),
            "no_call_count": sum(
                values["cohort_no_call_count"]
                for values in aggregate.values()
            ),
        },
        {
            "family_id": "bbo_top5_pressure",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": sum(
                values["top5_order_change"]
                for values in aggregate.values()
            ) > 0,
            "actually_selected": True,
            "status": (
                "top-five only where causal; named NO_CALL otherwise; "
                "credited only on an actual price difference"
            ),
            "no_call_count": sum(
                values["top5_no_call_count"]
                for values in aggregate.values()
            ),
        },
        {
            "family_id": "own_order_contribution_subtraction",
            "loaded": True,
            "available": True,
            "evaluated": True,
            "decision_changing": False,
            "actually_selected": True,
            "coverage_credit": False,
            "status": (
                "safety-only invariant; zero attributable own volume in "
                "D=804, so it is not credited as decision-changing coverage"
            ),
        },
        {
            "family_id": "deployed_pair_policy_seal",
            "loaded": False,
            "available": False,
            "evaluated": False,
            "decision_changing": False,
            "actually_selected": False,
            "status": (
                "UNAVAILABLE; latest deployed sealed pair-policy object is "
                "not bound in the research checkout and is not proxied"
            ),
        },
        {
            "family_id": "shape_mapping",
            "loaded": False,
            "available": False,
            "evaluated": False,
            "decision_changing": False,
            "actually_selected": False,
            "status": "UNAVAILABLE; no lawful independent causal mapping",
        },
        {
            "family_id": "pinnacle",
            "loaded": False,
            "available": False,
            "evaluated": False,
            "decision_changing": False,
            "actually_selected": False,
            "status": "UNAVAILABLE",
        },
        {
            "family_id": "proved_full_depth",
            "loaded": False,
            "available": False,
            "evaluated": False,
            "decision_changing": False,
            "actually_selected": False,
            "status": "UNAVAILABLE; top-five is not full depth",
        },
    ]


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
    features = [
        row for row in read_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in features
    }
    if len(feature_map) != 2 * binding.D_REQUIRED:
        raise PreRunError("1,608 T8 leg identities not found")
    spec = r3.load_candidate_spec(repo)
    candidate_ids = list(map(str, spec["candidate_ids"]))
    if len(candidate_ids) != 8 or len(set(candidate_ids)) != 8:
        raise PreRunError("Round-3 must freeze exactly eight candidates")
    corridor = float(
        spec["common_parameters"]["policy_corridor_seconds_after_anchor"]
    )
    indexed = list(enumerate(events))
    worker_count = max(1, min(int(workers), len(indexed)))
    chunks = [indexed[index::worker_count] for index in range(worker_count)]
    if worker_count == 1:
        outputs = [
            _process_chunk(
                str(repo),
                str(cache_root),
                chunks[0],
                feature_map,
                candidate_ids,
                corridor,
            )
        ]
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
                )
                for chunk in chunks
            ]
            outputs = [future.result() for future in futures]
    rows = [row for output in outputs for row in output]
    rows.sort(key=lambda row: (
        int(row["event_index"]), int(row["candidate_index"])
    ))
    if len(rows) != binding.D_REQUIRED * len(candidate_ids):
        raise PreRunError("candidate-event stream conservation failed")
    if any(
        row["candidate_id"]
        != candidate_ids[int(row["candidate_index"])]
        for row in rows
    ):
        raise PreRunError("candidate ordering changed")

    streams: dict[str, dict[str, Mapping[str, Any]]] = {
        candidate_id: {} for candidate_id in candidate_ids
    }
    summaries: dict[str, list[Mapping[str, Any]]] = {
        candidate_id: [] for candidate_id in candidate_ids
    }
    for row in rows:
        candidate_id = str(row["candidate_id"])
        event_id = str(row["event_id"])
        streams[candidate_id][event_id] = row["stream"]
        summaries[candidate_id].append(row["summary"])

    aggregate_hashes = {
        candidate_id: sha256_json([
            {
                "event_id": event_id,
                "decisions": decision_signature(
                    streams[candidate_id][event_id]
                ),
            }
            for event_id in sorted(streams[candidate_id])
        ])
        for candidate_id in candidate_ids
    }
    if len(set(aggregate_hashes.values())) != len(candidate_ids):
        raise PreRunError("duplicate/inert Round-3 candidate retained")

    witnesses: list[dict[str, Any]] = []
    difference_rows: list[dict[str, Any]] = []
    for candidate_id in candidate_ids:
        reference_id = REFERENCE_BY_CANDIDATE[candidate_id]
        candidate_witnesses: list[dict[str, Any]] = []
        for event in events:
            event_id = str(event["event_id"])
            candidate_decisions = decision_signature(
                streams[candidate_id][event_id]
            )
            reference_decisions = decision_signature(
                streams[reference_id][event_id]
            )
            if candidate_decisions == reference_decisions:
                continue
            difference = _first_difference(
                candidate_decisions, reference_decisions
            )
            row = {
                "schema_version": (
                    "window1-round3-real-order-difference-v1"
                ),
                "candidate_id": candidate_id,
                "reference_candidate_id": reference_id,
                "event_id": event_id,
                "event_date": str(event["event_date"]),
                "candidate_decision_sha256": sha256_json(
                    candidate_decisions
                ),
                "reference_decision_sha256": sha256_json(
                    reference_decisions
                ),
                **difference,
                "expected_order_action_difference": True,
                "scored": False,
            }
            candidate_witnesses.append(row)
            difference_rows.append(row)
        if not candidate_witnesses:
            raise PreRunError(
                f"candidate lacks real distinctness: {candidate_id}"
            )
        witnesses.append(candidate_witnesses[0])

    candidate_summaries: list[dict[str, Any]] = []
    for candidate_id in candidate_ids:
        rows_for_candidate = summaries[candidate_id]
        action_counts: Counter[str] = Counter()
        reason_counts: Counter[str] = Counter()
        for row in rows_for_candidate:
            action_counts.update(row["action_counts"])
            reason_counts.update(row["reason_counts"])
        candidate_summaries.append({
            "candidate_id": candidate_id,
            "eligible_event_count": sum(
                bool(row["eligible"]) for row in rows_for_candidate
            ),
            "censored_event_count": sum(
                not row["eligible"] for row in rows_for_candidate
            ),
            "censor_reasons": dict(sorted(Counter(
                reason
                for row in rows_for_candidate
                for reason in row["feature_censors"]
            ).items())),
            "order_decision_count": sum(
                int(row["decision_count"]) for row in rows_for_candidate
            ),
            "place_count": int(action_counts["place"]),
            "reprice_count": int(action_counts["reprice"]),
            "cancel_count": int(action_counts["cancel"]),
            "sibling_reaim_applied_count": int(
                action_counts["sibling_reaim_applied"]
            ),
            "sibling_reaim_no_call_count": int(
                action_counts["sibling_reaim_no_call"]
            ),
            "pair_cost_no_call_count": int(
                action_counts["pair_cost_no_call"]
            ),
            "cohort_no_call_count": int(
                action_counts["cohort_no_call"]
            ),
            "top5_no_call_count": int(
                action_counts["feature_no_call"]
            ),
            "positive_size_print_count_consumed": sum(
                int(row["positive_size_print_count_consumed"])
                for row in rows_for_candidate
            ),
            "BBO_covered_event_count": sum(
                int(row["bbo_covered_legs"]) == 2
                for row in rows_for_candidate
            ),
            "top5_covered_event_count": sum(
                int(row["top5_covered_legs"]) == 2
                for row in rows_for_candidate
            ),
            "events_distinct_from_declared_reference": sum(
                row["candidate_id"] == candidate_id
                for row in difference_rows
            ),
            "aggregate_order_decision_sha256": (
                aggregate_hashes[candidate_id]
            ),
            "metrics": None,
            "scored": False,
        })
    if any(
        row["eligible_event_count"] == 0
        or row["order_decision_count"] == 0
        or row["events_distinct_from_declared_reference"] == 0
        for row in candidate_summaries
    ):
        raise PreRunError("Round-3 candidate hard gate failed")

    reaim_pair_proof, reaim_order_differences = _reaim_pair_proof(
        candidate_ids, streams, events
    )
    return {
        "schema_version": VERSION,
        "D": binding.D_REQUIRED,
        "candidate_ids": candidate_ids,
        "candidate_count": len(candidate_ids),
        "candidate_event_stream_count": len(rows),
        "candidate_rows": rows,
        "candidate_summaries": candidate_summaries,
        "candidate_distinctness_witnesses": witnesses,
        "candidate_order_difference_ledger": difference_rows,
        "base_reaim_pair_proof": reaim_pair_proof,
        "reaim_order_difference_ledger": reaim_order_differences,
        "family_capability_matrix": _family_matrix(
            candidate_ids, summaries
        ),
        "development_dates": binding.DEV_DATES,
        "policy_clock": {
            "anchor": "timestamped exchange schedule available at decision",
            "evaluation_real_start_access": False,
            "statistical_tdeep_is_hard_gate": False,
            "corridor_seconds_after_anchor": corridor,
        },
        "metric_contract_changed": False,
        "candidate_scoring_performed": False,
        "performance_ablation_performed": False,
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze score-free Round-3 real-input order capability."
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
    stream_path = output / "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
    with stream_path.open("wb") as raw_handle:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw_handle, mtime=0
        ) as gzip_handle:
            with io.TextIOWrapper(
                gzip_handle, encoding="utf-8", newline="\n"
            ) as handle:
                for row in value["candidate_rows"]:
                    handle.write(compact({
                        "candidate_id": row["candidate_id"],
                        "event_id": row["event_id"],
                        "stream": row["stream"],
                    }) + "\n")
    write_json(
        output / "ROUND3_REAL_CAPABILITY.json",
        {
            key: item for key, item in value.items()
            if key not in {
                "candidate_rows",
                "candidate_order_difference_ledger",
                "reaim_order_difference_ledger",
            }
        },
    )
    write_jsonl(
        output / "ROUND3_CANDIDATE_ORDER_DIFFERENCES.jsonl",
        value["candidate_order_difference_ledger"],
    )
    write_jsonl(
        output / "ROUND3_REAIM_ORDER_DIFFERENCES.jsonl",
        value["reaim_order_difference_ledger"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
