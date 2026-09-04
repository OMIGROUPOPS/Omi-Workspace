#!/usr/bin/env python3
"""Cut range-overlap rows from a static recorder-store snapshot, never ingest it.

The existing ORDER 1 row contract and filed truth-table bounds are inherited.
No bell, formation, price, volume, or chronology is guessed.  --self-test uses
only a temporary synthetic SQLite database.  The live subsecond_store.db name
is deliberately refused while the consolidation is in progress.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import closing, redirect_stdout
from datetime import date, datetime, timezone
import gzip
import hashlib
import heapq
import itertools
import io
import json
import math
from pathlib import Path
import sqlite3
import statistics
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/"
TRUTH_DEFAULT = AUDIT + "W1_GROUND_TRUTH_TABLE.json"
TRUE_PRINT_SOURCES = ("public_tape", "ws_log", "spaces_trades")
SCHEMA = {
    "prints": ("event", "ticker", "ts", "price", "size", "src", "src_role", "obj"),
    "ticks": ("event", "ticker", "ts", "bid", "ask", "last", "size", "src", "src_role", "obj"),
    "cadence": ("src", "obj", "raw_rows", "kept_rows", "distinct_ts", "median_gap_raw", "median_gap_kept"),
}
PATH_FIELDS = ("seen_true_trade_low_cents", "seen_true_trade_high_cents", "last_cents", "bid_cents", "ask_cents", "volume_cum")
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


def open_snapshot(path):
    path = Path(path).resolve(strict=True)
    if path.name == "subsecond_store.db":
        raise ValueError("LIVE_STORE_REFUSED: use a named static backup, not subsecond_store.db")
    for suffix in ("-wal", "-journal"):
        if Path(str(path) + suffix).exists():
            raise ValueError("SNAPSHOT_HAS_JOURNAL:" + str(path))
    connection = sqlite3.connect(path.as_uri() + "?mode=ro&immutable=1", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def observations(connection, spec):
    params = (spec["ticker"], spec["bell_epoch"])
    # NULL roles are not silently promoted into LIBRARY. SQL != excludes NULL.
    books = connection.execute("SELECT rowid,ts,bid,ask,src,src_role,obj FROM ticks WHERE ticker=? AND ts<? AND src_role!='TUNE_SAMPLE' ORDER BY ts,rowid", params)
    trades = connection.execute("SELECT rowid,ts,price,size,src,src_role,obj FROM prints WHERE ticker=? AND ts<? AND src_role!='TUNE_SAMPLE' AND src IN (?,?,?) ORDER BY ts,rowid", params + TRUE_PRINT_SOURCES)
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
    for ts, grouped in itertools.groupby(observations(connection, spec), key=lambda row: row[0]):
        group = list(grouped)
        # A store rowid is ingestion order, not proof of same-timestamp order.
        prices = {finite(r["price"]) for _, table, _, r in group if table == "prints"}
        books = {(finite(r["bid"]), finite(r["ask"])) for _, table, _, r in group if table == "ticks"}
        if len(prices) > 1 or len(books) > 1:
            raise ValueError("AMBIGUOUS_SAME_TIMESTAMP_ORDER:" + spec["ticker"] + "@" + str(ts))
        if None in prices:
            raise ValueError("MISSING_TRUE_PRINT_PRICE:" + spec["ticker"])
        for _, table, _, observation in group:
            source_counts[(table, observation["src"], observation["src_role"])] += 1
            if observation["obj"]:
                objects.add(observation["obj"])
            if table == "ticks":
                bid, ask = finite(observation["bid"]), finite(observation["ask"])
                continue
            price = finite(observation["price"])
            low = price if low is None else min(low, price)
            last = price
            if ts < formation:
                continue
            size = finite(observation["size"])
            if size is None or size < 0:
                raise ValueError("MISSING_OR_INVALID_TRUE_PRINT_SIZE:" + spec["ticker"])
            volume += size
            trade_count += 1
            if first_trade is None:
                first_trade = {"timestamp_epoch": ts, "price_cents": compact(price)}
            high = price if high is None else max(high, price)
            if floor is None or price < floor:
                floor, floor_epoch = price, ts
        if ts < formation:
            continue
        timestamp_groups += 1
        row_times.append(ts)
        signature = (low, high, last, bid, ask, volume)
        if signature == previous_signature:
            continue
        previous_signature = signature
        path.append({"window_fraction": (ts - formation) / (bell - formation),
                     **{key: compact(value) for key, value in zip(PATH_FIELDS, signature)}})
    if not path or first_trade is None:
        raise ValueError("NO_IN_SPAN_TRUE_PRINT:" + spec["ticker"])
    cadence = []
    for obj in sorted(objects):
        cadence.extend(dict(row) for row in connection.execute("SELECT * FROM cadence WHERE obj=? ORDER BY src", (obj,)))
    gaps = [b-a for a,b in zip(row_times, row_times[1:])]
    # Output is the old row shape plus named source/cadence/bound disclosures.
    return {**spec, "floor_fraction": (floor_epoch-formation)/(bell-formation),
        "path": path, "grain": "NATIVE_TICK", "source": "RECORDER_STORE_STATIC_SNAPSHOT",
        "licensed_layers": ["MACRO", "MICRO"], "micro_micro_licensed": False,
        "first_true_trade": first_trade,
        "source_rows": [{"table": t, "src": src, "src_role": role, "rows": n}
                        for (t,src,role),n in sorted(source_counts.items())],
        "cadence": {"unit": "seconds", "resampling": "NONE", "timestamp_groups_in_span": timestamp_groups,
                    "minimum_gap": min(gaps) if gaps else None, "median_gap": statistics.median(gaps) if gaps else None,
                    "maximum_gap": max(gaps) if gaps else None, "source_objects": cadence,
                    "objects_without_cadence": sorted(objects-{r["obj"] for r in cadence}),
                    "same_timestamp_policy": "Group equal native timestamps only; reject conflicting prints/books without sequence proof"},
        "true_print_count_in_span": trade_count,
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
            "roles": "Only src_role != TUNE_SAMPLE; NULL src_role is excluded rather than inferred from name.",
            "side": "LEADER if inherited filed post-formation anchor_cents >= 50, otherwise UNDERDOG. The scoreboard's first-tick pair anchors are a separate causal read.",
            "low": "Running minimum of accepted prints.price initialized through formation, identical to ORDER 1's prior-low convention; subsequent true prints update it.",
            "high": "Running maximum of accepted prints.price from formation; never ticks.last or book_transition.",
            "last": "Most recent accepted prints.price at or before native timestamp; no midpoint, anchor, or ticks.last fallback.",
            "book": "ticks.bid and ticks.ask in stored cents, carried between book observations; missing sides remain null.",
            "volume": "Running sum of accepted prints.size at formation <= ts < bell; missing/negative sizes exclude the leg. Stored zero sizes remain zero and are not estimated.",
            "true_print_sources": TRUE_PRINT_SOURCES,
            "excluded_inferred_source": "book_transition is a changed-last surrogate, not a true trade; never authors low/high/last/volume.",
            "change_point": "Every native timestamp where any of the six fields changes; no minute rounding and no synthetic formation tick. Equal-timestamp conflicts exclude the leg instead of imposing ingestion order.",
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


def self_test():
    """Synthetic only: real DB is neither opened nor copied."""
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
            ("SYNTHETIC","SYNTHETIC-A",20,1,99,"spaces_trades","LIBRARY","p")])
        connection.execute("INSERT INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)",("SYNTHETIC","SYNTHETIC-A",10,56,58,99,None,"spaces_ticks","LIBRARY","b"))
        connection.commit()
        assert not inspect_schema(connection)[1]
        leg = build_leg(connection,spec)
        assert [p["window_fraction"] for p in leg["path"]] == [0,0.025,0.1125]
        assert leg["path"][0]["last_cents"] == 55
        assert leg["path"][-1]["volume_cum"] == 11
        assert leg["path"][-1]["seen_true_trade_low_cents"] == 54
        assert leg["path"][-1]["seen_true_trade_high_cents"] == 57
        assert leg["floor_fraction"] == 0.1125
        assert leg["true_print_count_in_span"] == 3
        connection.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",("SYNTHETIC","SYNTHETIC-A",11.125,53,1,"spaces_trades","LIBRARY","p"))
        try:
            build_leg(connection,spec)
            raise AssertionError("same-timestamp conflict must fail")
        except ValueError as error:
            assert str(error).startswith("AMBIGUOUS_SAME_TIMESTAMP_ORDER")
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
        assert report["counts"] == {"events":1,"legs":2,"points":6}
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
    print("SELF TEST PASS — synthetic native fractions; pre-formation low/last; high reset; true-print volume; bell/tune/null-role/inferred-print exclusion; same-timestamp conflict; read-only snapshot; full cutter deterministic x2; legacy-schema fail-closed")


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
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.db is None:
        parser.error("--db must name a static snapshot; the live store is forbidden")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
