import os, csv, glob, gzip, json, re, math, statistics as st
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
def pearson(x,y):
    n=len(x)
    if n<10: return None
    mx=sum(x)/n; my=sum(y)/n
    sxy=sum((a-mx)*(b-my) for a,b in zip(x,y))
    sxx=sum((a-mx)**2 for a in x); syy=sum((b-my)**2 for b in y)
    if sxx<=0 or syy<=0: return None
    return sxy/math.sqrt(sxx*syy)

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
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","ITF_M","ITF_W"]:
    SAMPLE+=bycat[c][:20]   # 20/cat
print(f"P2 sample: {len(SAMPLE)} paired events (<=20/cat)")

def grid(tk, t0):
    # 30s grid over [t0-4h, t0], forward-fill book
    f=findf(tk)
    if not f: return None
    rows=[]
    for r in csv.DictReader(opent(f)):
        e=ptape(r["ts_et"])
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        rows.append((e,gi("bid_1"),gi("ask_1"),gi("bid_1_sz"),gi("ask_1_sz"),gi("last_trade")))
    rows.sort()
    if not rows: return None
    g={}; i=0; cur=None
    start=t0-4*3600
    tt=start
    while tt<=t0:
        while i<len(rows) and rows[i][0]<=tt: cur=rows[i]; i+=1
        if cur and cur[1]>0 and cur[2]>0:
            g[int(tt)]=(cur[1],cur[2],cur[3],cur[4],cur[5])  # bid,ask,bsz,asz,last
        tt+=30
    return g

def rmed(seq,idx,win=60):  # running median over prior `win` points
    lo=max(0,idx-win); vals=[v for v in seq[lo:idx] if v is not None]
    return st.median(vals) if vals else None

tierrows=defaultdict(lambda: dict(rb=[],ra=[],ob=[],oa=[],spr=[],n=0,ev=0))
dv=defaultdict(lambda: dict(total=0,strong=0,lag=[]))
for e in SAMPLE:
    legs=sorted(ev2[e]); t0=sched[e]
    gA=grid(legs[0],t0); gB=grid(legs[1],t0)
    if not gA or not gB: continue
    ts=sorted(set(gA)&set(gB))
    if len(ts)<30: continue
    midsum=[]; bidsum=[]; asksum=[]; sprsum=[]; szmed=[]
    midA=[]; bidB=[]
    for t in ts:
        bA,aA,bszA,aszA,lA=gA[t]; bB,aB,bszB,aszB,lB=gB[t]
        mA=(bA+aA)/2; mB=(bB+aB)/2
        midsum.append(mA+mB); bidsum.append(bA+bB); asksum.append(aA+aB)
        sprsum.append((aA-bA)+(aB-bB)); szmed.append(bszA+aszA+bszB+aszB)
        midA.append(mA); bidB.append(bB)
    tier = "thin(ITF)" if cat(e+"-X").startswith("ITF") else "main(ATP/WTA)"
    T=tierrows[tier]; T["ev"]+=1; T["n"]+=len(ts)
    rb=pearson(bidsum,midsum); ra=pearson(asksum,midsum)
    if rb is not None: T["rb"].append(rb)
    if ra is not None: T["ra"].append(ra)
    T["ob"].append(st.mean([b-m for b,m in zip(bidsum,midsum)]))
    T["oa"].append(st.mean([a-m for a,m in zip(asksum,midsum)]))
    T["spr"]+=sprsum
    # divot check: leg-1(midA) local minima; is leg-2 bid (bidB) >= its running median?
    for i in range(3,len(midA)-3):
        if midA[i]<min(midA[i-3:i]) and midA[i]<min(midA[i+1:i+4]):  # local min
            dv[tier]["total"]+=1
            rm=rmed(bidB,i,win=60)
            if rm is not None:
                if bidB[i]>=rm: dv[tier]["strong"]+=1
                else: dv[tier]["lag"].append(rm-bidB[i])

print("\n=== SEESAW AT THE TOUCH — by liquidity tier ===")
for tier in ("main(ATP/WTA)","thin(ITF)"):
    T=tierrows[tier]
    if not T["ev"]: continue
    def m(x): return st.median(x) if x else float('nan')
    sprtail=100*sum(1 for s in T["spr"] if s>6)/len(T["spr"]) if T["spr"] else 0
    print(f"  {tier:7s} (events={T['ev']}, gridpts={T['n']}):")
    print(f"    r(bid-sum,mid-sum) median={m(T['rb']):.3f} | r(ask-sum,mid-sum) median={m(T['ra']):.3f}   [gate r>0.9]")
    print(f"    offset bid-sum-vs-mid median={m(T['ob']):+.2f}c | ask-sum-vs-mid median={m(T['oa']):+.2f}c   [gate |offset|<2c]")
    print(f"    combined-spread>6c tail: {sprtail:.0f}% of gridpts")
print("\n=== DIVOT-TIMING CHECK (leg-1 mid local-min moments) by tier ===")
for tier in ("main(ATP/WTA)","thin(ITF)"):
    D=dv[tier]
    if not D["total"]: continue
    lag=D["lag"]
    print(f"  {tier:14s} divots={D['total']:3d} | leg-2 BID strong(>=run-med) {D['strong']} ({100*D['strong']/D['total']:.0f}%) | lagging {len(lag)} ({100*len(lag)/D['total']:.0f}%)"+(f", median gap {st.median(lag):.1f}c" if lag else ""))
