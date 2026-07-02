#!/usr/bin/env python3
# P6 — CAPPED-WALK REPLAY + CEILING SWEEP. Read-only.
# Walk model = the bot's ACTUAL logged bid trajectory (v4_place target_bid + each v4_move_repost new_target).
# Intervention = a COMBINED CAP applied by construction: the leader (higher) leg's walk is clamped so
#   leaderTgt(t) <= CAP - followerTgt(t) at all times. Follower (cheaper) leg unclamped.
# For each CAP in {95,96,97,98,99,uncapped} we replay fills against the L1 tape and report:
#   completions/day-equiv, combined distribution (median+shape), locked-edge ($), P&L under 3 fixed exit policies.
# VALIDATION: uncapped must approx-reproduce the live box (combined 98-100, completion by flag era) or the
#   walk model is miscalibrated (STOP before judging). PASS/FAIL judged at CAP-97 on 3 pre-committed axes.
import os, csv, glob, gzip, json, sys, statistics as st
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
BASE="/root/Omi-Workspace/arb-executor"; TICK=BASE+"/analysis/premarket_ticks"; TR=BASE+"/analysis/trades"; LOGDIR=BASE+"/logs"
EDT=timezone(timedelta(hours=-4))
def ep(y,mo,d,h,mi): return datetime(y,mo,d,h,mi,tzinfo=EDT).timestamp()
# BOX = current deploy box (matches grade_current.py START)
BOX_START=ep(2026,6,30,15,46)
LOGS=[LOGDIR+"/live_v3_20260630.jsonl",LOGDIR+"/live_v3_20260701.jsonl"]
CAPS=[95,96,97,98,99,None]   # None = uncapped
BAND=8       # E2 exit band (observed +7/+8 adaptive; fixed here)
STOP=12      # E3 loser stop (cut loser at entry-STOP)
QTY=5        # shares per leg

def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(d,tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(d+"/"+tk+e): return d+"/"+tk+e
    return None
def cat(t):
    for p,c in (("KXATPCHALLENGERMATCH","ATP_CHALL"),("KXWTACHALLENGERMATCH","WTA_CHALL"),("KXATPMATCH","ATP_MAIN"),("KXWTAMATCH","WTA_MAIN"),("KXITFWMATCH","ITF_W"),("KXITFMATCH","ITF_M")):
        if t.startswith(p): return c
    return "?"
def evkey(t): return t.rsplit("-",1)[0]
def leg(t): return t.rsplit("-",1)[1] if "-" in t else t
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None

# ---- ingest logs: per-leg trajectory + fill + settle + deadline ----
L=defaultdict(lambda: dict(traj=[],fill=None,settle=None,mlive=None,first=None,last=None))
# substring pre-filter: only json.loads the ~handful of event types we ingest (1.38M lines -> ~50k parses)
NEED=('"v4_place"','"v4_move_repost"','"entry_filled"','"completion_fill"','"settled"','resting_cancel','match_live_cancel')
for f in LOGS:
    if not os.path.exists(f): continue
    for line in open(f,errors="replace"):
        if not any(t in line for t in NEED): continue
        try: e=json.loads(line)
        except: continue
        ts=e.get("ts_epoch")
        if ts is None or ts<BOX_START: continue
        tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}
        if not tk: continue
        d=L[tk]
        if ev=="v4_place" and D.get("target_bid") is not None:
            d["traj"].append((ts,int(D["target_bid"])))
        elif ev=="v4_move_repost" and D.get("new_target") is not None:
            d["traj"].append((ts,int(D["new_target"])))
        elif ev in ("entry_filled","completion_fill") and d["fill"] is None:
            d["fill"]=(ts,D.get("fill_price"))
        elif ev=="settled":
            d["settle"]=(D.get("settle"),D.get("pnl_dollars"))
        elif ev in ("match_live_resting_cancel","v4_resting_cancel","match_live_cancel"):
            d["mlive"]=ts if d["mlive"] is None else min(d["mlive"],ts)
        if d["first"] is None or ts<d["first"]: d["first"]=ts
        d["last"]=ts if d["last"] is None else max(d["last"],ts)
for tk in L:
    L[tk]["traj"].sort()

# ---- tape (NO global cache; csv.reader+index, not DictReader, for speed) ----
def load_tape(tk):
    f=findf(TICK,tk)
    if not f: return None
    op=opent(f); rdr=csv.reader(op)
    hdr=next(rdr,None)
    if not hdr: return []
    ix={h:i for i,h in enumerate(hdr)}
    ci=[ix.get(c,-1) for c in ("ts_et","bid_1","ask_1","bid_1_sz","ask_1_sz","last_trade")]
    rows=[]
    for r in rdr:
        try: e=ptape(r[ci[0]])
        except: continue
        if e is None: continue
        def gi(j):
            if j<0: return 0
            try: return int(float(r[j] or 0))
            except: return 0
        rows.append((e,gi(ci[1]),gi(ci[2]),gi(ci[3]),gi(ci[4]),gi(ci[5])))
    rows.sort(); return rows

def active_tgt(traj,t):
    v=None
    for (ts,tg) in traj:
        if ts<=t: v=tg
        else: break
    return v

def median_tgt(traj):
    vs=[tg for _,tg in traj]
    return st.median(vs) if vs else 0

# two-pointer linear-pass fills (traj is time-sorted; advance a pointer instead of rescanning)
def fill_follower(rows, trajF, post_start, deadline):
    if not rows or not trajF: return None
    iF=0; nF=len(trajF); curF=None
    for (e,bid,ask,bsz,asz,lt) in rows:
        if deadline is not None and e>deadline: break
        while iF<nF and trajF[iF][0]<=e: curF=trajF[iF][1]; iF+=1
        if e<post_start or curF is None: continue
        if (0<lt<=curF) or (0<ask<=curF): return (e,curF)
    return None
def fill_leader(rows, trajL, trajF, CAP, post_start, deadline):
    if not rows or not trajL: return None
    iL=0; nL=len(trajL); curL=None
    iF=0; nF=len(trajF); curF=None
    firstF=trajF[0][1] if trajF else 0
    for (e,bid,ask,bsz,asz,lt) in rows:
        if deadline is not None and e>deadline: break
        while iL<nL and trajL[iL][0]<=e: curL=trajL[iL][1]; iL+=1
        while iF<nF and trajF[iF][0]<=e: curF=trajF[iF][1]; iF+=1
        if e<post_start or curL is None: continue
        if CAP is None: tg=curL
        else:
            ft=curF if curF is not None else firstF
            tg=min(curL, CAP-ft)     # combined cap by construction: leader clamped by CAP - follower
        if (0<lt<=tg) or (0<ask<=tg): return (e,tg)
    return None

# ---- build paired events (both legs touched in box) ----
events=defaultdict(list)
for tk,d in L.items():
    if d["traj"] or d["fill"]:
        events[evkey(tk)].append(tk)
pairs=[(ek,sorted(ls)) for ek,ls in events.items() if len(ls)==2]

# tape day-span for /day-equiv
all_ts=[d["first"] for d in L.values() if d["first"]]+[d["last"] for d in L.values() if d["last"]]
DAYS=max(1.0,(max(all_ts)-min(all_ts))/86400.0) if all_ts else 1.0

def deadline_for(a,b):
    # hold-to-settle window: fills allowed until the LATER of the two legs' last log activity (proxy for settle window)
    ds=[L[a]["mlive"],L[b]["mlive"]]
    ml=[x for x in ds if x]
    # cap window at the last observed tape activity; use last log ts + 2h tail
    end=max(L[a]["last"] or 0, L[b]["last"] or 0)+2*3600
    return end   # walk-hold: we DO NOT cancel at t20m/mlive in P6 (the walk-hold thesis); mlive kept for reference

# ONE pass over pairs. Load each pair's 2 tapes ONCE, evaluate ALL caps in hand, then release
# (memory bounded to 2 tapes at a time — safe on the 2GB box). Follower fill is cap-independent.
def run_all_caps():
    import sys as _sys
    comp={tag(c):[] for c in CAPS}; strand={tag(c):0 for c in CAPS}
    for _i,(ek,(a,b)) in enumerate(pairs):
        if _i%20==0: print(f"[progress] pair {_i}/{len(pairs)} {ek[-24:]}",file=_sys.stderr,flush=True)
        ta,tb=L[a]["traj"],L[b]["traj"]
        if not ta or not tb: continue
        if median_tgt(ta)>=median_tgt(tb): lead,foll=a,b
        else: lead,foll=b,a
        trajL,trajF=L[lead]["traj"],L[foll]["traj"]
        post_start=min([t for t,_ in trajL+trajF] or [0])
        dl=deadline_for(a,b)
        rowsL=load_tape(lead); rowsF=load_tape(foll)   # loaded once for this pair
        fF=fill_follower(rowsF, trajF, post_start, dl)  # cap-independent
        for CAP in CAPS:
            fL=fill_leader(rowsL, trajL, trajF, CAP, post_start, dl)
            tg=tag(CAP)
            if fL and fF:
                comp[tg].append(dict(event=ek,cat=cat(ek+"-X"),combined=fL[1]+fF[1],
                                     leadpx=fL[1],follpx=fF[1],lead=leg(lead),foll=leg(foll),
                                     settle=(L[lead]["settle"],L[foll]["settle"])))
            elif fL or fF:
                strand[tg]+=1
        del rowsL, rowsF   # release tapes before next pair
    return comp,strand

def tag(c): return "uncap" if c is None else str(c)

# ---- exit policies (on a completed pair). Returns $ per pair (QTY shares) ----
def exit_E1(p):   # HOLD-TO-SETTLE : mirror pair -> guaranteed locked edge
    return (100-p["combined"])/100.0*QTY
def _outcome(p):  # which leg (lead/foll) settled to WIN(100), from settle data; None if unknown
    sL,sF=p["settle"]
    sl=sL[0] if sL else None; sf=sF[0] if sF else None
    if sl=="WIN": return "lead"
    if sf=="WIN": return "foll"
    return None
def exit_E2(p):   # BAND+8 both legs, else settle. needs outcome for settle legs.
    oc=_outcome(p)
    if oc is None: return None
    # winner: sells at entry+BAND if reachable else settles 100. loser: rarely reaches +BAND, settles 0.
    # We approximate: winner captures min(band, to-100); loser held to 0 (band unreachable on a faller).
    if oc=="lead": win_e,lose_e=p["leadpx"],p["follpx"]
    else: win_e,lose_e=p["follpx"],p["leadpx"]
    win_gain=min(BAND,100-win_e)      # +band capped at 100
    lose_loss=lose_e                  # loser to 0
    return (win_gain-lose_loss)/100.0*QTY
def exit_E3(p):   # WINNER-RIDE to settle, LOSER-STOP at entry-STOP
    oc=_outcome(p)
    if oc is None: return None
    if oc=="lead": win_e,lose_e=p["leadpx"],p["follpx"]
    else: win_e,lose_e=p["follpx"],p["leadpx"]
    win_gain=100-win_e                       # winner rides to settle
    lose_loss=min(lose_e,STOP)               # loser cut at STOP (loss = min(entry, stop))
    return (win_gain-lose_loss)/100.0*QTY

def dist(xs):
    xs=sorted(xs)
    if not xs: return "n=0"
    return f"n={len(xs)} min={xs[0]} med={int(st.median(xs))} p75={xs[min(len(xs)-1,int(len(xs)*.75))]} max={xs[-1]}"

print(f"=== P6 CAPPED-WALK CEILING SWEEP === box start {datetime.fromtimestamp(BOX_START,EDT):%Y-%m-%d %H:%M} | {len(pairs)} paired events | tape span {DAYS:.2f} d")
print(f"{'CAP':>7} | {'comp':>4} {'/day':>5} | {'strand':>6} | {'combined dist':<34} | {'lockE$':>7} | {'E1$':>7} {'E2$':>8} {'E3$':>8} | {'<=97':>4} {'96-97cl':>7}")
COMP,STRAND=run_all_caps()   # single pass, memory-bounded
frontier={}
for CAP in CAPS:
    tg=tag(CAP); comp=COMP[tg]; strand=STRAND[tg]
    combs=[p["combined"] for p in comp]
    le=sum(exit_E1(p) for p in comp)
    e2v=[exit_E2(p) for p in comp]; e3v=[exit_E3(p) for p in comp]
    e2=sum(x for x in e2v if x is not None); e3=sum(x for x in e3v if x is not None)
    n97=sum(1 for c in combs if c<=97); cluster=sum(1 for c in combs if c in (96,97))
    percat=Counter(p["cat"] for p in comp)
    print(f"{tg:>7} | {len(comp):>4} {len(comp)/DAYS:>5.1f} | {strand:>6} | {dist(combs):<34} | {le:>7.2f} | {le:>7.2f} {e2:>8.2f} {e3:>8.2f} | {n97:>4} {cluster:>7}")
    frontier[tg]=dict(comp=len(comp),per_day=len(comp)/DAYS,strand=strand,
                       combined=combs,locked=le,E1=le,E2=e2,E3=e3,n97=n97,cluster9697=cluster,
                       percat=dict(percat),
                       e2_cov=sum(1 for x in e2v if x is not None),e3_cov=sum(1 for x in e3v if x is not None))

# ---- VALIDATION: uncapped vs known live box ----
u=frontier["uncap"]; ucombs=sorted(u["combined"])
print(f"\n=== VALIDATION (uncapped must reproduce live box) ===")
if ucombs:
    inband=sum(1 for c in ucombs if 98<=c<=100)
    print(f"  uncapped combined: {dist(ucombs)} | in 98-100 band: {inband}/{len(ucombs)}={100*inband/len(ucombs):.0f}%")
    print(f"  uncapped completions/day: {u['per_day']:.1f} (live box completion regime)")
    print(f"  -> {'PASS: reproduces box (median in 98-100, clustered high)' if 98<=st.median(ucombs)<=100 else 'FAIL: walk model miscalibrated — median NOT in 98-100, DO NOT judge axes'}")
else:
    print("  FAIL: no uncapped completions — walk model produced nothing.")

# ---- PASS/FAIL at CAP-97 (pre-committed) ----
c97=frontier["97"]
print(f"\n=== PASS/FAIL @ CAP-97 (pre-committed axes) ===")
med97=int(st.median(c97["combined"])) if c97["combined"] else None
ax1 = c97["per_day"]>=25
ax2 = (med97 is not None and med97<=95) and not (c97["cluster9697"]>0 and c97["cluster9697"]>=0.5*len(c97["combined"]))
print(f"  axis1 >=25 completions/day : {c97['per_day']:.1f} -> {'PASS' if ax1 else 'FAIL'}")
print(f"  axis2 median<=95, no 96-97 pile : med={med97} cluster={c97['cluster9697']}/{len(c97['combined'])} -> {'PASS' if ax2 else 'FAIL'}")
print(f"  axis3 reproducible signature : deterministic replay | per-cat completions @97: {c97.get('percat',{})} | n={c97['comp']} both-fills, {c97['n97']} <=97")
verdict = "PASS" if (ax1 and ax2) else "FAIL (closure fires per pre-commit)"
print(f"  VERDICT @ cap-97: {verdict}")

json.dump({k:{kk:vv for kk,vv in v.items() if kk!='combined'} | {'combined':v['combined']} for k,v in frontier.items()},
          open("/root/shadow_p4/p6_frontier.json","w"), default=str)
print("\nwrote /root/shadow_p4/p6_frontier.json")
