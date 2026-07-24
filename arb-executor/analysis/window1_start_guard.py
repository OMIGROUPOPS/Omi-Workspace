#!/usr/bin/env python3
"""Corrected Window-1 start-boundary semantics.

This module is deliberately policy-blind.  It converts the frozen V4
TennisExplorer result clocks into calibrated, five-minute-quantized
late-detection proxy intervals and exposes the only lawful boundary
comparators used by the corrected development scorer.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Mapping


VERSION = "window1-start-boundary-law-v1"
UTC = dt.timezone.utc

OFFICIAL_STRICT_GUARD_SECONDS = 60.0
PROXY_POSITIVE_GUARD_SECONDS = 900.0
PROXY_NEGATIVE_GUARD_SECONDS = 600.0
PROXY_GUARD_ID = "te-calibration-central-93pct-asymmetric-v1"
OFFICIAL_GUARD_ID = "official-point-strict-60s-v1"
INTERVAL_GUARD_ID = "causal-interval-strict-60s-v1"

TENNIS_EXPLORER_SOURCE = (
    "tennisexplorer_historical_result_start_clock"
)
NAMED_PROXY_CENSORS = {
    "KXATPCHALLENGERMATCH-26JUL14MAKSEY":
        "provider_final_start_differs_by_about_20h",
    "KXATPCHALLENGERMATCH-26JUL15NAPBAR":
        "provider_final_start_differs_by_about_16h",
    "KXATPCHALLENGERMATCH-26JUL17DELFUE":
        "proxy_precedes_retained_live_by_conflict",
    "KXATPMATCH-26JUL15KYMTSI":
        "provider_final_start_differs_by_about_21h",
    "KXATPMATCH-26JUL16SHESTR":
        "provider_final_start_differs_by_about_16h",
    "KXATPMATCH-26JUL19MOLOFN":
        "retained_causal_live_by_conflicts_with_proxy_band",
    "KXWTAMATCH-26JUL15BURJAC":
        "retained_causal_live_by_conflicts_with_proxy_band",
    "KXATPMATCH-26JUL16BURUGO":
        "retained_causal_live_by_conflicts_with_proxy_band",
    "KXATPCHALLENGERMATCH-26JUL14MATMOR":
        "retained_causal_live_by_conflicts_with_proxy_band",
    "KXATPMATCH-26JUL18COLCER":
        "retained_causal_live_by_conflicts_with_proxy_band",
    "KXATPMATCH-26JUL18CORSAC":
        "retained_causal_live_by_conflicts_with_proxy_band",
    "KXATPMATCH-26JUL15TRUDAV":
        "retained_causal_live_by_conflicts_with_proxy_band",
    "KXATPMATCH-26JUL15ALTDAR":
        "retained_causal_live_by_conflicts_with_proxy_band",
}


class StartGuardError(RuntimeError):
    """A corrected start-boundary invariant failed."""


def parse_utc(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("Z", "+00:00")
    stamp = dt.datetime.fromisoformat(text)
    if stamp.tzinfo is None:
        raise StartGuardError(f"timezone-free timestamp: {value!r}")
    return stamp.timestamp()


def iso_utc(value: float | None) -> str | None:
    if value is None:
        return None
    return dt.datetime.fromtimestamp(value, UTC).isoformat()


def is_te_proxy(row: Mapping[str, Any]) -> bool:
    return (
        row.get("selected_source") == TENNIS_EXPLORER_SOURCE
        or row.get("start_source_class")
        == "quantized_late_detection_proxy"
        or row.get("precision_class")
        == "quantized_late_detection_proxy"
    )


def _candidate_bounds(
    row: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    live_by: list[dict[str, Any]] = []
    not_live: list[dict[str, Any]] = []
    for raw in row.get("candidate_sources") or []:
        candidate = dict(raw)
        stamp = parse_utc(candidate.get("timestamp_utc"))
        if stamp is None:
            continue
        if candidate.get("source") == TENNIS_EXPLORER_SOURCE:
            candidate["direction"] = "quantized_late_detection_proxy"
            candidate["precision"] = "five_minute_quantized"
            continue
        direction = str(candidate.get("direction") or "")
        if direction in {"live_by", "exact"}:
            candidate["_stamp"] = stamp
            live_by.append(candidate)
        elif direction == "not_live_through":
            candidate["_stamp"] = stamp
            not_live.append(candidate)
    return live_by, not_live


def repair_v4_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return a public-safe V5 boundary row without changing D membership."""
    repaired = dict(row)
    repaired["schema_version"] = "window1-real-start-ledger-v5-guarded"
    repaired["start_boundary_law_version"] = VERSION
    repaired["source_partition_class"] = str(
        row.get("precision_class") or ""
    )
    repaired["guard_band"] = None
    repaired["guard_censor_reason"] = None

    if not is_te_proxy(row):
        precision = str(row.get("precision_class") or "")
        if precision == "exact":
            repaired["start_source_class"] = "official_exact"
            repaired["source_partition_class"] = "start_clock"
            repaired["guard_band"] = {
                "guard_id": OFFICIAL_GUARD_ID,
                "positive_guard_seconds": OFFICIAL_STRICT_GUARD_SECONDS,
                "negative_guard_seconds": OFFICIAL_STRICT_GUARD_SECONDS,
            }
        elif precision == "clean_interval":
            repaired["start_source_class"] = "clean_causal_interval"
            repaired["guard_band"] = {
                "guard_id": INTERVAL_GUARD_ID,
                "positive_guard_seconds": OFFICIAL_STRICT_GUARD_SECONDS,
                "negative_guard_seconds": OFFICIAL_STRICT_GUARD_SECONDS,
            }
        else:
            repaired["start_source_class"] = precision
        return repaired

    event_id = str(row.get("event_id") or "")
    proxy = parse_utc(
        row.get("proxy_clock_utc") or row.get("exact_start_utc")
    )
    if proxy is None:
        raise StartGuardError(f"TE proxy lacks clock: {event_id}")
    stamp = dt.datetime.fromtimestamp(proxy, UTC)
    if stamp.second != 0 or stamp.microsecond != 0 or stamp.minute % 5:
        raise StartGuardError(
            f"TE proxy is not on five-minute grid: {event_id}"
        )

    lower = proxy - PROXY_POSITIVE_GUARD_SECONDS
    upper = proxy + PROXY_NEGATIVE_GUARD_SECONDS
    live_by, not_live = _candidate_bounds(row)
    retained_live = min(
        live_by, key=lambda value: float(value["_stamp"]),
        default=None,
    )
    retained_not_live = max(
        not_live, key=lambda value: float(value["_stamp"]),
        default=None,
    )
    causal_live_by = (
        float(retained_live["_stamp"]) if retained_live else None
    )
    known_live_by = min(
        value for value in (causal_live_by, upper)
        if value is not None
    )

    repaired.update({
        "precision_class": "quantized_late_detection_proxy",
        "start_source_class": "quantized_late_detection_proxy",
        "source_partition_class": "start_clock",
        "proxy_clock_utc": iso_utc(proxy),
        "exact_start_utc": None,
        "verified_start_utc": None,
        "selected_timestamp_precision": "five_minute_quantized",
        "positive_window1_provable": event_id not in NAMED_PROXY_CENSORS,
        "known_live_by_utc": iso_utc(known_live_by),
        "known_live_by_source": (
            retained_live.get("source")
            if retained_live and causal_live_by == known_live_by
            else TENNIS_EXPLORER_SOURCE + ":calibrated_upper"
        ),
        "not_live_through_utc": (
            iso_utc(float(retained_not_live["_stamp"]))
            if retained_not_live else row.get("not_live_through_utc")
        ),
        "start_interval_utc": {
            "lower_inclusive": iso_utc(lower),
            "upper_inclusive": iso_utc(upper),
        },
        "guard_band": {
            "guard_id": PROXY_GUARD_ID,
            "positive_guard_seconds": PROXY_POSITIVE_GUARD_SECONDS,
            "negative_guard_seconds": PROXY_NEGATIVE_GUARD_SECONDS,
            "strict_window1_completion_lte_utc": iso_utc(lower),
            "strict_post_start_completion_gte_utc": iso_utc(upper),
            "calibration_population_official": 234,
            "calibration_comparable_unique": 222,
            "calibration_central_band_count": 207,
            "calibration_central_band_rate": 207 / 222,
            "calibration_median_proxy_minus_official_seconds": 300.0,
        },
        "one_sided_conflict_law": {
            "law_id": "retain-stronger-causal-bounds-v1",
            "proxy_may_never_overwrite_earlier_live_by": True,
            "strictly_higher_rank_not_live_may_block_proxy": True,
            "ties_may_not_promote_proxy_to_exact": True,
            "retained_live_by_utc": iso_utc(causal_live_by),
            "retained_live_by_source": (
                retained_live.get("source") if retained_live else None
            ),
        },
    })
    if event_id in NAMED_PROXY_CENSORS:
        repaired["guard_censor_reason"] = NAMED_PROXY_CENSORS[event_id]
        repaired["conflict_status"] = "named_proxy_conflict_censored"
    return repaired


def boundary_verdict(
    row: Mapping[str, Any],
    completion_exchange_ts: float,
    *,
    proxy_guard_override_seconds: float | None = None,
) -> dict[str, Any]:
    """Adjudicate one completion and print the guard beside the verdict."""
    completion = float(completion_exchange_ts)
    event_id = str(row.get("event_id") or "")
    precision = str(row.get("precision_class") or "")

    if is_te_proxy(row):
        proxy = parse_utc(
            row.get("proxy_clock_utc") or row.get("exact_start_utc")
        )
        if proxy is None:
            raise StartGuardError(f"proxy clock missing: {event_id}")
        if proxy_guard_override_seconds is None:
            positive_guard = PROXY_POSITIVE_GUARD_SECONDS
            negative_guard = PROXY_NEGATIVE_GUARD_SECONDS
            guard_id = PROXY_GUARD_ID
        else:
            positive_guard = negative_guard = float(
                proxy_guard_override_seconds
            )
            guard_id = (
                f"te-strict-{int(proxy_guard_override_seconds)}s-"
                "witness-only"
            )
        lower = proxy - positive_guard
        upper = proxy + negative_guard
        if event_id in NAMED_PROXY_CENSORS:
            verdict = "censored_named_proxy_conflict"
        elif completion <= lower:
            verdict = "strict_window1"
        elif completion >= upper:
            verdict = "strict_post_start"
        else:
            verdict = "censored_guard_band"
        return {
            "verdict": verdict,
            "guard_id": guard_id,
            "positive_guard_seconds": positive_guard,
            "negative_guard_seconds": negative_guard,
            "positive_cutoff_utc": iso_utc(lower),
            "negative_cutoff_utc": iso_utc(upper),
            "completion_exchange_ts": completion,
            "margin_to_proxy_seconds": proxy - completion,
        }

    guard = OFFICIAL_STRICT_GUARD_SECONDS
    if precision == "exact":
        exact = parse_utc(row.get("exact_start_utc"))
        if exact is None:
            raise StartGuardError(f"official exact missing: {event_id}")
        lower, upper = exact - guard, exact + guard
        verdict = (
            "strict_window1" if completion <= lower else
            "strict_post_start" if completion >= upper else
            "censored_guard_band"
        )
        guard_id = OFFICIAL_GUARD_ID
    elif precision == "clean_interval":
        interval = row.get("start_interval_utc") or {}
        lower_raw = parse_utc(interval.get("lower_inclusive"))
        upper_raw = parse_utc(interval.get("upper_inclusive"))
        if lower_raw is None or upper_raw is None:
            raise StartGuardError(f"clean interval incomplete: {event_id}")
        lower, upper = lower_raw - guard, upper_raw + guard
        verdict = (
            "strict_window1" if completion <= lower else
            "strict_post_start" if completion >= upper else
            "censored_guard_band"
        )
        guard_id = INTERVAL_GUARD_ID
    else:
        live_by = parse_utc(row.get("known_live_by_utc"))
        lower = None
        upper = live_by + guard if live_by is not None else None
        verdict = (
            "strict_post_start"
            if upper is not None and completion >= upper
            else "censored_no_positive_boundary"
        )
        guard_id = "one-sided-live-by-strict-60s-v1"
    return {
        "verdict": verdict,
        "guard_id": guard_id,
        "positive_guard_seconds": guard,
        "negative_guard_seconds": guard,
        "positive_cutoff_utc": iso_utc(lower),
        "negative_cutoff_utc": iso_utc(upper),
        "completion_exchange_ts": completion,
    }


def strict_positive_cutoff(row: Mapping[str, Any]) -> float | None:
    """Return the only right edge that may contribute to C/PC."""
    if row.get("guard_censor_reason"):
        return None
    precision = str(row.get("precision_class") or "")
    if is_te_proxy(row):
        proxy = parse_utc(
            row.get("proxy_clock_utc") or row.get("exact_start_utc")
        )
        return (
            proxy - PROXY_POSITIVE_GUARD_SECONDS
            if proxy is not None else None
        )
    if precision == "exact":
        exact = parse_utc(row.get("exact_start_utc"))
        return (
            exact - OFFICIAL_STRICT_GUARD_SECONDS
            if exact is not None else None
        )
    if precision == "clean_interval":
        lower = parse_utc(
            (row.get("start_interval_utc") or {}).get(
                "lower_inclusive"
            )
        )
        return (
            lower - OFFICIAL_STRICT_GUARD_SECONDS
            if lower is not None else None
        )
    return None
