#!/usr/bin/env python3
"""Freeze post-Stage-B capture candidates without invoking any policy.

The corrected historical 171 are combined later from their frozen Git
receipts.  This script handles only the capture-only registry extension: it
binds retained-archive materialization, applies the existing REAL_START source
precedence, and preserves the dev floor-pass law (two authoritative formed
legs). Coverage relative to the selected boundary is flagged, never promoted
to a new exclusion rule.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


OFFICIAL_EXACT = {"live", "ended", "interrupted", "P"}
POLICY_BLIND_LIVE_BY_SOURCES = {"tape_flow", "price_divergence", "tape_latch", "te_scoreboard"}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iso(epoch: float) -> str:
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso(value: Any) -> float | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def fetch_market(ticker: str) -> dict[str, Any]:
    url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}"
    errors = []
    for attempt in range(1, 7):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "window1-v47-sealed-exam-stage1/1"})
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
            payload = json.loads(body)
            market = payload.get("market")
            if not isinstance(market, dict):
                raise RuntimeError("missing market envelope")
            return {
                "ticker": ticker,
                "url": url,
                "attempts": attempt,
                "raw_sha256": sha_bytes(body),
                "raw_bytes": len(body),
                "market": {
                    key: market.get(key)
                    for key in (
                        "ticker", "event_ticker", "status", "occurrence_datetime",
                        "expected_expiration_time", "open_time", "close_time",
                    )
                },
            }
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            errors.append(f"attempt={attempt}:{type(exc).__name__}:{exc}")
            if attempt < 6:
                time.sleep(min(10, 2 ** (attempt - 1)))
    raise RuntimeError(f"market metadata failed {ticker}: {' | '.join(errors)}")


def event_leg_id(event_id: str, ticker: str) -> str:
    prefix = event_id + "-"
    if not ticker.startswith(prefix):
        raise RuntimeError(f"ticker/event mismatch {ticker} {event_id}")
    return ticker[len(prefix):]


def selected_boundary(
    event: dict[str, Any],
    receipt: dict[str, Any],
    official: dict[str, Any] | None,
    bell: dict[str, Any] | None,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    if isinstance(official, dict):
        start = official.get("start_ep")
        try:
            start = float(start)
        except (TypeError, ValueError):
            start = None
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
    if isinstance(bell, dict):
        source = str(bell.get("source") or "")
        stamp_value = bell.get("bell_ts") if source == "milestone_official" else bell.get("gun_ts")
        try:
            stamp = float(stamp_value)
        except (TypeError, ValueError):
            stamp = None
        if source == "milestone_official" and stamp is not None:
            candidates.append({"source": "daysheet_milestone_official", "direction": "exact", "timestamp_epoch": stamp, "timestamp_utc": iso(stamp), "precision": "subsecond", "evidence": bell})
        elif source in POLICY_BLIND_LIVE_BY_SOURCES and stamp is not None:
            candidates.append({"source": f"daysheet_{source}_live_onset", "direction": "live_by", "timestamp_epoch": stamp, "timestamp_utc": iso(stamp), "precision": "subsecond", "evidence": bell})
    market = receipt["market"]
    raw = market.get("occurrence_datetime") or market.get("expected_expiration_time")
    schedule = parse_iso(raw)
    if schedule is not None:
        candidates.append({
            "source": "exchange_occurrence_schedule",
            "direction": "schedule_bound",
            "timestamp_epoch": schedule,
            "timestamp_utc": iso(schedule),
            "precision": "second",
            "evidence": {
                "ticker": market.get("ticker"), "event_ticker": market.get("event_ticker"),
                "occurrence_datetime": market.get("occurrence_datetime"), "expected_expiration_time": market.get("expected_expiration_time"),
                "response_sha256": receipt["raw_sha256"],
            },
        })
    ranked = [
        ("exact", "exact", "exact_start_utc"),
        ("live_by", "live_by_only", "known_live_by_utc"),
        ("schedule_bound", "schedule_only", "schedule_bound_utc"),
    ]
    selected = precision = field = None
    for direction, candidate_precision, candidate_field in ranked:
        rows = sorted((row for row in candidates if row["direction"] == direction), key=lambda row: (row["timestamp_epoch"], row["source"]))
        if rows:
            selected, precision, field = rows[0], candidate_precision, candidate_field
            break
    if selected is None:
        raise RuntimeError(f"no REAL_START-method boundary source for {event['event_id']}")
    return {
        "schema_version": "window1-v47-sealed-exam-boundary-v1", "event_id": event["event_id"], "event_date": event["event_date"],
        "category": event["category"], "legs": list(event["tickers"]), "precision_class": precision, "right_edge_source_field": field,
        "right_edge_epoch": selected["timestamp_epoch"], "right_edge_utc": selected["timestamp_utc"],
        "exact_start_utc": selected["timestamp_utc"] if precision == "exact" else None,
        "known_live_by_utc": selected["timestamp_utc"] if precision == "live_by_only" else None,
        "schedule_bound_utc": selected["timestamp_utc"] if precision == "schedule_only" else None,
        "selected_source": selected["source"], "selected_timestamp_precision": selected["precision"], "candidate_sources": candidates,
        "policy_outcome_sources_excluded": ["self_fill", "fallback_bell", "percat_fitted"],
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    registry_path = Path(args.registry).resolve()
    manifest_path = Path(args.materialization_manifest).resolve()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    registry = read_jsonl(registry_path)
    materialization = json.loads(manifest_path.read_text(encoding="utf-8"))
    tape_by_ticker = {row["ticker"]: row for row in materialization["tickers"]}
    source_root = Path(args.source_root).resolve()
    official_path = source_root / "daysheet_bells_official.json"
    bells_path = source_root / "daysheet_bells.json"
    shadow_path = source_root / "milestone_shadow.jsonl"
    official = json.loads(official_path.read_text(encoding="utf-8"))
    bells_payload = json.loads(bells_path.read_text(encoding="utf-8"))
    bells = bells_payload.get("bells", bells_payload)

    candidate_rows = []
    pre_exclusions = []
    for event in sorted(registry, key=lambda row: row["event_id"]):
        tickers = list(event.get("tickers") or [])
        reasons = []
        if len(tickers) != 2:
            reasons.append("NOT_EXACTLY_TWO_BIG4_LEGS")
        for ticker in tickers:
            tape = tape_by_ticker.get(ticker)
            if not tape:
                reasons.append(f"NO_RETAINED_ARCHIVE_ROWS:{ticker}")
            elif not tape.get("authoritative_from_snapshot"):
                reasons.append(f"NO_RETAINED_ARCHIVE_SNAPSHOT:{ticker}")
        if reasons:
            pre_exclusions.append({"event_id": event["event_id"], "category": event["category"], "reasons": reasons})
        else:
            candidate_rows.append(event)

    metadata: dict[str, dict[str, Any]] = {}
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {pool.submit(fetch_market, event["tickers"][0]): event for event in candidate_rows}
        for future in concurrent.futures.as_completed(future_map):
            event = future_map[future]
            try:
                metadata[event["event_id"]] = future.result()
            except Exception as exc:  # exact failure retained in exclusion ledger
                failures.append({"event_id": event["event_id"], "error": str(exc)})

    admitted = []
    boundaries = []
    exclusions = list(pre_exclusions)
    metadata_rows = []
    for event in candidate_rows:
        event_id = event["event_id"]
        receipt = metadata.get(event_id)
        if receipt is None:
            exclusions.append({"event_id": event_id, "category": event["category"], "reasons": ["MARKET_METADATA_UNAVAILABLE"]})
            continue
        metadata_rows.append({"event_id": event_id, **receipt})
        market = receipt["market"]
        reasons = []
        coverage_flags = []
        try:
            boundary = selected_boundary(event, receipt, official.get(event_id), bells.get(event_id))
            right = boundary["right_edge_epoch"]
        except RuntimeError:
            boundary = None
            right = None
            reasons.append("NO_REAL_START_LEDGER_SOURCE")
        leg_rows = []
        for ticker in event["tickers"]:
            tape = tape_by_ticker[ticker]
            first_authoritative = tape.get("first_snapshot_epoch")
            last = tape.get("last_raw_epoch")
            if right is not None and (first_authoritative is None or first_authoritative > right):
                coverage_flags.append(f"AUTHORITATIVE_TAPE_BEGINS_AFTER_BOUNDARY:{ticker}")
            if right is not None and (last is None or last < right):
                coverage_flags.append(f"TAPE_ENDS_BEFORE_BOUNDARY:{ticker}")
            leg_rows.append({
                "ticker": ticker,
                "leg_id": event_leg_id(event_id, ticker),
                "category": event["category"],
                "event_id": event_id,
                "event_date": event["event_date"],
                "path": f"tapes/{ticker}.csv.gz",
                "sha256": tape["tape_sha256"],
                "bytes": tape["tape_bytes"],
                "formed_rows": tape["formed_rows"],
                "formed_rows_after_snapshot": tape["formed_rows_after_snapshot"],
                "first_snapshot_epoch": first_authoritative,
                "first_snapshot_utc": iso(first_authoritative) if first_authoritative is not None else None,
                "last_capture_epoch": last,
                "last_capture_utc": iso(last) if last is not None else None,
            })
        if reasons:
            exclusions.append({"event_id": event_id, "category": event["category"], "reasons": sorted(set(reasons))})
            continue
        assert boundary is not None
        boundaries.append(boundary)
        admitted.append({
            "event_id": event_id,
            "event_date": event["event_date"],
            "category": event["category"],
            "legs": leg_rows,
            "capture_tag": event["tag"],
            "touch_status_at_capture": event["touch_status_at_capture"],
            "first_tagged_utc": event["first_tagged_utc"],
            "capture_quality_flags": sorted(coverage_flags),
            "capture_quality_role": "FLAG_ONLY_NOT_EXCLUSION; FLOOR_PASS_ADMISSION_MATCHES_DEV_TWO_SIDED_BOOK_LAW",
            "boundary": boundary,
        })

    list_bytes = "".join(row["event_id"] + "\n" for row in admitted).encode()
    (output / "NEW_CAPTURE_EVENT_LIST.txt").write_bytes(list_bytes)
    (output / "NEW_CAPTURE_DECLARATION.json").write_bytes(canonical({
        "schema_version": "window1-v47-sealed-exam-new-capture-declaration-v1",
        "registry_sha256": sha_file(registry_path),
        "materialization_manifest_sha256": sha_file(manifest_path),
        "registry_events": len(registry),
        "pre_metadata_candidates": len(candidate_rows),
        "admitted_N": len(admitted),
        "event_list_sha256": sha_bytes(list_bytes),
        "events": admitted,
    }))
    (output / "NEW_CAPTURE_BOUNDARY_LEDGER.jsonl").write_text(
        "".join(compact(row) + "\n" for row in boundaries), encoding="utf-8", newline="\n"
    )
    (output / "NEW_CAPTURE_EXCLUSIONS.json").write_bytes(canonical({
        "schema_version": "window1-v47-sealed-exam-new-capture-exclusions-v1",
        "excluded_N": len(exclusions),
        "reason_counts": {
            reason: sum(reason in row["reasons"] for row in exclusions)
            for reason in sorted({reason for row in exclusions for reason in row["reasons"]})
        },
        "metadata_failures": failures,
        "events": exclusions,
    }))
    (output / "NEW_CAPTURE_MARKET_METADATA.json").write_bytes(canonical({
        "schema_version": "window1-v47-sealed-exam-market-metadata-v1",
        "receipts": sorted(metadata_rows, key=lambda row: row["event_id"]),
    }))
    summary = {
        "schema_version": "window1-v47-sealed-exam-stage1-new-capture-v1",
        "policy_invocations": 0,
        "score_rows": 0,
        "registry_N": len(registry),
        "authoritative_candidate_N": len(candidate_rows),
        "admitted_N": len(admitted),
        "excluded_N": len(exclusions),
        "event_list_sha256": sha_bytes(list_bytes),
        "boundary_ledger_sha256": sha_file(output / "NEW_CAPTURE_BOUNDARY_LEDGER.jsonl"),
        "metadata_receipts": len(metadata_rows),
        "capture_quality_flagged_events": sum(bool(event.get("capture_quality_flags")) for event in admitted),
        "REAL_START_method_sources": {
            "daysheet_bells_official": {"sha256": sha_file(official_path), "bytes": official_path.stat().st_size, "matching_events": sum(event["event_id"] in official for event in admitted)},
            "daysheet_bells": {"sha256": sha_file(bells_path), "bytes": bells_path.stat().st_size, "matching_events": sum(event["event_id"] in bells for event in admitted)},
            "milestone_shadow": {"sha256": sha_file(shadow_path), "bytes": shadow_path.stat().st_size},
            "exchange_metadata_receipts": len(metadata_rows),
        },
    }
    (output / "NEW_CAPTURE_STAGE1_SUMMARY.json").write_bytes(canonical(summary))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--materialization-manifest", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=8)
    result = run(parser.parse_args())
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
