#!/usr/bin/env python3
"""
Task 1: Check Kalshi historical data endpoints.
Task 2: Verify forward premarket tick collection timing.
"""
import os, time, base64, json, csv, requests
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

ARB_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ARB_DIR / ".env")
ak = os.getenv("KALSHI_API_KEY")
pk = serialization.load_pem_private_key(
    (ARB_DIR / "kalshi.pem").read_bytes(),
    password=None, backend=default_backend())
BASE = "https://api.elections.kalshi.com"
ET = ZoneInfo("America/New_York")

def auth(method, path):
    ts = str(int(time.time() * 1000))
    msg = ("%s%s%s" % (ts, method, path)).encode("utf-8")
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": ak,
            "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode("utf-8"),
            "KALSHI-ACCESS-TIMESTAMP": ts}

def get(path):
    r = requests.get(BASE + path, headers=auth("GET", path.split("?")[0]), timeout=15)
    try:
        return r.json(), r.status_code
    except:
        return {"_raw_len": len(r.content), "_content_type": r.headers.get("content-type","?")}, r.status_code

def fmt_et(epoch):
    return datetime.fromtimestamp(epoch, tz=ET).strftime("%I:%M %p ET") if epoch else "N/A"

# ============================================================
print("=" * 80)
print("TASK 1: KALSHI HISTORICAL DATA ENDPOINTS")
print("=" * 80)

# Test various historical/candlestick endpoints
# Use a current active ticker for testing
test_ticker = "KXATPCHALLENGERMATCH-26APR18FOMSUN-SUN"

endpoints = [
    "/trade-api/v2/markets/%s/history" % test_ticker,
    "/trade-api/v2/markets/%s/candlesticks" % test_ticker,
    "/trade-api/v2/markets/%s/orderbook" % test_ticker,
    "/trade-api/v2/series/KXATPCHALLENGERMATCH/markets/%s/history" % test_ticker,
    "/v1/markets/%s/history" % test_ticker,
    "/v1/markets/%s/candlesticks" % test_ticker,
]

# Also try with query params
endpoints_with_params = [
    "/trade-api/v2/markets/%s/history?limit=10" % test_ticker,
    "/trade-api/v2/markets/%s/candlesticks?series_ticker=KXATPCHALLENGERMATCH&period_interval=60" % test_ticker,
    "/trade-api/v2/markets/trades?ticker=%s&limit=10" % test_ticker,
    "/trade-api/v2/markets/%s/orderbook/history" % test_ticker,
]

print("\nProbing historical endpoints for %s:" % test_ticker)
for ep in endpoints + endpoints_with_params:
    try:
        data, status = get(ep)
        if status == 200:
            keys = list(data.keys()) if isinstance(data, dict) else "list[%d]" % len(data)
            print("  [%d] %s" % (status, ep[:70]))
            print("       Keys: %s" % keys)
            # Show first entry if it's a list
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list) and v:
                        print("       %s[0]: %s" % (k, json.dumps(v[0])[:150]))
                        break
                    elif not isinstance(v, list):
                        print("       %s: %s" % (k, str(v)[:100]))
        elif status == 404:
            print("  [404] %s  (not found)" % ep[:70])
        else:
            msg = json.dumps(data)[:80] if isinstance(data, dict) else str(data)[:80]
            print("  [%d] %s  %s" % (status, ep[:70], msg))
    except Exception as e:
        print("  [ERR] %s  %s" % (ep[:70], str(e)[:60]))
    time.sleep(0.2)

# Try the trades endpoint specifically
print("\nTrades endpoint (public trade history):")
trades_path = "/trade-api/v2/markets/trades?ticker=%s&limit=20" % test_ticker
data, status = get(trades_path)
if status == 200:
    trades = data.get("trades", [])
    print("  Trades returned: %d" % len(trades))
    if trades:
        print("  First trade: %s" % json.dumps(trades[0], indent=2))
        print("  Last trade:  %s" % json.dumps(trades[-1], indent=2))
        # Check timestamp range
        if len(trades) >= 2:
            t0 = trades[0].get("created_time", trades[0].get("ts", ""))
            t1 = trades[-1].get("created_time", trades[-1].get("ts", ""))
            print("  Time range: %s to %s" % (t0[:19], t1[:19]))
else:
    print("  Status: %d  %s" % (status, json.dumps(data)[:100]))

# Try candlesticks with V2
print("\nCandlestick probes:")
for period in [1, 5, 60, 1440]:
    ep = "/trade-api/v2/markets/%s/candlesticks?period_interval=%d" % (test_ticker, period)
    data, status = get(ep)
    if status == 200:
        candles = data.get("candlesticks", data.get("candles", []))
        print("  period=%d min: %d candles  keys=%s" % (period, len(candles) if isinstance(candles, list) else 0,
              list(data.keys())))
        if isinstance(candles, list) and candles:
            print("    Sample: %s" % json.dumps(candles[0])[:150])
    else:
        print("  period=%d min: [%d]" % (period, status))
    time.sleep(0.15)

# ============================================================
print("\n" + "=" * 80)
print("TASK 2: FORWARD COLLECTION TIMING AUDIT")
print("=" * 80)

TICKS_DIR = Path(__file__).resolve().parent / "analysis" / "premarket_ticks"

# Get market open_times from Kalshi
print("\nFetching market open_times for current tickers...")
series_list = ["KXATPMATCH", "KXWTAMATCH", "KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH"]
market_open_times = {}
for series in series_list:
    data, _ = get("/trade-api/v2/markets?limit=200&status=open&series_ticker=%s" % series)
    for m in (data or {}).get("markets", []):
        tk = m.get("ticker", "")
        ot = m.get("open_time", "")
        if ot:
            try:
                market_open_times[tk] = datetime.fromisoformat(ot.replace("Z", "+00:00")).timestamp()
            except:
                pass

# Check each premarket tick file
print("\n%-50s %-15s %-15s %-8s %-6s" % ("TICKER", "MKT_OPEN", "FIRST_TICK", "GAP", "TICKS"))

ticker_gaps = []
for f in sorted(TICKS_DIR.glob("*.csv")):
    tk = f.stem
    # Read first tick timestamp
    with open(f) as fh:
        reader = csv.reader(fh)
        header = next(reader)
        first_row = None
        tick_count = 0
        for row in reader:
            if first_row is None:
                first_row = row
            tick_count += 1

    if not first_row:
        continue

    first_tick_str = first_row[0]  # ts_et field
    try:
        first_tick_dt = datetime.strptime(first_tick_str, "%Y-%m-%d %I:%M:%S %p")
        first_tick_dt = first_tick_dt.replace(tzinfo=ET)
        first_tick_epoch = first_tick_dt.timestamp()
    except:
        continue

    mkt_open = market_open_times.get(tk)
    if mkt_open:
        gap_sec = first_tick_epoch - mkt_open
        gap_str = "%+.0fm" % (gap_sec / 60)
        ticker_gaps.append(gap_sec)
    else:
        gap_str = "no mkt"

    print("%-50s %-15s %-15s %-8s %5d" % (
        tk[:50],
        fmt_et(mkt_open) if mkt_open else "N/A",
        first_tick_str[11:22],
        gap_str,
        tick_count))

if ticker_gaps:
    print("\nGap distribution (first_tick - market_open):")
    s = sorted(ticker_gaps)
    n = len(s)
    print("  min=%.0fm  p25=%.0fm  median=%.0fm  p75=%.0fm  max=%.0fm" % (
        s[0]/60, s[int(n*0.25)]/60, s[int(n*0.5)]/60, s[int(n*0.75)]/60, s[-1]/60))
    print("  Negative = we captured ticks BEFORE market open (shouldn't happen)")
    print("  Positive = we missed early premarket by this many minutes")
    missed = sum(1 for g in ticker_gaps if g > 300)
    print("  Missed >5 min of premarket: %d / %d (%.0f%%)" % (
        missed, n, 100*missed/n if n else 0))

# Check live_v3 subscription timing
print("\n" + "=" * 80)
print("SUBSCRIPTION ARCHITECTURE")
print("=" * 80)
print()
print("Current live_v3 flow:")
print("  1. discover_markets() runs every 5 min")
print("  2. New tickers get ws_subscribe()")
print("  3. BBO snapshots arrive ~1s after subscribe")
print("  4. _log_tick() writes to premarket_ticks/*.csv")
print()
print("The gap between market_open and first_tick depends on:")
print("  a) How soon after market_open the next discovery cycle runs")
print("  b) Whether the market passes MIN_VOLUME filter (now 0, no issue)")
print("  c) Whether MAX_HOURS_TO_EXPIRY filter blocks it (now 36h, no issue)")
print()
print("Worst case gap: market opens 1s after a discovery cycle,")
print("  next cycle is 5 min later. So max ~5 min of missed premarket.")
print("  For most tennis markets, premarket is 6-12 hours. Missing")
print("  5 min out of 360+ min is negligible (<1.5%).")
