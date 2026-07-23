#!/usr/bin/env python3
"""Build the immutable July 12-20 Window-1 real-start evidence ledger.

This is an evidence classifier, not a start-time imputer.  Exact observed
starts, one-sided live/tape bounds, competing schedules, and schedule-only
fallbacks remain different states.  A schedule-only corridor never becomes
an observed right edge.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, BinaryIO, Iterable
from zoneinfo import ZoneInfo


VERSION = "window1-real-start-ledger-v2"
D = 804
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
LOG_EVENTS = {
    "gun_fired",
    "gun_source_confirm",
    "gun_truth_delta",
    "clock_liar",
    "schedule_match",
    "pm_clock_shadow",
}
TAPE_WINDOW_SECONDS = 15 * 60
TAPE_ACTIVE_MINUTES = 5
TAPE_ONSET_FLOOR = 8
TAPE_ONSET_K = 3.0


class StartLedgerError(RuntimeError):
    pass


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    output = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise StartLedgerError(f"non-object {path}:{line_number}")
            output.append(row)
    return output


def parse_epoch(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        result = float(value)
        if result > 10_000_000_000:
            result /= 1000.0
        return result if math.isfinite(result) else None
    try:
        stamp = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    return stamp.timestamp()


def parse_et(value: Any) -> float | None:
    text = str(value or "")
    for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %I:%M:%S %p"):
        try:
            return dt.datetime.strptime(text, pattern).replace(
                tzinfo=ET
            ).timestamp()
        except ValueError:
            pass
    return None


def iso_utc(value: float | None) -> str | None:
    return (
        dt.datetime.fromtimestamp(value, UTC).isoformat()
        if value is not None else None
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stream_lines(
    path: Path, prefix_bytes: int | None = None,
) -> Iterable[bytes]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as handle:
        if prefix_bytes is None:
            yield from handle
            return
        yield from stream_prefix(handle, prefix_bytes)


def stream_prefix(handle: BinaryIO, prefix_bytes: int) -> Iterable[bytes]:
    used = 0
    while used < prefix_bytes:
        line = handle.readline(prefix_bytes - used)
        if not line:
            break
        used += len(line)
        yield line


def log_paths(log_dir: Path, active_name: str) -> list[Path]:
    output = []
    for day in range(12, 20):
        path = log_dir / f"live_v3_202607{day:02d}.jsonl.gz"
        if path.is_file():
            output.append(path)
    recovered = log_dir / "live_v3_20260718_part2_recovered.jsonl.gz"
    if recovered.is_file():
        output.append(recovered)
    active = log_dir / active_name
    if active.is_file():
        output.append(active)
    return output


def scan_logs(
    paths: list[Path],
    required_events: set[str],
    active_name: str,
    active_prefix_bytes: int,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    facts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    physical = 0
    parsed = 0
    errors = 0
    file_receipts = []
    needles = tuple(
        f'"{value}"'.encode() for value in sorted(LOG_EVENTS)
    )
    for path in paths:
        limit = active_prefix_bytes if path.name == active_name else None
        file_physical = 0
        file_selected = 0
        hasher = hashlib.sha256()
        for line in stream_lines(path, limit):
            physical += 1
            file_physical += 1
            hasher.update(line)
            if not any(needle in line for needle in needles):
                continue
            try:
                row = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                errors += 1
                continue
            event_type = str(row.get("event") or "")
            if event_type not in LOG_EVENTS:
                continue
            details = row.get("details")
            if not isinstance(details, dict):
                continue
            event_id = str(details.get("event") or "")
            if event_id not in required_events:
                continue
            parsed += 1
            file_selected += 1
            facts[event_id].append({
                "event_type": event_type,
                "receipt_ts": parse_epoch(row.get("ts_epoch")),
                "source": details.get("source"),
                "details": details,
                "log_source": (
                    path.name + (
                        f":prefix={active_prefix_bytes}"
                        if limit is not None else ""
                    )
                ),
            })
        file_receipts.append({
            "logical_name": path.name,
            "pinned_prefix_bytes": limit,
            "physical_lines_scanned": file_physical,
            "selected_rows": file_selected,
            "scanned_bytes_sha256": hasher.hexdigest(),
        })
    return facts, {
        "physical_lines_scanned": physical,
        "selected_rows": parsed,
        "parse_errors": errors,
        "files": file_receipts,
    }


def observed_start_rows(path: Path) -> list[dict[str, Any]]:
    connection = sqlite3.connect(
        "file:" + str(path) + "?mode=ro&immutable=1", uri=True
    )
    try:
        columns = [
            row[1] for row in connection.execute(
                "pragma table_info(observed_starts)"
            ).fetchall()
        ]
        required = {
            "te_match_id", "player1", "player2", "kalshi_ticker",
            "first_inplay_at", "inserted_at",
        }
        if not required.issubset(columns):
            raise StartLedgerError("observed_starts schema changed")
        rows = connection.execute(
            """SELECT te_match_id, player1, player2, kalshi_ticker,
                      first_inplay_at, inserted_at
               FROM observed_starts
               WHERE first_inplay_at >= '2026-07-11'
                 AND first_inplay_at < '2026-07-22'"""
        ).fetchall()
    finally:
        connection.close()
    return [{
        "te_match_id": str(row[0]),
        "player1": row[1],
        "player2": row[2],
        "leg_code": str(row[3] or ""),
        "first_inplay_ts": parse_et(row[4]),
        "inserted_ts": parse_et(row[5]),
    } for row in rows]


def normalized_name(value: Any) -> str:
    return "".join(
        character for character in str(value or "").casefold()
        if character.isalnum()
    )


def surname(value: Any) -> str:
    words = [
        "".join(character for character in word.casefold()
                if character.isalnum())
        for word in str(value or "").split()
    ]
    return words[-1] if words else ""


def same_person(left: Any, right: Any) -> bool:
    a, b = normalized_name(left), normalized_name(right)
    if a and b and (a == b or (len(a) >= 5 and (a in b or b in a))):
        return True
    sa, sb = surname(left), surname(right)
    return bool(sa and sb and sa == sb)


def live_score_candidates(
    database: Path | None,
    events: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Use live_scores only at the evidence grain its producer preserves."""
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    summary = {
        "available": False,
        "sha256": None,
        "physical_rows": 0,
        "uniquely_joined_events": 0,
        "ambiguous_or_unmapped_rows": 0,
        "producer_semantics": (
            "te_live.py INSERT OR REPLACE current-state row; last_updated "
            "is a local scrape receipt and not first-point history"
        ),
    }
    if database is None or not database.is_file():
        return output, summary
    connection = sqlite3.connect(
        "file:" + str(database) + "?mode=ro&immutable=1", uri=True
    )
    try:
        columns = {
            row[1] for row in connection.execute(
                "pragma table_info(live_scores)"
            ).fetchall()
        }
        required = {
            "te_match_id", "player1", "player2", "p1_sets", "p2_sets",
            "status", "kalshi_ticker", "last_updated",
        }
        if not required.issubset(columns):
            raise StartLedgerError("live_scores schema changed")
        players: dict[str, set[str]] = defaultdict(set)
        for code, name in connection.execute(
            """SELECT kalshi_code, name FROM players
               WHERE kalshi_code IS NOT NULL AND name IS NOT NULL"""
        ):
            players[str(code).upper()].add(str(name))
        rows = connection.execute(
            """SELECT te_match_id, player1, player2, p1_sets, p2_sets,
                      status, kalshi_ticker, last_updated
               FROM live_scores
               WHERE last_updated >= '2026-07-11'
                 AND last_updated < '2026-07-22'"""
        ).fetchall()
    finally:
        connection.close()
    summary["available"] = True
    summary["sha256"] = sha256_file(database)
    summary["physical_rows"] = len(rows)
    event_windows = []
    for event in events:
        scheduled = parse_epoch(event.get("scheduled_start_exchange_ts"))
        if scheduled is None:
            continue
        leg_names = [
            players.get(str(leg.get("leg") or "").upper(), set())
            for leg in event["legs"]
        ]
        leg_codes = {
            str(leg.get("leg") or "").upper() for leg in event["legs"]
        }
        event_windows.append((event, scheduled, leg_names, leg_codes))
    joined_events: set[str] = set()
    for row in rows:
        (
            match_id, player1, player2, p1_sets, p2_sets,
            status, leg_code, last_updated,
        ) = row
        receipt = parse_et(last_updated)
        if receipt is None:
            summary["ambiguous_or_unmapped_rows"] += 1
            continue
        candidates = []
        for event, scheduled, leg_names, leg_codes in event_windows:
            if not scheduled - 36 * 3600 <= receipt <= scheduled + 36 * 3600:
                continue
            if str(leg_code or "").upper() not in leg_codes:
                continue
            if not all(leg_names):
                continue
            direct = (
                any(same_person(player1, value) for value in leg_names[0])
                and any(same_person(player2, value)
                        for value in leg_names[1])
            )
            reverse = (
                any(same_person(player2, value) for value in leg_names[0])
                and any(same_person(player1, value)
                        for value in leg_names[1])
            )
            if direct or reverse:
                candidates.append(event)
        if len(candidates) != 1:
            summary["ambiguous_or_unmapped_rows"] += 1
            continue
        proof = (
            str(status or "").lower() in {"live", "finished"}
            or int(p1_sets or 0) > 0 or int(p2_sets or 0) > 0
        )
        if not proof:
            continue
        event_id = str(candidates[0]["event_id"])
        output[event_id].append({
            "source": "tennis_db_live_scores_current_state",
            "timestamp": receipt,
            "confidence": "low",
            "authority_tier": 3,
            "exact_point": False,
            "bound_direction": "live_by",
            "timestamp_basis": "local_te_results_scrape_receipt_et",
            "receipt_ts": receipt,
            "evidence": {
                "te_match_id_hash": hashlib.sha256(
                    str(match_id).encode()
                ).hexdigest(),
                "status": status,
                "p1_sets": p1_sets,
                "p2_sets": p2_sets,
                "join": "unique_two_participant_and_time_corridor",
                "semantics": (
                    "current/terminal score proves started by this receipt; "
                    "INSERT OR REPLACE discarded the first transition"
                ),
            },
        })
        joined_events.add(event_id)
    summary["uniquely_joined_events"] = len(joined_events)
    return output, summary


def ws_lifecycle_candidates(
    coverage_ledger: Path | None,
    required_events: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    summary = {
        "available": False,
        "sha256": None,
        "event_rows": 0,
        "events_with_live_transition": 0,
    }
    if coverage_ledger is None or not coverage_ledger.is_file():
        return output, summary
    seen = set()
    for row in read_jsonl(coverage_ledger):
        event_id = str(row.get("event_id") or "")
        if event_id not in required_events:
            raise StartLedgerError(
                f"source coverage row outside D: {event_id}"
            )
        summary["event_rows"] += 1
        for leg in row.get("legs") or []:
            ws = ((leg.get("sources") or {}).get("ws_depth") or {})
            timestamp = parse_epoch(ws.get("first_live_transition_ts"))
            if timestamp is None:
                continue
            basis = (
                ws.get("first_live_transition_timestamp_basis")
                or "unknown_ws_timestamp_basis"
            )
            identity = (event_id, timestamp, basis)
            if identity in seen:
                continue
            seen.add(identity)
            exact = basis == "exchange_payload_timestamp"
            output[event_id].append({
                "source": "ws_market_lifecycle_live_transition",
                "timestamp": timestamp,
                "confidence": "high" if exact else "medium",
                "authority_tier": 1 if exact else 3,
                "exact_point": exact,
                "bound_direction": "exact" if exact else "live_by",
                "timestamp_basis": basis,
                "receipt_ts": (
                    timestamp
                    if basis == "local_ws_recorder_receipt_utc" else None
                ),
                "evidence": {
                    "event_type": "market_lifecycle_v2",
                    "semantics": (
                        "explicit live transition; exact only when the "
                        "payload carries the transition timestamp"
                    ),
                },
            })
    summary.update({
        "available": True,
        "sha256": sha256_file(coverage_ledger),
        "events_with_live_transition": len(output),
    })
    return output, summary


def milestone_shadow_candidates(
    path: Path | None,
    required_events: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    summary = {
        "available": False,
        "sha256": None,
        "physical_rows": 0,
        "parse_errors": 0,
        "required_event_rows": 0,
        "required_events": 0,
        "accepted_exact_rows": 0,
        "accepted_not_live_rows": 0,
        "rejected_rows": 0,
        "status_counts": {},
    }
    if path is None or not path.is_file():
        return output, summary
    summary["available"] = True
    summary["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    statuses: Counter[str] = Counter()
    events_seen: set[str] = set()
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            summary["physical_rows"] += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                summary["parse_errors"] += 1
                continue
            event_id = str(row.get("event") or "")
            if event_id not in required_events:
                continue
            summary["required_event_rows"] += 1
            events_seen.add(event_id)
            status = str(row.get("ms_status") or "")
            statuses[status or "<missing>"] += 1
            timestamp = parse_epoch(row.get("ms_start_ep"))
            receipt = parse_epoch(row.get("ts"))
            live_age = (
                receipt - timestamp
                if receipt is not None and timestamp is not None else None
            )
            accepted_exact = (
                timestamp is not None
                and (
                    status == "P"
                    or (
                        status == "live"
                        and live_age is not None
                        and -300 <= live_age <= 6 * 3600
                    )
                )
            )
            accepted_not_live = (
                receipt is not None
                and status in {"not_started", "SCH"}
                and timestamp is not None
                and timestamp - 12 * 3600 <= receipt <= timestamp + 6 * 3600
            )
            candidate = {
                "source": "milestone_shadow_official_start",
                "timestamp": (
                    timestamp if accepted_exact else receipt
                ) or timestamp,
                "confidence": (
                    "high" if accepted_exact
                    else "medium" if accepted_not_live else "rejected"
                ),
                "authority_tier": (
                    1 if accepted_exact else 2 if accepted_not_live else None
                ),
                "exact_point": accepted_exact,
                "bound_direction": (
                    "exact" if accepted_exact
                    else "not_live_through" if accepted_not_live
                    else "rejected"
                ),
                "timestamp_basis": (
                    "official_provider_start_timestamp"
                    if timestamp is not None
                    else "local_shadow_receipt_utc"
                ),
                "receipt_ts": receipt,
                "evidence": {
                    "ms_status": status or None,
                    "live_age_seconds": (
                        round(live_age, 3)
                        if live_age is not None else None
                    ),
                    "source_id_present": bool(row.get("source_id")),
                    "reason": (
                        None if (accepted_exact or accepted_not_live) else
                        "status/start pair is not in the deployed live/P "
                        "whitelist, or a live observation was stale/outside "
                        "the six-hour deployed age corridor; non-live rows "
                        "must be contemporaneous with the scheduled start"
                    ),
                },
            }
            if candidate["timestamp"] is None:
                candidate["evidence"]["reason"] = (
                    "milestone row lacks both start and receipt timestamp"
                )
            output[event_id].append(candidate)
            summary[
                "accepted_exact_rows" if accepted_exact
                else "accepted_not_live_rows" if accepted_not_live
                else "rejected_rows"
            ] += 1
    summary["required_events"] = len(events_seen)
    summary["status_counts"] = dict(statuses)
    return output, summary


def public_milestone_candidates(
    normalized_path: Path | None,
    manifest_path: Path | None,
    required_events: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    output: dict[str, list[dict[str, Any]]] = defaultdict(list)
    summary = {
        "available": False,
        "normalized_sha256": None,
        "manifest_sha256": None,
        "row_count": 0,
        "required_events_with_rows": 0,
        "accepted_exact_rows": 0,
        "accepted_not_live_rows": 0,
        "rejected_rows": 0,
        "status_counts": {},
        "pagination_complete": False,
    }
    if normalized_path is None and manifest_path is None:
        return output, summary
    if (
        normalized_path is None or manifest_path is None
        or not normalized_path.is_file() or not manifest_path.is_file()
    ):
        raise StartLedgerError(
            "public milestone normalized data and manifest must coexist"
        )
    normalized_hash = hashlib.sha256(
        normalized_path.read_bytes()
    ).hexdigest()
    manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise StartLedgerError("public milestone manifest is not an object")
    pagination = manifest.get("pagination") or {}
    scope = manifest.get("scope") or {}
    artifacts = manifest.get("artifacts") or {}
    complete = (
        scope.get("D") == D
        and scope.get("event_queries") == D
        and pagination.get("all_terminal_cursors_empty") is True
        and pagination.get("failed_event_count") == 0
        and artifacts.get("normalized_sha256") == normalized_hash
    )
    if not complete:
        raise StartLedgerError(
            "public milestone export completeness/hash gate failed"
        )
    statuses: Counter[str] = Counter()
    events_seen: set[str] = set()
    with normalized_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise StartLedgerError(
                    f"non-object public milestone row {line_number}"
                )
            event_id = str(row.get("event_id") or "")
            if event_id not in required_events:
                raise StartLedgerError(
                    f"public milestone row outside D: {event_id}"
                )
            summary["row_count"] += 1
            events_seen.add(event_id)
            status = str(row.get("status") or "")
            statuses[status or "<missing>"] += 1
            timestamp = parse_epoch(row.get("start_utc"))
            exported = parse_epoch(row.get("exported_utc"))
            last_updated = parse_epoch(row.get("last_updated_utc"))
            live_age = (
                last_updated - timestamp
                if last_updated is not None and timestamp is not None
                else None
            )
            accepted_exact = (
                timestamp is not None
                and (
                    status == "P"
                    or (
                        status == "live"
                        and live_age is not None
                        and -300 <= live_age <= 6 * 3600
                    )
                )
            )
            accepted_not_live = (
                status in {"not_started", "SCH"}
                and last_updated is not None
                and timestamp is not None
                and timestamp - 12 * 3600
                <= last_updated <= timestamp + 6 * 3600
            )
            output[event_id].append({
                "source": "public_milestone_final_or_fresh_live",
                "timestamp": (
                    timestamp if accepted_exact else last_updated
                ) or exported,
                "confidence": (
                    "high" if accepted_exact
                    else "medium" if accepted_not_live else "rejected"
                ),
                "authority_tier": (
                    1 if accepted_exact else 2 if accepted_not_live else None
                ),
                "exact_point": accepted_exact,
                "bound_direction": (
                    "exact" if accepted_exact
                    else "not_live_through" if accepted_not_live
                    else "rejected"
                ),
                "timestamp_basis": (
                    "official_provider_start_timestamp"
                    if timestamp is not None
                    else "public_export_receipt_utc"
                ),
                "receipt_ts": last_updated or exported,
                "evidence": {
                    "status": status or None,
                    "last_updated_utc": row.get("last_updated_utc"),
                    "exported_utc": row.get("exported_utc"),
                    "milestone_identity_sha256": row.get(
                        "milestone_identity_sha256"
                    ),
                    "source_identity_sha256": row.get(
                        "source_identity_sha256"
                    ),
                    "live_age_seconds": (
                        round(live_age, 3)
                        if live_age is not None else None
                    ),
                    "reason": (
                        None if (accepted_exact or accepted_not_live) else
                        "status/start pair is not final P or a fresh live "
                        "observation in the deployed six-hour corridor; "
                        "non-live rows must have a contemporaneous provider "
                        "update timestamp"
                    ),
                },
            })
            summary[
                "accepted_exact_rows" if accepted_exact
                else "accepted_not_live_rows" if accepted_not_live
                else "rejected_rows"
            ] += 1
    summary.update({
        "available": True,
        "normalized_sha256": normalized_hash,
        "manifest_sha256": manifest_hash,
        "required_events_with_rows": len(events_seen),
        "status_counts": dict(statuses),
        "pagination_complete": True,
    })
    return output, summary


def exact_te_candidates(
    event_id: str,
    facts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    output = []
    seen = set()
    for fact in facts:
        details = fact["details"]
        if fact["event_type"] == "gun_fired" and (
            fact["source"] != "te_scoreboard"
        ):
            continue
        if fact["event_type"] == "gun_truth_delta" and (
            details.get("truth_src") != "te_scoreboard"
        ):
            continue
        if fact["event_type"] not in {"gun_fired", "gun_truth_delta"}:
            continue
        timestamp = parse_et(details.get("te_first_inplay"))
        if timestamp is None:
            continue
        identity = (
            str(details.get("te_match_id") or ""),
            timestamp,
        )
        if identity in seen:
            continue
        seen.add(identity)
        output.append({
            "source": "te_scoreboard_first_observed_inplay",
            "timestamp": timestamp,
            "confidence": "medium",
            "authority_tier": 2,
            "exact_point": False,
            "timestamp_basis": "local_collector_first_seen_et",
            "receipt_ts": fact["receipt_ts"],
            "evidence": {
                "te_match_id_hash": hashlib.sha256(
                    identity[0].encode()
                ).hexdigest() if identity[0] else None,
                "match_how": details.get("match_how"),
                "log_source": fact["log_source"],
                "semantics": (
                    "collector first sighting on the TE /live/ page; proves "
                    "the match was live by this local receipt but does not "
                    "embed an exchange or first-point start timestamp"
                ),
            },
        })
    return output


def observed_db_candidates(
    event: dict[str, Any],
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scheduled = parse_epoch(event.get("scheduled_start_exchange_ts"))
    leg_codes = {str(leg.get("leg") or "") for leg in event["legs"]}
    candidates = []
    ambiguous = []
    for row in rows:
        timestamp = row["first_inplay_ts"]
        if timestamp is None or row["leg_code"] not in leg_codes:
            continue
        if scheduled is not None and abs(timestamp - scheduled) > 36 * 3600:
            continue
        matching_events = 0
        # Caller supplies only one event here.  Uniqueness across the ledger
        # is checked separately before this evidence is accepted.
        matching_events += 1
        item = {
            "source": "observed_starts_db_first_observed_inplay",
            "timestamp": timestamp,
            "confidence": "medium",
            "authority_tier": 2,
            "exact_point": False,
            "timestamp_basis": "local_collector_first_seen_et",
            "receipt_ts": row["inserted_ts"],
            "evidence": {
                "join": "unique_leg_code_within_36h_schedule_corridor",
                "leg_code": row["leg_code"],
                "te_match_id_hash": hashlib.sha256(
                    row["te_match_id"].encode()
                ).hexdigest(),
                "semantics": (
                    "set-once collector receipt from the TE /live/ page; "
                    "known-live-by bound, not an exchange start clock"
                ),
            },
            "_row_identity": row["te_match_id"],
        }
        (candidates if matching_events == 1 else ambiguous).append(item)
    return candidates, ambiguous


def official_and_bound_candidates(
    facts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    output = []
    for fact in facts:
        if fact["event_type"] != "gun_fired":
            continue
        source = str(fact["source"] or "")
        details = fact["details"]
        receipt = fact["receipt_ts"]
        if source == "milestone_official":
            status = str(details.get("ms_status") or "")
            official = parse_epoch(
                details.get("official_start_ep")
                or details.get("official_start")
            )
            if status in {"live", "P"}:
                output.append({
                    "source": "exchange_milestone_live_transition",
                    "timestamp": official or receipt,
                    "confidence": "high" if official else "medium",
                    "authority_tier": 1,
                    "exact_point": official is not None,
                    "timestamp_basis": (
                        "official_provider_start_timestamp"
                        if official is not None
                        else "local_engine_receipt_utc"
                    ),
                    "receipt_ts": receipt,
                    "evidence": {
                        "ms_status": status,
                        "official_start_present": official is not None,
                        "log_source": fact["log_source"],
                    },
                })
            else:
                output.append({
                    "source": "milestone_nonlive_status",
                    "timestamp": receipt,
                    "confidence": "rejected",
                    "authority_tier": None,
                    "exact_point": False,
                    "timestamp_basis": "local_engine_receipt_utc",
                    "receipt_ts": receipt,
                    "evidence": {
                        "ms_status": status,
                        "reason": "status does not prove live transition",
                        "official_start_claim": iso_utc(official),
                        "log_source": fact["log_source"],
                    },
                })
        elif source == "schedule_live":
            output.append({
                "source": "schedule_feed_live_transition",
                "timestamp": receipt,
                "confidence": "medium",
                "authority_tier": 3,
                "exact_point": False,
                "timestamp_basis": "local_engine_receipt_utc",
                "receipt_ts": receipt,
                "evidence": {
                    "semantics": "match known live by receipt timestamp",
                    "log_source": fact["log_source"],
                },
            })
        elif source in {
            "tape_latch", "tape_flow", "fallback_bell",
            "price_divergence", "self_fill", "percat_fitted",
        }:
            output.append({
                "source": "engine_regime_transition:" + source,
                "timestamp": receipt,
                "confidence": "low",
                "authority_tier": 4,
                "exact_point": False,
                "timestamp_basis": "local_engine_receipt_utc",
                "receipt_ts": receipt,
                "evidence": {
                    "semantics": "corroborating regime bound, not exact start",
                    "log_source": fact["log_source"],
                },
            })
    return output


def load_tape_onsets(
    path: Path | None,
    ticker_to_event: dict[str, str],
    anchors: dict[str, float],
    fire_times: dict[str, float],
) -> dict[str, float]:
    if path is None or not path.is_file():
        return {}
    minutes_by_event: dict[str, Counter[int]] = defaultdict(Counter)
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            ticker = str(row.get("ticker") or "")
            event = ticker_to_event.get(ticker)
            timestamp = parse_epoch(row.get("exchange_ts"))
            identity = str(
                row.get("trade_id") or row.get("receipt_id") or ""
            )
            size = float(row.get("size") or 0)
            anchor = anchors.get(event or "")
            if (
                event and timestamp is not None and identity and size > 0
                and anchor is not None
            ):
                t0 = anchor - 2 * 3600
                t1 = max(
                    anchor + 4 * 3600,
                    fire_times.get(event, 0) + 1800,
                )
                if t0 <= timestamp <= t1:
                    minutes_by_event[event][
                        int(timestamp // 60) * 60
                    ] += 1
    output = {}
    for event, minutes in minutes_by_event.items():
        anchor = anchors.get(event)
        if anchor is None:
            continue
        t0 = anchor - 2 * 3600
        if not minutes:
            continue
        base60 = sum(
            count for minute, count in minutes.items()
            if minute < t0 + 3600
        )
        needed = max(
            TAPE_ONSET_FLOOR,
            TAPE_ONSET_K * (base60 / 4.0),
        )
        for minute in sorted(minutes):
            active = sum(
                bool(minutes.get(value))
                for value in range(
                    minute - 14 * 60, minute + 60, 60
                )
            )
            if active < TAPE_ACTIVE_MINUTES:
                continue
            trailing = sum(
                minutes.get(value, 0)
                for value in range(
                    minute - 14 * 60, minute + 60, 60
                )
            )
            forward = sum(
                minutes.get(value, 0)
                for value in range(
                    minute + 60, minute + 31 * 60, 60
                )
            )
            if trailing >= needed and forward >= needed:
                output[event] = float(minute)
                break
    return output


def choose_start(
    candidates: list[dict[str, Any]],
    scheduled: float | None,
    corridor_minutes: int,
) -> dict[str, Any]:
    accepted = [
        row for row in candidates
        if row.get("authority_tier") is not None
    ]
    exact = [row for row in accepted if row["exact_point"]]
    live_bounds = [
        row for row in accepted
        if not row["exact_point"]
        and row.get("bound_direction", "live_by") == "live_by"
    ]
    not_live_bounds = [
        row for row in accepted
        if row.get("bound_direction") == "not_live_through"
    ]
    not_live_winner = (
        max(
            not_live_bounds,
            key=lambda row: (
                row["timestamp"], -row["authority_tier"], row["source"]
            ),
        )
        if not_live_bounds else None
    )
    if exact:
        winner = sorted(
            exact, key=lambda row: (
                row["authority_tier"], row["timestamp"], row["source"]
            )
        )[0]
        bound_winner = winner
        state = "verified_exact"
        right_edge = winner["timestamp"]
        latest_bound = winner["timestamp"]
        safe_prestart = winner["timestamp"]
    elif live_bounds:
        winner = sorted(
            live_bounds, key=lambda row: (
                row["authority_tier"], row["timestamp"], row["source"]
            )
        )[0]
        # Every accepted transition proves start <= its timestamp.  The
        # earliest such receipt is the tightest lawful no-post-start bound,
        # even when another source has higher descriptive precedence.
        bound_winner = sorted(
            live_bounds, key=lambda row: (
                row["timestamp"], row["authority_tier"], row["source"]
            )
        )[0]
        state = (
            "bounded_start_interval"
            if not_live_winner is not None
            else "bounded_live_by_timestamp"
        )
        right_edge = None
        latest_bound = bound_winner["timestamp"]
        safe_prestart = (
            not_live_winner["timestamp"]
            if not_live_winner is not None else None
        )
    else:
        winner = {
            "source": "schedule_plus_declared_corridor",
            "confidence": "fallback_only",
            "authority_tier": 5,
            "exact_point": False,
            "timestamp_basis": (
                "exchange_catalog_schedule_plus_declared_corridor"
            ),
            "timestamp": (
                scheduled + corridor_minutes * 60
                if scheduled is not None else None
            ),
            "receipt_ts": None,
            "evidence": {
                "corridor_minutes": corridor_minutes,
                "semantics": "estimated right edge; never observed start",
            },
        }
        bound_winner = winner
        state = (
            "schedule_fallback_with_not_live_bound"
            if not_live_winner is not None
            else "schedule_only_censored"
        )
        right_edge = None
        latest_bound = None
        safe_prestart = (
            not_live_winner["timestamp"]
            if not_live_winner is not None else None
        )
    exact_values = sorted({
        round(row["timestamp"], 3) for row in exact
    })
    contradiction = (
        len(exact_values) > 1
        and exact_values[-1] - exact_values[0] > 60
    )
    interval_contradiction = (
        right_edge is None
        and not_live_winner is not None
        and safe_prestart is not None
        and latest_bound is not None
        and safe_prestart >= latest_bound
    )
    contradiction = contradiction or interval_contradiction
    return {
        "start_state": state,
        "selected_source": winner["source"],
        "selected_confidence": winner["confidence"],
        "selected_evidence_utc": iso_utc(winner["timestamp"]),
        "selected_evidence_time_basis": winner.get("timestamp_basis"),
        "verified_start_utc": iso_utc(right_edge),
        "verified_start_time_basis": (
            winner.get("timestamp_basis") if right_edge is not None else None
        ),
        "known_live_by_utc": iso_utc(latest_bound),
        "known_live_by_source": (
            bound_winner["source"] if latest_bound is not None else None
        ),
        "known_live_by_time_basis": (
            bound_winner.get("timestamp_basis")
            if latest_bound is not None else None
        ),
        "not_live_through_utc": iso_utc(
            not_live_winner["timestamp"]
            if not_live_winner is not None else None
        ),
        "not_live_through_source": (
            not_live_winner["source"]
            if not_live_winner is not None else None
        ),
        "not_live_through_time_basis": (
            not_live_winner.get("timestamp_basis")
            if not_live_winner is not None else None
        ),
        "safe_prestart_cutoff_utc": (
            iso_utc(safe_prestart) if not contradiction else None
        ),
        "safe_prestart_cutoff_time_basis": (
            winner.get("timestamp_basis")
            if right_edge is not None
            else (
                not_live_winner.get("timestamp_basis")
                if not_live_winner is not None else None
            )
        ),
        "start_interval_utc": {
            "lower_exclusive": iso_utc(
                not_live_winner["timestamp"]
                if not_live_winner is not None else None
            ),
            "upper_inclusive": iso_utc(latest_bound),
        },
        "schedule_fallback_right_edge_utc": iso_utc(
            scheduled + corridor_minutes * 60
            if scheduled is not None else None
        ),
        "boundary_censored": state != "verified_exact" or contradiction,
        "definitely_prestart_scoring_available": (
            safe_prestart is not None and not contradiction
        ),
        "interval_contradiction": interval_contradiction,
        "contradiction": contradiction,
        "exact_candidate_spread_seconds": (
            exact_values[-1] - exact_values[0]
            if len(exact_values) > 1 else 0
        ),
    }


def sanitize_candidate(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (
            iso_utc(value) if key in {"timestamp", "receipt_ts"} else value
        )
        for key, value in row.items()
        if not key.startswith("_")
    }


def post_sample_official_start(
    event_id: str,
    milestone_shadow: Path | None,
    official_bells: Path | None,
) -> dict[str, Any]:
    starts: list[float] = []
    statuses: Counter[str] = Counter()
    shadow_receipts: list[dict[str, Any]] = []
    if milestone_shadow is not None and milestone_shadow.is_file():
        with milestone_shadow.open(
            encoding="utf-8", errors="replace"
        ) as handle:
            for line in handle:
                if event_id not in line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if str(row.get("event") or "") != event_id:
                    continue
                status = str(row.get("ms_status") or "")
                timestamp = parse_epoch(
                    row.get("ms_start_ep") or row.get("ms_start")
                )
                receipt = parse_epoch(row.get("ts"))
                statuses[status or "<missing>"] += 1
                if timestamp is not None:
                    starts.append(timestamp)
                shadow_receipts.append({
                    "status": status or None,
                    "official_start_utc": iso_utc(timestamp),
                    "local_receipt_utc": iso_utc(receipt),
                })
    bell = None
    if official_bells is not None and official_bells.is_file():
        value = json.loads(official_bells.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            raw = value.get(event_id)
            if isinstance(raw, dict):
                timestamp = parse_epoch(
                    raw.get("start_ep") or raw.get("start_date")
                )
                status = str(raw.get("status") or "")
                if timestamp is not None:
                    starts.append(timestamp)
                if status:
                    statuses[status] += 1
                bell = {
                    "status": status or None,
                    "official_start_utc": iso_utc(timestamp),
                    "fetched_at_utc": iso_utc(
                        parse_epoch(raw.get("fetched_at"))
                    ),
                    "final": raw.get("final"),
                }
    distinct = sorted({round(value, 3) for value in starts})
    inplay_status = any(
        statuses.get(value, 0) > 0
        for value in ("live", "P", "interrupted")
    )
    exact = (
        distinct[0] if distinct
        and distinct[-1] - distinct[0] <= 1
        and inplay_status else None
    )
    return {
        "verified_start_utc": iso_utc(exact),
        "timestamp_basis": (
            "consistent_official_milestone_start_date"
            if exact is not None else None
        ),
        "confidence": "high" if exact is not None else "unresolved",
        "shadow_rows": shadow_receipts,
        "official_bell": bell,
        "status_counts": dict(statuses),
        "distinct_reported_start_count": len(distinct),
        "reported_starts_consistent_within_one_second": (
            bool(distinct) and distinct[-1] - distinct[0] <= 1
        ),
    }


def scan_post_sample(
    active_log: Path,
    event_id: str,
    milestone_shadow: Path | None = None,
    official_bells: Path | None = None,
) -> dict[str, Any]:
    selected = []
    start_candidates = []
    relevant_types = {
        "schedule_match", "kalshi_occ_delta", "v4_place",
        "order_placed", "tape_seed_live_confirm",
        "unbooked_fill_defect", "reconcile_v4_adopted",
        "entry_filled", "gun_fired", "order_cancelled",
        "match_live_resting_cancel", "clock_liar",
    }

    def scrub(value: Any, key: str = "") -> Any:
        lowered = key.lower()
        if (
            lowered == "id" or lowered.endswith("_id")
            or "order_id" in lowered or "client_order" in lowered
            or lowered in {
                "api_key", "account", "subaccount", "token",
                "signature", "credential",
            }
        ):
            return "[redacted-private-identifier]"
        if isinstance(value, dict):
            return {str(k): scrub(v, str(k)) for k, v in value.items()}
        if isinstance(value, list):
            return [scrub(item, key) for item in value]
        return value

    with active_log.open("rb") as handle:
        for line in handle:
            if event_id.encode() not in line:
                continue
            try:
                row = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            details = row.get("details")
            if not isinstance(details, dict):
                details = {}
            clean = scrub(details)
            event_type = str(row.get("event") or "")
            timestamp = parse_epoch(row.get("ts_epoch"))
            if event_type not in relevant_types:
                continue
            if (
                event_type == "order_placed"
                and str(clean.get("action") or "") != "buy"
            ):
                continue
            selected.append({
                "event_type": event_type,
                "ticker": row.get("ticker"),
                "exchange_or_receipt_ts": iso_utc(timestamp),
                "details": clean,
            })
            if event_type == "gun_fired":
                start_candidates.extend(official_and_bound_candidates([{
                    "event_type": event_type,
                    "source": clean.get("source"),
                    "receipt_ts": timestamp,
                    "details": clean,
                    "log_source": active_log.name,
                }]))
            if event_type == "gun_truth_delta":
                start_candidates.extend(exact_te_candidates(event_id, [{
                    "event_type": event_type,
                    "source": clean.get("source"),
                    "receipt_ts": timestamp,
                    "details": clean,
                    "log_source": active_log.name,
                }]))
    start = choose_start(start_candidates, None, 60)
    official_start = post_sample_official_start(
        event_id, milestone_shadow, official_bells
    )
    exact = parse_epoch(official_start["verified_start_utc"])
    buy_rows = [
        row for row in selected
        if row["event_type"] == "order_placed"
    ]
    fill_rows = [
        row for row in selected
        if row["event_type"] == "entry_filled"
    ]
    cancel_rows = [
        row for row in selected
        if row["event_type"] == "order_cancelled"
        and row["details"].get("success") is True
    ]
    schedule_rows = [
        row for row in selected
        if row["event_type"] == "schedule_match"
    ]
    live_by = parse_epoch(start["known_live_by_utc"])
    def after_start(row: dict[str, Any]) -> bool | None:
        timestamp = parse_epoch(row["exchange_or_receipt_ts"])
        return timestamp >= exact if timestamp is not None and exact else None

    return {
        "event_id": event_id,
        "in_D": False,
        "scope": "separate_post_sample_boundary_forensic",
        "generic_development_start_ruling": start,
        "official_start_ruling": official_start,
        "chronology_authority": {
            "commit": (
                "3f5d85d47a49083dd40056b1866191c649057b7b"
            ),
            "statement": (
                "P0 regression chronology records actual start about "
                "19:00 ET and the false 22:00 schedule"
            ),
        },
        "old_start_input": (
            schedule_rows[0] if schedule_rows else None
        ),
        "entry_buy_rows": [
            {**row, "after_official_start": after_start(row)}
            for row in buy_rows
        ],
        "entry_fill_rows": [
            {
                **row,
                "after_official_start": after_start(row),
                "timestamp_semantics": (
                    "local engine reconciliation/booking receipt; exact "
                    "exchange fill timestamp was not retained in this log"
                ),
            }
            for row in fill_rows
        ],
        "successful_cancel_rows": [
            {**row, "after_official_start": after_start(row)}
            for row in cancel_rows
        ],
        "causal_findings": {
            "mayo_placement_post_start": any(
                str(row["ticker"]).endswith("-MAY")
                and after_start(row) is True
                for row in buy_rows
            ),
            "mayo_fill_proven_post_start": any(
                str(row["ticker"]).endswith("-MAY")
                and after_start(row) is True
                for row in fill_rows
            ),
            "michelsen_placement_post_start": any(
                str(row["ticker"]).endswith("-MIC")
                and after_start(row) is True
                for row in buy_rows
            ),
            "michelsen_cancel_post_start": any(
                str(row["ticker"]).endswith("-MIC")
                and after_start(row) is True
                for row in cancel_rows
            ),
            "exact_exchange_fill_timestamp_available": False,
            "old_start_defect": (
                "22:00 ET expected-expiration/end clock was treated as "
                "the 19:00 ET match start"
            ),
        },
        "selected_log_row_count": len(selected),
        "entry_buy_row_count": len(buy_rows),
        "entry_fill_row_count": len(fill_rows),
        "successful_cancel_row_count": len(cancel_rows),
        "rows_at_or_after_known_live_bound": (
            sum(
                parse_epoch(row["exchange_or_receipt_ts"]) >= live_by
                for row in buy_rows + fill_rows
            )
            if live_by is not None else None
        ),
        "sanitized_rows": selected,
    }


def run(args: argparse.Namespace) -> int:
    events = read_jsonl(Path(args.events).resolve())
    if len(events) != D:
        raise StartLedgerError(f"immutable D changed: {len(events)}")
    required_events = {str(row["event_id"]) for row in events}
    if len(required_events) != D:
        raise StartLedgerError("duplicate event ids")
    ticker_to_event = {
        str(leg["ticker"]): str(event["event_id"])
        for event in events for leg in event["legs"]
    }
    public_path = (
        Path(args.public_prints).resolve() if args.public_prints else None
    )
    public_manifest_path = (
        Path(args.public_tape_manifest).resolve()
        if args.public_tape_manifest else None
    )
    public_receipt = {
        "available": False,
        "normalized_sha256": None,
        "manifest_sha256": None,
        "pagination_complete": False,
    }
    if public_path is not None or public_manifest_path is not None:
        if (
            public_path is None or public_manifest_path is None
            or not public_path.is_file()
            or not public_manifest_path.is_file()
        ):
            raise StartLedgerError(
                "public prints and public-tape manifest must coexist"
            )
        public_hash = sha256_file(public_path)
        public_manifest = json.loads(
            public_manifest_path.read_text(encoding="utf-8")
        )
        pagination = public_manifest.get("pagination") or {}
        denominator = (
            public_manifest.get("immutable_denominator") or {}
        )
        artifact = (
            (public_manifest.get("artifacts") or {})
            .get("normalized_true_prints") or {}
        )
        if not (
            pagination.get("all_terminal_cursors_empty") is True
            and pagination.get("failed_ticker_count") == 0
            and denominator.get("D") == D
            and denominator.get("required_leg_tickers") == 1608
            and artifact.get("sha256") == public_hash
        ):
            raise StartLedgerError(
                "public-tape completeness/hash gate failed"
            )
        public_receipt = {
            "available": True,
            "normalized_sha256": public_hash,
            "manifest_sha256": sha256_file(public_manifest_path),
            "pagination_complete": True,
        }
    log_dir = Path(args.log_dir).resolve()
    paths = log_paths(log_dir, args.active_log_name)
    facts, log_summary = scan_logs(
        paths, required_events, args.active_log_name,
        args.active_log_prefix_bytes,
    )
    observed = observed_start_rows(Path(args.observed_starts_db).resolve())
    live_scores, live_score_summary = live_score_candidates(
        Path(args.tennis_db).resolve() if args.tennis_db else None,
        events,
    )
    ws_lifecycle, ws_lifecycle_summary = ws_lifecycle_candidates(
        Path(args.source_coverage_ledger).resolve()
        if args.source_coverage_ledger else None,
        required_events,
    )
    milestone_candidates, milestone_summary = milestone_shadow_candidates(
        Path(args.milestone_shadow).resolve()
        if args.milestone_shadow else None,
        required_events,
    )
    public_milestones, public_milestone_summary = (
        public_milestone_candidates(
            Path(args.milestones_normalized).resolve()
            if args.milestones_normalized else None,
            Path(args.milestone_manifest).resolve()
            if args.milestone_manifest else None,
            required_events,
        )
    )
    anchors = {
        str(event["event_id"]): parse_epoch(
            event.get("scheduled_start_exchange_ts")
        )
        for event in events
    }
    fire_times = {}
    for event_id, event_facts in facts.items():
        for fact in event_facts:
            details = fact["details"]
            if (
                fact["event_type"] == "clock_liar"
                and str(details.get("anchor_source") or "").startswith(
                    "te_honest"
                )
                and parse_epoch(details.get("te_honest_start")) is not None
            ):
                anchors[event_id] = parse_epoch(
                    details["te_honest_start"]
                )
            if (
                fact["event_type"] == "gun_fired"
                and fact["receipt_ts"] is not None
            ):
                fire_times[event_id] = min(
                    fire_times.get(event_id, math.inf),
                    fact["receipt_ts"],
                )
    tape_onsets = load_tape_onsets(
        public_path,
        ticker_to_event, anchors, fire_times,
    )

    # Prove uniqueness before accepting leg-code/date joins from the bank.
    db_matches: dict[str, list[str]] = defaultdict(list)
    raw_db_by_event = {}
    for event in events:
        candidates, _ = observed_db_candidates(event, observed)
        raw_db_by_event[event["event_id"]] = candidates
        for row in candidates:
            db_matches[row["_row_identity"]].append(event["event_id"])

    ledger = []
    for event in events:
        event_id = str(event["event_id"])
        candidates = exact_te_candidates(event_id, facts.get(event_id, []))
        candidates.extend(milestone_candidates.get(event_id, []))
        candidates.extend(public_milestones.get(event_id, []))
        candidates.extend(live_scores.get(event_id, []))
        candidates.extend(ws_lifecycle.get(event_id, []))
        for row in raw_db_by_event[event_id]:
            if len(db_matches[row["_row_identity"]]) == 1:
                candidates.append(row)
        candidates.extend(
            official_and_bound_candidates(facts.get(event_id, []))
        )
        if event_id in tape_onsets:
            candidates.append({
                "source": "public_tape_5_prints_in_15m_onset",
                "timestamp": tape_onsets[event_id],
                "confidence": "low",
                "authority_tier": 4,
                "exact_point": False,
                "bound_direction": "live_by",
                "timestamp_basis": "public_trade_exchange_created_time",
                "receipt_ts": None,
                "evidence": {
                    "active_minutes_required": TAPE_ACTIVE_MINUTES,
                    "trailing_window_seconds": TAPE_WINDOW_SECONDS,
                    "flow_step_floor": TAPE_ONSET_FLOOR,
                    "flow_step_multiple": TAPE_ONSET_K,
                    "identity_deduplicated": True,
                    "positive_verified_size_only": True,
                },
            })
        scheduled = parse_epoch(event.get("scheduled_start_exchange_ts"))
        ruling = choose_start(
            candidates, scheduled, args.schedule_corridor_minutes
        )
        ledger.append({
            "schema_version": VERSION,
            "event_id": event_id,
            "event_date": event["event_date"],
            "category": event["category"],
            "legs": event["legs"],
            "scheduled_start_exchange_ts": event.get(
                "scheduled_start_exchange_ts"
            ),
            "schedule_source": event.get("schedule_source"),
            "schedule_corridor_minutes": args.schedule_corridor_minutes,
            **ruling,
            "candidate_evidence": [
                sanitize_candidate(row) for row in sorted(
                    candidates,
                    key=lambda value: (
                        value.get("authority_tier") or 99,
                        value.get("timestamp") or math.inf,
                        value.get("source") or "",
                    ),
                )
            ],
            "unmatched_observed_start_rows_are_not_silently_joined": True,
        })

    output = Path(args.ledger_output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in ledger:
            handle.write(json.dumps(
                row, sort_keys=True, separators=(",", ":")
            ) + "\n")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    states = Counter(row["start_state"] for row in ledger)
    sources = Counter(row["selected_source"] for row in ledger)
    summary = {
        "schema_version": VERSION,
        "D": D,
        "ledger_sha256": digest,
        "precedence": [
            "exchange milestone status live/P with official timestamp",
            (
                "timestamped scoreboard/first-point evidence when its source "
                "carries an actual point clock"
            ),
            (
                "TE first-observed-inplay collector receipt as a one-sided "
                "known-live-by bound"
            ),
            "one-sided live-feed transition bound",
            "identity-deduplicated verified-size public-tape regime bound",
            "schedule plus declared corridor fallback",
        ],
        "state_counts": dict(states),
        "selected_source_counts": dict(sources),
        "boundary_censored_events": sum(
            row["boundary_censored"] for row in ledger
        ),
        "definitely_prestart_scorable_events": sum(
            row["definitely_prestart_scoring_available"]
            for row in ledger
        ),
        "contradictory_events": sum(
            row["contradiction"] for row in ledger
        ),
        "public_tape_onset_events": len(tape_onsets),
        "public_tape_receipt": public_receipt,
        "observed_starts_db_rows_in_scan": len(observed),
        "observed_starts_uniquely_joined_rows": sum(
            len(events_for_row) == 1
            for events_for_row in db_matches.values()
        ),
        "observed_starts_ambiguous_rows": sum(
            len(events_for_row) > 1
            for events_for_row in db_matches.values()
        ),
        "milestone_shadow": milestone_summary,
        "public_milestone_export": public_milestone_summary,
        "tennis_db_live_scores": live_score_summary,
        "ws_lifecycle": ws_lifecycle_summary,
        "log_scan": log_summary,
        "laws": {
            "schedule_only_is_observed": False,
            "post_known_live_placement_is_window1": False,
            "first_market_trade_alone_is_start": False,
            "live_scores_last_updated_is_exact_start": False,
            "bounded_action_is_scorable_only_if_complete_at_or_before_"
            "safe_prestart_cutoff": True,
            "all_events_remain_in_D": True,
        },
    }
    Path(args.summary_output).resolve().write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if args.post_sample_event and args.post_sample_output:
        post = scan_post_sample(
            log_dir / args.active_log_name,
            args.post_sample_event,
            (
                Path(args.post_sample_milestone_shadow).resolve()
                if args.post_sample_milestone_shadow else None
            ),
            (
                Path(args.post_sample_official_bells).resolve()
                if args.post_sample_official_bells else None
            ),
        )
        Path(args.post_sample_output).resolve().write_text(
            json.dumps(post, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "D": D,
        "state_counts": dict(states),
        "boundary_censored_events": summary["boundary_censored_events"],
        "contradictory_events": summary["contradictory_events"],
        "ledger_sha256": digest,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--log-dir", required=True)
    result.add_argument("--active-log-name", default="live_v3_20260720.jsonl")
    result.add_argument("--active-log-prefix-bytes", type=int, required=True)
    result.add_argument("--observed-starts-db", required=True)
    result.add_argument("--milestone-shadow")
    result.add_argument("--milestones-normalized")
    result.add_argument("--milestone-manifest")
    result.add_argument("--public-prints")
    result.add_argument("--public-tape-manifest")
    result.add_argument("--tennis-db")
    result.add_argument("--source-coverage-ledger")
    result.add_argument("--schedule-corridor-minutes", type=int, default=60)
    result.add_argument("--ledger-output", required=True)
    result.add_argument("--summary-output", required=True)
    result.add_argument("--post-sample-event")
    result.add_argument("--post-sample-output")
    result.add_argument("--post-sample-milestone-shadow")
    result.add_argument("--post-sample-official-bells")
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
