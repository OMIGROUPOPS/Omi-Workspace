#!/usr/bin/env python3
"""C-ABORT-EVIDENCE: reproduces the ATP_MAIN staircase abort-trigger FP rates from the
committed corpus. READ-ONLY analysis; writes the fills table to docs/policy/ once.

Corpus: data/durable/per_minute_universe/per_minute_features_batch_*.parquet (ATP_MAIN),
        docs/policy/range_final_walk_schedule.json (@3a701ba),
        docs/policy/range_final_ATP_MAIN.csv (@3c2161c, final_target),
        analysis/exit_charts/deploy_gated_optima_full.csv (exit EXIT[cell]),
        docs/policy/entry_table_percell.csv (cur_offset, baseline / cross-check).

Run: cd arb-executor && python3 analysis/exit_charts/abort_validation.py
"""
import os, glob, json
import numpy as np, pandas as pd
PMU="data/durable/per_minute_universe"; EC="analysis/exit_charts"; POL="docs/policy"
COLS=["ticker","category","minute_ts","time_to_match_start_min","match_start_ts",
      "price_close","price_low","trade_count_in_minute","minute_has_trade"]
LIVE=10; NEAR=60; RUNK=30; CAT="ATP_MAIN"
SCH=json.load(open(f"{POL}/range_final_walk_schedule.json")); KN=SCH["knots_min_before_start"]; FR=SCH["depth_fraction_at_knot"]
def frac2(t):
    c=[(k,f) for k,f in zip(KN,FR) if k>=t]; return min(c,key=lambda x:x[0])[1] if c else 0.0
def regime(c):
    lo=((c-5)//10)*10+5; return "r%02d_%02d"%(lo,lo+9)
deep={int(r.c):int(r.final_target) for r in pd.read_csv(f"{POL}/range_final_{CAT}.csv").itertuples()}
EXIT={int(r.c):float(r.exp_ret_match) for r in pd.read_csv(os.path.join(EC,"deploy_gated_optima_full.csv"),comment="#").itertuples()}
cur={int(r.c):int(r.bid_offset_cents) for r in pd.read_csv(f"{POL}/entry_table_percell.csv").itertuples() if r.category==CAT}

frames=[]
for f in glob.glob(os.path.join(PMU,"per_minute_features_batch_*.parquet")):
    try: dd=pd.read_parquet(f,columns=COLS,filters=[("category","==",CAT)])
    except: dd=pd.read_parquet(f); dd=dd[dd.category==CAT][COLS]
    if len(dd): frames.append(dd)
df=pd.concat(frames,ignore_index=True); df["ticker"]=df.ticker.astype(str)
df=df.sort_values(["ticker","minute_ts"],kind="stable").reset_index(drop=True)
pc=(df.price_close.astype(float)*100.0); df["_ff"]=pc.groupby(df.ticker).ffill()
df["_rmid"]=df["_ff"].groupby(df.ticker).transform(lambda s:s.rolling(RUNK,min_periods=3).mean())
tts=df.time_to_match_start_min.to_numpy(float); plo=(df.price_low.astype(float)*100).to_numpy()
tcnt=df.trade_count_in_minute.to_numpy(float); hastr=np.asarray(df.minute_has_trade.to_numpy(),bool)
rmid=df["_rmid"].to_numpy(float); mst=df.match_start_ts.to_numpy(float)
groups=[idx.to_numpy() for _,idx in pd.Series(np.arange(len(df))).groupby(pd.factorize(df.ticker,sort=False)[0])]

placed=0; rows=[]
for ix in groups:
    t=tts[ix];rm=rmid[ix];lo=plo[ix];tc=tcnt[ix];ht=hastr[ix];ms=mst[ix]
    o=np.argsort(-t); t,rm,lo,tc,ht=t[o],rm[o],lo[o],tc[o],ht[o]
    win=(t>=1)&(t<=240)
    if not win.any(): continue
    burst=(tc>=LIVE)&(t<=NEAR); onset=t[burst].max() if burst.any() else -1e9
    pj=None
    for j in range(len(t)):
        if t[j]<=240 and t[j]>onset and np.isfinite(rm[j]) and rm[j]>0: pj=j; break
    if pj is None: continue
    cell=int(np.clip(round(rm[pj]),5,94)); anchor=round(rm[pj])
    if cell not in deep or cell not in EXIT: continue
    placed+=1; dt=deep[cell]; fo=None
    for k in range(pj,len(t)):
        if t[k]<=onset: break
        D=max(1,int(round(1+(dt-1)*frac2(t[k]))))   # anchor-1 floor: D>=1 (SIM-ONLY invariant)
        if ht[k] and np.isfinite(lo[k]) and lo[k]<=anchor-D: fo=D; break
    if fo is not None:
        rows.append({"ticker_idx":int(ix[0]),"cell":cell,"regime":regime(cell),"anchor":anchor,
                     "offset":fo,"match_start_ts":float(ms[0]) if len(ms) else 0.0,
                     "exit_er":EXIT[cell],"mk_ret":EXIT[cell]+fo,"mk_cap":anchor-fo})
F=pd.DataFrame(rows).sort_values("match_start_ts").reset_index(drop=True)
OUT=f"{POL}/range_final_ATP_MAIN_abort_fills.csv"; F.to_csv(OUT,index=False)
import hashlib
fsha=hashlib.sha256(open(OUT,"rb").read()).hexdigest()

# ---- (1) CORPUS IDENTITY ----
N_fills=len(F); N_placed=placed; N_win=N_fills-9
fill_rate=100.0*N_fills/N_placed
print("=== (1) CORPUS IDENTITY ===")
print(f"  placed (engagement attempts) = {N_placed}")
print(f"  fills (fills table N)        = {N_fills}   [the 3,595]")
print(f"  rolling-10 windows           = {N_win}     [= N_fills - 9 = the 3,586]")
print(f"  fills table: {OUT}  content-sha256={fsha}")

# ---- (3) PER-REGIME EXPECTED-OFFSET + derivation rule + cur_offset cross-check ----
print("\n=== (3) PER-REGIME EXPECTED-OFFSET ===")
print("  RULE: expected[regime] = median(realized fill_offset over validation fills whose placement-cell falls in the regime 10c bin).")
regmed=F.groupby("regime").offset.median()
curmed={rg: np.median([cur[c] for c in range(5,95) if regime(c)==rg and c in cur]) for rg in regmed.index}
print(f"  {'regime':>8} {'expected(fill_off med)':>22} {'cross-check median(cur_offset)':>30}")
for rg in sorted(regmed.index):
    print(f"  {rg:>8} {regmed[rg]:>22.1f} {curmed[rg]:>30.1f}")
F["exp"]=F.regime.map(regmed); F["resid"]=F.offset-F.exp

# ---- (2)+ reproduce all FP rates ----
r=F.resid.to_numpy()
print("\n=== TRIGGER 1 (one-sided shallow, >=3-of-10 fills residual < -1c) ===")
cnt=sum(1 for i in range(0,N_win) if ((r[i:i+10] < -1).sum()>=3))
print(f"  validation FP = {cnt}/{N_win} = {100*cnt/N_win:.1f}%")

print("\n=== (4) ROLLING-10 ROC METHODOLOGY + TRIGGER 3 ===")
print("  method: per-FILL (filled legs only), chronological by match_start_ts, STRIDE 1 (overlapping),")
print("          SIMPLE capital-weighted ROC = sum(mk_ret)/sum(mk_cap) over each 10-fill window (NOT compounded).")
roll=np.array([F.mk_ret.iloc[i:i+10].sum()/F.mk_cap.iloc[i:i+10].sum()*100 for i in range(0,N_win)])
neg=(roll<0).sum()
print(f"  rolling-10-fill ROC: mean={roll.mean():.2f} sd={roll.std():.2f} min={roll.min():.2f} max={roll.max():.2f}")
print(f"  TRIGGER 3 (rolling-10-fill ROC < 0): validation FP = {neg}/{N_win} = {100*neg/N_win:.1f}%")

print("\n=== (5) FILL-RATE (point-estimate, denominator = engagement attempts) ===")
print(f"  rate = fills / attempts = {N_fills}/{N_placed} = {fill_rate:.1f}%")
print(f"  BAR = {fill_rate:.1f}% - 10pp = {fill_rate-10:.1f}%  (point-estimate; NO bootstrap CI in the bar)")
print(f"  live: over first 10 engagement attempts (first nonzero attempt = t=0), fills/10 < {(fill_rate-10)/10:.2f} -> abort")

print("\n=== (6) ANCHOR-1 FLOOR CODE-POINTER (HONEST) ===")
print("  Validation enforces offset>=1 (bid<=anchor-1) ONLY in this script: D=max(1,...) above.")
print("  LIVE: NO offset>=anchor-1 invariant exists. _reprice_target (live_v4.py:3166) / _fallback_order")
print("  (live_v4.py:3175) clamp to max(1, best_ask-1) -- a PRICE floor (ask-1), NOT an anchor-relative floor.")
print("  => a code path CAN place shallower than anchor-1 (at ask-1) when ask > anchor.")
print("  => Trigger-1 0% FP + degenerate-band (r05_14/r65_74) immunity are CONDITIONAL on the eventual")
print("     staircase deploy adding an explicit offset>=1 (bid<=anchor-1) clamp. live_v4.py blob @HEAD: PIN_BELOW")
print("[done]")
