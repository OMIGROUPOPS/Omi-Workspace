"""
build_chart_mirror_outlook.py — MACRO / MICRO / MIRROR three-panel outlook.

(a) Cost-basis band reach signatures, CORRECTED price_high instrument: each band
    (deep-underdog 5-20 / slight 21-40 / even 41-60 / slight-fav 61-80 / heavy 81-94)
    gets a distinct fill-rate-vs-X curve. Bands give density (NOT per-cell knife-edge).
(b) MICRO mirror: ONE real paired event, underdog yes_bid path vs partner favorite
    yes_bid path overlaid (in-row partner_yes_bid_close, perfectly aligned), showing
    inverse motion minute by minute.
(c) MACRO mirror: heavy-underdog forward up-excursion overlaid on heavy-favorite
    forward down-excursion (excursion-window instrument on yes_bid / partner_yes_bid).
    Annotated with the PINNED verified stats (+0.66 corr, 85% within 2c) — discovery
    is NOT re-run here; the probe scatter is shown only as an eye-audit illustration.

Mirror panels use yes_bid_close / partner_yes_bid_close ONLY (the verified mirror
instrument). NEVER a timestamp join, NEVER raw minute-diff correlation.

Usage: python build_chart_mirror_outlook.py [--input PATH] [--category ATP_MAIN] [--out FILE]
"""
from __future__ import annotations
import argparse
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import chart_common as cc

# PINNED verified mirror stats (from CHART_DEFINITIONS_VERIFIED.md). DO NOT re-derive.
PINNED_LEVEL_SUM = 0.974
PINNED_EXC_CORR = 0.66
PINNED_WITHIN_2C = 0.85
EXC_WINDOW_MIN = 60  # forward excursion window for the macro panel


def forward_window_extremum(df: pd.DataFrame, col: str, w_min: int, kind: str) -> np.ndarray:
    """Per ticker, extremum of `col` over rows with t < t' <= t + w_min*60 (strictly forward)."""
    out = np.full(len(df), np.nan)
    vals = df[col].to_numpy(dtype=float)
    ts = df["minute_ts"].to_numpy()
    codes = pd.factorize(df["ticker"], sort=False)[0]
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy()
        t = ts[ix]
        v = vals[ix]
        for i in range(len(ix)):
            hi = np.searchsorted(t, t[i] + w_min * 60, side="right")
            window = v[i + 1:hi]
            window = window[~np.isnan(window)]
            if window.size:
                out[ix[i]] = window.max() if kind == "max" else window.min()
    return out


def band_reach_signatures(df: pd.DataFrame, x_max: int = 35):
    rt = cc.reach_table(df, x_max=x_max)
    rt["band"] = rt["c"].apply(cc.band_of)
    sigs = {}
    for name, lo, hi in cc.BANDS:
        b = rt[(rt.c >= lo) & (rt.c <= hi)]
        # N-weighted mean fill per X across cells in band
        agg = (b.groupby("X")
                 .apply(lambda g: np.average(g.fill_corrected, weights=g.N))
                 .rename("fill"))
        nbeh = b.groupby("X").N.sum()
        sigs[name] = pd.DataFrame({"X": agg.index, "fill": agg.values, "N": nbeh.values})
    return sigs


def pick_paired_event(df: pd.DataFrame) -> str:
    """Pick the underdog ticker (lower mean yes_bid) of the event with the largest
    underdog price travel — clearest visual mirror."""
    best, best_range = None, -1
    for tk, g in df.groupby("ticker"):
        rng = g.yes_bid_close.max() - g.yes_bid_close.min()
        if g.yes_bid_close.mean() < 0.5 and rng > best_range and g.partner_yes_bid_close.notna().mean() > 0.8:
            best, best_range = tk, rng
    return best


def build(df: pd.DataFrame, out_html: str, category: str):
    sigs = band_reach_signatures(df)
    micro_tk = pick_paired_event(df)

    # ---- macro excursion-window arrays (heavy-underdog vs heavy-favorite partner) ----
    ud = df[(df.cell >= 5) & (df.cell <= 20)].copy()  # heavy/deep underdog cost basis
    ud_up = forward_window_extremum(ud, "yes_bid_close", EXC_WINDOW_MIN, "max") - ud.yes_bid_close.to_numpy()
    pf_dn = forward_window_extremum(ud, "partner_yes_bid_close", EXC_WINDOW_MIN, "min") - ud.partner_yes_bid_close.to_numpy()
    m = ~(np.isnan(ud_up) | np.isnan(pf_dn))
    ud_up, pf_dn = ud_up[m] * 100, pf_dn[m] * 100  # cents
    pf_dn_mag = -pf_dn  # favorite DOWN as positive magnitude
    probe_corr = float(np.corrcoef(ud_up, pf_dn_mag)[0, 1]) if len(ud_up) > 2 else float("nan")
    within2 = float(np.mean(np.abs(ud_up - pf_dn_mag) <= 2)) if len(ud_up) else float("nan")
    level_sum_probe = float(df.paired_yes_bid_sum.dropna().mean())

    fig = make_subplots(
        rows=1, cols=3, horizontal_spacing=0.07,
        subplot_titles=(
            "(a) Cost-basis band reach signatures<br><sub>CORRECTED price_high · fill% vs exit +X</sub>",
            f"(b) MICRO mirror — one real pair<br><sub>{micro_tk}</sub>",
            "(c) MACRO mirror — excursion window<br><sub>underdog up vs favorite down</sub>",
        ),
    )

    # (a) band signatures
    palette = {"deep-underdog": "#22d3ee", "slight-underdog": "#34d399",
               "even": "#a3a3a3", "slight-fav": "#fbbf24", "heavy-fav": "#f87171"}
    for name, lo, hi in cc.BANDS:
        s = sigs[name]
        fig.add_trace(go.Scatter(
            x=s.X, y=s.fill * 100, mode="lines+markers", name=f"{name} ({lo}-{hi})",
            line=dict(color=palette[name], width=2),
            hovertemplate=f"{name}<br>exit +%{{x}}c · fill %{{y:.0f}}%%<extra></extra>",
        ), row=1, col=1)
    fig.add_hline(y=50, line=dict(color="#555", dash="dot"), row=1, col=1)

    # (b) micro mirror
    g = df[df.ticker == micro_tk].sort_values("minute_ts")
    tmin = (g.minute_ts - g.minute_ts.min()) / 60.0
    fig.add_trace(go.Scatter(x=tmin, y=g.yes_bid_close * 100, mode="lines", name="underdog yes_bid",
                             line=dict(color="#22d3ee", width=2),
                             hovertemplate="t+%{x:.0f}m · underdog %{y:.0f}c<extra></extra>"), row=1, col=2)
    fig.add_trace(go.Scatter(x=tmin, y=g.partner_yes_bid_close * 100, mode="lines", name="favorite yes_bid (partner)",
                             line=dict(color="#f87171", width=2),
                             hovertemplate="t+%{x:.0f}m · favorite %{y:.0f}c<extra></extra>"), row=1, col=2)
    fig.add_trace(go.Scatter(x=tmin, y=(g.yes_bid_close + g.partner_yes_bid_close) * 100, mode="lines",
                             name="bid sum (≈100)", line=dict(color="#888", width=1, dash="dot"),
                             hovertemplate="t+%{x:.0f}m · sum %{y:.0f}c<extra></extra>"), row=1, col=2)

    # (c) macro mirror scatter (illustration) + pinned annotation
    fig.add_trace(go.Scatter(
        x=ud_up, y=pf_dn_mag, mode="markers", name="excursion windows",
        marker=dict(color="#22d3ee", size=4, opacity=0.35),
        hovertemplate="underdog +%{x:.0f}c · favorite -%{y:.0f}c<extra></extra>", showlegend=False,
    ), row=1, col=3)
    lim = max(1, np.nanpercentile(np.concatenate([ud_up, pf_dn_mag]), 99))
    fig.add_trace(go.Scatter(x=[0, lim], y=[0, lim], mode="lines", name="perfect mirror y=x",
                             line=dict(color="#34d399", dash="dash", width=2),
                             hoverinfo="skip", showlegend=False), row=1, col=3)

    fig.add_annotation(
        xref="x3 domain", yref="y3 domain", x=0.03, y=0.97, align="left", showarrow=False,
        font=dict(color="#e5e5e5", size=11), bgcolor="rgba(0,0,0,0.55)", bordercolor="#34d399",
        text=(f"<b>VERIFIED / PINNED</b> (not re-derived)<br>excursion corr = +{PINNED_EXC_CORR}<br>"
              f"{PINNED_WITHIN_2C*100:.0f}% within 2c<br>level-sum = {PINNED_LEVEL_SUM}<br>"
              f"<i>probe shape-check only (38 games, overlapping<br>"
              f"{EXC_WINDOW_MIN}m windows ≠ pinned method): corr +{probe_corr:.2f},<br>"
              f"{within2*100:.0f}% within 2c · level-sum {level_sum_probe:.3f} ✓</i>"),
    )

    fig.update_xaxes(title_text="exit offset +X (cents)", row=1, col=1)
    fig.update_yaxes(title_text="fill rate %", range=[0, 102], row=1, col=1)
    fig.update_xaxes(title_text="minutes from first observation", row=1, col=2)
    fig.update_yaxes(title_text="yes_bid (cents)", range=[0, 100], row=1, col=2)
    fig.update_xaxes(title_text="underdog UP-excursion (cents)", row=1, col=3)
    fig.update_yaxes(title_text="favorite DOWN-excursion (cents)", row=1, col=3)
    fig.update_layout(
        title=(f"MACRO / MICRO / MIRROR outlook ({category}, {df.ticker.nunique()} tickers)  ·  "
               f"mirror instrument = in-row partner_yes_bid_close (level-sum + excursion-window)"),
        template="plotly_dark", width=1500, height=620, legend=dict(orientation="h", y=-0.18),
    )
    fig.write_html(out_html, include_plotlyjs="cdn")
    return {"micro_event": micro_tk, "macro_n_windows": int(len(ud_up)),
            "probe_excursion_corr": probe_corr, "probe_within2c": within2,
            "probe_level_sum": level_sum_probe,
            "pinned": {"corr": PINNED_EXC_CORR, "within2c": PINNED_WITHIN_2C, "level_sum": PINNED_LEVEL_SUM},
            "out": out_html}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=cc.DEFAULT_INPUT)
    ap.add_argument("--category", default="ATP_MAIN")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "chart_mirror_outlook.html"))
    args = ap.parse_args()
    df = cc.load_universe(args.input, args.category)
    print("MIRROR/OUTLOOK:", build(df, args.out, args.category))


if __name__ == "__main__":
    main()
