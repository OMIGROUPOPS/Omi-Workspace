#!/usr/bin/env python3
"""
build_premarket_scope_a_v1.py — corpus-wide atlas premarket dynamics map.

Two descriptive parquets over the atlas universe (14,033 N), T-4h..T-20m:
  (1) per_minute_distributions_v1: per (minute x category x anchor_regime) aggregate stats
  (2) per_event_fingerprint_v1:    per atlas event trajectory summary

DEVIATION #1 (documented, output contract preserved): the drafted prompt said "stream
fv_overlap_join_v1.parquet", but that file is only the FV-window subset (1,293 of 14,033 atlas
tickers). Gate 4 requires exactly 14,033 atlas tickers and gate 5 expects ~5% FV coverage — both
only satisfiable with premarket_tape_v1 as the corpus-wide BASE (all 14,033 atlas N) and
fv_overlap_join_v1 LAYERED on for FV columns (~5% subset). The prompt body itself states "FV stats
populated only for fv_overlap window subset". We build base=tape, FV-layer=join.

DEVIATION #2: gate 2's "~9,400 atlas events" contradicts the committed PAIRING_DIAGNOSTIC.md
(7,825 distinct atlas events = 6,208 paired + 1,617 singleton, summing to 14,033 N). We validate
against 7,825.

Prices (yes_bid/ask/spread/mid/price_close), paired_arb_gap_maker and consumption velocities are
stored 0-1 in the tape; ALL price-like outputs here are in CENTS (x100). Volume/taker_flow/OI are
left in native units. fv_consensus_own / fv_delta_at_last_traded are already in cents.
"""
import json, os, time, resource, gc, datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.compute as pc
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parent.parent.parent
TAPE = REPO / "data/durable/per_minute_universe/premarket_tape_v1.parquet"
JOIN = REPO / "data/durable/per_minute_universe/fv_overlap_join_v1.parquet"
SPIKES = {
    "ATP_MAIN": REPO / "data/durable/spike_volatility_map/atp_main_spike_perN.parquet",
    "WTA_MAIN": REPO / "data/durable/spike_volatility_map/wta_main_spike_perN.parquet",
    "ATP_CHALL": REPO / "data/durable/spike_volatility_map/atp_chall_spike_perN.parquet",
    "WTA_CHALL": REPO / "data/durable/spike_volatility_map/wta_chall_spike_perN.parquet",
}
OUT_DIST = REPO / "data/durable/per_minute_universe/probe/per_minute_distributions_v1_probe.parquet"
OUT_FP = REPO / "data/durable/per_minute_universe/probe/per_event_fingerprint_v1_probe.parquet"

PRICE_COLS = ["yes_bid_close", "yes_ask_close", "spread_close", "mid_close", "price_close",
              "paired_arb_gap_maker", "bid_consumption_velocity", "ask_consumption_velocity"]
TAPE_COLS = ["ticker", "minute_ts", "time_to_match_start_min", "match_start_ts",
             "yes_bid_close", "yes_ask_close", "spread_close", "mid_close", "price_close",
             "volume_in_minute", "taker_flow_in_minute", "paired_arb_gap_maker",
             "bid_consumption_velocity", "ask_consumption_velocity", "open_interest_ffill"]

BANDS = [(5, 14, "r05_14"), (15, 24, "r15_24"), (25, 34, "r25_34"), (35, 44, "r35_44"),
         (45, 54, "r45_54"), (55, 64, "r55_64"), (65, 74, "r65_74"), (75, 84, "r75_84"),
         (85, 94, "r85_94")]
STD_REGIMES = [b[2] for b in BANDS]


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def band_of(cents):
    if cents is None or np.isnan(cents):
        return "r_oob"
    for lo, hi, lab in BANDS:
        if lo <= cents <= hi:
            return lab
    return "r_oob"


def main():
    t0 = time.time()
    # --- atlas universe + per-ticker meta ---
    meta = {}  # ticker -> (category, anchor_cents, anchor_regime)
    cat_counts = {}
    for cat, p in SPIKES.items():
        t = pq.read_table(p, columns=["ticker", "anchor_price"])
        tk = t.column("ticker").to_pylist(); ap = t.column("anchor_price").to_pylist()
        cat_counts[cat] = len(set(tk))
        for k, a in zip(tk, ap):
            c = a * 100.0 if a is not None else np.nan
            meta[k] = (cat, c, band_of(c))
    atlas = set(meta)
    print(f"atlas tickers: {len(atlas)}  per-cat: {cat_counts}", flush=True)

    # --- FV layer (subset) ---
    fvj = pq.read_table(JOIN, columns=["ticker", "minute_ts", "fv_consensus_own", "fv_delta_at_last_traded"]).to_pandas()
    fvj = fvj.set_index(["ticker", "minute_ts"])
    print(f"FV layer rows: {len(fvj)}  rss={rss_mb():.0f}MB", flush=True)

    # --- base: atlas-filtered tape ---
    dset = ds.dataset(TAPE)
    df = dset.scanner(columns=TAPE_COLS, filter=pc.field("ticker").isin(list(atlas))).to_table().to_pandas()
    print(f"atlas tape rows: {len(df)}  distinct tickers: {df.ticker.nunique()}  rss={rss_mb():.0f}MB", flush=True)

    # downcast float64 microstructure cols -> float32 (halves footprint; precision ample for cents stats)
    f32 = ["yes_bid_close", "yes_ask_close", "spread_close", "mid_close", "price_close",
           "volume_in_minute", "taker_flow_in_minute", "paired_arb_gap_maker",
           "bid_consumption_velocity", "ask_consumption_velocity", "open_interest_ffill",
           "time_to_match_start_min"]
    for c in f32:
        if c in df.columns and df[c].dtype == "float64":
            df[c] = df[c].astype("float32")
    df["category"] = df.ticker.map(lambda k: meta[k][0]).astype("category")
    df["anchor_regime"] = df.ticker.map(lambda k: meta[k][2]).astype("category")
    df["event_ticker"] = df.ticker.str.rsplit("-", n=1).str[0]

    # FV layer via index-align assignment (NO full-frame merge copy — the merge was the 1.6GB driver)
    df = df.set_index(["ticker", "minute_ts"])
    df["fv_consensus_own"] = fvj["fv_consensus_own"].astype("float32")
    df["fv_delta_at_last_traded"] = fvj["fv_delta_at_last_traded"].astype("float32")
    df = df.reset_index()
    del fvj; gc.collect()
    # price-like -> cents (in place)
    for c in PRICE_COLS:
        df[c] = (df[c] * 100.0).astype("float32")
    print(f"after fv-align+cents rss={rss_mb():.0f}MB", flush=True)

    # ===== OUTPUT 1: per-minute distributions (standard 9 regimes only) =====
    d1 = df[df.anchor_regime.isin(STD_REGIMES)]
    n_oob = (df.anchor_regime == "r_oob").sum()
    keys = ["time_to_match_start_min", "category", "anchor_regime"]
    gp = d1.groupby(keys, observed=True)
    out = gp.size().rename("n_observations").to_frame()

    def add(col, stats, where_notnull=False, prefix=None):
        pre = prefix or col
        sub = d1.dropna(subset=[col]) if where_notnull else d1
        g = sub.groupby(keys, observed=True)[col]
        for st in stats:
            if isinstance(st, float):
                out[f"{pre}_p{int(round(st*100))}"] = g.quantile(st)
            elif st == "mean":
                out[f"{pre}_mean"] = g.mean()
            elif st == "median":
                out[f"{pre}_median"] = g.median()
            elif st == "std":
                out[f"{pre}_std"] = g.std()

    full = ["mean", "median", 0.10, 0.25, 0.75, 0.90, "std"]
    for c in ["yes_bid_close", "yes_ask_close", "spread_close", "mid_close"]:
        add(c, full)
    out["price_close_available_rate"] = gp["price_close"].apply(lambda s: s.notna().mean())
    add("price_close", ["mean", "median"], where_notnull=True)
    add("volume_in_minute", ["mean", "median", 0.90])
    add("taker_flow_in_minute", ["mean", "median", 0.10, 0.90])
    add("paired_arb_gap_maker", ["mean", "median", 0.10, 0.90, "std"], where_notnull=True)
    add("bid_consumption_velocity", ["mean", 0.10, 0.90, "std"])
    add("ask_consumption_velocity", ["mean", 0.10, 0.90, "std"])
    add("open_interest_ffill", ["mean", "median"], where_notnull=True)
    out["fv_consensus_own_available_rate"] = gp["fv_consensus_own"].apply(lambda s: s.notna().mean())
    add("fv_consensus_own", ["mean", "median"], where_notnull=True)
    out["fv_delta_at_last_traded_available_rate"] = gp["fv_delta_at_last_traded"].apply(lambda s: s.notna().mean())
    add("fv_delta_at_last_traded", ["mean", "median", 0.10, 0.90, "std"], where_notnull=True)

    out = out.reset_index()
    OUT_DIST.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(out, preserve_index=False), OUT_DIST, compression="snappy")
    print(f"per_minute_distributions rows={len(out)} (n_oob rows dropped from strat={n_oob}) rss={rss_mb():.0f}MB", flush=True)

    # ===== OUTPUT 2: per-event fingerprint =====
    # per-leg features
    lg = df.groupby("ticker", observed=True)
    leg = pd.DataFrame(index=sorted(atlas))
    leg["minute_count"] = lg.size()
    leg["trade_minute_count"] = lg["price_close"].apply(lambda s: s.notna().sum())
    leg["total_volume"] = lg["volume_in_minute"].sum()
    leg["mean_spread"] = lg["spread_close"].mean()
    leg["p90_spread"] = lg["spread_close"].quantile(0.90)
    leg["wide_spread_minute_count"] = df.assign(w=df.spread_close > 5).groupby("ticker", observed=True)["w"].sum()
    leg["max_abs_bid_consumption_velocity"] = lg["bid_consumption_velocity"].apply(lambda s: s.abs().max())
    leg["max_abs_ask_consumption_velocity"] = lg["ask_consumption_velocity"].apply(lambda s: s.abs().max())
    idx_t4h = lg["time_to_match_start_min"].idxmax()
    idx_t20m = lg["time_to_match_start_min"].idxmin()
    leg["mid_t4h"] = df.loc[idx_t4h].set_index("ticker")["mid_close"]
    leg["mid_t20m"] = df.loc[idx_t20m].set_index("ticker")["mid_close"]
    leg["mid_drift"] = leg["mid_t20m"] - leg["mid_t4h"]
    leg["fv_coverage_rate"] = lg["fv_consensus_own"].apply(lambda s: s.notna().mean())
    leg["mean_fv_delta_at_last_traded"] = lg["fv_delta_at_last_traded"].mean()
    leg["max_abs_fv_delta_at_last_traded"] = lg["fv_delta_at_last_traded"].apply(lambda s: s.abs().max())
    def burst(s):
        tot = s.sum()
        return (s.nlargest(10).sum() / tot) if tot and tot > 0 else np.nan
    leg["volume_burst_concentration"] = lg["volume_in_minute"].apply(burst)

    # event-level paired distortion (per event_ticker, from its rows)
    ev_gap = df.groupby("event_ticker", observed=True)["paired_arb_gap_maker"]
    gap_max = ev_gap.max(); gap_min = ev_gap.min()
    gap_evt = df.assign(big=df.paired_arb_gap_maker.abs() > 5).groupby("event_ticker", observed=True)["big"].sum()
    ev_fv = df.groupby("event_ticker", observed=True)["fv_consensus_own"].apply(lambda s: s.notna().any())
    ev_match = df.groupby("event_ticker", observed=True)["match_start_ts"].first()

    # assemble per-event
    ev2legs = {}
    for tk in atlas:
        ev2legs.setdefault(tk.rsplit("-", 1)[0], []).append(tk)
    rows = []
    for et, legs in ev2legs.items():
        legs = sorted(legs)
        A = legs[0]; B = legs[1] if len(legs) > 1 else None
        paired = B is not None
        r = {"event_ticker": et, "leg_A_ticker": A, "leg_B_ticker": B,
             "category": meta[A][0], "match_start_ts": ev_match.get(et),
             "is_paired": paired,
             "leg_A_anchor_price": meta[A][1], "leg_A_anchor_regime": meta[A][2],
             "leg_B_anchor_price": (meta[B][1] if paired else np.nan),
             "leg_B_anchor_regime": (meta[B][2] if paired else None)}
        for tag, lk in [("leg_A", A), ("leg_B", B)]:
            if lk is None:
                for f in ["minute_count", "trade_minute_count", "total_volume", "mean_spread", "p90_spread",
                          "wide_spread_minute_count", "max_abs_bid_consumption_velocity",
                          "max_abs_ask_consumption_velocity", "mid_t4h", "mid_t20m", "mid_drift",
                          "fv_coverage_rate", "mean_fv_delta_at_last_traded", "max_abs_fv_delta_at_last_traded",
                          "volume_burst_concentration"]:
                    r[f"{tag}_{f}"] = np.nan
                continue
            lr = leg.loc[lk]
            for f in leg.columns:
                r[f"{tag}_{f}"] = lr[f]
        r["max_paired_arb_gap_maker"] = (gap_max.get(et) if paired else np.nan)
        r["min_paired_arb_gap_maker"] = (gap_min.get(et) if paired else np.nan)
        r["max_abs_paired_arb_gap_maker_minute_count"] = (gap_evt.get(et) if paired else np.nan)
        r["has_fv_coverage"] = bool(ev_fv.get(et, False))
        rows.append(r)
    fp = pd.DataFrame(rows)
    pq.write_table(pa.Table.from_pandas(fp, preserve_index=False), OUT_FP, compression="snappy")

    # ---- validation summary ----
    n_paired = int(fp.is_paired.sum()); n_single = int((~fp.is_paired).sum())
    n_atlas_legs = n_paired * 2 + n_single
    print("=== VALIDATION ===", flush=True)
    print(f"per_minute rows={len(out)}  (max 9*4*220=7920)", flush=True)
    print(f"per_minute categories present: {sorted(out.category.unique())}", flush=True)
    print(f"per_event rows(events)={len(fp)}  paired={n_paired} singleton={n_single}  atlas_N=2*paired+singleton={n_atlas_legs}", flush=True)
    print(f"per_event category split: {fp.category.value_counts().to_dict()}", flush=True)
    # gate3 spot checks
    for cat, reg in [("ATP_MAIN", "r05_14"), ("WTA_MAIN", "r85_94")]:
        cell = out[(out.category == cat) & (out.anchor_regime == reg) & (out.time_to_match_start_min == 20)]
        if len(cell):
            print(f"gate3 {cat} {reg} T-20m yes_bid_close_mean={cell.yes_bid_close_mean.iloc[0]:.2f} (expect in band)", flush=True)
    fv_evt_rate = fp.has_fv_coverage.mean()
    print(f"gate5 has_fv_coverage rate={fv_evt_rate:.4f}", flush=True)
    print(f"per-category FV coverage: {fp.groupby('category').has_fv_coverage.mean().to_dict()}", flush=True)
    print(f"n_oob anchor tickers: {sum(1 for k in meta if meta[k][2]=='r_oob')}", flush=True)
    print(f"dist_size={OUT_DIST.stat().st_size} fp_size={OUT_FP.stat().st_size}", flush=True)
    print(f"wall_clock_s={time.time()-t0:.1f} peak_rss_mb={rss_mb():.0f}", flush=True)
    print("DONE_MARKER", flush=True)


if __name__ == "__main__":
    main()
