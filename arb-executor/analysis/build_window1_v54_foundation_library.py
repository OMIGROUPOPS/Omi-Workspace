#!/usr/bin/env python3
"""Materialize the bell-bounded Foundation minute store for V54 repair iteration 2.

The source parquet stays in external custody.  This builder streams row groups and
commits only a compact, event-grain retrieval index.  Every value in that index is
derived inside the source row's native match_start_ts boundary.  Rows whose
match_start_method is ``unknown`` are never served.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pyarrow.parquet as pq


SOURCE_COLUMNS = [
    "ticker", "event_ticker", "minute_ts", "category",
    "yes_bid_close", "yes_ask_close", "spread_close", "mid_close",
    "price_close", "price_high", "price_low", "volume_in_minute",
    "trade_count_in_minute", "open_interest_ffill", "match_start_ts",
    "match_start_method", "minutes_since_open", "premarket_phase", "regime",
    "partner_ticker", "partner_yes_bid_close", "partner_yes_ask_close",
    "paired_mid_sum", "pair_gap_abs", "bid_consumption_velocity",
    "ask_consumption_velocity", "trade_clustering_in_minute",
]

SPIKE_FILES = {
    "ATP_CHALL": "atp_chall_spike_perN.parquet",
    "ATP_MAIN": "atp_main_spike_perN.parquet",
    "WTA_CHALL": "wta_chall_spike_perN.parquet",
    "WTA_MAIN": "wta_main_spike_perN.parquet",
}


def finite(value):
    return value if isinstance(value, (int, float)) and math.isfinite(value) else None


def epoch(value):
    if value is None:
        return None
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.timestamp()
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except ValueError:
        return None


def cents(value):
    value = finite(value)
    if value is None:
        return None
    converted = round(value * 100) if -1.0 <= value <= 1.0 else round(value)
    return converted if 0 <= converted <= 100 else None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_default(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    raise TypeError(type(value).__name__)


def load_spike_atlas(spike_dir: Path):
    atlas = {}
    receipts = []
    for category, filename in SPIKE_FILES.items():
        path = spike_dir / filename
        table = pq.read_table(path)
        receipts.append({
            "category": category,
            "path": str(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "rows": table.num_rows,
            "grain": "EVENT_LEG_DESCRIPTIVE",
            "licensed_layers": ["MACRO", "MICRO"],
            "micro_micro_licensed": False,
        })
        for row_number, row in enumerate(table.to_pylist(), start=1):
            ticker = row.get("ticker")
            if not ticker:
                continue
            atlas[str(ticker)] = {
                "source_id": f"SPIKE_ATLAS_{category}",
                "row_ref": f"{path}#row-{row_number}",
                "grain": "EVENT_LEG_DESCRIPTIVE",
                "licensed_layers": ["MACRO", "MICRO"],
                "micro_micro_licensed": False,
                "anchor_cents": cents(row.get("anchor_price")),
                "spike_cents": finite(row.get("spike_cents")),
                "size_qualified_max_cents": cents(row.get("size_qual_max")),
                "time_to_max_seconds": finite(row.get("time_to_max")),
                "drop_reason": row.get("drop_reason"),
            }
    return atlas, receipts


def choose_formation_row(rows):
    stable = [row for row in rows if row.get("premarket_phase") == "stable"]
    return stable[0] if stable else rows[0]


def summarize_leg(ticker, rows, spike_atlas):
    rows = sorted(rows, key=lambda row: epoch(row.get("minute_ts")) or -math.inf)
    formation = choose_formation_row(rows)
    formation_epoch = epoch(formation.get("minute_ts"))
    through_formation = [row for row in rows if (epoch(row.get("minute_ts")) or math.inf) <= formation_epoch]
    trade_rows = [row for row in rows if (finite(row.get("trade_count_in_minute")) or 0) > 0]
    observed_trade_rows = [row for row in through_formation if (finite(row.get("trade_count_in_minute")) or 0) > 0]
    final_trade_low = min((cents(row.get("price_low")) for row in trade_rows if cents(row.get("price_low")) is not None), default=None)
    observed_trade_low = min((cents(row.get("price_low")) for row in observed_trade_rows if cents(row.get("price_low")) is not None), default=None)
    final_ask_low = min((cents(row.get("yes_ask_close")) for row in rows if cents(row.get("yes_ask_close")) is not None), default=None)
    observed_ask_low = min((cents(row.get("yes_ask_close")) for row in through_formation if cents(row.get("yes_ask_close")) is not None), default=None)
    anchor = cents(formation.get("mid_close"))
    if anchor is None:
        bid, ask = cents(formation.get("yes_bid_close")), cents(formation.get("yes_ask_close"))
        anchor = math.floor((bid + ask) / 2) if bid is not None and ask is not None else cents(formation.get("price_close"))
    reference = cents(formation.get("price_close"))
    if reference is None:
        reference = anchor
    observed_low = observed_trade_low if observed_trade_low is not None else observed_ask_low
    final_low = final_trade_low if final_trade_low is not None else final_ask_low
    low_basis = "TRUE_TRADE" if final_trade_low is not None else "QUALIFYING_MINUTE_ASK"
    source_ref = f"{ticker}@{int(formation_epoch)}" if formation_epoch is not None else ticker
    leg = {
        "leg_id": ticker.split("-")[-1],
        "ticker": ticker,
        "anchor_cents": anchor,
        "reference_cents_at_formation": reference,
        "observed_low_cents": observed_low,
        "observed_trade_low_cents": observed_trade_low,
        "observed_ask_low_cents": observed_ask_low,
        "low_cents": final_low,
        "true_trade_low_cents": final_trade_low,
        "qualifying_minute_ask_low_cents": final_ask_low,
        "low_basis": low_basis,
        "high_cents": max((cents(row.get("price_high")) for row in trade_rows if cents(row.get("price_high")) is not None), default=None),
        "close_cents": cents(rows[-1].get("price_close")),
        "formation_end_epoch": formation_epoch,
        "bell_epoch": epoch(formation.get("match_start_ts")),
        "formation_phase_source": "premarket_phase=stable" if formation.get("premarket_phase") == "stable" else "FIRST_LAWFUL_MINUTE_NO_NATIVE_STABLE_ROW",
        "volume_through_formation": sum(finite(row.get("volume_in_minute")) or 0 for row in through_formation),
        "trades_through_formation": sum(int(finite(row.get("trade_count_in_minute")) or 0) for row in through_formation),
        "source_row_ref": source_ref,
        "spike_atlas": spike_atlas.get(ticker),
    }
    return leg, formation


def summarize_event(event_id, rows, spike_atlas, source_path):
    lawful = []
    excluded_unknown = 0
    excluded_after_bell = 0
    for row in rows:
        bell = epoch(row.get("match_start_ts"))
        minute = epoch(row.get("minute_ts"))
        if row.get("match_start_method") == "unknown" or bell is None:
            excluded_unknown += 1
            continue
        if minute is None or minute > bell:
            excluded_after_bell += 1
            continue
        lawful.append(row)
    if not lawful:
        return None, {"unknown": excluded_unknown, "after_bell": excluded_after_bell}
    by_ticker = defaultdict(list)
    for row in lawful:
        by_ticker[str(row["ticker"])].append(row)
    if len(by_ticker) != 2:
        return None, {"unknown": excluded_unknown, "after_bell": excluded_after_bell, "not_two_legs": 1}
    summarized = [summarize_leg(ticker, leg_rows, spike_atlas) for ticker, leg_rows in sorted(by_ticker.items())]
    legs = [item[0] for item in summarized]
    formation_rows = [item[1] for item in summarized]
    oriented = sorted(legs, key=lambda leg: ((leg["anchor_cents"] if leg["anchor_cents"] is not None else 50), leg["leg_id"]))
    anchors = [leg["anchor_cents"] for leg in oriented]
    observed_lows = [leg["observed_low_cents"] for leg in oriented]
    references = [leg["reference_cents_at_formation"] for leg in oriented]
    formation_epochs = [leg["formation_end_epoch"] for leg in oriented]
    first_minute = min(epoch(row.get("minute_ts")) for row in lawful if epoch(row.get("minute_ts")) is not None)
    formation_spreads = [cents(row.get("spread_close")) for row in formation_rows]
    # spread_close is already a proportion; cents() gives the intended cent width.
    vector = {
        "category": lawful[0].get("category"),
        "anchor_split_cents": abs(anchors[0] - anchors[1]) if all(value is not None for value in anchors) else None,
        "leg0_anchor_cents": anchors[0],
        "leg1_anchor_cents": anchors[1],
        "leg0_drift_cents": references[0] - anchors[0] if references[0] is not None and anchors[0] is not None else None,
        "leg1_drift_cents": references[1] - anchors[1] if references[1] is not None and anchors[1] is not None else None,
        "leg0_travel_cents": abs(references[0] - observed_lows[0]) if references[0] is not None and observed_lows[0] is not None else None,
        "leg1_travel_cents": abs(references[1] - observed_lows[1]) if references[1] is not None and observed_lows[1] is not None else None,
        "joint_mid_sum_cents": sum(references) if all(value is not None for value in references) else None,
        "joint_spread_cents": sum(value for value in formation_spreads if value is not None) if all(value is not None for value in formation_spreads) else None,
        "inverse_coherence": 1.0 if all(value is not None for value in references) else None,
        "volume_log1p": math.log1p(sum(leg["volume_through_formation"] for leg in oriented)),
        "hours_from_discovery": (max(formation_epochs) - first_minute) / 3600 if all(value is not None for value in formation_epochs) else None,
        "divot_depth_cents": None,
    }
    methods = sorted(set(row.get("match_start_method") for row in lawful))
    row_refs = [f"{source_path}#event={event_id}"] + [leg["source_row_ref"] for leg in legs]
    for leg in legs:
        if leg.get("spike_atlas"):
            row_refs.append(leg["spike_atlas"]["row_ref"])
    return {
        "event_id": event_id,
        "event_date": str(event_id).split("-")[1][:7] if "-" in str(event_id) else None,
        "category": lawful[0].get("category"),
        "quality": "FOUNDATION_MINUTE_BELL_BOUNDED",
        "span": {
            "status": "BOUNDED",
            "start_epoch": first_minute,
            "end_epoch": min(epoch(row.get("match_start_ts")) for row in lawful if epoch(row.get("match_start_ts")) is not None),
            "method": methods,
            "unknown_method_excluded": True,
        },
        "grain": "MINUTE",
        "licensed_layers": ["MACRO", "MICRO"],
        "micro_micro_licensed": False,
        "vector": vector,
        "legs": oriented,
        "source_receipts": [{
            "source_id": "FOUNDATION_PER_MINUTE_UNIVERSE",
            "row_ref": row_ref,
            "grain": "MINUTE",
            "licensed_layers": ["MACRO", "MICRO"],
            "micro_micro_licensed": False,
        } for row_ref in sorted(set(row_refs))],
    }, {"unknown": excluded_unknown, "after_bell": excluded_after_bell}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--spike-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--custody-location", default="/root/Omi-Workspace/arb-executor/data/durable/per_minute_universe/per_minute_features.parquet")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    spike_dir = Path(args.spike_dir).resolve()
    output = Path(args.output).resolve()
    receipt_path = Path(args.receipt).resolve()
    spike_atlas, spike_receipts = load_spike_atlas(spike_dir)
    parquet = pq.ParquetFile(source)
    names = set(parquet.schema.names)
    missing = sorted(set(SOURCE_COLUMNS) - names)
    if missing:
        raise RuntimeError(f"FOUNDATION_SCHEMA_MISSING {missing}")
    output.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    source_rows = 0
    skipped = Counter()
    by_category = Counter()
    current_event = None
    current_rows = []
    previous_event = None

    # Gzip mtime is fixed so two clean materializations are byte-identical.
    with output.open("wb") as raw_output, gzip.GzipFile(fileobj=raw_output, mode="wb", compresslevel=9, mtime=0) as gzip_output, io.TextIOWrapper(gzip_output, encoding="utf-8", newline="\n") as handle:
        def flush():
            nonlocal rows_written, current_rows, current_event
            if not current_rows:
                return
            summary, excluded = summarize_event(current_event, current_rows, spike_atlas, args.custody_location)
            skipped.update(excluded)
            if summary is not None:
                handle.write(json.dumps(summary, sort_keys=True, separators=(",", ":"), default=json_default) + "\n")
                rows_written += 1
                by_category[summary["category"]] += 1
            current_rows = []

        for row_group in range(parquet.num_row_groups):
            table = parquet.read_row_group(row_group, columns=SOURCE_COLUMNS)
            for row in table.to_pylist():
                source_rows += 1
                event_id = str(row.get("event_ticker") or "")
                if not event_id:
                    skipped["missing_event"] += 1
                    continue
                if current_event is None:
                    current_event = event_id
                if event_id != current_event:
                    flush()
                    if previous_event is not None and event_id < previous_event:
                        raise RuntimeError(f"FOUNDATION_NOT_EVENT_SORTED {event_id} after {previous_event}")
                    previous_event = current_event
                    current_event = event_id
                current_rows.append(row)
        flush()

    receipt = {
        "label": "V54_REPAIR_ITERATION2_FOUNDATION_LIBRARY",
        "source": {
            "path": str(source),
            "external_custody_location": args.custody_location,
            "sha256": sha256_file(source),
            "bytes": source.stat().st_size,
            "rows": source_rows,
            "grain": "MINUTE",
        },
        "native_window_law": {
            "right_edge": "match_start_ts",
            "method_field": "match_start_method",
            "excluded_method": "unknown",
            "rows_after_right_edge_excluded": True,
        },
        "layer_license": {
            "licensed": ["MACRO", "MICRO"],
            "forbidden": ["MICRO_MICRO", "TICK_TIMING"],
        },
        "spike_atlas": spike_receipts,
        "output": {
            "path": str(output),
            "sha256": sha256_file(output),
            "bytes": output.stat().st_size,
            "rows": rows_written,
            "by_category": dict(sorted(by_category.items())),
        },
        "exclusions": dict(sorted(skipped.items())),
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
