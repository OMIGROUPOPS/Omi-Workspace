#!/usr/bin/env python3
"""Score-free Round-4 macro×micro composition overlay.

The overlay preserves the audited V2 fill and asynchronous headroom mechanics.
It adds only honest last-trade normalization, a role-free fitted-cell macro
read, and chronological book/print confirmation.  It has no scorer, network,
exchange, account, holdout, live, exit, settlement, DCA, or Window-2 surface.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping

import window1_round2_instrument as r2
import window1_round2_real_capability as r2cap
import window1_round3_prerun_builder as r3builder
import window1_round4_instrument_v2 as v2


VERSION = "window1-round4-macromicro-composition-v1"
CANDIDATE_SPEC_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_ROUND4_MACROMICRO_CANDIDATES_V1.json"
)
RECUT_PATH = ".claude/seqfloor_20260708/recut_cells.json"
CLIMB_SPEC_PATH = ".claude/rulings/CLIMBSIDE_SPEC.md"
GRANULARITY_PATH = ".claude/rulings/RULING_GRANULARITY_LAW.md"
EXPRESSION_PATH = ".claude/rulings/PLEX_EXPRESSION_INVARIANT.md"
VERIFIED_PRINT = "VERIFIED_PRINT_TIMESTAMP"
CARRIED_UNKNOWN = "CARRIED_EXECUTION_TIME_UNKNOWN"
LAST_TRADE_NO_CALL = "last_trade_unavailable_chain_evidence_continues"
TOP5_NO_CALL = "top5_unavailable_base_chain_policy_continues"
TOP20_NO_CALL = "top20_depth_unavailable_optional_steering_no_call"
InstrumentError = v2.InstrumentError


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    spec = r2.read_json(repo / CANDIDATE_SPEC_PATH)
    if spec.get("schema_version") != "window1-round4-macromicro-candidates-v1":
        raise InstrumentError("macro×micro candidate schema mismatch")
    if spec.get("instrument_version") != VERSION:
        raise InstrumentError("macro×micro instrument mismatch")
    expected = [
        "r4m_climb_decay__last_trade_chain__causal_headroom",
        "r4m_climb_decay__last_trade_chain_flow__causal_headroom",
    ]
    if list(spec.get("candidate_ids") or []) != expected:
        raise InstrumentError("macro×micro candidate order changed")
    if spec.get("free_numeric_parameters") != []:
        raise InstrumentError("free numeric surface is forbidden")
    return spec


def candidate_policy(
    spec: Mapping[str, Any],
    candidate_id: str,
    *,
    ablations: Iterable[str] = (),
) -> dict[str, Any]:
    if list(ablations):
        raise InstrumentError("post-freeze ablation is forbidden")
    candidates = list(map(str, spec.get("candidate_ids") or []))
    if candidate_id not in candidates:
        raise InstrumentError(f"candidate not frozen: {candidate_id}")
    base_spec = v2.load_candidate_spec(Path(__file__).resolve().parents[2])
    base = v2.candidate_policy(
        base_spec,
        "r4_pair_presence__park_join__causal_headroom_ladder",
    )
    flow = candidate_id.endswith("_chain_flow__causal_headroom")
    return {
        **base,
        "candidate_id": candidate_id,
        "profile": (
            "r4m_last_trade_chain_flow"
            if flow else "r4m_last_trade_chain"
        ),
        "enabled_families": sorted(set(base["enabled_families"]) | {
            "category_cell_macro",
            "climb_decay_posture",
            "last_trade_chain_micro",
            "coherent_pair_read",
            *(
                {"actual_print_flow", "top5_pressure_when_bound"}
                if flow else set()
            ),
        }),
        "macromicro_flow_enabled": flow,
        "posture_by_role": {},
        "ablations": [],
    }


def _positive_price(value: Any) -> int | None:
    try:
        price = int(value)
    except (TypeError, ValueError):
        return None
    return price if 1 <= price <= 99 else None


def _positive_levels(rows: Any, *, descending: bool) -> list[list[float]]:
    output = []
    for raw in rows or []:
        if not isinstance(raw, (list, tuple)) or len(raw) < 2:
            continue
        price = _positive_price(raw[0])
        size = r2.positive_level_size(raw[1])
        if price is not None and size > 0:
            output.append([price, size])
    output.sort(key=lambda row: row[0], reverse=descending)
    return output[:5]


def _delta_map(
    prior: list[list[float]], current: list[list[float]],
) -> dict[str, list[dict[str, float]]]:
    before = {int(price): float(size) for price, size in prior}
    after = {int(price): float(size) for price, size in current}
    additions, removals, depletion, replenishment = [], [], [], []
    for price in sorted(set(before) | set(after)):
        old, new = before.get(price, 0.0), after.get(price, 0.0)
        row = {
            "price_cents": float(price),
            "prior_size": old,
            "current_size": new,
            "delta_size": new - old,
        }
        if old == 0 < new:
            additions.append(row)
        elif old > 0 == new:
            removals.append(row)
        elif new < old:
            depletion.append(row)
        elif new > old:
            replenishment.append(row)
    return {
        "additions": additions,
        "removals": removals,
        "depletion": depletion,
        "replenishment": replenishment,
    }


def _last_trade_position(
    last_trade: int | None, bid: int | None, ask: int | None,
) -> str:
    if last_trade is None:
        return "UNAVAILABLE"
    if bid is None or ask is None:
        return "NO_LAWFUL_BBO"
    if last_trade < bid:
        return "BELOW_BID"
    if last_trade == bid:
        return "AT_BID"
    if bid < last_trade < ask:
        return "INSIDE_SPREAD"
    if last_trade == ask:
        return "AT_ASK"
    return "ABOVE_ASK"


def preserve_last_trade(
    normalized_event: MutableMapping[str, Any],
    cache: Mapping[str, Any],
) -> dict[str, Any]:
    """Attach honest last-trade and chain state without creating prints."""
    cache_by_ticker = {
        str(leg["ticker"]): leg for leg in cache.get("legs") or []
    }
    census = {
        "raw_snapshot_count": 0,
        "raw_positive_last_trade_count": 0,
        "normalized_book_count": 0,
        "normalized_positive_last_trade_count": 0,
        "verified_print_timestamp_count": 0,
        "carried_execution_time_unknown_count": 0,
        "carried_before_first_window1_print_count": 0,
        "legs_with_carried_state_and_no_window1_print_count": 0,
        "last_trade_created_print_count": 0,
    }
    for leg in normalized_event["legs"]:
        ticker = str(leg["ticker"])
        cached = cache_by_ticker[ticker]
        snapshots = list(cached.get("snapshots") or [])
        census["raw_snapshot_count"] += len(snapshots)
        census["raw_positive_last_trade_count"] += sum(
            _positive_price(row.get("last_trade")) is not None
            for row in snapshots
        )
        snapshots_by_ts: dict[float, list[Mapping[str, Any]]] = {}
        for row in snapshots:
            snapshots_by_ts.setdefault(float(row["ts"]), []).append(row)
        prints = [
            row for row in cached.get("prints") or []
            if float(normalized_event["policy_left_ts"])
            <= float(row["ts"])
            < float(normalized_event["policy_decision_horizon_ts"])
            and r2.positive_public_print({
                **row,
                "receipt_id": row.get("trade_id"),
                "size_verified": True,
                "synthetic_transition": False,
                "source": "normalized_public_true_print",
            })[0]
        ]
        prints.sort(key=lambda row: (
            float(row["ts"]), str(row.get("trade_id") or "")
        ))
        first_print_ts = min(
            (float(row["ts"]) for row in prints), default=None
        )
        prior_bids: list[list[float]] = []
        prior_asks: list[list[float]] = []
        prior_last: int | None = None
        carried_on_leg = False
        print_pointer = -1
        for observation in leg["observations"]:
            if observation["kind"] != "book":
                continue
            census["normalized_book_count"] += 1
            timestamp = float(observation["ts"])
            matches = snapshots_by_ts.get(timestamp) or []
            raw = next(
                (
                    row for row in matches
                    if row.get("bids") == observation.get("bids")
                    and row.get("asks") == observation.get("asks")
                ),
                matches[-1] if matches else {},
            )
            last_trade = _positive_price(raw.get("last_trade"))
            while (
                print_pointer + 1 < len(prints)
                and float(prints[print_pointer + 1]["ts"]) <= timestamp
            ):
                print_pointer += 1
            latest_print = (
                prints[print_pointer] if print_pointer >= 0 else None
            )
            execution = (
                latest_print
                if (
                    last_trade is not None
                    and latest_print is not None
                    and int(latest_print["price"]) == last_trade
                )
                else None
            )
            provenance = (
                VERIFIED_PRINT if execution is not None else CARRIED_UNKNOWN
            ) if last_trade is not None else None
            execution_at = (
                float(execution["ts"]) if execution is not None else None
            )
            bids = _positive_levels(
                observation.get("bids"), descending=True
            )
            asks = _positive_levels(
                observation.get("asks"), descending=False
            )
            bid = int(bids[0][0]) if bids else None
            ask = int(asks[0][0]) if asks else None
            transitions = {
                "bid": _delta_map(prior_bids, bids),
                "ask": _delta_map(prior_asks, asks),
            }
            bid_size = sum(float(row[1]) for row in bids)
            ask_size = sum(float(row[1]) for row in asks)
            observation.update({
                "last_trade_cents": last_trade,
                "last_trade_observed_at": timestamp,
                "last_trade_execution_at": execution_at,
                "last_trade_provenance": provenance,
                "last_trade_source_receipt": (
                    str(execution.get("trade_id"))
                    if execution is not None
                    else (
                        f"{ticker}|carried-last-trade|{timestamp:.6f}"
                        if last_trade is not None else None
                    )
                ),
                "last_trade_is_fill_volume": False,
                "chain_state": {
                    "nonself_best_bid_cents": bid,
                    "nonself_best_ask_cents": ask,
                    "spread_cents": (
                        ask - bid if bid is not None and ask is not None
                        else None
                    ),
                    "top5_bids": bids,
                    "top5_asks": asks,
                    "top5_bid_size": bid_size,
                    "top5_ask_size": ask_size,
                    "top5_pressure_sign": (
                        "BID" if bid_size > ask_size
                        else "ASK" if ask_size > bid_size else "BALANCED"
                    ),
                    "last_trade_position": _last_trade_position(
                        last_trade, bid, ask
                    ),
                    "last_trade_changed": last_trade != prior_last,
                    "transitions": transitions,
                    "receipt_timestamp": timestamp,
                },
            })
            if last_trade is not None:
                census["normalized_positive_last_trade_count"] += 1
                if provenance == VERIFIED_PRINT:
                    census["verified_print_timestamp_count"] += 1
                else:
                    carried_on_leg = True
                    census[
                        "carried_execution_time_unknown_count"
                    ] += 1
                    if first_print_ts is None or timestamp < first_print_ts:
                        census[
                            "carried_before_first_window1_print_count"
                        ] += 1
            prior_bids, prior_asks, prior_last = bids, asks, last_trade
        if carried_on_leg and not prints:
            census[
                "legs_with_carried_state_and_no_window1_print_count"
            ] += 1
    return census


def normalize_event(
    event: Mapping[str, Any],
    cache: Mapping[str, Any],
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    *,
    corridor_seconds: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    normalized = r2cap.normalize_event(
        event, cache, feature_map, corridor_seconds=corridor_seconds
    )
    census = preserve_last_trade(normalized, cache)
    # The receipt binds all three observables and provenance, unlike the
    # inherited receipt which intentionally predates last-trade preservation.
    for leg in normalized["legs"]:
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
                "last_trade_cents": row.get("last_trade_cents"),
                "last_trade_provenance": row.get(
                    "last_trade_provenance"
                ),
                "last_trade_execution_at": row.get(
                    "last_trade_execution_at"
                ),
            }
            row["source_receipt_identity"] = (
                f"{ticker}|book3|{float(row['ts']):.6f}|"
                f"{sha256_json(content)}"
            )
    return normalized, census


class Round4MacroMicroInstrument(v2.Round4InstrumentV2):
    """V2 fills/headroom plus fitted macro × chronological micro decisions."""

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        state = super()._new_state(event, leg)
        state.update({
            "macro_side": None,
            "macro_cell": None,
            "macro_edge_p50_cents": None,
            "macro_source_receipt": None,
            "pair_read_id": None,
            "pair_composed": False,
            "current_micro_receipt": None,
            "prior_micro_receipt": None,
            "last_positive_print_receipt": None,
            "last_positive_print_taker_side": None,
            "last_positive_print_ts": None,
            "last_trade_no_call_emitted": False,
            "top5_no_call_emitted": False,
            "top20_no_call_emitted": False,
            "micro_hold_count": 0,
        })
        return state

    def _initialize_birth(
        self, state: MutableMapping[str, Any], timestamp: float,
    ) -> None:
        super()._initialize_birth(state, timestamp)
        if state.get("birth_anchor") is None:
            return
        anchor = float(state["birth_anchor"])
        state["macro_side"] = (
            "CLIMB_SIDE" if anchor >= 50 else "DECAY_SIDE"
        )
        state["macro_cell"] = r2.nearest_int(anchor)
        cell = r2.recut_cell(
            self.surfaces, str(self.event["category"]), anchor
        )
        state["macro_edge_p50_cents"] = (
            float(cell["edge_p50"])
            if cell and cell.get("edge_p50") is not None
            else float(state.get("recut_depth") or 0)
        )
        state["macro_source_receipt"] = self.source_receipts.get("recut")
        r2._action(
            state,
            timestamp,
            "macromicro_macro_bind",
            "category_own_price_cell_edge_p50_role_free",
            category=str(self.event["category"]),
            own_price_cell=state["macro_cell"],
            macro_side=state["macro_side"],
            posture=self._posture(state),
            edge_p50_cents=state["macro_edge_p50_cents"],
            t_deep_minutes=state.get("recut_timing_minutes"),
            t_deep_is_advisory=True,
            fav_dog_or_causal_role_used=False,
            source_path=RECUT_PATH,
            source_sha256=state["macro_source_receipt"],
            order_changed=False,
        )

    def _posture(self, state: Mapping[str, Any]) -> str:
        return (
            "fitted_edge_park_hold"
            if state.get("macro_side") == "CLIMB_SIDE"
            else "fitted_edge_join_improve"
        )

    def _target_price(
        self,
        state: Mapping[str, Any],
        *,
        include_top5: bool = True,
    ) -> int:
        del include_top5
        book = state["current_book"]
        bids = r2.external_bids(book, self._subtract_own())
        asks = r2.asks(book)
        if not bids or not asks:
            raise InstrumentError("lawful external BBO required")
        bid, ask = int(bids[0][0]), int(asks[0][0])
        edge = r2.nearest_int(
            float(state.get("macro_edge_p50_cents") or 0)
        )
        fitted_target = bid - edge
        # Ratified non-self expression: fitted target rests at/below chain;
        # no midpoint and no last-trade price substitution.
        expressed = (
            fitted_target if fitted_target <= bid else bid + 1
        )
        expressed += int(state.get("sibling_bias_cents") or 0)
        return max(1, min(ask - 1, expressed))

    def _macro_receipt(self, state: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "category": str(self.event["category"]),
            "macro_side": state.get("macro_side"),
            "own_price_cell": state.get("macro_cell"),
            "edge_p50_cents": state.get("macro_edge_p50_cents"),
            "posture": self._posture(state),
            "source_path": RECUT_PATH,
            "source_sha256": state.get("macro_source_receipt"),
            "checkpoint_triggered_action": False,
        }

    def _micro_receipt(self, state: Mapping[str, Any]) -> dict[str, Any]:
        book = state.get("current_book") or {}
        chain = book.get("chain_state") or {}
        transitions = chain.get("transitions") or {}
        transition_counts = {
            f"{side}_{kind}_count": len(
                ((transitions.get(side) or {}).get(kind) or [])
            )
            for side in ("bid", "ask")
            for kind in (
                "additions", "removals", "depletion", "replenishment"
            )
        }
        return {
            "book_receipt": book.get("source_receipt_identity"),
            "book_ts": book.get("ts"),
            "nonself_best_bid_cents": chain.get(
                "nonself_best_bid_cents"
            ),
            "nonself_best_ask_cents": chain.get(
                "nonself_best_ask_cents"
            ),
            "spread_cents": chain.get("spread_cents"),
            "last_trade_cents": book.get("last_trade_cents"),
            "last_trade_observed_at": book.get(
                "last_trade_observed_at"
            ),
            "last_trade_execution_at": book.get(
                "last_trade_execution_at"
            ),
            "last_trade_provenance": book.get(
                "last_trade_provenance"
            ),
            "last_trade_position": chain.get("last_trade_position"),
            "last_trade_is_bbo_authority": False,
            "last_trade_is_fill_volume": False,
            "chain_transition_sha256": sha256_json(transitions),
            "chain_transition_counts": transition_counts,
            "top5_pressure_sign": chain.get("top5_pressure_sign"),
            "last_positive_print_receipt": state.get(
                "last_positive_print_receipt"
            ),
            "last_positive_print_ts": state.get(
                "last_positive_print_ts"
            ),
            "last_positive_print_taker_side": state.get(
                "last_positive_print_taker_side"
            ),
        }

    def _pair_receipt(self, state: Mapping[str, Any]) -> dict[str, Any]:
        siblings = [
            {
                "leg_id": row.get("leg_id"),
                "macro_side": row.get("macro_side"),
                "macro_cell": row.get("macro_cell"),
                "birth_anchor": row.get("birth_anchor"),
            }
            for row in self.states
        ]
        return {
            "pair_read_id": state.get("pair_read_id"),
            "coherent_initial_pair_read": state.get("pair_composed"),
            "legs": siblings,
            "headroom_active": state.get("headroom_active"),
            "realized_d1_cents": state.get("headroom_b1_cents"),
            "frozen_fee_cents": state.get("headroom_fee_cents"),
            "b2_max_cents": state.get("headroom_b2_max_cents"),
            "strict_joint_budget": "d1+d2+fee<0",
            "IC_gate": False,
            "S_gate": False,
        }

    def _annotate_decisions(
        self, state: MutableMapping[str, Any], start: int,
    ) -> None:
        for action in state["actions"][start:]:
            if action["action"] not in {"place", "reprice", "cancel"}:
                continue
            action["macro_decision_receipt"] = self._macro_receipt(state)
            action["micro_decision_receipt"] = self._micro_receipt(state)
            action["pair_decision_receipt"] = self._pair_receipt(state)
            action["composed_macro_micro"] = True

    def _place(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
        *,
        action_type: str = "place",
    ) -> None:
        start = len(state["actions"])
        super()._place(
            state, timestamp, reason, action_type=action_type
        )
        self._annotate_decisions(state, start)

    def _cancel(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
    ) -> None:
        start = len(state["actions"])
        super()._cancel(state, timestamp, reason)
        self._annotate_decisions(state, start)

    def _replace_at_price(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        price: int,
        *,
        reason: str,
    ) -> None:
        start = len(state["actions"])
        super()._replace_at_price(
            state, timestamp, price, reason=reason
        )
        self._annotate_decisions(state, start)

    def _compose_pair(self, timestamp: float) -> None:
        pair = [{
            "leg_id": state["leg_id"],
            "anchor_cents": state["birth_anchor"],
            "macro_side": state["macro_side"],
            "macro_cell": state["macro_cell"],
            "edge_p50_cents": state["macro_edge_p50_cents"],
            "book_receipt": (
                state.get("current_book") or {}
            ).get("source_receipt_identity"),
        } for state in self.states]
        pair_read_id = sha256_json({
            "event_id": self.event["event_id"],
            "timestamp": timestamp,
            "pair": pair,
        })
        for state in self.states:
            state["pair_read_id"] = pair_read_id
            state["pair_composed"] = True
            r2._action(
                state,
                timestamp,
                "pair_macro_micro_compose",
                "coherent_two_leg_initial_pair_read",
                pair_read_id=pair_read_id,
                pair=pair,
                independent_future_leg_clocks=True,
                static_symmetric_target=False,
                order_changed=False,
            )

    def _maybe_place(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
    ) -> None:
        if not all(row.get("birth_anchor") is not None for row in self.states):
            return
        if not all(row.get("pair_composed") for row in self.states):
            self._compose_pair(timestamp)
            for row in self.states:
                super()._maybe_place(
                    row, timestamp, "coherent_pair_first_lawful_bbo"
                )
            return
        # Presence is never suppressed by optional macro/micro evidence.
        super()._maybe_place(state, timestamp, reason)

    def _book_micro_allows_reprice(
        self, state: MutableMapping[str, Any],
    ) -> tuple[bool, str]:
        book = state.get("current_book") or {}
        chain = book.get("chain_state") or {}
        last_trade = book.get("last_trade_cents")
        bid = chain.get("nonself_best_bid_cents")
        if last_trade is None:
            if not state["last_trade_no_call_emitted"]:
                state["last_trade_no_call_emitted"] = True
                r2._action(
                    state,
                    float(book.get("ts") or self.left),
                    "feature_no_call",
                    LAST_TRADE_NO_CALL,
                    family_id="last_trade_relative_to_chain",
                    response_status="NO_CALL_UNAVAILABLE",
                    underlying_chain_policy_continues=True,
                )
            base = True
        elif state.get("macro_side") == "CLIMB_SIDE":
            base = float(last_trade) <= float(bid)
        else:
            base = float(last_trade) >= float(bid)
        if not self.policy.get("macromicro_flow_enabled"):
            return base, "last_trade_chain"
        bids = chain.get("top5_bids") or []
        asks = chain.get("top5_asks") or []
        if not bids or not asks:
            if not state["top5_no_call_emitted"]:
                state["top5_no_call_emitted"] = True
                r2._action(
                    state,
                    float(book.get("ts") or self.left),
                    "feature_no_call",
                    TOP5_NO_CALL,
                    family_id="top5_pressure_when_bound",
                    response_status="NO_CALL_UNAVAILABLE",
                    underlying_chain_policy_continues=True,
                )
            return base, "top5_no_call_base_chain"
        pressure = chain.get("top5_pressure_sign")
        pressure_confirms = (
            pressure in {"BID", "BALANCED"}
            if state.get("macro_side") == "CLIMB_SIDE"
            else pressure in {"ASK", "BALANCED"}
        )
        flow_side = state.get("last_positive_print_taker_side")
        flow_confirms = (
            True if flow_side is None
            else flow_side == (
                "no" if state.get("macro_side") == "CLIMB_SIDE"
                else "yes"
            )
        )
        return (
            base and pressure_confirms and flow_confirms,
            "last_trade_chain_top5_actual_flow",
        )

    def _on_book(
        self, state: MutableMapping[str, Any], row: Mapping[str, Any],
    ) -> None:
        prior_order = (
            int(state["active_order"]["price"])
            if state.get("active_order") is not None else None
        )
        prior_receipt = (
            state.get("current_book") or {}
        ).get("source_receipt_identity")
        super()._on_book(state, row)
        book = state.get("current_book") or {}
        if book.get("source_receipt_identity") != row.get(
            "source_receipt_identity"
        ):
            return
        state["prior_micro_receipt"] = prior_receipt
        state["current_micro_receipt"] = book.get(
            "source_receipt_identity"
        )
        if not state["top20_no_call_emitted"]:
            state["top20_no_call_emitted"] = True
            r2._action(
                state,
                float(row["ts"]),
                "feature_no_call",
                TOP20_NO_CALL,
                family_id="top20_depth",
                response_status="NO_CALL_UNAVAILABLE",
                underlying_top5_BBO_policy_continues=True,
            )
        order = state.get("active_order")
        if (
            prior_order is None
            or order is None
            or int(order["price"]) != prior_order
            or state["quantity"] >= r2.LOT
        ):
            return
        try:
            target = self._target_price(state)
        except InstrumentError:
            return
        if target == prior_order:
            return
        allowed, confirmation = self._book_micro_allows_reprice(state)
        r2._action(
            state,
            float(row["ts"]),
            "macromicro_transition",
            (
                "chronological_micro_confirms_fitted_macro_transition"
                if allowed else "chronological_micro_withholds_order_change"
            ),
            confirmation=confirmation,
            macro_target_cents=target,
            active_order_cents=prior_order,
            action_authority="strictly_chronological_book_receipt",
            action_taken=allowed,
            macro_receipt=self._macro_receipt(state),
            micro_receipt=self._micro_receipt(state),
            pair_receipt=self._pair_receipt(state),
        )
        if allowed:
            self._reprice(
                state,
                float(row["ts"]),
                "macromicro_fitted_cell_chain_transition",
            )
        else:
            state["micro_hold_count"] += 1

    def _on_print(
        self, state: MutableMapping[str, Any], row: Mapping[str, Any],
    ) -> None:
        valid, _ = r2.positive_public_print(row)
        nonself = row.get("own_order_fingerprint") is not True
        if valid and nonself:
            state["last_positive_print_receipt"] = str(
                row.get("trade_id") or row.get("receipt_id")
            )
            state["last_positive_print_taker_side"] = str(
                row.get("taker_side") or ""
            )
            state["last_positive_print_ts"] = float(row["ts"])
        prior_order = (
            int(state["active_order"]["price"])
            if state.get("active_order") is not None else None
        )
        super()._on_print(state, row)
        if (
            not valid
            or not nonself
            or not self.policy.get("macromicro_flow_enabled")
            or prior_order is None
            or state.get("active_order") is None
            or state["quantity"] >= r2.LOT
        ):
            return
        target = self._target_price(state)
        current = int(state["active_order"]["price"])
        if target == current:
            return
        allowed, confirmation = self._book_micro_allows_reprice(state)
        r2._action(
            state,
            float(row["ts"]),
            "macromicro_transition",
            (
                "positive_print_flow_confirms_fitted_macro_transition"
                if allowed else "positive_print_flow_withholds_order_change"
            ),
            confirmation=confirmation,
            macro_target_cents=target,
            active_order_cents=current,
            action_authority="receipt_identified_positive_size_public_print",
            action_taken=allowed,
            macro_receipt=self._macro_receipt(state),
            micro_receipt=self._micro_receipt(state),
            pair_receipt=self._pair_receipt(state),
        )
        if allowed:
            self._reprice(
                state,
                float(row["ts"]),
                "macromicro_actual_flow_transition",
            )

    def _result(
        self,
        event: Mapping[str, Any],
        states: Iterable[Mapping[str, Any]],
        event_terminal: str,
    ) -> dict[str, Any]:
        state_list = list(states)
        result = super()._result(event, state_list, event_terminal)
        result["schema_version"] = VERSION + "-order-stream-v1"
        result["instrument_version"] = VERSION
        result["macromicro_contract"] = {
            "macro_sets_target_and_posture": True,
            "micro_receipt_times_every_transition": True,
            "causal_role_or_fav_dog_selects_posture": False,
            "last_trade_preserved": True,
            "last_trade_is_BBO_authority": False,
            "last_trade_is_fill_volume": False,
            "carried_last_trade_is_new_execution": False,
            "constructed_midpoint_used": False,
            "initial_pair_read_is_coherent": True,
            "future_leg_clocks_are_independent": True,
            "metrics": None,
            "scored": False,
        }
        result["stream_sha256"] = r2.sha256_json(result["order_stream"])
        result["metrics"] = None
        result["scored"] = False
        return result


Round4Instrument = Round4MacroMicroInstrument
