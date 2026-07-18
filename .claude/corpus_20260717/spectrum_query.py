#!/usr/bin/env python3
"""PHASE B — spectrum query tool: the range spectrum, queryable by posture
+ journey vector. Category is a HARD filter (populations never pool).

Usage:
  python3 analysis/spectrum_query.py --cat ITF_W [--side dog|fav]
      [--shape dip_recover] [--anchor-lo 26 --anchor-hi 50]
      [--min-prints-per-min 0.05] [--wake-before-min 240]
      [--edge official_actual|onset_snapshot_est|onset_ticks_est]
      [--stats | --events | --limit N]

Side: fav = the leg whose anchor >= sibling's; dog = the other. --stats
prints the cohort's empirical distributions (n first — thin is honest):
orientation (rose/fell/flat from net), low-depth-below-anchor
distribution, low timing, seesaw corr. This is the Phase C engine's seed
query path; Phase C adds journey-so-far re-selection.
"""
import argparse, json, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "state/range_spectrum_v1.jsonl"

p = argparse.ArgumentParser()
p.add_argument("--cat", required=True)
p.add_argument("--side", choices=["dog", "fav"])
p.add_argument("--shape")
p.add_argument("--anchor-lo", type=int)
p.add_argument("--anchor-hi", type=int)
p.add_argument("--min-prints-per-min", type=float)
p.add_argument("--wake-before-min", type=float)
p.add_argument("--edge")
p.add_argument("--stats", action="store_true")
p.add_argument("--events", action="store_true")
p.add_argument("--limit", type=int, default=20)
a = p.parse_args()

rows = []
for line in open(SPEC):
    r = json.loads(line)
    if r["cat"] != a.cat:
        continue
    if a.edge and r.get("edge_src") != a.edge:
        continue
    legs = {k: v for k, v in r["legs"].items() if v.get("shape")}
    if len(legs) < (2 if a.side else 1):
        continue
    items = list(legs.items())
    if a.side and len(items) == 2:
        items.sort(key=lambda kv: kv[1]["anchor"], reverse=True)
        items = [items[0]] if a.side == "fav" else [items[1]]
    for leg, v in items:
        if a.shape and v["shape"] != a.shape:
            continue
        if a.anchor_lo is not None and v["anchor"] < a.anchor_lo:
            continue
        if a.anchor_hi is not None and v["anchor"] > a.anchor_hi:
            continue
        if (a.min_prints_per_min is not None
                and v["prints_per_min"] < a.min_prints_per_min):
            continue
        if (a.wake_before_min is not None
                and (v.get("wake_trade_tmin_min") or 0) < a.wake_before_min):
            continue
        rows.append((r, leg, v))

print("cohort n = %d  (cat %s, hard partition)" % (len(rows), a.cat))
if not rows:
    print("THIN: empty cohort — the voice says thin, never padded.")
    raise SystemExit(0)
if a.stats:
    nets = [v["net"] for _, _, v in rows]
    rose = sum(1 for x in nets if x >= 3)
    fell = sum(1 for x in nets if x <= -3)
    dips = sorted(v["anchor"] - v["low"] for _, _, v in rows)
    lows_t = sorted(v["low_tmin_min"] for _, _, v in rows)
    shapes = {}
    for _, _, v in rows:
        shapes[v["shape"]] = shapes.get(v["shape"], 0) + 1
    corr = [r.get("seesaw_corr") for r, _, _ in rows
            if r.get("seesaw_corr") is not None]
    def d(v):
        v = sorted(v)
        return ("median %.1f · p25 %.1f · p75 %.1f · p95 %.1f"
                % (statistics.median(v), v[len(v)//4],
                   v[3*len(v)//4], v[int(0.95*len(v))]))
    print("orientation: rose %d (%.0f%%) · fell %d (%.0f%%) · flat %d"
          % (rose, 100.0*rose/len(rows), fell, 100.0*fell/len(rows),
             len(rows)-rose-fell))
    print("shapes:", shapes)
    print("dip below anchor (c):", d(dips),
          "· share >=3c: %.0f%%"
          % (100.0*sum(1 for x in dips if x >= 3)/len(dips)))
    print("low timing (T-min):", d(lows_t))
    if corr:
        print("seesaw corr: %s (n=%d)" % (d(corr), len(corr)))
elif a.events:
    for r, leg, v in rows[:a.limit]:
        print(r["event"], leg, v["shape"], "anchor", v["anchor"],
              "low", v["low"], "@T-%.0fm" % v["low_tmin_min"],
              "close", v["close"])
