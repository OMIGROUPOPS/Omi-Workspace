"""Apply the EXISTING drift envelope (drift_low_vs_anchor per cell, atlas-consistent N)
to set per-cell per-category maker offsets at a stated REACH target. A rested bid fills
if price VISITS the level -> reach fraction = P(dip >= offset). offset@reach(f) =
quantile(dip, 1-f). Replaces the fixed/deep T47 offsets that miss. Sand-pooled k+-3.
Cross-checks vs current config (entry_table_percell) + flags the deep miss-cells.
Read-only. Validate projected fill against the envelope before any deploy."""
import glob, os
import pandas as pd, numpy as np
SVM = "/root/Omi-Workspace/arb-executor/data/durable/spike_volatility_map"
POL = "/root/Omi-Workspace/arb-executor/docs/policy"
OUT = "/root/Omi-Workspace/arb-executor/analysis/exit_charts"
CATS = {"ATP_MAIN": ("atp_main", 4137), "WTA_MAIN": ("wta_main", 3683),
        "ATP_CHALL": ("atp_chall", 5326), "WTA_CHALL": ("wta_chall", 887)}
REACH_PRIMARY = 0.60   # fill-rate target: rest where price dips >= offset 60% of the time
REACH_REF = 0.50       # median-dip reference (operator's ~50% anchor)
OFFSET_CAP = 8         # never deeper than this (exit is fixed-profit; A43/A52 — depth adds miss not upside)

cur = {}
ot = pd.read_csv(os.path.join(POL, "entry_table_percell.csv"))
for r in ot.itertuples():
    cur[(r.category, int(r.c))] = int(r.bid_offset_cents)

for cat, (slug, atlasN) in CATS.items():
    d = pd.read_parquet(os.path.join(SVM, "%s_drift_envelope.parquet" % slug))
    d["cell"] = d.anchor_cents.round().astype(int).clip(5, 94)
    d = d[(d.drift_low_vs_anchor.notna())]
    print("\n================ %s ================  envelope N=%d  (atlas N=%d) %s" % (
        cat, len(d), atlasN, "MATCH" if abs(len(d) - atlasN) <= 5 else "MISMATCH"))
    rows = []
    for c in range(5, 95):
        pool = d[(d.cell >= c - 3) & (d.cell <= c + 3)]
        dips = pool.drift_low_vs_anchor.to_numpy(float)
        dips = dips[np.isfinite(dips)]
        n = len(dips)
        if n < 5:
            rows.append({"c": c, "n": n, "med_dip": np.nan, "off_reach50": np.nan,
                         "off_reach60": np.nan, "current_offset": cur.get((cat, c)),
                         "cur_fill_pred": np.nan, "new_fill_pred": np.nan}); continue
        med = float(np.median(dips))
        # offset at reach f = quantile(dip, 1-f), clipped to [1, OFFSET_CAP]
        o50 = int(np.clip(round(np.quantile(dips, 1 - REACH_REF)), 1, OFFSET_CAP))
        o60 = int(np.clip(round(np.quantile(dips, 1 - REACH_PRIMARY)), 1, OFFSET_CAP))
        co = cur.get((cat, c))
        cur_fill = float((dips >= co).mean()) if co is not None else np.nan
        new_fill = float((dips >= o60).mean())
        rows.append({"c": c, "n": n, "med_dip": round(med, 1), "off_reach50": o50,
                     "off_reach60": o60, "current_offset": co,
                     "cur_fill_pred": round(cur_fill, 3) if co is not None else np.nan,
                     "new_fill_pred": round(new_fill, 3)})
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "envelope_offsets_%s.csv" % cat), index=False)
    v = out.dropna(subset=["new_fill_pred"])
    print(" cell | med_dip | curOff | reach@curOff | NEWoff(60%) | reach@new | n")
    for c in range(5, 95, 5):
        r = out[out.c == c].iloc[0]
        print("  c%-3d | %5s | %4s | %6s | %5s | %6s | %4d" % (
            c, r.med_dip, r.current_offset, r.cur_fill_pred, r.off_reach60, r.new_fill_pred, int(r.n) if r.n == r.n else 0))
    # deep-cell cross-check
    deep = v[v.current_offset >= 7]
    print("DEEP cells (current offset >=7): %d | mean reach@curOff=%.2f -> mean reach@NEWoff=%.2f" % (
        len(deep), deep.cur_fill_pred.mean() if len(deep) else 0, deep.new_fill_pred.mean() if len(deep) else 0))
    print("spectrum: mean reach@current=%.2f -> mean reach@new(60%%target)=%.2f  | new offset median=%dc (was %dc)" % (
        v.cur_fill_pred.mean(), v.new_fill_pred.mean(), int(v.off_reach60.median()), int(v.current_offset.median())))
