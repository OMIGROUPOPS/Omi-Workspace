#!/usr/bin/env python3
"""Materialize capture-class top-five tapes from the sealed WS recorder.

This utility is deliberately policy-free.  It reconstructs the same YES/NO
order book carried by ``ws_depth_recorder.py`` and emits one deterministic
CSV gzip per registry ticker.  A ticker is admission-eligible only after a
snapshot was observed in the retained archive; a delta-only prefix is emitted
for audit but is explicitly marked non-authoritative in the manifest.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ET = dt.timezone(dt.timedelta(hours=-4))
HEADER = ["ts_et"] + [
    value
    for level in range(1, 6)
    for value in (f"bid_{level}", f"bid_{level}_sz")
] + [
    value
    for level in range(1, 6)
    for value in (f"ask_{level}", f"ask_{level}_sz")
] + ["mid", "bid_depth_5", "ask_depth_5", "depth_ratio", "last_trade"]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cent(value: Any) -> int | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    result = round(number * 100 if number < 1 else number)
    return int(result) if 0 <= result <= 100 else None


def quantity(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def source_epoch(row: dict[str, Any]) -> float | None:
    value = row.get("t")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def timestamp_et(epoch: float) -> str:
    return dt.datetime.fromtimestamp(epoch, ET).strftime("%Y-%m-%d %I:%M:%S %p")


class TapeWriter:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.raw = path.open("wb")
        self.gzip = gzip.GzipFile(filename="", mode="wb", fileobj=self.raw, mtime=0, compresslevel=9)
        self.text = io.TextIOWrapper(self.gzip, encoding="utf-8", newline="")
        self.csv = csv.writer(self.text, lineterminator="\n")
        self.csv.writerow(HEADER)
        self.rows = 0

    def write(self, row: list[Any]) -> None:
        self.csv.writerow(row)
        self.rows += 1

    def close(self) -> None:
        self.text.flush()
        self.text.detach()
        self.gzip.close()
        self.raw.close()


def load_registry(path: Path) -> tuple[list[dict[str, Any]], set[str]]:
    events = []
    tickers: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            events.append(row)
            tickers.update(str(ticker) for ticker in row.get("tickers", []))
    return events, tickers


def apply_book(message: dict[str, Any], books: dict[str, dict[str, dict[int, float]]]) -> tuple[str | None, bool]:
    kind = message.get("type")
    body = message.get("msg")
    if not isinstance(body, dict):
        return None, False
    ticker = body.get("market_ticker")
    if not ticker:
        return None, False
    snapshot = kind == "orderbook_snapshot"
    if snapshot:
        book = {"yes": {}, "no": {}}
        for side in ("yes", "no"):
            levels = body.get(f"{side}_dollars_fp") or body.get(side) or []
            for level in levels:
                if not isinstance(level, (list, tuple)) or len(level) < 2:
                    continue
                price = cent(level[0])
                size = quantity(level[1])
                if price is not None and size is not None:
                    book[side][price] = size
        books[ticker] = book
    elif kind == "orderbook_delta":
        side = body.get("side")
        price = cent(body.get("price_dollars", body.get("price")))
        try:
            delta = float(body.get("delta_fp", body.get("delta")))
        except (TypeError, ValueError):
            return None, False
        if side not in ("yes", "no") or price is None:
            return None, False
        book = books.setdefault(ticker, {"yes": {}, "no": {}})
        current = book[side].get(price, 0.0) + delta
        if current > 0:
            book[side][price] = current
        else:
            book[side].pop(price, None)
    else:
        return None, False
    return str(ticker), snapshot


def tape_row(epoch: float, book: dict[str, dict[int, float]], last_trade: int | None) -> list[Any] | None:
    bids = sorted(book["yes"].items(), reverse=True)[:5]
    asks = sorted(((100 - price, size) for price, size in book["no"].items()))[:5]
    if not bids or not asks:
        return None
    cells: list[Any] = [timestamp_et(epoch)]
    for levels in (bids, asks):
        for index in range(5):
            if index < len(levels):
                price, size = levels[index]
                cells.extend((price, format(size, ".10g")))
            else:
                cells.extend(("", ""))
    bid_depth = sum(size for _, size in bids)
    ask_depth = sum(size for _, size in asks)
    denominator = bid_depth + ask_depth
    cells.extend((
        format((bids[0][0] + asks[0][0]) / 2, ".10g"),
        format(bid_depth, ".10g"),
        format(ask_depth, ".10g"),
        format(bid_depth / denominator, ".10g") if denominator else "",
        last_trade if last_trade is not None else "",
    ))
    return cells


def run(args: argparse.Namespace) -> dict[str, Any]:
    registry = Path(args.registry).resolve()
    raw_dir = Path(args.raw_dir).resolve()
    member_list = Path(args.source_member_list).resolve()
    output = Path(args.output).resolve()
    tape_dir = output / "tapes"
    output.mkdir(parents=True, exist_ok=True)
    events, targets = load_registry(registry)
    raw_files = sorted(raw_dir.glob("ws_*.jsonl.gz"))
    if not raw_files:
        raise RuntimeError("no recorder archives")
    expected_names = [Path(row).name for row in member_list.read_text(encoding="utf-8").splitlines() if row]
    if [row.name for row in raw_files] != expected_names:
        missing = sorted(set(expected_names) - {row.name for row in raw_files})
        extra = sorted({row.name for row in raw_files} - set(expected_names))
        raise RuntimeError(f"filtered raw member conservation failed missing={missing} extra={extra}")

    books: dict[str, dict[str, dict[int, float]]] = {}
    last_trade: dict[str, int] = {}
    writers: dict[str, TapeWriter] = {}
    stats = {
        ticker: {
            "ticker": ticker,
            "snapshot_seen": False,
            "first_snapshot_epoch": None,
            "first_raw_epoch": None,
            "last_raw_epoch": None,
            "formed_rows": 0,
            "formed_rows_after_snapshot": 0,
            "trade_messages": 0,
        }
        for ticker in sorted(targets)
    }
    raw_rows = 0
    target_rows = 0
    first_archive_epoch = None
    last_archive_epoch = None
    for raw_file in raw_files:
        with gzip.open(raw_file, "rt", encoding="utf-8", errors="strict") as handle:
            for line in handle:
                if not line.strip():
                    continue
                raw_rows += 1
                row = json.loads(line)
                epoch = source_epoch(row)
                if epoch is not None:
                    first_archive_epoch = epoch if first_archive_epoch is None else min(first_archive_epoch, epoch)
                    last_archive_epoch = epoch if last_archive_epoch is None else max(last_archive_epoch, epoch)
                message = row.get("m")
                if not isinstance(message, dict):
                    continue
                body = message.get("msg")
                ticker = body.get("market_ticker") if isinstance(body, dict) else None
                if ticker not in targets:
                    continue
                target_rows += 1
                ticker = str(ticker)
                if epoch is not None:
                    stat = stats[ticker]
                    stat["first_raw_epoch"] = epoch if stat["first_raw_epoch"] is None else min(stat["first_raw_epoch"], epoch)
                    stat["last_raw_epoch"] = epoch if stat["last_raw_epoch"] is None else max(stat["last_raw_epoch"], epoch)
                if message.get("type") == "trade":
                    price = cent(body.get("yes_price_dollars", body.get("yes_price")))
                    if price is not None:
                        last_trade[ticker] = price
                    stats[ticker]["trade_messages"] += 1
                    continue
                changed, snapshot = apply_book(message, books)
                if changed != ticker or epoch is None:
                    continue
                if snapshot:
                    stats[ticker]["snapshot_seen"] = True
                    stats[ticker]["first_snapshot_epoch"] = (
                        epoch
                        if stats[ticker]["first_snapshot_epoch"] is None
                        else min(stats[ticker]["first_snapshot_epoch"], epoch)
                    )
                values = tape_row(epoch, books[ticker], last_trade.get(ticker))
                if values is None:
                    continue
                writer = writers.get(ticker)
                if writer is None:
                    writer = TapeWriter(tape_dir / f"{ticker}.csv.gz")
                    writers[ticker] = writer
                writer.write(values)
                stats[ticker]["formed_rows"] += 1
                if stats[ticker]["snapshot_seen"]:
                    stats[ticker]["formed_rows_after_snapshot"] += 1

    for writer in writers.values():
        writer.close()
    ticker_rows = []
    for ticker in sorted(targets):
        tape = tape_dir / f"{ticker}.csv.gz"
        row = stats[ticker]
        row.update({
            "tape_exists": tape.exists(),
            "tape_sha256": sha_file(tape) if tape.exists() else None,
            "tape_bytes": tape.stat().st_size if tape.exists() else 0,
            "authoritative_from_snapshot": bool(row["snapshot_seen"] and row["formed_rows_after_snapshot"] > 0),
        })
        ticker_rows.append(row)
    manifest = {
        "schema_version": "window1-v47-exam-capture-materialization-v1",
        "policy_invocations": 0,
        "score_rows": 0,
        "registry": {"path": str(registry), "sha256": sha_file(registry), "events": len(events), "tickers": len(targets)},
        "raw_archive": {
            "directory": str(raw_dir),
            "files": len(raw_files),
            "raw_rows": raw_rows,
            "target_rows": target_rows,
            "first_epoch": first_archive_epoch,
            "last_epoch": last_archive_epoch,
            "first_file": raw_files[0].name,
            "last_file": raw_files[-1].name,
            "source_member_list_sha256": sha_file(member_list),
            "source_member_list_bytes": member_list.stat().st_size,
        },
        "tickers": ticker_rows,
        "admission_note": "Only formed rows after an observed retained-archive snapshot are authoritative; delta-only prefixes are excluded.",
    }
    (output / "CAPTURE_MATERIALIZATION_MANIFEST.json").write_bytes(canonical(manifest))
    (output / "CAPTURE_MATERIALIZATION_TICKERS.jsonl").write_text(
        "".join(compact(row) + "\n" for row in ticker_rows), encoding="utf-8", newline="\n"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--source-member-list", required=True)
    parser.add_argument("--output", required=True)
    result = run(parser.parse_args())
    print(compact({
        "registry_events": result["registry"]["events"],
        "registry_tickers": result["registry"]["tickers"],
        "raw_files": result["raw_archive"]["files"],
        "authoritative_tickers": sum(row["authoritative_from_snapshot"] for row in result["tickers"]),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
