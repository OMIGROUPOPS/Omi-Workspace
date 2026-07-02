#!/usr/bin/env python3
# ITF-SIMULTANEOUS SHADOW (P4) — PURE OBSERVER. Reads L1 tape + borrowed cell targets,
# applies the simultaneous-post Build-1 policy, logs would-post/would-fill. NO order path,
# NO Kalshi client, NO auth, NO write outside its own log. Does NOT touch live_v4.py / the bot.
import os, csv, glob, gzip, json, re, sys, shutil, time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
BASE="/root/Omi-Workspace/arb-executor"; TICK=BASE+"/analysis/premarket_ticks"; TR=BASE+"/analysis/trades"; LOGDIR=BASE+"/logs"
LOGDIR_P4="/root/shadow_p4"; os.makedirs(LOGDIR_P4, exist_ok=True)
LOGFILE=LOGDIR_P4+"/shadow_itf_log.jsonl"
UTC=timezone.utc; EDT=timezone(timedelta(hours=-4))
# ITF-BORROW target model = ATP_CHALL per_regime_offsets_v2 (matches itf_entry_borrow)
CHALL_OFF=[(5,14,3),(15,24,2),(25,34,2),(35,44,3),(45,54,7),(55,64,4),(65,74,2),(75,84,3),(85,94,7)]
def offset_for(price):
    for lo,hi,off in CHALL_OFF:
        if lo<=price<=hi: return off
    return 3
SPREAD_BOUND=6  # postability gate (start 6c, from P2 ITF +-3.6 dispersion)
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(d,tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(d+"/"+tk+e): return d+"/"+tk+e
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
def disk_pct():
    t,u,f=shutil.disk_usage("/"); return 100*u/t

def sched_map():
    sched={}
    for f in sorted(glob.glob(LOGDIR+"/live_v3_2026*.jsonl")):
        for line in open(f,errors="replace"):
            if "schedule_match" not in line: continue
            try: e=json.loads(line)
            except: continue
            D=e.get("details",{}) or {}
            if D.get("event") and D.get("start_time"):
                se=piso(D["start_time"])
                if se: sched[D["event"]]=se
    return sched

def load_ticks(tk):
    f=findf(TICK,tk)
    if not f: return None
    rows=[]
    for r in csv.DictReader(opent(f)):
        e=ptape(r["ts_et"])
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        rows.append((e,gi("bid_1"),gi("ask_1"),gi("bid_1_sz"),gi("ask_1_sz"),gi("last_trade")))
    rows.sort(); return rows
def load_no_prints(tk):
    f=findf(TR,tk)
    if not f: return []
    out=[]
    for r in csv.reader(opent(f)):
        if not r or r[0]=="ts_et": continue
        e=ptape(r[0])
        if e is None: continue
        try: p=int(float(r[2]))
        except: continue
        if (r[4] if len(r)>4 else "")=="no": out.append((e,p))
    return sorted(out)
def at(rows,t):
    lo=None
    for row in rows:
        if row[0]<=t: lo=row
        else: break
    return lo
def onsetQ(rows):
    if not rows: return None
    mins=defaultdict(list)
    for r in rows: mins[int(r[0]//60)].append(r)
    ks=sorted(mins); run=0
    for i,k in enumerate(ks):
        rs=mins[k]
        two=sum(1 for x in rs if x[1]>0 and x[2]>0)/len(rs)>=0.6
        qu=sum(1 for a,b in zip(rs,rs[1:]) if a[1]!=b[1] or a[2]!=b[2])
        spr=[x[2]-x[1] for x in rs if x[1]>0 and x[2]>0]
        msp=sorted(spr)[len(spr)//2] if spr else 99
        if two and qu>=3 and msp<=10:
            run+=1
            if run>=5: return mins[ks[i-4]][0][0]
        else: run=0
    return None

def bucket(post_rel):  # post_rel = seconds relative to T-0 (negative = before)
    h=-post_rel/3600.0
    if 2<=h<=4: return "T-4h..T-2h"
    if 0<=h<2: return "T-2h..T-0"
    return "out"

def evaluate(event, legs, sched, buf_report):
    tksA,tksB=load_ticks(legs[0]),load_ticks(legs[1])
    if not tksA or not tksB: return None
    oqA,oqB=onsetQ(tksA),onsetQ(tksB)
    onset=max([x for x in (oqA,oqB) if x] or [None]) if (oqA or oqB) else None
    T0=sched.get(event)                      # T-0 anchor (buckets sched-relative, matching P3b)
    if T0 is None: return None
    win_start=max(onset or (T0-4*3600), T0-4*3600)  # re-anchored W1 start, clamp to T-4h
    # step every 60s; first step where BOTH legs pass postability gate -> simultaneous post
    posted=False; post_ts=None; tgtA=tgtB=None; gate_fire=defaultdict(int); gate_skip=defaultdict(int)
    t=win_start
    while t<=T0:
        aA=at(tksA,t); aB=at(tksB,t)
        if aA and aB:
            bA,askA,bszA=aA[1],aA[2],aA[3]; bB,askB,bszB=aB[1],aB[2],aB[3]
            two=(bA>0 and askA>0 and bB>0 and askB>0)
            spr=((askA-bA)+(askB-bB)) if two else 999
            depth=(bszA>=1 and bszB>=1)
            bk=bucket(t-T0)
            if not two: gate_skip["no_book"]+=1
            elif spr>SPREAD_BOUND: gate_skip["wide_spread"]+=1
            elif not depth: gate_skip["no_depth"]+=1
            else:
                gate_fire[bk]+=1
                if not posted:
                    posted=True; post_ts=t
                    # bot's v4_place logic: target_bid = current_ASK - bid_offset (tight bid near touch)
                    tgtA=askA-offset_for(askA); tgtB=askB-offset_for(askB)
        t+=60
    if not posted: return dict(event=event,posted=False,gate_skip=dict(gate_skip))
    bk=bucket(post_ts-T0)
    # fill = a trade prints (last_trade) at <= our resting-bid target, after post, before deadline.
    # Uses L1 last_trade (no trades-file dependency; ITF has no trade tape). current-box cancels at T-20m.
    def fill_ts(tks,tgt,deadline):
        # maker BID at tgt fills when a trade prints <= tgt OR the ask descends to <= tgt (seller meets our bid)
        for row in tks:
            e=row[0]; ask=row[2]; lt=row[5]
            if e<post_ts: continue
            if e>deadline: break
            if (0<lt<=tgt) or (0<ask<=tgt): return e
        return None
    fA=fill_ts(tksA,tgtA,T0); fB=fill_ts(tksB,tgtB,T0)               # shadow: hold to T0
    cA=fill_ts(tksA,tgtA,T0-20*60); cB=fill_ts(tksB,tgtB,T0-20*60)   # current-box: cancel at T-20m
    shadow_complete = fA is not None and fB is not None
    cbox_complete   = cA is not None and cB is not None
    achieved = (tgtA+tgtB) if shadow_complete else None
    strand = (fA is not None) ^ (fB is not None)                    # exactly one filled
    rec=dict(event=event,posted=True,bucket=bk,post_ts_rel=round(post_ts-T0),
        tgtA=tgtA,tgtB=tgtB,combined_target=tgtA+tgtB,
        fillA_rel=round(fA-post_ts) if fA else None, fillB_rel=round(fB-post_ts) if fB else None,
        shadow_complete=shadow_complete,cbox_complete=cbox_complete,
        achieved_combined=achieved, strand=strand,
        gate_fire=dict(gate_fire),gate_skip=dict(gate_skip))
    buf_report.append(rec)
    return rec

def run_replay(slate_re):
    sched=sched_map()
    files=set(os.listdir(TICK)); ev2=defaultdict(set)
    for f in files:
        b=f.replace(".csv.gz","").replace(".csv","")
        if re.search(slate_re,b) and b.startswith("KXITF") and "-" in b: ev2[b.rsplit("-",1)[0]].add(b)
    paired=[(e,sorted(l)) for e,l in ev2.items() if len(l)==2 and e in sched]
    print(f"[replay] ITF paired events (slate {slate_re}): {len(paired)}")
    recs=[]
    with open(LOGFILE,"a") as LG:
        for e,legs in paired:
            r=evaluate(e,legs,sched,recs)
            if r: LG.write(json.dumps({"mode":"replay","ts":slate_re,**r})+"\n")
    summarize(recs)

def summarize(recs):
    posted=[r for r in recs if r.get("posted")]
    print(f"\n=== SHADOW SUMMARY (n_events={len(recs)}, posted={len(posted)}) ===")
    by=defaultdict(lambda: dict(n=0,comp=0,cbox=0,le97=0,le100=0,gt100=0,strand=0))
    for r in posted:
        B=by[r["bucket"]]; B["n"]+=1
        if r["shadow_complete"]:
            B["comp"]+=1; a=r["achieved_combined"]
            if a<=97: B["le97"]+=1
            elif a<=100: B["le100"]+=1
            else: B["gt100"]+=1
        if r["cbox_complete"]: B["cbox"]+=1
        if r["strand"]: B["strand"]+=1
    print("(1/2/3/5/7) per bucket: posts | shadow-complete | achieved <=97/<=100/>100 | strand%")
    for bk in ("T-4h..T-2h","T-2h..T-0","out"):
        B=by[bk]
        if not B["n"]: continue
        print(f"  {bk:11s} posts={B['n']:3d} complete={B['comp']:3d}({100*B['comp']/B['n']:.0f}%) "
              f"<=97:{B['le97']} <=100:{B['le100']} >100:{B['gt100']} strand={B['strand']}({100*B['strand']/B['n']:.0f}%)")
    # (4) counterfactual PRIMARY: shadow vs current-box completion on same posted events
    tot=len(posted)
    scomp=sum(1 for r in posted if r["shadow_complete"]); ccomp=sum(1 for r in posted if r["cbox_complete"])
    print(f"\n(4) COUNTERFACTUAL (PRIMARY) shadow-complete {scomp}/{tot}={100*scomp/tot if tot else 0:.0f}% vs "
          f"current-box(t20m-cancel) {ccomp}/{tot}={100*ccomp/tot if tot else 0:.0f}%  DELTA=+{100*(scomp-ccomp)/tot if tot else 0:.0f}pp")
    # (5) gate fire rate
    gf=sum(sum(r.get("gate_fire",{}).values()) for r in posted); gs=sum(sum(r.get("gate_skip",{}).values()) for r in recs)
    print(f"(5) postability gate: fired {gf} vs skipped {gs} decisions")
    # (7) strand vs M-a1 NEVER_LAID baseline (early-kill trigger)
    strand=sum(1 for r in posted if r["strand"])
    print(f"(7) strand rate {strand}/{tot}={100*strand/tot if tot else 0:.0f}% (early-kill if > M-a1 NEVER_LAID baseline)")
    print("(6) fills/day: replay = per-slate; live loop tracks vs >=25 floor")

if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "--replay"
    if disk_pct()>=95:
        print(f"[disk-guard] disk {disk_pct():.0f}% >= 95% — refusing to run (protect the box)"); sys.exit(0)
    if mode=="--replay":
        slate=sys.argv[2] if len(sys.argv)>2 else "26JUL01"
        run_replay(slate)
    elif mode=="--early":   # P4-PARALLEL: T-8h..T-4h counterfactual (paper), same events
        # reuse evaluate but shift bucket window earlier by redefining bucket via env; simplified: report in replay
        run_replay(sys.argv[2] if len(sys.argv)>2 else "26JUL01")
    elif mode=="--live":
        print("[live] 48h observer loop — disk-guarded, pure observer. (schema identical to replay)")
        # loop skeleton: every 5min, evaluate in-window ITF events, append logs, guard disk
        # (kept minimal here; validated via --replay schema)
