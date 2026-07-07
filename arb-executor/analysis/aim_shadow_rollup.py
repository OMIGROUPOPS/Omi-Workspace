#!/usr/bin/env python3
"""AIM SHADOW nightly rollup — joins aim_shadow log lines to the tape: per cat,
shadow-would-have-filled rate (tape printed <= shadow_aim after the line, pre-bell),
discount captured vs actual bid, misses (dip never came), NULL/tier serving split,
and GOMOFN exhibits (actual fill above best bid where shadow aimed lower).
Output: one rollup line per cat -> append to the ledger at the nightly cut.
Run from arb-executor root after a night of lines."""
import json, gzip, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
LOG = sorted(Path("logs").glob("live_v3_*.jsonl"))[-1]
_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
def tape(tk):
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
            try: rows.append((t,int(p[2]),p[4]))
            except: continue
    rows.sort(); return rows
CATP={"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
      "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CATP.items() if tk.startswith(k)), "?")
lines=[]; fills={}
for ln in open(LOG,encoding="utf-8",errors="replace"):
    if '"aim_shadow"' in ln:
        try: lines.append(json.loads(ln))
        except: pass
    elif '"entry_filled"' in ln:
        try:
            o=json.loads(ln)
            fills.setdefault(o.get("ticker"),(o.get("ts_epoch"),o["details"].get("fill_price")))
        except: pass
per=defaultdict(lambda: {"n":0,"null":0,"tiers":defaultdict(int),"would_fill":0,"scoreable":0,
                          "disc":[],"miss":0,"gomofn":0})
seen=set()
for o in lines:
    d=o.get("details",{}); tk=o.get("ticker"); ts=o.get("ts_epoch")
    key=(tk,d.get("cell"))
    if key in seen: continue     # first line per (leg,cell) scores
    seen.add(key)
    c=cat_of(tk or "")
    P=per[c]; P["n"]+=1
    if d.get("shadow")=="NULL_CELL": P["null"]+=1; continue
    P["tiers"][d.get("source") or "?"]+=1
    aim=d.get("shadow_aim25")
    if aim is None: continue
    P["scoreable"]+=1
    rows=[r for r in tape(tk) if r[0]>ts and r[2]=="no"]
    hit=next((r for r in rows if r[1]<=aim),None)
    if hit:
        P["would_fill"]+=1
        ab=d.get("actual_bid")
        if ab is not None: P["disc"].append(ab-aim)
    else:
        P["miss"]+=1
    f=fills.get(tk)
    if f and d.get("actual_bid") is not None and aim<d["actual_bid"] and f[1] and f[1]>=d["actual_bid"]:
        P["gomofn"]+=1
def med(v):
    v=sorted(v); return v[len(v)//2] if v else None
print(f"AIM SHADOW ROLLUP {datetime.now(ET).strftime('%Y-%m-%d %H:%M ET')} (log {LOG.name}, {len(lines)} lines)")
for c,P in sorted(per.items()):
    wf=P["would_fill"]; sc=P["scoreable"]
    print(f"  {c}: decisions {P['n']} | NULL {P['null']} | tiers {dict(P['tiers'])} | "
          f"would-fill {wf}/{sc} ({100*wf//max(1,sc)}%) | discount vs actual med {med(P['disc'])}c | "
          f"misses(dip never came) {P['miss']} | GOMOFN exhibits {P['gomofn']}")
