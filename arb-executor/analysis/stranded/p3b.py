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
def tier(c): return "thin(ITF)" if c.startswith("ITF") else "main(ATP/WTA)"
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

def load(tk):
    rows=[]
    for r in csv.DictReader(opent(findf(tk))):
        e=ptape(r["ts_et"])
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        rows.append((e,gi("bid_1"),gi("ask_1")))
    rows.sort(); return rows
def at(rows,t):
    lo=None
    for row in rows:
        if row[0]<=t: lo=row
        else: break
    return lo

# ---- (0) COVERAGE ----
print("=== P3b (0) COVERAGE CHECK — L1 recorder reach before scheduled start ===")
cov=defaultdict(list)
tapes={}
for e in SAMPLE:
    legs=sorted(ev2[e]); r=load(legs[0]); tapes[e]=(r,load(legs[1]))
    if r: cov[tier(cat(e+"-X"))].append((sched[e]-r[0][0])/3600.0)  # hours of pre-sched reach
for tr in ("main(ATP/WTA)","thin(ITF)"):
    x=sorted(cov[tr],reverse=True)
    if not x: continue
    pre4=sum(1 for v in x if v>=4)
    print(f"  {tr:14s} n={len(x)} median reach {st.median(x):.1f}h before sched | max {x[0]:.1f}h | reach>=4h(pre-T-4h): {pre4} ({100*pre4/len(x):.0f}%)")

# ---- shape study by bucket (only where covered) ----
BUCKETS=[("T-8h",8),("T-6h",6),("T-4h",4),("T-2h",2),("T-1h",1),("T-30m",0.5),("T-0",0.0)]
agg=defaultdict(lambda: defaultdict(lambda: dict(n=0,le97=0,postable=0,joint=0,bidsum=[])))
for e in SAMPLE:
    rA,rB=tapes[e]
    if not rA or not rB: continue
    s=sched[e]; tr=tier(cat(e+"-X"))
    for (lbl,h) in BUCKETS:
        t=s-h*3600
        if rA[0][0]>t or rB[0][0]>t: continue   # no coverage this early
        a=at(rA,t); b=at(rB,t)
        if not a or not b: continue
        bA,aA=a[1],a[2]; bB,aB=b[1],b[2]
        A=agg[tr][lbl]; A["n"]+=1
        # postable: both two-sided + spread sane
        two=(bA>0 and aA>0 and bB>0 and aB>0)
        spr=((aA-bA)+(aB-bB)) if two else 999
        postable = two and spr<=12
        if postable: A["postable"]+=1
        # achievable combined = best-bid sum (where a maker rests)
        bidsum=bA+bB if (bA>0 and bB>0) else None
        if bidsum is not None:
            A["bidsum"].append(bidsum)
            if bidsum<=97: A["le97"]+=1
            if bidsum<=97 and postable: A["joint"]+=1

print("\n=== (1)(2)(4) COMBINED-<=97 ACHIEVABILITY x POSTABILITY x THROUGHPUT, by tier x bucket ===")
print("   achievable combined = best-BID sum (maker-restable); <=97 rate | postable% | JOINT(<=97 & postable)%")
for tr in ("main(ATP/WTA)","thin(ITF)"):
    print(f"  --- {tr} ---")
    print(f"    {'bucket':7s} {'n':>4s} {'bidsum_med':>10s} {'<=97%':>6s} {'postable%':>9s} {'JOINT%':>7s}")
    for (lbl,h) in BUCKETS:
        A=agg[tr][lbl]
        if not A["n"]: continue
        bm=st.median(A["bidsum"]) if A["bidsum"] else float('nan')
        print(f"    {lbl:7s} {A['n']:>4d} {bm:>10.0f} {100*A['le97']/A['n']:>5.0f} {100*A['postable']/A['n']:>8.0f} {100*A['joint']/A['n']:>6.0f}")
print("\nNOTE (3) drift-shapes-per-side pre-T-4h require a settlement join (winner/loser labels) — deferred to the")
print("settlement-joined pass; this run delivers coverage + combined-cost + postability + joint throughput.")
