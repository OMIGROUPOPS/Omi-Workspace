"""
Football-Data.org API integration for EPL data
API: https://api.football-data.org/v4/
Auth: X-Auth-Token header
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "")
BASE_URL = "https://api.football-data.org/v4"

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
        "X-Auth-Token": FOOTBALL_DATA_API_KEY,
        "Content-Type": "application/json"
    }


async def get_epl_standings() -> Optional[Dict[str, Any]]:
    """
    Fetch EPL standings including team positions, points, and form.

    Returns:
        Dict with standings data or None if request fails
    """
    if not FOOTBALL_DATA_API_KEY:
        print("[FOOTBALL-DATA] No API key configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/competitions/PL/standings",
                headers=get_headers(),
                timeout=10.0
            )

            if response.status_code != 200:
                print(f"[FOOTBALL-DATA] Standings request failed: {response.status_code}")
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

            return standings

    except Exception as e:
        print(f"[FOOTBALL-DATA] Error fetching standings: {e}")
        return None


async def get_epl_matches(days_ahead: int = 7) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch upcoming EPL fixtures.

    Args:
        days_ahead: Number of days to look ahead for fixtures

    Returns:
        List of match data or None if request fails
    """
    if not FOOTBALL_DATA_API_KEY:
        print("[FOOTBALL-DATA] No API key configured")
        return None

    try:
        date_from = datetime.now().strftime("%Y-%m-%d")
        date_to = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

        async with httpx.AsyncClient() as client:
            response = await client.get(
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


async def get_team_info(team_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed team information.

    Args:
        team_id: Football-Data team ID

    Returns:
        Team data or None if request fails
    """
    if not FOOTBALL_DATA_API_KEY:
        print("[FOOTBALL-DATA] No API key configured")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
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


async def get_team_standings_data(team_name: str) -> Optional[Dict[str, Any]]:
    """
    Get standings data for a specific team by name.

    Args:
        team_name: Team name (from Odds API)

    Returns:
        Team standings data or None if not found
    """
    standings = await get_epl_standings()
    if not standings:
        return None

    # Try to find team in standings by various name matches
    for name, data in standings.items():
        if team_name.lower() in name.lower() or name.lower() in team_name.lower():
            return data

    return None


# Sync wrappers for use in non-async contexts
def get_epl_standings_sync() -> Optional[Dict[str, Any]]:
    """Synchronous wrapper for get_epl_standings."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_epl_standings())


def get_team_standings_data_sync(team_name: str) -> Optional[Dict[str, Any]]:
    """Synchronous wrapper for get_team_standings_data."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_team_standings_data(team_name))
