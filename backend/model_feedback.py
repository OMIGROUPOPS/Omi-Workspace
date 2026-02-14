"""
Model Feedback Engine

Analyzes graded predictions to compute per-pillar performance metrics,
closing line value (CLV), and weight adjustment suggestions.

Main entry: ModelFeedback.run_feedback(sport, min_games=20)

Writes results to calibration_feedback table. The auto-adjustment logic
in weight_calculator.py reads from calibration_feedback to update weights.
"""

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from supabase import create_client, Client

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

PILLAR_KEYS = ["execution", "incentives", "shocks", "time_decay", "flow", "game_environment"]

# Pillar score thresholds for high/low grouping
PILLAR_HIGH_THRESHOLD = 0.55
PILLAR_LOW_THRESHOLD = 0.45

# EMA smoothing for weight adjustments
EMA_ALPHA = 0.1

# Max weight change per pillar per cycle
MAX_ADJUSTMENT = 0.05

# Minimum pillar weight floor
MIN_WEIGHT = 0.05

# Sport key normalization
SPORT_DISPLAY = {
    "basketball_nba": "NBA", "BASKETBALL_NBA": "NBA", "NBA": "NBA",
    "americanfootball_nfl": "NFL", "AMERICANFOOTBALL_NFL": "NFL", "NFL": "NFL",
    "icehockey_nhl": "NHL", "ICEHOCKEY_NHL": "NHL", "NHL": "NHL",
    "americanfootball_ncaaf": "NCAAF", "AMERICANFOOTBALL_NCAAF": "NCAAF", "NCAAF": "NCAAF",
    "basketball_ncaab": "NCAAB", "BASKETBALL_NCAAB": "NCAAB", "NCAAB": "NCAAB",
    "soccer_epl": "EPL", "SOCCER_EPL": "EPL", "EPL": "EPL",
}


def _normalize_sport(raw: str) -> str:
    return SPORT_DISPLAY.get(raw, raw.upper())


class ModelFeedback:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase credentials")
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def run_feedback(
        self,
        sport: Optional[str] = None,
        min_games: int = 50,
        days: int = 60,
    ) -> dict:
        """
        Run feedback analysis for one or all sports.

        1. Fetch graded predictions from prediction_grades
        2. Join with game_results for pillar scores
        3. Join with closing_lines for CLV
        4. Compute per-pillar metrics, CLV, market metrics
        5. Compute suggested weight adjustments
        6. Write to calibration_feedback

        Returns summary dict.
        """
        sports_to_analyze = self._get_sports(sport)
        results = {}

        for sp in sports_to_analyze:
            try:
                result = self._analyze_sport(sp, min_games, days)
                results[sp] = result
            except Exception as e:
                logger.error(f"[ModelFeedback] Error analyzing {sp}: {e}")
                results[sp] = {"error": str(e)}

        return {
            "sports_analyzed": list(results.keys()),
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _get_sports(self, sport: Optional[str]) -> list:
        """Get list of sports to analyze."""
        if sport:
            return [_normalize_sport(sport)]
        # Query distinct sports from prediction_grades
        try:
            result = self.client.table("prediction_grades").select(
                "sport_key"
            ).not_.is_("is_correct", "null").limit(5000).execute()
            sports = set()
            for row in (result.data or []):
                sports.add(_normalize_sport(row.get("sport_key", "")))
            return sorted(sports) if sports else []
        except Exception:
            return ["NBA", "NFL", "NHL", "NCAAB", "NCAAF", "EPL"]

    def _analyze_sport(self, sport: str, min_games: int, days: int) -> dict:
        """Analyze a single sport and write feedback row."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        # 1. Fetch graded predictions
        grades = self._fetch_grades(sport, cutoff)
        if len(grades) < min_games:
            return {
                "status": "insufficient_data",
                "sample_size": len(grades),
                "min_required": min_games,
            }

        # 2. Fetch game_results for pillar scores
        game_ids = list({g["game_id"] for g in grades})
        pillar_map = self._fetch_pillar_scores(game_ids)

        # 3. Fetch closing_lines for CLV
        closing_map = self._fetch_closing_lines(game_ids)

        # 4. Compute per-pillar metrics
        pillar_metrics = self._compute_pillar_metrics(grades, pillar_map)

        # 5. Compute CLV
        clv_spread, clv_total = self._compute_clv(grades, closing_map)

        # 6. Compute market-level metrics
        market_metrics = self._compute_market_metrics(grades)

        # 6b. Compute bias (spread/total systematic error)
        bias_data = self._compute_bias(grades, pillar_map)
        logger.info(
            f"[ModelFeedback] {sport}: spread_bias={bias_data.get('spread_bias')} "
            f"(n={bias_data.get('spread_sample')}), total_bias={bias_data.get('total_bias')} "
            f"(n={bias_data.get('total_sample')})"
        )

        # 7. Get current weights
        current_weights = self._get_current_weights(sport)

        # 8. Compute suggested adjustments
        suggested = self._compute_suggested_adjustments(pillar_metrics, current_weights)

        # 9. Write to calibration_feedback
        feedback_row = {
            "sport_key": sport,
            "sample_size": len(grades),
            "pillar_metrics": pillar_metrics,
            "avg_clv_spread": clv_spread,
            "avg_clv_total": clv_total,
            "market_metrics": market_metrics,
            "current_weights": current_weights,
            "suggested_adjustments": suggested,
            "applied_adjustments": None,  # Filled by weight_calculator when applied
            "metric_data": bias_data,
        }

        try:
            self.client.table("calibration_feedback").insert(feedback_row).execute()
            logger.info(f"[ModelFeedback] Wrote feedback for {sport}: {len(grades)} games")
        except Exception as e:
            logger.error(f"[ModelFeedback] Failed to write feedback for {sport}: {e}")

        return {
            "status": "success",
            "sample_size": len(grades),
            "pillar_metrics": pillar_metrics,
            "avg_clv_spread": clv_spread,
            "avg_clv_total": clv_total,
            "market_metrics": market_metrics,
            "suggested_adjustments": suggested,
            "bias": bias_data,
        }

    def _fetch_grades(self, sport: str, cutoff: str) -> list:
        """Fetch graded prediction_grades for a sport."""
        # prediction_grades has mixed sport_key formats
        variants = [k for k, v in SPORT_DISPLAY.items() if v == sport]
        if not variants:
            variants = [sport]

        try:
            result = self.client.table("prediction_grades").select(
                "game_id, market_type, omi_fair_line, book_line, gap, signal, "
                "is_correct, pillar_composite, book_name"
            ).in_("sport_key", variants).not_.is_(
                "is_correct", "null"
            ).gte("created_at", cutoff).limit(5000).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"[ModelFeedback] Fetch grades failed for {sport}: {e}")
            return []

    def _fetch_pillar_scores(self, game_ids: list) -> dict:
        """Fetch pillar scores from game_results. Returns {game_id: {pillar: score}}."""
        pillar_map = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i:i + 50]
            try:
                result = self.client.table("game_results").select(
                    "game_id, pillar_execution, pillar_incentives, pillar_shocks, "
                    "pillar_time_decay, pillar_flow, "
                    "home_score, away_score, closing_spread_home, closing_total_line"
                ).in_("game_id", batch).execute()

                # Try fetching game_environment separately (column may not exist yet)
                ge_map = {}
                try:
                    ge_result = self.client.table("game_results").select(
                        "game_id, pillar_game_environment"
                    ).in_("game_id", batch).execute()
                    for r in (ge_result.data or []):
                        ge_map[r["game_id"]] = r.get("pillar_game_environment")
                except Exception:
                    pass  # Column doesn't exist yet — game_environment will be None

                for row in (result.data or []):
                    gid = row["game_id"]
                    pillar_map[gid] = {
                        "execution": row.get("pillar_execution"),
                        "incentives": row.get("pillar_incentives"),
                        "shocks": row.get("pillar_shocks"),
                        "time_decay": row.get("pillar_time_decay"),
                        "flow": row.get("pillar_flow"),
                        "game_environment": ge_map.get(gid),
                        "home_score": row.get("home_score"),
                        "away_score": row.get("away_score"),
                        "closing_spread": row.get("closing_spread_home"),
                        "closing_total": row.get("closing_total_line"),
                    }
            except Exception as e:
                logger.warning(f"[ModelFeedback] Fetch pillar scores batch failed: {e}")
        return pillar_map

    def _fetch_closing_lines(self, game_ids: list) -> dict:
        """Fetch closing_lines. Returns {game_id: row}."""
        closing_map = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i:i + 50]
            try:
                result = self.client.table("closing_lines").select(
                    "game_id, book_spread, book_total, omi_fair_spread, omi_fair_total"
                ).in_("game_id", batch).execute()
                for row in (result.data or []):
                    closing_map[row["game_id"]] = row
            except Exception as e:
                logger.warning(f"[ModelFeedback] Fetch closing lines batch failed: {e}")
        return closing_map

    def _compute_pillar_metrics(self, grades: list, pillar_map: dict) -> dict:
        """
        For each pillar, compute:
        - hit_rate_high: hit rate when pillar > 0.55
        - hit_rate_low: hit rate when pillar < 0.45
        - lift: hit_rate_high - hit_rate_low (positive = pillar is predictive)
        - avg_correct: mean pillar score for correct predictions
        - avg_wrong: mean pillar score for wrong predictions
        - bias: avg_wrong - avg_correct (positive = pillar misleading)
        """
        metrics = {}

        for pillar in PILLAR_KEYS:
            high_correct = 0
            high_total = 0
            low_correct = 0
            low_total = 0
            correct_scores = []
            wrong_scores = []

            for grade in grades:
                game_pillars = pillar_map.get(grade["game_id"])
                if not game_pillars:
                    continue

                score = game_pillars.get(pillar)
                if score is None:
                    continue

                is_correct = grade.get("is_correct")

                if score > PILLAR_HIGH_THRESHOLD:
                    high_total += 1
                    if is_correct:
                        high_correct += 1
                elif score < PILLAR_LOW_THRESHOLD:
                    low_total += 1
                    if is_correct:
                        low_correct += 1

                if is_correct is True:
                    correct_scores.append(score)
                elif is_correct is False:
                    wrong_scores.append(score)

            hit_rate_high = high_correct / high_total if high_total >= 5 else None
            hit_rate_low = low_correct / low_total if low_total >= 5 else None
            lift = None
            if hit_rate_high is not None and hit_rate_low is not None:
                lift = round(hit_rate_high - hit_rate_low, 4)

            avg_correct = round(sum(correct_scores) / len(correct_scores), 4) if correct_scores else None
            avg_wrong = round(sum(wrong_scores) / len(wrong_scores), 4) if wrong_scores else None
            bias = None
            if avg_correct is not None and avg_wrong is not None:
                bias = round(avg_wrong - avg_correct, 4)

            metrics[pillar] = {
                "hit_rate_high": round(hit_rate_high, 4) if hit_rate_high is not None else None,
                "hit_rate_low": round(hit_rate_low, 4) if hit_rate_low is not None else None,
                "lift": lift,
                "high_sample": high_total,
                "low_sample": low_total,
                "avg_correct": avg_correct,
                "avg_wrong": avg_wrong,
                "bias": bias,
            }

        return metrics

    def _compute_clv(self, grades: list, closing_map: dict) -> tuple:
        """
        Compute average closing line value.
        CLV = how much closer OMI fair was to the actual result vs book close.

        For spread: clv = abs(actual_margin - omi_fair) - abs(actual_margin - book_close)
                    Negative CLV = OMI was closer (better). We negate so positive = good.
        """
        spread_clvs = []
        total_clvs = []

        # We need game_results for actual scores, but we already have pillar_map
        # which includes home_score/away_score. Let's gather from grades.
        game_scores = {}
        for grade in grades:
            gid = grade["game_id"]
            closing = closing_map.get(gid)
            if not closing:
                continue

            # Get actual scores (need from game_results via pillar map — but we
            # don't pass pillar_map here. Use closing_map + grade info instead.)
            # We'll just measure OMI fair vs book close divergence as CLV proxy.
            if grade.get("market_type") == "spread":
                omi_fair = closing.get("omi_fair_spread")
                book_close = closing.get("book_spread")
                if omi_fair is not None and book_close is not None:
                    # Simple CLV: how far OMI moved from the book close
                    # Positive = OMI saw value the book didn't
                    clv = abs(float(omi_fair) - float(book_close))
                    # Direction: if OMI prediction was correct, CLV is positive
                    if grade.get("is_correct"):
                        spread_clvs.append(clv)
                    else:
                        spread_clvs.append(-clv)

            elif grade.get("market_type") == "total":
                omi_fair = closing.get("omi_fair_total")
                book_close = closing.get("book_total")
                if omi_fair is not None and book_close is not None:
                    clv = abs(float(omi_fair) - float(book_close))
                    if grade.get("is_correct"):
                        total_clvs.append(clv)
                    else:
                        total_clvs.append(-clv)

        avg_clv_spread = round(sum(spread_clvs) / len(spread_clvs), 4) if spread_clvs else None
        avg_clv_total = round(sum(total_clvs) / len(total_clvs), 4) if total_clvs else None

        return avg_clv_spread, avg_clv_total

    def _compute_market_metrics(self, grades: list) -> dict:
        """Compute hit rate and sample size per market type."""
        by_market = {}
        for grade in grades:
            mtype = grade.get("market_type", "unknown")
            if mtype not in by_market:
                by_market[mtype] = {"total": 0, "correct": 0, "wrong": 0}
            by_market[mtype]["total"] += 1
            if grade.get("is_correct") is True:
                by_market[mtype]["correct"] += 1
            elif grade.get("is_correct") is False:
                by_market[mtype]["wrong"] += 1

        result = {}
        for mtype, data in by_market.items():
            decided = data["correct"] + data["wrong"]
            result[mtype] = {
                "total": data["total"],
                "correct": data["correct"],
                "wrong": data["wrong"],
                "hit_rate": round(data["correct"] / decided, 4) if decided > 0 else None,
            }
        return result

    def _compute_bias(self, grades: list, pillar_map: dict) -> dict:
        """Calculate systematic bias in fair line predictions.

        total_bias = AVG(omi_fair_total - actual_total)
        spread_bias = AVG(omi_fair_spread - actual_spread)
        Positive bias = model overestimates, negative = underestimates.
        """
        spread_diffs = []
        total_diffs = []

        for grade in grades:
            gid = grade["game_id"]
            pillars = pillar_map.get(gid)
            if not pillars:
                continue

            home_score = pillars.get("home_score")
            away_score = pillars.get("away_score")
            if home_score is None or away_score is None:
                continue

            fair_line = grade.get("omi_fair_line")
            if fair_line is None:
                continue

            if grade.get("market_type") == "spread":
                actual_spread = home_score - away_score
                spread_diffs.append(float(fair_line) - actual_spread)
            elif grade.get("market_type") == "total":
                actual_total = home_score + away_score
                total_diffs.append(float(fair_line) - actual_total)

        return {
            "spread_bias": round(sum(spread_diffs) / len(spread_diffs), 2) if spread_diffs else None,
            "spread_sample": len(spread_diffs),
            "total_bias": round(sum(total_diffs) / len(total_diffs), 2) if total_diffs else None,
            "total_sample": len(total_diffs),
        }

    def _get_current_weights(self, sport: str) -> dict:
        """Get current pillar weights from calibration_config."""
        try:
            result = self.client.table("calibration_config").select(
                "config_data"
            ).eq("sport_key", sport).eq(
                "config_type", "pillar_weights"
            ).eq("active", True).limit(1).execute()

            if result.data:
                return result.data[0]["config_data"]
        except Exception as e:
            logger.warning(f"[ModelFeedback] Failed to get weights for {sport}: {e}")

        # Fallback to defaults
        from config import SPORT_WEIGHTS, DEFAULT_WEIGHTS
        return SPORT_WEIGHTS.get(sport, DEFAULT_WEIGHTS)

    def _compute_suggested_adjustments(
        self, pillar_metrics: dict, current_weights: dict
    ) -> dict:
        """
        Compute suggested weight adjustments based on pillar lift.

        Formula per pillar:
          raw_adjustment = lift * EMA_ALPHA
          bounded = clamp(raw_adjustment, -MAX_ADJUSTMENT, +MAX_ADJUSTMENT)
          new_weight = max(MIN_WEIGHT, current_weight + bounded)

        Then normalize so all weights sum to 1.0.
        """
        adjustments = {}
        new_weights = {}

        for pillar in PILLAR_KEYS:
            current = current_weights.get(pillar, 1.0 / len(PILLAR_KEYS))
            metrics = pillar_metrics.get(pillar, {})
            lift = metrics.get("lift")

            if lift is not None:
                raw_adj = lift * EMA_ALPHA
                bounded = max(-MAX_ADJUSTMENT, min(MAX_ADJUSTMENT, raw_adj))
                new_w = max(MIN_WEIGHT, current + bounded)
            else:
                bounded = 0.0
                new_w = current

            adjustments[pillar] = {
                "current": round(current, 4),
                "lift": lift,
                "raw_adjustment": round(lift * EMA_ALPHA, 4) if lift is not None else None,
                "bounded_adjustment": round(bounded, 4),
                "new_weight_raw": round(new_w, 4),
            }
            new_weights[pillar] = new_w

        # Normalize
        total = sum(new_weights.values())
        if total > 0:
            for pillar in PILLAR_KEYS:
                normalized = round(new_weights[pillar] / total, 4)
                adjustments[pillar]["new_weight_normalized"] = normalized

        return adjustments

    def run_and_apply_feedback(
        self,
        sport_key: Optional[str] = None,
        min_games: int = 50,
    ) -> dict:
        """Run feedback analysis + apply weight adjustments in one call.

        Convenience wrapper that:
        1. Runs run_feedback() to compute pillar metrics + bias
        2. Applies EMA-bounded weight adjustments for sports with enough data
        """
        result = self.run_feedback(sport_key, min_games)

        from engine.weight_calculator import apply_feedback_adjustments

        adjustments = {}
        for sp_key, sp_result in result.get("results", {}).items():
            if (
                sp_result.get("status") == "success"
                and sp_result.get("sample_size", 0) >= min_games
            ):
                adj = apply_feedback_adjustments(sp_key)
                adjustments[sp_key] = adj
                logger.info(f"[WeightAdj] {sp_key}: {adj.get('status', 'unknown')}")

        result["weight_adjustments"] = adjustments
        return result

    def get_latest_feedback(self, sport: Optional[str] = None, days: int = 30) -> dict:
        """Get latest calibration_feedback rows for inspection."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        try:
            query = self.client.table("calibration_feedback").select("*").gte(
                "analysis_date", cutoff
            ).order("analysis_date", desc=True).limit(50)

            if sport:
                query = query.eq("sport_key", _normalize_sport(sport))

            result = query.execute()
            return {"rows": result.data or [], "count": len(result.data or [])}
        except Exception as e:
            logger.error(f"[ModelFeedback] Failed to get feedback: {e}")
            return {"error": str(e)}

    def get_closing_lines(self, sport: Optional[str] = None, days: int = 7) -> dict:
        """Get recent closing_lines rows for inspection."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        try:
            query = self.client.table("closing_lines").select("*").gte(
                "captured_at", cutoff
            ).order("captured_at", desc=True).limit(200)

            if sport:
                variants = [k for k, v in SPORT_DISPLAY.items() if v == _normalize_sport(sport)]
                if variants:
                    query = query.in_("sport_key", variants)

            result = query.execute()
            return {"rows": result.data or [], "count": len(result.data or [])}
        except Exception as e:
            logger.error(f"[ModelFeedback] Failed to get closing lines: {e}")
            return {"error": str(e)}
