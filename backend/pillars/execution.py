"""
Pillar 1: Execution & Resolution Risk
Weight: 0.20

Measures: Who/what determines the outcome
- Player availability (injuries)
- Weather conditions (outdoor sports)
- Lineup uncertainty
- NFL position importance weighting
- Soccer: League position, form, goal difference
"""
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

from data_sources.espn import espn_client

# Try to import soccer data sources (optional - may not have API keys)
# Priority: Football-Data.org (FOOTBALL_DATA_API_KEY) then API-Football (API_FOOTBALL_KEY)
import os
SOCCER_DATA_AVAILABLE = False
USING_FOOTBALL_DATA = False
USING_API_FOOTBALL = False

print(f"[Execution INIT] Checking FOOTBALL_DATA_API_KEY: {bool(os.getenv('FOOTBALL_DATA_API_KEY'))}")
print(f"[Execution INIT] Checking API_FOOTBALL_KEY: {bool(os.getenv('API_FOOTBALL_KEY'))}")

try:
    from data_sources.football_data import get_epl_standings, get_team_standings_data_sync
    print("[Execution INIT] football_data module imported successfully")
    if os.getenv("FOOTBALL_DATA_API_KEY"):
        SOCCER_DATA_AVAILABLE = True
        USING_FOOTBALL_DATA = True
        print("[Execution INIT] FOOTBALL_DATA_API_KEY found - using Football-Data.org")
    else:
        print("[Execution INIT] FOOTBALL_DATA_API_KEY NOT SET")
except ImportError as e:
    print(f"[Execution INIT] football_data import failed: {e}")

if not SOCCER_DATA_AVAILABLE:
    try:
        from data_sources.api_football import get_league_standings_sync
        print("[Execution INIT] api_football module imported successfully")
        if os.getenv("API_FOOTBALL_KEY"):
            SOCCER_DATA_AVAILABLE = True
            USING_API_FOOTBALL = True
            print("[Execution INIT] API_FOOTBALL_KEY found - using API-Football")
        else:
            print("[Execution INIT] API_FOOTBALL_KEY NOT SET")
    except ImportError as e:
        print(f"[Execution INIT] api_football import failed: {e}")

print(f"[Execution INIT] Final: SOCCER_DATA_AVAILABLE={SOCCER_DATA_AVAILABLE}, USING_FOOTBALL_DATA={USING_FOOTBALL_DATA}")

if not SOCCER_DATA_AVAILABLE:
    print("[Execution INIT] WARNING: No soccer data sources available!")

# NFL position importance weights - AMPLIFIED for visual differentiation
# Higher = more impactful when injured (scale: 0-10)
NFL_POSITION_WEIGHTS = {
    "QB": 10.0,   # Quarterback is CRITICAL - 25-30% swing if out
    "LT": 4.0,    # Left tackle protects blind side
    "RT": 3.5,
    "WR": 3.0,    # Star WR matters
    "RB": 2.5,
    "TE": 2.0,
    "CB": 3.5,    # Cornerbacks critical vs pass
    "EDGE": 4.0,  # Pass rushers
    "DE": 3.5,
    "DT": 2.5,
    "LB": 2.5,
    "S": 2.5,
    "K": 1.5,
    "P": 0.5,
}

# Known Super Bowl / Championship game detection
def is_championship_game(home_team: str, away_team: str, sport: str) -> bool:
    """Detect if this is a championship/Super Bowl game."""
    # Super Bowl teams typically have high-stakes matchups
    # This is a heuristic - in production, check game metadata
    championship_keywords = ["super bowl", "championship", "final"]
    return False  # Will be enhanced with actual game metadata


def calculate_execution_score(
    sport: str,
    home_team: str,
    away_team: str,
    game_time: datetime,
    venue: Optional[dict] = None
) -> dict:
    """
    Calculate Pillar 1: Execution & Resolution Risk score.

    A score > 0.5 means the AWAY team has execution advantages
    A score < 0.5 means the HOME team has execution advantages
    A score = 0.5 means neutral/balanced
    """
    import os
    # Comprehensive debug logging
    logger.info(f"[Execution] ===== CALLED =====")
    logger.info(f"[Execution] sport={sport}, home={home_team}, away={away_team}")
    logger.info(f"[Execution] SOCCER_DATA_AVAILABLE={SOCCER_DATA_AVAILABLE}, USING_FOOTBALL_DATA={USING_FOOTBALL_DATA}, USING_API_FOOTBALL={USING_API_FOOTBALL}")
    logger.info(f"[Execution] FOOTBALL_DATA_API_KEY exists: {bool(os.getenv('FOOTBALL_DATA_API_KEY'))}")
    logger.info(f"[Execution] API_FOOTBALL_KEY exists: {bool(os.getenv('API_FOOTBALL_KEY'))}")

    home_injuries = espn_client.get_team_injury_impact(sport, home_team)
    away_injuries = espn_client.get_team_injury_impact(sport, away_team)

    home_injury_score = home_injuries["impact_score"]
    away_injury_score = away_injuries["impact_score"]

    reasoning_parts = []

    # AMPLIFIED NFL injury analysis for visual differentiation
    if sport in ["NFL", "americanfootball_nfl"]:
        # Apply NFL-specific position weighting
        home_weighted = _calculate_nfl_weighted_injuries(home_injuries)
        away_weighted = _calculate_nfl_weighted_injuries(away_injuries)

        # Use weighted scores if we have position data
        if home_weighted > 0 or away_weighted > 0:
            home_injury_score = home_weighted
            away_injury_score = away_weighted
            logger.info(f"[Execution] NFL weighted injuries: Home={home_weighted:.3f}, Away={away_weighted:.3f}")

        # Check for QB injuries specifically - GAME CHANGING (25-35% swing)
        home_qb_out = _check_qb_status(home_injuries)
        away_qb_out = _check_qb_status(away_injuries)

        if home_qb_out:
            home_injury_score += 0.50  # QB out = massive 50% impact
            reasoning_parts.append(f"CRITICAL: {home_team} QB situation impacted")
        if away_qb_out:
            away_injury_score += 0.50  # QB out = massive 50% impact
            reasoning_parts.append(f"CRITICAL: {away_team} QB situation impacted")

        # Additional impact for multiple key players out
        home_key_count = len(home_injuries.get("key_players_out", []))
        away_key_count = len(away_injuries.get("key_players_out", []))

        if home_key_count >= 3:
            home_injury_score += 0.15
            reasoning_parts.append(f"{home_team} decimated by injuries ({home_key_count} key players)")
        if away_key_count >= 3:
            away_injury_score += 0.15
            reasoning_parts.append(f"{away_team} decimated by injuries ({away_key_count} key players)")

    injury_differential = home_injury_score - away_injury_score

    # SOCCER-SPECIFIC: Use league standings and form
    # Match any soccer sport key (soccer_epl, soccer_england_efl_champ, etc.)
    is_soccer_sport = sport and ("soccer" in sport.lower() or sport.lower().startswith("soccer"))
    logger.info(f"[Execution] Sport check: sport={sport}, is_soccer={is_soccer_sport}, SOCCER_DATA_AVAILABLE={SOCCER_DATA_AVAILABLE}")

    if is_soccer_sport and SOCCER_DATA_AVAILABLE:
        try:
            logger.info(f"[Execution] Fetching soccer standings for {home_team} vs {away_team} (using={'Football-Data' if USING_FOOTBALL_DATA else 'API-Football'})...")

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

            logger.info(f"[Execution] Got standings: {len(standings) if standings else 0} teams")
            if standings:
                home_standing = None
                away_standing = None
                for name, data in standings.items():
                    if home_team.lower() in name.lower() or name.lower() in home_team.lower():
                        home_standing = data
                    if away_team.lower() in name.lower() or name.lower() in away_team.lower():
                        away_standing = data

                if home_standing and away_standing:
                    # Position differential (lower position = better)
                    home_pos = home_standing.get("position", 12)
                    away_pos = away_standing.get("position", 12)
                    pos_diff = (away_pos - home_pos) / 20  # Normalize to -0.5 to 0.5

                    # Goal difference differential
                    home_gd = home_standing.get("goal_difference", 0)
                    away_gd = away_standing.get("goal_difference", 0)
                    gd_diff = (home_gd - away_gd) / 30  # Normalize

                    # Form analysis (recent 5 games)
                    home_form = home_standing.get("form", "")
                    away_form = away_standing.get("form", "")
                    home_form_score = _calculate_soccer_form_score(home_form)
                    away_form_score = _calculate_soccer_form_score(away_form)
                    form_diff = (home_form_score - away_form_score) / 15  # Normalize

                    # Combine factors
                    soccer_adjustment = (pos_diff * 0.4) + (gd_diff * 0.3) + (form_diff * 0.3)

                    # Adjust injury scores based on soccer data
                    home_injury_score -= soccer_adjustment * 0.3
                    away_injury_score += soccer_adjustment * 0.3

                    if home_pos <= 4:
                        reasoning_parts.append(f"{home_team} in top 4 (pos {home_pos})")
                    elif home_pos >= 18:
                        reasoning_parts.append(f"{home_team} in relegation zone (pos {home_pos})")

                    if away_pos <= 4:
                        reasoning_parts.append(f"{away_team} in top 4 (pos {away_pos})")
                    elif away_pos >= 18:
                        reasoning_parts.append(f"{away_team} in relegation zone (pos {away_pos})")

                    if home_form:
                        reasoning_parts.append(f"{home_team} form: {home_form}")
                    if away_form:
                        reasoning_parts.append(f"{away_team} form: {away_form}")

                    logger.info(f"[Execution] Soccer context: Home pos={home_pos}, Away pos={away_pos}, adjustment={soccer_adjustment:.3f}")

        except Exception as e:
            logger.warning(f"[Execution] Soccer data fetch failed: {e}")

    weather_factor = 0.0
    is_outdoor = False

    if sport in ["NFL", "NCAAF", "americanfootball_nfl", "americanfootball_ncaaf"]:
        is_outdoor = venue.get("indoor", True) == False if venue else False
        if is_outdoor:
            # Could add weather API integration here
            weather_factor = 0.0

    base_score = 0.5

    # AMPLIFIED injury differential impact for visual differentiation
    # Goal: key injuries = 30-40% swing, QB out = 65-80% range
    if sport in ["NFL", "americanfootball_nfl"]:
        # Higher multiplier for NFL - injuries matter more
        injury_adjustment = injury_differential * 0.65
    else:
        injury_adjustment = injury_differential * 0.50

    score = base_score + injury_adjustment + weather_factor

    # Clamp but preserve extremes for visual impact
    score = max(0.15, min(0.85, score))  # Allow 15-85% range for dramatic injuries

    # Add reasoning based on injury counts
    if home_injuries['out_count'] > 0:
        reasoning_parts.append(f"{home_team}: {home_injuries['out_count']} out")
        if home_injuries.get("key_players_out"):
            reasoning_parts.append(f"Key: {', '.join(home_injuries['key_players_out'][:3])}")

    if away_injuries['out_count'] > 0:
        reasoning_parts.append(f"{away_team}: {away_injuries['out_count']} out")
        if away_injuries.get("key_players_out"):
            reasoning_parts.append(f"Key: {', '.join(away_injuries['key_players_out'][:3])}")

    if is_outdoor:
        reasoning_parts.append("Outdoor venue - weather factor")

    # If no injuries detected, provide context
    if not reasoning_parts:
        if home_injury_score == 0 and away_injury_score == 0:
            reasoning_parts.append("Both teams relatively healthy")
        else:
            reasoning_parts.append("Minor injury situations for both teams")

    return {
        "score": round(score, 3),
        "home_injury_impact": round(home_injury_score, 3),
        "away_injury_impact": round(away_injury_score, 3),
        "weather_factor": weather_factor,
        "breakdown": {
            "home_injuries": home_injuries,
            "away_injuries": away_injuries,
            "injury_differential": round(injury_differential, 3),
            "is_outdoor": is_outdoor
        },
        "reasoning": "; ".join(reasoning_parts)
    }


def _calculate_nfl_weighted_injuries(injuries: dict) -> float:
    """Calculate NFL-specific weighted injury score based on position importance."""
    if not injuries:
        return 0.0

    # AMPLIFIED scoring for visual differentiation
    base_score = injuries.get("impact_score", 0)

    # Key players out = significant impact (15% per key player, max 50%)
    key_count = len(injuries.get("key_players_out", []))
    if key_count > 0:
        # 15% for first key player, 12% for second, 10% for third, etc.
        key_impact = 0
        for i in range(key_count):
            key_impact += max(0.15 - (i * 0.03), 0.08)
        base_score += min(key_impact, 0.50)

    # Out count also matters (role players still impact)
    out_count = injuries.get("out_count", 0)
    if out_count > 5:
        base_score += 0.10  # Significant roster attrition

    return min(base_score, 1.0)


def _check_qb_status(injuries: dict) -> bool:
    """Check if QB is among injured players."""
    key_players = injuries.get("key_players_out", [])
    # Check for QB position indicator
    for player in key_players:
        # QB would typically be in key players list if injured
        if "QB" in str(player).upper():
            return True
    return False


def _calculate_soccer_form_score(form: str) -> int:
    """Calculate form score from form string (e.g., 'WWDLW')."""
    if not form:
        return 0
    score = 0
    for char in form.upper():
        if char == 'W':
            score += 3
        elif char == 'D':
            score += 1
        # L = 0
    return score


def get_execution_edge_direction(score: float) -> str:
    """Interpret the execution score."""
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "neutral"