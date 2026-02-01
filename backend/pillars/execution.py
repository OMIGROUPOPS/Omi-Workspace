"""
Pillar 1: Execution & Resolution Risk
Weight: 0.20

Measures: Who/what determines the outcome
- Player availability (injuries)
- Weather conditions (outdoor sports)
- Lineup uncertainty
- NFL position importance weighting
"""
from datetime import datetime
from typing import Optional
import logging

from data_sources.espn import espn_client

logger = logging.getLogger(__name__)

# NFL position importance weights (higher = more impactful when injured)
NFL_POSITION_WEIGHTS = {
    "QB": 5.0,    # Quarterback is most important
    "LT": 2.5,    # Left tackle protects blind side
    "RT": 2.0,
    "WR": 1.8,
    "RB": 1.5,
    "TE": 1.3,
    "CB": 2.0,    # Cornerbacks critical vs pass
    "EDGE": 2.2,  # Pass rushers
    "DE": 2.0,
    "DT": 1.5,
    "LB": 1.5,
    "S": 1.5,
    "K": 1.0,
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
    home_injuries = espn_client.get_team_injury_impact(sport, home_team)
    away_injuries = espn_client.get_team_injury_impact(sport, away_team)

    home_injury_score = home_injuries["impact_score"]
    away_injury_score = away_injuries["impact_score"]

    reasoning_parts = []

    # Enhanced NFL injury analysis
    if sport in ["NFL", "americanfootball_nfl"]:
        # Apply NFL-specific position weighting
        home_weighted = _calculate_nfl_weighted_injuries(home_injuries)
        away_weighted = _calculate_nfl_weighted_injuries(away_injuries)

        # Use weighted scores if we have position data
        if home_weighted > 0 or away_weighted > 0:
            home_injury_score = home_weighted
            away_injury_score = away_weighted
            logger.info(f"[Execution] NFL weighted injuries: Home={home_weighted:.3f}, Away={away_weighted:.3f}")

        # Check for QB injuries specifically (game-changing)
        home_qb_out = _check_qb_status(home_injuries)
        away_qb_out = _check_qb_status(away_injuries)

        if home_qb_out:
            home_injury_score += 0.3
            reasoning_parts.append(f"{home_team} QB situation impacted")
        if away_qb_out:
            away_injury_score += 0.3
            reasoning_parts.append(f"{away_team} QB situation impacted")

    injury_differential = home_injury_score - away_injury_score

    weather_factor = 0.0
    is_outdoor = False

    if sport in ["NFL", "NCAAF", "americanfootball_nfl", "americanfootball_ncaaf"]:
        is_outdoor = venue.get("indoor", True) == False if venue else False
        if is_outdoor:
            # Could add weather API integration here
            weather_factor = 0.0

    base_score = 0.5

    # Amplify injury differential impact for NFL
    if sport in ["NFL", "americanfootball_nfl"]:
        injury_adjustment = injury_differential * 0.5  # Higher multiplier for NFL
    else:
        injury_adjustment = injury_differential * 0.4

    score = base_score + injury_adjustment + weather_factor
    score = max(0.0, min(1.0, score))

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

    # This would ideally use detailed injury data with positions
    # For now, use the base score but could be enhanced with position data
    base_score = injuries.get("impact_score", 0)

    # Boost score if key players are out
    key_count = len(injuries.get("key_players_out", []))
    if key_count > 0:
        base_score += key_count * 0.1

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


def get_execution_edge_direction(score: float) -> str:
    """Interpret the execution score."""
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "neutral"