"""
OMI Edge - Internal Grader
Enhanced grading with prediction_grades table for per-market/period/book granularity.
"""

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


def composite_to_confidence_tier(composite: float) -> Optional[int]:
    """Map composite score (0-1) to confidence tier."""
    # Convert 0-1 scale to 0-100 for tier thresholds
    score = composite * 100
    if score >= 70:
        return 70
    elif score >= 65:
        return 65
    elif score >= 60:
        return 60
    elif score >= 55:
        return 55
    return None  # No prediction


def determine_signal(gap: float, market_type: str) -> str:
    """Determine signal from gap size."""
    abs_gap = abs(gap)
    if market_type == "spread":
        if abs_gap >= 3:
            return "MISPRICED"
        elif abs_gap >= 1.5:
            return "VALUE"
        elif abs_gap >= 0.5:
            return "FAIR"
        return "SHARP"
    elif market_type == "total":
        if abs_gap >= 3:
            return "MISPRICED"
        elif abs_gap >= 1.5:
            return "VALUE"
        elif abs_gap >= 0.5:
            return "FAIR"
        return "SHARP"
    else:  # moneyline — gap is in implied probability %
        if abs_gap >= 8:
            return "MISPRICED"
        elif abs_gap >= 4:
            return "VALUE"
        elif abs_gap >= 2:
            return "FAIR"
        return "SHARP"


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
        # Step 0: Bootstrap game_results from predictions table.
        # The scheduler creates predictions but never calls snapshot_prediction_at_close,
        # so game_results may be empty. We need to create game_results rows for
        # completed games that have predictions but no game_results entry.
        bootstrapped = self._bootstrap_game_results(sport)
        logger.info(f"[InternalGrader] Bootstrapped {bootstrapped} game_results from predictions")

        # Step 1: Run existing auto-grader
        grader = AutoGrader(self.tracker)
        auto_result = grader.grade_completed_games(sport)

        graded_count = 0
        errors = []

        # Step 2: For each graded game, generate prediction_grades rows
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
        """
        Create game_results rows from predictions for completed games.

        The scheduler writes to the predictions table but never calls
        snapshot_prediction_at_close(), so game_results stays empty.
        This method bridges that gap by snapshotting predictions for
        games that have already started (commence_time in the past).
        """
        cutoff = datetime.now(timezone.utc).isoformat()
        count = 0

        try:
            # Find predictions for completed games
            query = self.client.table("predictions").select(
                "game_id, sport_key"
            ).lt("commence_time", cutoff)

            if sport:
                query = query.eq("sport_key", sport)

            result = query.execute()
            predictions = result.data or []

            if not predictions:
                logger.info("[InternalGrader] No completed predictions to bootstrap")
                return 0

            # Check which ones already have game_results
            game_ids = [p["game_id"] for p in predictions]

            # Query in batches of 50 to avoid URL length issues
            existing_ids = set()
            for i in range(0, len(game_ids), 50):
                batch = game_ids[i:i+50]
                existing = self.client.table("game_results").select(
                    "game_id"
                ).in_("game_id", batch).execute()
                existing_ids.update(r["game_id"] for r in (existing.data or []))

            # Snapshot predictions that don't have game_results yet
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

    def _generate_prediction_grades(self, game_id: str) -> int:
        """Generate prediction_grades rows for a graded game."""
        # Get game_results record
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
            return 0  # Below threshold, skip

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

        # Get per-book lines from cached_odds
        book_lines = self._get_book_lines(game_id)

        rows_created = 0

        # Generate rows for each market + book
        for book_name, book_data in book_lines.items():
            # Spread
            if fair_spread is not None and "spread" in book_data:
                book_spread = book_data["spread"]
                gap = fair_spread - book_spread
                signal = determine_signal(gap, "spread")

                # Determine prediction side and actual result
                if gap > 0:
                    prediction_side = "away"
                    actual_result = "away_covered" if final_spread < closing_spread else (
                        "push" if final_spread == closing_spread else "home_covered"
                    )
                    is_correct = final_spread < book_spread
                else:
                    prediction_side = "home"
                    actual_result = "home_covered" if final_spread > closing_spread else (
                        "push" if final_spread == closing_spread else "away_covered"
                    )
                    is_correct = final_spread > book_spread

                if final_spread == book_spread:
                    actual_result = "push"
                    is_correct = None  # Push = no decision

                self._upsert_prediction_grade({
                    "game_id": game_id,
                    "sport_key": sport_key,
                    "market_type": "spread",
                    "period": "full",
                    "omi_fair_line": fair_spread,
                    "book_line": book_spread,
                    "book_name": book_name,
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
            if fair_total is not None and "total" in book_data:
                book_total = book_data["total"]
                gap = fair_total - book_total
                signal = determine_signal(gap, "total")

                if gap > 0:
                    prediction_side = "over"
                    is_correct = final_total > book_total
                else:
                    prediction_side = "under"
                    is_correct = final_total < book_total

                if final_total == book_total:
                    actual_result = "push"
                    is_correct = None
                else:
                    actual_result = "over" if final_total > book_total else "under"

                self._upsert_prediction_grade({
                    "game_id": game_id,
                    "sport_key": sport_key,
                    "market_type": "total",
                    "period": "full",
                    "omi_fair_line": fair_total,
                    "book_line": book_total,
                    "book_name": book_name,
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
            if closing_ml_home and closing_ml_away and "moneyline_home" in book_data:
                # Use vig-free implied probabilities for comparison
                fair_home_prob = self._implied_prob(closing_ml_home)
                fair_away_prob = self._implied_prob(closing_ml_away)
                total_prob = fair_home_prob + fair_away_prob
                if total_prob > 0:
                    fair_home_prob /= total_prob
                    fair_away_prob /= total_prob

                book_ml_home = book_data.get("moneyline_home")
                book_ml_away = book_data.get("moneyline_away")
                if book_ml_home and book_ml_away:
                    book_home_prob = self._implied_prob(book_ml_home)
                    book_away_prob = self._implied_prob(book_ml_away)
                    btotal = book_home_prob + book_away_prob
                    if btotal > 0:
                        book_home_prob /= btotal

                    gap = (fair_home_prob - book_home_prob) * 100  # in percentage points
                    signal = determine_signal(gap, "moneyline")

                    winner = "home" if home_score > away_score else ("away" if away_score > home_score else "push")

                    if gap > 0:
                        prediction_side = "home"
                        is_correct = winner == "home"
                    else:
                        prediction_side = "away"
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

    def _get_book_lines(self, game_id: str) -> dict:
        """Get closing lines per book from line_snapshots."""
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
                key = f"{book}_{mtype}_{outcome}"

                if key in seen:
                    continue
                seen.add(key)

                if book not in books:
                    books[book] = {}

                if mtype == "spread":
                    books[book]["spread"] = snap.get("line", 0)
                elif mtype == "total":
                    books[book]["total"] = snap.get("line", 0)
                elif mtype == "moneyline":
                    if outcome == "home":
                        books[book]["moneyline_home"] = snap.get("odds", 0)
                    elif outcome == "away":
                        books[book]["moneyline_away"] = snap.get("odds", 0)

            return books
        except Exception as e:
            logger.error(f"Error getting book lines for {game_id}: {e}")
            return {}

    def _implied_prob(self, american_odds: int) -> float:
        """Convert American odds to implied probability."""
        if american_odds is None:
            return 0.5
        if american_odds < 0:
            return abs(american_odds) / (abs(american_odds) + 100)
        return 100 / (american_odds + 100)

    def _upsert_prediction_grade(self, record: dict):
        """Insert a prediction_grades row."""
        try:
            self.client.table("prediction_grades").insert(record).execute()
        except Exception as e:
            logger.error(f"Error inserting prediction grade: {e}")

    def get_performance(
        self,
        sport: Optional[str] = None,
        days: int = 30,
        market: Optional[str] = None,
        confidence_tier: Optional[int] = None,
        since: Optional[str] = None,
    ) -> dict:
        """
        Query prediction_grades and aggregate performance metrics.

        Args:
            since: Optional ISO date string. When provided, only include
                   prediction_grades whose game commenced on or after this date.
                   Used by the "Clean Data Only" toggle (since=2026-02-10).
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        # If `since` is provided, pre-filter to game_ids with commence_time >= since
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

        # Apply since filter if needed
        if valid_game_ids is not None:
            rows = [r for r in rows if r.get("game_id") in valid_game_ids]

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
            # ROI assumes -110 odds: win pays 0.91, loss costs 1.0
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
    # Graded Games — individual prediction rows with game context
    # ------------------------------------------------------------------

    def get_graded_games(
        self,
        sport: Optional[str] = None,
        market: Optional[str] = None,
        verdict: Optional[str] = None,
        since: Optional[str] = None,
        days: int = 30,
        limit: int = 500,
    ) -> dict:
        """Return individual graded prediction rows merged with game context."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        # Pre-filter game_ids by commence_time if `since` is set
        valid_game_ids: Optional[set] = None
        if since:
            gr_result = self.client.table("game_results").select("game_id").gte(
                "commence_time", since
            ).execute()
            valid_game_ids = {r["game_id"] for r in (gr_result.data or [])}

        # Query prediction_grades
        query = self.client.table("prediction_grades").select("*").not_.is_(
            "graded_at", "null"
        ).gte("created_at", cutoff).order("graded_at", desc=True).limit(limit)

        if sport:
            query = query.eq("sport_key", sport)
        if market:
            query = query.eq("market_type", market)

        result = query.execute()
        rows = result.data or []

        # Apply since filter
        if valid_game_ids is not None:
            rows = [r for r in rows if r.get("game_id") in valid_game_ids]

        # Apply verdict filter
        if verdict == "win":
            rows = [r for r in rows if r.get("is_correct") is True]
        elif verdict == "loss":
            rows = [r for r in rows if r.get("is_correct") is False]
        elif verdict == "push":
            rows = [r for r in rows if r.get("is_correct") is None]

        # Fetch game context from game_results
        game_ids = list({r["game_id"] for r in rows})
        game_map: dict = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i : i + 50]
            gr = self.client.table("game_results").select(
                "game_id, home_team, away_team, commence_time, home_score, away_score"
            ).in_("game_id", batch).execute()
            for g in (gr.data or []):
                game_map[g["game_id"]] = g

        # Merge rows
        merged = []
        for row in rows:
            game = game_map.get(row["game_id"], {})
            merged.append({
                "game_id": row["game_id"],
                "sport_key": row.get("sport_key"),
                "home_team": game.get("home_team", ""),
                "away_team": game.get("away_team", ""),
                "commence_time": game.get("commence_time", ""),
                "home_score": game.get("home_score"),
                "away_score": game.get("away_score"),
                "market_type": row.get("market_type"),
                "book_name": row.get("book_name"),
                "omi_fair_line": row.get("omi_fair_line"),
                "book_line": row.get("book_line"),
                "gap": row.get("gap"),
                "signal": row.get("signal"),
                "confidence_tier": row.get("confidence_tier"),
                "pillar_composite": row.get("pillar_composite"),
                "prediction_side": row.get("prediction_side"),
                "actual_result": row.get("actual_result"),
                "is_correct": row.get("is_correct"),
            })

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

    def _best_group(self, rows: list, field: str, min_sample: int = 10) -> Optional[dict]:
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
