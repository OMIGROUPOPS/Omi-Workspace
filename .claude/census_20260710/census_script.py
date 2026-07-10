#!/usr/bin/env python3
"""BOARD -1b1: CLOCK CROSS-CALIBRATION CENSUS (read-only).
Three start-derivations: (a) match_facts_v3 mid-jump DETECTOR (re-run on
live-era premarket_ticks -- the archive window 03-20..04-10 shares no matches
with the live sources, so the DETECTOR is what gets cross-calibrated),
(b) gun volume-onset (jsonl gun_fired), (c) TE observed_starts.
Detector params replicate build_match_facts_v3.py: JUMP_CENTS=3,
JUMP_WINDOW_SEC=30, SUSTAIN_WINDOWS=2 (30s grid reimplementation, noted).
Self-contamination flag: events with our entry_filled since 07-06."""
import csv, glob, gzip, json, sqlite3, sys, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ROOT = "/root/Omi-Workspace/arb-executor"
ET = timezone(timedelta(hours=-4))
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
def cat_of(ev):
    for k, v in CAT.items():
        if ev.startswith(k): return v
    return None

# ---- (b) gun fires + our fills from jsonl (07-06 .. now) ----
guns, fills_ev = {}, set()
for p in sorted(glob.glob(ROOT + "/logs/live_v3_202607*.jsonl") +
                glob.glob(ROOT + "/logs/live_v3_202607*.jsonl.gz")):
    day = p.split("live_v3_")[1][:8]
    if day < "20260706": continue
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"gun_fired"' in line:
                try: d = json.loads(line)
                except ValueError: continue
                det = d.get("details") or {}
                ev = det.get("event", "")
                if ev and ev not in guns:
                    guns[ev] = {"ts": d.get("ts_epoch", 0), "source": det.get("source"),
                                "lag": det.get("feed_lag_sec")}
            elif '"entry_filled"' in line:
                try: d = json.loads(line)
                except ValueError: continue
                tk = d.get("ticker", "")
                if tk: fills_ev.add(tk.rsplit("-", 1)[0])

# ---- (c) TE observed_starts, both-leg matcher (scorecard's fixed join) ----
con = sqlite3.connect("file:%s/tennis.db?mode=ro" % ROOT, uri=True, timeout=5)
rows = con.execute("SELECT player1,player2,kalshi_ticker,first_inplay_at FROM observed_starts").fetchall()
con.close()
known = set(guns)
# also add events with tick files (so TE-only matches can enter A'xC)
tickfiles = glob.glob(ROOT + "/analysis/premarket_ticks/*.csv*")
for f in tickfiles:
    tk = f.split("/")[-1].split(".csv")[0]
    known.add(tk.rsplit("-", 1)[0])
ev_pair = {ev: ev.rsplit("-", 1)[-1][-6:].upper() for ev in known}
te = {}
for p1, p2, kc, fia in rows:
    sides = []
    for nm in (p1 or "", p2 or ""):
        s = set()
        for part in nm.replace(".", " ").replace(",", " ").replace("-", " ").split():
            if len(part) >= 3: s.add(part[:3].upper())
        sides.append(s)
    both = [ev for ev, pr in ev_pair.items()
            if (pr[:3] in sides[0] and pr[3:] in sides[1]) or (pr[:3] in sides[1] and pr[3:] in sides[0])]
    if len(both) == 1:
        try:
            t = datetime.strptime(fia, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ET).timestamp()
        except Exception: continue
        if both[0] not in te or t < te[both[0]]: te[both[0]] = t

# ---- (a') mid-jump detector on live-era ticks ----
_daycache = {}
def _fastts(d0):
    # 'YYYY-MM-DD HH:MM:SS AM/PM' ET -> epoch (manual parse; strptime is 10x slower)
    day = d0[:10]
    base = _daycache.get(day)
    if base is None:
        base = datetime(int(day[:4]), int(day[5:7]), int(day[8:10]), tzinfo=ET).timestamp()
        _daycache[day] = base
    hh = int(d0[11:13]) % 12 + (12 if d0[20:22] == "PM" else 0)
    return base + hh * 3600 + int(d0[14:16]) * 60 + int(d0[17:19])

def midjump(ev):
    """First sustained mid-jump >=3c/30s x2 windows across the event's legs.
    30s grid over each leg's tick file; earliest trigger wins."""
    best = None
    for f in glob.glob(ROOT + "/analysis/premarket_ticks/" + ev + "-*.csv*"):
        op = gzip.open if f.endswith(".gz") else open
        try:
            with op(f, "rt", encoding="utf-8", errors="replace") as fh:
                next(fh, None)
                grid = {}   # 30s bucket -> last mid
                for ln in fh:
                    p = ln.split(",")
                    if len(p) < 23: continue
                    try:
                        ts = _fastts(p[0])
                        mid = float(p[22])
                    except Exception: continue
                    grid[int(ts // 30)] = mid
            ks = sorted(grid)
            run = 0
            for i in range(1, len(ks)):
                if ks[i] - ks[i-1] == 1 and abs(grid[ks[i]] - grid[ks[i-1]]) >= 3:
                    run += 1
                    if run >= 2:
                        t0 = (ks[i-1]) * 30
                        if best is None or t0 < best: best = t0
                        break
                else:
                    run = 0
        except OSError: continue
    return best

# events eligible: has gun or te AND has tick files
cands = sorted(ev for ev in (set(guns) | set(te)) & set(ev_pair)
               if any(t in ev for t in ("26JUL08", "26JUL09", "26JUL10")))
mj = {}
for ev in cands:
    m = midjump(ev)
    if m: mj[ev] = m

def stats(deltas):
    if not deltas: return None
    d = sorted(deltas); n = len(d)
    pct = lambda x: d[min(n-1, int(x*n))]
    w = lambda m: round(100.0*sum(1 for x in d if abs(x) <= m)/n, 1)
    return {"n": n, "med": round(pct(0.5), 1), "p10": round(pct(0.10), 1),
            "p90": round(pct(0.90), 1), "w5": w(5), "w15": w(15), "w30": w(30)}

out = {"generated": datetime.now(ET).strftime("%Y-%m-%d %I:%M %p ET"),
       "overlap_def": {
           "window": "2026-07-06 .. now (TE bank exists Jul 6+; gun era Jul 8+; archive file 03-20..04-10 shares NO matches -> the DETECTOR re-runs on live premarket_ticks)",
           "n_gun": len(guns), "n_te_joined": len(te), "n_midjump": len(mj),
           "n_candidates": len(cands), "n_fills_events": len(fills_ev)},
       "pairs": {}}
for name, pair in (("midjump_vs_gun", (mj, guns)), ("midjump_vs_te", (mj, te)), ("gun_vs_te", (guns, te))):
    A, B = pair
    per = defaultdict(lambda: {"all": [], "ours": [], "clean": []})
    for ev in set(A) & set(B):
        c = cat_of(ev)
        if not c: continue
        a = A[ev]["ts"] if isinstance(A[ev], dict) else A[ev]
        b = B[ev]["ts"] if isinstance(B[ev], dict) else B[ev]
        dmin = (a - b) / 60.0
        per[c]["all"].append(dmin)
        per[c]["ours" if ev in fills_ev else "clean"].append(dmin)
    out["pairs"][name] = {c: {k: stats(v) for k, v in d.items()} for c, d in per.items()}

# ---- Part 2: fallback tail from the archive file ----
rows = list(csv.DictReader(open(ROOT + "/data/match_facts_v3.csv")))
tail = defaultdict(lambda: defaultdict(int))
volq = defaultdict(list)
for r in rows:
    tail[r["category"]][r["pregame_detection_method"]] += 1
    if r["pregame_detection_method"].startswith("fallback"):
        try: volq["fallback"].append(float(r["volume_fp"]))
        except Exception: pass
    elif r["pregame_detection_method"] == "jump":
        try: volq["jump"].append(float(r["volume_fp"]))
        except Exception: pass
def vstats(v):
    if not v: return None
    v = sorted(v); n = len(v)
    return {"n": n, "med": round(v[n//2]), "p10": round(v[int(0.1*n)]), "p90": round(v[min(n-1,int(0.9*n))])}
out["fallback_tail"] = {c: dict(m) for c, m in tail.items()}
out["fallback_volume"] = {k: vstats(v) for k, v in volq.items()}
out["itf_absent_from_archive"] = True

print(json.dumps(out, indent=1))
