#!/usr/bin/env python3
"""
kalshi_price_scraper.py — Continuous Kalshi price snapshot collector.

Every 5 min, queries all open Kalshi tennis markets and records
bid/ask/last/volume into kalshi_price_snapshots table in tennis.db.
"""

import hashlib, json, time, os, base64, requests, sqlite3, traceback
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

ET = ZoneInfo("America/New_York")
DB_PATH = str(Path(__file__).resolve().parent / "tennis.db")
POLL_INTERVAL = 300  # 5 minutes
BASE = "https://api.elections.kalshi.com"

SERIES = [
    "KXATPMATCH", "KXWTAMATCH",
    "KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH",
    "KXITFMATCH", "KXITFWMATCH",
]

load_dotenv(Path(__file__).resolve().parent / ".env")
_api_key = os.getenv("KALSHI_API_KEY")
_pk = serialization.load_pem_private_key(
    (Path(__file__).resolve().parent / "kalshi.pem").read_bytes(),
    password=None, backend=default_backend())


def _sign(method, path):
    ts = str(int(time.time() * 1000))
    msg = ts + method + path
    sig = _pk.sign(msg.encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": _api_key,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
            "KALSHI-ACCESS-TIMESTAMP": ts}


def _write_heartbeat(count, tickers):
    try:
        with open("/tmp/heartbeat_kalshi_price.json", "w") as f:
            json.dump({"ts": int(time.time()), "name": "kalshi_price",
                        "status": "ok", "rows_written": count, "tickers": tickers}, f)
    except Exception:
        pass


def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS kalshi_price_snapshots (
        polled_at TEXT NOT NULL,
        ticker TEXT NOT NULL,
        event_ticker TEXT NOT NULL,
        series_ticker TEXT,
        bid_cents INTEGER,
        ask_cents INTEGER,
        last_cents INTEGER,
        volume_24h REAL,
        commence_time TEXT,
        PRIMARY KEY (polled_at, ticker)
    )""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_kps_event ON kalshi_price_snapshots(event_ticker, polled_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_kps_ticker_time ON kalshi_price_snapshots(ticker, polled_at DESC)")
    # [W1 RETENTION V2] Full schedule-revision history. One row is retained
    # only when a market's schedule-bearing fields change; the exact HTTP
    # response hash that carried the revision is bound to it.
    cur.execute("""CREATE TABLE IF NOT EXISTS kalshi_schedule_revisions (
        ticker TEXT NOT NULL,
        schedule_sha256 TEXT NOT NULL,
        event_ticker TEXT NOT NULL,
        series_ticker TEXT,
        first_observed_at_utc TEXT NOT NULL,
        last_observed_at_utc TEXT NOT NULL,
        schedule_fields_json TEXT NOT NULL,
        raw_response_sha256 TEXT NOT NULL,
        request_path TEXT NOT NULL,
        PRIMARY KEY (ticker, schedule_sha256)
    )""")
    cur.execute("""CREATE INDEX IF NOT EXISTS idx_ksr_event_time
        ON kalshi_schedule_revisions(event_ticker, first_observed_at_utc)""")
    conn.commit()
    conn.close()


def poll_cycle():
    now_et = datetime.now(ET)
    polled_at = now_et.strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    revision_rows = []
    for series in SERIES:
        path = "/trade-api/v2/markets"
        try:
            r = requests.get(BASE + path + "?series_ticker=%s&status=open&limit=500" % series,
                             headers=_sign("GET", path), timeout=15)
            if r.status_code != 200:
                continue
            received_at = datetime.now(timezone.utc).isoformat()
            raw_response_sha256 = hashlib.sha256(r.content).hexdigest()
            response = r.json()
            request_path = path + "?series_ticker=%s&status=open&limit=500" % series
            for m in response.get("markets", []):
                ticker = m.get("ticker", "")
                if not ticker:
                    continue
                bid = round(float(m.get("yes_bid_dollars", "0") or "0") * 100)
                ask = round(float(m.get("yes_ask_dollars", "0") or "0") * 100)
                last = round(float(m.get("last_price_dollars", "0") or "0") * 100)
                vol = float(m.get("volume_24h_fp", "0") or "0")
                commence = m.get("expected_expiration_time", "")
                rows.append((polled_at, ticker, m.get("event_ticker", ""),
                             series, bid, ask, last, vol, commence))
                schedule_fields = {
                    field: m.get(field)
                    for field in (
                        "open_time",
                        "close_time",
                        "expected_expiration_time",
                        "expiration_time",
                        "latest_expiration_time",
                        "occurrence_datetime",
                        "status",
                    )
                }
                schedule_json = json.dumps(
                    schedule_fields, sort_keys=True, separators=(",", ":")
                )
                schedule_sha256 = hashlib.sha256(
                    schedule_json.encode("utf-8")
                ).hexdigest()
                revision_rows.append((
                    ticker, schedule_sha256, m.get("event_ticker", ""),
                    series, received_at, received_at, schedule_json,
                    raw_response_sha256, request_path,
                ))
        except Exception as e:
            print("  Error fetching %s: %s" % (series, e))
        time.sleep(0.1)

    if not rows:
        print("[%s] No rows to insert" % now_et.strftime("%I:%M:%S %p ET"))
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cur = conn.cursor()
        cur.executemany(
            "INSERT OR REPLACE INTO kalshi_price_snapshots VALUES (?,?,?,?,?,?,?,?,?)",
            rows)
        cur.executemany(
            """INSERT INTO kalshi_schedule_revisions
               (ticker, schedule_sha256, event_ticker, series_ticker,
                first_observed_at_utc, last_observed_at_utc,
                schedule_fields_json, raw_response_sha256, request_path)
               VALUES (?,?,?,?,?,?,?,?,?)
               ON CONFLICT(ticker, schedule_sha256) DO UPDATE SET
                 last_observed_at_utc=excluded.last_observed_at_utc""",
            revision_rows,
        )
        conn.commit()
    except Exception as e:
        print("  DB error: %s" % e)
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

    unique_tickers = len(set(r[1] for r in rows))
    print("[%s] Snapshotted %d rows (%d tickers)" % (
        now_et.strftime("%I:%M:%S %p ET"), len(rows), unique_tickers))
    _write_heartbeat(len(rows), unique_tickers)


if __name__ == "__main__":
    print("Kalshi Price Scraper — polling every %ds" % POLL_INTERVAL)
    print("=" * 50)
    init_db()
    while True:
        try:
            poll_cycle()
        except Exception as e:
            print("Error: %s" % e)
            traceback.print_exc()
        time.sleep(POLL_INTERVAL)
