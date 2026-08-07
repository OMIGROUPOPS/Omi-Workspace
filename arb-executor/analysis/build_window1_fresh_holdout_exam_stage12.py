#!/usr/bin/env python3
"""Freeze the boundary and unchanged floor-pass admission for the fresh exam.

This is deliberately policy-blind.  It reads identities, start evidence and
captured book files, but no brain output or score.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


VERSION = "window1-fresh-holdout-exam-stage12-v1"
SEALED_LIST_SHA256 = "06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313"
V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83"
UTC = dt.timezone.utc
OFFICIAL_EXACT = {"live", "ended", "interrupted", "P"}
POLICY_BLIND_LIVE_BY_SOURCES = {
    "tape_flow",
    "price_divergence",
    "tape_latch",
    "te_scoreboard",
}
OLD_DEGRADED_RECORDER_START_EPOCH = 1785415787
OLD_DEGRADED_RECORDER_END_EPOCH = 1786118081


class ExamPreparationError(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iso(value: float | None) -> str | None:
    if value is None:
        return None
    return dt.datetime.fromtimestamp(value, UTC).isoformat()


def number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def positive(value: Any) -> float | None:
    result = number(value)
    return result if result is not None and result > 0 else None


def integer(value: Any) -> int | None:
    result = number(value)
    return int(result) if result is not None and result.is_integer() else None


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(compact(row) + "\n" for row in rows), encoding="utf-8", newline="\n")


def market_url(ticker: str) -> str:
    return f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}"


def fetch_market(ticker: str) -> dict[str, Any]:
    url = market_url(ticker)
    errors: list[str] = []
    for attempt in range(1, 6):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "window1-exam-boundary/1"})
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
            payload = json.loads(body)
            market = payload.get("market")
            if not isinstance(market, dict):
                raise ExamPreparationError(f"market envelope missing for {ticker}")
            receipt = {
                "ticker": ticker,
                "url": url,
                "raw_sha256": sha_bytes(body),
                "raw_bytes": len(body),
                "attempts": attempt,
                "market": market,
            }
            return sanitize_market_receipt(receipt)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(f"attempt={attempt}:{type(exc).__name__}:{exc}")
            if attempt == 5:
                break
            time.sleep(min(8, 2 ** (attempt - 1)))
    raise ExamPreparationError(f"market metadata failed for {ticker}: {' | '.join(errors)}")


def sanitize_market_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    market = receipt["market"]
    return {
        "ticker": receipt["ticker"],
        "url": receipt["url"],
        "raw_sha256": receipt["raw_sha256"],
        "raw_bytes": receipt["raw_bytes"],
        "attempts": receipt["attempts"],
        "market": {
            "ticker": market.get("ticker"),
            "event_ticker": market.get("event_ticker"),
            "occurrence_datetime": market.get("occurrence_datetime"),
            "expected_expiration_time": market.get("expected_expiration_time"),
        },
    }


def boundary_row(
    event: dict[str, Any],
    official: dict[str, Any] | None,
    bell: dict[str, Any] | None,
    market_receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    if official:
        start = number(official.get("start_ep"))
        status = str(official.get("status") or "")
        if start is not None:
            candidates.append({
                "source": "official_provider_match_start" if status in OFFICIAL_EXACT else "official_provider_schedule",
                "direction": "exact" if status in OFFICIAL_EXACT else "schedule_bound",
                "timestamp_epoch": start,
                "timestamp_utc": iso(start),
                "precision": "second",
                "evidence": official,
            })
    if bell:
        source = str(bell.get("source") or "")
        if source == "milestone_official" and number(bell.get("bell_ts")) is not None:
            stamp = number(bell["bell_ts"])
            candidates.append({
                "source": "daysheet_milestone_official",
                "direction": "exact",
                "timestamp_epoch": stamp,
                "timestamp_utc": iso(stamp),
                "precision": "subsecond",
                "evidence": bell,
            })
        elif source in POLICY_BLIND_LIVE_BY_SOURCES and number(bell.get("gun_ts")) is not None:
            stamp = number(bell["gun_ts"])
            candidates.append({
                "source": f"daysheet_{source}_live_onset",
                "direction": "live_by",
                "timestamp_epoch": stamp,
                "timestamp_utc": iso(stamp),
                "precision": "subsecond",
                "evidence": bell,
            })
    if market_receipt:
        market = market_receipt["market"]
        raw = market.get("occurrence_datetime") or market.get("expected_expiration_time")
        stamp = dt.datetime.fromisoformat(str(raw).replace("Z", "+00:00")).timestamp() if raw else None
        if stamp is not None:
            candidates.append({
                "source": "exchange_occurrence_schedule",
                "direction": "schedule_bound",
                "timestamp_epoch": stamp,
                "timestamp_utc": iso(stamp),
                "precision": "second",
                "evidence": {
                    "ticker": market.get("ticker"),
                    "event_ticker": market.get("event_ticker"),
                    "occurrence_datetime": market.get("occurrence_datetime"),
                    "expected_expiration_time": market.get("expected_expiration_time"),
                    "response_sha256": market_receipt["raw_sha256"],
                },
            })
    exact = sorted((row for row in candidates if row["direction"] == "exact"), key=lambda row: (row["timestamp_epoch"], row["source"]))
    live_by = sorted((row for row in candidates if row["direction"] == "live_by"), key=lambda row: (row["timestamp_epoch"], row["source"]))
    schedule = sorted((row for row in candidates if row["direction"] == "schedule_bound"), key=lambda row: (row["timestamp_epoch"], row["source"]))
    if exact:
        selected = exact[0]
        precision = "exact"
        field = "exact_start_utc"
    elif live_by:
        selected = live_by[0]
        precision = "live_by_only"
        field = "known_live_by_utc"
    elif schedule:
        selected = schedule[0]
        precision = "schedule_only"
        field = "schedule_bound_utc"
    else:
        raise ExamPreparationError(f"no boundary source for {event['event_id']}")
    return {
        "schema_version": VERSION + "-boundary",
        "event_id": event["event_id"],
        "event_date": event["event_date"],
        "category": event["category"],
        "legs": [leg["ticker"] for leg in event["legs"]],
        "precision_class": precision,
        "right_edge_source_field": field,
        "right_edge_epoch": selected["timestamp_epoch"],
        "right_edge_utc": selected["timestamp_utc"],
        "exact_start_utc": selected["timestamp_utc"] if precision == "exact" else None,
        "known_live_by_utc": selected["timestamp_utc"] if precision == "live_by_only" else None,
        "schedule_bound_utc": selected["timestamp_utc"] if precision == "schedule_only" else None,
        "selected_source": selected["source"],
        "selected_timestamp_precision": selected["precision"],
        "candidate_sources": candidates,
        "policy_outcome_sources_excluded": ["self_fill", "fallback_bell", "percat_fitted"],
    }


def inspect_tape(path: Path) -> dict[str, Any]:
    rows = 0
    parsed = 0
    witness = 0
    first = None
    last = None
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows += 1
            stamp = row.get("ts_et")
            if stamp:
                parsed += 1
                first = first or stamp
                last = stamp
            if witness == 0:
                bids = any(integer(row.get(f"bid_{level}")) is not None and positive(row.get(f"bid_{level}_sz")) is not None for level in range(1, 6))
                asks = any(integer(row.get(f"ask_{level}")) is not None and positive(row.get(f"ask_{level}_sz")) is not None for level in range(1, 6))
                if bids and asks:
                    witness = 1
    return {"csv_rows": rows, "parsed_timestamp_rows": parsed, "first_timestamp_et": first, "last_timestamp_et": last, "two_sided_witness_rows": witness}


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    declaration = load(Path(args.sealed_declaration).resolve())
    event_list = Path(args.event_list).resolve().read_bytes()
    if sha_bytes(event_list) != SEALED_LIST_SHA256:
        raise ExamPreparationError("sealed list hash mismatch")
    event_ids = [line for line in event_list.decode().splitlines() if line]
    if len(event_ids) != 171 or declaration.get("sealed_N") != 171:
        raise ExamPreparationError("sealed denominator mismatch")
    events = [row for row in declaration["events"] if row["event_id"] in set(event_ids)]
    if [row["event_id"] for row in events] != event_ids:
        events = sorted(events, key=lambda row: row["event_id"])
    if [row["event_id"] for row in events] != event_ids:
        raise ExamPreparationError("sealed declaration/list identity mismatch")

    source_root = Path(args.source_root).resolve()
    official_path = source_root / "daysheet_bells_official.json"
    bells_path = source_root / "daysheet_bells.json"
    shadow_path = source_root / "milestone_shadow.jsonl"
    official = load(official_path)
    bells_payload = load(bells_path)
    bells = bells_payload.get("bells", bells_payload)
    metadata_path = Path(args.market_metadata).resolve()
    metadata = load(metadata_path) if metadata_path.exists() else {}
    metadata = {event_id: sanitize_market_receipt(receipt) for event_id, receipt in metadata.items()}
    for event in events:
        if event["event_id"] not in official and event["event_id"] not in metadata:
            ticker = event["legs"][0]["ticker"]
            metadata[event["event_id"]] = fetch_market(ticker)
            time.sleep(0.15)
    write_json(metadata_path, metadata)

    boundaries = []
    for event in events:
        market_receipt = metadata.get(event["event_id"])
        boundaries.append(boundary_row(event, official.get(event["event_id"]), bells.get(event["event_id"]), market_receipt))
    if len({row["event_id"] for row in boundaries}) != 171:
        raise ExamPreparationError("boundary identity conservation failed")
    boundary_path = output / "PRE_MATCH_BOUNDARY_LEDGER.jsonl"
    write_jsonl(boundary_path, boundaries)

    tape_root = Path(args.tape_root).resolve()
    admission_rows = []
    admitted_events = []
    exclusions = []
    for event in events:
        leg_receipts = []
        reasons = []
        for leg in event["legs"]:
            path = tape_root / Path(leg["remote_path"]).name
            if not path.exists():
                reasons.append(f"MISSING_TAPE:{leg['ticker']}")
                continue
            actual_hash = sha_file(path)
            actual_size = path.stat().st_size
            if actual_hash != leg["sha256"] or actual_size != leg["bytes"]:
                reasons.append(f"TAPE_IDENTITY_MISMATCH:{leg['ticker']}")
                continue
            inspected = ({
                "csv_rows": leg["csv_rows"],
                "parsed_timestamp_rows": leg["parsed_timestamp_rows"],
                "first_timestamp_et": leg["first_timestamp_et"],
                "last_timestamp_et": leg["last_timestamp_et"],
                "two_sided_witness_rows": leg["v36_admission_witness_rows"],
            } if args.frozen_witness else inspect_tape(path))
            if inspected["csv_rows"] != leg["csv_rows"] or inspected["parsed_timestamp_rows"] != leg["parsed_timestamp_rows"]:
                reasons.append(f"TAPE_ROW_CENSUS_MISMATCH:{leg['ticker']}")
            if inspected["two_sided_witness_rows"] < 1:
                reasons.append(f"NO_ADMISSIBLE_TWO_SIDED_RECEIPT:{leg['ticker']}")
            leg_receipts.append({
                "ticker": leg["ticker"],
                "path": str(path),
                "sha256": actual_hash,
                "bytes": actual_size,
                **inspected,
            })
        if len(event["legs"]) != 2:
            reasons.append("NOT_EXACTLY_TWO_BIG4_LEGS")
        overlap = event["last_timestamp_epoch"] >= OLD_DEGRADED_RECORDER_START_EPOCH and event["first_timestamp_epoch"] <= OLD_DEGRADED_RECORDER_END_EPOCH
        quality_flags = ["OVERLAPS_OLD_RECORDER_DEGRADED_RECONNECT_INTERVAL"] if overlap else []
        passed = not reasons
        row = {
            "event_id": event["event_id"],
            "category": event["category"],
            "passed": passed,
            "exclusion_reasons": reasons,
            "capture_quality_flags": quality_flags,
            "capture_overlap_is_exclusion_under_dev_law": False,
            "legs": leg_receipts,
        }
        admission_rows.append(row)
        (admitted_events if passed else exclusions).append(event["event_id"] if passed else {"event_id": event["event_id"], "reasons": reasons})
    admission_path = output / "FLOOR_PASS_ADMISSION_LEDGER.jsonl"
    write_jsonl(admission_path, admission_rows)
    exam_list = "".join(event_id + "\n" for event_id in admitted_events).encode()
    (output / "EXAM_EVENT_LIST.txt").write_bytes(exam_list)
    N = len(admitted_events)
    boundary_counts = Counter(row["precision_class"] for row in boundaries if row["event_id"] in set(admitted_events))
    source_snapshot = {
        "schema_version": VERSION + "-sources",
        "files": {
            "daysheet_bells_official.json": {"sha256": sha_file(official_path), "bytes": official_path.stat().st_size},
            "daysheet_bells.json": {"sha256": sha_file(bells_path), "bytes": bells_path.stat().st_size},
            "milestone_shadow.jsonl": {"sha256": sha_file(shadow_path), "bytes": shadow_path.stat().st_size},
            "market_metadata.json": {"sha256": sha_file(metadata_path), "bytes": metadata_path.stat().st_size},
        },
        "official_rows": {event_id: official[event_id] for event_id in sorted(set(event_ids) & set(official))},
        "daysheet_rows": {event_id: bells[event_id] for event_id in sorted(set(event_ids) & set(bells))},
        "market_metadata_for_official_gaps": metadata,
    }
    write_json(output / "BOUNDARY_SOURCE_SNAPSHOT.json", source_snapshot)
    summary = {
        "schema_version": VERSION + "-population",
        "sealed_input_N": 171,
        "admitted_N": N,
        "minimum_N": 60,
        "gate_pass": N >= 60,
        "excluded_N": len(exclusions),
        "exclusions": exclusions,
        "precision_classes": dict(sorted(boundary_counts.items())),
        "capture_gap_flagged_events": [row["event_id"] for row in admission_rows if row["capture_quality_flags"]],
        "sealed_input_list_sha256": SEALED_LIST_SHA256,
        "exam_event_list_sha256": sha_bytes(exam_list),
        "boundary_ledger_sha256": sha_file(boundary_path),
        "admission_ledger_sha256": sha_file(admission_path),
        "floor_pass_law": {
            "source_commit": V36_COMMIT,
            "source_path": "arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js",
            "law": "two big4 leg tapes; each leg has at least one exact-integer, positive-size, two-sided level-1-to-5 receipt",
            "capture_quality_role": "flagged; exclusion only if the unchanged law itself fails",
        },
    }
    write_json(output / "EXAM_POPULATION.json", summary)
    write_json(output / "STAGE12_FORBIDDEN_ACCESS_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden",
        "brain_invocations": 0,
        "score_rows": 0,
        "order_access": 0,
        "position_access": 0,
        "service_mutation": 0,
        "live_engine_access": 0,
        "network_access": "PUBLIC_MARKET_METADATA_FOR_MISSING_SCHEDULE_BOUNDS_ONLY",
    })
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sealed-declaration", required=True)
    parser.add_argument("--event-list", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--tape-root", required=True)
    parser.add_argument("--market-metadata", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--frozen-witness", action="store_true", help="reuse the hash-bound Stage-B row/witness census after re-verifying each tape hash")
    summary = build(parser.parse_args())
    print(compact(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
