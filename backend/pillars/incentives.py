"""
Pillar 2: Incentives & Strategic Behavior
Weight: 0.15

Measures: Motivation asymmetries between teams
- Playoff positioning (fighting for spot vs clinched)
- Tank scenarios (eliminated teams may rest players)
- Rivalry games (heightened motivation)
"""
from datetime import datetime
import logging

from data_sources.espn import espn_client

logger = logging.getLogger(__name__)

RIVALRIES = {
    "NFL": [
        ("Dallas Cowboys", "Washington Commanders"),
        ("Green Bay Packers", "Chicago Bears"),
        ("New England Patriots", "New York Jets"),
        ("Pittsburgh Steelers", "Baltimore Ravens"),
        ("San Francisco 49ers", "Seattle Seahawks"),
        ("Kansas City Chiefs", "Las Vegas Raiders"),
    ],
    "NBA": [
        ("Los Angeles Lakers", "Boston Celtics"),
        ("Los Angeles Lakers", "Los Angeles Clippers"),
        ("New York Knicks", "Brooklyn Nets"),
        ("Golden State Warriors", "Cleveland Cavaliers"),
        ("Miami Heat", "Boston Celtics"),
    ],
    "NHL": [
        ("Boston Bruins", "Montreal Canadiens"),
        ("Chicago Blackhawks", "Detroit Red Wings"),
        ("Pittsburgh Penguins", "Philadelphia Flyers"),
        ("Colorado Avalanche", "Detroit Red Wings"),
    ],
    "NCAAF": [
        ("Ohio State Buckeyes", "Michigan Wolverines"),
        ("Alabama Crimson Tide", "Auburn Tigers"),
        ("USC Trojans", "UCLA Bruins"),
        ("Texas Longhorns", "Oklahoma Sooners"),
    ],
    "NCAAB": [
        ("Duke Blue Devils", "North Carolina Tar Heels"),
        ("Kentucky Wildcats", "Louisville Cardinals"),
        ("Kansas Jayhawks", "Missouri Tigers"),
    ],
    # Soccer rivalries
    "soccer": [
        ("Manchester United", "Manchester City"),
        ("Manchester United", "Liverpool"),
        ("Liverpool", "Everton"),
        ("Arsenal", "Tottenham"),
        ("Chelsea", "Arsenal"),
        ("Chelsea", "Tottenham"),
        ("Newcastle", "Sunderland"),  # Tyne-Wear derby
        ("Aston Villa", "Birmingham"),
        ("West Ham", "Millwall"),
        ("Leeds", "Manchester United"),
        ("Nottingham Forest", "Derby"),
    ],
    "soccer_epl": [
        ("Manchester United", "Manchester City"),
        ("Manchester United", "Liverpool"),
        ("Liverpool", "Everton"),
        ("Arsenal", "Tottenham"),
        ("Chelsea", "Arsenal"),
        ("Chelsea", "Tottenham"),
    ],
    "soccer_england_championship": [
        ("Newcastle", "Sunderland"),
        ("Leeds", "Sheffield United"),
        ("Nottingham Forest", "Derby"),
        ("Bristol City", "Cardiff"),
        ("Birmingham", "Aston Villa"),
        ("West Brom", "Wolverhampton"),
    ],
}

# Try to import soccer data sources (optional - may not have API keys)
# Priority: Football-Data.org (FOOTBALL_DATA_API_KEY) then API-Football (API_FOOTBALL_KEY)
import os

# Import modules at module level, but check API keys at runtime
# This handles cases where env vars are set after module import (Railway/Docker)
_football_data_available = False
_api_football_available = False
_football_data_import_error = None
_api_football_import_error = None

try:
    from data_sources.football_data import get_epl_standings
    _football_data_available = True
    logger.info("[Incentives INIT] football_data module imported successfully")
except Exception as e:
    _football_data_import_error = str(e)
    logger.error(f"[Incentives INIT] football_data import FAILED: {e}")

try:
    from data_sources.api_football import get_league_standings_sync
    _api_football_available = True
    logger.info("[Incentives INIT] api_football module imported successfully")
except Exception as e:
    _api_football_import_error = str(e)
    logger.error(f"[Incentives INIT] api_football import FAILED: {e}")

logger.info(f"[Incentives INIT] _football_data_available={_football_data_available}, _api_football_available={_api_football_available}")


def _get_soccer_data_source():
    """
    Determine which soccer data source to use at runtime.
    Checks env vars each time to handle late-loaded environment variables.
    """
    has_fd_key = bool(os.getenv("FOOTBALL_DATA_API_KEY"))
    has_af_key = bool(os.getenv("API_FOOTBALL_KEY"))

    if _football_data_available and has_fd_key:
        return "football_data"
    if _api_football_available and has_af_key:
        return "api_football"
    return None


def is_rivalry_game(sport: str, team1: str, team2: str) -> bool:
    """Check if this matchup is a known rivalry."""
    sport_rivalries = RIVALRIES.get(sport, [])

    # For soccer, also check the generic "soccer" rivalries
    if sport and "soccer" in sport.lower():
        sport_rivalries = sport_rivalries + RIVALRIES.get("soccer", [])

    for r1, r2 in sport_rivalries:
        if (team1.lower() in r1.lower() or r1.lower() in team1.lower()) and \
           (team2.lower() in r2.lower() or r2.lower() in team2.lower()):
            return True
        if (team2.lower() in r1.lower() or r1.lower() in team2.lower()) and \
           (team1.lower() in r2.lower() or r2.lower() in team1.lower()):
            return True
    return False


def _is_championship_game(sport: str, home_team: str, away_team: str, game_time: datetime) -> bool:
    """Detect if this is likely a championship/Super Bowl game."""
    # Check if it's late January/early February for Super Bowl
    if sport in ["NFL", "americanfootball_nfl"]:
        month = game_time.month
        day = game_time.day
        # Super Bowl is typically first Sunday in February
        if month == 2 and day <= 15:
            return True
        # Conference championships are mid-late January
        if month == 1 and day >= 15:
            return True
    return False


def calculate_incentives_score(
    sport: str,
    home_team: str,
    away_team: str,
    game_time: datetime
) -> dict:
    """
    Calculate Pillar 2: Incentives & Strategic Behavior score.

    A score > 0.5 means AWAY team has motivation advantage
    A score < 0.5 means HOME team has motivation advantage
    A score = 0.5 means balanced motivation
    """
    # Determine soccer data source at runtime (handles late-loaded env vars)
    soccer_source = _get_soccer_data_source()

    home_incentive = espn_client.get_team_incentive_score(sport, home_team)
    away_incentive = espn_client.get_team_incentive_score(sport, away_team)

    home_motivation = home_incentive["motivation_score"]
    away_motivation = away_incentive["motivation_score"]

    rivalry = is_rivalry_game(sport, home_team, away_team)
    rivalry_boost = 0.1 if rivalry else 0.0

    # Championship game detection
    is_championship = _is_championship_game(sport, home_team, away_team, game_time)

    if is_championship:
        # Both teams have maximum motivation in championship games
        home_motivation = 1.0
        away_motivation = 1.0

    if rivalry:
        home_motivation = min(1.0, home_motivation + rivalry_boost)
        away_motivation = min(1.0, away_motivation + rivalry_boost)
    
    motivation_differential = away_motivation - home_motivation
    
    tank_alert = False
    rest_alert = False
    
    home_status = home_incentive["playoff_status"]
    away_status = away_incentive["playoff_status"]
    home_gb = home_incentive.get("games_back", 0)
    away_gb = away_incentive.get("games_back", 0)

    logger.info(f"[Incentives] {home_team}: status={home_status}, GB={home_gb}, motivation={home_motivation}")
    logger.info(f"[Incentives] {away_team}: status={away_status}, GB={away_gb}, motivation={away_motivation}")

    # Tank scenarios: eliminated vs contending
    if home_status == "eliminated" and away_status == "contending":
        tank_alert = True
        motivation_differential += 0.15
    elif away_status == "eliminated" and home_status == "contending":
        tank_alert = True
        motivation_differential -= 0.15

    # Rest scenarios: clinched teams may rest starters
    if home_status == "clinched":
        rest_alert = True
        motivation_differential += 0.1
    if away_status == "clinched":
        rest_alert = True
        motivation_differential -= 0.1

    # SOCCER-SPECIFIC: Title race (top 4) vs relegation battle (bottom 3)
    title_race_alert = False
    relegation_battle_alert = False
    soccer_motivation_adjustment = 0.0  # Direct adjustment to final score
    is_soccer_sport = sport and ("soccer" in sport.lower() or sport.lower().startswith("soccer"))
    logger.info(f"[Incentives] Sport check: sport={sport}, is_soccer={is_soccer_sport}, soccer_source={soccer_source}")

    if is_soccer_sport and soccer_source:
        try:
            logger.info(f"[Incentives] Fetching soccer standings for {home_team} vs {away_team} (using={soccer_source})...")

            standings = None
            if soccer_source == "football_data":
                standings = get_epl_standings()
            elif soccer_source == "api_football":
                standings = get_league_standings_sync()

            logger.info(f"[Incentives] Got standings: {len(standings) if standings else 0} teams")
            if standings:
                home_pos = None
                away_pos = None
                for name, data in standings.items():
                    if home_team.lower() in name.lower() or name.lower() in home_team.lower():
                        home_pos = data.get("position", 12)
                    if away_team.lower() in name.lower() or name.lower() in away_team.lower():
                        away_pos = data.get("position", 12)

                if home_pos and away_pos:
                    logger.info(f"[Incentives] Positions: {home_team}={home_pos}, {away_team}={away_pos}")

                    # Calculate motivation levels based on league position
                    # Higher score = more desperate/motivated
                    def get_position_motivation(pos):
                        if pos <= 2:  # Title race
                            return 0.95
                        elif pos <= 4:  # CL spots
                            return 0.90
                        elif pos <= 7:  # Europa race
                            return 0.80
                        elif pos <= 14:  # Mid-table (nothing to play for)
                            return 0.50
                        elif pos <= 17:  # Above relegation (nervous)
                            return 0.75
                        else:  # Relegation zone (DESPERATE)
                            return 1.0

                    home_pos_motivation = get_position_motivation(home_pos)
                    away_pos_motivation = get_position_motivation(away_pos)

                    # Relegation zone detection
                    home_in_relegation = home_pos >= 18
                    away_in_relegation = away_pos >= 18
                    home_mid_table = 8 <= home_pos <= 14
                    away_mid_table = 8 <= away_pos <= 14

                    # CASE 1: Relegation team vs mid-table (HUGE motivation gap)
                    # Mid-table has ADVANTAGE because relegation team is under pressure
                    if home_in_relegation and away_mid_table:
                        relegation_battle_alert = True
                        # Away (mid-table) has psychological edge - no pressure
                        soccer_motivation_adjustment = 0.15  # Push score toward away
                        reasoning_parts.append(f"RELEGATION PRESSURE: {home_team} ({home_pos}th) in survival mode")
                        reasoning_parts.append(f"{away_team} ({away_pos}th) plays with freedom - no pressure")

                    elif away_in_relegation and home_mid_table:
                        relegation_battle_alert = True
                        # Home (mid-table) has psychological edge
                        soccer_motivation_adjustment = -0.15  # Push score toward home
                        reasoning_parts.append(f"RELEGATION PRESSURE: {away_team} ({away_pos}th) in survival mode")
                        reasoning_parts.append(f"{home_team} ({home_pos}th) plays with freedom - no pressure")

                    # CASE 2: Both in relegation zone (both desperate, neutral)
                    elif home_in_relegation and away_in_relegation:
                        relegation_battle_alert = True
                        soccer_motivation_adjustment = 0.0  # Both desperate = neutral
                        reasoning_parts.append(f"RELEGATION SIX-POINTER: Both teams fighting for survival")
                        reasoning_parts.append(f"{home_team} {home_pos}th vs {away_team} {away_pos}th")

                    # CASE 3: Top 4/6 race
                    elif home_pos <= 6 and away_pos <= 6:
                        title_race_alert = True
                        soccer_motivation_adjustment = 0.0  # Both motivated
                        reasoning_parts.append(f"TOP OF TABLE CLASH: Both chasing European spots")

                    # CASE 4: Top team vs relegation team (top team should win but less motivated)
                    elif home_pos <= 6 and away_in_relegation:
                        relegation_battle_alert = True
                        soccer_motivation_adjustment = 0.08  # Slight away edge (desperation factor)
                        reasoning_parts.append(f"{away_team} DESPERATE ({away_pos}th) vs comfortable {home_team} ({home_pos}th)")

                    elif away_pos <= 6 and home_in_relegation:
                        relegation_battle_alert = True
                        soccer_motivation_adjustment = -0.08  # Slight home edge
                        reasoning_parts.append(f"{home_team} DESPERATE ({home_pos}th) vs comfortable {away_team} ({away_pos}th)")

                    # CASE 5: General position-based motivation
                    else:
                        motivation_gap = away_pos_motivation - home_pos_motivation
                        # Scale: 0.5 motivation gap = 10% score adjustment
                        soccer_motivation_adjustment = motivation_gap * 0.20
                        if abs(motivation_gap) > 0.2:
                            more_motivated = home_team if motivation_gap < 0 else away_team
                            reasoning_parts.append(f"{more_motivated} more motivated based on league position")

                    logger.info(f"[Incentives] Motivation: home={home_pos_motivation:.2f}, away={away_pos_motivation:.2f}")
                    logger.info(f"[Incentives] soccer_motivation_adjustment={soccer_motivation_adjustment:.3f}")

        except Exception as e:
            logger.warning(f"[Incentives] Soccer data fetch failed: {e}")

    # Motivation edge based on playoff position
    # Teams actively fighting for playoffs have stronger motivation than:
    # - Teams out of the race (>5 GB, nothing to play for)
    # - Teams that have clinched (may rest players)

    # contending vs out_of_race: contending team is hungry
    if home_status == "contending" and away_status == "out_of_race":
        motivation_differential -= 0.15  # Home team has motivation edge
        logger.info(f"[Incentives] {home_team} contending vs {away_team} out_of_race → home edge")
    elif away_status == "contending" and home_status == "out_of_race":
        motivation_differential += 0.15  # Away team has motivation edge
        logger.info(f"[Incentives] {away_team} contending vs {home_team} out_of_race → away edge")

    # contending vs clinched: contending team is desperate, clinched may coast
    elif home_status == "contending" and away_status == "clinched":
        motivation_differential -= 0.12  # Home fighting for spot, away may rest
        logger.info(f"[Incentives] {home_team} contending vs {away_team} clinched → home edge")
    elif away_status == "contending" and home_status == "clinched":
        motivation_differential += 0.12  # Away fighting for spot, home may rest
        logger.info(f"[Incentives] {away_team} contending vs {home_team} clinched → away edge")

    # clinched vs out_of_race: clinched has better position, but neither is desperate
    elif home_status == "clinched" and away_status == "out_of_race":
        motivation_differential -= 0.05  # Slight home edge (better team, seeding)
    elif away_status == "clinched" and home_status == "out_of_race":
        motivation_differential += 0.05  # Slight away edge (better team, seeding)

    logger.info(f"[Incentives] Final differential: {motivation_differential:.3f}")
    logger.info(f"[Incentives] Soccer motivation adjustment: {soccer_motivation_adjustment:.3f}")

    base_score = 0.5

    # Apply standard motivation differential (increased multiplier from 0.5 to 0.8)
    score = base_score + (motivation_differential * 0.8)

    # Apply soccer-specific motivation adjustment DIRECTLY
    score += soccer_motivation_adjustment

    # Clamp to valid range but allow strong edges
    score = max(0.15, min(0.85, score))

    logger.info(f"[Incentives] Final score: {score:.3f}")

    reasoning_parts = []

    if is_championship:
        reasoning_parts.append("Championship game: maximum motivation for both teams")

    if rivalry:
        reasoning_parts.append("Rivalry game: heightened motivation for both teams")

    if tank_alert:
        reasoning_parts.append("Tank/elimination scenario detected")

    if rest_alert:
        reasoning_parts.append("Clinched team may rest players")

    # Soccer-specific reasoning
    if title_race_alert:
        reasoning_parts.append("Top 4 race: Champions League qualification at stake")

    if relegation_battle_alert:
        reasoning_parts.append("RELEGATION BATTLE: Survival on the line - maximum desperation")

    if not is_championship:
        if home_status == "contending":
            reasoning_parts.append(f"{home_team} fighting for playoff spot ({home_incentive['games_back']} GB)")
        elif home_status == "out_of_race":
            reasoning_parts.append(f"{home_team} out of playoff race ({home_incentive['games_back']} GB)")
        elif home_status == "clinched":
            reasoning_parts.append(f"{home_team} clinched playoffs")
        elif home_status == "eliminated":
            reasoning_parts.append(f"{home_team} eliminated from playoffs")

        if away_status == "contending":
            reasoning_parts.append(f"{away_team} fighting for playoff spot ({away_incentive['games_back']} GB)")
        elif away_status == "out_of_race":
            reasoning_parts.append(f"{away_team} out of playoff race ({away_incentive['games_back']} GB)")
        elif away_status == "clinched":
            reasoning_parts.append(f"{away_team} clinched playoffs")
        elif away_status == "eliminated":
            reasoning_parts.append(f"{away_team} eliminated from playoffs")

    if abs(motivation_differential) < 0.1 and not reasoning_parts:
        reasoning_parts.append("No significant motivation asymmetry")
    
    return {
        "score": round(score, 3),
        "home_motivation": round(home_motivation, 3),
        "away_motivation": round(away_motivation, 3),
        "is_rivalry": rivalry,
        "is_championship": is_championship,
        "breakdown": {
            "home_incentive": home_incentive,
            "away_incentive": away_incentive,
            "motivation_differential": round(motivation_differential, 3),
            "tank_alert": tank_alert,
            "rest_alert": rest_alert,
            "is_championship": is_championship
        },
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Balanced motivation levels"
    }


def get_incentive_edge_direction(score: float) -> str:
    """Interpret the incentives score."""
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "neutral"