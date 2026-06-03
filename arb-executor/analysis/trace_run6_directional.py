#!/usr/bin/env python3
"""READ-ONLY RUN-6 directional tape analysis (26JUN03, post-06:28Z). For each placed leg:
classify ACTUAL price path (rise/dip/flat) from the full trade tape, validate the favorite=rise/
underdog=dip prior, size the dip-bottom (where a resting bid should sit) and the rise early-entry,
and split the (e) 'no-flow' legs into rise-legs (recoverable by early placement) vs true deserts.
Also: do the dip-bottom prints land before or after T-15m (the buffer question)."""
import time, base64, requests, json, glob
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import statistics as st
PK=serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(),password=None,backend=default_backend())
AK="f3b064d1-a02e-42a4-b2b1-132834694d23"; BASE="https://api.elections.kalshi.com"
def sign(ts,m,p): return base64.b64encode(PK.sign((ts+m+p).encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())).decode()
def gx(p):
    ts=str(int(time.time()*1000)); h={"KALSHI-ACCESS-KEY":AK,"KALSHI-ACCESS-SIGNATURE":sign(ts,"GET",p.split("?")[0]),"KALSHI-ACCESS-TIMESTAMP":ts}
    r=requests.get(BASE+p,headers=h,timeout=25); return r.json() if r.status_code==200 else {}
def ep(iso): return datetime.strptime(iso[:19],"%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()

LOGS=sorted(glob.glob("logs/live_v3_2026060*.jsonl")); B=0.0
for lf in LOGS:
    for l in open(lf,errors="replace"):
        if '"system_start"' in l:
            try: B=max(B,json.loads(l).get("ts_epoch",0))
            except: pass
target={}; direction={}; cell={}; match_start={}; filled=set()
for lf in LOGS:
    for l in open(lf,errors="replace"):
        if '"event"' not in l: continue
        try: r=json.loads(l)
        except: continue
        if r.get("ts_epoch",0)<B: continue
        e=r.get("event"); tk=r.get("ticker",""); d=r.get("details",{})
        if "26JUN03" not in (tk or d.get("event","")): continue
        if e=="v4_place": target[tk]=d.get("target_bid"); direction[tk]=d.get("direction"); cell[tk]=d.get("current_price")
        elif e=="entry_filled": filled.add(tk)
        elif e=="entry_cancelled": match_start[tk]=d.get("match_start",match_start.get(tk,0))

def tape(tk, lo, hi):
    out=[]; cur=""
    for _ in range(12):
        d=gx("/trade-api/v2/markets/trades?ticker=%s&limit=1000&min_ts=%d&max_ts=%d"%(tk,int(lo),int(hi))+("&cursor="+cur if cur else ""))
        for t in d.get("trades",[]):
            out.append((ep(t["created_time"]), round(float(t["yes_price_dollars"])*100), t.get("taker_side")))
        cur=d.get("cursor","")
        if not cur: break
    return sorted(out)

legs=[t for t in target if "-" in t]
rows=[]
for tk in legs:
    ms=match_start.get(tk,0)
    if not ms: continue
    lo=ms-5*3600; hi=ms
    tp=tape(tk,lo,hi)
    n=len(tp); tgt=target[tk]; dr=direction.get(tk); t15=ms-15*60
    sy=[(ts,yp) for ts,yp,sd in tp if sd=="no"]            # sell-yes prints (fill our yes bid)
    prices=[yp for _,yp,_ in tp]
    if n>=4:
        third=max(1,n//3)
        early=st.median(prices[:third]); late=st.median(prices[-third:])
        delta=late-early
        actual = "RISE" if delta>=3 else ("DIP" if delta<=-3 else "flat")
    else:
        early=late=delta=None; actual="thin"
    prior = "RISE" if dr=="leader" else ("DIP" if dr=="underdog" else "?")
    pmin = min(prices) if prices else None
    pmin_ts = min((ts for ts,yp,_ in tp if yp==pmin), default=None) if pmin is not None else None
    symin = min((yp for _,yp in sy), default=None)
    reached = symin is not None and symin<=tgt
    rows.append(dict(tk=tk,leg=tk.rsplit("-",1)[1],dr=dr,prior=prior,cell=cell.get(tk),tgt=tgt,
        n=n,early=early,late=late,delta=delta,actual=actual,pmin=pmin,symin=symin,
        pmin_ts=pmin_ts,t15=t15,ms=ms,reached=reached,filled=(tk in filled)))

# ---- A) prior accuracy ----
det=[r for r in rows if r["actual"] in ("RISE","DIP")]
correct=sum(1 for r in det if r["actual"]==r["prior"])
print("="*100)
print("A) DIRECTIONAL PRIOR vs ACTUAL TAPE PATH")
print("  legs with determinable path: %d / %d (rest thin/flat)" % (len(det), len(rows)))
print("  prior (favorite=RISE / underdog=DIP) CORRECT: %d/%d = %.0f%%" % (correct,len(det),100*correct/len(det) if det else 0))
mism=[r for r in det if r["actual"]!=r["prior"]]
print("  mispredicted (%d):" % len(mism))
for r in mism: print("     %-8s label=%-8s cell=%s  prior=%s actual=%s (%s->%s)" % (r["leg"],r["dr"],r["cell"],r["prior"],r["actual"],r["early"],r["late"]))

# ---- B-dip) where dips actually bottom, + #1 timing ----
print("\nB-dip) DIP legs (by actual path) — actual print-low vs current target, and bottom-ts vs T-15m")
print("  %-8s %4s %4s %5s %6s %9s" % ("leg","cell","tgt","pmin","shallow","bottom_vs_T15"))
dips=[r for r in rows if r["actual"]=="DIP"]
pre=post=0
for r in sorted(dips,key=lambda x:x["cell"] or 0):
    shal = (r["pmin"]-r["tgt"]) if (r["pmin"] is not None and r["tgt"] is not None) else None
    tcmp = "?"
    if r["pmin_ts"] is not None:
        tcmp = "PRE-T15 (%.0fm)"%((r["ms"]-r["pmin_ts"])/60) if r["pmin_ts"]<r["t15"] else "post-T15 (%.0fm)"%((r["ms"]-r["pmin_ts"])/60)
        if r["pmin_ts"]<r["t15"]: pre+=1
        else: post+=1
    print("  %-8s %4s %4s %5s %6s %9s" % (r["leg"],r["cell"],r["tgt"],r["pmin"],("+%d"%shal) if shal is not None else "?",tcmp))
print("  -> dip-bottom timing: PRE-T15=%d  post-T15=%d  (post-T15 => needs buffer fix too)" % (pre,post))

# ---- B-rise) split the no-reach legs into RISE (recoverable) vs DESERT ----
print("\nB-rise) the 'never reached us' legs (sell-yes never printed <= target): RISE vs DESERT")
noreach=[r for r in rows if not r["reached"] and not r["filled"]]
rise_rec=[r for r in noreach if r["actual"]=="RISE"]
desert=[r for r in noreach if r["actual"] in ("thin","flat")]
dip_butdeep=[r for r in noreach if r["actual"]=="DIP"]
print("  no-reach legs: %d" % len(noreach))
print("    RISE legs (flow went to sibling; recoverable by EARLY at-market placement): %d" % len(rise_rec))
for r in rise_rec: print("       %-8s cell=%s tgt=%s path %s->%s (early entry ~%s before rise)" % (r["leg"],r["cell"],r["tgt"],r["early"],r["late"],r["early"]))
print("    DIP legs that stayed >target (too deep, dip came but short): %d" % len(dip_butdeep))
print("    thin/flat DESERTS (no usable flow either way): %d" % len(desert))
print("\nDECISIVE SPLIT of the no-flow set: RISE-recoverable=%d  too-deep-dip=%d  true-desert=%d" % (
    len(rise_rec),len(dip_butdeep),len(desert)))
