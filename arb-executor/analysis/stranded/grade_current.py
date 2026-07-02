#!/usr/bin/env python3
# GRADE THE CURRENT DEPLOY BOX (Jun30 15:46 bisect -> now). Read-only. Rubric + mechanism rollup.
import os, csv, glob, gzip, json, re, statistics as st
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
BASE="/root/Omi-Workspace/arb-executor"; TICK=BASE+"/analysis/premarket_ticks"; TR=BASE+"/analysis/trades"; LOGDIR=BASE+"/logs"
EDT=timezone(timedelta(hours=-4))
START=datetime(2026,6,30,15,46,tzinfo=EDT).timestamp()
LOGS=[LOGDIR+"/live_v3_20260630.jsonl",LOGDIR+"/live_v3_20260701.jsonl"]
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

L=defaultdict(lambda: dict(place=[],placed=[],cancel=[],fill=[],walk=[],settle=None,skip=Counter(),mlive=None,exitp=[]))
for f in LOGS:
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        ts=e.get("ts_epoch")
        if ts is None or ts<START: continue
        tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}
        if not tk: continue
        d=L[tk]
        if ev=="v4_place": d["place"].append((ts,D.get("target_bid"),D.get("cell"),D.get("current_ask")))
        elif ev=="order_placed" and D.get("action")=="buy": d["placed"].append((ts,D.get("price")))
        elif ev=="order_cancelled": d["cancel"].append((ts,D.get("label")))
        elif ev in ("entry_filled","completion_fill"): d["fill"].append((ts,D.get("fill_price"),ev))
        elif ev=="v4_move_repost": d["walk"].append((ts,D.get("new_target")))
        elif ev=="settled": d["settle"]=(D.get("settle"),D.get("pnl_dollars"))
        elif ev in ("match_live_resting_cancel","v4_resting_cancel"): d["mlive"]=ts if d["mlive"] is None else min(d["mlive"],ts)
        elif ev=="skipped": d["skip"][D.get("reason","")]+=1

legs=[tk for tk,d in L.items() if d["placed"] or d["place"] or d["fill"]]
events=defaultdict(list)
for tk in legs: events[evkey(tk)].append(tk)

def load_tape(tk):
    f=findf(TICK,tk)
    if not f: return None
    rows=[]
    for r in csv.DictReader(opent(f)):
        e=ptape(r["ts_et"])
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        rows.append((e,gi("bid_1"),gi("bid_1_sz"),gi("ask_1"),gi("ask_1_sz"),gi("last_trade")))
    rows.sort(); return rows
def best_fillable(tk):
    # lowest last_trade price that printed with real size backing (bid_1_sz>=5) = a level a 5-lot maker bid could catch
    rows=load_tape(tk)
    if not rows: return None
    lows=[lt for (e,b,bs,a,az,lt) in rows if lt>0 and bs>=5]
    return min(lows) if lows else None
def no_prints(tk):
    f=findf(TR,tk)
    if not f: return []
    out=[]
    for r in csv.reader(opent(f)):
        if not r or r[0]=="ts_et": continue
        try: p=int(float(r[2])); c=int(float(r[3]))
        except: continue
        if (r[4] if len(r)>4 else "")=="no": out.append((p,c))
    return out

# per-pair grade
def realized(tk):
    d=L[tk]
    return d["settle"][1] if d["settle"] and d["settle"][1] is not None else None
def filled(tk): return len(L[tk]["fill"])>0
def fillpx(tk): return L[tk]["fill"][0][1] if L[tk]["fill"] else None
def walked(tk): return len(L[tk]["walk"])>0

grades=[]
for ek,ls in events.items():
    c=cat(ek+"-X")
    fc=[tk for tk in ls if filled(tk)]
    rec=dict(event=ek,cat=c,nlegs=len(ls),nfill=len(fc))
    if len(fc)==2:
        a,b=fc; comb=fillpx(a)+fillpx(b)
        rec.update(state="BOTH",combined=comb, walked=(walked(a) or walked(b)),
                   realized=sum(x for x in (realized(a),realized(b)) if x is not None))
        # per-leg fill-quality gap vs best-fillable
        for tk in fc:
            bf=best_fillable(tk); rec.setdefault("gaps",[]).append((leg(tk),fillpx(tk),bf,(fillpx(tk)-bf) if bf is not None else None))
    elif len(fc)==1:
        kept=fc[0]; missed=[tk for tk in ls if tk!=kept]
        rec.update(state="ONE",kept=leg(kept),kept_fill=fillpx(kept),realized=realized(kept))
        if missed:
            mt=missed[0]
            # miss class
            iv_prices=[p for (_,p) in L[mt]["placed"]]; tgt=[a[1] for a in L[mt]["place"] if a[1] is not None]
            ref=max(iv_prices+tgt+[0]); bf=best_fillable(mt); nps=no_prints(mt)
            if not L[mt]["placed"] and not L[mt]["place"]: cls="NEVER_LAID"
            elif L[mt]["cancel"] and not filled(mt): cls="PULLED"
            elif bf is not None and ref<bf: cls="TOO_DEEP"
            else: cls="NEVER_LAID"
            catch=[(p,cc) for (p,cc) in nps if p<=ref+2]
            rec.update(missed=leg(mt),miss_cls=cls,missed_best_fillable=bf,
                       forfeit_combined=(fillpx(kept)+bf) if bf is not None else None,
                       postable=(load_tape(mt) is not None and any(x[1]>0 and x[3]>0 for x in (load_tape(mt) or []))))
    else:
        rec.update(state="MISSED_BOTH")
    grades.append(rec)

# ==== REPORT ====
print(f"=== CURRENT DEPLOY BOX GRADE (Jun30 15:46 -> now) : {len(events)} events, {len(legs)} legs touched ===")
both=[g for g in grades if g["state"]=="BOTH"]; one=[g for g in grades if g["state"]=="ONE"]; mb=[g for g in grades if g["state"]=="MISSED_BOTH"]
print(f"[1] pair completion: BOTH {len(both)} | ONE-sided {len(one)} | MISSED-both {len(mb)}  = completion {100*len(both)/len(events):.0f}%")
cb=Counter("<100" if g["combined"]<100 else ">=100" for g in both); c97=sum(1 for g in both if g["combined"]<=97)
print(f"[2] combined on BOTH-filled: <100 {cb['<100']} (of which <=97: {c97}) | >=100 {cb['>=100']}")
if both:
    combs=sorted(g["combined"] for g in both); print(f"    combined dist: min {combs[0]} med {int(st.median(combs))} max {combs[-1]}")
# [3] per-leg fill-quality gap (achieved - best_fillable)
gaps=[gp[3] for g in both for gp in g.get("gaps",[]) if gp[3] is not None]
if gaps:
    gs=sorted(gaps); print(f"[3] per-leg gap achieved-vs-best-fillable (c): med {int(st.median(gs))} | overpaid>0: {sum(1 for x in gs if x>0)}/{len(gs)} | worst +{gs[-1]}")
print(f"[miss] classes: {Counter(g.get('miss_cls') for g in one if g.get('miss_cls'))}")
# realized P&L
realized_tot=sum(g["realized"] for g in grades if g.get("realized") is not None)
nsettled=sum(1 for g in grades if g.get("realized") is not None)
print(f"[P&L] realized (settled legs) events with data: {nsettled}; box realized so far: ${realized_tot:.2f}")

# ==== MECHANISM ROLLUP (dollar-weighted) ====
print("\n=== MECHANISM ROLLUP (pairs touched | realized$ on them | implication) ===")
def mech_pairs(pred):
    evs=set()
    for ek,ls in events.items():
        if any(pred(tk) for tk in ls): evs.add(ek)
    return evs
def dollars(evs):
    tot=0.0; n=0
    for ek in evs:
        for tk in events[ek]:
            r=realized(tk)
            if r is not None: tot+=r; n+=1
    return tot,n
mechs={
 "v4_t20m_fallback": lambda tk: any(lb=="v4_t20m_fallback" for (_,lb) in L[tk]["cancel"]),
 "itf_recent_volume_floor": lambda tk: L[tk]["skip"].get("itf_recent_volume_floor",0)>0,
 "maker_only_no_late_entry": lambda tk: L[tk]["skip"].get("maker_only_no_late_entry",0)>0,
 "walk(v4_move_repost)": lambda tk: walked(tk),
 "completion_ceiling(completion_fill)": lambda tk: any(ev=="completion_fill" for (_,_,ev) in L[tk]["fill"]),
}
roll=[]
for name,pred in mechs.items():
    evs=mech_pairs(pred); d,n=dollars(evs); roll.append((name,len(evs),d,n))
for name,npairs,d,n in sorted(roll,key=lambda x:-x[1]):
    print(f"  {name:34s} pairs={npairs:3d}  realized_on_them=${d:+.2f} (n_settled={n})")
# walk completions specifically
walk_comp=[g for g in both if g.get("walked")]
print(f"  -> walk produced completions: {len(walk_comp)}/{len(both)} both-fills involved a walk; their combined med={int(st.median([g['combined'] for g in walk_comp])) if walk_comp else 0}")

# ==== EXHIBITS ====
def exhibit(evk):
    print(f"\n### EXHIBIT {evk}")
    for tk in sorted(events.get(evk,[])):
        d=L[tk]; tl=[]
        for (ts,p) in d["placed"]: tl.append((ts,f"post {p}"))
        for (ts,nt) in d["walk"]: tl.append((ts,f"walk->{nt}"))
        for (ts,lb) in d["cancel"]: tl.append((ts,f"cancel[{lb}]"))
        for (ts,fp,ev) in d["fill"]: tl.append((ts,f"FILL {fp} ({ev})"))
        tl.sort()
        bf=best_fillable(tk)
        print(f"  {leg(tk):4s} best_fillable={bf} settle={d['settle']}  " + " | ".join(f"{datetime.fromtimestamp(t,EDT).strftime('%H:%M')} {x}" for t,x in tl[:16]))
for e in list(events):
    if "BOUHAR" in e: exhibit(e)
for e in list(events):
    if "NASCHA" in e: exhibit(e)
json.dump(grades, open("/root/shadow_p4/grade_current.json","w"), default=str)
print("\nwrote /root/shadow_p4/grade_current.json")
