"""READ-ONLY corpus drift (G9/PMU). Per category x favorite/underdog: how far does price drift
between a T-4h anchor and (a) match start, (b) settle -- magnitude + DIRECTION. Plus: WHEN does the
volume happen (pre-match vs final-15m vs in-play). Adjudicates: is pre-match flow a static desert,
or does price drift across cells so flow arrives where we weren't positioned (anchor->start drift)?"""
import glob, os
import pandas as pd, numpy as np
PMU="data/durable/per_minute_universe"
CATS=["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL"]
COLS=["ticker","category","time_to_match_start_min","price_close","settlement_value","result",
      "volume_in_minute","minute_has_trade"]
ANCHOR=(180,300)  # T-3h..T-5h open window

def med(a): return float(np.median(a)) if len(a) else float("nan")

for cat in CATS:
    fr=[]
    for f in glob.glob(os.path.join(PMU,"per_minute_features_batch_*.parquet")):
        try: d=pd.read_parquet(f,columns=COLS,filters=[("category","==",cat)])
        except Exception:
            d=pd.read_parquet(f); d=d[d.category==cat][COLS]
        if len(d): fr.append(d)
    df=pd.concat(fr,ignore_index=True); df["ticker"]=df.ticker.astype(str)
    rows=[]
    vol_pre=vol_f15=vol_inplay=0.0
    for tk,g in df.groupby("ticker"):
        t=g.time_to_match_start_min.to_numpy(float); pc=g.price_close.to_numpy(float)
        h=np.asarray(g.minute_has_trade.to_numpy(),bool); v=g.volume_in_minute.to_numpy(float)
        sv=g.settlement_value.to_numpy(); res=g.result.astype(str).to_numpy()
        om=(t>=ANCHOR[0])&(t<=ANCHOR[1])&h&np.isfinite(pc)&(pc>0)
        if not om.any(): continue
        j=np.argmin(np.abs(t[om]-240)); anchor=round(float(pc[om][j])*100)  # price_close is DOLLARS
        if anchor<5 or anchor>94: continue
        # start price: closest to T-0 from the pre-match side (t in [0,20])
        sm=(t>=0)&(t<=20)&h&np.isfinite(pc)&(pc>0)
        if not sm.any(): continue
        start=round(float(pc[sm][np.argmin(t[sm])])*100)
        # settle (normalize dollars->cents)
        settle=None
        svn=pd.to_numeric(g.settlement_value,errors="coerce").to_numpy(); fin=np.isfinite(svn)
        if fin.any():
            settle=float(svn[fin][-1]); settle = settle*100 if settle<=1.0 else settle
        elif (res!="nan").any():
            r=res[res!="nan"][-1]; settle=100.0 if r=="yes" else (0.0 if r=="no" else None)
        side="fav" if anchor>50 else "dog"
        rows.append((side,anchor,start,start-anchor,(settle-anchor) if settle is not None else np.nan))
        # volume timing buckets
        vol_pre += v[(t>15)&(t<=300)].sum(); vol_f15 += v[(t>=0)&(t<=15)].sum(); vol_inplay += v[t<0].sum()
    R=pd.DataFrame(rows,columns=["side","anchor","start","d_start","d_settle"])
    vt=vol_pre+vol_f15+vol_inplay
    print("\n================ %s ================  N=%d" % (cat,len(R)))
    print("  VOLUME timing: pre-match(T-5h..T-15m)=%.0f%%  final-15m=%.0f%%  in-play(t<0)=%.0f%%" % (
        100*vol_pre/vt if vt else 0,100*vol_f15/vt if vt else 0,100*vol_inplay/vt if vt else 0))
    for side in ("fav","dog"):
        s=R[R.side==side]
        if not len(s): continue
        ds=s.d_start.to_numpy(); ds=ds[np.isfinite(ds)]
        dse=s.d_settle.to_numpy(); dse=dse[np.isfinite(dse)]
        up=100*np.mean(ds>0) if len(ds) else 0; dn=100*np.mean(ds<0) if len(ds) else 0
        ge5=100*np.mean(np.abs(ds)>=5) if len(ds) else 0; ge10=100*np.mean(np.abs(ds)>=10) if len(ds) else 0
        print("  %s (n=%d, anchor med %.0f): drift_to_START med %+.1f  |med|=%.1f  up=%.0f%%/down=%.0f%%  |drift|>=5c:%.0f%%  >=10c:%.0f%%" % (
              side, len(s), med(s.anchor.to_numpy()), med(ds), med(np.abs(ds)), up, dn, ge5, ge10))
        print("        drift_to_SETTLE med %+.1f  |med|=%.1f" % (med(dse), med(np.abs(dse))))
print("\nINVERSE-STRUCTURE TEST: fav should drift UP (toward 100), dog DOWN (toward 0).")
print("DESERT-vs-DRIFT: if |drift_to_start| small + vol pre-match -> static anchor OK (genuine desert).")
print("                 if drift large OR vol in-play -> flow arrives at a drifted cell / in-play (mispositioned).")
