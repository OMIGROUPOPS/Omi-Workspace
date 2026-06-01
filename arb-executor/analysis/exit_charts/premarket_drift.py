"""
premarket_drift.py — test the premarket directional-drift hypothesis on the FULL universe.

Thesis: favorites (high cells) drift UP and underdogs (low cells) drift DOWN over T-4h→T-20
(retail piles into the favorite into match start). Probe couldn't resolve it; full N can.

drift = traded price near T-20  −  traded price near T-4h   (cents, + = toward 100)
grouped by STARTING cell-band (price near T-4h). Traded price = price_close on minutes that
actually printed (honest; ~56-72% of minutes are no-trade and are skipped).

Reports per starting-band × category:
  1. mean drift, %up, %down  — does favorite-up / dog-down hold at full N?
  2. OUTCOME SPLIT (the critical one): drift of eventual-WINNERS vs eventual-LOSERS. Favorites
     drifting up even on eventual-LOSERS = tradeable retail overshoot (real edge). Only winners
     drifting up = efficient repricing (already priced in, no free money).
  3. timing: per-band traded-price trajectory across the window — when does drift concentrate?
  4. mirror: per event, underdog-side drift vs favorite-side drift — same matches, drift ≈ −drift?

Usage: python premarket_drift.py --input premarket_tape_v1.parquet [--category ATP_MAIN]
"""
from __future__ import annotations
import argparse
import os
import numpy as np
import pandas as pd
import chart_common as cc

COLS = ["ticker", "event_ticker", "category", "minute_ts", "price_close",
        "time_to_match_start_min", "settlement_value"]
BANDS = cc.BANDS                          # deep-ud 5-20 / slight-ud 21-40 / even 41-60 / slight-fav 61-80 / heavy-fav 81-94
EARLY = (200, 240)                        # "near T-4h"
LATE = (20, 60)                           # "near T-20"


def load(input_path, category):
    files = cc.resolve_input(input_path)
    fr = []
    for f in files:
        try:
            d = pd.read_parquet(f, columns=COLS, filters=[("category", "==", category)] if category else None)
        except Exception:
            d = pd.read_parquet(f)
            if category: d = d[d["category"] == category]
            d = d[COLS]
        fr.append(d)
    df = pd.concat(fr, ignore_index=True)
    if category is not None and (len(df) == 0 or (df["category"] != category).any()):
        df = df[df["category"] == category]
    df = df.sort_values(["ticker", "minute_ts"], kind="stable").reset_index(drop=True)
    return df


def band_of(c):
    for nm, lo, hi in BANDS:
        if lo <= c <= hi:
            return nm
    return "out"


def per_ticker(df):
    """One row per ticker: start price S (near T-4h), end price E (near T-20), drift, band, settle."""
    w = df[df["time_to_match_start_min"].between(20, 240)]
    tr = w[w["price_close"].notna()].copy()           # traded minutes only
    early = tr[tr["time_to_match_start_min"].between(*EARLY)]
    late = tr[tr["time_to_match_start_min"].between(*LATE)]
    S = early.groupby("ticker", observed=True)["price_close"].median()
    E = late.groupby("ticker", observed=True)["price_close"].median()
    first = tr.groupby("ticker", observed=True)["price_close"].first()   # earliest traded (sorted asc)
    last = tr.groupby("ticker", observed=True)["price_close"].last()     # latest traded
    S = S.reindex(first.index).fillna(first)
    E = E.reindex(last.index).fillna(last)
    meta = df.groupby("ticker", observed=True).agg(event=("event_ticker", "first"),
                                                   settle=("settlement_value", "first"))
    t = pd.DataFrame({"S": S, "E": E}).join(meta).dropna(subset=["S", "E"])
    t["drift"] = (t["E"] - t["S"]) * 100.0
    t["start_cell"] = (t["S"] * 100).round().astype(int)
    t = t[t["start_cell"].between(5, 94)]
    t["band"] = t["start_cell"].map(band_of)
    return t


def band_report(t, cat):
    print(f"\n================ {cat} - drift by starting band (n_tickers={len(t)}) ================")
    print(f"{'band':<11} {'N':>4} {'meanD':>7} {'%up':>5} {'%dn':>5} | {'WINNER_D':>8} {'LOSER_D':>8}  verdict")
    rows = []
    for nm, lo, hi in BANDS:
        b = t[t.band == nm]
        if len(b) == 0:
            continue
        win = b[b.settle == 1]; los = b[b.settle == 0]
        wm = win.drift.mean() if len(win) else np.nan
        lm = los.drift.mean() if len(los) else np.nan
        # OVERSHOOT test = does the OUTCOME-CONTRARY group drift in the retail direction?
        #   favorites: retail pushes UP -> overshoot iff favorite-LOSERS still drift up (>+1c).
        #   underdogs: retail pushes DOWN -> overshoot iff underdog-WINNERS still drift down (<-1c).
        # Anything else = efficient repricing (price moved toward the true outcome) = no edge.
        if nm in ("heavy-fav", "slight-fav"):
            v = "OVERSHOOT(losers-up)" if lm > 1 else "repricing"
        elif nm in ("deep-underdog", "slight-underdog"):
            v = "OVERSHOOT(winners-dn)" if wm < -1 else "repricing"
        else:
            v = "-"
        print(f"{nm:<11} {len(b):>4} {b.drift.mean():>+7.2f} {(b.drift>0).mean()*100:>4.0f}% "
              f"{(b.drift<0).mean()*100:>4.0f}% | {wm:>+8.2f} {lm:>+8.2f}  {v}")
        rows.append({"category": cat, "band": nm, "N": len(b), "mean_drift": b.drift.mean(),
                     "pct_up": (b.drift > 0).mean(), "pct_down": (b.drift < 0).mean(),
                     "winner_drift": wm, "loser_drift": lm, "verdict": v})
    return pd.DataFrame(rows)


def timing(df, t, cat):
    w = df[df["time_to_match_start_min"].between(20, 240) & df["price_close"].notna()].copy()
    w = w.merge(t[["band"]], left_on="ticker", right_index=True, how="inner")
    w["tbin"] = (w["time_to_match_start_min"] // 30 * 30).astype(int)
    traj = w.groupby(["band", "tbin"], observed=True)["price_close"].mean().reset_index()
    print(f"  timing - mean traded price by band across window (cents; T-4h~240 -> T-20~20):")
    for nm, lo, hi in BANDS:
        s = traj[traj.band == nm].sort_values("tbin", ascending=False)
        if len(s) < 2:
            continue
        pts = {int(r.tbin): r.price_close * 100 for r in s.itertuples()}
        base = pts[max(pts)]
        # cumulative drift at a few checkpoints from the T-4h baseline
        cps = [c for c in (240, 120, 60, 30) if c in pts]
        traj_str = " ".join(f"T-{c}:{pts[c]-base:+.1f}" for c in cps)
        # concentration: share of total drift in the last 60 min (<=60) vs earlier
        print(f"    {nm:<11} {traj_str}")
    return traj


def mirror(t, cat):
    rows = []
    for ev, g in t.groupby("event", observed=True):
        if len(g) != 2:
            continue
        g = g.sort_values("start_cell")
        lo, hi = g.iloc[0], g.iloc[1]      # lo = underdog side, hi = favorite side
        rows.append((lo.drift, hi.drift))
    if len(rows) < 5:
        print("  mirror: too few paired events"); return
    a = np.array(rows)
    dlo, dhi = a[:, 0], a[:, 1]
    corr = np.corrcoef(dlo, dhi)[0, 1]
    summ = dlo + dhi
    print(f"  mirror ({len(rows)} paired events): corr(underdog-drift, favorite-drift) = {corr:+.2f}  "
          f"| mean(driftA+driftB) = {summ.mean():+.2f}c (0 = perfect mirror) | "
          f"within-2c of mirror: {np.mean(np.abs(summ) <= 2)*100:.0f}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--category", default="ATP_MAIN")
    args = ap.parse_args()
    df = load(args.input, args.category)
    t = per_ticker(df)
    rep = band_report(t, args.category)
    timing(df, t, args.category)
    mirror(t, args.category)
    rep.to_csv(os.path.join(os.path.dirname(__file__), f"premarket_drift_{args.category}.csv"), index=False)


if __name__ == "__main__":
    main()
