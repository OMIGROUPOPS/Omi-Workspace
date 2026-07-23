#!/usr/bin/env python3
"""Read-only live/historical order-tier reconciliation for Window 1.

The `select` command is offline and builds a stratified owner-only sample from
the frozen 703 targets, byte-pinned engine logs, and confirmed exchange
controls.  The `query-sample` command performs authenticated GET requests only:
cutoff, live order/fill, and historical order/fill endpoints.  Raw responses
and identities remain in an owner-only private directory; sanitized receipts
contain no order, client-order, fill, trade, or account identities.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import time
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlencode


SCHEMA = "window1-live-historical-tier-v1"
EXPECTED_TARGETS = 703
EXPECTED_IMMEDIATE_FILLS = 1
EXPECTED_SUCCESSFUL_CANCELS = 671
EXPECTED_CANCEL_FAILURES = 4
RETRYABLE = {429, 500, 502, 503, 504}
METHOD = "GET"
TERMINAL = {"canceled", "executed", "expired", "rejected"}


class TierError(RuntimeError):
    """A violated reconciliation or evidence invariant."""


def present(value: Any) -> bool:
    return value not in (None, "")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TierError(f"{path.name}: expected object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                value = json.loads(line)
            except ValueError as exc:
                raise TierError(
                    f"{path.name}:{line_number}: malformed JSON") from exc
            if not isinstance(value, dict):
                raise TierError(
                    f"{path.name}:{line_number}: expected object")
            rows.append(value)
    return rows


def write_json(path: Path, value: Mapping[str, Any], mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(value), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.chmod(temporary, mode)
    os.replace(temporary, path)
    os.chmod(path, mode)


def write_jsonl(
    path: Path, rows: Iterable[Mapping[str, Any]], mode: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(
                dict(row), sort_keys=True, separators=(",", ":")) + "\n")
    os.chmod(temporary, mode)
    os.replace(temporary, path)
    os.chmod(path, mode)


def sha256_file(path: Path, byte_limit: int | None = None) -> str:
    digest = hashlib.sha256()
    remaining = byte_limit
    with path.open("rb") as handle:
        while True:
            size = 1024 * 1024
            if remaining is not None:
                if remaining <= 0:
                    break
                size = min(size, remaining)
            chunk = handle.read(size)
            if not chunk:
                break
            digest.update(chunk)
            if remaining is not None:
                remaining -= len(chunk)
    if remaining not in (None, 0):
        raise TierError(f"{path.name}: shorter than byte pin")
    return digest.hexdigest()


def parse_ts(value: Any) -> float:
    if not present(value):
        raise TierError("timestamp missing")
    if isinstance(value, (int, float)):
        number = float(value)
        return number / 1000 if number > 10_000_000_000 else number
    text = str(value).strip()
    try:
        number = float(text)
    except ValueError:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise TierError("timezone-naive timestamp")
        return parsed.timestamp()
    return number / 1000 if number > 10_000_000_000 else number


def iso_utc(value: float) -> str:
    return dt.datetime.fromtimestamp(
        value, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def event_from_ticker(ticker: str) -> str:
    return ticker.rsplit("-", 1)[0] if "-" in ticker else ""


def iter_log_lines(
    log_dir: Path, active_prefix_bytes: int,
) -> Iterable[tuple[str, bytes]]:
    immutable = sorted(log_dir.glob("live_v3_2026071[2-9]*.jsonl.gz"))
    if not immutable:
        raise TierError("immutable log set is empty")
    for path in immutable:
        with gzip.open(path, "rb") as handle:
            for line in handle:
                yield path.name, line
    active = log_dir / "live_v3_20260720.jsonl"
    with active.open("rb") as handle:
        while handle.tell() < active_prefix_bytes:
            line = handle.readline()
            if not line or handle.tell() > active_prefix_bytes:
                break
            yield active.name, line


def target_orders(
    source_orders: Sequence[Mapping[str, Any]],
    mismatches: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    target_rows = [
        row for row in mismatches
        if row.get("mismatch_type") == "accepted_order_missing_receipt"
    ]
    if len(target_rows) != EXPECTED_TARGETS:
        raise TierError(
            f"target mismatches={len(target_rows)}, expected 703")
    by_id = {
        str(row.get("order_id")): dict(row)
        for row in source_orders if present(row.get("order_id"))
    }
    result = []
    seen = set()
    for mismatch in target_rows:
        order_id = str(mismatch.get("order_id") or "")
        if not order_id or order_id in seen:
            raise TierError("target order identity absent or duplicated")
        source = by_id.get(order_id)
        if source is None:
            raise TierError("target identity absent from source orders")
        seen.add(order_id)
        result.append(source)
    result.sort(key=lambda row: (
        str(row.get("event_id") or ""),
        str(row.get("ticker") or ""),
        parse_ts(row.get("local_logged_ts")),
        str(row.get("order_id") or ""),
    ))
    return result


def load_target_log_evidence(
    log_dir: Path,
    active_prefix_bytes: int,
    target_ids: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    evidence = {
        order_id: {
            "placements": [],
            "cancellations": [],
            "orphan_readoptions": [],
        }
        for order_id in target_ids
    }
    physical_rows = 0
    selected_rows = 0
    parse_errors = 0
    placement_fields = Counter()
    cancellation_fields = Counter()
    raw_post_body_rows = 0
    raw_cancel_body_rows = 0
    raw_post_markers = {
        "order", "response", "response_body", "fill_count",
        "fill_count_fp", "remaining_count", "remaining_count_fp",
        "initial_count", "initial_count_fp", "created_time", "ts_ms",
        "_error", "_status",
    }
    raw_cancel_markers = {
        "order", "response", "response_body", "reduced_by",
        "reduced_by_fp", "count", "count_fp", "client_order_id",
        "created_time", "ts_ms", "_error", "_status",
    }
    for file_name, line in iter_log_lines(log_dir, active_prefix_bytes):
        physical_rows += 1
        if not any(marker in line for marker in (
                b'"order_placed"', b'"order_cancelled"',
                b'"orphan_readopted_fingerprint"')):
            continue
        try:
            row = json.loads(line)
        except ValueError:
            parse_errors += 1
            continue
        event_type = str(row.get("event") or "")
        details = row.get("details")
        if not isinstance(details, dict):
            continue
        order_id = str(details.get("order_id") or "")
        if order_id not in target_ids:
            continue
        selected_rows += 1
        base = {
            "event_type": event_type,
            "ticker": row.get("ticker"),
            "local_logged_ts": row.get("ts_epoch"),
            "source_file_class": (
                "active_byte_pinned"
                if file_name.endswith(".jsonl")
                else "immutable_gzip"
            ),
            "details": details,
        }
        if event_type == "order_placed":
            evidence[order_id]["placements"].append(base)
            placement_fields.update(details.keys())
            if raw_post_markers.intersection(details):
                raw_post_body_rows += 1
        elif event_type == "order_cancelled":
            evidence[order_id]["cancellations"].append(base)
            cancellation_fields.update(details.keys())
            if raw_cancel_markers.intersection(details) - {
                    "client_order_id", "count"}:
                raw_cancel_body_rows += 1
        elif event_type == "orphan_readopted_fingerprint":
            evidence[order_id]["orphan_readoptions"].append(base)
    audit = {
        "physical_log_rows_scanned": physical_rows,
        "selected_target_lifecycle_rows": selected_rows,
        "selected_parse_errors": parse_errors,
        "placement_detail_fields": dict(sorted(placement_fields.items())),
        "cancellation_detail_fields": dict(sorted(
            cancellation_fields.items())),
        "raw_post_response_body_rows": raw_post_body_rows,
        "raw_cancel_response_body_rows": raw_cancel_body_rows,
        "producer_contract": {
            "post": (
                "successful response JSON was parsed in memory; order_placed "
                "persisted selected identity/state fields, not the raw body"),
            "cancel": (
                "DELETE reduced every response to Boolean success before "
                "order_cancelled logging; status/body were not persisted"),
        },
    }
    return evidence, audit


def spread(rows: Sequence[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    if len(rows) <= count:
        return list(rows)
    if count == 1:
        return [rows[0]]
    indices = [
        round(index * (len(rows) - 1) / (count - 1))
        for index in range(count)
    ]
    return [rows[index] for index in sorted(set(indices))]


def strata_for(
    source: Mapping[str, Any], evidence: Mapping[str, Any],
) -> list[str]:
    strata = []
    placements = evidence["placements"]
    cancellations = evidence["cancellations"]
    has_cancel_success = any(
        row["details"].get("success") is True for row in cancellations)
    has_cancel_failure = any(
        row["details"].get("success") is False for row in cancellations)
    if any(str(
            row["details"].get("response_status") or "").lower() == "filled"
           for row in placements):
        strata.append("immediate_fill")
    if has_cancel_success:
        strata.append("successful_cancel")
    if has_cancel_failure:
        strata.append("cancel_failure_attempt")
    if has_cancel_failure and not has_cancel_success:
        strata.append("cancel_failure")
    if not cancellations:
        strata.append("never_cancelled")
    if evidence["orphan_readoptions"]:
        strata.append("orphan_readopted")
    if not strata:
        strata.append("other")
    return sorted(strata)


def sample_id(index: int, is_control: bool) -> str:
    prefix = "control" if is_control else "target"
    return f"{prefix}-{index:03d}"


def select_sample(args: argparse.Namespace) -> int:
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.chmod(output, 0o700)
    source_orders_path = Path(args.source_orders).resolve()
    mismatches_path = Path(args.source_mismatches).resolve()
    api_orders_path = Path(args.existing_api_orders).resolve()
    source_orders = read_jsonl(source_orders_path)
    mismatches = read_jsonl(mismatches_path)
    existing_api_orders = read_jsonl(api_orders_path)
    targets = target_orders(source_orders, mismatches)
    target_ids = {str(row["order_id"]) for row in targets}
    evidence, source_audit = load_target_log_evidence(
        Path(args.log_dir).resolve(),
        args.active_log_prefix_bytes,
        target_ids,
    )

    enriched = []
    for source in targets:
        order_id = str(source["order_id"])
        strata = strata_for(source, evidence[order_id])
        enriched.append({
            "source_order": source,
            "log_evidence": evidence[order_id],
            "strata": strata,
        })
    immediate = [row for row in enriched
                 if "immediate_fill" in row["strata"]]
    successful = [row for row in enriched
                  if "successful_cancel" in row["strata"]]
    failures = [row for row in enriched
                if "cancel_failure" in row["strata"]]
    never = [row for row in enriched
             if "never_cancelled" in row["strata"]]
    orphan = [row for row in enriched
              if "orphan_readopted" in row["strata"]
              and "successful_cancel" in row["strata"]]
    if len(immediate) != EXPECTED_IMMEDIATE_FILLS:
        raise TierError(f"immediate fills={len(immediate)}, expected 1")
    if len(successful) != EXPECTED_SUCCESSFUL_CANCELS:
        raise TierError(
            f"successful cancels={len(successful)}, expected 671")
    if len(failures) != EXPECTED_CANCEL_FAILURES:
        raise TierError(f"cancel failures={len(failures)}, expected 4")

    selected_targets: dict[str, dict[str, Any]] = {}

    def add(rows: Sequence[dict[str, Any]]) -> None:
        for row in rows:
            selected_targets[str(row["source_order"]["order_id"])] = row

    add(immediate)
    add(failures)
    add(spread(orphan, min(4, len(orphan))))
    normal = [
        row for row in successful
        if "orphan_readopted" not in row["strata"]
        and "cancel_failure_attempt" not in row["strata"]
    ]
    add(spread(normal, 6))
    recovered_cancel_failures = [
        row for row in successful
        if "cancel_failure_attempt" in row["strata"]]
    add(spread(recovered_cancel_failures, 2))
    plain_never = [
        row for row in never if "immediate_fill" not in row["strata"]]
    add(spread(plain_never, 6))
    target_sample = sorted(
        selected_targets.values(),
        key=lambda row: (
            str(row["source_order"].get("event_id") or ""),
            str(row["source_order"].get("ticker") or ""),
            parse_ts(row["source_order"].get("local_logged_ts")),
        ),
    )

    api_ids = {
        str(row.get("order_id") or "") for row in existing_api_orders}
    target_events = {
        str(row["source_order"].get("event_id") or "")
        for row in target_sample
    }
    controls = [
        dict(row) for row in source_orders
        if str(row.get("event_id") or "") in target_events
        and str(row.get("order_id") or "") in api_ids
        and str(row.get("order_id") or "") not in target_ids
        and present(row.get("client_order_id"))
        and str(row.get("exchange_status") or "").lower() in TERMINAL
    ]
    controls.sort(key=lambda row: (
        str(row.get("event_id") or ""),
        str(row.get("ticker") or ""),
        parse_ts(
            row.get("exchange_created_ts") or row.get("local_logged_ts")),
        str(row.get("order_id") or ""),
    ))
    controls = spread(controls, 6)
    if len(controls) < 4:
        raise TierError("fewer than four confirmed sibling controls")

    private_rows = []
    sanitized_rows = []
    for index, row in enumerate(target_sample, 1):
        source = row["source_order"]
        private_rows.append({
            "schema_version": SCHEMA,
            "sample_id": sample_id(index, False),
            "is_target": True,
            "strata": row["strata"],
            "order_id": source.get("order_id"),
            "client_order_id": source.get("client_order_id"),
            "internal_trade_id": source.get("trade_id"),
            "event_id": source.get("event_id"),
            "ticker": source.get("ticker"),
            "side": next((
                receipt["details"].get("side")
                for receipt in row["log_evidence"]["placements"]
                if present(receipt["details"].get("side"))
            ), None),
            "action": source.get("action"),
            "price_cents": source.get("price_cents"),
            "quantity": source.get("quantity"),
            "local_logged_ts": source.get("local_logged_ts"),
            "placement_receipts": row["log_evidence"]["placements"],
            "cancellation_receipts": row["log_evidence"]["cancellations"],
            "orphan_readoption_receipts":
                row["log_evidence"]["orphan_readoptions"],
            "raw_post_201_body_proof": False,
            "raw_cancel_body_proof": False,
            "normalized_successful_placement_receipt": bool(
                row["log_evidence"]["placements"]),
        })
    for index, source in enumerate(controls, 1):
        private_rows.append({
            "schema_version": SCHEMA,
            "sample_id": sample_id(index, True),
            "is_target": False,
            "strata": ["confirmed_sibling_control"],
            "order_id": source.get("order_id"),
            "client_order_id": source.get("client_order_id"),
            "internal_trade_id": source.get("trade_id"),
            "event_id": source.get("event_id"),
            "ticker": source.get("ticker"),
            "side": source.get("side"),
            "action": source.get("action"),
            "price_cents": source.get("price_cents"),
            "quantity": source.get("quantity"),
            "local_logged_ts": source.get("local_logged_ts"),
            "placement_receipts": [],
            "cancellation_receipts": [],
            "orphan_readoption_receipts": [],
            "raw_post_201_body_proof": False,
            "raw_cancel_body_proof": False,
            "normalized_successful_placement_receipt": True,
            "prior_exchange_status": source.get("exchange_status"),
        })
    private_rows.sort(key=lambda row: (
        not row["is_target"], row["sample_id"]))
    for row in private_rows:
        sanitized_rows.append({
            "schema_version": SCHEMA,
            "sample_id": row["sample_id"],
            "is_target": row["is_target"],
            "strata": row["strata"],
            "event_id": row["event_id"],
            "ticker": row["ticker"],
            "identifier_presence": {
                "order_id": present(row.get("order_id")),
                "client_order_id": present(row.get("client_order_id")),
                "internal_trade_id": present(row.get("internal_trade_id")),
            },
            "raw_post_201_body_proof": row["raw_post_201_body_proof"],
            "raw_cancel_body_proof": row["raw_cancel_body_proof"],
            "normalized_successful_placement_receipt":
                row["normalized_successful_placement_receipt"],
            "private_identifiers_emitted": False,
        })
    private_path = output / "TIER_SAMPLE.private.jsonl"
    sanitized_path = output / "TIER_SAMPLE.sanitized.jsonl"
    write_jsonl(private_path, private_rows, mode=0o400)
    write_jsonl(sanitized_path, sanitized_rows, mode=0o600)
    strata_counts = Counter(
        stratum for row in enriched for stratum in row["strata"])
    summary = {
        "schema_version": SCHEMA,
        "D": 804,
        "target_population": EXPECTED_TARGETS,
        "population_strata": dict(sorted(strata_counts.items())),
        "sample_target_rows": len(target_sample),
        "sample_control_rows": len(controls),
        "sample_total_rows": len(private_rows),
        "selected_target_strata": dict(sorted(Counter(
            stratum for row in target_sample for stratum in row["strata"]
        ).items())),
        "raw_source_preservation": source_audit,
        "private_sample_sha256": sha256_file(private_path),
        "sanitized_sample_sha256": sha256_file(sanitized_path),
        "private_identifiers_emitted": False,
        "strategy_scoring_permitted": False,
        "input_hashes": {
            "source_orders": sha256_file(source_orders_path),
            "source_mismatches": sha256_file(mismatches_path),
            "existing_api_orders": sha256_file(api_orders_path),
        },
    }
    write_json(
        output / "TIER_SAMPLE_SELECTION.sanitized.json",
        summary,
        mode=0o600,
    )
    print(json.dumps({
        "D": 804,
        "targets": EXPECTED_TARGETS,
        "successful_cancels": len(successful),
        "cancel_failures": len(failures),
        "never_cancelled": len(never),
        "immediate_fills": len(immediate),
        "orphan_readopted_successes": len(orphan),
        "sample_targets": len(target_sample),
        "sample_controls": len(controls),
        "private_identifiers_printed": False,
    }, sort_keys=True))
    return 0


def query_path(base: str, params: Mapping[str, Any]) -> str:
    if not base.startswith("/trade-api/v2/"):
        raise TierError("query outside trade-api v2")
    clean = {
        key: value for key, value in params.items()
        if value not in (None, "")
    }
    return base + ("?" + urlencode(clean) if clean else "")


class RawWriter:
    def __init__(self, path: Path):
        self.path = path
        self.temporary = path.with_suffix(path.suffix + ".tmp")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.temporary.open(
            "w", encoding="utf-8", newline="\n")
        os.chmod(self.temporary, 0o600)

    def append(self, value: Mapping[str, Any]) -> None:
        self.handle.write(json.dumps(
            dict(value), sort_keys=True, separators=(",", ":")) + "\n")
        self.handle.flush()
        os.fsync(self.handle.fileno())

    def close(self) -> None:
        self.handle.close()
        os.replace(self.temporary, self.path)
        os.chmod(self.path, 0o400)


class ReadOnlyClient:
    def __init__(
        self, base_url: str, private_key: Any, headers_fn: Any,
        writer: RawWriter, min_interval: float,
    ):
        import requests
        self.session = requests.Session()
        self.base_url = base_url.rstrip("/")
        self.private_key = private_key
        self.headers_fn = headers_fn
        self.writer = writer
        self.min_interval = min_interval
        self.last_request = 0.0
        self.requests = 0
        self.retries = 0
        self.rate_limits = 0
        self.errors = 0
        self.pagination_queries = 0
        self.pagination_completed = 0
        self.cursor_cycles = 0
        self.status_counts = Counter()

    def get(
        self, path: str, label: str, allow_404: bool = False,
    ) -> tuple[int, dict[str, Any]]:
        if not path.startswith("/trade-api/v2/"):
            raise TierError("refused non-v2 path")
        for attempt in range(9):
            delay = self.min_interval - (
                time.monotonic() - self.last_request)
            if delay > 0:
                time.sleep(delay)
            headers = self.headers_fn(self.private_key, METHOD, path)
            try:
                response = self.session.get(
                    self.base_url + path, headers=headers, timeout=45)
            except Exception as exc:
                self.errors += 1
                if attempt == 8:
                    raise TierError(
                        f"{label}: network retries exhausted") from exc
                self.retries += 1
                time.sleep(min(30.0, 0.5 * (2 ** attempt)))
                continue
            finally:
                self.last_request = time.monotonic()
            self.requests += 1
            status = int(response.status_code)
            self.status_counts[str(status)] += 1
            try:
                body = response.json()
            except ValueError:
                body = {"non_json_body": response.text[:2000]}
            if not isinstance(body, dict):
                body = {"unexpected_body": body}
            self.writer.append({
                "schema_version": SCHEMA,
                "method": METHOD,
                "path": path,
                "label": label,
                "http_status": status,
                "retry_attempt": attempt,
                "received_utc": iso_utc(time.time()),
                "response": body,
            })
            if status in RETRYABLE:
                self.retries += 1
                if status == 429:
                    self.rate_limits += 1
                if attempt == 8:
                    raise TierError(f"{label}: HTTP retries exhausted")
                wait = response.headers.get("Retry-After")
                time.sleep(
                    max(0.2, float(wait) if wait else min(
                        30.0, 0.5 * (2 ** attempt))))
                continue
            if status == 404 and allow_404:
                return status, body
            if status != 200:
                self.errors += 1
                raise TierError(f"{label}: unexpected HTTP {status}")
            return status, body
        raise TierError("unreachable retry state")

    def paged(
        self, base: str, params: Mapping[str, Any], key: str, label: str,
        allow_404_empty: bool = False,
    ) -> list[dict[str, Any]]:
        self.pagination_queries += 1
        cursor = ""
        seen = set()
        rows = []
        page = 0
        while True:
            page += 1
            actual = dict(params)
            if cursor:
                actual["cursor"] = cursor
            status, body = self.get(
                query_path(base, actual),
                f"{label}:page-{page:04d}",
                allow_404=allow_404_empty,
            )
            if status == 404 and allow_404_empty:
                self.pagination_completed += 1
                break
            values = body.get(key)
            if not isinstance(values, list) or "cursor" not in body:
                raise TierError(f"{label}: invalid paginated response")
            rows.extend(
                dict(value) for value in values
                if isinstance(value, dict))
            next_cursor = str(body.get("cursor") or "")
            if not next_cursor:
                self.pagination_completed += 1
                break
            if next_cursor in seen:
                self.cursor_cycles += 1
                raise TierError(f"{label}: cursor cycle")
            seen.add(next_cursor)
            cursor = next_cursor
        return rows

    def proof(self) -> dict[str, Any]:
        complete = (
            self.pagination_queries == self.pagination_completed
            and self.cursor_cycles == 0 and self.errors == 0
        )
        return {
            "methods": ["GET"],
            "http_requests": self.requests,
            "retry_attempts": self.retries,
            "rate_limit_responses": self.rate_limits,
            "request_errors": self.errors,
            "http_status_counts": dict(sorted(self.status_counts.items())),
            "pagination_queries": self.pagination_queries,
            "pagination_completed_empty_cursor":
                self.pagination_completed,
            "cursor_cycles": self.cursor_cycles,
            "complete": complete,
        }


def load_auth(module_dir: Path) -> tuple[Any, Any, str]:
    module_path = module_dir / "kalshi_reconciler.py"
    spec = importlib.util.spec_from_file_location(
        "tier_private_auth", module_path)
    if spec is None or spec.loader is None:
        raise TierError("cannot load established auth module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    load_key = getattr(module, "_load_private_key")
    headers = getattr(module, "_headers")
    base_url = str(getattr(module, "KALSHI_BASE_URL"))
    return load_key(), headers, base_url


def dedup(
    rows: Sequence[Mapping[str, Any]], keys: Sequence[str],
) -> tuple[list[dict[str, Any]], int]:
    result = {}
    duplicates = 0
    for source in rows:
        identity = next(
            (str(source.get(key)) for key in keys if present(source.get(key))),
            "",
        )
        if not identity:
            raise TierError("API row lacks stable identity")
        row = dict(source)
        prior = result.get(identity)
        if prior is not None:
            duplicates += 1
            if prior != row:
                raise TierError("conflicting duplicate API identity")
            continue
        result[identity] = row
    return [result[key] for key in sorted(result)], duplicates


def classify_sample(
    sample: Mapping[str, Any],
    live_orders: Sequence[Mapping[str, Any]],
    historical_orders: Sequence[Mapping[str, Any]],
    live_fills: Sequence[Mapping[str, Any]],
    historical_fills: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    order_id = str(sample.get("order_id") or "")
    client_id = str(sample.get("client_order_id") or "")
    live_exact = [
        row for row in live_orders
        if str(row.get("order_id") or "") == order_id]
    history_exact = [
        row for row in historical_orders
        if str(row.get("order_id") or "") == order_id]
    live_client = [
        row for row in live_orders
        if client_id and str(row.get("client_order_id") or "") == client_id]
    history_client = [
        row for row in historical_orders
        if client_id and str(row.get("client_order_id") or "") == client_id]
    if live_exact and history_exact:
        classification = "E_contradictory_or_unknown"
        reason = "exact_order_present_in_both_partitions"
    elif len(live_exact) == 1:
        classification = "A_exchange_created_found_live"
        reason = "exact_order_id_live"
    elif len(history_exact) == 1:
        classification = "B_exchange_created_found_historical"
        reason = "exact_order_id_historical"
    elif live_exact or history_exact:
        classification = "E_contradictory_or_unknown"
        reason = "exact_order_id_collision"
    elif sample.get("raw_post_201_body_proof") is True:
        classification = "C_raw_201_subsequently_unretrievable"
        reason = "raw_post_body_proves_create_but_both_tiers_absent"
    elif sample.get("normalized_successful_placement_receipt") is True:
        classification = "D_log_only_acknowledgement_raw_body_absent"
        reason = "normalized_receipt_only_and_both_tiers_absent"
    else:
        classification = "E_contradictory_or_unknown"
        reason = "no_sufficient_create_proof"
    all_fills = [*live_fills, *historical_fills]
    exact_fills = [
        row for row in all_fills
        if str(row.get("order_id") or "") == order_id]
    return {
        "schema_version": SCHEMA,
        "sample_id": sample["sample_id"],
        "is_target": sample["is_target"],
        "strata": sample["strata"],
        "event_id": sample["event_id"],
        "ticker": sample["ticker"],
        "classification": classification,
        "reason": reason,
        "exact_live_order_count": len(live_exact),
        "exact_historical_order_count": len(history_exact),
        "exact_live_client_count": len(live_client),
        "exact_historical_client_count": len(history_client),
        "exact_fill_count": len(exact_fills),
        "raw_post_201_body_proof":
            sample.get("raw_post_201_body_proof") is True,
        "raw_cancel_body_proof":
            sample.get("raw_cancel_body_proof") is True,
        "private_identifiers_emitted": False,
    }


def query_sample(args: argparse.Namespace) -> int:
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.chmod(output, 0o700)
    sample_path = Path(args.sample).resolve()
    samples = read_jsonl(sample_path)
    if not samples or not any(row.get("is_target") for row in samples):
        raise TierError("sample lacks target rows")
    private_key, headers, base_url = load_auth(
        Path(args.auth_module_dir).resolve())
    raw_path = output / "TIER_QUERY_PAGES.private.jsonl"
    writer = RawWriter(raw_path)
    client = ReadOnlyClient(
        base_url, private_key, headers, writer, args.min_interval)
    started = time.time()
    direct_status = Counter()
    live_orders_raw = []
    historical_orders_raw = []
    live_fills_raw = []
    historical_fills_raw = []
    try:
        _, cutoff = client.get(
            "/trade-api/v2/historical/cutoff",
            "historical-cutoff",
        )
        tickers = sorted({str(row["ticker"]) for row in samples})
        minimum = math.floor(min(
            parse_ts(row["local_logged_ts"]) for row in samples)) - 3600
        maximum = math.ceil(started) + 1
        for ticker_number, ticker in enumerate(tickers, 1):
            base_label = f"ticker-{ticker_number:03d}"
            live_orders_raw.extend(client.paged(
                "/trade-api/v2/portfolio/orders",
                {"ticker": ticker, "limit": 1000},
                "orders",
                f"live-orders-all-{base_label}",
            ))
            live_orders_raw.extend(client.paged(
                "/trade-api/v2/portfolio/orders",
                {
                    "ticker": ticker, "min_ts": minimum,
                    "max_ts": maximum, "limit": 1000,
                },
                "orders",
                f"live-orders-time-{base_label}",
            ))
            for status in ("resting", "canceled", "executed"):
                live_orders_raw.extend(client.paged(
                    "/trade-api/v2/portfolio/orders",
                    {
                        "ticker": ticker, "status": status,
                        "limit": 1000,
                    },
                    "orders",
                    f"live-orders-status-{status}-{base_label}",
                ))
            live_orders_raw.extend(client.paged(
                "/trade-api/v2/portfolio/orders",
                {"ticker": ticker, "subaccount": 0, "limit": 1000},
                "orders",
                f"live-orders-primary-{base_label}",
            ))
            historical_orders_raw.extend(client.paged(
                "/trade-api/v2/historical/orders",
                {"ticker": ticker, "limit": 1000},
                "orders",
                f"historical-orders-{base_label}",
                allow_404_empty=True,
            ))
            historical_fills_raw.extend(client.paged(
                "/trade-api/v2/historical/fills",
                {"ticker": ticker, "limit": 1000},
                "fills",
                f"historical-fills-{base_label}",
                allow_404_empty=True,
            ))
        for index, sample in enumerate(samples, 1):
            order_id = str(sample["order_id"])
            status, body = client.get(
                f"/trade-api/v2/portfolio/orders/{order_id}",
                f"live-exact-order-{index:03d}",
                allow_404=True,
            )
            direct_status[str(status)] += 1
            if status == 200:
                order = body.get("order")
                if not isinstance(order, dict):
                    raise TierError("exact order response lacks order")
                live_orders_raw.append(order)
            live_fills_raw.extend(client.paged(
                "/trade-api/v2/portfolio/fills",
                {"order_id": order_id, "limit": 1000},
                "fills",
                f"live-fills-order-{index:03d}",
            ))
    finally:
        writer.close()
    proof = client.proof()
    if not proof["complete"]:
        raise TierError("query set is not pagination complete")
    live_orders, live_order_duplicates = dedup(
        live_orders_raw, ("order_id",))
    historical_orders, historical_order_duplicates = dedup(
        historical_orders_raw, ("order_id",))
    live_fills, live_fill_duplicates = dedup(
        live_fills_raw, ("fill_id", "trade_id"))
    historical_fills, historical_fill_duplicates = dedup(
        historical_fills_raw, ("fill_id", "trade_id"))
    for name, rows in (
        ("LIVE_ORDERS.private.jsonl", live_orders),
        ("HISTORICAL_ORDERS.private.jsonl", historical_orders),
        ("LIVE_FILLS.private.jsonl", live_fills),
        ("HISTORICAL_FILLS.private.jsonl", historical_fills),
    ):
        write_jsonl(output / name, rows, mode=0o400)
    results = [
        classify_sample(
            sample, live_orders, historical_orders,
            live_fills, historical_fills,
        )
        for sample in samples
    ]
    private_results = []
    live_by_id = {
        str(row.get("order_id") or ""): row for row in live_orders}
    history_by_id = {
        str(row.get("order_id") or ""): row
        for row in historical_orders}
    fills_by_order: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in [*live_fills, *historical_fills]:
        fills_by_order[str(row.get("order_id") or "")].append(row)
    for sample, result in zip(samples, results):
        order_id = str(sample["order_id"])
        private_results.append({
            "schema_version": SCHEMA,
            "sample": sample,
            "classification": result["classification"],
            "reason": result["reason"],
            "live_order": live_by_id.get(order_id),
            "historical_order": history_by_id.get(order_id),
            "fills": fills_by_order.get(order_id, []),
        })
    private_results_path = output / "TIER_QUERY_RESULTS.private.jsonl"
    sanitized_results_path = (
        output / "TIER_QUERY_RESULTS.sanitized.jsonl")
    write_jsonl(private_results_path, private_results, mode=0o400)
    write_jsonl(sanitized_results_path, results, mode=0o600)
    target_results = [row for row in results if row["is_target"]]
    control_results = [row for row in results if not row["is_target"]]
    target_classes = Counter(
        row["classification"] for row in target_results)
    control_classes = Counter(
        row["classification"] for row in control_results)
    historical_target_recovered = target_classes[
        "B_exchange_created_found_historical"]
    manifest = {
        "schema_version": SCHEMA,
        "D": 804,
        "export_started_utc": iso_utc(started),
        "export_completed_utc": iso_utc(time.time()),
        "api_endpoint": base_url.rstrip("/") + "/trade-api/v2",
        "api_version": "trade-api/v2",
        "methods_used": ["GET"],
        "cutoff": {
            "orders_updated_ts": cutoff.get("orders_updated_ts"),
            "trades_created_ts": cutoff.get("trades_created_ts"),
            "market_settled_ts": cutoff.get("market_settled_ts"),
        },
        "query_time_bounds": {
            "min_ts": minimum,
            "min_utc": iso_utc(minimum),
            "max_ts": maximum,
            "max_utc": iso_utc(maximum),
            "timezone": "UTC",
        },
        "filter_law": {
            "live_orders": (
                "ticker-only all-status/all-subaccount query; bounded-time "
                "query; each documented status; explicit primary-subaccount "
                "control; exact ID query"),
            "historical_orders": (
                "ticker-only because historical orders supports ticker, "
                "max_ts, limit and cursor but no order_id/status/subaccount"),
            "live_fills": "exact order_id, all subaccounts by omission",
            "historical_fills": (
                "ticker-only because historical fills has no order_id "
                "filter; exact order attribution performed after retrieval"),
        },
        "direct_live_order_http_status_counts": dict(sorted(
            direct_status.items())),
        "pagination_proof": proof,
        "deduplicated_records": {
            "live_orders": len(live_orders),
            "historical_orders": len(historical_orders),
            "live_fills": len(live_fills),
            "historical_fills": len(historical_fills),
            "live_order_duplicate_occurrences": live_order_duplicates,
            "historical_order_duplicate_occurrences":
                historical_order_duplicates,
            "live_fill_duplicate_occurrences": live_fill_duplicates,
            "historical_fill_duplicate_occurrences":
                historical_fill_duplicates,
        },
        "sample": {
            "target_rows": len(target_results),
            "control_rows": len(control_results),
            "target_classifications": dict(sorted(target_classes.items())),
            "control_classifications": dict(sorted(control_classes.items())),
            "historical_target_recovered":
                historical_target_recovered,
        },
        "full_export_required": historical_target_recovered > 0,
        "validation_rerun_performed": False,
        "strategy_scoring_permitted": False,
        "private_identifiers_emitted": False,
        "private_file_hashes": {
            "raw_pages": sha256_file(raw_path),
            "live_orders": sha256_file(
                output / "LIVE_ORDERS.private.jsonl"),
            "historical_orders": sha256_file(
                output / "HISTORICAL_ORDERS.private.jsonl"),
            "live_fills": sha256_file(
                output / "LIVE_FILLS.private.jsonl"),
            "historical_fills": sha256_file(
                output / "HISTORICAL_FILLS.private.jsonl"),
            "private_results": sha256_file(private_results_path),
        },
        "sanitized_results_sha256": sha256_file(
            sanitized_results_path),
    }
    write_json(
        output / "TIER_QUERY_MANIFEST.sanitized.json",
        manifest,
        mode=0o600,
    )
    print(json.dumps({
        "D": 804,
        "targets": len(target_results),
        "controls": len(control_results),
        "target_classifications": dict(sorted(target_classes.items())),
        "control_classifications": dict(sorted(control_classes.items())),
        "historical_target_recovered": historical_target_recovered,
        "full_export_required": historical_target_recovered > 0,
        "private_identifiers_printed": False,
    }, sort_keys=True))
    return 10 if historical_target_recovered > 0 else 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    select = commands.add_parser("select")
    select.add_argument("--source-orders", required=True)
    select.add_argument("--source-mismatches", required=True)
    select.add_argument("--existing-api-orders", required=True)
    select.add_argument("--log-dir", required=True)
    select.add_argument("--active-log-prefix-bytes", type=int, required=True)
    select.add_argument("--output-dir", required=True)
    select.set_defaults(func=select_sample)
    query = commands.add_parser("query-sample")
    query.add_argument("--sample", required=True)
    query.add_argument("--auth-module-dir", required=True)
    query.add_argument("--output-dir", required=True)
    query.add_argument("--min-interval", type=float, default=0.15)
    query.set_defaults(func=query_sample)
    return root


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
