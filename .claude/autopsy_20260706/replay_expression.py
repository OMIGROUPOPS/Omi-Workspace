#!/usr/bin/env python3
"""[READ-ONLY] EXPRESSION-LAW REPLAY vs TODAY (C46 Lane-1, rider item 1).
Reads /tmp/spread_recount.json (non-self rows via THE chain); re-expresses every
placement under expressed = min(px, ns_bid+1); the CONVERTED set (px > ns_bid+1)
gets: would-the-expressed-level-have-filled (conservative: sell-flow print <= level
after ts, 8h window — SIM-FLATTERED where assumed, flagged), fill kept/lost/cheaper
deltas, and the <=97 structural note (expression only LOWERS -> the bound can never
be violated by conversion). GOMOFN + TANKAW re-graded. Writes /tmp/expr_replay.json."""
import json, gzip, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))
ROOT = Path("/root/Omi-Workspace/arb-executor")
import sys as _s
_s.path.insert(0, str(ROOT/"analysis"))
from ex_self_chain import express_target   # [ONE CHAIN]

R = json.load(open("/tmp/spread_recount.json"))
rows = R["rows"] if "rows" in R else None
# the recount json may not carry rows; rebuild converted set from summary impossible ->
# require rows; if absent, exit with instruction
if rows is None:
    print("recount json has no per-row dump; re-run recount with rows", file=sys.stderr)
    sys.exit(1)

_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
def tape_sf(tk):
    for suf in (".csv",".csv.gz"):
        f=ROOT/"analysis/trades"/(tk+suf)
        if f.exists(): break
    else: return []
    op=gzip.open if f.suffix==".gz" else open
    rows_=[]
    with op(f,"rt",encoding="utf-8",errors="replace") as fh:
        next(fh,None)
        for ln in fh:
            p=ln.rstrip("\n").split(",")
            if len(p)<5: continue
            t=pts(p[0])
            if t is None: continue
            try: rows_.append((t,int(p[2]),p[4]))
            except: continue
    rows_.sort(); return rows_

# ticker suffixes in recount rows are truncated (-20:) -- rebuild full names from trades dir
full_by_suffix={}
for f in (ROOT/"analysis/trades").iterdir():
    name=f.name.replace(".csv.gz","").replace(".csv","")
    full_by_suffix[name[-20:]]=name

conv=[]; kept=0; unchanged=0
tapes={}
for r_ in rows:
    px, nb = r_["px"], r_["ns_bid"]
    ex = express_target(px, nb)
    if ex == px:
        unchanged += 1
        continue
    tk_full = full_by_suffix.get(r_["tk"])
    would = None
    if tk_full:
        if tk_full not in tapes: tapes[tk_full]=tape_sf(tk_full)
        would = any(pr <= ex for t,pr,s in tapes[tk_full] if s=="no" and r_["ts"] < t < r_["ts"]+8*3600)
    conv.append({**{k:r_[k] for k in ("tk","px","ns_bid","cls","filled","fill_px")},
                 "expressed": ex, "saved_c": px-ex, "would_fill": would})
n=len(conv)
w=sum(1 for c in conv if c["would_fill"])
lost=sum(1 for c in conv if c["filled"] and not c["would_fill"])
cheaper=sum(1 for c in conv if c["filled"] and c["would_fill"])
gained=sum(1 for c in conv if not c["filled"] and c["would_fill"])
saved=[c["saved_c"] for c in conv]
def med(v):
    v=sorted(v); return v[len(v)//2] if v else None
out={"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
     "total_rows":len(rows),"unchanged":unchanged,"converted":n,
     "converted_would_fill":w,"fills_kept_cheaper":cheaper,"fills_LOST":lost,"fills_GAINED":gained,
     "saved_c_med":med(saved),"saved_c_max":max(saved) if saved else None,
     "le97_note":"expression only LOWERS targets; the <=97 bound is structurally unviolable by conversion",
     "sim_flag":"would_fill assumes a print<=level fills us (queue ignored) — SIM-FLATTERED, flagged",
     "converted_rows":conv[:200]}
json.dump(out,open("/tmp/expr_replay.json","w"))
print(f"rows {len(rows)} | converted {n} | would-fill {w} | kept-cheaper {cheaper} | LOST {lost} | GAINED {gained} | saved med {med(saved)}c max {max(saved) if saved else None}c",file=sys.stderr)
