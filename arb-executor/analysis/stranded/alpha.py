import json, os, csv, glob, gzip, statistics as st
from datetime import datetime, timezone, timedelta
from collections import defaultdict

BASE="/root/Omi-Workspace/arb-executor"
TICK=BASE+"/analysis/premarket_ticks"; TR=BASE+"/analysis/trades"; LOGDIR=BASE+"/logs"
EDT=timezone(timedelta(hours=-4))
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None

d=json.load(open("/tmp/stranded_91.json"))
evs=[r for r in d if os.path.exists(TICK+"/"+r["missed"]+".csv") and os.path.exists(TR+"/"+r["missed"]+".csv")]
missed_tk={r["missed"] for r in evs}; sib_tk={r["kept"] for r in evs}
allwant=missed_tk|sib_tk
print(f"alpha set: {len(evs)} events (covered + trades). missed legs={len(missed_tk)}")

# ---- parse logs: our order lifecycle on the missed legs + sibling trades already in trade tape ----
placed=defaultdict(list)   # ticker -> [(ts, order_id, price)]
cancelled={}               # order_id -> ts
legcancel=defaultdict(list) # ticker -> [ts]  (leg-level resting cancels)
target=defaultdict(list)   # ticker -> [target_bid]
logs=sorted(glob.glob(LOGDIR+"/live_v3_2026062*.jsonl")+glob.glob(LOGDIR+"/live_v3_20260630.jsonl"))
oid_ticker={}
for f in logs:
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        # cheap prefilter
        if not any(tk in line for tk in ()):
            pass
        try: e=json.loads(line)
        except: continue
        tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}; ts=e.get("ts_epoch")
        if ev=="order_placed" and tk in missed_tk and D.get("action")=="buy" and D.get("side")=="yes":
            oid=D.get("order_id"); placed[tk].append((ts,oid,D.get("price"))); oid_ticker[oid]=tk
        elif ev=="v4_place" and tk in missed_tk:
            if D.get("target_bid") is not None: target[tk].append(D["target_bid"])
        elif ev=="order_cancelled":
            oid=D.get("order_id")
            if oid: cancelled[oid]=ts
        elif ev in ("match_live_resting_cancel","v4_resting_cancel","orphan_buy_cancelled") and tk in missed_tk:
            legcancel[tk].append(ts)

def bid_intervals(tk):
    # list of (start,end,price) resting intervals for our buy orders
    iv=[]
    lc=sorted(legcancel[tk])
    for (ts,oid,price) in placed[tk]:
        if ts is None or price is None: continue
        end=cancelled.get(oid)
        # if not explicitly cancelled, resting until next leg-cancel after ts, else +2h
        if end is None:
            nxt=[c for c in lc if c>=ts]
            end=nxt[0] if nxt else ts+7200
        iv.append((ts,end,price))
    return iv

def active_bid(iv, t):
    return max([p for (s,e,p) in iv if s<=t<=e], default=None)

def last_pulled(iv, t, p):
    # did we have a bid >= p that ended (cancel) at or before t (and not resting now)?
    ended=[(e,pr) for (s,e,pr) in iv if e<=t and pr>=p]
    return bool(ended)

def load_ticks(tk):
    rows=[]
    for r in csv.DictReader(open(TICK+"/"+tk+".csv")):
        e=ptape(r["ts_et"]);
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        rows.append(dict(t=e,bid1=gi("bid_1"),ask1=gi("ask_1"),
            bdep=gi("bid_depth_5"),adep=gi("ask_depth_5"),mid=r.get("mid"),last=gi("last_trade")))
    rows.sort(key=lambda x:x["t"]); return rows

def load_trades(tk):
    rows=[]
    for r in csv.reader(open(TR+"/"+tk+".csv")):
        if not r or r[0]=="ts_et": continue
        e=ptape(r[0])
        if e is None: continue
        try: p=int(float(r[2])); c=int(float(r[3]))
        except: continue
        side=r[4] if len(r)>4 else ""
        rows.append((e,p,c,side))
    rows.sort(); return rows

# sibling trade times (for sibling-trade signal)
sib_trades={}
for r in evs:
    st_tk=r["kept"]
    sib_trades[r["missed"]]=[t for (t,p,c,s) in (load_trades(st_tk) if os.path.exists(TR+"/"+st_tk+".csv") else [])]

def window_dur(ticks, tau, p):
    # contiguous run of bid1<=p containing tau
    idx=[i for i,x in enumerate(ticks) if x["t"]<=tau]
    if not idx: return 0.0
    i=idx[-1]
    if ticks[i]["bid1"]>p and ticks[i]["bid1"]!=0:
        # tau tick already above; use nearest small window
        return 0.0
    lo=i
    while lo-1>=0 and (ticks[lo-1]["bid1"]<=p or ticks[lo-1]["bid1"]==0): lo-=1
    hi=i
    while hi+1<len(ticks) and (ticks[hi+1]["bid1"]<=p or ticks[hi+1]["bid1"]==0): hi+=1
    return ticks[hi]["t"]-ticks[lo]["t"]

def sig_before(ticks, tau, win=5.0):
    # book signals in [tau-win, tau)
    pre=[x for x in ticks if tau-win<=x["t"]<tau]
    if len(pre)<2: return {}
    d_bdep=pre[-1]["bdep"]-pre[0]["bdep"]
    d_adep=pre[-1]["adep"]-pre[0]["adep"]
    qv=sum(1 for a,b in zip(pre,pre[1:]) if a["bid1"]!=b["bid1"] or a["ask1"]!=b["ask1"])
    return dict(depth_pull=d_bdep<0, ask_thin=d_adep<0, quote_vel=qv>=2)

CLASSES=["PULLED","TOO_DEEP","BEHIND_WALL","NEVER_LAID"]
cnt=defaultdict(int); dol=defaultdict(float)
ledger=[]; windows=[]; sig_pos=defaultdict(int); sig_tot=0; sib_lead=0
latency_gaps=[]

for r in evs:
    tk=r["missed"]; iv=bid_intervals(tk); ticks=load_ticks(tk); trades=load_trades(tk)
    gun=r["gun_cancel_ts"] or (ticks[-1]["t"] if ticks else None)
    ref=max([p for (_,_,p) in iv]+target[tk]+[0])   # our reference bid level
    # inter-repost latency proxy
    pts=sorted(s for (s,_,_) in [(x[0],0,0) for x in placed[tk]])
    latency_gaps+=[b-a for a,b in zip(pts,pts[1:]) if 0<b-a<120]
    caught=0.0  # lots attributed on this leg (cap 5)
    for (tau,p,c,side) in trades:
        if gun and tau>=gun: continue           # premarket only
        if side!="no": continue                 # catchable = sell-into-bid
        if p>ref: continue                       # at/below our reference level
        q=active_bid(iv,tau)
        if q is None:
            cls="PULLED" if last_pulled(iv,tau,p) else "NEVER_LAID"
        elif q>=p: cls="BEHIND_WALL"
        else: cls="TOO_DEEP"
        lots=min(c, max(0,5-caught));
        if lots<=0:
            # still log class exposure but no incremental $
            pass
        val=(100-p)/100.0*min(c,5)   # missed-fill value (winner pays 100), per-print proxy
        cnt[cls]+=1; dol[cls]+=val; caught+=lots
        wd=window_dur(ticks,tau,p); windows.append(wd)
        sg=sig_before(ticks,tau); sig_tot+=1
        for k,v in sg.items():
            if v: sig_pos[k]+=1
        # sibling trade in prior 5s?
        if any(tau-5<=stt<tau for stt in sib_trades.get(tk,[])): sib_lead+=1
        ledger.append(dict(event=r["event"],leg=tk,ts=round(tau,2),price=p,count=c,
            our_bid=q,ref=ref,cls=cls,win_s=round(wd,1),
            depth_pull=sg.get("depth_pull",False),ask_thin=sg.get("ask_thin",False),
            quote_vel=sg.get("quote_vel",False)))

json.dump(ledger, open("/tmp/alpha_ledger.json","w"), indent=0)
print(f"\ncatchable missed prints: {len(ledger)}  (across {len(evs)} legs)")
print("=== ERROR-CLASS SPLIT (count | $-weight = missed-fill value) ===")
tot=sum(cnt.values()); totd=sum(dol.values())
for cl in CLASSES:
    print(f"  {cl:11s} {cnt[cl]:4d} ({100*cnt[cl]/tot if tot else 0:4.1f}%)  ${dol[cl]:7.2f} ({100*dol[cl]/totd if totd else 0:4.1f}%)")
print(f"  {'TOTAL':11s} {tot:4d}          ${totd:7.2f}")
print(f"\nPULLED-then-touched share: {100*cnt['PULLED']/tot if tot else 0:.1f}% (reconcile vs cancel-timing 89%)")
if windows:
    ws=sorted(windows)
    def pc(q): return ws[min(len(ws)-1,int(q*len(ws)))]
    print(f"\n=== CATCHABILITY WINDOW (level-available duration, s) ===")
    print(f"  P50={pc(.5):.1f}  P75={pc(.75):.1f}  P90={pc(.9):.1f}  max={max(ws):.1f}")
lat=st.median(latency_gaps) if latency_gaps else None
print(f"  our repost-latency proxy (median inter-repost gap): {lat:.1f}s" if lat else "  latency proxy: n/a")
print(f"\n=== LEADING SIGNALS (share of prints with signal in prior 5s) — small-N, N={sig_tot} ===")
for k in ("depth_pull","ask_thin","quote_vel"):
    print(f"  {k:11s}: {100*sig_pos[k]/sig_tot if sig_tot else 0:.1f}%")
print(f"  sibling_trade(prior5s): {100*sib_lead/sig_tot if sig_tot else 0:.1f}%")
print("wrote /tmp/alpha_ledger.json")
