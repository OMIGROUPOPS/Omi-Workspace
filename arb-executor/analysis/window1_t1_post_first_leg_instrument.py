#!/usr/bin/env python3
"""Score-free T1 post-first-leg response and persistence overlay.

The passed Range-Attack V2 simulator remains immutable.  This module changes
only the unfilled sibling after the first credited leg.  Every switch is
causally dormant before that fill, and all first-leg accounting continues to
come from the passed strict-ask/PRICE_REACHED implementation.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping

import window1_range_attack_instrument_v2 as passed


VERSION = "window1-t1-post-first-leg-response-persistence-v1"
EXACT_PARENT = "7fe299e50a9fc018378873e1277c7c891ce313c0"
CONTROLLING_AUDIT = "b96873c9a5eb340a7abb0eda9bffd6f0cedb4341"
SPEC_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_T1_POST_FIRST_LEG_CANDIDATES_V1.json"
)
LOT = passed.LOT

BASE_CANDIDATES = (
    "w1_range_attack__macro_hold__combined_headroom",
    "w1_range_attack__macro_micro__combined_headroom",
)
VARIANTS = (
    "response_only",
    "target_completeness_only",
    "persistence_only",
    "full_stack",
)
CANDIDATES = tuple(
    f"w1_t1__{regime}__{variant}"
    for regime in ("macro_hold", "macro_micro")
    for variant in VARIANTS
)
SWITCHES = {
    "response_only": {
        "receipt_keyed_response": True,
        "target_completeness": False,
        "lawful_persistence": False,
    },
    "target_completeness_only": {
        "receipt_keyed_response": False,
        "target_completeness": True,
        "lawful_persistence": False,
    },
    "persistence_only": {
        "receipt_keyed_response": False,
        "target_completeness": False,
        "lawful_persistence": True,
    },
    "full_stack": {
        "receipt_keyed_response": True,
        "target_completeness": True,
        "lawful_persistence": True,
    },
}
_EVENT_FLOW_CACHE: dict[tuple[Any, ...], dict[str, Any]] = {}
_EVENT_PRINT_WINDOW_CACHE: dict[tuple[Any, ...], dict[str, Any]] = {}
_EVENT_DIVOT_CACHE: dict[tuple[Any, ...], dict[str, Any]] = {}


class T1Error(RuntimeError):
    """A T1 causal or freeze contract was violated."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _variant(candidate_id: str) -> str:
    for value in VARIANTS:
        if candidate_id.endswith("__" + value):
            return value
    raise T1Error(f"unknown T1 candidate: {candidate_id}")


def _regime(candidate_id: str) -> str:
    if "__macro_hold__" in candidate_id:
        return "macro_hold"
    if "__macro_micro__" in candidate_id:
        return "macro_micro"
    raise T1Error(f"unknown T1 regime: {candidate_id}")


def base_candidate_id(candidate_id: str) -> str:
    regime = _regime(candidate_id)
    return BASE_CANDIDATES[0 if regime == "macro_hold" else 1]


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    spec = read_json(repo / SPEC_PATH)
    if spec.get("instrument_version") != VERSION:
        raise T1Error("T1 instrument version mismatch")
    if spec.get("exact_parent") != EXACT_PARENT:
        raise T1Error("T1 parent binding mismatch")
    if spec.get("controlling_audit") != CONTROLLING_AUDIT:
        raise T1Error("T1 audit binding mismatch")
    if tuple(spec.get("candidate_ids") or ()) != CANDIDATES:
        raise T1Error("T1 candidate order or membership changed")
    if tuple(spec.get("baseline_candidate_ids") or ()) != BASE_CANDIDATES:
        raise T1Error("baseline candidate binding changed")
    if spec.get("free_numeric_parameters") != []:
        raise T1Error("free T1 parameters are forbidden")
    if spec.get("metrics") is not None or spec.get("scored") is not False:
        raise T1Error("performance entered T1 candidate specification")
    for candidate in CANDIDATES:
        expected = SWITCHES[_variant(candidate)]
        actual = (spec.get("switch_matrix") or {}).get(candidate)
        if actual != expected:
            raise T1Error(f"switch matrix changed for {candidate}")
    return spec


def candidate_policy(
    repo: Path,
    spec: Mapping[str, Any],
    candidate_id: str,
    *,
    ablations: Iterable[str] = (),
) -> dict[str, Any]:
    if list(ablations):
        raise T1Error("post-freeze ablations are forbidden")
    if candidate_id not in CANDIDATES:
        raise T1Error(f"candidate not frozen: {candidate_id}")
    baseline_spec = passed.load_candidate_spec(repo)
    baseline_id = base_candidate_id(candidate_id)
    policy = passed.candidate_policy(baseline_spec, baseline_id)
    policy.update({
        "candidate_id": candidate_id,
        "base_candidate_id": baseline_id,
        "t1_variant": _variant(candidate_id),
        "t1_switches": dict(SWITCHES[_variant(candidate_id)]),
        "metrics": None,
        "scored": False,
    })
    return policy


def exact_cent(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise T1Error(f"{field}: bool is not an exact cent")
    if isinstance(value, int):
        result = value
    elif (
        isinstance(value, float)
        and math.isfinite(value)
        and value.is_integer()
    ):
        result = int(value)
    else:
        raise T1Error(f"{field}: non-integer cent")
    if not 1 <= result <= 99:
        raise T1Error(f"{field}: outside 1..99")
    return result


def construct_headroom_target(
    *,
    bid: Any,
    ask: Any,
    d1: Any,
    b2_max: Any,
    fee: Any,
    existing_raw_target: Any | None,
) -> dict[str, Any]:
    """Construct the exact frozen target and retain rejected alternatives."""
    bid_i = exact_cent(bid, "bid")
    ask_i = exact_cent(ask, "ask")
    if bid_i >= ask_i:
        raise T1Error("crossed external BBO")
    d1_i = int(d1)
    b2_max_i = int(b2_max)
    fee_i = int(fee)
    if float(d1_i) != float(d1) or float(b2_max_i) != float(b2_max):
        raise T1Error("headroom arithmetic is not integer-cent exact")

    headroom = min(ask_i - 1, bid_i + min(1, b2_max_i))
    alternatives: list[dict[str, Any]] = []

    def evaluate(label: str, price: int) -> dict[str, Any]:
        d2 = int(price) - bid_i
        checks = {
            "positive_lawful_cent": 1 <= int(price) <= 99,
            "maker_safe": int(price) < ask_i,
            "inside_b2_max": d2 <= b2_max_i,
            "strict_combined_negative": d1_i + d2 + fee_i < 0,
            "at_most_one_cent_improvement": int(price) <= bid_i + 1,
        }
        return {
            "alternative": label,
            "price_cents": int(price),
            "d2_cents": d2,
            "checks": checks,
            "lawful": all(checks.values()),
        }

    alternatives.append(evaluate("X_headroom", int(headroom)))
    if existing_raw_target is not None:
        raw = exact_cent(existing_raw_target, "existing_raw_target")
        expressed = raw if raw <= bid_i else bid_i + 1
        expressed = max(1, min(99, ask_i - 1, expressed))
        alternatives.append(evaluate("existing_macro_target", expressed))
    lawful = [row for row in alternatives if row["lawful"]]
    selected = max((row["price_cents"] for row in lawful), default=None)
    return {
        "formula": "min(ask-1,bid+min(1,b2_max))",
        "bid_cents": bid_i,
        "ask_cents": ask_i,
        "d1_cents": d1_i,
        "fee_cents": fee_i,
        "b2_max_cents": b2_max_i,
        "X_headroom_cents": int(headroom),
        "alternatives": alternatives,
        "selected_X_cents": selected,
        "selected_d2_cents": (
            None if selected is None else int(selected) - bid_i
        ),
        "strict_combined_negative": (
            False if selected is None
            else d1_i + int(selected) - bid_i + fee_i < 0
        ),
    }


def clear_event_flow_cache() -> None:
    """Drop the causal read cache between development events."""
    _EVENT_FLOW_CACHE.clear()
    _EVENT_PRINT_WINDOW_CACHE.clear()
    _EVENT_DIVOT_CACHE.clear()


class T1Simulator(passed.RangeAttackSimulatorV2):
    """Passed simulator plus independently switchable post-fill mechanisms."""

    def __init__(
        self,
        policy: Mapping[str, Any],
        *,
        boundary: Mapping[str, Any],
        **kwargs: Any,
    ) -> None:
        super().__init__(policy, **kwargs)
        self.boundary = dict(boundary)
        self.base_horizon = 0.0
        self.post_fill_right: float | None = (
            float(boundary["guarded_cutoff_ts"])
            if boundary.get("positive_window1_provable")
            and boundary.get("guarded_cutoff_ts") is not None
            else None
        )
        self.switches = dict(policy["t1_switches"])
        self._target_intercept_active = False

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        state = super()._new_state(event, leg)
        state.update({
            "t1_episode_receipts_seen": set(),
            "t1_episode_decisions": [],
            "t1_target_construction_receipts": [],
            "t1_persistence_receipts": [],
            "t1_base_horizon_extension_receipt": None,
            "t1_divot_price_counts": [0] * 100,
            "t1_divot_price_count_total": 0,
        })
        return state

    def _flow_state(
        self,
        state: Mapping[str, Any],
        timestamp: float,
    ) -> dict[str, Any]:
        """Reuse identical public-flow reads across the eight T1 variants.

        T1 never changes books or prints.  The cache key binds the complete
        causal observation state, so it is only a mechanical elimination of
        eight duplicate calculations, not a new evidence source.
        """
        prints = state["prints"]
        key = (
            state["event_id"],
            state["leg_id"],
            float(timestamp),
            state.get("current_book_receipt"),
            len(prints),
            prints[-1]["receipt"] if prints else None,
            state.get("depth_within_three"),
            state.get("depth_trend"),
        )
        cached = _EVENT_FLOW_CACHE.get(key)
        if cached is None:
            timestamps = [float(row["ts"]) for row in prints]
            start = bisect.bisect_left(
                timestamps,
                float(timestamp) - passed.v1.FLOW_WINDOW_SECONDS,
            )
            window_key = (
                state["event_id"],
                state["leg_id"],
                len(prints),
                start,
                prints[-1]["receipt"] if prints else None,
            )
            aggregate = _EVENT_PRINT_WINDOW_CACHE.get(window_key)
            if aggregate is None:
                rows = prints[start:]
                prices = [float(row["price"]) for row in rows]
                aggregate = {
                    "unique_positive_print_count_30m": len(rows),
                    "executed_share_volume_30m": float(sum(
                        float(row["size"]) for row in rows
                    )),
                    "inter_print_cadence_seconds":
                        passed.v1.median_cadence(rows),
                    "verified_print_trailing_signature":
                        passed.v1.print_signature(prices),
                    "first_print_receipt": (
                        rows[0]["receipt"] if rows else None
                    ),
                    "last_print_receipt": (
                        rows[-1]["receipt"] if rows else None
                    ),
                    "print_receipts_sha256": passed.sha256_json([
                        row["receipt"] for row in rows
                    ]),
                }
                _EVENT_PRINT_WINDOW_CACHE[window_key] = aggregate
            book = state.get("current_book") or {}
            bids = passed.mechanical.external_bids(book, True)
            asks = passed.mechanical.asks(book)
            spread = (
                int(asks[0][0]) - int(bids[0][0])
                if bids and asks else None
            )
            mapping = passed.v1.liveaim_mapping(
                category=str(state["category"]),
                print_count=int(
                    aggregate["unique_positive_print_count_30m"]
                ),
                signature=str(
                    aggregate["verified_print_trailing_signature"]
                ),
                depth_trend=state.get("depth_trend"),
                spread_cents=spread,
            )
            cached = {
                "timestamp": float(timestamp),
                **aggregate,
                "spread_cents": spread,
                "bid_depth_within_three_cents": state.get(
                    "depth_within_three"
                ),
                "depth_trend": state.get("depth_trend"),
                **mapping,
            }
            _EVENT_FLOW_CACHE[key] = cached
        return cached

    def _detect_divot(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        """Run the passed divot law with an exact bounded-cent median."""
        definition = self.policy["divot"]
        timestamp = float(row["ts"])
        window = state["divot_window"]
        counts = state["t1_divot_price_counts"]
        while window and float(window[0]["ts"]) < (
            timestamp - float(definition["trailing_median_seconds"])
        ):
            expired = window.popleft()
            counts[int(expired["price"])] -= 1
            state["t1_divot_price_count_total"] -= 1
        if state["t1_divot_price_count_total"] != len(window):
            raise T1Error("divot price-count window lost conservation")
        receipt = passed._source_receipt(row)
        key = (
            state["event_id"], state["leg_id"], receipt,
            len(window),
            window[0]["receipt"] if window else None,
            window[-1]["receipt"] if window else None,
            state.get("current_book_receipt"),
        )
        try:
            evidence = _EVENT_DIVOT_CACHE.get(key)
            if evidence is None:
                evidence = {"qualifies": False}
                if (
                    str(row.get("taker_side")) == "no"
                    and len(window) >= int(
                        definition["minimum_prior_positive_prints"]
                    )
                ):
                    total = int(state["t1_divot_price_count_total"])

                    def order_value(position: int) -> int:
                        running = 0
                        for cent in range(1, 100):
                            running += int(counts[cent])
                            if running > position:
                                return cent
                        raise T1Error("divot median rank unavailable")

                    if total % 2:
                        median = float(order_value(total // 2))
                    else:
                        median = (
                            order_value(total // 2 - 1)
                            + order_value(total // 2)
                        ) / 2.0
                    depth = median - float(row["price"])
                    _, asks = self._lawful_bbo(state)
                    ask_hold = bool(
                        asks
                        and float(asks[0][0]) >= (
                            median
                            - float(definition["ask_hold_within_cents"])
                        )
                    )
                    evidence = {
                        "qualifies": bool(
                            depth
                            >= float(definition["minimum_depth_cents"])
                            and ask_hold
                        ),
                        "median": median,
                        "depth": depth,
                        "ask": int(asks[0][0]) if asks else None,
                    }
                _EVENT_DIVOT_CACHE[key] = evidence
            if evidence["qualifies"]:
                state["divot_count"] += 1
                state["queue_preserved_hold_count"] += int(
                    state.get("active_order") is not None
                )
                self._action(
                    state,
                    timestamp,
                    "divot_hold",
                    "source_proven_positive_print_divot_holds_selected_target",
                    authority="DIVOT_SOURCE_MAPPING",
                    composition_selected_or_gated=True,
                    print_receipt=receipt,
                    print_price_cents=float(row["price"]),
                    trailing_median_cents=evidence["median"],
                    divot_depth_cents=evidence["depth"],
                    lawful_ask_cents=evidence["ask"],
                    queue_preserved=state.get("active_order") is not None,
                    displayed_size_gate=False,
                    causal_state=self._decision_state(state, timestamp),
                )
        finally:
            price = int(row["price"])
            counts[price] += 1
            state["t1_divot_price_count_total"] += 1

    def _is_unfilled_sibling(self, state: Mapping[str, Any]) -> bool:
        return bool(
            self.first_filled_leg is not None
            and state["leg_id"] != self.first_filled_leg
            and state["simulated_accounting_quantity"] != LOT
        )

    def _inside_t1_corridor(self, timestamp: float) -> bool:
        right = (
            self.post_fill_right
            if self.switches["lawful_persistence"]
            else self.base_horizon
        )
        return bool(
            self.boundary.get("positive_window1_provable")
            and right is not None
            and self.first_fill_ts is not None
            and float(timestamp) > float(self.first_fill_ts)
            and float(timestamp) <= float(right)
        )

    def _current_target_construction(
        self,
        state: Mapping[str, Any],
        *,
        existing_raw_target: Any | None,
    ) -> dict[str, Any] | None:
        bids, asks = self._lawful_bbo(state)
        if not bids or not asks:
            return None
        if int(bids[0][0]) >= int(asks[0][0]):
            return None
        return construct_headroom_target(
            bid=bids[0][0],
            ask=asks[0][0],
            d1=state["headroom_d1_cents"],
            b2_max=state["headroom_b2_max_cents"],
            fee=self.policy["fee_cents"],
            existing_raw_target=existing_raw_target,
        )

    def _record_target_construction(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        *,
        trigger_receipt: str,
        trigger_kind: str,
        proposed_raw_target: Any | None,
        construction: Mapping[str, Any] | None,
        application: str,
    ) -> None:
        row = {
            "event_id": state["event_id"],
            "candidate_id": state["candidate_id"],
            "base_candidate_id": self.policy["base_candidate_id"],
            "leg_id": state["leg_id"],
            "timestamp": float(timestamp),
            "trigger_receipt": trigger_receipt,
            "trigger_kind": trigger_kind,
            "first_fill_timestamp": self.first_fill_ts,
            "first_filled_leg": self.first_filled_leg,
            "proposed_existing_raw_target_cents": proposed_raw_target,
            "construction": dict(construction) if construction else None,
            "application": application,
            "metrics": None,
            "scored": False,
        }
        state["t1_target_construction_receipts"].append(row)

    def _active_order_law(
        self, state: Mapping[str, Any], timestamp: float,
    ) -> dict[str, Any]:
        order = state.get("active_order")
        bids, asks = self._lawful_bbo(state)
        if order is None:
            return {"lawful": False, "reason": "NO_ACTIVE_ORDER"}
        if not bids or not asks:
            return {
                "lawful": False,
                "reason": "CONTEMPORANEOUS_EXTERNAL_BBO_UNAVAILABLE",
            }
        price = int(order["price"])
        bid = int(bids[0][0])
        ask = int(asks[0][0])
        d1 = int(state["headroom_d1_cents"])
        d2 = price - bid
        fee = int(self.policy["fee_cents"])
        maximum = int(state["headroom_b2_max_cents"])
        checks = {
            "inside_guarded_Window1": self._inside_t1_corridor(timestamp),
            "positive_lawful_cent": 1 <= price <= 99,
            "maker_safe": price < ask,
            "inside_b2_max": d2 <= maximum,
            "strict_combined_negative": d1 + d2 + fee < 0,
            "lawful_non_crossed_BBO": bid < ask,
        }
        return {
            "lawful": all(checks.values()),
            "reason": (
                "ACTIVE_X_REMAINS_LAWFUL"
                if all(checks.values()) else "ACTIVE_X_LAW_FAILED"
            ),
            "price_cents": price,
            "bid_cents": bid,
            "ask_cents": ask,
            "d1_cents": d1,
            "d2_cents": d2,
            "fee_cents": fee,
            "b2_max_cents": maximum,
            "checks": checks,
        }

    def _place_or_reprice(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        raw_target: int,
        reason: str,
        *,
        authority: str,
        composed: bool,
        allow_upward: bool,
    ) -> bool:
        if not self._is_unfilled_sibling(state) or not self._inside_t1_corridor(
            timestamp
        ):
            return super()._place_or_reprice(
                state, timestamp, raw_target, reason,
                authority=authority, composed=composed,
                allow_upward=allow_upward,
            )

        trigger_receipt = str(
            state.get("current_book_receipt") or "NO_BOOK_RECEIPT"
        )
        proposed = int(raw_target)
        construction = None
        if (
            self.switches["target_completeness"]
            and not self._target_intercept_active
            and (
                state.get("active_order") is None
                or authority == "CAUSAL_PAIR_HEADROOM"
            )
        ):
            construction = self._current_target_construction(
                state, existing_raw_target=proposed
            )
            selected = (
                construction.get("selected_X_cents")
                if construction is not None else None
            )
            self._record_target_construction(
                state, timestamp,
                trigger_receipt=trigger_receipt,
                trigger_kind="inherited_target_transition",
                proposed_raw_target=proposed,
                construction=construction,
                application=(
                    "SELECTED_COMPLETE_TARGET"
                    if selected is not None else "MARKET_EVIDENCE_NO_CALL"
                ),
            )
            if selected is None:
                self._no_call(
                    state, timestamp,
                    "T1_MARKET_EVIDENCE_NO_CALL",
                    "lawful_positive_size_external_BBO_or_target_unavailable",
                    authority="CAUSAL_PAIR_HEADROOM",
                )
                return False
            proposed = int(selected)

        if (
            self.switches["lawful_persistence"]
            and state.get("active_order") is not None
        ):
            law = self._active_order_law(state, timestamp)
            if law["lawful"]:
                interval = state["order_intervals"][
                    state["active_order"]["interval_index"]
                ]
                receipt = {
                    "event_id": state["event_id"],
                    "candidate_id": state["candidate_id"],
                    "leg_id": state["leg_id"],
                    "timestamp": float(timestamp),
                    "trigger_receipt": trigger_receipt,
                    "original_order_interval_id": interval[
                        "order_interval_id"
                    ],
                    "original_X_cents": int(
                        state["active_order"]["price"]
                    ),
                    "suppressed_authority": authority,
                    "suppressed_reason": reason,
                    "proposed_replacement_X_cents": proposed,
                    "law": law,
                    "decision": "HOLD",
                    "queue_position_surrendered": False,
                    "metrics": None,
                    "scored": False,
                }
                state["t1_persistence_receipts"].append(receipt)
                state["queue_preserved_hold_count"] += 1
                self._action(
                    state, timestamp,
                    "t1_persistence_hold",
                    "lawful_post_first_sibling_X_preserved",
                    authority="CAUSAL_PAIR_HEADROOM",
                    original_order_interval_id=interval[
                        "order_interval_id"
                    ],
                    price_cents=int(state["active_order"]["price"]),
                    suppressed_authority=authority,
                    suppressed_reason=reason,
                    proposed_replacement_X_cents=proposed,
                    queue_preserved=True,
                    combined_headroom_law=law,
                )
                return False
            state["t1_persistence_receipts"].append({
                "event_id": state["event_id"],
                "candidate_id": state["candidate_id"],
                "leg_id": state["leg_id"],
                "timestamp": float(timestamp),
                "trigger_receipt": trigger_receipt,
                "original_order_interval_id": state["order_intervals"][
                    state["active_order"]["interval_index"]
                ]["order_interval_id"],
                "original_X_cents": int(state["active_order"]["price"]),
                "suppressed_authority": None,
                "suppressed_reason": None,
                "proposed_replacement_X_cents": proposed,
                "law": law,
                "decision": "RECEIPT_BACKED_CHANGE_ALLOWED",
                "queue_position_surrendered": True,
                "metrics": None,
                "scored": False,
            })

        self._target_intercept_active = True
        try:
            return super()._place_or_reprice(
                state, timestamp, proposed, reason,
                authority=authority, composed=composed,
                allow_upward=allow_upward,
            )
        finally:
            self._target_intercept_active = False

    def _credit_fillable_at_x(self, *args: Any, **kwargs: Any) -> bool:
        had_first = self.first_filled_leg is not None
        credited = super()._credit_fillable_at_x(*args, **kwargs)
        if (
            credited
            and not had_first
            and self.first_filled_leg is not None
            and self.switches["lawful_persistence"]
            and self.post_fill_right is not None
            and self.post_fill_right > self.base_horizon
        ):
            self.horizon = float(self.post_fill_right)
            sibling = next(
                state for state in self.states
                if state["leg_id"] != self.first_filled_leg
            )
            receipt = {
                "event_id": sibling["event_id"],
                "candidate_id": sibling["candidate_id"],
                "leg_id": sibling["leg_id"],
                "first_fill_timestamp": self.first_fill_ts,
                "base_policy_horizon_ts": self.base_horizon,
                "guarded_window1_cutoff_ts": self.post_fill_right,
                "decision": "EXTEND_SIBLING_PERSISTENCE_TO_GUARDED_CUTOFF",
                "metrics": None,
                "scored": False,
            }
            sibling["t1_base_horizon_extension_receipt"] = receipt
            sibling["t1_persistence_receipts"].append(receipt)
        return credited

    def _episode_decision(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
        if (
            not self._is_unfilled_sibling(state)
            or not self._inside_t1_corridor(timestamp)
        ):
            return
        receipt = passed._source_receipt(row)
        if not receipt or receipt in state["t1_episode_receipts_seen"]:
            return
        state["t1_episode_receipts_seen"].add(receipt)
        response = self.switches["receipt_keyed_response"]
        completeness = self.switches["target_completeness"]
        if not response and not (
            completeness and state.get("active_order") is None
        ):
            return

        before = state.get("active_order")
        prior_price = int(before["price"]) if before is not None else None
        decision = "HOLD" if before is not None else "NO_CALL"
        selected = prior_price
        reason = "existing_lawful_sibling_exposure_retained"
        construction = None
        if before is None:
            raw = state.get("macro_target_raw")
            if completeness:
                construction = self._current_target_construction(
                    state, existing_raw_target=raw
                )
                self._record_target_construction(
                    state, timestamp,
                    trigger_receipt=receipt,
                    trigger_kind=str(row.get("kind")),
                    proposed_raw_target=raw,
                    construction=construction,
                    application="EPISODE_KEYED_TARGET_COMPLETENESS",
                )
                selected = (
                    construction.get("selected_X_cents")
                    if construction is not None else None
                )
            else:
                selected = None
                if raw is not None:
                    try:
                        macro = self._current_target_construction(
                            state, existing_raw_target=raw
                        )
                        if macro is not None:
                            lawful_macro = [
                                alt for alt in macro["alternatives"]
                                if alt["alternative"] == "existing_macro_target"
                                and alt["lawful"]
                            ]
                            selected = (
                                lawful_macro[0]["price_cents"]
                                if lawful_macro else None
                            )
                            construction = macro
                    except (T1Error, ValueError, TypeError):
                        selected = None
            if selected is not None:
                changed = self._place_or_reprice(
                    state, timestamp, int(selected),
                    "t1_episode_keyed_sibling_response",
                    authority="CAUSAL_PAIR_HEADROOM",
                    composed=False,
                    allow_upward=True,
                )
                after = state.get("active_order")
                if changed and after is not None:
                    decision = "PLACE"
                    selected = int(after["price"])
                    reason = "strictly_later_receipt_created_sibling_exposure"
                else:
                    decision = "NO_CALL"
                    reason = "lawful_target_not_expressed"
            else:
                bids, asks = self._lawful_bbo(state)
                reason = (
                    "market_evidence_unavailable_NO_CALL"
                    if not bids or not asks
                    else "lawful_existing_or_headroom_target_unavailable_NO_CALL"
                )
                self._no_call(
                    state, timestamp,
                    "T1_MARKET_EVIDENCE_NO_CALL",
                    reason,
                    authority="CAUSAL_PAIR_HEADROOM",
                )

        active = state.get("active_order")
        interval_id = (
            state["order_intervals"][active["interval_index"]][
                "order_interval_id"
            ] if active is not None else None
        )
        record = {
            "event_id": state["event_id"],
            "candidate_id": state["candidate_id"],
            "base_candidate_id": self.policy["base_candidate_id"],
            "leg_id": state["leg_id"],
            "timestamp": timestamp,
            "trigger_receipt": receipt,
            "trigger_kind": str(row.get("kind")),
            "first_filled_leg": self.first_filled_leg,
            "first_fill_timestamp": self.first_fill_ts,
            "strictly_later_than_first_fill": (
                self.first_fill_ts is not None
                and timestamp > float(self.first_fill_ts)
            ),
            "d1_cents": state["headroom_d1_cents"],
            "b2_max_cents": state["headroom_b2_max_cents"],
            "fee_cents": self.policy["fee_cents"],
            "prior_X_cents": prior_price,
            "selected_X_cents": selected,
            "active_order_interval_id": interval_id,
            "decision": decision,
            "reason": reason,
            "new_action_fill_eligible_on_trigger_receipt": False,
            "next_evidence_must_be_strictly_later": decision in {
                "PLACE", "REPRICE"
            },
            "target_construction": construction,
            "metrics": None,
            "scored": False,
        }
        state["t1_episode_decisions"].append(record)
        self._action(
            state, timestamp,
            "t1_episode_keyed_decision",
            reason,
            authority="CAUSAL_PAIR_HEADROOM",
            trigger_receipt=receipt,
            trigger_kind=str(row.get("kind")),
            t1_decision=decision,
            selected_X_cents=selected,
            active_order_interval_id=interval_id,
            strictly_later_than_first_fill=True,
            new_action_fill_eligible_on_trigger_receipt=False,
        )

    def _on_book(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        super()._on_book(state, row)
        self._episode_decision(state, row)

    def _on_print(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        super()._on_print(state, row)
        self._episode_decision(state, row)

    def _terminalize(self, state: MutableMapping[str, Any]) -> None:
        self._flush_deferred_equal_ask_maker_safety(
            state, effective_ts=self.horizon
        )
        if state["discovery_status"] == "ACCUMULATING":
            self._finalize_discovery(state, self.horizon)
        if state["discovery_status"] == "WAITING_FIRST_PRINT":
            state["discovery_status"] = "NO_CALL"
            state["macro_target_status"] = "NO_CALL"
            self._no_call(
                state, self.horizon,
                "MACRO_TARGET_NO_CALL",
                "no_lawful_true_print_for_native_discovery",
                authority="ATLAS_DISCOVERY_MACRO",
            )
        if state["active_order"] is not None:
            extended = bool(
                self.switches["lawful_persistence"]
                and self.first_filled_leg is not None
                and self.horizon > self.base_horizon
            )
            reason = (
                "guarded_window1_cutoff_after_first_fill"
                if extended else "declared_policy_horizon"
            )
            self._close_order(
                state, self.horizon,
                "GUARDED_WINDOW1_CUTOFF" if extended else "POLICY_HORIZON",
                authority="POLICY_HORIZON",
                action_reason=reason,
            )
        if not state["placed_any"]:
            self._no_call(
                state, self.horizon,
                "MARKET_EVIDENCE_NO_CALL",
                "no_lawful_external_BBO_pair_read",
                authority="INITIAL_PAIR_BBO",
            )
        terminal_reason = (
            "complete_score_free_policy_stream"
            if self.first_filled_leg is None
            else "complete_score_free_T1_policy_stream"
        )
        state["terminal"] = terminal_reason
        self._action(
            state, self.horizon,
            "terminal",
            terminal_reason,
            authority="POLICY_HORIZON",
            D_membership_continues=True,
            metrics=None,
            scored=False,
        )

    def run(self, event: Mapping[str, Any]) -> dict[str, Any]:
        self._validate_event(event)
        self.event = event
        self.left = float(event["policy_left_ts"])
        self.base_horizon = float(event["policy_decision_horizon_ts"])
        self.horizon = self.base_horizon
        self.states = [
            self._new_state(event, leg) for leg in event["legs"]
        ]
        self.same_timestamp_book_asks = {}
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
        for state in self.states:
            self._action(
                state, self.left,
                "leg_open",
                "range_attack_pair_leg_initialized",
                authority="INITIAL_PAIR_BBO",
                evaluation_start_inaccessible=True,
                metrics=None,
            )
        maximum_right = self.base_horizon
        if (
            self.switches["lawful_persistence"]
            and self.post_fill_right is not None
        ):
            maximum_right = max(maximum_right, self.post_fill_right)
        timeline = []
        for index, leg in enumerate(event["legs"]):
            for observation in leg.get("observations") or []:
                timestamp = float(observation["ts"])
                if self.left <= timestamp <= maximum_right:
                    priority = 0 if observation.get("kind") == "book" else 1
                    timeline.append(
                        (timestamp, priority, index, observation)
                    )
        timeline.sort(key=lambda value: (
            value[0], value[1], value[2], passed._source_receipt(value[3])
        ))
        for timestamp, _, leg_index, observation in timeline:
            if timestamp > self.base_horizon and (
                not self.switches["lawful_persistence"]
                or self.first_filled_leg is None
            ):
                break
            if timestamp > self.horizon:
                break
            self._finalize_due_discoveries(timestamp)
            state = self.states[leg_index]
            if observation.get("kind") == "book":
                self._on_book(state, observation)
            elif observation.get("kind") == "print":
                self._on_print(state, observation)
        self._finalize_due_discoveries(self.horizon)
        for state in self.states:
            self._terminalize(state)
        actions = sorted(
            [row for state in self.states for row in state["actions"]],
            key=lambda row: (
                float(row["ts"]), str(row["leg_id"]),
                str(row["action"]), str(row["reason"]),
            ),
        )
        if any(
            action.get("above_nonself_bid_plus_one")
            or action.get("marketable")
            or action.get("lawful_band") is False
            for action in actions
        ):
            raise T1Error("post-adjustment expression violation")
        if any(
            row["action"] == "t1_episode_keyed_decision"
            and not row["strictly_later_than_first_fill"]
            for row in actions
        ):
            raise T1Error("T1 action was not strictly post-first-fill")
        result = {
            "schema_version": VERSION + "-candidate-event-stream-v1",
            "instrument_version": VERSION,
            "candidate_id": self.policy["candidate_id"],
            "base_candidate_id": self.policy["base_candidate_id"],
            "t1_variant": self.policy["t1_variant"],
            "t1_switches": dict(self.switches),
            "event_id": str(event["event_id"]),
            "event_date": str(event["event_date"]),
            "category": str(event["category"]),
            "policy_clock": {
                "policy_anchor_ts": float(event["policy_anchor_ts"]),
                "policy_anchor_observed_at_ts": float(
                    event["policy_anchor_observed_at_ts"]
                ),
                "policy_anchor_source": str(event["policy_anchor_source"]),
                "policy_left_ts": self.left,
                "baseline_policy_decision_horizon_ts": self.base_horizon,
                "post_first_terminal_ts": self.horizon,
                "guarded_cutoff_source": (
                    self.boundary.get("boundary_law")
                    if self.switches["lawful_persistence"]
                    and self.first_filled_leg is not None else None
                ),
                "evaluation_start_inaccessible_before_first_fill": True,
            },
            "order_stream": actions,
            "order_intervals_by_leg": {
                state["leg_id"]: state["order_intervals"]
                for state in self.states
            },
            "causal_policy_fill_state_by_leg": {
                state["leg_id"]: {
                    "simulated_accounting_quantity": state[
                        "simulated_accounting_quantity"
                    ],
                    "simulated_fill_price": state["simulated_fill_price"],
                    "simulated_fill_ts": state["simulated_fill_ts"],
                    "simulated_fill_receipt": state[
                        "simulated_fill_receipt"
                    ],
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
            },
            "pair_state": {
                "pair_read_id": self.pair_read_id,
                "first_filled_leg": self.first_filled_leg,
                "first_fill_ts": self.first_fill_ts,
                "causal_d1_cents": self.first_fill_d1,
                "fee_cents": float(self.policy["fee_cents"]),
                "C": None,
                "PC": None,
                "S": None,
                "IC": None,
            },
            "t1_episode_decisions_by_leg": {
                state["leg_id"]: state["t1_episode_decisions"]
                for state in self.states
            },
            "t1_target_construction_receipts_by_leg": {
                state["leg_id"]: state[
                    "t1_target_construction_receipts"
                ] for state in self.states
            },
            "t1_persistence_receipts_by_leg": {
                state["leg_id"]: state["t1_persistence_receipts"]
                for state in self.states
            },
            "metrics": None,
            "performance": None,
            "scored": False,
        }
        result["order_stream_sha256"] = sha256_json(result["order_stream"])
        result["order_intervals_sha256"] = sha256_json(
            result["order_intervals_by_leg"]
        )
        return result


RangeAttackT1Instrument = T1Simulator
