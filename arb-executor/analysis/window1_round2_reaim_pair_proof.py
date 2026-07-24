#!/usr/bin/env python3
"""Prove each restored reaim variant on bound real development events."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import window1_round2_data_binding as binding
import window1_round2_instrument as instrument
import window1_round2_real_capability as capability


VERSION = "window1-round2-reaim-pair-proof-v1"
PAIRS = [
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


class ReaimProofError(RuntimeError):
    """Raised when a restored reaim pair lacks a real order witness."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def order_prefix(
    result: Mapping[str, Any], before: float,
) -> list[dict[str, Any]]:
    return [
        {
            key: row.get(key)
            for key in (
                "leg_id", "ticker", "ts", "action", "reason",
                "price_cents", "quantity", "remaining_quantity",
                "posture",
            )
        }
        for row in result["order_stream"]
        if row["action"] in ORDER_ACTIONS
        and float(row["ts"]) < before
    ]


def active_price_after(
    leg_stream: Sequence[Mapping[str, Any]], timestamp: float,
) -> int | None:
    active: int | None = None
    for row in leg_stream:
        if float(row["ts"]) > timestamp:
            break
        action = str(row["action"])
        if action in {"place", "reprice"}:
            active = int(row["price_cents"])
        elif action == "cancel":
            active = None
        elif action == "fill_observed" and row.get("complete") is True:
            active = None
    return active


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
    receipt = json.loads(
        args.capability_receipt.read_text(encoding="utf-8")
    )
    if (
        receipt.get("D") != binding.D_REQUIRED
        or receipt.get("candidate_count") != 8
        or receipt.get("candidate_gate_pass") is not True
        or receipt.get("candidate_scoring_performed") is not False
        or receipt.get("metrics") is not None
    ):
        raise ReaimProofError("eight-candidate capability receipt failed")
    summaries = {
        str(row["candidate_id"]): row
        for row in receipt["candidate_summaries"]
    }
    events = {
        str(row["event_id"]): row
        for row in capability.read_jsonl(args.events.resolve())
    }
    features = [
        row for row in capability.read_jsonl(
            repo / binding.FEATURE_LEDGER
        )
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in features
    }
    spec = instrument.load_candidate_spec(repo)
    surfaces = instrument.load_surfaces(repo)
    corridor = float(
        spec["common_parameters"]["policy_corridor_seconds_after_anchor"]
    )
    pair_rows = []
    for base_id, reaim_id in PAIRS:
        if base_id not in summaries or reaim_id not in summaries:
            raise ReaimProofError(f"candidate pair missing: {reaim_id}")
        base_summary = summaries[base_id]
        reaim_summary = summaries[reaim_id]
        base_receipts = {
            str(row["event_id"]): row["decision_sha256"]
            for row in base_summary["event_stream_receipts"]
        }
        reaim_receipts = {
            str(row["event_id"]): row["decision_sha256"]
            for row in reaim_summary["event_stream_receipts"]
        }
        changed_ids = [
            event_id for event_id in sorted(base_receipts)
            if base_receipts[event_id] != reaim_receipts[event_id]
        ]
        if not changed_ids:
            raise ReaimProofError(f"reaim is order-inert: {reaim_id}")
        applied_event_ids = sorted(
            reaim_summary["real_events_exercising"][
                "sibling_response"
            ]
        )
        if changed_ids != applied_event_ids:
            raise ReaimProofError(
                "order difference without exact +1 applied receipt: "
                + reaim_id
            )
        witness = None
        for event_id in changed_ids:
            event = events[event_id]
            normalized = capability.normalize_event(
                event,
                capability.load_cache(
                    args.market_cache.resolve() / f"{event_id}.json.gz"
                ),
                feature_map,
                corridor_seconds=corridor,
            )
            base = instrument.run_event(
                repo, normalized, base_id, surfaces=surfaces
            )
            reaim = instrument.run_event(
                repo, normalized, reaim_id, surfaces=surfaces
            )
            applied_rows = [
                row for row in reaim["order_stream"]
                if row["action"] == "sibling_reaim_applied"
            ]
            for applied in applied_rows:
                trigger = float(applied["ts"])
                leg_id = str(applied["leg_id"])
                base_prefix = order_prefix(base, trigger)
                reaim_prefix = order_prefix(reaim, trigger)
                base_price = active_price_after(
                    base["leg_streams"][leg_id], trigger
                )
                reaim_price = active_price_after(
                    reaim["leg_streams"][leg_id], trigger
                )
                macro = next(
                    row for row in reaim["leg_streams"][leg_id]
                    if row["action"] == "macro_bind"
                )
                first_fill = [
                    row for row in reaim["order_stream"]
                    if row["action"] == "fill_observed"
                    and row.get("complete") is True
                    and row["leg_id"] == applied["first_filled_leg"]
                    and float(row["ts"]) == float(
                        applied["first_leg_fill_ts"]
                    )
                ]
                order_action = [
                    row for row in reaim["leg_streams"][leg_id]
                    if float(row["ts"]) == trigger
                    and row["action"] in {"place", "reprice"}
                    and row["reason"]
                    == "first_fill_sibling_reaim_later_trigger"
                ]
                if (
                    base_prefix == reaim_prefix
                    and first_fill
                    and order_action
                    and trigger > float(applied["first_leg_fill_ts"])
                    and trigger >= float(macro["eligible_ts"])
                    and base_price
                    == int(applied["base_sibling_order_cents"])
                    and reaim_price
                    == int(applied["reaim_sibling_order_cents"])
                    and reaim_price == base_price + 1
                    and all(
                        applied.get(name) is True for name in (
                            "price_guard_passed",
                            "par_guard_passed",
                            "band_guard_passed",
                            "maximum_cost_guard_passed",
                        )
                    )
                ):
                    witness = {
                        "event_id": event_id,
                        "event_date": event["event_date"],
                        "sibling_leg_id": leg_id,
                        "sibling_ticker": applied["ticker"],
                        "first_filled_leg_id": (
                            applied["first_filled_leg"]
                        ),
                        "first_leg_fill_timestamp": (
                            applied["first_leg_fill_ts"]
                        ),
                        "sibling_later_lawful_trigger_timestamp": trigger,
                        "sibling_eligibility_timestamp": (
                            macro["eligible_ts"]
                        ),
                        "base_sibling_order_cents": base_price,
                        "reaim_sibling_order_cents": reaim_price,
                        "exact_reaim_difference_cents": (
                            reaim_price - base_price
                        ),
                        "earlier_order_decisions_byte_identical": True,
                        "earlier_order_decisions_sha256": (
                            sha256_json(base_prefix)
                        ),
                        "trigger_action": order_action[-1],
                        "guard_proof": {
                            name: applied[name] for name in (
                                "price_guard_passed",
                                "par_guard_passed",
                                "band_guard_passed",
                                "maximum_cost_guard_passed",
                            )
                        },
                    }
                    break
            if witness is not None:
                break
        if witness is None:
            raise ReaimProofError(
                f"no lawful real +1 witness: {reaim_id}"
            )
        pair_rows.append({
            "base_candidate_id": base_id,
            "reaim_candidate_id": reaim_id,
            "real_D804_events_with_order_change": len(changed_ids),
            "changed_event_ids": changed_ids,
            "exact_plus_one_applied_event_ids": applied_event_ids,
            "every_changed_event_has_exact_plus_one_applied_receipt": True,
            "base_counts": {
                "eligible": base_summary["eligible_event_count"],
                "censored": base_summary["censored_event_count"],
                "cohort_NO_CALL": base_summary["cohort_NO_CALL_count"],
                "reaim_NO_CALL": base_summary["reaim_NO_CALL_count"],
            },
            "reaim_counts": {
                "eligible": reaim_summary["eligible_event_count"],
                "censored": reaim_summary["censored_event_count"],
                "cohort_NO_CALL": reaim_summary["cohort_NO_CALL_count"],
                "reaim_NO_CALL": reaim_summary["reaim_NO_CALL_count"],
            },
            "witness": witness,
        })
    return {
        "schema_version": VERSION,
        "D": binding.D_REQUIRED,
        "candidate_pair_count": len(pair_rows),
        "pairs": pair_rows,
        "all_pairs_real_order_changing": True,
        "sibling_hold_bookkeeping_counted_as_order_witness": False,
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "performance_ablation_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
        "gate_pass": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--binding-manifest", type=Path, required=True)
    parser.add_argument("--capability-receipt", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--prints", type=Path, required=True)
    parser.add_argument("--tape-manifest", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
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
        "pair_count": value["candidate_pair_count"],
        "gate_pass": value["gate_pass"],
        "scored": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
