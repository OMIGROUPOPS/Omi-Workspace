#!/usr/bin/env python3
# LOOP 6 ADDENDUM — THE SECOND GAUGE. Post-pass over holdout with the
# CONVERGED policies: every dual scored BOTH ways — (a) the delta bar as
# ruled; (b) combined cost, tiers <=93 / <=95 / <=97 / >97 with % per
# tier, per band-pair and portfolio. FLAG (never silent-seal): delta bar
# clears while >97 share exceeds 10%.
import json
from collections import defaultdict
from pathlib import Path
import importlib.util
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "l6", str(ROOT / "analysis/loop6_frontier.py"))
# reuse loop6's loaders WITHOUT re-running its drill: import its module
# namespace up to the seed (the drill loop guards on __main__? it does
# not — so replicate the tiny bits instead of importing).
POL = json.loads((ROOT / "state/policy_tables_v1.json").read_text())["policies"]
BMAP = json.loads((ROOT / "state/band_map_v1.json").read_text())
DRIFT = json.loads((ROOT / "state/drift_surfaces_v1.json").read_text())
RECOG = DRIFT.get("recognition", {})
SURF = DRIFT["bands"]

def dband(cat, a):
    c = BMAP["cats"].get(cat)
    if not c or c.get("thin"):
        return None
    fl = [b for b in c["bands"] if b["direction"] == "flat"] or c["bands"]
    return min(fl, key=lambda b: abs(b["anchor_med"] - a))["band"]

def pbk(a, n, d):
    ab = "a25" if a <= 25 else "a50" if a <= 50 else "a75" if a <= 75 else "a95"
    nb = ("dn10" if n <= -10 else "dn3" if n <= -3 else
          "flat" if n < 3 else "up3" if n < 10 else "up10")
    return ab + "|" + nb + "|" + ("d0" if d <= 2 else "d3" if d <= 9 else "d10")

def call(cat, a, n, d):
    cell = (RECOG.get(cat + "|h6") or {}).get(pbk(a, n, d))
    if cell and cell.get("purity", 0) >= 0.5:
        return cell["top"]
    return dband(cat, a)

def reach_ok(band, d):
    rc = (SURF.get(band) or {}).get("reach") or {}
    n = (SURF.get(band) or {}).get("n", 0)
    return d <= 1 or float(rc.get(str(d), 0) or 0) * n >= 8

def lvl_at(band, pol, anchor, frac):
    d = pol[0] if frac < 0.4 else pol[1] if frac < 0.8 else pol[2]
    while d > 0 and not reach_ok(band, d):
        d -= 1
    return anchor - d

tiers = {"le93": 0, "le95": 0, "le97": 0, "gt97": 0}
per = defaultdict(lambda: dict(tiers))
duals = bothneg = 0
for line in open(ROOT / "state/range_spectrum_v1.jsonl"):
    r = json.loads(line)
    day = r["event"].split("-")[1][:7]
    if not (day >= "26JUL14" and day.startswith("26JUL")):
        continue
    legs = {k: v for k, v in r["legs"].items() if v.get("shape")}
    if len(legs) != 2:
        continue
    t8 = r["sched"] - 8 * 3600
    cut = t8 + 2 * 3600
    span = max(r["right_edge"] - t8, 1.0)
    fills = []
    for leg, v in legs.items():
        tk = [(ts, lc) for ts, b, a, lc in (v.get("ticks") or []) if lc]
        p1 = [(ts, lc) for ts, lc in tk if ts <= cut]
        nh = (p1[-1][1] - p1[0][1]) if p1 else 0
        dh = (v["anchor"] - min(x[1] for x in p1)) if p1 else 0
        b1 = dband(r["cat"], v["anchor"])
        b2 = call(r["cat"], v["anchor"], nh, dh) or b1
        got = None
        for ts, lc in tk:
            band = b1 if ts <= cut else b2
            if band not in POL:
                break
            lv = lvl_at(band, POL[band], v["anchor"], (ts - t8) / span)
            if lv >= 5 and lc <= lv:
                got = (band, lv, lv - v["close"])
                break
        fills.append(got)
    if all(f is not None for f in fills):
        duals += 1
        comb = sum(f[1] for f in fills)
        key = ("le93" if comb <= 93 else "le95" if comb <= 95 else
               "le97" if comb <= 97 else "gt97")
        tiers[key] += 1
        pk = "|".join(sorted(f[0] for f in fills))
        per[pk][key] = per[pk].get(key, 0) + 1
        if all(f[2] < 0 for f in fills):
            bothneg += 1
L = ["# LOOP 6 — THE SECOND GAUGE (holdout duals, converged policies)", ""]
L.append("- duals %d · both-neg %.1f%% (gauge a) · combined tiers: "
         "<=93 %.0f%% · <=95 %.0f%% · <=97 %.0f%% · >97 %.0f%% (gauge b)"
         % (duals, 100 * bothneg / max(duals, 1),
            *(100 * tiers[k] / max(duals, 1)
              for k in ("le93", "le95", "le97", "gt97"))))
flag = (bothneg / max(duals, 1) >= 0.75
        and tiers["gt97"] / max(duals, 1) > 0.10)
L.append("- FLAG RULE (delta clears while combined degrades >97 >10%%): "
         "%s" % ("**FLAGGED**" if flag else "clean"))
for pk, t in sorted(per.items(), key=lambda kv: -sum(kv[1].values()))[:12]:
    n = sum(t.values())
    L.append("- %s (n=%d): " % (pk, n) + " ".join(
        "%s %.0f%%" % (k, 100 * t.get(k, 0) / n)
        for k in ("le93", "le95", "le97", "gt97")))
Path("/tmp/LOOP6_GAUGE2.md").write_text("\n".join(L) + "\n")
print("GAUGE2-DONE duals", duals, "bothneg%",
      round(100 * bothneg / max(duals, 1), 1), "gt97%",
      round(100 * tiers["gt97"] / max(duals, 1), 1))
