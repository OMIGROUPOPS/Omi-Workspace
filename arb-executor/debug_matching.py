#!/usr/bin/env python3
"""Debug team code matching - show all games to find overlaps"""
import asyncio
import aiohttp
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '.')
from arb_executor_v7 import (
    PolymarketUSAPI, KalshiAPI,
    PM_US_API_KEY, PM_US_SECRET_KEY,
    KALSHI_API_KEY, KALSHI_PRIVATE_KEY,
    SLUG_TO_KALSHI, SPORTS_CONFIG, parse_gid
)

async def debug_matching():
    pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)
    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)

    async with aiohttp.ClientSession() as session:
        print("=" * 70)
        print("FULL GAME COMPARISON: PM US vs KALSHI")
        print("=" * 70)

        # Fetch PM pending markets
        all_pm = await pm_api.get_all_markets_including_pending(session)
        pending = [m for m in all_pm if not m.get('active')]

        # Fetch Kalshi markets
        kalshi_by_date = {}  # {date: {sport: [(teams, gid)]}}

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
                                    if date not in kalshi_by_date:
                                        kalshi_by_date[date] = {}
                                    if sport not in kalshi_by_date[date]:
                                        kalshi_by_date[date][sport] = []
                                    kalshi_by_date[date][sport].append((sorted([t1, t2]), gid))

                        cursor = data.get('cursor')
                        if not cursor or not markets:
                            break
                    else:
                        break

        # Process PM pending markets by date
        pm_by_date = {}
        for m in pending:
            slug = m.get('slug', '')
            game_time = m.get('gameStartTime', '')

            # Parse sport
            sport = None
            for s in ['nba', 'nhl', 'cbb', 'ncaab']:
                if f'-{s}-' in slug:
                    sport = s if s != 'ncaab' else 'cbb'
                    break

            if not sport:
                continue

            # Parse teams
            parts = slug.split('-')
            sport_idx = next((i for i, p in enumerate(parts) if p in ['nba', 'nhl', 'cbb', 'ncaab']), -1)
            if sport_idx + 2 >= len(parts):
                continue

            raw_team1 = parts[sport_idx + 1].upper()
            raw_team2 = parts[sport_idx + 2].upper()
            team1 = SLUG_TO_KALSHI.get(raw_team1, raw_team1)
            team2 = SLUG_TO_KALSHI.get(raw_team2, raw_team2)

            # Get EST date
            if game_time:
                try:
                    dt_utc = datetime.fromisoformat(game_time.replace('Z', '+00:00')).replace(tzinfo=None)
                    dt_est = dt_utc - timedelta(hours=5)
                    date = dt_est.strftime('%Y-%m-%d')
                except:
                    date = game_time[:10]
            else:
                date = 'unknown'

            if date not in pm_by_date:
                pm_by_date[date] = {}
            if sport not in pm_by_date[date]:
                pm_by_date[date][sport] = []
            pm_by_date[date][sport].append({
                'teams': sorted([team1, team2]),
                'raw': sorted([raw_team1, raw_team2]),
                'slug': slug
            })

        # Compare by date
        today = datetime.now().strftime('%Y-%m-%d')

        for date in sorted(set(list(pm_by_date.keys()) + list(kalshi_by_date.keys()))):
            print(f"\n{'='*70}")
            print(f"DATE: {date}")
            print('='*70)

            pm_sports = pm_by_date.get(date, {})
            k_sports = kalshi_by_date.get(date, {})

            for sport in ['nba', 'nhl', 'cbb']:
                pm_games = pm_sports.get(sport, [])
                k_games = k_sports.get(sport, [])

                if not pm_games and not k_games:
                    continue

                print(f"\n  {sport.upper()}:")
                print(f"    PM: {len(pm_games)} games | Kalshi: {len(k_games)} games")

                # Find matches
                matches = []
                for pm in pm_games:
                    for k_teams, k_gid in k_games:
                        if pm['teams'] == k_teams:
                            matches.append((pm, k_teams, k_gid))
                            break

                if matches:
                    print(f"    [MATCHES: {len(matches)}]")
                    for pm, k_teams, k_gid in matches:
                        print(f"      {pm['teams'][0]} vs {pm['teams'][1]}: PM={pm['slug']}, K={k_gid}")
                else:
                    print(f"    [NO MATCHES]")
                    if pm_games:
                        print(f"      PM games (mapped teams):")
                        for pm in pm_games[:5]:
                            raw_info = f" (raw: {pm['raw']})" if pm['raw'] != pm['teams'] else ""
                            print(f"        {pm['teams'][0]} vs {pm['teams'][1]}{raw_info}")
                    if k_games:
                        print(f"      Kalshi games:")
                        for k_teams, k_gid in k_games[:5]:
                            print(f"        {k_teams[0]} vs {k_teams[1]} ({k_gid})")

if __name__ == '__main__':
    asyncio.run(debug_matching())
