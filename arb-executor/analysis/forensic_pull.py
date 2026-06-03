#!/usr/bin/env python3
"""READ-ONLY forensic data pull: fills, settlements, positions, resting orders since 2026-06-01.
Dumps raw JSON to /tmp/forensic_data.json and prints field names of samples (verify _dollars vs cents)."""
import time, base64, requests, json
from pathlib import Path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

BASE = "https://api.elections.kalshi.com"
AK = "f3b064d1-a02e-42a4-b2b1-132834694d23"
PK = serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(), password=None, backend=default_backend())


def sign(ts, m, p):
    s = PK.sign((ts + m + p).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return base64.b64encode(s).decode()


def get(path):
    ts = str(int(time.time() * 1000)); sp = path.split("?")[0]
    h = {"KALSHI-ACCESS-KEY": AK, "KALSHI-ACCESS-SIGNATURE": sign(ts, "GET", sp), "KALSHI-ACCESS-TIMESTAMP": ts}
    r = requests.get(BASE + path, headers=h, timeout=25)
    return r.json() if r.status_code == 200 else {"_err": r.status_code, "_body": r.text[:200]}


def paginate(base_path, key):
    out = []; cur = ""
    for _ in range(40):
        p = base_path + ("&cursor=" + cur if cur else "")
        d = get(p)
        if "_err" in d:
            print("ERR", base_path, d); break
        out += d.get(key, []); cur = d.get("cursor", "")
        if not cur:
            break
    return out


TENNIS = ("KXATPMATCH", "KXWTAMATCH", "KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH")


def istennis(tk):
    return any(tk.startswith(p) for p in TENNIS)


fills = paginate("/trade-api/v2/portfolio/fills?limit=500", "fills")
setts = paginate("/trade-api/v2/portfolio/settlements?limit=500", "settlements")
pos = get("/trade-api/v2/portfolio/positions?limit=500")
orders = paginate("/trade-api/v2/portfolio/orders?status=resting&limit=500", "orders")

tf = [f for f in fills if istennis(f.get("ticker", ""))]
ts_ = [s for s in setts if istennis(s.get("ticker", ""))]
to_ = [o for o in orders if istennis(o.get("ticker", ""))]
mp = pos.get("market_positions", []) if isinstance(pos, dict) else []
tp = [p for p in mp if istennis(p.get("ticker", ""))]

json.dump({"fills": tf, "settlements": ts_, "positions": tp, "orders": to_}, open("/tmp/forensic_data.json", "w"))
print("TENNIS  fills:", len(tf), " settlements:", len(ts_), " open_positions:", len(tp), " resting_orders:", len(to_))
print("(all fills:", len(fills), " all settlements:", len(setts), ")")
print("\n=== SAMPLE FILL (raw fields) ===\n", json.dumps(tf[0], indent=2) if tf else "none")
print("\n=== SAMPLE SETTLEMENT (raw fields) ===\n", json.dumps(ts_[0], indent=2) if ts_ else "none")
print("\n=== SAMPLE POSITION (raw fields) ===\n", json.dumps(tp[0], indent=2) if tp else "none")
print("\n=== SAMPLE RESTING ORDER (raw fields) ===\n", json.dumps(to_[0], indent=2) if to_ else "none")
