"""
Entry-completion economics via TAPE REPLAY (respin of bbd88feb economics layer).
Envelope layer (window-open keying, traded-print discipline) REUSED. READ-ONLY.

R1 EQUIVALENCE GATE (hard halt): replay with NO completion branch reproduces the locked
   surface (path_b_v3_per_n_simulation.parquet) — v3 fill logic VERBATIM (full premarket
   tape, raw float prices, NO onset gate). Tolerances (all 3): (i) deployed blended ROC
   within +/-0.3pp of 10.9% (r=0.60); (ii) >=90% of N>=25 cells within +/-2pp of locked
   per-cell ROC; (iii) no N>=25 cell beyond +/-5pp. Fail -> HALT.
R2 ONE completion branch: leg-1 fills on its tape (v3 sim, unchanged) -> reprice sibling to
   min(s0+X, sibling_ask-1, 99-leg1_basis), X in {1,2,3}; check SIBLING'S OWN TAPE for a
   premarket touch thereafter (time-ordered, ttm in [20, leg1_fill)). Touch = traded
   price_low/high. s0 = sibling window-open price (ratified respec keying).
R3 same locked per-cell exit replay for every fill; unexited settle.
R4 eligible iff completion-leg net ROC > 0 at conservative end of DEPLOYED realism band
   0.5-0.7x (bid_laying_policy L105), N>=25, Wilson-90% LB on fill-rate. Sensitivity 0.3-0.5x.
"""
import pyarrow.parquet as pq, pyarrow as pa
import glob, collections, math, statistics, hashlib, json, os
ROOT="/root/Omi-Workspace/arb-executor"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
TAPE=ROOT+"/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PBV1=ROOT+"/data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet"
LOCKED=ROOT+"/data/durable/per_minute_universe/path_b_v3_per_n_simulation.parquet"
OUTDIR=ROOT+"/data/durable/entry_completion"; os.makedirs(OUTDIR,exist_ok=True)
Z90=1.6449; NFLOOR=25; LIFT_FLOOR=0.10
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"
def wilson_lb(x,n,z=Z90):
    if n<=0: return 0.0
    p=x/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; m=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return max(0.0,c-m)

# ---- atlas legs ----
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
_pb=pq.read_table(PBV1).to_pandas()   # 42 (placement x offset) rows per (cat,regime)
for r in _pb.loc[_pb.groupby(["category","anchor_regime"]).expected_improvement_cents.idxmax()].itertuples():
    lut[(r.category,r.anchor_regime)]=(int(r.placement_minute),int(r.bid_offset_cents))  # v3 argmax(expected_improvement)
exitr={}
for f in glob.glob(SPIKE+"/*_descriptive_1c.parquet"):
    cat=f.split("/")[-1].replace("_descriptive_1c.parquet","").upper()
    for r in pq.read_table(f).to_pandas().itertuples():
        exitr[(cat,int(r.cell_id))]=(int(r.best_exit_X),str(r.rule).startswith("exit at"))
print("legs",len(leg),"lut",len(lut),"exitr",len(exitr))

# ---- tape series (cohort, premarket, C32 ok); raw *100 floats ----
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

# ---- per-leg v3 fill (VERBATIM: full tape, no onset gate) + window-open cell ----
INF=1e18
res={}
for tk,rows in series.items():
    if tk not in leg: continue
    rows.sort(key=lambda r:-r[0])              # ttms desc = time ascending
    traded=[r for r in rows if r[5]]
    if not traded: continue
    L=leg[tk]; anchor=L["anchor"]; cat=L["cat"]
    wopen=int(round(traded[0][2])); cell=min(94,max(5,wopen))
    reg=band(anchor); pl,off=lut.get((cat,reg),(20,1)); bid=max(anchor-off,1)
    ask_by_ttm={r[0]:r[1] for r in rows if r[1] is not None}
    a_at=ask_by_ttm.get(pl)
    if a_at is not None and a_at<=bid:
        mode,entry,emin,taker="marketable_taker",int(round(a_at)),pl,True
    else:
        hit=None
        for (a,ak,pc_,pl_,ph,ht) in rows:       # highest ttm first => earliest fill
            if 20<=a<=pl:
                trig=min(ak if ak is not None else INF, pc_ if pc_ is not None else INF)
                if trig<=bid: hit=a; break
        if hit is not None: mode,entry,emin,taker="maker_resting",bid,hit,False
        else: mode,entry,emin,taker="miss_fallback",anchor,20,True
    X,isx=exitr.get((cat,anchor),(0,False))
    realized,_=realize(entry,L["win"],X,isx,L["sq"]); base,_=realize(anchor,L["win"],X,isx,L["sq"])
    res[tk]=dict(cat=cat,cell=cell,wopen=wopen,mode=mode,entry=entry,emin=emin,taker=taker,
        realized=realized,baseline=base,anchor=anchor,rows=rows,ask_by_ttm=ask_by_ttm)
print("simulated legs",len(res))

# ================= R1 EQUIVALENCE GATE =================
rl=[r["realized"] for r in res.values()]; en=[r["entry"] for r in res.values()]
bl=[r["baseline"] for r in res.values()]; an=[r["anchor"] for r in res.values()]
atlas=sum(bl)/sum(an)*100; maker=sum(rl)/sum(en)*100
dep=(sum(bl)+0.60*(sum(rl)-sum(bl)))/sum(en)*100
print("\n=== R1 EQUIVALENCE ===")
print("atlas blended=%.3f%% maker(pre-realism)=%.3f%% deployed(r=0.60)=%.3f%%"%(atlas,maker,dep))
lk=pq.read_table(LOCKED).to_pandas(); lk["cat"]=lk.category.str.upper()
lkc=lk.groupby(["cat","anchor_price_cents"]).apply(lambda d:(d.realized_pnl_cents.sum()/d.entry_price_cents.sum()*100,len(d)),include_groups=False)
mine=collections.defaultdict(lambda:[0.0,0.0,0])
for tk,r in res.items(): m=mine[(r["cat"],r["anchor"])]; m[0]+=r["realized"]; m[1]+=r["entry"]; m[2]+=1
within2=tot=tailbad=0; worst=[]
for k,(lroc,ln) in lkc.items():
    if ln<NFLOOR: continue
    m=mine.get(k)
    if not m or m[1]==0: continue
    mroc=m[0]/m[1]*100; tot+=1; d=abs(mroc-lroc)
    if d<=2.0: within2+=1
    if d>5.0: tailbad+=1; worst.append((k,lroc,mroc,d))
g_i=abs(dep-10.9)<=0.3; g_ii=(within2/tot)>=0.90 if tot else False; g_iii=tailbad==0
print("(i) deployed within +/-0.3pp of 10.9: %s (%.3f)"%(g_i,dep))
print("(ii) %.1f%% of %d N>=25 cells within +/-2pp: %s"%(100*within2/max(tot,1),tot,g_ii))
print("(iii) tail cells beyond +/-5pp: %d -> %s"%(tailbad,g_iii))
for k,lr,mr,d in sorted(worst,key=lambda x:-x[3])[:6]: print("    worst %s locked=%.2f mine=%.2f d=%.2f"%(k,lr,mr,d))
if not (g_i and g_ii and g_iii):
    print("R1 HALT — replay does not reproduce locked surface. Completion branch NOT run."); raise SystemExit(1)
print("R1 PASS — completion branch runs.\n")

# ================= R2/R3 COMPLETION BRANCH =================
def first_touch_after(rows, t_after, thr, lo=20, up=False):
    for (a,ak,pc_,pl,ph,ht) in rows:
        if a<t_after and a>=lo:
            v=ph if up else pl
            if v is not None and ((up and v>=thr) or ((not up) and v<=thr)): return a
    return None
agg=collections.defaultdict(lambda:dict(ncond=0,nfill=0,net_sum=0.0,cap_sum=0.0,net_cents=[],orphan0=0,sibloss=[]))
cellcap=collections.defaultdict(list)
for tk,r in res.items(): cellcap[(r["cat"],r["cell"])].append(r["entry"])
for tk,r1 in res.items():
    if r1["mode"]=="miss_fallback": continue
    L1=leg[tk]; sib=L1["partner"]
    if sib not in res: continue
    r2=res[sib]; L2=leg[sib]; emin=r1["emin"]; leg1_basis=r1["entry"]; s0=r2["wopen"]; cell=r1["cell"]
    sib_ask=None
    for a in sorted([t for t in r2["ask_by_ttm"] if t<=emin],reverse=True): sib_ask=r2["ask_by_ttm"][a]; break
    for X in (1,2,3):
        a=agg[(L1["cat"],cell,X)]; a["ncond"]+=1; a["orphan0"]+=(0 if L1["win"] else 1)
        cands=[s0+X, 99-leg1_basis]
        if sib_ask is not None: cands.append(sib_ask-1)
        comp_bid=min(cands)
        if comp_bid<1: continue
        if sib_ask is not None and comp_bid>=sib_ask:
            sib_entry,taker=int(round(sib_ask)),True
        else:
            if first_touch_after(r2["rows"],emin,comp_bid,lo=20,up=False) is None: continue
            sib_entry,taker=int(round(comp_bid)),False
        if sib_entry<1 or sib_entry>=100: continue
        X2,isx2=exitr.get((L2["cat"],r2["anchor"]),(0,False))
        sreal,_=realize(sib_entry,L2["win"],X2,isx2,L2["sq"]); net=sreal-(1.0 if taker else 0.0)
        a["nfill"]+=1; a["net_sum"]+=net; a["cap_sum"]+=sib_entry; a["net_cents"].append(net)
        a["sibloss"].append(0 if L2["win"] else 1)

# ================= R4 ELIGIBILITY + OUTPUT =================
out=[]; ship=sens=inelig=insuf=0
for (cat,cell,X),a in sorted(agg.items()):
    nc=a["ncond"]; nf=a["nfill"]
    comp_roc=(a["net_sum"]/a["cap_sum"]*100) if a["cap_sum"]>0 else None
    mean_net=statistics.fmean(a["net_cents"]) if a["net_cents"] else None
    touch=nf/nc if nc else 0.0; wlb=wilson_lb(nf,nc)
    l1cap=statistics.fmean(cellcap[(cat,cell)]) if cellcap[(cat,cell)] else 0.0
    def lift(rz): return (rz*wlb*mean_net/l1cap*100) if (mean_net is not None and l1cap>0) else None
    l05,l03,l07=lift(0.5),lift(0.3),lift(0.7)
    eligible=(comp_roc is not None and comp_roc>0 and nc>=NFLOOR and wlb>0 and l05 is not None and l05>0)
    if nc<NFLOOR: wave="insufficient_data"; insuf+=1
    elif eligible:
        if l03 is not None and l03>=LIFT_FLOOR: wave="SHIP_FIRST"; ship+=1
        else: wave="REALISM_SENSITIVE"; sens+=1
    else: wave="INELIGIBLE"; inelig+=1
    out.append(dict(category=cat,cell=cell,X=X,n_conditioning=nc,n_completion_fills=nf,
        completion_fill_rate=round(touch,4),fill_wilson_lb=round(wlb,4),
        completion_leg_net_roc_pct=round(comp_roc,3) if comp_roc is not None else None,
        completion_leg_net_cents=round(mean_net,3) if mean_net is not None else None,
        blended_lift_pp_0p5x=round(l05,4) if l05 is not None else None,
        blended_lift_pp_0p7x=round(l07,4) if l07 is not None else None,
        blended_lift_pp_0p3x=round(l03,4) if l03 is not None else None,
        tail_orphan_settle0=round(a["orphan0"]/nc,4) if nc else None, tail_paired_settle0=0.0,
        tail_completion_sibling_loses=round(statistics.fmean(a["sibloss"]),4) if a["sibloss"] else None,
        leg1_mean_capital_cents=round(l1cap,2),wave=wave))
tbl=pa.Table.from_pylist(out); OUTP=OUTDIR+"/entry_completion_replay_v1.parquet"; pq.write_table(tbl,OUTP)
sha=hashlib.sha256(open(OUTP,"rb").read()).hexdigest()
print("=== R4 ELIGIBILITY (cat,cell,X) ===")
print("rows",len(out)," SHIP_FIRST",ship," REALISM_SENSITIVE",sens," INELIGIBLE",inelig," insufficient_data",insuf)
print("SHAPE: %s"%("SHIP — cells clear completion net ROC>0 at 0.5x" if ship>0 else "NOTHING clears at 0.5x -> mechanism does NOT ship"))
print("parquet",OUTP); print("sha256",sha)
elig=sorted([r for r in out if r["wave"] in("SHIP_FIRST","REALISM_SENSITIVE")],key=lambda r:-(r["completion_leg_net_roc_pct"] or -1e9))
print("\n-- top completion-eligible --")
for r in elig[:14]:
    print("  %-9s c%2d X%d ncond=%3d nfill=%3d touch=%.2f wlb=%.2f comp_roc=%6.1f%% net=%5.1fc l0.5=%.2f %s"%(
        r["category"],r["cell"],r["X"],r["n_conditioning"],r["n_completion_fills"],r["completion_fill_rate"],
        r["fill_wilson_lb"],r["completion_leg_net_roc_pct"],r["completion_leg_net_cents"],r["blended_lift_pp_0p5x"],r["wave"]))
json.dump(dict(sha256=sha,rows=len(out),ship=ship,sens=sens,inelig=inelig,insuf=insuf,
    R1=dict(atlas=atlas,maker=maker,deployed=dep,within2=within2,tot=tot,tailbad=tailbad)),
    open(OUTDIR+"/_replay_meta.json","w"),indent=1)
print("\nDONE.")
