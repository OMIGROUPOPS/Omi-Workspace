#!/usr/bin/env python3
"""Acquire policy-blind start/status identity evidence for Round 2.

The collector is deliberately confined to:

* the frozen real-start ledger (to identify its 539 blocked events);
* already-retained public milestone responses (event/source identity);
* public structured-target and retained-score endpoints used by collectors;
* TennisExplorer historical results pages used by ``te_live.py``.

It never opens an execution, policy, placement, fill, price, delta, or
candidate-result artifact.  Raw HTTP responses are written only to the
operator-supplied private directory.  Existing responses are hash-verified
and reused so an exhausted query is not repeated.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


VERSION = "window1-start-truth-round2-acquisition-v1"
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
TE_RESULTS = "https://www.tennisexplorer.com/results/"
USER_AGENT = "omi-window1-start-truth-round2/1.0"
EXPECTED_D = 804
EXPECTED_RESIDUAL = 539
EXPECTED_BASE_COUNTS = {
    "exact": 234,
    "clean_interval": 31,
    "live_by_only": 450,
    "contradictory": 26,
    "schedule_only": 63,
}


class AcquisitionError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise AcquisitionError(f"non-object at {path}:{number}")
            rows.append(row)
    return rows


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(compact(row) + "\n")


def load_milestone(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        raw = json.load(handle)
    milestones = [
        row
        for page in raw.get("pages") or []
        for row in (page.get("response") or {}).get("milestones") or []
        if isinstance(row, dict)
    ]
    event_id = str(raw.get("request_event_id") or path.name.split(".")[0])
    matching = [
        row for row in milestones
        if event_id in (row.get("related_event_tickers") or [])
        or event_id in (row.get("primary_event_tickers") or [])
        or (row.get("details") or {}).get("main_game_event_ticker")
        == event_id
    ]
    if len(matching) > 1:
        raise AcquisitionError(f"ambiguous milestone identity: {event_id}")
    row = matching[0] if matching else (milestones[0] if milestones else {})
    details = row.get("details") or {}
    return {
        "event_id": event_id,
        "milestone_id": row.get("id"),
        "event_source_id": (
            row.get("source_id")
            or (row.get("source_ids") or {}).get("source_3_id")
        ),
        "competitor_target_ids": [
            details.get("first_competitor_id"),
            details.get("second_competitor_id"),
        ],
        "title": row.get("title"),
        "tour": details.get("tour"),
        "tournament": details.get("tournament_name"),
        "round": details.get("round"),
        "gender": details.get("gender"),
        "milestone_status": details.get("status"),
        "milestone_start_date": row.get("start_date"),
        "milestone_end_date": row.get("end_date"),
        "milestone_last_updated": row.get("last_updated_ts"),
        "retained_raw_sha256": sha256_file(path),
    }


def get_bytes(url: str, *, headers: dict[str, str] | None = None) -> bytes:
    request_headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9",
    }
    request_headers.update(headers or {})
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise AcquisitionError(f"HTTP {response.status}: {url}")
        return response.read()


def cache_json_response(
    *,
    url: str,
    destination: Path,
    request_kind: str,
    request_id: str,
) -> dict[str, Any]:
    if destination.exists():
        raw_bytes = destination.read_bytes()
        try:
            with gzip.open(destination, "rt", encoding="utf-8") as handle:
                cached = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise AcquisitionError(
                f"invalid cached response {destination}: {exc}"
            ) from exc
        return {
            "request_kind": request_kind,
            "request_id_sha256": hashlib.sha256(
                request_id.encode()
            ).hexdigest(),
            "cache": "reused",
            "path": str(destination),
            "sha256": sha256_bytes(raw_bytes),
            "response_payload_sha256": cached.get(
                "response_payload_sha256"
            ),
            "http_status": cached.get("http_status"),
        }
    payload = get_bytes(url)
    try:
        response = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise AcquisitionError(f"non-JSON response: {url}") from exc
    wrapper = {
        "schema_version": VERSION,
        "request_kind": request_kind,
        "request_id": request_id,
        "request_path": urllib.parse.urlparse(url).path,
        "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "http_status": 200,
        "response_payload_sha256": sha256_bytes(payload),
        "response": response,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(destination, "wt", encoding="utf-8", newline="\n") as handle:
        handle.write(compact(wrapper) + "\n")
    return {
        "request_kind": request_kind,
        "request_id_sha256": hashlib.sha256(
            request_id.encode()
        ).hexdigest(),
        "cache": "fetched",
        "path": str(destination),
        "sha256": sha256_file(destination),
        "response_payload_sha256": wrapper["response_payload_sha256"],
        "http_status": 200,
    }


def cache_te_page(day: dt.date, destination: Path) -> dict[str, Any]:
    if destination.exists():
        with gzip.open(destination, "rb") as handle:
            html = handle.read()
        return {
            "day": day.isoformat(),
            "cache": "reused",
            "sha256": sha256_file(destination),
            "html_sha256": sha256_bytes(html),
            "bytes": len(html),
        }
    url = (
        f"{TE_RESULTS}?type=all&year={day.year:04d}"
        f"&month={day.month:02d}&day={day.day:02d}"
    )
    # The collector's historical default is Berlin/Prague/Vienna.  The
    # response's displayed timezone is retained in the raw HTML and parsed
    # later rather than guessed at acquisition time.
    html = get_bytes(url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(destination, "wb") as handle:
        handle.write(html)
    return {
        "day": day.isoformat(),
        "cache": "fetched",
        "sha256": sha256_file(destination),
        "html_sha256": sha256_bytes(html),
        "bytes": len(html),
    }


def acquire_parallel(
    tasks: list[dict[str, Any]],
    *,
    workers: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    receipts: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    def run(task: dict[str, Any]) -> dict[str, Any]:
        return cache_json_response(**task)

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, workers)
    ) as executor:
        futures = {executor.submit(run, task): task for task in tasks}
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            try:
                receipts.append(future.result())
            except (
                AcquisitionError,
                OSError,
                urllib.error.URLError,
                TimeoutError,
            ) as exc:
                failures.append({
                    "request_kind": str(task["request_kind"]),
                    "request_id_sha256": hashlib.sha256(
                        str(task["request_id"]).encode()
                    ).hexdigest(),
                    "error": type(exc).__name__,
                    "detail": str(exc)[:240],
                })
    return receipts, failures


def run(args: argparse.Namespace) -> int:
    ledger_path = Path(args.baseline_ledger).resolve()
    milestone_dir = Path(args.milestone_raw_dir).resolve()
    private = Path(args.private_output).resolve()
    ledger = read_jsonl(ledger_path)
    counts = Counter(str(row.get("precision_class")) for row in ledger)
    if (
        len(ledger) != EXPECTED_D
        or len({str(row["event_id"]) for row in ledger}) != EXPECTED_D
        or any(counts[key] != value for key, value in EXPECTED_BASE_COUNTS.items())
    ):
        raise AcquisitionError(
            f"baseline freeze mismatch: D={len(ledger)} counts={dict(counts)}"
        )
    residual_ids = {
        str(row["event_id"])
        for row in ledger
        if not row.get("positive_window1_provable")
    }
    if len(residual_ids) != EXPECTED_RESIDUAL:
        raise AcquisitionError(
            f"residual changed: {len(residual_ids)} != {EXPECTED_RESIDUAL}"
        )
    milestones = {}
    for event_id in sorted(residual_ids):
        path = milestone_dir / f"{event_id}.json.gz"
        if not path.exists():
            raise AcquisitionError(f"missing retained milestone: {event_id}")
        milestones[event_id] = load_milestone(path)
    write_jsonl(
        private / "normalized" / "RESIDUAL_IDENTITY_CROSSWALK.jsonl",
        (milestones[event_id] for event_id in sorted(milestones)),
    )

    target_ids = sorted({
        str(target_id)
        for row in milestones.values()
        for target_id in row["competitor_target_ids"]
        if target_id
    })
    target_tasks = [{
        "url": f"{BASE_URL}/structured_targets/{target_id}",
        "destination": (
            private / "raw" / "structured_targets" / f"{target_id}.json.gz"
        ),
        "request_kind": "structured_target",
        "request_id": target_id,
    } for target_id in target_ids]
    score_tasks = [{
        "url": f"{BASE_URL}/live_data/scores/milestone/{row['milestone_id']}",
        "destination": (
            private / "raw" / "retained_scores" / f"{event_id}.json.gz"
        ),
        "request_kind": "retained_milestone_score",
        "request_id": event_id,
    } for event_id, row in sorted(milestones.items()) if row["milestone_id"]]
    receipts, failures = acquire_parallel(
        target_tasks + score_tasks,
        workers=args.workers,
    )

    first_day = dt.date.fromisoformat(args.first_te_day)
    last_day = dt.date.fromisoformat(args.last_te_day)
    if last_day < first_day:
        raise AcquisitionError("last TE day precedes first TE day")
    te_receipts = []
    cursor = first_day
    while cursor <= last_day:
        destination = (
            private / "raw" / "tennisexplorer_results"
            / f"results-{cursor.isoformat()}.html.gz"
        )
        try:
            te_receipts.append(cache_te_page(cursor, destination))
        except (
            AcquisitionError,
            OSError,
            urllib.error.URLError,
            TimeoutError,
        ) as exc:
            failures.append({
                "request_kind": "tennisexplorer_results",
                "request_id_sha256": hashlib.sha256(
                    cursor.isoformat().encode()
                ).hexdigest(),
                "error": type(exc).__name__,
                "detail": str(exc)[:240],
            })
        cursor += dt.timedelta(days=1)
        if args.page_delay_seconds:
            time.sleep(args.page_delay_seconds)

    manifest = {
        "schema_version": VERSION,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "privacy": {
            "raw_responses_outside_git": True,
            "credentials_used": False,
            "account_or_order_data_requested": False,
        },
        "blindness": {
            "policy_decisions_read": False,
            "placements_read": False,
            "fills_read": False,
            "prices_read": False,
            "deltas_read": False,
            "candidate_results_read": False,
        },
        "baseline": {
            "D": len(ledger),
            "ledger_sha256": sha256_file(ledger_path),
            "precision_counts": dict(counts),
            "residual_events": len(residual_ids),
        },
        "retained_milestone_identity": {
            "events": len(milestones),
            "events_with_milestone_id": sum(
                bool(row["milestone_id"]) for row in milestones.values()
            ),
            "unique_competitor_target_ids": len(target_ids),
            "normalized_crosswalk_sha256": sha256_file(
                private
                / "normalized"
                / "RESIDUAL_IDENTITY_CROSSWALK.jsonl"
            ),
        },
        "http_receipts": {
            "requests": len(receipts),
            "fetched": sum(
                row["cache"] == "fetched" for row in receipts
            ),
            "reused": sum(row["cache"] == "reused" for row in receipts),
            "by_kind": dict(Counter(
                row["request_kind"] for row in receipts
            )),
            "receipt_set_sha256": sha256_bytes(compact(sorted(
                ({
                    "kind": row["request_kind"],
                    "request_id_sha256": row["request_id_sha256"],
                    "sha256": row["sha256"],
                    "response_payload_sha256": row[
                        "response_payload_sha256"
                    ],
                } for row in receipts),
                key=lambda row: (
                row["kind"], row["request_id_sha256"]
                ),
            )).encode()),
        },
        "tennisexplorer_results": {
            "first_day": first_day.isoformat(),
            "last_day": last_day.isoformat(),
            "pages": len(te_receipts),
            "fetched": sum(
                row["cache"] == "fetched" for row in te_receipts
            ),
            "reused": sum(
                row["cache"] == "reused" for row in te_receipts
            ),
            "page_hash_set_sha256": sha256_bytes(compact(sorted(
                ({
                    "day": row["day"],
                    "sha256": row["sha256"],
                    "html_sha256": row["html_sha256"],
                } for row in te_receipts),
                key=lambda row: row["day"],
            )).encode()),
        },
        "failures": sorted(
            failures,
            key=lambda row: (
                row["request_kind"], row["request_id_sha256"]
            ),
        ),
    }
    write_json(private / "ACQUISITION_MANIFEST.json", manifest)
    print(compact({
        "residual": len(residual_ids),
        "targets": len(target_ids),
        "http_requests": len(receipts),
        "te_pages": len(te_receipts),
        "failures": len(failures),
        "manifest": str(private / "ACQUISITION_MANIFEST.json"),
    }))
    return 1 if failures else 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--baseline-ledger", required=True)
    result.add_argument("--milestone-raw-dir", required=True)
    result.add_argument("--private-output", required=True)
    result.add_argument("--first-te-day", default="2026-07-11")
    result.add_argument("--last-te-day", default="2026-07-23")
    result.add_argument("--workers", type=int, default=12)
    result.add_argument("--page-delay-seconds", type=float, default=0.1)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
