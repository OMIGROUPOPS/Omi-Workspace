"""
Pillar 5: Market Microstructure & Flow
Weight: 0.25

Measures: Sharp vs public money patterns
- Opening line vs current line movement
- Cross-book line discrepancies
- Reverse line movement
- Steam moves (coordinated sharp action)
"""
from datetime import datetime
from typing import Optional
import logging
import statistics

from data_sources.odds_api import odds_client

logger = logging.getLogger(__name__)


def calculate_flow_score(
    game: dict,
    opening_line: Optional[float] = None,
    line_snapshots: Optional[list] = None
) -> dict:
    """
    Calculate Pillar 5: Market Microstructure & Flow score.
    
    A score > 0.5 means flow suggests value on AWAY team
    A score < 0.5 means flow suggests value on HOME team
    A score = 0.5 means balanced/unclear flow signals
    """
    parsed = odds_client.parse_game_odds(game)
    bookmakers = parsed["bookmakers"]
    
    if not bookmakers:
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
    
    spreads_by_book = {}
    for book_key, markets in bookmakers.items():
        if "spreads" in markets and "home" in markets["spreads"]:
            spreads_by_book[book_key] = markets["spreads"]["home"]["line"]
    
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
    
    if movement_direction == "toward_away":
        base_score += min(abs(line_movement) * 0.08, 0.2)
    elif movement_direction == "toward_home":
        base_score -= min(abs(line_movement) * 0.08, 0.2)
    
    if sharpest_book and sharpest_line != consensus_line:
        sharp_deviation = sharpest_line - consensus_line
        if abs(sharp_deviation) >= 0.5:
            base_score += sharp_deviation * 0.1
            reasoning_parts.append(f"Sharp book ({sharpest_book}) at {sharpest_line} vs consensus {consensus_line:.1f}")
    
    if book_agreement < 0.7:
        reasoning_parts.append(f"Low book agreement ({book_agreement:.2f}) suggests uncertainty")
    
    if abs(velocity) >= 1.0:
        base_score += velocity * 0.05
    
    score = max(0.0, min(1.0, base_score))
    
    if not reasoning_parts:
        reasoning_parts.append("Market flow appears balanced across books")
    
    return {
        "score": round(score, 3),
        "spread_variance": round(variance, 3),
        "consensus_line": round(consensus_line, 2),
        "sharpest_line": round(sharpest_line, 2),
        "book_agreement": round(book_agreement, 3),
        "breakdown": {
            "spreads_by_book": spreads_by_book,
            "book_count": book_count,
            "stdev": round(stdev, 3),
            "outlier_books": outlier_books,
            "line_movement": round(line_movement, 2),
            "movement_direction": movement_direction,
            "velocity": round(velocity, 2),
            "sharpest_book": sharpest_book
        },
        "reasoning": "; ".join(reasoning_parts)
    }


def _analyze_moneyline_flow(bookmakers: dict, parsed: dict) -> dict:
    """Fallback flow analysis using moneyline odds when spreads unavailable."""
    home_odds_list = []
    
    for book_key, markets in bookmakers.items():
        if "h2h" in markets:
            if "home" in markets["h2h"]:
                home_odds_list.append(markets["h2h"]["home"])
    
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
    avg_home_prob = sum(home_probs) / len(home_probs)
    
    if len(home_probs) >= 2:
        prob_variance = statistics.variance(home_probs)
    else:
        prob_variance = 0
    
    score = 0.5
    if prob_variance > 0.01:
        score += 0.1 if avg_home_prob > 0.5 else -0.1
    
    return {
        "score": round(score, 3),
        "spread_variance": 0.0,
        "consensus_line": 0.0,
        "sharpest_line": 0.0,
        "book_agreement": round(1 - min(prob_variance * 10, 1), 3),
        "breakdown": {
            "home_odds_list": home_odds_list,
            "avg_home_prob": round(avg_home_prob, 4),
            "prob_variance": round(prob_variance, 4)
        },
        "reasoning": f"Moneyline flow analysis: avg home prob {avg_home_prob:.1%}"
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