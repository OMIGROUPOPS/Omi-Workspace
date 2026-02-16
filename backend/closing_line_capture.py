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
    Extract median book lines + Pinnacle-specific lines from game_data bookmakers.
    Pinnacle closing lines are captured separately for CLV calculation.
    """
    home_team = game_data.get("home_team", "")
    bookmakers = game_data.get("bookmakers", [])

    spread_lines = []
    total_lines = []
    ml_home_odds = []
    ml_away_odds = []
    ml_draw_odds = []

    # Track Pinnacle specifically for CLV
    pinnacle_spread = None
    pinnacle_total = None
    pinnacle_ml_home = None
    pinnacle_ml_away = None

    for bk in bookmakers:
        bk_key = (bk.get("key") or "").lower()
        for market in bk.get("markets", []):
            key = market.get("key")
            outcomes = market.get("outcomes", [])

            if key == "spreads":
                for o in outcomes:
                    if o.get("name") == home_team and o.get("point") is not None:
                        spread_lines.append(o["point"])
                        if bk_key == "pinnacle":
                            pinnacle_spread = o["point"]

            elif key == "totals":
                for o in outcomes:
                    if o.get("name") == "Over" and o.get("point") is not None:
                        total_lines.append(o["point"])
                        if bk_key == "pinnacle":
                            pinnacle_total = o["point"]

            elif key == "h2h":
                for o in outcomes:
                    if o.get("name") == home_team:
                        ml_home_odds.append(o["price"])
                        if bk_key == "pinnacle":
                            pinnacle_ml_home = o["price"]
                    elif o.get("name") == "Draw":
                        ml_draw_odds.append(o["price"])
                    else:
                        ml_away_odds.append(o["price"])
                        if bk_key == "pinnacle":
                            pinnacle_ml_away = o["price"]

    return {
        "book_spread": statistics.median(spread_lines) if spread_lines else None,
        "book_total": statistics.median(total_lines) if total_lines else None,
        "book_ml_home": round(statistics.median(ml_home_odds)) if ml_home_odds else None,
        "book_ml_away": round(statistics.median(ml_away_odds)) if ml_away_odds else None,
        "book_ml_draw": round(statistics.median(ml_draw_odds)) if ml_draw_odds else None,
        "pinnacle_spread": pinnacle_spread,
        "pinnacle_total": pinnacle_total,
        "pinnacle_ml_home": pinnacle_ml_home,
        "pinnacle_ml_away": pinnacle_ml_away,
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

            # Pinnacle closing lines for CLV tracking
            pin_spread = book_lines.get("pinnacle_spread")
            pin_total = book_lines.get("pinnacle_total")
            pin_ml_home = book_lines.get("pinnacle_ml_home")
            pin_ml_away = book_lines.get("pinnacle_ml_away")

            if pin_spread is not None:
                closing_row["pinnacle_spread"] = pin_spread
            if pin_total is not None:
                closing_row["pinnacle_total"] = pin_total
            if pin_ml_home is not None:
                closing_row["pinnacle_ml_home"] = pin_ml_home
            if pin_ml_away is not None:
                closing_row["pinnacle_ml_away"] = pin_ml_away

            # Pre-calculate CLV at capture time (OMI fair vs Pinnacle close)
            # Positive CLV = OMI fair line was sharper than Pinnacle
            omi_fair_spread = fair_lines.get("omi_fair_spread")
            if omi_fair_spread is not None and pin_spread is not None:
                spread_clv = abs(omi_fair_spread - pin_spread)
                closing_row["spread_clv"] = round(spread_clv, 2)
                logger.info(
                    f"[ClosingLine] CLV for {game_id}: OMI={omi_fair_spread}, "
                    f"Pinnacle={pin_spread}, CLV={spread_clv:.2f}pts"
                )

            omi_fair_total = fair_lines.get("omi_fair_total")
            if omi_fair_total is not None and pin_total is not None:
                total_clv = abs(omi_fair_total - pin_total)
                closing_row["total_clv"] = round(total_clv, 2)

            # Upsert (update on conflict with game_id)
            # Unknown columns will be silently ignored by Supabase
            try:
                db.client.table("closing_lines").upsert(
                    closing_row, on_conflict="game_id"
                ).execute()
            except Exception as upsert_err:
                # If Pinnacle/CLV columns don't exist yet, retry without them
                for extra_col in ["pinnacle_spread", "pinnacle_total",
                                  "pinnacle_ml_home", "pinnacle_ml_away",
                                  "spread_clv", "total_clv"]:
                    closing_row.pop(extra_col, None)
                db.client.table("closing_lines").upsert(
                    closing_row, on_conflict="game_id"
                ).execute()
                logger.warning(f"[ClosingLine] Pinnacle/CLV columns not in table yet, saved without: {upsert_err}")

            captured += 1
            pin_info = f", Pinnacle={pin_spread}/{pin_total}" if pin_spread or pin_total else ""
            logger.info(
                f"[ClosingLine] Captured {game_id} ({sport_key}): "
                f"spread={book_lines['book_spread']} total={book_lines['book_total']}{pin_info}"
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
