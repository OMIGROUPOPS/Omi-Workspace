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
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","ITF_M","ITF_W"]: SAMPLE+=bycat[c][:30]

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
    if not rows: return None
    mins=defaultdict(list)
    for (e,b,a,lt) in rows: mins[int(e//60)].append((e,b,a,lt))
    ks=sorted(mins)
    def active(k):
        rs=mins[k]
        two=sum(1 for (e,b,a,lt) in rs if b>0 and a>0)/len(rs)>=0.6
        qu=sum(1 for (p,c) in zip(rs,rs[1:]) if p[1]!=c[1] or p[2]!=c[2])
        spr=[a-b for (e,b,a,lt) in rs if b>0 and a>0]; msp=st.median(spr) if spr else 99
        trs=sum(1 for (p,c) in zip(rs,rs[1:]) if p[3]!=c[3] and c[3]>0)
        return (two and qu>=3 and msp<=10) if mode=="Q" else (two and trs>=3)
    run=0
    for i,k in enumerate(ks):
        if active(k):
            run+=1
            if run>=5: return mins[ks[i-4]][0][0]
        else: run=0
    return None

W1_LOOKBACK=4*3600; BUF=20*60
offbytier=defaultdict(list); rows_out=[]; ext=defaultdict(int); trim=defaultdict(int); w2undet=defaultdict(int); tot=defaultdict(int)
for e in SAMPLE:
    legs=sorted(ev2[e]); tk=legs[0]; s=sched[e]; c=cat(e+"-X"); tot[c]+=1
    rows=load(tk); oq=onset(rows,"Q"); ot=onset(rows,"T")
    if oq is None: continue
    offbytier[c].append((oq-s)/60.0)
    old_w1_start=s-W1_LOOKBACK           # old premarket lookback start (sched-4h)
    w1_start=oq                          # RE-ANCHORED W1 start = tape-onset (ONSET-Q)
    if w1_start<old_w1_start: ext[c]+=1  # market active before old lookback -> W1 EXTENDS
    else: trim[c]+=1                      # market activated later -> W1 TRIMS dead lead
    gun=ot                               # W2 start = match-live (ONSET-T)
    if gun is None: w2undet[c]+=1
    w2_start_rel=(gun-s)/60.0 if gun else None
    corridor_start_rel=(w2_start_rel-20) if gun else None
    rows_out.append(dict(event=e,tier=c,onsetQ_off_min=round((oq-s)/60.0,1),
        onsetT_off_min=round((ot-s)/60.0,1) if ot else None,
        W1_start_rel_min=round((w1_start-s)/60.0,1), W2_start_rel_min=round(w2_start_rel,1) if gun else None,
        corridor_start_rel_min=round(corridor_start_rel,1) if gun else None,
        W1_flag=("EXTEND" if w1_start<old_w1_start else "trim"), W2_detect=(gun is not None)))

# save full per-event table
with open("/tmp/window_boundaries_reanchored.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows_out[0].keys())); w.writeheader(); w.writerows(rows_out)

print("=== P3a WINDOW-MAP RE-DERIVATION — per-tier ONSET-Q offset vs scheduled (min; +=onset AFTER sched) ===")
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","ITF_M","ITF_W"]:
    x=sorted(offbytier[c])
    if not x: continue
    n=len(x); tails=sum(1 for v in x if abs(v)>15)
    def pc(q): return x[min(n-1,int(q*n))]
    print(f"  {c:9s} n={n:2d}  median {st.median(x):+6.0f}  IQR[{pc(.25):+.0f},{pc(.75):+.0f}]  min{x[0]:+.0f}/max{x[-1]:+.0f}  |>15min|={tails}({100*tails/n:.0f}%)")
print("\n  MAIN(ATP/WTA) pooled vs ITF pooled:")
mainoff=offbytier["ATP_MAIN"]+offbytier["WTA_MAIN"]+offbytier["ATP_CHALL"]; itfoff=offbytier["ITF_M"]+offbytier["ITF_W"]
for nm,x in (("main",mainoff),("ITF",itfoff)):
    x=sorted(x); n=len(x); tails=sum(1 for v in x if abs(v)>15)
    print(f"    {nm:5s} n={n:2d} median {st.median(x):+.0f}min  |>15min|={100*tails/n:.0f}%")
print("\n=== W1 re-anchor classification per tier (EXTEND = market active before old sched-4h lookback) ===")
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","ITF_M","ITF_W"]:
    if tot[c]: print(f"  {c:9s} EXTEND={ext[c]} trim={trim[c]} W2-undetectable(no trade-burst)={w2undet[c]} / n={tot[c]}")
print("\n=== sample per-event boundary rows (rel to scheduled start, min) ===")
print(f"  {'event':38s} {'tier':9s} {'onsetQ':>7s} {'onsetT':>7s} {'W1st':>6s} {'corr_st':>7s} {'W2st':>6s} {'W1flag':7s} W2det")
for r in rows_out[:2]+[x for x in rows_out if x['tier']=='ITF_M'][:2]+[x for x in rows_out if x['tier']=='ATP_MAIN'][:2]:
    print(f"  {r['event'][-38:]:38s} {r['tier']:9s} {str(r['onsetQ_off_min']):>7s} {str(r['onsetT_off_min']):>7s} {str(r['W1_start_rel_min']):>6s} {str(r['corridor_start_rel_min']):>7s} {str(r['W2_start_rel_min']):>6s} {r['W1_flag']:7s} {r['W2_detect']}")
print("wrote /tmp/window_boundaries_reanchored.csv  n=%d"%len(rows_out))
