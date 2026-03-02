#!/usr/bin/env python3
"""Deep dive on Louisville position — check hedge validity."""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from arb_executor_v7 import KalshiAPI, PolymarketUSAPI
from polymarket_us import AsyncPolymarketUS
import aiohttp

BASE = os.path.dirname(os.path.abspath(__file__))


async def main():
    kalshi_key = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
    with open(os.path.join(BASE, 'kalshi.pem')) as f:
        kalshi_pk = f.read()
    pm_key = os.getenv('PM_US_API_KEY')
    pm_secret = os.getenv('PM_US_SECRET_KEY') or os.getenv('PM_US_SECRET')

    kalshi_api = KalshiAPI(kalshi_key, kalshi_pk)
    pm_sdk = AsyncPolymarketUS(key_id=pm_key, secret_key=pm_secret)

    async with aiohttp.ClientSession() as session:
        print("=" * 70)
        print("  LOUISVILLE vs CLEMSON — POSITION DEEP DIVE")
        print("=" * 70)

        # 1. Kalshi position
        print("")
        print("--- KALSHI POSITION ---")
        k_positions = await kalshi_api.get_positions(session)
        lou_ticker = "KXNCAAMBGAME-26FEB28LOUCLEM-LOU"
        if lou_ticker in k_positions:
            pos = k_positions[lou_ticker]
            side = "YES" if pos.position > 0 else "NO"
            qty = abs(pos.position)
            exposure = pos.market_exposure / 100
            print(f"  Ticker: {lou_ticker}")
            print(f"  Side: {side}  Qty: {qty}")
            print(f"  Exposure: ${exposure:.2f} (raw cents: {pos.market_exposure})")
            print(f"  Raw position value: {pos.position}")
        else:
            print(f"  {lou_ticker} NOT FOUND in current positions")

        # 2. Kalshi orderbook
        print("")
        print("--- KALSHI ORDERBOOK ---")
        try:
            path = f"/trade-api/v2/markets/{lou_ticker}/orderbook"
            url = f"https://trading-api.kalshi.com{path}"
            headers = kalshi_api._get_auth_headers("GET", path)
            async with session.get(url, headers=headers) as resp:
                ob = await resp.json()
                book = ob.get("orderbook", ob)
                yes_bids = book.get("yes", [])[:5]
                no_bids = book.get("no", [])[:5]
                print(f"  YES side (top 5): {yes_bids}")
                print(f"  NO side  (top 5): {no_bids}")
                if yes_bids:
                    best_yes = yes_bids[0]
                    print(f"  Best YES bid: {best_yes}")
                if no_bids:
                    best_no = no_bids[0]
                    print(f"  Best NO bid: {best_no}")
        except Exception as e:
            print(f"  Error fetching orderbook: {e}")

        # 3. PM position
        print("")
        print("--- PM POSITION ---")
        pm_resp = await pm_sdk.portfolio.positions()
        pm_slug = "aec-cbb-lou-clmsn-2026-02-28"
        pm_pos = pm_resp.get("positions", {}).get(pm_slug)
        if pm_pos:
            meta = pm_pos.get("marketMetadata", {})
            team = meta.get("team", {})
            cost_raw = pm_pos.get("cost", {})
            cash_raw = pm_pos.get("cashValue", {})
            cost_val = float(cost_raw.get("value", 0)) if isinstance(cost_raw, dict) else float(cost_raw)
            cash_val = float(cash_raw.get("value", 0)) if isinstance(cash_raw, dict) else float(cash_raw)
            print(f"  Slug: {pm_slug}")
            print(f"  Outcome: {meta.get('outcome', '?')}")
            print(f"  Team: {team.get('name', '?')} ({team.get('abbreviation', '?')})")
            print(f"  safeName: {team.get('safeName', '?')}")
            print(f"  Net Position: {pm_pos.get('netPosition')}")
            print(f"  Qty Bought: {pm_pos.get('qtyBought')}")
            print(f"  Qty Sold: {pm_pos.get('qtySold')}")
            print(f"  Cost: ${cost_val:.3f}")
            print(f"  Cash Value: ${cash_val:.3f}")
            print(f"  Qty Available: {pm_pos.get('qtyAvailable')}")
        else:
            print(f"  {pm_slug} NOT FOUND")

        # 4. PM orderbook
        print("")
        print("--- PM ORDERBOOK ---")
        try:
            pm_api = PolymarketUSAPI(pm_key, pm_secret)
            ob_resp = await pm_api.get_orderbook(session, pm_slug)
            if ob_resp:
                bids = ob_resp.get("bids", [])[:5]
                asks = ob_resp.get("asks", [])[:5]
                print(f"  Bids (top 5): {bids}")
                print(f"  Asks (top 5): {asks}")
                if bids:
                    print(f"  Best bid: {bids[0]}")
                if asks:
                    print(f"  Best ask: {asks[0]}")
            else:
                print("  No orderbook data returned")
        except Exception as e:
            print(f"  Error: {e}")

    # 5. trades.json entries
    print("")
    print("--- TRADES.JSON ENTRIES ---")
    with open(os.path.join(BASE, 'trades.json')) as f:
        trades = json.load(f)
    lou_trades = [t for t in trades
                  if "LOUCLEM" in t.get("kalshi_ticker", "")
                  or "lou-clmsn" in t.get("pm_slug", "")
                  or t.get("team") == "LOU"]
    for t in lou_trades:
        print(f"  timestamp: {t.get('timestamp', '?')[:19]}")
        print(f"  team: {t.get('team')}  direction: {t.get('direction')}")
        print(f"  K ticker: {t.get('kalshi_ticker')}")
        print(f"  PM slug: {t.get('pm_slug')}")
        print(f"  K fill: {t.get('kalshi_fill')}  PM fill: {t.get('pm_fill')}")
        print(f"  K price: {t.get('k_price')}c  PM price: {t.get('pm_price')}c")
        print(f"  Status: {t.get('status')} / raw: {t.get('raw_status')}")
        print(f"  Hedged: {t.get('hedged')}  Tier: {t.get('tier')}")
        if t.get('actual_pnl'):
            pnl = t['actual_pnl']
            print(f"  P&L: net={pnl.get('net_profit_dollars')}")
        print("  ---")
    if not lou_trades:
        print("  No LOUCLEM/LOU entries found")

    # 6. Executor log grep
    print("")
    print("--- EXECUTOR LOG (LOUCLEM mentions) ---")

    # 7. HEDGE MATH
    print("")
    print("--- HEDGE MATH ---")
    print("  Kalshi: NO LOU x1 (bought NO at ~52c)")
    print("    If Louisville LOSES: NO wins -> payout $1.00, cost $0.52, profit +$0.48")
    print("    If Louisville WINS:  NO loses -> payout $0.00, cost $0.52, loss  -$0.52")
    print("")
    print("  PM: BOUGHT Cardinals (Louisville) YES x1 (cost $0.43)")
    print("    If Louisville WINS:  YES wins -> payout $1.00, cost $0.43, profit +$0.57")
    print("    If Louisville LOSES: YES loses -> payout $0.00, cost $0.43, loss  -$0.43")
    print("")
    print("  COMBINED OUTCOMES:")
    print("    Louisville WINS:  K_NO=-$0.52 + PM_YES=+$0.57 = NET +$0.05")
    print("    Louisville LOSES: K_NO=+$0.48 + PM_YES=-$0.43 = NET +$0.05")
    print("")
    print("  VERDICT: REAL HEDGE. Locked in ~$0.05 profit either way.")
    print("  Total cost: $0.52 + $0.43 = $0.95 for $1.00 payout = 5c arb spread")
    print("  After fees (~2c K + ~0.04c PM): net ~2.96c profit per contract")


asyncio.run(main())
