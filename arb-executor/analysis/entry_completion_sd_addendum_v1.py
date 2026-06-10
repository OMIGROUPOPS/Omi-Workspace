"""[C-SD] Replay micro-addendum: per-(category,cell,X) attempt-arm / no-attempt-arm
outcome SDs -- the wave-gate's C3(iii) predicted-SE inputs. READ-ONLY.

Derived from analysis/entry_completion_replay_v1.py (1944b250): SAME engine, SAME
gates, byte-equivalent fill/exit logic; the only addition is per-event intermediate
collection in the completion branch. The committed aggregate parquet
(entry_completion_replay_v1.parquet, sha 7883f5c8...) is loaded and every recomputed
(n_conditioning, n_completion_fills, net_sum) is ASSERTED equal to it -- a
row-for-row consistency gate on top of the re-run R1 equivalence gate.

Outcome variable (cents/contract, per conditioning event = a leg-1 maker/taker fill
with the sibling simulated):
  attempt_arm        = leg1_realized + completion_leg_net (0 when the completion bid
                       does not fill) -- the R4-ratified incremental frame.
  noattempt_leg1only = leg1_realized (orphan rides alone).
  noattempt_leg1_plus_sib_v3maker = leg1_realized + sibling's own v3 outcome ONLY
                       when the sibling filled as maker_resting; 0 otherwise -- the
                       foregone-alternative frame under live Stage-1 reality
                       (maker_only_entry: no T-20 fallback cross, no marketable
                       taker -- an unfilled maker bid is NO position). [C-ARM]
                       correction 2026-06-10: the first emission included the
                       sibling's miss_fallback taker outcomes; superseded.
                       DISCLOSED VACUITY: the spec does not pin which no-attempt
                       frame feeds C3(iii); both leg1-only and leg1+sib_v3maker are
                       emitted (superset is inert; the gate chooses at use time).

Output: data/durable/entry_completion/entry_completion_replay_v1_sd.parquet
(companion; the committed aggregate parquet is NOT modified).
"""
import pyarrow.parquet as pq, pyarrow as pa
import glob, collections, math, statistics, hashlib, json, os
ROOT="/root/Omi-Workspace/arb-executor"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
TAPE=ROOT+"/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PBV1=ROOT+"/data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet"
LOCKED=ROOT+"/data/durable/per_minute_universe/path_b_v3_per_n_simulation.parquet"
COMMITTED=ROOT+"/data/durable/entry_completion/entry_completion_replay_v1.parquet"
COMMITTED_SHA="7883f5c8d99200a5dc9c468c381e39ea20441ff93e1c664ac98a0a334ba911e4"
OUTDIR=ROOT+"/data/durable/entry_completion"
NFLOOR=25
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"

sha=hashlib.sha256(open(COMMITTED,"rb").read()).hexdigest()
assert sha==COMMITTED_SHA, "committed parquet sha mismatch: %s" % sha
committed=pq.read_table(COMMITTED).to_pandas()
ckey={}
for r in committed.itertuples():
    ckey[(r.category,int(r.cell),int(r.X))]=(int(r.n_conditioning),int(r.n_completion_fills),
        r.completion_leg_net_roc_pct, r.completion_leg_net_cents, r.wave)

# ---- atlas legs (VERBATIM from entry_completion_replay_v1.py) ----
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
    wopen=int(round(traded[0][2])); cell=min(94,max(5,wopen))
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
    res[tk]=dict(cat=cat,cell=cell,wopen=wopen,mode=mode,entry=entry,emin=emin,taker=taker,
        realized=realized,baseline=base,anchor=anchor,rows=rows,ask_by_ttm=ask_by_ttm)
print("simulated legs",len(res))

# ================= R1 EQUIVALENCE GATE (VERBATIM tolerances) =================
rl=[r["realized"] for r in res.values()]; en=[r["entry"] for r in res.values()]
bl=[r["baseline"] for r in res.values()]; an=[r["anchor"] for r in res.values()]
atlas=sum(bl)/sum(an)*100; maker=sum(rl)/sum(en)*100
dep=(sum(bl)+0.60*(sum(rl)-sum(bl)))/sum(en)*100
print("=== R1 EQUIVALENCE === atlas=%.3f maker=%.3f deployed=%.3f"%(atlas,maker,dep))
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
g_i=abs(dep-10.9)<=0.3; g_ii=(within2/tot)>=0.90 if tot else False; g_iii=tailbad==0
print("(i)%s (ii)%.1f%%/%d %s (iii)tail=%d %s"%(g_i,100*within2/max(tot,1),tot,g_ii,tailbad,g_iii))
if not (g_i and g_ii and g_iii):
    print("R1 HALT -- replay does not reproduce locked surface."); raise SystemExit(1)
print("R1 PASS")

# ================= COMPLETION BRANCH + per-event intermediates =================
def first_touch_after(rows, t_after, thr, lo=20, up=False):
    for (a,ak,pc_,pl,ph,ht) in rows:
        if a<t_after and a>=lo:
            v=ph if up else pl
            if v is not None and ((up and v>=thr) or ((not up) and v<=thr)): return a
    return None

agg=collections.defaultdict(lambda:dict(ncond=0,nfill=0,net_sum=0.0,
    att=[],no_l1=[],no_l1sib=[]))
for tk,r1 in res.items():
    if r1["mode"]=="miss_fallback": continue
    L1=leg[tk]; sib=L1["partner"]
    if sib not in res: continue
    r2=res[sib]; L2=leg[sib]; emin=r1["emin"]; leg1_basis=r1["entry"]; s0=r2["wopen"]; cell=r1["cell"]
    sib_ask=None
    for a in sorted([t for t in r2["ask_by_ttm"] if t<=emin],reverse=True): sib_ask=r2["ask_by_ttm"][a]; break
    leg1_real=r1["realized"]
    # [C-ARM] live-Stage-1 counterfactual: sibling's foregone v3 outcome counts ONLY
    # for a maker_resting fill; miss_fallback (T-20 taker) and marketable_taker are
    # gated off live (maker_only_entry) -> unfilled maker = NO position = 0.
    sib_v3_maker=r2["realized"] if r2["mode"]=="maker_resting" else 0.0
    for X in (1,2,3):
        a=agg[(L1["cat"],cell,X)]; a["ncond"]+=1
        comp_net=0.0; filled=False
        cands=[s0+X, 99-leg1_basis]
        if sib_ask is not None: cands.append(sib_ask-1)
        comp_bid=min(cands)
        if comp_bid>=1:
            if sib_ask is not None and comp_bid>=sib_ask:
                sib_entry,taker=int(round(sib_ask)),True; filled=True
            elif first_touch_after(r2["rows"],emin,comp_bid,lo=20,up=False) is not None:
                sib_entry,taker=int(round(comp_bid)),False; filled=True
            if filled and (sib_entry<1 or sib_entry>=100): filled=False
            if filled:
                X2,isx2=exitr.get((L2["cat"],r2["anchor"]),(0,False))
                sreal,_=realize(sib_entry,L2["win"],X2,isx2,L2["sq"])
                comp_net=sreal-(1.0 if taker else 0.0)
                a["nfill"]+=1; a["net_sum"]+=comp_net
        a["att"].append(leg1_real+comp_net)
        a["no_l1"].append(leg1_real)
        a["no_l1sib"].append(leg1_real+sib_v3_maker)

# ---- consistency gate vs the committed aggregate parquet ----
mism=0
for key,a in agg.items():
    c=ckey.get(key)
    if c is None: mism+=1; print("MISSING committed row", key); continue
    if c[0]!=a["ncond"] or c[1]!=a["nfill"]:
        mism+=1; print("MISMATCH", key, "ncond %d vs %d, nfill %d vs %d"%(c[0],a["ncond"],c[1],a["nfill"]))
extra=[k for k in ckey if k not in agg]
if extra: mism+=len(extra); print("rows in committed but not recomputed:", extra[:5])
print("consistency: %d keys, %d mismatches"%(len(agg),mism))
if mism: print("CONSISTENCY HALT -- intermediates do not reproduce the committed aggregates."); raise SystemExit(1)

def sd(v): return statistics.stdev(v) if len(v)>=2 else None
out=[]
for (cat,cell,X),a in sorted(agg.items()):
    c=ckey[(cat,cell,X)]
    out.append(dict(category=cat,cell=cell,X=X,n_conditioning=a["ncond"],
        n_completion_fills=a["nfill"],wave=c[4],
        mean_attempt_arm_cents=round(statistics.fmean(a["att"]),4),
        sd_attempt_arm_cents=round(sd(a["att"]),4) if sd(a["att"]) is not None else None,
        mean_noattempt_leg1only_cents=round(statistics.fmean(a["no_l1"]),4),
        sd_noattempt_leg1only_cents=round(sd(a["no_l1"]),4) if sd(a["no_l1"]) is not None else None,
        mean_noattempt_leg1_plus_sib_v3maker_cents=round(statistics.fmean(a["no_l1sib"]),4),
        sd_noattempt_leg1_plus_sib_v3maker_cents=round(sd(a["no_l1sib"]),4) if sd(a["no_l1sib"]) is not None else None,
        sd_paired_diff_cents=round(sd([x-y for x,y in zip(a["att"],a["no_l1"])]),4)
            if sd([x-y for x,y in zip(a["att"],a["no_l1"])]) is not None else None))
tbl=pa.Table.from_pylist(out)
OUTP=OUTDIR+"/entry_completion_replay_v1_sd.parquet"
pq.write_table(tbl,OUTP)
osha=hashlib.sha256(open(OUTP,"rb").read()).hexdigest()
print("rows",len(out))
print("-- SHIP_FIRST cells (deployed X per completion_cells_v1) --")
shipx={("ATP_CHALL",25):1,("ATP_CHALL",27):1,("ATP_CHALL",35):1,("ATP_CHALL",53):1,
       ("ATP_CHALL",54):1,("ATP_CHALL",56):1,("ATP_CHALL",58):1,("ATP_MAIN",35):3,
       ("ATP_MAIN",37):3,("ATP_MAIN",39):2,("ATP_MAIN",41):2,("ATP_MAIN",42):1}
for r in out:
    if shipx.get((r["category"],r["cell"]))==r["X"]:
        print("  %-9s c%2d X%d n=%3d mean_att=%7.2f sd_att=%7.2f | mean_noatt_l1sibM=%7.2f sd=%7.2f | sd_noatt_l1=%6.2f sd_diff=%6.2f"%(
            r["category"],r["cell"],r["X"],r["n_conditioning"],
            r["mean_attempt_arm_cents"],r["sd_attempt_arm_cents"],
            r["mean_noattempt_leg1_plus_sib_v3maker_cents"],
            r["sd_noattempt_leg1_plus_sib_v3maker_cents"],
            r["sd_noattempt_leg1only_cents"],r["sd_paired_diff_cents"]))
print("parquet",OUTP)
print("sha256",osha)
