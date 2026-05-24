#!/usr/bin/env python3
"""
build_path_c_phase1.py — Path C Phase 1: 3-feature drift predictor (Plex Round 7 Tier 1).

Tests whether 3 features observable at T-4h predict drift_reached_bid (did the maker bid's fill
level get reached by T-20m). Pure numpy (no sklearn on VPS): rank-AUC, IRLS logistic, manual CPCV.

SUBSTRATE NOTE (documented): Feature 2 (taker_imbalance over the 30 min BEFORE placement, ttm
[240,270]) is sourced from per_minute_features.parquet, NOT premarket_tape_v1 — the tape is filtered
to ttm [20,240] and has no pre-T-4h data. The before-window is the causally-correct choice for a
T-240 predictor (Plex's "T-4h->T-3.5h" after-window would be look-ahead leakage). Features 1, 3 and
the drift target come from premarket_tape_v1 (all within [20,240]).
"""
import json, time, resource, re, itertools
import numpy as np, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.dataset as ds, pyarrow.compute as pc
REPO="/root/Omi-Workspace/arb-executor"
TAPE=f"{REPO}/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PMF=f"{REPO}/data/durable/per_minute_universe/per_minute_features.parquet"
CSV=f"{REPO}/docs/policy/per_regime_offsets_v1.csv"
V3=f"{REPO}/data/durable/per_minute_universe/path_b_v3_per_n_simulation.parquet"
SPK={"ATP_MAIN":"atp_main","WTA_MAIN":"wta_main","ATP_CHALL":"atp_chall","WTA_CHALL":"wta_chall"}
OUT_F=f"{REPO}/data/durable/per_minute_universe/probe/path_c_phase1_per_n_features_probe.parquet"
OUT_L=f"{REPO}/data/durable/per_minute_universe/probe/path_c_phase1_logistic_results_probe.parquet"
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
MON={"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,"JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"
def parse_date(tk):
    m=re.search(r"-(\d{2})([A-Z]{3})(\d{2})",tk)
    if not m: return pd.NaT
    yy,mon,dd=m.groups()
    try: return pd.Timestamp(2000+int(yy),MON[mon],int(dd))
    except: return pd.NaT
def rankdata(a):
    a=np.asarray(a,float); order=np.argsort(a,kind="mergesort"); r=np.empty(len(a))
    sa=a[order]; i=0
    while i<len(a):
        j=i
        while j+1<len(a) and sa[j+1]==sa[i]: j+=1
        r[order[i:j+1]]=(i+j)/2.0+1; i=j+1
    return r
def auc(y,s):
    y=np.asarray(y); s=np.asarray(s,float)
    n1=y.sum(); n0=len(y)-n1
    if n1==0 or n0==0 or not np.isfinite(s).all():
        if not np.isfinite(s).all(): s=np.nan_to_num(s)
        if n1==0 or n0==0: return np.nan
    r=rankdata(s)
    return (r[y==1].sum()-n1*(n1+1)/2.0)/(n1*n0)
def fit_logit(X,y,l2=1.0,iters=60):
    n,p=X.shape; beta=np.zeros(p)
    for _ in range(iters):
        eta=np.clip(X@beta,-30,30); mu=1/(1+np.exp(-eta)); mu=np.clip(mu,1e-9,1-1e-9)
        W=mu*(1-mu); H=(X.T*W)@X+l2*np.eye(p); g=X.T@(y-mu)-l2*beta
        try: step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError: step=np.linalg.lstsq(H,g,rcond=None)[0]
        beta=beta+step
        if np.max(np.abs(step))<1e-8: break
    try: cov=np.linalg.inv(H)
    except: cov=np.linalg.pinv(H)
    return beta,np.sqrt(np.clip(np.diag(cov),0,None))
def pred(X,beta): return 1/(1+np.exp(-np.clip(X@beta,-30,30)))

def main():
    t0=time.time()
    # atlas + regime + date
    frames=[]
    for cat,s in SPK.items():
        t=pq.read_table(f"{REPO}/data/durable/spike_volatility_map/{s}_spike_perN.parquet",
            columns=["ticker","event_ticker","anchor_price"]).to_pandas(); t["category"]=cat; frames.append(t)
    sp=pd.concat(frames,ignore_index=True)
    sp["anchor_price_cents"]=(sp.anchor_price*100).round().astype(int)
    sp["anchor_regime"]=sp.anchor_price_cents.map(band)
    sp["date"]=sp.ticker.map(parse_date)
    sp["tournament_block"]=sp.date.dt.strftime("%G-W%V")
    sp["holdout"]=sp.date>=pd.Timestamp(2026,3,1)
    atlas=list(sp.ticker)
    # offset CSV -> target_bid
    csv=pd.read_csv(CSV)
    offmap={(r.category,r.anchor_regime):int(r.bid_offset_cents) for _,r in csv.iterrows()}
    sp["bid_offset_cents"]=sp.apply(lambda r:offmap.get((r.category,r.anchor_regime),15),axis=1)
    sp["target_bid_cents"]=np.maximum(sp.anchor_price_cents-sp.bid_offset_cents,1)
    print(f"atlas {len(sp)} rss={rss():.0f}MB",flush=True)

    # premarket_tape: features 1,3 at ttm=240 + drift target over [20,240]
    tp=ds.dataset(TAPE).scanner(columns=["ticker","time_to_match_start_min","yes_ask_close","yes_bid_close",
        "spread_close","price_close","paired_arb_gap_maker"],filter=pc.field("ticker").isin(atlas)).to_table().to_pandas()
    # use the earliest-available row per ticker (max ttm, ~T-4h) so every ticker has a feature value
    idxmax=tp.groupby("ticker").time_to_match_start_min.idxmax()
    at240=tp.loc[idxmax].set_index("ticker")
    f1=(at240.spread_close*100).round()  # initial_spread_cents
    f3=(at240.paired_arb_gap_maker*100)  # paired_arb_gap_cents (NaN for singleton)
    tp["trig"]=np.minimum(np.where(tp.yes_ask_close.isna(),np.inf,tp.yes_ask_close*100),
                          np.where(tp.price_close.isna(),np.inf,tp.price_close*100))
    mintrig=tp.groupby("ticker").trig.min()
    sp=sp.set_index("ticker")
    sp["initial_spread_cents"]=f1.reindex(sp.index)
    sp["paired_arb_gap_cents"]=f3.reindex(sp.index)
    sp["min_trig"]=mintrig.reindex(sp.index)
    sp["drift_reached_bid"]=sp.min_trig<=sp.target_bid_cents
    print(f"tape features done rss={rss():.0f}MB",flush=True)

    # feature 2 from per_minute_features pre-T4h [240,270]
    pm=ds.dataset(PMF).scanner(columns=["ticker","time_to_match_start_min","taker_flow_in_minute"],
        filter=(pc.field("ticker").isin(atlas))&(pc.field("time_to_match_start_min")>=240)&(pc.field("time_to_match_start_min")<=270)).to_table().to_pandas()
    tf=pm.taker_flow_in_minute.values
    pm["nb"]=np.where(tf>0,tf,0.0); pm["ns"]=np.where(tf<0,-tf,0.0)
    g=pm.groupby("ticker").agg(net_buy=("nb","sum"),net_sell=("ns","sum"))
    tot=g.net_buy+g.net_sell
    g["taker_imbalance_30min"]=np.where(tot>0,(g.net_buy-g.net_sell)/tot,0.0)
    g["taker_data_available"]=tot>0
    sp["taker_imbalance_30min"]=g.taker_imbalance_30min.reindex(sp.index).fillna(0.0)
    sp["taker_data_available"]=g.taker_data_available.reindex(sp.index).fillna(False)
    sp=sp.reset_index()
    print(f"feature2 done; taker_data_available rate={sp.taker_data_available.mean():.3f} rss={rss():.0f}MB",flush=True)

    # ---- gate checks early ----
    y=sp.drift_reached_bid.values.astype(int)
    print(f"drift_reached_bid count={y.sum()} (PathB v3 fill target 3,983)",flush=True)

    # ---- univariate SFI: per-feature corpus AUC + per-cell ----
    feats=["initial_spread_cents","taker_imbalance_30min","paired_arb_gap_cents"]
    thr={"initial_spread_cents":(lambda v:v>=5),"taker_imbalance_30min":(lambda v:np.abs(v)>0.15),"paired_arb_gap_cents":(lambda v:v>=5)}
    sfi={}
    for f in feats:
        v=sp[f].values.astype(float)
        mask=np.isfinite(v)
        # for AUC use |taker_imbalance| (signal is magnitude) ; spread/gap raw
        score=np.abs(v) if f=="taker_imbalance_30min" else v
        sfi[f]=auc(y[mask],score[mask])
    print("univariate corpus AUC:",{f:round(sfi[f],4) for f in feats},flush=True)
    # per-cell lift
    cell_rows=[]
    for (cat,reg),gg in sp.groupby(["category","anchor_regime"]):
        yy=gg.drift_reached_bid.values.astype(int); base=yy.mean()
        for f in feats:
            v=gg[f].values.astype(float); m=np.isfinite(v);
            if m.sum()<10 or len(set(yy[m]))<2:
                a=np.nan; lift=np.nan; cond=np.nan
            else:
                score=np.abs(v) if f=="taker_imbalance_30min" else v
                a=auc(yy[m],score[m])
                passmask=thr[f](v)&m
                cond=yy[passmask].mean() if passmask.sum()>0 else np.nan
                lift=cond/base if base>0 else np.nan
            cell_rows.append(dict(category=cat,anchor_regime=reg,feature=f,n=int(m.sum()),base_rate=base,cond_rate=cond,lift=lift,auc=a))
    cells=pd.DataFrame(cell_rows)
    strong=cells[(cells.auc>0.60)&cells.auc.notna()]
    print(f"per-cell AUC>0.60 cells: {len(strong)} of {len(cells)}; by feature: {strong.feature.value_counts().to_dict()}",flush=True)

    # ---- design matrix: 3 standardized feats + cat-regime one-hot + intercept ----
    sp["catreg"]=sp.category+"|"+sp.anchor_regime
    Xfeat=sp[feats].copy()
    Xfeat["paired_arb_gap_cents"]=Xfeat["paired_arb_gap_cents"].fillna(0.0)  # singletons -> 0 (no gap signal)
    Xfeat["initial_spread_cents"]=Xfeat["initial_spread_cents"].fillna(Xfeat["initial_spread_cents"].median())
    mu=Xfeat.mean(); sd=Xfeat.std().replace(0,1); Z=((Xfeat-mu)/sd).fillna(0.0)
    dummies=pd.get_dummies(sp.catreg,prefix="cr",drop_first=True).astype(float)
    Xall=np.column_stack([np.ones(len(sp)),Z.values,dummies.values])
    feat_idx={f:1+i for i,f in enumerate(feats)}  # columns 1..3 are the features
    cpcv_mask=(~sp.holdout).values; hold_mask=sp.holdout.values

    # ---- CPCV on cpcv window ----
    blocks=sp.tournament_block.values
    cw=np.where(cpcv_mask)[0]
    ub=sorted(sp.loc[cpcv_mask,"tournament_block"].unique())
    fold_of={b:(i%8) for i,b in enumerate(ub)}  # round-robin block->fold
    sp_fold=sp.tournament_block.map(fold_of)
    # week index for embargo
    def wkidx(b):
        try: yr,wk=b.split("-W"); return int(yr)*53+int(wk)
        except: return -9999
    wk=sp.tournament_block.map(wkidx).values
    fold_aucs=[]
    for testf in itertools.combinations(range(8),2):
        test_idx=cw[np.isin(sp_fold.values[cw],testf)]
        if len(test_idx)<20: continue
        test_wk=set(wk[test_idx].tolist())
        train_idx=cw[~np.isin(sp_fold.values[cw],testf)]
        # embargo 2 weeks: drop train events within 2 weeks of any test week
        keep=np.array([min(abs(w-tw) for tw in test_wk)>2 for w in wk[train_idx]])
        train_idx=train_idx[keep]
        if len(set(y[train_idx]))<2 or len(set(y[test_idx]))<2: continue
        b,_=fit_logit(Xall[train_idx],y[train_idx].astype(float))
        fold_aucs.append(auc(y[test_idx],pred(Xall[test_idx],b)))
    fold_aucs=np.array([a for a in fold_aucs if np.isfinite(a)])
    cpcv_mean=fold_aucs.mean(); cpcv_std=fold_aucs.std()
    print(f"CPCV folds={len(fold_aucs)} mean_auc={cpcv_mean:.4f} std={cpcv_std:.4f}",flush=True)

    # ---- holdout: train on all cpcv, predict holdout ----
    bH,seH=fit_logit(Xall[cpcv_mask],y[cpcv_mask].astype(float))
    hold_auc=auc(y[hold_mask],pred(Xall[hold_mask],bH))
    print(f"holdout AUC={hold_auc:.4f} (bar 0.62: {hold_auc>0.62})",flush=True)
    # coefficients (feature cols) with CI on the holdout-trained model
    coef_rows=[]
    for f in feats:
        i=feat_idx[f]; c=bH[i]; s=seH[i]
        coef_rows.append(dict(feature=f,coef=c,se=s,ci_lo=c-1.96*s,ci_hi=c+1.96*s,odds_ratio=np.exp(c)))
    print("coefficients (standardized, holdout-trained):",flush=True)
    for r in coef_rows: print(f"  {r['feature']}: coef={r['coef']:.4f} [{r['ci_lo']:.4f},{r['ci_hi']:.4f}] OR={r['odds_ratio']:.3f}",flush=True)
    # permutation importance on holdout
    rng=np.random.default_rng(42); base_h=auc(y[hold_mask],pred(Xall[hold_mask],bH)); perm={}
    for f in feats:
        i=feat_idx[f]; drops=[]
        for _ in range(10):
            Xp=Xall[hold_mask].copy(); Xp[:,i]=rng.permutation(Xp[:,i]); drops.append(base_h-auc(y[hold_mask],pred(Xp,bH)))
        perm[f]=float(np.mean(drops))
    print("permutation importance (AUC drop, holdout):",{f:round(perm[f],4) for f in feats},flush=True)

    # predicted P for all N (holdout-trained model applied to all; for cpcv rows this is in-sample-ish, flagged)
    sp["pred_p_drift"]=pred(Xall,bH)

    # ---- conditional rules vs Path B v3 ----
    v3=pq.read_table(V3,columns=["ticker","realized_pnl_cents","atlas_baseline_realized_pnl_cents","entry_price_cents"]).to_pandas().set_index("ticker")
    j=sp.set_index("ticker").join(v3,how="left")
    base_pnl=j.realized_pnl_cents.sum()*0.1; base_cap=j.entry_price_cents.sum()*0.1
    print(f"v3 reproduce: PnL=${base_pnl:,.0f} cap=${base_cap:,.0f} ROI={100*base_pnl/base_cap:.2f}%",flush=True)
    # Rule A: place (use v3) if >=2/3 thresholds pass; else taker-fallback (atlas baseline entry=anchor)
    passes=( (j.initial_spread_cents>=5).fillna(False).astype(int)
            +(j.taker_imbalance_30min.abs()>0.15).astype(int)
            +(j.paired_arb_gap_cents>=5).fillna(False).astype(int) )
    gateA=passes>=2
    pnlA=np.where(gateA,j.realized_pnl_cents,j.atlas_baseline_realized_pnl_cents)
    capA=np.where(gateA,j.entry_price_cents,j.anchor_price_cents)
    roiA=100*pnlA.sum()/capA.sum()
    gateB=j.pred_p_drift>0.5
    pnlB=np.where(gateB,j.realized_pnl_cents,j.atlas_baseline_realized_pnl_cents)
    capB=np.where(gateB,j.entry_price_cents,j.anchor_price_cents)
    roiB=100*pnlB.sum()/capB.sum()
    print(f"Rule A (>=2/3 gate): place_frac={gateA.mean():.3f} PnL=${pnlA.sum()*0.1:,.0f} ROI={roiA:.2f}% (v3 {100*base_pnl/base_cap:.2f}%)",flush=True)
    print(f"Rule B (P>0.5 gate): place_frac={gateB.mean():.3f} PnL=${pnlB.sum()*0.1:,.0f} ROI={roiB:.2f}%",flush=True)

    # ---- outputs ----
    out1=sp[["ticker","event_ticker","category","anchor_regime","anchor_price_cents","target_bid_cents",
        "drift_reached_bid","initial_spread_cents","taker_imbalance_30min","paired_arb_gap_cents",
        "taker_data_available","tournament_block","holdout","pred_p_drift"]]
    import os; os.makedirs(os.path.dirname(OUT_F),exist_ok=True)
    pq.write_table(pa.Table.from_pandas(out1,preserve_index=False),OUT_F,compression="snappy")
    pq.write_table(pa.Table.from_pandas(sp[["ticker","pred_p_drift"]],preserve_index=False),OUT_L,compression="snappy")
    cells.to_csv("/tmp/path_c_cells.csv",index=False)

    # ---- validation gates ----
    print("=== GATES ===",flush=True)
    print(f"gate1 rows={len(out1)} (14033)",flush=True)
    nondegen=sum(1 for (cat,reg),gg in sp.groupby(["category","anchor_regime"]) if True)
    fvar={f:sum(1 for (cat,reg),gg in sp.groupby(["category","anchor_regime"]) if gg[f].dropna().nunique()>1) for f in feats}
    print(f"gate2 feature non-degeneracy (cells with variance / 36): {fvar}",flush=True)
    print(f"gate3 drift count={y.sum()} vs v3 3983 (within5%: {abs(y.sum()-3983)/3983<=0.05})",flush=True)
    print(f"gate4 holdout AUC={hold_auc:.4f} >0.62: {hold_auc>0.62}",flush=True)
    print(f"gate5 ruleA ROI={roiA:.2f}% ruleB ROI={roiB:.2f}% vs v3 {100*base_pnl/base_cap:.2f}%",flush=True)
    # save metadata for run_summary
    meta=dict(univariate_auc={f:float(sfi[f]) for f in feats},cpcv_mean_auc=float(cpcv_mean),cpcv_std=float(cpcv_std),
        cpcv_folds=int(len(fold_aucs)),holdout_auc=float(hold_auc),coefficients=coef_rows,
        permutation_importance=perm,drift_count=int(y.sum()),taker_data_available_rate=float(sp.taker_data_available.mean()),
        ruleA_roi=float(roiA),ruleB_roi=float(roiB),v3_roi=float(100*base_pnl/base_cap),
        ruleA_place_frac=float(gateA.mean()),ruleB_place_frac=float(gateB.mean()),
        strong_cells=int(len(strong)),feature_variance_cells=fvar)
    json.dump(meta,open("/tmp/path_c_meta.json","w"),indent=2,default=float)
    print(f"wall={time.time()-t0:.1f}s peak_rss={rss():.0f}MB",flush=True)
    print("DONE_MARKER",flush=True)
if __name__=="__main__": main()
