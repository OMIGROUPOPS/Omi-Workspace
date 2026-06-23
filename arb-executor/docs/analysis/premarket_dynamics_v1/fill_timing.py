#!/usr/bin/env python3
"""READ-ONLY: where today's fills land in TIME vs window1/scheduled/real markers. Source of truth =
live log entry_filled events. Markers reuse today_bands_fix.py definitions byte-for-byte. Writes CSV."""
import json,datetime,csv,collections,hashlib,re
from pathlib import Path
HERE=Path("/root/Omi-Workspace/arb-executor"); DOCS=HERE/"docs/analysis/premarket_dynamics_v1"
LOG=HERE/"logs/live_v3_20260622.jsonl"
def iso2ep(s):
    try: return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
    except: return None
def logts2ep(ts):
    m=re.match(r'(\d{4})-(\d\d)-(\d\d) (\d+):(\d\d):(\d\d) (AM|PM)',ts)
    if not m: return None
    y,mo,d,h,mi,s=int(m[1]),int(m[2]),int(m[3]),int(m[4]),int(m[5]),int(m[6])
    if m[7]=="PM" and h!=12:h+=12
    if m[7]=="AM" and h==12:h=0
    return datetime.datetime(y,mo,d,h,mi,s,tzinfo=datetime.timezone.utc).timestamp()+4*3600
def etstr(ep): return datetime.datetime.fromtimestamp(ep-4*3600,tz=datetime.timezone.utc).strftime("%H:%M:%S")
def cat_of(tk):
    if tk.startswith("KXATPCHALLENGERMATCH"): return "ATP_CHALL"
    if tk.startswith("KXWTACHALLENGERMATCH"): return "WTA_CHALL"
    if tk.startswith("KXATPMATCH"): return "ATP_MAIN"
    if tk.startswith("KXWTAMATCH"): return "WTA_MAIN"
sched={}; real={}; names={}; refsrc={}; fills=[]
for line in open(LOG):
    if not any(s in line for s in ('schedule_match','match_live_detected','v4_place','entry_filled')): continue
    try: d=json.loads(line)
    except: continue
    e=d.get("event"); det=d.get("details",{}); tk=d.get("ticker","")
    if e=="schedule_match":
        ev=det.get("event")
        if ev and det.get("start_time"): sched[ev]=iso2ep(det["start_time"]); names[ev]={"p1":det.get("p1"),"p2":det.get("p2")}
    elif e=="match_live_detected":
        ev=det.get("event") or (tk.rsplit("-",1)[0] if tk else None)
        if ev and ev not in real: real[ev]=logts2ep(d["ts"])
    elif e=="v4_place" and "-" in tk:
        if tk not in refsrc: refsrc[tk]=det.get("reference_source") or det.get("anchor_src") or ""
    elif e=="entry_filled" and "-" in tk:
        fills.append((logts2ep(d["ts"]),tk,det.get("fill_price"),det.get("play_type")))
ANCHOR={"KXATPMATCH-26JUN22CRAROD-ROD":"Jurij Rodionov","KXATPMATCH-26JUN22CRAROD-CRA":"Oliver Crawford"}
def nm(tk):
    if tk in ANCHOR: return ANCHOR[tk]
    ev=tk.rsplit("-",1)[0]; sd=tk.rsplit("-",1)[1]; dn=names.get(ev,{})
    for p in (dn.get("p1"),dn.get("p2")):
        if p and p.split()[-1][:3].upper()==sd.upper(): return p
    return sd+"?"
def src_label(tk,play):
    rs=refsrc.get(tk,"")
    if rs=="staircase": return "staircase"
    if rs=="join_bid": return "join_bid"
    pl=(play or "")
    if "engagement" in pl: return "engagement"
    if "fallback" in pl: return "fallback"
    if "resting_maker" in pl: return "resting_maker"
    if "complete_cross" in pl or "cross" in pl: return "complete_cross"
    if "reconcil" in pl: return "reconcile"
    return rs or pl or "other"
rows=[]
for fts,tk,fc,play in fills:
    ev=tk.rsplit("-",1)[0]; sc=sched.get(ev); rs=real.get(ev)
    rsrc="latch" if rs else "scheduled_fallback"
    if sc is None:
        bucket="NO_SCHEDULE"
    else:
        w1=sc-14400.0
        if fts is None: bucket="NA"
        elif fts<w1: bucket="PRE_WINDOW1"
        elif fts<sc: bucket="PREMARKET"
        else:
            bucket="POST_SCHEDULED"
            if rs:
                bucket = "CORRIDOR" if fts<rs else "POST_REAL"
    rows.append(dict(fill_ts_ET=etstr(fts) if fts else "",player=nm(tk),category=cat_of(tk),fill_cent=fc,
        source=src_label(tk,play),play_type=play,reference_source=refsrc.get(tk,""),real_start_source=rsrc,
        scheduled_ET=etstr(sc) if sc else "",real_ET=etstr(rs) if rs else "",bucket=bucket,event=ev))
rows.sort(key=lambda r:r["fill_ts_ET"])
cols=["fill_ts_ET","player","category","fill_cent","source","play_type","reference_source","real_start_source","scheduled_ET","real_ET","bucket","event"]
outp=DOCS/"fill_timing_2026-06-22.csv"
with open(outp,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in rows]
sha=hashlib.sha256(open(outp,"rb").read()).hexdigest()
# ---- summary ----
C=collections.Counter
N=len(rows)
# PRIMARY cut: PREMARKET vs POST_SCHEDULED (POST_SCHEDULED = CORRIDOR+POST_REAL+POST_SCHEDULED)
def primary(b): return "PREMARKET" if b=="PREMARKET" else ("POST_SCHEDULED" if b in ("POST_SCHEDULED","CORRIDOR","POST_REAL") else b)
pc=C(primary(r["bucket"]) for r in rows)
print("================ FILL TIMING SUMMARY (Jun 22 2026 ET) ================")
print(f"N entry_filled events today: {N}")
prem=pc["PREMARKET"]; post=pc["POST_SCHEDULED"]; denom=prem+post
print(f"PRIMARY cut (scheduled-only, latch-independent):")
print(f"  PREMARKET (window1<=fill<scheduled): {prem} ({100*prem/denom:.0f}% of prem+post)")
print(f"  POST_SCHEDULED (fill>=scheduled):    {post} ({100*post/denom:.0f}% of prem+post)")
other={k:v for k,v in pc.items() if k not in ("PREMARKET","POST_SCHEDULED")}
print(f"  (other buckets: {other})")
# latch-leg sub-split
latch_rows=[r for r in rows if r["real_start_source"]=="latch" and r["bucket"] in ("CORRIDOR","POST_REAL")]
ls=C(r["bucket"] for r in latch_rows)
print(f"\nlatch-legs POST_SCHEDULED sub-split (corridor/post-real, latch legs only): CORRIDOR={ls['CORRIDOR']} POST_REAL={ls['POST_REAL']} (n latch post-sched={len(latch_rows)})")
# by source within bucket
print("\nfill source within PREMARKET:", dict(C(r["source"] for r in rows if r["bucket"]=="PREMARKET")))
print("fill source within POST_SCHEDULED (incl corridor/post_real):", dict(C(r["source"] for r in rows if primary(r["bucket"])=="POST_SCHEDULED")))
# cross-check 1: vs today_bands_FIXED filled legs
try:
    fx=list(csv.DictReader(open(DOCS/"today_bands_FIXED_2026-06-22.csv")))
    filled_in_bands=sum(1 for x in fx if x.get("our_fill_cent","") not in ("","None"))
except Exception as ex: filled_in_bands=f"(could not read: {ex})"
carry=sum(1 for r in rows if "26JUN22" not in r["event"])
print(f"\nCROSS-CHECK 1: entry_filled today={N} vs today_bands_FIXED filled legs={filled_in_bands}")
print(f"  reconciliation: of {N} fills, {carry} are non-26JUN22 carryover; 26JUN22 fills={N-carry}; today_bands counts only 26JUN22 depth-covered legs")
# cross-check 2: Crawford
cr=[r for r in rows if r["player"]=="Oliver Crawford"]
for r in cr: print(f"CROSS-CHECK 2: Oliver Crawford fill_ts={r['fill_ts_ET']} scheduled={r['scheduled_ET']} real={r['real_ET']} -> bucket={r['bucket']}  {'PASS' if r['bucket']=='CORRIDOR' else 'FAIL'}")
print(f"\nCSV: {outp}\nsha256: {sha}")
