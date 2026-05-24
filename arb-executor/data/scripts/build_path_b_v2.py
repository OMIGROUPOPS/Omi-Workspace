#!/usr/bin/env python3
"""
build_path_b_v2.py — Path B v2: marketable-vs-resting split + atlas exit-rule replay.

Single-rule strategy (T-240 placement, 15c universal offset) over all 14,033 atlas N.
Per N: determine execution mode at T-240 (marketable_taker / maker_resting / miss_fallback),
capture actual entry_price, then replay the locked atlas cell rule from that entry forward and
compute realized PnL per ct. Compares to the atlas baseline (entry at T-20m anchor).

SUBSTRATE (resolved; documented in run_summary deviations): the atlas exit-rule replay uses the
spike_perN columns size_qual_max_250 (the >=250ct depth-qualified max price reached post-anchor) and
settlement_value. "exit at +X" triggers iff entry+X <= size_qual_max_250_cents (interpretation per
prompt Step 1/3: realized = X above ANY entry). Because maker/marketable entries are <= anchor, the
target entry+X <= anchor+X, so this is a conservative LOWER BOUND on the true post-entry trigger
(the pre-T-20m window, where a climbing favorite can also hit the target, is not added in). No
g9_trades / post-T-20m trajectory walk is required; spike_cents/size_qual were themselves baked from
g9_trades by build_spike_perN.py.
"""
import json, time, resource
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.dataset as ds, pyarrow.compute as pc
REPO="/root/Omi-Workspace/arb-executor"
TAPE=f"{REPO}/data/durable/per_minute_universe/premarket_tape_v1.parquet"
SPK={"ATP_MAIN":"atp_main","WTA_MAIN":"wta_main","ATP_CHALL":"atp_chall","WTA_CHALL":"wta_chall"}
OUT_N=f"{REPO}/data/durable/per_minute_universe/probe/path_b_v2_per_n_simulation_probe.parquet"
OUT_R=f"{REPO}/data/durable/per_minute_universe/probe/path_b_v2_per_regime_summary_probe.parquet"
OFFSET=15; PLACEMENT=240
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"
def main():
    t0=time.time()
    # spike + descriptive
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
    sp["regime"]=sp.anchor_c.map(band)
    sp["win"]=(sp.settlement_value.astype(int)==1)
    atlas=set(sp.ticker)
    print(f"atlas N={len(sp)} rss={rss():.0f}MB",flush=True)

    # tape entry side
    df=ds.dataset(TAPE).scanner(columns=["ticker","time_to_match_start_min","yes_ask_close","price_close"],
        filter=pc.field("ticker").isin(list(atlas))).to_table().to_pandas()
    df["ask_c"]=(df.yes_ask_close*100); df["pcl_c"]=(df.price_close*100)
    df=df.sort_values(["ticker","time_to_match_start_min"],ascending=[True,False])
    print(f"tape rows={len(df)} rss={rss():.0f}MB",flush=True)
    # per ticker: ask@240 and resting-fill minute for a given bid (bid depends on anchor; compute per ticker)
    anchor_map=dict(zip(sp.ticker,sp.anchor_c))
    ask240={}; trigger_by_tk={}
    for tk,gg in df.groupby("ticker",sort=False):
        ttm=gg.time_to_match_start_min.values; ask=gg.ask_c.values; pcl=gg.pcl_c.values
        a240=ask[ttm==PLACEMENT]; ask240[tk]=float(a240[0]) if len(a240) else np.nan
        trig=np.minimum(np.where(np.isnan(ask),np.inf,ask),np.where(np.isnan(pcl),np.inf,pcl))
        trigger_by_tk[tk]=(ttm,trig)
    # compute mode/entry per N
    modes=[]; entries=[]; emins=[]
    for _,r in sp.iterrows():
        tk=r.ticker; anchor=r.anchor_c; bid=max(anchor-OFFSET,1)
        a240=ask240.get(tk,np.nan)
        if not np.isnan(a240) and a240<=bid:
            modes.append("marketable_taker"); entries.append(int(round(a240))); emins.append(PLACEMENT); continue
        ttm,trig=trigger_by_tk[tk]
        hit=np.where((ttm<=PLACEMENT)&(ttm>=20)&(trig<=bid))[0]
        if len(hit):
            # earliest = highest ttm among hits (ttm sorted desc so first index in window)
            order=np.argsort(-ttm[hit])  # highest ttm first
            fi=hit[order[0]]
            modes.append("maker_resting"); entries.append(int(bid)); emins.append(int(ttm[fi]))
        else:
            modes.append("miss_fallback"); entries.append(int(anchor)); emins.append(20)
    sp["execution_mode"]=modes; sp["entry_price_cents"]=entries; sp["entry_minute"]=emins
    sp["bid_price_cents"]=np.maximum(sp.anchor_c-OFFSET,1)

    # replay
    def realize(entry,win,X,rule,sq):
        if rule.startswith("exit at") and sq>=entry+X:
            return X,True
        return ((99-entry) if win else -(entry-1)),False
    rl=[];tr=[];bx_X=[];bx_rule=[];base=[]
    for _,r in sp.iterrows():
        info=bx[r.category].get(r.anchor_c)
        X,rule=info if info else (0,"hold")
        bx_X.append(X); bx_rule.append(rule)
        rr,tt=realize(r.entry_price_cents,r.win,X,rule,r.sq_c); rl.append(rr); tr.append(tt)
        bb,_=realize(r.anchor_c,r.win,X,rule,r.sq_c); base.append(bb)
    sp["cell_best_exit_X"]=bx_X; sp["cell_rule"]=bx_rule
    sp["realized_pnl_cents"]=rl; sp["exit_triggered"]=tr
    sp["exit_minute"]=np.nan  # proxy gives boolean trigger, not the minute (documented)
    sp["atlas_baseline_realized_pnl_cents"]=base
    sp["improvement_vs_baseline_cents"]=sp.realized_pnl_cents-sp.atlas_baseline_realized_pnl_cents

    out1=sp[["ticker","event_ticker","category","anchor_c","regime","settlement_value","bid_price_cents",
        "execution_mode","entry_price_cents","entry_minute","cell_best_exit_X","cell_rule","exit_triggered",
        "exit_minute","realized_pnl_cents","atlas_baseline_realized_pnl_cents","improvement_vs_baseline_cents"]].rename(
        columns={"anchor_c":"anchor_price_cents","regime":"anchor_regime"})
    import os; os.makedirs(os.path.dirname(OUT_N),exist_ok=True)
    pq.write_table(pa.Table.from_pandas(out1,preserve_index=False),OUT_N,compression="snappy")

    # aggregation
    sp["cap_c"]=sp.entry_price_cents; sp["base_cap_c"]=sp.anchor_c
    rows=[]
    for (cat,reg),g in sp.groupby(["category","regime"],observed=True):
        n=len(g); pnl=g.realized_pnl_cents.sum()*0.1; cap=g.cap_c.sum()*0.1
        bpnl=g.atlas_baseline_realized_pnl_cents.sum()*0.1; bcap=g.base_cap_c.sum()*0.1
        rows.append(dict(category=cat,anchor_regime=reg,n_tickers=n,
            pct_marketable_taker=(g.execution_mode=="marketable_taker").mean(),
            pct_maker_resting=(g.execution_mode=="maker_resting").mean(),
            pct_miss_fallback=(g.execution_mode=="miss_fallback").mean(),
            mean_realized_pnl_cents=g.realized_pnl_cents.mean(),
            total_realized_pnl_dollars=pnl, capital_deployed_dollars=cap,
            roi_pct=100*pnl/cap if cap else np.nan,
            atlas_baseline_roi_pct=100*bpnl/bcap if bcap else np.nan,
            roi_lift_pct=(100*pnl/cap-100*bpnl/bcap) if cap and bcap else np.nan))
    agg=pd.DataFrame(rows)
    pq.write_table(pa.Table.from_pandas(agg,preserve_index=False),OUT_R,compression="snappy")

    # corpus + gates
    TP=sp.realized_pnl_cents.sum()*0.1; CAP=sp.cap_c.sum()*0.1
    BTP=sp.atlas_baseline_realized_pnl_cents.sum()*0.1; BCAP=sp.base_cap_c.sum()*0.1
    print("=== VALIDATION ===",flush=True)
    print(f"gate2 rows={len(out1)} (expect 14033)",flush=True)
    print(f"gate1 baseline_total=${BTP:,.2f} (atlas $6,158.20; ratio {BTP/6158.20:.4f}) baseline_cap=${BCAP:,.2f}",flush=True)
    print(f"      baseline within +-2%: {abs(BTP-6158.20)/6158.20<=0.02}",flush=True)
    print(f"maker total PnL=${TP:,.2f}  capital=${CAP:,.2f}  blended ROI={100*TP/CAP:.2f}%",flush=True)
    print(f"gate4 mean realized {sp.realized_pnl_cents.mean():.3f}c > baseline {sp.atlas_baseline_realized_pnl_cents.mean():.3f}c: {sp.realized_pnl_cents.mean()>sp.atlas_baseline_realized_pnl_cents.mean()}",flush=True)
    print(f"gate5 maker capital ${CAP:,.0f} < atlas ${BCAP:,.0f}: {CAP<BCAP}",flush=True)
    print(f"execution modes corpus: {sp.execution_mode.value_counts(normalize=True).round(3).to_dict()}",flush=True)
    print("gate3 mode dist by regime (ATP_MAIN):",flush=True)
    for reg in ["r05_14","r45_54","r85_94"]:
        gg=sp[(sp.category=="ATP_MAIN")&(sp.regime==reg)]
        print(f"  {reg}: mkt={ (gg.execution_mode=='marketable_taker').mean():.2f} rest={(gg.execution_mode=='maker_resting').mean():.2f} miss={(gg.execution_mode=='miss_fallback').mean():.2f}",flush=True)
    print("per-mode contribution:",flush=True)
    for m,gm in sp.groupby("execution_mode"):
        print(f"  {m}: n={len(gm)} pnl=${gm.realized_pnl_cents.sum()*0.1:,.0f} cap=${gm.cap_c.sum()*0.1:,.0f} roi={100*gm.realized_pnl_cents.sum()/gm.cap_c.sum():.1f}% mean_entry={gm.entry_price_cents.mean():.0f}c",flush=True)
    print(f"agg rows={len(agg)}  wall={time.time()-t0:.1f}s peak_rss={rss():.0f}MB",flush=True)
    print(f"CORPUS_BLENDED_ROI={100*TP/CAP:.2f} ATLAS_BASELINE_ROI={100*BTP/BCAP:.2f}",flush=True)
    print("DONE_MARKER",flush=True)
if __name__=="__main__": main()
