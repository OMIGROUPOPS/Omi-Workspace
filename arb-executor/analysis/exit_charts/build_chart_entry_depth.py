"""
build_chart_entry_depth.py — OPTIMAL BID-DEPTH per cell: harvest the premarket dip envelope.

Not directional prediction (that was rejected) — this harvests the RELIABLE premarket oscillation
BELOW anchor. Prior drift-envelope work (drift_envelope_*_2026-05-26.md) found the price reliably
dips below the T-20 anchor (median ~3¢ dip, only ~3% never dip below). So instead of laying a maker
bid AT the anchor cell c, lay it at c−D and harvest the dip — a cheaper cost basis → higher exit ROC.

This joins three locked pieces:
  1. dip→fill curve  p(c, D) = honest maker-fill prob at depth D below anchor c
     (real traded low ≤ (c−D)/100 before T-20m; same honest instrument as the entry surface,
     NOT the quoted min_bid the envelope doc used — the envelope's bid-dip is carried as a cross-check).
  2. exit ROC(cost) from the locked exit surface (deploy_gated_optima_<CAT>.csv).
  3. optimal depth D*(c) = argmax_D  p(c,D) · [ROC_exit(c−D) − ROC_exit(c)]
     — balances the reliable dip (fill-prob falls with depth) against the ROC lift of a cheaper basis
     (deep-underdog engine: lower cost cell → higher ROC). With taker-at-anchor fallback the lift is
     pure upside, so D* is where fill-prob × ROC-gain peaks.

Two modes (the surface needs the VPS tape; the join uses the local exit CSVs):
  --surface-only : compute p(c,D) on the premarket tape -> entry_depth_fill_<CAT>.csv (+ env cross-check)
  (default)      : join entry_depth_fill_<CAT>.csv to deploy_gated_optima_<CAT>.csv -> optimal depth + HTML
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
import build_chart_entry_fill as ef

DMAX = 12
ENV_PATH = {"ATP_MAIN": "atp_main", "WTA_MAIN": "wta_main",
            "ATP_CHALL": "atp_chall", "WTA_CHALL": "wta_chall"}


# ---------------------------------------------------------------- surface (VPS) ----
def depth_fill_raw(df: pd.DataFrame) -> pd.DataFrame:
    """Per (anchor cell c, depth D) honest maker-fill prob, one-match-one-vote. Placement = first
    premarket minute at c (max wait), rested to T-20; fill = traded low ≤ (c−D)/100 afterwards."""
    sub = df[df["cell"].notna() & df["time_to_match_start_min"].notna()].copy()
    sub = sub[(sub["time_to_match_start_min"] >= ef.T20) & (sub["time_to_match_start_min"] <= 240)]
    sub["cell"] = sub["cell"].astype(int)
    idx = sub.groupby(["ticker", "cell"], observed=True)["time_to_match_start_min"].idxmax()
    fv = sub.loc[idx]
    rows = []
    for c, g in fv.groupby("cell", observed=True):
        c = int(c)
        fl = g["fwd_min_low"].to_numpy() * 100.0
        ev = pd.factorize(g["event_ticker"], sort=False)[0]
        n = int(ev.max() + 1) if len(ev) else 0
        den = np.bincount(ev, minlength=n) if n else np.array([])
        for D in range(0, DMAX + 1):
            if c - D < 1:
                break
            hit = (fl <= (c - D)).astype(float)
            vote = (np.bincount(ev, hit, n) / den) if n else np.array([])
            rows.append({"c": c, "D": D, "fill": float(vote.mean()) if n else np.nan, "n_match": n})
    return pd.DataFrame(rows)


def pool_depth(raw: pd.DataFrame, df: pd.DataFrame, kmax: int = 3) -> pd.DataFrame:
    cells, mat, _, _ = bso.grain_mass_overlap(df)
    ci = {c: i for i, c in enumerate(cells)}
    kp = {k: bso.OFFSETS.index(k) for k in bso.OFFSETS}
    Nm = raw.groupby("c")["n_match"].first().to_dict()
    vis = df[df["cell"].notna()].groupby("cell", observed=True)["event_ticker"].apply(set).to_dict()
    fz = {(int(r.c), int(r.D)): r.fill for r in raw.itertuples()}
    out = []
    for c in sorted(Nm):
        c = int(c)
        u = set()
        for k in range(-kmax, kmax + 1):
            if (c + k) in vis:
                u |= vis[c + k]
        for D in range(0, DMAX + 1):
            if c - D < 1:
                break
            wsum = val = 0.0
            for k in range(-kmax, kmax + 1):
                nb = c + k
                if nb not in Nm or c not in ci:
                    continue
                w = mat[ci[c], kp[k]]
                f = fz.get((nb, D))
                if np.isnan(w) or f is None or (isinstance(f, float) and np.isnan(f)):
                    continue
                wn = w * Nm[nb]
                wsum += wn
                val += wn * f
            out.append({"c": c, "D": D, "fill": (val / wsum) if wsum > 0 else np.nan,
                        "match_N": len(u)})
    return pd.DataFrame(out)


def env_median_dip(category: str) -> pd.Series:
    """Cross-check: per anchor cell, median bid-based dip (drift_low_vs_anchor) from the envelope."""
    base = "/root/Omi-Workspace/arb-executor/data/durable/spike_volatility_map"
    p = os.path.join(base, f"{ENV_PATH[category]}_drift_envelope.parquet")
    try:
        e = pd.read_parquet(p, columns=["anchor_cents", "drift_low_vs_anchor"])
        return e.groupby("anchor_cents")["drift_low_vs_anchor"].median()
    except Exception:
        return pd.Series(dtype=float)


# ---------------------------------------------------------------- optimize (local) ----
FILL_FLOOR = 0.40   # "reliable" = the bid still fills this often on the honest traded instrument

def optimize(fill_csv: str, exit_csv: str) -> pd.DataFrame:
    fz = pd.read_csv(fill_csv)
    ex = pd.read_csv(exit_csv)
    ex["roc"] = ex["exp_ret_match"] / ex["c"]
    roc = {int(r.c): r.roc for r in ex.itertuples()}
    fmap = {(int(r.c), int(r.D)): r.fill for r in fz.itertuples()}
    mN = fz.groupby("c")["match_N"].first().to_dict()
    env = fz.groupby("c")["env_med_dip"].first().to_dict() if "env_med_dip" in fz.columns else {}
    rows = []
    for c in sorted({int(x) for x in fz["c"]}):
        if c not in roc:
            continue
        base = roc[c]
        depths = []
        for D in range(0, DMAX + 1):
            cost = c - D
            if cost < 5 or cost not in roc:
                continue
            f = fmap.get((c, D))
            if f is None or np.isnan(f):
                continue
            depths.append((D, f, cost, roc[cost], f * (roc[cost] - base)))
        if not depths:
            continue
        # RELIABLE depth (headline): the ROC-best depth whose HONEST fill clears the floor — the dip
        # you can actually rest into AND that lifts ROC. If no fillable depth lifts ROC, lay at the
        # anchor (D=0, no dip-harvest edge there). Uses traded fill, not the envelope's bid-dip.
        d0 = next((d for d in depths if d[0] == 0), depths[0])
        rel = [d for d in depths if d[1] >= FILL_FLOOR]
        cand = max(rel, key=lambda x: x[4]) if rel else d0
        rD, rf, rcost, rroc, rlift = cand if cand[4] > 0 else d0
        # AGGRESSIVE depth: unconstrained argmax fill·ROC-gain (chases the deep-underdog ROC; often
        # pinned at DMAX => flagged, low-fill tail, taker-fallback most of the time).
        aD, af, acost, aroc, alift = max(depths, key=lambda x: x[4])
        rows.append({
            "anchor_c": c,
            "reliable_depth": rD, "reliable_fill": round(rf, 4), "reliable_cost": rcost,
            "reliable_roc_at_cost": round(rroc, 4), "reliable_roc_lift": round(rlift, 4),
            "reliable_combined_roc": round(rf * rroc + (1 - rf) * base, 4),
            "aggr_depth": aD, "aggr_fill": round(af, 4), "aggr_lift": round(alift, 4),
            "aggr_capped": aD >= DMAX,
            "roc_anchor": round(base, 4), "env_med_dip_bid": env.get(c, np.nan),
            "match_N": int(mN.get(c, 0))})
    return pd.DataFrame(rows)


def render(fz: pd.DataFrame, opt: pd.DataFrame, out_html: str, category: str):
    if go is None:
        print("[headless] plotly missing — skipping HTML")
        return
    ex_roc = None
    cells = sorted({int(x) for x in fz["c"]})
    piv = fz.pivot(index="c", columns="D", values="fill").reindex(cells)
    ob = opt.set_index("anchor_c")
    fig = go.Figure(go.Heatmap(z=piv.values * 100, x=[str(d) for d in piv.columns], y=piv.index,
                               colorscale="Viridis", zmin=0, zmax=100,
                               colorbar=dict(title="maker-fill %"), hoverongaps=False))
    txt = [(f"<b>anchor c={c}</b><br>RELIABLE: lay at c−{int(ob.loc[c,'reliable_depth'])} = {int(ob.loc[c,'reliable_cost'])}c, "
            f"fill {ob.loc[c,'reliable_fill']*100:.0f}%, ROC {ob.loc[c,'roc_anchor']*100:.0f}%→{ob.loc[c,'reliable_roc_at_cost']*100:.0f}% "
            f"(+{ob.loc[c,'reliable_roc_lift']*100:.1f}pp)<br>aggr argmax: c−{int(ob.loc[c,'aggr_depth'])} @ {ob.loc[c,'aggr_fill']*100:.0f}% fill"
            f"{' [CAPPED]' if ob.loc[c,'aggr_capped'] else ''}<br>env-dip(bid) {ob.loc[c,'env_med_dip_bid']:.0f}c")
           if c in ob.index else "" for c in cells]
    # RELIABLE depth (white square) — the bid-depth you can actually rest into
    rd = [str(int(ob.loc[c, "reliable_depth"])) if c in ob.index else "0" for c in cells]
    fig.add_trace(go.Scatter(x=rd, y=cells, mode="markers",
                             marker=dict(symbol="square-open", size=10, line=dict(width=2, color="#ffffff")),
                             text=txt, hoverinfo="text", showlegend=False, name="reliable depth"))
    # aggressive argmax (magenta diamond) — chases deep-underdog ROC on the low-fill tail
    ad = [str(int(ob.loc[c, "aggr_depth"])) if c in ob.index else "0" for c in cells]
    fig.add_trace(go.Scatter(x=ad, y=cells, mode="markers",
                             marker=dict(symbol="diamond-open", size=7, line=dict(width=1, color="#ff2bd6")),
                             hoverinfo="skip", showlegend=False, name="aggressive argmax"))
    fig.update_layout(
        title=(f"ENTRY bid-DEPTH optimizer — harvest the premarket dip ({category})<br>"
               f"<sub>lay maker BUY at c−D; color = honest fill% at depth D (traded low ≤ c−D before T-20) · "
               f"□ = optimal D* = argmax fill·(ROC(c−D)−ROC(c)) joined to locked exit ROC · NOT directional</sub>"),
        xaxis_title="bid depth below anchor D (cents)",
        yaxis=dict(title="anchor cell c (cents)", autorange="reversed", dtick=5),
        template="plotly_dark", width=1150, height=1050)
    fig.write_html(out_html, include_plotlyjs="cdn")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--surface-only", action="store_true", help="VPS: compute dip→fill surface from tape")
    ap.add_argument("--input", help="premarket tape (surface mode)")
    ap.add_argument("--fill-csv", help="entry_depth_fill_<CAT>.csv (optimize mode)")
    ap.add_argument("--exit-csv", help="deploy_gated_optima_<CAT>.csv (optimize mode)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    here = os.path.dirname(__file__)

    if args.surface_only:
        df = ef.load_premarket(args.input, args.category)
        raw = depth_fill_raw(df)
        fz = pool_depth(raw, df)
        med = env_median_dip(args.category)
        fz["env_med_dip"] = fz["c"].map(med)
        outcsv = os.path.join(here, f"entry_depth_fill_{args.category}.csv")
        fz.to_csv(outcsv, index=False)
        print(f"{args.category}: depth surface -> {outcsv} ({len(fz)} (c,D) cells, "
              f"{df.event_ticker.nunique()} matches, env median dip carried)")
        return

    fill_csv = args.fill_csv or os.path.join(here, f"entry_depth_fill_{args.category}.csv")
    exit_csv = args.exit_csv or os.path.join(here, f"deploy_gated_optima_{args.category}.csv")
    fz = pd.read_csv(fill_csv)
    opt = optimize(fill_csv, exit_csv)
    opt.to_csv(os.path.join(here, f"deploy_entry_depth_{args.category}.csv"), index=False)
    render(fz, opt, args.out or os.path.join(here, f"chart_entry_depth_{args.category}.html"), args.category)
    ncap = int(opt.aggr_capped.sum())
    print(f"\n{args.category} — RELIABLE bid-depth (deepest D with honest fill>={FILL_FLOOR:.0%}), joined to exit ROC:")
    print("  anchor | reliable: D bid@ fill  ROC anchor->cost (+lift) | aggr argmax D@fill | env-dip(bid)")
    for r in opt[opt.anchor_c.isin(range(5, 95, 6))].itertuples():
        cap = "*" if r.aggr_capped else " "
        print(f"   c={int(r.anchor_c):2d}  |  {int(r.reliable_depth):2d} {int(r.reliable_cost):2d}c {r.reliable_fill*100:3.0f}%  "
              f"{r.roc_anchor*100:4.0f}%->{r.reliable_roc_at_cost*100:4.0f}% (+{r.reliable_roc_lift*100:3.1f}pp) | "
              f"{int(r.aggr_depth):2d}@{r.aggr_fill*100:2.0f}%{cap} | {r.env_med_dip_bid:.0f}c")
    print(f"  [{ncap}/{len(opt)} cells: aggr argmax pinned at DMAX={DMAX} (deep-underdog ROC pulls past the cap — "
          f"speculative low-fill tail, not the reliable harvest)]")


if __name__ == "__main__":
    main()
