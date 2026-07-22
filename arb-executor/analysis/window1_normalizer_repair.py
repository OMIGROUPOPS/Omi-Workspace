#!/usr/bin/env python3
"""Pure source adapters and sanitized samples for Window-1 repair.

This module does not read production paths or databases. It demonstrates the
field-preserving repair needed before raw public trades or limited books can
enter the Window-1 evidence contract.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Mapping


def iso_epoch(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return dt.datetime.fromisoformat(
        str(value).replace("Z", "+00:00")).timestamp()


def positive_size(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    size = float(value)
    return size if size > 0 else 0.0


def upstream_public_trade(
    row: Mapping[str, Any], ticker: str,
) -> dict[str, Any]:
    receipt = str(row.get("trade_id") or row.get("id") or "")
    if not receipt:
        raise ValueError("upstream public trade lacks stable trade identity")
    size = positive_size(row.get("count_fp"))
    if size <= 0:
        raise ValueError("upstream public trade lacks verified positive size")
    created = row.get("created_time")
    if created in (None, ""):
        raise ValueError("upstream public trade lacks exchange timestamp")
    price_dollars = row.get("yes_price_dollars")
    if price_dollars in (None, ""):
        raise ValueError("upstream public trade lacks yes price")
    return {
        "receipt_id": receipt,
        "ticker": ticker,
        "exchange_ts": iso_epoch(created),
        "price_cents": int(round(float(price_dollars) * 100)),
        "size": size,
        "source": "kalshi_public_trade",
        "true_print": True,
        "taker_side": row.get("taker_side"),
        "field_lineage": {
            "receipt_id": "trade_id",
            "exchange_ts": "created_time",
            "price_cents": "yes_price_dollars",
            "size": "count_fp",
            "taker_side": "taker_side",
        },
    }


def inspect_daysheet_cache(
    row: Mapping[str, Any], ticker: str,
) -> dict[str, Any]:
    """Preserve ct as size while refusing identity-free cached rows."""
    size = positive_size(row.get("ct"))
    present = {
        "ticker": ticker,
        "exchange_ts": (
            iso_epoch(row["ts"]) if row.get("ts") not in (None, "")
            else None),
        "price_cents": (
            int(row["price_c"]) if row.get("price_c") not in (None, "")
            else None),
        "size": size,
        "source": "daysheet_tape_cache",
    }
    rejection = []
    if not row.get("trade_id"):
        rejection.append("stable receipt identity was discarded by producer")
    if present["exchange_ts"] is None:
        rejection.append("exchange timestamp missing")
    if present["price_cents"] is None:
        rejection.append("price missing")
    if size <= 0:
        rejection.append("verified positive size missing")
    return {
        "preserved_fields": present,
        "admissible_true_print": not rejection,
        "contract_rejections": rejection,
        "directional_features_available": bool(row.get("taker_side")),
        "repair": (
            "re-fetch or join the upstream trade_id and taker fields; map ct "
            "to size without float(value or 1)"),
    }


def synthetic_transition(
    ticker: str, exchange_ts: float, price_cents: int,
) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "exchange_ts": float(exchange_ts),
        "price_cents": int(price_cents),
        "size": 0.0,
        "source": "book_transition",
        "true_print": False,
        "admissible_true_print": False,
        "use": "diagnostic movement only",
    }


def limited_book(
    source: str, ticker: str, exchange_ts: float,
) -> dict[str, Any]:
    depths = {"premarket_ticks": "top5", "depth_recorder": "top20"}
    if source not in depths:
        raise ValueError("limited book source is not recognized")
    return {
        "source": source,
        "ticker": ticker,
        "exchange_ts": float(exchange_ts),
        "capture_depth": depths[source],
        "limited_feature_use": True,
        "exact_queue_use": False,
        "full_ladder": False,
        "required_for_exact_queue": (
            "ws_depth full ladder with epoch, sequence, gap, reconnect, and "
            "corruption fields"),
    }


def sanitized_samples() -> dict[str, Any]:
    ticker = "KXSAMPLEMATCH-26JUL12ABCCDE-ABC"
    upstream = {
        "trade_id": "sample-redacted-receipt",
        "created_time": "2026-07-12T12:00:00Z",
        "yes_price_dollars": "0.42",
        "count_fp": "5",
        "taker_side": "yes",
    }
    cached = {
        "ts": 1783857600.0,
        "price_c": 42,
        "ct": 5.0,
    }
    return {
        "schema_version": "window1-normalizer-repair-samples-v1",
        "structural_samples_not_market_observations": True,
        "upstream_public_trade": {
            "input": upstream,
            "normalized": upstream_public_trade(upstream, ticker),
        },
        "daysheet_cache_after_producer_loss": {
            "input": cached,
            "inspection": inspect_daysheet_cache(cached, ticker),
        },
        "synthetic_transition": synthetic_transition(
            ticker, 1783857601.0, 41),
        "premarket_top5": limited_book(
            "premarket_ticks", ticker, 1783857602.0),
        "depth_top20": limited_book(
            "depth_recorder", ticker, 1783857603.0),
        "exact_repair_sequence": [
            "retain upstream trade_id before cache serialization",
            "retain count_fp or map cached ct to size",
            "retain created_time as exchange timestamp",
            "retain taker_side for directional features",
            "deduplicate overlapping feeds by trade_id",
            "never promote zero or missing size",
            "never admit book_transition as a true print",
            "normalize top5/top20 books as limited feature sources",
            "reserve exact queue replay for valid ws_depth sequence epochs",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-output", required=True)
    args = parser.parse_args()
    output = Path(args.sample_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(sanitized_samples(), indent=2, sort_keys=True) + chr(10),
        encoding="utf-8",
    )
    print(json.dumps({
        "sample_output": str(output),
        "contains_market_observations": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
