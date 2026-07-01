#!/usr/bin/env python3
# HALF B (READ-ONLY): clean-pair rate + failure breakdown, TRADED universe (we have fills only where we placed).
# 3 days of logs available (06-24/25/26); ITF excluded (see-not-trade). STARVE vs STRAND via book@gun.
import json,glob,collections,csv,datetime,os
TICK="/root/Omi-Workspace/arb-executor/analysis/premarket_ticks"
def cat(t):
    if t.startswith("KXATPCHALLENGERMATCH"):return "ATP_CHALL"
    if t.startswith("KXWTACHALLENGERMATCH"):return "WTA_CHALL"
    if t.startswith("KXATPMATCH"):return "ATP_MAIN"
    if t.startswith("KXWTAMATCH"):return "WTA_MAIN"
    if t.startswith("KXITF"):return "ITF"
    return "OTHER"
def ep(s):
    try:
        import datetime as D
        return D.datetime.strptime(s[0:10],"%Y-%m-%d").toordinal()*86400+(int(s[11:13])%12+(12 if s[20]=='P' else 0))*3600+int(s[14:16])*60+int(s[17:19])
    except: return None
rows=[]
for f in sorted(glob.glob("/root/Omi-Workspace/arb-executor/logs/live_v3_2026062[456].jsonl")):
    for l in open(f):
        try: rows.append(json.loads(l))
        except: pass
def ev(d):return d.get("event")
def D(d):return d.get("details",{})
# per-leg state
placed=collections.defaultdict(dict)   # leg -> {price,ts}  (last placed buy)
filled=collections.defaultdict(dict)   # leg -> {price,posted,ts}
startts={}                             # event -> start epoch
matchlive=set()
for d in rows:
    tk=d.get("ticker",""); e=tk.rsplit("-",1)[0] if tk else ""
    x=D(d); E=ev(d)
    if E=="order_placed" and x.get("action")=="buy":
        placed[tk]={"price":x.get("price"),"ts":d.get("ts_epoch")}
    elif E=="entry_filled":
        if tk not in filled: filled[tk]={"price":x.get("fill_price"),"posted":x.get("posted_price"),"ts":d.get("ts_epoch")}
    elif E=="match_live_resting_cancel": matchlive.add(e)
    # start time: several events carry epoch
    for key in ("start_ts","match_start_ts","event_start_ts"):
        if key in x and e and e not in startts:
            try: startts[e]=float(x[key])
            except: pass
# event -> legs (from placed + filled + any ticker seen)
evlegs=collections.defaultdict(set)
for tk in set(list(placed)+list(filled)):
    evlegs[tk.rsplit("-",1)[0]].add(tk)
# best_bid near gun from premarket_ticks (last valid row's bid_1)
def bestbid_gun(tk):
    p=os.path.join(TICK,tk+".csv")
    if not os.path.exists(p): return None
    last=None
    for r in csv.DictReader(open(p)):
        try: b=int(r["bid_1"] or 0)
        except: continue
        if b>0: last=b
    return last
CATS=["ATP_MAIN","WTA_MAIN","ATP_CHALL"]   # traded cats (WTA_CHALL=0 placed, ITF see-not-trade)
res=collections.defaultdict(lambda: collections.Counter())
strand_samples=[]
for e,legs in evlegs.items():
    c=cat(e+"-X")  # category from event prefix
    c=cat(list(legs)[0])
    if c not in CATS: continue
    res[c]["eligible"]+=1
    pl=[l for l in legs if l in placed]
    fi=[l for l in legs if l in filled]
    # CLEAN: both legs filled (2 legs filled)
    if len(fi)>=2:
        # bad-price check: combined fill > 100 (overround)
        fps=sorted(filled[l]["price"] for l in fi if filled[l]["price"] is not None)[:2]
        if len(fps)==2 and sum(fps)>100: res[c]["clean_but_badprice"]+=1
        else: res[c]["CLEAN"]+=1
        continue
    # non-clean: classify primary failure
    if len(legs)<2 or len(pl)<2:
        res[c]["one_leg_placed (orphan/single-eligible)"]+=1
        continue
    # both placed, <2 filled -> at least one starved/stranded
    starved=[l for l in pl if l not in filled]
    classified=False
    for l in starved:
        ob=placed[l].get("price"); bg=bestbid_gun(l)
        if ob is not None and bg is not None and bg>ob+1:
            res[c]["STRAND (best-bid moved above our bid)"]+=1
            if len(strand_samples)<12: strand_samples.append((l[-22:],f"ourbid{ob}",f"bestbid_gun{bg}",f"gap{bg-ob}"))
            classified=True; break
    if not classified:
        res[c]["STARVE (placed, at-touch, never filled)"]+=1

print("HALF B — clean-pair rate + failure breakdown (TRADED cats, 3 days 06-24..26; ITF excl see-not-trade)")
for c in CATS:
    r=res[c]; el=r["eligible"]
    print(f"\n=== {c}  (eligible games={el}) ===")
    if not el: continue
    clean=r["CLEAN"]
    print(f"  CLEAN-PAIR (both filled, combined<=100): {clean} ({100*clean//el}%)")
    for k in ["clean_but_badprice","STARVE (placed, at-touch, never filled)","STRAND (best-bid moved above our bid)","one_leg_placed (orphan/single-eligible)"]:
        if r[k]: print(f"    {k}: {r[k]}")
print("\n=== STRAND samples (Nick Hardt class: our bid stranded below moved best-bid at gun) ===")
for s in strand_samples: print("   ",s)
print("\nNOTE: clean = both legs entry_filled (pre-gun timing approximated; start_ts sparse in logs).")
print("STARVE vs STRAND split = the fix selector (starve=market-selection; strand=best-bid-aware follow).")
