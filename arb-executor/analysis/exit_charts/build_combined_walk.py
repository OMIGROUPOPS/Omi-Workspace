"""Per-match walk validation of the COMBINED entry change vs current. Read-only.
Levers: (1) min-rule offsets new_off=min(current, envelope@60), (2) fallback pulled
T-20 -> T-1 (fill window open->T-2, premarket), (3) maker-or-SKIP at the fallback (no
taker cross). vs CURRENT: current offsets, open->T-20 window, maker-or-CROSS (taker on
miss). Realized blended ROC (capital-wt) + fill-rate per cat. EXIT=gated_optima
exp_ret_match (A43 fixed-profit; reach-improvement only helps if exit pays).
Lever-3 caveat: the historical walk assumes STABLE resting (no cancel-churn), so its
fill-rate is the PROJECTED live rate once cancel-churn is fixed (live is 6% today)."""
import glob, os
import pandas as pd, numpy as np
PMU = "/root/Omi-Workspace/arb-executor/data/durable/per_minute_universe"
EC = "/root/Omi-Workspace/arb-executor/analysis/exit_charts"
POL = "/root/Omi-Workspace/arb-executor/docs/policy"
CATS = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]
OPTF = {"ATP_MAIN": "deploy_gated_optima.csv", "WTA_MAIN": "deploy_gated_optima_WTA_MAIN.csv",
        "ATP_CHALL": "deploy_gated_optima_ATP_CHALL.csv", "WTA_CHALL": "deploy_gated_optima_WTA_CHALL.csv"}
COLS = ["ticker", "event_ticker", "category", "time_to_match_start_min", "price_low", "price_close", "minute_has_trade"]
OPEN_W = (180, 300); FEE = 1.0

cur_off = {}; pd.read_csv(os.path.join(POL, "entry_table_percell.csv"))
for r in pd.read_csv(os.path.join(POL, "entry_table_percell.csv")).itertuples():
    cur_off[(r.category, int(r.c))] = int(r.bid_offset_cents)

for cat in CATS:
    EXIT = {int(r.c): float(r.exp_ret_match) for r in pd.read_csv(os.path.join(EC, OPTF[cat])).itertuples()}
    env = {int(r.c): int(r.off_reach60) for r in pd.read_csv(os.path.join(EC, "envelope_offsets_%s.csv" % cat)).itertuples()
           if r.off_reach60 == r.off_reach60}
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
    cur = {"fill": 0, "n": 0, "ret": 0.0, "cap": 0.0, "crossed": 0}
    new = {"fill": 0, "n": 0, "ret": 0.0, "cap": 0.0, "skip": 0}
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy(); t = tts[ix]; pc = pcl[ix]; pl = plow[ix]; h = htr[ix]
        om = (t >= OPEN_W[0]) & (t <= OPEN_W[1]) & h & np.isfinite(pc) & (pc > 0)
        if not om.any(): continue
        j = np.argmin(np.abs(t[om] - 240)); anchor = round(float(pc[om][j]) * 100); ots = float(t[om][j])
        if anchor < 5 or anchor > 94 or anchor not in EXIT: continue
        co = cur_off.get((cat, anchor)); eo = env.get(anchor)
        if co is None or eo is None: continue
        mo = min(co, eo)                     # min-rule offset
        tr = h & np.isfinite(pl) & (pl > 0)
        d20 = tr & (t >= 20) & (t <= ots); d1 = tr & (t >= 2) & (t <= ots)
        dip20 = (anchor - pl[d20].min()) if d20.any() else -1
        dip1 = (anchor - pl[d1].min()) if d1.any() else -1
        er = EXIT[anchor]
        # CURRENT: current offset, T-20 window, maker-or-cross
        cur["n"] += 1
        if dip20 >= co:
            cur["fill"] += 1; cur["ret"] += er + co; cur["cap"] += anchor - co
        else:
            cur["crossed"] += 1; cur["ret"] += er - FEE; cur["cap"] += anchor   # taker at ~anchor, -1c fee
        # NEW: min-rule offset, T-1 window, maker-or-SKIP
        new["n"] += 1
        if dip1 >= mo:
            new["fill"] += 1; new["ret"] += er + mo; new["cap"] += anchor - mo
        else:
            new["skip"] += 1                  # no position, no capital
    def roc(s): return s["ret"] / s["cap"] * 100 if s["cap"] else 0
    print("\n================ %s ================" % cat)
    print("  CURRENT (cur-off, T-20, maker-or-cross): legs=%d fill=%.0f%% crossed=%d  blended_ROC=%.2f%%" % (
        cur["n"], 100 * cur["fill"] / cur["n"], cur["crossed"], roc(cur)))
    print("  NEW (min-off, T-1, maker-or-SKIP)      : legs=%d fill=%.0f%% skipped=%d  blended_ROC=%.2f%%" % (
        new["n"], 100 * new["fill"] / new["n"], new["skip"], roc(new)))
    print("  -> fill-rate %+.0fpp | ROC %+.2fpp | (NEW deploys capital on %d filled vs CURRENT %d filled+%d crossed)" % (
        100 * (new["fill"] - cur["fill"]) / cur["n"], roc(new) - roc(cur), new["fill"], cur["fill"], cur["crossed"]))
