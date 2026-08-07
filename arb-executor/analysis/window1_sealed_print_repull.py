#!/usr/bin/env python3
"""Capture-class public-trade re-pull for the sealed Window-1 exam.

This uses the same unauthenticated, per-ticker, fully paginated public trade
endpoint and canonical row function as ``window1_public_tape_export.py``.
It intentionally accepts only the frozen 171-event / 342-leg declaration.
Raw responses and normalized prints stay outside Git; a hash-only receipt is
safe to commit.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import window1_public_tape_export as public_export
import window1_nightly_reconciliation as nightly


VERSION = "window1-sealed-171-public-trade-repull-v1"
SEALED_LIST_SHA256 = (
    "06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313"
)


class SealedRepullError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_population(declaration_path: Path, event_list_path: Path):
    list_bytes = event_list_path.read_bytes()
    if hashlib.sha256(list_bytes).hexdigest() != SEALED_LIST_SHA256:
        raise SealedRepullError("sealed event-list hash mismatch")
    event_ids = [row for row in list_bytes.decode().splitlines() if row]
    declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
    by_id = {row["event_id"]: row for row in declaration.get("events", [])}
    events = [by_id.get(event_id) for event_id in event_ids]
    if len(event_ids) != 171 or any(row is None for row in events):
        raise SealedRepullError("sealed 171-event identity mismatch")
    tickers = []
    ticker_to_event = {}
    for event in events:
        legs = event.get("legs") or []
        if len(legs) != 2:
            raise SealedRepullError(f"not two legs: {event['event_id']}")
        for leg in legs:
            ticker = str(leg.get("ticker") or "")
            if not ticker or ticker in ticker_to_event:
                raise SealedRepullError("ticker identity is absent or duplicated")
            tickers.append(ticker)
            ticker_to_event[ticker] = event["event_id"]
    if len(tickers) != 342:
        raise SealedRepullError("sealed leg denominator is not 342")
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


def reconcile_sample(
    events: list[dict[str, Any]], normalized_by_ticker: dict[str, dict[str, dict[str, Any]]],
    sample_size: int,
) -> dict[str, Any]:
    sample = nightly.deterministic_sample(
        events, "SEALED-171-" + SEALED_LIST_SHA256, sample_size
    )
    rows = []
    for event in sample:
        ours = {}
        exchange = {}
        for leg in event["legs"]:
            ticker = leg["ticker"]
            for trade_id, row in normalized_by_ticker[ticker].items():
                if trade_id in ours:
                    raise SealedRepullError("sample normalized trade repeats")
                ours[trade_id] = nightly_shape(row)
            for row in nightly.fetch_ticker(ticker):
                if row["trade_id"] in exchange:
                    raise SealedRepullError("sample exchange trade repeats")
                exchange[row["trade_id"]] = row
        counts = nightly.compare(ours, exchange)
        mismatch = sum(counts[key] for key in (
            "ex_not_ours", "ours_not_ex", "price_mm", "size_mm", "side_mm"
        ))
        rows.append({
            "event_id": event["event_id"],
            **counts,
            "verdict": "PRINTS_FAITHFUL" if mismatch == 0 else "DEFECT",
        })
    verdicts = Counter(row["verdict"] for row in rows)
    return {
        "method_commit": "938dca474e8bc4d96b17095e2aaa7cbb2fe97a87",
        "method_source": "arb-executor/analysis/window1_nightly_reconciliation.py",
        "sample_N": sample_size,
        "sample_seed": "SHA256(SEALED-171-<event-list-sha256>)",
        "sample_events": [row["event_id"] for row in rows],
        "sample_event_list_sha256": hashlib.sha256(
            ("\n".join(row["event_id"] for row in rows) + "\n").encode()
        ).hexdigest(),
        "verdicts": dict(sorted(verdicts.items())),
        "totals": {key: sum(row[key] for row in rows) for key in (
            "exchange_trades", "our_prints", "ex_not_ours", "ours_not_ex",
            "price_mm", "size_mm", "side_mm",
        )},
        "per_event": rows,
        "pass": verdicts.get("PRINTS_FAITHFUL", 0) == sample_size,
    }


def run(args: argparse.Namespace) -> int:
    declaration_path = Path(args.sealed_declaration).resolve()
    event_list_path = Path(args.event_list).resolve()
    output = Path(args.output).resolve()
    raw_dir = output / "raw"
    normalized_path = output / "prints.jsonl"
    private_manifest_path = output / "PRIVATE_REPULL_MANIFEST.json"
    receipt_path = Path(args.receipt).resolve()
    events, tickers, ticker_to_event, list_bytes = load_population(
        declaration_path, event_list_path
    )
    output.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    results = []
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {
            pool.submit(
                public_export.fetch_ticker,
                ticker,
                public_export.DEFAULT_ENDPOINT,
                raw_dir,
                page_limit=1000,
                attempts=8,
                timeout_seconds=30,
                resume=args.resume,
            ): ticker for ticker in tickers
        }
        for completed, future in enumerate(
            concurrent.futures.as_completed(future_map), 1
        ):
            ticker = future_map[future]
            try:
                results.append(future.result())
            except Exception as exc:
                failures.append({"ticker": ticker, "error": str(exc)})
            if completed % 25 == 0 or completed == len(tickers):
                print(compact({"completed": completed, "total": len(tickers),
                               "failures": len(failures)}), flush=True)
    if failures:
        (output / "REPULL_FAILURES.json").write_bytes(canonical({
            "schema_version": VERSION + "-failures", "failures": failures,
        }))
        raise SealedRepullError(f"incomplete re-pull: {len(failures)} tickers")

    seen: dict[str, str] = {}
    per_leg = []
    normalized_by_ticker: dict[str, dict[str, dict[str, Any]]] = {}
    total_raw = total_zero = total_positive = duplicates = 0
    with normalized_path.open("w", encoding="utf-8", newline="\n") as handle:
        for result in sorted(results, key=lambda row: row["ticker"]):
            ticker_rows = []
            ticker_map = {}
            for row in raw_rows(result):
                total_raw += 1
                identity = row["trade_id"]
                line = compact(row)
                if identity in seen:
                    if seen[identity] != line:
                        raise SealedRepullError(
                            f"conflicting duplicate trade_id: {identity}"
                        )
                    duplicates += 1
                    continue
                seen[identity] = line
                ticker_rows.append(row)
                ticker_map[identity] = row
                handle.write(line + "\n")
                total_zero += row["size"] == 0
                total_positive += row["size"] > 0
            normalized_by_ticker[result["ticker"]] = ticker_map
            stamps = [row["exchange_ts"] for row in ticker_rows]
            per_leg.append({
                "event_id": ticker_to_event[result["ticker"]],
                "ticker": result["ticker"],
                "raw_rows": result["trade_count"],
                "canonical_rows": len(ticker_rows),
                "positive_size_rows": sum(row["size"] > 0 for row in ticker_rows),
                "zero_size_rows": sum(row["size"] == 0 for row in ticker_rows),
                "seller_aggressed_rows": sum(row.get("taker_side") == "no" for row in ticker_rows),
                "buyer_aggressed_rows": sum(row.get("taker_side") == "yes" for row in ticker_rows),
                "unknown_taker_side_rows": sum(row.get("taker_side") not in {"yes", "no"} for row in ticker_rows),
                "first_exchange_timestamp": min(stamps) if stamps else None,
                "last_exchange_timestamp": max(stamps) if stamps else None,
                "pages": result["page_count"],
                "terminal_cursor_empty": result["terminal_cursor_empty"],
                "raw_sha256": result["raw_sha256"],
                "raw_bytes": result["raw_bytes"],
                "resumed": result["resumed"],
            })

    sample = reconcile_sample(events, normalized_by_ticker, args.sample_size)
    if not sample["pass"]:
        raise SealedRepullError("N=20 nightly-method reconciliation failed")
    raw_hash_set = hashlib.sha256(
        "\n".join(f"{row['ticker']} {row['raw_sha256']}" for row in per_leg).encode()
    ).hexdigest()
    private_manifest = {
        "schema_version": VERSION + "-private-manifest",
        "capture_class": True,
        "touch_class": False,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "event_N": 171,
        "leg_N": 342,
        "event_list_sha256": hashlib.sha256(list_bytes).hexdigest(),
        "endpoint": public_export.DEFAULT_ENDPOINT,
        "authentication": "none_public_endpoint",
        "pagination": {
            "page_limit": 1000,
            "pages": sum(row["pages"] for row in per_leg),
            "all_terminal_cursors_empty": all(row["terminal_cursor_empty"] for row in per_leg),
            "failed_tickers": 0,
        },
        "counts": {
            "raw_rows": total_raw,
            "canonical_rows": len(seen),
            "duplicate_rows_removed": duplicates,
            "positive_size_rows": total_positive,
            "zero_size_rows": total_zero,
        },
        "artifacts": {
            "normalized_prints": {
                "path": str(normalized_path),
                "sha256": sha256_file(normalized_path),
                "bytes": normalized_path.stat().st_size,
            },
            "raw_ticker_files": 342,
            "raw_hash_set_sha256": raw_hash_set,
            "raw_total_bytes": sum(row["raw_bytes"] for row in per_leg),
        },
        "per_leg": per_leg,
        "nightly_method_spot_reconciliation": sample,
        "forbidden_access": {
            "account": 0, "orders": 0, "positions": 0, "trading": 0,
            "strategy": 0, "scorer": 0,
        },
    }
    private_manifest_path.write_bytes(canonical(private_manifest))
    receipt = {
        **private_manifest,
        "private_paths_redacted": True,
        "artifacts": {
            **private_manifest["artifacts"],
            "normalized_prints": {
                key: value for key, value in private_manifest["artifacts"]["normalized_prints"].items()
                if key != "path"
            },
            "private_manifest_sha256": sha256_file(private_manifest_path),
            "private_manifest_bytes": private_manifest_path.stat().st_size,
        },
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_bytes(canonical(receipt))
    print(compact({
        "status": "PASS", "events": 171, "legs": 342,
        "prints": len(seen), "prints_sha256": sha256_file(normalized_path),
        "spot_reconciliation": sample["verdicts"],
    }))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sealed-declaration", required=True)
    parser.add_argument("--event-list", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--resume", action="store_true")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
