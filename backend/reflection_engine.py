"""
Reflection Engine — Deep analysis of prediction accuracy and pillar effectiveness.

Queries game_results and prediction_grades to produce:
  a) Pillar contribution: which pillars actually predict outcomes (lift analysis)
  b) Scale calibration: what fair-line factors match reality
  c) Confidence calibration: predicted tier vs actual hit rates
  d) Bias detection: home/away, sport, market, favorite/underdog biases
  e) Weight recommendations: data-driven pillar weight suggestions
"""
import logging
from typing import Optional
from collections import defaultdict

from database import db
from config import SPORT_WEIGHTS, DEFAULT_WEIGHTS

logger = logging.getLogger(__name__)

PILLAR_COLUMNS = [
    "pillar_execution", "pillar_incentives", "pillar_shocks",
    "pillar_time_decay", "pillar_flow", "pillar_game_environment",
]
PILLAR_NAMES = [c.replace("pillar_", "") for c in PILLAR_COLUMNS]

CURRENT_SPREAD_FACTOR = 0.15
CURRENT_TOTAL_FACTOR = 0.20


class ReflectionEngine:

    def analyze(self, sport_filter: Optional[str] = None) -> dict:
        """Main entry point. Returns full reflection analysis."""
        if not db._is_connected():
            return {"error": "Database not connected"}

        games = self._fetch_games(sport_filter)
        grades = self._fetch_grades(sport_filter)

        pillar_contrib = self._pillar_contribution(games)

        return {
            "sample_size": len(games),
            "grades_count": len(grades),
            "sport_filter": sport_filter,
            "pillar_contribution": pillar_contrib,
            "scale_calibration": self._scale_calibration(games),
            "confidence_calibration": self._confidence_calibration(grades),
            "bias_detection": self._bias_detection(games, grades),
            "weight_recommendations": self._weight_recommendations(pillar_contrib, sport_filter),
        }

    # -------------------------------------------------------------------------
    # Data fetching
    # -------------------------------------------------------------------------

    def _fetch_games(self, sport_filter: Optional[str]) -> list:
        """Fetch graded game_results rows."""
        query = db.client.table("game_results").select("*").not_.is_("graded_at", "null")
        if sport_filter:
            query = query.eq("sport_key", sport_filter)
        result = query.execute()
        return result.data or []

    def _fetch_grades(self, sport_filter: Optional[str]) -> list:
        """Fetch graded prediction_grades rows."""
        query = db.client.table("prediction_grades").select("*").not_.is_("graded_at", "null")
        if sport_filter:
            query = query.eq("sport_key", sport_filter)
        result = query.execute()
        return result.data or []

    # -------------------------------------------------------------------------
    # (a) Pillar Contribution — lift analysis per pillar
    # -------------------------------------------------------------------------

    def _pillar_contribution(self, games: list) -> dict:
        """
        For each pillar, bucket games into LOW/NEUTRAL/HIGH and compute hit rates.
        Lift = HIGH hit rate - NEUTRAL hit rate.
        """
        result = {}

        for col, name in zip(PILLAR_COLUMNS, PILLAR_NAMES):
            buckets = {"low": [], "neutral": [], "high": []}

            for g in games:
                val = g.get(col)
                if val is None:
                    continue
                val = float(val)
                if val < 0.4:
                    buckets["low"].append(g)
                elif val <= 0.6:
                    buckets["neutral"].append(g)
                else:
                    buckets["high"].append(g)

            is_totals_pillar = (name == "game_environment")
            pillar_result = {}

            for bucket_name, bucket_games in buckets.items():
                hits, decided = 0, 0

                for g in bucket_games:
                    val = float(g.get(col, 0.5))
                    pillar_favors_home = val > 0.5
                    pillar_favors_over = val > 0.5

                    # In LOW bucket, the pillar signal is inverted
                    if bucket_name == "low":
                        pillar_favors_home = not pillar_favors_home
                        pillar_favors_over = not pillar_favors_over

                    # Spread: use raw final_spread vs closing_spread_home
                    final_spread = g.get("final_spread")
                    closing_spread = g.get("closing_spread_home")
                    if final_spread is not None and closing_spread is not None:
                        final_spread, closing_spread = float(final_spread), float(closing_spread)
                        if final_spread != closing_spread:  # not a push
                            decided += 1
                            home_covered = final_spread > closing_spread
                            if pillar_favors_home == home_covered:
                                hits += 1

                    # ML: use winner column ("home"/"away"/"push")
                    winner = g.get("winner")
                    if winner and winner != "push":
                        decided += 1
                        if pillar_favors_home and winner == "home":
                            hits += 1
                        elif not pillar_favors_home and winner == "away":
                            hits += 1

                    # Total: use raw final_total vs closing_total_line
                    if is_totals_pillar:
                        final_total = g.get("final_total")
                        closing_total = g.get("closing_total_line")
                        if final_total is not None and closing_total is not None:
                            final_total, closing_total = float(final_total), float(closing_total)
                            if final_total != closing_total:  # not a push
                                decided += 1
                                went_over = final_total > closing_total
                                if pillar_favors_over == went_over:
                                    hits += 1

                pillar_result[bucket_name] = {
                    "count": len(bucket_games),
                    "decided": decided,
                    "hits": hits,
                    "hit_rate": round(hits / decided, 4) if decided > 0 else None,
                }

            # Lift = HIGH hit rate - NEUTRAL hit rate
            high_rate = pillar_result["high"].get("hit_rate")
            neutral_rate = pillar_result["neutral"].get("hit_rate")
            pillar_result["lift"] = round(high_rate - neutral_rate, 4) if high_rate is not None and neutral_rate is not None else None

            result[name] = pillar_result

        return result

    # -------------------------------------------------------------------------
    # (b) Scale Calibration — optimal fair-line factors
    # -------------------------------------------------------------------------

    def _scale_calibration(self, games: list) -> dict:
        """Compare predicted edges vs actual margins to find optimal scale factors."""
        spread_edges, spread_margins = [], []
        total_edges, total_margins = [], []

        for g in games:
            # Spread
            edge = g.get("our_edge_spread_home")
            closing = g.get("closing_spread_home")
            final = g.get("final_spread")
            if edge is not None and closing is not None and final is not None:
                edge, closing, final = float(edge), float(closing), float(final)
                if edge != 0:
                    spread_edges.append(edge)
                    spread_margins.append(final - closing)

            # Total
            edge_t = g.get("our_edge_total_over")
            closing_t = g.get("closing_total_line")
            final_t = g.get("final_total")
            if edge_t is not None and closing_t is not None and final_t is not None:
                edge_t, closing_t, final_t = float(edge_t), float(closing_t), float(final_t)
                if edge_t != 0:
                    total_edges.append(edge_t)
                    total_margins.append(final_t - closing_t)

        spread_result = {
            "current_factor": CURRENT_SPREAD_FACTOR,
            "optimal_factor": None,
            "sample": len(spread_edges),
        }
        if spread_edges:
            mean_margin = sum(spread_margins) / len(spread_margins)
            mean_edge = sum(spread_edges) / len(spread_edges)
            if mean_edge != 0:
                spread_result["optimal_factor"] = round(mean_margin / mean_edge, 4)
            spread_result["mean_edge"] = round(mean_edge, 4)
            spread_result["mean_margin"] = round(mean_margin, 4)

        total_result = {
            "current_factor": CURRENT_TOTAL_FACTOR,
            "optimal_factor": None,
            "sample": len(total_edges),
        }
        if total_edges:
            mean_margin = sum(total_margins) / len(total_margins)
            mean_edge = sum(total_edges) / len(total_edges)
            if mean_edge != 0:
                total_result["optimal_factor"] = round(mean_margin / mean_edge, 4)
            total_result["mean_edge"] = round(mean_edge, 4)
            total_result["mean_margin"] = round(mean_margin, 4)

        return {"spread": spread_result, "total": total_result}

    # -------------------------------------------------------------------------
    # (c) Confidence Calibration — predicted tier vs actual
    # -------------------------------------------------------------------------

    def _confidence_calibration(self, grades: list) -> list:
        """Compare confidence tier predictions to actual hit rates."""
        tiers = defaultdict(lambda: {"correct": 0, "wrong": 0, "push": 0})

        for g in grades:
            tier = g.get("confidence_tier")
            if tier is None:
                continue
            is_correct = g.get("is_correct")
            if is_correct is True:
                tiers[tier]["correct"] += 1
            elif is_correct is False:
                tiers[tier]["wrong"] += 1
            else:
                tiers[tier]["push"] += 1

        result = []
        total_correct, total_decided = 0, 0

        for tier in sorted(tiers.keys()):
            data = tiers[tier]
            decided = data["correct"] + data["wrong"]
            rate = round(data["correct"] / decided * 100, 1) if decided > 0 else None
            total_correct += data["correct"]
            total_decided += decided
            result.append({
                "predicted": tier,
                "actual_hit_rate": rate,
                "sample_size": decided,
                "gap": round(rate - tier, 1) if rate is not None else None,
            })

        # Overall row
        overall_rate = round(total_correct / total_decided * 100, 1) if total_decided > 0 else None
        result.append({
            "predicted": "all",
            "actual_hit_rate": overall_rate,
            "sample_size": total_decided,
            "gap": None,
        })

        return result

    # -------------------------------------------------------------------------
    # (d) Bias Detection
    # -------------------------------------------------------------------------

    def _bias_detection(self, games: list, grades: list) -> dict:
        """Detect systematic biases in predictions."""

        # Home/away bias from game_results
        # spread_result is "win"/"loss"/"push" relative to our edge direction
        home_picks, home_hits = 0, 0
        away_picks, away_hits = 0, 0
        for g in games:
            sr = g.get("spread_result")
            edge_home = g.get("our_edge_spread_home")
            if sr is None or sr == "push" or edge_home is None:
                continue
            edge_home = float(edge_home)
            if edge_home > 0:
                home_picks += 1
                if sr == "win":
                    home_hits += 1
            elif edge_home < 0:
                away_picks += 1
                if sr == "win":
                    away_hits += 1

        home_away = {
            "home": {"picks": home_picks, "hits": home_hits, "rate": round(home_hits / home_picks, 4) if home_picks > 0 else None},
            "away": {"picks": away_picks, "hits": away_hits, "rate": round(away_hits / away_picks, 4) if away_picks > 0 else None},
        }

        # By sport
        sport_data = defaultdict(lambda: {"correct": 0, "wrong": 0})
        for g in grades:
            sport = g.get("sport_key")
            is_correct = g.get("is_correct")
            if sport and is_correct is not None:
                if is_correct:
                    sport_data[sport]["correct"] += 1
                else:
                    sport_data[sport]["wrong"] += 1
        by_sport = {}
        for sport, data in sport_data.items():
            total = data["correct"] + data["wrong"]
            by_sport[sport] = {
                "total": total,
                "hit_rate": round(data["correct"] / total, 4) if total > 0 else None,
            }

        # By market
        market_data = defaultdict(lambda: {"correct": 0, "wrong": 0})
        for g in grades:
            mkt = g.get("market_type")
            is_correct = g.get("is_correct")
            if mkt and is_correct is not None:
                if is_correct:
                    market_data[mkt]["correct"] += 1
                else:
                    market_data[mkt]["wrong"] += 1
        by_market = {}
        for mkt, data in market_data.items():
            total = data["correct"] + data["wrong"]
            by_market[mkt] = {
                "total": total,
                "hit_rate": round(data["correct"] / total, 4) if total > 0 else None,
            }

        # Favorite/underdog bias
        fav_picks, fav_hits = 0, 0
        dog_picks, dog_hits = 0, 0
        for g in games:
            closing = g.get("closing_spread_home")
            edge_home = g.get("our_edge_spread_home")
            sr = g.get("spread_result")
            if closing is None or edge_home is None or sr is None or sr == "push":
                continue
            closing, edge_home = float(closing), float(edge_home)
            home_is_fav = closing < 0

            if edge_home > 0:  # We picked home
                if home_is_fav:
                    fav_picks += 1
                    if sr == "win":
                        fav_hits += 1
                else:
                    dog_picks += 1
                    if sr == "win":
                        dog_hits += 1
            elif edge_home < 0:  # We picked away
                if not home_is_fav:  # Away is favorite
                    fav_picks += 1
                    if sr == "win":
                        fav_hits += 1
                else:
                    dog_picks += 1
                    if sr == "win":
                        dog_hits += 1

        fav_dog = {
            "favorite": {"picks": fav_picks, "hits": fav_hits, "rate": round(fav_hits / fav_picks, 4) if fav_picks > 0 else None},
            "underdog": {"picks": dog_picks, "hits": dog_hits, "rate": round(dog_hits / dog_picks, 4) if dog_picks > 0 else None},
        }

        return {
            "home_away": home_away,
            "by_sport": by_sport,
            "by_market": by_market,
            "fav_dog": fav_dog,
        }

    # -------------------------------------------------------------------------
    # (e) Weight Recommendations
    # -------------------------------------------------------------------------

    def _weight_recommendations(self, pillar_contribution: dict, sport_filter: Optional[str]) -> dict:
        """Suggest pillar weights based on observed lift."""
        lifts = {}
        total_games = 0

        for name in PILLAR_NAMES:
            data = pillar_contribution.get(name, {})
            lift = data.get("lift")
            lifts[name] = lift if lift is not None else 0.0
            total_games = max(total_games, data.get("high", {}).get("count", 0) + data.get("neutral", {}).get("count", 0) + data.get("low", {}).get("count", 0))

        # Normalize positive lifts to weights summing to 1.0
        # Floor negative lifts to small positive value so pillar isn't zeroed out
        adjusted = {k: max(v, 0.01) for k, v in lifts.items()}
        total_lift = sum(adjusted.values())
        recommended = {k: round(v / total_lift, 4) for k, v in adjusted.items()} if total_lift > 0 else {}

        # Get current weights for comparison
        if sport_filter:
            sport_upper = sport_filter.upper()
            # Handle Odds API format
            from engine.analyzer import SPORT_KEY_TO_LEAGUE
            league = SPORT_KEY_TO_LEAGUE.get(sport_filter, sport_upper)
            current = SPORT_WEIGHTS.get(league, DEFAULT_WEIGHTS)
        else:
            current = DEFAULT_WEIGHTS

        changes = {}
        for k in PILLAR_NAMES:
            if k in recommended and k in current:
                changes[k] = round(recommended[k] - current[k], 4)

        return {
            "recommended": recommended,
            "current": current,
            "changes": changes,
            "lifts": {k: round(v, 4) for k, v in lifts.items()},
            "low_sample": total_games < 100,
            "total_games": total_games,
        }
