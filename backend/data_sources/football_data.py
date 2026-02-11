"""
Football-Data.org API integration for EPL data
API: https://api.football-data.org/v4/
Auth: X-Auth-Token header

Uses synchronous requests to avoid async event loop conflicts with FastAPI.
"""

import os
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

BASE_URL = "https://api.football-data.org/v4"


def _get_api_key() -> str:
    """Read API key fresh each time (handles late-loaded env vars in Railway/Docker)."""
    return os.getenv("FOOTBALL_DATA_API_KEY", "")

# EPL team name mappings from Odds API names to Football-Data team IDs
# Note: These IDs are for the 2024-25 EPL season
EPL_TEAM_MAPPINGS: Dict[str, int] = {
    # Current EPL teams (2024-25)
    "Arsenal": 57,
    "Aston Villa": 58,
    "Bournemouth": 1044,
    "Brentford": 402,
    "Brighton": 397,
    "Brighton and Hove Albion": 397,
    "Chelsea": 61,
    "Crystal Palace": 354,
    "Everton": 62,
    "Fulham": 63,
    "Ipswich": 349,
    "Ipswich Town": 349,
    "Leicester": 338,
    "Leicester City": 338,
    "Liverpool": 64,
    "Manchester City": 65,
    "Man City": 65,
    "Manchester United": 66,
    "Man United": 66,
    "Newcastle": 67,
    "Newcastle United": 67,
    "Nottingham Forest": 351,
    "Nott'm Forest": 351,
    "Southampton": 340,
    "Tottenham": 73,
    "Tottenham Hotspur": 73,
    "West Ham": 563,
    "West Ham United": 563,
    "Wolverhampton": 76,
    "Wolves": 76,
    "Wolverhampton Wanderers": 76,
    # Championship teams that might appear in odds
    "Burnley": 328,
    "Sunderland": 71,
    "Leeds": 341,
    "Leeds United": 341,
    "Sheffield United": 356,
    "Luton": 389,
    "Luton Town": 389,
    "Watford": 346,
    "Norwich": 68,
    "Norwich City": 68,
    "Middlesbrough": 343,
    "Coventry": 1076,
    "Coventry City": 1076,
    "West Brom": 74,
    "West Bromwich Albion": 74,
    "Bristol City": 387,
    "Hull": 322,
    "Hull City": 322,
    "Stoke": 70,
    "Stoke City": 70,
    "Blackburn": 59,
    "Blackburn Rovers": 59,
    "Preston": 1081,
    "Preston North End": 1081,
    "Swansea": 72,
    "Swansea City": 72,
    "Cardiff": 715,
    "Cardiff City": 715,
    "Millwall": 384,
    "QPR": 69,
    "Queens Park Rangers": 69,
    "Sheffield Wednesday": 345,
    "Derby": 342,
    "Derby County": 342,
    "Plymouth": 1138,
    "Plymouth Argyle": 1138,
    "Oxford United": 1082,
    "Portsmouth": 1096,
}


def get_headers() -> Dict[str, str]:
    """Get headers for Football-Data API requests."""
    return {
        "X-Auth-Token": _get_api_key(),
        "Content-Type": "application/json"
    }


def get_standings(competition: str = "PL") -> Optional[Dict[str, Any]]:
    """
    Fetch standings for a competition.
    SYNCHRONOUS - safe to call from FastAPI/async context.

    Args:
        competition: Competition code (PL=Premier League, ELC=Championship, etc.)

    Returns:
        Dict with standings data or None if request fails
    """
    if not _get_api_key():
        print("[FOOTBALL-DATA] No API key configured (FOOTBALL_DATA_API_KEY not set)")
        return None

    try:
        print(f"[FOOTBALL-DATA] Fetching {competition} standings...")
        response = requests.get(
            f"{BASE_URL}/competitions/{competition}/standings",
            headers=get_headers(),
            timeout=10.0
        )

        print(f"[FOOTBALL-DATA] Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"[FOOTBALL-DATA] Standings request failed: {response.status_code} - {response.text[:200]}")
            return None

        data = response.json()

        # Parse standings into a usable format
        standings = {}
        if "standings" in data:
            for table in data["standings"]:
                if table.get("type") == "TOTAL":
                    for entry in table.get("table", []):
                        team_name = entry.get("team", {}).get("name", "")
                        standings[team_name] = {
                            "position": entry.get("position"),
                            "points": entry.get("points"),
                            "played": entry.get("playedGames"),
                            "won": entry.get("won"),
                            "draw": entry.get("draw"),
                            "lost": entry.get("lost"),
                            "goals_for": entry.get("goalsFor"),
                            "goals_against": entry.get("goalsAgainst"),
                            "goal_difference": entry.get("goalDifference"),
                            "form": entry.get("form", ""),  # e.g., "W,D,L,W,W"
                            "team_id": entry.get("team", {}).get("id"),
                        }

        print(f"[FOOTBALL-DATA] Got {len(standings)} teams in standings")
        return standings

    except Exception as e:
        print(f"[FOOTBALL-DATA] Error fetching standings: {e}")
        return None


def get_epl_standings() -> Optional[Dict[str, Any]]:
    """Fetch Premier League standings."""
    return get_standings("PL")


def get_championship_standings() -> Optional[Dict[str, Any]]:
    """Fetch Championship standings."""
    return get_standings("ELC")


def get_standings_for_sport(sport_key: str) -> Optional[Dict[str, Any]]:
    """
    Get standings based on sport key.
    Maps Odds API sport keys to Football-Data competition codes.

    Args:
        sport_key: e.g., "soccer_epl", "soccer_england_efl_champ"

    Returns:
        Standings dict or None
    """
    # Map sport keys to Football-Data competition codes
    sport_to_competition = {
        "soccer_epl": "PL",                      # Premier League
        "EPL": "PL",                             # Short key (from server/cron)
        "SOCCER_EPL": "PL",                      # Uppercased Odds API key
        "soccer_england_efl_champ": "ELC",       # Championship
        "soccer_england_league1": "EL1",         # League One
        "soccer_england_league2": "EL2",         # League Two
        "soccer_germany_bundesliga": "BL1",      # Bundesliga
        "soccer_spain_la_liga": "PD",            # La Liga
        "soccer_italy_serie_a": "SA",            # Serie A
        "soccer_france_ligue_one": "FL1",        # Ligue 1
    }

    competition = sport_to_competition.get(sport_key)
    if competition:
        print(f"[FOOTBALL-DATA] Sport '{sport_key}' -> competition '{competition}'")
        return get_standings(competition)

    # Fallback: try to guess from sport key
    if "efl_champ" in sport_key or "championship" in sport_key.lower():
        return get_standings("ELC")
    elif "epl" in sport_key or "premier" in sport_key.lower():
        return get_standings("PL")
    elif "league1" in sport_key.lower():
        return get_standings("EL1")
    elif "league2" in sport_key.lower():
        return get_standings("EL2")

    print(f"[FOOTBALL-DATA] Unknown sport key: {sport_key}, defaulting to PL")
    return get_standings("PL")


def get_epl_matches(days_ahead: int = 7) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch upcoming EPL fixtures.
    SYNCHRONOUS - safe to call from FastAPI/async context.

    Args:
        days_ahead: Number of days to look ahead for fixtures

    Returns:
        List of match data or None if request fails
    """
    if not _get_api_key():
        print("[FOOTBALL-DATA] No API key configured (FOOTBALL_DATA_API_KEY not set)")
        return None

    try:
        date_from = datetime.now().strftime("%Y-%m-%d")
        date_to = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        response = requests.get(
            f"{BASE_URL}/competitions/PL/matches",
            headers=get_headers(),
            params={
                "dateFrom": date_from,
                "dateTo": date_to,
                "status": "SCHEDULED,TIMED"
            },
            timeout=10.0
        )

        if response.status_code != 200:
            print(f"[FOOTBALL-DATA] Matches request failed: {response.status_code}")
            return None

        data = response.json()

        matches = []
        for match in data.get("matches", []):
            matches.append({
                "id": match.get("id"),
                "home_team": match.get("homeTeam", {}).get("name"),
                "away_team": match.get("awayTeam", {}).get("name"),
                "home_team_id": match.get("homeTeam", {}).get("id"),
                "away_team_id": match.get("awayTeam", {}).get("id"),
                "utc_date": match.get("utcDate"),
                "matchday": match.get("matchday"),
                "status": match.get("status"),
            })

        return matches

    except Exception as e:
        print(f"[FOOTBALL-DATA] Error fetching matches: {e}")
        return None


def get_team_info(team_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed team information.
    SYNCHRONOUS - safe to call from FastAPI/async context.

    Args:
        team_id: Football-Data team ID

    Returns:
        Team data or None if request fails
    """
    if not _get_api_key():
        print("[FOOTBALL-DATA] No API key configured (FOOTBALL_DATA_API_KEY not set)")
        return None

    try:
        response = requests.get(
            f"{BASE_URL}/teams/{team_id}",
            headers=get_headers(),
            timeout=10.0
        )

        if response.status_code != 200:
            print(f"[FOOTBALL-DATA] Team request failed: {response.status_code}")
            return None

        data = response.json()

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "short_name": data.get("shortName"),
            "tla": data.get("tla"),  # Three-letter abbreviation
            "crest": data.get("crest"),
            "venue": data.get("venue"),
            "founded": data.get("founded"),
            "coach": data.get("coach", {}).get("name"),
        }

    except Exception as e:
        print(f"[FOOTBALL-DATA] Error fetching team: {e}")
        return None


def get_team_id(team_name: str) -> Optional[int]:
    """
    Get Football-Data team ID from Odds API team name.

    Args:
        team_name: Team name from Odds API

    Returns:
        Team ID or None if not found
    """
    # Try exact match first
    if team_name in EPL_TEAM_MAPPINGS:
        return EPL_TEAM_MAPPINGS[team_name]

    # Try case-insensitive match
    team_lower = team_name.lower()
    for name, team_id in EPL_TEAM_MAPPINGS.items():
        if name.lower() == team_lower:
            return team_id

    # Try partial match
    for name, team_id in EPL_TEAM_MAPPINGS.items():
        if team_lower in name.lower() or name.lower() in team_lower:
            return team_id

    return None


def get_team_standings_data(team_name: str) -> Optional[Dict[str, Any]]:
    """
    Get standings data for a specific team by name.
    SYNCHRONOUS - safe to call from FastAPI/async context.

    Args:
        team_name: Team name (from Odds API)

    Returns:
        Team standings data or None if not found
    """
    standings = get_epl_standings()
    if not standings:
        return None

    # Try to find team in standings by various name matches
    for name, data in standings.items():
        if team_name.lower() in name.lower() or name.lower() in team_name.lower():
            return data

    return None


# Legacy aliases for backwards compatibility (all functions are now synchronous)
def get_epl_standings_sync() -> Optional[Dict[str, Any]]:
    """Alias for get_epl_standings (now synchronous)."""
    return get_epl_standings()


def get_team_standings_data_sync(team_name: str) -> Optional[Dict[str, Any]]:
    """Alias for get_team_standings_data (now synchronous)."""
    return get_team_standings_data(team_name)
