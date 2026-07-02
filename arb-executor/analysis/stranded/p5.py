#!/usr/bin/env python3
# P5 CORE — BOUHAR-class survival study (walked completions <100). Read-only.
import os, glob, json, statistics as st
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
BASE="/root/Omi-Workspace/arb-executor"; LOGDIR=BASE+"/logs"
EDT=timezone(timedelta(hours=-4))
def ep(y,mo,d,h,mi): return datetime(y,mo,d,h,mi,tzinfo=EDT).timestamp()
PRIOR=(ep(2026,6,30,0,56), ep(2026,6,30,15,46))
CURRENT=(ep(2026,6,30,15,46), ep(2026,7,3,0,0))
LOGS=[LOGDIR+"/live_v3_20260630.jsonl",LOGDIR+"/live_v3_20260701.jsonl"]
def cat(t):
    for p,c in (("KXATPCHALLENGERMATCH","ATP_CHALL"),("KXWTACHALLENGERMATCH","WTA_CHALL"),("KXATPMATCH","ATP_MAIN"),("KXWTAMATCH","WTA_MAIN"),("KXITFWMATCH","ITF_W"),("KXITFMATCH","ITF_M")):
        if t.startswith(p): return c
    return "?"
def evkey(t): return t.rsplit("-",1)[0]
L=defaultdict(lambda: dict(fill=[],walk=0,settle=None,exitf=[],firstfill=None))
for f in LOGS:
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        ts=e.get("ts_epoch")
        if ts is None or ts<PRIOR[0]: continue
        tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}
        if not tk: continue
        d=L[tk]
        if ev in ("entry_filled","completion_fill"):
            d["fill"].append((ts,D.get("fill_price")))
            if d["firstfill"] is None: d["firstfill"]=ts
        elif ev=="v4_move_repost": d["walk"]+=1
        elif ev=="settled": d["settle"]=(D.get("settle"),D.get("pnl_dollars"))
        elif ev=="exit_filled": d["exitf"].append((ts,D.get("pnl_dollars")))
def filled(tk): return len(L[tk]["fill"])>0
def fpx(tk): return L[tk]["fill"][0][1] if L[tk]["fill"] else None
events=defaultdict(set)
for tk in L:
    if filled(tk): events[evkey(tk)].add(tk)

pop=[]
for ek,ls in events.items():
    fc=[tk for tk in ls if filled(tk)]
    if len(fc)!=2: continue
    a,b=fc; comb=fpx(a)+fpx(b)
    if comb>=100: continue                 # BOUHAR-class = combined <100
    walked = (L[a]["walk"]>0 or L[b]["walk"]>0)
    if not walked: continue                # walked completions only
    ff=min(L[a]["firstfill"],L[b]["firstfill"])
    box = "PRIOR" if PRIOR[0]<=ff<PRIOR[1] else ("CURRENT" if CURRENT[0]<=ff<CURRENT[1] else "?")
    realized=sum(x for x in (L[a]["settle"][1] if L[a]["settle"] else None, L[b]["settle"][1] if L[b]["settle"] else None) if x is not None)
    nsettled=sum(1 for tk in fc if L[tk]["settle"] and L[tk]["settle"][1] is not None)
    exited=any(L[tk]["exitf"] for tk in fc)
    pop.append(dict(event=ek,cat=cat(ek+"-X"),box=box,combined=comb,locked_edge=100-comb,
                    realized=realized,nsettled=nsettled,exited=exited,le97=(comb<=97)))

print(f"=== P5 CORE — BOUHAR-class (walked completions <100) ===")
print(f"population: {len(pop)} pairs")
print("by box:",Counter(p["box"] for p in pop))
print("by cat:",Counter(p["cat"] for p in pop))
if pop:
    combs=sorted(p["combined"] for p in pop)
    print(f"[sizing] combined dist: min {combs[0]} med {int(st.median(combs))} max {combs[-1]} | <=97: {sum(p['le97'] for p in pop)}/{len(pop)}")
    print(f"[ribbon? my interp] sum locked-edge (100-combined) = {sum(p['locked_edge'] for p in pop)}c = ${sum(p['locked_edge'] for p in pop)/100.0:.2f} theoretical lock")
    fully=[p for p in pop if p['nsettled']==2]
    print(f"[net P&L] pairs both-legs-settled: {len(fully)}; realized on them = ${sum(p['realized'] for p in fully):.2f}")
    print(f"          all-pairs realized-so-far (partial settle) = ${sum(p['realized'] for p in pop):.2f} ({sum(p['nsettled'] for p in pop)}/{2*len(pop)} legs settled)")
    print(f"[exit-reach] pairs with an early exit_filled: {sum(1 for p in pop if p['exited'])}/{len(pop)}")
    print("\nper-pair:")
    for p in sorted(pop,key=lambda x:x['combined']):
        print(f"  {p['event'][-30:]:30s} {p['cat']:9s} {p['box']:7s} comb={p['combined']:3d} edge={p['locked_edge']:2d} realized=${p['realized']:+.2f} settled={p['nsettled']}/2 exit={p['exited']}")
json.dump(pop, open("/root/shadow_p4/p5_population.json","w"), default=str)
print("\nwrote /root/shadow_p4/p5_population.json")
