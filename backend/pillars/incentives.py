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

# Try to import soccer data sources
# Priority: Football-Data.org (FOOTBALL_DATA_API_KEY) then API-Football (API_FOOTBALL_KEY)
SOCCER_DATA_AVAILABLE = False
USING_FOOTBALL_DATA = False
USING_API_FOOTBALL = False

try:
    from data_sources.football_data import get_epl_standings
    import os
    if os.getenv("FOOTBALL_DATA_API_KEY"):
        SOCCER_DATA_AVAILABLE = True
        USING_FOOTBALL_DATA = True
        logger.info("[Incentives] Football-Data.org API key found - using Football-Data")
except ImportError as e:
    logger.warning(f"[Incentives] Football-Data not available: {e}")

if not SOCCER_DATA_AVAILABLE:
    try:
        from data_sources.api_football import get_league_standings_sync
        import os
        if os.getenv("API_FOOTBALL_KEY"):
            SOCCER_DATA_AVAILABLE = True
            USING_API_FOOTBALL = True
            logger.info("[Incentives] API-Football key found - using API-Football")
    except ImportError as e:
        logger.warning(f"[Incentives] API-Football not available: {e}")


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
    is_soccer_sport = sport and ("soccer" in sport.lower() or sport.lower().startswith("soccer"))
    logger.info(f"[Incentives] Sport check: sport={sport}, is_soccer={is_soccer_sport}, SOCCER_DATA_AVAILABLE={SOCCER_DATA_AVAILABLE}")

    if is_soccer_sport and SOCCER_DATA_AVAILABLE:
        try:
            logger.info(f"[Incentives] Fetching soccer standings for {home_team} vs {away_team} (using={'Football-Data' if USING_FOOTBALL_DATA else 'API-Football'})...")

            # Use the appropriate API based on which key is available
            standings = None
            if USING_FOOTBALL_DATA:
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                standings = loop.run_until_complete(get_epl_standings())
            elif USING_API_FOOTBALL:
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
                    # Top 4 race (Champions League spots)
                    home_in_top_4 = home_pos <= 4
                    away_in_top_4 = away_pos <= 4
                    home_chasing_top_4 = 5 <= home_pos <= 7
                    away_chasing_top_4 = 5 <= away_pos <= 7

                    # Relegation zone (bottom 3)
                    home_in_relegation = home_pos >= 18
                    away_in_relegation = away_pos >= 18
                    home_above_relegation = 15 <= home_pos <= 17
                    away_above_relegation = 15 <= away_pos <= 17

                    # Title race motivation
                    if home_in_top_4 and away_chasing_top_4:
                        title_race_alert = True
                        motivation_differential -= 0.12  # Home defending position
                    elif away_in_top_4 and home_chasing_top_4:
                        title_race_alert = True
                        motivation_differential += 0.12  # Away defending position

                    # Relegation battle motivation (DESPERATE games)
                    if home_in_relegation:
                        relegation_battle_alert = True
                        motivation_differential -= 0.20  # Home DESPERATE to stay up
                        home_motivation = min(1.0, home_motivation + 0.3)
                    if away_in_relegation:
                        relegation_battle_alert = True
                        motivation_differential += 0.20  # Away DESPERATE to stay up
                        away_motivation = min(1.0, away_motivation + 0.3)

                    # Mid-table vs relegation/top 4
                    if 8 <= home_pos <= 14 and (away_in_relegation or away_in_top_4):
                        motivation_differential += 0.10  # Away has more to play for
                    elif 8 <= away_pos <= 14 and (home_in_relegation or home_in_top_4):
                        motivation_differential -= 0.10  # Home has more to play for

                    logger.info(f"[Incentives] Soccer positions: Home={home_pos}, Away={away_pos}")

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
    
    base_score = 0.5
    score = base_score + (motivation_differential * 0.5)
    score = max(0.0, min(1.0, score))
    
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