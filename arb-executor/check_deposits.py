#!/usr/bin/env python3
"""One-shot script: probe Kalshi and PM APIs for deposit/transfer history."""
import asyncio, aiohttp, os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
from arb_executor_v7 import KalshiAPI, PolymarketUSAPI

async def main():
    kalshi_key = "f3b064d1-a02e-42a4-b2b1-132834694d23"
    with open(os.path.join(os.path.dirname(__file__), 'kalshi.pem')) as f:
        kalshi_pk = f.read()
    kalshi_api = KalshiAPI(kalshi_key, kalshi_pk)

    pm_key = os.getenv("PM_US_API_KEY")
    pm_secret = os.getenv("PM_US_SECRET_KEY") or os.getenv("PM_US_SECRET")
    pm_api = PolymarketUSAPI(pm_key, pm_secret)

    async with aiohttp.ClientSession() as session:
        print("=== KALSHI ENDPOINTS ===")
        for endpoint in [
            "/trade-api/v2/portfolio/balance",
            "/trade-api/v2/wallet",
            "/trade-api/v2/wallet/balance",
            "/trade-api/v2/portfolio/history?limit=10",
        ]:
            try:
                async with session.get(
                    f"{kalshi_api.BASE_URL}{endpoint}",
                    headers=kalshi_api._headers("GET", endpoint),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    print(f"  {endpoint}: {r.status}")
                    if r.status == 200:
                        text = await r.text()
                        print(f"    {text[:500]}")
            except Exception as e:
                print(f"  {endpoint}: ERROR {e}")

        print("\n=== PM ENDPOINTS ===")
        for endpoint in [
            "/v1/account/balances",
            "/v1/account",
            "/v1/wallet/balance",
        ]:
            try:
                async with session.get(
                    f"{pm_api.BASE_URL}{endpoint}",
                    headers=pm_api._headers("GET", endpoint),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    print(f"  {endpoint}: {r.status}")
                    if r.status == 200:
                        text = await r.text()
                        print(f"    {text[:500]}")
            except Exception as e:
                print(f"  {endpoint}: ERROR {e}")

asyncio.run(main())
