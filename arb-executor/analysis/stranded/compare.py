import json, os, csv, gzip, statistics as stx
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
BASE="/root/Omi-Workspace/arb-executor"; TR=BASE+"/analysis/trades"; TICK=BASE+"/analysis/premarket_ticks"
EDT=timezone(timedelta(hours=-4))
def ep(y,mo,d,h,mi): return datetime(y,mo,d,h,mi,tzinfo=EDT).timestamp()
PRIOR=(ep(2026,6,30,0,56), ep(2026,6,30,15,46))     # W6: Monday flags ON + completion_ceiling
CURRENT=(ep(2026,6,30,15,46), ep(2026,7,1,18,40))    # bisect: 3 flags OFF
LOGS=[BASE+"/logs/live_v3_20260630.jsonl",BASE+"/logs/live_v3_20260701.jsonl"]
def cat(t):
    for p,c in (("KXATPCHALLENGERMATCH","ATP_CHALL"),("KXWTACHALLENGERMATCH","WTA_CHALL"),("KXATPMATCH","ATP_MAIN"),("KXWTAMATCH","WTA_MAIN"),("KXITFWMATCH","ITF_W"),("KXITFMATCH","ITF_M")):
        if t.startswith(p): return c
    return "OTHER"
def evkey(t): return t.rsplit("-",1)[0]
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(dir_,tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(dir_+"/"+tk+e): return dir_+"/"+tk+e
    return None
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None

# collect per-leg (across full Jun30-Jul1, then box by entry)
L=defaultdict(lambda: dict(place=[],placed=[],cancel=[],fill=[],settle=None,skip=Counter(),mlive=None))
for f in LOGS:
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        ts=e.get("ts_epoch");
        if ts is None: continue
        tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}
        if not tk: continue
        d=L[tk]
        if ev=="v4_place": d["place"].append((ts,D.get("target_bid"),D.get("cell")))
        elif ev=="order_placed" and D.get("action")=="buy": d["placed"].append((ts,D.get("price")))
        elif ev=="order_cancelled": d["cancel"].append((ts,D.get("label")))
        elif ev in ("entry_filled","completion_fill"): d["fill"].append((ts,D.get("fill_price")))
        elif ev=="settled": d["settle"]=D.get("pnl_dollars")
        elif ev in ("match_live_resting_cancel","v4_resting_cancel"): d["mlive"]=ts if d["mlive"] is None else min(d["mlive"],ts)
        elif ev=="skipped": d["skip"][D.get("reason","")]+=1

def box_of(d):
    # entry-box: first fill ts if filled else first post ts
    if d["fill"]: t=min(x[0] for x in d["fill"])
    elif d["placed"]: t=min(x[0] for x in d["placed"])
    elif d["place"]: t=min(x[0] for x in d["place"])
    else: return None
    for name,(a,b) in (("PRIOR",PRIOR),("CURRENT",CURRENT)):
        if a<=t<b: return name
    return None

def tape_lts(tk,onset):
    f=findf(TICK,tk)
    if not f: return None
    lts=[]
    for r in csv.DictReader(opent(f)):
        e=ptape(r["ts_et"])
        if e is None: continue
        if onset and e>=onset: continue
        try: v=int(float(r.get("last_trade") or 0))
        except: v=0
        if v>0: lts.append(v)
    return lts
def tercile(fill,lts):
    if not lts or fill is None: return None
    lo,hi=min(lts),max(lts); rng=hi-lo
    if rng<=0: return "flat"
    if fill<lo+rng/3: return "cheap"
    if fill<lo+2*rng/3: return "mid"
    return "expensive"
def dedup_no(tk,ref,onset):
    f=findf(TR,tk)
    if not f: return []
    fil=[]
    for r in csv.reader(opent(f)):
        if not r or r[0]=="ts_et": continue
        e=ptape(r[0])
        if e is None: continue
        try: p=int(float(r[2])); c=int(float(r[3]))
        except: continue
        if (r[4] if len(r)>4 else "")=="no" and p<=ref+2 and (onset is None or e<onset): fil.append((e,p,c))
    opps=[]; cur=None
    for (e,p,c) in fil:
        if cur and p<=cur["lvl"]+2 and e-cur["t2"]<120: cur["lots"]+=c; cur["t2"]=e; cur["lvl"]=max(cur["lvl"],p); cur["pmin"]=min(cur["pmin"],p)
        else:
            if cur: opps.append(cur)
            cur=dict(t=e,t2=e,lvl=p,pmin=p,lots=c)
    if cur: opps.append(cur)
    return opps

# metrics per box
def metrics(boxname, hours):
    legs=[tk for tk,d in L.items() if box_of(d)==boxname]
    ev=defaultdict(list)
    for tk in legs: ev[evkey(tk)].append(tk)
    nfill=sum(1 for tk in legs if L[tk]["fill"])
    m=dict(legs=len(legs),events=len(ev),fills=nfill,hours=hours,
            both=0,one=0,missed=0,comb=Counter(),terc=Counter(),cls=Counter(),
            gates=Counter(),pnl=0.0,settled_n=0,open_n=0)
    for tk in legs:
        d=L[tk]
        if d["fill"]:
            lts=tape_lts(tk,d["mlive"]); t=tercile(d["fill"][0][1],lts)
            if t: m["terc"][t]+=1
        for (ts,lb) in d["cancel"]:
            if lb in ("v4_t20m_fallback","no_fallback_fat_spread"): m["gates"][lb]+=1
        if d["skip"].get("itf_recent_volume_floor"): m["gates"]["itf_recent_volume_floor"]+=1
        if d["skip"].get("maker_only_no_late_entry"): m["gates"]["maker_only_no_late_entry"]+=1
        if d["settle"] is not None: m["pnl"]+=d["settle"]; m["settled_n"]+=1
        elif d["fill"]: m["open_n"]+=1
    for ek,ls in ev.items():
        both=[tk for tk in ls if L[tk]["fill"]]
        if len(both)==2:
            comb=L[both[0]]["fill"][0][1]+L[both[1]]["fill"][0][1]
            m["both"]+=1; m["comb"]["<=97" if comb<=97 else ("98-100" if comb<=100 else ">100")]+=1
        elif len(both)==1:
            m["one"]+=1
            kept=both[0]; miss=[tk for tk in ls if tk!=kept]
            if miss:
                mt=miss[0]; ref=max([p for (_,p) in L[mt]["placed"]]+[a[1] for a in L[mt]["place"] if a[1] is not None]+[0])
                opps=dedup_no(mt,ref,L[mt]["mlive"] or L[kept]["mlive"])
                if not L[mt]["placed"]: c="NEVER_LAID"
                elif opps: c=("TOO_DEEP" if max(p for (_,p) in L[mt]["placed"])<opps[0]["pmin"] else "PULLED")
                else: c="NO_OPP"
                m["cls"][c]+=1
        else: m["missed"]+=1
    return m

PH=(PRIOR[1]-PRIOR[0])/3600.0; CH=(CURRENT[1]-CURRENT[0])/3600.0
mp=metrics("PRIOR",PH); mc=metrics("CURRENT",CH)
def perday(n,h): return n/(h/24.0)
print(f"PRIOR window hours={PH:.1f}  CURRENT hours={CH:.1f} (current spans ~10h disk-crash outage)")
import json as _J
open("/tmp/compare_metrics.json","w").write(_J.dumps(dict(prior=mp,current=mc,PH=PH,CH=CH),default=str))
def row(lbl, a, b): print(f"  {lbl:26s} PRIOR {str(a):<24} | CURRENT {b}")
row("legs touched", f"{mp['legs']} ({perday(mp['legs'],PH):.0f}/day)", f"{mc['legs']} ({perday(mc['legs'],CH):.0f}/day)")
row("events", mp['events'], mc['events'])
row("fills", f"{mp['fills']} ({perday(mp['fills'],PH):.0f}/day)", f"{mc['fills']} ({perday(mc['fills'],CH):.0f}/day)")
row("pair both/one/missed", f"{mp['both']}/{mp['one']}/{mp['missed']}", f"{mc['both']}/{mc['one']}/{mc['missed']}")
comprate=lambda m: (100*m['both']/(m['both']+m['one']+m['missed'])) if (m['both']+m['one']+m['missed']) else 0
row("completion rate", f"{comprate(mp):.0f}%", f"{comprate(mc):.0f}%")
row("combined dist", dict(mp['comb']), dict(mc['comb']))
row("entry terciles", dict(mp['terc']), dict(mc['terc']))
row("one-sided class", dict(mp['cls']), dict(mc['cls']))
row("gate footprints", dict(mp['gates']), dict(mc['gates']))
row("P&L (settled, entry-boxed)", f"${mp['pnl']:.2f} (n={mp['settled_n']}, open={mp['open_n']})", f"${mc['pnl']:.2f} (n={mc['settled_n']}, open={mc['open_n']})")
row("P&L $/day (settled)", f"${perday(mp['pnl'],PH):.1f}", f"${perday(mc['pnl'],CH):.1f}")
import json as J
open("/tmp/compare_metrics.json","w").write(J.dumps(dict(prior=mp,current=mc,PH=PH,CH=CH),default=str))
print("wrote /tmp/compare_metrics.json")
