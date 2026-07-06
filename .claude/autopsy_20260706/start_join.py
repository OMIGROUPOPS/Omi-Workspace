#!/usr/bin/env python3
"""[READ-ONLY] CORPUS START-TIME JOIN — one question: does anything on disk hold actual
start times for the corpus matches? Sources: state/schedule.json (TE/ESPN),
tennis.db live_scores (TE in-play transitions = OBSERVED starts), bookmaker_odds
(pre-match scrape bounds), historical_events (first_ts = TRADE-derived, circular —
reported as such, not used). Writes /tmp/start_join.json."""
import json, sqlite3, sys, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
# ---- corpus matches (true denominator) ----
events=defaultdict(set)
for f in Path("analysis/trades").iterdir():
    name=f.name.replace(".csv.gz","").replace(".csv","")
    if "MATCH-" not in name: continue
    events[name.rsplit("-",1)[0]].add(name)
matches=sorted(events)
print(f"corpus: {sum(len(v) for v in events.values())} tickers -> {len(matches)} matches",file=sys.stderr)

def code_of(ev):
    m=re.search(r"\d{2}([A-Z]{3})[A-Z]*\d{2}([A-Z]{6})$", ev)
    if not m: return None,None
    mon=ev  # date code like 26JUL01
    m2=re.search(r"-(\d{2}[A-Z]{3}\d{2})([A-Z]{4,8})$", ev)
    if not m2: return None,None
    return m2.group(1), m2.group(2)

# ---- (a) schedule.json ----
sch=json.load(open("state/schedule.json"))["schedule"]
def sched_join(pc):
    for k in (pc, pc[3:]+pc[:3]) if len(pc)==6 else (pc,):
        e=sch.get(k)
        if e and e.get("start_time"):
            return e["start_time"], bool(e.get("espn_midnight"))
    return None,None

# ---- (b) live_scores observed starts ----
c=sqlite3.connect("file:tennis.db?mode=ro",uri=True)
stat=[r[0] for r in c.execute("select distinct status from live_scores")]
print("live_scores statuses:",stat,file=sys.stderr)
INPLAY=set(s for s in stat if s and s.lower() not in ("finished","scheduled","not_started","cancelled","canceled","walkover","retired","postponed",""))
rows=c.execute("select te_match_id,player1,player2,status,last_updated from live_scores").fetchall()
def surkey(p1,p2):
    def pre(n):
        n=(n or "").strip().split(" ")[0].upper()
        n=re.sub(r"[^A-Z]","",n)
        return n[:3]
    return pre(p1),pre(p2)
first_inplay={}
meta={}
for mid,p1,p2,st,lu in rows:
    if not lu: continue
    if st in INPLAY:
        if mid not in first_inplay or lu<first_inplay[mid]:
            first_inplay[mid]=lu
    meta[mid]=(p1,p2)
# index by (prefix-pair, date)
by_code=defaultdict(list)
for mid,lu in first_inplay.items():
    p1,p2=meta[mid]
    a,b=surkey(p1,p2)
    d=lu[:10]
    by_code[(a+b,d)].append(lu); by_code[(b+a,d)].append(lu)
MON={"JAN":"01","FEB":"02","MAR":"03","APR":"04","MAY":"05","JUN":"06","JUL":"07"}
def date_of(dc):  # 26JUL01 -> 2026-07-01
    return f"20{dc[:2]}-{MON[dc[2:5]]}-{dc[5:7]}"
def live_join(dc,pc):
    d=date_of(dc)
    for dd in (d,):  # same-day; TE tz vs ET handled in calibration below
        for k in (pc, pc[3:]+pc[:3]) if len(pc)==6 else (pc,):
            v=by_code.get((k,dd))
            if v: return min(v)
    # next-day (UTC rollover)
    from datetime import date
    y,mo,dy=map(int,d.split("-"))
    d2=date(y,mo,dy)+timedelta(days=1)
    for k in (pc, pc[3:]+pc[:3]) if len(pc)==6 else (pc,):
        v=by_code.get((k,str(d2)))
        if v: return min(v)
    return None

# ---- run the joins over corpus matches ----
res={"sched":0,"sched_midnight":0,"live":0,"either":0,"none":0}
per_match={}
for ev in matches:
    dc,pc=code_of(ev)
    if not pc: res["none"]+=1; continue
    st,mid=sched_join(pc)
    lv=live_join(dc,pc) if dc else None
    if st and not mid: res["sched"]+=1
    if st and mid: res["sched_midnight"]+=1
    if lv: res["live"]+=1
    if (st and not mid) or lv: res["either"]+=1
    else: res["none"]+=1
    per_match[ev]={"sched":st,"midnight":mid,"live":lv}
print(f"JOIN over {len(matches)} matches: {res}",file=sys.stderr)

# ---- (c) overlap-53: lookup vs certified latch ----
latch={}
for LOG in ("/tmp/session_since_boot.jsonl","logs/live_v3_20260706.jsonl"):
    if not Path(LOG).exists(): continue
    for line in open(LOG,encoding="utf-8",errors="replace"):
        if '"match_live_detected"' not in line: continue
        try: o=json.loads(line)
        except: continue
        ev=o.get("details",{}).get("event")
        if ev and ev not in latch: latch[ev]=o.get("ts_epoch")
def parse_lu(lu, tzoff):
    try:
        return datetime.strptime(lu,"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()+tzoff*3600
    except: return None
overlap=[]
for ev,lt in latch.items():
    ev2=ev.replace("KX","")
    dc,pc=code_of(ev2)
    if not pc: continue
    lv=live_join(dc,pc) if dc else None
    st,mid=sched_join(pc)
    overlap.append({"ev":ev2[-20:],"latch":lt,"live_raw":lv,"sched":st,"midnight":mid})
# tz calibration for live_scores: test offsets, pick min median |err|
def errs_at(off):
    e=[]
    for o in overlap:
        if not o["live_raw"]: continue
        t=parse_lu(o["live_raw"],off)
        if t: e.append((t-o["latch"])/60)
    return e
best_off=None
for off in (-8,-7,-6,-5,-4,-3,-2,-1,0):
    e=errs_at(off)
    if len(e)>=10:
        m=sorted(abs(x) for x in e)[len(e)//2]
        if best_off is None or m<best_off[1]: best_off=(off,m,len(e))
def med(v):
    v=sorted(v); return v[len(v)//2] if v else None
def q(v,p):
    v=sorted(v); return v[min(len(v)-1,int(len(v)*p))] if v else None
lerr=errs_at(best_off[0]) if best_off else []
# sched vs latch too
serr=[]
for o in overlap:
    if not o["sched"] or o["midnight"]: continue
    try:
        t=datetime.fromisoformat(o["sched"].replace("Z","+00:00")).timestamp()
        serr.append((t-o["latch"])/60)
    except: pass
print(f"(c) live_scores lookup vs latch: tz-off {best_off[0] if best_off else '?'}h n={len(lerr)} med {med(lerr)}m [p25 {q(lerr,0.25)} p75 {q(lerr,0.75)}] med|err| {med(sorted(abs(x) for x in lerr))}m",file=sys.stderr)
print(f"(c) schedule.json vs latch: n={len(serr)} med {med(serr)}m [p25 {q(serr,0.25)} p75 {q(serr,0.75)}] med|err| {med(sorted(abs(x) for x in serr))}m",file=sys.stderr)

# ---- (d) recount exclusions under lookup ----
# exclusion classes: matches whose bell detection failed (no_bell) or thin prebell —
# recount = of those, how many have EITHER lookup (live or sched-non-midnight)
def gun(rows,K,M):
    mv=defaultdict(float)
    for t,pr,ct in rows: mv[int(t//60)*60]+=ct
    mins=sorted(mv)
    fwd={m:sum(mv[x] for x in mins if m<=x<m+600) for m in mins}
    return next((m for m in mins if mv[m]>=K and fwd[m]>=M), None)
import gzip
_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
recount={"BAR":{"excluded":0,"comeback":0},"LATCHCAL":{"excluded":0,"comeback":0}}
for ev,tks in events.items():
    dc,pc=code_of(ev)
    if not pc: continue
    rows_all=[]
    ok=True
    for tk in tks:
        for suf in (".csv",".csv.gz"):
            f=Path("analysis/trades")/(tk+suf)
            if f.exists(): break
        else: ok=False; break
        op=gzip.open if f.suffix==".gz" else open
        rr=[]
        with op(f,"rt",encoding="utf-8",errors="replace") as fh:
            next(fh,None)
            for ln in fh:
                p=ln.rstrip("\n").split(",")
                if len(p)<5: continue
                t=pts(p[0])
                if t is None: continue
                try: rr.append((t,int(p[2]),int(float(p[3]))))
                except: continue
        if len(rr)<30: ok=False; break
        rows_all.append(sorted(rr))
    if not ok or len(rows_all)!=2: continue
    pm=per_match.get(ev,{})
    has_lookup=bool(pm.get("live") or (pm.get("sched") and not pm.get("midnight")))
    for tag,K,M in (("BAR",150,3000),("LATCHCAL",600,20000)):
        bells=[gun(r,K,M) for r in rows_all]
        if not any(bells):
            recount[tag]["excluded"]+=1
            if has_lookup: recount[tag]["comeback"]+=1
print(f"(d) no-bell matches coming back under lookup: {recount}",file=sys.stderr)

json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
           "corpus_matches":len(matches),"corpus_tickers":sum(len(v) for v in events.values()),
           "join":res,"overlap_live":{"tz_off":best_off[0] if best_off else None,"n":len(lerr),
               "med":med(lerr),"p25":q(lerr,0.25),"p75":q(lerr,0.75),
               "med_abs":med(sorted(abs(x) for x in lerr))},
           "overlap_sched":{"n":len(serr),"med":med(serr),"p25":q(serr,0.25),"p75":q(serr,0.75),
               "med_abs":med(sorted(abs(x) for x in serr)) if serr else None},
           "recount":recount},
          open("/tmp/start_join.json","w"))
print("DONE",file=sys.stderr)
