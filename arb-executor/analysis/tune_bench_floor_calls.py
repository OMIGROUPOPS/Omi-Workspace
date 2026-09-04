#!/usr/bin/env python3
"""Walk-forward tune bench for pair shape, floor, timing, and conduct.

This script is deliberately read-only with respect to its inputs.  It writes
only the four requested artifacts under analysis/tune_bench.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import numpy as np


EXPECTED_LIBRARY_SHA256 = "019d84b0500a79c5d762d95ae7f481c3ae9a5bd5f0818f81aea9207a27fdd76e"
PHASES = (0.10, 0.25, 0.50, 0.75)
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90)
POOL_SIZES = (50, 200, 800, "all")
CATEGORIES = ("ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL")
SERIES = (
    "favorite_last",
    "favorite_bid",
    "favorite_ask",
    "underdog_last",
    "underdog_bid",
    "underdog_ask",
    "favorite_plus_underdog_last",
)
SIDE_SERIES = {"favorite": (0, 1, 2), "underdog": (3, 4, 5)}
FAMILIES = ("HOLD", "RISE", "FADE", "DIP_RECOVER", "OTHER")
NAMED_SUFFIXES = ("ALTGAS", "GIUBAR", "URSPAL", "LAJSVA", "DANPRA")
NEW_YORK = ZoneInfo("America/New_York")
STORE_SILENT_SIMILARITY_REASON = (
    "STORE_SILENT: the licensed RANGE_OVERLAP_LIBRARY rows do not contain the "
    "eleven-scalar similarity vectors. The live builder joins those vectors from "
    "other corpus stores, which ORDER 4 did not license as bench inputs; no vector "
    "was reconstructed or substituted."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    os.replace(temporary, path)


def finite(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def event_date(event_id: str) -> str | None:
    match = re.search(r"-(\d{2}[A-Z]{3}\d{2})", event_id)
    return match.group(1) if match else None


def inverse_weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float | None:
    valid = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not np.any(valid):
        return None
    v = values[valid]
    w = weights[valid]
    order = np.lexsort((np.arange(v.size), v))
    v = v[order]
    w = w[order]
    target = float(w.sum()) * q
    index = int(np.searchsorted(np.cumsum(w), target, side="left"))
    return float(v[min(index, v.size - 1)])


def distribution(values: Iterable[float]) -> dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    array = array[np.isfinite(array)]
    if not array.size:
        return {"count": 0, "min": None, "q10": None, "q25": None, "q50": None, "q75": None, "q90": None, "max": None, "mean": None}
    weights = np.ones(array.size, dtype=np.float64)
    return {
        "count": int(array.size),
        "min": float(array.min()),
        "q10": inverse_weighted_quantile(array, weights, 0.10),
        "q25": inverse_weighted_quantile(array, weights, 0.25),
        "q50": inverse_weighted_quantile(array, weights, 0.50),
        "q75": inverse_weighted_quantile(array, weights, 0.75),
        "q90": inverse_weighted_quantile(array, weights, 0.90),
        "max": float(array.max()),
        "mean": float(array.mean()),
    }


@dataclass(slots=True)
class Leg:
    leg_id: str
    anchor: int
    fractions: np.ndarray
    values: np.ndarray
    lows: np.ndarray
    highs: np.ndarray
    volumes: np.ndarray
    true_trade_fractions: np.ndarray

    def positions(self, fractions: np.ndarray) -> np.ndarray:
        return np.searchsorted(self.fractions, fractions, side="right") - 1

    def sample_values(self, fractions: np.ndarray) -> np.ndarray:
        positions = self.positions(fractions)
        result = np.full((len(fractions), 3), np.nan, dtype=np.float32)
        valid = positions >= 0
        if np.any(valid):
            result[valid] = self.values[positions[valid]]
        return result

    def point_at(self, fraction: float) -> int:
        return int(np.searchsorted(self.fractions, fraction, side="right") - 1)

    def has_true_trade_before_and_after(self, fraction: float) -> tuple[bool, bool]:
        return bool(np.any(self.true_trade_fractions <= fraction)), bool(np.any(self.true_trade_fractions > fraction))


@dataclass(slots=True)
class Pair:
    event_id: str
    date: str | None
    category: str
    formation: float
    bell: float
    favorite: Leg
    underdog: Leg
    families: dict[float, tuple[str, str]] = field(default_factory=dict)

    def grid(self, fraction: float, remainder: bool) -> np.ndarray:
        if remainder:
            left = self.favorite.fractions[self.favorite.fractions > fraction]
            right = self.underdog.fractions[self.underdog.fractions > fraction]
        else:
            left = self.favorite.fractions[self.favorite.fractions <= fraction]
            right = self.underdog.fractions[self.underdog.fractions <= fraction]
        return np.union1d(left, right)

    def levels(self, fractions: np.ndarray) -> np.ndarray:
        favorite = self.favorite.sample_values(fractions)
        underdog = self.underdog.sample_values(fractions)
        result = np.full((len(fractions), 7), np.nan, dtype=np.float32)
        result[:, :3] = favorite
        result[:, 3:6] = underdog
        result[:, 6] = favorite[:, 0] + underdog[:, 0]
        return result

    def baseline(self, fraction: float) -> np.ndarray:
        return self.levels(np.asarray([fraction], dtype=np.float64))[0]

    def scorable(self, fraction: float) -> tuple[bool, dict[str, bool]]:
        fav_before, fav_after = self.favorite.has_true_trade_before_and_after(fraction)
        dog_before, dog_after = self.underdog.has_true_trade_before_and_after(fraction)
        detail = {
            "favorite_trade_at_or_before": fav_before,
            "favorite_trade_after": fav_after,
            "underdog_trade_at_or_before": dog_before,
            "underdog_trade_after": dog_after,
        }
        return all(detail.values()), detail


def leg_from_row(row: dict[str, Any]) -> Leg:
    path = row["path"]
    fractions = np.asarray([point["window_fraction"] for point in path], dtype=np.float64)
    values = np.asarray(
        [[point.get("last_cents"), point.get("bid_cents"), point.get("ask_cents")] for point in path],
        dtype=np.float32,
    )
    lows = np.asarray([np.nan if point.get("seen_true_trade_low_cents") is None else point["seen_true_trade_low_cents"] for point in path], dtype=np.float32)
    highs = np.asarray([np.nan if point.get("seen_true_trade_high_cents") is None else point["seen_true_trade_high_cents"] for point in path], dtype=np.float32)
    volumes = np.asarray([point.get("volume_cum", 0) for point in path], dtype=np.float64)
    trade = np.zeros(len(path), dtype=bool)
    if len(path):
        trade[0] = bool(volumes[0] > 0 or np.isfinite(highs[0]))
    if len(path) > 1:
        trade[1:] = volumes[1:] > volumes[:-1]
    return Leg(
        leg_id=row["leg_id"],
        anchor=int(row["anchor_cents"]),
        fractions=fractions,
        values=values,
        lows=lows,
        highs=highs,
        volumes=volumes,
        true_trade_fractions=fractions[trade],
    )


def load_library(path: Path) -> tuple[list[Pair], dict[str, Any]]:
    pending: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                row = json.loads(line)
                pending[row["event_id"]].append(row)
    pairs: list[Pair] = []
    ties = Counter()
    malformed = Counter()
    for event_id in sorted(pending):
        rows = pending[event_id]
        category = rows[0].get("category", "UNKNOWN")
        if len(rows) != 2:
            malformed[category] += 1
            continue
        rows.sort(key=lambda row: (-int(row["anchor_cents"]), row["leg_id"]))
        if int(rows[0]["anchor_cents"]) == int(rows[1]["anchor_cents"]):
            ties[category] += 1
            continue
        pairs.append(
            Pair(
                event_id=event_id,
                date=event_date(event_id),
                category=category,
                formation=float(max(row["formation_end_epoch"] for row in rows)),
                bell=float(max(row["bell_epoch"] for row in rows)),
                favorite=leg_from_row(rows[0]),
                underdog=leg_from_row(rows[1]),
            )
        )
    pairs.sort(key=lambda pair: pair.event_id)
    return pairs, {
        "input_pair_events": len(pending),
        "oriented_pair_events": len(pairs),
        "equal_anchor_store_silent": dict(sorted(ties.items())),
        "malformed_pair_store_silent": dict(sorted(malformed.items())),
    }


def side_family(leg: Leg, fraction: float) -> str:
    position = leg.point_at(fraction)
    if position < 0 or not np.isfinite(leg.values[position, 0]):
        return "OTHER"
    now = float(leg.values[position, 0])
    remainder = leg.values[leg.fractions > fraction, 0]
    remainder = remainder[np.isfinite(remainder)]
    if not remainder.size:
        return "OTHER"
    floor = float(remainder.min())
    dip = now - floor
    net = float(remainder[-1]) - now
    floor_position = int(np.flatnonzero(remainder == floor)[0])
    never_above_after_dip = bool(np.all(remainder[floor_position:] <= now))
    if dip <= 1 and net >= 0:
        return "HOLD"
    if net >= 3 and dip <= 2:
        return "RISE"
    if net <= -3 and never_above_after_dip:
        return "FADE"
    if dip >= 3 and net > -3:
        return "DIP_RECOVER"
    return "OTHER"


def supplementary_other_label(leg: Leg, fraction: float) -> str:
    position = leg.point_at(fraction)
    now = float(leg.values[position, 0])
    remainder = leg.values[leg.fractions > fraction, 0]
    remainder = remainder[np.isfinite(remainder)]
    if not remainder.size:
        return "NO_REMAINDER"
    dip = now - float(remainder.min())
    net = float(remainder[-1]) - now
    if dip >= 3 and net <= -3:
        return "DIP_AND_STAY_LOWER"
    return "SMALL_OR_MIXED_MOVE"


def prepare_families(pairs: list[Pair]) -> None:
    for pair in pairs:
        for phase in PHASES:
            pair.families[phase] = (side_family(pair.favorite, phase), side_family(pair.underdog, phase))


def sample_member_levels(pairs: list[Pair], indices: np.ndarray, fractions: np.ndarray) -> np.ndarray:
    result = np.empty((len(indices), len(fractions), 7), dtype=np.float32)
    for output_index, pair_index in enumerate(indices):
        result[output_index] = pairs[int(pair_index)].levels(fractions)
    return result


def distance_rows(query: Pair, pairs: list[Pair], indices: np.ndarray, phase: float) -> tuple[np.ndarray, np.ndarray]:
    grid = query.grid(phase, remainder=False)
    query_levels = query.levels(grid)
    query_delta = query_levels.copy()
    query_delta[:, :3] -= query.favorite.anchor
    query_delta[:, 3:6] -= query.underdog.anchor
    query_delta[:, 6] -= query.favorite.anchor + query.underdog.anchor
    level_distance = np.full(len(indices), np.nan, dtype=np.float64)
    delta_distance = np.full(len(indices), np.nan, dtype=np.float64)
    for output_index, pair_index in enumerate(indices):
        member = pairs[int(pair_index)]
        levels = member.levels(grid)
        valid = np.isfinite(query_levels) & np.isfinite(levels)
        if np.any(valid):
            level_distance[output_index] = float(np.abs(query_levels[valid] - levels[valid]).mean())
        delta = levels.copy()
        delta[:, :3] -= member.favorite.anchor
        delta[:, 3:6] -= member.underdog.anchor
        delta[:, 6] -= member.favorite.anchor + member.underdog.anchor
        valid = np.isfinite(query_delta) & np.isfinite(delta)
        if np.any(valid):
            delta_distance[output_index] = float(np.abs(query_delta[valid] - delta[valid]).mean())
    return level_distance, delta_distance


def kernel_weights(distances: np.ndarray) -> tuple[np.ndarray | None, float | None]:
    finite_distances = distances[np.isfinite(distances)]
    if not finite_distances.size:
        return None, None
    scale = inverse_weighted_quantile(finite_distances, np.ones(finite_distances.size), 0.50)
    if scale is None or scale <= 0:
        return None, scale
    weights = np.zeros(distances.size, dtype=np.float64)
    valid = np.isfinite(distances)
    weights[valid] = np.exp(-distances[valid] / scale)
    return weights, scale


def ranked_local_indices(indices: np.ndarray, weights: np.ndarray, pairs: list[Pair]) -> np.ndarray:
    usable = np.flatnonzero(np.isfinite(weights) & (weights > 0))
    return np.asarray(
        sorted(usable.tolist(), key=lambda local: (-float(weights[local]), pairs[int(indices[local])].event_id)),
        dtype=np.int64,
    )


def quantile_paths(values: np.ndarray, weights: np.ndarray) -> dict[float, np.ndarray]:
    if values.ndim != 3 or values.shape[0] != weights.size:
        raise RuntimeError("QUANTILE_PATH_SHAPE_MISMATCH")
    points = values.shape[1] * values.shape[2]
    flat = values.reshape(values.shape[0], points)
    outputs = {q: np.full(points, np.nan, dtype=np.float32) for q in QUANTILES}
    block_width = 256
    for start in range(0, points, block_width):
        stop = min(points, start + block_width)
        block = flat[:, start:stop]
        valid = np.isfinite(block) & np.isfinite(weights[:, None]) & (weights[:, None] > 0)
        if not np.any(valid):
            continue
        rounded = np.rint(np.where(valid, block, 0)).astype(np.int16)
        if np.any(valid & (np.abs(block - rounded) > 0)):
            raise RuntimeError("NON_INTEGER_CENT_REMAINDER")
        minimum = int(rounded[valid].min())
        maximum = int(rounded[valid].max())
        span = maximum - minimum + 1
        width = stop - start
        columns = np.broadcast_to(np.arange(width, dtype=np.int64), block.shape)
        keys = columns * span + rounded.astype(np.int64) - minimum
        expanded_weights = np.broadcast_to(weights[:, None], block.shape)
        histogram = np.bincount(keys[valid], weights=expanded_weights[valid], minlength=width * span).reshape(width, span)
        cumulative = np.cumsum(histogram, axis=1)
        totals = cumulative[:, -1]
        nonzero = totals > 0
        for q in QUANTILES:
            thresholds = totals * q
            selected = np.argmax(cumulative >= thresholds[:, None], axis=1).astype(np.float32) + minimum
            selected[~nonzero] = np.nan
            outputs[q][start:stop] = selected
    return {q: value.reshape(values.shape[1], values.shape[2]) for q, value in outputs.items()}


def family_distribution(pairs: list[Pair], member_indices: np.ndarray, weights: np.ndarray, phase: float) -> dict[str, Any]:
    side_counts = {"favorite": defaultdict(float), "underdog": defaultdict(float)}
    pair_counts: dict[str, float] = defaultdict(float)
    total = float(weights.sum())
    for index, weight in zip(member_indices, weights):
        favorite, underdog = pairs[int(index)].families[phase]
        side_counts["favorite"][favorite] += float(weight)
        side_counts["underdog"][underdog] += float(weight)
        pair_counts[f"{favorite}|{underdog}"] += float(weight)
    def finish(counts: dict[str, float]) -> dict[str, float]:
        return {key: counts.get(key, 0.0) / total for key in sorted(counts)} if total > 0 else {}
    side = {name: finish(values) for name, values in side_counts.items()}
    pair = finish(pair_counts)
    top = {
        "favorite": min(side["favorite"], key=lambda key: (-side["favorite"][key], key)) if side["favorite"] else None,
        "underdog": min(side["underdog"], key=lambda key: (-side["underdog"][key], key)) if side["underdog"] else None,
        "pair": min(pair, key=lambda key: (-pair[key], key)) if pair else None,
    }
    return {"side": side, "pair": pair, "top": top}


def ess(weights: np.ndarray) -> float | None:
    total = float(weights.sum())
    squared = float(np.square(weights).sum())
    return total * total / squared if squared > 0 else None


def prediction_for_set(
    query: Pair,
    pairs: list[Pair],
    all_member_indices: np.ndarray,
    member_remainders: np.ndarray,
    selected_local: np.ndarray,
    all_weights: np.ndarray,
    phase: float,
    remainder_fractions: np.ndarray,
    actual_levels: np.ndarray,
) -> dict[str, Any] | None:
    if not selected_local.size:
        return None
    member_indices = all_member_indices[selected_local]
    weights = all_weights[selected_local]
    positive = np.isfinite(weights) & (weights > 0)
    member_indices = member_indices[positive]
    selected_local = selected_local[positive]
    weights = weights[positive]
    if not weights.size:
        return None
    q_delta = quantile_paths(member_remainders[selected_local], weights)
    query_baseline = query.baseline(phase)
    q_level = {q: values + query_baseline[None, :] for q, values in q_delta.items()}
    tau = (remainder_fractions - phase) / (1 - phase)
    family = family_distribution(pairs, member_indices, weights, phase)
    realized_family = query.families[phase]
    floors: dict[str, Any] = {}
    reaches: dict[str, Any] = {}
    for side, last_column, bid_column, leg in (
        ("favorite", 0, 1, query.favorite),
        ("underdog", 3, 4, query.underdog),
    ):
        actual_last = actual_levels[:, last_column]
        actual_valid = np.isfinite(actual_last)
        actual_floor = float(np.min(actual_last[actual_valid])) if np.any(actual_valid) else None
        actual_floor_tau = None
        if actual_floor is not None:
            actual_floor_tau = float(tau[int(np.flatnonzero(actual_last == actual_floor)[0])])
        predicted = {}
        for q in (0.25, 0.50, 0.75):
            path = q_level[q][:, last_column]
            valid = np.isfinite(path)
            if np.any(valid):
                floor = float(path[valid].min())
                original_positions = np.flatnonzero(valid)
                first = int(original_positions[np.flatnonzero(path[valid] == floor)[0]])
                predicted[str(q)] = {"level_cents": floor, "tau": float(tau[first])}
            else:
                predicted[str(q)] = {"level_cents": None, "tau": None}
        band_values = [predicted["0.25"]["level_cents"], predicted["0.75"]["level_cents"]]
        finite_band = [value for value in band_values if value is not None]
        floors[side] = {
            "actual_level_cents": actual_floor,
            "actual_tau": actual_floor_tau,
            "predicted_q50_level_cents": predicted["0.5"]["level_cents"],
            "predicted_q50_tau": predicted["0.5"]["tau"],
            "predicted_q25_level_cents": predicted["0.25"]["level_cents"],
            "predicted_q25_tau": predicted["0.25"]["tau"],
            "predicted_q75_level_cents": predicted["0.75"]["level_cents"],
            "predicted_q75_tau": predicted["0.75"]["tau"],
            "band_low_cents": min(finite_band) if finite_band else None,
            "band_high_cents": max(finite_band) if finite_band else None,
        }
        at_f_bid = float(query_baseline[bid_column]) if np.isfinite(query_baseline[bid_column]) else None
        after = leg.fractions > phase
        after_lows = leg.lows[after]
        reaches[side] = {}
        for q in (0.25, 0.50):
            label = f"q{int(q * 100)}"
            level = predicted[str(q)]["level_cents"]
            postable = level is not None and at_f_bid is not None and at_f_bid > level
            reached = bool(postable and np.any(np.isfinite(after_lows) & (after_lows <= level)))
            reaches[side][label] = {
                "level_cents": level,
                "bid_at_f_cents": at_f_bid,
                "status": "REACHED" if reached else ("NOT_REACHED" if postable else "NOT_POSTABLE"),
                "postable": postable,
                "reached": reached,
            }
    reaches["pair"] = {}
    for label in ("q25", "q50"):
        both_postable = reaches["favorite"][label]["postable"] and reaches["underdog"][label]["postable"]
        both_reached = reaches["favorite"][label]["reached"] and reaches["underdog"][label]["reached"]
        favorite_level = reaches["favorite"][label]["level_cents"]
        underdog_level = reaches["underdog"][label]["level_cents"]
        discount = 100 - favorite_level - underdog_level if both_reached and favorite_level is not None and underdog_level is not None else None
        reaches["pair"][label] = {
            "status": "REACHED" if both_reached else ("NOT_REACHED" if both_postable else "NOT_POSTABLE"),
            "postable": both_postable,
            "reached": both_reached,
            "discount_cents_if_reached": discount,
        }
    return {
        "member_count": int(weights.size),
        "weight_sum": float(weights.sum()),
        "ess": ess(weights),
        "family": family,
        "realized_family": {"favorite": realized_family[0], "underdog": realized_family[1], "pair": f"{realized_family[0]}|{realized_family[1]}"},
        "floors": floors,
        "reach": reaches,
        "q_level_paths": q_level,
        "actual_levels": actual_levels,
        "tau": tau,
    }


def empty_accumulator() -> dict[str, Any]:
    return {
        "queries": 0,
        "coverage": {band: {name: [0, 0] for name in SERIES} for band in ("q25_q75", "q10_q90")},
        "side_coverage": {band: {side: [0, 0] for side in SIDE_SERIES} for band in ("q25_q75", "q10_q90")},
        "joint_lasts": {band: [0, 0] for band in ("q25_q75", "q10_q90")},
        "last_error": {side: [0.0, 0] for side in SIDE_SERIES},
        "family": {
            scope: {"correct": 0, "total": 0, "logloss_sum": 0.0, "logloss_finite_count": 0, "logloss_infinite_count": 0, "confusion": defaultdict(Counter)}
            for scope in ("favorite", "underdog", "pair")
        },
        "floor": {
            side: {"abs_error_sum": 0.0, "count": 0, "within_2": 0, "timing_abs_sum": 0.0, "timing_count": 0, "timing_within_0_10": 0, "band_inside": 0, "band_count": 0}
            for side in SIDE_SERIES
        },
        "joint_floor_hit": [0, 0],
        "joint_floor_band": [0, 0],
        "reach": {
            label: {side: {"reached": 0, "total": 0, "not_postable": 0} for side in ("favorite", "underdog", "pair")}
            for label in ("q25", "q50")
        },
        "discount": {label: {"sum": 0.0, "reached": 0, "queries": 0} for label in ("q25", "q50")},
        "ess": [],
    }


def update_accumulator(acc: dict[str, Any], prediction: dict[str, Any]) -> None:
    acc["queries"] += 1
    actual = prediction["actual_levels"]
    for band, low_q, high_q in (("q25_q75", 0.25, 0.75), ("q10_q90", 0.10, 0.90)):
        low = prediction["q_level_paths"][low_q]
        high = prediction["q_level_paths"][high_q]
        lower = np.minimum(low, high)
        upper = np.maximum(low, high)
        inside = np.isfinite(actual) & np.isfinite(lower) & np.isfinite(upper) & (actual >= lower) & (actual <= upper)
        available = np.isfinite(actual) & np.isfinite(lower) & np.isfinite(upper)
        for column, name in enumerate(SERIES):
            acc["coverage"][band][name][0] += int(inside[:, column].sum())
            acc["coverage"][band][name][1] += int(available[:, column].sum())
        for side, columns in SIDE_SERIES.items():
            acc["side_coverage"][band][side][0] += int(inside[:, columns].sum())
            acc["side_coverage"][band][side][1] += int(available[:, columns].sum())
        joint_available = available[:, 0] & available[:, 3]
        joint_inside = inside[:, 0] & inside[:, 3] & joint_available
        acc["joint_lasts"][band][0] += int(joint_inside.sum())
        acc["joint_lasts"][band][1] += int(joint_available.sum())
    for side, column in (("favorite", 0), ("underdog", 3)):
        predicted = prediction["q_level_paths"][0.50][:, column]
        valid = np.isfinite(actual[:, column]) & np.isfinite(predicted)
        if np.any(valid):
            acc["last_error"][side][0] += float(np.abs(actual[valid, column] - predicted[valid]).sum())
            acc["last_error"][side][1] += int(valid.sum())
    realized = prediction["realized_family"]
    for scope in ("favorite", "underdog", "pair"):
        state = acc["family"][scope]
        top = prediction["family"]["top"][scope]
        actual_family = realized[scope]
        state["total"] += 1
        state["correct"] += int(top == actual_family)
        state["confusion"][actual_family][top or "NONE"] += 1
        probabilities = prediction["family"]["side"][scope] if scope != "pair" else prediction["family"]["pair"]
        probability = probabilities.get(actual_family, 0.0)
        if probability > 0:
            state["logloss_sum"] += -math.log(probability)
            state["logloss_finite_count"] += 1
        else:
            state["logloss_infinite_count"] += 1
    both_within = True
    both_band = True
    both_available = True
    for side in SIDE_SERIES:
        floor = prediction["floors"][side]
        actual_floor = floor["actual_level_cents"]
        predicted_floor = floor["predicted_q50_level_cents"]
        actual_tau = floor["actual_tau"]
        predicted_tau = floor["predicted_q50_tau"]
        state = acc["floor"][side]
        if actual_floor is None or predicted_floor is None:
            both_available = False
            both_within = False
        else:
            error = abs(actual_floor - predicted_floor)
            state["abs_error_sum"] += error
            state["count"] += 1
            state["within_2"] += int(error <= 2)
            both_within = both_within and error <= 2
        if actual_tau is not None and predicted_tau is not None:
            timing_error = abs(actual_tau - predicted_tau)
            state["timing_abs_sum"] += timing_error
            state["timing_count"] += 1
            state["timing_within_0_10"] += int(timing_error <= 0.10)
        low, high = floor["band_low_cents"], floor["band_high_cents"]
        if actual_floor is None or low is None or high is None:
            both_band = False
        else:
            inside = low <= actual_floor <= high
            state["band_inside"] += int(inside)
            state["band_count"] += 1
            both_band = both_band and inside
    if both_available:
        acc["joint_floor_hit"][0] += int(both_within)
        acc["joint_floor_hit"][1] += 1
    acc["joint_floor_band"][0] += int(both_band)
    acc["joint_floor_band"][1] += 1
    for label in ("q25", "q50"):
        for side in ("favorite", "underdog", "pair"):
            reach = prediction["reach"][side][label]
            state = acc["reach"][label][side]
            state["total"] += 1
            state["reached"] += int(reach["reached"])
            state["not_postable"] += int(not reach["postable"])
        pair_reach = prediction["reach"]["pair"][label]
        discount = acc["discount"][label]
        discount["queries"] += 1
        if pair_reach["reached"]:
            discount["sum"] += float(pair_reach["discount_cents_if_reached"])
            discount["reached"] += 1
    if prediction["ess"] is not None:
        acc["ess"].append(float(prediction["ess"]))


def ratio(pair: list[float | int]) -> float | None:
    return float(pair[0]) / int(pair[1]) if int(pair[1]) else None


def finish_accumulator(acc: dict[str, Any]) -> dict[str, Any]:
    macro_coverage = {}
    for band in ("q25_q75", "q10_q90"):
        target = 0.50 if band == "q25_q75" else 0.80
        series = {name: ratio(value) for name, value in acc["coverage"][band].items()}
        sides = {name: ratio(value) for name, value in acc["side_coverage"][band].items()}
        joint = ratio(acc["joint_lasts"][band])
        macro_coverage[band] = {
            "target": target,
            "series": {name: {"coverage": value, "gap_from_target": value - target if value is not None else None} for name, value in series.items()},
            "sides": {name: {"coverage": value, "gap_from_target": value - target if value is not None else None} for name, value in sides.items()},
            "joint_lasts": {"coverage": joint, "gap_from_target": joint - target if joint is not None else None},
        }
    family = {}
    for scope, state in acc["family"].items():
        infinite = state["logloss_infinite_count"]
        family[scope] = {
            "accuracy": state["correct"] / state["total"] if state["total"] else None,
            "log_loss": "INF" if infinite else (state["logloss_sum"] / state["logloss_finite_count"] if state["logloss_finite_count"] else None),
            "log_loss_infinite_queries": infinite,
            "confusion_realized_by_predicted": {actual: dict(sorted(values.items())) for actual, values in sorted(state["confusion"].items())},
        }
    floor = {}
    for side, state in acc["floor"].items():
        floor[side] = {
            "level_mae_cents": state["abs_error_sum"] / state["count"] if state["count"] else None,
            "within_2_share": state["within_2"] / state["count"] if state["count"] else None,
            "timing_mae_tau": state["timing_abs_sum"] / state["timing_count"] if state["timing_count"] else None,
            "timing_within_0_10_share": state["timing_within_0_10"] / state["timing_count"] if state["timing_count"] else None,
            "floor_band_coverage": state["band_inside"] / state["band_count"] if state["band_count"] else None,
        }
    reach = {}
    for label, sides in acc["reach"].items():
        reach[label] = {
            side: {
                "reach_rate": state["reached"] / state["total"] if state["total"] else None,
                "not_postable_share": state["not_postable"] / state["total"] if state["total"] else None,
            }
            for side, state in sides.items()
        }
        discount = acc["discount"][label]
        reach[label]["pair"]["mean_discount_cents_if_reached"] = discount["sum"] / discount["reached"] if discount["reached"] else None
        reach[label]["pair"]["reach_times_discount_cents_per_query"] = discount["sum"] / discount["queries"] if discount["queries"] else None
    return {
        "queries": acc["queries"],
        "macro": {
            "path_coverage": macro_coverage,
            "last_q50_mae_cents": {side: values[0] / values[1] if values[1] else None for side, values in acc["last_error"].items()},
            "family": family,
        },
        "micro": {
            "floor": floor,
            "joint_within_2_share": ratio(acc["joint_floor_hit"]),
            "joint_floor_band_coverage": ratio(acc["joint_floor_band"]),
        },
        "micro_micro": reach,
        "ess": distribution(acc["ess"]),
    }


def config_name(definition: str, pool: int | str) -> str:
    return f"{definition}|{pool}"


def other_share_report(pairs: list[Pair], category: str, phase: float, scorable: np.ndarray) -> dict[str, Any]:
    selected = [pairs[int(index)] for index in np.flatnonzero(scorable)]
    output = {}
    for side, attr, position in (("favorite", "favorite", 0), ("underdog", "underdog", 1)):
        count = sum(pair.families[phase][position] == "OTHER" for pair in selected)
        share = count / len(selected) if selected else None
        suggestions = Counter(
            supplementary_other_label(getattr(pair, attr), phase)
            for pair in selected
            if pair.families[phase][position] == "OTHER"
        )
        output[side] = {
            "other_count": count,
            "other_share": share,
            "data_suggested_labels_required": bool(share is not None and share > 0.15),
            "data_suggested_label_counts": dict(sorted(suggestions.items())) if share is not None and share > 0.15 else {},
        }
    return output


def exclusions_for_category(pairs: list[Pair], category_indices: np.ndarray, phase: float, tie_count: int) -> tuple[np.ndarray, dict[str, Any]]:
    scorable = np.zeros(len(category_indices), dtype=bool)
    missing_before = 0
    missing_after = 0
    missing_both = 0
    for local, global_index in enumerate(category_indices):
        okay, detail = pairs[int(global_index)].scorable(phase)
        scorable[local] = okay
        before = not (detail["favorite_trade_at_or_before"] and detail["underdog_trade_at_or_before"])
        after = not (detail["favorite_trade_after"] and detail["underdog_trade_after"])
        missing_before += int(before)
        missing_after += int(after)
        missing_both += int(before and after)
    return scorable, {
        "equal_anchor_store_silent": tie_count,
        "oriented_pairs": int(len(category_indices)),
        "scorable_pairs": int(scorable.sum()),
        "excluded_missing_true_trade_at_or_before": missing_before,
        "excluded_missing_true_trade_after": missing_after,
        "excluded_missing_both": missing_both,
        "scorable_rule": "both legs have a volume_cum-identified true-trade point at or before f and after f",
    }


def evaluate_category_phase(
    pairs: list[Pair],
    category: str,
    category_indices: np.ndarray,
    phase: float,
    scorable_local: np.ndarray,
    progress_every: int,
) -> tuple[dict[str, Any], dict[str, list[float]], dict[str, int]]:
    configs = [config_name(definition, pool) for definition in ("DEF-A_L7", "DEF-B_D7") for pool in POOL_SIZES] + [config_name("DEF-E_BASE", "all")]
    accumulators = {name: empty_accumulator() for name in configs}
    scales = {"DEF-A_L7": [], "DEF-B_D7": []}
    walk_counts = Counter()
    scorable_globals = category_indices[scorable_local]
    started = time.perf_counter()
    for query_number, query_index in enumerate(scorable_globals, 1):
        query = pairs[int(query_index)]
        member_mask = (
            scorable_local
            & np.asarray([pairs[int(index)].bell < query.formation for index in category_indices], dtype=bool)
            & np.asarray([pairs[int(index)].date != query.date for index in category_indices], dtype=bool)
        )
        member_indices = category_indices[member_mask]
        same_day_prior = sum(
            1
            for local, index in enumerate(category_indices)
            if scorable_local[local] and pairs[int(index)].bell < query.formation and pairs[int(index)].date == query.date
        )
        walk_counts["same_day_prior_excluded"] += same_day_prior
        walk_counts["eligible_member_observations"] += int(member_indices.size)
        if not member_indices.size:
            walk_counts["queries_without_walk_forward_members"] += 1
            continue
        remainder_fractions = query.grid(phase, remainder=True)
        if not remainder_fractions.size:
            walk_counts["queries_without_remainder_grid"] += 1
            continue
        actual_levels = query.levels(remainder_fractions)
        member_levels = sample_member_levels(pairs, member_indices, remainder_fractions)
        member_baselines = sample_member_levels(pairs, member_indices, np.asarray([phase], dtype=np.float64))[:, 0, :]
        member_remainders = member_levels - member_baselines[:, None, :]
        del member_levels
        distance_a, distance_b = distance_rows(query, pairs, member_indices, phase)
        weights_a, scale_a = kernel_weights(distance_a)
        weights_b, scale_b = kernel_weights(distance_b)
        definitions: list[tuple[str, np.ndarray, np.ndarray, tuple[int | str, ...]]] = []
        if weights_a is not None:
            scales["DEF-A_L7"].append(float(scale_a))
            definitions.append(("DEF-A_L7", weights_a, ranked_local_indices(member_indices, weights_a, pairs), POOL_SIZES))
        else:
            walk_counts["def_a_zero_or_missing_scale_queries"] += 1
        if weights_b is not None:
            scales["DEF-B_D7"].append(float(scale_b))
            definitions.append(("DEF-B_D7", weights_b, ranked_local_indices(member_indices, weights_b, pairs), POOL_SIZES))
        else:
            walk_counts["def_b_zero_or_missing_scale_queries"] += 1
        base_weights = np.ones(member_indices.size, dtype=np.float64)
        definitions.append(("DEF-E_BASE", base_weights, ranked_local_indices(member_indices, base_weights, pairs), ("all",)))
        for definition, weights, ranking, pools in definitions:
            for pool in pools:
                selected = ranking if pool == "all" else ranking[: int(pool)]
                prediction = prediction_for_set(
                    query,
                    pairs,
                    member_indices,
                    member_remainders,
                    selected,
                    weights,
                    phase,
                    remainder_fractions,
                    actual_levels,
                )
                if prediction is not None:
                    update_accumulator(accumulators[config_name(definition, pool)], prediction)
        if progress_every and query_number % progress_every == 0:
            elapsed = time.perf_counter() - started
            rate = elapsed / query_number
            remaining = rate * (len(scorable_globals) - query_number)
            print(f"progress {category} f={phase:.2f} {query_number}/{len(scorable_globals)} elapsed={elapsed:.1f}s eta={remaining:.1f}s", flush=True)
    return {name: finish_accumulator(value) for name, value in accumulators.items()}, scales, dict(walk_counts)


def tape_epoch(text: str) -> float:
    parsed = datetime.strptime(text, "%Y-%m-%d %I:%M:%S %p")
    return parsed.replace(tzinfo=NEW_YORK).timestamp()


def trace_named_specs(path: Path) -> dict[str, dict[str, Any]]:
    wanted = set(NAMED_SUFFIXES)
    specs: dict[str, dict[str, Any]] = {}
    pattern = re.compile(rb'^\{"event_id":"([^"]+)","kind":"([^"]+)"')
    with gzip.open(path, "rb") as stream:
        while True:
            prefix = stream.readline(4096)
            if not prefix:
                break
            match = pattern.search(prefix[:180])
            if not match or match.group(2) != b"DECISION_STAGE":
                while prefix and not prefix.endswith(b"\n"):
                    prefix = stream.readline(1024 * 1024)
                continue
            event_id = match.group(1).decode("utf-8")
            suffix = next((value for value in wanted if event_id.endswith(value)), None)
            if suffix is None or suffix in specs:
                while prefix and not prefix.endswith(b"\n"):
                    prefix = stream.readline(1024 * 1024)
                continue
            chunks = [prefix]
            while chunks[-1] and not chunks[-1].endswith(b"\n"):
                chunks.append(stream.readline(1024 * 1024))
            row = json.loads(b"".join(chunks))
            derivations = row.get("derivations") or []
            vector = next((item.get("vector") for item in derivations if item.get("vector")), None)
            if not vector:
                raise RuntimeError(f"FIRST_STAGE_VECTOR_MISSING {event_id}")
            leg_ids = vector.get("oriented_leg_ids") or []
            if len(leg_ids) != 2:
                raise RuntimeError(f"FIRST_STAGE_ORIENTATION_MISSING {event_id}")
            anchors = {leg_ids[0]: int(vector["leg0_anchor_cents"]), leg_ids[1]: int(vector["leg1_anchor_cents"])}
            hours = finite((((row.get("reads") or {}).get("time_in_window") or {}).get("value") or {}).get("hours_to_truth_bell"))
            formation = finite(row.get("timestamp_epoch"))
            if formation is None or hours is None:
                raise RuntimeError(f"FIRST_STAGE_CLOCK_MISSING {event_id}")
            specs[suffix] = {
                "event_id": event_id,
                "category": vector.get("category"),
                "formation": formation,
                "bell": formation + hours * 3600,
                "anchors": anchors,
                "first_stage_receipt": row.get("receipt"),
            }
            if len(specs) == len(wanted):
                break
    missing = wanted - set(specs)
    if missing:
        raise RuntimeError(f"NAMED_TRACE_EVENTS_MISSING {sorted(missing)}")
    return specs


def tape_leg(path: Path, leg_id: str, anchor: int, formation: float, bell: float) -> Leg:
    last = None
    bid = None
    ask = None
    seen_low = None
    had_trade_before = False
    formation_last = None
    formation_bid = None
    formation_ask = None
    minutes: dict[int, dict[str, Any]] = {}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            try:
                epoch = tape_epoch(row.get("ts_et") or "")
            except ValueError:
                continue
            if epoch >= bell:
                break
            trade = finite(row.get("last_trade"))
            new_trade_state = trade is not None and trade > 0 and (last is None or trade != last)
            if new_trade_state:
                last = trade
            bid = finite(row.get("bid_1"))
            ask = finite(row.get("ask_1"))
            if epoch <= formation:
                if new_trade_state:
                    had_trade_before = True
                    seen_low = trade if seen_low is None else min(seen_low, trade)
                formation_last = last
                formation_bid = bid
                formation_ask = ask
                continue
            minute = int(epoch // 60)
            state = minutes.setdefault(minute, {"epoch": epoch, "bid": bid, "ask": ask, "trades": []})
            state["epoch"] = epoch
            state["bid"] = bid
            state["ask"] = ask
            if new_trade_state:
                state["trades"].append(trade)
    if formation_bid is None and formation_ask is None:
        raise RuntimeError(f"NAMED_TAPE_NO_FORMATION_STATE {path}")
    initial_last = formation_last if formation_last is not None else anchor
    points = [(0.0, initial_last, formation_bid, formation_ask, seen_low, None, 0)]
    prior = points[0][1:]
    span = bell - formation
    seen_high = None
    volume = 0
    true_fractions = []
    current_last = initial_last
    for minute in sorted(minutes):
        state = minutes[minute]
        trades = state["trades"]
        if trades:
            current_last = trades[-1]
            minute_low = min(trades)
            minute_high = max(trades)
            seen_low = minute_low if seen_low is None else min(seen_low, minute_low)
            seen_high = minute_high if seen_high is None else max(seen_high, minute_high)
            volume += len(trades)
            true_fractions.append((state["epoch"] - formation) / span)
        fraction = (state["epoch"] - formation) / span
        signature = (current_last, state["bid"], state["ask"], seen_low, seen_high, volume)
        if signature == prior:
            continue
        prior = signature
        points.append((fraction, *signature))
    fractions = np.asarray([point[0] for point in points], dtype=np.float64)
    values = np.asarray([[point[1], point[2], point[3]] for point in points], dtype=np.float32)
    lows = np.asarray([np.nan if point[4] is None else point[4] for point in points], dtype=np.float32)
    highs = np.asarray([np.nan if point[5] is None else point[5] for point in points], dtype=np.float32)
    volumes = np.asarray([point[6] for point in points], dtype=np.float64)
    true_fractions = np.asarray(true_fractions, dtype=np.float64)
    if had_trade_before:
        true_fractions = np.union1d(np.asarray([0.0]), true_fractions)
    return Leg(leg_id, anchor, fractions, values, lows, highs, volumes, true_fractions)


def load_named_pairs(specs: dict[str, dict[str, Any]], tape_dir: Path) -> dict[str, Pair]:
    output = {}
    for suffix in NAMED_SUFFIXES:
        spec = specs[suffix]
        anchors = spec["anchors"]
        ordered = sorted(anchors, key=lambda leg_id: (-anchors[leg_id], leg_id))
        legs = []
        for leg_id in ordered:
            path = tape_dir / f"{spec['event_id']}-{leg_id}.csv.gz"
            if not path.is_file():
                raise RuntimeError(f"NAMED_TAPE_MISSING {path}")
            legs.append(tape_leg(path, leg_id, anchors[leg_id], spec["formation"], spec["bell"]))
        pair = Pair(spec["event_id"], event_date(spec["event_id"]), spec["category"], spec["formation"], spec["bell"], legs[0], legs[1])
        for phase in PHASES:
            pair.families[phase] = (side_family(pair.favorite, phase), side_family(pair.underdog, phase))
        output[suffix] = pair
    return output


def named_check_phase(query: Pair, pairs: list[Pair], category_indices: np.ndarray, phase: float) -> dict[str, Any]:
    query_scorable, query_scorable_detail = query.scorable(phase)
    if not query_scorable:
        return {"status": "STORE_SILENT", "reason": "named query is not scorable at this phase", "scorable_detail": query_scorable_detail}
    scorable = np.asarray([pairs[int(index)].scorable(phase)[0] for index in category_indices], dtype=bool)
    eligible = category_indices[
        scorable
        & np.asarray([pairs[int(index)].bell < query.formation for index in category_indices], dtype=bool)
        & np.asarray([pairs[int(index)].date != query.date for index in category_indices], dtype=bool)
    ]
    remainder_fractions = query.grid(phase, remainder=True)
    if not eligible.size or not remainder_fractions.size:
        return {"status": "STORE_SILENT", "reason": "no walk-forward members or no named remainder grid"}
    actual_levels = query.levels(remainder_fractions)
    member_levels = sample_member_levels(pairs, eligible, remainder_fractions)
    baselines = sample_member_levels(pairs, eligible, np.asarray([phase]))[:, 0, :]
    remainders = member_levels - baselines[:, None, :]
    distance_a, distance_b = distance_rows(query, pairs, eligible, phase)
    weights_a, scale_a = kernel_weights(distance_a)
    weights_b, scale_b = kernel_weights(distance_b)
    output: dict[str, Any] = {
        "query": {
            "event_id": query.event_id,
            "category": query.category,
            "favorite_leg_id": query.favorite.leg_id,
            "underdog_leg_id": query.underdog.leg_id,
            "realized_family": {"favorite": query.families[phase][0], "underdog": query.families[phase][1], "pair": "|".join(query.families[phase])},
        },
        "eligible_walk_forward_members": int(eligible.size),
        "definitions": {},
    }
    definitions = []
    if weights_a is not None:
        definitions.append(("DEF-A_L7", weights_a, ranked_local_indices(eligible, weights_a, pairs), scale_a, POOL_SIZES))
    if weights_b is not None:
        definitions.append(("DEF-B_D7", weights_b, ranked_local_indices(eligible, weights_b, pairs), scale_b, POOL_SIZES))
    base_weights = np.ones(eligible.size)
    definitions.append(("DEF-E_BASE", base_weights, ranked_local_indices(eligible, base_weights, pairs), None, ("all",)))
    for definition, weights, ranking, scale, pools in definitions:
        detail = {"scale_s_cents": scale, "pools": {}}
        for pool in pools:
            selected = ranking if pool == "all" else ranking[: int(pool)]
            prediction = prediction_for_set(query, pairs, eligible, remainders, selected, weights, phase, remainder_fractions, actual_levels)
            if prediction is None:
                detail["pools"][str(pool)] = {"status": "STORE_SILENT", "reason": "empty weighted pool"}
                continue
            detail["pools"][str(pool)] = {
                "status": "SCORED",
                "member_count": prediction["member_count"],
                "weight_sum": prediction["weight_sum"],
                "ess": prediction["ess"],
                "predicted_floors": prediction["floors"],
                "predicted_family_distribution": prediction["family"],
                "realized_family": prediction["realized_family"],
                "reached": prediction["reach"],
            }
        output["definitions"][definition] = detail
    for definition in ("DEF-C_OVERLAP", "DEF-D_IOU"):
        output["definitions"][definition] = {"status": "STORE_SILENT", "reason": STORE_SILENT_SIMILARITY_REASON}
    if query.event_id.endswith("ALTGAS") and phase == 0.25:
        closest = {}
        for definition, distances, weights in (("DEF-A_L7", distance_a, weights_a), ("DEF-B_D7", distance_b, weights_b)):
            if weights is None:
                closest[definition] = {"status": "STORE_SILENT", "reason": "zero or missing empirical median scale"}
                continue
            ranking = ranked_local_indices(eligible, weights, pairs)[:20]
            rows = []
            for local in ranking:
                member = pairs[int(eligible[local])]
                floors = {}
                for side, leg in (("favorite", member.favorite), ("underdog", member.underdog)):
                    remainder = leg.values[leg.fractions > phase, 0]
                    remainder = remainder[np.isfinite(remainder)]
                    floors[side] = float(remainder.min()) if remainder.size else None
                rows.append({
                    "event_id": member.event_id,
                    "distance_cents": float(distances[local]),
                    "weight": float(weights[local]),
                    "realized_family": {"favorite": member.families[phase][0], "underdog": member.families[phase][1], "pair": "|".join(member.families[phase])},
                    "realized_floor_cents": floors,
                })
            closest[definition] = rows
        output["closest_20"] = closest
    return output


def markdown_number(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, str):
        return value
    return f"{value:.{digits}f}"


def summary_tables(scoreboard: dict[str, Any]) -> str:
    lines = ["# Tune bench summary", "", "All cells are walk-forward and same-day excluded. `STORE_SILENT` means the requested definition could not be computed from the licensed inputs.", ""]
    row_order = [config_name(definition, pool) for definition in ("DEF-A_L7", "DEF-B_D7") for pool in POOL_SIZES] + ["DEF-C_OVERLAP|50", "DEF-C_OVERLAP|200", "DEF-C_OVERLAP|800", "DEF-C_OVERLAP|all", "DEF-D_IOU|50", "DEF-D_IOU|200", "DEF-D_IOU|800", "DEF-D_IOU|all", "DEF-E_BASE|all"]
    for category in CATEGORIES:
        lines.extend([f"## {category}", ""])
        for level in ("MACRO", "MICRO", "MICRO-MICRO"):
            lines.extend([f"### {level}", "", "| definition · pool | f=.10 | f=.25 | f=.50 | f=.75 |", "|---|---|---|---|---|"])
            for config in row_order:
                cells = []
                for phase in PHASES:
                    phase_value = scoreboard["categories"][category][str(phase)]
                    value = phase_value["scores"].get(config)
                    if value is None or value.get("status") == "STORE_SILENT":
                        cells.append("STORE_SILENT")
                        continue
                    if level == "MACRO":
                        joint = value["macro"]["path_coverage"]["q25_q75"]["joint_lasts"]["coverage"]
                        fav = value["macro"]["last_q50_mae_cents"]["favorite"]
                        dog = value["macro"]["last_q50_mae_cents"]["underdog"]
                        family = value["macro"]["family"]["pair"]["accuracy"]
                        cells.append(f"joint50 {markdown_number(joint)} · last MAE {markdown_number(fav)}/{markdown_number(dog)} · pair fam {markdown_number(family)}")
                    elif level == "MICRO":
                        fav = value["micro"]["floor"]["favorite"]["level_mae_cents"]
                        dog = value["micro"]["floor"]["underdog"]["level_mae_cents"]
                        timing_fav = value["micro"]["floor"]["favorite"]["timing_mae_tau"]
                        timing_dog = value["micro"]["floor"]["underdog"]["timing_mae_tau"]
                        joint = value["micro"]["joint_within_2_share"]
                        cells.append(f"floor MAE {markdown_number(fav)}/{markdown_number(dog)} · τ MAE {markdown_number(timing_fav)}/{markdown_number(timing_dog)} · joint±2 {markdown_number(joint)}")
                    else:
                        reach = value["micro_micro"]["q25"]["pair"]["reach_rate"]
                        discount = value["micro_micro"]["q25"]["pair"]["mean_discount_cents_if_reached"]
                        expected = value["micro_micro"]["q25"]["pair"]["reach_times_discount_cents_per_query"]
                        cells.append(f"q25 reach {markdown_number(reach)} · disc {markdown_number(discount)} · reach×disc {markdown_number(expected)}")
                lines.append(f"| {config} | " + " | ".join(cells) + " |")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_outputs(args: argparse.Namespace) -> dict[str, Path]:
    library = args.library.resolve()
    receipt_path = args.receipt.resolve()
    named_trace = args.named_trace.resolve()
    comparison_trace = args.comparison_trace.resolve()
    tape_dir = args.tape_dir.resolve()
    output_dir = args.output_dir.resolve()
    library_hash = sha256_file(library)
    if library_hash != EXPECTED_LIBRARY_SHA256:
        raise RuntimeError(f"RANGE_OVERLAP_LIBRARY_SHA256_MISMATCH {library_hash}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("output", {}).get("sha256") != library_hash:
        raise RuntimeError("RANGE_OVERLAP_RECEIPT_SHA256_MISMATCH")
    print("loading library", flush=True)
    pairs, census = load_library(library)
    prepare_families(pairs)
    by_category = {category: np.asarray([index for index, pair in enumerate(pairs) if pair.category == category], dtype=np.int64) for category in CATEGORIES}
    tie_counts = census["equal_anchor_store_silent"]
    category_filter = tuple(args.categories) if args.categories else CATEGORIES
    scoreboard: dict[str, Any] = {"label": "TUNE_BENCH_SCOREBOARD", "categories": {}}
    exclusion_counts: dict[str, Any] = {}
    scale_distributions: dict[str, Any] = {}
    other_shares: dict[str, Any] = {}
    for category in CATEGORIES:
        scoreboard["categories"][category] = {}
        exclusion_counts[category] = {}
        scale_distributions[category] = {}
        other_shares[category] = {}
        indices = by_category[category]
        for phase in PHASES:
            scorable, exclusions = exclusions_for_category(pairs, indices, phase, int(tie_counts.get(category, 0)))
            exclusion_counts[category][str(phase)] = exclusions
            other_shares[category][str(phase)] = other_share_report(pairs, category, phase, scorable)
            wta_silent = category.startswith("WTA_") and int(scorable.sum()) < 200
            if category not in category_filter or wta_silent:
                reason = f"STORE_SILENT: WTA scorable count {int(scorable.sum())} is below 200" if wta_silent else "STORE_SILENT: category deferred by runtime category filter"
                scoreboard["categories"][category][str(phase)] = {
                    "status": "STORE_SILENT",
                    "reason": reason,
                    "scores": {config_name(definition, pool): {"status": "STORE_SILENT", "reason": reason} for definition in ("DEF-A_L7", "DEF-B_D7", "DEF-C_OVERLAP", "DEF-D_IOU") for pool in POOL_SIZES} | {config_name("DEF-E_BASE", "all"): {"status": "STORE_SILENT", "reason": reason}},
                }
                continue
            print(f"scoring {category} f={phase:.2f} scorable={int(scorable.sum())}", flush=True)
            scores, scales, walk = evaluate_category_phase(pairs, category, indices, phase, scorable, args.progress_every)
            for definition in ("DEF-C_OVERLAP", "DEF-D_IOU"):
                for pool in POOL_SIZES:
                    scores[config_name(definition, pool)] = {"status": "STORE_SILENT", "reason": STORE_SILENT_SIMILARITY_REASON}
            exclusion_counts[category][str(phase)]["walk_forward"] = walk
            scale_distributions[category][str(phase)] = {definition: distribution(values) for definition, values in scales.items()}
            scoreboard["categories"][category][str(phase)] = {"status": "SCORED", "scores": scores}
    print("reading named trace and tapes", flush=True)
    named_specs = trace_named_specs(named_trace)
    named_pairs = load_named_pairs(named_specs, tape_dir)
    named_checks: dict[str, Any] = {"label": "TUNE_BENCH_NAMED_CHECKS", "events": {}}
    for suffix in NAMED_SUFFIXES:
        query = named_pairs[suffix]
        named_checks["events"][suffix] = {"event_id": query.event_id, "phases": {}}
        for phase in PHASES:
            named_checks["events"][suffix]["phases"][str(phase)] = named_check_phase(query, pairs, by_category[query.category], phase)
    receipt_output = {
        "label": "TUNE_BENCH_RECEIPT",
        "inputs": {
            "range_overlap_library": {"path": str(library), "sha256": library_hash, "bytes": library.stat().st_size},
            "range_overlap_library_receipt": {"path": str(receipt_path), "sha256": sha256_file(receipt_path), "bytes": receipt_path.stat().st_size},
            "named_trace_current": {"path": str(named_trace), "sha256": sha256_file(named_trace), "bytes": named_trace.stat().st_size},
            "named_trace_prior": {"path": str(comparison_trace), "sha256": sha256_file(comparison_trace), "bytes": comparison_trace.stat().st_size, "use": "provenance/hash comparison only; named state is read from current trace"},
            "named_tape_dir": str(tape_dir),
        },
        "universe": census,
        "walk_forward": "A member is eligible only when the later of its two leg bell_epoch values is strictly earlier than the later of the query's two leg formation_end_epoch values. This is the first instant when both query legs are formed and ensures both member legs have rung. The query event and same event-date members are excluded. No named-game exception.",
        "event_date_rule": "The raw index omits event_date, so the exact YYMMMDD date code is read reversibly from event_id for same-day exclusion.",
        "true_trade_change_point_rule": "The compact path omits minute_has_trade. A point is identified as true-trade when volume_cum increases; the formation point is true-trade when volume_cum > 0 or seen_true_trade_high_cents is present. No price or book field is substituted.",
        "named_tape_conversion": "Named-check tick tapes are collapsed to the last observed bid/ask state in each observed ET minute so they match the library's minute grain. The carried last_trade field becomes a new named true-print state only when its positive value changes; per-minute low/high are the min/max of those changed states. The change point is stamped at that minute's last observed tape epoch. This affects named checks only, never tuning selection or scores.",
        "conversions": {
            "remainder_delta": "Each side's last/bid/ask subtracts that same series' value at f; the seventh series subtracts the pair last sum at f.",
            "remainder_clock": "tau = (window_fraction - f) / (1 - f)",
            "pair_vector": list(SERIES),
            "so_far_grid": "union of the query pair's own stored change points <= f; member sampled at largest change point <= each query fraction",
            "remainder_grid": "union of the query pair's own stored change points > f; member sampled at the corresponding f + tau*(1-f), which is the same fraction grid",
        },
        "definitions": {
            "DEF-A_L7": "mean absolute difference over all jointly present values of the seven-series so-far level path; s is the equal-base-weight inverse-CDF median distance in that query's full eligible pool; weight exp(-d/s)",
            "DEF-B_D7": "same as DEF-A after subtracting each side's anchor from last/bid/ask and the pair anchor sum from the seventh series",
            "DEF-C_OVERLAP": STORE_SILENT_SIMILARITY_REASON,
            "DEF-D_IOU": STORE_SILENT_SIMILARITY_REASON,
            "DEF-E_BASE": "all eligible category/orientation members weight 1; all pool only",
        },
        "weighted_quantiles": "inverse weighted empirical CDF: first ascending integer-cent value whose cumulative positive weight reaches q*total; no interpolation",
        "family_thresholds_and_precedence": [
            "HOLD first: max further dip <=1 and net >=0",
            "RISE second: net >=3 and max further dip <=2",
            "FADE third: net <=-3 and, from the first occurrence of the remainder minimum onward, last never exceeds the level at f",
            "DIP_RECOVER fourth: max further dip >=3 and net >-3",
            "OTHER otherwise",
        ],
        "log_loss": "natural logarithm; a realized label with zero predicted mass is reported as INF with its query count; no smoothing constant is introduced",
        "micro_micro_note": "Computed exactly as ordered as a diagnostic. The source receipt labels the minute library micro_micro_licensed=false.",
        "exclusions": exclusion_counts,
        "other_family_share_and_suggested_labels": other_shares,
        "s_distributions_cents": scale_distributions,
        "category_filter": list(category_filter),
        "deviations": [
            "DEF-C and DEF-D are STORE_SILENT because the licensed index and receipt do not carry the eleven-scalar vectors that the builder joins from unlicensed corpus inputs.",
            "event_date is parsed from event_id because the index row omits the field required by the order's same-day exclusion.",
        ],
    }
    output_paths = {
        "scoreboard": output_dir / "TUNE_BENCH_SCOREBOARD.json",
        "receipt": output_dir / "TUNE_BENCH_RECEIPT.json",
        "named": output_dir / "TUNE_BENCH_NAMED_CHECKS.json",
        "summary": output_dir / "TUNE_BENCH_SUMMARY.md",
    }
    stable_json(output_paths["scoreboard"], scoreboard)
    stable_json(output_paths["receipt"], receipt_output)
    stable_json(output_paths["named"], named_checks)
    output_paths["summary"].write_text(summary_tables(scoreboard), encoding="utf-8", newline="\n")
    return output_paths


def parse_args() -> argparse.Namespace:
    script = Path(__file__).resolve()
    analysis = script.parent
    repo = analysis.parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, default=repo / "arb-executor/data/durable/RANGE_OVERLAP_LIBRARY.jsonl.gz")
    parser.add_argument("--receipt", type=Path, default=repo / "arb-executor/data/durable/RANGE_OVERLAP_LIBRARY_RECEIPT.json")
    parser.add_argument("--named-trace", type=Path, default=Path(r"C:\tmp\v54_altgas_face_20260903_2131_receipts\KEEP\REPAIR_FOUR_GAME_TRACE.jsonl.gz"))
    parser.add_argument("--comparison-trace", type=Path, default=Path(r"C:\tmp\v54_altgas_extra_2dfb5b0a_20260902_run2_custody\REPAIR_FOUR_GAME_TRACE.jsonl.gz"))
    parser.add_argument("--tape-dir", type=Path, default=Path(r"C:\Users\omigr\OMI-Window1-private\fit-local\ticks"))
    parser.add_argument("--output-dir", type=Path, default=analysis / "tune_bench")
    parser.add_argument("--categories", nargs="*", choices=CATEGORIES)
    parser.add_argument("--progress-every", type=int, default=25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    paths = build_outputs(args)
    print(f"completed in {time.perf_counter() - started:.3f}s", flush=True)
    for name, path in paths.items():
        print(f"{name} {sha256_file(path)} {path}", flush=True)


if __name__ == "__main__":
    main()
