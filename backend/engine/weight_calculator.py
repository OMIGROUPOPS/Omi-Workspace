"""
Weight Calculator Module

Calculates market-specific AND period-specific pillar weights.
Base pillar scores are game-level truths (injuries exist, lines moved),
but weights vary by market/period context.

Market Types:
- spread: Will favorite cover the point spread?
- totals: Over or under the total?
- moneyline: Who wins straight up?

Periods:
- full: Full game
- h1, h2: 1st/2nd half
- q1-q4: Quarters (basketball/football)
- p1-p3: Periods (hockey)
"""

import logging
from typing import Dict, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SPORT_WEIGHTS,
    DEFAULT_WEIGHTS,
    MARKET_ADJUSTMENTS,
    PERIOD_ADJUSTMENTS,
    SPORT_PERIOD_AVAILABILITY,
    EDGE_THRESHOLDS,
)

logger = logging.getLogger(__name__)

# Pillar keys (for iteration)
PILLAR_KEYS = ["execution", "incentives", "shocks", "time_decay", "flow", "game_environment"]


def get_effective_weights(
    sport: str,
    market_type: str = "spread",
    period: str = "full"
) -> Dict[str, float]:
    """
    Compute final pillar weights by applying market and period adjustments
    to base sport weights.

    Formula: final_weight = base_weight * market_adj * period_adj
    Then normalize so weights sum to 1.0

    Args:
        sport: Sport key (NBA, NFL, NHL, etc.)
        market_type: Market type (spread, totals, moneyline)
        period: Game period (full, h1, h2, q1-q4, p1-p3)

    Returns:
        Dict of pillar weights that sum to 1.0
    """
    # Get base weights for sport
    sport_upper = sport.upper()
    base_weights = SPORT_WEIGHTS.get(sport_upper, DEFAULT_WEIGHTS)

    # Get market adjustments (default to spread if unknown)
    market_adj = MARKET_ADJUSTMENTS.get(market_type, MARKET_ADJUSTMENTS.get("spread", {}))

    # Get period adjustments (default to full if unknown)
    period_adj = PERIOD_ADJUSTMENTS.get(period, PERIOD_ADJUSTMENTS.get("full", {}))

    # Calculate raw weights (base * market * period)
    raw_weights = {}
    for pillar in PILLAR_KEYS:
        base = base_weights.get(pillar, 0.15)
        m_adj = market_adj.get(pillar, 1.0)
        p_adj = period_adj.get(pillar, 1.0)
        raw_weights[pillar] = base * m_adj * p_adj

    # Normalize to sum to 1.0
    total = sum(raw_weights.values())
    if total == 0:
        # Fallback to equal weights
        return {p: 1.0 / len(PILLAR_KEYS) for p in PILLAR_KEYS}

    normalized = {p: round(w / total, 4) for p, w in raw_weights.items()}

    logger.debug(
        f"[WeightCalc] sport={sport} market={market_type} period={period} "
        f"weights={normalized}"
    )

    return normalized


def calculate_weighted_composite(
    pillar_scores: Dict[str, float],
    weights: Dict[str, float]
) -> float:
    """
    Calculate weighted composite score from pillar scores and weights.

    Args:
        pillar_scores: Dict of pillar name -> score (0.0-1.0 scale)
        weights: Dict of pillar name -> weight (should sum to 1.0)

    Returns:
        Weighted average composite score (0.0-1.0 scale)
    """
    composite = 0.0
    total_weight = 0.0

    for pillar, weight in weights.items():
        if pillar in pillar_scores:
            score = pillar_scores[pillar]
            composite += score * weight
            total_weight += weight

    if total_weight == 0:
        return 0.5  # Neutral

    return round(composite / total_weight * total_weight, 4)


def get_confidence_rating(composite: float) -> str:
    """
    Get confidence rating from composite score.

    Args:
        composite: Composite score (0.0-1.0 scale)

    Returns:
        Confidence tier: PASS, WATCH, EDGE, STRONG, or RARE
    """
    if composite >= EDGE_THRESHOLDS["RARE"]["min_composite"]:
        return "RARE"
    elif composite >= EDGE_THRESHOLDS["STRONG"]["min_composite"]:
        return "STRONG"
    elif composite >= EDGE_THRESHOLDS["EDGE"]["min_composite"]:
        return "EDGE"
    elif composite >= EDGE_THRESHOLDS["WATCH"]["min_composite"]:
        return "WATCH"
    else:
        return "PASS"


def apply_market_period_weights(
    base_scores: Dict[str, float],
    sport: str,
    market_type: str = "spread",
    period: str = "full"
) -> Dict:
    """
    Apply market and period-specific weight adjustments to base pillar scores.

    Args:
        base_scores: Dict of pillar name -> score (0.0-1.0 scale)
        sport: Sport key
        market_type: Market type (spread, totals, moneyline)
        period: Game period

    Returns:
        Dict with composite, confidence, weights, market_type, period
    """
    weights = get_effective_weights(sport, market_type, period)
    composite = calculate_weighted_composite(base_scores, weights)
    confidence = get_confidence_rating(composite)

    return {
        "composite": composite,
        "confidence": confidence,
        "weights": weights,
        "market_type": market_type,
        "period": period,
    }


def calculate_all_composites(
    base_scores: Dict[str, float],
    sport: str
) -> Dict[str, Dict[str, Dict]]:
    """
    Generate all market/period combination composites for a game.

    Args:
        base_scores: Dict of pillar name -> score (0.0-1.0 scale)
        sport: Sport key

    Returns:
        Nested dict: market_type -> period -> {composite, confidence, weights}

    Example return:
        {
            "spread": {
                "full": {"composite": 0.62, "confidence": "EDGE", "weights": {...}},
                "h1": {"composite": 0.58, "confidence": "WATCH", "weights": {...}},
                ...
            },
            "totals": {
                "full": {"composite": 0.71, "confidence": "STRONG", "weights": {...}},
                ...
            },
            "moneyline": {...}
        }
    """
    sport_upper = sport.upper()
    available_periods = SPORT_PERIOD_AVAILABILITY.get(sport_upper, ["full"])
    market_types = ["spread", "totals", "moneyline"]

    results = {}

    for market in market_types:
        results[market] = {}
        for period in available_periods:
            result = apply_market_period_weights(base_scores, sport, market, period)
            results[market][period] = {
                "composite": result["composite"],
                "confidence": result["confidence"],
                "weights": result["weights"],
            }

    logger.info(
        f"[WeightCalc] Generated {len(market_types)}x{len(available_periods)} = "
        f"{len(market_types) * len(available_periods)} composites for {sport_upper}"
    )

    return results


def get_available_periods(sport: str) -> list:
    """
    Get list of available periods for a sport.

    Args:
        sport: Sport key

    Returns:
        List of period keys (e.g., ["full", "h1", "h2", "q1", "q2", "q3", "q4"])
    """
    return SPORT_PERIOD_AVAILABILITY.get(sport.upper(), ["full"])


# For testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Test with sample pillar scores
    test_scores = {
        "execution": 0.65,
        "incentives": 0.52,
        "shocks": 0.60,
        "time_decay": 0.48,
        "flow": 0.55,
        "game_environment": 0.71,
    }

    print("\n=== Weight Calculator Test ===\n")

    # Test single calculation
    print("Single calculation (NBA, totals, h1):")
    result = apply_market_period_weights(test_scores, "NBA", "totals", "h1")
    print(f"  Composite: {result['composite']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Weights: {result['weights']}")

    # Test all combinations
    print("\nAll combinations (NBA):")
    all_results = calculate_all_composites(test_scores, "NBA")
    for market, periods in all_results.items():
        print(f"\n  {market.upper()}:")
        for period, data in periods.items():
            print(f"    {period}: composite={data['composite']:.3f} ({data['confidence']})")
