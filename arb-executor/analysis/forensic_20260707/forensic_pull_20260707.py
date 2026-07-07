#!/usr/bin/env python3
"""READ-ONLY forensic pull 2026-07-07 morning.
Exchange truth: fills since 00:00 ET, all unsettled positions, all resting orders, marks.
Outputs JSON to stdout. No writes, no order placement."""
import base64, json, os, sys, time
from pathlib import Path
from datetime import datetime, timezone

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

BASE = "https://api.elections.kalshi.com"
ROOT = Path("/root/Omi-Workspace/arb-executor")
CUTOFF_UTC = "2026-07-07T04:00:00Z"  # 00:00 ET


def load_creds():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    ak = os.getenv("KALSHI_API_KEY")
    pk = serialization.load_pem_private_key((ROOT / "kalshi.pem").read_bytes(),
                                            password=None, backend=default_backend())
    return ak, pk


def headers(ak, pk, method, path):
    ts = str(int(time.time() * 1000))
    msg = ("%s%s%s" % (ts, method, path.split("?")[0])).encode()
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": ak,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
            "KALSHI-ACCESS-TIMESTAMP": ts, "Content-Type": "application/json"}


def get(ak, pk, path):
    for attempt in range(5):
        r = requests.get(BASE + path, headers=headers(ak, pk, "GET", path), timeout=30)
        if r.status_code == 429:
            time.sleep(1 + attempt)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("rate-limited 5x on " + path)


def paged(ak, pk, path_base, key):
    out, cursor = [], None
    while True:
        path = path_base + ("&cursor=%s" % cursor if cursor else "")
        j = get(ak, pk, path)
        rows = j.get(key) or []
        out.extend(rows)
        cursor = j.get("cursor")
        if not cursor or not rows:
            return out
        time.sleep(0.15)


def main():
    ak, pk = load_creds()
    result = {"pulled_at_utc": datetime.now(timezone.utc).isoformat(),
              "cutoff_utc": CUTOFF_UTC}

    # ---- fills (paginate back past cutoff; keep 48h for restart-window context) ----
    fills = paged(ak, pk, "/trade-api/v2/portfolio/fills?limit=200", "fills")
    keep_floor = "2026-07-05T12:00:00Z"
    fills = [f for f in fills if (f.get("created_time") or "") >= keep_floor]
    result["fills_48h_count"] = len(fills)
    result["fills"] = fills

    # ---- positions (exchange referee) ----
    mkt_pos = paged(ak, pk,
        "/trade-api/v2/portfolio/positions?limit=200&count_filter=position&settlement_status=unsettled",
        "market_positions")
    mkt_pos = [p for p in mkt_pos if p.get("position")]
    result["positions"] = mkt_pos

    # ---- resting orders ----
    orders = paged(ak, pk, "/trade-api/v2/portfolio/orders?status=resting&limit=200", "orders")
    result["resting_orders"] = orders

    # ---- marks for held tickers ----
    marks = {}
    for p in mkt_pos:
        tk = p["ticker"]
        try:
            m = get(ak, pk, "/trade-api/v2/markets/%s" % tk).get("market", {})
            marks[tk] = {"yes_bid": m.get("yes_bid"), "yes_ask": m.get("yes_ask"),
                         "last_price": m.get("last_price"), "status": m.get("status")}
        except Exception as e:
            marks[tk] = {"error": str(e)}
        time.sleep(0.12)
    result["marks"] = marks

    json.dump(result, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
