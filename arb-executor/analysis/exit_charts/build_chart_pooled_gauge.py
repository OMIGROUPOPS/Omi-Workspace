"""
build_chart_pooled_gauge.py — LAYER 2: the sand-pooled, settlement-blind exit gauge.

This is the missing middle layer. The sand/overlap chart proved ~97-100% of a cell's
grain-mass is shared with c+-1 (same physical paths recovered from adjacent sample
points). Layer 1 then *ignored* that and scored each cell on its own thin N. Layer 2
closes the circle: it POOLS each cell's effective sample through the sand overlap
weights, then gauges reach / net / ROI on the pooled, settlement-blind sample.

GAUGE CONTRACT (per the conceptual correction):
  Reach is SETTLEMENT-BLIND. reach(c,X) = fraction of ALL contracts passing through
    cell c that EVER trade to c+X at any forward minute. NO winner/loser split.
    Instrument = TRADED price: max(forward price_high) >= (c+X)/100, skip-inclusive.
    (yes_bid_high / max_yes_bid_forward_* are QUOTED bid -> banned for reach.
     bounce_* is bid-derived (corr 0.84 vs max_yes_bid_forward at settlement, and
     goes negative) -> also not reused.)
  Settlement enters ONLY on the misses. A miss = never reached c+X; you hold to
    settlement and realise settlement_value. Per-miss loss (cents) = c - 100*settle.
    net(c,X) = reach*X  -  miss_rate * E[c - 100*settle | miss]
  A winner that traded through c+X is a REAL fill we take (counted in reach); it is
    not free inflation because misses are charged at settlement.

POOLING (Layer 2):
  w(c,k) = grain-mass overlap from the sand chart (build_chart_sand_overlap).
  pooled_q(c,X) = Σ_k w(c,k)·N(c+k)·q(c+k,X) / Σ_k w(c,k)·N(c+k)   for q in {reach,net,roi}
  pooled_N(c)   = Σ_k w(c,k)·N(c+k)        (effective weighted sample; raw_N also reported)
  Each neighbor's q is cost-relative (its own cost c+k, its own +X), so pooling
  estimates the +X action "near cost c" on a thick sample — favorites included.

Usage: python build_chart_pooled_gauge.py [--input PATH] [--category ATP_MAIN] [--kmax 3]
"""
from __future__ import annotations
import argparse
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

import chart_common as cc
import build_chart_sand_overlap as bso


def raw_cell_block_table(df: pd.DataFrame) -> pd.DataFrame:
    """Per (c, X) settlement-blind reach + settlement-on-miss net, own-cell sample."""
    rows = []
    sub = df[df["cell"].notna()]
    for c, g in sub.groupby("cell"):
        c = int(c)
        ft = g["fwd_max_traded"].to_numpy() * 100.0          # traded forward high, cents
        settle = g["settlement_value"].to_numpy() * 100.0    # 0 or 100 cents
        n = len(g)
        # match-weighted reach denominator: best forward-traded per DISTINCT match (ticker).
        # minute-weighted reach over-counts winner-minutes (a winner lingers near c on its
        # way up and reaches 99); per-match collapses that survivorship bias.
        match_max = g.groupby("ticker")["fwd_max_traded"].max().to_numpy() * 100.0
        n_tk = len(match_max)
        for X in range(1, cc.LOCK - c + 1):
            tgt = c + X
            fill_mask = ft >= tgt                            # settlement-blind reach
            reach = float(np.nanmean(fill_mask.astype(float)))
            match_reach = float(np.nanmean((match_max >= tgt).astype(float)))
            miss_mask = ~fill_mask & ~np.isnan(ft)
            miss_rate = 1.0 - reach
            # downside of a miss: hold to settlement -> realise settle; loss = c - settle
            if miss_mask.any():
                settle_on_miss = np.nanmean(settle[miss_mask])
            else:
                settle_on_miss = np.nan
            miss_cost = c - settle_on_miss if not np.isnan(settle_on_miss) else 0.0
            net = reach * X - miss_rate * miss_cost
            rows.append({
                "c": c, "X": X, "target": tgt, "raw_N": n, "n_tk": n_tk,
                "reach": reach, "match_reach": match_reach, "miss_rate": miss_rate,
                "settle_on_miss": settle_on_miss, "miss_cost": miss_cost,
                "net": net, "roi_on_cost": net / c,
            })
    return pd.DataFrame(rows)


def pooled_gauge(raw: pd.DataFrame, df: pd.DataFrame, kmax: int):
    """Pool each (c,X) through sand grain-mass overlap weights."""
    cells, mat, total_mass, n_tickers = bso.grain_mass_overlap(df)
    cell_idx = {c: i for i, c in enumerate(cells)}
    kpos = {k: bso.OFFSETS.index(k) for k in bso.OFFSETS}
    Nraw = raw.groupby("c")["raw_N"].first().to_dict()
    Ntk = raw.groupby("c")["n_tk"].first().to_dict()   # distinct matches per cell

    # weight w(c,k) = overlap mass; pooled_N(c) = Σ_k w·N(c+k)
    pooled_N = {}
    for c in Nraw:
        tot = 0.0
        for k in range(-kmax, kmax + 1):
            nb = c + k
            if nb in Nraw and not np.isnan(mat[cell_idx[c], kpos[k]]):
                tot += mat[cell_idx[c], kpos[k]] * Nraw[nb]
        pooled_N[c] = tot

    # index raw by (c,X) for fast neighbor lookup
    raw_ix = {(r.c, r.X): r for r in raw.itertuples()}
    out = []
    for r in raw.itertuples():
        c, X = r.c, r.X
        wsum = 0.0          # minute-mass weight (overlap × minute-N)
        wsum_tk = 0.0       # match weight (overlap × distinct-match-N)
        rch = net = roi = 0.0
        mrch = 0.0
        for k in range(-kmax, kmax + 1):
            nb = c + k
            w = mat[cell_idx[c], kpos[k]] if (c in cell_idx) else np.nan
            if nb not in Nraw or np.isnan(w):
                continue
            nbr = raw_ix.get((nb, X))           # cost-relative: neighbor's own +X
            if nbr is None:
                continue
            wn = w * Nraw[nb]
            wsum += wn
            rch += wn * nbr.reach
            net += wn * nbr.net
            roi += wn * nbr.roi_on_cost
            wtk = w * Ntk[nb]
            wsum_tk += wtk
            mrch += wtk * nbr.match_reach
        if wsum > 0:
            out.append({
                "c": c, "X": X, "target": r.target,
                "raw_N": int(r.raw_N), "pooled_N": round(pooled_N[c], 1),
                "reach_raw": r.reach, "reach_pooled": rch / wsum,
                "reach_pooled_match": (mrch / wsum_tk) if wsum_tk > 0 else np.nan,
                "net_raw": r.net, "net_pooled": net / wsum,
                "roi_pooled": roi / wsum,
                "miss_rate_raw": r.miss_rate, "miss_cost_raw": r.miss_cost,
            })
    res = pd.DataFrame(out)
    # monotone reach envelope (physical: P(reach higher target) <= P(reach lower target)).
    # cummin over X within each cell removes the 99-lock uptick artifact before gating.
    res["reach_pooled_mono"] = res.sort_values("X").groupby("c")["reach_pooled"].cummin()
    return res, pooled_N, Nraw


def predictability_optimal(pooled: pd.DataFrame, reach_floor: float,
                           gate_basis: str = "minute") -> pd.DataFrame:
    """PREDICTABILITY-GATED optimum: per cell, the DEEPEST X whose pooled reach clears
    the floor. NOT argmax(net) — that chases cheap-cell moonshots (c5→+81 at 47% reach
    nets +35c only because miss-cost is ~5c, the variance-chase the operator rejects).
    Going as deep as the floor allows maximises offset while keeping the fill predictable.
    Cells where no X clears the floor are not deployable at that floor.

    gate_basis='minute' (default, honors the +14 c5 anchor): gate on the monotone
        minute-weighted pooled reach. Deep picks may be minute-survivorship-inflated
        (flagged via match_confirmed).
    gate_basis='match' (conservative deploy gate): gate on match-weighted pooled reach
        (each distinct match once) — collapses winner-minute survivorship.
    """
    gate_col = {"minute": "reach_pooled_mono", "match": "reach_pooled_match"}[gate_basis]
    rows = []
    for c, grp in pooled.groupby("c"):
        # deepest X in the contiguous high-reach run from X=1 (never jump a sub-floor dip).
        ok = grp[grp[gate_col] >= reach_floor]
        if len(ok):
            rows.append(ok.loc[ok.X.idxmax()])
    opt = pd.DataFrame(rows).sort_values("c").reset_index(drop=True)
    # honesty flag: is the gated optimum still predictable on the MATCH denominator?
    # If match-weighted pooled reach falls well below the floor, the depth is inflated
    # by minute-level winner-survivorship — surface, do not deploy blindly.
    opt["match_confirmed"] = opt["reach_pooled_match"] >= (reach_floor - 0.05)
    return opt


def floor_sweep(pooled: pd.DataFrame, pooled_N: dict, floors=(0.80, 0.85, 0.90),
                healthy_min_pooled_N: float = 200.0) -> pd.DataFrame:
    """Deployable-set sensitivity across reach floors, measured on healthy-pooled-N cells.
    Lock the floor sitting in the flattest stretch (lowest |dX| to neighbours)."""
    sets = {f: predictability_optimal(pooled, f).set_index("c")["X"].to_dict() for f in floors}
    healthy = {c for c in pooled["c"].unique() if pooled_N.get(c, 0) >= healthy_min_pooled_N}
    rows = []
    fl = list(floors)
    for i, f in enumerate(fl):
        s = sets[f]
        dprev = dnext = np.nan
        if i > 0:
            common = [c for c in s if c in sets[fl[i-1]] and c in healthy]
            dprev = float(np.mean([abs(s[c] - sets[fl[i-1]][c]) for c in common]))
        if i < len(fl) - 1:
            common = [c for c in s if c in sets[fl[i+1]] and c in healthy]
            dnext = float(np.mean([abs(s[c] - sets[fl[i+1]][c]) for c in common]))
        rows.append({"floor": f, "n_deployable": len(s),
                     "meanX": float(np.mean(list(s.values()))),
                     "c5_X": s.get(5), "c50_X": s.get(50), "c90_X": s.get(90),
                     "meanAbsDX_to_lower": dprev, "meanAbsDX_to_higher": dnext})
    return pd.DataFrame(rows)


def build(df: pd.DataFrame, out_html: str, category: str, kmax: int, reach_floor: float, gate_basis: str = "minute"):
    raw = raw_cell_block_table(df)
    pooled, pooled_N, Nraw = pooled_gauge(raw, df, kmax)

    # PREDICTABILITY-GATED optimal (deepest X clearing the reach floor) — NOT argmax net.
    opt = predictability_optimal(pooled, reach_floor, gate_basis)
    opt_keys = set(zip(opt.c, opt.X))

    pooled["W"] = cc.LOCK - pooled["c"]
    pooled["xpos"] = pooled["X"] - (pooled["W"] + 1) / 2.0
    mlow = {(r.c, r.X) for r in opt.itertuples() if not r.match_confirmed}
    hov = [
        f"<b>cost c={int(r.c)}c → exit +{int(r.X)}c (sell @ {int(r.target)}c)</b><br>"
        f"reach (settlement-blind, traded): raw {r.reach_raw*100:.1f}% → <b>pooled {r.reach_pooled*100:.1f}%</b><br>"
        f"  match-weighted (honest denom): {r.reach_pooled_match*100:.1f}%<br>"
        f"net: raw {r.net_raw:+.2f}c → <b>pooled {r.net_pooled:+.2f}c</b>  · ROI {r.roi_pooled*100:+.1f}%<br>"
        f"miss {r.miss_rate_raw*100:.1f}% · miss-cost {r.miss_cost_raw:.1f}c (c − settle)<br>"
        f"N: raw {r.raw_N} → <b>pooled {r.pooled_N:.0f}</b>"
        + (f"<br><b>★ optimal — deepest X with reach≥{reach_floor*100:.0f}%</b>" if (r.c, r.X) in opt_keys else "")
        + ("<br>⚠ match-weighted reach below floor — minute-survivorship-inflated depth"
           if (r.c, r.X) in mlow else "")
        for r in pooled.itertuples()
    ]

    # default color layer = pooled reach (the gated quantity); net layers are for comparison.
    fig = go.Figure()
    fig.add_trace(go.Scatter(  # 0
        x=pooled.xpos, y=pooled.c, mode="markers", name=f"pooled reach % (gate={reach_floor*100:.0f})",
        marker=dict(symbol="square", size=7, color=pooled.reach_pooled * 100, colorscale="YlGnBu",
                    cmin=0, cmax=100, colorbar=dict(title="pooled reach %"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=True))
    fig.add_trace(go.Scatter(  # 1
        x=pooled.xpos, y=pooled.c, mode="markers", name="pooled net (c)",
        marker=dict(symbol="square", size=7, color=pooled.net_pooled, colorscale="RdYlGn",
                    cmid=0, colorbar=dict(title="pooled net (c)"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=False))
    fig.add_trace(go.Scatter(  # 2 — raw (own-cell) net, comparison only; NOT optimised on
        x=pooled.xpos, y=pooled.c, mode="markers", name="raw net (own-cell, compare only)",
        marker=dict(symbol="square", size=7, color=pooled.net_raw, colorscale="RdYlGn",
                    cmid=0, colorbar=dict(title="raw net (c)"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=False))
    ot_mask = [(c, X) in opt_keys for c, X in zip(pooled.c, pooled.X)]
    ot = pooled[ot_mask]
    # white = match-confirmed; amber = minute-survivorship-inflated depth (audit before deploy)
    ot_colors = ["#ffb020" if (c, X) in mlow else "#ffffff" for c, X in zip(ot.c, ot.X)]
    fig.add_trace(go.Scatter(  # 3 — predictability-gated optimum, always visible
        x=ot.xpos, y=ot.c, mode="markers",
        name=f"optimal (deepest X, reach≥{reach_floor*100:.0f}%; amber=match-unconfirmed)",
        marker=dict(symbol="square-open", size=11, color="rgba(0,0,0,0)", line=dict(width=2, color=ot_colors)),
        text=[h for h, k in zip(hov, ot_mask) if k], hoverinfo="text", visible=True))

    fig.update_layout(
        title=(f"LAYER 2 — sand-pooled, SETTLEMENT-BLIND exit gauge ({category}, {df.ticker.nunique()} tickers, k±{kmax})<br>"
               f"<sub>reach = traded-forward to c+X (no winner/loser split) · net = reach·X − miss·(c−settle) · "
               f"pooled sample · ★ = PREDICTABILITY-GATED optimum: deepest X with pooled reach ≥ {reach_floor*100:.0f}% "
               f"(NOT argmax-net; raw net kept as compare layer only)</sub>"),
        xaxis=dict(title="exit offset slots (centred; reach to the 99 lock)", zeroline=False, showgrid=False),
        yaxis=dict(title="cost-basis cell c (cents)", autorange="reversed", dtick=5, showgrid=False),
        template="plotly_dark", width=1400, height=1150, plot_bgcolor="#0a0a0a",
        updatemenus=[dict(type="buttons", direction="right", x=0, y=1.06, xanchor="left", buttons=[
            dict(label="pooled reach %", method="update", args=[{"visible": [True, False, False, True]}]),
            dict(label="pooled net", method="update", args=[{"visible": [False, True, False, True]}]),
            dict(label="raw net (compare)", method="update", args=[{"visible": [False, False, True, True]}]),
        ])])
    fig.write_html(out_html, include_plotlyjs="cdn")
    return raw, pooled, opt, pooled_N, Nraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=cc.DEFAULT_INPUT)
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--kmax", type=int, default=3)
    ap.add_argument("--reach-floor", type=float, default=0.85,
                    help="predictability gate: optimal X = deepest X with pooled reach >= this")
    ap.add_argument("--gate-basis", choices=["minute", "match"], default="minute",
                    help="minute (default, honors c5 +14 anchor) or match (conservative deploy gate)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "chart_pooled_gauge.html"))
    args = ap.parse_args()
    df = cc.load_universe(args.input, args.category)
    raw, pooled, opt, pooled_N, Nraw = build(df, args.out, args.category, args.kmax, args.reach_floor, args.gate_basis)

    # distinct-ticker (independent match) denominators — the deployment-relevant N.
    # minute-pooled_N is inflated by within-match autocorrelation; ticker counts are not.
    sub = df[df["cell"].notna()]
    vis = sub.groupby("cell")["ticker"].apply(lambda s: set(s)).to_dict()

    def pooled_tk(c):
        u = set()
        for k in range(-args.kmax, args.kmax + 1):
            u |= vis.get(c + k, set())
        return len(u)

    # pooled-N-per-cell flag-back table
    rep = pd.DataFrame({"c": sorted(Nraw), "raw_N": [Nraw[c] for c in sorted(Nraw)],
                        "pooled_N": [round(pooled_N[c], 1) for c in sorted(Nraw)],
                        "raw_tickers": [len(vis.get(c, set())) for c in sorted(Nraw)],
                        "pooled_tickers": [pooled_tk(c) for c in sorted(Nraw)]})
    rep["pool_mult"] = (rep.pooled_N / rep.raw_N).round(2)
    rep.to_csv(os.path.join(os.path.dirname(__file__), "pooled_N_per_cell.csv"), index=False)
    pooled.to_csv(os.path.join(os.path.dirname(__file__), "pooled_gauge_blocks.csv"), index=False)

    print("LAYER2 pooled gauge ->", args.out)
    print(f"cells: {len(rep)}  | minute raw_N [{rep.raw_N.min()}, {rep.raw_N.max()}] -> "
          f"pooled_N [{rep.pooled_N.min():.0f}, {rep.pooled_N.max():.0f}]  | "
          f"distinct-ticker raw [{rep.raw_tickers.min()}, {rep.raw_tickers.max()}] -> "
          f"pooled [{rep.pooled_tickers.min()}, {rep.pooled_tickers.max()}] of {df.ticker.nunique()}")
    # show the thin-favorite rescue explicitly (minutes AND independent matches)
    thin = rep[rep.raw_N < 60].sort_values("c")
    print(f"\nthin own-N cells rescued by pooling (raw_N<60), {len(thin)} cells:")
    for r in thin.itertuples():
        print(f"  c={r.c:2d}  raw_N={r.raw_N:3d}->pooled {r.pooled_N:6.0f} ({r.pool_mult:4.1f}x)  "
              f"| matches {r.raw_tickers}->{r.pooled_tickers}")
    # predictability-gate floor sweep (the lock decision, on healthy-pooled-N cells)
    sweep = floor_sweep(pooled, pooled_N, floors=(0.80, 0.85, 0.90))
    sweep.to_csv(os.path.join(os.path.dirname(__file__), "reach_floor_sweep.csv"), index=False)
    print(f"\nPREDICTABILITY-GATE floor sweep (locked floor = {args.reach_floor:.2f}):")
    print(sweep.to_string(index=False, float_format=lambda v: f"{v:.2f}"))

    n_unconf = int((~opt.match_confirmed).sum())
    print(f"\nGATED optimum (deepest X, monotone pooled reach >= {args.reach_floor:.0%}) per cell, sample "
          f"({n_unconf}/{len(opt)} match-UNconfirmed = minute-survivorship-inflated depth):")
    for r in opt.iloc[::8].itertuples():
        flag = "" if r.match_confirmed else "  <<MATCH-UNCONFIRMED"
        print(f"  c={int(r.c):2d}  +{int(r.X):2d}  reach_min={r.reach_pooled*100:5.1f}%  "
              f"reach_match={r.reach_pooled_match*100:5.1f}%  ROI(X/c)={r.X/r.c*100:5.0f}%  "
              f"net={r.net_pooled:+.2f}c{flag}")


if __name__ == "__main__":
    main()
