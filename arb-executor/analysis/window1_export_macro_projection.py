#!/usr/bin/env python3
"""Export a receipted causal bookmaker projection for offline fit execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


VERSION = "window1-macro-projection-v1"


class ProjectionError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_events(path: Path) -> list[dict[str, Any]]:
    rows = [
        json.loads(line) for line in path.read_text(
            encoding="utf-8"
        ).splitlines() if line.strip()
    ]
    if len(rows) != 804 or len({
        str(row.get("event_id") or "") for row in rows
    }) != 804:
        raise ProjectionError("immutable event grain changed")
    return rows


def export(args: argparse.Namespace) -> int:
    source = Path(args.source_db).resolve()
    events_path = Path(args.events).resolve()
    start_summary_path = Path(args.start_summary).resolve()
    output = Path(args.output).resolve()
    receipt_path = Path(args.receipt_output).resolve()
    if output.exists() or receipt_path.exists():
        raise ProjectionError("refusing to overwrite projection evidence")
    events = read_events(events_path)
    start_summary = json.loads(
        start_summary_path.read_text(encoding="utf-8")
    )
    source_sha = (
        start_summary.get("tennis_db_live_scores") or {}
    ).get("sha256")
    if not source_sha:
        raise ProjectionError("start receipt lacks frozen database hash")
    source_connection = sqlite3.connect(
        "file:" + str(source) + "?mode=ro&immutable=1", uri=True
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    destination = sqlite3.connect(str(output))
    category_rows: Counter[str] = Counter()
    event_rows: dict[str, int] = {}
    try:
        destination.executescript(
            """
            PRAGMA journal_mode=DELETE;
            PRAGMA synchronous=FULL;
            CREATE TABLE book_prices(
              event_ticker TEXT NOT NULL,
              book_key TEXT NOT NULL,
              player1_name TEXT,
              player2_name TEXT,
              book_p1_fv_cents REAL,
              book_p2_fv_cents REAL,
              polled_at TEXT
            );
            CREATE TABLE players(
              kalshi_code TEXT,
              name TEXT
            );
            """
        )
        player_rows = source_connection.execute(
            """SELECT kalshi_code, name FROM players
               WHERE kalshi_code IS NOT NULL AND name IS NOT NULL"""
        ).fetchall()
        destination.executemany(
            "INSERT INTO players(kalshi_code,name) VALUES (?,?)",
            player_rows,
        )
        for index, event in enumerate(events, 1):
            event_id = str(event["event_id"])
            rows = source_connection.execute(
                """SELECT event_ticker, book_key, player1_name,
                          player2_name, book_p1_fv_cents,
                          book_p2_fv_cents, polled_at
                   FROM book_prices
                   WHERE event_ticker=?
                   ORDER BY polled_at, book_key""",
                (event_id,),
            ).fetchall()
            destination.executemany(
                """INSERT INTO book_prices
                   VALUES (?,?,?,?,?,?,?)""",
                rows,
            )
            event_rows[event_id] = len(rows)
            category_rows[str(event["category"])] += len(rows)
            if index % 100 == 0 or index == len(events):
                print(
                    f"projection_events={index}/{len(events)}",
                    flush=True,
                )
        destination.executescript(
            """
            CREATE INDEX idx_book_prices_event
              ON book_prices(event_ticker,polled_at);
            CREATE INDEX idx_book_prices_book
              ON book_prices(book_key,polled_at);
            CREATE INDEX idx_players_code ON players(kalshi_code);
            """
        )
        destination.commit()
        quick = destination.execute("PRAGMA quick_check").fetchone()[0]
        book_rows = destination.execute(
            "SELECT COUNT(*) FROM book_prices"
        ).fetchone()[0]
        bounds = destination.execute(
            "SELECT MIN(polled_at),MAX(polled_at) FROM book_prices"
        ).fetchone()
    finally:
        destination.close()
        source_connection.close()
    os.chmod(output, 0o600)
    receipt = {
        "schema_version": VERSION,
        "source": {
            "logical_name": "frozen_cutover_tennis_db",
            "sha256": source_sha,
            "start_summary_sha256": sha256_file(start_summary_path),
        },
        "event_ledger": {
            "D": 804,
            "sha256": sha256_file(events_path),
        },
        "projection": {
            "sha256": sha256_file(output),
            "bytes": output.stat().st_size,
            "quick_check": quick,
            "book_price_rows": book_rows,
            "player_rows": len(player_rows),
            "events_with_rows": sum(
                count > 0 for count in event_rows.values()
            ),
            "events_without_rows": sum(
                count == 0 for count in event_rows.values()
            ),
            "rows_by_category": dict(sorted(category_rows.items())),
            "first_polled_at": bounds[0],
            "last_polled_at": bounds[1],
        },
        "field_law": {
            "book_prices": [
                "event_ticker", "book_key", "player1_name",
                "player2_name", "book_p1_fv_cents",
                "book_p2_fv_cents", "polled_at",
            ],
            "players": ["kalshi_code", "name"],
            "causal_filter": (
                "runner admits only rows with polled_at <= simulated time"
            ),
            "selection": "exact immutable D event_ticker only",
            "outcomes_or_settlement_included": False,
        },
        "privacy": {
            "account_or_order_data_included": False,
            "credentials_included": False,
            "projection_outside_git": True,
        },
    }
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt["projection"], sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--source-db", required=True)
    result.add_argument("--events", required=True)
    result.add_argument("--start-summary", required=True)
    result.add_argument("--output", required=True)
    result.add_argument("--receipt-output", required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(export(parser().parse_args()))
