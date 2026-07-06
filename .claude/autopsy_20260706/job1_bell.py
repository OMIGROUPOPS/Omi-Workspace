#!/usr/bin/env python3
"""[READ-ONLY] Job-1 exact bell prices for the 3 reaim-pulled concluded games.
Bell = unambiguous tape onset where available, else last price before scheduled start.
Prints per leg: price at bell, price path summary near the pull, min price W1/corridor."""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
ET = timezone(timedelta(hours=-4))

CASES = {
 "KXATPCHALLENGERMATCH-26JUL06DAMHUE": {"onset": "2026-07-06 09:55", "pull": "2026-07-06 09:32", "legs": ["DAM","HUE"]},
 "KXATPCHALLENGERMATCH-26JUL06POPSAN": {"onset": "2026-07-06 11:13", "pull": "2026-07-06 10:14", "legs": ["POP","SAN"]},
 "KXITFWMATCH-26JUL06BUEPOR":          {"onset": None, "sched": "2026-07-06 16:00", "pull": "2026-07-06 10:54", "legs": ["BUE","POR"]},
}
_dc={}
def pts(s):
    try:
        d,t,ap=s.split(" ")
        if d not in _dc:
            y,mo,dy=d.split("-"); _dc[d]=datetime(int(y),int(mo),int(dy),tzinfo=ET).timestamp()
        hh,mm,ss=t.split(":")
        return _dc[d]+(int(hh)%12+(12 if ap=="PM" else 0))*3600+int(mm)*60+int(ss)
    except: return None
def ts_of(s): return datetime.strptime(s,"%Y-%m-%d %H:%M").replace(tzinfo=ET).timestamp() if s else None

for ev, c in CASES.items():
    bell = ts_of(c.get("onset")) or ts_of(c.get("sched"))
    pull = ts_of(c["pull"])
    print(f"\n=== {ev.replace('KX','')} bell={'onset' if c.get('onset') else 'sched(no onset)'} {c.get('onset') or c.get('sched')}")
    for suf in c["legs"]:
        f = Path("analysis/trades")/(ev+"-"+suf+".csv")
        rows=[]
        if f.exists():
            with open(f,encoding="utf-8",errors="replace") as fh:
                next(fh,None)
                for ln in fh:
                    p=ln.rstrip("\n").split(",")
                    if len(p)<5: continue
                    t=pts(p[0])
                    if t is None: continue
                    try: rows.append((t,int(p[2]),int(float(p[3])),p[4]))
                    except: continue
        rows.sort()
        pre=[r for r in rows if r[0]<=bell]
        at_bell = pre[-1][1] if pre else None
        at_pull = ([r for r in rows if r[0]<=pull] or [(None,None)])[-1][1]
        w1min = min((r[1] for r in pre), default=None)
        post_pull_pre_bell = [r for r in rows if pull < r[0] <= bell]
        pp_min = min((r[1] for r in post_pull_pre_bell), default=None)
        sf = [r for r in post_pull_pre_bell if r[3]=="no"]
        pp_sf_min = min((r[1] for r in sf), default=None)
        print(f"  {suf}: at-bell {at_bell} | at-pull {at_pull} | pregame min {w1min} | after-pull-pre-bell min {pp_min} (sell-flow min {pp_sf_min}) | prints pre-bell {len(pre)}")
