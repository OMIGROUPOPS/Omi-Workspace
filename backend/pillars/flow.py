"""
Pillar 5: Market Microstructure & Flow
Weight: 0.25

Measures: Sharp vs public money patterns
- Opening line vs current line movement
- Cross-book line discrepancies
- Reverse line movement
- Steam moves (coordinated sharp action)
- PINNACLE DIVERGENCE (sharp baseline comparison)
"""
from datetime import datetime
from typing import Optional
import logging
import statistics

from data_sources.odds_api import odds_client

logger = logging.getLogger(__name__)

# Sharp books list - Pinnacle is the gold standard
SHARP_BOOKS = ["pinnacle", "bookmaker", "betcris", "5dimes"]
# Retail/Square books - tend to shade lines toward public
RETAIL_BOOKS = ["draftkings", "fanduel", "betmgm", "caesars", "pointsbet", "wynnbet"]


def _analyze_pinnacle_divergence(spreads_by_book: dict, parsed: dict) -> dict:
    """
    Analyze Pinnacle line vs retail book consensus.

    Pinnacle is considered the sharpest book - they take large limits
    and have the most efficient lines. When retail books diverge from
    Pinnacle, it often indicates value.

    When Pinnacle data isn't available (US markets), we estimate based on
    market efficiency principles: Pinnacle typically gives underdogs
    0.5-1.0 more points than retail books.

    Returns:
        dict with pinnacle_line, retail_consensus, divergence, signal_direction
    """
    pinnacle_line = None
    retail_lines = []

    for book, line in spreads_by_book.items():
        book_lower = book.lower()
        if book_lower in SHARP_BOOKS or "pinnacle" in book_lower:
            pinnacle_line = line
        elif book_lower in RETAIL_BOOKS:
            retail_lines.append(line)

    # If no Pinnacle available, estimate based on market efficiency
    # Pinnacle typically gives underdogs 0.5 more points than retail
    if pinnacle_line is None and retail_lines:
        retail_consensus = sum(retail_lines) / len(retail_lines)

        # For home underdogs (positive spread), Pinnacle gives more points
        # For home favorites (negative spread), Pinnacle gives fewer points
        # This reflects Pinnacle's sharper, more efficient lines
        if retail_consensus > 0:
            # Home is underdog - Pinnacle would give them MORE points
            pinnacle_line = retail_consensus + 0.5
            logger.info(f"[Flow] Estimated Pinnacle (home underdog): {pinnacle_line:+.1f} vs retail {retail_consensus:+.1f}")
        elif retail_consensus < -3:
            # Home is big favorite - Pinnacle would shade toward dog
            pinnacle_line = retail_consensus + 0.5
            logger.info(f"[Flow] Estimated Pinnacle (home favorite): {pinnacle_line:+.1f} vs retail {retail_consensus:+.1f}")
        else:
            # Close to pick'em - minimal adjustment
            pinnacle_line = retail_consensus
            logger.info(f"[Flow] Pinnacle estimated same as retail for close game: {pinnacle_line:+.1f}")

    # Case 1: No Pinnacle AND no retail lines - truly no data
    if pinnacle_line is None and not retail_lines:
        return {
            "pinnacle_line": None,
            "retail_consensus": None,
            "divergence": 0,
            "signal_direction": "neutral",
            "reasoning": None
        }

    # Case 2: We have Pinnacle but no retail lines (common for soccer)
    # Use Pinnacle line as THE sharp signal - home favored if negative
    if pinnacle_line is not None and not retail_lines:
        signal_direction = "neutral"
        reasoning = None

        # Pinnacle line IS the sharp signal
        # Negative line = home favored by Pinnacle
        # Positive line = away favored by Pinnacle
        if pinnacle_line <= -1.0:
            signal_direction = "home"
            reasoning = f"PINNACLE SHARP: Home favored at {pinnacle_line:+.2f} handicap"
        elif pinnacle_line >= 1.0:
            signal_direction = "away"
            reasoning = f"PINNACLE SHARP: Away favored, home at {pinnacle_line:+.2f} handicap"
        elif pinnacle_line < 0:
            signal_direction = "home"
            reasoning = f"Pinnacle: slight home edge at {pinnacle_line:+.2f}"
        elif pinnacle_line > 0:
            signal_direction = "away"
            reasoning = f"Pinnacle: slight away edge, home at {pinnacle_line:+.2f}"

        logger.info(f"[Flow] Pinnacle-only analysis: line={pinnacle_line:+.2f}, signal={signal_direction}")

        return {
            "pinnacle_line": pinnacle_line,
            "retail_consensus": None,
            "divergence": abs(pinnacle_line),  # Use line magnitude as "divergence"
            "signal_direction": signal_direction,
            "reasoning": reasoning
        }

    # Case 3: No Pinnacle but have retail lines
    if pinnacle_line is None and retail_lines:
        return {
            "pinnacle_line": None,
            "retail_consensus": sum(retail_lines) / len(retail_lines),
            "divergence": 0,
            "signal_direction": "neutral",
            "reasoning": "No sharp book data available"
        }

    # Case 4: Have both Pinnacle and retail - compare them
    retail_consensus = sum(retail_lines) / len(retail_lines)
    divergence = pinnacle_line - retail_consensus

    # Interpret divergence:
    # If Pinnacle has HOME at -3.5 but retail has HOME at -2.5
    # divergence = -3.5 - (-2.5) = -1.0
    # This means Pinnacle thinks HOME is stronger than retail does
    # Signal: HOME value (score < 0.5)

    signal_direction = "neutral"
    reasoning = None

    # AMPLIFIED thresholds for visual differentiation
    # 0.5 pts = moderate signal
    # 1.0+ pts = strong signal
    if abs(divergence) >= 1.0:
        # Strong signal - 1+ point divergence
        if divergence < 0:
            signal_direction = "home"
            reasoning = f"STRONG PINNACLE: Pinnacle {pinnacle_line:+.1f} vs retail {retail_consensus:+.1f} ({divergence:+.1f}) - STRONG HOME signal"
        else:
            signal_direction = "away"
            reasoning = f"STRONG PINNACLE: Pinnacle {pinnacle_line:+.1f} vs retail {retail_consensus:+.1f} ({divergence:+.1f}) - STRONG AWAY signal"
    elif abs(divergence) >= 0.5:
        # Moderate signal - 0.5 point divergence
        if divergence < 0:
            signal_direction = "home"
            reasoning = f"PINNACLE SHARP: Pinnacle {pinnacle_line:+.1f} vs retail {retail_consensus:+.1f} ({divergence:+.1f}) - favors HOME"
        else:
            signal_direction = "away"
            reasoning = f"PINNACLE SHARP: Pinnacle {pinnacle_line:+.1f} vs retail {retail_consensus:+.1f} ({divergence:+.1f}) - favors AWAY"

    logger.info(f"[Flow] Pinnacle analysis: pinnacle={pinnacle_line}, retail_avg={retail_consensus:.1f}, div={divergence:+.1f}")

    return {
        "pinnacle_line": pinnacle_line,
        "retail_consensus": round(retail_consensus, 2),
        "divergence": round(divergence, 2),
        "signal_direction": signal_direction,
        "reasoning": reasoning
    }


def _detect_reverse_line_movement(
    opening_line: Optional[float],
    current_line: float,
    public_side: str = "unknown"
) -> dict:
    """
    Detect reverse line movement - when line moves AGAINST public money.

    This is a strong sharp indicator:
    - If 70% of bets are on Team A, you'd expect line to move toward A
    - If line moves toward Team B instead = sharps on Team B

    Args:
        opening_line: Opening spread
        current_line: Current spread
        public_side: Which side public is betting ("home" or "away")

    Returns:
        dict with rlm_detected, direction, magnitude
    """
    if opening_line is None:
        return {
            "rlm_detected": False,
            "direction": "neutral",
            "magnitude": 0,
            "reasoning": None
        }

    movement = current_line - opening_line

    # Without actual betting splits, we can infer from line movement patterns
    # Large movement with small line change = possible RLM
    # For now, flag significant movements
    rlm_detected = False
    direction = "neutral"
    reasoning = None

    if abs(movement) >= 1.0:
        # Significant line movement
        if movement > 0:
            # Line moved toward away team (home spread increased)
            direction = "away"
            reasoning = f"Line moved {movement:+.1f} toward away - possible sharp action"
        else:
            direction = "home"
            reasoning = f"Line moved {movement:+.1f} toward home - possible sharp action"
        rlm_detected = True

    return {
        "rlm_detected": rlm_detected,
        "direction": direction,
        "magnitude": round(movement, 2),
        "reasoning": reasoning
    }


def _blend_exchange_signal(
    game_id: str, score: float, reasoning_parts: list
) -> float:
    """
    Blend exchange implied probability into flow score (45% weight).
    Returns updated score. Zero-regression: if no data or error, returns original.
    """
    try:
        from exchange_tracker import ExchangeTracker
        if not game_id:
            return score
        tracker = ExchangeTracker()
        contracts = tracker.get_game_exchange_data(game_id)
        if not contracts:
            return score
        # Find home team's moneyline contract via subtitle matching
        # For moneyline, each team has a separate contract — must NOT average them
        from database import db
        home_team = ""
        try:
            cached = db.client.table("cached_odds").select("game_data").eq(
                "game_id", game_id
            ).limit(1).execute()
            if cached.data:
                home_team = (cached.data[0].get("game_data") or {}).get("home_team", "")
        except Exception:
            pass

        ml_contracts = [c for c in contracts if c.get("market_type") == "moneyline"
                        and c.get("yes_price") is not None and c["yes_price"] > 0]
        other_contracts = [c for c in contracts if c.get("market_type") != "moneyline"
                          and c.get("yes_price") is not None and c["yes_price"] > 0]

        exchange_prob = None
        if ml_contracts and home_team:
            # Match subtitle to home team
            home_lower = home_team.lower()
            home_words = [w for w in home_lower.split() if len(w) > 3]
            for c in ml_contracts:
                sub = (c.get("subtitle") or "").lower()
                if any(w in sub for w in home_words):
                    exchange_prob = c["yes_price"] / 100.0
                    break
        if exchange_prob is None and ml_contracts:
            # Fallback: highest yes_price contract (likely favorite, better than averaging to 50)
            best = max(ml_contracts, key=lambda c: c["yes_price"])
            exchange_prob = best["yes_price"] / 100.0
        if exchange_prob is None and other_contracts:
            # No moneyline data — average other contract types
            exchange_prob = sum(c["yes_price"] / 100.0 for c in other_contracts) / len(other_contracts)
        if exchange_prob is None:
            return score
        # Convert to flow scale: flow >0.5 = away edge, so invert exchange home prob
        exchange_flow = 1 - exchange_prob
        old_score = score
        score = 0.55 * score + 0.45 * exchange_flow
        score = max(0.15, min(0.85, score))
        # Summarize price movement direction
        price_changes = [c.get("price_change", 0) or 0 for c in contracts]
        net_change = sum(price_changes)
        direction = "rising" if net_change > 0 else "falling" if net_change < 0 else "flat"
        reasoning_parts.append(
            f"Exchange signal: {exchange_prob:.1%} implied home "
            f"(contracts: {len(contracts)}, {direction})"
        )
        logger.info(
            f"Flow: exchange blend for {game_id} | exchange_prob={exchange_prob:.3f} "
            f"blended={score:.3f} (was {old_score:.3f}, contracts={len(contracts)})"
        )
        return score
    except Exception as e:
        logger.debug(f"[Flow] No exchange data for game {game_id}: {e}")
        return score


def calculate_flow_score(
    game: dict,
    opening_line: Optional[float] = None,
    line_snapshots: Optional[list] = None,
    market_type: str = "spread"
) -> dict:
    """
    Calculate Pillar 5: Market Microstructure & Flow score.

    For SPREAD/MONEYLINE:
    - score > 0.5: Sharp flow on AWAY team
    - score < 0.5: Sharp flow on HOME team

    For TOTALS:
    - score > 0.5: Sharp flow on OVER
    - score < 0.5: Sharp flow on UNDER

    A score = 0.5 means balanced/unclear flow signals
    """
    parsed = odds_client.parse_game_odds(game)
    bookmakers = parsed["bookmakers"]

    logger.info(f"[Flow] Parsed game: {parsed.get('away_team')} @ {parsed.get('home_team')}")
    logger.info(f"[Flow] Found {len(bookmakers)} bookmakers")
    for book_key, markets in bookmakers.items():
        market_keys = list(markets.keys()) if markets else []
        logger.info(f"[Flow]   {book_key}: {market_keys}")
        if "spreads" in markets:
            logger.info(f"[Flow]     spreads: {markets['spreads']}")

    if not bookmakers:
        logger.warning(f"[Flow] WARNING: Returning default 0.5 — no bookmaker data available for game")
        logger.warning(f"[Flow]   game keys: {list(game.keys()) if isinstance(game, dict) else 'not a dict'}")
        logger.warning(f"[Flow]   game.bookmakers length: {len(game.get('bookmakers', []))}")
        return {
            "score": 0.5,
            "spread_variance": 0.0,
            "consensus_line": 0.0,
            "sharpest_line": 0.0,
            "book_agreement": 0.0,
            "breakdown": {},
            "reasoning": "No bookmaker data available"
        }
    
    reasoning_parts = []

    # Extract BOTH lines AND prices for spread analysis
    spreads_by_book = {}
    spread_prices_by_book = {}
    for book_key, markets in bookmakers.items():
        if "spreads" in markets and "home" in markets["spreads"]:
            home_spread = markets["spreads"]["home"]
            spreads_by_book[book_key] = home_spread.get("line", 0)
            spread_prices_by_book[book_key] = home_spread.get("odds", -110)
            logger.info(f"[Flow] {book_key}: line={home_spread.get('line')} odds={home_spread.get('odds')}")

    if not spreads_by_book:
        return _analyze_moneyline_flow(bookmakers, parsed)
    
    lines = list(spreads_by_book.values())
    book_count = len(lines)
    
    consensus_line = sum(lines) / len(lines)
    
    if len(lines) >= 2:
        variance = statistics.variance(lines)
        stdev = statistics.stdev(lines)
    else:
        variance = 0
        stdev = 0
    
    sharp_priority = ["betmgm", "caesars", "draftkings", "fanduel"]
    
    sharpest_line = consensus_line
    sharpest_book = None
    for book in sharp_priority:
        if book in spreads_by_book:
            sharpest_line = spreads_by_book[book]
            sharpest_book = book
            break
    
    outlier_books = []
    for book, line in spreads_by_book.items():
        if abs(line - consensus_line) >= 1.0:
            outlier_books.append({
                "book": book,
                "line": line,
                "deviation": line - consensus_line
            })
    
    if outlier_books:
        reasoning_parts.append(f"Book disagreement: {len(outlier_books)} outliers")
    
    if stdev == 0:
        book_agreement = 1.0
    else:
        book_agreement = max(0, 1 - (stdev / 3))
    
    line_movement = 0.0
    movement_direction = "neutral"
    
    if opening_line is not None:
        line_movement = consensus_line - opening_line
        
        if abs(line_movement) >= 0.5:
            if line_movement > 0:
                movement_direction = "toward_away"
                reasoning_parts.append(f"Line moved +{line_movement:.1f} toward {parsed['away_team']}")
            else:
                movement_direction = "toward_home"
                reasoning_parts.append(f"Line moved {line_movement:.1f} toward {parsed['home_team']}")
    
    velocity = 0.0
    if line_snapshots and len(line_snapshots) >= 2:
        recent_lines = [s["line"] for s in sorted(line_snapshots, key=lambda x: x["timestamp"])[-5:]]
        if len(recent_lines) >= 2:
            velocity = recent_lines[-1] - recent_lines[0]
            if abs(velocity) >= 1.0:
                reasoning_parts.append(f"Recent velocity: {velocity:+.1f} in last few updates")
    
    base_score = 0.5

    # === PRICE DIVERGENCE ANALYSIS ===
    # This is the KEY signal - when books have vastly different prices on similar lines
    price_divergence = 0
    best_price_book = None
    worst_price_book = None
    if len(spread_prices_by_book) >= 2:
        prices = list(spread_prices_by_book.values())
        max_price = max(prices)
        min_price = min(prices)

        # Calculate divergence in cents (absolute difference)
        # +116 to -250 = 366 cents divergence
        price_divergence = abs(max_price - min_price)

        best_price_book = [k for k, v in spread_prices_by_book.items() if v == max_price][0]
        worst_price_book = [k for k, v in spread_prices_by_book.items() if v == min_price][0]

        logger.info(f"[Flow] Price divergence: {price_divergence} cents ({best_price_book}: {max_price} vs {worst_price_book}: {min_price})")

        # Price divergence thresholds:
        # > 50 cents = notable (e.g., -110 vs -160)
        # > 100 cents = significant
        # > 200 cents = extreme
        # > 300 cents = massive arbitrage signal
        if price_divergence >= 50:
            # Strong signal - move score based on divergence magnitude
            divergence_impact = min(price_divergence / 500, 0.4)  # Cap at 0.4 adjustment

            # Positive prices (like +116) indicate value on that side
            # If best price is positive or close to even, that's where value is
            if max_price >= -105:  # Plus money or nearly even
                base_score += divergence_impact
                reasoning_parts.append(f"PRICE DIVERGENCE: {best_price_book} offers {max_price:+d} vs {worst_price_book} at {min_price:+d} ({price_divergence} cents)")
            else:
                # Both negative but big gap - still signals value at better price
                base_score += divergence_impact * 0.5
                reasoning_parts.append(f"Price gap: {best_price_book} {max_price:+d} vs {worst_price_book} {min_price:+d} ({price_divergence}c)")

    # === PINNACLE DIVERGENCE ANALYSIS (KEY SHARP SIGNAL) ===
    # AMPLIFIED for visual differentiation
    pinnacle_analysis = _analyze_pinnacle_divergence(spreads_by_book, parsed)
    pinnacle_divergence = pinnacle_analysis.get("divergence", 0)

    if pinnacle_analysis["signal_direction"] != "neutral":
        # AMPLIFIED: Pinnacle divergence impact
        # 0.5 pts = 8-12% swing
        # 1.0+ pts = 15-20% swing
        abs_div = abs(pinnacle_divergence)
        if abs_div >= 1.0:
            divergence_impact = 0.15 + (abs_div - 1.0) * 0.05  # 15-20%
        elif abs_div >= 0.5:
            divergence_impact = 0.08 + (abs_div - 0.5) * 0.08  # 8-12%
        else:
            divergence_impact = abs_div * 0.16  # 0-8%

        divergence_impact = min(divergence_impact, 0.25)  # Cap at 25%

        if pinnacle_analysis["signal_direction"] == "away":
            base_score += divergence_impact
        else:  # home
            base_score -= divergence_impact

        if pinnacle_analysis["reasoning"]:
            reasoning_parts.append(pinnacle_analysis["reasoning"])

    # === REVERSE LINE MOVEMENT DETECTION ===
    # AMPLIFIED for visual differentiation
    rlm_analysis = _detect_reverse_line_movement(opening_line, consensus_line)

    if rlm_analysis["rlm_detected"]:
        # AMPLIFIED: RLM impact
        # 1 point move = 8-10% swing
        # 2+ point move = 15-20% swing
        abs_mag = abs(rlm_analysis["magnitude"])
        if abs_mag >= 2.0:
            rlm_impact = 0.15 + (abs_mag - 2.0) * 0.05  # 15-20%
        elif abs_mag >= 1.0:
            rlm_impact = 0.08 + (abs_mag - 1.0) * 0.07  # 8-15%
        else:
            rlm_impact = abs_mag * 0.08  # 0-8%

        rlm_impact = min(rlm_impact, 0.20)  # Cap at 20%

        if rlm_analysis["direction"] == "away":
            base_score += rlm_impact
        else:  # home
            base_score -= rlm_impact

        if rlm_analysis["reasoning"]:
            reasoning_parts.append(rlm_analysis["reasoning"])

    # === LINE MOVEMENT ANALYSIS ===
    # Line movement is a strong signal
    if movement_direction == "toward_away":
        base_score += min(abs(line_movement) * 0.15, 0.3)
    elif movement_direction == "toward_home":
        base_score -= min(abs(line_movement) * 0.15, 0.3)

    # Sharp book deviation - even small deviations matter (if Pinnacle not available)
    if sharpest_book and sharpest_line != consensus_line and pinnacle_analysis["pinnacle_line"] is None:
        sharp_deviation = sharpest_line - consensus_line
        if abs(sharp_deviation) >= 0.25:
            base_score += sharp_deviation * 0.15
            reasoning_parts.append(f"Sharp book ({sharpest_book}) at {sharpest_line} vs consensus {consensus_line:.1f}")

    # Book disagreement indicates opportunity
    if book_agreement < 0.85:
        base_score += (0.85 - book_agreement) * 0.2
        reasoning_parts.append(f"Book disagreement ({book_agreement:.2f}) - potential value")

    # Velocity matters
    if abs(velocity) >= 0.5:
        base_score += velocity * 0.08

    # If we have many books, slight deviations are more meaningful
    if book_count >= 3 and stdev > 0.3:
        base_score += 0.05 if consensus_line < 0 else -0.05
        reasoning_parts.append(f"Cross-book variance detected ({book_count} books, stdev {stdev:.2f})")

    score = max(0.0, min(1.0, base_score))

    if not reasoning_parts:
        reasoning_parts.append("Market flow appears balanced across books")

    # Diagnostic: log when Flow returns near-default with data present
    if abs(score - 0.5) < 0.01:
        logger.warning(f"[Flow] WARNING: Returning ~0.5 despite having {len(spreads_by_book)} books")
        logger.warning(f"[Flow]   opening_line={'present' if opening_line is not None else 'MISSING'}, "
                       f"snapshots={len(line_snapshots) if line_snapshots else 0}")
        logger.warning(f"[Flow]   spreads: {spreads_by_book}")
        logger.warning(f"[Flow]   pinnacle_div={pinnacle_divergence}, book_agreement={book_agreement:.3f}, "
                       f"stdev={stdev:.3f}, velocity={velocity:.2f}")

    # Calculate market-specific scores
    # SPREAD/MONEYLINE: Sharp flow on home or away? (score as calculated)
    # TOTALS: Sharp flow on over or under? (similar signal but for totals)
    market_scores = {}
    market_scores["spread"] = score
    market_scores["moneyline"] = score  # Same flow signals apply

    # TOTALS: Use the same directional signals but apply to over/under
    # Sharp money flow generally indicates where value is
    # Book disagreement on totals would require separate totals odds analysis
    # For now, use a slightly dampened version of spread flow for totals
    totals_score = 0.5 + (score - 0.5) * 0.7  # Dampen the signal for totals
    totals_score = max(0.15, min(0.85, totals_score))
    market_scores["totals"] = totals_score

    logger.info(f"[Flow] Market scores: spread={score:.3f}, totals={totals_score:.3f}")

    # Blend exchange signal if available (30% weight within Flow)
    game_id = game.get("id", "")
    score = _blend_exchange_signal(game_id, score, reasoning_parts)
    # Recompute market scores after exchange blend
    market_scores["spread"] = score
    market_scores["moneyline"] = score
    totals_score = 0.5 + (score - 0.5) * 0.7
    totals_score = max(0.15, min(0.85, totals_score))
    market_scores["totals"] = totals_score

    return {
        "score": round(score, 3),
        "market_scores": {k: round(v, 3) for k, v in market_scores.items()},
        "spread_variance": round(variance, 3),
        "consensus_line": round(consensus_line, 2),
        "sharpest_line": round(sharpest_line, 2),
        "book_agreement": round(book_agreement, 3),
        "pinnacle_divergence": pinnacle_divergence,
        "breakdown": {
            "spreads_by_book": spreads_by_book,
            "spread_prices_by_book": spread_prices_by_book,
            "price_divergence": price_divergence,
            "best_price_book": best_price_book,
            "worst_price_book": worst_price_book,
            "book_count": book_count,
            "stdev": round(stdev, 3),
            "outlier_books": outlier_books,
            "line_movement": round(line_movement, 2),
            "movement_direction": movement_direction,
            "velocity": round(velocity, 2),
            "sharpest_book": sharpest_book,
            "pinnacle_analysis": pinnacle_analysis,
            "rlm_analysis": rlm_analysis,
        },
        "reasoning": "; ".join(reasoning_parts)
    }


def _analyze_moneyline_flow(bookmakers: dict, parsed: dict) -> dict:
    """Fallback flow analysis using moneyline odds when spreads unavailable."""
    home_odds_list = []
    away_odds_list = []
    draw_odds_list = []

    for book_key, markets in bookmakers.items():
        if "h2h" in markets:
            if "home" in markets["h2h"]:
                home_odds_list.append(markets["h2h"]["home"])
            if "away" in markets["h2h"]:
                away_odds_list.append(markets["h2h"]["away"])
            if "draw" in markets["h2h"]:
                draw_odds_list.append(markets["h2h"]["draw"])

    if not home_odds_list:
        return {
            "score": 0.5,
            "spread_variance": 0.0,
            "consensus_line": 0.0,
            "sharpest_line": 0.0,
            "book_agreement": 0.0,
            "breakdown": {},
            "reasoning": "Insufficient data for flow analysis"
        }

    def american_to_prob(odds):
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    home_probs = [american_to_prob(o) for o in home_odds_list]
    away_probs = [american_to_prob(o) for o in away_odds_list] if away_odds_list else []

    avg_home_prob = sum(home_probs) / len(home_probs)
    avg_away_prob = sum(away_probs) / len(away_probs) if away_probs else 0

    if len(home_probs) >= 2:
        prob_variance = statistics.variance(home_probs)
    else:
        prob_variance = 0

    reasoning_parts = []
    base_score = 0.5

    # AMPLIFIED moneyline analysis for soccer
    # If home is heavily favored (>55% implied prob), lean toward away (contrarian)
    # If away is heavily favored (>55% implied prob), lean toward home (contrarian)
    # Market usually overvalues favorites

    if avg_home_prob >= 0.55:
        # Home heavily favored - slight contrarian lean to away
        adjustment = (avg_home_prob - 0.50) * 0.3
        base_score += adjustment
        reasoning_parts.append(f"Home favored ({avg_home_prob:.1%}) - market may overvalue")
    elif avg_away_prob >= 0.55:
        # Away heavily favored - slight contrarian lean to home
        adjustment = (avg_away_prob - 0.50) * 0.3
        base_score -= adjustment
        reasoning_parts.append(f"Away favored ({avg_away_prob:.1%}) - market may overvalue")
    elif avg_home_prob > 0.45 and avg_home_prob < 0.55:
        # Close to pick'em - no strong edge
        reasoning_parts.append(f"Close matchup: home {avg_home_prob:.1%}, away {avg_away_prob:.1%}")

    # Book disagreement indicates opportunity
    if prob_variance > 0.005:  # Lowered threshold
        variance_adjustment = min(prob_variance * 20, 0.15)  # Up to 15% adjustment
        base_score += variance_adjustment if avg_home_prob > 0.5 else -variance_adjustment
        reasoning_parts.append(f"Book disagreement detected (var={prob_variance:.4f})")

    # If we have draw odds, factor that in (soccer-specific)
    if draw_odds_list:
        avg_draw_prob = sum([american_to_prob(o) for o in draw_odds_list]) / len(draw_odds_list)
        if avg_draw_prob > 0.30:
            # High draw probability = game likely to be close
            reasoning_parts.append(f"Draw likely ({avg_draw_prob:.1%}) - game expected to be tight")
        elif avg_draw_prob < 0.22:
            # Low draw probability = likely decisive result
            reasoning_parts.append(f"Draw unlikely ({avg_draw_prob:.1%}) - clear favorite")

    score = max(0.15, min(0.85, base_score))

    if not reasoning_parts:
        reasoning_parts.append(f"Moneyline: home {avg_home_prob:.1%}, away {avg_away_prob:.1%}")

    # Calculate market-specific scores for moneyline flow analysis
    market_scores = {}
    market_scores["spread"] = score
    market_scores["moneyline"] = score

    # Blend exchange signal if available (30% weight within Flow)
    game_id = game.get("id", "")
    score = _blend_exchange_signal(game_id, score, reasoning_parts)

    # TOTALS: Dampen the signal for totals
    totals_score = 0.5 + (score - 0.5) * 0.7
    totals_score = max(0.15, min(0.85, totals_score))
    market_scores["totals"] = totals_score

    return {
        "score": round(score, 3),
        "market_scores": {k: round(v, 3) for k, v in market_scores.items()},
        "spread_variance": 0.0,
        "consensus_line": 0.0,
        "sharpest_line": 0.0,
        "book_agreement": round(1 - min(prob_variance * 10, 1), 3),
        "breakdown": {
            "home_odds_list": home_odds_list,
            "away_odds_list": away_odds_list,
            "draw_odds_list": draw_odds_list,
            "avg_home_prob": round(avg_home_prob, 4),
            "avg_away_prob": round(avg_away_prob, 4),
            "prob_variance": round(prob_variance, 4)
        },
        "reasoning": "; ".join(reasoning_parts)
    }


def get_flow_edge_direction(score: float, book_agreement: float) -> str:
    """Interpret the flow score."""
    if book_agreement < 0.5:
        return "uncertain"
    
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "neutral"