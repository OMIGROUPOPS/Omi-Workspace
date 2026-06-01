#!/usr/bin/env python3
"""Entry-phase conclusion — per-match maker-entry ROC lift on the locked exit surface.

THE HONEST ENTRY NUMBER. A per-match walk over the premarket tape that respects
the paired-binary MIRROR (per match exactly ONE leg's resting maker bid fills —
the dipping leg, disproportionately the low-exit-ROC favorite) and uses the T47
net-optimal SHALLOW offsets (docs/policy/per_regime_offsets_v2.csv), NOT a deep
f x D argmax. Realized lift is ~+3pp, roughly a THIRD of the inflated cell-average
(+8pp): the cell-average double-counted the mirror by letting the book implicitly
collect the cheap cell's high exit-ROC AND the favorite cell's high entry-fill on
DIFFERENT matches, when per match only one leg ever fills.

============================ BASELINE RECONCILIATION ============================
The four carried-forward per-category baselines were on TWO DIFFERENT FRAMES:

  * WTA_MAIN 9.7, ATP_CHALL 9.5, WTA_CHALL 6.8  reconcile EXACTLY to the
    simple-mean of per-cell roc_match in deploy_gated_optima[_CAT].csv
    (the per-cell EXIT-ROC frame; verified to 0.1pp).

  * ATP_MAIN "10.5" does NOT live on that frame. On the SAME simple-mean exit-ROC
    frame ATP_MAIN = 27.1% (right-skewed: median 14.6, match-wt 28.0 — a handful
    of cheap cells with huge X/c inflate the mean). No honest trim of ATP_MAIN's
    exit table reaches 10.5 (c-floors give 12-17; 10% winsor 22; only an arbitrary
    capW x 0.66 hits ~10.3). The 10.5 is instead ATP_MAIN's per-category
    capital-weighted v4 NET DEPLOYABLE ROI = 10.28% (path_b_v4_cell_optimum;
    corpus-blended v3-net 10.51% / 10.70%, v4 11.73% — ROADMAP T47/T48). That net
    is a different object: entry + atlas exit + miss-fallback - 1c fee,
    capital-weighted — and it ALREADY CONTAINS the maker-entry improvement. So the
    +2.7pp entry lift here must NOT be stacked onto 10.5 (it would double-count
    entry). On the consistent exit-ROC frame, ATP_MAIN blended = 27.1 -> ~29.8.

The clean three (operator-stated): WTA_MAIN 9.7->~10.5, ATP_CHALL 9.5->~11.2,
WTA_CHALL 6.8->~9.4 — i.e. simple-mean exit-ROC + the per-match realized lift.
=================================================================================

Walk mechanics: premarket window time_to_match_start in (1,240]; volume-onset =
last minute with trade_count>=10 within tts<=60 (the T51 live-onset analog,
delay-robust); anchor a = last REAL traded price_close before onset; cell
c=round(100a) in [5,94]; offset from per_regime_offsets_v2 by anchor regime;
filled iff min premarket TRADED price_low*100 <= a-offset (honest traded prints
only — no quote phantoms). Per leg exit value er = exp_ret_match[c] from
deploy_gated_optima. mk_ret = er+off if filled else er; mk_cap = a-off if filled
else a. base_roc = sum(er)/sum(a) (capital-weighted over the actual leg
population); real_roc = sum(mk_ret)/sum(mk_cap); lift = real-base (frame-robust:
a delta on one population). Read-only / analysis — touches no table the bot loads.

Run (data lives on the VPS): cd arb-executor && python3 analysis/exit_charts/entry_lift_permatch.py
Emits: analysis/exit_charts/entry_lift_permatch_by_category.csv
"""
import os, glob, csv
import pandas as pd, numpy as np

ROOT = os.environ.get("OMI_ARB_ROOT") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EC = os.path.join(ROOT, "analysis", "exit_charts")
PMU = os.path.join(ROOT, "data", "durable", "per_minute_universe")

REG = pd.read_csv(os.path.join(ROOT, "docs", "policy", "per_regime_offsets_v2.csv"))
OFF = {(r.category, r.anchor_regime): float(r.bid_offset_cents) for r in REG.itertuples()}
OPTF = {"ATP_MAIN": "deploy_gated_optima.csv", "WTA_MAIN": "deploy_gated_optima_WTA_MAIN.csv",
        "ATP_CHALL": "deploy_gated_optima_ATP_CHALL.csv", "WTA_CHALL": "deploy_gated_optima_WTA_CHALL.csv"}
# Operator-carried baselines + frame provenance (see header).
STATED = {"ATP_MAIN": 10.5, "WTA_MAIN": 9.7, "ATP_CHALL": 9.5, "WTA_CHALL": 6.8}
# ATP_MAIN net-deploy is a DIFFERENT frame (capital-wt v4 net, entry-inclusive).
NET_DEPLOY = {"ATP_MAIN": 10.28, "WTA_MAIN": 13.07, "ATP_CHALL": 10.90, "WTA_CHALL": 18.03}
CELLAVG = {"ATP_MAIN": 8.2, "WTA_MAIN": 7.8, "ATP_CHALL": 6.7, "WTA_CHALL": 8.4}  # inflated cell-avg lift (pp)

def regime(c):
    for hi, nm in [(15, "r05_14"), (25, "r15_24"), (35, "r25_34"), (45, "r35_44"), (55, "r45_54"),
                   (65, "r55_64"), (75, "r65_74"), (85, "r75_84"), (100, "r85_94")]:
        if c < hi:
            return nm

COLS = ["ticker", "event_ticker", "category", "minute_ts", "time_to_match_start_min",
        "price_close", "price_low", "trade_count_in_minute", "minute_has_trade"]
LIVE = 10  # trade_count burst threshold defining live-onset
NEAR = 60  # only treat a burst within tts<=60 as the onset

rows = []
hdr = ("cat        exit-smean  exit-capW   cell-avg-lift  PERMATCH-lift  blended(smean)  | "
       "fav_fill udog_fill | exitROC(filled vs unfilled)")
print(hdr)
for cat, optf in OPTF.items():
    opt = pd.read_csv(os.path.join(EC, optf))
    EXIT = {int(r.c): float(r.exp_ret_match) for r in opt.itertuples()}
    # exit-ROC frame consistent across all four categories (simple-mean of roc_match)
    exit_smean = float(opt["roc_match"].astype(float).mean()) * 100.0

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
    tts = df.time_to_match_start_min.to_numpy(float); pc = df.price_close.to_numpy(float)
    plo = df.price_low.to_numpy(float); tcnt = df.trade_count_in_minute.to_numpy(float)
    hastr = np.asarray(df.minute_has_trade.to_numpy(), bool); ev = df.event_ticker.to_numpy()
    codes = pd.factorize(df.ticker, sort=False)[0]

    legs = []  # (event, c, a, off, filled, exitret)
    for _, idx in pd.Series(np.arange(len(df))).groupby(codes):
        ix = idx.to_numpy(); t = tts[ix]; pcx = pc[ix]; plox = plo[ix]
        win = (t >= 1) & (t <= 240)
        if not win.any():
            continue
        burst = (tcnt[ix] >= LIVE) & (t <= NEAR); onset = t[burst].max() if burst.any() else -1e9
        pm = win & (t > onset); has = pm & hastr[ix] & np.isfinite(pcx)
        if not has.any():
            continue
        a = round(pcx[np.where(has)[0][np.argmin(t[has])]] * 100.0)
        if a < 5 or a > 94 or int(a) not in EXIT:
            continue
        off = OFF.get((cat, regime(a)))
        if off is None:
            continue
        lowtr = plox[pm][np.isfinite(plox[pm])] * 100.0
        minlow = lowtr.min() if len(lowtr) else 999
        filled = minlow <= (a - off)
        legs.append((ev[ix][0], int(a), float(a), float(off), bool(filled), float(EXIT[int(a)])))

    L = pd.DataFrame(legs, columns=["event", "c", "a", "off", "filled", "er"])
    L["mk_ret"] = np.where(L.filled, L.er + L.off, L.er)
    L["mk_cap"] = np.where(L.filled, L.a - L.off, L.a)
    base_roc = L.er.sum() / L.a.sum() * 100          # capital-weighted exit-ROC over the leg population
    real_roc = L.mk_ret.sum() / L.mk_cap.sum() * 100
    lift = real_roc - base_roc                        # frame-robust delta
    favf = L[L.c > 50].filled.mean() * 100; udf = L[L.c < 50].filled.mean() * 100
    er_f = L[L.filled].er.mean(); er_u = L[~L.filled].er.mean()
    blended_smean = exit_smean + lift                 # operator's construction: stated baseline + realized lift

    print("%-9s  %7.2f%%  %7.2f%%   + %4.1f       + %5.2f pp     %7.2f%%       | %5.1f%%  %5.1f%%  | %.2f vs %.2f" % (
        cat, exit_smean, base_roc, CELLAVG[cat], lift, blended_smean, favf, udf, er_f, er_u))
    rows.append({
        "category": cat, "n_legs": len(L), "n_matches": L.event.nunique(),
        "exit_roc_simplemean_pct": round(exit_smean, 2),     # consistent frame across all 4
        "stated_baseline_pct": STATED[cat],
        "exit_roc_capW_base_pct": round(base_roc, 2),         # walk base (capital-wt)
        "permatch_realized_lift_pp": round(lift, 2),
        "blended_simplemean_pct": round(blended_smean, 2),    # baseline + lift (the clean number)
        "blended_capW_pct": round(real_roc, 2),
        "inflated_cellavg_lift_pp": CELLAVG[cat],
        "fav_fill_pct": round(favf, 1), "udog_fill_pct": round(udf, 1),
        "exitroc_filled": round(float(er_f), 2), "exitroc_unfilled": round(float(er_u), 2),
        "net_deploy_roi_pct": NET_DEPLOY[cat],                # capital-wt v4 net (entry-INCLUSIVE; do not stack lift)
    })

# ATP_MAIN reconciliation note as a trailing comment row for downstream readers
out = os.path.join(EC, "entry_lift_permatch_by_category.csv")
fields = list(rows[0].keys())
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print("\nwrote", out)
print("FRAME NOTE: stated_baseline reconciles to exit_roc_simplemean for WTA_MAIN/ATP_CHALL/WTA_CHALL;")
print("ATP_MAIN stated 10.5 = net_deploy_roi (entry-inclusive, capital-wt) NOT exit-ROC -> on the consistent")
print("exit-ROC frame ATP_MAIN baseline = %.1f%%, blended = %.1f%%." % (
    rows[0]["exit_roc_simplemean_pct"], rows[0]["blended_simplemean_pct"]))
