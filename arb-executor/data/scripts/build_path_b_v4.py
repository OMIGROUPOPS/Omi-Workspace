#!/usr/bin/env python3
"""
build_path_b_v4.py — per-cell offset re-optimization on the FULL-STRATEGY net-PnL objective.

v1 picked per-cell offsets maximizing entry-capture (fill_rate x offset). v4 re-sweeps the
(placement_minute x offset) grid per (category x anchor_regime) cell maximizing NET realized PnL
through the full strategy (entry + atlas X exit + miss fallback - 1c taker fee). Candidate set per
cell = the 84-grid UNION v3's exact config (so the winner is >= v3 by construction).
"""
import json, time, resource
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.dataset as ds, pyarrow.compute as pc
REPO="/root/Omi-Workspace/arb-executor"
TAPE=f"{REPO}/data/durable/per_minute_universe/premarket_tape_v1.parquet"
CSV=f"{REPO}/docs/policy/per_regime_offsets_v1.csv"
SPK={"ATP_MAIN":"atp_main","WTA_MAIN":"wta_main","ATP_CHALL":"atp_chall","WTA_CHALL":"wta_chall"}
OUT_N=f"{REPO}/data/durable/per_minute_universe/probe/path_b_v4_per_n_simulation_probe.parquet"
OUT_C=f"{REPO}/data/durable/per_minute_universe/probe/path_b_v4_cell_optimum_probe.parquet"
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
PLACE=[240,180,120,90,60,30,20]; OFFS=[0,1,2,3,4,5,7,10,12,15,18,20]; FEE=1.0
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
    v3off={(r.category,r.anchor_regime):int(r.bid_offset_cents) for _,r in csv.iterrows()}
    v3pl={(r.category,r.anchor_regime):int(r.placement_minute) for _,r in csv.iterrows()}
    N=len(sp); atlas=list(sp.ticker); print(f"atlas {N} rss={rss():.0f}MB",flush=True)
    # per-N atlas X / rule
    Xarr=np.array([bx[c].get(a,(0,"hold"))[0] for c,a in zip(sp.category,sp.anchor_c)])
    ruleexit=np.array([bx[c].get(a,(0,"hold"))[1].startswith("exit at") for c,a in zip(sp.category,sp.anchor_c)])
    anchor=sp.anchor_c.values.astype(float); win=sp.win.values; sq=sp.sq_c.values.astype(float)

    df=ds.dataset(TAPE).scanner(columns=["ticker","time_to_match_start_min","yes_ask_close","price_close"],
        filter=pc.field("ticker").isin(atlas)).to_table().to_pandas()
    df["ask_c"]=df.yes_ask_close*100; df["pcl_c"]=df.price_close*100
    pos={tk:i for i,tk in enumerate(sp.ticker)}
    ask_pl=np.full((N,len(PLACE)),np.nan); mintrig_pl=np.full((N,len(PLACE)),np.inf)
    for tk,gg in df.groupby("ticker",sort=False):
        i=pos[tk]
        ttm=gg.time_to_match_start_min.values.astype(int); ask=gg.ask_c.values; pcl=gg.pcl_c.values
        trig=np.minimum(np.where(np.isnan(ask),np.inf,ask),np.where(np.isnan(pcl),np.inf,pcl))
        order=np.argsort(ttm); ta=ttm[order]; tr=trig[order]; cmin=np.minimum.accumulate(tr)  # cummin over [20,ttm asc]
        ad={t:a for t,a in zip(ttm,ask)}
        for k,pl in enumerate(PLACE):
            a=ad.get(pl,np.nan)
            if np.isnan(a):
                for d_ in range(1,6):
                    if pl-d_ in ad and not np.isnan(ad[pl-d_]): a=ad[pl-d_]; break
                    if pl+d_ in ad and not np.isnan(ad[pl+d_]): a=ad[pl+d_]; break
            ask_pl[i,k]=a
            le=np.searchsorted(ta,pl,side="right")-1   # largest ttm <= pl
            mintrig_pl[i,k]=cmin[le] if le>=0 else np.inf
    print(f"precompute done rss={rss():.0f}MB",flush=True)

    def eval_config(pl_idx,off):
        bid=np.maximum(anchor-off,1.0)
        ask=ask_pl[:,pl_idx]; mt=mintrig_pl[:,pl_idx]
        marketable=(~np.isnan(ask))&(ask<=bid)
        resting=(~marketable)&(mt<=bid)
        miss=(~marketable)&(~resting)
        entry=np.where(marketable,np.round(ask),np.where(resting,bid,anchor))
        taker=marketable|miss
        trig=ruleexit&(sq>=entry+Xarr)
        realized=np.where(trig,Xarr.astype(float),np.where(win,99-entry,-(entry-1)))
        fee=np.where(taker,FEE,0.0)
        mode=np.where(marketable,0,np.where(resting,1,2))  # 0 mkt,1 rest,2 miss
        return entry,realized,fee,realized-fee,mode
    plidx={p:i for i,p in enumerate(PLACE)}

    # evaluate v3 per-N config (gate1) + full grid
    # v3 per-N
    v3_pl_n=np.array([v3pl[(c,r)] for c,r in zip(sp.category,sp.regime)])
    v3_off_n=np.array([v3off[(c,r)] for c,r in zip(sp.category,sp.regime)])
    # v3 may use placement/offset not in grid (offset 8); eval directly per-N
    def eval_perN(pl_n,off_n):
        # ask/mintrig at each N's pl_n (must be in PLACE; v3 placements are subset of PLACE)
        ai=np.array([plidx[p] for p in pl_n])
        ask=ask_pl[np.arange(N),ai]; mt=mintrig_pl[np.arange(N),ai]
        bid=np.maximum(anchor-off_n,1.0)
        marketable=(~np.isnan(ask))&(ask<=bid); resting=(~marketable)&(mt<=bid); miss=(~marketable)&(~resting)
        entry=np.where(marketable,np.round(ask),np.where(resting,bid,anchor)); taker=marketable|miss
        trig=ruleexit&(sq>=entry+Xarr); realized=np.where(trig,Xarr.astype(float),np.where(win,99-entry,-(entry-1)))
        return entry,realized-np.where(taker,FEE,0.0)
    v3_entry,v3_net=eval_perN(v3_pl_n,v3_off_n)
    v3_gross=( eval_perN(v3_pl_n,v3_off_n)[1] + np.where((eval_config(0,0)[3]*0),0,0) ).sum()  # placeholder
    # gross for v3: recompute without fee
    aiv=np.array([plidx[p] for p in v3_pl_n]); askv=ask_pl[np.arange(N),aiv]; mtv=mintrig_pl[np.arange(N),aiv]
    bidv=np.maximum(anchor-v3_off_n,1.0); mk=(~np.isnan(askv))&(askv<=bidv); rs=(~mk)&(mtv<=bidv); ms=(~mk)&(~rs)
    env=np.where(mk,np.round(askv),np.where(rs,bidv,anchor)); tk=mk|ms
    trv=ruleexit&(sq>=env+Xarr); grv=np.where(trv,Xarr.astype(float),np.where(win,99-env,-(env-1)))
    v3_gross=grv.sum()*0.1; v3_cap=env.sum()*0.1; v3_net_tot=v3_net.sum()*0.1
    print(f"v3-repro: gross=${v3_gross:,.2f} net=${v3_net_tot:,.2f} cap=${v3_cap:,.2f} grossROI={100*v3_gross/v3_cap:.2f}% netROI={100*v3_net_tot/v3_cap:.2f}%",flush=True)

    # full grid: store net & entry per config; aggregate per cell
    cellkey=(sp.category+"|"+sp.regime).values
    cells=sorted(set(cellkey))
    long_parts=[]
    # per (cell,config) net sum + cap sum
    rec={}  # (cell,pl,off)->(netsum,capsum,fill,n)
    for pl in PLACE:
        for off in OFFS:
            entry,realized,fee,net,mode=eval_config(plidx[pl],off)
            # long table rows (downsample? keep full)
            long_parts.append(pd.DataFrame({"ticker":sp.ticker.values,"cell":cellkey,"placement_minute":pl,"offset":off,
                "execution_mode":pd.Categorical.from_codes(mode,["marketable_taker","maker_resting","miss_fallback"]),
                "entry_price":entry.astype(int),"gross_pnl":realized,"fee":fee,"net_pnl":net}))
            dfc=pd.DataFrame({"cell":cellkey,"net":net,"cap":entry,"fill":(mode!=2)})
            gb=dfc.groupby("cell").agg(net=("net","sum"),cap=("cap","sum"),fill=("fill","mean"),n=("net","size"))
            for cell,row in gb.iterrows():
                rec[(cell,pl,off)]=(row.net,row.cap,row.fill,int(row.n))
    print(f"grid evaluated rss={rss():.0f}MB",flush=True)
    # v3 per cell sums
    v3cell={}
    dfv=pd.DataFrame({"cell":cellkey,"net":v3_net,"cap":v3_entry}); gv=dfv.groupby("cell").agg(net=("net","sum"),cap=("cap","sum"))
    for cell,row in gv.iterrows(): v3cell[cell]=(row.net,row.cap)

    # per-cell winner (over grid + v3)
    crows=[]; dom_v3=0; mat=0; winners={}
    for cell in cells:
        cat,reg=cell.split("|"); v3p=v3pl[(cat,reg)]; v3o=v3off[(cat,reg)]
        cands=[(pl,off,rec[(cell,pl,off)][0],rec[(cell,pl,off)][1],rec[(cell,pl,off)][2]) for pl in PLACE for off in OFFS]
        cands.append((v3p,v3o,v3cell[cell][0],v3cell[cell][1],np.nan))  # v3 candidate
        best=max(cands,key=lambda x:x[2])
        wpl,woff,wnet,wcap,wfill=best
        v3net,v3cap=v3cell[cell]
        wroi=100*wnet*0.1/(wcap*0.1) if wcap else np.nan; v3roi=100*v3net*0.1/(v3cap*0.1) if v3cap else np.nan
        imp=wroi-v3roi
        if wnet>=v3net-1e-9: dom_v3+=1
        if imp>=0.5: mat+=1
        winners[cell]=(wpl,woff,wnet,wcap)
        crows.append(dict(category=cat,anchor_regime=reg,winning_placement_minute=int(wpl),winning_offset=int(woff),
            n_tickers=rec[(cell,PLACE[0],OFFS[0])][3],winning_fill_rate=float(wfill) if not np.isnan(wfill) else np.nan,
            winning_net_pnl=float(wnet*0.1),winning_net_roi=float(wroi),
            v3_baseline_placement_minute=v3p,v3_baseline_offset=v3o,v3_baseline_net_pnl=float(v3net*0.1),v3_baseline_net_roi=float(v3roi),
            improvement_pp=float(imp)))
    cellopt=pd.DataFrame(crows)
    # corpus v4
    v4_net=sum(winners[c][2] for c in cells)*0.1; v4_cap=sum(winners[c][3] for c in cells)*0.1
    print(f"v4 winner: net=${v4_net:,.2f} cap=${v4_cap:,.2f} netROI={100*v4_net/v4_cap:.2f}% vs v3 net {100*v3_net_tot/v3_cap:.2f}%",flush=True)
    print(f"improvement distribution pp: mean={cellopt.improvement_pp.mean():.3f} median={cellopt.improvement_pp.median():.3f} max={cellopt.improvement_pp.max():.3f} min={cellopt.improvement_pp.min():.3f}",flush=True)
    print(f"cells winner!=v3 offset-or-placement: {((cellopt.winning_offset!=cellopt.v3_baseline_offset)|(cellopt.winning_placement_minute!=cellopt.v3_baseline_placement_minute)).sum()}/36",flush=True)
    print(f"cells with material improvement (>=0.5pp): {mat}/36",flush=True)
    print(f"winning offsets value_counts: {cellopt.winning_offset.value_counts().to_dict()}",flush=True)
    print(f"winning placements value_counts: {cellopt.winning_placement_minute.value_counts().to_dict()}",flush=True)

    # outputs
    import os; os.makedirs(os.path.dirname(OUT_N),exist_ok=True)
    longdf=pd.concat(long_parts,ignore_index=True)
    pq.write_table(pa.Table.from_pandas(longdf,preserve_index=False),OUT_N,compression="snappy")
    pq.write_table(pa.Table.from_pandas(cellopt,preserve_index=False),OUT_C,compression="snappy")
    cellopt.to_csv("/tmp/path_b_v4_cell_optimum.csv",index=False)

    print("=== GATES ===",flush=True)
    print(f"gate1 v3 gross ${v3_gross:,.2f} within2% of $8,098.50: {abs(v3_gross-8098.50)/8098.50<=0.02}",flush=True)
    print(f"gate2 long rows={len(longdf)} (expect 14033*84={14033*84})",flush=True)
    print(f"gate3 cells winner>=v3: {dom_v3}/36 (==36: {dom_v3==36})",flush=True)
    print(f"gate4 non-degeneracy: distinct winning (pl,off) = {cellopt[['winning_placement_minute','winning_offset']].drop_duplicates().shape[0]}",flush=True)
    print(f"gate5 corpus v4 netROI {100*v4_net/v4_cap:.2f}% >= v3 net {100*v3_net_tot/v3_cap:.2f}%: {v4_net>=v3_net_tot}",flush=True)
    v4_minus_v3_pp=100*v4_net/v4_cap-100*v3_net_tot/v3_cap
    print(f"gate6 MATERIAL: v4 netROI - v3 netROI = {v4_minus_v3_pp:+.3f}pp (>=0.5pp: {v4_minus_v3_pp>=0.5})",flush=True)
    meta=dict(v3_gross=float(v3_gross),v3_net=float(v3_net_tot),v3_net_roi=float(100*v3_net_tot/v3_cap),
        v4_net=float(v4_net),v4_cap=float(v4_cap),v4_net_roi=float(100*v4_net/v4_cap),v4_minus_v3_pp=float(v4_minus_v3_pp),
        cells_winner_ne_v3=int(((cellopt.winning_offset!=cellopt.v3_baseline_offset)|(cellopt.winning_placement_minute!=cellopt.v3_baseline_placement_minute)).sum()),
        material_cells=int(mat),dom_v3=int(dom_v3),imp_mean=float(cellopt.improvement_pp.mean()),imp_max=float(cellopt.improvement_pp.max()),
        winning_offsets=cellopt.winning_offset.value_counts().to_dict(),winning_placements=cellopt.winning_placement_minute.value_counts().to_dict())
    json.dump(meta,open("/tmp/path_b_v4_meta.json","w"),indent=2,default=float)
    print(f"wall={time.time()-t0:.1f}s peak_rss={rss():.0f}MB",flush=True); print("DONE_MARKER",flush=True)
if __name__=="__main__": main()
