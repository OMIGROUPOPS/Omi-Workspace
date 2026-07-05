#!/usr/bin/env python3
"""aim_time_axis.py — derive the 3-D aim table {cat x price-bucket x tts-bucket} from the
premarket drift/dip/timing surfaces. Re-runnable; writes docs/policy/aim_table_t.json.
Run from arb-executor root (surfaces live in analysis/exit_charts/).

## Prior art (gate — C45): this is DEPLOYMENT of existing analysis, not new measurement.
- premarket_dip_surface_{CAT}.csv / premarket_dip_timing_{CAT}.csv / premarket_drift_{CAT}.csv
  (analysis/exit_charts/, tour cats): per-cell dip-reach probability by depth and by
  time-bin — THE source surfaces.
- A49 (aim = the fillable dip below current, not FV; T-20m anchor is the sucker's baseline),
  A50 (dips cluster late-window) — the timing surfaces quantify A50 per cell.
- P3b shape-sequenced replay (analysis/stranded/, 4H addendum #3) — decay-curve precedent.
- aim_table.json flat values (deployed: faller MAIN 2/CHALL 3/ITF 4; riser_post CHALL 3/
  ITF_M 3/ITF_W 2/mains 0) — the T4-bucket anchor this table must reduce to.
- DELTA: the time axis itself — per-bucket depth from P_remain(D, T) = P_total(D) * (1 - phi(T)).

## Conventions (stated)
- phi(T) = cumulative reach-by-time share (timing surface, D=3 shape, fallback D=5),
  normalized by the last bin -> the fraction of the total dip probability already SPENT by T.
- faller_depth(cell, T) = max D in 1..6 with P_remain(D,T) >= 0.50; floor 1 (A49: 97% dip >=1c).
- riser_post(cell, T)  = max D in 0..4 with P_remain(D,T) >= 0.50 at the RISER's own cell
  (one read, both legs: the same surface machinery is the inverse drift read); mains cap 1
  (RISER_REVISION_PROPOSAL: liquid books don't dip — hold 0-1).
- tts buckets (minutes before start): T8>(360), T6=(240,360], T4=(120,240], T2=(60,120],
  T1=(30,60], T30<=30. Representative surface bin per bucket: T8/T6->240 (surfaces stop at
  240; earlier = flat extrapolation, stated), T4->180, T2->90, T1->40, T30->10.
- CLOCK CAVEAT: the surfaces' time bins are vs the schedule clock of their build (the card
  clock). Runtime tts uses the same card clock today, honest clock when per_match_clock arms
  (Part 1) — at THAT point this table should be re-derived on honest-anchored surfaces.
- ITF (no surfaces): borrow the ATP_CHALL bucket-level time-SHAPE, anchored so the T4 bucket
  equals the deployed flat values (faller 4 / riser 3 (ITF_M), 2 (ITF_W)); clamped 1..6 / 0..4.
  Stated assumption, revisit when ITF surfaces exist.
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SURF = ROOT / "analysis" / "exit_charts"
OUT = ROOT / "docs" / "policy" / "aim_table_t.json"

TOUR = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]
BUCKETS = [("01-20", 1, 20), ("21-40", 21, 40), ("41-49", 41, 49),
           ("50-59", 50, 59), ("60-79", 60, 79), ("80-99", 80, 99)]
TB_REP = [("T8", 240), ("T6", 240), ("T4", 180), ("T2", 90), ("T1", 40), ("T30", 10)]
BAR = 0.50
FALLER_RANGE = range(1, 7)
RISER_RANGE = range(0, 5)
RISER_CAP = {"ATP_MAIN": 1, "WTA_MAIN": 1}
FLAT_ITF = {"ITF_M": {"faller": 4, "riser": 3}, "ITF_W": {"faller": 4, "riser": 2}}

def load_cat(cat):
    """-> (totals[c][D] = P_total, phi[c][bin] = cumulative share spent)."""
    totals = defaultdict(dict); nmatch = {}
    for r in csv.DictReader(open(SURF / ("premarket_dip_surface_%s.csv" % cat))):
        c, d = int(r["c"]), int(r["D"])
        v = r.get("reach_dip_pooled_match_mono") or r.get("reach_dip_pooled_match") or r.get("reach_dip_raw")
        totals[int(c)][d] = float(v)
        nmatch[c] = float(r.get("match_N") or 0)
    timing = defaultdict(dict)   # c -> D -> {bin: cum}
    for r in csv.DictReader(open(SURF / ("premarket_dip_timing_%s.csv" % cat))):
        c, d, b = int(r["c"]), int(r["D"]), int(r["time_bin_min_before_start"])
        timing[c].setdefault(d, {})[b] = float(r["reach_dip_by_time_raw"])
    phi = {}
    for c, byd in timing.items():
        prof = byd.get(3) or byd.get(5) or byd.get(8)
        if not prof:
            continue
        final = prof.get(1) or max(prof.values()) or 0.0
        if final <= 0:
            phi[c] = {b: 0.0 for b in prof}
        else:
            phi[c] = {b: min(1.0, v / final) for b, v in prof.items()}
    return totals, phi, nmatch

def depth_at(totals_c, phi_c, rep_bin, rng, bar=BAR):
    """max D in rng with P_total(D)*(1-phi(rep_bin)) >= bar; else min(rng)."""
    spent = phi_c.get(rep_bin, 0.0) if phi_c else 0.0
    best = min(rng)
    for d in rng:
        p_tot = totals_c.get(d)
        if p_tot is None:
            # interpolate: nearest known depths
            ks = sorted(totals_c)
            if not ks:
                continue
            lo = max((k for k in ks if k <= d), default=ks[0])
            hi = min((k for k in ks if k >= d), default=ks[-1])
            p_tot = totals_c[lo] if lo == hi else totals_c[lo] + (totals_c[hi] - totals_c[lo]) * (d - lo) / (hi - lo)
        if p_tot * (1.0 - spent) >= bar:
            best = d
    return best

out = {"meta": {
    "derived": "aim_time_axis.py (re-runnable) from premarket_dip_surface_/dip_timing_ per cat",
    "semantics": "P_remain(D,T)=P_total(D)*(1-phi(T)); depth = max D with P_remain>=0.50",
    "tts_buckets_min": {"T8": ">360", "T6": "240-360", "T4": "120-240", "T2": "60-120", "T1": "30-60", "T30": "<=30"},
    "clock": "card clock (surfaces' build clock); re-derive on honest surfaces when per_match_clock arms",
    "itf": "ATP_CHALL shape borrowed, anchored to deployed flat values at T4 (stated assumption)",
}, "aim_t": {}}

chall_shape = {}   # bucket -> {tb: faller_depth} for the ITF borrow
for cat in TOUR:
    totals, phi, nmatch = load_cat(cat)
    out["aim_t"][cat] = {}
    for bname, lo, hi in BUCKETS:
        cells = [c for c in totals if lo <= c <= hi]
        if not cells:
            continue
        row = {}
        for tb, rep in TB_REP:
            wf = wr = wn = 0.0
            for c in cells:
                n = max(1.0, nmatch.get(c, 1.0))
                f = depth_at(totals[c], phi.get(c, {}), rep, FALLER_RANGE)
                r = depth_at(totals[c], phi.get(c, {}), rep, RISER_RANGE)
                wf += f * n; wr += r * n; wn += n
            fd = max(1, int(round(wf / wn)))
            rp = max(0, int(round(wr / wn)))
            rp = min(rp, RISER_CAP.get(cat, 4))
            row[tb] = {"faller_depth": fd, "riser_post": rp}
        out["aim_t"][cat][bname] = row
        if cat == "ATP_CHALL":
            chall_shape[bname] = {tb: v["faller_depth"] for tb, v in row.items()}

# ITF: CHALL shape anchored at T4 to the deployed flat values
for cat, flat in FLAT_ITF.items():
    out["aim_t"][cat] = {}
    for bname, _, _ in BUCKETS:
        shape = chall_shape.get(bname) or {}
        base_t4 = shape.get("T4", 3)
        row = {}
        for tb, _rep in TB_REP:
            dlt = (shape.get(tb, base_t4) - base_t4)
            row[tb] = {"faller_depth": max(1, min(6, flat["faller"] + dlt)),
                       "riser_post": max(0, min(4, flat["riser"] + dlt))}
        out["aim_t"][cat][bname] = row

OUT.write_text(json.dumps(out, indent=1))
print("wrote", OUT)
for cat in out["aim_t"]:
    b = out["aim_t"][cat].get("60-79") or next(iter(out["aim_t"][cat].values()))
    print(cat, "60-79:", {tb: (v["faller_depth"], v["riser_post"]) for tb, v in b.items()})
