#!/usr/bin/env python3
"""Test PENDING market monitoring and Kalshi matching"""
import asyncio
import aiohttp
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '.')
from arb_executor_v7 import (
    PolymarketUSAPI, KalshiAPI,
    PM_US_API_KEY, PM_US_SECRET_KEY,
    KALSHI_API_KEY, KALSHI_PRIVATE_KEY,
    process_pending_markets, display_pending_markets,
    load_activated_markets, get_activation_stats,
    SLUG_TO_KALSHI, SPORTS_CONFIG, parse_gid
)

async def test_pending():
    pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)
    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)

    print("=" * 70)
    print("TESTING PENDING MARKET MONITORING + KALSHI MATCHING")
    print("=" * 70)

    async with aiohttp.ClientSession() as session:
        # Fetch all PM US markets including pending
        print("\n[1] Fetching ALL PM US markets...")
        all_pm_markets = await pm_api.get_all_markets_including_pending(session, debug=True)

        # Build Kalshi cache (simulating what the main bot does)
        print("\n[2] Fetching Kalshi markets to build cache...")
        kalshi_cache = {}

        for cfg in SPORTS_CONFIG:
            sport = cfg['sport']
            series = cfg['series']

            cursor = None
            while True:
                path = f'/trade-api/v2/markets?series_ticker={series}&status=open&limit=200'
                if cursor:
                    path += f'&cursor={cursor}'

                async with session.get(
                    f'{kalshi_api.BASE_URL}{path}',
                    headers=kalshi_api._headers('GET', path),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        markets = data.get('markets', [])

                        for m in markets:
                            ticker = m.get('ticker', '')
                            parts = ticker.split('-')
                            if len(parts) >= 3:
                                gid = parts[1]
                                team = parts[2]
                                if team == 'TIE':
                                    continue

                                date, t1, t2 = parse_gid(gid)
                                if date and t1 and t2:
                                    # Use same format as main bot: sport:TEAM1-TEAM2:date
                                    sorted_teams = '-'.join(sorted([t1, t2]))
                                    cache_key = f"{sport}:{sorted_teams}:{date}"
                                    kalshi_cache[cache_key] = {
                                        'gid': gid,
                                        'ticker': ticker,
                                        'team': team,
                                    }
                                    # Debug: print first few cache keys
                                    if len(kalshi_cache) <= 5:
                                        print(f"    Sample cache key: {cache_key}")

                        cursor = data.get('cursor')
                        if not cursor or not markets:
                            break
                    else:
                        break

        print(f"    Built Kalshi cache with {len(kalshi_cache)} entries")

        # Process pending markets
        print("\n[3] Processing PENDING markets with Kalshi matching...")
        pending, activated = process_pending_markets(all_pm_markets, kalshi_cache)

        # Check how many pending markets have Kalshi matches
        matches = 0
        no_matches = 0

        print(f"\n[PENDING MARKET KALSHI MATCH ANALYSIS]")
        today = datetime.now().strftime('%Y-%m-%d')

        for p in pending:
            sport = p.get('sport')
            team1 = p.get('team1')
            team2 = p.get('team2')
            game_time = p.get('game_time', '')
            hours = p.get('hours_to_game')

            if not sport or not team1 or not team2:
                continue

            # Build cache key - IMPORTANT: Convert UTC to EST for date
            game_date = None
            if game_time:
                try:
                    dt_utc = datetime.fromisoformat(game_time.replace('Z', '+00:00')).replace(tzinfo=None)
                    dt_est = dt_utc - timedelta(hours=5)  # UTC to EST
                    game_date = dt_est.strftime('%Y-%m-%d')
                except:
                    game_date = game_time[:10]
            else:
                game_date = today

            sorted_teams = '-'.join(sorted([team1, team2]))
            cache_key = f"{sport}:{sorted_teams}:{game_date}"

            if cache_key in kalshi_cache:
                matches += 1
                if hours and hours < 12:  # Only show games within 12 hours
                    k_info = kalshi_cache[cache_key]
                    print(f"  [MATCH] {sport.upper()} {team1} vs {team2} ({hours:.1f}h)")
                    print(f"         PM: {p['slug']}")
                    print(f"         Kalshi: {k_info['ticker']}")
            else:
                no_matches += 1

        print(f"\n[SUMMARY]")
        print(f"  Pending PM US markets: {len(pending)}")
        print(f"  With Kalshi match: {matches}")
        print(f"  Without Kalshi match: {no_matches}")
        print(f"  Match rate: {100*matches/(matches+no_matches):.1f}%" if (matches+no_matches) > 0 else "N/A")

        # Display pending by urgency
        display_pending_markets(pending, limit=10)

        # Show activation stats
        print("\n[ACTIVATION HISTORY]")
        history = load_activated_markets()
        if history:
            stats = get_activation_stats()
            print(f"  Total records: {stats.get('count', 0)}")
            if stats.get('avg_hours_before'):
                print(f"  Avg activation: {stats['avg_hours_before']:.1f}h before game")
        else:
            print("  No activations recorded yet - waiting for first activation!")

        print("\n" + "=" * 70)
        print("When a market activates, it will be logged to activated_markets.json")
        print("This helps us understand PM US activation timing patterns")
        print("=" * 70)

if __name__ == '__main__':
    asyncio.run(test_pending())
