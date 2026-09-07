#!/usr/bin/env python3
"""Cut range-overlap rows from a static recorder-store snapshot, never ingest it.

The existing ORDER 1 row contract is inherited. --consolidated derives spans
using the operator's two formation sources; legacy mode accepts filed bounds.
No price, volume, or same-timestamp chronology is guessed. --self-test uses
only a temporary synthetic SQLite database. Consolidated mode requires a
matching source receipt/hash and writes only beneath the named output folder.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import closing, contextmanager, redirect_stdout
from datetime import date, datetime, timezone
import gzip
import hashlib
import heapq
import itertools
import io
import json
import math
import os
from pathlib import Path
import socket
import sqlite3
import statistics
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/"
TRUTH_DEFAULT = AUDIT + "W1_GROUND_TRUTH_TABLE.json"
TRUE_PRINT_SOURCES = ("public_tape", "ws_log", "spaces_trades")
JOINED_TRUE_PRINT_SOURCES = TRUE_PRINT_SOURCES + ("backfill",)
PRINT_SOURCE_PRIORITY = ("spaces_trades", "public_tape", "backfill")
TUNE_NAME_START, TUNE_NAME_END = "2026-07-11", "2026-07-21"
NON_TUNE_SQL = " AND (src_role IS NULL OR src_role <> 'TUNE_SAMPLE')"
DEDUPE_POLICY = "Before density, anchors, volume and change points, group accepted non-TUNE_SAMPLE true prints by (ticker, floor(ts), price, size). When a key occurs across sources, retain one row: spaces_trades, then public_tape, then backfill; within the surviving source retain the last rowid. Same-source-only repeated prints are preserved. Counts are discarded rows by removed source -> surviving source. Retain the survivor's native timestamp and raw source/role; no store rows are changed."
EXCLUSION_DEFINITIONS = {
    "TUNE_SAMPLE_EVENT_NAME": "Event-name YYMMMDD date is 26JUL11 through 26JUL21 inclusive, independent of bell and row role.",
    "NOT_EXACTLY_TWO_LEGS": "Union inventory of ticks/prints has other than exactly two tickers for the event.",
    "SOURCE_EVENT_OR_TIMESTAMP_ERROR": "A surveyed source row has an event/ticker mismatch or nonfinite timestamp.",
    "UNKNOWN_CATEGORY": "Event prefix does not match the inherited all-tour category map.",
    "UNKNOWN_BELL": "No finite official_ts, sched_honest, identity-matched machine first_inplay_at, or qualifying both-sides trade-density run.",
    "BELL_AFTER_CUTOFF": "UTC date of selected bell exceeds the unchanged inclusive 2026-07-11 cutoff.",
    "UNKNOWN_FORMATION": "Either leg has no accepted deduplicated true print before bell.",
    "EMPTY_FORMATION_TO_BELL_SPAN": "Resolved formation is absent or at/after bell, including a first-both-trades fallback minute that reaches bell.",
    "UNKNOWN_CAUSAL_FORMATION_ANCHOR": "No finite accepted deduplicated print at/before formation after the June-to-first-both pair fallback; a guard, not permission to borrow a future price.",
    "PAIR_HAS_LEG_WITHOUT_ROWS_IN_SPAN": "At least one exact ticker has no non-TUNE_SAMPLE tick or print at formation <= ts < bell under any stored source.",
    "NO_IN_SPAN_TRUE_PRINT": "Path is empty or has no accepted deduplicated true print at formation <= ts < bell.",
    "MISSING_TRUE_PRINT_PRICE": "An accepted print before bell has a missing/nonfinite price.",
    "MISSING_OR_INVALID_TRUE_PRINT_SIZE": "An accepted in-span print has a missing/nonfinite or negative size.",
}
SCHEMA = {
    "prints": ("event", "ticker", "ts", "price", "size", "src", "src_role", "obj"),
    "ticks": ("event", "ticker", "ts", "bid", "ask", "last", "size", "src", "src_role", "obj"),
    "cadence": ("src", "obj", "raw_rows", "kept_rows", "distinct_ts", "median_gap_raw", "median_gap_kept"),
}
PATH_FIELDS = ("seen_true_trade_low_cents", "seen_true_trade_high_cents", "last_cents", "bid_cents", "ask_cents", "volume_cum")
SECOND_ORDER_POLICY = "Group native observations by floor(ts), then order each table's rows by rowid within the second. Emit the second's last book and last true print, retaining all true-print minima/maxima and size sums. Stamp the point at the greatest observed ts in that second (not earlier than any contributing row). Table rowids are independent; their interleaving does not author a cross-table sequence. This is operator-authorized deterministic ordering, not exchange sequence proof."
PRIOR_ART = (
    ("trendpath_build.py", "66b50db3", "arb-executor/analysis/trendpath_build.py", "Minutes-before-bell slices and side rule; discovery/ESS/slice extensions are explicit PARALLEL BUILD overrides, not claims about the old source."),
    ("RECOGNITION_OPERATING_POINT", "41c1f724", AUDIT + "RECOGNITION_OPERATING_POINT.md", "Post-formation drift role rule and gate coverage/accuracy; consumed by the scoreboard, not reimplemented in this cutter."),
    ("SHAPE_TAXONOMY_BUILD1", "e269779b", AUDIT + "SHAPE_TAXONOMY_BUILD1.json", "The filed 13 families and floor-timing null are inherited by the scoreboard; this cutter does not relabel them."),
    ("GATE_POLICY_EVAL_LIVE_COORDS", "71de534a", AUDIT + "GATE_POLICY_EVAL_LIVE_COORDS.md", "Onset/trade-count/travel coordinates, FIRST-BIND and flip-rate scoring are inherited by the scoreboard; no scoring is done here."),
)


def sha256_file(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def finite(value):
    if value is None or isinstance(value, bool):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def compact(value):
    return int(value) if value is not None and float(value).is_integer() else value


def utc_date(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).date().isoformat()


def named_event_date(event):
    """Same event-calendar label as the historical library, not UTC bell day."""
    try:
        return datetime.strptime(event.rsplit("-", 1)[-1][:7], "%y%b%d").date().isoformat()
    except ValueError:
        return None


def tune_named_event(event):
    day = named_event_date(event)
    return day is not None and TUNE_NAME_START <= day <= TUNE_NAME_END


def dedupe_print_rows(rows, removed=None):
    """Bounded to one ticker-second; input and output ordered by native ts."""
    for _, second in itertools.groupby(rows, key=lambda row: math.floor(row["ts"])):
        keys = defaultdict(list)
        for row in second:
            keys[(row["price"], row["size"])].append(row)
        kept = []
        for group in keys.values():
            sources = {row["src"] for row in group}
            if len(sources) == 1:
                kept.extend(group)
                continue
            if not sources.issubset(PRINT_SOURCE_PRIORITY):
                # No invented priority for an unobserved source such as ws_log.
                raise RuntimeError("UNLICENSED_DEDUPE_SOURCE_PRIORITY:" + repr(sorted(sources)))
            survivor_source = next(src for src in PRINT_SOURCE_PRIORITY if src in sources)
            survivor = max((row for row in group if row["src"] == survivor_source), key=lambda row: row["rowid"])
            kept.append(survivor)
            if removed is not None:
                for row in group:
                    if row["rowid"] != survivor["rowid"]:
                        removed[(row["src"], survivor_source)] += 1
        yield from sorted(kept, key=lambda row: (row["ts"], row["rowid"]))


def accepted_print_rows(connection, ticker, joined=False, before=None, inclusive=False, after=None, removed=None):
    sources = JOINED_TRUE_PRINT_SOURCES if joined else TRUE_PRINT_SOURCES
    query = "SELECT rowid,event,ticker,ts,price,size,src,src_role,obj FROM prints WHERE ticker=?"
    query += NON_TUNE_SQL if joined else " AND src_role='LIBRARY'"
    params = [ticker]
    if before is not None:
        query += " AND ts" + ("<=?" if inclusive else "<?")
        params.append(before)
    if after is not None:
        query += " AND ts>=?"
        params.append(after)
    query += " AND src IN (" + ",".join("?" for _ in sources) + ") ORDER BY ts,rowid"
    rows = connection.execute(query, tuple(params) + sources)
    return dedupe_print_rows(rows, removed) if joined else rows


def prior_bindings(root):
    rows = []
    for name, revision, path, inherited in PRIOR_ART:
        source = subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=root)
        commit = subprocess.check_output(["git", "rev-parse", f"{revision}^{{commit}}"], cwd=root, text=True).strip()
        rows.append({"name": name, "commit": commit, "path": path,
                     "sha256": hashlib.sha256(source).hexdigest(), "inherited": inherited})
    return rows


def load_bounds(paths, cutoff):
    """Consume filed truth-table rows; never derive a new bell or formation."""
    specs, exclusions, sources = {}, [], []
    for path in paths:
        document = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        if not isinstance(document, dict) or not isinstance(document.get("rows"), list):
            raise ValueError(f"TRUTH_TABLE_SCHEMA_REQUIRED: {path}")
        sources.append({"path": str(Path(path)), "sha256": sha256_file(path),
                        "bytes": Path(path).stat().st_size,
                        "column_sources": document.get("column_sources", {})})
        for index, row in enumerate(document["rows"]):
            event = row.get("event_id")
            bell = finite(row.get("bell_epoch"))
            reason = None
            if row.get("verified_span") != "OK":
                reason = "UNVERIFIED_SPAN:" + str(row.get("verified_span"))
            elif not row.get("bell_source") or "UNKNOWN" in str(row["bell_source"]).upper() or bell is None:
                reason = "UNKNOWN_BELL"
            elif date.fromisoformat(utc_date(bell)) > cutoff:
                reason = "BELL_AFTER_CUTOFF"
            if reason:
                exclusions.append({"event_id": event, "reason": reason})
                continue
            event_specs = []
            for side in ("legA", "legB"):
                leg = row.get(side)
                formation = finite(row.get(side + "_formation_end_epoch"))
                anchor = finite(row.get(side + "_open_postformation_c"))
                if not event or not row.get("category") or not leg or formation is None or anchor is None or formation >= bell:
                    reason = "MISSING_OR_INVALID_FILED_LEG_BOUND"
                    break
                ticker = row.get(side + "_ticker") or f"{event}-{leg}"
                event_specs.append({"event_id": event, "event_date": named_event_date(event),
                    "bell_utc_date": utc_date(bell),
                    "category": row["category"], "leg_id": leg, "ticker": ticker,
                    "anchor_cents": compact(anchor), "side": "LEADER" if anchor >= 50 else "UNDERDOG",
                    "formation_end_epoch": formation, "bell_epoch": bell,
                    "bell_source": row["bell_source"], "bell_precision": row.get("bell_precision"),
                    "filed_span_end_epoch": row.get("span_end_epoch"),
                    "bound_receipt": {"path": str(path), "row_index": index, "side": side}})
            if reason:
                exclusions.append({"event_id": event, "reason": reason})
                continue
            for spec in event_specs:
                if spec["ticker"] in specs:
                    raise ValueError("DUPLICATE_FILED_TICKER:" + spec["ticker"])
                specs[spec["ticker"]] = spec
    return specs, exclusions, sources


def inspect_schema(connection):
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    actual = {table: [dict(row) for row in connection.execute(f'PRAGMA table_info("{table}")')]
              for table in sorted(tables) if table in SCHEMA}
    missing = {table: [name for name in columns if name not in {r["name"] for r in actual.get(table, [])}]
               for table, columns in SCHEMA.items()}
    return actual, {table: columns for table, columns in missing.items() if columns}


def open_snapshot(path, consolidated=False):
    path = Path(path).resolve(strict=True)
    if path.name == "subsecond_store.db" and not consolidated:
        raise ValueError("LIVE_STORE_REFUSED: use a named static backup, not subsecond_store.db")
    for suffix in ("-wal", "-journal"):
        if Path(str(path) + suffix).exists():
            raise ValueError("SNAPSHOT_HAS_JOURNAL:" + str(path))
    connection = sqlite3.connect(path.as_uri() + "?mode=ro&immutable=1", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def observations(connection, spec, removed=None):
    params = (spec["ticker"], spec["bell_epoch"])
    roles = NON_TUNE_SQL if spec.get("include_other_roles") else " AND src_role='LIBRARY'"
    books = connection.execute("SELECT rowid,ts,bid,ask,src,src_role,obj FROM ticks WHERE ticker=? AND ts<?"+roles+" ORDER BY ts,rowid", params)
    trades = accepted_print_rows(connection, spec["ticker"], joined=spec.get("include_other_roles",False), before=spec["bell_epoch"], removed=removed)
    def tagged(stream, table):
        for row in stream:
            yield float(row["ts"]), table, row["rowid"], dict(row)
    return heapq.merge(tagged(books, "ticks"), tagged(trades, "prints"))


def build_leg(connection, spec):
    formation, bell = spec["formation_end_epoch"], spec["bell_epoch"]
    low = high = last = bid = ask = None
    volume = 0
    path, source_counts, objects = [], Counter(), set()
    timestamp_groups = 0
    previous_signature = None
    first_trade = floor_epoch = floor = None
    row_times = []
    trade_count = 0
    removed = Counter()
    for _, grouped in itertools.groupby(observations(connection, spec, removed), key=lambda row: math.floor(row[0])):
        group = sorted(grouped,key=lambda row:(row[2],row[1]))
        ts = max(row[0] for row in group)
        # rowid orders each table independently; book and trade update disjoint
        # fields. Range extrema use every true print, not just the closing one.
        prices = {finite(r["price"]) for _, table, _, r in group if table == "prints"}
        if None in prices:
            raise ValueError("MISSING_TRUE_PRINT_PRICE:" + spec["ticker"])
        for native_ts, table, _, observation in group:
            source_counts[(table, observation["src"], observation["src_role"])] += 1
            if observation["obj"]:
                objects.add(observation["obj"])
            if table == "ticks":
                bid, ask = finite(observation["bid"]), finite(observation["ask"])
                continue
            price = finite(observation["price"])
            low = price if low is None else min(low, price)
            last = price
            if native_ts < formation:
                continue
            size = finite(observation["size"])
            if size is None or size < 0:
                raise ValueError("MISSING_OR_INVALID_TRUE_PRINT_SIZE:" + spec["ticker"])
            volume += size
            trade_count += 1
            if first_trade is None:
                first_trade = {"timestamp_epoch": native_ts, "price_cents": compact(price)}
            high = price if high is None else max(high, price)
            if floor is None or price < floor:
                floor, floor_epoch = price, native_ts
        if ts < formation:
            continue
        timestamp_groups += 1
        row_times.append(ts)
        signature = (low, high, last, bid, ask, volume)
        if signature == previous_signature:
            continue
        previous_signature = signature
        path.append({"ts": ts, "minutes_to_bell": (bell-ts)/60,
                     "window_fraction": (ts - formation) / (bell - formation),
                     **{key: compact(value) for key, value in zip(PATH_FIELDS, signature)}})
    if not path or first_trade is None:
        raise ValueError("NO_IN_SPAN_TRUE_PRINT:" + spec["ticker"])
    cadence = []
    for obj in sorted(objects):
        cadence.extend(dict(row) for row in connection.execute("SELECT * FROM cadence WHERE obj=? ORDER BY src", (obj,)))
    gaps = [b-a for a,b in zip(row_times, row_times[1:])]
    # Output is the old row shape plus named source/cadence/bound disclosures.
    return {**spec, "floor_fraction": (floor_epoch-formation)/(bell-formation),
        "path": path, "grain": "TICK", "source": "RECORDER_STORE_STATIC_SNAPSHOT",
        "cadence_s": statistics.median(gaps) if gaps else None,
        "licensed_layers": ["MACRO", "MICRO"], "micro_micro_licensed": False,
        "first_true_trade": first_trade,
        "source_rows": [{"table": t, "src": src, "src_role": role, "rows": n}
                        for (t,src,role),n in sorted(source_counts.items(),key=lambda item:tuple(str(v) for v in item[0]))],
        "cadence": {"unit": "seconds", "resampling": "SECOND_LAST_STATE_WITH_TRUE_PRINT_EXTREMA", "timestamp_groups_in_span": timestamp_groups,
                    "minimum_gap": min(gaps) if gaps else None, "median_gap": statistics.median(gaps) if gaps else None,
                    "maximum_gap": max(gaps) if gaps else None, "source_objects": cadence,
                    "objects_without_cadence": sorted(objects-{r["obj"] for r in cadence}),
                    "same_timestamp_policy": SECOND_ORDER_POLICY},
        "true_print_count_in_span": trade_count,
        "cross_source_print_duplicates_removed": nested_counts(removed),
        "starts_exactly_at_formation": path[0]["window_fraction"] == 0,
        "postformation_floor_cents": compact(floor),
        "inherited_seen_low_may_precede_formation": low != floor}


def receipt_template(root, cutoff):
    return {"method": "NATIVE_TICK_RECORDER_RANGE_OVERLAP_FROM_FILED_TRUTH_TABLE_BOUNDS",
        "status": "PENDING", "prior_art_bound": prior_bindings(root),
        "inherited_builder": {"path": "arb-executor/analysis/build_range_overlap_library.py",
                              "sha256": sha256_file(root / "arb-executor/analysis/build_range_overlap_library.py")},
        "schema_contract": SCHEMA, "bell_cutoff_inclusive_utc_date": cutoff.isoformat(),
        "rules": {
            "span": "File W1_GROUND_TRUTH_TABLE schema only; verified_span=OK and known bell_source; per-leg formation_end_epoch <= ts < bell_epoch; no bell or formation inference. The literal bell endpoint is used; filed_span_end_epoch is disclosed separately.",
            "roles": "Only src_role = LIBRARY; NULL and all other roles are excluded rather than inferred from name.",
            "side": "LEADER if inherited filed post-formation anchor_cents >= 50, otherwise UNDERDOG. The scoreboard's first-tick pair anchors are a separate causal read.",
            "low": "Running minimum of accepted prints.price initialized through formation, identical to ORDER 1's prior-low convention; subsequent true prints update it.",
            "high": "Running maximum of accepted prints.price from formation; never ticks.last or book_transition.",
            "last": "Most recent accepted prints.price at or before native timestamp; no midpoint, anchor, or ticks.last fallback.",
            "book": "ticks.bid and ticks.ask in stored cents, carried between book observations; missing sides remain null.",
            "volume": "Running sum of accepted prints.size at formation <= ts < bell; missing/negative sizes exclude the leg. Stored zero sizes remain zero and are not estimated.",
            "true_print_sources": TRUE_PRINT_SOURCES,
            "excluded_inferred_source": "book_transition is a changed-last surrogate, not a true trade; never authors low/high/last/volume.",
            "change_point": SECOND_ORDER_POLICY+" Emit only when at least one of the six fields changes; no synthetic formation tick.",
            "floor_fraction": "First accepted true print at the eventual post-formation minimum, on this leg's formation-to-bell clock. No future path labels are inserted into causal points.",
            "pair_hygiene": "Only events with exactly two successful bounded legs emitted; incomplete pairs excluded and counted.",
            "event_date": "The event_id's YYMMMDD calendar label, distinct from bell_utc_date; same-day retrieval hygiene must use the same basis for old and new libraries.",
            "leave_self_out": "Not applied while cutting; scoreboard applies walk-forward, leave-self-out and same-day exclusion."},
        "differs_from_prior_art": {
            "vs_June_minute_cut": "Native recorder tick timestamps, targeted Mar-Jul 2026 rather than the June-filed library ending 2026-05-01; actual span is reported, never assumed. No resampling or manufactured boundary ticks. Bell/formation now come from the filed truth-table source, not historical parquet spans.",
            "vs_range_spectrum_v1": "Recorder true prints and native book changes, bell-bounded formation-to-bell; not polling snapshots with an onset right edge.",
            "vs_FUTURE_LOW_RETURN_LIBRARY": "Carries high, last, bid, ask and true-print size-sum beside running low; native grain rather than minute labels.",
            "vs_trendpath_build": "Per-game leg paths, not page percentiles. The pinned source uses first-hour-median discovery; PARALLEL BUILD's first-true-tick discovery is explicitly a new override, not silently attributed to that source."}}


def write_receipt(path, receipt):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False))


def run(args):
    cutoff = date.fromisoformat(args.bell_cutoff)
    db = Path(args.db).resolve(strict=True)
    truth_paths = args.truth_table or [Path(args.repo_root)/TRUTH_DEFAULT]
    destinations = [Path(args.out).resolve(), Path(args.receipt).resolve()]
    protected = {db, Path(__file__).resolve(), *(Path(path).resolve() for path in truth_paths)}
    if destinations[0] == destinations[1] or any(path in protected for path in destinations):
        raise ValueError("OUTPUT_MUST_NOT_ALIAS_INPUT_OR_OTHER_OUTPUT")
    if db.name == "subsecond_store.db":
        raise ValueError("LIVE_STORE_REFUSED: use a named static backup, not subsecond_store.db")
    receipt = receipt_template(Path(args.repo_root), cutoff)
    specs, excluded, source_receipts = load_bounds(truth_paths, cutoff)
    receipt["bound_sources"] = source_receipts
    receipt["bounds_excluded"] = dict(Counter(row["reason"] for row in excluded))
    receipt["eligible_bounded_legs"] = len(specs)
    before = (db.stat().st_size, db.stat().st_mtime_ns)
    receipt["source_snapshot"] = {"path": str(db), "bytes": before[0], "sha256": sha256_file(db)}
    if args.expected_sha256 and not receipt["source_snapshot"]["sha256"].startswith(args.expected_sha256.lower()):
        raise ValueError("SNAPSHOT_HASH_MISMATCH")
    with closing(open_snapshot(db)) as connection:
        schema, missing = inspect_schema(connection)
        receipt["schema_observed"] = schema
        if missing:
            receipt.update(status="PROOF BLOCKED — pre-ingest backup lacks required fields", missing_schema=missing,
                           counts={"events": 0, "legs": 0, "points": 0}, library_written=False)
            write_receipt(args.receipt, receipt)
            return 2
        if not specs:
            receipt.update(status="PROOF BLOCKED — no eligible filed pre-cutoff bell/formation bounds",
                           counts={"events": 0, "legs": 0, "points": 0}, library_written=False)
            write_receipt(args.receipt, receipt)
            return 2
        by_event, failed = defaultdict(list), []
        for ticker, spec in sorted(specs.items()):
            by_event[spec["event_id"]].append(spec)
        counts, categories = Counter(events=0,legs=0,points=0), Counter()
        first_formation = last_bell = None
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        # Keep only one game's native paths in memory, not the whole tick era.
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=output.name+".", suffix=".partial", delete=False) as raw:
            temporary_output = Path(raw.name)
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
                for event, event_specs in sorted(by_event.items()):
                    legs = []
                    for spec in event_specs:
                        try:
                            legs.append(build_leg(connection, spec))
                        except ValueError as error:
                            failed.append({"event_id": event, "ticker": spec["ticker"], "reason": str(error)})
                    if len(legs) != 2:
                        failed.append({"event_id": event, "reason": "INCOMPLETE_PAIR", "successful_legs": len(legs)})
                        continue
                    counts["events"] += 1
                    for row in sorted(legs, key=lambda row: row["ticker"]):
                        counts["legs"] += 1
                        counts["points"] += len(row["path"])
                        categories[row["category"]] += 1
                        first_formation = row["formation_end_epoch"] if first_formation is None else min(first_formation,row["formation_end_epoch"])
                        last_bell = row["bell_epoch"] if last_bell is None else max(last_bell,row["bell_epoch"])
                        zipped.write((json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n").encode())
        receipt.update(exclusions=failed, counts=dict(counts))
        if (db.stat().st_size, db.stat().st_mtime_ns) != before:
            temporary_output.unlink()
            raise ValueError("SNAPSHOT_CHANGED_DURING_READ")
        if not counts["legs"]:
            temporary_output.unlink()
            receipt.update(status="PROOF BLOCKED — no complete eligible pairs", library_written=False)
            write_receipt(args.receipt, receipt)
            return 2
        temporary_output.replace(output)
    receipt.update(status="PROOF RUN — STATIC TICK SNAPSHOT — NOT A RULING", library_written=True,
        output={"path": str(output), "bytes": output.stat().st_size, "sha256": sha256_file(output)},
        category_breakdown=dict(categories),
        actual_date_span={"formation_min": utc_date(first_formation),"bell_max": utc_date(last_bell)})
    write_receipt(args.receipt, receipt)
    return 0


def minute_end(ts):
    """June producer's half-open [minute-60, minute) trade bucket."""
    return (math.floor(ts / 60) + 1) * 60


def iso_epoch(value):
    if not value:
        return None
    stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return stamp.replace(tzinfo=timezone.utc).timestamp() if stamp.tzinfo is None else stamp.timestamp()


def event_category(event):
    # corpus_restamp2.py's filed all-tour mapping, including both ITF tours.
    for prefix, category in (("KXATPCHALLENGER", "ATP_CHALL"),
            ("KXWTACHALLENGER", "WTA_CHALL"), ("KXITFWMATCH", "ITF_W"),
            ("KXITFMATCH", "ITF_M"), ("KXWTAMATCH", "WTA_MAIN"),
            ("KXATPMATCH", "ATP_MAIN")):
        if event.startswith(prefix):
            return category
    return None


def file_binding(path):
    path = Path(path).resolve(strict=True)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def create_catalog(source, catalog, args):
    """Small on-disk metadata catalogue; source table rows are never loaded."""
    catalog.executescript("""
        CREATE TABLE tickers(ticker TEXT PRIMARY KEY,event TEXT NOT NULL);
        CREATE INDEX ticker_event ON tickers(event,ticker);
        CREATE TABLE market(ticker TEXT PRIMARY KEY,open_epoch REAL,settlement_epoch REAL);
        CREATE TABLE corpus(event TEXT PRIMARY KEY,body TEXT NOT NULL);
        CREATE TABLE observed(event TEXT PRIMARY KEY,body TEXT NOT NULL);
    """)
    print("CATALOG: indexed next-ticker seeks (no full index scan)", flush=True)
    for table in ("ticks", "prints"):
        found = source.execute(f"SELECT ticker FROM {table} ORDER BY ticker LIMIT 1").fetchone()
        while found is not None:
            ticker = found[0]
            if not ticker or "-" not in ticker:
                raise ValueError("INVALID_SOURCE_TICKER")
            catalog.execute("INSERT OR IGNORE INTO tickers VALUES(?,?)", (ticker,ticker.rsplit("-",1)[0]))
            found = source.execute(f"SELECT ticker FROM {table} WHERE ticker>? ORDER BY ticker LIMIT 1",(ticker,)).fetchone()
        catalog.commit()
        print(f"CATALOG: {table} ticker index complete", flush=True)
    import pyarrow.parquet as pq
    for batch in pq.ParquetFile(args.market_metadata).iter_batches(
            batch_size=256, columns=["ticker", "open_time", "settlement_ts"]):
        for row in batch.to_pylist():
            catalog.execute("INSERT INTO market VALUES(?,?,?)", (
                row["ticker"],iso_epoch(row["open_time"]),iso_epoch(row["settlement_ts"])))
    with Path(args.corpus_events).open(encoding="utf-8-sig") as stream:
        for line in stream:
            row = json.loads(line)
            catalog.execute("INSERT INTO corpus VALUES(?,?)",(row["event"],json.dumps(row)))
    if args.observed_starts and Path(args.observed_starts).exists():
        with closing(sqlite3.connect(Path(args.observed_starts).resolve().as_uri()+"?mode=ro",uri=True)) as observed:
            observed.row_factory = sqlite3.Row
            tables = {row[0] for row in observed.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "observed_start_events" in tables:
                for row in observed.execute("SELECT * FROM observed_start_events"):
                    catalog.execute("INSERT INTO observed VALUES(?,?)",(row["kalshi_event_ticker"],json.dumps(dict(row))))
    catalog.commit()
    return catalog.execute("SELECT count(*) FROM tickers").fetchone()[0]


def survey_ticker(source, ticker, include_other_roles=False, census_only=False):
    """One ticker streamed twice (quotes, prints); only minute summaries stay."""
    counts, trade_minutes, observed_minutes = Counter(), Counter(), set()
    first_trade = None
    library_rows = 0
    errors = set()
    removed, first_by_source = Counter(), {}
    sources = JOINED_TRUE_PRINT_SOURCES if include_other_roles else TRUE_PRINT_SOURCES
    for table, fields in (("ticks","bid,ask"),("prints","price,size")):
        query = f"SELECT rowid,event,ts,src,src_role,{fields} FROM {table} WHERE ticker=? ORDER BY ts,rowid"
        def surveyed_rows():
            nonlocal library_rows
            for row in source.execute(query,(ticker,)):
                role = row["src_role"] if row["src_role"] is not None else "NULL"
                counts[(table,row["src"],role)] += 1
                if row["event"] != ticker.rsplit("-",1)[0]:
                    errors.add("SOURCE_EVENT_TICKER_MISMATCH")
                if role == "LIBRARY":
                    library_rows += 1
                if census_only or role == "TUNE_SAMPLE" or (not include_other_roles and role != "LIBRARY"):
                    continue
                if finite(row["ts"]) is None:
                    errors.add("INVALID_TIMESTAMP")
                    continue
                if table == "ticks" or row["src"] in sources:
                    yield row
        stream = surveyed_rows()
        if table == "prints" and include_other_roles:
            stream = dedupe_print_rows(stream, removed)
        for row in stream:
            ts = float(row["ts"])
            if table == "ticks":
                observed_minutes.add(minute_end(ts))
            elif finite(row["price"]) is not None:
                end = minute_end(ts)
                observed_minutes.add(end)
                trade_minutes[end] += 1
                if first_trade is None:
                    first_trade = ts
                first_by_source.setdefault(row["src"], ts)
    return {"ticker":ticker,"counts":counts,"trade_minutes":trade_minutes,
            "observed_minutes":observed_minutes,"first_trade":first_trade,
            "library_rows":library_rows,"errors":sorted(errors),"include_other_roles":include_other_roles,
            "duplicates_removed":removed,"first_accepted_print_by_source":first_by_source}


def density_bell(surveys):
    """June tier-2: three consecutive minutes, >=3 true trades on each leg."""
    common = sorted(set(surveys[0]["trade_minutes"]) & set(surveys[1]["trade_minutes"]))
    run_start = previous = None
    run_length = 0
    for minute in common:
        enough = all(leg["trade_minutes"][minute] >= 3 for leg in surveys)
        if enough:
            if previous is not None and minute == previous + 60:
                run_length += 1
            else:
                run_start, run_length = minute, 1
            if run_length == 3:
                return run_start
        else:
            run_length = 0
        previous = minute if enough else None
    return None


def resolve_bell(catalog, event, surveys):
    filed = catalog.execute("SELECT body FROM corpus WHERE event=?",(event,)).fetchone()
    row = json.loads(filed[0]) if filed else {}
    if finite(row.get("official_ts")) is not None:
        return finite(row["official_ts"]), "CORPUS_OFFICIAL_MACHINE_RECEIPT", "official_ts"
    if finite(row.get("sched_honest")) is not None:
        return finite(row["sched_honest"]), "CORPUS_SCHED_HONEST:"+str(row.get("sched_src")), "sched_honest"
    observed = catalog.execute("SELECT body FROM observed WHERE event=?",(event,)).fetchone()
    if observed:
        record = json.loads(observed[0])
        # Identity-matched event table only. Legacy three-letter leg rows cannot join.
        stamp = iso_epoch(record.get("first_inplay_at"))
        if stamp is not None:
            return stamp, "OBSERVED_STARTS_MACHINE_RECEIPT_DISCOVERY_UPPER_BOUND", "first_inplay_at"
    stamp = density_bell(surveys)
    return stamp, "both_sides_trade_density" if stamp is not None else "UNKNOWN", "prints.price / true-trade count"


def resolve_formations(catalog, surveys, bell):
    # FIRST_BOTH_SIDES_TRADE is cumulative availability, not simultaneous prints.
    if any(s["first_trade"] is None or s["first_trade"] >= bell for s in surveys):
        raise ValueError("UNKNOWN_FORMATION")
    first_both = minute_end(max(s["first_trade"] for s in surveys))
    results = []
    for survey in surveys:
        metadata = catalog.execute("SELECT open_epoch,settlement_epoch FROM market WHERE ticker=?",
                                   (survey["ticker"],)).fetchone()
        opened = metadata[0] if metadata else None
        if opened is not None:
            # June classify_premarket_phase + first stable minute; metadata's
            # settlement-zone exclusion is also inherited, not used as a bell.
            stable = (m for m in survey["observed_minutes"] if m >= opened+120*60 and m < bell
                      and (metadata[1] is None or m < metadata[1]-300))
            formation = min(stable, default=None)
            method = "JUNE_OPEN_PLUS_120"
        else:
            formation, method = first_both, "FIRST_BOTH_SIDES_TRADE"
        if formation is None or formation >= bell:
            raise ValueError("EMPTY_FORMATION_TO_BELL_SPAN:"+method)
        results.append((formation,method,opened))
    return results


def causal_anchor(source,ticker,formation):
    placeholders = ",".join("?" for _ in JOINED_TRUE_PRINT_SOURCES)
    latest = source.execute("SELECT ts FROM prints WHERE ticker=? AND ts<=?"+NON_TUNE_SQL+
        f" AND src IN ({placeholders}) ORDER BY ts DESC,rowid DESC LIMIT 1",
        (ticker,formation)+JOINED_TRUE_PRINT_SOURCES).fetchone()
    if latest is None:
        return None
    rows = list(accepted_print_rows(source,ticker,joined=True,before=formation,inclusive=True,after=math.floor(latest[0])))
    return finite(max(rows,key=lambda row:row["rowid"])["price"]) if rows else None


def pair_specs(source,catalog,event,surveys,cutoff,diagnostics=None):
    """Shared bounded eligibility for the cutter and non-publishing yield audit."""
    if tune_named_event(event):
        raise ValueError("TUNE_SAMPLE_EVENT_NAME")
    if len(surveys) != 2:
        raise ValueError("NOT_EXACTLY_TWO_LEGS")
    if any(s["errors"] for s in surveys):
        raise ValueError("SOURCE_EVENT_OR_TIMESTAMP_ERROR")
    category = event_category(event)
    if not category:
        raise ValueError("UNKNOWN_CATEGORY")
    bell,bell_source,bell_field = resolve_bell(catalog,event,surveys)
    if bell is None:
        raise ValueError("UNKNOWN_BELL")
    if date.fromisoformat(utc_date(bell)) > cutoff:
        raise ValueError("BELL_AFTER_CUTOFF")
    bounds = resolve_formations(catalog,surveys,bell)
    anchors = [causal_anchor(source,s["ticker"],bound[0]) for s,bound in zip(surveys,bounds)]
    previous_bounds = bounds
    switched = any(anchor is None and bound[1] == "JUNE_OPEN_PLUS_120" for anchor,bound in zip(anchors,bounds))
    if switched:
        if diagnostics is not None:
            diagnostics["anchor_fallback_pairs_switched"] += 1
        first_both = minute_end(max(s["first_trade"] for s in surveys))
        if first_both >= bell:
            raise ValueError("EMPTY_FORMATION_TO_BELL_SPAN:FIRST_BOTH_SIDES_TRADE_ANCHOR_FALLBACK")
        bounds = [(first_both,"FIRST_BOTH_SIDES_TRADE",bound[2]) for bound in bounds]
        anchors = [causal_anchor(source,s["ticker"],first_both) for s in surveys]
    if any(anchor is None for anchor in anchors):
        raise ValueError("UNKNOWN_CAUSAL_FORMATION_ANCHOR")
    specs=[]
    for survey,(formation,method,opened),anchor,prior in zip(surveys,bounds,anchors,previous_bounds):
        # Membership is measured inside the actual span, across both tables
        # and all stored role/source labels, not from a lifetime LIBRARY count.
        in_span = any(source.execute(f"SELECT 1 FROM {table} WHERE ticker=? AND ts>=? AND ts<?"+NON_TUNE_SQL+" LIMIT 1",
            (survey["ticker"],formation,bell)).fetchone() for table in ("ticks","prints"))
        if not in_span:
            raise ValueError("PAIR_HAS_LEG_WITHOUT_ROWS_IN_SPAN:"+survey["ticker"])
        specs.append({"event_id":event,"event_date":named_event_date(event),
            "category":category,"leg_id":survey["ticker"].rsplit("-",1)[-1],"ticker":survey["ticker"],
            "anchor_cents":compact(anchor),"side":"LEADER" if anchor>=50 else "UNDERDOG",
            "formation_end_epoch":formation,"formation_source":method,"market_open_epoch":opened,
            "bell_epoch":bell,"bell_utc_date":utc_date(bell),"bell_source":bell_source,"bell_source_field":bell_field,
            "span_method":method+" / "+bell_source,"include_other_roles":True,
            "row_role_policy":"BOUNDARY_JOIN_EXCLUDING_TUNE_SAMPLE_PRESERVE_LABELS",
            "anchor_fallback_from_june":switched,
            "formation_before_anchor_fallback":{"epoch":prior[0],"source":prior[1]} if switched else None,
            "pair_first_true_trade_epochs":{s["ticker"]:s["first_trade"] for s in surveys}})
    return specs


def nested_counts(counter):
    result = {}
    for (outer,inner),count in sorted(counter.items()):
        result.setdefault(outer,{})[inner] = count
    return result


def consolidated_receipt(args):
    root = Path(args.repo_root)
    if args.prior_art_receipt:
        receipt = json.loads(Path(args.prior_art_receipt).read_text(encoding="utf-8"))
        receipt["prior_art_bundle"] = file_binding(args.prior_art_receipt)
    else:
        receipt = prior_art_bundle(root,date.fromisoformat(args.bell_cutoff))
    receipt.update(method="CONSOLIDATED_STORE_NATIVE_TICK_CUT_WITH_DERIVED_SPANS",
        started_utc=datetime.now(timezone.utc).isoformat(),
        base_commit="28692162", builder=file_binding(__file__),
        consolidation_receipt=file_binding(args.consolidation_receipt),
        market_metadata=file_binding(args.market_metadata), corpus_events=file_binding(args.corpus_events),
        observed_starts=file_binding(args.observed_starts) if args.observed_starts and Path(args.observed_starts).exists() else None)
    receipt["rules"].update(
        span="Derived per leg; formation_end_epoch <= native ts < bell_epoch. No filed truth-table bounds required.",
        formation_sources={
            "JUNE_OPEN_PLUS_120":"Where g9_metadata.open_time exists: first observed minute end at/after open+120 minutes, before bell and outside June's settlement-minus-300-second zone. Native book/print minutes supply observed coverage; not a manufactured path row.",
            "FIRST_BOTH_SIDES_TRADE":"Without a market open, or for both legs when either June formation lacks a causal accepted anchor: minute_end(max(first_true_trade_A,first_true_trade_B)), using non-TUNE_SAMPLE deduplicated true prints. Cumulative availability, not simultaneous prints. The pair fallback moves formation itself; it never inserts a future price at the old June formation. Prior formation/source is retained per leg."},
        minute_clock="June's half-open [minute_ts-60,minute_ts) buckets; minute_end(ts)=(floor(ts/60)+1)*60. Only span derivation uses minutes; path stays native.",
        bell="corpus_events_v2.official_ts, else sched_honest, else event-identity-matched observed_starts.first_inplay_at (discovery upper bound labeled), else June both_sides_trade_density (3 consecutive minutes with >=3 true trades on each side), else UNKNOWN. No expected-expiration/settlement/name-date/onset_est bell substitute.",
        side="LEADER if latest accepted deduplicated true-print price at formation >=50, else UNDERDOG. Missing June anchor triggers a pair-wide FIRST_BOTH_SIDES_TRADE formation fallback; no midpoint or future-price borrowing at an earlier formation.",
        population="All ticker events are counted. Event-name dates July 11 through July 21 inclusive are excluded independently of bell. Exactly two legs required; join exact tickers across non-TUNE_SAMPLE roles, preserving labels, then enforce lawful per-leg spans and the unchanged inclusive UTC bell cutoff. Output month is UTC bell month; input month is event-name month.",
        roles="TUNE_SAMPLE rows are always filtered before use, including books, density, formation, anchor, presence checks and paths. Other stored roles, including NULL and OTHER, may join without relabeling. All ticks sources may supply book rows; public_tape, ws_log, spaces_trades and verified backfill supply true prints. book_transition remains inferred and excluded as a true print. No rows at/after bell enter a path.",
        true_print_sources=JOINED_TRUE_PRINT_SOURCES,
        backfill_source_proof={"path":"/root/Omi-Workspace/arb-executor/analysis/print_backfill.py","sha256":"bc29c1c72541d1343ebfa9c1361dc25b31ba6dcd4c9be6df526a737ea3307c5f","fields":"Kalshi /markets/trades: created_time -> ts; yes_price_dollars * 100 -> price; count_fp/count -> size (lines 31-32, 52-65). Read-only source classification; writer not invoked."},
        cross_source_duplicates=DEDUPE_POLICY,
        tag_804="Exam exclusion is the union of event-name dates 26JUL11..26JUL21 and TUNE_SAMPLE-tagged rows, regardless of bell. Census counts inspect but never consume those rows as member observations. Name/tag cardinality is measured, not asserted to equal 804.",
        validation4="validation4 (Mar 20-Apr 18) is book-only and supplies no true prints; validation4-only legs yield no library legs by construction. The effective true-print library start is the first spaces_trades date, Apr 18, not Mar 20. Mixed-source tickers still require accepted true prints and lawful spans; input first accepted source dates and actual emitted span are measured in this receipt.",
        change_point=SECOND_ORDER_POLICY+" Emit only when at least one of the six values changes; no synthetic formation tick.",
        resource_policy="nice 10; source immutable read-only/query_only; stream by ticker; only one pair's minute summaries and native paths resident; SQLite catalogue/temp files and outputs under output directory.",
        source_lock="Hold CC's subsecond_store.db.lock with flock LOCK_EX from before the starting store hash through the ending hash and receipt publication. Consolidator's LOCK_NB skips; stage ingest's blocking LOCK_EX waits. CUTTER_RUN.lock is a separate audit record, not a second coordination lock.",
        source_hashes="Exactly two full store SHA256 scans on a successful cut: once at start and once at end, both while holding the shared writer lock. No mid-cut scan or preverified-hash bypass; publish only when both hashes equal the consolidation receipt hash and stat/journal guards pass.")
    receipt["differs_from_prior_art"].update(
        vs_28692162_proof="Derive spans instead of requiring filed 804 bounds; non-TUNE_SAMPLE cross-role boundary join, exam event-name exclusion, source-priority print deduplication and rowid-ordered second close/extrema replace role-only and timestamp-conflict exclusions. Missing June anchors move both formations to first-both-trades. Store is read-only under CC's shared lock with equal start/end hashes and stat/journal guards.",
        vs_June_minute_cut="Native TICK paths from consolidated store, all tours. Formation inherits June open+120 where available, on observed native-tape minute coverage; otherwise operator-authorized FIRST_BOTH_SIDES_TRADE. Bell prefers specified machine/schedule receipts, then June tier-2 density; no tier-1 price-discovery or expected-expiration substitute. Missing actual calendar minutes break density runs.",
        anchor="Latest accepted deduplicated true print at formation; missing June anchor moves the pair's formation to FIRST_BOTH_SIDES_TRADE, explicitly recorded, never a later print borrowed at the old formation.")
    return receipt


def prior_art_bundle(root,cutoff):
    receipt = receipt_template(root,cutoff)
    receipt["span_prior_art"] = {name:file_binding(root/path) for name,path in (
        ("June_producer","arb-executor/data/scripts/build_per_minute_universe.py"),
        ("future_low","arb-executor/analysis/build_window1_v54_future_low_return_library.py"),
        ("all_tour_categories","arb-executor/analysis/corpus_restamp2.py"))}
    return receipt


@contextmanager
def store_cut_lock(args):
    import fcntl  # Linux cutter only; legacy synthetic tests also run on Windows.

    # CC forms this name from the repo's DB path BEFORE resolving its symlink.
    # Opening the existing inode read-only avoids truncating/replacing CC's lock.
    lock_path = Path(args.store_lock or args.repo_root/"arb-executor/state/subsecond_store.db.lock")
    audit_path = Path(args.out).resolve().parent/"CUTTER_RUN.lock"
    if lock_path.resolve(strict=True) == Path(args.db).resolve(strict=True):
        raise ValueError("STORE_LOCK_MUST_NOT_BE_THE_DATABASE")
    with lock_path.open("rb") as held:
        print(f"LOCK_WAIT pid={os.getpid()} path={lock_path}",flush=True)
        fcntl.flock(held,fcntl.LOCK_EX)
        try:
            if audit_path.exists():
                raise ValueError("REFUSE_TO_OVERWRITE_PRIOR_CUTTER_RUN_LOCK_RECORD")
            stat = os.fstat(held.fileno())
            state = {"lock_holder":{"pid":os.getpid(),"host":socket.gethostname()},
                "start_time_utc":datetime.now(timezone.utc).isoformat(),
                "shared_lock_path":str(lock_path),"shared_lock_device":stat.st_dev,"shared_lock_inode":stat.st_ino,
                "audit_path":str(audit_path),"store_path":str(Path(args.db).resolve()),
                "expected_store_sha256":args.expected_sha256,"store_sha256":None,
                "store_sha256_start":None,"store_sha256_end":None,"lock_held":True}

            def record(**fields):
                state.update(fields)
                # Atomic replacement applies only to our audit file, never CC's lock.
                temporary = audit_path.with_name(audit_path.name+".tmp")
                temporary.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n",encoding="utf-8")
                temporary.replace(audit_path)

            record(status="LOCK_HELD")
            print("LOCK_ACQUIRED "+json.dumps(state),flush=True)
            try:
                yield state,record
            except BaseException as error:
                record(status="FAILED",error=str(error))
                raise
            else:
                record(status="COMPLETE")
            finally:
                record(lock_held=False,releasing_utc=datetime.now(timezone.utc).isoformat())
        finally:
            fcntl.flock(held,fcntl.LOCK_UN)


def run_consolidated(args):
    db = Path(args.db).resolve(strict=True)
    output, receipt_path = Path(args.out).resolve(), Path(args.receipt).resolve()
    if output.parent != receipt_path.parent or output == receipt_path or db in (output,receipt_path):
        raise ValueError("OUTPUTS_MUST_SHARE_ONE_DIRECTORY_AND_NOT_ALIAS_INPUT")
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists() or receipt_path.exists():
        raise ValueError("REFUSE_TO_OVERWRITE_EXISTING_LIBRARY_OR_RECEIPT")
    if os.name != "nt" and os.getpriority(os.PRIO_PROCESS,0) < 10:
        raise ValueError("CONSOLIDATED_RUN_REQUIRES_NICE_10_OR_LOWER_PRIORITY")
    if args.verified_source_mtime_ns is not None or args.verified_source_bytes is not None:
        raise ValueError("CONSOLIDATED_HASH_BYPASS_NOT_ALLOWED")
    with store_cut_lock(args) as (lock_state,record_lock):
        return run_consolidated_locked(args,lock_state,record_lock)


def run_consolidated_locked(args,lock_state,record_lock):
    db = Path(args.db).resolve(strict=True)
    output,receipt_path = Path(args.out).resolve(),Path(args.receipt).resolve()
    os.environ["TMPDIR"] = str(output.parent)
    tempfile.tempdir = str(output.parent)
    before = (db.stat().st_size,db.stat().st_mtime_ns)
    consolidation = json.loads(Path(args.consolidation_receipt).read_text(encoding="utf-8-sig"))
    expected = args.expected_sha256.lower() if args.expected_sha256 else None
    if not expected or len(expected) != 64 or expected not in json.dumps(consolidation).lower():
        raise ValueError("FULL_SOURCE_HASH_MUST_BE_BOUND_BY_CONSOLIDATION_RECEIPT")
    record_lock(status="HASHING_START",hash_start_started_utc=datetime.now(timezone.utc).isoformat())
    print("VERIFY_START: full source SHA256 scan (shared lock held)",flush=True)
    actual = sha256_file(db)
    record_lock(status="RUNNING",store_sha256=actual,store_sha256_start=actual,
        hash_start_completed_utc=datetime.now(timezone.utc).isoformat())
    print(f"SOURCE_SHA256_START={actual}",flush=True)
    verification = "Full store SHA256 at start and end only, both under CC's exclusive writer lock; matching consolidation hash and unchanged stat/journal guards required before publication."
    if actual != expected:
        raise ValueError("CONSOLIDATED_SOURCE_HASH_MISMATCH")
    receipt = consolidated_receipt(args)
    receipt["source_snapshot"] = {"path":str(db),"bytes":before[0],"mtime_ns":before[1],"sha256":actual,
        "sha256_start":actual,"sha256_end":None,"verification":verification}
    cutoff = date.fromisoformat(args.bell_cutoff)
    counts, months, categories, formations, methods = Counter(), Counter(), Counter(), Counter(), Counter()
    input_sources, role_rows, role_tickers, role_events, excluded_events, excluded_legs = (Counter() for _ in range(6))
    cadence_values, source_output, lawful_months, emitted_roles = [], Counter(), Counter(), Counter()
    dedupe_survey, dedupe_emitted, switches, named_exclusion, first_sources = Counter(), Counter(), Counter(), Counter(), {}
    formation_min = bell_max = None
    exclusions_path = output.parent / "RANGE_OVERLAP_LIBRARY_TICKS_EXCLUSIONS.jsonl"
    progress_path = output.parent / "RANGE_OVERLAP_LIBRARY_TICKS_PROGRESS.json"
    census_path = output.parent / "RANGE_OVERLAP_LIBRARY_TICKS_CENSUS.sqlite"
    if any(p.exists() for p in (exclusions_path,census_path)):
        raise ValueError("REFUSE_TO_OVERWRITE_PRIOR_CENSUS")
    work_started = time.monotonic()
    with closing(open_snapshot(db,consolidated=True)) as source, closing(sqlite3.connect(census_path)) as catalog:
        _, missing = inspect_schema(source)
        if missing:
            raise ValueError("MISSING_SOURCE_SCHEMA:"+json.dumps(missing))
        catalog.execute("PRAGMA temp_store=FILE")
        catalog.execute("PRAGMA cache_size=-8192")
        total = create_catalog(source,catalog,args)
        print(f"CATALOG READY: {total} tickers; starting per-ticker survey/cut",flush=True)
        ticker_started = time.monotonic()
        next_progress = args.progress_every
        receipt["catalog_tickers"] = total
        first_thousand = None
        with exclusions_path.open("x",encoding="utf-8") as exclusions, \
                tempfile.NamedTemporaryFile(dir=output.parent,prefix=output.name+".",suffix=".partial",delete=False) as raw:
            partial = Path(raw.name)
            with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped:
                events = catalog.execute("SELECT event,ticker FROM tickers ORDER BY event,ticker")
                for event, grouped in itertools.groupby(events,key=lambda row:row[0]):
                    tickers = [row[1] for row in grouped]
                    counts["events_surveyed"] += 1
                    surveys = []
                    event_roles = set()
                    month = (named_event_date(event) or "UNKNOWN")[:7]
                    exam_named = tune_named_event(event)
                    for ticker in tickers:
                        survey = survey_ticker(source,ticker,include_other_roles=True,census_only=exam_named)
                        surveys.append(survey)
                        counts["tickers_surveyed"] += 1
                        ticker_roles = set()
                        for (table,src,role),number in survey["counts"].items():
                            input_sources[(month,f"{table}/{src}/{role}")] += number
                            role_rows[role] += number
                            if exam_named:
                                named_exclusion["input_rows"] += number
                                if role == "TUNE_SAMPLE":
                                    named_exclusion["also_TUNE_SAMPLE_tagged_rows"] += number
                            ticker_roles.add(role)
                        dedupe_survey.update(survey["duplicates_removed"])
                        for src,stamp in survey["first_accepted_print_by_source"].items():
                            first_sources[src] = min(first_sources.get(src,stamp),stamp)
                        role_tickers.update(ticker_roles)
                        event_roles.update(ticker_roles)
                    role_events.update(event_roles)
                    if exam_named:
                        named_exclusion["events"] += 1
                        named_exclusion["tickers"] += len(tickers)
                    reason = None
                    detail = None
                    rows = []
                    category = event_category(event)
                    if len(surveys)==2 and all(s["library_rows"] for s in surveys):
                        counts["events_both_legs_with_library_rows"] += 1
                    try:
                        specs=pair_specs(source,catalog,event,surveys,cutoff,switches)
                        bell=specs[0]["bell_epoch"]
                        lawful_months[utc_date(bell)[:7]] += 1
                        rows=[build_leg(source,spec) for spec in specs]
                    except ValueError as error:
                        reason = str(error).split(":")[0]
                        detail = str(error)
                    if reason:
                        excluded_events[reason] += 1
                        excluded_legs[reason] += len(tickers)
                        exclusions.write(json.dumps({"event_id":event,"tickers":tickers,"reason":reason,
                            "detail":detail},sort_keys=True)+"\n")
                    else:
                        counts["events"] += 1
                        months[utc_date(bell)[:7]] += 1
                        categories[category] += 1
                        if any(row["anchor_fallback_from_june"] for row in rows):
                            switches["anchor_fallback_pairs_emitted"] += 1
                        for row in rows:
                            assert not tune_named_event(row["event_id"])
                            assert all(s["src_role"] != "TUNE_SAMPLE" for s in row["source_rows"])
                            counts["legs"] += 1
                            counts["points"] += len(row["path"])
                            formations[(utc_date(bell)[:7],row["formation_source"])] += 1
                            methods[row["span_method"]] += 1
                            formation_min = row["formation_end_epoch"] if formation_min is None else min(formation_min,row["formation_end_epoch"])
                            bell_max = row["bell_epoch"] if bell_max is None else max(bell_max,row["bell_epoch"])
                            for removed_src,kept_counts in row["cross_source_print_duplicates_removed"].items():
                                for kept_src,number in kept_counts.items():
                                    dedupe_emitted[(removed_src,kept_src)] += number
                            if row["cadence_s"] is not None:
                                cadence_values.append(row["cadence_s"])
                            for source_row in row["source_rows"]:
                                source_output[(source_row["table"],source_row["src"])] += source_row["rows"]
                                emitted_roles[source_row["src_role"] if source_row["src_role"] is not None else "NULL"] += source_row["rows"]
                            zipped.write((json.dumps(row,separators=(",",":"),sort_keys=True,allow_nan=False)+"\n").encode())
                    if counts["tickers_surveyed"] >= next_progress or counts["tickers_surveyed"] == total:
                        elapsed = time.monotonic()-ticker_started
                        rate = counts["tickers_surveyed"]/elapsed
                        report = {"status":"RUNNING","tickers_done":counts["tickers_surveyed"],"tickers_total":total,
                            "tickers_per_second":rate,"elapsed_seconds":elapsed,
                            "eta_seconds":(total-counts["tickers_surveyed"])/rate,
                            "emitted_events":counts["events"],"excluded_events":dict(excluded_events)}
                        report.update(last_event=event,last_ticker=tickers[-1],
                            anchor_fallback_pairs_switched=switches["anchor_fallback_pairs_switched"],
                            cross_source_duplicates_removed=sum(dedupe_survey.values()))
                        progress_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
                        print("PROGRESS "+json.dumps(report),flush=True)
                        if first_thousand is None:
                            first_thousand = report.copy()
                        next_progress = counts["tickers_surveyed"]+args.progress_every
            record_lock(status="HASHING_END",hash_end_started_utc=datetime.now(timezone.utc).isoformat())
            print("VERIFY_END: full source SHA256 scan (shared lock held)",flush=True)
            final_hash = sha256_file(db)
            record_lock(status="VERIFYING_OUTPUT",store_sha256_end=final_hash,
                hash_end_completed_utc=datetime.now(timezone.utc).isoformat())
            print(f"SOURCE_SHA256_END={final_hash}",flush=True)
            receipt["source_snapshot"]["sha256_end"] = final_hash
            after_stat = db.stat()
            after = (after_stat.st_size,after_stat.st_mtime_ns)
            journals = [str(db)+suffix for suffix in ("-wal","-journal") if Path(str(db)+suffix).exists()]
            if final_hash != actual or after != before or journals:
                print("SOURCE_GUARD_FAILURE "+json.dumps({"before":before,"after":after,"journals_present":journals,
                    "sha256_start":actual,"sha256_end":final_hash}),flush=True)
                raise ValueError("SOURCE_CHANGED_DURING_CUT_PARTIAL_NOT_PUBLISHED")
    expected_rows = consolidation["rows_after"]
    surveyed_by_table = Counter()
    for (_,key),number in input_sources.items():
        surveyed_by_table[key.split("/",1)[0]] += number
    if any(surveyed_by_table[table] != expected_rows[table] for table in ("ticks","prints")):
        raise ValueError("SOURCE_CENSUS_DOES_NOT_MATCH_CONSOLIDATION_RECEIPT")
    if emitted_roles["TUNE_SAMPLE"]:
        raise ValueError("EXAM_TAG_LEAK_REFUSE_PUBLICATION")
    partial.replace(output)
    receipt["store_lock"] = dict(lock_state,held_through_receipt_publication=True)
    receipt.update(status="COMPLETE — NATIVE TICK LIBRARY — NOT A BENCH SCORE",counts=dict(counts),
        completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-work_started,
        output=file_binding(output),exclusions_log=file_binding(exclusions_path),
        events_per_bell_month_both_legs_lawful_span=dict(sorted(months.items())),
        events_with_derived_spans_before_path_quality_exclusions=dict(sorted(lawful_months.items())),
        events_per_category=dict(sorted(categories.items())),formation_source_legs_by_bell_month=nested_counts(formations),
        span_method_legs=dict(sorted(methods.items())),excluded_events_by_reason=dict(excluded_events),
        excluded_legs_by_pair_exclusion_reason=dict(excluded_legs),
        exclusion_table=[{"reason":reason,"events":excluded_events[reason],"legs":excluded_legs[reason],"definition":definition}
                         for reason,definition in EXCLUSION_DEFINITIONS.items()],
        anchor_fallback=dict(switches),
        print_dedupe={"rule":DEDUPE_POLICY,"scope_note":"survey covers all timestamps of non-exam-name tickers after tag filtering, counted once; emitted counts cover those legs before bell, including inherited preformation low/anchor initialization, not added to survey counts.",
            "survey_duplicates_removed":sum(dedupe_survey.values()),"survey_removed_source_to_survivor":nested_counts(dedupe_survey),
            "emitted_duplicates_removed":sum(dedupe_emitted.values()),"emitted_removed_source_to_survivor":nested_counts(dedupe_emitted)},
        exclusion_804_by_name={"inclusive_start":TUNE_NAME_START,"inclusive_end":TUNE_NAME_END,**dict(named_exclusion)},
        exclusion_804_union_input_rows=named_exclusion["input_rows"]+role_rows["TUNE_SAMPLE"]-named_exclusion["also_TUNE_SAMPLE_tagged_rows"],
        first_accepted_print_by_source={src:{"ts":stamp,"utc_date":utc_date(stamp)} for src,stamp in sorted(first_sources.items())},
        actual_date_span={"formation_min":utc_date(formation_min) if formation_min is not None else None,"bell_max":utc_date(bell_max) if bell_max is not None else None},
        input_rows_by_event_name_month_source_tag=nested_counts(input_sources),
        input_role_census={role:{"rows":role_rows[role],"tickers":role_tickers[role],"events":role_events[role],
            "rows_excluded_by_role":role_rows[role] if role=="TUNE_SAMPLE" else 0,"rows_consumed_by_emitted_legs":emitted_roles[role],
            "rows_not_consumed_by_emitted_legs":role_rows[role]-emitted_roles[role]} for role in sorted(role_rows)},
        exclusion_804_by_tag={"TUNE_SAMPLE":{"input_rows":role_rows["TUNE_SAMPLE"],"tickers":role_tickers["TUNE_SAMPLE"],"events":role_events["TUNE_SAMPLE"],
            "rows_consumed_by_emitted_legs":emitted_roles["TUNE_SAMPLE"],"rows_not_consumed_by_emitted_legs":role_rows["TUNE_SAMPLE"]-emitted_roles["TUNE_SAMPLE"]}},
        emitted_source_rows=nested_counts(source_output),
        cadence_s={"basis":"distribution of emitted legs' medians of distinct in-span native timestamp gaps",
            "legs":len(cadence_values),"minimum":min(cadence_values) if cadence_values else None,
            "median":statistics.median(cadence_values) if cadence_values else None,"maximum":max(cadence_values) if cadence_values else None},
        first_1000_ticker_rate=first_thousand,source_unchanged=True)
    write_receipt(receipt_path,receipt)
    progress_path.write_text(json.dumps({"status":"COMPLETE","counts":dict(counts),"receipt":str(receipt_path)},indent=2)+"\n",encoding="utf-8")
    return 0


def self_test_consolidated(args):
    self_test_v2()
    import pyarrow as pa
    import pyarrow.parquet as pq
    from unittest.mock import patch

    def probe_lock(path):
        # Mimic CC's open("w") + nonblocking flock, without opening SQLite.
        return subprocess.run([os.sys.executable,"-B","-c",
            "import fcntl,sys\nf=open(sys.argv[1],'w')\ntry: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)\nexcept BlockingIOError: sys.exit(73)",
            str(path)],check=False).returncode

    with tempfile.TemporaryDirectory(prefix="synthetic-consolidated-",dir=Path(args.out).parent) as temporary:
        folder = Path(temporary)
        db = folder/"synthetic.db"
        event = "KXATPMATCH-26APR01SYNTHETIC"
        epoch = 1775001600
        with closing(sqlite3.connect(db)) as connection:
            connection.executescript("CREATE TABLE prints(event TEXT,ticker TEXT,ts REAL,price INTEGER,size REAL,src TEXT,src_role TEXT,obj TEXT);CREATE TABLE ticks(event TEXT,ticker TEXT,ts REAL,bid INTEGER,ask INTEGER,last INTEGER,size REAL,src TEXT,src_role TEXT,obj TEXT);CREATE TABLE cadence(src TEXT,obj TEXT,raw_rows INTEGER,kept_rows INTEGER,distinct_ts INTEGER,median_gap_raw REAL,median_gap_kept REAL);")
            for side,price in (("A",59),("B",43)):
                ticker = event+"-"+side
                for offset,level in ((9,price),(61,price-1),(91,price+1)):
                    connection.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",(event,ticker,epoch+offset,level,2,"spaces_trades","LIBRARY","p"))
                connection.execute("INSERT INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)",(event,ticker,epoch+60,price-1,price+1,None,None,"spaces_ticks","LIBRARY","b"))
            connection.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",(event,event+"-A",epoch+71,1,99,"spaces_trades","TUNE_SAMPLE","p"))
            for table in ("ticks","prints"):
                connection.execute(f"UPDATE {table} SET src_role='OTHER' WHERE ticker=?",(event+"-B",))
            connection.commit()
        metadata = folder/"market.parquet"
        pq.write_table(pa.Table.from_pylist([{"ticker":event+"-A","open_time":datetime.fromtimestamp(epoch-7140,timezone.utc).isoformat(),"settlement_ts":None}]),metadata)
        corpus = folder/"corpus.jsonl"
        corpus.write_text(json.dumps({"event":event,"sched_honest":epoch+240,"sched_src":"SYNTHETIC"})+"\n",encoding="utf-8")
        input_receipt = folder/"source_receipt.json"
        source_hash = sha256_file(db)
        input_receipt.write_text(json.dumps({"sha256":source_hash,"rows_after":{"ticks":2,"prints":7}}),encoding="utf-8")
        test = argparse.Namespace(**vars(args))
        test.db,test.expected_sha256 = db,source_hash
        test.market_metadata,test.corpus_events = metadata,corpus
        test.observed_starts = folder/"absent.db"
        test.consolidation_receipt = input_receipt
        test.out,test.receipt = folder/"library.jsonl.gz",folder/"receipt.json"
        test.store_lock = folder/"synthetic.db.lock"
        test.store_lock.touch()
        lock_inode = test.store_lock.stat().st_ino
        test.verified_source_mtime_ns = None
        test.verified_source_bytes = None
        test.progress_every = 1
        source_hash_calls = []
        original_hash,original_write = sha256_file,write_receipt

        def checked_hash(path):
            if Path(path).resolve() == db.resolve():
                assert probe_lock(test.store_lock) == 73
                source_hash_calls.append(str(path))
            return original_hash(path)

        def checked_receipt(path,body):
            if Path(path) == test.receipt:
                assert probe_lock(test.store_lock) == 73
            return original_write(path,body)

        with redirect_stdout(io.StringIO()), patch(__name__+".sha256_file",side_effect=checked_hash), \
                patch(__name__+".write_receipt",side_effect=checked_receipt):
            assert run_consolidated(test) == 0
        assert len(source_hash_calls) == 2
        assert probe_lock(test.store_lock) == 0
        assert test.store_lock.stat().st_ino == lock_inode
        audit = json.loads((folder/"CUTTER_RUN.lock").read_text())
        assert audit["status"] == "COMPLETE" and not audit["lock_held"]
        assert audit["store_sha256"] == audit["store_sha256_start"] == audit["store_sha256_end"] == source_hash
        assert audit["lock_holder"]["pid"] == os.getpid() and audit["start_time_utc"]
        with gzip.open(test.out,"rt",encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream]
        assert len(rows) == 2 and all(row["grain"] == "TICK" for row in rows)
        assert [row["formation_source"] for row in rows] == ["JUNE_OPEN_PLUS_120","FIRST_BOTH_SIDES_TRADE"]
        assert all(row["formation_end_epoch"] == epoch+60 for row in rows)
        assert all(row["path"][1]["ts"] == epoch+61 for row in rows)
        assert [row["path"][-1]["volume_cum"] for row in rows] == [4,4]
        assert rows[0]["path"][-1]["seen_true_trade_low_cents"] == 58
        report = json.loads(test.receipt.read_text())
        assert report["source_snapshot"]["sha256_start"] == report["source_snapshot"]["sha256_end"] == source_hash
        assert report["store_lock"]["held_through_receipt_publication"]
        assert report["counts"]["events"] == 1
        assert report["exclusion_804_by_tag"]["TUNE_SAMPLE"]["input_rows"] == 1
        assert report["exclusion_804_by_tag"]["TUNE_SAMPLE"]["rows_consumed_by_emitted_legs"] == 0
        assert report["input_role_census"]["TUNE_SAMPLE"]["rows_excluded_by_role"] == 1
        assert all(row["include_other_roles"] for row in rows)
        assert all(s["src_role"]=="OTHER" for s in rows[1]["source_rows"])
        assert report["input_role_census"]["OTHER"]["rows_consumed_by_emitted_legs"] == 4
        assert report["events_per_bell_month_both_legs_lawful_span"] == {"2026-04":1}
        assert report["formation_source_legs_by_bell_month"] == {"2026-04":{"JUNE_OPEN_PLUS_120":1,"FIRST_BOTH_SIDES_TRADE":1}}
        assert sha256_file(db) == source_hash
        # An exception must release the kernel lock and retain a FAILED audit.
        failure = folder/"failure"
        failure.mkdir()
        test.out = failure/"unused.jsonl.gz"
        with redirect_stdout(io.StringIO()):
            try:
                with store_cut_lock(test):
                    assert probe_lock(test.store_lock) == 73
                    raise ValueError("SYNTHETIC_FAILURE")
            except ValueError as error:
                assert str(error) == "SYNTHETIC_FAILURE"
        assert probe_lock(test.store_lock) == 0
        audit = json.loads((failure/"CUTTER_RUN.lock").read_text())
        assert audit["status"] == "FAILED" and not audit["lock_held"]
        # A differing end hash must not publish a library or completion receipt.
        mismatch = folder/"end-hash-mismatch"
        mismatch.mkdir()
        test.out,test.receipt = mismatch/"library.jsonl.gz",mismatch/"receipt.json"
        source_hash_calls.clear()

        def changed_end_hash(path):
            digest = checked_hash(path)
            if Path(path).resolve() == db.resolve() and len(source_hash_calls) == 2:
                return "0"*64
            return digest

        with redirect_stdout(io.StringIO()), patch(__name__+".sha256_file",side_effect=changed_end_hash):
            try:
                run_consolidated(test)
                raise AssertionError("different end hash must fail")
            except ValueError as error:
                assert str(error) == "SOURCE_CHANGED_DURING_CUT_PARTIAL_NOT_PUBLISHED"
        assert len(source_hash_calls) == 2 and not test.out.exists() and not test.receipt.exists()
        assert probe_lock(test.store_lock) == 0
        audit = json.loads((mismatch/"CUTTER_RUN.lock").read_text())
        assert audit["status"] == "FAILED" and audit["store_sha256_start"] == source_hash
        assert audit["store_sha256_end"] == "0"*64 and not audit["lock_held"]
        test.verified_source_bytes = db.stat().st_size
        try:
            run_consolidated(test)
            raise AssertionError("preverified hash bypass must fail")
        except ValueError as error:
            assert str(error) == "CONSOLIDATED_HASH_BYPASS_NOT_ALLOWED"
    print("CONSOLIDATED SELF TEST PASS: v2 dedupe/exam/fallback tests; full cut; two formation sources; schedule precedence; zero emitted TUNE_SAMPLE rows; role census; month split; unchanged source; CC writer excluded through both hashes and receipt; exactly two store hashes; lock released on success/error; end-hash mismatch blocks publication; no preverified bypass")
    return 0


def self_test():
    """Synthetic only: real DB is neither opened nor copied."""
    self_test_v2()
    assert minute_end(60) == 120 and minute_end(59.9) == 60
    survey_a = dict(ticker="PAIR-A",first_trade=61,observed_minutes={120,180,7260},trade_minutes=Counter({120:3,180:3,240:3}))
    survey_b = dict(ticker="PAIR-B",first_trade=121,observed_minutes={180,240},trade_minutes=Counter({120:3,180:3,240:3}))
    assert density_bell([survey_a,survey_b]) == 120
    gap_b = {**survey_b,"trade_minutes":Counter({120:3,240:3,300:3})}
    assert density_bell([survey_a,gap_b]) is None
    with closing(sqlite3.connect(":memory:")) as catalog:
        catalog.executescript("CREATE TABLE market(ticker TEXT,open_epoch REAL,settlement_epoch REAL);CREATE TABLE corpus(event TEXT,body TEXT);CREATE TABLE observed(event TEXT,body TEXT);")
        assert resolve_formations(catalog,[survey_a,survey_b],10000) == [(180,"FIRST_BOTH_SIDES_TRADE",None)]*2
        catalog.execute("INSERT INTO market VALUES('PAIR-A',0,NULL)")
        assert resolve_formations(catalog,[survey_a,survey_b],10000) == [(7260,"JUNE_OPEN_PLUS_120",0),(180,"FIRST_BOTH_SIDES_TRADE",None)]
        assert resolve_bell(catalog,"PAIR",[survey_a,survey_b])[0] == 120
        catalog.execute("INSERT INTO corpus VALUES(?,?)",("PAIR",json.dumps({"sched_honest":9000,"sched_src":"test"})))
        assert resolve_bell(catalog,"PAIR",[survey_a,survey_b])[:2] == (9000,"CORPUS_SCHED_HONEST:test")
        try:
            resolve_formations(catalog,[survey_a,{**survey_b,"first_trade":None}],10000)
            raise AssertionError("missing side trade cannot invent formation")
        except ValueError as error:
            assert str(error) == "UNKNOWN_FORMATION"
    with tempfile.TemporaryDirectory(prefix="range-overlap-synthetic-") as tmp:
        path = Path(tmp)/"synthetic_backup.db"
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        connection.executescript("CREATE TABLE prints(event TEXT,ticker TEXT,ts REAL,price INTEGER,size REAL,src TEXT,src_role TEXT,obj TEXT);CREATE TABLE ticks(event TEXT,ticker TEXT,ts REAL,bid INTEGER,ask INTEGER,last INTEGER,size REAL,src TEXT,src_role TEXT,obj TEXT);CREATE TABLE cadence(src TEXT,obj TEXT,raw_rows INTEGER,kept_rows INTEGER,distinct_ts INTEGER,median_gap_raw REAL,median_gap_kept REAL);")
        spec = dict(event_id="SYNTHETIC", category="ATP_MAIN",leg_id="A",ticker="SYNTHETIC-A",anchor_cents=57,side="LEADER",formation_end_epoch=10,bell_epoch=20)
        connection.executemany("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)", [
            ("SYNTHETIC","SYNTHETIC-A",9,55,2,"spaces_trades","LIBRARY","p"),
            ("SYNTHETIC","SYNTHETIC-A",10.25,57,3,"spaces_trades","LIBRARY","p"),
            ("SYNTHETIC","SYNTHETIC-A",11.125,54,4,"spaces_trades","LIBRARY","p"),
            ("SYNTHETIC","SYNTHETIC-A",11.125,54,4,"spaces_trades","LIBRARY","p"),
            ("SYNTHETIC","SYNTHETIC-A",12,1,99,"book_transition","LIBRARY","p"),
            ("SYNTHETIC","SYNTHETIC-A",13,2,99,"spaces_trades","TUNE_SAMPLE","p"),
            ("SYNTHETIC","SYNTHETIC-A",14,3,99,"spaces_trades",None,"p"),
            ("SYNTHETIC","SYNTHETIC-A",15,4,99,"spaces_trades","OTHER","p"),
            ("SYNTHETIC","SYNTHETIC-A",20,1,99,"spaces_trades","LIBRARY","p")])
        connection.execute("INSERT INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)",("SYNTHETIC","SYNTHETIC-A",10,56,58,99,None,"spaces_ticks","LIBRARY","b"))
        connection.commit()
        assert not inspect_schema(connection)[1]
        leg = build_leg(connection,spec)
        assert [p["window_fraction"] for p in leg["path"]] == [0.025,0.1125]
        assert leg["path"][0]["last_cents"] == 57
        assert leg["path"][-1]["volume_cum"] == 11
        assert leg["path"][-1]["seen_true_trade_low_cents"] == 54
        assert leg["path"][-1]["seen_true_trade_high_cents"] == 57
        assert leg["floor_fraction"] == 0.1125
        assert leg["true_print_count_in_span"] == 3
        connection.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",("SYNTHETIC","SYNTHETIC-A",11.125,53,1,"spaces_trades","LIBRARY","p"))
        ordered=build_leg(connection,spec)
        assert ordered["path"][-1]["last_cents"] == 53
        assert ordered["path"][-1]["seen_true_trade_low_cents"] == 53
        assert ordered["path"][-1]["seen_true_trade_high_cents"] == 57
        assert ordered["path"][-1]["volume_cum"] == 12
        # Later rowid at an earlier native timestamp in the same second wins
        # the closing last/book, without dropping either true-print extreme.
        connection.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",("SYNTHETIC","SYNTHETIC-A",11.05,60,1,"spaces_trades","LIBRARY","p"))
        connection.execute("INSERT INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)",("SYNTHETIC","SYNTHETIC-A",11.125,51,55,None,None,"spaces_ticks","LIBRARY","b"))
        connection.execute("INSERT INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)",("SYNTHETIC","SYNTHETIC-A",11.05,52,56,None,None,"spaces_ticks","LIBRARY","b"))
        ordered=build_leg(connection,spec)
        assert ordered["path"][-1]["ts"] == 11.125
        assert ordered["path"][-1]["last_cents"] == 60
        assert (ordered["path"][-1]["bid_cents"],ordered["path"][-1]["ask_cents"]) == (52,56)
        assert (ordered["path"][-1]["seen_true_trade_low_cents"],ordered["path"][-1]["seen_true_trade_high_cents"]) == (53,60)
        joined=build_leg(connection,{**spec,"include_other_roles":True})
        assert joined["path"][-1]["last_cents"] == 4
        assert joined["path"][-1]["seen_true_trade_low_cents"] == 3
        assert joined["path"][-1]["volume_cum"] == 211
        connection.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",("SYNTHETIC","SYNTHETIC-A",16.2,48,2,"backfill",None,"p"))
        joined=build_leg(connection,{**spec,"include_other_roles":True})
        assert joined["path"][-1]["last_cents"] == 48 and joined["path"][-1]["volume_cum"] == 213
        assert any(s["src"]=="backfill" and s["src_role"] is None for s in joined["source_rows"])
        connection.close()
        with closing(open_snapshot(path)) as readonly:
            try:
                readonly.execute("DELETE FROM prints")
                raise AssertionError("read-only guard must reject writes")
            except sqlite3.OperationalError:
                pass
        # End-to-end synthetic proof: two legs, filed-bounds exclusions,
        # deterministic gzip/receipt, no input database mutation.
        connection = sqlite3.connect(path)
        connection.execute("DELETE FROM prints WHERE price=53")
        connection.execute("INSERT INTO prints SELECT event,'SYNTHETIC-B',ts,price,size,src,src_role,obj FROM prints")
        connection.execute("INSERT INTO ticks SELECT event,'SYNTHETIC-B',ts,bid,ask,last,size,src,src_role,obj FROM ticks")
        connection.commit()
        connection.close()
        truth = {"rows": [{"event_id":"SYNTHETIC","category":"ATP_MAIN","bell_epoch":20,
            "bell_source":"MACHINE_RECEIPT","verified_span":"OK","legA":"A","legB":"B",
            "legA_formation_end_epoch":10,"legB_formation_end_epoch":10,
            "legA_open_postformation_c":57,"legB_open_postformation_c":43},
            {"event_id":"UNKNOWN","verified_span":"UNKNOWN","bell_source":"UNKNOWN"},
            {"event_id":"FUTURE","verified_span":"OK","bell_epoch":4102444800,"bell_source":"MACHINE_RECEIPT"}]}
        truth_path = Path(tmp)/"truth.json"
        truth_path.write_text(json.dumps(truth),encoding="utf-8")
        args = argparse.Namespace(repo_root=ROOT,db=path,truth_table=[truth_path],bell_cutoff="2026-07-11",
            expected_sha256=sha256_file(path),out=Path(tmp)/"SYNTHETIC_PROOF.jsonl.gz",receipt=Path(tmp)/"SYNTHETIC_PROOF_RECEIPT.json")
        with redirect_stdout(io.StringIO()):
            assert run(args) == 0
            first_hashes = sha256_file(args.out),sha256_file(args.receipt)
            assert run(args) == 0
            assert first_hashes == (sha256_file(args.out),sha256_file(args.receipt))
        report = json.loads(args.receipt.read_text(encoding="utf-8"))
        assert report["counts"] == {"events":1,"legs":2,"points":4}
        assert report["bounds_excluded"] == {"UNVERIFIED_SPAN:UNKNOWN":1,"BELL_AFTER_CUTOFF":1}
        assert sha256_file(path) == args.expected_sha256
        legacy = Path(tmp)/"legacy_backup.db"
        with closing(sqlite3.connect(legacy)) as old:
            old.execute("CREATE TABLE prints(event TEXT,ticker TEXT,ts REAL,price INTEGER,size REAL,src TEXT)")
        args.db, args.expected_sha256 = legacy, sha256_file(legacy)
        args.out = Path(tmp)/"MUST_NOT_EXIST_PROOF.jsonl.gz"
        with redirect_stdout(io.StringIO()):
            assert run(args) == 2
        blocked = json.loads(args.receipt.read_text(encoding="utf-8"))
        assert blocked["missing_schema"]["prints"] == ["src_role","obj"]
        assert "ticks" in blocked["missing_schema"] and not args.out.exists()
        receipt_target = args.receipt
        for protected_target in (legacy, truth_path, args.out):
            args.receipt = protected_target
            try:
                run(args)
                raise AssertionError("output alias must fail before schema receipt write")
            except ValueError as error:
                assert str(error) == "OUTPUT_MUST_NOT_ALIAS_INPUT_OR_OTHER_OUTPUT"
        args.receipt = receipt_target
        assert sha256_file(legacy) == args.expected_sha256
    print("SELF TEST PASS — v2 exam name/tag exclusion; source-priority dedupe before density/anchor/path/volume; pair-wide June anchor fallback; second-close rowid order/extrema; true-print volume; preserved non-exam roles; read-only source; deterministic legacy cutter; fail-closed schema")


def self_test_v2():
    event = "KXATPMATCH-26APR18SYNTHETIC"
    assert all(tune_named_event("KXATPMATCH-"+day+"SYNTHETIC") for day in ("26JUL11","26JUL12","26JUL21"))
    assert not any(tune_named_event("KXATPMATCH-"+day+"SYNTHETIC") for day in ("26JUL10","26JUL22"))
    with closing(sqlite3.connect(":memory:")) as source, closing(sqlite3.connect(":memory:")) as catalog:
        source.row_factory = sqlite3.Row
        source.executescript("CREATE TABLE prints(event TEXT,ticker TEXT,ts REAL,price INTEGER,size REAL,src TEXT,src_role TEXT,obj TEXT);CREATE TABLE ticks(event TEXT,ticker TEXT,ts REAL,bid INTEGER,ask INTEGER,last INTEGER,size REAL,src TEXT,src_role TEXT,obj TEXT);CREATE TABLE cadence(src TEXT,obj TEXT,raw_rows INTEGER,kept_rows INTEGER,distinct_ts INTEGER,median_gap_raw REAL,median_gap_kept REAL);")
        catalog.executescript("CREATE TABLE market(ticker TEXT,open_epoch REAL,settlement_epoch REAL);CREATE TABLE corpus(event TEXT,body TEXT);CREATE TABLE observed(event TEXT,body TEXT);")
        catalog.execute("INSERT INTO corpus VALUES(?,?)",(event,json.dumps({"sched_honest":300,"sched_src":"SYNTHETIC"})))
        for side in ("A","B"):
            ticker = event+"-"+side
            catalog.execute("INSERT INTO market VALUES(?,?,NULL)",(ticker,-7200))
            source.execute("INSERT INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)",(event,ticker,1,50,52,None,None,"validation4_bin","LIBRARY",None))
            source.execute("INSERT INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)",(event,ticker,180,1,2,None,None,"spaces_ticks","TUNE_SAMPLE",None))
            for ts,price in ((100,60),(160,58),(220,55)):
                for src,offset in (("spaces_trades",0.2),("public_tape",0.1),("backfill",0.8)):
                    source.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",(event,ticker,ts+offset,price,2,src,None,None))
            source.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",(event,ticker,170,1,99,"spaces_trades","TUNE_SAMPLE",None))
            source.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",(event,ticker,175,2,99,"book_transition",None,None))
        surveys = [survey_ticker(source,event+"-"+side,True) for side in ("A","B")]
        assert all(s["trade_minutes"] == Counter({120:1,180:1,240:1}) for s in surveys)
        assert density_bell(surveys) is None  # Three source copies must not manufacture density.
        assert all(s["duplicates_removed"] == Counter({("public_tape","spaces_trades"):3,("backfill","spaces_trades"):3}) for s in surveys)
        switched = Counter()
        specs = pair_specs(source,catalog,event,surveys,date(2026,7,11),switched)
        assert switched == Counter(anchor_fallback_pairs_switched=1)
        assert all(s["formation_end_epoch"]==120 and s["formation_source"]=="FIRST_BOTH_SIDES_TRADE" and s["anchor_cents"]==60 for s in specs)
        assert all(s["formation_before_anchor_fallback"]=={"epoch":60,"source":"JUNE_OPEN_PLUS_120"} for s in specs)
        for spec in specs:
            row = build_leg(source,spec)
            assert row["true_print_count_in_span"]==2 and row["path"][-1]["volume_cum"]==4
            assert row["path"][-1]["seen_true_trade_low_cents"]==55
            assert (row["path"][-1]["bid_cents"],row["path"][-1]["ask_cents"])==(50,52)
            assert all(r["src_role"] != "TUNE_SAMPLE" for r in row["source_rows"])
        try:
            pair_specs(source,catalog,"KXATPMATCH-26JUL11SYNTHETIC",surveys,date(2026,7,11))
            raise AssertionError("exam name must override an old bell and all row tags")
        except ValueError as error:
            assert str(error)=="TUNE_SAMPLE_EVENT_NAME"
        censused = survey_ticker(source,event+"-A",True,census_only=True)
        assert sum(censused["counts"].values())==13 and censused["first_trade"] is None
        # Single-source same-key multiplicity is not evidence of cross-source duplication.
        rows = [dict(rowid=i,ts=1.2,price=50,size=1,src="public_tape") for i in (1,2)]
        assert len(list(dedupe_print_rows(rows)))==2
        rows.append(dict(rowid=3,ts=1.3,price=50,size=1,src="backfill"))
        assert list(dedupe_print_rows(rows))[0]["rowid"]==2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--db", type=Path)
    parser.add_argument("--truth-table", type=Path, action="append")
    parser.add_argument("--bell-cutoff", default="2026-07-11", help="Inclusive UTC bell date, not ticker date")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--out", type=Path, default=ROOT/"arb-executor/data/durable/RANGE_OVERLAP_LIBRARY_TICKS_PROOF.jsonl.gz")
    parser.add_argument("--receipt", type=Path, default=ROOT/"arb-executor/data/durable/RANGE_OVERLAP_LIBRARY_TICKS_PROOF_RECEIPT.json")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--consolidated",action="store_true")
    parser.add_argument("--market-metadata",type=Path)
    parser.add_argument("--corpus-events",type=Path)
    parser.add_argument("--observed-starts",type=Path)
    parser.add_argument("--consolidation-receipt",type=Path)
    parser.add_argument("--store-lock",type=Path,help="Existing CC writer lock; default is repo-root/arb-executor/state/subsecond_store.db.lock (before resolving the DB symlink)")
    parser.add_argument("--verified-source-mtime-ns",type=int)
    parser.add_argument("--verified-source-bytes",type=int)
    parser.add_argument("--progress-every",type=int,default=1000)
    parser.add_argument("--prior-art-receipt",type=Path)
    parser.add_argument("--write-prior-art",type=Path)
    parser.add_argument("--self-test-consolidated",action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.write_prior_art:
        write_receipt(args.write_prior_art,prior_art_bundle(args.repo_root,date.fromisoformat(args.bell_cutoff)))
        return 0
    if args.self_test_consolidated:
        return self_test_consolidated(args)
    if args.db is None:
        parser.error("--db is required")
    if args.consolidated:
        if args.progress_every <= 0:
            parser.error("--progress-every must be positive")
        args.market_metadata = args.market_metadata or args.repo_root/"arb-executor/data/durable/g9_metadata.parquet"
        args.corpus_events = args.corpus_events or args.repo_root/"arb-executor/state/corpus_events_v2.jsonl"
        args.observed_starts = args.observed_starts or args.repo_root/"arb-executor/state/observed_starts.db"
        args.consolidation_receipt = args.consolidation_receipt or args.repo_root/"artifacts/review_mirror/CONSOLIDATION_RECEIPT_20260904.json"
        return run_consolidated(args)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
