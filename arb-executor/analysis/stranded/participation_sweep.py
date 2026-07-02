#!/usr/bin/env python3
# LIVE PARTICIPATION SWEEP (read-only). Every tracked tennis event with scheduled/occurrence start in the
# next 12h: category | T-minus | resting bids per leg (price,size) or NONE | if NONE the blocking reason.
# Flags IN-WINDOW events (start <= 4h) with no resting bid on one/both legs = a live BROTIA.
import json, glob, time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
LOGDIR="/root/Omi-Workspace/arb-executor/logs"
ET=timezone(timedelta(hours=-4))
NOW=time.time()
H12=NOW+12*3600
WINDOW_SEC=4*3600   # entry window ~T-4h (in-window = start within 4h)
def cat(t):
    for p,c in (("KXATPCHALLENGERMATCH","ATP_CHALL"),("KXWTACHALLENGERMATCH","WTA_CHALL"),("KXATPMATCH","ATP_MAIN"),("KXWTAMATCH","WTA_MAIN"),("KXITFWMATCH","ITF_W"),("KXITFMATCH","ITF_M")):
        if t.startswith(p): return c
    return "?"
def leg(t): return t.rsplit("-",1)[1] if "-" in t else t
def ev(t): return t.rsplit("-",1)[0]
def piso(s):
    if not s: return None
    for f in ("%Y-%m-%dT%H:%M:%S%z","%Y-%m-%dT%H:%M%z","%Y-%m-%dT%H:%M:%SZ","%Y-%m-%dT%H:%MZ"):
        try:
            d=datetime.strptime(s,f)
            if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
            return d.timestamp()
        except: pass
    return None
def tmfmt(sec):
    sign="-" if sec>=0 else "+"; sec=abs(int(sec)); h=sec//3600; m=(sec%3600)//60
    return f"T{sign}{h}h{m:02d}m"

start={}        # event -> scheduled start epoch (latest wins)
occ={}          # event -> kalshi occurrence epoch
processed=set() # events dropped (match_already_started)
skipreason={}   # event -> latest skip reason
players={}
# per-leg order lifecycle -> current resting BUY bid
resting={}      # ticker -> (price,count,oid) or None
filled=set()    # tickers with an entry fill

# read this-boot jsonl(s) for July (current + prior boot, latest start wins)
files=sorted(glob.glob(LOGDIR+"/live_v3_2026070*.jsonl"))
for f in files:
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        evn=e.get("event"); D=e.get("details",{}) or {}; tk=e.get("ticker","")
        if evn in ("schedule_match","schedule_corrected"):
            k=D.get("event"); s=piso(D.get("start_time") or D.get("new_start"))
            if k and s: start[k]=s
        elif evn=="kalshi_occ_observe":
            k=D.get("event"); s=piso(D.get("occurrence_datetime"))
            if k and s: occ[k]=s
        elif evn=="kalshi_occ_delta":
            k=D.get("event"); s=piso(D.get("kalshi_occurrence"))
            if k and s: occ[k]=s
        elif evn=="skipped":
            k=D.get("event") or (ev(tk) if tk else None)
            if k:
                skipreason[k]=D.get("reason","")
                if D.get("reason")=="match_already_started": processed.add(k)
        elif evn=="order_placed" and tk:
            if D.get("action")=="buy":
                resting[tk]=(D.get("price"),D.get("count"),D.get("order_id"))
        elif evn=="order_cancelled" and tk:
            oid=D.get("order_id")
            if tk in resting and resting[tk] and resting[tk][2]==oid: resting[tk]=None
        elif evn in ("entry_filled","completion_fill") and tk:
            filled.add(tk); resting[tk]=None

# candidate events = have a start (sched or occ) in [now, now+12h]
cands=[]
for k in set(list(start)+list(occ)):
    s=start.get(k, occ.get(k)); src="sched" if k in start else "occ"
    if s is None: continue
    if NOW-600 <= s <= H12:   # allow 10min grace on the past edge
        cands.append((s,k,src))
cands.sort()

def legs_of(k):
    # infer the two leg tickers from resting/filled keys or leave generic
    ls=[t for t in set(list(resting)+list(filled)) if ev(t)==k]
    return ls

print(f"=== LIVE PARTICIPATION SWEEP {datetime.fromtimestamp(NOW,ET):%Y-%m-%d %H:%M ET} | next 12h | {len(cands)} tracked events ===")
print(f"{'cat':9} {'T-minus':9} {'event':26} {'bids (leg:price x size)':34} {'block (if NONE)'}")
inwin_miss=[]
for s,k,src in cands:
    c=cat(k+"-X"); tm=tmfmt(s-NOW); evshort=k.split('-',1)[1] if '-' in k else k
    ls=legs_of(k)
    bidstr=[]
    have_bid=False
    for t in sorted(ls):
        r=resting.get(t)
        if r and r[0] is not None:
            bidstr.append(f"{leg(t)}:{r[0]}x{r[1]}"); have_bid=True
        elif t in filled:
            bidstr.append(f"{leg(t)}:FILLED")
    bids = ", ".join(bidstr) if bidstr else "NONE"
    block=""
    if not have_bid and "FILLED" not in bids:
        if k in processed: block="PROCESSED"
        elif skipreason.get(k): block=skipreason[k]
        elif not ls: block="never posted (no order/leg)"
        else: block="no resting bid"
    inwin = (s-NOW) <= WINDOW_SEC
    flag = "  <== IN-WINDOW, NO BID (live BROTIA)" if (inwin and not have_bid and "FILLED" not in bids) else ("  in-window" if inwin else "")
    print(f"{c:9} {tm:9} {evshort:26} {bids:34} {block}{flag}")
    if inwin and not have_bid and "FILLED" not in bids:
        inwin_miss.append((c,evshort,block))

print(f"\n=== IN-WINDOW SILENT MISSES (live BROTIAs): {len(inwin_miss)} ===")
bycat=defaultdict(int)
for c,e,b in inwin_miss: bycat[c]+=1
for c,n in sorted(bycat.items(),key=lambda x:-x[1]): print(f"  {c}: {n}")
for c,e,b in inwin_miss: print(f"   {c:9} {e:26} block={b}")
