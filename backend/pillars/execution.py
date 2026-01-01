"""
Pillar 1: Execution & Resolution Risk
Weight: 0.20

Measures: Who/what determines the outcome
- Player availability (injuries)
- Weather conditions (outdoor sports)
- Lineup uncertainty
"""
from datetime import datetime
from typing import Optional
import logging

from data_sources.espn import espn_client

logger = logging.getLogger(__name__)


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
    
    injury_differential = home_injury_score - away_injury_score
    
    weather_factor = 0.0
    is_outdoor = False
    
    if sport in ["NFL", "NCAAF"]:
        is_outdoor = venue.get("indoor", True) == False if venue else False
        if is_outdoor:
            weather_factor = 0.0
    
    base_score = 0.5
    injury_adjustment = injury_differential * 0.4
    
    score = base_score + injury_adjustment + weather_factor
    score = max(0.0, min(1.0, score))
    
    reasoning_parts = []
    
    if home_injury_score > 0.3:
        reasoning_parts.append(f"Home ({home_team}) has significant injuries: {home_injuries['out_count']} out")
        if home_injuries["key_players_out"]:
            reasoning_parts.append(f"Key players out: {', '.join(home_injuries['key_players_out'][:3])}")
    
    if away_injury_score > 0.3:
        reasoning_parts.append(f"Away ({away_team}) has significant injuries: {away_injuries['out_count']} out")
        if away_injuries["key_players_out"]:
            reasoning_parts.append(f"Key players out: {', '.join(away_injuries['key_players_out'][:3])}")
    
    if is_outdoor:
        reasoning_parts.append("Outdoor venue - weather could be a factor")
    
    if not reasoning_parts:
        reasoning_parts.append("No significant execution advantages for either team")
    
    return {
        "score": round(score, 3),
        "home_injury_impact": home_injury_score,
        "away_injury_impact": away_injury_score,
        "weather_factor": weather_factor,
        "breakdown": {
            "home_injuries": home_injuries,
            "away_injuries": away_injuries,
            "injury_differential": round(injury_differential, 3),
            "is_outdoor": is_outdoor
        },
        "reasoning": "; ".join(reasoning_parts)
    }


def get_execution_edge_direction(score: float) -> str:
    """Interpret the execution score."""
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "neutral"