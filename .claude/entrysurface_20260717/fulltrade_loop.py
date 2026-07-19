#!/usr/bin/env python3
"""FULL-TRADE LOOP — P1 capture autopsy · P3 exit half · P4 blended drill.
One chained run; each part writes its own artifact. Frames stated inline.
"""
import json, math, sqlite3
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BMAP = json.loads((ROOT / "state/band_map_v1.json").read_text())
TAB = json.loads((ROOT / "state/entry_tables_v1.json").read_text())["tables"]
DRIFT = json.loads((ROOT / "state/drift_surfaces_v1.json").read_text())
SPEC = ROOT / "state/range_spectrum_v1.jsonl"
RECOG = DRIFT.get("recognition", {})

def default_band(cat, anchor):
    c = BMAP["cats"].get(cat)
    if not c or c.get("thin"):
        return None
    flats = [b for b in c["bands"] if b["direction"] == "flat"] or c["bands"]
    return min(flats, key=lambda b: abs(b["anchor_med"] - anchor))["band"]

# ================= P1 — CAPTURE AUTOPSY ==================================
log = sorted((ROOT / "logs").glob("live_v3_2026071[89].jsonl"))[-1]
posted, filled = {}, set()
for line in open(log, encoding="utf-8", errors="replace"):
    if '"order_placed"' in line or '"entry_filled"' in line:
        try:
            j = json.loads(line)
        except ValueError:
            continue
        tk = j.get("ticker") or ""
        d = j.get("details") or {}
        if j["event"] == "entry_filled":
            filled.add(tk)
        elif d.get("action") == "buy":
            posted.setdefault(tk, []).append((j.get("ts_epoch"),
                                              d.get("price")))
unfilled = {tk: v for tk, v in posted.items() if tk not in filled}
con = sqlite3.connect("file:%s?mode=ro" % (ROOT / "state/subsecond_store.db"),
                      uri=True, timeout=10)
classes = Counter()
rows = []
for tk, bids in unfilled.items():
    cat = ("ATP_CHALL" if tk.startswith("KXATPCHALLENGER") else
           "WTA_CHALL" if tk.startswith("KXWTACHALLENGER") else
           "ITF_W" if tk.startswith("KXITFW") else
           "ITF_M" if tk.startswith("KXITF") else
           "WTA_MAIN" if tk.startswith("KXWTA") else "ATP_MAIN")
    lvl = bids[-1][1]
    t0 = min(b[0] for b in bids if b[0])
    prints = [p for (p,) in con.execute(
        "SELECT price FROM prints WHERE ticker=? AND ts>=?", (tk, t0 - 60))]
    if not prints:
        cls = "dead_band"
    else:
        gap = min(prints) - lvl
        if gap <= 0:
            cls = "timing"          # a print reached the level outside the rest span
        elif gap <= 2:
            cls = "near_miss_1_2c"
        elif cat.endswith("MAIN"):
            cls = "under_mains_book"
        else:
            cls = "too_deep_in_flat"
    classes[cls] += 1
    rows.append((tk[-14:], cat, lvl,
                 (min(prints) - lvl) if prints else None, cls))
P1 = ["# P1 — CAPTURE AUTOPSY (%s; %d posted-unfilled legs)"
      % (log.name, len(unfilled)), "",
      "classes: %s" % dict(classes.most_common()), ""]
for r in sorted(rows, key=lambda x: (x[4], x[3] if x[3] is not None else 99))[:40]:
    P1.append("- %s %s bid %s¢ · min-print-gap %s · %s" % r)
Path("/tmp/CAPTURE_AUTOPSY.md").write_text("\n".join(P1) + "\n")
print("P1 done:", dict(classes), flush=True)

# ================= P3 — THE EXIT HALF (per-band bounce surfaces) =========
# Frame: given a fill at anchor-d (the band's solved entry), bounce = the
# max traded print AFTER the first touch, before the right edge.
# P(bounce >= fill + b) for b=1..12, realism-gated (>=8 touches).
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

legs = []
bounce = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # band -> d -> [touch, bounced_by_b...]
raw = defaultdict(lambda: defaultdict(list))               # band -> d -> [bounce_cents]
for line in open(SPEC):
    r = json.loads(line)
    for leg, v in r["legs"].items():
        if not v.get("shape"):
            continue
        band = assign_band(r["cat"], v["anchor"], v["net"],
                           v["anchor"] - v["low"])
        if not band:
            continue
        ticks = [(ts, lc) for ts, b, a, lc in (v.get("ticks") or []) if lc]
        legs.append((r, leg, v, band, ticks))
        for d in (1, 3, 5, 8, 12, 16, 20, 25):
            lvl = v["anchor"] - d
            if lvl < 3:
                continue
            hit = None
            for i, (ts, lc) in enumerate(ticks):
                if lc <= lvl:
                    hit = i
                    break
            if hit is None:
                continue
            after = [lc for ts, lc in ticks[hit:]]
            raw[band][d].append(max(after) - lvl if after else 0)
EX = {"frame": "bounce = max traded print after first touch of anchor-d, "
      "before the right edge; realism >=8 touches", "bands": {}}
for band, dd in raw.items():
    EX["bands"][band] = {}
    for d, v in dd.items():
        if len(v) < 8:
            continue
        v2 = sorted(v)
        EX["bands"][band][str(d)] = {
            "n": len(v), "bounce_p50": v2[len(v2)//2],
            "p_ge": {str(b): round(sum(1 for x in v if x >= b) / len(v), 3)
                     for b in (1, 2, 3, 5, 8, 12)}}
(ROOT / "state/exit_bands_v1.json").write_text(json.dumps(EX))
print("P3 done: bands with exit surfaces:", len(EX["bands"]), flush=True)

# ================= P4 — LOOP 3, THE BLENDED OBJECT =======================
# Own-frame two-phase entry (loop2 frame) + P3 exit: sell at fill+b if the
# bounce reaches it, else mark at close. Drill (d, b) per band on TRAIN,
# judged HOLDOUT; verdicts HOLDOUT-PASS / CONVERGED-NEGATIVE.
def pbucket(anchor, net, dip):
    ab = ("a25" if anchor <= 25 else "a50" if anchor <= 50 else
          "a75" if anchor <= 75 else "a95")
    nb = ("dn10" if net <= -10 else "dn3" if net <= -3 else
          "flat" if net < 3 else "up3" if net < 10 else "up10")
    db = "d0" if dip <= 2 else "d3" if dip <= 9 else "d10"
    return ab + "|" + nb + "|" + db

def call_band(cat, anchor, net_h, dip_h):
    cell = (RECOG.get("%s|h6" % cat) or {}).get(pbucket(anchor, net_h, dip_h))
    if cell and cell.get("purity", 0) >= 0.5:
        return cell["top"]
    return default_band(cat, anchor)

R = []
for (r, leg, v, band, ticks) in legs:
    t8 = r["sched"] - 8 * 3600
    cut = t8 + 2 * 3600
    p1 = [(ts, lc) for ts, lc in ticks if ts <= cut]
    net_h = (p1[-1][1] - p1[0][1]) if p1 else 0
    dip_h = (v["anchor"] - min(x[1] for x in p1)) if p1 else 0
    day = r["event"].split("-")[1][:7]
    R.append({"cat": r["cat"], "anchor": v["anchor"], "close": v["close"],
              "ticks": ticks, "cut": cut, "net_h": net_h, "dip_h": dip_h,
              "day": day, "hold": day >= "26JUL14" and day.startswith("26JUL")})

def trade(x, band, d, b):
    lvl = x["anchor"] - d
    if lvl < 5:
        return None
    hit = None
    tick = x["ticks"]
    for i, (ts, lc) in enumerate(tick):
        if lc <= lvl:
            hit = i
            break
    if hit is None:
        return 0.0, 0     # bid, no fill
    after = [lc for ts, lc in tick[hit:]]
    exit_px = lvl + b if (after and max(after) >= lvl + b) else x["close"]
    return (exit_px - lvl) / lvl, 1

def replay(params, cohort):
    tot = n_bid = n_fill = 0
    per = defaultdict(lambda: [0, 0, 0.0])
    for x in cohort:
        b1 = default_band(x["cat"], x["anchor"])
        band = call_band(x["cat"], x["anchor"], x["net_h"], x["dip_h"]) or b1
        if not band or band not in params:
            continue
        d, b = params[band]
        out = trade(x, band, d, b)
        if out is None:
            continue
        ret, f = out
        n_bid += 1
        n_fill += f
        tot += ret
        per[band][0] += 1
        per[band][1] += f
        per[band][2] += ret
    return tot / max(n_bid, 1), n_bid, n_fill, per

train = [x for x in R if not x["hold"]]
hold = [x for x in R if x["hold"]]
params = {}
for band, row in TAB.items():
    if row.get("thin") or row.get("depth") is None:
        continue
    if row["kind"] == "faller" and (row.get("roc") or 0) <= 0:
        continue
    params[band] = (row["depth"], 3)
L = ["# P4 — LOOP 3, THE BLENDED OBJECT (entry+exit one trade; holdout "
     "law absolute)", ""]
prev = None
for it in range(1, 11):
    tr = replay(params, train)
    ho = replay(params, hold)
    L.append("- iter %d: TRAIN %.4f (bids %d fills %d) · HOLDOUT %.4f "
             "(bids %d fills %d) · gap %+.4f"
             % (it, tr[0], tr[1], tr[2], ho[0], ho[1], ho[2],
                tr[0] - ho[0]))
    acc = []
    base = tr[0]
    for band in sorted(params):
        d0, b0 = params[band]
        best = (d0, b0, base)
        for dd in (-2, -1, 0, 1, 2):
            for db in (-2, -1, 0, 1, 2):
                nd, nb2 = d0 + dd, b0 + db
                if nd < 1 or nd > 30 or nb2 < 1 or nb2 > 12 or \
                        (dd == 0 and db == 0):
                    continue
                cand = dict(params)
                cand[band] = (nd, nb2)
                s = replay(cand, train)[0]
                if s > best[2]:
                    best = (nd, nb2, s)
        if (best[0], best[1]) != (d0, b0):
            acc.append((band, d0, b0, best[0], best[1]))
            params[band] = (best[0], best[1])
            base = best[2]
    if acc:
        L.append("    adjusted: " + " · ".join(
            "%s d%d,b%d→d%d,b%d" % a for a in acc[:6]))
    else:
        L.append("- STOP: CONVERGED.")
        break
    prev = tr[0]
final = replay(params, hold)
L.append("")
L.append("## VERDICTS (holdout; PASS = ROC>0 and n>=10)")
verdicts = {}
for band, (nb, nf, sret) in sorted(final[3].items()):
    roc = sret / max(nb, 1)
    v = ("HOLDOUT-PASS" if roc > 0 and nb >= 10 else
         "THIN" if nb < 10 else "CONVERGED-NEGATIVE")
    verdicts[band] = {"params": params.get(band), "n": nb, "fills": nf,
                      "roc": round(roc, 4), "verdict": v}
    L.append("- %s: (d,b)=%s · holdout %d/%d · ROC %.4f · **%s**"
             % (band, params.get(band), nf, nb, roc, v))
(ROOT / "state/blend_tables_v1.json").write_text(json.dumps(
    {"params": {k: list(v) for k, v in params.items()},
     "verdicts": verdicts}))
Path("/tmp/LOOP3_CAMPAIGN.md").write_text("\n".join(L) + "\n")
print("P4 done. PASS:", [b for b, v in verdicts.items()
                         if v["verdict"] == "HOLDOUT-PASS"], flush=True)
print("FULLTRADE-DONE")
