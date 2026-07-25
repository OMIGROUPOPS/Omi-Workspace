#!/usr/bin/env python3
"""Round-2 partner-leg starvation forensic for the Round-3 design lane.

This module is read-only with respect to source evidence.  It consumes the
admitted Round-2 result ledgers, the already-frozen counterfactual streams, and
the immutable July 12-20 market caches.  It does not invoke the scorer, compute
candidate performance, inspect the sealed holdout, or contact any live system.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


RESULTS_COMMIT = "10ac6dbc68d65cb21ab3718e118ff34d7220ad87"
AUDIT_COMMIT = "807e2c865c3cf7384757c54a3b879518568dec4f"
AUTHORIZED_PRERUN = "47bfbd4335a435a30054be9007c5029331252eee"
EXPECTED_D = 804
EXPECTED_WINDOW1_FILL_RECEIPTS = 82

RESULT_DIRECTORY = (
    ".claude/window1_round2_results_"
    "w1r2-dev-20260712-20260720-0a7fd1c6-grid2-stdoutsafe"
)
STREAM_PATH = (
    ".claude/window1_round2_execution_package_20260724/"
    "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
)
EVENT_LEDGER_PATH = "../OMI-Window1-private/joined/events.jsonl"
LEG_FEATURE_PATH = ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl"
CACHE_DIRECTORY = "../OMI-Window1-private/fit-local/guarded-cache-v3"

CANDIDATE_IDS = [
    "r2_async_pair__park_join__hold",
    "r2_async_pair__park_join__reaim",
    "r2_async_pair__touch_park__hold",
    "r2_async_pair__touch_park__reaim",
    "r2_causal_steer__park_join__hold",
    "r2_causal_steer__park_join__reaim",
    "r2_full_os__walk_park__hold",
    "r2_full_os__walk_park__reaim",
]
BASE_REAIM_PAIRS = [
    (
        "r2_async_pair__park_join__hold",
        "r2_async_pair__park_join__reaim",
    ),
    (
        "r2_async_pair__touch_park__hold",
        "r2_async_pair__touch_park__reaim",
    ),
    (
        "r2_causal_steer__park_join__hold",
        "r2_causal_steer__park_join__reaim",
    ),
    (
        "r2_full_os__walk_park__hold",
        "r2_full_os__walk_park__reaim",
    ),
]
ORDER_ACTIONS = {"place", "reprice", "cancel"}
STARVATION_CATEGORIES = [
    "sibling_required_feature_unavailable",
    "first_leg_partial_response_not_armed_before_cutoff",
    "sibling_eligibility_began_after_guarded_cutoff",
    "sibling_order_never_called_no_posteligibility_divot",
    "reaim_armed_no_posteligibility_trigger",
    "policy_horizon_ended_before_sibling_reach",
    "reaim_applied_policy_horizon_ended_before_sibling_reach",
    "sibling_filled_only_after_guarded_cutoff",
    "reaim_applied_but_sibling_filled_after_guarded_cutoff",
    "sibling_order_reached_but_insufficient_positive_size",
    "sibling_order_placed_never_reached_by_causal_print",
    "reaim_applied_no_executable_improvement",
    "other_precisely_evidenced_cause",
]


class ForensicError(RuntimeError):
    """Raised when admitted evidence does not satisfy the frozen contract."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_cache(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def price_bucket(value: float) -> str:
    price = float(value)
    if price <= 25:
        return "01-25"
    if price <= 50:
        return "26-50"
    if price <= 75:
        return "51-75"
    return "76-99"


def action_signature(
    stream: Mapping[str, Any],
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
        "queue_ahead",
    )
    return [
        {field: row.get(field) for field in fields}
        for row in stream.get("order_stream") or []
        if row.get("action") in ORDER_ACTIONS
    ]


def _first_action(
    actions: Sequence[Mapping[str, Any]], name: str,
) -> Mapping[str, Any] | None:
    return next(
        (row for row in actions if row.get("action") == name),
        None,
    )


def _strict_reach_evidence(
    *,
    cache_leg: Mapping[str, Any],
    actions: Sequence[Mapping[str, Any]],
    boundary: float,
) -> dict[str, Any]:
    """Measure positive-size causal sell prints while an order was active.

    Prints sharing a timestamp with a newly placed order are excluded.  In the
    frozen instrument, a print-triggered placement happens only after that
    print has been processed, so the triggering print cannot fill the order.
    """
    intervals: list[dict[str, Any]] = []
    active: dict[str, Any] | None = None
    for row in actions:
        action = str(row.get("action"))
        timestamp = float(row["ts"])
        if timestamp > boundary:
            break
        if action in {"place", "reprice"}:
            if active is not None:
                active["end_ts"] = timestamp
                intervals.append(active)
            active = {
                "start_ts": timestamp,
                "end_ts": boundary,
                "price_cents": int(row["price_cents"]),
                "queue_ahead": float(row.get("queue_ahead") or 0),
            }
        elif action == "cancel" and active is not None:
            active["end_ts"] = min(boundary, timestamp)
            intervals.append(active)
            active = None
        elif action == "fill_observed" and active is not None:
            if bool(row.get("complete")):
                active["end_ts"] = timestamp
                intervals.append(active)
                active = None
    if active is not None:
        intervals.append(active)

    reached_prints: list[dict[str, Any]] = []
    for interval in intervals:
        for row in cache_leg.get("prints") or []:
            try:
                size = float(row.get("size"))
            except (TypeError, ValueError):
                continue
            timestamp = float(row["ts"])
            if (
                size <= 0
                or str(row.get("taker_side")) != "no"
                or not (
                    float(interval["start_ts"])
                    < timestamp
                    <= float(interval["end_ts"])
                )
                or timestamp > boundary
                or float(row["price"]) > float(interval["price_cents"])
            ):
                continue
            reached_prints.append({
                "ts": timestamp,
                "price_cents": float(row["price"]),
                "size": size,
                "trade_id": str(row.get("trade_id") or ""),
                "order_price_cents": interval["price_cents"],
                "queue_ahead_at_order_birth": interval["queue_ahead"],
            })
    return {
        "active_order_interval_count": len(intervals),
        "reached_positive_print_count": len(reached_prints),
        "reached_positive_size": sum(
            float(row["size"]) for row in reached_prints
        ),
        "strictly_better_price_print_count": sum(
            float(row["price_cents"]) < float(row["order_price_cents"])
            for row in reached_prints
        ),
        "reached_print_receipts": reached_prints,
    }


def _classify_starvation(
    *,
    filled_leg: Mapping[str, Any],
    sibling: Mapping[str, Any],
    stream: Mapping[str, Any],
    sibling_actions: Sequence[Mapping[str, Any]],
    reach: Mapping[str, Any],
) -> tuple[str, str]:
    boundary = float(sibling["boundary"]["boundary_timestamp"])
    horizon = float(
        stream["policy_clock"]["policy_decision_horizon_ts"]
    )
    macro = _first_action(sibling_actions, "macro_bind")
    eligible = (
        float(macro["eligible_ts"])
        if macro and macro.get("eligible_ts") is not None
        else None
    )
    feature_censor = _first_action(sibling_actions, "feature_censor")
    pre_orders = [
        row for row in sibling_actions
        if (
            row.get("action") in {"place", "reprice"}
            and float(row["ts"]) <= boundary
        )
    ]
    pre_reaim = [
        row for row in sibling_actions
        if (
            row.get("action") == "sibling_reaim_applied"
            and float(row["ts"]) <= boundary
        )
    ]
    pre_armed = [
        row for row in sibling_actions
        if (
            row.get("action") == "sibling_reaim_armed"
            and float(row["ts"]) <= boundary
        )
    ]
    after_cutoff_fills = [
        row for row in sibling_actions
        if (
            row.get("action") == "fill_observed"
            and float(row["ts"]) > boundary
        )
    ]
    posteligible_divots = [
        row for row in sibling_actions
        if (
            row.get("action") == "micro_divot"
            and eligible is not None
            and eligible <= float(row["ts"]) <= boundary
        )
    ]

    if feature_censor is not None:
        return (
            "sibling_required_feature_unavailable",
            str(feature_censor.get("reason") or "required_feature_absent"),
        )
    if float(filled_leg["inside_window_quantity"]) < 5:
        return (
            "first_leg_partial_response_not_armed_before_cutoff",
            "Round-2 armed sibling response only at exact-five completion",
        )
    if eligible is not None and eligible >= boundary:
        return (
            "sibling_eligibility_began_after_guarded_cutoff",
            "statistical t_deep timing was enforced as a hard eligibility gate",
        )
    if not pre_orders:
        if pre_armed:
            return (
                "reaim_armed_no_posteligibility_trigger",
                (
                    "reaim remained pending because the sibling produced no "
                    "qualifying post-eligibility divot before cutoff"
                ),
            )
        return (
            "sibling_order_never_called_no_posteligibility_divot",
            (
                "sibling was eligible but produced no qualifying "
                "post-eligibility divot before cutoff"
            ),
        )
    if horizon < boundary and not after_cutoff_fills:
        if pre_reaim:
            return (
                "reaim_applied_policy_horizon_ended_before_sibling_reach",
                (
                    "the +1 order was real, but the schedule-derived policy "
                    "horizon cancelled it before later market activity"
                ),
            )
        return (
            "policy_horizon_ended_before_sibling_reach",
            (
                "the schedule-derived policy horizon cancelled the order "
                "before later market activity"
            ),
        )
    if after_cutoff_fills:
        if pre_reaim:
            return (
                "reaim_applied_but_sibling_filled_after_guarded_cutoff",
                (
                    "the +1 order was real, but its fill receipts arrived "
                    "only after the guarded Window-1 cutoff"
                ),
            )
        return (
            "sibling_filled_only_after_guarded_cutoff",
            (
                "the order was executable later, but all sibling fill "
                "receipts arrived after the guarded Window-1 cutoff"
            ),
        )
    if int(reach["reached_positive_print_count"]) > 0:
        if int(reach["strictly_better_price_print_count"]) > 0:
            return (
                "other_precisely_evidenced_cause",
                (
                    "a strictly better causal print crossed an active order "
                    "without a frozen fill action; evidence inconsistency"
                ),
            )
        return (
            "sibling_order_reached_but_insufficient_positive_size",
            "positive-size prints reached the price but did not clear queue",
        )
    if pre_reaim:
        return (
            "reaim_applied_no_executable_improvement",
            "the +1 order was placed but no causal sell print reached it",
        )
    if pre_orders:
        return (
            "sibling_order_placed_never_reached_by_causal_print",
            "no positive-size causal sell print reached an active order",
        )
    if posteligible_divots:
        return (
            "other_precisely_evidenced_cause",
            "post-eligibility divot existed but no order action was emitted",
        )
    return (
        "other_precisely_evidenced_cause",
        "no earlier mutually exclusive causal condition matched",
    )


def _increment_group(
    groups: dict[str, Counter[str]], key: str, category: str,
) -> None:
    groups[key][category] += 1


def _ordered_counts(counter: Mapping[str, int]) -> dict[str, int]:
    return {
        category: int(counter.get(category, 0))
        for category in STARVATION_CATEGORIES
    }


def build_forensic(repo: Path) -> dict[str, Any]:
    results_dir = repo / RESULT_DIRECTORY
    stream_path = repo / STREAM_PATH
    event_path = (repo / EVENT_LEDGER_PATH).resolve()
    cache_dir = (repo / CACHE_DIRECTORY).resolve()

    events = {
        str(row["event_id"]): row
        for row in read_jsonl(event_path)
    }
    feature_roles = {
        (str(row["event_id"]), str(row["ticker"])): str(
            row.get("role") or "UNAVAILABLE"
        )
        for row in read_jsonl(repo / LEG_FEATURE_PATH)
    }
    if len(events) != EXPECTED_D:
        raise ForensicError(f"D changed: {len(events)}")
    if any(
        str(row["event_date"]) not in {
            f"2026-07-{day:02d}" for day in range(12, 21)
        }
        for row in events.values()
    ):
        raise ForensicError("event ledger escaped July 12-20")

    result_rows: dict[tuple[str, str], dict[str, Any]] = {}
    candidate_census: dict[str, Counter[str]] = {}
    for path in sorted(results_dir.glob("*_EVENT_LEDGER.jsonl")):
        rows = read_jsonl(path)
        if len(rows) != EXPECTED_D:
            raise ForensicError(f"candidate ledger changed: {path}")
        candidate_id = str(rows[0]["candidate_id"])
        if candidate_id not in CANDIDATE_IDS:
            raise ForensicError(f"unknown candidate result: {candidate_id}")
        if any(
            any(bool(row[metric]) for metric in ("C", "PC", "S", "IC"))
            for row in rows
        ):
            raise ForensicError("admitted all-zero metric result changed")
        candidate_census[candidate_id] = Counter(
            str(row["classification"]) for row in rows
        )
        for row in rows:
            result_rows[(candidate_id, str(row["event_id"]))] = row
    if sorted(candidate_census) != CANDIDATE_IDS:
        raise ForensicError("eight admitted candidate ledgers not found")

    streams: dict[tuple[str, str], dict[str, Any]] = {}
    with gzip.open(stream_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            key = (str(row["candidate_id"]), str(row["event_id"]))
            streams[key] = row["stream"]
    if len(streams) != EXPECTED_D * len(CANDIDATE_IDS):
        raise ForensicError("6,432 frozen streams not found")

    fill_bearing = {
        key: row for key, row in result_rows.items()
        if row["classification"] == "naked_single_leg"
    }
    groups: dict[str, dict[str, Counter[str]]] = {
        name: defaultdict(Counter)
        for name in (
            "candidate",
            "event",
            "tournament_class",
            "first_filled_leg",
            "first_filled_role",
            "filled_birth_band",
            "filled_entry_price_band",
            "start_source",
        )
    }
    ledger: list[dict[str, Any]] = []
    cache_by_event: dict[str, dict[str, Any]] = {}
    receipt_total = 0

    for (candidate_id, event_id), result in sorted(fill_bearing.items()):
        event = events[event_id]
        stream = streams[(candidate_id, event_id)]
        filled = next(
            leg for leg in result["leg_results"]
            if float(leg["inside_window_quantity"]) > 0
        )
        sibling = next(
            leg for leg in result["leg_results"]
            if float(leg["inside_window_quantity"]) == 0
        )
        receipt_count = len(filled["inside_window_fill_receipts"])
        receipt_total += receipt_count
        filled_actions = stream["leg_streams"][filled["leg_id"]]
        sibling_actions = stream["leg_streams"][sibling["leg_id"]]
        filled_macro = _first_action(filled_actions, "macro_bind") or {}
        sibling_macro = _first_action(sibling_actions, "macro_bind") or {}
        event_cache = cache_by_event.get(event_id)
        if event_cache is None:
            event_cache = load_cache(cache_dir / f"{event_id}.json.gz")
            cache_by_event[event_id] = event_cache
        cache_leg = next(
            leg for leg in event_cache["legs"]
            if str(leg["leg"]) == str(sibling["leg_id"])
        )
        boundary = float(sibling["boundary"]["boundary_timestamp"])
        reach = _strict_reach_evidence(
            cache_leg=cache_leg,
            actions=sibling_actions,
            boundary=boundary,
        )
        category, cause = _classify_starvation(
            filled_leg=filled,
            sibling=sibling,
            stream=stream,
            sibling_actions=sibling_actions,
            reach=reach,
        )
        if category not in STARVATION_CATEGORIES:
            raise ForensicError(f"unknown starvation category: {category}")

        filled_role = feature_roles.get(
            (event_id, str(filled["ticker"])), "UNAVAILABLE"
        )
        birth_band = str(filled_macro.get("birth_band") or "UNAVAILABLE")
        entry_vwap = float(filled["entry_vwap_cents"])
        row = {
            "schema_version": "window1-round3-starvation-ledger-v1",
            "candidate_id": candidate_id,
            "event_id": event_id,
            "event_date": str(event["event_date"]),
            "tournament_class": str(event["category"]),
            "first_filled_leg_id": str(filled["leg_id"]),
            "first_filled_role": filled_role,
            "first_filled_quantity": float(
                filled["inside_window_quantity"]
            ),
            "first_filled_entry_vwap_cents": entry_vwap,
            "first_filled_birth_band": birth_band,
            "first_filled_entry_price_band": price_bucket(entry_vwap),
            "window1_fill_receipt_count": receipt_count,
            "first_window1_fill_ts": min(
                float(receipt["timestamp"])
                for receipt in filled["inside_window_fill_receipts"]
            ),
            "last_window1_fill_ts": max(
                float(receipt["timestamp"])
                for receipt in filled["inside_window_fill_receipts"]
            ),
            "sibling_leg_id": str(sibling["leg_id"]),
            "sibling_inside_window_quantity": 0,
            "sibling_eligible_ts": sibling_macro.get("eligible_ts"),
            "guarded_boundary_ts": boundary,
            "start_source_class": str(
                sibling["boundary"]["source_class"]
            ),
            "start_guard_seconds": float(
                sibling["boundary"]["guard_seconds"]
            ),
            "policy_anchor_ts": float(
                stream["policy_clock"]["policy_anchor_ts"]
            ),
            "policy_horizon_ts": float(
                stream["policy_clock"]["policy_decision_horizon_ts"]
            ),
            "sibling_place_count_before_cutoff": sum(
                row["action"] == "place" and float(row["ts"]) <= boundary
                for row in sibling_actions
            ),
            "sibling_reprice_count_before_cutoff": sum(
                row["action"] == "reprice" and float(row["ts"]) <= boundary
                for row in sibling_actions
            ),
            "sibling_posteligibility_divot_count_before_cutoff": sum(
                (
                    row["action"] == "micro_divot"
                    and sibling_macro.get("eligible_ts") is not None
                    and float(sibling_macro["eligible_ts"])
                    <= float(row["ts"])
                    <= boundary
                )
                for row in sibling_actions
            ),
            "sibling_hold_bookkeeping_count": sum(
                row["action"] == "sibling_hold"
                for row in sibling_actions
            ),
            "sibling_reaim_armed_count": sum(
                row["action"] == "sibling_reaim_armed"
                for row in sibling_actions
            ),
            "sibling_reaim_applied_count_before_cutoff": sum(
                (
                    row["action"] == "sibling_reaim_applied"
                    and float(row["ts"]) <= boundary
                )
                for row in sibling_actions
            ),
            "sibling_reaim_no_call_count": sum(
                row["action"] == "sibling_reaim_no_call"
                for row in sibling_actions
            ),
            "sibling_fill_count_after_cutoff": sum(
                (
                    row["action"] == "fill_observed"
                    and float(row["ts"]) > boundary
                )
                for row in sibling_actions
            ),
            "reach_evidence": reach,
            "starvation_category": category,
            "precise_cause": cause,
            "missingness_combined_with_nonfill": False,
            "scored": False,
        }
        ledger.append(row)
        dimensions = {
            "candidate": candidate_id,
            "event": event_id,
            "tournament_class": str(event["category"]),
            "first_filled_leg": str(filled["leg_id"]),
            "first_filled_role": filled_role,
            "filled_birth_band": birth_band,
            "filled_entry_price_band": price_bucket(entry_vwap),
            "start_source": str(sibling["boundary"]["source_class"]),
        }
        for dimension, value in dimensions.items():
            _increment_group(groups[dimension], value, category)

    if receipt_total != EXPECTED_WINDOW1_FILL_RECEIPTS:
        raise ForensicError(
            f"admitted Window-1 receipt total changed: {receipt_total}"
        )

    difference_rows: list[dict[str, Any]] = []
    pair_summaries: list[dict[str, Any]] = []
    for base_id, reaim_id in BASE_REAIM_PAIRS:
        changed = 0
        applied = 0
        earlier_identity_pass = 0
        for event_id in sorted(events):
            base_stream = streams[(base_id, event_id)]
            reaim_stream = streams[(reaim_id, event_id)]
            base_signature = action_signature(base_stream)
            reaim_signature = action_signature(reaim_stream)
            if base_signature == reaim_signature:
                continue
            changed += 1
            applied_actions = [
                row for row in reaim_stream["order_stream"]
                if row["action"] == "sibling_reaim_applied"
            ]
            if not applied_actions:
                raise ForensicError(
                    "order difference lacks real reaim action: "
                    f"{reaim_id} {event_id}"
                )
            applied += 1
            first = applied_actions[0]
            timestamp = float(first["ts"])
            base_earlier = [
                row for row in base_signature
                if float(row["ts"]) < timestamp
            ]
            reaim_earlier = [
                row for row in reaim_signature
                if float(row["ts"]) < timestamp
            ]
            earlier_identical = base_earlier == reaim_earlier
            earlier_identity_pass += int(earlier_identical)
            difference_rows.append({
                "schema_version": (
                    "window1-round2-base-reaim-order-difference-v1"
                ),
                "base_candidate_id": base_id,
                "reaim_candidate_id": reaim_id,
                "event_id": event_id,
                "reaim_action_ts": timestamp,
                "leg_id": str(first["leg_id"]),
                "base_sibling_order_cents": int(
                    first["base_sibling_order_cents"]
                ),
                "reaim_sibling_order_cents": int(
                    first["reaim_sibling_order_cents"]
                ),
                "exact_difference_cents": int(
                    first["exact_reaim_difference_cents"]
                ),
                "earlier_order_decisions_byte_identical": (
                    earlier_identical
                ),
                "earlier_base_decision_sha256": sha256_json(base_earlier),
                "earlier_reaim_decision_sha256": sha256_json(
                    reaim_earlier
                ),
                "base_complete_pair": bool(
                    result_rows[(base_id, event_id)]["C"]
                ),
                "reaim_complete_pair": bool(
                    result_rows[(reaim_id, event_id)]["C"]
                ),
                "scored_in_this_forensic": False,
            })
        pair_summaries.append({
            "base_candidate_id": base_id,
            "reaim_candidate_id": reaim_id,
            "changed_order_event_count": changed,
            "real_reaim_action_event_count": applied,
            "earlier_decisions_identical_event_count": (
                earlier_identity_pass
            ),
            "completed_pairs_base": 0,
            "completed_pairs_reaim": 0,
            "explanation": (
                "reaim altered real sibling orders by +1, but the admitted "
                "guarded evaluator found no dual completion"
            ),
        })

    candidate_decisions: list[dict[str, Any]] = []
    base_streams = {
        event_id: action_signature(
            streams[(CANDIDATE_IDS[0], event_id)]
        )
        for event_id in events
    }
    for candidate_id in CANDIDATE_IDS:
        action_counts: Counter[str] = Counter()
        decision_count = 0
        different_from_base = 0
        for event_id in events:
            stream = streams[(candidate_id, event_id)]
            action_counts.update(
                str(row["action"]) for row in stream["order_stream"]
            )
            signature = action_signature(stream)
            decision_count += len(signature)
            if signature != base_streams[event_id]:
                different_from_base += 1
        candidate_decisions.append({
            "candidate_id": candidate_id,
            "order_decision_count": decision_count,
            "order_decision_sha256": sha256_json([
                {
                    "event_id": event_id,
                    "decisions": action_signature(
                        streams[(candidate_id, event_id)]
                    ),
                }
                for event_id in sorted(events)
            ]),
            "events_different_from_first_base_candidate": (
                different_from_base
            ),
            "place_count": int(action_counts["place"]),
            "reprice_count": int(action_counts["reprice"]),
            "cancel_count": int(action_counts["cancel"]),
            "fill_observation_count_over_policy_horizon": int(
                action_counts["fill_observed"]
            ),
            "sibling_hold_bookkeeping_count": int(
                action_counts["sibling_hold"]
            ),
            "sibling_reaim_armed_count": int(
                action_counts["sibling_reaim_armed"]
            ),
            "sibling_reaim_applied_count": int(
                action_counts["sibling_reaim_applied"]
            ),
            "sibling_reaim_no_call_count": int(
                action_counts["sibling_reaim_no_call"]
            ),
            "window1_fill_receipt_count": sum(
                row["window1_fill_receipt_count"]
                for row in ledger
                if row["candidate_id"] == candidate_id
            ),
            "window1_dual_completion_count": 0,
        })

    return {
        "schema_version": "window1-round3-root-cause-forensic-v1",
        "controlling_identities": {
            "results_commit": RESULTS_COMMIT,
            "independent_audit_commit": AUDIT_COMMIT,
            "authorized_prerun": AUTHORIZED_PRERUN,
        },
        "accepted_ground_truth": {
            "D_per_candidate": EXPECTED_D,
            "candidate_count": len(CANDIDATE_IDS),
            "C_PC_S_IC_per_candidate": 0,
            "window1_fill_receipt_count": receipt_total,
            "fill_bearing_candidate_event_count": len(ledger),
            "all_fills_single_leg": True,
            "market_ceiling_claim": False,
        },
        "candidate_classification_census": {
            candidate_id: dict(sorted(census.items()))
            for candidate_id, census in candidate_census.items()
        },
        "starvation_ledger": ledger,
        "starvation_counts": {
            dimension: {
                key: _ordered_counts(counter)
                for key, counter in sorted(values.items())
            }
            for dimension, values in groups.items()
        },
        "candidate_order_decisions": candidate_decisions,
        "base_reaim_pair_summaries": pair_summaries,
        "base_reaim_order_difference_ledger": difference_rows,
        "source_receipts": {
            "event_ledger": {
                "path": EVENT_LEDGER_PATH,
                "sha256": sha256_file(event_path),
            },
            "frozen_streams": {
                "path": STREAM_PATH,
                "sha256": sha256_file(stream_path),
            },
            "result_directory": RESULT_DIRECTORY,
        },
        "holdout_opened": False,
        "holdout_queried": False,
        "candidate_scoring_performed": False,
        "candidate_tuning_performed": False,
        "live_or_production_access": False,
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact(row) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the score-free Round-2 sibling-starvation forensic."
    )
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir
        if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    output.mkdir(parents=True, exist_ok=False)
    forensic = build_forensic(repo)
    write_json(
        output / "ROUND2_ROOT_CAUSE_FORENSIC.json",
        {
            key: value for key, value in forensic.items()
            if key not in {
                "starvation_ledger",
                "base_reaim_order_difference_ledger",
            }
        },
    )
    write_jsonl(
        output / "PARTNER_LEG_STARVATION_LEDGER.jsonl",
        forensic["starvation_ledger"],
    )
    write_json(
        output / "PARTNER_LEG_STARVATION_COUNTS.json",
        forensic["starvation_counts"],
    )
    write_jsonl(
        output / "BASE_REAIM_ORDER_DIFFERENCE_LEDGER.jsonl",
        forensic["base_reaim_order_difference_ledger"],
    )
    write_json(
        output / "ROUND2_CANDIDATE_DECISION_PROOF.json",
        {
            "schema_version": (
                "window1-round2-candidate-decision-proof-v1"
            ),
            "candidate_order_decisions": (
                forensic["candidate_order_decisions"]
            ),
            "base_reaim_pair_summaries": (
                forensic["base_reaim_pair_summaries"]
            ),
            "candidate_scoring_performed": False,
            "holdout_queried": False,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
