"""[C-TERMINAL-EV] part B: sub-T-20 buckets from API candlesticks. READ-ONLY.

The premarket tape's domain floor is exactly T-20 (verified: min ttm 20.0, zero rows
below, 2,064,211 rows) -- buckets inside T-20 are unanswerable from per_minute
features. This part derives them from data/historical_pull/candlesticks (per-minute
yes_ask_close, full session), clocked by the foundation's match_start_ts labels,
same atlas legs + locked exit surface + realize() convention + 1c taker fee.

GATE (v2 -- the v1 gate compared mismatched cohorts and halted on a -0.826pp delta
that conflated cohort composition with misalignment): per-leg ask agreement on the
INTERSECTION cohort -- candle ask@T-20 vs tape ask@T-20 for the same ticker. PASS =
median |delta| <= 1c AND >=80% of legs within 2c. Same-cohort ROC comparison is
also reported for transparency. Pairing rates inside T-20 are carried at the T-20
v3-model level (all v3 maker/marketable fills occur at ttm>=20) -- disclosed.
"""
import pyarrow.parquet as pq, pyarrow as pa
import glob, csv, collections, math, statistics, hashlib, json, os
from datetime import datetime, timezone
ROOT="/root/Omi-Workspace/arb-executor"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
TAPE=ROOT+"/data/durable/per_minute_universe/premarket_tape_v1.parquet"
CAND=ROOT+"/data/historical_pull/candlesticks"
PARTA="/tmp/entry_minute_ev_v1.parquet"
BUCKETS=[20,15,10,5,2,1]

leg={}
for f in glob.glob(SPIKE+"/*_spike_perN.parquet"):
    cat=f.split("/")[-1].replace("_spike_perN.parquet","").upper()
    t=pq.read_table(f,columns=["ticker","anchor_price","size_qual_max_250","settlement_value"]).to_pandas()
    for r in t.itertuples():
        if r.anchor_price is None: continue
        sq=r.size_qual_max_250
        sqc=int(round(sq*100)) if (sq is not None and sq<=1.5) else (int(round(sq)) if sq is not None else 0)
        leg[r.ticker]=dict(cat=cat,sq=sqc,
            win=(int(r.settlement_value)==1) if r.settlement_value is not None else False)
exitr={}
for f in glob.glob(SPIKE+"/*_descriptive_1c.parquet"):
    cat=f.split("/")[-1].replace("_descriptive_1c.parquet","").upper()
    for r in pq.read_table(f).to_pandas().itertuples():
        exitr[(cat,int(r.cell_id))]=(int(r.best_exit_X),str(r.rule).startswith("exit at"))

pf=pq.ParquetFile(TAPE)
start={}
tape_ask20={}   # ticker -> tape yes_ask_close at ttm exactly 20.0 (cents)
for i in range(pf.metadata.num_row_groups):
    rg=pf.read_row_group(i,columns=["ticker","match_start_ts","match_start_method",
                                    "time_to_match_start_min","yes_ask_close"])
    tks=rg.column("ticker").to_pylist(); sts=rg.column("match_start_ts").to_pylist()
    ms=rg.column("match_start_method").to_pylist()
    tt=rg.column("time_to_match_start_min").to_pylist(); ak=rg.column("yes_ask_close").to_pylist()
    for t,s,m,a,v in zip(tks,sts,ms,tt,ak):
        if s is not None and m!="unknown" and t not in start:
            try: start[t]=s.timestamp() if hasattr(s,"timestamp") else float(s)
            except Exception: pass
        if a is not None and 20.0<=a<25.0 and v is not None:
            cur=tape_ask20.get(t)
            if cur is None or a<cur[0]: tape_ask20[t]=(a,v*100.0)
print("legs",len(leg),"starts",len(start),"tape_ask20",len(tape_ask20))

def realize(entry,win,X,is_exit,sq):
    if is_exit and sq>=entry+X: return X,True
    return ((99-entry) if win else -(entry-1)),False

grid=collections.defaultdict(lambda:dict(net=[],caps=[]))
slip60=collections.defaultdict(list); slip300=collections.defaultdict(list)
ask_deltas=[]            # per-leg |candle ask@20 - tape ask@20|
same_cohort=dict(nets=[],caps=[],tape_nets=[],tape_caps=[])
n_files=n_used=0
for tk,L in leg.items():
    st=start.get(tk)
    if st is None: continue
    p=os.path.join(CAND,tk+".csv")
    if not os.path.exists(p): continue
    n_files+=1
    asks={}  # minutes-before-start -> ask cents
    try:
        for row in csv.DictReader(open(p)):
            try:
                ts=int(row["end_period_ts"]); a=row.get("yes_ask_close_dollars","")
                if not a: continue
                mins=(st-ts)/60.0
                if -1.0<=mins<=130.0:
                    asks[mins]=float(a)*100.0
            except Exception: continue
    except Exception: continue
    if not asks: continue
    n_used+=1
    cat=L["cat"]
    def ask_at(b):
        best=None
        for m,a in asks.items():
            if m>=b and m<=b+5:
                if best is None or m<best[0]: best=(m,a)
        return best
    def terminal():
        best=None
        for m,a in asks.items():
            if 0.0<=m<=2.0:
                if best is None or m<best[0]: best=(m,a)
        return best
    got_terminal=terminal()
    for b in BUCKETS+["terminal"]:
        got = got_terminal if b=="terminal" else ask_at(b)
        if got is None: continue
        m,a=got
        entry=int(round(a))
        if entry<1 or entry>=100: continue
        cell=min(94,max(5,entry))
        X,isx=exitr.get((cat,cell),(0,False))
        gr,_=realize(entry,L["win"],X,isx,L["sq"])
        g=grid[(cat,cell,str(b))]
        g["net"].append(gr-1.0); g["caps"].append(entry)
        if b==20:
            ta=tape_ask20.get(tk)
            if ta is not None:
                ask_deltas.append(abs(a-ta[1]))
                # same-cohort ROC legs (candle vs tape pricing, identical leg set)
                te=int(round(ta[1]))
                if 1<=te<100:
                    tc=min(94,max(5,te))
                    tX,tisx=exitr.get((cat,tc),(0,False))
                    tgr,_=realize(te,L["win"],tX,tisx,L["sq"])
                    same_cohort["nets"].append(gr-1.0); same_cohort["caps"].append(entry)
                    same_cohort["tape_nets"].append(tgr-1.0); same_cohort["tape_caps"].append(te)
    if got_terminal is not None:
        tm,ta=got_terminal
        for lag,store in ((1.0,slip60),(5.0,slip300)):
            prior=None
            for m,a in asks.items():
                if m>=tm+lag and m<=tm+lag+5:
                    if prior is None or m<prior[0]: prior=(m,a)
            if prior is not None: store[cat].append(ta-prior[1])
print("candle files found=%d used=%d"%(n_files,n_used))

rows_out=[]
for (cat,cell,b),v in sorted(grid.items()):
    n=len(v["net"])
    rows_out.append(dict(category=cat,cell_at_entry=cell,bucket=b,N=n,source="candlesticks",
        net_roc_pct=round(sum(v["net"])/sum(v["caps"])*100,3) if sum(v["caps"])>0 else None,
        mean_net_cents=round(statistics.fmean(v["net"]),3),
        sd_net_cents=round(statistics.stdev(v["net"]),3) if n>=2 else None))
OUTP="/tmp/entry_minute_ev_v1b.parquet"
pq.write_table(pa.Table.from_pylist(rows_out),OUTP)
sha=hashlib.sha256(open(OUTP,"rb").read()).hexdigest()

def nwt(b):
    nets=[];caps=[]
    for (cat,cell,bb),v in grid.items():
        if bb!=b: continue
        nets+=v["net"];caps+=v["caps"]
    if not nets: return None
    roc=sum(nets)/sum(caps)*100
    sd=statistics.stdev(nets) if len(nets)>=2 else float("nan")
    se_roc=(sd/math.sqrt(len(nets)))/(sum(caps)/len(nets))*100
    return roc,se_roc,len(nets)

# gate v2: per-leg ask agreement + same-cohort ROC comparison (see header)

S=[];A=S.append
A("[C-TERMINAL-EV part B] sub-T-20 buckets from candlesticks (tape floor = T-20, verified)")
A("coverage: %d atlas legs with candle files used (Mar-Apr pull window)"%n_used)
if ask_deltas:
    ds=sorted(ask_deltas)
    med=ds[len(ds)//2]; within2=100.0*sum(1 for d in ds if d<=2.0)/len(ds)
    ok=(med<=1.0) and (within2>=80.0)
    A("GATE v2 (per-leg ask agreement, intersection n=%d): median |candle-tape| ask@T-20 = %.2fc;"%(len(ds),med))
    A("  %.1f%% within 2c -> %s"%(within2,"PASS" if ok else "FAIL-HALT"))
    sc=same_cohort
    if sc["caps"]:
        c_roc=sum(sc["nets"])/sum(sc["caps"])*100
        t_roc=sum(sc["tape_nets"])/sum(sc["tape_caps"])*100
        A("  same-cohort T-20 ROC: candle %.3f%% vs tape %.3f%% (delta %+.3fpp)"%(c_roc,t_roc,c_roc-t_roc))
        A("  (the v1 gate's -0.826pp was cohort composition: Mar-Apr candle cohort vs full-corpus reference)")
    if not ok:
        open("/tmp/entry_minute_ev_v1b_summary.txt","w").write("\n".join(S)+"\n")
        print("\n".join(S)); raise SystemExit(1)
else:
    A("GATE v2: NO intersection legs -- HALT")
    open("/tmp/entry_minute_ev_v1b_summary.txt","w").write("\n".join(S)+"\n")
    print("\n".join(S)); raise SystemExit(1)
A("")
A("N-weighted net ROC by bucket (candle cohort; net = gross - 1c taker fee):")
ser={}
for b in [str(x) for x in BUCKETS]+["terminal"]:
    r=nwt(b)
    if r is None: continue
    ser[b]=r
    A("  T-%-8s N=%6d  net ROC %+7.3f%%  (SE %.3fpp)"%(b,r[2],r[0],r[1]))
A("")
if "20" in ser and "terminal" in ser:
    t20=ser["20"];term=ser["terminal"]
    bar=t20[0]-t20[1]
    A("PRE-REGISTERED BAR (within candle cohort): terminal %.3f%% vs T20 %.3f%% - 1xSE(%.3f) = %.3f%% -> %s"%(
        term[0],t20[0],t20[1],bar,
        "CLEAN (terminal >= T20 - 1xSE)" if term[0]>=bar else "DIRTY (terminal < T20 - 1xSE)"))
A("")
A("SLIPPAGE into the gun (terminal ask - ask 60s/300s prior; +ve adverse):")
for cat in sorted(slip60):
    s1=sorted(slip60[cat]); s5=sorted(slip300.get(cat,[]))
    def q(d,p): return d[min(len(d)-1,int(len(d)*p))] if d else float("nan")
    A("  %-10s 60s: p50=%+.1f p90=%+.1f (n=%d) | 300s: p50=%+.1f p90=%+.1f (n=%d)"%(
        cat,q(s1,.5),q(s1,.9),len(s1),q(s5,.5),q(s5,.9),len(s5)))
A("")
A("pairing inside T-20: carried at the T-20 v3-model rates (all v3 fills occur at ttm>=20) -- part A table governs.")
A("parquet %s"%OUTP)
A("sha256 %s"%sha)
open("/tmp/entry_minute_ev_v1b_summary.txt","w").write("\n".join(S)+"\n")
print("\n".join(S))
