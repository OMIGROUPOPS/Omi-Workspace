#!/usr/bin/env python3
"""Full portfolio accounting — balance, positions, settlements, fills, orders."""
import asyncio, aiohttp, sys, json, time
sys.path.insert(0, "/root/Omi-Workspace/arb-executor")
from ncaamb_stb import api_get, RateLimiter

API_KEY_ID = ""
PRIVATE_KEY = ""
with open("/root/Omi-Workspace/arb-executor/.env") as f:
    for line in f:
        line = line.strip()
        if line.startswith("KALSHI_API_KEY="):
            API_KEY_ID = line.split("=", 1)[1]
        elif line.startswith("KALSHI_PRIVATE_KEY_PATH="):
            key_path = line.split("=", 1)[1]
            with open(key_path) as kf:
                PRIVATE_KEY = kf.read()

rl = RateLimiter(8)

async def main():
    async with aiohttp.ClientSession() as session:
        # 1. Balance
        print("=" * 60)
        print("1. BALANCE")
        print("=" * 60)
        bal = await api_get(session, API_KEY_ID, PRIVATE_KEY,
                           "/trade-api/v2/portfolio/balance", rl)
        if bal:
            print(json.dumps(bal, indent=2))

        # 2. Open positions
        print()
        print("=" * 60)
        print("2. OPEN POSITIONS")
        print("=" * 60)
        pos = await api_get(session, API_KEY_ID, PRIVATE_KEY,
                           "/trade-api/v2/portfolio/positions?count_filter=position&limit=200", rl)
        if pos:
            open_pos = [p for p in pos.get("market_positions", [])
                       if p.get("position", 0) > 0]
            if open_pos:
                for p in open_pos:
                    t = p.get("ticker", "?")
                    ct = p.get("position", 0)
                    avg = p.get("market_average_price", "?")
                    print("  %s: %dct avg=%sc" % (t, ct, avg))
            else:
                print("  No open positions")

        # 3. Settlements
        print()
        print("=" * 60)
        print("3. SETTLEMENTS (last 30)")
        print("=" * 60)
        stl = await api_get(session, API_KEY_ID, PRIVATE_KEY,
                           "/trade-api/v2/portfolio/settlements?limit=30", rl)
        if stl:
            settlements = stl.get("settlements", [])
            if settlements:
                for s in settlements:
                    ticker = s.get("ticker", "?")
                    revenue = s.get("revenue", "?")
                    market_result = s.get("market_result", "?")
                    ts = str(s.get("settled_time", s.get("created_time", "?")))[:19]
                    count = s.get("count", s.get("position", "?"))
                    print("  %s | %s | result=%s ct=%s revenue=%s" %
                          (ts, ticker, market_result, count, revenue))
            else:
                print("  No settlements in response")
                print("  Keys: %s" % list(stl.keys()))
                raw = json.dumps(stl, indent=2)
                print("  Raw (first 800 chars): %s" % raw[:800])
        else:
            print("  API returned None")

        # 4. Fills (last 50)
        print()
        print("=" * 60)
        print("4. FILLS (last 50)")
        print("=" * 60)
        fills = await api_get(session, API_KEY_ID, PRIVATE_KEY,
                             "/trade-api/v2/portfolio/fills?limit=50", rl)
        if fills:
            fill_list = fills.get("fills", [])
            if fill_list:
                for f in fill_list:
                    ticker = f.get("ticker", "?")
                    action = f.get("action", "?")
                    side = f.get("side", "?")
                    count = f.get("count", 0)
                    # Handle both old (cents) and new (dollars) price fields
                    price = f.get("yes_price", "?")
                    price_d = f.get("yes_price_dollars", None)
                    if price_d:
                        price = price_d
                    ts = str(f.get("created_time", "?"))[:19]
                    is_taker = f.get("is_taker", "?")
                    oid = str(f.get("order_id", "?"))[:12]
                    print("  %s | %4s %3s %3dct @%s | taker=%s | %s" %
                          (ts, action, side, count, price, is_taker, ticker))
            else:
                print("  No fills in response")
                print("  Keys: %s" % list(fills.keys()))
                raw = json.dumps(fills, indent=2)
                print("  Raw (first 800 chars): %s" % raw[:800])
        else:
            print("  API returned None")

        # 5. Resting orders
        print()
        print("=" * 60)
        print("5. RESTING ORDERS")
        print("=" * 60)
        orders = await api_get(session, API_KEY_ID, PRIVATE_KEY,
                              "/trade-api/v2/portfolio/orders?status=resting", rl)
        if orders:
            resting = [o for o in orders.get("orders", [])
                      if o.get("status") == "resting"]
            if resting:
                for o in resting:
                    t = o.get("ticker", "?")
                    act = o.get("action", "?")
                    s = o.get("side", "?")
                    ct = o.get("remaining_count", o.get("count", "?"))
                    p = o.get("yes_price", o.get("yes_price_dollars", "?"))
                    oid = str(o.get("order_id", "?"))[:12]
                    print("  %s %s %s %sct @%sc oid=%s" % (t, act, s, ct, p, oid))
            else:
                print("  No resting orders")
        else:
            print("  API returned None")

asyncio.run(main())
