"""
Pillar 3: Structural Stability & Information Shocks
Weight: 0.25

Measures: New information the market hasn't fully digested
- Breaking news (injury updates, lineup changes)
- Time since news broke vs time until game
- Line movement since news
"""
from datetime import datetime, timezone
from typing import Optional
import logging

from data_sources.espn import espn_client

logger = logging.getLogger(__name__)


def calculate_shocks_score(
    sport: str,
    home_team: str,
    away_team: str,
    game_time: datetime,
    current_line: Optional[float] = None,
    opening_line: Optional[float] = None,
    line_movement_history: Optional[list] = None
) -> dict:
    """
    Calculate Pillar 3: Structural Stability & Information Shocks score.
    
    A score > 0.5 means there may be undigested news FAVORING AWAY team
    A score < 0.5 means there may be undigested news FAVORING HOME team
    A score = 0.5 means market appears to have digested available info
    """
    now = datetime.now(timezone.utc)
    time_to_game = (game_time - now).total_seconds() / 3600
    
    home_injuries = espn_client.get_team_injury_impact(sport, home_team)
    away_injuries = espn_client.get_team_injury_impact(sport, away_team)
    
    shock_detected = False
    shock_direction = "neutral"
    shock_magnitude = 0.0
    reasoning_parts = []
    
    line_movement = 0.0
    movement_significance = 0.0
    
    if current_line is not None and opening_line is not None:
        line_movement = current_line - opening_line
        
        movement_thresholds = {
            "NFL": 2.5,
            "NCAAF": 3.0,
            "NBA": 3.0,
            "NCAAB": 3.5,
            "NHL": 0.5,
        }
        threshold = movement_thresholds.get(sport, 2.5)
        
        if abs(line_movement) >= threshold:
            shock_detected = True
            movement_significance = abs(line_movement) / threshold
            
            if line_movement > 0:
                shock_direction = "away"
                reasoning_parts.append(f"Significant line movement: +{line_movement:.1f} toward {away_team}")
            else:
                shock_direction = "home"
                reasoning_parts.append(f"Significant line movement: {line_movement:.1f} toward {home_team}")
        elif abs(line_movement) >= threshold * 0.5:
            reasoning_parts.append(f"Moderate line movement: {line_movement:+.1f}")
    
    key_player_shock = False
    
    if home_injuries["key_players_out"]:
        key_player_shock = True
        shock_magnitude += 0.2
        shock_direction = "away" if shock_direction == "neutral" else shock_direction
        reasoning_parts.append(f"Key {home_team} player(s) out: {', '.join(home_injuries['key_players_out'][:2])}")
    
    if away_injuries["key_players_out"]:
        key_player_shock = True
        shock_magnitude += 0.2
        if shock_direction == "neutral":
            shock_direction = "home"
        reasoning_parts.append(f"Key {away_team} player(s) out: {', '.join(away_injuries['key_players_out'][:2])}")
    
    if key_player_shock:
        shock_detected = True
    
    time_factor = 1.0
    if time_to_game < 1:
        time_factor = 1.5
        reasoning_parts.append("Very close to game time - limited adjustment window")
    elif time_to_game < 4:
        time_factor = 1.2
    elif time_to_game > 24:
        time_factor = 0.7
        if shock_detected:
            reasoning_parts.append("Game is 24+ hours away - market has time to adjust")
    
    base_score = 0.5
    
    if shock_detected:
        direction_multiplier = 1.0 if shock_direction == "away" else -1.0
        adjustment = min(shock_magnitude + movement_significance * 0.15, 0.4)
        adjustment *= direction_multiplier
        adjustment *= time_factor
        base_score += adjustment
    
    score = max(0.0, min(1.0, base_score))
    
    volatility = 0.0
    if line_movement_history and len(line_movement_history) >= 3:
        lines = [snap["line"] for snap in line_movement_history]
        avg_line = sum(lines) / len(lines)
        volatility = sum((l - avg_line) ** 2 for l in lines) / len(lines)
        
        if volatility > 1.0:
            reasoning_parts.append(f"High line volatility detected ({volatility:.2f})")
    
    if not reasoning_parts:
        reasoning_parts.append("No significant information shocks detected")
    
    return {
        "score": round(score, 3),
        "line_movement": round(line_movement, 2) if line_movement else 0.0,
        "shock_detected": shock_detected,
        "shock_direction": shock_direction,
        "breakdown": {
            "movement_significance": round(movement_significance, 3),
            "shock_magnitude": round(shock_magnitude, 3),
            "time_factor": round(time_factor, 3),
            "time_to_game_hours": round(time_to_game, 1),
            "volatility": round(volatility, 3),
            "home_key_players_out": home_injuries.get("key_players_out", []),
            "away_key_players_out": away_injuries.get("key_players_out", [])
        },
        "reasoning": "; ".join(reasoning_parts)
    }


def get_shock_edge_direction(score: float, shock_detected: bool) -> str:
    """Interpret the shocks score."""
    if not shock_detected:
        return "stable"
    
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "unstable"