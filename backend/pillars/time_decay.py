"""
Pillar 4: Time, Fatigue & Attention Decay
Weight: 0.15

Measures: Timing asymmetries between teams
- Days of rest
- Back-to-back games
- Travel distance and road trips
- Schedule density (3rd game in 4 nights, etc.)
"""
from datetime import datetime
import logging

from data_sources.espn import espn_client

logger = logging.getLogger(__name__)

SPORT_REST_IMPORTANCE = {
    "NFL": 0.3,
    "NCAAF": 0.3,
    "NBA": 1.0,
    "NCAAB": 0.8,
    "NHL": 0.9,
}


def calculate_time_decay_score(
    sport: str,
    home_team: str,
    away_team: str,
    game_time: datetime
) -> dict:
    """
    Calculate Pillar 4: Time, Fatigue & Attention Decay score.
    
    A score > 0.5 means AWAY team has rest/timing advantage
    A score < 0.5 means HOME team has rest/timing advantage
    A score = 0.5 means balanced rest situation
    """
    home_rest = espn_client.calculate_rest_and_travel(sport, home_team, game_time)
    away_rest = espn_client.calculate_rest_and_travel(sport, away_team, game_time)
    
    home_fatigue = home_rest["fatigue_score"]
    away_fatigue = away_rest["fatigue_score"]
    
    importance = SPORT_REST_IMPORTANCE.get(sport, 0.5)
    
    fatigue_differential = (home_fatigue - away_fatigue) * importance
    
    situational_adjustment = 0.0
    reasoning_parts = []
    
    if home_rest["is_back_to_back"]:
        situational_adjustment += 0.15
        reasoning_parts.append(f"{home_team} on back-to-back")
    if away_rest["is_back_to_back"]:
        situational_adjustment -= 0.15
        reasoning_parts.append(f"{away_team} on back-to-back")
    
    if home_rest["is_third_in_four"]:
        situational_adjustment += 0.1
        reasoning_parts.append(f"{home_team} playing 3rd game in 4 nights")
    if away_rest["is_third_in_four"]:
        situational_adjustment -= 0.1
        reasoning_parts.append(f"{away_team} playing 3rd game in 4 nights")
    
    rest_diff = home_rest["days_rest"] - away_rest["days_rest"]
    if rest_diff <= -2:
        situational_adjustment += 0.1
        reasoning_parts.append(f"Rest disparity: {home_team} {home_rest['days_rest']}d vs {away_team} {away_rest['days_rest']}d")
    elif rest_diff >= 2:
        situational_adjustment -= 0.1
        reasoning_parts.append(f"Rest advantage: {home_team} {home_rest['days_rest']}d vs {away_team} {away_rest['days_rest']}d")
    
    if away_rest["travel_situation"] == "road_trip":
        situational_adjustment -= 0.05
        reasoning_parts.append(f"{away_team} on extended road trip")
    if home_rest["travel_situation"] == "home_stand":
        situational_adjustment -= 0.03
        reasoning_parts.append(f"{home_team} on home stand")
    
    base_score = 0.5
    score = base_score + fatigue_differential + situational_adjustment
    score = max(0.0, min(1.0, score))
    
    if not reasoning_parts:
        if abs(fatigue_differential) < 0.05:
            reasoning_parts.append("Similar rest situations for both teams")
        elif fatigue_differential > 0:
            reasoning_parts.append(f"{away_team} has slight rest advantage")
        else:
            reasoning_parts.append(f"{home_team} has slight rest advantage")
    
    return {
        "score": round(score, 3),
        "home_fatigue": round(home_fatigue, 3),
        "away_fatigue": round(away_fatigue, 3),
        "home_rest_days": home_rest["days_rest"],
        "away_rest_days": away_rest["days_rest"],
        "breakdown": {
            "home_rest": home_rest,
            "away_rest": away_rest,
            "fatigue_differential": round(fatigue_differential, 3),
            "situational_adjustment": round(situational_adjustment, 3),
            "sport_importance": importance
        },
        "reasoning": "; ".join(reasoning_parts)
    }


def get_fatigue_edge_direction(score: float) -> str:
    """Interpret the time decay score."""
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "neutral"