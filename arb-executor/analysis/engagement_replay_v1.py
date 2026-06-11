"""
ENGAGEMENT REPLAY #1 — the no-print skip hole, via TAPE REPLAY. READ-ONLY.

Live discipline (live_v4 _resolve_anchor): no traded print with age <= 1800s
(V4_LAST_TRADE_MAX_AGE_SEC) -> skip_no_trade, no entry, retry next tick. This
replay measures what engaging those skipped moments would have earned.

R1 EQUIVALENCE GATE FIRST (hard halt) — identical to entry_completion_replay_v1:
   the v3 fill replay must reproduce the locked surface (atlas 8.70 / maker
   12.11 / deployed 10.9 +/-0.3pp; >=90% of N>=25 cells within +/-2pp; no cell
   beyond +/-5pp). Fail -> HALT, engagement branch NOT run.

HOLE MOMENT: minute m of a cohort leg where the most recent traded print (ttm
   > m) is ABSENT or older than 1800s (age_sec = (print_ttm - m)*60). One
   engagement per (leg, time bucket): the FIRST hole minute in the bucket where
   the variant's precondition holds. Buckets: T-240->T-60 (240,60], T-60->T-15
   (60,15], T-15->T-0 (15,0].

VARIANTS (entry semantics only; exit/settle = locked v1 machinery, exit rule
   keyed on the leg's atlas anchor; realize() incl. size-qual scalp; all bids
   are MAKER — no taker fee):
   C0  skip baseline: realized 0, capital 0 (what live does).
   C1  join-bid: level = yes_bid_close at engagement, reported in BOTH fill
       semantics as separate rows (C-REPLAY-DELIVER item-4 correction — "dual
       semantics" = two variants, not one dual trigger):
         C1_join_strict: filled iff a later minute (within the bucket, before
           live takes over) has price_low < level (tape traded strictly through
           the joined queue) OR yes_ask_close < level — back of the queue.
         C1_join_touch:  same level, touch semantics (price_low <= level OR
           yes_ask_close <= level) — front-of-queue upper bound.
   C2  bid-1: level = yes_bid_close - 1 (alone at the level): touch semantics
       price_low <= level OR yes_ask_close <= level.
   C3  aged last-trade sweep, A in {1200,1800,3600,7200,14400}s:
       EXTENSION arm (the hole): most recent print age in (1800, A] -> anchor
         on it; offset from the v3 per-regime LUT; v3 fill trigger VERBATIM
         (min(ask_close, price_close) <= level, non-strict).
       REMOVAL arm (control, A <= 1800 meaningful): R1-world placements whose
         anchor age at the placement minute is in (A, 1800] — the entries a
         TIGHTER cutoff would delete; their locked v1 economics, sign tells
         whether tightening wins. (A=1200/1800 have empty extension arms by
         construction — live already covers age <= 1800.)
   Scan containment: fills counted only while ttm in (bucket_floor, e] AND the
   hole persists (first new print -> live machinery takes over in both worlds;
   scan stops; conservative). Degenerate books (bid<1, ask>99, missing) do not
   engage.

ELIGIBILITY (per variant/arm/A x category x bucket x level band): beats-skip at
   0.5x realism — N>=25 engagements, Wilson-90% LB on fill rate > 0, mean net
   cents > 0; conservative lift = 0.5 * wlb * mean_net (cents/engagement).
   SHAPE pre-commit stands: any row clearing at 0.5x -> the hole engagement
   SHIPS (shape), else does not.

Output: data/durable/entry_completion/engagement_replay_v1.parquet (+ meta).
Inputs untouched; bot untouched.
"""
import pyarrow.parquet as pq, pyarrow as pa
import glob, collections, math, statistics, hashlib, json, os
ROOT="/root/Omi-Workspace/arb-executor"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
TAPE=ROOT+"/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PBV1=ROOT+"/data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet"
LOCKED=ROOT+"/data/durable/per_minute_universe/path_b_v3_per_n_simulation.parquet"
OUTDIR=ROOT+"/data/durable/entry_completion"; os.makedirs(OUTDIR,exist_ok=True)
Z90=1.6449; NFLOOR=25; F_LIVE=1800.0
SWEEP=[1200,1800,3600,7200,14400]
BUCKETS=[(240.0,60.0,"T240_T60"),(60.0,15.0,"T60_T15"),(15.0,0.0,"T15_T0")]
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

# ---- atlas legs (verbatim v1) ----
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
print("legs",len(leg),"lut",len(lut),"exitr",len(exitr),flush=True)

# ---- tape series (v1 columns + yes_bid_close) ----
cols=["ticker","time_to_match_start_min","yes_ask_close","yes_bid_close","price_close",
      "price_low","price_high","minute_has_trade","match_start_method"]
def f100(x): return None if x is None else x*100.0
series=collections.defaultdict(list)
sc=pq.ParquetFile(TAPE)
for i in range(sc.metadata.num_row_groups):
    rg=sc.read_row_group(i,columns=cols)
    tk=rg.column("ticker").to_pylist(); tt=rg.column("time_to_match_start_min").to_pylist()
    ak=rg.column("yes_ask_close").to_pylist(); bd=rg.column("yes_bid_close").to_pylist()
    pcl=rg.column("price_close").to_pylist()
    plo=rg.column("price_low").to_pylist(); phi=rg.column("price_high").to_pylist()
    mh=rg.column("minute_has_trade").to_pylist(); ms=rg.column("match_start_method").to_pylist()
    for j in range(len(tk)):
        t=tk[j]
        if t not in cohort or ms[j]=="unknown": continue
        a=tt[j]
        if a is None or not (0.0<a<=240.0): continue
        series[t].append((a,f100(ak[j]),f100(pcl[j]),f100(plo[j]),f100(phi[j]),
                          bool(mh[j] and pcl[j] is not None),f100(bd[j])))
print("tape tickers",len(series),flush=True)

def realize(entry,win,X,is_exit,sq):
    if is_exit and sq>=entry+X: return X,True
    return ((99-entry) if win else -(entry-1)),False

# ---- per-leg v3 fill (VERBATIM v1; tuple gains bid at idx 6, untouched here) ----
INF=1e18
res={}; anchor_age_at_pl={}
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
        for (a,ak,pc_,pl_,ph,ht,_bd) in rows:
            if 20<=a<=pl:
                trig=min(ak if ak is not None else INF, pc_ if pc_ is not None else INF)
                if trig<=bid: hit=a; break
        if hit is not None: mode,entry,emin,taker="maker_resting",bid,hit,False
        else: mode,entry,emin,taker="miss_fallback",anchor,20,True
    X,isx=exitr.get((cat,anchor),(0,False))
    realized,_=realize(entry,L["win"],X,isx,L["sq"]); base,_=realize(anchor,L["win"],X,isx,L["sq"])
    res[tk]=dict(cat=cat,cell=cell,mode=mode,entry=entry,emin=emin,taker=taker,
        realized=realized,baseline=base,anchor=anchor)
    # anchor age at the v3 placement minute (for the C3 REMOVAL arm)
    prior=[r[0] for r in traded if r[0]>pl]
    anchor_age_at_pl[tk]=((min(prior)-pl)*60.0) if prior else INF
print("simulated legs",len(res),flush=True)

# ================= R1 EQUIVALENCE GATE (verbatim v1) =================
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
within2=tot=tailbad=0
for k,(lroc,ln) in lkc.items():
    if ln<NFLOOR: continue
    m=mine.get(k)
    if not m or m[1]==0: continue
    mroc=m[0]/m[1]*100; tot+=1; d=abs(mroc-lroc)
    if d<=2.0: within2+=1
    if d>5.0: tailbad+=1
g_i=abs(dep-10.9)<=0.3; g_ii=(within2/tot)>=0.90 if tot else False; g_iii=tailbad==0
print("(i) %.3f within +/-0.3 of 10.9: %s  (ii) %d/%d within 2pp: %s  (iii) tail %d: %s"%(
    dep,g_i,within2,tot,g_ii,tailbad,g_iii))
if not (g_i and g_ii and g_iii):
    print("R1 HALT — engagement branch NOT run."); raise SystemExit(1)
print("R1 PASS — engagement branch runs.\n",flush=True)

# ================= ENGAGEMENT BRANCH =================
def hole_at(traded_ttms, m):
    """True iff at minute m the most recent print is absent or older than F_LIVE."""
    prior=[t for t in traded_ttms if t>m]
    if not prior: return True, None
    age=(min(prior)-m)*60.0
    return age>F_LIVE, (min(prior), age)

agg=collections.defaultdict(lambda:dict(n=0,nf=0,net=[],cap=0.0,nx=0,nsw=0,nsl=0,capb=0))
nev={"legs_with_hole":0,"never_traded":0}
for tk,rows in series.items():
    if tk not in leg: continue
    rows.sort(key=lambda r:-r[0])
    L=leg[tk]; cat=L["cat"]
    traded_ttms=[r[0] for r in rows if r[5]]
    if not traded_ttms: nev["never_traded"]+=1
    X,isx=exitr.get((cat,L["anchor"]),(0,False))
    leg_has_hole=False
    for blo,bhi,bname in BUCKETS:
        # engagement minute: first (highest-ttm) hole minute in the bucket
        e=None; erow=None
        for r in rows:
            if not (bhi<r[0]<=blo): continue
            h,_=hole_at(traded_ttms,r[0])
            if h: e,erow=r[0],r; break
        if e is None: continue
        leg_has_hole=True
        # scan window: after e, inside bucket, while the hole persists
        scan=[r for r in rows if bhi<r[0]<e]
        def fill_scan(level,strict_print,strict_ask,nonstrict_v3=False):
            for r in scan:
                a,ak,pc_,plo_,_,ht,_bd=r
                h,_=hole_at(traded_ttms,a)
                if not h: return None   # live takes over
                if nonstrict_v3:
                    trig=min(ak if ak is not None else INF, pc_ if pc_ is not None else INF)
                    if trig<=level: return a
                    continue
                if plo_ is not None and ((plo_<level) if strict_print else (plo_<=level)): return a
                if ak is not None and ((ak<level) if strict_ask else (ak<=level)): return a
            return None
        bd0=erow[6]; ak0=erow[1]
        book_ok=(bd0 is not None and ak0 is not None and 1<=round(bd0)<round(ak0)<=99)
        def book_fill(k,lvl):
            net,exited=realize(lvl,L["win"],X,isx,L["sq"])
            a=agg[k]; a["nf"]+=1; a["net"].append(net); a["cap"]+=lvl
            if exited: a["nx"]+=1
            elif L["win"]: a["nsw"]+=1
            else: a["nsl"]+=1
            sr=res.get(L["partner"])
            if sr is not None and lvl+sr["entry"]>99: a["capb"]+=1
        # --- C1 join-bid, BOTH semantics (strict traded-through vs touch) ---
        if book_ok:
            lvl=int(round(bd0))
            for vname,sp,sa in (("C1_join_strict",True,True),("C1_join_touch",False,False)):
                k=(vname,"engage",0,cat,bname,band(lvl)); agg[k]["n"]+=1
                if fill_scan(lvl,sp,sa) is not None: book_fill(k,lvl)
        # --- C2 bid-1 (touch) ---
        if book_ok and round(bd0)>=2:
            lvl=int(round(bd0))-1
            k=("C2_bid_minus_1","engage",0,cat,bname,band(lvl)); agg[k]["n"]+=1
            if fill_scan(lvl,False,False) is not None: book_fill(k,lvl)
        # --- C3 extension arms (aged anchor, v3 semantics) ---
        h,info=hole_at(traded_ttms,e)
        if info is not None:
            p_ttm,age=info
            pc_map={r[0]:r[2] for r in rows if r[5]}
            aged_anchor=pc_map.get(p_ttm)
            if aged_anchor is not None:
                aa=min(94,max(5,int(round(aged_anchor))))
                _,off=lut.get((cat,band(aa)),(20,1))
                lvl=max(aa-off,1)
                for A in SWEEP:
                    if not (F_LIVE<age<=A): continue
                    k=("C3_aged_%d"%A,"extend",A,cat,bname,band(lvl)); agg[k]["n"]+=1
                    if fill_scan(lvl,False,False,nonstrict_v3=True) is not None:
                        book_fill(k,lvl)
    if leg_has_hole: nev["legs_with_hole"]+=1

# --- C3 REMOVAL arms: R1-world placements a tighter cutoff would delete ---
for tk,r in res.items():
    age=anchor_age_at_pl.get(tk,INF)
    if r["mode"]=="miss_fallback": continue
    L=leg[tk]; X,isx=exitr.get((r["cat"],r["anchor"]),(0,False))
    _,exited=realize(r["entry"],L["win"],X,isx,L["sq"])
    for A in SWEEP:
        if A<F_LIVE or A==F_LIVE:
            if A<age<=F_LIVE:
                k=("C3_aged_%d"%A,"remove",A,r["cat"],"at_v3_placement",band(r["entry"]))
                a=agg[k]; a["n"]+=1; a["nf"]+=1; a["net"].append(r["realized"]); a["cap"]+=r["entry"]
                if exited: a["nx"]+=1
                elif L["win"]: a["nsw"]+=1
                else: a["nsl"]+=1
                sr=res.get(L["partner"])
                if sr is not None and r["entry"]+sr["entry"]>99: a["capb"]+=1

# ================= ELIGIBILITY + OUTPUT =================
out=[]; ship=0
for (var,arm,A,cat,bname,bd_),a in sorted(agg.items()):
    n,nf=a["n"],a["nf"]; wlb=wilson_lb(nf,n)
    mean_net=statistics.fmean(a["net"]) if a["net"] else None
    roc=(sum(a["net"])/a["cap"]*100) if a["cap"]>0 else None
    lift05=(0.5*wlb*mean_net) if mean_net is not None else None
    if arm=="engage" or arm=="extend":
        eligible=(n>=NFLOOR and wlb>0 and mean_net is not None and mean_net>0 and lift05>0)
        wave="BEATS_SKIP_0p5x" if eligible else ("insufficient_data" if n<NFLOOR else "INELIGIBLE")
        if eligible: ship+=1
    else:
        wave=("REMOVE_WINS" if (n>=NFLOOR and mean_net is not None and mean_net<0)
              else ("insufficient_data" if n<NFLOOR else "KEEP_status_quo"))
    lift07=(0.7*wlb*mean_net) if mean_net is not None else None
    out.append(dict(variant=var,arm=arm,age_cutoff_s=A,category=cat,bucket=bname,level_band=bd_,
        n_engagements=n,n_fills=nf,fill_rate=round(nf/n,4) if n else None,
        fill_wilson_lb=round(wlb,4),mean_net_cents=round(mean_net,3) if mean_net is not None else None,
        net_roc_pct=round(roc,3) if roc is not None else None,
        lift_cents_per_engagement_0p5x=round(lift05,4) if lift05 is not None else None,
        lift_cents_per_engagement_0p7x=round(lift07,4) if lift07 is not None else None,
        n_exit_scalps=a["nx"],n_settle_wins=a["nsw"],n_settle_losses=a["nsl"],
        settle0_share_of_fills=round(a["nsl"]/nf,4) if nf else None,
        cap_breach_fills_vs_r1_sibling=a["capb"],
        wave=wave))
tbl=pa.Table.from_pylist(out); OUTP=OUTDIR+"/engagement_replay_v1.parquet"; pq.write_table(tbl,OUTP)
sha=hashlib.sha256(open(OUTP,"rb").read()).hexdigest()
print("=== ELIGIBILITY (variant/arm x cat x bucket x band) ===")
print("rows",len(out)," beats-skip@0.5x",ship," legs_with_hole",nev["legs_with_hole"],
      " never_traded",nev["never_traded"])
print("SHAPE: %s"%("ENGAGEMENT SHIPS (shape) — rows clear beats-skip at 0.5x" if ship>0
      else "NOTHING beats skip at 0.5x -> hole engagement does NOT ship"))
print("parquet",OUTP); print("sha256",sha)
el=[r for r in out if r["wave"] in ("BEATS_SKIP_0p5x","REMOVE_WINS")]
el.sort(key=lambda r:-(r["lift_cents_per_engagement_0p5x"] or (-(r["mean_net_cents"] or 0))))
print("\n-- cleared rows --")
for r in el[:20]:
    print("  %-14s %-7s %-9s %-9s %-7s N=%4d nf=%3d wlb=%.2f net=%6.1fc roc=%6.1f%% lift0.5=%6.2f %s"%(
        r["variant"],r["arm"],r["category"],r["bucket"],r["level_band"],r["n_engagements"],
        r["n_fills"],r["fill_wilson_lb"],r["mean_net_cents"] or 0,r["net_roc_pct"] or 0,
        r["lift_cents_per_engagement_0p5x"] or 0,r["wave"]))
# ---- per-candidate aggregates (all categories/buckets/bands pooled) ----
print("\n=== PER-CANDIDATE AGGREGATE (pooled; lift = r * wilson_lb * mean_net, cents/engagement) ===")
vagg=collections.defaultdict(lambda:dict(n=0,nf=0,net=[],cap=0.0,nx=0,nsw=0,nsl=0,capb=0))
for (var,arm,A,cat,bname,bd_),a in agg.items():
    v=vagg[(var,arm)]
    v["n"]+=a["n"]; v["nf"]+=a["nf"]; v["net"]+=a["net"]; v["cap"]+=a["cap"]
    v["nx"]+=a["nx"]; v["nsw"]+=a["nsw"]; v["nsl"]+=a["nsl"]; v["capb"]+=a["capb"]
print("  C0_skip        engage  N=all-hole-moments fills=0 net=0.0c roc=0.0% lift0.5=0.00 lift0.7=0.00 (baseline)")
for (var,arm),v in sorted(vagg.items()):
    n,nf=v["n"],v["nf"]; wl=wilson_lb(nf,n)
    mn=statistics.fmean(v["net"]) if v["net"] else 0.0
    rc=(sum(v["net"])/v["cap"]*100) if v["cap"]>0 else 0.0
    print("  %-14s %-7s N=%5d fills=%4d rate=%.3f wlb=%.3f net=%6.1fc roc=%6.1f%% lift0.5=%5.2f lift0.7=%5.2f exit=%d settleW=%d settle0=%d capbreach=%d"%(
        var,arm,n,nf,(nf/n if n else 0),wl,mn,rc,0.5*wl*mn,0.7*wl*mn,v["nx"],v["nsw"],v["nsl"],v["capb"]))

print("\n=== TIME-BUCKET DISTRIBUTION OF FILLS (per candidate, engage/extend arms) ===")
bdist=collections.defaultdict(lambda:collections.Counter())
for (var,arm,A,cat,bname,bd_),a in agg.items():
    if arm in ("engage","extend"): bdist[var][bname]+=a["nf"]
for var in sorted(bdist):
    c=bdist[var]; totf=sum(c.values())
    print("  %-14s T240_T60=%4d  T60_T15=%4d  T15_T0=%4d  (total %d, T15_T0 share %.0f%%)"%(
        var,c.get("T240_T60",0),c.get("T60_T15",0),c.get("T15_T0",0),totf,
        (100*c.get("T15_T0",0)/totf) if totf else 0))

# ---- settlement-bleed / cap-hygiene lines ----
print("\n=== SETTLEMENT-BLEED / CAP-HYGIENE (pooled per candidate) ===")
for (var,arm),v in sorted(vagg.items()):
    nf=v["nf"]
    if nf==0:
        print("  %-14s %-7s no fills"%(var,arm)); continue
    print("  %-14s %-7s fills=%4d exit_scalps=%4d (%.0f%%) settle_wins=%3d settle0_losses=%3d (bleed %.1f%%) cap_breach_vs_r1_sibling=%d (%.1f%%)"%(
        var,arm,nf,v["nx"],100*v["nx"]/nf,v["nsw"],v["nsl"],100*v["nsl"]/nf,v["capb"],100*v["capb"]/nf))

json.dump(dict(sha256=sha,rows=len(out),beats_skip=ship,
    legs_with_hole=nev["legs_with_hole"],never_traded=nev["never_traded"],
    R1=dict(atlas=atlas,maker=maker,deployed=dep,within2=within2,tot=tot,tailbad=tailbad),
    f_live_sec=F_LIVE,sweep=SWEEP),
    open(OUTDIR+"/_engagement_meta.json","w"),indent=1)
print("\nDONE.")
