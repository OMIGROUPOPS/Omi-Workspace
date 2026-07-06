#!/usr/bin/env python3
"""[READ-ONLY] THE ONE AIM FIX — build + replay. Two phases, one run.
PHASE A (shapes): per (cat x price-bucket x T-minus bin), from the historical tape corpus
  (analysis/trades/*, EXCLUDING 26JUL06 = no self-leak; bell = unambiguous tape_gun onset):
  med_drift = median(bell_px - px_at_T)   -> FV_hat(p,T) = p + med_drift  (own-FV, current-anchored)
  med_dip   = median(min px in [t,bell] - px_at_T) -> aim(p,T) = p + med_dip (dip-informed
  discount to own FV; A49 preserved: the aim is the fillable dip, FV is the yardstick).
PHASE B (replay, census 161 concluded games, pair-coherent):
  per leg: from its FIRST actual post time to the bell, step 10min: p = last trade,
  aim = clamp(p + med_dip, 1, FV_hat - 1); CAP ONLY: if sibling already filled in sim,
  aim = min(aim, 97 - sib_fill). Fill: first step whose next-10min sell-flow prints <= aim.
  The step sequence IS the walk model (aims re-derive; never above FV_hat - 1).
  Lane-1: joint paid-vs-achievable gap, participation, lazy-leg-1 (fill >= own FV_hat).
  Lane-2: settled P&L via actual market results (n flagged).
Writes /tmp/fv_shapes.json + /tmp/fv_replay.json. NO writes to bot state."""
import json, sys, gzip, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
BIN = 600; GRID = 48   # 10-min bins to 8h
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), None)
BUCK = 20
def buck(px): return min(4, max(0, int(px)//BUCK))

_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None

def read_tape_path(f):
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
                try: rows.append((t, int(p[2]), int(float(p[3])), p[4]))
                except: continue
    except Exception:
        return []
    rows.sort()
    return rows

def tape_gun(rows):
    if not rows: return None
    mv = defaultdict(float)
    for t, pr, ct, s in rows: mv[int(t//60)*60] += ct
    mins = sorted(mv)
    fwd = {m: sum(mv[x] for x in mins if m <= x < m+600) for m in mins}
    gun = next((m for m in mins if mv[m] >= 150 and fwd[m] >= 3000), None)
    if gun is None: return None          # unambiguous only
    return gun

# ---------------- PHASE A ----------------
samples = defaultdict(lambda: defaultdict(lambda: ([], [])))  # (cat,buck)[Tbin] -> (drifts, dips)
n_legs = 0
for f in sorted(Path("analysis/trades").iterdir()):
    name = f.name.replace(".csv.gz","").replace(".csv","")
    if "26JUL06" in name: continue     # no self-leak
    c = cat_of(name)
    if not c: continue
    rows = read_tape_path(f)
    if len(rows) < 30: continue
    bell = tape_gun(rows)
    if bell is None: continue
    pre = [(t,pr) for t,pr,ct,s in rows if t <= bell]
    if len(pre) < 8: continue
    bell_px = pre[-1][1]
    n_legs += 1
    # per bin: last price in bin; dip = min price from that time to bell
    binpx = {}
    for t, pr in pre:
        tb = int((bell - t)//BIN)
        if 0 <= tb <= GRID: binpx[tb] = (t, pr)   # later t overwrites -> last in bin
    mins_after = {}
    cur = 10**9
    for t, pr in reversed(pre):
        cur = min(cur, pr)
        mins_after[t] = cur
    for tb, (t, pr) in binpx.items():
        d, dp = samples[(c, buck(pr))][tb]
        d.append(bell_px - pr); dp.append(mins_after[t] - pr)
def med(v):
    v = sorted(v); return v[len(v)//2] if v else None
shapes = {}
for key, bins in samples.items():
    shapes[key] = {tb: {"n": len(d), "drift": med(d), "dip": med(dp)}
                   for tb, (d, dp) in bins.items() if len(d) >= 8}
json.dump({f"{k[0]}|{k[1]}": v for k, v in shapes.items()}, open("/tmp/fv_shapes.json","w"))
print(f"PHASE A: {n_legs} corpus legs (pre-JUL06), {len(shapes)} (cat,bucket) shapes", file=sys.stderr)

def shape_at(c, b, tb):
    for db in range(0, 5):
        for cand in (tb-db, tb+db):
            v = shapes.get((c, b), {}).get(cand)
            if v: return v
    return None

# ---------------- PHASE B ----------------
D = json.load(open("/tmp/census_dump.json"))
conc = [g for g in D["games"] if g["concluded"]]
def parse_hm(s):
    if not s: return None
    try: return datetime.strptime("2026-"+s, "%Y-%m-%d %H:%M").replace(tzinfo=ET).timestamp()
    except: return None

out = []
for g in conc:
    bell = parse_hm(g.get("onset_t")) if not g.get("onset_amb") else None
    if bell is None: bell = parse_hm(g.get("hstart_t")) or parse_hm(g.get("sstart_t"))
    if bell is None: continue
    legs = []
    for l in g["legs"]:
        tk = l["tk"] if l["tk"].startswith("KX") else "KX"+l["tk"]
        f = Path("analysis/trades")/(tk+".csv")
        if not f.exists(): f = Path("analysis/trades")/(tk+".csv.gz")
        rows = read_tape_path(f) if f.exists() else []
        legs.append({"l": l, "rows": rows})
    # simulate legs jointly on a 10-min grid from earliest post to bell
    posts = [x["l"].get("post_ts") for x in legs if x["l"].get("post_ts")]
    if not posts: continue
    t0 = min(float(p) for p in posts)
    sim = {i: {"fill": None, "aim_path": [], "lazy": None, "fv_at_fill": None} for i in range(len(legs))}
    t = t0
    while t < bell:
        for i, L in enumerate(legs):
            if sim[i]["fill"] is not None: continue
            if L["l"].get("post_ts") and t < float(L["l"]["post_ts"]) - 1: continue
            rows = L["rows"]
            pre = [(tt, pr) for tt, pr, ct, s in rows if tt <= t]
            if not pre: continue
            p = pre[-1][1]
            tb = int((bell - t)//BIN)
            sh = shape_at(g["cat"], buck(p), tb)
            if not sh: continue
            fv = p + sh["drift"]
            aim = p + sh["dip"]
            aim = max(1, min(aim, fv - 1))
            # CAP only: sibling basis in sim
            j = 1 - i
            if len(legs) == 2 and sim[j]["fill"] is not None:
                aim = min(aim, 97 - sim[j]["fill"])
            if aim < 1: aim = 1
            sim[i]["aim_path"].append((round((bell-t)/60), p, aim, round(fv,1)))
            hits = [pr for tt, pr, ct, s in rows if s == "no" and t <= tt < t + BIN and pr <= aim]
            if hits:
                sim[i]["fill"] = aim   # maker at aim: filled at our level
                sim[i]["fv_at_fill"] = fv
                sim[i]["lazy"] = aim >= fv
        t += BIN
    filled = [sim[i]["fill"] for i in range(len(legs)) if sim[i]["fill"] is not None]
    comb_new = round(sum(filled), 1) if len(legs) == 2 and len(filled) == 2 else None
    # actual (old) numbers from census
    old_fills = [x["l"].get("fill_px") for x in legs]
    comb_old = g.get("combined")
    # old lazy-leg-1: actual fill >= FV_hat at the actual fill moment (approx: use shape at fill bin)
    lazy_old = []
    for x in legs:
        l = x["l"]
        if l.get("fill_px") is None or not l.get("fill_ts"): lazy_old.append(None); continue
        ft = float(l["fill_ts"])
        if ft >= bell: lazy_old.append(None); continue
        pre = [(tt, pr) for tt, pr, ct, s in x["rows"] if tt <= ft]
        if not pre: lazy_old.append(None); continue
        sh = shape_at(g["cat"], buck(pre[-1][1]), int((bell-ft)//BIN))
        lazy_old.append(bool(l["fill_px"] >= pre[-1][1] + sh["drift"]) if sh else None)
    # settled P&L per sim (results known)
    pnl_new = pnl_old = 0.0; have_res = True
    for i, x in enumerate(legs):
        r = x["l"].get("result")
        if r not in ("yes","no"): have_res = False; continue
        q = 5
        if sim[i]["fill"] is not None:
            pnl_new += q*(100-sim[i]["fill"])/100.0 if r == "yes" else -q*sim[i]["fill"]/100.0
        if x["l"].get("fill_px") is not None:
            pnl_old += q*(100-x["l"]["fill_px"])/100.0 if r == "yes" else -q*x["l"]["fill_px"]/100.0
    out.append({"ev": g["ev"], "cat": g["cat"],
                "old_part": g["participation"], "new_part": len(filled),
                "comb_old": comb_old, "comb_new": comb_new,
                "best_ach": g.get("best_achievable"),
                "new_fills": [sim[i]["fill"] for i in range(len(legs))],
                "old_fills": old_fills,
                "lazy_old": lazy_old,
                "lazy_new": [sim[i]["lazy"] for i in range(len(legs))],
                "steps_used": [len(sim[i]["aim_path"]) for i in range(len(legs))],
                "fill_step": [next((k for k,ap in enumerate(sim[i]["aim_path"])), None) for i in range(len(legs))],
                "pnl_old": round(pnl_old,2) if have_res else None,
                "pnl_new": round(pnl_new,2) if have_res else None})
json.dump(out, open("/tmp/fv_replay.json","w"))

# ---- rollup ----
both_old = sum(1 for r in out if r["old_part"] == "both")
both_new = sum(1 for r in out if r["new_part"] == 2)
gap_old = [r["comb_old"] - r["best_ach"] for r in out if r["comb_old"] and r["best_ach"]]
gap_new = [r["comb_new"] - r["best_ach"] for r in out if r["comb_new"] and r["best_ach"]]
lz_o = sum(1 for r in out for x in r["lazy_old"] if x is True)
lz_o_n = sum(1 for r in out for x in r["lazy_old"] if x is not None)
lz_n = sum(1 for r in out for x in r["lazy_new"] if x is True)
lz_n_n = sum(1 for r in out for x in r["lazy_new"] if x is not None)
pn = [(r["pnl_new"], r["pnl_old"]) for r in out if r["pnl_new"] is not None and r["pnl_old"] is not None]
print(f"PHASE B: {len(out)} games replayed", file=sys.stderr)
print(f"participation: old both={both_old} new both={both_new}", file=sys.stderr)
print(f"joint gap (paid-vs-achievable): old med {med(gap_old)} (n={len(gap_old)}) new med {med(gap_new)} (n={len(gap_new)})", file=sys.stderr)
print(f"lazy-leg (fill>=own FV): old {lz_o}/{lz_o_n} new {lz_n}/{lz_n_n}", file=sys.stderr)
print(f"Lane-2 settled: old ${sum(p[1] for p in pn):.2f} new ${sum(p[0] for p in pn):.2f} (n={len(pn)} games)", file=sys.stderr)
