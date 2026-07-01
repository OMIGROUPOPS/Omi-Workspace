import json, os, csv
from datetime import datetime, timezone, timedelta
BASE="/root/Omi-Workspace/arb-executor"; TR=BASE+"/analysis/trades"; TICK=BASE+"/analysis/premarket_ticks"
LOG=BASE+"/logs/live_v3_20260701.jsonl"
EDT=timezone(timedelta(hours=-4))
EV="KXITFWMATCH-26JUL01HUIAHN"; HUI=EV+"-HUI"; AHN=EV+"-AHN"
def et(ts): return datetime.fromtimestamp(ts,EDT).strftime("%H:%M:%S")
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None

# ---- (1) order timeline both legs ----
KEEP={"v4_place","order_placed","order_cancelled","v4_move_repost","entry_filled",
      "match_live_resting_cancel","v4_resting_cancel","would_skip_walled_post","skipped",
      "staircase_hold_place","fv_anchor_place","join_queue","orphan_buy_cancelled","liquid_repost_at_touch",
      "settled","ws_settled_pre_finalized","exit_filled","v4_exit_posted","completion_fill"}
tl=[]
for line in open(LOG,errors="replace"):
    if "HUIAHN" not in line: continue
    try: e=json.loads(line)
    except: continue
    tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}; ts=e.get("ts_epoch")
    if EV not in tk and D.get("event")!=EV: continue
    if ev not in KEEP: continue
    leg = "HUI" if tk.endswith("-HUI") else ("AHN" if tk.endswith("-AHN") else "?")
    tl.append((ts,leg,ev,D))
tl.sort(key=lambda x:x[0])
print("="*90); print("(1) ORDER TIMELINE — KXITFWMATCH-26JUL01HUIAHN  (Hui=dog, Ahn=held)"); print("="*90)
def fld(D,*ks):
    return " ".join(f"{k}={D[k]}" for k in ks if k in D and D[k] is not None)
for (ts,leg,ev,D) in tl:
    extra=fld(D,"price","count","target_bid","entry_mode","cell","current_ask","new_target","current_price",
              "fill_price","qty","play_type","label","reason","response_status","move_cents","runway_status","market_status","settle","settle_price","pnl_dollars")
    print(f"  {et(ts)} {leg:3s} {ev:26s} {extra}")

# ---- bid intervals for HUI ----
placed=[]; cancelled={}; legcancel=[]
for (ts,leg,ev,D) in tl:
    if leg!="HUI": continue
    if ev=="order_placed" and D.get("action")=="buy": placed.append((ts,D.get("order_id"),D.get("price")))
    elif ev=="order_cancelled" and D.get("order_id"): cancelled[D["order_id"]]=ts
    elif ev in ("match_live_resting_cancel","v4_resting_cancel","orphan_buy_cancelled"): legcancel.append(ts)
iv=[]
for (ts,oid,pr) in placed:
    if ts is None or pr is None: continue
    end=cancelled.get(oid) or next((c for c in sorted(legcancel) if c>=ts),None) or ts+7200
    iv.append((ts,end,pr))
def active(t): return max([p for (s,e,p) in iv if s<=t<=e],default=None)
def pulled(t,p): return any(e<=t and pr>=p for (s,e,pr) in iv)
ref=max([p for (_,_,p) in iv]+[D.get("target_bid",0) for (_,leg,ev,D) in tl if leg=="HUI" and ev=="v4_place"]+[0])

def loadtr(tk):
    f=TR+"/"+tk+".csv"
    if not os.path.exists(f): return []
    out=[]
    for r in csv.reader(open(f)):
        if not r or r[0]=="ts_et": continue
        e=ptape(r[0])
        if e is None: continue
        try: out.append((e,int(float(r[2])),int(float(r[3])),r[4] if len(r)>4 else ""))
        except: continue
    return sorted(out)
def loadtick(tk):
    f=TICK+"/"+tk+".csv"
    if not os.path.exists(f): return []
    out=[]
    for r in csv.DictReader(open(f)):
        e=ptape(r["ts_et"])
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        out.append((e,gi("bid_1"),gi("bid_1_sz"),gi("ask_1"),gi("ask_1_sz"),gi("last_trade")))
    return sorted(out)

hui_tr=loadtr(HUI)
# match-live gun proxy
gun=sorted(legcancel)[0] if legcancel else (hui_tr[-1][0] if hui_tr else None)
print("\n"+"="*90); print(f"(2) HUI DIVOTS — taker_side=no prints at <= {ref}c (our ref bid) during premarket; classify our bid state"); print("="*90)
print(f"  our HUI ref bid level = {ref}c ; gun(match-live) ~ {et(gun) if gun else '?'}")
print(f"  {'ts':8s} {'px':>3s} {'ct':>4s} {'ourBid':>6s} {'class':11s}")
cls_ct={}
for (ts,p,c,side) in hui_tr:
    if gun and ts>=gun: continue
    if side!="no" or p>ref+3: continue
    q=active(ts)
    if q is None: cls="PULLED" if pulled(ts,p) else "NEVER_LAID"
    elif q>=p: cls="BEHIND_WALL"
    else: cls="TOO_DEEP"
    cls_ct[cls]=cls_ct.get(cls,0)+1
    print(f"  {et(ts)} {p:>3} {c:>4} {str(q):>6s} {cls}")
print(f"  divot-class counts: {cls_ct}")
# catchable size in low-30s
low=[c for (ts,p,c,side) in hui_tr if side=='no' and p<=35 and (not gun or ts<gun)]
print(f"  catchable taker_no size @<=35c premarket: {sum(low)} contracts across {len(low)} prints (ITF thinness check)")

# ---- (3) AHN fill vs tape ----
print("\n"+"="*90); print("(3) AHN FILL vs tape"); print("="*90)
ahn_fill=[(ts,D) for (ts,leg,ev,D) in tl if leg=="AHN" and ev in ("entry_filled","completion_fill")]
ahn_tick=loadtick(AHN); ahn_tr=loadtr(AHN)
def tick_at(ticks,t):
    lo=None
    for row in ticks:
        if row[0]<=t: lo=row
        else: break
    return lo
for (ts,D) in ahn_fill:
    tk=tick_at(ahn_tick,ts)
    print(f"  AHN fill @ {et(ts)}  fill_price={D.get('fill_price')} qty={D.get('qty') or D.get('new_fills')} play_type={D.get('play_type')} kalshi={D.get('kalshi_status')}")
    if tk: print(f"    tape@fill: bid_1={tk[1]}({tk[2]}) ask_1={tk[3]}({tk[4]}) last_trade={tk[5]}")
if ahn_tr:
    prem=[(p) for (ts,p,c,s) in ahn_tr if not gun or ts<gun]
    if prem: print(f"  AHN premarket trade range: min={min(prem)} max={max(prem)} first={prem[0]} last={prem[-1]}  (n={len(prem)})")

# ---- (4) pair math ----
print("\n"+"="*90); print("(4) PAIR MATH"); print("="*90)
ahn_px=ahn_fill[0][1].get("fill_price") if ahn_fill else None
hui_catch=min([p for (ts,p,c,s) in hui_tr if s=='no' and (not gun or ts<gun)], default=None)
print(f"  AHN actual fill = {ahn_px}c (held naked)")
print(f"  best catchable HUI divot (taker_no premarket, lowest) = {hui_catch}c")
if ahn_px is not None and hui_catch is not None:
    comb=ahn_px+hui_catch
    print(f"  achievable combined = {ahn_px} + {hui_catch} = {comb}c  ->  {'GOOD <=97' if comb<=97 else ('par <=100' if comb<=100 else 'OVER 100')}")
print(f"  ACTUAL: one leg (AHN {ahn_px}c) naked, Hui NEVER filled.")
