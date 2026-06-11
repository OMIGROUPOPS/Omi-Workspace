"""[C-GUARD-EV] T-20->gun rolling price guard on the unfilled-at-T-20 cohort.
READ-ONLY. Lineage: entry_minute_ev v1/v1b (8b0edf30); engine R1-gated verbatim.

Cohort: legs whose v3 sim is unfilled at T-20 (mode == miss_fallback -- the legs the
historical T-20 taker fallback converted), restricted to candle coverage (full-session
per-minute asks; the per_minute tape floor is T-20).
Policy simulated: walk minutes m = 19 -> 0 (gun); cross permitted at the FIRST m where
ask(m) <= ask(m+1) + G (rolling-60s guard); fill taker at ask(m); locked per-cell exit;
net = realized - 1c fee. Sweep G in {1,2,3,4}c.
Emit per (category, G) and overall: acceptance rate, accepted-subset net ROC, N, SE.
PRE-REGISTERED (Plex): accepted EV >= 0 after fee at some G -> part (ii) ships with
the EV-maximizing G; accepted EV < 0 at every G -> part (ii) DROPS (convert-at-T-20-
then-stop). Reported verbatim.
"""
import pyarrow.parquet as pq, pyarrow as pa
import glob, csv, collections, math, statistics, hashlib, os
from datetime import datetime
ROOT="/root/Omi-Workspace/arb-executor"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
TAPE=ROOT+"/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PBV1=ROOT+"/data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet"
LOCKED=ROOT+"/data/durable/per_minute_universe/path_b_v3_per_n_simulation.parquet"
CAND=ROOT+"/data/historical_pull/candlesticks"
NFLOOR=25; GS=[1,2,3,4]
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"

leg={}
for f in glob.glob(SPIKE+"/*_spike_perN.parquet"):
    cat=f.split("/")[-1].replace("_spike_perN.parquet","").upper()
    t=pq.read_table(f,columns=["ticker","anchor_price","size_qual_max_250","settlement_value"]).to_pandas()
    for r in t.itertuples():
        if r.anchor_price is None: continue
        ac=int(round(r.anchor_price*100)); ac=min(94,max(5,ac))
        sq=r.size_qual_max_250
        sqc=int(round(sq*100)) if (sq is not None and sq<=1.5) else (int(round(sq)) if sq is not None else 0)
        leg[r.ticker]=dict(cat=cat,anchor=ac,sq=sqc,
            win=(int(r.settlement_value)==1) if r.settlement_value is not None else False)
cohort=set(leg)
lut={}
_pb=pq.read_table(PBV1).to_pandas()
for r in _pb.loc[_pb.groupby(["category","anchor_regime"]).expected_improvement_cents.idxmax()].itertuples():
    lut[(r.category,r.anchor_regime)]=(int(r.placement_minute),int(r.bid_offset_cents))
exitr={}
for f in glob.glob(SPIKE+"/*_descriptive_1c.parquet"):
    cat=f.split("/")[-1].replace("_descriptive_1c.parquet","").upper()
    for r in pq.read_table(f).to_pandas().itertuples():
        exitr[(cat,int(r.cell_id))]=(int(r.best_exit_X),str(r.rule).startswith("exit at"))

cols=["ticker","time_to_match_start_min","yes_ask_close","price_close","price_low","price_high",
      "minute_has_trade","match_start_method","match_start_ts"]
def f100(x): return None if x is None else x*100.0
series=collections.defaultdict(list)
start={}
sc=pq.ParquetFile(TAPE)
for i in range(sc.metadata.num_row_groups):
    rg=sc.read_row_group(i,columns=cols)
    tk=rg.column("ticker").to_pylist(); tt=rg.column("time_to_match_start_min").to_pylist()
    ak=rg.column("yes_ask_close").to_pylist(); pcl=rg.column("price_close").to_pylist()
    plo=rg.column("price_low").to_pylist(); phi=rg.column("price_high").to_pylist()
    mh=rg.column("minute_has_trade").to_pylist(); ms=rg.column("match_start_method").to_pylist()
    mst=rg.column("match_start_ts").to_pylist()
    for j in range(len(tk)):
        t=tk[j]
        if t not in cohort or ms[j]=="unknown": continue
        a=tt[j]
        if a is None or not (0.0<a<=240.0): continue
        series[t].append((a,f100(ak[j]),f100(pcl[j]),f100(plo[j]),f100(phi[j]),bool(mh[j] and pcl[j] is not None)))
        if t not in start and mst[j] is not None:
            try: start[t]=mst[j].timestamp() if hasattr(mst[j],"timestamp") else float(mst[j])
            except Exception: pass

def realize(entry,win,X,is_exit,sq):
    if is_exit and sq>=entry+X: return X,True
    return ((99-entry) if win else -(entry-1)),False

INF=1e18
res={}
for tk,rows in series.items():
    if tk not in leg: continue
    rows.sort(key=lambda r:-r[0])
    traded=[r for r in rows if r[5]]
    if not traded: continue
    L=leg[tk]; anchor=L["anchor"]; cat=L["cat"]
    reg=band(anchor); pl,off=lut.get((cat,reg),(20,1)); bid=max(anchor-off,1)
    ask_by_ttm={r[0]:r[1] for r in rows if r[1] is not None}
    a_at=ask_by_ttm.get(pl)
    if a_at is not None and a_at<=bid:
        mode,entry,emin,taker="marketable_taker",int(round(a_at)),pl,True
    else:
        hit=None
        for (a,ak,pc_,pl_,ph,ht) in rows:
            if 20<=a<=pl:
                trig=min(ak if ak is not None else INF, pc_ if pc_ is not None else INF)
                if trig<=bid: hit=a; break
        if hit is not None: mode,entry,emin,taker="maker_resting",bid,hit,False
        else: mode,entry,emin,taker="miss_fallback",anchor,20,True
    X,isx=exitr.get((cat,anchor),(0,False))
    realized,_=realize(entry,L["win"],X,isx,L["sq"]); base,_=realize(anchor,L["win"],X,isx,L["sq"])
    res[tk]=dict(cat=cat,mode=mode,entry=entry,realized=realized,baseline=base,anchor=anchor)

# R1 gate
rl=[r["realized"] for r in res.values()]; en=[r["entry"] for r in res.values()]
bl=[r["baseline"] for r in res.values()]; an=[r["anchor"] for r in res.values()]
atlas=sum(bl)/sum(an)*100; maker=sum(rl)/sum(en)*100
dep=(sum(bl)+0.60*(sum(rl)-sum(bl)))/sum(en)*100
lk=pq.read_table(LOCKED).to_pandas(); lk["cat"]=lk.category.str.upper()
lkc=lk.groupby(["cat","anchor_price_cents"]).apply(lambda d:(d.realized_pnl_cents.sum()/d.entry_price_cents.sum()*100,len(d)),include_groups=False)
mine=collections.defaultdict(lambda:[0.0,0.0])
for tk,r in res.items(): m=mine[(r["cat"],r["anchor"])]; m[0]+=r["realized"]; m[1]+=r["entry"]
within2=tot=tailbad=0
for k,(lroc,ln) in lkc.items():
    if ln<NFLOOR: continue
    m=mine.get(k)
    if not m or m[1]==0: continue
    mroc=m[0]/m[1]*100; tot+=1; d=abs(mroc-lroc)
    if d<=2.0: within2+=1
    if d>5.0: tailbad+=1
g=(abs(dep-10.9)<=0.3) and ((within2/tot)>=0.90 if tot else False) and (tailbad==0)
print("R1: atlas=%.3f maker=%.3f dep=%.3f gate=%s"%(atlas,maker,dep,g))
if not g:
    print("R1 HALT"); raise SystemExit(1)

# ---- guard walk on miss_fallback legs with candle coverage ----
agg=collections.defaultdict(lambda:dict(acc_net=[],acc_caps=[],n_cohort=0,conv_min=[]))
n_mf=n_cand=0
for tk,r in res.items():
    if r["mode"]!="miss_fallback": continue
    n_mf+=1
    st=start.get(tk)
    p=os.path.join(CAND,tk+".csv")
    if st is None or not os.path.exists(p): continue
    asks={}
    try:
        for row in csv.DictReader(open(p)):
            try:
                ts=int(row["end_period_ts"]); a=row.get("yes_ask_close_dollars","")
                if not a: continue
                mins=(st-ts)/60.0
                if -1.0<=mins<=25.0:
                    m=int(mins) if mins>=0 else 0
                    if m not in asks or mins<asks[m][0]:
                        asks[m]=(mins,float(a)*100.0)
            except Exception: continue
    except Exception: continue
    if not asks: continue
    n_cand+=1
    L=leg[tk]; cat=r["cat"]
    for G in GS:
        a=agg[(cat,G)]; a["n_cohort"]+=1
        conv=None
        for m in range(19,-1,-1):
            cur=asks.get(m); prior=asks.get(m+1)
            if cur is None or prior is None: continue
            if cur[1] <= prior[1]+G:
                conv=(m,cur[1]); break
        if conv is None: continue
        m,askc=conv
        entry=int(round(askc))
        if entry<1 or entry>=100: continue
        cell=min(94,max(5,entry))
        X,isx=exitr.get((cat,cell),(0,False))
        gr,_=realize(entry,L["win"],X,isx,L["sq"])
        a["acc_net"].append(gr-1.0); a["acc_caps"].append(entry); a["conv_min"].append(m)
print("miss_fallback legs=%d with candle coverage=%d"%(n_mf,n_cand))

rows_out=[]; S=[]; A=S.append
A("[C-GUARD-EV] rolling-60s price guard, T-19->gun, unfilled-at-T-20 cohort")
A("engine R1 PASS (atlas %.3f / maker %.3f / deployed %.3f)"%(atlas,maker,dep))
A("cohort: %d miss_fallback legs, %d with candle coverage"%(n_mf,n_cand))
A("")
A("per (category, G): acceptance / accepted net ROC / N / SE / median conv minute")
best={}
for (cat,G),a in sorted(agg.items()):
    n=len(a["acc_net"]); nc=a["n_cohort"]
    roc=sum(a["acc_net"])/sum(a["acc_caps"])*100 if a["acc_caps"] else None
    sd=statistics.stdev(a["acc_net"]) if n>=2 else None
    se=(sd/math.sqrt(n))/(sum(a["acc_caps"])/n)*100 if (sd is not None and a["acc_caps"]) else None
    cm=sorted(a["conv_min"])[n//2] if n else None
    rows_out.append(dict(category=cat,G=G,n_cohort=nc,n_accepted=n,
        acceptance_rate=round(n/nc,4) if nc else None,
        accepted_net_roc_pct=round(roc,3) if roc is not None else None,
        accepted_se_pp=round(se,3) if se is not None else None,
        median_conversion_minute=cm))
    A("  %-10s G=%dc  acc %5.1f%%  net ROC %+7.3f%%  N=%4d  SE %.3fpp  conv@T-%s"%(
        cat,G,100*n/max(nc,1),roc if roc is not None else float("nan"),n,
        se if se is not None else float("nan"),cm))
A("")
A("overall per G (N-wtd):")
for G in GS:
    nets=[];caps=[];nc=0
    for (cat,g2),a in agg.items():
        if g2!=G: continue
        nets+=a["acc_net"];caps+=a["acc_caps"];nc+=a["n_cohort"]
    if not nets:
        A("  G=%dc: no acceptances"%G); continue
    roc=sum(nets)/sum(caps)*100
    sd=statistics.stdev(nets) if len(nets)>=2 else float("nan")
    se=(sd/math.sqrt(len(nets)))/(sum(caps)/len(nets))*100
    best[G]=(roc,se,len(nets),100*len(nets)/nc)
    A("  G=%dc: acc %5.1f%%  accepted net ROC %+7.3f%%  (SE %.3fpp, N=%d)"%(G,100*len(nets)/nc,roc,se,len(nets)))
A("")
if best:
    gstar=max(best,key=lambda g:best[g][0])
    roc,se,n,acc=best[gstar]
    if roc>=0:
        A("PRE-REGISTERED BAR: accepted-subset EV >= 0 after fee at G=%dc (%.3f%%) -> part (ii) SHIPS with G=%dc"%(gstar,roc,gstar))
    else:
        A("PRE-REGISTERED BAR: accepted-subset EV < 0 at every G (best G=%dc -> %.3f%%) -> part (ii) DROPS; policy = convert-at-T-20-then-stop"%(gstar,roc))
tbl=pa.Table.from_pylist(rows_out)
OUTP="/tmp/entry_guard_ev_v1.parquet"
pq.write_table(tbl,OUTP)
sha=hashlib.sha256(open(OUTP,"rb").read()).hexdigest()
A("")
A("parquet %s"%OUTP)
A("sha256 %s"%sha)
open("/tmp/entry_guard_ev_summary.txt","w").write("\n".join(S)+"\n")
print("\n".join(S))
