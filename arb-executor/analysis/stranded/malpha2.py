import json, os, csv, glob, gzip, math
from collections import defaultdict
BASE="/root/Omi-Workspace/arb-executor"; TR=BASE+"/analysis/trades"; LOGDIR=BASE+"/logs"
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(TR+"/"+tk+e): return TR+"/"+tk+e
    return None
def evkey(t): return t.rsplit("-",1)[0]
def taker_fee(a,q): p=a/100.0; return math.ceil(0.07*q*p*(1-p)*100)/100.0

placed={}; t20m=[]; filled_px={}; legcancel=defaultdict(list); det=set()
for f in sorted(glob.glob(LOGDIR+"/live_v3_2026062*.jsonl")+glob.glob(LOGDIR+"/live_v3_20260630.jsonl")):
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}; ts=e.get("ts_epoch")
        if ev=="order_placed" and D.get("action")=="buy" and D.get("side")=="yes" and D.get("order_id"):
            placed[D["order_id"]]=(tk,D.get("price"),ts)
        elif ev=="order_cancelled" and D.get("label")=="v4_t20m_fallback" and D.get("order_id"):
            t20m.append((D["order_id"],ts))
        elif ev=="entry_filled" and tk not in filled_px and D.get("fill_price") is not None: filled_px[tk]=D["fill_price"]
        elif ev in ("match_live_resting_cancel","v4_resting_cancel"): legcancel[tk].append(ts)
        elif ev=="ws_settled_pre_finalized" and D.get("market_status")=="determined": det.add(tk)

# group cancels by ticker
byticker=defaultdict(list)
for (oid,cts) in t20m:
    if oid in placed:
        tk,bid,pts=placed[oid]
        if bid is not None and cts is not None: byticker[tk].append((bid,cts))

tape_cache={}
def tape(tk):
    if tk in tape_cache: return tape_cache[tk]
    f=findf(tk); out=[]
    if f:
        for r in csv.reader(opent(f)):
            if not r or r[0]=="ts_et": continue
            try: p=int(float(r[2]))
            except: continue
            out.append((r[0],p,r[4] if len(r)>4 else ""))  # keep raw ts str; we only need order + price + side
    # we need epoch to window; but flow-through existence: any taker=no at p<=bid AFTER cancel.
    tape_cache[tk]=out; return out
# to window by time we need epoch; parse ts lazily via a monotonic index using the log cancel ts.
from datetime import datetime, timezone, timedelta
EDT=timezone(timedelta(hours=-4))
def pt(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None

QTY=5; PUB=-24.62
rows=[]; no_tape=0
for tk,cancels in byticker.items():
    f=findf(tk)
    if not f: no_tape+=len(cancels); continue
    trs=[(pt(s),p,side) for (s,p,side) in tape(tk)]
    trs=[x for x in trs if x[0] is not None]
    gun=min(legcancel[tk]) if legcancel[tk] else None
    for (bid,cts) in cancels:
        cap = gun if gun else cts+4*3600
        ft=None
        for (e,p,side) in trs:
            if e<=cts or e>=cap: continue
            if side=="no" and p<=bid: ft=p; break
        if not ft: continue
        ek=evkey(tk); sib=[filled_px[s] for s in filled_px if evkey(s)==ek and s!=tk]
        rows.append(dict(leg=tk,bid=bid,flow_px=ft,sib_filled=bool(sib),
                         sib_entry=(sib[0] if sib else None),
                         combined=(sib[0]+bid) if sib else None, det=tk in det))

n=len(rows); nsib=sum(1 for r in rows if r["sib_filled"])
print(f"M-alpha2 | v4_t20m_fallback flow-through cancels: {n} (doc=81; no-tape skipped {no_tape})")
print(f"  sibling-filled (completable): {nsib} (doc n=64)")
le97=le100=gt100=0; pnet=0.0
for r in rows:
    if not r["sib_filled"]: continue
    comb=r["combined"]; pnet+=(100-comb)/100.0*QTY - taker_fee(r["bid"],QTY)
    if comb<=97: le97+=1
    elif comb<=100: le100+=1
    else: gt100+=1
print(f"\n=== PAIR-FRAME (sibling-filled {nsib}, complete+hold-to-settle, winner-independent) ===")
print(f"  combined buckets: <=97:{le97}  98-100:{le100}  >100:{gt100}")
print(f"  PAIR-FRAME NET: ${pnet:+.2f}   published NAKED band-capped: ${PUB}")
print(f"  M2-cost DELTA (pair - naked): ${pnet-PUB:+.2f}")
print(f"  -> {'M2 NO LONGER PROTECTIVE under pair frame (fill+complete >= naked, within +$10/day gate)' if pnet>=-10 else 'M2 STILL PROTECTIVE under pair frame'}")
json.dump(rows, open("/tmp/malpha2_flips.json","w"), indent=0)
print("\n=== FLIP TABLE (sibling-filled, first 25) ===")
sh=0
for r in rows:
    if not r["sib_filled"]: continue
    flag="GOOD<=97" if r["combined"]<=97 else ("par" if r["combined"]<=100 else "OVER")
    print(f"  {r['leg'][-22:]:22s} bid={r['bid']:>2} sib={r['sib_entry']:>3} comb={r['combined']:>3} {flag} det={r['det']}")
    sh+=1
    if sh>=25: break
print("wrote /tmp/malpha2_flips.json")
