#!/usr/bin/env python3
"""P3 — THE DIVOT DECONSTRUCTION, on the consolidated store (flat bands;
ITF prioritized — divots are their ENTIRE entry story per the drift
surfaces).

Definition (operational, stated plainly): within a leg's window
(T−8h → right edge), a DIVOT is a print ≥2¢ BELOW the trailing-30-min
rolling median of prints, followed by recovery (a later print within
the window back within 1¢ of that median). Depth = median − print low
of the excursion; duration = first-sub-print → recovery print.

Per FLAT band per cat, from the store's prints joined to the spectrum's
flat-band legs (public_tape prints preferred; book_transition where the
tape has no coverage — source share reported):
  frequency per window · depth distribution · duration distribution ·
  clustering vs volume onset (share of divots inside the first
  30 min after the leg's wake) · REACHABILITY: a resting bid at
  anchor−X catches how many divots per window, at what P(≥1 catch).
Deliverable: /tmp/DIVOT_TABLES.md + state/divot_tables_v1.json + the
walked exhibit (the busiest ITF flat leg, every divot listed).
"""
import json, sqlite3, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "state/range_spectrum_v1.jsonl"
BMAP = json.loads((ROOT / "state/band_map_v1.json").read_text())
DB = ROOT / "state/subsecond_store.db"
OUTM = Path("/tmp/DIVOT_TABLES.md")
OUTJ = ROOT / "state/divot_tables_v1.json"

FLAT = {}
for cat, c in BMAP["cats"].items():
    if c.get("thin"):
        continue
    for b in c["bands"]:
        if b["direction"] == "flat":
            FLAT.setdefault(cat, []).append(b)

def assign_flat(cat, anchor, net, dip):
    c = BMAP["cats"].get(cat)
    if not c or c.get("thin"):
        return None
    mus, sds = c["feature_mus"], c["feature_sds"]
    z = tuple((v - m) / s for v, m, s in zip((anchor, net, dip), mus, sds))
    cents = c["centroids_z"]
    j = min(range(len(cents)), key=lambda i: sum(
        (a - b) ** 2 for a, b in zip(z, cents[i])))
    amed = cents[j][0] * sds[0] + mus[0]
    best = min(c["bands"], key=lambda b: abs(b["anchor_med"] - amed))
    return best["band"] if best["direction"] == "flat" else None

con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=10)
stats = defaultdict(lambda: {"windows": 0, "divots": 0, "depths": [],
                             "durs": [], "near_wake": 0,
                             "catch": defaultdict(int), "src": defaultdict(int)})
exhibit = None

n_done = 0
for line in open(SPEC):
    r = json.loads(line)
    cat = r["cat"]
    if cat not in FLAT:
        continue
    t8 = r["sched"] - 8 * 3600
    redge = r["right_edge"]
    for leg, v in r["legs"].items():
        if not v.get("shape"):
            continue
        band = assign_flat(cat, v["anchor"], v["net"], v["anchor"] - v["low"])
        if not band:
            continue
        tk = r["event"] + "-" + leg
        rows = con.execute(
            "SELECT ts, price, src FROM prints WHERE ticker=? AND ts>=? "
            "AND ts<=? ORDER BY ts", (tk, t8, redge)).fetchall()
        if len(rows) < 10:
            continue
        st = stats[band]
        st["windows"] += 1
        for _, _, s in rows:
            st["src"][s] += 1
        anchor = v["anchor"]
        wake = rows[0][0]
        # rolling median over trailing 30 min
        window = []
        divots = []
        cur = None   # (start_ts, low, med_at_start)
        for ts, px, s in rows:
            window = [(t, p) for t, p in window if t >= ts - 1800]
            med = statistics.median([p for _, p in window]) if window else px
            window.append((ts, px))
            if cur is None and window and px <= med - 2:
                cur = [ts, px, med]
            elif cur is not None:
                if px < cur[1]:
                    cur[1] = px
                if px >= cur[2] - 1:      # recovered
                    divots.append((cur[0], cur[1], cur[2], ts))
                    cur = None
        for (ts0, low, med, ts1) in divots:
            st["divots"] += 1
            st["depths"].append(med - low)
            st["durs"].append(ts1 - ts0)
            if ts0 - wake <= 1800:
                st["near_wake"] += 1
            for d in range(1, 13):
                if low <= anchor - d:
                    st["catch"][d] += 1
        if divots and cat.startswith("KXITF") is False and cat in ("ITF_M", "ITF_W"):
            pass
        if divots and cat in ("ITF_M", "ITF_W"):
            if exhibit is None or len(divots) > len(exhibit["divots"]):
                exhibit = {"ticker": tk, "band": band, "anchor": anchor,
                           "n_prints": len(rows),
                           "divots": [(round(a), l, round(m, 1), round(b))
                                      for a, l, m, b in divots][:20]}
        n_done += 1

def q(v, p):
    v = sorted(v)
    return round(v[min(len(v) - 1, int(p * len(v)))], 1) if v else None

out = {"definition": "print >=2c under trailing-30min rolling median, "
                     "recovery within 1c of that median", "bands": {}}
L = ["# P3 — THE DIVOT TABLES (flat bands; the flat-band entry model)", "",
     "definition: %s" % out["definition"], ""]
for band in sorted(stats):
    st = stats[band]
    if not st["windows"]:
        continue
    freq = st["divots"] / st["windows"]
    row = {"windows": st["windows"], "divots": st["divots"],
           "per_window": round(freq, 2),
           "depth_p50": q(st["depths"], 0.5),
           "depth_p90": q(st["depths"], 0.9),
           "dur_p50_s": q(st["durs"], 0.5),
           "near_wake_share": (round(st["near_wake"] / st["divots"], 2)
                               if st["divots"] else None),
           "src_share": {k: round(v / sum(st["src"].values()), 2)
                         for k, v in st["src"].items()},
           "catch": {str(d): {"divots_caught": st["catch"][d],
                              "per_window": round(st["catch"][d]
                                                  / st["windows"], 2)}
                     for d in range(1, 13)}}
    out["bands"][band] = row
    L.append("## %s (windows %d · divots %d · %.2f/window)"
             % (band, st["windows"], st["divots"], freq))
    L.append("- depth p50/p90: %s/%s¢ · duration p50: %ss · near-wake "
             "share: %s · print sources: %s"
             % (row["depth_p50"], row["depth_p90"], row["dur_p50_s"],
                row["near_wake_share"], row["src_share"]))
    L.append("- catch table (bid at anchor−X¢ → divots/window): " +
             " · ".join("X=%d: %.2f" % (d, st["catch"][d] / st["windows"])
                        for d in (1, 2, 3, 4, 5, 6, 8, 10)))
    L.append("")
if exhibit:
    L.append("## WALKED EXHIBIT — %s (band %s, anchor %d¢, %d prints)"
             % (exhibit["ticker"], exhibit["band"], exhibit["anchor"],
                exhibit["n_prints"]))
    L.append("every divot a resting bid would have caught "
             "(start_ep, low¢, median-at-start¢, recovery_ep):")
    for d in exhibit["divots"]:
        L.append("- %s" % (d,))
OUTJ.write_text(json.dumps(out))
OUTM.write_text("\n".join(L) + "\n")
print("flat legs processed:", n_done, "| bands:", len(out["bands"]))
print("\n".join(L[:12]))
