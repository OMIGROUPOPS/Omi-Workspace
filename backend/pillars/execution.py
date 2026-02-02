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

# Import modules at module level, but check API keys at runtime
# This handles cases where env vars are set after module import (Railway/Docker)
_football_data_available = False
_api_football_available = False
_football_data_import_error = None
_api_football_import_error = None

try:
    from data_sources.football_data import get_epl_standings, get_standings_for_sport
    _football_data_available = True
    logger.info("[Execution INIT] football_data module imported successfully")
except Exception as e:
    _football_data_import_error = str(e)
    logger.error(f"[Execution INIT] football_data import FAILED: {e}")

try:
    from data_sources.api_football import get_league_standings_sync
    _api_football_available = True
    logger.info("[Execution INIT] api_football module imported successfully")
except Exception as e:
    _api_football_import_error = str(e)
    logger.error(f"[Execution INIT] api_football import FAILED: {e}")

logger.info(f"[Execution INIT] _football_data_available={_football_data_available}, _api_football_available={_api_football_available}")


def _normalize_team_name(name: str) -> str:
    """Normalize team name for matching by removing common suffixes."""
    name = name.lower().strip()
    # Remove common suffixes
    suffixes = [' fc', ' afc', ' united', ' city', ' town', ' wanderers', ' rovers', ' albion']
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    # Remove leading prefixes
    prefixes = ['afc ', 'fc ']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name.strip()


def _teams_match(search_name: str, standing_name: str) -> bool:
    """Check if two team names match, handling variations."""
    search_lower = search_name.lower().strip()
    standing_lower = standing_name.lower().strip()

    # Direct match
    if search_lower == standing_lower:
        return True

    # Substring match (either direction)
    if search_lower in standing_lower or standing_lower in search_lower:
        return True

    # Normalized match (remove FC, AFC, etc.)
    search_norm = _normalize_team_name(search_name)
    standing_norm = _normalize_team_name(standing_name)

    if search_norm == standing_norm:
        return True

    # Partial normalized match
    if search_norm in standing_norm or standing_norm in search_norm:
        return True

    # Handle specific edge cases
    # "Nott'm Forest" vs "Nottingham Forest"
    if "nott" in search_norm and "nott" in standing_norm:
        return True
    if "forest" in search_norm and "forest" in standing_norm:
        return True

    return False


def _get_soccer_data_source():
    """
    Determine which soccer data source to use at runtime.
    Checks env vars each time to handle late-loaded environment variables.
    """
    has_fd_key = bool(os.getenv("FOOTBALL_DATA_API_KEY"))
    has_af_key = bool(os.getenv("API_FOOTBALL_KEY"))

    logger.info(f"[Execution] _get_soccer_data_source: _football_data_available={_football_data_available}, has_fd_key={has_fd_key}")
    logger.info(f"[Execution] _get_soccer_data_source: _api_football_available={_api_football_available}, has_af_key={has_af_key}")

    if _football_data_available and has_fd_key:
        return "football_data"
    if _api_football_available and has_af_key:
        return "api_football"

    # Log why we're returning None
    if not _football_data_available and _football_data_import_error:
        logger.warning(f"[Execution] football_data not available: {_football_data_import_error}")
    if not _api_football_available and _api_football_import_error:
        logger.warning(f"[Execution] api_football not available: {_api_football_import_error}")

    return None

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
    # Determine soccer data source at runtime (handles late-loaded env vars)
    soccer_source = _get_soccer_data_source()

    # Debug logging
    logger.info(f"[Execution] ===== CALLED =====")
    logger.info(f"[Execution] sport={sport}, home={home_team}, away={away_team}")
    logger.info(f"[Execution] soccer_source={soccer_source}")
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
    soccer_adjustment = 0.0  # Initialize outside try block
    logger.info(f"[Execution] Sport check: sport={sport}, is_soccer={is_soccer_sport}, soccer_source={soccer_source}")

    if is_soccer_sport and soccer_source:
        try:
            logger.info(f"[Execution] Fetching soccer standings for {home_team} vs {away_team} (using={soccer_source}, sport={sport})...")

            # Use the appropriate API based on which key is available
            # All functions are now synchronous - no asyncio needed
            standings = None
            if soccer_source == "football_data":
                # Use sport-aware function to get correct league standings
                standings = get_standings_for_sport(sport)
            elif soccer_source == "api_football":
                standings = get_league_standings_sync()

            logger.info(f"[Execution] Got standings: {len(standings) if standings else 0} teams")
            if standings:
                # Log available team names for debugging
                logger.info(f"[Execution] Looking for: home='{home_team}', away='{away_team}'")
                logger.info(f"[Execution] Available teams: {list(standings.keys())}")

                home_standing = None
                away_standing = None
                for name, data in standings.items():
                    if _teams_match(home_team, name):
                        home_standing = data
                        logger.info(f"[Execution] MATCHED home: '{home_team}' -> '{name}' (pos {data.get('position')})")
                    if _teams_match(away_team, name):
                        away_standing = data
                        logger.info(f"[Execution] MATCHED away: '{away_team}' -> '{name}' (pos {data.get('position')})")

                if not home_standing:
                    logger.warning(f"[Execution] NO MATCH for home team: '{home_team}' (normalized: '{_normalize_team_name(home_team)}')")
                if not away_standing:
                    logger.warning(f"[Execution] NO MATCH for away team: '{away_team}' (normalized: '{_normalize_team_name(away_team)}')")

                if home_standing and away_standing:
                    # Position differential (lower position = better)
                    # Positive = home team better, negative = away team better
                    home_pos = home_standing.get("position", 12)
                    away_pos = away_standing.get("position", 12)
                    pos_gap = away_pos - home_pos  # Positive if home is higher in table

                    # AMPLIFIED position impact: 8 position gap = 20% swing
                    # Scale: each position difference = 2.5% swing
                    pos_adjustment = pos_gap * 0.025

                    # Goal difference differential - secondary factor
                    home_gd = home_standing.get("goal_difference", 0)
                    away_gd = away_standing.get("goal_difference", 0)
                    gd_gap = home_gd - away_gd  # Positive if home has better GD

                    # GD impact: 10 GD difference = 10% swing
                    gd_adjustment = min(max(gd_gap / 100, -0.15), 0.15)

                    # Form analysis (recent 5 games) - W=3, D=1, L=0
                    home_form = home_standing.get("form", "")
                    away_form = away_standing.get("form", "")
                    home_form_score = _calculate_soccer_form_score(home_form)
                    away_form_score = _calculate_soccer_form_score(away_form)
                    form_gap = home_form_score - away_form_score  # Max 15 (all W vs all L)

                    # Form impact: 15 point form gap = 15% swing
                    form_adjustment = form_gap * 0.01

                    # DIRECT soccer adjustment to final score
                    # Weight: Position 50%, GD 25%, Form 25%
                    soccer_adjustment = (pos_adjustment * 0.50) + (gd_adjustment * 0.25) + (form_adjustment * 0.25)

                    # soccer_adjustment is NEGATIVE when home is better (lower score = home advantage)
                    # Positive adjustment = away is better (higher score = away advantage)
                    # Will be applied directly to final score below
                    logger.info(f"[Execution] soccer_adjustment calculated: {soccer_adjustment:.3f}")

                    # Build detailed reasoning
                    reasoning_parts.append(f"Position: {home_team} {home_pos}th vs {away_team} {away_pos}th")

                    if abs(pos_gap) >= 5:
                        if pos_gap > 0:
                            reasoning_parts.append(f"SIGNIFICANT: {away_team} {abs(pos_gap)} places lower")
                        else:
                            reasoning_parts.append(f"SIGNIFICANT: {home_team} {abs(pos_gap)} places lower")

                    if home_pos <= 6:
                        reasoning_parts.append(f"{home_team} in promotion/European zone")
                    elif home_pos >= 18:
                        reasoning_parts.append(f"{home_team} in RELEGATION ZONE")
                    elif home_pos >= 15:
                        reasoning_parts.append(f"{home_team} in relegation danger")

                    if away_pos <= 6:
                        reasoning_parts.append(f"{away_team} in promotion/European zone")
                    elif away_pos >= 18:
                        reasoning_parts.append(f"{away_team} in RELEGATION ZONE")
                    elif away_pos >= 15:
                        reasoning_parts.append(f"{away_team} in relegation danger")

                    if home_form and away_form:
                        reasoning_parts.append(f"Form: {home_team} {home_form} ({home_form_score}pts) vs {away_team} {away_form} ({away_form_score}pts)")
                    elif home_form:
                        reasoning_parts.append(f"{home_team} form: {home_form}")
                    elif away_form:
                        reasoning_parts.append(f"{away_team} form: {away_form}")

                    if gd_gap != 0:
                        reasoning_parts.append(f"GD: {home_team} {home_gd:+d} vs {away_team} {away_gd:+d}")

                    logger.info(f"[Execution] Soccer: pos_gap={pos_gap}, gd_gap={gd_gap}, form_gap={form_gap}")
                    logger.info(f"[Execution] Adjustments: pos={pos_adjustment:.3f}, gd={gd_adjustment:.3f}, form={form_adjustment:.3f}")
                    logger.info(f"[Execution] Total soccer_adjustment={soccer_adjustment:.3f}")

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

    # Apply all adjustments to score
    # soccer_adjustment: negative = home advantage, positive = away advantage
    # We SUBTRACT because lower score = home advantage
    score = base_score + injury_adjustment + weather_factor - soccer_adjustment

    logger.info(f"[Execution] Score calc: base={base_score}, injury_adj={injury_adjustment:.3f}, weather={weather_factor}, soccer_adj={soccer_adjustment:.3f}")
    logger.info(f"[Execution] Final score before clamp: {score:.3f}")

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

    logger.info(f"[Execution] FINAL RETURN: score={score:.3f}, soccer_adj={soccer_adjustment:.3f}")

    return {
        "score": round(score, 3),
        "home_injury_impact": round(home_injury_score, 3),
        "away_injury_impact": round(away_injury_score, 3),
        "weather_factor": weather_factor,
        "soccer_adjustment": round(soccer_adjustment, 3),
        "breakdown": {
            "home_injuries": home_injuries,
            "away_injuries": away_injuries,
            "injury_differential": round(injury_differential, 3),
            "is_outdoor": is_outdoor,
            "soccer_adjustment": round(soccer_adjustment, 3)
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