#!/usr/bin/env python3
"""Sanitized July 12-20 Window-1 evidence reconciliation.

This script reads the existing normalized bundle and a byte-pinned engine-log
snapshot.  It does not query the exchange, mutate production data, or emit raw
order/fill identities.  Outputs are suitable for the public research branch:
one decision receipt per previously absent leg, an event-level reclassification
of the old policy mismatches, and aggregate actual-outcome bounds.

The script does not score a strategy.  Its schedule-plus-60-minute right edge is
only a validation inventory edge for schedule-only rows, not a selected Window-1
definition.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA = "window1-evidence-reconcile-v1"
VALIDATION_CORRIDOR_SECONDS = 60 * 60
LEFT_EDGE_SECONDS = 8 * 60 * 60
TERMINAL = {"executed", "canceled", "expired", "rejected"}

EVENT_RE = re.compile(br'"event"\s*:\s*"([^"]+)"')
TICKER_RE = re.compile(br'"ticker"\s*:\s*"([^"]+)"')
REASON_RE = re.compile(br'"reason"\s*:\s*"([^"]+)"')
TS_RE = re.compile(br'"ts_epoch"\s*:\s*([0-9.]+)')

VISIBILITY_EVENTS = {
    "aim_shadow",
    "entry_dossier",
    "order_error",
    "order_placed",
    "v4_place",
}
EXPLICIT_NO_PLACEMENT_EVENTS = {
    "conception_horizon_defer",
    "event_skip_stale_book",
    "schedule_abandon_deferred",
    "skip_live_match",
    "skipped",
    "wall_skip_pair",
}


def json_dump(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json_dump(dict(row)) + "\n")


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
                    f"{path.name}:{line_number}: row is not an object")
            rows.append(row)
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def leg_tickers(event: Mapping[str, Any]) -> list[str]:
    tickers = []
    for leg in event.get("legs") or []:
        ticker = leg.get("ticker") if isinstance(leg, dict) else leg
        if ticker:
            tickers.append(str(ticker))
    return sorted(set(tickers))


def event_from_ticker(ticker: str) -> str:
    return ticker.rsplit("-", 1)[0] if "-" in ticker else ""


def parse_timestamp(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    try:
        return float(text)
    except ValueError:
        return dt.datetime.fromisoformat(
            text.replace("Z", "+00:00")).timestamp()


def source_timestamp(row: Mapping[str, Any]) -> float | None:
    return parse_timestamp(row.get("exchange_ts"))


def decision_event_type(event_type: str) -> str | None:
    lower = event_type.lower()
    if "refus" in lower:
        return "causal_refusal"
    if (event_type in EXPLICIT_NO_PLACEMENT_EVENTS
            or lower.startswith("skip_")
            or "_skip_" in lower
            or lower.endswith("_skip")
            or lower.endswith("_defer")
            or lower.endswith("_deferred")):
        return "causal_no_placement"
    return None


def decode(raw: bytes) -> str:
    return raw.decode("utf-8", "replace")


def iter_log_lines(
    log_dir: Path, active_prefix_bytes: int,
) -> Iterable[tuple[str, bytes]]:
    immutable = sorted(log_dir.glob("live_v3_2026071[2-9]*.jsonl.gz"))
    for path in immutable:
        with gzip.open(path, "rb") as handle:
            for line in handle:
                yield path.name, line
    active = log_dir / "live_v3_20260720.jsonl"
    with active.open("rb") as handle:
        while handle.tell() < active_prefix_bytes:
            line = handle.readline()
            if not line:
                break
            yield active.name, line


def validation_edges(event: Mapping[str, Any]) -> tuple[float, float]:
    scheduled = parse_timestamp(event["scheduled_start_exchange_ts"])
    if scheduled is None:
        raise ValueError("event lacks a scheduled start timestamp")
    actual = event.get("actual_start_exchange_ts")
    right = (parse_timestamp(actual) if actual not in (None, "")
             and event.get("actual_start_verified") is True
             else scheduled + VALIDATION_CORRIDOR_SECONDS)
    if right is None:
        raise ValueError("verified actual start is not parseable")
    return scheduled - LEFT_EDGE_SECONDS, right


def first_five_vwap(fills: list[tuple[float, float, float]]) -> float | None:
    needed = 5.0
    cost = 0.0
    taken = 0.0
    for _, quantity, price in sorted(fills):
        use = min(needed, quantity)
        cost += use * price
        taken += use
        needed -= use
        if needed <= 1e-9:
            return cost / taken
    return None


def reconcile(args: argparse.Namespace) -> int:
    normalized = Path(args.normalized_dir).resolve()
    output = Path(args.output_dir).resolve()
    events = load_jsonl(normalized / "events.jsonl")
    orders = load_jsonl(normalized / "orders.jsonl")
    fills = load_jsonl(normalized / "fills.jsonl")
    event_map = {str(row["event_id"]): row for row in events}
    event_ids = set(event_map)
    legs = {event_id: leg_tickers(row)
            for event_id, row in event_map.items()}
    edges = {event_id: validation_edges(row)
             for event_id, row in event_map.items()}

    denominator_orders = [
        row for row in orders
        if str(row.get("event_id") or "") in event_ids
        and row.get("purpose") == "entry"
        and row.get("action") == "buy"
    ]
    orders_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in denominator_orders:
        orders_by_event[str(row["event_id"])].append(row)
    missing_by_event = {}
    for event_id in sorted(event_ids):
        attempted = {str(row.get("ticker") or "")
                     for row in orders_by_event.get(event_id, [])}
        missing = sorted(set(legs[event_id]) - attempted)
        if missing:
            missing_by_event[event_id] = missing
    target_events = set(missing_by_event)

    observed_events: set[str] = set()
    mapping_defect_legs: set[tuple[str, str]] = set()
    evidence: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    seen_receipts: set[tuple[Any, ...]] = set()
    physical_log_rows = 0
    selected_log_rows = 0
    log_event_counts = Counter()
    for file_name, line in iter_log_lines(
            Path(args.log_dir).resolve(), args.active_log_prefix_bytes):
        physical_log_rows += 1
        event_values = EVENT_RE.findall(line)
        if not event_values:
            continue
        event_type = decode(event_values[0])
        decision_type = decision_event_type(event_type)
        if (event_type not in VISIBILITY_EVENTS
                and decision_type is None):
            continue
        selected_log_rows += 1
        log_event_counts[event_type] += 1
        ticker_values = [decode(value) for value in TICKER_RE.findall(line)]
        tickers = [value for value in ticker_values if value.startswith("KX")]
        event_candidates = [
            decode(value) for value in event_values[1:]
            if value.startswith(b"KX")
        ]
        for ticker in tickers:
            candidate = event_from_ticker(ticker)
            if candidate:
                event_candidates.append(candidate)
        event_id = next(
            (value for value in event_candidates if value in target_events),
            None)
        if event_id is None:
            continue
        timestamp_match = TS_RE.search(line)
        timestamp = (float(timestamp_match.group(1))
                     if timestamp_match else None)
        left, right = edges[event_id]
        if timestamp is not None and not left <= timestamp <= right:
            continue
        observed_events.add(event_id)
        missing = missing_by_event[event_id]
        relevant_tickers = [ticker for ticker in tickers if ticker in missing]
        if not relevant_tickers and any(
                value == event_id for value in event_candidates):
            relevant_tickers = list(missing)
        if event_type == "order_placed":
            for ticker in relevant_tickers:
                mapping_defect_legs.add((event_id, ticker))
            continue
        if decision_type is None or timestamp is None:
            continue
        reason_match = REASON_RE.search(line)
        reason = decode(reason_match.group(1)) if reason_match else event_type
        for ticker in relevant_tickers:
            fingerprint = (
                event_id, ticker, event_type, reason, round(timestamp, 6))
            if fingerprint in seen_receipts:
                continue
            seen_receipts.add(fingerprint)
            evidence[(event_id, ticker)].append({
                "event_type": event_type,
                "reason": reason,
                "local_logged_ts": timestamp,
                "source_file_class": (
                    "active_byte_pinned" if file_name.endswith(".jsonl")
                    else "immutable_gzip"),
                "decision_type": decision_type,
            })

    decisions = []
    reclassified = []
    class_counts = Counter()
    reason_counts = Counter()
    for event_id, missing in sorted(missing_by_event.items()):
        event_orders = orders_by_event.get(event_id, [])
        accepted_missing = any(
            row.get("accepted") is True
            and row.get("exchange_status") in (None, "")
            for row in event_orders)
        mapped = sorted(
            ticker for ticker in missing
            if (event_id, ticker) in mapping_defect_legs)
        decided = sorted(
            ticker for ticker in missing if evidence.get((event_id, ticker)))
        if mapped:
            classification = "mapping_defect"
        elif accepted_missing:
            classification = "accepted_order_with_missing_receipt"
        elif set(decided) == set(missing):
            classification = "causally_proven_refusal_or_no_placement"
        elif event_id not in observed_events:
            classification = "logging_gap"
        else:
            classification = "genuinely_unknown"
        class_counts[classification] += 1
        receipts = sorted({
            row["event_type"] for ticker in missing
            for row in evidence.get((event_id, ticker), [])
        })
        for receipt in receipts:
            reason_counts[receipt] += 1
        reclassified.append({
            "schema_version": SCHEMA,
            "event_id": event_id,
            "category": event_map[event_id]["category"],
            "missing_leg_tickers": missing,
            "classification": classification,
            "causal_receipt_event_types": receipts,
            "mapped_order_placed_legs": mapped,
        })
        for ticker in decided:
            row = sorted(
                evidence[(event_id, ticker)],
                key=lambda item: item["local_logged_ts"])[-1]
            digest = hashlib.sha256(
                json_dump([event_id, ticker, row["event_type"],
                           row["reason"], row["local_logged_ts"]]).encode()
            ).hexdigest()[:24]
            decisions.append({
                "schema_version": "window1-normalized-v2",
                "decision_id": "san-" + digest,
                "event_id": event_id,
                "ticker": ticker,
                "leg": ticker.rsplit("-", 1)[-1],
                "decision_type": row["decision_type"],
                "reason": row["reason"],
                "receipt_event_type": row["event_type"],
                "local_logged_ts": row["local_logged_ts"],
                "exchange_ts": None,
                "clock_basis": "local_engine_log_time",
                "source": "live_engine_jsonl_frozen_prefix",
            })

    denominator_order_ids = {
        str(row.get("order_id") or "") for row in denominator_orders
        if row.get("order_id")}
    fills_by_order: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fill in fills:
        order_id = str(fill.get("order_id") or "")
        if order_id in denominator_order_ids:
            fills_by_order[order_id].append(fill)
    accepted = [row for row in denominator_orders
                if row.get("accepted") is not False]
    failed = [row for row in denominator_orders
              if row.get("accepted") is False]
    terminal_counts = Counter(
        str(row.get("exchange_status")) for row in accepted)
    receipt_errors = Counter()
    exact_terminal_orders = 0
    for order in accepted:
        status = str(order.get("exchange_status") or "").lower()
        if status not in TERMINAL:
            receipt_errors["accepted_order_missing_terminal_receipt"] += 1
            continue
        expected = order.get("exchange_fill_count")
        if expected in (None, ""):
            receipt_errors["terminal_receipt_missing_fill_count"] += 1
            continue
        official = fills_by_order.get(str(order.get("order_id") or ""), [])
        quantity = sum(float(row.get("quantity") or 0) for row in official)
        if not math.isclose(
                quantity, float(expected), rel_tol=0.0, abs_tol=1e-9):
            receipt_errors["terminal_fill_count_mismatch"] += 1
            continue
        exact_terminal_orders += 1

    fill_inventory: dict[tuple[str, str], list[tuple[float, float, float]]] = (
        defaultdict(list))
    order_by_id = {
        str(row.get("order_id") or ""): row for row in denominator_orders
        if row.get("order_id")}
    for fill in fills:
        order = order_by_id.get(str(fill.get("order_id") or ""))
        if not order:
            continue
        event_id = str(order["event_id"])
        timestamp = source_timestamp(fill)
        if timestamp is None or timestamp > edges[event_id][1]:
            continue
        fill_inventory[(event_id, str(order["ticker"]))].append((
            timestamp, float(fill.get("quantity") or 0),
            float(fill.get("price_cents"))))
    missing_capacity: dict[tuple[str, str], float] = defaultdict(float)
    for order in accepted:
        if order.get("exchange_status") not in (None, ""):
            continue
        key = (str(order["event_id"]), str(order["ticker"]))
        missing_capacity[key] = max(
            missing_capacity[key], float(order.get("quantity") or 0))

    exact_c = 0
    exact_s = 0
    optimistic_c = 0
    exact_combined_costs = []
    for event_id in sorted(event_ids):
        tickers = legs[event_id]
        if len(tickers) != 2:
            continue
        vwaps = [first_five_vwap(fill_inventory[(event_id, ticker)])
                 for ticker in tickers]
        known_qty = [
            sum(quantity for _, quantity, _ in
                fill_inventory[(event_id, ticker)])
            for ticker in tickers
        ]
        exact = all(quantity >= 5 for quantity in known_qty)
        possible = all(
            quantity + missing_capacity[(event_id, ticker)] >= 5
            for quantity, ticker in zip(known_qty, tickers))
        if exact:
            exact_c += 1
            combined = float(vwaps[0]) + float(vwaps[1])
            exact_combined_costs.append(combined)
            if combined < 100:
                exact_s += 1
        if possible:
            optimistic_c += 1

    denominator = {
        "schema_version": SCHEMA,
        "U_raw_unique_catalog_games": len(events),
        "minus_duplicate_market_or_event_rows": 0,
        "minus_reschedule_aliases_proven": 0,
        "minus_non_match_rows": 0,
        "minus_verified_pre_window_cancellations_or_voids": 0,
        "minus_causal_pre_simulation_violent_faller_receipts": 0,
        "D": len(events),
        "proof_note": (
            "No eventual-path band label is used as a pre-simulation "
            "exclusion; absent a contemporaneous pre-left-edge receipt, "
            "the event remains in D."),
    }
    census = {
        "schema_version": SCHEMA,
        "gate_pass": False,
        "D": len(events),
        "prior_policy_mismatch_events": len(missing_by_event),
        "policy_reclassification": dict(sorted(class_counts.items())),
        "policy_reclassification_sums_to_prior": (
            sum(class_counts.values()) == len(missing_by_event)),
        "causal_receipt_event_type_event_counts":
            dict(sorted(reason_counts.items())),
        "denominator_entry_attempts": len(denominator_orders),
        "accepted_orders": len(accepted),
        "failed_attempts": len(failed),
        "accepted_terminal_status": dict(sorted(terminal_counts.items())),
        "exact_terminal_orders": exact_terminal_orders,
        "receipt_error_counts": dict(sorted(receipt_errors.items())),
        "failed_attempt_http_status": dict(sorted(Counter(
            str(row.get("failure_status")) for row in failed).items())),
        "failed_attempt_clock_gap": sum(
            row.get("exchange_rejected_ts") in (None, "")
            for row in failed),
        "recoverable_bounded_irrecoverable": {
            "recoverable_exact_terminal_orders": exact_terminal_orders,
            "bounded_accepted_orders_missing_terminal_receipt":
                receipt_errors["accepted_order_missing_terminal_receipt"],
            "irrecoverable_or_unobserved_decision_events": (
                class_counts["logging_gap"]
                + class_counts["genuinely_unknown"]),
            "mapping_defect_events": class_counts["mapping_defect"],
        },
        "source_scan": {
            "physical_log_rows": physical_log_rows,
            "selected_log_rows": selected_log_rows,
            "active_log_prefix_bytes": args.active_log_prefix_bytes,
            "event_type_counts": dict(sorted(log_event_counts.items())),
        },
        "strategy_scoring_permitted": False,
        "stop_reason": (
            "accepted terminal receipts and/or required decisions remain "
            "unrecoverable; no candidate tuning is lawful"),
    }
    bounds = {
        "schema_version": SCHEMA,
        "not_a_strategy_result": True,
        "validation_inventory_edge": (
            "verified actual start else scheduled start plus 60 minutes"),
        "D": len(events),
        "exact_actual_dual5_lower_bound": exact_c,
        "optimistic_actual_dual5_upper_bound": optimistic_c,
        "exact_actual_under_par_dual5_lower_bound": exact_s,
        "optimistic_actual_under_par_dual5_upper_bound": optimistic_c,
        "exact_combined_costs_below_100": exact_s,
        "exact_combined_costs_n": len(exact_combined_costs),
        "individual_leg_delta_vs_frozen_w1_close": None,
        "individual_leg_delta_reason": (
            "Window-1 boundary/reference is not frozen while validation "
            "fails"),
        "C": None,
        "S": None,
        "C_over_D": None,
        "S_over_C": None,
        "S_over_D": None,
    }

    write_jsonl(output / "decisions.jsonl", sorted(
        decisions, key=lambda row: (
            row["event_id"], row["ticker"], row["local_logged_ts"])))
    write_jsonl(output / "policy_mismatch_reclassification.jsonl",
                reclassified)
    write_json(output / "corrected_mismatch_census.json", census)
    write_json(output / "actual_outcome_bounds.json", bounds)
    write_json(output / "denominator_audit.json", denominator)
    receipt = {
        "schema_version": SCHEMA,
        "inputs": {
            name: {
                "bytes": (normalized / name).stat().st_size,
                "sha256": sha256_file(normalized / name),
            }
            for name in ("events.jsonl", "orders.jsonl", "fills.jsonl")
        },
        "outputs": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in sorted(output.iterdir())
            if path.is_file() and path.name != "reconciliation_receipt.json"
        },
    }
    write_json(output / "reconciliation_receipt.json", receipt)
    print(json.dumps({
        "D": len(events),
        "policy_reclassification": dict(sorted(class_counts.items())),
        "exact_terminal_orders": exact_terminal_orders,
        "receipt_errors": dict(sorted(receipt_errors.items())),
        "actual_dual5_bounds": [exact_c, optimistic_c],
        "actual_under_par_bounds": [exact_s, optimistic_c],
        "strategy_scoring_permitted": False,
    }, indent=2, sort_keys=True))
    return 3


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--normalized-dir", required=True)
    root.add_argument("--log-dir", required=True)
    root.add_argument("--active-log-prefix-bytes", type=int, required=True)
    root.add_argument("--output-dir", required=True)
    return root


if __name__ == "__main__":
    raise SystemExit(reconcile(parser().parse_args()))
