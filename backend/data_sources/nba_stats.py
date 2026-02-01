"""
NBA.com Stats API Integration

Free, no authentication required.
Provides advanced team stats: pace, offensive/defensive ratings, etc.

NOTE: NBA.com's stats API is notoriously unreliable and often:
- Blocks requests based on IP/user-agent
- Has rate limiting
- Times out frequently

For production, consider using a proxy or caching layer.
Fallback: Use ESPN data which is already integrated.
"""

import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

NBA_STATS_BASE = "https://stats.nba.com/stats"
NBA_CDN_BASE = "https://cdn.nba.com/static/json"  # Alternative CDN endpoint

# Required headers to avoid 403
HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


async def get_team_advanced_stats(season: str = "2024-25") -> Optional[dict]:
    """
    Fetch advanced team stats including pace and ratings.

    Returns dict with team stats:
    - PACE: Possessions per 48 minutes
    - OFF_RATING: Points per 100 possessions (offense)
    - DEF_RATING: Points per 100 possessions (defense)
    - NET_RATING: OFF_RATING - DEF_RATING
    """
    params = {
        'Conference': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'GameScope': '',
        'GameSegment': '',
        'LastNGames': 0,
        'LeagueID': '00',
        'Location': '',
        'MeasureType': 'Advanced',
        'Month': 0,
        'OpponentTeamID': 0,
        'Outcome': '',
        'PORound': 0,
        'PaceAdjust': 'N',
        'PerMode': 'PerGame',
        'Period': 0,
        'PlayerExperience': '',
        'PlayerPosition': '',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': season,
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'StarterBench': '',
        'TeamID': 0,
        'TwoWay': 0,
        'VsConference': '',
        'VsDivision': ''
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{NBA_STATS_BASE}/leaguedashteamstats",
                params=params,
                headers=HEADERS
            )
            response.raise_for_status()
            data = response.json()

            # Parse the NBA.com response format
            result_sets = data.get('resultSets', [])
            if not result_sets:
                return None

            headers = result_sets[0].get('headers', [])
            rows = result_sets[0].get('rowSet', [])

            # Convert to dict keyed by team abbreviation
            teams = {}
            for row in rows:
                team_data = dict(zip(headers, row))
                team_abbr = team_data.get('TEAM_ABBREVIATION', '')
                if team_abbr:
                    teams[team_abbr] = {
                        'team_id': team_data.get('TEAM_ID'),
                        'team_name': team_data.get('TEAM_NAME'),
                        'pace': team_data.get('PACE', 0),
                        'off_rating': team_data.get('OFF_RATING', 0),
                        'def_rating': team_data.get('DEF_RATING', 0),
                        'net_rating': team_data.get('NET_RATING', 0),
                        'ast_pct': team_data.get('AST_PCT', 0),
                        'ast_to_ratio': team_data.get('AST_TO', 0),
                        'reb_pct': team_data.get('REB_PCT', 0),
                        'ts_pct': team_data.get('TS_PCT', 0),
                        'efg_pct': team_data.get('EFG_PCT', 0),
                    }

            logger.info(f"Fetched advanced stats for {len(teams)} NBA teams")
            return teams

    except httpx.TimeoutException:
        logger.warning("NBA Stats API timeout - API is known to be slow/unreliable")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"NBA Stats API HTTP error: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"NBA Stats API error: {e}")
        return None


async def get_team_pace_matchup(home_abbr: str, away_abbr: str, season: str = "2024-25") -> Optional[dict]:
    """
    Get pace matchup data for a specific game.

    Returns expected game pace and tempo analysis.
    """
    teams = await get_team_advanced_stats(season)
    if not teams:
        return None

    home_stats = teams.get(home_abbr)
    away_stats = teams.get(away_abbr)

    if not home_stats or not away_stats:
        logger.warning(f"Could not find stats for {home_abbr} or {away_abbr}")
        return None

    # Calculate expected game pace (average of both teams)
    home_pace = home_stats.get('pace', 100)
    away_pace = away_stats.get('pace', 100)
    expected_pace = (home_pace + away_pace) / 2

    # League average pace is ~100
    league_avg_pace = 100.0
    pace_differential = expected_pace - league_avg_pace

    return {
        'home_team': home_abbr,
        'away_team': away_abbr,
        'home_pace': home_pace,
        'away_pace': away_pace,
        'expected_game_pace': expected_pace,
        'pace_vs_average': pace_differential,
        'pace_category': 'fast' if pace_differential > 2 else 'slow' if pace_differential < -2 else 'average',
        'home_off_rating': home_stats.get('off_rating', 0),
        'home_def_rating': home_stats.get('def_rating', 0),
        'away_off_rating': away_stats.get('off_rating', 0),
        'away_def_rating': away_stats.get('def_rating', 0),
    }


# Team abbreviation mapping (ESPN to NBA.com)
ESPN_TO_NBA_ABBR = {
    'ATL': 'ATL', 'BOS': 'BOS', 'BKN': 'BKN', 'CHA': 'CHA',
    'CHI': 'CHI', 'CLE': 'CLE', 'DAL': 'DAL', 'DEN': 'DEN',
    'DET': 'DET', 'GS': 'GSW', 'HOU': 'HOU', 'IND': 'IND',
    'LAC': 'LAC', 'LAL': 'LAL', 'MEM': 'MEM', 'MIA': 'MIA',
    'MIL': 'MIL', 'MIN': 'MIN', 'NO': 'NOP', 'NY': 'NYK',
    'OKC': 'OKC', 'ORL': 'ORL', 'PHI': 'PHI', 'PHX': 'PHX',
    'POR': 'POR', 'SAC': 'SAC', 'SA': 'SAS', 'TOR': 'TOR',
    'UTAH': 'UTA', 'WAS': 'WAS',
}
