#!/usr/bin/env python3
"""Measure one event's Window-1 journey from retained best quotes.

The report deliberately separates:
  * exchange prints and their contract volume;
  * top-of-book states and their observed dwell;
  * print-fitted band labels, which contain no quote-level divot fit.

An archived best quote is treated as effective from its timestamp until the
next retained best-quote change for that leg.  This is a retention statement,
not a claim about unobserved queue depth.
"""

from __future__ import annotations

import argparse
import csv
import html
import importlib.util
import json
import math
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo


REPO = Path(__file__).resolve().parents[2]
REPLAY_SOURCE = REPO / "arb-executor" / "analysis" / "window1_live_v4_replay.py"
ET = ZoneInfo("America/New_York")
NEVER_WAKE_CONTRACT_FLOOR = 2500.0
NEVER_WAKE_SOURCE = ".claude/master_20260709/NEVERWAKE.md"
NEVER_WAKE_SCOPE = "ITF-specific study and production qualification"


def load_replay_module():
    spec = importlib.util.spec_from_file_location(
        "_window1_quote_input_reader", REPLAY_SOURCE
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fmt_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, ET).isoformat(timespec="seconds")


def tminus_minutes(anchor: float, ts: float) -> float:
    return (anchor - ts) / 60.0


def fmt_tminus(value: float) -> str:
    sign = "-" if value >= 0 else "+"
    return f"T{sign}{abs(value):.3f}"


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lo = math.floor(position)
    hi = math.ceil(position)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)


def first_level(levels: list[list[float]]) -> int | None:
    return int(levels[0][0]) if levels else None


def load_leg(
    replay,
    *,
    ticker: str,
    ranges: dict[str, list[int]],
    left_ts: float,
    bell_ts: float,
) -> dict:
    prints, _ = replay.load_print_block(
        ticker, ranges, float("-inf"), float("inf")
    )
    window_prints = [
        row for row in prints if left_ts <= row["ts"] <= bell_ts
    ]
    cumulative_prints = [row for row in prints if row["ts"] <= bell_ts]
    ticks, prior = replay.load_tick_block(ticker, left_ts, bell_ts)

    states = []
    for raw in ticks:
        bid = first_level(raw.get("bids") or [])
        ask = first_level(raw.get("asks") or [])
        last = int(raw.get("last_trade") or 0) or None
        if (
            states
            and states[-1]["bid"] == bid
            and states[-1]["ask"] == ask
        ):
            states[-1]["raw_rows"] += 1
            if last is not None:
                states[-1]["last"] = last
            continue
        states.append(
            {
                "ts": float(raw["ts"]),
                "bid": bid,
                "ask": ask,
                "last": last,
                "raw_rows": 1,
            }
        )
    for index, state in enumerate(states):
        state["end_ts"] = (
            states[index + 1]["ts"] if index + 1 < len(states) else bell_ts
        )
        state["duration_seconds"] = max(
            0.0, state["end_ts"] - state["ts"]
        )

    raw_gaps = [
        float(right["ts"]) - float(left["ts"])
        for left, right in zip(ticks, ticks[1:])
    ]
    return {
        "ticker": ticker,
        "prints": window_prints,
        "cumulative_prints": cumulative_prints,
        "raw_ticks": ticks,
        "prior_tick": prior,
        "states": states,
        "raw_gap_seconds": raw_gaps,
    }


def side_changes(states: list[dict], side: str) -> list[dict]:
    changes = []
    for state in states:
        price = state[side]
        if price is None:
            continue
        if changes and changes[-1]["price"] == price:
            continue
        changes.append({"ts": state["ts"], "price": price})
    return changes


def down_resume_episodes(
    *,
    leg: str,
    side: str,
    states: list[dict],
    scheduled_ts: float,
    bell_ts: float,
) -> list[dict]:
    """Return each uninterrupted down-run followed by its first up-step."""
    changes = side_changes(states, side)
    episodes = []
    index = 1
    episode_id = 0
    while index < len(changes):
        if changes[index]["price"] >= changes[index - 1]["price"]:
            index += 1
            continue
        peak = changes[index - 1]
        trough = changes[index]
        cursor = index + 1
        while (
            cursor < len(changes)
            and changes[cursor]["price"] < changes[cursor - 1]["price"]
        ):
            if changes[cursor]["price"] < trough["price"]:
                trough = changes[cursor]
            cursor += 1
        if (
            cursor >= len(changes)
            or changes[cursor]["price"] <= changes[cursor - 1]["price"]
        ):
            index += 1
            continue
        resume = changes[cursor]
        full_recovery = next(
            (
                row
                for row in changes[cursor:]
                if row["price"] >= peak["price"]
            ),
            None,
        )
        episode_id += 1
        episodes.append(
            {
                "episode_id": f"{leg}_{side}_{episode_id:04d}",
                "leg": leg,
                "side": side,
                "peak_price_cents": peak["price"],
                "peak_ts_et": fmt_ts(peak["ts"]),
                "peak_tminus_scheduled": fmt_tminus(
                    tminus_minutes(scheduled_ts, peak["ts"])
                ),
                "peak_tminus_bell": fmt_tminus(
                    tminus_minutes(bell_ts, peak["ts"])
                ),
                "trough_price_cents": trough["price"],
                "trough_ts_et": fmt_ts(trough["ts"]),
                "trough_tminus_scheduled": fmt_tminus(
                    tminus_minutes(scheduled_ts, trough["ts"])
                ),
                "trough_tminus_bell": fmt_tminus(
                    tminus_minutes(bell_ts, trough["ts"])
                ),
                "resume_price_cents": resume["price"],
                "resume_ts_et": fmt_ts(resume["ts"]),
                "resume_tminus_scheduled": fmt_tminus(
                    tminus_minutes(scheduled_ts, resume["ts"])
                ),
                "resume_tminus_bell": fmt_tminus(
                    tminus_minutes(bell_ts, resume["ts"])
                ),
                "depth_cents": peak["price"] - trough["price"],
                "seconds_peak_to_trough": trough["ts"] - peak["ts"],
                "seconds_at_trough_before_resume": (
                    resume["ts"] - trough["ts"]
                ),
                "seconds_peak_to_resume": resume["ts"] - peak["ts"],
                "full_recovery_ts_et": (
                    fmt_ts(full_recovery["ts"]) if full_recovery else ""
                ),
                "full_recovery_tminus_scheduled": (
                    fmt_tminus(
                        tminus_minutes(scheduled_ts, full_recovery["ts"])
                    )
                    if full_recovery
                    else ""
                ),
                "full_recovery_tminus_bell": (
                    fmt_tminus(tminus_minutes(bell_ts, full_recovery["ts"]))
                    if full_recovery
                    else ""
                ),
            }
        )
        index = cursor + 1
    return episodes


def matching_intervals(
    states: list[dict],
    *,
    side: str,
    predicate,
    scheduled_ts: float,
    bell_ts: float,
) -> list[dict]:
    out = []
    for state in states:
        price = state[side]
        if price is None or not predicate(price):
            continue
        out.append(
            {
                "price_cents": price,
                "bid_cents": state["bid"],
                "ask_cents": state["ask"],
                "start_ts": state["ts"],
                "start_et": fmt_ts(state["ts"]),
                "start_tminus_scheduled": fmt_tminus(
                    tminus_minutes(scheduled_ts, state["ts"])
                ),
                "start_tminus_bell": fmt_tminus(
                    tminus_minutes(bell_ts, state["ts"])
                ),
                "end_ts": state["end_ts"],
                "end_et": fmt_ts(state["end_ts"]),
                "duration_seconds": state["duration_seconds"],
            }
        )
    return out


def merge_adjacent_intervals(intervals: list[dict]) -> list[dict]:
    merged = []
    for row in intervals:
        if merged and merged[-1]["end_ts"] == row["start_ts"]:
            merged[-1]["end_ts"] = row["end_ts"]
            merged[-1]["end_et"] = row["end_et"]
            merged[-1]["duration_seconds"] += row["duration_seconds"]
            merged[-1]["min_price_cents"] = min(
                merged[-1]["min_price_cents"], row["price_cents"]
            )
            merged[-1]["max_price_cents"] = max(
                merged[-1]["max_price_cents"], row["price_cents"]
            )
            continue
        merged.append(
            {
                "start_ts": row["start_ts"],
                "start_et": row["start_et"],
                "start_tminus_scheduled": row[
                    "start_tminus_scheduled"
                ],
                "start_tminus_bell": row["start_tminus_bell"],
                "end_ts": row["end_ts"],
                "end_et": row["end_et"],
                "duration_seconds": row["duration_seconds"],
                "min_price_cents": row["price_cents"],
                "max_price_cents": row["price_cents"],
            }
        )
    return merged


def minimum_summary(
    states: list[dict],
    *,
    side: str,
    scheduled_ts: float,
    bell_ts: float,
) -> dict:
    prices = [state[side] for state in states if state[side] is not None]
    minimum = min(prices)
    intervals = matching_intervals(
        states,
        side=side,
        predicate=lambda price: price == minimum,
        scheduled_ts=scheduled_ts,
        bell_ts=bell_ts,
    )
    return {
        "price_cents": minimum,
        "interval_count": len(intervals),
        "total_observed_seconds": sum(
            row["duration_seconds"] for row in intervals
        ),
        "longest_observed_seconds": max(
            row["duration_seconds"] for row in intervals
        ),
        "intervals": intervals,
    }


def build_dual_series(
    *,
    legs: dict[str, dict],
    scheduled_ts: float,
    bell_ts: float,
    left_ts: float,
) -> list[dict]:
    events = []
    for leg, data in legs.items():
        for sequence, state in enumerate(data["states"], 1):
            events.append(
                (state["ts"], leg, sequence, state["bid"], state["ask"])
            )
    events.sort(key=lambda row: (row[0], row[1], row[2]))
    current = {
        leg: {"bid": None, "ask": None}
        for leg in legs
    }
    output = []
    previous = {
        "ts": left_ts,
        "changed_leg": "GATE_OPEN",
        **{
            f"{leg}_{side}": None
            for leg in legs
            for side in ("bid", "ask")
        },
    }
    for ts, leg, _, bid, ask in events:
        previous["end_ts"] = ts
        previous["duration_seconds"] = max(0.0, ts - previous["ts"])
        output.append(previous)
        current[leg] = {"bid": bid, "ask": ask}
        previous = {
            "ts": ts,
            "changed_leg": leg,
            **{
                f"{name}_{side}": current[name][side]
                for name in legs
                for side in ("bid", "ask")
            },
        }
    previous["end_ts"] = bell_ts
    previous["duration_seconds"] = max(0.0, bell_ts - previous["ts"])
    output.append(previous)

    rows = []
    for sequence, row in enumerate(output, 1):
        rendered = {
            "sequence": sequence,
            "changed_leg": row["changed_leg"],
            "valid_from_et": fmt_ts(row["ts"]),
            "valid_from_tminus_scheduled": fmt_tminus(
                tminus_minutes(scheduled_ts, row["ts"])
            ),
            "valid_from_tminus_bell": fmt_tminus(
                tminus_minutes(bell_ts, row["ts"])
            ),
            "valid_to_et": fmt_ts(row["end_ts"]),
            "duration_seconds": row["duration_seconds"],
        }
        for leg in legs:
            rendered[f"{leg}_bid"] = row.get(f"{leg}_bid")
            rendered[f"{leg}_ask"] = row.get(f"{leg}_ask")
            rendered[f"{leg}_spread"] = (
                row[f"{leg}_ask"] - row[f"{leg}_bid"]
                if row.get(f"{leg}_ask") is not None
                and row.get(f"{leg}_bid") is not None
                else None
            )
        rows.append(rendered)
    return rows


def band_classification(
    *,
    band_map_path: Path,
    leg: str,
    anchor: int,
    close: int,
    low: int,
) -> dict:
    data = json.loads(band_map_path.read_text(encoding="utf-8"))
    category = "ATP_CHALL"
    cat = data["cats"][category]
    features = (anchor, close - anchor, anchor - low)
    mus = cat["feature_mus"]
    sds = cat["feature_sds"]
    z = [(value - mean) / sd for value, mean, sd in zip(features, mus, sds)]
    centroids = cat["centroids_z"]
    distances = [
        sum((value - center) ** 2 for value, center in zip(z, centroid))
        for centroid in centroids
    ]
    centroid_index = min(range(len(distances)), key=distances.__getitem__)
    centroid_raw = [
        centroid * sd + mean
        for centroid, sd, mean in zip(
            centroids[centroid_index], sds, mus
        )
    ]
    band = min(
        cat["bands"],
        key=lambda row: sum(
            (
                (value - target) / sd
            ) ** 2
            for value, target, sd in zip(
                centroid_raw,
                (
                    row["anchor_med"],
                    row["net_med"],
                    row["dip_med"],
                ),
                sds,
            )
        ),
    )
    riser_bands = [
        row for row in cat["bands"] if row["direction"] == "riser"
    ]
    return {
        "leg": leg,
        "category": category,
        "category_band_count": cat["k"],
        "taxonomy_scope": "category-specific; not six universal shapes",
        "fit_features": ["anchor", "net", "dip"],
        "fit_uses_bbo": False,
        "observed_tuple": {
            "anchor_cents": features[0],
            "net_cents": features[1],
            "dip_cents": features[2],
        },
        "nearest_band": band,
        "nearest_centroid_raw": {
            "anchor_cents": round(centroid_raw[0], 3),
            "net_cents": round(centroid_raw[1], 3),
            "dip_cents": round(centroid_raw[2], 3),
        },
        "riser_bands": riser_bands,
        "quote_level_typical_divot": None,
        "quote_level_typical_divot_reason": (
            "band_taxonomy.py fits (anchor, net, dip) from "
            "range_spectrum_v1.jsonl and never reads archived BBO states"
        ),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def svg_step_path(
    states: list[dict],
    side: str,
    *,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    left_ts: float,
    bell_ts: float,
    low: float,
    high: float,
) -> str:
    points = [(row["ts"], row[side]) for row in states if row[side] is not None]
    if not points:
        return ""

    def x(ts):
        return x0 + (ts - left_ts) / (bell_ts - left_ts) * (x1 - x0)

    def y(price):
        return y1 - (price - low) / (high - low) * (y1 - y0)

    commands = [f"M{x(points[0][0]):.2f},{y(points[0][1]):.2f}"]
    for ts, price in points[1:]:
        commands.append(f"H{x(ts):.2f}V{y(price):.2f}")
    commands.append(f"H{x(bell_ts):.2f}")
    return " ".join(commands)


def operational_states(states: list[dict]) -> list[dict]:
    """Drop only the initial market-formation placeholder from plotting."""
    first_tight = next(
        (
            index
            for index, row in enumerate(states)
            if row["bid"] is not None
            and row["ask"] is not None
            and row["ask"] - row["bid"] <= 10
        ),
        0,
    )
    return states[first_tight:]


def write_html(
    path: Path,
    *,
    legs: dict[str, dict],
    dual_rows: list[dict],
    episodes: list[dict],
    summary: dict,
    left_ts: float,
    scheduled_ts: float,
    bell_ts: float,
) -> None:
    width, height = 1220, 620
    panels = {"VRB": (45, 270), "NIK": (340, 565)}
    paths = []
    annotations = []
    grids = []
    for leg, (top, bottom) in panels.items():
        states = operational_states(legs[leg]["states"])
        prices = [
            row[side]
            for row in states
            for side in ("bid", "ask")
            if row[side] is not None
        ]
        low, high = min(prices) - 2, max(prices) + 2
        for tick in range(int(math.ceil(low / 10) * 10), int(high) + 1, 10):
            y = bottom - (tick - low) / (high - low) * (bottom - top)
            grids.append(
                f'<line x1="65" x2="1190" y1="{y:.2f}" y2="{y:.2f}" '
                f'class="grid"/><text x="58" y="{y + 4:.2f}" '
                f'text-anchor="end">{tick}</text>'
            )
        for side, css_class in (("bid", "bid"), ("ask", "ask")):
            d = svg_step_path(
                states,
                side,
                x0=65,
                x1=1190,
                y0=top,
                y1=bottom,
                left_ts=left_ts,
                bell_ts=bell_ts,
                low=low,
                high=high,
            )
            paths.append(f'<path d="{d}" class="{css_class}"/>')
        annotations.append(
            f'<text x="70" y="{top + 18}" class="leg">{leg}</text>'
        )
    for minutes in (480, 360, 240, 120, 0):
        ts = scheduled_ts - minutes * 60
        x = 65 + (ts - left_ts) / (bell_ts - left_ts) * (1190 - 65)
        grids.append(
            f'<line x1="{x:.2f}" x2="{x:.2f}" y1="35" y2="570" '
            f'class="timegrid"/><text x="{x:.2f}" y="594" '
            f'text-anchor="middle">T−{minutes}</text>'
        )

    episode_rows = []
    for row in episodes:
        episode_rows.append(
            "<tr>"
            + "".join(
                f"<td>{html.escape(str(row[key]))}</td>"
                for key in (
                    "leg",
                    "side",
                    "peak_price_cents",
                    "trough_price_cents",
                    "resume_price_cents",
                    "depth_cents",
                    "peak_ts_et",
                    "trough_ts_et",
                    "resume_ts_et",
                    "seconds_at_trough_before_resume",
                )
            )
            + "</tr>"
        )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NIK–VRB quote journey</title>
<style>
body{{font:13px system-ui;margin:18px;color:#172033;background:#f6f7fb}}
h1{{margin:0 0 6px}} p{{max-width:1000px}} svg{{background:white;border:1px solid #ccd2df}}
.grid,.timegrid{{stroke:#dfe4ed;stroke-width:1}} .timegrid{{stroke-dasharray:4 4}}
.bid{{fill:none;stroke:#146c43;stroke-width:1.5}} .ask{{fill:none;stroke:#b42318;stroke-width:1.5}}
.leg{{font-size:16px;font-weight:700}} .legend{{display:flex;gap:18px;margin:8px 0}}
.swatch{{display:inline-block;width:20px;border-top:3px solid;margin-right:5px}}
.swatch.bid{{border-color:#146c43}} .swatch.ask{{border-color:#b42318}}
.wrap{{overflow:auto;max-height:70vh;background:white;border:1px solid #ccd2df}}
table{{border-collapse:collapse;white-space:nowrap;width:100%}}
th,td{{border-bottom:1px solid #e2e6ef;padding:4px 7px;text-align:right}}
th{{position:sticky;top:0;background:#26344d;color:white}}
</style></head><body>
<h1>NIK–VRB retained best quotes, gate to actual bell</h1>
<p>Step lines begin at each leg's first spread at or below 10 cents so the
operational journey remains readable. The complete CSV preserves the initial
5/92 market-formation state. A quote is carried only until the next retained
top-of-book change for that leg.</p>
<div class="legend"><span><i class="swatch bid"></i>best bid</span>
<span><i class="swatch ask"></i>best ask</span></div>
<svg viewBox="0 0 {width} {height}" role="img"
aria-label="Synchronized VRB and NIK best bid and ask step charts">
{''.join(grids)}{''.join(paths)}{''.join(annotations)}
</svg>
<h2>Every down-step followed by an up-step</h2>
<p>{len(episodes)} episodes. Definition: uninterrupted declining side-price
changes ending at the first subsequent increase. Full data are also in CSV.</p>
<div class="wrap"><table><thead><tr>
<th>Leg</th><th>Side</th><th>Peak</th><th>Trough</th><th>Resume</th>
<th>Depth</th><th>Peak time</th><th>Trough time</th><th>Resume time</th>
<th>Trough dwell seconds</th></tr></thead>
<tbody>{''.join(episode_rows)}</tbody></table></div>
</body></html>"""
    path.write_text(document, encoding="utf-8")


def write_inline_visualization(
    path: Path,
    *,
    legs: dict[str, dict],
    left_ts: float,
    scheduled_ts: float,
    bell_ts: float,
) -> None:
    panels = {"VRB": (38, 222), "NIK": (280, 464)}
    plot_left, plot_right = 70.0, 1165.0
    paths = []
    structure = []
    labels = []
    for leg, (top, bottom) in panels.items():
        states = operational_states(legs[leg]["states"])
        prices = [
            row[side]
            for row in states
            for side in ("bid", "ask")
            if row[side] is not None
        ]
        low, high = min(prices) - 2, max(prices) + 2
        for tick in range(
            int(math.ceil(low / 10) * 10), int(high) + 1, 10
        ):
            y = bottom - (tick - low) / (high - low) * (bottom - top)
            structure.append(
                f'<line x1="{plot_left}" x2="{plot_right}" '
                f'y1="{y:.2f}" y2="{y:.2f}" class="q-grid"/>'
                f'<text x="{plot_left - 9}" y="{y + 4:.2f}" '
                f'text-anchor="end">{tick}¢</text>'
            )
        for side, class_name in (("bid", "q-bid"), ("ask", "q-ask")):
            path_data = svg_step_path(
                states,
                side,
                x0=plot_left,
                x1=plot_right,
                y0=top,
                y1=bottom,
                left_ts=left_ts,
                bell_ts=bell_ts,
                low=low,
                high=high,
            )
            paths.append(f'<path d="{path_data}" class="{class_name}"/>')
        minimum_ask = min(
            row["ask"] for row in states if row["ask"] is not None
        )
        first_minimum = next(
            row for row in states if row["ask"] == minimum_ask
        )
        min_x = plot_left + (
            (first_minimum["ts"] - left_ts) / (bell_ts - left_ts)
        ) * (plot_right - plot_left)
        min_y = bottom - (
            (minimum_ask - low) / (high - low)
        ) * (bottom - top)
        labels.extend(
            [
                f'<text x="{plot_left + 4}" y="{top + 17}" '
                f'class="q-leg">{leg}</text>',
                f'<circle cx="{min_x:.2f}" cy="{min_y:.2f}" r="4" '
                f'class="q-min"/>',
                f'<text x="{min_x + 8:.2f}" y="{min_y - 8:.2f}" '
                f'class="q-min-label">ask low {minimum_ask}¢</text>',
            ]
        )
    for minutes in (480, 360, 240, 120, 0):
        ts = scheduled_ts - minutes * 60
        x = plot_left + (ts - left_ts) / (bell_ts - left_ts) * (
            plot_right - plot_left
        )
        structure.append(
            f'<line x1="{x:.2f}" x2="{x:.2f}" y1="26" y2="472" '
            f'class="q-time"/>'
            f'<text x="{x:.2f}" y="497" text-anchor="middle">'
            f'T−{minutes}</text>'
        )
    structure.append(
        f'<text x="{plot_right}" y="517" text-anchor="end">'
        "actual bell (schedule +5m)</text>"
    )
    fragment = f"""<div id="nik-vrb-quote-path" style="width:100%">
  <div class="viz-row text-small" aria-hidden="true">
    <span><i class="q-key q-key-bid"></i>best bid</span>
    <span><i class="q-key q-key-ask"></i>best ask</span>
  </div>
  <svg class="q-chart" viewBox="0 0 1200 525" role="img"
       aria-labelledby="nik-vrb-quote-title nik-vrb-quote-desc">
    <title id="nik-vrb-quote-title">NIK and VRB retained best quotes</title>
    <desc id="nik-vrb-quote-desc">Aligned operational step charts from each
    leg's first spread at or below 10 cents through the actual bell. VRB ask
    reaches 68 cents; NIK ask reaches 18 cents. The complete CSV retains the
    earlier market-formation states.</desc>
    {''.join(structure)}
    {''.join(paths)}
    {''.join(labels)}
  </svg>
  <style>
    #nik-vrb-quote-path .q-chart {{
      width: 100%;
      display: block;
      color: var(--muted-foreground);
    }}
    #nik-vrb-quote-path .q-grid,
    #nik-vrb-quote-path .q-time {{
      stroke: var(--border);
      stroke-width: 1;
      vector-effect: non-scaling-stroke;
    }}
    #nik-vrb-quote-path .q-time {{ stroke-dasharray: 4 5; }}
    #nik-vrb-quote-path .q-bid,
    #nik-vrb-quote-path .q-ask {{
      fill: none;
      stroke-width: 1.75;
      vector-effect: non-scaling-stroke;
    }}
    #nik-vrb-quote-path .q-bid {{ stroke: var(--viz-series-1); }}
    #nik-vrb-quote-path .q-ask {{ stroke: var(--viz-series-2); }}
    #nik-vrb-quote-path .q-leg,
    #nik-vrb-quote-path .q-min-label {{
      fill: var(--foreground);
      font-weight: 500;
    }}
    #nik-vrb-quote-path text {{ fill: var(--muted-foreground); }}
    #nik-vrb-quote-path .q-min {{
      fill: var(--background);
      stroke: var(--viz-series-2);
      stroke-width: 2;
      vector-effect: non-scaling-stroke;
    }}
    #nik-vrb-quote-path .q-key {{
      display: inline-block;
      width: 20px;
      border-top: 3px solid;
      margin-right: 5px;
      vertical-align: middle;
    }}
    #nik-vrb-quote-path .q-key-bid {{ border-color: var(--viz-series-1); }}
    #nik-vrb-quote-path .q-key-ask {{ border-color: var(--viz-series-2); }}
  </style>
</div>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(fragment, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--legs", nargs=2, default=("NIK", "VRB"))
    parser.add_argument("--scheduled-ts", required=True, type=float)
    parser.add_argument("--bell-ts", required=True, type=float)
    parser.add_argument("--print-index", required=True, type=Path)
    parser.add_argument(
        "--band-map",
        type=Path,
        default=REPO / ".claude" / "entrysurface_20260717" / "band_map_v1.json",
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--inline-vis", type=Path)
    args = parser.parse_args()

    replay = load_replay_module()
    ranges = json.loads(args.print_index.read_text(encoding="utf-8"))[
        "ticker_ranges"
    ]
    left_ts = args.scheduled_ts - 8 * 3600
    legs = {
        leg: load_leg(
            replay,
            ticker=f"{args.event}-{leg}",
            ranges=ranges,
            left_ts=left_ts,
            bell_ts=args.bell_ts,
        )
        for leg in args.legs
    }
    dual_rows = build_dual_series(
        legs=legs,
        scheduled_ts=args.scheduled_ts,
        bell_ts=args.bell_ts,
        left_ts=left_ts,
    )
    episodes = []
    for leg, data in legs.items():
        for side in ("bid", "ask"):
            episodes.extend(
                down_resume_episodes(
                    leg=leg,
                    side=side,
                    states=data["states"],
                    scheduled_ts=args.scheduled_ts,
                    bell_ts=args.bell_ts,
                )
            )
    episodes.sort(
        key=lambda row: (
            row["peak_ts_et"],
            row["leg"],
            row["side"],
            row["episode_id"],
        )
    )

    leg_summaries = {}
    for leg, data in legs.items():
        prints = data["prints"]
        cumulative = data["cumulative_prints"]
        operational = operational_states(data["states"])
        first_operational = operational[0]
        bid_minimum = minimum_summary(
            data["states"],
            side="bid",
            scheduled_ts=args.scheduled_ts,
            bell_ts=args.bell_ts,
        )
        ask_minimum = minimum_summary(
            data["states"],
            side="ask",
            scheduled_ts=args.scheduled_ts,
            bell_ts=args.bell_ts,
        )
        gaps = data["raw_gap_seconds"]
        leg_episodes = [row for row in episodes if row["leg"] == leg]
        leg_summaries[leg] = {
            "ticker": data["ticker"],
            "volume": {
                "window1_contracts": round(
                    sum(row["size"] for row in prints), 6
                ),
                "window1_exchange_trade_ids": len(prints),
                "window1_unique_timestamps": len(
                    {row["ts"] for row in prints}
                ),
                "window1_distinct_prices": sorted(
                    {row["price"] for row in prints}
                ),
                "cumulative_contracts_at_bell": round(
                    sum(row["size"] for row in cumulative), 6
                ),
                "pre_gate_contracts": round(
                    sum(row["size"] for row in cumulative if row["ts"] < left_ts),
                    6,
                ),
                "above_2500_contract_never_wake_floor": (
                    sum(row["size"] for row in cumulative)
                    >= NEVER_WAKE_CONTRACT_FLOOR
                ),
            },
            "quote_retention": {
                "raw_bbo_rows": len(data["raw_ticks"]),
                "distinct_top_states": len(data["states"]),
                "first_state_et": fmt_ts(data["states"][0]["ts"]),
                "first_state_tminus_scheduled": fmt_tminus(
                    tminus_minutes(args.scheduled_ts, data["states"][0]["ts"])
                ),
                "first_state_tminus_bell": fmt_tminus(
                    tminus_minutes(args.bell_ts, data["states"][0]["ts"])
                ),
                "last_distinct_top_change_et": fmt_ts(
                    data["states"][-1]["ts"]
                ),
                "last_raw_bbo_et": fmt_ts(
                    float(data["raw_ticks"][-1]["ts"])
                ),
                "quote_carried_to_bell": {
                    "bid_cents": data["states"][-1]["bid"],
                    "ask_cents": data["states"][-1]["ask"],
                },
                "market_formation": {
                    "initial_bid_cents": data["states"][0]["bid"],
                    "initial_ask_cents": data["states"][0]["ask"],
                    "first_spread_at_or_below_10_et": fmt_ts(
                        first_operational["ts"]
                    ),
                    "first_spread_at_or_below_10_tminus_scheduled": (
                        fmt_tminus(
                            tminus_minutes(
                                args.scheduled_ts,
                                first_operational["ts"],
                            )
                        )
                    ),
                    "first_spread_at_or_below_10_tminus_bell": fmt_tminus(
                        tminus_minutes(
                            args.bell_ts, first_operational["ts"]
                        )
                    ),
                    "first_operational_bid_cents": first_operational["bid"],
                    "first_operational_ask_cents": first_operational["ask"],
                    "operational_minimum_bid_cents": min(
                        row["bid"]
                        for row in operational
                        if row["bid"] is not None
                    ),
                    "operational_minimum_ask_cents": min(
                        row["ask"]
                        for row in operational
                        if row["ask"] is not None
                    ),
                },
                "raw_gap_seconds": {
                    "p50": percentile(gaps, 0.50),
                    "p95": percentile(gaps, 0.95),
                    "max": max(gaps),
                },
            },
            "minimum_bid": bid_minimum,
            "minimum_ask": ask_minimum,
            "down_resume_episodes": {
                "count": len(leg_episodes),
                "by_side": dict(Counter(row["side"] for row in leg_episodes)),
                "depth_counts": dict(
                    sorted(
                        Counter(
                            row["depth_cents"] for row in leg_episodes
                        ).items()
                    )
                ),
                "depth_counts_by_side": {
                    side: dict(
                        sorted(
                            Counter(
                                row["depth_cents"]
                                for row in leg_episodes
                                if row["side"] == side
                            ).items()
                        )
                    )
                    for side in ("bid", "ask")
                },
            },
        }

    vrb_ask_le70 = matching_intervals(
        legs["VRB"]["states"],
        side="ask",
        predicate=lambda price: price <= 70,
        scheduled_ts=args.scheduled_ts,
        bell_ts=args.bell_ts,
    )
    merged_vrb_ask_le70 = merge_adjacent_intervals(vrb_ask_le70)
    band_facts = {}
    for leg, data in legs.items():
        prints = data["prints"]
        band_facts[leg] = band_classification(
            band_map_path=args.band_map,
            leg=leg,
            anchor=int(prints[0]["price"]),
            close=int(prints[-1]["price"]),
            low=min(int(row["price"]) for row in prints),
        )

    summary = {
        "schema_version": "window1-quote-divot-report-v1",
        "event": args.event,
        "window": {
            "gate_open_et": fmt_ts(left_ts),
            "scheduled_start_et": fmt_ts(args.scheduled_ts),
            "actual_bell_et": fmt_ts(args.bell_ts),
            "schedule_to_bell_slip_minutes": (
                args.bell_ts - args.scheduled_ts
            )
            / 60.0,
        },
        "quote_dwell_law": (
            "Each distinct retained best bid/ask state is effective from its "
            "timestamp until the next retained best-quote change for that leg."
        ),
        "never_wake_comparison": {
            "threshold_contracts": NEVER_WAKE_CONTRACT_FLOOR,
            "source": NEVER_WAKE_SOURCE,
            "scope": NEVER_WAKE_SCOPE,
            "warning": (
                "NIK-VRB is ATP_CHALL. Both legs clear the numeric floor, "
                "but the deployed qualification was ITF-specific."
            ),
        },
        "legs": leg_summaries,
        "pair_cumulative_contracts_at_bell": round(
            sum(
                item["volume"]["cumulative_contracts_at_bell"]
                for item in leg_summaries.values()
            ),
            6,
        ),
        "vrb_ask_at_or_below_70": {
            "total_observed_seconds": sum(
                row["duration_seconds"] for row in vrb_ask_le70
            ),
            "longest_contiguous_seconds": max(
                row["duration_seconds"] for row in merged_vrb_ask_le70
            ),
            "intervals": vrb_ask_le70,
            "contiguous_spans": merged_vrb_ask_le70,
            "resting_touch_implication": (
                "Under RESTING_TOUCH_FILL_V1, a previously resting YES bid "
                "at 70 or 69 is crossed when the opposite best ask reaches "
                "that limit or lower. Queue depth and maker status are not "
                "proved by this quote-only observation."
            ),
        },
        "band_taxonomy": band_facts,
        "outputs": {
            "dual_quote_series_rows": len(dual_rows),
            "down_resume_episode_rows": len(episodes),
        },
    }

    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "NIKVRB_DUAL_QUOTE_SERIES.csv", dual_rows)
    write_csv(args.out / "NIKVRB_QUOTE_DIVOT_EPISODES.csv", episodes)
    (args.out / "NIKVRB_QUOTE_DIVOT_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_html(
        args.out / "NIKVRB_QUOTE_JOURNEY.html",
        legs=legs,
        dual_rows=dual_rows,
        episodes=episodes,
        summary=summary,
        left_ts=left_ts,
        scheduled_ts=args.scheduled_ts,
        bell_ts=args.bell_ts,
    )
    if args.inline_vis:
        write_inline_visualization(
            args.inline_vis,
            legs=legs,
            left_ts=left_ts,
            scheduled_ts=args.scheduled_ts,
            bell_ts=args.bell_ts,
        )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
