#!/usr/bin/env python3
"""Run the score-free Round-2 capability gate on the bound D=804 inputs."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import window1_round2_data_binding as binding
import window1_round2_instrument as instrument


VERSION = "window1-round2-real-capability-v2"
DECISION_ACTIONS = {
    "place", "reprice", "cancel",
}
FAMILY_ACTIONS = {
    "asynchronous_divot_timing": {"macro_bind"},
    "leg_specific_posture": {"place", "reprice"},
    "nonself_one_cent_walk": {"reprice"},
    "first_fill_sibling_response": {
        "sibling_reaim_applied", "reprice", "place"
    },
    "pair_divot_recut": {"pair_recut"},
    "causal_orientation": {"orientation_observed"},
    "causal_drift_recognition": {"drift_recognition_observed"},
    "cohort_steering": {"cohort_steer", "cohort_no_call"},
    "true_print_flow": {"micro_divot", "place"},
    "bbo_top5_pressure": {"place", "reprice"},
    "own_order_contribution_subtraction": {
        "contributed_volume_excluded"
    },
}


class CapabilityError(RuntimeError):
    """Raised when a real-population PRE-RUN gate fails."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def parse_utc(value: str) -> float:
    return dt.datetime.fromisoformat(
        str(value).replace("Z", "+00:00")
    ).timestamp()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_cache(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_event(
    event: Mapping[str, Any],
    cache: Mapping[str, Any],
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    *,
    corridor_seconds: float,
) -> dict[str, Any]:
    anchor = parse_utc(str(event["scheduled_start_exchange_ts"]))
    observed = parse_utc(str(event["schedule_observed_exchange_ts"]))
    left = anchor - 8 * 3600
    by_ticker = {
        str(row["ticker"]): row for row in cache["legs"]
    }
    activation = max(left, observed)
    horizon = anchor + corridor_seconds
    role_by_ticker: dict[str, str] = {}
    role_available = True
    for raw_leg in event["legs"]:
        ticker = str(raw_leg["ticker"])
        feature = feature_map[(str(event["event_id"]), ticker)]
        role = str(feature.get("role") or "")
        if role in {"favorite", "underdog"}:
            role_by_ticker[ticker] = role
    if set(role_by_ticker.values()) != {"favorite", "underdog"}:
        first_bids: dict[str, float] = {}
        for raw_leg in event["legs"]:
            ticker = str(raw_leg["ticker"])
            snapshots = [
                row for row in by_ticker[ticker].get("snapshots") or []
                if activation <= float(row["ts"]) < horizon
                and row.get("best_bid") is not None
            ]
            if snapshots:
                first_bids[ticker] = float(snapshots[0]["best_bid"])
        if (
            len(first_bids) == 2
            and len(set(first_bids.values())) == 2
        ):
            leader = max(first_bids, key=first_bids.get)
            role_by_ticker = {
                ticker: (
                    "favorite" if ticker == leader else "underdog"
                )
                for ticker in first_bids
            }
        else:
            role_available = False
            role_by_ticker = {
                str(raw_leg["ticker"]): (
                    "favorite" if index == 0 else "underdog"
                )
                for index, raw_leg in enumerate(event["legs"])
            }
    legs = []
    for raw_leg in event["legs"]:
        ticker = str(raw_leg["ticker"])
        cached = by_ticker[ticker]
        feature = feature_map[(str(event["event_id"]), ticker)]
        observations = []
        raw_prints = [
            row for row in cached.get("prints") or []
            if activation <= float(row["ts"]) < horizon
        ]
        raw_snapshots = [
            row for row in cached.get("snapshots") or []
            if activation <= float(row["ts"]) < horizon
        ]
        selected_snapshot_indices: set[int] = set()
        if raw_snapshots:
            selected_snapshot_indices.add(0)
        prior_price_state: tuple[Any, Any] | None = None
        prior_minute: int | None = None
        for index, row in enumerate(raw_snapshots):
            price_state = (
                row.get("best_bid"),
                row.get("best_ask"),
            )
            minute = int((float(row["ts"]) - activation) // 60)
            if price_state != prior_price_state or minute != prior_minute:
                selected_snapshot_indices.add(index)
            prior_price_state = price_state
            prior_minute = minute
        pointer = -1
        for print_row in raw_prints:
            timestamp = float(print_row["ts"])
            while (
                pointer + 1 < len(raw_snapshots)
                and float(raw_snapshots[pointer + 1]["ts"]) <= timestamp
            ):
                pointer += 1
            if pointer >= 0:
                selected_snapshot_indices.add(pointer)
        for checkpoint in (
            activation + 3600,
            activation + 7200,
            horizon,
        ):
            pointer = -1
            while (
                pointer + 1 < len(raw_snapshots)
                and float(raw_snapshots[pointer + 1]["ts"]) <= checkpoint
            ):
                pointer += 1
            if pointer >= 0:
                selected_snapshot_indices.add(pointer)
        for index in sorted(selected_snapshot_indices):
            row = raw_snapshots[index]
            timestamp = float(row["ts"])
            observations.append({
                "kind": "book",
                "ts": timestamp,
                "bids": [list(value) for value in row.get("bids") or []],
                "asks": [list(value) for value in row.get("asks") or []],
                "own_bid_size_by_price": {},
                "source": str(row.get("source") or ""),
                "source_receipt_identity": (
                    f"{ticker}|book|{timestamp:.6f}"
                ),
            })
        for row in raw_prints:
            timestamp = float(row["ts"])
            identity = str(row["trade_id"])
            observations.append({
                "kind": "print",
                "ts": timestamp,
                "price": int(row["price"]),
                "size": float(row["size"]),
                "taker_side": str(row.get("taker_side") or ""),
                "trade_id": identity,
                "receipt_id": identity,
                "source": "normalized_public_true_print",
                "size_verified": True,
                "synthetic_transition": False,
                "own_order_fingerprint": False,
            })
        observations.sort(
            key=lambda row: (
                float(row["ts"]),
                0 if row["kind"] == "book" else 1,
                str(row.get("trade_id") or ""),
            )
        )
        top5 = bool(feature.get("top5_available")) and bool(
            cached.get("snapshots")
        )
        own_receipt = (
            feature.get("own_historical_order_volume_attributable")
            is False
        )
        legs.append({
            "leg_id": str(raw_leg["leg"]),
            "ticker": ticker,
            "role": role_by_ticker[ticker],
            "feature_availability": {
                "causal_role": role_available,
                "true_prints": True,
                "top5": top5,
                "own_order_fingerprints": own_receipt,
            },
            "feature_availability_receipt": {
                "causal_role": (
                    "T8_feature_role_or_first_causal_pair_BBO"
                    if role_available else "causal_pair_role_unavailable"
                ),
                "true_prints": "complete_bound_public_tape_ticker",
                "top5": (
                    "causal_top5_present" if top5
                    else "causal_top5_absent"
                ),
                "own_order_fingerprints": (
                    "verified_no_attributable_own_volume"
                    if own_receipt
                    else "unavailable"
                ),
            },
            "observations": observations,
        })
    return {
        "event_id": str(event["event_id"]),
        "event_date": str(event["event_date"]),
        "category": str(event["category"]),
        "policy_anchor_ts": anchor,
        "policy_anchor_observed_at_ts": observed,
        "policy_anchor_source": str(event["schedule_source"]),
        "policy_left_ts": left,
        "policy_decision_horizon_ts": anchor + corridor_seconds,
        "policy_corridor_seconds_after_anchor": corridor_seconds,
        "legs": legs,
    }


def decision_signature(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            key: row.get(key)
            for key in (
                "leg_id", "ts", "action", "reason", "price_cents",
                "quantity", "remaining_quantity", "posture",
                "reaim_cents", "base_sibling_order_cents",
                "reaim_sibling_order_cents",
            )
        }
        for row in result["order_stream"]
        if row["action"] in DECISION_ACTIONS
    ]


def event_summary(
    result: Mapping[str, Any],
    event: Mapping[str, Any],
) -> dict[str, Any]:
    actions = list(result["order_stream"])
    all_actions = Counter(str(row["action"]) for row in actions)
    reasons = Counter(str(row["reason"]) for row in actions)
    feature_censors: Counter[str] = Counter()
    for row in actions:
        if row["action"] == "feature_censor":
            values = row.get("missing_features") or [row["reason"]]
            feature_censors.update(map(str, values))
    decisions = Counter(
        str(row["action"]) for row in actions
        if row["action"] in {"place", "reprice", "cancel"}
    )
    by_leg: dict[str, Counter[str]] = defaultdict(Counter)
    for row in actions:
        if row["action"] in {"place", "reprice", "cancel"}:
            by_leg[str(row["ticker"])][str(row["action"])] += 1
    macro = [
        row for row in actions if row["action"] == "macro_bind"
    ]
    eligible_times = {float(row["eligible_ts"]) for row in macro}
    postures = {
        str(row.get("posture")) for row in actions
        if row["action"] in {"place", "reprice"}
    }
    cohort = [
        {
            "event_id": result["event_id"],
            "event_date": result["event_date"],
            "category": event["category"],
            "leg_id": row["leg_id"],
            "cohort_zone": row.get("cohort_zone"),
            "cohort_n": row.get("cohort_n"),
            "cohort_status": row.get("cohort_status"),
            "reason": row["reason"],
        }
        for row in actions
        if row["action"] in {"cohort_no_call", "cohort_steer"}
    ]
    missing = Counter()
    for leg in event["legs"]:
        for name, available in leg["feature_availability"].items():
            if available is not True:
                missing[name] += 1
    return {
        "event_id": result["event_id"],
        "event_date": result["event_date"],
        "terminal": result["event_terminal"],
        "eligible": result["event_terminal"] != "censored_feature",
        "feature_censors": dict(feature_censors),
        "all_action_counts": dict(all_actions),
        "reason_counts": dict(reasons),
        "decision_counts": dict(decisions),
        "per_leg_decisions": {
            leg: dict(counts) for leg, counts in by_leg.items()
        },
        "decision_sha256": sha256_json(decision_signature(result)),
        "stream_sha256": result["stream_sha256"],
        "cohort": cohort,
        "asynchronous_timing_exercised": len(eligible_times) > 1,
        "posture_exercised": bool(postures),
        "recut_exercised": any(
            row["action"] == "pair_recut" for row in actions
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
        "positive_size_prints_consumed": sum(
            int(
                row.get("positive_prints_consumed") or 0
            )
            for row in result.get("evidence_census_by_leg") or []
        ),
        "bbo_covered_legs": sum(
            any(obs["kind"] == "book" for obs in leg["observations"])
            for leg in event["legs"]
        ),
        "top5_covered_legs": sum(
            leg["feature_availability"]["top5"]
            for leg in event["legs"]
        ),
        "missing_feature_legs": dict(missing),
    }


def summarize_candidate(
    candidate_id: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    base_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    censored = Counter()
    decisions = Counter()
    missing = Counter()
    cohort_status = Counter()
    reaim_no_call = Counter()
    by_leg = Counter()
    for row in rows:
        censored.update(row["feature_censors"])
        decisions.update(row["decision_counts"])
        missing.update(row["missing_feature_legs"])
        for item in row["cohort"]:
            cohort_status[str(item["cohort_status"])] += 1
        reaim_no_call.update({
            reason: int(count)
            for reason, count in row["reason_counts"].items()
            if reason in {
                "required_sibling_policy_evidence_unavailable",
                "no_later_lawful_sibling_trigger",
            }
        })
        for leg, counts in row["per_leg_decisions"].items():
            for action, count in counts.items():
                by_leg[f"{leg}:{action}"] += int(count)
    distinct = sum(
        row["decision_sha256"] != base["decision_sha256"]
        for row, base in zip(rows, base_rows)
    )
    return {
        "candidate_id": candidate_id,
        "eligible_event_count": sum(bool(row["eligible"]) for row in rows),
        "censored_event_count": sum(not row["eligible"] for row in rows),
        "censor_reasons": dict(sorted(censored.items())),
        "cohort_NO_CALL_count": sum(
            count for status, count in cohort_status.items()
            if status.startswith("NO_CALL")
        ),
        "cohort_status_counts": dict(sorted(cohort_status.items())),
        "reaim_NO_CALL_count": sum(reaim_no_call.values()),
        "reaim_NO_CALL_reasons": dict(sorted(reaim_no_call.items())),
        "distinct_order_decisions_versus_base_events": distinct,
        "decision_counts": dict(sorted(decisions.items())),
        "per_leg_place_reprice_cancel": dict(sorted(by_leg.items())),
        "real_events_exercising": {
            family: [
                str(row["event_id"]) for row in rows if row[field]
            ]
            for family, field in (
                ("asynchronous_timing", "asynchronous_timing_exercised"),
                ("posture", "posture_exercised"),
                ("recut", "recut_exercised"),
                ("sibling_response", "sibling_response_exercised"),
                ("walk", "walk_exercised"),
            )
        },
        "positive_size_print_count_consumed": sum(
            int(row["positive_size_prints_consumed"]) for row in rows
        ),
        "BBO_covered_event_count": sum(
            row["bbo_covered_legs"] == 2 for row in rows
        ),
        "top5_covered_event_count": sum(
            row["top5_covered_legs"] == 2 for row in rows
        ),
        "missing_feature_leg_counts": dict(sorted(missing.items())),
        "event_stream_receipts": [
            {
                "event_id": row["event_id"],
                "decision_sha256": row["decision_sha256"],
                "stream_sha256": row["stream_sha256"],
                "terminal": row["terminal"],
            }
            for row in rows
        ],
        "cohort_availability_by_class_zone_event": [
            item for row in rows for item in row["cohort"]
        ],
        "scored": False,
        "metrics": None,
    }


def duplicate_groups(
    candidate_rows: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[list[str]]:
    bundles: dict[str, list[str]] = defaultdict(list)
    for candidate_id, rows in candidate_rows.items():
        bundles[sha256_json([
            row["decision_sha256"] for row in rows
        ])].append(candidate_id)
    return [
        sorted(ids) for ids in bundles.values() if len(ids) > 1
    ]


def family_matrix(
    candidate_summaries: Sequence[Mapping[str, Any]],
    candidate_rows: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    all_rows = [row for rows in candidate_rows.values() for row in rows]
    action_seen = Counter()
    reason_seen = Counter()
    for rows in candidate_rows.values():
        for row in rows:
            action_seen.update(row["all_action_counts"])
            reason_seen.update(row["reason_counts"])
    candidate_distinct = any(
        int(row["distinct_order_decisions_versus_base_events"]) > 0
        for row in candidate_summaries[1:]
    )
    matrix = []
    for family, expected_actions in FAMILY_ACTIONS.items():
        evaluated = any(action_seen[action] for action in expected_actions)
        available = evaluated
        decision_changing = False
        status = "available"
        if family == "cohort_steering":
            available = action_seen["cohort_steer"] > 0
            decision_changing = action_seen["cohort_steer"] > 0
            status = "available" if available else "unavailable_NO_CALL"
        elif family == "nonself_one_cent_walk":
            decision_changing = (
                reason_seen[
                    "verified_nonself_chain_exact_one_cent"
                ] > 0
            )
            available = decision_changing
            status = "available" if available else "inert_on_development"
        elif family == "first_fill_sibling_response":
            decision_changing = (
                action_seen["sibling_reaim_applied"] > 0
                and (
                    reason_seen[
                        "first_fill_sibling_reaim_later_trigger"
                    ] > 0
                    or reason_seen[
                        "first_fill_sibling_reaim_later_trigger_cancel"
                    ] > 0
                )
            )
            available = decision_changing
            status = "available" if available else "inert_on_development"
        elif family == "own_order_contribution_subtraction":
            decision_changing = (
                action_seen["contributed_volume_excluded"] > 0
            )
            available = True
            status = (
                "safety_law_no_attributable_own_volume"
                if not decision_changing else "available"
            )
        elif family == "asynchronous_divot_timing":
            decision_changing = any(
                row["asynchronous_timing_exercised"] for row in all_rows
            )
        elif family == "pair_divot_recut":
            decision_changing = any(
                row["recut_exercised"] for row in all_rows
            )
        elif family == "leg_specific_posture":
            decision_changing = candidate_distinct
        elif family == "causal_orientation":
            decision_changing = (
                reason_seen["causal_orientation_reaim_cancel"]
                + reason_seen["causal_orientation_reaim"] > 0
            )
        elif family == "causal_drift_recognition":
            decision_changing = (
                reason_seen["causal_T6_drift_recognition_cancel"]
                + reason_seen["causal_T6_drift_recognition"] > 0
            )
        elif family == "bbo_top5_pressure":
            decision_changing = candidate_distinct and evaluated
        elif family == "true_print_flow":
            decision_changing = (
                reason_seen["causal_true_print_micro_trigger"] > 0
            )
        matrix.append({
            "family_id": family,
            "loaded": True,
            "available": available,
            "evaluated": evaluated,
            "decision_changing": decision_changing,
            "actually_selected": False,
            "status": status,
            "counted_as_advertised_coverage": (
                available and decision_changing
            ),
        })
    matrix.append({
        "family_id": "start_boundary_evaluator",
        "loaded": True,
        "available": True,
        "evaluated": False,
        "decision_changing": False,
        "actually_selected": False,
        "status": "evaluation_only_not_policy_input",
        "counted_as_advertised_coverage": False,
    })
    return matrix


def _process_event_chunk(
    repo_text: str,
    cache_text: str,
    indexed_events: Sequence[tuple[int, Mapping[str, Any]]],
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    candidate_ids: Sequence[str],
    corridor: float,
) -> dict[str, list[dict[str, Any]]]:
    repo = Path(repo_text)
    cache_root = Path(cache_text)
    spec = instrument.load_candidate_spec(repo)
    policies = {
        candidate_id: instrument.candidate_policy(spec, candidate_id)
        for candidate_id in candidate_ids
    }
    surfaces = instrument.load_surfaces(repo)
    output: dict[str, list[dict[str, Any]]] = {
        candidate_id: [] for candidate_id in candidate_ids
    }
    for position, (event_index, event) in enumerate(indexed_events, 1):
        event_id = str(event["event_id"])
        cache = load_cache(cache_root / f"{event_id}.json.gz")
        normalized = normalize_event(
            event, cache, feature_map, corridor_seconds=corridor
        )
        for candidate_id in candidate_ids:
            result = instrument.CausalInstrument(
                surfaces, policies[candidate_id]
            ).run(normalized)
            row = event_summary(result, normalized)
            row["_event_index"] = event_index
            output[candidate_id].append(row)
        if position % 50 == 0 or position == len(indexed_events):
            print(compact({
                "stage": "real_capability_worker",
                "chunk_events": position,
                "chunk_size": len(indexed_events),
                "candidate_count": len(candidate_ids),
                "scored": False,
            }), flush=True)
    return output


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.resolve()
    binding.validate_bound_inputs(
        repo,
        args.binding_manifest.resolve(),
        events_path=args.events.resolve(),
        prints_path=args.prints.resolve(),
        tape_manifest_path=args.tape_manifest.resolve(),
        cache_root=args.market_cache.resolve(),
    )
    events = read_jsonl(args.events.resolve())
    features = [
        row for row in read_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in features
    }
    spec = instrument.load_candidate_spec(repo)
    candidate_ids = list(spec["candidate_ids"])
    if not candidate_ids:
        raise CapabilityError("candidate allowlist is empty")
    candidate_rows: dict[str, list[dict[str, Any]]] = {
        candidate_id: [] for candidate_id in candidate_ids
    }
    corridor = float(
        spec["common_parameters"]["policy_corridor_seconds_after_anchor"]
    )
    indexed = list(enumerate(events))
    workers = max(1, min(int(args.workers), len(indexed)))
    chunks = [
        indexed[index::workers] for index in range(workers)
    ]
    if workers == 1:
        results = [
            _process_event_chunk(
                str(repo),
                str(args.market_cache.resolve()),
                chunks[0],
                feature_map,
                candidate_ids,
                corridor,
            )
        ]
    else:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=workers
        ) as executor:
            futures = [
                executor.submit(
                    _process_event_chunk,
                    str(repo),
                    str(args.market_cache.resolve()),
                    chunk,
                    feature_map,
                    candidate_ids,
                    corridor,
                )
                for chunk in chunks
            ]
            results = [future.result() for future in futures]
    for result in results:
        for candidate_id, rows in result.items():
            candidate_rows[candidate_id].extend(rows)
    for rows in candidate_rows.values():
        rows.sort(key=lambda row: int(row["_event_index"]))
        for row in rows:
            row.pop("_event_index", None)

    duplicates = duplicate_groups(candidate_rows)
    base_id = candidate_ids[0]
    base_rows = candidate_rows[base_id]
    summaries = [
        summarize_candidate(
            candidate_id,
            candidate_rows[candidate_id],
            base_rows=base_rows,
        )
        for candidate_id in candidate_ids
    ]
    if any(row["eligible_event_count"] == 0 for row in summaries):
        raise CapabilityError("retained candidate has zero real eligibility")
    if duplicates and not args.discovery_mode:
        raise CapabilityError(
            "duplicate/inert retained candidates: " + compact(duplicates)
        )
    if not args.discovery_mode and len(candidate_ids) > 1 and any(
        all(
            candidate_rows[candidate_id][i]["decision_sha256"]
            == candidate_rows[other][i]["decision_sha256"]
            for i in range(binding.D_REQUIRED)
        )
        for pos, candidate_id in enumerate(candidate_ids)
        for other in candidate_ids[pos + 1:]
    ):
        raise CapabilityError("pairwise candidate uniqueness gate failed")

    matrix = family_matrix(summaries, candidate_rows)
    result = {
        "schema_version": VERSION,
        "D": binding.D_REQUIRED,
        "development_dates": binding.DEV_DATES,
        "candidate_ids": candidate_ids,
        "base_candidate_id": base_id,
        "candidate_count": len(candidate_ids),
        "candidate_summaries": summaries,
        "duplicate_candidate_groups": duplicates,
        "candidate_gate_pass": not duplicates,
        "discovery_mode": bool(args.discovery_mode),
        "family_capability_matrix": matrix,
        "family_coverage_claim_count": sum(
            bool(row["counted_as_advertised_coverage"]) for row in matrix
        ),
        "policy_clock": {
            "anchor": "timestamped exchange schedule",
            "corridor_seconds_after_anchor": corridor,
            "evaluation_real_start_access": False,
        },
        "positive_size_gate": {
            "cache_nonpositive_or_malformed_rows": 0,
            "instrument_rejects_nonpositive_missing_malformed_synthetic": True,
        },
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "performance_ablation_performed": False,
        "metrics": None,
        "holdout_opened": False,
        "holdout_queried": False,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--binding-manifest", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--prints", type=Path, required=True)
    parser.add_argument("--tape-manifest", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--discovery-mode", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    value = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(compact({
        "output": str(args.output),
        "D": value["D"],
        "candidate_count": value["candidate_count"],
        "candidate_gate_pass": value["candidate_gate_pass"],
        "scored": False,
        "holdout_queried": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
