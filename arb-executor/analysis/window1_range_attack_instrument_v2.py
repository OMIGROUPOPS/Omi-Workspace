#!/usr/bin/env python3
"""Narrow strict-ask accounting repair for the frozen range-attack simulator.

V1 remains immutable.  This overlay changes only the accounting-fill union and
the ordering of book handling: a lawful external ask strictly below an already
exposed buy limit is credited at that original limit before maker safety may
cancel or reprice it.  All target, posture, LIVE-AIM, divot, expression, and
combined-headroom mechanics are inherited unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping

import window1_range_attack_instrument as v1


VERSION = "window1-range-attack-simulator-v2-strict-ask-accounting"
CANDIDATE_SPEC_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_RANGE_ATTACK_CANDIDATES_V2_STRICT_ASK.json"
)
EXACT_PARENT = "66b50db35e9dcec756ce6366bed1fe44147f8e29"
CONTROLLING_AUDIT = "43dab8df0c7ce2394d35beadd7d035b8519f66ac"
AUDIT_REPORT_BLOB = "b9ab235e51f0d2ca82dd066c1a78a318d644dec7"
AUDIT_CENSUS_BLOB = "8a769ba40669408a4f0945302b99ea9495c5038f"

# Re-export the frozen V1 surface for builders and tests.
ATLAS_PATH = v1.ATLAS_PATH
GUIDEBOOK_PATH = v1.GUIDEBOOK_PATH
RECUT_PATH = v1.RECUT_PATH
TAKER_REACH_PATH = v1.TAKER_REACH_PATH
DIVOT_PATH = v1.DIVOT_PATH
DRIFT_PATH = v1.DRIFT_PATH
BAND_PATH = v1.BAND_PATH
LIBRARY_PATH = v1.LIBRARY_PATH
ORIENT_PATH = v1.ORIENT_PATH
LIVEAIM_PROOF_PATH = v1.LIVEAIM_PROOF_PATH
LIVEAIM_CODE_PATH = v1.LIVEAIM_CODE_PATH
VOLUME_PATH = v1.VOLUME_PATH
DEVELOPMENT_DATES = v1.DEVELOPMENT_DATES
SEALED_HOLDOUT_DATES = v1.SEALED_HOLDOUT_DATES
LOT = v1.LOT
CARRIED_UNKNOWN = v1.CARRIED_UNKNOWN
VERIFIED_PRINT = v1.VERIFIED_PRINT
RangeAttackError = v1.RangeAttackError
compact = v1.compact
sha256_json = v1.sha256_json
read_json = v1.read_json
positive_print = v1.positive_print
headroom_b2_max = v1.headroom_b2_max
strict_pair_budget = v1.strict_pair_budget
_source_receipt = v1._source_receipt
_top5_depth_within_three = v1._top5_depth_within_three


def __getattr__(name: str) -> Any:
    """Forward every untouched V1 helper/constant to the frozen module."""
    return getattr(v1, name)


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    spec = read_json(repo / CANDIDATE_SPEC_PATH)
    expected = [
        "w1_range_attack__macro_hold__combined_headroom",
        "w1_range_attack__macro_micro__combined_headroom",
    ]
    if spec.get("instrument_version") != VERSION:
        raise RangeAttackError("strict-ask V2 instrument version mismatch")
    if list(spec.get("candidate_ids") or []) != expected:
        raise RangeAttackError("range-attack candidate order changed")
    if spec.get("exact_parent") != EXACT_PARENT:
        raise RangeAttackError("strict-ask V2 parent binding changed")
    if spec.get("controlling_audit") != CONTROLLING_AUDIT:
        raise RangeAttackError("strict-ask V2 audit binding changed")
    if spec.get("free_numeric_parameters") != []:
        raise RangeAttackError("free parameters are forbidden")
    if spec.get("candidate_additions_after_freeze_allowed") is not False:
        raise RangeAttackError("candidate family is not frozen")
    return spec


def candidate_policy(
    spec: Mapping[str, Any],
    candidate_id: str,
    *,
    ablations: Iterable[str] = (),
) -> dict[str, Any]:
    # V1's policy constructor contains the complete frozen candidate behavior.
    return v1.candidate_policy(spec, candidate_id, ablations=ablations)


class RangeAttackSimulatorV2(v1.RangeAttackSimulator):
    """V1 strategy with a corrected FILLABLE_AT_X accounting union."""

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        state = super()._new_state(event, leg)
        state.update({
            "simulated_fill_evidence_type": None,
            "simulated_fill_external_ask_cents": None,
            "simulated_fill_order_interval_id": None,
            "simulated_fill_book_receipt": None,
            "deferred_equal_ask_maker_safety": None,
        })
        return state

    def _flush_deferred_equal_ask_maker_safety(
        self,
        state: MutableMapping[str, Any],
        *,
        effective_ts: float,
    ) -> None:
        deferred = state.get("deferred_equal_ask_maker_safety")
        if deferred is None:
            return
        state["deferred_equal_ask_maker_safety"] = None
        order = state.get("active_order")
        if (
            order is None
            or state["simulated_accounting_quantity"] == LOT
            or order.get("interval_index") != deferred["interval_index"]
        ):
            return
        _, asks = self._lawful_bbo(state)
        if not asks or int(order["price"]) < int(asks[0][0]):
            return
        # A strict ask would already have been credited during its book update.
        if int(asks[0][0]) < int(order["price"]):
            raise RangeAttackError(
                "deferred maker safety reached uncredited strict ask"
            )
        self._place_or_reprice(
            state,
            float(effective_ts),
            int(asks[0][0]) - 1,
            "maker_safety_external_ask_move",
            authority="MAKER_SAFETY",
            composed=False,
            allow_upward=False,
        )

    def _credit_fillable_at_x(
        self,
        state: MutableMapping[str, Any],
        *,
        timestamp: float,
        evidence_type: str,
        evidence_receipt: str,
        print_row: Mapping[str, Any] | None = None,
        external_ask_cents: int | None = None,
    ) -> bool:
        order = state.get("active_order")
        if order is None or state["simulated_accounting_quantity"] == LOT:
            return False
        interval = state["order_intervals"][order["interval_index"]]
        exposed_x = int(order["price"])
        if evidence_type == "PRICE_REACHED":
            if print_row is None or float(print_row["price"]) > exposed_x:
                return False
            close_reason = "CAUSAL_TAPE_PRICE_REACHED"
            action = "price_reached_policy_tape"
            reason = (
                "receipt_identified_positive_public_execution_"
                "at_or_below_limit"
            )
            evidence_fields = {
                "print_price_cents": float(print_row["price"]),
                "print_size": float(print_row["size"]),
                "print_receipt": evidence_receipt,
            }
            arm_reason = "first_PRICE_REACHED_leg_freezes_causal_pair_budget"
        elif evidence_type == "STRICT_ASK_CERTAIN_FILL":
            if external_ask_cents is None or int(external_ask_cents) >= exposed_x:
                return False
            close_reason = "STRICT_ASK_CERTAIN_FILL_AT_ORIGINAL_EXPOSED_X"
            action = "strict_ask_certain_fill"
            reason = (
                "lawful_external_best_ask_strictly_below_exposed_limit_"
                "credited_before_maker_safety"
            )
            evidence_fields = {
                "external_ask_price_cents": int(external_ask_cents),
                "book_receipt": evidence_receipt,
            }
            arm_reason = (
                "first_STRICT_ASK_CERTAIN_FILL_leg_"
                "freezes_causal_pair_budget"
            )
        else:
            raise RangeAttackError(f"unknown fill evidence: {evidence_type}")

        state.update({
            "simulated_accounting_quantity": LOT,
            "simulated_fill_price": exposed_x,
            "simulated_fill_ts": float(timestamp),
            "simulated_fill_receipt": evidence_receipt,
            "simulated_fill_evidence_type": evidence_type,
            "simulated_fill_external_ask_cents": external_ask_cents,
            "simulated_fill_order_interval_id": interval["order_interval_id"],
            "simulated_fill_book_receipt": (
                evidence_receipt
                if evidence_type == "STRICT_ASK_CERTAIN_FILL"
                else state.get("current_book_receipt")
            ),
        })
        interval["closed_ts"] = float(timestamp)
        interval["close_reason"] = close_reason
        if evidence_type == "STRICT_ASK_CERTAIN_FILL":
            interval.update({
                "accounting_fill_evidence_type": evidence_type,
                "accounting_fill_receipt": evidence_receipt,
                "accounting_fill_price_cents": exposed_x,
                "accounting_fill_quantity": LOT,
            })
        common_action_fields = {
            "order_interval_id": interval["order_interval_id"],
            "limit_price_cents": exposed_x,
            "simulated_accounting_quantity": LOT,
            "cumulative_five_required": False,
            "queue_clearance_required": False,
            "displayed_depth_required": False,
            **evidence_fields,
            "causal_state": self._decision_state(state, timestamp),
        }
        if evidence_type == "STRICT_ASK_CERTAIN_FILL":
            common_action_fields.update({
                "simulated_fill_price_cents": exposed_x,
                "evidence_type": evidence_type,
            })
        self._action(
            state,
            timestamp,
            action,
            reason,
            authority=str(order["authority"]),
            **common_action_fields,
        )
        state["active_order"] = None

        bids, _ = self._lawful_bbo(state)
        if self.first_filled_leg is None and bids:
            d1 = float(exposed_x) - float(bids[0][0])
            self.first_filled_leg = state["leg_id"]
            self.first_fill_ts = float(timestamp)
            self.first_fill_d1 = d1
            sibling = next(other for other in self.states if other is not state)
            sibling["headroom_armed"] = True
            sibling["headroom_d1_cents"] = d1
            sibling["headroom_b2_max_cents"] = headroom_b2_max(
                d1, float(self.policy["fee_cents"])
            )
            reference = {
                "first_filled_leg": state["leg_id"],
                "first_fill_ts": float(timestamp),
                "first_leg_limit_price_cents": exposed_x,
                "R1_external_bid_cents": int(bids[0][0]),
                "R1_book_receipt": state.get("current_book_receipt"),
                "d1_cents": d1,
                "fee_cents": float(self.policy["fee_cents"]),
            }
            if evidence_type == "STRICT_ASK_CERTAIN_FILL":
                reference.update({
                    "first_fill_evidence_type": evidence_type,
                    "first_fill_evidence_receipt": evidence_receipt,
                    "first_fill_order_interval_id": interval[
                        "order_interval_id"
                    ],
                })
            sibling["headroom_first_fill_reference"] = reference
            self._action(
                sibling,
                timestamp,
                "headroom_armed",
                arm_reason,
                authority="CAUSAL_PAIR_HEADROOM",
                **sibling["headroom_first_fill_reference"],
                b2_max_cents=sibling["headroom_b2_max_cents"],
                sibling_action_same_timestamp=False,
            )
        return True

    def _first_price_reach(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        self._credit_fillable_at_x(
            state,
            timestamp=float(row["ts"]),
            evidence_type="PRICE_REACHED",
            evidence_receipt=_source_receipt(row),
            print_row=row,
        )

    def _on_book(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
        deferred = state.get("deferred_equal_ask_maker_safety")
        if deferred is not None and timestamp > float(deferred["ts"]):
            self._flush_deferred_equal_ask_maker_safety(
                state, effective_ts=timestamp
            )
        receipt = _source_receipt(row)
        if not receipt or receipt in state["seen_book_receipts"]:
            return
        state["seen_book_receipts"].add(receipt)
        book = dict(row)
        book["bids"] = [list(value) for value in row.get("bids") or []]
        book["asks"] = [list(value) for value in row.get("asks") or []]
        state["current_book"] = book
        state["current_book_receipt"] = receipt
        state["current_last_trade"] = row.get("last_trade_cents")
        state["current_last_trade_provenance"] = row.get(
            "last_trade_provenance"
        )
        state["current_last_trade_observed_at"] = row.get(
            "last_trade_observed_at"
        )
        state["current_last_trade_execution_at"] = row.get(
            "last_trade_execution_at"
        )
        prior_depth = state.get("depth_within_three")
        depth = _top5_depth_within_three(book)
        state["prior_depth_within_three"] = prior_depth
        state["depth_within_three"] = depth
        state["depth_trend"] = (
            float(depth) - float(prior_depth)
            if depth is not None and prior_depth is not None
            else 0.0 if depth is not None else None
        )

        # The active order's pre-update exposed X is authoritative.  Credit it
        # before any same-timestamp macro, maker-safety, or LIVE-AIM movement.
        order = state.get("active_order")
        _, asks = self._lawful_bbo(state)
        credited = bool(
            order is not None
            and asks
            and int(asks[0][0]) < int(order["price"])
            and self._credit_fillable_at_x(
                state,
                timestamp=timestamp,
                evidence_type="STRICT_ASK_CERTAIN_FILL",
                evidence_receipt=receipt,
                external_ask_cents=int(asks[0][0]),
            )
        )
        if credited:
            state["deferred_equal_ask_maker_safety"] = None
        self._maybe_compose_pair(timestamp)
        self._apply_pending_macro(state, timestamp)
        if not credited:
            order = state.get("active_order")
            _, asks = self._lawful_bbo(state)
            if order is not None and asks and int(order["price"]) == int(
                asks[0][0]
            ):
                same_tick_asks = self.same_timestamp_book_asks.get(
                    (state["leg_id"], timestamp), ()
                )
                if any(
                    int(candidate_ask) < int(order["price"])
                    for candidate_ask in same_tick_asks
                ):
                    # All receipts at one exchange timestamp share the frozen
                    # evidence boundary.  Do not let an equal-ask receipt lower
                    # X before another receipt in that exact timestamp proves
                    # ask < X.
                    state["deferred_equal_ask_maker_safety"] = {
                        "ts": timestamp,
                        "interval_index": order["interval_index"],
                        "book_receipt": state.get("current_book_receipt"),
                    }
                else:
                    # With no same-timestamp strict evidence, preserve V1
                    # maker-safety semantics byte-for-byte.
                    self._place_or_reprice(
                        state,
                        timestamp,
                        int(asks[0][0]) - 1,
                        "maker_safety_external_ask_move",
                        authority="MAKER_SAFETY",
                        composed=False,
                        allow_upward=False,
                    )
        self._apply_liveaim(state, timestamp)

    def _on_print(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        deferred = state.get("deferred_equal_ask_maker_safety")
        timestamp = float(row["ts"])
        if deferred is not None and timestamp > float(deferred["ts"]):
            self._flush_deferred_equal_ask_maker_safety(
                state, effective_ts=timestamp
            )
        super()._on_print(state, row)

    def _terminalize(self, state: MutableMapping[str, Any]) -> None:
        self._flush_deferred_equal_ask_maker_safety(
            state, effective_ts=self.horizon
        )
        super()._terminalize(state)

    def run(self, event: Mapping[str, Any]) -> dict[str, Any]:
        self.same_timestamp_book_asks: dict[
            tuple[str, float], tuple[int, ...]
        ] = {}
        grouped: dict[tuple[str, float], list[int]] = {}
        for leg in event.get("legs") or []:
            leg_id = str(leg["leg_id"])
            for row in leg.get("observations") or []:
                asks = row.get("asks") or []
                if (
                    row.get("kind") == "book"
                    and asks
                    and float(asks[0][1]) > 0
                ):
                    grouped.setdefault(
                        (leg_id, float(row["ts"])), []
                    ).append(int(asks[0][0]))
        self.same_timestamp_book_asks = {
            key: tuple(values) for key, values in grouped.items()
            if len(values) > 1
        }
        result = super().run(event)
        result["schema_version"] = VERSION + "-candidate-event-stream-v1"
        result["instrument_version"] = VERSION
        result["causal_policy_fill_state_by_leg"] = {
            state["leg_id"]: {
                "simulated_accounting_quantity": state[
                    "simulated_accounting_quantity"
                ],
                "simulated_fill_price": state["simulated_fill_price"],
                "simulated_fill_ts": state["simulated_fill_ts"],
                "simulated_fill_receipt": state["simulated_fill_receipt"],
                "simulated_fill_evidence_type": state[
                    "simulated_fill_evidence_type"
                ],
                "simulated_fill_external_ask_cents": state[
                    "simulated_fill_external_ask_cents"
                ],
                "simulated_fill_order_interval_id": state[
                    "simulated_fill_order_interval_id"
                ],
                "simulated_fill_book_receipt": state[
                    "simulated_fill_book_receipt"
                ],
                "FILLABLE_AT_X_accounting_quantity": state[
                    "simulated_accounting_quantity"
                ],
                "guarded_Window1_status": None,
            }
            for state in self.states
        }
        result["accounting_fill_contract"] = {
            "PRICE_REACHED": "positive-size public print at or below X",
            "STRICT_ASK_CERTAIN_FILL": "lawful external ask strictly below X",
            "FILLABLE_AT_X": "PRICE_REACHED OR STRICT_ASK_CERTAIN_FILL",
            "ask_equal_X_auto_credit": False,
            "quantity_assigned_after_fillability": LOT,
            "cumulative_volume_gate": False,
            "displayed_depth_gate": False,
            "queue_clearance_gate": False,
        }
        result["order_stream_sha256"] = sha256_json(result["order_stream"])
        result["order_intervals_sha256"] = sha256_json(
            result["order_intervals_by_leg"]
        )
        return result


RangeAttackSimulator = RangeAttackSimulatorV2
RangeAttackInstrument = RangeAttackSimulatorV2
