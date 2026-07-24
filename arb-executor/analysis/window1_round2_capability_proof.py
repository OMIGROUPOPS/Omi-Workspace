#!/usr/bin/env python3
"""Synthetic causal-fixture proofs for the frozen Round-2 instrument.

The fixtures contain no development or holdout outcomes.  Each advertised
family passes only when enabling it changes an eligible order decision, not
merely metadata.  The module also proves that T6 recognition cannot change any
decision timestamped before T6.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import window1_round2_instrument as instrument


VERSION = "window1-round2-capability-proof-v3"
BASE_CANDIDATE = "r2_full_os__walk_park__hold"
DECISION_ACTIONS = {
    "place",
    "reprice",
    "cancel",
}


def synthetic_surfaces() -> instrument.SurfaceBundle:
    bands = [
        {
            "band": "ATP_MAIN-B1",
            "direction": "flat",
            "anchor_med": 40,
        },
        {
            "band": "ATP_MAIN-B2",
            "direction": "flat",
            "anchor_med": 59,
        },
        {
            "band": "ATP_MAIN-B3",
            "direction": "flat",
            "anchor_med": 52,
        },
        {
            "band": "ATP_MAIN-B4",
            "direction": "flat",
            "anchor_med": 34,
        },
    ]
    divot_rows = {
        "ATP_MAIN-B1": {
            "depth_p50": 2,
            "depth_p90": 5,
            "dur_p50_s": 10000,
        },
        "ATP_MAIN-B2": {
            "depth_p50": 2,
            "depth_p90": 6,
            "dur_p50_s": 10000,
        },
        "ATP_MAIN-B3": {
            "depth_p50": 7,
            "depth_p90": 9,
            "dur_p50_s": 10000,
        },
        "ATP_MAIN-B4": {
            "depth_p50": 6,
            "depth_p90": 8,
            "dur_p50_s": 10000,
        },
    }
    recut = {}
    for price in range(1, 100):
        recut[str(price)] = {
            "n": 40,
            "edge_p50": (
                6 if price <= 52 else 2
            ),
            "t_deep_p50": (
                -360 if price <= 49 else -420
            ),
        }
    cohort_rows = [
        {
            "cat": "ATP_MAIN",
            "px": 40 if index < 35 else 60,
            "cell_edge": 5,
        }
        for index in range(70)
    ]
    return instrument.SurfaceBundle(
        band_map={
            "cats": {
                "ATP_MAIN": {
                    "thin": False,
                    "bands": bands,
                }
            }
        },
        divot={"bands": divot_rows},
        drift={
            "recognition": {
                "ATP_MAIN|h6": {
                    "a75|dn3|d3": {
                        "top": "ATP_MAIN-B3",
                        "purity": 0.8,
                    },
                    "a50|flat|d0": {
                        "top": "ATP_MAIN-B1",
                        "purity": 0.8,
                    },
                }
            }
        },
        recut={"ATP_MAIN": recut},
        orientation={
            "cats": {
                "ATP_MAIN": {
                    "1|hi|mid": {
                        "n": 40,
                        "dog_rise_rate": 0.8,
                    }
                }
            }
        },
        cohort={"rows": cohort_rows},
    )


def book(
    timestamp: float,
    bid: int,
    ask: int,
    *,
    bid_size: float = 10,
    ask_size: float = 50,
    own: Mapping[str, float] | None = None,
    second_bid: tuple[int, float] | None = None,
) -> dict[str, Any]:
    bids = [[bid, bid_size]]
    if second_bid is not None:
        bids.append([second_bid[0], second_bid[1]])
    return {
        "kind": "book",
        "ts": timestamp,
        "bids": bids,
        "asks": [[ask, ask_size]],
        "own_bid_size_by_price": dict(own or {}),
    }


def trade(
    timestamp: float,
    price: int,
    *,
    size: float = 1,
    trade_id: str,
    own: bool = False,
) -> dict[str, Any]:
    return {
        "kind": "print",
        "ts": timestamp,
        "price": price,
        "size": size,
        "taker_side": "no",
        "trade_id": trade_id,
        "receipt_id": trade_id,
        "source": "normalized_public_true_print",
        "size_verified": True,
        "synthetic_transition": False,
        "own_order_fingerprint": own,
    }


def base_event() -> dict[str, Any]:
    left = 1_000_000.0
    anchor = left + 8 * 3600
    leg_a = [
        book(
            left + 10, 60, 62, own={"60": 5},
            bid_size=5, second_bid=(59, 10),
        ),
        trade(left + 3000, 60, trade_id="A-BASE-1"),
        trade(left + 3200, 60, trade_id="A-BASE-2"),
        trade(left + 3400, 60, trade_id="A-BASE-3"),
        book(
            left + 3590, 58, 60, bid_size=5,
            own={"58": 5}, second_bid=(57, 10),
        ),
        trade(left + 3610, 54, trade_id="A-DIVOT"),
        trade(left + 3700, 55, trade_id="A-CHAIN-1"),
        trade(left + 3710, 56, trade_id="A-CHAIN-2"),
        book(left + 7100, 52, 60),
        trade(left + 7300, 40, size=20, trade_id="A-FILL"),
    ]
    leg_b = [
        book(left + 10, 40, 42),
        trade(left + 100, 40, trade_id="B-BASE-1"),
        trade(left + 200, 40, trade_id="B-BASE-2"),
        trade(left + 300, 44, trade_id="B-BASE-3"),
        trade(left + 6500, 40, trade_id="B-LATE-BASE-1"),
        trade(left + 6700, 40, trade_id="B-LATE-BASE-2"),
        trade(left + 6900, 40, trade_id="B-LATE-BASE-3"),
        book(left + 7190, 38, 40),
        trade(left + 7210, 34, trade_id="B-DIVOT"),
        trade(left + 7600, 36, trade_id="B-LATE-1"),
        trade(left + 7610, 37, trade_id="B-LATE-2"),
    ]
    return {
        "event_id": "FIXTURE-R2-BASE",
        "event_date": "2026-07-12",
        "category": "ATP_MAIN",
        "policy_anchor_ts": anchor,
        "policy_anchor_observed_at_ts": left - 60,
        "policy_anchor_source": "fixture_causal_schedule",
        "policy_left_ts": left,
        "policy_decision_horizon_ts": anchor,
        "policy_corridor_seconds_after_anchor": 0,
        "legs": [
            {
                "leg_id": "A",
                "ticker": "FIXTURE-A",
                "role": "favorite",
                "feature_availability": {
                    "causal_role": True,
                    "true_prints": True,
                    "top5": True,
                    "own_order_fingerprints": True,
                },
                "observations": leg_a,
            },
            {
                "leg_id": "B",
                "ticker": "FIXTURE-B",
                "role": "underdog",
                "feature_availability": {
                    "causal_role": True,
                    "true_prints": True,
                    "top5": True,
                    "own_order_fingerprints": True,
                },
                "observations": leg_b,
            },
        ],
    }


def timing_event() -> dict[str, Any]:
    event = base_event()
    event["event_id"] = "FIXTURE-R2-ASYNC"
    left = float(event["policy_left_ts"])
    for leg, anchor in zip(event["legs"], (60, 40)):
        leg["observations"] = [
            book(left + 10, anchor, anchor + 2),
            trade(left + 100, anchor, trade_id=f"{leg['leg_id']}-T1"),
            trade(left + 200, anchor, trade_id=f"{leg['leg_id']}-T2"),
            trade(left + 300, anchor, trade_id=f"{leg['leg_id']}-T3"),
            trade(
                left + 400, anchor - 4,
                trade_id=f"{leg['leg_id']}-DIVOT",
            ),
            trade(
                left + (3500 if leg["leg_id"] == "A" else 7100),
                anchor,
                trade_id=f"{leg['leg_id']}-FLOW-REFRESH",
            ),
            book(
                left + (3610 if leg["leg_id"] == "A" else 7210),
                anchor - 1,
                anchor + 1,
            ),
        ]
    return event


def no_flow_event() -> dict[str, Any]:
    event = base_event()
    event["event_id"] = "FIXTURE-R2-FLOW"
    left = float(event["policy_left_ts"])
    event["legs"][0]["role"] = "underdog"
    event["legs"][1]["role"] = "favorite"
    event["legs"][0]["observations"] = [
        book(left + 10, 40, 42),
        book(left + 7210, 40, 42),
    ]
    event["legs"][1]["observations"] = [
        book(left + 10, 60, 62),
    ]
    return event


def reaim_event() -> dict[str, Any]:
    event = base_event()
    event["event_id"] = "FIXTURE-R2-LATER-SIBLING-REAIM"
    left = float(event["policy_left_ts"])
    event["legs"][1]["observations"].append(
        book(left + 7500, 39, 42)
    )
    return event


def schedule_only_event() -> dict[str, Any]:
    event = base_event()
    event["event_id"] = "FIXTURE-R2-SCHEDULE"
    return event


def missing_feature_event() -> dict[str, Any]:
    event = base_event()
    event["event_id"] = "FIXTURE-R2-MISSING-FEATURE"
    event["legs"][0]["feature_availability"]["top5"] = False
    return event


def decision_signature(
    result: Mapping[str, Any],
    *,
    before: float | None = None,
    after_or_at: float | None = None,
) -> list[dict[str, Any]]:
    output = []
    for row in result["order_stream"]:
        timestamp = float(row["ts"])
        if row["action"] not in DECISION_ACTIONS:
            continue
        if before is not None and timestamp >= before:
            continue
        if after_or_at is not None and timestamp < after_or_at:
            continue
        output.append({
            key: row.get(key)
            for key in (
                "leg_id", "ts", "action", "reason", "price_cents",
                "posture", "reaim_cents",
            )
        })
    return output


def run_policy(
    repo: Path,
    surfaces: instrument.SurfaceBundle,
    event: Mapping[str, Any],
    candidate_id: str = BASE_CANDIDATE,
    ablations: Iterable[str] = (),
) -> dict[str, Any]:
    spec = instrument.load_candidate_spec(repo)
    policy = instrument.candidate_policy(
        spec, candidate_id, ablations=ablations
    )
    return instrument.CausalInstrument(surfaces, policy).run(event)


def compare_ablation(
    repo: Path,
    surfaces: instrument.SurfaceBundle,
    event: Mapping[str, Any],
    family: str,
    *,
    candidate_id: str = BASE_CANDIDATE,
) -> dict[str, Any]:
    enabled = run_policy(repo, surfaces, event, candidate_id)
    disabled = run_policy(
        repo,
        surfaces,
        event,
        candidate_id,
        [f"without_{family}"],
    )
    enabled_signature = decision_signature(enabled)
    disabled_signature = decision_signature(disabled)
    return {
        "family_id": family,
        "eligible_fixture": str(event["event_id"]),
        "enabled_decision_sha256": instrument.sha256_json(enabled_signature),
        "ablated_decision_sha256": instrument.sha256_json(disabled_signature),
        "decision_changing": enabled_signature != disabled_signature,
        "enabled_decision_count": len(enabled_signature),
        "ablated_decision_count": len(disabled_signature),
    }


def capability_proof(repo: Path) -> dict[str, Any]:
    surfaces = synthetic_surfaces()
    event = base_event()
    rows = []
    rows.append(compare_ablation(
        repo, surfaces, timing_event(), "asynchronous_divot_timing"
    ))

    park = run_policy(
        repo, surfaces, event, "r2_causal_steer__park_join__hold"
    )
    walk = run_policy(
        repo, surfaces, event, "r2_full_os__walk_park__hold"
    )
    rows.append({
        "family_id": "leg_specific_posture",
        "eligible_fixture": event["event_id"],
        "enabled_decision_sha256": instrument.sha256_json(
            decision_signature(walk)
        ),
        "ablated_decision_sha256": instrument.sha256_json(
            decision_signature(park)
        ),
        "decision_changing": (
            decision_signature(walk) != decision_signature(park)
        ),
        "enabled_decision_count": len(decision_signature(walk)),
        "ablated_decision_count": len(decision_signature(park)),
    })
    reaim_fixture = reaim_event()
    reaim_hold = run_policy(
        repo,
        surfaces,
        reaim_fixture,
        "r2_full_os__walk_park__hold",
    )
    reaim_enabled = run_policy(
        repo,
        surfaces,
        reaim_fixture,
        "r2_full_os__walk_park__reaim",
    )
    applied = next(
        row for row in reaim_enabled["order_stream"]
        if row["action"] == "sibling_reaim_applied"
    )
    trigger_ts = float(applied["ts"])
    hold_prefix = decision_signature(reaim_hold, before=trigger_ts)
    reaim_prefix = decision_signature(reaim_enabled, before=trigger_ts)
    rows.append({
        "family_id": "first_fill_sibling_response",
        "eligible_fixture": reaim_fixture["event_id"],
        "proof_mode": "hold_vs_reaim_at_later_sibling_owned_trigger",
        "enabled_decision_sha256": instrument.sha256_json(
            decision_signature(reaim_enabled)
        ),
        "ablated_decision_sha256": instrument.sha256_json(
            decision_signature(reaim_hold)
        ),
        "decision_changing": (
            decision_signature(reaim_enabled)
            != decision_signature(reaim_hold)
            and hold_prefix == reaim_prefix
            and applied["exact_reaim_difference_cents"] == 1
        ),
        "earlier_order_decisions_byte_identical": (
            hold_prefix == reaim_prefix
        ),
        "first_leg_fill_ts": applied["first_leg_fill_ts"],
        "sibling_lawful_trigger_ts": applied["ts"],
        "base_sibling_order_cents": (
            applied["base_sibling_order_cents"]
        ),
        "reaim_sibling_order_cents": (
            applied["reaim_sibling_order_cents"]
        ),
        "exact_reaim_difference_cents": (
            applied["exact_reaim_difference_cents"]
        ),
        "enabled_decision_count": len(
            decision_signature(reaim_enabled)
        ),
        "ablated_decision_count": len(
            decision_signature(reaim_hold)
        ),
    })
    for family in (
        "nonself_one_cent_walk",
        "pair_divot_recut",
        "causal_orientation",
        "causal_drift_recognition",
        "cohort_steering",
        "bbo_top5_pressure",
    ):
        rows.append(compare_ablation(repo, surfaces, event, family))

    # True flow and own-volume subtraction are evidence/safety laws, not
    # ablatable placement shortcuts.  Their fixtures vary the causal input
    # while keeping the exact same frozen policy.
    no_flow = no_flow_event()
    with_flow = copy.deepcopy(no_flow)
    left = float(with_flow["policy_left_ts"])
    with_flow["legs"][0]["observations"].append(
        trade(left + 7205, 40, trade_id="FLOW-CONFIRM")
    )
    flow_enabled = run_policy(
        repo,
        surfaces,
        with_flow,
        "r2_causal_steer__park_join__hold",
    )
    flow_absent = run_policy(
        repo,
        surfaces,
        no_flow,
        "r2_causal_steer__park_join__hold",
    )
    rows.append({
        "family_id": "true_print_flow",
        "eligible_fixture": "FIXTURE-R2-FLOW causal-signal contrast",
        "proof_mode": "same_policy_causal_input_contrast",
        "enabled_decision_sha256": instrument.sha256_json(
            decision_signature(flow_enabled)
        ),
        "ablated_decision_sha256": instrument.sha256_json(
            decision_signature(flow_absent)
        ),
        "decision_changing": (
            decision_signature(flow_enabled)
            != decision_signature(flow_absent)
        ),
        "enabled_decision_count": len(decision_signature(flow_enabled)),
        "ablated_decision_count": len(decision_signature(flow_absent)),
    })

    own_present = base_event()
    own_external = copy.deepcopy(own_present)
    for observation in own_external["legs"][0]["observations"]:
        if observation["kind"] == "book":
            observation["own_bid_size_by_price"] = {}
    own_subtracted = run_policy(repo, surfaces, own_present)
    same_size_external = run_policy(repo, surfaces, own_external)
    rows.append({
        "family_id": "own_order_contribution_subtraction",
        "eligible_fixture": (
            "FIXTURE-R2-BASE fingerprinted-own versus same-size external"
        ),
        "proof_mode": "same_policy_provenance_contrast",
        "enabled_decision_sha256": instrument.sha256_json(
            decision_signature(own_subtracted)
        ),
        "ablated_decision_sha256": instrument.sha256_json(
            decision_signature(same_size_external)
        ),
        "decision_changing": (
            decision_signature(own_subtracted)
            != decision_signature(same_size_external)
        ),
        "enabled_decision_count": len(decision_signature(own_subtracted)),
        "ablated_decision_count": len(decision_signature(same_size_external)),
    })

    # Exact T8/T6 proof: change only the frozen recognition mapping.  Since
    # recognition is read at the T6 checkpoint, the complete decision prefix
    # must be identical while the post-T6 stream must differ.
    alternate_drift = copy.deepcopy(surfaces.drift)
    alternate_drift["recognition"]["ATP_MAIN|h6"]["a75|dn3|d3"] = {
        "top": "ATP_MAIN-B1",
        "purity": 0.8,
    }
    alternate = instrument.SurfaceBundle(
        band_map=surfaces.band_map,
        divot=surfaces.divot,
        drift=alternate_drift,
        recut=surfaces.recut,
        orientation=surfaces.orientation,
        cohort=surfaces.cohort,
    )
    first = run_policy(repo, surfaces, event)
    second = run_policy(repo, alternate, event)
    checkpoint = float(event["policy_left_ts"]) + 7200
    prefix_first = decision_signature(first, before=checkpoint)
    prefix_second = decision_signature(second, before=checkpoint)
    suffix_first = decision_signature(first, after_or_at=checkpoint)
    suffix_second = decision_signature(second, after_or_at=checkpoint)
    lookahead = {
        "schema_version": "window1-round2-t8-t6-lookahead-proof-v1",
        "fixture": event["event_id"],
        "T8_left_ts": event["policy_left_ts"],
        "T6_recognition_ts": checkpoint,
        "changed_input": "recognition mapping only",
        "pre_T6_decision_sha256_a": instrument.sha256_json(prefix_first),
        "pre_T6_decision_sha256_b": instrument.sha256_json(prefix_second),
        "pre_T6_decisions_identical": prefix_first == prefix_second,
        "post_T6_decision_sha256_a": instrument.sha256_json(suffix_first),
        "post_T6_decision_sha256_b": instrument.sha256_json(suffix_second),
        "post_T6_decisions_differ": suffix_first != suffix_second,
        "future_information_used_before_T6": prefix_first != prefix_second,
    }

    missing = run_policy(repo, surfaces, missing_feature_event())
    missing_terminals = [
        row["reason"] for row in missing["order_stream"]
        if row["action"] == "terminal"
    ]
    missing_feature_proof = {
        "fixture": "FIXTURE-R2-MISSING-FEATURE",
        "event_terminal": missing["event_terminal"],
        "leg_terminals": missing_terminals,
        "missing_feature_became_nonfill": (
            missing["event_terminal"] != "censored_feature"
        ),
    }

    failed = [
        row["family_id"] for row in rows
        if row["decision_changing"] is not True
    ]
    gate_pass = (
        not failed
        and lookahead["pre_T6_decisions_identical"]
        and lookahead["post_T6_decisions_differ"]
        and not lookahead["future_information_used_before_T6"]
        and missing["event_terminal"] == "censored_feature"
        and not missing_feature_proof["missing_feature_became_nonfill"]
    )
    return {
        "schema_version": VERSION,
        "fixture_data": "synthetic_only_no_development_or_holdout_outcomes",
        "advertised_family_count": len(rows),
        "family_capability_matrix": rows,
        "failed_or_inert_families": failed,
        "t8_t6_lookahead_proof": lookahead,
        "missing_feature_proof": missing_feature_proof,
        "gate_pass": gate_pass,
        "scoring_performed": False,
        "holdout_queried": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    result = capability_proof(repo)
    raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output
        if not output.is_absolute():
            output = repo / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(raw, encoding="utf-8", newline="\n")
    else:
        print(raw, end="")
    return 0 if result["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
