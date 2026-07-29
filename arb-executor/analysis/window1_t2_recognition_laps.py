#!/usr/bin/env python3
"""Offline Window-1 T2 recognition laps on the frozen 804-event development set.

This is intentionally a recognition-only harness.  It does not alter control
targets, orders, fills, completions, or the full-tape opportunity census.
Every instrument read is made from the repository artifacts named below and
from market observations available no later than the event's guarded cutoff.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


VERSION = "window1-t2-recognition-laps-v1"
D_REQUIRED = 804
TAPE_OPPORTUNITY_REQUIRED = 692
CONTROL_COMPLETIONS_REQUIRED = 131
CONTROL_NEVER_RECOGNIZED_MISSES_REQUIRED = 510
DEV_DATES = {f"2026-07-{day:02d}" for day in range(12, 21)}

CONTROL_LEDGER = (
    ".claude/window1_t2_results_"
    "w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v5/"
    "01_w1_t2__macro_hold__fixed_admission_parent_control_EVENT_LEDGER.jsonl"
)
FEATURE_MATRIX = ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl"
ATLAS_PATH = ".claude/trendpath/ATLAS_V1.json"
BAND_PATH = ".claude/entrysurface_20260717/band_map_v1.json"
DRIFT_PATH = ".claude/entrysurface_20260717/drift_surfaces_v1.json"
DIVOT_PATH = ".claude/entrysurface_20260717/divot_tables_v1.json"
LIBRARY_PATH = ".claude/trendpath/LIBRARY_V1.json"
REACH_PATH = ".claude/takerreach/LAW.json"
AIM_PATH = "arb-executor/data/shape_corpus/aim_v2_operational_LATCHCAL.json"


class RecognitionLapError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RecognitionLapError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise RecognitionLapError(
                    f"JSON object required: {path}:{line_number}"
                )
            rows.append(value)
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def price_zone(price: float) -> str:
    if price <= 25:
        return "le25"
    if price <= 50:
        return "26_50"
    if price <= 75:
        return "51_75"
    return "ge75"


def recognition_bucket(anchor: float, net: float, dip: float) -> str:
    anchor_bucket = (
        "a25" if anchor <= 25 else
        "a50" if anchor <= 50 else
        "a75" if anchor <= 75 else "a95"
    )
    net_bucket = (
        "dn10" if net <= -10 else
        "dn3" if net <= -3 else
        "flat" if net < 3 else
        "up3" if net < 10 else "up10"
    )
    dip_bucket = "d0" if dip <= 2 else "d3" if dip <= 9 else "d10"
    return f"{anchor_bucket}|{net_bucket}|{dip_bucket}"


def default_flat_band(
    band_map: Mapping[str, Any], category: str, anchor: float,
) -> str | None:
    category_row = band_map.get("cats", {}).get(category)
    if not category_row or category_row.get("thin"):
        return None
    bands = [
        row for row in category_row.get("bands") or []
        if row.get("direction") == "flat"
    ]
    if not bands:
        return None
    return str(min(
        bands,
        key=lambda row: abs(float(row["anchor_med"]) - anchor),
    )["band"])


def drift_band_signal(
    *,
    band_map: Mapping[str, Any],
    drift: Mapping[str, Any],
    divot: Mapping[str, Any],
    category: str,
    anchor: float,
    current: float,
    dip: float,
) -> dict[str, Any] | None:
    net = current - anchor
    bucket = recognition_bucket(anchor, net, dip)
    cell = (
        drift.get("recognition", {})
        .get(f"{category}|h6", {})
        .get(bucket)
    )
    purity = float((cell or {}).get("purity") or 0)
    if not cell or purity < 0.5:
        return None
    band = str(cell["top"])
    row = divot.get("bands", {}).get(band)
    depth = (row or {}).get("depth_p50")
    if depth is None:
        return None
    return {
        "instrument": "band_taxonomy",
        "band": band,
        "bucket": bucket,
        "purity": purity,
        "depth_cents": float(depth),
    }


def atlas_signal(
    atlas: Mapping[str, Any],
    category: str,
    role: str,
    anchor: float,
) -> dict[str, Any] | None:
    atlas_role = "leader" if role == "favorite" else "underdog"
    key = f"{category}|{atlas_role}|{price_zone(anchor)}"
    page = atlas.get("pages", {}).get(key)
    depth = ((page or {}).get("bottom") or {}).get("depth_p50")
    if not page or page.get("verdict") != "PATH" or depth is None:
        return None
    return {
        "instrument": "w1_drift_atlas",
        "page": key,
        "page_n": int(page.get("n") or 0),
        "depth_cents": float(depth),
    }


def volume_band(
    library: Mapping[str, Any], category: str, first_hour_prints: int,
) -> str | None:
    cuts = library.get("meta", {}).get("vol_cuts", {}).get(category)
    if not isinstance(cuts, list) or len(cuts) != 2:
        return None
    if first_hour_prints <= int(cuts[0]):
        return "lo"
    if first_hour_prints <= int(cuts[1]):
        return "mid"
    return "hi"


def library_signal(
    library: Mapping[str, Any],
    category: str,
    anchor: float,
    first_hour_prints: int,
) -> dict[str, Any] | None:
    vol = volume_band(library, category, first_hour_prints)
    if vol is None:
        return None
    key = f"{category}|{price_zone(anchor)}|{vol}"
    cell = library.get("cells", {}).get(key)
    if not cell:
        return None
    dip_frequency = cell.get("dip_freq")
    depths = cell.get("depth_p25_50_75")
    never_wake = cell.get("never_wake_p")
    if (
        dip_frequency is None
        or float(dip_frequency) < 0.5
        or not isinstance(depths, list)
        or len(depths) != 3
        or depths[1] is None
        or (never_wake is not None and float(never_wake) >= 0.5)
    ):
        return None
    return {
        "instrument": "cohort_library",
        "cell": key,
        "cell_n": int(cell.get("n") or 0),
        "dip_frequency": float(dip_frequency),
        "never_wake_probability": (
            None if never_wake is None else float(never_wake)
        ),
        "depth_cents": float(depths[1]),
    }


def reach_annotation(
    reach: Mapping[str, Any],
    category: str,
    flow_state: str,
    depth: float,
    remaining_hours: float,
) -> dict[str, Any] | None:
    row = reach.get("law", {}).get(f"{category}|{flow_state}")
    rates = (row or {}).get("rate_per_hr") or {}
    depth_key = str(max(1, int(math.floor(depth + 0.5))))
    value = rates.get(depth_key)
    if value is None:
        return None
    rate = float(value)
    probability = 1.0 - math.exp(-rate * max(0.0, remaining_hours))
    return {
        "instrument": "reach_law",
        "cell": f"{category}|{flow_state}",
        "depth_cents": int(depth_key),
        "rate_per_hour": rate,
        "remaining_hours": remaining_hours,
        "reach_probability": probability,
    }


def aim_v2_signals(
    aim: Mapping[str, Any],
    category: str,
    states: list[dict[str, Any]],
    recognition_ts: float,
    cutoff: float,
) -> dict[str, dict[str, Any]]:
    by_role = {str(row["role"]): row for row in states}
    favorite = by_role.get("favorite")
    underdog = by_role.get("underdog")
    if (
        favorite is None
        or underdog is None
        or favorite.get("available") is not True
        or underdog.get("available") is not True
    ):
        return {}
    fav_price = float(favorite["current_bid_cents"])
    fav_bucket = min(4, max(0, int(fav_price // 20)))
    time_bucket = int(max(0.0, cutoff - recognition_ts) // 600)
    key = f"{category}|{fav_bucket}|{time_bucket}"
    cell = aim.get("table", {}).get(key)
    if (
        not cell
        or cell.get("null_reason") is not None
        or cell.get("dip_admissible") is not True
    ):
        return {}
    output: dict[str, dict[str, Any]] = {}
    for role, field in (("favorite", "fdip50"), ("underdog", "ddip50")):
        state = by_role[role]
        dip_delta = cell.get(field)
        if dip_delta is None or float(dip_delta) >= 0:
            continue
        output[str(state["leg_id"])] = {
            "instrument": "aim_v2",
            "cell": key,
            "cell_source": cell.get("source"),
            "cell_n": int(cell.get("n") or 0),
            "honest_n": int(cell.get("n_honest") or 0),
            "depth_cents": -float(dip_delta),
        }
    return output


def load_market(path: Path, event_id: str) -> dict[str, Any]:
    file_path = path / f"{event_id}.json.gz"
    if not file_path.is_file():
        raise RecognitionLapError(f"market cache missing: {event_id}")
    with gzip.open(file_path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if (
        value.get("event_id") != event_id
        or value.get("cache_version")
        != "window1-guarded-event-market-cache-v3"
        or not isinstance(value.get("legs"), list)
        or len(value["legs"]) != 2
    ):
        raise RecognitionLapError(f"market cache contract failed: {event_id}")
    return value


def first_at_or_after(
    rows: list[Mapping[str, Any]], timestamp: float, cutoff: float,
) -> Mapping[str, Any] | None:
    return next(
        (
            row for row in rows
            if timestamp <= float(row["ts"]) < cutoff
        ),
        None,
    )


def build_leg_states(
    *,
    event: Mapping[str, Any],
    market: Mapping[str, Any],
    features: Mapping[tuple[str, str], Mapping[str, Any]],
    left: float,
    cutoff: float,
    allow_birth_fallback: bool,
) -> tuple[list[dict[str, Any]], float]:
    checkpoint = left + 2 * 3600
    states: list[dict[str, Any]] = []
    recognition_times: list[float] = []
    for leg in market["legs"]:
        ticker = str(leg["ticker"])
        feature = features.get((str(event["event_id"]), ticker))
        if feature is None:
            raise RecognitionLapError(
                f"T-8 feature missing: {event['event_id']}:{ticker}"
            )
        snapshots = list(leg.get("snapshots") or [])
        birth = first_at_or_after(snapshots, left, cutoff)
        recognition = first_at_or_after(snapshots, checkpoint, cutoff)
        recognition_source = "t6_checkpoint"
        if (
            birth is not None
            and recognition is None
            and allow_birth_fallback
        ):
            recognition = birth
            recognition_source = (
                "birth_book_before_short_guarded_window_cutoff"
            )
        if birth is None or recognition is None:
            states.append({
                "leg_id": str(feature.get("leg_id") or leg.get("leg") or ""),
                "ticker": ticker,
                "role": str(feature.get("role") or ""),
                "available": False,
                "signals": [],
            })
            continue
        recognition_ts = float(recognition["ts"])
        recognition_times.append(recognition_ts)
        anchor = float(birth["best_bid"])
        current = float(recognition["best_bid"])
        history = [
            row for row in snapshots
            if float(birth["ts"]) <= float(row["ts"]) <= recognition_ts
        ]
        dip = max(
            0.0,
            anchor - min(
                [float(row["best_bid"]) for row in history] or [anchor]
            ),
        )
        prints = list(leg.get("prints") or [])
        first_hour_prints = sum(
            left <= float(row["ts"]) <= min(cutoff, left + 3600)
            for row in prints
        )
        first_half_hour_prints = sum(
            left <= float(row["ts"]) <= min(cutoff, left + 1800)
            for row in prints
        )
        flow_state = (
            "open" if first_half_hour_prints >= 16 else
            "warm" if first_half_hour_prints > 0 else "quiet"
        )
        states.append({
            "leg_id": str(feature.get("leg_id") or leg.get("leg") or ""),
            "ticker": ticker,
            "role": str(feature.get("role") or ""),
            "available": True,
            "birth_ts": float(birth["ts"]),
            "recognition_ts": recognition_ts,
            "recognition_source": recognition_source,
            "anchor_bid_cents": anchor,
            "current_bid_cents": current,
            "net_cents": current - anchor,
            "dip_cents": dip,
            "first_hour_print_count": first_hour_prints,
            "first_half_hour_print_count": first_half_hour_prints,
            "flow_state": flow_state,
            "signals": [],
        })
    return states, (max(recognition_times) if recognition_times else checkpoint)


def instrument_event(
    *,
    event: Mapping[str, Any],
    market: Mapping[str, Any],
    features: Mapping[tuple[str, str], Mapping[str, Any]],
    left: float,
    cutoff: float,
    surfaces: Mapping[str, Any],
    allow_birth_fallback: bool,
) -> dict[str, Any]:
    category = str(event["category"])
    states, recognition_ts = build_leg_states(
        event=event,
        market=market,
        features=features,
        left=left,
        cutoff=cutoff,
        allow_birth_fallback=allow_birth_fallback,
    )
    for state in states:
        if not state["available"]:
            continue
        anchor = float(state["anchor_bid_cents"])
        current = float(state["current_bid_cents"])
        dip = float(state["dip_cents"])
        role = str(state["role"])
        atlas = atlas_signal(
            surfaces["atlas"], category, role, anchor
        )
        band = drift_band_signal(
            band_map=surfaces["band"],
            drift=surfaces["drift"],
            divot=surfaces["divot"],
            category=category,
            anchor=anchor,
            current=current,
            dip=dip,
        )
        library = library_signal(
            surfaces["library"],
            category,
            anchor,
            int(state["first_hour_print_count"]),
        )
        for signal in (atlas, band, library):
            if signal is not None:
                state["signals"].append(signal)
        reach_inputs = [
            signal for signal in state["signals"]
            if signal["instrument"] in {
                "w1_drift_atlas", "band_taxonomy", "cohort_library",
            }
        ]
        for source in reach_inputs:
            reach = reach_annotation(
                surfaces["reach"],
                category,
                str(state["flow_state"]),
                float(source["depth_cents"]),
                (cutoff - float(state["recognition_ts"])) / 3600.0,
            )
            if reach is not None:
                reach["source_instrument"] = source["instrument"]
                state["signals"].append(reach)
    aim_signals = aim_v2_signals(
        surfaces["aim"], category, states, recognition_ts, cutoff
    )
    for state in states:
        aim = aim_signals.get(str(state["leg_id"]))
        if aim is not None:
            state["signals"].append(aim)
    instruments = sorted({
        str(signal["instrument"])
        for state in states
        for signal in state["signals"]
        if signal["instrument"] != "reach_law"
    })
    return {
        "event_id": str(event["event_id"]),
        "category": category,
        "left_ts": left,
        "guarded_cutoff_ts": cutoff,
        "recognition_ts": recognition_ts,
        "recognized": bool(instruments),
        "recognized_both_legs": all(
            any(
                signal["instrument"] != "reach_law"
                for signal in state["signals"]
            )
            for state in states
        ),
        "recognition_instruments": instruments,
        "legs": states,
    }


def render_report(result: Mapping[str, Any]) -> str:
    lines = [
        "# Window-1 T2 recognition laps",
        "",
        (
            "`NEVER_RECOGNIZED` was the fallback for a null recognition "
            "field, not a finding that the tape lacked an opportunity."
        ),
        "",
    ]
    for lap in result["laps"]:
        lines.extend([
            f"## {lap['lap_id']}",
            "",
            (
                f"completions: **{lap['completions_out_of_804']}/804**, "
                f"and **{lap['completions_out_of_692']}/692** the tape proves"
            ),
            "",
            (
                "how many of the 510 we now see: "
                f"**{lap['recognized_of_510']}/510**"
            ),
            "",
            f"what changed since last lap: {lap['change_since_last_lap']}",
            "",
        ])
    lines.extend([
        "No target, exposure, order, fill, or completion was changed. "
        "Holdout stayed sealed; live and network access stayed off.",
        "",
    ])
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    events_path = Path(args.events).resolve()
    market_path = Path(args.market_cache).resolve()
    output_json = (repo / args.output_json).resolve()
    output_report = (repo / args.output_report).resolve()

    analysis_dir = repo / "arb-executor" / "analysis"
    sys.path.insert(0, str(analysis_dir))
    import window1_fit_benchmark as fit

    control_path = repo / CONTROL_LEDGER
    feature_path = repo / FEATURE_MATRIX
    control = read_jsonl(control_path)
    events = fit.load_events(events_path)
    event_map = {str(row["event_id"]): row for row in events}
    feature_rows = read_jsonl(feature_path)
    features = {
        (str(row["event_id"]), str(row["ticker"])): row
        for row in feature_rows
        if int(row["boundary_hours_before_schedule"]) == 8
    }

    if len(control) != D_REQUIRED or len(event_map) != D_REQUIRED:
        raise RecognitionLapError("development population is not 804")
    if set(event_map) != {str(row["event_id"]) for row in control}:
        raise RecognitionLapError("control/event identity set differs")
    if {str(row["event_date"]) for row in control} - DEV_DATES:
        raise RecognitionLapError("non-development date entered the run")
    if len(features) != 1608:
        raise RecognitionLapError("T-8 feature population is not 1,608")

    tape_opportunities = [
        row for row in control
        if row["pair_regret"]["combined_five_contract_proven_floor_cents"]
        is not None
    ]
    completions = [row for row in control if row["C"] is True]
    baseline_misses = [
        row for row in tape_opportunities
        if row["C"] is not True
        and row["primary_loss_stage"] == "NEVER_RECOGNIZED"
    ]
    if len(tape_opportunities) != TAPE_OPPORTUNITY_REQUIRED:
        raise RecognitionLapError("full-tape opportunity census changed")
    if len(completions) != CONTROL_COMPLETIONS_REQUIRED:
        raise RecognitionLapError("control completion count changed")
    if len(baseline_misses) != CONTROL_NEVER_RECOGNIZED_MISSES_REQUIRED:
        raise RecognitionLapError("control 510-miss census changed")

    surfaces = {
        "atlas": read_json(repo / ATLAS_PATH),
        "band": read_json(repo / BAND_PATH),
        "drift": read_json(repo / DRIFT_PATH),
        "divot": read_json(repo / DIVOT_PATH),
        "library": read_json(repo / LIBRARY_PATH),
        "reach": read_json(repo / REACH_PATH),
        "aim": read_json(repo / AIM_PATH),
    }
    event_rows_lap_1: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    plateau_rows: list[dict[str, Any]] = []
    for index, control_row in enumerate(baseline_misses, 1):
        event_id = str(control_row["event_id"])
        event = event_map[event_id]
        market = load_market(market_path, event_id)
        scheduled = fit.parse_utc(
            event["scheduled_start_exchange_ts"],
            "scheduled_start_exchange_ts",
        )
        left = scheduled - 8 * 3600
        cutoff = float(control_row["guarded_cutoff_ts"])
        if left >= cutoff:
            raise RecognitionLapError(
                f"invalid guarded window in 510 set: {event_id}"
            )
        event_rows_lap_1.append(instrument_event(
            event=event,
            market=market,
            features=features,
            left=left,
            cutoff=cutoff,
            surfaces=surfaces,
            allow_birth_fallback=False,
        ))
        corrected = instrument_event(
            event=event,
            market=market,
            features=features,
            left=left,
            cutoff=cutoff,
            surfaces=surfaces,
            allow_birth_fallback=True,
        )
        repeated = instrument_event(
            event=event,
            market=market,
            features=features,
            left=left,
            cutoff=cutoff,
            surfaces=surfaces,
            allow_birth_fallback=True,
        )
        if compact(corrected) != compact(repeated):
            raise RecognitionLapError(
                f"plateau replay differs: {event_id}"
            )
        event_rows.append(corrected)
        plateau_rows.append(repeated)
        if index % 50 == 0 or index == len(baseline_misses):
            print(
                f"recognition_events={index}/{len(baseline_misses)}",
                flush=True,
            )

    lap_1_recognized_ids = sorted(
        row["event_id"]
        for row in event_rows_lap_1
        if row["recognized"]
    )
    recognized_ids = sorted(
        row["event_id"] for row in event_rows if row["recognized"]
    )
    recognized_both_ids = sorted(
        row["event_id"]
        for row in event_rows
        if row["recognized_both_legs"]
    )
    by_instrument = Counter()
    for row in event_rows:
        for instrument in row["recognition_instruments"]:
            by_instrument[instrument] += 1
    signal_counts = Counter()
    for row in event_rows:
        for state in row["legs"]:
            for signal in state["signals"]:
                signal_counts[str(signal["instrument"])] += 1

    integrated_change = (
        "wired the existing W1 drift atlas, T-6h band taxonomy, "
        "cohort LIBRARY_V1, reach-law annotation, and AIM_V2 pair-state "
        "table into the control recognition read; targeting and fills "
        "were left unchanged"
    )
    laps = [
        {
            "lap_id": "control",
            "completions_out_of_804": len(completions),
            "completions_out_of_692": sum(
                row["C"] is True for row in tape_opportunities
            ),
            "recognized_of_510": 0,
            "change_since_last_lap": (
                "none; frozen control with no recognition organ"
            ),
        },
        {
            "lap_id": "recognition_lap_1",
            "completions_out_of_804": len(completions),
            "completions_out_of_692": sum(
                row["C"] is True for row in tape_opportunities
            ),
            "recognized_of_510": len(lap_1_recognized_ids),
            "change_since_last_lap": integrated_change,
        },
        {
            "lap_id": "recognition_lap_2",
            "completions_out_of_804": len(completions),
            "completions_out_of_692": sum(
                row["C"] is True for row in tape_opportunities
            ),
            "recognized_of_510": len(recognized_ids),
            "change_since_last_lap": (
                "changed one thing: when the guarded window ends before "
                "the nominal T-6 checkpoint, static atlas/library "
                "recognition now reads the first available birth book "
                "instead of remaining null; no post-cutoff data is read"
            ),
        },
        {
            "lap_id": "recognition_lap_3_plateau",
            "completions_out_of_804": len(completions),
            "completions_out_of_692": sum(
                row["C"] is True for row in tape_opportunities
            ),
            "recognized_of_510": len(recognized_ids),
            "change_since_last_lap": (
                "nothing; a second execution of the corrected "
                "recognition function produced byte-identical event "
                "records"
            ),
        },
    ]
    result = {
        "schema_version": VERSION,
        "scope": {
            "development_dates": sorted(DEV_DATES),
            "D": D_REQUIRED,
            "holdout_opened": False,
            "live_accessed": False,
            "network_accessed": False,
            "targets_changed": False,
            "orders_changed": False,
            "fills_changed": False,
            "completions_changed": False,
        },
        "classification_semantics": {
            "control_never_recognized_is_null_fallback": True,
            "code_path": (
                "window1_t2_scoring_runner_v4.execute -> "
                "classify_regret(recognized="
                "best_recognized_opportunity_cents is not None) -> "
                "if not recognized: NEVER_RECOGNIZED"
            ),
        },
        "input_receipts": {
            "events": {
                "bytes": events_path.stat().st_size,
                "sha256": sha256_file(events_path),
            },
            "control_ledger": {
                "path": CONTROL_LEDGER,
                "bytes": control_path.stat().st_size,
                "sha256": sha256_file(control_path),
            },
            "feature_matrix": {
                "path": FEATURE_MATRIX,
                "bytes": feature_path.stat().st_size,
                "sha256": sha256_file(feature_path),
            },
            "surfaces": {
                path: sha256_file(repo / path)
                for path in (
                    ATLAS_PATH, BAND_PATH, DRIFT_PATH, DIVOT_PATH,
                    LIBRARY_PATH, REACH_PATH, AIM_PATH,
                )
            },
            "market_cache": {
                "path_redacted": True,
                "cache_version": (
                    "window1-guarded-event-market-cache-v3"
                ),
                "events_read": len(event_rows),
            },
        },
        "baseline": {
            "completions": len(completions),
            "full_tape_opportunities": len(tape_opportunities),
            "full_tape_misses": (
                len(tape_opportunities)
                - sum(row["C"] is True for row in tape_opportunities)
            ),
            "never_recognized_full_tape_misses": len(baseline_misses),
        },
        "recognition": {
            "lap_1_recognized_event_count": len(
                lap_1_recognized_ids
            ),
            "lap_1_recognized_event_ids": lap_1_recognized_ids,
            "recognized_event_count": len(recognized_ids),
            "recognized_event_ids": recognized_ids,
            "recognized_both_legs_count": len(recognized_both_ids),
            "recognized_both_legs_event_ids": recognized_both_ids,
            "event_coverage_by_instrument": dict(sorted(
                by_instrument.items()
            )),
            "leg_signal_count_by_instrument": dict(sorted(
                signal_counts.items()
            )),
            "events": event_rows,
            "plateau_replay_identical": (
                compact(event_rows) == compact(plateau_rows)
            ),
        },
        "laps": laps,
        "stop_reason": (
            "recognition count stopped moving on the deterministic "
            "plateau replay"
        ),
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        )
    with output_report.open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(render_report(result))
    print(json.dumps({
        "completions_out_of_804": len(completions),
        "completions_out_of_692": sum(
            row["C"] is True for row in tape_opportunities
        ),
        "recognized_of_510": len(recognized_ids),
        "recognized_both_legs_of_510": len(recognized_both_ids),
        "event_coverage_by_instrument": dict(sorted(
            by_instrument.items()
        )),
        "holdout_opened": False,
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--repo", required=True)
    result.add_argument("--events", required=True)
    result.add_argument("--market-cache", required=True)
    result.add_argument(
        "--output-json",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_T2_RECOGNITION_LAPS.json"
        ),
    )
    result.add_argument(
        "--output-report",
        default=(
            ".claude/window1_t2_iteration_history/"
            "WINDOW1_T2_RECOGNITION_LAPS.md"
        ),
    )
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
