#!/usr/bin/env python3
"""latch_blind_forensic.py — what does a THIN match's tape do at the TRUE start?
Prior art (C45): CLOCK_AUDIT (gun certified ITF/CHALL but ~undetectable class on thin books;
honest anchor certified); T51 (volume-acceleration mandate); C-THIN-GUN shadow (the candidate
detector this forensic calibrates); scale-gun Part-3 principle (relative acceleration).
DELTA: per-event tape read AT the honest start for the gun-blind class — print cadence,
quote/print gaps, spread shift — to calibrate THIN_GUN_* and pre-register false-fire bars.

Population: honest-joined events in /tmp/ftr_dump.json (yesterday's box) + today's settled
honest-window slate whose events never latched (latch_ts None) — the gun-blind class.
For each: prints/min in [hs-120m,hs-60m], [hs-60m,hs], [hs,hs+15m], [hs+15,hs+45m];
first print after hs; max 60s-burst in [hs, hs+30m]. Honest clock = STUDY ANCHOR ONLY.
Writes /tmp/latch_blind.json + summary. Run from arb-executor root after the slate settles.
"""
import json, re, time, base64
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ROOT = Path("/root/Omi-Workspace/arb-executor")
sch = json.load(open(ROOT / "state" / "schedule.json"))["schedule"]
dump = json.load(open("/tmp/ftr_dump.json"))

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
def tape_ev(ev, legs):
    out = []
    for tk in legs:
        cur = ""
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
    return sorted(out)

rows = []
for g in dump["games"]:
    if g.get("latch_ts"):
        continue   # the gun fired -> not the blind class
    ev = g["ev"]; hs = honest_start(ev)
    if not hs: continue
    legs = [l["tk"] for l in (g.get("legs") or [])]
    if not legs: continue
    tp = tape_ev(ev, legs)
    def rate(a, b):
        n = sum(1 for t, _ in tp if a <= t < b)
        return round(n / max(1e-9, (b - a) / 60.0), 2)
    win = [t for t, _ in tp if hs <= t < hs + 1800]
    burst = 0
    for i, t0 in enumerate(win):
        burst = max(burst, sum(1 for t in win if t0 <= t < t0 + 60))
    first_after = next((t for t, _ in tp if t >= hs), None)
    rows.append({"ev": ev, "cat": g["cat"],
                 "pm2h": rate(hs - 7200, hs - 3600), "pm1h": rate(hs - 3600, hs),
                 "live15": rate(hs, hs + 900), "live45": rate(hs + 900, hs + 2700),
                 "max_burst60_in30m": burst,
                 "first_print_after_start_min": (round((first_after - hs) / 60.0, 1) if first_after else None)})

json.dump(rows, open("/tmp/latch_blind.json", "w"), indent=1)
bycat = defaultdict(list)
for r in rows: bycat[r["cat"]].append(r)
print("=== LATCH-BLIND FORENSIC (gun never fired; honest clock = study anchor only) ===")
for cat, v in sorted(bycat.items()):
    def med(k):
        x = sorted(r[k] for r in v if r[k] is not None)
        return x[len(x) // 2] if x else None
    print("%-10s n=%2d  prints/min: pre1h=%s -> live15=%s live45=%s | max60s-burst med=%s | first print T+%smin" % (
        cat, len(v), med("pm1h"), med("live15"), med("live45"), med("max_burst60_in30m"),
        med("first_print_after_start_min")))
print("thin-latch candidate check: would recent>=max(3, 3x baseline) fire at live15 rates while pre1h stays under it?")
