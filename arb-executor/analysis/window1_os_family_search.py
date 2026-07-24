#!/usr/bin/env python3
"""Deterministic corrected Window-1 OS-family development search.

The runner consumes only the frozen July 12-20 development population.  It
uses the shared execution kernel and the committed chronological OS surfaces;
missing features are recorded and disabled individually.  It has no holdout,
production, order-placement, position, exit, settlement, or DCA interface.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import math
import statistics
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import window1_fit_benchmark as fit
from window1_start_guard import strict_positive_cutoff


VERSION = "window1-corrected-os-family-search-v1"
D_REQUIRED = 804
TARGET = 603
LOT = 5.0
UTC = dt.timezone.utc
DEV_DATES = {f"2026-07-{day:02d}" for day in range(12, 21)}
HOLDOUT_DATES = {f"2026-07-{day:02d}" for day in range(24, 27)}

_SURFACES: dict[str, Any] = {}
_ORIGINAL_PRICE = fit.price_for_policy
_ORIGINAL_BUILD_ACTIONS = fit.build_actions


class SearchError(RuntimeError):
    """A frozen search or evidence invariant failed."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SearchError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise SearchError(
                    f"JSON object required: {path}:{line_number}"
                )
            rows.append(value)
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_output(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def verify_prerun(
    repo: Path, freeze_path: Path, pre_run_commit: str,
    events_path: Path,
) -> dict[str, Any]:
    freeze = read_json(freeze_path)
    if freeze.get("schema_version") != "window1-os-family-prerun-v2":
        raise SearchError("unrecognized PRE-RUN schema")
    if freeze.get("execution_order", {}).get(
        "candidate_scoring_performed"
    ) is not False:
        raise SearchError("PRE-RUN claims prior scoring")
    head = git_output(repo, "rev-parse", "HEAD")
    if head != pre_run_commit:
        raise SearchError(
            f"search must begin at PRE-RUN HEAD: {head} != "
            f"{pre_run_commit}"
        )
    git_output(repo, "cat-file", "-e", f"{pre_run_commit}^{{commit}}")
    result = subprocess.run(
        [
            "git", "merge-base", "--is-ancestor", pre_run_commit,
            "origin/codex/window1-definition",
        ],
        cwd=repo,
    )
    if result.returncode != 0:
        raise SearchError(
            "PRE-RUN commit is not present on "
            "origin/codex/window1-definition"
        )
    if git_output(repo, "status", "--porcelain"):
        raise SearchError("worktree must be clean before scoring")

    for locator, receipt in (
        freeze.get("repository_input_receipts") or {}
    ).items():
        path = (repo / locator).resolve()
        if not path.is_file() or sha256_file(path) != receipt["sha256"]:
            raise SearchError(f"PRE-RUN input drift: {locator}")
    event_receipt = (
        freeze.get("private_development_input_receipts", {})
        .get("development_events", {})
    )
    if sha256_file(events_path) != event_receipt.get("sha256"):
        raise SearchError("development event input drift")
    if (
        freeze.get("development", {}).get("dates")
        != sorted(DEV_DATES)
        or freeze.get("holdout", {}).get("dates")
        != sorted(HOLDOUT_DATES)
        or freeze.get("holdout", {}).get("opened") is not False
    ):
        raise SearchError("development/holdout freeze changed")
    return freeze


def market_cache_receipt(path: Path) -> dict[str, Any]:
    files = sorted(path.glob("*.json.gz"), key=lambda item: item.name)
    rows = [{
        "name": item.name,
        "bytes": item.stat().st_size,
        "sha256": sha256_file(item),
    } for item in files]
    return {
        "files": len(files),
        "bytes": sum(row["bytes"] for row in rows),
        "hash_set_sha256": hashlib.sha256(
            compact(rows).encode()
        ).hexdigest(),
    }


def load_frozen_event_market(
    event: Mapping[str, Any],
    start: Mapping[str, Any],
    source: Path,
    expected_cache_key: str,
    left: float,
    right: float,
) -> list[dict[str, Any]]:
    event_id = str(event["event_id"])
    path = source / f"{event_id}.json.gz"
    if not path.is_file():
        raise SearchError(f"market cache missing event: {event_id}")
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    if (
        payload.get("event_id") != event_id
        or payload.get("cache_key") != expected_cache_key
        or not isinstance(payload.get("legs"), list)
        or len(payload["legs"]) != 2
    ):
        raise SearchError(f"market cache receipt mismatch: {event_id}")
    earliest = fit.parse_utc(
        payload.get("earliest_utc"), "cache.earliest_utc"
    )
    latest = fit.parse_utc(
        payload.get("latest_utc"), "cache.latest_utc"
    )
    if earliest > left or latest < right:
        raise SearchError(
            f"market cache does not cover guarded window: {event_id}"
        )
    expected_tickers = {
        str(row["ticker"]) for row in event["legs"]
    }
    actual_tickers = {
        str(row.get("ticker") or "") for row in payload["legs"]
    }
    if expected_tickers != actual_tickers:
        raise SearchError(f"market cache ticker set differs: {event_id}")
    for leg in payload["legs"]:
        prior_snapshot = -math.inf
        for snapshot in leg.get("snapshots") or []:
            timestamp = float(snapshot["ts"])
            if timestamp < prior_snapshot:
                raise SearchError(
                    f"market snapshots unsorted: {event_id}"
                )
            prior_snapshot = timestamp
        seen_trades = set()
        prior_print = -math.inf
        for trade in leg.get("prints") or []:
            identity = str(trade.get("trade_id") or "")
            timestamp = float(trade["ts"])
            if (
                not identity or identity in seen_trades
                or timestamp < prior_print
                or float(trade.get("size") or 0) <= 0
            ):
                raise SearchError(
                    f"cached true-print contract failed: {event_id}"
                )
            seen_trades.add(identity)
            prior_print = timestamp
    return list(payload["legs"])


def nearest_int(value: float) -> int:
    return int(math.floor(float(value) + 0.5))


def price_zone(price: float) -> str:
    if price <= 25:
        return "le25"
    if price <= 50:
        return "26_50"
    if price <= 75:
        return "51_75"
    return "ge75"


def default_flat_band(category: str, anchor: float) -> str | None:
    category_row = (
        _SURFACES["band_map"].get("cats", {}).get(category)
    )
    if not category_row or category_row.get("thin"):
        return None
    bands = [
        row for row in category_row.get("bands") or []
        if row.get("direction") == "flat"
    ]
    if not bands:
        return None
    return str(min(
        bands,
        key=lambda row: abs(float(row["anchor_med"]) - anchor),
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
    category: str, anchor: float, net: float, dip: float,
) -> tuple[str | None, bool, float | None]:
    bucket = recognition_bucket(anchor, net, dip)
    cell = (
        _SURFACES["drift"].get("recognition", {})
        .get(f"{category}|h6", {})
        .get(bucket)
    )
    if cell and float(cell.get("purity") or 0) >= 0.5:
        return str(cell["top"]), True, float(cell["purity"])
    return default_flat_band(category, anchor), False, (
        float(cell.get("purity")) if cell else None
    )


def divot_depth(band: str | None, quantile: str) -> float | None:
    if not band:
        return None
    row = _SURFACES["divot"].get("bands", {}).get(band)
    if not row:
        return None
    field = "depth_p90" if quantile == "p90" else "depth_p50"
    value = row.get(field)
    return float(value) if value is not None else None


def sealed_depth(band: str | None) -> float | None:
    if not band:
        return None
    row = _SURFACES["sealed"].get("bands", {}).get(band)
    if not row or row.get("status") != "SEALED":
        return None
    value = row.get("depth")
    return float(value) if value is not None else None


def recut_depth(category: str, anchor: float) -> float | None:
    cell = (
        _SURFACES["recut"].get(category, {})
        .get(str(max(1, min(99, nearest_int(anchor)))))
    )
    value = (cell or {}).get("edge_p50")
    return float(value) if value is not None else None


def atlas_depth(
    category: str, role: str, anchor: float,
) -> tuple[float | None, str | None]:
    atlas_role = "leader" if role == "favorite" else "underdog"
    key = f"{category}|{atlas_role}|{price_zone(anchor)}"
    page = _SURFACES["atlas"].get("pages", {}).get(key)
    if not page or page.get("verdict") != "PATH":
        return None, key
    value = (page.get("bottom") or {}).get("depth_p50")
    return (float(value) if value is not None else None), key


def cohort_prior_depth(category: str, anchor: float) -> float | None:
    zone = int(max(0, min(3, anchor // 25)))
    values = [
        float(row["cell_edge"])
        for row in _SURFACES["cohort"].get("rows") or []
        if row.get("cat") == category
        and row.get("cell_edge") is not None
        and int(float(row.get("px") or 0) // 25) == zone
    ]
    return float(statistics.median(values)) if values else None


def reach_rate(
    category: str, depth: float | None, flow_state: str,
) -> float | None:
    if depth is None:
        return None
    row = _SURFACES["reach"].get("law", {}).get(
        f"{category}|{flow_state}"
    )
    rates = (row or {}).get("rate_per_hr") or {}
    value = rates.get(str(max(1, nearest_int(depth))))
    return float(value) if value is not None else None


def orientation_call(
    category: str,
    contexts: Sequence[Mapping[str, Any]],
    left: float,
) -> dict[str, Any]:
    by_role = {
        str(context["feature"].get("role")): context
        for context in contexts
    }
    dog = by_role.get("underdog")
    leader = by_role.get("favorite")
    if dog is None or leader is None:
        return {"available": False, "reason": "role_mapping_missing"}

    def stats(context: Mapping[str, Any]) -> dict[str, Any] | None:
        rows = [
            row for row in context["prints"]
            if left <= float(row["ts"]) < left + 3600
        ]
        if len(rows) < 3:
            return None
        prices = [float(row["price"]) for row in rows]
        return {
            "median": statistics.median(prices),
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
        _SURFACES["orient"].get("cats", {})
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


def event_feature_state(
    event: Mapping[str, Any],
    contexts: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
) -> dict[str, Any]:
    category = str(event["category"])
    t6 = left + 2 * 3600
    orientation = orientation_call(category, contexts, left)
    leg_states = []
    for context in contexts:
        birth = fit.snapshot_after(context["snapshots"], left, right)
        recognition = fit.snapshot_after(
            context["snapshots"], t6, right
        )
        feature = context["feature"]
        if birth is None:
            state = {
                "ticker": context["ticker"],
                "birth_book": False,
                "component_coverage": {},
                "depths": {},
                "recognition_at": t6,
            }
            feature["_os"] = state
            leg_states.append(state)
            continue
        anchor = float(birth["best_bid"])
        upto = [
            row for row in context["snapshots"]
            if float(birth["ts"]) <= float(row["ts"]) <= t6
        ]
        current = (
            float(recognition["best_bid"])
            if recognition is not None else anchor
        )
        dip = max(
            0.0, anchor - min(
                [float(row["best_bid"]) for row in upto] or [anchor]
            )
        )
        net = current - anchor
        birth_band = default_flat_band(category, anchor)
        called_band, recognition_used, purity = recognized_band(
            category, anchor, net, dip
        )
        core_depth = divot_depth(birth_band, "p50")
        called_quantile = (
            "p90"
            if orientation.get("called_role") == feature.get("role")
            else "p50"
        )
        recognized_depth = divot_depth(called_band, called_quantile)
        sealed = sealed_depth(called_band)
        recut = recut_depth(category, anchor)
        atlas, atlas_key = atlas_depth(
            category, str(feature.get("role") or ""), anchor
        )
        cohort = cohort_prior_depth(category, anchor)
        print_count = sum(
            1 for row in context["prints"]
            if left <= float(row["ts"]) <= min(right, left + 1800)
        )
        flow_state = (
            "open" if print_count >= 16 else
            "warm" if print_count > 0 else "quiet"
        )
        reach = reach_rate(category, atlas, flow_state)
        pressure = (
            feature.get("ask_over_bid_top5")
            if feature.get("top5_available") is True else None
        )
        state = {
            "ticker": context["ticker"],
            "birth_book": True,
            "anchor_bid_cents": anchor,
            "birth_band": birth_band,
            "recognition_band": called_band,
            "recognition_used": recognition_used,
            "recognition_purity": purity,
            "recognition_net_cents": net,
            "recognition_dip_cents": dip,
            "recognition_at": t6,
            "orientation": orientation,
            "atlas_key": atlas_key,
            "flow_state": flow_state,
            "reach_rate_per_hour": reach,
            "depths": {
                "divot_core": core_depth,
                "recognized_divot": recognized_depth,
                "sealed_band": sealed,
                "cohort": cohort,
                "dynamic_recut": recut,
                "atlas": atlas,
            },
            "pressure_ratio": pressure,
            "bookmaker_divergence_cents": (
                feature.get("book_market_divergence_cents")
                if feature.get("bookmaker_available") is True else None
            ),
            "component_coverage": {
                "pair_law": True,
                "first_fill_sibling_response": True,
                "sealed_bands": sealed is not None,
                "dual_divot_steering_and_catch": core_depth is not None,
                "drift_recognition": recognition_used,
                "cohort_steering": cohort is not None,
                "orientation_prior": orientation.get("available") is True,
                "walk_park_posture": True,
                "riser_deceleration_mirror_seesaw": abs(net) >= 5,
                "dynamic_floor_and_recut_cells": recut is not None,
                "atlas_and_reach": atlas is not None and reach is not None,
                "shape_corpus": False,
                "fv_and_bookmaker_voice": (
                    feature.get("bookmaker_available") is True
                ),
                "bbo_and_top_five_pressure": (
                    feature.get("top5_available") is True
                ),
                "own_order_fingerprints_and_contributed_volume": (
                    feature.get(
                        "own_historical_order_volume_attributable"
                    ) is True
                ),
                "true_print_tape": True,
            },
            "feature_censors": [
                name for name, available in {
                    "shape_corpus_no_independent_causal_cell_mapping": False,
                    "full_depth_sequence_unavailable": False,
                    "pinnacle_unavailable": False,
                    "own_order_fingerprint": feature.get(
                        "own_historical_order_volume_attributable"
                    ) is True,
                    "bookmaker_fv": feature.get(
                        "bookmaker_available"
                    ) is True,
                    "top_five": feature.get("top5_available") is True,
                }.items() if not available
            ],
        }
        feature["_os"] = state
        leg_states.append(state)

    available_count = sum(
        all(
            state.get("component_coverage", {}).get(component, False)
            for state in leg_states
        )
        for component in _SURFACES["allowed_features"]
    )
    coverage_class = (
        "no_causal_birth_book"
        if any(not state.get("birth_book") for state in leg_states)
        else f"available_{available_count}_of_16"
    )
    return {
        "coverage_class": coverage_class,
        "available_feature_families": available_count,
        "leg_states": leg_states,
        "orientation": orientation,
    }


def enabled_depths(
    family: str, feature: Mapping[str, Any],
    ablations: set[str],
) -> list[float]:
    state = feature.get("_os") or {}
    depths = state.get("depths") or {}
    values = []

    def add(name: str, ablation: str | None = None) -> None:
        if ablation and ablation in ablations:
            return
        value = depths.get(name)
        if value is not None:
            values.append(float(value))

    add("divot_core", "without_divot_catch")
    if family in {
        "pair_divot_core", "drift_cohort_orientation",
        "mirror_deceleration", "full_chronological_stack",
    }:
        add("sealed_band", "without_sealed_bands")
    if family in {
        "drift_cohort_orientation", "full_chronological_stack",
    }:
        add("recognized_divot", "without_drift_recognition")
        add("cohort", "without_cohort_steering")
    if family in {
        "dynamic_recut_atlas", "full_chronological_stack",
    }:
        add("dynamic_recut", "without_dynamic_floor_recut")
        add("atlas", "without_atlas_reach")
    if family == "causal_micro_pressure":
        pass
    if family == "full_chronological_stack":
        pass
    return values


def family_price(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    feature: Mapping[str, Any],
    snapshot: Mapping[str, Any],
) -> int | None:
    family = policy.get("os_family")
    if not family:
        return _ORIGINAL_PRICE(policy, event, feature, snapshot)
    ablations = set(policy.get("ablations") or [])
    depths = enabled_depths(str(family), feature, ablations)
    if not depths:
        return None
    depth = max(depths)
    state = feature.get("_os") or {}
    if (
        family in {"causal_micro_pressure", "full_chronological_stack"}
        and "without_top_five_pressure" not in ablations
        and state.get("pressure_ratio") is not None
        and float(state["pressure_ratio"]) >= 1.5
    ):
        depth += 1
    if (
        family == "full_chronological_stack"
        and "without_bookmaker_fv" not in ablations
        and state.get("bookmaker_divergence_cents") is not None
        and float(state["bookmaker_divergence_cents"]) <= -3
    ):
        depth += 1
    price = int(snapshot["best_bid"]) - nearest_int(depth)
    maker_ceiling = int(snapshot["best_ask"]) - 1
    return max(1, min(maker_ceiling, price))


def family_build_actions(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    feature: Mapping[str, Any],
    snapshots: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    not_before: float,
    right: float,
    scheduled: float,
) -> list[dict[str, Any]]:
    family = str(policy.get("os_family") or "")
    if family in {
        "drift_cohort_orientation",
        "mirror_deceleration",
        "full_chronological_stack",
    }:
        recognition_at = (feature.get("_os") or {}).get(
            "recognition_at"
        )
        if recognition_at is not None:
            not_before = max(not_before, float(recognition_at))
    return _ORIGINAL_BUILD_ACTIONS(
        policy, event, feature, snapshots, prints,
        not_before, right, scheduled,
    )


def candidate_policies(spec: Mapping[str, Any]) -> list[dict[str, Any]]:
    policies = []
    for policy_id in spec.get("permitted_policy_ids") or []:
        family, posture, response = str(policy_id).split("__")
        policies.append({
            "policy_id": policy_id,
            "os_family": family,
            "posture": posture,
            "first_fill_sibling_response_id": response,
            "placement_rule": (
                "walk_law" if posture == "walk" else "touch"
            ),
            "max_moves": 2,
            "move_step_cents": 1,
            "sequence_rule": "simultaneous",
            "first_fill_response": (
                "reaim_depth_support"
                if response == "reaim" else "hold"
            ),
            "ablations": [],
        })
    return policies


def source_class(row: Mapping[str, Any]) -> str:
    return str(
        row.get("start_source_class")
        or row.get("precision_class") or "unknown"
    )


def empty_outcome(
    policy_id: str, event: Mapping[str, Any], reason: str,
) -> dict[str, Any]:
    legs = [{
        "status": reason,
        "quantity": 0.0,
        "cost": 0.0,
        "vwap": None,
        "completion_ts": None,
    } for _ in range(2)]
    return {
        "candidate_id": policy_id,
        "event_id": event["event_id"],
        "event_date": event["event_date"],
        "category": event["category"],
        "lower_complete": False,
        "upper_complete": False,
        "upper_complete_with_known_price": False,
        "censored": reason != "window_left_after_guarded_start",
        "lower_metrics": None,
        "upper_metrics": None,
        "leg_references_cents": [None, None],
        "lower_leg_results": legs,
        "upper_leg_results": legs,
    }


def classify(
    outcome: Mapping[str, Any], start: Mapping[str, Any],
    has_cutoff: bool,
) -> str:
    precision = str(start.get("precision_class") or "")
    if precision == "contradictory":
        return "contradictory"
    if not has_cutoff:
        return "censored"
    if outcome.get("lower_complete"):
        return "exact_five"
    quantities = [
        float(row.get("quantity") or 0)
        for row in outcome.get("lower_leg_results") or []
    ]
    if any(quantity > LOT + 1e-9 for quantity in quantities):
        return "other_quantity"
    if any(0 < quantity < LOT for quantity in quantities):
        return "partial"
    if outcome.get("upper_complete") or outcome.get("censored"):
        return "censored"
    return "nonfill"


def compact_event_record(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    start: Mapping[str, Any],
    outcome: Mapping[str, Any],
    feature_state: Mapping[str, Any],
    cutoff: float | None,
) -> dict[str, Any]:
    metrics = outcome.get("lower_metrics") or {}
    classification = classify(outcome, start, cutoff is not None)
    leg_results = []
    references = outcome.get("leg_references_cents") or [None, None]
    deltas = metrics.get("leg_deltas")
    for index, row in enumerate(
        outcome.get("lower_leg_results") or []
    ):
        leg_results.append({
            "quantity": float(row.get("quantity") or 0),
            "vwap_cents": row.get("vwap"),
            "completion_exchange_ts": row.get("completion_ts"),
            "window1_close_reference_cents": (
                references[index] if index < len(references) else None
            ),
            "window1_close_delta_cents": (
                deltas[index]
                if deltas is not None and index < len(deltas) else None
            ),
            "status": row.get("status"),
        })
    return {
        "schema_version": VERSION + "-event-v1",
        "policy_id": policy["policy_id"],
        "policy_family": policy["os_family"],
        "event_id": event["event_id"],
        "event_date": event["event_date"],
        "tournament_class": event["category"],
        "start_source_class": source_class(start),
        "start_guard": start.get("guard_band"),
        "strict_positive_cutoff_utc": (
            dt.datetime.fromtimestamp(cutoff, UTC).isoformat()
            if cutoff is not None else None
        ),
        "feature_coverage_class": feature_state["coverage_class"],
        "available_feature_family_count": feature_state[
            "available_feature_families"
        ],
        "feature_components_by_leg": [
            state.get("component_coverage", {})
            for state in feature_state.get("leg_states") or []
        ],
        "feature_censors_by_leg": [
            state.get("feature_censors", [])
            for state in feature_state.get("leg_states") or []
        ],
        "classification": classification,
        "C": bool(outcome.get("lower_complete")),
        "PC": metrics.get("NC") is True,
        "S": metrics.get("PC") is True,
        "IC": metrics.get("IC") is True,
        "combined_entry_cost_cents": metrics.get("combined_cost"),
        "combined_window1_close_delta_cents": metrics.get("pair_delta"),
        "reference_available": metrics.get(
            "reference_available", False
        ),
        "optimistic_queue_complete": bool(
            outcome.get("upper_complete")
        ),
        "legs": leg_results,
    }


def group_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "D": len(rows),
        "C": sum(bool(row["C"]) for row in rows),
        "PC": sum(bool(row["PC"]) for row in rows),
        "S": sum(bool(row["S"]) for row in rows),
        "IC": sum(bool(row["IC"]) for row in rows),
        "classifications": dict(Counter(
            str(row["classification"]) for row in rows
        )),
    }


def distribution(values: Iterable[float]) -> dict[str, Any]:
    data = [float(value) for value in values if value is not None]
    return {
        "n": len(data),
        "mean": statistics.mean(data) if data else None,
        "median": statistics.median(data) if data else None,
        "p25": fit.percentile(data, .25),
        "p75": fit.percentile(data, .75),
        "min": min(data) if data else None,
        "max": max(data) if data else None,
    }


def summarize_candidate(
    policy: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if len(rows) != D_REQUIRED:
        raise SearchError(
            f"candidate changed D: {policy['policy_id']}={len(rows)}"
        )
    raw = group_summary(rows)
    raw.update({
        "exact_five": raw["classifications"].get("exact_five", 0),
        "partial": raw["classifications"].get("partial", 0),
        "other_quantity": raw["classifications"].get(
            "other_quantity", 0
        ),
        "nonfill": raw["classifications"].get("nonfill", 0),
        "contradictory": raw["classifications"].get(
            "contradictory", 0
        ),
        "censored": raw["classifications"].get("censored", 0),
    })
    counts = [
        raw[name] for name in (
            "exact_five", "partial", "other_quantity",
            "nonfill", "contradictory", "censored",
        )
    ]
    if sum(counts) != D_REQUIRED or raw["exact_five"] != raw["C"]:
        raise SearchError(
            f"classification conservation failed: {policy['policy_id']}"
        )

    def grouped(field: str) -> dict[str, Any]:
        values: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for row in rows:
            values[str(row.get(field) or "missing")].append(row)
        return {
            key: group_summary(value)
            for key, value in sorted(values.items())
        }

    feature_full = sum(
        row["available_feature_family_count"] == 16 for row in rows
    )
    optimistic = sum(
        row["optimistic_queue_complete"] for row in rows
    )
    combined_costs = [
        row["combined_entry_cost_cents"]
        for row in rows if row["C"]
        and row["combined_entry_cost_cents"] is not None
    ]
    combined_deltas = [
        row["combined_window1_close_delta_cents"]
        for row in rows if row["C"]
        and row["combined_window1_close_delta_cents"] is not None
    ]
    individual_deltas = [
        leg["window1_close_delta_cents"]
        for row in rows if row["C"] for leg in row["legs"]
        if leg["window1_close_delta_cents"] is not None
    ]
    return {
        "schema_version": VERSION + "-candidate-v1",
        "policy_id": policy["policy_id"],
        "policy_family": policy["os_family"],
        "posture": policy["posture"],
        "first_fill_sibling_response": policy[
            "first_fill_sibling_response_id"
        ],
        "ablations": policy.get("ablations") or [],
        "raw": raw,
        "percentages": {
            "C_over_D": raw["C"] / D_REQUIRED,
            "PC_over_D": raw["PC"] / D_REQUIRED,
            "PC_over_C": raw["PC"] / raw["C"] if raw["C"] else None,
            "S_over_C": raw["S"] / raw["C"] if raw["C"] else None,
            "IC_over_D": raw["IC"] / D_REQUIRED,
            "IC_over_C": raw["IC"] / raw["C"] if raw["C"] else None,
        },
        "combined_entry_cost_cents": distribution(combined_costs),
        "combined_window1_close_delta_cents": distribution(
            combined_deltas
        ),
        "individual_leg_window1_close_delta_cents": distribution(
            individual_deltas
        ),
        "groups": {
            "by_date": grouped("event_date"),
            "by_tournament_class": grouped("tournament_class"),
            "by_start_source_class": grouped("start_source_class"),
            "by_feature_coverage_class": grouped(
                "feature_coverage_class"
            ),
        },
        "failure_census": dict(Counter(
            str(row["classification"]) for row in rows
            if not row["PC"]
        )),
        "feature_ceiling": {
            "events_with_all_16_feature_families": feature_full,
            "note": (
                "feature coverage is distinct from fill/data ceiling; "
                "missing features were not imputed"
            ),
        },
        "data_ceiling": {
            "strict_positive_boundary_events": sum(
                row["strict_positive_cutoff_utc"] is not None
                for row in rows
            ),
            "optimistic_queue_complete_events": optimistic,
            "note": (
                "a development miss is not a market ceiling"
            ),
        },
        "distance_from_target": {
            "target_PC": TARGET,
            "raw_shortfall": max(0, TARGET - raw["PC"]),
            "reached": raw["PC"] >= TARGET,
        },
    }


def select_candidate(
    summaries: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    return min(summaries, key=lambda row: (
        -int(row["raw"]["PC"]),
        -int(row["raw"]["C"]),
        -int(row["raw"]["IC"]),
        -int(row["raw"]["S"]),
        str(row["policy_id"]),
    ))


def evaluate(
    policies: Sequence[Mapping[str, Any]],
    events: Sequence[Mapping[str, Any]],
    starts: Mapping[str, Mapping[str, Any]],
    feature_map: Mapping[tuple[str, int, str], Mapping[str, Any]],
    market_cache_source: Path,
    expected_cache_key: str,
) -> dict[str, list[dict[str, Any]]]:
    output = {
        str(policy["policy_id"]): [] for policy in policies
    }
    for index, event in enumerate(events, 1):
        event_id = str(event["event_id"])
        start = starts[event_id]
        cutoff = strict_positive_cutoff(start)
        scheduled = fit.parse_utc(
            event["scheduled_start_exchange_ts"],
            "scheduled_start_exchange_ts",
        )
        left = scheduled - 8 * 3600
        if cutoff is None:
            feature_state = {
                "coverage_class": "start_boundary_censored",
                "available_feature_families": 0,
                "leg_states": [],
            }
            for policy in policies:
                outcome = empty_outcome(
                    str(policy["policy_id"]), event,
                    "start_boundary_censored",
                )
                output[str(policy["policy_id"])].append(
                    compact_event_record(
                        policy, event, start, outcome,
                        feature_state, None,
                    )
                )
            continue
        if left >= cutoff:
            feature_state = {
                "coverage_class": "window_left_after_guarded_start",
                "available_feature_families": 0,
                "leg_states": [],
            }
            for policy in policies:
                outcome = empty_outcome(
                    str(policy["policy_id"]), event,
                    "window_left_after_guarded_start",
                )
                output[str(policy["policy_id"])].append(
                    compact_event_record(
                        policy, event, start, outcome,
                        feature_state, cutoff,
                    )
                )
            continue

        leg_data = load_frozen_event_market(
            event, start, market_cache_source,
            expected_cache_key, left, cutoff,
        )
        contexts = fit.contexts_for_event(
            event, leg_data, [8], feature_map
        )[8]
        feature_state = event_feature_state(
            event, contexts, left, cutoff
        )
        for policy in policies:
            outcome = fit.event_candidate_outcome(
                str(policy["policy_id"]), policy, event,
                contexts, left, cutoff, scheduled,
            )
            output[str(policy["policy_id"])].append(
                compact_event_record(
                    policy, event, start, outcome,
                    feature_state, cutoff,
                )
            )
        if index % 25 == 0 or index == len(events):
            print(
                f"development_events={index}/{len(events)} "
                f"policies={len(policies)}",
                flush=True,
            )
    return output


def markdown(result: Mapping[str, Any]) -> str:
    selected = result["selected"]
    raw = selected["raw"]
    lines = [
        "# Corrected Window-1 OS-family development result",
        "",
        f"PRE-RUN commit: `{result['pre_run_commit']}`.",
        "",
        "Raw integers before percentages:",
        "",
        f"- D = {raw['D']}",
        f"- C = {raw['C']}",
        f"- PC = {raw['PC']}",
        f"- S = {raw['S']}",
        f"- IC = {raw['IC']}",
        f"- exact-five = {raw['exact_five']}",
        f"- partial = {raw['partial']}",
        f"- other-quantity = {raw['other_quantity']}",
        f"- nonfill = {raw['nonfill']}",
        f"- contradictory = {raw['contradictory']}",
        f"- censored = {raw['censored']}",
        "",
        f"Leading lawful policy: `{selected['policy_id']}`. "
        f"PC is {raw['PC']}/804; the fixed target is 603, a raw "
        f"shortfall of {selected['distance_from_target']['raw_shortfall']}.",
        "",
        "The result is development-only. Missing data stays in D. Feature "
        "coverage and data ceilings are reported separately; a miss is not "
        "called a market ceiling. The July 24-26 holdout was not queried.",
        "",
    ]
    return "\n".join(lines)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(
    path: Path, rows: Iterable[Mapping[str, Any]]
) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact(row) + "\n")


def run(args: argparse.Namespace) -> int:
    global _SURFACES
    repo = Path(args.repo).resolve()
    output = Path(args.output_dir).resolve()
    if output.exists():
        raise SearchError(f"refusing to overwrite: {output}")
    events_path = Path(args.events).resolve()
    prints_path = Path(args.prints).resolve()
    freeze_path = Path(args.pre_run_freeze).resolve()
    freeze = verify_prerun(
        repo, freeze_path, args.pre_run_commit, events_path
    )

    candidate_path = repo / args.candidates
    start_path = repo / args.start_ledger
    feature_path = repo / args.feature_matrix
    tape_manifest_path = Path(args.tape_manifest).resolve()
    events = fit.load_events(events_path)
    if {str(row["event_date"]) for row in events} - DEV_DATES:
        raise SearchError("event input contains non-development date")
    starts_list = read_jsonl(start_path)
    starts = {
        str(row["event_id"]): row for row in starts_list
    }
    if len(starts) != D_REQUIRED or set(starts) != {
        str(row["event_id"]) for row in events
    }:
        raise SearchError("corrected start/event population differs")
    strict_count = sum(
        strict_positive_cutoff(row) is not None
        for row in starts.values()
    )
    if strict_count != 705:
        raise SearchError(f"guarded positive ceiling changed: {strict_count}")

    feature_rows = read_jsonl(feature_path)
    feature_map = {
        (
            str(row["event_id"]),
            int(row["boundary_hours_before_schedule"]),
            str(row["ticker"]),
        ): row
        for row in feature_rows
        if int(row["boundary_hours_before_schedule"]) == 8
    }
    if len(feature_map) != 1608:
        raise SearchError(
            f"T-8 causal feature population changed: {len(feature_map)}"
        )
    prohibited_fields = {
        "shape_aim50_cents", "shape_dip50_cents",
        "shape_drift_cents", "shape_residual_sd",
    }
    # The old matrix contains those frozen columns, but this runner proves
    # its independent shape feature is unavailable and never reads them.
    if any(
        field in compact(_SURFACES)
        for field in prohibited_fields
    ):
        raise SearchError("prohibited AIM-derived field entered OS surfaces")

    allowlist = read_json(repo / args.feature_allowlist)
    _SURFACES = {
        "band_map": read_json(
            repo / ".claude/entrysurface_20260717/band_map_v1.json"
        ),
        "sealed": read_json(
            repo / (
                ".claude/entrysurface_20260717/"
                "entry_tables_sealed_v1.json"
            )
        ),
        "divot": read_json(
            repo / (
                ".claude/entrysurface_20260717/divot_tables_v1.json"
            )
        ),
        "drift": read_json(
            repo / (
                ".claude/entrysurface_20260717/drift_surfaces_v1.json"
            )
        ),
        "cohort": read_json(
            repo / ".claude/master_20260709/cohort.json"
        ),
        "orient": read_json(
            repo / ".claude/trendpath/ORIENT_V1.json"
        ),
        "recut": read_json(
            repo / ".claude/seqfloor_20260708/recut_cells.json"
        ),
        "atlas": read_json(
            repo / ".claude/trendpath/ATLAS_V1.json"
        ),
        "reach": read_json(
            repo / ".claude/takerreach/LAW.json"
        ),
        "allowed_features": list(allowlist["allowed"]),
    }
    if len(_SURFACES["allowed_features"]) != 16:
        raise SearchError("feature allowlist changed")

    tape_manifest = read_json(tape_manifest_path)
    frozen_tape_manifest_hash = (
        freeze.get("private_development_input_receipts", {})
        .get("public_tape_manifest", {}).get("sha256")
    )
    if sha256_file(tape_manifest_path) != frozen_tape_manifest_hash:
        raise SearchError("public tape manifest PRE-RUN binding failed")
    expected_print_hash = (
        tape_manifest.get("artifacts", {})
        .get("normalized_true_prints", {})
        .get("sha256")
    )
    frozen_print_hash = (
        freeze.get("private_development_input_receipts", {})
        .get("normalized_true_prints", {}).get("sha256")
    )
    if expected_print_hash != frozen_print_hash:
        raise SearchError("normalized true-print PRE-RUN binding failed")
    market_cache_source = Path(args.market_cache_source).resolve()
    frozen_market_cache = (
        freeze.get("private_development_input_receipts", {})
        .get("validated_event_market_cache", {})
    )
    current_market_cache = market_cache_receipt(market_cache_source)
    for field in ("files", "bytes", "hash_set_sha256"):
        if current_market_cache.get(field) != frozen_market_cache.get(field):
            raise SearchError(
                f"validated market-cache PRE-RUN drift: {field}"
            )
    expected_cache_key = str(frozen_market_cache.get("cache_key") or "")
    if not expected_cache_key:
        raise SearchError("validated market cache lacks cache key")

    spec = read_json(candidate_path)
    policies = candidate_policies(spec)
    if [row["policy_id"] for row in policies] != freeze.get(
        "candidate_policy_ids"
    ):
        raise SearchError("policy grid differs from PRE-RUN")

    cache_receipt = {
        "runner": VERSION,
        "events": sha256_file(events_path),
        "prints": expected_print_hash,
        "starts": sha256_file(start_path),
        "features": sha256_file(feature_path),
        "pre_run_commit": args.pre_run_commit,
    }
    cache_key = hashlib.sha256(compact(cache_receipt).encode()).hexdigest()
    fit.price_for_policy = family_price
    fit.build_actions = family_build_actions
    try:
        grid_rows = evaluate(
            policies, events, starts, feature_map,
            market_cache_source, expected_cache_key,
        )
        summaries = [
            summarize_candidate(
                policy, grid_rows[str(policy["policy_id"])]
            )
            for policy in policies
        ]
        selected_summary = select_candidate(summaries)
        selected_policy = next(
            policy for policy in policies
            if policy["policy_id"] == selected_summary["policy_id"]
        )
        ablation_policies = []
        for ablation in spec["predeclared_ablations"]:
            policy = dict(selected_policy)
            policy["policy_id"] = (
                selected_policy["policy_id"] + "__" + ablation
            )
            policy["ablations"] = [ablation]
            if ablation == "without_first_fill_sibling_response":
                policy["first_fill_response"] = "hold"
            if ablation == "without_true_print_walk":
                policy["placement_rule"] = "touch"
                policy["posture"] = "park"
            ablation_policies.append(policy)
        ablation_rows = evaluate(
            ablation_policies, events, starts, feature_map,
            market_cache_source, expected_cache_key,
        )
        ablations = [
            summarize_candidate(
                policy, ablation_rows[str(policy["policy_id"])]
            )
            for policy in ablation_policies
        ]
    finally:
        fit.price_for_policy = _ORIGINAL_PRICE
        fit.build_actions = _ORIGINAL_BUILD_ACTIONS

    selected_rows = grid_rows[selected_summary["policy_id"]]
    result = {
        "schema_version": VERSION,
        "pre_run_commit": args.pre_run_commit,
        "D": D_REQUIRED,
        "target_PC": TARGET,
        "holdout_opened": False,
        "holdout_queried": False,
        "development_dates": sorted(DEV_DATES),
        "candidate_count": len(summaries),
        "selected_policy_id": selected_summary["policy_id"],
        "selected": selected_summary,
        "candidates": summaries,
        "ablation_count": len(ablations),
        "ablations": ablations,
        "invariants": {
            "D_immutable": True,
            "source_conservation_held": True,
            "guarded_positive_ceiling": strict_count,
            "candidate_allowlist_held": True,
            "adapter_hash_held": True,
            "metric_hash_held": True,
            "source_hashes_held": True,
            "schedule_as_start_used": False,
            "future_information_used": False,
            "narrow_proxy_substitution_used": False,
            "feature_gap_imputation_used": False,
            "full_depth_used": False,
            "pinnacle_used": False,
            "aim_v2_used": False,
            "holdout_opened": False,
        },
        "scope_clause": (
            "development-only July 12-20; a miss is not automatically a "
            "market ceiling; stop for independent audit"
        ),
    }

    output.mkdir(parents=True)
    result_path = output / "WINDOW1_OS_FAMILY_RESULTS.json"
    selected_path = output / "WINDOW1_OS_FAMILY_SELECTED_EVENTS.jsonl"
    ablation_path = output / "WINDOW1_OS_FAMILY_ABLATIONS.json"
    coverage_path = output / "WINDOW1_OS_FAMILY_FEATURE_COVERAGE.json"
    report_path = output / "WINDOW1_OS_FAMILY_REPORT.md"
    write_json(result_path, result)
    write_jsonl(selected_path, selected_rows)
    write_json(ablation_path, {
        "selected_policy_id": selected_summary["policy_id"],
        "ablations": ablations,
    })
    coverage_counter = Counter(
        row["feature_coverage_class"] for row in selected_rows
    )
    component_counts: Counter[str] = Counter()
    for row in selected_rows:
        for leg in row["feature_components_by_leg"]:
            for component, available in leg.items():
                if available:
                    component_counts[component] += 1
    write_json(coverage_path, {
        "D": D_REQUIRED,
        "selected_policy_id": selected_summary["policy_id"],
        "event_coverage_classes": dict(sorted(coverage_counter.items())),
        "available_leg_component_counts": dict(
            sorted(component_counts.items())
        ),
        "required_legs": 1608,
        "shape_corpus": (
            "unavailable per event: no independent non-AIM causal cell "
            "mapping; not imputed"
        ),
        "full_depth": "unavailable; not used",
    })
    report_path.write_text(markdown(result), encoding="utf-8")
    artifacts = {}
    for path in (
        result_path, selected_path, ablation_path,
        coverage_path, report_path,
    ):
        artifacts[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    write_json(output / "ARTIFACT_MANIFEST.json", {
        "schema_version": VERSION + "-manifest-v1",
        "pre_run_commit": args.pre_run_commit,
        "D": D_REQUIRED,
        "holdout_opened": False,
        "private_paths_included": False,
        "artifacts": artifacts,
    })
    print(json.dumps({
        "selected_policy_id": selected_summary["policy_id"],
        "raw": selected_summary["raw"],
        "target": TARGET,
        "shortfall": selected_summary[
            "distance_from_target"
        ]["raw_shortfall"],
        "holdout_opened": False,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", default=Path(__file__).parents[2])
    result.add_argument("--pre-run-freeze", required=True)
    result.add_argument("--pre-run-commit", required=True)
    result.add_argument("--events", required=True)
    result.add_argument("--prints", required=True)
    result.add_argument("--market-cache-source", required=True)
    result.add_argument(
        "--candidates",
        default=(
            "arb-executor/docs/research/window1/"
            "WINDOW1_OS_FAMILY_CANDIDATES_V1.json"
        ),
    )
    result.add_argument(
        "--feature-allowlist",
        default=(
            "arb-executor/docs/research/window1/"
            "WINDOW1_OS_FAMILY_FEATURE_ALLOWLIST_V1.json"
        ),
    )
    result.add_argument(
        "--start-ledger",
        default=(
            ".claude/window1_start_guard_corrected_20260724/"
            "REAL_START_LEDGER_V5.jsonl"
        ),
    )
    result.add_argument(
        "--feature-matrix",
        default=".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl",
    )
    result.add_argument("--tape-manifest", required=True)
    result.add_argument("--output-dir", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
