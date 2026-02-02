"""
Pillar 3: Structural Stability & Information Shocks
Weight: 0.25

Measures: New information the market hasn't fully digested
- Breaking news (injury updates, lineup changes)
- Time since news broke vs time until game
- Line movement since news
- Soccer: Key player injuries from API-Football
"""
from datetime import datetime, timezone
from typing import Optional
import logging

from data_sources.espn import espn_client

logger = logging.getLogger(__name__)

# Try to import soccer data sources
# For injuries, we need API-Football (Football-Data doesn't have injury data)
import os

# Import modules at module level, but check API keys at runtime
# This handles cases where env vars are set after module import (Railway/Docker)
_api_football_available = False
_api_football_import_error = None

try:
    from data_sources.api_football import get_team_injuries, get_team_id
    _api_football_available = True
    logger.info("[Shocks INIT] api_football module imported successfully")
except Exception as e:
    _api_football_import_error = str(e)
    logger.error(f"[Shocks INIT] api_football import FAILED: {e}")

logger.info(f"[Shocks INIT] _api_football_available={_api_football_available}")


def _is_soccer_injuries_available():
    """Check if soccer injury data is available at runtime."""
    has_key = bool(os.getenv("API_FOOTBALL_KEY"))
    logger.info(f"[Shocks] _is_soccer_injuries_available: _api_football_available={_api_football_available}, has_key={has_key}")
    return _api_football_available and has_key


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

        # AMPLIFIED thresholds for visual impact
        # Line move > 1pt = significant, > 2pt = major
        abs_movement = abs(line_movement)

        if abs_movement >= 2.0:
            # MAJOR line movement - 70-80% range
            shock_detected = True
            movement_significance = 0.25 + (abs_movement - 2.0) * 0.05  # 25-30%+

            if line_movement > 0:
                shock_direction = "away"
                reasoning_parts.append(f"MAJOR line move: +{line_movement:.1f} toward {away_team}")
            else:
                shock_direction = "home"
                reasoning_parts.append(f"MAJOR line move: {line_movement:.1f} toward {home_team}")

        elif abs_movement >= 1.0:
            # Significant line movement - 60-70% range
            shock_detected = True
            movement_significance = 0.12 + (abs_movement - 1.0) * 0.13  # 12-25%

            if line_movement > 0:
                shock_direction = "away"
                reasoning_parts.append(f"Significant line move: +{line_movement:.1f} toward {away_team}")
            else:
                shock_direction = "home"
                reasoning_parts.append(f"Significant line move: {line_movement:.1f} toward {home_team}")

        elif abs_movement >= 0.5:
            # Moderate movement - 55-60% range
            movement_significance = 0.05 + (abs_movement - 0.5) * 0.14  # 5-12%
            if line_movement > 0:
                reasoning_parts.append(f"Moderate line move: +{line_movement:.1f} toward {away_team}")
            else:
                reasoning_parts.append(f"Moderate line move: {line_movement:.1f} toward {home_team}")
    
    key_player_shock = False

    # SOCCER-SPECIFIC: Fetch injuries from API-Football
    soccer_injury_shock = False
    soccer_injury_adjustment = 0.0
    is_soccer_sport = sport and ("soccer" in sport.lower() or sport.lower().startswith("soccer"))
    soccer_injuries_available = _is_soccer_injuries_available()
    logger.info(f"[Shocks] Sport check: sport={sport}, is_soccer={is_soccer_sport}, soccer_injuries_available={soccer_injuries_available}")

    if is_soccer_sport and soccer_injuries_available:
        try:
            home_team_id = get_team_id(home_team)
            away_team_id = get_team_id(away_team)
            logger.info(f"[Shocks] Soccer team IDs: home={home_team_id}, away={away_team_id}")

            home_soccer_injuries = []
            away_soccer_injuries = []

            # All functions are now synchronous - no asyncio needed
            if home_team_id:
                home_soccer_injuries = get_team_injuries(home_team_id) or []
            if away_team_id:
                away_soccer_injuries = get_team_injuries(away_team_id) or []

            home_injury_count = len(home_soccer_injuries)
            away_injury_count = len(away_soccer_injuries)
            injury_diff = home_injury_count - away_injury_count

            logger.info(f"[Shocks] Soccer injuries: home={home_injury_count}, away={away_injury_count}, diff={injury_diff}")

            # Only count as shock if there's a meaningful difference
            if abs(injury_diff) >= 3:
                soccer_injury_shock = True

                # More injuries = disadvantage for that team
                # Positive diff (home has more) = away advantage (score > 0.5)
                # Scale: 10 injury difference = 10% swing, max 20%
                soccer_injury_adjustment = min(max(injury_diff / 100, -0.20), 0.20)

                if injury_diff > 0:
                    shock_direction = "away"  # Home has more injuries, favors away
                    reasoning_parts.append(f"INJURY EDGE: {home_team} has {injury_diff} more injuries than {away_team}")
                else:
                    shock_direction = "home"  # Away has more injuries, favors home
                    reasoning_parts.append(f"INJURY EDGE: {away_team} has {abs(injury_diff)} more injuries than {home_team}")

                reasoning_parts.append(f"Injuries: {home_team} {home_injury_count} vs {away_team} {away_injury_count}")

            elif home_injury_count > 0 or away_injury_count > 0:
                # Minor note if injuries exist but no significant difference
                reasoning_parts.append(f"Injuries similar: {home_team} {home_injury_count} vs {away_team} {away_injury_count}")

        except Exception as e:
            logger.warning(f"[Shocks] Soccer injury fetch failed: {e}")

    # AMPLIFIED injury impact for visual differentiation
    # Key player out = 15-25% swing per player
    home_key_count = len(home_injuries.get("key_players_out", []))
    away_key_count = len(away_injuries.get("key_players_out", []))

    if home_injuries["key_players_out"]:
        key_player_shock = True
        # 15% base + 10% per additional key player (max 35%)
        injury_impact = min(0.15 + (home_key_count - 1) * 0.10, 0.35)
        shock_magnitude += injury_impact
        shock_direction = "away" if shock_direction == "neutral" else shock_direction
        reasoning_parts.append(f"KEY OUT {home_team}: {', '.join(home_injuries['key_players_out'][:3])}")

    if away_injuries["key_players_out"]:
        key_player_shock = True
        # 15% base + 10% per additional key player (max 35%)
        injury_impact = min(0.15 + (away_key_count - 1) * 0.10, 0.35)
        shock_magnitude += injury_impact
        if shock_direction == "neutral":
            shock_direction = "home"
        reasoning_parts.append(f"KEY OUT {away_team}: {', '.join(away_injuries['key_players_out'][:3])}")
    
    if key_player_shock:
        shock_detected = True

    # Soccer injury differential also counts as a shock
    if soccer_injury_shock:
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

    # Apply standard shock adjustments
    if shock_detected:
        direction_multiplier = 1.0 if shock_direction == "away" else -1.0
        adjustment = min(shock_magnitude + movement_significance * 0.15, 0.4)
        adjustment *= direction_multiplier
        adjustment *= time_factor
        base_score += adjustment

    # Apply soccer-specific injury adjustment (already accounts for direction)
    if soccer_injury_adjustment != 0:
        base_score += soccer_injury_adjustment
        logger.info(f"[Shocks] Applied soccer_injury_adjustment={soccer_injury_adjustment:.3f}")

    score = max(0.0, min(1.0, base_score))
    
    # Enhanced line movement velocity analysis
    volatility = 0.0
    velocity = 0.0
    sharp_move_detected = False

    if line_movement_history and len(line_movement_history) >= 2:
        # Sort by timestamp
        sorted_history = sorted(line_movement_history, key=lambda x: x.get("timestamp", ""))
        lines = [snap.get("line", 0) for snap in sorted_history if snap.get("line") is not None]

        if len(lines) >= 2:
            # Calculate velocity (points per hour)
            first_snap = sorted_history[0]
            last_snap = sorted_history[-1]

            try:
                t1 = datetime.fromisoformat(first_snap.get("timestamp", "").replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(last_snap.get("timestamp", "").replace("Z", "+00:00"))
                hours_elapsed = max((t2 - t1).total_seconds() / 3600, 0.1)

                total_movement = lines[-1] - lines[0]
                velocity = total_movement / hours_elapsed

                # AMPLIFIED sharp move detection for visual impact
                # >0.3 pts/hr = notable, >0.5 pts/hr = sharp, >1.0 pts/hr = steam
                if abs(velocity) >= 1.0:
                    sharp_move_detected = True
                    direction = "toward away" if velocity > 0 else "toward home"
                    reasoning_parts.append(f"STEAM MOVE: {velocity:+.2f} pts/hr ({direction})")

                    # Steam move = 15-25% adjustment
                    sharp_adjustment = 0.15 + min((abs(velocity) - 1.0) * 0.10, 0.10)
                    if velocity > 0:
                        base_score += sharp_adjustment
                    else:
                        base_score -= sharp_adjustment

                elif abs(velocity) > 0.5:
                    sharp_move_detected = True
                    direction = "toward away" if velocity > 0 else "toward home"
                    reasoning_parts.append(f"SHARP: {velocity:+.2f} pts/hr ({direction})")

                    # Sharp move = 8-15% adjustment
                    sharp_adjustment = 0.08 + (abs(velocity) - 0.5) * 0.14
                    if velocity > 0:
                        base_score += sharp_adjustment
                    else:
                        base_score -= sharp_adjustment

                elif abs(velocity) > 0.3:
                    direction = "toward away" if velocity > 0 else "toward home"
                    reasoning_parts.append(f"Line moving: {velocity:+.2f} pts/hr ({direction})")
            except Exception as e:
                logger.warning(f"Error calculating velocity: {e}")

        if len(lines) >= 3:
            avg_line = sum(lines) / len(lines)
            volatility = sum((l - avg_line) ** 2 for l in lines) / len(lines)

            if volatility > 1.0:
                reasoning_parts.append(f"High line volatility ({volatility:.2f})")
    
    if not reasoning_parts:
        reasoning_parts.append("No significant information shocks detected")
    
    return {
        "score": round(score, 3),
        "line_movement": round(line_movement, 2) if line_movement else 0.0,
        "shock_detected": shock_detected or sharp_move_detected,
        "shock_direction": shock_direction,
        "breakdown": {
            "movement_significance": round(movement_significance, 3),
            "shock_magnitude": round(shock_magnitude, 3),
            "time_factor": round(time_factor, 3),
            "time_to_game_hours": round(time_to_game, 1),
            "volatility": round(volatility, 3),
            "velocity": round(velocity, 3),
            "sharp_move_detected": sharp_move_detected,
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