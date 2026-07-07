#!/usr/bin/env python3
"""[READ-ONLY] POSITION RECONCILE vs KALSHI — live REST vs the ledger HELD set (00:18 read).
Every ticker in either source classified: MATCH / LEDGER-ONLY(named) / EXCHANGE-ONLY
(manual first, then new-since-cut, then UNTRACKED loud). Headline numbers to the penny.
Writes /tmp/pos_reconcile.json."""
import json, time, base64, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
SNAP_TS = datetime(2026,7,7,0,18,15,tzinfo=ET).timestamp()
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests
pk = serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(), password=None, backend=default_backend())
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

bal=g("/portfolio/balance")
pos=[]; cursor=""
for _ in range(40):
    p="/portfolio/positions?limit=200&settlement_status=unsettled"+(f"&cursor={cursor}" if cursor else "")
    r=g(p); pos+=r.get("market_positions",[])
    cursor=r.get("cursor")
    if not cursor: break
fills=[]; cursor=""
for _ in range(40):
    p=f"/portfolio/fills?limit=200&min_ts={int(SNAP_TS)}"+(f"&cursor={cursor}" if cursor else "")
    r=g(p); fills+=r.get("fills",[])
    cursor=r.get("cursor")
    if not cursor: break
setts=[]; cursor=""
for _ in range(10):
    p="/portfolio/settlements?limit=200"+(f"&cursor={cursor}" if cursor else "")
    r=g(p); batch=r.get("settlements",[])
    setts+=batch; cursor=r.get("cursor")
    if not cursor or not batch: break
    try:
        if datetime.fromisoformat(batch[-1]["settled_time"].replace("Z","+00:00")).timestamp()<SNAP_TS: break
    except: break
setts=[s for s in setts if datetime.fromisoformat(s["settled_time"].replace("Z","+00:00")).timestamp()>=SNAP_TS]

led=json.load(open("/tmp/slate_ledger.json"))
manual=set(led["manual_excluded"])
held={}
for r in led["rows"]:
    for l in r["legs"]:
        if l.get("open_qty"):
            tk="KX"+l["tk"] if not l["tk"].startswith("KX") else l["tk"]
            held[tk]={"qty":l["open_qty"],"basis":l["vw"],"mark_bid":l.get("bid")}
ex={}
for p_ in pos:
    q=float(p_.get("position_fp") or 0)
    if q==0: continue
    ex[p_["ticker"]]={"qty":q,"cost":float(p_.get("market_exposure_dollars") or 0)}
# live marks for exchange positions
tks=sorted(ex)
mk={}
for i in range(0,len(tks),90):
    r=g("/markets?tickers="+",".join(tks[i:i+90])+"&limit=100")
    for m in r.get("markets",[]):
        bd=m.get("yes_bid_dollars")
        mk[m["ticker"]]=float(bd)*100 if bd else None
new_since=set(f["ticker"] for f in fills if f.get("action")=="buy")
sold_since=set(f["ticker"] for f in fills if f.get("action")=="sell")
settled_since=set(s["ticker"] for s in setts)

rows=[]; cls=defaultdict(int)
val={"bot":0.0,"manual":0.0}
for tk in sorted(set(held)|set(ex)):
    h=held.get(tk); e=ex.get(tk)
    mark_now=(mk.get(tk) or 0)*(e["qty"] if e else 0)/100.0
    if e:
        val["manual" if (tk in manual or "MATCH-" not in tk) else "bot"]+=mark_now
    if h and e:
        c="MATCH" if abs(h["qty"]-e["qty"])<0.01 else "QTY-DRIFT(fills since cut)" if tk in new_since|sold_since else "QTY-MISMATCH"
    elif h and not e:
        c=("LEDGER-ONLY: settled since cut" if tk in settled_since else
           "LEDGER-ONLY: exited since cut" if tk in sold_since else "LEDGER-ONLY: STALE?")
    else:
        c=("EXCHANGE-ONLY: MANUAL (excluded set)" if tk in manual or "MATCH-" not in tk else
           "EXCHANGE-ONLY: new since cut (overnight fills)" if tk in new_since else
           "EXCHANGE-ONLY: UNTRACKED !!")
    cls[c.split(":")[0].split("(")[0].strip()]+=1
    rows.append({"tk":tk[-26:],"cls":c,
                 "led_qty":h and h["qty"],"led_basis":h and h["basis"],
                 "ex_qty":e and e["qty"],"ex_cost":e and round(e["cost"],2),
                 "mark_now":round(mark_now,2)})
# cash decomposition since snapshot
buys=sum(float(f["yes_price_dollars"])*float(f["count_fp"]) for f in fills if f["action"]=="buy")
sells=sum(float(f["yes_price_dollars"])*float(f["count_fp"]) for f in fills if f["action"]=="sell")
fees=sum(float(f.get("fee_cost") or 0) for f in fills)+sum(float(s.get("fee_cost") or 0) for s in setts)
rev=sum(float(s.get("revenue") or 0)/100.0 for s in setts)
cash_now=float(bal.get("balance_dollars") or 0)
out={"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
     "cash_now":cash_now,"pv_now_c":bal.get("portfolio_value"),
     "classes":dict(cls),"rows":rows,"marks":val,
     "cash_decomp":{"snap_00_18":847.7388,"buys_since":round(buys,2),"sells_since":round(sells,2),
                    "settle_rev_since":round(rev,2),"fees_since":round(fees,2),
                    "predicted_now":round(847.7388-buys+sells+rev-fees,2)}}
json.dump(out,open("/tmp/pos_reconcile.json","w"))
print(f"cash {cash_now} pv {bal.get('portfolio_value')} | classes {dict(cls)} | marks bot {val['bot']:.2f} manual {val['manual']:.2f}",file=sys.stderr)
print(f"cash decomp: 847.74 -{buys:.2f} +{sells:.2f} +{rev:.2f} -{fees:.2f} = {847.7388-buys+sells+rev-fees:.2f} vs actual {cash_now}",file=sys.stderr)
for r in rows:
    if "UNTRACKED" in r["cls"] or "STALE" in r["cls"]: print("  !!",r,file=sys.stderr)
