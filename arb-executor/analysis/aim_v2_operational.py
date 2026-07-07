#!/usr/bin/env python3
"""AIM_V2 OPERATIONAL DERIVATION — PLEX_AIM_V2_RULING parameters, GATED-OFF.
Clock = LATCH-CAL canonical (K=600/M=20000) · per-event residual gate |bell−latch|≤25m
where a latch exists (fail → no_bell) · prior weight w=0.25 (estimator input; the §3
trigger stays honest-only) · dip admissibility ITF+CHALL only with survival floor
P(dip≥3¢)≥0.50, mains dip NULL full stop · complement fold per-cell gate · hierarchical
fallback ⑦ ACTIVE: cell → (cat,bucket) T-curve → (cat,T) curve, parent serves only if
its own honest n≥30, borrowed_from + inflated resid_sd (×1.5 / ×2.0) on every fallback.
Writes data/shape_corpus/aim_v2_operational_LATCHCAL.json. Nothing arms."""
import json, gzip, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT/"data"/"shape_corpus"
BIN=600; GRID=48; FLOOR=30; POOL_K=50; W_PRIOR=0.25; GOAL=97
K,M = 600, 20000
RESID_GATE_MIN = 25
HONEST = datetime(2026,7,6,3,50,tzinfo=timezone.utc).timestamp()
DIP_CATS={"ITF_M","ITF_W","ATP_CHALL","WTA_CHALL"}
CAT={"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
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
def gun(rows):
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

# latches for the residual gate
latch={}
for LOG in ("/tmp/session_since_boot.jsonl", str(ROOT/"logs/live_v3_20260706.jsonl")):
    if not Path(LOG).exists(): continue
    for line in open(LOG,encoding="utf-8",errors="replace"):
        if '"match_live_detected"' not in line: continue
        try: o=json.loads(line)
        except: continue
        ev=o.get("details",{}).get("event")
        if ev and ev not in latch: latch[ev]=o.get("ts_epoch")

# ---- corpus pass ----
excl=defaultdict(int)
S=defaultdict(lambda: {"fd":[],"dd":[],"fdip":[],"ddip":[],"fpx":[],"dpx":[],"cres":[],
                       "n_h":0,"fd_h":[],"dd_h":[],"fdip_h":[],"ddip_h":[]})
files=defaultdict(dict)
for f in sorted((ROOT/"analysis/trades").iterdir()):
    name=f.name.replace(".csv.gz","").replace(".csv","")
    if cat_of(name): files[name.rsplit("-",1)[0]][name]=f
for ev,legs in files.items():
    if len(legs)!=2: excl["not_two_tickers"]+=1; continue
    tks=sorted(legs)
    rows={tk:read_tape(legs[tk]) for tk in tks}
    if any(len(r)<30 for r in rows.values()): excl["dead_tape"]+=1; continue
    bells={tk:gun(r) for tk,r in rows.items()}
    bell=min((b for b in bells.values() if b),default=None)
    if bell is None: excl["no_bell"]+=1; continue
    lt=latch.get("KX"+ev) or latch.get(ev)
    if lt and abs(bell-lt)/60>RESID_GATE_MIN:
        excl["residual_gate_25m"]+=1; continue
    pre={tk:[x for x in r if x[0]<=bell] for tk,r in rows.items()}
    if any(len(p)<8 for p in pre.values()): excl["thin_prebell"]+=1; continue
    c=cat_of(tks[0]); bellpx={tk:p[-1][1] for tk,p in pre.items()}
    hon = bell>=HONEST
    fav=max(tks,key=lambda tk:pre[tk][0][1]); dog=[t for t in tks if t!=fav][0]
    def series(p):
        binpx={}
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
        cell=S[(c,min(4,max(0,fp//20)),tb)]
        cell["fd"].append(bellpx[fav]-fp); cell["dd"].append(bellpx[dog]-dp)
        cell["fdip"].append(flow[tb]-fp); cell["ddip"].append(dlow[tb]-dp)
        cell["fpx"].append(fp); cell["dpx"].append(dp)
        cell["cres"].append((bellpx[fav]-fp)+(bellpx[dog]-dp))
        if hon:
            cell["n_h"]+=1
            cell["fd_h"].append(bellpx[fav]-fp); cell["dd_h"].append(bellpx[dog]-dp)
            cell["fdip_h"].append(flow[tb]-fp); cell["ddip_h"].append(dlow[tb]-dp)
print(f"pass: cells {len(S)} excl {dict(excl)}",file=sys.stderr)

def dip_ok(c, dips):
    if c not in DIP_CATS: return False
    if not dips: return False
    return sum(1 for d in dips if d<=-3)/len(dips)>=0.5

# tiers
tier2=defaultdict(lambda: defaultdict(lambda: {"fd":[],"dd":[],"fdip":[],"ddip":[],"n_h":0}))
tier3=defaultdict(lambda: defaultdict(lambda: {"fd":[],"dd":[],"fdip":[],"ddip":[],"n_h":0}))
for (c,b,t),v in S.items():
    x=tier2[(c,b)][t]; y=tier3[c][t]
    for src,dst in ((v,x),(v,y)):
        dst["fd"]+=src["fd"]; dst["dd"]+=src["dd"]; dst["fdip"]+=src["fdip"]; dst["ddip"]+=src["ddip"]
        dst["n_h"]+=src["n_h"]
t2_valid={k: sum(x["n_h"] for x in ts.values())>=FLOOR for k,ts in tier2.items()}
t3_valid={c: sum(x["n_h"] for x in ts.values())>=FLOOR for c,ts in tier3.items()}
def fit(vals):
    return {"fd":med(vals["fd"]),"dd":med(vals["dd"]),
            "fdip25":quant(vals["fdip"],0.25),"fdip50":quant(vals["fdip"],0.5),
            "ddip25":quant(vals["ddip"],0.25),"ddip50":quant(vals["ddip"],0.5),
            "f_sd":sd(vals["fd"]),"d_sd":sd(vals["dd"]),
            "dip_admissible":None}
table={}
addressable=set()
for c in tier3:
    for b in range(5):
        for t in range(GRID+1): addressable.add((c,b,t))
serving=defaultdict(int)
for key in sorted(addressable):
    c,b,t=key
    v=S.get(key)
    eff=(v["n_h"]+W_PRIOR*(len(v["fd"])-v["n_h"])) if v else 0
    rec=None
    if v and eff>=FLOOR:
        rec=fit(v); rec["source"]="cell"; rec["n"]=len(v["fd"]); rec["n_honest"]=v["n_h"]
        rec["dip_admissible"]=dip_ok(c,v["fdip"]+v["ddip"])
        rec["cres_med"]=med(v["cres"])
        av=[abs(x) for x in v["cres"]]
        rec["cres_fat"]=bool(quant(av,0.75) and quant(av,0.75)>4)
        infl=1.0
    elif t2_valid.get((c,b)) and tier2[(c,b)].get(t) and (tier2[(c,b)][t]["fd"]):
        vv=tier2[(c,b)][t]
        rec=fit(vv); rec["source"]="tier2"; rec["borrowed_from"]=f"{c}|{b}"
        rec["n"]=len(vv["fd"]); rec["n_honest"]=vv["n_h"]
        rec["dip_admissible"]=dip_ok(c,vv["fdip"]+vv["ddip"]); infl=1.5
    elif t3_valid.get(c) and tier3[c].get(t) and tier3[c][t]["fd"]:
        vv=tier3[c][t]
        rec=fit(vv); rec["source"]="tier3"; rec["borrowed_from"]=c
        rec["n"]=len(vv["fd"]); rec["n_honest"]=vv["n_h"]
        rec["dip_admissible"]=dip_ok(c,vv["fdip"]+vv["ddip"]); infl=2.0
    if rec is None:
        table[f"{c}|{b}|{t}"]={"null_reason":"no_valid_tier","n":len(v["fd"]) if v else 0,
                               "n_honest":v["n_h"] if v else 0}
        serving["null"]+=1; continue
    if c not in DIP_CATS or not rec["dip_admissible"]:
        rec["fdip25"]=rec["fdip50"]=rec["ddip25"]=rec["ddip50"]=None   # mains NULL full stop / floor fail
    for kk in ("f_sd","d_sd"):
        if rec.get(kk) is not None: rec[kk]=round(rec[kk]*infl,2)
    rec["null_reason"]=None
    table[f"{c}|{b}|{t}"]=rec
    serving[rec["source"]]+=1
out={"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
     "params":{"clock":"LATCHCAL","K":K,"M":M,"resid_gate_min":RESID_GATE_MIN,
               "w_prior":W_PRIOR,"floor":FLOOR,"dip_cats":sorted(DIP_CATS),
               "survival_floor":"P(dip>=3c)>=0.50","resid_infl":{"tier2":1.5,"tier3":2.0}},
     "excluded":dict(excl),"serving":dict(serving),"table":table}
(CORPUS/"aim_v2_operational_LATCHCAL.json").write_text(json.dumps(out))
print(f"OPERATIONAL: serving {dict(serving)} | excl {dict(excl)}",file=sys.stderr)
