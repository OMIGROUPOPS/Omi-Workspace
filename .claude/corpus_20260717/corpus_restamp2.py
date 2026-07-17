#!/usr/bin/env python3
"""PHASE A v2 — assembly + census with the honest fixes (Dispatch 2, 07-17).

Fixes over v1 (each named from v1's own scrutiny):
  1. UNIVERSE += ITF: the official cache's keys + premarket_ticks CSV event
     codes (ITF has no snapshot rows and no historical_events rows — v1
     dropped 191 of 205 officials by missing ITF entirely). New events get
     milestone fetches (cache-resumable).
  2. OLD STAMP = the LAST pre-observed commence_time (what the era's fits
     actually consumed at trade time), with the FIRST kept beside it — the
     |first−last| split names the RESCHEDULE class separately instead of
     billing Kalshi's own corrections as fit error.
  3. ONSET fallback: >=2 consecutive positive volume deltas, window opens
     AT sched (never before — a match cannot start before its schedule,
     P0v3 law), right_edge = max(sched, onset). Estimate-grade, named.
  4. CENSUS splits: session-clock class (exact-hour offsets) vs reschedule
     class (|err| > 12h) vs residual; corridor tables split by evidence
     grade (official_actual vs onset_est); ITF old-stamp error named
     UNMEASURABLE-FROM-SNAPSHOTS (the engine logs' clock_liar lines are its
     documented record).
"""
import glob, json, re, sqlite3, sys, time, urllib.request
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime
import statistics

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "state/milestone_starts.json"
OUT = ROOT / "state/corpus_events_v2.jsonl"
CENSUS = Path("/tmp/CORPUS_RESTAMP_CENSUS.md")

def iso_ep(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None

def cat_of(et):
    for pre, c in (("KXATPCHALLENGER", "ATP_CHALL"),
                   ("KXWTACHALLENGER", "WTA_CHALL"),
                   ("KXITFWMATCH", "ITF_W"), ("KXITFMATCH", "ITF_M"),
                   ("KXWTAMATCH", "WTA_MAIN"), ("KXATPMATCH", "ATP_MAIN")):
        if et.startswith(pre):
            return c
    return "?"

con = sqlite3.connect("file:%s?mode=ro" % (ROOT / "tennis.db"), uri=True,
                      timeout=5)

# ---- universe (fix 1) ---------------------------------------------------
events = set()
for (et,) in con.execute("SELECT DISTINCT event_ticker FROM historical_events"):
    events.add(et)
first_stamp, last_stamp = {}, {}
for et, cf, cl in con.execute(
        "SELECT event_ticker, MIN(commence_time), MAX(commence_time) "
        "FROM kalshi_price_snapshots WHERE commence_time IS NOT NULL "
        "GROUP BY event_ticker"):
    events.add(et)
    first_stamp[et] = iso_ep(cf)
    last_stamp[et] = iso_ep(cl)
official = {}
try:
    ob = json.loads((ROOT / "state/daysheet_bells_official.json").read_text())
    for ev, e in ob.items():
        events.add(ev)
        if e.get("start_ep") and e.get("status") not in (None, "not_started"):
            official[ev] = float(e["start_ep"])
except Exception as e:
    print("official cache:", e)
for f in glob.glob(str(ROOT / "analysis/premarket_ticks/*.csv")):
    tk = Path(f).stem
    if "-" in tk:
        events.add(tk.rsplit("-", 1)[0])
print("universe:", len(events), "| officials:", len(official), flush=True)

# ---- milestone top-up for new events (cache-resumable) ------------------
cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
todo = [et for et in events if et not in cache]
print("milestone top-up:", len(todo), flush=True)
for i, et in enumerate(todo):
    url = ("https://api.elections.kalshi.com/trade-api/v2/milestones?"
           "related_event_ticker=%s&limit=2" % et)
    try:
        with urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent": "omi-corpus-restamp"}),
                timeout=12) as r:
            d = json.load(r)
        ms = (d.get("milestones") or [None])[0] or {}
        cache[et] = {"start_date": ms.get("start_date"),
                     "source_id": ms.get("source_id"),
                     "status": ms.get("status")}
    except Exception as e:
        cache[et] = {"err": str(e)[:60]}
        if "429" in str(e):
            time.sleep(5)
    time.sleep(0.25)
    if i % 200 == 199:
        CACHE.write_text(json.dumps(cache))
        print("  %d/%d" % (i + 1, len(todo)), flush=True)
CACHE.write_text(json.dumps(cache))

# ---- onset (fix 3): >=2 consecutive positive deltas at/after sched ------
print("onset scan ...", flush=True)
onset = {}
rows = con.execute(
    "SELECT event_ticker, polled_at, SUM(volume_24h) FROM "
    "kalshi_price_snapshots GROUP BY event_ticker, polled_at "
    "ORDER BY event_ticker, polled_at")
prev_et, prev_vol, series = None, None, []
def _flush(et, series):
    if not et or not series:
        return
    sh = iso_ep((cache.get(et) or {}).get("start_date"))
    if not sh:
        return
    run = 0
    for ts, dv in series:
        if ts < sh:
            continue
        if dv and dv > 0:
            run += 1
            if run >= 2:
                onset[et] = ts
                return
        else:
            run = 0
for et, pa, vol in rows:
    ts = iso_ep(pa)
    if et != prev_et:
        _flush(prev_et, series)
        prev_et, prev_vol, series = et, None, []
    if ts is not None:
        if prev_vol is not None:
            series.append((ts, (vol or 0) - prev_vol))
        prev_vol = vol or 0
_flush(prev_et, series)
print("onsets:", len(onset), flush=True)

# ---- assemble (fix 2) + census (fix 4) ----------------------------------
out_rows = []
err_by = defaultdict(list)
classes = defaultdict(Counter)
resched = defaultdict(list)
cor_official, cor_onset = [], []
for et in sorted(events):
    ms = cache.get(et) or {}
    sched = iso_ep(ms.get("start_date"))
    off = official.get(et)
    on = onset.get(et)
    if off:
        right, rsrc = max(off, sched or off), "official_actual"
    elif on:
        right, rsrc = max(on, sched or on), "onset_snapshot_est"
    else:
        right, rsrc = sched, "sched_only_no_evidence"
    old_l, old_f = last_stamp.get(et), first_stamp.get(et)
    err_min = (round((old_l - sched) / 60.0, 1)
               if (old_l and sched) else None)
    cat = cat_of(et)
    out_rows.append({
        "event": et, "cat": cat,
        "era": et.split("-")[1][:5] if "-" in et else "?",
        "old_stamp_last": old_l, "old_stamp_first": old_f,
        "sched_honest": sched,
        "sched_src": "milestone_sportradar" if sched else "MISSING",
        "official_ts": off, "onset_est": on,
        "right_edge": right, "right_edge_src": rsrc,
        "old_err_min": err_min})
    if err_min is not None:
        a = abs(err_min)
        err_by[cat].append(a)
        cls = ("reschedule" if a > 720 else
               "session_clock" if (a >= 25 and abs(err_min % 60) <= 5)
               else "near" if a <= 30 else "residual")
        classes[cat][cls] += 1
    if old_l and old_f and abs(old_l - old_f) > 600:
        resched[cat].append((old_l - old_f) / 60.0)
    if sched and right and rsrc == "official_actual":
        cor_official.append((right - sched) / 60.0)
    elif sched and right and rsrc == "onset_snapshot_est":
        cor_onset.append((right - sched) / 60.0)

with open(OUT, "w") as fh:
    for r in out_rows:
        fh.write(json.dumps(r) + "\n")
print("wrote", OUT, len(out_rows), flush=True)

def dist(v):
    v = sorted(v)
    return ("n=%d · median %.0f · p75 %.0f · p95 %.0f"
            % (len(v), statistics.median(v), v[int(0.75 * len(v))],
               v[int(0.95 * len(v))])) if v else "n=0"

L = ["# PHASE A — CORPUS RE-STAMP CENSUS v2 (the indictment, scrutinized)",
     "",
     "- universe %d events · sched resolved %d · official actuals matched %d"
     " · onset fallbacks %d · sched-only %d"
     % (len(out_rows),
        sum(1 for r in out_rows if r["sched_honest"]),
        sum(1 for r in out_rows if r["official_ts"]),
        sum(1 for r in out_rows if r["right_edge_src"] == "onset_snapshot_est"),
        sum(1 for r in out_rows if r["right_edge_src"] == "sched_only_no_evidence")),
     "",
     "## |LAST-consumed old stamp − honest sched| by category (min) — the "
     "error the fits actually ate",
     "(old stamp = the last commence_time the era's machinery read; "
     "Kalshi's own later corrections are NOT billed as fit error — the "
     "reschedule class is split out below)"]
for cat, errs in sorted(err_by.items()):
    errs.sort()
    L.append("- %s: %s · >30min %.0f%% · >2h %.0f%% · classes %s"
             % (cat, dist(errs),
                100.0 * sum(1 for e in errs if e > 30) / len(errs),
                100.0 * sum(1 for e in errs if e > 120) / len(errs),
                dict(classes[cat])))
L.append("- ITF_M / ITF_W: old-stamp error UNMEASURABLE FROM SNAPSHOTS "
         "(the snapshot collector never carried ITF commence_time); the "
         "engine logs' clock_liar lines are the ITF lying-clock record — "
         "named, not guessed.")
L.append("")
L.append("## Kalshi self-corrections (|first − last commence| > 10 min) — "
         "the reschedule tail")
for cat, v in sorted(resched.items()):
    L.append("- %s: %s (minutes moved)" % (cat, dist([abs(x) for x in v])))
L.append("")
L.append("## sched → right-edge corridor (the tail where the entries live)")
L.append("- OFFICIAL-ACTUAL corridors (evidence-grade): %s"
         % dist(cor_official))
L.append("- ONSET-EST corridors (estimate-grade, poll-cadence resolution, "
         "clamped >= sched): %s" % dist(cor_onset))
CENSUS.write_text("\n".join(L) + "\n")
print(CENSUS.read_text())
