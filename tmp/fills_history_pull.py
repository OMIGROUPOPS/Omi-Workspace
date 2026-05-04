#!/usr/bin/env python3
"""
Pull Kalshi account fill history from /trade-api/v2/portfolio/fills.
Read-only against Kalshi API. Paginates via cursor + min_ts/max_ts.
Saves to /tmp/kalshi_fills_history.json. Prints stats.
"""
import sys, os, asyncio, time, json, hashlib
sys.path.insert(0, "/root/Omi-Workspace/arb-executor")
sys.path.insert(0, "/root/Omi-Workspace/arb-executor/intra_kalshi")

import aiohttp
from intra_kalshi.live_scanner import auth_headers, load_credentials

BASE_URL = "https://api.elections.kalshi.com"
OUT_PATH = "/tmp/kalshi_fills_history.json"

async def fetch_all():
    ak, pk = load_credentials()
    print("credentials loaded ok")
    # Date range: 2026-03-01 UTC to now
    import datetime
    min_ts = int(datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc).timestamp())
    max_ts = int(time.time())
    print("date range: min_ts=%d (2026-03-01) max_ts=%d (%s)" % (
        min_ts, max_ts, datetime.datetime.fromtimestamp(max_ts, tz=datetime.timezone.utc).isoformat()))

    all_fills = []
    cursor = ""
    page = 0
    async with aiohttp.ClientSession() as session:
        while True:
            page += 1
            path = "/trade-api/v2/portfolio/fills?min_ts=%d&max_ts=%d&limit=1000" % (min_ts, max_ts)
            if cursor:
                path += "&cursor=%s" % cursor
            url = BASE_URL + path
            headers = auth_headers(ak, pk, "GET", path)
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as r:
                    body = await r.text()
                    if r.status != 200:
                        print("PAGE %d HTTP %d: %s" % (page, r.status, body[:300]))
                        break
                    data = json.loads(body)
            except Exception as e:
                print("PAGE %d EXCEPTION: %s" % (page, e))
                break
            fills = data.get("fills", [])
            cursor = data.get("cursor", "")
            print("PAGE %d: %d fills (cursor=%r)" % (page, len(fills), cursor[:30]))
            all_fills.extend(fills)
            if not cursor or not fills:
                break
            await asyncio.sleep(0.5)  # gentle rate

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump({"fills": all_fills, "min_ts": min_ts, "max_ts": max_ts,
                   "fetched_at": time.time()}, f, indent=2)
    h = hashlib.sha256()
    with open(OUT_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    sha = h.hexdigest()

    # Stats
    print()
    print("=== TOTAL FILLS ===")
    print("count: %d" % len(all_fills))
    print("file: %s" % OUT_PATH)
    print("sha256: %s" % sha)
    print()

    if not all_fills:
        print("(no fills returned)")
        return

    # Print one sample fill schema
    print("=== Sample fill (first record, all keys) ===")
    s = all_fills[0]
    for k, v in s.items():
        sv = str(v)
        if len(sv) > 80:
            sv = sv[:80] + "..."
        print("  %-25s = %s" % (k, sv))
    print()

    # Date range
    times = []
    for f_ in all_fills:
        ts = f_.get("created_time") or f_.get("created_ts") or f_.get("ts")
        if ts:
            times.append(ts)
    if times:
        times_sorted = sorted([str(t) for t in times])
        print("=== Date range (created_time) ===")
        print("oldest: %s" % times_sorted[0])
        print("newest: %s" % times_sorted[-1])
    print()

    # Per-day breakdown
    from collections import Counter, defaultdict
    by_day = Counter()
    for f_ in all_fills:
        ts = f_.get("created_time", "")
        if ts and len(ts) >= 10:
            by_day[ts[:10]] += 1
    print("=== Per-day breakdown ===")
    for d in sorted(by_day.keys()):
        print("  %s: %d" % (d, by_day[d]))
    print()

    # Breakdown by side / action / yes-or-no
    side_counts = Counter()
    action_counts = Counter()
    is_taker_counts = Counter()
    side_action = Counter()
    for f_ in all_fills:
        side = f_.get("side", "?")
        action = f_.get("action", "?")
        is_taker = f_.get("is_taker", "?")
        side_counts[side] += 1
        action_counts[action] += 1
        is_taker_counts[is_taker] += 1
        side_action[(action, side)] += 1
    print("=== Breakdown by side ===")
    for s_, n in sorted(side_counts.items()):
        print("  side=%s: %d" % (s_, n))
    print("=== Breakdown by action ===")
    for a, n in sorted(action_counts.items()):
        print("  action=%s: %d" % (a, n))
    print("=== Breakdown by is_taker ===")
    for it, n in sorted(is_taker_counts.items(), key=lambda x: str(x[0])):
        print("  is_taker=%s: %d" % (it, n))
    print("=== Breakdown by (action, side) ===")
    for k, n in sorted(side_action.items()):
        print("  %s: %d" % (k, n))


if __name__ == "__main__":
    asyncio.run(fetch_all())
