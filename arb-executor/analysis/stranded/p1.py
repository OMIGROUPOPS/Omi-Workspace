import os, csv, glob, gzip, json, re, statistics as st
from datetime import datetime, timezone, timedelta
from collections import defaultdict
BASE="/root/Omi-Workspace/arb-executor"; TICK=BASE+"/analysis/premarket_ticks"; LOGDIR=BASE+"/logs"
UTC=timezone.utc; EDT=timezone(timedelta(hours=-4))
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(TICK+"/"+tk+e): return TICK+"/"+tk+e
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

# scheduled starts from logs (latest per event)
sched={}
for f in sorted(glob.glob(LOGDIR+"/live_v3_2026062*.jsonl")+glob.glob(LOGDIR+"/live_v3_20260630.jsonl")):
    for line in open(f,errors="replace"):
        if "schedule_match" not in line: continue
        try: e=json.loads(line)
        except: continue
        D=e.get("details",{}) or {}; ev=D.get("event"); stt=D.get("start_time")
        if ev and stt:
            se=piso(stt)
            if se: sched[ev]=se

# pick 15 stratified events (paired, tape-covered, with a scheduled start)
files=set(os.listdir(TICK)); ev2legs=defaultdict(set); SL=re.compile(r"-26JUN(\d\d)")
for f in files:
    b=f.replace(".csv.gz","").replace(".csv","")
    m=SL.search(b)
    if m and 24<=int(m.group(1))<=30 and "-" in b: ev2legs[b.rsplit("-",1)[0]].add(b)
paired=[e for e,l in ev2legs.items() if len(l)==2 and e in sched]
bycat=defaultdict(list)
for e in sorted(paired): bycat[cat(e+"-X")].append(e)
sample=[]
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","ITF_M","ITF_W"]:
    sample+=bycat[c][:3]
print(f"scheduled-start events: {len(sched)} | paired+sched+tape: {len(paired)} | sample: {len(sample)}")

def load(tk):
    rows=[]
    for r in csv.DictReader(opent(findf(tk))):
        e=ptape(r["ts_et"])
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        rows.append((e,gi("bid_1"),gi("ask_1"),gi("last_trade")))
    rows.sort(); return rows

def onset(rows, mode):
    # bucket by minute
    if not rows: return None
    mins=defaultdict(list)
    for (e,b,a,lt) in rows: mins[int(e//60)].append((e,b,a,lt))
    ks=sorted(mins)
    def active(k):
        rs=mins[k]
        two=sum(1 for (e,b,a,lt) in rs if b>0 and a>0)/len(rs)>=0.6
        # quote updates: changes in b/a
        qu=sum(1 for (p,c) in zip(rs,rs[1:]) if p[1]!=c[1] or p[2]!=c[2])
        spr=[a-b for (e,b,a,lt) in rs if b>0 and a>0]
        msp=st.median(spr) if spr else 99
        trs=sum(1 for (p,c) in zip(rs,rs[1:]) if p[3]!=c[3] and c[3]>0)
        if mode=="Q": return two and qu>=3 and msp<=10
        else: return two and trs>=3
    # first run of >=5 consecutive active minutes
    run=0
    for i,k in enumerate(ks):
        if active(k):
            run+=1
            if run>=5: return mins[ks[i-4]][0][0]  # start of the run
        else: run=0
    return None

print(f"\n{'event':40s} {'cat':9s} {'ONSET-Q off(min)':>16s} {'ONSET-T off(min)':>16s}")
offQ=[]; offT=[]
for e in sample:
    legs=sorted(ev2legs[e]); rows=load(legs[0])  # onset from leg-1 (representative)
    s=sched[e]
    oq=onset(rows,"Q"); ot=onset(rows,"T")
    dq=(oq-s)/60.0 if oq else None; dt=(ot-s)/60.0 if ot else None
    if dq is not None: offQ.append(dq)
    if dt is not None: offT.append(dt)
    print(f"{e[-40:]:40s} {cat(e+'-X'):9s} {('%+.0f'%dq) if dq is not None else 'n/a':>16s} {('%+.0f'%dt) if dt is not None else 'n/a':>16s}")

def dist(name,x):
    if not x: print(f"  {name}: no data"); return
    xs=sorted(x); n=len(xs)
    def pc(q): return xs[min(n-1,int(q*n))]
    tails=sum(1 for v in xs if abs(v)>15)
    print(f"  {name} (n={n}): median {st.median(xs):+.0f}min  IQR[{pc(.25):+.0f},{pc(.75):+.0f}]  min{xs[0]:+.0f}/max{xs[-1]:+.0f}  |>15min tails|={tails} ({100*tails/n:.0f}%)")
print("\n=== OFFSET DISTRIBUTION (tape-onset - scheduled_start, minutes; + = onset AFTER sched) ===")
dist("ONSET-Q (two-sided+quote+spread)",offQ)
dist("ONSET-T (trade-burst / match-live proxy)",offT)
