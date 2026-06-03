"""READ-ONLY: quantify the lever-2 fill-window truncation. The combined walk credited a
maker fill if price dipped to the min-rule offset anywhere in t in [2, ots] (open->T-2m).
The LIVE config cancels the unfilled bid at T-15m (match_start_buffer), so it can only fill in
t in [15, ots]. This computes, per category, fill% on the WALK window [2,ots] vs the LIVE
window [15,ots], the truncation (pp + as a share of walk fills), and the blended ROC on each
window. Offsets = the DEPLOYED minrule table. Mirrors build_combined_walk plumbing."""
import glob, os
import pandas as pd, numpy as np
PMU = "/root/Omi-Workspace/arb-executor/data/durable/per_minute_universe"
EC = "/root/Omi-Workspace/arb-executor/analysis/exit_charts"
POL = "/root/Omi-Workspace/arb-executor/docs/policy"
CATS = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]
OPTF = {"ATP_MAIN": "deploy_gated_optima.csv", "WTA_MAIN": "deploy_gated_optima_WTA_MAIN.csv",
        "ATP_CHALL": "deploy_gated_optima_ATP_CHALL.csv", "WTA_CHALL": "deploy_gated_optima_WTA_CHALL.csv"}
COLS = ["ticker", "category", "time_to_match_start_min", "price_low", "price_close", "minute_has_trade"]
OPEN_W = (180, 300); FEE = 1.0
LIVE_CANCEL_MIN = 15   # ENTRY_BUFFER_SEC = 900s
WALK_FLOOR_MIN = 2     # the walk's d1 floor

# deployed minrule offsets per (category, c)
mo_map = {}
mr = pd.read_csv(os.path.join(POL, "entry_table_percell_minrule.csv"))
for r in mr.itertuples():
    mo_map[(r.category, int(r.c))] = int(r.bid_offset_cents)

print("window-truncation: WALK fill window t>=%d  vs  LIVE fill window t>=%d (bid cancelled at T-15m)\n" % (
    WALK_FLOOR_MIN, LIVE_CANCEL_MIN))
print("%-10s %6s %8s %8s %9s %9s %8s %8s" % (
    "CAT", "legs", "fill_WALK", "fill_LIVE", "trunc_pp", "trunc_sh", "ROC_WALK", "ROC_LIVE"))
print("-" * 78)
tot = {"legs": 0, "fw": 0, "fl": 0}
for cat in CATS:
    EXIT = {int(r.c): float(r.exp_ret_match) for r in pd.read_csv(os.path.join(EC, OPTF[cat])).itertuples()}
    fs = glob.glob(os.path.join(PMU, "per_minute_features_batch_*.parquet"))
    fr = []
    for f in fs:
        try: d = pd.read_parquet(f, columns=COLS, filters=[("category", "==", cat)])
        except Exception: d = pd.read_parquet(f); d = d[d.category == cat][COLS]
        if len(d): fr.append(d)
    df = pd.concat(fr, ignore_index=True); df["ticker"] = df.ticker.astype(str)
    tts = df.time_to_match_start_min.to_numpy(float)
    htr = np.asarray(df.minute_has_trade.to_numpy(), bool)
    plow = (df.price_low.astype(float) * 100).to_numpy(); pcl = df.price_close.to_numpy(float)
    codes = pd.factorize(df.ticker, sort=False)[0]
    w = {"n": 0, "fw": 0, "fl": 0, "rw": 0.0, "cw": 0.0, "rl": 0.0, "cl": 0.0}
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy(); t = tts[ix]; pc = pcl[ix]; pl = plow[ix]; h = htr[ix]
        om = (t >= OPEN_W[0]) & (t <= OPEN_W[1]) & h & np.isfinite(pc) & (pc > 0)
        if not om.any(): continue
        j = np.argmin(np.abs(t[om] - 240)); anchor = round(float(pc[om][j]) * 100); ots = float(t[om][j])
        if anchor < 5 or anchor > 94 or anchor not in EXIT: continue
        mo = mo_map.get((cat, anchor))
        if mo is None: continue
        tr = h & np.isfinite(pl) & (pl > 0)
        d_walk = tr & (t >= WALK_FLOOR_MIN) & (t <= ots)
        d_live = tr & (t >= LIVE_CANCEL_MIN) & (t <= ots)
        dip_walk = (anchor - pl[d_walk].min()) if d_walk.any() else -1
        dip_live = (anchor - pl[d_live].min()) if d_live.any() else -1
        er = EXIT[anchor]
        w["n"] += 1
        if dip_walk >= mo:
            w["fw"] += 1; w["rw"] += er + mo; w["cw"] += anchor - mo   # maker-or-skip: capital only on fills
        if dip_live >= mo:
            w["fl"] += 1; w["rl"] += er + mo; w["cl"] += anchor - mo
    n = w["n"] or 1
    fwp = 100 * w["fw"] / n; flp = 100 * w["fl"] / n
    trunc_pp = fwp - flp
    trunc_sh = 100 * (w["fw"] - w["fl"]) / (w["fw"] or 1)   # truncated as share of walk fills
    rocw = w["rw"] / w["cw"] * 100 if w["cw"] else 0
    rocl = w["rl"] / w["cl"] * 100 if w["cl"] else 0
    print("%-10s %6d %7.0f%% %7.0f%% %8.1fpp %7.0f%% %7.2f%% %7.2f%%" % (
        cat, w["n"], fwp, flp, trunc_pp, trunc_sh, rocw, rocl))
    tot["legs"] += w["n"]; tot["fw"] += w["fw"]; tot["fl"] += w["fl"]
print("-" * 78)
TFW = 100 * tot["fw"] / (tot["legs"] or 1); TFL = 100 * tot["fl"] / (tot["legs"] or 1)
print("%-10s %6d %7.0f%% %7.0f%% %8.1fpp %7.0f%%" % (
    "ALL", tot["legs"], TFW, TFL, TFW - TFL, 100 * (tot["fw"] - tot["fl"]) / (tot["fw"] or 1)))
print("\nfill_WALK = the open->T-2m projection (what 69-81%% was measured on)")
print("fill_LIVE = the open->T-15m projection (what to read first-wave against)")
print("trunc_sh  = share of walk-credited fills that live LOSES to the T-15m cancel")
