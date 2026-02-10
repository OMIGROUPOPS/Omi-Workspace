"""
Pillar 3: Structural Stability & Information Shocks
Weight: 0.25

Measures: Market reaction to new information via line movement
- Line movement magnitude (opening vs current)
- Line movement velocity (pts/hr from snapshots)
- Steam move detection (velocity > 1.0 pts/hr)
- Time factor (hours until game multiplier)
- Volatility detection (variance across snapshots)

# NOTE: Injury signals removed in P1. Injuries are handled by the Execution pillar.
# Shocks measures market reaction (line movement, velocity, steam moves) not the underlying news.
"""
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def calculate_shocks_score(
    sport: str,
    home_team: str,
    away_team: str,
    game_time: datetime,
    current_line: Optional[float] = None,
    opening_line: Optional[float] = None,
    line_movement_history: Optional[list] = None,
    market_type: str = "spread"
) -> dict:
    """
    Calculate Pillar 3: Structural Stability & Information Shocks score.

    For SPREAD/MONEYLINE:
    - score > 0.5: Line moved toward AWAY (sharp money on away)
    - score < 0.5: Line moved toward HOME (sharp money on home)

    For TOTALS:
    - score > 0.5: Total moved UP (sharp money on over)
    - score < 0.5: Total moved DOWN (sharp money on under)

    A score = 0.5 means no significant line movement detected
    """
    now = datetime.now(timezone.utc)
    time_to_game = (game_time - now).total_seconds() / 3600

    shock_detected = False
    shock_direction = "neutral"
    reasoning_parts = []

    line_movement = 0.0
    movement_significance = 0.0

    # === LINE MOVEMENT MAGNITUDE (opening vs current) ===
    # Calibrated thresholds for spread movements:
    # 0-1 pt:   barely notable (50-55%)
    # 1-3 pt:   moderate (55-65%)
    # 3-5 pt:   significant (65-75%)
    # 5-10 pt:  major (75-85%)
    # 10+ pt:   extreme (85-95%) - very rare, usually injury/news driven
    if current_line is not None and opening_line is not None:
        line_movement = current_line - opening_line
        abs_movement = abs(line_movement)

        if abs_movement >= 10.0:
            # EXTREME line movement (10+ pts) - 85-95% range
            shock_detected = True
            # 10pt = 0.35, 15pt = 0.40, 20pt = 0.45 (capped)
            movement_significance = 0.35 + min((abs_movement - 10.0) * 0.02, 0.10)

            if line_movement > 0:
                shock_direction = "away"
                reasoning_parts.append(f"EXTREME line move: +{line_movement:.1f} toward {away_team}")
            else:
                shock_direction = "home"
                reasoning_parts.append(f"EXTREME line move: {line_movement:.1f} toward {home_team}")

        elif abs_movement >= 5.0:
            # MAJOR line movement (5-10 pts) - 75-85% range
            shock_detected = True
            # 5pt = 0.25, 7.5pt = 0.30, 10pt = 0.35
            movement_significance = 0.25 + (abs_movement - 5.0) * 0.02

            if line_movement > 0:
                shock_direction = "away"
                reasoning_parts.append(f"MAJOR line move: +{line_movement:.1f} toward {away_team}")
            else:
                shock_direction = "home"
                reasoning_parts.append(f"MAJOR line move: {line_movement:.1f} toward {home_team}")

        elif abs_movement >= 3.0:
            # Significant line movement (3-5 pts) - 65-75% range
            shock_detected = True
            # 3pt = 0.15, 4pt = 0.20, 5pt = 0.25
            movement_significance = 0.15 + (abs_movement - 3.0) * 0.05

            if line_movement > 0:
                shock_direction = "away"
                reasoning_parts.append(f"Significant line move: +{line_movement:.1f} toward {away_team}")
            else:
                shock_direction = "home"
                reasoning_parts.append(f"Significant line move: {line_movement:.1f} toward {home_team}")

        elif abs_movement >= 1.0:
            # Moderate line movement (1-3 pts) - 55-65% range
            shock_detected = True
            # 1pt = 0.05, 2pt = 0.10, 3pt = 0.15
            movement_significance = 0.05 + (abs_movement - 1.0) * 0.05

            if line_movement > 0:
                shock_direction = "away"
                reasoning_parts.append(f"Moderate line move: +{line_movement:.1f} toward {away_team}")
            else:
                shock_direction = "home"
                reasoning_parts.append(f"Moderate line move: {line_movement:.1f} toward {home_team}")

        elif abs_movement >= 0.5:
            # Slight movement (0.5-1 pts) - 52-55% range
            movement_significance = 0.02 + (abs_movement - 0.5) * 0.06  # 2-5%
            if line_movement > 0:
                reasoning_parts.append(f"Slight line move: +{line_movement:.1f} toward {away_team}")
            else:
                reasoning_parts.append(f"Slight line move: {line_movement:.1f} toward {home_team}")

    # === TIME FACTOR (hours until game) ===
    time_factor = 1.0
    if time_to_game < 1:
        time_factor = 1.5
        if shock_detected:
            reasoning_parts.append("Very close to game time - limited adjustment window")
    elif time_to_game < 4:
        time_factor = 1.2
    elif time_to_game > 24:
        time_factor = 0.7
        if shock_detected:
            reasoning_parts.append("Game is 24+ hours away - market has time to adjust")

    # === BASE SCORE CALCULATION ===
    base_score = 0.5

    # Apply line movement adjustments
    # Cap at 0.45 to allow extreme moves to reach 95% max
    if shock_detected:
        direction_multiplier = 1.0 if shock_direction == "away" else -1.0
        adjustment = min(movement_significance, 0.45)
        adjustment *= direction_multiplier
        adjustment *= time_factor
        base_score += adjustment

    # === LINE MOVEMENT VELOCITY ANALYSIS ===
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

                # Sharp move detection thresholds
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

        # === VOLATILITY DETECTION ===
        if len(lines) >= 3:
            avg_line = sum(lines) / len(lines)
            volatility = sum((l - avg_line) ** 2 for l in lines) / len(lines)

            if volatility > 1.0:
                reasoning_parts.append(f"High line volatility ({volatility:.2f})")

    # Clamp final score
    score = max(0.0, min(1.0, base_score))

    if not reasoning_parts:
        reasoning_parts.append("No significant line movement detected")

    # Diagnostic: warn when returning default 50 due to missing data
    if score == 0.5:
        if current_line is None and opening_line is None:
            logger.warning(f"[Shocks] WARNING: Returning default 0.5 — no opening_line or current_line available for {away_team} @ {home_team}")
            logger.warning(f"[Shocks]   line_movement_history has {len(line_movement_history) if line_movement_history else 0} snapshots")
        elif not line_movement_history or len(line_movement_history) < 2:
            logger.warning(f"[Shocks] WARNING: Returning 0.5 — only {len(line_movement_history) if line_movement_history else 0} snapshots (need >=2 for velocity)")
        else:
            logger.info(f"[Shocks] Score 0.5 with data present — genuinely balanced line movement")

    # Calculate market-specific scores
    # SPREAD/MONEYLINE: Line moved toward home or away? (score as calculated)
    # TOTALS: Total moved up or down? (same directional logic applies)
    market_scores = {}
    market_scores["spread"] = score
    market_scores["moneyline"] = score  # Same signal for ML

    # TOTALS: If there's line movement data, the shocks score indicates sharp money direction
    # For totals, this indicates whether sharps are on over or under
    # We use the same score because line movement velocity/magnitude applies similarly
    # However, we could adjust based on total line movement specifically if available
    market_scores["totals"] = score

    logger.info(f"[Shocks] Market scores: spread={score:.3f}, totals={score:.3f}")

    return {
        "score": round(score, 3),
        "market_scores": {k: round(v, 3) for k, v in market_scores.items()},
        "line_movement": round(line_movement, 2) if line_movement else 0.0,
        "shock_detected": shock_detected or sharp_move_detected,
        "shock_direction": shock_direction,
        "breakdown": {
            "movement_significance": round(movement_significance, 3),
            "time_factor": round(time_factor, 3),
            "time_to_game_hours": round(time_to_game, 1),
            "volatility": round(volatility, 3),
            "velocity": round(velocity, 3),
            "sharp_move_detected": sharp_move_detected,
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
