#!/usr/bin/env python3
"""READ-ONLY exchange-truth pull for the 2026-07-06 autopsy.
Pulls fills + settlements + positions + balance since session boot (2026-07-05 23:50 ET
= 2026-07-06 03:50 UTC, epoch 1783309800). Writes JSON to /tmp/autopsy_truth/.
"""
import time, base64, json, os
from pathlib import Path
from datetime import datetime, timezone
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

BASE = "https://api.elections.kalshi.com"
AK = "f3b064d1-a02e-42a4-b2b1-132834694d23"
PEM = Path("/root/Omi-Workspace/arb-executor/kalshi.pem")
if not PEM.exists():
    # fall back to common locations
    for cand in ("/root/arb-executor/kalshi.pem", "/root/kalshi.pem", "/root/Omi-Workspace/kalshi.pem"):
        if Path(cand).exists():
            PEM = Path(cand); break
PK = serialization.load_pem_private_key(PEM.read_bytes(), password=None, backend=default_backend())

def sign(ts, m, p):
    s = PK.sign((ts + m + p).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return base64.b64encode(s).decode()

def get(path):
    for attempt in range(3):
        ts = str(int(time.time() * 1000)); sp = path.split("?")[0]
        h = {"KALSHI-ACCESS-KEY": AK, "KALSHI-ACCESS-SIGNATURE": sign(ts, "GET", sp),
             "KALSHI-ACCESS-TIMESTAMP": ts}
        r = requests.get(BASE + path, headers=h, timeout=20)
        if r.status_code == 200:
            return r.json()
        time.sleep(1 + attempt)
    print(f"FAIL {path} -> {r.status_code} {r.text[:200]}")
    return None

BOOT = datetime(2026, 7, 6, 3, 50, 0, tzinfo=timezone.utc)
OUT = Path("/tmp/autopsy_truth"); OUT.mkdir(exist_ok=True)

def paged(endpoint, key, cutoff_field="created_time"):
    rows, cursor = [], ""
    for _ in range(200):
        p = f"/trade-api/v2{endpoint}?limit=200" + (f"&cursor={cursor}" if cursor else "")
        d = get(p)
        if not d: break
        batch = d.get(key, [])
        if not batch: break
        rows += batch
        cursor = d.get("cursor", "")
        last = batch[-1].get(cutoff_field) or batch[-1].get("settled_time") or ""
        if not cursor: break
        try:
            if last and datetime.fromisoformat(last.replace("Z", "+00:00")) < BOOT:
                break
        except ValueError:
            pass
        time.sleep(0.15)
    return rows

fills = paged("/portfolio/fills", "fills")
print("fills pulled:", len(fills))
sess_fills = [f for f in fills
              if datetime.fromisoformat(f["created_time"].replace("Z", "+00:00")) >= BOOT]
print("session fills (>= boot):", len(sess_fills))
(OUT / "fills_session.json").write_text(json.dumps(sess_fills, indent=1))
(OUT / "fills_raw_window.json").write_text(json.dumps(fills, indent=1))

setts = paged("/portfolio/settlements", "settlements", cutoff_field="settled_time")
print("settlements pulled:", len(setts))
sess_setts = [s for s in setts
              if datetime.fromisoformat((s.get("settled_time") or "1970-01-01T00:00:00Z").replace("Z", "+00:00")) >= BOOT]
print("session settlements:", len(sess_setts))
(OUT / "settlements_session.json").write_text(json.dumps(sess_setts, indent=1))

pos_rows, cursor = [], ""
for _ in range(50):
    p = "/trade-api/v2/portfolio/positions?limit=200&settlement_status=unsettled" + (f"&cursor={cursor}" if cursor else "")
    d = get(p)
    if not d: break
    pos_rows += d.get("market_positions", [])
    cursor = d.get("cursor", "")
    if not cursor: break
    time.sleep(0.15)
print("open market positions:", len([p for p in pos_rows if p.get("position", 0) != 0]))
(OUT / "positions.json").write_text(json.dumps(pos_rows, indent=1))

bal = get("/trade-api/v2/portfolio/balance")
print("balance:", bal)
(OUT / "balance.json").write_text(json.dumps(bal, indent=1))
print("DONE ->", OUT)
