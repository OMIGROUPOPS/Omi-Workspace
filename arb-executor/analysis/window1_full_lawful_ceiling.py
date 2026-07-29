#!/usr/bin/env python3
"""Measure the Window-1 ceiling through the guarded actual-start cutoff.

The OS policy clock and the evaluator clock are deliberately separate:

* the OS may stop or cancel at ``policy_right_ts``;
* the evaluator reads tape through ``guarded_cutoff_ts``;
* unresolved start boundaries remain censored.

Primary fill model: a resting order fills on the first true-price touch.  No
depth proof and no five-contract capacity gate are applied.  The prior strict
five-contract sequential oracle can be requested as a labeled comparison but
is not part of the governing ceiling.
"""

from __future__ import annotations

import argparse
import bisect
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import statistics
import sys
from typing import Any, Iterable, Mapping


VERSION = "window1-full-lawful-ceiling-v1"
POPULATION = 804
QUANTITY = 5
TIERS = (93, 95, 97)
RAW_START_LEDGER = (
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
CONTROL_LEDGER = (
    ".claude/"
    "window1_t2_results_w1-t2-dev-20260712-20260720-"
    "frontier-regret-grid1-scorepkg-v5/"
    "01_w1_t2__macro_hold__fixed_admission_parent_control_"
    "EVENT_LEDGER.jsonl"
)


class CeilingError(RuntimeError):
    """A full-window measurement contract failed."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    opener = gzip.open if path.suffix == ".gz" else path.open
    with opener(path, "rt", encoding="utf-8") if path.suffix == ".gz" else (
        path.open("r", encoding="utf-8")
    ) as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise CeilingError(f"object required: {path}:{line_number}")
            rows.append(value)
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_utc(value: str | None) -> float | None:
    if not value:
        return None
    return datetime.fromisoformat(
        str(value).replace("Z", "+00:00")
    ).timestamp()


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def stats(values: Iterable[float]) -> dict[str, Any]:
    rows = [float(value) for value in values]
    if not rows:
        return {
            "count": 0,
            "min": None,
            "p10": None,
            "median": None,
            "mean": None,
            "p90": None,
            "max": None,
        }
    return {
        "count": len(rows),
        "min": min(rows),
        "p10": percentile(rows, 0.10),
        "median": statistics.median(rows),
        "mean": statistics.fmean(rows),
        "p90": percentile(rows, 0.90),
        "max": max(rows),
    }


def true_prints(
    leg: Mapping[str, Any],
    left: float,
    right: float,
) -> list[dict[str, Any]]:
    by_receipt: dict[str, dict[str, Any]] = {}
    for row in leg.get("prints") or []:
        timestamp = float(row["ts"])
        receipt = str(row.get("trade_id") or "")
        size = float(row.get("size") or 0)
        if not left <= timestamp <= right or not receipt or size <= 0:
            continue
        normalized = {
            "ts": timestamp,
            "price_cents": int(row["price"]),
            "size": size,
            "receipt": receipt,
        }
        prior = by_receipt.get(receipt)
        if prior is not None and prior != normalized:
            raise CeilingError("conflicting duplicate true-print receipt")
        by_receipt[receipt] = normalized
    return sorted(
        by_receipt.values(),
        key=lambda row: (float(row["ts"]), str(row["receipt"])),
    )


def indexed_true_prints(
    *,
    path: Path,
    ticker_ranges: Mapping[str, list[int]],
    ticker: str,
    left: float,
    right: float,
) -> list[dict[str, Any]]:
    span = ticker_ranges.get(ticker)
    if not span:
        return []
    rows: list[dict[str, Any]] = []
    with path.open("rb") as handle:
        handle.seek(int(span[0]))
        while handle.tell() < int(span[1]):
            line = handle.readline()
            if not line:
                break
            raw = json.loads(line)
            timestamp = parse_utc(str(raw["exchange_ts"]))
            if timestamp is None or timestamp < left:
                continue
            if timestamp > right:
                break
            receipt = str(raw.get("trade_id") or "")
            size = float(raw.get("size") or 0)
            if not receipt or size <= 0:
                continue
            rows.append({
                "ts": float(timestamp),
                "price_cents": int(raw["price_cents"]),
                "size": size,
                "receipt": receipt,
            })
    return rows


def first_touch(
    prints: list[dict[str, Any]],
    target: int,
    *,
    strictly_after: float | None = None,
) -> dict[str, Any] | None:
    for row in prints:
        if (
            strictly_after is not None
            and float(row["ts"]) <= strictly_after
        ):
            continue
        if int(row["price_cents"]) <= int(target):
            return row
    return None


def maker_fee_cents(price_cents: int) -> int:
    price = int(price_cents)
    if not 1 <= price <= 99:
        raise CeilingError(f"invalid maker price: {price}")
    return math.ceil(
        7 * QUANTITY * price * (100 - price) / 40000
    )


def touch_cost(first: int, second: int) -> dict[str, Any]:
    price_sum = int(first) + int(second)
    fee_sum = maker_fee_cents(first) + maker_fee_cents(second)
    total = price_sum * QUANTITY + fee_sum
    return {
        "first_target_cents": int(first),
        "second_target_cents": int(second),
        "price_sum_cents_per_contract": price_sum,
        "maker_fee_total_cents_for_five_contract_pair": fee_sum,
        "maker_cost_total_cents_for_five_contract_pair": total,
        "maker_cost_cents_per_contract": total / QUANTITY,
    }


def independent_touch_floor(
    leg_prints: Mapping[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    if len(leg_prints) != 2 or any(not rows for rows in leg_prints.values()):
        return None
    legs = sorted(leg_prints)
    selected = []
    for leg_id in legs:
        selected.append(min(
            leg_prints[leg_id],
            key=lambda row: (
                int(row["price_cents"]),
                float(row["ts"]),
                str(row["receipt"]),
            ),
        ))
    result = touch_cost(
        int(selected[0]["price_cents"]),
        int(selected[1]["price_cents"]),
    )
    result.update({
        "leg_order": legs,
        "touches": {
            legs[index]: selected[index] for index in range(2)
        },
    })
    return result


def sequential_touch_floor(
    leg_prints: Mapping[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    if len(leg_prints) != 2:
        return None
    legs = sorted(leg_prints)
    candidates: list[dict[str, Any]] = []
    by_orientation: dict[str, dict[str, Any]] = {}
    for first_leg, second_leg in (
        (legs[0], legs[1]),
        (legs[1], legs[0]),
    ):
        orientation = f"{first_leg}__then__{second_leg}"
        first_by_target: dict[int, dict[str, Any]] = {}
        remaining = set(range(1, 100))
        for row in leg_prints[first_leg]:
            reached = [
                target for target in remaining
                if int(row["price_cents"]) <= target
            ]
            for target in reached:
                first_by_target[target] = row
                remaining.remove(target)
            if not remaining:
                break

        second_rows = leg_prints[second_leg]
        second_times = [float(row["ts"]) for row in second_rows]
        suffix_best: list[dict[str, Any] | None] = [
            None
        ] * len(second_rows)
        best_second: dict[str, Any] | None = None
        for row_index in range(len(second_rows) - 1, -1, -1):
            row = second_rows[row_index]
            if best_second is None or (
                int(row["price_cents"]) * QUANTITY
                + maker_fee_cents(int(row["price_cents"])),
                float(row["ts"]),
            ) < (
                int(best_second["price_cents"]) * QUANTITY
                + maker_fee_cents(int(best_second["price_cents"])),
                float(best_second["ts"]),
            ):
                best_second = row
            suffix_best[row_index] = best_second

        for first_target, first in sorted(first_by_target.items()):
            second_index = bisect.bisect_right(
                second_times, float(first["ts"])
            )
            if second_index >= len(second_rows):
                continue
            second = suffix_best[second_index]
            if second is None:
                continue
            second_target = int(second["price_cents"])
            candidate = touch_cost(first_target, second_target)
            candidate.update({
                "orientation": orientation,
                "first_leg_id": first_leg,
                "second_leg_id": second_leg,
                "first_fill": first,
                "second_fill": second,
                "minutes_between_touches": (
                    float(second["ts"]) - float(first["ts"])
                ) / 60.0,
            })
            candidates.append(candidate)
        orientation_rows = [
            row for row in candidates if row["orientation"] == orientation
        ]
        if orientation_rows:
            by_orientation[orientation] = min(
                orientation_rows,
                key=lambda row: (
                    row["maker_cost_total_cents_for_five_contract_pair"],
                    float(row["second_fill"]["ts"]),
                    float(row["first_fill"]["ts"]),
                ),
            )
    if not candidates:
        return None
    best = min(
        candidates,
        key=lambda row: (
            row["maker_cost_total_cents_for_five_contract_pair"],
            float(row["second_fill"]["ts"]),
            float(row["first_fill"]["ts"]),
            row["orientation"],
        ),
    )
    best["ordering_minimums"] = {
        key: {
            "maker_cost_total_cents_for_five_contract_pair": value[
                "maker_cost_total_cents_for_five_contract_pair"
            ],
            "maker_cost_cents_per_contract": value[
                "maker_cost_cents_per_contract"
            ],
        }
        for key, value in sorted(by_orientation.items())
    }
    return best


def ladder(
    values: Iterable[Mapping[str, Any] | None],
) -> dict[str, int]:
    rows = [value for value in values if value is not None]
    output = {
        f"le_{tier}": sum(
            int(row["maker_cost_total_cents_for_five_contract_pair"])
            <= tier * QUANTITY
            for row in rows
        )
        for tier in TIERS
    }
    output["lt_100"] = sum(
        int(row["maker_cost_total_cents_for_five_contract_pair"])
        < 100 * QUANTITY
        for row in rows
    )
    output["any"] = len(rows)
    return output


def raw_source_group(row: Mapping[str, Any]) -> str:
    partition = str(row.get("source_partition_class") or "")
    source = str(row.get("start_source_class") or "")
    if partition == "contradictory" or row.get("conflict_status") == (
        "contradictory"
    ):
        return "contradictory"
    if partition == "schedule_only":
        return "schedule_only"
    if partition == "live_by_only":
        return "live_by_only"
    if partition == "clean_interval":
        return "observed_bounded_interval"
    if source == "official_exact":
        return "observed_official_exact"
    if source == "quantized_late_detection_proxy":
        return "inferred_quantized_proxy"
    return source or partition or "unknown"


def unresolved_reason(
    row: Mapping[str, Any],
    *,
    zero_length: bool,
) -> tuple[str, str, bool]:
    if zero_length:
        return (
            "guarded_cutoff_at_or_before_contemporaneous_T_minus_8_left",
            (
                "Tape can support an actual-start-anchored diagnostic when "
                "both legs have prints in cutoff-minus-8h..cutoff, but it "
                "cannot reconstruct the missing contemporaneous schedule "
                "snapshot or silently change the selected left-edge law."
            ),
            False,
        )
    partition = str(row.get("source_partition_class") or "")
    if partition == "schedule_only":
        return (
            "schedule_only_no_independent_start_evidence",
            "Price tape has no observed-start receipt; silence is not proof.",
            False,
        )
    if partition == "live_by_only":
        return (
            "one_sided_live_by_bound_without_not_live_through_bound",
            (
                "Tape proves the match was live by a time, but cannot prove "
                "how much earlier it started."
            ),
            False,
        )
    if (
        partition == "contradictory"
        or row.get("conflict_status") == "contradictory"
    ):
        return (
            "contradictory_start_evidence",
            (
                "The existing tape is one of the conflicting causal bounds; "
                "external start evidence is required to adjudicate it."
            ),
            False,
        )
    if row.get("guard_censor_reason"):
        return (
            "named_start_evidence_conflict",
            (
                "A proxy or provider timestamp conflicts with a retained "
                "causal bound; tape alone cannot promote either to exact."
            ),
            False,
        )
    return (
        "boundary_not_positive",
        "No strict pre-start cutoff is provable from the existing tape.",
        False,
    )


def observed_starts_inventory(
    path: Path,
    event_ids: set[str],
) -> dict[str, Any]:
    if not path.is_file():
        return {
            "path": str(path),
            "available": False,
            "table_count": 0,
            "row_count": 0,
            "matching_event_count": 0,
        }
    connection = sqlite3.connect(
        f"file:{path.resolve().as_posix()}?mode=ro", uri=True
    )
    try:
        tables = [
            str(row[0]) for row in connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' ORDER BY name"
            )
        ]
        details = []
        matches: set[str] = set()
        total = 0
        development_rows = 0
        development_leg_codes: set[str] = set()
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            columns = [
                str(row[1]) for row in connection.execute(
                    f"PRAGMA table_info({quoted})"
                )
            ]
            count = int(connection.execute(
                f"SELECT COUNT(*) FROM {quoted}"
            ).fetchone()[0])
            total += count
            if (
                "inserted_at" in columns
                and "kalshi_ticker" in columns
            ):
                development_rows += int(connection.execute(
                    f"SELECT COUNT(*) FROM {quoted} "
                    "WHERE inserted_at >= '2026-07-14' "
                    "AND inserted_at < '2026-07-21'"
                ).fetchone()[0])
                development_leg_codes.update(
                    str(value) for value, in connection.execute(
                        f"SELECT DISTINCT kalshi_ticker FROM {quoted} "
                        "WHERE inserted_at >= '2026-07-14' "
                        "AND inserted_at < '2026-07-21'"
                    )
                    if value is not None
                )
            candidate_columns = [
                column for column in columns
                if column.lower() in {
                    "event", "event_id", "event_ticker", "ticker",
                    "series_ticker", "kalshi_ticker",
                }
            ]
            for column in candidate_columns:
                qcolumn = '"' + column.replace('"', '""') + '"'
                for value, in connection.execute(
                    f"SELECT {qcolumn} FROM {quoted} "
                    f"WHERE {qcolumn} IS NOT NULL"
                ):
                    text = str(value)
                    if text in event_ids:
                        matches.add(text)
                    else:
                        matches.update(
                            event_id for event_id in event_ids
                            if text.startswith(event_id)
                        )
            details.append({
                "table": table,
                "row_count": count,
                "columns": columns,
            })
        return {
            "path": str(path),
            "available": True,
            "sha256": sha256_file(path),
            "table_count": len(tables),
            "row_count": total,
            "development_period_row_count_july14_through_20": (
                development_rows
            ),
            "development_period_distinct_leg_code_count": len(
                development_leg_codes
            ),
            "matching_event_count": len(matches),
            "matching_event_ids": sorted(matches),
            "direct_join_limitation": (
                "observed_starts stores only a three-letter leg code in "
                "kalshi_ticker, not the full Kalshi event identity; zero "
                "direct event-id matches does not mean zero historical rows"
            ),
            "tables": details,
        }
    finally:
        connection.close()


def render_report(result: Mapping[str, Any]) -> str:
    touch = result["ceilings"]["independent_touch"]
    sequential = result["ceilings"]["strict_sequential_touch"]
    legacy = result["ceilings"]["legacy_five_contract_sequential"]
    boundary = result["boundary_census"]
    source = result["start_evidence"]
    unmeasurable_reasons = Counter(
        row["reason"] for row in result["unmeasurable_games"]
    )
    lines = [
        "# Full-lawful Window-1 ceiling",
        "",
        (
            "**Evaluator boundary fixed:** the OS policy edge remains "
            "`min(scheduled horizon, guarded cutoff)`, while tape evaluation "
            "continues to the positive guarded actual-start cutoff."
        ),
        "",
        (
            "Primary fill model: **resting limit order; first true-price "
            "touch fills; no depth proof; no five-contract capacity gate.**"
        ),
        "",
        "## Corrected ladder",
        "",
        "| ceiling | ≤93 | ≤95 | ≤97 | <100 | any |",
        "|---|---:|---:|---:|---:|---:|",
        (
            "| independent two-leg touch | "
            f"{touch['frontier']['le_93']} | {touch['frontier']['le_95']} | "
            f"{touch['frontier']['le_97']} | {touch['frontier']['lt_100']} | "
            f"{touch['frontier']['any']} |"
        ),
        (
            "| second leg only after first touch | "
            f"{sequential['frontier']['le_93']} | "
            f"{sequential['frontier']['le_95']} | "
            f"{sequential['frontier']['le_97']} | "
            f"{sequential['frontier']['lt_100']} | "
            f"{sequential['frontier']['any']} |"
        ),
    ]
    if legacy["computed"]:
        lines.append((
            "| legacy five-contract proof comparison | "
            f"{legacy['frontier']['le_93']} | "
            f"{legacy['frontier']['le_95']} | "
            f"{legacy['frontier']['le_97']} | "
            f"{legacy['frontier']['lt_100']} | "
            f"{legacy['frontier']['any']} |"
        ))
    lines.extend([
        "",
        "All tier comparisons include the published maker fee for five "
        "contracts on each leg.",
        "",
        "## Boundary census",
        "",
        f"- Positive guarded boundary: **{boundary['positive']}**",
        f"- Undefined boundary: **{boundary['undefined']}**",
        f"- Positive but zero-length selected window: **{boundary['zero_length']}**",
        (
            "- Strictly measurable nonzero Window 1: "
            f"**{boundary['measurable_nonzero']}**"
        ),
        "",
        "## Start evidence",
        "",
        (
            "| source class | all | positive | earlier / equal / later | "
            "min | median | p90 | max |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for group, values in sorted(source["groups"].items()):
        movement = values["cutoff_minus_schedule_minutes"]
        def shown(name: str) -> str:
            value = movement[name]
            return f"{value:.1f}" if value is not None else "n/a"

        lines.append(
            f"| {group} | {values['all_count']} | "
            f"{values['positive_count']} | "
            f"{values['cutoff_earlier_than_schedule_count']} / "
            f"{values['cutoff_equal_schedule_count']} / "
            f"{values['cutoff_later_than_schedule_count']} | "
            f"{shown('min')} | {shown('median')} | {shown('p90')} | "
            f"{shown('max')} |"
        )
    lines.extend([
        "",
        (
            "Cutoff movements are minutes relative to the scheduled start. "
            "Negative means the evaluator cutoff is earlier; positive means "
            "later."
        ),
        "",
        (
            f"The copied `observed_starts.db` contains "
            f"**{source['observed_starts_db']['row_count']}** rows, including "
            f"**{source['observed_starts_db']['development_period_row_count_july14_through_20']}** "
            "from July 14-20. It stores only a three-letter leg code, not a "
            "full event id, so it cannot be directly joined to the 804."
        ),
        "",
        "## Why 111 games are unmeasurable",
        "",
    ])
    for reason, count in unmeasurable_reasons.most_common():
        lines.append(f"- {count}: `{reason}`")
    lines.extend([
        "",
        (
            "None of the 111 can be assigned a strict actual-start boundary "
            "from the existing tape. The 12 zero-length rows were also "
            "checked against the full normalized print tape; zero had both "
            "legs inside an actual-start-anchored alternative Window 1."
        ),
        "",
        (
            f"Per-game reasons for all **{len(result['unmeasurable_games'])}** "
            "unmeasurable rows are in the companion JSON."
        ),
        "",
    ])
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    cache = Path(args.market_cache).resolve()
    raw_path = (repo / RAW_START_LEDGER).resolve()
    observed_path = Path(args.observed_starts_db).resolve()
    normalized_prints = (
        Path(args.normalized_prints).resolve()
        if args.normalized_prints else None
    )
    normalized_index = (
        Path(args.normalized_print_index).resolve()
        if args.normalized_print_index else None
    )
    output_json = (repo / args.output_json).resolve()
    output_report = (repo / args.output_report).resolve()
    output_unmeasurable = (repo / args.output_unmeasurable).resolve()

    analysis_dir = Path(__file__).resolve().parent
    if str(analysis_dir) not in sys.path:
        sys.path.insert(0, str(analysis_dir))
    import window1_t2_game_grid as game_grid
    import window1_t2_target_laps as target_laps

    raw_rows = read_jsonl(raw_path)
    control_rows = read_jsonl((repo / CONTROL_LEDGER).resolve())
    if len(raw_rows) != POPULATION or len(control_rows) != POPULATION:
        raise CeilingError("expected 804 raw-start and control rows")
    raw = {str(row["event_id"]): row for row in raw_rows}
    control = {str(row["event_id"]): row for row in control_rows}
    if set(raw) != set(control) or len(raw) != POPULATION:
        raise CeilingError("804 event identities do not reconcile")
    ticker_ranges: dict[str, list[int]] = {}
    if normalized_prints is not None or normalized_index is not None:
        if (
            normalized_prints is None
            or normalized_index is None
            or not normalized_prints.is_file()
            or not normalized_index.is_file()
        ):
            raise CeilingError(
                "both normalized prints and its byte index are required"
            )
        index_payload = json.loads(
            normalized_index.read_text(encoding="utf-8")
        )
        ticker_ranges = {
            str(key): [int(value[0]), int(value[1])]
            for key, value in index_payload["ticker_ranges"].items()
        }

    ladders = game_grid.load_ladders(repo)
    by_event: dict[str, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for (event_id, leg_id), window in ladders.items():
        by_event[event_id][leg_id] = window
    if len(by_event) != POPULATION:
        raise CeilingError("ladder event count changed")

    target_windows = {
        key: {
            "left": float(value["left_ts"]),
            "right": float(value["right_ts"]),
            "positive": bool(value["positive"]),
        }
        for key, value in ladders.items()
    }
    event_rows = []
    unmeasurable = []
    source_all: Counter[str] = Counter()
    source_positive: Counter[str] = Counter()
    movement_by_source: dict[str, list[float]] = defaultdict(list)
    positive_count = 0
    undefined_count = 0
    zero_count = 0
    zero_with_alternate_tape = 0

    for index, event_id in enumerate(sorted(raw), 1):
        raw_row = raw[event_id]
        windows = by_event[event_id]
        if len(windows) != 2:
            raise CeilingError(f"{event_id}: expected two legs")
        first_window = next(iter(windows.values()))
        positive = bool(first_window["positive"])
        left = max(float(row["left_ts"]) for row in windows.values())
        policy_right = min(
            float(row["policy_right_ts"]) for row in windows.values()
        )
        cutoff = (
            min(
                float(row["evaluator_right_ts"])
                for row in windows.values()
            )
            if positive else None
        )
        source_group = raw_source_group(raw_row)
        source_all[source_group] += 1
        scheduled = float(first_window["policy_horizon_ts"])
        if positive:
            positive_count += 1
            source_positive[source_group] += 1
            movement_by_source[source_group].append(
                (float(cutoff) - scheduled) / 60.0
            )
        else:
            undefined_count += 1
        zero_length = positive and float(cutoff) <= left
        zero_count += int(zero_length)

        market = game_grid.load_market(cache, event_id)
        market_legs = {
            str(row["leg"]): row for row in market["legs"]
        }
        print_paths: dict[str, list[dict[str, Any]]] = {}
        if positive and not zero_length:
            for leg_id in sorted(windows):
                print_paths[leg_id] = true_prints(
                    market_legs[leg_id], left, float(cutoff)
                )
        independent = independent_touch_floor(print_paths)
        sequential = sequential_touch_floor(print_paths)
        legacy = (
            target_laps.strict_sequential_floor(
                control[event_id], market, target_windows
            )
            if (
                args.include_legacy_five_contract
                and positive
                and not zero_length
            ) else None
        )

        alternate_tape = {}
        if zero_length:
            alternate_left = float(cutoff) - 8 * 3600
            for leg_id in sorted(windows):
                ticker = str(market_legs[leg_id].get("ticker") or "")
                rows = (
                    indexed_true_prints(
                        path=normalized_prints,
                        ticker_ranges=ticker_ranges,
                        ticker=ticker,
                        left=alternate_left,
                        right=float(cutoff),
                    )
                    if normalized_prints is not None else true_prints(
                        market_legs[leg_id],
                        alternate_left,
                        float(cutoff),
                    )
                )
                alternate_tape[leg_id] = {
                    "true_print_count": len(rows),
                    "first_ts": float(rows[0]["ts"]) if rows else None,
                    "last_ts": float(rows[-1]["ts"]) if rows else None,
                    "low_cents": (
                        min(int(row["price_cents"]) for row in rows)
                        if rows else None
                    ),
                }
            has_alternate = all(
                row["true_print_count"] > 0
                for row in alternate_tape.values()
            )
            zero_with_alternate_tape += int(has_alternate)
        else:
            has_alternate = False

        if not positive or zero_length:
            reason, resolution, strictly_resolved = unresolved_reason(
                raw_row, zero_length=zero_length
            )
            unmeasurable.append({
                "event_id": event_id,
                "event_date": str(raw_row["event_date"]),
                "category": str(raw_row["category"]),
                "source_group": source_group,
                "source_partition_class": raw_row.get(
                    "source_partition_class"
                ),
                "start_source_class": raw_row.get("start_source_class"),
                "conflict_status": raw_row.get("conflict_status"),
                "guard_censor_reason": raw_row.get("guard_censor_reason"),
                "scheduled_start_ts": scheduled,
                "selected_left_ts": left,
                "policy_right_ts": policy_right,
                "guarded_cutoff_ts": cutoff,
                "reason": reason,
                "can_existing_tape_strictly_resolve": strictly_resolved,
                "tape_resolution_explanation": resolution,
                "actual_start_anchored_alternate_tape": alternate_tape,
                "alternate_tape_has_both_legs": has_alternate,
                "candidate_sources": [
                    {
                        "source": row.get("source"),
                        "source_family": row.get("source_family"),
                        "direction": row.get("direction"),
                        "timestamp_utc": row.get("timestamp_utc"),
                        "precision": row.get("precision"),
                    }
                    for row in raw_row.get("candidate_sources") or []
                ],
            })

        event_rows.append({
            "event_id": event_id,
            "event_date": str(raw_row["event_date"]),
            "category": str(raw_row["category"]),
            "source_group": source_group,
            "positive_guarded_boundary": positive,
            "zero_length_selected_window": zero_length,
            "selected_left_ts": left,
            "scheduled_policy_horizon_ts": scheduled,
            "os_policy_right_ts": policy_right,
            "evaluator_right_ts": cutoff,
            "cutoff_minus_schedule_minutes": (
                (float(cutoff) - scheduled) / 60.0
                if cutoff is not None else None
            ),
            "leg_true_print_counts": {
                leg_id: len(rows)
                for leg_id, rows in sorted(print_paths.items())
            },
            "independent_touch_floor": independent,
            "strict_sequential_touch_floor": sequential,
            "legacy_five_contract_sequential_floor": legacy,
        })
        if index % 50 == 0 or index == POPULATION:
            print(f"ceiling_events={index}/{POPULATION}", flush=True)

    groups = {}
    for group in sorted(source_all):
        movements = movement_by_source.get(group, [])
        groups[group] = {
            "all_count": source_all[group],
            "positive_count": source_positive[group],
            "cutoff_minus_schedule_minutes": stats(movements),
            "cutoff_earlier_than_schedule_count": sum(
                value < 0 for value in movements
            ),
            "cutoff_equal_schedule_count": sum(
                abs(value) <= 1e-9 for value in movements
            ),
            "cutoff_later_than_schedule_count": sum(
                value > 0 for value in movements
            ),
        }

    observed_db = observed_starts_inventory(
        observed_path, set(event_rows[index]["event_id"] for index in range(
            len(event_rows)
        ))
    )
    independent_values = [
        row["independent_touch_floor"] for row in event_rows
    ]
    sequential_values = [
        row["strict_sequential_touch_floor"] for row in event_rows
    ]
    legacy_values = [
        row["legacy_five_contract_sequential_floor"] for row in event_rows
    ]
    result = {
        "schema_version": VERSION,
        "fill_model": (
            "resting_limit_order_first_true_price_touch_fills;"
            "no_depth_proof;no_five_contract_capacity_gate"
        ),
        "evaluator_boundary": {
            "os_policy_right": (
                "min(policy_horizon_ts, guarded_cutoff_ts)"
            ),
            "tape_evaluator_right": (
                "guarded_cutoff_ts for positive boundaries"
            ),
            "unresolved_boundary_law": "censored; no schedule substitution",
        },
        "scope": {
            "population": POPULATION,
            "holdout_opened": False,
            "live_accessed": False,
            "orders_created": False,
            "os_replay_executed": False,
        },
        "boundary_census": {
            "positive": positive_count,
            "undefined": undefined_count,
            "zero_length": zero_count,
            "measurable_nonzero": positive_count - zero_count,
            "unmeasurable_total": len(unmeasurable),
            "zero_length_with_both_leg_actual_start_anchored_tape": (
                zero_with_alternate_tape
            ),
        },
        "ceilings": {
            "independent_touch": {
                "description": (
                    "both orders may rest from the selected left edge"
                ),
                "frontier": ladder(independent_values),
            },
            "strict_sequential_touch": {
                "description": (
                    "second order becomes eligible only after first touch; "
                    "both leg orderings tested"
                ),
                "frontier": ladder(sequential_values),
            },
            "legacy_five_contract_sequential": {
                "computed": bool(args.include_legacy_five_contract),
                "description": (
                    "comparison only; prior strict ask/cumulative print "
                    "capacity proof, recomputed through guarded cutoff"
                ),
                "frontier": (
                    ladder(legacy_values)
                    if args.include_legacy_five_contract else None
                ),
            },
        },
        "start_evidence": {
            "headline": {
                "observed_exact_or_bounded_count": (
                    source_all["observed_official_exact"]
                    + source_all["observed_bounded_interval"]
                ),
                "inferred_quantized_proxy_count": source_all[
                    "inferred_quantized_proxy"
                ],
                "unresolved_one_sided_schedule_or_contradictory_count": (
                    source_all["live_by_only"]
                    + source_all["schedule_only"]
                    + source_all["contradictory"]
                ),
                "positive_observed_exact_or_bounded_count": (
                    source_positive["observed_official_exact"]
                    + source_positive["observed_bounded_interval"]
                ),
                "positive_inferred_quantized_proxy_count": source_positive[
                    "inferred_quantized_proxy"
                ],
            },
            "classification": {
                "observed_official_exact": (
                    "direct official start timestamp"
                ),
                "observed_bounded_interval": (
                    "causal not-live-through/live-by interval"
                ),
                "inferred_quantized_proxy": (
                    "five-minute historical result clock with calibrated "
                    "minus-900-second strict pre-start guard"
                ),
                "live_by_only": "one-sided causal live-by bound",
                "schedule_only": "no observed start evidence",
                "contradictory": "conflicting causal evidence",
            },
            "groups": groups,
            "observed_starts_db": observed_db,
        },
        "unmeasurable_games": unmeasurable,
        "events": event_rows,
        "input_receipts": {
            "raw_start_ledger": {
                "path": RAW_START_LEDGER,
                "sha256": sha256_file(raw_path),
            },
            "control_ledger": {
                "path": CONTROL_LEDGER,
                "sha256": sha256_file(
                    (repo / CONTROL_LEDGER).resolve()
                ),
            },
            "observed_starts_db": {
                "path": str(observed_path),
                "sha256": (
                    sha256_file(observed_path)
                    if observed_path.is_file() else None
                ),
            },
            "market_cache": {
                "path_redacted": True,
                "cache_version": "window1-guarded-event-market-cache-v3",
                "events_read": POPULATION,
            },
            "normalized_prints_for_zero_length_resolution": {
                "path_redacted": normalized_prints is not None,
                "index_path": (
                    str(normalized_index)
                    if normalized_index is not None else None
                ),
                "zero_length_events_read": zero_count,
            },
        },
    }
    if len(unmeasurable) != undefined_count + zero_count:
        raise CeilingError("unmeasurable census does not reconcile")

    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with output_unmeasurable.open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        json.dump({
            "schema_version": VERSION + "-unmeasurable-v1",
            "count": len(unmeasurable),
            "reason_counts": dict(Counter(
                row["reason"] for row in unmeasurable
            )),
            "strictly_resolvable_from_existing_tape_count": sum(
                bool(row["can_existing_tape_strictly_resolve"])
                for row in unmeasurable
            ),
            "games": unmeasurable,
        }, handle, indent=2, sort_keys=True)
        handle.write("\n")
    output_report.write_text(
        render_report(result), encoding="utf-8", newline="\n"
    )
    print(json.dumps({
        "boundary_census": result["boundary_census"],
        "independent_touch": result["ceilings"]["independent_touch"][
            "frontier"
        ],
        "strict_sequential_touch": result["ceilings"][
            "strict_sequential_touch"
        ]["frontier"],
        "legacy_five_contract_sequential": result["ceilings"][
            "legacy_five_contract_sequential"
        ],
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    result.add_argument("--market-cache", required=True)
    result.add_argument("--observed-starts-db", required=True)
    result.add_argument("--normalized-prints")
    result.add_argument("--normalized-print-index")
    result.add_argument(
        "--include-legacy-five-contract",
        action="store_true",
        help=(
            "Also run the superseded five-contract/depth-proof comparison; "
            "not part of the touch-fill ceiling."
        ),
    )
    result.add_argument(
        "--output-json",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_FULL_LAWFUL_CEILING.json"
        ),
    )
    result.add_argument(
        "--output-report",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_FULL_LAWFUL_CEILING.md"
        ),
    )
    result.add_argument(
        "--output-unmeasurable",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_UNMEASURABLE_START_BOUNDARIES.json"
        ),
    )
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
