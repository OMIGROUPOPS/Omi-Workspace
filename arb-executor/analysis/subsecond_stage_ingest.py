#!/usr/bin/env python3
"""P2 — SUBSECOND CONSOLIDATION, staged-file ingest (2026-09-05, operator-approved method change).

Replaces the per-object streamed ingest of subsecond_consolidate.py for the
spaces_ticks source (run 1 = rclone cat per object, run 2 = persistent SigV4
GET per object; both stopped cleanly — ingest_log is the resume key and stays
valid). Method here:
  * objects are staged to /root/tick_stage/<prefix>/ by a parallel rclone copy
    (month-sized batches, deleted after the batch is receipted); this script
    reads the staged .csv.gz files, verifies each file's md5 against the
    bucket listing (etag) and records key + etag in ingest_log;
  * PRAGMA journal_mode=WAL, synchronous=OFF during the load;
  * UNIQUE INDEX t_uq ON ticks(ticker, ts, IFNULL(bid,-1), IFNULL(ask,-1),
    IFNULL(last,-1), IFNULL(size,-1), src) created before the load (--prep) —
    the operator's key with NULL treated as a value, since plain UNIQUE treats
    NULLs as distinct; rows go in with INSERT OR IGNORE in batches of
    >= --batch-rows per transaction (transactions close on object boundaries,
    so an object is either fully in the store with its ingest_log row or not
    at all); no per-row dedupe lookups;
  * objects already in ingest_log are skipped, not re-read;
  * row semantics unchanged from subsecond_consolidate.py: book-transition
    grade — one row whenever (bid_1, ask_1, last_trade) changes; boundary
    2026-03-20 <= ts(UTC) < 2026-07-26 per row; objects named 26JUL26+ are
    skipped entirely; src_role TUNE_SAMPLE for 26JUL11..26JUL21, else LIBRARY;
    ts is absolute UTC epoch seconds parsed from the ET 12-hour ts_et string.
Cross-source duplicates are no longer dropped (src is part of the unique key);
the receipt reports the validation4_bin ∩ spaces_ticks overlap instead.
prints keeps no UNIQUE key: identical trade rows inside one object are
distinct prints at 1 s resolution, so a UNIQUE key would delete data
(spaces_trades was already complete before this method started).
No cron is installed by this file.
"""
import argparse, csv, gzip, hashlib, io, json, os, re, sqlite3, statistics, sys, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "state/subsecond_store.db"
MON = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}

ap = argparse.ArgumentParser()
ap.add_argument("--stage-dir", default="/root/tick_stage")
ap.add_argument("--prefix", default="ticks", help="ticks (→ ticks table) or trades (→ prints table)")
ap.add_argument("--listing", default="/tmp/spaces_ticks_lsjson.json", help="rclone lsjson -R --hash output for the prefix (the census listing)")
ap.add_argument("--month", default="", help="only objects whose name date is in this YYYY-MM (batch label)")
ap.add_argument("--boundary-start", default="2026-03-20")
ap.add_argument("--boundary-end", default="2026-07-25", help="inclusive (UTC date)")
ap.add_argument("--tune-start", default="26JUL11")
ap.add_argument("--tune-end", default="26JUL21")
ap.add_argument("--batch-rows", type=int, default=50000)
ap.add_argument("--prep", action="store_true", help="create the UNIQUE index / columns and exit")
ap.add_argument("--ingest", action="store_true")
ap.add_argument("--progress", default="/tmp/stage_ingest_progress.json")
ap.add_argument("--receipt", default="", help="write the consolidation receipt json here")
ap.add_argument("--no-hash", action="store_true")
ap.add_argument("--limit", type=int, default=0)
args = ap.parse_args()
T_LO = datetime.fromisoformat(args.boundary_start).replace(tzinfo=timezone.utc).timestamp()
T_HI = datetime.fromisoformat(args.boundary_end).replace(tzinfo=timezone.utc).timestamp() + 86400.0
T0 = time.time()

def name_date(tk):
    m = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", tk)
    if not m or m.group(2) not in MON: return None
    return (2000 + int(m.group(1)), MON[m.group(2)], int(m.group(3)))
def key_of(code): return (2000 + int(code[:2]), MON[code[2:5]], int(code[5:7]))
TUNE_LO, TUNE_HI = key_of(args.tune_start), key_of(args.tune_end)
B_END_KEY = tuple(int(x) for x in args.boundary_end.split("-"))
def role_of(tk):
    d = name_date(tk); return "TUNE_SAMPLE" if d and TUNE_LO <= d <= TUNE_HI else "LIBRARY"
def skip_object(tk):
    d = name_date(tk); return bool(d and d > B_END_KEY)
def med(xs): return statistics.median(xs) if xs else None

# ts_et "YYYY-MM-DD HH:MM:SS AM/PM" (America/New_York) → UTC epoch. Equivalent to
# datetime.strptime(s, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp();
# the (date, hour) base is cached so the per-row cost is a few int() calls.
_hour_base = {}
def ep_et(s):
    try:
        k = s[:13]; ap_ = s[20:22]
        base = _hour_base.get((k, ap_))
        if base is None:
            hh = int(s[11:13]) % 12 + (12 if ap_ == "PM" else 0)
            if ap_ not in ("AM", "PM"): raise ValueError(s)
            base = datetime(int(s[0:4]), int(s[5:7]), int(s[8:10]), hh, tzinfo=ET).timestamp()
            if len(_hour_base) > 200000: _hour_base.clear()
            _hour_base[(k, ap_)] = base
        return base + int(s[14:16]) * 60 + int(s[17:19])
    except (ValueError, IndexError):
        try: return datetime.strptime(s, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
        except ValueError: return None

import fcntl
_lock = open(str(DB) + ".lock", "w")
t_l = time.time(); fcntl.flock(_lock, fcntl.LOCK_EX)   # blocks while the nightly consolidator (cron 04:35 ET) holds it
if time.time() - t_l > 1: print("waited %.0f s for subsecond_store.db.lock" % (time.time() - t_l))
con = sqlite3.connect(DB, timeout=600)
con.execute("PRAGMA journal_mode=WAL")
con.execute("PRAGMA synchronous=OFF")
con.execute("PRAGMA cache_size=-60000")
con.execute("PRAGMA temp_store=FILE")

if args.prep:
    # NULL is distinct under a plain UNIQUE index (size is NULL on every tick row; bid/ask/last
    # can be NULL), which would let within-object duplicates through. IFNULL(x,-1) makes the
    # operator's key (ticker, ts, bid, ask, last, size, src) behave as a real uniqueness key.
    cur = con.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name='t_uq'").fetchone()
    if not cur or "IFNULL" not in cur[0]:
        con.execute("DROP INDEX IF EXISTS t_uq")
        con.execute("CREATE UNIQUE INDEX t_uq ON ticks(ticker, ts, IFNULL(bid,-1), IFNULL(ask,-1), IFNULL(last,-1), IFNULL(size,-1), src)")
    for ix in ("t_tk", "t_key", "p_key"):   # redundant under t_uq / p_tk; recreated once by a nightly run → drop again
        con.execute("DROP INDEX IF EXISTS " + ix)
    con.execute("CREATE INDEX IF NOT EXISTS t_ev ON ticks(event, ts)")
    con.commit()
    print("prep done; indexes:", [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name IN ('ticks','prints')")])

stats = defaultdict(int)
def progress(src, i, n, note=""):
    el = time.time() - T0
    d = {"src": src, "batch": args.month, "done": i, "total": n, "elapsed_s": round(el, 1), "stats": dict(stats), "note": note}
    if el > 0 and stats["objects"]:
        d["objects_per_hour"] = round(stats["objects"] * 3600 / el, 1)
        d["raw_rows_per_hour"] = round(stats["raw_rows"] * 3600 / el)
        d["inserted_rows_per_hour"] = round(stats["inserted"] * 3600 / el)
        d["eta_s_this_batch"] = round((n - i) / (stats["objects"] / el)) if stats["objects"] else None
    Path(args.progress).write_text(json.dumps(d))

if args.ingest:
    src = "spaces_" + args.prefix; table = "ticks" if args.prefix == "ticks" else "prints"
    listing = {o["Path"]: o for o in json.load(open(args.listing))}
    stage = Path(args.stage_dir) / args.prefix
    files = sorted(p for p in stage.rglob("*.csv.gz"))
    if args.month:
        y, m = int(args.month[:4]), int(args.month[5:7])
        files = [p for p in files if (name_date(p.name) or (0, 0, 0))[:2] == (y, m)]
    if args.limit: files = files[:args.limit]
    done = {r[0] for r in con.execute("SELECT path FROM ingest_log WHERE src=?", (src,))}
    pend_rows = 0; pend_objs = 0; t_batch = time.time()
    for i, p in enumerate(files):
        key = p.relative_to(stage).as_posix(); path = "spaces:%s/%s" % (args.prefix, key)
        if path in done: stats["skipped_already_logged"] += 1; continue
        lst = listing.get(key); etag = (lst or {}).get("Hashes", {}).get("md5")
        tk = key.replace(".csv.gz", "").replace(".csv", ""); ev = tk.rsplit("-", 1)[0]; role = role_of(tk)
        if skip_object(tk):
            con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at,etag) VALUES(?,?,?,?,?)", (src, path, 0, time.time(), "SKIPPED_AFTER_BOUNDARY:" + (etag or "")))
            stats["skipped_after_boundary"] += 1; continue
        try:
            body = p.read_bytes()
        except OSError as e:
            stats["read_errors"] += 1; stats_last = repr(e); continue
        md5 = hashlib.md5(body).hexdigest()
        if lst is not None and lst.get("Size") != len(body): stats["size_mismatch"] += 1
        if etag and md5 != etag: stats["md5_mismatch"] += 1; etag = "STAGED_MD5_MISMATCH:%s:listing:%s" % (md5, etag)
        etag = etag or md5
        stats["bytes_read"] += len(body)
        rows = []; raw = 0; tss = []; kept_ts = []; prev = None; bad = 0
        try:
            fh = io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(body)), encoding="utf-8", errors="replace")
            rd = csv.reader(fh); hdr = next(rd)
            ix = {c: j for j, c in enumerate(hdr)}
            its = ix["ts_et"]
            if table == "ticks":
                # early-format files (Apr 2026) have no last_trade column → last is NULL,
                # exactly as the DictReader-based streamed runs stored them.
                ib, ia = ix["bid_1"], ix["ask_1"]; il = ix.get("last_trade")
                if il is None: stats["objects_without_last_trade_column"] += 1
                for row in rd:
                    try:
                        ts = ep_et(row[its])
                    except IndexError:
                        bad += 1; continue
                    if ts is None: bad += 1; continue
                    if not (T_LO <= ts < T_HI): continue
                    raw += 1; tss.append(ts)
                    try:
                        k = (row[ib], row[ia], row[il] if il is not None else "")
                    except IndexError:
                        bad += 1; continue
                    if k != prev:
                        try:
                            bid = int(float(k[0])) if k[0] != "" else None
                            ask = int(float(k[1])) if k[1] != "" else None
                            last = int(float(k[2])) if k[2] != "" else None
                        except ValueError:
                            bad += 1; prev = k; continue
                        rows.append((ev, tk, ts, bid, ask, last, None, src, role, path)); kept_ts.append(ts)
                    prev = k
            else:
                ip, ic = ix["price"], ix["count"]
                for row in rd:
                    try:
                        ts = ep_et(row[its])
                    except IndexError:
                        bad += 1; continue
                    if ts is None: bad += 1; continue
                    if not (T_LO <= ts < T_HI): continue
                    raw += 1; tss.append(ts)
                    try: px = int(float(row[ip])); sz = float(row[ic] or 0)
                    except (ValueError, IndexError): bad += 1; continue
                    rows.append((ev, tk, ts, px, sz, src, role, path))
                kept_ts = tss
        except Exception as e:
            stats["read_errors"] += 1; stats["last_error_obj"] = key; continue
        before = con.total_changes
        if table == "ticks":
            con.executemany("INSERT OR IGNORE INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)", rows)
        else:
            con.executemany("INSERT INTO prints(event,ticker,ts,price,size,src,src_role,obj) VALUES(?,?,?,?,?,?,?,?)", rows)
        new = con.total_changes - before
        gr = [b2 - a2 for a2, b2 in zip(tss, tss[1:]) if b2 > a2]; gk = [b2 - a2 for a2, b2 in zip(kept_ts, kept_ts[1:]) if b2 > a2]
        con.execute("INSERT OR REPLACE INTO cadence VALUES(?,?,?,?,?,?,?)", (src, path, raw, len(rows), len(set(tss)), med(gr), med(gk)))
        con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at,etag) VALUES(?,?,?,?,?)", (src, path, new, time.time(), etag))
        stats["objects"] += 1; stats["raw_rows"] += raw; stats["kept_rows"] += len(rows); stats["inserted"] += new
        stats["ignored_by_unique_key"] += len(rows) - new; stats["bad_rows"] += bad
        pend_rows += len(rows); pend_objs += 1
        if pend_rows >= args.batch_rows:
            con.commit(); stats["transactions"] += 1; pend_rows = 0; pend_objs = 0
        if i % 25 == 0: progress(src, i + 1, len(files))
    con.commit(); stats["transactions"] += 1
    progress(src, len(files), len(files), "batch done")
    print(json.dumps({"batch": args.month, "files_seen": len(files), "elapsed_s": round(time.time() - T0, 1), "stats": dict(stats)}))

# ---------------------------------------------------------------- receipt
if args.receipt:
    def q1(sql, *a): return con.execute(sql, a).fetchone()[0]
    R = {"label": "CONSOLIDATION_RECEIPT", "date": "2026-09-04", "store": str(DB), "store_realpath": os.path.realpath(DB),
         "boundary": [args.boundary_start, args.boundary_end], "tune_sample": [args.tune_start, args.tune_end],
         "receipt_built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "rows_after": {t: q1("SELECT COUNT(*) FROM %s" % t) for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")},
         "indexes": {t: [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=?", (t,))] for t in ("ticks", "prints", "ingest_log")}}
    objs_by = defaultdict(int)
    for s, p, n in con.execute("SELECT src, path, rows FROM ingest_log"):
        d = name_date(p)
        if d: objs_by[(s, "%04d-%02d" % (d[0], d[1]))] += 1
    def per_src_month(table):
        both = {}
        for s, m, c in con.execute("SELECT src, m, COUNT(*) FROM (SELECT src, strftime('%%Y-%%m', ts, 'unixepoch') m, event, COUNT(DISTINCT ticker) c FROM %s GROUP BY src, m, event) WHERE c>=2 GROUP BY src, m" % table):
            both[(s, m)] = c
        out = []
        for s, m, n, tk, ev in con.execute("SELECT src, strftime('%%Y-%%m', ts, 'unixepoch') m, COUNT(*), COUNT(DISTINCT ticker), COUNT(DISTINCT event) FROM %s GROUP BY src, m ORDER BY src, m" % table):
            out.append({"src": s, "month": m, "rows": n, "distinct_tickers": tk, "distinct_events": ev, "events_both_legs": both.get((s, m), 0), "objects_ingested_by_name_month": objs_by.get((s, m), 0)})
        return out
    R["per_source_month"] = {"prints": per_src_month("prints"), "ticks": per_src_month("ticks")}
    R["cadence_per_source"] = []
    for (s,) in con.execute("SELECT DISTINCT src FROM cadence"):
        g1 = [x for (x,) in con.execute("SELECT median_gap_raw FROM cadence WHERE src=? AND median_gap_raw IS NOT NULL", (s,))]
        g2 = [x for (x,) in con.execute("SELECT median_gap_kept FROM cadence WHERE src=? AND median_gap_kept IS NOT NULL", (s,))]
        n, r, k = con.execute("SELECT COUNT(*), SUM(raw_rows), SUM(kept_rows) FROM cadence WHERE src=?", (s,)).fetchone()
        R["cadence_per_source"].append({"src": s, "objects": n, "raw_rows": r, "kept_rows": k, "median_of_object_median_gap_raw_s": med(g1), "median_of_object_median_gap_kept_s": med(g2)})
    R["dupes_dropped_by_streamed_runs"] = [dict(src_new=a, src_existing=b, table=t, n=n) for a, b, t, n in con.execute("SELECT * FROM dupes")]
    R["cross_source_overlap_kept"] = {"validation4_bin_rows_also_in_spaces_ticks_on_(ticker,ts,bid,ask,last)":
        q1("SELECT COUNT(*) FROM ticks a WHERE a.src='validation4_bin' AND EXISTS (SELECT 1 FROM ticks b WHERE b.ticker=a.ticker AND b.ts=a.ts AND b.bid IS a.bid AND b.ask IS a.ask AND b.last IS a.last AND b.src='spaces_ticks')")}
    R["src_role"] = {t: [dict(src=s, role=r, rows=n) for s, r, n in con.execute("SELECT src, src_role, COUNT(*) FROM %s GROUP BY src, src_role" % t)] for t in ("ticks", "prints")}
    R["ingest_log_by_src"] = [dict(src=s, objects=n, rows_logged=r, skipped_after_boundary=k) for s, n, r, k in con.execute("SELECT src, COUNT(*), SUM(rows), SUM(CASE WHEN etag LIKE 'SKIPPED_AFTER_BOUNDARY%' THEN 1 ELSE 0 END) FROM ingest_log GROUP BY src")]
    R["md5_mismatches_logged"] = q1("SELECT COUNT(*) FROM ingest_log WHERE etag LIKE 'STAGED_MD5_MISMATCH%'")
    days = set()
    for t in ("ticks", "prints"):
        for (d,) in con.execute("SELECT DISTINCT strftime('%%Y-%%m-%%d', ts, 'unixepoch') FROM %s WHERE ts>=? AND ts<?" % t, (T_LO, T_HI)):
            days.add(d)
    d0 = datetime.fromisoformat(args.boundary_start).date(); d1 = datetime.fromisoformat(args.boundary_end).date(); gaps = []; cur = None; d = d0
    while d <= d1:
        if d.isoformat() not in days: cur = [d.isoformat(), d.isoformat()] if cur is None else [cur[0], d.isoformat()]
        else:
            if cur: gaps.append(cur); cur = None
        d += timedelta(days=1)
    if cur: gaps.append(cur)
    R["zero_capture_day_ranges_in_store_utc_days"] = gaps; R["days_with_capture_in_store"] = len(days)
    R["receipt_query_s"] = round(time.time() - T0, 1)
    if not args.no_hash:
        con.commit(); con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        h = hashlib.sha256()
        with open(DB, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 24), b""): h.update(chunk)
        R["store_sha256_after"] = h.hexdigest(); R["store_bytes_after"] = os.path.getsize(DB)
    Path(args.receipt).write_text(json.dumps(R, indent=1, default=str))
    print("receipt", args.receipt, "in", round(time.time() - T0), "s")
con.commit(); con.close()
