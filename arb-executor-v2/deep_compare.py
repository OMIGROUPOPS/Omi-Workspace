#!/usr/bin/env python3
"""Deep comparison of PM US vs Kalshi for TODAY using full team names"""
import asyncio
import aiohttp
import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, '.')
from arb_executor_v7 import (
    PolymarketUSAPI, KalshiAPI,
    PM_US_API_KEY, PM_US_SECRET_KEY,
    KALSHI_API_KEY, KALSHI_PRIVATE_KEY,
    SLUG_TO_KALSHI, SPORTS_CONFIG, parse_gid
)

async def deep_compare():
    pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)
    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)

    today = datetime.now().strftime('%Y-%m-%d')
    print("=" * 80)
    print(f"DEEP COMPARISON: PM US vs KALSHI for {today}")
    print("=" * 80)

    async with aiohttp.ClientSession() as session:
        # ================================================================
        # FETCH KALSHI GAMES FOR TODAY
        # ================================================================
        print(f"\n[1] FETCHING KALSHI GAMES FOR {today}...")

        kalshi_games = []  # List of {sport, gid, teams, team_codes, ticker}

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
                            title = m.get('title', '')  # Full game title
                            subtitle = m.get('subtitle', '')
                            event_ticker = m.get('event_ticker', '')

                            parts = ticker.split('-')
                            if len(parts) >= 3:
                                gid = parts[1]
                                team_code = parts[2]
                                if team_code == 'TIE':
                                    continue

                                date, t1, t2 = parse_gid(gid)
                                if date == today and t1 and t2:
                                    # Check if we already have this game
                                    existing = next((g for g in kalshi_games if g['gid'] == gid), None)
                                    if not existing:
                                        kalshi_games.append({
                                            'sport': sport,
                                            'gid': gid,
                                            'team_codes': sorted([t1, t2]),
                                            'title': title,
                                            'subtitle': subtitle,
                                            'ticker': ticker,
                                        })

                        cursor = data.get('cursor')
                        if not cursor or not markets:
                            break
                    else:
                        break

        # Sort by sport then by team codes
        kalshi_games.sort(key=lambda x: (x['sport'], x['team_codes']))

        print(f"\n[KALSHI {today.upper()}] {len(kalshi_games)} unique games:")
        kalshi_by_sport = defaultdict(list)
        for g in kalshi_games:
            kalshi_by_sport[g['sport']].append(g)

        for sport in ['nba', 'nhl', 'cbb']:
            games = kalshi_by_sport.get(sport, [])
            print(f"\n  {sport.upper()} ({len(games)} games):")
            for g in games:
                t1, t2 = g['team_codes']
                # Extract team names from title if available
                title = g['title'] or g['subtitle'] or ''
                print(f"    {t1} vs {t2}: {title[:60]}")

        # ================================================================
        # FETCH PM US PENDING GAMES FOR TODAY
        # ================================================================
        print(f"\n\n[2] FETCHING PM US PENDING GAMES FOR {today}...")

        all_pm = await pm_api.get_all_markets_including_pending(session)

        pm_games = []  # List of {sport, slug, teams, team_codes_raw, team_codes_mapped, team_names}

        for m in all_pm:
            slug = m.get('slug', '')
            active = m.get('active', False)
            game_time = m.get('gameStartTime', '')
            outcomes = m.get('outcomes', '[]')
            market_sides = m.get('marketSides', [])

            # Parse outcomes for team names
            try:
                if isinstance(outcomes, str):
                    team_names = json.loads(outcomes)
                else:
                    team_names = outcomes
            except:
                team_names = []

            # Get full team names from marketSides if available
            full_names = []
            for side in market_sides:
                team_info = side.get('team', {})
                if team_info:
                    full_name = team_info.get('name', '') or team_info.get('safeName', '')
                    if full_name:
                        full_names.append(full_name)

            # Only pending games
            if active:
                continue

            # Check sport
            sport = None
            for s in ['nba', 'nhl', 'cbb', 'ncaab']:
                if f'-{s}-' in slug:
                    sport = s if s != 'ncaab' else 'cbb'
                    break
            if not sport:
                continue

            # Parse teams from slug
            parts = slug.split('-')
            sport_idx = next((i for i, p in enumerate(parts) if p in ['nba', 'nhl', 'cbb', 'ncaab']), -1)
            if sport_idx < 0 or sport_idx + 2 >= len(parts):
                continue

            raw_t1 = parts[sport_idx + 1].upper()
            raw_t2 = parts[sport_idx + 2].upper()
            mapped_t1 = SLUG_TO_KALSHI.get(raw_t1, raw_t1)
            mapped_t2 = SLUG_TO_KALSHI.get(raw_t2, raw_t2)

            # Get game date (convert UTC to EST)
            game_date = None
            if game_time:
                try:
                    dt_utc = datetime.fromisoformat(game_time.replace('Z', '+00:00')).replace(tzinfo=None)
                    dt_est = dt_utc - timedelta(hours=5)
                    game_date = dt_est.strftime('%Y-%m-%d')
                except:
                    game_date = game_time[:10]

            if game_date != today:
                continue

            pm_games.append({
                'sport': sport,
                'slug': slug,
                'team_codes_raw': sorted([raw_t1, raw_t2]),
                'team_codes_mapped': sorted([mapped_t1, mapped_t2]),
                'team_names': team_names,
                'full_names': full_names,
                'game_time': game_time,
            })

        # Sort by sport then by team codes
        pm_games.sort(key=lambda x: (x['sport'], x['team_codes_mapped']))

        print(f"\n[PM US {today.upper()} PENDING] {len(pm_games)} games:")
        pm_by_sport = defaultdict(list)
        for g in pm_games:
            pm_by_sport[g['sport']].append(g)

        for sport in ['nba', 'nhl', 'cbb']:
            games = pm_by_sport.get(sport, [])
            print(f"\n  {sport.upper()} ({len(games)} games):")
            for g in games:
                raw = g['team_codes_raw']
                mapped = g['team_codes_mapped']
                names = g['full_names'] or g['team_names']
                mapping_note = ""
                if raw != mapped:
                    mapping_note = f" (raw: {raw[0]}-{raw[1]})"
                name_str = f" [{', '.join(names[:2])}]" if names else ""
                print(f"    {mapped[0]} vs {mapped[1]}{mapping_note}{name_str}")

        # ================================================================
        # COMPARE BY TEAM CODES
        # ================================================================
        print(f"\n\n[3] COMPARING GAMES...")

        overlaps = []
        kalshi_only = []
        pm_only = []

        # Build lookup sets
        kalshi_set = {(g['sport'], tuple(g['team_codes'])) for g in kalshi_games}
        pm_set = {(g['sport'], tuple(g['team_codes_mapped'])) for g in pm_games}

        # Find overlaps
        for g in pm_games:
            key = (g['sport'], tuple(g['team_codes_mapped']))
            if key in kalshi_set:
                # Find matching Kalshi game
                k_game = next((k for k in kalshi_games
                              if k['sport'] == g['sport'] and tuple(k['team_codes']) == tuple(g['team_codes_mapped'])), None)
                overlaps.append({
                    'sport': g['sport'],
                    'pm': g,
                    'kalshi': k_game,
                })

        # Find Kalshi-only
        for g in kalshi_games:
            key = (g['sport'], tuple(g['team_codes']))
            if key not in pm_set:
                kalshi_only.append(g)

        # Find PM-only
        for g in pm_games:
            key = (g['sport'], tuple(g['team_codes_mapped']))
            if key not in kalshi_set:
                pm_only.append(g)

        # ================================================================
        # DISPLAY RESULTS
        # ================================================================
        print(f"\n\n{'='*80}")
        print(f"[CONFIRMED OVERLAPS - {today}] {len(overlaps)} games on BOTH platforms:")
        print('='*80)

        for i, o in enumerate(overlaps, 1):
            sport = o['sport'].upper()
            pm = o['pm']
            k = o['kalshi']
            t1, t2 = pm['team_codes_mapped']
            pm_names = pm['full_names'] or pm['team_names']
            k_title = k['title'] if k else 'N/A'

            print(f"\n  {i}. {sport}: {t1} vs {t2}")
            print(f"     PM US: {pm['slug']}")
            if pm_names:
                print(f"     PM Names: {', '.join(pm_names[:2])}")
            print(f"     Kalshi: {k['ticker'] if k else 'N/A'}")
            if k_title:
                print(f"     Kalshi Title: {k_title[:70]}")

        print(f"\n\n{'='*80}")
        print(f"[KALSHI ONLY - {today}] {len(kalshi_only)} games NOT on PM US:")
        print('='*80)

        ko_by_sport = defaultdict(list)
        for g in kalshi_only:
            ko_by_sport[g['sport']].append(g)

        for sport in ['nba', 'nhl', 'cbb']:
            games = ko_by_sport.get(sport, [])
            if games:
                print(f"\n  {sport.upper()} ({len(games)}):")
                for g in games[:10]:  # Limit display
                    t1, t2 = g['team_codes']
                    title = g['title'][:50] if g['title'] else ''
                    print(f"    {t1} vs {t2}: {title}")
                if len(games) > 10:
                    print(f"    ... and {len(games)-10} more")

        print(f"\n\n{'='*80}")
        print(f"[PM US ONLY - {today}] {len(pm_only)} games NOT on Kalshi:")
        print('='*80)

        po_by_sport = defaultdict(list)
        for g in pm_only:
            po_by_sport[g['sport']].append(g)

        for sport in ['nba', 'nhl', 'cbb']:
            games = po_by_sport.get(sport, [])
            if games:
                print(f"\n  {sport.upper()} ({len(games)}):")
                for g in games[:10]:  # Limit display
                    t1, t2 = g['team_codes_mapped']
                    raw = g['team_codes_raw']
                    names = g['full_names'] or g['team_names']
                    name_str = f" [{', '.join(names[:2])}]" if names else ""
                    mapping = f" (raw: {raw[0]}-{raw[1]})" if raw != [t1, t2] else ""
                    print(f"    {t1} vs {t2}{mapping}{name_str}")
                if len(games) > 10:
                    print(f"    ... and {len(games)-10} more")

        # ================================================================
        # SUMMARY
        # ================================================================
        print(f"\n\n{'='*80}")
        print("[SUMMARY]")
        print('='*80)
        print(f"\n  Kalshi games today: {len(kalshi_games)}")
        print(f"  PM US pending today: {len(pm_games)}")
        print(f"  Confirmed overlaps: {len(overlaps)}")
        print(f"  Kalshi-only: {len(kalshi_only)}")
        print(f"  PM US-only: {len(pm_only)}")
        print(f"\n  Overlap rate (PM->Kalshi): {100*len(overlaps)/len(pm_games):.1f}%" if pm_games else "N/A")
        print(f"  Overlap rate (Kalshi->PM): {100*len(overlaps)/len(kalshi_games):.1f}%" if kalshi_games else "N/A")

        # By sport
        print(f"\n  By sport:")
        for sport in ['nba', 'nhl', 'cbb']:
            k_count = len(kalshi_by_sport.get(sport, []))
            pm_count = len(pm_by_sport.get(sport, []))
            overlap_count = len([o for o in overlaps if o['sport'] == sport])
            print(f"    {sport.upper()}: Kalshi={k_count}, PM={pm_count}, Overlap={overlap_count}")

if __name__ == '__main__':
    asyncio.run(deep_compare())
