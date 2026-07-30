#!/usr/bin/env python3
"""Honest cell-level Window-1 refit on exact-bell games.

This is a comparison against the ratified SEQFLOOR recut_cells.json surface,
not a replacement aim surface.  Timing remains descriptive and is never
promoted to an entry trigger.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import statistics
from typing import Iterable

from window1_live_v4_replay import build_print_index, load_print_block


DEFAULT_EVENTS = Path(
    r"C:\Users\omigr\OMI-Window1-private\joined\events.jsonl"
)
DEFAULT_PRINTS = Path(
    r"C:\Users\omigr\OMI-Window1-private\fit-local\prints.jsonl"
)
DEFAULT_PRINT_INDEX = Path(
    r"C:\tmp\window1-actual-bell-refit\prints_by_ticker.json"
)
DEFAULT_BOOKS = Path(
    r"C:\Users\omigr\OMI-Window1-private\fit-local\depth_recorder"
)
STARTS = Path(
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
FULL = Path(
    ".claude/window1_t2_iteration_history/WINDOW1_FULL_LAWFUL_CEILING.json"
)
RECUT = Path(".claude/seqfloor_20260708/recut_cells.json")
ATLAS = Path(".claude/trendpath/ATLAS_V1.json")
DEFAULT_OUT = Path(
    ".claude/window1_live_v4_replay/actual_bell_refit_20260729"
)

GRID_CATEGORIES = (
    "ATP_CHALL",
    "ATP_MAIN",
    "ITF_M",
    "ITF_W",
    "WTA_CHALL",
    "WTA_MAIN",
)
GRID_CELLS = tuple(range(5, 95))
THIN_N = 20
MAX_BOOK_AGE_SECONDS = 300.0

POSTURES = {
    "JOIN": {
        "formula": "best_bid",
        "denominator": "that leg's archived best_ask - best_bid",
    },
    "TOUCH_MINUS_1": {
        "formula": "best_bid - 1 cent",
        "denominator": "that leg's archived best_ask - best_bid",
    },
    "ONE_SPREAD_BELOW_MID": {
        "formula": (
            "(best_bid + best_ask) / 2 - "
            "1 * (best_ask - best_bid)"
        ),
        "denominator": "that leg's archived best_ask - best_bid",
    },
    "TWO_SPREADS_BELOW_MID": {
        "formula": (
            "(best_bid + best_ask) / 2 - "
            "2 * (best_ask - best_bid)"
        ),
        "denominator": "that leg's archived best_ask - best_bid",
    },
}


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def epoch(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def q(values: Iterable[float], fraction: float) -> float | None:
    rows = sorted(float(value) for value in values)
    if not rows:
        return None
    index = min(len(rows) - 1, max(0, int(len(rows) * fraction)))
    return rows[index]


def distribution(values: Iterable[float]) -> dict:
    rows = [float(value) for value in values]
    return {
        "n": len(rows),
        "min": min(rows) if rows else None,
        "p10": q(rows, 0.10),
        "p25": q(rows, 0.25),
        "median": statistics.median(rows) if rows else None,
        "p75": q(rows, 0.75),
        "p90": q(rows, 0.90),
        "max": max(rows) if rows else None,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def grid_cell(price: float) -> int | None:
    value = int(price)
    if float(value) != float(price):
        raise RuntimeError(f"non-integer traded price cannot key grid: {price}")
    return value if 5 <= value < 95 else None


def aim_zone(cell: int) -> str:
    if cell < 50:
        return "JOIN"
    if cell < 75:
        return "SHALLOW"
    return "DEEP"


def book_target(posture: str, bid: float, ask: float) -> float:
    spread = ask - bid
    if posture == "JOIN":
        return bid
    if posture == "TOUCH_MINUS_1":
        return bid - 1.0
    # A constructed midpoint exists only inside these two canonical formulas.
    if posture == "ONE_SPREAD_BELOW_MID":
        return (bid + ask) / 2.0 - spread
    if posture == "TWO_SPREADS_BELOW_MID":
        return (bid + ask) / 2.0 - 2.0 * spread
    raise KeyError(posture)


def scan_books(
    directory: Path, close_by_ticker: dict[str, float]
) -> tuple[dict[str, dict], dict]:
    if not directory.exists():
        raise RuntimeError(f"archived BBO directory is absent: {directory}")
    files = sorted(directory.rglob("*.gz"))
    selected: dict[str, dict] = {}
    physical_rows = 0
    target_rows = 0
    malformed_rows = 0
    invalid_books = 0
    for path in files:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                physical_rows += 1
                try:
                    row = json.loads(line)
                    ticker = str(row.get("ticker") or "")
                    if ticker not in close_by_ticker:
                        continue
                    target_rows += 1
                    ts = float(row.get("ts_epoch") or row.get("ts"))
                    bid = float(row["bid"])
                    ask = float(row["ask"])
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    malformed_rows += 1
                    continue
                if not (0 < bid < ask < 100):
                    invalid_books += 1
                    continue
                if ts > close_by_ticker[ticker]:
                    continue
                previous = selected.get(ticker)
                if previous is None or ts > previous["ts"]:
                    selected[ticker] = {
                        "ts": ts,
                        "best_bid_cents": bid,
                        "best_ask_cents": ask,
                    }
    manifest_rows = [
        {
            "path": str(path),
            "bytes": path.stat().st_size,
            "mtime_ns": path.stat().st_mtime_ns,
        }
        for path in files
    ]
    manifest_hash = hashlib.sha256(
        json.dumps(
            manifest_rows, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    return selected, {
        "directory": str(directory),
        "gzip_files": len(files),
        "physical_rows_scanned": physical_rows,
        "target_ticker_rows_scanned": target_rows,
        "malformed_target_rows": malformed_rows,
        "invalid_or_crossed_target_books": invalid_books,
        "source_manifest_sha256": manifest_hash,
        "source_manifest_definition": (
            "sha256 of sorted path/byte-size/source-mtime-ns rows; "
            "not a content hash of the private archive"
        ),
    }


def attach_book_denominators(
    legs: list[dict], selected: dict[str, dict], census: dict
) -> None:
    statuses = Counter()
    no_denominator_reasons = Counter()
    ages = []
    for row in legs:
        book = selected.get(row["ticker"])
        if book is None:
            row["book_denominator"] = {
                "status": "NO_DENOMINATOR",
                "reason": "no valid archived BBO at or before W1 close",
            }
            statuses["NO_DENOMINATOR"] += 1
            no_denominator_reasons["NO_VALID_BOOK_AT_OR_BEFORE_CLOSE"] += 1
            continue
        age = float(row["close_ts"]) - float(book["ts"])
        if age < 0 or age > MAX_BOOK_AGE_SECONDS:
            row["book_denominator"] = {
                "status": "NO_DENOMINATOR",
                "reason": (
                    "last archived BBO is stale relative to W1 close "
                    f"({age:.3f}s > {MAX_BOOK_AGE_SECONDS:.0f}s)"
                ),
                "last_book_age_seconds": age,
            }
            statuses["NO_DENOMINATOR"] += 1
            no_denominator_reasons["STALE_GT_300_SECONDS"] += 1
            continue
        bid = float(book["best_bid_cents"])
        ask = float(book["best_ask_cents"])
        spread = ask - bid
        row["book_denominator"] = {
            "status": "AVAILABLE",
            "book_ts": book["ts"],
            "age_seconds": age,
            "best_bid_cents": bid,
            "best_ask_cents": ask,
            "spread_cents": spread,
        }
        statuses["AVAILABLE"] += 1
        ages.append(age)
    census["leg_status_counts"] = dict(sorted(statuses.items()))
    census["no_denominator_reason_counts"] = dict(
        sorted(no_denominator_reasons.items())
    )
    census["available_book_age_seconds"] = distribution(ages)
    census["freshness_rule_seconds"] = MAX_BOOK_AGE_SECONDS
    census["fallback_used"] = False


def posture_summary(members: list[dict], posture: str) -> dict:
    denominator = 0
    reached = 0
    for row in members:
        book = row["book_denominator"]
        if book["status"] != "AVAILABLE":
            continue
        target = book_target(
            posture,
            float(book["best_bid_cents"]),
            float(book["best_ask_cents"]),
        )
        if not (1 <= target <= 99):
            continue
        denominator += 1
        reached += float(row["low_price_cents"]) <= target
    return {
        **POSTURES[posture],
        "n_denominator": denominator,
        "n_reached": reached,
        "reach_fraction": reached / denominator if denominator else None,
        "fill_rule": "resting order fills when true traded price touches target",
        "depth_proof_required": False,
    }


def build_cell_comparison(
    legs: list[dict], recut: dict
) -> list[dict]:
    grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in legs:
        if row["grid_cell"] is not None:
            grouped[(row["category"], row["grid_cell"])].append(row)

    result = []
    for category in GRID_CATEGORIES:
        prior_category = recut.get(category, {})
        for cell in GRID_CELLS:
            members = grouped.get((category, cell), [])
            prior = prior_category.get(str(cell))
            exact_edges = distribution(
                row["depth_below_window1_close_cents"] for row in members
            )
            exact_times = distribution(
                row["low_tminus_actual_bell_minutes"] for row in members
            )
            books = [
                row for row in members
                if row["book_denominator"]["status"] == "AVAILABLE"
            ]
            prior_edge = (
                float(prior["edge_p50"]) if prior is not None else None
            )
            exact_edge = exact_edges["median"]
            exact_spreads = [
                row["depth_below_window1_close_cents"]
                / row["book_denominator"]["spread_cents"]
                for row in books
            ]
            prior_spreads = [
                prior_edge / row["book_denominator"]["spread_cents"]
                for row in books
                if prior_edge is not None
            ]
            signed_spreads = [
                (
                    row["depth_below_window1_close_cents"] - prior_edge
                ) / row["book_denominator"]["spread_cents"]
                for row in books
                if prior_edge is not None
            ]
            if not members:
                status = "NO_EXACT_BELL_SAMPLE"
            elif len(members) < THIN_N:
                status = "THIN_EXACT_BELL_SAMPLE"
            else:
                status = "FIT"
            result.append({
                "category": category,
                "cell": cell,
                "aim_zone_ratified": aim_zone(cell),
                "status": status,
                "thin_threshold_n": THIN_N,
                "prior": {
                    "source": str(RECUT),
                    "n": int(prior["n"]) if prior else 0,
                    "status": (
                        "ABSENT"
                        if prior is None
                        else "THIN"
                        if int(prior["n"]) < THIN_N
                        else "FIT"
                    ),
                    "edge_p25_cents_compatibility_only": (
                        prior.get("edge_p25") if prior else None
                    ),
                    "edge_p50_cents_compatibility_only": prior_edge,
                    "edge_p75_cents_compatibility_only": (
                        prior.get("edge_p75") if prior else None
                    ),
                    "legacy_t_deep_p50_raw_descriptive_only": (
                        prior.get("t_deep_p50") if prior else None
                    ),
                },
                "exact_bell": {
                    "n": len(members),
                    "n_with_spread_denominator": len(books),
                    "n_no_denominator": len(members) - len(books),
                    "edge_cents_compatibility_only": exact_edges,
                    "low_tminus_actual_bell_minutes_descriptive_only": (
                        exact_times
                    ),
                },
                "requested_signed_comparison": {
                    "unit": "cents; compatibility comparison only",
                    "formula": (
                        "exact-bell median(close-last-trade minus low) "
                        "- recut_cells edge_p50"
                    ),
                    "value": (
                        exact_edge - prior_edge
                        if exact_edge is not None and prior_edge is not None
                        else None
                    ),
                },
                "spread_normalized_comparison": {
                    "denominator": (
                        "each leg's own fresh archived "
                        "(best_ask - best_bid) at W1 close"
                    ),
                    "actual_close_to_low_spreads": distribution(exact_spreads),
                    "prior_edge_p50_spreads": distribution(prior_spreads),
                    "actual_minus_prior_spreads": distribution(signed_spreads),
                    "no_midpoint_anchor_used": True,
                },
                "canonical_posture_reach": {
                    posture: posture_summary(members, posture)
                    for posture in POSTURES
                },
            })
    return result


def count_mapping(obj: dict, key: str) -> int:
    value = obj.get(key, {})
    return len(value) if isinstance(value, dict) else 0


def surface_census(repo: Path, recut: dict) -> list[dict]:
    atlas = read_json(repo / ATLAS)
    cohort = read_json(repo / "arb-executor/state/cohort_surface_v1.json")
    library = read_json(repo / ".claude/trendpath/LIBRARY_V1.json")
    range_layer = read_json(
        repo / ".claude/range_layer/RANGE_LAYER_3WAY.json"
    )
    band_map = read_json(repo / "arb-executor/state/band_map_v1.json")
    drift = read_json(repo / "arb-executor/state/drift_surfaces_v1.json")
    pair = read_json(
        repo / "arb-executor/state/pair_policies_sealed_v1.json"
    )
    entry = read_json(
        repo / "arb-executor/state/entry_tables_sealed_v1.json"
    )
    guide = read_json(repo / ".claude/guidebook/GUIDEBOOK_V1.json")
    orient = read_json(repo / ".claude/trendpath/ORIENT_V1.json")
    aim_v2 = read_json(
        repo / "arb-executor/data/shape_corpus/"
        "aim_v2_operational_LATCHCAL.json"
    )
    aim_table = read_json(repo / "arb-executor/docs/policy/aim_table.json")
    band_count = sum(
        len(value.get("bands", []))
        for value in band_map.get("cats", {}).values()
    )
    recut_cells = sum(len(value) for value in recut.values())
    recut_legs = sum(
        int(cell["n"])
        for category in recut.values()
        for cell in category.values()
    )
    recut_lawful_grid_legs = sum(
        int(category[str(cell)]["n"])
        for category in recut.values()
        for cell in GRID_CELLS
        if str(cell) in category
    )
    with (repo / "arb-executor/docs/policy/per_regime_offsets_v2.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        regime_rows = sum(1 for _ in csv.DictReader(handle))
    with (repo / "arb-executor/docs/policy/engagement_cells_v1.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        engagement_rows = sum(1 for _ in csv.DictReader(handle))

    return [
        {
            "surface": str(RECUT),
            "rows": recut_cells,
            "fitted_legs": recut_legs,
            "lawful_grid_legs": recut_lawful_grid_legs,
            "outside_grid_evidence_legs": (
                recut_legs - recut_lawful_grid_legs
            ),
            "key": "category|own W1-close one-cent cell",
            "role_keyed": False,
            "verdict": "RATIFIED_PRIOR",
            "note": (
                "The source contains raw evidence outside [5,95); this report "
                "consumes only the 90 lawful cells 5..94 and never clamps."
            ),
        },
        {
            "surface": str(ATLAS),
            "rows": count_mapping(atlas, "pages"),
            "key": "category|leader/underdog|le25/26_50/51_75/ge75",
            "role_keyed": True,
            "verdict": "C45_RETIRED",
            "live_effect": "path aim and selector; live_v4.py:2852-2923,4108-4144",
        },
        {
            "surface": "arb-executor/state/cohort_surface_v1.json",
            "rows": count_mapping(cohort, "cells"),
            "key": "category|fav/dog|le25/26_50/51_75/ge76",
            "role_keyed": True,
            "verdict": "C45_RETIRED",
            "live_effect": "cohort authority/steer; live_v4.py:3734-3770,4059-4072",
        },
        {
            "surface": ".claude/range_layer/RANGE_LAYER_3WAY.json",
            "rows": count_mapping(range_layer, "cells"),
            "key": (
                "category|leader/underdog|range-shape|"
                "le25/26_50/51_75/ge75"
            ),
            "role_keyed": True,
            "verdict": "C45_RETIRED",
            "live_effect": "range dossier/position prior; live_v4.py:3303-3318,9496-9534",
        },
        {
            "surface": ".claude/trendpath/ORIENT_V1.json",
            "rows": sum(
                len(value) for value in orient.get("cats", {}).values()
            ),
            "key": "category|drift/range/flow cell with dog_rise_rate payload",
            "role_keyed": True,
            "verdict": "C45_ROLE_SEMANTIC_RETIRED",
            "live_effect": "authority orientation; live_v4.py:3629-3725,4033-4079",
        },
        {
            "surface": ".claude/trendpath/LIBRARY_V1.json",
            "rows": count_mapping(library, "cells"),
            "key": "category|le25/26_50/51_75/ge75|volume band",
            "role_keyed": False,
            "verdict": "RETIRED_BROAD_PRICE_BAND",
            "live_effect": "dossier consultation; live_v4.py:3480-3515",
        },
        {
            "surface": "arb-executor/docs/policy/aim_table.json",
            "rows": sum(
                len(value) for value in aim_table.get("aim", {}).values()
            ),
            "key": "category|01-20/21-40/41-49/50-59/60-79/80-99",
            "role_keyed": False,
            "verdict": "RETIRED_BROAD_PRICE_BAND",
            "live_effect": "faller/riser order depth; live_v4.py:2660-2694,4667-4668",
        },
        {
            "surface": "arb-executor/docs/policy/per_regime_offsets_v2.csv",
            "rows": regime_rows,
            "key": "category|nine 10-cent regimes",
            "role_keyed": False,
            "verdict": "RETIRED_BROAD_PRICE_BAND",
            "live_effect": "fallback entry offset; live_v4.py:2582-2610,5199-5220",
        },
        {
            "surface": "arb-executor/docs/policy/engagement_cells_v1.csv",
            "rows": engagement_rows,
            "key": "category|clock bucket|10-cent regime",
            "role_keyed": False,
            "verdict": "RETIRED_BROAD_BAND_AND_CLOCK_TRIGGER",
            "live_effect": "engagement gate; live_v4.py:4845-4870",
        },
        {
            "surface": "arb-executor/state/band_map_v1.json",
            "rows": band_count,
            "key": "category-B1..B8 learned shape clusters",
            "role_keyed": False,
            "verdict": "NOT_C45_ROLE_KEYED; NON_GRID_SHAPE_BAND",
            "live_effect": "recognition/shape lookup; live_v4.py:3807-3840",
            "note": (
                "A shape band may remain descriptive, but it cannot replace "
                "the ratified one-cent aim key."
            ),
        },
        {
            "surface": "arb-executor/state/drift_surfaces_v1.json",
            "rows": count_mapping(drift, "bands"),
            "key": (
                "category-Bn at top level; lifecycle subcells still use "
                "le25/26_50/51_75/ge76"
            ),
            "role_keyed": False,
            "verdict": "RETIRED_BROAD_SUBCELLS",
            "live_effect": "recognition/dossier; live_v4.py:3809-3840",
        },
        {
            "surface": "arb-executor/state/pair_policies_sealed_v1.json",
            "rows": count_mapping(pair, "bands"),
            "key": "category-Bn; no leader/underdog token",
            "role_keyed": False,
            "verdict": "NO_C45_ROLE_KEY; BAND_KEYED_ORDER_POLICY",
            "live_effect": "sealed order offset; live_v4.py:3974-4000,4723-4759",
        },
        {
            "surface": "arb-executor/state/entry_tables_sealed_v1.json",
            "rows": count_mapping(entry, "bands"),
            "key": "category-Bn; no leader/underdog token",
            "role_keyed": False,
            "verdict": "NO_C45_ROLE_KEY; BAND_KEYED_ENTRY_TABLE",
            "live_effect": "sealed entry lookup; live_v4.py:3777-3800",
        },
        {
            "surface": ".claude/guidebook/GUIDEBOOK_V1.json",
            "rows": count_mapping(guide, "pages"),
            "key": "category|one-cent cell",
            "role_keyed": False,
            "verdict": "CELL_KEY_COMPLIANT; ABSOLUTE_CENT_PAYLOAD_NEEDS_TRANSLATION",
            "live_effect": "dossier/authority consultation; live_v4.py:4194-4310",
        },
        {
            "surface": (
                "arb-executor/data/shape_corpus/"
                "aim_v2_operational_LATCHCAL.json"
            ),
            "rows": count_mapping(aim_v2, "table"),
            "key": (
                "category|favorite-price 20-cent bin|time bin; "
                "separate f/d payload fields"
            ),
            "role_keyed": True,
            "verdict": "C45_IMPLICIT_ROLE_AND_RETIRED_BANDS",
            "live_effect": "shadow log only; live_v4.py:4332-4365",
        },
    ]


def flow_state_audit() -> dict:
    return {
        "vault_section_5_primitive": (
            "(prints/min + spread-tightening), conditioned per category"
        ),
        "live_wiring": {
            "print_rate": (
                "PARTIAL: 30-minute WS/REST print count is bucketed "
                "quiet/warm/open in _entry_dossier "
                "(live_v4.py:3237-3280)"
            ),
            "spread_tightening": (
                "ABSENT from the dossier flow state; the logged object carries "
                "prints_30m/bucket/harvest rate only "
                "(live_v4.py:3349-3357)"
            ),
            "aim_activation": (
                "NOT WIRED: the dossier is observational and does not place "
                "orders (live_v4.py:3195-3205). Print-count guns and corridor "
                "gates act elsewhere, while check_pending_entries' spread "
                "path is disabled (live_v4.py:11963-12020,16135-16136)."
            ),
        },
        "required_change": [
            (
                "Maintain a per-ticker microstate from each trade and BBO: "
                "rolling print rate, current spread, and spread-tightening "
                "transition, all timestamped and stale-gated."
            ),
            (
                "Fit category-conditioned flow-state transitions from the "
                "subsecond tape. The one-cent cell surface supplies aim depth; "
                "it does not supply entry time."
            ),
            (
                "Gate aim activation on an observed flow-state transition "
                "(for example quiet-to-waking plus spread confirmation), never "
                "on per-minute atlas/cohort output."
            ),
            (
                "Fail closed when either trade flow or BBO state is absent or "
                "stale; emit the state and transition that armed each order."
            ),
            (
                "Replay both legs on the same event clock and verify that "
                "changing only the flow gate changes activation, not the "
                "ratified cell aim."
            ),
        ],
        "timing_surface_action": (
            "No timing surface was refitted as a trigger. Exact-bell T-minus "
            "values in this report are descriptive diagnostics only."
        ),
    }


def build(args: argparse.Namespace) -> dict:
    repo = args.repo.resolve()
    starts = {
        row["event_id"]: row
        for row in read_jsonl(repo / STARTS)
        if row.get("start_source_class") == "official_exact"
    }
    if len(starts) != 234:
        raise RuntimeError(f"expected 234 exact-bell games, found {len(starts)}")
    full = {
        row["event_id"]: row
        for row in read_json(repo / FULL)["events"]
    }
    events = {row["event_id"]: row for row in read_jsonl(args.events)}
    print_ranges = build_print_index(args.prints, args.print_index)

    legs = []
    skipped = []
    outside_grid = []
    for event_id, start in sorted(starts.items()):
        lawful = full[event_id]
        catalog = events[event_id]
        bell = epoch(start["exact_start_utc"])
        if bell is None:
            raise RuntimeError(f"missing exact bell on {event_id}")
        left = bell - 8 * 3600
        right = float(lawful["evaluator_right_ts"])
        for leg in catalog["legs"]:
            ticker = str(leg["ticker"])
            prints, _prior = load_print_block(
                ticker, print_ranges, left, right
            )
            if not prints:
                skipped.append({
                    "event_id": event_id,
                    "leg_id": str(leg["leg"]),
                    "ticker": ticker,
                    "reason": "no_true_print_inside_actual_bell_window",
                })
                continue
            low_price = min(float(row["price"]) for row in prints)
            low = next(
                row for row in prints if float(row["price"]) == low_price
            )
            close = prints[-1]
            close_price = float(close["price"])
            cell = grid_cell(close_price)
            row = {
                "event_id": event_id,
                "category": start["category"],
                "leg_id": str(leg["leg"]),
                "ticker": ticker,
                "exact_bell_ts": bell,
                "window_left_ts": left,
                "guarded_right_ts": right,
                "low_price_cents": low_price,
                "low_ts": float(low["ts"]),
                "close_price_cents": close_price,
                "close_ts": float(close["ts"]),
                "grid_cell": cell,
                "low_tminus_actual_bell_minutes": (
                    bell - float(low["ts"])
                ) / 60.0,
                "depth_below_window1_close_cents": close_price - low_price,
            }
            legs.append(row)
            if cell is None:
                outside_grid.append({
                    "event_id": event_id,
                    "ticker": ticker,
                    "category": start["category"],
                    "close_price_cents": close_price,
                    "action": "EXCLUDED_NOT_CLAMPED",
                })

    close_by_ticker = {}
    for row in legs:
        prior = close_by_ticker.setdefault(row["ticker"], row["close_ts"])
        if prior != row["close_ts"]:
            raise RuntimeError(f"ticker reused with two closes: {row['ticker']}")
    books, book_census = scan_books(args.books, close_by_ticker)
    attach_book_denominators(legs, books, book_census)

    recut = read_json(repo / RECUT)
    cells = build_cell_comparison(legs, recut)
    atlas = read_json(repo / ATLAS)
    old_page = atlas["pages"]["ATP_CHALL|leader|ge75"]
    heavy_rows = [
        row for row in cells
        if row["category"] == "ATP_CHALL" and 75 <= row["cell"] <= 94
    ]
    comparable_cells = [
        row for row in cells
        if row["requested_signed_comparison"]["value"] is not None
    ]
    disagreement_census = {
        "n_comparable_cells": len(comparable_cells),
        "n_exact_bell_deeper_than_prior": sum(
            row["requested_signed_comparison"]["value"] > 0
            for row in comparable_cells
        ),
        "n_exact_bell_shallower_than_prior": sum(
            row["requested_signed_comparison"]["value"] < 0
            for row in comparable_cells
        ),
        "n_equal": sum(
            row["requested_signed_comparison"]["value"] == 0
            for row in comparable_cells
        ),
        "all_populated_exact_cells_thin": all(
            row["exact_bell"]["n"] < THIN_N
            for row in cells
            if row["exact_bell"]["n"]
        ),
        "interpretation": (
            "Every nonzero signed cell is a named disagreement, not a "
            "replacement fit. All populated exact-bell cells are thin."
        ),
    }
    old_reconciliation = {
        "old_surface": str(ATLAS),
        "old_page": "ATP_CHALL|leader|ge75",
        "old_page_n": old_page["n"],
        "old_bottom_depth_p25_p50_p75_cents": [
            old_page["bottom"]["depth_p25"],
            old_page["bottom"]["depth_p50"],
            old_page["bottom"]["depth_p75"],
        ],
        "comparison_rows": heavy_rows,
        "all_exact_cells_thin": all(
            row["exact_bell"]["n"] < THIN_N for row in heavy_rows
        ),
        "ruling": (
            "The earlier category-average comparison was invalid. The old "
            "2/5/12 tuple is itself structurally retired because it pools "
            "leader status and a broad discovery-price band. The price-aligned "
            "75-94 exact-bell rows are all printed separately; thin rows do "
            "not prove the tuple numerically right or wrong."
        ),
    }

    result = {
        "schema_version": "window1-actual-bell-cell-comparison-v2",
        "correction": {
            "withdrawn": (
                "the prior 1/2/3-cent category-level depth headline and the "
                "48 broad exact-bell cohort cells"
            ),
            "reason": (
                "they flattened a ratified category-by-one-cent-cell prior"
            ),
            "replacement": (
                "a 90-cell [5,95) comparison against recut_cells.json, with "
                "n on both sides, no borrowing, no averaging up and no clamp"
            ),
        },
        "contracts": {
            "grid": (
                "90 one-cent cells per category over [5,95); "
                "cell is each leg's own W1 closing true-trade price"
            ),
            "ratified_aim_structure": (
                "<50 JOIN; 50-74 SHALLOW; 75-94 DEEP; "
                "edge_p50 read from recut_cells.json, never re-derived here"
            ),
            "fit_population": "234 official_exact actual-bell games only",
            "proxy_clock_games_blended": 0,
            "timing": (
                "T-minus actual bell, descriptive only; never an aim trigger"
            ),
            "spread": (
                "fresh archived BBO at or before each leg's W1 close; no "
                "book means NO_DENOMINATOR; no cent-line fallback"
            ),
            "midpoint": (
                "forbidden as a general analysis anchor; constructed only "
                "inside the named 1x/2x spread-below-mid formulas"
            ),
        },
        "source_hashes": {
            str(RECUT): sha256(repo / RECUT),
            str(ATLAS): sha256(repo / ATLAS),
            str(STARTS): sha256(repo / STARTS),
            str(FULL): sha256(repo / FULL),
        },
        "coverage": {
            "exact_games": len(starts),
            "leg_rows": len(legs),
            "skipped_legs": skipped,
            "outside_grid_legs": outside_grid,
        },
        "book_denominator_census": book_census,
        "posture_definitions": POSTURES,
        "cell_comparison": cells,
        "cell_disagreement_census": disagreement_census,
        "old_atlas_reconciliation": old_reconciliation,
        "flow_state_audit": flow_state_audit(),
        "retired_role_and_band_surface_census": surface_census(repo, recut),
        "leg_rows": legs,
    }
    return round_floats(result)


def round_floats(value):
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, list):
        return [round_floats(item) for item in value]
    if isinstance(value, dict):
        return {key: round_floats(item) for key, item in value.items()}
    return value


def shown(value, suffix: str = "") -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:+.2f}{suffix}"
    return f"{value}{suffix}"


def reach(cell: dict, posture: str) -> str:
    row = cell["canonical_posture_reach"][posture]
    denominator = row["n_denominator"]
    if not denominator:
        return "0/0 NO_DENOMINATOR"
    return f"{row['n_reached']}/{denominator}"


def render(result: dict) -> str:
    lines = [
        "# Actual-bell cell honesty recut",
        "",
        "**Correction: the prior 1/2/3-cent category headline is withdrawn. "
        "It compared a category average to cell-conditional doctrine. This "
        "report does not create a parallel aim grid; it compares exact-bell "
        "evidence directly to the ratified `recut_cells.json` prior.**",
        "",
        "THE GRID is exactly 90 one-cent cells per category, `[5,95)`. "
        "Out-of-grid close prints are excluded and never clamped. Each row "
        "prints prior n, exact-bell n and BBO-denominator n. `THIN` is not "
        "borrowed and is not averaged upward.",
        "",
        "The signed cent difference is included only because it was requested "
        "for reconciliation: exact-bell median `(W1 close last trade - low)` "
        "minus prior `edge_p50`. Canonical depth evidence is reported in each "
        "leg's own spread and by the four named postures.",
        "",
        "Postures and denominators:",
        "",
    ]
    for name, row in result["posture_definitions"].items():
        lines.append(
            f"- `{name}` = `{row['formula']}`; denominator = "
            f"`{row['denominator']}`."
        )
    lines += [
        "",
        "A fresh archived BBO must exist at or before that leg's Window-1 "
        "close and be no more than 300 seconds old. Otherwise the leg is "
        "`NO_DENOMINATOR`; there is no fallback. The constructed midpoint "
        "appears only inside the two named midpoint formulas.",
        "",
        "## Cell-by-cell comparison",
        "",
        (
            f"Comparable cells: "
            f"{result['cell_disagreement_census']['n_comparable_cells']}; "
            f"exact-bell deeper than prior: "
            f"{result['cell_disagreement_census']['n_exact_bell_deeper_than_prior']}; "
            f"shallower: "
            f"{result['cell_disagreement_census']['n_exact_bell_shallower_than_prior']}; "
            f"equal: {result['cell_disagreement_census']['n_equal']}. "
            "Every populated exact-bell cell is thin, so each difference is "
            "a finding to inspect, not a replacement fit."
        ),
        "",
        "| Category | cell | zone | prior n | exact n | spread n | status | "
        "prior p50¢ | exact p50¢ | signed Δ¢ | signed Δ / own spread p50 | "
        "JOIN | touch−1 | 1× below mid | 2× below mid |",
        "|---|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["cell_comparison"]:
        prior = row["prior"]
        exact = row["exact_bell"]
        signed = row["requested_signed_comparison"]["value"]
        signed_spread = row["spread_normalized_comparison"][
            "actual_minus_prior_spreads"
        ]["median"]
        lines.append(
            f"| {row['category']} | {row['cell']} | "
            f"{row['aim_zone_ratified']} | {prior['n']} | {exact['n']} | "
            f"{exact['n_with_spread_denominator']} | {row['status']} | "
            f"{shown(prior['edge_p50_cents_compatibility_only'])} | "
            f"{shown(exact['edge_cents_compatibility_only']['median'])} | "
            f"{shown(signed)} | {shown(signed_spread, '×')} | "
            f"{reach(row, 'JOIN')} | {reach(row, 'TOUCH_MINUS_1')} | "
            f"{reach(row, 'ONE_SPREAD_BELOW_MID')} | "
            f"{reach(row, 'TWO_SPREADS_BELOW_MID')} |"
        )

    old = result["old_atlas_reconciliation"]
    lines += [
        "",
        "## Old atlas 2/5/12 reconciliation",
        "",
        f"The old `{old['old_page']}` page has n={old['old_page_n']} and "
        "reports absolute-cent bottom p25/p50/p75 = 2/5/12. That page uses "
        "`leader` plus broad discovery band `ge75`; both axes are retired. "
        "The comparison below is price-aligned to ATP Challenger cells 75–94 "
        "without pooling them.",
        "",
        "| cell | old page | recut n / p25-p50-p75¢ | exact n / "
        "p25-p50-p75¢ | signed exact−recut p50¢ | status |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for row in old["comparison_rows"]:
        prior = row["prior"]
        exact = row["exact_bell"]
        ep = exact["edge_cents_compatibility_only"]
        lines.append(
            f"| {row['cell']} | 2/5/12 pooled | "
            f"{prior['n']} / "
            f"{shown(prior['edge_p25_cents_compatibility_only'])}-"
            f"{shown(prior['edge_p50_cents_compatibility_only'])}-"
            f"{shown(prior['edge_p75_cents_compatibility_only'])} | "
            f"{exact['n']} / {shown(ep['p25'])}-{shown(ep['median'])}-"
            f"{shown(ep['p75'])} | "
            f"{shown(row['requested_signed_comparison']['value'])} | "
            f"{row['status']} |"
        )
    lines += [
        "",
        old["ruling"],
        "",
        "## Live flow-state primitive",
        "",
        "Vault §5 defines the primitive as **prints/min plus "
        "spread-tightening, per category**. Live wiring is incomplete:",
        "",
    ]
    for key, value in result["flow_state_audit"]["live_wiring"].items():
        lines.append(f"- **{key}:** {value}")
    lines += [
        "",
        "To key aim activation on observed flow rather than clock distance:",
        "",
    ]
    for item in result["flow_state_audit"]["required_change"]:
        lines.append(f"- {item}")
    lines += [
        "",
        result["flow_state_audit"]["timing_surface_action"],
        "",
        "## Retired fav/dog and band census",
        "",
        "This census covers fitted artifacts and sealed state tables, not "
        "only Python branches.",
        "",
        "| Surface | rows | key | role keyed? | ruling | live effect |",
        "|---|---:|---|---|---|---|",
    ]
    for row in result["retired_role_and_band_surface_census"]:
        lines.append(
            f"| `{row['surface']}` | {row['rows']} | {row['key']} | "
            f"{'yes' if row['role_keyed'] else 'no'} | "
            f"{row['verdict']} | {row.get('live_effect', row.get('note', ''))} |"
        )
    book = result["book_denominator_census"]
    lines += [
        "",
        "## BBO denominator census",
        "",
        f"Private archive: `{book['directory']}`. Scanned "
        f"{book['gzip_files']} gzip files / "
        f"{book['physical_rows_scanned']:,} rows. Leg statuses: "
        f"`{json.dumps(book['leg_status_counts'], sort_keys=True)}`; "
        "NO_DENOMINATOR reasons: "
        f"`{json.dumps(book['no_denominator_reason_counts'], sort_keys=True)}`. "
        "No midpoint or cent-line fallback was used.",
        "",
        "Timing distributions in the JSON are descriptive only. They are not "
        "an aim trigger and are not fitted back into live placement.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--prints", type=Path, default=DEFAULT_PRINTS)
    parser.add_argument(
        "--print-index", type=Path, default=DEFAULT_PRINT_INDEX
    )
    parser.add_argument("--books", type=Path, default=DEFAULT_BOOKS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build(args)
    out = (args.repo / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "ACTUAL_BELL_REFIT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out / "ACTUAL_BELL_REFIT.md").write_text(
        render(result), encoding="utf-8", newline="\n"
    )
    print(json.dumps({
        "exact_games": result["coverage"]["exact_games"],
        "leg_rows": result["coverage"]["leg_rows"],
        "outside_grid": len(result["coverage"]["outside_grid_legs"]),
        "book_status": result["book_denominator_census"][
            "leg_status_counts"
        ],
        "cells": len(result["cell_comparison"]),
        "all_atp_chall_75_94_exact_cells_thin": result[
            "old_atlas_reconciliation"
        ]["all_exact_cells_thin"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
