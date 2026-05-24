#!/usr/bin/env python3
"""
build_path_c_phase2.py — Path C Phase 2: conditional offset modulation (predictor-driven aggressiveness).

Deploys Phase 1's P(drift_reached_bid) as offset MODULATION (per LESSONS A42, not skip-gating):
high P -> more aggressive offset (bigger discount), low P -> more conservative. Same dual-improvement
sim as Path B v3 (execution-mode split + atlas exit replay from actual entry). Tests 4 threshold
variants + a no-modulation v3-reproduction. Pre-realism. P is in-sample for CPCV rows (Phase-1 caveat).
"""
import json, time, resource
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.dataset as ds, pyarrow.compute as pc
REPO="/root/Omi-Workspace/arb-executor"
TAPE=f"{REPO}/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PH1=f"{REPO}/data/durable/per_minute_universe/path_c_phase1_per_n_features.parquet"
CSV=f"{REPO}/docs/policy/per_regime_offsets_v1.csv"
SPK={"ATP_MAIN":"atp_main","WTA_MAIN":"wta_main","ATP_CHALL":"atp_chall","WTA_CHALL":"wta_chall"}
OUT_N=f"{REPO}/data/durable/per_minute_universe/probe/path_c_phase2_per_n_simulation_probe.parquet"
OUT_R=f"{REPO}/data/durable/per_minute_universe/probe/path_c_phase2_per_regime_summary_probe.parquet"
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
# variant: (name, agg_thr, agg_delta, cons_thr, cons_delta)  cons_thr=None -> two-tier
VARIANTS=[("primary_065_035",0.65,+5,0.35,-2),("narrow_070_030",0.70,+5,0.30,-2),
          ("broad_060_040",0.60,+5,0.40,-2),("twotier_050",0.50,+5,None,None)]
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"
def main():
    t0=time.time()
    ph1=pq.read_table(PH1,columns=["ticker","pred_p_drift"]).to_pandas().set_index("ticker")
    frames=[]; bx={}
    for cat,s in SPK.items():
        t=pq.read_table(f"{REPO}/data/durable/spike_volatility_map/{s}_spike_perN.parquet",
            columns=["ticker","event_ticker","anchor_price","size_qual_max_250","settlement_value"]).to_pandas()
        t["category"]=cat; frames.append(t)
        d=pq.read_table(f"{REPO}/data/durable/spike_volatility_map/{s}_descriptive_1c.parquet").to_pandas()
        bx[cat]={int(r.cell_id):(int(r.best_exit_X),str(r.rule)) for _,r in d.iterrows()}
    sp=pd.concat(frames,ignore_index=True)
    sp["anchor_c"]=(sp.anchor_price*100).round().astype(int)
    sp["sq_c"]=np.where(sp.size_qual_max_250<=1.5,sp.size_qual_max_250*100,sp.size_qual_max_250).round().astype(int)
    sp["regime"]=sp.anchor_c.map(band); sp["win"]=(sp.settlement_value.astype(int)==1)
    sp["pred_p_drift"]=ph1.pred_p_drift.reindex(sp.ticker).values
    csv=pd.read_csv(CSV)
    offmap={(r.category,r.anchor_regime):int(r.bid_offset_cents) for _,r in csv.iterrows()}
    plmap={(r.category,r.anchor_regime):int(r.placement_minute) for _,r in csv.iterrows()}
    sp["base_off"]=sp.apply(lambda r:offmap.get((r.category,r.regime),15),axis=1)
    sp["placement"]=sp.apply(lambda r:plmap.get((r.category,r.regime),240),axis=1)
    atlas=list(sp.ticker)
    print(f"atlas {len(sp)} rss={rss():.0f}MB",flush=True)

    df=ds.dataset(TAPE).scanner(columns=["ticker","time_to_match_start_min","yes_ask_close","price_close"],
        filter=pc.field("ticker").isin(atlas)).to_table().to_pandas()
    df=df.sort_values(["ticker","time_to_match_start_min"],ascending=[True,False])
    df["ask_c"]=df.yes_ask_close*100; df["pcl_c"]=df.price_close*100
    TK={}
    for tk,gg in df.groupby("ticker",sort=False):
        ttm=gg.time_to_match_start_min.values; ask=gg.ask_c.values; pcl=gg.pcl_c.values
        trig=np.minimum(np.where(np.isnan(ask),np.inf,ask),np.where(np.isnan(pcl),np.inf,pcl))
        TK[tk]=(ttm,ask,trig)
    print(f"tape arrays rss={rss():.0f}MB",flush=True)

    def realize(entry,win,X,rule,sq):
        if rule.startswith("exit at") and sq>=entry+X: return X,True
        return ((99-entry) if win else -(entry-1)),False
    def sim(offsets):
        # offsets: array per row (modulated offset cents). returns realized[],entry[],mode[],trig[]
        rl=np.empty(len(sp)); en=np.empty(len(sp),dtype=int); md=[]; tg=np.zeros(len(sp),dtype=bool)
        for i,(tk,anchor,pl,win,sqc,cat) in enumerate(zip(sp.ticker,sp.anchor_c,sp.placement,sp.win,sp.sq_c,sp.category)):
            off=offsets[i]; bid=max(anchor-off,1)
            ttm,ask,trig=TK[tk]
            a_at=ask[ttm==pl]; a_at=float(a_at[0]) if len(a_at) else np.nan
            if not np.isnan(a_at) and a_at<=bid:
                mode="marketable_taker"; entry=int(round(a_at))
            else:
                w=(ttm<=pl)&(ttm>=20)&(trig<=bid); hit=np.where(w)[0]
                if len(hit):
                    fi=hit[np.argmax(ttm[hit])]; mode="maker_resting"; entry=int(bid)
                else:
                    mode="miss_fallback"; entry=int(anchor)
            X,rule=bx[cat].get(anchor,(0,"hold")); rr,tt=realize(entry,win,X,rule,sqc)
            rl[i]=rr; en[i]=entry; md.append(mode); tg[i]=tt
        return rl,en,np.array(md),tg
    def mod_offsets(agg_thr,agg_d,cons_thr,cons_d):
        P=sp.pred_p_drift.values; base=sp.base_off.values; anch=sp.anchor_c.values
        off=base.copy().astype(int); tier=np.full(len(sp),"neutral",dtype=object)
        am=P>=agg_thr; off[am]=np.minimum(base[am]+agg_d,anch[am]-1); tier[am]="aggressive"
        if cons_thr is not None:
            cm=(P<cons_thr)&(~am); off[cm]=np.maximum(base[cm]+cons_d,1); tier[cm]="conservative"
        off=np.maximum(off,1)
        return off,tier

    # no-mod v3 reproduction (gate 1)
    rl0,en0,md0,tg0=sim(sp.base_off.values.astype(int))
    v3_pnl=rl0.sum()*0.1; v3_cap=en0.sum()*0.1
    print(f"v3-repro: PnL=${v3_pnl:,.2f} cap=${v3_cap:,.2f} ROI={100*v3_pnl/v3_cap:.2f}% (target $8,098.50/12.11%)",flush=True)

    variant_results={}
    for name,at,ad,ct,cd in VARIANTS:
        off,tier=mod_offsets(at,ad,ct,cd)
        rl,en,md,tg=sim(off)
        pnl=rl.sum()*0.1; cap=en.sum()*0.1; roi=100*pnl/cap
        fill=(md!="miss_fallback").mean()
        # per-tier
        tiers={}
        for tn in ["aggressive","neutral","conservative"]:
            m=tier==tn
            if m.sum()>0: tiers[tn]=dict(n=int(m.sum()),pnl=float(rl[m].sum()*0.1),cap=float(en[m].sum()*0.1),roi=float(100*rl[m].sum()/en[m].sum()) if en[m].sum() else None,frac=float(m.mean()))
        variant_results[name]=dict(pnl=pnl,cap=cap,roi=roi,fill=fill,tiers=tiers,off=off,tier=tier,rl=rl,en=en,md=md,tg=tg)
        print(f"variant {name}: ROI={roi:.2f}% PnL=${pnl:,.0f} cap=${cap:,.0f} fill={fill:.3f} agg_frac={(tier=='aggressive').mean():.3f} cons_frac={(tier=='conservative').mean():.3f}",flush=True)

    # pick best by ROI
    best=max(variant_results,key=lambda k:variant_results[k]["roi"])
    print(f"BEST variant: {best} ROI={variant_results[best]['roi']:.2f}% (v3 {100*v3_pnl/v3_cap:.2f}%)",flush=True)
    primary=variant_results["primary_065_035"]

    # Output 1: primary rule per-N
    sp["pred_p_drift_v"]=sp.pred_p_drift
    out1=pd.DataFrame({"ticker":sp.ticker,"event_ticker":sp.event_ticker,"category":sp.category,
        "anchor_regime":sp.regime,"pred_p_drift":sp.pred_p_drift,"modulation_tier":primary["tier"],
        "baseline_offset_cents":sp.base_off,"modulated_offset_cents":primary["off"],
        "bid_price_cents":np.maximum(sp.anchor_c-primary["off"],1),"execution_mode":primary["md"],
        "entry_price_cents":primary["en"],"exit_triggered":primary["tg"],
        "realized_pnl_cents":primary["rl"],"v3_baseline_pnl_cents":rl0,
        "improvement_vs_v3_cents":primary["rl"]-rl0})
    import os; os.makedirs(os.path.dirname(OUT_N),exist_ok=True)
    pq.write_table(pa.Table.from_pandas(out1,preserve_index=False),OUT_N,compression="snappy")

    # per-regime summary (primary) + per-cell dominance
    rows=[]; dom=0
    for (cat,reg),idx in sp.groupby(["category","regime"]).groups.items():
        ii=sp.index.get_indexer(idx)
        prl=primary["rl"][ii]; pen=primary["en"][ii]; brl=rl0[ii]; ben=en0[ii]
        proi=100*prl.sum()/pen.sum() if pen.sum() else np.nan
        broi=100*brl.sum()/ben.sum() if ben.sum() else np.nan
        if proi>=broi-1e-9: dom+=1
        P=sp.pred_p_drift.values[ii]
        rows.append(dict(category=cat,anchor_regime=reg,n_tickers=len(ii),mean_mod_offset=float(primary["off"][ii].mean()),
            pct_high_P=float((P>=0.65).mean()),pct_neutral_P=float(((P>=0.35)&(P<0.65)).mean()),pct_low_P=float((P<0.35).mean()),
            total_pnl=float(prl.sum()*0.1),capital=float(pen.sum()*0.1),roi_pct=proi,v3_roi_pct=broi,improvement_pp=proi-broi,
            fill_rate=float((primary["md"][ii]!="miss_fallback").mean())))
    agg=pd.DataFrame(rows)
    pq.write_table(pa.Table.from_pandas(agg,preserve_index=False),OUT_R,compression="snappy")

    # gates
    print("=== GATES ===",flush=True)
    print(f"gate1 v3-repro ${v3_pnl:,.2f} vs $8,098.50 within2%={abs(v3_pnl-8098.50)/8098.50<=0.02}",flush=True)
    print(f"gate2 rows={len(out1)}",flush=True)
    af=(primary['tier']=='aggressive').mean(); cf=(primary['tier']=='conservative').mean()
    print(f"gate3 primary agg_frac={af:.3f} (>=0.10:{af>=0.10}) cons_frac={cf:.3f} (>=0.10:{cf>=0.10})  [P right-skewed: distribution span 0.08-0.94, not narrow]",flush=True)
    print(f"gate4 per-cell dominance: {dom}/36 (>=30:{dom>=30})",flush=True)
    pt=primary["tiers"]
    aroi=pt.get("aggressive",{}).get("roi"); croi=pt.get("conservative",{}).get("roi")
    print(f"gate5 aggressive ROI={aroi} > conservative ROI={croi}: {aroi>croi if (aroi is not None and croi is not None) else 'NA'}",flush=True)
    print(f"gate6 primary ROI={primary['roi']:.2f}% >= v3 12.11%: {primary['roi']>=12.11}  | BEST {best} ROI={variant_results[best]['roi']:.2f}% >= v3: {variant_results[best]['roi']>=12.11}",flush=True)
    print(f"fill primary={primary['fill']:.3f} vs v3 0.284",flush=True)
    # save meta
    meta=dict(v3_repro_pnl=float(v3_pnl),v3_repro_roi=float(100*v3_pnl/v3_cap),
        variants={n:dict(roi=float(r["roi"]),pnl=float(r["pnl"]),cap=float(r["cap"]),fill=float(r["fill"]),
            agg_frac=float((r["tier"]=="aggressive").mean()),cons_frac=float((r["tier"]=="conservative").mean()),
            tiers={k:{kk:vv for kk,vv in v.items()} for k,v in r["tiers"].items()}) for n,r in variant_results.items()},
        best_variant=best,per_cell_dominance=int(dom),primary_fill=float(primary["fill"]))
    json.dump(meta,open("/tmp/path_c_phase2_meta.json","w"),indent=2,default=float)
    print(f"wall={time.time()-t0:.1f}s peak_rss={rss():.0f}MB",flush=True); print("DONE_MARKER",flush=True)
if __name__=="__main__": main()
