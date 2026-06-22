#!/usr/bin/env python3
"""READ-ONLY: full-slate pre-game BAND table, Jun 22 2026 ET. Per leg, the literal per-tick range
(no buckets) of best_bid/best_ask/last_traded across T-4h -> real-start (volume-burst latch), with the
internal corridor (scheduled->real) split out. Writes CSV to a tracked docs path."""
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
def logts2ep(ts):  # '2026-06-22 02:00:07 AM ET'
    import re; m=re.match(r'(\d{4})-(\d\d)-(\d\d) (\d+):(\d\d):(\d\d) (AM|PM)',ts)
    if not m: return None
    y,mo,d,h,mi,s=int(m[1]),int(m[2]),int(m[3]),int(m[4]),int(m[5]),int(m[6])
    if m[7]=="PM" and h!=12:h+=12
    if m[7]=="AM" and h==12:h=0
    return datetime.datetime(y,mo,d,h,mi,s,tzinfo=datetime.timezone.utc).timestamp()+4*3600
LOG=HERE/"logs/live_v3_20260622.jsonl"
def cat_of(tk):
    if tk.startswith("KXATPCHALLENGERMATCH"): return "ATP_CHALL"
    if tk.startswith("KXWTACHALLENGERMATCH"): return "WTA_CHALL"
    if tk.startswith("KXATPMATCH"): return "ATP_MAIN"
    if tk.startswith("KXWTAMATCH"): return "WTA_MAIN"
# parse log: scheduled, real, names, our bid path
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
# depth per 26JUN22 leg
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
print(f"depth-covered 26JUN22 legs: {len(depth)}",flush=True)
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
def at(series,ep):  # last (ts<=ep) value
    v=None
    for t,x in series:
        if t<=ep: v=x
        else: break
    return v
def band(series,lo,hi):
    seg=[x for t,x in series if lo<=t<=hi and x is not None]
    return (min(seg),max(seg),max(seg)-min(seg)) if seg else (None,None,None)
ANCHOR={"KXATPMATCH-26JUN22CRAROD-ROD":"Jurij Rodionov","KXATPMATCH-26JUN22CRAROD-CRA":"Oliver Crawford"}
def nm(tk):
    if tk in ANCHOR: return ANCHOR[tk]
    ev=tk.rsplit("-",1)[0]; sd=tk.rsplit("-",1)[1]; d=names.get(ev,{})
    for p in (d.get("p1"),d.get("p2")):
        if p and p.split()[-1][:3].upper()==sd.upper(): return p
    return sd+"?"
rows=[]; items=sorted(depth)
for i,tk in enumerate(items):
    ev=tk.rsplit("-",1)[0]; sd=tk.rsplit("-",1)[1]
    sc=sched.get(ev)
    if sc is None: continue
    w1=sc-14400.0
    rs=real.get(ev); rsrc="latch" if rs else "scheduled_fallback"
    if rs is None: rs=sc
    dd=[(t,b,a) for (t,b,a) in depth[tk] if w1<=t<=rs]
    bbs=[(t,b) for t,b,a in dd if b is not None]; bas=[(t,a) for t,b,a in dd if a is not None]
    tr=trades(tk,w1,rs); lts=[(t,p) for t,p,q,s in tr if p is not None]
    if not lts and not bbs: continue   # leg didn't trade / no book in span
    out=dict(category=cat_of(tk),player=nm(tk),match=ev.split("-",1)[1] if "-" in ev else ev,
             window1_open_ET=etstr(w1),scheduled_ET=etstr(sc),realstart_ET=etstr(rs),real_start_source=rsrc,
             is_anchor=("YES" if tk in ANCHOR else ""))
    for lab,series in [("bid",bbs),("ask",bas),("last",lts)]:
        mn,mx,bw=band(series,w1,rs)
        v0=at(series,w1); vs=at(series,sc); vr=at(series,rs)
        _,_,prew=band(series,w1,sc); _,_,corrw=band(series,sc,rs)
        nd = 0 if (v0 is None or vr is None) else (1 if vr>v0 else (-1 if vr<v0 else 0))
        wmi = (corrw/bw) if (bw and corrw is not None) else (0.0 if bw==0 else None)
        out.update({f"{lab}_min":mn,f"{lab}_max":mx,f"{lab}_band_width":bw,
            f"{lab}_at_window1":v0,f"{lab}_at_scheduled":vs,f"{lab}_at_realstart":vr,
            f"{lab}_precorridor_width":prew,f"{lab}_corridor_width":corrw,
            f"{lab}_net_direction":nd,f"{lab}_where_motion_corridorfrac":(round(wmi,3) if wmi is not None else "")})
    out["taker_buy_vol"]=sum(q for t,p,q,s in tr if s=="buy")
    out["taker_sell_vol"]=sum(q for t,p,q,s in tr if s=="sell")
    op=ourpath.get(tk)
    if op:
        pth="->".join(str(x) for x in op["path"]) if op["path"] else ""
        out["our_bid_path"]=f"{op['src'] or '?'}:{pth}" if pth else (op['src'] or "")
        out["our_fill_cent"]=op["fill"] if op["fill"] is not None else ""
    else: out["our_bid_path"]=""; out["our_fill_cent"]=""
    rows.append(out)
    if i%40==0: print(f"  ...{i}/{len(items)}",flush=True)
cols=["category","player","match","is_anchor","window1_open_ET","scheduled_ET","realstart_ET","real_start_source",
 "bid_min","bid_max","bid_band_width","bid_at_window1","bid_at_scheduled","bid_at_realstart","bid_precorridor_width","bid_corridor_width","bid_net_direction","bid_where_motion_corridorfrac",
 "ask_min","ask_max","ask_band_width","ask_at_window1","ask_at_scheduled","ask_at_realstart","ask_precorridor_width","ask_corridor_width","ask_net_direction","ask_where_motion_corridorfrac",
 "last_min","last_max","last_band_width","last_at_window1","last_at_scheduled","last_at_realstart","last_precorridor_width","last_corridor_width","last_net_direction","last_where_motion_corridorfrac",
 "taker_buy_vol","taker_sell_vol","our_bid_path","our_fill_cent"]
outp=DOCS/"today_bands_2026-06-22.csv"
with open(outp,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in rows]
sha=hashlib.sha256(open(outp,"rb").read()).hexdigest()
# ---- summary ----
def pct(a,p): a=sorted(a); k=(len(a)-1)*p/100; import math; lo=math.floor(k); return a[lo] if lo>=len(a)-1 else a[lo]+(a[lo+1]-a[lo])*(k-lo)
matches=set(r["match"] for r in rows)
lbw=[r["last_band_width"] for r in rows if isinstance(r["last_band_width"],int)]
bbw=[r["bid_band_width"] for r in rows if isinstance(r["bid_band_width"],int)]
latched=sum(1 for r in rows if r["real_start_source"]=="latch")
print("\n================ FULL-SLATE BAND SUMMARY (Jun 22 2026 ET) ================")
print(f"legs in table: {len(rows)}  | matches: {len(matches)}  | real-start latch legs: {latched} (rest scheduled_fallback)")
from collections import Counter
print("by category:",dict(Counter(r["category"] for r in rows)))
print(f"\nLAST-TRADED band_width (cents) distribution: n={len(lbw)} min={min(lbw)} p25={pct(lbw,25):.0f} median={statistics.median(lbw):.0f} p75={pct(lbw,75):.0f} p90={pct(lbw,90):.0f} max={max(lbw)}")
print(f"BEST-BID  band_width (cents) distribution: median={statistics.median(bbw):.0f} p90={pct(bbw,90):.0f} max={max(bbw)}")
wmf=[r["last_where_motion_corridorfrac"] for r in rows if isinstance(r["last_where_motion_corridorfrac"],float)]
if wmf: print(f"where_motion (last, corridor fraction) median={statistics.median(wmf):.2f}  (0=all pre-corridor,1=all corridor)")
for tk,who in ANCHOR.items():
    r=next((r for r in rows if r["player"]==who),None)
    if r:
        print(f"\n[ANCHOR {who}] last band {r['last_band_width']}c (min{r['last_min']}-max{r['last_max']}) | bid band {r['bid_band_width']}c | net_dir(last) {r['last_net_direction']} | where_motion {r['last_where_motion_corridorfrac']} | realstart_src {r['real_start_source']} | our_fill {r['our_fill_cent']}")
        med=statistics.median(lbw)
        print(f"    vs slate: last-band median {med:.0f}c -> {who} is {'ABOVE' if r['last_band_width']>med else 'BELOW/EQ'} median")
print(f"\nCSV: {outp}\nsha256: {sha}")
print(f"depth source: {len(glob.glob(str(HERE/'data/durable/depth_recorder/depth_20260622_*.jsonl.gz')))} files depth_20260622_*.jsonl.gz")
