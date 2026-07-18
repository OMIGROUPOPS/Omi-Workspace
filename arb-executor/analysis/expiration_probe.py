#!/usr/bin/env python3
"""P0 (6) — AT-EVENT-START EXPIRATION TEST (operator-authorized single tiny
probe order).

Stage 1 (field discovery, receipts): POST create-order-v2 with
time_in_force="good_till_event_start" — a 400 enumerating the valid enum IS
the receipt. Stage 2: GTC + expiration_ts = the match's honest sched → if
accepted, the probe order (1 share, 2c, far from touch) rests with an
exchange-side clock; the checker records the exact cancel second against
all three clocks (sched / our bell / milestone stamp).

Usage: python3 analysis/expiration_probe.py [--ticker TK --sched EPOCH]
Writes /tmp/EXPIRATION_PROBE.md as it goes. Cleanup: cancels the probe
order if still resting at the end of the check window.
"""
import json, sys, time, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import live_v4 as L

OUT = Path("/tmp/EXPIRATION_PROBE.md")
BASE = "https://api.elections.kalshi.com"
ak, pk = L.load_credentials()

def call(method, path, payload=None):
    hdr = L.auth_headers(ak, pk, method, path)
    req = urllib.request.Request(BASE + path, method=method,
                                 headers=hdr,
                                 data=(json.dumps(payload).encode()
                                       if payload is not None else None))
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()[:400]
        except Exception:
            body = "?"
        return e.code, body
    except Exception as e:
        return -1, str(e)[:200]

lines = ["# AT-EVENT-START EXPIRATION PROBE — receipts", ""]
tk = sched = None
for i, a in enumerate(sys.argv):
    if a == "--ticker":
        tk = sys.argv[i + 1]
    if a == "--sched":
        sched = float(sys.argv[i + 1])
if not tk:
    print("need --ticker and --sched")
    sys.exit(1)

def order_payload(tif, extra=None):
    p = L.build_order_payload_v2(tk, "buy", 2, 1, True,
                                 "probe-expiry-%d" % int(time.time()))
    p["time_in_force"] = tif
    if extra:
        p.update(extra)
    return p

# Stage 1: enum discovery
st, body = call("POST", L.ORDER_CREATE_V2_PATH,
                order_payload("good_till_event_start"))
lines.append("## Stage 1 — time_in_force enum discovery")
lines.append("- sent time_in_force=good_till_event_start → HTTP %s" % st)
lines.append("- body: `%s`" % str(body)[:350])
oid1 = None
if st == 200 or st == 201:
    oid1 = (body if isinstance(body, dict) else {}).get("order_id") or \
           (body if isinstance(body, dict) else {}).get("id")
    lines.append("- UNEXPECTED ACCEPT — order %s placed; will cancel in cleanup" % oid1)

# Stage 2: GTC + expiration_ts = sched
st2, body2 = call("POST", L.ORDER_CREATE_V2_PATH,
                  order_payload("good_till_canceled",
                                {"expiration_ts": int(sched)}))
lines.append("")
lines.append("## Stage 2 — GTC + expiration_ts = honest sched (%d)" % int(sched))
lines.append("- HTTP %s" % st2)
lines.append("- body: `%s`" % str(body2)[:350])
oid2 = None
if st2 in (200, 201) and isinstance(body2, dict):
    oid2 = body2.get("order_id") or body2.get("id")
    lines.append("- PROBE ORDER RESTING: %s (1sh @2c, expiration_ts=sched)" % oid2)
OUT.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print("OIDS", oid1, oid2)
