#!/usr/bin/env python3
"""Measure decision-time anchor retention from the durable WS session tape."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import gzip
import json
import math
from pathlib import Path


TENNIS_PREFIXES = {
    "KXATPMATCH": "ATP_MAIN",
    "KXWTAMATCH": "WTA_MAIN",
    "KXATPCHALLENGERMATCH": "ATP_CHALL",
    "KXWTACHALLENGERMATCH": "WTA_CHALL",
    "KXITFMATCH": "ITF_M",
    "KXITFWMATCH": "ITF_W",
}


def category_of(ticker: str) -> str | None:
    return TENNIS_PREFIXES.get((ticker or "").split("-", 1)[0])


def price_cents(value) -> int | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if 0 < number < 1:
        number *= 100
    rounded = int(round(number))
    return rounded if 1 <= rounded <= 99 else None


def projected_cell_rows(
    anchors: dict[tuple[str, str], tuple[str, int]],
    projection_days: float,
    as_of: datetime,
) -> list[dict]:
    counts = Counter(
        (category, cell)
        for category, cell in anchors.values()
    )
    rows = []
    for category in sorted(set(TENNIS_PREFIXES.values())):
        for cell in range(5, 95):
            n = counts[(category, cell)]
            daily_rate = n / projection_days if projection_days > 0 else 0.0
            if n >= 20:
                days = 0
                date = as_of.date().isoformat()
            elif daily_rate > 0:
                days = int(math.ceil((20 - n) / daily_rate))
                date = (as_of.date() + timedelta(days=days)).isoformat()
            else:
                days = None
                date = None
            rows.append({
                "category": category,
                "cell_cents": cell,
                "retained_leg_days_n": n,
                "observed_daily_rate": round(daily_rate, 3),
                "days_to_n20_at_observed_rate": days,
                "estimated_n20_date": date,
            })
    return rows


def summarize_categories(cell_rows: list[dict]) -> dict:
    output = {}
    for category in sorted(set(TENNIS_PREFIXES.values())):
        rows = [row for row in cell_rows if row["category"] == category]
        dated = [
            row for row in rows if row["days_to_n20_at_observed_rate"] is not None
        ]
        output[category] = {
            "cells": len(rows),
            "cells_with_any_anchor": sum(
                row["retained_leg_days_n"] > 0 for row in rows
            ),
            "cells_already_n20": sum(
                row["retained_leg_days_n"] >= 20 for row in rows
            ),
            "cells_with_projectable_date": len(dated),
            "latest_projected_n20_date": max(
                (row["estimated_n20_date"] for row in dated),
                default=None,
            ),
            "unprojectable_cells_at_current_volume": sum(
                row["estimated_n20_date"] is None for row in rows
            ),
        }
    return output


def scan(paths: list[Path], session_marker: str) -> dict:
    selected = [
        path for path in sorted(paths)
        if session_marker in path.name
    ]
    if not selected:
        raise SystemExit(f"no files contain session marker {session_marker!r}")

    states = defaultdict(lambda: {"bbo": None, "trade": None})
    receiver_anchors = {}
    provider_anchors = {}
    tennis_tickers = set()
    all_tickers = set()
    row_types = Counter()
    staleness = Counter()
    raw_hashes = set()
    min_ts = None
    max_ts = None
    observed_dates = set()
    rows_read = 0
    duplicate_raw_rows = 0
    partial_files = []

    for path in selected:
        try:
            handle = gzip.open(path, "rt", encoding="utf-8")
            with handle:
                for line in handle:
                    row = json.loads(line)
                    raw_hash = row.get("raw_ws_sha256")
                    if raw_hash and raw_hash in raw_hashes:
                        duplicate_raw_rows += 1
                        continue
                    if raw_hash:
                        raw_hashes.add(raw_hash)
                    rows_read += 1
                    ts = float(row["t"])
                    min_ts = ts if min_ts is None else min(min_ts, ts)
                    max_ts = ts if max_ts is None else max(max_ts, ts)
                    observed_dates.add(datetime.fromtimestamp(
                        ts, tz=timezone.utc
                    ).date())
                    message = row.get("m") or {}
                    msg = message.get("msg") or {}
                    ticker = (
                        msg.get("market_ticker")
                        or (row.get("bbo") or {}).get("market_ticker")
                    )
                    if ticker:
                        all_tickers.add(ticker)
                    category = category_of(ticker)
                    if not category:
                        continue
                    tennis_tickers.add(ticker)
                    kind = str(message.get("type") or "unknown")
                    row_types[kind] += 1
                    staleness[str(row.get("staleness_status"))] += 1
                    received_ts = ts
                    source_ts = row.get("source_epoch")
                    base = {
                        "received_ts": received_ts,
                        "source_ts": (
                            float(source_ts) if source_ts is not None else None
                        ),
                        "raw_hash": raw_hash,
                    }
                    bbo = row.get("bbo") or {}
                    bid = price_cents(bbo.get("yes_bid"))
                    ask = price_cents(bbo.get("yes_ask"))
                    if (
                        bbo.get("denominator_status") == "AVAILABLE"
                        and bid is not None
                        and ask is not None
                        and 0 < bid < ask < 100
                    ):
                        states[ticker]["bbo"] = {
                            **base, "bid": bid, "ask": ask,
                        }
                    if kind == "trade":
                        price = price_cents(
                            msg.get("yes_price", msg.get("yes_price_dollars"))
                        )
                        if price is not None:
                            states[ticker]["trade"] = {
                                **base, "price": price,
                            }

                    state = states[ticker]
                    book = state["bbo"]
                    trade = state["trade"]
                    if not book or not trade:
                        continue
                    if not (
                        book["raw_hash"] and trade["raw_hash"]
                        and abs(book["received_ts"] - trade["received_ts"]) <= 1800
                    ):
                        continue
                    cell = trade["price"]
                    if not 5 <= cell < 95:
                        continue
                    day = datetime.fromtimestamp(
                        received_ts, tz=timezone.utc
                    ).date().isoformat()
                    receiver_anchors.setdefault(
                        (day, ticker), (category, cell)
                    )
                    if (
                        book["source_ts"] is not None
                        and trade["source_ts"] is not None
                        and abs(book["source_ts"] - trade["source_ts"]) <= 1800
                    ):
                        provider_anchors.setdefault(
                            (day, ticker), (category, cell)
                        )
        except (EOFError, OSError):
            partial_files.append(str(path))

    if min_ts is None or max_ts is None:
        raise SystemExit("session contained no readable rows")
    observed_hours = max((max_ts - min_ts) / 3600.0, 1 / 3600.0)
    observed_days = observed_hours / 24.0
    as_of = datetime.fromtimestamp(max_ts, tz=timezone.utc)
    calendar_days = len(observed_dates)
    projection_days = float(max(1, calendar_days))
    receiver_cells = projected_cell_rows(
        receiver_anchors, projection_days, as_of
    )
    provider_cells = projected_cell_rows(
        provider_anchors, projection_days, as_of
    )
    return {
        "schema_version": "window1-retention-burndown-v1",
        "session_marker": session_marker,
        "files": [str(path) for path in selected],
        "partial_active_files": partial_files,
        "rows_read": rows_read,
        "duplicate_raw_rows_ignored": duplicate_raw_rows,
        "observed": {
            "first_received_utc": datetime.fromtimestamp(
                min_ts, tz=timezone.utc
            ).isoformat(),
            "last_received_utc": as_of.isoformat(),
            "hours": round(observed_hours, 3),
            "days": round(observed_days, 6),
            "calendar_days_used_for_projection": int(projection_days),
        },
        "subscriptions": {
            "all_unique_market_tickers": len(all_tickers),
            "tennis_unique_leg_tickers": len(tennis_tickers),
        },
        "tennis_row_types": dict(row_types),
        "tennis_staleness_status": dict(staleness),
        "receiver_clock_contract": {
            "definition": (
                "distinct tennis leg-day with a retained trade price and "
                "two-sided BBO no more than 30 minutes apart; both rows "
                "carry receive timestamps and raw frame hashes"
            ),
            "retained_leg_days": len(receiver_anchors),
            "retained_legs_per_observed_slate_day": round(
                len(receiver_anchors) / projection_days, 2
            ),
            "new_anchor_acquisition_per_observed_hour": round(
                len(receiver_anchors) / observed_hours, 2
            ),
            "by_category": summarize_categories(receiver_cells),
            "cells": receiver_cells,
        },
        "provider_clock_contract": {
            "definition": (
                "receiver-clock contract plus non-null exchange/provider "
                "source timestamps on both the trade and BBO"
            ),
            "retained_leg_days": len(provider_anchors),
            "retained_legs_per_observed_slate_day": round(
                len(provider_anchors) / projection_days, 2
            ),
            "new_anchor_acquisition_per_observed_hour": round(
                len(provider_anchors) / observed_hours, 2
            ),
            "by_category": summarize_categories(provider_cells),
            "cells": provider_cells,
        },
        "projection_caveat": (
            "Projection treats the partial session as one slate-day, never "
            "multiplies an initial snapshot burst by 24 hours. "
            "Zero-rate cells have no date; category slates are not assumed "
            "exchangeable across days."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--session-marker", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    payload = scan(
        list(args.input_dir.glob("ws_*.jsonl.gz")),
        args.session_marker,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps({
        "observed": payload["observed"],
        "subscriptions": payload["subscriptions"],
        "receiver": {
            key: value
            for key, value in payload["receiver_clock_contract"].items()
            if key not in {"cells", "by_category"}
        },
        "provider": {
            key: value
            for key, value in payload["provider_clock_contract"].items()
            if key not in {"cells", "by_category"}
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
