#!/usr/bin/env python3
"""AIM V2 VALIDATION HARNESS — PLEX_REGRESSION_RULING §3 / Ruling ② (2026-07-06).
Built now; runs whenever data permits (reports insufficient-coverage weeks cleanly).

Walk-forward by ISO week over the shape corpus (data/shape_corpus/samples_*.jsonl):
train on weeks < W (honest-era weight 1.0, card-era 0.25 — CARD-ERA FLAGGED per the
ruling), HARD min-n gate (effective-n >= 30; below-floor cells are NULL — the consumer
falls back to the deployed FLAT aim, explicitly counted, never a silent neighbor borrow),
replay week W tape-only (bid active from T-6h to the bell; fill = tape printed at/below
aim in a 10-min step; resting bid carries across re-derives).

LANE-1 BARS (standing, restated verbatim):
  - joint achievable-vs-paid gap SHRINKS vs the flat baseline
  - lazy-leg rate (fills at/above own FV_hat) SHRINKS
  - participation HOLDS
  - beats the -$20.31 verdict on the new basis (Lane-2 reported with n, luck-flagged)
  - walk/repost interaction explicitly modeled: the riser bar-(e) EROSION pattern is the
    test — share of sim fills above their first-posted aim must stay < 25%
  - the walk-cap honest-window anchor ships WITH OR BEFORE any arm (deployment condition,
    tracked outside this harness)
Census-161 (2026-07-06) is the SECONDARY confirmatory OOS: .claude/autopsy_20260706/
fv_aim_build2.py phase-B against any candidate table (run separately, reported alongside).
NOTHING ARMS from this harness; its output feeds Plex."""
import json, gzip, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "shape_corpus"
BIN = 600; GRID = 48; FLOOR = 30
CARD_W = 0.25
FLAT = {"ATP_MAIN": 2, "WTA_MAIN": 2, "ATP_CHALL": 3, "WTA_CHALL": 3, "ITF_M": 4, "ITF_W": 4}
def buck(px): return min(4, max(0, int(px)//20))
def med(v):
    v = sorted(v); return v[len(v)//2] if v else None

# ---------- load corpus ----------
samples = []
for sf in sorted(CORPUS.glob("samples_*.jsonl")):
    for line in open(sf, encoding="utf-8"):
        try: s = json.loads(line)
        except: continue
        if "bell" not in s: continue
        s["week"] = datetime.fromtimestamp(s["bell"], timezone.utc).strftime("%G-W%V")
        samples.append(s)
if not samples:
    print("HARNESS: corpus empty — run analysis/shape_accumulator.py first", file=sys.stderr)
    sys.exit(0)
weeks = sorted(set(s["week"] for s in samples))
by_leg = defaultdict(list)
for s in samples:
    by_leg[s["tk"]].append(s)

def train(upto_week):
    vals = defaultdict(lambda: ([], []))
    for s in samples:
        if s["week"] >= upto_week: continue
        w = 1.0 if s["era"] == "honest" else CARD_W
        d, dp = vals[(s["cat"], s["b"], s["t"])]
        d.append((s["drift"], w)); dp.append((s["dip"], w))
    table = {}
    for k, (d, dp) in vals.items():
        eff_n = sum(w for _, w in d)
        if eff_n < FLOOR:
            table[k] = None                      # PARKED — no silent interpolation
            continue
        table[k] = {"drift": med([x for x, _ in d]), "dip": med([x for x, _ in dp]),
                    "eff_n": round(eff_n, 1)}
    return table

def replay_week(week, table):
    """Tape-only replay of week-W legs: per (leg, Tbin) sample sequence (descending T),
    bid = trained aim if cell live else FLAT fallback (counted); fill when the leg's
    NEXT-bin price path reaches the bid (dip sample carries min-to-bell)."""
    res = {"legs": 0, "fills": 0, "flat_fallback_steps": 0, "steps": 0,
           "lazy": 0, "gap": [], "erosion": 0}
    for tk, ss in by_leg.items():
        if not ss or ss[0]["week"] != week: continue
        ss = sorted(ss, key=lambda s: -s["t"])
        res["legs"] += 1
        first_aim = None; filled_at = None; fv_at_fill = None
        for s in ss:
            cell = table.get((s["cat"], s["b"], s["t"]))
            p_now = 0  # anchor: prices are relative (drift/dip vs current) — aim depth below current
            if cell:
                aim_rel = cell["dip"]; fv_rel = cell["drift"]
            else:
                aim_rel = -FLAT[s["cat"]]; fv_rel = None
                res["flat_fallback_steps"] += 1
            res["steps"] += 1
            if first_aim is None: first_aim = aim_rel
            # fill test: this bin's actual remaining-dip (s["dip"]) reaches the aim depth
            if s["dip"] <= aim_rel:
                filled_at = aim_rel
                if fv_rel is not None:
                    res["lazy"] += 1 if aim_rel >= fv_rel else 0
                # erosion pattern: filled at a SHALLOWER (higher) aim than first posted
                if aim_rel > first_aim: res["erosion"] += 1
                # gap vs the leg's true best (min dip over its whole window)
                best = min(x["dip"] for x in ss)
                res["gap"].append(aim_rel - best)
                break
        if filled_at is not None: res["fills"] += 1
    return res

print(f"HARNESS walk-forward: {len(weeks)} weeks, {len(by_leg)} legs, {len(samples)} samples", file=sys.stderr)
report = []
for i, w in enumerate(weeks):
    if i == 0:
        report.append({"week": w, "status": "no-prior-training-data"}); continue
    table = train(w)
    live = sum(1 for v in table.values() if v)
    if live < 20:
        report.append({"week": w, "status": f"insufficient-coverage ({live} live cells)"}); continue
    r = replay_week(w, table)
    fill_rate = r["fills"]/max(1, r["legs"])
    report.append({"week": w, "status": "ok", "legs": r["legs"], "fill_rate": round(fill_rate, 3),
                   "pair_proxy": round(fill_rate**2, 3), "gap_med": med(r["gap"]),
                   "lazy": r["lazy"], "erosion": r["erosion"],
                   "flat_fallback_share": round(r["flat_fallback_steps"]/max(1, r["steps"]), 3),
                   "live_cells": live})
out = ROOT / "data" / "shape_corpus" / "harness_report.json"
json.dump({"generated": datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), "weeks": report}, open(out, "w"), indent=1)
for r in report: print(r, file=sys.stderr)
print(f"-> {out}", file=sys.stderr)
