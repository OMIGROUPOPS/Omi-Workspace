#!/usr/bin/env python3
"""Score-free Round-3 Window-1 counterfactual order-stream instrument.

Round 3 keeps the Round-2 evidence validators, fill model, frozen surfaces,
policy/evaluation clock separation, and holdout refusals.  It changes only the
mechanics implicated by the admitted partner-leg starvation forensic:

* both legs establish independent maker presence from their first causal BBO;
* fitted t_deep remains advisory instead of becoming a hard eligibility gate;
* cell recuts preserve queue until a positive-size causal trigger;
* first positive fill arms a real, later sibling +1 action chain.

The module has no scorer, ranking, exchange, production, configuration,
position, exit, settlement, DCA, Window-2, or holdout interface.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import deque
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

import window1_round2_instrument as r2


VERSION = "window1-round3-causal-instrument-v1"
CANDIDATE_SPEC_PATH = (
    "arb-executor/docs/research/window1/WINDOW1_ROUND3_CANDIDATES_V1.json"
)


InstrumentError = r2.InstrumentError


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    spec = r2.read_json(repo / CANDIDATE_SPEC_PATH)
    if spec.get("instrument_version") != VERSION:
        raise InstrumentError("Round-3 candidate spec version mismatch")
    if spec.get("free_numeric_parameters") != []:
        raise InstrumentError("Round-3 cannot expose free parameters")
    return spec


def candidate_policy(
    spec: Mapping[str, Any], candidate_id: str,
    *, ablations: Iterable[str] = (),
) -> dict[str, Any]:
    if list(ablations):
        raise InstrumentError("Round-3 has no post-freeze ablation surface")
    allowed = [str(value) for value in spec.get("candidate_ids") or []]
    if candidate_id not in allowed:
        raise InstrumentError(f"candidate is not frozen: {candidate_id}")
    parts = candidate_id.split("__")
    if len(parts) != 3:
        raise InstrumentError(f"malformed candidate id: {candidate_id}")
    profile, posture_pair, response = parts
    profile_families = spec.get("profiles", {}).get(profile)
    posture = spec.get("posture_pairs", {}).get(posture_pair)
    if not isinstance(profile_families, list) or not isinstance(posture, dict):
        raise InstrumentError(f"candidate mapping missing: {candidate_id}")
    if response not in {"hold", "reaim"}:
        raise InstrumentError(f"unknown sibling response: {response}")
    return {
        "candidate_id": candidate_id,
        "profile": profile,
        "posture_pair": posture_pair,
        "posture_by_role": dict(posture),
        "sibling_response": response,
        "enabled_families": sorted(map(str, profile_families)),
        "ablations": [],
        "parameters": dict(spec["common_parameters"]),
    }


class Round3Instrument(r2.CausalInstrument):
    """Round-2 causal substrate with evidence-proved Round-3 mechanics."""

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        availability = dict(leg.get("feature_availability") or {})
        required = []
        if "leg_specific_posture" in self.families:
            required.append("causal_role")
        if "true_print_flow" in self.families:
            required.append("true_prints")
        if "own_order_contribution_subtraction" in self.families:
            required.append("own_order_fingerprints")
        missing = [
            name for name in required
            if availability.get(name) is not True
        ]
        state: MutableMapping[str, Any] = {
            "event_id": str(event["event_id"]),
            "candidate_id": str(self.policy["candidate_id"]),
            "leg_id": str(leg["leg_id"]),
            "ticker": str(leg["ticker"]),
            "role": str(leg["role"]),
            "availability": availability,
            "missing_features": missing,
            "actions": [],
            "books": [],
            "nonself_prints": [],
            "seen_book_receipts": set(),
            "seen_print_receipts": set(),
            "flow_sell_timestamps": deque(),
            "walk_sell_evidence": deque(
                maxlen=int(
                    self.parameters["walk"]["minimum_chain_prints"]
                )
            ),
            "divot_window": deque(),
            "divot_prices_sorted": [],
            "current_book": None,
            "birth_anchor": None,
            "birth_band": None,
            "current_band": None,
            "recut_depth": None,
            "recut_timing_minutes": None,
            "advisory_tdeep_ts": None,
            "divot_depth": None,
            "cohort_depth": None,
            "cohort_n": 0,
            "cohort_zone": None,
            "cohort_status": "NOT_LOADED",
            "recognition_depth": None,
            "recognition": None,
            "orientation": None,
            "eligible_ts": self.left,
            "divot_signal_ts": None,
            "divot_signal_median": None,
            "active_order": None,
            "placed_any": False,
            "quantity": 0.0,
            "cost": 0.0,
            "sibling_bias_cents": 0,
            "sibling_reaim_pending": False,
            "sibling_reaim_armed_ts": None,
            "sibling_reaim_first_filled_leg": None,
            "sibling_reaim_first_fill_vwap_cents": None,
            "sibling_reaim_applied_ts": None,
            "sibling_reaim_no_call_reason": None,
            "walk_distance_cents": 0,
            "last_walk_evidence_index": 0,
            "terminal": None,
            "feature_censored": bool(missing),
            "last_pair_cost_no_call": None,
        }
        r2._action(
            state, self.left, "leg_open", "pair_stream_initialized"
        )
        if missing:
            r2._action(
                state,
                self.left,
                "feature_censor",
                "required_feature_absent",
                missing_features=missing,
            )
        if (
            "bbo_top5_pressure" in self.families
            and availability.get("top5") is not True
        ):
            r2._action(
                state,
                self.left,
                "feature_no_call",
                "top5_unavailable_underlying_bbo_policy_continues",
                family_id="bbo_top5_pressure",
                response_status="NO_CALL_UNAVAILABLE",
                underlying_policy_continues=True,
            )
        return state

    def _initialize_birth(
        self, state: MutableMapping[str, Any], timestamp: float,
    ) -> None:
        book = state["current_book"]
        bid_rows = r2.external_bids(book, self._subtract_own())
        ask_rows = r2.asks(book)
        if not bid_rows or not ask_rows:
            state["feature_censored"] = True
            state["missing_features"].append(
                "positive_size_external_bbo"
            )
            r2._action(
                state,
                timestamp,
                "feature_censor",
                "positive_size_external_bbo_unavailable",
            )
            return
        anchor = float(bid_rows[0][0])
        state["birth_anchor"] = anchor
        band = r2.default_flat_band(
            self.surfaces, str(self.event["category"]), anchor
        )
        state["birth_band"] = band
        state["current_band"] = band
        state["divot_depth"] = r2.divot_value(
            self.surfaces, band, "depth_p50"
        )
        cell = r2.recut_cell(
            self.surfaces, str(self.event["category"]), anchor
        )
        if cell is None or cell.get("edge_p50") is None:
            state["feature_censored"] = True
            state["missing_features"].append("dynamic_recut_cell")
            r2._action(
                state,
                timestamp,
                "feature_censor",
                "dynamic_recut_cell_unavailable",
                anchor_cents=anchor,
            )
            return
        state["recut_depth"] = float(cell["edge_p50"])
        state["recut_timing_minutes"] = float(cell["t_deep_p50"])
        state["eligible_ts"] = max(self.left, float(timestamp))
        state["advisory_tdeep_ts"] = (
            float(self.event["policy_anchor_ts"])
            + float(cell["t_deep_p50"]) * 60.0
        )

        minimum_n = int(self.parameters["cohort_minimum_n"])
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
                self.parameters["cohort_minimum_reaim_delta_cents"]
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
                state["cohort_status"] = "NO_CALL_BELOW_REAIM_DELTA"
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
            birth_band=band,
            divot_depth_cents=state["divot_depth"],
            recut_depth_cents=state["recut_depth"],
            recut_timing_minutes=state["recut_timing_minutes"],
            eligible_ts=state["eligible_ts"],
            advisory_tdeep_ts=state["advisory_tdeep_ts"],
            advisory_tdeep_is_hard_gate=False,
        )

    def _effective_depth(
        self,
        state: Mapping[str, Any],
        *,
        include_top5: bool = True,
    ) -> float:
        values = [
            float(value)
            for value in (
                state.get("divot_depth"),
                state.get("recut_depth"),
            )
            if value is not None
        ]
        if not values:
            raise InstrumentError("no causal divot/recut depth")
        depth = max(values)
        if (
            "cohort_steering" in self.families
            and state.get("cohort_depth") is not None
        ):
            depth = float(state["cohort_depth"])
        if (
            "causal_drift_recognition" in self.families
            and state.get("recognition_depth") is not None
        ):
            depth = float(state["recognition_depth"])
        orientation = state.get("orientation") or {}
        if (
            "causal_orientation" in self.families
            and orientation.get("called_role") == state.get("role")
        ):
            p90 = r2.divot_value(
                self.surfaces,
                str(state.get("current_band")),
                "depth_p90",
            )
            if p90 is not None:
                depth = max(depth, p90)
        if (
            include_top5
            and
            "bbo_top5_pressure" in self.families
            and state.get("availability", {}).get("top5") is True
        ):
            ratio = r2.book_pressure_ratio(
                state["current_book"], self._subtract_own()
            )
            if ratio is not None and ratio >= float(
                self.parameters[
                    "top5_ask_over_external_bid_threshold"
                ]
            ):
                depth += float(
                    self.parameters[
                        "top5_pressure_extra_depth_cents"
                    ]
                )
        return max(0.0, depth)

    def _target_price(
        self,
        state: Mapping[str, Any],
        *,
        include_top5: bool = True,
    ) -> int:
        book = state["current_book"]
        bid_rows = r2.external_bids(book, self._subtract_own())
        ask_rows = r2.asks(book)
        if not bid_rows or not ask_rows:
            raise InstrumentError("positive-size BBO unavailable at decision")
        external_bid = int(bid_rows[0][0])
        maker_ceiling = int(ask_rows[0][0]) - 1
        depth = self._effective_depth(
            state, include_top5=include_top5
        )
        posture = self._posture(state)
        if posture == "touch":
            target = external_bid
        elif posture == "join":
            target = min(external_bid + 1, maker_ceiling)
        elif posture in {"park", "walk"}:
            target = external_bid - r2.nearest_int(depth)
        else:
            raise InstrumentError(f"unknown posture: {posture}")
        target += int(state.get("sibling_bias_cents") or 0)
        return max(1, min(maker_ceiling, int(target)))

    def _pair_cost_passes(
        self, state: Mapping[str, Any], price: int,
    ) -> tuple[bool, float | None]:
        sibling = next(
            (row for row in self.states if row is not state),
            None,
        )
        if sibling is None or sibling.get("active_order") is None:
            return True, None
        sibling_price = float(sibling["active_order"]["price"])
        combined = float(price) + sibling_price
        return (
            combined
            <= float(self.parameters["maximum_pair_order_cost_cents"]),
            combined,
        )

    def _place(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
        *,
        action_type: str = "place",
    ) -> None:
        if state["feature_censored"] or state["quantity"] >= r2.LOT:
            return
        price = self._target_price(state)
        passes, combined = self._pair_cost_passes(state, price)
        if not passes:
            fingerprint = (price, combined)
            if state.get("last_pair_cost_no_call") != fingerprint:
                state["last_pair_cost_no_call"] = fingerprint
                r2._action(
                    state,
                    timestamp,
                    "pair_cost_no_call",
                    "combined_maker_orders_exceed_frozen_par_guard",
                    proposed_price_cents=price,
                    combined_order_cost_cents=combined,
                    maximum_pair_order_cost_cents=float(
                        self.parameters[
                            "maximum_pair_order_cost_cents"
                        ]
                    ),
                    underlying_pair_management_continues=True,
                )
            return
        state["last_pair_cost_no_call"] = None
        target_without_top5 = self._target_price(
            state, include_top5=False
        )
        if target_without_top5 != price:
            r2._action(
                state,
                timestamp,
                "top5_pressure_order_effect",
                "causal_top5_pressure_changes_order_price",
                order_action=action_type,
                order_price_without_top5_cents=target_without_top5,
                order_price_with_top5_cents=price,
                exact_difference_cents=price - target_without_top5,
            )
        order = {
            "price": price,
            "remaining": r2.LOT - float(state["quantity"]),
            "queue_ahead": self._queue_ahead(state, price),
            "placed_ts": float(timestamp),
        }
        state["active_order"] = order
        state["placed_any"] = True
        r2._action(
            state,
            timestamp,
            action_type,
            reason,
            price_cents=price,
            quantity=order["remaining"],
            queue_ahead=order["queue_ahead"],
            posture=self._posture(state),
            effective_depth_cents=self._effective_depth(state),
            one_price_authority="round3_instrument",
        )

    def _reprice(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
        *,
        sibling_trigger: str | None = None,
    ) -> None:
        order = state.get("active_order")
        if order is None or state["feature_censored"]:
            return
        activated_reaim = False
        if sibling_trigger is not None:
            activated_reaim = self._activate_pending_sibling_reaim(
                state, timestamp, sibling_trigger
            )
        if activated_reaim:
            reason = "first_fill_sibling_reaim_later_trigger"
        target = self._target_price(state)
        if target == int(order["price"]):
            return
        passes, combined = self._pair_cost_passes(state, target)
        if not passes:
            fingerprint = (target, combined)
            if state.get("last_pair_cost_no_call") != fingerprint:
                state["last_pair_cost_no_call"] = fingerprint
                r2._action(
                    state,
                    timestamp,
                    "pair_cost_no_call",
                    "reprice_refused_current_queue_preserved",
                    proposed_price_cents=target,
                    current_price_cents=int(order["price"]),
                    combined_order_cost_cents=combined,
                    maximum_pair_order_cost_cents=float(
                        self.parameters[
                            "maximum_pair_order_cost_cents"
                        ]
                    ),
                    current_order_held=True,
                )
            return
        state["last_pair_cost_no_call"] = None
        self._cancel(state, timestamp, reason + "_cancel")
        self._place(
            state, timestamp, reason, action_type="reprice"
        )

    def _maybe_place(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
    ) -> None:
        if (
            state["active_order"] is not None
            or state["quantity"] >= r2.LOT
            or state["feature_censored"]
            or state["current_book"] is None
            or timestamp < float(state["eligible_ts"])
        ):
            return
        if state.get("sibling_reaim_pending") and reason.startswith(
            "positive_print_"
        ):
            if not self._flow_confirmed(state, timestamp):
                return
            self._activate_pending_sibling_reaim(
                state, timestamp, reason
            )
        self._place(
            state,
            timestamp,
            (
                "first_fill_sibling_reaim_later_trigger"
                if state.get("sibling_reaim_applied_ts") == timestamp
                else reason
            ),
        )

    def _on_book(
        self, state: MutableMapping[str, Any], row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
        receipt_identity = str(
            row.get("source_receipt_identity") or ""
        ).strip()
        if not receipt_identity:
            r2._action(
                state,
                timestamp,
                "book_excluded",
                "missing_book_receipt_identity",
                contributes_zero=True,
                triggered_surfaces=[],
            )
            return
        if receipt_identity in state["seen_book_receipts"]:
            r2._action(
                state,
                timestamp,
                "book_excluded",
                "duplicate_book_receipt_identity",
                source_receipt_identity=receipt_identity,
                contributes_zero=True,
                triggered_surfaces=[],
            )
            return
        state["seen_book_receipts"].add(receipt_identity)
        book = dict(row)
        book["bids"] = [
            list(value) for value in row.get("bids") or []
        ]
        book["asks"] = [
            list(value) for value in row.get("asks") or []
        ]
        state["current_book"] = book
        bid_rows = r2.external_bids(book, self._subtract_own())
        ask_rows = r2.asks(book)
        if not bid_rows or not ask_rows:
            return
        state["books"].append({
            "ts": timestamp,
            "best_external_bid": float(bid_rows[0][0]),
        })
        if state["birth_anchor"] is None:
            self._initialize_birth(state, timestamp)
        elif "positive_print_divot_recut" in self.families:
            cell = r2.recut_cell(
                self.surfaces,
                str(self.event["category"]),
                float(bid_rows[0][0]),
            )
            if cell and cell.get("edge_p50") is not None:
                prior = state["recut_depth"]
                current = float(cell["edge_p50"])
                if prior is None or current != float(prior):
                    state["recut_depth"] = current
                    r2._action(
                        state,
                        timestamp,
                        "latent_pair_recut",
                        "causal_book_updates_cell_queue_held",
                        prior_depth_cents=prior,
                        recut_depth_cents=current,
                        order_changed=False,
                    )
        self._maybe_place(
            state, timestamp, "independent_first_causal_bbo_presence"
        )

    def _terminalize(self, state: MutableMapping[str, Any]) -> None:
        if (
            state.get("birth_anchor") is None
            and not state["feature_censored"]
        ):
            state["feature_censored"] = True
            state["missing_features"].append(
                "positive_size_external_bbo"
            )
            r2._action(
                state,
                self.horizon,
                "feature_censor",
                "positive_size_external_bbo_unavailable",
            )
        super()._terminalize(state)

    def _sibling_response(
        self, filled_state: MutableMapping[str, Any], timestamp: float,
    ) -> None:
        if "first_fill_sibling_response" not in self.families:
            return
        sibling = next(
            state for state in self.states if state is not filled_state
        )
        if sibling["quantity"] >= r2.LOT:
            return
        response = str(self.policy["sibling_response"])
        if response == "hold":
            if sibling["feature_censored"]:
                return
            r2._action(
                sibling,
                timestamp,
                "sibling_hold",
                "first_positive_fill_other_leg_independently_held",
                first_filled_leg=filled_state["leg_id"],
                active_order=sibling["active_order"] is not None,
                order_changed=False,
            )
            return
        if response != "reaim":
            raise InstrumentError(f"unknown sibling response: {response}")
        if sibling["feature_censored"]:
            sibling["sibling_reaim_no_call_reason"] = (
                "required_sibling_policy_evidence_unavailable"
            )
            r2._action(
                sibling,
                timestamp,
                "sibling_reaim_no_call",
                "required_sibling_policy_evidence_unavailable",
                response_status="NO_CALL_UNAVAILABLE",
                first_filled_leg=filled_state["leg_id"],
                underlying_policy_continues=True,
            )
            return
        sibling["sibling_reaim_pending"] = True
        sibling["sibling_reaim_armed_ts"] = float(timestamp)
        sibling["sibling_reaim_first_filled_leg"] = (
            filled_state["leg_id"]
        )
        sibling["sibling_reaim_first_fill_vwap_cents"] = (
            float(filled_state["cost"])
            / float(filled_state["quantity"])
        )
        r2._action(
            sibling,
            timestamp,
            "sibling_reaim_armed",
            "first_positive_fill_arms_later_sibling_owned_trigger",
            first_filled_leg=filled_state["leg_id"],
            first_leg_fill_ts=float(timestamp),
            reaim_cents=int(
                self.parameters["first_fill_sibling_reaim_cents"]
            ),
            immediate_order_change=False,
            sibling_eligible_ts=float(sibling["eligible_ts"]),
            underlying_policy_continues=True,
        )

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

        first_positive_fill = (
            quantity_before <= 0
            and float(state["quantity"]) > 0
        )
        if first_positive_fill:
            self._sibling_response(state, timestamp)

        activated_reaim = False
        if (
            state.get("sibling_reaim_pending")
            and timestamp > float(
                state.get("sibling_reaim_armed_ts") or timestamp
            )
            and self._flow_confirmed(state, timestamp)
        ):
            activated_reaim = self._activate_pending_sibling_reaim(
                state,
                timestamp,
                (
                    "positive_print_divot"
                    if new_divot else "positive_print_flow"
                ),
            )
            if activated_reaim and state["active_order"] is not None:
                self._reprice(
                    state,
                    timestamp,
                    "first_fill_sibling_reaim_later_trigger",
                )
        if (
            new_divot
            and state["active_order"] is not None
            and not activated_reaim
            and "positive_print_divot_recut" in self.families
        ):
            self._reprice(
                state,
                timestamp,
                "positive_print_divot_recut",
                sibling_trigger="positive_print_divot",
            )
        self._maybe_walk(state, timestamp)
        self._maybe_place(
            state,
            timestamp,
            (
                "positive_print_divot_trigger"
                if new_divot else "positive_print_flow_trigger"
            ),
        )

    def _result(
        self,
        event: Mapping[str, Any],
        states: Sequence[Mapping[str, Any]],
        event_terminal: str,
    ) -> dict[str, Any]:
        result = super()._result(event, states, event_terminal)
        result["schema_version"] = VERSION + "-order-stream-v1"
        result["instrument_version"] = VERSION
        result["round3_mechanical_contract"] = {
            "independent_pair_presence": True,
            "advisory_tdeep_not_hard_gate": True,
            "positive_print_recut_only": True,
            "first_positive_fill_sibling_response": True,
            "candidate_scored": False,
        }
        return result


def run_event(
    repo: Path,
    event: Mapping[str, Any],
    candidate_id: str,
    *,
    surfaces: r2.SurfaceBundle | None = None,
) -> dict[str, Any]:
    spec = load_candidate_spec(repo)
    policy = candidate_policy(spec, candidate_id)
    bundle = surfaces if surfaces is not None else r2.load_surfaces(repo)
    return Round3Instrument(bundle, policy).run(event)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit one score-free Round-3 order stream."
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
