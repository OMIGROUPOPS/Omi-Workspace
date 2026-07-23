#!/usr/bin/env python3
"""Forensic identity bridge for the frozen Window-1 lifecycle export.

This tool is deliberately offline.  It reads the immutable private API export,
the 703 private lifecycle slots, and the byte-pinned engine-log snapshot.  It
does not import an API client and contains no network operation.

Raw identifiers are written only to an owner-only private output directory.
The separate sanitized ledger contains public event/ticker identities, field
presence, format classes, candidate counts, failure classes, and aggregate
proofs suitable for Git.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import datetime as dt
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import parse_qs, urlsplit


SCHEMA = "window1-identity-bridge-v1"
EXPECTED_SLOTS = 703
ALLOWED_FAILURE_CLASSES = {
    "exchange_id_absent_from_slot",
    "exchange_id_present_but_absent_from_api",
    "identifier_format_type_mismatch",
    "ticker_or_participant_mapping_mismatch",
    "timestamp_or_timezone_mismatch",
    "side_or_action_canonicalization_mismatch",
    "cents_dollars_or_count_count_fp_mismatch",
    "query_window_exclusion",
    "genuinely_no_corresponding_exchange_record",
}
TERMINAL_STATUSES = {"canceled", "executed", "expired", "rejected"}
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
    r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
UUID_LOOSE_RE = re.compile(r"^[{(]?[0-9a-fA-F-]{32,38}[)}]?$")


class BridgeError(RuntimeError):
    """A violated evidence or identity invariant."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BridgeError(f"{path.name}: expected JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                value = json.loads(line)
            except ValueError as exc:
                raise BridgeError(
                    f"{path.name}:{line_number}: malformed JSON") from exc
            if not isinstance(value, dict):
                raise BridgeError(
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
        raise BridgeError(f"{path.name}: shorter than pinned byte limit")
    return digest.hexdigest()


def present(value: Any) -> bool:
    return value not in (None, "")


def parse_timestamp(value: Any) -> float:
    if not present(value):
        raise BridgeError("timestamp missing")
    if isinstance(value, (int, float)):
        number = float(value)
        return number / 1000.0 if number > 10_000_000_000 else number
    text = str(value).strip()
    try:
        number = float(text)
    except ValueError:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise BridgeError("timezone-naive timestamp")
        return parsed.timestamp()
    return number / 1000.0 if number > 10_000_000_000 else number


def utc_iso(value: float) -> str:
    return dt.datetime.fromtimestamp(
        value, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def decimal_value(value: Any) -> Decimal:
    if not present(value):
        raise BridgeError("numeric field missing")
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise BridgeError("invalid numeric field") from exc


def decimal_text(value: Any) -> str:
    number = decimal_value(value)
    result = format(number.normalize(), "f")
    return "0" if result in {"-0", ""} else result


def dollars_to_cents(value: Any) -> int:
    return int((decimal_value(value) * 100).quantize(Decimal("1")))


def api_side(row: Mapping[str, Any]) -> str:
    return str(row.get("outcome_side") or row.get("side") or "").lower()


def api_price_cents(row: Mapping[str, Any]) -> int:
    side = api_side(row)
    if side == "yes":
        return dollars_to_cents(row.get("yes_price_dollars"))
    if side == "no":
        return dollars_to_cents(row.get("no_price_dollars"))
    raise BridgeError("API order lacks yes/no outcome side")


def api_quantity(row: Mapping[str, Any]) -> str:
    value = row.get("initial_count_fp")
    if not present(value):
        value = row.get("initial_count")
    return decimal_text(value)


def api_created_ts(row: Mapping[str, Any]) -> float:
    return parse_timestamp(
        row.get("created_time") or row.get("created_ts_ms"))


def identifier_shape(value: Any) -> dict[str, Any]:
    if not present(value):
        return {"present": False}
    text = str(value)
    if UUID_RE.fullmatch(text):
        shape = "uuid_hyphenated"
    elif UUID_LOOSE_RE.fullmatch(text):
        shape = "uuid_loose"
    elif text.isdecimal():
        shape = "decimal"
    else:
        shape = "opaque"
    return {
        "present": True,
        "source_type": type(value).__name__,
        "length": len(text),
        "format_class": shape,
    }


def canonical_identifier(value: Any) -> str:
    if not present(value):
        return ""
    text = str(value).strip()
    if UUID_LOOSE_RE.fullmatch(text):
        compact = re.sub(r"[^0-9a-fA-F]", "", text).lower()
        if len(compact) == 32:
            return "uuid:" + compact
    return "exact:" + text


def source_local_ts(source: Mapping[str, Any]) -> tuple[float | None, str]:
    for key in (
        "local_logged_ts", "local_created_ts", "attempt_ts",
        "exchange_created_ts",
    ):
        if present(source.get(key)):
            return parse_timestamp(source[key]), key
    return None, "absent"


def build_target_slots(
    mismatch_rows: Sequence[Mapping[str, Any]],
    source_orders: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    targets = [
        row for row in mismatch_rows
        if row.get("mismatch_type") == "accepted_order_missing_receipt"
    ]
    if len(targets) != EXPECTED_SLOTS:
        raise BridgeError(
            f"target mismatch rows={len(targets)}, expected 703")
    orders_by_id = {
        str(row.get("order_id")): dict(row)
        for row in source_orders if present(row.get("order_id"))
    }
    result = []
    seen = set()
    for target in targets:
        order_id = str(target.get("order_id") or "")
        if not order_id or order_id in seen:
            raise BridgeError("target rows lack unique order IDs")
        source = orders_by_id.get(order_id)
        if source is None:
            raise BridgeError("target order ID absent from frozen orders")
        seen.add(order_id)
        result.append({
            "event_id": source.get("event_id"),
            "ticker": source.get("ticker"),
            "leg": (
                source.get("leg")
                or str(source.get("ticker") or "").rsplit("-", 1)[-1]
            ),
            "source_order": source,
        })
    result.sort(key=lambda row: (
        str(row.get("event_id") or ""),
        str(row.get("ticker") or ""),
        source_local_ts(row["source_order"])[0] or 0.0,
        str(row["source_order"].get("order_id") or ""),
    ))
    return result


def event_from_ticker(ticker: str) -> str:
    return ticker.rsplit("-", 1)[0] if "-" in ticker else ""


def source_composite(
    source: Mapping[str, Any], log: Mapping[str, Any] | None,
) -> tuple[str, str, str, int, str] | None:
    side = str(source.get("side") or "").lower()
    if not side and log:
        side = str(log.get("side") or "").lower()
    if side not in {"yes", "no"}:
        return None
    try:
        return (
            str(source.get("ticker") or ""),
            side,
            str(source.get("action") or "").lower(),
            int(decimal_value(source.get("price_cents"))),
            decimal_text(source.get("quantity")),
        )
    except BridgeError:
        return None


def api_composite(
    order: Mapping[str, Any],
) -> tuple[str, str, str, int, str] | None:
    try:
        return (
            str(order.get("ticker") or ""),
            api_side(order),
            str(order.get("action") or "").lower(),
            api_price_cents(order),
            api_quantity(order),
        )
    except BridgeError:
        return None


def response_accepted(value: Any) -> bool:
    if not present(value):
        return False
    normalized = str(value).strip().lower()
    if normalized in TERMINAL_STATUSES | {"resting", "pending", "filled"}:
        return True
    try:
        status = int(str(value).split()[0])
    except (ValueError, TypeError):
        return False
    return 200 <= status < 300


def iter_log_lines(
    log_dir: Path, active_prefix_bytes: int,
) -> Iterable[tuple[str, bytes]]:
    immutable = sorted(log_dir.glob("live_v3_2026071[2-9]*.jsonl.gz"))
    if not immutable:
        raise BridgeError("immutable engine log set is empty")
    for path in immutable:
        with gzip.open(path, "rb") as handle:
            for line in handle:
                yield path.name, line
    active = log_dir / "live_v3_20260720.jsonl"
    if not active.is_file():
        raise BridgeError("byte-pinned active engine log is absent")
    with active.open("rb") as handle:
        while handle.tell() < active_prefix_bytes:
            line = handle.readline()
            if not line:
                break
            if handle.tell() > active_prefix_bytes:
                break
            yield active.name, line


def read_order_placed_logs(
    log_dir: Path, active_prefix_bytes: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: dict[tuple[Any, ...], dict[str, Any]] = {}
    physical_rows = 0
    parse_errors = 0
    placed_rows = 0
    duplicate_rows = 0
    for file_name, line in iter_log_lines(log_dir, active_prefix_bytes):
        physical_rows += 1
        if b'"order_placed"' not in line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            parse_errors += 1
            continue
        if row.get("event") != "order_placed":
            continue
        placed_rows += 1
        details = row.get("details")
        if not isinstance(details, dict):
            continue
        ticker = str(row.get("ticker") or "")
        record = {
            "event_id": event_from_ticker(ticker),
            "ticker": ticker,
            "order_id": details.get("order_id"),
            "client_order_id": details.get("client_order_id"),
            "internal_attempt_id": details.get("attempt_id"),
            "internal_trade_id": details.get("trade_id"),
            "side": details.get("side"),
            "action": details.get("action"),
            "price_cents": details.get("price"),
            "quantity": details.get("count"),
            "local_logged_ts": row.get("ts_epoch"),
            "response_status": details.get("response_status"),
            "source_file_class": (
                "active_byte_pinned"
                if file_name.endswith(".jsonl")
                else "immutable_gzip"
            ),
        }
        fingerprint = (
            str(record.get("order_id") or ""),
            str(record.get("client_order_id") or ""),
            ticker,
            str(record.get("local_logged_ts") or ""),
            str(record.get("internal_trade_id") or ""),
        )
        prior = records.get(fingerprint)
        if prior is not None:
            duplicate_rows += 1
            if prior != record:
                raise BridgeError("conflicting duplicate order_placed receipt")
            continue
        records[fingerprint] = record
    hashes = []
    for path in sorted(log_dir.glob("live_v3_2026071[2-9]*.jsonl.gz")):
        hashes.append({
            "logical_name": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "evidence_class": "immutable_gzip",
        })
    active = log_dir / "live_v3_20260720.jsonl"
    hashes.append({
        "logical_name": active.name + ":pinned-prefix",
        "bytes": active_prefix_bytes,
        "sha256": sha256_file(active, active_prefix_bytes),
        "evidence_class": "active_byte_pinned",
    })
    audit = {
        "physical_rows_scanned": physical_rows,
        "order_placed_physical_rows": placed_rows,
        "deduplicated_order_placed_rows": len(records),
        "duplicate_order_placed_rows": duplicate_rows,
        "selected_parse_errors": parse_errors,
        "active_prefix_bytes": active_prefix_bytes,
        "source_hashes": hashes,
    }
    return list(records.values()), audit


def endpoint_class(path: str) -> str:
    parsed = urlsplit(path)
    bare = parsed.path
    if bare == "/trade-api/v2/historical/cutoff":
        return "historical_cutoff"
    if bare == "/trade-api/v2/portfolio/orders":
        return "current_orders_collection"
    if re.fullmatch(r"/trade-api/v2/portfolio/orders/[^/]+", bare):
        return "current_order_exact_id"
    if bare == "/trade-api/v2/portfolio/fills":
        return "current_fills_collection"
    if bare == "/trade-api/v2/historical/orders":
        return "historical_orders_collection"
    if bare == "/trade-api/v2/historical/fills":
        return "historical_fills_collection"
    return "unexpected_endpoint"


def pagination_group(label: str) -> tuple[str, int | None]:
    match = re.fullmatch(r"(.+):page-(\d{4})", label)
    if not match:
        return label, None
    return match.group(1), int(match.group(2))


def audit_raw_pages(
    raw_pages: Sequence[Mapping[str, Any]],
    api_orders: Sequence[Mapping[str, Any]],
    api_fills: Sequence[Mapping[str, Any]],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    endpoints = Counter()
    logical_labels: dict[str, set[str]] = defaultdict(set)
    statuses: dict[str, Counter[str]] = defaultdict(Counter)
    parameter_sets: dict[str, Counter[tuple[str, ...]]] = defaultdict(Counter)
    groups: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    unexpected_methods = Counter()
    raw_orders: list[Mapping[str, Any]] = []
    raw_fills: list[Mapping[str, Any]] = []
    for row in raw_pages:
        method = str(row.get("method") or "")
        if method != "GET":
            unexpected_methods[method] += 1
        path = str(row.get("path") or "")
        kind = endpoint_class(path)
        endpoints[kind] += 1
        statuses[kind][str(row.get("http_status"))] += 1
        parsed = urlsplit(path)
        parameters = parse_qs(parsed.query)
        parameter_sets[kind][tuple(sorted(parameters))] += 1
        label = str(row.get("label") or "")
        logical_labels[kind].add(pagination_group(label)[0])
        group, page = pagination_group(label)
        response = row.get("response")
        if not isinstance(response, dict):
            response = {}
        if page is not None and int(row.get("http_status") or 0) == 200:
            groups[group].append((
                page,
                str(parameters.get("cursor", [""])[0]),
                str(response.get("cursor") or ""),
            ))
        values = response.get("orders")
        if isinstance(values, list):
            raw_orders.extend(
                value for value in values if isinstance(value, dict))
        values = response.get("fills")
        if isinstance(values, list):
            raw_fills.extend(
                value for value in values if isinstance(value, dict))
    pagination_errors = []
    for group, pages in sorted(groups.items()):
        pages.sort()
        numbers = [row[0] for row in pages]
        if numbers != list(range(1, len(numbers) + 1)):
            pagination_errors.append(group + ":nonconsecutive_pages")
        if not pages or pages[-1][2] != "":
            pagination_errors.append(group + ":nonempty_terminal_cursor")
        input_cursors = [row[1] for row in pages if row[1]]
        if len(input_cursors) != len(set(input_cursors)):
            pagination_errors.append(group + ":repeated_input_cursor")
        for index in range(1, len(pages)):
            if pages[index][1] != pages[index - 1][2]:
                pagination_errors.append(group + ":cursor_chain_break")
    order_ids = [str(row.get("order_id") or "") for row in raw_orders]
    fill_ids = [
        str(row.get("fill_id") or row.get("trade_id") or "")
        for row in raw_fills
    ]
    raw_order_duplicates = len(order_ids) - len(set(order_ids))
    raw_fill_duplicates = len(fill_ids) - len(set(fill_ids))
    if "" in order_ids or "" in fill_ids:
        raise BridgeError("raw API collection contains identity-free record")
    manifest_proof = receipt.get("pagination_proof") or {}
    return {
        "methods": {"GET": len(raw_pages)},
        "unexpected_methods": dict(sorted(unexpected_methods.items())),
        "endpoint_request_counts": dict(sorted(endpoints.items())),
        "endpoint_logical_query_counts": {
            key: len(value)
            for key, value in sorted(logical_labels.items())
        },
        "endpoint_http_status_counts": {
            key: dict(sorted(value.items()))
            for key, value in sorted(statuses.items())
        },
        "endpoint_filter_key_sets": {
            key: [
                {"keys": list(keys), "requests": count}
                for keys, count in sorted(value.items())
            ]
            for key, value in sorted(parameter_sets.items())
        },
        "pagination": {
            "groups": len(groups),
            "groups_ending_empty_cursor": sum(
                bool(rows) and sorted(rows)[-1][2] == ""
                for rows in groups.values()
            ),
            "errors": pagination_errors,
            "manifest_queries": manifest_proof.get("pagination_queries"),
            "manifest_completed": manifest_proof.get(
                "pagination_complete_empty_cursor"),
            "manifest_cursor_cycles": manifest_proof.get("cursor_cycles"),
            "manifest_request_errors": manifest_proof.get("request_errors"),
        },
        "records": {
            "raw_order_occurrences": len(raw_orders),
            "raw_fill_occurrences": len(raw_fills),
            "raw_order_duplicate_occurrences": raw_order_duplicates,
            "raw_fill_duplicate_occurrences": raw_fill_duplicates,
            "deduplicated_orders": len(api_orders),
            "deduplicated_fills": len(api_fills),
            "retry_attempt_rows": sum(
                int(row.get("retry_attempt") or 0) > 0
                for row in raw_pages
            ),
        },
        "status_coverage": dict(sorted(Counter(
            str(row.get("status") or "missing").lower()
            for row in api_orders
        ).items())),
        "order_id_shapes": shape_counts(
            row.get("order_id") for row in api_orders),
        "client_order_id_shapes": shape_counts(
            row.get("client_order_id") for row in api_orders),
        "fill_id_shapes": shape_counts(
            row.get("fill_id") or row.get("trade_id") for row in api_fills),
        "identity_normalization": (
            "exact string keys first; UUID canonical form is diagnostic only; "
            "no case folding, trimming or numeric coercion can create a match"),
    }


def shape_counts(values: Iterable[Any]) -> dict[str, int]:
    counts = Counter()
    for value in values:
        shape = identifier_shape(value)
        key = (
            "absent" if not shape["present"] else
            f"{shape['source_type']}:{shape['format_class']}:"
            f"len-{shape['length']}"
        )
        counts[key] += 1
    return dict(sorted(counts.items()))


def index_many(
    rows: Sequence[Mapping[str, Any]], key,
) -> dict[Any, list[dict[str, Any]]]:
    result: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for source in rows:
        value = key(source)
        if value not in (None, ""):
            result[value].append(dict(source))
    return result


def unique_semantic_logs(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    result: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row.get("order_id") or ""),
            str(row.get("client_order_id") or ""),
            str(row.get("ticker") or ""),
            str(row.get("side") or ""),
            str(row.get("action") or ""),
            str(row.get("price_cents") or ""),
            str(row.get("quantity") or ""),
            str(row.get("local_logged_ts") or ""),
            str(row.get("response_status") or ""),
        )
        result[key] = dict(row)
    return list(result.values())


def fields_match_source_log(
    source: Mapping[str, Any], log: Mapping[str, Any],
) -> list[str]:
    failures = []
    if str(source.get("ticker") or "") != str(log.get("ticker") or ""):
        failures.append("ticker")
    if str(source.get("action") or "").lower() != str(
            log.get("action") or "").lower():
        failures.append("action")
    try:
        if int(decimal_value(source.get("price_cents"))) != int(
                decimal_value(log.get("price_cents"))):
            failures.append("price")
    except BridgeError:
        failures.append("price")
    try:
        if decimal_text(source.get("quantity")) != decimal_text(
                log.get("quantity")):
            failures.append("quantity")
    except BridgeError:
        failures.append("quantity")
    if present(source.get("client_order_id")) and str(
            source.get("client_order_id")) != str(
                log.get("client_order_id") or ""):
        failures.append("client_order_id")
    return failures


def strict_candidate_failures(
    source: Mapping[str, Any],
    log: Mapping[str, Any] | None,
    api: Mapping[str, Any],
    max_receipt_lag: float,
) -> list[str]:
    failures = []
    if str(source.get("ticker") or "") != str(api.get("ticker") or ""):
        failures.append("ticker_or_participant_mapping_mismatch")
    if str(source.get("action") or "").lower() != str(
            api.get("action") or "").lower():
        failures.append("side_or_action_canonicalization_mismatch")
    if log is not None:
        if str(log.get("side") or "").lower() != api_side(api):
            failures.append("side_or_action_canonicalization_mismatch")
        try:
            receipt_ts = parse_timestamp(log.get("local_logged_ts"))
            created_ts = api_created_ts(api)
            lag = receipt_ts - created_ts
            if lag < 0 or lag > max_receipt_lag:
                failures.append("timestamp_or_timezone_mismatch")
        except BridgeError:
            failures.append("timestamp_or_timezone_mismatch")
    else:
        failures.append("genuinely_no_corresponding_exchange_record")
    try:
        if int(decimal_value(source.get("price_cents"))) != api_price_cents(
                api):
            failures.append("cents_dollars_or_count_count_fp_mismatch")
        if decimal_text(source.get("quantity")) != api_quantity(api):
            failures.append("cents_dollars_or_count_count_fp_mismatch")
    except BridgeError:
        failures.append("cents_dollars_or_count_count_fp_mismatch")
    return sorted(set(failures))


def causal_composite_candidates(
    source: Mapping[str, Any],
    log: Mapping[str, Any] | None,
    api_by_composite: Mapping[Any, Sequence[dict[str, Any]]],
    max_receipt_lag: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    composite = source_composite(source, log)
    if composite is None or log is None:
        return [], []
    compatible = []
    incompatible = []
    try:
        receipt_ts = parse_timestamp(log.get("local_logged_ts"))
    except BridgeError:
        return [], list(api_by_composite.get(composite, []))
    for api in api_by_composite.get(composite, []):
        try:
            lag = receipt_ts - api_created_ts(api)
        except BridgeError:
            incompatible.append(api)
            continue
        if 0 <= lag <= max_receipt_lag:
            compatible.append(api)
        else:
            incompatible.append(api)
    return compatible, incompatible


def forensic(args: argparse.Namespace) -> int:
    output = Path(args.output_dir).resolve()
    if output.is_symlink():
        raise BridgeError("private output directory may not be a symlink")
    output.mkdir(parents=True, exist_ok=True)
    os.chmod(output, 0o700)

    slot_join_path = Path(args.slot_join).resolve()
    api_orders_path = Path(args.api_orders).resolve()
    api_fills_path = Path(args.api_fills).resolve()
    raw_pages_path = Path(args.raw_pages).resolve()
    receipt_path = Path(args.export_receipt).resolve()
    source_orders_path = Path(args.source_orders).resolve()
    source_mismatches_path = Path(args.source_mismatches).resolve()
    receipt = read_json(receipt_path)
    expected_hashes = receipt.get("private_files") or {}
    for logical, path in (
        ("raw_api_pages", raw_pages_path),
        ("api_orders", api_orders_path),
        ("api_fills", api_fills_path),
    ):
        expected = (expected_hashes.get(logical) or {}).get("sha256")
        actual = sha256_file(path)
        if not expected or expected != actual:
            raise BridgeError(f"{logical}: immutable export hash mismatch")

    prior_slot_results = read_jsonl(slot_join_path)
    source_orders = read_jsonl(source_orders_path)
    source_mismatches = read_jsonl(source_mismatches_path)
    slots = build_target_slots(source_mismatches, source_orders)
    api_orders = read_jsonl(api_orders_path)
    api_fills = read_jsonl(api_fills_path)
    raw_pages = read_jsonl(raw_pages_path)
    if len(slots) != EXPECTED_SLOTS:
        raise BridgeError(f"slot count={len(slots)}, expected 703")
    prior_slot_keys = Counter((
        str(row.get("event_id") or ""),
        str(row.get("ticker") or ""),
        str(row.get("leg") or ""),
    ) for row in prior_slot_results)
    rebuilt_slot_keys = Counter((
        str(row.get("event_id") or ""),
        str(row.get("ticker") or ""),
        str(row.get("leg") or ""),
    ) for row in slots)
    if prior_slot_keys != rebuilt_slot_keys:
        raise BridgeError(
            "rebuilt target slots disagree with prior lifecycle artifact")
    logs, log_audit = read_order_placed_logs(
        Path(args.log_dir).resolve(), args.active_log_prefix_bytes)

    api_by_order = index_many(
        api_orders, lambda row: str(row.get("order_id") or ""))
    api_by_client = index_many(
        api_orders, lambda row: str(row.get("client_order_id") or ""))
    api_by_canonical = index_many(
        api_orders, lambda row: canonical_identifier(row.get("order_id")))
    api_by_composite = index_many(api_orders, api_composite)
    logs_by_order = index_many(
        logs, lambda row: str(row.get("order_id") or ""))
    logs_by_client = index_many(
        logs, lambda row: str(row.get("client_order_id") or ""))
    logs_by_trade = index_many(
        logs, lambda row: str(row.get("internal_trade_id") or ""))

    private_rows = []
    working = []
    slot_clients = Counter()
    for index, slot in enumerate(slots, 1):
        source = slot.get("source_order")
        if not isinstance(source, dict):
            raise BridgeError("private slot lacks source_order")
        slot_id = f"slot-{index:04d}"
        order_id = source.get("order_id")
        client_id = source.get("client_order_id")
        trade_id = source.get("trade_id")
        if present(client_id):
            slot_clients[str(client_id)] += 1
        log_candidates = unique_semantic_logs([
            *logs_by_order.get(str(order_id or ""), []),
            *logs_by_client.get(str(client_id or ""), []),
            *logs_by_trade.get(str(trade_id or ""), []),
        ])
        log_matches = [
            row for row in log_candidates
            if not fields_match_source_log(source, row)
            and (
                (present(order_id) and str(order_id) == str(
                    row.get("order_id") or ""))
                or (present(client_id) and str(client_id) == str(
                    row.get("client_order_id") or ""))
                or (present(trade_id) and str(trade_id) == str(
                    row.get("internal_trade_id") or ""))
            )
        ]
        accepted_logs = [
            row for row in log_matches
            if response_accepted(row.get("response_status"))]
        log_field_mismatch_counts = Counter(
            failure for candidate in log_candidates
            for failure in fields_match_source_log(source, candidate))
        log_identity_path_counts = Counter()
        for candidate in log_candidates:
            if present(order_id) and str(order_id) == str(
                    candidate.get("order_id") or ""):
                log_identity_path_counts["exact_exchange_order_id"] += 1
            if present(client_id) and str(client_id) == str(
                    candidate.get("client_order_id") or ""):
                log_identity_path_counts["exact_client_order_id"] += 1
            if present(trade_id) and str(trade_id) == str(
                    candidate.get("internal_trade_id") or ""):
                log_identity_path_counts["exact_internal_trade_id"] += 1
        corroborating_log = accepted_logs[0] if len(accepted_logs) == 1 else None
        local_ts, local_ts_field = source_local_ts(source)
        api_exact = list(api_by_order.get(str(order_id or ""), []))
        canonical = canonical_identifier(order_id)
        canonical_candidates = list(api_by_canonical.get(canonical, []))
        format_candidates = [
            row for row in canonical_candidates
            if str(row.get("order_id") or "") != str(order_id or "")]
        tier1_valid = [
            row for row in api_exact
            if not strict_candidate_failures(
                source, corroborating_log, row, args.max_receipt_lag_seconds)
        ]
        client_candidates = list(
            api_by_client.get(str(client_id or ""), []))
        tier2_valid = [
            row for row in client_candidates
            if not strict_candidate_failures(
                source, corroborating_log, row, args.max_receipt_lag_seconds)
        ]
        tier3_valid, tier3_time_incompatible = causal_composite_candidates(
            source, corroborating_log, api_by_composite,
            args.max_receipt_lag_seconds,
        )
        working.append({
            "slot_id": slot_id,
            "slot": slot,
            "source": source,
            "order_id": order_id,
            "client_id": client_id,
            "trade_id": trade_id,
            "local_ts": local_ts,
            "local_ts_field": local_ts_field,
            "log_candidates": log_candidates,
            "accepted_logs": accepted_logs,
            "log_field_mismatch_counts": log_field_mismatch_counts,
            "log_identity_path_counts": log_identity_path_counts,
            "corroborating_log": corroborating_log,
            "api_exact": api_exact,
            "format_candidates": format_candidates,
            "client_candidates": client_candidates,
            "tier1_valid": tier1_valid,
            "tier2_valid": tier2_valid,
            "tier3_valid": tier3_valid,
            "tier3_time_incompatible": tier3_time_incompatible,
        })

    tier2_api_claims = Counter(
        str(row["tier2_valid"][0].get("order_id") or "")
        for row in working
        if len(row["tier2_valid"]) == 1
    )
    tier3_api_claims = Counter(
        str(row["tier3_valid"][0].get("order_id") or "")
        for row in working
        if len(row["tier3_valid"]) == 1
    )

    sanitized_rows = []
    tier_counts = Counter()
    failure_counts = Counter()
    acceptance_counts = Counter()
    collision_counts = Counter()
    for row in working:
        source = row["source"]
        join_tier = "unresolved"
        api_match = None
        if len(row["tier1_valid"]) == 1:
            join_tier = "tier1_exact_exchange_order_id"
            api_match = row["tier1_valid"][0]
        elif (
            len(row["tier2_valid"]) == 1
            and slot_clients[str(row["client_id"] or "")] == 1
            and tier2_api_claims[
                str(row["tier2_valid"][0].get("order_id") or "")] == 1
        ):
            join_tier = "tier2_exact_client_order_id"
            api_match = row["tier2_valid"][0]
        elif (
            len(row["tier3_valid"]) == 1
            and tier3_api_claims[
                str(row["tier3_valid"][0].get("order_id") or "")] == 1
        ):
            join_tier = "tier3_unique_corroborated_composite"
            api_match = row["tier3_valid"][0]
        tier_counts[join_tier] += 1

        if len(row["accepted_logs"]) == 1:
            accepted_class = "exchange_accepted_response_corroborated"
        elif len(row["accepted_logs"]) > 1:
            accepted_class = (
                "exchange_accepted_response_corroborated_multiple_receipts")
        elif row["log_candidates"]:
            accepted_class = "engine_receipt_not_proven_accepted"
        else:
            accepted_class = "no_persisted_order_placed_receipt"
        acceptance_counts[accepted_class] += 1

        failures = []
        if not present(row["order_id"]):
            failures.append("exchange_id_absent_from_slot")
        elif not row["api_exact"]:
            failures.append("exchange_id_present_but_absent_from_api")
        if row["format_candidates"]:
            failures.append("identifier_format_type_mismatch")
        all_identity_candidates = [
            *row["api_exact"], *row["client_candidates"],
            *row["format_candidates"],
        ]
        candidate_failures = {
            failure
            for candidate in all_identity_candidates
            for failure in strict_candidate_failures(
                source, row["corroborating_log"], candidate,
                args.max_receipt_lag_seconds)
        }
        failures.extend(sorted(candidate_failures))
        if row["tier3_time_incompatible"]:
            failures.append("timestamp_or_timezone_mismatch")
        if row["local_ts"] is not None:
            bounds = receipt.get("causal_time_bounds") or {}
            minimum = bounds.get("min_ts")
            maximum = bounds.get("max_ts")
            if (
                present(minimum) and present(maximum)
                and not float(minimum) <= row["local_ts"] <= float(maximum)
            ):
                failures.append("query_window_exclusion")
        if (
            not all_identity_candidates
            and not row["tier3_valid"]
            and not row["tier3_time_incompatible"]
            and not row["log_candidates"]
        ):
            failures.append("genuinely_no_corresponding_exchange_record")
        failures = sorted(set(failures))
        if join_tier != "unresolved":
            failures = []
        for failure in failures:
            if failure not in ALLOWED_FAILURE_CLASSES:
                raise BridgeError(f"unknown failure class: {failure}")
            failure_counts[failure] += 1

        collisions = []
        if len(row["api_exact"]) > 1:
            collisions.append("tier1_exchange_order_id")
        if (
            len(row["client_candidates"]) > 1
            or slot_clients[str(row["client_id"] or "")] > 1
        ):
            collisions.append("tier2_client_order_id")
        if (
            len(row["tier3_valid"]) > 1
            or (
                len(row["tier3_valid"]) == 1
                and tier3_api_claims[str(
                    row["tier3_valid"][0].get("order_id") or "")] > 1
            )
        ):
            collisions.append("tier3_composite")
        for collision in collisions:
            collision_counts[collision] += 1

        slot = row["slot"]
        source_timestamps = {
            key: {
                "present": present(source.get(key)),
                "basis": (
                    "exchange"
                    if key.startswith("exchange_")
                    or key == "evaluation_end_exchange_ts"
                    else "local"
                ),
            }
            for key in (
                "exchange_created_ts", "local_created_ts",
                "local_logged_ts", "attempt_ts",
                "evaluation_end_exchange_ts",
            )
        }
        sanitized = {
            "schema_version": SCHEMA,
            "slot_id": row["slot_id"],
            "event_id": slot.get("event_id") or source.get("event_id"),
            "ticker": slot.get("ticker") or source.get("ticker"),
            "leg": slot.get("leg") or source.get("leg"),
            "identifier_presence": {
                "internal_attempt_id": identifier_shape(
                    source.get("attempt_id")),
                "internal_trade_id": identifier_shape(
                    source.get("trade_id")),
                "exchange_order_id": identifier_shape(
                    source.get("order_id")),
                "client_order_id": identifier_shape(
                    source.get("client_order_id")),
            },
            "field_presence": {
                "event": present(source.get("event_id")),
                "ticker": present(source.get("ticker")),
                "side": present(source.get("side")),
                "action": present(source.get("action")),
                "price_cents": present(source.get("price_cents")),
                "quantity": present(source.get("quantity")),
                "timestamps": source_timestamps,
            },
            "persisted_log_proof": {
                "candidate_receipts": len(row["log_candidates"]),
                "accepted_response_receipts": len(row["accepted_logs"]),
                "classification": accepted_class,
                "independently_corroborated": (
                    row["corroborating_log"] is not None),
                "identity_path_counts": dict(sorted(
                    row["log_identity_path_counts"].items())),
                "field_mismatch_counts": dict(sorted(
                    row["log_field_mismatch_counts"].items())),
                "response_status_counts": dict(sorted(Counter(
                    str(log.get("response_status") or "missing").lower()
                    for log in row["log_candidates"]
                ).items())),
            },
            "accepted_evidence_classification": accepted_class,
            "join": {
                "tier": join_tier,
                "matched": api_match is not None,
                "tier1_exact_order_candidates": len(row["api_exact"]),
                "tier1_format_only_candidates": len(
                    row["format_candidates"]),
                "tier2_exact_client_candidates": len(
                    row["client_candidates"]),
                "tier3_compatible_composite_candidates": len(
                    row["tier3_valid"]),
                "tier3_time_incompatible_candidates": len(
                    row["tier3_time_incompatible"]),
                "collisions": collisions,
            },
            "failure_classes": failures,
            "private_identifiers_emitted": False,
        }
        sanitized_rows.append(sanitized)
        private_rows.append({
            "schema_version": SCHEMA,
            "slot_id": row["slot_id"],
            "event_id": sanitized["event_id"],
            "ticker": sanitized["ticker"],
            "leg": sanitized["leg"],
            "internal_attempt_id": source.get("attempt_id"),
            "internal_trade_id": source.get("trade_id"),
            "exchange_order_id": source.get("order_id"),
            "client_order_id": source.get("client_order_id"),
            "side": source.get("side"),
            "action": source.get("action"),
            "price_cents": source.get("price_cents"),
            "quantity": source.get("quantity"),
            "timestamps": {
                key: source.get(key)
                for key in (
                    "exchange_created_ts", "local_created_ts",
                    "local_logged_ts", "attempt_ts",
                    "evaluation_end_exchange_ts",
                )
            },
            "accepted_log_receipts": row["accepted_logs"],
            "candidate_log_receipts": row["log_candidates"],
            "api_match": api_match,
            "join_tier": join_tier,
            "failure_classes": failures,
        })

    matched = EXPECTED_SLOTS - tier_counts["unresolved"]
    raw_audit = audit_raw_pages(
        raw_pages, api_orders, api_fills, receipt)
    raw_audit["time_bounds_and_timezone"] = {
        "min_ts": receipt["causal_time_bounds"]["min_ts"],
        "max_ts": receipt["causal_time_bounds"]["max_ts"],
        "min_utc": receipt["causal_time_bounds"]["min_utc"],
        "max_utc": receipt["causal_time_bounds"]["max_utc"],
        "timezone": "UTC",
        "timestamp_rule": receipt["causal_time_bounds"]["law"],
        "bulk_orders_upper_bound": (
            "export start; exact order lookups and order-scoped fills were "
            "also made without a time filter"),
        "bulk_fills_upper_bound": "frozen validation inventory edge",
    }
    summary = {
        "schema_version": SCHEMA,
        "D": 804,
        "target_slots": EXPECTED_SLOTS,
        "join_hierarchy": [
            "tier1_exact_exchange_order_id",
            "tier2_exact_client_order_id",
            "tier3_unique_corroborated_composite",
        ],
        "max_receipt_lag_seconds": args.max_receipt_lag_seconds,
        "join_tier_counts": {
            key: tier_counts[key]
            for key in (
                "tier1_exact_exchange_order_id",
                "tier2_exact_client_order_id",
                "tier3_unique_corroborated_composite",
                "unresolved",
            )
        },
        "matched_slots": matched,
        "unresolved_slots": tier_counts["unresolved"],
        "failure_class_counts": {
            key: failure_counts[key]
            for key in sorted(ALLOWED_FAILURE_CLASSES)
        },
        "collision_counts": {
            key: collision_counts[key]
            for key in (
                "tier1_exchange_order_id",
                "tier2_client_order_id",
                "tier3_composite",
            )
        },
        "candidate_counts": {
            "tier1_exact_exchange_order_id": sum(
                len(row["api_exact"]) for row in working),
            "tier1_format_only": sum(
                len(row["format_candidates"]) for row in working),
            "tier2_exact_client_order_id": sum(
                len(row["client_candidates"]) for row in working),
            "tier3_compatible_composite": sum(
                len(row["tier3_valid"]) for row in working),
            "tier3_time_incompatible_composite": sum(
                len(row["tier3_time_incompatible"]) for row in working),
        },
        "accepted_order_evidence_counts": dict(sorted(
            acceptance_counts.items())),
        "slot_log_response_status_counts": dict(sorted(Counter(
            str(log.get("response_status") or "missing").lower()
            for row in working for log in row["accepted_logs"]
        ).items())),
        "slot_identifier_presence_counts": {
            key: sum(
                row["identifier_presence"][key]["present"]
                for row in sanitized_rows
            )
            for key in (
                "internal_attempt_id", "internal_trade_id",
                "exchange_order_id", "client_order_id",
            )
        },
        "slot_field_presence_counts": {
            key: sum(
                row["field_presence"][key] for row in sanitized_rows)
            for key in (
                "event", "ticker", "side", "action",
                "price_cents", "quantity",
            )
        },
        "validation_rerun_required": matched > 0,
        "validation_rerun_performed": False,
        "strategy_scoring_permitted": False,
        "private_identifiers_emitted": False,
        "micmay_joined": False,
    }
    representative = []
    represented = set()
    for row in sanitized_rows:
        key = (
            row["join"]["tier"],
            tuple(row["failure_classes"]),
            row["persisted_log_proof"]["classification"],
        )
        if key in represented:
            continue
        represented.add(key)
        representative.append(row)
        if len(representative) >= args.representative_limit:
            break
    output_hashes = {
        "immutable_input_hashes": {
            "slot_join_private": sha256_file(slot_join_path),
            "source_orders_private": sha256_file(source_orders_path),
            "source_mismatches_private": sha256_file(
                source_mismatches_path),
            "api_orders_private": sha256_file(api_orders_path),
            "api_fills_private": sha256_file(api_fills_path),
            "raw_api_pages_private": sha256_file(raw_pages_path),
            "export_receipt_private": sha256_file(receipt_path),
        },
        "log_snapshot": log_audit,
        "raw_export_audit": raw_audit,
    }

    private_path = output / "IDENTITY_BRIDGE.private.jsonl"
    sanitized_path = output / "IDENTITY_BRIDGE.sanitized.jsonl"
    write_jsonl(private_path, private_rows, mode=0o400)
    write_jsonl(sanitized_path, sanitized_rows, mode=0o600)
    write_json(
        output / "IDENTITY_BRIDGE_SUMMARY.sanitized.json",
        summary,
        mode=0o600,
    )
    write_json(
        output / "IDENTITY_BRIDGE_EXPORT_AUDIT.sanitized.json",
        output_hashes,
        mode=0o600,
    )
    write_json(
        output / "IDENTITY_BRIDGE_PROOFS.sanitized.json",
        {
            "schema_version": SCHEMA,
            "representative_count": len(representative),
            "representative_proofs": representative,
            "selection": (
                "first slot in deterministic slot order for each distinct "
                "join/failure/acceptance evidence class"),
            "private_identifiers_emitted": False,
        },
        mode=0o600,
    )
    print(json.dumps({
        "D": 804,
        "target_slots": EXPECTED_SLOTS,
        "matched_slots": matched,
        "unresolved_slots": tier_counts["unresolved"],
        "join_tier_counts": dict(sorted(tier_counts.items())),
        "validation_rerun_required": matched > 0,
        "private_identifiers_printed": False,
    }, sort_keys=True))
    return 3 if matched > 0 else 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--slot-join", required=True)
    root.add_argument("--source-orders", required=True)
    root.add_argument("--source-mismatches", required=True)
    root.add_argument("--api-orders", required=True)
    root.add_argument("--api-fills", required=True)
    root.add_argument("--raw-pages", required=True)
    root.add_argument("--export-receipt", required=True)
    root.add_argument("--log-dir", required=True)
    root.add_argument("--active-log-prefix-bytes", type=int, required=True)
    root.add_argument("--output-dir", required=True)
    root.add_argument("--max-receipt-lag-seconds", type=float, default=60.0)
    root.add_argument("--representative-limit", type=int, default=12)
    return root


def main() -> int:
    return forensic(parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
