#!/usr/bin/env python3
"""Export final public milestone/start evidence for the immutable Window-1 D.

Raw responses remain outside Git.  The normalized output contains public
event/status/time facts only.  Every event-filtered query follows cursors,
retries rate limits, and retains a per-event immutable raw receipt.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
import os
import random
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


HOST = "https://api.elections.kalshi.com"
ENDPOINT = "/trade-api/v2/milestones"
D = 804
UTC = dt.timezone.utc


class MilestoneExportError(RuntimeError):
    pass


def iso_now() -> str:
    return dt.datetime.now(UTC).isoformat()


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def event_ids(path: Path) -> list[str]:
    values = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                values.append(str(row.get("event_id") or ""))
    if len(values) != D or len(set(values)) != D or any(not x for x in values):
        raise MilestoneExportError(
            f"immutable event contract changed: rows={len(values)} "
            f"unique={len(set(values))}"
        )
    return sorted(values)


def request_json(
    params: dict[str, str],
    *,
    attempts: int,
    timeout: float,
) -> dict[str, Any]:
    url = HOST + ENDPOINT + "?" + urllib.parse.urlencode(params)
    for attempt in range(attempts):
        request = urllib.request.Request(
            url, headers={"User-Agent": "omi-window1-start-audit/1"}
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise MilestoneExportError(
                        f"unexpected HTTP {response.status}"
                    )
                value = json.load(response)
                if not isinstance(value, dict):
                    raise MilestoneExportError("non-object milestone response")
                return value
        except urllib.error.HTTPError as exc:
            if exc.code != 429 and exc.code < 500:
                raise
            retry = exc.headers.get("Retry-After")
            delay = (
                float(retry) if retry
                else min(20.0, 0.5 * (2 ** attempt))
            )
        except (urllib.error.URLError, TimeoutError):
            delay = min(20.0, 0.5 * (2 ** attempt))
        if attempt + 1 >= attempts:
            raise MilestoneExportError(
                f"request exhausted after {attempts} attempts"
            )
        time.sleep(delay + random.random() * 0.2)
    raise AssertionError("unreachable")


def validate_raw(path: Path, event_id: str) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if (
        not isinstance(value, dict)
        or value.get("request_event_id") != event_id
        or not isinstance(value.get("pages"), list)
        or not value["pages"]
        or value.get("terminal_cursor") not in ("", None)
    ):
        raise MilestoneExportError(f"invalid resumed raw receipt: {event_id}")
    return value


def fetch_event(
    event_id: str,
    raw_dir: Path,
    *,
    limit: int,
    attempts: int,
    timeout: float,
    resume: bool,
) -> dict[str, Any]:
    path = raw_dir / f"{event_id}.json.gz"
    if resume and path.is_file():
        receipt = validate_raw(path, event_id)
        return {
            "event_id": event_id,
            "path": path,
            "receipt": receipt,
            "resumed": True,
        }
    pages = []
    cursor = ""
    seen = set()
    while True:
        params = {
            "related_event_ticker": event_id,
            "limit": str(limit),
        }
        if cursor:
            params["cursor"] = cursor
        response = request_json(
            params, attempts=attempts, timeout=timeout
        )
        milestones = response.get("milestones")
        if not isinstance(milestones, list):
            raise MilestoneExportError(
                f"{event_id} response lacks milestones[]"
            )
        next_cursor = str(response.get("cursor") or "")
        pages.append({
            "request": {
                "related_event_ticker": event_id,
                "limit": limit,
                "cursor_present": bool(cursor),
            },
            "response": response,
        })
        if not next_cursor:
            cursor = ""
            break
        if next_cursor in seen:
            raise MilestoneExportError(f"{event_id} cursor loop")
        seen.add(next_cursor)
        cursor = next_cursor
    receipt = {
        "schema_version": "window1-public-milestone-raw-v1",
        "request_event_id": event_id,
        "endpoint": ENDPOINT,
        "host": HOST,
        "fetched_utc": iso_now(),
        "pages": pages,
        "terminal_cursor": cursor,
    }
    with gzip.open(path, "wt", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    return {
        "event_id": event_id,
        "path": path,
        "receipt": receipt,
        "resumed": False,
    }


def normalized_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    event_id = result["event_id"]
    fetched = result["receipt"]["fetched_utc"]
    output = []
    seen = set()
    for page_index, page in enumerate(result["receipt"]["pages"], 1):
        for row_index, row in enumerate(
            page["response"].get("milestones") or [], 1
        ):
            if not isinstance(row, dict):
                raise MilestoneExportError(
                    f"{event_id} contains a non-object milestone"
                )
            details = row.get("details") or {}
            if not isinstance(details, dict):
                details = {}
            source_identity = str(
                row.get("source_id")
                or (row.get("source_ids") or {}).get("source_3_id")
                or ""
            )
            identity = str(row.get("id") or "")
            canonical = (
                identity, str(details.get("status") or ""),
                str(row.get("start_date") or ""),
                str(row.get("last_updated_ts") or ""),
            )
            if canonical in seen:
                continue
            seen.add(canonical)
            output.append({
                "schema_version": "window1-public-milestone-v1",
                "event_id": event_id,
                "status": details.get("status"),
                "start_utc": row.get("start_date"),
                "last_updated_utc": row.get("last_updated_ts"),
                "exported_utc": fetched,
                "milestone_identity_sha256": (
                    hashlib.sha256(identity.encode()).hexdigest()
                    if identity else None
                ),
                "source_identity_sha256": (
                    hashlib.sha256(source_identity.encode()).hexdigest()
                    if source_identity else None
                ),
                "raw_page": page_index,
                "raw_row": row_index,
            })
    return output


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> int:
    started = iso_now()
    ids = event_ids(Path(args.events).resolve())
    raw_dir = Path(args.raw_dir).resolve()
    normalized = Path(args.normalized_output).resolve()
    manifest_path = Path(args.manifest_output).resolve()
    raw_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(raw_dir, stat.S_IRWXU)
    results = []
    failures = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.workers
    ) as executor:
        futures = {
            executor.submit(
                fetch_event, event_id, raw_dir,
                limit=args.limit,
                attempts=args.attempts,
                timeout=args.timeout,
                resume=args.resume,
            ): event_id
            for event_id in ids
        }
        for index, future in enumerate(
            concurrent.futures.as_completed(futures), 1
        ):
            event_id = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                failures.append({
                    "event_id": event_id,
                    "error": str(exc),
                })
            if index % 50 == 0 or index == len(ids):
                print(
                    f"milestones={index}/{len(ids)} "
                    f"failures={len(failures)}",
                    flush=True,
                )
    if failures:
        write_json(
            manifest_path.with_name(
                manifest_path.stem + ".failures.json"
            ),
            {"failures": failures, "started_utc": started},
        )
        raise MilestoneExportError(
            f"incomplete milestone export: {len(failures)} failures"
        )
    all_rows = []
    for result in sorted(results, key=lambda row: row["event_id"]):
        all_rows.extend(normalized_rows(result))
    normalized.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(normalized.parent, stat.S_IRWXU)
    with normalized.open("w", encoding="utf-8", newline="\n") as handle:
        for row in all_rows:
            handle.write(compact(row) + "\n")
    os.chmod(normalized, stat.S_IRUSR | stat.S_IWUSR)
    raw_hash_lines = [
        f"{result['event_id']} {sha256_file(result['path'])}"
        for result in sorted(results, key=lambda row: row["event_id"])
    ]
    status_counts = Counter(
        str(row.get("status") or "<missing>") for row in all_rows
    )
    manifest = {
        "schema_version": "window1-public-milestone-manifest-v1",
        "started_utc": started,
        "completed_utc": iso_now(),
        "scope": {
            "D": D,
            "event_queries": len(results),
            "host": HOST,
            "endpoint": ENDPOINT,
            "filter": "related_event_ticker exact event id",
        },
        "pagination": {
            "page_count": sum(
                len(row["receipt"]["pages"]) for row in results
            ),
            "all_terminal_cursors_empty": all(
                row["receipt"]["terminal_cursor"] in ("", None)
                for row in results
            ),
            "failed_event_count": 0,
            "resumed_event_count": sum(row["resumed"] for row in results),
            "new_event_count": sum(not row["resumed"] for row in results),
        },
        "coverage": {
            "normalized_rows": len(all_rows),
            "events_with_rows": len({
                row["event_id"] for row in all_rows
            }),
            "events_with_zero_rows": sorted(
                set(ids) - {row["event_id"] for row in all_rows}
            ),
            "status_counts": dict(status_counts),
            "final_P_rows": sum(
                row.get("status") == "P" for row in all_rows
            ),
        },
        "artifacts": {
            "normalized_sha256": sha256_file(normalized),
            "normalized_bytes": normalized.stat().st_size,
            "raw_file_count": len(results),
            "raw_hash_set_sha256": hashlib.sha256(
                ("\n".join(raw_hash_lines) + "\n").encode()
            ).hexdigest(),
        },
        "privacy": {
            "credentials_used": False,
            "account_data_present": False,
            "raw_outside_git": True,
        },
    }
    write_json(manifest_path, manifest)
    print(json.dumps({
        "D": D,
        "rows": len(all_rows),
        "events_with_rows": manifest["coverage"]["events_with_rows"],
        "status_counts": dict(status_counts),
        "manifest": str(manifest_path),
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--events", required=True)
    result.add_argument("--raw-dir", required=True)
    result.add_argument("--normalized-output", required=True)
    result.add_argument("--manifest-output", required=True)
    result.add_argument("--workers", type=int, default=4)
    result.add_argument("--limit", type=int, default=100)
    result.add_argument("--attempts", type=int, default=6)
    result.add_argument("--timeout", type=float, default=20.0)
    result.add_argument("--resume", action="store_true")
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
