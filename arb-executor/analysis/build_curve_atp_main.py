"""
Reconstruct the HONEST per-offset EV/hit/ROI curve for every cent, directly
from the spike corpus (actual tape), priced at each cent's own cost basis.

For entry cent c and target offset +X:
  - A position "hits" if its peak (raw_max) reached c+X  -> capture +X.
  - If it misses, it rides to settlement: win -> (100-c), loss -> -c.
  - EV(c,X) = mean PnL over all positions at cent c.

Validated: 89c argmax = +9, EV 4.92, 95.8% hit -> matches locked achievable.
"""
import pandas as pd, numpy as np, json

CAT = "atp_main"
df = pd.read_parquet(f"../data/durable/spike_volatility_map/{CAT}_spike_perN.parquet")
df["cent"] = (df["anchor_price"] * 100).round().astype(int)
df["peak"] = (df["raw_max"] * 100).round().astype(int)
df["settle"] = df["settlement_value"].astype(int)

surf = json.load(open(f"../data/durable/exit_atlas_v1/{CAT}_pooled_surface_v3.json"))
ach = {r["c"]: r["achievable"] for r in surf["rows"]}

out = {}
for c in range(5, 95):
    sub = df[df["cent"] == c]
    n = len(sub)
    rec = {"c": c, "n": int(n), "curve": []}
    if n > 0:
        peak = sub["peak"].values
        settle = sub["settle"].values
        for X in range(1, 100 - c):
            target = c + X
            hit_mask = peak >= target
            nhit = int(hit_mask.sum())
            hitrate = nhit / n
            miss_settle = settle[~hit_mask]
            miss_pnl = np.where(miss_settle == 1, 100 - c, -c).sum()
            ev = (nhit * X + miss_pnl) / n
            roi = ev / c
            rec["curve"].append({
                "X": X, "ev": round(float(ev), 3),
                "hit": round(float(hitrate * 100), 1),
                "roi": round(float(roi * 100), 1),
            })
    # attach the locked achievable choice for this cent
    a = ach.get(c, {})
    rec["achievable"] = {
        "bestX": a.get("bestX"), "ev": round(a.get("ev", 0), 2),
        "hit": round((a.get("hit", 0) * 100) if a.get("hit", 0) <= 1 else a.get("hit", 0), 1),
        "roi": round((a.get("roi", 0) * 100) if a.get("roi", 0) <= 2 else a.get("roi", 0), 1),
        "basis": a.get("basis"),
    }
    out[c] = rec

json.dump(out, open("curve_atp_main.json", "w"))
print("wrote curve_atp_main.json for", len([c for c in out if out[c]['n']>0]), "cents with data")
# quick sanity: where does corpus argmax disagree with achievable.bestX?
dis = 0
for c in range(5, 95):
    r = out[c]
    if r["n"] == 0 or not r["curve"]: continue
    amax = max(r["curve"], key=lambda z: z["ev"])["X"]
    if r["achievable"]["bestX"] is not None and amax != r["achievable"]["bestX"]:
        dis += 1
print("cents where corpus-argmax != achievable.bestX:", dis, "/ 90")
