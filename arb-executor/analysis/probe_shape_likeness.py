#!/usr/bin/env python3
"""Read-only shape-likeness probe over the durable range-overlap library.

The probe reads custody inputs and writes one requested JSON report. It never
changes the library, trace, tapes, or engine files.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo


EXPECTED_LIBRARY_SHA256 = "019d84b0500a79c5d762d95ae7f481c3ae9a5bd5f0818f81aea9207a27fdd76e"
ALTGAS_EVENT = "KXATPMATCH-26JUL12ALTGAS"
GIUBAR_EVENT = "KXATPCHALLENGERMATCH-26JUL12GIUBAR"
ALTGAS_FRACTIONS = (0.075, 0.21, 0.33, 0.55)
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90)
TOP_CLOSEST = 20
NEW_YORK = ZoneInfo("America/New_York")
SERIES = ("favorite_last", "favorite_bid", "favorite_ask", "underdog_last", "underdog_bid", "underdog_ask")


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def finite(value):
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def compact(value):
    parsed = finite(value)
    if parsed is None:
        return None
    rounded = round(parsed)
    return int(rounded) if abs(parsed - rounded) < 1e-12 else parsed


def tape_cents(value, zero_is_null: bool = False):
    parsed = finite(value)
    if parsed is None or (zero_is_null and parsed == 0):
        return None
    return compact(parsed)


def date_code(event_id: str):
    match = re.search(r"-(\d{2}[A-Z]{3}\d{2})", event_id)
    return match.group(1) if match else None


def tape_epoch(text: str) -> float:
    parsed = datetime.strptime(text, "%Y-%m-%d %I:%M:%S %p")
    return parsed.replace(tzinfo=NEW_YORK).timestamp()


def trace_queries(trace_path: str):
    wanted = {ALTGAS_EVENT, GIUBAR_EVENT}
    first = {}
    giubar_resolved = []
    with gzip.open(trace_path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            event_id = row.get("event_id")
            if event_id not in wanted or row.get("kind") != "DECISION_STAGE":
                continue
            if event_id not in first:
                derivations = row.get("derivations") or []
                vector = next((item.get("vector") for item in derivations if item.get("vector")), None)
                if not vector:
                    raise RuntimeError(f"FIRST_STAGE_VECTOR_MISSING {event_id}")
                oriented = vector.get("oriented_leg_ids") or []
                if len(oriented) != 2:
                    raise RuntimeError(f"FIRST_STAGE_ORIENTATION_MISSING {event_id}")
                anchors = {
                    oriented[0]: compact(vector.get("leg0_anchor_cents")),
                    oriented[1]: compact(vector.get("leg1_anchor_cents")),
                }
                if any(value is None for value in anchors.values()):
                    raise RuntimeError(f"FIRST_STAGE_ANCHOR_MISSING {event_id}")
                favorite, underdog = sorted(anchors, key=lambda leg: (-anchors[leg], leg))
                formation = finite(row.get("timestamp_epoch"))
                hours_to_bell = finite(((row.get("reads") or {}).get("time_in_window") or {}).get("value", {}).get("hours_to_truth_bell"))
                if formation is None or hours_to_bell is None:
                    raise RuntimeError(f"FIRST_STAGE_CLOCK_MISSING {event_id}")
                first[event_id] = {
                    "event_id": event_id,
                    "event_date": date_code(event_id),
                    "category": vector.get("category"),
                    "formation_end_epoch": formation,
                    "bell_epoch": formation + hours_to_bell * 3600,
                    "hours_to_bell_at_formation": hours_to_bell,
                    "favorite_leg_id": favorite,
                    "underdog_leg_id": underdog,
                    "anchors_cents": {favorite: anchors[favorite], underdog: anchors[underdog]},
                    "first_stage_receipt": row.get("receipt"),
                }
            if event_id == GIUBAR_EVENT and len(giubar_resolved) < 2:
                beliefs = (((row.get("layers") or {}).get("micro") or {}).get("context") or {}).get("beliefs") or {}
                if beliefs and all((belief or {}).get("status") == "RESOLVED" for belief in beliefs.values()):
                    spec = first[event_id]
                    fraction = (float(row["timestamp_epoch"]) - spec["formation_end_epoch"]) / (spec["bell_epoch"] - spec["formation_end_epoch"])
                    giubar_resolved.append({
                        "fraction": fraction,
                        "timestamp_epoch": row.get("timestamp_epoch"),
                        "receipt": row.get("receipt"),
                    })
            if len(first) == len(wanted) and len(giubar_resolved) == 2:
                break
    if set(first) != wanted:
        raise RuntimeError(f"TRACE_FIRST_STAGE_MISSING {sorted(wanted - set(first))}")
    if len(giubar_resolved) != 2:
        raise RuntimeError("GIUBAR_FIRST_TWO_RESOLVED_STAGES_MISSING")
    return first, giubar_resolved


def read_tape(path: str, formation: float, bell: float):
    raw_rows = []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        for row_number, row in enumerate(csv.DictReader(stream), 2):
            try:
                epoch = tape_epoch(row.get("ts_et") or "")
            except (TypeError, ValueError):
                continue
            if epoch > bell:
                break
            state = {
                "last": tape_cents(row.get("last_trade"), zero_is_null=True),
                "bid": tape_cents(row.get("bid_1")),
                "ask": tape_cents(row.get("ask_1")),
            }
            raw_rows.append((epoch, row_number, state))
    before = [entry for entry in raw_rows if entry[0] <= formation]
    if not before:
        raise RuntimeError(f"TAPE_HAS_NO_STATE_AT_FORMATION {path}")
    points = [{"fraction": 0.0, "row_number": before[-1][1], **before[-1][2]}]
    prior = tuple(before[-1][2].get(key) for key in ("last", "bid", "ask"))
    span = bell - formation
    for epoch, row_number, state in raw_rows:
        if epoch <= formation:
            continue
        signature = tuple(state.get(key) for key in ("last", "bid", "ask"))
        if signature == prior:
            continue
        prior = signature
        point = {"fraction": (epoch - formation) / span, "row_number": row_number, **state}
        if points and point["fraction"] == points[-1]["fraction"]:
            points[-1] = point
        else:
            points.append(point)
    return points


def sample_path(path, fraction: float):
    selected = None
    for point in path:
        if finite(point.get("window_fraction", point.get("fraction"))) > fraction:
            break
        selected = point
    return selected


def load_query_pair(spec, tape_dir: str, checkpoints):
    paths = {}
    for leg_id in (spec["favorite_leg_id"], spec["underdog_leg_id"]):
        tape_path = os.path.join(tape_dir, f"{spec['event_id']}-{leg_id}.csv.gz")
        if not os.path.isfile(tape_path):
            raise RuntimeError(f"TAPE_MISSING {tape_path}")
        paths[leg_id] = read_tape(tape_path, spec["formation_end_epoch"], spec["bell_epoch"])
    maximum = max(item["fraction"] for item in checkpoints)
    grid = sorted({point["fraction"] for path in paths.values() for point in path if point["fraction"] <= maximum})
    if not grid or grid[0] != 0.0:
        raise RuntimeError(f"QUERY_GRID_HAS_NO_FORMATION {spec['event_id']}")
    records = []
    for fraction in grid:
        favorite = sample_path(paths[spec["favorite_leg_id"]], fraction)
        underdog = sample_path(paths[spec["underdog_leg_id"]], fraction)
        records.append(pair_vector(favorite, underdog, spec["anchors_cents"][spec["favorite_leg_id"]], spec["anchors_cents"][spec["underdog_leg_id"]], fraction))
    return {"spec": spec, "paths": paths, "grid": grid, "records": records, "checkpoints": checkpoints}


def point_value(point, field):
    if point is None:
        return None
    library_field = {"last": "last_cents", "bid": "bid_cents", "ask": "ask_cents"}[field]
    value = point.get(field) if field in point else point.get(library_field)
    return compact(value)


def pair_vector(favorite, underdog, favorite_anchor, underdog_anchor, fraction):
    levels = {
        "favorite_last": point_value(favorite, "last"),
        "favorite_bid": point_value(favorite, "bid"),
        "favorite_ask": point_value(favorite, "ask"),
        "underdog_last": point_value(underdog, "last"),
        "underdog_bid": point_value(underdog, "bid"),
        "underdog_ask": point_value(underdog, "ask"),
    }
    deltas = {
        key: (value - (favorite_anchor if key.startswith("favorite_") else underdog_anchor)) if value is not None else None
        for key, value in levels.items()
    }
    if levels["favorite_last"] is not None and levels["underdog_last"] is not None:
        last_sum = levels["favorite_last"] + levels["underdog_last"]
        mirror_gap = last_sum - 100
    else:
        last_sum = None
        mirror_gap = None
    return {
        "fraction": fraction,
        "level_cents": levels,
        "delta_from_anchor_cents": deltas,
        "favorite_plus_underdog_last_cents": last_sum,
        "mirror_gap_from_100_cents": mirror_gap,
    }


def orient_library_pair(rows):
    if len(rows) != 2:
        return None
    ordered = sorted(rows, key=lambda row: (-row["anchor_cents"], row["leg_id"]))
    return ordered[0], ordered[1]


def aligned_member_records(pair, grid):
    favorite, underdog = pair
    favorite_points = sample_path_many(favorite["path"], grid)
    underdog_points = sample_path_many(underdog["path"], grid)
    return [
        pair_vector(
            favorite_point,
            underdog_point,
            favorite["anchor_cents"],
            underdog["anchor_cents"],
            fraction,
        )
        for fraction, favorite_point, underdog_point in zip(grid, favorite_points, underdog_points)
    ]


def sample_path_many(path, fractions):
    selected = None
    index = 0
    sampled = []
    for fraction in fractions:
        while index < len(path):
            point_fraction = finite(path[index].get("window_fraction", path[index].get("fraction")))
            if point_fraction is None or point_fraction > fraction:
                break
            selected = path[index]
            index += 1
        sampled.append(selected)
    return sampled


def distance(query_records, member_records, basis: str, include_mirror: bool):
    total = 0.0
    compared = 0
    mirror_compared = 0
    for query, member in zip(query_records, member_records):
        left = query[basis]
        right = member[basis]
        for series in SERIES:
            if left[series] is None or right[series] is None:
                continue
            total += abs(left[series] - right[series])
            compared += 1
        if include_mirror:
            query_gap = query["mirror_gap_from_100_cents"]
            member_gap = member["mirror_gap_from_100_cents"]
            if query_gap is not None and member_gap is not None:
                total += abs(query_gap - member_gap)
                compared += 1
                mirror_compared += 1
    return (total / compared if compared else None), compared, mirror_compared


def eventual_dip(row, fraction):
    current = sample_path(row["path"], fraction)
    final = row["path"][-1] if row.get("path") else None
    current_low = compact((current or {}).get("seen_true_trade_low_cents"))
    final_low = compact((final or {}).get("seen_true_trade_low_cents"))
    return current_low - final_low if current_low is not None and final_low is not None else None


def weighted_quantile(rows, quantile):
    ordered = sorted((value, weight) for value, weight in rows if value is not None and weight > 0)
    total = sum(weight for _, weight in ordered)
    if not ordered or not total:
        return None
    target = total * quantile
    cumulative = 0.0
    for value, weight in ordered:
        cumulative += weight
        if cumulative >= target:
            return value
    return ordered[-1][0]


def distribution(records, side):
    field = f"{side}_eventual_dip_cents"
    rows = [(record[field], record["weight"]) for record in records if record.get(field) is not None]
    total = sum(weight for _, weight in rows)
    zero = sum(weight for value, weight in rows if value == 0)
    return {
        "members": len(rows),
        "weight_sum": total,
        "q10": weighted_quantile(rows, 0.10),
        "q25": weighted_quantile(rows, 0.25),
        "q50": weighted_quantile(rows, 0.50),
        "q75": weighted_quantile(rows, 0.75),
        "q90": weighted_quantile(rows, 0.90),
        "weighted_share_dip_zero": zero / total if total else None,
    }


def summarize(records, distance_field):
    weighted = []
    for record in records:
        value = record[distance_field]["distance_cents"]
        if value is None:
            continue
        item = {
            "event_id": record["event_id"],
            "distance_cents": value,
            "compared_values": record[distance_field]["compared_values"],
            "mirror_gap_values": record[distance_field]["mirror_gap_values"],
            "favorite_eventual_dip_cents": record["favorite_eventual_dip_cents"],
            "underdog_eventual_dip_cents": record["underdog_eventual_dip_cents"],
            "favorite_leg_id": record["favorite_leg_id"],
            "underdog_leg_id": record["underdog_leg_id"],
        }
        item["weight"] = 1 / (1 + value)
        weighted.append(item)
    weighted.sort(key=lambda row: (row["distance_cents"], row["event_id"]))
    sum_weight = sum(row["weight"] for row in weighted)
    sum_weight_squared = sum(row["weight"] ** 2 for row in weighted)
    ess = sum_weight ** 2 / sum_weight_squared if sum_weight_squared else 0
    closest_ess_count = min(len(weighted), math.ceil(ess))
    closest_ess = weighted[:closest_ess_count]
    return {
        "pool_pairs": len(weighted),
        "weight_sum": sum_weight,
        "effective_sample_size": ess,
        "closest_20": weighted[:TOP_CLOSEST],
        "whole_pool": {
            "favorite": distribution(weighted, "favorite"),
            "underdog": distribution(weighted, "underdog"),
        },
        "closest_ess": {
            "selection_rule": "first ceil(effective_sample_size) pairs after ascending distance, event_id tiebreak",
            "pairs": closest_ess_count,
            "favorite": distribution(closest_ess, "favorite"),
            "underdog": distribution(closest_ess, "underdog"),
        },
    }


def analyze_checkpoint(query, checkpoint, member_pairs):
    fraction = checkpoint["fraction"]
    grid_count = sum(1 for value in query["grid"] if value <= fraction)
    query_records = query["records"][:grid_count]
    records = []
    for favorite, underdog in member_pairs:
        member_records = aligned_member_records((favorite, underdog), query["grid"][:grid_count])
        item = {
            "event_id": favorite["event_id"],
            "favorite_leg_id": favorite["leg_id"],
            "underdog_leg_id": underdog["leg_id"],
            "favorite_eventual_dip_cents": eventual_dip(favorite, fraction),
            "underdog_eventual_dip_cents": eventual_dip(underdog, fraction),
        }
        for basis_name, basis_field in (("level", "level_cents"), ("delta", "delta_from_anchor_cents")):
            for mirror_name, include_mirror in (("without_mirror", False), ("with_mirror", True)):
                value, compared, mirror_compared = distance(query_records, member_records, basis_field, include_mirror)
                item[f"{basis_name}_{mirror_name}"] = {
                    "distance_cents": value,
                    "compared_values": compared,
                    "mirror_gap_values": mirror_compared,
                }
        records.append(item)
    modes = {
        mode: summarize(records, mode)
        for mode in ("level_without_mirror", "level_with_mirror", "delta_without_mirror", "delta_with_mirror")
    }
    endpoint = pair_vector(
        sample_path(query["paths"][query["spec"]["favorite_leg_id"]], fraction),
        sample_path(query["paths"][query["spec"]["underdog_leg_id"]], fraction),
        query["spec"]["anchors_cents"][query["spec"]["favorite_leg_id"]],
        query["spec"]["anchors_cents"][query["spec"]["underdog_leg_id"]],
        fraction,
    )
    return {
        **checkpoint,
        "hours_from_formation": fraction * query["spec"]["hours_to_bell_at_formation"],
        "query_change_point_grid_count": grid_count,
        "query_endpoint": endpoint,
        "modes": modes,
    }


def load_member_pairs(library_path, queries):
    pending = {}
    selected = {query["spec"]["event_id"]: [] for query in queries}
    category_counts = {}
    tie_anchor_pairs = 0
    with gzip.open(library_path, "rt", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            event_id = row["event_id"]
            rows = pending.setdefault(event_id, [])
            rows.append(row)
            if len(rows) < 2:
                continue
            if len(rows) > 2:
                raise RuntimeError(f"LIBRARY_EVENT_HAS_MORE_THAN_TWO_LEGS {event_id}")
            pair = orient_library_pair(rows)
            del pending[event_id]
            favorite, underdog = pair
            category = favorite.get("category")
            category_counts[category] = category_counts.get(category, 0) + 1
            if favorite["anchor_cents"] == underdog["anchor_cents"]:
                tie_anchor_pairs += 1
            member_date = date_code(event_id)
            for query in queries:
                spec = query["spec"]
                if category != spec["category"] or event_id == spec["event_id"] or member_date == spec["event_date"]:
                    continue
                selected[spec["event_id"]].append(pair)
    if pending:
        raise RuntimeError(f"LIBRARY_UNPAIRED_EVENTS count={len(pending)}")
    return selected, category_counts, tie_anchor_pairs


def format_distribution(value):
    zero = value["weighted_share_dip_zero"]
    zero_text = "null" if zero is None else f"{zero * 100:.2f}%"
    return f"{value['q10']}/{value['q25']}/{value['q50']}/{value['q75']}/{value['q90']} · zero {zero_text}"


def print_tables(report):
    for query in report["queries"]:
        spec = query["spec"]
        print(f"\n## {spec['event_id']} ({spec['category']})")
        print(f"favorite {spec['favorite_leg_id']}@{spec['anchors_cents'][spec['favorite_leg_id']]} · underdog {spec['underdog_leg_id']}@{spec['anchors_cents'][spec['underdog_leg_id']]}")
        for checkpoint in query["results"]:
            print(f"\n### f={checkpoint['fraction']:.12f} ({checkpoint['hours_from_formation']:.6f}h; grid={checkpoint['query_change_point_grid_count']})")
            print("| mode | pool | ESS | whole favorite q10/q25/q50/q75/q90 | whole underdog | closest-ESS n | ESS favorite | ESS underdog |")
            print("|---|---:|---:|---|---|---:|---|---|")
            for mode, summary in checkpoint["modes"].items():
                print(f"| {mode} | {summary['pool_pairs']} | {summary['effective_sample_size']:.6f} | {format_distribution(summary['whole_pool']['favorite'])} | {format_distribution(summary['whole_pool']['underdog'])} | {summary['closest_ess']['pairs']} | {format_distribution(summary['closest_ess']['favorite'])} | {format_distribution(summary['closest_ess']['underdog'])} |")
            print("\n| mode | 20 closest: event:distance:favorite-dip/underdog-dip |")
            print("|---|---|")
            for mode, summary in checkpoint["modes"].items():
                closest = "; ".join(
                    f"{row['event_id']}:{row['distance_cents']:.6f}:{row['favorite_eventual_dip_cents']}/{row['underdog_eventual_dip_cents']}"
                    for row in summary["closest_20"]
                )
                print(f"| {mode} | {closest} |")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--trace", required=True)
    parser.add_argument("--tape-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    library = os.path.abspath(args.library)
    trace = os.path.abspath(args.trace)
    tape_dir = os.path.abspath(args.tape_dir)
    output = os.path.abspath(args.output)
    library_sha256 = sha256_file(library)
    if library_sha256 != EXPECTED_LIBRARY_SHA256:
        raise RuntimeError(f"RANGE_OVERLAP_LIBRARY_SHA256_MISMATCH {library_sha256}")

    specs, giubar_resolved = trace_queries(trace)
    query_inputs = [
        load_query_pair(specs[ALTGAS_EVENT], tape_dir, [{"fraction": value, "source": "OPERATOR_REQUESTED"} for value in ALTGAS_FRACTIONS]),
        load_query_pair(specs[GIUBAR_EVENT], tape_dir, [{**value, "source": "FIRST_TWO_MICRO_RESOLVED_STAGES"} for value in giubar_resolved]),
    ]
    selected, category_counts, tie_anchor_pairs = load_member_pairs(library, query_inputs)
    query_reports = []
    for query in query_inputs:
        event_id = query["spec"]["event_id"]
        results = [analyze_checkpoint(query, checkpoint, selected[event_id]) for checkpoint in query["checkpoints"]]
        query_reports.append({
            "spec": query["spec"],
            "query_change_point_grid": query["records"],
            "results": results,
        })

    report = {
        "label": "SHAPE_LIKENESS_READ_ONLY_PROBE",
        "inputs": {
            "range_overlap_library": {"path": library, "sha256": library_sha256},
            "trace": {"path": trace, "sha256": sha256_file(trace)},
            "tape_dir": tape_dir,
        },
        "method": {
            "orientation": "favorite is the higher anchor; underdog is second; leg_id breaks an equal-anchor tie",
            "grid": "union of the query pair's own last/bid/ask tape change points from formation through the checkpoint",
            "sampling": "largest stored path change point with window_fraction <= each query-grid fraction",
            "six_series": list(SERIES),
            "level_basis": "stored cents",
            "delta_basis": "stored cents minus that side's anchor_cents",
            "seventh_series": "favorite_last + underdog_last - 100, in cents; distance is identical if represented as the raw last sum because subtracting 100 cancels",
            "missing_values": "pairwise omitted only; no print, book, anchor, or mirror value is substituted",
            "distance": "mean absolute difference over all jointly stored sampled values",
            "weight": "1 / (1 + distance)",
            "effective_sample_size": "sum(weight)^2 / sum(weight^2)",
            "eventual_dip": "seen_true_trade_low_cents at checkpoint minus final stored seen_true_trade_low_cents",
            "weighted_quantile": "first value whose ascending cumulative weight reaches the requested fraction; no interpolation",
            "closest_ess": "first ceil(effective_sample_size) pairs by ascending distance, event_id tiebreak",
            "leave_out": "exclude the query event and events with the same date code",
        },
        "library_pair_counts_by_category": category_counts,
        "equal_anchor_pair_count_all_categories": tie_anchor_pairs,
        "queries": query_reports,
    }
    os.makedirs(os.path.dirname(output), exist_ok=True)
    temporary = f"{output}.tmp"
    with open(temporary, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary, output)
    print(f"wrote {output}")
    print(f"library sha256 {library_sha256}")
    print(f"trace sha256 {report['inputs']['trace']['sha256']}")
    print_tables(report)


if __name__ == "__main__":
    main()
