#!/usr/bin/env python3
"""Validate the drift-informed CANDIDATE entry table against the CURRENT T47-derived
table on REALIZED blended ROC, via a timing-aware, running-mid-anchored per-match walk
that models what the live bot (T58) actually does. Deploy-safe, read-only.

Why a new walk: the committed entry_lift_permatch.py is timing-INSENSITIVE (whole-
window dip, premarket-close anchor, regime offset) — it cannot test a TIMING claim,
which is what the drift table mostly encodes. This walk:
  - anchors on the live running-mid at PLACEMENT time (rolling-30min mean of last-
    traded price), exactly as T58 _v4_entry_anchor does;
  - places each leg when tts first <= the cell's placement_minute (per-cell timing,
    as the live loop gates); cell = round(running_mid) at that moment;
  - fills iff a TRADED price_low reaches (anchor - offset) AFTER placement and BEFORE
    the volume live-onset (the resting window);
  - accounts mirror-correct, capital-weighted: filled -> ret=EXIT[cell]+offset on
    cap=anchor-offset; miss -> ret=EXIT[cell] on cap=anchor (taker-at-anchor floor,
    IDENTICAL for both tables so the comparison is fair).
The ONLY thing that differs between the two runs is the (placement_minute, offset)
per cell. Higher Sigma(ret)/Sigma(cap) = better. EXIT[cell] = deploy_gated_optima
exp_ret_match (the locked validated exit).

Run: cd arb-executor && python3 analysis/exit_charts/drift_table_validate.py
"""
import os, glob
import pandas as pd, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POL = os.path.join(ROOT, "docs", "policy")
EC = os.path.join(ROOT, "analysis", "exit_charts")
PMU = os.path.join(ROOT, "data", "durable", "per_minute_universe")
CATS = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]
OPTF = {"ATP_MAIN": "deploy_gated_optima.csv", "WTA_MAIN": "deploy_gated_optima_WTA_MAIN.csv",
        "ATP_CHALL": "deploy_gated_optima_ATP_CHALL.csv", "WTA_CHALL": "deploy_gated_optima_WTA_CHALL.csv"}
COLS = ["ticker", "event_ticker", "category", "minute_ts", "time_to_match_start_min",
        "price_close", "price_low", "trade_count_in_minute", "minute_has_trade"]
LIVE = 10; NEAR = 60; RUNK = 30


def load_table(path):
    t = pd.read_csv(path)
    return {(r.category, int(r.c)): (int(r.placement_minute), int(r.bid_offset_cents))
            for r in t.itertuples()}


def load_cat(cat):
    """Load + prepare one category's per-minute frame ONCE (running-mid precomputed),
    reused for both tables. Returns the numpy arrays + leg index groups."""
    fs = glob.glob(os.path.join(PMU, "per_minute_features_batch_*.parquet"))
    frames = []
    for f in fs:
        try:
            d = pd.read_parquet(f, columns=COLS, filters=[("category", "==", cat)])
        except Exception:
            d = pd.read_parquet(f); d = d[d.category == cat][COLS]
        if len(d):
            frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df["ticker"] = df.ticker.astype(str); df["event_ticker"] = df.event_ticker.astype(str)
    df = df.sort_values(["ticker", "minute_ts"], kind="stable").reset_index(drop=True)
    pc_c = (df.price_close.astype(float) * 100.0)
    df["_pc_ff"] = pc_c.groupby(df.ticker).ffill()
    df["_rmid"] = (df["_pc_ff"].groupby(df.ticker)
                   .transform(lambda s: s.rolling(RUNK, min_periods=3).mean()))
    groups = [idx.to_numpy() for _, idx in pd.Series(np.arange(len(df))).groupby(
        pd.factorize(df.ticker, sort=False)[0])]
    return {
        "tts": df.time_to_match_start_min.to_numpy(float),
        "plo": (df.price_low.astype(float) * 100.0).to_numpy(),
        "tcnt": df.trade_count_in_minute.to_numpy(float),
        "hastr": np.asarray(df.minute_has_trade.to_numpy(), bool),
        "rmid": df["_rmid"].to_numpy(float),
        "ev": df.event_ticker.to_numpy(),
        "groups": groups,
    }


def walk(cat, table, EXIT, P):
    tts = P["tts"]; plo = P["plo"]; tcnt = P["tcnt"]; hastr = P["hastr"]
    rmid = P["rmid"]; ev = P["ev"]
    legs = []
    for ix in P["groups"]:
        t = tts[ix]; rm = rmid[ix]; lo = plo[ix]; tc = tcnt[ix]; ht = hastr[ix]
        order = np.argsort(-t)            # time-forward = tts descending
        t, rm, lo, tc, ht = t[order], rm[order], lo[order], tc[order], ht[order]
        win = (t >= 1) & (t <= 240)
        if not win.any():
            continue
        burst = (tc >= LIVE) & (t <= NEAR); onset = t[burst].max() if burst.any() else -1e9
        # PLACEMENT: first premarket minute (tts desc) with a defined running-mid where
        # tts <= the cell's placement_minute.
        placed = None
        for j in range(len(t)):
            if not (win[j] and t[j] > onset):
                continue
            if not np.isfinite(rm[j]) or rm[j] <= 0:
                continue
            cell = int(np.clip(round(rm[j]), 5, 94))
            row = table.get((cat, cell))
            if row is None:
                continue
            pmin, off = row
            if t[j] <= pmin:
                placed = (j, cell, off, rm[j]); break
        if placed is None:
            continue
        j, cell, off, anchor = placed
        if cell not in EXIT:
            continue
        anchor_c = round(anchor)
        bid = anchor_c - off
        # FILL: traded low after placement (tts < t[j]) and before/at onset reaches bid
        post = (t < t[j]) & (t > onset) & ht & np.isfinite(lo)
        minlow = lo[post].min() if post.any() else 1e9
        filled = minlow <= bid
        er = float(EXIT[cell])
        legs.append((ev[ix][0], cell, float(anchor_c), float(off), bool(filled), er))
    L = pd.DataFrame(legs, columns=["event", "c", "anchor", "off", "filled", "er"])
    if L.empty:
        return None
    L["mk_ret"] = np.where(L.filled, L.er + L.off, L.er)
    L["mk_cap"] = np.where(L.filled, L.anchor - L.off, L.anchor)
    roc = L.mk_ret.sum() / L.mk_cap.sum() * 100
    base = L.er.sum() / L.anchor.sum() * 100
    return {"n_legs": len(L), "n_matches": L.event.nunique(), "fill_rate": L.filled.mean() * 100,
            "avg_off": L.off.mean(), "base_roc": base, "real_roc": roc, "lift": roc - base}


CUR = load_table(os.path.join(POL, "entry_table_percell.csv"))
DRIFT = load_table(os.path.join(POL, "entry_table_drift_candidate.csv"))

print("%-10s | %-32s | %-32s | verdict" % ("category", "CURRENT (T47-derived)", "DRIFT-INFORMED candidate"))
print("%-10s | %-32s | %-32s |" % ("", "fill%  base   real   lift  N", "fill%  base   real   lift  N"))
tot = {"cur": [0.0, 0.0], "drift": [0.0, 0.0]}  # [sum_ret, sum_cap] proxy via roc*... use weighted later
agg = []
for cat in CATS:
    EXIT = {int(r.c): float(r.exp_ret_match) for r in pd.read_csv(os.path.join(EC, OPTF[cat])).itertuples()}
    P = load_cat(cat)                       # load once, reuse for both tables
    rc = walk(cat, CUR, EXIT, P); rd = walk(cat, DRIFT, EXIT, P)
    def fmt(r):
        return "%5.1f %6.2f %6.2f %+5.2f %4d" % (r["fill_rate"], r["base_roc"], r["real_roc"], r["lift"], r["n_legs"])
    verdict = "DRIFT +%.2fpp" % (rd["real_roc"] - rc["real_roc"]) if rd["real_roc"] > rc["real_roc"] \
        else "CURRENT +%.2fpp" % (rc["real_roc"] - rd["real_roc"])
    print("%-10s | %-32s | %-32s | %s" % (cat, fmt(rc), fmt(rd), verdict))
    agg.append((cat, rc, rd))
print("\nrealized blended ROC = Sigma(mk_ret)/Sigma(mk_cap); lift = real - base (taker-at-anchor floor).")
print("Higher real_roc wins. Same leg population + identical accounting; only the table differs.")
