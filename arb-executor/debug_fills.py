#!/usr/bin/env python3
"""Debug: show raw fills for tickers with entry=? in the audit."""
import asyncio
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from arb_executor_v7 import KalshiAPI
import aiohttp

BASE = os.path.dirname(os.path.abspath(__file__))

# Tickers that showed entry=? in the audit
MISSING_TICKERS = [
    "KXNCAAMBGAME-26FEB28CITWOF-CIT",
    "KXNCAAMBGAME-26FEB28GTWNXAV-GTWN",
    "KXNCAAMBGAME-26FEB28LOUCLEM-LOU",
    "KXNCAAMBGAME-26FEB28PEAYBELL-PEAY",
    "KXNCAAMBGAME-26FEB28RADLONG-LONG",
    "KXNCAAMBGAME-26FEB28SFPACCSU-SFPA",
    "KXUFCFIGHT-26FEB28MORKAV-MOR",
]


async def main():
    kalshi_key = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
    with open(os.path.join(BASE, 'kalshi.pem')) as f:
        kalshi_pk = f.read()

    kalshi_api = KalshiAPI(kalshi_key, kalshi_pk)

    async with aiohttp.ClientSession() as session:
        # Fetch ALL fills
        all_fills = []
        cursor = None
        page = 0
        while True:
            path = '/trade-api/v2/portfolio/fills?limit=100'
            if cursor:
                path += f'&cursor={cursor}'
            async with session.get(
                f'{kalshi_api.BASE_URL}{path}',
                headers=kalshi_api._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status != 200:
                    text = await r.text()
                    print(f"Fills API error {r.status}: {text[:200]}")
                    break
                data = await r.json()
            fills = data.get('fills', [])
            if not fills:
                break
            all_fills.extend(fills)
            cursor = data.get('cursor', None)
            page += 1
            if not cursor or page > 20:
                break

        print(f"Total fills fetched: {len(all_fills)}")

        # Group by ticker
        fills_by_ticker = defaultdict(list)
        for f in all_fills:
            fills_by_ticker[f.get('ticker', '')].append(f)

        # Check each missing ticker
        print("\n=== MISSING TICKERS ===")
        for ticker in MISSING_TICKERS:
            fills = fills_by_ticker.get(ticker, [])
            print(f"\n{ticker}:")
            if fills:
                for f in fills:
                    print(f"  side={f.get('side')} action={f.get('action')} count={f.get('count')} yes_price={f.get('yes_price')} no_price={f.get('no_price', '?')} created={f.get('created_time', '?')[:19]}")
            else:
                print("  NO FILLS FOUND")
                # Check for partial match
                game = ticker.split('-')[0]  # e.g., KXNCAAMBGAME
                event = '-'.join(ticker.split('-')[:2])  # e.g., KXNCAAMBGAME-26FEB28LOUCLEM
                partial_matches = [t for t in fills_by_ticker.keys() if event in t or ticker[:30] in t]
                if partial_matches:
                    print(f"  Partial matches: {partial_matches}")
                    for pm_t in partial_matches:
                        for f in fills_by_ticker[pm_t]:
                            print(f"    {pm_t}: side={f.get('side')} action={f.get('action')} count={f.get('count')} yes_price={f.get('yes_price')}")

        # Also show first fill as format example
        if all_fills:
            print("\n=== SAMPLE FILL (for format reference) ===")
            print(json.dumps(all_fills[0], indent=2))

        # Check: do NO-side fills have the ticker with the team that bought NO?
        # Or do they have the opposite team's ticker?
        print("\n=== FILLS FOR LOUCLEM EVENT (any team suffix) ===")
        for ticker, fills in fills_by_ticker.items():
            if "LOUCLEM" in ticker:
                print(f"\n{ticker}:")
                for f in fills:
                    print(f"  side={f.get('side')} action={f.get('action')} count={f.get('count')} yes_price={f.get('yes_price')}")

        print("\n=== FILLS FOR MORKAV EVENT ===")
        for ticker, fills in fills_by_ticker.items():
            if "MORKAV" in ticker:
                print(f"\n{ticker}:")
                for f in fills:
                    print(f"  side={f.get('side')} action={f.get('action')} count={f.get('count')} yes_price={f.get('yes_price')}")

        print("\n=== FILLS FOR PEAYBELL EVENT ===")
        for ticker, fills in fills_by_ticker.items():
            if "PEAYBELL" in ticker:
                print(f"\n{ticker}:")
                for f in fills:
                    print(f"  side={f.get('side')} action={f.get('action')} count={f.get('count')} yes_price={f.get('yes_price')}")

asyncio.run(main())
