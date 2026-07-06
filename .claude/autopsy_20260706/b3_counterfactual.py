#!/usr/bin/env python3
"""[READ-ONLY] B3 DISCOUNT COUNTERFACTUAL — the 43 rode legs vs their own lows.
Conservative fill convention: a maker bid at X counts FILLED only if the tape PRINTED
at <= X inside the window (no credit the tape doesn't support; single-print lows are
sub-flagged for queue risk). Windows on the HONEST clock from the ledger rows
(hs_ts; corridor end = cor_end_ts). band_x at a counterfactual fill = empirical
per-(cat, price-bucket) median from this session's own v4_exit_posted records.
Writes /tmp/b3_cf.json."""
import json, sys, gzip
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
LOGS = ["/tmp/session_since_boot.jsonl", "logs/live_v3_20260706.jsonl"]
led = json.load(open("/tmp/slate_ledger.json"))

# empirical band map: (cat, px//10) -> median band_x from v4_exit_posted
bands = defaultdict(list)
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), None)
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for line in open(LOG, encoding="utf-8", errors="replace"):
        if '"v4_exit_posted"' not in line: continue
        try: o=json.loads(line)
        except: continue
        d=o.get("details",{}); tk=o.get("ticker") or ""
        if d.get("entry_price") is not None and d.get("band_x") is not None:
            bands[(cat_of(tk), int(d["entry_price"])//10)].append(int(d["band_x"]))
def med(v):
    v=sorted(v); return v[len(v)//2] if v else None
band_map={k: med(v) for k,v in bands.items()}
def band_at(cat, px):
    b=band_map.get((cat, int(px)//10))
    if b is not None: return b
    # nearest bucket fallback (stated in doc)
    for db in (1,2,3):
        for c2 in (int(px)//10-db, int(px)//10+db):
            b=band_map.get((cat,c2))
            if b is not None: return b
    return None

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
            try: rows.append((t,int(p[2]),int(float(p[3]))))
            except: continue
    rows.sort(); return rows

def analyze(r, l, kind):
    tk="KX"+l["tk"] if not l["tk"].startswith("KX") else l["tk"]
    hs=float(r["hs_ts"]) if r.get("hs_ts") else None
    ce=float(r["cor_end_ts"]) if r.get("cor_end_ts") else None
    ft=float(l["fill_ts"]) if l.get("fill_ts") else None
    rows=tape(tk)
    out={"ev":r["ev"],"tk":tk[-18:],"cat":r["cat"],"kind":kind,"fill":l["vw"],"qty":l["qty"],
         "pnl":l.get("pnl"),"winner":bool((l.get("pnl") or 0)>0),"hs":hs is not None,"ce":ce is not None}
    if not (hs and ce and rows):
        out["nodata"]=True; return out
    w4=[x for x in rows if hs-4*3600<=x[0]<ce]
    w8=[x for x in rows if hs-8*3600<=x[0]<hs-4*3600]
    out["t8_coverage"]=bool(rows and rows[0][0]<=hs-4*3600)
    out["t8_prints"]=len(w8)
    if not w4:
        out["no_w4_tape"]=True; return out
    low=min(pr for _,pr,_ in w4)
    lts=next(t for t,pr,_ in w4 if pr==low)
    out["low_t4"]=low
    out["low_prints"]=sum(1 for _,pr,_ in w4 if pr<=low)
    out["single_print_low"]=out["low_prints"]<2
    out["missed_disc"]=round((l["vw"] or 0)-low,1)
    out["low_vs_fill_min"]=round((lts-ft)/60,1) if ft else None
    if w8:
        low8=min(pr for _,pr,_ in w8)
        out["low_t8"]=low8; out["t8_extra_disc"]=round(low-low8,1)
    # counterfactual at three depths (fill at cf level when tape prints <= level; time = first such print)
    cf={}
    for dth in (0,1,2):
        lvl=low+dth
        ct=next((t for t,pr,_ in w4 if pr<=lvl), None)   # always exists (low printed)
        b=band_at(r["cat"], lvl)
        touch_w1=touch_cor=False
        if b is not None and ct is not None:
            ex=lvl+b
            for t,pr,_ in rows:
                if t<=ct: continue
                if t>=ce: break
                if pr>=ex:
                    if t<hs: touch_w1=True
                    touch_cor=True
                    break
        q=l["qty"] or 5
        if touch_w1 or touch_cor:
            newp=round((b)*q/100.0,2)   # cashed at band
            conv="W1" if touch_w1 else "COR"
        else:
            newp=round(((100-lvl) if out["winner"] else (-lvl))*q/100.0,2)  # rides at cf basis
            conv="NO"
        cf[f"d{dth}"]={"lvl":lvl,"band":b,"conv":conv,"new_pnl":newp,
                       "delta_vs_actual":round(newp-(l.get("pnl") or 0),2)}
    out["cf"]=cf
    # band distance from LOW (col for table 5)
    b0=band_at(r["cat"], low)
    out["band_from_low"]=b0
    return out

rode=[]; gold=[]
for r in led["rows"]:
    if r["status"]!="SETTLED": continue
    for l in r["legs"]:
        if l.get("vw") is None: continue
        if l.get("disp")=="RODE_TO_SETTLEMENT":
            # only B3 pairs: event has 2 filled legs
            if sum(1 for x in r["legs"] if x.get("vw") is not None)==2:
                rode.append(analyze(r,l,"RODE"))
        elif (l.get("disp") in ("EXIT_FILLED_W1","EXIT_FILLED_CORRIDOR")
              and l.get("w1_filled")):
            gold.append(analyze(r,l,"GOLD"))
print(f"rode analyzed={len(rode)} gold={len(gold)} band_map cells={len(band_map)}",file=sys.stderr)
json.dump({"generated":datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S ET"),
           "rode":rode,"gold":gold,
           "band_map":{f"{k[0]}|{k[1]}":v for k,v in band_map.items()}},
          open("/tmp/b3_cf.json","w"),default=str)
# quick rollup
ok=[x for x in rode if x.get("cf")]
for d in ("d0","d1","d2"):
    w1=sum(1 for x in ok if x["cf"][d]["conv"]=="W1")
    cor=sum(1 for x in ok if x["cf"][d]["conv"]=="COR")
    no=sum(1 for x in ok if x["cf"][d]["conv"]=="NO")
    rec=sum(x["cf"][d]["delta_vs_actual"] for x in ok)
    print(f"{d}: W1-conv {w1} COR-conv {cor} no-conv {no} | delta vs actual ${rec:+.2f}",file=sys.stderr)
print(f"no-tape legs: {sum(1 for x in rode if x.get('no_w4_tape') or x.get('nodata'))}",file=sys.stderr)
print(f"T8 coverage: {sum(1 for x in rode if x.get('t8_coverage'))}/{len(rode)} legs, prints {sum(x.get('t8_prints',0) for x in rode)}",file=sys.stderr)
