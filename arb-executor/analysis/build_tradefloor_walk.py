"""READ-ONLY RUN-7 step 1+2: build the trade-print-floor offset table + print-truth walk-requalify.
Step 1: per-cell offset = reach60 of the actual trade-print-floor dip (PMU price_low) in the live
resting window [T-15..T-180] (the reachable, pre-T-15m floor) -- NOT the candle/envelope the _minrule
used. Step 2 (the gate): walk fill% + blended ROC on PRINT-TRUTH (price_low) for tradefloor vs _minrule;
the recalibrated table must LIFT fills over _minrule on print-truth, else flag (do not deploy)."""
import glob, os
import pandas as pd, numpy as np
PMU="data/durable/per_minute_universe"; POL="docs/policy"; EC="analysis/exit_charts"
CATS=["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL"]
OPTF={"ATP_MAIN":"deploy_gated_optima.csv","WTA_MAIN":"deploy_gated_optima_WTA_MAIN.csv",
      "ATP_CHALL":"deploy_gated_optima_ATP_CHALL.csv","WTA_CHALL":"deploy_gated_optima_WTA_CHALL.csv"}
COLS=["ticker","category","time_to_match_start_min","price_low","price_close","minute_has_trade"]
REACH=0.60; CAP=8; FEE=1.0; LIVE=(15,180)

mr=pd.read_csv(os.path.join(POL,"entry_table_percell_minrule.csv"))
minrule={(r.category,int(r.c)):int(r.bid_offset_cents) for r in mr.itertuples()}

# collect live-window print-floor dips per (cat,c)
dips={cat:{} for cat in CATS}
EXIT={}
for cat in CATS:
    EXIT[cat]={int(r.c):float(r.exp_ret_match) for r in pd.read_csv(os.path.join(EC,OPTF[cat])).itertuples()}
    fr=[]
    for f in glob.glob(os.path.join(PMU,"per_minute_features_batch_*.parquet")):
        try: d=pd.read_parquet(f,columns=COLS,filters=[("category","==",cat)])
        except Exception:
            d=pd.read_parquet(f); d=d[d.category==cat][COLS]
        if len(d): fr.append(d)
    df=pd.concat(fr,ignore_index=True); df["ticker"]=df.ticker.astype(str)
    legs=[]
    for tk,g in df.groupby("ticker"):
        t=g.time_to_match_start_min.to_numpy(float); pc=g.price_close.to_numpy(float)
        pl=g.price_low.to_numpy(float); h=np.asarray(g.minute_has_trade.to_numpy(),bool)
        om=(t>=180)&(t<=300)&h&np.isfinite(pc)&(pc>0)
        if not om.any(): continue
        anchor=round(float(pc[om][np.argmin(np.abs(t[om]-240))])*100)
        if anchor<5 or anchor>94: continue
        live=h&np.isfinite(pl)&(pl>0)&(t>=LIVE[0])&(t<=LIVE[1])
        if not live.any(): continue
        dip=anchor-round(float(pl[live].min())*100)
        dips[cat].setdefault(anchor,[]).append(dip)
        legs.append((anchor,dip))
    df.legs=legs  # stash per-cat legs for the walk
    globals().setdefault("_legs",{})[cat]=legs

# build tradefloor offsets
tf={}
for cat in CATS:
    for c in range(5,95):
        d=dips[cat].get(c,[])
        if len(d)>=20:
            tf[(cat,c)]=int(np.clip(round(np.quantile(d,1-REACH)),1,CAP))
        else:
            tf[(cat,c)]=minrule.get((cat,c))  # thin cell: keep minrule

# write the drop-in table (same schema as _minrule, override bid_offset_cents)
out=mr.copy()
out["prev_offset"]=out["bid_offset_cents"]
out["bid_offset_cents"]=[tf.get((r.category,int(r.c)),int(r.bid_offset_cents)) for r in mr.itertuples()]
out["fill_src"]="tradefloor_print_reach60"
out.to_csv(os.path.join(POL,"entry_table_percell_tradefloor.csv"),index=False)
print("WROTE entry_table_percell_tradefloor.csv (%d rows)" % len(out))

# print-truth walk: fill on price_low [15,180]; ROC = (exp_ret + offset)/(anchor-offset), maker-or-skip
def walk(offmap):
    agg={cat:{"n":0,"fill":0,"ret":0.0,"cap":0.0} for cat in CATS}
    for cat in CATS:
        for anchor,dip in _legs[cat]:
            o=offmap.get((cat,anchor)); er=EXIT[cat].get(anchor)
            if o is None or er is None: continue
            a=agg[cat]; a["n"]+=1
            if dip>=o:
                a["fill"]+=1; a["ret"]+=er+o; a["cap"]+=anchor-o
    return agg

A=walk(minrule); B=walk(tf)
print("\nPRINT-TRUTH WALK (fill on actual trade-print floor [T-15..T-180]) -- _minrule vs tradefloor")
print("  %-10s %6s | minrule fill / ROC | tradefloor fill / ROC | fill lift" % ("cat","legs"))
for cat in CATS:
    a=A[cat]; b=B[cat]
    if not a["n"]: continue
    af=100*a["fill"]/a["n"]; bf=100*b["fill"]/b["n"]
    ar=a["ret"]/a["cap"]*100 if a["cap"] else 0; br=b["ret"]/b["cap"]*100 if b["cap"] else 0
    flag="" if bf>=af else "  *** NO LIFT (flag)"
    print("  %-10s %6d |  %4.0f%% / %5.1f%%     |   %4.0f%% / %5.1f%%      |  %+.0fpp%s" % (
        cat,a["n"],af,ar,bf,br,bf-af,flag))
print("\nGATE: tradefloor must lift fill over _minrule on print-truth (else do not deploy the recalibration).")
