#!/usr/bin/env python3
"""READ-ONLY per-tick premarket+corridor band report: Jurij Rodionov vs Oliver Crawford, Jun 22 ET.
depth_recorder subsecond book + Kalshi last-traded (normalized) + our resting-bid overlay. CSV + sha256."""
import os,time,base64,json,urllib.request,glob,gzip,datetime,hashlib,csv,statistics
from pathlib import Path
HERE=Path("/root/Omi-Workspace/arb-executor"); BASE="https://api.elections.kalshi.com"
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
    except Exception as e: return {"_err":str(e)}
def etstr(epoch): return datetime.datetime.fromtimestamp(epoch-4*3600,tz=datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-4]
# boundaries (ET) -> epoch (ET=UTC-4)
def et2ep(s):  # 'YYYY-MM-DD HH:MM:SS'
    return datetime.datetime.fromisoformat(s+"+00:00").timestamp()+4*3600
W1=et2ep("2026-06-22 06:30:00")      # window-1 open (T-4h)
CORR=et2ep("2026-06-22 10:30:00")    # corridor open (scheduled start)
REAL=et2ep("2026-06-22 11:16:15")    # real start (match_live_detected)
EV="KXATPMATCH-26JUN22CRAROD"; LEGS={"ROD":"Jurij Rodionov","CRA":"Oliver Crawford"}
OURBID={  # (epoch_start, price) step path from live_v3 order_placed
 "ROD":[(et2ep("2026-06-22 06:30:08"),63),(et2ep("2026-06-22 07:11:36"),64),(et2ep("2026-06-22 08:32:34"),65),(et2ep("2026-06-22 09:00:49"),66),(et2ep("2026-06-22 10:21:18"),67),(et2ep("2026-06-22 11:16:16"),None)],
 "CRA":[(et2ep("2026-06-22 06:30:08"),30),(et2ep("2026-06-22 10:11:25"),31),(et2ep("2026-06-22 11:14:18"),"FILLED@31")],
}
SRC={"ROD":"staircase(no_trade_staircase) deep-cast, walked 63->67","CRA":"engagement_join->fallback_maker_clamp @31"}
def ourbid(leg,ep):
    cur=None
    for t,p in OURBID[leg]:
        if ep>=t: cur=p
    return cur
# settle time
setl={}
r=kget(f"/trade-api/v2/markets/trades?ticker={EV}-ROD&limit=1")  # warm
for sd in LEGS:
    s=kget(f"/trade-api/v2/markets/{EV}-{sd}")
    m=s.get("market",{}); st=m.get("close_time") or m.get("settlement_time")
    setl[sd]=None
SETTLE_EP=et2ep("2026-06-22 14:00:00")  # generous end bound (well past real start)
# depth per leg
files=sorted(glob.glob(str(HERE/"data/durable/depth_recorder/depth_20260622_*.jsonl.gz")))
depth={"ROD":[],"CRA":[]}
for f in files:
    with gzip.open(f,"rt") as fh:
        for line in fh:
            if "CRAROD" not in line: continue
            try: d=json.loads(line)
            except: continue
            tk=d.get("ticker","");
            if not tk.startswith(EV+"-"): continue
            sd=tk.rsplit("-",1)[1]
            if sd not in depth: continue
            bb=d.get("bid"); ba=d.get("ask")
            bd={int(p):int(s) for p,s in (d.get("bids") or [])}; ad={int(p):int(s) for p,s in (d.get("asks") or [])}
            depth[sd].append((d["ts_epoch"],bb,ba,bd.get(bb,0) if bb else 0,ad.get(ba,0) if ba else 0))
for sd in depth: depth[sd].sort()
# trades per leg (normalized: yes->buy, no->sell)
def trades(sd):
    out=[]; cur=None
    for _ in range(30):
        r=kget(f"/trade-api/v2/markets/trades?ticker={EV}-{sd}&min_ts={int(W1)}&max_ts={int(SETTLE_EP)}&limit=1000"+(f"&cursor={cur}" if cur else ""))
        out+=r.get("trades",[]); cur=r.get("cursor")
        if not cur: break
    ev=[]
    for t in out:
        try: te=datetime.datetime.fromisoformat(t["created_time"].replace("Z","+00:00")).timestamp()
        except: continue
        yp=t.get("yes_price_dollars"); px=round(float(yp)*100) if yp is not None else (100-round(float(t["no_price_dollars"])*100) if t.get("no_price_dollars") else None)
        side="buy" if t.get("taker_side")=="yes" else ("sell" if t.get("taker_side")=="no" else "?")
        ev.append((te,px,round(float(t.get("count_fp",0) or 0)),side))
    ev.sort(); return ev
TR={sd:trades(sd) for sd in LEGS}
# build per-tick CSV: each depth tick + most-recent trade
rows=[]
for sd in LEGS:
    tr=TR[sd]; ti=0; lastp=lastq=None; lasts=""
    for ep,bb,ba,bd,ad in depth[sd]:
        while ti<len(tr) and tr[ti][0]<=ep:
            lastp,lastq,lasts=tr[ti][1],tr[ti][2],tr[ti][3]; ti+=1
        rows.append(dict(ts_ET=etstr(ep),leg=LEGS[sd],best_bid=bb,best_ask=ba,bid_depth=bd,ask_depth=ad,
            last_traded_price=lastp,last_traded_side=lasts,last_traded_size=lastq,our_bid=ourbid(sd,ep),
            phase=("window1" if ep<CORR else "corridor" if ep<REAL else "in_play")))
rows.sort(key=lambda r:(r["ts_ET"],r["leg"]))
outp=str(HERE/"data/durable/crawford_rodionov_band_2026-06-22.csv")
cols=["ts_ET","leg","phase","best_bid","best_ask","bid_depth","ask_depth","last_traded_price","last_traded_side","last_traded_size","our_bid"]
with open(outp,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore"); w.writeheader()
    for r in rows: w.writerow(r)
sha=hashlib.sha256(open(outp,"rb").read()).hexdigest()
# FV reads
def fv(sd,end,lab):
    seg=[p for te,p,q,s in TR[sd] if end-60<=te<=end and p is not None]
    close=[(te,p) for te,p,q,s in TR[sd] if p is not None and te<=end]
    ct=close[-1] if close else None
    return (statistics.median(seg) if seg else None, len(seg), (etstr(ct[0]),ct[1]) if ct else None)
# decisive extract: Rodionov
rod_w1=[(te,p) for te,p,q,s in TR["ROD"] if W1<=te<CORR and p is not None]
low_lt=min(rod_w1,key=lambda x:x[1]) if rod_w1 else None
sells=[(te,p,q) for te,p,q,s in TR["ROD"] if W1<=te<REAL and s=="sell" and p is not None]
low_sell=min(sells,key=lambda x:x[1]) if sells else None
# cumulative sell at the lowest sell level
cum_at_low=sum(q for te,p,q in sells if low_sell and p<=low_sell[1])
print("================ BAND REPORT SUMMARY: Jurij Rodionov vs Oliver Crawford (ATP, Jun 22 ET) ================")
print(f"event=KXATPMATCH-26JUN22CRAROD  legs: ROD=Jurij Rodionov, CRA=Oliver Crawford")
print(f"boundaries ET: window-1 open 06:30:00 | corridor open (scheduled) 10:30:00 | real start 11:16:15")
print(f"depth source files: {len(files)} hourly gz (depth_20260622_*.jsonl.gz); rows: ROD ticks={len(depth['ROD'])} CRA ticks={len(depth['CRA'])}")
print(f"trades: ROD={len(TR['ROD'])} CRA={len(TR['CRA'])}  | CSV rows={len(rows)}")
for sd in ("ROD","CRA"):
    pre=fv(sd,CORR,"pre"); post=fv(sd,REAL,"post")
    print(f"\n[{LEGS[sd]}] our cast: {SRC[sd]}")
    print(f"  FV_pre  (median last-traded final 60s before corridor open 10:30): {pre[0]} (n={pre[1]})  closing tick {pre[2]}")
    print(f"  FV_post (median last-traded final 60s before real start 11:16:15): {post[0]} (n={post[1]})  closing tick {post[2]}")
print("\n--- DECISIVE: Jurij Rodionov 'why no fill' (window-1 + corridor) ---")
print(f"  our Rodionov resting bid path: 63 -> 64 -> 65 -> 66 -> 67 (deep cast 63, walked up; cancelled at real start, NEVER filled)")
print(f"  lowest last-traded in window-1: {low_lt[1]}c @ {etstr(low_lt[0])}" if low_lt else "  no window-1 trades")
print(f"  lowest price level reached by taker-NO SELL flow (W1->real): {low_sell[1]}c @ {etstr(low_sell[0])} (cum sell<=level: {cum_at_low})" if low_sell else "  no sell flow")
# TIME-ALIGNED: did any taker-NO sell trade at or below OUR bid at that instant?
reaching=[(te,p,q) for te,p,q,s in TR["ROD"] if W1<=te<REAL and s=="sell" and p is not None and ourbid("ROD",te) is not None and p<=ourbid("ROD",te)]
cum_reach=sum(q for te,p,q in reaching)
print(f"  TIME-ALIGNED test (sell price <= OUR bid at that instant): {len(reaching)} such sells, cum size {cum_reach}")
if reaching:
    for te,p,q in reaching[:5]: print(f"    sell {p}c x{q} @ {etstr(te)} (our bid then {ourbid('ROD',te)}c)")
    print(f"  -> a worked bid COULD have caught flow ({cum_reach} contracts reached our band)")
else:
    print(f"  -> NO taker-NO sell ever traded at/below our resting bid. Rodionov ONLY FIRMED (lowest trade {low_lt[1] if low_lt else '?'}c stayed above our 63->67 cast the whole window).")
# Crawford fill location
cf=et2ep("2026-06-22 11:14:18")
loc="window-1" if cf<CORR else ("corridor (post-scheduled, pre-real-start)" if cf<REAL else "post-gun")
print(f"\n--- Oliver Crawford fill location: @31c at 11:14:18 ET -> {loc}  (exit cfg: resting sell @38, band 7) ---")
print(f"\nCSV: {outp}\nsha256: {sha}")
