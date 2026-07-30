#!/usr/bin/env python3
"""Build a chronological, two-leg book table from retained replay inputs.

This is an input reader, not an OS replay. It merges the archived BBO states
and true prints for one event and carries both leg states forward on one clock.
"""

from __future__ import annotations

import argparse
import csv
import html
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


REPO = Path(__file__).resolve().parents[2]
REPLAY_SOURCE = REPO / "arb-executor" / "analysis" / "window1_live_v4_replay.py"
GRID = (
    REPO
    / ".claude"
    / "window1_t2_iteration_history"
    / "WINDOW1_T2_GAME_GRID.json"
)
ET = ZoneInfo("America/New_York")
LEGS = ("NIK", "VRB")


def load_replay_module():
    spec = importlib.util.spec_from_file_location(
        "_window1_replay_input_reader", REPLAY_SOURCE
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (
        ordered[upper] - ordered[lower]
    ) * (position - lower)


def fmt_tminus(value: float) -> str:
    sign = "-" if value >= 0 else "+"
    return f"T{sign}{abs(value):.3f}"


def sum_or_blank(*values):
    if any(value in (None, "") for value in values):
        return ""
    return sum(values)


def build_clock_rows(
    *,
    replay,
    event: str,
    scheduled_ts: float,
    bell_ts: float,
    print_ranges: dict,
) -> tuple[list[dict], dict]:
    left_ts = scheduled_ts - 8 * 3600
    tickers = {leg: f"{event}-{leg}" for leg in LEGS}
    events: list[tuple] = [
        (left_ts, -1, 0, "BOUNDARY", "", {"name": "GATE_OPEN"}),
        (bell_ts, 3, 0, "BOUNDARY", "", {"name": "ACTUAL_BELL"}),
    ]
    counts = Counter()
    serial = 0
    for leg, ticker in tickers.items():
        ticks, _ = replay.load_tick_block(ticker, left_ts, bell_ts)
        prints, _ = replay.load_print_block(
            ticker, print_ranges, left_ts, bell_ts
        )
        counts[f"{leg}_bbo_states"] = len(ticks)
        counts[f"{leg}_prints"] = len(prints)
        for item in ticks:
            serial += 1
            events.append((item["ts"], 0, serial, "BBO", leg, item))
        for item in prints:
            serial += 1
            events.append((item["ts"], 1, serial, "PRINT", leg, item))
    events.sort(key=lambda value: (value[0], value[1], value[2]))

    state = {
        leg: {"bid": "", "ask": "", "last": "", "print_size": ""}
        for leg in LEGS
    }
    rows: list[dict] = []
    focus = None
    for sequence, (ts, _, _, kind, leg, payload) in enumerate(events, 1):
        for side in LEGS:
            state[side]["print_size"] = ""
        if kind == "BBO":
            bids = payload.get("bids") or []
            asks = payload.get("asks") or []
            state[leg]["bid"] = int(bids[0][0]) if bids else ""
            state[leg]["ask"] = int(asks[0][0]) if asks else ""
            last = int(payload.get("last_trade") or 0)
            if last:
                state[leg]["last"] = last
        elif kind == "PRINT":
            state[leg]["last"] = int(payload["price"])
            state[leg]["print_size"] = float(payload.get("size") or 0)

        scheduled_min = (scheduled_ts - ts) / 60.0
        bell_min = (bell_ts - ts) / 60.0
        row = {
            "sequence": sequence,
            "event_kind": (
                payload["name"] if kind == "BOUNDARY" else f"{kind}_{leg}"
            ),
            "timestamp_et": datetime.fromtimestamp(ts, ET).isoformat(
                timespec="microseconds"
            ),
            "tminus_scheduled": fmt_tminus(scheduled_min),
            "tminus_scheduled_min": round(scheduled_min, 6),
            "tminus_actual_bell": fmt_tminus(bell_min),
            "tminus_actual_bell_min": round(bell_min, 6),
            "NIK_bid": state["NIK"]["bid"],
            "NIK_ask": state["NIK"]["ask"],
            "NIK_last": state["NIK"]["last"],
            "NIK_print_size": state["NIK"]["print_size"],
            "VRB_bid": state["VRB"]["bid"],
            "VRB_ask": state["VRB"]["ask"],
            "VRB_last": state["VRB"]["last"],
            "VRB_print_size": state["VRB"]["print_size"],
            "combined_bid_total": sum_or_blank(
                state["NIK"]["bid"], state["VRB"]["bid"]
            ),
            "combined_ask_total": sum_or_blank(
                state["NIK"]["ask"], state["VRB"]["ask"]
            ),
            "combined_last_total": sum_or_blank(
                state["NIK"]["last"], state["VRB"]["last"]
            ),
        }
        rows.append(row)
        if (
            kind == "PRINT"
            and leg == "VRB"
            and payload["price"] == 70
            and focus is None
        ):
            focus = dict(row)
            focus["print_trade_id"] = payload.get("trade_id")
            focus["print_taker_side"] = payload.get("taker_side")

    if focus is None:
        raise RuntimeError("VRB 70 print not found")
    return rows, {
        "event": event,
        "gate_open_ts": left_ts,
        "scheduled_start_ts": scheduled_ts,
        "actual_bell_ts": bell_ts,
        "schedule_to_bell_slip_minutes": (bell_ts - scheduled_ts) / 60.0,
        "counts": dict(counts),
        "table_rows": len(rows),
        "focus_vrb_70": focus,
        "combined_total_definition": {
            "bid": "NIK best bid + VRB best bid",
            "ask": "NIK best ask + VRB best ask",
            "last": "NIK last traded + VRB last traded",
            "constructed_midpoint": "not computed",
        },
    }


def corpus_gap_census(event: str) -> dict:
    grid = json.loads(GRID.read_text(encoding="utf-8"))
    usable = []
    exclusions = Counter()
    role_sources = Counter()
    for game in grid["games"]:
        legs = []
        for leg_id, leg in game["legs"].items():
            path = leg.get("price_path") or {}
            low = path.get("tape_low") or {}
            opening = path.get("open") or {}
            regime = (
                (leg.get("instrument_shape") or {}).get("native_regime") or ""
            )
            legs.append(
                {
                    "leg_id": leg_id,
                    "low_ts": low.get("timestamp"),
                    "open_price": opening.get("price_cents"),
                    "native_regime": regime,
                }
            )
        if len(legs) != 2 or any(x["low_ts"] is None for x in legs):
            exclusions["missing_one_or_both_tape_lows"] += 1
            continue
        leaders = [
            leg for leg in legs if "|leader|" in leg["native_regime"]
        ]
        if len(leaders) == 1:
            riser = leaders[0]
            role_source = "grid_native_leader"
        elif (
            all(leg["open_price"] is not None for leg in legs)
            and legs[0]["open_price"] != legs[1]["open_price"]
        ):
            riser = max(legs, key=lambda value: value["open_price"])
            role_source = "higher_window_open_proxy"
        else:
            exclusions["riser_role_unresolved"] += 1
            continue
        other = next(leg for leg in legs if leg is not riser)
        order = (
            "tie"
            if riser["low_ts"] == other["low_ts"]
            else (
                "riser_first"
                if riser["low_ts"] < other["low_ts"]
                else "other_first"
            )
        )
        role_sources[role_source] += 1
        usable.append(
            {
                "event_id": game["event_id"],
                "category": game["category"],
                "gap_minutes": abs(
                    riser["low_ts"] - other["low_ts"]
                ) / 60.0,
                "order": order,
                "riser_leg_id": riser["leg_id"],
                "riser_low_ts": riser["low_ts"],
                "other_low_ts": other["low_ts"],
                "role_source": role_source,
            }
        )

    def summarize(rows: list[dict]) -> dict:
        gaps = [row["gap_minutes"] for row in rows]
        orders = Counter(row["order"] for row in rows)
        return {
            "n": len(rows),
            "gap_minutes": {
                "p25": round(quantile(gaps, 0.25), 3),
                "p50": round(quantile(gaps, 0.50), 3),
                "p75": round(quantile(gaps, 0.75), 3),
                "p90": round(quantile(gaps, 0.90), 3),
                "max": round(max(gaps), 3),
            },
            "ordering": {
                **dict(orders),
                "riser_first_pct": round(
                    100 * orders["riser_first"] / len(rows), 3
                ),
            },
        }

    categories = defaultdict(list)
    for row in usable:
        categories[row["category"]].append(row)
    strict_native = [
        row
        for row in usable
        if row["role_source"] == "grid_native_leader"
    ]
    selected = next(row for row in usable if row["event_id"] == event)
    return {
        "schema_version": "window1-existing-grid-inter-divot-census-v1",
        "source": str(GRID.relative_to(REPO)).replace("\\", "/"),
        "scope": {
            "games_in_existing_grid": len(grid["games"]),
            "usable_games": len(usable),
            "exclusions": dict(exclusions),
            "role_sources": dict(role_sources),
        },
        "definitions": {
            "divot_time": "timestamp of each leg's tape_low in the existing game grid",
            "gap": "absolute difference between the two tape-low timestamps",
            "riser": (
                "grid native leader when present; otherwise the higher-priced "
                "leg at the retained Window-1 open. This is a corpus proxy, "
                "not an 804-event live _orientation_prior replay."
            ),
        },
        "overall": summarize(usable),
        "strict_native_leader_subset": summarize(strict_native),
        "by_category": {
            category: summarize(rows)
            for category, rows in sorted(categories.items())
        },
        "selected_event": selected,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_html(path: Path, rows: list[dict], summary: dict) -> None:
    columns = list(rows[0])
    head = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body = []
    for row in rows:
        focus = (
            row["event_kind"] == "PRINT_VRB"
            and row["VRB_last"] == 70
        )
        cells = "".join(
            f"<td>{html.escape(str(row[column]))}</td>" for column in columns
        )
        body.append(
            f"<tr{' class=\"focus\"' if focus else ''}>{cells}</tr>"
        )
    focus = summary["focus_vrb_70"]
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NIK–VRB dual-book clock</title>
<style>
body{{font:13px system-ui;margin:18px;color:#172033;background:#f6f7fb}}
h1{{margin:0 0 6px}} .note{{margin:4px 0 12px}}
.focusbox{{background:#fff4c2;border:1px solid #d7af00;padding:10px;margin:12px 0}}
.controls{{position:sticky;top:0;background:#f6f7fb;padding:8px 0;z-index:2}}
input{{width:360px;padding:7px}} button{{padding:7px;margin-left:6px}}
.wrap{{overflow:auto;height:78vh;border:1px solid #ccd2df;background:white}}
table{{border-collapse:collapse;white-space:nowrap;width:100%}}
th,td{{border-bottom:1px solid #e2e6ef;padding:4px 7px;text-align:right}}
th{{position:sticky;top:0;background:#26344d;color:white;z-index:1}}
th:nth-child(2),td:nth-child(2),th:nth-child(3),td:nth-child(3){{text-align:left}}
tr.focus{{background:#fff0a6;font-weight:700}} tr:hover{{background:#e9f2ff}}
</style>
</head>
<body>
<h1>NIK–VRB: both books on one clock</h1>
<p class="note">Every retained BBO state and true print from the scheduled
T−8 admission gate through the exact bell. Positive T-minus means before the
anchor. No constructed midpoint is used: combined totals are bid+bid,
ask+ask, and last+last.</p>
<div class="focusbox"><b>VRB 70 print:</b>
{html.escape(focus['tminus_scheduled'])} scheduled /
{html.escape(focus['tminus_actual_bell'])} actual bell.
NIK {focus['NIK_bid']}/{focus['NIK_ask']} last {focus['NIK_last']};
VRB {focus['VRB_bid']}/{focus['VRB_ask']} last {focus['VRB_last']}.
Combined bid/ask/last totals:
{focus['combined_bid_total']}/{focus['combined_ask_total']}/
{focus['combined_last_total']}.</div>
<div class="controls">
<input id="q" placeholder="Filter any cell (for example PRINT_VRB or T-316)">
<button onclick="filterRows()">Filter</button>
<button onclick="showFocus()">VRB 70</button>
<button onclick="resetRows()">Reset</button>
<span id="count"></span>
</div>
<div class="wrap"><table id="grid"><thead><tr>{head}</tr></thead>
<tbody>{''.join(body)}</tbody></table></div>
<script>
const rows=[...document.querySelectorAll('#grid tbody tr')];
const count=document.querySelector('#count');
function setCount(){{count.textContent=' '+rows.filter(r=>r.style.display!=='none').length+' rows';}}
function filterRows(){{const q=document.querySelector('#q').value.toLowerCase();
 rows.forEach(r=>r.style.display=r.textContent.toLowerCase().includes(q)?'':'none');setCount();}}
function resetRows(){{document.querySelector('#q').value='';rows.forEach(r=>r.style.display='');setCount();}}
function showFocus(){{rows.forEach(r=>r.style.display=r.classList.contains('focus')?'':'none');setCount();
 document.querySelector('tr.focus')?.scrollIntoView({{block:'center'}});}}
setCount();
</script>
</body></html>"""
    path.write_text(document, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--scheduled-ts", required=True, type=float)
    parser.add_argument("--bell-ts", required=True, type=float)
    parser.add_argument("--print-index", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    replay = load_replay_module()
    ranges = json.loads(args.print_index.read_text(encoding="utf-8"))[
        "ticker_ranges"
    ]
    rows, summary = build_clock_rows(
        replay=replay,
        event=args.event,
        scheduled_ts=args.scheduled_ts,
        bell_ts=args.bell_ts,
        print_ranges=ranges,
    )
    census = corpus_gap_census(args.event)
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "NIKVRB_DUAL_BOOK_CLOCK.csv", rows)
    write_html(args.out / "NIKVRB_DUAL_BOOK_CLOCK.html", rows, summary)
    (args.out / "NIKVRB_DUAL_BOOK_CLOCK_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.out / "EXISTING_804_INTER_DIVOT_CENSUS.json").write_text(
        json.dumps(census, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"summary": summary, "census": census}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
