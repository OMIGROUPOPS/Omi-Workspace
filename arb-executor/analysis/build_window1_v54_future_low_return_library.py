#!/usr/bin/env python3
"""Materialize the bell-bounded future-low/seen-low path for V54.

The source is the already-filed Foundation minute universe.  The output keeps
only exact change points, so it is a lossless derivative of the minute path for
the question "what was the next true-trade low relative to the low already
seen?"  It does not fit a threshold, bucket, or placement constant.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
from collections import Counter

import duckdb


SOURCE_COLUMNS = (
    "ticker",
    "event_ticker",
    "minute_ts",
    "premarket_phase",
    "minute_has_trade",
    "price_low",
    "match_start_ts",
    "match_start_method",
)


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def cents(value):
    if value is None or not math.isfinite(float(value)):
        return None
    converted = int(round(float(value) * 100))
    return converted if 1 <= converted <= 99 else None


def compact_ticker(rows):
    rows.sort(key=lambda row: int(row["minute_ts"]))
    known = [row for row in rows if row.get("match_start_method") != "unknown" and row.get("match_start_ts") is not None]
    if not known:
        return None
    bell = int(known[0]["match_start_ts"])
    stable = [int(row["minute_ts"]) for row in rows if row.get("premarket_phase") == "stable" and int(row["minute_ts"]) < bell]
    if not stable:
        return None
    formation = min(stable)
    bounded = [row for row in rows if int(row["minute_ts"]) <= formation or int(row["minute_ts"]) < bell]
    pre = [cents(row.get("price_low")) for row in bounded if row.get("minute_has_trade") and int(row["minute_ts"]) <= formation]
    pre = [value for value in pre if value is not None]
    if not pre:
        return None
    seen = min(pre)
    post = []
    for row in bounded:
        minute = int(row["minute_ts"])
        if minute <= formation or minute >= bell:
            continue
        low = cents(row.get("price_low")) if row.get("minute_has_trade") else None
        post.append((minute, low))
    future = [None] * len(post)
    running = None
    for index in range(len(post) - 1, -1, -1):
        # Strict future: the member's current minute never supplies its own
        # label.  This preserves causality at the Foundation's MINUTE grain.
        future[index] = running
        low = post[index][1]
        if low is not None:
            running = low if running is None else min(running, low)
    path = []
    prior = object()
    span = bell - formation
    for index, (minute, low) in enumerate(post):
        if low is not None:
            seen = min(seen, low)
        next_low = future[index]
        value = None if next_low is None else next_low - seen
        signature = (seen, next_low, value)
        if signature == prior:
            continue
        prior = signature
        path.append({
            "minute_epoch": minute,
            "window_fraction": (minute - formation) / span,
            "seen_true_trade_low_cents": seen,
            "strict_future_true_trade_low_cents": next_low,
            "future_low_minus_seen_low_cents": value,
            "source_row_ref": f'{rows[0]["ticker"]}@minute_ts={minute}',
        })
    if not path or path[0]["minute_epoch"] > formation:
        next_low = running
        path.insert(0, {
            "minute_epoch": formation,
            "window_fraction": 0.0,
            "seen_true_trade_low_cents": min(pre),
            "strict_future_true_trade_low_cents": next_low,
            "future_low_minus_seen_low_cents": None if next_low is None else next_low - min(pre),
            "source_row_ref": f'{rows[0]["ticker"]}@minute_ts={formation}',
        })
    return {
        "ticker": rows[0]["ticker"],
        "leg_id": rows[0]["ticker"].split("-")[-1],
        "formation_end_epoch": formation,
        "bell_epoch": bell,
        "bell_method": known[0]["match_start_method"],
        "grain": "MINUTE",
        "strict_future_excludes_current_minute": True,
        "path": path,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    connection = duckdb.connect(database=":memory:")
    selected = ",".join(SOURCE_COLUMNS)
    cursor = connection.execute(f"SELECT {selected} FROM read_parquet(?)", [os.path.abspath(args.source)])
    events = {}
    current_ticker = None
    current_rows = []
    source_rows = 0
    bounded_legs = 0
    path_points = 0
    by_category = Counter()

    def flush():
        nonlocal current_rows, bounded_legs, path_points
        if not current_rows:
            return
        leg = compact_ticker(current_rows)
        current_rows = []
        if leg is None:
            return
        event_id = leg["ticker"].rsplit("-", 1)[0]
        category = "ATP_CHALL" if event_id.startswith("KXATPCHALLENGERMATCH") else "ATP_MAIN" if event_id.startswith("KXATPMATCH") else "WTA_CHALL" if event_id.startswith("KXWTACHALLENGERMATCH") else "WTA_MAIN" if event_id.startswith("KXWTAMATCH") else "OTHER"
        events.setdefault(event_id, {"event_id": event_id, "category": category, "legs": []})["legs"].append(leg)
        bounded_legs += 1
        path_points += len(leg["path"])
        by_category[category] += 1

    prior_minute = None
    while True:
        batch = cursor.fetchmany(131072)
        if not batch:
            break
        for values in batch:
            row = dict(zip(SOURCE_COLUMNS, values))
            source_rows += 1
            ticker = row["ticker"]
            if current_ticker is not None and ticker != current_ticker:
                flush()
                prior_minute = None
            if ticker == current_ticker and prior_minute is not None and int(row["minute_ts"]) < prior_minute:
                raise RuntimeError(f"SOURCE_NOT_SORTED_WITHIN_TICKER {ticker}: {row['minute_ts']} < {prior_minute}")
            current_ticker = ticker
            prior_minute = int(row["minute_ts"])
            current_rows.append(row)
    flush()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    digest = hashlib.sha256()
    output_rows = 0
    with gzip.open(args.output, "wt", encoding="utf-8", compresslevel=9, newline="\n") as stream:
        for event_id in sorted(events):
            event = events[event_id]
            event["legs"].sort(key=lambda leg: leg["leg_id"])
            line = json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n"
            stream.write(line)
            output_rows += 1
    output_sha = sha256_file(args.output)
    receipt = {
        "label": "V54_BELL_BOUNDED_FUTURE_LOW_RETURN_LIBRARY",
        "question": "STRICT_FUTURE_TRUE_TRADE_LOW_MINUS_CAUSAL_SEEN_TRUE_TRADE_LOW_AT_MEMBER_MINUTE",
        "method": "EXACT_MINUTE_PATH_CHANGE_POINTS; NO_BUCKETS; NO_THRESHOLDS; NO_PLACEMENT_CONSTANTS; CURRENT_MINUTE_EXCLUDED_FROM_ITS_LABEL",
        "source": {"path": args.source, "sha256": sha256_file(args.source), "bytes": os.path.getsize(args.source), "rows": source_rows},
        "output": {"path": args.output, "sha256": output_sha, "bytes": os.path.getsize(args.output), "rows": output_rows, "bounded_legs": bounded_legs, "path_points": path_points, "by_category_legs": dict(sorted(by_category.items()))},
        "layer_license": {"grain": "MINUTE", "licensed_layers": ["MACRO", "MICRO"], "micro_micro_licensed": False},
        "unknown_bell_method_excluded": True,
    }
    with open(args.receipt, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
