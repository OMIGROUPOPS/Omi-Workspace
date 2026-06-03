"""READ-ONLY Check-2: Slam-specific final-window revert within the MAIN PMU cohort. Slam matches are
KXATPMATCH/KXWTAMATCH (= ATP_MAIN/WTA_MAIN bucket; build_g9 pulled them unfiltered). Isolate the
Slam date-windows (AO ~Jan12-26, RG ~May24-Jun8 2026 -- the windows PMU may cover) vs non-Slam, and
compare the final-window revert. Decides if the maker thesis is profitable on Slams or just fillable."""
import glob, os
import pandas as pd, numpy as np
from datetime import datetime, timezone
PMU="data/durable/per_minute_universe"; EC="analysis/exit_charts"
OPTF={"ATP_MAIN":"deploy_gated_optima.csv","WTA_MAIN":"deploy_gated_optima_WTA_MAIN.csv"}
COLS=["ticker","category","match_start_ts","time_to_match_start_min","price_low","price_close",
      "max_yes_bid_forward_to_settlement","settlement_value","result","minute_has_trade"]
def E(y,mo,d): return datetime(y,mo,d,tzinfo=timezone.utc).timestamp()
WINDOWS=[("AO",E(2026,1,12),E(2026,1,27)),("RG",E(2026,5,24),E(2026,6,9))]
def is_slam(ts):
    return any(lo<=ts<=hi for _,lo,hi in WINDOWS)

for cat in ["ATP_MAIN","WTA_MAIN"]:
    Xb={int(r.c):float(r.X) for r in pd.read_csv(os.path.join(EC,OPTF[cat])).itertuples()}
    fr=[]
    for f in glob.glob(os.path.join(PMU,"per_minute_features_batch_*.parquet")):
        try: d=pd.read_parquet(f,columns=COLS,filters=[("category","==",cat)])
        except Exception:
            d=pd.read_parquet(f); d=d[d.category==cat][COLS]
        if len(d): fr.append(d)
    df=pd.concat(fr,ignore_index=True); df["ticker"]=df.ticker.astype(str)
    mst_all=pd.to_numeric(df.match_start_ts,errors="coerce")
    cov=(datetime.fromtimestamp(mst_all.min(),timezone.utc).date(),datetime.fromtimestamp(mst_all.max(),timezone.utc).date())
    buckets={"SLAM":{"t":0,"rl":0,"n":0},"non-SLAM":{"t":0,"rl":0,"n":0}}
    for tk,g in df.groupby("ticker"):
        t=g.time_to_match_start_min.to_numpy(float); pl=g.price_low.to_numpy(float); pc=g.price_close.to_numpy(float)
        h=np.asarray(g.minute_has_trade.to_numpy(),bool); fwd=pd.to_numeric(g.max_yes_bid_forward_to_settlement,errors="coerce").to_numpy()
        mst=pd.to_numeric(g.match_start_ts,errors="coerce").dropna()
        if not len(mst): continue
        ms=float(mst.iloc[0])
        om=(t>=180)&(t<=300)&h&np.isfinite(pc)&(pc>0)
        if not om.any(): continue
        anchor=round(float(pc[om][np.argmin(np.abs(t[om]-240))])*100)
        if anchor<5 or anchor>94: continue
        fw=(t>=0)&(t<=15)&h&np.isfinite(pl)&(pl>0)
        if not fw.any(): continue
        i=np.where(fw)[0][np.argmin(pl[fw])]; F=round(float(pl[i])*100); X=Xb.get(F)
        if X is None or not np.isfinite(fwd[i]): continue
        sv=pd.to_numeric(g.settlement_value,errors="coerce").to_numpy(); fin=np.isfinite(sv); res=g.result.astype(str).to_numpy()
        if fin.any(): s=float(sv[fin][-1]); s=s*100 if s<=1 else s
        elif (res!="nan").any(): s=100.0 if res[res!="nan"][-1]=="yes" else 0.0
        else: continue
        b=buckets["SLAM" if is_slam(ms) else "non-SLAM"]; b["n"]+=1
        if round(float(fwd[i])*100)>=F+X: b["t"]+=1
        elif s<50: b["rl"]+=1
    print("\n================ %s ================  PMU coverage %s -> %s" % (cat,cov[0],cov[1]))
    for k in ("SLAM","non-SLAM"):
        b=buckets[k]
        if not b["n"]: print("  %-9s N=0 (not covered in PMU window)"%k); continue
        print("  %-9s N=%-5d revert(+X)=%.0f%%  settle-loss=%.0f%%" % (k,b["n"],100*b["t"]/b["n"],100*b["rl"]/b["n"]))
print("\nSlam windows: AO Jan12-27, RG May24-Jun9 2026. If SLAM revert ~ non-SLAM -> Slams behave like MAIN")
print("(deep, ~23%% pick-off). Worse -> lean out. Better -> Slams cleaner despite depth.")
