"""
API-Football (RapidAPI) integration for EPL data
API: https://v3.football.api-sports.io/
Auth: x-rapidapi-key header
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
BASE_URL = "https://v3.football.api-sports.io"

# League IDs
EPL_LEAGUE_ID = 39  # English Premier League
CHAMPIONSHIP_LEAGUE_ID = 40  # English Championship
CURRENT_SEASON = 2024  # Will need to update for 2025 season

# Team ID mappings from Odds API names to API-Football team IDs
# Note: Different from Football-Data IDs
API_FOOTBALL_TEAM_MAPPINGS: Dict[str, int] = {
    # Current EPL teams
    "Arsenal": 42,
    "Aston Villa": 66,
    "Bournemouth": 35,
    "Brentford": 55,
    "Brighton": 51,
    "Brighton and Hove Albion": 51,
    "Chelsea": 49,
    "Crystal Palace": 52,
    "Everton": 45,
    "Fulham": 36,
    "Ipswich": 57,
    "Ipswich Town": 57,
    "Leicester": 46,
    "Leicester City": 46,
    "Liverpool": 40,
    "Manchester City": 50,
    "Man City": 50,
    "Manchester United": 33,
    "Man United": 33,
    "Newcastle": 34,
    "Newcastle United": 34,
    "Nottingham Forest": 65,
    "Nott'm Forest": 65,
    "Southampton": 41,
    "Tottenham": 47,
    "Tottenham Hotspur": 47,
    "West Ham": 48,
    "West Ham United": 48,
    "Wolverhampton": 39,
    "Wolves": 39,
    "Wolverhampton Wanderers": 39,
    # Championship teams
    "Burnley": 44,
    "Sunderland": 71,
    "Leeds": 63,
    "Leeds United": 63,
    "Sheffield United": 62,
    "Luton": 1359,
    "Luton Town": 1359,
    "Watford": 38,
    "Norwich": 68,
    "Norwich City": 68,
    "Middlesbrough": 69,
    "Coventry": 1070,
    "Coventry City": 1070,
    "West Brom": 60,
    "West Bromwich Albion": 60,
    "Bristol City": 1074,
    "Hull": 64,
    "Hull City": 64,
    "Stoke": 75,
    "Stoke City": 75,
    "Blackburn": 1103,
    "Blackburn Rovers": 1103,
    "Preston": 1101,
    "Preston North End": 1101,
    "Swansea": 54,
    "Swansea City": 54,
    "Cardiff": 61,
    "Cardiff City": 61,
    "Millwall": 1067,
    "QPR": 1066,
    "Queens Park Rangers": 1066,
    "Sheffield Wednesday": 56,
    "Derby": 67,
    "Derby County": 67,
    "Plymouth": 1099,
    "Plymouth Argyle": 1099,
    "Oxford United": 1115,
    "Portsmouth": 1061,
}


def get_headers() -> Dict[str, str]:
    """Get headers for API-Football requests."""
    return {
        "x-rapidapi-key": API_FOOTBALL_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }


async def get_league_standings(league_id: int = EPL_LEAGUE_ID, season: int = CURRENT_SEASON) -> Optional[Dict[str, Any]]:
    """
    Fetch league standings.

    Args:
        league_id: League ID (default: EPL)
        season: Season year (default: 2024)

    Returns:
        Dict with standings data or None if request fails
    """
    if not API_FOOTBALL_KEY:
        print("[API-FOOTBALL] No API key configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/standings",
                headers=get_headers(),
                params={
                    "league": league_id,
                    "season": season
                },
                timeout=10.0
            )

            if response.status_code != 200:
                print(f"[API-FOOTBALL] Standings request failed: {response.status_code}")
                return None

            data = response.json()

            if data.get("errors"):
                print(f"[API-FOOTBALL] API errors: {data['errors']}")
                return None

            standings = {}
            response_data = data.get("response", [])
            if response_data:
                for league in response_data:
                    for standing in league.get("league", {}).get("standings", [[]])[0]:
                        team = standing.get("team", {})
                        team_name = team.get("name", "")
                        standings[team_name] = {
                            "position": standing.get("rank"),
                            "points": standing.get("points"),
                            "played": standing.get("all", {}).get("played"),
                            "won": standing.get("all", {}).get("win"),
                            "draw": standing.get("all", {}).get("draw"),
                            "lost": standing.get("all", {}).get("lose"),
                            "goals_for": standing.get("all", {}).get("goals", {}).get("for"),
                            "goals_against": standing.get("all", {}).get("goals", {}).get("against"),
                            "goal_difference": standing.get("goalsDiff"),
                            "form": standing.get("form", ""),  # e.g., "WWDLW"
                            "team_id": team.get("id"),
                            "logo": team.get("logo"),
                        }

            return standings

    except Exception as e:
        print(f"[API-FOOTBALL] Error fetching standings: {e}")
        return None


async def get_team_injuries(team_id: int, season: int = CURRENT_SEASON) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch injuries for a specific team.

    Args:
        team_id: API-Football team ID
        season: Season year

    Returns:
        List of injuries or None if request fails
    """
    if not API_FOOTBALL_KEY:
        print("[API-FOOTBALL] No API key configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/injuries",
                headers=get_headers(),
                params={
                    "team": team_id,
                    "season": season
                },
                timeout=10.0
            )

            if response.status_code != 200:
                print(f"[API-FOOTBALL] Injuries request failed: {response.status_code}")
                return None

            data = response.json()

            if data.get("errors"):
                print(f"[API-FOOTBALL] API errors: {data['errors']}")
                return None

            injuries = []
            for item in data.get("response", []):
                player = item.get("player", {})
                fixture = item.get("fixture", {})
                injuries.append({
                    "player_name": player.get("name"),
                    "player_id": player.get("id"),
                    "player_photo": player.get("photo"),
                    "type": player.get("type"),  # e.g., "Knee Injury"
                    "reason": player.get("reason"),
                    "fixture_id": fixture.get("id"),
                    "fixture_date": fixture.get("date"),
                })

            return injuries

    except Exception as e:
        print(f"[API-FOOTBALL] Error fetching injuries: {e}")
        return None


async def get_head_to_head(team1_id: int, team2_id: int, last: int = 10) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch head-to-head record between two teams.

    Args:
        team1_id: First team's API-Football ID
        team2_id: Second team's API-Football ID
        last: Number of recent matches to fetch

    Returns:
        List of H2H matches or None if request fails
    """
    if not API_FOOTBALL_KEY:
        print("[API-FOOTBALL] No API key configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/fixtures/headtohead",
                headers=get_headers(),
                params={
                    "h2h": f"{team1_id}-{team2_id}",
                    "last": last
                },
                timeout=10.0
            )

            if response.status_code != 200:
                print(f"[API-FOOTBALL] H2H request failed: {response.status_code}")
                return None

            data = response.json()

            if data.get("errors"):
                print(f"[API-FOOTBALL] API errors: {data['errors']}")
                return None

            matches = []
            for fixture in data.get("response", []):
                teams = fixture.get("teams", {})
                goals = fixture.get("goals", {})
                score = fixture.get("score", {})

                matches.append({
                    "fixture_id": fixture.get("fixture", {}).get("id"),
                    "date": fixture.get("fixture", {}).get("date"),
                    "venue": fixture.get("fixture", {}).get("venue", {}).get("name"),
                    "home_team": teams.get("home", {}).get("name"),
                    "away_team": teams.get("away", {}).get("name"),
                    "home_goals": goals.get("home"),
                    "away_goals": goals.get("away"),
                    "home_winner": teams.get("home", {}).get("winner"),
                    "away_winner": teams.get("away", {}).get("winner"),
                    "fulltime": score.get("fulltime"),
                    "halftime": score.get("halftime"),
                })

            return matches

    except Exception as e:
        print(f"[API-FOOTBALL] Error fetching H2H: {e}")
        return None


async def get_team_statistics(team_id: int, league_id: int = EPL_LEAGUE_ID, season: int = CURRENT_SEASON) -> Optional[Dict[str, Any]]:
    """
    Fetch team statistics for the season.

    Args:
        team_id: API-Football team ID
        league_id: League ID
        season: Season year

    Returns:
        Team statistics or None if request fails
    """
    if not API_FOOTBALL_KEY:
        print("[API-FOOTBALL] No API key configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/teams/statistics",
                headers=get_headers(),
                params={
                    "team": team_id,
                    "league": league_id,
                    "season": season
                },
                timeout=10.0
            )

            if response.status_code != 200:
                print(f"[API-FOOTBALL] Stats request failed: {response.status_code}")
                return None

            data = response.json()

            if data.get("errors"):
                print(f"[API-FOOTBALL] API errors: {data['errors']}")
                return None

            response_data = data.get("response", {})
            if not response_data:
                return None

            fixtures = response_data.get("fixtures", {})
            goals = response_data.get("goals", {})

            return {
                "team": response_data.get("team", {}).get("name"),
                "form": response_data.get("form"),
                "played_home": fixtures.get("played", {}).get("home"),
                "played_away": fixtures.get("played", {}).get("away"),
                "wins_home": fixtures.get("wins", {}).get("home"),
                "wins_away": fixtures.get("wins", {}).get("away"),
                "draws_home": fixtures.get("draws", {}).get("home"),
                "draws_away": fixtures.get("draws", {}).get("away"),
                "loses_home": fixtures.get("loses", {}).get("home"),
                "loses_away": fixtures.get("loses", {}).get("away"),
                "goals_for_home": goals.get("for", {}).get("total", {}).get("home"),
                "goals_for_away": goals.get("for", {}).get("total", {}).get("away"),
                "goals_against_home": goals.get("against", {}).get("total", {}).get("home"),
                "goals_against_away": goals.get("against", {}).get("total", {}).get("away"),
                "clean_sheets": response_data.get("clean_sheet", {}),
                "failed_to_score": response_data.get("failed_to_score", {}),
                "biggest_streak": response_data.get("biggest", {}).get("streak", {}),
            }

    except Exception as e:
        print(f"[API-FOOTBALL] Error fetching team statistics: {e}")
        return None


def get_team_id(team_name: str) -> Optional[int]:
    """
    Get API-Football team ID from Odds API team name.

    Args:
        team_name: Team name from Odds API

    Returns:
        Team ID or None if not found
    """
    # Try exact match first
    if team_name in API_FOOTBALL_TEAM_MAPPINGS:
        return API_FOOTBALL_TEAM_MAPPINGS[team_name]

    # Try case-insensitive match
    team_lower = team_name.lower()
    for name, team_id in API_FOOTBALL_TEAM_MAPPINGS.items():
        if name.lower() == team_lower:
            return team_id

    # Try partial match
    for name, team_id in API_FOOTBALL_TEAM_MAPPINGS.items():
        if team_lower in name.lower() or name.lower() in team_lower:
            return team_id

    return None


async def get_match_context(home_team: str, away_team: str) -> Dict[str, Any]:
    """
    Get comprehensive match context for a fixture.

    Args:
        home_team: Home team name
        away_team: Away team name

    Returns:
        Dict with standings, form, injuries, and H2H data
    """
    home_id = get_team_id(home_team)
    away_id = get_team_id(away_team)

    context = {
        "home_team": home_team,
        "away_team": away_team,
        "standings": None,
        "home_injuries": [],
        "away_injuries": [],
        "h2h": [],
    }

    # Get standings
    standings = await get_league_standings()
    if standings:
        home_standing = None
        away_standing = None
        for name, data in standings.items():
            if home_team.lower() in name.lower() or name.lower() in home_team.lower():
                home_standing = data
            if away_team.lower() in name.lower() or name.lower() in away_team.lower():
                away_standing = data
        context["standings"] = {
            "home": home_standing,
            "away": away_standing,
        }

    # Get injuries
    if home_id:
        context["home_injuries"] = await get_team_injuries(home_id) or []
    if away_id:
        context["away_injuries"] = await get_team_injuries(away_id) or []

    # Get H2H
    if home_id and away_id:
        context["h2h"] = await get_head_to_head(home_id, away_id) or []

    return context


# Sync wrappers for use in non-async contexts
def get_league_standings_sync(league_id: int = EPL_LEAGUE_ID, season: int = CURRENT_SEASON) -> Optional[Dict[str, Any]]:
    """Synchronous wrapper for get_league_standings."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_league_standings(league_id, season))


def get_match_context_sync(home_team: str, away_team: str) -> Dict[str, Any]:
    """Synchronous wrapper for get_match_context."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_match_context(home_team, away_team))
