#!/usr/bin/env python3
"""[READ-ONLY] SPREAD-EXPRESSION CENSUS — every bot placement since flip boot:
posted level vs the chain (book at post). Classes: BELOW_CHAIN / JOINED / IMPROVED_1 /
CREATED_MID (intrusion c above bid) / MARKETABLE. Per class: fill rate (exchange
order_id joins), fill vs bid-at-post, vs window low, time-to-fill. THE NUMBER:
c/day paid by mid-spread creation vs join/improve, fill-rate delta stated both ways.
Plus the TANKAW exhibit anatomy. Writes /tmp/spread_census.json."""
import json, gzip, sys, time, base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
B_FLIP = 1783309839.0
ROOT = Path("/root/Omi-Workspace/arb-executor")
LOGS = ["/tmp/session_since_boot.jsonl", str(ROOT/"logs/live_v3_20260706.jsonl"), str(ROOT/"logs/live_v3_20260707.jsonl")]
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), "?")
_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
def book_min(tk):
    for suf in (".csv.gz",".csv"):
        f=ROOT/"analysis/premarket_ticks"/(tk+suf)
        if f.exists(): break
    else: return {}
    op=gzip.open if f.suffix==".gz" else open
    out={}
    with op(f,"rt",encoding="utf-8",errors="replace") as fh:
        next(fh,None)
        for ln in fh:
            p=ln.split(",",14)
            if len(p)<14: continue
            t=pts(p[0])
            if t is None: continue
            try:
                b=int(p[2]) if p[2] else None; a=int(p[12]) if p[12] else None
            except: continue
            out[int(t//60)]=(b,a)
    return out
def tape_sf(tk):
    for suf in (".csv",".csv.gz"):
        f=ROOT/"analysis/trades"/(tk+suf)
        if f.exists(): break
    else: return []
    op=gzip.open if f.suffix==".gz" else open
    rows=[]
    with op(f,"rt",encoding="utf-8",errors="replace") as fh:
        next(fh,None)
        for ln in fh:
            p=ln.rstrip("\n").split(",")
            if len(p)<5: continue
            t=pts(p[0])
            if t is None: continue
            try: rows.append((t,int(p[2]),p[4]))
            except: continue
    rows.sort(); return rows

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
def g(p):
    for _ in range(4):
        try: return requests.get(B+p,headers=sgn("GET",p),timeout=30).json()
        except Exception: time.sleep(0.5)
    return {}
fill_by_oid={}
cursor=""; pages=0
while pages<120:
    p=f"/portfolio/fills?limit=200&min_ts={int(B_FLIP)}"+(f"&cursor={cursor}" if cursor else "")
    r=g(p); pages+=1
    for f in r.get("fills",[]):
        if f.get("action")=="buy":
            t=datetime.fromisoformat(f["created_time"].replace("Z","+00:00")).timestamp()
            o=fill_by_oid.setdefault(f["order_id"],{"px":float(f["yes_price_dollars"])*100,"qty":0.0,"ts":t})
            o["qty"]+=float(f["count_fp"])
    cursor=r.get("cursor")
    if not cursor: break
print(f"exchange buy fills: {len(fill_by_oid)} orders",file=sys.stderr)

# placements: order_placed buys w/ oid; book fields from same-second v4_place if present
places=[]; vp_book={}
seen_lines=set()
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for ln in open(LOG,encoding="utf-8",errors="replace"):
        if '"v4_place"' in ln:
            try: o=json.loads(ln)
            except: continue
            d=o.get("details",{})
            if d.get("book_bid") is not None:
                vp_book[(o.get("ticker"),int(o.get("ts_epoch",0)))]=(d["book_bid"],d["book_ask"])
        elif '"order_placed"' in ln and '"buy"' in ln:
            try: o=json.loads(ln)
            except: continue
            d=o.get("details",{})
            if d.get("action")!="buy" or d.get("price") is None: continue
            k=(o.get("ticker"),d.get("order_id"))
            if k in seen_lines: continue
            seen_lines.add(k)
            places.append({"tk":o["ticker"],"ts":o.get("ts_epoch",0),"px":d["price"],"oid":d.get("order_id")})
print(f"placements: {len(places)}",file=sys.stderr)

books={}; tapes={}
def get_book(tk):
    if tk not in books: books[tk]=book_min(tk)
    return books[tk]
def get_tape(tk):
    if tk not in tapes: tapes[tk]=tape_sf(tk)
    return tapes[tk]

rows=[]
for pl in places:
    tk,ts,px,oid=pl["tk"],pl["ts"],pl["px"],pl["oid"]
    bb=ba=None
    for dt in (0,-1,1):
        v=vp_book.get((tk,int(ts)+dt))
        if v: bb,ba=v; break
    if bb is None:
        bm=get_book(tk)
        for dm in (0,-1,-2,1):
            v=bm.get(int(ts//60)+dm)
            if v and v[0] is not None: bb,ba=v; break
    if bb is None: continue
    if px<bb: cls="BELOW_CHAIN"; intr=None
    elif px==bb: cls="JOINED"; intr=None
    elif px==bb+1: cls="IMPROVED_1"; intr=None
    elif ba is not None and px>=ba: cls="MARKETABLE"; intr=None
    else: cls="CREATED_MID"; intr=px-bb
    f=fill_by_oid.get(oid)
    low=None
    sf=[r_ for r_ in get_tape(tk) if r_[2]=="no" and ts<r_[0]<ts+8*3600]
    if sf: low=min(r_[1] for r_ in sf)
    rows.append({"tk":tk[-20:],"cat":cat_of(tk),"ts":ts,"px":px,"bid":bb,"ask":ba,
                 "spread":(ba-bb) if (ba is not None and bb is not None) else None,
                 "cls":cls,"intrusion":intr,
                 "filled":f is not None,"fill_px":f and f["px"],"fill_qty":f and f["qty"],
                 "ttf_min":round((f["ts"]-ts)/60,1) if f else None,
                 "win_low":low})
per=defaultdict(lambda: {"n":0,"filled":0,"vs_bid":[],"vs_low":[],"ttf":[],"intr":[],"mid_cost":0.0})
for r_ in rows:
    P=per[r_["cls"]]; P["n"]+=1
    if r_["intrusion"] is not None: P["intr"].append(r_["intrusion"])
    if r_["filled"]:
        P["filled"]+=1
        P["vs_bid"].append(r_["fill_px"]-r_["bid"])
        if r_["win_low"] is not None: P["vs_low"].append(r_["fill_px"]-r_["win_low"])
        P["ttf"].append(r_["ttf_min"])
        if r_["cls"]=="CREATED_MID":
            P["mid_cost"]+=(r_["fill_px"]-(r_["bid"]+1))*(r_["fill_qty"] or 0)/100.0
def med(v):
    v=sorted(x for x in v if x is not None); return v[len(v)//2] if v else None
summary={}
for c,P in per.items():
    summary[c]={"n":P["n"],"fill_rate":round(P["filled"]/P["n"],3),
                "fill_vs_bid_med":med(P["vs_bid"]),"fill_vs_winlow_med":med(P["vs_low"]),
                "ttf_med":med(P["ttf"]),"intrusion_med":med(P["intr"]),
                "mid_cost_$":round(P["mid_cost"],2)}
    print(c,summary[c],file=sys.stderr)

# TANKAW exhibit
ex={}
tk="KXITFMATCH-26JUL06TANKAW-TAN"
p_tan=[p for p in places if p["tk"]==tk]
bm=get_book(tk)
if p_tan:
    last=max(p_tan,key=lambda p:p["ts"])
    mmin=int(last["ts"]//60)
    ex["posts"]=[{"t":datetime.fromtimestamp(p['ts'],ET).strftime('%H:%M:%S'),"px":p["px"],
                  "book":bm.get(int(p["ts"]//60))} for p in sorted(p_tan,key=lambda p:p["ts"])]
    sf=[r_ for r_ in get_tape(tk)]
    fill_ts=1783391663.88
    after=[(datetime.fromtimestamp(t,ET).strftime('%H:%M'),pr,s) for t,pr,s in sf if fill_ts<t<fill_ts+6*3600]
    ex["prints_73_76_after_fill"]=[x for x in after if 73<=x[1]<=76][:10]
    ex["all_after_fill_first10"]=after[:10]
    ex["book_at_fill_min"]=bm.get(int(fill_ts//60))
json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
           "summary":summary,"rows_n":len(rows),"exhibit_TANKAW":ex},
          open("/tmp/spread_census.json","w"))
print("DONE",file=sys.stderr)
