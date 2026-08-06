#!/usr/bin/env python3
"""Tag newly captured big-4 tennis events as capture-only holdout candidates.

This is recorder infrastructure.  It reads public event metadata and writes an
append-only registry.  It never imports a strategy, scorer, or trading client.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import random
import tempfile
import time
from typing import Any
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows imports the module for tests.
    fcntl = None


VERSION = "window1-holdout-capture-registry-v1"
ENDPOINT = "https://api.elections.kalshi.com/trade-api/v2/events"
SERIES = {
    "KXATPMATCH": "ATP_MAIN",
    "KXWTAMATCH": "WTA_MAIN",
    "KXATPCHALLENGERMATCH": "ATP_CHALL",
    "KXWTACHALLENGERMATCH": "WTA_CHALL",
}
ET = ZoneInfo("America/New_York")


class CaptureRegistryError(RuntimeError):
    """The capture-only registry contract failed closed."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def request_json(url: str, attempts: int = 4) -> dict[str, Any]:
    last: Exception | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json",
                     "User-Agent": f"omi-capture-registry/{VERSION}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                value = json.loads(response.read())
            if not isinstance(value, dict):
                raise CaptureRegistryError("event endpoint returned non-object")
            return value
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                json.JSONDecodeError, CaptureRegistryError) as exc:
            last = exc
            retryable = not isinstance(exc, urllib.error.HTTPError) or (
                exc.code == 429 or 500 <= exc.code < 600
            )
            if not retryable or attempt + 1 == attempts:
                break
            time.sleep(min(12.0, (2 ** attempt) + random.random()))
    raise CaptureRegistryError(f"event discovery failed: {last}")


def event_date(event_id: str) -> dt.date | None:
    import re
    match = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", event_id)
    if not match:
        return None
    months = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5,
        "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10,
        "NOV": 11, "DEC": 12,
    }
    try:
        return dt.date(2000 + int(match.group(1)), months[match.group(2)],
                       int(match.group(3)))
    except (KeyError, ValueError):
        return None


def discover(now: dt.datetime) -> list[dict[str, Any]]:
    dates = {now.astimezone(ET).date(),
             now.astimezone(ET).date() + dt.timedelta(days=1)}
    rows: dict[str, dict[str, Any]] = {}
    for series, category in SERIES.items():
        cursor = None
        for page_number in range(1, 41):
            query = {
                "series_ticker": series,
                "with_nested_markets": "true",
                "limit": "200",
                "status": "settled,open,closed,unopened",
            }
            if cursor:
                query["cursor"] = cursor
            payload = request_json(ENDPOINT + "?" + urllib.parse.urlencode(query))
            events = payload.get("events")
            if not isinstance(events, list):
                raise CaptureRegistryError(
                    f"{series} page {page_number} lacks events[]"
                )
            for event in events:
                event_id = str((event or {}).get("event_ticker") or "")
                if event_date(event_id) not in dates:
                    continue
                markets = event.get("markets") or []
                tickers = sorted({
                    str(market.get("ticker") or "")
                    for market in markets if market.get("ticker")
                })
                if len(tickers) != 2:
                    continue
                identity = {
                    "event_id": event_id,
                    "category": category,
                    "event_date": event_date(event_id).isoformat(),
                    "tickers": tickers,
                    "series": series,
                }
                rows[event_id] = identity
            cursor = str(payload.get("cursor") or "")
            if not cursor:
                break
        else:
            raise CaptureRegistryError(f"{series} pagination exceeded 40 pages")
    return [rows[key] for key in sorted(rows)]


def load_registry(path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    rows = []
    identities = set()
    if not path.exists():
        return rows, identities
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            event_id = str(value.get("event_id") or "")
            if not event_id or event_id in identities:
                raise CaptureRegistryError(
                    f"registry identity invalid at line {number}"
                )
            identities.add(event_id)
            rows.append(value)
    return rows, identities


def acquire_single_writer(registry: Path):
    """Hold a non-blocking process lock for one complete registry pass."""
    if fcntl is None:
        raise CaptureRegistryError("single-writer locking is unavailable")
    lock_path = registry.with_suffix(registry.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        return None
    return handle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--recorder-source", required=True)
    parser.add_argument("--activation-utc", required=True)
    args = parser.parse_args()

    registry = Path(args.registry).resolve()
    writer_lock = acquire_single_writer(registry)
    if writer_lock is None:
        print(compact({
            "schema_version": VERSION + "-state",
            "status": "SKIP_ALREADY_RUNNING",
            "trading_access": 0,
        }))
        return 0
    state_path = Path(args.state).resolve()
    policy_path = Path(args.policy).resolve()
    recorder_source = Path(args.recorder_source).resolve()
    if not policy_path.is_file() or not recorder_source.is_file():
        raise CaptureRegistryError("policy or recorder source is absent")
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if policy.get("touch_law") != "DECISION_RELEVANT_CONSUMPTION_ONLY":
        raise CaptureRegistryError("capture policy touch law is not bound")
    source_sha = hashlib.sha256(recorder_source.read_bytes()).hexdigest()
    now = dt.datetime.now(dt.timezone.utc)
    discovered = discover(now)
    existing, identities = load_registry(registry)
    new_rows = []
    for event in discovered:
        if event["event_id"] in identities:
            continue
        new_rows.append({
            **event,
            "schema_version": VERSION,
            "first_tagged_utc": now.isoformat().replace("+00:00", "Z"),
            "activation_utc": args.activation_utc,
            "tag": "HOLDOUT_ELIGIBLE_CAPTURE_ONLY",
            "touch_status_at_capture": "UNTOUCHED",
            "capture_source": "ws_depth_recorder_raw_exchange_frames",
            "recorder_source_sha256": source_sha,
            "identity_receipt_sha256": digest(event),
            "pipeline_exclusion": (
                "NO_EVALUATION_REPLAY_DIAGNOSTIC_OR_FIX_MOTIVATING_CITATION"
            ),
        })
    if new_rows:
        registry.parent.mkdir(parents=True, exist_ok=True)
        with registry.open("a", encoding="utf-8", newline="\n") as handle:
            for row in new_rows:
                handle.write(compact(row) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    all_rows, all_identities = load_registry(registry)
    state = {
        "schema_version": VERSION + "-state",
        "status": "PASS",
        "checked_utc": now.isoformat().replace("+00:00", "Z"),
        "activation_utc": args.activation_utc,
        "discovered_this_pass": len(discovered),
        "newly_tagged_this_pass": len(new_rows),
        "registry_events": len(all_rows),
        "unique_registry_events": len(all_identities),
        "registry_sha256": hashlib.sha256(registry.read_bytes()).hexdigest(),
        "recorder_source_sha256": source_sha,
        "decision_relevant_consumption": 0,
        "trading_access": 0,
    }
    atomic_json(state_path, state)
    print(compact(state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
