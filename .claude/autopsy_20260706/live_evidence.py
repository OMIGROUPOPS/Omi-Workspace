#!/usr/bin/env python3
"""[READ-ONLY] LIVE EVIDENCE PASS — items 2/3/5 of the day queue, from the CURRENT
session (12:15 boot) + overnight (23:50 boot), tapes + logs, timestamped now.
 (2) THIN-GUN: every gun_scale_shadow fire joined to true tape onset + legacy latch;
     false pregame fires; the live blind count (onset seen, no latch) TODAY.
 (3) WALK-CAP HONEST ANCHOR census: conception(first-post)->fill drift per category
     from today's honest windows (the distributions the cap re-anchors to).
 (5) THIN-BOOK: today's priced-out legs (bid below where the tape traded).
Writes /tmp/live_evidence.json. Run from arb-executor root."""
import json, sys, gzip
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
LOGS = ["/tmp/session_since_boot.jsonl", "logs/live_v3_20260706.jsonl"]
NOW = datetime.now(ET)
def hm(e): return datetime.fromtimestamp(e, ET).strftime("%H:%M") if e else None

_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
def read_tape(tk):
    for suf in (".csv", ".csv.gz"):
        f = Path("analysis/trades")/(tk+suf)
        if f.exists(): break
    else: return []
    rows=[]
    op = gzip.open if f.suffix==".gz" else open
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
def tape_gun(rows):
    if not rows: return None
    mv=defaultdict(float)
    for t,pr,ct,s in rows: mv[int(t//60)*60]+=ct
    mins=sorted(mv)
    fwd={m:sum(mv[x] for x in mins if m<=x<m+600) for m in mins}
    return next((m for m in mins if mv[m]>=150 and fwd[m]>=3000), None)

# ---- parse logs ----
gunshadow=[]; latch={}; posts=defaultdict(list); fills={}; wopen={}; cats={}
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for line in open(LOG,encoding="utf-8",errors="replace"):
        if '"event"' not in line: continue
        try: o=json.loads(line)
        except: continue
        e,tk,d,ts=o.get("event"),o.get("ticker") or "",o.get("details",{}),o.get("ts_epoch",0)
        if e=="gun_scale_shadow":
            gunshadow.append({"ev":d.get("event"),"ts":ts,"tts_min":d.get("tts_min"),
                              "burst":d.get("recent_burst"),"bar":d.get("scaled_bar"),
                              "legacy":d.get("legacy_gun_latched")})
        elif e=="match_live_detected":
            ev=d.get("event")
            if ev and ev not in latch: latch[ev]=ts
        elif e=="order_placed" and d.get("action")=="buy" and tk and d.get("price") is not None:
            posts[tk].append((ts,d["price"]))
        elif e=="entry_filled" and tk and tk not in fills:
            fills[tk]=(ts,d.get("fill_price"))
        elif e=="window_open_set" and tk and tk not in wopen:
            wopen[tk]=(ts,d.get("price"))
        elif e=="v4_place" and tk and d.get("cat"): cats[tk]=d["cat"]

# ---- (2) thin-gun join ----
evs=set(x["ev"] for x in gunshadow if x["ev"])
onset={}
for ev in evs:
    for tk in list(posts)+list(fills):
        if tk.rsplit("-",1)[0]==ev:
            rows=read_tape(tk)
            g=tape_gun(rows)
            if g and (ev not in onset or g<onset[ev]): onset[ev]=g
gun_rows=[]
for x in gunshadow:
    ev=x["ev"]; on=onset.get(ev); lt=latch.get(ev)
    verdict="?"
    if on is None: verdict="no_onset_detected"
    else:
        dm=(x["ts"]-on)/60
        verdict=("FALSE_PREGAME" if dm<-10 else "early" if dm<-2 else "on" if dm<=5 else "late")
    gun_rows.append({**x,"t":hm(x["ts"]),"onset_t":hm(on),"latch_t":hm(lt),
                     "vs_onset_min":round((x["ts"]-on)/60,1) if on else None,"verdict":verdict,
                     "legacy_silent": lt is None})
# blind count TODAY (since 12:15): events with onset in current session window and no latch
today0=datetime(2026,7,6,12,15,tzinfo=ET).timestamp()
blind_today=[]
seen_ev=set(tk.rsplit("-",1)[0] for tk in list(posts)+list(fills))
for ev in seen_ev:
    if ev in latch: continue
    on=onset.get(ev)
    if on is None:
        for tk in list(posts)+list(fills):
            if tk.rsplit("-",1)[0]==ev:
                g=tape_gun(read_tape(tk))
                if g and (on is None or g<on): on=g
        if on: onset[ev]=on
    if on and on>=today0 and on <= NOW.timestamp()-600:
        blind_today.append({"ev":ev.replace("KX",""),"onset_t":hm(on)})

# ---- (3) conception->fill drift census (today's honest windows) ----
drift_rows=defaultdict(list)
for tk,f in fills.items():
    ps=sorted(posts.get(tk,[]))
    if not ps or f[1] is None: continue
    c=cats.get(tk,"?")
    drift_rows[c].append(f[1]-ps[0][1])   # fill vs first-post (conception at first post)
def med(v): v=sorted(v); return v[len(v)//2] if v else None
def q(v,p): v=sorted(v); return v[min(len(v)-1,int(len(v)*p))] if v else None
drift_stats={c:{"n":len(v),"med":med(v),"p75":q(v,0.75),"p90":q(v,0.9),"max":max(v)}
             for c,v in drift_rows.items()}

# ---- (5) priced-out legs today ----
priced_out=[]
for tk,ps in posts.items():
    if tk in fills: continue
    ps=sorted(ps)
    rows=read_tape(tk)
    if not rows: continue
    end=latch.get(tk.rsplit("-",1)[0]) or NOW.timestamp()
    sf=[(t,pr,ct) for t,pr,ct,s in rows if s=="no" and ps[0][0]<=t<=end]
    if not sf: continue
    lo=min(pr for _,pr,_ in sf)
    lvl=None
    for t,pr in ps:
        if t<=sf[0][0]: lvl=pr
    if lvl is not None and lo>lvl:
        priced_out.append({"tk":tk[-18:],"cat":cats.get(tk,"?"),"ours":lvl,"traded_low":lo,
                           "gap":lo-lvl,"prints":len(sf)})

json.dump({"generated":NOW.strftime("%Y-%m-%d %H:%M ET"),
           "gun_rows":gun_rows,"blind_today":blind_today,
           "drift_stats":drift_stats,"priced_out":priced_out},
          open("/tmp/live_evidence.json","w"),default=str)
from collections import Counter
print("THIN-GUN:",Counter(r["verdict"] for r in gun_rows),"| shadow fires w/ legacy SILENT:",
      sum(1 for r in gun_rows if r["legacy_silent"]),file=sys.stderr)
print("BLIND TODAY (onset, no latch, since 12:15):",len(blind_today),file=sys.stderr)
print("DRIFT (conception->fill):",json.dumps(drift_stats),file=sys.stderr)
print("PRICED-OUT today:",len(priced_out),file=sys.stderr)
