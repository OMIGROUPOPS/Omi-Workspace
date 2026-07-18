#!/usr/bin/env python3
"""P0 (6) checker: watch the probe order through its expiration_ts second.
Sleeps to sched-120s, then polls every 5s; records the exact transition
second; if still resting at sched+20min, the field was IGNORED -> cancel
manually, verdict posted. Writes /tmp/EXPIRATION_VERDICT.md."""
import json, sys, time, urllib.request, urllib.error
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import live_v4 as L

import argparse
_ap = argparse.ArgumentParser(); _ap.add_argument("--oid", required=True); _ap.add_argument("--sched", type=float, required=True)
_a = _ap.parse_args(); OID = _a.oid; SCHED = _a.sched
OUT = Path("/tmp/EXPIRATION_VERDICT.md")
BASE = "https://api.elections.kalshi.com"
ak, pk = L.load_credentials()

def call(method, path):
    hdr = L.auth_headers(ak, pk, method, path)
    req = urllib.request.Request(BASE + path, method=method, headers=hdr)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]
    except Exception as e:
        return -1, str(e)[:200]

path = "/trade-api/v2/portfolio/orders/%s" % OID
time.sleep(max(0, SCHED - 120 - time.time()))
last_status = None
transition = None
while time.time() < SCHED + 1200:
    st, body = call("GET", path)
    o = (body.get("order") if isinstance(body, dict) else None) or \
        (body if isinstance(body, dict) else {})
    status = o.get("status")
    if status != last_status:
        now = time.time()
        with open("/tmp/expiration_checker.log", "a") as fh:
            fh.write("%s %.1f status=%s\n" % (
                time.strftime("%H:%M:%S"), now, status))
        if last_status is not None and status not in ("resting", None):
            transition = (now, status, o)
            break
        last_status = status
    time.sleep(5)
lines = ["# AT-EVENT-START EXPIRATION — VERDICT", "",
         "- probe order %s (1sh @2c, engine-invisible market), expiration_ts=%d "
         "(= milestone sched)" % (OID, int(SCHED))]
if transition:
    now, status, o = transition
    lines.append("- TRANSITION observed at %.1f (%s ET): status=%s"
                 % (now, time.strftime("%I:%M:%S %p",
                                       time.localtime(now)), status))
    lines.append("- delta vs sched: %+.1fs" % (now - SCHED))
    lines.append("- order object: `%s`" % json.dumps(o)[:400])
    lines.append("- (poll cadence 5s: the true cancel second is within "
                 "[obs-5s, obs]; the order's own updated ts in the object "
                 "is the exchange stamp)")
else:
    st, body = call("GET", path)
    lines.append("- NO transition by sched+20min: expiration_ts IGNORED "
                 "by the v2 endpoint (silently dropped field).")
    stc, bc = call("DELETE", "/trade-api/v2/portfolio/events/orders/%s" % OID)
    lines.append("- cleanup cancel: HTTP %s" % stc)
OUT.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
