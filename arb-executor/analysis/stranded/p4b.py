#!/usr/bin/env python3
# P4b SHAPE-SEQUENCED REPLAY (read-only). Doctrine policy: favorite bid EARLY (T-8h..T-4h),
# dog bid LATE (T-2h..T-0), each at ask-offset, postability-gated, hold to T-0.
import os, csv, glob, gzip, json, re, sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict
BASE="/root/Omi-Workspace/arb-executor"; TICK=BASE+"/analysis/premarket_ticks"; LOGDIR=BASE+"/logs"
UTC=timezone.utc; EDT=timezone(timedelta(hours=-4))
CHALL_OFF=[(5,14,3),(15,24,2),(25,34,2),(35,44,3),(45,54,7),(55,64,4),(65,74,2),(75,84,3),(85,94,7)]
def offset_for(p):
    for lo,hi,off in CHALL_OFF:
        if lo<=p<=hi: return off
    return 3
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(TICK+"/"+tk+e): return TICK+"/"+tk+e
    return None
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
for f in sorted(glob.glob(LOGDIR+"/live_v3_2026*.jsonl*")):
    for line in opent(f):
        if "schedule_match" not in line: continue
        try: e=json.loads(line)
        except: continue
        D=e.get("details",{}) or {}
        if D.get("event") and D.get("start_time"):
            se=piso(D["start_time"])
            if se: sched[D["event"]]=se
def load(tk):
    f=findf(tk)
    if not f: return None
    rows=[]
    for r in csv.DictReader(opent(f)):
        e=ptape(r["ts_et"])
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        rows.append((e,gi("bid_1"),gi("ask_1"),gi("bid_1_sz"),gi("last_trade")))
    rows.sort(); return rows
def at(rows,t):
    lo=None
    for row in rows:
        if row[0]<=t: lo=row
        else: break
    return lo
def post_in_window(rows,lo,hi):   # first gate-pass in [lo,hi]; post at ask-offset
    for row in rows:
        e,b,a,bs,lt=row
        if e<lo: continue
        if e>hi: break
        if b>0 and a>0 and (a-b)<=6 and bs>=1:
            return e, a-offset_for(a)
    return None,None
def fill_after(rows,tgt,start,deadline):
    for row in rows:
        e,b,a,bs,lt=row
        if e<start: continue
        if e>deadline: break
        if (0<lt<=tgt) or (0<a<=tgt): return e
    return None

files=set(os.listdir(TICK)); ev2=defaultdict(set)
for f in files:
    b=f.replace(".csv.gz","").replace(".csv","")
    if re.search("26JUL01",b) and b.startswith("KXITF") and "-" in b: ev2[b.rsplit("-",1)[0]].add(b)
paired=[(e,sorted(l)) for e,l in ev2.items() if len(l)==2 and e in sched]
print(f"[P4b] ITF paired events (26JUL01): {len(paired)}")

def run(dog_mode):
    # dog_mode: "late"=T-2h..T-0 ; "static_t4h"=T-4h..T-2h (variant)
    comp=0; scored=0; le97=le100=gt100=0; strand=0; strand_fav=0; strand_dog=0
    fav_fill_phase=defaultdict(int); dog_fill_phase=defaultdict(int); cbox=0
    for e,legs in paired:
        rA,rB=load(legs[0]),load(legs[1])
        if not rA or not rB: continue
        T0=sched[e]
        ref=T0-4*3600
        mA=at(rA,ref); mB=at(rB,ref)
        if not mA or not mB or mA[1]<=0 or mB[1]<=0: continue
        midA=(mA[1]+mA[2])/2; midB=(mB[1]+mB[2])/2
        if midA>=midB: favr,dogr=rA,rB   # favorite = higher-mid leg
        else: favr,dogr=rB,rA
        # FAV early, DOG late/variant
        pf,tf=post_in_window(favr,T0-8*3600,T0-4*3600)
        if dog_mode=="late": pd,td=post_in_window(dogr,T0-2*3600,T0)
        else: pd,td=post_in_window(dogr,T0-4*3600,T0-2*3600)
        if pf is None or pd is None: continue
        scored+=1
        ff=fill_after(favr,tf,pf,T0); df_=fill_after(dogr,td,pd,T0)
        # current-box counterfactual (both posted at their windows, cancel unfilled at T-20m)
        ffc=fill_after(favr,tf,pf,T0-20*60); dfc=fill_after(dogr,td,pd,T0-20*60)
        if ffc and dfc: cbox+=1
        if ff and df_:
            comp+=1; combined=tf+td
            if combined<=97: le97+=1
            elif combined<=100: le100+=1
            else: gt100+=1
            fav_fill_phase["filled"]+=1; dog_fill_phase["filled"]+=1
        elif ff or df_:
            strand+=1
            if ff and not df_: strand_dog+=1   # fav filled, dog stranded
            elif df_ and not ff: strand_fav+=1 # dog filled, fav stranded
    tot=scored
    print(f"\n--- dog_mode={dog_mode} (fav EARLY T-8h..T-4h; dog {'LATE T-2h..T-0' if dog_mode=='late' else 'STATIC T-4h..T-2h'}) ---")
    print(f"  scored pairs (both legs postable in their windows): {tot}")
    if tot:
        print(f"  COMPLETION: {comp}/{tot} = {100*comp/tot:.0f}%   (vs static-simultaneous baseline 0%, vs current-box {cbox}/{tot}={100*cbox/tot:.0f}%)")
        print(f"  achieved-combined: <=97:{le97} 98-100:{le100} >100:{gt100}")
        print(f"  strand: {strand}/{tot}={100*strand/tot:.0f}%  (which side: dog-stranded={strand_dog}, fav-stranded={strand_fav})")

run("late")
run("static_t4h")
