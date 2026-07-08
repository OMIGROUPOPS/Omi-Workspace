#!/usr/bin/env python3
"""PART3 clean-3day: Jul-8 (partial day, bot dead 02:52-11:30 ET) per-cat GROSS vs CLEAN.
READ-ONLY: GET-only API use, prints JSON to stdout, writes nothing.
Sources: /root/naked_sweep_20260708/fills_recent.json (exchange truth),
orders_resting.json (bands = resting sell px), premarket_ticks CSVs (divot classes,
post_fill_move.py convention), Kalshi trades API (own-low prints, w1_grading tape()),
state/schedule.json honest clock.
Mechanical = named naked-class legs + any leg all of whose buys landed in the dead window.
"""
import gzip, json, re, time, base64, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
ET = timezone(timedelta(hours=-4))
DEAD0 = datetime(2026, 7, 8, 2, 52, tzinfo=ET).timestamp()
DEAD1 = datetime(2026, 7, 8, 11, 30, tzinfo=ET).timestamp()
NAMED = {"MILMIS-MIS", "MILMIS-MIL", "VANSEL-VAN", "JONJEA-JON", "JONJEA-JEA",
         "LUENAT-LUE", "LUENAT-NAT", "TOMSHI-TOM", "DAMARN-ARN", "DAMARN-DAM",
         "PDARIB-RIB", "MAXABA-MAX", "ISHCRO-CRO"}
CATMAP = [("KXATPCHALLENGERMATCH", "ATP_CHALL"), ("KXWTACHALLENGERMATCH", "WTA_CHALL"),
          ("KXITFMMATCH", "ITF_M"), ("KXITFWMATCH", "ITF_W"),
          ("KXITFMATCH", "ITF_M"), ("KXITFWMATCH", "ITF_W"),
          ("KXATPMATCH", "ATP_MAIN"), ("KXWTAMATCH", "WTA_MAIN")]
def cat_of(tk):
    for p, c in CATMAP:
        if tk.startswith(p): return c
    return "OTHER"

fills = json.load(open("/root/naked_sweep_20260708/fills_recent.json"))
legs = defaultdict(list)
for f in fills:
    if f.get("action") != "buy": continue
    ts = datetime.fromisoformat(f["created_time"].replace("Z", "+00:00")).timestamp()
    if datetime.fromtimestamp(ts, ET).strftime("%m-%d") != "07-08": continue
    px = round(float(f["yes_price_dollars"]) * 100, 1)
    qty = float(f["count_fp"])
    legs[f["ticker"]].append((ts, px, qty))

# bands from resting sell orders (11:45 pull)
orders = json.load(open("/root/naked_sweep_20260708/orders_resting.json"))
ol = orders.get("orders", orders) if isinstance(orders, dict) else orders
bands = {}
for o in ol:
    try:
        if o.get("action") == "sell" and o.get("status") in ("resting", "partially_filled", None):
            px = o.get("yes_price")
            if px is None and o.get("yes_price_dollars"): px = round(float(o["yes_price_dollars"]) * 100)
            bands.setdefault(o["ticker"], px)
    except Exception: pass

sch = json.load(open(ROOT / "state" / "schedule.json"))["schedule"]
def honest_start(tk):
    m = re.search(r"\d{2}[A-Z]{3}\d{2}([A-Z]{4,6})-", tk)
    if not m: return None
    pc = m.group(1)
    for k in (pc, pc[3:] + pc[:3]):
        e = sch.get(k)
        if e and not e.get("espn_midnight"):
            try: return datetime.fromisoformat(e["start_time"].replace("Z", "+00:00")).timestamp()
            except Exception: pass
    return None

# Kalshi trades tape (GET only)
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
def tape(tk):
    out, cur = [], ""
    for _ in range(10):
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

# premarket_ticks window + post_fill_move classifier (verbatim convention)
_dc = {}
def pts(s):
    try:
        d, t, ap = s.split(" ")
        if d not in _dc:
            y, mo, dy = d.split("-")
            _dc[d] = datetime(int(y), int(mo), int(dy), tzinfo=ET).timestamp()
        hh, mm, ss = t.split(":")
        return _dc[d] + (int(hh) % 12 + (12 if ap == "PM" else 0)) * 3600 + int(mm) * 60 + int(ss)
    except Exception:
        return None
def ticks_window(tk, t0, t1):
    for suf in (".csv", ".csv.gz"):
        f = ROOT / "analysis" / "premarket_ticks" / (tk + suf)
        if f.exists():
            op = gzip.open if suf.endswith("gz") else open
            out = []
            with op(f, "rt", encoding="utf-8", errors="replace") as fh:
                next(fh, None)
                for ln in fh:
                    p = ln.split(",")
                    if len(p) < 13: continue
                    t = pts(p[0])
                    if t is None or t < t0 or t > t1: continue
                    try:
                        b = int(p[2]) if p[2] else None
                        a = int(p[12]) if p[12] else None
                    except ValueError: continue
                    out.append((t, b, a))
            return out
    return None
def classify(tk, vw, fts):
    tks = ticks_window(tk, fts - 600, fts + 3900)
    if not tks or sum(1 for t, b, a in tks if t > fts) < 5:
        return "NO_TAPE", None
    pre_ask = [a for t, b, a in tks if t <= fts and a]
    ask_ref = pre_ask[-1] if pre_ask else None
    post = [(t, b, a) for t, b, a in tks if t > fts]
    und_t = next((t for t, b, a in post if b is not None and b < vw), None)
    p30 = [(t, b, a) for t, b, a in post if t <= fts + 1800]
    min_ask30 = min((a for t, b, a in p30 if a), default=None)
    mid30 = None
    for t, b, a in p30[::-1]:
        if b and a:
            mid30 = (b + a) / 2.0
            break
    und_min = round((und_t - fts) / 60, 1) if und_t else None
    if und_t is None: return "NO_UNDERCUT", und_min
    recovered = any(b is not None and b >= vw for t, b, a in post if und_t < t <= und_t + 1800)
    divot = (min_ask30 is not None and ask_ref is not None and min_ask30 >= ask_ref - 2 and recovered)
    reprice = (min_ask30 is not None and ask_ref is not None and min_ask30 <= ask_ref - 3
               and mid30 is not None and mid30 < vw)
    return ("DIVOT" if divot else ("REPRICE" if reprice else "AMBIG")), und_min

out_legs = []
now = time.time()
for i, (tk, fl) in enumerate(sorted(legs.items())):
    q = sum(x[2] for x in fl)
    vw = sum(x[1] * x[2] for x in fl) / q
    t0 = min(x[0] for x in fl)
    dead = [x for x in fl if DEAD0 <= x[0] <= DEAD1]
    suffix = tk.split("MATCH-")[1][7:] if "MATCH-" in tk else tk
    named = suffix in NAMED
    hs = honest_start(tk)
    w1 = bool(hs and t0 <= hs)
    tp = tape(tk)
    win0 = t0 - 86400
    win1 = min(hs, now) if hs else now
    pre = [px for ts, px in tp if win0 <= ts <= win1]
    own_low = min(pre) if pre else None
    band = bands.get(tk)
    band_reach = None
    if band is not None:
        band_reach = any(ts > t0 and px >= band for ts, px in tp)
    cls, und = classify(tk, vw, t0)
    out_legs.append(dict(tk=tk, cat=cat_of(tk), vw=round(vw, 1), qty=q,
                         first_fill_et=datetime.fromtimestamp(t0, ET).strftime("%H:%M"),
                         dead_window=bool(dead), n_dead=len(dead), n_fills=len(fl),
                         named=named, mech=named or bool(dead),
                         hs=bool(hs), w1=w1, own_low=own_low,
                         gap=(round(vw - own_low, 1) if own_low is not None else None),
                         band=band, band_reach=band_reach, cls=cls, undercut_min=und))
    print("... %d/%d" % (i + 1, len(legs)), file=sys.stderr, flush=True)

def med(xs):
    xs = sorted(xs); n = len(xs)
    return None if not n else (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0)

agg = {}
for cat in sorted(set(l["cat"] for l in out_legs)):
    sub = [l for l in out_legs if l["cat"] == cat]
    def block(ls):
        gl = [l["gap"] for l in ls if l["gap"] is not None and l["w1"]]
        dec = [l for l in ls if l["w1"] and l["cls"] in ("DIVOT", "REPRICE", "NO_UNDERCUT")]
        nb = [l for l in ls if l["band"] is not None]
        return {"n_legs": len(ls), "n_w1": sum(1 for l in ls if l["w1"]),
                "n_gap": len(gl), "gap_med": med(gl),
                "decisive": len(dec), "divot": sum(1 for l in dec if l["cls"] == "DIVOT"),
                "reprice": sum(1 for l in dec if l["cls"] == "REPRICE"),
                "no_undercut": sum(1 for l in dec if l["cls"] == "NO_UNDERCUT"),
                "no_tape": sum(1 for l in ls if l["cls"] == "NO_TAPE"),
                "n_band": len(nb), "reach": sum(1 for l in nb if l["band_reach"])}
    agg[cat] = {"gross": block(sub), "clean": block([l for l in sub if not l["mech"]]),
                "mech": [(l["tk"][-20:], "named" if l["named"] else "dead_window") for l in sub if l["mech"]]}
print(json.dumps({"legs": out_legs, "agg": agg}))
