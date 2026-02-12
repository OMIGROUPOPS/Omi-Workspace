"""
OMI Edge - Internal Grader
Enhanced grading with prediction_grades table for per-market/period/book granularity.
Uses point-to-probability edge model: each point of OMI-vs-book disagreement ≈ 3% win
probability, minus book juice.
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
FAIR_LINE_TOTAL_FACTOR = 0.20
FAIR_LINE_ML_FACTOR = 0.01

# Industry standard: ~3% win probability per point of spread/total difference
PROB_PER_POINT = 0.03

# Cap displayed American odds to avoid absurd values
ODDS_CAP = 500  # max ±500

# Only grade against books where users actually place bets
GRADING_BOOKS = {"fanduel", "draftkings"}

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


def determine_signal(edge_pct: float) -> str:
    """Determine signal tier from implied probability edge %.
    All markets use the same thresholds since edge is already in universal % units.
    """
    ae = abs(edge_pct)
    if ae >= 6:
        return "MISPRICED"
    if ae >= 3:
        return "VALUE"
    if ae >= 1:
        return "FAIR"
    return "SHARP"


def composite_to_confidence_tier(composite: float) -> Optional[int]:
    """Map composite score (0-1) to confidence tier."""
    score = composite * 100
    if score >= 70:
        return 70
    elif score >= 65:
        return 65
    elif score >= 60:
        return 60
    elif score >= 55:
        return 55
    return None


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


def calc_edge_pct(fair_value: float, book_line: float, book_odds: int) -> float:
    """Calculate edge as implied probability percentage.

    Each point of OMI-vs-book disagreement ≈ 3% win probability.
    Subtract book juice (how much above 50% the book charges) so that
    a standard -110 line with minimal point difference reads as SHARP.
    """
    point_diff = abs(fair_value - book_line)
    edge = point_diff * PROB_PER_POINT * 100  # percentage

    # Subtract book juice
    if book_odds and book_odds != 0:
        book_implied = american_to_implied(book_odds)
        juice = (book_implied - 0.50) * 100  # typically ~2.4% for -110
        edge = max(0, edge - juice)

    return round(edge, 1)


def calc_fair_price(fair_value: float, book_line: float) -> int:
    """Convert OMI fair value at a book's line to capped American odds.

    Uses point difference → probability, then converts to American.
    Caps at ±ODDS_CAP to avoid absurd display values.
    """
    point_diff = abs(fair_value - book_line)
    fair_prob = 0.50 + point_diff * PROB_PER_POINT
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
        errors = []

        for detail in auto_result.get("details", []):
            game_id = detail.get("game_id")
            try:
                count = self._generate_prediction_grades(game_id)
                graded_count += count
            except Exception as e:
                logger.error(f"Error generating prediction grades for {game_id}: {e}")
                errors.append({"game_id": game_id, "error": str(e)})

        return {
            "auto_grader": auto_result,
            "prediction_grades_created": graded_count,
            "bootstrapped_game_results": bootstrapped,
            "errors": errors,
        }

    def _bootstrap_game_results(self, sport: Optional[str] = None) -> int:
        """Create game_results rows from predictions for completed games."""
        cutoff = datetime.now(timezone.utc).isoformat()
        count = 0

        try:
            query = self.client.table("predictions").select(
                "game_id, sport_key"
            ).lt("commence_time", cutoff)

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
                outcome = snap.get("outcome_type", "")

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
        result = self.client.table("game_results").select("*").eq(
            "game_id", game_id
        ).single().execute()

        if not result.data:
            return 0

        game = result.data
        home_score = game.get("home_score")
        away_score = game.get("away_score")

        if home_score is None or away_score is None:
            return 0

        sport_key = game.get("sport_key", "")
        composite = game.get("composite_score", 0.5) or 0.5
        tier = composite_to_confidence_tier(composite)

        if tier is None:
            return 0

        final_spread = home_score - away_score
        final_total = home_score + away_score

        # Get closing lines from game_results
        closing_spread = game.get("closing_spread_home")
        closing_total = game.get("closing_total_line")
        closing_ml_home = game.get("closing_ml_home")
        closing_ml_away = game.get("closing_ml_away")

        # Calculate OMI fair lines
        fair_spread = None
        if closing_spread is not None:
            adjustment = (composite - 0.5) * FAIR_LINE_SPREAD_FACTOR * 10
            fair_spread = closing_spread + adjustment

        fair_total = None
        game_env = game.get("pillar_game_environment") or composite
        if closing_total is not None:
            adjustment = (game_env - 0.5) * FAIR_LINE_TOTAL_FACTOR * 10
            fair_total = closing_total + adjustment

        book_lines = self._get_book_lines(game_id)

        rows_created = 0

        for book_name, book_data in book_lines.items():
            if book_name not in GRADING_BOOKS:
                continue

            # Spread
            spread_data = book_data.get("spread")
            if fair_spread is not None and spread_data and spread_data.get("line") is not None:
                book_spread = spread_data["line"]
                gap = fair_spread - book_spread

                if gap > 0:
                    prediction_side = "away"
                    book_odds = spread_data.get("away_odds") or -110
                    actual_result = "away_covered" if final_spread < closing_spread else (
                        "push" if final_spread == closing_spread else "home_covered"
                    )
                    is_correct = final_spread < book_spread
                else:
                    prediction_side = "home"
                    book_odds = spread_data.get("home_odds") or -110
                    actual_result = "home_covered" if final_spread > closing_spread else (
                        "push" if final_spread == closing_spread else "away_covered"
                    )
                    is_correct = final_spread > book_spread

                if final_spread == book_spread:
                    actual_result = "push"
                    is_correct = None

                # Edge as implied probability %
                edge_pct = calc_edge_pct(fair_spread, book_spread, book_odds)
                signal = determine_signal(edge_pct)

                self._upsert_prediction_grade({
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
                })
                rows_created += 1

            # Total
            total_data = book_data.get("total")
            if fair_total is not None and total_data and total_data.get("line") is not None:
                book_total = total_data["line"]
                gap = fair_total - book_total

                if gap > 0:
                    prediction_side = "over"
                    book_odds = total_data.get("over_odds") or -110
                    is_correct = final_total > book_total
                else:
                    prediction_side = "under"
                    book_odds = total_data.get("under_odds") or -110
                    is_correct = final_total < book_total

                if final_total == book_total:
                    actual_result = "push"
                    is_correct = None
                else:
                    actual_result = "over" if final_total > book_total else "under"

                edge_pct = calc_edge_pct(fair_total, book_total, book_odds)
                signal = determine_signal(edge_pct)

                self._upsert_prediction_grade({
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
                })
                rows_created += 1

            # Moneyline
            ml_data = book_data.get("moneyline")
            if closing_ml_home and closing_ml_away and ml_data:
                book_ml_home = ml_data.get("home_odds")
                book_ml_away = ml_data.get("away_odds")
                if book_ml_home and book_ml_away:
                    # Remove vig from consensus closing line for fair probability
                    fair_home_prob = american_to_implied(closing_ml_home)
                    fair_away_prob = american_to_implied(closing_ml_away)
                    total_prob = fair_home_prob + fair_away_prob
                    if total_prob > 0:
                        fair_home_prob /= total_prob
                        fair_away_prob /= total_prob

                    # Remove vig from book line for comparison
                    book_home_prob = american_to_implied(book_ml_home)
                    book_away_prob = american_to_implied(book_ml_away)
                    btotal = book_home_prob + book_away_prob
                    if btotal > 0:
                        book_home_prob /= btotal

                    gap = (fair_home_prob - book_home_prob) * 100
                    edge_pct = abs(gap)
                    signal = determine_signal(edge_pct)

                    winner = "home" if home_score > away_score else (
                        "away" if away_score > home_score else "push"
                    )

                    if gap > 0:
                        prediction_side = "home"
                        book_odds = book_ml_home
                        is_correct = winner == "home"
                    else:
                        prediction_side = "away"
                        book_odds = book_ml_away
                        is_correct = winner == "away"

                    if winner == "push":
                        is_correct = None

                    self._upsert_prediction_grade({
                        "game_id": game_id,
                        "sport_key": sport_key,
                        "market_type": "moneyline",
                        "period": "full",
                        "omi_fair_line": fair_home_prob * 100,
                        "book_line": book_home_prob * 100,
                        "book_name": book_name,
                        "book_odds": int(book_odds),
                        "gap": gap,
                        "signal": signal,
                        "confidence_tier": tier,
                        "prediction_side": prediction_side,
                        "actual_result": winner,
                        "is_correct": is_correct,
                        "pillar_composite": composite,
                        "ceq_score": None,
                        "graded_at": datetime.now(timezone.utc).isoformat(),
                    })
                    rows_created += 1

        return rows_created

    def _upsert_prediction_grade(self, record: dict):
        """Insert a prediction_grades row."""
        try:
            self.client.table("prediction_grades").insert(record).execute()
        except Exception as e:
            logger.error(f"Error inserting prediction grade: {e}")

    # ------------------------------------------------------------------
    # Performance aggregation
    # ------------------------------------------------------------------

    def get_performance(
        self,
        sport: Optional[str] = None,
        days: int = 30,
        market: Optional[str] = None,
        confidence_tier: Optional[int] = None,
        since: Optional[str] = None,
    ) -> dict:
        """Query prediction_grades and aggregate performance metrics."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        valid_game_ids: Optional[set] = None
        if since:
            gr_result = self.client.table("game_results").select("game_id").gte(
                "commence_time", since
            ).execute()
            valid_game_ids = {r["game_id"] for r in (gr_result.data or [])}

        query = self.client.table("prediction_grades").select("*").not_.is_(
            "graded_at", "null"
        ).gte("created_at", cutoff)

        if sport:
            query = query.eq("sport_key", sport)
        if market:
            query = query.eq("market_type", market)
        if confidence_tier:
            query = query.eq("confidence_tier", confidence_tier)

        result = query.execute()
        rows = result.data or []

        if valid_game_ids is not None:
            rows = [r for r in rows if r.get("game_id") in valid_game_ids]

        # Normalize sport keys for aggregation
        for r in rows:
            r["sport_key"] = _normalize_sport(r.get("sport_key", ""))

        return {
            "total_predictions": len(rows),
            "days": days,
            "filters": {
                "sport": sport,
                "market": market,
                "confidence_tier": confidence_tier,
                "since": since,
            },
            "by_confidence_tier": self._aggregate_by_field(rows, "confidence_tier"),
            "by_market": self._aggregate_by_field(rows, "market_type"),
            "by_sport": self._aggregate_by_field(rows, "sport_key"),
            "by_signal": self._aggregate_by_field(rows, "signal"),
            "by_pillar": self._pillar_performance(rows),
            "calibration": self._calibration(rows),
        }

    def _aggregate_by_field(self, rows: list, field: str) -> dict:
        """Aggregate hit rate and ROI by a grouping field."""
        groups: dict = {}
        for row in rows:
            key = row.get(field)
            if key is None:
                continue
            key = str(key)
            if key not in groups:
                groups[key] = {"total": 0, "correct": 0, "wrong": 0, "push": 0}

            groups[key]["total"] += 1
            if row.get("is_correct") is True:
                groups[key]["correct"] += 1
            elif row.get("is_correct") is False:
                groups[key]["wrong"] += 1
            else:
                groups[key]["push"] += 1

        result = {}
        for key, data in groups.items():
            decided = data["correct"] + data["wrong"]
            hit_rate = data["correct"] / decided if decided > 0 else 0
            roi = (data["correct"] * 0.91 - data["wrong"]) / data["total"] if data["total"] > 0 else 0
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

    def _calibration(self, rows: list) -> list:
        """Calculate calibration: predicted tier vs actual hit rate."""
        tiers = [55, 60, 65, 70]
        calibration = []

        for tier in tiers:
            tier_rows = [r for r in rows if r.get("confidence_tier") == tier]
            decided = [r for r in tier_rows if r.get("is_correct") is not None]
            correct = sum(1 for r in decided if r.get("is_correct") is True)
            actual_rate = correct / len(decided) * 100 if decided else 0

            calibration.append({
                "predicted": tier,
                "actual": round(actual_rate, 1),
                "sample_size": len(decided),
            })

        return calibration

    # ------------------------------------------------------------------
    # Regrade — purge + regenerate all prediction_grades
    # ------------------------------------------------------------------

    def regrade_all(self) -> dict:
        """Delete all prediction_grades and regenerate from graded game_results."""
        deleted = 0
        while True:
            batch = self.client.table("prediction_grades").select("id").limit(500).execute()
            ids = [r["id"] for r in (batch.data or [])]
            if not ids:
                break
            self.client.table("prediction_grades").delete().in_("id", ids).execute()
            deleted += len(ids)

        graded = self.client.table("game_results").select("game_id").not_.is_(
            "home_score", "null"
        ).execute()
        game_ids = [r["game_id"] for r in (graded.data or [])]

        created = 0
        errors = 0
        for gid in game_ids:
            try:
                created += self._generate_prediction_grades(gid)
            except Exception as e:
                logger.error(f"[Regrade] Error for {gid}: {e}")
                errors += 1

        logger.info(f"[Regrade] Purged {deleted}, regenerated {created} from {len(game_ids)} games")
        return {"purged": deleted, "games": len(game_ids), "created": created, "errors": errors}

    # ------------------------------------------------------------------
    # Graded Games — one row per game × market, per-book implied prob edges
    # ------------------------------------------------------------------

    @staticmethod
    def _omi_fair_display(fair_value: float, mtype: str, home: str, away: str) -> str:
        """Build OMI fair display string: 'O 242.5 (-134)' or 'Spurs +11.5 (-120)'."""
        if fair_value is None:
            return "—"

        # Find the nearest half-point as reference
        ref_half = round(fair_value * 2) / 2

        # Calculate fair price at the nearest half-point using point-to-prob model
        fp = calc_fair_price(fair_value, ref_half)

        if mtype == "total":
            direction = "O" if fair_value >= ref_half else "U"
            if abs(fair_value - ref_half) < 0.01:
                return f"PK {ref_half:.1f}"
            return f"{direction} {ref_half:.1f} ({fp:+d})" if fp != 0 else f"{direction} {ref_half:.1f}"
        elif mtype == "spread":
            if abs(fair_value - ref_half) < 0.01:
                sign = "+" if ref_half > 0 else ""
                return f"PK {sign}{ref_half:.1f}"
            if fair_value < ref_half:
                sign = "+" if ref_half > 0 else ""
                return f"{home} {sign}{ref_half:.1f} ({fp:+d})" if fp != 0 else f"{home} {sign}{ref_half:.1f}"
            else:
                away_half = -ref_half
                sign = "+" if away_half > 0 else ""
                return f"{away} {sign}{away_half:.1f} ({fp:+d})" if fp != 0 else f"{away} {sign}{away_half:.1f}"
        elif mtype == "moneyline":
            return f"{fair_value:.1f}% ({fp:+d})" if fp != 0 else f"{fair_value:.1f}%"

        return f"{fair_value:.1f}"

    def _book_detail_implied(self, brow, fair, mtype, home, away):
        """Extract per-book edge detail using point-to-probability model."""
        if brow is None or fair is None:
            return None
        bl = brow.get("book_line")
        if bl is None:
            return None

        book_odds = brow.get("book_odds") or -110
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
            # Spread / Total: point-to-probability model
            edge_pct = calc_edge_pct(float(fair), float(bl), book_odds)
            fp = calc_fair_price(float(fair), float(bl))

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
    ) -> dict:
        """Return graded predictions: one row per game×market, per-book implied prob edges."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        valid_game_ids: Optional[set] = None
        if since:
            gr_result = self.client.table("game_results").select("game_id").gte(
                "commence_time", since
            ).execute()
            valid_game_ids = {r["game_id"] for r in (gr_result.data or [])}

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
            home = game.get("home_team", "?")
            away = game.get("away_team", "?")

            fd = self._book_detail_implied(fd_row, fair, mtype, home, away)
            dk = self._book_detail_implied(dk_row, fair, mtype, home, away)

            # Best edge
            best_edge = None
            best_book = None
            if fd and dk:
                if fd["edge"] >= dk["edge"]:
                    best_edge, best_book = fd["edge"], "FD"
                else:
                    best_edge, best_book = dk["edge"], "DK"
            elif fd:
                best_edge, best_book = fd["edge"], "FD"
            elif dk:
                best_edge, best_book = dk["edge"], "DK"

            # Overall verdict from best-book row
            best_row = (fd_row if best_book == "FD" else dk_row) or first
            is_correct = best_row.get("is_correct")

            sport_normalized = _normalize_sport(first.get("sport_key", ""))

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
                "omi_fair_display": self._omi_fair_display(fair, mtype, home, away),
                "confidence_tier": first.get("confidence_tier"),
                "pillar_composite": first.get("pillar_composite"),
                "best_edge": best_edge,
                "best_book": best_book,
                "is_correct": is_correct,
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
        }

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
