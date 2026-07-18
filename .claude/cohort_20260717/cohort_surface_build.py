#!/usr/bin/env python3
"""PHASE C P1 — THE COHORT SURFACE (built from the re-cut range spectrum).

Cells: cat (HARD partition) × side (fav/dog by anchor vs sibling) ×
anchor bucket (le25 / 26_50 / 51_75 / ge76). Per cell, EMPIRICAL
distributions — no curve-fitting poetry:
  orientation   rose/fell/flat counts (net >= +3 / <= −3)
  cast_depth    dip-below-anchor distribution (p25/50/75/90, share >= 3c)
                — the 3c fiction's replacement
  reachability  P(touch anchor−d) for d = 1..15, + median touch timing
                (T-minus min) — range-prior, reach-recal, chain proof, M15
                intake retire into this one voice
  pair_coherence seesaw corr distribution
Walk rates per CAT (P0-3b deliverable): grind-up legs' cents-per-30min
distribution — the fitted sanctioned-walk read that retires 1c/30min.
Kinship (P4, self-executing): ITF cells with n < FLOOR borrow the same
side/bucket CHALL cell IFF the ITF cat's own floor-passing cells sit
within tolerance of CHALL (|dip_p50| <= 2c AND |rose%| <= 12pts) —
labeled borrowed, weight-discounted 0.5, retired as native n matures.
Output: state/cohort_surface_v1.json
"""
import json, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "state/range_spectrum_v1.jsonl"
OUT = ROOT / "state/cohort_surface_v1.json"
FLOOR = 30

def bucket(a):
    return "le25" if a <= 25 else "26_50" if a <= 50 else \
        "51_75" if a <= 75 else "ge76"

cells = defaultdict(lambda: {"n": 0, "rose": 0, "fell": 0, "flat": 0,
                             "dips": [], "corr": [], "touch_t": [],
                             "reach": defaultdict(int)})
walk = defaultdict(list)
n_rows = 0
for line in open(SPEC):
    r = json.loads(line)
    cat = r["cat"]
    legs = {k: v for k, v in r["legs"].items() if v.get("shape")}
    if not legs:
        continue
    n_rows += 1
    items = sorted(legs.items(), key=lambda kv: kv[1]["anchor"],
                   reverse=True)
    for i, (leg, v) in enumerate(items):
        side = "fav" if (len(items) == 2 and i == 0) or \
            (len(items) == 1 and v["anchor"] >= 50) else "dog"
        key = "%s|%s|%s" % (cat, side, bucket(v["anchor"]))
        c = cells[key]
        c["n"] += 1
        net = v["net"]
        c["rose" if net >= 3 else "fell" if net <= -3 else "flat"] += 1
        dip = v["anchor"] - v["low"]
        c["dips"].append(dip)
        c["touch_t"].append(v["low_tmin_min"])
        for d in range(1, 16):
            if dip >= d:
                c["reach"][d] += 1
        if r.get("seesaw_corr") is not None:
            c["corr"].append(r["seesaw_corr"])
        # walk rate: grind-up legs only (real strengthening)
        if v["shape"] == "grind" and net >= 3:
            span_30m = max((r["right_edge"] - (r["sched"] - 8 * 3600))
                           / 1800.0, 0.5)
            walk[cat].append(net / span_30m)

def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))] if v else None

surface = {"built_from": str(SPEC), "spectrum_rows": n_rows,
           "floor_n": FLOOR, "cells": {}, "walk_rates": {},
           "kinship": {}}
for key, c in cells.items():
    n = c["n"]
    surface["cells"][key] = {
        "n": n,
        "rose": c["rose"], "fell": c["fell"], "flat": c["flat"],
        "rose_pct": round(100.0 * c["rose"] / n, 1),
        "dip_p25": pct(c["dips"], 0.25), "dip_p50": pct(c["dips"], 0.50),
        "dip_p75": pct(c["dips"], 0.75), "dip_p90": pct(c["dips"], 0.90),
        "dip_ge3_pct": round(100.0 * sum(1 for d in c["dips"] if d >= 3)
                             / n, 1),
        "reach": {str(d): round(c["reach"][d] / n, 3)
                  for d in range(1, 16)},
        "touch_tmin_p50": pct(c["touch_t"], 0.5),
        "seesaw_corr_p50": (pct(c["corr"], 0.5) if c["corr"] else None),
    }
for cat, v in walk.items():
    surface["walk_rates"][cat] = {
        "n": len(v), "cents_per_30m_p50": round(pct(v, 0.5), 2),
        "cents_per_30m_p75": round(pct(v, 0.75), 2),
        "cents_per_30m_p90": round(pct(v, 0.90), 2),
        "cite": "PHASE-C P1 07-17: fitted per-cat sanctioned-walk rate "
                "(grind-up legs, re-cut spectrum) — retires the 1c/30min "
                "constant per P0v3-3b"}

# kinship (P4): cat-level tolerance test, then per-cell borrowing
for itf, chall in (("ITF_M", "ATP_CHALL"), ("ITF_W", "WTA_CHALL")):
    itf_cells = {k: v for k, v in surface["cells"].items()
                 if k.startswith(itf) and v["n"] >= 15}
    ok = tot = 0
    for k, v in itf_cells.items():
        ck = k.replace(itf, chall)
        cv = surface["cells"].get(ck)
        if not cv or cv["n"] < FLOOR:
            continue
        tot += 1
        if (v["dip_p50"] is not None and cv["dip_p50"] is not None
                and abs(v["dip_p50"] - cv["dip_p50"]) <= 2
                and abs(v["rose_pct"] - cv["rose_pct"]) <= 12):
            ok += 1
    within = tot > 0 and ok / tot >= 0.5
    surface["kinship"][itf] = {
        "vs": chall, "cells_compared": tot, "within_tolerance": ok,
        "verdict": "BORROW" if within else "NO-BORROW",
        "tolerance": "|dip_p50|<=2c AND |rose_pct|<=12pts on "
                     "floor-passing cells; >=50% must pass"}
    if within:
        borrowed = 0
        for k in list(surface["cells"].keys()):
            if not k.startswith(chall):
                continue
            ik = k.replace(chall, itf)
            iv = surface["cells"].get(ik)
            if iv is None or iv["n"] < FLOOR:
                bc = dict(surface["cells"][k])
                bc.update({"borrowed_from": k, "weight_discount": 0.5,
                           "native_n": (iv["n"] if iv else 0),
                           "retire_rule": "native n >= %d" % FLOOR})
                surface["cells"][ik + "|borrowed"] = bc
                borrowed += 1
        surface["kinship"][itf]["cells_borrowed"] = borrowed

OUT.write_text(json.dumps(surface))
print("cells:", len(surface["cells"]), "| walk_rates:",
      {k: v["cents_per_30m_p75"] for k, v in surface["walk_rates"].items()})
print("kinship:", {k: v["verdict"] for k, v in surface["kinship"].items()})
th = sum(1 for v in surface["cells"].values()
         if isinstance(v, dict) and v.get("n", 0) < FLOOR)
print("thin cells (<%d): %d of %d" % (FLOOR, th, len(surface["cells"])))
