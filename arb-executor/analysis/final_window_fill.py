"""READ-ONLY: ask-1 maker fill opportunity in the final window vs the deep target, per category.
The fallback decision: replacing the T-20m taker CROSS with an ask-1 maker clamp (post_only=True)
needs taker-SELL flow to fill (taker_no_count = sell-yes hitting our top-of-book bid). The taker
fallback instead LIFTS the ask (needs ask liquidity, taker_yes side) and is ~100%.
Windows: W20 = final 20m [T-0..T-20]; W5 = [T-15..T-20] (the ONLY window an ask-1 bid is alive,
since match_start_buffer cancels at T-15m). Compares ask-1 fill (any sell-yes flow) vs deep-target
fill (price_low<=target) vs taker certainty (100%). Corpus = G9/PMU (minute; B25: sub-min ~2.4x)."""
import glob, os
import pandas as pd, numpy as np
PMU="data/durable/per_minute_universe"; POL="docs/policy"
CATS=["ATP_CHALL","WTA_CHALL","ATP_MAIN","WTA_MAIN"]
COLS=["ticker","category","time_to_match_start_min","price_low","yes_ask_close","minute_has_trade",
      "taker_no_count_in_minute","taker_yes_count_in_minute"]
cur={}
for r in pd.read_csv(os.path.join(POL,"entry_table_percell_minrule.csv")).itertuples():
    cur[(r.category,int(r.c))]=int(r.bid_offset_cents)

for cat in CATS:
    fr=[]
    for f in glob.glob(os.path.join(PMU,"per_minute_features_batch_*.parquet")):
        try: d=pd.read_parquet(f,columns=COLS,filters=[("category","==",cat)])
        except Exception:
            d=pd.read_parquet(f); d=d[d.category==cat][COLS]
        if len(d): fr.append(d)
    df=pd.concat(fr,ignore_index=True); df["ticker"]=df.ticker.astype(str)
    n=0; ask1_w20=0; ask1_w5=0; deep_w20=0; deep_w5=0; sell_sz_w5=[]; ask_liq_w5=0
    for tk,g in df.groupby("ticker"):
        t=g.time_to_match_start_min.to_numpy(float); pl=g.price_low.to_numpy(float)
        h=np.asarray(g.minute_has_trade.to_numpy(),bool)
        tno=pd.to_numeric(g.taker_no_count_in_minute,errors="coerce").fillna(0).to_numpy()
        tye=pd.to_numeric(g.taker_yes_count_in_minute,errors="coerce").fillna(0).to_numpy()
        om=(t>=180)&(t<=300)&h&np.isfinite(pl)&(pl>0)
        # anchor from price_low proxy of open (use price at open window)
        if not om.any(): continue
        anchor=round(float(pl[om][np.argmin(np.abs(t[om]-240))])*100)
        if anchor<5 or anchor>94: continue
        off=cur.get((cat,anchor))
        if off is None: continue
        target=anchor-off
        n+=1
        w20=(t>=0)&(t<=20); w5=(t>=15)&(t<=20)
        # ask-1 maker fill opportunity = any taker-SELL flow in window (sell-yes hits our top bid)
        if tno[w20].sum()>0: ask1_w20+=1
        if tno[w5].sum()>0: ask1_w5+=1
        # deep-target fill = price actually printed <= target in window
        if (w20&h&np.isfinite(pl)&(pl>0)).any() and float(pl[w20&h&np.isfinite(pl)&(pl>0)].min()*100)<=target: deep_w20+=1
        m5=w5&h&np.isfinite(pl)&(pl>0)
        if m5.any() and float(pl[m5].min()*100)<=target: deep_w5+=1
        sell_sz_w5.append(tno[w5].sum())
        if tye[w5].sum()>0: ask_liq_w5+=1   # ask-lifting liquidity (taker fallback's flow side)
    if not n: print("\n%s: N=0"%cat); continue
    pct=lambda x:100*x/n
    med_sell=float(np.median([s for s in sell_sz_w5])) if sell_sz_w5 else 0
    print("\n================ %s ================  N=%d" % (cat,n))
    print("  ask-1 MAKER fill-opp (any sell-yes flow): W20[final 20m]=%.0f%%  W5[T20->T15, buffer-live]=%.0f%%" % (pct(ask1_w20),pct(ask1_w5)))
    print("  DEEP-target fill (price_low<=target):     W20=%.0f%%  W5=%.0f%%   (current offsets)" % (pct(deep_w20),pct(deep_w5)))
    print("  TAKER fallback (lift ask): certainty ~100%% where ask liquidity exists; ask-lift flow in W5=%.0f%%" % pct(ask_liq_w5))
    print("  median sell-yes contracts in W5: %.0f  (need >=5 to fill a 5-lot)" % med_sell)
print("\nDECISION: if ask-1 W5 >> deep W5 -> ask-1 catches more in the buffer-live window (replace taker).")
print("          if ask-1 W5 ~ 0 -> book too thin to cross down in 5m -> ask-1 buys nothing; keep taker certainty or accept no-fallback.")
