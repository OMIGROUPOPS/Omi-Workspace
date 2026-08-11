#!/usr/bin/env python3
"""Public exchange-print re-pull for a frozen V47 exam population.

The normalized rows and the N=20 spot reconciliation use the exact canonical
dev export and nightly-reconciliation adapters.  This is capture-class input
preparation: it invokes no policy and emits no score row.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

import window1_nightly_reconciliation as nightly
import window1_public_tape_export as public_export


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_population(declaration_path: Path, event_list_path: Path):
    list_bytes = event_list_path.read_bytes()
    list_hash = hashlib.sha256(list_bytes).hexdigest()
    ids = [row for row in list_bytes.decode().splitlines() if row]
    declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
    if declaration.get("event_list_sha256") != list_hash or declaration.get("N") != len(ids):
        raise RuntimeError("population declaration/list mismatch")
    by_id = {row["event_id"]: row for row in declaration["events"]}
    events = [by_id.get(event_id) for event_id in ids]
    if any(row is None for row in events):
        raise RuntimeError("event missing from declaration")
    tickers = []
    ticker_to_event = {}
    for event in events:
        if len(event["legs"]) != 2:
            raise RuntimeError(f"not two legs {event['event_id']}")
        for leg in event["legs"]:
            ticker = leg["ticker"]
            if ticker in ticker_to_event:
                raise RuntimeError(f"duplicate ticker {ticker}")
            tickers.append(ticker)
            ticker_to_event[ticker] = event["event_id"]
    return events, sorted(tickers), ticker_to_event, list_bytes


def raw_rows(result: dict[str, Any]):
    with gzip.open(result["raw_path"], "rt", encoding="utf-8") as handle:
        pages = json.load(handle)
    for page in pages:
        for raw in page["response"]["trades"]:
            yield public_export.canonical_trade(raw, result["ticker"])


def nightly_shape(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "trade_id": row["trade_id"],
        "ticker": row["ticker"],
        "ts": nightly.epoch(row["exchange_ts"]),
        "price": int(row["price_cents"]),
        "size": nightly.size_text(row["size"]),
        "side": str(row.get("taker_side") or ""),
    }


def reconcile(sample, normalized_by_ticker, right_by_ticker, event_list_hash: str, sample_size: int):
    rows = []
    for event in sample:
        ours = {}
        exchange = {}
        for leg in event["legs"]:
            ticker = leg["ticker"]
            for trade_id, row in normalized_by_ticker[ticker].items():
                ours[trade_id] = nightly_shape(row)
            for row in nightly.fetch_ticker(ticker):
                if row["ts"] <= right_by_ticker[ticker]:
                    exchange[row["trade_id"]] = row
        counts = nightly.compare(ours, exchange)
        mismatch = sum(counts[key] for key in ("ex_not_ours", "ours_not_ex", "price_mm", "size_mm", "side_mm"))
        rows.append({"event_id": event["event_id"], **counts, "verdict": "PRINTS_FAITHFUL" if mismatch == 0 else "DEFECT"})
    verdicts = Counter(row["verdict"] for row in rows)
    return {
        "method_commit": "938dca474e8bc4d96b17095e2aaa7cbb2fe97a87",
        "method_source": "arb-executor/analysis/window1_nightly_reconciliation.py",
        "sample_N": sample_size,
        "sample_seed": "SHA256(V47-SEALED-EXAM-<event-list-sha256>)",
        "sample_events": [row["event_id"] for row in rows],
        "verdicts": dict(sorted(verdicts.items())),
        "totals": {key: sum(row[key] for row in rows) for key in ("exchange_trades", "our_prints", "ex_not_ours", "ours_not_ex", "price_mm", "size_mm", "side_mm")},
        "per_event": rows,
        "pass": verdicts.get("PRINTS_FAITHFUL", 0) == sample_size,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    declaration = Path(args.population_declaration).resolve()
    event_list = Path(args.event_list).resolve()
    boundary_path = Path(args.boundary_ledger).resolve()
    output = Path(args.output).resolve()
    receipt_path = Path(args.receipt).resolve()
    raw_dir = output / "raw"
    normalized_path = output / "prints.jsonl"
    events, tickers, ticker_to_event, list_bytes = load_population(declaration, event_list)
    event_list_hash = hashlib.sha256(list_bytes).hexdigest()
    boundaries = {row["event_id"]: row for row in read_jsonl(boundary_path)}
    if set(boundaries) != {event["event_id"] for event in events}:
        raise RuntimeError("boundary/event population mismatch")
    right_by_ticker = {
        leg["ticker"]: float(boundaries[event["event_id"]]["right_edge_epoch"])
        for event in events for leg in event["legs"]
    }
    output.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    sample = nightly.deterministic_sample(events, "V47-SEALED-EXAM-" + event_list_hash, args.sample_size)
    sample_tickers = {leg["ticker"] for event in sample for leg in event["legs"]}

    results = []
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(public_export.fetch_ticker, ticker, public_export.DEFAULT_ENDPOINT, raw_dir, page_limit=1000, attempts=8, timeout_seconds=30, resume=args.resume): ticker
            for ticker in tickers
        }
        for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
            ticker = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                failures.append({"ticker": ticker, "error": str(exc)})
            if completed % 25 == 0 or completed == len(tickers):
                print(compact({"completed": completed, "total": len(tickers), "failures": len(failures)}), flush=True)
    if failures:
        (output / "REPULL_FAILURES.json").write_bytes(canonical({"failures": failures}))
        raise RuntimeError(f"incomplete public print re-pull: {len(failures)}")

    identity_db = output / "trade_identity.sqlite"
    if identity_db.exists():
        raise RuntimeError(f"dedupe database already exists: {identity_db}")
    db = sqlite3.connect(identity_db)
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.execute("PRAGMA temp_store=FILE")
    db.execute("CREATE TABLE identities (trade_id TEXT PRIMARY KEY, line_sha256 BLOB NOT NULL) WITHOUT ROWID")
    per_leg = []
    normalized_by_ticker = {}
    raw_count = canonical_count = duplicates = positive = zero = after_boundary = 0
    try:
        with db, normalized_path.open("w", encoding="utf-8", newline="\n") as handle:
            for result in sorted(results, key=lambda row: row["ticker"]):
                ticker_map = {}
                ticker_count = ticker_positive = ticker_zero = ticker_seller = ticker_buyer = ticker_unknown = 0
                first_stamp = last_stamp = None
                for row in raw_rows(result):
                    raw_count += 1
                    if nightly.epoch(row["exchange_ts"]) > right_by_ticker[result["ticker"]]:
                        after_boundary += 1
                        continue
                    identity = row["trade_id"]
                    line = compact(row)
                    line_digest = hashlib.sha256(line.encode()).digest()
                    inserted = db.execute(
                        "INSERT OR IGNORE INTO identities(trade_id,line_sha256) VALUES (?,?)",
                        (identity, line_digest),
                    ).rowcount
                    if not inserted:
                        existing = db.execute("SELECT line_sha256 FROM identities WHERE trade_id=?", (identity,)).fetchone()
                        if existing is None or existing[0] != line_digest:
                            raise RuntimeError(f"conflicting duplicate trade {identity}")
                        duplicates += 1
                        continue
                    canonical_count += 1
                    ticker_count += 1
                    handle.write(line + "\n")
                    positive += row["size"] > 0
                    zero += row["size"] == 0
                    ticker_positive += row["size"] > 0
                    ticker_zero += row["size"] == 0
                    ticker_seller += row.get("taker_side") == "no"
                    ticker_buyer += row.get("taker_side") == "yes"
                    ticker_unknown += row.get("taker_side") not in {"yes", "no"}
                    stamp = row["exchange_ts"]
                    first_stamp = stamp if first_stamp is None else min(first_stamp, stamp)
                    last_stamp = stamp if last_stamp is None else max(last_stamp, stamp)
                    if result["ticker"] in sample_tickers:
                        ticker_map[identity] = row
                if result["ticker"] in sample_tickers:
                    normalized_by_ticker[result["ticker"]] = ticker_map
                per_leg.append({
                    "event_id": ticker_to_event[result["ticker"]],
                    "ticker": result["ticker"],
                    "raw_rows": result["trade_count"],
                    "canonical_rows": ticker_count,
                    "positive_size_rows": ticker_positive,
                    "zero_size_rows": ticker_zero,
                    "seller_aggressed_rows": ticker_seller,
                    "buyer_aggressed_rows": ticker_buyer,
                    "unknown_taker_side_rows": ticker_unknown,
                    "first_exchange_timestamp": first_stamp,
                    "last_exchange_timestamp": last_stamp,
                    "pages": result["page_count"],
                    "terminal_cursor_empty": result["terminal_cursor_empty"],
                    "raw_sha256": result["raw_sha256"],
                    "raw_bytes": result["raw_bytes"],
                    "resumed": result["resumed"],
                })
    finally:
        db.close()
    sample = reconcile(sample, normalized_by_ticker, right_by_ticker, event_list_hash, args.sample_size)
    if not sample["pass"]:
        raise RuntimeError("N=20 nightly-method reconciliation failed")
    manifest = {
        "schema_version": "window1-v47-sealed-exam-public-print-repull-v1",
        "capture_class": True,
        "touch_class": False,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "event_N": len(events),
        "leg_N": len(tickers),
        "event_list_sha256": event_list_hash,
        "boundary_ledger": {"sha256": sha_file(boundary_path), "bytes": boundary_path.stat().st_size},
        "endpoint": public_export.DEFAULT_ENDPOINT,
        "adapter_sources": {
            "canonical_public_print_export": {"path": str(Path(public_export.__file__).resolve()), "sha256": sha_file(Path(public_export.__file__).resolve())},
            "nightly_reconciliation": {"path": str(Path(nightly.__file__).resolve()), "sha256": sha_file(Path(nightly.__file__).resolve()), "commit": "938dca474e8bc4d96b17095e2aaa7cbb2fe97a87"},
        },
        "authentication": "none_public_endpoint",
        "pagination": {"pages": sum(row["pages"] for row in per_leg), "all_terminal_cursors_empty": all(row["terminal_cursor_empty"] for row in per_leg), "failed_tickers": 0},
        "counts": {"raw_rows": raw_count, "canonical_rows_through_hard_edge": canonical_count, "post_boundary_rows_excluded": after_boundary, "duplicates_removed": duplicates, "positive_size_rows": positive, "zero_size_rows": zero},
        "canonical_scope": "ALL_TRUE_EXCHANGE_PRINTS_AT_OR_BEFORE_EACH_EVENT_FROZEN_HARD_PRE_BELL_RIGHT_EDGE",
        "memory_bound": {"dedupe": "SQLITE_DISK_BACKED_EXACT_TRADE_ID_AND_LINE_HASH", "in_memory_canonical_rows": "N20_SAMPLE_TICKERS_ONLY"},
        "normalized_prints": {"sha256": sha_file(normalized_path), "bytes": normalized_path.stat().st_size},
        "raw_ticker_files": len(tickers),
        "raw_total_bytes": sum(row["raw_bytes"] for row in per_leg),
        "per_leg": per_leg,
        "nightly_method_spot_reconciliation": sample,
        "forbidden_access": {"policy": 0, "score_rows": 0, "account": 0, "orders": 0, "positions": 0, "trading": 0},
    }
    (output / "PRIVATE_REPULL_MANIFEST.json").write_bytes(canonical(manifest))
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_bytes(canonical({**manifest, "private_paths_redacted": True}))
    return {"status": "PASS", "events": len(events), "legs": len(tickers), "prints": canonical_count, "prints_sha256": sha_file(normalized_path), "spot_reconciliation": sample["verdicts"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population-declaration", required=True)
    parser.add_argument("--event-list", required=True)
    parser.add_argument("--boundary-ledger", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--resume", action="store_true")
    result = run(parser.parse_args())
    print(compact(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
