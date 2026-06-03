"""Per-cell per-category: validated-config BID DEPTH (offset) vs actual TRADED-PRICE
DOWNWARD travel from the T-4h open anchor — in the open->T-20 window (what the maker
has before the fallback crosses) AND the full open->start window. Resolves the 6% fill:
a maker bid at anchor-offset fills iff downward dip >= offset. Misses cluster where
offset > local period-1 travel (thin/flat cells). If fill_full >> fill_p1, the eager
T-20 fallback is forfeiting period-2 dips. 4 cats, sand-pooled k+-3, one-vote-per-event.
Read-only. Outputs offset_vs_travel_{cat}.csv."""
import glob, os
import pandas as pd, numpy as np
PMU = "/root/Omi-Workspace/arb-executor/data/durable/per_minute_universe"
OUT = "/root/Omi-Workspace/arb-executor/analysis/exit_charts"
POL = "/root/Omi-Workspace/arb-executor/docs/policy"
CATS = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]
COLS = ["ticker", "event_ticker", "category", "time_to_match_start_min", "price_low", "price_close", "minute_has_trade"]
OPEN_W = (180, 300)

# validated-config per-cell offsets
off = {}
ot = pd.read_csv(os.path.join(POL, "entry_table_percell.csv"))
for r in ot.itertuples():
    off[(r.category, int(r.c))] = int(r.bid_offset_cents)


def closest_open(t, pc, htr):
    m = (t >= OPEN_W[0]) & (t <= OPEN_W[1]) & htr & np.isfinite(pc) & (pc > 0)
    if not m.any(): return None, None
    j = np.argmin(np.abs(t[m] - 240))
    return round(float(pc[m][j]) * 100), float(t[m][j])


for cat in CATS:
    fs = glob.glob(os.path.join(PMU, "per_minute_features_batch_*.parquet"))
    fr = []
    for f in fs:
        try: d = pd.read_parquet(f, columns=COLS, filters=[("category", "==", cat)])
        except Exception: d = pd.read_parquet(f); d = d[d.category == cat][COLS]
        if len(d): fr.append(d)
    df = pd.concat(fr, ignore_index=True)
    df["ticker"] = df.ticker.astype(str); df["event_ticker"] = df.event_ticker.astype(str)
    tts = df.time_to_match_start_min.to_numpy(float)
    htr = np.asarray(df.minute_has_trade.to_numpy(), bool)
    plow = (df.price_low.astype(float) * 100).to_numpy()
    pcl = df.price_close.to_numpy(float)
    ev = df.event_ticker.to_numpy(); codes = pd.factorize(df.ticker, sort=False)[0]
    legs = []  # (event, ocell, p1_down, full_down)
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy(); t = tts[ix]; pc = pcl[ix]; pl = plow[ix]; h = htr[ix]
        anchor, ots = closest_open(t, pc, h)
        if anchor is None or anchor < 5 or anchor > 94: continue
        tr = h & np.isfinite(pl) & (pl > 0)
        p1 = tr & (t >= 20) & (t <= ots)     # open -> T-20 (before fallback)
        fu = tr & (t >= 2) & (t <= ots)       # open -> start (full)
        p1_down = (anchor - pl[p1].min()) if p1.any() else np.nan
        fu_down = (anchor - pl[fu].min()) if fu.any() else np.nan
        legs.append((ev[ix][0], anchor, p1_down, fu_down))
    L = pd.DataFrame(legs, columns=["event", "ocell", "p1d", "fud"])
    rows = []
    for c in range(5, 95):
        o = off.get((cat, c))
        pool = L[(L.ocell >= c - 3) & (L.ocell <= c + 3)]
        evg = pool.groupby("event").agg(p1=("p1d", "mean"), fu=("fud", "mean"))
        p1 = evg.p1.dropna(); fu = evg.fu.dropna()
        fp1 = float((p1 >= o).mean()) if (o is not None and len(p1)) else np.nan
        fpf = float((fu >= o).mean()) if (o is not None and len(fu)) else np.nan
        rows.append({"c": c, "offset": o,
                     "p1_downtravel_med": round(float(p1.median()), 1) if len(p1) else np.nan,
                     "full_downtravel_med": round(float(fu.median()), 1) if len(fu) else np.nan,
                     "fill_prob_p1": round(fp1, 3) if fp1 == fp1 else np.nan,
                     "fill_prob_full": round(fpf, 3) if fpf == fpf else np.nan,
                     "event_N": int(len(p1)),
                     "offset_vs_p1travel": ("inside" if (o is not None and len(p1) and o <= p1.median()) else "TOO-DEEP")})
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "offset_vs_travel_%s.csv" % cat), index=False)
    print("\n================ %s ================" % cat)
    print(" cell | off | p1travel_med | fulltravel_med | fill_p1 | fill_full | N | verdict")
    for c in range(5, 95, 5):
        r = out[out.c == c].iloc[0]
        print("  c%-3d | %3s | %5s | %6s | %5s | %6s | %4d | %s" % (
            c, r.offset, r.p1_downtravel_med, r.full_downtravel_med, r.fill_prob_p1, r.fill_prob_full, r.event_N, r.offset_vs_p1travel))
    valid = out.dropna(subset=["fill_prob_p1", "fill_prob_full"])
    toodeep = valid[valid.offset_vs_p1travel == "TOO-DEEP"]
    print("spectrum: mean fill_p1=%.2f  mean fill_full=%.2f  (eager-fallback forfeit = full-p1 = %.2f)" % (
        valid.fill_prob_p1.mean(), valid.fill_prob_full.mean(), valid.fill_prob_full.mean() - valid.fill_prob_p1.mean()))
    print("  cells where offset > p1 travel (TOO-DEEP for period-1): %d/%d  cells:%s" % (
        len(toodeep), len(valid), list(toodeep.c.values)[:30]))
