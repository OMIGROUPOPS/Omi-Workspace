"""READ-ONLY final-window REVERT RATE (the buffer decision). For a hypothetical maker bid living
to T-0: of fills that occur in the final window [T-15..T-0], what fraction trigger their +X exit
(price reverted UP by the gated_optima band = GOOD fill) vs ride to a settle-0 loss (price kept
falling = picked off / BAD fill)? Measured outcome from G9/PMU forward path, per category.
High revert => buffer relaxation is a clean win, pick-off theory dead. Mostly settle-0 => buffer protects."""
import glob, os
import pandas as pd, numpy as np
PMU="data/durable/per_minute_universe"; EC="analysis/exit_charts"
OPTF={"ATP_MAIN":"deploy_gated_optima.csv","WTA_MAIN":"deploy_gated_optima_WTA_MAIN.csv",
      "ATP_CHALL":"deploy_gated_optima_ATP_CHALL.csv","WTA_CHALL":"deploy_gated_optima_WTA_CHALL.csv"}
COLS=["ticker","category","time_to_match_start_min","price_low","price_close",
      "max_yes_bid_forward_to_settlement","settlement_value","result","minute_has_trade"]

for cat in ["ATP_CHALL","WTA_CHALL","ATP_MAIN","WTA_MAIN"]:
    Xb={int(r.c):float(r.X) for r in pd.read_csv(os.path.join(EC,OPTF[cat])).itertuples()}
    fr=[]
    for f in glob.glob(os.path.join(PMU,"per_minute_features_batch_*.parquet")):
        try: d=pd.read_parquet(f,columns=COLS,filters=[("category","==",cat)])
        except Exception:
            d=pd.read_parquet(f); d=d[d.category==cat][COLS]
        if len(d): fr.append(d)
    df=pd.concat(fr,ignore_index=True); df["ticker"]=df.ticker.astype(str)
    trig=0; ride_win=0; ride_loss=0; n=0
    for tk,g in df.groupby("ticker"):
        t=g.time_to_match_start_min.to_numpy(float); pl=g.price_low.to_numpy(float)
        pc=g.price_close.to_numpy(float); h=np.asarray(g.minute_has_trade.to_numpy(),bool)
        fwd=pd.to_numeric(g.max_yes_bid_forward_to_settlement,errors="coerce").to_numpy()
        om=(t>=180)&(t<=300)&h&np.isfinite(pc)&(pc>0)
        if not om.any(): continue
        anchor=round(float(pc[om][np.argmin(np.abs(t[om]-240))])*100)
        if anchor<5 or anchor>94: continue
        fw=(t>=0)&(t<=15)&h&np.isfinite(pl)&(pl>0)        # final-window fill candidates
        if not fw.any(): continue
        i=np.where(fw)[0][np.argmin(pl[fw])]               # deepest dip minute = where a resting bid fills
        F=round(float(pl[i])*100)
        X=Xb.get(F) or Xb.get(min(94,max(5,F)))
        if X is None: continue
        fmax=fwd[i]
        if not np.isfinite(fmax): continue
        fmax=round(float(fmax)*100)
        # settle
        sv=pd.to_numeric(g.settlement_value,errors="coerce").to_numpy(); fin=np.isfinite(sv)
        res=g.result.astype(str).to_numpy()
        if fin.any(): settle=float(sv[fin][-1]); settle=settle*100 if settle<=1 else settle
        elif (res!="nan").any(): r=res[res!="nan"][-1]; settle=100.0 if r=="yes" else 0.0
        else: continue
        n+=1
        if fmax >= F + X: trig+=1                            # +X exit triggers (revert up)
        elif settle>=50: ride_win+=1                         # rode up to settle-win (no +X but won)
        else: ride_loss+=1                                   # rode to settle-0 (picked off)
    if not n: print("\n%s N=0"%cat); continue
    p=lambda x:100*x/n
    print("\n================ %s ================  N=%d  (final-window fills)" % (cat,n))
    print("  REVERT (+X exit triggers, price bounced >=band): %.0f%%" % p(trig))
    print("  rode to settle-WIN (no +X but settled 100):      %.0f%%" % p(ride_win))
    print("  rode to settle-LOSS (picked off, settled 0):     %.0f%%" % p(ride_loss))
    print("  => good (revert + win) %.0f%%  vs  bad (settle-0) %.0f%%" % (p(trig)+p(ride_win), p(ride_loss)))
print("\nDECISION: high REVERT => buffer relaxation clean win (fills bounce to +X), pick-off dead.")
print("          high settle-LOSS => final-window fills are picked off => buffer protects.")
