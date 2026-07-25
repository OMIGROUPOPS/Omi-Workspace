#!/usr/bin/env python3
"""Score-separated Round-4 opportunity and causal-reference diagnostics.

This module may read ex-post scorer references, but it is unreachable from the
Round-4 policy module: the policy does not import it, and this module never
returns data to policy generation.  It does not invoke the frozen scorer and
does not aggregate C/PC/S/IC performance.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import window1_round2_data_binding as binding
import window1_round2_instrument as r2
import window1_round2_real_capability as r2cap
import window1_round3_prerun_builder as r3builder
import window1_round4_instrument as r4


VERSION = "window1-round4-score-separated-diagnostics-v1"
R3_STREAMS = (
    ".claude/window1_round3_prerun_20260725/"
    "FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz"
)


class DiagnosticError(RuntimeError):
    pass


class ShardedGzipJsonlWriter:
    """Write exactly two deterministic 402-event gzip shards."""

    def __init__(self, base_path: Path, rows_per_shard: int = 402) -> None:
        self.base_path = base_path
        self.rows_per_shard = rows_per_shard
        self.row_count = 0
        self.paths: list[Path] = []
        self._raw = None
        self._gzip = None
        self._text = None

    def _open_shard(self) -> None:
        index = len(self.paths) + 1
        name = self.base_path.name
        if not name.endswith(".jsonl.gz"):
            raise DiagnosticError("opportunity path must end .jsonl.gz")
        path = self.base_path.with_name(
            name.removesuffix(".jsonl.gz") + f"_{index:02d}.jsonl.gz"
        )
        self.paths.append(path)
        self._raw = path.open("wb")
        self._gzip = gzip.GzipFile(
            filename="", mode="wb", fileobj=self._raw, mtime=0
        )
        self._text = io.TextIOWrapper(
            self._gzip, encoding="utf-8", newline="\n"
        )

    def _close_shard(self) -> None:
        if self._text is not None:
            self._text.close()
        self._text = None
        self._gzip = None
        self._raw = None

    def write(self, value: str) -> None:
        if self.row_count % self.rows_per_shard == 0:
            self._close_shard()
            self._open_shard()
        if self._text is None:
            raise DiagnosticError("shard writer is closed")
        self._text.write(value)
        self.row_count += 1

    def __enter__(self) -> "ShardedGzipJsonlWriter":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._close_shard()


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _quantile(values: Sequence[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(map(float, values))
    index = (len(ordered) - 1) * fraction
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _sign(value: float) -> str:
    if value < 0:
        return "negative"
    if value > 0:
        return "positive"
    return "zero"


def _valid_prints(
    leg: Mapping[str, Any], left: float, horizon: float,
) -> list[dict[str, Any]]:
    output = []
    seen = set()
    for row in leg.get("observations") or []:
        if row.get("kind") != "print":
            continue
        timestamp = float(row["ts"])
        if not left <= timestamp < horizon:
            continue
        valid, _ = r2.positive_public_print(row)
        identity = str(
            row.get("trade_id") or row.get("receipt_id") or ""
        )
        if (
            not valid
            or not identity
            or identity in seen
            or row.get("own_order_fingerprint") is True
        ):
            continue
        seen.add(identity)
        output.append({
            "receipt_identity": identity,
            "timestamp": timestamp,
            "price_cents": float(row["price"]),
            "size": float(row["size"]),
            "taker_side": str(row.get("taker_side") or ""),
            "source": str(row.get("source") or ""),
            "size_verified": bool(row.get("size_verified")),
            "synthetic_transition": bool(
                row.get("synthetic_transition")
            ),
        })
    return output


def _order_intervals(
    actions: Sequence[Mapping[str, Any]], horizon: float,
) -> list[dict[str, Any]]:
    intervals: list[dict[str, Any]] = []
    active: dict[str, Any] | None = None
    for action in actions:
        timestamp = float(action["ts"])
        kind = str(action["action"])
        if kind in {"place", "reprice"}:
            if active is not None:
                active["end_ts"] = timestamp
                active["end_reason"] = "implicit_replace"
                intervals.append(active)
            active = {
                "start_ts": timestamp,
                "end_ts": None,
                "end_reason": None,
                "price_cents": int(action["price_cents"]),
                "quantity": float(action.get("quantity") or 0),
                "queue_ahead": float(action.get("queue_ahead") or 0),
                "posture": action.get("posture"),
                "placement_reason": action.get("reason"),
            }
        elif kind == "cancel" and active is not None:
            active["end_ts"] = timestamp
            active["end_reason"] = str(action.get("reason"))
            intervals.append(active)
            active = None
        elif (
            kind == "fill_observed"
            and action.get("complete") is True
            and active is not None
        ):
            active["end_ts"] = timestamp
            active["end_reason"] = "exact_five_fill"
            intervals.append(active)
            active = None
    if active is not None:
        active["end_ts"] = float(horizon)
        active["end_reason"] = "policy_horizon"
        intervals.append(active)
    return intervals


def _proved_five_opportunities(
    intervals: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    cutoff: float,
) -> list[dict[str, Any]]:
    cumulative = 0.0
    seen_receipts: set[str] = set()
    for interval in sorted(
        intervals, key=lambda row: float(row["start_ts"])
    ):
        end = float(interval["end_ts"])
        start = float(interval["start_ts"])
        if min(end, float(cutoff)) <= start:
            continue
        for row in prints:
            timestamp = float(row["timestamp"])
            if timestamp <= start or timestamp >= float(cutoff):
                continue
            end_inclusive = (
                str(interval.get("end_reason"))
                != "policy_horizon"
            )
            if (
                timestamp > end
                or (timestamp == end and not end_inclusive)
            ):
                continue
            if (
                row["taker_side"] != "no"
                or float(row["price_cents"])
                > float(interval["price_cents"])
            ):
                continue
            receipt = str(row["receipt_identity"])
            if receipt in seen_receipts:
                continue
            seen_receipts.add(receipt)
            cumulative += float(row["size"])
            if cumulative >= 5:
                return [{
                    "proved_at_ts": timestamp,
                    "order_price_cents": interval["price_cents"],
                    "initial_queue_ahead": interval["queue_ahead"],
                    "receipt_identity": receipt,
                    "cumulative_qualifying_executed_volume": cumulative,
                    "proof": (
                        "chronological positive-size non-self executed "
                        "prints across the leg's successive active order "
                        "intervals total five at each active limit or "
                        "better before the guarded cutoff"
                    ),
                    "estimated_queue_applied_to_primary": False,
                }]
    return []


def _execution_reach_facts(
    intervals: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    cutoff: float,
) -> dict[str, Any]:
    """Separate authoritative print-volume reach from queue sensitivity."""
    interval_facts = []
    for interval in intervals:
        end = float(interval["end_ts"])
        start = float(interval["start_ts"])
        stop = min(end, float(cutoff))
        if stop <= start:
            continue
        initial_queue = float(interval["queue_ahead"])
        queue = initial_queue
        qualifying_size = 0.0
        queue_sensitive_size = 0.0
        receipt_count = 0
        first_reach_ts = None
        for row in prints:
            timestamp = float(row["timestamp"])
            if timestamp <= start or timestamp >= float(cutoff):
                continue
            end_inclusive = (
                str(interval.get("end_reason"))
                != "policy_horizon"
            )
            if (
                timestamp > end
                or (timestamp == end and not end_inclusive)
            ):
                continue
            if (
                row["taker_side"] != "no"
                or float(row["price_cents"])
                > float(interval["price_cents"])
            ):
                continue
            receipt_count += 1
            if first_reach_ts is None:
                first_reach_ts = timestamp
            size = float(row["size"])
            qualifying_size += size
            if (
                float(row["price_cents"])
                == float(interval["price_cents"])
                and queue > 0
            ):
                debit = min(queue, size)
                queue -= debit
                size -= debit
            queue_sensitive_size += max(0.0, size)
        interval_facts.append({
            "start_ts": interval["start_ts"],
            "end_ts": stop,
            "order_price_cents": interval["price_cents"],
            "initial_queue_ahead": initial_queue,
            "first_price_reach_ts": first_reach_ts,
            "positive_size_receipt_count": receipt_count,
            "primary_qualifying_executed_volume": qualifying_size,
            "primary_exact_five_proved": qualifying_size >= 5,
            "primary_fill_uses_estimated_queue": False,
            "queue_sensitivity_diagnostic_only": {
                "initial_estimated_queue_ahead": initial_queue,
                "estimated_queue_ahead_remaining": queue,
                "volume_after_estimated_queue": queue_sensitive_size,
                "five_contracts_after_estimated_queue": (
                    queue_sensitive_size >= 5
                ),
                "alters_primary_result": False,
            },
        })
    price_reached = any(
        row["positive_size_receipt_count"] > 0
        for row in interval_facts
    )
    total_primary = sum(
        float(row["primary_qualifying_executed_volume"])
        for row in interval_facts
    )
    total_queue_sensitive = sum(
        float(
            row["queue_sensitivity_diagnostic_only"][
                "volume_after_estimated_queue"
            ]
        )
        for row in interval_facts
    )
    maximum_primary = max(
        (
            float(row["primary_qualifying_executed_volume"])
            for row in interval_facts
        ),
        default=0.0,
    )
    maximum_queue_sensitive = max(
        (
            float(
                row["queue_sensitivity_diagnostic_only"][
                    "volume_after_estimated_queue"
                ]
            )
            for row in interval_facts
        ),
        default=0.0,
    )
    primary_class = (
        "at_least_five_qualifying_contracts_exact_five_primary_fill"
        if total_primary >= 5
        else "qualifying_volume_below_five_before_cutoff"
        if price_reached
        else "no_qualifying_executed_volume_at_order_price"
    )
    queue_class = (
        "estimated_queue_not_cleared_sensitivity_only"
        if total_primary >= 5 and total_queue_sensitive < 5
        else "five_after_estimated_queue_sensitivity_only"
        if total_queue_sensitive >= 5
        else "below_five_after_estimated_queue_sensitivity_only"
    )
    return {
        "price_reached": price_reached,
        "primary_print_volume_class": primary_class,
        "five_qualifying_contracts_reached": total_primary >= 5,
        "primary_exact_five_proved": total_primary >= 5,
        "total_primary_qualifying_executed_volume": total_primary,
        "maximum_primary_qualifying_executed_volume": maximum_primary,
        "queue_sensitivity_diagnostic_only": {
            "unknown_queue_never_defaults_to_nonfill": True,
            "primary_result_altered": False,
            "sensitivity_class": queue_class,
            "maximum_volume_after_estimated_queue": (
                maximum_queue_sensitive
            ),
            "total_volume_after_estimated_queue": (
                total_queue_sensitive
            ),
            "any_five_after_estimated_queue": (
                total_queue_sensitive >= 5
            ),
        },
        "maximum_queue_sensitive_volume": maximum_queue_sensitive,
        "intervals": interval_facts,
    }


def _control_leg_map(
    row: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    return {
        str(leg["leg_id"]): leg for leg in row["leg_results"]
    }


def _fill_facts(
    actions: Sequence[Mapping[str, Any]], cutoff: float,
) -> dict[str, Any]:
    fills = [
        row for row in actions
        if row["action"] == "fill_observed"
        and float(row["ts"]) < cutoff
    ]
    quantity = sum(float(row.get("fill_quantity") or 0) for row in fills)
    cost = sum(
        float(row.get("fill_quantity") or 0)
        * float(row.get("order_price_cents") or 0)
        for row in fills
    )
    return {
        "inside_guarded_cutoff_quantity": quantity,
        "exact_five_inside_guarded_cutoff": abs(quantity - 5) < 1e-9,
        "inside_guarded_cutoff_vwap_cents": (
            cost / quantity if quantity > 0 else None
        ),
        "fill_receipts": [
            {
                "timestamp": float(row["ts"]),
                "trade_id": row.get("trade_id"),
                "order_price_cents": row.get("order_price_cents"),
                "print_price_cents": row.get("print_price_cents"),
                "fill_quantity": row.get("fill_quantity"),
                "cumulative_quantity": row.get(
                    "cumulative_quantity"
                ),
            }
            for row in fills
        ],
        "first_fill_ts": (
            min(float(row["ts"]) for row in fills) if fills else None
        ),
    }


def _compact_headroom_receipt(
    row: Mapping[str, Any],
) -> dict[str, Any]:
    fields = (
        "event_id",
        "candidate_id",
        "leg_id",
        "ts",
        "action",
        "reason",
        "trigger_receipt",
        "trigger_ts",
        "first_filled_leg",
        "first_leg_exact5_vwap_cents",
        "R1_cents",
        "R1_ts",
        "R1_source",
        "b1_cents",
        "fee_cents",
        "R2_cents",
        "R2_ts",
        "R2_source",
        "proposed_price_cents",
        "b2_cents",
        "b2_max_cents",
        "prior_order_price_cents",
        "queue_ahead_before",
        "queue_ahead_after",
        "action_taken",
        "queue_retained",
        "queue_surrendered",
    )
    return {field: row.get(field) for field in fields}


def _compact_macro_state(row: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "ts",
        "action",
        "reason",
        "causal_book_ts",
        "prior_band",
        "current_band",
        "prior_posture",
        "current_posture",
        "posture_changed",
        "order_changed",
        "cohort_status",
        "cohort_n",
        "cohort_zone",
    )
    output = {field: row.get(field) for field in fields}
    recognition = row.get("recognition")
    if isinstance(recognition, Mapping):
        output["recognition"] = {
            field: recognition.get(field)
            for field in (
                "observed_at",
                "anchor_cents",
                "current_cents",
                "net_cents",
                "dip_cents",
                "band",
                "used",
                "purity",
                "recall_trigger",
                "causal_book_ts",
            )
        }
    orientation = row.get("orientation")
    if isinstance(orientation, Mapping):
        output["orientation"] = {
            field: orientation.get(field)
            for field in (
                "called_role",
                "status",
                "n",
                "dog_rise_rate",
            )
        }
    return output


def _leg_diagnostic(
    *,
    event: Mapping[str, Any],
    normalized_leg: Mapping[str, Any],
    stream: Mapping[str, Any],
    control_leg: Mapping[str, Any],
    candidate: str,
    source_hashes: Mapping[str, str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    leg_id = str(normalized_leg["leg_id"])
    actions = list(stream["leg_streams"][leg_id])
    boundary = dict(control_leg["boundary"])
    left = float(stream["policy_clock"]["policy_activation_ts"])
    horizon = float(
        stream["policy_clock"]["policy_decision_horizon_ts"]
    )
    cutoff = (
        float(boundary["boundary_timestamp"])
        if boundary.get("boundary_timestamp") is not None
        else left
    )
    prints = _valid_prints(normalized_leg, left, horizon)
    intervals = _order_intervals(actions, horizon)
    opportunities = _proved_five_opportunities(
        intervals, prints, cutoff
    )
    reach_facts = _execution_reach_facts(
        intervals, prints, cutoff
    )
    fills = _fill_facts(actions, cutoff)
    macro = next(
        (row for row in actions if row["action"] == "macro_bind"),
        None,
    )
    reach = [
        row for row in actions
        if row["action"] in {
            "macro_reach_bind", "macro_atlas_bind", "latent_pair_recut"
        }
    ]
    divots = [
        {
            "timestamp": row["ts"],
            "print_price_cents": row.get("print_price_cents"),
            "trailing_median_cents": row.get(
                "trailing_median_cents"
            ),
            "depth_cents": row.get("depth_cents"),
        }
        for row in actions if row["action"] == "micro_divot"
    ]
    exact_reference = next(
        (
            row for row in actions
            if row["action"] == "causal_exact5_reference"
            and row.get("status") == "AVAILABLE"
        ),
        None,
    )
    ex_post_delta = (
        float(fills["inside_guarded_cutoff_vwap_cents"])
        - float(control_leg["window1_close_reference_cents"])
        if (
            fills["inside_guarded_cutoff_vwap_cents"] is not None
            and control_leg.get("window1_close_reference_cents")
            is not None
        )
        else None
    )
    headroom = [
        row for row in actions
        if row["action"] in {
            "headroom_partial_arm",
            "headroom_exact5_arm",
            "headroom_decision",
            "headroom_no_call",
        }
    ]
    item = {
        "event_id": str(event["event_id"]),
        "leg_id": leg_id,
        "ticker": str(normalized_leg["ticker"]),
        "candidate_id": candidate,
        "boundary": {
            "source_class": boundary.get("source_class"),
            "guard_id": boundary.get("guard_id"),
            "guard_seconds": boundary.get("guard_seconds"),
            "direction": boundary.get("direction"),
            "cutoff_ts": boundary.get("boundary_timestamp"),
            "status": boundary.get("status"),
        },
        "macro_opportunity_status": (
            "AVAILABLE"
            if macro is not None else "NO_CALL_UNAVAILABLE"
        ),
        "birth": {
            "anchor_cents": macro.get("anchor_cents") if macro else None,
            "band": macro.get("birth_band") if macro else None,
            "recut_cell_edge_p50": (
                macro.get("recut_depth_cents") if macro else None
            ),
            "advisory_tdeep_ts": (
                macro.get("advisory_tdeep_ts") if macro else None
            ),
        },
        "chronological_macro_states": [
            _compact_macro_state(row)
            for row in actions
            if row["action"] in {
                "orientation_observed",
                "drift_recognition_observed",
                "drift_recognition_recall",
                "cohort_no_call",
                "cohort_steer",
            }
        ],
        "fitted_reach_and_recut": reach,
        "fitted_source_hashes": dict(source_hashes),
        "microdivot_receipts": divots,
        "candidate_relevant_positive_size_prints": prints,
        "order_presence_intervals": intervals,
        "lawful_five_contract_price_opportunity_appeared": bool(
            opportunities
        ),
        "lawful_five_contract_opportunity_proofs": opportunities,
        "price_size_queue_reach": reach_facts,
        "candidate_had_order_present": bool(intervals),
        "absence_nonmovement_or_nonfill_reasons": sorted({
            str(row["reason"])
            for row in actions
            if row["action"] in {
                "feature_censor",
                "feature_no_call",
                "cohort_no_call",
                "headroom_no_call",
                "headroom_decision",
                "terminal",
            }
        }),
        "exact_five_fill_status": fills,
        "causal_budget_delta": (
            exact_reference.get("causal_delta_cents")
            if exact_reference else None
        ),
        "headroom_decision_receipts": {
            "storage": (
                "ROUND4_HEADROOM_DECISION_RECEIPTS.jsonl.gz "
                "filtered by event/candidate/leg"
            ),
            "count": len(headroom),
            "sha256": hashlib.sha256(
                compact([
                    _compact_headroom_receipt(row) for row in headroom
                ]).encode("utf-8")
            ).hexdigest(),
        },
        "oracle_diagnostic_only": {
            "window1_close_reference_cents": control_leg.get(
                "window1_close_reference_cents"
            ),
            "ex_post_window1_close_delta_cents": ex_post_delta,
            "unreachable_from_policy": True,
        },
        "scored": False,
        "metrics": None,
    }
    calibration = []
    exact_ex_post_delta = (
        float(exact_reference["vwap_cents"])
        - float(control_leg["window1_close_reference_cents"])
        if (
            exact_reference is not None
            and control_leg.get("window1_close_reference_cents")
            is not None
        )
        else None
    )
    if exact_reference is not None and exact_ex_post_delta is not None:
        calibration.append({
            "event_id": str(event["event_id"]),
            "candidate_id": candidate,
            "leg_id": leg_id,
            "tournament_class": str(event["category"]),
            "start_source_class": boundary.get("source_class"),
            "macro_band": (
                macro.get("birth_band") if macro else None
            ),
            "entry_vwap_cents": exact_reference["vwap_cents"],
            "causal_reference_cents": exact_reference[
                "reference_cents"
            ],
            "causal_b_i_cents": exact_reference[
                "causal_delta_cents"
            ],
            "eventual_window1_close_reference_cents": (
                control_leg["window1_close_reference_cents"]
            ),
            "ex_post_d_i_cents": exact_ex_post_delta,
        })
    return item, calibration


def _failure_class(
    legs: Sequence[Mapping[str, Any]],
    stream: Mapping[str, Any],
) -> str:
    boundaries = [leg["boundary"] for leg in legs]
    if any(row["status"] == "contradictory" for row in boundaries):
        return "contradictory boundary"
    if stream["event_terminal"] == "zero_length_window1_opportunity":
        return "zero-length Window 1"
    if any(
        any(
            action["action"] == "feature_censor"
            for action in stream["leg_streams"][leg["leg_id"]]
        )
        for leg in legs
    ):
        return "evidence censored"
    exact = [
        bool(leg["exact_five_fill_status"][
            "exact_five_inside_guarded_cutoff"
        ])
        for leg in legs
    ]
    deltas = [
        leg["oracle_diagnostic_only"][
            "ex_post_window1_close_delta_cents"
        ]
        for leg in legs
    ]
    if all(exact):
        if all(value is not None for value in deltas) and sum(deltas) < 0:
            return "completed PC"
        return "completed non-PC"
    all_actions = list(stream["order_stream"])
    if not any(
        action["action"] == "macro_bind" for action in all_actions
    ):
        return "no macro opportunity"
    if not all(leg["macro_opportunity_status"] == "AVAILABLE" for leg in legs):
        return "macro opportunity not recognized"
    if not all(leg["candidate_had_order_present"] for leg in legs):
        return "recognized but no lawful order"
    post_cutoff_complete = False
    for leg in legs:
        cutoff = leg["boundary"]["cutoff_ts"]
        if cutoff is None:
            continue
        cutoff = float(cutoff)
        post_cutoff_complete |= any(
            action["action"] == "fill_observed"
            and action.get("complete") is True
            and float(action["ts"]) >= cutoff
            for action in stream["leg_streams"][leg["leg_id"]]
        )
    if post_cutoff_complete:
        return "lawful opportunity only after cutoff"
    headroom_actions = [
        action for action in all_actions
        if action["action"] == "headroom_decision"
        and action.get("action_taken") is True
    ]
    negative_single = any(
        exact[index] and deltas[index] is not None and deltas[index] < 0
        for index in range(2)
    )
    if negative_single and not headroom_actions:
        return "negative single captured but headroom unused"
    if headroom_actions:
        return "headroom used but sibling not reached"
    unfilled = [
        leg for index, leg in enumerate(legs) if not exact[index]
    ]
    if any(
        leg["price_size_queue_reach"]["price_reached"]
        and not leg["price_size_queue_reach"][
            "five_qualifying_contracts_reached"
        ]
        for leg in unfilled
    ):
        return "price reached but insufficient size"
    if any(
        leg["price_size_queue_reach"][
            "five_qualifying_contracts_reached"
        ]
        for leg in unfilled
    ):
        raise DiagnosticError(
            "primary five-volume proof did not produce an exact-five fill"
        )
    return "order present but price not reached"


def _calibration_summary(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    def summarize(group: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        errors = [
            abs(
                float(row["causal_b_i_cents"])
                - float(row["ex_post_d_i_cents"])
            )
            for row in group
        ]
        confusion = Counter(
            f"{_sign(float(row['causal_b_i_cents']))}"
            f"->{_sign(float(row['ex_post_d_i_cents']))}"
            for row in group
        )
        causal_negative = sum(
            float(row["causal_b_i_cents"]) < 0 for row in group
        )
        causal_nonnegative = len(group) - causal_negative
        false_positive = sum(
            float(row["causal_b_i_cents"]) < 0
            and float(row["ex_post_d_i_cents"]) >= 0
            for row in group
        )
        false_negative = sum(
            float(row["causal_b_i_cents"]) >= 0
            and float(row["ex_post_d_i_cents"]) < 0
            for row in group
        )
        return {
            "n": len(group),
            "sign_confusion_matrix": dict(sorted(confusion.items())),
            "MAE_cents": (
                sum(errors) / len(errors) if errors else None
            ),
            "absolute_error_cents": {
                "p25": _quantile(errors, 0.25),
                "p50": _quantile(errors, 0.50),
                "p75": _quantile(errors, 0.75),
                "p90": _quantile(errors, 0.90),
            },
            "false_positive_proxy_count": false_positive,
            "false_positive_proxy_rate": (
                false_positive / causal_negative
                if causal_negative else None
            ),
            "false_negative_proxy_count": false_negative,
            "false_negative_proxy_rate": (
                false_negative / causal_nonnegative
                if causal_nonnegative else None
            ),
        }

    dimensions = {
        "candidate": "candidate_id",
        "tournament_class": "tournament_class",
        "start_source_class": "start_source_class",
        "macro_band": "macro_band",
    }
    breakdowns = {}
    for name, field in dimensions.items():
        groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for row in rows:
            groups[str(row.get(field))].append(row)
        breakdowns[name] = {
            key: summarize(value) for key, value in sorted(groups.items())
        }
    return {
        "schema_version": "window1-round4-causal-reference-calibration-v1",
        "policy_threshold_tuned_from_calibration": False,
        "policy_imports_this_artifact": False,
        "comparison": (
            "causal b_i at exact-five versus eventual guarded "
            "Window-1-close d_i"
        ),
        "overall": summarize(rows),
        "breakdowns": breakdowns,
        "sample_rows": list(rows),
        "scored_candidate_metrics": None,
    }


def _round3_oracle_census(
    repo: Path, results_dir: Path,
) -> dict[str, Any]:
    ledger_paths = sorted(results_dir.glob("*_EVENT_LEDGER.jsonl"))
    if len(ledger_paths) != 8:
        raise DiagnosticError("Round-3 eight result ledgers not found")
    ledgers = {
        read_jsonl(path)[0]["candidate_id"]: {
            row["event_id"]: row for row in read_jsonl(path)
        }
        for path in ledger_paths
    }
    accumulators = {
        candidate: {
            "naked_single_count": 0,
            "filled_leg_ex_post_d1_negative_count": 0,
            "unused_allowances": [],
            "later_logged_strict_price_reach_count": 0,
            "negative_d1_sibling_fill_only_after_cutoff_count": 0,
        }
        for candidate in ledgers
    }
    with gzip.open(
        repo / R3_STREAMS, "rt", encoding="utf-8"
    ) as handle:
        for line in handle:
            wrapper = json.loads(line)
            candidate = str(wrapper["candidate_id"])
            event_id = str(wrapper["event_id"])
            stream = wrapper["stream"]
            result = ledgers[candidate][event_id]
            target = accumulators[candidate]
            if result["classification"] != "naked_single_leg":
                continue
            target["naked_single_count"] += 1
            filled = [
                leg for leg in result["leg_results"]
                if leg.get("individual_delta_cents") is not None
            ]
            if (
                len(filled) != 1
                or float(filled[0]["individual_delta_cents"]) >= 0
            ):
                continue
            target["filled_leg_ex_post_d1_negative_count"] += 1
            sibling = next(
                leg for leg in result["leg_results"]
                if leg is not filled[0]
            )
            sibling_actions = stream["leg_streams"][
                sibling["leg_id"]
            ]
            posts = [
                float(row["price_cents"])
                for row in sibling_actions
                if row["action"] in {"place", "reprice"}
                and row.get("price_cents") is not None
            ]
            if not posts:
                raise DiagnosticError(
                    "negative naked single has no sibling presence"
                )
            strict_max_price = (
                float(sibling["window1_close_reference_cents"])
                - float(filled[0]["individual_delta_cents"])
                - 1
            )
            unused = strict_max_price - max(posts)
            target["unused_allowances"].append(unused)
            cutoff = float(sibling["boundary"]["boundary_timestamp"])
            later_fills = [
                row for row in sibling_actions
                if row["action"] == "fill_observed"
                and float(row["ts"]) >= cutoff
            ]
            if later_fills:
                target[
                    "negative_d1_sibling_fill_only_after_cutoff_count"
                ] += 1
            # "Logged strict price reach" is deliberately weaker than a
            # completion claim.  It is the source-supplied comparator:
            # after the filled leg completed, but before the sibling cutoff,
            # a receipt-backed microdivot print lay strictly above every
            # sibling price actually posted and no higher than the unused
            # strict ex-post allowance.  It does not assert cumulative
            # five-contract qualifying executed volume.
            first_leg_exact5_ts = max(
                float(row["timestamp"])
                for row in filled[0]["inside_window_fill_receipts"]
            )
            later_strict = [
                row for row in sibling_actions
                if row["action"] == "micro_divot"
                and first_leg_exact5_ts < float(row["ts"]) < cutoff
                and max(posts)
                < float(row["print_price_cents"])
                <= strict_max_price
            ]
            if later_strict:
                target["later_logged_strict_price_reach_count"] += 1
    output = []
    for candidate in sorted(accumulators):
        item = accumulators[candidate]
        allowances = list(map(float, item.pop("unused_allowances")))
        output.append({
            "candidate_id": candidate,
            **item,
            "unused_ex_post_pair_allowance": {
                "n": len(allowances),
                "at_least_1_cent": sum(x >= 1 for x in allowances),
                "at_least_2_cents": sum(x >= 2 for x in allowances),
                "at_least_3_cents": sum(x >= 3 for x in allowances),
                "at_least_5_cents": sum(x >= 5 for x in allowances),
                "median_cents": (
                    statistics.median(allowances)
                    if allowances else None
                ),
            },
        })
    selected = next(
        row for row in output
        if row["candidate_id"]
        == "r3_pair_presence__park_join__reaim"
    )
    expected = {
        "naked_single_count": 278,
        "filled_leg_ex_post_d1_negative_count": 92,
        "allowance_at_least_1": 75,
        "allowance_at_least_2": 68,
        "allowance_at_least_3": 59,
        "allowance_at_least_5": 40,
        "allowance_median": 4,
        "later_logged_strict_price_reach": 12,
        "post_cutoff_sibling_fills": 53,
    }
    actual = {
        "naked_single_count": selected["naked_single_count"],
        "filled_leg_ex_post_d1_negative_count": selected[
            "filled_leg_ex_post_d1_negative_count"
        ],
        "allowance_at_least_1": selected[
            "unused_ex_post_pair_allowance"
        ]["at_least_1_cent"],
        "allowance_at_least_2": selected[
            "unused_ex_post_pair_allowance"
        ]["at_least_2_cents"],
        "allowance_at_least_3": selected[
            "unused_ex_post_pair_allowance"
        ]["at_least_3_cents"],
        "allowance_at_least_5": selected[
            "unused_ex_post_pair_allowance"
        ]["at_least_5_cents"],
        "allowance_median": selected[
            "unused_ex_post_pair_allowance"
        ]["median_cents"],
        "later_logged_strict_price_reach": selected[
            "later_logged_strict_price_reach_count"
        ],
        "post_cutoff_sibling_fills": selected[
            "negative_d1_sibling_fill_only_after_cutoff_count"
        ],
    }
    if actual != expected:
        raise DiagnosticError(
            f"supplied Round-3 headroom census not reproduced: {actual}"
        )
    return {
        "schema_version": "window1-round3-oracle-false-negative-census-v1",
        "source_round3_result": (
            "754415bb81a328d671cd327f216d1753802442b1"
        ),
        "source_round3_audit": (
            "25735d9c9d9775a122da2a067962f45312aa62dc"
        ),
        "logged_price_reach_is_completion_claim": False,
        "logged_price_reach_definition": (
            "receipt-backed sibling microdivot after filled-leg exact five "
            "and before guarded cutoff, strictly above every actually "
            "posted sibling price and <= the strict ex-post allowance"
        ),
        "five_contract_primary_print_volume_required_for_completion": True,
        "estimated_queue_required_for_primary_completion": False,
        "queue_sensitivity_alters_primary_completion": False,
        "post_cutoff_fills_excluded_from_PC": True,
        "supplied_selected_candidate_counts_reproduced": True,
        "supplied_count_comparison": {
            "expected": expected,
            "actual": actual,
        },
        "candidates": output,
    }


def _pair_opportunity_summary(
    legs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if len(legs) != 2:
        raise DiagnosticError("pair opportunity requires exactly two legs")
    proof_sets = [
        list(leg["lawful_five_contract_opportunity_proofs"])
        for leg in legs
    ]
    references = [
        leg["oracle_diagnostic_only"][
            "window1_close_reference_cents"
        ]
        for leg in legs
    ]
    witnesses = []
    if all(proof_sets) and all(value is not None for value in references):
        for first in proof_sets[0]:
            for second in proof_sets[1]:
                combined_delta = (
                    float(first["order_price_cents"])
                    - float(references[0])
                    + float(second["order_price_cents"])
                    - float(references[1])
                )
                witnesses.append({
                    "leg_1": {
                        "leg_id": legs[0]["leg_id"],
                        "proved_at_ts": first["proved_at_ts"],
                        "order_price_cents": first[
                            "order_price_cents"
                        ],
                        "receipt_identity": first[
                            "receipt_identity"
                        ],
                    },
                    "leg_2": {
                        "leg_id": legs[1]["leg_id"],
                        "proved_at_ts": second["proved_at_ts"],
                        "order_price_cents": second[
                            "order_price_cents"
                        ],
                        "receipt_identity": second[
                            "receipt_identity"
                        ],
                    },
                    "combined_ex_post_delta_cents": combined_delta,
                    "oracle_diagnostic_only": True,
                })
    best = (
        min(
            witnesses,
            key=lambda row: (
                row["combined_ex_post_delta_cents"],
                row["leg_1"]["proved_at_ts"],
                row["leg_2"]["proved_at_ts"],
            ),
        )
        if witnesses else None
    )
    both = all(bool(rows) for rows in proof_sets)
    return {
        "two_separate_lawful_five_contract_times": both,
        "separately_timed_prices_combined_ex_post_"
        "delta_strictly_negative": (
            best is not None
            and float(best["combined_ex_post_delta_cents"]) < 0
        ),
        "best_separately_timed_pair_witness": best,
        "candidate_recognized_both": both,
        "definition": (
            "each leg accumulates at least five qualifying executed "
            "contracts at its posted limit or better while its candidate "
            "order is present before its guarded cutoff; estimated queue "
            "does not alter the primary proof, and the ex-post close is "
            "used only to label the diagnostic pair"
        ),
        "unreachable_from_policy": True,
    }


def build(
    *,
    repo: Path,
    events_path: Path,
    cache_root: Path,
    streams_path: Path,
    round3_results_dir: Path,
    opportunity_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    events = read_jsonl(events_path)
    if len(events) != binding.D_REQUIRED:
        raise DiagnosticError("opportunity denominator changed")
    event_map = {str(row["event_id"]): row for row in events}
    features = [
        row for row in read_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in features
    }
    control_path = (
        round3_results_dir
        / "02_r3_pair_presence__park_join__reaim_EVENT_LEDGER.jsonl"
    )
    control = {
        str(row["event_id"]): row for row in read_jsonl(control_path)
    }
    if set(control) != set(event_map):
        raise DiagnosticError("Round-3 control event identity mismatch")
    candidate_ids = r4.load_candidate_spec(repo)["candidate_ids"]
    source_hashes = {
        "drift": sha256_path(repo / r4.DRIFT_PATH),
        "atlas": sha256_path(repo / r4.ATLAS_PATH),
        "recut": sha256_path(
            repo / ".claude/seqfloor_20260708/recut_cells.json"
        ),
    }
    calibration_rows: list[dict[str, Any]] = []
    event_count = 0
    with gzip.open(
        streams_path, "rt", encoding="utf-8"
    ) as streams, ShardedGzipJsonlWriter(opportunity_path) as output:
                iterator = iter(streams)
                while True:
                    try:
                        wrappers = [
                            json.loads(next(iterator))
                            for _ in candidate_ids
                        ]
                    except StopIteration:
                        break
                    event_ids = {
                        str(row["event_id"]) for row in wrappers
                    }
                    if len(event_ids) != 1:
                        raise DiagnosticError(
                            "candidate stream order is not event-major"
                        )
                    event_id = event_ids.pop()
                    if [row["candidate_id"] for row in wrappers] != list(
                        candidate_ids
                    ):
                        raise DiagnosticError(
                            "candidate stream order changed"
                        )
                    event = event_map[event_id]
                    normalized = r2cap.normalize_event(
                        event,
                        r2cap.load_cache(
                            cache_root / f"{event_id}.json.gz"
                        ),
                        feature_map,
                        corridor_seconds=0,
                    )
                    r3builder.bind_round3_book_receipts(normalized)
                    normalized_legs = {
                        str(leg["leg_id"]): leg
                        for leg in normalized["legs"]
                    }
                    control_legs = _control_leg_map(control[event_id])
                    candidate_entries = {}
                    shared_prints_by_leg: dict[str, list[dict[str, Any]]] = {}
                    for wrapper in wrappers:
                        candidate = str(wrapper["candidate_id"])
                        stream = wrapper["stream"]
                        if (
                            stream["metrics"] is not None
                            or stream["scored"] is not False
                        ):
                            raise DiagnosticError(
                                "Round-4 stream is not score-free"
                            )
                        legs = []
                        for leg_id in sorted(normalized_legs):
                            item, calibration = _leg_diagnostic(
                                event=event,
                                normalized_leg=normalized_legs[leg_id],
                                stream=stream,
                                control_leg=control_legs[leg_id],
                                candidate=candidate,
                                source_hashes=source_hashes,
                            )
                            legs.append(item)
                            calibration_rows.extend(calibration)
                            leg_id = str(item["leg_id"])
                            prints = item.pop(
                                "candidate_relevant_positive_size_prints"
                            )
                            prior_prints = shared_prints_by_leg.setdefault(
                                leg_id, prints
                            )
                            if prior_prints != prints:
                                raise DiagnosticError(
                                    "candidate print evidence diverged"
                                )
                            item[
                                "candidate_relevant_positive_size_prints"
                            ] = {
                                "storage": (
                                    "event.shared_leg_public_print_evidence."
                                    + leg_id
                                ),
                                "count": len(prints),
                                "sha256": hashlib.sha256(
                                    compact(prints).encode("utf-8")
                                ).hexdigest(),
                            }
                        headroom_decisions = [
                            row for row in stream["order_stream"]
                            if row["action"] == "headroom_decision"
                        ]
                        compact_headroom_decisions = [
                            _compact_headroom_receipt(row)
                            for row in headroom_decisions
                        ]
                        headroom_sibling_leg_ids = sorted({
                            str(row["leg_id"])
                            for row in headroom_decisions
                        })
                        exact = [
                            leg["exact_five_fill_status"][
                                "exact_five_inside_guarded_cutoff"
                            ]
                            for leg in legs
                        ]
                        deltas = [
                            leg["oracle_diagnostic_only"][
                                "ex_post_window1_close_delta_cents"
                            ]
                            for leg in legs
                        ]
                        first_fills = [
                            (
                                leg["leg_id"],
                                leg["exact_five_fill_status"][
                                    "first_fill_ts"
                                ],
                            )
                            for leg in legs
                            if leg["exact_five_fill_status"][
                                "first_fill_ts"
                            ] is not None
                        ]
                        pair_opportunity = _pair_opportunity_summary(
                            legs
                        )
                        candidate_entry = {
                            "candidate_id": candidate,
                            "legs": legs,
                            "pair_diagnostic": {
                                "two_separate_lawful_five_contract_times": (
                                    pair_opportunity[
                                        "two_separate_lawful_"
                                        "five_contract_times"
                                    ]
                                ),
                                "separately_timed_prices_combined_ex_post_"
                                "delta_strictly_negative": (
                                    pair_opportunity[
                                        "separately_timed_prices_combined_"
                                        "ex_post_delta_strictly_negative"
                                    ]
                                ),
                                "best_separately_timed_pair_witness": (
                                    pair_opportunity[
                                        "best_separately_timed_pair_witness"
                                    ]
                                ),
                                "candidate_recognized_both": (
                                    pair_opportunity[
                                        "candidate_recognized_both"
                                    ]
                                ),
                                "opportunity_definition": (
                                    pair_opportunity["definition"]
                                ),
                                "opportunity_oracle_unreachable_from_policy": (
                                    pair_opportunity[
                                        "unreachable_from_policy"
                                    ]
                                ),
                                "both_orders_present": all(
                                    leg["candidate_had_order_present"]
                                    for leg in legs
                                ),
                                "first_fill_identity_and_time": (
                                    min(
                                        first_fills,
                                        key=lambda value: value[1],
                                    )
                                    if first_fills else None
                                ),
                                "b1_fee_and_sibling_b2_receipts": (
                                    compact_headroom_decisions
                                ),
                                "maximum_lawful_sibling_allowance_cents": (
                                    max(
                                        (
                                            float(row["b2_max_cents"])
                                            for row in headroom_decisions
                                            if row.get("b2_max_cents")
                                            is not None
                                        ),
                                        default=None,
                                    )
                                ),
                                "maximum_price_actually_posted_cents": max(
                                    (
                                        float(row["price_cents"])
                                        for row in stream["order_stream"]
                                        if row["action"]
                                        in {"place", "reprice"}
                                        and str(row["leg_id"])
                                        in headroom_sibling_leg_ids
                                        and row.get("price_cents")
                                        is not None
                                    ),
                                    default=None,
                                ),
                                "headroom_sibling_leg_ids": (
                                    headroom_sibling_leg_ids
                                ),
                                "unused_headroom_cents": (
                                    max(
                                        (
                                            float(row["b2_max_cents"])
                                            - float(row["b2_cents"])
                                            for row in headroom_decisions
                                            if row.get("b2_max_cents")
                                            is not None
                                            and row.get("b2_cents")
                                            is not None
                                        ),
                                        default=None,
                                    )
                                ),
                                "queue_lost_through_changes": [
                                    {
                                        "timestamp": row["ts"],
                                        "leg_id": row["leg_id"],
                                        "queue_ahead_before": row.get(
                                            "queue_ahead_before"
                                        ),
                                        "queue_ahead_after": row.get(
                                            "queue_ahead_after"
                                        ),
                                    }
                                    for row in headroom_decisions
                                    if row.get("queue_surrendered")
                                    is True
                                ],
                                "final_C": None,
                                "final_PC": None,
                                "final_S": None,
                                "final_IC": None,
                                "failure_class": _failure_class(
                                    legs, stream
                                ),
                                "scored": False,
                                "metrics": None,
                            },
                        }
                        candidate_entries[candidate] = candidate_entry
                    output.write(compact({
                        "schema_version": (
                            "window1-round4-opportunity-ledger-v1"
                        ),
                        "event_id": event_id,
                        "event_date": str(event["event_date"]),
                        "tournament_class": str(event["category"]),
                        "shared_leg_public_print_evidence": (
                            shared_prints_by_leg
                        ),
                        "candidate_entries": candidate_entries,
                        "diagnostic_only": True,
                        "policy_importable": False,
                        "benchmark_metrics": None,
                        "scored": False,
                    }) + "\n")
                    event_count += 1
    if event_count != binding.D_REQUIRED:
        raise DiagnosticError(
            f"opportunity event conservation failed: {event_count}"
        )
    calibration = _calibration_summary(calibration_rows)
    census = _round3_oracle_census(repo, round3_results_dir)
    shard_receipts = [
        {
            "path": str(path.relative_to(repo)).replace("\\", "/"),
            "row_count": 402,
            "bytes": path.stat().st_size,
            "sha256": sha256_path(path),
        }
        for path in output.paths
    ]
    if len(shard_receipts) != 2:
        raise DiagnosticError("opportunity ledger must have two shards")
    shard_manifest = {
        "schema_version": "window1-round4-opportunity-ledger-shards-v1",
        "D": 804,
        "ordered_shards": shard_receipts,
        "aggregate_sha256": hashlib.sha256(
            compact(shard_receipts).encode("utf-8")
        ).hexdigest(),
    }
    write_json(
        opportunity_path.with_name(
            "WINDOW1_OPPORTUNITY_LEDGER_MANIFEST.json"
        ),
        shard_manifest,
    )
    receipt = {
        "schema_version": VERSION,
        "D": binding.D_REQUIRED,
        "event_rows": event_count,
        "candidate_ids": list(candidate_ids),
        "candidate_event_diagnostic_count": 2 * event_count,
        "opportunity_ledger_shards": shard_receipts,
        "opportunity_ledger_aggregate_sha256": (
            shard_manifest["aggregate_sha256"]
        ),
        "calibration_sample_count": len(calibration_rows),
        "policy_module_imports_diagnostics": False,
        "scorer_invoked": False,
        "candidate_scoring_performed": False,
        "C_PC_S_IC_populated": False,
        "all_stream_metrics_null": True,
        "holdout_opened": False,
        "holdout_queried": False,
        "threshold_tuned_from_diagnostics": False,
    }
    return receipt, calibration, census


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build score-separated Round-4 diagnostics."
    )
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--streams", type=Path, required=True)
    parser.add_argument("--round3-results-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (
        args.output_dir
        if args.output_dir.is_absolute()
        else repo / args.output_dir
    )
    opportunity = output / "WINDOW1_OPPORTUNITY_LEDGER.jsonl.gz"
    receipt, calibration, census = build(
        repo=repo,
        events_path=args.events.resolve(),
        cache_root=args.market_cache.resolve(),
        streams_path=args.streams.resolve(),
        round3_results_dir=args.round3_results_dir.resolve(),
        opportunity_path=opportunity,
    )
    write_json(output / "ROUND4_DIAGNOSTIC_RECEIPT.json", receipt)
    write_json(
        output / "CAUSAL_REFERENCE_CALIBRATION.json", calibration
    )
    write_json(
        output / "ORACLE_FALSE_NEGATIVE_CENSUS.json", census
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
