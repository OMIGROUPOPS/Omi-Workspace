#!/usr/bin/env python3
"""[READ-ONLY] THE ONE AIM FIX v2 — quantile-sweep build + replay.
Same frame as v1 (aim = dip-informed discount to OWN FV, current-price-anchored,
goal-basis as CAP only, walk = the 10-min re-derivation trajectory bounded at FV-1).
v1 finding: P50 dip collapses participation (133->56). v2 sweeps the dip quantile
q in {0.5, 0.6, 0.75, 0.9} (q=0.9 = shallow: 90% of similar legs' tapes touched it)
and reports the participation/price/lazy frontier per q. Shapes exclude 26JUL06."""
import json, sys, gzip
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
BIN = 600; GRID = 48
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), None)
def buck(px): return min(4, max(0, int(px)//20))
QS = (0.5, 0.6, 0.75, 0.9)

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
    return next((m for m in mins if mv[m] >= 150 and fwd[m] >= 3000), None)

def med(v):
    v = sorted(x for x in v if x is not None); return v[len(v)//2] if v else None
def quant(v, q):
    v = sorted(v)
    return v[min(len(v)-1, int(len(v)*q))] if v else None

# ---------------- PHASE A ----------------
samples = defaultdict(lambda: defaultdict(lambda: ([], [])))
n_legs = 0
for f in sorted(Path("analysis/trades").iterdir()):
    name = f.name.replace(".csv.gz","").replace(".csv","")
    if "26JUL06" in name: continue
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
    binpx = {}
    for t, pr in pre:
        tb = int((bell - t)//BIN)
        if 0 <= tb <= GRID: binpx[tb] = (t, pr)
    mins_after = {}
    cur = 10**9
    for t, pr in reversed(pre):
        cur = min(cur, pr)
        mins_after[t] = cur
    for tb, (t, pr) in binpx.items():
        d, dp = samples[(c, buck(pr))][tb]
        d.append(bell_px - pr); dp.append(mins_after[t] - pr)

shapes = {}
for key, bins in samples.items():
    shapes[key] = {tb: {"n": len(d), "drift": {q: quant(d, q) for q in QS},
                        "dip": {q: quant(dp, q) for q in QS}}
                   for tb, (d, dp) in bins.items() if len(d) >= 30}   # AIM_V2_SPEC hard floor; below = PARKED
json.dump({f"{k[0]}|{k[1]}": {tb: {"n": v["n"],
                                    "drift": {str(q): x for q, x in v["drift"].items()},
                                    "dip": {str(q): x for q, x in v["dip"].items()}}
                              for tb, v in bb.items()}
           for k, bb in shapes.items()}, open("/tmp/fv_shapes.json","w"))
print(f"PHASE A: {n_legs} corpus legs, {len(shapes)} (cat,bucket) shapes", file=sys.stderr)

def shape_at(c, b, tb):
    """Explicit neighbor borrow (AIM_V2_SPEC §5): returns (cell, bin_used).
    bin_used != tb => BORROWED, and every consumer counts it first-class."""
    for db in range(0, 5):
        for cand in (tb-db, tb+db):
            v = shapes.get((c, b), {}).get(cand)
            if v: return v, cand
    return None, None

# ---------------- PHASE B ----------------
D = json.load(open("/tmp/census_dump.json"))
conc = [g for g in D["games"] if g["concluded"]]
def parse_hm(s):
    if not s: return None
    try: return datetime.strptime("2026-"+s, "%Y-%m-%d %H:%M").replace(tzinfo=ET).timestamp()
    except: return None

# pre-load census game tapes once
CORR_EST = {"ITF_M": 72, "ITF_W": 77, "ATP_CHALL": 19, "WTA_CHALL": 5, "ATP_MAIN": 30, "WTA_MAIN": 30}
prepped = []
for g in conc:
    bell = parse_hm(g.get("onset_t")) if not g.get("onset_amb") else None
    if bell is None: bell = parse_hm(g.get("latch_t"))
    if bell is None:
        hs = parse_hm(g.get("hstart_t")) or parse_hm(g.get("sstart_t"))
        bell = (hs + 60*CORR_EST.get(g["cat"], 30)) if hs else None
    if bell is None: continue
    legs = []
    for l in g["legs"]:
        tk = l["tk"] if l["tk"].startswith("KX") else "KX"+l["tk"]
        f = Path("analysis/trades")/(tk+".csv")
        if not f.exists(): f = Path("analysis/trades")/(tk+".csv.gz")
        legs.append({"l": l, "rows": read_tape_path(f) if f.exists() else []})
    posts = [x["l"].get("post_ts") for x in legs if x["l"].get("post_ts")]
    if not posts: continue
    prepped.append((g, bell, legs, min(float(p) for p in posts)))

def run_sim(fvq, q):
    out = []
    for g, bell, legs, t0 in prepped:
        sim = {i: {"fill": None, "steps": 0, "fill_step": None, "lazy": None,
                   "aim": None, "fv": None} for i in range(len(legs))}
        t = t0
        while t < bell:
            for i, L in enumerate(legs):
                if sim[i]["fill"] is not None: continue
                if L["l"].get("post_ts") and t < float(L["l"]["post_ts"]) - 1: continue
                rows = L["rows"]
                pre = [(tt, pr) for tt, pr, ct, s in rows if tt <= t]
                if not pre: continue
                p = pre[-1][1]
                _tb = int((bell - t)//BIN)
                sh, _bin = shape_at(g["cat"], buck(p), _tb)
                if sh and _bin != _tb: sim[i]["borrowed"] = sim[i].get("borrowed", 0) + 1
                if sh:  # re-derive; on a shape gap the RESTING bid carries (real semantics)
                    fv = p + sh["drift"][fvq]
                    aim = max(1, min(p + sh["dip"][q], fv - 1))
                    sim[i]["aim"] = aim; sim[i]["fv"] = fv
                if sim[i]["aim"] is None: continue
                aim = sim[i]["aim"]
                j = 1 - i
                if len(legs) == 2 and sim[j]["fill"] is not None:
                    aim = min(aim, 97 - sim[j]["fill"])
                if aim < 1: aim = 1
                sim[i]["steps"] += 1
                hits = [pr for tt, pr, ct, s in rows if s == "no" and t <= tt < t + BIN and pr <= aim]
                if hits:
                    sim[i]["fill"] = aim
                    sim[i]["fill_step"] = sim[i]["steps"] - 1
                    sim[i]["lazy"] = (aim >= sim[i]["fv"]) if sim[i]["fv"] is not None else None
            t += BIN
        filled = [sim[i]["fill"] for i in range(len(legs)) if sim[i]["fill"] is not None]
        comb_new = round(sum(filled), 1) if len(legs) == 2 and len(filled) == 2 else None
        pnl_new = pnl_old = 0.0; have_res = True
        for i, x in enumerate(legs):
            r = x["l"].get("result")
            if r not in ("yes","no"): have_res = False; continue
            if sim[i]["fill"] is not None:
                pnl_new += 5*(100-sim[i]["fill"])/100.0 if r == "yes" else -5*sim[i]["fill"]/100.0
            if x["l"].get("fill_px") is not None:
                pnl_old += 5*(100-x["l"]["fill_px"])/100.0 if r == "yes" else -5*x["l"]["fill_px"]/100.0
        out.append({"ev": g["ev"], "cat": g["cat"], "old_part": g["participation"],
                    "n_new": len(filled), "comb_old": g.get("combined"), "comb_new": comb_new,
                    "best_ach": g.get("best_achievable"),
                    "walk_fill": sum(1 for i in range(len(legs)) if sim[i]["fill_step"] not in (None, 0)),
                    "lazy_new": sum(1 for i in range(len(legs)) if sim[i]["lazy"] is True),
                    "borrowed_steps": sum(sim[i].get("borrowed", 0) for i in range(len(legs))),
                    "pnl_old": round(pnl_old,2) if have_res else None,
                    "pnl_new": round(pnl_new,2) if have_res else None})
    return out

results = {}
for fvq, q in [(0.5,0.75),(0.5,0.9),(0.75,0.75),(0.75,0.9),(0.9,0.75),(0.9,0.9)]:
    out = run_sim(fvq, q)
    both_new = sum(1 for r in out if r["n_new"] == 2)
    one_new = sum(1 for r in out if r["n_new"] == 1)
    gap_new = [r["comb_new"] - r["best_ach"] for r in out if r["comb_new"] and r["best_ach"]]
    le97 = sum(1 for r in out if r["comb_new"] and r["comb_new"] <= 97)
    walkf = sum(r["walk_fill"] for r in out)
    lazy_n = sum(r["lazy_new"] for r in out)
    pn = [(r["pnl_new"], r["pnl_old"]) for r in out if r["pnl_new"] is not None and r["pnl_old"] is not None]
    results[f"fv{fvq}_dip{q}"] = {"pairs": both_new, "singles": one_new, "gap_med": med(gap_new),
                       "le97": le97, "walk_fills": walkf, "lazy": lazy_n,
                       "pnl_new": round(sum(p[0] for p in pn),2), "pnl_old": round(sum(p[1] for p in pn),2),
                       "n_pnl": len(pn)}
    json.dump(out, open(f"/tmp/fv_replay_fv{fvq}_q{q}.json","w"))
    print(f"fv={fvq} dip={q}: pairs {both_new} (old 133) | singles {one_new} | gap med {med(gap_new)} (old 12) | "
          f"<=97 {le97} | walk-fills {walkf} | lazy {lazy_n} (old 88) | "
          f"pnl new ${sum(p[0] for p in pn):.2f} vs old ${sum(p[1] for p in pn):.2f}", file=sys.stderr)
json.dump(results, open("/tmp/fv_sweep.json","w"))
print("DONE", file=sys.stderr)
