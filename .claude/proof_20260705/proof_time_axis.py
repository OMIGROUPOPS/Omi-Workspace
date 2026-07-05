#!/usr/bin/env python3
"""[READ-ONLY] TIME-AXIS OUTCOME PROOF (C46 two-lane) — replay the 147-game box under
time-aware aims (aim_table_t.json) vs the flat table, against the real tape.
Writes /tmp/proof_time_rows.json + prints the two-lane summary.

Conventions:
- tts_at_post on the CARD clock (matches both the surfaces' build clock and runtime today).
- Per filled leg: flat level = the ACTUAL posted level (embodies the deployed flat aim);
  time-aware level = posted +/- (flat_depth - t_depth) for its (cat, price-bucket, tts-bucket).
- DEEPER (t_depth > flat): retained iff REST prints <= t_level while resting (post->latch);
  retained -> better basis (t-flat)c x qty; lost -> -(leg pnl) (pair-break flagged).
- SHALLOWER (t_depth < flat): the actual fill proves the tape reached the deeper flat level,
  so the shallower bid fills too, at the WORSE level: -(flat-t)c x qty. BLIND SPOT (stated):
  extra fills a shallower bid would win on legs that never filled are NOT counted (not in
  the population) -- this biases AGAINST shallower aims; the verdict must weigh it.
"""
import json, re, time, base64
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

ROOT = Path("/root/Omi-Workspace/arb-executor")
ET = timezone(timedelta(hours=-4))
dump = json.load(open("/tmp/ftr_dump.json"))
games = dump["games"]
TT = json.load(open(ROOT / "docs/policy/aim_table_t.json"))["aim_t"]
FLAT = json.load(open(ROOT / "docs/policy/aim_table.json"))["aim"]

def bucket_of(p):
    for lo, hi, nm in ((1,20,"01-20"),(21,40,"21-40"),(41,49,"41-49"),(50,59,"50-59"),(60,79,"60-79"),(80,99,"80-99")):
        if lo <= p <= hi: return nm
    return None
def tb_of(tts_min):
    if tts_min > 360: return "T8"
    if tts_min > 240: return "T6"
    if tts_min > 120: return "T4"
    if tts_min > 60: return "T2"
    if tts_min > 30: return "T1"
    return "T30"

# REST tape (same client as proof_pass)
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests
pk = serialization.load_pem_private_key((ROOT/"kalshi.pem").read_bytes(), password=None, backend=default_backend())
B = "https://api.elections.kalshi.com/trade-api/v2"
KEY = "f3b064d1-a02e-42a4-b2b1-132834694d23"
def sgn(m, p):
    ts = str(int(time.time()*1000)); sp = "/trade-api/v2"+p.split("?")[0]
    sig = pk.sign((ts+m+sp).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": KEY, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(), "KALSHI-ACCESS-TIMESTAMP": ts}
_tc = {}
def trades_of(tk):
    if tk in _tc: return _tc[tk]
    out, cur = [], ""
    for _ in range(20):
        p = "/markets/trades?ticker=%s&limit=1000%s" % (tk, "&cursor="+cur if cur else "")
        try: r = requests.get(B+p, headers=sgn("GET", p), timeout=30).json()
        except Exception: break
        for t in r.get("trades", []):
            try:
                ts = datetime.fromisoformat(t["created_time"].replace("Z","+00:00")).timestamp()
                px = t.get("yes_price")
                if px is None: px = round(float(t["yes_price_dollars"])*100)
                out.append((ts, int(px)))
            except Exception: pass
        cur = r.get("cursor","")
        if not cur: break
    _tc[tk] = sorted(out); return _tc[tk]

rows = []
agg = Counter(); dsum = defaultdict(float)
deltas = []
for g in games:
    cat = g["cat"]; st = g.get("sched_start")
    for l in (g.get("legs") or []):
        if not l.get("fill") or not st: continue
        post_ts = l.get("posted_first_ts") or l.get("fill_ts")
        posted = l.get("posted_first_px") or l.get("fill")
        side = l.get("side"); qty = l.get("qty") or 5
        tts_min = (st - post_ts) / 60.0
        tb = tb_of(tts_min); pb = bucket_of(int(posted))
        if not pb or cat not in TT:
            continue
        trow = (TT.get(cat, {}).get(pb, {}) or {}).get(tb)
        frow = (FLAT.get(cat, {}) or {}).get(pb, {})
        if not trow: continue
        if side == "faller":
            flat_d = int(frow.get("faller_depth", 3)); t_d = trow["faller_depth"]
        elif side == "riser":
            flat_d = int(frow.get("riser_post", 0)); t_d = trow["riser_post"]
        else:
            continue
        dd = t_d - flat_d
        agg["legs"] += 1; agg["tb_"+tb] += 1
        if dd == 0:
            agg["no_change"] += 1; continue
        t_level = max(1, int(posted) - dd)
        if dd > 0:   # deeper
            end_ts = g.get("latch_ts") or 9e12
            hit = any(post_ts <= ts <= end_ts and px <= t_level for ts, px in trades_of(l["tk"]))
            if hit:
                agg["deeper_retained"] += 1; d = dd * qty / 100.0
                dsum["lane2"] += d; deltas.append(-dd)   # better (lower) basis
            else:
                agg["deeper_lost"] += 1
                dsum["lane2"] += -(l.get("pnl") or 0.0); deltas.append(0)
        else:        # shallower: fills at the worse level (blind spot stated)
            agg["shallower_worse"] += 1
            dsum["lane2"] += dd * qty / 100.0            # dd negative -> negative dollars
            deltas.append(-dd)                            # positive = basis WORSE by that many cents
        rows.append({"ev": g["ev"], "tk": l["tk"], "cat": cat, "side": side, "tb": tb,
                     "posted": posted, "flat_d": flat_d, "t_d": t_d, "dd": dd})

json.dump({"rows": rows, "agg": dict(agg), "lane2": round(dsum["lane2"], 2)},
          open("/tmp/proof_time_rows.json", "w"), indent=1)
n = agg["legs"]
print("legs graded:", n, "| tb mix:", {k[3:]: v for k, v in agg.items() if k.startswith('tb_')})
print("no_change:", agg["no_change"], "| deeper retained/lost:", agg["deeper_retained"], "/", agg["deeper_lost"],
      "| shallower(worse basis, blind-spot biased):", agg["shallower_worse"])
ch = [d for d in deltas if d != 0]
print("LANE 1: legs changed:", len(ch), "| mean basis shift (c, + = worse):",
      round(sum(ch)/len(ch), 2) if ch else 0)
print("LANE 2: $ %.2f (n=%d changed legs -- LUCK-POLLUTED if settlements < 30)" % (dsum["lane2"], len(ch)))
