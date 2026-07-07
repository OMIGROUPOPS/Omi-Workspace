#!/usr/bin/env python3
"""AIM_V2 OPERATIONAL VALIDATION — ledger-day replay against the OPERATIONAL table
(PLEX_AIM_V2_RULING params), C46 two-lane, with the fallback chain's serving split
reported separately (steps by true-cell / tier2 / tier3 / NULL / dip-inadmissible).
Writes /tmp/aim_v2_val_op.json. GATED-OFF; nothing arms."""
import json, gzip, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
ROOT = Path(__file__).resolve().parents[1]
BIN=600; GOAL=97
T=json.loads((ROOT/"data/shape_corpus/aim_v2_operational_LATCHCAL.json").read_text())["table"]
led=json.load(open("/tmp/slate_ledger.json"))
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
        f=ROOT/"analysis"/"trades"/(tk+suf)
        if f.exists(): break
    else: return []
    op=gzip.open if f.suffix==".gz" else open
    rows=[]
    with op(f,"rt",encoding="utf-8",errors="replace") as fh:
        next(fh,None)
        for ln in fh:
            p=ln.rstrip("\n").split(",")
            if len(p)<5: continue
            t_=pts(p[0])
            if t_ is None: continue
            try: rows.append((t_,int(p[2]),int(float(p[3])),p[4]))
            except: continue
    rows.sort(); return rows
CATP={"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
      "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CATP.items() if tk.startswith(k)), None)
bands=defaultdict(list)
for LOG in ("/tmp/session_since_boot.jsonl", str(ROOT/"logs/live_v3_20260706.jsonl")):
    if not Path(LOG).exists(): continue
    for line in open(LOG,encoding="utf-8",errors="replace"):
        if '"v4_exit_posted"' not in line: continue
        try: o=json.loads(line)
        except: continue
        d=o.get("details",{})
        if d.get("entry_price") is not None and d.get("band_x") is not None:
            bands[(cat_of(o.get("ticker") or ""),int(d["entry_price"])//10)].append(int(d["band_x"]))
def med(v):
    v=sorted(x for x in v if x is not None); return v[len(v)//2] if v else None
band_map={k:med(v) for k,v in bands.items()}
def band_at(cat,px):
    for db in (0,1,2,3):
        for c2 in (int(px)//10-db,int(px)//10+db):
            b=band_map.get((cat,c2))
            if b is not None: return b
    return None
prepped=[]
for r in led["rows"]:
    hs=r.get("hs_ts"); ce=r.get("cor_end_ts")
    if not (hs and ce): continue
    hs=float(hs); ce=float(ce)
    legs=[l for l in r["legs"]]
    if len(legs)!=2: continue
    tks=["KX"+l["tk"] if not l["tk"].startswith("KX") else l["tk"] for l in legs]
    rows={tk:tape(tk) for tk in tks}
    if any(not v for v in rows.values()): continue
    posts=[float(l["conc_ts"]) for l in legs if l.get("conc_ts")]
    if not posts: continue
    prepped.append((r,hs,ce,tks,rows,min(posts)))
actual_pairs=sum(1 for r in led["rows"] if r["status"]=="SETTLED" and r["n_filled"]==2)
rode_tks=set(("KX"+l["tk"] if not l["tk"].startswith("KX") else l["tk"])
             for r in led["rows"] for l in r["legs"] if l.get("disp")=="RODE_TO_SETTLEMENT")
print(f"prepped {len(prepped)} | actual pairs {actual_pairs}",file=sys.stderr)

def run(q):
    res={"pairs":0,"le97":0,"combs":[],"lazy":0,"legs":0,"gold":0,"b3c":0,"b3n":0,
         "pnl_new":0.0,"pnl_old":0.0,"n_pnl":0,
         "serve":{"cell":0,"tier2":0,"tier3":0,"null":0,"dip_inadmissible":0}}
    for r,hs,ce,tks,rows,t0 in prepped:
        sim={tk:{"fill":None,"aim":None,"fv":None,"ft":None} for tk in tks}
        t=t0
        while t<ce:
            pre={tk:[x for x in rows[tk] if x[0]<=t] for tk in tks}
            if all(pre.values()):
                fav=max(tks,key=lambda tk:pre[tk][-1][1]); dog=[x for x in tks if x!=fav][0]
                fp=pre[fav][-1][1]
                cell=T.get(f"{r['cat']}|{min(4,max(0,fp//20))}|{int(max(0,(ce-t))//BIN)}")
                if not cell or cell.get("null_reason"):
                    res["serve"]["null"]+=1
                else:
                    res["serve"][cell["source"]]+=1
                    for tk,pfx in ((fav,"f"),(dog,"d")):
                        if sim[tk]["fill"] is not None: continue
                        p=pre[tk][-1][1]
                        dip=cell.get(f"{pfx}dip{q}")
                        drift=cell.get(f"{pfx}d")
                        if dip is None:
                            res["serve"]["dip_inadmissible"]+=1; continue
                        aim=max(1,p+dip)
                        oth=[x for x in tks if x!=tk][0]
                        if sim[oth]["fill"] is not None: aim=min(aim,GOAL-sim[oth]["fill"])
                        sim[tk]["aim"]=max(1,aim)
                        sim[tk]["fv"]=p+drift if drift is not None else None
                for tk in tks:
                    s=sim[tk]
                    if s["fill"] is not None or s["aim"] is None: continue
                    if any(pr<=s["aim"] for tt,pr,ct,sd_ in rows[tk] if sd_=="no" and t<=tt<t+BIN):
                        s["fill"]=s["aim"]; s["ft"]=t
                        if s["fv"] is not None and s["aim"]>=s["fv"]: res["lazy"]+=1
            t+=BIN
        filled=[tk for tk in tks if sim[tk]["fill"] is not None]
        res["legs"]+=len(filled)
        for tk in filled:
            if sim[tk]["ft"]<hs:
                b=band_at(r["cat"],sim[tk]["fill"])
                if b is not None and any(pr>=sim[tk]["fill"]+b for tt,pr,ct,sd_ in rows[tk] if sim[tk]["ft"]<tt<ce):
                    res["gold"]+=1
            if tk in rode_tks:
                res["b3n"]+=1
                b=band_at(r["cat"],sim[tk]["fill"])
                if b is not None and any(pr>=sim[tk]["fill"]+b for tt,pr,ct,sd_ in rows[tk] if sim[tk]["ft"]<tt<ce):
                    res["b3c"]+=1
        if len(filled)==2:
            comb=sum(sim[tk]["fill"] for tk in filled)
            res["pairs"]+=1; res["combs"].append(comb)
            if comb<=GOAL: res["le97"]+=1
        if r["status"]=="SETTLED":
            po=pn=0.0; ok=True
            for l in r["legs"]:
                tk="KX"+l["tk"] if not l["tk"].startswith("KX") else l["tk"]
                if l.get("pnl") is None: ok=False; continue
                po+=l["pnl"]
                if sim[tk]["fill"] is not None:
                    pn+=5*(100-sim[tk]["fill"])/100.0 if (l["pnl"]>0) else -5*sim[tk]["fill"]/100.0
            if ok: res["pnl_new"]+=pn; res["pnl_old"]+=po; res["n_pnl"]+=1
    res["comb_med"]=med(res["combs"])
    return res
out={}
for q in ("25","50"):
    out[q]=run(q)
    r=out[q]
    print(f"OP q{q}: pairs {r['pairs']}/{actual_pairs} le97 {r['le97']} comb {r['comb_med']} legs {r['legs']} "
          f"lazy {r['lazy']} gold {r['gold']} B3 {r['b3c']}/{r['b3n']} serve {r['serve']} "
          f"| $ {r['pnl_new']:+.2f} vs {r['pnl_old']:+.2f} (n={r['n_pnl']})",file=sys.stderr)
json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"),
           "actual_pairs":actual_pairs,"results":out},open("/tmp/aim_v2_val_op.json","w"))
print("DONE",file=sys.stderr)
