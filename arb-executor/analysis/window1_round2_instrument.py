#!/usr/bin/env python3
"""Causal Round-2 Window-1 counterfactual order-stream instrument.

The module is deliberately entry-only and score-free.  Given one normalized
development event, a frozen candidate, and the frozen OS surfaces, it emits a
complete, independently timestamped stream for both legs.  It has no network,
private API, production, configuration, position, exit, settlement, DCA,
Window-2, or holdout interface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence


VERSION = "window1-round2-causal-instrument-v1"
LOT = 5.0
DEVELOPMENT_DATES = {
    f"2026-07-{day:02d}" for day in range(12, 21)
}
SEALED_HOLDOUT_DATES = {
    "2026-07-24", "2026-07-25", "2026-07-26"
}
START_POSITIVE_CLASSES = {
    "official_exact",
    "quantized_late_detection_proxy",
    "clean_causal_interval",
}
START_CENSORED_CLASSES = {
    "schedule_only",
    "live_by_only",
    "contradictory",
}


class InstrumentError(RuntimeError):
    """Raised for a contract or causal-order violation."""


@dataclass(frozen=True)
class SurfaceBundle:
    band_map: Mapping[str, Any]
    divot: Mapping[str, Any]
    drift: Mapping[str, Any]
    recut: Mapping[str, Any]
    orientation: Mapping[str, Any]
    cohort: Mapping[str, Any]


SURFACE_PATHS = {
    "band_map": ".claude/entrysurface_20260717/band_map_v1.json",
    "divot": ".claude/entrysurface_20260717/divot_tables_v1.json",
    "drift": ".claude/entrysurface_20260717/drift_surfaces_v1.json",
    "recut": ".claude/seqfloor_20260708/recut_cells.json",
    "orientation": ".claude/trendpath/ORIENT_V1.json",
    "cohort": ".claude/master_20260709/cohort.json",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_json(value: Any) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_surfaces(repo: Path) -> SurfaceBundle:
    values = {
        name: read_json(repo / relative)
        for name, relative in SURFACE_PATHS.items()
    }
    return SurfaceBundle(**values)


def load_candidate_spec(repo: Path) -> dict[str, Any]:
    path = (
        repo / "arb-executor/docs/research/window1/"
        "WINDOW1_ROUND2_CANDIDATES_V1.json"
    )
    spec = read_json(path)
    if spec.get("instrument_version") != VERSION:
        raise InstrumentError("candidate spec instrument version mismatch")
    return spec


def candidate_policy(
    spec: Mapping[str, Any], candidate_id: str,
    *, ablations: Iterable[str] = (),
) -> dict[str, Any]:
    allowed = [str(value) for value in spec.get("candidate_ids") or []]
    if candidate_id not in allowed:
        raise InstrumentError(f"candidate is not frozen: {candidate_id}")
    parts = candidate_id.split("__")
    if len(parts) != 3:
        raise InstrumentError(f"malformed candidate id: {candidate_id}")
    profile, posture_pair, response = parts
    profile_families = (
        spec.get("profiles", {}).get(profile)
    )
    posture = spec.get("posture_pairs", {}).get(posture_pair)
    if not isinstance(profile_families, list) or not isinstance(posture, dict):
        raise InstrumentError(f"candidate mapping missing: {candidate_id}")
    allowed_ablations = {
        str(value)
        for value in spec.get("predeclared_selected_candidate_ablations") or []
    }
    requested = {str(value) for value in ablations}
    if not requested.issubset(allowed_ablations):
        raise InstrumentError(
            f"unfrozen ablation(s): {sorted(requested - allowed_ablations)}"
        )
    families = set(map(str, profile_families))
    for ablation in requested:
        family = ablation.removeprefix("without_")
        families.discard(family)
    if "without_leg_specific_posture" in requested:
        posture = {"favorite": "touch", "underdog": "touch"}
    if "without_first_fill_sibling_response" in requested:
        response = "hold"
    return {
        "candidate_id": candidate_id,
        "profile": profile,
        "posture_pair": posture_pair,
        "posture_by_role": dict(posture),
        "sibling_response": response,
        "enabled_families": sorted(families),
        "ablations": sorted(requested),
        "parameters": dict(spec["common_parameters"]),
    }


def nearest_int(value: float) -> int:
    return int(math.floor(float(value) + 0.5))


def default_flat_band(
    surfaces: SurfaceBundle, category: str, anchor: float,
) -> str | None:
    category_row = surfaces.band_map.get("cats", {}).get(category)
    if not category_row or category_row.get("thin"):
        return None
    rows = [
        row for row in category_row.get("bands") or []
        if row.get("direction") == "flat"
    ]
    if not rows:
        return None
    return str(min(
        rows, key=lambda row: abs(float(row["anchor_med"]) - anchor)
    )["band"])


def recognition_bucket(anchor: float, net: float, dip: float) -> str:
    anchor_bucket = (
        "a25" if anchor <= 25 else
        "a50" if anchor <= 50 else
        "a75" if anchor <= 75 else "a95"
    )
    net_bucket = (
        "dn10" if net <= -10 else
        "dn3" if net <= -3 else
        "flat" if net < 3 else
        "up3" if net < 10 else "up10"
    )
    dip_bucket = "d0" if dip <= 2 else "d3" if dip <= 9 else "d10"
    return f"{anchor_bucket}|{net_bucket}|{dip_bucket}"


def recognized_band(
    surfaces: SurfaceBundle,
    category: str,
    anchor: float,
    net: float,
    dip: float,
) -> tuple[str | None, bool, float | None]:
    bucket = recognition_bucket(anchor, net, dip)
    cell = (
        surfaces.drift.get("recognition", {})
        .get(f"{category}|h6", {})
        .get(bucket)
    )
    if cell and float(cell.get("purity") or 0) >= 0.5:
        return str(cell["top"]), True, float(cell["purity"])
    return default_flat_band(surfaces, category, anchor), False, (
        float(cell["purity"]) if cell and cell.get("purity") is not None
        else None
    )


def divot_value(
    surfaces: SurfaceBundle, band: str | None, field: str,
) -> float | None:
    row = surfaces.divot.get("bands", {}).get(str(band))
    if not row or row.get(field) is None:
        return None
    return float(row[field])


def recut_cell(
    surfaces: SurfaceBundle, category: str, price: float,
) -> Mapping[str, Any] | None:
    return (
        surfaces.recut.get(category, {})
        .get(str(max(1, min(99, nearest_int(price)))))
    )


def cohort_depth(
    surfaces: SurfaceBundle, category: str, price: float, minimum_n: int,
) -> tuple[float | None, int]:
    zone = int(max(0, min(3, float(price) // 25)))
    rows = [
        row for row in surfaces.cohort.get("rows") or []
        if row.get("cat") == category
        and row.get("cell_edge") is not None
        and int(float(row.get("px") or 0) // 25) == zone
    ]
    if len(rows) < minimum_n:
        return None, len(rows)
    return float(statistics.median(
        float(row["cell_edge"]) for row in rows
    )), len(rows)


def external_bids(
    book: Mapping[str, Any], subtract_own: bool,
) -> list[tuple[int, float]]:
    own = {
        int(price): max(0.0, float(size))
        for price, size in (book.get("own_bid_size_by_price") or {}).items()
    }
    output = []
    for raw in book.get("bids") or []:
        price, size = int(raw[0]), max(0.0, float(raw[1]))
        external = max(0.0, size - (own.get(price, 0.0) if subtract_own else 0))
        if external > 0:
            output.append((price, external))
    output.sort(reverse=True)
    return output


def asks(book: Mapping[str, Any]) -> list[tuple[int, float]]:
    output = [
        (int(raw[0]), max(0.0, float(raw[1])))
        for raw in book.get("asks") or []
        if float(raw[1]) > 0
    ]
    output.sort()
    return output


def book_pressure_ratio(
    book: Mapping[str, Any], subtract_own: bool,
) -> float | None:
    bids = external_bids(book, subtract_own)[:5]
    ask_rows = asks(book)[:5]
    bid_size = sum(size for _, size in bids)
    ask_size = sum(size for _, size in ask_rows)
    if bid_size <= 0:
        return None
    return ask_size / bid_size


def orientation_call(
    surfaces: SurfaceBundle,
    category: str,
    states: Sequence[MutableMapping[str, Any]],
    left: float,
    checkpoint: float,
) -> dict[str, Any]:
    by_role = {str(state["role"]): state for state in states}
    dog, leader = by_role.get("underdog"), by_role.get("favorite")
    if dog is None or leader is None:
        return {"available": False, "reason": "role_mapping_missing"}

    def stats(state: Mapping[str, Any]) -> dict[str, float] | None:
        rows = [
            row for row in state["nonself_prints"]
            if left <= float(row["ts"]) <= checkpoint
        ]
        if len(rows) < 3:
            return None
        prices = [float(row["price"]) for row in rows]
        return {
            "median": float(statistics.median(prices)),
            "last": prices[-1],
            "low": min(prices),
            "high": max(prices),
            "volume": sum(float(row["size"]) for row in rows),
        }

    dog_stats, leader_stats = stats(dog), stats(leader)
    if dog_stats is None or leader_stats is None:
        return {
            "available": False,
            "reason": "first_hour_true_print_support_missing",
        }
    drift = dog_stats["last"] - dog_stats["median"]
    f1 = 1 if drift >= 1 else -1 if drift <= -1 else 0
    span = max(1.0, dog_stats["high"] - dog_stats["low"])
    position = (dog_stats["last"] - dog_stats["low"]) / span
    f2 = "lo" if position < 0.33 else "mid" if position < 0.67 else "hi"
    total = dog_stats["volume"] + leader_stats["volume"]
    share = dog_stats["volume"] / total if total else 0.5
    f3 = "lo" if share < 0.4 else "mid" if share < 0.6 else "hi"
    bucket = f"{f1}|{f2}|{f3}"
    cell = (
        surfaces.orientation.get("cats", {})
        .get(category, {}).get(bucket)
    )
    if not cell or int(cell.get("n") or 0) < 10:
        return {
            "available": False,
            "reason": "orientation_bucket_below_frozen_min_n",
            "bucket": bucket,
        }
    rate = float(cell["dog_rise_rate"])
    called_role = (
        "underdog" if rate >= 0.65 else
        "favorite" if rate <= 0.35 else None
    )
    return {
        "available": True,
        "bucket": bucket,
        "n": int(cell["n"]),
        "dog_rise_rate": rate,
        "called_role": called_role,
        "no_call": called_role is None,
    }


def _action(
    state: MutableMapping[str, Any],
    timestamp: float,
    action_type: str,
    reason: str,
    **values: Any,
) -> dict[str, Any]:
    row = {
        "event_id": state["event_id"],
        "candidate_id": state["candidate_id"],
        "leg_id": state["leg_id"],
        "ticker": state["ticker"],
        "ts": float(timestamp),
        "action": action_type,
        "reason": reason,
        **values,
    }
    if state["actions"] and float(timestamp) < float(state["actions"][-1]["ts"]):
        raise InstrumentError("per-leg action clock moved backward")
    state["actions"].append(row)
    return row


class CausalInstrument:
    """Stateful two-leg causal stream generator."""

    def __init__(
        self,
        surfaces: SurfaceBundle,
        policy: Mapping[str, Any],
    ) -> None:
        self.surfaces = surfaces
        self.policy = dict(policy)
        self.families = set(map(str, policy["enabled_families"]))
        self.parameters = dict(policy["parameters"])
        self.states: list[MutableMapping[str, Any]] = []
        self.event: Mapping[str, Any] = {}
        self.left = 0.0
        self.cutoff = 0.0

    def _validate_event(self, event: Mapping[str, Any]) -> None:
        event_date = str(event.get("event_date"))
        if event_date in SEALED_HOLDOUT_DATES:
            raise InstrumentError("sealed holdout event refused")
        if event_date not in DEVELOPMENT_DATES:
            raise InstrumentError("event date is outside frozen development dates")
        legs = list(event.get("legs") or [])
        if len(legs) != 2:
            raise InstrumentError("pair law requires exactly two legs")
        source_class = str(event.get("start_source_class"))
        cutoff = event.get("strict_positive_cutoff_ts")
        if source_class in START_CENSORED_CLASSES and cutoff is not None:
            raise InstrumentError(
                f"{source_class} may not create a positive cutoff"
            )
        if source_class in START_POSITIVE_CLASSES:
            if cutoff is None:
                raise InstrumentError("positive-capable start lacks cutoff")
            guard = event.get("start_guard")
            if not isinstance(guard, dict) or not guard.get("guard_id"):
                raise InstrumentError("positive-capable start lacks guard")
        if source_class not in START_POSITIVE_CLASSES | START_CENSORED_CLASSES:
            raise InstrumentError(f"unknown start source class: {source_class}")

    def _new_state(
        self, event: Mapping[str, Any], leg: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        availability = dict(leg.get("feature_availability") or {})
        required = []
        if "true_print_flow" in self.families:
            required.append("true_prints")
        if "bbo_top5_pressure" in self.families:
            required.append("top5")
        if "own_order_contribution_subtraction" in self.families:
            required.append("own_order_fingerprints")
        missing = [name for name in required if availability.get(name) is not True]
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
            "current_book": None,
            "birth_anchor": None,
            "birth_band": None,
            "current_band": None,
            "recut_depth": None,
            "recut_timing_minutes": None,
            "divot_depth": None,
            "cohort_depth": None,
            "cohort_n": 0,
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
            "walk_distance_cents": 0,
            "last_walk_evidence_index": 0,
            "terminal": None,
            "feature_censored": bool(missing),
        }
        _action(state, self.left, "leg_open", "pair_stream_initialized")
        if missing:
            _action(
                state,
                self.left,
                "feature_censor",
                "required_feature_absent",
                missing_features=missing,
            )
        return state

    def _subtract_own(self) -> bool:
        return "own_order_contribution_subtraction" in self.families

    def _initialize_birth(
        self, state: MutableMapping[str, Any], timestamp: float,
    ) -> None:
        book = state["current_book"]
        bid_rows = external_bids(book, self._subtract_own())
        if not bid_rows:
            state["feature_censored"] = True
            state["missing_features"].append("external_bbo_after_own_subtraction")
            _action(
                state, timestamp, "feature_censor",
                "no_external_bid_after_own_subtraction",
            )
            return
        anchor = float(bid_rows[0][0])
        state["birth_anchor"] = anchor
        band = default_flat_band(
            self.surfaces, str(self.event["category"]), anchor
        )
        state["birth_band"] = band
        state["current_band"] = band
        state["divot_depth"] = divot_value(
            self.surfaces, band, "depth_p50"
        )
        cell = recut_cell(
            self.surfaces, str(self.event["category"]), anchor
        )
        if cell is None or cell.get("edge_p50") is None:
            state["feature_censored"] = True
            state["missing_features"].append("dynamic_recut_cell")
            _action(
                state, timestamp, "feature_censor",
                "dynamic_recut_cell_unavailable",
                anchor_cents=anchor,
            )
            return
        state["recut_depth"] = float(cell["edge_p50"])
        state["recut_timing_minutes"] = float(cell["t_deep_p50"])
        if "asynchronous_divot_timing" in self.families:
            state["eligible_ts"] = max(
                self.left,
                min(
                    self.cutoff,
                    self.cutoff + float(cell["t_deep_p50"]) * 60.0,
                ),
            )
        minimum_n = int(self.parameters["cohort_minimum_n"])
        cohort, cohort_n = cohort_depth(
            self.surfaces,
            str(self.event["category"]),
            anchor,
            minimum_n,
        )
        state["cohort_n"] = cohort_n
        if "cohort_steering" in self.families:
            if cohort is None:
                state["feature_censored"] = True
                state["missing_features"].append("cohort_cell_n30")
                _action(
                    state, timestamp, "feature_censor",
                    "cohort_cell_below_frozen_min_n",
                    cohort_n=cohort_n,
                )
            elif abs(cohort - float(state["recut_depth"])) >= float(
                self.parameters["cohort_minimum_reaim_delta_cents"]
            ):
                state["cohort_depth"] = cohort
                _action(
                    state, timestamp, "cohort_steer",
                    "frozen_cohort_n30_delta_ge_2",
                    cohort_n=cohort_n,
                    depth_cents=cohort,
                )
        _action(
            state,
            timestamp,
            "macro_bind",
            "birth_cell_and_independent_timing",
            anchor_cents=anchor,
            birth_band=band,
            divot_depth_cents=state["divot_depth"],
            recut_depth_cents=state["recut_depth"],
            recut_timing_minutes=state["recut_timing_minutes"],
            eligible_ts=state["eligible_ts"],
        )

    def _effective_depth(self, state: Mapping[str, Any]) -> float:
        values = [
            float(value)
            for value in (state.get("divot_depth"), state.get("recut_depth"))
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
            p90 = divot_value(
                self.surfaces,
                str(state.get("current_band")),
                "depth_p90",
            )
            if p90 is not None:
                depth = max(depth, p90)
        if "bbo_top5_pressure" in self.families:
            ratio = book_pressure_ratio(
                state["current_book"], self._subtract_own()
            )
            if ratio is not None and ratio >= float(
                self.parameters["top5_ask_over_external_bid_threshold"]
            ):
                depth += float(
                    self.parameters["top5_pressure_extra_depth_cents"]
                )
        return max(0.0, depth)

    def _posture(self, state: Mapping[str, Any]) -> str:
        return str(self.policy["posture_by_role"][str(state["role"])])

    def _target_price(self, state: Mapping[str, Any]) -> int:
        book = state["current_book"]
        bid_rows = external_bids(book, self._subtract_own())
        ask_rows = asks(book)
        if not bid_rows or not ask_rows:
            raise InstrumentError("BBO unavailable at decision")
        external_bid = int(bid_rows[0][0])
        maker_ceiling = int(ask_rows[0][0]) - 1
        depth = self._effective_depth(state)
        macro_target = external_bid - nearest_int(depth)
        posture = self._posture(state)
        if posture == "touch":
            target = external_bid
        elif posture in {"join", "walk", "park"}:
            # Expression law: a fitted target at/below the non-self chain
            # rests at its target; above-chain expression improves by 1c only.
            target = (
                macro_target
                if macro_target <= external_bid
                else external_bid + 1
            )
        else:
            raise InstrumentError(f"unknown posture: {posture}")
        target += int(state.get("sibling_bias_cents") or 0)
        return max(1, min(maker_ceiling, int(target)))

    def _queue_ahead(self, state: Mapping[str, Any], price: int) -> float:
        for level, size in external_bids(
            state["current_book"], self._subtract_own()
        ):
            if level == price:
                return float(size)
        return 0.0

    def _place(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
        *,
        action_type: str = "place",
    ) -> None:
        if state["feature_censored"] or state["quantity"] >= LOT:
            return
        price = self._target_price(state)
        order = {
            "price": price,
            "remaining": LOT - float(state["quantity"]),
            "queue_ahead": self._queue_ahead(state, price),
            "placed_ts": float(timestamp),
        }
        state["active_order"] = order
        state["placed_any"] = True
        _action(
            state,
            timestamp,
            action_type,
            reason,
            price_cents=price,
            quantity=order["remaining"],
            queue_ahead=order["queue_ahead"],
            posture=self._posture(state),
            effective_depth_cents=self._effective_depth(state),
        )

    def _cancel(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
    ) -> None:
        order = state.get("active_order")
        if order is None:
            return
        _action(
            state,
            timestamp,
            "cancel",
            reason,
            price_cents=order["price"],
            remaining_quantity=order["remaining"],
        )
        state["active_order"] = None

    def _reprice(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
    ) -> None:
        order = state.get("active_order")
        if order is None or state["feature_censored"]:
            return
        target = self._target_price(state)
        if target == int(order["price"]):
            return
        self._cancel(state, timestamp, reason + "_cancel")
        self._place(
            state, timestamp, reason, action_type="reprice"
        )

    def _flow_count(
        self, state: Mapping[str, Any], timestamp: float,
    ) -> int:
        return sum(
            1 for row in state["nonself_prints"]
            if timestamp - 1800 <= float(row["ts"]) <= timestamp
            and str(row.get("taker_side")) == "no"
            and float(row.get("size") or 0) > 0
        )

    def _flow_confirmed(
        self, state: Mapping[str, Any], timestamp: float,
    ) -> bool:
        if "true_print_flow" not in self.families:
            return True
        minimums = self.parameters["flow_minimum_nonself_prints_30m"]
        required = int(minimums[str(self.event["category"])])
        return self._flow_count(state, timestamp) >= required

    def _recent_divot(
        self, state: Mapping[str, Any], timestamp: float,
    ) -> bool:
        signal = state.get("divot_signal_ts")
        if signal is None:
            return False
        duration = divot_value(
            self.surfaces, str(state.get("current_band")), "dur_p50_s"
        )
        maximum_age = max(1.0, float(duration or 300.0))
        return 0 <= timestamp - float(signal) <= maximum_age

    def _maybe_place(
        self,
        state: MutableMapping[str, Any],
        timestamp: float,
        reason: str,
    ) -> None:
        if (
            state["active_order"] is not None
            or state["quantity"] >= LOT
            or state["feature_censored"]
            or state["current_book"] is None
            or timestamp < float(state["eligible_ts"])
        ):
            return
        posture = self._posture(state)
        if not self._flow_confirmed(state, timestamp):
            return
        if posture in {"park", "walk"} and not self._recent_divot(
            state, timestamp
        ):
            return
        self._place(state, timestamp, reason)

    def _detect_divot(
        self,
        state: MutableMapping[str, Any],
        print_row: Mapping[str, Any],
    ) -> None:
        if str(print_row.get("taker_side")) != "no":
            return
        timestamp = float(print_row["ts"])
        prior = [
            row for row in state["nonself_prints"]
            if timestamp - float(
                self.parameters["divot_definition"]["trailing_median_seconds"]
            ) <= float(row["ts"]) < timestamp
        ]
        minimum = int(
            self.parameters["divot_definition"]["minimum_prior_nonself_prints"]
        )
        if len(prior) < minimum or state["current_book"] is None:
            return
        median = float(statistics.median(
            float(row["price"]) for row in prior
        ))
        depth = median - float(print_row["price"])
        if depth < float(
            self.parameters["divot_definition"]["minimum_depth_cents"]
        ):
            return
        ask_rows = asks(state["current_book"])
        if not ask_rows:
            return
        ask_hold = float(ask_rows[0][0]) >= median - float(
            self.parameters["divot_definition"]["ask_hold_within_cents"]
        )
        if not ask_hold:
            return
        state["divot_signal_ts"] = timestamp
        state["divot_signal_median"] = median
        _action(
            state,
            timestamp,
            "micro_divot",
            "nonself_print_below_trailing_median_with_ask_hold",
            print_price_cents=float(print_row["price"]),
            trailing_median_cents=median,
            depth_cents=depth,
        )

    def _maybe_walk(
        self, state: MutableMapping[str, Any], timestamp: float,
    ) -> None:
        if (
            "nonself_one_cent_walk" not in self.families
            or self._posture(state) != "walk"
            or state["active_order"] is None
        ):
            return
        cap = int(
            self.parameters["walk"]["maximum_journey_cents"][
                str(self.event["category"])
            ]
        )
        if int(state["walk_distance_cents"]) >= cap:
            return
        rows = state["nonself_prints"]
        start = int(state["last_walk_evidence_index"])
        candidates = [
            row for row in rows[start:]
            if str(row.get("taker_side")) == "no"
        ]
        needed = int(self.parameters["walk"]["minimum_chain_prints"])
        if len(candidates) < needed:
            return
        chain = candidates[-needed:]
        prices = [float(row["price"]) for row in chain]
        current = int(state["active_order"]["price"])
        if (
            prices != sorted(prices)
            or min(prices) < current + 1
        ):
            return
        bid_rows = external_bids(
            state["current_book"], self._subtract_own()
        )
        ask_rows = asks(state["current_book"])
        if not bid_rows or not ask_rows:
            return
        target = min(
            current + int(self.parameters["walk"]["step_cents"]),
            int(bid_rows[0][0]) + 1,
            int(ask_rows[0][0]) - 1,
        )
        if target != current + 1:
            return
        self._cancel(state, timestamp, "verified_nonself_chain_walk_cancel")
        old_bias = int(state["sibling_bias_cents"])
        old_depth = self._effective_depth(state)
        # Force exactly the one-cent expression for this repost only.
        state["sibling_bias_cents"] = (
            target
            - (
                int(bid_rows[0][0]) - nearest_int(old_depth)
            )
        )
        self._place(
            state,
            timestamp,
            "verified_nonself_chain_exact_one_cent",
            action_type="reprice",
        )
        state["sibling_bias_cents"] = old_bias
        state["walk_distance_cents"] = (
            int(state["walk_distance_cents"]) + 1
        )
        state["last_walk_evidence_index"] = len(rows)

    def _fill_from_print(
        self,
        state: MutableMapping[str, Any],
        print_row: Mapping[str, Any],
    ) -> bool:
        order = state.get("active_order")
        if order is None or str(print_row.get("taker_side")) != "no":
            return False
        price = float(print_row["price"])
        size = max(0.0, float(print_row.get("size") or 0))
        if size <= 0 or price > float(order["price"]):
            return False
        fillable = size
        if price == float(order["price"]):
            debit = min(fillable, float(order["queue_ahead"]))
            order["queue_ahead"] = float(order["queue_ahead"]) - debit
            fillable -= debit
        if fillable <= 0:
            return False
        filled = min(fillable, float(order["remaining"]))
        order["remaining"] = float(order["remaining"]) - filled
        state["quantity"] = float(state["quantity"]) + filled
        state["cost"] = float(state["cost"]) + filled * float(order["price"])
        completed = state["quantity"] >= LOT - 1e-9
        _action(
            state,
            float(print_row["ts"]),
            "fill_observed",
            "public_nonself_true_print",
            order_price_cents=int(order["price"]),
            print_price_cents=price,
            fill_quantity=filled,
            cumulative_quantity=state["quantity"],
            complete=completed,
            trade_id=print_row.get("trade_id"),
        )
        if completed:
            state["active_order"] = None
        return completed

    def _sibling_response(
        self, filled_state: MutableMapping[str, Any], timestamp: float,
    ) -> None:
        sibling = next(
            state for state in self.states if state is not filled_state
        )
        if sibling["quantity"] >= LOT or sibling["feature_censored"]:
            return
        response = str(self.policy["sibling_response"])
        if response == "hold":
            _action(
                sibling,
                timestamp,
                "sibling_hold",
                "first_leg_filled_other_leg_independently_held",
                first_filled_leg=filled_state["leg_id"],
                active_order=sibling["active_order"] is not None,
            )
            return
        if response != "reaim":
            raise InstrumentError(f"unknown sibling response: {response}")
        sibling["sibling_bias_cents"] = int(
            self.parameters["first_fill_sibling_reaim_cents"]
        )
        _action(
            sibling,
            timestamp,
            "sibling_reaim_decision",
            "first_leg_fill_is_causal_information",
            first_filled_leg=filled_state["leg_id"],
            reaim_cents=sibling["sibling_bias_cents"],
        )
        if sibling["active_order"] is not None:
            self._reprice(
                sibling, timestamp, "first_fill_sibling_reaim"
            )
        else:
            self._maybe_place(
                sibling, timestamp, "first_fill_sibling_reaim"
            )

    def _on_book(
        self, state: MutableMapping[str, Any], row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
        book = dict(row)
        book["bids"] = [list(value) for value in row.get("bids") or []]
        book["asks"] = [list(value) for value in row.get("asks") or []]
        state["current_book"] = book
        bid_rows = external_bids(book, self._subtract_own())
        if not bid_rows:
            if state["birth_anchor"] is None:
                self._initialize_birth(state, timestamp)
            return
        state["books"].append({
            "ts": timestamp,
            "best_external_bid": float(bid_rows[0][0]),
        })
        if state["birth_anchor"] is None:
            self._initialize_birth(state, timestamp)
        elif "pair_divot_recut" in self.families:
            cell = recut_cell(
                self.surfaces,
                str(self.event["category"]),
                float(bid_rows[0][0]),
            )
            if cell and cell.get("edge_p50") is not None:
                prior = state["recut_depth"]
                current = float(cell["edge_p50"])
                if prior is None or current != float(prior):
                    state["recut_depth"] = current
                    _action(
                        state,
                        timestamp,
                        "pair_recut",
                        "leg_specific_causal_book_cell_change",
                        prior_depth_cents=prior,
                        recut_depth_cents=current,
                    )
                    self._reprice(
                        state, timestamp, "leg_specific_pair_recut"
                    )
        self._maybe_place(state, timestamp, "eligible_causal_book")

    def _on_print(
        self, state: MutableMapping[str, Any], row: Mapping[str, Any],
    ) -> None:
        timestamp = float(row["ts"])
        if row.get("own_order_fingerprint") is True:
            _action(
                state,
                timestamp,
                "contributed_volume_excluded",
                "own_fingerprint_never_confirms_market",
                trade_id=row.get("trade_id"),
                size=float(row.get("size") or 0),
            )
            return
        completed = self._fill_from_print(state, row)
        self._detect_divot(state, row)
        state["nonself_prints"].append(dict(row))
        if completed:
            self._sibling_response(state, timestamp)
        self._maybe_walk(state, timestamp)
        self._maybe_place(state, timestamp, "causal_true_print_micro_trigger")

    def _on_orientation(self, timestamp: float) -> None:
        if "causal_orientation" not in self.families:
            return
        call = orientation_call(
            self.surfaces,
            str(self.event["category"]),
            self.states,
            self.left,
            timestamp,
        )
        for state in self.states:
            state["orientation"] = call
            _action(
                state,
                timestamp,
                "orientation_observed",
                "first_hour_causal_orientation_checkpoint",
                orientation=call,
            )
            self._reprice(state, timestamp, "causal_orientation_reaim")

    def _on_recognition(self, timestamp: float) -> None:
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
            anchor = float(state["birth_anchor"])
            prices = [float(row["best_external_bid"]) for row in history]
            current = prices[-1]
            net = current - anchor
            dip = max(0.0, anchor - min(prices))
            band, used, purity = recognized_band(
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
            _action(
                state,
                timestamp,
                "drift_recognition_observed",
                "T6_checkpoint_uses_history_through_decision_only",
                recognition=state["recognition"],
            )
            if used:
                state["current_band"] = band
                field = (
                    "depth_p90"
                    if (
                        state.get("orientation") or {}
                    ).get("called_role") == state["role"]
                    else "depth_p50"
                )
                state["recognition_depth"] = divot_value(
                    self.surfaces, band, field
                )
                self._reprice(
                    state, timestamp, "causal_T6_drift_recognition"
                )

    def _terminalize(self, state: MutableMapping[str, Any]) -> None:
        if state["active_order"] is not None:
            self._cancel(state, self.cutoff, "lawful_window_end")
        quantity = float(state["quantity"])
        if state["feature_censored"]:
            terminal = "censored_feature"
        elif quantity >= LOT - 1e-9:
            terminal = "filled_exact_five"
        elif quantity > 0:
            terminal = "partial_fill"
        elif state["placed_any"]:
            terminal = "genuine_zero_fill"
        else:
            terminal = "no_eligible_micro_trigger"
        state["terminal"] = terminal
        _action(
            state,
            self.cutoff,
            "terminal",
            terminal,
            quantity=quantity,
            vwap_cents=(
                float(state["cost"]) / quantity if quantity > 0 else None
            ),
            feature_censors=sorted(set(state["missing_features"])),
        )

    def _censored_start_result(
        self, event: Mapping[str, Any],
    ) -> dict[str, Any]:
        timestamp = float(event.get("left_ts") or 0)
        states = []
        for leg in event["legs"]:
            state: MutableMapping[str, Any] = {
                "event_id": str(event["event_id"]),
                "candidate_id": str(self.policy["candidate_id"]),
                "leg_id": str(leg["leg_id"]),
                "ticker": str(leg["ticker"]),
                "actions": [],
            }
            _action(
                state, timestamp, "leg_open",
                "pair_stream_initialized_without_positive_start",
            )
            _action(
                state, timestamp, "terminal",
                "censored_start_boundary",
                quantity=0.0,
                feature_censors=[],
            )
            states.append(state)
        return self._result(event, states, "censored_start_boundary")

    def _zero_length_result(
        self, event: Mapping[str, Any],
    ) -> dict[str, Any]:
        states = []
        for leg in event["legs"]:
            state: MutableMapping[str, Any] = {
                "event_id": str(event["event_id"]),
                "candidate_id": str(self.policy["candidate_id"]),
                "leg_id": str(leg["leg_id"]),
                "ticker": str(leg["ticker"]),
                "actions": [],
            }
            _action(
                state, self.left, "leg_open",
                "pair_stream_initialized_zero_length",
            )
            _action(
                state, self.left, "terminal",
                "zero_length_window1_opportunity",
                quantity=0.0,
                feature_censors=[],
            )
            states.append(state)
        return self._result(
            event, states, "zero_length_window1_opportunity"
        )

    def _result(
        self,
        event: Mapping[str, Any],
        states: Sequence[Mapping[str, Any]],
        event_terminal: str,
    ) -> dict[str, Any]:
        streams = {
            str(state["leg_id"]): list(state["actions"])
            for state in states
        }
        flattened = sorted(
            [row for rows in streams.values() for row in rows],
            key=lambda row: (
                float(row["ts"]), str(row["leg_id"]), str(row["action"])
            ),
        )
        return {
            "schema_version": VERSION + "-order-stream-v1",
            "instrument_version": VERSION,
            "candidate_id": self.policy["candidate_id"],
            "ablations": list(self.policy.get("ablations") or []),
            "event_id": event["event_id"],
            "event_date": event["event_date"],
            "start_source_class": event["start_source_class"],
            "start_guard": event.get("start_guard"),
            "event_terminal": event_terminal,
            "leg_streams": streams,
            "order_stream": flattened,
            "scored": False,
            "metrics": None,
            "holdout_queried": False,
            "stream_sha256": sha256_json(flattened),
        }

    def run(self, event: Mapping[str, Any]) -> dict[str, Any]:
        self._validate_event(event)
        self.event = event
        self.left = float(event["left_ts"])
        source_class = str(event["start_source_class"])
        if source_class in START_CENSORED_CLASSES:
            return self._censored_start_result(event)
        self.cutoff = float(event["strict_positive_cutoff_ts"])
        if self.cutoff <= self.left:
            return self._zero_length_result(event)
        self.states = [
            self._new_state(event, leg) for leg in event["legs"]
        ]
        state_by_leg = {
            str(state["leg_id"]): state for state in self.states
        }
        timeline: list[tuple[float, int, str, Mapping[str, Any] | None]] = []
        for leg in event["legs"]:
            leg_id = str(leg["leg_id"])
            for row in leg.get("observations") or []:
                timestamp = float(row["ts"])
                kind = str(row["kind"])
                priority = 0 if kind == "book" else 1 if kind == "print" else 9
                if priority == 9:
                    raise InstrumentError(f"unknown observation kind: {kind}")
                timeline.append((timestamp, priority, leg_id, row))
        orientation_at = self.left + float(
            self.parameters["orientation_checkpoint_seconds_after_left"]
        )
        recognition_at = self.left + float(
            self.parameters["recognition_checkpoint_seconds_after_left"]
        )
        timeline.extend([
            (orientation_at, 2, "*orientation", None),
            (recognition_at, 3, "*recognition", None),
        ])
        timeline.sort(key=lambda value: (value[0], value[1], value[2]))
        for timestamp, _, key, row in timeline:
            if timestamp < self.left or timestamp >= self.cutoff:
                continue
            if key == "*orientation":
                self._on_orientation(timestamp)
            elif key == "*recognition":
                self._on_recognition(timestamp)
            else:
                state = state_by_leg[key]
                if row is None:
                    raise InstrumentError("missing timeline observation")
                if row["kind"] == "book":
                    self._on_book(state, row)
                else:
                    self._on_print(state, row)
        for state in self.states:
            self._terminalize(state)
        event_terminal = (
            "censored_feature"
            if any(state["feature_censored"] for state in self.states)
            else "complete_counterfactual_stream"
        )
        return self._result(event, self.states, event_terminal)


def run_event(
    repo: Path,
    event: Mapping[str, Any],
    candidate_id: str,
    *,
    ablations: Iterable[str] = (),
    surfaces: SurfaceBundle | None = None,
) -> dict[str, Any]:
    spec = load_candidate_spec(repo)
    policy = candidate_policy(spec, candidate_id, ablations=ablations)
    bundle = surfaces if surfaces is not None else load_surfaces(repo)
    return CausalInstrument(bundle, policy).run(event)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit one score-free Round-2 counterfactual order stream."
    )
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--event-json", type=Path, required=True)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--ablation", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    event = read_json(args.event_json.resolve())
    result = run_event(
        repo, event, args.candidate_id, ablations=args.ablation
    )
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
