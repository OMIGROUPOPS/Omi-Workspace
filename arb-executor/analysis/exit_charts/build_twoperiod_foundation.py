"""Two-period foundation (DESCRIPTIVE) on the verified T-4h-vicinity OPEN anchor.
NOT running-mid, NOT eventual close. Three solid categories (ATP_MAIN/WTA_MAIN/ATP_CHALL).
Per cell across the 5-94 spectrum, sand-pooled k+-3 (same as exits), one-vote-per-event:
  Segment-1: open(T-240 vicinity) -> T-20   (premarket drift / maker-laying window)
  Segment-2: T-20 -> scheduled start         (pre-live convergence)
Reports mean d-cents, direction (sign), dispersion (std), event-N per cell, both segments.
Caveats carried: vicinity-open anchor (closest traded print to T-240 in [180,300], not a
crisp tick); legs with no usable open EXCLUDED + counted; per-segment endpoint coverage
reported (legs lacking a T-20 or start print excluded from that segment, counted).
No band config, no entry rule. Read-only. Outputs foundation_twoperiod_open_{cat}.csv."""
import glob, os
import pandas as pd, numpy as np
PMU = "/root/Omi-Workspace/arb-executor/data/durable/per_minute_universe"
OUT = "/root/Omi-Workspace/arb-executor/analysis/exit_charts"
CATS = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL"]
COLS = ["ticker", "event_ticker", "category", "time_to_match_start_min", "price_close", "minute_has_trade"]
OPEN_W = (180, 300); T20_W = (10, 40); START_W = (1, 12); OPEN_TGT = 240; T20_TGT = 20; START_TGT = 2


def closest_traded(tts, pc, lo, hi, tgt):
    m = (tts >= lo) & (tts <= hi) & np.isfinite(pc) & (pc > 0)
    if not m.any():
        return None
    j = np.argmin(np.abs(tts[m] - tgt))
    return round(float(pc[m][j]) * 100)


for cat in CATS:
    fs = glob.glob(os.path.join(PMU, "per_minute_features_batch_*.parquet"))
    frames = []
    for f in fs:
        try: d = pd.read_parquet(f, columns=COLS, filters=[("category", "==", cat)])
        except Exception: d = pd.read_parquet(f); d = d[d.category == cat][COLS]
        if len(d): frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df["ticker"] = df.ticker.astype(str); df["event_ticker"] = df.event_ticker.astype(str)
    df = df.reset_index(drop=True)   # closest-by-tts is order-independent; no sort needed
    tts_a = df.time_to_match_start_min.to_numpy(float)
    pc_a = np.where(np.asarray(df.minute_has_trade.to_numpy(), bool), df.price_close.to_numpy(float), np.nan)
    ev_a = df.event_ticker.to_numpy(); codes = pd.factorize(df.ticker, sort=False)[0]
    legs = []  # (event, open_cell, seg1, seg2)
    n_tk = 0; n_noopen = 0; n_no_t20 = 0; n_no_start = 0
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy(); t = tts_a[ix]; p = pc_a[ix]; n_tk += 1
        po = closest_traded(t, p, OPEN_W[0], OPEN_W[1], OPEN_TGT)
        if po is None or po < 5 or po > 94:
            n_noopen += 1; continue
        p20 = closest_traded(t, p, T20_W[0], T20_W[1], T20_TGT)
        ps = closest_traded(t, p, START_W[0], START_W[1], START_TGT)
        if p20 is None: n_no_t20 += 1
        if ps is None: n_no_start += 1
        seg1 = (p20 - po) if p20 is not None else np.nan
        seg2 = (ps - p20) if (ps is not None and p20 is not None) else np.nan
        legs.append((ev_a[ix][0], po, seg1, seg2))
    L = pd.DataFrame(legs, columns=["event", "ocell", "seg1", "seg2"])
    # one-vote-per-event within each cell: average a cell's legs from the same event
    rows = []
    for c in range(5, 95):
        pool = L[(L.ocell >= c - 3) & (L.ocell <= c + 3)]
        if pool.empty:
            rows.append({"c": c, "seg1_mean_dc": np.nan, "seg1_std": np.nan, "seg1_event_N": 0,
                         "seg2_mean_dc": np.nan, "seg2_std": np.nan, "seg2_event_N": 0, "pooled_event_N": 0})
            continue
        ev = pool.groupby("event").agg(s1=("seg1", "mean"), s2=("seg2", "mean"))
        s1 = ev.s1.dropna(); s2 = ev.s2.dropna()
        rows.append({"c": c,
                     "seg1_mean_dc": round(float(s1.mean()), 2) if len(s1) else np.nan,
                     "seg1_std": round(float(s1.std()), 2) if len(s1) > 1 else np.nan,
                     "seg1_event_N": int(len(s1)),
                     "seg2_mean_dc": round(float(s2.mean()), 2) if len(s2) else np.nan,
                     "seg2_std": round(float(s2.std()), 2) if len(s2) > 1 else np.nan,
                     "seg2_event_N": int(len(s2)),
                     "pooled_event_N": int(ev.shape[0])})
    out = pd.DataFrame(rows)
    path = os.path.join(OUT, "foundation_twoperiod_open_%s.csv" % cat)
    out.to_csv(path, index=False)
    print("\n================ %s ================" % cat)
    print("tickers=%d  anchored=%d  EXCLUDED no-open=%d (%.0f%%)  [seg endpoint misses: no-T20=%d no-start=%d]" % (
        n_tk, n_tk - n_noopen, n_noopen, 100.0 * n_noopen / n_tk, n_no_t20, n_no_start))
    print("wrote", os.path.basename(path))
    # spectrum summary: every-5th cell so it's eyeballable here (full detail in CSV)
    print(" cell | seg1 dc (std,N) open->T20 | seg2 dc (std,N) T20->start")
    for c in range(5, 95, 5):
        r = out[out.c == c].iloc[0]
        print("  c%-3d | %+6.2f (s=%4s N=%4d) | %+6.2f (s=%4s N=%4d)" % (
            c, r.seg1_mean_dc, r.seg1_std, r.seg1_event_N, r.seg2_mean_dc, r.seg2_std, r.seg2_event_N))
    # overall (event-weighted) segment means
    a1 = out.seg1_mean_dc.dropna(); a2 = out.seg2_mean_dc.dropna()
    print("spectrum mean |seg1| dc=%.2f  |seg2| dc=%.2f  (seg2/seg1 magnitude ratio=%.2f)" % (
        a1.abs().mean(), a2.abs().mean(), a2.abs().mean() / a1.abs().mean() if a1.abs().mean() else 0))
