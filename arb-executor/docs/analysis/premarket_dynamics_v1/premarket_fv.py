#!/usr/bin/env python3
"""READ-ONLY definitive premarket check, Jun 22 2026 ET. FV = TRIPLE (close bid, close ask, close last),
each = median over final 5 min before scheduled start: bid/ask from depth_recorder, last from Kalshi
trades. above-FV flagged PRIMARILY on close BID (we rest a bid, fill vs sell-flow); close spread shown
so within-spread fills aren't miscounted as chases. Universe = full Kalshi tennis slate (4 series)."""
import os,time,base64,json,urllib.request,datetime,csv,collections,hashlib,re,glob,gzip,statistics
from pathlib import Path
HERE=Path("/root/Omi-Workspace/arb-executor"); BASE="https://api.elections.kalshi.com"; DOCS=HERE/"docs/analysis/premarket_dynamics_v1"
for ln in (HERE/".env").read_text().splitlines():
    if "=" in ln and not ln.startswith("#"): k,v=ln.split("=",1); os.environ.setdefault(k.strip(),v.strip().strip('"'))
API=os.environ["KALSHI_API_KEY"]
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
PK=serialization.load_pem_private_key((HERE/"kalshi.pem").read_bytes(),password=None,backend=default_backend())
def sign(ts,m,p): return base64.b64encode(PK.sign(f"{ts}{m}{p}".encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())).decode()
def get(path):
    ts=str(int(time.time()*1000)); h={"KALSHI-ACCESS-KEY":API,"KALSHI-ACCESS-SIGNATURE":sign(ts,"GET",path.split("?")[0]),"KALSHI-ACCESS-TIMESTAMP":ts}
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(BASE+path,headers=h),timeout=30).read())
    except Exception as e: return {"_err":str(e)}
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
def cat_of(tk):
    if tk.startswith("KXATPCHALLENGERMATCH"): return "ATP_CHALL"
    if tk.startswith("KXWTACHALLENGERMATCH"): return "WTA_CHALL"
    if tk.startswith("KXATPMATCH"): return "ATP_MAIN"
    if tk.startswith("KXWTAMATCH"): return "WTA_MAIN"
SERIES=["KXATPMATCH","KXWTAMATCH","KXATPCHALLENGERMATCH","KXWTACHALLENGERMATCH"]
slate={}
for s in SERIES:
    cur=None
    for _ in range(40):
        r=get(f"/trade-api/v2/events?series_ticker={s}&with_nested_markets=true&limit=200&status=settled,open,closed,unopened"+(f"&cursor={cur}" if cur else ""))
        for ev in r.get("events",[]):
            et=ev.get("event_ticker","")
            if "26JUN22" not in et: continue
            legs={}
            for mk in ev.get("markets",[]):
                mt=mk.get("ticker","")
                if "-" in mt: legs[mt.rsplit("-",1)[1]]={"ticker":mt,"last_price":mk.get("last_price"),"name":mk.get("yes_sub_title") or mt.rsplit("-",1)[1]}
            if legs: slate[et]={"cat":cat_of(et),"legs":legs}
        cur=r.get("cursor")
        if not cur: break
print(f"full slate: {len(slate)} events, {sum(len(v['legs']) for v in slate.values())} legs",flush=True)
LOG=HERE/"logs/live_v3_20260622.jsonl"
sched={}; names={}; ourbidpath=collections.defaultdict(list); fills={}
for line in open(LOG):
    if not any(x in line for x in ('schedule_match','order_placed','entry_filled')): continue
    try: d=json.loads(line)
    except: continue
    e=d.get("event"); det=d.get("details",{}); tk=d.get("ticker","")
    if e=="schedule_match":
        ev=det.get("event")
        if ev and det.get("start_time"): sched.setdefault(ev,iso2ep(det["start_time"])); names.setdefault(ev,{"p1":det.get("p1"),"p2":det.get("p2")})
    elif e=="order_placed" and det.get("action")=="buy" and "-" in tk: ourbidpath[tk].append((logts2ep(d["ts"]),det.get("price")))
    elif e=="entry_filled" and "-" in tk: fills[tk]=(logts2ep(d["ts"]),det.get("fill_price"))
ANCHOR={"KXATPMATCH-26JUN22CRAROD-ROD":"Jurij Rodionov","KXATPMATCH-26JUN22CRAROD-CRA":"Oliver Crawford"}
def nm(tk):
    if tk in ANCHOR: return ANCHOR[tk]
    ev=tk.rsplit("-",1)[0]; sd=tk.rsplit("-",1)[1]; dn=names.get(ev,{})
    for p in (dn.get("p1"),dn.get("p2")):
        if p and any(t[:3].upper()==sd.upper() for t in p.split() if t): return p
    return slate.get(ev,{}).get("legs",{}).get(sd,{}).get("name") or (sd+"?")
touched=set(ourbidpath)|set(fills)
# depth for touched legs (bid/ask)
depth=collections.defaultdict(list)
for f in sorted(glob.glob(str(HERE/"data/durable/depth_recorder/depth_20260622_*.jsonl.gz"))):
    with gzip.open(f,"rt") as fh:
        for line in fh:
            if "26JUN22" not in line: continue
            try: d=json.loads(line)
            except: continue
            tk=d.get("ticker","")
            if tk in touched: depth[tk].append((d["ts_epoch"],d.get("bid"),d.get("ask")))
for tk in depth: depth[tk].sort()
def med_depth(tk,lo,hi,idx):
    vals=[r[idx] for r in depth.get(tk,[]) if lo<=r[0]<=hi and r[idx] is not None]
    if vals: return round(statistics.median(vals))
    pre=[r[idx] for r in depth.get(tk,[]) if r[0]<=hi and r[idx] is not None]  # fallback last<=sched
    return round(pre[-1]) if pre else None
def trades(tk,lo,hi):
    out=[]; cur=None
    for _ in range(12):
        r=get(f"/trade-api/v2/markets/trades?ticker={tk}&min_ts={int(lo)}&max_ts={int(hi)}&limit=1000"+(f"&cursor={cur}" if cur else ""))
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
rows=[]
for ev,info in slate.items():
    sc=sched.get(ev)
    for sd,leg in info["legs"].items():
        tk=leg["ticker"]; posted=tk in ourbidpath; filled=tk in fills
        fc=fills[tk][1] if filled else None; fts=fills[tk][0] if filled else None
        bucket=("PREMARKET" if (filled and sc and fts<sc) else ("POST" if filled and sc else ("NO_SCHED" if filled else "")))
        our_bid=ourbidpath[tk][-1][1] if posted else None
        fvb=fva=fvl=None; fvflag=""; direction=""; cspread=None
        if (posted or filled) and sc is not None:
            lo,hi=sc-300,sc
            fvb=med_depth(tk,lo,hi,1); fva=med_depth(tk,lo,hi,2)
            tr=trades(tk,lo,hi); seg=[p for t,p,q,s in tr if p is not None]
            if len(seg)>=2: fvl=round(statistics.median(seg)); fvflag="5min_median"
            else:
                tr2=trades(tk,sc-14400,sc); seg2=[p for t,p,q,s in tr2 if p is not None]
                fvl=seg2[-1] if seg2 else None; fvflag="fallback_last_at_sched" if seg2 else "no_trades"
            tr2=trades(tk,sc-14400,sc); seg2=[p for t,p,q,s in tr2 if p is not None]
            if len(seg2)>=2: direction="firm" if seg2[-1]>seg2[0] else ("fade" if seg2[-1]<seg2[0] else "flat")
            if fvb is not None and fva is not None: cspread=fva-fvb
        fmb=(fc-fvb) if (filled and fvb is not None) else None
        fma=(fc-fva) if (filled and fva is not None) else None
        fml=(fc-fvl) if (filled and fvl is not None) else None
        leg_status=""
        if posted and not filled and sc is not None and our_bid is not None:
            t0=ourbidpath[tk][0][0]; tr3=trades(tk,t0,sc)
            reached=any(p is not None and s=="sell" and p<=our_bid for t,p,q,s in tr3)
            leg_status="bid_unfilled_starved(no_sellflow<=bid)" if not reached else "bid_unfilled_sellflow_reached"
        elif filled: leg_status="filled"
        elif posted: leg_status="bid_unfilled_no_sched"
        else: leg_status="not_posted"
        obvc = (our_bid-fvb) if (our_bid is not None and fvb is not None) else None
        rows.append(dict(event=ev,player=nm(tk),category=info["cat"],side=sd,posted=posted,filled=filled,bucket=bucket,
            our_bid=our_bid,fill_cent=fc,fv_close_bid=fvb,fv_close_ask=fva,fv_close_last=fvl,close_spread=cspread,fv_flag=fvflag,
            fill_minus_fv_bid=fmb,fill_minus_fv_ask=fma,fill_minus_fv_last=fml,our_bid_minus_close_bid=obvc,
            direction=direction,leg_status=leg_status,last_price=leg["last_price"]))
    if len(rows)%80==0: print(f"  ...{len(rows)} legs",flush=True)
outp=DOCS/"premarket_fv_check_2026-06-22.csv"
cols=["event","player","category","side","posted","filled","bucket","our_bid","fill_cent","fv_close_bid","fv_close_ask","fv_close_last","close_spread","fv_flag","fill_minus_fv_bid","fill_minus_fv_ask","fill_minus_fv_last","our_bid_minus_close_bid","direction","leg_status","last_price"]
with open(outp,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in rows]
sha=hashlib.sha256(open(outp,"rb").read()).hexdigest()
C=collections.Counter
fl=[r for r in rows if r["filled"]]; prem=[r for r in fl if r["bucket"]=="PREMARKET"]; post=[r for r in fl if r["bucket"]=="POST"]
print("\n================ A) FILL LOCATION + COUNT ================")
print(f"total fills(slate-joined): {len(fl)} | PREMARKET {len(prem)} | POST {len(post)} | NO_SCHED {sum(1 for r in fl if r['bucket']=='NO_SCHED')}")
biu=[r for r in rows if r["posted"] and not r["filled"]]
print(f"posted-but-unfilled: {len(biu)} -> {dict(C(r['leg_status'] for r in biu))}")
print("\n================ B) ABOVE-FV (primary = close BID; spread shown) ================")
def rep(group,lab):
    g=[r for r in group if r["fill_minus_fv_bid"] is not None]
    if not g: print(f"  {lab}: no FV-joined fills"); return
    ab_bid=[r for r in g if r["fill_minus_fv_bid"]>0]
    within=[r for r in ab_bid if r["fill_minus_fv_ask"] is not None and r["fill_cent"]<=r["fv_close_ask"]]
    above_ask=[r for r in ab_bid if r["fill_minus_fv_ask"] is not None and r["fill_cent"]>r["fv_close_ask"]]
    prem_b=[r["fill_minus_fv_bid"] for r in ab_bid]
    print(f"  {lab}: n={len(g)} | above close-BID {len(ab_bid)} ({100*len(ab_bid)/len(g):.0f}%)  premium(vs bid) median={statistics.median(prem_b) if prem_b else 0:.0f}c max={max(prem_b) if prem_b else 0}c")
    print(f"     of those above-bid: WITHIN spread(<=close ask) {len(within)} | ABOVE close-ask (true chase) {len(above_ask)} | median close spread={statistics.median([r['close_spread'] for r in g if r['close_spread'] is not None]) if any(r['close_spread'] is not None for r in g) else '?'}c")
    ab_last=[r for r in g if r['fill_minus_fv_last'] is not None and r['fill_minus_fv_last']>0]
    print(f"     (vs close-LAST: above {len(ab_last)} ({100*len(ab_last)/len(g):.0f}%))")
    if lab.startswith("PREMARKET") and ab_bid: print(f"     premarket above-bid direction: {dict(C(r['direction'] for r in ab_bid))}")
rep(prem,"PREMARKET fills"); rep(post,"POST fills")
print("\n================ C) IGNORED GAMES ================")
eo={ev:sum(1 for sd,lg in info["legs"].items() if lg["ticker"] in ourbidpath) for ev,info in slate.items()}
ign=[e for e in slate if eo[e]==0]; one=[e for e in slate if eo[e]==1]; both=[e for e in slate if eo[e]>=2]
print(f"slate events {len(slate)} | both-legs {len(both)} | ONE-leg {len(one)} | IGNORED(0) {len(ign)}")
print("  ignored by cat:",dict(C(slate[e]['cat'] for e in ign)))
def band(e):
    lp=[lg['last_price'] for lg in slate[e]['legs'].values() if lg['last_price']];
    return (f"{(max(lp)//10)*10}-{(max(lp)//10)*10+9}c" if lp else "no_price")
print("  ignored by favorite band:",dict(C(band(e) for e in ign)))
print("  one-leg by cat:",dict(C(slate[e]['cat'] for e in one)))
print("\n================ CROSS-CHECK ================")
print(f"slate-joined fills {len(fl)} ; entry_filled today 176 ; unmatched {176-len(fl)} (26JUN20 carryover / non-slate)")
print(f"\nCSV: {outp}\nsha256: {sha}\nrows: {len(rows)}")
