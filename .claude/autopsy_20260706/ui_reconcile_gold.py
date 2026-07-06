#!/usr/bin/env python3
"""[READ-ONLY] (1) KALSHI UI RECONCILE flows + (3) GOLD-CLASS CENSUS raw material.
Window for the reconcile: 2026-07-05 16:30 ET -> now (the UI's 24h delta reference).
Writes /tmp/ui_gold.json."""
import json, time, base64, sys, gzip
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
W0 = datetime(2026,7,5,16,30,tzinfo=ET).timestamp()
B_FLIP = 1783309839.0
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests
pk = serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(), password=None, backend=default_backend())
B = "https://api.elections.kalshi.com/trade-api/v2"
def sgn(m, p):
    ts = str(int(time.time()*1000)); sp = "/trade-api/v2"+p.split("?")[0]
    sig = pk.sign((ts+m+sp).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY":"f3b064d1-a02e-42a4-b2b1-132834694d23","KALSHI-ACCESS-SIGNATURE":base64.b64encode(sig).decode(),"KALSHI-ACCESS-TIMESTAMP":ts}
def g(p):
    for _ in range(4):
        try: return requests.get(B+p, headers=sgn("GET", p), timeout=30).json()
        except Exception: time.sleep(0.5)
    return {}

bal = g("/portfolio/balance")
led = json.load(open("/tmp/slate_ledger.json"))
led_tks = set()
for r in led["rows"]:
    for l in r["legs"]:
        led_tks.add("KX"+l["tk"] if not l["tk"].startswith("KX") else l["tk"])
manual = set(led["manual_excluded"])

# fills since window start (ALL tickers)
fills = defaultdict(list); cursor=""; pages=0
while pages < 120:
    p = f"/portfolio/fills?limit=200&min_ts={int(W0)}" + (f"&cursor={cursor}" if cursor else "")
    r = g(p); pages += 1
    for f in r.get("fills", []): fills[f["ticker"]].append(f)
    cursor = r.get("cursor")
    if not cursor: break
setts = {}; cursor=""; pages=0
while pages < 60:
    p = "/portfolio/settlements?limit=200" + (f"&cursor={cursor}" if cursor else "")
    r = g(p); pages += 1
    batch = r.get("settlements", [])
    for s in batch: setts.setdefault(s["ticker"], s)
    cursor = r.get("cursor")
    if not cursor: break
    try:
        last = batch[-1].get("settled_time","")
        if last and datetime.fromisoformat(last.replace("Z","+00:00")).timestamp() < W0 - 86400: break
    except: pass
pos_rows=[]; cursor=""
for _ in range(40):
    p="/portfolio/positions?limit=200&settlement_status=unsettled"+(f"&cursor={cursor}" if cursor else "")
    r=g(p)
    pos_rows+=r.get("market_positions",[])
    cursor=r.get("cursor")
    if not cursor: break
print(f"balance={bal} fills_tks={len(fills)} setts={len(setts)} pos={len(pos_rows)}", file=sys.stderr)

def wflows(tk):
    """in-window flows for ticker: buys$, sells$, fees$ (fills), settle revenue$ + fee if settled in window."""
    b=s=fee=0.0
    for f in fills.get(tk,[]):
        t=datetime.fromisoformat(f["created_time"].replace("Z","+00:00")).timestamp()
        if t < W0: continue
        v=float(f.get("yes_price_dollars") or 0)*float(f.get("count_fp") or 0)
        if f.get("action")=="buy": b+=v
        else: s+=v
        fee+=float(f.get("fee_cost") or 0)
    rev=sfee=0.0; st=setts.get(tk)
    settled_in=False
    if st:
        t=datetime.fromisoformat(st["settled_time"].replace("Z","+00:00")).timestamp()
        if t>=W0:
            settled_in=True
            rev=float(st.get("revenue") or 0)/100.0
            sfee=float(st.get("fee_cost") or 0)
    return b,s,fee,rev,sfee,settled_in

# bucket the universe: every ticker with any in-window activity or open position
universe=set(fills.keys())|set(t for t,s in setts.items()
    if datetime.fromisoformat(s["settled_time"].replace("Z","+00:00")).timestamp()>=W0)|set(p["ticker"] for p in pos_rows)
buckets=defaultdict(lambda: {"buys":0.0,"sells":0.0,"fees":0.0,"rev":0.0,"n":0,"n_settled":0})
for tk in universe:
    b,s,fee,rev,sfee,settled_in=wflows(tk)
    if tk in manual or "MATCH-" not in tk: key="manual_or_nonmatch"
    elif tk in led_tks: key="bot_ledger"
    else: key="preboot_tail"   # tennis, not in ledger (no post-boot fills) = July-5 slate tail
    bb=buckets[key]
    bb["buys"]+=b; bb["sells"]+=s; bb["fees"]+=fee+sfee; bb["rev"]+=rev; bb["n"]+=1
    bb["n_settled"]+=1 if settled_in else 0
for k,v in buckets.items():
    v["realized_vs_cost"]=round(v["rev"]+v["sells"]-v["buys"]-v["fees"],2)
    for kk in ("buys","sells","fees","rev"): v[kk]=round(v[kk],2)

# open positions mark now (all, split bot vs manual)
mark={"bot":0.0,"manual":0.0}; cost={"bot":0.0,"manual":0.0}
tks=[p["ticker"] for p in pos_rows if float(p.get("position_fp") or 0)!=0]
mkt={}
for i in range(0,len(tks),90):
    r=g("/markets?tickers="+",".join(tks[i:i+90])+"&limit=100")
    for m in r.get("markets",[]): mkt[m["ticker"]]=m
for p in pos_rows:
    q=float(p.get("position_fp") or 0)
    if q==0: continue
    m=mkt.get(p["ticker"],{})
    bd=m.get("yes_bid_dollars"); bid=float(bd) if bd else 0.0
    key="manual" if (p["ticker"] in manual or "MATCH-" not in p["ticker"]) else "bot"
    mark[key]+=q*bid
    cost[key]+=float(p.get("market_exposure_dollars") or 0)

# ---------- GOLD CENSUS ----------
_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
def tape(tk):
    for suf in (".csv",".csv.gz"):
        f=Path("analysis/trades")/(tk+suf)
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
            try: rows.append((t,int(p[2]),int(float(p[3])),p[4]))
            except: continue
    rows.sort(); return rows

def leg_census(r, l, kind):
    tk="KX"+l["tk"] if not l["tk"].startswith("KX") else l["tk"]
    rows=tape(tk)
    ft=float(l["fill_ts"]) if l.get("fill_ts") else None
    conc=float(l["conc_ts"]) if l.get("conc_ts") else None
    # own W1 dip: min sell-flow print before fill
    sf=[pr for t,pr,ct,s in rows if s=="no" and ft and t<=ft]
    own_dip=min(sf) if sf else None
    # band touch after fill
    bt=None
    if l.get("exit_lvl") is not None and ft:
        for t,pr,ct,s in rows:
            if t>ft and pr>=l["exit_lvl"]: bt=t; break
    sib=[x for x in r["legs"] if x["tk"]!=l["tk"]]
    sibd=sib[0] if sib else {}
    return {"ev":r["ev"][-22:],"cat":r["cat"],"kind":kind,
            "bucket":min(4,max(0,int((l["vw"] or 0)//20))),
            "fill":l["vw"],"own_w1_dip":own_dip,
            "fill_vs_dip":round((l["vw"]-own_dip),1) if (l.get("vw") is not None and own_dip is not None) else None,
            "daim":l.get("daim"),"combined":r.get("combined"),
            "conc_to_fill_min":round((ft-conc)/60,1) if (ft and conc) else None,
            "fill_to_touch_min":round((bt-ft)/60,1) if (bt and ft) else None,
            "band_dist":round(l["exit_lvl"]-l["vw"],1) if (l.get("exit_lvl") is not None and l.get("vw") is not None) else None,
            "sib_disp":sibd.get("disp"),"sib_fill":sibd.get("vw"),
            "sib_dt_min":round((float(sibd["fill_ts"])-ft)/60,1) if (sibd.get("fill_ts") and ft) else None}

gold=[]; rode=[]
for r in led["rows"]:
    if r["status"]!="SETTLED": continue
    for l in r["legs"]:
        if l.get("vw") is None: continue
        w1fill = l.get("w1") in ("W1_CASHED","W1_REACHABLE","W2_ONLY") and l.get("fill_ts") and l.get("conc_ts")
        # gold: filled in W1 (fill before honest start => w1 stamp exists non-'—') and cashed W1/COR
        if l.get("disp") in ("EXIT_FILLED_W1","EXIT_FILLED_CORRIDOR") and l.get("w1") in ("W1_CASHED","W1_REACHABLE","W2_ONLY"):
            gold.append(leg_census(r,l,"GOLD"))
        elif l.get("disp")=="RODE_TO_SETTLEMENT":
            rode.append(leg_census(r,l,"RODE"))
json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
           "balance":bal,"buckets":dict(buckets),
           "open_mark":{k:round(v,2) for k,v in mark.items()},
           "open_cost":{k:round(v,2) for k,v in cost.items()},
           "gold":gold,"rode":rode},
          open("/tmp/ui_gold.json","w"),default=str)
print(f"buckets: {json.dumps({k:v['realized_vs_cost'] for k,v in buckets.items()})}",file=sys.stderr)
print(f"open mark bot={mark['bot']:.2f} manual={mark['manual']:.2f} | cost bot={cost['bot']:.2f} manual={cost['manual']:.2f}",file=sys.stderr)
print(f"gold legs={len(gold)} rode legs={len(rode)}",file=sys.stderr)
