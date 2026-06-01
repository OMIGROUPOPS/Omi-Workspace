"""
build_chart_entry_fill.py — ENTRY maker-fill surface on the premarket tape (Axis 2).

Entry-side mirror of the locked exit ROC surface. Supersedes the boxy Path B v4.
You rest a maker BUY at cell c during premarket (T-4h → T-20m); it fills only when a REAL
trade prints DOWN to your bid. A maker fill (0 fees, bought at the bid) lands a cost basis
below the taker baseline → lifts the exit ROC on that position.

SOURCE: premarket_tape_v1.parquet (T-4h→T-20m, regime-pure premarket, per-minute, sha ff2a63d9).
Per-minute is sufficient: the premarket moves that fill a resting bid are drawn-out, depth-backed
drifts the minute tape captures cleanly — not sub-second wicks.

HONEST FILL INSTRUMENT (the whole point):
    fill = a real TRADED print at/below the bid, AFTER placement, before T-20m:
           min(forward price_low within ticker) <= bid/100
    NOT yes_ask_close <= bid (quoted ask coming down = a cheaper TAKE, not a maker fill).
    NOT minute-close lag. Only a genuine cross DOWN into the resting bid counts.
    At 10ct sizing a trade at/below the bid = a fill (no depth model needed).

THREE corrections vs old Path B:
  - per-CENT cell (5-94), not regime boxes (r05_14 …).
  - per-MINUTE placement across the window, not coarse bins (240/180/120/90/60/40).
  - honest fill instrument (real traded cross), not the quoted-ask-comes-down phantom.

Cluster-sand-pooled: each cell reads its premarket drift through its cost-basis cluster's
grain-mass overlap weights (same sand as the exit surface) — fill-prob on cluster mass, not
thin own-cell count. One-match-one-vote (event-dedup) like the exit gate.

OUTPUT per cell (deploy_entry_fill_<CAT>.csv) + interactive HTML surface:
  - maker-fill probability (real cross into bid by T-20), placed early & rested the full window
  - base bid at cell c AND conservative variants 1-2c below the cell (fills only on a genuine dip)
  - resulting cost basis when filled (feeds lifted exit ROC)
  - chase-vs-wait read: high fill-prob -> WAIT (rest the cheap maker bid); low -> CHASE taker / PASS
  - (c × placement-minute) heatmap: how fill-prob grows the earlier you place

Usage: python build_chart_entry_fill.py --input premarket_tape_v1.parquet [--category ATP_MAIN]
"""
from __future__ import annotations
import argparse
import os
import numpy as np
import pandas as pd
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

import chart_common as cc
import build_chart_sand_overlap as bso

ENTRY_COLS = ["ticker", "event_ticker", "category", "minute_ts",
              "yes_bid_close", "price_low", "time_to_match_start_min", "settlement_value"]
OFFSETS = (0, 1, 2)            # bid at cell c (0) or 1-2c below (conservative)
T20 = 20                       # premarket window closes at T-20m
WAIT_FLOOR = 0.50              # fill-prob above which "WAIT for the maker fill" beats chasing taker


def load_premarket(input_path: str, category: str = "ATP_MAIN") -> pd.DataFrame:
    files = cc.resolve_input(input_path)
    frames = []
    for f in files:
        try:
            d = pd.read_parquet(f, columns=ENTRY_COLS,
                                filters=[("category", "==", category)] if category else None)
        except Exception:
            d = pd.read_parquet(f)
            if category is not None:
                d = d[d["category"] == category]
            d = d[ENTRY_COLS]
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    if category is not None and (len(df) == 0 or (df["category"] != category).any()):
        df = df[df["category"] == category]
    for col in ("ticker", "event_ticker"):
        df[col] = df[col].astype("category")
    df["price_low"] = df["price_low"].astype("float32")
    df["settlement_value"] = df["settlement_value"].astype("float32")
    df = df.sort_values(["ticker", "minute_ts"], kind="stable").reset_index(drop=True)
    cell = np.round(df["yes_bid_close"].to_numpy(dtype=float) * 100.0)
    cell[(cell < cc.CELL_MIN) | (cell > cc.CELL_MAX)] = np.nan
    df["cell"] = cell
    df["fwd_min_low"] = cc.compute_forward_min(df, "price_low")   # honest maker-fill instrument
    return df


def headline_fill(df: pd.DataFrame) -> pd.DataFrame:
    """Per cell c: place the bid at the FIRST premarket minute price is at c (max wait time),
    rest it to T-20. Fill = a real traded low <= (c-offset) afterwards. One-match-one-vote:
    average the sides' 0/1 fill within each match, then over matches. match_N = distinct matches."""
    sub = df[df["cell"].notna() & df["time_to_match_start_min"].notna()].copy()
    sub = sub[(sub["time_to_match_start_min"] >= T20) & (sub["time_to_match_start_min"] <= 240)]
    sub["cell"] = sub["cell"].astype(int)
    # earliest placement per (ticker, cell) = row with largest time_to_match_start
    idx = sub.groupby(["ticker", "cell"], observed=True)["time_to_match_start_min"].idxmax()
    fv = sub.loc[idx]
    rows = []
    for c, g in fv.groupby("cell", observed=True):
        c = int(c)
        fl = g["fwd_min_low"].to_numpy() * 100.0
        ev = pd.factorize(g["event_ticker"], sort=False)[0]
        n_ev = int(ev.max() + 1) if len(ev) else 0
        denom = np.bincount(ev, minlength=n_ev) if n_ev else np.array([])
        rec = {"c": c, "n_match": n_ev, "n_side": len(g)}
        for o in OFFSETS:
            hit = (fl <= (c - o)).astype(float)        # real trade down to the bid
            vote = (np.bincount(ev, hit, n_ev) / denom) if n_ev else np.array([])
            rec[f"fill_off{o}"] = float(vote.mean()) if n_ev else np.nan
            rec[f"cost_off{o}"] = c - o
        rows.append(rec)
    return pd.DataFrame(rows)


def pool_headline(hl: pd.DataFrame, df: pd.DataFrame, kmax: int = 3) -> pd.DataFrame:
    """Cluster-sand pool each cell's fill-probs through grain-mass overlap weights (same sand
    as the exit surface), weighted by neighbour match-count. pooled match-N = union of matches."""
    cells, mat, _, _ = bso.grain_mass_overlap(df)
    ci = {c: i for i, c in enumerate(cells)}
    kp = {k: bso.OFFSETS.index(k) for k in bso.OFFSETS}
    Nm = hl.set_index("c")["n_match"].to_dict()
    hi = hl.set_index("c")
    vis = df[df["cell"].notna()].groupby("cell", observed=True)["event_ticker"].apply(set).to_dict()
    out = []
    for c in sorted(Nm):
        c = int(c)
        rec = {"c": c, "own_match_N": int(Nm[c])}
        u = set()
        for k in range(-kmax, kmax + 1):
            if (c + k) in vis:
                u |= vis[c + k]
        rec["match_N"] = len(u)
        for o in OFFSETS:
            wsum = val = 0.0
            for k in range(-kmax, kmax + 1):
                nb = c + k
                if nb not in Nm or c not in ci:
                    continue
                w = mat[ci[c], kp[k]]
                if np.isnan(w):
                    continue
                wn = w * Nm[nb]
                wsum += wn
                val += wn * hi.loc[nb, f"fill_off{o}"]
            rec[f"fill_off{o}"] = (val / wsum) if wsum > 0 else np.nan
            rec[f"cost_off{o}"] = c - o
        # chase-vs-wait: WAIT if the best maker fill-prob clears the floor; else CHASE the taker.
        best = max(rec["fill_off0"], rec["fill_off1"], rec["fill_off2"])
        rec["verdict"] = "WAIT" if best >= WAIT_FLOOR else "CHASE/PASS"
        out.append(rec)
    return pd.DataFrame(out)


def placement_surface(df: pd.DataFrame, kmax: int = 3, bin_min: int = 10) -> pd.DataFrame:
    """(cell c × placement-time bin) base-offset fill-prob — the wait-value curve. Per-minute
    placements (each ticker at one cell per minute); pooled across the c-cluster."""
    sub = df[df["cell"].notna()].copy()
    sub["cell"] = sub["cell"].astype(int)
    sub = sub[(sub["time_to_match_start_min"] >= T20) & (sub["time_to_match_start_min"] <= 240)]
    sub["tbin"] = (sub["time_to_match_start_min"] // bin_min * bin_min).astype(int)
    sub["hit0"] = (sub["fwd_min_low"] * 100.0 <= sub["cell"]).astype(float)
    raw = sub.groupby(["cell", "tbin"], observed=True).agg(fill=("hit0", "mean"),
                                                           n=("hit0", "size")).reset_index()
    # cluster-sand pool over c within each tbin
    cells, mat, _, _ = bso.grain_mass_overlap(df)
    ci = {c: i for i, c in enumerate(cells)}
    kp = {k: bso.OFFSETS.index(k) for k in bso.OFFSETS}
    piv_f = raw.pivot(index="cell", columns="tbin", values="fill")
    piv_n = raw.pivot(index="cell", columns="tbin", values="n").fillna(0)
    out = []
    for c in piv_f.index:
        for tb in piv_f.columns:
            wsum = val = 0.0
            for k in range(-kmax, kmax + 1):
                nb = c + k
                if nb not in piv_f.index or c not in ci:
                    continue
                w = mat[ci[c], kp[k]]
                f = piv_f.loc[nb, tb]
                if np.isnan(w) or pd.isna(f):
                    continue
                wn = w * piv_n.loc[nb, tb]
                wsum += wn
                val += wn * f
            if wsum > 0:
                out.append({"c": int(c), "tbin": int(tb), "fill": val / wsum})
    return pd.DataFrame(out)


def render(hl: pd.DataFrame, surf: pd.DataFrame, out_html: str, category: str, n_tickers: int):
    if go is None:
        print("[headless] plotly not available — skipping HTML")
        return
    cells = sorted(hl["c"])
    hbi = hl.set_index("c")
    hov = {c: (f"<b>cost cell c={c}c</b><br>"
               f"maker-fill (rest @ c): <b>{hbi.loc[c,'fill_off0']*100:.0f}%</b><br>"
               f"  @ c−1 ({c-1}c): {hbi.loc[c,'fill_off1']*100:.0f}%  ·  @ c−2 ({c-2}c): {hbi.loc[c,'fill_off2']*100:.0f}%<br>"
               f"verdict: <b>{hbi.loc[c,'verdict']}</b> · match-N {int(hbi.loc[c,'match_N'])}")
           for c in cells}
    pv = surf.pivot(index="c", columns="tbin", values="fill").reindex(cells)
    tbins = sorted(surf["tbin"].unique())
    fig = go.Figure(go.Heatmap(
        z=pv.values * 100, x=[f"{t}" for t in pv.columns], y=pv.index,
        colorscale="Viridis", zmin=0, zmax=100, colorbar=dict(title="maker-fill %"),
        hoverongaps=False))
    # overlay per-cell headline + verdict markers on the left edge
    fig.add_trace(go.Scatter(
        x=[str(max(tbins))] * len(cells), y=cells, mode="markers",
        marker=dict(symbol="square", size=6,
                    color=[hbi.loc[c, "fill_off0"] * 100 for c in cells],
                    colorscale="Viridis", cmin=0, cmax=100, line=dict(width=0)),
        text=[hov[c] for c in cells], hoverinfo="text", showlegend=False))
    fig.update_layout(
        title=(f"ENTRY maker-fill surface — premarket tape ({category}, {n_tickers} sides)<br>"
               f"<sub>rest a maker BUY at cell c; fill = real traded low ≤ bid before T-20m (honest cross, "
               f"NOT quoted-ask) · cluster-sand-pooled · color = fill% by placement-time (left=early T-4h, "
               f"right=late T-20m) · hover = per-cell headline + conservative offsets + chase/wait</sub>"),
        xaxis_title="placement time-to-match-start (min) — earlier (left) = more wait time",
        yaxis=dict(title="cost-basis cell c (cents)", autorange="reversed", dtick=5),
        template="plotly_dark", width=1300, height=1050)
    fig.write_html(out_html, include_plotlyjs="cdn")


def build(df, out_html, category, kmax=3):
    hl = headline_fill(df)
    pooled = pool_headline(hl, df, kmax)
    surf = placement_surface(df, kmax)
    render(pooled, surf, out_html, category, df["ticker"].nunique())
    return pooled, surf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--kmax", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "chart_entry_fill.html"))
    args = ap.parse_args()
    df = load_premarket(args.input, args.category)
    print(f"{args.category}: {len(df):,} premarket rows · {df.ticker.nunique()} sides · "
          f"{df.event_ticker.nunique()} matches")
    pooled, surf = build(df, args.out, args.category, args.kmax)
    pooled.to_csv(os.path.join(os.path.dirname(__file__), "deploy_entry_fill.csv"), index=False)
    surf.to_csv(os.path.join(os.path.dirname(__file__), "entry_placement_surface.csv"), index=False)

    print("\nENTRY maker-fill headline (place early, rest to T-20, cluster-pooled, 1-match-1-vote):")
    print("  c  fill@c  @c-1  @c-2  verdict     matchN")
    for r in pooled.sort_values("c").iloc[::6].itertuples():
        print(f"  {int(r.c):2d}  {r.fill_off0*100:4.0f}%  {r.fill_off1*100:4.0f}% {r.fill_off2*100:4.0f}%  "
              f"{r.verdict:10s}  {int(r.match_N)}")
    n_wait = int((pooled.verdict == "WAIT").sum())
    print(f"\nWAIT cells: {n_wait}/{len(pooled)}  | fill@c range [{pooled.fill_off0.min()*100:.0f}%, "
          f"{pooled.fill_off0.max()*100:.0f}%]")


if __name__ == "__main__":
    main()
