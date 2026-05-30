"""
Build a CORRECTED surface JSON per category: identical to the locked
{cat}_pooled_surface_v3.json, EXCEPT the `cells` grid is replaced by the
corpus-reconstructed GROUND-TRUTH grid (own-cost-basis EV/hit/ROI per (c,R)),
which matches achievable.bestX on 82/90 cents. The broken relative-trajectory
`cells` grid is discarded.

For entry cent c and target offset R (=+X):
  - position "hits" if its peak (raw_max*100) >= c+R  -> capture +R
  - else rides to settlement: win -> (100-c), loss -> -c
  - EV = mean PnL; hit = P(peak>=c+R); roi = EV/c*100

All other keys (meta, rows, achievable, achievableLocked, finest) are preserved
verbatim, so the existing tooltip provenance (neighbors, basis, locked ref)
still works. Output: {cat}_corrected_surface_v3.json
"""
import pandas as pd, numpy as np, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ATLAS = ROOT / "data" / "durable" / "exit_atlas_v1"
SPIKE = ROOT / "data" / "durable" / "spike_volatility_map"

CATS = ["atp_main", "atp_chall", "wta_main", "wta_chall"]


def build_cells(df):
    df = df.copy()
    df["cent"] = (df["anchor_price"] * 100).round().astype(int)
    df["peak"] = (df["raw_max"] * 100).round().astype(int)
    df["settle"] = df["settlement_value"].astype(int)
    cells = []
    for c in range(5, 95):
        sub = df[df["cent"] == c]
        n = len(sub)
        if n == 0:
            continue
        peak = sub["peak"].values
        settle = sub["settle"].values
        for R in range(1, 100 - c):
            target = c + R
            hit_mask = peak >= target
            nhit = int(hit_mask.sum())
            hitrate = nhit / n
            miss_settle = settle[~hit_mask]
            miss_pnl = np.where(miss_settle == 1, 100 - c, -c).sum()
            ev = (nhit * R + miss_pnl) / n
            roi = ev / c * 100.0
            cells.append({
                "c": int(c), "R": int(R),
                "ev": round(float(ev), 4),
                "hit": round(float(hitrate * 100), 2),
                "roi": round(float(roi), 3),
                "n": int(n),
            })
    return cells


for cat in CATS:
    surf_path = ATLAS / f"{cat}_pooled_surface_v3.json"
    spike_path = SPIKE / f"{cat}_spike_perN.parquet"
    if not surf_path.exists() or not spike_path.exists():
        print(f"SKIP {cat}: missing input"); continue
    surf = json.loads(surf_path.read_text())
    df = pd.read_parquet(spike_path)
    cells = build_cells(df)
    surf["cells"] = cells
    surf.setdefault("meta", {})["cellsSource"] = "corpus-ground-truth (own-cost-basis); broken relative grid discarded"
    out = ATLAS / f"{cat}_corrected_surface_v3.json"
    out.write_text(json.dumps(surf, separators=(",", ":")))
    # validation: corpus-argmax vs achievable.bestX agreement
    ach = {r["c"]: r["achievable"] for r in surf["rows"]}
    from collections import defaultdict
    gE = defaultdict(dict)
    for cl in cells:
        gE[cl["c"]][cl["R"]] = cl["ev"]
    agree = 0; total = 0
    for c, g in gE.items():
        if not g:
            continue
        total += 1
        amax = max(g, key=lambda r: g[r])
        if ach.get(c, {}).get("bestX") == amax:
            agree += 1
    print(f"{cat}: {len(cells)} cells, argmax==achievable on {agree}/{total} cents -> {out.name}")
