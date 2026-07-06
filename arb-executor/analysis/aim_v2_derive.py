#!/usr/bin/env python3
"""AIM_V2 DERIVATION PIPELINE — pair-state tables from the corpus, BOTH clock variants,
GATED-OFF (analysis artifact; no bot read path; nothing arms).

Prior art (C45): AIM_V2_SPEC (estimator law) · PLEX_REGRESSION_RULING · OPERATOR_RULING_2C
(pair as ONE STATE — both legs' aims live in one cell keyed on the FAV; no sibling
conditionals exist because no sibling lookup exists) · BELL_FEASIBILITY (65% detection;
bell-vs-latch −54.9m 53/53 → the LATCH-CAL variant; complement residual = check only) ·
B3_DISCOUNT_COUNTERFACTUAL · the exit-surface precedent (same corpus, entry logic now).

Outputs: data/shape_corpus/aim_v2_candidate_{BAR|LATCHCAL}.json + derivation stats.
Estimator per spec: per-cell drift med + resid_sd; dips at q=0.25/0.50; monotone
smoothing across T via pool-adjacent-violators (paths converge to the bell); hierarchical
pooling toward the cat curve, pooled_w = n/(n+50); HARD floor eff_n>=30 at prior-weight
1.0 (coverage also reported at 0.5/0.25 for the Plex slot); null_reason on parked cells;
NO interpolation anywhere; complement residual reported per cell as a consistency gate.
UNTRADEABLE-AT-Q marked where median joint combined-at-dip > 97 (table fact, not a skip)."""
import json, gzip, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "shape_corpus"
BIN = 600; GRID = 48; FLOOR = 30; POOL_K = 50
GOAL = 97
HONEST_ERA = datetime(2026, 7, 6, 3, 50, tzinfo=timezone.utc).timestamp()
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), None)
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
    op=gzip.open if f.suffix==".gz" else open
    rows=[]
    try:
        with op(f,"rt",encoding="utf-8",errors="replace") as fh:
            next(fh,None)
            for ln in fh:
                p=ln.rstrip("\n").split(",")
                if len(p)<5: continue
                t=pts(p[0])
                if t is None: continue
                try: rows.append((t,int(p[2]),int(float(p[3]))))
                except: continue
    except Exception: return []
    rows.sort(); return rows
def gun(rows, K, M):
    if not rows: return None
    mv=defaultdict(float)
    for t,pr,ct in rows: mv[int(t//60)*60]+=ct
    mins=sorted(mv)
    fwd={m:sum(mv[x] for x in mins if m<=x<m+600) for m in mins}
    return next((m for m in mins if mv[m]>=K and fwd[m]>=M), None)
def med(v):
    v=sorted(v); return v[len(v)//2] if v else None
def quant(v,q):
    v=sorted(v); return v[min(len(v)-1,int(len(v)*q))] if v else None
def sd(v):
    if len(v)<2: return None
    m=sum(v)/len(v)
    return round((sum((x-m)**2 for x in v)/(len(v)-1))**0.5,2)

# ---------- 0. LATCH-CAL: grid-fit the bar to the live latch on the overlap ----------
latch={}
for LOG in ("/tmp/session_since_boot.jsonl", str(ROOT/"logs/live_v3_20260706.jsonl")):
    if not Path(LOG).exists(): continue
    for line in open(LOG,encoding="utf-8",errors="replace"):
        if '"match_live_detected"' not in line: continue
        try: o=json.loads(line)
        except: continue
        ev=o.get("details",{}).get("event")
        if ev and ev not in latch: latch[ev]=o.get("ts_epoch")
# events -> a leg tape for grid fit
ev_tape={}
for f in sorted((ROOT/"analysis/trades").iterdir()):
    name=f.name.replace(".csv.gz","").replace(".csv","")
    ev=name.rsplit("-",1)[0]
    if ev in latch and ev not in ev_tape:
        ev_tape[ev]=f
GRID_K=(150,300,600,1000,1500); GRID_M=(3000,6000,10000,20000)
best=None
tape_cache={ev: read_tape(f) for ev,f in ev_tape.items()}
for K in GRID_K:
    for M in GRID_M:
        errs=[]
        for ev,rows in tape_cache.items():
            b=gun(rows,K,M)
            if b is not None: errs.append(abs(b-latch[ev])/60)
        if len(errs)>=20:
            m=med(errs)
            if best is None or m<best[2]: best=(K,M,m,len(errs))
K_CAL,M_CAL,ERR_CAL,N_CAL = best if best else (1500,20000,None,0)
print(f"LATCH-CAL grid: K={K_CAL} M={M_CAL} med|err|={ERR_CAL}m on n={N_CAL} (BAR baseline: 150/3000, med -54.9m)",file=sys.stderr)

# ---------- 1. PAIR-STATE EXTRACTION, both variants ----------
def build_variant(K, M, tag):
    excl=defaultdict(int)
    cells=defaultdict(lambda: {"fd":[],"dd":[],"fdip":[],"ddip":[],"fpx":[],"dpx":[],"cres":[],"n_h":0})
    files=defaultdict(dict)
    for f in sorted((ROOT/"analysis/trades").iterdir()):
        name=f.name.replace(".csv.gz","").replace(".csv","")
        c=cat_of(name)
        if not c: continue
        files[name.rsplit("-",1)[0]][name]=f
    for ev,legs in files.items():
        if len(legs)!=2: excl["not_two_tickers"]+=1; continue
        tks=sorted(legs)
        rows={tk: read_tape(legs[tk]) for tk in tks}
        if any(len(r)<30 for r in rows.values()): excl["dead_tape"]+=1; continue
        bells={tk: gun(r,K,M) for tk,r in rows.items()}
        bell=min((b for b in bells.values() if b), default=None)
        if bell is None: excl["no_bell"]+=1; continue
        pre={tk:[x for x in r if x[0]<=bell] for tk,r in rows.items()}
        if any(len(p)<8 for p in pre.values()): excl["thin_prebell"]+=1; continue
        c=cat_of(tks[0])
        bellpx={tk: p[-1][1] for tk,p in pre.items()}
        era_h = bell >= HONEST_ERA
        # fav = side with higher price at the earliest common observation
        fav = max(tks, key=lambda tk: pre[tk][0][1])
        dog = [t for t in tks if t!=fav][0]
        # per-bin last px + remaining low, per side
        def series(p):
            binpx={};
            for t,pr in [(x[0],x[1]) for x in p]:
                tb=int((bell-t)//BIN)
                if 0<=tb<=GRID: binpx[tb]=pr
            lows={}; cur=10**9
            for t,pr in reversed([(x[0],x[1]) for x in p]):
                cur=min(cur,pr); lows[t]=cur
            binlow={}
            for t,pr in [(x[0],x[1]) for x in p]:
                tb=int((bell-t)//BIN)
                if 0<=tb<=GRID: binlow[tb]=lows[t]
            return binpx,binlow
        fpx,flow=series(pre[fav]); dpx,dlow=series(pre[dog])
        for tb in set(fpx)&set(dpx):
            fp,dp=fpx[tb],dpx[tb]
            key=(c,min(4,max(0,fp//20)),tb)
            cell=cells[key]
            cell["fd"].append(bellpx[fav]-fp); cell["dd"].append(bellpx[dog]-dp)
            cell["fdip"].append(flow[tb]-fp); cell["ddip"].append(dlow[tb]-dp)
            cell["fpx"].append(fp); cell["dpx"].append(dp)
            cell["cres"].append((bellpx[fav]-fp)+(bellpx[dog]-dp))
            if era_h: cell["n_h"]+=1
    # ---------- 3. FIT: cell stats + PAV monotone + pooling ----------
    raw={}
    for k,v in cells.items():
        raw[k]={"n":len(v["fd"]),"n_honest":v["n_h"],
                "fdrift":med(v["fd"]),"ddrift":med(v["dd"]),
                "f_sd":sd(v["fd"]),"d_sd":sd(v["dd"]),
                "fdip25":quant(v["fdip"],0.25),"fdip50":quant(v["fdip"],0.5),
                "ddip25":quant(v["ddip"],0.25),"ddip50":quant(v["ddip"],0.5),
                "fpx":med(v["fpx"]),"dpx":med(v["dpx"]),
                "cres_med":med(v["cres"]),"cres_fat":bool(quant([abs(x) for x in v["cres"]],0.75) and quant([abs(x) for x in v["cres"]],0.75)>4)}
    # cat-level pooled curves per Tbin (fav & dog)
    catcurve=defaultdict(lambda: defaultdict(lambda: {"fd":[],"dd":[],"f25":[],"d25":[],"f50":[],"d50":[]}))
    for (c,b,t),v in cells.items():
        cc=catcurve[c][t]
        cc["fd"]+=v["fd"]; cc["dd"]+=v["dd"]
        cc["f25"]+=v["fdip"]; cc["d25"]+=v["ddip"]
    catfit={c:{t:{"fd":med(x["fd"]),"dd":med(x["dd"]),
                  "f25":quant(x["f25"],0.25),"d25":quant(x["d25"],0.25),
                  "f50":quant(x["f25"],0.5),"d50":quant(x["d25"],0.5)}
             for t,x in ts.items() if len(x["fd"])>=FLOOR} for c,ts in catcurve.items()}
    def pav_monotone(seq):
        """|value| non-increasing toward the bell (T->0): pool adjacent violators on the
        T-descending sequence of magnitudes, sign preserved from input."""
        idx=[t for t,_ in seq]; vals=[v for _,v in seq]
        mags=[abs(v) for v in vals]; signs=[1 if v>=0 else -1 for v in vals]
        # enforce mags non-decreasing in T (i.e., non-increasing toward bell): PAV ascending on T
        order=sorted(range(len(idx)),key=lambda i: idx[i])
        m=[mags[i] for i in order]
        blocks=[[m[0],1]]
        for x in m[1:]:
            blocks.append([x,1])
            while len(blocks)>1 and blocks[-1][0]<blocks[-2][0]:
                s=blocks[-1][0]*blocks[-1][1]+blocks[-2][0]*blocks[-2][1]
                n=blocks[-1][1]+blocks[-2][1]
                blocks=blocks[:-2]+[[s/n,n]]
        fit=[]
        for val,n in blocks: fit+= [val]*n
        out={}
        for pos,i in enumerate(order): out[idx[i]]=round(signs[i]*fit[pos],2)
        return out
    table={}
    for (c,b,t),v in raw.items():
        eff={w: v["n_honest"]+w*(v["n"]-v["n_honest"]) for w in (1.0,0.5,0.25)}
        if eff[1.0]<FLOOR:
            table[f"{c}|{b}|{t}"]={"n":v["n"],"n_honest":v["n_honest"],"null_reason":"below_floor"}
            continue
        w=v["n"]/(v["n"]+POOL_K)
        cf=catfit.get(c,{}).get(t)
        def pool(cell_v, cat_v):
            if cell_v is None: return None
            if cat_v is None: return cell_v
            return round(w*cell_v+(1-w)*cat_v,2)
        table[f"{c}|{b}|{t}"]={"n":v["n"],"n_honest":v["n_honest"],"pooled_w":round(w,3),
            "null_reason":None,
            "fav":{"drift":pool(v["fdrift"],cf and cf["fd"]),"resid_sd":v["f_sd"],
                   "dip25":pool(v["fdip25"],cf and cf["f25"]),"dip50":pool(v["fdip50"],cf and cf["f50"]),"px":v["fpx"]},
            "dog":{"drift":pool(v["ddrift"],cf and cf["dd"]),"resid_sd":v["d_sd"],
                   "dip25":pool(v["ddip25"],cf and cf["d25"]),"dip50":pool(v["ddip50"],cf and cf["d50"]),"px":v["dpx"]},
            "complement_residual_med":v["cres_med"],"complement_fat":v["cres_fat"]}
    # PAV monotone pass per (cat,bucket,side,field)
    bykey=defaultdict(list)
    for k,v in table.items():
        if v.get("null_reason"): continue
        c,b,t=k.split("|")
        bykey[(c,b)].append((int(t),v))
    for (c,b),seq in bykey.items():
        for side in ("fav","dog"):
            for fld in ("drift","dip25","dip50"):
                pts_=[(t,v[side][fld]) for t,v in seq if v[side][fld] is not None]
                if len(pts_)<3: continue
                fit=pav_monotone(pts_)
                for t,v in seq:
                    if t in fit: v[side][fld]=fit[t]
    # ---------- 4. JOINT AIM ----------
    for k,v in table.items():
        if v.get("null_reason"): continue
        for q in ("25","50"):
            fa=v["fav"]["px"]+ (v["fav"][f"dip{q}"] or 0)
            da=v["dog"]["px"]+ (v["dog"][f"dip{q}"] or 0)
            v[f"joint_q{q}"]={"fav_aim":round(fa,1),"dog_aim":round(da,1),
                              "combined_at_dip":round(fa+da,1),
                              "untradeable":bool(fa+da>GOAL)}
    live=sum(1 for v in table.values() if not v.get("null_reason"))
    park=len(table)-live
    unt={q: sum(1 for v in table.values() if v.get(f"joint_q{q}",{}).get("untradeable")) for q in ("25","50")}
    covw={w: sum(1 for v in table.values() if (v["n_honest"]+w*(v["n"]-v["n_honest"]))>=FLOOR) for w in (1.0,0.5,0.25)}
    out={"variant":tag,"bar":{"K":K,"M":M},"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
         "excluded":dict(excl),"cells_live":live,"cells_parked":park,
         "untradeable_at_q":unt,"coverage_at_prior_w":covw,"table":table}
    (CORPUS/f"aim_v2_candidate_{tag}.json").write_text(json.dumps(out))
    print(f"{tag}: live {live} / parked {park} | untradeable q25={unt['25']} q50={unt['50']} | cov w1.0={covw[1.0]} w0.5={covw[0.5]} w0.25={covw[0.25]} | excl {dict(excl)}",file=sys.stderr)
    return out

v1=build_variant(150,3000,"BAR")
v2=build_variant(K_CAL,M_CAL,"LATCHCAL")
json.dump({"latchcal_fit":{"K":K_CAL,"M":M_CAL,"med_err_min":ERR_CAL,"n":N_CAL}},
          open(CORPUS/"aim_v2_derivation_meta.json","w"))
print("DONE",file=sys.stderr)
