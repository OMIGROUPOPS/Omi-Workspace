#!/usr/bin/env python3
"""STAGE 4 — THE SOLVE-REPLAY LOOP (the operator's loop, built to law).

INFORMATION TIME: the brain walks each leg's tick series in order; at every
decision moment it knows only prints/quotes at or before that moment. At
T−6h (decreed decision hour, stated) it: (1) calls the band from the
PARTIAL journey via the recognition table (confidence = bucket purity;
below CONF_MIN falls to the anchor-region default band, named); (2) prices
the level from the CURRENT parameter set (per-band depth); (3) rests the
bid. Scoring against the leg's OWN later tape: filled iff any later W1
print <= level. Score = realized ROC under the solve's close-based frame:
fill → (close − level)/level per unit; no fill → 0 (capital unspent, W1
frame — misses are also counted as miss-rate for the report).

THE DRILL: solve → replay → score → adjust → re-solve, automatically.
HOLDOUT LAW: parameters adjust ONLY on the TRAIN era (pre-Jul-14); every
iteration ALSO scores the untouched HOLDOUT era (Jul-14+), reported side
by side — the train-vs-holdout gap is printed every iteration (the
memorization meter; a widening gap = diverging, named). Adjustment: per
band, coordinate step (±1..3¢) accepted only if TRAIN ROC improves;
stopping by evidence: CONVERGED (no accepted step), PLATEAUED (<0.5%
train gain twice), DIVERGING (holdout falls 2 iters while train rises).

Outputs: state/entry_tables_v2.json (post-drill tables) +
/tmp/LOOP_CAMPAIGN.md (iterations, adjustments, train/holdout ROC per
iter, verdicts per band w/ binomial CIs, named failures) +
/tmp/REPLAY_DAY.md (every bid the finished brain places on the walked
day, reasoning printed).
"""
import json, math, random
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BMAP = json.loads((ROOT / "state/band_map_v1.json").read_text())
DRIFT = json.loads((ROOT / "state/drift_surfaces_v1.json").read_text())
TAB = json.loads((ROOT / "state/entry_tables_v1.json").read_text())["tables"]
SPEC = ROOT / "state/range_spectrum_v1.jsonl"
OUTJ = ROOT / "state/entry_tables_v2.json"
OUTM = Path("/tmp/LOOP_CAMPAIGN.md")
OUTD = Path("/tmp/REPLAY_DAY.md")
random.seed(20260718)

DECISION_H = 6      # decide at T-6h (decreed, stated)
CONF_MIN = 0.5
WALK_DAY = "26JUL16"
RECOG = json.loads((ROOT / "state/drift_surfaces_v1.json").read_text()) \
    .get("recognition", {})

def pbucket(anchor, net, dip):
    ab = ("a25" if anchor <= 25 else "a50" if anchor <= 50 else
          "a75" if anchor <= 75 else "a95")
    nb = ("dn10" if net <= -10 else "dn3" if net <= -3 else
          "flat" if net < 3 else "up3" if net < 10 else "up10")
    db = "d0" if dip <= 2 else "d3" if dip <= 9 else "d10"
    return ab + "|" + nb + "|" + db

def default_band(cat, anchor):
    """anchor-region default: the flat band nearest this anchor (the
    dominant population everywhere)."""
    c = BMAP["cats"].get(cat)
    if not c or c.get("thin"):
        return None
    flats = [b for b in c["bands"] if b["direction"] == "flat"] or c["bands"]
    return min(flats, key=lambda b: abs(b["anchor_med"] - anchor))["band"]

def call_band(cat, anchor, net_h, dip_h):
    """(band, confidence, how) from the recognition table at DECISION_H."""
    cell = (RECOG.get("%s|h%d" % (cat, DECISION_H)) or {}).get(
        pbucket(anchor, net_h, dip_h))
    if cell and cell.get("purity", 0) >= CONF_MIN:
        return cell["top"], cell["purity"], "recognition"
    return default_band(cat, anchor), (cell or {}).get("purity", 0.0), \
        "anchor_default"

# ---- load legs once: (cat, day, anchor, partial@T-6h, later-tape, close)
legs = []
for line in open(SPEC):
    r = json.loads(line)
    t8 = r["sched"] - 8 * 3600
    cut = t8 + (8 - DECISION_H) * 3600     # T-6h wall clock
    day = r["event"].split("-")[1][:7]
    for leg, v in r["legs"].items():
        if not v.get("shape"):
            continue
        ticks = v.get("ticks") or []
        seen = [(ts, lc) for ts, b, a, lc in ticks if lc and ts <= cut]
        later = [lc for ts, b, a, lc in ticks if lc and ts > cut]
        if not seen or not later:
            continue
        net_h = seen[-1][1] - seen[0][1]
        dip_h = v["anchor"] - min(x[1] for x in seen)
        legs.append({"cat": r["cat"], "day": day, "event": r["event"],
                     "leg": leg, "anchor": v["anchor"], "net_h": net_h,
                     "dip_h": dip_h, "later_low": min(later),
                     "close": v["close"],
                     "is_holdout": day >= "26JUL14" and day.startswith("26JUL")})
print("replayable legs:", len(legs), "| holdout:",
      sum(1 for x in legs if x["is_holdout"]), flush=True)

def replay(depths, cohort):
    """Score one parameter set over a cohort. Returns (roc_mean, n_bid,
    n_fill, per_band dict)."""
    tot_ret = 0.0
    n_bid = n_fill = 0
    per = defaultdict(lambda: [0, 0, 0.0])
    for x in cohort:
        band, conf, how = call_band(x["cat"], x["anchor"], x["net_h"],
                                    x["dip_h"])
        if not band:
            continue
        row = TAB.get(band)
        if not row or row.get("thin"):
            continue
        d = depths.get(band, row.get("depth"))
        if d is None:
            continue
        if row["kind"] == "faller" and row.get("roc", 0) <= 0:
            continue                      # the violent faller's REFUSE is law
        level = x["anchor"] - d
        if level < 5:
            continue
        n_bid += 1
        per[band][0] += 1
        if x["later_low"] <= level:
            n_fill += 1
            ret = (x["close"] - level) / max(level, 1)
            tot_ret += ret
            per[band][1] += 1
            per[band][2] += ret
    return (tot_ret / max(n_bid, 1), n_bid, n_fill, per)

train = [x for x in legs if not x["is_holdout"]]
hold = [x for x in legs if x["is_holdout"]]
depths = {b: r.get("depth") for b, r in TAB.items()
          if r.get("depth") is not None and not r.get("thin")}
bands = sorted(depths)
hist = []
L = ["# STAGE 4 — THE DRILL CAMPAIGN (holdout law: adjust on train, "
     "judged on held-out; gap printed every iteration)", ""]
prev_train = None
plateau = diverge = 0
for it in range(1, 13):
    tr = replay(depths, train)
    ho = replay(depths, hold)
    gap = tr[0] - ho[0]
    hist.append((it, tr[0], ho[0], gap))
    L.append("- iter %d: TRAIN ROC %.4f (bids %d fills %d) · HOLDOUT ROC "
             "%.4f (bids %d fills %d) · gap %+.4f"
             % (it, tr[0], tr[1], tr[2], ho[0], ho[1], ho[2], gap))
    # stopping rules by evidence
    if prev_train is not None:
        if tr[0] - prev_train < 0.005 * max(abs(prev_train), 0.01):
            plateau += 1
        else:
            plateau = 0
        if len(hist) >= 3 and hist[-1][2] < hist[-2][2] < hist[-3][2] \
                and tr[0] > prev_train:
            diverge += 1
    prev_train = tr[0]
    if plateau >= 2:
        L.append("- STOP: PLATEAUED (<0.5% train gain twice).")
        break
    if diverge >= 1:
        L.append("- STOP: DIVERGING (holdout falling while train rises — "
                 "memorization named).")
        break
    # adjust: per-band coordinate step accepted only on TRAIN improvement
    accepted = []
    base = tr[0]
    for b in bands:
        best_d, best_s = depths[b], base
        for step in (-3, -2, -1, 1, 2, 3):
            cand = dict(depths)
            nd = depths[b] + step
            if nd < 1 or nd > 30:
                continue
            cand[b] = nd
            s = replay(cand, train)[0]
            if s > best_s:
                best_s, best_d = s, nd
        if best_d != depths[b]:
            accepted.append((b, depths[b], best_d))
            depths[b] = best_d
            base = best_s
    if accepted:
        L.append("    adjusted: " + " · ".join(
            "%s %d→%d" % a for a in accepted[:8]) +
            (" (+%d more)" % (len(accepted) - 8) if len(accepted) > 8 else ""))
    else:
        L.append("- STOP: CONVERGED (no accepted step).")
        break

# ---- validation report per band (holdout, with binomial CIs) ------------
L.append("")
L.append("## STAGE 4 VALIDATION REPORT (held-out only; CI = 95% Wilson)")
final_ho = replay(depths, hold)
def wilson(k, n):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    z = 1.96
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0, c - h), min(1, c + h))
fails = []
for band, (nb, nf, sret) in sorted(final_ho[3].items()):
    if nb < 5:
        L.append("- %s: holdout n=%d — TOO THIN TO JUDGE (said so)."
                 % (band, nb))
        continue
    lo, hi = wilson(nf, nb)
    pred = None
    trow = TAB.get(band) or {}
    g = (trow.get("gated_levels") or {}).get(str(depths.get(band)))
    if g:
        pred = g.get("p_fill", g.get("rate"))
    roc = sret / nb
    verdict = "OK"
    if pred is not None and not (lo <= pred <= hi) and nb >= 10:
        verdict = "FAILS (predicted %.2f outside CI)" % pred
        fails.append(band)
    L.append("- %s: depth %d¢ · holdout fills %d/%d (CI %.2f–%.2f) vs "
             "predicted %s · holdout ROC %.4f · %s"
             % (band, depths.get(band, -1), nf, nb, lo, hi,
                ("%.2f" % pred) if pred is not None else "n/a", roc, verdict))
L.append("")
L.append("named failures: %s" % (fails or "none"))

# ---- the walked replay day ----------------------------------------------
D = ["# REPLAY DAY — %s (every bid the finished brain places; reasoning "
     "printed)" % WALK_DAY, ""]
for x in legs:
    if x["day"] != WALK_DAY:
        continue
    band, conf, how = call_band(x["cat"], x["anchor"], x["net_h"], x["dip_h"])
    if not band:
        continue
    row = TAB.get(band) or {}
    if row.get("thin") or row.get("depth") is None:
        continue
    if row["kind"] == "faller" and row.get("roc", 0) <= 0:
        D.append("- %s-%s: band %s called (%s, conf %.2f) → REFUSE (violent "
                 "faller — the law)" % (x["event"][-6:], x["leg"], band, how,
                                        conf))
        continue
    d = depths.get(band, row["depth"])
    level = x["anchor"] - d
    if level < 5:
        continue
    filled = x["later_low"] <= level
    D.append("- %s-%s: anchor %d¢, journey@T−6h (net %+d, dip %d) → band "
             "**%s** (%s, conf %.2f) · zone %s · bid **%d¢** (depth %d) → "
             "%s%s"
             % (x["event"][-6:], x["leg"], x["anchor"], x["net_h"],
                x["dip_h"], band, how, conf, row["kind"], level, d,
                "FILLED" if filled else "no fill (honest miss)",
                (" · close %d¢ → %+d¢/sh" % (x["close"],
                                             x["close"] - level))
                if filled else ""))
OUTD.write_text("\n".join(D) + "\n")
OUTJ.write_text(json.dumps({"depths": depths, "campaign": hist,
                            "frame": "post-drill tables; holdout-judged"}))
OUTM.write_text("\n".join(L) + "\n")
print("CAMPAIGN-DONE iters:", len(hist), "fails:", fails)
print("\n".join(L[:12]))
