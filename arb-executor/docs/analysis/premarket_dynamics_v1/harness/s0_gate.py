#!/usr/bin/env python3
"""OMQS harness Stage 1 -- S0 CORRECTNESS GATE (spec v2 sec 8). READ-ONLY.
Replay the bot's ACTUAL entry placements (Jun 19-22 logs) through the queue-adjusted fill model and
require set-equality vs the bot's own entry_filled stream, BOTH directions (missed AND spurious halt),
<=100ms, exact price, per leg type.

CLOCK FIX (built in): the ground-truth fill timestamp is the EXCHANGE TRADE ts, NOT the bot's
entry_filled booking ts (which lags by WS-detect+process, often >100ms). Both the bot-fill set and the
replay-fill set are keyed to the exchange trade that realized the fill. On existing tape the trade feed
is API-backfilled (granularity bounded); the definitive <=100ms run is tomorrow vs the WS capture --
but the gate LOGIC and the CLOCK REFERENCE are correct now."""
import os,time,base64,json,urllib.request,glob,gzip,datetime,re,collections,sys
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
DAYS=["20260619","20260620","20260621","20260622"]
QTY=5; TICK=0.100  # 100ms
def legtype(refsrc,play):
    if refsrc=="staircase": return "staircase"
    if refsrc=="join_bid": return "join_bid"
    p=play or ""
    if "engagement" in p: return "engagement"
    if "fallback_maker" in p: return "fallback_maker"
    if "miss_fallback" in p: return "miss_fallback"
    if "complete_cross" in p or (refsrc=="" and "cross" in p): return "complete_cross"
    return "other"
# ---- per-day: placements (walk) + actual fills + leg type ----
def load_day(day):
    lf=HERE/f"logs/live_v3_{day}.jsonl"
    place=collections.defaultdict(list); fill={}; refsrc={}; play={}; ccross=set()
    if not lf.exists(): return None
    for line in open(lf):
        if not any(x in line for x in ('order_placed','v4_place','entry_filled','complete_cross')): continue
        try: d=json.loads(line)
        except: continue
        e=d.get("event"); det=d.get("details",{}); tk=d.get("ticker","")
        if "-" not in tk: continue
        if e=="v4_place": refsrc.setdefault(tk,det.get("reference_source") or det.get("anchor_src") or "")
        elif e=="order_placed" and det.get("action")=="buy": place[tk].append((logts2ep(d["ts"]),det.get("price")))
        elif e=="entry_filled":
            fill[tk]=(logts2ep(d["ts"]),det.get("fill_price"),det.get("qty") or QTY); play[tk]=det.get("play_type")
            if det.get("source")=="complete_cross": ccross.add(tk)
    return place,fill,refsrc,play,ccross
# ---- depth index (depth_recorder per-level bids), per day for placed legs ----
def depth_for(day, tickers):
    dep=collections.defaultdict(list)
    for f in sorted(glob.glob(str(HERE/f"data/durable/depth_recorder/depth_{day}_*.jsonl.gz"))):
        with gzip.open(f,"rt") as fh:
            for line in fh:
                if "-26JUN" not in line: continue
                try: d=json.loads(line)
                except: continue
                tk=d.get("ticker","")
                if tk not in tickers: continue
                dep[tk].append((d["ts_epoch"], {int(p):int(s) for p,s in (d.get("bids") or [])}))
    for tk in dep: dep[tk].sort()
    return dep
def queue_at(dep,tk,price,ts):
    rows=dep.get(tk,[]); v=0
    for t,bids in rows:
        if t<=ts: v=bids.get(price,0)
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
def walk_segments(pl):
    """[(price, t_start, t_end)] from the order_placed walk."""
    pl=sorted(p for p in pl if p[0] is not None and p[1] is not None)
    segs=[]
    for i,(t,p) in enumerate(pl):
        end=pl[i+1][0] if i+1<len(pl) else 9e18
        segs.append((p,t,end))
    return segs

print("================ S0 CORRECTNESS GATE (queue-adjusted; clock=exchange-trade-ts) ================",flush=True)
gate_green=True; total_missed=0; total_spurious=0; total_time=0; total_price=0
for day in DAYS:
    ld=load_day(day)
    if not ld: continue
    place,fill,refsrc,play,ccross=ld
    placed=set(place)|set(fill)
    dep=depth_for(day,placed)
    bot=[]; replay=[]; bytype=collections.Counter(); diffs=[]
    for tk in sorted(placed):
        lt=legtype(refsrc.get(tk,""),play.get(tk))
        if tk in ccross: lt="complete_cross"
        bytype[lt]+=1
        segs=walk_segments(place.get(tk,[]))
        lo=segs[0][1] if segs else (fill[tk][0]-14400 if tk in fill else None)
        if lo is None: continue
        hi=(fill[tk][0]+5 if tk in fill else (segs[-1][2] if segs and segs[-1][2]<9e18 else lo+18000))
        if hi>9e17: hi=lo+18000
        tr=trades(tk,lo-300,hi)
        # --- map bot ACTUAL fill -> exchange trade ts ---
        if tk in fill:
            fts,fp,q=fill[tk]
            cand=[t for t in tr if t[3]=="sell" and t[1] is not None and fp is not None and t[1]<=fp and t[0]<=fts+0.5]
            ex=min(cand,key=lambda t:abs(t[0]-fts)) if cand else None
            ex_ts=ex[0] if ex else fts   # fall back to booking ts if no trade mapped (flagged)
            bot.append((tk,lt,round(ex_ts,3),fp,"mapped" if ex else "NO_TRADE_MATCH"))
        # --- replay queue-adjusted over the actual walk ---
        rfill=None
        for (P,t0,t1) in segs:
            qa=queue_at(dep,tk,P,t0); cum=0
            for (te,px,qy,sd) in tr:
                if te<t0 or te>=t1: continue
                if sd=="sell" and px is not None and px<=P:
                    cum+=qy
                    if cum>qa+QTY: rfill=(P,te); break
            if rfill: break
        if rfill: replay.append((tk,lt,round(rfill[1],3),rfill[0]))
    # ---- set-equality both directions (per day) ----
    botkey={(b[0],b[3]):b for b in bot}        # (leg, price) -> bot fill
    repkey={(r[0],r[3]):r for r in replay}
    missed=[]; spurious=[]; timed=[]; priced=[]
    for k,b in botkey.items():
        r=repkey.get(k)
        if not r: missed.append(b)
        elif abs(r[2]-b[2])>TICK: timed.append((b,r))
    for k,r in repkey.items():
        if k not in botkey: spurious.append(r)
    # price mismatches: a bot fill leg present in replay at a different price
    botleg=collections.defaultdict(list); repleg=collections.defaultdict(list)
    for b in bot: botleg[b[0]].append(b)
    for r in replay: repleg[r[0]].append(r)
    for leg in botleg:
        bp={b[3] for b in botleg[leg]}; rp={r[3] for r in repleg.get(leg,[])}
        if repleg.get(leg) and bp!=rp: priced.append((leg,sorted(bp),sorted(rp)))
    green = not missed and not spurious and not timed
    if not green: gate_green=False
    total_missed+=len(missed); total_spurious+=len(spurious); total_time+=len(timed); total_price+=len(priced)
    print(f"\n--- {day} --- leg types placed: {dict(bytype)}")
    print(f"  bot actual fills: {len(bot)} (exchange-ts mapped: {sum(1 for b in bot if b[4]=='mapped')}, no-trade-match: {sum(1 for b in bot if b[4]=='NO_TRADE_MATCH')})")
    print(f"  replay fills (queue-adjusted): {len(replay)}")
    print(f"  >> MISSED (bot filled, replay didn't): {len(missed)} | SPURIOUS (replay filled, bot didn't): {len(spurious)} | TIMING>100ms: {len(timed)} | PRICE-mismatch: {len(priced)}  -> {'GREEN' if green else 'HALT'}")
    for b in missed[:6]: print(f"     MISSED  {b[0].rsplit('-',1)[1]:<6} {b[1]:<14} @{b[3]}c exch_ts={datetime.datetime.utcfromtimestamp(b[2]).strftime('%H:%M:%S')} ({b[4]})")
    for r in spurious[:6]: print(f"     SPURIOUS {r[0].rsplit('-',1)[1]:<6} {r[1]:<14} @{r[3]}c ts={datetime.datetime.utcfromtimestamp(r[2]).strftime('%H:%M:%S')}")
    for (b,r) in timed[:4]: print(f"     TIMING  {b[0].rsplit('-',1)[1]:<6} bot_exch_ts {datetime.datetime.utcfromtimestamp(b[2]).strftime('%H:%M:%S')} vs replay {datetime.datetime.utcfromtimestamp(r[2]).strftime('%H:%M:%S')} (dt={r[2]-b[2]:+.2f}s)")
print(f"\n================ GATE RESULT ================")
print(f"TOTAL: missed={total_missed} spurious={total_spurious} timing>100ms={total_time} price={total_price}")
print("GATE:", "GREEN -- proceed to S1-S5" if gate_green else "HALT -- fill model not set-equal to bot fills; NO stratagem scores")
