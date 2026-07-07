#!/usr/bin/env python3
"""[READ-ONLY] SLATE LEDGER — the authoritative single book, flip boot -> now.
Extends trade_roll.py (same exchange-truth pulls, same exclusions) with:
  - settled_time per ticker -> timestamp CUTS (continuity proof vs -9.33 and -16.05)
  - OPEN rows mark-to-book (basis, live bid, achievable combined now)
  - BOUHAR stamps (both legs W1_CASHED)
  - one table, settled AND open together
Canonical $ rule: SETTLEMENT-REALIZED per ticker = revenue + sells - buys - fees
(exchange only; an exited-but-unsettled leg is OPEN with realized-so-far cash noted).
Writes /tmp/slate_ledger.json."""
import json, time, base64, sys, re, gzip
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
B_FLIP, B_GUARDS, B_DISARM = 1783309839.0, 1783354522.0, 1783365958.0
CUT_A = datetime(2026,7,6,11,13,tzinfo=ET).timestamp()   # autopsy exchange pull
CUT_B = datetime(2026,7,6,15,47,tzinfo=ET).timestamp()   # 15:52 roll pull
CUT_C = datetime(2026,7,6,16,28,tzinfo=ET).timestamp()   # the 16:28 book (target -19.65/197)
CUT_D = datetime(2026,7,7,0,18,15,tzinfo=ET).timestamp() # prior SLATE_LEDGER generation (target -15.05)
GOAL = 97
LOGS = ["/tmp/session_since_boot.jsonl", "logs/live_v3_20260706.jsonl", "logs/live_v3_20260707.jsonl"]
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

posts=defaultdict(list); exitfill={}; manual=set(); vstamp={}; latch={}
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
            _mts=globals().setdefault("manual_ts",{})
            _mts[tk]=min(_mts.get(tk,ts or 9e18), ts or 9e18)
        elif e=="match_live_detected":
            _ev=d.get("event")
            if _ev and _ev not in latch: latch[_ev]=ts
if Path(VALID).exists():
    for line in open(VALID,encoding="utf-8",errors="replace"):
        try: o=json.loads(line)
        except: continue
        if o.get("type") in ("fill","fill_regrade") and o.get("ticker"):
            cur=vstamp.get(o["ticker"],{})
            cur.update({k:o[k] for k in ("aim_level","fill_minus_aim") if o.get(k) is not None})
            vstamp[o["ticker"]]=cur

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
    if not cursor: break
pos_rows=[]; cursor=""
for _ in range(40):
    p="/portfolio/positions?limit=200&settlement_status=unsettled"+(f"&cursor={cursor}" if cursor else "")
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
print(f"fills tks={len(fills)} setts={len(setts)} pos={len(pos_rows)} orders={len(orders)}",file=sys.stderr)

# [STEP-3 FIX v2, continuity-preserving] the 10:21 ET 07-07 containment boot mass-adopted
# cross-boot orphan fills with attribution="manual" (memory empty after restart) -- 256
# stamps vs the ratified 39. Rescue ONLY legs whose manual stamp originates at/after that
# boot AND that have bot order_placed posts on record; every pre-boot manual stamp keeps
# the ratified exclusion (CUT A/B/C/D must reproduce).
# boundary = the prior ledger's generation (00:18:15 ET 07-07): its 39-manual set is the
# ratified baseline; every stamp after it came from the overnight/containment restart waves.
_BOOT_0721 = datetime(2026,7,7,0,18,15,tzinfo=ET).timestamp()
_mts = globals().get("manual_ts", {})
manual = set(t for t in manual
             if _mts.get(t, 0) < _BOOT_0721 or not posts.get(t))
def is_bot(tk): return "MATCH-" in tk and tk not in manual
def buy_vwap(tk):
    ct=px=0.0; first=None
    for f in fills.get(tk,[]):
        if f.get("action")!="buy": continue
        c=float(f.get("count_fp") or 0); pxx=float(f.get("yes_price_dollars") or 0)*100
        ct+=c; px+=c*pxx
        t=datetime.fromisoformat(f["created_time"].replace("Z","+00:00")).timestamp()
        first=t if first is None else min(first,t)
    return (round(px/ct,1),ct,first) if ct else (None,0,None)
def cash(tk, until=None):
    b=s=fee=0.0
    for f in fills.get(tk,[]):
        t=datetime.fromisoformat(f["created_time"].replace("Z","+00:00")).timestamp()
        if until and t>until: continue
        v=float(f.get("yes_price_dollars") or 0)*float(f.get("count_fp") or 0)
        if f.get("action")=="buy": b+=v
        else: s+=v
        fee+=float(f.get("fee_cost") or 0)
    return b,s,fee
def sett_of(tk):
    s=setts.get(tk)
    if not s: return None,None
    t=datetime.fromisoformat(s["settled_time"].replace("Z","+00:00")).timestamp()
    return float(s.get("revenue") or 0)/100.0 + float(s.get("fee_cost") or 0)*-1, t
def tk_pnl(tk, cut=None):
    s=setts.get(tk)
    if not s: return None
    st=datetime.fromisoformat(s["settled_time"].replace("Z","+00:00")).timestamp()
    if cut and st>cut: return None
    rev=float(s.get("revenue") or 0)/100.0
    b,sl,fee=cash(tk, cut)
    return round(rev+sl-b-fee-float(s.get("fee_cost") or 0),2)

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
def read_tape_rows(tk):
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
            try: rows.append((t,int(p[2]),int(float(p[3]))))
            except: continue
    rows.sort(); return rows
def tape_gun_rows(rows, w0, w1):
    rr=[r for r in rows if w0<=r[0]<=w1]
    if not rr: return None
    mv=defaultdict(float)
    for t,pr,ct in rr: mv[int(t//60)*60]+=ct
    mins=sorted(mv)
    fwd={m:sum(mv[x] for x in mins if m<=x<m+600) for m in mins}
    return next((m for m in mins if mv[m]>=150 and fwd[m]>=3000), None)
CORR_EST={"ITF_M":72,"ITF_W":77,"ATP_CHALL":19,"WTA_CHALL":5,"ATP_MAIN":30,"WTA_MAIN":30}
def sell_fills(tk):
    out=[]
    for f in fills.get(tk,[]):
        if f.get("action")!="sell": continue
        t=datetime.fromisoformat(f["created_time"].replace("Z","+00:00")).timestamp()
        out.append((t,float(f.get("count_fp") or 0)))
    return sorted(out)
exitpx={}
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for line in open(LOG,encoding="utf-8",errors="replace"):
        if '"v4_exit_posted"' not in line: continue
        try: o=json.loads(line)
        except: continue
        tk=o.get("ticker")
        if tk and tk not in exitpx: exitpx[tk]=o.get("details",{}).get("exit_price")

# [STEP-3] MECHANICAL flag per leg from BLEED_ATTRIBUTION_20260707 (classes a/b/c, $)
try:
    _bl=json.load(open("/root/bleed_attribution_20260707.json"))
except Exception:
    _bl={"class_a":{},"class_b":{},"class_c":{}}
def mech_of(tk):
    m={}
    a=_bl["class_a"].get(tk)
    if a: m["a"]=round((a["mech_realized_c"]+a["mech_mark_c"])/100,2); m["a_sh"]=a["surplus_qty"]
    b=_bl["class_b"].get(tk)
    if b: m["b"]=round(-b["delta_c"]/100,2); m["b_band"]=b["band"]; m["b_sh"]=b["naked_qty"]
    c=_bl["class_c"].get(tk)
    if c: m["c"]=round(c["c"]/100,2)
    return m or None
all_tks=set(t for t in set(list(fills)+list(posts)) if is_bot(t))
evs=defaultdict(list)
for tk in all_tks: evs[tk.rsplit("-",1)[0]].append(tk)
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

rows=[]
for ev,tks in sorted(evs.items()):
    cat=cat_of(ev+"-") or "?"
    hs=honest_start(ev)
    # corridor end: unambiguous onset (hs-30m..hs+8h) > latch > hs + cat-median est
    _tapes={tk: read_tape_rows(tk) for tk in sorted(set(tks))}
    onset=None
    if hs:
        for _tk,_rows in _tapes.items():
            gnn=tape_gun_rows(_rows, hs-1800, hs+8*3600)
            if gnn and (onset is None or gnn<onset): onset=gnn
    cor_end = onset or latch.get("KX"+ev if not ev.startswith("KX") else ev) or latch.get(ev) or ((hs+60*CORR_EST.get(cat,30)) if hs else None)
    legs=[]
    for tk in sorted(set(tks)):
        vw,q,ft=buy_vwap(tk)
        p0=sorted(posts.get(tk,[]))
        conc=p0[0][0] if p0 else ft
        pnl,st_t=tk_pnl(tk),(sett_of(tk)[1])
        w1="—"
        if vw is not None and hs and ft and ft<hs:
            xf=exitfill.get(tk)
            if xf and xf<hs: w1="W1_CASHED"
            elif exitpx.get(tk) and band_touch_pre(tk,exitpx[tk],hs): w1="W1_REACHABLE"
            else: w1="W2_ONLY"
        elif vw is not None: w1="W2_ONLY" if hs else "no-clock"
        oq=float((open_pos.get(tk) or {}).get("position_fp") or 0)
        b,sl,fee=cash(tk)
        sf=sell_fills(tk)
        settled_flag = pnl is not None
        if sf:
            t0=sf[0][0]
            if hs and t0<hs: disp="EXIT_FILLED_W1"
            elif cor_end and t0<cor_end: disp="EXIT_FILLED_CORRIDOR"
            else: disp="EXIT_FILLED_W2"
        elif settled_flag and vw is not None: disp="RODE_TO_SETTLEMENT"
        elif vw is not None: disp="OPEN"
        else: disp="—"
        # band touched-not-filled per window (only meaningful when no sell fill)
        touch={"W1":False,"COR":False,"W2":False}
        if vw is not None and not sf and exitpx.get(tk) is not None:
            lvl=exitpx[tk]
            for t,pr,ct in _tapes.get(tk,[]):
                if hs and t<hs: w="W1"
                elif cor_end and t<cor_end: w="COR"
                else: w="W2"
                if pr>=lvl: touch[w]=True
        legs.append({"tk":tk,"suf":tk.rsplit("-",1)[-1],"vw":vw,"qty":q,"fill_ts":ft,
                     "conc_ts":conc,"conc_e":epoch_of(conc),
                     "daim":vstamp.get(tk,{}).get("fill_minus_aim"),
                     "w1":w1,"pnl":pnl,"sett_ts":st_t,"open_qty":oq,
                     "cash_out":round(sl-b-fee,2),
                     "disp":disp,"sells_qty":round(sum(q for _,q in sf),1),
                     "w1_filled":bool(hs and ft and ft<hs),
                     "touch":touch,"exit_lvl":exitpx.get(tk),
                     "resting":[{"px":round(float(o.get("yes_price_dollars") or 0)*100)} for o in resting.get(tk,[])],
                     "mech":mech_of(tk)})
    filled=[l for l in legs if l["vw"] is not None]
    engaged=bool(filled or any(l["resting"] for l in legs) or any(posts.get(l["tk"]) for l in legs))
    if not engaged: continue
    comb=round(sum(l["vw"] for l in filled),1) if len(filled)==2 else None
    concs=[l["conc_ts"] for l in legs if l["conc_ts"]]
    ep=epoch_of(min(concs)) if concs else "?"
    spans=sorted(set(l["conc_e"] for l in legs if l["conc_ts"]))
    all_settled=bool(filled) and all(l["pnl"] is not None for l in filled) and not any(l["open_qty"] for l in legs)
    row={"ev":ev.replace("KX",""),"cat":cat,"epoch":ep,"spans":spans,"legs":legs,
         "hs_ts":hs,"cor_end_ts":cor_end,
         "combined":comb,"n_filled":len(filled),
         "bouhar":len(filled)==2 and all(l["w1"]=="W1_CASHED" for l in filled)}
    if all_settled:
        row["status"]="SETTLED"; row["pnl"]=round(sum(l["pnl"] for l in filled),2)
        row["sett_ts"]=max(l["sett_ts"] for l in filled)
        if len(filled)==1: row["grade"]="F" if row["pnl"]<0 else "D"
        elif comb is None: row["grade"]="?"
        elif comb>105: row["grade"]="D"
        elif comb>100: row["grade"]="C"
        elif comb>GOAL: row["grade"]="C"
        else:
            row["grade"]="A" if (all(l["w1"] in ("W1_CASHED","W1_REACHABLE") for l in filled) and row["pnl"]>=0) else "B"
    else:
        row["status"]="OPEN"
        mm=mkt([l["tk"] for l in legs])
        basis_cost=0.0; mark=0.0
        def _px(m,k):
            v=m.get(k)
            if v is not None: return v
            vd=m.get(k+"_dollars")
            return round(float(vd)*100) if vd is not None else None
        for l in legs:
            m=mm.get(l["tk"],{})
            l["bid"]=_px(m,"yes_bid"); l["ask"]=_px(m,"yes_ask")
            if l["open_qty"]:
                basis_cost+=l["open_qty"]*(l["vw"] or 0)/100.0
                mark+=l["open_qty"]*(l["bid"] or 0)/100.0
        row["open_basis"]=round(basis_cost,2); row["open_mark"]=round(mark,2)
        row["cash_partial"]=round(sum(l["cash_out"] for l in legs),2)
        held=[l for l in legs if l["open_qty"]]
        ach=None
        if len(held)==1:
            sib=[l for l in legs if l is not held[0]]
            if sib and sib[0].get("ask"): ach=round((held[0]["vw"] or 0)+sib[0]["ask"],1)
        row["achievable"]=ach
        row["grade"]="OPEN"
    rows.append(row)

# continuity cuts
def cut_sum(cut):
    tot=0.0; n=0; evl=[]
    for r in rows:
        fl=[l for l in r["legs"] if l["vw"] is not None and l["fill_ts"] and l["fill_ts"]<=cut]
        if not fl: continue
        pn=[tk_pnl(l["tk"],cut) for l in fl]
        if all(p is not None for p in pn) and not any(
                float((open_pos.get(l["tk"]) or {}).get("position_fp") or 0) for l in fl):
            s=round(sum(pn),2); tot+=s; n+=1; evl.append((r["ev"],s,hm(max(sett_of(l['tk'])[1] for l in fl))))
    return round(tot,2),n,evl
cutA,cutA_n,cutA_ev=cut_sum(CUT_A)
cutB,cutB_n,cutB_ev=cut_sum(CUT_B)
cutC,cutC_n,cutC_ev=cut_sum(CUT_C)
cutD,cutD_n,cutD_ev=cut_sum(CUT_D)
# [STEP-3 EXHIBIT] GOMOFN: did 16-17c print before the bell on GOM (the 21c fill)?
_gtk="KXATPCHALLENGERMATCH-26JUL07GOMOFN-GOM"
_ghs=honest_start("KXATPCHALLENGERMATCH-26JUL07GOMOFN")
_grows=read_tape_rows(_gtk)
_gpre=[r for r in _grows if _ghs and r[0]<_ghs]
_gfill=buy_vwap(_gtk)
gomofn={"fill_vwap":_gfill[0],"fill_qty":_gfill[1],
        "hs_et":hm(_ghs),"tape_rows_pre_bell":len(_gpre),
        "min_print_pre_bell":min((p for _,p,_ in _gpre),default=None),
        "prints_le17_pre_bell":sum(c for _,p,c in _gpre if p<=17),
        "prints_le16_pre_bell":sum(c for _,p,c in _gpre if p<=16),
        "first_le17_et":hm(next((t for t,p,_ in _gpre if p<=17),None))}
bal=g("/portfolio/balance")
json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
           "rows":rows,
           "cuts":{"A_1113":{"sum":cutA,"n":cutA_n},"B_1547":{"sum":cutB,"n":cutB_n},
                   "C_1628":{"sum":cutC,"n":cutC_n},"D_0018":{"sum":cutD,"n":cutD_n},
                   "A_events":cutA_ev,"B_events":cutB_ev,"C_events":cutC_ev},
           "gomofn":gomofn,
           "account_snapshot":{"pulled_at":datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
                               "cash":bal.get("balance_dollars"),"portfolio_value_c":bal.get("portfolio_value")},
           "manual_excluded":sorted(manual)},
          open("/tmp/slate_ledger_v2.json","w"),default=str)
st=[r for r in rows if r["status"]=="SETTLED"]; op=[r for r in rows if r["status"]=="OPEN"]
print(f"rows={len(rows)} settled={len(st)} open={len(op)}",file=sys.stderr)
print(f"LEDGER: settled ${sum(r['pnl'] for r in st):+.2f} | open basis ${sum(r.get('open_basis',0) for r in op):.2f} | open mark ${sum(r.get('open_mark',0) for r in op):.2f}",file=sys.stderr)
print(f"CUT A: {cutA}/{cutA_n} | CUT B: {cutB}/{cutB_n} | CUT C: {cutC}/{cutC_n} | CUT D 00:18: {cutD}/{cutD_n} (target -15.05) | bal {bal.get(chr(39)+chr(98)+chr(97)+chr(108)+chr(97)+chr(110)+chr(99)+chr(101)+chr(95)+chr(100)+chr(111)+chr(108)+chr(108)+chr(97)+chr(114)+chr(115)+chr(39))}",file=sys.stderr)
