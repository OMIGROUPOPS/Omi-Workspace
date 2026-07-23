import json, collections
N="/srv/omi-research/window1-20260722/normalized"
J="/mnt/omi-trading-data-nyc3/private-evidence/window1-20260722/joined"
ld=lambda p:[json.loads(l) for l in open(p)]
ev=ld(N+"/events.jsonl"); fills=ld(N+"/fills.jsonl"); orders=ld(N+"/orders.jsonl")
mm=ld(J+"/validation_mismatch_ledger.jsonl")
print("D(events)=%d fills=%d orders=%d"%(len(ev),len(fills),len(orders)))
print("legs sample:",json.dumps(ev[0].get("legs"))[:220])
print("legs-per-event:",dict(collections.Counter(len(e.get("legs") or []) for e in ev)))
# map ticker -> event, leg tickers per event
def leg_tickers(e):
    L=e.get("legs")
    out=[]
    if isinstance(L,list):
        for x in L:
            if isinstance(x,str): out.append(x)
            elif isinstance(x,dict): out.append(x.get("ticker") or x.get("leg_ticker") or x.get("market_ticker"))
    return [t for t in out if t]
ev_legs={e["event_id"]:leg_tickers(e) for e in ev}
tk2ev={}
for e in ev:
    for t in leg_tickers(e): tk2ev[t]=e["event_id"]
# filled qty per leg-ticker (FILL = complete private fill receipt)
filled_qty=collections.Counter()
for f in fills:
    filled_qty[str(f.get("ticker"))]+= float(f.get("quantity") or 0)
# the 703 CENSORED set (accepted, unconfirmed) - by ticker/event
tgt_oid=set(str(r.get("order_id")) for r in mm if r.get("mismatch_type")=="accepted_order_missing_receipt")
o_by_oid={str(o.get("order_id")):o for o in orders if o.get("order_id")}
censored_legs=set()
for oid in tgt_oid:
    o=o_by_oid.get(oid)
    if o: censored_legs.add(str(o.get("ticker")))
# per-leg confirmed nonfill: leg has orders all terminal exchange_status in canceled/expired/rejected w/ 0 fills AND not censored
leg_orders=collections.defaultdict(list)
for o in orders:
    leg_orders[str(o.get("ticker"))].append(o)
def leg_status(tk):
    q=filled_qty.get(tk,0)
    if q>=5: return "FILL"
    if q>0: return "PARTIAL"
    if tk in censored_legs: return "CENSORED"
    os_=leg_orders.get(tk,[])
    if not os_: return "NOPLACE"  # confirmed nonfill: no placement
    # any accepted order without exchange_status (ambiguous) -> censored
    if any(o.get("accepted") is True and o.get("exchange_status") in (None,"") for o in os_): return "CENSORED"
    # all terminal canceled/expired/rejected -> confirmed nonfill
    if all(str(o.get("exchange_status") or "") in ("canceled","expired","rejected") for o in os_): return "NONFILL"
    return "CENSORED"
# per-game classification
gcls=collections.Counter(); games=[]
for e in ev:
    legs=ev_legs[e["event_id"]]
    st=[leg_status(t) for t in legs]
    fills_n=sum(1 for s in st if s=="FILL")
    if not legs: cls="NO_LEGS"
    elif fills_n>=2 and len(legs)>=2: cls="C_dual_capture"
    elif fills_n==1: cls="P_partial"
    elif any(s=="CENSORED" for s in st): cls="I_censored"
    elif all(s in ("NONFILL","NOPLACE") for s in st): cls="N_nonfill"
    else: cls="I_censored"
    gcls[cls]+=1
    games.append((e["event_id"],cls,st,legs))
print("=== GAME-LEVEL CENSUS (D=%d) ==="%len(ev))
for k in ("C_dual_capture","P_partial","N_nonfill","I_censored","NO_LEGS"):
    print("  %-16s : %d"%(k,gcls.get(k,0)))
C=gcls.get("C_dual_capture",0); Dn=len(ev); cens=gcls.get("I_censored",0)
# capture-rate bounds: lower = C/D (censored=non-capture); upper=(C+censored)/D
print("=== DUAL 5x5 CAPTURE RATE vs >=75%% objective ===")
print("  C=%d D=%d  lower=%.1f%% (censored non-capture)  upper=%.1f%% (censored all-capture)"%(C,Dn,100*C/Dn,100*(C+cens)/Dn))
# leg-level tally
legcls=collections.Counter()
for e in ev:
    for t in ev_legs[e["event_id"]]: legcls[leg_status(t)]+=1
print("=== LEG-LEVEL ===",dict(legcls))
# combined cost for captured games: sum of the two legs' avg fill price
def leg_avg_price(tk):
    fs=[f for f in fills if str(f.get("ticker"))==tk]
    if not fs: return None
    tq=sum(float(f.get("quantity") or 0) for f in fs)
    return sum(float(f.get("price_cents") or 0)*float(f.get("quantity") or 0) for f in fs)/tq if tq else None
combos=[]
for eid,cls,st,legs in games:
    if cls!="C_dual_capture": continue
    ps=[leg_avg_price(t) for t in legs]
    if all(p is not None for p in ps) and len(ps)>=2:
        combos.append((eid,ps[0],ps[1],ps[0]+ps[1]))
import statistics
if combos:
    cc=[c[3] for c in combos]
    under=sum(1 for x in cc if x<100)
    print("=== CAPTURED-GAME COMBINED COST (per-leg + combined, <100c check) ===")
    print("  captured priced games=%d  combined_cost: min=%.1f p50=%.1f max=%.1f  under_100c=%d/%d"%(len(cc),min(cc),statistics.median(cc),max(cc),under,len(cc)))
    print("  combined DELTA (100 - combined_cost): p50=%.1f  (negative-combined-delta games i.e. cost>100: %d)"%(100-statistics.median(cc),sum(1 for x in cc if x>100)))
