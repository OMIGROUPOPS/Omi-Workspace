#!/usr/bin/env python3
"""Nightly N=20 public-trade reconciliation for the frozen Window-1 tape.

The job is capture integrity only.  It reads no account, order, position,
strategy, or scorer surface.
"""

from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile
import time
from typing import Any, Iterable
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo


VERSION = "window1-nightly-reconciliation-938dca47-v1"
ENDPOINT = "https://api.elections.kalshi.com/trade-api/v2/markets/trades"
ET = ZoneInfo("America/New_York")


class ReconciliationError(RuntimeError):
    """The nightly reconciliation contract failed closed."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def epoch(value: Any) -> float:
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReconciliationError(f"invalid timestamp {value!r}") from exc
    if parsed.tzinfo is None:
        raise ReconciliationError("timestamp is timezone-free")
    return parsed.timestamp()


def size_text(value: Any) -> str:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ReconciliationError(f"invalid size {value!r}") from exc
    if not parsed.is_finite() or parsed < 0:
        raise ReconciliationError(f"invalid size {value!r}")
    return format(parsed.normalize(), "f")


def public_trade(row: dict[str, Any], ticker: str) -> dict[str, Any]:
    trade_id = str(row.get("trade_id") or "")
    if not trade_id or str(row.get("ticker") or "") != ticker:
        raise ReconciliationError("public trade identity mismatch")
    price_raw = row.get("yes_price_dollars")
    price = int(Decimal(str(price_raw)) * 100) if price_raw not in (None, "") \
        else int(row.get("yes_price"))
    return {
        "trade_id": trade_id,
        "ticker": ticker,
        "ts": epoch(row.get("created_time")),
        "price": price,
        "size": size_text(row.get("count_fp", row.get("count", 0))),
        "side": str(row.get("taker_side") or ""),
    }


def stored_trade(row: dict[str, Any]) -> dict[str, Any]:
    trade_id = str(row.get("trade_id") or row.get("receipt_id") or "")
    if not trade_id or row.get("true_print") is not True:
        raise ReconciliationError("stored print identity or truth flag invalid")
    return {
        "trade_id": trade_id,
        "ticker": str(row.get("ticker") or ""),
        "ts": epoch(row.get("exchange_ts")),
        "price": int(row.get("price_cents")),
        "size": size_text(row.get("size")),
        "side": str(row.get("taker_side") or ""),
    }


def request_json(url: str, attempts: int = 5) -> dict[str, Any]:
    last: Exception | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json",
                     "User-Agent": f"omi-nightly-reconcile/{VERSION}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                value = json.loads(response.read())
            if not isinstance(value, dict):
                raise ReconciliationError("trade endpoint returned non-object")
            return value
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                json.JSONDecodeError, ReconciliationError) as exc:
            last = exc
            retryable = not isinstance(exc, urllib.error.HTTPError) or (
                exc.code == 429 or 500 <= exc.code < 600
            )
            if not retryable or attempt + 1 == attempts:
                break
            retry_after = exc.headers.get("Retry-After") \
                if isinstance(exc, urllib.error.HTTPError) else None
            delay = float(retry_after) if retry_after and retry_after.isdigit() \
                else min(30.0, (2 ** attempt) + random.random())
            time.sleep(delay)
    raise ReconciliationError(f"public trade GET failed: {last}")


def fetch_ticker(ticker: str) -> list[dict[str, Any]]:
    rows = []
    cursor = ""
    seen = set()
    for _page in range(100):
        query = {"ticker": ticker, "limit": "1000"}
        if cursor:
            query["cursor"] = cursor
        payload = request_json(ENDPOINT + "?" + urllib.parse.urlencode(query))
        page = payload.get("trades")
        if not isinstance(page, list):
            raise ReconciliationError(f"{ticker} response lacks trades[]")
        rows.extend(public_trade(row, ticker) for row in page)
        cursor = str(payload.get("cursor") or "")
        if not cursor:
            return rows
        if cursor in seen:
            raise ReconciliationError(f"{ticker} cursor repeated")
        seen.add(cursor)
    raise ReconciliationError(f"{ticker} pagination exceeded 100 pages")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def deterministic_sample(events: Iterable[dict[str, Any]], seed: str,
                         count: int) -> list[dict[str, Any]]:
    ordered = sorted(events, key=lambda row: row["event_id"])
    if len(ordered) < count:
        raise ReconciliationError("eligible event population is below sample N")
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    return sorted(rng.sample(ordered, count), key=lambda row: row["event_id"])


def load_stored(path: Path, tickers: set[str], bounds: dict[str, tuple[float, float]]) -> dict[str, dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    ticker_bytes = {ticker.encode() for ticker in tickers}
    ticker_pattern = re.compile(rb'"ticker"\s*:\s*"([^"]+)"')
    rows: dict[str, dict[str, Any]] = {}
    with opener(path, "rb") as handle:
        for raw in handle:
            match = ticker_pattern.search(raw)
            if not match or match.group(1) not in ticker_bytes:
                continue
            row = stored_trade(json.loads(raw))
            ticker = row["ticker"]
            if ticker not in tickers:
                continue
            left, right = bounds[ticker]
            if not left <= row["ts"] <= right:
                continue
            if row["trade_id"] in rows:
                raise ReconciliationError("stored trade_id repeats")
            rows[row["trade_id"]] = row
    return rows


def compare(ours: dict[str, dict[str, Any]], exchange: dict[str, dict[str, Any]]) -> dict[str, int]:
    ours_ids = set(ours)
    exchange_ids = set(exchange)
    common = ours_ids & exchange_ids
    return {
        "exchange_trades": len(exchange),
        "our_prints": len(ours),
        "ex_not_ours": len(exchange_ids - ours_ids),
        "ours_not_ex": len(ours_ids - exchange_ids),
        "price_mm": sum(ours[key]["price"] != exchange[key]["price"] for key in common),
        "size_mm": sum(ours[key]["size"] != exchange[key]["size"] for key in common),
        "side_mm": sum(ours[key]["side"] != exchange[key]["side"] for key in common),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True)
    parser.add_argument("--boundaries", required=True)
    parser.add_argument("--prints", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--seed-date")
    args = parser.parse_args()
    events_path = Path(args.events).resolve()
    boundaries_path = Path(args.boundaries).resolve()
    prints_path = Path(args.prints).resolve()
    output = Path(args.output_dir).resolve()
    for path in (events_path, boundaries_path, prints_path):
        if not path.is_file():
            raise ReconciliationError(f"input absent: {path}")
    events = load_jsonl(events_path)
    boundaries = {
        row["event_id"]: row for row in load_jsonl(boundaries_path)
    }
    if len(events) != 804 or len(boundaries) != 804:
        raise ReconciliationError("frozen D=804 identity failed")
    eligible = []
    for event in events:
        event_id = event["event_id"]
        boundary = boundaries.get(event_id)
        legs = event.get("legs") or []
        if (not boundary or len(legs) != 2
                or boundary.get("positive_window1_provable") is not True
                or boundary.get("guarded_cutoff_ts") is None):
            continue
        scheduled = epoch(event["scheduled_start_exchange_ts"])
        eligible.append({
            **event,
            "left": scheduled - 8 * 3600,
            "right": float(boundary["guarded_cutoff_ts"]),
        })
    seed_date = args.seed_date or dt.datetime.now(ET).date().isoformat()
    sample = deterministic_sample(eligible, seed_date, args.sample_size)
    tickers = {leg["ticker"] for event in sample for leg in event["legs"]}
    bounds = {
        leg["ticker"]: (event["left"], event["right"])
        for event in sample for leg in event["legs"]
    }
    ours = load_stored(prints_path, tickers, bounds)
    exchange = {}
    unpullable = []
    for ticker in sorted(tickers):
        try:
            for row in fetch_ticker(ticker):
                left, right = bounds[ticker]
                if left <= row["ts"] <= right:
                    if row["trade_id"] in exchange:
                        raise ReconciliationError("exchange trade_id repeats")
                    exchange[row["trade_id"]] = row
        except Exception as exc:
            unpullable.append({"ticker": ticker, "error": type(exc).__name__,
                               "detail": str(exc)[:240]})
    per_game = []
    for event in sample:
        event_tickers = {leg["ticker"] for leg in event["legs"]}
        ours_event = {key: row for key, row in ours.items()
                      if row["ticker"] in event_tickers}
        exchange_event = {key: row for key, row in exchange.items()
                          if row["ticker"] in event_tickers}
        counts = compare(ours_event, exchange_event)
        event_unpullable = [row for row in unpullable
                            if row["ticker"] in event_tickers]
        mismatch = sum(counts[key] for key in (
            "ex_not_ours", "ours_not_ex", "price_mm", "size_mm", "side_mm"
        ))
        per_game.append({
            "event_id": event["event_id"],
            "guarded_left_ts": event["left"],
            "guarded_right_ts": event["right"],
            **counts,
            "unpullable": event_unpullable,
            "verdict": "PRINTS_FAITHFUL" if not mismatch and not event_unpullable
                       else "UNPULLABLE" if event_unpullable else "DEFECT",
        })
    verdicts = Counter(row["verdict"] for row in per_game)
    status = "PASS" if verdicts["PRINTS_FAITHFUL"] == args.sample_size else "ALARM"
    result = {
        "schema_version": VERSION,
        "status": status,
        "seed_date_et": seed_date,
        "sample_size": args.sample_size,
        "sample_event_list_sha256": hashlib.sha256(
            ("\n".join(row["event_id"] for row in sample) + "\n").encode()
        ).hexdigest(),
        "sample_events": [row["event_id"] for row in sample],
        "verdicts": dict(sorted(verdicts.items())),
        "totals": {key: sum(row[key] for row in per_game) for key in (
            "exchange_trades", "our_prints", "ex_not_ours", "ours_not_ex",
            "price_mm", "size_mm", "side_mm"
        )},
        "per_game": per_game,
        "law": {
            "spec_commit": "938dca474e8bc4d96b17095e2aaa7cbb2fe97a87",
            "N": 20,
            "seed": "ET calendar date",
            "window": "scheduled_start_minus_8h_through_guarded_cutoff_inclusive",
            "identity": "exchange_trade_id",
            "alarm_on_first_nonzero": True,
            "escalation": "freeze_downstream_and_run_full_804_reconciliation",
        },
        "inputs": {
            "events_sha256": sha256_file(events_path),
            "boundaries_sha256": sha256_file(boundaries_path),
            "prints_sha256": sha256_file(prints_path),
        },
        "forbidden_access": {
            "account": 0, "orders": 0, "positions": 0, "trading": 0,
            "strategy": 0, "scorer": 0,
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    dated = output / f"RECONCILIATION_{seed_date}.json"
    atomic_json(dated, result)
    atomic_json(output / "LATEST.json", result)
    if status != "PASS":
        atomic_json(output / f"ALARM_{seed_date}.json", result)
        subprocess.run(["logger", "-p", "user.err", "-t",
                        "window1-reconciliation", compact({
                            "status": status, "seed_date": seed_date,
                            "verdicts": result["verdicts"],
                        })], check=False)
    print(compact({"status": status, "seed_date": seed_date,
                   "verdicts": result["verdicts"],
                   "totals": result["totals"]}))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
