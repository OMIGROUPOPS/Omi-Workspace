#!/usr/bin/env python3
"""READ-ONLY RUN-6 tape-vs-book overlay. For each placed 26JUN03 leg (post-06:28Z): reconstruct
our order's live-in-book intervals (order_placed->order_cancelled, with removal reason) and overlay
the ACTUAL trade tape (Kalshi /markets/trades, taker_side=no = sell-yes that fills our yes bid).
Decisive check per reaching print: were we resting at/above that level at that instant?
Buckets: (a) filled (b) queue-loss (c) not-live-when-print-came [+reason] (d) too-deep (e) never-came."""
import time, base64, requests, json, glob
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
PK=serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(),password=None,backend=default_backend())
AK="f3b064d1-a02e-42a4-b2b1-132834694d23"; BASE="https://api.elections.kalshi.com"
def sign(ts,m,p): return base64.b64encode(PK.sign((ts+m+p).encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())).decode()
def gx(p):
    ts=str(int(time.time()*1000)); h={"KALSHI-ACCESS-KEY":AK,"KALSHI-ACCESS-SIGNATURE":sign(ts,"GET",p.split("?")[0]),"KALSHI-ACCESS-TIMESTAMP":ts}
    r=requests.get(BASE+p,headers=h,timeout=25); return r.json() if r.status_code==200 else {}
def ep(iso):
    return datetime.strptime(iso[:19],"%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()

# ---- RUN-6 boundary ----
LOGS=sorted(glob.glob("logs/live_v3_2026060*.jsonl")); B=0.0
for lf in LOGS:
    for l in open(lf,errors="replace"):
        if '"system_start"' in l:
            try: B=max(B,json.loads(l).get("ts_epoch",0))
            except: pass

# ---- parse log: per-leg order intervals + reasons + target + match_start ----
placed=defaultdict(list)   # tk -> [(ts, price, oid)]
cancelled=defaultdict(list) # tk -> [(ts, oid, reason)]
target={}; match_start={}; vplace={}; filled_log=set()
rc_by_tk=defaultdict(list)  # ticker -> [(ts, kind)]
for lf in LOGS:
    for l in open(lf,errors="replace"):
        if '"event"' not in l: continue
        try: r=json.loads(l)
        except: continue
        if r.get("ts_epoch",0)<B: continue
        e=r.get("event"); tk=r.get("ticker",""); d=r.get("details",{}); ts=r.get("ts_epoch",0)
        if "26JUN03" not in (tk or d.get("event","")): continue
        if e=="order_placed" and d.get("action")=="buy": placed[tk].append((ts, d.get("price"), d.get("order_id")))
        elif e=="order_cancelled": cancelled[tk].append((ts, d.get("order_id"), d.get("reason","?")))
        elif e=="v4_place": vplace[tk]=d; target[tk]=d.get("target_bid")
        elif e=="entry_filled": filled_log.add(tk)
        elif e=="entry_cancelled":
            rc_by_tk[tk].append((ts,"match_buffer")); match_start[tk]=d.get("match_start",match_start.get(tk,0))
        elif e=="v4_resting_cancel": rc_by_tk[tk].append((ts,"resting_cancel:"+d.get("reason","")[:10]))
        elif e=="v4_move_repost": rc_by_tk[tk].append((ts,"reprice"))

legs=sorted(set(list(placed)+list(target)))
def intervals(tk):
    """live [t_place, t_cancel) at price, matched by order_id."""
    cmap={oid:(cts,rsn) for cts,oid,rsn in cancelled[tk]}
    out=[]
    for tts,price,oid in placed[tk]:
        cts,rsn = cmap.get(oid,(match_start.get(tk, tts+1e9),"none/still"))
        out.append((tts,cts,price,rsn))
    return sorted(out)
def reason_at(tk, t):
    """why was the bid gone at time t: the most recent removal kind before t."""
    prev=[(ts,k) for ts,k in sorted(rc_by_tk.get(tk,[])) if ts<=t]
    return prev[-1][1] if prev else ("paired_skip" if not placed[tk] else "unknown")

# ---- trades per leg (sell-yes = taker_side no), filter to [first_place-300, match_start] ----
def trades_sellyes(tk, lo, hi):
    """Bound server-side with min_ts/max_ts so we get the PRE-MATCH tape, not the most-recent
    (in-play) trades. Returns sell-yes prints (taker_side=no) and the count of ALL trades seen."""
    out=[]; cur=""; nall=0
    base="/trade-api/v2/markets/trades?ticker=%s&limit=1000&min_ts=%d&max_ts=%d" % (tk, int(lo), int(hi))
    for _ in range(12):
        d=gx(base + ("&cursor="+cur if cur else ""))
        ts_list=d.get("trades",[])
        nall+=len(ts_list)
        for t in ts_list:
            if t.get("taker_side")!="no": continue
            out.append((ep(t["created_time"]), round(float(t["yes_price_dollars"])*100), float(t.get("count_fp",0))))
        cur=d.get("cursor","")
        if not cur: break
    return sorted(out), nall

buckets=Counter(); creason=Counter(); rows=[]
for tk in legs:
    if "-" not in tk: continue
    tgt=target.get(tk)
    ivs=intervals(tk)
    ms=match_start.get(tk, 0)
    if not ms and ivs: ms = ivs[0][0] + 4*3600
    lo = (ivs[0][0]-300) if ivs else (B)
    hi = ms if ms else (lo+5*3600)
    sy, nall = trades_sellyes(tk, lo, hi) if tgt else ([],0)
    leg=tk.rsplit("-",1)[1]
    if tk in filled_log:
        buckets["a_filled"]+=1; rows.append((tk,leg,tgt,"a_filled","")); continue
    if tgt is None:
        buckets["skip_noplace"]+=1; creason[reason_at(tk,hi)]+=1; rows.append((tk,leg,tgt,"c_notlive",reason_at(tk,hi))); continue
    reaching=[(tts,yp) for tts,yp,c in sy if yp<=tgt]
    if reaching:
        live_hit=False
        for tts,yp in reaching:
            for a,b2,price,rsn in ivs:
                if a<=tts<=b2 and price is not None and price>=yp:
                    live_hit=True; break
            if live_hit: break
        if live_hit:
            buckets["b_queue_loss"]+=1; rows.append((tk,leg,tgt,"b_queue_loss","print@%d"%reaching[0][1]))
        else:
            rsn=reason_at(tk, reaching[0][0])
            buckets["c_not_live"]+=1; creason[rsn]+=1
            rows.append((tk,leg,tgt,"c_not_live","%s @print%d/t%.0f"%(rsn,reaching[0][1],reaching[0][0])))
    else:
        minp = min((yp for _,yp,_ in sy), default=None)
        if minp is not None and minp<=tgt+3:
            buckets["d_too_deep"]+=1; rows.append((tk,leg,tgt,"d_too_deep","dip_min=%d vs tgt=%d (off by %d)"%(minp,tgt,minp-tgt)))
        elif minp is not None:
            buckets["e_never_came"]+=1; rows.append((tk,leg,tgt,"e_price_high","dip_min=%d vs tgt=%d (%d too deep); pre-match sell-prints=%d"%(minp,tgt,minp-tgt,len(sy))))
        else:
            tag = "e_no_sellflow" if nall>0 else "e_no_tape"
            buckets["e_never_came"]+=1; rows.append((tk,leg,tgt,tag,"no sell-yes print<=tgt; pre-match trades seen=%d"%nall))

print("="*100)
print("RUN-6 TAPE-vs-BOOK OVERLAY (26JUN03, post-06:28Z) — %d legs" % len(rows))
print("="*100)
for tk,leg,tgt,bk,note in sorted(rows, key=lambda x:x[3]):
    print("  %-44s tgt=%-3s %-14s %s" % (tk.replace("KX","")[:44], tgt, bk, note))
print("\n"+"="*60+"\nBUCKETS")
for k in ["a_filled","b_queue_loss","c_not_live","d_too_deep","e_never_came","skip_noplace"]:
    print("  %-16s %d" % (k, buckets.get(k,0)))
print("\n(c) not-live REMOVAL REASON breakdown — what pulled the bid before the print:")
for k,v in creason.most_common(): print("    %-26s %d" % (k,v))
