#!/usr/bin/env python3
"""Exact cumulative print counts on their own accepted-print-second grid.

Read-only SQLite, streamed one ticker at a time under the cutter/CC store lock.
Import the hash-bound cutter's accepted_print_rows, rather than recoding dedupe.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import gzip
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import sqlite3
import sys
import time

sys.dont_write_bytecode = True


def load_cutter(path):
    spec = importlib.util.spec_from_file_location("bound_tick_cutter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def count_leg(connection, leg, cutter, removed):
    if cutter.tune_named_event(leg["event_id"]):
        raise ValueError("TUNE_SAMPLE_EVENT_IN_LIBRARY:" + leg["event_id"])
    formation, bell = leg["formation_end_epoch"], leg["bell_epoch"]
    if leg["grain"] != "TICK" or not formation < bell:
        raise ValueError("INVALID_FILED_SPAN_OR_GRAIN:" + leg["ticker"])
    # Do not apply an SQL lower bound: the cutter dedupes a whole second before
    # testing each surviving print's native timestamp against formation.
    rows = cutter.accepted_print_rows(connection, leg["ticker"],
        joined=leg.get("include_other_roles", False), before=bell, removed=removed)
    points = iter(leg["path"])
    point = next(points, None)
    count, volume = 0, 0
    for second, group in itertools.groupby(rows, key=lambda row: math.floor(row["ts"])):
        # Still independently verify the original price/volume grid. A print
        # need not change that grid to appear in the separate count series.
        while point is not None and math.floor(point["ts"]) < second:
            if volume != point["volume_cum"]:
                raise ValueError("POINT_VOLUME_MISMATCH:" + leg["ticker"] + ":" + str(point["ts"]))
            point = next(points, None)
        previous = count
        for row in sorted(group, key=lambda row: row["rowid"]):
            if row["event"] != leg["event_id"] or row["src_role"] == "TUNE_SAMPLE":
                raise ValueError("SOURCE_IDENTITY_OR_EXAM_VIOLATION:" + leg["ticker"])
            if row["ts"] >= formation:
                size = cutter.finite(row["size"])
                if size is None or size < 0:
                    raise ValueError("INVALID_PRINT_SIZE:" + leg["ticker"])
                count += 1
                volume += size
        if count > previous:
            yield dict(ticker=leg["ticker"], second=second, true_print_count_cum=count)
    while point is not None:
        if volume != point["volume_cum"]:
            raise ValueError("POINT_VOLUME_MISMATCH:" + leg["ticker"] + ":" + str(point["ts"]))
        point = next(points, None)
    expected = leg["true_print_count_in_span"]
    if count != expected:
        raise ValueError(f"FINAL_COUNT_MISMATCH:{leg['ticker']}:source={count}:library={expected}")


def verify(sidecar, library):
    legs = points = total = 0
    with gzip.open(sidecar, "rt", encoding="utf-8") as source, gzip.open(library, "rt", encoding="utf-8") as grid:
        groups = iter(itertools.groupby((json.loads(line) for line in source), key=lambda row: row["ticker"]))
        for line in grid:
            leg = json.loads(line)
            ticker, rows = next(groups)
            if ticker != leg["ticker"]:
                raise ValueError("SIDECAR_LEG_IDENTITY_MISMATCH")
            previous, previous_second = 0, None
            for row in rows:
                second = row["second"]
                if set(row) != {"ticker", "second", "true_print_count_cum"}:
                    raise ValueError("SIDECAR_SCHEMA_MISMATCH")
                if not isinstance(second, int) or (previous_second is not None and second <= previous_second):
                    raise ValueError("SIDECAR_SECONDS_NOT_STRICTLY_INCREASING")
                if not math.floor(leg["formation_end_epoch"]) <= second < leg["bell_epoch"]:
                    raise ValueError("SIDECAR_SECOND_OUTSIDE_SPAN")
                count = row["true_print_count_cum"]
                if isinstance(count, bool) or not isinstance(count, int) or count <= previous:
                    raise ValueError("SIDECAR_COUNT_NOT_STRICTLY_INCREASING_INTEGER")
                previous, previous_second = count, second
                points += 1
            if previous != leg["true_print_count_in_span"]:
                raise ValueError("SIDECAR_FINAL_COUNT_MISMATCH:" + leg["ticker"])
            total += previous
            legs += 1
        if next(groups, None) is not None:
            raise ValueError("SIDECAR_EXTRA_ROW")
    return dict(legs_checked=legs, rows_checked=points, final_count_matches=legs,
                final_count_mismatches=0, total_true_prints_in_spans=total,
                grid_identity="Every library leg, in library order; own floor(native ts) seconds with accepted in-span prints; independent of library change points")


def run(args, cutter):
    receipt_source = json.loads(args.library_receipt.read_text(encoding="utf-8"))
    if cutter.sha256_file(args.cutter) != receipt_source["builder"]["sha256"]:
        raise ValueError("CUTTER_HASH_NOT_BOUND_TO_LIBRARY")
    library_sha = cutter.sha256_file(args.library)
    if library_sha != args.library_sha256:
        raise ValueError("LIBRARY_HASH_MISMATCH")
    args.expected_sha256 = receipt_source["source_snapshot"]["sha256"]
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise ValueError("REQUIRES_NICE_10")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    receipt_path = args.out.with_name("RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS_RECEIPT.json")
    partial = args.out.with_name(args.out.name + ".partial")
    if any(path.exists() for path in (args.out, receipt_path, partial)):
        raise ValueError("REFUSE_TO_OVERWRITE_SIDECAR_OUTPUT")
    with cutter.store_cut_lock(args) as (lock_state, record_lock):
        db = args.db.resolve(strict=True)
        original_stat = (db.stat().st_size, db.stat().st_mtime_ns)
        record_lock(status="HASHING_START")
        start_sha = cutter.sha256_file(db)
        print("SOURCE_SHA256_START=" + start_sha, flush=True)
        record_lock(status="EXTRACTING", store_sha256=start_sha, store_sha256_start=start_sha)
        if start_sha != args.expected_sha256:
            raise ValueError("STORE_NOT_LIBRARY_SNAPSHOT:" + start_sha)
        removed, categories = Counter(), Counter()
        leg_count = row_count = 0
        started = time.monotonic()
        with closing(cutter.open_snapshot(db, consolidated=True)) as connection:
            with partial.open("xb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as output:
                with gzip.open(args.library, "rt", encoding="utf-8") as source:
                    for line in source:
                        leg = json.loads(line)
                        for row in count_leg(connection, leg, cutter, removed):
                            output.write((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode())
                            row_count += 1
                        leg_count += 1
                        categories[leg["category"]] += 1
                        if leg_count % 100 == 0:
                            elapsed = time.monotonic() - started
                            print("PROGRESS " + json.dumps(dict(legs_done=leg_count, rows_written=row_count,
                                last_ticker=leg["ticker"], elapsed_seconds=elapsed,
                                legs_per_second=leg_count/elapsed)), flush=True)
        record_lock(status="VERIFYING_SIDECAR")
        verification = verify(partial, args.library)
        if verification["legs_checked"] != leg_count or verification["rows_checked"] != row_count:
            raise ValueError("SERIALIZED_COUNTS_MISMATCH")
        record_lock(status="HASHING_END")
        end_sha = cutter.sha256_file(db)
        print("SOURCE_SHA256_END=" + end_sha, flush=True)
        record_lock(store_sha256_end=end_sha)
        if start_sha != end_sha or original_stat != (db.stat().st_size, db.stat().st_mtime_ns):
            raise ValueError("SOURCE_CHANGED")
        if any(Path(str(db) + suffix).exists() for suffix in ("-wal", "-journal")):
            raise ValueError("SOURCE_HAS_JOURNAL")
        receipt = dict(schema="TICK_LIBRARY_EXACT_PRINT_COUNTS_V2", status="VERIFIED",
            library=dict(path=str(args.library), sha256=library_sha,
                         receipt_sha256=cutter.sha256_file(args.library_receipt)),
            cutter=dict(path=str(args.cutter), sha256=cutter.sha256_file(args.cutter),
                        inherited_functions=["accepted_print_rows", "dedupe_print_rows", "store_cut_lock", "open_snapshot"]),
            builder=dict(path=str(Path(__file__)), sha256=cutter.sha256_file(Path(__file__))),
            store=dict(path=str(db), sha256_start=start_sha, sha256_end=end_sha,
                       bytes=original_stat[0], read_only=True, hash_scans=2),
            store_lock={**lock_state, "held_through_receipt_publication": True},
            counts=verification, legs_by_category=dict(sorted(categories.items())),
            dedupe_removed_before_bell={a+" -> "+b: n for (a,b),n in sorted(removed.items())},
            rules=dict(span="Use every library leg's exact formation_end_epoch <= accepted native ts < bell_epoch; no span rederivation",
                exam="Reject July 11-21 event-name dates; never consume TUNE_SAMPLE-tagged rows",
                dedupe=cutter.DEDUPE_POLICY,
                count="Number of accepted true-print rows, including zero-size trades; never volume, book changes, or changed prices",
                grid="One row (ticker, second, true_print_count_cum) for every floor(native ts) second with accepted in-span prints, including zero-size prints and seconds absent from the library path. Library grid unchanged.",
                gate_join="Latest sidecar second <= gate epoch; zero before the first accepted print second. Operator-authorized discrete second clock, not subsecond arrival ordering.",
                final_check="Every leg's last sidecar count must equal both the streamed source total and true_print_count_in_span",
                volume_check="Cumulative accepted size equals volume_cum at every original library point",
                dedupe_count_scope="All accepted pre-bell rows for emitted tickers, including pre-formation, exactly as the cutter queries them"),
            output=dict(path=str(args.out), bytes=partial.stat().st_size, sha256=cutter.sha256_file(partial)),
            completed_utc=datetime.now(timezone.utc).isoformat())
        partial.replace(args.out)
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("VERIFIED " + json.dumps(verification, sort_keys=True), flush=True)
        print("SIDECAR_SHA256=" + receipt["output"]["sha256"], flush=True)
        print("RECEIPT_SHA256=" + cutter.sha256_file(receipt_path), flush=True)


def self_test(cutter):
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE prints(event,ticker,ts,price,size,src,src_role,obj)")
    event, ticker = "KXATPMATCH-26JUN01ABCDEF", "KXATPMATCH-26JUN01ABCDEF-ABC"
    for ts, price, size, src, tag in ((99.5,20,3,"spaces_trades","LIBRARY"),
        (100.1,21,4,"backfill","LIBRARY"),(100.8,21,4,"spaces_trades","LIBRARY"),
        (100.9,21,4,"spaces_trades","LIBRARY"),(101,21,0,"spaces_trades","LIBRARY"),
        (101,21,9,"spaces_trades","TUNE_SAMPLE"),(102,22,1,"spaces_trades","LIBRARY"),
        (102,22,1,"spaces_trades","LIBRARY"),(103,23,5,"book_transition","LIBRARY"),
        (103.5,22,0,"spaces_trades","LIBRARY"),(104,20,2,"spaces_trades","LIBRARY")):
        c.execute("INSERT INTO prints VALUES(?,?,?,?,?,?,?,?)",(event,ticker,ts,price,size,src,tag,None))
    leg=dict(event_id=event,ticker=ticker,leg_id="ABC",grain="TICK",include_other_roles=True,
        formation_end_epoch=100,bell_epoch=104,true_print_count_in_span=5,
        path=[dict(ts=100.9,volume_cum=4),dict(ts=102,volume_cum=6)])
    removed=Counter()
    out=list(count_leg(c,leg,cutter,removed))
    assert [r["true_print_count_cum"] for r in out] == [1,2,4,5]
    assert [r["second"] for r in out] == [100,101,102,103]
    assert removed == Counter({("backfill","spaces_trades"):1,("spaces_trades","spaces_trades"):1})
    bad={**leg,"event_id":"KXATPMATCH-26JUL12ABCDEF"}
    try:
        list(count_leg(c,bad,cutter,Counter()))
        raise AssertionError("exam accepted")
    except ValueError as e:
        assert str(e).startswith("TUNE_SAMPLE_EVENT_IN_LIBRARY")
    print("SELF-TEST PASS: exact counts; source-priority dedupe; same-source repeats; zero-size prints between/after library points; exam name/tag; exclusive bell; independent print-second grid")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cutter",type=Path,default=Path(__file__).with_name("build_range_overlap_library_ticks.py"))
    p.add_argument("--library",type=Path)
    p.add_argument("--library-receipt",type=Path)
    p.add_argument("--library-sha256")
    p.add_argument("--db",type=Path)
    p.add_argument("--store-lock",type=Path)
    p.add_argument("--repo-root",type=Path,default=Path("/root/Omi-Workspace"))
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--verify-only",action="store_true")
    args=p.parse_args()
    cutter=load_cutter(args.cutter)
    if args.self_test:
        self_test(cutter)
    elif args.verify_only:
        print(json.dumps(verify(args.out,args.library),indent=2))
    else:
        try:
            run(args,cutter)
        except BaseException:
            if args.out and args.out.parent.is_dir():
                args.out.with_name("PRINT_COUNTS_RUN.exit").write_text("1\n",encoding="ascii")
            raise
        else:
            args.out.with_name("PRINT_COUNTS_RUN.exit").write_text("0\n",encoding="ascii")


if __name__ == "__main__":
    main()
