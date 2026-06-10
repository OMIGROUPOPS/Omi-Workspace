"""[C-TERMINAL-EV] Entry-minute EV decomposition -- taker entries by minute bucket.
READ-ONLY (writes /tmp + durable parquet at commit time). Q1/Q2 fence: conversion-
timing economics only; bid pricing untouched.

Engine: validated Path B v3 replay lineage (entry_completion_sd_addendum_v1 /
1944b250), verbatim leg+tape+sim construction. GATES: full R1 equivalence (atlas
8.699 / maker 12.110 / deployed 10.949 reproduction; HALT on fail). SPEC PATCH
(disclosed): the prompt's "T-20 bucket must reproduce the deployed 10.9%" is
implemented as (a) anchor-entry reproduction of the locked atlas 8.70 baseline --
the number the deployed 10.9 blend anchors on -- plus the full R1 gate; a pure
T-20 taker-at-ask bucket sits below the anchor baseline by the spread cost and is
reported as the bucket series' own T-20 row.

Buckets: taker fill at prevailing yes ask at ttm in {120,60,30,20,15,10,5,2} (+
terminal = last ask with ttm<=2). Exit: locked per-cell surface keyed on the
cell-at-entry; realize() convention identical to the completion engine; net = -1c
taker fee. Sibling-pairing model: the v3 engine's own sibling sim (maker/marketable
fills only), filled-by-bucket if its fill minute (ttm) >= bucket ttm.
"""
import pyarrow.parquet as pq, pyarrow as pa
import glob, collections, math, statistics, hashlib, json, os
ROOT="/root/Omi-Workspace/arb-executor"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
TAPE=ROOT+"/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PBV1=ROOT+"/data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet"
LOCKED=ROOT+"/data/durable/per_minute_universe/path_b_v3_per_n_simulation.parquet"
NFLOOR=25
BUCKETS=[120,60,30,20,15,10,5,2]   # + terminal handled separately
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"

# ---- atlas legs (VERBATIM lineage) ----
leg={}
for f in glob.glob(SPIKE+"/*_spike_perN.parquet"):
    cat=f.split("/")[-1].replace("_spike_perN.parquet","").upper()
    t=pq.read_table(f,columns=["ticker","event_ticker","partner_ticker","anchor_price","size_qual_max_250","settlement_value"]).to_pandas()
    for r in t.itertuples():
        if r.anchor_price is None: continue
        ac=int(round(r.anchor_price*100)); ac=min(94,max(5,ac))
        sq=r.size_qual_max_250
        sqc=int(round(sq*100)) if (sq is not None and sq<=1.5) else (int(round(sq)) if sq is not None else 0)
        leg[r.ticker]=dict(cat=cat,event=r.event_ticker,partner=r.partner_ticker,anchor=ac,sq=sqc,
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
print("legs",len(leg),"lut",len(lut),"exitr",len(exitr))

cols=["ticker","time_to_match_start_min","yes_ask_close","price_close","price_low","price_high",
      "minute_has_trade","match_start_method"]
def f100(x): return None if x is None else x*100.0
series=collections.defaultdict(list)
sc=pq.ParquetFile(TAPE)
for i in range(sc.metadata.num_row_groups):
    rg=sc.read_row_group(i,columns=cols)
    tk=rg.column("ticker").to_pylist(); tt=rg.column("time_to_match_start_min").to_pylist()
    ak=rg.column("yes_ask_close").to_pylist(); pcl=rg.column("price_close").to_pylist()
    plo=rg.column("price_low").to_pylist(); phi=rg.column("price_high").to_pylist()
    mh=rg.column("minute_has_trade").to_pylist(); ms=rg.column("match_start_method").to_pylist()
    for j in range(len(tk)):
        t=tk[j]
        if t not in cohort or ms[j]=="unknown": continue
        a=tt[j]
        if a is None or not (0.0<a<=240.0): continue
        series[t].append((a,f100(ak[j]),f100(pcl[j]),f100(plo[j]),f100(phi[j]),bool(mh[j] and pcl[j] is not None)))
print("tape tickers",len(series))

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
    res[tk]=dict(cat=cat,mode=mode,entry=entry,emin=emin,realized=realized,baseline=base,
        anchor=anchor,ask_by_ttm=ask_by_ttm)
print("simulated legs",len(res))

# ===== R1 EQUIVALENCE GATE (verbatim tolerances) =====
rl=[r["realized"] for r in res.values()]; en=[r["entry"] for r in res.values()]
bl=[r["baseline"] for r in res.values()]; an=[r["anchor"] for r in res.values()]
atlas=sum(bl)/sum(an)*100; maker=sum(rl)/sum(en)*100
dep=(sum(bl)+0.60*(sum(rl)-sum(bl)))/sum(en)*100
print("=== R1 === atlas=%.3f maker=%.3f deployed=%.3f"%(atlas,maker,dep))
lk=pq.read_table(LOCKED).to_pandas(); lk["cat"]=lk.category.str.upper()
lkc=lk.groupby(["cat","anchor_price_cents"]).apply(lambda d:(d.realized_pnl_cents.sum()/d.entry_price_cents.sum()*100,len(d)),include_groups=False)
mine=collections.defaultdict(lambda:[0.0,0.0,0])
for tk,r in res.items(): m=mine[(r["cat"],r["anchor"])]; m[0]+=r["realized"]; m[1]+=r["entry"]; m[2]+=1
within2=tot=tailbad=0
for k,(lroc,ln) in lkc.items():
    if ln<NFLOOR: continue
    m=mine.get(k)
    if not m or m[1]==0: continue
    mroc=m[0]/m[1]*100; tot+=1; d=abs(mroc-lroc)
    if d<=2.0: within2+=1
    if d>5.0: tailbad+=1
g=(abs(dep-10.9)<=0.3) and ((within2/tot)>=0.90 if tot else False) and (tailbad==0)
print("gate: dep_ok=%s within2=%.1f%% tail=%d -> %s"%(abs(dep-10.9)<=0.3,100*within2/max(tot,1),tailbad,g))
if not g:
    print("EQUIVALENCE HALT."); raise SystemExit(1)
print("R1 PASS (atlas anchor-baseline %.3f%% is the locked T-20 reference)"%atlas)

# ===== bucket simulation =====
def ask_at(r, b):
    """latest ask at ttm >= b within b+5 (minute-bar staleness bound)."""
    best=None
    for ttm,ask in r["ask_by_ttm"].items():
        if ttm>=b and ttm<=b+5 and ask is not None:
            if best is None or ttm<best[0]: best=(ttm,ask)
    return best

def ask_terminal(r):
    best=None
    for ttm,ask in r["ask_by_ttm"].items():
        if ttm<=2 and ask is not None:
            if best is None or ttm<best[0]: best=(ttm,ask)
    return best

grid=collections.defaultdict(lambda:dict(net=[],gross=[]))
slip60=collections.defaultdict(list); slip300=collections.defaultdict(list)
pair=collections.defaultdict(lambda:[0,0])   # (cat,bucket) -> [sib_filled, n]
for tk,r in res.items():
    L=leg[tk]; cat=r["cat"]; sib=L["partner"]; r2=res.get(sib)
    for b in BUCKETS+["terminal"]:
        got = ask_terminal(r) if b=="terminal" else ask_at(r,b)
        if got is None: continue
        ttm,ask=got
        entry=int(round(ask))
        if entry<1 or entry>=100: continue
        cell=min(94,max(5,entry))
        X,isx=exitr.get((cat,cell),(0,False))
        gr,_=realize(entry,L["win"],X,isx,L["sq"])
        net=gr-1.0   # taker fee
        gkey=(cat,cell,str(b))
        grid[gkey]["net"].append((net,entry)); grid[gkey]["gross"].append(gr)
        # pairing
        if r2 is not None and r2["mode"]!="miss_fallback":
            bt = ttm
            pk=(cat,str(b)); pair[pk][1]+=1
            if r2["emin"]>=bt: pair[pk][0]+=1
        else:
            pk=(cat,str(b)); pair[pk][1]+=1
    # slippage into the gun
    t=ask_terminal(r)
    if t is not None:
        tt,ta=t
        for lag,store in ((1,slip60),(5,slip300)):
            prior=None
            for ttm,ask in r["ask_by_ttm"].items():
                if ttm>=tt+lag and ttm<=tt+lag+5 and ask is not None:
                    if prior is None or ttm<prior[0]: prior=(ttm,ask)
            if prior is not None:
                store[cat].append(ta-prior[1])

rows_out=[]
for (cat,cell,b),v in sorted(grid.items()):
    nets=[x[0] for x in v["net"]]; caps=[x[1] for x in v["net"]]
    n=len(nets)
    rows_out.append(dict(category=cat,cell_at_entry=cell,bucket=b,N=n,
        net_roc_pct=round(sum(nets)/sum(caps)*100,3) if sum(caps)>0 else None,
        mean_net_cents=round(statistics.fmean(nets),3),
        sd_net_cents=round(statistics.stdev(nets),3) if n>=2 else None,
        mean_gross_cents=round(statistics.fmean(v["gross"]),3)))
tbl=pa.Table.from_pylist(rows_out)
OUTP="/tmp/entry_minute_ev_v1.parquet"
pq.write_table(tbl,OUTP)
sha=hashlib.sha256(open(OUTP,"rb").read()).hexdigest()

# ===== summary =====
S=[]; A=S.append
A("[C-TERMINAL-EV] taker entry by minute bucket -- locked exit surface, R1-gated engine")
A("R1 PASS: atlas %.3f / maker %.3f / deployed %.3f (reproduction gate)"%(atlas,maker,dep))
A("SPEC PATCH (disclosed): T-20 gate anchors on the locked atlas 8.70 (anchor-entry);")
A("the ask-entry T-20 bucket below carries spread+fee and is the bucket-series row.")
A("")
A("N-weighted net ROC by bucket (all categories; net = gross - 1c taker fee):")
bser={}
for b in [str(x) for x in BUCKETS]+["terminal"]:
    nets=[]; caps=[]
    for (cat,cell,bb),v in grid.items():
        if bb!=b: continue
        nets+= [x[0] for x in v["net"]]; caps+=[x[1] for x in v["net"]]
    if not nets: continue
    roc=sum(nets)/sum(caps)*100
    sd=statistics.stdev(nets) if len(nets)>=2 else float("nan")
    se=sd/math.sqrt(len(nets))
    se_roc=se/ (sum(caps)/len(nets)) *100
    bser[b]=(roc,se_roc,len(nets))
    A("  T-%-8s N=%6d  net ROC %+7.3f%%  (SE %.3fpp)"%(b,len(nets),roc,se_roc))
A("")
t20=bser.get("20"); term=bser.get("terminal")
if t20 and term:
    bar=t20[0]-1*t20[1]
    verdict="CLEAN (terminal >= T20 - 1xSE)" if term[0]>=bar else "DIRTY (terminal < T20 - 1xSE)"
    A("PRE-REGISTERED BAR: terminal %.3f%% vs T20 %.3f%% - 1xSE(%.3f) = %.3f%% -> %s"%(
        term[0],t20[0],t20[1],bar,verdict))
A("")
A("SLIPPAGE into the gun (terminal ask minus ask 60s/300s prior; +ve = adverse), by category:")
for cat in sorted(slip60):
    s1=sorted(slip60[cat]); s5=sorted(slip300.get(cat,[]))
    def q(d,p): return d[min(len(d)-1,int(len(d)*p))] if d else float("nan")
    A("  %-10s 60s: p50=%+.1f p90=%+.1f (n=%d) | 300s: p50=%+.1f p90=%+.1f (n=%d)"%(
        cat,q(s1,.5),q(s1,.9),len(s1),q(s5,.5),q(s5,.9),len(s5)))
A("")
A("PAIRING: sibling-already-filled rate by bucket (v3-engine sibling fill model):")
for b in [str(x) for x in BUCKETS]+["terminal"]:
    parts=[]
    for cat in ("ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL"):
        f,n=pair.get((cat,b),(0,0))
        if n: parts.append("%s %.0f%%"%(cat[:7],100*f/n))
    if parts: A("  T-%-8s %s"%(b,"  ".join(parts)))
A("")
A("parquet %s"%OUTP)
A("sha256 %s"%sha)
open("/tmp/entry_minute_ev_summary.txt","w").write("\n".join(S)+"\n")
print("\n".join(S))
