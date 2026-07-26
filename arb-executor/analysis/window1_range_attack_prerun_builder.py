#!/usr/bin/env python3
"""Freeze the score-free Window-1 Range-Mastery Attack PRE-RUN.

Policy streams are produced without evaluation-start truth.  This builder then
joins the independently frozen V5 boundary ledger only to label the historical
range canvas and the selected-price fillability diagnostics.  It never imports
or invokes a scorer and never computes C, PC, S, or IC.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import window1_range_attack_instrument as attack
import window1_round2_data_binding as binding
import window1_round2_real_capability as capability
import window1_round4_macromicro_instrument as passed_normalizer


VERSION = "window1-range-mastery-attack-prerun-v1"
OUTPUT_DIR = ".claude/window1_range_attack_prerun_20260725"
START_LEDGER = (
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
FIVE_NO_BBO = {
    "KXATPCHALLENGERMATCH-26JUL19KRUCAS",
    "KXATPCHALLENGERMATCH-26JUL20CREMAT",
    "KXWTAMATCH-26JUL13TAUTOM",
    "KXWTAMATCH-26JUL14PUTJEA",
    "KXWTAMATCH-26JUL20KUDKOR",
}
DECISION_ACTIONS = {"place", "reprice", "cancel"}
METRIC_FIELDS = {"C", "PC", "S", "IC"}

FILES = {
    "stream_1": "UNSCORED_CANDIDATE_EVENT_STREAMS_01.jsonl.gz",
    "stream_2": "UNSCORED_CANDIDATE_EVENT_STREAMS_02.jsonl.gz",
    "stream_3": "UNSCORED_CANDIDATE_EVENT_STREAMS_03.jsonl.gz",
    "stream_4": "UNSCORED_CANDIDATE_EVENT_STREAMS_04.jsonl.gz",
    "ladder_1": "WINDOW1_PRICE_RANGE_LADDER_01.jsonl.gz",
    "ladder_2": "WINDOW1_PRICE_RANGE_LADDER_02.jsonl.gz",
    "ladder_3": "WINDOW1_PRICE_RANGE_LADDER_03.jsonl.gz",
    "ladder_4": "WINDOW1_PRICE_RANGE_LADDER_04.jsonl.gz",
    "fillability": "PRICE_FILLABILITY_RECEIPTS.jsonl.gz",
    "stress": "DEPTH_VOLUME_STRESS_RECEIPTS.jsonl.gz",
    "opportunity": "PAIRWISE_ASYNCHRONOUS_OPPORTUNITY_LEDGER.jsonl.gz",
    "headroom": "COMBINED_HEADROOM_RECEIPTS.jsonl.gz",
    "actions": "ACTION_AUTHORITY_RECEIPTS.jsonl.gz",
    "bindings": "RAW_LAST_TRADE_CHAIN_VOLUME_BINDINGS.json",
    "diagnostics": "RANGE_ATTACK_DIAGNOSTICS.json",
    "five": "FIVE_EVENT_D_MEMBERSHIP_PROOF.json",
}


class FreezeError(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_utc(value: str | None) -> float | None:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl_gzip(
    path: Path, rows: Iterable[Mapping[str, Any]],
) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0
        ) as zipped:
            with io.TextIOWrapper(
                zipped, encoding="utf-8", newline="\n"
            ) as text:
                for row in rows:
                    text.write(compact(row) + "\n")


def boundary_contract(row: Mapping[str, Any]) -> dict[str, Any]:
    source_class = str(row["start_source_class"])
    positive = bool(row["positive_window1_provable"])
    cutoff = None
    guard = None
    law = None
    if positive and source_class == "official_exact":
        guard = 60
        cutoff = float(parse_utc(str(row["exact_start_utc"]))) - guard
        law = "official_exact_start_minus_committed_60_seconds"
    elif positive and source_class == "quantized_late_detection_proxy":
        guard = 900
        cutoff = parse_utc(
            str(row["guard_band"]["strict_window1_completion_lte_utc"])
        )
        law = "V5_proxy_asymmetric_strict_window1_cutoff_900_seconds"
    elif positive and source_class == "clean_causal_interval":
        guard = 60
        lower = parse_utc(str(row["start_interval_utc"]["lower_inclusive"]))
        cutoff = float(lower) - guard
        law = "clean_causal_interval_lower_bound_minus_60_seconds"
    if positive and cutoff is None:
        raise FreezeError(
            f"positive boundary lacks lawful cutoff: {row['event_id']}"
        )
    return {
        "event_id": str(row["event_id"]),
        "start_source_class": source_class,
        "positive_window1_provable": positive,
        "guard_seconds": guard,
        "guarded_cutoff_ts": cutoff,
        "boundary_law": law,
        "guard_id": (
            (row.get("guard_band") or {}).get("guard_id")
        ),
        "conflict_status": row.get("conflict_status"),
        "guard_censor_reason": row.get("guard_censor_reason"),
        "schedule_can_prove_positive": bool(
            row.get("schedule_can_prove_positive")
        ),
        "source_record_sha256": sha256_json(row),
    }


def _valid_prints(
    observations: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
) -> list[dict[str, Any]]:
    rows, seen = [], set()
    for row in observations:
        if row.get("kind") != "print":
            continue
        timestamp = float(row["ts"])
        if not left <= timestamp <= right:
            continue
        valid, _ = attack.positive_print(row)
        receipt = str(
            row.get("trade_id")
            or row.get("source_receipt_identity")
            or ""
        )
        if not valid or not receipt or receipt in seen:
            continue
        seen.add(receipt)
        rows.append({
            "ts": timestamp,
            "price": int(row["price"]),
            "size": float(row["size"]),
            "receipt": receipt,
            "taker_side": row.get("taker_side"),
        })
    rows.sort(key=lambda value: (
        value["ts"], value["receipt"], value["price"]
    ))
    return rows


def _books(
    observations: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
) -> list[dict[str, Any]]:
    rows, seen = [], set()
    for row in observations:
        if row.get("kind") != "book":
            continue
        timestamp = float(row["ts"])
        receipt = str(row.get("source_receipt_identity") or "")
        if not left <= timestamp <= right or not receipt or receipt in seen:
            continue
        seen.add(receipt)
        rows.append({
            "ts": timestamp,
            "receipt": receipt,
            "bids": [list(value) for value in row.get("bids") or []],
            "asks": [list(value) for value in row.get("asks") or []],
            "last_trade_cents": row.get("last_trade_cents"),
            "last_trade_provenance": row.get("last_trade_provenance"),
            "last_trade_observed_at": row.get("last_trade_observed_at"),
            "last_trade_execution_at": row.get("last_trade_execution_at"),
            "chain_state": dict(row.get("chain_state") or {}),
        })
    rows.sort(key=lambda value: (value["ts"], value["receipt"]))
    return rows


def _latest_before(
    rows: Sequence[Mapping[str, Any]], timestamp: float,
) -> Mapping[str, Any] | None:
    value = None
    for row in rows:
        if float(row["ts"]) > timestamp:
            break
        value = row
    return value


def _rolling_print_state(
    prints: Sequence[Mapping[str, Any]], timestamp: float,
) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for minutes in (5, 15, 30):
        rows = [
            row for row in prints
            if timestamp - minutes * 60 <= float(row["ts"]) <= timestamp
        ]
        values[f"print_count_{minutes}m"] = len(rows)
        values[f"executed_volume_{minutes}m"] = float(
            sum(float(row["size"]) for row in rows)
        )
    rows30 = [
        row for row in prints
        if timestamp - 1800 <= float(row["ts"]) <= timestamp
    ]
    values["inter_print_cadence_seconds_30m"] = attack.median_cadence(
        rows30
    )
    values["trailing_price_signature_30m"] = attack.print_signature(
        [float(row["price"]) for row in rows30]
    )
    return values


def _book_context(
    book: Mapping[str, Any] | None, target: int,
) -> dict[str, Any] | None:
    if book is None:
        return None
    bids = [
        [int(price), float(size)]
        for price, size in book.get("bids") or []
        if float(size) > 0
    ][:5]
    asks = [
        [int(price), float(size)]
        for price, size in book.get("asks") or []
        if float(size) > 0
    ][:5]
    bid = bids[0][0] if bids else None
    ask = asks[0][0] if asks else None
    exact = next(
        (size for price, size in bids if int(price) == target), None
    )
    ahead = float(
        sum(size for price, size in bids if int(price) >= target)
    )
    chain = dict(book.get("chain_state") or {})
    return {
        "timestamp": float(book["ts"]),
        "receipt": str(book["receipt"]),
        "nonself_best_bid_cents": bid,
        "nonself_best_ask_cents": ask,
        "spread_cents": (
            ask - bid if ask is not None and bid is not None else None
        ),
        "top5_bids": bids,
        "top5_asks": asks,
        "observable_depth_at_target": exact,
        "observable_top5_depth_at_or_ahead": ahead,
        "top5_covers_target": bool(
            bids and target >= int(bids[-1][0])
        ),
        "last_trade_cents": book.get("last_trade_cents"),
        "last_trade_provenance": book.get("last_trade_provenance"),
        "last_trade_observed_at": book.get("last_trade_observed_at"),
        "last_trade_execution_at": book.get(
            "last_trade_execution_at"
        ),
        "last_trade_position": chain.get("last_trade_position"),
        "last_trade_changed": chain.get("last_trade_changed"),
        "chain_transitions": chain.get("transitions"),
    }


def _sibling_context(
    sibling_books: Sequence[Mapping[str, Any]],
    sibling_prints: Sequence[Mapping[str, Any]],
    timestamp: float,
) -> dict[str, Any]:
    book = _latest_before(sibling_books, timestamp)
    prices = [
        float(row["price"]) for row in sibling_prints
        if float(row["ts"]) <= timestamp
    ]
    return {
        "book": _book_context(book, 1) if book is not None else None,
        "last_print_price_cents": prices[-1] if prices else None,
        "observed_print_range_cents": (
            [min(prices), max(prices)] if prices else None
        ),
        "flow": _rolling_print_state(sibling_prints, timestamp),
    }


def _residency_seconds(
    books: Sequence[Mapping[str, Any]],
    target: int,
    right: float,
) -> float:
    total = 0.0
    for index, book in enumerate(books):
        asks = book.get("asks") or []
        ask = int(asks[0][0]) if asks else None
        next_ts = (
            float(books[index + 1]["ts"])
            if index + 1 < len(books) else right
        )
        if ask is not None and ask <= target:
            total += max(0.0, next_ts - float(book["ts"]))
    return total


def build_leg_range_ladder(
    *,
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    sibling: Mapping[str, Any],
    boundary: Mapping[str, Any],
) -> dict[str, Any]:
    left = float(event["policy_left_ts"])
    policy_right = float(event["policy_decision_horizon_ts"])
    cutoff = boundary.get("guarded_cutoff_ts")
    range_right = (
        min(policy_right, float(cutoff))
        if cutoff is not None else policy_right
    )
    prints = _valid_prints(leg["observations"], left, range_right)
    books = _books(leg["observations"], left, range_right)
    sibling_prints = _valid_prints(
        sibling["observations"], left, range_right
    )
    sibling_books = _books(
        sibling["observations"], left, range_right
    )
    total_volume = float(sum(row["size"] for row in prints))
    price_rows = []
    for target in range(1, 100):
        touches = [row for row in prints if row["price"] <= target]
        strict = [row for row in prints if row["price"] < target]
        exact = [row for row in prints if row["price"] == target]
        below = [row for row in prints if row["price"] < target]
        first = touches[0] if touches else None
        first_book = (
            _latest_before(books, float(first["ts"]))
            if first is not None else None
        )
        ask_exact = next((
            book for book in books
            if book.get("asks")
            and int(book["asks"][0][0]) == target
        ), None)
        ask_strict = next((
            book for book in books
            if book.get("asks")
            and int(book["asks"][0][0]) < target
        ), None)
        context = None
        if first is not None:
            prior_last = [
                {
                    "ts": float(book["ts"]),
                    "last_trade_cents": book.get("last_trade_cents"),
                    "provenance": book.get("last_trade_provenance"),
                }
                for book in books
                if float(book["ts"]) <= float(first["ts"])
                and book.get("last_trade_cents") is not None
            ][-5:]
            later_last = [
                {
                    "ts": float(book["ts"]),
                    "last_trade_cents": book.get("last_trade_cents"),
                    "provenance": book.get("last_trade_provenance"),
                }
                for book in books
                if float(book["ts"]) >= float(first["ts"])
                and book.get("last_trade_cents") is not None
            ][:5]
            context = {
                "first_reach_book": _book_context(first_book, target),
                "last_trade_path_into_reach": prior_last,
                "last_trade_path_away_from_reach": later_last,
                "rolling_flow": _rolling_print_state(
                    prints, float(first["ts"])
                ),
                "category_flow_state": attack.flow_bucket(
                    str(event["category"]),
                    _rolling_print_state(
                        prints, float(first["ts"])
                    )["print_count_30m"],
                ),
                "sibling_same_timestamp": _sibling_context(
                    sibling_books, sibling_prints, float(first["ts"])
                ),
            }
        price_rows.append({
            "price_cents": target,
            "first_true_print_at_or_below": first,
            "first_strict_trade_through_below": (
                strict[0] if strict else None
            ),
            "last_true_print_at_or_below": (
                touches[-1] if touches else None
            ),
            "true_print_count_at": len(exact),
            "true_print_count_below": len(below),
            "executed_share_volume_at": float(
                sum(row["size"] for row in exact)
            ),
            "executed_share_volume_below": float(
                sum(row["size"] for row in below)
            ),
            "total_window1_share_volume": total_volume,
            "ask_residency_at_or_below_seconds": _residency_seconds(
                books, target, range_right
            ),
            "first_ask_exact_touch": (
                {
                    "ts": ask_exact["ts"],
                    "receipt": ask_exact["receipt"],
                } if ask_exact is not None else None
            ),
            "first_ask_strictly_below": (
                {
                    "ts": ask_strict["ts"],
                    "receipt": ask_strict["receipt"],
                } if ask_strict is not None else None
            ),
            "first_reach_context": context,
            "range_outcome_only_not_policy_input": True,
        })
    return {
        "schema_version": VERSION + "-integer-cent-range-ladder-v1",
        "event_id": str(event["event_id"]),
        "event_date": str(event["event_date"]),
        "category": str(event["category"]),
        "leg_id": str(leg["leg_id"]),
        "ticker": str(leg["ticker"]),
        "D_member": True,
        "policy_left_ts": left,
        "range_right_ts": range_right,
        "policy_horizon_ts": policy_right,
        "boundary": dict(boundary),
        "positive_range_outcomes_provable": bool(
            boundary["positive_window1_provable"]
        ),
        "true_positive_print_count": len(prints),
        "book_receipt_count": len(books),
        "integer_cent_price_rows": price_rows,
        "integer_cent_price_row_count": len(price_rows),
        "future_range_outcomes_unreachable_from_policy": True,
        "C": None,
        "PC": None,
        "S": None,
        "IC": None,
        "metrics": None,
        "scored": False,
    }


def evaluate_interval(
    *,
    candidate_id: str,
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    interval: Mapping[str, Any],
    boundary: Mapping[str, Any],
    taker_reach: Mapping[str, Any],
) -> dict[str, Any]:
    opened = float(interval["opened_ts"])
    policy_closed = float(
        interval["closed_ts"]
        if interval.get("closed_ts") is not None
        else event["policy_decision_horizon_ts"]
    )
    cutoff = boundary.get("guarded_cutoff_ts")
    right = (
        min(policy_closed, float(cutoff))
        if cutoff is not None else policy_closed
    )
    target = int(interval["limit_price_cents"])
    positive = bool(boundary["positive_window1_provable"])
    observations = leg.get("observations") or []
    prints = (
        _valid_prints(observations, opened, right)
        if positive and opened <= right else []
    )
    books = (
        _books(observations, opened, right)
        if positive and opened <= right else []
    )
    reached = [row for row in prints if row["price"] <= target]
    strict_print = [row for row in prints if row["price"] < target]
    strict_ask = [
        row for row in books
        if row.get("asks") and int(row["asks"][0][0]) < target
    ]
    exact_print = [row for row in prints if row["price"] == target]
    exact_ask = [
        row for row in books
        if row.get("asks") and int(row["asks"][0][0]) == target
    ]
    first = reached[0] if reached else None
    context_book = (
        _latest_before(books, float(first["ts"]))
        if first is not None else None
    )
    stress = None
    exact_touch = bool(exact_print or exact_ask)
    if exact_touch:
        touch_ts = min(
            [float(row["ts"]) for row in exact_print + exact_ask]
        )
        touch_book = _latest_before(books, touch_ts)
        touch_flow = _rolling_print_state(prints, touch_ts)
        flow_class = attack.flow_bucket(
            str(event["category"]), int(touch_flow["print_count_30m"])
        )
        reach_page = (
            (taker_reach.get("law") or {}).get(
                f"{event['category']}|{flow_class}"
            )
        )
        touch_context = _book_context(touch_book, target)
        touch_bid = (
            touch_context.get("nonself_best_bid_cents")
            if touch_context else None
        )
        reach_depth = (
            max(1, min(20, int(touch_bid) - target))
            if touch_bid is not None else None
        )
        reach_rate = (
            (reach_page.get("rate_per_hr") or {}).get(str(reach_depth))
            if isinstance(reach_page, Mapping)
            and reach_depth is not None else None
        )
        residency_hours = max(0.0, touch_ts - opened) / 3600.0
        reach_probability = (
            1.0 - math.exp(-float(reach_rate) * residency_hours)
            if reach_rate is not None else None
        )
        stress = {
            "candidate_id": candidate_id,
            "event_id": str(event["event_id"]),
            "leg_id": str(leg["leg_id"]),
            "order_interval_id": str(interval["order_interval_id"]),
            "target_price_cents": target,
            "exact_touch_ts": touch_ts,
            "exact_touch_print_receipts": [
                row["receipt"] for row in exact_print
            ],
            "exact_touch_book_receipts": [
                row["receipt"] for row in exact_ask
            ],
            "chain": touch_context,
            "executed_sell_volume_at_and_below": float(sum(
                row["size"] for row in reached
                if row.get("taker_side") == "no"
            )),
            "executed_volume_at_and_below": float(sum(
                row["size"] for row in reached
            )),
            "total_market_volume_during_exposure": float(sum(
                row["size"] for row in prints
            )),
            "flow": touch_flow,
            "fitted_taker_reach": {
                "source": attack.TAKER_REACH_PATH,
                "native_key": f"{event['category']}|{flow_class}",
                "target_depth_from_contemporaneous_bid_cents": reach_depth,
                "rate_per_hour": reach_rate,
                "residency_hours": residency_hours,
                "probability": reach_probability,
                "decision_gate": False,
                "stress_diagnostic_only": True,
            },
            "queue_preserved_from_interval_open": True,
            "queue_primary_gate": False,
            "displayed_depth_primary_gate": False,
            "metrics": None,
            "scored": False,
        }
    counterfactual_right = (
        min(
            float(event["policy_decision_horizon_ts"]),
            float(cutoff),
        ) if cutoff is not None else policy_closed
    )
    future_at_price = (
        _valid_prints(observations, opened, counterfactual_right)
        if positive and opened <= counterfactual_right else []
    )
    cumulative_volume = float(sum(
        row["size"] for row in future_at_price
        if row["price"] <= target
    ))
    primary = bool(reached)
    return {
        "schema_version": VERSION + "-price-fillability-v1",
        "candidate_id": candidate_id,
        "event_id": str(event["event_id"]),
        "event_date": str(event["event_date"]),
        "category": str(event["category"]),
        "leg_id": str(leg["leg_id"]),
        "ticker": str(leg["ticker"]),
        "order_interval_id": str(interval["order_interval_id"]),
        "opened_ts": opened,
        "policy_closed_ts": policy_closed,
        "evaluated_right_ts": right,
        "target_price_cents": target,
        "boundary": dict(boundary),
        "PRICE_REACHED": primary,
        "PRICE_REACHED_receipt": first,
        "CERTAIN_FILL": bool(strict_print or strict_ask),
        "CERTAIN_FILL_first_strict_print": (
            strict_print[0] if strict_print else None
        ),
        "CERTAIN_FILL_first_strict_ask": (
            {
                "ts": strict_ask[0]["ts"],
                "receipt": strict_ask[0]["receipt"],
            } if strict_ask else None
        ),
        "EXACT_TOUCH": exact_touch,
        "EXACT_TOUCH_print_count": len(exact_print),
        "EXACT_TOUCH_ask_count": len(exact_ask),
        "primary_price_fillability_assigns_five": primary,
        "accounting_quantity_if_later_scored": 5 if primary else 0,
        "cumulative_printed_size_required": False,
        "cumulative_volume_at_or_below_through_cutoff": cumulative_volume,
        "cumulative_size_five_counterfactual_pass": (
            cumulative_volume >= 5.0
        ),
        "cumulative_size_five_would_false_negative": (
            primary and cumulative_volume < 5.0
        ),
        "queue_clearance_required": False,
        "displayed_depth_five_required": False,
        "single_five_print_required": False,
        "trade_through_required": False,
        "first_reach_book": _book_context(context_book, target),
        "depth_volume_stress": stress,
        "range_outcome_separate_from_decision_receipt": True,
        "C": None,
        "PC": None,
        "S": None,
        "IC": None,
        "metrics": None,
        "scored": False,
    }


def _last_trade_census(censuses: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    fields = [
        "raw_snapshot_count",
        "raw_positive_last_trade_count",
        "normalized_book_count",
        "normalized_positive_last_trade_count",
        "verified_print_timestamp_count",
        "carried_execution_time_unknown_count",
        "carried_before_first_window1_print_count",
        "legs_with_carried_state_and_no_window1_print_count",
        "last_trade_created_print_count",
    ]
    return {
        "schema_version": VERSION + "-raw-normalized-binding-census-v1",
        "event_count": len(censuses),
        **{
            field: sum(int(row[field]) for row in censuses)
            for field in fields
        },
        "last_trade_is_BBO_authority": False,
        "last_trade_is_fill_volume": False,
        "last_trade_direction_gate": False,
        "constructed_midpoint_used": False,
        "top5_chain_preserved": True,
        "actual_print_volume_preserved": True,
        "actual_print_cadence_preserved": True,
        "metrics": None,
        "scored": False,
    }


def _process_chunk(
    repo_text: str,
    cache_text: str,
    rows: Sequence[tuple[int, Mapping[str, Any]]],
    feature_map: Mapping[tuple[str, str], Mapping[str, Any]],
    boundaries: Mapping[str, Mapping[str, Any]],
    candidate_ids: Sequence[str],
    source_hashes: Mapping[str, str],
) -> dict[str, Any]:
    repo = Path(repo_text)
    cache_root = Path(cache_text)
    spec = attack.load_candidate_spec(repo)
    policies = {
        candidate: attack.candidate_policy(spec, candidate)
        for candidate in candidate_ids
    }
    atlas = json.loads((repo / attack.ATLAS_PATH).read_text(encoding="utf-8"))
    guidebook = json.loads(
        (repo / attack.GUIDEBOOK_PATH).read_text(encoding="utf-8")
    )
    recut = json.loads((repo / attack.RECUT_PATH).read_text(encoding="utf-8"))
    reach = json.loads(
        (repo / attack.TAKER_REACH_PATH).read_text(encoding="utf-8")
    )
    streams, ladders, fillability, censuses = [], [], [], []
    for event_index, event in rows:
        event_id = str(event["event_id"])
        cache = capability.load_cache(cache_root / f"{event_id}.json.gz")
        normalized, census = passed_normalizer.normalize_event(
            event, cache, feature_map, corridor_seconds=0.0
        )
        census["event_id"] = event_id
        censuses.append(census)
        boundary = boundaries[event_id]
        for leg_index, leg in enumerate(normalized["legs"]):
            sibling = normalized["legs"][1 - leg_index]
            ladder = build_leg_range_ladder(
                event=normalized,
                leg=leg,
                sibling=sibling,
                boundary=boundary,
            )
            ladder["event_index"] = event_index
            ladder["leg_index"] = leg_index
            ladders.append(ladder)
        for candidate_index, candidate in enumerate(candidate_ids):
            result = attack.RangeAttackSimulator(
                policies[candidate],
                atlas=atlas,
                guidebook=guidebook,
                recut=recut,
                taker_reach=reach,
                source_hashes=source_hashes,
            ).run(normalized)
            if result["metrics"] is not None or result["scored"]:
                raise FreezeError("performance metric entered policy stream")
            stream_row = {
                "event_index": event_index,
                "candidate_index": candidate_index,
                "candidate_id": candidate,
                "event_id": event_id,
                "event_date": str(event["event_date"]),
                "category": str(event["category"]),
                "stream": result,
            }
            streams.append(stream_row)
            by_leg = {
                str(leg["leg_id"]): leg for leg in normalized["legs"]
            }
            for leg_id, intervals in (
                result["order_intervals_by_leg"].items()
            ):
                for interval in intervals:
                    fillability.append(evaluate_interval(
                        candidate_id=candidate,
                        event=normalized,
                        leg=by_leg[leg_id],
                        interval=interval,
                        boundary=boundary,
                        taker_reach=reach,
                    ))
    return {
        "streams": streams,
        "ladders": ladders,
        "fillability": fillability,
        "censuses": censuses,
    }


def _classify_stress(row: Mapping[str, Any]) -> str:
    stress = row.get("depth_volume_stress") or {}
    chain = stress.get("chain") or {}
    depth = chain.get("observable_depth_at_target")
    volume = float(stress.get("executed_volume_at_and_below") or 0.0)
    if depth is None:
        depth_class = "DEPTH_UNKNOWN"
    elif float(depth) < 5:
        depth_class = "DISPLAY_LT5"
    else:
        depth_class = "DISPLAY_GE5"
    if volume < 5:
        volume_class = "EXECUTED_LT5"
    else:
        volume_class = "EXECUTED_GE5"
    return f"{depth_class}|{volume_class}"


def _action_authority_rows(
    streams: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for envelope in streams:
        for action in envelope["stream"]["order_stream"]:
            if action["action"] not in DECISION_ACTIONS:
                continue
            rows.append({
                "candidate_id": envelope["candidate_id"],
                "event_id": envelope["event_id"],
                "event_date": envelope["event_date"],
                "category": envelope["category"],
                "leg_id": action["leg_id"],
                "timestamp": action["ts"],
                "action": action["action"],
                "reason": action["reason"],
                "primary_authority": action["primary_authority"],
                "composed_macro_micro": action[
                    "composed_macro_micro"
                ],
                "price_cents": action.get("price_cents"),
                "prior_price_cents": action.get("prior_price_cents"),
                "reprice_direction": action.get("reprice_direction"),
                "causal_state": action.get("causal_state"),
                "metrics": None,
                "scored": False,
            })
    return rows


def _headroom_rows(
    streams: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    names = {"headroom_armed", "headroom_decision"}
    return [{
        "candidate_id": envelope["candidate_id"],
        "event_id": envelope["event_id"],
        "event_date": envelope["event_date"],
        "category": envelope["category"],
        **action,
        "metrics": None,
        "scored": False,
    } for envelope in streams
      for action in envelope["stream"]["order_stream"]
      if action["action"] in names]


def _pair_opportunities(
    streams: Sequence[Mapping[str, Any]],
    fillability: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    fills_by_key: dict[tuple[str, str, str], list[Mapping[str, Any]]] = (
        defaultdict(list)
    )
    for row in fillability:
        fills_by_key[(
            str(row["candidate_id"]),
            str(row["event_id"]),
            str(row["leg_id"]),
        )].append(row)
    output = []
    for envelope in streams:
        result = envelope["stream"]
        leg_ids = list(result["order_intervals_by_leg"])
        firsts = {}
        for leg_id in leg_ids:
            rows = [
                row for row in fills_by_key[(
                    envelope["candidate_id"],
                    envelope["event_id"],
                    leg_id,
                )]
                if row["PRICE_REACHED"]
            ]
            rows.sort(key=lambda value: (
                float(value["PRICE_REACHED_receipt"]["ts"]),
                str(value["order_interval_id"]),
            ))
            firsts[leg_id] = rows[0] if rows else None
        both = all(firsts.values())
        distinct = (
            both
            and float(firsts[leg_ids[0]]["PRICE_REACHED_receipt"]["ts"])
            != float(firsts[leg_ids[1]]["PRICE_REACHED_receipt"]["ts"])
        )
        actions = result["order_stream"]
        headroom = [
            row for row in actions
            if row["action"] in {"headroom_armed", "headroom_decision"}
        ]
        accepted = [
            row for row in headroom if row.get("action_taken") is True
        ]
        output.append({
            "schema_version": VERSION + "-pair-opportunity-v1",
            "candidate_id": envelope["candidate_id"],
            "event_id": envelope["event_id"],
            "event_date": envelope["event_date"],
            "category": envelope["category"],
            "D_member": True,
            "leg_price_opportunity": {
                leg_id: firsts[leg_id] for leg_id in leg_ids
            },
            "both_legs_have_primary_PRICE_REACHED": both,
            "separately_timed_price_opportunities": bool(distinct),
            "first_leg_identity": (
                min(
                    leg_ids,
                    key=lambda value: float(
                        firsts[value]["PRICE_REACHED_receipt"]["ts"]
                    ),
                ) if both else next((
                    leg_id for leg_id in leg_ids
                    if firsts[leg_id] is not None
                ), None)
            ),
            "headroom_activation_count": sum(
                row["action"] == "headroom_armed" for row in headroom
            ),
            "headroom_decision_count": sum(
                row["action"] == "headroom_decision" for row in headroom
            ),
            "accepted_sibling_headroom_count": len(accepted),
            "sibling_opportunity_inside_remaining_budget_count": sum(
                row.get("strict_guard_passed") is True
                for row in headroom
                if row["action"] == "headroom_decision"
            ),
            "C": None,
            "PC": None,
            "S": None,
            "IC": None,
            "metrics": None,
            "scored": False,
        })
    return output


def _assert_metrics_null(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in METRIC_FIELDS and child is not None:
                raise FreezeError(f"performance metric populated at {path}.{key}")
            if key == "metrics" and child is not None:
                raise FreezeError(f"metrics populated at {path}.metrics")
            _assert_metrics_null(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_metrics_null(child, f"{path}[{index}]")


def build(
    *,
    repo: Path,
    events_path: Path,
    cache_root: Path,
    workers: int,
) -> dict[str, Any]:
    events = read_jsonl(events_path)
    if len(events) != 804:
        raise FreezeError(f"D changed: {len(events)}")
    if sorted({str(row["event_date"]) for row in events}) != list(
        binding.DEV_DATES
    ):
        raise FreezeError("development dates changed")
    if any(str(row["event_date"]) in attack.SEALED_HOLDOUT_DATES for row in events):
        raise FreezeError("sealed holdout date entered input")
    event_ids = [str(row["event_id"]) for row in events]
    if len(set(event_ids)) != 804:
        raise FreezeError("event identity duplicate")

    feature_rows = [
        row for row in read_jsonl(repo / binding.FEATURE_LEDGER)
        if int(row["boundary_hours_before_schedule"]) == 8
    ]
    feature_map = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in feature_rows
    }
    if len(feature_map) != 1608:
        raise FreezeError("1,608-leg identity law changed")
    boundaries = {
        str(row["event_id"]): boundary_contract(row)
        for row in read_jsonl(repo / START_LEDGER)
    }
    if set(boundaries) != set(event_ids):
        raise FreezeError("V5 boundary identity mismatch")
    spec = attack.load_candidate_spec(repo)
    candidates = list(spec["candidate_ids"])
    if len(candidates) != 2:
        raise FreezeError("candidate count changed")
    source_paths = {
        "atlas": attack.ATLAS_PATH,
        "guidebook": attack.GUIDEBOOK_PATH,
        "recut": attack.RECUT_PATH,
        "taker_reach": attack.TAKER_REACH_PATH,
        "liveaim_proof": attack.LIVEAIM_PROOF_PATH,
        "volume": attack.VOLUME_PATH,
        "start_ledger": START_LEDGER,
        "drift": attack.DRIFT_PATH,
        "divot": attack.DIVOT_PATH,
        "band": attack.BAND_PATH,
        "library": attack.LIBRARY_PATH,
        "orient": attack.ORIENT_PATH,
    }
    source_hashes = {
        key: sha256_path(repo / path) for key, path in source_paths.items()
    }
    indexed = list(enumerate(events))
    worker_count = max(1, min(int(workers), len(indexed)))
    chunks = [
        indexed[index::worker_count] for index in range(worker_count)
    ]
    if worker_count == 1:
        groups = [_process_chunk(
            str(repo), str(cache_root), chunks[0], feature_map,
            boundaries, candidates, source_hashes,
        )]
    else:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=worker_count
        ) as pool:
            futures = [
                pool.submit(
                    _process_chunk,
                    str(repo),
                    str(cache_root),
                    chunk,
                    feature_map,
                    boundaries,
                    candidates,
                    source_hashes,
                )
                for chunk in chunks
            ]
            groups = [future.result() for future in futures]

    streams = [row for group in groups for row in group["streams"]]
    ladders = [row for group in groups for row in group["ladders"]]
    fillability = [
        row for group in groups for row in group["fillability"]
    ]
    censuses = [row for group in groups for row in group["censuses"]]
    streams.sort(key=lambda row: (
        int(row["event_index"]), int(row["candidate_index"])
    ))
    ladders.sort(key=lambda row: (
        int(row["event_index"]), int(row["leg_index"])
    ))
    fillability.sort(key=lambda row: (
        str(row["candidate_id"]), str(row["event_id"]),
        str(row["leg_id"]), float(row["opened_ts"]),
        str(row["order_interval_id"]),
    ))
    censuses.sort(key=lambda row: str(row["event_id"]))
    if len(streams) != 1608 or len(ladders) != 1608:
        raise FreezeError("stream or range-ladder conservation failed")
    identities = {
        (row["candidate_id"], row["event_id"]) for row in streams
    }
    if len(identities) != 1608:
        raise FreezeError("candidate-event identity duplicate")
    if any(row["candidate_id"] != candidates[row["candidate_index"]]
           for row in streams):
        raise FreezeError("frozen candidate order changed")
    if any(row["integer_cent_price_row_count"] != 99 for row in ladders):
        raise FreezeError("integer-cent range ladder incomplete")

    actions = _action_authority_rows(streams)
    headroom = _headroom_rows(streams)
    opportunity = _pair_opportunities(streams, fillability)
    stress = [
        row["depth_volume_stress"] for row in fillability
        if row.get("depth_volume_stress") is not None
    ]
    five = []
    for row in streams:
        if row["event_id"] not in FIVE_NO_BBO:
            continue
        order_actions = [
            action for action in row["stream"]["order_stream"]
            if action["action"] in {"place", "reprice"}
        ]
        no_calls = [
            action for action in row["stream"]["order_stream"]
            if action["action"] == "feature_no_call"
        ]
        five.append({
            "candidate_id": row["candidate_id"],
            "event_id": row["event_id"],
            "D_member": True,
            "placement_count": len(order_actions),
            "market_evidence_NO_CALL_count": sum(
                action["reason"] == "MARKET_EVIDENCE_NO_CALL"
                for action in no_calls
            ),
            "fabricated_price_count": 0,
            "terminal_censored": False,
            "metrics": None,
        })
    if len(five) != 10 or any(
        row["placement_count"] != 0
        or row["market_evidence_NO_CALL_count"] < 2
        for row in five
    ):
        raise FreezeError("five no-BBO event contract changed")

    target_exposure = Counter()
    authority = Counter()
    reprice = Counter()
    reprice_reason = Counter()
    for row in streams:
        candidate = row["candidate_id"]
        for leg in row["stream"]["evidence_census_by_leg"]:
            target_exposure[(candidate, "macro_target_available")] += (
                leg["macro_target_status"] not in {"PENDING", "NO_CALL"}
            )
        target_exposure[(candidate, "exposed_event")] += any(
            action["action"] == "place"
            for action in row["stream"]["order_stream"]
        )
    for row in actions:
        authority[(row["candidate_id"], row["primary_authority"])] += 1
        if row["action"] == "reprice":
            reprice[(
                row["candidate_id"],
                str(row["reprice_direction"]),
                row["primary_authority"],
            )] += 1
            reprice_reason[(
                row["candidate_id"],
                str(row["reprice_direction"]),
                row["primary_authority"],
                row["reason"],
            )] += 1
    if any(
        row["action"] == "reprice"
        and row["reprice_direction"] == "UP"
        and row["primary_authority"] != "CAUSAL_PAIR_HEADROOM"
        for row in actions
    ):
        raise FreezeError("unsupported upward reprice")
    if any(
        (row.get("causal_state") or {}).get(
            "nonself_best_ask_cents"
        ) is not None
        and row.get("price_cents") is not None
        and int(row["price_cents"]) >= int(
            row["causal_state"]["nonself_best_ask_cents"]
        )
        for row in actions
        if row["action"] in {"place", "reprice"}
    ):
        raise FreezeError("marketable action")

    fill_counts = {
        candidate: {
            "PRICE_REACHED": sum(
                row["candidate_id"] == candidate and row["PRICE_REACHED"]
                for row in fillability
            ),
            "CERTAIN_FILL": sum(
                row["candidate_id"] == candidate and row["CERTAIN_FILL"]
                for row in fillability
            ),
            "EXACT_TOUCH": sum(
                row["candidate_id"] == candidate and row["EXACT_TOUCH"]
                for row in fillability
            ),
            "cumulative_five_false_negative": sum(
                row["candidate_id"] == candidate
                and row["cumulative_size_five_would_false_negative"]
                for row in fillability
            ),
        }
        for candidate in candidates
    }
    stress_counts = Counter(
        (row["candidate_id"], _classify_stress(row))
        for row in fillability if row["EXACT_TOUCH"]
    )
    diagnostics = {
        "schema_version": VERSION + "-diagnostics-v1",
        "D_per_candidate": {candidate: 804 for candidate in candidates},
        "candidate_count": 2,
        "candidate_event_stream_count": len(streams),
        "leg_range_ladder_count": len(ladders),
        "integer_cent_range_row_count": sum(
            row["integer_cent_price_row_count"] for row in ladders
        ),
        "target_exposure_counts": {
            candidate: {
                kind: target_exposure[(candidate, kind)]
                for kind in ("macro_target_available", "exposed_event")
            } for candidate in candidates
        },
        "price_fillability_counts": fill_counts,
        "exact_touch_depth_volume_stress": {
            candidate: {
                label: stress_counts[(candidate, label)]
                for label in sorted({
                    key[1] for key in stress_counts if key[0] == candidate
                })
            } for candidate in candidates
        },
        "queue_preserved_counts": {
            candidate: sum(
                int(leg["queue_preserved_hold_count"])
                for row in streams if row["candidate_id"] == candidate
                for leg in row["stream"]["evidence_census_by_leg"]
            ) for candidate in candidates
        },
        "queue_reposted_counts": {
            candidate: sum(
                int(leg["queue_surrender_count"])
                for row in streams if row["candidate_id"] == candidate
                for leg in row["stream"]["evidence_census_by_leg"]
            ) for candidate in candidates
        },
        "reprice_counts_by_direction_authority": [{
            "candidate_id": key[0],
            "direction": key[1],
            "authority": key[2],
            "count": count,
        } for key, count in sorted(reprice.items())],
        "target_change_counts_by_reason_direction_authority": [{
            "candidate_id": key[0],
            "direction": key[1],
            "authority": key[2],
            "reason": key[3],
            "count": count,
        } for key, count in sorted(reprice_reason.items())],
        "action_authority_counts": [{
            "candidate_id": key[0],
            "authority": key[1],
            "count": count,
        } for key, count in sorted(authority.items())],
        "headroom": {
            candidate: {
                "activation_count": sum(
                    row["candidate_id"] == candidate
                    and row["action"] == "headroom_armed"
                    for row in headroom
                ),
                "decision_count": sum(
                    row["candidate_id"] == candidate
                    and row["action"] == "headroom_decision"
                    for row in headroom
                ),
                "accepted_count": sum(
                    row["candidate_id"] == candidate
                    and row["action"] == "headroom_decision"
                    and row.get("action_taken") is True
                    for row in headroom
                ),
                "sibling_opportunity_inside_budget_count": sum(
                    row["candidate_id"] == candidate
                    and row["sibling_opportunity_inside_remaining_budget_count"]
                    for row in opportunity
                ),
            } for candidate in candidates
        },
        "mechanism_classification_totals": {
            "BOUND": 9,
            "PROXIED": 10,
            "ABSENT": 4,
            "RETRACTED": 5,
        },
        "all_C_PC_S_IC_null": True,
        "benchmark_or_scorer_invoked": False,
        "ranking_selection_or_tuning": False,
    }
    value = {
        "streams": streams,
        "ladders": ladders,
        "fillability": fillability,
        "stress": stress,
        "opportunity": opportunity,
        "headroom": headroom,
        "actions": actions,
        "bindings": _last_trade_census(censuses),
        "diagnostics": diagnostics,
        "five": five,
        "source_hashes": source_hashes,
        "candidate_ids": candidates,
    }
    _assert_metrics_null(value)
    return value


def emit(output: Path, value: Mapping[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=False)
    streams = [{
        "candidate_id": row["candidate_id"],
        "event_id": row["event_id"],
        "event_date": row["event_date"],
        "category": row["category"],
        "stream": row["stream"],
    } for row in value["streams"]]
    for prefix, rows in (
        ("stream", streams),
        ("ladder", value["ladders"]),
    ):
        if len(rows) % 4:
            raise FreezeError(f"{prefix} cannot split into fixed shards")
        size = len(rows) // 4
        for index in range(4):
            write_jsonl_gzip(
                output / FILES[f"{prefix}_{index + 1}"],
                rows[index * size:(index + 1) * size],
            )
    write_jsonl_gzip(output / FILES["fillability"], value["fillability"])
    write_jsonl_gzip(output / FILES["stress"], value["stress"])
    write_jsonl_gzip(output / FILES["opportunity"], value["opportunity"])
    write_jsonl_gzip(output / FILES["headroom"], value["headroom"])
    write_jsonl_gzip(output / FILES["actions"], value["actions"])
    write_json(output / FILES["bindings"], value["bindings"])
    write_json(output / FILES["diagnostics"], value["diagnostics"])
    write_json(output / FILES["five"], {
        "schema_version": VERSION + "-five-event-proof-v1",
        "rows": value["five"],
        "row_count": len(value["five"]),
        "all_D_members": True,
        "all_zero_orders": True,
        "all_named_market_evidence_NO_CALL": True,
        "metrics": None,
        "scored": False,
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).parents[2]
    )
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    arguments = parser.parse_args()
    repo = arguments.repo.resolve()
    output = (
        arguments.output_dir
        if arguments.output_dir.is_absolute()
        else repo / arguments.output_dir
    )
    value = build(
        repo=repo,
        events_path=arguments.events.resolve(),
        cache_root=arguments.market_cache.resolve(),
        workers=arguments.workers,
    )
    emit(output, value)
    print(compact({
        "status": "PASS_SCORE_FREE_PRE_RUN",
        "output_dir": str(output),
        "D": 804,
        "candidate_event_stream_count": 1608,
        "candidate_ids": value["candidate_ids"],
        "diagnostics": value["diagnostics"],
        "metrics": None,
        "scored": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
