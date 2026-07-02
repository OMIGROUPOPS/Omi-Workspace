import os, csv, glob, gzip, json, re, statistics as st
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
BASE="/root/Omi-Workspace/arb-executor"; TICK=BASE+"/analysis/premarket_ticks"; TR=BASE+"/analysis/trades"; LOGDIR=BASE+"/logs"
UTC=timezone.utc; EDT=timezone(timedelta(hours=-4))
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(d,tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(d+"/"+tk+e): return d+"/"+tk+e
    return None
def cat(t):
    for p,c in (("KXATPCHALLENGERMATCH","ATP_CHALL"),("KXWTACHALLENGERMATCH","WTA_CHALL"),("KXATPMATCH","ATP_MAIN"),("KXWTAMATCH","WTA_MAIN"),("KXITFWMATCH","ITF_W"),("KXITFMATCH","ITF_M")):
        if t.startswith(p): return c
    return "?"
def piso(s):
    for f in ("%Y-%m-%dT%H:%M:%SZ","%Y-%m-%dT%H:%MZ"):
        try: return datetime.strptime(s,f).replace(tzinfo=UTC).timestamp()
        except: pass
    return None
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None

sched={}
for f in sorted(glob.glob(LOGDIR+"/live_v3_2026062*.jsonl")+glob.glob(LOGDIR+"/live_v3_20260630.jsonl")):
    for line in open(f,errors="replace"):
        if "schedule_match" not in line: continue
        try: e=json.loads(line)
        except: continue
        D=e.get("details",{}) or {}
        if D.get("event") and D.get("start_time"):
            se=piso(D["start_time"])
            if se: sched[D["event"]]=se

files=set(os.listdir(TICK)); ev2=defaultdict(set); SL=re.compile(r"-26JUN(\d\d)")
for f in files:
    b=f.replace(".csv.gz","").replace(".csv","")
    m=SL.search(b)
    if m and 24<=int(m.group(1))<=30 and "-" in b: ev2[b.rsplit("-",1)[0]].add(b)
paired=[e for e,l in ev2.items() if len(l)==2 and e in sched]
bycat=defaultdict(list)
for e in sorted(paired): bycat[cat(e+"-X")].append(e)
SAMPLE=[]
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","ITF_M","ITF_W"]: SAMPLE+=bycat[c][:40]

def best_divot(tk,t0):
    # lowest taker_side=no print price in premarket window [t0-4h, t0) = best sequential maker-catchable dip
    f=findf(TR,tk)
    if not f: return None
    lo=None
    for r in csv.reader(opent(f)):
        if not r or r[0]=="ts_et": continue
        e=ptape(r[0])
        if e is None or e>=t0 or e<t0-4*3600: continue
        if (r[4] if len(r)>4 else "")=="no":
            try: p=int(float(r[2]))
            except: continue
            lo = p if lo is None else min(lo,p)
    return lo

buck=Counter(); n=0; bycatbuck=defaultdict(Counter)
for e in SAMPLE:
    legs=sorted(ev2[e]); t0=sched[e]
    a=best_divot(legs[0],t0); b=best_divot(legs[1],t0)
    if a is None or b is None: continue
    comb=a+b; n+=1
    k="<=97" if comb<=97 else ("98-100" if comb<=100 else ">100")
    buck[k]+=1; bycatbuck[cat(e+"-X")][k]+=1

print("=== JOB-2 DRY-RUN — KNOWN-CONTAMINATED (pre-re-anchor timing; premarket window on STALE scheduled start) ===")
print("PIPELINE SHAKEOUT ONLY, NOT DECISION DATA. (ii) window-reachability DEFERRED to post-P1 re-anchor.\n")
print(f"(i) combined-<=97 achievability ceiling under SEQUENTIAL best-divot fills (min taker_no print per leg, premarket):")
print(f"    n pairs scored: {n}")
for k in ("<=97","98-100",">100"):
    print(f"      {k:8s}: {buck[k]:4d} ({100*buck[k]/n:.0f}%)" if n else k)
print(f"    NOTE: this is the CEILING (perfect divot-catch, both legs). Real fills < ceiling. Contaminated window.")
print("    by cat:")
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","ITF_M","ITF_W"]:
    bc=bycatbuck[c]; tot=sum(bc.values())
    if tot: print(f"      {c:9s} n={tot:3d}  <=97 {100*bc['<=97']/tot:3.0f}%  98-100 {100*bc['98-100']/tot:3.0f}%  >100 {100*bc['>100']/tot:3.0f}%")
print(f"\n(iii) throughput floor (>=25 fills/day) — from OMQS_DEPLOYBOX_COMPARE (our actual fills, not ceiling):")
print(f"      CURRENT deploy (flags OFF): ~44 fills/day (69 outage-adj) -> ABOVE floor")
print(f"      PRIOR deploy (flags ON):    ~354 fills/day -> far above floor")
