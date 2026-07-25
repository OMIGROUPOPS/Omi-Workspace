#!/usr/bin/env python3
"""Score-free Round-4 Window-1 causal-headroom instrument.

This policy module extends the audited Round-3 independent pair-presence
mechanics.  It deliberately has no scorer, evaluation-start, Window-1-close,
network, exchange, account, live, production, exit, settlement, DCA, Window-2,
or holdout interface.  Diagnostic/oracle code is kept in a separate module
which this file never imports.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

import window1_round2_instrument as r2
import window1_round3_instrument as r3


VERSION = "window1-round4-causal-headroom-instrument-v1"
CANDIDATE_SPEC_PATH = (
    "arb-executor/docs/research/window1/WINDOW1_ROUND4_CANDIDATES_V1.json"
)
ATLAS_PATH = ".claude/trendpath/ATLAS_V1.json"
DRIFT_PATH = ".claude/entrysurface_20260717/drift_surfaces_v1.json"
InstrumentError = r2.InstrumentError
FORBIDDEN_ORACLE_FIELDS = {
    "window1_close_reference_cents",
    "window1_close",
    "evaluation_reference",
    "evaluation_real_start_ts",
    "strict_positive_cutoff_ts",
}


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    spec = r2.read_json(repo / CANDIDATE_SPEC_PATH)
    if spec.get("instrument_version") != VERSION:
        raise InstrumentError("Round-4 candidate spec version mismatch")
    candidates = list(map(str, spec.get("candidate_ids") or []))
    if len(candidates) != 2 or len(set(candidates)) != 2:
        raise InstrumentError("Round-4 must freeze exactly two candidates")
    if spec.get("free_numeric_parameters") != []:
        raise InstrumentError("Round-4 cannot expose free parameters")
    return spec


def candidate_policy(
    spec: Mapping[str, Any],
    candidate_id: str,
    *,
    ablations: Iterable[str] = (),
) -> dict[str, Any]:
    if list(ablations):
        raise InstrumentError("Round-4 has no post-freeze ablation surface")
    allowed = list(map(str, spec.get("candidate_ids") or []))
    if candidate_id not in allowed:
        raise InstrumentError(f"candidate is not frozen: {candidate_id}")
    if not candidate_id.endswith("__causal_headroom_ladder"):
        raise InstrumentError(f"malformed Round-4 candidate: {candidate_id}")
    profile = (
        "r4_pair_presence"
        if candidate_id.startswith("r4_pair_presence__")
        else "r4_full_drift_stack"
        if candidate_id.startswith("r4_full_drift_stack__")
        else ""
    )
    families = spec.get("profiles", {}).get(profile)
    if not isinstance(families, list):
        raise InstrumentError(f"candidate profile missing: {candidate_id}")
    return {
        "candidate_id": candidate_id,
        "profile": profile,
        "posture_by_role": dict(spec["posture_by_role"]),
        "sibling_response": "causal_headroom_ladder",
        "enabled_families": sorted(map(str, families)),
        "ablations": [],
        "parameters": dict(spec["common_parameters"]),
    }


def load_atlas(repo: Path) -> dict[str, Any]:
    value = r2.read_json(repo / ATLAS_PATH)
    if not isinstance(value.get("pages"), dict):
        raise InstrumentError("bound atlas has no pages")
    return value


def _price_cell(price: float) -> str:
    if price <= 25:
        return "le25"
    if price <= 50:
        return "26_50"
    if price <= 75:
        return "51_75"
    return "ge75"


def _atlas_role(role: str) -> str:
    return "leader" if role == "favorite" else "underdog"


def headroom_b2_max(b1_cents: float, fee_cents: float = 0) -> int:
    """Largest integer-cent sibling delta satisfying strict pair negativity."""
    return math.floor(-float(b1_cents) - float(fee_cents) - 1.0)


def strict_pair_budget(
    b1_cents: float, b2_cents: float, fee_cents: float = 0,
) -> bool:
    return (
        float(b1_cents) + float(b2_cents) + float(fee_cents)
        < 0
    )


def _forbidden_oracle_paths(
    value: Any, prefix: str = "$",
) -> list[str]:
    paths: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}"
            if key_text in FORBIDDEN_ORACLE_FIELDS:
                paths.append(path)
            paths.extend(_forbidden_oracle_paths(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            paths.extend(
                _forbidden_oracle_paths(item, f"{prefix}[{index}]")
            )
    return paths


class Round4Instrument(r3.Round3Instrument):
    """Round-3 causal substrate with a strict pair-delta headroom actuator."""

    def __init__(
        self,
        surfaces: r2.SurfaceBundle,
        policy: Mapping[str, Any],
        *,
        atlas: Mapping[str, Any] | None = None,
        source_receipts: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(surfaces, policy)
        self.atlas = dict(atlas or {})
        self.source_receipts = dict(source_receipts or {})

    def _validate_event(self, event: Mapping[str, Any]) -> None:
        super()._validate_event(event)
        leaked = sorted(_forbidden_oracle_paths(event))
        if leaked:
            raise InstrumentError(
                "evaluation truth is inaccessible to policy code: "
                + ",".join(leaked)
            )

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        state = super()._new_state(event, leg)
        state.update({
            "partial_sibling_armed": False,
            "partial_sibling_armed_ts": None,
            "headroom_active": False,
            "headroom_armed_ts": None,
            "headroom_first_leg_id": None,
            "headroom_first_leg_vwap_cents": None,
            "headroom_R1_cents": None,
            "headroom_R1_ts": None,
            "headroom_R1_source": None,
            "headroom_b1_cents": None,
            "headroom_b2_max_cents": None,
            "headroom_fee_cents": float(
                self.parameters["headroom_fee_cents"]
            ),
            "headroom_no_call_reason": None,
            "headroom_trigger_count": 0,
            "headroom_action_count": 0,
            "headroom_queue_surrendered": 0.0,
            "exact5_causal_reference": None,
            "drift_reach_depth_cents": None,
            "drift_reach_status": "NOT_EVALUATED",
            "atlas_depth_cents": None,
            "atlas_tdeep_minutes": None,
            "atlas_status": "NOT_EVALUATED",
            "atlas_page": None,
            "macro_posture": None,
            "last_recognition_recall_book_ts": None,
        })
        return state

    def _pair_cost_passes(
        self, state: Mapping[str, Any], price: int,
    ) -> tuple[bool, float | None]:
        """S/combined entry cost is diagnostic and never a policy gate."""
        sibling = next(
            (row for row in self.states if row is not state), None
        )
        combined = None
        if sibling is not None and sibling.get("active_order") is not None:
            combined = float(price) + float(
                sibling["active_order"]["price"]
            )
        return True, combined

    def _initialize_birth(
        self, state: MutableMapping[str, Any], timestamp: float,
    ) -> None:
        super()._initialize_birth(state, timestamp)
        if state.get("birth_anchor") is None:
            return
        if (
            state.get("feature_censored")
            and state.get("missing_features") == ["dynamic_recut_cell"]
        ):
            # A missing optional macro recut cell cannot suppress the
            # underlying independent maker leg.  Remove the inherited
            # censor receipt and replace it with a named NO_CALL.
            state["actions"] = [
                row for row in state["actions"]
                if not (
                    row["action"] == "feature_censor"
                    and row["reason"]
                    == "dynamic_recut_cell_unavailable"
                )
            ]
            state["feature_censored"] = False
            state["missing_features"] = []
            state["recut_depth"] = (
                float(state["divot_depth"])
                if state.get("divot_depth") is not None else 0.0
            )
            state["recut_timing_minutes"] = None
            state["eligible_ts"] = max(self.left, float(timestamp))
            state["advisory_tdeep_ts"] = None
            r2._action(
                state,
                timestamp,
                "feature_no_call",
                "dynamic_recut_cell_unavailable_pair_presence_continues",
                family_id="dynamic_band_cell_recut",
                response_status="NO_CALL_UNAVAILABLE",
                fallback_depth_authority=(
                    "source_proved_divot_depth"
                    if state.get("divot_depth") is not None
                    else "neutral_zero_depth_no_macro_steering"
                ),
                underlying_policy_continues=True,
            )

            minimum_n = int(self.parameters["cohort_minimum_n"])
            anchor = float(state["birth_anchor"])
            cohort_zone = int(max(0, min(3, anchor // 25)))
            cohort, cohort_n = r2.cohort_depth(
                self.surfaces,
                str(self.event["category"]),
                anchor,
                minimum_n,
            )
            state["cohort_n"] = cohort_n
            state["cohort_zone"] = cohort_zone
            if "cohort_steering" in self.families:
                if cohort is None:
                    state["cohort_status"] = "NO_CALL_UNAVAILABLE"
                    r2._action(
                        state,
                        timestamp,
                        "cohort_no_call",
                        "cohort_cell_below_frozen_min_n",
                        cohort_status="NO_CALL_UNAVAILABLE",
                        cohort_n=cohort_n,
                        cohort_minimum_n=minimum_n,
                        cohort_zone=cohort_zone,
                        category=str(self.event["category"]),
                        underlying_policy_continues=True,
                    )
                elif abs(
                    cohort - float(state["recut_depth"])
                ) >= float(
                    self.parameters[
                        "cohort_minimum_reaim_delta_cents"
                    ]
                ):
                    state["cohort_status"] = "CALL"
                    state["cohort_depth"] = cohort
                    r2._action(
                        state,
                        timestamp,
                        "cohort_steer",
                        "frozen_cohort_n30_delta_ge_2",
                        cohort_status="CALL",
                        cohort_n=cohort_n,
                        cohort_zone=cohort_zone,
                        depth_cents=cohort,
                    )
                else:
                    state[
                        "cohort_status"
                    ] = "NO_CALL_BELOW_REAIM_DELTA"
                    r2._action(
                        state,
                        timestamp,
                        "cohort_no_call",
                        "cohort_supported_but_below_reaim_delta",
                        cohort_status="NO_CALL_BELOW_REAIM_DELTA",
                        cohort_n=cohort_n,
                        cohort_minimum_n=minimum_n,
                        cohort_zone=cohort_zone,
                        category=str(self.event["category"]),
                        underlying_policy_continues=True,
                    )
            r2._action(
                state,
                timestamp,
                "macro_bind",
                "first_positive_size_bbo_independent_presence",
                anchor_cents=anchor,
                birth_band=state.get("birth_band"),
                divot_depth_cents=state.get("divot_depth"),
                recut_depth_cents=state.get("recut_depth"),
                recut_timing_minutes=None,
                recut_status="NO_CALL_UNAVAILABLE",
                eligible_ts=state["eligible_ts"],
                advisory_tdeep_ts=None,
                advisory_tdeep_is_hard_gate=False,
            )
        if self.policy["profile"] != "r4_full_drift_stack":
            return

        band = str(state.get("birth_band") or "")
        drift_band = (self.surfaces.drift.get("bands") or {}).get(band)
        reach = (
            drift_band.get("reach")
            if isinstance(drift_band, Mapping) else None
        )
        if isinstance(reach, Mapping) and reach:
            supported = [
                int(depth)
                for depth, probability in reach.items()
                if float(probability) >= 0.5
            ]
            if supported:
                state["drift_reach_depth_cents"] = float(max(supported))
                state["drift_reach_status"] = "AVAILABLE"
                r2._action(
                    state,
                    timestamp,
                    "macro_reach_bind",
                    "source_proved_drift_reach_p50",
                    birth_band=band,
                    depth_cents=state["drift_reach_depth_cents"],
                    source_path=DRIFT_PATH,
                    source_sha256=self.source_receipts.get("drift"),
                    order_changed=False,
                    underlying_presence_continues=True,
                )
            else:
                state["drift_reach_status"] = "NO_CALL_UNAVAILABLE"
        else:
            state["drift_reach_status"] = "NO_CALL_UNAVAILABLE"
        if state["drift_reach_status"] != "AVAILABLE":
            r2._action(
                state,
                timestamp,
                "feature_no_call",
                "drift_reach_unavailable_underlying_presence_continues",
                family_id="source_proved_drift_reach",
                response_status="NO_CALL_UNAVAILABLE",
                underlying_policy_continues=True,
            )

        page_key = "|".join([
            str(self.event["category"]),
            _atlas_role(str(state["role"])),
            _price_cell(float(state["birth_anchor"])),
        ])
        page = (self.atlas.get("pages") or {}).get(page_key)
        bottom = page.get("bottom") if isinstance(page, Mapping) else None
        depth = (
            bottom.get("depth_p50")
            if isinstance(bottom, Mapping) else None
        )
        if (
            isinstance(page, Mapping)
            and int(page.get("n") or 0) > 0
            and depth is not None
        ):
            state["atlas_status"] = "AVAILABLE"
            state["atlas_page"] = page_key
            state["atlas_depth_cents"] = float(depth)
            state["atlas_tdeep_minutes"] = (
                float(bottom["t_med_min"])
                if bottom.get("t_med_min") is not None else None
            )
            r2._action(
                state,
                timestamp,
                "macro_atlas_bind",
                "source_proved_g9_atlas_bottom_reach",
                atlas_page=page_key,
                atlas_n=int(page["n"]),
                depth_p50_cents=state["atlas_depth_cents"],
                t_deep_minutes=state["atlas_tdeep_minutes"],
                t_deep_is_advisory=True,
                source_path=ATLAS_PATH,
                source_sha256=self.source_receipts.get("atlas"),
                order_changed=False,
                underlying_presence_continues=True,
            )
        else:
            state["atlas_status"] = "NO_CALL_UNAVAILABLE"
            r2._action(
                state,
                timestamp,
                "feature_no_call",
                "atlas_reach_unavailable_underlying_presence_continues",
                family_id="source_proved_atlas_reach",
                atlas_page=page_key,
                response_status="NO_CALL_UNAVAILABLE",
                underlying_policy_continues=True,
            )

    def _effective_depth(
        self,
        state: Mapping[str, Any],
        *,
        include_top5: bool = True,
    ) -> float:
        depth = super()._effective_depth(
            state, include_top5=include_top5
        )
        if self.policy["profile"] == "r4_full_drift_stack":
            proved = [
                float(value)
                for value in (
                    state.get("drift_reach_depth_cents"),
                    state.get("atlas_depth_cents"),
                )
                if value is not None
            ]
            if proved:
                depth = max([depth, *proved])
        return depth

    def _posture(self, state: Mapping[str, Any]) -> str:
        if self.policy["profile"] != "r4_full_drift_stack":
            return super()._posture(state)
        recognition = state.get("recognition") or {}
        orientation = state.get("orientation") or {}
        if orientation.get("called_role") == state.get("role"):
            posture = "touch"
        elif float(recognition.get("net_cents") or 0) < 0:
            posture = "walk"
        elif float(recognition.get("net_cents") or 0) > 0:
            posture = "park"
        else:
            posture = super()._posture(state)
        return posture

    def _on_orientation(self, timestamp: float) -> None:
        """Observe macro orientation; never reprice on a clock alone."""
        if "causal_orientation" not in self.families:
            return
        call = r2.orientation_call(
            self.surfaces,
            str(self.event["category"]),
            self.states,
            self.left,
            timestamp,
        )
        for state in self.states:
            prior = self._posture(state)
            state["orientation"] = call
            current = self._posture(state)
            state["macro_posture"] = current
            r2._action(
                state,
                timestamp,
                "orientation_observed",
                "causal_orientation_changes_posture_only",
                orientation=call,
                prior_posture=prior,
                current_posture=current,
                posture_changed=prior != current,
                order_changed=False,
                movement_requires_later_positive_print=True,
                underlying_presence_continues=True,
            )

    def _on_recognition(self, timestamp: float) -> None:
        """Observe chronological drift; never reprice on a clock alone."""
        if "causal_drift_recognition" not in self.families:
            return
        for state in self.states:
            if state["birth_anchor"] is None:
                continue
            history = [
                row for row in state["books"]
                if float(row["ts"]) <= timestamp
            ]
            if not history:
                continue
            prior_posture = self._posture(state)
            anchor = float(state["birth_anchor"])
            prices = [float(row["best_external_bid"]) for row in history]
            current = prices[-1]
            net = current - anchor
            dip = max(0.0, anchor - min(prices))
            band, used, purity = r2.recognized_band(
                self.surfaces,
                str(self.event["category"]),
                anchor,
                net,
                dip,
            )
            state["recognition"] = {
                "observed_at": timestamp,
                "anchor_cents": anchor,
                "current_cents": current,
                "net_cents": net,
                "dip_cents": dip,
                "band": band,
                "used": used,
                "purity": purity,
            }
            if used:
                state["current_band"] = band
                field = (
                    "depth_p90"
                    if (state.get("orientation") or {}).get(
                        "called_role"
                    ) == state["role"]
                    else "depth_p50"
                )
                state["recognition_depth"] = r2.divot_value(
                    self.surfaces, band, field
                )
            current_posture = self._posture(state)
            state["macro_posture"] = current_posture
            r2._action(
                state,
                timestamp,
                "drift_recognition_observed",
                "causal_checkpoint_updates_latent_posture_and_cell",
                recognition=state["recognition"],
                prior_posture=prior_posture,
                current_posture=current_posture,
                posture_changed=prior_posture != current_posture,
                order_changed=False,
                movement_requires_later_positive_print=True,
                underlying_presence_continues=True,
            )

    def _arm_partial_sibling(
        self,
        filled_state: MutableMapping[str, Any],
        timestamp: float,
    ) -> None:
        sibling = next(
            state for state in self.states if state is not filled_state
        )
        if sibling["quantity"] >= r2.LOT:
            return
        sibling["partial_sibling_armed"] = True
        sibling["partial_sibling_armed_ts"] = float(timestamp)
        r2._action(
            sibling,
            timestamp,
            "headroom_partial_arm",
            "positive_partial_fill_arms_sibling_without_budget",
            first_filled_leg=filled_state["leg_id"],
            first_leg_cumulative_quantity=float(filled_state["quantity"]),
            headroom_balance_created=False,
            immediate_order_change=False,
            underlying_policy_continues=True,
        )

    def _recall_recognition_on_print(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
    ) -> None:
        """Recall drift only on a later true-print trigger and new book state."""
        if (
            self.policy["profile"] != "r4_full_drift_stack"
            or "causal_drift_recognition" not in self.families
            or state.get("birth_anchor") is None
            or timestamp <= self.left + float(
                self.parameters[
                    "recognition_checkpoint_seconds_after_left"
                ]
            )
        ):
            return
        book = state.get("current_book")
        if book is None:
            return
        book_ts = float(book["ts"])
        if state.get("last_recognition_recall_book_ts") == book_ts:
            return
        history = [
            row for row in state["books"]
            if float(row["ts"]) <= timestamp
        ]
        if not history:
            return
        prior_posture = self._posture(state)
        prior_band = state.get("current_band")
        anchor = float(state["birth_anchor"])
        prices = [float(row["best_external_bid"]) for row in history]
        current = prices[-1]
        net = current - anchor
        dip = max(0.0, anchor - min(prices))
        band, used, purity = r2.recognized_band(
            self.surfaces,
            str(self.event["category"]),
            anchor,
            net,
            dip,
        )
        state["recognition"] = {
            "observed_at": timestamp,
            "anchor_cents": anchor,
            "current_cents": current,
            "net_cents": net,
            "dip_cents": dip,
            "band": band,
            "used": used,
            "purity": purity,
            "recall_trigger": "receipt_identified_positive_size_print",
            "causal_book_ts": book_ts,
        }
        if used:
            state["current_band"] = band
            field = (
                "depth_p90"
                if (state.get("orientation") or {}).get(
                    "called_role"
                ) == state["role"]
                else "depth_p50"
            )
            state["recognition_depth"] = r2.divot_value(
                self.surfaces, band, field
            )
        state["last_recognition_recall_book_ts"] = book_ts
        current_posture = self._posture(state)
        r2._action(
            state,
            timestamp,
            "drift_recognition_recall",
            "new_causal_book_state_recalled_on_positive_print",
            trigger_is_positive_size_nonself_print=True,
            causal_book_ts=book_ts,
            prior_band=prior_band,
            current_band=state.get("current_band"),
            recognition=state["recognition"],
            prior_posture=prior_posture,
            current_posture=current_posture,
            posture_changed=prior_posture != current_posture,
            order_changed=False,
            movement_uses_current_print_trigger=True,
            underlying_presence_continues=True,
        )

    def _arm_exact_headroom(
        self,
        filled_state: MutableMapping[str, Any],
        timestamp: float,
    ) -> None:
        if any(state.get("headroom_active") for state in self.states):
            return
        sibling = next(
            state for state in self.states if state is not filled_state
        )
        if sibling["quantity"] >= r2.LOT:
            return
        book = filled_state.get("current_book")
        bid_rows = (
            r2.external_bids(book, self._subtract_own()) if book else []
        )
        if not bid_rows:
            sibling["headroom_no_call_reason"] = (
                "contemporaneous_R1_external_bid_unavailable"
            )
            r2._action(
                sibling,
                timestamp,
                "headroom_no_call",
                "contemporaneous_R1_external_bid_unavailable",
                response_status="NO_CALL_UNAVAILABLE",
                underlying_policy_continues=True,
            )
            return
        vwap = float(filled_state["cost"]) / float(
            filled_state["quantity"]
        )
        r1 = float(bid_rows[0][0])
        b1 = vwap - r1
        fee = float(self.parameters["headroom_fee_cents"])
        b2_max = headroom_b2_max(b1, fee)
        sibling.update({
            "headroom_active": True,
            "headroom_armed_ts": float(timestamp),
            "headroom_first_leg_id": filled_state["leg_id"],
            "headroom_first_leg_vwap_cents": vwap,
            "headroom_R1_cents": r1,
            "headroom_R1_ts": float(book["ts"]),
            "headroom_R1_source": book.get(
                "source_receipt_identity"
            ),
            "headroom_b1_cents": b1,
            "headroom_b2_max_cents": b2_max,
            "partial_sibling_armed": True,
        })
        r2._action(
            sibling,
            timestamp,
            "headroom_exact5_arm",
            "first_leg_exact_five_freezes_causal_budget",
            first_filled_leg=filled_state["leg_id"],
            first_leg_exact5_ts=float(timestamp),
            first_leg_exact5_vwap_cents=vwap,
            R1_cents=r1,
            R1_ts=float(book["ts"]),
            R1_source=book.get("source_receipt_identity"),
            b1_cents=b1,
            fee_cents=fee,
            b2_max_cents=b2_max,
            immediate_order_change=False,
            underlying_policy_continues=True,
        )

    def _record_exact5_reference(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
    ) -> None:
        if state.get("exact5_causal_reference") is not None:
            return
        book = state.get("current_book")
        bid_rows = (
            r2.external_bids(book, self._subtract_own()) if book else []
        )
        if not bid_rows:
            state["exact5_causal_reference"] = {
                "status": "NO_CALL_UNAVAILABLE",
                "timestamp": timestamp,
            }
            r2._action(
                state,
                timestamp,
                "causal_exact5_reference",
                "contemporaneous_external_bid_unavailable",
                response_status="NO_CALL_UNAVAILABLE",
            )
            return
        vwap = float(state["cost"]) / float(state["quantity"])
        reference = float(bid_rows[0][0])
        value = {
            "status": "AVAILABLE",
            "exact5_ts": timestamp,
            "vwap_cents": vwap,
            "reference_cents": reference,
            "causal_delta_cents": vwap - reference,
            "source_timestamp": float(book["ts"]),
            "source_receipt": book.get("source_receipt_identity"),
        }
        state["exact5_causal_reference"] = value
        r2._action(
            state,
            timestamp,
            "causal_exact5_reference",
            "exact_five_vwap_minus_contemporaneous_external_bid",
            **value,
        )

    def _fill_from_print(
        self,
        state: MutableMapping[str, Any],
        print_row: Mapping[str, Any],
    ) -> bool:
        """Fill from chronological qualifying volume; queue is diagnostic."""
        order = state.get("active_order")
        if order is None or str(print_row.get("taker_side")) != "no":
            return False
        price = float(print_row["price"])
        size = max(0.0, float(print_row.get("size") or 0))
        if size <= 0 or price > float(order["price"]):
            return False

        if "queue_sensitivity_remaining" not in order:
            queue_observation = order.get("queue_ahead")
            order["queue_sensitivity_unknown"] = (
                queue_observation is None
            )
            order["queue_sensitivity_remaining"] = max(
                0.0, float(queue_observation or 0)
            )
        queue_before = float(order["queue_sensitivity_remaining"])
        queue_after = queue_before
        queue_sensitive_volume = size
        if price == float(order["price"]) and queue_after > 0:
            debit = min(queue_sensitive_volume, queue_after)
            queue_after -= debit
            queue_sensitive_volume -= debit
        order["queue_sensitivity_remaining"] = queue_after

        # Primary authority: every lawful executed contract at the limit or
        # better counts chronologically.  Displayed size and estimated queue
        # cannot reduce, censor, or veto this quantity.
        filled = min(size, float(order["remaining"]))
        order["remaining"] = float(order["remaining"]) - filled
        state["quantity"] = float(state["quantity"]) + filled
        state["cost"] = (
            float(state["cost"]) + filled * float(order["price"])
        )
        completed = state["quantity"] >= r2.LOT - 1e-9
        r2._action(
            state,
            float(print_row["ts"]),
            "fill_observed",
            "primary_qualifying_executed_print_volume",
            order_price_cents=int(order["price"]),
            print_price_cents=price,
            qualifying_print_size=size,
            fill_quantity=filled,
            cumulative_quantity=state["quantity"],
            complete=completed,
            trade_id=print_row.get("trade_id"),
            receipt_id=print_row.get("receipt_id"),
            primary_fill_authority=(
                "chronological_positive_size_nonself_executed_volume_"
                "at_limit_or_better"
            ),
            displayed_depth_required=False,
            estimated_queue_applied_to_primary=False,
            strict_trade_through_required=False,
            one_print_five_contracts_required=False,
            queue_sensitivity_diagnostic_only={
                "queue_unknown": bool(
                    order["queue_sensitivity_unknown"]
                ),
                "estimated_queue_before": queue_before,
                "estimated_queue_after": queue_after,
                "same_print_volume_after_estimated_queue": (
                    queue_sensitive_volume
                ),
                "alters_primary_fill": False,
            },
        )
        if completed:
            state["active_order"] = None
        return completed

    def _replace_at_price(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        price: int,
        *,
        reason: str,
    ) -> None:
        prior = state.get("active_order")
        if prior is not None:
            self._cancel(state, timestamp, reason + "_cancel")
        order = {
            "price": int(price),
            "remaining": r2.LOT - float(state["quantity"]),
            "queue_ahead": self._queue_ahead(state, int(price)),
            "placed_ts": float(timestamp),
        }
        state["active_order"] = order
        state["placed_any"] = True
        r2._action(
            state,
            timestamp,
            "reprice" if prior is not None else "place",
            reason,
            price_cents=int(price),
            quantity=float(order["remaining"]),
            queue_ahead=float(order["queue_ahead"]),
            posture=self._posture(state),
            effective_depth_cents=self._effective_depth(state),
            one_price_authority="round4_headroom_actuator",
        )

    def _headroom_ladder_trigger(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> bool:
        timestamp = float(row["ts"])
        if (
            not state.get("headroom_active")
            or timestamp <= float(state.get("headroom_armed_ts") or timestamp)
            or state["quantity"] >= r2.LOT
        ):
            return False
        state["headroom_trigger_count"] = (
            int(state["headroom_trigger_count"]) + 1
        )
        order = state.get("active_order")
        book = state.get("current_book")
        bid_rows = (
            r2.external_bids(book, self._subtract_own()) if book else []
        )
        ask_rows = r2.asks(book) if book else []
        prior_price = int(order["price"]) if order is not None else None
        prior_queue = (
            float(order["queue_ahead"]) if order is not None else None
        )
        common = {
            "trigger_receipt": str(
                row.get("trade_id") or row.get("receipt_id")
            ),
            "trigger_ts": timestamp,
            "first_filled_leg": state.get("headroom_first_leg_id"),
            "first_leg_exact5_vwap_cents": state.get(
                "headroom_first_leg_vwap_cents"
            ),
            "R1_cents": state.get("headroom_R1_cents"),
            "R1_ts": state.get("headroom_R1_ts"),
            "R1_source": state.get("headroom_R1_source"),
            "b1_cents": state.get("headroom_b1_cents"),
            "fee_cents": state.get("headroom_fee_cents"),
            "b2_max_cents": state.get("headroom_b2_max_cents"),
            "prior_order_price_cents": prior_price,
            "queue_ahead_before": prior_queue,
            "macro_state": {
                "birth_band": state.get("birth_band"),
                "current_band": state.get("current_band"),
                "recut_depth_cents": state.get("recut_depth"),
                "recut_cell_edge_p50": state.get("recut_depth"),
                "orientation": state.get("orientation"),
                "recognition": state.get("recognition"),
                "cohort_status": state.get("cohort_status"),
                "atlas_status": state.get("atlas_status"),
                "drift_reach_status": state.get(
                    "drift_reach_status"
                ),
            },
            "micro_state": {
                "divot_signal_ts": state.get("divot_signal_ts"),
                "positive_prints_consumed": len(
                    state.get("nonself_prints") or []
                ),
                "posture": self._posture(state),
            },
        }
        if order is None or not bid_rows or not ask_rows:
            reason = (
                "sibling_order_unavailable"
                if order is None else "contemporaneous_R2_BBO_unavailable"
            )
            r2._action(
                state,
                timestamp,
                "headroom_decision",
                reason,
                R2_cents=(
                    float(bid_rows[0][0]) if bid_rows else None
                ),
                R2_ts=(float(book["ts"]) if book else None),
                R2_source=(
                    book.get("source_receipt_identity")
                    if book else None
                ),
                proposed_price_cents=None,
                b2_cents=None,
                strict_combined_guard=False,
                maker_guard=False,
                positive_price_guard=False,
                lawful_band_guard=False,
                exact_five_quantity_guard=(
                    float(state["quantity"]) < r2.LOT
                ),
                action_taken=False,
                queue_retained=True,
                queue_surrendered=False,
                queue_ahead_after=prior_queue,
                **common,
            )
            return True

        r2_value = float(bid_rows[0][0])
        maker_ceiling = int(ask_rows[0][0]) - 1
        b2_max = int(state["headroom_b2_max_cents"])
        active_b2 = float(prior_price) - r2_value
        if active_b2 > b2_max:
            proposed = math.floor(r2_value + b2_max)
            movement_kind = "budget_reducing_correction"
        else:
            proposed = int(prior_price) + int(
                self.parameters["headroom_step_cents"]
            )
            movement_kind = "one_cent_improvement"
        b2 = float(proposed) - r2_value
        b1 = float(state["headroom_b1_cents"])
        fee = float(state["headroom_fee_cents"])
        strict = strict_pair_budget(b1, b2, fee)
        at_most_one_up = (
            proposed <= int(prior_price) + 1
            if proposed > int(prior_price) else True
        )
        guards = {
            "strict_combined_guard": strict and b2 <= b2_max,
            "maker_guard": proposed <= maker_ceiling,
            "positive_price_guard": proposed > 0,
            "lawful_band_guard": 1 <= proposed <= 99,
            "exact_five_quantity_guard": (
                0 <= float(state["quantity"]) < r2.LOT
                and r2.LOT - float(state["quantity"]) <= r2.LOT
            ),
            "one_cent_per_trigger_guard": at_most_one_up,
        }
        changed = proposed != prior_price and all(guards.values())
        next_queue = (
            self._queue_ahead(state, proposed)
            if changed else prior_queue
        )
        reason = (
            movement_kind
            if changed
            else (
                "proposed_price_unchanged"
                if proposed == prior_price
                else "headroom_guard_refusal"
            )
        )
        r2._action(
            state,
            timestamp,
            "headroom_decision",
            reason,
            R2_cents=r2_value,
            R2_ts=float(book["ts"]),
            R2_source=book.get("source_receipt_identity"),
            proposed_price_cents=proposed,
            b2_cents=b2,
            combined_budget_cents=b1 + b2 + fee,
            maker_ask_cents=float(ask_rows[0][0]),
            maker_ceiling_cents=maker_ceiling,
            movement_kind=movement_kind,
            **guards,
            action_taken=changed,
            queue_retained=not changed,
            queue_surrendered=changed,
            queue_ahead_after=next_queue,
            **common,
        )
        if changed:
            state["headroom_action_count"] = (
                int(state["headroom_action_count"]) + 1
            )
            state["headroom_queue_surrendered"] = float(
                state["headroom_queue_surrendered"]
            ) + float(prior_queue or 0)
            self._replace_at_price(
                state,
                timestamp,
                int(proposed),
                reason="causal_headroom_ladder",
            )
        return True

    def _on_print(
        self, state: MutableMapping[str, Any], row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
        valid, validation_reason = r2.positive_public_print(row)
        if not valid:
            r2._action(
                state,
                timestamp,
                "print_excluded",
                validation_reason,
                trade_id=row.get("trade_id"),
                receipt_id=row.get("receipt_id"),
                raw_size=row.get("size"),
                contributes_zero=True,
                triggered_surfaces=[],
            )
            return
        receipt_identity = str(
            row.get("trade_id") or row.get("receipt_id")
        ).strip()
        if receipt_identity in state["seen_print_receipts"]:
            r2._action(
                state,
                timestamp,
                "print_excluded",
                "duplicate_print_receipt_identity",
                trade_id=row.get("trade_id"),
                receipt_id=row.get("receipt_id"),
                contributes_zero=True,
                triggered_surfaces=[],
            )
            return
        state["seen_print_receipts"].add(receipt_identity)
        if row.get("own_order_fingerprint") is True:
            r2._action(
                state,
                timestamp,
                "contributed_volume_excluded",
                "own_fingerprint_never_confirms_market",
                trade_id=row.get("trade_id"),
                size=float(row.get("size") or 0),
            )
            return

        quantity_before = float(state["quantity"])
        self._fill_from_print(state, row)
        quantity_after = float(state["quantity"])
        first_positive = quantity_before <= 0 < quantity_after
        first_exact_five = (
            quantity_before < r2.LOT
            and quantity_after >= r2.LOT - 1e-9
        )

        prior_divot_ts = state.get("divot_signal_ts")
        self._detect_divot(state, row)
        new_divot = (
            state.get("divot_signal_ts") is not None
            and state.get("divot_signal_ts") != prior_divot_ts
        )
        state["nonself_prints"].append(dict(row))
        if str(row.get("taker_side")) == "no":
            state["flow_sell_timestamps"].append(timestamp)
            state["walk_sell_evidence"].append(dict(row))
        state["divot_window"].append((
            timestamp, float(row["price"])
        ))
        r2.bisect.insort(
            state["divot_prices_sorted"], float(row["price"])
        )
        self._recall_recognition_on_print(state, timestamp)

        if first_positive:
            self._arm_partial_sibling(state, timestamp)
        if first_exact_five:
            self._record_exact5_reference(state, timestamp)
            self._arm_exact_headroom(state, timestamp)

        headroom_triggered = self._headroom_ladder_trigger(state, row)
        if (
            not headroom_triggered
            and new_divot
            and state["active_order"] is not None
            and "positive_print_divot_recut" in self.families
        ):
            self._reprice(
                state,
                timestamp,
                "positive_print_divot_recut",
            )
        if not state.get("headroom_active"):
            self._maybe_walk(state, timestamp)
        self._maybe_place(
            state,
            timestamp,
            (
                "positive_print_divot_trigger"
                if new_divot else "positive_print_flow_trigger"
            ),
        )

    def _terminalize(self, state: MutableMapping[str, Any]) -> None:
        if (
            state.get("partial_sibling_armed")
            and not state.get("headroom_active")
            and state["quantity"] < r2.LOT
        ):
            r2._action(
                state,
                self.horizon,
                "headroom_no_call",
                "first_leg_never_reached_exact_five",
                response_status="NO_CALL_UNAVAILABLE",
                partial_arm_did_not_spend_budget=True,
                underlying_policy_continues=True,
            )
        elif (
            state.get("headroom_active")
            and int(state.get("headroom_trigger_count") or 0) == 0
        ):
            r2._action(
                state,
                self.horizon,
                "headroom_no_call",
                "no_strictly_later_lawful_sibling_print_trigger",
                response_status="NO_CALL_UNAVAILABLE",
                underlying_policy_continues=True,
            )
        super()._terminalize(state)

    def _result(
        self,
        event: Mapping[str, Any],
        states: Sequence[Mapping[str, Any]],
        event_terminal: str,
    ) -> dict[str, Any]:
        result = super()._result(event, states, event_terminal)
        result["schema_version"] = VERSION + "-order-stream-v1"
        result["instrument_version"] = VERSION
        result["round4_mechanical_contract"] = {
            "independent_pair_presence": True,
            "macro_never_place_skip_gate": True,
            "advisory_tdeep_not_hard_gate": True,
            "positive_print_movement_only": True,
            "partial_fill_arms_without_budget": True,
            "exact_five_freezes_b1": True,
            "headroom_fee_cents": 0,
            "strict_pair_budget": True,
            "combined_cost_never_gates": True,
            "individual_delta_never_gates": True,
            "primary_fill_authority": (
                "chronological positive-size non-self executed print "
                "volume at limit or better"
            ),
            "displayed_depth_required_for_fill": False,
            "estimated_queue_applied_to_primary_fill": False,
            "queue_sensitivity_is_diagnostic_only": True,
            "evaluation_truth_access": False,
            "candidate_scored": False,
        }
        result["scored"] = False
        result["metrics"] = None
        return result


def run_event(
    repo: Path,
    event: Mapping[str, Any],
    candidate_id: str,
    *,
    surfaces: r2.SurfaceBundle | None = None,
    atlas: Mapping[str, Any] | None = None,
    source_receipts: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    spec = load_candidate_spec(repo)
    policy = candidate_policy(spec, candidate_id)
    bundle = surfaces if surfaces is not None else r2.load_surfaces(repo)
    atlas_value = atlas if atlas is not None else load_atlas(repo)
    return Round4Instrument(
        bundle,
        policy,
        atlas=atlas_value,
        source_receipts=source_receipts,
    ).run(event)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit one score-free Round-4 order stream."
    )
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--event-json", type=Path, required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    event = r2.read_json(args.event_json.resolve())
    result = run_event(repo, event, args.candidate_id)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
