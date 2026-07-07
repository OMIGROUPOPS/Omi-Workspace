#!/usr/bin/env python3
"""[READ-ONLY] SPREAD CENSUS RECOUNT — NON-SELF chain. Own resting orders (by oid
lifecycle: order_placed buy -> order_cancelled/fill) subtracted from the 5-level book
at each placement decision; levels emptied by our own size fall through to the next.
Classifies fresh posts AND walk steps vs the non-self chain. Writes /tmp/spread_recount.json."""
import json, gzip, sys, time, base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
B_FLIP = 1783309839.0
ROOT = Path("/root/Omi-Workspace/arb-executor")
LOGS = ["/tmp/session_since_boot.jsonl", str(ROOT/"logs/live_v3_20260706.jsonl"), str(ROOT/"logs/live_v3_20260707.jsonl")]
OWN_QTY = 5.0
_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
def book_rows(tk):
    """full 5-level rows: (ts, [(bid,sz)x5], ask1)"""
    for suf in (".csv.gz",".csv"):
        f=ROOT/"analysis/premarket_ticks"/(tk+suf)
        if f.exists(): break
    else: return []
    op=gzip.open if f.suffix==".gz" else open
    out=[]
    with op(f,"rt",encoding="utf-8",errors="replace") as fh:
        next(fh,None)
        for ln in fh:
            p=ln.split(",",14)
            if len(p)<14: continue
            t=pts(p[0])
            if t is None: continue
            try:
                bids=[(int(p[2+i*2]) if p[2+i*2] else None, float(p[3+i*2]) if p[3+i*2] else 0.0) for i in range(5)]
                a1=int(p[12]) if p[12] else None
            except: continue
            out.append((t,bids,a1))
    out.sort(key=lambda r:r[0]); return out

# ---- own-order lifecycle ----
placed=[]; cancels={}; fills_log={}
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for ln in open(LOG,encoding="utf-8",errors="replace"):
        if '"order_placed"' in ln and '"buy"' in ln:
            try: o=json.loads(ln)
            except: continue
            d=o.get("details",{})
            if d.get("action")=="buy" and d.get("price") is not None and d.get("order_id"):
                placed.append({"tk":o["ticker"],"ts":o.get("ts_epoch",0),"px":d["price"],"oid":d["order_id"]})
        elif '"order_cancelled"' in ln or '"order_canceled"' in ln:
            try: o=json.loads(ln)
            except: continue
            oid=o.get("details",{}).get("order_id")
            if oid and oid not in cancels: cancels[oid]=o.get("ts_epoch",0)
        elif '"entry_filled"' in ln:
            try: o=json.loads(ln)
            except: continue
            fills_log.setdefault(o.get("ticker"),o.get("ts_epoch",0))
own_by_tk=defaultdict(list)
seen_oid=set()
for p_ in placed:
    if p_["oid"] in seen_oid: continue
    seen_oid.add(p_["oid"])
    end=cancels.get(p_["oid"]) or fills_log.get(p_["tk"]) or (p_["ts"]+12*3600)
    own_by_tk[p_["tk"]].append((p_["ts"],end,p_["px"]))
print(f"placements {len(placed)} | own intervals {sum(len(v) for v in own_by_tk.values())}",file=sys.stderr)

# exchange fills by oid
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests
pk=serialization.load_pem_private_key((ROOT/"kalshi.pem").read_bytes(),password=None,backend=default_backend())
B="https://api.elections.kalshi.com/trade-api/v2"
def sgn(m,p):
    ts=str(int(time.time()*1000)); sp="/trade-api/v2"+p.split("?")[0]
    sig=pk.sign((ts+m+sp).encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())
    return {"KALSHI-ACCESS-KEY":"f3b064d1-a02e-42a4-b2b1-132834694d23","KALSHI-ACCESS-SIGNATURE":base64.b64encode(sig).decode(),"KALSHI-ACCESS-TIMESTAMP":ts}
fill_by_oid={}
cursor=""; pages=0
while pages<120:
    p=f"/portfolio/fills?limit=200&min_ts={int(B_FLIP)}"+(f"&cursor={cursor}" if cursor else "")
    try: r=requests.get(B+p,headers=sgn("GET",p),timeout=30).json()
    except Exception: time.sleep(1); continue
    pages+=1
    for f in r.get("fills",[]):
        if f.get("action")=="buy":
            t=datetime.fromisoformat(f["created_time"].replace("Z","+00:00")).timestamp()
            o=fill_by_oid.setdefault(f["order_id"],{"px":float(f["yes_price_dollars"])*100,"qty":0.0,"ts":t})
            o["qty"]+=float(f["count_fp"])
    cursor=r.get("cursor")
    if not cursor: break

books={}
def get_book(tk):
    if tk not in books: books[tk]=book_rows(tk)
    return books[tk]
import sys as _sys
_sys.path.insert(0, str(ROOT/"analysis"))
from ex_self_chain import book_ex_self as _one_chain   # [ONE CHAIN] the only non-self math
def nonself_book(tk, ts, exclude_own_at):
    """last book row <= ts; subtract own resting qty at own px levels."""
    rows=get_book(tk)
    lo,hi=0,len(rows)
    import bisect
    idx=bisect.bisect_right([r[0] for r in rows], ts)-1
    if idx<0: return None,None,None
    t_row,bids,a1=rows[idx]
    own_px=[px for (s,e,px) in own_by_tk.get(tk,[]) if s<=exclude_own_at<e]
    own_p = own_px[0] if own_px else None   # one entry order per ticker by construction
    nb = _one_chain([(b, sz) for b, sz in bids if b is not None],
                    own_px=own_p, own_qty=OWN_QTY * len(own_px) if own_px else 0.0)
    return nb,a1,t_row

rows_out=[]
self_flips=0; tick_postdates=0
for p_ in placed:
    tk,ts,px,oid=p_["tk"],p_["ts"],p_["px"],p_["oid"]
    nb,na,t_row=nonself_book(tk, ts-0.5, ts-0.5)
    if nb is None: continue
    if t_row>ts: tick_postdates+=1
    if px<nb: cls="BELOW_CHAIN"; intr=None
    elif px==nb: cls="JOINED"; intr=None
    elif px==nb+1: cls="IMPROVED_1"; intr=None
    elif na is not None and px>=na: cls="MARKETABLE"; intr=None
    else: cls="CREATED_MID"; intr=px-nb
    f=fill_by_oid.get(oid)
    rows_out.append({"tk":tk[-20:],"ts":ts,"px":px,"ns_bid":nb,"ask":na,"cls":cls,"intr":intr,
                     "filled":f is not None,"fill_px":f and f["px"],"fill_qty":f and f["qty"],
                     "ttf_min":round((f["ts"]-ts)/60,1) if f else None})
per=defaultdict(lambda: {"n":0,"filled":0,"vs_bid":[],"ttf":[],"intr":[],"mid_cost":0.0})
for r_ in rows_out:
    P=per[r_["cls"]]; P["n"]+=1
    if r_["intr"] is not None: P["intr"].append(r_["intr"])
    if r_["filled"]:
        P["filled"]+=1; P["vs_bid"].append(r_["fill_px"]-r_["ns_bid"]); P["ttf"].append(r_["ttf_min"])
        if r_["cls"]=="CREATED_MID": P["mid_cost"]+=(r_["fill_px"]-(r_["ns_bid"]+1))*(r_["fill_qty"] or 0)/100.0
def med(v):
    v=sorted(x for x in v if x is not None); return v[len(v)//2] if v else None
summary={}
for c,P in sorted(per.items()):
    summary[c]={"n":P["n"],"share":round(P["n"]/len(rows_out),3),"fill_rate":round(P["filled"]/P["n"],3),
                "fill_vs_nsbid_med":med(P["vs_bid"]),"ttf_med":med(P["ttf"]),
                "intr_med":med(P["intr"]),"intr_p90":None if not P["intr"] else sorted(P["intr"])[int(len(P["intr"])*0.9)],
                "mid_cost_$":round(P["mid_cost"],2)}
    print(c,summary[c],file=sys.stderr)
# TANKAW walk steps under non-self lens
tan=[r_ for r_ in rows_out if "TANKAW-TAN" in r_["tk"]]
gom=[r_ for r_ in rows_out if "GOMOFN" in r_["tk"]]
json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
           "n":len(rows_out),"tick_postdates":tick_postdates,
           "summary":summary,"rows":rows_out,
           "tankaw_steps":[{k:r_[k] for k in ("ts","px","ns_bid","ask","cls")} for r_ in sorted(tan,key=lambda x:x["ts"])],
           "gomofn":[{k:r_[k] for k in ("ts","px","ns_bid","ask","cls","filled","fill_px")} for r_ in sorted(gom,key=lambda x:x["ts"])]},
          open("/tmp/spread_recount.json","w"))
print("DONE",file=sys.stderr)
