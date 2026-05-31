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
        # MATCH-weighted denominator (canonical deploy gate): one match = one vote.
        # minute-weighted reach over-counts winner-minutes (a winner loiters at a price on
        # its way up to 99 and donates dozens of "reached" minutes — stuffs the ballot box).
        # Per-match (best forward-traded + settlement per ticker) is the honest denominator:
        # of N matches, how many actually paid.
        gm = g.groupby("ticker")
        match_max = gm["fwd_max_traded"].max().to_numpy() * 100.0
        match_settle = gm["settlement_value"].first().to_numpy() * 100.0  # 0/100, const per match
        n_tk = len(match_max)
        for X in range(1, cc.LOCK - c + 1):
            tgt = c + X
            fill_mask = ft >= tgt                            # settlement-blind reach
            reach = float(np.nanmean(fill_mask.astype(float)))           # minute (diagnostic)
            m_reach = float(np.nanmean((match_max >= tgt).astype(float)))  # match (canonical)
            # minute miss-cost (diagnostic)
            miss_mask = ~fill_mask & ~np.isnan(ft)
            miss_rate = 1.0 - reach
            settle_on_miss = np.nanmean(settle[miss_mask]) if miss_mask.any() else np.nan
            miss_cost = c - settle_on_miss if not np.isnan(settle_on_miss) else 0.0
            net = reach * X - miss_rate * miss_cost
            # match miss-cost + EXPECTED RETURN (deploy surface): hold a miss to settlement.
            m_miss = match_max < tgt
            m_settle_on_miss = np.nanmean(match_settle[m_miss]) if m_miss.any() else np.nan
            m_miss_cost = c - m_settle_on_miss if not np.isnan(m_settle_on_miss) else 0.0
            exp_ret_match = m_reach * X - (1.0 - m_reach) * m_miss_cost
            rows.append({
                "c": c, "X": X, "target": tgt, "raw_N": n, "n_tk": n_tk,
                "reach": reach, "match_reach": m_reach, "miss_rate": miss_rate,
                "settle_on_miss": settle_on_miss, "miss_cost": miss_cost, "net": net,
                "match_miss_cost": m_miss_cost, "exp_ret_match": exp_ret_match,
            })
    return pd.DataFrame(rows)


def pooled_gauge(raw: pd.DataFrame, df: pd.DataFrame, kmax: int):
    """Pool each (c,X) through sand grain-mass overlap weights."""
    cells, mat, total_mass, n_tickers = bso.grain_mass_overlap(df)
    cell_idx = {c: i for i, c in enumerate(cells)}
    kpos = {k: bso.OFFSETS.index(k) for k in bso.OFFSETS}
    Nraw = raw.groupby("c")["raw_N"].first().to_dict()
    Ntk = raw.groupby("c")["n_tk"].first().to_dict()   # distinct matches per cell
    # distinct-match sets per cell -> pooled match-N = union of matches over k±kmax (the
    # deployment-relevant N behind a gated pick; NOT a minute count).
    vis = df[df["cell"].notna()].groupby("cell")["ticker"].apply(set).to_dict()

    # weight w(c,k) = overlap mass; pooled_N(c) = Σ_k w·N(c+k)
    pooled_N, match_N = {}, {}
    for c in Nraw:
        tot = 0.0
        u = set()
        for k in range(-kmax, kmax + 1):
            nb = c + k
            if nb in Nraw and not np.isnan(mat[cell_idx[c], kpos[k]]):
                tot += mat[cell_idx[c], kpos[k]] * Nraw[nb]
            u |= vis.get(nb, set())
        pooled_N[c] = tot
        match_N[c] = len(u)

    # index raw by (c,X) for fast neighbor lookup
    raw_ix = {(r.c, r.X): r for r in raw.itertuples()}
    out = []
    for r in raw.itertuples():
        c, X = r.c, r.X
        wsum = 0.0          # minute-mass weight (overlap × minute-N)
        wsum_tk = 0.0       # match weight (overlap × distinct-match-N)
        rch = net = 0.0
        mrch = expret = 0.0
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
            wtk = w * Ntk[nb]
            wsum_tk += wtk
            mrch += wtk * nbr.match_reach
            expret += wtk * nbr.exp_ret_match
        if wsum > 0:
            out.append({
                "c": c, "X": X, "target": r.target,
                "raw_N": int(r.raw_N), "pooled_N": round(pooled_N[c], 1),
                "match_N": match_N[c],                       # distinct matches behind the pick
                "reach_raw": r.reach, "reach_pooled": rch / wsum,            # minute (diagnostic)
                "reach_pooled_match": (mrch / wsum_tk) if wsum_tk > 0 else np.nan,  # canonical
                "exp_ret_match": (expret / wsum_tk) if wsum_tk > 0 else np.nan,     # DEPLOY value
                "net_raw": r.net, "net_pooled": net / wsum,                 # minute net (diag)
                "miss_cost_raw": r.miss_cost,
            })
    res = pd.DataFrame(out)
    # monotone reach envelope (physical: P(reach higher target) <= P(reach lower target)).
    # cummin over X within each cell removes the 99-lock uptick artifact before gating.
    s = res.sort_values("X")
    res["reach_pooled_mono"] = s.groupby("c")["reach_pooled"].cummin()
    res["reach_pooled_match_mono"] = s.groupby("c")["reach_pooled_match"].cummin()
    return res, pooled_N, Nraw


def predictability_optimal(pooled: pd.DataFrame, reach_floor: float,
                           gate_basis: str = "match") -> pd.DataFrame:
    """PREDICTABILITY-GATED optimum: per cell, the DEEPEST X whose pooled reach clears
    the floor. NOT argmax(net) — that chases cheap-cell moonshots (c5→+81 at 47% reach
    nets +35c only because miss-cost is ~5c, the variance-chase the operator rejects).
    Going as deep as the floor allows maximises offset while keeping the fill predictable.
    Cells where no X clears the floor are not deployable at that floor.

    gate_basis='match' (DEFAULT, canonical deploy gate): gate on the monotone match-weighted
        pooled reach — one match one vote. Collapses winner-minute survivorship (a winning
        contract loitering on its way to 99 would otherwise stuff the ballot box).
    gate_basis='minute' (DIAGNOSTIC ONLY): monotone minute-weighted reach. Over-optimistic
        wherever winners linger; the minute-vs-match gap pinpoints those cells. Do NOT deploy.
    """
    gate_col = {"match": "reach_pooled_match_mono", "minute": "reach_pooled_mono"}[gate_basis]
    rows = []
    for c, grp in pooled.groupby("c"):
        # deepest X in the contiguous high-reach run from X=1 (never jump a sub-floor dip).
        ok = grp[grp[gate_col] >= reach_floor]
        if len(ok):
            rows.append(ok.loc[ok.X.idxmax()])
    opt = pd.DataFrame(rows).sort_values("c").reset_index(drop=True)
    # diagnostic: how far the minute gate would have over-reached vs this match-gated pick.
    opt["minute_over_optimistic"] = opt["reach_pooled"] - opt["reach_pooled_match"]
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


THIN_MATCH_N = 15  # distinct matches below which a gated pick is structurally thin

def build(df: pd.DataFrame, out_html: str, category: str, kmax: int, reach_floor: float, gate_basis: str = "match"):
    raw = raw_cell_block_table(df)
    pooled, pooled_N, Nraw = pooled_gauge(raw, df, kmax)

    # PREDICTABILITY-GATED optimal (deepest X clearing the reach floor) — MATCH-weighted.
    opt = predictability_optimal(pooled, reach_floor, gate_basis)
    opt_keys = set(zip(opt.c, opt.X))
    thin = {(r.c, r.X) for r in opt.itertuples() if r.match_N < THIN_MATCH_N}

    pooled["W"] = cc.LOCK - pooled["c"]
    pooled["xpos"] = pooled["X"] - (pooled["W"] + 1) / 2.0
    hov = [
        f"<b>cost c={int(r.c)}c → exit +{int(r.X)}c (sell @ {int(r.target)}c)</b><br>"
        f"<b>match-weighted reach (CANONICAL): {r.reach_pooled_match*100:.1f}%</b>  "
        f"[minute diag: {r.reach_pooled*100:.1f}%, gap {(r.reach_pooled-r.reach_pooled_match)*100:+.1f}pp]<br>"
        f"<b>expected return: {r.exp_ret_match:+.2f}c</b>  = reach_match·X − miss·(c−settle)<br>"
        f"minute net (diag, do not deploy): {r.net_pooled:+.2f}c<br>"
        f"<b>match-N (distinct matches): {r.match_N}</b> · pooled minute-N {r.pooled_N:.0f}"
        + (f"<br><b>★ optimal — deepest X with match reach≥{reach_floor*100:.0f}%</b>" if (r.c, r.X) in opt_keys else "")
        + ("<br>⚠ THIN: <15 distinct matches behind this pick" if (r.c, r.X) in thin else "")
        for r in pooled.itertuples()
    ]

    # CANONICAL deploy layer first = match-weighted EXPECTED RETURN. Minute layers = diagnostic.
    fig = go.Figure()
    er = pooled.exp_ret_match
    erlim = float(np.nanpercentile(np.abs(er), 98))
    fig.add_trace(go.Scatter(  # 0 — DEPLOY surface
        x=pooled.xpos, y=pooled.c, mode="markers", name="expected return (c) — DEPLOY",
        marker=dict(symbol="square", size=7, color=er, colorscale="RdYlGn", cmid=0,
                    cmin=-erlim, cmax=erlim, colorbar=dict(title="exp. return (c)"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=True))
    fig.add_trace(go.Scatter(  # 1 — canonical reach
        x=pooled.xpos, y=pooled.c, mode="markers", name="match reach % (canonical)",
        marker=dict(symbol="square", size=7, color=pooled.reach_pooled_match * 100, colorscale="YlGnBu",
                    cmin=0, cmax=100, colorbar=dict(title="match reach %"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=False))
    fig.add_trace(go.Scatter(  # 2 — minute reach DIAGNOSTIC
        x=pooled.xpos, y=pooled.c, mode="markers", name="minute reach % (DIAGNOSTIC — over-optimistic)",
        marker=dict(symbol="square", size=7, color=pooled.reach_pooled * 100, colorscale="YlOrBr",
                    cmin=0, cmax=100, colorbar=dict(title="minute reach %"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=False))
    fig.add_trace(go.Scatter(  # 3 — minute-vs-match gap DIAGNOSTIC (winner-contamination map)
        x=pooled.xpos, y=pooled.c, mode="markers", name="minute−match gap pp (winner contamination)",
        marker=dict(symbol="square", size=7, color=(pooled.reach_pooled - pooled.reach_pooled_match) * 100,
                    colorscale="Reds", cmin=0, cmax=40, colorbar=dict(title="gap pp"), line=dict(width=0)),
        text=hov, hoverinfo="text", visible=False))
    ot_mask = [(c, X) in opt_keys for c, X in zip(pooled.c, pooled.X)]
    ot = pooled[ot_mask]
    ot_colors = ["#ff2bd6" if (c, X) in thin else "#ffffff" for c, X in zip(ot.c, ot.X)]
    fig.add_trace(go.Scatter(  # 4 — gated optimum, always visible (magenta = thin match-N)
        x=ot.xpos, y=ot.c, mode="markers",
        name=f"optimal (deepest X, match reach≥{reach_floor*100:.0f}%; magenta=thin <{THIN_MATCH_N})",
        marker=dict(symbol="square-open", size=11, color="rgba(0,0,0,0)", line=dict(width=2, color=ot_colors)),
        text=[h for h, k in zip(hov, ot_mask) if k], hoverinfo="text", visible=True))

    V = lambda i: [j == i for j in range(4)] + [True]
    fig.update_layout(
        title=(f"LAYER 2 — sand-pooled, SETTLEMENT-BLIND exit gauge · MATCH-WEIGHTED deploy gate "
               f"({category}, {df.ticker.nunique()} tickers, k±{kmax})<br>"
               f"<sub>reach = traded-forward to c+X (no winner/loser split) · canonical = match-weighted "
               f"(one match one vote) · ★ = deepest X with match reach ≥ {reach_floor*100:.0f}% · "
               f"DEPLOY color = expected return = reach_match·X − miss·(c−settle) · minute layers DIAGNOSTIC only</sub>"),
        xaxis=dict(title="exit offset slots (centred; reach to the 99 lock)", zeroline=False, showgrid=False),
        yaxis=dict(title="cost-basis cell c (cents)", autorange="reversed", dtick=5, showgrid=False),
        template="plotly_dark", width=1400, height=1150, plot_bgcolor="#0a0a0a",
        updatemenus=[dict(type="buttons", direction="right", x=0, y=1.06, xanchor="left", buttons=[
            dict(label="expected return (DEPLOY)", method="update", args=[{"visible": V(0)}]),
            dict(label="match reach %", method="update", args=[{"visible": V(1)}]),
            dict(label="minute reach (diag)", method="update", args=[{"visible": V(2)}]),
            dict(label="minute−match gap (diag)", method="update", args=[{"visible": V(3)}]),
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
    ap.add_argument("--gate-basis", choices=["match", "minute"], default="match",
                    help="match (DEFAULT, canonical deploy gate) or minute (DIAGNOSTIC only)")
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

    opt.to_csv(os.path.join(os.path.dirname(__file__), "deploy_gated_optima.csv"), index=False)
    n_thin = int((opt.match_N < THIN_MATCH_N).sum())
    print(f"\nDEPLOY optimum — gate_basis={args.gate_basis}, MATCH reach >= {args.reach_floor:.0%} "
          f"({n_thin}/{len(opt)} cells THIN <{THIN_MATCH_N} matches):")
    for r in opt.iloc[::8].itertuples():
        flag = f"  <<THIN(N={int(r.match_N)})" if r.match_N < THIN_MATCH_N else ""
        print(f"  c={int(r.c):2d}  +{int(r.X):2d}  match_reach={r.reach_pooled_match*100:5.1f}%  "
              f"(minute {r.reach_pooled*100:4.0f}%, gap {r.minute_over_optimistic*100:+4.0f}pp)  "
              f"exp_ret={r.exp_ret_match:+6.2f}c  matchN={int(r.match_N)}{flag}")


if __name__ == "__main__":
    main()
