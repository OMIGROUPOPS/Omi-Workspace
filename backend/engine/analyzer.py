"""
OMI Edge Analysis Engine

The core engine that:
1. Fetches data from all sources
2. Calculates all 5 pillar scores
3. Computes composite score and edge percentage
4. Determines confidence rating
"""
from datetime import datetime, timezone
from typing import Optional
import logging

from config import PILLAR_WEIGHTS, EDGE_THRESHOLDS
from data_sources.odds_api import odds_client
from data_sources.espn import espn_client
from pillars import (
    calculate_execution_score,
    calculate_incentives_score,
    calculate_shocks_score,
    calculate_time_decay_score,
    calculate_flow_score,
)

logger = logging.getLogger(__name__)


def american_to_implied_prob(odds: int) -> float:
    """Convert American odds to implied probability."""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def implied_prob_to_american(prob: float) -> int:
    """Convert implied probability to American odds."""
    if prob <= 0 or prob >= 1:
        return 0
    if prob >= 0.5:
        return int(-100 * prob / (1 - prob))
    else:
        return int(100 * (1 - prob) / prob)


def calculate_composite_score(pillar_scores: dict) -> float:
    """Calculate weighted composite score from all pillars."""
    composite = 0.0
    total_weight = 0.0
    
    for pillar, weight in PILLAR_WEIGHTS.items():
        if pillar in pillar_scores:
            composite += pillar_scores[pillar] * weight
            total_weight += weight
    
    if total_weight == 0:
        return 0.5
    
    return composite / total_weight * (sum(PILLAR_WEIGHTS.values()) / total_weight)


def calculate_edge_percentage(
    composite_score: float,
    book_implied_prob: float,
    side: str = "home"
) -> float:
    """Calculate edge percentage based on composite score and book odds."""
    adjustment = (composite_score - 0.5) * 0.2
    
    if side == "home":
        our_true_prob = book_implied_prob - adjustment
    else:
        our_true_prob = book_implied_prob + adjustment
    
    our_true_prob = max(0.01, min(0.99, our_true_prob))
    edge = (our_true_prob - book_implied_prob) * 100
    
    return round(edge, 2)


def get_confidence_rating(edge_pct: float, composite_score: float) -> str:
    """Determine confidence rating based on edge and composite."""
    abs_edge = abs(edge_pct)
    composite_strength = abs(composite_score - 0.5) * 2
    
    if abs_edge >= 6.0 and composite_strength >= 0.4:
        return "STRONG_EDGE"
    elif abs_edge >= 4.0 and composite_strength >= 0.3:
        return "EDGE"
    elif abs_edge >= 2.0 and composite_strength >= 0.2:
        return "WATCH"
    else:
        return "PASS"


def analyze_game(
    game: dict,
    sport: str,
    opening_line: Optional[float] = None,
    line_snapshots: Optional[list] = None
) -> dict:
    """Full analysis of a single game using all 5 pillars."""
    parsed = odds_client.parse_game_odds(game)
    
    home_team = parsed["home_team"]
    away_team = parsed["away_team"]
    game_time = parsed["commence_time"]
    game_id = parsed["game_id"]
    
    logger.info(f"Analyzing: {away_team} @ {home_team}")
    
    venue = None
    
    execution = calculate_execution_score(
        sport=sport,
        home_team=home_team,
        away_team=away_team,
        game_time=game_time,
        venue=venue
    )
    
    incentives = calculate_incentives_score(
        sport=sport,
        home_team=home_team,
        away_team=away_team,
        game_time=game_time
    )
    
    # Calculate consensus odds (now includes extended markets)
    consensus = odds_client.calculate_consensus_odds(game)
    current_line = None
    if consensus.get("spreads", {}).get("home"):
        current_line = consensus["spreads"]["home"]["line"]
    
    shocks = calculate_shocks_score(
        sport=sport,
        home_team=home_team,
        away_team=away_team,
        game_time=game_time,
        current_line=current_line,
        opening_line=opening_line,
        line_movement_history=line_snapshots
    )
    
    time_decay = calculate_time_decay_score(
        sport=sport,
        home_team=home_team,
        away_team=away_team,
        game_time=game_time
    )
    
    flow = calculate_flow_score(
        game=game,
        opening_line=opening_line,
        line_snapshots=line_snapshots
    )
    
    pillar_scores = {
        "execution": execution["score"],
        "incentives": incentives["score"],
        "shocks": shocks["score"],
        "time_decay": time_decay["score"],
        "flow": flow["score"],
    }
    
    composite = calculate_composite_score(pillar_scores)
    
    edges = {}
    
    if consensus.get("h2h"):
        home_odds = consensus["h2h"].get("home")
        away_odds = consensus["h2h"].get("away")
        
        if home_odds:
            home_prob = american_to_implied_prob(home_odds)
            home_edge = calculate_edge_percentage(composite, home_prob, "home")
            edges["ml_home"] = {
                "odds": home_odds,
                "implied_prob": round(home_prob, 4),
                "edge_pct": home_edge,
                "confidence": get_confidence_rating(home_edge, composite)
            }
        
        if away_odds:
            away_prob = american_to_implied_prob(away_odds)
            away_edge = calculate_edge_percentage(composite, away_prob, "away")
            edges["ml_away"] = {
                "odds": away_odds,
                "implied_prob": round(away_prob, 4),
                "edge_pct": away_edge,
                "confidence": get_confidence_rating(away_edge, composite)
            }
    
    if consensus.get("spreads"):
        home_spread = consensus["spreads"].get("home", {})
        away_spread = consensus["spreads"].get("away", {})
        
        if home_spread:
            spread_prob = american_to_implied_prob(home_spread.get("odds", -110))
            home_spread_edge = calculate_edge_percentage(composite, spread_prob, "home")
            edges["spread_home"] = {
                "line": home_spread.get("line"),
                "odds": home_spread.get("odds"),
                "implied_prob": round(spread_prob, 4),
                "edge_pct": home_spread_edge,
                "confidence": get_confidence_rating(home_spread_edge, composite)
            }
        
        if away_spread:
            spread_prob = american_to_implied_prob(away_spread.get("odds", -110))
            away_spread_edge = calculate_edge_percentage(composite, spread_prob, "away")
            edges["spread_away"] = {
                "line": away_spread.get("line"),
                "odds": away_spread.get("odds"),
                "implied_prob": round(spread_prob, 4),
                "edge_pct": away_spread_edge,
                "confidence": get_confidence_rating(away_spread_edge, composite)
            }
    
    if consensus.get("totals"):
        over = consensus["totals"].get("over", {})
        under = consensus["totals"].get("under", {})
        
        totals_composite = (flow["score"] * 0.5 + shocks["score"] * 0.3 + time_decay["score"] * 0.2)
        
        if over:
            over_prob = american_to_implied_prob(over.get("odds", -110))
            over_edge = (totals_composite - 0.5) * 10
            edges["total_over"] = {
                "line": over.get("line"),
                "odds": over.get("odds"),
                "implied_prob": round(over_prob, 4),
                "edge_pct": round(over_edge, 2),
                "confidence": get_confidence_rating(over_edge, totals_composite)
            }
        
        if under:
            under_prob = american_to_implied_prob(under.get("odds", -110))
            under_edge = (0.5 - totals_composite) * 10
            edges["total_under"] = {
                "line": under.get("line"),
                "odds": under.get("odds"),
                "implied_prob": round(under_prob, 4),
                "edge_pct": round(under_edge, 2),
                "confidence": get_confidence_rating(under_edge, totals_composite)
            }
    
    best_bet = None
    best_edge = 0
    
    for market_key, edge_data in edges.items():
        if edge_data["confidence"] in ["EDGE", "STRONG_EDGE"]:
            if abs(edge_data["edge_pct"]) > abs(best_edge):
                best_edge = edge_data["edge_pct"]
                best_bet = market_key
    
    return {
        "game_id": game_id,
        "sport": sport,
        "home_team": home_team,
        "away_team": away_team,
        "commence_time": game_time.isoformat(),
        "pillars": {
            "execution": execution,
            "incentives": incentives,
            "shocks": shocks,
            "time_decay": time_decay,
            "flow": flow,
        },
        "pillar_scores": pillar_scores,
        "pillar_weights": PILLAR_WEIGHTS,
        "composite_score": round(composite, 3),
        "consensus_odds": consensus,
        "edges": edges,
        "best_bet": best_bet,
        "best_edge": best_edge,
        "overall_confidence": get_confidence_rating(best_edge, composite) if best_bet else "PASS",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


def analyze_all_games(sport: str) -> list[dict]:
    """Analyze all upcoming games for a sport with ALL markets (including extended)."""
    # Use get_all_markets() instead of get_upcoming_games() to include extended markets
    all_markets_data = odds_client.get_all_markets(sport)
    games = all_markets_data.get("games", [])
    
    logger.info(f"Analyzing {len(games)} games for {sport} with extended markets")
    
    analyses = []
    for game in games:
        try:
            analysis = analyze_game(game, sport)
            analyses.append(analysis)
        except Exception as e:
            logger.error(f"Error analyzing game {game.get('id')}: {e}")
            continue
    
    return analyses


def analyze_all_sports() -> dict[str, list[dict]]:
    """Analyze all upcoming games across all sports."""
    from config import ODDS_API_SPORTS
    
    all_analyses = {}
    for sport in ODDS_API_SPORTS.keys():
        logger.info(f"Analyzing {sport}...")
        analyses = analyze_all_games(sport)
        all_analyses[sport] = analyses
        logger.info(f"Completed {len(analyses)} games for {sport}")
    
    return all_analyses