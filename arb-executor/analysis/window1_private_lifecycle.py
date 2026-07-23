#!/usr/bin/env python3
"""Read-only private lifecycle export and strict Window-1 validation join.

Raw API responses, exchange identities, and private normalized data must stay
outside Git.  This instrument emits sanitized aggregates and public
event/ticker mismatch rows separately.  It never sends a non-GET request.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlencode


SCHEMA = "window1-private-lifecycle-v1"
EXPECTED_TARGET_SLOTS = 703
TERMINAL_STATUSES = {"canceled", "executed", "expired", "rejected"}
RETRYABLE = {429, 500, 502, 503, 504}
ALLOWED_METHOD = "GET"


class LifecycleError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LifecycleError(f"{path.name}: expected JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                value = json.loads(line)
            except ValueError as exc:
                raise LifecycleError(
                    f"{path.name}:{line_number}: malformed JSON") from exc
            if not isinstance(value, dict):
                raise LifecycleError(
                    f"{path.name}:{line_number}: expected object")
            rows.append(value)
    return rows


def write_json(path: Path, value: Mapping[str, Any], mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(dict(value), indent=2, sort_keys=True) + chr(10),
        encoding="utf-8",
    )
    os.chmod(temporary, mode)
    os.replace(temporary, path)
    os.chmod(path, mode)


def write_jsonl(
    path: Path, rows: Iterable[Mapping[str, Any]], mode: int = 0o600,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline=chr(10)) as handle:
        for row in rows:
            handle.write(json.dumps(
                dict(row), sort_keys=True, separators=(",", ":")))
            handle.write(chr(10))
    os.chmod(temporary, mode)
    os.replace(temporary, path)
    os.chmod(path, mode)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iso_utc(epoch: float | int) -> str:
    return dt.datetime.fromtimestamp(
        float(epoch), tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_ts(value: Any) -> float:
    if value in (None, ""):
        raise LifecycleError("timestamp missing")
    if isinstance(value, (int, float)):
        number = float(value)
        return number / 1000.0 if number > 10_000_000_000 else number
    text = str(value).strip()
    try:
        number = float(text)
    except ValueError:
        return dt.datetime.fromisoformat(
            text.replace("Z", "+00:00")).timestamp()
    return number / 1000.0 if number > 10_000_000_000 else number


def number(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def cents(value: Any) -> int:
    return int(round(float(value) * 100))


def chunks(values: Sequence[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(values), size):
        yield list(values[index:index + size])


def query_path(base: str, params: Mapping[str, Any]) -> str:
    if not base.startswith("/trade-api/v2/"):
        raise LifecycleError("API path is outside trade-api v2")
    clean = {key: value for key, value in params.items()
             if value not in (None, "")}
    return base + ("?" + urlencode(clean) if clean else "")


def target_slots(
    mismatch_rows: Sequence[Mapping[str, Any]],
    source_orders: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    missing = [
        row for row in mismatch_rows
        if row.get("mismatch_type") == "accepted_order_missing_receipt"
    ]
    if len(missing) != EXPECTED_TARGET_SLOTS:
        raise LifecycleError(
            f"target mismatch rows={len(missing)}, expected 703")
    orders_by_id = {
        str(row.get("order_id")): dict(row)
        for row in source_orders if row.get("order_id")
    }
    result = []
    seen: set[str] = set()
    for row in missing:
        order_id = str(row.get("order_id") or "")
        if not order_id or order_id in seen:
            raise LifecycleError("703 target rows lack unique exact order IDs")
        source = orders_by_id.get(order_id)
        if source is None:
            raise LifecycleError("target order ID is absent from normalized orders")
        client_id = str(source.get("client_order_id") or "")
        ticker = str(source.get("ticker") or "")
        event_id = str(source.get("event_id") or "")
        if not client_id or not ticker or not event_id:
            raise LifecycleError("target lacks strict client/ticker/event identity")
        seen.add(order_id)
        result.append({
            "order_id": order_id,
            "client_order_id": client_id,
            "event_id": event_id,
            "ticker": ticker,
            "leg": source.get("leg") or ticker.rsplit("-", 1)[-1],
            "source_order": source,
        })
    result.sort(key=lambda row: (
        row["event_id"], row["ticker"],
        parse_ts(
            row["source_order"].get("exchange_created_ts")
            or row["source_order"].get("local_created_ts")
            or row["source_order"].get("local_logged_ts")
            or row["source_order"].get("attempt_ts")
            or 0),
        row["order_id"],
    ))
    return result


def event_evaluation_end(event: Mapping[str, Any]) -> tuple[float, str]:
    if (event.get("actual_start_verified") is True
            and event.get("actual_start_exchange_ts") not in (None, "")):
        return (
            parse_ts(event["actual_start_exchange_ts"]),
            "verified_actual_start",
        )
    scheduled = parse_ts(event.get("scheduled_start_exchange_ts"))
    return scheduled + 3600.0, "scheduled_start_plus_60m_corridor"


def enrich_evaluation_edges(
    source_orders: Sequence[Mapping[str, Any]],
    source_events: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], collections.Counter[str]]:
    event_map = {
        str(row.get("event_id") or ""): row for row in source_events}
    result = []
    sources: collections.Counter[str] = collections.Counter()
    for source in source_orders:
        row = dict(source)
        if row.get("evaluation_end_exchange_ts") in (None, ""):
            event = event_map.get(str(row.get("event_id") or ""))
            if event is None:
                sources["event_outside_normalized_D_catalog"] += 1
                result.append(row)
                continue
            edge, edge_source = event_evaluation_end(event)
            row["evaluation_end_exchange_ts"] = edge
            row["evaluation_end_source"] = edge_source
            sources[edge_source] += 1
        else:
            sources["source_order_existing"] += 1
        result.append(row)
    return result, sources


def derive_bounds(
    source_orders: Sequence[Mapping[str, Any]],
    event_ids: set[str],
) -> dict[str, Any]:
    relevant = [
        row for row in source_orders
        if str(row.get("event_id") or "") in event_ids
        and row.get("purpose") == "entry"
        and row.get("action") == "buy"
    ]
    created = []
    local_bound_rows = 0
    for row in relevant:
        value = row.get("exchange_created_ts")
        if value in (None, ""):
            value = (
                row.get("local_created_ts")
                or row.get("local_logged_ts")
                or row.get("attempt_ts"))
            if value not in (None, ""):
                local_bound_rows += 1
        if value not in (None, ""):
            created.append(parse_ts(value))
    ends = [
        parse_ts(row["evaluation_end_exchange_ts"]) for row in relevant
        if row.get("evaluation_end_exchange_ts") not in (None, "")
    ]
    if not created or not ends:
        raise LifecycleError("cannot derive causal export bounds")
    minimum = math.floor(min(created)) - 3600
    maximum = math.ceil(max(ends)) + 1
    return {
        "min_ts": minimum,
        "max_ts": maximum,
        "min_utc": iso_utc(minimum),
        "max_utc": iso_utc(maximum),
        "source_order_rows": len(relevant),
        "law": (
            "one-hour capture buffer before earliest retained D entry clock "
            "through one second after latest frozen evaluation edge; local "
            "clocks select export range only and never establish causal order"),
        "local_clock_rows_used_for_lower_bound": local_bound_rows,
    }


class RawPageWriter:
    def __init__(self, path: Path):
        self.path = path
        self.temporary = path.with_suffix(path.suffix + ".tmp")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.temporary.open(
            "w", encoding="utf-8", newline=chr(10))
        os.chmod(self.temporary, 0o600)
        self.pages = 0

    def append(self, row: Mapping[str, Any]) -> None:
        self.handle.write(json.dumps(
            dict(row), sort_keys=True, separators=(",", ":")))
        self.handle.write(chr(10))
        self.handle.flush()
        os.fsync(self.handle.fileno())
        self.pages += 1

    def close(self) -> None:
        self.handle.close()
        os.replace(self.temporary, self.path)
        os.chmod(self.path, 0o400)


class ReadOnlyClient:
    def __init__(
        self, base_url: str, private_key: Any, headers_fn: Any,
        writer: RawPageWriter, min_interval: float = 0.15,
    ):
        import requests

        self.session = requests.Session()
        self.base_url = base_url.rstrip("/")
        self.private_key = private_key
        self.headers_fn = headers_fn
        self.writer = writer
        self.min_interval = min_interval
        self.last_request = 0.0
        self.http_requests = 0
        self.retries = 0
        self.rate_limits = 0
        self.request_errors = 0
        self.pagination_queries = 0
        self.pagination_complete = 0
        self.cursor_cycles = 0
        self.records = collections.Counter()

    def _throttle(self) -> None:
        delay = self.min_interval - (time.monotonic() - self.last_request)
        if delay > 0:
            time.sleep(delay)

    def get(
        self, path: str, label: str, *, allow_404: bool = False,
    ) -> tuple[int, dict[str, Any]]:
        if not path.startswith("/trade-api/v2/"):
            raise LifecycleError("refused non-v2 GET path")
        for attempt in range(9):
            self._throttle()
            headers = self.headers_fn(self.private_key, ALLOWED_METHOD, path)
            try:
                response = self.session.get(
                    self.base_url + path, headers=headers, timeout=45)
            except Exception as exc:
                self.request_errors += 1
                if attempt == 8:
                    raise LifecycleError(
                        f"{label}: network retries exhausted") from exc
                self.retries += 1
                time.sleep(min(30.0, 0.5 * (2 ** attempt)))
                continue
            finally:
                self.last_request = time.monotonic()
            self.http_requests += 1
            status = int(response.status_code)
            retry_after = response.headers.get("Retry-After")
            try:
                body = response.json()
            except ValueError:
                body = {"non_json_body": response.text[:2000]}
            if not isinstance(body, dict):
                body = {"unexpected_body": body}
            self.writer.append({
                "schema_version": SCHEMA,
                "label": label,
                "method": ALLOWED_METHOD,
                "path": path,
                "http_status": status,
                "response": body,
                "received_utc": iso_utc(time.time()),
                "retry_attempt": attempt,
            })
            if status in RETRYABLE:
                self.retries += 1
                if status == 429:
                    self.rate_limits += 1
                if attempt == 8:
                    raise LifecycleError(
                        f"{label}: HTTP retries exhausted ({status})")
                wait = float(retry_after) if retry_after else min(
                    30.0, 0.5 * (2 ** attempt))
                time.sleep(max(0.2, wait))
                continue
            if status == 404 and allow_404:
                return status, body
            if status != 200:
                self.request_errors += 1
                raise LifecycleError(f"{label}: unexpected HTTP {status}")
            return status, body
        raise LifecycleError(f"{label}: unreachable retry state")

    def paged(
        self, base: str, params: Mapping[str, Any], key: str, label: str,
    ) -> list[dict[str, Any]]:
        self.pagination_queries += 1
        cursor = ""
        seen: set[str] = set()
        rows: list[dict[str, Any]] = []
        page = 0
        while True:
            page += 1
            actual = dict(params)
            if cursor:
                actual["cursor"] = cursor
            _, body = self.get(
                query_path(base, actual), f"{label}:page-{page:04d}")
            values = body.get(key)
            if not isinstance(values, list):
                raise LifecycleError(f"{label}: response lacks {key} list")
            if "cursor" not in body:
                raise LifecycleError(f"{label}: response lacks cursor field")
            for value in values:
                if not isinstance(value, dict):
                    raise LifecycleError(f"{label}: non-object record")
                rows.append(value)
            self.records[key] += len(values)
            next_cursor = str(body.get("cursor") or "")
            if not next_cursor:
                self.pagination_complete += 1
                break
            if next_cursor in seen:
                self.cursor_cycles += 1
                raise LifecycleError(f"{label}: cursor cycle")
            seen.add(next_cursor)
            cursor = next_cursor
        return rows

    def proof(self) -> dict[str, Any]:
        return {
            "http_get_requests": self.http_requests,
            "retry_attempts": self.retries,
            "rate_limit_responses": self.rate_limits,
            "request_errors": self.request_errors,
            "pagination_queries": self.pagination_queries,
            "pagination_complete_empty_cursor": self.pagination_complete,
            "cursor_cycles": self.cursor_cycles,
            "records_returned_before_dedup": dict(sorted(self.records.items())),
            "complete": (
                self.pagination_queries == self.pagination_complete
                and self.cursor_cycles == 0 and self.request_errors == 0),
        }


def dedup_records(
    rows: Sequence[Mapping[str, Any]], identity_keys: Sequence[str],
) -> tuple[list[dict[str, Any]], int]:
    result: dict[str, dict[str, Any]] = {}
    duplicates = 0
    for source in rows:
        row = dict(source)
        identity = next(
            (str(row.get(key)) for key in identity_keys if row.get(key)), "")
        if not identity:
            raise LifecycleError("API record lacks stable identity")
        prior = result.get(identity)
        if prior is not None:
            duplicates += 1
            if prior != row:
                raise LifecycleError("same API identity has conflicting payloads")
            continue
        result[identity] = row
    return [result[key] for key in sorted(result)], duplicates


def api_order_price(order: Mapping[str, Any]) -> int:
    outcome = str(order.get("outcome_side") or order.get("side") or "")
    if outcome == "yes":
        return cents(order["yes_price_dollars"])
    if outcome == "no":
        return cents(order["no_price_dollars"])
    raise LifecycleError("API order lacks outcome side")


def api_fill_price(fill: Mapping[str, Any]) -> int:
    outcome = str(fill.get("outcome_side") or fill.get("side") or "")
    if outcome == "yes":
        return cents(fill["yes_price_dollars"])
    if outcome == "no":
        return cents(fill["no_price_dollars"])
    raise LifecycleError("API fill lacks outcome side")


def strict_identity_errors(
    source: Mapping[str, Any], api_order: Mapping[str, Any],
) -> list[str]:
    errors = []
    comparisons = [
        ("order_id", str(source.get("order_id") or ""),
         str(api_order.get("order_id") or "")),
        ("client_order_id", str(source.get("client_order_id") or ""),
         str(api_order.get("client_order_id") or "")),
        ("ticker", str(source.get("ticker") or ""),
         str(api_order.get("ticker") or "")),
        ("action", str(source.get("action") or ""),
         str(api_order.get("action") or "")),
        ("side", str(source.get("side") or ""),
         str(api_order.get("side") or "")),
    ]
    for name, expected, actual in comparisons:
        if name == "side" and not expected:
            if actual not in {"yes", "no"}:
                errors.append("api_side_missing")
            continue
        if not expected or expected != actual:
            errors.append(f"{name}_mismatch")
    try:
        api_created = parse_ts(
            api_order.get("created_time") or api_order.get("created_ts_ms"))
        evaluation_end = parse_ts(source.get("evaluation_end_exchange_ts"))
        if api_created > evaluation_end:
            errors.append("api_created_after_evaluation_edge")
        if source.get("exchange_created_ts") not in (None, ""):
            if abs(parse_ts(source.get("exchange_created_ts"))
                   - api_created) > 0.001:
                errors.append("exchange_created_ts_mismatch")
    except (LifecycleError, ValueError, TypeError):
        errors.append("api_exchange_created_ts_missing")
    try:
        if not math.isclose(
            number(source.get("quantity")),
            number(api_order.get("initial_count_fp")),
            rel_tol=0.0, abs_tol=1e-9,
        ):
            errors.append("initial_quantity_mismatch")
    except (ValueError, TypeError):
        errors.append("initial_quantity_missing")
    try:
        if int(source.get("price_cents")) != api_order_price(api_order):
            errors.append("limit_price_mismatch")
    except (LifecycleError, ValueError, TypeError, KeyError):
        errors.append("limit_price_missing")
    return errors


def normalize_api_fill(fill: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "window1-normalized-v2",
        "fill_id": fill.get("fill_id") or fill.get("trade_id"),
        "trade_id": fill.get("trade_id"),
        "order_id": fill.get("order_id"),
        "ticker": fill.get("ticker") or fill.get("market_ticker"),
        "action": fill.get("action"),
        "side": fill.get("side"),
        "price_cents": api_fill_price(fill),
        "quantity": number(fill.get("count_fp")),
        "exchange_ts": parse_ts(
            fill.get("created_time") or fill.get("ts_ms") or fill.get("ts")),
        "source": "kalshi_private_fills_export",
    }


def classify_slot(
    slot: Mapping[str, Any],
    api_orders_by_id: Mapping[str, Sequence[Mapping[str, Any]]],
    api_fills_by_order: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    order_id = str(slot["order_id"])
    source = slot["source_order"]
    candidates = [dict(row) for row in api_orders_by_id.get(order_id, ())]
    unique = []
    seen_payloads: set[str] = set()
    for row in candidates:
        payload = json.dumps(row, sort_keys=True, separators=(",", ":"))
        if payload not in seen_payloads:
            seen_payloads.add(payload)
            unique.append(row)
    public = {
        "event_id": slot["event_id"],
        "ticker": slot["ticker"],
        "leg": slot["leg"],
    }
    if not unique:
        return {
            **public,
            "final_class": "still_absent_after_complete_source_exhaustion",
            "terminal_receipt_recovered": False,
            "fill_receipt_recovered": False,
            "reason_codes": ["no_exact_order_id_match"],
            "api_order": None,
            "normalized_fills": [],
        }
    if len(unique) != 1:
        return {
            **public,
            "final_class": "ambiguous",
            "terminal_receipt_recovered": False,
            "fill_receipt_recovered": False,
            "reason_codes": ["conflicting_exact_order_payloads"],
            "api_order": None,
            "normalized_fills": [],
        }
    api_order = unique[0]
    errors = strict_identity_errors(source, api_order)
    status = str(api_order.get("status") or "").lower()
    fill_count = number(
        api_order.get("fill_count_fp", api_order.get("fill_count")))
    remaining = number(api_order.get(
        "remaining_count_fp", api_order.get("remaining_count")))
    initial = number(api_order.get(
        "initial_count_fp", api_order.get("initial_count")))
    if status not in TERMINAL_STATUSES:
        errors.append("nonterminal_status")
    if initial > 0 and not math.isclose(
            initial, fill_count + remaining, rel_tol=0.0, abs_tol=1e-9):
        errors.append("quantity_conservation_mismatch")
    normalized_fills = []
    fill_ids: set[str] = set()
    fill_errors = []
    for fill in api_fills_by_order.get(order_id, ()):
        try:
            normalized = normalize_api_fill(fill)
        except (LifecycleError, ValueError, TypeError, KeyError):
            fill_errors.append("malformed_fill")
            continue
        fill_id = str(normalized.get("fill_id") or "")
        if not fill_id or fill_id in fill_ids:
            fill_errors.append("missing_or_duplicate_fill_id")
            continue
        fill_ids.add(fill_id)
        if normalized["order_id"] != order_id:
            fill_errors.append("fill_order_id_mismatch")
        if normalized["ticker"] != slot["ticker"]:
            fill_errors.append("fill_ticker_mismatch")
        if normalized["action"] != source.get("action"):
            fill_errors.append("fill_action_mismatch")
        normalized_fills.append(normalized)
    normalized_fills.sort(key=lambda row: (
        row["exchange_ts"], str(row["fill_id"])))
    summed = sum(number(row["quantity"]) for row in normalized_fills)
    if not math.isclose(summed, fill_count, rel_tol=0.0, abs_tol=1e-9):
        fill_errors.append("fill_sum_terminal_count_mismatch")
    errors.extend(fill_errors)
    if errors:
        return {
            **public,
            "final_class": "ambiguous",
            "terminal_receipt_recovered": status in TERMINAL_STATUSES,
            "fill_receipt_recovered": False,
            "reason_codes": sorted(set(errors)),
            "api_order": api_order,
            "normalized_fills": normalized_fills,
        }
    if fill_count > 0:
        final_class = "exact_fill_receipt_recovered"
        fill_recovered = True
    elif status in {"canceled", "expired", "rejected"}:
        final_class = "valid_nonfill_cancellation_rejection_recovered"
        fill_recovered = False
    else:
        final_class = "ambiguous"
        fill_recovered = False
    return {
        **public,
        "final_class": final_class,
        "terminal_receipt_recovered": status in TERMINAL_STATUSES,
        "fill_receipt_recovered": fill_recovered,
        "reason_codes": [] if final_class != "ambiguous"
                        else ["executed_without_fills"],
        "api_order": api_order,
        "normalized_fills": normalized_fills,
    }


def sanitized_slot_rows(
    results: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    counters: collections.Counter[tuple[str, str]] = collections.Counter()
    rows = []
    for result in sorted(results, key=lambda row: (
            str(row["event_id"]), str(row["ticker"]))):
        key = (str(result["event_id"]), str(result["ticker"]))
        counters[key] += 1
        rows.append({
            "schema_version": SCHEMA,
            "slot_id": f"slot-{len(rows) + 1:04d}",
            "event_id": result["event_id"],
            "ticker": result["ticker"],
            "leg": result["leg"],
            "ticker_slot_ordinal": counters[key],
            "final_class": result["final_class"],
            "terminal_receipt_recovered":
                result["terminal_receipt_recovered"],
            "fill_receipt_recovered": result["fill_receipt_recovered"],
            "reason_codes": list(result["reason_codes"]),
            "private_order_or_fill_identity_emitted": False,
        })
    return rows


def apply_order_replacements(
    source_orders: Sequence[Mapping[str, Any]],
    replacements: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        dict(replacements.get(str(row.get("order_id") or ""), row))
        for row in source_orders
    ]


def sanitize_validation_rows(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    sanitized = []
    for index, row in enumerate(rows, 1):
        sanitized.append({
            "schema_version": SCHEMA,
            "mismatch_id": f"validation-{index:04d}",
            "mismatch_type": row.get("mismatch_type"),
            "event_id": row.get("event_id"),
            "ticker": row.get("ticker"),
            "leg": row.get("leg"),
            "detail": row.get("detail"),
            "private_order_attempt_fill_identity_emitted": False,
        })
    return sanitized


def import_auth_module(module_dir: Path) -> tuple[Any, Any, str]:
    sys.path.insert(0, str(module_dir))
    try:
        from kalshi_reconciler import (  # type: ignore
            KALSHI_BASE_URL, _headers, _load_private_key)
    finally:
        sys.path.pop(0)
    return _load_private_key(), _headers, str(KALSHI_BASE_URL)


def run_preflight(args: argparse.Namespace) -> int:
    source_orders_raw = read_jsonl(Path(args.source_orders))
    source_mismatches = read_jsonl(Path(args.source_mismatches))
    source_events = read_jsonl(Path(args.source_events))
    source_orders, edge_sources = enrich_evaluation_edges(
        source_orders_raw, source_events)
    ledger = read_jsonl(Path(args.event_ledger))
    if len(ledger) != 804 or sum(
            bool(row.get("floor_pass")) for row in ledger) != 804:
        raise LifecycleError("D changed from 804")
    event_ids = {str(row["event_id"]) for row in ledger}
    if "KXATPCHALLENGERMATCH-26JUL21MICMAY" in event_ids:
        raise LifecycleError("post-sample MICMAY entered D")
    slots = target_slots(source_mismatches, source_orders)
    required = (
        "order_id", "client_order_id", "event_id", "ticker", "action",
        "quantity", "price_cents", "evaluation_end_exchange_ts",
    )
    presence = {
        key: sum(
            slot["source_order"].get(key) not in (None, "")
            for slot in slots)
        for key in required
    }
    report = {
        "schema_version": SCHEMA,
        "D": 804,
        "target_slots": len(slots),
        "target_source_available_fields": sorted({
            str(key) for slot in slots for key in slot["source_order"].keys()}),
        "target_window_receipt_available_fields": sorted({
            str(key)
            for slot in slots
            for key in (
                slot["source_order"].get("window_receipt") or {}).keys()
            if isinstance(
                slot["source_order"].get("window_receipt"), Mapping)
        }),
        "source_event_available_fields": sorted({
            str(key) for row in source_events for key in row.keys()}),
        "target_source_field_presence": presence,
        "source_exchange_created_ts_presence": sum(
            slot["source_order"].get("exchange_created_ts") not in (None, "")
            for slot in slots),
        "source_side_presence": sum(
            slot["source_order"].get("side") not in (None, "")
            for slot in slots),
        "source_local_clock_presence": sum(
            any(slot["source_order"].get(key) not in (None, "")
                for key in ("local_created_ts", "local_logged_ts", "attempt_ts"))
            for slot in slots),
        "causal_time_bounds": derive_bounds(source_orders, event_ids),
        "evaluation_end_source_counts": dict(sorted(edge_sources.items())),
        "micmay_joined": False,
        "private_identifiers_printed": False,
        "ready": all(value == 703 for value in presence.values()),
    }
    print(json.dumps(report, sort_keys=True))
    return 0 if report["ready"] else 2


def run_export(args: argparse.Namespace) -> int:
    output = Path(args.output_dir).resolve()
    if output.is_symlink():
        raise LifecycleError("private output directory may not be a symlink")
    output.mkdir(parents=True, exist_ok=True)
    os.chmod(output, 0o700)
    source_orders_raw = read_jsonl(Path(args.source_orders))
    source_events = read_jsonl(Path(args.source_events))
    source_orders, edge_sources = enrich_evaluation_edges(
        source_orders_raw, source_events)
    source_mismatches = read_jsonl(Path(args.source_mismatches))
    ledger = read_jsonl(Path(args.event_ledger))
    if len(ledger) != 804 or sum(
            bool(row.get("floor_pass")) for row in ledger) != 804:
        raise LifecycleError("D changed from 804")
    slots = target_slots(source_mismatches, source_orders)
    event_ids = {str(row["event_id"]) for row in ledger}
    if "KXATPCHALLENGERMATCH-26JUL21MICMAY" in event_ids:
        raise LifecycleError("post-sample MICMAY entered D")
    bounds = derive_bounds(source_orders, event_ids)
    key, headers_fn, base_url = import_auth_module(
        Path(args.auth_module_dir).resolve())
    raw_path = output / "raw_api_pages.private.jsonl"
    writer = RawPageWriter(raw_path)
    client = ReadOnlyClient(
        base_url, key, headers_fn, writer,
        min_interval=float(args.min_interval),
    )
    api_orders: list[dict[str, Any]] = []
    api_fills: list[dict[str, Any]] = []
    direct_status = collections.Counter()
    started = time.time()
    try:
        _, cutoff = client.get(
            "/trade-api/v2/historical/cutoff", "historical-cutoff")
        event_list = sorted(event_ids)
        order_max = math.ceil(started)
        for batch_number, batch in enumerate(chunks(event_list, 10), 1):
            api_orders.extend(client.paged(
                "/trade-api/v2/portfolio/orders",
                {
                    "limit": 1000,
                    "event_ticker": ",".join(batch),
                    "min_ts": bounds["min_ts"],
                    "max_ts": order_max,
                },
                "orders",
                f"live-orders-event-batch-{batch_number:03d}",
            ))
        api_fills.extend(client.paged(
            "/trade-api/v2/portfolio/fills",
            {
                "limit": 1000,
                "min_ts": bounds["min_ts"],
                "max_ts": bounds["max_ts"],
            },
            "fills",
            "live-fills-causal-range",
        ))
        cutoff_order = parse_ts(cutoff["orders_updated_ts"])
        cutoff_fill = parse_ts(cutoff["trades_created_ts"])
        historical_orders_queried = cutoff_order > bounds["min_ts"]
        historical_fills_queried = cutoff_fill > bounds["min_ts"]
        if historical_orders_queried:
            for ticker_number, ticker in enumerate(sorted({
                    str(row["ticker"]) for row in slots}), 1):
                api_orders.extend(client.paged(
                    "/trade-api/v2/historical/orders",
                    {
                        "limit": 1000,
                        "ticker": ticker,
                        "max_ts": min(bounds["max_ts"], math.ceil(cutoff_order)),
                    },
                    "orders",
                    f"historical-orders-ticker-{ticker_number:04d}",
                ))
        if historical_fills_queried:
            for ticker_number, ticker in enumerate(sorted({
                    str(row["ticker"]) for row in slots}), 1):
                api_fills.extend(client.paged(
                    "/trade-api/v2/historical/fills",
                    {
                        "limit": 1000,
                        "ticker": ticker,
                        "max_ts": min(bounds["max_ts"], math.ceil(cutoff_fill)),
                    },
                    "fills",
                    f"historical-fills-ticker-{ticker_number:04d}",
                ))
        for slot_number, slot in enumerate(slots, 1):
            order_id = str(slot["order_id"])
            status, body = client.get(
                f"/trade-api/v2/portfolio/orders/{order_id}",
                f"direct-order-slot-{slot_number:04d}",
                allow_404=True,
            )
            direct_status[str(status)] += 1
            if status == 200:
                order = body.get("order")
                if not isinstance(order, dict):
                    raise LifecycleError("direct order response lacks order")
                api_orders.append(order)
            api_fills.extend(client.paged(
                "/trade-api/v2/portfolio/fills",
                {"limit": 1000, "order_id": order_id},
                "fills",
                f"direct-fills-slot-{slot_number:04d}",
            ))
    finally:
        writer.close()
    orders_deduped, order_duplicates = dedup_records(
        api_orders, ("order_id",))
    fills_deduped, fill_duplicates = dedup_records(
        api_fills, ("fill_id", "trade_id"))
    orders_path = output / "api_orders.private.jsonl"
    fills_path = output / "api_fills.private.jsonl"
    write_jsonl(orders_path, orders_deduped, mode=0o400)
    write_jsonl(fills_path, fills_deduped, mode=0o400)
    proof = client.proof()
    manifest = {
        "schema_version": SCHEMA,
        "export_started_utc": iso_utc(started),
        "export_completed_utc": iso_utc(time.time()),
        "api_endpoint": "https://api.elections.kalshi.com/trade-api/v2",
        "api_version": "trade-api/v2",
        "methods_used": ["GET"],
        "D": 804,
        "target_slots": len(slots),
        "development_period": ["2026-07-12", "2026-07-20"],
        "causal_time_bounds": bounds,
        "evaluation_end_source_counts": dict(sorted(edge_sources.items())),
        "historical_cutoff": {
            "orders_updated_ts": cutoff.get("orders_updated_ts"),
            "trades_created_ts": cutoff.get("trades_created_ts"),
            "historical_orders_queried": historical_orders_queried,
            "historical_fills_queried": historical_fills_queried,
        },
        "pagination_proof": proof,
        "direct_order_http_status_counts": dict(sorted(direct_status.items())),
        "deduplicated_records": {
            "orders": len(orders_deduped),
            "fills": len(fills_deduped),
            "duplicate_order_receipts": order_duplicates,
            "duplicate_fill_receipts": fill_duplicates,
        },
        "private_files": {
            "raw_api_pages": {
                "bytes": raw_path.stat().st_size,
                "sha256": sha256_file(raw_path),
                "mode": "0400",
            },
            "api_orders": {
                "bytes": orders_path.stat().st_size,
                "sha256": sha256_file(orders_path),
                "mode": "0400",
            },
            "api_fills": {
                "bytes": fills_path.stat().st_size,
                "sha256": sha256_file(fills_path),
                "mode": "0400",
            },
        },
        "raw_private_identifiers_emitted_to_console_or_sanitized_manifest": False,
        "micmay_joined": False,
        "complete": proof["complete"] and len(slots) == 703,
    }
    private_manifest = output / "EXPORT_RECEIPT.private.json"
    sanitized_manifest = output / "EXPORT_MANIFEST.sanitized.json"
    write_json(private_manifest, manifest, mode=0o400)
    public = dict(manifest)
    public.pop("private_files")
    public["private_file_hashes"] = {
        name: {"bytes": value["bytes"], "sha256": value["sha256"]}
        for name, value in manifest["private_files"].items()
    }
    write_json(sanitized_manifest, public, mode=0o600)
    print(json.dumps({
        "complete": manifest["complete"],
        "D": 804,
        "target_slots": len(slots),
        "http_get_requests": proof["http_get_requests"],
        "pagination_complete": proof["complete"],
        "orders": len(orders_deduped),
        "fills": len(fills_deduped),
        "private_identifiers_printed": False,
    }, sort_keys=True))
    return 0 if manifest["complete"] else 2


def run_join(args: argparse.Namespace) -> int:
    source = Path(args.source_normalized_dir).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.chmod(output, 0o700)
    source_orders_raw = read_jsonl(source / "orders.jsonl")
    source_events = read_jsonl(source / "events.jsonl")
    source_orders, edge_sources = enrich_evaluation_edges(
        source_orders_raw, source_events)
    source_fills = read_jsonl(source / "fills.jsonl")
    mismatch_rows = read_jsonl(Path(args.source_mismatches))
    slots = target_slots(mismatch_rows, source_orders)
    api_orders = read_jsonl(Path(args.api_orders))
    api_fills = read_jsonl(Path(args.api_fills))
    orders_by_id: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    fills_by_order: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in api_orders:
        orders_by_id[str(row.get("order_id") or "")].append(row)
    for row in api_fills:
        fills_by_order[str(row.get("order_id") or "")].append(row)
    results = [
        classify_slot(slot, orders_by_id, fills_by_order) for slot in slots]
    target_ids = {str(slot["order_id"]) for slot in slots}
    replacement_orders: dict[str, dict[str, Any]] = {}
    replacement_fills: dict[str, list[dict[str, Any]]] = {}
    for slot, result in zip(slots, results):
        if result["final_class"] not in {
            "exact_fill_receipt_recovered",
            "valid_nonfill_cancellation_rejection_recovered",
        }:
            continue
        order_id = str(slot["order_id"])
        api_order = result["api_order"]
        updated = dict(slot["source_order"])
        updated["exchange_created_ts"] = parse_ts(
            api_order.get("created_time") or api_order.get("created_ts_ms"))
        updated["exchange_status"] = str(api_order["status"]).lower()
        updated["exchange_fill_count"] = number(
            api_order.get("fill_count_fp", api_order.get("fill_count")))
        updated["exchange_remaining_count"] = number(api_order.get(
            "remaining_count_fp", api_order.get("remaining_count")))
        updated["exchange_last_update_ts"] = parse_ts(
            api_order.get("last_update_time")
            or api_order.get("last_updated_ts_ms"))
        updated["terminal_receipt_source"] = "kalshi_private_orders_export"
        replacement_orders[order_id] = updated
        replacement_fills[order_id] = [
            dict(row) for row in result["normalized_fills"]]
    joined_orders = apply_order_replacements(
        source_orders, replacement_orders)
    joined_fills = [
        dict(row) for row in source_fills
        if str(row.get("order_id") or "") not in target_ids
        or str(row.get("order_id") or "") not in replacement_fills
    ]
    for order_id in sorted(replacement_fills):
        joined_fills.extend(replacement_fills[order_id])
    private_result = output / "slot_join.private.jsonl"
    write_jsonl(private_result, results, mode=0o400)
    write_jsonl(output / "orders.jsonl", joined_orders, mode=0o600)
    write_jsonl(output / "fills.jsonl", joined_fills, mode=0o600)
    for name in ("events.jsonl", "prints.jsonl", "books.jsonl"):
        source_path = source / name
        destination = output / name
        destination.write_bytes(source_path.read_bytes())
        os.chmod(destination, 0o600)
    decisions_source = Path(args.decisions)
    (output / "decisions.jsonl").write_bytes(decisions_source.read_bytes())
    os.chmod(output / "decisions.jsonl", 0o600)
    sanitized = sanitized_slot_rows(results)
    sanitized_path = output / "LIFECYCLE_SLOT_RESULTS.sanitized.jsonl"
    write_jsonl(sanitized_path, sanitized, mode=0o600)
    class_counts = collections.Counter(
        str(row["final_class"]) for row in results)
    summary = {
        "schema_version": SCHEMA,
        "D": 804,
        "target_slots": len(results),
        "classification_counts": dict(sorted(class_counts.items())),
        "evaluation_end_source_counts": dict(sorted(edge_sources.items())),
        "exact_terminal_receipt_recovered": sum(
            bool(row["terminal_receipt_recovered"]) for row in results),
        "exact_fill_receipt_recovered": sum(
            bool(row["fill_receipt_recovered"]) for row in results),
        "valid_nonfill_cancellation_rejection_recovered": class_counts[
            "valid_nonfill_cancellation_rejection_recovered"],
        "ambiguous": class_counts["ambiguous"],
        "still_absent_after_complete_source_exhaustion": class_counts[
            "still_absent_after_complete_source_exhaustion"],
        "joined_order_rows": len(joined_orders),
        "joined_fill_rows": len(joined_fills),
        "private_slot_join_sha256": sha256_file(private_result),
        "sanitized_slot_results_sha256": sha256_file(sanitized_path),
        "private_identifiers_emitted": False,
        "micmay_joined": False,
        "strategy_scoring_permitted": False,
    }
    write_json(output / "LIFECYCLE_JOIN_SUMMARY.sanitized.json",
               summary, mode=0o600)
    print(json.dumps({
        "D": 804,
        "target_slots": len(results),
        "classification_counts": dict(sorted(class_counts.items())),
        "private_identifiers_printed": False,
    }, sort_keys=True))
    return 0


def run_sanitize_validation(args: argparse.Namespace) -> int:
    before = read_json(Path(args.before_summary))
    after = read_json(Path(args.after_summary))
    mismatches = read_jsonl(Path(args.after_mismatches))
    if after.get("floor_passing_events") != 804:
        raise LifecycleError("after validation changed D")
    sanitized = sanitize_validation_rows(mismatches)
    output = Path(args.output_dir)
    write_jsonl(output / "VALIDATION_UNRESOLVED.sanitized.jsonl",
                sanitized, mode=0o600)
    report = {
        "schema_version": SCHEMA,
        "D": 804,
        "before": {
            "gate_pass": before.get("gate_pass"),
            "mismatch_count": before.get("mismatch_count"),
            "mismatch_types": before.get("mismatch_types"),
        },
        "after": {
            "gate_pass": after.get("gate_pass"),
            "mismatch_count": after.get("mismatch_count"),
            "mismatch_types": after.get("mismatch_types"),
            "accepted_orders_missing_terminal_receipt":
                after.get("accepted_orders_missing_terminal_receipt"),
            "receipt_validation_errors":
                after.get("receipt_validation_errors"),
            "unobserved_decision_legs":
                after.get("unobserved_decision_legs"),
        },
        "unresolved_rows": len(sanitized),
        "strategy_scoring_permitted": after.get("gate_pass") is True,
        "scoring_tuning_ablation_holdout_run": False,
        "micmay_joined": False,
        "private_identifiers_emitted": False,
    }
    write_json(output / "LIFECYCLE_VALIDATION_RESULT.sanitized.json",
               report, mode=0o600)
    print(json.dumps({
        "D": 804,
        "before_mismatches": before.get("mismatch_count"),
        "after_mismatches": after.get("mismatch_count"),
        "gate_pass": after.get("gate_pass"),
        "private_identifiers_printed": False,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--source-orders", required=True)
    preflight.add_argument("--source-mismatches", required=True)
    preflight.add_argument("--source-events", required=True)
    preflight.add_argument("--event-ledger", required=True)
    preflight.set_defaults(func=run_preflight)
    export = subparsers.add_parser("export")
    export.add_argument("--source-orders", required=True)
    export.add_argument("--source-mismatches", required=True)
    export.add_argument("--source-events", required=True)
    export.add_argument("--event-ledger", required=True)
    export.add_argument("--auth-module-dir", required=True)
    export.add_argument("--output-dir", required=True)
    export.add_argument("--min-interval", type=float, default=0.15)
    export.set_defaults(func=run_export)
    join = subparsers.add_parser("join")
    join.add_argument("--source-normalized-dir", required=True)
    join.add_argument("--source-mismatches", required=True)
    join.add_argument("--decisions", required=True)
    join.add_argument("--api-orders", required=True)
    join.add_argument("--api-fills", required=True)
    join.add_argument("--output-dir", required=True)
    join.set_defaults(func=run_join)
    sanitize = subparsers.add_parser("sanitize-validation")
    sanitize.add_argument("--before-summary", required=True)
    sanitize.add_argument("--after-summary", required=True)
    sanitize.add_argument("--after-mismatches", required=True)
    sanitize.add_argument("--output-dir", required=True)
    sanitize.set_defaults(func=run_sanitize_validation)
    return root


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
