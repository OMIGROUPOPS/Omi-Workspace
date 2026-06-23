#!/usr/bin/env python3
"""READ-ONLY: fix net_direction (open=first-in-span, close=last-in-span, NA if empty) + add
latch_diagnosis {latch, A_producer_missed, B1_should_have_latched, B2_benign_no_start}. Writes FIXED CSV."""
import os,time,base64,json,urllib.request,glob,gzip,datetime,csv,statistics,hashlib
from pathlib import Path
HERE=Path("/root/Omi-Workspace/arb-executor"); BASE="https://api.elections.kalshi.com"
DOCS=HERE/"docs/analysis/premarket_dynamics_v1"
for ln in (HERE/".env").read_text().splitlines():
    if "=" in ln and not ln.startswith("#"): k,v=ln.split("=",1); os.environ.setdefault(k.strip(),v.strip().strip('"'))
API=os.environ["KALSHI_API_KEY"]
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
PK=serialization.load_pem_private_key((HERE/"kalshi.pem").read_bytes(),password=None,backend=default_backend())
def sign(ts,m,p): return base64.b64encode(PK.sign(f"{ts}{m}{p}".encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())).decode()
def kget(path):
    ts=str(int(time.time()*1000)); h={"KALSHI-ACCESS-KEY":API,"KALSHI-ACCESS-SIGNATURE":sign(ts,"GET",path.split("?")[0]),"KALSHI-ACCESS-TIMESTAMP":ts}
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(BASE+path,headers=h),timeout=30).read())
    except: return {}
def etstr(ep): return datetime.datetime.fromtimestamp(ep-4*3600,tz=datetime.timezone.utc).strftime("%H:%M:%S")
def iso2ep(s):
    try: return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
    except: return None
def logts2ep(ts):
    import re; m=re.match(r'(\d{4})-(\d\d)-(\d\d) (\d+):(\d\d):(\d\d) (AM|PM)',ts)
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
LOG=HERE/"logs/live_v3_20260622.jsonl"
sched={}; real={}; names={}; ourpath={}
for line in open(LOG):
    if not any(s in line for s in ('schedule_match','match_live_detected','v4_place','order_placed','entry_filled')): continue
    try: d=json.loads(line)
    except: continue
    e=d.get("event"); det=d.get("details",{}); tk=d.get("ticker","")
    if e=="schedule_match":
        ev=det.get("event")
        if ev and det.get("start_time"): sched[ev]=iso2ep(det["start_time"]); names[ev]={"p1":det.get("p1"),"p2":det.get("p2")}
    elif e=="match_live_detected":
        ev=det.get("event") or (tk.rsplit("-",1)[0] if tk else None)
        if ev and ev not in real: real[ev]=logts2ep(d["ts"])
    elif e in ("v4_place","order_placed","entry_filled") and "-" in tk:
        p=ourpath.setdefault(tk,{"src":None,"path":[],"fill":None})
        if e=="v4_place": p["src"]=det.get("reference_source") or det.get("anchor_src")
        elif e=="order_placed" and det.get("action")=="buy": p["path"].append(det.get("price"))
        elif e=="entry_filled": p["fill"]=det.get("fill_price")
REAL_SET=set(real)
# settlements: event -> (result, settled_ts)
setl={}; cur=None
for _ in range(60):
    r=kget("/trade-api/v2/portfolio/settlements?limit=200"+(f"&cursor={cur}" if cur else ""))
    for s in r.get("settlements",[]):
        ev=s.get("event_ticker"); res=s.get("market_result"); st=s.get("settled_time")
        if ev: setl.setdefault(ev,(res,st))
    cur=r.get("cursor")
    if not cur: break
depth={}
for f in sorted(glob.glob(str(HERE/"data/durable/depth_recorder/depth_20260622_*.jsonl.gz"))):
    with gzip.open(f,"rt") as fh:
        for line in fh:
            if "26JUN22" not in line: continue
            try: d=json.loads(line)
            except: continue
            tk=d.get("ticker","")
            if "-26JUN22" not in tk: continue
            depth.setdefault(tk,[]).append((d["ts_epoch"],d.get("bid"),d.get("ask")))
for tk in depth: depth[tk].sort()
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
def first_in(series,lo,hi):
    for t,x in series:
        if lo<=t<=hi and x is not None: return x
    return None
def last_in(series,lo,hi):
    v=None
    for t,x in series:
        if lo<=t<=hi and x is not None: v=x
    return v
def asof(series,ep,lo):  # last <= ep, else first in [lo,ep] window fallback
    v=None
    for t,x in series:
        if t<=ep and x is not None: v=x
    return v
def band(series,lo,hi):
    seg=[x for t,x in series if lo<=t<=hi and x is not None]
    return (min(seg),max(seg),max(seg)-min(seg)) if seg else (None,None,None)
def ndir(o,c):
    if o is None or c is None: return "NA"
    return 1 if c>o else (-1 if c<o else 0)
ANCHOR={"KXATPMATCH-26JUN22CRAROD-ROD":"Jurij Rodionov","KXATPMATCH-26JUN22CRAROD-CRA":"Oliver Crawford"}
def nm(tk):
    if tk in ANCHOR: return ANCHOR[tk]
    ev=tk.rsplit("-",1)[0]; sd=tk.rsplit("-",1)[1]; d=names.get(ev,{})
    for p in (d.get("p1"),d.get("p2")):
        if p and p.split()[-1][:3].upper()==sd.upper(): return p
    return sd+"?"
# original CSV (for real_start_source -> bucket A detection)
orig={}
for row in csv.DictReader(open("/tmp/today_bands.csv")):
    orig[(row["player"],row["match"])]=row["real_start_source"]
rows=[]; items=sorted(depth)
for i,tk in enumerate(items):
    ev=tk.rsplit("-",1)[0]; sd=tk.rsplit("-",1)[1]
    sc=sched.get(ev)
    if sc is None: continue
    w1=sc-14400.0; rs=real.get(ev); rsrc="latch" if rs else "scheduled_fallback"
    if rs is None: rs=sc
    dd=[(t,b,a) for (t,b,a) in depth[tk] if w1<=t<=rs]
    bbs=[(t,b) for t,b,a in dd if b is not None]; bas=[(t,a) for t,b,a in dd if a is not None]
    tr=trades(tk,w1,rs); lts=[(t,p) for t,p,q,s in tr if p is not None]
    if not lts and not bbs: continue
    matchname=ev.split("-",1)[1] if "-" in ev else ev
    out=dict(category=cat_of(tk),player=nm(tk),match=matchname,is_anchor=("YES" if tk in ANCHOR else ""),
             window1_open_ET=etstr(w1),scheduled_ET=etstr(sc),realstart_ET=etstr(rs),real_start_source=rsrc)
    for lab,series in [("bid",bbs),("ask",bas),("last",lts)]:
        mn,mx,bw=band(series,w1,rs); v0=first_in(series,w1,rs); vs=asof(series,sc,w1) or v0; vr=last_in(series,w1,rs)
        _,_,prew=band(series,w1,sc); _,_,corrw=band(series,sc,rs)
        wmi=(round(corrw/bw,3) if (bw and corrw is not None) else (0.0 if bw==0 else ""))
        out.update({f"{lab}_min":mn,f"{lab}_max":mx,f"{lab}_band_width":bw,f"{lab}_at_window1":v0,
            f"{lab}_at_scheduled":vs,f"{lab}_at_realstart":vr,f"{lab}_precorridor_width":prew,
            f"{lab}_corridor_width":corrw,f"{lab}_net_direction":ndir(v0,vr),f"{lab}_where_motion_corridorfrac":wmi})
    out["taker_buy_vol"]=sum(q for t,p,q,s in tr if s=="buy"); out["taker_sell_vol"]=sum(q for t,p,q,s in tr if s=="sell")
    op=ourpath.get(tk)
    out["our_bid_path"]=(f"{op['src'] or '?'}:"+"->".join(str(x) for x in op['path']) if (op and op['path']) else (op['src'] if op else "")) or ""
    out["our_fill_cent"]=op["fill"] if (op and op["fill"] is not None) else ""
    # latch_diagnosis
    if ev in REAL_SET:
        origsrc=orig.get((out["player"],matchname))
        out["latch_diagnosis"]="latch" if origsrc=="latch" else "A_producer_missed"
    else:
        res,st=setl.get(ev,(None,None))
        started = (res in ("yes","no")) and st  # settled with a real win/loss + timestamp
        out["latch_diagnosis"]="B1_should_have_latched" if started else "B2_benign_no_start"
    rows.append(out)
    if i%40==0: print(f"  ...{i}/{len(items)}",flush=True)
cols=["category","player","match","is_anchor","window1_open_ET","scheduled_ET","realstart_ET","real_start_source","latch_diagnosis",
 "bid_min","bid_max","bid_band_width","bid_at_window1","bid_at_scheduled","bid_at_realstart","bid_precorridor_width","bid_corridor_width","bid_net_direction","bid_where_motion_corridorfrac",
 "ask_min","ask_max","ask_band_width","ask_at_window1","ask_at_scheduled","ask_at_realstart","ask_precorridor_width","ask_corridor_width","ask_net_direction","ask_where_motion_corridorfrac",
 "last_min","last_max","last_band_width","last_at_window1","last_at_scheduled","last_at_realstart","last_precorridor_width","last_corridor_width","last_net_direction","last_where_motion_corridorfrac",
 "taker_buy_vol","taker_sell_vol","our_bid_path","our_fill_cent"]
outp=DOCS/"today_bands_FIXED_2026-06-22.csv"
with open(outp,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in rows]
sha=hashlib.sha256(open(outp,"rb").read()).hexdigest()
from collections import Counter
print("\n================ FIXED SUMMARY ================")
# Rodionov sanity
rod=next((r for r in rows if r["player"]=="Jurij Rodionov"),None)
print(f"[SANITY] Jurij Rodionov last_at_window1={rod['last_at_window1']} last_at_realstart={rod['last_at_realstart']} last_net_direction={rod['last_net_direction']}  (MUST be +1)")
print("last_net_direction slate split:",dict(Counter(r["last_net_direction"] for r in rows)))
print("bid_net_direction slate split:",dict(Counter(r["bid_net_direction"] for r in rows)))
print("latch_diagnosis counts:",dict(Counter(r["latch_diagnosis"] for r in rows)))
lat=Counter(r["latch_diagnosis"] for r in rows)
B1=lat["B1_should_have_latched"]; A=lat["A_producer_missed"]; fb=sum(v for k,v in lat.items() if k.startswith(("A_","B")))
verdict = ("PRODUCER bug dominates (A) -> fix analysis only" if A>=B1 else
           "LIVE bug indicated (B1 dominates fallback) -> latch genuinely not firing on real matches")
print(f"\nVERDICT: fallback legs split A={A} B1={B1} B2={lat['B2_benign_no_start']} -> {verdict}")
print(f"\nCSV: {outp}\nsha256: {sha}\nrows: {len(rows)}")
