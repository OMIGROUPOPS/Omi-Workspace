#!/usr/bin/env python3
"""Build the per-leg, bell-bounded range-overlap path index.

The index is a lossless change-point compaction of stored minute observations.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

import pyarrow.parquet as pq


SOURCE_COLUMNS = (
    "ticker",
    "event_ticker",
    "minute_ts",
    "premarket_phase",
    "minute_has_trade",
    "price_low",
    "price_high",
    "price_close",
    "yes_bid_close",
    "yes_ask_close",
    "volume_in_minute",
    "match_start_ts",
    "match_start_method",
)

VERIFY_EVENT = "KXATPCHALLENGERMATCH-26APR01ALUMEJ"
VERIFY_LEG = "ALU"


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def finite_number(value):
    if value is None:
        return None
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def cents(value):
    parsed = finite_number(value)
    return None if parsed is None else int(round(parsed * 100))


def compact_number(value):
    parsed = finite_number(value)
    if parsed is None:
        return None
    rounded = round(parsed)
    return int(rounded) if abs(parsed - rounded) < 1e-9 else parsed


def utc_stamp(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def load_span_source(path: str):
    specs = {}
    events = 0
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            span = row.get("span") or {}
            if span.get("status") != "BOUNDED":
                continue
            events += 1
            event_id = row["event_id"]
            category = row["category"]
            for leg in row.get("legs") or []:
                ticker = leg["ticker"]
                if ticker in specs:
                    raise RuntimeError(f"DUPLICATE_BOUNDED_TICKER {ticker}")
                formation = int(leg["formation_end_epoch"])
                bell = int(leg["bell_epoch"])
                if formation >= bell:
                    raise RuntimeError(f"INVALID_BOUNDED_SPAN {ticker}: {formation} >= {bell}")
                anchor = int(leg["anchor_cents"])
                specs[ticker] = {
                    "event_id": event_id,
                    "event_date": row.get("event_date"),
                    "category": category,
                    "leg_id": leg["leg_id"],
                    "ticker": ticker,
                    "anchor_cents": anchor,
                    "side": "LEADER" if anchor >= 50 else "UNDERDOG",
                    "formation_end_epoch": formation,
                    "bell_epoch": bell,
                    "floor_fraction": leg.get("floor_fraction"),
                    "span_source_row": line_number,
                }
    return specs, events


def build_leg(rows, spec):
    rows.sort(key=lambda row: int(row["minute_ts"]))
    formation = spec["formation_end_epoch"]
    bell = spec["bell_epoch"]

    known = {
        str(row.get("match_start_method"))
        for row in rows
        if row.get("match_start_method") not in (None, "unknown")
    }
    bells = {
        int(row["match_start_ts"])
        for row in rows
        if row.get("match_start_method") not in (None, "unknown")
        and row.get("match_start_ts") is not None
    }
    if not known or not bells:
        raise RuntimeError(f"BOUNDED_TICKER_HAS_NO_KNOWN_BELL {spec['ticker']}")
    if bell not in bells:
        raise RuntimeError(f"BELL_MISMATCH {spec['ticker']}: span={bell} parquet={sorted(bells)}")

    seen_low = None
    last_cents = None
    for row in rows:
        minute = int(row["minute_ts"])
        if minute > formation:
            break
        if row.get("minute_has_trade"):
            low = cents(row.get("price_low"))
            close = cents(row.get("price_close"))
            if low is not None:
                seen_low = low if seen_low is None else min(seen_low, low)
            if close is not None:
                last_cents = close

    path = []
    prior = object()
    seen_high = None
    volume_cum = 0
    found_formation = False
    span_seconds = bell - formation

    for row in rows:
        minute = int(row["minute_ts"])
        if minute < formation:
            continue
        if minute >= bell:
            break
        if minute == formation:
            found_formation = True

        if row.get("minute_has_trade"):
            low = cents(row.get("price_low"))
            high = cents(row.get("price_high"))
            close = cents(row.get("price_close"))
            if low is not None:
                seen_low = low if seen_low is None else min(seen_low, low)
            if high is not None:
                seen_high = high if seen_high is None else max(seen_high, high)
            if close is not None:
                last_cents = close

        minute_volume = finite_number(row.get("volume_in_minute"))
        if minute_volume is None:
            raise RuntimeError(f"NULL_VOLUME_IN_MINUTE {spec['ticker']}@{minute}")
        volume_cum += minute_volume

        bid_cents = cents(row.get("yes_bid_close"))
        ask_cents = cents(row.get("yes_ask_close"))
        signature = (
            seen_low,
            seen_high,
            last_cents,
            bid_cents,
            ask_cents,
            compact_number(volume_cum),
        )
        if signature == prior:
            continue
        prior = signature
        path.append(
            {
                "window_fraction": (minute - formation) / span_seconds,
                "seen_true_trade_low_cents": seen_low,
                "seen_true_trade_high_cents": seen_high,
                "last_cents": last_cents,
                "bid_cents": bid_cents,
                "ask_cents": ask_cents,
                "volume_cum": compact_number(volume_cum),
            }
        )

    if not found_formation:
        raise RuntimeError(f"FORMATION_MINUTE_MISSING {spec['ticker']}@{formation}")
    if not path or path[0]["window_fraction"] != 0.0:
        raise RuntimeError(f"PATH_DOES_NOT_START_AT_FORMATION {spec['ticker']}")

    return {
        key: spec[key]
        for key in (
            "event_id",
            "category",
            "leg_id",
            "ticker",
            "anchor_cents",
            "side",
            "formation_end_epoch",
            "bell_epoch",
            "floor_fraction",
        )
    } | {"path": path}


def load_future_low_verification(path: str):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("event_id") != VERIFY_EVENT:
                continue
            for leg in event.get("legs") or []:
                if leg.get("leg_id") == VERIFY_LEG:
                    return leg
    raise RuntimeError(f"VERIFY_LEG_NOT_FOUND {VERIFY_EVENT}|{VERIFY_LEG}")


def verify_alumej(actual, future_leg):
    expected_points = (future_leg.get("path") or [])[:4]
    actual_by_fraction = {point["window_fraction"]: point for point in actual["path"]}
    comparisons = []
    for expected in expected_points:
        fraction = expected["window_fraction"]
        point = actual_by_fraction.get(fraction)
        comparisons.append(
            {
                "future_low_window_fraction": fraction,
                "future_low_seen_true_trade_low_cents": expected.get("seen_true_trade_low_cents"),
                "range_overlap_point": point,
                "fraction_match": point is not None,
                "seen_low_match": point is not None
                and point.get("seen_true_trade_low_cents") == expected.get("seen_true_trade_low_cents"),
            }
        )
    return {
        "event_id": VERIFY_EVENT,
        "leg_id": VERIFY_LEG,
        "future_low_source_sha256": sha256_file(path=future_leg["_source_path"]),
        "points": comparisons,
        "all_fraction_matches": all(row["fraction_match"] for row in comparisons),
        "all_seen_low_matches": all(row["seen_low_match"] for row in comparisons),
    }


def deterministic_gzip_text(path: str):
    raw = open(path, "wb")
    zipped = gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0)
    return raw, io.TextIOWrapper(zipped, encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--span-source", required=True)
    parser.add_argument("--future-low", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--source-receipt-path")
    parser.add_argument("--span-source-receipt-path")
    parser.add_argument("--output-receipt-path")
    args = parser.parse_args()

    source = os.path.abspath(args.source)
    span_source = os.path.abspath(args.span_source)
    future_low = os.path.abspath(args.future_low)
    output = os.path.abspath(args.output)
    receipt_path = os.path.abspath(args.receipt)
    specs, bounded_events_in_span_source = load_span_source(span_source)
    event_dates = sorted(
        datetime.strptime(spec["event_date"], "%y%b%d").date().isoformat()
        for spec in specs.values()
        if spec.get("event_date")
    )
    future_leg = load_future_low_verification(future_low)
    future_leg["_source_path"] = future_low

    parquet = pq.ParquetFile(source)
    source_fields = set(parquet.schema_arrow.names)
    missing_fields = [field for field in SOURCE_COLUMNS if field not in source_fields]
    if missing_fields:
        raise RuntimeError(f"SOURCE_FIELDS_MISSING {missing_fields}")

    os.makedirs(os.path.dirname(output), exist_ok=True)
    os.makedirs(os.path.dirname(receipt_path), exist_ok=True)
    temporary = output + ".tmp"
    raw_stream, output_stream = deterministic_gzip_text(temporary)

    current_ticker = None
    current_rows = []
    seen_blocks = set()
    written_tickers = set()
    event_ids = set()
    category_events = defaultdict(set)
    category_legs = Counter()
    category_points = Counter()
    points = 0
    minimum_formation = None
    maximum_bell = None
    verification_actual = None

    def flush():
        nonlocal current_rows, points, minimum_formation, maximum_bell, verification_actual
        if not current_rows:
            return
        ticker = current_rows[0]["ticker"]
        spec = specs.get(ticker)
        rows = current_rows
        current_rows = []
        if spec is None:
            return
        leg = build_leg(rows, spec)
        output_stream.write(json.dumps(leg, sort_keys=True, separators=(",", ":")) + "\n")
        written_tickers.add(ticker)
        event_ids.add(leg["event_id"])
        category_events[leg["category"]].add(leg["event_id"])
        category_legs[leg["category"]] += 1
        category_points[leg["category"]] += len(leg["path"])
        points += len(leg["path"])
        minimum_formation = leg["formation_end_epoch"] if minimum_formation is None else min(minimum_formation, leg["formation_end_epoch"])
        maximum_bell = leg["bell_epoch"] if maximum_bell is None else max(maximum_bell, leg["bell_epoch"])
        if leg["event_id"] == VERIFY_EVENT and leg["leg_id"] == VERIFY_LEG:
            verification_actual = leg

    try:
        for batch in parquet.iter_batches(batch_size=131072, columns=list(SOURCE_COLUMNS)):
            columns = batch.to_pydict()
            for index in range(batch.num_rows):
                row = {field: columns[field][index] for field in SOURCE_COLUMNS}
                ticker = row["ticker"]
                if current_ticker is not None and ticker != current_ticker:
                    flush()
                    seen_blocks.add(current_ticker)
                    if ticker in seen_blocks:
                        raise RuntimeError(f"SOURCE_TICKER_BLOCK_REPEATED {ticker}")
                current_ticker = ticker
                if ticker in specs:
                    current_rows.append(row)
        flush()
        output_stream.flush()
        output_stream.close()
        raw_stream.close()
        os.replace(temporary, output)
    except Exception:
        try:
            output_stream.close()
        finally:
            raw_stream.close()
        if os.path.exists(temporary):
            os.remove(temporary)
        raise

    missing_tickers = sorted(set(specs) - written_tickers)
    if missing_tickers:
        raise RuntimeError(f"BOUNDED_TICKERS_MISSING_FROM_PARQUET count={len(missing_tickers)} first={missing_tickers[:10]}")
    if verification_actual is None:
        raise RuntimeError(f"VERIFY_OUTPUT_NOT_FOUND {VERIFY_EVENT}|{VERIFY_LEG}")

    verification = verify_alumej(verification_actual, future_leg)
    categories = {
        category: {
            "events": len(category_events[category]),
            "legs": category_legs[category],
            "points": category_points[category],
        }
        for category in sorted(category_legs)
    }
    receipt = {
        "label": "RANGE_OVERLAP_LIBRARY_RECEIPT",
        "method": "FOUNDATION_BOUNDED_SPANS; EXACT_MINUTE_PATH_CHANGE_POINTS; CAUSAL_STATE_THROUGH_CURRENT_MINUTE; CURRENT_MINUTE_EXCLUDED_FROM_OWN_STRICT_FUTURE_LABEL; NO_FUTURE_LABEL_EMITTED",
        "counts": {
            "events": len(event_ids),
            "legs": len(written_tickers),
            "points": points,
        },
        "category_breakdown": categories,
        "date_span": {
            "event_start": event_dates[0],
            "event_end": event_dates[-1],
            "formation_start_epoch": minimum_formation,
            "formation_start_utc": utc_stamp(minimum_formation),
            "bell_end_epoch": maximum_bell,
            "bell_end_utc": utc_stamp(maximum_bell),
        },
        "sources": {
            "parquet": {
                "path": args.source_receipt_path or args.source,
                "sha256": sha256_file(source),
                "bytes": os.path.getsize(source),
                "rows": parquet.metadata.num_rows,
            },
            "bounded_span_source": {
                "path": args.span_source_receipt_path or args.span_source,
                "sha256": sha256_file(span_source),
                "bytes": os.path.getsize(span_source),
                "bounded_events": bounded_events_in_span_source,
                "bounded_legs": len(specs),
            },
        },
        "output": {
            "path": args.output_receipt_path or args.output,
            "sha256": sha256_file(output),
            "bytes": os.path.getsize(output),
            "rows": len(written_tickers),
        },
        "span_rule": "Only span.status BOUNDED members from the filed foundation library; each leg runs formation_end_epoch <= minute_ts < bell_epoch; parquet match_start_method=unknown is excluded.",
        "side_rule": "LEADER when anchor_cents >= 50; otherwise UNDERDOG.",
        "field_rules": {
            "seen_true_trade_low_cents": "Running minimum of price_low on minute_has_trade rows, initialized through formation_end_epoch exactly as the future-low builder and updated causally thereafter.",
            "seen_true_trade_high_cents": "Running maximum from formation_end_epoch of price_high, the highest true-trade price in each minute from the per-minute trade OHLC field; no substitute field.",
            "last_cents": "Latest price_close on a minute_has_trade row, carried forward; price_close is the last true-trade price in the minute and is the close field beside the future-low builder's price_low true-trade source.",
            "bid_cents": "yes_bid_close converted to integer cents.",
            "ask_cents": "yes_ask_close converted to integer cents.",
            "volume_cum": "Running sum of trade-tape-sourced volume_in_minute from formation_end_epoch through the current minute.",
            "change_point": "Emit the formation minute and each later minute where any of seen_true_trade_low_cents, seen_true_trade_high_cents, last_cents, bid_cents, ask_cents, or volume_cum changes.",
        },
        "layer_license": {
            "grain": "MINUTE",
            "licensed_layers": ["MACRO", "MICRO"],
            "micro_micro_licensed": False,
        },
        "leave_self_out_applied": False,
        "verification": verification,
        "differs_from_prior_art": {
            "range_spectrum_v1": "Recorder minute tape, bell-bounded formation-to-bell fractions, Aug 2025-May 2026 bounded library; not poll snapshots with an onset edge.",
            "July_DRIFT_ATLAS_trendpath_build.py": "Per-leg paths, not page percentiles.",
            "FUTURE_LOW_RETURN_LIBRARY": "Carries high, last, bid, ask, and volume beside the low.",
        },
    }
    with open(receipt_path, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
