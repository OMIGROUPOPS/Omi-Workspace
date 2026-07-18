#!/usr/bin/env python3
"""STAGE 2 P1 — THE DRIFT SURFACES, per band per cat (Range-First Law;
band map v1 = the parent key). Off the spectrum, both legs one object.

Per band:
  MOVEMENT  — (price − anchor) quartiles by 30-min tts bucket, three
              series (bid / ask / traded)
  LIFECYCLE — level-bucket × tts-bucket → P(next-30m rise / fall / flat)
              (traded series; entry-side action grammar)
  REACH     — P(dip ≥ d by tts) for d in 1..15 + dip-bottom timing
              distribution (when the low prints, per band)
  RECOGNITION — at each hour into the window: partial-journey bucket
              (net-so-far × dip-so-far) → eventual-band distribution;
              the table answers "at T−6h, X% of eventual risers are
              already distinguishable" with n. No fitting — counted.
Outputs: state/drift_surfaces_v1.json + /tmp/DRIFT_SURFACES.md.
Conditioning axes deferred where n is thin — thin says thin (the
honest-n map is in the doc).
"""
import json, statistics
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "state/range_spectrum_v1.jsonl"
BMAP = json.loads((ROOT / "state/band_map_v1.json").read_text())
OUTJ = ROOT / "state/drift_surfaces_v1.json"
OUTM = Path("/tmp/DRIFT_SURFACES.md")

def assign_band(cat, anchor, net, dip):
    c = BMAP["cats"].get(cat)
    if not c or c.get("thin"):
        return None
    mus, sds = c["feature_mus"], c["feature_sds"]
    z = tuple((v - m) / s for v, m, s in zip((anchor, net, dip), mus, sds))
    cents = c["centroids_z"]
    j = min(range(len(cents)), key=lambda i: sum(
        (a - b) ** 2 for a, b in zip(z, cents[i])))
    # centroid -> band label via nearest anchor med (mirrors the builder)
    amed = cents[j][0] * sds[0] + mus[0]
    best = min(c["bands"], key=lambda b: abs(b["anchor_med"] - amed))
    return best["band"]

TTS_BIN = 1800.0
move = defaultdict(lambda: defaultdict(lambda: {"bid": [], "ask": [],
                                                "trd": []}))
life = defaultdict(lambda: defaultdict(Counter))
reach = defaultdict(lambda: defaultdict(int))
reach_n = defaultdict(int)
low_frac = defaultdict(list)
recog = defaultdict(lambda: defaultdict(Counter))   # hour -> pbucket -> band
band_n = Counter()

def lvl_bucket(p):
    return "le25" if p <= 25 else "26_50" if p <= 50 else \
        "51_75" if p <= 75 else "ge76"

def pbucket(anchor, net, dip):
    # [v2 fix, named in the C50] v1 omitted the ANCHOR from the partial
    # fingerprint — flats in different anchor regions (dog-basement vs
    # fav-ceiling) were asked to separate on net/dip alone: a designed 0%.
    # The fingerprint is (anchor region x net-so-far x dip-so-far).
    ab = ("a25" if anchor <= 25 else "a50" if anchor <= 50 else
          "a75" if anchor <= 75 else "a95")
    nb = ("dn10" if net <= -10 else "dn3" if net <= -3 else
          "flat" if net < 3 else "up3" if net < 10 else "up10")
    db = "d0" if dip <= 2 else "d3" if dip <= 9 else "d10"
    return ab + "|" + nb + "|" + db

n_legs = 0
for line in open(SPEC):
    r = json.loads(line)
    cat = r["cat"]
    t8 = r["sched"] - 8 * 3600
    redge = r["right_edge"]
    for leg, v in r["legs"].items():
        if not v.get("shape"):
            continue
        band = assign_band(cat, v["anchor"], v["net"],
                           v["anchor"] - v["low"])
        if not band:
            continue
        n_legs += 1
        band_n[band] += 1
        anchor = v["anchor"]
        ticks = v.get("ticks") or []
        # movement + lifecycle + reach off the tick series
        lows_so_far = None
        prev_trd_bin = {}
        for ts, b, a, lc in ticks:
            tts_min = (redge - ts) / 60.0
            bin_i = int(max(0.0, (redge - ts)) // TTS_BIN)
            m = move[band][bin_i]
            if b:
                m["bid"].append(b - anchor)
            if a:
                m["ask"].append(a - anchor)
            if lc:
                m["trd"].append(lc - anchor)
                prev_trd_bin.setdefault(bin_i, []).append(lc)
                lows_so_far = lc if lows_so_far is None else \
                    min(lows_so_far, lc)
        # lifecycle: per adjacent bin pair, action = sign of median move
        bins = sorted(prev_trd_bin.keys(), reverse=True)   # far -> near
        for i in range(len(bins) - 1):
            b0, b1 = bins[i], bins[i + 1]
            m0 = statistics.median(prev_trd_bin[b0])
            m1 = statistics.median(prev_trd_bin[b1])
            act = "rise" if m1 - m0 >= 2 else \
                "fall" if m1 - m0 <= -2 else "flat"
            life[band][(lvl_bucket(m0), b0)][act] += 1
        # reach + low timing
        dip = anchor - v["low"]
        reach_n[band] += 1
        for d in range(1, 31):
            if dip >= d:
                reach[band][d] += 1
        low_frac[band].append(v.get("low_frac", 0))
        # recognition: partial features at each hour into the window
        for h in range(1, 8):
            cut = t8 + h * 3600
            seen = [(ts, lc) for ts, b, a, lc in ticks
                    if lc and ts <= cut]
            if not seen:
                continue
            first = seen[0][1]
            net_h = seen[-1][1] - first
            dip_h = anchor - min(x[1] for x in seen)
            recog[cat + "|h%d" % h][pbucket(anchor, net_h, dip_h)][band] += 1

# ---- write ---------------------------------------------------------------
def q(v):
    v = sorted(v)
    n = len(v)
    return [round(v[int(p * n)] if int(p * n) < n else v[-1], 1)
            for p in (0.25, 0.5, 0.75)] if v else None

out = {"built_from": str(SPEC), "band_map": "band_map_v1", "bands": {}}
L = ["# STAGE 2 — THE DRIFT SURFACES (per band; honest-n map inline)", ""]
for band in sorted(band_n):
    n = band_n[band]
    ms = {}
    for bin_i, m in sorted(move[band].items()):
        ms[str(bin_i)] = {k: q(vv) for k, vv in m.items() if vv}
    rc = {str(d): round(reach[band][d] / reach_n[band], 3)
          for d in range(1, 31)} if reach_n[band] else {}
    lf = q(low_frac[band])
    lc = {}
    for (lvl, bin_i), c in life[band].items():
        tot = sum(c.values())
        if tot >= 8:
            lc["%s@%d" % (lvl, bin_i)] = {
                "n": tot, "rise": round(c["rise"] / tot, 2),
                "fall": round(c["fall"] / tot, 2),
                "flat": round(c["flat"] / tot, 2)}
    out["bands"][band] = {"n": n, "movement": ms, "reach": rc,
                          "low_frac_q": lf, "lifecycle": lc}
    L.append("## %s (n=%d)" % (band, n))
    if n < 30:
        L.append("- THIN: surfaces recorded, decision-grade NO.")
    if rc:
        L.append("- reach: P(dip>=3) %.2f · P(>=5) %.2f · P(>=10) %.2f · "
                 "low timing (frac of window, q25/50/75): %s"
                 % (float(rc.get("3", 0)), float(rc.get("5", 0)),
                    float(rc.get("10", 0)), lf))
    mv0 = ms.get("0") or {}
    mv15 = ms.get("15") or {}
    L.append("- movement (px−anchor q25/50/75): @edge %s · @T−7.5h %s"
             % (mv0.get("trd"), mv15.get("trd")))
L.append("")
L.append("## RECOGNITION TABLE (partial journey → eventual band; counted, "
         "not fitted)")
out["recognition"] = {}
for key in sorted(recog):
    cells = recog[key]
    total = sum(sum(c.values()) for c in cells.values())
    # distinguishability: share of legs sitting in a partial-bucket whose
    # dominant eventual band has >=60% purity (n>=10 cells only)
    disting = 0
    for pb, c in cells.items():
        tot = sum(c.values())
        if tot >= 10 and c.most_common(1)[0][1] / tot >= 0.6:
            disting += tot
    out["recognition"][key] = {
        pb: {"n": sum(c.values()),
             "top": c.most_common(1)[0][0],
             "purity": round(c.most_common(1)[0][1] / sum(c.values()), 2)}
        for pb, c in cells.items() if sum(c.values()) >= 10}
    if total:
        L.append("- %s: %d legs observed · %.0f%% sit in a >=60%%-pure "
                 "partial bucket (n>=10 buckets only)"
                 % (key, total, 100.0 * disting / total))
OUTJ.write_text(json.dumps(out))
OUTM.write_text("\n".join(L) + "\n")
print("legs surfaced:", n_legs, "bands:", len(band_n))
print("\n".join(L[:14]))
