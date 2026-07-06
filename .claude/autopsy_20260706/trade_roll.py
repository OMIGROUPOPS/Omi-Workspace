#!/usr/bin/env python3
"""[READ-ONLY] TRADE ROLL — every bot tennis position since the flip boot, settled AND live.
Exchange truth: /portfolio/fills + /portfolio/settlements + /portfolio/positions +
/portfolio/orders + live /markets book. Epoch-stamped by CONCEPTION (first post ts):
  E3a [23:50:39 07-05, 12:15:22 07-06)  riser ARMED, pre guards/true-basis
  E3b [12:15:22, 15:25:58)              riser ARMED + guards/true-basis live (d01a3cc)
  E4  [15:25:58, now]                   riser DISARMED (3db9af8)
(E1 flip + E2 bound-ruling are coincident context for every in-scope row.)
Excludes non-MATCH tickers and manual-attributed adoptions. Writes /tmp/trade_roll.json."""
import json, time, base64, sys, re, gzip
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
B_FLIP, B_GUARDS, B_DISARM = 1783309839.0, 1783354522.0, 1783365958.0
GOAL = 97
LOGS = ["/tmp/session_since_boot.jsonl", "logs/live_v3_20260706.jsonl"]
VALID = "/root/Omi-Workspace/.claude/live_20260705/live_validation.jsonl"
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), None)
def epoch_of(ts):
    if ts is None: return "?"
    if ts < B_FLIP: return "E0"
    if ts < B_GUARDS: return "E3a"
    if ts < B_DISARM: return "E3b"
    return "E4"
def hm(e): return datetime.fromtimestamp(e, ET).strftime("%m-%d %H:%M") if e else None

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

sch = json.load(open("state/schedule.json"))["schedule"]
def honest_start(ev):
    m = re.search(r"\d{2}[A-Z]{3}\d{2}([A-Z]{6})$", ev)
    if not m: return None
    pc = m.group(1)
    for k in (pc, pc[3:]+pc[:3]):
        e = sch.get(k)
        if e and not e.get("espn_midnight"):
            try: return datetime.fromisoformat(e["start_time"].replace("Z","+00:00")).timestamp()
            except: pass
    return None

# ---------- logs ----------
posts=defaultdict(list); exitfill={}; manual=set(); vstamp={}; reaim=set(); latch={}
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for line in open(LOG, encoding="utf-8", errors="replace"):
        if '"event"' not in line: continue
        try: o=json.loads(line)
        except: continue
        e,tk,d,ts=o.get("event"),o.get("ticker") or "",o.get("details",{}),o.get("ts_epoch",0)
        if e=="order_placed" and d.get("action")=="buy" and tk and d.get("price") is not None:
            posts[tk].append((ts,d["price"]))
        elif e=="exit_filled" and tk and tk not in exitfill:
            exitfill[tk]=ts
        elif e=="reconcile_v4_adopted" and tk and d.get("attribution")=="manual":
            manual.add(tk)
        elif e=="reaim_sibling_arrival" and tk:
            reaim.add(tk)
        elif e=="match_live_detected":
            ev=d.get("event")
            if ev and ev not in latch: latch[ev]=ts
if Path(VALID).exists():
    for line in open(VALID,encoding="utf-8",errors="replace"):
        try: o=json.loads(line)
        except: continue
        if o.get("type") in ("fill","fill_regrade") and o.get("ticker"):
            cur=vstamp.get(o["ticker"],{})
            cur.update({k:o[k] for k in ("aim_level","fill_minus_aim","side") if o.get(k) is not None})
            vstamp[o["ticker"]]=cur

# ---------- exchange truth ----------
fills=defaultdict(list); cursor=""; pages=0
while pages<80:
    p=f"/portfolio/fills?limit=200&min_ts={int(B_FLIP)}"+(f"&cursor={cursor}" if cursor else "")
    r=g(p); pages+=1
    for f in r.get("fills",[]): fills[f["ticker"]].append(f)
    cursor=r.get("cursor")
    if not cursor: break
setts={}; cursor=""; pages=0
while pages<40:
    p=f"/portfolio/settlements?limit=200"+(f"&cursor={cursor}" if cursor else "")
    r=g(p); pages+=1
    batch=r.get("settlements",[])
    for s in batch: setts.setdefault(s["ticker"],s)
    cursor=r.get("cursor")
    last=batch[-1].get("settled_time","") if batch else ""
    if not cursor: break
    try:
        if last and datetime.fromisoformat(last.replace("Z","+00:00")).timestamp()<B_FLIP: break
    except: pass
pos_rows=[]; cursor=""
for _ in range(40):
    p="/trade-api/v2/portfolio/positions?limit=200&settlement_status=unsettled".replace("/trade-api/v2","")+(f"&cursor={cursor}" if cursor else "")
    r=g(p)
    pos_rows+=r.get("market_positions",[])
    cursor=r.get("cursor")
    if not cursor: break
orders=[]; cursor=""
for _ in range(40):
    p="/portfolio/orders?status=resting&limit=200"+(f"&cursor={cursor}" if cursor else "")
    r=g(p)
    orders+=r.get("orders",[])
    cursor=r.get("cursor")
    if not cursor: break
print(f"fills tks={len(fills)} setts={len(setts)} open_pos={len(pos_rows)} resting={len(orders)}",file=sys.stderr)

def is_bot_tennis(tk): return "MATCH-" in tk and tk not in manual
def buy_vwap(tk):
    ct=px=0.0; first=None
    for f in fills.get(tk,[]):
        if f.get("action")!="buy": continue
        c=float(f.get("count_fp") or 0); pxx=float(f.get("yes_price_dollars") or 0)*100
        ct+=c; px+=c*pxx
        t=datetime.fromisoformat(f["created_time"].replace("Z","+00:00")).timestamp()
        first=t if first is None else min(first,t)
    return (round(px/ct,1),ct,first) if ct else (None,0,None)
def sells_cash(tk):
    return sum(float(f.get("yes_price_dollars") or 0)*float(f.get("count_fp") or 0)
               for f in fills.get(tk,[]) if f.get("action")=="sell")
def tk_pnl(tk):
    s=setts.get(tk)
    if s is None: return None
    rev=float(s.get("revenue") or 0)/100.0
    buys=sum(float(f.get("yes_price_dollars") or 0)*float(f.get("count_fp") or 0)
             for f in fills.get(tk,[]) if f.get("action")=="buy")
    fee=float(s.get("fee_cost") or 0)+sum(float(f.get("fee_cost") or 0) for f in fills.get(tk,[]))
    return round(rev+sells_cash(tk)-buys-fee,2)

# tape for W1_REACHABLE
_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
def band_touch_pre(tk, level, hstart):
    for suf in (".csv",".csv.gz"):
        f=Path("analysis/trades")/(tk+suf)
        if f.exists(): break
    else: return False
    op=gzip.open if f.suffix==".gz" else open
    with op(f,"rt",encoding="utf-8",errors="replace") as fh:
        next(fh,None)
        for ln in fh:
            p=ln.rstrip("\n").split(",")
            if len(p)<5: continue
            t=pts(p[0])
            if t is None or t>=hstart: continue
            try:
                if int(p[2])>=level: return True
            except: continue
    return False

# exit levels from logs (v4_exit_posted)
exitpx={}
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for line in open(LOG,encoding="utf-8",errors="replace"):
        if '"v4_exit_posted"' not in line: continue
        try: o=json.loads(line)
        except: continue
        tk=o.get("ticker")
        if tk and tk not in exitpx: exitpx[tk]=o.get("details",{}).get("exit_price")

# ---------- assemble events ----------
all_tks=set(t for t in set(list(fills)+list(posts)) if is_bot_tennis(t))
evs=defaultdict(list)
for tk in all_tks: evs[tk.rsplit("-",1)[0]].append(tk)
settled_rows=[]; live_rows=[]
open_pos={p["ticker"]: p for p in pos_rows if float(p.get("position_fp") or 0)!=0}
resting=defaultdict(list)
for o in orders:
    if o.get("action")=="buy": resting[o["ticker"]].append(o)
mkt_cache={}
def mkt(tks):
    need=[t for t in tks if t not in mkt_cache]
    for i in range(0,len(need),90):
        r=g("/markets?tickers="+",".join(need[i:i+90])+"&limit=100")
        for m in r.get("markets",[]): mkt_cache[m["ticker"]]=m
    return {t:mkt_cache.get(t,{}) for t in tks}

now=time.time()
for ev,tks in sorted(evs.items()):
    cat=cat_of(ev+"-") or "?"
    hs=honest_start(ev)
    legs=[]
    for tk in sorted(set(tks)):
        vw,q,ft=buy_vwap(tk)
        p0=sorted(posts.get(tk,[]))
        conc=p0[0][0] if p0 else ft
        st=setts.get(tk)
        w1="—"
        if vw is not None and hs and ft and ft<hs:
            xf=exitfill.get(tk)
            if xf and xf<hs: w1="W1_CASHED"
            elif exitpx.get(tk) and band_touch_pre(tk,exitpx[tk],hs): w1="W1_REACHABLE"
            else: w1="W2_ONLY"
        elif vw is not None: w1="W2_ONLY" if hs else "no-honest-clock"
        vs=vstamp.get(tk,{})
        legs.append({"tk":tk,"suf":tk.rsplit("-",1)[-1],"vw":vw,"qty":q,"fill_ts":ft,
                     "conc_ts":conc,"conc_e":epoch_of(conc),"fill_e":epoch_of(ft),
                     "aim":vs.get("aim_level"),"daim":vs.get("fill_minus_aim"),
                     "w1":w1,"settled":st is not None,"pnl":tk_pnl(tk),
                     "open_qty":float((open_pos.get(tk) or {}).get("position_fp") or 0),
                     "resting":[{"px":round(float(o.get("yes_price_dollars") or 0)*100),
                                 "ts":o.get("created_time","")[11:16]} for o in resting.get(tk,[])],
                     "reaim":tk in reaim})
    filled=[l for l in legs if l["vw"] is not None]
    all_settled=filled and all(l["settled"] for l in filled)
    comb=round(sum(l["vw"] for l in filled),1) if len(filled)==2 else None
    concs=[l["conc_ts"] for l in legs if l["conc_ts"]]
    ep=epoch_of(min(concs)) if concs else "?"
    spans=sorted(set([l["conc_e"] for l in legs if l["conc_ts"]]+[l["fill_e"] for l in filled if l["fill_ts"]]))
    row={"ev":ev.replace("KX",""),"cat":cat,"epoch":ep,"spans":spans,
         "legs":legs,"combined":comb,"hs_t":hm(hs),"latched":ev in latch}
    if all_settled and not any(l["open_qty"] for l in legs):
        row["pnl"]=round(sum(l["pnl"] or 0 for l in filled),2)
        # grade (roll rubric: combined + naked + W1 gate)
        if len(filled)==1:
            row["grade"]="F" if (filled[0]["pnl"] or 0)<0 else "D"
        elif comb is None: row["grade"]="?"
        elif comb>100: row["grade"]="C" if comb<=105 else "D"
        elif comb>GOAL: row["grade"]="C"
        else:
            w1s=[l["w1"] for l in filled]
            row["grade"]="A" if (comb<=GOAL and all(w in ("W1_CASHED","W1_REACHABLE") for w in w1s) and row["pnl"]>=0) else "B"
        settled_rows.append(row)
    elif filled or any(resting.get(l["tk"]) for l in legs):
        # live: achievable combined
        mm=mkt([l["tk"] for l in legs])
        for l in legs:
            l["ask"]=mm.get(l["tk"],{}).get("yes_ask")
        f1=[l for l in filled if l["open_qty"]]
        ach=None
        if len(f1)==1:
            sib=[l for l in legs if l is not f1[0]]
            if sib and sib[0].get("ask"): ach=round(f1[0]["vw"]+sib[0]["ask"],1)
        row["achievable"]=ach
        row["half_arm"]=(len(f1)==1 and not any(l["resting"] or l["open_qty"] for l in legs if l is not f1[0]))
        live_rows.append(row)

json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
           "boundaries":{"B_FLIP":hm(B_FLIP),"B_GUARDS":hm(B_GUARDS),"B_DISARM":hm(B_DISARM)},
           "settled":settled_rows,"live":live_rows,
           "manual_excluded":sorted(manual)},
          open("/tmp/trade_roll.json","w"),default=str)
print(f"settled events={len(settled_rows)} live={len(live_rows)} manual excluded={len(manual)}",file=sys.stderr)
