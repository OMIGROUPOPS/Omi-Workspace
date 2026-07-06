#!/usr/bin/env python3
"""[READ-ONLY] BELL-REANCHOR FEASIBILITY — the five gating numbers for the Plex amendment.
1. per-match bell detection rate inside the corpus (denominators by skip reason)
2. bell vs certified gun (the live latch) error distribution on the overlap set
3. coverage recount under re-anchored prior rows (bell-anchored card-era counting toward
   the floor, reweighted, vs honest-only)
4. complement-fold residuals (drift_A + drift_B at same T ~ 0 test)
5. divot survival at full-corpus granularity: P(dip <= -X) per (cat,bucket), T4-band
Writes /tmp/bell_feas.json."""
import json, sys, gzip
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
CORPUS = Path("data/shape_corpus")
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
def tape_gun(rows):
    if not rows: return None
    mv=defaultdict(float)
    for t,pr,ct in rows: mv[int(t//60)*60]+=ct
    mins=sorted(mv)
    fwd={m:sum(mv[x] for x in mins if m<=x<m+600) for m in mins}
    return next((m for m in mins if mv[m]>=150 and fwd[m]>=3000), None)

# ---- 1. detection rate with denominators ----
det=defaultdict(int); det_cat=defaultdict(lambda: defaultdict(int))
bells={}  # per-ticker bell for overlap use
for f in sorted(Path("analysis/trades").iterdir()):
    name=f.name.replace(".csv.gz","").replace(".csv","")
    c=cat_of(name)
    if not c: det["non_tennis"]+=1; continue
    rows=read_tape(f)
    if len(rows)<30: det["lt30_rows"]+=1; det_cat[c]["lt30_rows"]+=1; continue
    b=tape_gun(rows)
    if b is None: det["no_unambiguous_bell"]+=1; det_cat[c]["no_bell"]+=1; continue
    pre=[x for x in rows if x[0]<=b]
    if len(pre)<8: det["lt8_prebell_prints"]+=1; det_cat[c]["lt8_pre"]+=1; continue
    det["DETECTED"]+=1; det_cat[c]["DETECTED"]+=1
    bells[name]=b
tot=sum(det.values())-det["non_tennis"]
print(f"1. DETECTION: {det['DETECTED']}/{tot} tennis tickers ({100*det['DETECTED']//max(1,tot)}%) | skips: {dict(det)}",file=sys.stderr)

# ---- 2. bell vs certified latch on overlap (post-flip sessions) ----
latch={}
for LOG in ("/tmp/session_since_boot.jsonl","logs/live_v3_20260706.jsonl"):
    if not Path(LOG).exists(): continue
    for line in open(LOG,encoding="utf-8",errors="replace"):
        if '"match_live_detected"' not in line: continue
        try: o=json.loads(line)
        except: continue
        ev=o.get("details",{}).get("event")
        if ev and ev not in latch: latch[ev]=o.get("ts_epoch")
overlap=[]
for ev,lt in latch.items():
    evb=[b for tk,b in bells.items() if tk.rsplit("-",1)[0]==ev]
    if evb:
        b=min(evb)
        overlap.append({"ev":ev.replace("KX","")[-20:],"bell_min_latch_min":round((b-lt)/60,1)})
errs=sorted(x["bell_min_latch_min"] for x in overlap)
def med(v): return v[len(v)//2] if v else None
def q(v,p): return v[min(len(v)-1,int(len(v)*p))] if v else None
print(f"2. OVERLAP n={len(overlap)}: bell-latch med {med(errs)}m [p25 {q(errs,0.25)} p75 {q(errs,0.75)}] | within ±5m: {sum(1 for e in errs if abs(e)<=5)} | bell earlier: {sum(1 for e in errs if e<0)}",file=sys.stderr)

# ---- 3+4+5 from samples ----
samples=[]
for sf in sorted(CORPUS.glob("samples_*.jsonl")):
    for line in open(sf,encoding="utf-8"):
        try: samples.append(json.loads(line))
        except: continue
cells_h=defaultdict(int); cells_t=defaultdict(int)
for s in samples:
    k=(s["cat"],s["b"],s["t"])
    cells_t[k]+=1
    if s.get("era")=="honest": cells_h[k]+=1
TGT=[(c,b,t) for c in ("ITF_M","ITF_W","ATP_CHALL","WTA_CHALL") for b in range(5) for t in range(12,37)]
cov_h=sum(1 for k in TGT if cells_h.get(k,0)>=30)
cov_t=sum(1 for k in TGT if cells_t.get(k,0)>=30)
cov_rw=sum(1 for k in TGT if cells_h.get(k,0)+0.25*(cells_t.get(k,0)-cells_h.get(k,0))>=30)
print(f"3. COVERAGE RECOUNT: honest-only {cov_h}/{len(TGT)} | re-anchored ALL rows {cov_t}/{len(TGT)} ({100*cov_t//len(TGT)}%) | reweighted (card 0.25) {cov_rw}/{len(TGT)} ({100*cov_rw//len(TGT)}%)",file=sys.stderr)

# 4. complement-fold residuals: per (event-ticker-pair, Tbin) drift_A + drift_B
by_ev_t=defaultdict(dict)
for s in samples:
    ev=s["tk"].rsplit("-",1)[0]
    by_ev_t[(ev,s["t"])][s["tk"]]=s["drift"]
res=[]
for (ev,t),legs in by_ev_t.items():
    if len(legs)==2:
        a,b=list(legs.values())
        res.append(a+b)
res.sort()
print(f"4. COMPLEMENT-FOLD residuals (drift_A+drift_B): n={len(res)} med {med(res)} [p25 {q(res,0.25)} p75 {q(res,0.75)}] | |res|<=2c: {sum(1 for r in res if abs(r)<=2)} ({100*sum(1 for r in res if abs(r)<=2)//max(1,len(res))}%)",file=sys.stderr)

# 5. divot survival at corpus granularity, T4 band (Tbin 12-24), per cat/bucket
surv=defaultdict(lambda: defaultdict(int)); denom=defaultdict(int)
for s in samples:
    if not (12<=s["t"]<=24): continue
    k=(s["cat"],s["b"])
    denom[k]+=1
    for X in range(1,11):
        if s["dip"]<=-X: surv[k][X]+=1
surv_out={}
for k,n in denom.items():
    if n<30: continue
    surv_out[f"{k[0]}|{k[1]}"]={"n":n,**{f"P_dip_ge_{X}c":round(surv[k][X]/n,3) for X in (1,2,3,4,6,8)}}
print(f"5. DIVOT SURVIVAL (T4 band, n>=30 cells): {len(surv_out)} cells",file=sys.stderr)
for kk in sorted(surv_out)[:12]:
    print(f"   {kk}: {surv_out[kk]}",file=sys.stderr)

json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
           "detection":{"by_reason":dict(det),"per_cat":{k:dict(v) for k,v in det_cat.items()},
                        "rate":round(det["DETECTED"]/max(1,tot),3)},
           "overlap":overlap,
           "coverage_recount":{"honest_only":cov_h,"all_rows":cov_t,"reweighted":cov_rw,"target":len(TGT)},
           "complement_residuals":{"n":len(res),"med":med(res),"p25":q(res,0.25),"p75":q(res,0.75),
                                   "within_2c":sum(1 for r in res if abs(r)<=2)},
           "divot_survival_T4":surv_out},
          open("/tmp/bell_feas.json","w"),default=str)
print("DONE",file=sys.stderr)
