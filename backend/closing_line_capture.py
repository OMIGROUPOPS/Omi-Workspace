"""
Closing Line Capture

Captures the final book lines and OMI fair lines shortly before game start.
Runs every 10 minutes via scheduler. For each game starting in the next 5-30
minutes, it snapshots:
  - Median book lines (spread, total, ML) from cached_odds
  - Latest OMI fair lines from composite_history
  - Composite scores at close

Writes to the closing_lines table (one row per game, upsert on game_id).
"""

import logging
import statistics
from datetime import datetime, timezone, timedelta

from database import db

logger = logging.getLogger(__name__)

# Window: capture games starting between 5 and 30 minutes from now
CAPTURE_WINDOW_MIN_MINUTES = 5
CAPTURE_WINDOW_MAX_MINUTES = 30


def _extract_median_lines(game_data: dict) -> dict:
    """
    Extract median book lines from game_data bookmakers (Odds API format).
    Same logic as composite_tracker._extract_median_lines.
    """
    home_team = game_data.get("home_team", "")
    bookmakers = game_data.get("bookmakers", [])

    spread_lines = []
    total_lines = []
    ml_home_odds = []
    ml_away_odds = []
    ml_draw_odds = []

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
                    elif o.get("name") == "Draw":
                        ml_draw_odds.append(o["price"])
                    else:
                        ml_away_odds.append(o["price"])

    return {
        "book_spread": statistics.median(spread_lines) if spread_lines else None,
        "book_total": statistics.median(total_lines) if total_lines else None,
        "book_ml_home": round(statistics.median(ml_home_odds)) if ml_home_odds else None,
        "book_ml_away": round(statistics.median(ml_away_odds)) if ml_away_odds else None,
        "book_ml_draw": round(statistics.median(ml_draw_odds)) if ml_draw_odds else None,
    }


def _get_latest_fair_lines(game_id: str) -> dict:
    """Get the most recent composite_history row for a game."""
    try:
        result = db.client.table("composite_history").select(
            "fair_spread, fair_total, fair_ml_home, fair_ml_away, "
            "composite_spread, composite_total, composite_ml"
        ).eq("game_id", game_id).order(
            "timestamp", desc=True
        ).limit(1).execute()

        if result.data:
            row = result.data[0]
            return {
                "omi_fair_spread": row.get("fair_spread"),
                "omi_fair_total": row.get("fair_total"),
                "omi_fair_ml_home": row.get("fair_ml_home"),
                "omi_fair_ml_away": row.get("fair_ml_away"),
                "composite_spread": row.get("composite_spread"),
                "composite_total": row.get("composite_total"),
                "composite_ml": row.get("composite_ml"),
            }
    except Exception as e:
        logger.warning(f"[ClosingLine] Failed to get fair lines for {game_id}: {e}")

    return {}


def run_closing_line_capture() -> dict:
    """
    Main entry point. Finds games starting in the next 5-30 minutes,
    captures their closing book lines + OMI fair lines.
    """
    if not db._is_connected():
        return {"error": "Database not connected", "captured": 0}

    now = datetime.now(timezone.utc)
    window_start = now + timedelta(minutes=CAPTURE_WINDOW_MIN_MINUTES)
    window_end = now + timedelta(minutes=CAPTURE_WINDOW_MAX_MINUTES)

    try:
        result = db.client.table("cached_odds").select(
            "game_id, sport_key, game_data"
        ).limit(5000).execute()
    except Exception as e:
        logger.error(f"[ClosingLine] Failed to query cached_odds: {e}")
        return {"error": str(e), "captured": 0}

    all_rows = result.data or []

    # Filter to games within the capture window
    eligible = []
    for row in all_rows:
        gd = row.get("game_data") or {}
        ct = gd.get("commence_time")
        if not ct:
            continue
        try:
            game_dt = datetime.fromisoformat(ct.replace("Z", "+00:00"))
            if window_start <= game_dt <= window_end:
                eligible.append(row)
        except (ValueError, AttributeError):
            continue

    if not eligible:
        logger.debug(f"[ClosingLine] No games in capture window ({window_start.isoformat()} - {window_end.isoformat()})")
        return {"captured": 0, "eligible": 0}

    logger.info(f"[ClosingLine] Found {len(eligible)} games in capture window")

    captured = 0
    errors = 0

    for row in eligible:
        try:
            game_id = row["game_id"]
            sport_key = row["sport_key"]
            game_data = row["game_data"]

            # Extract median book lines
            book_lines = _extract_median_lines(game_data)

            # Get latest OMI fair lines from composite_history
            fair_lines = _get_latest_fair_lines(game_id)

            # Build row for upsert
            closing_row = {
                "game_id": game_id,
                "sport_key": sport_key,
                "captured_at": now.isoformat(),
                "book_spread": book_lines["book_spread"],
                "book_total": book_lines["book_total"],
                "book_ml_home": book_lines["book_ml_home"],
                "book_ml_away": book_lines["book_ml_away"],
                "book_ml_draw": book_lines["book_ml_draw"],
                "omi_fair_spread": fair_lines.get("omi_fair_spread"),
                "omi_fair_total": fair_lines.get("omi_fair_total"),
                "omi_fair_ml_home": fair_lines.get("omi_fair_ml_home"),
                "omi_fair_ml_away": fair_lines.get("omi_fair_ml_away"),
                "composite_spread": fair_lines.get("composite_spread"),
                "composite_total": fair_lines.get("composite_total"),
                "composite_ml": fair_lines.get("composite_ml"),
            }

            # Upsert (update on conflict with game_id)
            db.client.table("closing_lines").upsert(
                closing_row, on_conflict="game_id"
            ).execute()

            captured += 1
            logger.info(
                f"[ClosingLine] Captured {game_id} ({sport_key}): "
                f"spread={book_lines['book_spread']} total={book_lines['book_total']}"
            )

        except Exception as e:
            logger.error(f"[ClosingLine] Error capturing {row.get('game_id', '?')}: {e}")
            errors += 1

    summary = {
        "captured": captured,
        "eligible": len(eligible),
        "errors": errors,
        "timestamp": now.isoformat(),
    }
    logger.info(f"[ClosingLine] Done: {summary}")
    return summary
