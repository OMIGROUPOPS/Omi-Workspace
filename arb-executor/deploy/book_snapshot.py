#!/usr/bin/env python3
"""[C47-ENFORCE] Bank the pre-restart book snapshot (paginated exchange truth)
to state/book_snapshot.json. Run by deploy_gate.sh BEFORE the restart so the
post-boot audit has an honest diff base. Exit nonzero on any pull failure --
the gate refuses to restart without a banked snapshot (assert-and-halt spirit).
Cwd must be arb-executor (kalshi.pem / .env / state/)."""
import base64, json, os, sys, time
from pathlib import Path

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

BASE = "https://api.elections.kalshi.com"


def creds():
    try:
        from dotenv import load_dotenv
        load_dotenv(".env")
    except ImportError:
        pass
    ak = os.getenv("KALSHI_API_KEY")
    pk = serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(),
                                            password=None, backend=default_backend())
    return ak, pk


def hdr(ak, pk, method, path):
    ts = str(int(time.time() * 1000))
    msg = ("%s%s%s" % (ts, method, path.split("?")[0])).encode()
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": ak, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
            "KALSHI-ACCESS-TIMESTAMP": ts}


def paged(ak, pk, base, key):
    out, cur = [], None
    while True:
        path = base + ("&cursor=%s" % cur if cur else "")
        r = requests.get(BASE + path, headers=hdr(ak, pk, "GET", path), timeout=30)
        r.raise_for_status()
        j = r.json()
        rows = j.get(key) or []
        out.extend(rows)
        cur = j.get("cursor")
        if not cur or not rows:
            return out
        time.sleep(0.1)


def main():
    ak, pk = creds()
    held = {p["ticker"]: float(p["position_fp"]) for p in paged(
        ak, pk, "/trade-api/v2/portfolio/positions?count_filter=position"
                "&settlement_status=unsettled&limit=200", "market_positions")
        if float(p.get("position_fp") or 0) != 0}
    buys, sells = {}, {}
    for o in paged(ak, pk, "/trade-api/v2/portfolio/orders?status=resting&limit=200", "orders"):
        d = buys if o.get("action") == "buy" else sells
        d[o["ticker"]] = d.get(o["ticker"], 0.0) + float(o.get("remaining_count_fp") or 0)
    Path("state").mkdir(exist_ok=True)
    json.dump({"ts": time.time(), "context": "gate_bank",
               "held": held, "buys": buys, "sells": sells},
              open("state/book_snapshot.json", "w"))
    print("[C47] banked pre-restart snapshot: %d positions, %d buy-legs, %d sell-legs"
          % (len(held), len(buys), len(sells)))


if __name__ == "__main__":
    sys.exit(main())
