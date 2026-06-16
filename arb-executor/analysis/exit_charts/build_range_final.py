#!/usr/bin/env python3
"""C-RANGE-COMMIT: per-cell entry range/depth table + depth-over-time walk + noise gate.

DIRECTION-FREE: embeds NO direction-conditioning. Premarket direction died at Cut 0
(persist 50.5% = coin flip) and in-match momentum is a coin flip / mean-reverting --
this table is PURE RANGE/DEPTH, no "which side" signal anywhere.

Inputs (committed):
  - data/durable/per_minute_universe/per_minute_features_batch_*.parquet (197 batches)
    drift-envelope source: min_yes_ask_forward_to_match_start (per-ticker premarket dip
    floor T-4h->start), mid_close (anchor @ T-4h, mark @ T-20m), price_low (traded-low
    fill realism).
  - docs/policy/entry_table_percell.csv  sha256:97fc2e1c7e0aba8c30cd...
    current-maker baseline (bid_offset_cents + placement_minute per cell) = the
    incremental-EV reference and the gated-cell fallback.

Method (per cat): deep_raw[c] = median over legs in cell c of (anchor - min_ask_forward);
neighbor-smoothed to maxStep<=1 (exit-reseal seal bar). Incremental EV/leg vs current
maker = case-a basis saving (deep-cur, both fill) + case-b give-up (basis_cur - mid20,
only current fills), marked at mid@T-20m -> NET OF SLIDERS. GATE: a cell holds the
current offset when n<NMIN (adequacy) or incremental EV<=0 (no lift). Walk: deep target
at T-240, monotone ramp to D=1 (market) over the final hour. Output: docs/policy/
range_final_<CAT>.csv (c, final_target, cur_offset, incr_ev_c_per_leg, n, gated_to_current,
D@T-bucket...). Read-only; writes only docs/policy/.
"""
import pyarrow.dataset as ds, pandas as pd, numpy as np, os
from collections import defaultdict
CATS=["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL"]
POL="docs/policy"
BUCKETS=[240,180,120,90,60,40,30,20,10,5]
NMIN=20   # adequacy floor (rationale: <20 matches/cell -> per-cell EV is sampling noise)

d=ds.dataset("data/durable/per_minute_universe/per_minute_features.parquet")
A={}
def upd(tk,key,ttm,val,tgt,tol):
    if val is None: return
    r=A.setdefault(tk,{}); cur=r.get(key); dd=abs(ttm-tgt)
    if (cur is None or dd<cur[0]) and dd<=tol: r[key]=(dd,val)
sc=d.scanner(columns=["ticker","category","time_to_match_start_min","mid_close",
                      "price_low","min_yes_ask_forward_to_match_start"], batch_size=300000)
for b in sc.to_batches():
    tk=b.column(0).to_pylist(); cat=b.column(1).to_pylist(); ttm=b.column(2).to_pylist()
    mid=b.column(3).to_pylist(); plo=b.column(4).to_pylist(); mnf=b.column(5).to_pylist()
    for i in range(len(tk)):
        c=cat[i]; t=ttm[i]
        if c not in CATS or t is None: continue
        T=tk[i]; r=A.setdefault(T,{}); r["cat"]=c
        if mid[i] is not None: upd(T,"anchor",t,mid[i]*100,240,25); upd(T,"mid20",t,mid[i]*100,20,12)
        if mnf[i] is not None: upd(T,"rangelow",t,mnf[i]*100,240,25)
        if plo[i] is not None and 0<=t<=240:
            lo=plo[i]*100
            if lo>0: r["fwdlow"]=min(r.get("fwdlow",1e9),lo)
percell=defaultdict(lambda: defaultdict(list)); legs=defaultdict(list)
for tk,r in A.items():
    if "cat" not in r or "anchor" not in r: continue
    cat=r["cat"]; anchor=r["anchor"][1]; c=int(np.clip(round(anchor),5,94))
    if "rangelow" in r:
        dip=anchor-r["rangelow"][1]
        if dip>=0: percell[cat][c].append(dip)
    if "mid20" in r and "fwdlow" in r:
        legs[cat].append((c,anchor,r["fwdlow"],r["mid20"][1]))

def smooth_step1(raw):
    s=pd.Series({c:raw.get(c,np.nan) for c in range(5,95)}).interpolate(limit_direction="both")
    v=s.rolling(5,center=True,min_periods=1).median().round().tolist()
    for _ in range(6):
        for i in range(1,len(v)): v[i]=min(v[i],v[i-1]+1); v[i]=max(v[i],v[i-1]-1)
        for i in range(len(v)-2,-1,-1): v[i]=min(v[i],v[i+1]+1); v[i]=max(v[i],v[i+1]-1)
    return {c:int(max(1,v[i])) for i,c in enumerate(range(5,95))}

cur_tbl=pd.read_csv(f"{POL}/entry_table_percell.csv")
for cat in CATS:
    cur={int(r.c):(int(r.placement_minute),int(r.bid_offset_cents))
         for r in cur_tbl[cur_tbl.category==cat].itertuples()}
    deep_raw={c:float(np.median(v)) for c,v in percell[cat].items() if len(v)>=3}
    deep_s=smooth_step1(deep_raw)
    cellstat=defaultdict(lambda:{"n":0,"contrib":0.0})
    for (c,anchor,fwdlow,mid20) in legs[cat]:
        cu=cur.get(c,(240,deep_s[c]))[1]; dp=max(deep_s[c],cu)
        b_cur=anchor-cu; b_deep=anchor-dp; cellstat[c]["n"]+=1
        if fwdlow<=b_deep:   cellstat[c]["contrib"]+=(dp-cu)
        elif fwdlow<=b_cur:  cellstat[c]["contrib"]+=(b_cur-mid20)
    final={}; ev={}
    for c in range(5,95):
        n=cellstat[c]["n"]; inc=(cellstat[c]["contrib"]/n) if n else 0.0
        cu=cur.get(c,(240,deep_s[c]))[1]
        if n>=NMIN and inc>0.01 and deep_s[c]>cu: final[c]=deep_s[c]; ev[c]=inc
        else: final[c]=cu; ev[c]=0.0
    final=smooth_step1(final)
    rows=[]
    for c in range(5,95):
        D=final[c]; walk={}
        for t in BUCKETS: walk[t]=D if t>=60 else max(1,int(round(1+(D-1)*(t-5)/55.0)))
        prev=D
        for t in BUCKETS: walk[t]=min(walk[t],prev); prev=walk[t]
        cu=cur.get(c,(240,D))[1]
        rows.append({"c":c,"final_target":D,"cur_offset":cu,"incr_ev_c_per_leg":round(ev[c],3),
                     "n":cellstat[c]["n"],"gated_to_current":int(final[c]==cu and ev[c]==0.0),
                     **{f"D@T-{t}":walk[t] for t in BUCKETS}})
    out=pd.DataFrame(rows); out.to_csv(f"{POL}/range_final_{cat}.csv",index=False)
    dd=out.final_target.to_numpy()
    print(f"{cat}: wrote {POL}/range_final_{cat}.csv  deep_mean={dd.mean():.1f} maxStep={int(np.max(np.abs(np.diff(dd))))} "
          f"steps>1={int(np.sum(np.abs(np.diff(dd))>1))} changed={int((out.gated_to_current==0).sum())}/90")
print("[build done]")
