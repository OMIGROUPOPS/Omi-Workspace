"""
Composite History Tracker

Recalculates pillar composites and fair lines for all active games.
Called every 15 minutes by Vercel cron (via POST /api/recalculate-composites)
after odds sync writes fresh data to cached_odds and line_snapshots.

Writes time-series rows to composite_history table for tracking
how OMI's fair pricing evolves over time.
"""
from datetime import datetime, timezone
from typing import Optional
import logging
import statistics

from database import db
from engine.analyzer import analyze_game, implied_prob_to_american

logger = logging.getLogger(__name__)

# Fair line constants — mirror edgescout.ts (lines 59-72)
FAIR_LINE_SPREAD_FACTOR = 0.15
FAIR_LINE_TOTAL_FACTOR = 0.20

SPREAD_TO_PROB_RATE = {
    "basketball_nba": 0.033,
    "basketball_ncaab": 0.030,
    "americanfootball_nfl": 0.027,
    "americanfootball_ncaaf": 0.025,
    "icehockey_nhl": 0.08,
    "baseball_mlb": 0.09,
}


def _round_to_half(value: float) -> float:
    """Round to nearest 0.5 — matches Math.round(x * 2) / 2 in edgescout.ts."""
    return round(value * 2) / 2


def _calculate_fair_spread(book_spread: float, composite_spread: float) -> float:
    """
    Mirror edgescout.ts calculateFairSpread (lines 80-91).
    composite_spread is on 0-1 scale from analyzer.
    """
    deviation = composite_spread * 100 - 50
    adjustment = deviation * FAIR_LINE_SPREAD_FACTOR
    return _round_to_half(book_spread - adjustment)


def _calculate_fair_total(book_total: float, game_env_score: float) -> float:
    """
    Mirror edgescout.ts calculateFairTotal (lines 98-109).
    game_env_score is the game_environment PILLAR score (0-1), not totals composite.
    """
    deviation = game_env_score * 100 - 50
    adjustment = deviation * FAIR_LINE_TOTAL_FACTOR
    return _round_to_half(book_total + adjustment)


def _calculate_fair_ml(fair_spread: float, sport_key: str) -> tuple[int, int]:
    """
    Derive fair ML from fair spread — mirrors edgescout.ts spreadToMoneyline (lines 136-149).
    Returns (fair_ml_home, fair_ml_away).
    """
    rate = SPREAD_TO_PROB_RATE.get(sport_key, 0.03)
    home_prob = max(0.05, min(0.95, 0.50 + (-fair_spread) * rate))
    away_prob = 1 - home_prob
    return (implied_prob_to_american(home_prob), implied_prob_to_american(away_prob))


def _extract_median_lines(game_data: dict) -> dict:
    """
    Extract median book lines from game_data bookmakers (Odds API format).
    Returns {book_spread, book_total, book_ml_home, book_ml_away}.
    """
    home_team = game_data.get("home_team", "")
    bookmakers = game_data.get("bookmakers", [])

    spread_lines = []
    total_lines = []
    ml_home_odds = []
    ml_away_odds = []

    for bk in bookmakers:
        for market in bk.get("markets", []):
            key = market.get("key")
            outcomes = market.get("outcomes", [])

            if key == "spreads":
                for o in outcomes:
                    if o.get("name") == home_team and o.get("point") is not None:
                        spread_lines.append(o["point"])

            elif key == "totals":
                for o in outcomes:
                    if o.get("name") == "Over" and o.get("point") is not None:
                        total_lines.append(o["point"])

            elif key == "h2h":
                for o in outcomes:
                    if o.get("name") == home_team:
                        ml_home_odds.append(o["price"])
                    elif o.get("name") != "Draw":
                        ml_away_odds.append(o["price"])

    return {
        "book_spread": statistics.median(spread_lines) if spread_lines else None,
        "book_total": statistics.median(total_lines) if total_lines else None,
        "book_ml_home": round(statistics.median(ml_home_odds)) if ml_home_odds else None,
        "book_ml_away": round(statistics.median(ml_away_odds)) if ml_away_odds else None,
    }


class CompositeTracker:
    """Recalculates composites + fair lines for all active games."""

    def recalculate_all(self) -> dict:
        """
        Main entry point. For every active (not yet started) game in cached_odds:
        1. Run analyze_game for fresh pillar scores
        2. Extract per-market composites
        3. Calculate fair lines (same formulas as edgescout.ts)
        4. Write row to composite_history
        """
        if not db._is_connected():
            return {"error": "Database not connected", "games_processed": 0, "errors": 0}

        now = datetime.now(timezone.utc).isoformat()

        try:
            result = db.client.table("cached_odds").select(
                "sport_key, game_id, game_data"
            ).gte(
                "game_data->>commence_time", now
            ).execute()
        except Exception as e:
            logger.error(f"[CompositeTracker] Failed to query cached_odds: {e}")
            return {"error": str(e), "games_processed": 0, "errors": 1}

        rows = result.data or []
        logger.info(f"[CompositeTracker] Found {len(rows)} active games to recalculate")

        games_processed = 0
        errors = 0

        for row in rows:
            try:
                sport_key = row["sport_key"]
                game_id = row["game_id"]
                game_data = row["game_data"]

                if not game_data:
                    continue

                # 1. Fresh pillar analysis
                analysis = analyze_game(game_data, sport_key)

                # 2. Per-market composites from pillars_by_market
                pbm = analysis.get("pillars_by_market", {})
                composite_spread = pbm.get("spread", {}).get("full", {}).get("composite")
                composite_total = pbm.get("totals", {}).get("full", {}).get("composite")
                composite_ml = pbm.get("moneyline", {}).get("full", {}).get("composite")

                # 3. Game environment pillar score (for fair total)
                game_env_score = analysis.get("pillar_scores", {}).get("game_environment", 0.5)

                # 4. Median book lines
                book_lines = _extract_median_lines(game_data)
                book_spread = book_lines["book_spread"]
                book_total = book_lines["book_total"]
                book_ml_home = book_lines["book_ml_home"]
                book_ml_away = book_lines["book_ml_away"]

                # 5. Calculate fair lines
                fair_spread = None
                fair_total = None
                fair_ml_home = None
                fair_ml_away = None

                if book_spread is not None and composite_spread is not None:
                    fair_spread = _calculate_fair_spread(book_spread, composite_spread)
                    fair_ml_home, fair_ml_away = _calculate_fair_ml(fair_spread, sport_key)

                if book_total is not None:
                    fair_total = _calculate_fair_total(book_total, game_env_score)

                # 6. Insert row
                db.client.table("composite_history").insert({
                    "game_id": game_id,
                    "sport_key": sport_key,
                    "timestamp": now,
                    "composite_spread": composite_spread,
                    "composite_total": composite_total,
                    "composite_ml": composite_ml,
                    "fair_spread": fair_spread,
                    "fair_total": fair_total,
                    "fair_ml_home": fair_ml_home,
                    "fair_ml_away": fair_ml_away,
                    "book_spread": book_spread,
                    "book_total": book_total,
                    "book_ml_home": book_ml_home,
                    "book_ml_away": book_ml_away,
                }).execute()

                games_processed += 1

            except Exception as e:
                logger.error(f"[CompositeTracker] Error processing {row.get('game_id', '?')}: {e}")
                errors += 1

        summary = {
            "games_processed": games_processed,
            "errors": errors,
            "timestamp": now,
        }
        logger.info(f"[CompositeTracker] Done: {summary}")
        return summary
