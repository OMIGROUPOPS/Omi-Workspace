#!/usr/bin/env python3
"""Emergency Louisville position check — direct API calls."""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from arb_executor_v7 import KalshiAPI, PolymarketUSAPI
from polymarket_us import AsyncPolymarketUS
import aiohttp

BASE = os.path.dirname(os.path.abspath(__file__))
LOU_TICKER = "KXNCAAMBGAME-26FEB28LOUCLEM-LOU"
LOU_EVENT = "KXNCAAMBGAME-26FEB28LOUCLEM"
PM_SLUG = "aec-cbb-lou-clmsn-2026-02-28"


async def main():
    kalshi_key = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
    with open(os.path.join(BASE, 'kalshi.pem')) as f:
        kalshi_pk = f.read()
    pm_key = os.getenv('PM_US_API_KEY')
    pm_secret = os.getenv('PM_US_SECRET_KEY') or os.getenv('PM_US_SECRET')

    kalshi_api = KalshiAPI(kalshi_key, kalshi_pk)
    pm_sdk = AsyncPolymarketUS(key_id=pm_key, secret_key=pm_secret)
    pm_api = PolymarketUSAPI(pm_key, pm_secret)

    now = datetime.now(timezone.utc)
    print("=" * 70)
    print("  LOUISVILLE EMERGENCY CHECK")
    print(f"  Time: {now.isoformat()}")
    print("=" * 70)

    async with aiohttp.ClientSession() as session:

        # ══════════════════════════════════════════════════════════════
        # 1. KALSHI — DIRECT POSITION CHECK
        # ══════════════════════════════════════════════════════════════
        print("\n[1] KALSHI POSITION (direct API)")
        print("-" * 50)
        k_positions = await kalshi_api.get_positions(session)
        if k_positions and LOU_TICKER in k_positions:
            pos = k_positions[LOU_TICKER]
            side = "YES" if pos.position > 0 else "NO"
            qty = abs(pos.position)
            print(f"  STATUS: POSITION EXISTS")
            print(f"  Ticker: {LOU_TICKER}")
            print(f"  Side: {side}  Qty: {qty}")
            print(f"  Exposure: ${pos.market_exposure / 100:.2f}")
            print(f"  Raw position: {pos.position}")
        else:
            print(f"  STATUS: NO POSITION FOUND")
            print(f"  {LOU_TICKER} is NOT in current portfolio")
            print(f"  (Settled, closed, or never existed)")

        # ══════════════════════════════════════════════════════════════
        # 2. KALSHI — MARKET STATUS & SETTLEMENT
        # ══════════════════════════════════════════════════════════════
        print("\n[2] KALSHI MARKET STATUS")
        print("-" * 50)
        try:
            # Get market details
            path = f"/trade-api/v2/markets/{LOU_TICKER}"
            url = f"https://trading-api.kalshi.com{path}"
            ts_str = str(int(now.timestamp() * 1000))
            # Use the same signing as the API class
            import time
            import base64
            from cryptography.hazmat.primitives.asymmetric import padding, utils as crypto_utils
            from cryptography.hazmat.primitives import hashes, serialization

            private_key = serialization.load_pem_private_key(kalshi_pk.encode(), password=None)
            timestamp = str(int(time.time() * 1000))
            msg = timestamp + "GET" + path
            signature = private_key.sign(
                msg.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            sig_b64 = base64.b64encode(signature).decode()
            headers = {
                "KALSHI-ACCESS-KEY": kalshi_key,
                "KALSHI-ACCESS-SIGNATURE": sig_b64,
                "KALSHI-ACCESS-TIMESTAMP": timestamp,
                "Content-Type": "application/json",
            }
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                market = data.get("market", data)
                print(f"  Title: {market.get('title', '?')}")
                print(f"  Subtitle: {market.get('subtitle', '?')}")
                print(f"  Status: {market.get('status', '?')}")
                print(f"  Result: {market.get('result', 'NOT SETTLED')}")
                print(f"  Close time: {market.get('close_time', '?')}")
                print(f"  Expiration: {market.get('expiration_time', '?')}")
                print(f"  Settlement time: {market.get('settlement_time', market.get('expected_expiration_time', '?'))}")
                print(f"  Yes bid: {market.get('yes_bid', '?')}  Yes ask: {market.get('yes_ask', '?')}")
                print(f"  No bid: {market.get('no_bid', '?')}  No ask: {market.get('no_ask', '?')}")
                print(f"  Last price: {market.get('last_price', '?')}")
                print(f"  Volume: {market.get('volume', '?')}")
                print(f"  Open interest: {market.get('open_interest', '?')}")

                # Game time detection
                close_time = market.get('close_time', '')
                exp_time = market.get('expiration_time', '')
                if close_time:
                    try:
                        ct = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
                        if ct < now:
                            print(f"  >>> MARKET CLOSED (closed {(now - ct).total_seconds() / 60:.0f} min ago)")
                        else:
                            print(f"  >>> MARKET OPEN (closes in {(ct - now).total_seconds() / 60:.0f} min)")
                    except Exception:
                        pass

                status = market.get('status', '')
                result = market.get('result', '')
                if result and result != '':
                    print(f"  >>> SETTLED: result = {result}")
                if status == 'settled':
                    print(f"  >>> GAME IS SETTLED")
                elif status == 'closed':
                    print(f"  >>> MARKET IS CLOSED (awaiting settlement)")
                elif status == 'active':
                    print(f"  >>> MARKET IS ACTIVE/OPEN")
        except Exception as e:
            print(f"  Error fetching market: {type(e).__name__}: {e}")

        # ══════════════════════════════════════════════════════════════
        # 3. KALSHI — ORDER HISTORY
        # ══════════════════════════════════════════════════════════════
        print("\n[3] KALSHI ORDER HISTORY")
        print("-" * 50)
        try:
            path = "/trade-api/v2/portfolio/orders?ticker=" + LOU_TICKER + "&limit=50"
            url = "https://trading-api.kalshi.com" + path
            timestamp = str(int(time.time() * 1000))
            msg = timestamp + "GET" + path
            signature = private_key.sign(msg.encode(), padding.PKCS1v15(), hashes.SHA256())
            sig_b64 = base64.b64encode(signature).decode()
            headers = {
                "KALSHI-ACCESS-KEY": kalshi_key,
                "KALSHI-ACCESS-SIGNATURE": sig_b64,
                "KALSHI-ACCESS-TIMESTAMP": timestamp,
                "Content-Type": "application/json",
            }
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                orders = data.get("orders", [])
                print(f"  Total orders found: {len(orders)}")
                for o in orders:
                    print(f"  ---")
                    print(f"  Order ID: {o.get('order_id', '?')[:16]}...")
                    print(f"  Created: {o.get('created_time', '?')}")
                    print(f"  Side: {o.get('side', '?')}  Action: {o.get('action', '?')}")
                    print(f"  Type: {o.get('type', '?')}  TIF: {o.get('time_in_force', '?')}")
                    print(f"  Price: {o.get('yes_price', o.get('no_price', '?'))}c")
                    print(f"  Qty: {o.get('count', '?')}  Remaining: {o.get('remaining_count', '?')}")
                    print(f"  Status: {o.get('status', '?')}")
                    print(f"  Filled qty: {o.get('count', 0) - o.get('remaining_count', 0)}")
                if not orders:
                    print("  No orders found for this ticker")
        except Exception as e:
            print(f"  Error fetching orders: {type(e).__name__}: {e}")

        # Also check fills/trades
        print("\n[3b] KALSHI FILLS/TRADES")
        print("-" * 50)
        try:
            path = "/trade-api/v2/portfolio/fills?ticker=" + LOU_TICKER + "&limit=50"
            url = "https://trading-api.kalshi.com" + path
            timestamp = str(int(time.time() * 1000))
            msg = timestamp + "GET" + path
            signature = private_key.sign(msg.encode(), padding.PKCS1v15(), hashes.SHA256())
            sig_b64 = base64.b64encode(signature).decode()
            headers = {
                "KALSHI-ACCESS-KEY": kalshi_key,
                "KALSHI-ACCESS-SIGNATURE": sig_b64,
                "KALSHI-ACCESS-TIMESTAMP": timestamp,
                "Content-Type": "application/json",
            }
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                fills = data.get("fills", [])
                print(f"  Total fills: {len(fills)}")
                for fl in fills:
                    print(f"  ---")
                    print(f"  Fill ID: {fl.get('trade_id', '?')[:16]}...")
                    print(f"  Created: {fl.get('created_time', '?')}")
                    print(f"  Side: {fl.get('side', '?')}  Action: {fl.get('action', '?')}")
                    print(f"  Price: {fl.get('yes_price', fl.get('no_price', '?'))}c")
                    print(f"  Count: {fl.get('count', '?')}")
                    print(f"  Is taker: {fl.get('is_taker', '?')}")
                if not fills:
                    print("  No fills found")
        except Exception as e:
            print(f"  Error fetching fills: {type(e).__name__}: {e}")

        # ══════════════════════════════════════════════════════════════
        # 4. PM POSITION — CURRENT
        # ══════════════════════════════════════════════════════════════
        print("\n[4] PM POSITION (live)")
        print("-" * 50)
        pm_resp = await pm_sdk.portfolio.positions()
        pm_pos = pm_resp.get("positions", {}).get(PM_SLUG)
        if pm_pos:
            meta = pm_pos.get("marketMetadata", {})
            team = meta.get("team", {})
            cost_raw = pm_pos.get("cost", {})
            cash_raw = pm_pos.get("cashValue", {})
            cost_val = float(cost_raw.get("value", 0)) if isinstance(cost_raw, dict) else float(cost_raw)
            cash_val = float(cash_raw.get("value", 0)) if isinstance(cash_raw, dict) else float(cash_raw)
            net = pm_pos.get('netPosition', '0')
            print(f"  STATUS: POSITION OPEN")
            print(f"  Outcome: {meta.get('outcome', '?')} ({team.get('safeName', '?')})")
            print(f"  Net Position: {net}")
            print(f"  Qty Bought: {pm_pos.get('qtyBought')}")
            print(f"  Qty Sold: {pm_pos.get('qtySold')}")
            print(f"  Entry Cost: ${cost_val:.3f}")
            print(f"  Current Cash Value: ${cash_val:.3f}")
            print(f"  Unrealized P&L: ${cash_val - cost_val:+.3f}")
            print(f"  Qty Available: {pm_pos.get('qtyAvailable')}")
        else:
            print(f"  STATUS: NO PM POSITION")
            print(f"  {PM_SLUG} not found (settled or closed)")

        # PM orderbook for current market price
        print("\n[4b] PM CURRENT MARKET")
        print("-" * 50)
        try:
            ob_resp = await pm_api.get_orderbook(session, PM_SLUG)
            if ob_resp:
                bids = ob_resp.get("bids", [])[:3]
                asks = ob_resp.get("asks", [])[:3]
                best_bid = bids[0]['price'] if bids else 0
                best_ask = asks[0]['price'] if asks else 0
                mid = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
                print(f"  Best bid: {best_bid} ({bids[0]['size']} qty)" if bids else "  No bids")
                print(f"  Best ask: {best_ask} ({asks[0]['size']} qty)" if asks else "  No asks")
                print(f"  Mid: {mid:.2f}")
                if pm_pos:
                    cost_val_cents = cost_val * 100
                    print(f"  Entry: {cost_val_cents:.0f}c  Current mid: {mid*100:.0f}c")
                    if mid > 0:
                        print(f"  Mark-to-market loss: {(mid - cost_val):.3f} per contract")
                        print(f"  If you sell now at bid ({best_bid}): get ${best_bid:.3f}, loss ${best_bid - cost_val:+.3f}")
        except Exception as e:
            print(f"  Error: {e}")

        # ══════════════════════════════════════════════════════════════
        # 5. PM — SETTLEMENT CHECK
        # ══════════════════════════════════════════════════════════════
        print("\n[5] PM SETTLEMENT CHECK")
        print("-" * 50)
        try:
            settlement = await pm_sdk.markets.settlement(PM_SLUG)
            print(f"  Settlement response: {json.dumps(settlement)}")
        except Exception as e:
            print(f"  Not settled yet: {type(e).__name__}: {e}")

        # ══════════════════════════════════════════════════════════════
        # 6. DECISION FRAMEWORK
        # ══════════════════════════════════════════════════════════════
        print("\n" + "=" * 70)
        print("  DECISION FRAMEWORK")
        print("=" * 70)
        k_exists = k_positions and LOU_TICKER in k_positions
        pm_exists = pm_pos is not None
        print(f"  Kalshi position exists: {k_exists}")
        print(f"  PM position exists: {pm_exists}")

        if k_exists and pm_exists:
            print("  >>> BOTH LEGS OPEN — hedge intact, hold both to settlement")
        elif not k_exists and pm_exists:
            print("  >>> K LEG GONE, PM STILL OPEN — NAKED PM POSITION")
            print("  >>> Options:")
            print("     1. HOLD: If you think Louisville wins, hold PM YES")
            print("     2. EXIT: Sell PM YES at current bid to cut exposure")
            print(f"     3. If K settled YES (Louisville won): K NO lost, PM YES won -> net profitable")
            print(f"     4. If K settled NO (Louisville lost): K NO won, PM YES lost -> net profitable")
            print(f"     5. If K position just closed with no settlement -> CHECK settlement result")
        elif k_exists and not pm_exists:
            print("  >>> PM LEG GONE, K STILL OPEN — NAKED K POSITION")
        else:
            print("  >>> BOTH POSITIONS GONE — fully settled or exited")


asyncio.run(main())
