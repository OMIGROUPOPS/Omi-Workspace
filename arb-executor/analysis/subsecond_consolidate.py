#!/usr/bin/env python3
"""P2 — THE SUBSECOND CONSOLIDATION (inventory census + ONE store).

Inventory: every subsecond/tick series we hold, each location NAMED (the
scatter is the finding to kill), span + row counts + per-cat coverage +
timestamp resolution. Then consolidate PRINTS (trade-grade events — the
divot deconstruction's fuel) into one queryable sqlite store:
  state/subsecond_store.db
    prints(event TEXT, ticker TEXT, ts REAL, price INTEGER, size REAL,
           src TEXT)  [indexed (ticker, ts), (event, ts)]
    ingest_log(src TEXT, path TEXT, rows INTEGER, ingested_at REAL)
Sources ingested v1 (trade-grade): daysheet_tape (public trades cache —
true subsecond) · engine-log trade lines (WS trade prints) · premarket_ticks
last_trade TRANSITIONS (book-cadence, transition-grade, src-labeled).
Book-grade sources (depth_recorder / ws_depth_recorder / snapshots) are
INVENTORIED with spans but not folded into prints — they are book series,
named for the Phase-D microstructure voice. Append-forward: nightly cron
re-runs with the ingest_log as the resume key (no re-scatter, no dupes).
Outputs: the store + /tmp/SUBSECOND_CENSUS.md.
"""
import csv, glob, gzip, io, json, os, sqlite3, time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "state/subsecond_store.db"
CENSUS = Path("/tmp/SUBSECOND_CENSUS.md")

def cat_of(tk):
    for pre, c in (("KXATPCHALLENGER", "ATP_CHALL"),
                   ("KXWTACHALLENGER", "WTA_CHALL"),
                   ("KXITFWMATCH", "ITF_W"), ("KXITFMATCH", "ITF_M"),
                   ("KXWTAMATCH", "WTA_MAIN"), ("KXATPMATCH", "ATP_MAIN")):
        if tk.startswith(pre):
            return c
    return "?"

con = sqlite3.connect(DB)
con.executescript("""
CREATE TABLE IF NOT EXISTS prints(
  event TEXT, ticker TEXT, ts REAL, price INTEGER, size REAL, src TEXT);
CREATE INDEX IF NOT EXISTS p_tk ON prints(ticker, ts);
CREATE INDEX IF NOT EXISTS p_ev ON prints(event, ts);
CREATE TABLE IF NOT EXISTS ingest_log(
  src TEXT, path TEXT PRIMARY KEY, rows INTEGER, ingested_at REAL);
""")
done = {r[0] for r in con.execute("SELECT path FROM ingest_log")}
census = defaultdict(lambda: {"files": 0, "rows": 0, "lo": None, "hi": None,
                              "cats": defaultdict(int), "note": ""})

def bank(src, lo, hi, n, cat=None, files=0):
    c = census[src]
    c["files"] += files
    c["rows"] += n
    if lo:
        c["lo"] = min(c["lo"] or lo, lo)
    if hi:
        c["hi"] = max(c["hi"] or hi, hi)
    if cat:
        c["cats"][cat] += n

# ---- 1) daysheet_tape: public trades caches (TRUE subsecond) ------------
for p in sorted(glob.glob(str(ROOT / "state/daysheet_tape/*.json"))):
    if p in done:
        continue
    try:
        d = json.loads(open(p, encoding="utf-8").read())
        tk = Path(p).stem
        ev = tk.rsplit("-", 1)[0]
        rows = [(ev, tk, float(x["ts"]), int(x["price_c"]),
                 float(x.get("count") or x.get("size") or 0),
                 "public_tape") for x in (d.get("prints") or [])
                if x.get("ts") and x.get("price_c")]
        if rows:
            con.executemany("INSERT INTO prints VALUES(?,?,?,?,?,?)", rows)
            bank("public_tape(daysheet_tape)", rows[0][2], rows[-1][2],
                 len(rows), cat_of(tk), 1)
        con.execute("INSERT OR REPLACE INTO ingest_log VALUES(?,?,?,?)",
                    ("public_tape", p, len(rows), time.time()))
    except Exception:
        continue
con.commit()

# ---- 2) engine-log WS trade prints --------------------------------------
for p in sorted(glob.glob(str(ROOT / "logs/live_v3_2026*.jsonl*"))):
    if p in done:
        continue
    op = (lambda q: io.TextIOWrapper(gzip.open(q, "rb"), encoding="utf-8",
                                     errors="replace")) \
        if p.endswith(".gz") else (lambda q: open(q, encoding="utf-8",
                                                  errors="replace"))
    n = 0
    lo = hi = None
    try:
        with op(p) as fh:
            batch = []
            for line in fh:
                if '"trade"' not in line and '"trade_print"' not in line:
                    continue
                try:
                    j = json.loads(line)
                except ValueError:
                    continue
                if j.get("event") not in ("trade", "trade_print"):
                    continue
                d = j.get("details") or {}
                tk = j.get("ticker") or ""
                px = d.get("price")
                ts = j.get("ts_epoch")
                if not (tk and px and ts):
                    continue
                batch.append((tk.rsplit("-", 1)[0], tk, float(ts), int(px),
                              float(d.get("count") or 0), "ws_log"))
                n += 1
                lo = min(lo or ts, ts)
                hi = max(hi or ts, ts)
            if batch:
                con.executemany("INSERT INTO prints VALUES(?,?,?,?,?,?)",
                                batch)
        bank("ws_log(engine jsonl)", lo, hi, n, files=1)
        con.execute("INSERT OR REPLACE INTO ingest_log VALUES(?,?,?,?)",
                    ("ws_log", p, n, time.time()))
        con.commit()
    except Exception:
        continue

# ---- 3) premarket_ticks last_trade transitions (transition-grade) -------
def ep_et(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %I:%M:%S %p").replace(
            tzinfo=ET).timestamp()
    except ValueError:
        return None
for p in sorted(glob.glob(str(ROOT / "analysis/premarket_ticks/*.csv*"))):
    if p in done:
        continue
    tk = Path(p).name.replace(".csv.gz", "").replace(".csv", "")
    op = (lambda q: io.TextIOWrapper(gzip.open(q, "rb"), encoding="utf-8",
                                     errors="replace")) \
        if p.endswith(".gz") else (lambda q: open(q, encoding="utf-8",
                                                  errors="replace"))
    n = 0
    lo = hi = None
    try:
        with op(p) as fh:
            rd = csv.DictReader(fh)
            prev = None
            batch = []
            for row in rd:
                try:
                    lt = int(float(row.get("last_trade") or 0))
                except ValueError:
                    continue
                if lt and lt != prev:
                    ts = ep_et(row.get("ts_et") or "")
                    if ts:
                        batch.append((tk.rsplit("-", 1)[0], tk, ts, lt,
                                      0.0, "book_transition"))
                        n += 1
                        lo = min(lo or ts, ts)
                        hi = max(hi or ts, ts)
                prev = lt if lt else prev
            if batch:
                con.executemany("INSERT INTO prints VALUES(?,?,?,?,?,?)",
                                batch)
        bank("book_transition(premarket_ticks)", lo, hi, n, cat_of(tk), 1)
        con.execute("INSERT OR REPLACE INTO ingest_log VALUES(?,?,?,?)",
                    ("book_transition", p, n, time.time()))
        if n:
            con.commit()
    except Exception:
        continue
con.commit()

# ---- 4) book-grade sources: INVENTORY ONLY (named for Phase D) ----------
for src, pat, note in (
    ("depth_recorder (book-grade, NOT in prints)",
     "data/durable/depth_recorder/depth_*.jsonl*", "5-level book deltas"),
    ("ws_depth_recorder (book-grade, NOT in prints)",
     "data/durable/ws_depth_recorder/*", "ws book archive"),
    ("kalshi_price_snapshots (poll-grade, NOT in prints)",
     None, "sqlite table, Apr-21→now, 3.35M rows"),
):
    if pat:
        fs = glob.glob(str(ROOT / pat))
        lo = hi = None
        for f in fs[:2000]:
            st = os.stat(f)
            lo = min(lo or st.st_mtime, st.st_mtime)
            hi = max(hi or st.st_mtime, st.st_mtime)
        census[src].update({"files": len(fs), "lo": lo, "hi": hi,
                            "note": note})
    else:
        census[src]["note"] = note

# ---- census ---------------------------------------------------------------
def dt(ts):
    return datetime.fromtimestamp(ts, ET).strftime("%m-%d") if ts else "?"
tot = con.execute("SELECT COUNT(*) FROM prints").fetchone()[0]
bymon = con.execute(
    "SELECT src, strftime('%Y-%m', ts, 'unixepoch') m, COUNT(*) "
    "FROM prints GROUP BY src, m ORDER BY m").fetchall()
L = ["# P2 — THE SUBSECOND CENSUS (one store; the scatter killed)", "",
     "store: state/subsecond_store.db · prints rows: %d · sources:" % tot, ""]
for src, c in sorted(census.items()):
    L.append("- **%s**: files %d · rows %d · span %s→%s · %s%s"
             % (src, c["files"], c["rows"], dt(c["lo"]), dt(c["hi"]),
                ("cats " + str(dict(c["cats"])) + " · ") if c["cats"] else "",
                c["note"]))
L.append("")
L.append("## coverage by month × source (prints store)")
for src, m, n in bymon:
    L.append("- %s %s: %d" % (m, src, n))
L.append("")
L.append("(append-forward: nightly cron re-runs this script; ingest_log "
         "is the resume key — no re-scatter, no dupes.)")
CENSUS.write_text("\n".join(L) + "\n")
print("\n".join(L[:20]))
print("TOTAL prints:", tot)
