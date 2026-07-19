#!/usr/bin/env python3
"""P4 (AMENDED) — LOOP 4: ENTRIES ALONE, ended by the CURRENT DEPLOYED
EXIT CONFIG (the June-sealed bands exactly as they run live).

Frame: own-frame two-phase entry (conception park at anchor-default band's
level; T−6h recognition re-call). On every replayed fill: post the
deployed band exit = fill + band_exit_X (the June parquet, ITF borrows
CHALL — the live ITF_EXIT_BORROW law); BANK it if any later print >= the
target; else RIDE TO SETTLEMENT (winner join from historical_events:
settle 100 if the leg code is the winner, 0 if the loser; legs without a
settlement record are EXCLUDED and counted — never guessed). HOLD-rule
cells ride to settlement by design.
Drill adjusts ENTRY DEPTHS ONLY (the exit is the machine as it is);
capture-fix constraint from P1 folded in: flat-band depths are capped at
the band's dip_p90 (the too-deep-in-flat class's ceiling). Holdout law +
gap meter unchanged. Verdicts per band: HOLDOUT-PASS / CONVERGED-NEGATIVE
/ THIN. Outputs: /tmp/LOOP4_CAMPAIGN.md + state/entry_only_tables_v1.json.
"""
import json, glob
from collections import defaultdict
from pathlib import Path
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
BMAP = json.loads((ROOT / "state/band_map_v1.json").read_text())
TAB = json.loads((ROOT / "state/entry_tables_v1.json").read_text())["tables"]
DIVOT = json.loads((ROOT / "state/divot_tables_v1.json").read_text())
DRIFT = json.loads((ROOT / "state/drift_surfaces_v1.json").read_text())
RECOG = DRIFT.get("recognition", {})
SPEC = ROOT / "state/range_spectrum_v1.jsonl"

# deployed exit surface (June-sealed), cell-expanded; ITF borrows CHALL
EXIT = {}
for f in glob.glob(str(ROOT / "data/durable/exit_surface_gated_optima/"
                        "*_adaptive_exit_bands.parquet")):
    cat = Path(f).name.split("_adaptive")[0].upper()
    m = {}
    for row in pq.read_table(f).to_pylist():
        x = row["band_exit_X"]
        val = None if str(x).upper() == "HOLD" else int(x)
        for c in range(int(row["price_low"]), int(row["price_high"]) + 1):
            m[c] = val
    EXIT[cat] = m
EXIT["ITF_M"] = EXIT["ATP_CHALL"]
EXIT["ITF_W"] = EXIT["WTA_CHALL"]

# [v2 fix, named] historical_events ENDS Apr-10; the spectrum begins
# Apr-21 — zero overlap (the first join returned 0 and said so). The
# settlement record for the spectrum era = Kalshi's own market result
# field, swept to state/settlements_hist.json (cache-resumable).
SETTLE = json.loads((ROOT / "state/settlements_hist.json").read_text())

def default_band(cat, anchor):
    c = BMAP["cats"].get(cat)
    if not c or c.get("thin"):
        return None
    flats = [b for b in c["bands"] if b["direction"] == "flat"] or c["bands"]
    return min(flats, key=lambda b: abs(b["anchor_med"] - anchor))["band"]

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
n_nosettle = 0
for line in open(SPEC):
    r = json.loads(line)
    win = SETTLE.get(r["event"]) or None
    if win and not any(isinstance(x, int) for x in win.values()):
        win = None
    t8 = r["sched"] - 8 * 3600
    cut = t8 + 2 * 3600
    day = r["event"].split("-")[1][:7]
    for leg, v in r["legs"].items():
        if not v.get("shape"):
            continue
        if not win:
            n_nosettle += 1
            continue
        settle = win.get(leg)
        if settle is None:
            n_nosettle += 1
            continue
        ticks = [(ts, lc) for ts, b, a, lc in (v.get("ticks") or []) if lc]
        p1 = [(ts, lc) for ts, lc in ticks if ts <= cut]
        R.append({"cat": r["cat"], "anchor": v["anchor"], "settle": settle,
                  "ticks": ticks,
                  "net_h": (p1[-1][1] - p1[0][1]) if p1 else 0,
                  "dip_h": (v["anchor"] - min(x[1] for x in p1)) if p1 else 0,
                  "hold": day >= "26JUL14" and day.startswith("26JUL")})
print("legs w/ settlement:", len(R), "| excluded no-settle:", n_nosettle,
      flush=True)

CAP = {}   # P1 fold-in: flat depths capped at the band's own dip_p90
for band, row in TAB.items():
    dv = (DIVOT.get("bands") or {}).get(band) or {}
    if row.get("kind") == "flat" and dv.get("depth_p90"):
        CAP[band] = int(dv["depth_p90"])

def trade(x, band, d):
    lvl = x["anchor"] - d
    if lvl < 5:
        return None
    hit = None
    for i, (ts, lc) in enumerate(x["ticks"]):
        if lc <= lvl:
            hit = i
            break
    if hit is None:
        return 0.0, 0
    bx = EXIT.get(x["cat"], {}).get(lvl)
    after = [lc for ts, lc in x["ticks"][hit:]]
    if bx is not None and after and max(after) >= lvl + bx:
        exit_px = lvl + bx          # the deployed band exit BANKS
    else:
        exit_px = x["settle"]       # HOLD rule or unfilled exit: settlement
    return (exit_px - lvl) / lvl, 1

def replay(depths, cohort):
    tot = n_bid = n_fill = 0
    per = defaultdict(lambda: [0, 0, 0.0])
    for x in cohort:
        band = call_band(x["cat"], x["anchor"], x["net_h"], x["dip_h"])
        if not band or band not in depths:
            continue
        out = trade(x, band, depths[band])
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
depths = {}
for b, r in TAB.items():
    if r.get("thin") or r.get("depth") is None:
        continue
    if r["kind"] == "faller" and (r.get("roc") or 0) <= 0:
        continue
    d = r["depth"]
    if b in CAP:
        d = min(d, CAP[b])
    depths[b] = d
L = ["# P4 AMENDED — LOOP 4: ENTRIES ALONE under the DEPLOYED exit "
     "(June bands verbatim; bank-or-settle; no new exit anything)", "",
     "legs w/ settlement %d · excluded-no-settle %d (counted, never "
     "guessed) · P1 fold-in: flat depths capped at own dip_p90" %
     (len(R), n_nosettle), ""]
for it in range(1, 11):
    tr = replay(depths, train)
    ho = replay(depths, hold)
    L.append("- iter %d: TRAIN %.4f (bids %d fills %d) · HOLDOUT %.4f "
             "(bids %d fills %d) · gap %+.4f"
             % (it, tr[0], tr[1], tr[2], ho[0], ho[1], ho[2],
                tr[0] - ho[0]))
    acc = []
    base = tr[0]
    for band in sorted(depths):
        best_d, best_s = depths[band], base
        for step in (-3, -2, -1, 1, 2, 3):
            nd = depths[band] + step
            if nd < 1 or nd > 30 or (band in CAP and nd > CAP[band]):
                continue
            cand = dict(depths)
            cand[band] = nd
            s = replay(cand, train)[0]
            if s > best_s:
                best_s, best_d = s, nd
        if best_d != depths[band]:
            acc.append((band, depths[band], best_d))
            depths[band] = best_d
            base = best_s
    if acc:
        L.append("    adjusted: " + " · ".join("%s %d→%d" % a
                                               for a in acc[:8]))
    else:
        L.append("- STOP: CONVERGED.")
        break
final = replay(depths, hold)
L.append("")
L.append("## VERDICTS (holdout; settle-ended; PASS = ROC>0, n>=10)")
verd = {}
for band, (nb, nf, sret) in sorted(final[3].items()):
    roc = sret / max(nb, 1)
    v = ("HOLDOUT-PASS" if roc > 0 and nb >= 10 else
         "THIN" if nb < 10 else "CONVERGED-NEGATIVE")
    verd[band] = {"depth": depths.get(band), "n": nb, "fills": nf,
                  "roc": round(roc, 4), "verdict": v}
    L.append("- %s: depth %s · holdout %d/%d · ROC %.4f · **%s**"
             % (band, depths.get(band), nf, nb, roc, v))
(ROOT / "state/entry_only_tables_v1.json").write_text(json.dumps(
    {"depths": depths, "verdicts": verd,
     "frame": "entries alone; deployed June exits verbatim; "
              "bank-or-settle; P1 caps folded"}))
Path("/tmp/LOOP4_CAMPAIGN.md").write_text("\n".join(L) + "\n")
print("LOOP4-DONE PASS:", [b for b, v in verd.items()
                           if v["verdict"] == "HOLDOUT-PASS"])
