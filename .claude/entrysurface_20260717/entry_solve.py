#!/usr/bin/env python3
"""STAGE 3 — THE GATED JOINT SOLVE (Range-First Law; W1 only, ever).

Inputs: band_map_v1 (parent key) · drift_surfaces_v1 (reach curves) ·
divot_tables_v1 (catch tables) · the spectrum (holdout + era-proof).

June's rigor, in order:
  UNITY       — all probabilities are empirical counts over their own
                denominators; reach curves are survival curves by
                construction (monotone, <=1); expected divot catches are
                RATES (E[catches/window]) used as rates — no distribution
                poetry anywhere.
  REALISM GATE— a candidate level exists ONLY where the tape proves it
                printable: reach support >= MIN_TOUCH legs (fallers/risers)
                or catch support >= MIN_CATCH divots (flats). Ungated
                levels DO NOT ENTER the optimization.
  GATED OPTIMA— per band: argmax over gated levels of ROC.
  ROC (the deploy metric, frame stated plainly):
    faller cast at depth d:  ROC = P(dip>=d) * (net_med + d) / (anchor-d)
    riser park at depth d:   same formula (net_med positive; d in 0..2)
    flat divot bid at d:     ROC = E[catches/win] * d / (anchor-d)
    Mark = the band's W1 close (close-based, conservative; exit-frame
    blending is Stage 6's word, not assumed here).
  HOLDOUT     — reach curves refit on the pre-Jul-14 era; the era-chosen
                depth judged on Jul-14+ legs only (realized P(fill) vs
                predicted + realized ROC). First cut of the operator's
                loop; the full solve-replay LOOP spec rides Stage 4.
  ERA-PROOF   — the same solve with windows cut at the OLD stamps
                (old_stamp_last as the right edge): divergence per band
                posted in cents (optimal depth shift + ROC delta). Bands
                whose answer didn't move say so — information, not failure.
Output: state/entry_tables_v1.json + /tmp/ENTRY_SOLVE.md (staged for the
Stage-5 seal; nothing arms).
"""
import json, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BMAP = json.loads((ROOT / "state/band_map_v1.json").read_text())
DRIFT = json.loads((ROOT / "state/drift_surfaces_v1.json").read_text())
DIVOT = json.loads((ROOT / "state/divot_tables_v1.json").read_text())
SPEC = ROOT / "state/range_spectrum_v1.jsonl"
CORPUS = {json.loads(l)["event"]: json.loads(l)
          for l in open(ROOT / "state/corpus_events_v2.jsonl")}
OUTJ = ROOT / "state/entry_tables_v1.json"
OUTM = Path("/tmp/ENTRY_SOLVE.md")

MIN_TOUCH = 8      # realism gate: legs that touched the level (fallers/risers)
MIN_CATCH = 8      # realism gate: divots at the level (flats)
HOLDOUT_SPLIT = "26JUL14"   # pre-Jul-14 = fit era; Jul-14+ = held-out

def band_meta(band):
    cat = band.split("-")[0]
    for b in BMAP["cats"][cat]["bands"]:
        if b["band"] == band:
            return b
    return None

def assign_band(cat, anchor, net, dip):
    c = BMAP["cats"].get(cat)
    if not c or c.get("thin"):
        return None
    mus, sds = c["feature_mus"], c["feature_sds"]
    z = tuple((v - m) / s for v, m, s in zip((anchor, net, dip), mus, sds))
    cents = c["centroids_z"]
    j = min(range(len(cents)), key=lambda i: sum(
        (a - b) ** 2 for a, b in zip(z, cents[i])))
    amed = cents[j][0] * sds[0] + mus[0]
    return min(c["bands"], key=lambda b: abs(b["anchor_med"] - amed))["band"]

def leg_date_key(event):
    # "-26JUL17XXX" -> "26JUL17" (sortable within month strings by day)
    try:
        return event.split("-")[1][:7]
    except IndexError:
        return "?"

def solve_band(band, reach, reach_den, net_med, anchor_med, kind, catch=None,
               windows=None):
    """Return (best_depth, roc, gated_levels) under the realism gate."""
    best = None
    gated = {}
    depths = range(0, 3) if kind == "riser" else range(1, 31)
    for d in depths:
        if kind == "flat":
            c = (catch or {}).get(str(d)) or {}
            support = c.get("divots_caught", 0)
            if support < MIN_CATCH:
                continue
            rate = c.get("per_window", 0.0)
            denom = max(anchor_med - d, 1)
            roc = rate * d / denom
            gated[d] = {"rate": rate, "roc": round(roc, 4)}
        else:
            p = reach.get(str(d))
            if p is None:
                continue
            support = int(round(p * reach_den))
            if support < MIN_TOUCH:
                continue
            ev = net_med + d
            denom = max(anchor_med - d, 1)
            roc = p * ev / denom
            gated[d] = {"p_fill": p, "ev_c": round(ev, 1),
                        "roc": round(roc, 4)}
        if best is None or gated[d]["roc"] > best[1]:
            best = (d, gated[d]["roc"])
    return best, gated

# ---- main solve on the clean surfaces -----------------------------------
tables = {}
L = ["# STAGE 3 — THE GATED JOINT SOLVE (per band; ROC the metric; "
     "close-based mark, frame stated in the header)", ""]
for band, surf in sorted(DRIFT["bands"].items()):
    meta = band_meta(band)
    if not meta:
        continue
    n = surf["n"]
    kind = meta["direction"] if meta["direction"] in ("riser", "flat") \
        else "faller"
    catch = (DIVOT["bands"].get(band) or {}).get("catch")
    windows = (DIVOT["bands"].get(band) or {}).get("windows")
    best, gated = solve_band(band, surf.get("reach") or {}, n,
                             meta["net_med"], meta["anchor_med"], kind,
                             catch, windows)
    row = {"n": n, "kind": kind, "anchor_med": meta["anchor_med"],
           "net_med": meta["net_med"], "gated_levels": gated,
           "thin": n < 30}
    if best:
        row["depth"] = best[0]
        row["roc"] = best[1]
    tables[band] = row
    if n < 30:
        L.append("- %s (%s, n=%d): THIN — inherits nothing; table row "
                 "recorded, decision-grade NO." % (band, kind, n))
        continue
    if not best:
        L.append("- %s (%s, n=%d): NO GATED LEVEL passes realism — the "
                 "tape never proved a printable level at support >= %d. "
                 "The solve REFUSES." % (band, kind, n, MIN_TOUCH))
        continue
    d, roc = best
    extra = gated[d]
    L.append("- **%s** (%s, n=%d, anchor~%d, net_med %+0.1f): depth **%d¢** "
             "→ ROC %.4f · %s"
             % (band, kind, n, meta["anchor_med"], meta["net_med"], d, roc,
                {k: v for k, v in extra.items() if k != "roc"}))

# ---- pair-aware joints (dominant mirrors) --------------------------------
L.append("")
L.append("## PAIR JOINTS (both legs one object; dominant mirrors from the "
         "band map; combined ROC = capital-weighted; <=97 scoreboard noted)")
joints = {}
for cat, c in BMAP["cats"].items():
    pm = c.get("pair_mirror") or {}
    for key, cnt in sorted(pm.items(), key=lambda kv: -kv[1])[:3]:
        fb, db = key.split("|")
        tf, td = tables.get(fb), tables.get(db)
        if not tf or not td or "depth" not in tf or "depth" not in td:
            continue
        lf = tf["anchor_med"] - tf["depth"]
        ld = td["anchor_med"] - td["depth"]
        cap = lf + ld
        wroc = (tf["roc"] * lf + td["roc"] * ld) / max(cap, 1)
        joints["%s|%s" % (fb, db)] = {
            "pairs_n": cnt, "fav_level": lf, "dog_level": ld,
            "combined_at_levels": cap, "weighted_roc": round(wroc, 4)}
        L.append("- %s→%s (n=%d pairs): fav %d¢ + dog %d¢ = combined %d "
                 "(scoreboard %s 97) · weighted ROC %.4f"
                 % (fb, db, cnt, lf, ld, cap,
                    "<=" if cap <= 97 else ">", wroc))

# ---- holdout: refit reach on pre-Jul-14, judge on Jul-14+ ---------------
L.append("")
L.append("## HOLDOUT (fit pre-Jul-14 · judged ONLY on Jul-14+ legs)")
fit_reach = defaultdict(lambda: defaultdict(int))
fit_n = defaultdict(int)
ho_touch = defaultdict(lambda: defaultdict(int))
ho_n = defaultdict(int)
ho_roc = defaultdict(list)
for line in open(SPEC):
    r = json.loads(line)
    cat = r["cat"]
    dk = leg_date_key(r["event"])
    is_holdout = dk >= HOLDOUT_SPLIT or not dk.startswith("26JUL")
    # months before July are fit-era; July splits at the 14th
    if not dk.startswith("26JUL"):
        is_holdout = False
    for leg, v in r["legs"].items():
        if not v.get("shape"):
            continue
        band = assign_band(cat, v["anchor"], v["net"],
                           v["anchor"] - v["low"])
        if not band:
            continue
        dip = v["anchor"] - v["low"]
        if is_holdout:
            ho_n[band] += 1
            for d in range(1, 31):
                if dip >= d:
                    ho_touch[band][d] += 1
        else:
            fit_n[band] += 1
            for d in range(1, 31):
                if dip >= d:
                    fit_reach[band][d] += 1
for band, row in sorted(tables.items()):
    if row.get("thin") or "depth" not in row or row["kind"] == "flat":
        continue
    if fit_n[band] < 30 or ho_n[band] < 10:
        continue
    # era-chosen depth from FIT reach only
    meta = band_meta(band)
    fr = {str(d): fit_reach[band][d] / fit_n[band] for d in range(1, 31)}
    best_fit, _ = solve_band(band, fr, fit_n[band], meta["net_med"],
                             meta["anchor_med"], row["kind"])
    if not best_fit:
        continue
    dfit = best_fit[0]
    pred = fr.get(str(dfit), 0)
    real = ho_touch[band][dfit] / ho_n[band]
    ev = meta["net_med"] + dfit
    roc_real = real * ev / max(meta["anchor_med"] - dfit, 1)
    L.append("- %s: fit-era depth %d¢ · predicted P(fill) %.2f vs "
             "HELD-OUT realized %.2f (n=%d) · held-out ROC %.4f"
             % (band, dfit, pred, real, ho_n[band], roc_real))
    tables[band]["holdout"] = {"depth_fit": dfit, "p_pred": round(pred, 3),
                               "p_realized": round(real, 3),
                               "n_holdout": ho_n[band],
                               "roc_realized": round(roc_real, 4)}

# ---- era-proof: same solve with OLD-stamp windows ------------------------
L.append("")
L.append("## ERA-PROOF (identical solve, windows cut at the OLD stamps — "
         "the poisoned clocks; divergence per band in cents)")
old_reach = defaultdict(lambda: defaultdict(int))
old_n = defaultdict(int)
for line in open(SPEC):
    r = json.loads(line)
    cat = r["cat"]
    cr = CORPUS.get(r["event"]) or {}
    old_edge = cr.get("old_stamp_last")
    if not old_edge:
        continue
    t8 = r["sched"] - 8 * 3600
    for leg, v in r["legs"].items():
        if not v.get("shape"):
            continue
        band = assign_band(cat, v["anchor"], v["net"],
                           v["anchor"] - v["low"])
        if not band:
            continue
        # recut the leg's dip under the OLD window (ticks up to old edge)
        lows = [lc for ts, b, a, lc in (v.get("ticks") or [])
                if lc and ts <= old_edge]
        if not lows:
            continue
        old_dip = v["anchor"] - min(lows)
        old_n[band] += 1
        for d in range(1, 31):
            if old_dip >= d:
                old_reach[band][d] += 1
n_moved = n_same = 0
for band, row in sorted(tables.items()):
    if row.get("thin") or "depth" not in row or row["kind"] == "flat":
        continue
    if old_n[band] < 30:
        continue
    meta = band_meta(band)
    orch = {str(d): old_reach[band][d] / old_n[band] for d in range(1, 31)}
    best_old, _ = solve_band(band, orch, old_n[band], meta["net_med"],
                             meta["anchor_med"], row["kind"])
    if not best_old:
        continue
    shift = best_old[0] - row["depth"]
    if shift == 0:
        n_same += 1
        L.append("- %s: answer DID NOT MOVE (depth %d¢ both eras) — "
                 "information, not failure." % (band, row["depth"]))
    else:
        n_moved += 1
        L.append("- %s: clean depth %d¢ vs poisoned depth %d¢ — "
                 "**divergence %+d¢** (the lying clocks would have cast "
                 "%s)" % (band, row["depth"], best_old[0], shift,
                          "deeper" if shift > 0 else "shallower"))
    tables[band]["era_proof"] = {"old_depth": best_old[0],
                                 "divergence_c": shift,
                                 "n_old": old_n[band]}
L.append("")
L.append("era-proof summary: %d bands moved · %d unchanged" % (n_moved, n_same))

OUTJ.write_text(json.dumps({"frame": "close-based mark; W1 only; "
                            "realism gate MIN_TOUCH=%d MIN_CATCH=%d"
                            % (MIN_TOUCH, MIN_CATCH),
                            "tables": tables, "joints": joints}))
OUTM.write_text("\n".join(L) + "\n")
print("SOLVE-DONE bands:", len(tables), "joints:", len(joints))
print("\n".join(L[:18]))
