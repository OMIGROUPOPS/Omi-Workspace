#!/usr/bin/env python3
"""
build_path_c_phase3_corrected.py — Path C Phase 3 (corrected): per-cell drift-gradient execution mode.

Corrects the prior Phase 3's binary 55c threshold (which net-loses on mild favorites like r55_64,
drift +1.6c < taker cost). Here: cross taker immediately at T-4h ONLY for cells whose MEASURED
Scope-A-T4 drift >= threshold (primary 4c, >2x the ~1.5c taker-conversion cost) = the heavy-favorite
tail (r75_84, r85_94). Else v3 maker-then-fallback. Drift read from data (not hardcoded). Net-of-fees
comparison: 1c flat taker fee on every taker entry (immediate_taker, marketable_taker, miss_fallback);
maker_resting fee 0. Hold all commits.
"""
import json, time, resource
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.dataset as ds, pyarrow.compute as pc
REPO="/root/Omi-Workspace/arb-executor"
TAPE=f"{REPO}/data/durable/per_minute_universe/premarket_tape_v1.parquet"
CSV=f"{REPO}/docs/policy/per_regime_offsets_v1.csv"
SPK={"ATP_MAIN":"atp_main","WTA_MAIN":"wta_main","ATP_CHALL":"atp_chall","WTA_CHALL":"wta_chall"}
OUT_N=f"{REPO}/data/durable/per_minute_universe/probe/path_c_phase3_corrected_per_n_simulation_probe.parquet"
OUT_R=f"{REPO}/data/durable/per_minute_universe/probe/path_c_phase3_corrected_per_regime_summary_probe.parquet"
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
T4REF={("ATP_MAIN","r75_84"):6.50,("ATP_MAIN","r85_94"):10.81,("WTA_MAIN","r75_84"):6.70,("WTA_MAIN","r85_94"):10.94,
       ("ATP_CHALL","r75_84"):6.24,("ATP_CHALL","r85_94"):10.41,("WTA_CHALL","r75_84"):8.87,("WTA_CHALL","r85_94"):13.08,
       ("ATP_MAIN","r05_14"):-10.56,("ATP_MAIN","r55_64"):1.62,("ATP_MAIN","r65_74"):3.09}
FEE_TAKER=1.0  # cents per ct, flat
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"
def main():
    t0=time.time()
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
    csv=pd.read_csv(CSV)
    offmap={(r.category,r.anchor_regime):int(r.bid_offset_cents) for _,r in csv.iterrows()}
    plmap={(r.category,r.anchor_regime):int(r.placement_minute) for _,r in csv.iterrows()}
    sp["base_off"]=sp.apply(lambda r:offmap.get((r.category,r.regime),15),axis=1)
    sp["placement"]=sp.apply(lambda r:plmap.get((r.category,r.regime),240),axis=1)
    atlas=list(sp.ticker); print(f"atlas {len(sp)} rss={rss():.0f}MB",flush=True)

    df=ds.dataset(TAPE).scanner(columns=["ticker","time_to_match_start_min","yes_ask_close","price_close","mid_close"],
        filter=pc.field("ticker").isin(atlas)).to_table().to_pandas()
    df=df.sort_values(["ticker","time_to_match_start_min"],ascending=[True,False])
    df["ask_c"]=df.yes_ask_close*100; df["pcl_c"]=df.price_close*100
    # per-ticker drift (mid@maxttm -> mid@minttm) + arrays
    TK={}; drift_rows=[]
    g=df.groupby("ticker",sort=False)
    imax=g.time_to_match_start_min.idxmax(); imin=g.time_to_match_start_min.idxmin()
    mid4h=df.loc[imax].set_index("ticker").mid_close*100; mid20=df.loc[imin].set_index("ticker").mid_close*100
    sp["drift_n"]=( (mid20-mid4h).reindex(sp.ticker).values )
    for tk,gg in g:
        ttm=gg.time_to_match_start_min.values; ask=gg.ask_c.values; pcl=gg.pcl_c.values
        trig=np.minimum(np.where(np.isnan(ask),np.inf,ask),np.where(np.isnan(pcl),np.inf,pcl))
        TK[tk]=(ttm,ask,trig)
    cell_drift=sp.groupby(["category","regime"]).drift_n.mean()
    print("=== drift gradient (computed) vs Scope A T4 ref ===",flush=True)
    maxdiff=0
    for (cat,reg),v in cell_drift.items():
        ref=T4REF.get((cat,reg))
        if ref is not None:
            diff=abs(v-ref); maxdiff=max(maxdiff,diff)
            print(f"  {cat} {reg}: computed {v:+.2f} ref {ref:+.2f} diff {diff:.2f}",flush=True)
    print(f"max |diff| vs ref (checked cells): {maxdiff:.2f}c (gate3 <=0.5: {maxdiff<=0.5})",flush=True)
    cd=cell_drift.to_dict()

    def realize(entry,win,X,rule,sq):
        if rule.startswith("exit at") and sq>=entry+X: return X,True
        return ((99-entry) if win else -(entry-1)),False
    def v3_entry(tk,anchor,off,pl):
        bid=max(anchor-off,1); ttm,ask,trig=TK[tk]
        a=ask[ttm==pl]; a=float(a[0]) if len(a) else np.nan
        if not np.isnan(a) and a<=bid: return "marketable_taker",int(round(a)),True
        w=(ttm<=pl)&(ttm>=20)&(trig<=bid); hit=np.where(w)[0]
        if len(hit): return "maker_resting",int(bid),False
        return "miss_fallback",int(anchor),True
    def imm_taker(tk):
        ttm,ask,trig=TK[tk]
        for tgt in range(245,234,-1):
            m=np.where(ttm==tgt)[0]
            if len(m) and not np.isnan(ask[m[0]]): return int(round(ask[m[0]]))
        return None
    def run(threshold):
        gr=np.empty(len(sp)); en=np.empty(len(sp),int); md=[]; tg=np.zeros(len(sp),bool); fee=np.zeros(len(sp)); nfb=0
        for i,(tk,anchor,off,pl,win,sqc,cat,reg) in enumerate(zip(sp.ticker,sp.anchor_c,sp.base_off,sp.placement,sp.win,sp.sq_c,sp.category,sp.regime)):
            fav = cd.get((cat,reg),0.0) >= threshold
            if fav:
                e=imm_taker(tk)
                if e is None: mode,entry,taker=v3_entry(tk,anchor,off,pl); nfb+=1
                else: mode,entry,taker="immediate_taker",e,True
            else:
                mode,entry,taker=v3_entry(tk,anchor,off,pl)
            X,rule=bx[cat].get(anchor,(0,"hold")); rr,tt=realize(entry,win,X,rule,sqc)
            gr[i]=rr; en[i]=entry; md.append(mode); tg[i]=tt; fee[i]=FEE_TAKER if taker else 0.0
        return gr,en,np.array(md),tg,fee,nfb
    # v3 baseline (threshold huge -> nobody favorite)
    g0,e0,m0,t0g,f0,_=run(1000.0)
    v3_gross=g0.sum()*0.1; v3_cap=e0.sum()*0.1; v3_fee=f0.sum()*0.1; v3_net=(g0-f0).sum()*0.1
    print(f"v3-repro: gross=${v3_gross:,.2f} cap=${v3_cap:,.2f} fee=${v3_fee:,.0f} net=${v3_net:,.2f} grossROI={100*v3_gross/v3_cap:.2f}% netROI={100*v3_net/v3_cap:.2f}%",flush=True)

    variants={}
    for thr in [3,4,5,6]:
        gr,en,md,tg,fee,nfb=run(float(thr))
        gross=gr.sum()*0.1; cap=en.sum()*0.1; feeT=fee.sum()*0.1; net=(gr-fee).sum()*0.1
        variants[thr]=dict(gr=gr,en=en,md=md,tg=tg,fee=fee,gross=gross,cap=cap,net=net,feeT=feeT,
            grossROI=100*gross/cap,netROI=100*net/cap,imm=(md=="immediate_taker").mean(),nfb=nfb)
        print(f"thr{thr}c: grossROI={100*gross/cap:.2f}% netROI={100*net/cap:.2f}% net=${net:,.0f} imm_frac={(md=='immediate_taker').mean():.3f} fee=${feeT:,.0f} nfb={nfb}",flush=True)
    bestnet=max(variants,key=lambda k:variants[k]["netROI"])
    print(f"BEST-by-netROI: thr{bestnet}c netROI={variants[bestnet]['netROI']:.2f}% vs v3 net {100*v3_net/v3_cap:.2f}%",flush=True)
    P=variants[4]  # primary

    # immediate-taker cohort = cells with drift>=4 (primary)
    favcell=sp.apply(lambda r: cd.get((r.category,r.regime),0.0)>=4.0,axis=1).values
    print(f"gate5 imm-taker cohort (drift>=4c cells, n={favcell.sum()}): Phase3 mean entry={P['en'][favcell].mean():.2f}c vs v3 {e0[favcell].mean():.2f}c",flush=True)
    nonfav=~favcell
    coh_id = np.array_equal(P['en'][nonfav],e0[nonfav]) and np.allclose(P['gr'][nonfav],g0[nonfav]) and np.array_equal(P['md'][nonfav],m0[nonfav])
    print(f"gate4 non-immediate cohort (n={nonfav.sum()}) identical to v3: {coh_id}",flush=True)

    # outputs (primary)
    out1=pd.DataFrame({"ticker":sp.ticker,"event_ticker":sp.event_ticker,"category":sp.category,"anchor_regime":sp.regime,
        "anchor_price_cents":sp.anchor_c,"expected_drift_cents":sp.apply(lambda r:cd.get((r.category,r.regime),0.0),axis=1),
        "phase3_execution_mode":P['md'],"entry_price_cents":P['en'],
        "entry_minute":np.where(P['md']=="immediate_taker",240,np.where(P['md']=="miss_fallback",20,np.nan)),
        "gross_realized_pnl_cents":P['gr'],"fee_cents":P['fee'],"net_realized_pnl_cents":P['gr']-P['fee'],
        "v3_net_pnl_cents":g0-f0,"improvement_vs_v3_cents":(P['gr']-P['fee'])-(g0-f0)})
    import os; os.makedirs(os.path.dirname(OUT_N),exist_ok=True)
    pq.write_table(pa.Table.from_pandas(out1,preserve_index=False),OUT_N,compression="snappy")
    rows=[]; dom=0
    for (cat,reg),idx in sp.groupby(["category","regime"]).groups.items():
        ii=sp.index.get_indexer(idx)
        pnet=(P['gr'][ii]-P['fee'][ii]).sum()*0.1; cap=P['en'][ii].sum()*0.1
        vnet=(g0[ii]-f0[ii]).sum()*0.1; vcap=e0[ii].sum()*0.1
        proi=100*pnet/cap if cap else np.nan; vroi=100*vnet/vcap if vcap else np.nan
        if proi>=vroi-1e-9: dom+=1
        rows.append(dict(category=cat,anchor_regime=reg,n_tickers=len(ii),expected_drift_cents=cd.get((cat,reg),0.0),
            mean_entry=float(P['en'][ii].mean()),v3_mean_entry=float(e0[ii].mean()),
            net_pnl=float(pnet),capital=float(cap),net_roi_pct=proi,v3_net_roi_pct=vroi,improvement_pp=proi-vroi,
            imm_taker_frac=float((P['md'][ii]=="immediate_taker").mean())))
    agg=pd.DataFrame(rows); pq.write_table(pa.Table.from_pandas(agg,preserve_index=False),OUT_R,compression="snappy")

    print("per-mode (primary thr4, net):",flush=True)
    for m in ["immediate_taker","marketable_taker","maker_resting","miss_fallback"]:
        mm=P['md']==m
        if mm.sum(): print(f"  {m}: n={mm.sum()} mean_entry={P['en'][mm].mean():.0f}c net_pnl=${(P['gr'][mm]-P['fee'][mm]).sum()*0.1:,.0f} netROI={100*(P['gr'][mm]-P['fee'][mm]).sum()/P['en'][mm].sum():.1f}%",flush=True)
    fav_contrib=((P['gr'][favcell]-P['fee'][favcell]).sum()-(g0[favcell]-f0[favcell]).sum())*0.1
    print(f"8-cell favorite immediate-taker net contribution vs v3: ${fav_contrib:,.1f}",flush=True)
    print("=== GATES ===",flush=True)
    print(f"gate1 v3 gross ${v3_gross:,.2f} within2% of $8,098.50: {abs(v3_gross-8098.50)/8098.50<=0.02}",flush=True)
    print(f"gate2 rows={len(out1)}",flush=True)
    print(f"gate3 drift match maxdiff {maxdiff:.2f}c <=0.5: {maxdiff<=0.5}",flush=True)
    print(f"gate4 cohort identical: {coh_id}",flush=True)
    print(f"gate5 imm mean entry {P['en'][favcell].mean():.2f} < v3 {e0[favcell].mean():.2f}: {P['en'][favcell].mean()<e0[favcell].mean()}",flush=True)
    print(f"gate6 primary netROI {P['netROI']:.2f}% >= v3 netROI {100*v3_net/v3_cap:.2f}%: {P['netROI']>=100*v3_net/v3_cap} | vs v3 gross 12.11%: {P['netROI']>=12.11} | BEST thr{bestnet} {variants[bestnet]['netROI']:.2f}%",flush=True)
    print(f"per-cell net dominance {dom}/36",flush=True)
    meta=dict(v3_gross=float(v3_gross),v3_net=float(v3_net),v3_net_roi=float(100*v3_net/v3_cap),v3_cap=float(v3_cap),
        drift_maxdiff=float(maxdiff),variants={str(k):dict(grossROI=float(v["grossROI"]),netROI=float(v["netROI"]),net=float(v["net"]),imm_frac=float((v["md"]=="immediate_taker").mean()),fee=float(v["feeT"]),nfb=int(v["nfb"])) for k,v in variants.items()},
        best_net_thr=int(bestnet),cohort_identical=bool(coh_id),per_cell_dominance=int(dom),
        imm_mean_entry=float(P['en'][favcell].mean()),v3_imm_cohort_entry=float(e0[favcell].mean()),fav8_contrib=float(fav_contrib))
    json.dump(meta,open("/tmp/path_c_p3c_meta.json","w"),indent=2,default=float)
    print(f"wall={time.time()-t0:.1f}s peak_rss={rss():.0f}MB",flush=True); print("DONE_MARKER",flush=True)
if __name__=="__main__": main()
