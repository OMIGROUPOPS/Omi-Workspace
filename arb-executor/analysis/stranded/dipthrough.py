#!/usr/bin/env python3
import json, gzip, glob, os
from collections import defaultdict
WS="/root/Omi-Workspace/arb-executor/data/durable/ws_depth_recorder"
stranded=json.load(open("/tmp/stranded_rolldowns.json"))
targets={s["ticker"] for s in stranded}
# build per-leg windows: list of (start_ts, end_ts, target, touch)
windows=defaultdict(list)
for s in stranded:
    rds=sorted(s["rolldowns"]); cx=s["cancel_ts"]
    for i,(ts,touch,nt) in enumerate(rds):
        end = rds[i+1][0] if i+1<len(rds) else (cx if cx else ts+7200)
        windows[s["ticker"]].append((ts,end,nt,touch))

# collect trades for target tickers from ws files (trade lines only)
# determine time span
allts=[w[0] for ws in windows.values() for w in ws]+[w[1] for ws in windows.values() for w in ws]
tmin,tmax=min(allts),max(allts)
trades=defaultdict(list)  # ticker -> [(ts, yes_price_cents, count, taker_side)]
files=sorted(glob.glob(f"{WS}/ws_*.jsonl.gz"))
for f in files:
    # quick mtime prefilter: file covers ~1hr; skip clearly-out-of-range by mtime
    mt=os.path.getmtime(f)
    if mt < tmin-200 or mt > tmax+7400: continue
    with gzip.open(f,"rt",errors="replace") as fh:
        for line in fh:
            if '"trade"' not in line: continue
            try: m=json.loads(line)["m"]
            except: continue
            if m.get("type")!="trade": continue
            msg=m["msg"]; tk=msg.get("market_ticker")
            if tk not in targets: continue
            yp=int(round(float(msg["yes_price_dollars"])*100))
            trades[tk].append((float(msg.get("ts_ms",0))/1000.0 or m.get("t"), yp, float(msg["count_fp"]), msg.get("taker_side")))

# per-leg: count taker_side==no volume in band (nt, touch] during each window
print("=== DIP-THROUGH COUNTERFACTUAL (would a touch-bid have filled?) ===")
print(f"{'event':16s} {'leg':4s} {'rolls':>5s} {'band':>10s}  no-flow@touch-band(shares)  verdict")
would_fill=0; total=0; partial=0
detail=[]
for s in stranded:
    tk=s["ticker"]; tr=trades.get(tk,[])
    miss_vol=0.0; band_lo=99; band_hi=0
    for (st,en,nt,touch) in windows[tk]:
        band_lo=min(band_lo,nt+1); band_hi=max(band_hi,touch)
        for (ts,yp,ct,ts_side) in tr:
            if st<=ts<=en and ts_side=="no" and nt < yp <= touch:
                miss_vol+=ct
    total+=1
    verdict = "WOULD-FILL(>=5)" if miss_vol>=5 else ("partial(<5)" if miss_vol>0 else "no dip-through (ran away)")
    if miss_vol>=5: would_fill+=1
    elif miss_vol>0: partial+=1
    ev=tk.rsplit('-',1)[0].split('-',1)[1]; leg=tk.rsplit('-',1)[1]
    print(f"{ev:16s} {leg:4s} {len(windows[tk]):5d} {f'({band_lo-1},{band_hi}]':>10s}  {miss_vol:8.0f}                  {verdict}")
    detail.append((ev,leg,miss_vol,verdict,len(tr)))
print(f"\nSTRANDED legs: {total}")
print(f"  WOULD have filled at touch (>=5 no-flow in band): {would_fill}")
print(f"  partial dip-through (1-4 shares):                 {partial}")
print(f"  ran away (no touch-band flow, directional):       {total-would_fill-partial}")
