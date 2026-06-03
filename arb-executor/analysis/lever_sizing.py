"""READ-ONLY lever 1+2 sizing (G9/PMU). LEVER 1: rebuild per-cell entry offset on the actual
trade-print floor (price_low = lowest trade print/min) in the LIVE resting window [T-15m..T-180m],
vs the current minrule offset (envelope/candle-low based). offset@reach60 = quantile(dip,0.40),
clip[1,8]. Also compares the floor in [15,180] vs [2,180] to confirm the dip is PRE-T-15m.
LEVER 2: reprice-tracking frequency — simulate reprice triggers at 3/4/5c thresholds over the path."""
import glob, os
import pandas as pd, numpy as np
PMU="data/durable/per_minute_universe"; POL="docs/policy"
CATS={"ATP_MAIN":"atp_main","WTA_MAIN":"wta_main","ATP_CHALL":"atp_chall","WTA_CHALL":"wta_chall"}
COLS=["ticker","category","time_to_match_start_min","price_close","price_low","minute_has_trade"]
REACH=0.60; CAP=8

cur={}
mr=pd.read_csv(os.path.join(POL,"entry_table_percell_minrule.csv"))
for r in mr.itertuples(): cur[(r.category,int(r.c))]=int(r.bid_offset_cents)

def reprice_count(prices, thr):
    if len(prices)<2: return 0
    anchor=prices[0]; n=0
    for p in prices[1:]:
        if abs(p-anchor)>=thr: n+=1; anchor=p
    return n

for cat in CATS:
    fr=[]
    for f in glob.glob(os.path.join(PMU,"per_minute_features_batch_*.parquet")):
        try: d=pd.read_parquet(f,columns=COLS,filters=[("category","==",cat)])
        except Exception:
            d=pd.read_parquet(f); d=d[d.category==cat][COLS]
        if len(d): fr.append(d)
    df=pd.concat(fr,ignore_index=True); df["ticker"]=df.ticker.astype(str)
    dip_by_c={}; dip_full_by_c={}; rc={3:[],4:[],5:[]}
    for tk,g in df.groupby("ticker"):
        t=g.time_to_match_start_min.to_numpy(float); pc=g.price_close.to_numpy(float)
        pl=g.price_low.to_numpy(float); h=np.asarray(g.minute_has_trade.to_numpy(),bool)
        om=(t>=180)&(t<=300)&h&np.isfinite(pc)&(pc>0)
        if not om.any(): continue
        anchor=round(float(pc[om][np.argmin(np.abs(t[om]-240))])*100)
        if anchor<5 or anchor>94: continue
        live=h&np.isfinite(pl)&(pl>0)&(t>=15)&(t<=180)     # live resting window, pre-T-15m
        full=h&np.isfinite(pl)&(pl>0)&(t>=2)&(t<=180)      # incl final 15m
        if live.any():
            dip=anchor-round(float(pl[live].min())*100)
            dip_by_c.setdefault(anchor,[]).append(dip)
        if full.any():
            dipf=anchor-round(float(pl[full].min())*100)
            dip_full_by_c.setdefault(anchor,[]).append(dipf)
        # reprice path: price_close in window, sorted by descending t (chronological)
        pw=h&np.isfinite(pc)&(pc>0)&(t>=15)&(t<=240)
        if pw.sum()>=2:
            order=np.argsort(-t[pw]); seq=(pc[pw][order]*100).round().astype(int).tolist()
            for thr in (3,4,5): rc[thr].append(reprice_count(seq,thr))
    print("\n================ %s ================" % cat)
    print("LEVER 1 — per-cell offset: trade-print-floor(reach60) vs CURRENT minrule")
    print("  cell | n  | newOff(print) | curOff | delta | full[2-180] vs live[15-180] floor-off")
    shifts=[]
    for c in range(10,95,10):
        d=dip_by_c.get(c,[]); df_=dip_full_by_c.get(c,[])
        if len(d)<20:
            print("  c%-3d | %-3d| (n<20)" % (c,len(d))); continue
        newoff=int(np.clip(round(np.quantile(d,1-REACH)),1,CAP))
        fulloff=int(np.clip(round(np.quantile(df_,1-REACH)),1,CAP)) if len(df_)>=20 else None
        co=cur.get((cat,c))
        delta=(newoff-co) if co is not None else None
        if co is not None: shifts.append(newoff-co)
        print("  c%-3d | %-3d| %d            | %s     | %s   | full=%s live=%d" % (
            c,len(d),newoff,co,("%+d"%delta) if delta is not None else "?",fulloff,newoff))
    if shifts:
        print("  -> median offset shift (new - current): %+.1fc  (negative = shallower)" % np.median(shifts))
    print("LEVER 2 — reprice-tracking frequency over [T-15m..T-4h] (mean #reprices/leg):")
    for thr in (3,4,5):
        a=rc[thr]; print("    thr=%dc: mean=%.2f  median=%d  legs>=1 reprice=%.0f%%  (n=%d)" % (
            thr, np.mean(a) if a else 0, int(np.median(a)) if a else 0, 100*np.mean([x>=1 for x in a]) if a else 0, len(a)))
