#!/usr/bin/env python3
"""Causal, score-free Window-1 Range-Mastery Attack Simulator.

The simulator deliberately does not inherit the rejected macro/micro strategy
at parent 84959172.  It reuses only the already-audited public-stream
normalizer, then applies native Trendpath discovery/path semantics, the
source-recorded LIVE-AIM mapping, and the frozen strict pair-headroom law.

Policy decisions cannot see the V5 evaluation start.  Guarded Window-1
fillability is adjudicated later by the separate PRE-RUN builder.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import deque
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

import window1_round2_instrument as mechanical
import window1_round4_macromicro_instrument as passed_normalizer


VERSION = "window1-range-attack-simulator-v1"
CANDIDATE_SPEC_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_RANGE_ATTACK_CANDIDATES_V1.json"
)
ATLAS_PATH = ".claude/trendpath/ATLAS_V1.json"
GUIDEBOOK_PATH = ".claude/guidebook/GUIDEBOOK_V1.json"
RECUT_PATH = ".claude/seqfloor_20260708/recut_cells.json"
TAKER_REACH_PATH = ".claude/takerreach/LAW.json"
DIVOT_PATH = ".claude/entrysurface_20260717/divot_tables_v1.json"
DRIFT_PATH = ".claude/entrysurface_20260717/drift_surfaces_v1.json"
BAND_PATH = ".claude/entrysurface_20260717/band_map_v1.json"
LIBRARY_PATH = ".claude/trendpath/LIBRARY_V1.json"
ORIENT_PATH = ".claude/trendpath/ORIENT_V1.json"
LIVEAIM_PROOF_PATH = ".claude/proof_20260714/PROOF_LIVE_AIM.md"
LIVEAIM_CODE_PATH = "arb-executor/live_v4.py"
VOLUME_PATH = ".claude/volume_20260709/VOLUME_LEDGER.md"

DEVELOPMENT_DATES = {f"2026-07-{day:02d}" for day in range(12, 21)}
SEALED_HOLDOUT_DATES = {
    "2026-07-24", "2026-07-25", "2026-07-26"
}
LOT = 5
DISCOVERY_SECONDS = 3600.0
FLOW_WINDOW_SECONDS = 1800.0
FLOW_THRESHOLDS = {
    "ITF_M": 6,
    "ITF_W": 6,
    "ATP_CHALL": 16,
    "WTA_CHALL": 16,
    "ATP_MAIN": None,
    "WTA_MAIN": None,
}
AUTHORITIES = {
    "INITIAL_PAIR_BBO",
    "ATLAS_DISCOVERY_MACRO",
    "LIVEAIM_SOURCE_MAPPING",
    "DIVOT_SOURCE_MAPPING",
    "CAUSAL_PAIR_HEADROOM",
    "MAKER_SAFETY",
    "POLICY_HORIZON",
}
DECISION_ACTIONS = {"place", "reprice", "cancel"}
FORBIDDEN_POLICY_FIELDS = {
    "evaluation_real_start_ts",
    "verified_start_utc",
    "exact_start_utc",
    "proxy_clock_utc",
    "guarded_cutoff_ts",
    "window1_close",
    "window1_close_cents",
}

# The passed normalizer is the only reused component of the blocked V1 file.
# None of its target, direction, pressure, flow, or action-annotation methods
# are invoked or inherited.
normalize_event = passed_normalizer.normalize_event
preserve_last_trade = passed_normalizer.preserve_last_trade
VERIFIED_PRINT = passed_normalizer.VERIFIED_PRINT
CARRIED_UNKNOWN = passed_normalizer.CARRIED_UNKNOWN


class RangeAttackError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    spec = read_json(repo / CANDIDATE_SPEC_PATH)
    expected = [
        "w1_range_attack__macro_hold__combined_headroom",
        "w1_range_attack__macro_micro__combined_headroom",
    ]
    if spec.get("instrument_version") != VERSION:
        raise RangeAttackError("range-attack instrument version mismatch")
    if list(spec.get("candidate_ids") or []) != expected:
        raise RangeAttackError("range-attack candidate order changed")
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
    if list(ablations):
        raise RangeAttackError("post-freeze ablations are forbidden")
    candidates = list(map(str, spec.get("candidate_ids") or []))
    if candidate_id not in candidates:
        raise RangeAttackError(f"candidate not frozen: {candidate_id}")
    return {
        "candidate_id": candidate_id,
        "liveaim_enabled": "__macro_micro__" in candidate_id,
        "fee_cents": 0,
        "headroom_step_cents": 1,
        "divot": {
            "minimum_depth_cents": 2,
            "trailing_median_seconds": 1800,
            "minimum_prior_positive_prints": 3,
            "ask_hold_within_cents": 1,
        },
        "metrics": None,
        "scored": False,
    }


def path_price_bucket(price: float) -> str:
    if price <= 25:
        return "le25"
    if price <= 50:
        return "26_50"
    if price <= 75:
        return "51_75"
    return "ge75"


def atlas_native_side(price: float) -> str:
    return "leader" if price >= 50 else "underdog"


def rounded_cent(value: float) -> int:
    return int(math.floor(float(value) + 0.5))


def positive_print(row: Mapping[str, Any]) -> tuple[bool, str | None]:
    valid, reason = mechanical.positive_public_print(row)
    if not valid:
        return False, reason
    if row.get("own_order_fingerprint") is True:
        return False, "self_evidence_excluded"
    receipt = str(row.get("trade_id") or row.get("receipt_id") or "").strip()
    if not receipt:
        return False, "missing_trade_receipt"
    return True, None


def print_signature(prices: Sequence[float]) -> str:
    if len(prices) < 3:
        return "flat"
    median = sorted(float(value) for value in prices)[len(prices) // 2]
    if float(prices[-1]) > median:
        return "rising"
    if float(prices[-1]) < median:
        return "falling"
    return "flat"


def median_cadence(rows: Sequence[Mapping[str, Any]]) -> float | None:
    if len(rows) < 2:
        return None
    gaps = [
        float(rows[index]["ts"]) - float(rows[index - 1]["ts"])
        for index in range(1, len(rows))
    ]
    return float(statistics.median(gaps))


def flow_bucket(category: str, print_count: int) -> str:
    threshold = FLOW_THRESHOLDS.get(category)
    if threshold is None:
        return "na"
    ratio = float(print_count) / float(threshold)
    if ratio < 0.25:
        return "quiet"
    if ratio < 1.0:
        return "warm"
    return "open"


def liveaim_mapping(
    *,
    category: str,
    print_count: int,
    signature: str,
    depth_trend: float | None,
    spread_cents: int | None,
) -> dict[str, Any]:
    threshold = FLOW_THRESHOLDS.get(category)
    ratio = (
        float(print_count) / float(threshold)
        if threshold is not None else None
    )
    if threshold is None:
        verdict = "GAUGE_OFF_AIM_PRIOR"
    elif signature == "rising":
        verdict = "NO_BID_CHASE_GUARD"
    elif ratio >= 1.0 and (
        signature == "falling"
        or (depth_trend is not None and float(depth_trend) < 0)
    ):
        verdict = "AIM_DEEP"
    elif ratio < 0.25 and (spread_cents or 0) >= 4:
        verdict = "AIM_SHALLOW"
    else:
        verdict = "AIM_PRIOR"
    return {
        "verdict": verdict,
        "open_threshold": threshold,
        "flow_ratio": ratio,
        "flow_bucket": flow_bucket(category, print_count),
    }


def headroom_b2_max(d1: float, fee: float) -> int:
    return int(math.floor(-float(d1) - float(fee) - 1.0))


def strict_pair_budget(d1: float, d2: float, fee: float) -> bool:
    return float(d1) + float(d2) + float(fee) < 0.0


def _source_receipt(row: Mapping[str, Any]) -> str:
    return str(
        row.get("source_receipt_identity")
        or row.get("trade_id")
        or row.get("receipt_id")
        or ""
    )


def _top5_depth_within_three(
    book: Mapping[str, Any], *, subtract_own: bool = True,
) -> float | None:
    bids = mechanical.external_bids(book, subtract_own)
    if not bids:
        return None
    best = int(bids[0][0])
    return float(
        sum(size for price, size in bids if int(price) >= best - 3)
    )


class RangeAttackSimulator:
    """One pair-level causal state machine with independent leg orders."""

    def __init__(
        self,
        policy: Mapping[str, Any],
        *,
        atlas: Mapping[str, Any],
        guidebook: Mapping[str, Any],
        recut: Mapping[str, Any],
        taker_reach: Mapping[str, Any],
        source_hashes: Mapping[str, str],
    ) -> None:
        self.policy = dict(policy)
        self.atlas = dict(atlas)
        self.guidebook = dict(guidebook)
        self.recut = dict(recut)
        self.taker_reach = dict(taker_reach)
        self.source_hashes = dict(source_hashes)
        self.event: Mapping[str, Any] = {}
        self.left = 0.0
        self.horizon = 0.0
        self.states: list[MutableMapping[str, Any]] = []
        self.pair_read_id: str | None = None
        self.first_filled_leg: str | None = None
        self.first_fill_ts: float | None = None
        self.first_fill_d1: float | None = None

    def _validate_event(self, event: Mapping[str, Any]) -> None:
        date = str(event.get("event_date"))
        if date in SEALED_HOLDOUT_DATES:
            raise RangeAttackError("sealed holdout event refused")
        if date not in DEVELOPMENT_DATES:
            raise RangeAttackError("non-development event refused")
        if len(list(event.get("legs") or [])) != 2:
            raise RangeAttackError("pair law requires exactly two legs")
        leaked = sorted(FORBIDDEN_POLICY_FIELDS.intersection(event))
        if leaked:
            raise RangeAttackError(
                "evaluation oracle leaked into policy: " + ",".join(leaked)
            )
        required = {
            "policy_anchor_ts",
            "policy_anchor_observed_at_ts",
            "policy_anchor_source",
            "policy_left_ts",
            "policy_decision_horizon_ts",
        }
        missing = sorted(required - set(event))
        if missing:
            raise RangeAttackError(
                "policy clock field missing: " + ",".join(missing)
            )
        left = float(event["policy_left_ts"])
        anchor = float(event["policy_anchor_ts"])
        horizon = float(event["policy_decision_horizon_ts"])
        if not left < anchor <= horizon:
            raise RangeAttackError("invalid policy clock corridor")

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        return {
            "event_id": str(event["event_id"]),
            "candidate_id": str(self.policy["candidate_id"]),
            "category": str(event["category"]),
            "leg_id": str(leg["leg_id"]),
            "ticker": str(leg["ticker"]),
            "feature_availability": dict(
                leg.get("feature_availability") or {}
            ),
            "actions": [],
            "current_book": None,
            "current_book_receipt": None,
            "current_last_trade": None,
            "current_last_trade_provenance": None,
            "current_last_trade_observed_at": None,
            "current_last_trade_execution_at": None,
            "prior_depth_within_three": None,
            "depth_within_three": None,
            "depth_trend": None,
            "seen_book_receipts": set(),
            "seen_print_receipts": set(),
            "prints": [],
            "discovery_t0": None,
            "discovery_deadline": None,
            "discovery_prints": [],
            "discovery_status": "WAITING_FIRST_PRINT",
            "discovery_price": None,
            "discovery_page_key": None,
            "discovery_page": None,
            "macro_target_raw": None,
            "macro_target_status": "PENDING",
            "macro_target_source": None,
            "macro_pending_expression": False,
            "macro_target_selected_ts": None,
            "recut_native_row_observed_not_consumed": None,
            "active_order": None,
            "order_intervals": [],
            "next_order_interval": 1,
            "placed_any": False,
            "simulated_accounting_quantity": 0,
            "simulated_fill_price": None,
            "simulated_fill_ts": None,
            "simulated_fill_receipt": None,
            "headroom_armed": False,
            "headroom_d1_cents": None,
            "headroom_b2_max_cents": None,
            "headroom_first_fill_reference": None,
            "headroom_trigger_count": 0,
            "divot_window": deque(),
            "divot_prices_sorted": [],
            "divot_count": 0,
            "last_liveaim_fingerprint": None,
            "last_liveaim_state": None,
            "liveaim_deep_target": None,
            "target_change_count": 0,
            "queue_preserved_hold_count": 0,
            "queue_surrender_count": 0,
            "no_calls": [],
            "terminal": None,
        }

    def _action(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        action: str,
        reason: str,
        *,
        authority: str,
        composition_selected_or_gated: bool = False,
        **values: Any,
    ) -> dict[str, Any]:
        if authority not in AUTHORITIES:
            raise RangeAttackError(f"unknown authority: {authority}")
        row = {
            "event_id": state["event_id"],
            "candidate_id": state["candidate_id"],
            "leg_id": state["leg_id"],
            "ticker": state["ticker"],
            "ts": float(timestamp),
            "action": action,
            "reason": reason,
            "primary_authority": authority,
            "composed_macro_micro": bool(
                composition_selected_or_gated
            ),
            **values,
        }
        if state["actions"] and float(timestamp) < float(
            state["actions"][-1]["ts"]
        ):
            raise RangeAttackError("per-leg action clock moved backward")
        state["actions"].append(row)
        return row

    def _flow_state(
        self,
        state: Mapping[str, Any],
        timestamp: float,
    ) -> dict[str, Any]:
        rows = []
        lower = float(timestamp) - FLOW_WINDOW_SECONDS
        for row in reversed(state["prints"]):
            row_ts = float(row["ts"])
            if row_ts < lower:
                break
            if row_ts <= float(timestamp):
                rows.append(row)
        rows.reverse()
        prices = [float(row["price"]) for row in rows]
        book = state.get("current_book") or {}
        bids = mechanical.external_bids(book, True)
        asks = mechanical.asks(book)
        spread = (
            int(asks[0][0]) - int(bids[0][0])
            if bids and asks else None
        )
        mapping = liveaim_mapping(
            category=str(state["category"]),
            print_count=len(rows),
            signature=print_signature(prices),
            depth_trend=state.get("depth_trend"),
            spread_cents=spread,
        )
        return {
            "timestamp": float(timestamp),
            "unique_positive_print_count_30m": len(rows),
            "executed_share_volume_30m": float(
                sum(float(row["size"]) for row in rows)
            ),
            "inter_print_cadence_seconds": median_cadence(rows),
            "verified_print_trailing_signature": print_signature(prices),
            "spread_cents": spread,
            "bid_depth_within_three_cents": state.get(
                "depth_within_three"
            ),
            "depth_trend": state.get("depth_trend"),
            "first_print_receipt": (
                rows[0]["receipt"] if rows else None
            ),
            "last_print_receipt": (
                rows[-1]["receipt"] if rows else None
            ),
            "print_receipts_sha256": sha256_json([
                row["receipt"] for row in rows
            ]),
            **mapping,
        }

    def _decision_state(
        self,
        state: Mapping[str, Any],
        timestamp: float,
    ) -> dict[str, Any]:
        book = state.get("current_book") or {}
        bids = mechanical.external_bids(book, True)
        asks = mechanical.asks(book)
        sibling = next(
            other for other in self.states if other is not state
        )
        sibling_book = sibling.get("current_book") or {}
        sibling_bids = mechanical.external_bids(sibling_book, True)
        sibling_asks = mechanical.asks(sibling_book)
        return {
            "causal_timestamp": float(timestamp),
            "last_trade_cents": state.get("current_last_trade"),
            "last_trade_provenance": state.get(
                "current_last_trade_provenance"
            ),
            "last_trade_observed_at": state.get(
                "current_last_trade_observed_at"
            ),
            "last_trade_execution_at": state.get(
                "current_last_trade_execution_at"
            ),
            "nonself_best_bid_cents": int(bids[0][0]) if bids else None,
            "nonself_best_ask_cents": int(asks[0][0]) if asks else None,
            "top5_bids": [list(value) for value in bids[:5]],
            "top5_asks": [list(value) for value in asks[:5]],
            "book_receipt": state.get("current_book_receipt"),
            "flow": self._flow_state(state, timestamp),
            "macro": {
                "status": state.get("macro_target_status"),
                "target_raw_cents": state.get("macro_target_raw"),
                "target_source": state.get("macro_target_source"),
                "discovery_price_cents": state.get("discovery_price"),
                "page_key": state.get("discovery_page_key"),
            },
            "sibling": {
                "leg_id": sibling["leg_id"],
                "last_trade_cents": sibling.get("current_last_trade"),
                "nonself_best_bid_cents": (
                    int(sibling_bids[0][0]) if sibling_bids else None
                ),
                "nonself_best_ask_cents": (
                    int(sibling_asks[0][0]) if sibling_asks else None
                ),
                "flow": self._flow_state(sibling, timestamp),
                "simulated_filled": (
                    sibling["simulated_accounting_quantity"] == LOT
                ),
            },
        }

    def _lawful_bbo(
        self, state: Mapping[str, Any],
    ) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
        book = state.get("current_book") or {}
        return (
            mechanical.external_bids(book, True),
            mechanical.asks(book),
        )

    def _express(
        self,
        state: Mapping[str, Any],
        raw_target: int,
    ) -> tuple[int, dict[str, Any]]:
        bids, asks = self._lawful_bbo(state)
        if not bids or not asks:
            raise RangeAttackError("lawful external BBO required")
        bid, ask = int(bids[0][0]), int(asks[0][0])
        expression = (
            int(raw_target)
            if int(raw_target) <= bid else bid + 1
        )
        final = max(1, min(99, ask - 1, expression))
        if final >= ask:
            raise RangeAttackError("maker expression became marketable")
        return final, {
            "complete_raw_target_cents": int(raw_target),
            "nonself_bid_cents": bid,
            "lawful_ask_cents": ask,
            "expression_rule": (
                "REST_AT_RAW_TARGET"
                if int(raw_target) <= bid
                else "IMPROVE_EXACTLY_ONE"
            ),
            "final_expressed_price_cents": final,
            "post_adjustment_expression_applied": True,
            "above_nonself_bid_plus_one": final > bid + 1,
            "marketable": final >= ask,
            "lawful_band": 1 <= final <= 99,
        }

    def _queue_ahead(
        self, state: Mapping[str, Any], price: int,
    ) -> dict[str, Any]:
        bids, _ = self._lawful_bbo(state)
        exact = next(
            (float(size) for level, size in bids if int(level) == price),
            None,
        )
        top5_ahead = float(
            sum(size for level, size in bids if int(level) >= price)
        )
        complete = bool(bids) and (
            price >= int(bids[-1][0])
        )
        return {
            "observable_exact_level_size": exact,
            "observable_top5_depth_at_or_ahead": top5_ahead,
            "top5_covers_target_level": complete,
            "queue_is_primary_fill_gate": False,
        }

    def _open_interval(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        price: int,
        raw_target: int,
        reason: str,
        authority: str,
    ) -> dict[str, Any]:
        interval_id = (
            f"{state['candidate_id']}|{state['event_id']}|"
            f"{state['leg_id']}|{state['next_order_interval']:04d}"
        )
        state["next_order_interval"] += 1
        interval = {
            "order_interval_id": interval_id,
            "leg_id": state["leg_id"],
            "ticker": state["ticker"],
            "opened_ts": float(timestamp),
            "closed_ts": None,
            "close_reason": None,
            "limit_price_cents": int(price),
            "raw_target_cents": int(raw_target),
            "authority": authority,
            "open_reason": reason,
            "book_receipt": state.get("current_book_receipt"),
            "queue_diagnostic": self._queue_ahead(state, price),
            "metrics": None,
        }
        state["order_intervals"].append(interval)
        return interval

    def _close_order(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
        *,
        authority: str,
        action_reason: str | None = None,
    ) -> None:
        order = state.get("active_order")
        if order is None:
            return
        interval = state["order_intervals"][order["interval_index"]]
        interval["closed_ts"] = float(timestamp)
        interval["close_reason"] = reason
        if action_reason is not None:
            self._action(
                state,
                timestamp,
                "cancel",
                action_reason,
                authority=authority,
                queue_surrendered=True,
                price_cents=int(order["price"]),
                order_interval_id=interval["order_interval_id"],
                queue_ahead_surrendered=interval["queue_diagnostic"],
                causal_state=self._decision_state(state, timestamp),
            )
            state["queue_surrender_count"] += 1
        state["active_order"] = None

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
        if state["simulated_accounting_quantity"] == LOT:
            return False
        bids, asks = self._lawful_bbo(state)
        if not bids or not asks:
            self._no_call(
                state,
                timestamp,
                "MARKET_EVIDENCE_NO_CALL",
                "lawful_positive_size_external_BBO_unavailable",
                authority=authority,
            )
            return False
        price, expression = self._express(state, int(raw_target))
        prior = state.get("active_order")
        prior_price = int(prior["price"]) if prior is not None else None
        if prior_price == price:
            state["queue_preserved_hold_count"] += 1
            self._action(
                state,
                timestamp,
                "hold",
                reason + "_target_unchanged_queue_preserved",
                authority=authority,
                composition_selected_or_gated=composed,
                price_cents=price,
                queue_preserved=True,
                causal_state=self._decision_state(state, timestamp),
                **expression,
            )
            return False
        if (
            prior_price is not None
            and price > prior_price
            and not allow_upward
        ):
            state["queue_preserved_hold_count"] += 1
            self._action(
                state,
                timestamp,
                "hold",
                reason + "_upward_revision_forbidden",
                authority=authority,
                composition_selected_or_gated=composed,
                prior_price_cents=prior_price,
                proposed_price_cents=price,
                queue_preserved=True,
                causal_state=self._decision_state(state, timestamp),
                **expression,
            )
            return False
        action = "place" if prior is None else "reprice"
        if prior is not None:
            self._close_order(
                state,
                timestamp,
                reason + "_cancel_replace",
                authority=authority,
                action_reason=reason + "_cancel",
            )
        interval = self._open_interval(
            state, timestamp, price, raw_target, reason, authority
        )
        state["active_order"] = {
            "price": int(price),
            "raw_target": int(raw_target),
            "placed_ts": float(timestamp),
            "interval_index": len(state["order_intervals"]) - 1,
            "authority": authority,
        }
        state["placed_any"] = True
        if action == "reprice":
            state["target_change_count"] += 1
        self._action(
            state,
            timestamp,
            action,
            reason,
            authority=authority,
            composition_selected_or_gated=composed,
            price_cents=int(price),
            simulated_order_quantity=LOT,
            prior_price_cents=prior_price,
            reprice_direction=(
                None
                if prior_price is None
                else "UP" if price > prior_price else "DOWN"
            ),
            order_interval_id=interval["order_interval_id"],
            queue_diagnostic=interval["queue_diagnostic"],
            causal_state=self._decision_state(state, timestamp),
            **expression,
        )
        return True

    def _no_call(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
        detail: str,
        *,
        authority: str,
    ) -> None:
        key = f"{reason}|{detail}"
        if key in state["no_calls"]:
            return
        state["no_calls"].append(key)
        self._action(
            state,
            timestamp,
            "feature_no_call",
            reason,
            authority=authority,
            detail=detail,
            response_status="NO_CALL_UNAVAILABLE",
            D_membership_continues=True,
            underlying_pair_presence_continues=True,
            optional_feature_censors_event=False,
        )

    def _maybe_compose_pair(self, timestamp: float) -> None:
        if self.pair_read_id is not None:
            return
        if not all(
            self._lawful_bbo(state)[0] and self._lawful_bbo(state)[1]
            for state in self.states
        ):
            return
        pair = [{
            "leg_id": state["leg_id"],
            "book_receipt": state["current_book_receipt"],
            "bid_cents": int(self._lawful_bbo(state)[0][0][0]),
            "ask_cents": int(self._lawful_bbo(state)[1][0][0]),
        } for state in self.states]
        self.pair_read_id = sha256_json({
            "event_id": self.event["event_id"],
            "timestamp": float(timestamp),
            "pair": pair,
        })
        for state in self.states:
            self._action(
                state,
                timestamp,
                "pair_compose",
                "coherent_first_lawful_external_BBO_pair_read",
                authority="INITIAL_PAIR_BBO",
                pair_read_id=self.pair_read_id,
                pair=pair,
            )
        for state in self.states:
            bid = int(self._lawful_bbo(state)[0][0][0])
            self._place_or_reprice(
                state,
                timestamp,
                bid,
                "initial_pair_join_presence",
                authority="INITIAL_PAIR_BBO",
                composed=False,
                allow_upward=False,
            )

    def _record_discovery_print(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
        if state["discovery_t0"] is None:
            state["discovery_t0"] = timestamp
            state["discovery_deadline"] = timestamp + DISCOVERY_SECONDS
            state["discovery_status"] = "ACCUMULATING"
        if timestamp < float(state["discovery_deadline"]):
            state["discovery_prints"].append({
                "ts": timestamp,
                "price": int(row["price"]),
                "size": float(row["size"]),
                "receipt": _source_receipt(row),
            })

    def _finalize_discovery(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
    ) -> None:
        if (
            state["discovery_status"] != "ACCUMULATING"
            or timestamp < float(state["discovery_deadline"])
        ):
            return
        prices = [
            float(row["price"]) for row in state["discovery_prints"]
        ]
        if not prices:
            state["discovery_status"] = "NO_CALL"
            state["macro_target_status"] = "NO_CALL"
            self._no_call(
                state,
                timestamp,
                "MACRO_TARGET_NO_CALL",
                "native_discovery_interval_contains_no_lawful_print",
                authority="ATLAS_DISCOVERY_MACRO",
            )
            return
        discovery = float(statistics.median(prices))
        category = str(state["category"])
        cell = rounded_cent(discovery)
        state["discovery_price"] = discovery
        state["recut_native_row_observed_not_consumed"] = (
            (self.recut.get(category) or {}).get(str(cell))
        )
        if category in {"ATP_MAIN", "WTA_MAIN"}:
            state["discovery_status"] = "AVAILABLE_FROZEN"
            state["macro_target_status"] = "PAR_LOCK_JOIN_FROZEN"
            state["macro_target_source"] = "GAME_LIFECYCLE_PAR_LOCK_JOIN"
            active = state.get("active_order")
            state["macro_target_raw"] = (
                int(active["raw_target"]) if active is not None else None
            )
            state["macro_target_selected_ts"] = float(timestamp)
            self._action(
                state,
                timestamp,
                "macro_target_selected",
                "mains_native_par_lock_join_no_deep_aim",
                authority="ATLAS_DISCOVERY_MACRO",
                discovery_price_cents=discovery,
                discovery_receipts=[
                    row["receipt"] for row in state["discovery_prints"]
                ],
                recut_close_keyed_row_consumed=False,
                future_close_used=False,
                moving_bid_minus_edge_used=False,
                target_frozen_once=True,
                historical_path_state={
                    "ATLAS_target": "NO_DEEP_AIM_FOR_MAINS",
                    "LIBRARY_timing": "NO_CALL_MISANCHORED_0K_AXIS",
                    "drift_band": "NO_CALL_FUTURE_PATH_COMPONENTS",
                    "orientation": "NO_CALL_NOT_REQUIRED_FOR_PAR_LOCK",
                },
                historical_surface_source_sha256={
                    key: self.source_hashes.get(key)
                    for key in (
                        "drift", "divot", "band", "library", "orient", "recut"
                    )
                },
                causal_state=self._decision_state(state, timestamp),
            )
            return
        side = atlas_native_side(discovery)
        page_key = (
            f"{category}|{side}|{path_price_bucket(discovery)}"
        )
        page = (self.atlas.get("pages") or {}).get(page_key)
        bottom = page.get("bottom") if isinstance(page, Mapping) else None
        depth = (
            bottom.get("depth_p50")
            if isinstance(bottom, Mapping) else None
        )
        if (
            not isinstance(page, Mapping)
            or page.get("verdict") != "PATH"
            or depth is None
        ):
            state["discovery_status"] = "NO_CALL"
            state["macro_target_status"] = "NO_CALL"
            state["discovery_page_key"] = page_key
            self._no_call(
                state,
                timestamp,
                "MACRO_TARGET_NO_CALL",
                "native_ATLAS_PATH_page_unavailable",
                authority="ATLAS_DISCOVERY_MACRO",
            )
            return
        target = max(1, min(99, rounded_cent(discovery - float(depth))))
        state.update({
            "discovery_status": "AVAILABLE_FROZEN",
            "discovery_page_key": page_key,
            "discovery_page": dict(page),
            "macro_target_raw": target,
            "macro_target_status": "ATLAS_PATH_TARGET_FROZEN",
            "macro_target_source": "ATLAS_V1_NATIVE_DISCOVERY_BOTTOM_P50",
            "macro_pending_expression": True,
            "macro_target_selected_ts": float(timestamp),
        })
        self._action(
            state,
            timestamp,
            "macro_target_selected",
            "native_discovery_ATLAS_path_target_frozen",
            authority="ATLAS_DISCOVERY_MACRO",
            composition_selected_or_gated=False,
            discovery_price_cents=discovery,
            discovery_t0=state["discovery_t0"],
            discovery_interval_end=state["discovery_deadline"],
            discovery_receipts=[
                row["receipt"] for row in state["discovery_prints"]
            ],
            atlas_page_key=page_key,
            atlas_page_n=int(page.get("n") or 0),
            atlas_branded=page.get("branded"),
            atlas_bottom=dict(bottom),
            atlas_path=dict(page.get("path") or {}),
            atlas_contention=page.get("contention"),
            atlas_timing_gun=page.get("timing_gun"),
            target_raw_cents=target,
            target_frozen_once=True,
            recut_native_close_cell=cell,
            recut_close_keyed_row=state[
                "recut_native_row_observed_not_consumed"
            ],
            recut_row_consumed_for_target=False,
            recut_no_call_reason=(
                "causal_own_close_projection_unavailable"
            ),
            future_close_used=False,
            moving_bid_minus_edge_used=False,
            source_sha256=self.source_hashes.get("atlas"),
            historical_surface_NO_CALLs={
                "drift_surfaces_v1": (
                    "requires future net/dip path components for fitted band"
                ),
                "band_map_v1": (
                    "requires future net/dip path components for fitted band"
                ),
                "LIBRARY_V1_timing": "native_0k_axis_is_marked_misanchored",
                "ORIENT_V1": (
                    "not consumed without separately frozen pair tell mapping"
                ),
                "recut_cells": (
                    "close_keyed_without_causal_own_close_projection"
                ),
            },
            historical_surface_source_sha256={
                key: self.source_hashes.get(key)
                for key in (
                    "drift", "divot", "band", "library", "orient", "recut"
                )
            },
            causal_state=self._decision_state(state, timestamp),
        )

    def _apply_pending_macro(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
    ) -> None:
        if (
            not state.get("macro_pending_expression")
            or state.get("macro_target_raw") is None
        ):
            return
        bids, asks = self._lawful_bbo(state)
        if not bids or not asks:
            self._no_call(
                state,
                timestamp,
                "MACRO_EXPRESSION_NO_CALL",
                "frozen_target_waiting_for_lawful_external_BBO",
                authority="ATLAS_DISCOVERY_MACRO",
            )
            return
        self._place_or_reprice(
            state,
            timestamp,
            int(state["macro_target_raw"]),
            "native_ATLAS_path_target_adoption",
            authority="ATLAS_DISCOVERY_MACRO",
            composed=True,
            allow_upward=False,
        )
        state["macro_pending_expression"] = False

    def _detect_divot(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        if str(row.get("taker_side")) != "no":
            return
        definition = self.policy["divot"]
        timestamp = float(row["ts"])
        window = state["divot_window"]
        while window and float(window[0]["ts"]) < (
            timestamp - float(definition["trailing_median_seconds"])
        ):
            window.popleft()
        if len(window) < int(definition["minimum_prior_positive_prints"]):
            return
        median = float(statistics.median(
            [float(value["price"]) for value in window]
        ))
        depth = median - float(row["price"])
        if depth < float(definition["minimum_depth_cents"]):
            return
        _, asks = self._lawful_bbo(state)
        if not asks:
            return
        ask_hold = float(asks[0][0]) >= (
            median - float(definition["ask_hold_within_cents"])
        )
        if not ask_hold:
            return
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
            print_receipt=_source_receipt(row),
            print_price_cents=float(row["price"]),
            trailing_median_cents=median,
            divot_depth_cents=depth,
            lawful_ask_cents=int(asks[0][0]),
            queue_preserved=state.get("active_order") is not None,
            displayed_size_gate=False,
            causal_state=self._decision_state(state, timestamp),
        )

    def _apply_liveaim(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
    ) -> None:
        if (
            not self.policy.get("liveaim_enabled")
            or state.get("discovery_status") != "AVAILABLE_FROZEN"
            or state.get("macro_target_status") != "ATLAS_PATH_TARGET_FROZEN"
        ):
            return
        current = self._flow_state(state, timestamp)
        # Receipt the state transition, not every unchanged observation.
        # The complete tick-level input remains in the frozen range canvas,
        # while an order stream contains only decisions and changed verdicts.
        fingerprint = str(current["verdict"])
        state["last_liveaim_state"] = current
        changed = state.get("last_liveaim_fingerprint") != fingerprint
        if changed:
            state["last_liveaim_fingerprint"] = fingerprint
            self._action(
                state,
                timestamp,
                "liveaim_state",
                "source_bound_LIVE_AIM_chronological_state",
                authority="LIVEAIM_SOURCE_MAPPING",
                composition_selected_or_gated=(
                    state.get("active_order") is not None
                ),
                liveaim_state=current,
                source_paths=[
                    LIVEAIM_PROOF_PATH,
                    LIVEAIM_CODE_PATH + "::_liveaim_shadow",
                    VOLUME_PATH,
                ],
                executed_share_volume_is_stored=True,
                cadence_is_stored=True,
                unsourced_volume_direction_gate=False,
                last_trade_direction_gate=False,
                top5_pressure_sign_gate=False,
                isolated_taker_side_direction_gate=False,
            )
        verdict = str(current["verdict"])
        if verdict != "AIM_DEEP":
            if state.get("active_order") is not None and changed:
                state["queue_preserved_hold_count"] += 1
                self._action(
                    state,
                    timestamp,
                    "hold",
                    (
                        "LIVEAIM_NO_BID_CHASE_queue_preserving_hold"
                        if verdict == "NO_BID_CHASE_GUARD"
                        else "LIVEAIM_prior_or_shallow_no_upward_revision"
                    ),
                    authority="LIVEAIM_SOURCE_MAPPING",
                    composition_selected_or_gated=True,
                    price_cents=int(state["active_order"]["price"]),
                    queue_preserved=True,
                    liveaim_state=current,
                    upward_revision_forbidden=True,
                    causal_state=self._decision_state(state, timestamp),
                )
            return
        key = f"{state['category']}|{rounded_cent(state['discovery_price'])}"
        page = (self.guidebook.get("pages") or {}).get(key)
        deep = (
            page.get("depth_p25_of_w1s")
            if isinstance(page, Mapping) else None
        )
        if deep is None:
            self._no_call(
                state,
                timestamp,
                "LIVEAIM_DEEP_TIER_NO_CALL",
                f"guidebook_page_unavailable:{key}",
                authority="LIVEAIM_SOURCE_MAPPING",
            )
            return
        target = max(
            1,
            min(
                int(state["macro_target_raw"]),
                rounded_cent(float(state["discovery_price"]) - float(deep)),
            ),
        )
        prior_deep = state.get("liveaim_deep_target")
        state["liveaim_deep_target"] = (
            target
            if prior_deep is None else min(int(prior_deep), target)
        )
        active = state.get("active_order")
        if (
            active is not None
            and int(state["liveaim_deep_target"]) < int(active["price"])
        ):
            self._place_or_reprice(
                state,
                timestamp,
                int(state["liveaim_deep_target"]),
                "LIVEAIM_AIM_DEEP_source_authorized",
                authority="LIVEAIM_SOURCE_MAPPING",
                composed=True,
                allow_upward=False,
            )

    def _first_price_reach(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        order = state.get("active_order")
        if order is None or state["simulated_accounting_quantity"] == LOT:
            return
        if float(row["price"]) > float(order["price"]):
            return
        timestamp = float(row["ts"])
        receipt = _source_receipt(row)
        interval = state["order_intervals"][order["interval_index"]]
        state.update({
            "simulated_accounting_quantity": LOT,
            "simulated_fill_price": int(order["price"]),
            "simulated_fill_ts": timestamp,
            "simulated_fill_receipt": receipt,
        })
        interval["closed_ts"] = timestamp
        interval["close_reason"] = "CAUSAL_TAPE_PRICE_REACHED"
        self._action(
            state,
            timestamp,
            "price_reached_policy_tape",
            "receipt_identified_positive_public_execution_at_or_below_limit",
            authority=str(order["authority"]),
            order_interval_id=interval["order_interval_id"],
            limit_price_cents=int(order["price"]),
            print_price_cents=float(row["price"]),
            print_size=float(row["size"]),
            print_receipt=receipt,
            simulated_accounting_quantity=LOT,
            cumulative_five_required=False,
            queue_clearance_required=False,
            displayed_depth_required=False,
            causal_state=self._decision_state(state, timestamp),
        )
        state["active_order"] = None
        bids, _ = self._lawful_bbo(state)
        if (
            self.first_filled_leg is None
            and bids
        ):
            d1 = float(state["simulated_fill_price"]) - float(bids[0][0])
            self.first_filled_leg = state["leg_id"]
            self.first_fill_ts = timestamp
            self.first_fill_d1 = d1
            sibling = next(
                other for other in self.states if other is not state
            )
            sibling["headroom_armed"] = True
            sibling["headroom_d1_cents"] = d1
            sibling["headroom_b2_max_cents"] = headroom_b2_max(
                d1, float(self.policy["fee_cents"])
            )
            sibling["headroom_first_fill_reference"] = {
                "first_filled_leg": state["leg_id"],
                "first_fill_ts": timestamp,
                "first_leg_limit_price_cents": int(
                    state["simulated_fill_price"]
                ),
                "R1_external_bid_cents": int(bids[0][0]),
                "R1_book_receipt": state.get("current_book_receipt"),
                "d1_cents": d1,
                "fee_cents": float(self.policy["fee_cents"]),
            }
            self._action(
                sibling,
                timestamp,
                "headroom_armed",
                "first_PRICE_REACHED_leg_freezes_causal_pair_budget",
                authority="CAUSAL_PAIR_HEADROOM",
                **sibling["headroom_first_fill_reference"],
                b2_max_cents=sibling["headroom_b2_max_cents"],
                sibling_action_same_timestamp=False,
            )

    def _headroom_trigger(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
        if (
            not state.get("headroom_armed")
            or self.first_fill_ts is None
            or timestamp <= float(self.first_fill_ts)
            or state["simulated_accounting_quantity"] == LOT
            or state.get("active_order") is None
        ):
            return
        state["headroom_trigger_count"] += 1
        bids, asks = self._lawful_bbo(state)
        if not bids or not asks:
            self._no_call(
                state,
                timestamp,
                "HEADROOM_NO_CALL",
                "later_sibling_trigger_without_lawful_external_BBO",
                authority="CAUSAL_PAIR_HEADROOM",
            )
            return
        prior = int(state["active_order"]["price"])
        raw = prior + int(self.policy["headroom_step_cents"])
        proposed, expression = self._express(state, raw)
        d1 = float(state["headroom_d1_cents"])
        d2 = float(proposed) - float(bids[0][0])
        fee = float(self.policy["fee_cents"])
        maximum = int(state["headroom_b2_max_cents"])
        accepted = (
            proposed == prior + 1
            and d2 <= maximum
            and strict_pair_budget(d1, d2, fee)
            and proposed < int(asks[0][0])
        )
        self._action(
            state,
            timestamp,
            "headroom_decision",
            (
                "strict_combined_headroom_accept"
                if accepted else "strict_combined_headroom_refuse"
            ),
            authority="CAUSAL_PAIR_HEADROOM",
            trigger_receipt=_source_receipt(row),
            trigger_price_cents=float(row["price"]),
            prior_sibling_order_cents=prior,
            raw_proposed_sibling_cents=raw,
            expressed_proposed_sibling_cents=proposed,
            R2_external_bid_cents=int(bids[0][0]),
            R2_book_receipt=state.get("current_book_receipt"),
            d1_cents=d1,
            d2_cents=d2,
            fee_cents=fee,
            b2_max_cents=maximum,
            strict_guard_passed=strict_pair_budget(d1, d2, fee),
            exact_plus_one=proposed == prior + 1,
            action_taken=accepted,
            **expression,
        )
        if accepted:
            self._place_or_reprice(
                state,
                timestamp,
                raw,
                "causal_pair_headroom_plus_one",
                authority="CAUSAL_PAIR_HEADROOM",
                composed=False,
                allow_upward=True,
            )

    def _on_book(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
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
        self._maybe_compose_pair(timestamp)
        self._apply_pending_macro(state, timestamp)
        order = state.get("active_order")
        _, asks = self._lawful_bbo(state)
        if order is not None and asks and int(order["price"]) >= int(
            asks[0][0]
        ):
            self._place_or_reprice(
                state,
                timestamp,
                min(int(order["price"]), int(asks[0][0]) - 1),
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
        valid, _ = positive_print(row)
        if not valid:
            return
        receipt = _source_receipt(row)
        if receipt in state["seen_print_receipts"]:
            return
        state["seen_print_receipts"].add(receipt)
        self._first_price_reach(state, row)
        normalized = {
            "ts": float(row["ts"]),
            "price": int(row["price"]),
            "size": float(row["size"]),
            "receipt": receipt,
            "taker_side": row.get("taker_side"),
        }
        self._record_discovery_print(state, row)
        self._detect_divot(state, row)
        state["prints"].append(normalized)
        state["divot_window"].append(normalized)
        self._apply_pending_macro(state, float(row["ts"]))
        self._apply_liveaim(state, float(row["ts"]))
        self._headroom_trigger(state, row)

    def _finalize_due_discoveries(self, timestamp: float) -> None:
        for state in self.states:
            self._finalize_discovery(state, timestamp)

    def _terminalize(self, state: MutableMapping[str, Any]) -> None:
        if state["discovery_status"] == "ACCUMULATING":
            self._finalize_discovery(state, self.horizon)
        if state["discovery_status"] == "WAITING_FIRST_PRINT":
            state["discovery_status"] = "NO_CALL"
            state["macro_target_status"] = "NO_CALL"
            self._no_call(
                state,
                self.horizon,
                "MACRO_TARGET_NO_CALL",
                "no_lawful_true_print_for_native_discovery",
                authority="ATLAS_DISCOVERY_MACRO",
            )
        if state["active_order"] is not None:
            self._close_order(
                state,
                self.horizon,
                "POLICY_HORIZON",
                authority="POLICY_HORIZON",
                action_reason="declared_policy_horizon",
            )
        if not state["placed_any"]:
            self._no_call(
                state,
                self.horizon,
                "MARKET_EVIDENCE_NO_CALL",
                "no_lawful_external_BBO_pair_read",
                authority="INITIAL_PAIR_BBO",
            )
        state["terminal"] = "complete_score_free_policy_stream"
        self._action(
            state,
            self.horizon,
            "terminal",
            "complete_score_free_policy_stream",
            authority="POLICY_HORIZON",
            D_membership_continues=True,
            metrics=None,
            scored=False,
        )

    def run(self, event: Mapping[str, Any]) -> dict[str, Any]:
        self._validate_event(event)
        self.event = event
        self.left = float(event["policy_left_ts"])
        self.horizon = float(event["policy_decision_horizon_ts"])
        self.states = [
            self._new_state(event, leg) for leg in event["legs"]
        ]
        for state in self.states:
            self._action(
                state,
                self.left,
                "leg_open",
                "range_attack_pair_leg_initialized",
                authority="INITIAL_PAIR_BBO",
                evaluation_start_inaccessible=True,
                metrics=None,
            )
        timeline = []
        for index, leg in enumerate(event["legs"]):
            for observation in leg.get("observations") or []:
                timestamp = float(observation["ts"])
                if self.left <= timestamp <= self.horizon:
                    priority = 0 if observation.get("kind") == "book" else 1
                    timeline.append(
                        (timestamp, priority, index, observation)
                    )
        timeline.sort(key=lambda value: (
            value[0], value[1], value[2], _source_receipt(value[3])
        ))
        for timestamp, _, leg_index, observation in timeline:
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
                float(row["ts"]),
                str(row["leg_id"]),
                str(row["action"]),
                str(row["reason"]),
            ),
        )
        if any(
            action.get("above_nonself_bid_plus_one")
            or action.get("marketable")
            or (
                action.get("lawful_band") is False
            )
            for action in actions
        ):
            raise RangeAttackError("post-adjustment expression violation")
        result = {
            "schema_version": VERSION + "-candidate-event-stream-v1",
            "instrument_version": VERSION,
            "candidate_id": str(self.policy["candidate_id"]),
            "event_id": str(event["event_id"]),
            "event_date": str(event["event_date"]),
            "category": str(event["category"]),
            "policy_clock": {
                "policy_anchor_ts": float(event["policy_anchor_ts"]),
                "policy_anchor_observed_at_ts": float(
                    event["policy_anchor_observed_at_ts"]
                ),
                "policy_anchor_source": str(
                    event["policy_anchor_source"]
                ),
                "policy_left_ts": self.left,
                "policy_decision_horizon_ts": self.horizon,
                "evaluation_start_inaccessible": True,
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
                    "guarded_Window1_status": None,
                }
                for state in self.states
            },
            "evidence_census_by_leg": [{
                "leg_id": state["leg_id"],
                "ticker": state["ticker"],
                "book_receipt_count": len(state["seen_book_receipts"]),
                "positive_print_receipt_count": len(
                    state["seen_print_receipts"]
                ),
                "discovery_status": state["discovery_status"],
                "discovery_price": state["discovery_price"],
                "discovery_page_key": state["discovery_page_key"],
                "macro_target_status": state["macro_target_status"],
                "macro_target_raw": state["macro_target_raw"],
                "macro_target_source": state["macro_target_source"],
                "target_change_count": state["target_change_count"],
                "queue_preserved_hold_count": state[
                    "queue_preserved_hold_count"
                ],
                "queue_surrender_count": state[
                    "queue_surrender_count"
                ],
                "divot_count": state["divot_count"],
                "headroom_trigger_count": state[
                    "headroom_trigger_count"
                ],
                "last_liveaim_state": state["last_liveaim_state"],
                "no_calls": state["no_calls"],
                "D_member": True,
                "metrics": None,
            } for state in self.states],
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
            "price_fillability_evaluation": None,
            "metrics": None,
            "scored": False,
        }
        result["order_stream_sha256"] = sha256_json(result["order_stream"])
        result["order_intervals_sha256"] = sha256_json(
            result["order_intervals_by_leg"]
        )
        return result


RangeAttackInstrument = RangeAttackSimulator
