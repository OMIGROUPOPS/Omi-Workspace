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
from datetime import datetime, timezone
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

# DB-backed weight cache: sport_key -> (weights_dict, timestamp)
_weight_cache: Dict[str, tuple] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def _fetch_db_weights(sport: str) -> Optional[Dict[str, float]]:
    """Try to load pillar weights from calibration_config table.
    Returns None on miss, error, or if table doesn't exist yet."""
    cache_key = sport.upper()
    now = datetime.now(timezone.utc).timestamp()

    # Check cache first
    if cache_key in _weight_cache:
        cached_weights, cached_at = _weight_cache[cache_key]
        if now - cached_at < CACHE_TTL_SECONDS:
            return cached_weights

    try:
        from database import db
        if not db._is_connected():
            return None
        result = db.client.table("calibration_config").select("config_data").eq(
            "sport_key", cache_key
        ).eq(
            "config_type", "pillar_weights"
        ).eq(
            "active", True
        ).limit(1).execute()

        if result.data and len(result.data) > 0:
            weights = result.data[0]["config_data"]
            # Validate: must have all 6 pillar keys
            if all(k in weights for k in PILLAR_KEYS):
                _weight_cache[cache_key] = (weights, now)
                logger.info(f"[WeightCalc] Loaded DB weights for {cache_key}")
                return weights
            else:
                logger.warning(f"[WeightCalc] DB weights for {cache_key} missing pillar keys")
    except Exception as e:
        logger.warning(f"[WeightCalc] Failed to fetch DB weights for {sport}: {e}")

    return None


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
    # Get base weights for sport (try DB first, fall back to hardcoded)
    sport_upper = sport.upper()
    db_weights = _fetch_db_weights(sport)
    base_weights = db_weights if db_weights else SPORT_WEIGHTS.get(sport_upper, DEFAULT_WEIGHTS)

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
    sport: str,
    pillar_market_scores: Dict[str, Dict[str, float]] = None
) -> Dict[str, Dict[str, Dict]]:
    """
    Generate all market/period combination composites for a game.

    Args:
        base_scores: Dict of pillar name -> score (0.0-1.0 scale) - default/spread scores
        sport: Sport key
        pillar_market_scores: Optional dict of pillar name -> {market_type -> score}
            If provided, uses market-specific pillar scores instead of base_scores

    Returns:
        Nested dict: market_type -> period -> {composite, confidence, weights, pillar_scores}

    Example return:
        {
            "spread": {
                "full": {"composite": 0.62, "confidence": "EDGE", "weights": {...}, "pillar_scores": {...}},
                "h1": {"composite": 0.58, "confidence": "WATCH", "weights": {...}, "pillar_scores": {...}},
                ...
            },
            "totals": {
                "full": {"composite": 0.71, "confidence": "STRONG", "weights": {...}, "pillar_scores": {...}},
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

        # Get market-specific pillar scores if available
        if pillar_market_scores:
            market_scores = {}
            for pillar in PILLAR_KEYS:
                pillar_ms = pillar_market_scores.get(pillar, {})
                # Use market-specific score if available, else fall back to base score
                market_scores[pillar] = pillar_ms.get(market, base_scores.get(pillar, 0.5))
        else:
            market_scores = base_scores

        for period in available_periods:
            result = apply_market_period_weights(market_scores, sport, market, period)
            results[market][period] = {
                "composite": result["composite"],
                "confidence": result["confidence"],
                "weights": result["weights"],
                "pillar_scores": {k: round(v, 3) for k, v in market_scores.items()},
            }

    logger.info(
        f"[WeightCalc] Generated {len(market_types)}x{len(available_periods)} = "
        f"{len(market_types) * len(available_periods)} composites for {sport_upper}"
    )

    return results


def apply_feedback_adjustments(sport: str) -> Dict:
    """
    Read latest calibration_feedback for a sport and apply bounded weight adjustments
    to calibration_config. This is the reflexive feedback loop.

    Steps:
    1. Read latest calibration_feedback row for sport
    2. Read current weights from calibration_config
    3. Apply EMA-smoothed adjustments (alpha=0.1), bounded at ±5% per pillar
    4. Normalize so weights sum to 1.0
    5. Upsert into calibration_config
    6. Clear weight cache
    7. Log applied adjustments back to calibration_feedback row

    Returns dict with old_weights, new_weights, adjustments, or error.
    """
    sport_upper = sport.upper()

    # Feedback constants — aggressive enough to correct fundamentally wrong
    # starting weights within a few cycles (not dozens).
    # EMA_ALPHA=0.25: new feedback gets 25% influence per cycle
    # MAX_ADJ=0.10: single pillar can move ±10% per cycle
    EMA_ALPHA = 0.25
    MAX_ADJ = 0.10
    MIN_WEIGHT = 0.05

    try:
        from database import db
        if not db._is_connected():
            return {"error": "Database not connected"}

        # 1. Get latest feedback
        fb_result = db.client.table("calibration_feedback").select(
            "id, pillar_metrics, suggested_adjustments, sample_size"
        ).eq("sport_key", sport_upper).is_(
            "applied_adjustments", "null"
        ).order("analysis_date", desc=True).limit(1).execute()

        if not fb_result.data:
            return {"status": "no_pending_feedback", "sport": sport_upper}

        feedback = fb_result.data[0]
        feedback_id = feedback["id"]
        pillar_metrics = feedback.get("pillar_metrics", {})
        sample_size = feedback.get("sample_size", 0)

        if sample_size < 50:
            return {"status": "insufficient_sample", "sample_size": sample_size}

        # 2. Get current weights
        current_weights = _fetch_db_weights(sport)
        if not current_weights:
            current_weights = SPORT_WEIGHTS.get(sport_upper, DEFAULT_WEIGHTS)
        old_weights = dict(current_weights)

        # 3. Compute adjustments
        new_weights = {}
        adjustment_log = {}

        for pillar in PILLAR_KEYS:
            current = current_weights.get(pillar, 1.0 / len(PILLAR_KEYS))
            metrics = pillar_metrics.get(pillar, {})
            lift = metrics.get("lift")

            if lift is not None:
                raw_adj = lift * EMA_ALPHA
                bounded = max(-MAX_ADJ, min(MAX_ADJ, raw_adj))
                new_w = max(MIN_WEIGHT, current + bounded)
            else:
                bounded = 0.0
                new_w = current

            new_weights[pillar] = new_w
            adjustment_log[pillar] = {
                "old": round(current, 4),
                "lift": lift,
                "adjustment": round(bounded, 4),
                "new_raw": round(new_w, 4),
            }

        # 4. Normalize to sum to 1.0
        total = sum(new_weights.values())
        if total > 0:
            new_weights = {p: round(w / total, 4) for p, w in new_weights.items()}
        for pillar in PILLAR_KEYS:
            adjustment_log[pillar]["new_normalized"] = new_weights[pillar]

        # 5. Update or insert into calibration_config
        # (Partial unique index doesn't work with Supabase upsert on_conflict)
        existing = db.client.table("calibration_config").select("id").eq(
            "sport_key", sport_upper
        ).eq("config_type", "pillar_weights").eq("active", True).limit(1).execute()

        if existing.data:
            db.client.table("calibration_config").update({
                "config_data": new_weights,
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            db.client.table("calibration_config").insert({
                "sport_key": sport_upper,
                "config_type": "pillar_weights",
                "config_data": new_weights,
                "active": True,
            }).execute()

        # 6. Clear weight cache
        if sport_upper in _weight_cache:
            del _weight_cache[sport_upper]

        # 7. Log applied adjustments back to feedback row
        db.client.table("calibration_feedback").update({
            "applied_adjustments": adjustment_log,
        }).eq("id", feedback_id).execute()

        logger.info(
            f"[WeightAdj] {sport_upper}: " +
            ", ".join(
                f"{p} {old_weights.get(p, 0):.3f}→{new_weights[p]:.3f}"
                for p in PILLAR_KEYS
            )
        )
        logger.info(
            f"[WeightCalc] Applied feedback adjustments for {sport_upper}: "
            f"sample={sample_size}"
        )

        return {
            "status": "applied",
            "sport": sport_upper,
            "sample_size": sample_size,
            "old_weights": old_weights,
            "new_weights": new_weights,
            "adjustments": adjustment_log,
        }

    except Exception as e:
        logger.error(f"[WeightCalc] apply_feedback_adjustments failed for {sport}: {e}")
        return {"error": str(e)}


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
