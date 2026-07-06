#!/usr/bin/env python3
"""w1_grading.py — WINDOW-1 GRADING (operator criteria upgrade, 2026-07-06; Vault §0A).
THE GOAL = filled AND cashed in Window 1 (the pregame opportunity window, HONEST clock).

Per leg:  W1_CASHED    exit band touched AND exit FILLED pregame (exit fill ts < honest start)
          W1_REACHABLE band touched pregame (tape printed >= exit level), exit not filled
          W2_ONLY      band only reachable in-match (or never)
Pair:     BOUHAR-class = BOTH legs W1_CASHED -> its own headline rate.
Grades:   A requires the W1 shape — both legs filled in W1 at combined <=97 AND both exits
          REACHED in W1 (cashed or touched); an entry that structurally can't reach its band
          before the gun (too late, too high) caps at B regardless of price.
Nightly:  the W1-cash rate per category is the PRIMARY scoreboard line — the money-machine metric.

Run on the VPS from arb-executor root AFTER full_tape_regrade.py (reads /tmp/ftr_dump.json,
state/schedule.json for the honest clock, Kalshi REST for pregame band-touch checks).
Writes /tmp/w1_grades.json + prints the per-category W1 scoreboard.
Prior art (C45): FULL_TAPE_REGRADE machinery; E15 (two capture windows); Vault 0A THREE WINDOWS
doctrine; BOUHAR-class survival (4H addendum #5). DELTA: W1 as tracked outcome + grade gate.
"""
import json, re, time, base64
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

ROOT = Path("/root/Omi-Workspace/arb-executor")
GOAL = 97
dump = json.load(open("/tmp/ftr_dump.json"))
sch = json.load(open(ROOT / "state" / "schedule.json"))["schedule"]

def honest_start(ev):
    m = re.search(r"\d{2}[A-Z]{3}\d{2}([A-Z]{6})$", ev)
    if not m: return None
    pc = m.group(1)
    for k in (pc, pc[3:] + pc[:3]):
        e = sch.get(k)
        if e and not e.get("espn_midnight"):
            try: return datetime.fromisoformat(e["start_time"].replace("Z", "+00:00")).timestamp()
            except Exception: pass
    return None

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests
pk = serialization.load_pem_private_key((ROOT / "kalshi.pem").read_bytes(), password=None, backend=default_backend())
B = "https://api.elections.kalshi.com/trade-api/v2"
KEY = "f3b064d1-a02e-42a4-b2b1-132834694d23"
def sgn(m, p):
    ts = str(int(time.time() * 1000)); sp = "/trade-api/v2" + p.split("?")[0]
    sig = pk.sign((ts + m + sp).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": KEY, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
            "KALSHI-ACCESS-TIMESTAMP": ts}
_tc = {}
def tape(tk):
    if tk in _tc: return _tc[tk]
    out, cur = [], ""
    for _ in range(20):
        p = "/markets/trades?ticker=%s&limit=1000%s" % (tk, "&cursor=" + cur if cur else "")
        try: r = requests.get(B + p, headers=sgn("GET", p), timeout=30).json()
        except Exception: break
        for t in r.get("trades", []):
            try:
                ts = datetime.fromisoformat(t["created_time"].replace("Z", "+00:00")).timestamp()
                px = t.get("yes_price")
                if px is None: px = round(float(t["yes_price_dollars"]) * 100)
                out.append((ts, int(px)))
            except Exception: pass
        cur = r.get("cursor", "")
        if not cur: break
    _tc[tk] = sorted(out); return _tc[tk]

rows = []; cat_stats = defaultdict(Counter)
for g in dump["games"]:
    ev, cat = g["ev"], g["cat"]
    hs = honest_start(ev)
    legs = g.get("legs") or []
    leg_out = []
    for l in legs:
        tk = l["tk"]; lab = "W2_ONLY"
        exit_px = None
        # exit level from the regrade's exitp capture if present in leg record
        exit_px = (l.get("exit_price") or (l.get("best_full") or {}).get("exit_price"))
        if exit_px is None and l.get("fill") is not None and l.get("band_x") is not None:
            exit_px = l["fill"] + l["band_x"]
        if hs and l.get("fill") and l.get("fill_ts") and l["fill_ts"] < hs:
            # leg filled in W1; did the band get touched pregame?
            oc = l.get("outc", ""); oc_ts = l.get("outc_ts")
            if oc == "exit_FILLED" and oc_ts and oc_ts < hs:
                lab = "W1_CASHED"
            elif exit_px is not None and any(t < hs and px >= exit_px for t, px in tape(tk)):
                lab = "W1_REACHABLE"
        leg_out.append({"tk": tk, "w1": lab})
        cat_stats[cat][lab] += 1
    both_cashed = len(legs) == 2 and all(x["w1"] == "W1_CASHED" for x in leg_out)
    both_w1fill = (len(legs) == 2 and hs and all(l.get("fill_ts") and l["fill_ts"] < hs for l in legs))
    comb = g.get("combined")
    w1_shape = (both_w1fill and comb is not None and comb <= GOAL
                and all(x["w1"] in ("W1_CASHED", "W1_REACHABLE") for x in leg_out))
    grade = g.get("grade")
    w1_grade = grade
    if grade == "A" and not w1_shape:
        w1_grade = "B"   # A requires the W1 shape; price alone no longer earns A
    # [B-SUBGRADES — operator ruling 2026-07-06, permanent §0E extension]
    #   B1 = W1-filled pair, cashed in W1/CORRIDOR (missed A only on W1-cash) — near-gold
    #   B2 = cashed but only in W2 (the knife window)
    #   B3 = completed pair with a leg that RODE to settlement (the structural-bleed wing)
    # corridor end = event gun_ts else latch_ts (tape supremacy; both in the dump).
    if w1_grade == "B" and len(legs) == 2:
        cor_end = g.get("gun_ts") or g.get("latch_ts")
        rode = any((l.get("outc") or "").startswith("settle") for l in legs)
        if rode:
            w1_grade = "B3"
        else:
            both_w1_filled = bool(hs and all(l.get("fill_ts") and l["fill_ts"] < hs for l in legs))
            exits_ts = [l.get("outc_ts") for l in legs if (l.get("outc") or "") == "exit_FILLED"]
            # pre-W2 = before the corridor end (tape onset else latch); no boundary -> B2, conservative
            all_pre_w2 = bool(exits_ts) and bool(cor_end) and all(
                t is not None and t < cor_end for t in exits_ts)
            w1_grade = "B1" if (both_w1_filled and all_pre_w2) else "B2"
    cat_stats[cat]["pairs"] += 1 if len(legs) == 2 else 0
    if both_cashed: cat_stats[cat]["BOUHAR"] += 1
    rows.append({"ev": ev, "cat": cat, "honest_join": hs is not None, "legs": leg_out,
                 "bouhar": both_cashed, "w1_shape": w1_shape,
                 "grade_old": grade, "grade_w1": w1_grade})

json.dump({"generated": time.time(), "rows": rows}, open("/tmp/w1_grades.json", "w"), indent=1)
print("=== W1 SCOREBOARD (primary line: W1-cash rate per category) ===")
for cat, s in sorted(cat_stats.items()):
    legs_n = s["W1_CASHED"] + s["W1_REACHABLE"] + s["W2_ONLY"]
    print("%-10s legs=%3d  W1_CASHED=%3d (%.0f%%)  W1_REACHABLE=%3d  W2_ONLY=%3d  BOUHAR-pairs=%d/%d" % (
        cat, legs_n, s["W1_CASHED"], 100 * s["W1_CASHED"] / max(1, legs_n),
        s["W1_REACHABLE"], s["W2_ONLY"], s["BOUHAR"], s["pairs"]))
regr = sum(1 for r in rows if r["grade_old"] == "A" and r["grade_w1"] == "B")
print("A->B regrades under the W1 gate:", regr)
