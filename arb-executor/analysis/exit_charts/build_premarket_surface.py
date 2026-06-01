"""
build_premarket_surface.py — PREMARKET MOVEMENT SURFACE (entry analog of the
locked exit reach surface). Re-presents per_minute_features (T37, sha 9fde4b5d)
through the IDENTICAL exit-surface discipline. DESCRIPTIVE — no fill-floor, no
deploy rule imposed; lays out the dip/spike envelopes per cost-basis cell so it
renders as a pyramid next to the exit one.

DISCIPLINE (identical to chart_common / build_chart_pooled_gauge):
  Instrument: honest TRADED prints only — price_low / price_high (NaN on no-trade
    minutes). NEVER yes_bid/yes_ask (phantom on no-trade), NEVER mid.
  Anchor: premarket-close = last real traded price_close BEFORE the book goes
    live, where "live" = T51 VOLUME-ACCELERATION onset (trade_count_in_minute
    burst), NOT a fixed clock (matches reschedule). All movement measured vs THIS.
    Cost-basis cell c0 = round(100 * premarket_close).
  Weighting: MATCH-weighted one-match-one-vote (event dedup; the two sides
    averaged to one vote in [0,1]) + sand-pooled through grain_mass_overlap k±kmax
    neighbor weights (the SAME overlap engine as the exit surface).
  Window: T-4h -> T-1m (time_to_match_start_min in (0,240]); time-binned finer in
    the final hour where dips concentrate.

MEASURES per cell c (5-94):
  Dip envelope (entry reach):  reach_dip(c,D)   = frac of MATCHES whose premarket
    price_low came <= (c0-D)/100 at any premarket minute (ungated, descriptive).
  Spike envelope (sell-side):  reach_spike(c,D) = price_high >= (c0+D)/100.
  Timing fold:  reach_dip by time-bin (does the dip concentrate late, per cell).
  Volume-to-start context:     mean cumulative premarket volume per cell.
  Mirror check:  partner-side dip vs own spike (the yes+no fold).

Usage:
  python build_premarket_surface.py --input '/path/per_minute_features_batch_*.parquet' \
      --category ATP_MAIN [--kmax 3] [--limit-tickers N (sample/probe)] [--suffix _full]
"""
from __future__ import annotations
import argparse, glob, os
import numpy as np
import pandas as pd

import chart_common as cc
import build_chart_sand_overlap as bso

CELL_MIN, CELL_MAX = cc.CELL_MIN, cc.CELL_MAX          # 5..94
LIVE_BURST = 10            # trade_count_in_minute burst = T51 volume-accel onset (LIVE_TRADE_BURST analog)
LIVE_NEAR_START_TTS = 60   # only treat a burst as the live onset within the final hour / post-start (delay-robust, not a fixed exact clock)
WIN_LO, WIN_HI = 1, 240    # premarket window: T-4h (240) -> T-1m (1), in time_to_match_start_min
TIME_BINS = [240, 180, 120, 90, 60, 40, 30, 20, 10, 5, 2, 1]   # minutes-before-start, finer late
DEPTH_MAX = 30

PM_COLUMNS = ["ticker", "event_ticker", "category", "minute_ts",
              "time_to_match_start_min", "price_close", "price_low", "price_high",
              "trade_count_in_minute", "minute_has_trade", "yes_bid_close",
              "volume_in_minute"]


def load_premarket(input_path, category):
    files = cc.resolve_input(input_path)
    frames = []
    for f in files:
        try:
            d = pd.read_parquet(f, columns=PM_COLUMNS,
                                filters=[("category", "==", category)] if category else None)
        except Exception:
            d = pd.read_parquet(f)
            if category:
                d = d[d["category"] == category]
            d = d[[c for c in PM_COLUMNS if c in d.columns]]
        if len(d):
            frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    if category:
        df = df[df["category"] == category].copy()
    for col in ("ticker", "event_ticker"):
        df[col] = df[col].astype(str)
    df = df.sort_values(["ticker", "minute_ts"], kind="stable").reset_index(drop=True)
    # cost-basis cell for the grain-mass overlap weights (same basis as exits: round(100*yes_bid_close))
    cell = np.round(df["yes_bid_close"].to_numpy(dtype=float) * 100.0)
    cell[(cell < CELL_MIN) | (cell > CELL_MAX)] = np.nan
    df["cell"] = cell
    return df


def per_side_envelopes(df):
    """One row per (event_ticker, ticker): anchor cell c0 + dip/spike reach arrays.

    Anchor = last TRADED price_close in the premarket window before the volume-accel
    live onset. Dip reach for depth D = did any premarket minute's TRADED price_low
    come <= (c0-D)/100; dip_first_tts = the largest tts (earliest) at which it did
    (for the timing fold). Spike symmetric on price_high >= (c0+D)/100.
    """
    rows = []
    tts_all = df["time_to_match_start_min"].to_numpy(dtype=float)
    pc = df["price_close"].to_numpy(dtype=float)
    plo = df["price_low"].to_numpy(dtype=float)
    phi = df["price_high"].to_numpy(dtype=float)
    tcnt = df["trade_count_in_minute"].to_numpy(dtype=float)
    hastr_b = np.asarray(df["minute_has_trade"].to_numpy(), dtype=bool)
    vol = df["volume_in_minute"].to_numpy(dtype=float)
    ev = df["event_ticker"].to_numpy()
    tkr = df["ticker"].to_numpy()
    codes = pd.factorize(df["ticker"], sort=False)[0]
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy()
        # slice EVERY per-ticker array by ix once (consistent lengths)
        tts = tts_all[ix]; pcx = pc[ix]; plox = plo[ix]; phix = phi[ix]
        tcntx = tcnt[ix]; hastrx = hastr_b[ix]; volx = vol[ix]; evx = ev[ix]; tkx = tkr[ix]
        # premarket window minutes (T-240 -> T-1m); rows already chronological by minute_ts
        in_win = (tts >= WIN_LO) & (tts <= WIN_HI)
        if not in_win.any():
            continue
        # volume-accel live onset: first burst minute near/after start (delay-robust; tts decreases to start)
        burst = (tcntx >= LIVE_BURST) & (tts <= LIVE_NEAR_START_TTS)
        onset_tts = tts[burst].max() if burst.any() else -1e9
        # premarket sample = window minutes strictly BEFORE the onset (tts > onset_tts)
        pm = in_win & (tts > onset_tts)
        has = pm & hastrx & np.isfinite(pcx)
        if not has.any():
            continue
        # anchor = last traded price_close before live (smallest tts among traded premarket mins)
        anchor_pos = np.where(has)[0][np.argmin(tts[has])]
        c0 = round(pcx[anchor_pos] * 100.0)
        if c0 < CELL_MIN or c0 > CELL_MAX:
            continue
        # traded dips/spikes within the premarket sample (NaN = no trade, skipped)
        lo = plox[pm]; hi = phix[pm]; tt = tts[pm]
        lo_t = tt[np.isfinite(lo)]; lo_v = lo[np.isfinite(lo)] * 100.0
        hi_t = tt[np.isfinite(hi)]; hi_v = hi[np.isfinite(hi)] * 100.0
        dip_first = np.full(DEPTH_MAX + 1, -1.0)   # largest tts (earliest) at which depth D dip occurred
        spk_hit = np.zeros(DEPTH_MAX + 1, dtype=bool)
        for D in range(1, DEPTH_MAX + 1):
            dmask = lo_v <= (c0 - D)
            if dmask.any():
                dip_first[D] = lo_t[dmask].max()
            spk_hit[D] = bool((hi_v >= (c0 + D)).any())
        cum_vol = float(np.nansum(volx[pm]))
        rows.append((evx[0], tkx[0], int(c0), dip_first, spk_hit, cum_vol))
    return rows


def codes_label(df, ix):
    return df["ticker"].to_numpy()[ix][0]


def aggregate(rows, df, kmax):
    """Match-weighted (one vote/match) reach per (c0 cell, depth D), pooled via
    grain-mass overlap. Returns dip surface, spike surface, timing fold."""
    cells, mat, _tot, _ntk = bso.grain_mass_overlap(df)
    cell_idx = {c: i for i, c in enumerate(cells)}
    kpos = {k: bso.OFFSETS.index(k) for k in bso.OFFSETS}

    # group sides by event, within each (event, c0) average sides -> one vote
    from collections import defaultdict
    by_cell_dip = defaultdict(lambda: defaultdict(list))   # cell -> D -> [event votes]
    by_cell_spk = defaultdict(lambda: defaultdict(list))
    by_cell_timing = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # cell->D->bin->[votes]
    by_cell_vol = defaultdict(list)
    # collapse sides to events first
    ev_group = defaultdict(list)
    for ev, tk, c0, dip_first, spk_hit, cvol in rows:
        ev_group[(ev, c0)].append((dip_first, spk_hit, cvol))
    for (ev, c0), sides in ev_group.items():
        for D in range(1, DEPTH_MAX + 1):
            dvote = np.mean([1.0 if s[0][D] >= 0 else 0.0 for s in sides])
            svote = np.mean([1.0 if s[1][D] else 0.0 for s in sides])
            by_cell_dip[c0][D].append(dvote)
            by_cell_spk[c0][D].append(svote)
            for b in TIME_BINS:
                bvote = np.mean([1.0 if (s[0][D] >= b) else 0.0 for s in sides])
                by_cell_timing[c0][D][b].append(bvote)
        by_cell_vol[c0].append(np.mean([s[2] for s in sides]))

    match_N = {c: len(by_cell_vol.get(c, [])) for c in cells}

    def raw_reach(table, c, D):
        v = table.get(c, {}).get(D)
        return float(np.mean(v)) if v else np.nan

    def pooled_match(table, c, D):
        num = den = 0.0
        for k in range(-kmax, kmax + 1):
            nb = c + k
            if c not in cell_idx:
                continue
            w = mat[cell_idx[c], kpos[k]]
            if nb not in match_N or match_N[nb] == 0 or np.isnan(w):
                continue
            r = raw_reach(table, nb, D)
            if np.isnan(r):
                continue
            wn = w * match_N[nb]
            num += wn * r; den += wn
        return (num / den) if den > 0 else np.nan

    def pooled_N(c):
        tot = 0.0
        for k in range(-kmax, kmax + 1):
            nb = c + k
            if c in cell_idx and nb in match_N and not np.isnan(mat[cell_idx[c], kpos[k]]):
                tot += mat[cell_idx[c], kpos[k]] * match_N[nb]
        return round(tot, 1)

    dip_rows, spk_rows, tim_rows = [], [], []
    for c in cells:
        if match_N.get(c, 0) == 0:
            continue
        meanvol = float(np.mean(by_cell_vol[c])) if by_cell_vol.get(c) else np.nan
        for D in range(1, DEPTH_MAX + 1):
            if (c - D) < 0:
                break
            dip_rows.append({"c": c, "D": D, "target_below": c - D,
                             "match_N": match_N[c], "pooled_N": pooled_N(c),
                             "reach_dip_raw": raw_reach(by_cell_dip, c, D),
                             "reach_dip_pooled_match": pooled_match(by_cell_dip, c, D),
                             "mean_premkt_volume": round(meanvol, 1)})
        for D in range(1, DEPTH_MAX + 1):
            if (c + D) > cc.LOCK:
                break
            spk_rows.append({"c": c, "D": D, "target_above": c + D,
                             "match_N": match_N[c], "pooled_N": pooled_N(c),
                             "reach_spike_raw": raw_reach(by_cell_spk, c, D),
                             "reach_spike_pooled_match": pooled_match(by_cell_spk, c, D)})
        for D in (3, 5, 8):                  # timing fold at a few representative depths
            if (c - D) < 0:
                continue
            for b in TIME_BINS:
                v = by_cell_timing.get(c, {}).get(D, {}).get(b)
                tim_rows.append({"c": c, "D": D, "time_bin_min_before_start": b,
                                 "match_N": match_N[c],
                                 "reach_dip_by_time_raw": float(np.mean(v)) if v else np.nan})

    # monotone dip envelope (deeper dip <= shallower dip), per cell
    dip = pd.DataFrame(dip_rows)
    if len(dip):
        dip["reach_dip_pooled_match_mono"] = (dip.sort_values("D")
            .groupby("c")["reach_dip_pooled_match"].cummin())
    return dip, pd.DataFrame(spk_rows), pd.DataFrame(tim_rows), match_N


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--kmax", type=int, default=3)
    ap.add_argument("--limit-tickers", type=int, default=0, help="sample/probe: cap distinct tickers")
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()
    HERE = os.path.dirname(os.path.abspath(__file__))

    df = load_premarket(args.input, args.category)
    if args.limit_tickers:
        keep = list(pd.unique(df["ticker"]))[:args.limit_tickers]
        df = df[df["ticker"].isin(keep)].copy()
    n_tk, n_ev = df.ticker.nunique(), df.event_ticker.nunique()
    print("PREMARKET SURFACE: %s · %s rows · %d tickers · %d events" % (args.category, f"{len(df):,}", n_tk, n_ev))

    rows = per_side_envelopes(df)
    print("anchored sides:", len(rows))
    dip, spk, tim, match_N = aggregate(rows, df, args.kmax)
    s = args.suffix or ("_" + args.category)
    dip.to_csv(os.path.join(HERE, "premarket_dip_surface%s.csv" % s), index=False)
    spk.to_csv(os.path.join(HERE, "premarket_spike_surface%s.csv" % s), index=False)
    tim.to_csv(os.path.join(HERE, "premarket_dip_timing%s.csv" % s), index=False)
    print("wrote premarket_{dip_surface,spike_surface,dip_timing}%s.csv" % s)
    if len(dip):
        # quick shape readout: dip reach at D=3 across the cell range
        d3 = dip[dip.D == 3].sort_values("c")
        print("dip reach (D=3) by cell (match-weighted, pooled):")
        for r in d3.itertuples():
            if int(r.c) % 10 == 0 or int(r.c) in (5, 25, 50, 75, 94):
                print("  c=%2d  reach=%.2f  matchN=%d" % (int(r.c),
                      r.reach_dip_pooled_match if not np.isnan(r.reach_dip_pooled_match) else -1, int(r.match_N)))


if __name__ == "__main__":
    main()
