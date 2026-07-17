#!/usr/bin/env python3
"""PHASE A — RE-STAMP HISTORY TO HONEST CLOCKS (Dispatch 2, 07-17).

Builds the corrected event table for the full corpus and the census of the
old stamps' error (the formal indictment of the lying-clock fits).

Stamp hierarchy, named per event (never silently guessed):
  sched_honest   — Kalshi /milestones start_date (Sportradar per-match
                   schedule; serves the corpus back to January; minute
                   precision).
  official_ts    — second-precision actual start where the official cache
                   has it (state/daysheet_bells_official.json — live status
                   flips, recent era only).
  onset_est      — NAMED FALLBACK for the true right edge where no official
                   exists: first sustained activity rise in
                   kalshi_price_snapshots (volume_24h delta across
                   consecutive polls at/after sched_honest − 30min;
                   poll-cadence resolution, estimate-grade).
  old_stamp      — what the era's fits actually used: the snapshot table's
                   commence_time (kalshi_schedule_primary lineage).

right_edge = official_ts > onset_est (source stamped). corridor =
[sched_honest, right_edge]. Output row per event:
  {event, cat, era_month, old_stamp, sched_honest, sched_src, official_ts,
   onset_est, right_edge, right_edge_src, old_err_min}

Resumable: milestone results cached to state/milestone_starts.json every
200 events. Public endpoint, unauthenticated, paced ~4/s with 429 backoff.

Usage:  python3 analysis/corpus_restamp.py [--limit N]
Writes: state/corpus_events_v2.jsonl + /tmp/CORPUS_RESTAMP_CENSUS.md
"""
import json, sqlite3, sys, time, urllib.request
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "state/milestone_starts.json"
OUT = ROOT / "state/corpus_events_v2.jsonl"
CENSUS = Path("/tmp/CORPUS_RESTAMP_CENSUS.md")
LIMIT = None
if "--limit" in sys.argv:
    LIMIT = int(sys.argv[sys.argv.index("--limit") + 1])

def iso_ep(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None

def cat_of(et):
    if et.startswith("KXATPCHALLENGER"):
        return "ATP_CHALL"
    if et.startswith("KXWTACHALLENGER"):
        return "WTA_CHALL"
    if et.startswith("KXITFWMATCH"):
        return "ITF_W"
    if et.startswith("KXITFMATCH"):
        return "ITF_M"
    if et.startswith("KXWTAMATCH"):
        return "WTA_MAIN"
    if et.startswith("KXATPMATCH"):
        return "ATP_MAIN"
    return "?"

con = sqlite3.connect("file:%s?mode=ro" % (ROOT / "tennis.db"), uri=True,
                      timeout=5)

# ---- event universe + the old stamps (what the era's fits used) ---------
print("universe + old stamps ...", flush=True)
events = {}
for et, first_ts in con.execute(
        "SELECT event_ticker, MIN(first_ts) FROM historical_events "
        "GROUP BY event_ticker"):
    events[et] = {"first_trade": iso_ep(first_ts)}
old_stamp = {}
for et, ct in con.execute(
        "SELECT event_ticker, MIN(commence_time) FROM kalshi_price_snapshots "
        "WHERE commence_time IS NOT NULL GROUP BY event_ticker"):
    old_stamp[et] = iso_ep(ct)
for et in old_stamp:
    events.setdefault(et, {})
print("events:", len(events), "| with old stamp:", len(old_stamp), flush=True)

# ---- official actuals (second-precision, recent era) --------------------
official = {}
try:
    ob = json.loads((ROOT / "state/daysheet_bells_official.json").read_text())
    for ev, e in ob.items():
        if e.get("start_ep") and e.get("status") not in (None, "not_started"):
            official[ev] = float(e["start_ep"])
except Exception as e:
    print("official cache:", e)
print("official actuals:", len(official), flush=True)

# ---- milestone sched (resumable API sweep) ------------------------------
cache = {}
if CACHE.exists():
    try:
        cache = json.loads(CACHE.read_text())
    except ValueError:
        cache = {}
todo = [et for et in events if et not in cache]
if LIMIT:
    todo = todo[:LIMIT]
print("milestone sweep: %d cached, %d to fetch" % (len(cache), len(todo)),
      flush=True)
n_err = 0
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
        n_err += 1
        if "429" in str(e):
            time.sleep(5)
        cache[et] = {"err": str(e)[:60]}
    time.sleep(0.25)
    if i % 200 == 199:
        CACHE.write_text(json.dumps(cache))
        print("  %d/%d (err %d)" % (i + 1, len(todo), n_err), flush=True)
CACHE.write_text(json.dumps(cache))
print("milestone sweep done (err %d)" % n_err, flush=True)

# ---- onset estimate (named fallback) from snapshot volume deltas --------
print("onset estimates ...", flush=True)
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
    lo = (sh - 1800) if sh else None
    for ts, dv in series:
        if dv and dv > 0 and (lo is None or ts >= lo):
            onset[et] = ts
            return
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

# ---- assemble the corrected event table + census ------------------------
out_rows = []
err_by = defaultdict(list)
for et, rec in events.items():
    ms = cache.get(et) or {}
    sched = iso_ep(ms.get("start_date"))
    off = official.get(et)
    on = onset.get(et)
    right, rsrc = (off, "official_actual") if off else \
        ((on, "onset_snapshot_est") if on else
         (sched, "sched_only_no_evidence"))
    old = old_stamp.get(et)
    err_min = (round((old - sched) / 60.0, 1)
               if (old and sched) else None)
    cat = cat_of(et)
    month = et.split("-")[1][:5] if "-" in et else "?"
    out_rows.append({
        "event": et, "cat": cat, "era": month,
        "old_stamp": old, "sched_honest": sched,
        "sched_src": ("milestone_sportradar" if sched else "MISSING"),
        "official_ts": off, "onset_est": on,
        "right_edge": right, "right_edge_src": rsrc,
        "old_err_min": err_min})
    if err_min is not None:
        err_by[(cat,)].append(abs(err_min))
with open(OUT, "w") as fh:
    for r in out_rows:
        fh.write(json.dumps(r) + "\n")
print("wrote", OUT, len(out_rows), flush=True)

L = ["# PHASE A — CORPUS RE-STAMP CENSUS (the indictment of the "
     "lying-clock fits)", "",
     "- events: %d · milestone sched resolved: %d · official actuals: %d "
     "· onset fallbacks: %d"
     % (len(out_rows), sum(1 for r in out_rows if r["sched_honest"]),
        sum(1 for r in out_rows if r["official_ts"]),
        sum(1 for r in out_rows
            if r["right_edge_src"] == "onset_snapshot_est")), ""]
L.append("## |old stamp − honest sched| by category (minutes)")
import statistics
for (cat,), errs in sorted(err_by.items()):
    errs.sort()
    L.append("- %s: n=%d · median %.0f · p75 %.0f · p95 %.0f · max %.0f · "
             ">30min %.0f%% · >2h %.0f%%"
             % (cat, len(errs), statistics.median(errs),
                errs[int(0.75 * len(errs))], errs[int(0.95 * len(errs))],
                errs[-1],
                100.0 * sum(1 for e in errs if e > 30) / len(errs),
                100.0 * sum(1 for e in errs if e > 120) / len(errs)))
L.append("")
L.append("## sched → right-edge corridor (the tail where the entries live)")
cor = [(r["right_edge"] - r["sched_honest"]) / 60.0 for r in out_rows
       if r["right_edge"] and r["sched_honest"]
       and r["right_edge_src"] != "sched_only_no_evidence"]
if cor:
    cor.sort()
    L.append("- corridor length (min): n=%d · median %.0f · p75 %.0f · "
             "p95 %.0f" % (len(cor), statistics.median(cor),
                           cor[int(0.75 * len(cor))],
                           cor[int(0.95 * len(cor))]))
CENSUS.write_text("\n".join(L) + "\n")
print("census ->", CENSUS, flush=True)
print("\n".join(L))
