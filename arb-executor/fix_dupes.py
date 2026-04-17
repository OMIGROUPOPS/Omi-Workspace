#!/usr/bin/env python3
"""Step 1-2: Cancel duplicate orders, check positions, post missing exits."""
import os, time, base64, json, uuid, requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
ak = os.getenv("KALSHI_API_KEY")
pk = serialization.load_pem_private_key(
    (Path(__file__).resolve().parent / "kalshi.pem").read_bytes(),
    password=None, backend=default_backend())
BASE = "https://api.elections.kalshi.com"
ET = ZoneInfo("America/New_York")
EXIT_CAP = 98

def auth(method, path):
    ts = str(int(time.time() * 1000))
    msg = ("%s%s%s" % (ts, method, path)).encode("utf-8")
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": ak,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode("utf-8"),
            "KALSHI-ACCESS-TIMESTAMP": ts, "Content-Type": "application/json"}

def get(path):
    r = requests.get(BASE + path, headers=auth("GET", path.split("?")[0]), timeout=15)
    return r.json()

# Cell config for exit computation
config = json.load(open(Path(__file__).resolve().parent / "config" / "deploy_v3.json"))

print("=" * 60)
print("STEP 1: CANCEL DUPLICATES")
print("=" * 60)

# Get all resting orders
ord_path = "/trade-api/v2/portfolio/orders?status=resting&limit=500"
resting = get(ord_path).get("orders", [])
print("\nAll resting orders (%d):" % len(resting))

# Group by ticker
by_ticker = {}
for o in resting:
    tk = o.get("ticker", "")
    by_ticker.setdefault(tk, []).append(o)

for tk, orders in sorted(by_ticker.items()):
    for o in sorted(orders, key=lambda x: x.get("created_time", "")):
        pr = round(float(o.get("yes_price_dollars", "0")) * 100)
        created = o.get("created_time", "")[:19]
        created_et = ""
        try:
            ts = datetime.fromisoformat(created.replace("Z", "+00:00") if "Z" not in created else created + "+00:00")
            created_et = ts.astimezone(ET).strftime("%I:%M %p ET")
        except:
            created_et = created
        print("  %-50s %s %dc  %s  oid=%s" % (
            tk[:50], o.get("action"), pr, created_et, o.get("order_id", "")[:12]))

# Identify duplicates to cancel
# BOLYUN-YUN: cancel older (c80a0eeb from 06:04 PM), keep newer (3d51357a from 06:16 PM)
# FOMSUN-FOM: cancel older manual (76d7dc27 from 05:11 PM), keep newer bot (741dbd5c from 06:16 PM)
to_cancel = []
for tk, orders in by_ticker.items():
    buys = [o for o in orders if o.get("action") == "buy"]
    if len(buys) <= 1:
        continue
    # Sort by created_time ascending — cancel all but the newest
    buys.sort(key=lambda x: x.get("created_time", ""))
    for old in buys[:-1]:
        pr = round(float(old.get("yes_price_dollars", "0")) * 100)
        to_cancel.append((tk, old.get("order_id"), pr, old.get("created_time", "")[:19]))

print("\nOrders to cancel (%d):" % len(to_cancel))
for tk, oid, pr, created in to_cancel:
    print("  CANCEL: %s  %dc  created=%s  oid=%s" % (tk[:45], pr, created, oid[:12]))
    del_path = "/trade-api/v2/portfolio/orders/%s" % oid
    r = requests.delete(BASE + del_path, headers=auth("DELETE", del_path), timeout=10)
    status = "OK" if r.status_code in (200, 204) else "FAILED(%d)" % r.status_code
    print("    -> %s" % status)
    time.sleep(0.2)

print("\n" + "=" * 60)
print("STEP 2: CHECK POSITIONS + POST MISSING EXITS")
print("=" * 60)

# Get positions
pos_path = "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled"
positions = get(pos_path).get("market_positions", [])
print("\nFilled positions (%d):" % len(positions))

# Re-fetch resting after cancels
time.sleep(1)
resting2 = get(ord_path).get("orders", [])
resting_tickers = {}
for o in resting2:
    tk = o.get("ticker", "")
    action = o.get("action", "")
    resting_tickers.setdefault(tk, []).append(action)

for p in positions:
    tk = p.get("ticker", "")
    qty = int(float(p.get("position_fp", 0)))
    total_cents = round(float(p.get("total_traded_dollars", 0)) * 100)
    avg = total_cents // qty if qty > 0 else 0
    has_exit = "sell" in resting_tickers.get(tk, [])
    print("  %-50s qty=%d  avg=%dc  exit_resting=%s" % (tk[:50], qty, avg, has_exit))

    if not has_exit and qty > 0:
        # Need to post exit — determine cell
        parts = tk.rsplit("-", 1)
        event_tk = parts[0] if len(parts) == 2 else tk
        player_code = parts[1] if len(parts) == 2 else ""

        # Determine direction from price
        direction = "leader" if avg > 50 else "underdog"

        # Determine category
        cat = None
        series_map = {
            'ATP_MAIN': ['KXATPMATCH'], 'WTA_MAIN': ['KXWTAMATCH'],
            'ATP_CHALL': ['KXATPCHALLENGERMATCH'], 'WTA_CHALL': ['KXWTACHALLENGERMATCH'],
        }
        for c, prefixes in series_map.items():
            for prefix in prefixes:
                if tk.startswith(prefix):
                    cat = c
                    break

        if cat:
            bucket = (avg // 5) * 5
            cell_name = "%s_%s_%d-%d" % (cat, direction, bucket, bucket + 4)
            cell_cfg = config["active_cells"].get(cell_name)
            if cell_cfg:
                exit_price = min(avg + cell_cfg["exit_cents"], EXIT_CAP)
                print("    -> POSTING EXIT: cell=%s  exit=%dc (avg %d + %d, cap %d)" % (
                    cell_name, exit_price, avg, cell_cfg["exit_cents"], EXIT_CAP))
                payload = {
                    "ticker": tk, "action": "sell", "side": "yes",
                    "type": "limit", "count": qty, "yes_price": exit_price,
                    "post_only": True, "client_order_id": str(uuid.uuid4()),
                }
                r = requests.post(BASE + "/trade-api/v2/portfolio/orders",
                                  headers=auth("POST", "/trade-api/v2/portfolio/orders"),
                                  json=payload, timeout=15)
                if r.status_code in (200, 201):
                    oid = r.json().get("order", {}).get("order_id", "?")
                    print("    -> OK  oid=%s" % oid[:12])
                else:
                    print("    -> FAILED(%d): %s" % (r.status_code, r.text[:200]))
            else:
                print("    -> [WARN] cell %s not in active_cells, no exit posted" % cell_name)
        else:
            print("    -> [WARN] unknown category, no exit posted")

print("\n" + "=" * 60)
print("FINAL STATE")
print("=" * 60)

time.sleep(1)
resting3 = get(ord_path).get("orders", [])
print("\nResting orders (%d):" % len(resting3))
for o in sorted(resting3, key=lambda x: x.get("ticker", "")):
    tk = o.get("ticker", "")
    pr = round(float(o.get("yes_price_dollars", "0")) * 100)
    action = o.get("action", "")
    qty = int(float(o.get("remaining_count_fp", o.get("initial_count_fp", 0)) or 0))
    print("  %-50s %s %dc qty=%d oid=%s" % (tk[:50], action, pr, qty, o.get("order_id","")[:12]))

positions2 = get(pos_path).get("market_positions", [])
print("\nPositions (%d):" % len(positions2))
for p in positions2:
    tk = p.get("ticker", "")
    qty = int(float(p.get("position_fp", 0)))
    total_cents = round(float(p.get("total_traded_dollars", 0)) * 100)
    avg = total_cents // qty if qty > 0 else 0
    print("  %-50s qty=%d  avg=%dc" % (tk[:50], qty, avg))
