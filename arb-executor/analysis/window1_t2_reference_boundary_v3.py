#!/usr/bin/env python3
"""V3 boundary compatibility and frozen-reference validation.

This module is deliberately score-free.  Raw V5 boundary rows are consumed
only while constructing the frozen reference ledger.  Runtime scoring consumes
that ledger through ``adapt_frozen_reference_rows`` and never supplies the
lossy normalized boundary contract to the raw V5 reference adapter.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from window1_range_attack_guarded_fill_adapter_v2 import exact_integer
from window1_range_attack_prerun_builder import boundary_contract
from window1_range_attack_reference_adapter_v1 import (
    ReferenceError,
    guarded_cutoff,
)
from window1_range_attack_reference_adapter_v2 import (
    AMBIGUOUS_REASON,
    Window1CloseReferenceV2,
    derive_window1_close_reference,
)
from window1_range_attack_scoring_runner_v1 import _load_cache


VERSION = "window1-t2-reference-boundary-v3"
RAW_V5_SHA256 = (
    "c6204d016aeeab9cec54c5f989e695cb74a13e40b8e25085a3a9410a2c5548ed"
)
NORMALIZED_SHA256 = (
    "c2c652dab2e382869a28785dd807cc8bb1bbe1c78842192ed39a54c685799faf"
)
DEVELOPMENT_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(12, 21)
)
SEALED_DATES = frozenset(
    f"2026-07-{day:02d}" for day in range(24, 27)
)


class BoundaryCompatibilityError(RuntimeError):
    """A V3 boundary or frozen reference failed closed."""


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def iter_gzip(path: Path) -> Iterable[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def _same(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is bool and type(right) is bool and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return (
            math.isfinite(float(left))
            and math.isfinite(float(right))
            and abs(float(left) - float(right)) <= 1e-6
        )
    return left == right


def _field_mismatches(
    expected: Mapping[str, Any],
    actual: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for field in sorted(set(expected) | set(actual)):
        if not _same(expected.get(field), actual.get(field)):
            rows.append({
                "field": field,
                "expected": expected.get(field),
                "actual": actual.get(field),
            })
    return rows


def reconcile_boundaries(
    raw_v5_path: Path,
    normalized_path: Path,
) -> dict[str, Any]:
    """Independently prove the V5-to-normalized cutoff contract for D=804."""
    raw_sha = sha256_file(raw_v5_path)
    normalized_sha = sha256_file(normalized_path)
    if raw_sha != RAW_V5_SHA256:
        raise BoundaryCompatibilityError("raw V5 guard-ledger hash changed")
    if normalized_sha != NORMALIZED_SHA256:
        raise BoundaryCompatibilityError(
            "normalized boundary-ledger hash changed"
        )
    raw_rows = read_jsonl(raw_v5_path)
    normalized_rows = read_jsonl(normalized_path)
    if len(raw_rows) != 804 or len(normalized_rows) != 804:
        raise BoundaryCompatibilityError("boundary D changed from 804")
    raw_by_event = {
        str(row["event_id"]): row for row in raw_rows
    }
    norm_by_event = {
        str(row["event_id"]): row for row in normalized_rows
    }
    if (
        len(raw_by_event) != 804
        or len(norm_by_event) != 804
        or set(raw_by_event) != set(norm_by_event)
    ):
        raise BoundaryCompatibilityError("boundary event identity mismatch")

    mismatches: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    positive = 0
    censored = 0
    contradictory = 0
    for event_id in sorted(raw_by_event):
        raw = raw_by_event[event_id]
        normalized = norm_by_event[event_id]
        independently_derived = boundary_contract(raw)
        contract_mismatches = _field_mismatches(
            independently_derived, normalized
        )
        try:
            cutoff = guarded_cutoff(raw)
        except ReferenceError as exc:
            mismatches.append({
                "event_id": event_id,
                "stage": "guarded_cutoff",
                "error": str(exc),
            })
            continue
        source_counts[str(cutoff["source_class"])] += 1
        status_counts[str(cutoff["status"])] += 1
        positive += int(cutoff["status"] == "positive")
        censored += int(cutoff["status"] == "censored")
        contradictory += int(cutoff["status"] == "contradictory")

        expected_status = (
            "positive"
            if normalized["positive_window1_provable"] is True
            else (
                "contradictory"
                if normalized["start_source_class"] == "contradictory"
                else "censored"
            )
        )
        direct = {
            "event_id": event_id,
            "source_class": normalized["start_source_class"],
            "status": expected_status,
            "cutoff_ts": normalized["guarded_cutoff_ts"],
            "guard_id": (
                normalized["guard_id"]
                if expected_status == "positive" else None
            ),
            "guard_seconds": (
                normalized["guard_seconds"]
                if expected_status == "positive" else None
            ),
        }
        actual = {
            "event_id": cutoff["event_id"],
            "source_class": cutoff["source_class"],
            "status": cutoff["status"],
            "cutoff_ts": cutoff.get("cutoff_ts"),
            "guard_id": cutoff.get("guard_id"),
            "guard_seconds": cutoff.get("guard_seconds"),
        }
        cutoff_mismatches = _field_mismatches(direct, actual)
        if contract_mismatches or cutoff_mismatches:
            mismatches.append({
                "event_id": event_id,
                "stage": "raw_v5_to_normalized_compatibility",
                "boundary_contract_mismatches": contract_mismatches,
                "guarded_cutoff_mismatches": cutoff_mismatches,
            })
    receipt = {
        "schema_version": VERSION + "-compatibility-receipt-v1",
        "raw_v5_ledger": {
            "path": (
                ".claude/window1_start_guard_corrected_20260724/"
                "REAL_START_LEDGER_V5.jsonl"
            ),
            "sha256": raw_sha,
            "row_count": len(raw_rows),
        },
        "normalized_boundary_ledger": {
            "path": (
                ".claude/window1_t2_scoring_package_prerun_20260728/"
                "GUARDED_BOUNDARY_LEDGER.jsonl"
            ),
            "sha256": normalized_sha,
            "row_count": len(normalized_rows),
            "contract": (
                "derived cutoff contract only; not valid raw-V5 input to "
                "window1_range_attack_reference_adapter_v2"
            ),
        },
        "events_compared": len(raw_by_event),
        "raw_boundary_contract_derivations": len(raw_by_event),
        "raw_guarded_cutoff_derivations": len(raw_by_event),
        "positive_count": positive,
        "censored_count": censored,
        "contradictory_count": contradictory,
        "source_class_counts": dict(sorted(source_counts.items())),
        "guarded_cutoff_status_counts": dict(sorted(status_counts.items())),
        "field_mismatch_count": len(mismatches),
        "mismatch_event_ids": [
            row["event_id"] for row in mismatches
        ],
        "mismatches": mismatches,
        "all_event_identities_conserved": set(raw_by_event) == set(norm_by_event),
        "source_class_conserved": not mismatches,
        "positive_censored_status_conserved": not mismatches,
        "cutoff_conserved": not mismatches,
        "guard_id_conserved": not mismatches,
        "guard_seconds_conserved": not mismatches,
        "boundary_law_conserved": not mismatches,
        "package_blocked": bool(mismatches),
        "scorer_invocations": 0,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "performance": None,
    }
    if mismatches:
        raise BoundaryCompatibilityError(
            "raw/normalized boundary mismatch: "
            + ",".join(receipt["mismatch_event_ids"][:10])
        )
    return receipt


def derive_reference_rows(
    *,
    events: Iterable[Mapping[str, Any]],
    raw_boundaries: Iterable[Mapping[str, Any]],
    cache_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Freeze every event-leg reference from raw V5 plus guarded true prints."""
    event_rows = list(events)
    raw_by_event = {
        str(row["event_id"]): row for row in raw_boundaries
    }
    if len(event_rows) != 804 or len(raw_by_event) != 804:
        raise BoundaryCompatibilityError("reference population is not D=804")
    references: list[dict[str, Any]] = []
    unavailable = Counter()
    source_classes = Counter()
    tie_rows = 0
    ambiguity_rows = 0
    supporting_receipts = 0
    for event in event_rows:
        event_id = str(event["event_id"])
        event_date = str(event["event_date"])
        if event_date in SEALED_DATES or event_date not in DEVELOPMENT_DATES:
            raise BoundaryCompatibilityError(
                "reference population contains forbidden date"
            )
        boundary = raw_by_event.get(event_id)
        if boundary is None:
            raise BoundaryCompatibilityError("event lacks raw V5 boundary")
        cache_path = cache_root / f"{event_id}.json.gz"
        if not cache_path.is_file():
            raise BoundaryCompatibilityError("guarded-cache event missing")
        cache = _load_cache(cache_path)
        if str(cache.get("event_id")) != event_id:
            raise BoundaryCompatibilityError("guarded-cache event mismatch")
        cache_legs = {
            str(row["ticker"]): row for row in cache.get("legs") or []
        }
        for leg in event["legs"]:
            leg_id = str(leg.get("leg_id") or leg.get("leg"))
            ticker = str(leg["ticker"])
            cached = cache_legs.get(ticker)
            if not isinstance(cached, Mapping):
                raise BoundaryCompatibilityError(
                    f"guarded-cache leg missing: {event_id}/{leg_id}"
                )
            reference = derive_window1_close_reference(
                event=event,
                leg=leg,
                boundary=boundary,
                true_prints=cached.get("prints") or [],
            )
            row = {
                "schema_version": "window1-close-reference-ledger-v3",
                **reference.to_dict(),
                "reference_supporting_receipts": list(
                    reference.reference_supporting_receipts
                ),
                "latest_timestamp_distinct_prices": list(
                    reference.latest_timestamp_distinct_prices
                ),
                "raw_v5_boundary_source_sha256": canonical_sha256(boundary),
                "raw_v5_boundary_ledger_sha256": RAW_V5_SHA256,
                "guarded_cache_file": f"{event_id}.json.gz",
                "guarded_cache_file_sha256": sha256_file(cache_path),
                "schedule_derived_reference": False,
                "carried_last_trade_substituted": False,
                "constructed_midpoint_substituted": False,
                "receipt_id_price_tiebreak_used": False,
                "scored": False,
                "metrics": None,
                "performance": None,
            }
            references.append(row)
            source_classes[reference.boundary_source_class] += 1
            unavailable[str(reference.reason)] += int(not reference.available)
            tie_rows += int(reference.latest_timestamp_tie_count > 1)
            ambiguity_rows += int(reference.reason == AMBIGUOUS_REASON)
            supporting_receipts += len(
                reference.reference_supporting_receipts
            )
    references.sort(
        key=lambda row: (row["event_id"], row["leg_id"])
    )
    adapted = adapt_frozen_reference_rows(
        references,
        expected_legs={
            (
                str(event["event_id"]),
                str(leg.get("leg_id") or leg.get("leg")),
            ): str(leg["ticker"])
            for event in event_rows
            for leg in event["legs"]
        },
        normalized_boundaries=None,
    )
    census = {
        "schema_version": VERSION + "-reference-census-v1",
        "event_count": len(event_rows),
        "event_leg_row_count": len(references),
        "expected_event_leg_row_count": 1608,
        "unique_event_leg_count": len(adapted),
        "available_count": sum(row["available"] is True for row in references),
        "unavailable_count": sum(
            row["available"] is False for row in references
        ),
        "unavailability_reason_counts": dict(sorted(unavailable.items())),
        "boundary_source_class_counts": dict(sorted(source_classes.items())),
        "latest_timestamp_tie_row_count": tie_rows,
        "latest_timestamp_differing_price_ambiguity_count": ambiguity_rows,
        "supporting_receipt_count": supporting_receipts,
        "raw_v5_rows_consumed": len(raw_by_event),
        "raw_v5_sha256": RAW_V5_SHA256,
        "holdout_rows": 0,
        "schedule_derived_reference_count": 0,
        "carried_last_trade_substitution_count": 0,
        "constructed_midpoint_substitution_count": 0,
        "receipt_id_price_tiebreak_count": 0,
        "scorer_invocations": 0,
        "C": None,
        "PC": None,
        "IC": None,
        "S": None,
        "performance": None,
    }
    if (
        len(references) != 1608
        or len(adapted) != 1608
        or census["holdout_rows"] != 0
    ):
        raise BoundaryCompatibilityError(
            "frozen reference ledger did not conserve 1,608 event legs"
        )
    return references, census


def adapt_frozen_reference_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    expected_legs: Mapping[tuple[str, str], str],
    normalized_boundaries: Mapping[str, Mapping[str, Any]] | None,
) -> dict[tuple[str, str], Window1CloseReferenceV2]:
    """Strictly validate frozen rows without re-running raw reference logic."""
    output: dict[tuple[str, str], Window1CloseReferenceV2] = {}
    for row in rows:
        if row.get("schema_version") != "window1-close-reference-ledger-v3":
            raise BoundaryCompatibilityError("wrong frozen-reference schema")
        event_id = str(row.get("event_id") or "")
        event_date = str(row.get("event_date") or "")
        leg_id = str(row.get("leg_id") or "")
        ticker = str(row.get("ticker") or "")
        key = (event_id, leg_id)
        if (
            not all((event_id, event_date, leg_id, ticker))
            or expected_legs.get(key) != ticker
            or key in output
        ):
            raise BoundaryCompatibilityError(
                "duplicate/unknown frozen reference identity"
            )
        if event_date in SEALED_DATES or event_date not in DEVELOPMENT_DATES:
            raise BoundaryCompatibilityError("forbidden reference date")
        if (
            row.get("raw_v5_boundary_ledger_sha256") != RAW_V5_SHA256
            or row.get("schedule_derived_reference") is not False
            or row.get("carried_last_trade_substituted") is not False
            or row.get("constructed_midpoint_substituted") is not False
            or row.get("receipt_id_price_tiebreak_used") is not False
            or row.get("scored") is not False
            or row.get("metrics") is not None
            or row.get("performance") is not None
        ):
            raise BoundaryCompatibilityError(
                "frozen reference provenance/score-free law changed"
            )
        available = row.get("available")
        if not isinstance(available, bool):
            raise BoundaryCompatibilityError(
                "reference availability is not boolean"
            )
        supporting = tuple(
            str(value) for value in row.get(
                "reference_supporting_receipts"
            ) or []
        )
        distinct = tuple(
            exact_integer(
                value, "reference distinct price", minimum=1, maximum=99
            )
            for value in row.get(
                "latest_timestamp_distinct_prices"
            ) or []
        )
        tie_count = exact_integer(
            row.get("latest_timestamp_tie_count"),
            "latest timestamp tie count",
            minimum=0,
        )
        cutoff = row.get("guarded_cutoff_ts")
        cutoff_value = None if cutoff is None else float(cutoff)
        if cutoff_value is not None and not math.isfinite(cutoff_value):
            raise BoundaryCompatibilityError(
                "reference cutoff is non-finite"
            )
        t8 = float(row.get("t8_floor_ts"))
        if not math.isfinite(t8):
            raise BoundaryCompatibilityError("reference T8 is non-finite")
        price = row.get("window1_close_cents")
        timestamp = row.get("reference_ts")
        receipt = row.get("reference_receipt")
        reason = row.get("reason")
        if available:
            price = exact_integer(
                price, "window1 close price", minimum=1, maximum=99
            )
            if timestamp is None or cutoff_value is None:
                raise BoundaryCompatibilityError(
                    "available reference lacks timestamp/cutoff"
                )
            timestamp = float(timestamp)
            if (
                not math.isfinite(timestamp)
                or not t8 <= timestamp <= cutoff_value
                or reason is not None
                or not supporting
                or distinct != (price,)
                or tie_count != len(supporting)
            ):
                raise BoundaryCompatibilityError(
                    "available frozen reference is inconsistent"
                )
            if len(supporting) == 1:
                if str(receipt or "") != supporting[0]:
                    raise BoundaryCompatibilityError(
                        "single-receipt identity mismatch"
                    )
            elif receipt is not None:
                raise BoundaryCompatibilityError(
                    "same-price tie selected one receipt"
                )
        else:
            if (
                price is not None
                or receipt is not None
                or not str(reason or "").strip()
            ):
                raise BoundaryCompatibilityError(
                    "unavailable reference fabricated price/receipt"
                )
            price = None
            timestamp = None if timestamp is None else float(timestamp)
            if reason == AMBIGUOUS_REASON:
                if (
                    timestamp is None
                    or len(distinct) <= 1
                    or tie_count != len(supporting)
                ):
                    raise BoundaryCompatibilityError(
                        "ambiguous reference lacks complete tie evidence"
                    )
            elif supporting or distinct or tie_count:
                raise BoundaryCompatibilityError(
                    "ordinary unavailable reference carries tie evidence"
                )
        if normalized_boundaries is not None:
            boundary = normalized_boundaries.get(event_id)
            if boundary is None:
                raise BoundaryCompatibilityError(
                    "frozen reference lacks normalized boundary"
                )
            if (
                str(boundary["start_source_class"])
                != str(row["boundary_source_class"])
                or not _same(
                    boundary.get("guarded_cutoff_ts"), cutoff_value
                )
                or (
                    boundary.get("positive_window1_provable") is True
                    and boundary.get("guard_id")
                    != row.get("boundary_guard_id")
                )
                or (
                    boundary.get("positive_window1_provable") is not True
                    and row.get("boundary_guard_id") is not None
                )
            ):
                raise BoundaryCompatibilityError(
                    "frozen reference/boundary mismatch"
                )
        output[key] = Window1CloseReferenceV2(
            event_id=event_id,
            event_date=event_date,
            leg_id=leg_id,
            ticker=ticker,
            available=available,
            window1_close_cents=price,
            reference_ts=timestamp,
            reference_receipt=(
                None if receipt is None else str(receipt)
            ),
            reference_supporting_receipts=supporting,
            reference_source=str(row["reference_source"]),
            t8_floor_ts=t8,
            guarded_cutoff_ts=cutoff_value,
            boundary_source_class=str(row["boundary_source_class"]),
            boundary_guard_id=(
                None
                if row.get("boundary_guard_id") is None
                else str(row["boundary_guard_id"])
            ),
            reason=None if reason is None else str(reason),
            latest_timestamp_tie_count=tie_count,
            latest_timestamp_distinct_prices=distinct,
            authoritative_sequence_available=(
                row.get("authoritative_sequence_available") is True
            ),
        )
    if set(output) != set(expected_legs):
        missing = sorted(set(expected_legs) - set(output))
        extra = sorted(set(output) - set(expected_legs))
        raise BoundaryCompatibilityError(
            f"frozen reference key mismatch missing={missing[:3]} "
            f"extra={extra[:3]}"
        )
    return output
