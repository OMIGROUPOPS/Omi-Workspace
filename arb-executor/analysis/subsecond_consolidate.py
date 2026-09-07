#!/usr/bin/env python3
"""P2 — THE SUBSECOND CONSOLIDATION (inventory census + ONE store).

v1 (2026-07-18): daysheet_tape (public_tape) · engine-log WS prints (ws_log) ·
premarket_ticks last_trade transitions (book_transition) into
state/subsecond_store.db prints(event, ticker, ts, price, size, src).

v2 (2026-09-04, ingest pass): three sources added, same resume semantics
(ingest_log path is the resume key; object key + etag recorded):
  spaces_ticks    — spaces:omi-tick-archive/ticks/<leg>.csv.gz streamed
                    (never copied to disk). Listing via rclone lsjson (or a
                    cached listing file); object bodies fetched in memory over
                    one persistent SigV4-signed HTTPS connection (stdlib only:
                    a fresh rclone process per object cost ~11 s on the 2 GB
                    droplet). HTTP ETag recorded per object. Book-transition-grade
                    rows: one row whenever (bid_1, ask_1, last_trade) changes.
                    → ticks(event, ticker, ts, bid, ask, last, size, src, src_role, obj)
  spaces_trades   — spaces:omi-tick-archive/trades/<leg>.csv.gz streamed.
                    Trade prints → prints(event, ticker, ts, price, size, src, src_role, obj)
  validation4_bin — data/durable/validation4_ticks/*.bin, writer format from
                    tmp/validation4_step6_real/binary_splitter.py: struct '<IBB'
                    (uint32 ts, uint8 bid, uint8 ask). The writer packs the
                    ET wall-clock string with calendar.timegm and NO offset,
                    so ts is naive America/New_York; converted to UTC here.
                    Change rows on (bid, ask) → ticks (last NULL).
Boundary: rows with 2026-03-20 ≤ ts(UTC) < 2026-07-26 only; objects whose
name date is 26JUL26 or later are skipped entirely (sealed exam / holdout).
src_role: TUNE_SAMPLE for tickers dated 26JUL11..26JUL21 (the 804), else LIBRARY.
Dedupe: across sources on (ticker, ts, bid, ask, last) for ticks and
(ticker, ts, price, size) for prints; first-seen source kept; duplicate
counts per (new source, existing source) in table dupes. Identical trade
rows inside one object are distinct prints at 1 s resolution and are kept.
Timestamps in every new row are absolute UTC epoch seconds.
No cron is installed by this file (the pre-existing /etc/cron.d/omi-subsecond nightly runs it
with the default --sources legacy, i.e. v1 behaviour).
"""
import argparse, calendar, csv, glob, gzip, hashlib, hmac, http.client, io, json, os, re, sqlite3, statistics, struct, subprocess, sys, time, urllib.parse
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "state/subsecond_store.db"
CENSUS = Path("/tmp/SUBSECOND_CENSUS.md")
PROGRESS = Path("/tmp/consolidate_progress.json")
BUCKET = "spaces:omi-tick-archive"
MON = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}

ap = argparse.ArgumentParser()
ap.add_argument("--sources", default="legacy", help="default = v1 nightly behaviour (daysheet_tape/ws_log/book_transition only); add validation4_bin,spaces_trades,spaces_ticks explicitly for the ingest pass")
ap.add_argument("--limit", type=int, default=0, help="max objects per new source (0 = all)")
ap.add_argument("--boundary-start", default="2026-03-20")
ap.add_argument("--boundary-end", default="2026-07-25", help="inclusive (UTC date)")
ap.add_argument("--tune-start", default="26JUL11")
ap.add_argument("--tune-end", default="26JUL21")
ap.add_argument("--receipt", default="", help="write CONSOLIDATION_RECEIPT json here at the end")
ap.add_argument("--no-hash", action="store_true")
ap.add_argument("--spaces-listing-dir", default="", help="reuse cached rclone lsjson output <dir>/spaces_<prefix>_lsjson.json instead of re-listing")
args = ap.parse_args()
SOURCES = set(s.strip() for s in args.sources.split(",") if s.strip())
T_LO = datetime.fromisoformat(args.boundary_start).replace(tzinfo=timezone.utc).timestamp()
T_HI = datetime.fromisoformat(args.boundary_end).replace(tzinfo=timezone.utc).timestamp() + 86400.0
T0 = time.time()

def cat_of(tk):
    for pre, c in (("KXATPCHALLENGER", "ATP_CHALL"), ("KXWTACHALLENGER", "WTA_CHALL"),
                   ("KXITFWMATCH", "ITF_W"), ("KXITFMATCH", "ITF_M"),
                   ("KXWTAMATCH", "WTA_MAIN"), ("KXATPMATCH", "ATP_MAIN")):
        if tk.startswith(pre):
            return c
    return "?"

def name_date(tk):
    """('26JUL11' as (y,m,d)) from a ticker or event id, else None."""
    m = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", tk)
    if not m or m.group(2) not in MON:
        return None
    return (2000 + int(m.group(1)), MON[m.group(2)], int(m.group(3)))

def key_of(code):
    return (2000 + int(code[:2]), MON[code[2:5]], int(code[5:7]))
TUNE_LO, TUNE_HI = key_of(args.tune_start), key_of(args.tune_end)
B_END_KEY = tuple(int(x) for x in args.boundary_end.split("-"))

def role_of(tk):
    d = name_date(tk)
    return "TUNE_SAMPLE" if d and TUNE_LO <= d <= TUNE_HI else "LIBRARY"

def skip_object(tk):
    d = name_date(tk)
    return bool(d and d > B_END_KEY)

def ep_et(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
    except ValueError:
        return None

# ---------------------------------------------------------------- schema
# one writer at a time: the nightly cron (/etc/cron.d/omi-subsecond, 04:35 ET) and the staged
# ingest must not overlap — a cron run that finds the lock held exits without touching the store.
import fcntl
_lock = open(str(DB) + ".lock", "w")
try:
    fcntl.flock(_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError:
    print("subsecond_store.db.lock held by another consolidation process; exiting without changes"); sys.exit(0)
con = sqlite3.connect(DB, timeout=60)
con.execute("PRAGMA journal_mode=WAL")
con.execute("PRAGMA synchronous=NORMAL")
con.execute("PRAGMA cache_size=-200000")
con.executescript("""
CREATE TABLE IF NOT EXISTS prints(
  event TEXT, ticker TEXT, ts REAL, price INTEGER, size REAL, src TEXT);
CREATE INDEX IF NOT EXISTS p_tk ON prints(ticker, ts);
CREATE INDEX IF NOT EXISTS p_ev ON prints(event, ts);
CREATE TABLE IF NOT EXISTS ingest_log(
  src TEXT, path TEXT PRIMARY KEY, rows INTEGER, ingested_at REAL);
CREATE TABLE IF NOT EXISTS ticks(
  event TEXT, ticker TEXT, ts REAL, bid INTEGER, ask INTEGER, last INTEGER,
  size REAL, src TEXT, src_role TEXT, obj TEXT);
CREATE INDEX IF NOT EXISTS t_ev ON ticks(event, ts);
CREATE TABLE IF NOT EXISTS dupes(
  src_new TEXT, src_existing TEXT, table_name TEXT, n INTEGER,
  PRIMARY KEY(src_new, src_existing, table_name));
CREATE TABLE IF NOT EXISTS cadence(
  src TEXT, obj TEXT PRIMARY KEY, raw_rows INTEGER, kept_rows INTEGER,
  distinct_ts INTEGER, median_gap_raw REAL, median_gap_kept REAL);
""")
def add_col(table, col, typ):
    cols = [c[1] for c in con.execute("PRAGMA table_info(%s)" % table)]
    if col not in cols:
        con.execute("ALTER TABLE %s ADD COLUMN %s %s" % (table, col, typ))
add_col("prints", "src_role", "TEXT"); add_col("prints", "obj", "TEXT")
add_col("ingest_log", "etag", "TEXT")
# t_tk / t_key / p_key were dropped 2026-09-05: the staged-ingest UNIQUE index t_uq (ticker, ts, ...) covers
# the ticks lookups and p_tk (ticker, ts) covers the prints dedupe join. Do not recreate them here.
con.execute("CREATE UNIQUE INDEX IF NOT EXISTS t_uq ON ticks(ticker, ts, IFNULL(bid,-1), IFNULL(ask,-1), IFNULL(last,-1), IFNULL(size,-1), src)")
con.commit()
done = {r[0] for r in con.execute("SELECT path FROM ingest_log")}
census = defaultdict(lambda: {"files": 0, "rows": 0, "lo": None, "hi": None,
                              "cats": defaultdict(int), "note": ""})
stats = defaultdict(lambda: defaultdict(int))

def bank(src, lo, hi, n, cat=None, files=0):
    c = census[src]
    c["files"] += files; c["rows"] += n
    if lo: c["lo"] = min(c["lo"] or lo, lo)
    if hi: c["hi"] = max(c["hi"] or hi, hi)
    if cat: c["cats"][cat] += n

def dupe_count(src_new, src_existing, table):
    con.execute("INSERT INTO dupes VALUES(?,?,?,0) ON CONFLICT(src_new,src_existing,table_name) DO NOTHING",
                (src_new, src_existing, table))
    con.execute("UPDATE dupes SET n=n+1 WHERE src_new=? AND src_existing=? AND table_name=?",
                (src_new, src_existing, table))

def insert_ticks(rows, src):
    """rows: (event, ticker, ts, bid, ask, last, size, src, role, obj). Dedupe on key across sources."""
    if not rows:
        return 0, 0
    seen = set(); uniq = []
    for r in rows:
        k = (r[1], r[2], r[3], r[4], r[5])
        if k in seen:
            stats[src]["dup_within_object"] += 1; continue
        seen.add(k); uniq.append(r)
    con.execute("CREATE TEMP TABLE IF NOT EXISTS b_t(ticker TEXT, ts REAL, bid INTEGER, ask INTEGER, last INTEGER, i INTEGER)")
    con.execute("DELETE FROM b_t")
    con.executemany("INSERT INTO b_t VALUES(?,?,?,?,?,?)", [(r[1], r[2], r[3], r[4], r[5], i) for i, r in enumerate(uniq)])
    existing = {}
    for i, s in con.execute("SELECT b.i, p.src FROM b_t b JOIN ticks p ON p.ticker=b.ticker AND p.ts=b.ts AND p.bid IS b.bid AND p.ask IS b.ask AND p.last IS b.last"):
        existing.setdefault(i, s)
    for i, s in existing.items():
        dupe_count(src, s, "ticks")
    new = [r for i, r in enumerate(uniq) if i not in existing]
    con.executemany("INSERT INTO ticks VALUES(?,?,?,?,?,?,?,?,?,?)", new)
    return len(new), len(existing)

def insert_prints(rows, src):
    """rows: (event, ticker, ts, price, size, src, role, obj). Dedupe on (ticker, ts, price, size)."""
    if not rows:
        return 0, 0
    # identical (ticker, ts, price, size) rows inside one object are distinct
    # prints at 1-second resolution: kept, counted, not deduped.
    seen = set(); uniq = list(rows)
    for r in rows:
        k = (r[1], r[2], r[3], r[4])
        if k in seen: stats[src]["identical_rows_within_object"] += 1
        seen.add(k)
    con.execute("CREATE TEMP TABLE IF NOT EXISTS b_p(ticker TEXT, ts REAL, price INTEGER, size REAL, i INTEGER)")
    con.execute("DELETE FROM b_p")
    con.executemany("INSERT INTO b_p VALUES(?,?,?,?,?)", [(r[1], r[2], r[3], r[4], i) for i, r in enumerate(uniq)])
    existing = {}
    for i, s in con.execute("SELECT b.i, p.src FROM b_p b JOIN prints p ON p.ticker=b.ticker AND p.ts=b.ts AND p.price=b.price AND p.size IS b.size WHERE p.src<>?", (src,)):
        existing.setdefault(i, s)
    for i, s in existing.items():
        dupe_count(src, s, "prints")
    new = [r for i, r in enumerate(uniq) if i not in existing]
    con.executemany("INSERT INTO prints(event,ticker,ts,price,size,src,src_role,obj) VALUES(?,?,?,?,?,?,?,?)", new)
    return len(new), len(existing)

def med(xs):
    return statistics.median(xs) if xs else None

def progress(src, i, n, extra=""):
    PROGRESS.write_text(json.dumps({"src": src, "done": i, "total": n, "elapsed_s": round(time.time() - T0, 1),
                                    "stats": {k: dict(v) for k, v in stats.items()}, "note": extra}))

# ---------------------------------------------------------------- v1 sources (unchanged)
if "legacy" in SOURCES:
    for p in sorted(glob.glob(str(ROOT / "state/daysheet_tape/*.json"))):
        if p in done: continue
        try:
            d = json.loads(open(p, encoding="utf-8").read()); tk = Path(p).stem; ev = tk.rsplit("-", 1)[0]
            rows = [(ev, tk, float(x["ts"]), int(x["price_c"]), float(x.get("count") or x.get("size") or 0), "public_tape")
                    for x in (d.get("prints") or []) if x.get("ts") and x.get("price_c")]
            if rows:
                con.executemany("INSERT INTO prints(event,ticker,ts,price,size,src) VALUES(?,?,?,?,?,?)", rows)
                bank("public_tape(daysheet_tape)", rows[0][2], rows[-1][2], len(rows), cat_of(tk), 1)
            con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at) VALUES(?,?,?,?)", ("public_tape", p, len(rows), time.time()))
        except Exception:
            continue
    con.commit()
    for p in sorted(glob.glob(str(ROOT / "logs/live_v3_2026*.jsonl*"))):
        if p in done: continue
        op = (lambda q: io.TextIOWrapper(gzip.open(q, "rb"), encoding="utf-8", errors="replace")) if p.endswith(".gz") else (lambda q: open(q, encoding="utf-8", errors="replace"))
        n = 0; lo = hi = None
        try:
            with op(p) as fh:
                batch = []
                for line in fh:
                    if '"trade"' not in line and '"trade_print"' not in line: continue
                    try: j = json.loads(line)
                    except ValueError: continue
                    if j.get("event") not in ("trade", "trade_print"): continue
                    d = j.get("details") or {}; tk = j.get("ticker") or ""; px = d.get("price"); ts = j.get("ts_epoch")
                    if not (tk and px and ts): continue
                    batch.append((tk.rsplit("-", 1)[0], tk, float(ts), int(px), float(d.get("count") or 0), "ws_log")); n += 1
                    lo = min(lo or ts, ts); hi = max(hi or ts, ts)
                if batch: con.executemany("INSERT INTO prints(event,ticker,ts,price,size,src) VALUES(?,?,?,?,?,?)", batch)
            bank("ws_log(engine jsonl)", lo, hi, n, files=1)
            con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at) VALUES(?,?,?,?)", ("ws_log", p, n, time.time())); con.commit()
        except Exception:
            continue
    for p in sorted(glob.glob(str(ROOT / "analysis/premarket_ticks/*.csv*"))):
        if p in done: continue
        tk = Path(p).name.replace(".csv.gz", "").replace(".csv", "")
        op = (lambda q: io.TextIOWrapper(gzip.open(q, "rb"), encoding="utf-8", errors="replace")) if p.endswith(".gz") else (lambda q: open(q, encoding="utf-8", errors="replace"))
        n = 0; lo = hi = None
        try:
            with op(p) as fh:
                rd = csv.DictReader(fh); prev = None; batch = []
                for row in rd:
                    try: lt = int(float(row.get("last_trade") or 0))
                    except ValueError: continue
                    if lt and lt != prev:
                        ts = ep_et(row.get("ts_et") or "")
                        if ts:
                            batch.append((tk.rsplit("-", 1)[0], tk, ts, lt, 0.0, "book_transition")); n += 1
                            lo = min(lo or ts, ts); hi = max(hi or ts, ts)
                    prev = lt if lt else prev
                if batch: con.executemany("INSERT INTO prints(event,ticker,ts,price,size,src) VALUES(?,?,?,?,?,?)", batch)
            bank("book_transition(premarket_ticks)", lo, hi, n, cat_of(tk), 1)
            con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at) VALUES(?,?,?,?)", ("book_transition", p, n, time.time()))
            if n: con.commit()
        except Exception:
            continue
    con.commit()

# ---------------------------------------------------------------- v2: validation4_bin
if "validation4_bin" in SOURCES:
    src = "validation4_bin"; V4 = ROOT / "data/durable/validation4_ticks"
    files = sorted(glob.glob(str(V4 / "*.bin")))
    if args.limit: files = files[:args.limit]
    for i, p in enumerate(files):
        path = "validation4_ticks/" + Path(p).name
        if path in done: continue
        tk = Path(p).name[:-4]; ev = tk.rsplit("-", 1)[0]; role = role_of(tk)
        if skip_object(tk):
            con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at,etag) VALUES(?,?,?,?,?)", (src, path, 0, time.time(), "SKIPPED_AFTER_BOUNDARY")); continue
        b = open(p, "rb").read(); m = len(b) // 6
        rows = []; prev = None; raw = 0; tss = []; kept_ts = []
        for j in range(m):
            u, bid, ask = struct.unpack_from("<IBB", b, j * 6)
            # writer packed ET wall clock via calendar.timegm (no offset): naive ET → UTC
            naive = datetime.fromtimestamp(u, timezone.utc).replace(tzinfo=None)
            ts = naive.replace(tzinfo=ET).timestamp()
            if not (T_LO <= ts < T_HI): continue
            raw += 1; tss.append(ts)
            if (bid, ask) != prev:
                rows.append((ev, tk, ts, bid, ask, None, None, src, role, path)); kept_ts.append(ts)
            prev = (bid, ask)
        new, dup = insert_ticks(rows, src)
        gr = [b2 - a2 for a2, b2 in zip(tss, tss[1:]) if b2 > a2]; gk = [b2 - a2 for a2, b2 in zip(kept_ts, kept_ts[1:]) if b2 > a2]
        con.execute("INSERT OR REPLACE INTO cadence VALUES(?,?,?,?,?,?,?)", (src, path, raw, len(rows), len(set(tss)), med(gr), med(gk)))
        con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at,etag) VALUES(?,?,?,?,?)", (src, path, new, time.time(), "bytes=%d" % len(b)))
        stats[src]["files"] += 1; stats[src]["raw_rows"] += raw; stats[src]["kept_rows"] += len(rows); stats[src]["inserted"] += new; stats[src]["dup_cross_source"] += dup
        if rows: bank(src, rows[0][2], rows[-1][2], new, cat_of(tk), 1)
        if i % 50 == 0:
            con.commit(); progress(src, i + 1, len(files))
    con.commit(); progress(src, len(files), len(files), "done")

# ---------------------------------------------------------------- v2: spaces streaming
def spaces_env():
    env = dict(os.environ)
    envf = ROOT / ".env"
    if envf.exists():
        for line in open(envf, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k, v = line.split("=", 1); env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    env.update({"RCLONE_CONFIG_SPACES_TYPE": "s3", "RCLONE_CONFIG_SPACES_PROVIDER": "DigitalOcean",
                "RCLONE_CONFIG_SPACES_ACCESS_KEY_ID": env.get("SPACES_KEY", ""),
                "RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY": env.get("SPACES_SECRET", ""),
                "RCLONE_CONFIG_SPACES_ENDPOINT": "nyc3.digitaloceanspaces.com"})
    return env

def spaces_list(prefix, env):
    if args.spaces_listing_dir:
        cached = Path(args.spaces_listing_dir) / ("spaces_%s_lsjson.json" % prefix)
        if cached.exists():
            return sorted(json.load(open(cached)), key=lambda x: x["Path"])
    out = subprocess.run(["rclone", "lsjson", "-R", "--files-only", "--no-mimetype", "--hash", "--hash-type", "md5", "%s/%s" % (BUCKET, prefix)],
                         capture_output=True, text=True, env=env, check=True).stdout
    return sorted(json.loads(out), key=lambda x: x["Path"])

S3_HOST = "nyc3.digitaloceanspaces.com"; S3_REGION = "nyc3"; S3_BUCKET = BUCKET.split(":", 1)[1]
EMPTY_SHA = hashlib.sha256(b"").hexdigest()

class S3Get:
    """Minimal SigV4 GET over one persistent HTTPS connection (bodies held in memory only)."""
    def __init__(self, key, secret):
        self.key = key; self.secret = secret; self.conn = None; self.fetched = 0; self.reconnects = 0
    def _connect(self):
        if self.conn is not None:
            try: self.conn.close()
            except Exception: pass
            self.reconnects += 1
        self.conn = http.client.HTTPSConnection(S3_HOST, 443, timeout=120)
    def _headers(self, path):
        t = datetime.now(timezone.utc); amz = t.strftime("%Y%m%dT%H%M%SZ"); ds = t.strftime("%Y%m%d")
        NL = chr(10)
        ch = "host:%s" % S3_HOST + NL + "x-amz-content-sha256:%s" % EMPTY_SHA + NL + "x-amz-date:%s" % amz + NL
        signed = "host;x-amz-content-sha256;x-amz-date"
        creq = NL.join(["GET", path, "", ch, signed, EMPTY_SHA])
        scope = "%s/%s/s3/aws4_request" % (ds, S3_REGION)
        sts = NL.join(["AWS4-HMAC-SHA256", amz, scope, hashlib.sha256(creq.encode()).hexdigest()])
        k = ("AWS4" + self.secret).encode()
        for part in (ds, S3_REGION, "s3", "aws4_request"):
            k = hmac.new(k, part.encode(), hashlib.sha256).digest()
        sig = hmac.new(k, sts.encode(), hashlib.sha256).hexdigest()
        return {"Host": S3_HOST, "x-amz-date": amz, "x-amz-content-sha256": EMPTY_SHA,
                "Authorization": "AWS4-HMAC-SHA256 Credential=%s/%s, SignedHeaders=%s, Signature=%s" % (self.key, scope, signed, sig)}
    def get(self, objkey):
        """objkey: '<prefix>/<Path>'. Returns (body_bytes, etag) or raises."""
        path = "/" + S3_BUCKET + "/" + urllib.parse.quote(objkey, safe="/-_.~")
        last = None
        for attempt in range(6):
            try:
                if self.conn is None: self._connect()
                self.conn.request("GET", path, headers=self._headers(path))
                r = self.conn.getresponse(); body = r.read()
                if r.status == 200:
                    self.fetched += 1
                    return body, (r.getheader("ETag") or "").strip('"')
                last = "HTTP %d %s" % (r.status, body[:200].decode("utf-8", "replace"))
                if r.status in (403, 404): raise RuntimeError(last)
            except RuntimeError: raise
            except Exception as e:
                last = repr(e)
            self._connect(); time.sleep(min(30, 2 ** attempt))
        raise RuntimeError("S3 GET failed after retries: %s" % last)

def spaces_open(prefix, key, s3):
    body, etag = s3.get("%s/%s" % (prefix, key))
    return io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(body)), encoding="utf-8", errors="replace"), etag, len(body)

for prefix, src in (("trades", "spaces_trades"), ("ticks", "spaces_ticks")):
    if src not in SOURCES: continue
    env = spaces_env()
    objs = spaces_list(prefix, env)
    s3 = S3Get(env.get("SPACES_KEY", ""), env.get("SPACES_SECRET", ""))
    if args.limit: objs = objs[:args.limit]
    for i, o in enumerate(objs):
        key = o["Path"]; path = "spaces:%s/%s" % (prefix, key); etag = (o.get("Hashes") or {}).get("md5")
        if path in done: continue
        tk = key.replace(".csv.gz", "").replace(".csv", ""); ev = tk.rsplit("-", 1)[0]; role = role_of(tk)
        if skip_object(tk):
            con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at,etag) VALUES(?,?,?,?,?)", (src, path, 0, time.time(), "SKIPPED_AFTER_BOUNDARY:" + (etag or ""))); continue
        rows = []; raw = 0; tss = []; kept_ts = []; prev = None; bad = 0
        try:
            fh, http_etag, nbytes = spaces_open(prefix, key, s3)
            if http_etag: etag = http_etag
            stats[src]["bytes_streamed"] += nbytes
            rd = csv.DictReader(fh)
            for row in rd:
                ts = ep_et(row.get("ts_et") or "")
                if ts is None: bad += 1; continue
                if not (T_LO <= ts < T_HI): continue
                raw += 1; tss.append(ts)
                if prefix == "trades":
                    try: px = int(float(row.get("price") or "")); sz = float(row.get("count") or 0)
                    except ValueError: bad += 1; continue
                    rows.append((ev, tk, ts, px, sz, src, role, path))
                else:
                    try:
                        bid = int(float(row["bid_1"])) if row.get("bid_1") not in (None, "") else None
                        ask = int(float(row["ask_1"])) if row.get("ask_1") not in (None, "") else None
                        last = int(float(row["last_trade"])) if row.get("last_trade") not in (None, "") else None
                    except (ValueError, KeyError): bad += 1; continue
                    k = (bid, ask, last)
                    if k != prev:
                        rows.append((ev, tk, ts, bid, ask, last, None, src, role, path)); kept_ts.append(ts)
                    prev = k
        except Exception as e:
            stats[src]["read_errors"] += 1; stats[src]["last_error"] = repr(e)[:200]; continue
        if prefix == "trades":
            new, dup = insert_prints(rows, src); kept = len(rows); kept_ts = tss
        else:
            new, dup = insert_ticks(rows, src); kept = len(rows)
        gr = [b2 - a2 for a2, b2 in zip(tss, tss[1:]) if b2 > a2]; gk = [b2 - a2 for a2, b2 in zip(kept_ts, kept_ts[1:]) if b2 > a2]
        con.execute("INSERT OR REPLACE INTO cadence VALUES(?,?,?,?,?,?,?)", (src, path, raw, kept, len(set(tss)), med(gr), med(gk)))
        con.execute("INSERT OR REPLACE INTO ingest_log(src,path,rows,ingested_at,etag) VALUES(?,?,?,?,?)", (src, path, new, time.time(), etag))
        stats[src]["objects"] += 1; stats[src]["raw_rows"] += raw; stats[src]["kept_rows"] += kept; stats[src]["inserted"] += new; stats[src]["dup_cross_source"] += dup; stats[src]["bad_rows"] += bad
        if rows: bank(src, rows[0][2], rows[-1][2], new, cat_of(tk), 1)
        if i % 25 == 0:
            con.commit(); progress(src, i + 1, len(objs))
    con.commit(); progress(src, len(objs), len(objs), "done")

# ---------------------------------------------------------------- census + receipt
def dt(ts):
    return datetime.fromtimestamp(ts, ET).strftime("%m-%d") if ts else "?"
tot_p = con.execute("SELECT COUNT(*) FROM prints").fetchone()[0]
tot_t = con.execute("SELECT COUNT(*) FROM ticks").fetchone()[0]
L = ["# P2 — THE SUBSECOND CENSUS (one store; the scatter killed)", "",
     "store: state/subsecond_store.db · prints rows: %d · ticks rows: %d · sources:" % (tot_p, tot_t), ""]
for src, c in sorted(census.items()):
    L.append("- **%s**: files %d · rows %d · span %s→%s · %s%s" % (src, c["files"], c["rows"], dt(c["lo"]), dt(c["hi"]), ("cats " + str(dict(c["cats"])) + " · ") if c["cats"] else "", c["note"]))
CENSUS.write_text("\n".join(L) + "\n")
print("\n".join(L[:30])); print("TOTAL prints:", tot_p, "ticks:", tot_t, "elapsed", round(time.time() - T0))

if args.receipt:
    R = {"label": "CONSOLIDATION_RECEIPT", "date": "2026-09-04", "store": str(DB), "boundary": [args.boundary_start, args.boundary_end],
         "tune_sample": [args.tune_start, args.tune_end], "sources_run": sorted(SOURCES), "runtime_s": round(time.time() - T0, 1),
         "rows_after": {t: con.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0] for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")},
         "stats": {k: dict(v) for k, v in stats.items()}}
    objs_by = defaultdict(int)
    for s, p, n in con.execute("SELECT src, path, rows FROM ingest_log"):
        d = name_date(p)
        if d: objs_by[(s, "%04d-%02d" % (d[0], d[1]))] += 1
    def per_src_month(table):
        q = ("SELECT src, strftime('%%Y-%%m', ts, 'unixepoch') m, COUNT(*), COUNT(DISTINCT ticker), COUNT(DISTINCT event) FROM %s GROUP BY src, m ORDER BY src, m" % table)
        out = []
        for src, m, n, tk, ev in con.execute(q):
            both = con.execute("SELECT COUNT(*) FROM (SELECT event, COUNT(DISTINCT ticker) c FROM %s WHERE src=? AND strftime('%%Y-%%m', ts, 'unixepoch')=? GROUP BY event) WHERE c>=2" % table, (src, m)).fetchone()[0]
            out.append({"src": src, "month": m, "rows": n, "distinct_tickers": tk, "distinct_events": ev, "events_both_legs": both, "objects_ingested_by_name_month": objs_by.get((src, m), 0)})
        return out
    R["per_source_month"] = {"prints": per_src_month("prints"), "ticks": per_src_month("ticks")}
    R["cadence_per_source"] = []
    for (s,) in con.execute("SELECT DISTINCT src FROM cadence"):
        g1 = [x for (x,) in con.execute("SELECT median_gap_raw FROM cadence WHERE src=? AND median_gap_raw IS NOT NULL", (s,))]
        g2 = [x for (x,) in con.execute("SELECT median_gap_kept FROM cadence WHERE src=? AND median_gap_kept IS NOT NULL", (s,))]
        n, r, k = con.execute("SELECT COUNT(*), SUM(raw_rows), SUM(kept_rows) FROM cadence WHERE src=?", (s,)).fetchone()
        R.setdefault("cadence_per_source", []).append({"src": s, "objects": n, "raw_rows": r, "kept_rows": k, "median_of_object_median_gap_raw_s": med(g1), "median_of_object_median_gap_kept_s": med(g2)})
    R["dupes"] = [dict(src_new=a, src_existing=b, table=t, n=n) for a, b, t, n in con.execute("SELECT * FROM dupes")]
    R["src_role"] = {t: [dict(src=s, role=r, rows=n) for s, r, n in con.execute("SELECT src, src_role, COUNT(*) FROM %s GROUP BY src, src_role" % t)] for t in ("ticks", "prints")}
    # day coverage inside the boundary from both tables
    days = set()
    for t in ("ticks", "prints"):
        for (d,) in con.execute("SELECT DISTINCT strftime('%%Y-%%m-%%d', ts, 'unixepoch') FROM %s WHERE ts>=? AND ts<?" % t, (T_LO, T_HI)):
            days.add(d)
    d0 = datetime.fromisoformat(args.boundary_start).date(); d1 = datetime.fromisoformat(args.boundary_end).date(); gaps = []; cur = None
    from datetime import timedelta
    d = d0
    while d <= d1:
        if d.isoformat() not in days:
            cur = [d.isoformat(), d.isoformat()] if cur is None else [cur[0], d.isoformat()]
        else:
            if cur: gaps.append(cur); cur = None
        d += timedelta(days=1)
    if cur: gaps.append(cur)
    R["zero_capture_day_ranges_in_store"] = gaps; R["days_with_capture_in_store"] = len(days)
    if not args.no_hash:
        import hashlib
        con.commit(); con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        h = hashlib.sha256()
        with open(DB, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 24), b""): h.update(chunk)
        R["store_sha256_after"] = h.hexdigest(); R["store_bytes_after"] = os.path.getsize(DB)
    Path(args.receipt).write_text(json.dumps(R, indent=1, default=str))
    print("receipt", args.receipt)
con.commit(); con.close()
