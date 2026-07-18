#!/usr/bin/env python3
"""ENTRY SURFACE — STAGE 1: THE BAND TAXONOMY (Range-First Law).

Bands are GIVEN BY THE MARKET: per category (HARD partition), cluster W1
range geometry — anchor level × signed net travel × dip depth — from the
spectrum's legs. No imposed deciles: k-means over standardized features
with k chosen by the largest silhouette-style separation gain across
k=2..8 (method stated plainly; every number reproducible from the
spectrum file). Pairs stay ONE object: each pair reports (fav band, dog
band) — the mirror matrix measures how strongly A's band implies B's.

Deliverable: /tmp/BAND_MAP.md (the operator's read) +
state/band_map_v1.json (boundaries + populations, Stage-2 input; nothing
fits until the operator reads the map).
"""
import json, math, random
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "state/range_spectrum_v1.jsonl"
OUTJ = ROOT / "state/band_map_v1.json"
OUTM = Path("/tmp/BAND_MAP.md")
random.seed(20260717)   # deterministic clustering (reproducible receipts)

legs_by_cat = defaultdict(list)
pairs_by_cat = defaultdict(list)
for line in open(SPEC):
    r = json.loads(line)
    ls = {k: v for k, v in r["legs"].items() if v.get("shape")}
    row = {}
    for leg, v in ls.items():
        row[leg] = (v["anchor"], v["net"], v["anchor"] - v["low"])
        legs_by_cat[r["cat"]].append(row[leg])
    if len(ls) == 2:
        items = sorted(ls.items(), key=lambda kv: kv[1]["anchor"],
                       reverse=True)
        pairs_by_cat[r["cat"]].append((row[items[0][0]], row[items[1][0]]))

def kmeans(X, k, iters=60):
    cents = random.sample(X, k)
    for _ in range(iters):
        groups = [[] for _ in range(k)]
        for x in X:
            j = min(range(k), key=lambda i: sum(
                (a - b) ** 2 for a, b in zip(x, cents[i])))
            groups[j].append(x)
        newc = []
        for g, c in zip(groups, cents):
            newc.append(tuple(sum(v[d] for v in g) / len(g)
                              for d in range(len(X[0]))) if g else c)
        if newc == cents:
            break
        cents = newc
    return cents, groups

def inertia(groups, cents):
    s = 0.0
    for g, c in zip(groups, cents):
        for x in g:
            s += sum((a - b) ** 2 for a, b in zip(x, c))
    return s

def standardize(rows):
    cols = list(zip(*rows))
    mus = [sum(c) / len(c) for c in cols]
    sds = [max((sum((v - m) ** 2 for v in c) / len(c)) ** 0.5, 1e-9)
           for c, m in zip(cols, mus)]
    Z = [tuple((v - m) / s for v, m, s in zip(r, mus, sds)) for r in rows]
    return Z, mus, sds

band_map = {"built_from": str(SPEC), "method":
            "k-means on standardized (anchor, net, dip); k by max relative "
            "inertia-drop gain over k=2..8 (elbow), deterministic seed "
            "20260717; per-cat HARD partition", "cats": {}}
L = ["# ENTRY SURFACE — STAGE 1: THE BAND MAP (bands given by the market)",
     "", "method: %s" % band_map["method"], ""]

for cat, rows in sorted(legs_by_cat.items()):
    if len(rows) < 60:
        L.append("## %s — THIN (n=%d): no taxonomy fitted; says thin."
                 % (cat, len(rows)))
        band_map["cats"][cat] = {"thin": True, "n": len(rows)}
        continue
    Z, mus, sds = standardize(rows)
    prev = None
    scores = {}
    fits = {}
    for k in range(2, 9):
        cents, groups = kmeans(Z, k)
        ine = inertia(groups, cents)
        fits[k] = (cents, groups, ine)
        if prev is not None:
            scores[k] = (prev - ine) / prev
        prev = ine
    # elbow: last k whose relative gain >= 12% (decreed elbow bar, stated)
    k_star = max([k for k, g in scores.items() if g >= 0.12] or [2])
    cents, groups, _ = fits[k_star]
    # describe each band in RAW units, ordered by anchor
    described = []
    for c, g in zip(cents, groups):
        if not g:
            continue
        raw = [(z[0] * sds[0] + mus[0], z[1] * sds[1] + mus[1],
                z[2] * sds[2] + mus[2]) for z in g]
        anchors = sorted(x[0] for x in raw)
        nets = sorted(x[1] for x in raw)
        dips = sorted(x[2] for x in raw)
        described.append({
            "n": len(g),
            "anchor_lo": round(anchors[int(0.05 * len(anchors))]),
            "anchor_hi": round(anchors[int(0.95 * len(anchors)) - 1]),
            "anchor_med": round(anchors[len(anchors) // 2]),
            "net_med": round(nets[len(nets) // 2], 1),
            "direction": ("riser" if nets[len(nets) // 2] >= 2 else
                          "faller" if nets[len(nets) // 2] <= -2 else
                          "flat"),
            "dip_med": round(dips[len(dips) // 2], 1),
            "width_p75": round(sorted(abs(x[1]) for x in raw)
                               [int(0.75 * len(raw))], 1)})
    described.sort(key=lambda b: b["anchor_med"])
    for i, b in enumerate(described):
        b["band"] = "%s-B%d" % (cat, i + 1)
    band_map["cats"][cat] = {"k": k_star, "n": len(rows),
                             "elbow_gains": {str(k): round(g, 3)
                                             for k, g in scores.items()},
                             "bands": described,
                             "feature_mus": mus, "feature_sds": sds,
                             "centroids_z": [list(c) for c in cents]}
    L.append("## %s — %d natural bands (n=%d legs; elbow gains %s)"
             % (cat, k_star, len(rows),
                {k: round(g, 2) for k, g in scores.items()}))
    for b in described:
        L.append("- **%s** n=%d · anchors %d–%d (med %d) · %s "
                 "(net med %+0.1f¢, width p75 %.1f¢) · dip med %.1f¢"
                 % (b["band"], b["n"], b["anchor_lo"], b["anchor_hi"],
                    b["anchor_med"], b["direction"].upper(),
                    b["net_med"], b["width_p75"], b["dip_med"]))
    # pair mirror: assign each pair's two legs to bands, count joints
    def assign(x):
        z = tuple((v - m) / s for v, m, s in zip(x, mus, sds))
        j = min(range(len(cents)), key=lambda i: sum(
            (a - b) ** 2 for a, b in zip(z, cents[i])))
        # map centroid index -> described band label via nearest anchor_med
        return j
    # build centroid->band-label map by describing in same order as cents
    cent_label = {}
    for ci, (c, g) in enumerate(zip(cents, groups)):
        if not g:
            continue
        raws = sorted(z[0] * sds[0] + mus[0] for z in g)
        amed = round(raws[len(raws) // 2])
        best = min(described, key=lambda b: abs(b["anchor_med"] - amed))
        cent_label[ci] = best["band"]
    mirror = Counter()
    for fav, dog in pairs_by_cat.get(cat, []):
        mirror[(cent_label.get(assign(fav), "?"),
                cent_label.get(assign(dog), "?"))] += 1
    top = mirror.most_common(6)
    tot = sum(mirror.values())
    if tot:
        L.append("  PAIR MIRROR (fav-band → dog-band, one object): " +
                 " · ".join("%s→%s %d (%.0f%%)" % (a, b, n, 100.0 * n / tot)
                            for (a, b), n in top))
        band_map["cats"][cat]["pair_mirror"] = {
            "%s|%s" % k: v for k, v in mirror.items()}
    L.append("")

OUTJ.write_text(json.dumps(band_map))
OUTM.write_text("\n".join(L) + "\n")
print("\n".join(L))
