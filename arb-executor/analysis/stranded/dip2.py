#!/usr/bin/env python3
import json
from collections import defaultdict
stranded=json.load(open("/tmp/stranded_rolldowns.json"))
# load extracted trades
trades=defaultdict(list)
n=0
for line in open("/tmp/ttrades.jsonl",errors="replace"):
    try: m=json.loads(line)["m"]
    except: continue
    if m.get("type")!="trade": continue
    msg=m["msg"]; tk=msg.get("market_ticker"); n+=1
    yp=int(round(float(msg["yes_price_dollars"])*100))
    ts=float(msg.get("ts_ms",0))/1000.0
    trades[tk].append((ts,yp,float(msg["count_fp"]),msg.get("taker_side")))
print(f"parsed {n} trades across {len(trades)} tickers\n")

windows=defaultdict(list)
for s in stranded:
    rds=sorted(s["rolldowns"]); cx=s["cancel_ts"]
    for i,(ts,touch,nt) in enumerate(rds):
        end=rds[i+1][0] if i+1<len(rds) else (cx if cx else ts+7200)
        windows[s["ticker"]].append((ts,end,nt,touch))

def cat(t):
    if t.startswith("KXATPCHALLENGERMATCH"): return "CHALL"
    if t.startswith("KXITFWMATCH"): return "ITF-W"
    if t.startswith("KXITFMATCH"): return "ITF-M"
print(f"{'event':16s} {'leg':4s} {'cat':6s} roll  band      missflow  totflow@<=touch  verdict")
wf=part=ran=0; bycat=defaultdict(lambda:[0,0,0])
for s in stranded:
    tk=s["ticker"]; tr=trades.get(tk,[]); c=cat(tk)
    miss=0.0; atbelow=0.0; lo=99; hi=0
    for (st,en,nt,touch) in windows[tk]:
        lo=min(lo,nt+1); hi=max(hi,touch)
        for (ts,yp,ct,sd) in tr:
            if sd=="no" and st<=ts<=en:
                if nt < yp <= touch: miss+=ct
                if yp <= touch: atbelow+=ct
    if miss>=5: v="WOULD-FILL(>=5)"; wf+=1; bycat[c][0]+=1
    elif miss>0: v="partial(1-4)"; part+=1; bycat[c][1]+=1
    else: v="ran-away(no touch flow)"; ran+=1; bycat[c][2]+=1
    ev=tk.rsplit('-',1)[0].split('-',1)[1]; leg=tk.rsplit('-',1)[1]
    print(f"{ev:16s} {leg:4s} {c:6s} {len(windows[tk]):4d}  ({lo-1},{hi}]  {miss:8.0f}  {atbelow:8.0f}        {v}")
print(f"\n=== of {len(stranded)} stranded rolled-down partner-legs ===")
print(f"  WOULD have filled at touch (>=5 no-flow in roll-band): {wf}")
print(f"  partial dip-through (1-4 shares):                      {part}")
print(f"  ran away / no touch-band flow (directional):           {ran}")
for c in ["CHALL","ITF-M","ITF-W"]:
    b=bycat[c]; print(f"    {c}: would-fill {b[0]}, partial {b[1]}, ran-away {b[2]}")
