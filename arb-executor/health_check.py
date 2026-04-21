#!/usr/bin/env python3
"""Single-command health check. Shows sidecar status + FV coverage + alerts."""
import os, time, json, sqlite3, subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tennis.db")

SIDECARS = {
    "tennis_odds": {"process": "tennis_odds.py", "expected_interval": 600},
    "betexplorer": {"process": "betexplorer.py", "expected_interval": 700},
    "fv_monitor": {"process": "fv_monitor", "expected_interval": 400},
    "live_v3": {"process": "live_v3.py", "expected_interval": 10},
    "kalshi_price": {"process": "kalshi_price_scraper.py", "expected_interval": 400},
}


def check_sidecars():
    results = {}
    for name, cfg in SIDECARS.items():
        alive = subprocess.run(["pgrep", "-f", cfg["process"]], capture_output=True).returncode == 0
        hb_path = "/tmp/heartbeat_%s.json" % name
        hb = {}
        age = None
        if os.path.exists(hb_path):
            try:
                with open(hb_path) as f:
                    hb = json.load(f)
                age = int(time.time()) - hb.get("ts", 0)
            except Exception:
                pass
        status = "DEAD"
        if alive:
            if age is not None and age > cfg["expected_interval"] * 2:
                status = "STALE"
            elif age is not None:
                status = "OK"
            else:
                status = "NO_HB"
        results[name] = {"alive": alive, "status": status, "heartbeat": hb, "age_sec": age}
    return results


def check_fv_coverage():
    now_et = datetime.now(ET)
    cutoff = (now_et - __import__("datetime").timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cur = conn.cursor()
        cur.execute("""SELECT book_key, COUNT(DISTINCT event_ticker), MAX(polled_at)
                       FROM book_prices WHERE polled_at > ?
                       GROUP BY book_key ORDER BY book_key""", (cutoff,))
        rows = [{"book": r[0], "events": r[1], "last_poll": r[2]} for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception:
        return []


def check_positions():
    try:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.backends import default_backend
        from dotenv import load_dotenv
        from pathlib import Path
        import base64, requests

        load_dotenv(Path(os.path.dirname(os.path.abspath(__file__))) / ".env")
        api_key = os.getenv("KALSHI_API_KEY")
        pk = serialization.load_pem_private_key(
            (Path(os.path.dirname(os.path.abspath(__file__))) / "kalshi.pem").read_bytes(),
            password=None, backend=default_backend())
        BASE = "https://api.elections.kalshi.com"

        def sign(m, p):
            ts = str(int(time.time() * 1000))
            msg = ts + m + p
            sig = pk.sign(msg.encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                          salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
            return {"KALSHI-ACCESS-KEY": api_key,
                    "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
                    "KALSHI-ACCESS-TIMESTAMP": ts}

        path = "/trade-api/v2/portfolio/balance"
        r = requests.get(BASE + path, headers=sign("GET", path), timeout=10)
        bal = r.json()
        cash = float(bal.get("balance", 0)) / 100
        port = float(bal.get("portfolio_value", 0)) / 100

        path = "/trade-api/v2/portfolio/positions"
        r = requests.get(BASE + path + "?count_filter=position&settlement_status=unsettled&limit=200",
                         headers=sign("GET", path), timeout=10)
        positions = len(r.json().get("market_positions", []))

        path = "/trade-api/v2/portfolio/orders"
        r = requests.get(BASE + path + "?status=resting&limit=200",
                         headers=sign("GET", path), timeout=10)
        orders = r.json().get("orders", [])
        buys = sum(1 for o in orders if o.get("action") == "buy")
        sells = sum(1 for o in orders if o.get("action") == "sell")

        return {"cash": cash, "portfolio": port, "total": cash + port,
                "positions": positions, "buys": buys, "sells": sells}
    except Exception as e:
        return {"error": str(e)}


def main():
    now_et = datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p ET")
    print("=== HEALTH CHECK @ %s ===" % now_et)
    print()

    print("SIDECARS:")
    sidecars = check_sidecars()
    alerts = []
    for name, info in sidecars.items():
        age_str = "%ds" % info["age_sec"] if info["age_sec"] is not None else "no heartbeat"
        extra = {k: v for k, v in info["heartbeat"].items() if k not in ("ts", "name", "status")}
        extra_str = " %s" % extra if extra else ""
        print("  %-14s %-7s (heartbeat %s)%s" % (name, info["status"], age_str, extra_str))
        if info["status"] == "DEAD":
            alerts.append("%s is DEAD" % name)
        elif info["status"] == "STALE":
            alerts.append("%s heartbeat stale (%ds old)" % (name, info["age_sec"]))

    print()
    print("FV COVERAGE (last 30 min):")
    coverage = check_fv_coverage()
    if coverage:
        for c in coverage:
            print("  %-15s %d events  (last: %s)" % (c["book"], c["events"], c["last_poll"]))
    else:
        print("  (unable to query)")

    print()
    print("PORTFOLIO:")
    port = check_positions()
    if "error" not in port:
        print("  Cash: $%.2f  Portfolio: $%.2f  Total: $%.2f" % (port["cash"], port["portfolio"], port["total"]))
        print("  Positions: %d  Orders: %d buys, %d sells" % (port["positions"], port["buys"], port["sells"]))
        print("  Deploy baseline: $2,789.18  P&L: %+.2f" % (port["total"] - 2789.18))
    else:
        print("  Error: %s" % port["error"])

    print()
    print("INTELLIGENCE:")
    try:
        from intelligence import confidence_score, _conn
        ic = _conn()
        icur = ic.cursor()
        icur.execute("""
            SELECT DISTINCT kps.event_ticker, kps.ticker
            FROM kalshi_price_snapshots kps
            INNER JOIN (SELECT ticker, MAX(polled_at) as mp FROM kalshi_price_snapshots GROUP BY ticker) l
            ON kps.ticker = l.ticker AND kps.polled_at = l.mp
        """)
        tks = icur.fetchall()
        ic.close()
        tiers = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "SKIP": 0}
        for et, tk in tks:
            try:
                cs = confidence_score(et, tk)
                tiers[cs.get("grade", "SKIP")] = tiers.get(cs.get("grade", "SKIP"), 0) + 1
            except Exception:
                tiers["SKIP"] += 1
        total = sum(tiers.values())
        tradeable = tiers["HIGH"] + tiers["MEDIUM"] + tiers["LOW"]
        print("  %d tickers: HIGH=%d MEDIUM=%d LOW=%d SKIP=%d  (%.0f%% tradeable)" % (
            total, tiers["HIGH"], tiers["MEDIUM"], tiers["LOW"], tiers["SKIP"],
            tradeable / total * 100 if total > 0 else 0))
    except Exception as e:
        print("  Error: %s" % str(e)[:100])

    print()
    print("ALERTS:")
    if alerts:
        for a in alerts:
            print("  !! %s" % a)
    else:
        print("  None")


if __name__ == "__main__":
    main()
