#!/usr/bin/env python3
"""Score-free Window-1 T2 causal-divot overlay.

T2 changes only the unfilled sibling after the first credited leg.  It binds
the passed Range-Attack/T1 chronology and fill admission, enumerates causal
source-backed sibling prices, preserves an active parent exposure unless a
named existing microstructure rule proves decay, and separates divot
recognition, later action, and still-later fill evidence.
"""

from __future__ import annotations

import heapq
import json
import math
from collections import Counter, deque
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping

import window1_t1_post_first_leg_instrument as t1


passed = t1.passed
VERSION = "window1-t2-causal-divot-v1"
EXACT_PARENT = "d710ba0606084f67625e255e87ebad1cd016bf6a"
CONTROLLING_RESULTS_AUDIT = "33ae7350f1bd67387146acae51951f0b76d52313"
CONTROLLING_RESULTS = "d710ba0606084f67625e255e87ebad1cd016bf6a"
CONTROLLING_T1_AUDIT = "de2f627e53885bd1a44a42b92f23b5b93a391a47"
CONTROLLING_ATTRIBUTION_AUDIT = (
    "b96873c9a5eb340a7abb0eda9bffd6f0cedb4341"
)
CONTROLLING_ASYNC_AUDIT = "26dd6e5e19a7890f02b538cc8b14a900f36e5b2f"
SPEC_PATH = (
    "arb-executor/docs/research/window1/"
    "WINDOW1_T2_CAUSAL_DIVOT_CANDIDATES_V1.json"
)
LOT = passed.LOT

BASE_CANDIDATES = t1.BASE_CANDIDATES
VARIANTS = (
    "fixed_admission_parent_control",
    "non_displacing_target_completeness",
    "target_completeness_evidence_decay",
    "full_causal_divot_stack",
)
CANDIDATES = tuple(
    f"w1_t2__{regime}__{variant}"
    for regime in ("macro_hold", "macro_micro")
    for variant in VARIANTS
)
SWITCHES = {
    "fixed_admission_parent_control": {
        "fixed_admission_control": True,
        "non_displacing_target_completeness": False,
        "evidence_decay_exit": False,
        "actionable_first_fill_response": False,
        "causal_divot_recall": False,
    },
    "non_displacing_target_completeness": {
        "fixed_admission_control": False,
        "non_displacing_target_completeness": True,
        "evidence_decay_exit": False,
        "actionable_first_fill_response": False,
        "causal_divot_recall": False,
    },
    "target_completeness_evidence_decay": {
        "fixed_admission_control": False,
        "non_displacing_target_completeness": True,
        "evidence_decay_exit": True,
        "actionable_first_fill_response": False,
        "causal_divot_recall": False,
    },
    "full_causal_divot_stack": {
        "fixed_admission_control": False,
        "non_displacing_target_completeness": True,
        "evidence_decay_exit": True,
        "actionable_first_fill_response": True,
        "causal_divot_recall": True,
    },
}
AUTHORITY_ORDER = {
    "CAUSAL_DIVOT_LATER_RECURRENCE": 0,
    "LIVEAIM_AIM_DEEP_SOURCE_MAPPING": 1,
    "NATIVE_MACRO_TARGET": 2,
    "CURRENT_EXTERNAL_BID": 3,
    "BID_PLUS_ONE_FALLBACK_NOT_PREFERRED": 4,
    "ACTIVE_PARENT_EXPOSURE": -1,
}


class T2Error(RuntimeError):
    """A T2 causal or freeze contract was violated."""


class _DynamicMedian:
    """Causal sliding median with exact add/remove semantics."""

    def __init__(self) -> None:
        self.low: list[float] = []
        self.high: list[float] = []
        self.delayed: Counter[float] = Counter()
        self.low_size = 0
        self.high_size = 0

    def _prune(self, heap: list[float], *, low: bool) -> None:
        while heap:
            value = -heap[0] if low else heap[0]
            if not self.delayed[value]:
                return
            heapq.heappop(heap)
            self.delayed[value] -= 1
            if not self.delayed[value]:
                del self.delayed[value]

    def _rebalance(self) -> None:
        if self.low_size > self.high_size + 1:
            value = -heapq.heappop(self.low)
            heapq.heappush(self.high, value)
            self.low_size -= 1
            self.high_size += 1
            self._prune(self.low, low=True)
        elif self.low_size < self.high_size:
            value = heapq.heappop(self.high)
            heapq.heappush(self.low, -value)
            self.high_size -= 1
            self.low_size += 1
            self._prune(self.high, low=False)

    def add(self, value: float) -> None:
        value = float(value)
        if not self.low or value <= -self.low[0]:
            heapq.heappush(self.low, -value)
            self.low_size += 1
        else:
            heapq.heappush(self.high, value)
            self.high_size += 1
        self._rebalance()

    def remove(self, value: float) -> None:
        value = float(value)
        self.delayed[value] += 1
        if self.low and value <= -self.low[0]:
            self.low_size -= 1
            if value == -self.low[0]:
                self._prune(self.low, low=True)
        else:
            self.high_size -= 1
            if self.high and value == self.high[0]:
                self._prune(self.high, low=False)
        self._rebalance()

    def median(self) -> float | None:
        total = self.low_size + self.high_size
        if total == 0:
            return None
        self._prune(self.low, low=True)
        self._prune(self.high, low=False)
        if total % 2:
            return float(-self.low[0])
        return float((-self.low[0] + self.high[0]) / 2.0)


class _RollingFlow:
    """Exact chronological 30-minute print state without future access."""

    def __init__(self) -> None:
        self.consumed = 0
        self.rows: deque[Mapping[str, Any]] = deque()
        self.price_counts = [0] * 100
        self.volume = 0.0
        self.gaps = _DynamicMedian()
        self.receipt_chain = "0" * 64

    def _chain(self, operation: str, row: Mapping[str, Any]) -> None:
        self.receipt_chain = t1.sha256_json({
            "prior": self.receipt_chain,
            "operation": operation,
            "receipt": row["receipt"],
            "ts": float(row["ts"]),
        })

    def _append(self, row: Mapping[str, Any]) -> None:
        if self.rows:
            self.gaps.add(
                float(row["ts"]) - float(self.rows[-1]["ts"])
            )
        self.rows.append(row)
        self.price_counts[int(row["price"])] += 1
        self.volume += float(row["size"])
        self._chain("ENTER", row)

    def _popleft(self) -> None:
        old = self.rows[0]
        if len(self.rows) >= 2:
            self.gaps.remove(
                float(self.rows[1]["ts"]) - float(old["ts"])
            )
        self.rows.popleft()
        self.price_counts[int(old["price"])] -= 1
        self.volume -= float(old["size"])
        self._chain("EXIT", old)

    def sync(
        self,
        prints: list[Mapping[str, Any]],
        timestamp: float,
    ) -> None:
        while self.consumed < len(prints):
            self._append(prints[self.consumed])
            self.consumed += 1
        cutoff = float(timestamp) - passed.v1.FLOW_WINDOW_SECONDS
        while self.rows and float(self.rows[0]["ts"]) < cutoff:
            self._popleft()

    def upper_price_median(self) -> int | None:
        if not self.rows:
            return None
        position = len(self.rows) // 2
        running = 0
        for cent in range(1, 100):
            running += self.price_counts[cent]
            if running > position:
                return cent
        raise T2Error("rolling price median lost conservation")


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _variant(candidate_id: str) -> str:
    for value in VARIANTS:
        if candidate_id.endswith("__" + value):
            return value
    raise T2Error(f"unknown T2 candidate: {candidate_id}")


def _regime(candidate_id: str) -> str:
    if "__macro_hold__" in candidate_id:
        return "macro_hold"
    if "__macro_micro__" in candidate_id:
        return "macro_micro"
    raise T2Error(f"unknown T2 regime: {candidate_id}")


def base_candidate_id(candidate_id: str) -> str:
    return BASE_CANDIDATES[0 if _regime(candidate_id) == "macro_hold" else 1]


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    spec = read_json(repo / SPEC_PATH)
    if spec.get("instrument_version") != VERSION:
        raise T2Error("T2 instrument version mismatch")
    if spec.get("exact_parent") != EXACT_PARENT:
        raise T2Error("T2 parent binding mismatch")
    if spec.get("controlling_t1_results_audit") != CONTROLLING_RESULTS_AUDIT:
        raise T2Error("T2 results-audit binding mismatch")
    if tuple(spec.get("candidate_ids") or ()) != CANDIDATES:
        raise T2Error("T2 candidate membership or order changed")
    if tuple(spec.get("baseline_candidate_ids") or ()) != BASE_CANDIDATES:
        raise T2Error("T2 baseline binding changed")
    if spec.get("free_numeric_parameters") != []:
        raise T2Error("free T2 parameters are forbidden")
    if spec.get("metrics") is not None or spec.get("scored") is not False:
        raise T2Error("performance entered T2 specification")
    for candidate in CANDIDATES:
        if (spec.get("switch_matrix") or {}).get(candidate) != SWITCHES[
            _variant(candidate)
        ]:
            raise T2Error(f"T2 switch matrix changed for {candidate}")
    return spec


def candidate_policy(
    repo: Path,
    spec: Mapping[str, Any],
    candidate_id: str,
    *,
    ablations: Iterable[str] = (),
) -> dict[str, Any]:
    if list(ablations):
        raise T2Error("post-freeze T2 ablations are forbidden")
    if candidate_id not in CANDIDATES:
        raise T2Error(f"candidate not frozen: {candidate_id}")
    baseline_spec = passed.load_candidate_spec(repo)
    baseline_id = base_candidate_id(candidate_id)
    policy = passed.candidate_policy(baseline_spec, baseline_id)
    policy.update({
        "candidate_id": candidate_id,
        "base_candidate_id": baseline_id,
        "t1_variant": "T2_FIXED_ADMISSION",
        "t1_switches": {
            "receipt_keyed_response": False,
            "target_completeness": False,
            "lawful_persistence": False,
        },
        "t2_variant": _variant(candidate_id),
        "t2_switches": dict(SWITCHES[_variant(candidate_id)]),
        "metrics": None,
        "scored": False,
    })
    return policy


def exact_cent(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise T2Error(f"{field}: bool is not an exact cent")
    if isinstance(value, int):
        result = value
    elif (
        isinstance(value, float)
        and math.isfinite(value)
        and value.is_integer()
    ):
        result = int(value)
    else:
        raise T2Error(f"{field}: non-integer cent")
    if not 1 <= result <= 99:
        raise T2Error(f"{field}: outside 1..99")
    return result


def _sign(value: int) -> str:
    if value < 0:
        return "NEGATIVE_D2"
    if value == 0:
        return "ZERO_D2"
    return "POSITIVE_D2"


class T2Simulator(t1.T1Simulator):
    """Fixed-admission parent plus causal post-first sibling composition."""

    def __init__(
        self,
        policy: Mapping[str, Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(policy, *args, **kwargs)
        self.t2_switches = dict(policy["t2_switches"])
        self._t2_authorized_replacement: dict[str, Any] | None = None

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        state = super()._new_state(event, leg)
        state.update({
            "t2_episode_receipts_seen": set(),
            "t2_observed_print_prices": {},
            "t2_cumulative_print_count": 0,
            "t2_cumulative_executed_volume": 0.0,
            "t2_rolling_flow": _RollingFlow(),
            "t2_rolling_flow_cache_key": None,
            "t2_rolling_flow_cache_value": None,
            "t2_divot_recognitions": [],
            "t2_latest_divot_by_price": {},
            "t2_divot_recurrences": [],
            "t2_target_surface_receipts": [],
            "t2_support_decay_receipts": [],
            "t2_target_selection_receipts": [],
            "t2_episode_decisions": [],
            "t2_divot_chronology": [],
            "t2_parent_exposure_receipts": [],
        })
        return state

    def _is_post_first_sibling(self, state: Mapping[str, Any]) -> bool:
        return bool(
            self.first_filled_leg is not None
            and self.first_fill_ts is not None
            and state["leg_id"] != self.first_filled_leg
            and state["simulated_accounting_quantity"] != LOT
        )

    def _inside_t2_corridor(self, timestamp: float) -> bool:
        return bool(
            self.first_fill_ts is not None
            and float(timestamp) > float(self.first_fill_ts)
            and float(timestamp) <= float(self.base_horizon)
        )

    def _flow_state(
        self,
        state: Mapping[str, Any],
        timestamp: float,
    ) -> dict[str, Any]:
        if (
            self.t2_switches["fixed_admission_control"]
        ):
            return super()._flow_state(state, timestamp)
        key = (
            float(timestamp),
            state.get("current_book_receipt"),
            len(state["prints"]),
            state.get("depth_within_three"),
            state.get("depth_trend"),
        )
        if state.get("t2_rolling_flow_cache_key") == key:
            return dict(state["t2_rolling_flow_cache_value"])
        rolling: _RollingFlow = state["t2_rolling_flow"]
        rolling.sync(state["prints"], float(timestamp))
        count = len(rolling.rows)
        median = rolling.upper_price_median()
        last_price = (
            int(rolling.rows[-1]["price"]) if rolling.rows else None
        )
        if count < 3 or last_price == median:
            signature = "flat"
        elif last_price is not None and median is not None:
            signature = "rising" if last_price > median else "falling"
        else:
            signature = "flat"
        book = state.get("current_book") or {}
        bids = passed.mechanical.external_bids(book, True)
        asks = passed.mechanical.asks(book)
        spread = (
            int(asks[0][0]) - int(bids[0][0])
            if bids and asks else None
        )
        mapping = passed.v1.liveaim_mapping(
            category=str(state["category"]),
            print_count=count,
            signature=signature,
            depth_trend=state.get("depth_trend"),
            spread_cents=spread,
        )
        value = {
            "timestamp": float(timestamp),
            "unique_positive_print_count_30m": count,
            "executed_share_volume_30m": float(rolling.volume),
            "inter_print_cadence_seconds": rolling.gaps.median(),
            "verified_print_trailing_signature": signature,
            "first_print_receipt": (
                rolling.rows[0]["receipt"] if rolling.rows else None
            ),
            "last_print_receipt": (
                rolling.rows[-1]["receipt"] if rolling.rows else None
            ),
            "print_receipts_sha256": t1.sha256_json({
                "causal_incremental_enter_exit_chain":
                    rolling.receipt_chain,
                "first": (
                    rolling.rows[0]["receipt"] if rolling.rows else None
                ),
                "last": (
                    rolling.rows[-1]["receipt"] if rolling.rows else None
                ),
                "count": count,
            }),
            "print_receipt_window_identity_law":
                "causal_incremental_enter_exit_chain_v1",
            "spread_cents": spread,
            "bid_depth_within_three_cents": state.get(
                "depth_within_three"
            ),
            "depth_trend": state.get("depth_trend"),
            **mapping,
        }
        # The state object is mutable in every caller; Mapping annotates that
        # this method does not alter market evidence, only its causal index.
        state["t2_rolling_flow_cache_key"] = key  # type: ignore[index]
        state["t2_rolling_flow_cache_value"] = value  # type: ignore[index]
        return dict(value)

    def _exact_liveaim_action_state(
        self,
        state: Mapping[str, Any],
        current: Mapping[str, Any],
    ) -> dict[str, Any]:
        value = dict(current)
        rolling: _RollingFlow = state["t2_rolling_flow"]
        value["print_receipts_sha256"] = t1.sha256_json([
            row["receipt"] for row in rolling.rows
        ])
        value["executed_share_volume_30m"] = float(sum(
            float(row["size"]) for row in rolling.rows
        ))
        value.pop("print_receipt_window_identity_law", None)
        return value

    def _decision_state(
        self,
        state: Mapping[str, Any],
        timestamp: float,
    ) -> dict[str, Any]:
        value = super()._decision_state(state, timestamp)
        if self.t2_switches["fixed_admission_control"]:
            return value
        value["flow"] = self._exact_liveaim_action_state(
            state, value["flow"]
        )
        sibling = next(
            other for other in self.states if other is not state
        )
        value["sibling"]["flow"] = self._exact_liveaim_action_state(
            sibling, value["sibling"]["flow"]
        )
        return value

    def _apply_liveaim(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
    ) -> None:
        if self.t2_switches["fixed_admission_control"]:
            super()._apply_liveaim(state, timestamp)
            return
        if (
            not self.policy.get("liveaim_enabled")
            or state.get("discovery_status") != "AVAILABLE_FROZEN"
            or state.get("macro_target_status")
            != "ATLAS_PATH_TARGET_FROZEN"
        ):
            return
        current = self._flow_state(state, timestamp)
        fingerprint = str(current["verdict"])
        state["last_liveaim_state"] = current
        changed = state.get("last_liveaim_fingerprint") != fingerprint
        action_state = (
            self._exact_liveaim_action_state(state, current)
            if changed else current
        )
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
                liveaim_state=action_state,
                source_paths=[
                    passed.LIVEAIM_PROOF_PATH,
                    passed.LIVEAIM_CODE_PATH + "::_liveaim_shadow",
                    passed.VOLUME_PATH,
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
                    liveaim_state=action_state,
                    upward_revision_forbidden=True,
                    causal_state=self._decision_state(state, timestamp),
                )
            return
        key = (
            f"{state['category']}|"
            f"{passed.v1.rounded_cent(state['discovery_price'])}"
        )
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
                passed.v1.rounded_cent(
                    float(state["discovery_price"]) - float(deep)
                ),
            ),
        )
        prior_deep = state.get("liveaim_deep_target")
        state["liveaim_deep_target"] = (
            target if prior_deep is None
            else min(int(prior_deep), target)
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

    def _headroom_trigger(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        if self.t2_switches["fixed_admission_control"]:
            super()._headroom_trigger(state, row)
            return
        if (
            self._is_post_first_sibling(state)
            and self._inside_t2_corridor(float(row["ts"]))
        ):
            self._action(
                state,
                float(row["ts"]),
                "t2_inherited_bid_plus_one_not_selected",
                "T1_bid_plus_one_rule_retracted_after_zero_of_82_fills",
                authority="CAUSAL_PAIR_HEADROOM",
                trigger_receipt=passed._source_receipt(row),
                positive_d2_preference=False,
                executable_action=False,
            )

    def _detect_divot(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        price = int(row["price"])
        state["t2_observed_print_prices"].setdefault(price, []).append({
            "ts": float(row["ts"]),
            "receipt": passed._source_receipt(row),
            "size": float(row["size"]),
        })
        before = int(state.get("divot_count") or 0)
        super()._detect_divot(state, row)
        if int(state.get("divot_count") or 0) <= before:
            return
        recognition = {
            "event_id": state["event_id"],
            "candidate_id": state["candidate_id"],
            "leg_id": state["leg_id"],
            "recognition_ts": float(row["ts"]),
            "recognition_receipt": passed._source_receipt(row),
            "recognized_X_cents": int(row["price"]),
            "recognition_number": len(state["t2_divot_recognitions"]) + 1,
            "source_rule": "positive_print_microdivot",
            "action_on_recognition_receipt": False,
            "fill_on_recognition_receipt": False,
            "metrics": None,
            "scored": False,
        }
        state["t2_divot_recognitions"].append(recognition)
        state["t2_latest_divot_by_price"][
            int(recognition["recognized_X_cents"])
        ] = recognition
        state["t2_divot_chronology"].append({
            **recognition,
            "chronology_stage": "RECOGNITION",
        })

    def _current_recurrences(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        timestamp = float(row["ts"])
        receipt = passed._source_receipt(row)
        result = []
        for recognition in state["t2_latest_divot_by_price"].values():
            if timestamp <= float(recognition["recognition_ts"]):
                continue
            x = int(recognition["recognized_X_cents"])
            evidence_type = None
            if row.get("kind") == "print" and int(row["price"]) == x:
                evidence_type = "LATER_TRUE_PRINT_RECURRENCE"
            if evidence_type is None:
                continue
            recurrence = {
                "event_id": state["event_id"],
                "candidate_id": state["candidate_id"],
                "leg_id": state["leg_id"],
                "recognized_X_cents": x,
                "recognition_ts": recognition["recognition_ts"],
                "recognition_receipt": recognition["recognition_receipt"],
                "recurrence_ts": timestamp,
                "recurrence_receipt": receipt,
                "recurrence_evidence_type": evidence_type,
                "recurrence_number": 1 + sum(
                    prior["recognition_receipt"]
                    == recognition["recognition_receipt"]
                    for prior in state["t2_divot_recurrences"]
                ),
                "strictly_later_than_recognition": True,
                "recurrence_receipt_can_fill_new_action": False,
                "metrics": None,
                "scored": False,
            }
            state["t2_divot_recurrences"].append(recurrence)
            state["t2_divot_chronology"].append({
                **recurrence,
                "chronology_stage": "LATER_RECURRENCE",
            })
            result.append(recurrence)
        return result

    def _lawful_candidate(
        self,
        *,
        source: str,
        x: int,
        bid: int,
        ask: int,
        d1: int,
        b2_max: int,
        fee: int,
        source_receipts: list[str],
        observed_support: Mapping[str, Any],
    ) -> dict[str, Any]:
        d2 = int(x) - int(bid)
        checks = {
            "exact_integer_cent": isinstance(x, int) and not isinstance(x, bool),
            "lawful_cent": 1 <= int(x) <= 99,
            "maker_safe": int(x) < int(ask),
            "inside_event_specific_b2_max": d2 <= int(b2_max),
            "strict_combined_negative": int(d1) + d2 + int(fee) < 0,
            "at_most_bid_plus_one": int(x) <= int(bid) + 1,
        }
        return {
            "source": source,
            "X_cents": int(x),
            "bid_cents": int(bid),
            "ask_cents": int(ask),
            "d1_cents": int(d1),
            "d2_cents": d2,
            "d2_sign": _sign(d2),
            "b2_max_cents": int(b2_max),
            "fee_cents": int(fee),
            "checks": checks,
            "lawful": all(checks.values()),
            "source_receipts": list(source_receipts),
            "support_snapshot_shared_with_surface": True,
        }

    def _target_surface(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
        recurrences: list[Mapping[str, Any]],
    ) -> dict[str, Any]:
        timestamp = float(row["ts"])
        receipt = passed._source_receipt(row)
        bids, asks = self._lawful_bbo(state)
        if not bids or not asks or int(bids[0][0]) >= int(asks[0][0]):
            result = {
                "event_id": state["event_id"],
                "candidate_id": state["candidate_id"],
                "leg_id": state["leg_id"],
                "timestamp": timestamp,
                "trigger_receipt": receipt,
                "trigger_kind": row.get("kind"),
                "status": "MARKET_EVIDENCE_NO_CALL",
                "reason": "lawful_positive_size_external_BBO_unavailable",
                "targets": [],
                "metrics": None,
                "scored": False,
            }
            state["t2_target_surface_receipts"].append(result)
            return result
        bid, ask = int(bids[0][0]), int(asks[0][0])
        d1 = int(state["headroom_d1_cents"])
        maximum = int(state["headroom_b2_max_cents"])
        fee = int(self.policy["fee_cents"])
        flow = self._flow_state(state, timestamp)
        cached_count = int(state["t2_cumulative_print_count"])
        if cached_count < len(state["prints"]):
            state["t2_cumulative_executed_volume"] += float(sum(
                float(value["size"])
                for value in state["prints"][cached_count:]
            ))
            state["t2_cumulative_print_count"] = len(state["prints"])
        causal_last_trade = (
            int(row["price"])
            if row.get("kind") == "print"
            else state.get("current_last_trade")
        )
        causal_last_trade_provenance = (
            "VERIFIED_PRINT_TIMESTAMP"
            if row.get("kind") == "print"
            else state.get("current_last_trade_provenance")
        )
        observed_support = {
            "current_last_trade_cents": causal_last_trade,
            "current_last_trade_provenance":
                causal_last_trade_provenance,
            "prints_observed_count": len(state["prints"]),
            "executed_share_volume_observed": float(
                state["t2_cumulative_executed_volume"]
            ),
            "print_cadence_seconds": flow.get(
                "inter_print_cadence_seconds"
            ),
            "flow_verdict": flow.get("verdict"),
            "flow_ratio": flow.get("flow_ratio"),
            "spread_cents": ask - bid,
            "external_bid_chain": [list(value) for value in bids[:5]],
            "external_ask_chain": [list(value) for value in asks[:5]],
            "positive_displayed_bid_depth_top5": float(sum(
                float(value[1]) for value in bids[:5]
            )),
            "positive_displayed_ask_depth_top5": float(sum(
                float(value[1]) for value in asks[:5]
            )),
            "depth_within_three_cents": state.get("depth_within_three"),
            "depth_trend": state.get("depth_trend"),
            "remaining_policy_seconds": max(0.0, self.base_horizon - timestamp),
            "macro_posture": state.get("macro_posture"),
            "macro_target_status": state.get("macro_target_status"),
            "macro_target_raw": state.get("macro_target_raw"),
            "discovery_price": state.get("discovery_price"),
            "discovery_cell": state.get("discovery_cell"),
            "category": state.get("category"),
            "prior_reach_prices": sorted(
                int(price) for price in state["t2_observed_print_prices"]
            ),
            "divot_recognition_count": len(
                state["t2_divot_recognitions"]
            ),
            "divot_recurrence_count": len(state["t2_divot_recurrences"]),
        }
        raw: list[tuple[str, int, list[str]]] = []
        active = state.get("active_order")
        if active is not None:
            raw.append((
                "ACTIVE_PARENT_EXPOSURE",
                int(active["price"]),
                [str(active.get("trigger_receipt") or "ACTIVE_INTERVAL")],
            ))
        for recurrence in recurrences:
            raw.append((
                "CAUSAL_DIVOT_LATER_RECURRENCE",
                int(recurrence["recognized_X_cents"]),
                [
                    str(recurrence["recognition_receipt"]),
                    str(recurrence["recurrence_receipt"]),
                ],
            ))
        deep = state.get("liveaim_deep_target")
        if deep is not None and flow.get("verdict") == "AIM_DEEP":
            raw.append((
                "LIVEAIM_AIM_DEEP_SOURCE_MAPPING",
                int(deep),
                [
                    str(state.get("current_book_receipt") or receipt),
                    str(flow.get("print_receipts_sha256") or "NO_PRINTS"),
                ],
            ))
        macro = state.get("macro_target_raw")
        if macro is not None:
            expressed = int(macro) if int(macro) <= bid else bid + 1
            raw.append((
                "NATIVE_MACRO_TARGET",
                max(1, min(99, ask - 1, expressed)),
                [str(state.get("current_book_receipt") or receipt)],
            ))
        current_last_trade = causal_last_trade
        if current_last_trade is not None:
            raw.append((
                "CURRENT_TRUE_PRINT_REACH_CONTEXT",
                int(current_last_trade),
                [receipt],
            ))
        raw.append((
            "CURRENT_EXTERNAL_BID", bid,
            [str(state.get("current_book_receipt") or receipt)],
        ))
        raw.append((
            "BID_PLUS_ONE_FALLBACK_NOT_PREFERRED",
            min(ask - 1, bid + 1),
            [str(state.get("current_book_receipt") or receipt)],
        ))
        unique: dict[tuple[str, int], tuple[str, int, list[str]]] = {}
        for source, x, receipts in raw:
            unique[(source, x)] = (source, x, receipts)
        targets = [
            self._lawful_candidate(
                source=source, x=x, bid=bid, ask=ask, d1=d1,
                b2_max=maximum, fee=fee, source_receipts=receipts,
                observed_support=observed_support,
            )
            for source, x, receipts in unique.values()
        ]
        result = {
            "event_id": state["event_id"],
            "candidate_id": state["candidate_id"],
            "leg_id": state["leg_id"],
            "timestamp": timestamp,
            "trigger_receipt": receipt,
            "trigger_kind": row.get("kind"),
            "status": "AVAILABLE",
            "first_filled_leg": self.first_filled_leg,
            "first_fill_timestamp": self.first_fill_ts,
            "d1_cents": d1,
            "b2_max_cents": maximum,
            "fee_cents": fee,
            "BBO_receipt": state.get("current_book_receipt"),
            "observed_support": observed_support,
            "targets": targets,
            "positive_d2_target_count": sum(
                target["lawful"] and target["d2_cents"] > 0
                for target in targets
            ),
            "future_evidence_used": False,
            "metrics": None,
            "scored": False,
        }
        state["t2_target_surface_receipts"].append(result)
        return result

    def _select_target(
        self,
        surface: Mapping[str, Any],
        *,
        active_price: int | None,
        allow_recurrence: bool,
        allow_decay: bool,
    ) -> dict[str, Any] | None:
        lawful = [
            dict(target) for target in surface.get("targets") or []
            if (
                target["lawful"]
                and target["source"] != "CURRENT_TRUE_PRINT_REACH_CONTEXT"
            )
        ]
        if active_price is not None:
            active = [
                target for target in lawful
                if target["source"] == "ACTIVE_PARENT_EXPOSURE"
                and target["X_cents"] == active_price
            ]
            if not allow_decay:
                return active[0] if active else None
            active_is_lawful = bool(active)
            if active_is_lawful:
                permitted = [
                    target for target in lawful
                    if (
                        target["source"]
                        == "LIVEAIM_AIM_DEEP_SOURCE_MAPPING"
                        and target["X_cents"] < active_price
                    ) or (
                        allow_recurrence
                        and target["source"]
                        == "CAUSAL_DIVOT_LATER_RECURRENCE"
                        and target["X_cents"] < active_price
                    )
                ]
            else:
                # A contemporaneous raw BBO receipt has proved that the old
                # target no longer obeys the event-specific budget/maker law.
                # In decay variants a source-backed lawful target may replace
                # it; bid+1 remains last and is never selected by sign.
                permitted = [
                    target for target in lawful
                    if target["source"] != "ACTIVE_PARENT_EXPOSURE"
                    and (
                        allow_recurrence
                        or target["source"]
                        != "CAUSAL_DIVOT_LATER_RECURRENCE"
                    )
                ]
            if permitted:
                return sorted(
                    permitted,
                    key=lambda target: (
                        AUTHORITY_ORDER[target["source"]],
                        target["X_cents"],
                    ),
                )[0]
            return active[0] if active else None
        permitted = [
            target for target in lawful
            if allow_recurrence
            or target["source"] != "CAUSAL_DIVOT_LATER_RECURRENCE"
        ]
        if not permitted:
            return None
        # Source authority is fixed.  BID+1 is last and therefore never
        # preferred merely because it spends positive-delta headroom.
        return sorted(
            permitted,
            key=lambda target: (
                AUTHORITY_ORDER[target["source"]],
                target["X_cents"],
            ),
        )[0]

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
        if (
            self.t2_switches["fixed_admission_control"]
            or not self._is_post_first_sibling(state)
            or not self._inside_t2_corridor(timestamp)
            or state.get("active_order") is None
        ):
            return super()._place_or_reprice(
                state, timestamp, raw_target, reason,
                authority=authority, composed=composed,
                allow_upward=allow_upward,
            )
        prior = int(state["active_order"]["price"])
        if authority == "MAKER_SAFETY":
            return super()._place_or_reprice(
                state, timestamp, raw_target, reason,
                authority=authority, composed=composed,
                allow_upward=allow_upward,
            )
        permit = self._t2_authorized_replacement
        if (
            permit is not None
            and int(permit["replacement_X_cents"]) == int(raw_target)
            and permit["authority"] == authority
        ):
            return super()._place_or_reprice(
                state, timestamp, raw_target, reason,
                authority=authority, composed=composed,
                allow_upward=allow_upward,
            )
        receipt = {
            "event_id": state["event_id"],
            "candidate_id": state["candidate_id"],
            "leg_id": state["leg_id"],
            "timestamp": float(timestamp),
            "trigger_receipt": state.get("current_book_receipt"),
            "active_X_cents": prior,
            "proposed_replacement_X_cents": int(raw_target),
            "proposed_authority": authority,
            "proposed_reason": reason,
            "decision": "HOLD",
            "counterfactual_action_rejected": "REPRICE",
            "rejection_reason": "NO_NAMED_RECEIPT_BACKED_EVIDENCE_DECAY",
            "queue_surrendered": False,
            "unconditional_persistence": False,
            "metrics": None,
            "scored": False,
        }
        state["t2_support_decay_receipts"].append(receipt)
        state["t2_parent_exposure_receipts"].append(receipt)
        self._action(
            state, timestamp,
            "t2_non_displacing_hold",
            "active_parent_exposure_preserved_without_decay_authority",
            authority="CAUSAL_PAIR_HEADROOM",
            price_cents=prior,
            rejected_replacement_X_cents=int(raw_target),
            rejected_authority=authority,
            queue_preserved=True,
            unconditional_persistence=False,
        )
        return False

    def _episode_decision(
        self,
        state: MutableMapping[str, Any],
        row: Mapping[str, Any],
    ) -> None:
        if self.t2_switches["fixed_admission_control"]:
            return
        timestamp = float(row["ts"])
        if (
            not self._is_post_first_sibling(state)
            or not self._inside_t2_corridor(timestamp)
        ):
            return
        receipt = passed._source_receipt(row)
        if not receipt or receipt in state["t2_episode_receipts_seen"]:
            return
        state["t2_episode_receipts_seen"].add(receipt)
        recurrences = self._current_recurrences(state, row)
        surface = self._target_surface(state, row, recurrences)
        active = state.get("active_order")
        prior_x = int(active["price"]) if active is not None else None
        selected = self._select_target(
            surface,
            active_price=prior_x,
            allow_recurrence=self.t2_switches["causal_divot_recall"],
            allow_decay=self.t2_switches["evidence_decay_exit"],
        )
        decision = "NO_CALL"
        reason = "NO_LAWFUL_SOURCE_BACKED_TARGET"
        replacement_authority = None
        changed = False
        active_target = next((
            target for target in surface.get("targets") or []
            if target["source"] == "ACTIVE_PARENT_EXPOSURE"
            and target["X_cents"] == prior_x
        ), None)
        active_lawful = bool(
            active_target is not None and active_target["lawful"]
        )
        if selected is not None and prior_x is None:
            changed = super()._place_or_reprice(
                state, timestamp, int(selected["X_cents"]),
                "t2_receipt_keyed_sibling_target",
                authority="CAUSAL_PAIR_HEADROOM",
                composed=True,
                allow_upward=True,
            )
            decision = "PLACE" if changed else "NO_CALL"
            reason = (
                "STRICTLY_LATER_SOURCE_BACKED_TARGET_EXPOSED"
                if changed else "TARGET_EXPRESSION_REFUSED"
            )
        elif selected is not None and prior_x is not None:
            replacement = int(selected["X_cents"])
            if replacement != prior_x:
                replacement_authority = {
                    "LIVEAIM_AIM_DEEP_SOURCE_MAPPING":
                        "LIVEAIM_SOURCE_MAPPING",
                    "CAUSAL_DIVOT_LATER_RECURRENCE":
                        "DIVOT_SOURCE_MAPPING",
                }.get(selected["source"], "CAUSAL_PAIR_HEADROOM")
                decay = {
                    "event_id": state["event_id"],
                    "candidate_id": state["candidate_id"],
                    "leg_id": state["leg_id"],
                    "timestamp": timestamp,
                    "trigger_receipt": receipt,
                    "active_X_cents": prior_x,
                    "replacement_X_cents": replacement,
                    "authority": replacement_authority,
                    "evidence_decay_condition": selected["source"],
                    "active_target_was_lawful": active_lawful,
                    "budget_or_maker_invalidation": not active_lawful,
                    "source_receipts": selected["source_receipts"],
                    "selected_target": selected,
                    "stronger_contemporaneous_support": True,
                    "inside_lawful_horizon": True,
                    "queue_surrendered_if_applied": True,
                    "metrics": None,
                    "scored": False,
                }
                state["t2_support_decay_receipts"].append(decay)
                self._t2_authorized_replacement = decay
                try:
                    changed = self._place_or_reprice(
                        state, timestamp, replacement,
                        "t2_receipt_backed_evidence_decay_reprice",
                        authority=replacement_authority,
                        composed=True,
                        allow_upward=False,
                    )
                finally:
                    self._t2_authorized_replacement = None
                decision = "REPRICE" if changed else "NO_CALL"
                reason = (
                    "NAMED_RECEIPT_BACKED_EVIDENCE_DECAY"
                    if changed else "AUTHORIZED_REPRICE_NOT_EXPRESSED"
                )
            else:
                decision = "HOLD"
                reason = "CURRENT_X_RETAINS_SOURCE_BACKED_SUPPORT"
                state["t2_support_decay_receipts"].append({
                    "event_id": state["event_id"],
                    "candidate_id": state["candidate_id"],
                    "leg_id": state["leg_id"],
                    "timestamp": timestamp,
                    "trigger_receipt": receipt,
                    "active_X_cents": prior_x,
                    "decision": "HOLD",
                    "support_rule": selected["source"],
                    "support_receipts": selected["source_receipts"],
                    "counterfactual_action_rejected": "REPRICE",
                    "queue_surrendered": False,
                    "unconditional_persistence": False,
                    "metrics": None,
                    "scored": False,
                })
        else:
            if prior_x is not None and not active_lawful and (
                surface.get("status") == "AVAILABLE"
            ):
                interval = state["order_intervals"][
                    state["active_order"]["interval_index"]
                ]
                self._close_order(
                    state, timestamp,
                    "COMBINED_BUDGET_OR_MAKER_LAW_INVALIDATED",
                    authority="CAUSAL_PAIR_HEADROOM",
                    action_reason=(
                        "receipt_backed_active_target_invalidation_"
                        "without_lawful_replacement"
                    ),
                )
                decision = "PARK"
                reason = (
                    "ACTIVE_TARGET_INVALIDATED_NO_LAWFUL_REPLACEMENT"
                )
                state["t2_support_decay_receipts"].append({
                    "event_id": state["event_id"],
                    "candidate_id": state["candidate_id"],
                    "leg_id": state["leg_id"],
                    "timestamp": timestamp,
                    "trigger_receipt": receipt,
                    "original_order_interval_id": interval[
                        "order_interval_id"
                    ],
                    "active_X_cents": prior_x,
                    "decision": "PARK",
                    "evidence_decay_condition":
                        "COMBINED_BUDGET_OR_MAKER_LAW_INVALIDATED",
                    "active_target_law": active_target,
                    "queue_surrendered": True,
                    "metrics": None,
                    "scored": False,
                })
            self._no_call(
                state, timestamp,
                "T2_MARKET_OR_TARGET_EVIDENCE_NO_CALL",
                str(surface.get("reason") or reason),
                authority="CAUSAL_PAIR_HEADROOM",
            )

        after = state.get("active_order")
        active_interval = (
            state["order_intervals"][after["interval_index"]][
                "order_interval_id"
            ] if after is not None else None
        )
        selected_x = int(after["price"]) if after is not None else None
        selection = {
            "event_id": state["event_id"],
            "candidate_id": state["candidate_id"],
            "leg_id": state["leg_id"],
            "timestamp": timestamp,
            "trigger_receipt": receipt,
            "trigger_kind": row.get("kind"),
            "first_filled_leg": self.first_filled_leg,
            "first_fill_timestamp": self.first_fill_ts,
            "d1_cents": state["headroom_d1_cents"],
            "b2_max_cents": state["headroom_b2_max_cents"],
            "fee_cents": self.policy["fee_cents"],
            "prior_X_cents": prior_x,
            "selected_target": selected,
            "selected_X_cents": selected_x,
            "decision": decision,
            "reason": reason,
            "replacement_authority": replacement_authority,
            "active_order_interval_id": active_interval,
            "new_action_fill_eligible_on_trigger_receipt": False,
            "next_evidence_must_be_strictly_later": decision in {
                "PLACE", "REPRICE"
            },
            "positive_d2_preferred": False,
            "metrics": None,
            "scored": False,
        }
        state["t2_target_selection_receipts"].append(selection)
        state["t2_episode_decisions"].append(selection)
        if (
            decision in {"PLACE", "REPRICE"}
            and selected is not None
            and selected["source"] == "CAUSAL_DIVOT_LATER_RECURRENCE"
        ):
            state["t2_divot_chronology"].append({
                **selection,
                "chronology_stage": "LATER_ACTION",
                "recognition_receipt": selected["source_receipts"][0],
                "recurrence_receipt": selected["source_receipts"][1],
            })
        self._action(
            state, timestamp,
            "t2_episode_keyed_decision",
            reason,
            authority="CAUSAL_PAIR_HEADROOM",
            trigger_receipt=receipt,
            trigger_kind=row.get("kind"),
            t2_decision=decision,
            prior_X_cents=prior_x,
            selected_X_cents=selected_x,
            source=(selected or {}).get("source"),
            active_order_interval_id=active_interval,
            strictly_later_than_first_fill=True,
            new_action_fill_eligible_on_trigger_receipt=False,
            positive_d2_preferred=False,
        )

    def _credit_fillable_at_x(self, *args: Any, **kwargs: Any) -> bool:
        state = args[0] if args else kwargs.get("state")
        before_quantity = (
            state.get("simulated_accounting_quantity")
            if isinstance(state, Mapping) else None
        )
        credited = super()._credit_fillable_at_x(*args, **kwargs)
        if (
            credited
            and isinstance(state, MutableMapping)
            and before_quantity != LOT
            and state["leg_id"] != self.first_filled_leg
        ):
            fill_ts = state.get("simulated_fill_ts")
            fill_receipt = state.get("simulated_fill_receipt")
            for chronology in reversed(state["t2_divot_chronology"]):
                if chronology.get("chronology_stage") != "LATER_ACTION":
                    continue
                if float(fill_ts) <= float(chronology["timestamp"]):
                    continue
                state["t2_divot_chronology"].append({
                    "event_id": state["event_id"],
                    "candidate_id": state["candidate_id"],
                    "leg_id": state["leg_id"],
                    "chronology_stage": "STILL_LATER_INDEPENDENT_FILL_EVIDENCE",
                    "recognition_receipt": chronology[
                        "recognition_receipt"
                    ],
                    "recurrence_receipt": chronology["recurrence_receipt"],
                    "action_receipt": chronology["trigger_receipt"],
                    "action_ts": chronology["timestamp"],
                    "fill_receipt": fill_receipt,
                    "fill_ts": fill_ts,
                    "strictly_later_than_action": True,
                    "metrics": None,
                    "scored": False,
                })
                break
        return credited

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

    def run(self, event: Mapping[str, Any]) -> dict[str, Any]:
        result = super().run(event)
        result.update({
            "schema_version": VERSION + "-candidate-event-stream-v1",
            "instrument_version": VERSION,
            "t2_variant": self.policy["t2_variant"],
            "t2_switches": dict(self.t2_switches),
            "t2_target_surfaces_by_leg": {
                state["leg_id"]: state["t2_target_surface_receipts"]
                for state in self.states
            },
            "t2_current_exposure_support_decay_by_leg": {
                state["leg_id"]: state["t2_support_decay_receipts"]
                for state in self.states
            },
            "t2_target_selection_by_leg": {
                state["leg_id"]: state["t2_target_selection_receipts"]
                for state in self.states
            },
            "t2_episode_decisions_by_leg": {
                state["leg_id"]: state["t2_episode_decisions"]
                for state in self.states
            },
            "t2_divot_chronology_by_leg": {
                state["leg_id"]: state["t2_divot_chronology"]
                for state in self.states
            },
            "t2_parent_exposure_receipts_by_leg": {
                state["leg_id"]: state["t2_parent_exposure_receipts"]
                for state in self.states
            },
            "metrics": None,
            "performance": None,
            "scored": False,
        })
        actions = result["order_stream"]
        if any(
            row.get("action") == "t2_episode_keyed_decision"
            and not row.get("strictly_later_than_first_fill")
            for row in actions
        ):
            raise T2Error("pre-first-fill T2 action")
        if any(
            decision["decision"] in {"PLACE", "REPRICE"}
            and any(
                fill.get("simulated_fill_receipt")
                == decision["trigger_receipt"]
                and fill.get("simulated_fill_ts")
                == decision["timestamp"]
                for fill in result[
                    "causal_policy_fill_state_by_leg"
                ].values()
            )
            for rows in result["t2_episode_decisions_by_leg"].values()
            for decision in rows
        ):
            raise T2Error("same-receipt T2 action/fill")
        result["order_stream_sha256"] = t1.sha256_json(actions)
        return result


Window1T2CausalDivotInstrument = T2Simulator
