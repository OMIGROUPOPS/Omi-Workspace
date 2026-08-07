#!/usr/bin/env python3
"""Build six read-only V36 exemplar packs from frozen traces and certified tapes.

This builder does not import or invoke policy code. It extracts the already-frozen
STRICT_LAW decisions at bfde0d8 and joins them to the exact BBO and print sources
hash-bound by that package.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83"
V36_PACKAGE = Path(".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806")
TEMPLATE_COMMIT = "1fd0328231dcff8bf03e470153deb26b84168e26"
PRINTS_SHA256 = "e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55"
PRINTS_BYTES = 1766090446
ET = ZoneInfo("America/New_York")

SELECTION = [
    {
        "short": "ARNROM",
        "event_id": "KXATPCHALLENGERMATCH-26JUL12ARNROM",
        "role": "LIVING_REST_PLUS_EVIDENCE_TAKE",
        "why": "Named V36 regression: ROM 38 plus ARN 56 equals 94 under par.",
    },
    {
        "short": "KIRSEK",
        "event_id": "KXATPCHALLENGERMATCH-26JUL14KIRSEK",
        "role": "DEEPEST_CLEAN_MAKER_FILL",
        "why": "Exact-bell, both-maker completion; KIR rests and fills at its exact 15-cent print floor, 18 cents below its own close telemetry.",
    },
    {
        "short": "DAHBAE",
        "event_id": "KXATPMATCH-26JUL12DAHBAE",
        "role": "WIDE_SPREAD_MAKER_ONLY_COMPLETION",
        "why": "BOSCOP-class 88-cent formation spreads; both legs fill by strict seller-aggressed maker evidence and complete 93 plus 5 equals 98.",
    },
    {
        "short": "LAJVAN",
        "event_id": "KXATPMATCH-26JUL12LAJVAN",
        "role": "CARRIED_PAIR_HONEST_WART",
        "why": "Exact-bell under-par pair with LAJ four cents above its own close and VAN eight cents below; one side carries the other.",
    },
    {
        "short": "WESPAA",
        "event_id": "KXATPCHALLENGERMATCH-26JUL12WESPAA",
        "role": "REST_STARVED_LOSS",
        "why": "Exact-bell no-fill pair; WES stands at its 60-cent ask/print floor but no qualifying seller print pays the rest.",
    },
    {
        "short": "MATMOR",
        "event_id": "KXATPCHALLENGERMATCH-26JUL14MATMOR",
        "role": "SKIPPED_ENTIRELY",
        "why": "Neither expression forms an actionable two-sided book inside the frozen Window-1 span; both decision counts are zero.",
    },
]


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_gzip_jsonl(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


class ConcatenatedRaw(io.RawIOBase):
    def __init__(self, paths: list[Path]):
        self.paths = paths
        self.index = 0
        self.handle = self.paths[0].open("rb") if self.paths else None

    def readable(self):
        return True

    def readinto(self, buffer):
        while self.handle is not None:
            count = self.handle.readinto(buffer)
            if count:
                return count
            self.handle.close()
            self.index += 1
            self.handle = self.paths[self.index].open("rb") if self.index < len(self.paths) else None
        return 0

    def close(self):
        if self.handle is not None:
            self.handle.close()
            self.handle = None
        super().close()


def read_split_gzip_jsonl(package: Path, manifest_name: str):
    manifest = read_json(package / manifest_name)
    paths = []
    byte_sum = 0
    for part in manifest["parts"]:
        path = package / part["name"]
        require(path.stat().st_size == part["bytes"], f"part size mismatch {path}")
        require(sha256_file(path) == part["sha256"], f"part hash mismatch {path}")
        byte_sum += part["bytes"]
        paths.append(path)
    require(byte_sum == manifest["source_bytes"], f"part conservation failed {manifest_name}")
    raw = ConcatenatedRaw(paths)
    buffered = io.BufferedReader(raw, buffer_size=1024 * 1024)
    zipped = gzip.GzipFile(fileobj=buffered, mode="rb")
    text = io.TextIOWrapper(zipped, encoding="utf-8")
    try:
        for line in text:
            if line.strip():
                yield json.loads(line)
    finally:
        text.close()


def epoch_from_et(value: str) -> float | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
    except (TypeError, ValueError):
        return None


def et_string(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, ET).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def number(value: str | None):
    if value is None or value == "":
        return None
    try:
        result = float(value)
    except ValueError:
        return None
    return int(result) if result.is_integer() else result


def load_books(path: Path, ticker: str, left: float, right: float):
    rows = []
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        current_ask = None
        ask_since = None
        for ordinal, raw in enumerate(reader, 2):
            timestamp = epoch_from_et(raw.get("ts_et"))
            if timestamp is None:
                continue
            bids = []
            asks = []
            for level in range(1, 6):
                bid = number(raw.get(f"bid_{level}"))
                bid_size = number(raw.get(f"bid_{level}_sz"))
                ask = number(raw.get(f"ask_{level}"))
                ask_size = number(raw.get(f"ask_{level}_sz"))
                if isinstance(bid, int) and bid_size is not None and bid_size > 0:
                    bids.append((bid, bid_size))
                if isinstance(ask, int) and ask_size is not None and ask_size > 0:
                    asks.append((ask, ask_size))
            if not bids or not asks:
                continue
            bids.sort(reverse=True)
            asks.sort()
            best_ask = asks[0][0]
            if best_ask != current_ask:
                current_ask = best_ask
                ask_since = timestamp
            dwell = timestamp - ask_since
            if left <= timestamp <= right:
                bid_depth = sum(x[1] for x in bids)
                ask_depth = sum(x[1] for x in asks)
                rows.append({
                    "kind": "BBO",
                    "ticker": ticker,
                    "ts": timestamp,
                    "ordinal": ordinal,
                    "receipt": f"{ticker}.csv.gz#row-{ordinal}",
                    "bid": bids[0][0],
                    "bid_size": bids[0][1],
                    "ask": best_ask,
                    "ask_size": asks[0][1],
                    "spread": best_ask - bids[0][0],
                    "ask_dwell": dwell,
                    "bid_depth_5": bid_depth,
                    "ask_depth_5": ask_depth,
                    "depth_ratio": bid_depth / (bid_depth + ask_depth),
                    "last_trade": number(raw.get("last_trade")),
                })
    return rows


def run_print_spool(v36_repo: Path, private_root: Path, output: Path, bounds: dict[str, tuple[float, float]]):
    spool = output / ".print-spool"
    spool.mkdir()
    sources = output / ".print-spool-sources.csv"
    receipt = output / ".print-spool-receipt.json"
    with sources.open("w", encoding="utf-8", newline="") as handle:
        handle.write("ticker,left,right\n")
        for ticker in sorted(bounds):
            left, right = bounds[ticker]
            handle.write(f"{ticker},{left},{right}\n")
    subprocess.check_call([
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
        str(v36_repo / "arb-executor/analysis/window1_v32_print_spool.ps1"),
        "-Prints", str(private_root / "fit-local/prints.jsonl"),
        "-Sources", str(sources),
        "-Spool", str(spool),
        "-Receipt", str(receipt),
        "-SourceCode", str(v36_repo / "arb-executor/analysis/window1_v32_print_spool.cs"),
    ])
    sealed = read_json(receipt)
    require(sealed["sha256"] == PRINTS_SHA256, "certified print archive hash mismatch")
    require(sealed["bytes"] == PRINTS_BYTES, "certified print archive size mismatch")
    by_ticker = {}
    for ticker in sorted(bounds):
        path = spool / f"{ticker}.jsonl"
        rows = []
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                ts, ordinal, receipt_id, price, size, taker_side, trade_id = json.loads(line)
                rows.append({
                    "kind": "PRINT",
                    "ticker": ticker,
                    "ts": ts,
                    "ordinal": ordinal,
                    "receipt": receipt_id,
                    "price": price,
                    "size": size,
                    "taker_side": taker_side,
                    "trade_id": trade_id,
                })
        by_ticker[ticker] = rows
    sources.unlink()
    receipt.unlink()
    shutil.rmtree(spool)
    return by_ticker, sealed


def state_strips(decisions: list[dict]):
    strips = []
    for row in decisions:
        key = (
            row.get("combined_state"),
            (row.get("quote_path") or {}).get("state"),
            row.get("pressure_state"),
            bool(row.get("disagreement")),
        )
        if not strips or strips[-1]["key"] != key:
            strips.append({
                "key": key,
                "start_ts": row["timestamp_epoch"],
                "start_receipt": row["receipt"],
                "end_ts": row["timestamp_epoch"],
                "end_receipt": row["receipt"],
                "decision_rows": 0,
                "actions": Counter(),
                "start_observation": row.get("observation"),
                "end_observation": row.get("observation"),
                "order_start_cents": row.get("order_before_cents"),
                "order_end_cents": row.get("order_after_cents"),
                "layer_tags": ["MACRO_QUOTE_PATH", "PAIR_MICRO_PRESSURE", "MICRO_POSITION", "MICRO_MICRO_TIMING"],
            })
        strip = strips[-1]
        strip["end_ts"] = row["timestamp_epoch"]
        strip["end_receipt"] = row["receipt"]
        strip["end_observation"] = row.get("observation")
        strip["order_end_cents"] = row.get("order_after_cents")
        strip["decision_rows"] += 1
        strip["actions"][(row.get("decision") or {}).get("action", "NONE")] += 1
    out = []
    for strip in strips:
        combined, quote, pressure, disagreement = strip.pop("key")
        strip["combined_state"] = combined
        strip["quote_state"] = quote
        strip["pressure_state"] = pressure
        strip["disagreement"] = disagreement
        strip["duration_seconds"] = strip["end_ts"] - strip["start_ts"]
        strip["actions"] = dict(sorted(strip["actions"].items()))
        out.append(strip)
    return out


def build_marks(selection: dict, event: dict, decisions: list[dict], actions: list[dict], tape_hashes: dict, print_counts: dict):
    per_leg_decisions = defaultdict(list)
    per_leg_actions = defaultdict(list)
    for row in sorted(decisions, key=lambda x: (x["timestamp_epoch"], x.get("ordinal", 0), x["leg_identity"])):
        per_leg_decisions[row["leg_identity"]].append(row)
    for row in sorted(actions, key=lambda x: (x["timestamp_epoch"], x.get("receipt") or "", x["leg_identity"], x["kind"])):
        per_leg_actions[row["leg_identity"]].append(row)
    legs = {}
    for leg_id, leg in sorted(event["legs"].items()):
        identity = leg["leg_identity"]
        leg_decisions = per_leg_decisions[identity]
        leg_actions = per_leg_actions[identity]
        rest_walks = []
        for row in leg_decisions:
            decision = row.get("decision") or {}
            if decision.get("action") not in {"PLACE_REST", "REPRICE_REST"}:
                continue
            rest_walks.append({
                "timestamp_epoch": row["timestamp_epoch"],
                "timestamp_et": et_string(row["timestamp_epoch"]),
                "receipt": row["receipt"],
                "action": decision["action"],
                "from_cents": row.get("order_before_cents"),
                "to_cents": row.get("order_after_cents"),
                "reason": decision.get("reason"),
                "book": row.get("observation"),
                "combined_state": row.get("combined_state"),
                "quote_state": (row.get("quote_path") or {}).get("state"),
                "pressure_state": row.get("pressure_state"),
                "pair_cap_cents": row.get("pair_cap_cents"),
                "layer_tags": ["SOURCE_BOOK", "MACRO_QUOTE_PATH", "PAIR_MICRO_PRESSURE", "MICRO_POSITION_REST", "MICRO_MICRO_ACTION"],
            })
        pair_arms = [row for row in leg_actions if row["kind"] == "PAIR_ARM"]
        take_moments = [row for row in leg_actions if row["kind"] == "FILL" and "TAKER" in str(row.get("fill_class"))]
        maker_fills = [row for row in leg_actions if row["kind"] == "FILL" and "MAKER" in str(row.get("fill_class"))]
        legs[leg_id] = {
            "leg_identity": identity,
            "ticker": leg["ticker"],
            "frozen_result": {
                "acted": leg["acted"],
                "credited": leg["credited"],
                "entry_cents": leg["entry_cents"],
                "fill_class": leg["fill_class"],
                "fill_timestamp_epoch": leg["fill_timestamp_epoch"],
                "terminal_reason": leg["terminal_reason"],
                "qualifying_ask_floor_cents": leg["w1_qualifying_ask_floor_cents"],
                "print_backed_floor_cents": leg["w1_print_backed_achievable_floor_cents"],
                "close_telemetry_only_cents": leg["w1_close_telemetry"].get("price_cents"),
                "resting_target_at_hard_edge_cents": leg["resting_target_at_hard_edge_cents"],
            },
            "source": {
                "book": tape_hashes[leg["ticker"]],
                "certified_print_rows_inside_window": print_counts[leg["ticker"]],
                "v36_frozen_print_count_inside_window": leg["w1_true_print_count"],
            },
            "state_strip": state_strips(leg_decisions),
            "rest_walks": rest_walks,
            "pair_arms": pair_arms,
            "take_moments": take_moments,
            "maker_fill_moments": maker_fills,
            "all_frozen_action_marks": leg_actions,
            "conservation": {
                "frozen_decision_count": leg["decision_count"],
                "extracted_decision_count": len(leg_decisions),
                "pass": leg["decision_count"] == len(leg_decisions),
            },
        }
    return {
        "schema_version": "v36-evidence-decision-marks-v1",
        "selection": selection,
        "event_id": event["event_id"],
        "category": event["category"],
        "starting_price_split": event["starting_price_split"],
        "window": {
            "left_epoch": event["w1_left_epoch"],
            "right_epoch": event["w1_right_epoch"],
            "right_edge_source": event["edge_source_field"],
            "precision_class": event["bell_confidence"],
        },
        "layers_in_execution_order": [
            "SOURCE_BOOK_OR_PRINT",
            "MACRO_QUOTE_PATH",
            "PAIR_MICRO_PRESSURE",
            "MICRO_POSITION_EVIDENCE_FLOOR_OR_REST",
            "MICRO_MICRO_ACTION",
            "PAIR_CAP_ARM",
            "STRICT_FILL_PROOF",
        ],
        "legs": legs,
        "read_only_extraction": True,
        "policy_invocations": 0,
        "score_invocations": 0,
    }


def timeline_rows(event: dict, books: dict, prints: dict, decisions: list[dict], actions: list[dict], schedules: dict, bells: dict):
    decision_by_receipt = {row["receipt"]: row for row in decisions}
    actions_by_receipt = defaultdict(list)
    for row in actions:
        if row.get("receipt"):
            actions_by_receipt[row["receipt"]].append(row)
    rows = []
    for leg_id, leg in sorted(event["legs"].items()):
        for edge, timestamp in (("WINDOW_LEFT", event["w1_left_epoch"]), ("WINDOW_RIGHT", event["w1_right_epoch"])):
            rows.append({"kind": edge, "leg_id": leg_id, "ticker": leg["ticker"], "ts": timestamp, "ordinal": -1 if edge == "WINDOW_LEFT" else 10**15, "receipt": edge})
        rows.extend({**row, "leg_id": leg_id} for row in books[leg["ticker"]])
        rows.extend({**row, "leg_id": leg_id} for row in prints[leg["ticker"]])
    rows.sort(key=lambda x: (x["ts"], x["leg_id"], 0 if x["kind"] == "WINDOW_LEFT" else 1 if x["kind"] == "BBO" else 2 if x["kind"] == "PRINT" else 3, x["ordinal"]))
    state = {leg_id: {"order": None, "combined": None, "quote": None, "pressure": None, "credited": False, "cap": None} for leg_id in event["legs"]}
    output = []
    for row in rows:
        leg_id = row["leg_id"]
        current = state[leg_id]
        decision = decision_by_receipt.get(row["receipt"])
        if decision:
            current["order"] = decision.get("order_after_cents")
            current["combined"] = decision.get("combined_state")
            current["quote"] = (decision.get("quote_path") or {}).get("state")
            current["pressure"] = decision.get("pressure_state")
            current["cap"] = decision.get("pair_cap_cents")
        receipt_actions = actions_by_receipt.get(row["receipt"], [])
        for action in receipt_actions:
            if action["kind"] == "PAIR_ARM":
                current["cap"] = action["pair_cap_cents"]
                if isinstance(current["order"], int) and current["order"] > current["cap"]:
                    current["order"] = current["cap"] if 1 <= current["cap"] <= 99 else None
            if action["kind"] == "FILL":
                current["credited"] = True
                current["order"] = None
        scheduled = schedules.get(row["ticker"])
        bell = bells.get(event["event_id"])
        layer_tags = []
        if row["kind"] == "BBO":
            layer_tags.append("SOURCE_BOOK")
        elif row["kind"] == "PRINT":
            layer_tags.append("SOURCE_CERTIFIED_PRINT")
        else:
            layer_tags.append("WINDOW_BOUNDARY")
        if decision:
            layer_tags.extend(["MACRO_QUOTE_PATH", "PAIR_MICRO_PRESSURE", "MICRO_POSITION", "MICRO_MICRO_DECISION"])
        if receipt_actions:
            layer_tags.extend(sorted({"PAIR_CAP" if action["kind"] == "PAIR_ARM" else "STRICT_FILL" if action["kind"] == "FILL" else "REST_ACTION" for action in receipt_actions}))
        output.append({
            "ts_epoch": row["ts"],
            "ts_et": et_string(row["ts"]),
            "t_minus_scheduled_s": None if scheduled is None else scheduled - row["ts"],
            "t_minus_actual_bell_s": None if bell is None else bell - row["ts"],
            "t_minus_pre_match_boundary_s": event["w1_right_epoch"] - row["ts"],
            "leg": leg_id,
            "ticker": row["ticker"],
            "row_type": row["kind"],
            "best_bid": row.get("bid"),
            "bid_size": row.get("bid_size"),
            "best_ask": row.get("ask"),
            "ask_size": row.get("ask_size"),
            "spread": row.get("spread"),
            "ask_dwell_s": row.get("ask_dwell"),
            "bid_depth_5": row.get("bid_depth_5"),
            "ask_depth_5": row.get("ask_depth_5"),
            "depth_ratio": row.get("depth_ratio"),
            "last_traded": row.get("last_trade"),
            "print_price": row.get("price"),
            "print_size": row.get("size"),
            "taker_side": row.get("taker_side"),
            "trade_id": row.get("trade_id"),
            "receipt": row.get("receipt"),
            "resting_bid": current["order"],
            "combined_state": current["combined"],
            "quote_state": current["quote"],
            "pressure_state": current["pressure"],
            "pair_cap": current["cap"],
            "decision_action": None if not decision else (decision.get("decision") or {}).get("action"),
            "decision_reason": None if not decision else (decision.get("decision") or {}).get("reason"),
            "layer_tags": "+".join(dict.fromkeys(layer_tags)),
        })
    return output


def write_csv(path: Path, rows: list[dict]):
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def validate_selection(events: dict[str, dict]):
    arn = events["KXATPCHALLENGERMATCH-26JUL12ARNROM"]
    require(arn["legs"]["ARN"]["entry_cents"] == 56 and arn["legs"]["ROM"]["entry_cents"] == 38, "ARNROM regression mismatch")
    kir = events["KXATPCHALLENGERMATCH-26JUL14KIRSEK"]
    require(kir["legs"]["KIR"]["entry_cents"] == 15 and kir["legs"]["KIR"]["entry_minus_print_backed_floor_cents"] == 0, "KIRSEK maker mismatch")
    require(all("MAKER" in leg["fill_class"] for leg in kir["legs"].values()), "KIRSEK is not both-maker")
    dah = events["KXATPMATCH-26JUL12DAHBAE"]
    require(sum(leg["entry_cents"] for leg in dah["legs"].values()) == 98 and all("MAKER" in leg["fill_class"] for leg in dah["legs"].values()), "DAHBAE maker mismatch")
    laj = events["KXATPMATCH-26JUL12LAJVAN"]
    deltas = sorted(leg["entry_cents"] - leg["w1_close_telemetry"]["price_cents"] for leg in laj["legs"].values())
    require(deltas == [-8, 4], "LAJVAN carried mismatch")
    wes = events["KXATPCHALLENGERMATCH-26JUL12WESPAA"]
    require(not any(leg["credited"] for leg in wes["legs"].values()) and wes["legs"]["WES"]["resting_target_at_hard_edge_cents"] == 60, "WESPAA rest-starved mismatch")
    mat = events["KXATPCHALLENGERMATCH-26JUL14MATMOR"]
    require(sum(leg["decision_count"] for leg in mat["legs"].values()) == 0, "MATMOR skip mismatch")


def build(repo: Path, v36_repo: Path, private_root: Path, output: Path, compare: Path | None):
    require(git(v36_repo, "rev-parse", "HEAD") == V36_COMMIT, "V36 detached worktree HEAD mismatch")
    package = v36_repo / V36_PACKAGE
    source_manifest = read_json(package / "SOURCE_HASH_MANIFEST.json")
    policy_path = v36_repo / "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js"
    require(sha256_file(policy_path) == "5db3922d5749e11548bca0c301abec19da5e2dfb993ffc17a44ec90989e34f73", "V36 policy hash mismatch")
    require(output.name.lower().find("v36") >= 0, "unsafe output path")
    if output.exists():
        shutil.rmtree(output)
    (output / "exemplar_packs").mkdir(parents=True)

    selected_ids = {row["event_id"] for row in SELECTION}
    events = {row["event_id"]: row for row in read_gzip_jsonl(package / "STRICT_EVENT_LEDGER.jsonl.gz") if row["event_id"] in selected_ids}
    require(set(events) == selected_ids, "selected event missing from V36 strict ledger")
    validate_selection(events)

    decisions = defaultdict(list)
    for row in read_split_gzip_jsonl(package, "FULL_DECISION_TRACE_PARTS.json"):
        if row.get("mode") == "STRICT_LAW" and row.get("event_id") in selected_ids:
            decisions[row["event_id"]].append(row)
    actions = defaultdict(list)
    with gzip.open(package / "ACTION_AND_FILL_TRACE.jsonl.gz.part000", "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("mode") == "STRICT_LAW" and row.get("event_id") in selected_ids:
                actions[row["event_id"]].append(row)

    quote_path = v36_repo / ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv"
    with quote_path.open("r", encoding="utf-8-sig", newline="") as handle:
        schedules = {row["ticker"]: float(row["scheduled_start_ts"]) for row in csv.DictReader(handle)}
    bell_path = v36_repo / ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json"
    bells = {row["event_id"]: row.get("exact_bell_ts") for row in read_json(bell_path)["leg_rows"]}

    bounds = {}
    for event in events.values():
        for leg in event["legs"].values():
            bounds[leg["ticker"]] = (event["w1_left_epoch"], event["w1_right_epoch"])
    print_rows, print_receipt = run_print_spool(v36_repo, private_root, output, bounds)

    tape_hashes = {}
    books = {}
    for ticker, (left, right) in sorted(bounds.items()):
        tape = private_root / "fit-local/ticks" / f"{ticker}.csv.gz"
        expected = source_manifest["private_full_life_books"][ticker]
        actual = {"sha256": sha256_file(tape), "bytes": tape.stat().st_size}
        require(actual == expected, f"V36-bound tape mismatch {ticker}")
        tape_hashes[ticker] = actual
        books[ticker] = load_books(tape, ticker, left, right)

    pack_manifest = {}
    selection_rows = []
    for selection in SELECTION:
        event_id = selection["event_id"]
        event = events[event_id]
        print_counts = {ticker: len(print_rows[ticker]) for ticker in bounds if ticker.startswith(event_id + "-")}
        for leg in event["legs"].values():
            require(print_counts[leg["ticker"]] == leg["w1_true_print_count"], f"certified print count mismatch {leg['ticker']}")
        marks = build_marks(selection, event, decisions[event_id], actions[event_id], tape_hashes, print_counts)
        timeline = timeline_rows(event, books, print_rows, decisions[event_id], actions[event_id], schedules, bells)
        csv_name = f"{selection['short']}_DUAL_TIMELINE_V2.csv"
        json_name = f"{selection['short']}_DECISION_MARKS.json"
        write_csv(output / "exemplar_packs" / csv_name, timeline)
        (output / "exemplar_packs" / json_name).write_bytes(canonical(marks))
        entries = {leg_id: leg["entry_cents"] for leg_id, leg in sorted(event["legs"].items())}
        selection_rows.append({
            **selection,
            "category": event["category"],
            "bell_confidence": event["bell_confidence"],
            "entries_cents": entries,
            "combined_entry_cents": sum(x for x in entries.values() if isinstance(x, int)) if all(isinstance(x, int) for x in entries.values()) else None,
            "timeline_rows": len(timeline),
            "decision_rows": len(decisions[event_id]),
            "action_and_fill_rows": len(actions[event_id]),
        })
        pack_manifest[selection["short"]] = {"timeline": csv_name, "marks": json_name}

    (output / "EVIDENCE_SELECTION.json").write_bytes(canonical({
        "schema_version": "stage-c-v36-evidence-selection-v1",
        "source_commit": V36_COMMIT,
        "standing_template_commit": TEMPLATE_COMMIT,
        "games": selection_rows,
        "count": len(selection_rows),
    }))
    (output / "SOURCE_HASH_MANIFEST.json").write_bytes(canonical({
        "v36": {
            "commit": V36_COMMIT,
            "policy_path": "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js",
            "policy_sha256": sha256_file(policy_path),
            "strict_event_ledger_sha256": sha256_file(package / "STRICT_EVENT_LEDGER.jsonl.gz"),
            "full_decision_trace_parts_manifest_sha256": sha256_file(package / "FULL_DECISION_TRACE_PARTS.json"),
            "action_and_fill_trace_part_sha256": sha256_file(package / "ACTION_AND_FILL_TRACE.jsonl.gz.part000"),
        },
        "certified_prints": {**print_receipt, "required_sha256": PRINTS_SHA256, "role": "READ_ONLY_EVIDENCE_JOIN"},
        "books": tape_hashes,
        "template": {
            "commit": TEMPLATE_COMMIT,
            "timeline_path": ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/BOSCOP_DUAL_TIMELINE_V2.csv",
            "marks_path": ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/BOSCOP_DECISION_MARKS.json",
        },
    }))
    (output / "FORBIDDEN_ACCESS_RECEIPT.json").write_bytes(canonical({
        "live_capital_accesses": 0,
        "live_engine_launches": 0,
        "shadow_launches": 0,
        "policy_invocations": 0,
        "score_invocations": 0,
        "network_runtime_accesses": 0,
        "order_accesses": 0,
        "position_accesses": 0,
        "cron_mutations": 0,
        "source": "FROZEN_V36_COMMITTED_TRACE_PLUS_CERTIFIED_PRIVATE_FIT_BBO_AND_PRINT_INPUTS",
    }))
    report_lines = [
        "# Frozen V36 evidence pack",
        "",
        "This is a read-only evidence extraction from V36 `bfde0d8d1135f5c5f48a5f3d619ab30050efab83`; it invokes neither policy nor scorer and performs no shadow or live action.",
        "",
    ]
    for row in selection_rows:
        report_lines.append(f"- **{row['short']} — {row['role']}**: {row['why']} Timeline rows {row['timeline_rows']}; frozen decision rows {row['decision_rows']}; action/fill marks {row['action_and_fill_rows']}.")
    report_lines.extend(["", "Every CSV carries both clocks, every raw two-sided BBO receipt and certified true print inside the frozen W1 span, the carried V36 rest/state, and exact layer tags. Every JSON carries the compressed state strip, every explicit rest walk, pair arm, take, maker fill, terminal state, and decision-count conservation.", ""])
    (output / "V36_EVIDENCE_PACK_REPORT.md").write_text("\n".join(report_lines), encoding="utf-8", newline="\n")

    core_files = sorted(path for path in output.rglob("*") if path.is_file() and path.name not in {"DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"})
    relative_hashes = {path.relative_to(output).as_posix(): {"sha256": sha256_file(path), "bytes": path.stat().st_size} for path in core_files}
    deterministic = {
        "schema_version": "v36-evidence-pack-regeneration-contract-v1",
        "required_clean_builds": 2,
        "comparison_scope": "ALL_GENERATED_FILES",
        "core_file_count": len(core_files),
        "cross_build_result_location": "../V36_EVIDENCE_DETERMINISM_RECEIPT.json",
    }
    (output / "DETERMINISM_RECEIPT.json").write_bytes(canonical(deterministic))
    all_files = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "ARTIFACT_HASH_MANIFEST.json")
    artifact_manifest = {path.relative_to(output).as_posix(): {"sha256": sha256_file(path), "bytes": path.stat().st_size} for path in all_files}
    (output / "ARTIFACT_HASH_MANIFEST.json").write_bytes(canonical({"files": artifact_manifest, "file_count": len(artifact_manifest)}))
    if compare is not None:
        current_files = {path.relative_to(output).as_posix(): {"sha256": sha256_file(path), "bytes": path.stat().st_size} for path in output.rglob("*") if path.is_file()}
        prior_files = {path.relative_to(compare).as_posix(): {"sha256": sha256_file(path), "bytes": path.stat().st_size} for path in compare.rglob("*") if path.is_file()}
        require(current_files == prior_files, "full-output determinism mismatch")
    return {"output": str(output), "games": len(SELECTION), "files": len(artifact_manifest) + 1, "policy_invocations": 0, "score_invocations": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--v36-repo", required=True, type=Path)
    parser.add_argument("--private-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    result = build(args.repo.resolve(), args.v36_repo.resolve(), args.private_root.resolve(), args.output.resolve(), None if args.compare is None else args.compare.resolve())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
