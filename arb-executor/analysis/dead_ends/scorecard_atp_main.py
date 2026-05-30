#!/usr/bin/env python3
"""ATP_MAIN full per-cent scorecard. Each cell's config = its OWN shoulder offset
(70% of peak EV, read from the pooled/converted cells grid where the relative eff-N
move is already priced at THIS cent's own cost basis -- apples->oranges done) plus
its own economics. Fixed sizing = 10 contracts/fill. Frequency from 317-day corpus.

Emits scorecard_atp_main.json (per-cent) + prints summary table.
"""
import json
from collections import defaultdict
import pandas as pd
import numpy as np

CAT = "atp_main"
SIZE = 10            # fixed contracts per fill
THR = 0.70

# --- frequency from real tape ---
df = pd.read_parquet(f"data/durable/spike_volatility_map/{CAT}_spike_perN.parquet")
df["cent"] = (df["anchor_price"] * 100).round().astype(int)
ts = pd.to_datetime(df["anchor_ts"])
SPAN = (ts.max() - ts.min()).days
freq = df["cent"].value_counts().to_dict()

# --- pooled/converted EV grid (oranges) ---
s = json.load(open(f"data/durable/exit_atlas_v1/{CAT}_pooled_surface_v3.json"))
gE = defaultdict(dict); gH = defaultdict(dict); gR = defaultdict(dict)
for cell in s["cells"]:
    gE[cell["c"]][cell["R"]] = cell["ev"]
    gH[cell["c"]][cell["R"]] = cell["hit"]
    gR[cell["c"]][cell["R"]] = cell["roi"]
rows = {r["c"]: r for r in s["rows"]}


def config(c):
    g = gE[c]
    if not g:
        return None
    peak = max(g.values())
    if peak <= 0:
        return None                       # gate: no profitable exit
    R = min(R for R, ev in g.items() if ev >= THR * peak)  # cent's OWN shoulder
    ev = g[R]; hit = gH[c][R]; roi = gR[c][R]
    fpd = freq.get(c, 0) / SPAN           # fills/day (real)
    r = rows.get(c, {})
    # daily/total PnL at fixed SIZE contracts; EV is cents/contract
    daily_pnl_c = ev * fpd * SIZE
    total_pnl_c = ev * freq.get(c, 0) * SIZE
    capital_c = c * fpd * SIZE
    daily_roi = 100 * daily_pnl_c / capital_c if capital_c > 0 else 0.0
    return {
        "c": c, "exit_offset": R, "peak_offset": max(g, key=g.get),
        "ev_per_trade_c": round(ev, 3), "hit_pct": round(hit, 1),
        "roi_pct": round(roi, 1), "fills_per_day": round(fpd, 3),
        "fills_total": int(freq.get(c, 0)),
        "daily_pnl_c": round(daily_pnl_c, 3), "total_pnl_c": round(total_pnl_c, 1),
        "daily_roi_pct": round(daily_roi, 2),
        "cost_basis_c": c, "size": SIZE,
        "ownN": r.get("ownN"), "effN": round(r.get("effN", 0), 1) if r.get("effN") else None,
        "basis": (r.get("achievable") or {}).get("basis"),
    }


def build(cents):
    out = []
    for c in cents:
        cf = config(c)
        out.append(cf if cf else {"c": c, "exit_offset": None, "skip": True})
    return out

LEAD = list(range(55, 90)); DOG = list(range(10, 45))
result = {"category": CAT.upper(), "size": SIZE, "span_days": SPAN,
          "threshold": THR, "underdog": build(DOG), "leader": build(LEAD)}
json.dump(result, open(f"analysis/scorecard_{CAT}.json", "w"), indent=1)

# summary
def totals(arr):
    t = [x for x in arr if not x.get("skip")]
    return (sum(x["daily_pnl_c"] for x in t), sum(x["total_pnl_c"] for x in t),
            np.mean([x["hit_pct"] for x in t]), np.mean([x["roi_pct"] for x in t]),
            len(t), len(arr) - len(t))

for name, arr in [("UNDERDOG", result["underdog"]), ("LEADER", result["leader"])]:
    dp, tp, h, r, n, sk = totals(arr)
    print(f"{name}: {n} trade / {sk} skip | daily PnL {dp:.1f}c/day | "
          f"total {tp/100:.2f}$ over {SPAN}d | avg hit {h:.0f}% | avg ROI {r:.0f}%")
print(f"wrote analysis/scorecard_{CAT}.json")
