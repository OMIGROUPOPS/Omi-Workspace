"""
NHL.com Stats API Integration

Free, no authentication required.
Provides team and player stats: TOI, shots, goals, etc.
"""

import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

NHL_STATS_BASE = "https://api.nhle.com/stats/rest/en"
NHL_WEB_API = "https://api-web.nhle.com/v1"

# NHL team name to abbreviation mapping
NHL_TEAM_NAME_TO_ABBR = {
    "Anaheim Ducks": "ANA",
    "Arizona Coyotes": "ARI",
    "Boston Bruins": "BOS",
    "Buffalo Sabres": "BUF",
    "Calgary Flames": "CGY",
    "Carolina Hurricanes": "CAR",
    "Chicago Blackhawks": "CHI",
    "Colorado Avalanche": "COL",
    "Columbus Blue Jackets": "CBJ",
    "Dallas Stars": "DAL",
    "Detroit Red Wings": "DET",
    "Edmonton Oilers": "EDM",
    "Florida Panthers": "FLA",
    "Los Angeles Kings": "LAK",
    "Minnesota Wild": "MIN",
    "Montréal Canadiens": "MTL",
    "Montreal Canadiens": "MTL",
    "Nashville Predators": "NSH",
    "New Jersey Devils": "NJD",
    "New York Islanders": "NYI",
    "New York Rangers": "NYR",
    "Ottawa Senators": "OTT",
    "Philadelphia Flyers": "PHI",
    "Pittsburgh Penguins": "PIT",
    "San Jose Sharks": "SJS",
    "Seattle Kraken": "SEA",
    "St. Louis Blues": "STL",
    "Tampa Bay Lightning": "TBL",
    "Toronto Maple Leafs": "TOR",
    "Utah Hockey Club": "UTA",
    "Vancouver Canucks": "VAN",
    "Vegas Golden Knights": "VGK",
    "Washington Capitals": "WSH",
    "Winnipeg Jets": "WPG",
}


def _get_team_abbr(team_name: str) -> str:
    """Get team abbreviation from full name."""
    return NHL_TEAM_NAME_TO_ABBR.get(team_name, "")


async def get_team_stats(season_id: str = "20242025") -> Optional[dict]:
    """
    Fetch team summary stats.

    Returns dict with team stats:
    - GP: Games played
    - W/L/OTL: Wins, losses, overtime losses
    - Points, goals for/against
    - Power play %, penalty kill %
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{NHL_STATS_BASE}/team/summary",
                params={
                    'sort': 'points',
                    'cayenneExp': f'seasonId={season_id}'
                }
            )
            response.raise_for_status()
            data = response.json()

            teams = {}
            for team in data.get('data', []):
                team_name = team.get('teamFullName', '')
                abbr = _get_team_abbr(team_name)

                if abbr:
                    # Convert decimal percentages to actual percentages (0.2 -> 20)
                    pp_pct = team.get('powerPlayPct', 0) * 100
                    pk_pct = team.get('penaltyKillPct', 0) * 100

                    teams[abbr] = {
                        'team_id': team.get('teamId'),
                        'team_name': team_name,
                        'games_played': team.get('gamesPlayed', 0),
                        'wins': team.get('wins', 0),
                        'losses': team.get('losses', 0),
                        'ot_losses': team.get('otLosses', 0),
                        'points': team.get('points', 0),
                        'goals_for': team.get('goalsFor', 0),
                        'goals_against': team.get('goalsAgainst', 0),
                        'goals_for_per_game': team.get('goalsForPerGame', 0),
                        'goals_against_per_game': team.get('goalsAgainstPerGame', 0),
                        'pp_pct': pp_pct,
                        'pk_pct': pk_pct,
                        'shots_for_per_game': team.get('shotsForPerGame', 0),
                        'shots_against_per_game': team.get('shotsAgainstPerGame', 0),
                    }
                else:
                    logger.warning(f"Unknown NHL team: {team_name}")

            logger.info(f"Fetched stats for {len(teams)} NHL teams")
            return teams

    except Exception as e:
        logger.error(f"NHL Stats API error: {e}")
        return None


async def get_team_advanced_stats(season_id: str = "20242025") -> Optional[dict]:
    """
    Fetch advanced team stats.

    Returns:
    - Corsi %, Fenwick %
    - Expected goals (xGF, xGA)
    - Scoring chances
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch miscellaneous stats which include some advanced metrics
            response = await client.get(
                f"{NHL_STATS_BASE}/team/percentages",
                params={
                    'sort': 'pointPct',
                    'cayenneExp': f'seasonId={season_id}'
                }
            )
            response.raise_for_status()
            data = response.json()

            teams = {}
            for team in data.get('data', []):
                abbr = team.get('teamAbbrev', '')
                if abbr:
                    teams[abbr] = {
                        'team_id': team.get('teamId'),
                        'point_pct': team.get('pointPct', 0),
                        'face_off_win_pct': team.get('faceoffWinPct', 0),
                        'shooting_pct': team.get('shootingPct', 0),
                        'save_pct': team.get('savePct', 0),
                    }

            return teams

    except Exception as e:
        logger.error(f"NHL Advanced Stats API error: {e}")
        return None


async def get_schedule(date: str) -> Optional[list]:
    """
    Get NHL schedule for a specific date.

    Args:
        date: YYYY-MM-DD format

    Returns list of games with basic info.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{NHL_WEB_API}/schedule/{date}")
            response.raise_for_status()
            data = response.json()

            games = []
            for week in data.get('gameWeek', []):
                for game in week.get('games', []):
                    games.append({
                        'game_id': game.get('id'),
                        'start_time': game.get('startTimeUTC'),
                        'game_state': game.get('gameState'),
                        'home_team': game.get('homeTeam', {}).get('abbrev'),
                        'away_team': game.get('awayTeam', {}).get('abbrev'),
                        'venue': game.get('venue', {}).get('default'),
                    })

            return games

    except Exception as e:
        logger.error(f"NHL Schedule API error: {e}")
        return None


async def get_team_matchup_stats(home_abbr: str, away_abbr: str, season_id: str = "20242025") -> Optional[dict]:
    """
    Get matchup analysis for a specific game.

    Calculates pace and efficiency metrics.
    """
    team_stats = await get_team_stats(season_id)
    if not team_stats:
        return None

    home = team_stats.get(home_abbr)
    away = team_stats.get(away_abbr)

    if not home or not away:
        logger.warning(f"Could not find stats for {home_abbr} or {away_abbr}")
        return None

    # Calculate expected game total
    home_gf = home.get('goals_for_per_game', 3.0)
    home_ga = home.get('goals_against_per_game', 3.0)
    away_gf = away.get('goals_for_per_game', 3.0)
    away_ga = away.get('goals_against_per_game', 3.0)

    # Expected goals = (Home offense vs Away defense + Away offense vs Home defense) / 2
    expected_home_goals = (home_gf + away_ga) / 2
    expected_away_goals = (away_gf + home_ga) / 2
    expected_total = expected_home_goals + expected_away_goals

    return {
        'home_team': home_abbr,
        'away_team': away_abbr,
        'home_goals_for_avg': home_gf,
        'home_goals_against_avg': home_ga,
        'away_goals_for_avg': away_gf,
        'away_goals_against_avg': away_ga,
        'expected_home_goals': round(expected_home_goals, 2),
        'expected_away_goals': round(expected_away_goals, 2),
        'expected_total': round(expected_total, 2),
        'home_pp_pct': home.get('pp_pct', 0),
        'away_pp_pct': away.get('pp_pct', 0),
        'home_pk_pct': home.get('pk_pct', 0),
        'away_pk_pct': away.get('pk_pct', 0),
    }


# Team abbreviation mapping (ESPN to NHL.com)
ESPN_TO_NHL_ABBR = {
    'ANA': 'ANA', 'ARI': 'ARI', 'BOS': 'BOS', 'BUF': 'BUF',
    'CGY': 'CGY', 'CAR': 'CAR', 'CHI': 'CHI', 'COL': 'COL',
    'CBJ': 'CBJ', 'DAL': 'DAL', 'DET': 'DET', 'EDM': 'EDM',
    'FLA': 'FLA', 'LA': 'LAK', 'MIN': 'MIN', 'MTL': 'MTL',
    'NSH': 'NSH', 'NJ': 'NJD', 'NYI': 'NYI', 'NYR': 'NYR',
    'OTT': 'OTT', 'PHI': 'PHI', 'PIT': 'PIT', 'SJ': 'SJS',
    'SEA': 'SEA', 'STL': 'STL', 'TB': 'TBL', 'TOR': 'TOR',
    'UTAH': 'UTA', 'VAN': 'VAN', 'VGK': 'VGK', 'WAS': 'WSH',
    'WPG': 'WPG',
}
