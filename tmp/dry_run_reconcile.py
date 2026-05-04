#!/usr/bin/env python3
"""Dry-run reconcile: read all positions using _read_position, check resting sells."""
import sys, asyncio, aiohttp, json
sys.path.insert(0, "/root/Omi-Workspace/arb-executor")
from ncaamb_stb import load_credentials, api_get, RateLimiter

api_key, private_key = load_credentials()
rl = RateLimiter(8)

def _read_position(p):
    fp = p.get("position_fp", None)
    if fp is not None:
        try:
            return int(float(fp))
        except (ValueError, TypeError):
            pass
    return p.get("position", 0)

async def main():
    async with aiohttp.ClientSession() as session:
        # 1. Read all positions
        print("=" * 60)
        print("POSITIONS (using _read_position)")
        print("=" * 60)
        pos = await api_get(session, api_key, private_key,
                           "/trade-api/v2/portfolio/positions?count_filter=position&limit=200", rl)
        open_positions = {}
        if pos:
            for p in pos.get("market_positions", []):
                ct = _read_position(p)
                old_ct = p.get("position", 0)
                ticker = p.get("ticker", "?")
                fp_val = p.get("position_fp", "MISSING")
                if ct > 0:
                    open_positions[ticker] = ct
                    print("  %s: %d ct (position_fp=%s, old position=%d)" % (ticker, ct, fp_val, old_ct))
            print("\n  TOTAL open positions: %d" % len(open_positions))
        else:
            print("  API returned None")

        # 2. Read resting orders
        print()
        print("=" * 60)
        print("RESTING SELLS")
        print("=" * 60)
        orders = await api_get(session, api_key, private_key,
                              "/trade-api/v2/portfolio/orders?status=resting", rl)
        resting_sells = {}
        if orders:
            for o in orders.get("orders", []):
                if o.get("status") == "resting" and o.get("action") == "sell":
                    t = o.get("ticker", "?")
                    ct = o.get("remaining_count", o.get("count", 0))
                    ct_fp = o.get("remaining_count_fp", o.get("count_fp", "?"))
                    p = o.get("yes_price_dollars", o.get("yes_price", "?"))
                    oid = str(o.get("order_id", "?"))[:12]
                    resting_sells[t] = int(float(ct_fp)) if ct_fp != "?" else ct
                    print("  %s: sell %s/%sct @%s oid=%s" % (t, ct, ct_fp, p, oid))
        print("\n  TOTAL resting sells: %d" % len(resting_sells))

        # 3. Cross-check
        print()
        print("=" * 60)
        print("CROSS-CHECK: positions vs resting sells")
        print("=" * 60)
        all_ok = True
        for ticker, ct in open_positions.items():
            sell_ct = resting_sells.get(ticker, 0)
            if sell_ct >= ct:
                print("  OK   %s: %dct position, %dct resting sell" % (ticker, ct, sell_ct))
            else:
                print("  MISS %s: %dct position, %dct resting sell — NEEDS SELL" % (ticker, ct, sell_ct))
                all_ok = False

        for ticker in resting_sells:
            if ticker not in open_positions:
                print("  ORPHAN SELL %s: no position but resting sell exists" % ticker)

        if all_ok and open_positions:
            print("\n  ALL POSITIONS COVERED BY RESTING SELLS")
        elif not open_positions:
            print("\n  NO OPEN POSITIONS FOUND")
        else:
            print("\n  WARNING: SOME POSITIONS MISSING RESTING SELLS")

asyncio.run(main())
