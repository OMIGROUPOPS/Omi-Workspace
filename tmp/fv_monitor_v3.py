#!/usr/bin/env python3
"""FV convergence monitor v3 — uses get_consensus_fv for all sources (Pinnacle + BetExplorer)."""
import sqlite3, time, os, base64, requests, sys, traceback
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

sys.path.insert(0, "/root/Omi-Workspace/arb-executor")
from fv import get_consensus_fv

ET = ZoneInfo("America/New_York")
load_dotenv(Path("/root/Omi-Workspace/arb-executor/.env"))
api_key = os.getenv("KALSHI_API_KEY")
pk = serialization.load_pem_private_key(
    Path("/root/Omi-Workspace/arb-executor/kalshi.pem").read_bytes(),
    password=None, backend=default_backend())
BASE = "https://api.elections.kalshi.com"

def auth(method, path):
    ts = str(int(time.time() * 1000))
    msg = ("%s%s%s" % (ts, method, path)).encode("utf-8")
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": api_key,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode("utf-8"),
            "KALSHI-ACCESS-TIMESTAMP": ts}

def get(path):
    return requests.get(BASE + path, headers=auth("GET", path.split("?")[0]), timeout=15).json()

LOG = "/tmp/fv_convergence_monitor.csv"
if not os.path.exists(LOG):
    with open(LOG, "w") as f:
        f.write("timestamp_et,event_ticker,side,player,kalshi_last,kalshi_bid,kalshi_ask,pinnacle_fv,gap_cents,gap_pct,time_to_start_hrs,fv_source,fv_tier\n")

def snapshot():
    now_et = datetime.now(ET)
    now_utc = datetime.now(timezone.utc)

    conn = sqlite3.connect("/root/Omi-Workspace/arb-executor/tennis.db", timeout=10)
    cur = conn.cursor()

    # Get ALL distinct events with any FV source (polled_at stored in ET)
    cutoff = (now_et - __import__('datetime').timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""SELECT event_ticker, player1_name, player2_name, commence_time
                   FROM book_prices
                   WHERE event_ticker IN (
                       SELECT event_ticker FROM book_prices
                       GROUP BY event_ticker
                       HAVING MAX(polled_at) > ?
                   )
                   GROUP BY event_ticker""", (cutoff,))
    rows = cur.fetchall()
    conn.close()
    ts_str = now_et.strftime("%Y-%m-%d %I:%M:%S %p ET")
    count = 0

    for et, p1, p2, commence in rows:
        tts_hrs = None
        if commence:
            try:
                ct = datetime.fromisoformat(commence.replace("Z", "+00:00"))
                tts_hrs = round((ct - now_utc).total_seconds() / 3600, 2)
            except:
                pass

        try:
            mkts = get("/trade-api/v2/markets?event_ticker=%s&limit=10" % et).get("markets", [])
        except:
            continue

        for m in mkts:
            yst = m.get("yes_sub_title", "").upper()
            try:
                last = round(float(m.get("last_price_dollars", "0") or "0") * 100)
                bid = round(float(m.get("yes_bid_dollars", "0") or "0") * 100)
                ask = round(float(m.get("yes_ask_dollars", "0") or "0") * 100)
            except:
                continue
            if last == 0:
                continue

            p1l = p1.split()[-1].upper() if p1 else ""
            p2l = p2.split()[-1].upper() if p2 else ""
            if p1l in yst:
                side, player = "p1", p1
            elif p2l in yst:
                side, player = "p2", p2
            else:
                continue

            fv_result = get_consensus_fv(et, side)
            if not fv_result or fv_result.get("fv_cents") is None:
                continue

            fv = fv_result["fv_cents"]
            fv_source = fv_result["source"]
            fv_tier = fv_result["tier"]

            gap = last - fv
            pct = (gap / fv * 100) if fv > 0 else 0
            tts = "%.2f" % tts_hrs if tts_hrs is not None else ""
            with open(LOG, "a") as f:
                f.write("%s,%s,%s,\"%s\",%d,%d,%d,%.1f,%+.1f,%+.1f,%s,%s,%d\n" % (
                    ts_str, et, side, player, last, bid, ask, fv, gap, pct, tts,
                    fv_source, fv_tier))
            count += 1
        time.sleep(0.08)

    print("[%s] Snapshotted %d sides across %d events" % (now_et.strftime("%I:%M:%S %p ET"), count, len(rows)))
    try:
        import json as _json
        with open("/tmp/heartbeat_fv_monitor.json", "w") as _f:
            _json.dump({"ts": int(time.time()), "name": "fv_monitor", "status": "ok", "rows_written": count, "events": len(rows)}, _f)
    except Exception:
        pass

while True:
    try:
        snapshot()
    except Exception as e:
        print("Error: %s" % e)
        traceback.print_exc()
    time.sleep(300)
