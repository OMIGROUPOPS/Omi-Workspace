"""READ-ONLY Lever-3 sizing: RUN-5 (26JUN02, 83e08395 cohort) pre-match TAKER reach. Of RUN-5's
fills, how many were taker (the T-20m fallback lifting the ask to enter), the PREMIUM paid over the
intended maker target_bid, and the realized P&L (exit_filled / settled) — does the exit edge cover
the taker premium? Sizes whether restoring a pre-T-15m fallback (at corrected prices) nets positive.
is_taker from /fills (ground truth); target_bid + pnl from the RUN-5 session log."""
import time, base64, requests, json, glob
from pathlib import Path
from collections import defaultdict
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
PK=serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(),password=None,backend=default_backend())
AK="f3b064d1-a02e-42a4-b2b1-132834694d23"; BASE="https://api.elections.kalshi.com"
def sign(ts,m,p): return base64.b64encode(PK.sign((ts+m+p).encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())).decode()
def gx(p):
    ts=str(int(time.time()*1000)); h={"KALSHI-ACCESS-KEY":AK,"KALSHI-ACCESS-SIGNATURE":sign(ts,"GET",p.split("?")[0]),"KALSHI-ACCESS-TIMESTAMP":ts}
    r=requests.get(BASE+p,headers=h,timeout=25); return r.json() if r.status_code==200 else {}

fills=[]; cur=""
for _ in range(40):
    d=gx("/trade-api/v2/portfolio/fills?limit=500"+("&cursor="+cur if cur else "")); fills+=d.get("fills",[]); cur=d.get("cursor","")
    if not cur: break
# RUN-5 cohort = 26JUN02 buys
buy=defaultdict(list)
for f in fills:
    if "26JUN02" in f.get("ticker","") and f["action"]=="buy": buy[f["ticker"]].append(f)

# RUN-5 session log: target_bid (v4_place), fill_price (entry_filled), realized pnl (exit_filled/settled)
target={}; fillpx={}; pnl=defaultdict(float); ptype={}
for lf in sorted(glob.glob("logs/live_v3_2026060*.jsonl")):
    for l in open(lf,errors="replace"):
        if '"event"' not in l or "26JUN02" not in l: continue
        try: r=json.loads(l)
        except: continue
        e=r.get("event"); tk=r.get("ticker",""); d=r.get("details",{})
        if "26JUN02" not in tk: continue
        if e=="v4_place": target[tk]=d.get("target_bid")
        elif e=="entry_filled": fillpx[tk]=d.get("fill_price"); ptype[tk]=d.get("play_type")
        elif e=="exit_filled": pnl[tk]+=float(d.get("pnl_dollars",0))
        elif e=="settled": pnl[tk]+=float(d.get("pnl_dollars",0))

rows=[]
for tk,fs in buy.items():
    taker = any(x["is_taker"] for x in fs)
    fp = round(float(fs[0]["yes_price_dollars"])*100) if fs[0].get("outcome_side")=="yes" else round(float(fs[0]["no_price_dollars"])*100)
    tgt = target.get(tk); prem = (fp - tgt) if tgt is not None else None
    rows.append(dict(tk=tk,leg=tk.rsplit("-",1)[1],taker=taker,fp=fp,tgt=tgt,prem=prem,pnl=pnl.get(tk,0.0),pt=ptype.get(tk,"?")))

tk_rows=[r for r in rows if r["taker"]]
mk_rows=[r for r in rows if not r["taker"]]
prem_rows=[r for r in tk_rows if r["prem"] is not None]
import statistics as st
print("="*92)
print("RUN-5 (26JUN02) FILL BREAKDOWN — taker reach sizing")
print("="*92)
print("  total RUN-5 buy-fills: %d  | TAKER: %d (%.0f%%)  maker: %d" % (
    len(rows), len(tk_rows), 100*len(tk_rows)/len(rows) if rows else 0, len(mk_rows)))
if prem_rows:
    prems=[r["prem"] for r in prem_rows]
    print("  TAKER premium over intended maker target (fill - target_bid): mean %+.1fc median %+.0fc max %+dc" % (
        st.mean(prems), st.median(prems), max(prems)))
def book(rs,label):
    if not rs: print("  %s: none" % label); return
    p=[r["pnl"] for r in rs]; pos=sum(1 for x in p if x>0)
    print("  %s (n=%d): realized P&L sum $%.2f  mean $%.3f/leg  win %d/%d (%.0f%%)" % (
        label,len(rs),sum(p),sum(p)/len(rs),pos,len(rs),100*pos/len(rs)))
book(tk_rows,"TAKER fills")
book(mk_rows,"MAKER fills")
print("\n  taker-reach legs (premium vs P&L):")
for r in sorted(tk_rows,key=lambda x:x["pnl"])[:18]:
    print("    %-30s fill=%s tgt=%s prem=%s pnl=$%.2f %s" % (r["leg"],r["fp"],r["tgt"],("%+d"%r["prem"]) if r["prem"] is not None else "?",r["pnl"],r["pt"][:14]))
print("\n  VERDICT: taker reach nets positive iff TAKER P&L mean > 0 despite the premium.")
