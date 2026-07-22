#!/usr/bin/env python3
"""Build local-only, sanitized Window-1 evidence-recovery artifacts.

The inputs are the public artifacts committed at b7039169. Private order,
attempt, fill, and account identities are intentionally unavailable. This
builder preserves exact public event/ticker identities where they survived and
uses explicit nulls plus deterministic recovery slots everywhere else.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA = "window1-mismatch-recovery-v1"
EXPECTED_MISMATCHES = {
    "accepted_order_missing_receipt": 703,
    "decision_unobserved": 335,
    "clock": 14,
    "fill_receipt": 2,
}
POLICY_BUCKETS = {
    "accepted_order_with_missing_receipt": 6,
    "causally_proven_refusal_or_no_placement": 132,
    "genuinely_unknown": 4,
    "logging_gap": 162,
    "mapping_defect": 47,
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: expected a JSON object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                row = json.loads(line)
            except ValueError as exc:
                raise ValueError(
                    f"{path.name}:{line_number}: malformed JSON") from exc
            if not isinstance(row, dict):
                raise ValueError(
                    f"{path.name}:{line_number}: expected an object")
            rows.append(row)
    return rows


def dump_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + chr(10),
        encoding="utf-8",
    )


def dump_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline=chr(10)) as handle:
        for row in rows:
            handle.write(json.dumps(
                dict(row), sort_keys=True, separators=(",", ":")))
            handle.write(chr(10))


def identity(value: str | None, status: str, slot: str | None = None) -> dict:
    return {
        "available": value is not None,
        "value": value,
        "status": status,
        "local_recovery_slot": slot,
    }


def absent_clock(event_date: str | None = None) -> dict:
    return {
        "value": None,
        "basis": "not_retained_or_evidence_missing",
        "event_date": event_date,
    }


def terminal_row(slot: int) -> dict[str, Any]:
    local_slot = f"terminal-{slot:04d}"
    return {
        "schema_version": SCHEMA,
        "mismatch_id": local_slot,
        "mismatch_class": "accepted_order_missing_receipt",
        "event": identity(
            None, "omitted_from_local_sanitized_artifacts", local_slot),
        "market_ticker": identity(
            None, "omitted_from_local_sanitized_artifacts", local_slot),
        "leg": None,
        "order_or_attempt_identity": identity(
            None, "private_identity_not_committed", local_slot),
        "causal_timestamp": absent_clock(),
        "expected_evidence": [
            "official exchange creation receipt",
            "official terminal status",
            "official fill count",
            "official cancellation or expiry timestamp when nonfilled",
        ],
        "evidence_actually_present": [
            "accepted=true existed in the private normalized bundle",
            "aggregate audit classified this row as terminal receipt missing",
            "row-level event, ticker, order, and client identity were redacted",
        ],
        "source_needed": [
            {
                "source": "private_kalshi_order_history",
                "required_keys": [
                    "order_id", "client_order_id", "event_id", "ticker"],
                "can_prove": [
                    "creation", "terminal status", "fill count",
                    "cancellation", "expiry"],
            },
            {
                "source": "private_kalshi_fills",
                "required_keys": ["order_id", "ticker"],
                "can_prove": ["partial fills", "fill quantity", "fill time"],
                "cannot_alone_prove": ["terminal nonfill or cancellation"],
            },
            {
                "source": "frozen_live_v4_logs",
                "required_keys": [
                    "order_id or client_order_id", "ticker", "local log time"],
                "can_prove": ["local placement/cancel intent"],
                "cannot_replace": ["exchange terminal timestamp"],
            },
            {
                "source": "persisted_orders_ledger",
                "required_keys": ["order_id", "ticker"],
                "can_prove": ["order was observed resting"],
                "cannot_alone_prove": ["complete terminal history"],
            },
        ],
        "required_recovery_identifiers": [
            "private normalized row slot-to-order join",
            "order_id",
            "client_order_id where present",
            "event_id",
            "ticker",
        ],
        "recovery_status": "uncertain",
        "recovery_basis": (
            "candidate sources exist, but the local branch intentionally "
            "does not retain the per-row keys needed to assign a source"),
    }


def decision_sources(classification: str, mapped: bool) -> list[dict]:
    sources = []
    if mapped:
        sources.append({
            "source": "frozen_live_v4_logs",
            "required_record": "order_placed",
            "repair": "join logged event/ticker to normalized order attempt",
        })
    if classification == "accepted_order_with_missing_receipt":
        sources.extend([
            {
                "source": "private_kalshi_order_history",
                "required_record": "official terminal order receipt",
            },
            {
                "source": "private_kalshi_fills",
                "required_record": "fills keyed by order identity",
            },
        ])
    elif classification in {"logging_gap", "genuinely_unknown"}:
        sources.extend([
            {
                "source": "frozen_live_v4_logs",
                "required_record": (
                    "event/ticker decision, placement, refusal, or skip"),
            },
            {
                "source": "private_kalshi_order_history",
                "required_record": "order attempt if one reached exchange",
            },
        ])
    elif classification == "mapping_defect" and not mapped:
        sources.append({
            "source": "normalizer_mapping_receipts",
            "required_record": "event/ticker alias or sibling mapping",
        })
    return sources


def build(
    events: list[dict[str, Any]],
    policy_rows: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    validation_summary: dict[str, Any],
) -> dict[str, Any]:
    if validation_summary.get("mismatch_types") != EXPECTED_MISMATCHES:
        raise ValueError("corrected mismatch census differs from 1,054 law")
    if validation_summary.get("mismatch_count") != 1054:
        raise ValueError("corrected mismatch total is not 1,054")
    if len(policy_rows) != 351:
        raise ValueError("policy reclassification does not contain 351 rows")
    policy_counts = collections.Counter(
        str(row.get("classification")) for row in policy_rows)
    if dict(policy_counts) != POLICY_BUCKETS:
        raise ValueError("policy bucket census differs from correction")

    event_map = {str(row["event_id"]): row for row in events}
    decision_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in decisions
    }
    mismatch_rows: list[dict[str, Any]] = [
        terminal_row(slot) for slot in range(1, 704)]
    receipt_rows = list(mismatch_rows)
    mapping_rows = []
    policy_leg_census = collections.defaultdict(collections.Counter)

    decision_slot = 0
    for policy in sorted(policy_rows, key=lambda row: row["event_id"]):
        event_id = str(policy["event_id"])
        event = event_map.get(event_id)
        if event is None:
            raise ValueError(f"policy event absent from D: {event_id}")
        classification = str(policy["classification"])
        missing = [str(value) for value in policy["missing_leg_tickers"]]
        mapped_legs = {
            str(value) for value in policy.get("mapped_order_placed_legs", [])}
        leg_states = []
        for ticker in sorted(missing):
            decision = decision_map.get((event_id, ticker))
            mapped = ticker in mapped_legs
            leg_states.append({
                "ticker": ticker,
                "leg": ticker.rsplit("-", 1)[-1],
                "normalized_attempt_present": False,
                "order_placed_log_evidence": mapped,
                "causal_decision_id": (
                    decision.get("decision_id") if decision else None),
                "decision_type": (
                    decision.get("decision_type") if decision else None),
                "validation_mismatch": decision is None,
            })
            policy_leg_census[classification]["missing_legs"] += 1
            if decision:
                policy_leg_census[classification]["causal_decision_legs"] += 1
                continue
            policy_leg_census[classification]["unobserved_legs"] += 1
            decision_slot += 1
            mismatch_id = f"decision-{decision_slot:04d}"
            possible = mapped
            mismatch_rows.append({
                "schema_version": SCHEMA,
                "mismatch_id": mismatch_id,
                "mismatch_class": "decision_unobserved",
                "event": identity(
                    event_id, "public_event_identity_available"),
                "market_ticker": identity(
                    ticker, "public_market_identity_available"),
                "leg": ticker.rsplit("-", 1)[-1],
                "order_or_attempt_identity": {
                    "available": False,
                    "value": None,
                    "status": "not_applicable_until_attempt_is_recovered",
                    "local_recovery_slot": mismatch_id,
                },
                "causal_timestamp": absent_clock(event.get("event_date")),
                "expected_evidence": [
                    "normalized entry attempt or causal refusal/no-placement",
                    "source timestamp inside the validation corridor",
                ],
                "evidence_actually_present": [
                    f"policy classification={classification}",
                    (
                        "order_placed event/ticker evidence survives"
                        if mapped else
                        "no leg-specific causal receipt survives locally"),
                ],
                "source_needed": decision_sources(classification, mapped),
                "required_recovery_identifiers": [
                    event_id, ticker, "source timestamp", "decision/order type"],
                "policy_reclassification": classification,
                "recovery_status": "possible" if possible else "uncertain",
                "recovery_basis": (
                    "exact order_placed event/ticker evidence survives"
                    if possible else
                    "candidate sources exist but no decisive leg receipt "
                    "survives in the branch"),
            })
        mapping_rows.append({
            "schema_version": "window1-mapping-defect-v1",
            "event_id": event_id,
            "event_date": event.get("event_date"),
            "category": event.get("category"),
            "classification": classification,
            "is_mapping_defect": classification == "mapping_defect",
            "missing_leg_tickers": sorted(missing),
            "mapped_order_placed_legs": sorted(mapped_legs),
            "causal_receipt_event_types":
                policy.get("causal_receipt_event_types", []),
            "leg_states": leg_states,
            "unobserved_leg_count": sum(
                state["validation_mismatch"] for state in leg_states),
            "recovery_status": (
                "possible" if classification == "mapping_defect"
                else "not_applicable"),
        })

    if decision_slot != 335:
        raise ValueError(f"unobserved decision legs={decision_slot}, not 335")

    for slot in range(1, 15):
        mismatch_id = f"rejection-clock-{slot:02d}"
        mismatch_rows.append({
            "schema_version": SCHEMA,
            "mismatch_id": mismatch_id,
            "mismatch_class": "clock",
            "event": identity(
                None, "omitted_from_local_sanitized_artifacts", mismatch_id),
            "market_ticker": identity(
                None, "omitted_from_local_sanitized_artifacts", mismatch_id),
            "leg": None,
            "order_or_attempt_identity": identity(
                None, "private_attempt_identity_not_committed", mismatch_id),
            "causal_timestamp": absent_clock(),
            "expected_evidence": [
                "exchange rejection timestamp", "exchange rejection code"],
            "evidence_actually_present": [
                "aggregate local HTTP failure status was 400 or 409",
                "local log time exists only in the private evidence bundle",
            ],
            "source_needed": [
                {
                    "source": "private_kalshi_order_history_or_error_receipt",
                    "required_record": "exchange-timestamped rejection",
                },
                {
                    "source": "frozen_live_v4_logs",
                    "required_record": "attempt event/ticker/price/quantity",
                    "cannot_replace": "exchange rejection timestamp",
                },
            ],
            "required_recovery_identifiers": [
                "attempt_id", "event_id", "ticker", "local request fingerprint"],
            "recovery_status": "uncertain",
            "recovery_basis": (
                "the aggregate HTTP outcome survives, but all row keys and "
                "the exchange clock are private and currently unavailable"),
        })

    fill_details = [
        "official fill receipts disagree with terminal fill count",
        "executed terminal status does not reach ordered quantity",
    ]
    for slot, detail in enumerate(fill_details, 1):
        mismatch_id = f"fill-receipt-{slot:02d}"
        mismatch_rows.append({
            "schema_version": SCHEMA,
            "mismatch_id": mismatch_id,
            "mismatch_class": "fill_receipt",
            "event": identity(
                None, "omitted_from_local_sanitized_artifacts", mismatch_id),
            "market_ticker": identity(
                None, "omitted_from_local_sanitized_artifacts", mismatch_id),
            "leg": None,
            "order_or_attempt_identity": identity(
                None, "private_order_identity_not_committed", mismatch_id),
            "causal_timestamp": absent_clock(),
            "expected_evidence": [
                "one immutable official order terminal receipt",
                "complete official fill set keyed by order identity",
            ],
            "evidence_actually_present": [detail],
            "source_needed": [
                {
                    "source": "private_kalshi_order_history",
                    "required_record": "official terminal status and fill count",
                },
                {
                    "source": "private_kalshi_fills",
                    "required_record": "complete deduplicated fill receipts",
                },
            ],
            "required_recovery_identifiers": [
                "order_id", "event_id", "ticker", "fill_id set"],
            "recovery_status": "possible",
            "recovery_basis": (
                "both conflicting source classes existed in the private "
                "validation bundle; an immutable export can adjudicate them"),
        })

    if len(mismatch_rows) != 1054:
        raise ValueError(f"recovery ledger has {len(mismatch_rows)} rows")
    mismatch_counts = collections.Counter(
        row["mismatch_class"] for row in mismatch_rows)
    if dict(mismatch_counts) != EXPECTED_MISMATCHES:
        raise ValueError("recovery ledger class counts do not reconcile")

    mapping_defects = [
        row for row in mapping_rows if row["is_mapping_defect"]]
    if len(mapping_defects) != 47:
        raise ValueError("mapping-defect report does not contain 47 events")
    recovery_counts = collections.Counter(
        row["recovery_status"] for row in mismatch_rows)
    recovery_status_counts = {
        status: recovery_counts[status]
        for status in ("possible", "uncertain", "impossible")
    }
    policy_summary = {}
    for classification, event_count in sorted(POLICY_BUCKETS.items()):
        counts = policy_leg_census[classification]
        policy_summary[classification] = {
            "events": event_count,
            "missing_legs": counts["missing_legs"],
            "causal_decision_legs": counts["causal_decision_legs"],
            "unobserved_legs": counts["unobserved_legs"],
        }

    micmay_id = "KXATPCHALLENGERMATCH-26JUL21MICMAY"
    micmay_present = micmay_id in event_map
    return {
        "mismatches": mismatch_rows,
        "terminal_receipts": receipt_rows,
        "mapping_defects": mapping_defects,
        "summary": {
            "schema_version": SCHEMA,
            "D": 804,
            "mismatch_rows": len(mismatch_rows),
            "mismatch_class_counts": dict(sorted(mismatch_counts.items())),
            "recovery_status_counts": recovery_status_counts,
            "identity_coverage": {
                "public_event_and_ticker_known": 335,
                "private_identity_redacted_event_and_ticker_unknown": 719,
                "raw_order_or_attempt_id_emitted": 0,
            },
            "terminal_receipt_source_allocation": {
                "private_kalshi_order_history_assigned": 0,
                "private_fills_assigned": 0,
                "live_v4_logs_assigned": 0,
                "persisted_order_ledger_assigned": 0,
                "confirmed_no_surviving_source": 0,
                "unallocated_pending_private_identity_join": 703,
            },
            "policy_reconciliation": policy_summary,
            "policy_event_total": 351,
            "policy_missing_leg_total": 643,
            "causal_decision_leg_total": 308,
            "unobserved_decision_leg_total": 335,
            "mapping_defect_events": 47,
            "mapping_defect_missing_legs": sum(
                len(row["missing_leg_tickers"]) for row in mapping_defects),
            "mapping_defect_mapped_order_placed_legs": sum(
                len(row["mapped_order_placed_legs"])
                for row in mapping_defects),
            "mapping_defect_unobserved_legs": sum(
                row["unobserved_leg_count"] for row in mapping_defects),
            "strategy_scoring_permitted": False,
        },
        "micmay": {
            "schema_version": "window1-post-sample-forensic-v1",
            "event_id": micmay_id,
            "named_participants": ["Michelsen", "Mayo"],
            "development_interval": ["2026-07-12", "2026-07-20"],
            "ticker_implied_date": "2026-07-21",
            "inside_D": False,
            "present_in_corrected_event_ledger": micmay_present,
            "present_in_policy_reclassification": any(
                row["event_id"] == micmay_id for row in policy_rows),
            "participant_mapping_status": (
                "not established from local July 12-20 artifacts"),
            "forensic_class": "post_sample_separate_forensic",
            "required_future_sources": [
                "July-21 exchange catalog event/market objects",
                "July-21 frozen live_v4 name/schedule/order logs",
                "structured-target participant cache",
            ],
            "authoritative_for_July12_20_validation": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", required=True)
    parser.add_argument("--policy-reclassification", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--validation-summary", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    result = build(
        load_jsonl(Path(args.events)),
        load_jsonl(Path(args.policy_reclassification)),
        load_jsonl(Path(args.decisions)),
        load_json(Path(args.validation_summary)),
    )
    output = Path(args.output_dir)
    dump_jsonl(output / "MISMATCH_RECOVERY_LEDGER.sanitized.jsonl",
               result["mismatches"])
    dump_jsonl(output / "TERMINAL_RECEIPT_RECOVERY_MANIFEST.sanitized.jsonl",
               result["terminal_receipts"])
    dump_jsonl(output / "MAPPING_DEFECTS.sanitized.jsonl",
               result["mapping_defects"])
    dump_json(output / "MISMATCH_RECOVERY_SUMMARY.json", result["summary"])
    dump_json(output / "POST_SAMPLE_MICMAY_FORENSIC.json", result["micmay"])
    print(json.dumps({
        "mismatch_rows": len(result["mismatches"]),
        "mapping_defects": len(result["mapping_defects"]),
        "terminal_receipts": len(result["terminal_receipts"]),
        "recovery_status_counts":
            result["summary"]["recovery_status_counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
