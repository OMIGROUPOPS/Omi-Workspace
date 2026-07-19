#!/usr/bin/env python3
"""STAGE 4b — RE-FRAME AND RE-DRILL (each strategy replayed in ITS OWN
frame; the 4a mis-frame named in the C50).

THE FRAME, rebuilt to the strategies as designed:
  - Bids rest from CONCEPTION (window start) — not a T−6h static.
  - PHASE 1 (conception → T−6h): the leg parks at its ANCHOR-DEFAULT
    band's level (no journey exists yet; flats dominate by population —
    the honest prior). Fill = any phase-1 print ≤ level.
  - PHASE 2 (T−6h → right edge): the recognition table re-calls the band
    from the journey-so-far (the cohort re-selection law); the bid re-aims
    to the called band's level. Fill = any phase-2 print ≤ level2.
  - Divot bids therefore rest ALL-WINDOW (the catch tables' own frame);
    casts rest conception→corridor; parks join at touch (depth 0–2).
  - REFUSE law unchanged. Mark unchanged (close-based W1 — the exit blend
    is Stage 6's word). ROC per bid = (close − fill_level)/fill_level.

THE DRILL: unchanged law — adjust on TRAIN only (pre-Jul-14), holdout
(Jul-14+) scored every iteration, gap meter printed, stopping by evidence.

DELIVERABLES: /tmp/LOOP2_CAMPAIGN.md (iterations + per-band holdout report
+ VERDICT DELTAS vs the 4a run: FRAME-failure vs REAL-failure named) +
state/entry_tables_v3.json (post-drill) + /tmp/REPLAY2_DAY.md.
"""
import json, math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BMAP = json.loads((ROOT / "state/band_map_v1.json").read_text())
DRIFT = json.loads((ROOT / "state/drift_surfaces_v1.json").read_text())
TAB = json.loads((ROOT / "state/entry_tables_v1.json").read_text())["tables"]
V2 = json.loads((ROOT / "state/entry_tables_v2.json").read_text())
SPEC = ROOT / "state/range_spectrum_v1.jsonl"
OUTJ = ROOT / "state/entry_tables_v3.json"
OUTM = Path("/tmp/LOOP2_CAMPAIGN.md")
OUTD = Path("/tmp/REPLAY2_DAY.md")
RECOG = DRIFT.get("recognition", {})
DECISION_H = 6
CONF_MIN = 0.5
WALK_DAY = "26JUL16"

def pbucket(anchor, net, dip):
    ab = ("a25" if anchor <= 25 else "a50" if anchor <= 50 else
          "a75" if anchor <= 75 else "a95")
    nb = ("dn10" if net <= -10 else "dn3" if net <= -3 else
          "flat" if net < 3 else "up3" if net < 10 else "up10")
    db = "d0" if dip <= 2 else "d3" if dip <= 9 else "d10"
    return ab + "|" + nb + "|" + db

def default_band(cat, anchor):
    c = BMAP["cats"].get(cat)
    if not c or c.get("thin"):
        return None
    flats = [b for b in c["bands"] if b["direction"] == "flat"] or c["bands"]
    return min(flats, key=lambda b: abs(b["anchor_med"] - anchor))["band"]

def call_band(cat, anchor, net_h, dip_h):
    cell = (RECOG.get("%s|h%d" % (cat, DECISION_H)) or {}).get(
        pbucket(anchor, net_h, dip_h))
    if cell and cell.get("purity", 0) >= CONF_MIN:
        return cell["top"], cell["purity"], "recognition"
    return default_band(cat, anchor), (cell or {}).get("purity", 0.0), \
        "anchor_default"

legs = []
for line in open(SPEC):
    r = json.loads(line)
    t8 = r["sched"] - 8 * 3600
    cut = t8 + (8 - DECISION_H) * 3600
    day = r["event"].split("-")[1][:7]
    for leg, v in r["legs"].items():
        if not v.get("shape"):
            continue
        ticks = v.get("ticks") or []
        p1 = [lc for ts, b, a, lc in ticks if lc and ts <= cut]
        p2 = [lc for ts, b, a, lc in ticks if lc and ts > cut]
        if not p1 and not p2:
            continue
        net_h = (p1[-1] - p1[0]) if p1 else 0
        dip_h = (v["anchor"] - min(p1)) if p1 else 0
        legs.append({"cat": r["cat"], "day": day, "event": r["event"],
                     "leg": leg, "anchor": v["anchor"], "net_h": net_h,
                     "dip_h": dip_h,
                     "p1_low": (min(p1) if p1 else None),
                     "p2_low": (min(p2) if p2 else None),
                     "close": v["close"],
                     "is_holdout": day >= "26JUL14"
                     and day.startswith("26JUL")})
print("replayable legs (own-frame):", len(legs), flush=True)

def leg_bid(x, depths):
    """Own-frame replay of one leg. Returns (band_used, level, fill_level
    or None, phase)."""
    b1 = default_band(x["cat"], x["anchor"])
    if not b1:
        return None
    r1 = TAB.get(b1) or {}
    d1 = depths.get(b1, r1.get("depth"))
    lvl1 = x["anchor"] - d1 if d1 is not None else None
    if (lvl1 is not None and not r1.get("thin")
            and not (r1.get("kind") == "faller" and (r1.get("roc") or 0) <= 0)
            and lvl1 >= 5 and x["p1_low"] is not None
            and x["p1_low"] <= lvl1):
        return (b1, lvl1, lvl1, 1)
    b2, conf, how = call_band(x["cat"], x["anchor"], x["net_h"], x["dip_h"])
    if not b2:
        return None
    r2 = TAB.get(b2) or {}
    if r2.get("thin") or (r2.get("kind") == "faller"
                          and (r2.get("roc") or 0) <= 0):
        return (b2, None, None, 2)      # refuse/thin at re-aim: no phase-2 bid
    d2 = depths.get(b2, r2.get("depth"))
    if d2 is None:
        return None
    lvl2 = x["anchor"] - d2
    if lvl2 < 5:
        return (b2, None, None, 2)
    if x["p2_low"] is not None and x["p2_low"] <= lvl2:
        return (b2, lvl2, lvl2, 2)
    return (b2, lvl2, None, 2)

def replay(depths, cohort):
    tot = 0.0
    n_bid = n_fill = 0
    per = defaultdict(lambda: [0, 0, 0.0])
    for x in cohort:
        out = leg_bid(x, depths)
        if out is None:
            continue
        band, lvl, fill, phase = out
        if lvl is None and fill is None and phase == 2:
            continue
        n_bid += 1
        per[band][0] += 1
        if fill is not None:
            n_fill += 1
            ret = (x["close"] - fill) / max(fill, 1)
            tot += ret
            per[band][1] += 1
            per[band][2] += ret
    return (tot / max(n_bid, 1), n_bid, n_fill, per)

train = [x for x in legs if not x["is_holdout"]]
hold = [x for x in legs if x["is_holdout"]]
depths = {b: r.get("depth") for b, r in TAB.items()
          if r.get("depth") is not None and not r.get("thin")}
bands = sorted(depths)
L = ["# STAGE 4b — RE-FRAMED DRILL (each strategy in its own frame; "
     "all-window divots, conception casts, touch parks)", ""]
hist = []
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
    if prev_train is not None:
        if tr[0] - prev_train < 0.005 * max(abs(prev_train), 0.01):
            plateau += 1
        else:
            plateau = 0
        if len(hist) >= 3 and hist[-1][2] > hist[-2][2] > hist[-3][2] \
                and hist[-1][2] > 0.01:
            diverge += 1
    prev_train = tr[0]
    if plateau >= 2:
        L.append("- STOP: PLATEAUED.")
        break
    if diverge >= 1:
        L.append("- STOP: DIVERGING (gap rising past 1pt — memorization "
                 "named).")
        break
    accepted = []
    base = tr[0]
    for b in bands:
        best_d, best_s = depths[b], base
        for step in (-3, -2, -1, 1, 2, 3):
            nd = depths[b] + step
            if nd < 1 or nd > 30:
                continue
            cand = dict(depths)
            cand[b] = nd
            s = replay(cand, train)[0]
            if s > best_s:
                best_s, best_d = s, nd
        if best_d != depths[b]:
            accepted.append((b, depths[b], best_d))
            depths[b] = best_d
            base = best_s
    if accepted:
        L.append("    adjusted: " + " · ".join("%s %d→%d" % a
                                               for a in accepted[:8]) +
                 (" (+%d more)" % (len(accepted) - 8)
                  if len(accepted) > 8 else ""))
    else:
        L.append("- STOP: CONVERGED.")
        break

def wilson(k, n):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    z = 1.96
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0, c - h), min(1, c + h))

OLD_FAILS = {"ATP_CHALL-B1", "ATP_MAIN-B5", "ITF_M-B1", "ITF_M-B3",
             "ITF_M-B4", "ITF_W-B1", "ITF_W-B2", "ITF_W-B5", "ITF_W-B7",
             "WTA_CHALL-B6"}
L.append("")
L.append("## VALIDATION REPORT v2 (holdout only) + VERDICT DELTAS vs 4a")
final_ho = replay(depths, hold)
fails2 = []
for band, (nb, nf, sret) in sorted(final_ho[3].items()):
    if nb < 5:
        L.append("- %s: holdout n=%d — TOO THIN (said so)." % (band, nb))
        continue
    lo, hi = wilson(nf, nb)
    roc = sret / nb
    trow = TAB.get(band) or {}
    g = (trow.get("gated_levels") or {}).get(str(depths.get(band)))
    pred = g.get("p_fill", g.get("rate")) if g else None
    ok = not (pred is not None and nb >= 10
              and not (lo <= min(pred, 1.0) <= hi))
    if not ok:
        fails2.append(band)
    delta = ""
    if band in OLD_FAILS:
        delta = " · 4a-FAIL → " + ("PASS: THE FRAME (mis-frame named)"
                                   if ok and roc > 0 else
                                   "STILL FAILS: REAL" if not ok else
                                   "CI-pass but ROC<=0: PARTIAL-FRAME")
    L.append("- %s: depth %d¢ · holdout %d/%d (CI %.2f–%.2f) vs pred %s · "
             "ROC %.4f · %s%s"
             % (band, depths.get(band, -1), nf, nb, lo, hi,
                ("%.2f" % pred) if pred is not None else "n/a", roc,
                "OK" if ok else "FAILS", delta))
L.append("")
L.append("named failures v2: %s" % (fails2 or "none"))

D = ["# REPLAY2 DAY — %s (own-frame; reasoning printed)" % WALK_DAY, ""]
for x in legs:
    if x["day"] != WALK_DAY:
        continue
    out = leg_bid(x, depths)
    if out is None:
        continue
    band, lvl, fill, phase = out
    if lvl is None and fill is None:
        D.append("- %s-%s: re-aim REFUSED at phase 2 (band %s)"
                 % (x["event"][-6:], x["leg"], band))
        continue
    D.append("- %s-%s: anchor %d¢ → band %s (phase %d) · rest %d¢ → %s%s"
             % (x["event"][-6:], x["leg"], x["anchor"], band, phase,
                lvl, "FILLED" if fill else "no fill (honest miss)",
                (" · close %d¢ → %+d¢/sh" % (x["close"], x["close"] - fill))
                if fill else ""))
OUTD.write_text("\n".join(D) + "\n")
OUTJ.write_text(json.dumps({"depths": depths, "campaign": hist,
                            "frame": "own-frame v2 (all-window divots, "
                            "conception casts, touch parks)"}))
OUTM.write_text("\n".join(L) + "\n")
print("CAMPAIGN2-DONE iters:", len(hist), "fails:", fails2)
