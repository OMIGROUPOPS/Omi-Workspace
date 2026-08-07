#!/usr/bin/env python3
"""Grade frozen V36 STRICT output against the frozen 57daf3c1 union-reach ruler.

This is a read-only artifact builder.  It does not import or invoke policy code.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83"
REACH_COMMIT = "57daf3c15ad618098a810566d24127df8f17f3f9"
V36_PACKAGE_REL = Path(".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806")
QUOTE_REL = Path(".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_CENSUS.json")
REACH_SUMMARY_REL = Path(".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MAKER_RESULTS_THREE_CHANNELS.json")
RECONCILIATION_REL = Path(".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RECONCILIATION_SEAL_804.json")
EXPECTED_REACH = {
    "print_rows": 373203,
    "trade": {"both": 773, "one": 11, "none": 20, "legs": 1557, "sum": 72870},
    "quote": {"both": 692, "one": 0, "none": 112, "legs": 1384, "sum": 68143},
    "union": {
        "both": 785, "one": 0, "none": 19, "legs": 1570, "sum": 73300,
        "under_par": 637, "locked_cents": 5253,
        "frontier": {"LE_93": 120, "LE_95": 183, "LE_97": 345, "LT_100": 637},
    },
}


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_record(path: Path, label: str | None = None, display_path: str | None = None) -> dict[str, Any]:
    return {"label": label or path.name, "path": display_path or path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def write_json(path: Path, obj: Any) -> None:
    path.write_text(canonical_json(obj), encoding="utf-8", newline="\n")


def write_jsonl_gz(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            for row in rows:
                gz.write((json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode())


def parse_epoch(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def percentile(values: list[int], q: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(q * len(ordered)) - 1)
    return ordered[index]


def distribution(values: list[int]) -> dict[str, Any]:
    return {
        "n": len(values),
        "sum": sum(values),
        "min": min(values) if values else None,
        "p25": percentile(values, 0.25),
        "median": percentile(values, 0.50),
        "p75": percentile(values, 0.75),
        "p90": percentile(values, 0.90),
        "max": max(values) if values else None,
    }


def channel_counts(by_event: dict[str, list[int | None]]) -> dict[str, int]:
    out = {"both": 0, "one": 0, "none": 0, "legs": 0, "sum": 0}
    for vals in by_event.values():
        n = sum(v is not None for v in vals)
        out[("none", "one", "both")[n]] += 1
        out["legs"] += n
        out["sum"] += sum(v for v in vals if v is not None)
    return out


def union_metrics(by_event: dict[str, list[int | None]]) -> dict[str, Any]:
    out: dict[str, Any] = channel_counts(by_event)
    out.update({"under_par": 0, "locked_cents": 0, "frontier": {"LE_93": 0, "LE_95": 0, "LE_97": 0, "LT_100": 0}})
    for vals in by_event.values():
        if any(v is None for v in vals):
            continue
        cost = int(sum(vals))
        if cost < 100:
            out["under_par"] += 1
            out["locked_cents"] += 100 - cost
            for tier in (93, 95, 97):
                if cost <= tier:
                    out["frontier"][f"LE_{tier}"] += 1
            out["frontier"]["LT_100"] += 1
    return out


class ConcatenatedParts(io.RawIOBase):
    def __init__(self, paths: list[Path]):
        self.paths = paths
        self.index = -1
        self.current: io.BufferedReader | None = None
        self._advance()

    def readable(self) -> bool:
        return True

    def _advance(self) -> None:
        if self.current:
            self.current.close()
        self.index += 1
        self.current = self.paths[self.index].open("rb") if self.index < len(self.paths) else None

    def readinto(self, b: bytearray) -> int:
        view = memoryview(b)
        total = 0
        while total < len(view) and self.current is not None:
            n = self.current.readinto(view[total:])
            if n:
                total += n
            else:
                self._advance()
        return total

    def close(self) -> None:
        if self.current:
            self.current.close()
        super().close()


def trace_at_reach(v36_package: Path, targets: dict[str, float]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    parts_manifest = json.loads((v36_package / "FULL_DECISION_TRACE_PARTS.json").read_text(encoding="utf-8"))
    part_paths = [v36_package / row["name"] for row in parts_manifest["parts"]]
    for path, row in zip(part_paths, parts_manifest["parts"]):
        if path.stat().st_size != row["bytes"] or sha256_file(path) != row["sha256"]:
            raise RuntimeError(f"full trace part identity mismatch: {path}")
    snapshots: dict[str, dict[str, Any]] = {}
    parsed = 0
    relevant = 0
    raw = ConcatenatedParts(part_paths)
    buffered = io.BufferedReader(raw, buffer_size=1024 * 1024)
    with gzip.GzipFile(fileobj=buffered, mode="rb") as gz:
        for encoded in gz:
            parsed += 1
            row = json.loads(encoded)
            ticker = row["ticker"]
            target = targets.get(ticker)
            if target is None or float(row["timestamp_epoch"]) > target:
                continue
            relevant += 1
            previous = snapshots.get(ticker)
            if previous is None or (row["timestamp_epoch"], row["ordinal"]) >= (previous["timestamp_epoch"], previous["ordinal"]):
                snapshots[ticker] = {
                    "timestamp_epoch": row["timestamp_epoch"],
                    "receipt": row["receipt"],
                    "ordinal": row["ordinal"],
                    "combined_state": row["combined_state"],
                    "quote_path_state": row["quote_path"]["state"],
                    "pressure_state": row["pressure_state"],
                    "observation": row["observation"],
                    "pair_cap_cents": row["pair_cap_cents"],
                    "order_before_cents": row["order_before_cents"],
                    "order_after_cents": row["order_after_cents"],
                    "decision_action": row["decision"]["action"],
                    "decision_reason": row["decision"]["reason"],
                }
    return snapshots, {"rows_parsed": parsed, "target_rows_seen": relevant, "targets": len(targets), "targets_with_snapshot": len(snapshots)}


def issue_owner(row: dict[str, Any], reach: dict[str, Any], snapshot: dict[str, Any] | None) -> tuple[str, str, int | None]:
    entry = row["entry_cents"]
    level = reach["union_reach_cents"]
    if entry is not None and entry > level:
        if "TAKER" in (row.get("fill_class") or ""):
            return "TAKE_FIRED_ABOVE_REACH", "V36 credited a take above the answer-key level", entry - level
        return "REST_PLACED_OFF_REACH_LEVEL", "V36's credited resting level was shallower than reach", entry - level
    if entry is not None:
        raise RuntimeError("issue_owner called for a non-issue credited row")
    if row["decision_count"] == 0:
        return "ADMISSION_NO_TWO_SIDED_BOOK", "no own two-sided-book decision existed inside V36's bound window", None
    rest = snapshot.get("order_after_cents") if snapshot else None
    cap = snapshot.get("pair_cap_cents") if snapshot else None
    if cap is not None and level > cap:
        return "PAIR_CAP_ARITHMETIC", f"reach {level} exceeded contemporaneous cap {cap}", level - cap
    if rest is not None and rest >= level:
        return "FILL_MODEL_SEAM_NOT_V36_ORGAN", "V36 rest was at/above union reach, but strict build-verification evidence did not credit it", 0
    if reach["leg_direction"] == "CLIMBING":
        gap = level - rest if rest is not None and rest < level else None
        return "DIVOT_CLASS_NOT_IMPLEMENTED", "riser rest was not resident at its answer-key divot floor", gap
    gap = level - rest if rest is not None and rest < level else None
    state = snapshot.get("combined_state") if snapshot else "NO_SNAPSHOT"
    return "REST_PLACED_OFF_REACH_LEVEL", f"rest was below reach while state={state}", gap


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v36-root", required=True, type=Path)
    ap.add_argument("--reach-root", required=True, type=Path)
    ap.add_argument("--private-root", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise SystemExit(f"output already exists: {out}")
    out.mkdir(parents=True)

    v36_package = args.v36_root.resolve() / V36_PACKAGE_REL
    quote_path = args.reach_root.resolve() / QUOTE_REL
    reach_summary_path = args.reach_root.resolve() / REACH_SUMMARY_REL
    reconciliation_path = args.reach_root.resolve() / RECONCILIATION_REL
    prints_path = args.private_root.resolve() / "fit-local/prints.jsonl"
    v36_trace_path = v36_package / "STRICT_DECISION_TRACE_1608.json"
    v36_score_path = v36_package / "SCORECARD_TWO_COLUMN.json"
    for p in (quote_path, reach_summary_path, reconciliation_path, prints_path, v36_trace_path, v36_score_path):
        if not p.is_file():
            raise RuntimeError(f"missing frozen input: {p}")

    def git_head(root: Path) -> str:
        return subprocess.run(["git", "-C", str(root.resolve()), "rev-parse", "HEAD"], check=True, text=True, capture_output=True).stdout.strip()
    if git_head(args.v36_root) != V36_COMMIT or git_head(args.reach_root) != REACH_COMMIT:
        raise RuntimeError("frozen input worktree commit mismatch")

    quote = json.loads(quote_path.read_text(encoding="utf-8"))
    reach_summary = json.loads(reach_summary_path.read_text(encoding="utf-8"))
    reconciliation = json.loads(reconciliation_path.read_text(encoding="utf-8"))
    strict_trace_doc = json.loads(v36_trace_path.read_text(encoding="utf-8"))
    strict_score_doc = json.loads(v36_score_path.read_text(encoding="utf-8"))
    strict_rows = strict_trace_doc["rows"]
    strict_by_ticker = {row["ticker"]: row for row in strict_rows}
    if len(strict_rows) != 1608 or len(strict_by_ticker) != 1608 or len(quote["events"]) != 804:
        raise RuntimeError("V36/reach population conservation failed")
    if strict_score_doc["STRICT_LAW"]["aggregate"]["credited_legs"] != 1035 or strict_score_doc["STRICT_LAW"]["aggregate"]["completed_pairs"] != 270:
        raise RuntimeError("frozen V36 STRICT scorecard identity changed")

    bounds: dict[str, tuple[str, float, float]] = {}
    leg_meta: dict[str, dict[str, Any]] = {}
    events_by_id: dict[str, dict[str, Any]] = {}
    for event in quote["events"]:
        events_by_id[event["event_id"]] = event
        for leg_id, leg in event["legs"].items():
            bounds[leg["ticker"]] = (event["event_id"], float(event["left_ts"]), float(event["right_ts"]))
            leg_meta[leg["ticker"]] = {"leg_id": leg_id, **leg}
    if set(bounds) != set(strict_by_ticker):
        raise RuntimeError("ticker identity mismatch between V36 and reach population")

    minima: dict[str, dict[str, Any]] = {ticker: {"count": 0, "low": None, "first_low": None} for ticker in bounds}
    print_hash = hashlib.sha256()
    all_print_rows = accepted_print_rows = 0
    accepted_by_event = Counter()
    with prints_path.open("rb") as raw:
        for encoded in raw:
            print_hash.update(encoded)
            all_print_rows += 1
            row = json.loads(encoded)
            ticker = row.get("ticker")
            bound = bounds.get(ticker)
            if not bound or not row.get("true_print"):
                continue
            epoch = parse_epoch(row["exchange_ts"])
            if not (bound[1] <= epoch < bound[2] + 1.0):
                continue
            accepted_print_rows += 1
            accepted_by_event[bound[0]] += 1
            price = int(row["price_cents"])
            target = minima[ticker]
            target["count"] += 1
            evidence = {
                "timestamp_epoch": epoch,
                "trade_id": row["trade_id"],
                "receipt_id": row.get("receipt_id"),
                "price_cents": price,
                "size": row.get("size"),
                "taker_book_side": row.get("taker_book_side"),
                "aggressor_side": "SELLER" if row.get("taker_book_side") == "bid" else "BUYER" if row.get("taker_book_side") == "ask" else "UNKNOWN",
            }
            if target["low"] is None or price < target["low"]:
                target["low"] = price
                target["first_low"] = evidence
            elif price == target["low"] and epoch < target["first_low"]["timestamp_epoch"]:
                target["first_low"] = evidence

    if accepted_print_rows != EXPECTED_REACH["print_rows"]:
        raise RuntimeError(f"print conservation mismatch: {accepted_print_rows}")
    seal_counts = {row["event"]: row["ours"] for row in reconciliation["per_game"]}
    mismatches = [event for event in sorted(events_by_id) if accepted_by_event[event] != seal_counts[event]]
    if mismatches:
        raise RuntimeError(f"per-event print reconciliation mismatch: {mismatches[:5]}")

    reach_leg_rows: list[dict[str, Any]] = []
    channel_trade: dict[str, list[int | None]] = {}
    channel_quote: dict[str, list[int | None]] = {}
    channel_union: dict[str, list[int | None]] = {}
    reach_by_ticker: dict[str, dict[str, Any]] = {}
    reach_targets: dict[str, float] = {}
    for event in quote["events"]:
        trade_vals: list[int | None] = []
        quote_vals: list[int | None] = []
        union_vals: list[int | None] = []
        for leg_id, leg in sorted(event["legs"].items()):
            q10 = leg.get("quote_touch_floors", {}).get("10")
            qv = q10.get("resting_bid_limit_cents") if q10 else None
            if q10 and not (q10["first_qualifying_span"]["min_ask_cents"] <= qv <= q10["first_qualifying_span"]["max_ask_cents"]):
                raise RuntimeError(f"quote floor falls outside its qualifying span: {leg['ticker']}")
            tv = minima[leg["ticker"]]["low"]
            uv = min(v for v in (qv, tv) if v is not None) if qv is not None or tv is not None else None
            sources = []
            evidence_candidates = []
            if uv is not None and tv == uv:
                sources.append("TRADED_AT_LEVEL")
                evidence_candidates.append(minima[leg["ticker"]]["first_low"])
            quote_evidence = None
            if uv is not None and qv == uv:
                sources.append("QUOTE_TOUCH_10S")
                span = q10["first_qualifying_span"]
                quote_evidence = {
                    "timestamp_epoch": float(span["start_ts"]) + 10.0,
                    "span_start_epoch": span["start_ts"], "span_end_epoch": span["end_ts"],
                    "dwell_threshold_seconds": 10, "min_ask_cents": span["min_ask_cents"],
                    "max_ask_cents": span["max_ask_cents"], "state_count": span["state_count"],
                }
                evidence_candidates.append(quote_evidence)
            evidence_candidates = [x for x in evidence_candidates if x is not None]
            evidence_epoch = min(x["timestamp_epoch"] for x in evidence_candidates) if evidence_candidates else None
            row = {
                "event_id": event["event_id"], "category": event["category"],
                "leg_id": leg_id, "ticker": leg["ticker"], "leg_identity": f"{event['event_id']}|{leg_id}",
                "leg_direction": leg["leg_direction"],
                "reach_left_epoch": event["left_ts"], "reach_right_epoch": event["right_ts"],
                "quote_touch_10_cents": qv, "quote_touch_evidence": quote_evidence,
                "traded_at_level_cents": tv, "traded_at_level_evidence": minima[leg["ticker"]]["first_low"],
                "union_reach_cents": uv, "union_sources": sources,
                "union_first_evidence_timestamp_epoch": evidence_epoch,
            }
            reach_leg_rows.append(row)
            reach_by_ticker[leg["ticker"]] = row
            if evidence_epoch is not None:
                reach_targets[leg["ticker"]] = evidence_epoch
            trade_vals.append(tv); quote_vals.append(qv); union_vals.append(uv)
        channel_trade[event["event_id"]] = trade_vals
        channel_quote[event["event_id"]] = quote_vals
        channel_union[event["event_id"]] = union_vals

    reconstructed = {"trade": channel_counts(channel_trade), "quote": channel_counts(channel_quote), "union": union_metrics(channel_union)}
    if reconstructed != {"trade": EXPECTED_REACH["trade"], "quote": EXPECTED_REACH["quote"], "union": EXPECTED_REACH["union"]}:
        raise RuntimeError(f"57daf3c1 reconstruction mismatch: {reconstructed}")

    expected_union = reach_summary["channels"]["UNION"]
    if expected_union["games"] != {"both": 785, "one": 0, "none": 19} or expected_union["under_par"] != 637:
        raise RuntimeError("controlling reach summary changed")

    snapshots, snapshot_receipt = trace_at_reach(v36_package, reach_targets)

    leg_rows: list[dict[str, Any]] = []
    game_rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    class_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    cell_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    scope_mismatch_rows: list[dict[str, Any]] = []

    for event in quote["events"]:
        traces = []
        reach_rows = []
        event_leg_rows = []
        for leg_id, leg in sorted(event["legs"].items()):
            ticker = leg["ticker"]
            v = strict_by_ticker[ticker]
            rr = reach_by_ticker[ticker]
            snapshot = snapshots.get(ticker)
            credited = v["entry_cents"] is not None
            has_reach = rr["union_reach_cents"] is not None
            issue = None
            if has_reach and (not credited or v["entry_cents"] > rr["union_reach_cents"]):
                owner, rationale, damage = issue_owner(v, rr, snapshot)
                issue = {
                    "owner": owner, "rationale": rationale, "measured_damage_cents": damage,
                    "issue_kind": "SHALLOW" if credited else "MISSING",
                }
            final_snapshot = v.get("last_decision")
            leg_row = {
                **{k: rr[k] for k in rr},
                "price_region": v["price_region"], "bell_confidence": v["bell_confidence"],
                "v36_left_epoch": v["w1_left_epoch"], "v36_right_epoch": v["w1_right_epoch"],
                "v36_decision_count": v["decision_count"], "v36_credited": credited,
                "v36_entry_cents": v["entry_cents"], "v36_fill_class": v["fill_class"],
                "v36_terminal_reason": v["terminal_reason"], "v36_final_state": v["final_state"],
                "v36_shallow_gap_cents": max(0, v["entry_cents"] - rr["union_reach_cents"]) if credited and has_reach else None,
                "v36_at_or_better_than_reach": v["entry_cents"] <= rr["union_reach_cents"] if credited and has_reach else None,
                "reach_moment_snapshot": snapshot,
                "terminal_snapshot": {
                    "timestamp_epoch": final_snapshot["timestamp_epoch"],
                    "combined_state": final_snapshot["combined_state"],
                    "quote_path_state": final_snapshot["quote_path"]["state"],
                    "pressure_state": final_snapshot["pressure_state"],
                    "order_after_cents": final_snapshot["order_after_cents"],
                    "pair_cap_cents": final_snapshot["pair_cap_cents"],
                    "decision_action": final_snapshot["decision"]["action"],
                    "decision_reason": final_snapshot["decision"]["reason"],
                } if final_snapshot else None,
                "layer_bind": issue,
            }
            if issue:
                issues.append({"event_id": event["event_id"], "ticker": ticker, "leg_id": leg_id, "category": event["category"], "bell_confidence": v["bell_confidence"], "price_region": v["price_region"], "reach_cents": rr["union_reach_cents"], "entry_cents": v["entry_cents"], "snapshot": snapshot, **issue})
            leg_rows.append(leg_row); event_leg_rows.append(leg_row); traces.append(v); reach_rows.append(rr)

        reach_count = sum(r["union_reach_cents"] is not None for r in reach_rows)
        credited_count = sum(t["entry_cents"] is not None for t in traces)
        if reach_count == 0:
            grade_class = "NO_REACH"
        elif reach_count != 2:
            raise RuntimeError(f"union answer key violates both-or-none conservation: {event['event_id']}")
        elif credited_count == 2:
            grade_class = "MATCHED" if all(t["entry_cents"] <= r["union_reach_cents"] for t, r in zip(traces, reach_rows)) else "SHALLOW"
        elif credited_count == 1:
            grade_class = "ONE_MISSING"
        else:
            grade_class = "BOTH_MISSING"
        game = {
            "event_id": event["event_id"], "category": event["category"],
            "starting_price_split": traces[0]["first_decision"]["starting_price_split"] if traces[0].get("first_decision") else traces[1]["first_decision"]["starting_price_split"] if traces[1].get("first_decision") else None,
            "bell_confidence": traces[0]["bell_confidence"], "grade_class": grade_class,
            "reach_combined_cents": sum(r["union_reach_cents"] for r in reach_rows) if reach_count == 2 else None,
            "reach_under_par": sum(r["union_reach_cents"] for r in reach_rows) < 100 if reach_count == 2 else None,
            "v36_credited_legs": credited_count,
            "v36_completed": credited_count == 2,
            "v36_combined_entry_cents": sum(t["entry_cents"] for t in traces) if credited_count == 2 else None,
            "v36_shallow_gap_cents": sum(l["v36_shallow_gap_cents"] or 0 for l in event_leg_rows),
            "missing_sides": [{"leg_id": l["leg_id"], "ticker": l["ticker"], "reach_cents": l["union_reach_cents"], "reach_evidence_timestamp_epoch": l["union_first_evidence_timestamp_epoch"], "reach_moment_snapshot": l["reach_moment_snapshot"], "terminal_state": l["v36_final_state"], "terminal_snapshot": l["terminal_snapshot"], "owner": l["layer_bind"]["owner"] if l["layer_bind"] else None} for l in event_leg_rows if l["union_reach_cents"] is not None and not l["v36_credited"]],
            "legs": [{"leg_id": l["leg_id"], "ticker": l["ticker"], "reach_cents": l["union_reach_cents"], "entry_cents": l["v36_entry_cents"], "gap_cents": l["v36_shallow_gap_cents"], "owner": l["layer_bind"]["owner"] if l["layer_bind"] else None} for l in event_leg_rows],
        }
        if grade_class == "NO_REACH" and game["v36_completed"]:
            scope_mismatch_rows.append({"event_id": event["event_id"], "category": event["category"], "bell_confidence": traces[0]["bell_confidence"], "reach_window": {"left": event["left_ts"], "right": event["right_ts"]}, "v36_window": {"left": traces[0]["w1_left_epoch"], "right": traces[0]["w1_right_epoch"]}, "v36_entries": {t["leg_identity"]: t["entry_cents"] for t in traces}})
        for leg_row in event_leg_rows:
            leg_row["game_grade_class"] = grade_class
        game_rows.append(game); class_groups[grade_class].append(game); cell_groups[(event["category"], traces[0]["bell_confidence"], grade_class)].append(game)

    expected_classes = {"MATCHED": 52, "SHALLOW": 212, "ONE_MISSING": 486, "BOTH_MISSING": 35, "NO_REACH": 19}
    actual_classes = {key: len(class_groups[key]) for key in expected_classes}
    if actual_classes != expected_classes:
        raise RuntimeError(f"grade class conservation changed: {actual_classes}")

    class_summary = {
        "schema_version": "v36-gap-to-union-reach-grade-v1",
        "definition": {
            "MATCHED": "V36 credited both legs and each entry was at-or-better than its 57daf3c1 union reach",
            "SHALLOW": "V36 credited both legs but at least one entry was above union reach",
            "ONE_MISSING": "the union answer key had both levels and V36 credited exactly one leg",
            "BOTH_MISSING": "the union answer key had both levels and V36 credited neither leg",
            "NO_REACH": "the 57daf3c1 union answer key had no level on either leg; no grade inferred",
        },
        "aggregate": {},
        "conservation": {"games": len(game_rows), "class_sum": sum(actual_classes.values()), "pass": len(game_rows) == sum(actual_classes.values()) == 804},
    }
    for key in expected_classes:
        rows = class_groups[key]
        game_gaps = [g["v36_shallow_gap_cents"] for g in rows if g["v36_shallow_gap_cents"] > 0]
        leg_gaps = [l["v36_shallow_gap_cents"] for l in leg_rows if l["game_grade_class"] == key and l["v36_shallow_gap_cents"] is not None and l["v36_shallow_gap_cents"] > 0]
        class_summary["aggregate"][key] = {
            "games": len(rows), "v36_completed_games": sum(g["v36_completed"] for g in rows),
            "missing_sides": sum(len(g["missing_sides"]) for g in rows),
            "shallow_gap_cents_per_leg": distribution(leg_gaps),
            "shallow_gap_cents_per_game": distribution(game_gaps),
        }

    cell_rows = []
    for (category, bell, grade_class), rows in sorted(cell_groups.items()):
        event_ids = {g["event_id"] for g in rows}
        leg_gaps = [l["v36_shallow_gap_cents"] for l in leg_rows if l["event_id"] in event_ids and l["v36_shallow_gap_cents"] is not None and l["v36_shallow_gap_cents"] > 0]
        game_gaps = [g["v36_shallow_gap_cents"] for g in rows if g["v36_shallow_gap_cents"] > 0]
        cell_rows.append({"category": category, "bell_confidence": bell, "grade_class": grade_class, "games": len(rows), "v36_completed_games": sum(g["v36_completed"] for g in rows), "missing_sides": sum(len(g["missing_sides"]) for g in rows), "shallow_gap_cents_per_leg": distribution(leg_gaps), "shallow_gap_cents_per_game": distribution(game_gaps)})

    coarse: dict[str, dict[str, Any]] = {}
    detailed: dict[tuple[str, str], dict[str, Any]] = {}
    for issue in issues:
        owner = issue["owner"]
        row = coarse.setdefault(owner, {"organ": owner, "issue_sides": 0, "games": set(), "measured_damage_cents": 0, "unpriced_issue_sides": 0, "shallow_sides": 0, "missing_sides": 0})
        row["issue_sides"] += 1; row["games"].add(issue["event_id"]); row["shallow_sides"] += issue["issue_kind"] == "SHALLOW"; row["missing_sides"] += issue["issue_kind"] == "MISSING"
        if issue["measured_damage_cents"] is None: row["unpriced_issue_sides"] += 1
        else: row["measured_damage_cents"] += issue["measured_damage_cents"]
        state = issue["snapshot"]["combined_state"] if issue.get("snapshot") else "NO_SNAPSHOT"
        d = detailed.setdefault((owner, state), {"organ": owner, "state_at_reach": state, "issue_sides": 0, "games": set(), "measured_damage_cents": 0, "unpriced_issue_sides": 0})
        d["issue_sides"] += 1; d["games"].add(issue["event_id"])
        if issue["measured_damage_cents"] is None: d["unpriced_issue_sides"] += 1
        else: d["measured_damage_cents"] += issue["measured_damage_cents"]
    def freeze_rank(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        frozen=[]
        for row in rows:
            row=dict(row);row["games"]=len(row["games"]);frozen.append(row)
        return sorted(frozen, key=lambda r: (-r["measured_damage_cents"], -r["games"], r["organ"], r.get("state_at_reach", "")))
    layer_ranking = {
        "damage_definition": "SHALLOW: entry minus reach. MISSING: positive cents that contemporaneous rest/cap sat below reach. No fabricated penalty is assigned where no comparable price exists; those sides remain unpriced_issue_sides.",
        "coarse_organ_ranking": freeze_rank(coarse.values()),
        "organ_x_state_ranking": freeze_rank(detailed.values()),
        "issue_conservation": {"issue_sides": len(issues), "shallow_sides": sum(i["issue_kind"] == "SHALLOW" for i in issues), "missing_sides": sum(i["issue_kind"] == "MISSING" for i in issues)},
    }

    reach_receipt = {
        "schema_version": "57daf3c1-union-reach-reconstruction-v1", "controlling_commit": REACH_COMMIT,
        "law": "per-leg union reach = min(10-second quote-touch floor, lowest lawful true trade in the whole-second-inclusive reach interval)",
        "prints": {"all_private_rows_scanned": all_print_rows, "accepted_rows": accepted_print_rows, "sha256": print_hash.hexdigest(), "per_event_reconciliation_mismatches": []},
        "reconstructed": reconstructed, "expected": EXPECTED_REACH, "exact_match": True,
        "named_rows_checked_by_controlling_artifact": sorted(reach_summary["named_rows"]),
    }
    boundary_receipt = {
        "finding": "57daf3c1 reach and bfde0d8 V36 bind different window edges on some games; NO_REACH remains ungradeable rather than coerced",
        "no_reach_games": 19, "no_reach_v36_completed_games": len(scope_mismatch_rows), "rows": scope_mismatch_rows,
    }
    forbidden = {"network_access": False, "live_access": False, "holdout_access": False, "orders_positions_exits_mutated": False, "policy_or_replay_invoked": False, "scoring_change": False, "statement": "Only frozen local dev artifacts and the hash-bound private print ledger were read."}

    write_jsonl_gz(out / "UNION_REACH_LEG_LEDGER.jsonl.gz", sorted(reach_leg_rows, key=lambda r: (r["event_id"], r["leg_id"])))
    write_jsonl_gz(out / "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz", sorted(leg_rows, key=lambda r: (r["event_id"], r["leg_id"])))
    write_jsonl_gz(out / "V36_GAP_TO_REACH_GAME_LEDGER.jsonl.gz", sorted(game_rows, key=lambda r: r["event_id"]))
    write_jsonl_gz(out / "LAYER_BIND_ISSUE_LEDGER.jsonl.gz", sorted(issues, key=lambda r: (r["event_id"], r["leg_id"])))
    write_json(out / "CLASS_SUMMARY.json", class_summary)
    write_json(out / "CATEGORY_X_BELL_CONFIDENCE_SUMMARY.json", {"rows": cell_rows, "conservation": {"games": sum(r["games"] for r in cell_rows), "expected": 804, "pass": sum(r["games"] for r in cell_rows) == 804}})
    write_json(out / "LAYER_BIND_RANKING.json", layer_ranking)
    write_json(out / "REACH_RECONSTRUCTION_RECEIPT.json", reach_receipt)
    write_json(out / "BOUNDARY_SCOPE_DIAGNOSTIC.json", boundary_receipt)
    write_json(out / "FORBIDDEN_ACCESS_RECEIPT.json", forbidden)
    write_json(out / "TRACE_AT_REACH_RECEIPT.json", snapshot_receipt)

    source_manifest = {
        "commits": {"V36": V36_COMMIT, "UNION_REACH": REACH_COMMIT},
        "files": [
            hash_record(v36_trace_path, "V36_STRICT_DECISION_TRACE_1608", f"{V36_COMMIT}:{V36_PACKAGE_REL.as_posix()}/STRICT_DECISION_TRACE_1608.json"),
            hash_record(v36_score_path, "V36_SCORECARD_TWO_COLUMN", f"{V36_COMMIT}:{V36_PACKAGE_REL.as_posix()}/SCORECARD_TWO_COLUMN.json"),
            hash_record(v36_package / "FULL_DECISION_TRACE_PARTS.json", "V36_FULL_TRACE_PARTS_MANIFEST", f"{V36_COMMIT}:{V36_PACKAGE_REL.as_posix()}/FULL_DECISION_TRACE_PARTS.json"),
            hash_record(quote_path, "QUOTE_TOUCH_CENSUS", f"{REACH_COMMIT}:{QUOTE_REL.as_posix()}"),
            hash_record(reach_summary_path, "MAKER_RESULTS_THREE_CHANNELS", f"{REACH_COMMIT}:{REACH_SUMMARY_REL.as_posix()}"),
            hash_record(reconciliation_path, "RECONCILIATION_SEAL_804", f"{REACH_COMMIT}:{RECONCILIATION_REL.as_posix()}"),
            {"label": "PRIVATE_PRINTS", "path": "PRIVATE:fit-local/prints.jsonl", "bytes": prints_path.stat().st_size, "sha256": print_hash.hexdigest()},
        ],
    }
    write_json(out / "SOURCE_HASH_MANIFEST.json", source_manifest)

    report = f"""# V36 gap to 57daf3c1 union reach

Read-only grade of frozen V36 STRICT output `{V36_COMMIT}` against the reconstructed, aggregate-exact union maker reach at `{REACH_COMMIT}`.

## Game classes

| class | games | V36 completed | missing sides | measured shallow gap cents |
|---|---:|---:|---:|---:|
"""
    for key in ("MATCHED", "SHALLOW", "ONE_MISSING", "BOTH_MISSING", "NO_REACH"):
        s = class_summary["aggregate"][key]
        report += f"| {key} | {s['games']} | {s['v36_completed_games']} | {s['missing_sides']} | {s['shallow_gap_cents_per_leg']['sum']} |\n"
    report += "\n## Layer bind, ranked by measured cents\n\n| owner | games | issue sides | measured cents | unpriced sides |\n|---|---:|---:|---:|---:|\n"
    for row in layer_ranking["coarse_organ_ranking"]:
        report += f"| {row['organ']} | {row['games']} | {row['issue_sides']} | {row['measured_damage_cents']} | {row['unpriced_issue_sides']} |\n"
    report += f"\nThe answer key reproduces 373,203 prints; 785/0/19 union availability; 637 under-par games; frontier 120/183/345/637; 5,253 cents locked. Six of the 19 NO_REACH games are V36-complete under bfde0d8's different window edge and remain ungradeable, never coerced.\n"
    (out / "REPORT.md").write_text(report, encoding="utf-8", newline="\n")

    artifact_files = sorted(p for p in out.iterdir() if p.is_file() and p.name != "ARTIFACT_HASH_MANIFEST.json")
    write_json(out / "ARTIFACT_HASH_MANIFEST.json", {"files": [hash_record(p, p.name) for p in artifact_files]})


if __name__ == "__main__":
    main()
