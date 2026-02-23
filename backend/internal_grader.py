"""
OMI Edge - Internal Grader
Enhanced grading with prediction_grades table for per-market/period/book granularity.
Edge model: each point of OMI-vs-book disagreement ≈ 3% win probability.
Book odds are display-only — not used in edge math.
"""

import math
import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from supabase import create_client, Client
from results_tracker import ResultsTracker
from espn_scores import AutoGrader

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

logger = logging.getLogger(__name__)

# Fair line factors (must match edgescout.ts)
FAIR_LINE_SPREAD_FACTOR = 0.15
FAIR_LINE_TOTAL_FACTOR = 0.10
FAIR_LINE_ML_FACTOR = 0.01

# Industry standard: ~3% win probability per point of spread difference
PROB_PER_POINT = 0.03
# Totals are higher-variance — 1 point of total difference ≈ 1.5% win probability
PROB_PER_TOTAL_POINT = 0.015

# Cap displayed American odds to avoid absurd values
ODDS_CAP = 500  # max ±500

# Only grade against books where users actually place bets
GRADING_BOOKS = {"fanduel", "draftkings"}

# Spread/total odds should be in normal juice range (-200 to +200).
# Anything outside this is either corrupt data or ML odds in the wrong slot.
SPREAD_ODDS_MIN = -250
SPREAD_ODDS_MAX = 250


def _clamp_juice(odds: int, market_type: str) -> int:
    """Clamp spread/total odds to reasonable range. Return -110 for corrupt values."""
    if market_type in ("spread", "total"):
        if abs(odds) > 250 or odds == 0:
            return -110
    return odds

# Sport key normalization — database has mixed formats
SPORT_DISPLAY = {
    "basketball_nba": "NBA", "BASKETBALL_NBA": "NBA", "NBA": "NBA",
    "americanfootball_nfl": "NFL", "AMERICANFOOTBALL_NFL": "NFL", "NFL": "NFL",
    "icehockey_nhl": "NHL", "ICEHOCKEY_NHL": "NHL", "NHL": "NHL",
    "americanfootball_ncaaf": "NCAAF", "AMERICANFOOTBALL_NCAAF": "NCAAF", "NCAAF": "NCAAF",
    "basketball_ncaab": "NCAAB", "BASKETBALL_NCAAB": "NCAAB", "NCAAB": "NCAAB",
    "soccer_epl": "EPL", "SOCCER_EPL": "EPL", "EPL": "EPL",
}


def _normalize_sport(raw: str) -> str:
    """Normalize any sport key variant to short display form."""
    return SPORT_DISPLAY.get(raw, raw)


# Soccer sports show ML+totals; everything else shows spread+totals
SOCCER_SPORTS = {"EPL", "SOCCER_EPL", "LA_LIGA", "SERIE_A", "BUNDESLIGA",
                 "LIGUE_1", "MLS", "CHAMPIONS_LEAGUE"}


def _is_soccer(sport_short: str) -> bool:
    return sport_short in SOCCER_SPORTS or "soccer" in sport_short.lower()


def determine_signal(edge_pct, market_type="spread") -> str:
    """Determine signal tier from IP edge %. Always returns a valid string.
    < 1%  = NO EDGE
    1-3%  = LOW EDGE
    3-5%  = MID EDGE
    5-8%  = HIGH EDGE
    8%+   = MAX EDGE (genuine strong signal — caps prevent garbage)

    ML edges are naturally larger than spread/total edges because implied
    probability divergences amplify through the 3-way market.  Apply 0.6x
    scaling so a 5% ML edge maps to the same tier as a 3% spread edge.
    """
    if edge_pct is None:
        return "NO EDGE"
    try:
        ae = abs(float(edge_pct))
    except (TypeError, ValueError):
        return "NO EDGE"
    # ML edges are systematically inflated — scale down before tier mapping
    if market_type in ("moneyline", "ml", "h2h"):
        ae = ae * 0.6
    if ae >= 8:
        return "MAX EDGE"
    if ae >= 5:
        return "HIGH EDGE"
    if ae >= 3:
        return "MID EDGE"
    if ae >= 1:
        return "LOW EDGE"
    return "NO EDGE"


def _cap_edge_display(raw_edge, threshold=8.0, decay=0.3):
    """Soft-cap edge for display — mirrors composite_tracker._cap_edge().
    Above threshold, apply diminishing returns so 12% raw → 9.2% display."""
    if raw_edge is None:
        return raw_edge
    if raw_edge <= threshold:
        return raw_edge
    return round(threshold + (raw_edge - threshold) * decay, 2)


def edge_to_confidence(edge_pct: float) -> float:
    """Map edge % to confidence % via linear interpolation within bands.
    < 1%  (NO EDGE)   → 50-54%
    1-3%  (LOW EDGE)  → 55-59%
    3-5%  (MID EDGE)  → 60-65%
    5-8%  (HIGH EDGE) → 66-70%
    8%+   (MAX EDGE)  → 71-75% (capped)
    Returns float with 1 decimal precision.
    """
    ae = abs(edge_pct)
    if ae < 1:
        return round(50 + (ae / 1.0) * 4, 1)
    if ae < 3:
        return round(55 + ((ae - 1) / 2.0) * 4, 1)
    if ae < 5:
        return round(60 + ((ae - 3) / 2.0) * 5, 1)
    if ae < 8:
        return round(66 + ((ae - 5) / 3.0) * 4, 1)
    return round(min(75, 71 + ((ae - 8) / 8.0) * 4), 1)


def composite_to_confidence_tier(composite: float) -> int:
    """Map composite score (0-1) to confidence tier.

    Never returns None — low-composite games get tier 50 so they are
    still graded (needed for calibration) but flagged as low-signal.
    """
    score = composite * 100
    if score >= 70:
        return 70
    elif score >= 65:
        return 65
    elif score >= 60:
        return 60
    elif score >= 55:
        return 55
    return 50


def american_to_implied(odds) -> float:
    """Convert American odds to implied probability (0-1)."""
    if odds is None:
        return 0.5
    odds = int(odds)
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    if odds > 0:
        return 100 / (odds + 100)
    return 0.5


def implied_to_american(prob: float) -> int:
    """Convert implied probability (0-1) to American odds."""
    if prob <= 0.01 or prob >= 0.99:
        return 0
    if prob >= 0.5:
        return int(-100 * prob / (1 - prob))
    return int(100 * (1 - prob) / prob)


def calc_edge_pct(fair_value: float, book_line: float, market_type: str = "spread", sport_key: str = "") -> float:
    """Calculate edge as logistic probability percentage.

    Uses the unified logistic formula from edge_calc.py.
    sport_key is required for accurate k-value lookup; defaults to generic 0.120.
    """
    from edge_calc import calculate_edge
    return round(calculate_edge(book_line, fair_value, market_type, sport_key), 1)


def calc_fair_price(fair_value: float, book_line: float, market_type: str = "spread", sport_key: str = "") -> int:
    """Convert OMI fair value at a book's line to capped American odds.

    Uses logistic spread-to-probability, then converts to American.
    Caps at ±ODDS_CAP to avoid absurd display values.
    """
    from edge_calc import spread_to_win_prob
    if market_type in ("total", "totals"):
        diff = book_line - fair_value
        fair_prob = spread_to_win_prob(diff, sport_key)
    else:
        fair_prob = spread_to_win_prob(fair_value, sport_key)
    fair_prob = min(0.95, max(0.05, fair_prob))
    raw = implied_to_american(fair_prob)
    if raw == 0:
        return 0
    if raw < -ODDS_CAP:
        return -ODDS_CAP
    if raw > ODDS_CAP:
        return ODDS_CAP
    return raw


class InternalGrader:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase credentials")
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.tracker = ResultsTracker()

    def grade_games(self, sport: Optional[str] = None) -> dict:
        """
        Grade completed games and generate prediction_grades rows.

        1. Bootstrap game_results from predictions (if not already present)
        2. Call AutoGrader to grade game_results
        3. For each newly graded game, generate prediction_grades rows
        """
        bootstrapped = self._bootstrap_game_results(sport)
        logger.info(f"[InternalGrader] Bootstrapped {bootstrapped} game_results from predictions")

        grader = AutoGrader(self.tracker)
        auto_result = grader.grade_completed_games(sport)

        graded_count = 0
        games_with_grades = 0
        errors = []

        details = auto_result.get("details", [])
        for detail in details:
            game_id = detail.get("game_id")
            try:
                count = self._generate_prediction_grades(game_id)
                graded_count += count
                if count > 0:
                    games_with_grades += 1
            except Exception as e:
                logger.error(f"Error generating prediction grades for {game_id}: {e}")
                errors.append({"game_id": game_id, "error": str(e)})

        logger.info(
            f"[InternalGrader] Prediction grades: {graded_count} inserted successfully "
            f"from {games_with_grades}/{len(details)} games ({len(errors)} errors)"
        )

        return {
            "auto_grader": auto_result,
            "prediction_grades_created": graded_count,
            "games_with_grades": games_with_grades,
            "bootstrapped_game_results": bootstrapped,
            "errors": errors,
        }

    def _bootstrap_game_results(self, sport: Optional[str] = None) -> int:
        """Create game_results rows from predictions for completed games."""
        now = datetime.now(timezone.utc)
        cutoff = now.isoformat()
        # Only look back 30 days — keeps query well under Supabase's 1000-row
        # default limit that was silently truncating recent games.
        lookback = (now - timedelta(days=30)).isoformat()
        count = 0

        try:
            query = self.client.table("predictions").select(
                "game_id, sport_key"
            ).gte("commence_time", lookback).lt("commence_time", cutoff).order(
                "commence_time", desc=True
            )

            if sport:
                query = query.eq("sport_key", sport)

            result = query.execute()
            predictions = result.data or []

            if not predictions:
                return 0

            game_ids = [p["game_id"] for p in predictions]
            existing_ids = set()
            for i in range(0, len(game_ids), 50):
                batch = game_ids[i:i+50]
                existing = self.client.table("game_results").select(
                    "game_id"
                ).in_("game_id", batch).execute()
                existing_ids.update(r["game_id"] for r in (existing.data or []))

            for pred in predictions:
                gid = pred["game_id"]
                if gid not in existing_ids:
                    try:
                        self.tracker.snapshot_prediction_at_close(gid, pred["sport_key"])
                        count += 1
                    except Exception as e:
                        logger.warning(f"[InternalGrader] Failed to bootstrap {gid}: {e}")

        except Exception as e:
            logger.error(f"[InternalGrader] Bootstrap error: {e}")

        return count

    # ------------------------------------------------------------------
    # Line extraction from line_snapshots
    # ------------------------------------------------------------------

    def _get_book_lines(self, game_id: str) -> dict:
        """Get closing lines per book from line_snapshots.

        Returns structured data with odds for both sides of each market:
        {
            "fanduel": {
                "spread": {"line": -3.5, "home_odds": -110, "away_odds": -110},
                "total":  {"line": 242.5, "over_odds": -110, "under_odds": -112},
                "moneyline": {"home_odds": -150, "away_odds": +130},
            }
        }
        """
        try:
            result = self.client.table("line_snapshots").select(
                "book_key, market_type, line, odds, outcome_type"
            ).eq("game_id", game_id).eq(
                "market_period", "full"
            ).order("snapshot_time", desc=True).execute()

            snapshots = result.data or []
            books: dict = {}
            seen: set = set()

            for snap in snapshots:
                book = snap.get("book_key", "consensus")
                mtype = snap.get("market_type")
                outcome = snap.get("outcome_type") or ""  # None → ""

                if book not in books:
                    books[book] = {}

                if mtype == "spread":
                    if "spread" not in books[book]:
                        books[book]["spread"] = {"line": None, "home_odds": None, "away_odds": None}
                    key = f"{book}_spread_{outcome}"
                    if key in seen:
                        continue
                    seen.add(key)
                    if outcome in ("home", ""):
                        books[book]["spread"]["line"] = snap.get("line", 0)
                        books[book]["spread"]["home_odds"] = snap.get("odds")
                    elif outcome == "away":
                        books[book]["spread"]["away_odds"] = snap.get("odds")
                        # If no home-perspective line yet, derive from away
                        if books[book]["spread"]["line"] is None:
                            books[book]["spread"]["line"] = -snap.get("line", 0)

                elif mtype == "total":
                    if "total" not in books[book]:
                        books[book]["total"] = {"line": None, "over_odds": None, "under_odds": None}
                    key = f"{book}_total_{outcome}"
                    if key in seen:
                        continue
                    seen.add(key)
                    if outcome in ("over", ""):
                        books[book]["total"]["line"] = snap.get("line", 0)
                        books[book]["total"]["over_odds"] = snap.get("odds")
                    elif outcome == "under":
                        books[book]["total"]["under_odds"] = snap.get("odds")

                elif mtype == "moneyline":
                    if "moneyline" not in books[book]:
                        books[book]["moneyline"] = {"home_odds": None, "away_odds": None}
                    key = f"{book}_ml_{outcome}"
                    if key in seen:
                        continue
                    seen.add(key)
                    if outcome == "home":
                        books[book]["moneyline"]["home_odds"] = snap.get("odds")
                    elif outcome == "away":
                        books[book]["moneyline"]["away_odds"] = snap.get("odds")

            return books
        except Exception as e:
            logger.error(f"Error getting book lines for {game_id}: {e}")
            return {}

    # ------------------------------------------------------------------
    # Prediction grade generation
    # ------------------------------------------------------------------

    def _generate_prediction_grades(self, game_id: str) -> int:
        """Generate prediction_grades rows for a graded game."""
        # Guard: skip if this game has already been graded
        existing = self.client.table("prediction_grades").select("id").eq(
            "game_id", game_id
        ).limit(1).execute()
        if existing.data:
            logger.info(f"[GenGrades] {game_id}: already graded, skipping")
            return 0

        result = self.client.table("game_results").select("*").eq(
            "game_id", game_id
        ).single().execute()

        if not result.data:
            logger.warning(f"[GenGrades] {game_id}: no game_results row found")
            return 0

        game = result.data

        # Guard: skip pre-calibration games (model recalibrated Feb 16 2026)
        commence_time = game.get("commence_time")
        if commence_time:
            try:
                game_date = datetime.fromisoformat(str(commence_time).replace("Z", "+00:00"))
                calibration_cutoff = datetime(2026, 2, 16, tzinfo=timezone.utc)
                if game_date < calibration_cutoff:
                    logger.info(f"[GenGrades] {game_id}: pre-calibration game ({commence_time}), skipping")
                    return 0
            except (ValueError, TypeError):
                pass  # If date parsing fails, proceed with grading

        home_score = game.get("home_score")
        away_score = game.get("away_score")

        if home_score is None or away_score is None:
            logger.warning(f"[GenGrades] {game_id}: scores missing (home={home_score}, away={away_score})")
            return 0

        sport_key = _normalize_sport(game.get("sport_key", ""))
        raw_composite = game.get("composite_score")
        composite = raw_composite if raw_composite is not None and raw_composite > 0 else 0.5
        tier = composite_to_confidence_tier(composite)

        if tier <= 50:
            logger.info(
                f"[GenGrades] {game_id}: composite {composite:.3f} (raw={raw_composite}) "
                f"→ tier={tier} (low signal, will still grade)"
            )

        final_spread = home_score - away_score
        final_total = home_score + away_score

        # Get closing lines from game_results
        closing_spread = game.get("closing_spread_home")
        closing_total = game.get("closing_total_line")
        closing_ml_home = game.get("closing_ml_home")
        closing_ml_away = game.get("closing_ml_away")

        book_lines = self._get_book_lines(game_id)

        # Fallback: if closing lines are missing, derive consensus from
        # the median of available book lines so we can still grade.
        if closing_spread is None or closing_total is None:
            all_spreads = []
            all_totals = []
            all_ml_home = []
            all_ml_away = []
            for bdata in book_lines.values():
                s = bdata.get("spread", {}).get("line")
                if s is not None:
                    all_spreads.append(s)
                t = bdata.get("total", {}).get("line")
                if t is not None:
                    all_totals.append(t)
                mh = bdata.get("moneyline", {}).get("home_odds")
                ma = bdata.get("moneyline", {}).get("away_odds")
                if mh is not None:
                    all_ml_home.append(mh)
                if ma is not None:
                    all_ml_away.append(ma)

            if closing_spread is None and all_spreads:
                all_spreads.sort()
                closing_spread = all_spreads[len(all_spreads) // 2]
                logger.info(f"[GenGrades] {game_id}: used median book spread as consensus: {closing_spread}")
            if closing_total is None and all_totals:
                all_totals.sort()
                closing_total = all_totals[len(all_totals) // 2]
                logger.info(f"[GenGrades] {game_id}: used median book total as consensus: {closing_total}")
            if closing_ml_home is None and all_ml_home:
                all_ml_home.sort()
                closing_ml_home = all_ml_home[len(all_ml_home) // 2]
            if closing_ml_away is None and all_ml_away:
                all_ml_away.sort()
                closing_ml_away = all_ml_away[len(all_ml_away) // 2]

        # Calculate OMI fair lines — sport-specific caps prevent hallucinated edges
        SPREAD_CAP_BY_SPORT = {
            "NCAAB": 4.0, "NBA": 3.0, "NFL": 3.0, "NCAAF": 3.0,
            "NHL": 1.5, "EPL": 1.0,
        }
        TOTAL_CAP_BY_SPORT = {
            "NCAAB": 6.0, "NBA": 5.0, "NFL": 5.0, "NCAAF": 5.0,
            "NHL": 1.0, "EPL": 1.0,
        }
        spread_cap = SPREAD_CAP_BY_SPORT.get(sport_key, 3.0)
        total_cap = TOTAL_CAP_BY_SPORT.get(sport_key, 4.0)
        FAIR_ML_PROB_CAP = 0.08 # max ±8% implied probability

        fair_spread = None
        if closing_spread is not None:
            confidence = max(0.40, abs(composite - 0.50) * 2)
            raw_adj = (composite - 0.5) * FAIR_LINE_SPREAD_FACTOR * 10 * confidence
            capped_adj = max(-spread_cap, min(spread_cap, raw_adj))
            if abs(raw_adj) > spread_cap:
                logger.warning(
                    f"[FairCap] {game_id}: spread adjustment capped "
                    f"{raw_adj:.1f} -> {capped_adj:.1f} (cap=±{spread_cap})"
                )
            fair_spread = closing_spread + capped_adj

        fair_total = None
        game_env = game.get("pillar_game_environment") or composite
        if closing_total is not None:
            confidence = max(0.40, abs(game_env - 0.50) * 2)
            raw_adj = (game_env - 0.5) * FAIR_LINE_TOTAL_FACTOR * 10 * confidence
            capped_adj = max(-total_cap, min(total_cap, raw_adj))
            if abs(raw_adj) > total_cap:
                logger.warning(
                    f"[FairCap] {game_id}: total adjustment capped "
                    f"{raw_adj:.1f} -> {capped_adj:.1f} (cap=±{total_cap})"
                )
            fair_total = closing_total + capped_adj

        if not book_lines:
            logger.info(
                f"[GenGrades] {game_id}: no line_snapshots found. "
                f"closing: spread={closing_spread}, total={closing_total}, "
                f"ml={closing_ml_home}/{closing_ml_away}"
            )
        else:
            grading_books_found = [b for b in book_lines if b in GRADING_BOOKS]
            logger.info(
                f"[GenGrades] {game_id}: book_lines={list(book_lines.keys())}, "
                f"grading_books={grading_books_found}, composite={composite:.3f}, tier={tier}, "
                f"fair_spread={fair_spread}, fair_total={fair_total}"
            )

        rows_created = 0

        for book_name, book_data in book_lines.items():
            if book_name not in GRADING_BOOKS:
                continue

            # Spread
            spread_data = book_data.get("spread")
            if fair_spread is not None and spread_data and spread_data.get("line") is not None:
                book_spread = spread_data["line"]

                # Skip if book diverges wildly from consensus (likely stale/bad data)
                if closing_spread is not None and abs(book_spread - closing_spread) > spread_cap * 2:
                    logger.warning(
                        f"[GenGrades] {game_id}: {book_name} spread {book_spread} "
                        f"diverges {abs(book_spread - closing_spread):.1f}pts from consensus "
                        f"{closing_spread} (threshold=±{spread_cap * 2}), skipping"
                    )
                    continue

                gap = fair_spread - book_spread

                if gap > 0:
                    prediction_side = "away"
                    book_odds = _clamp_juice(spread_data.get("away_odds") or -110, "spread")
                    actual_result = "away_covered" if final_spread < closing_spread else (
                        "push" if final_spread == closing_spread else "home_covered"
                    )
                    is_correct = final_spread < book_spread
                else:
                    prediction_side = "home"
                    book_odds = _clamp_juice(spread_data.get("home_odds") or -110, "spread")
                    actual_result = "home_covered" if final_spread > closing_spread else (
                        "push" if final_spread == closing_spread else "away_covered"
                    )
                    is_correct = final_spread > book_spread

                if final_spread == book_spread:
                    actual_result = "push"
                    is_correct = None

                # Edge as implied probability %
                edge_pct = calc_edge_pct(fair_spread, book_spread, "spread", sport_key)

                # Confidence penalty: large gap likely means bad data, not real edge
                if abs(fair_spread - book_spread) > 3:
                    edge_pct = round(edge_pct * 0.70, 1)

                signal = determine_signal(edge_pct)
                logger.info(
                    f"Edge: game={game_id} market=spread book={book_name} "
                    f"fair={fair_spread:.2f} book_raw={book_spread} "
                    f"diff={abs(fair_spread - book_spread):.2f} edge_pct={edge_pct}%"
                )

                if self._upsert_prediction_grade({
                    "game_id": game_id,
                    "sport_key": sport_key,
                    "market_type": "spread",
                    "period": "full",
                    "omi_fair_line": fair_spread,
                    "book_line": book_spread,
                    "book_name": book_name,
                    "book_odds": int(book_odds),
                    "gap": gap,
                    "signal": signal,
                    "confidence_tier": tier,
                    "prediction_side": prediction_side,
                    "actual_result": actual_result,
                    "is_correct": is_correct,
                    "pillar_composite": composite,
                    "ceq_score": None,
                    "graded_at": datetime.now(timezone.utc).isoformat(),
                }):
                    rows_created += 1

            # Total
            total_data = book_data.get("total")
            if fair_total is not None and total_data and total_data.get("line") is not None:
                book_total = total_data["line"]

                # Skip if book diverges wildly from consensus (likely stale/bad data)
                if closing_total is not None and abs(book_total - closing_total) > total_cap * 2:
                    logger.warning(
                        f"[GenGrades] {game_id}: {book_name} total {book_total} "
                        f"diverges {abs(book_total - closing_total):.1f}pts from consensus "
                        f"{closing_total} (threshold=±{total_cap * 2}), skipping"
                    )
                    continue

                gap = fair_total - book_total

                if gap > 0:
                    prediction_side = "over"
                    book_odds = _clamp_juice(total_data.get("over_odds") or -110, "total")
                    is_correct = final_total > book_total
                else:
                    prediction_side = "under"
                    book_odds = _clamp_juice(total_data.get("under_odds") or -110, "total")
                    is_correct = final_total < book_total

                if final_total == book_total:
                    actual_result = "push"
                    is_correct = None
                else:
                    actual_result = "over" if final_total > book_total else "under"

                edge_pct = calc_edge_pct(fair_total, book_total, "total", sport_key)

                # Confidence penalty: large total gap likely means bad data
                if abs(fair_total - book_total) > 5:
                    edge_pct = round(edge_pct * 0.70, 1)

                signal = determine_signal(edge_pct)
                logger.info(
                    f"Edge: game={game_id} market=total book={book_name} "
                    f"fair={fair_total:.2f} book_raw={book_total} "
                    f"diff={abs(fair_total - book_total):.2f} edge_pct={edge_pct}%"
                )

                if self._upsert_prediction_grade({
                    "game_id": game_id,
                    "sport_key": sport_key,
                    "market_type": "total",
                    "period": "full",
                    "omi_fair_line": fair_total,
                    "book_line": book_total,
                    "book_name": book_name,
                    "book_odds": int(book_odds),
                    "gap": gap,
                    "signal": signal,
                    "confidence_tier": tier,
                    "prediction_side": prediction_side,
                    "actual_result": actual_result,
                    "is_correct": is_correct,
                    "pillar_composite": composite,
                    "ceq_score": None,
                    "graded_at": datetime.now(timezone.utc).isoformat(),
                }):
                    rows_created += 1

            # Moneyline — excluded for basketball/football (35% / -33% ROI across 237 picks).
            # Re-enabled for soccer only (3-way ML is the primary market).
            is_soccer_game = _is_soccer(sport_key)
            if is_soccer_game and closing_ml_home is not None and closing_ml_away is not None:
                for book_name, book_data in book_lines.items():
                    if book_name not in GRADING_BOOKS:
                        continue
                    ml_data = book_data.get("h2h") or book_data.get("moneyline")
                    if not ml_data:
                        continue
                    book_ml_h = ml_data.get("home_odds")
                    book_ml_a = ml_data.get("away_odds")
                    if book_ml_h is None or book_ml_a is None:
                        continue

                    # Use OMI fair ML probs
                    fair_hp = american_to_implied(float(closing_ml_home))
                    fair_ap = american_to_implied(float(closing_ml_away))
                    book_hp = american_to_implied(book_ml_h)

                    # OMI says home is underpriced → bet home; overpriced → bet away
                    if fair_hp > book_hp:
                        prediction_side = "home"
                        book_odds = int(book_ml_h)
                        is_correct = home_score > away_score
                    else:
                        prediction_side = "away"
                        book_odds = int(book_ml_a)
                        is_correct = away_score > home_score

                    # Draw = push for ML grading
                    if home_score == away_score:
                        is_correct = None
                        actual_result = "draw"
                    else:
                        actual_result = "home_win" if home_score > away_score else "away_win"

                    edge_pct = round(abs(fair_hp - book_hp) * 100, 1)
                    signal = determine_signal(edge_pct, market_type="moneyline")

                    gap = fair_hp - book_hp  # positive = home underpriced

                    if self._upsert_prediction_grade({
                        "game_id": game_id,
                        "sport_key": sport_key,
                        "market_type": "moneyline",
                        "period": "full",
                        "omi_fair_line": round(fair_hp * 100, 1),
                        "book_line": round(book_hp * 100, 1),
                        "book_name": book_name,
                        "book_odds": book_odds,
                        "gap": round(gap * 100, 1),
                        "signal": signal,
                        "confidence_tier": tier,
                        "prediction_side": prediction_side,
                        "actual_result": actual_result,
                        "is_correct": is_correct,
                        "pillar_composite": composite,
                        "ceq_score": None,
                        "graded_at": datetime.now(timezone.utc).isoformat(),
                    }):
                        rows_created += 1

        # Log exchange accuracy comparisons (if exchange data exists for this game)
        if rows_created > 0:
            try:
                ex_logged = self._log_exchange_accuracy(
                    game_id, sport_key, fair_spread, fair_total,
                    final_spread, final_total, book_lines,
                )
                if ex_logged > 0:
                    logger.info(f"[GenGrades] {game_id}: logged {ex_logged} exchange accuracy rows")
            except Exception as e:
                logger.warning(f"[GenGrades] Exchange accuracy logging failed for {game_id}: {e}")

        return rows_created

    def _log_exchange_accuracy(self, game_id: str, sport_key: str,
                                fair_spread: float, fair_total: float,
                                final_spread: float, final_total: float,
                                book_lines: dict) -> int:
        """Check if exchange data exists for this game and log accuracy comparisons.

        Compares exchange implied probability vs book implied probability
        vs actual outcome for each matched exchange contract.
        """
        try:
            # Fetch exchange data matched to this game
            result = self.client.table("exchange_data").select(
                "exchange, market_type, yes_price, mapped_game_id, contract_ticker"
            ).eq("mapped_game_id", game_id).order(
                "snapshot_time", desc=True
            ).limit(20).execute()

            exchange_rows = result.data or []
            if not exchange_rows:
                return 0

            # Deduplicate by (exchange, market_type) — take latest
            seen = set()
            deduped = []
            for r in exchange_rows:
                key = (r["exchange"], r.get("market_type", ""))
                if key not in seen:
                    seen.add(key)
                    deduped.append(r)

            logged = 0
            for ex_row in deduped:
                exchange = ex_row["exchange"]
                mtype = ex_row.get("market_type", "moneyline")
                yes_price = ex_row.get("yes_price")
                if yes_price is None:
                    continue

                exchange_implied = yes_price / 100.0  # yes_price is 0-100

                # Determine actual binary outcome and book implied prob
                actual_binary = None
                book_implied = None
                actual_value = None

                if mtype == "spread" and fair_spread is not None:
                    actual_value = final_spread
                    # For spread: exchange yes_price typically = home covers prob
                    # Actual: did home cover the spread?
                    # We need the book spread to determine "covered"
                    for bname, bdata in book_lines.items():
                        if bname not in ("fanduel", "draftkings"):
                            continue
                        s = bdata.get("spread", {}).get("line")
                        if s is not None:
                            actual_binary = 1.0 if final_spread > s else 0.0
                            h_odds = bdata.get("spread", {}).get("home_odds") or -110
                            book_implied = american_to_implied(h_odds)
                            self._insert_accuracy_row(
                                game_id, sport_key, mtype, exchange, bname,
                                exchange_implied, book_implied, None,
                                "home_covered" if actual_binary == 1 else "away_covered",
                                actual_value, actual_binary,
                            )
                            logged += 1

                elif mtype == "total" and fair_total is not None:
                    actual_value = final_total
                    for bname, bdata in book_lines.items():
                        if bname not in ("fanduel", "draftkings"):
                            continue
                        t = bdata.get("total", {}).get("line")
                        if t is not None:
                            actual_binary = 1.0 if final_total > t else 0.0
                            o_odds = bdata.get("total", {}).get("over_odds") or -110
                            book_implied = american_to_implied(o_odds)
                            self._insert_accuracy_row(
                                game_id, sport_key, mtype, exchange, bname,
                                exchange_implied, book_implied, None,
                                "over" if actual_binary == 1 else "under",
                                actual_value, actual_binary,
                            )
                            logged += 1

                elif mtype == "moneyline":
                    for bname, bdata in book_lines.items():
                        if bname not in ("fanduel", "draftkings"):
                            continue
                        ml = bdata.get("moneyline", {})
                        h_odds = ml.get("home_odds")
                        if h_odds is not None:
                            book_implied = american_to_implied(h_odds)
                            actual_binary = 1.0 if final_spread > 0 else 0.0
                            self._insert_accuracy_row(
                                game_id, sport_key, mtype, exchange, bname,
                                exchange_implied, book_implied, None,
                                "home_win" if actual_binary == 1 else "away_win",
                                final_spread, actual_binary,
                            )
                            logged += 1

            return logged
        except Exception as e:
            logger.warning(f"[ExchangeAccuracy] Error for {game_id}: {e}")
            return 0

    def _insert_accuracy_row(self, game_id, sport_key, market_type, exchange,
                              book_name, exchange_implied, book_implied,
                              omi_fair_prob, actual_result, actual_value,
                              actual_binary):
        """Insert a single exchange_accuracy_log row."""
        try:
            ex_error = abs(exchange_implied - actual_binary) if actual_binary is not None else None
            bk_error = abs(book_implied - actual_binary) if book_implied is not None and actual_binary is not None else None
            ex_closer = (ex_error < bk_error) if ex_error is not None and bk_error is not None else None

            self.client.table("exchange_accuracy_log").insert({
                "game_id": game_id,
                "sport_key": sport_key,
                "market_type": market_type,
                "exchange": exchange,
                "book_name": book_name,
                "exchange_implied_prob": round(exchange_implied, 4) if exchange_implied is not None else None,
                "book_implied_prob": round(book_implied, 4) if book_implied is not None else None,
                "omi_fair_prob": round(omi_fair_prob, 4) if omi_fair_prob is not None else None,
                "actual_result": actual_result,
                "actual_value": round(actual_value, 2) if actual_value is not None else None,
                "exchange_error": round(ex_error, 4) if ex_error is not None else None,
                "book_error": round(bk_error, 4) if bk_error is not None else None,
                "exchange_closer": ex_closer,
            }).execute()
        except Exception as e:
            logger.warning(f"[ExchangeAccuracy] Insert failed: {e}")

    def _upsert_prediction_grade(self, record: dict) -> bool:
        """Insert a prediction_grades row. Returns True on success."""
        try:
            self.client.table("prediction_grades").insert(record).execute()
            return True
        except Exception as e:
            logger.error(
                f"Error inserting prediction grade: {e} | "
                f"game={record.get('game_id')} market={record.get('market_type')} "
                f"book={record.get('book_name')}"
            )
            return False

    # ------------------------------------------------------------------
    # Performance aggregation
    # ------------------------------------------------------------------

    def get_performance(
        self,
        sport: Optional[str] = None,
        days: int = 30,
        market: Optional[str] = None,
        confidence_tier: Optional[int] = None,
        signal: Optional[str] = None,
        since: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> dict:
        """Query prediction_grades and aggregate performance metrics.

        Tries SQL RPC first (get_performance_summary) for speed, falls back
        to the Python aggregation path if the function doesn't exist yet.
        """
        filters = {
            "sport": sport,
            "market": market,
            "confidence_tier": confidence_tier,
            "signal": signal,
            "since": since,
            "from_date": from_date,
            "to_date": to_date,
        }

        return self._get_performance_python(sport, days, market, confidence_tier, signal, since, filters,
                                            from_date=from_date, to_date=to_date)

    def _get_performance_python(
        self,
        sport: Optional[str],
        days: int,
        market: Optional[str],
        confidence_tier: Optional[int],
        signal: Optional[str],
        since: Optional[str],
        filters: dict,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> dict:
        """Aggregate pick-based performance from prediction_grades.

        Uses prediction_grades (pick correctness: did OMI-favored side cover?)
        NOT prediction_accuracy_log (accuracy: was OMI line closer to result?).
        Deduplicates per game×market: prefer fanduel, fallback to draftkings.
        ROI uses actual book_odds for proper payout calculation.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        # Build valid_game_ids from game_results when date filters are active
        valid_game_ids: Optional[set] = None
        if since or from_date or to_date:
            gr_query = self.client.table("game_results").select("game_id").limit(5000)
            if since:
                gr_query = gr_query.gte("commence_time", since)
            if from_date:
                gr_query = gr_query.gte("commence_time", f"{from_date}T00:00:00+00:00")
            if to_date:
                gr_query = gr_query.lte("commence_time", f"{to_date}T23:59:59+00:00")
            gr_result = gr_query.execute()
            valid_game_ids = {r["game_id"] for r in (gr_result.data or [])}
            logger.info(f"[Performance] valid_game_ids (since={since}, from={from_date}, to={to_date}): {len(valid_game_ids)}")

        # Read from prediction_grades — pick correctness source of truth
        query = self.client.table("prediction_grades").select(
            "game_id, sport_key, signal, is_correct, "
            "pillar_composite, market_type, book_name, book_odds, "
            "confidence_tier, created_at"
        ).not_.is_("graded_at", "null").gte(
            "created_at", cutoff
        ).in_(
            "book_name", list(GRADING_BOOKS)
        ).order("created_at", desc=True).limit(5000)

        if sport:
            query = query.eq("sport_key", sport)
        if market:
            query = query.eq("market_type", market)
        if signal:
            query = query.eq("signal", signal)

        result = query.execute()
        raw_rows = result.data or []
        logger.info(f"[Performance] prediction_grades raw: {len(raw_rows)} rows")

        if valid_game_ids is not None:
            raw_rows = [r for r in raw_rows if r.get("game_id") in valid_game_ids]

        # Deduplicate per game×market: prefer fanduel, fallback to draftkings.
        # This prevents double-counting when both FD and DK are graded.
        dedup: dict = {}  # key: (game_id, market_type)
        for r in raw_rows:
            key = (r.get("game_id"), r.get("market_type"))
            existing = dedup.get(key)
            if existing is None:
                dedup[key] = r
            elif r.get("book_name") == "fanduel" and existing.get("book_name") != "fanduel":
                dedup[key] = r
            # else keep existing (already fanduel, or first-seen draftkings)

        rows = list(dedup.values())
        logger.info(f"[Performance] after dedup: {len(rows)} rows (from {len(raw_rows)} raw)")

        # Normalize sport keys for aggregation
        for r in rows:
            r["sport_key"] = _normalize_sport(r.get("sport_key", ""))

        return {
            "total_predictions": len(rows),
            "days": days,
            "filters": filters,
            "by_confidence_tier": self._aggregate_by_field(rows, "confidence_tier"),
            "by_market": self._aggregate_by_field(rows, "market_type"),
            "by_sport": self._aggregate_by_field(rows, "sport_key"),
            "by_signal": self._aggregate_by_field(rows, "signal"),
            "by_pillar": self._pillar_performance(rows),
            "calibration": self._calibration_by_signal(rows),
        }

    def _aggregate_by_field(self, rows: list, field: str) -> dict:
        """Aggregate hit rate and ROI by a grouping field.

        ROI uses actual book_odds when available:
          Win at -110 → profit = 100/110 = +$0.909 per $1 risked
          Win at +150 → profit = 150/100 = +$1.50 per $1 risked
          Loss → -$1.00 per $1 risked
          Push → $0
        Falls back to flat -110 assumption (0.909 payout) when book_odds missing.
        """
        groups: dict = {}
        for row in rows:
            key = row.get(field)
            if key is None:
                continue
            key = str(key)
            if key not in groups:
                groups[key] = {"total": 0, "correct": 0, "wrong": 0, "push": 0, "profit": 0.0}

            groups[key]["total"] += 1
            if row.get("is_correct") is True:
                groups[key]["correct"] += 1
                # Calculate actual payout from book_odds
                odds = row.get("book_odds")
                if odds is not None and odds != 0:
                    odds = int(odds)
                    if odds < 0:
                        payout = 100 / abs(odds)  # e.g. -110 → 0.909
                    else:
                        payout = odds / 100  # e.g. +150 → 1.50
                else:
                    payout = 100 / 110  # default -110
                groups[key]["profit"] += payout
            elif row.get("is_correct") is False:
                groups[key]["wrong"] += 1
                groups[key]["profit"] -= 1.0
            else:
                groups[key]["push"] += 1

        result = {}
        for key, data in groups.items():
            decided = data["correct"] + data["wrong"]
            hit_rate = data["correct"] / decided if decided > 0 else 0
            roi = data["profit"] / data["total"] if data["total"] > 0 else 0
            result[key] = {
                "total": data["total"],
                "correct": data["correct"],
                "wrong": data["wrong"],
                "push": data["push"],
                "hit_rate": round(hit_rate, 4),
                "roi": round(roi, 4),
            }

        return result

    def _pillar_performance(self, rows: list) -> dict:
        """Compare average pillar composite for correct vs wrong predictions."""
        correct_composites = []
        wrong_composites = []

        for row in rows:
            comp = row.get("pillar_composite")
            if comp is None:
                continue
            if row.get("is_correct") is True:
                correct_composites.append(comp)
            elif row.get("is_correct") is False:
                wrong_composites.append(comp)

        avg_correct = sum(correct_composites) / len(correct_composites) if correct_composites else 0
        avg_wrong = sum(wrong_composites) / len(wrong_composites) if wrong_composites else 0

        return {
            "composite": {
                "avg_correct": round(avg_correct * 100, 1),
                "avg_wrong": round(avg_wrong * 100, 1),
                "correct_count": len(correct_composites),
                "wrong_count": len(wrong_composites),
            }
        }

    def _calibration_by_signal(self, rows: list) -> list:
        """Calculate calibration: edge signal tier vs actual hit rate.
        Higher edge tiers should produce higher hit rates if calibrated.
        """
        # Map each tier to its expected confidence midpoint
        tier_order = [
            ("NO EDGE", 52),    # 50-54% midpoint
            ("LOW EDGE", 57),   # 55-59% midpoint
            ("MID EDGE", 63),   # 60-65% midpoint
            ("HIGH EDGE", 68),  # 66-70% midpoint
            ("MAX EDGE", 73),   # 71-75% midpoint
        ]
        calibration = []

        for tier_name, predicted in tier_order:
            tier_rows = [r for r in rows if r.get("signal") == tier_name]
            decided = [r for r in tier_rows if r.get("is_correct") is not None]
            correct = sum(1 for r in decided if r.get("is_correct") is True)
            actual_rate = correct / len(decided) * 100 if decided else 0

            calibration.append({
                "predicted": predicted,
                "actual": round(actual_rate, 1),
                "sample_size": len(decided),
                "tier": tier_name,
            })

        return calibration

    # ------------------------------------------------------------------
    # Regrade — purge + regenerate all prediction_grades
    # ------------------------------------------------------------------

    def regrade_all(self, progress: Optional[dict] = None) -> dict:
        """Delete all prediction_grades and regenerate from graded game_results.

        If progress dict is provided, updates it in-place for status polling:
          phase, deleted, total_games, games_processed, grades_created, errors
        """
        def _update(key, val):
            if progress is not None:
                progress[key] = val

        _update("phase", "purging")
        deleted = 0
        while True:
            batch = self.client.table("prediction_grades").select("id").limit(500).execute()
            ids = [r["id"] for r in (batch.data or [])]
            if not ids:
                break
            self.client.table("prediction_grades").delete().in_("id", ids).execute()
            deleted += len(ids)
            _update("deleted", deleted)

        _update("phase", "regenerating")
        graded = self.client.table("game_results").select("game_id").not_.is_(
            "home_score", "null"
        ).limit(5000).execute()
        game_ids = [r["game_id"] for r in (graded.data or [])]
        logger.info(f"[Regrade] Found {len(game_ids)} graded game_results to regenerate")
        _update("total_games", len(game_ids))

        created = 0
        errors = 0
        zero_count = 0
        for i, gid in enumerate(game_ids):
            try:
                count = self._generate_prediction_grades(gid)
                created += count
                if count == 0:
                    zero_count += 1
            except Exception as e:
                logger.error(f"[Regrade] Error for {gid}: {e}")
                errors += 1
            _update("games_processed", i + 1)
            _update("grades_created", created)
            _update("errors", errors)

        # Diagnostic probe: sample first few games to explain why 0 grades
        sample_diagnostics = []
        if created == 0 and game_ids:
            for gid in game_ids[:3]:
                try:
                    gr = self.client.table("game_results").select(
                        "game_id, sport_key, home_team, away_team, home_score, away_score, "
                        "composite_score, closing_spread_home, closing_total_line, "
                        "closing_ml_home, closing_ml_away"
                    ).eq("game_id", gid).single().execute()
                    g = gr.data or {}
                    raw_comp = g.get("composite_score")
                    comp = raw_comp if raw_comp is not None and raw_comp > 0 else 0.5
                    tier = composite_to_confidence_tier(comp)
                    bl = self._get_book_lines(gid)
                    sample_diagnostics.append({
                        "game_id": gid,
                        "sport": g.get("sport_key"),
                        "matchup": f"{g.get('away_team')} @ {g.get('home_team')}",
                        "scores": f"{g.get('home_score')}-{g.get('away_score')}",
                        "composite_raw": raw_comp,
                        "composite_used": comp,
                        "tier": tier,
                        "closing_spread": g.get("closing_spread_home"),
                        "closing_total": g.get("closing_total_line"),
                        "closing_ml": f"{g.get('closing_ml_home')}/{g.get('closing_ml_away')}",
                        "book_lines_keys": list(bl.keys()) if bl else [],
                        "grading_books_found": [b for b in bl if b in GRADING_BOOKS] if bl else [],
                    })
                except Exception as e:
                    sample_diagnostics.append({"game_id": gid, "error": str(e)})

        _update("phase", "done")
        logger.info(
            f"[Regrade] Purged {deleted}, regenerated {created} from {len(game_ids)} games "
            f"({zero_count} produced 0 grades, {errors} errors)"
        )
        return {
            "purged": deleted,
            "games": len(game_ids),
            "created": created,
            "zero_grade_games": zero_count,
            "errors": errors,
            "sample_diagnostics": sample_diagnostics,
        }

    # ------------------------------------------------------------------
    # Graded Games — one row per game × market, per-book implied prob edges
    # ------------------------------------------------------------------

    @staticmethod
    def _omi_fair_display(fair_value: float, mtype: str, home: str, away: str, book_line: float = None) -> str:
        """Build OMI fair display string.

        Spreads always shown from home team perspective: 'HOU -8.0'
        Totals shown as O/U relative to book total: 'O 242.5'
        """
        if fair_value is None:
            return "—"

        ref_half = round(fair_value * 2) / 2

        if mtype == "total":
            # Direction based on OMI fair vs book total
            if book_line is not None:
                bl = float(book_line)
                if fair_value > bl:
                    direction = "O"
                elif fair_value < bl:
                    direction = "U"
                else:
                    direction = "PK"
            else:
                # Fallback: compare to nearest half-point
                if abs(fair_value - ref_half) < 0.01:
                    direction = "PK"
                else:
                    direction = "O" if fair_value > ref_half else "U"
            if direction == "PK":
                return f"PK {ref_half:.1f}"
            return f"{direction} {ref_half:.1f}"
        elif mtype == "spread":
            # Always home team perspective — fair_value IS home spread
            sign = "+" if fair_value > 0 else ""
            return f"{home} {sign}{fair_value:.1f}"
        elif mtype == "moneyline":
            fp_ml = implied_to_american(fair_value / 100) if fair_value > 0 else 0
            if fp_ml < -ODDS_CAP:
                fp_ml = -ODDS_CAP
            elif fp_ml > ODDS_CAP:
                fp_ml = ODDS_CAP
            return f"{fair_value:.1f}% ({fp_ml:+d})" if fp_ml != 0 else f"{fair_value:.1f}%"

        return f"{fair_value:.1f}"

    def _book_detail_implied(self, brow, fair, mtype, home, away, sport_key=""):
        """Extract per-book edge detail using logistic probability model."""
        if brow is None or fair is None:
            return None
        bl = brow.get("book_line")
        if bl is None:
            return None

        raw_odds = brow.get("book_odds") or -110
        book_odds = _clamp_juice(raw_odds, mtype)
        gap = float(fair) - float(bl)
        side = brow.get("prediction_side", "")

        if mtype == "moneyline":
            # ML: fair and book_line are already in implied probability %
            edge_pct = round(abs(gap), 1)
            fi_pct = float(fair)
            fp = implied_to_american(fi_pct / 100)
            # Cap odds
            if fp < -ODDS_CAP:
                fp = -ODDS_CAP
            elif fp > ODDS_CAP:
                fp = ODDS_CAP

            call_team = home if side == "home" else away
            call = f"{call_team} ML ({fp:+d})" if fp != 0 else f"{call_team} ML"
            book_offer = f"{call_team} ML {book_odds:+d}"
        else:
            # Spread / Total: logistic probability model
            edge_pct = calc_edge_pct(float(fair), float(bl), mtype, sport_key)
            fp = calc_fair_price(float(fair), float(bl), mtype, sport_key)

            if mtype == "total":
                direction = "O" if gap > 0 else "U"
                call = f"{direction} {float(bl):.1f} ({fp:+d})" if fp != 0 else f"{direction} {float(bl):.1f}"
                book_offer = f"{direction} {float(bl):.1f} {book_odds:+d}"
            elif mtype == "spread":
                if gap > 0:
                    away_line = -float(bl)
                    sign = "+" if away_line > 0 else ""
                    call = f"{away} {sign}{away_line:.1f} ({fp:+d})" if fp != 0 else f"{away} {sign}{away_line:.1f}"
                    book_offer = f"{away} {sign}{away_line:.1f} {book_odds:+d}"
                else:
                    sign = "+" if float(bl) > 0 else ""
                    call = f"{home} {sign}{float(bl):.1f} ({fp:+d})" if fp != 0 else f"{home} {sign}{float(bl):.1f}"
                    book_offer = f"{home} {sign}{float(bl):.1f} {book_odds:+d}"
            else:
                call = ""
                book_offer = ""

        signal = determine_signal(edge_pct)

        return {
            "line": float(bl),
            "odds": int(book_odds),
            "fair_price": fp,
            "edge": edge_pct,
            "signal": signal,
            "call": call,
            "book_offer": book_offer,
            "side": side,
            "correct": brow.get("is_correct"),
        }

    def get_graded_games(
        self,
        sport: Optional[str] = None,
        market: Optional[str] = None,
        verdict: Optional[str] = None,
        since: Optional[str] = None,
        days: int = 30,
        limit: int = 500,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> dict:
        """Return graded predictions: one row per game×market, per-book implied prob edges."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        valid_game_ids: Optional[set] = None
        if since or from_date or to_date:
            gr_query = self.client.table("game_results").select("game_id").limit(5000)
            if since:
                gr_query = gr_query.gte("commence_time", since)
            if from_date:
                gr_query = gr_query.gte("commence_time", f"{from_date}T00:00:00+00:00")
            if to_date:
                gr_query = gr_query.lte("commence_time", f"{to_date}T23:59:59+00:00")
            gr_result = gr_query.execute()
            valid_game_ids = {r["game_id"] for r in (gr_result.data or [])}
            logger.info(f"[GradedGames] valid_game_ids (since={since}, from={from_date}, to={to_date}): {len(valid_game_ids)}")

        query = self.client.table("prediction_grades").select("*").not_.is_(
            "graded_at", "null"
        ).gte("created_at", cutoff).in_(
            "book_name", list(GRADING_BOOKS)
        ).order("graded_at", desc=True).limit(limit)

        if sport:
            query = query.eq("sport_key", sport)
        if market:
            query = query.eq("market_type", market)

        result = query.execute()
        rows = result.data or []
        logger.info(
            f"[GradedGames] Raw query returned {len(rows)} prediction_grades rows "
            f"(cutoff={cutoff[:10]}, limit={limit}, books={list(GRADING_BOOKS)})"
        )

        if valid_game_ids is not None:
            rows = [r for r in rows if r.get("game_id") in valid_game_ids]

        # Fetch game context
        game_ids = list({r["game_id"] for r in rows})
        game_map: dict = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i : i + 50]
            gr = self.client.table("game_results").select(
                "game_id, home_team, away_team, commence_time, home_score, away_score"
            ).in_("game_id", batch).execute()
            for g in (gr.data or []):
                game_map[g["game_id"]] = g

        # Get pillar scores for all games
        try:
            pillar_data = self._get_pillar_data(game_ids)
        except Exception as e:
            logger.warning(f"[GradedGames] Failed to get pillar data: {e}")
            pillar_data = {}

        # Group by (game_id, market_type)
        groups: dict = {}
        for row in rows:
            key = (row["game_id"], row.get("market_type", ""))
            if key not in groups:
                groups[key] = {"rows_by_book": {}, "first": row}
            book = row.get("book_name", "")
            if book not in groups[key]["rows_by_book"]:
                groups[key]["rows_by_book"][book] = row

        # Build merged rows
        merged = []
        for (gid, mtype), grp in groups.items():
            game = game_map.get(gid, {})
            first = grp["first"]
            fd_row = grp["rows_by_book"].get("fanduel")
            dk_row = grp["rows_by_book"].get("draftkings")

            fair = first.get("omi_fair_line")
            book_line = first.get("book_line")
            home = game.get("home_team", "?")
            away = game.get("away_team", "?")

            gk = game.get("sport_key", "")
            fd = self._book_detail_implied(fd_row, fair, mtype, home, away, gk)
            dk = self._book_detail_implied(dk_row, fair, mtype, home, away, gk)

            # Stale data detection — flag books with impossible line divergence
            if fd and dk:
                fd_line = fd["line"]
                dk_line = dk["line"]
                line_diff = abs(fd_line - dk_line)
                if mtype == "spread" and line_diff > 5:
                    # Flag the book that's further from OMI fair as stale
                    if fair is not None:
                        fd_dist = abs(float(fair) - fd_line)
                        dk_dist = abs(float(fair) - dk_line)
                        if fd_dist > dk_dist:
                            fd["signal"] = "STALE"
                            fd["edge"] = 0
                        else:
                            dk["signal"] = "STALE"
                            dk["edge"] = 0
                elif mtype == "total" and line_diff > 8:
                    if fair is not None:
                        fd_dist = abs(float(fair) - fd_line)
                        dk_dist = abs(float(fair) - dk_line)
                        if fd_dist > dk_dist:
                            fd["signal"] = "STALE"
                            fd["edge"] = 0
                        else:
                            dk["signal"] = "STALE"
                            dk["edge"] = 0
                elif mtype == "moneyline" and line_diff > 30:
                    if fair is not None:
                        fd_dist = abs(float(fair) - fd_line)
                        dk_dist = abs(float(fair) - dk_line)
                        if fd_dist > dk_dist:
                            fd["signal"] = "STALE"
                            fd["edge"] = 0
                        else:
                            dk["signal"] = "STALE"
                            dk["edge"] = 0

            # Best edge (skip STALE books)
            best_edge = None
            best_book = None
            fd_valid = fd and fd.get("signal") != "STALE"
            dk_valid = dk and dk.get("signal") != "STALE"
            if fd_valid and dk_valid:
                if fd["edge"] >= dk["edge"]:
                    best_edge, best_book = fd["edge"], "FD"
                else:
                    best_edge, best_book = dk["edge"], "DK"
            elif fd_valid:
                best_edge, best_book = fd["edge"], "FD"
            elif dk_valid:
                best_edge, best_book = dk["edge"], "DK"

            # Overall verdict from best-book row
            best_row = (fd_row if best_book == "FD" else dk_row) or first
            is_correct = best_row.get("is_correct")

            sport_normalized = _normalize_sport(first.get("sport_key", ""))

            # Confidence from edge (interpolated, not bucketed)
            conf = edge_to_confidence(best_edge) if best_edge is not None else 50.0

            # Signal tier from best edge
            row_signal = determine_signal(best_edge) if best_edge is not None else "NO EDGE"

            # Actual margin (home - away) for ATS grading display
            h_score = game.get("home_score")
            a_score = game.get("away_score")
            actual_margin = (h_score - a_score) if h_score is not None and a_score is not None else None

            row_out = {
                "game_id": gid,
                "sport_key": sport_normalized,
                "home_team": home,
                "away_team": away,
                "commence_time": game.get("commence_time", ""),
                "home_score": game.get("home_score"),
                "away_score": game.get("away_score"),
                "market_type": mtype,
                "omi_fair_line": fair,
                "omi_fair_display": self._omi_fair_display(fair, mtype, home, away, book_line=book_line),
                "confidence_tier": conf,
                "pillar_composite": first.get("pillar_composite"),
                "best_edge": best_edge,
                "best_book": best_book,
                "is_correct": is_correct,
                "signal": row_signal,
                "actual_margin": actual_margin,
                "pillar_scores": (pillar_data.get(gid) or {}).get("scores"),
                "composite": (pillar_data.get(gid) or {}).get("composite"),
                "fd": fd,
                "dk": dk,
            }
            merged.append(row_out)

        # Apply verdict filter
        if verdict == "win":
            merged = [r for r in merged if r["is_correct"] is True]
        elif verdict == "loss":
            merged = [r for r in merged if r["is_correct"] is False]
        elif verdict == "push":
            merged = [r for r in merged if r["is_correct"] is None]

        # Sort: date desc, then abs(best_edge) desc
        merged.sort(
            key=lambda r: (
                r.get("commence_time") or "",
                abs(r.get("best_edge") or 0),
            ),
            reverse=True,
        )

        # Summary stats
        wins = sum(1 for r in merged if r["is_correct"] is True)
        losses = sum(1 for r in merged if r["is_correct"] is False)
        pushes = sum(1 for r in merged if r["is_correct"] is None)
        decided = wins + losses
        hit_rate = wins / decided if decided > 0 else 0
        roi = (wins * 0.91 - losses) / len(merged) if merged else 0

        # Diagnostic: count total prediction_grades in DB for visibility
        try:
            total_count_result = self.client.table("prediction_grades").select(
                "id", count="exact"
            ).execute()
            db_total = total_count_result.count if hasattr(total_count_result, 'count') and total_count_result.count is not None else len(total_count_result.data or [])
        except Exception:
            db_total = -1

        return {
            "rows": merged,
            "summary": {
                "total_graded": len(merged),
                "wins": wins,
                "losses": losses,
                "pushes": pushes,
                "hit_rate": round(hit_rate, 4),
                "roi": round(roi, 4),
                "best_sport": self._best_group(merged, "sport_key"),
                "best_market": self._best_group(merged, "market_type"),
            },
            "count": len(merged),
            "diagnostics": {
                "db_total_prediction_grades": db_total,
                "raw_query_rows": len(result.data or []),
                "valid_game_ids_count": len(valid_game_ids) if valid_game_ids is not None else "no_filter",
                "unique_game_ids_in_rows": len({r["game_id"] for r in (result.data or [])}),
            },
        }

    # ------------------------------------------------------------------
    # Live Markets — upcoming games with current OMI edges
    # ------------------------------------------------------------------

    def get_live_markets(self, sport: Optional[str] = None) -> dict:
        """Return upcoming games with current OMI fair lines and book edges."""
        import traceback
        now = datetime.now(timezone.utc).isoformat()

        try:
            # 1. Get upcoming games from cached_odds
            query = self.client.table("cached_odds").select(
                "sport_key, game_id, game_data"
            ).gte("game_data->>commence_time", now)
            if sport:
                # cached_odds uses full sport_key (e.g. basketball_nba)
                # Accept either short or long form
                variants = [k for k, v in SPORT_DISPLAY.items() if v == sport.upper()]
                if variants:
                    query = query.in_("sport_key", variants)
                else:
                    query = query.eq("sport_key", sport)
            result = query.execute()
            games = result.data or []
        except Exception as e:
            logger.error(f"[LiveMarkets] Failed to query cached_odds: {e}\n{traceback.format_exc()}")
            return {"rows": [], "count": 0, "error": f"cached_odds query failed: {e}"}

        if not games:
            return {"rows": [], "count": 0}

        try:
            # 2. Get latest composite_history snapshot per game
            game_ids = list({g["game_id"] for g in games})
            ch_map: dict = {}
            for i in range(0, len(game_ids), 50):
                batch = game_ids[i:i+50]
                ch = self.client.table("composite_history").select(
                    "*"
                ).in_("game_id", batch).order("timestamp", desc=True).execute()
                for row in (ch.data or []):
                    gid = row["game_id"]
                    if gid not in ch_map:
                        ch_map[gid] = row
        except Exception as e:
            logger.error(f"[LiveMarkets] Failed to query composite_history: {e}\n{traceback.format_exc()}")
            ch_map = {}

        # 2b. Get pillar data (scores + driver) from predictions table
        try:
            pillar_data = self._get_pillar_data(game_ids)
        except Exception as e:
            logger.warning(f"[LiveMarkets] Failed to get pillar data: {e}")
            pillar_data = {}

        # 3. Build rows — one per game × market
        rows = []
        game_errors = 0
        for g in games:
          try:
            gid = g["game_id"]
            gdata = g.get("game_data") or {}
            sport_raw = g.get("sport_key", "")
            sport_short = _normalize_sport(sport_raw)
            home = gdata.get("home_team", "?")
            away = gdata.get("away_team", "?")
            commence = gdata.get("commence_time", "")

            ch = ch_map.get(gid)

            # Extract current book lines from cached_odds game_data
            bookmakers = gdata.get("bookmakers") or []
            fd_lines: dict = {}
            dk_lines: dict = {}
            for bm in bookmakers:
                bkey = (bm.get("key") or "").lower()
                if bkey not in ("fanduel", "draftkings"):
                    continue
                target = fd_lines if bkey == "fanduel" else dk_lines
                for mkt in (bm.get("markets") or []):
                    mkey = mkt.get("key", "")
                    outcomes = mkt.get("outcomes") or []
                    if mkey == "spreads":
                        for o in outcomes:
                            if o.get("name") == home:
                                target["spread_line"] = o.get("point", 0)
                                target["spread_odds"] = o.get("price", -110)
                    elif mkey == "totals":
                        for o in outcomes:
                            if o.get("name") == "Over":
                                target["total_line"] = o.get("point", 0)
                                target["total_odds"] = o.get("price", -110)
                    elif mkey == "h2h":
                        for o in outcomes:
                            if o.get("name") == home:
                                target["ml_home"] = o.get("price", 0)
                            elif o.get("name") == away:
                                target["ml_away"] = o.get("price", 0)
                            elif o.get("name") == "Draw":
                                target["ml_draw"] = o.get("price", 0)

            fair_spread = ch.get("fair_spread") if ch else None
            fair_total = ch.get("fair_total") if ch else None
            fair_ml_home = ch.get("fair_ml_home") if ch else None
            fair_ml_away = ch.get("fair_ml_away") if ch else None
            fair_ml_draw = ch.get("fair_ml_draw") if ch else None

            has_composite = ch is not None

            is_soccer_game = _is_soccer(sport_short)

            # If no composite data, emit placeholder rows for any book lines we have
            if not has_composite:
                # Spread placeholder (non-soccer only)
                if not is_soccer_game:
                    fd_bl = fd_lines.get("spread_line")
                    dk_bl = dk_lines.get("spread_line")
                    if fd_bl is not None or dk_bl is not None:
                        rows.append({
                            "game_id": gid, "sport_key": sport_short,
                            "home_team": home, "away_team": away,
                            "commence_time": commence, "market_type": "spread",
                            "omi_fair": "Awaiting OMI Fair", "omi_fair_line": None,
                            "fd_line": fd_bl, "fd_odds": fd_lines.get("spread_odds"),
                            "fd_edge": None, "fd_signal": None,
                            "fd_call": None,
                            "dk_line": dk_bl, "dk_odds": dk_lines.get("spread_odds"),
                            "dk_edge": None, "dk_signal": None,
                            "dk_call": None,
                            "best_edge": None, "signal": "PENDING",
                            "pillar_driver": (pillar_data.get(gid) or {}).get("driver", "—"),
                            "pillar_scores": (pillar_data.get(gid) or {}).get("scores"),
                            "composite": (pillar_data.get(gid) or {}).get("composite"),
                        })
                # Total placeholder (always)
                fd_bl = fd_lines.get("total_line")
                dk_bl = dk_lines.get("total_line")
                if fd_bl is not None or dk_bl is not None:
                    rows.append({
                        "game_id": gid, "sport_key": sport_short,
                        "home_team": home, "away_team": away,
                        "commence_time": commence, "market_type": "total",
                        "omi_fair": "Awaiting OMI Fair", "omi_fair_line": None,
                        "fd_line": fd_bl, "fd_odds": fd_lines.get("total_odds"),
                        "fd_edge": None, "fd_signal": None,
                        "fd_call": None,
                        "dk_line": dk_bl, "dk_odds": dk_lines.get("total_odds"),
                        "dk_edge": None, "dk_signal": None,
                        "dk_call": None,
                        "best_edge": None, "signal": "PENDING",
                        "pillar_driver": (pillar_data.get(gid) or {}).get("driver", "—"),
                        "pillar_scores": (pillar_data.get(gid) or {}).get("scores"),
                        "composite": (pillar_data.get(gid) or {}).get("composite"),
                    })
                # Moneyline placeholder (soccer only)
                if is_soccer_game:
                    fd_mlh = fd_lines.get("ml_home")
                    dk_mlh = dk_lines.get("ml_home")
                    if fd_mlh is not None or dk_mlh is not None:
                        rows.append({
                            "game_id": gid, "sport_key": sport_short,
                            "home_team": home, "away_team": away,
                            "commence_time": commence, "market_type": "moneyline",
                            "omi_fair": "Awaiting OMI Fair", "omi_fair_line": None,
                            "fd_line": fd_mlh, "fd_odds": fd_mlh,
                            "fd_edge": None, "fd_signal": None,
                            "fd_call": None,
                            "dk_line": dk_mlh, "dk_odds": dk_mlh,
                            "dk_edge": None, "dk_signal": None,
                            "dk_call": None,
                            "best_edge": None, "signal": "PENDING",
                            "pillar_driver": (pillar_data.get(gid) or {}).get("driver", "—"),
                            "pillar_scores": (pillar_data.get(gid) or {}).get("scores"),
                            "composite": (pillar_data.get(gid) or {}).get("composite"),
                        })
                continue

            # Spread rows (non-soccer only)
            if fair_spread is not None and not is_soccer_game:
                fair_s = float(fair_spread)
                for book_key, book_label, blines in [
                    ("fd", "FD", fd_lines), ("dk", "DK", dk_lines)
                ]:
                    bl = blines.get("spread_line")
                    if bl is not None:
                        edge = calc_edge_pct(fair_s, float(bl), "spread", sport_key)
                        signal = determine_signal(edge)
                    else:
                        edge = None
                        signal = None

                sign = "+" if fair_s > 0 else ""
                fair_display = f"{home} {sign}{fair_s:.1f}"

                fd_bl = fd_lines.get("spread_line")
                dk_bl = dk_lines.get("spread_line")

                # Stale check between books (soft-cap edges before signal tier)
                fd_edge = _cap_edge_display(calc_edge_pct(fair_s, float(fd_bl), "spread", sport_key)) if fd_bl is not None else None
                dk_edge = _cap_edge_display(calc_edge_pct(fair_s, float(dk_bl), "spread", sport_key)) if dk_bl is not None else None
                fd_signal = determine_signal(fd_edge) if fd_edge is not None else None
                dk_signal = determine_signal(dk_edge) if dk_edge is not None else None

                if fd_bl is not None and dk_bl is not None and abs(float(fd_bl) - float(dk_bl)) > 5:
                    fd_dist = abs(fair_s - float(fd_bl))
                    dk_dist = abs(fair_s - float(dk_bl))
                    if fd_dist > dk_dist:
                        fd_signal = "STALE"
                        fd_edge = 0
                    else:
                        dk_signal = "STALE"
                        dk_edge = 0

                best_e = max(
                    fd_edge if fd_signal and fd_signal != "STALE" else 0,
                    dk_edge if dk_signal and dk_signal != "STALE" else 0,
                ) if (fd_edge is not None or dk_edge is not None) else None
                best_sig = determine_signal(best_e) if best_e else "NO EDGE"

                # Spread call: which side has value at each book
                def _spread_call(bl, fair, h, a):
                    if bl is None:
                        return None
                    b = float(bl)
                    if fair > b:  # away side has value
                        away_line = -b
                        return f"{a} {away_line:+.1f}"
                    else:  # home side has value (or exact match)
                        return f"{h} {b:+.1f}"

                fd_call = _spread_call(fd_bl, fair_s, home, away)
                dk_call = _spread_call(dk_bl, fair_s, home, away)

                rows.append({
                    "game_id": gid, "sport_key": sport_short,
                    "home_team": home, "away_team": away,
                    "commence_time": commence, "market_type": "spread",
                    "omi_fair": fair_display, "omi_fair_line": fair_s,
                    "fd_line": fd_bl, "fd_odds": fd_lines.get("spread_odds"),
                    "fd_edge": fd_edge, "fd_signal": fd_signal,
                    "fd_call": fd_call,
                    "dk_line": dk_bl, "dk_odds": dk_lines.get("spread_odds"),
                    "dk_edge": dk_edge, "dk_signal": dk_signal,
                    "dk_call": dk_call,
                    "best_edge": best_e, "signal": best_sig,
                    "pillar_driver": (pillar_data.get(gid) or {}).get("driver", "—"),
                    "pillar_scores": (pillar_data.get(gid) or {}).get("scores"),
                    "composite": (pillar_data.get(gid) or {}).get("composite"),
                })

            # Total rows
            if fair_total is not None:
                fair_t = float(fair_total)
                book_t = float(ch.get("book_total")) if ch and ch.get("book_total") is not None else None
                ref_half = round(fair_t * 2) / 2
                if book_t is not None:
                    direction = "O" if fair_t > book_t else "U" if fair_t < book_t else "PK"
                else:
                    direction = "O" if fair_t > ref_half else "U" if fair_t < ref_half else "PK"
                fair_display = f"{direction} {ref_half:.1f}" if direction != "PK" else f"PK {ref_half:.1f}"

                fd_bl = fd_lines.get("total_line")
                dk_bl = dk_lines.get("total_line")

                fd_edge = _cap_edge_display(calc_edge_pct(fair_t, float(fd_bl), "total", sport_key)) if fd_bl is not None else None
                dk_edge = _cap_edge_display(calc_edge_pct(fair_t, float(dk_bl), "total", sport_key)) if dk_bl is not None else None
                fd_signal = determine_signal(fd_edge) if fd_edge is not None else None
                dk_signal = determine_signal(dk_edge) if dk_edge is not None else None

                if fd_bl is not None and dk_bl is not None and abs(float(fd_bl) - float(dk_bl)) > 8:
                    fd_dist = abs(fair_t - float(fd_bl))
                    dk_dist = abs(fair_t - float(dk_bl))
                    if fd_dist > dk_dist:
                        fd_signal = "STALE"
                        fd_edge = 0
                    else:
                        dk_signal = "STALE"
                        dk_edge = 0

                best_e = max(
                    fd_edge if fd_signal and fd_signal != "STALE" else 0,
                    dk_edge if dk_signal and dk_signal != "STALE" else 0,
                ) if (fd_edge is not None or dk_edge is not None) else None
                best_sig = determine_signal(best_e) if best_e else "NO EDGE"

                # Total call: over or under at each book's line
                def _total_call(bl, fair):
                    if bl is None:
                        return None
                    b = float(bl)
                    d = "O" if fair > b else "U" if fair < b else "PK"
                    return f"{d} {b:.1f}"

                fd_call = _total_call(fd_bl, fair_t)
                dk_call = _total_call(dk_bl, fair_t)

                rows.append({
                    "game_id": gid, "sport_key": sport_short,
                    "home_team": home, "away_team": away,
                    "commence_time": commence, "market_type": "total",
                    "omi_fair": fair_display, "omi_fair_line": fair_t,
                    "fd_line": fd_bl, "fd_odds": fd_lines.get("total_odds"),
                    "fd_edge": fd_edge, "fd_signal": fd_signal,
                    "fd_call": fd_call,
                    "dk_line": dk_bl, "dk_odds": dk_lines.get("total_odds"),
                    "dk_edge": dk_edge, "dk_signal": dk_signal,
                    "dk_call": dk_call,
                    "best_edge": best_e, "signal": best_sig,
                    "pillar_driver": (pillar_data.get(gid) or {}).get("driver", "—"),
                    "pillar_scores": (pillar_data.get(gid) or {}).get("scores"),
                    "composite": (pillar_data.get(gid) or {}).get("composite"),
                })

            # Moneyline rows (soccer only — 3-way: home/draw/away)
            # Wrapped in try/except: draw columns may not exist in DB yet
            if fair_ml_home is not None and fair_ml_away is not None and is_soccer_game:
                try:
                    fh = float(fair_ml_home)
                    fa = float(fair_ml_away)
                    fair_hp = american_to_implied(fh)
                    fair_ap = american_to_implied(fa)

                    # 3-way: use fair_ml_draw if available, otherwise derive from book draw odds
                    if fair_ml_draw is not None:
                        fd_val = float(fair_ml_draw)
                        fair_dp = american_to_implied(fd_val)
                    else:
                        # Fallback: use median book draw odds with vig removal
                        draw_odds_list = []
                        for bm in (gdata.get("bookmakers") or []):
                            for mkt in (bm.get("markets") or []):
                                if mkt.get("key") == "h2h":
                                    for o in mkt.get("outcomes", []):
                                        if o.get("name") == "Draw" and o.get("price"):
                                            draw_odds_list.append(o["price"])
                        if draw_odds_list:
                            import statistics
                            median_draw = statistics.median(draw_odds_list)
                            raw_dp = american_to_implied(median_draw)
                            # Remove vig: normalize all 3 book implied probs
                            raw_total = fair_hp + fair_ap + raw_dp
                            fair_dp = raw_dp / raw_total if raw_total > 0 else 0.25
                        else:
                            fair_dp = 0.25  # ~25% EPL historical average

                    # Normalize to sum to 1.0
                    ft = fair_hp + fair_dp + fair_ap
                    if ft > 0:
                        fair_hp /= ft
                        fair_dp /= ft
                        fair_ap /= ft

                    fp_display = f"H {fair_hp*100:.0f}% / D {fair_dp*100:.0f}% / A {fair_ap*100:.0f}%"

                    fd_mlh = fd_lines.get("ml_home")
                    fd_mla = fd_lines.get("ml_away")
                    fd_mld = fd_lines.get("ml_draw")
                    dk_mlh = dk_lines.get("ml_home")
                    dk_mla = dk_lines.get("ml_away")
                    dk_mld = dk_lines.get("ml_draw")

                    fd_edge = None
                    dk_edge = None
                    fd_signal = None
                    dk_signal = None

                    def _calc_3way_edge(book_h, book_d, book_a, fair_h, fair_d, fair_a):
                        """Best positive edge across 3 outcomes, vig-removed. Returns (edge, best_idx).

                        Only returns the edge on the outcome OMI thinks is underpriced
                        (positive edge = book is offering worse odds than fair).
                        Previous max(abs(e)) inflated edges by picking the largest
                        absolute divergence, which double-counts because shifting one
                        outcome's probability automatically shifts the others.
                        """
                        bh = american_to_implied(book_h)
                        ba = american_to_implied(book_a)
                        bd = american_to_implied(book_d) if book_d else 0
                        bt = bh + bd + ba
                        if bt > 0:
                            bh /= bt
                            bd /= bt
                            ba /= bt
                        # Positive = OMI thinks more likely than book (undervalued)
                        edges = [
                            (fair_h - bh) * 100,            # home
                            (fair_d - bd) * 100 if bd > 0 else 0,  # draw
                            (fair_a - ba) * 100,            # away
                        ]
                        best_idx = max(range(3), key=lambda i: edges[i])
                        best_edge = max(0, edges[best_idx])
                        return round(best_edge, 1), best_idx

                    fd_call = None
                    dk_call = None

                    if fd_mlh and fd_mla:
                        fd_edge, fd_best = _calc_3way_edge(fd_mlh, fd_mld, fd_mla, fair_hp, fair_dp, fair_ap)
                        fd_signal = determine_signal(fd_edge, market_type="moneyline")
                        fd_call = [f"{home} ML", "Draw", f"{away} ML"][fd_best]

                    if dk_mlh and dk_mla:
                        dk_edge, dk_best = _calc_3way_edge(dk_mlh, dk_mld, dk_mla, fair_hp, fair_dp, fair_ap)
                        dk_signal = determine_signal(dk_edge, market_type="moneyline")
                        dk_call = [f"{home} ML", "Draw", f"{away} ML"][dk_best]

                    # ML stale check
                    if fd_edge is not None and dk_edge is not None and fd_mlh and dk_mlh:
                        fd_imp = american_to_implied(fd_mlh) * 100
                        dk_imp = american_to_implied(dk_mlh) * 100
                        if abs(fd_imp - dk_imp) > 30:
                            fair_imp = fair_hp * 100
                            if abs(fair_imp - fd_imp) > abs(fair_imp - dk_imp):
                                fd_signal = "STALE"
                                fd_edge = 0
                            else:
                                dk_signal = "STALE"
                                dk_edge = 0

                    best_e = max(
                        fd_edge if fd_signal and fd_signal != "STALE" else 0,
                        dk_edge if dk_signal and dk_signal != "STALE" else 0,
                    ) if (fd_edge is not None or dk_edge is not None) else None
                    best_sig = determine_signal(best_e, market_type="moneyline") if best_e else "NO EDGE"

                    rows.append({
                        "game_id": gid, "sport_key": sport_short,
                        "home_team": home, "away_team": away,
                        "commence_time": commence, "market_type": "moneyline",
                        "omi_fair": fp_display, "omi_fair_line": fair_hp * 100,
                        "fd_line": fd_mlh, "fd_odds": fd_mlh,
                        "fd_edge": fd_edge, "fd_signal": fd_signal,
                        "fd_call": fd_call,
                        "dk_line": dk_mlh, "dk_odds": dk_mlh,
                        "dk_edge": dk_edge, "dk_signal": dk_signal,
                        "dk_call": dk_call,
                        "best_edge": best_e, "signal": best_sig,
                        "pillar_driver": (pillar_data.get(gid) or {}).get("driver", "—"),
                        "pillar_scores": (pillar_data.get(gid) or {}).get("scores"),
                        "composite": (pillar_data.get(gid) or {}).get("composite"),
                    })
                except Exception as e:
                    logger.warning(f"[LiveMarkets] Soccer ML error for {gid}: {e}")

          except Exception as e:
            game_errors += 1
            logger.error(
                f"[LiveMarkets] Error processing game {g.get('game_id', '?')} "
                f"(sport={g.get('sport_key', '?')}): {e}\n{traceback.format_exc()}"
            )

        # Sort: sport, then commence_time
        rows.sort(key=lambda r: (r["sport_key"], r["commence_time"], r["game_id"], r["market_type"]))

        if game_errors > 0:
            logger.warning(f"[LiveMarkets] {game_errors} games had errors, {len(rows)} rows returned")

        return {"rows": rows, "count": len(rows)}

    # ------------------------------------------------------------------
    # Pillar driver — which pillar deviated most from neutral (0.5)
    # ------------------------------------------------------------------

    PILLAR_NAMES = {
        "pillar_execution": "Injuries",
        "pillar_incentives": "Motivation",
        "pillar_shocks": "Line Move",
        "pillar_time_decay": "Rest",
        "pillar_flow": "Sharp $",
        "pillar_game_environment": "Matchup",
    }

    # Short labels for pillar score display
    PILLAR_SHORT = {
        "pillar_execution": "EX",
        "pillar_incentives": "MO",
        "pillar_shocks": "LM",
        "pillar_time_decay": "RE",
        "pillar_flow": "SH",
        "pillar_game_environment": "MA",
    }

    def _get_pillar_data(self, game_ids: list) -> dict:
        """Get pillar scores, composite, and top driver per game from predictions table.

        Returns {game_id: {
            "driver": "Sharp $",
            "composite": 0.62,
            "scores": {"execution": 0.5, "incentives": 0.5, ...}
        }}
        """
        if not game_ids:
            return {}
        data: dict = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i:i+50]
            try:
                result = self.client.table("predictions").select(
                    "game_id, composite_score, "
                    "pillar_execution, pillar_incentives, pillar_shocks, "
                    "pillar_time_decay, pillar_flow, pillar_game_environment"
                ).in_("game_id", batch).execute()
                for row in (result.data or []):
                    gid = row["game_id"]
                    if gid in data:
                        continue
                    max_dev = 0.0
                    top = "—"
                    scores = {}
                    for col, label in self.PILLAR_NAMES.items():
                        val = row.get(col, 0.5) or 0.5
                        val = float(val)
                        # Store with short key name (strip "pillar_" prefix)
                        short_key = col.replace("pillar_", "")
                        scores[short_key] = round(val, 2)
                        dev = abs(val - 0.5)
                        if dev > max_dev:
                            max_dev = dev
                            top = label
                    comp = row.get("composite_score")
                    data[gid] = {
                        "driver": top,
                        "composite": round(float(comp), 2) if comp is not None else None,
                        "scores": scores,
                    }
            except Exception as e:
                logger.warning(f"[PillarData] Error fetching batch: {e}")
        return data

    def _best_group(self, rows: list, field: str, min_sample: int = 5) -> Optional[dict]:
        """Find the group with the highest hit rate (min sample size)."""
        groups: dict = {}
        for r in rows:
            key = r.get(field)
            if not key:
                continue
            if key not in groups:
                groups[key] = {"wins": 0, "losses": 0}
            if r.get("is_correct") is True:
                groups[key]["wins"] += 1
            elif r.get("is_correct") is False:
                groups[key]["losses"] += 1

        best = None
        best_rate = 0.0
        for key, g in groups.items():
            decided = g["wins"] + g["losses"]
            if decided < min_sample:
                continue
            rate = g["wins"] / decided
            if rate > best_rate:
                best_rate = rate
                best = {"key": key, "hit_rate": round(rate, 4), "count": decided}

        return best
