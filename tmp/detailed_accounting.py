#!/usr/bin/env python3
"""Detailed portfolio accounting with all fields."""
import sys, asyncio, aiohttp, json
sys.path.insert(0, "/root/Omi-Workspace/arb-executor")
from ncaamb_stb import load_credentials, api_get, RateLimiter

api_key, private_key = load_credentials()
rl = RateLimiter(8)

async def main():
    async with aiohttp.ClientSession() as session:
        # Settlements
        print("=" * 80)
        print("SETTLEMENTS (last 30)")
        print("=" * 80)
        stl = await api_get(session, api_key, private_key,
                           "/trade-api/v2/portfolio/settlements?limit=30", rl)
        if stl:
            for s in stl.get("settlements", []):
                et = s.get("event_ticker", "?")
                short_et = et[-20:] if len(et) > 20 else et
                res = s.get("market_result", "?")
                rev = s.get("revenue", 0)
                fee = s.get("fee_cost", "0")
                no_ct = s.get("no_count_fp", "0")
                no_cost = s.get("no_total_cost_dollars", "0")
                yes_ct = s.get("yes_count_fp", "0")
                yes_cost = s.get("yes_total_cost_dollars", "0")
                ts = str(s.get("settled_time", "?"))[:16]
                ticker = s.get("ticker", s.get("market_ticker", ""))
                short_ticker = ticker[-15:] if ticker else ""
                print("%s | %-20s | res=%-3s | yes=%5sct $%8s | no=%5sct $%8s | rev=$%7s fee=$%s" %
                      (ts, short_et, res, yes_ct, yes_cost, no_ct, no_cost,
                       "%.2f" % (rev/100) if isinstance(rev, (int, float)) else rev, fee))

        # Fills
        print()
        print("=" * 80)
        print("FILLS (last 50)")
        print("=" * 80)
        fills = await api_get(session, api_key, private_key,
                             "/trade-api/v2/portfolio/fills?limit=50", rl)
        if fills:
            for f in fills.get("fills", []):
                t = f.get("ticker", "?")
                short_t = t.split("-")[-1] if "-" in t else t[-10:]
                a = f.get("action", "?")
                s = f.get("side", "?")
                c = f.get("count", 0)
                cfp = f.get("count_fp", "?")
                p_yes = f.get("yes_price_dollars", f.get("yes_price", "?"))
                p_no = f.get("no_price_dollars", f.get("no_price", "?"))
                ts = str(f.get("created_time", "?"))[:19]
                taker = f.get("is_taker", "?")
                oid = str(f.get("order_id", "?"))[:8]
                # Get event from ticker
                parts = t.split("-")
                event = "-".join(parts[:-1]) if len(parts) > 1 else t
                short_event = event[-20:]
                print("%s | %4s %3s %3d/%5sct @y=%s n=%s | tkr=%s | %s | %s" %
                      (ts, a, s, c, cfp, p_yes, p_no, str(taker)[:1], short_t, short_event))

        # Current positions (all, not just open)
        print()
        print("=" * 80)
        print("ALL POSITIONS")
        print("=" * 80)
        pos = await api_get(session, api_key, private_key,
                           "/trade-api/v2/portfolio/positions?limit=200", rl)
        if pos:
            for p in pos.get("market_positions", []):
                t = p.get("ticker", "?")
                position = p.get("position", 0)
                avg = p.get("market_average_price", "?")
                # Show all non-zero
                if position != 0:
                    print("  %s: %dct avg=%s" % (t[-30:], position, avg))
            zero_count = sum(1 for p in pos.get("market_positions", [])
                           if p.get("position", 0) == 0)
            nonzero = sum(1 for p in pos.get("market_positions", [])
                        if p.get("position", 0) != 0)
            print("  (%d with position, %d zero)" % (nonzero, zero_count))

        # Resting orders with counts
        print()
        print("=" * 80)
        print("RESTING ORDERS")
        print("=" * 80)
        orders = await api_get(session, api_key, private_key,
                              "/trade-api/v2/portfolio/orders?status=resting", rl)
        if orders:
            for o in orders.get("orders", []):
                if o.get("status") == "resting":
                    t = o.get("ticker", "?")
                    act = o.get("action", "?")
                    s = o.get("side", "?")
                    ct = o.get("remaining_count", o.get("count", "?"))
                    ct_fp = o.get("remaining_count_fp", o.get("count_fp", "?"))
                    p = o.get("yes_price_dollars", o.get("yes_price", "?"))
                    oid = str(o.get("order_id", "?"))[:12]
                    print("  %s %s %s %s/%sct @%s oid=%s" %
                          (t[-30:], act, s, ct, ct_fp, p, oid))

asyncio.run(main())
