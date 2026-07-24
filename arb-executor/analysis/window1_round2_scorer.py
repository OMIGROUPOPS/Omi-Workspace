#!/usr/bin/env python3
"""Pure deterministic scorer for frozen Round-2 Window-1 streams.

The scoring core has no market, network, policy-generation, production, or
holdout interface.  It accepts only a fully receipt-bound scoring bundle and
the immutable PRE-RUN scorer contract.  Candidate performance must not be
executed until a later independently authorized run.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


VERSION = "window1-round2-deterministic-scorer-v1"
D_REQUIRED = 804
LOT = 5.0
DEVELOPMENT_DATES = [
    f"2026-07-{day:02d}" for day in range(12, 21)
]
SEALED_HOLDOUT_DATES = [
    f"2026-07-{day:02d}" for day in range(24, 27)
]
POSITIVE_START_CLASSES = {
    "official_exact",
    "quantized_late_detection_proxy",
    "clean_causal_interval",
}
CENSORED_START_CLASSES = {
    "schedule_only",
    "live_by_only",
}
FORBIDDEN_RAW_START_FIELDS = {
    "evaluation_real_start_ts",
    "realized_start_utc",
    "raw_realized_start_ts",
    "raw_start_ts",
    "unGuarded_start_utc",
}
SECTION_NAMES = (
    "event_ledger",
    "candidate_order_streams",
    "fill_evidence",
    "start_boundaries",
    "references",
    "feature_classifications",
    "data_binding_manifest",
)
EVENT_SECTION_NAMES = SECTION_NAMES[1:6]


class ScoringError(RuntimeError):
    """Raised when a frozen scorer contract or input is violated."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def normalized_source_sha256(value: bytes) -> str:
    return hashlib.sha256(
        value.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def parse_timestamp(value: Any) -> float:
    if isinstance(value, bool):
        raise ScoringError("boolean is not a timestamp")
    if isinstance(value, (int, float)):
        timestamp = float(value)
    elif isinstance(value, str) and value.strip():
        try:
            timestamp = dt.datetime.fromisoformat(
                value.replace("Z", "+00:00")
            ).timestamp()
        except ValueError as exc:
            raise ScoringError(f"invalid timestamp: {value}") from exc
    else:
        raise ScoringError("timestamp is missing")
    if not math.isfinite(timestamp):
        raise ScoringError("timestamp is not finite")
    return timestamp


def _finite(value: Any, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ScoringError(f"{field} is not numeric") from exc
    if not math.isfinite(result):
        raise ScoringError(f"{field} is not finite")
    return result


def _same(left: float, right: float, tolerance: float = 1e-6) -> bool:
    return abs(float(left) - float(right)) <= tolerance


def _leg_identity(leg: Mapping[str, Any]) -> str:
    return str(leg.get("leg_id") or leg.get("leg") or "")


def _require_keys(
    value: Mapping[str, Any], required: set[str], label: str,
) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise ScoringError(f"{label} missing: {','.join(missing)}")


def strict_cutoff(
    boundary: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive the V5 positive cutoff with its frozen directionality."""
    leaked = sorted(FORBIDDEN_RAW_START_FIELDS & set(boundary))
    if leaked:
        raise ScoringError(
            "raw realized start field is forbidden: " + ",".join(leaked)
        )
    _require_keys(
        boundary,
        {
            "event_id",
            "schema_version",
            "start_source_class",
            "selected_source",
            "selected_source_family",
            "positive_window1_provable",
        },
        "start provenance",
    )
    source_class = str(boundary["start_source_class"])
    if source_class == "contradictory":
        if str(boundary.get("conflict_status") or "none") == "none":
            raise ScoringError("contradictory start lacks conflict provenance")
        return {
            "status": "contradictory",
            "source_class": source_class,
            "boundary_timestamp": None,
            "guard_seconds": None,
            "guard_id": None,
            "direction": None,
        }
    if source_class in CENSORED_START_CLASSES:
        if boundary.get("positive_window1_provable") is not False:
            raise ScoringError(
                f"{source_class} may not prove positive Window 1"
            )
        if source_class == "schedule_only" and not boundary.get(
            "schedule_source"
        ):
            raise ScoringError("schedule-only row lacks schedule provenance")
        return {
            "status": "censored",
            "source_class": source_class,
            "boundary_timestamp": None,
            "guard_seconds": None,
            "guard_id": None,
            "direction": None,
        }
    if source_class not in POSITIVE_START_CLASSES:
        raise ScoringError(f"unknown start source class: {source_class}")
    if boundary.get("positive_window1_provable") is not True:
        reason = str(boundary.get("guard_censor_reason") or "")
        if not reason:
            raise ScoringError(
                "positive-capable source lacks named guard censor"
            )
        guard = boundary.get("guard_band") or {}
        return {
            "status": "censored",
            "source_class": source_class,
            "boundary_timestamp": None,
            "guard_seconds": guard.get("positive_guard_seconds"),
            "guard_id": guard.get("guard_id"),
            "direction": "censored_before_cutoff_application",
            "guard_censor_reason": reason,
        }
    guard = boundary.get("guard_band")
    if not isinstance(guard, Mapping):
        raise ScoringError("positive start lacks V5 guard band")
    guard_id = str(guard.get("guard_id") or "")
    positive_guard = _finite(
        guard.get("positive_guard_seconds"),
        "positive_guard_seconds",
    )
    if source_class == "official_exact":
        expected_id = "official-point-strict-60s-v1"
        anchor = parse_timestamp(boundary.get("exact_start_utc"))
        expected_guard = 60.0
        anchor_field = "exact_start_utc"
    elif source_class == "quantized_late_detection_proxy":
        expected_id = "te-calibration-central-93pct-asymmetric-v1"
        anchor = parse_timestamp(boundary.get("proxy_clock_utc"))
        expected_guard = 900.0
        anchor_field = "proxy_clock_utc"
        if not _same(
            _finite(
                guard.get("negative_guard_seconds"),
                "negative_guard_seconds",
            ),
            600.0,
        ):
            raise ScoringError("proxy negative guard changed")
    else:
        expected_id = "causal-interval-strict-60s-v1"
        interval = boundary.get("start_interval_utc")
        if not isinstance(interval, Mapping):
            raise ScoringError("clean interval lacks interval provenance")
        anchor = parse_timestamp(interval.get("lower_inclusive"))
        expected_guard = 60.0
        anchor_field = "start_interval_utc.lower_inclusive"
    if guard_id != expected_id or not _same(
        positive_guard, expected_guard
    ):
        raise ScoringError("V5 guarded strict cutoff law changed")
    cutoff = anchor - positive_guard
    if source_class == "quantized_late_detection_proxy":
        committed = parse_timestamp(
            guard.get("strict_window1_completion_lte_utc")
        )
        if not _same(cutoff, committed):
            raise ScoringError("proxy cutoff directionality changed")
    return {
        "status": "positive",
        "source_class": source_class,
        "boundary_timestamp": cutoff,
        "boundary_utc": dt.datetime.fromtimestamp(
            cutoff, tz=dt.timezone.utc
        ).isoformat(),
        "anchor_timestamp": anchor,
        "anchor_field": anchor_field,
        "guard_seconds": positive_guard,
        "guard_id": guard_id,
        "direction": "anchor_minus_positive_guard",
    }


def _validate_positive_fill_evidence(
    row: Mapping[str, Any],
) -> tuple[str, float, float]:
    identity = str(
        row.get("trade_id") or row.get("receipt_id") or ""
    ).strip()
    if not identity:
        raise ScoringError("fill evidence lacks receipt identity")
    if row.get("size_verified") is not True:
        raise ScoringError("fill evidence size is not verified")
    size = _finite(row.get("size"), "fill evidence size")
    if size <= 0:
        raise ScoringError("fill evidence size is not positive")
    if row.get("synthetic_transition") is True:
        raise ScoringError("synthetic transition cannot prove a fill")
    if str(row.get("source") or "") not in {
        "normalized_public_true_print",
        "independently_size_verified_public_trade",
    }:
        raise ScoringError("fill evidence source is unproved")
    return identity, parse_timestamp(row.get("ts")), size


def _validate_policy_result(
    event: Mapping[str, Any],
    result: Mapping[str, Any],
    candidate_id: str,
    expected_stream_sha256: str | None = None,
) -> None:
    if (
        str(result.get("candidate_id")) != candidate_id
        or str(result.get("event_id")) != str(event["event_id"])
        or str(result.get("event_date")) != str(event["event_date"])
    ):
        raise ScoringError("candidate stream identity changed")
    if (
        result.get("scored") is not False
        or result.get("metrics") is not None
        or result.get("holdout_queried") is not False
        or result.get("evaluation_truth_present") is not False
    ):
        raise ScoringError("policy stream is not frozen score-free output")
    order_stream = result.get("order_stream")
    if not isinstance(order_stream, list):
        raise ScoringError("candidate order stream is missing")
    if canonical_sha256(order_stream) != result.get("stream_sha256"):
        raise ScoringError("candidate order stream hash changed")
    if (
        expected_stream_sha256 is not None
        and result.get("stream_sha256") != expected_stream_sha256
    ):
        raise ScoringError("candidate stream is outside frozen receipts")
    expected_legs = {_leg_identity(row) for row in event["legs"]}
    if set(result.get("leg_streams") or {}) != expected_legs:
        raise ScoringError("candidate stream leg identity changed")


def _fill_rows_by_leg(
    event: Mapping[str, Any],
    result: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
    cutoff: float,
) -> dict[str, list[dict[str, float | str]]]:
    event_id = str(event["event_id"])
    evidence_by_key: dict[tuple[str, str], tuple[Mapping[str, Any], float, float]] = {}
    for row in evidence:
        if str(row.get("event_id")) != event_id:
            raise ScoringError("fill evidence event identity changed")
        ticker = str(row.get("ticker") or "")
        identity, timestamp, size = _validate_positive_fill_evidence(row)
        key = (ticker, identity)
        if key in evidence_by_key:
            raise ScoringError("duplicate public fill evidence receipt")
        evidence_by_key[key] = (row, timestamp, size)
    by_leg: dict[str, list[dict[str, float | str]]] = {
        _leg_identity(row): [] for row in event["legs"]
    }
    ticker_by_leg = {
        _leg_identity(row): str(row["ticker"]) for row in event["legs"]
    }
    used: set[tuple[str, str]] = set()
    for row in result["order_stream"]:
        if row.get("action") != "fill_observed":
            continue
        leg_id = str(row.get("leg_id") or "")
        ticker = str(row.get("ticker") or "")
        if leg_id not in by_leg or ticker_by_leg[leg_id] != ticker:
            raise ScoringError("fill action leg identity changed")
        identity = str(
            row.get("trade_id") or row.get("receipt_id") or ""
        ).strip()
        key = (ticker, identity)
        if not identity or key not in evidence_by_key:
            raise ScoringError("fill action lacks bound public receipt")
        if key in used:
            raise ScoringError("duplicate fill receipt cannot inflate quantity")
        used.add(key)
        _, evidence_ts, evidence_size = evidence_by_key[key]
        fill_ts = parse_timestamp(row.get("ts"))
        fill_quantity = _finite(
            row.get("fill_quantity"), "fill quantity"
        )
        order_price = _finite(
            row.get("order_price_cents"), "order fill price"
        )
        if (
            fill_quantity <= 0
            or fill_quantity > evidence_size + 1e-9
            or not _same(fill_ts, evidence_ts)
        ):
            raise ScoringError("fill action/public receipt mismatch")
        if fill_ts <= cutoff:
            by_leg[leg_id].append({
                "receipt_id": identity,
                "timestamp": fill_ts,
                "quantity": fill_quantity,
                "price_cents": order_price,
            })
    return by_leg


def _classification(
    quantities: Sequence[float],
) -> str:
    positive = [value > 1e-9 for value in quantities]
    if all(_same(value, LOT) for value in quantities):
        return "exact_five"
    if sum(positive) == 1:
        return "naked_single_leg"
    if not any(positive):
        return "genuine_nonfill"
    if any(0 < value < LOT for value in quantities):
        return "partial"
    return "other_quantity"


def score_event(
    event: Mapping[str, Any],
    policy_result: Mapping[str, Any],
    fill_evidence: Sequence[Mapping[str, Any]],
    start_boundary: Mapping[str, Any],
    references: Mapping[str, Any],
    feature_classification: Mapping[str, Any],
    candidate_id: str,
    expected_stream_sha256: str | None = None,
) -> dict[str, Any]:
    """Score one already-bound event; used by population scorer and fixtures."""
    event_id = str(event.get("event_id") or "")
    event_date = str(event.get("event_date") or "")
    if not event_id:
        raise ScoringError("event identity missing")
    if event_date in SEALED_HOLDOUT_DATES:
        raise ScoringError("sealed holdout date refused")
    if event_date not in DEVELOPMENT_DATES:
        raise ScoringError("non-development date refused")
    legs = list(event.get("legs") or [])
    if len(legs) != 2:
        raise ScoringError("event must contain exactly two legs")
    if len({_leg_identity(row) for row in legs}) != 2 or len({
        str(row["ticker"]) for row in legs
    }) != 2:
        raise ScoringError("event leg identity is not unique")
    if str(start_boundary.get("event_id")) != event_id:
        raise ScoringError("start-boundary event identity changed")
    _validate_policy_result(
        event,
        policy_result,
        candidate_id,
        expected_stream_sha256,
    )
    boundary = strict_cutoff(start_boundary)
    cohort_no_calls = int(
        feature_classification.get("cohort_NO_CALL_count") or 0
    )
    reaim_no_calls = int(
        feature_classification.get("reaim_NO_CALL_count") or 0
    )
    feature_unavailable = sorted(set(map(
        str, feature_classification.get("feature_unavailable") or []
    )))
    censor_reasons = sorted(set(map(
        str, feature_classification.get("censor_reasons") or []
    )))
    if feature_classification.get("censored") is True and not censor_reasons:
        raise ScoringError("feature censor lacks named reason")
    base = {
        "event_id": event_id,
        "event_date": event_date,
        "candidate_id": candidate_id,
        "cohort_NO_CALL_count": cohort_no_calls,
        "reaim_NO_CALL_count": reaim_no_calls,
        "feature_unavailable": feature_unavailable,
        "feature_censor_reasons": censor_reasons,
        "C": False,
        "PC": False,
        "S": False,
        "IC": False,
        "combined_entry_cost_cents": None,
        "combined_window1_close_delta_cents": None,
        "individual_leg_window1_close_delta_cents": None,
    }
    if boundary["status"] == "contradictory":
        return {
            **base,
            "classification": "contradictory",
            "leg_results": [
                {
                    "leg_id": _leg_identity(leg),
                    "ticker": leg["ticker"],
                    "boundary": dict(boundary),
                }
                for leg in legs
            ],
        }
    if boundary["status"] == "censored":
        return {
            **base,
            "classification": "censored",
            "censor_reasons": [
                f"start_boundary:{boundary['source_class']}"
            ],
            "leg_results": [
                {
                    "leg_id": _leg_identity(leg),
                    "ticker": leg["ticker"],
                    "boundary": dict(boundary),
                }
                for leg in legs
            ],
        }
    cutoff = float(boundary["boundary_timestamp"])
    activation = parse_timestamp(
        policy_result.get("policy_clock", {}).get(
            "policy_activation_ts"
        )
    )
    if cutoff <= activation:
        return {
            **base,
            "classification": "zero_length_window",
            "leg_results": [
                {
                    "leg_id": _leg_identity(leg),
                    "ticker": leg["ticker"],
                    "boundary": dict(boundary),
                }
                for leg in legs
            ],
        }
    if censor_reasons or feature_unavailable:
        return {
            **base,
            "classification": "censored",
            "censor_reasons": censor_reasons + [
                f"feature_unavailable:{name}"
                for name in feature_unavailable
            ],
            "leg_results": [
                {
                    "leg_id": _leg_identity(leg),
                    "ticker": leg["ticker"],
                    "boundary": dict(boundary),
                }
                for leg in legs
            ],
        }
    fills = _fill_rows_by_leg(
        event, policy_result, fill_evidence, cutoff
    )
    leg_results = []
    for leg in legs:
        leg_id = _leg_identity(leg)
        ticker = str(leg["ticker"])
        rows = fills[leg_id]
        quantity = sum(float(row["quantity"]) for row in rows)
        total_cost = sum(
            float(row["quantity"]) * float(row["price_cents"])
            for row in rows
        )
        vwap = total_cost / quantity if quantity > 0 else None
        reference = references.get(ticker)
        reference_available = (
            isinstance(reference, Mapping)
            and reference.get("available") is True
            and reference.get("window1_close_cents") is not None
        )
        close = (
            _finite(
                reference["window1_close_cents"],
                "Window-1-close reference",
            )
            if reference_available else None
        )
        leg_results.append({
            "leg_id": leg_id,
            "ticker": ticker,
            "inside_window_quantity": quantity,
            "inside_window_fill_receipts": rows,
            "entry_vwap_cents": vwap,
            "window1_close_reference_cents": close,
            "individual_delta_cents": (
                vwap - close
                if vwap is not None and close is not None else None
            ),
            "boundary": dict(boundary),
        })
    quantities = [
        float(row["inside_window_quantity"]) for row in leg_results
    ]
    classification = _classification(quantities)
    if classification == "exact_five" and any(
        row["window1_close_reference_cents"] is None
        for row in leg_results
    ):
        return {
            **base,
            "classification": "censored",
            "censor_reasons": [
                "feature_unavailable:window1_close_reference"
            ],
            "leg_results": leg_results,
        }
    completed = classification == "exact_five"
    costs = [
        row["entry_vwap_cents"] for row in leg_results
    ]
    deltas = [
        row["individual_delta_cents"] for row in leg_results
    ]
    combined_cost = (
        sum(float(value) for value in costs)
        if completed else None
    )
    combined_delta = (
        sum(float(value) for value in deltas)
        if completed else None
    )
    return {
        **base,
        "classification": classification,
        "C": completed,
        "PC": bool(completed and combined_delta < 0),
        "S": bool(completed and combined_cost < 100),
        "IC": bool(
            completed and all(float(value) < 0 for value in deltas)
        ),
        "combined_entry_cost_cents": combined_cost,
        "combined_window1_close_delta_cents": combined_delta,
        "individual_leg_window1_close_delta_cents": deltas,
        "leg_results": leg_results,
    }


def _validate_frozen_contract(
    bundle: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> str:
    if (
        contract.get("schema_version")
        != "window1-round2-scorer-contract-v1"
        or contract.get("scorer_version") != VERSION
        or contract.get("D") != D_REQUIRED
        or contract.get("target_PC") != 603
        or contract.get("lot_per_leg") != 5
        or contract.get("development_dates") != DEVELOPMENT_DATES
        or contract.get("sealed_holdout_dates") != SEALED_HOLDOUT_DATES
    ):
        raise ScoringError("frozen scorer contract changed")
    candidate_id = str(bundle.get("candidate_id") or "")
    if candidate_id not in (contract.get("candidate_ids") or []):
        raise ScoringError("candidate is outside frozen eight-candidate grid")
    lineage = bundle.get("freeze_lineage")
    expected = contract.get("freeze_lineage")
    if not isinstance(lineage, Mapping) or lineage != expected:
        raise ScoringError("post-freeze candidate or metric change")
    source_receipts = bundle.get("source_receipts")
    frozen_sources = contract.get("frozen_source_receipts")
    if (
        not isinstance(source_receipts, Mapping)
        or source_receipts != frozen_sources
    ):
        raise ScoringError("missing, changed, or unbound source receipt")
    return candidate_id


def score_population(
    bundle: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Score exactly one candidate over the immutable D=804 population."""
    candidate_id = _validate_frozen_contract(bundle, contract)
    sections = bundle.get("sections")
    receipts = bundle.get("section_receipts")
    if not isinstance(sections, Mapping) or not isinstance(
        receipts, Mapping
    ):
        raise ScoringError("bound scoring sections are missing")
    if set(sections) != set(SECTION_NAMES) or set(receipts) != set(
        SECTION_NAMES
    ):
        raise ScoringError("unbound scoring input section")
    for name in SECTION_NAMES:
        receipt = receipts[name]
        if (
            not isinstance(receipt, Mapping)
            or receipt.get("canonical_sha256")
            != canonical_sha256(sections[name])
            or receipt.get("source_sha256")
            != contract["frozen_source_receipts"][name]
        ):
            raise ScoringError(f"changed input hash: {name}")
    ledger = list(sections["event_ledger"])
    data_binding = sections["data_binding_manifest"]
    if (
        not isinstance(data_binding, Mapping)
        or data_binding.get("D") != D_REQUIRED
        or data_binding.get("leg_identities") != 1608
        or data_binding.get("binding_bundle_sha256")
        != contract["freeze_lineage"]["data_binding"]
        or data_binding.get("holdout_dates_present_in_any_input") != 0
        or data_binding.get("holdout_queried") is not False
    ):
        raise ScoringError("immutable data-binding manifest changed")
    if len(ledger) != D_REQUIRED:
        raise ScoringError("D=804 denominator changed")
    event_ids = [str(row.get("event_id") or "") for row in ledger]
    if len(set(event_ids)) != D_REQUIRED or any(not value for value in event_ids):
        raise ScoringError("event identities are not the frozen D=804 set")
    dates = {str(row.get("event_date") or "") for row in ledger}
    if not dates.issubset(set(DEVELOPMENT_DATES)):
        raise ScoringError("outside-date or holdout event refused")
    tickers = [
        str(leg.get("ticker") or "")
        for event in ledger for leg in event.get("legs") or []
    ]
    if (
        any(len(event.get("legs") or []) != 2 for event in ledger)
        or len(tickers) != 1608
        or len(set(tickers)) != 1608
    ):
        raise ScoringError("1,608-leg identity contract changed")
    identities = sorted(
        (
            {
                "event_id": str(event["event_id"]),
                "event_date": str(event["event_date"]),
                "leg_id": _leg_identity(leg),
                "ticker": str(leg.get("ticker") or ""),
            }
            for event in ledger for leg in event.get("legs") or []
        ),
        key=lambda row: (
            row["event_id"], row["leg_id"], row["ticker"]
        ),
    )
    if (
        identities != contract.get("frozen_event_leg_identities")
        or canonical_sha256(identities)
        != contract.get("frozen_event_leg_identities_sha256")
    ):
        raise ScoringError("event or leg identity is outside frozen ledger")
    all_stream_receipts = contract.get("candidate_stream_receipts")
    if (
        not isinstance(all_stream_receipts, Mapping)
        or set(all_stream_receipts)
        != set(contract.get("candidate_ids") or [])
        or canonical_sha256(all_stream_receipts)
        != contract.get("candidate_stream_receipts_sha256")
    ):
        raise ScoringError("candidate stream receipt manifest changed")
    candidate_stream_receipts = all_stream_receipts.get(candidate_id)
    if (
        not isinstance(candidate_stream_receipts, Mapping)
        or set(candidate_stream_receipts) != set(event_ids)
        or any(
            not isinstance(value, str) or len(value) != 64
            for value in candidate_stream_receipts.values()
        )
    ):
        raise ScoringError("candidate stream receipts are incomplete")
    by_section: dict[str, Mapping[str, Any]] = {}
    for name in EVENT_SECTION_NAMES:
        section = sections[name]
        if not isinstance(section, Mapping) or set(section) != set(
            event_ids
        ):
            raise ScoringError(f"unknown or missing event in {name}")
        by_section[name] = section
    event_rows = []
    for event in ledger:
        event_id = str(event["event_id"])
        event_rows.append(score_event(
            event,
            by_section["candidate_order_streams"][event_id],
            by_section["fill_evidence"][event_id],
            by_section["start_boundaries"][event_id],
            by_section["references"][event_id],
            by_section["feature_classifications"][event_id],
            candidate_id,
            candidate_stream_receipts[event_id],
        ))
    census_keys = [
        "exact_five",
        "partial",
        "other_quantity",
        "genuine_nonfill",
        "naked_single_leg",
        "zero_length_window",
        "contradictory",
        "censored",
    ]
    census = {
        key: sum(row["classification"] == key for row in event_rows)
        for key in census_keys
    }
    if sum(census.values()) != D_REQUIRED:
        raise ScoringError("event census does not conserve to D=804")
    raw = {
        "D": D_REQUIRED,
        "C": sum(bool(row["C"]) for row in event_rows),
        "PC": sum(bool(row["PC"]) for row in event_rows),
        "S": sum(bool(row["S"]) for row in event_rows),
        "IC": sum(bool(row["IC"]) for row in event_rows),
        **census,
        "genuine_zero_fill": census["genuine_nonfill"],
        "cohort_NO_CALL": sum(
            int(row["cohort_NO_CALL_count"]) for row in event_rows
        ),
        "reaim_NO_CALL": sum(
            int(row["reaim_NO_CALL_count"]) for row in event_rows
        ),
        "feature_unavailable": sum(
            len(row["feature_unavailable"]) for row in event_rows
        ),
    }
    rates = {
        "C_over_D": raw["C"] / D_REQUIRED,
        "PC_over_D": raw["PC"] / D_REQUIRED,
        "PC_over_C": (
            raw["PC"] / raw["C"] if raw["C"] else None
        ),
        "S_over_C": raw["S"] / raw["C"] if raw["C"] else None,
        "IC_over_D": raw["IC"] / D_REQUIRED,
        "IC_over_C": raw["IC"] / raw["C"] if raw["C"] else None,
    }
    output = {
        "schema_version": VERSION + "-result-v1",
        "candidate_id": candidate_id,
        "raw_integer_metrics_before_percentages": raw,
        "rates_after_raw_integers": rates,
        "event_results": event_rows,
        "metric_definitions": contract["metric_definitions"],
        "source_receipts": dict(bundle["source_receipts"]),
        "section_receipts": dict(bundle["section_receipts"]),
        "freeze_lineage": dict(bundle["freeze_lineage"]),
        "census_conserves_to_D": sum(census.values()) == D_REQUIRED,
        "holdout_queried": False,
    }
    output["result_sha256"] = canonical_sha256(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score one frozen Round-2 candidate after authorization."
    )
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--expected-contract-sha256", required=True,
        help="SHA-256 frozen in the PRE-RUN manifest",
    )
    args = parser.parse_args()
    contract_bytes = args.contract.read_bytes()
    if hashlib.sha256(contract_bytes).hexdigest() != (
        args.expected_contract_sha256
    ):
        raise ScoringError("scorer contract file hash changed")
    contract = json.loads(contract_bytes)
    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    result = score_population(bundle, contract)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(compact({
        "candidate_id": result["candidate_id"],
        "result_sha256": result["result_sha256"],
        "D": D_REQUIRED,
        "holdout_queried": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
