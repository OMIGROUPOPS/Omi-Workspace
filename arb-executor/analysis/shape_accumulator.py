#!/usr/bin/env python3
"""NIGHTLY SHAPE ACCUMULATOR — PLEX_REGRESSION_RULING §1 (2026-07-06).
Folds each slate's tape into the shape corpus (cat x 20c-bucket x 10-min T-minus bin,
bell = unambiguous tape onset; honest-era rows flagged), keeps a per-cell coverage
counter so the honest-era corpus is VISIBLE filling in, and fires the median
re-derivation AUTOMATICALLY when the coverage trigger is met (AIM_V2_SPEC §3:
>=50% of target cells — Tbin 12..36 x all buckets x {ITF_M,ITF_W,ATP_CHALL,WTA_CHALL}
— reach n_honest >= 30). Coverage, not vibes.

Outputs (append-only / rebuilt):
  data/shape_corpus/samples_<UTCDATE>.jsonl   one line per (leg,Tbin) sample
  data/shape_corpus/manifest.json             processed tickers (idempotent nightly)
  data/shape_corpus/coverage.json             per-cell n_total / n_honest + trigger state
  data/shape_corpus/derived_<date>.json       median table (min-n gate per AIM_V2_SPEC §5:
                                              below-floor cells null/parked, NEVER silently
                                              interpolated) — written when the trigger fires
  /root/Omi-Workspace/.claude/shape_corpus_reports/SHAPE_RERUN_REPORT_<date>.md
Then commits+pushes its outputs (push-after-commit law). READ-ONLY vs bot state.
Cron: 45 4 * * * (installed by deploy/install_shape_accum_cron.sh)."""
import json, gzip, sys, subprocess, time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
ROOT = Path(__file__).resolve().parents[1]           # arb-executor
REPO = ROOT.parent                                    # Omi-Workspace
CORPUS = ROOT / "data" / "shape_corpus"
REPORTS = REPO / ".claude" / "shape_corpus_reports"
CORPUS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

BIN = 600; GRID = 48
FLOOR = 30                                            # AIM_V2_SPEC hard min-n
HONEST_ERA_START = datetime(2026, 7, 6, 3, 50, tzinfo=timezone.utc).timestamp()  # flip boot
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), None)
def buck(px): return min(4, max(0, int(px)//20))
TARGET_CATS = {"ITF_M","ITF_W","ATP_CHALL","WTA_CHALL"}
TARGET_TBINS = range(12, 37)

_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None

def read_tape(f):
    rows=[]
    op = gzip.open if f.suffix == ".gz" else open
    try:
        with op(f, "rt", encoding="utf-8", errors="replace") as fh:
            next(fh, None)
            for ln in fh:
                p = ln.rstrip("\n").split(",")
                if len(p) < 5: continue
                t = pts(p[0])
                if t is None: continue
                try: rows.append((t, int(p[2]), int(float(p[3]))))
                except: continue
    except Exception:
        return []
    rows.sort()
    return rows

# [C-RETENTION + PLEX_AIM_V2_RULING] observed true starts (tennis.db observed_starts,
# read-only) are PREFERRED as the bell where present; LATCH-CAL bar (K=600/M=20000,
# the ruled canonical axis) for everything unobserved. Every sample now carries
# bell_src ('observed'|'latchcal_bar'); pre-2026-07-07 samples were bar150 (untagged) --
# derivation re-detects independently, so the mix touches coverage/harness only (stated).
import sqlite3 as _sql, re as _re
def _load_observed():
    out={}
    try:
        conn=_sql.connect("file:"+str(ROOT/"tennis.db")+"?mode=ro",uri=True,timeout=5)
        for mid,p1,p2,ts in conn.execute("select te_match_id,player1,player2,first_inplay_at from observed_starts"):
            def pre(n):
                n=(n or "").strip().split(" ")[0].upper()
                return _re.sub(r"[^A-Z]","",n)[:3]
            try:
                t=datetime.strptime(ts,"%Y-%m-%d %H:%M:%S").replace(tzinfo=ET).timestamp()
            except Exception:
                continue
            d=ts[:10]
            for k in (pre(p1)+pre(p2), pre(p2)+pre(p1)):
                out.setdefault((k,d),t)
        conn.close()
    except Exception:
        pass
    return out
_OBS=_load_observed()
def observed_bell(name):
    m=_re.search(r"-(\d{2}[A-Z]{3}\d{2})([A-Z]{4,8})-", name+"-")
    if not m: return None
    MON={"JAN":"01","FEB":"02","MAR":"03","APR":"04","MAY":"05","JUN":"06","JUL":"07","AUG":"08"}
    dc=m.group(1); pc=m.group(2)
    try: d=f"20{dc[:2]}-{MON[dc[2:5]]}-{dc[5:7]}"
    except Exception: return None
    for k in ((pc,d),(pc[3:]+pc[:3],d)) if len(pc)==6 else ((pc,d),):
        if k in _OBS: return _OBS[k]
    return None

def tape_gun(rows):
    if not rows: return None
    mv = defaultdict(float)
    for t, pr, ct in rows: mv[int(t//60)*60] += ct
    mins = sorted(mv)
    fwd = {m: sum(mv[x] for x in mins if m <= x < m+600) for m in mins}
    return next((m for m in mins if mv[m] >= 150 and fwd[m] >= 3000), None)

# ---------- 1. fold new tickers into the corpus ----------
man_p = CORPUS / "manifest.json"
manifest = set(json.load(open(man_p))) if man_p.exists() else set()
today = datetime.now(timezone.utc).strftime("%Y%m%d")
out_f = open(CORPUS / f"samples_{today}.jsonl", "a", encoding="utf-8")
new_legs = 0; new_samples = 0
for f in sorted((ROOT / "analysis" / "trades").iterdir()):
    name = f.name.replace(".csv.gz","").replace(".csv","")
    if name in manifest: continue
    c = cat_of(name)
    if not c: continue
    rows = read_tape(f)
    if len(rows) < 30:
        # small tapes may still grow today; only mark done if file is older than 24h
        if time.time() - f.stat().st_mtime > 86400: manifest.add(name)
        continue
    # only fold CONCLUDED tapes: last print older than 6h (the match is over)
    if time.time() - rows[-1][0] < 6*3600: continue
    bell = observed_bell(name)
    bell_src = "observed" if bell is not None else None
    if bell is None:
        bell = tape_gun(rows); bell_src = "latchcal_bar"
    manifest.add(name)
    if bell is None: continue
    pre = [(t,pr) for t,pr,ct in rows if t <= bell]
    if len(pre) < 8: continue
    bell_px = pre[-1][1]
    era = "honest" if bell >= HONEST_ERA_START else "card"
    binpx = {}
    for t, pr in pre:
        tb = int((bell - t)//BIN)
        if 0 <= tb <= GRID: binpx[tb] = pr
    mins_after = {}; cur = 10**9
    for t, pr in reversed(pre):
        cur = min(cur, pr); mins_after[t] = cur
    lastmin = {}
    for t, pr in pre:
        tb = int((bell - t)//BIN)
        if 0 <= tb <= GRID: lastmin[tb] = (pr, mins_after[t])
    new_legs += 1
    for tb, (pr, mn) in lastmin.items():
        out_f.write(json.dumps({"tk": name, "cat": c, "b": buck(pr), "t": tb,
                                "drift": bell_px - pr, "dip": mn - pr, "era": era,
                                # [07-09 FIX] bell_src was computed (:135-137) but
                                # never serialized -- n_honest read 0 on all 64,644
                                # samples; the 0/500 coverage was STRUCTURAL.
                                "bell_src": bell_src,
                                "bell": int(bell)}) + "\n")
        new_samples += 1
out_f.close()
json.dump(sorted(manifest), open(man_p, "w"))
print(f"folded {new_legs} new legs / {new_samples} samples", file=sys.stderr)

# ---------- 2. rebuild coverage ----------
cells = defaultdict(lambda: {"n": 0, "n_honest": 0})
for sf in sorted(CORPUS.glob("samples_*.jsonl")):
    for line in open(sf, encoding="utf-8"):
        try: s = json.loads(line)
        except: continue
        key = f"{s['cat']}|{s['b']}|{s['t']}"
        cells[key]["n"] += 1
        if s.get("era") == "honest": cells[key]["n_honest"] += 1
target = [f"{c}|{b}|{t}" for c in TARGET_CATS for b in range(5) for t in TARGET_TBINS]
covered = sum(1 for k in target if cells.get(k, {}).get("n_honest", 0) >= FLOOR)
cov_share = covered / len(target)
trigger = cov_share >= 0.50
cov_p = CORPUS / "coverage.json"
prev = json.load(open(cov_p)) if cov_p.exists() else {}
already_fired = prev.get("trigger_fired_at")
json.dump({"generated": datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
           "floor": FLOOR, "target_cells": len(target), "covered": covered,
           "coverage_share": round(cov_share, 4), "trigger": trigger,
           "trigger_fired_at": already_fired or (today if trigger else None),
           "cells": cells}, open(cov_p, "w"), indent=1)
print(f"coverage: {covered}/{len(target)} target cells at n_honest>={FLOOR} ({cov_share:.1%}) trigger={trigger}", file=sys.stderr)

# ---------- 3. coverage-triggered re-derivation (median, min-n gated, NO silent interp) ----------
if trigger and not already_fired:
    vals = defaultdict(lambda: ([], []))
    for sf in sorted(CORPUS.glob("samples_*.jsonl")):
        for line in open(sf, encoding="utf-8"):
            try: s = json.loads(line)
            except: continue
            if s.get("era") != "honest": continue     # honest-era derivation
            d, dp = vals[(s["cat"], s["b"], s["t"])]
            d.append(s["drift"]); dp.append(s["dip"])
    def med(v): v = sorted(v); return v[len(v)//2] if v else None
    def sd(v):
        if len(v) < 2: return None
        m = sum(v)/len(v)
        return round((sum((x-m)**2 for x in v)/(len(v)-1))**0.5, 2)
    table = {}
    for (c, b, t), (d, dp) in vals.items():
        key = f"{c}|{b}"
        cell = ({"n": len(d), "n_honest": len(d), "drift": med(d), "dip": med(dp),
                 "resid_sd": sd(d), "null_reason": None} if len(d) >= FLOOR else
                {"n": len(d), "n_honest": len(d), "drift": None, "dip": None,
                 "resid_sd": None, "null_reason": "below_floor"})
        table.setdefault(key, {})[t] = cell
    dp_ = CORPUS / f"derived_{today}.json"
    json.dump(table, open(dp_, "w"), indent=1)
    (CORPUS / "derived_latest.json").write_text(json.dumps(table))
    rep = REPORTS / f"SHAPE_RERUN_REPORT_{today}.md"
    n_ok = sum(1 for bb in table.values() for cell in bb.values() if not cell["null_reason"])
    n_park = sum(1 for bb in table.values() for cell in bb.values() if cell["null_reason"])
    rep.write_text(f"""# SHAPE RERUN REPORT — {today} (coverage trigger fired)
Coverage: {covered}/{len(target)} target cells at n_honest>={FLOOR} ({cov_share:.1%}).
Derived (honest-era, median, HARD min-n gate — below-floor cells PARKED, never interpolated):
{n_ok} live cells / {n_park} parked. Table: data/shape_corpus/derived_{today}.json (+ derived_latest.json).
Next per AIM_V2_SPEC: run analysis/aim_v2_harness.py (walk-forward) -> Lane-1 bars -> Plex.
NOTHING ARMS from this report.
""", encoding="utf-8")
    print(f"TRIGGER FIRED: derived table written ({n_ok} live / {n_park} parked cells)", file=sys.stderr)

# ---------- 4. commit + push (push-after-commit law) ----------
def sh(*args):
    return subprocess.run(args, cwd=str(REPO), capture_output=True, text=True, timeout=120)
try:
    sh("git", "add", str(CORPUS.relative_to(REPO)), ".claude/shape_corpus_reports")
    r = sh("git", "commit", "-m", f"shape-accumulator {today}: +{new_legs} legs, coverage {covered}/{len(target)} ({cov_share:.1%})" + (" [TRIGGER FIRED]" if trigger and not already_fired else ""))
    if r.returncode == 0:
        sh("git", "pull", "--rebase", "--autostash", "origin", "blend/kalshi-occ-fallback")
        p = sh("git", "push", "origin", "blend/kalshi-occ-fallback")
        print("pushed" if p.returncode == 0 else f"push failed: {p.stderr[:200]}", file=sys.stderr)
    else:
        print("nothing to commit", file=sys.stderr)
except Exception as e:
    print(f"git step failed: {e}", file=sys.stderr)
