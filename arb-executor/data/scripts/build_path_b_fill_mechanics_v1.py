#!/usr/bin/env python3
"""
build_path_b_fill_mechanics_v1.py — premarket maker-bid FILL MECHANICS across the atlas corpus.

Single concern (Axis 2 entry-side improvement, per G22; downstream of locked atlas T42 d99c6e9):
for each atlas N x (placement_minute, bid_offset_cents), would a maker bid posted at
bid_price = anchor_price_cents - bid_offset_cents have FILLED by natural premarket trajectory
between the placement minute and T-20m? Pure fill mechanics — NO PnL, NO exit logic, NO settlement.

Fill condition at minute cadence: fill if price_close (last_traded, when non-null) <= bid_price
OR yes_ask_close <= bid_price. First minute walking forward from placement_minute toward T-20m
(i.e. highest time_to_match_start_min <= placement_minute satisfying the condition) is the fill.

Grid: placement_minute in {240,180,120,90,60,40} x bid_offset in {1,2,3,5,8,10,15} = 42 cells/N.
14,033 atlas N x 42 = 589,386 rows.
"""
import json, time, resource, datetime as dt
from pathlib import Path
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.dataset as ds, pyarrow.compute as pc, pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent.parent
TAPE = REPO / "data/durable/per_minute_universe/premarket_tape_v1.parquet"
SPK = {"ATP_MAIN": "atp_main", "WTA_MAIN": "wta_main", "ATP_CHALL": "atp_chall", "WTA_CHALL": "wta_chall"}
OUT_N = REPO / "data/durable/per_minute_universe/probe/path_b_per_n_fill_results_probe.parquet"
OUT_R = REPO / "data/durable/per_minute_universe/probe/path_b_per_regime_fill_summary_probe.parquet"

PLACEMENTS = [240, 180, 120, 90, 60, 40]
OFFSETS = np.array([1, 2, 3, 5, 8, 10, 15], dtype=np.int64)
BANDS = [(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
         (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
STD_REGIMES = [b[2] for b in BANDS]

def rss_mb(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0
def band(c):
    if c is None or np.isnan(c): return "r_oob"
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"

def main():
    t0=time.time()
    meta={}
    for cat,s in SPK.items():
        t=pq.read_table(REPO/f"data/durable/spike_volatility_map/{s}_spike_perN.parquet",columns=["ticker","anchor_price"])
        for k,a in zip(t.column("ticker").to_pylist(),t.column("anchor_price").to_pylist()):
            c=int(round(a*100)) if a is not None else None
            meta[k]=(cat,c,band(float(c) if c is not None else np.nan))
    atlas=list(meta)
    print(f"atlas N: {len(atlas)}  rss={rss_mb():.0f}MB",flush=True)

    df=ds.dataset(TAPE).scanner(columns=["ticker","time_to_match_start_min","yes_ask_close","price_close"],
        filter=pc.field("ticker").isin(atlas)).to_table().to_pandas()
    # cents; trigger = min(ask, price_close) with NaN -> +inf (that minute can't fill on that channel)
    ask=(df["yes_ask_close"]*100).to_numpy(dtype=np.float64,copy=True); ask[np.isnan(ask)]=np.inf
    pcl=(df["price_close"]*100).to_numpy(dtype=np.float64,copy=True); pcl[np.isnan(pcl)]=np.inf
    df["trigger"]=np.minimum(ask,pcl)
    df["ttm"]=df["time_to_match_start_min"].to_numpy(dtype=np.int64)
    print(f"atlas tape rows: {len(df)}  rss={rss_mb():.0f}MB",flush=True)

    # per-ticker arrays sorted by ttm desc
    df=df.sort_values(["ticker","ttm"],ascending=[True,False])
    grp=df.groupby("ticker",sort=False)
    tick_arr=df["ticker"].to_numpy()
    trig_all=df["trigger"].to_numpy(); ttm_all=df["ttm"].to_numpy()
    # group boundaries
    starts=grp.size().cumsum().to_numpy();
    keys=list(grp.groups.keys())  # group order matches sort (sort=False keeps first-appearance = sorted ticker)
    # build index ranges
    sizes=grp.size().to_numpy(); ends=np.cumsum(sizes); begins=ends-sizes

    rows_ticker=[]; rows_event=[]; rows_cat=[]; rows_anchor=[]; rows_reg=[]
    rows_place=[]; rows_off=[]; rows_bid=[]; rows_out=[]; rows_fmin=[]
    OFFS=OFFSETS
    for gi,tk in enumerate(keys):
        b,e=begins[gi],ends[gi]
        ttm=ttm_all[b:e]; trig=trig_all[b:e]   # sorted ttm desc
        cat,anchor,reg=meta[tk]
        ev=tk.rsplit("-",1)[0]
        bids=np.maximum(anchor-OFFS,1)          # (7,)
        for P in PLACEMENTS:
            w=ttm<=P                            # window mask (contiguous tail since desc)
            tw=trig[w]; ttmw=ttm[w]
            if tw.size==0:
                for oi,off in enumerate(OFFS.tolist()):
                    rows_ticker.append(tk);rows_event.append(ev);rows_cat.append(cat);rows_anchor.append(anchor);rows_reg.append(reg)
                    rows_place.append(P);rows_off.append(off);rows_bid.append(int(bids[oi]));rows_out.append("missed");rows_fmin.append(None)
                continue
            mask=tw[:,None]<=bids[None,:]       # (W,7)
            anyfill=mask.any(axis=0)
            firstidx=mask.argmax(axis=0)        # first True per offset (0 if none, guarded by anyfill)
            for oi,off in enumerate(OFFS.tolist()):
                rows_ticker.append(tk);rows_event.append(ev);rows_cat.append(cat);rows_anchor.append(anchor);rows_reg.append(reg)
                rows_place.append(P);rows_off.append(off);rows_bid.append(int(bids[oi]))
                if anyfill[oi]:
                    rows_out.append("filled");rows_fmin.append(int(ttmw[firstidx[oi]]))
                else:
                    rows_out.append("missed");rows_fmin.append(None)
    out=pd.DataFrame({"ticker":rows_ticker,"event_ticker":rows_event,"category":rows_cat,
        "anchor_price_cents":rows_anchor,"anchor_regime":rows_reg,"placement_minute":rows_place,
        "bid_offset_cents":rows_off,"bid_price_cents":rows_bid,"fill_outcome":rows_out,"fill_minute":rows_fmin})
    print(f"per-N rows: {len(out)}  rss={rss_mb():.0f}MB",flush=True)
    OUT_N.parent.mkdir(parents=True,exist_ok=True)
    pq.write_table(pa.Table.from_pandas(out,preserve_index=False),OUT_N,compression="snappy")

    # ---- aggregation ----
    out["filled"]=(out.fill_outcome=="filled")
    g=out.groupby(["category","anchor_regime","placement_minute","bid_offset_cents"],observed=True)
    agg=g.agg(n_tickers_in_stratum=("filled","size"),fill_rate=("filled","mean"),
              mean_fill_minute=("fill_minute","mean"),median_fill_minute=("fill_minute","median")).reset_index()
    agg["expected_improvement_cents"]=agg.fill_rate*agg.bid_offset_cents
    pq.write_table(pa.Table.from_pandas(agg,preserve_index=False),OUT_R,compression="snappy")

    # ---- validation ----
    print("=== VALIDATION ===",flush=True)
    print(f"gate1 per-N rows = {len(out)} (expect 589386: {len(out)==589386})",flush=True)
    print(f"per-category N: {(out.groupby('category').ticker.nunique()).to_dict()}",flush=True)
    print(f"regimes present: {sorted(out.anchor_regime.unique())}",flush=True)
    a=out[(out.placement_minute==240)&(out.bid_offset_cents==1)]
    print("gate3 (P=240,off=1) fill_rate by cat x regime (expect >0.85 most):",flush=True)
    print(a.groupby(['category','anchor_regime'],observed=True).filled.mean().round(2).to_dict(),flush=True)
    z=out[(out.placement_minute==40)&(out.bid_offset_cents==15)]
    print("gate4 (P=40,off=15) fill_rate by cat x regime (expect <0.20 most):",flush=True)
    print(z.groupby(['category','anchor_regime'],observed=True).filled.mean().round(2).to_dict(),flush=True)
    # gate5 monotonic in offset
    mono=0;tot=0
    for _,sub in agg.groupby(["category","anchor_regime","placement_minute"],observed=True):
        s=sub.sort_values("bid_offset_cents").fill_rate.to_numpy()
        tot+=1
        if np.all(np.diff(s)<=1e-9): mono+=1
    print(f"gate5 monotonic-decreasing fill_rate in offset: {mono}/{tot} = {100*mono/tot:.0f}% (expect >=80%)",flush=True)
    print(f"agg rows: {len(agg)}  N_sizeb={OUT_N.stat().st_size} R_sizeb={OUT_R.stat().st_size}",flush=True)
    print(f"wall_clock_s={time.time()-t0:.1f} peak_rss_mb={rss_mb():.0f}",flush=True)
    print("DONE_MARKER",flush=True)

if __name__=="__main__":
    main()
