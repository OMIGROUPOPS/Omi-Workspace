"""
build_premarket_lifecycle_surface.py — PAIRED PREMARKET LIFECYCLE SURFACE.

The entry-side analog of the locked exit reach surface, but 3-AXIS + PAIRED,
because entry is a live minute-to-minute decision on a MIRRORED binary. Re-presents
per_minute_features (T37, sha 9fde4b5d) through the full exit-surface discipline.
DESCRIPTIVE ONLY — no fill-floor, no wait-vs-take rule, no deploy config. Lays out
the joint shape; the rule is written off the surface afterward (as exits were).
Supersedes the single-leg dip surface (ee34c0a7), which measured one leg, one snapshot.

INSTRUMENT + WEIGHTING (identical to chart_common / build_chart_pooled_gauge):
  Honest TRADED prints only: price_low / price_high / price_close (NaN on no-trade
    minutes). BANNED: yes_bid/yes_ask quotes (phantom), mid_close.
  Anchor = eventual premarket-close = last real traded price_close BEFORE the
    volume-acceleration live onset (trade_count_in_minute burst near start, the
    T51 analog; delay-robust, NOT a fixed clock). Cost-basis cell c0=round(100*close).
  Match-weighted: one vote per event (per cell; sides averaged where both land in c0),
    NOT minute-weighted.
  Sand-pooled via the SAME grain_mass_overlap k±3 weights as exits.
  Window: T-4h -> est-start (time_to_match_start_min in (0,240]); time-binned finer late.

THREE AXES, joined, paired:
  Axis 1  cost-basis cell c (5-94).
  Axis 2  time-to-start bin (coarse early, fine late).
  Axis 3  discount/premium-to-close D(t) = round(100*price_close(t)) - c0  (cents;
          negative = discount/cheap-now, positive = premium/rich-now). [HINDSIGHT vs the
          eventual close — correct for the DESCRIPTIVE surface; deployment needs a
          real-time close proxy, the NEXT problem, flagged not solved here.]
  Per (cell x time-bin x discount-bucket):
    occupancy        = frac of matches (present at cell c in that time-bin) whose leg
                       was observed in that discount bucket  (where the lifecycle goes).
    fill_reach       = a maker bid resting at that level fills = forward TRADED price_low
                       <= current price before start  (entry analog of exit reach).
    deepen_frac      = forward price_low goes >=1c BELOW current  (wait pays).
    extra_dip_cents  = mean (current - forward_min_low)  (how much cheaper it gets).

PAIRED / MIRROR layer (premarket_paired_sum_lifecycle):
    paired_yes_bid_sum / paired_mid_sum trajectory by time-bin -> ROOM zones (sum<100,
    a maker bid on the favorable leg keeps the pair profitable) vs HAZARD zones (sum>100,
    the KESMAR/overround guaranteed-loss state). Spread-width lifecycle (own + partner).

CONTEXT columns (for later conditioning, NOT gated): premarket volume-to-minute,
    taker_flow / taker_yes vs taker_no.

Usage:
  python build_premarket_lifecycle_surface.py --input '<glob>' --category ATP_MAIN [--limit-tickers N]
"""
from __future__ import annotations
import argparse, os
import numpy as np
import pandas as pd

import chart_common as cc
import build_chart_sand_overlap as bso

CELL_MIN, CELL_MAX = cc.CELL_MIN, cc.CELL_MAX
LIVE_BURST = 10
LIVE_NEAR_START_TTS = 60
WIN_LO, WIN_HI = 1, 240
# time-to-start bins (lo, hi]; coarse early, fine late. Labeled by hi (minutes-before-start).
TBINS = [(180, 240), (120, 180), (90, 120), (60, 90), (45, 60), (30, 45),
         (20, 30), (15, 20), (10, 15), (7, 10), (5, 7), (3, 5), (2, 3), (1, 2)]
DBUCKET_CLIP = 20    # discount/premium clipped to +-20c (1c buckets)

PM_COLS = ["ticker", "event_ticker", "category", "minute_ts", "time_to_match_start_min",
           "price_close", "price_low", "price_high", "trade_count_in_minute",
           "minute_has_trade", "yes_bid_close", "volume_in_minute",
           "paired_yes_bid_sum", "paired_mid_sum", "spread_close", "partner_spread_close",
           "taker_flow_in_minute", "taker_yes_count_in_minute", "taker_no_count_in_minute"]


def load(input_path, category):
    frames = []
    for f in cc.resolve_input(input_path):
        try:
            d = pd.read_parquet(f, columns=PM_COLS,
                                filters=[("category", "==", category)] if category else None)
        except Exception:
            d = pd.read_parquet(f)
            if category:
                d = d[d["category"] == category]
            d = d[[c for c in PM_COLS if c in d.columns]]
        if len(d):
            frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    if category:
        df = df[df["category"] == category].copy()
    for c in ("ticker", "event_ticker"):
        df[c] = df[c].astype(str)
    df = df.sort_values(["ticker", "minute_ts"], kind="stable").reset_index(drop=True)
    cell = np.round(df["yes_bid_close"].to_numpy(dtype=float) * 100.0)
    cell[(cell < CELL_MIN) | (cell > CELL_MAX)] = np.nan
    df["cell"] = cell                      # for grain_mass_overlap pooling weights (same basis as exits)
    return df


def tbin_label(tts):
    for lo, hi in TBINS:
        if lo < tts <= hi:
            return hi
    return -1


def per_minute_records(df):
    """Per TRADED premarket minute, one record with the joint state + forward stats."""
    tts_a = df["time_to_match_start_min"].to_numpy(float)
    pc = df["price_close"].to_numpy(float); plo = df["price_low"].to_numpy(float)
    tcnt = df["trade_count_in_minute"].to_numpy(float)
    hastr = np.asarray(df["minute_has_trade"].to_numpy(), dtype=bool)
    vol = df["volume_in_minute"].to_numpy(float)
    pys = df["paired_yes_bid_sum"].to_numpy(float); pms = df["paired_mid_sum"].to_numpy(float)
    spr = df["spread_close"].to_numpy(float); pspr = df["partner_spread_close"].to_numpy(float)
    tflow = df["taker_flow_in_minute"].to_numpy(float)
    ev = df["event_ticker"].to_numpy(); tkr = df["ticker"].to_numpy()
    codes = pd.factorize(df["ticker"], sort=False)[0]
    rec = []
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy()
        tts = tts_a[ix]; pcx = pc[ix]; plox = plo[ix]
        in_win = (tts >= WIN_LO) & (tts <= WIN_HI)
        if not in_win.any():
            continue
        burst = (tcnt[ix] >= LIVE_BURST) & (tts <= LIVE_NEAR_START_TTS)
        onset = tts[burst].max() if burst.any() else -1e9
        pm = in_win & (tts > onset)
        has = pm & hastr[ix] & np.isfinite(pcx)
        if not has.any():
            continue
        c0 = round(pcx[np.where(has)[0][np.argmin(tts[has])]] * 100.0)
        if c0 < CELL_MIN or c0 > CELL_MAX:
            continue
        # forward MIN of traded price_low over the remaining premarket window (to start)
        pm_pos = np.where(pm)[0]
        lo_pm = plox[pm_pos]
        rev = np.fmin.accumulate(lo_pm[::-1])[::-1]               # incl[i]=min(low[i..end])
        fwd_min = np.empty_like(rev); fwd_min[:-1] = rev[1:]; fwd_min[-1] = np.nan  # strict-forward
        evx = ev[ix]; tkx = tkr[ix]; volx = vol[ix]; pysx = pys[ix]; pmsx = pms[ix]
        sprx = spr[ix]; psprx = pspr[ix]; tfx = tflow[ix]
        cum = np.nancumsum(np.where(np.isfinite(volx), volx, 0.0))
        for j, p in enumerate(pm_pos):
            if not (hastr[ix][p] and np.isfinite(pcx[p])):
                continue
            cur = round(pcx[p] * 100.0)
            tb = tbin_label(tts[p])
            if tb < 0:
                continue
            fml = fwd_min[j] * 100.0 if np.isfinite(fwd_min[j]) else np.nan
            fill_here = 1.0 if (np.isfinite(fml) and fml <= cur) else 0.0
            deepen = 1.0 if (np.isfinite(fml) and fml <= cur - 1) else 0.0
            extra = (cur - fml) if np.isfinite(fml) else np.nan
            rec.append((evx[p], tkx[p], int(c0), int(tb),
                        int(np.clip(cur - c0, -DBUCKET_CLIP, DBUCKET_CLIP)),
                        fill_here, deepen, extra, float(cum[p]),
                        pysx[p], pmsx[p], sprx[p], psprx[p], tfx[p]))
    cols = ["event", "ticker", "c", "tbin", "dbucket", "fill_here", "deepen",
            "extra_dip", "vol_cum", "paired_yes_bid_sum", "paired_mid_sum",
            "spread_close", "partner_spread_close", "taker_flow"]
    return pd.DataFrame(rec, columns=cols)


def aggregate(rec, df, kmax):
    cells, mat, _t, _n = bso.grain_mass_overlap(df)
    cell_idx = {c: i for i, c in enumerate(cells)}
    kpos = {k: bso.OFFSETS.index(k) for k in bso.OFFSETS}

    # collapse minutes -> one event-state vote (one match one vote)
    ev_state = rec.groupby(["event", "c", "tbin", "dbucket"], observed=True).agg(
        fill=("fill_here", "mean"), deepen=("deepen", "mean"),
        extra=("extra_dip", "mean"), vol=("vol_cum", "mean")).reset_index()
    # present matches per (c, tbin) = distinct events with any traded minute there
    present = ev_state.groupby(["c", "tbin"], observed=True)["event"].nunique().rename("present_N")

    g = ev_state.groupby(["c", "tbin", "dbucket"], observed=True)
    surf = g.agg(occ_N=("event", "nunique"), fill_reach=("fill", "mean"),
                 deepen_frac=("deepen", "mean"), extra_dip=("extra", "mean"),
                 mean_vol=("vol", "mean")).reset_index().merge(present, on=["c", "tbin"])
    surf["occupancy"] = surf["occ_N"] / surf["present_N"]
    surf["match_N"] = surf["occ_N"]

    # pooled match-N per cell + pooled fill_reach/occupancy across cell-neighbors at same (tbin,dbucket)
    Nmatch_cell = ev_state.groupby("c", observed=True)["event"].nunique().to_dict()
    def pooled_N(c):
        return round(sum(mat[cell_idx[c], kpos[k]] * Nmatch_cell.get(c + k, 0)
                         for k in range(-kmax, kmax + 1)
                         if c in cell_idx and not np.isnan(mat[cell_idx[c], kpos[k]])), 1)
    fr = {(r.c, r.tbin, r.dbucket): (r.fill_reach, r.occupancy, r.match_N) for r in surf.itertuples()}
    fpool, opool, pN = [], [], []
    for r in surf.itertuples():
        wf = ws = wo = 0.0
        for k in range(-kmax, kmax + 1):
            nb = r.c + k
            if r.c not in cell_idx:
                continue
            w = mat[cell_idx[r.c], kpos[k]]
            v = fr.get((nb, r.tbin, r.dbucket))
            if v is None or np.isnan(w):
                continue
            wn = w * v[2]
            wf += wn * v[0]; wo += wn * v[1]; ws += wn
        fpool.append(wf / ws if ws > 0 else np.nan)
        opool.append(wo / ws if ws > 0 else np.nan)
        pN.append(pooled_N(r.c))
    surf["fill_reach_pooled"] = fpool
    surf["occupancy_pooled"] = opool
    surf["pooled_N"] = pN
    surf = surf.sort_values(["c", "tbin", "dbucket"]).reset_index(drop=True)

    # paired-sum lifecycle (match-weighted by event within tbin)
    ev_tb = rec.groupby(["event", "tbin"], observed=True).agg(
        pys=("paired_yes_bid_sum", "mean"), pms=("paired_mid_sum", "mean"),
        own_spread=("spread_close", "mean"), partner_spread=("partner_spread_close", "mean"),
        hazard=("paired_yes_bid_sum", lambda s: float(np.mean(np.asarray(s, float) > 1.0)))).reset_index()
    paired = ev_tb.groupby("tbin", observed=True).agg(
        match_N=("event", "nunique"), mean_paired_yes_bid_sum=("pys", "mean"),
        mean_paired_mid_sum=("pms", "mean"), hazard_frac=("hazard", "mean"),
        mean_own_spread=("own_spread", "mean"), mean_partner_spread=("partner_spread", "mean")).reset_index()
    paired = paired.sort_values("tbin", ascending=False).reset_index(drop=True)
    return surf, paired


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--kmax", type=int, default=3)
    ap.add_argument("--limit-tickers", type=int, default=0)
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()
    HERE = os.path.dirname(os.path.abspath(__file__))

    df = load(args.input, args.category)
    if args.limit_tickers:
        df = df[df["ticker"].isin(list(pd.unique(df["ticker"]))[:args.limit_tickers])].copy()
    print("LIFECYCLE: %s · %s rows · %d tickers · %d events"
          % (args.category, f"{len(df):,}", df.ticker.nunique(), df.event_ticker.nunique()))

    rec = per_minute_records(df)
    print("traded premarket minute-records:", f"{len(rec):,}")
    # VALIDATION: mirror check
    pys_mean = float(np.nanmean(df["paired_yes_bid_sum"].to_numpy(float)))
    print("MIRROR check paired_yes_bid_sum mean: %.3f (expect ~0.97)" % pys_mean)

    surf, paired = aggregate(rec, df, args.kmax)
    s = args.suffix or ("_" + args.category)
    surf.to_csv(os.path.join(HERE, "premarket_lifecycle_surface%s.csv" % s), index=False)
    paired.to_csv(os.path.join(HERE, "premarket_paired_sum_lifecycle%s.csv" % s), index=False)
    print("wrote premarket_lifecycle_surface%s.csv (%d states) + premarket_paired_sum_lifecycle%s.csv" % (s, len(surf), s))

    # headline shape: where is the catchable discount? fill_reach at discount buckets by time-bin, mid cells
    mid = surf[(surf.c >= 45) & (surf.c <= 55) & (surf.dbucket <= -2)]
    if len(mid):
        piv = mid.groupby("tbin").agg(fill=("fill_reach_pooled", "mean"), occ=("occupancy", "mean")).sort_index(ascending=False)
        print("mid-cells (c45-55), discount<=-2c — by time-bin (min-before-start):")
        for tb, row in piv.iterrows():
            print("  T-%3dm  fill_reach=%.2f  occupancy=%.2f" % (tb, row["fill"], row["occ"]))
    print("PAIRED-SUM lifecycle (hazard_frac = paired_yes_bid_sum>1.0):")
    for r in paired.itertuples():
        print("  T-%3dm  sum=%.3f  hazard=%.1f%%  matchN=%d" % (int(r.tbin), r.mean_paired_yes_bid_sum, r.hazard_frac * 100, int(r.match_N)))


if __name__ == "__main__":
    main()
