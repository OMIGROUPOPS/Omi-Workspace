#!/usr/bin/env python3
"""
build_path_b_v3.py — Path B v3: per-regime offsets + atlas exit replay (deployable measurement).

Identical dual-improvement methodology to v2, but replaces the universal 15c offset with the
per-(category x anchor_regime) optimal (placement_minute, bid_offset) from Path B v1 Section 3
(path_b_per_regime_fill_summary_v1.parquet, argmax expected_improvement_cents per cell). Each N gets
its regime's offset/placement; underdog cells get 2-3c (which actually fill) instead of the universal
15c clamp-to-1c that left them on the table.
"""
import json, time, resource
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.dataset as ds, pyarrow.compute as pc
REPO="/root/Omi-Workspace/arb-executor"
TAPE=f"{REPO}/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PBV1=f"{REPO}/data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet"
SPK={"ATP_MAIN":"atp_main","WTA_MAIN":"wta_main","ATP_CHALL":"atp_chall","WTA_CHALL":"wta_chall"}
OUT_N=f"{REPO}/data/durable/per_minute_universe/probe/path_b_v3_per_n_simulation_probe.parquet"
OUT_R=f"{REPO}/data/durable/per_minute_universe/probe/path_b_v3_per_regime_summary_probe.parquet"
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"
def main():
    t0=time.time()
    # per-regime offset lookup (argmax expected_improvement)
    v1=pq.read_table(PBV1).to_pandas()
    lut={}
    for (cat,reg),g in v1.groupby(["category","anchor_regime"]):
        r=g.loc[g.expected_improvement_cents.idxmax()]
        lut[(cat,reg)]=(int(r.placement_minute),int(r.bid_offset_cents))
    print("per-regime lookup sample:",{k:lut[k] for k in list(lut)[:6]},flush=True)

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
    atlas=set(sp.ticker)
    print(f"atlas N={len(sp)} rss={rss():.0f}MB",flush=True)

    df=ds.dataset(TAPE).scanner(columns=["ticker","time_to_match_start_min","yes_ask_close","price_close"],
        filter=pc.field("ticker").isin(list(atlas))).to_table().to_pandas()
    df["ask_c"]=df.yes_ask_close*100; df["pcl_c"]=df.price_close*100
    df=df.sort_values(["ticker","time_to_match_start_min"],ascending=[True,False])
    print(f"tape rows={len(df)} rss={rss():.0f}MB",flush=True)
    tk_arrays={}
    for tk,gg in df.groupby("ticker",sort=False):
        ttm=gg.time_to_match_start_min.values
        ask=gg.ask_c.values; pcl=gg.pcl_c.values
        trig=np.minimum(np.where(np.isnan(ask),np.inf,ask),np.where(np.isnan(pcl),np.inf,pcl))
        tk_arrays[tk]=(ttm,ask,trig)

    modes=[];entries=[];emins=[];placements=[];offsets=[];bids=[]
    for _,r in sp.iterrows():
        cat=r.category; reg=r.regime; anchor=r.anchor_c
        pl,off=lut.get((cat,reg),(240,15))
        bid=max(anchor-off,1)
        placements.append(pl);offsets.append(off);bids.append(bid)
        ttm,ask,trig=tk_arrays[r.ticker]
        a_at=ask[ttm==pl]
        a_at=float(a_at[0]) if len(a_at) else np.nan
        if not np.isnan(a_at) and a_at<=bid:
            modes.append("marketable_taker");entries.append(int(round(a_at)));emins.append(pl);continue
        win_mask=(ttm<=pl)&(ttm>=20)&(trig<=bid)
        hit=np.where(win_mask)[0]
        if len(hit):
            # earliest fill = highest ttm among hits
            fi=hit[np.argmax(ttm[hit])]
            modes.append("maker_resting");entries.append(int(bid));emins.append(int(ttm[fi]))
        else:
            modes.append("miss_fallback");entries.append(int(anchor));emins.append(20)
    sp["placement_minute"]=placements; sp["bid_offset_cents"]=offsets; sp["bid_price_cents"]=bids
    sp["execution_mode"]=modes; sp["entry_price_cents"]=entries; sp["entry_minute"]=emins

    def realize(entry,win,X,rule,sq):
        if rule.startswith("exit at") and sq>=entry+X: return X,True
        return ((99-entry) if win else -(entry-1)),False
    rl=[];tr=[];bX=[];bR=[];base=[]
    for _,r in sp.iterrows():
        info=bx[r.category].get(r.anchor_c); X,rule=info if info else (0,"hold")
        bX.append(X);bR.append(rule)
        rr,tt=realize(r.entry_price_cents,r.win,X,rule,r.sq_c); rl.append(rr);tr.append(tt)
        bb,_=realize(r.anchor_c,r.win,X,rule,r.sq_c); base.append(bb)
    sp["cell_best_exit_X"]=bX; sp["cell_rule"]=bR; sp["exit_triggered"]=tr
    sp["realized_pnl_cents"]=rl; sp["atlas_baseline_realized_pnl_cents"]=base
    sp["improvement_vs_baseline_cents"]=sp.realized_pnl_cents-sp.atlas_baseline_realized_pnl_cents

    out1=sp[["ticker","event_ticker","category","anchor_c","regime","placement_minute","bid_offset_cents",
        "bid_price_cents","execution_mode","entry_price_cents","entry_minute","cell_best_exit_X","cell_rule",
        "exit_triggered","realized_pnl_cents","atlas_baseline_realized_pnl_cents","improvement_vs_baseline_cents"]].rename(
        columns={"anchor_c":"anchor_price_cents","regime":"anchor_regime"})
    import os; os.makedirs(os.path.dirname(OUT_N),exist_ok=True)
    pq.write_table(pa.Table.from_pandas(out1,preserve_index=False),OUT_N,compression="snappy")

    rows=[]
    for (cat,reg),g in sp.groupby(["category","regime"],observed=True):
        pl,off=lut.get((cat,reg),(240,15))
        n=len(g); pnl=g.realized_pnl_cents.sum()*0.1; cap=g.entry_price_cents.sum()*0.1
        bpnl=g.atlas_baseline_realized_pnl_cents.sum()*0.1; bcap=g.anchor_c.sum()*0.1
        fill=(g.execution_mode!="miss_fallback").mean()
        rows.append(dict(category=cat,anchor_regime=reg,placement_minute=pl,bid_offset_cents=off,n_tickers=n,
            pct_marketable_taker=(g.execution_mode=="marketable_taker").mean(),
            pct_maker_resting=(g.execution_mode=="maker_resting").mean(),
            pct_miss_fallback=(g.execution_mode=="miss_fallback").mean(),fill_rate=fill,
            mean_realized_pnl_cents=g.realized_pnl_cents.mean(),total_realized_pnl_dollars=pnl,
            capital_deployed_dollars=cap,roi_pct=100*pnl/cap if cap else np.nan,
            atlas_baseline_roi_pct=100*bpnl/bcap if bcap else np.nan,
            roi_lift_pp=(100*pnl/cap-100*bpnl/bcap) if cap and bcap else np.nan))
    agg=pd.DataFrame(rows)
    pq.write_table(pa.Table.from_pandas(agg,preserve_index=False),OUT_R,compression="snappy")

    TP=sp.realized_pnl_cents.sum()*0.1; CAP=sp.entry_price_cents.sum()*0.1
    BTP=sp.atlas_baseline_realized_pnl_cents.sum()*0.1; BCAP=sp.anchor_c.sum()*0.1
    fill_all=(sp.execution_mode!="miss_fallback").mean()
    print("=== VALIDATION ===",flush=True)
    print(f"gate2 rows={len(out1)}",flush=True)
    print(f"gate1 baseline=${BTP:,.2f} (atlas $6,158.20 ratio {BTP/6158.20:.4f}) within2%={abs(BTP-6158.20)/6158.20<=0.02} cap=${BCAP:,.2f}",flush=True)
    print(f"maker total PnL=${TP:,.2f} capital=${CAP:,.2f} blended ROI={100*TP/CAP:.2f}%",flush=True)
    print(f"gate3 aggregate fill_rate={fill_all:.3f} (>=0.25: {fill_all>=0.25})",flush=True)
    print(f"gate5 ROI_lift={100*TP/CAP-100*BTP/BCAP:.2f}pp (>v2 2.93pp: {(100*TP/CAP-100*BTP/BCAP)>2.93})",flush=True)
    print(f"gate6 capital ${CAP:,.0f} <v2 $67,346: {CAP<67346}",flush=True)
    print(f"modes corpus: {sp.execution_mode.value_counts(normalize=True).round(3).to_dict()}",flush=True)
    print("underdog harvest (r05_14,r15_24,r25_34 across cats): fill_rate + lift vs v2 universal:",flush=True)
    for reg in ["r05_14","r15_24","r25_34"]:
        gg=sp[sp.regime==reg]; f=(gg.execution_mode!="miss_fallback").mean()
        imp=gg.improvement_vs_baseline_cents.sum()*0.1
        print(f"  {reg}: n={len(gg)} fill={f:.2f} improvement_over_baseline=${imp:,.0f}",flush=True)
    for m,gm in sp.groupby("execution_mode"):
        print(f"  mode {m}: n={len(gm)} pnl=${gm.realized_pnl_cents.sum()*0.1:,.0f} cap=${gm.entry_price_cents.sum()*0.1:,.0f} roi={100*gm.realized_pnl_cents.sum()/gm.entry_price_cents.sum():.1f}% mean_entry={gm.entry_price_cents.mean():.0f}c",flush=True)
    print(f"wall={time.time()-t0:.1f}s peak_rss={rss():.0f}MB",flush=True)
    print("DONE_MARKER",flush=True)
if __name__=="__main__": main()
