#!/usr/bin/env python3
"""OMQS S0 gate v2 (spec v2 sec 8) -- COMPLETE per-mechanism fill model. READ-ONLY.
Placement universe = legs with a real order_placed(buy) (adopted/reconcile/other EXCLUDED).
Mechanisms modelled the way each actually fills:
  MAKER (engagement-join / staircase / resting_maker / fallback_maker): a resting bid at its walked
    price fills when cumulative taker-NO sell-flow at <=price exceeds queue-ahead+size (queue-adjusted).
    Walk = order_placed(buy) + v4_move_repost + v4_fallback_maker_clamp (so the ask-1 clamp price is in).
  TAKER (miss_fallback / complete_cross): immediate lift -- fills at best_ask at the cross moment,
    NOT a maker waiting for sell-flow.
Clock = EXCHANGE TRADE ts on both sides (maker fill = taker-NO sell at our bid; taker fill = taker-YES
lift at the ask). Set-equality both directions, <=100ms, exact price, per day, per leg type.
Residual granularity failures on 6s/backfilled tape are the data limit; definitive run tomorrow on WS."""
import os,time,base64,json,urllib.request,glob,gzip,datetime,re,collections
from pathlib import Path
HERE=Path("/root/Omi-Workspace/arb-executor"); BASE="https://api.elections.kalshi.com"
for ln in (HERE/".env").read_text().splitlines():
    if "=" in ln and not ln.startswith("#"): k,v=ln.split("=",1); os.environ.setdefault(k.strip(),v.strip().strip('"'))
API=os.environ["KALSHI_API_KEY"]
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
PK=serialization.load_pem_private_key((HERE/"kalshi.pem").read_bytes(),password=None,backend=default_backend())
def sign(t,m,p): return base64.b64encode(PK.sign(f"{t}{m}{p}".encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())).decode()
def kget(path):
    t=str(int(time.time()*1000)); h={"KALSHI-ACCESS-KEY":API,"KALSHI-ACCESS-SIGNATURE":sign(t,"GET",path.split("?")[0]),"KALSHI-ACCESS-TIMESTAMP":t}
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(BASE+path,headers=h),timeout=30).read())
    except: return {}
def iso2ep(s):
    try: return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
    except: return None
def logts2ep(ts):
    m=re.match(r'(\d{4})-(\d\d)-(\d\d) (\d+):(\d\d):(\d\d) (AM|PM)',ts)
    if not m: return None
    y,mo,d,h,mi,s=int(m[1]),int(m[2]),int(m[3]),int(m[4]),int(m[5]),int(m[6])
    if m[7]=="PM" and h!=12:h+=12
    if m[7]=="AM" and h==12:h=0
    return datetime.datetime(y,mo,d,h,mi,s,tzinfo=datetime.timezone.utc).timestamp()+4*3600
def hhmmss(ep): return datetime.datetime.fromtimestamp(ep,datetime.timezone.utc).strftime("%H:%M:%S")
DAYS=["20260619","20260620","20260621","20260622"]; QTY=5; TOL=0.100
def mechanism(play,source):
    if source=="complete_cross": return "complete_cross","taker"
    p=play or ""
    if "miss_fallback" in p: return "miss_fallback","taker"
    if "engagement" in p: return "engagement","maker"
    if "fallback_maker" in p: return "fallback_maker","maker"
    if "resting_maker" in p: return "resting_maker","maker"
    if "reconcil" in p or "adopt" in p: return "reconcile","EXCLUDE"
    return (p or "other"),"EXCLUDE"
def load_day(day):
    lf=HERE/f"logs/live_v3_{day}.jsonl"
    if not lf.exists(): return None
    walk=collections.defaultdict(list); placed=set(); fill={}; cross_ts={}; refsrc={}
    for line in open(lf):
        if not any(x in line for x in ('order_placed','v4_move_repost','v4_fallback_maker_clamp','entry_filled','complete_cross','v4_place')): continue
        try: d=json.loads(line)
        except: continue
        e=d.get("event"); det=d.get("details",{}); tk=d.get("ticker","")
        if "-" not in tk: continue
        ep=logts2ep(d["ts"])
        if e=="v4_place": refsrc.setdefault(tk,det.get("reference_source") or "")
        elif e=="order_placed" and det.get("action")=="buy":
            placed.add(tk); walk[tk].append((ep,det.get("price")))
        elif e=="v4_move_repost" and det.get("new_target") is not None: walk[tk].append((ep,det.get("new_target")))
        elif e=="v4_fallback_maker_clamp" and det.get("ask1_price") is not None: walk[tk].append((ep,det.get("ask1_price")))
        elif e=="entry_filled":
            fill[tk]=(ep,det.get("fill_price"),det.get("qty") or QTY,det.get("play_type"),det.get("source"))
        elif e=="complete_cross" and det.get("event"):
            # complete_cross fires on the crossed leg; ticker carries the leg
            cross_ts[tk]=ep
    return walk,placed,fill,cross_ts,refsrc
def depth_for(day,tickers):
    dep=collections.defaultdict(list)
    for f in sorted(glob.glob(str(HERE/f"data/durable/depth_recorder/depth_{day}_*.jsonl.gz"))):
        with gzip.open(f,"rt") as fh:
            for line in fh:
                if "-26JUN" not in line: continue
                try: d=json.loads(line)
                except: continue
                tk=d.get("ticker","")
                if tk not in tickers: continue
                dep[tk].append((d["ts_epoch"],{int(p):int(s) for p,s in (d.get("bids") or [])},d.get("ask")))
    for tk in dep: dep[tk].sort()
    return dep
def queue_at(dep,tk,price,ts):
    v=0
    for t,bids,ask in dep.get(tk,[]):
        if t<=ts: v=bids.get(price,0)
        else: break
    return v
def ask_at(dep,tk,ts):
    v=None
    for t,bids,ask in dep.get(tk,[]):
        if t<=ts: v=ask
        else: break
    return v
def trades(tk,lo,hi):
    out=[]; cur=None
    for _ in range(15):
        r=kget(f"/trade-api/v2/markets/trades?ticker={tk}&min_ts={int(lo)}&max_ts={int(hi)}&limit=1000"+(f"&cursor={cur}" if cur else ""))
        out+=r.get("trades",[]); cur=r.get("cursor")
        if not cur: break
    ev=[]
    for t in out:
        te=iso2ep(t.get("created_time",""))
        if te is None: continue
        yp=t.get("yes_price_dollars"); px=round(float(yp)*100) if yp is not None else (100-round(float(t["no_price_dollars"])*100) if t.get("no_price_dollars") else None)
        side="buy" if t.get("taker_side")=="yes" else ("sell" if t.get("taker_side")=="no" else "?")
        ev.append((te,px,round(float(t.get("count_fp",0) or 0)),side))
    ev.sort(); return ev
def segments(w):
    w=sorted((t,p) for t,p in w if t is not None and p is not None)
    return [(p,t,(w[i+1][0] if i+1<len(w) else 9e18)) for i,(t,p) in enumerate(w)]

print("============== S0 GATE v2 (complete per-mechanism fill model; clock=exchange-trade-ts) ==============",flush=True)
gtot=collections.Counter(); green=True
for day in DAYS:
    ld=load_day(day)
    if not ld: continue
    walk,placed,fill,cross_ts,refsrc=ld
    dep=depth_for(day,placed)
    bot=[]; replay=[]; bytype=collections.Counter(); excluded=0
    for tk in sorted(placed):
        play=fill[tk][3] if tk in fill else None; src=fill[tk][4] if tk in fill else None
        lt,kind=mechanism(play,src) if tk in fill else ("unfilled_maker","maker")
        if kind=="EXCLUDE": excluded+=1; continue
        bytype[lt]+=1
        segs=segments(walk.get(tk,[]))
        if not segs: continue
        lo=segs[0][1]; hi=(fill[tk][0]+5 if tk in fill else segs[-1][1]+18000)
        tr=trades(tk,lo-300,hi if hi<9e17 else lo+18000)
        # ---- bot actual fill -> exchange trade (mechanism-aware) ----
        if tk in fill:
            fts,fp,q,_,_=fill[tk]
            if kind=="taker": cand=[t for t in tr if t[3]=="buy" and t[1]==fp and t[0]<=fts+0.5]
            else: cand=[t for t in tr if t[3]=="sell" and t[1] is not None and fp is not None and t[1]<=fp and t[0]<=fts+0.5]
            ex=min(cand,key=lambda t:abs(t[0]-fts)) if cand else None
            bot.append((tk,lt,round(ex[0] if ex else fts,3),fp,"mapped" if ex else "NOMATCH"))
        # ---- replay (per mechanism) ----
        rf=None
        if kind=="taker":
            ct=cross_ts.get(tk) or (segs[-1][1])   # cross moment
            a=ask_at(dep,tk,ct)
            # the lift = first taker-YES trade at/after cross moment
            lift=next((t for t in tr if t[3]=="buy" and t[0]>=ct-1),None)
            if lift: rf=(lift[1],lift[0])           # immediate fill at the lifted ask
            elif a is not None: rf=(a,ct)
        else:
            for (P,t0,t1) in segs:
                qa=queue_at(dep,tk,P,t0); cum=0
                for (te,px,qy,sd) in tr:
                    if te<t0 or te>=t1: continue
                    if sd=="sell" and px is not None and px<=P:
                        cum+=qy
                        if cum>qa+QTY: rf=(P,te); break
                if rf: break
        if rf: replay.append((tk,lt,round(rf[1],3),rf[0]))
    botk={(b[0],b[3]):b for b in bot}; repk={(r[0],r[3]):r for r in replay}
    missed=[b for k,b in botk.items() if k not in repk]
    spurious=[r for k,r in repk.items() if k not in botk]
    timed=[(botk[k],repk[k]) for k in botk if k in repk and abs(repk[k][2]-botk[k][2])>TOL]
    d_green = not missed and not spurious and not timed
    green = green and d_green
    gtot["missed"]+=len(missed); gtot["spurious"]+=len(spurious); gtot["timed"]+=len(timed)
    print(f"\n--- {day} --- placed(in-universe): {dict(bytype)} | excluded adopted/reconcile/other: {excluded}")
    print(f"  bot fills {len(bot)} (mapped {sum(1 for b in bot if b[4]=='mapped')}) | replay fills {len(replay)}")
    print(f"  >> MISSED {len(missed)} | SPURIOUS {len(spurious)} | TIMING>100ms {len(timed)} -> {'GREEN' if d_green else 'HALT'}")
    mm=collections.Counter(b[1] for b in missed); sm=collections.Counter(r[1] for r in spurious)
    if missed: print("     missed by type:",dict(mm))
    if spurious: print("     spurious by type:",dict(sm))
    for b in missed[:5]: print(f"       MISSED {b[0].rsplit('-',1)[1]:<6} {b[1]:<14} @{b[3]}c {hhmmss(b[2])} ({b[4]})")
    for (b,r) in timed[:3]: print(f"       TIMING {b[0].rsplit('-',1)[1]:<6} {b[1]:<14} bot {hhmmss(b[2])} vs replay {hhmmss(r[2])} dt={r[2]-b[2]:+.1f}s")
print(f"\n============== GATE v2 RESULT ==============")
print(f"TOTAL: missed={gtot['missed']} spurious={gtot['spurious']} timing>100ms={gtot['timed']}")
print("GATE:", "GREEN" if green else "HALT (residuals -> see by-type; data-limit vs model)")
