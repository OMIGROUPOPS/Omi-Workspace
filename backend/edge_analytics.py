"""
Edge Analytics Module

Deep per-result attribution, calibration curves, conditional breakdowns,
CLV analysis, and auto-generated plain-English insights.

Computes everything on-read from prediction_grades + game_results + closing_lines.
No new tables required.
"""

import logging
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from internal_grader import calc_edge_pct

logger = logging.getLogger(__name__)

# Sport key normalization (same as model_feedback.py)
SPORT_DISPLAY = {
    "basketball_nba": "NBA", "BASKETBALL_NBA": "NBA", "NBA": "NBA",
    "americanfootball_nfl": "NFL", "AMERICANFOOTBALL_NFL": "NFL", "NFL": "NFL",
    "icehockey_nhl": "NHL", "ICEHOCKEY_NHL": "NHL", "NHL": "NHL",
    "americanfootball_ncaaf": "NCAAF", "AMERICANFOOTBALL_NCAAF": "NCAAF", "NCAAF": "NCAAF",
    "basketball_ncaab": "NCAAB", "BASKETBALL_NCAAB": "NCAAB", "NCAAB": "NCAAB",
    "soccer_epl": "EPL", "SOCCER_EPL": "EPL", "EPL": "EPL",
}

PILLAR_KEYS = ["execution", "incentives", "shocks", "time_decay", "flow", "game_environment"]

# Column name mapping: pillar key -> game_results column
PILLAR_COLUMNS = {
    "execution": "pillar_execution",
    "incentives": "pillar_incentives",
    "shocks": "pillar_shocks",
    "time_decay": "pillar_time_decay",
    "flow": "pillar_flow",
}

# Minimum sample to generate an insight
MIN_INSIGHT_SAMPLE = 10

# Edge bucket boundaries and midpoints
EDGE_BUCKETS = [
    ("<1%", 0, 1.0, 0.5),
    ("1-2%", 1.0, 2.0, 1.5),
    ("2-4%", 2.0, 4.0, 3.0),
    ("4-6%", 4.0, 6.0, 5.0),
    ("6-10%", 6.0, 10.0, 8.0),
    ("10%+", 10.0, 999, 12.0),
]


def _normalize_sport(raw: str) -> str:
    return SPORT_DISPLAY.get(raw, raw.upper())


def _edge_bucket(edge_pct: float) -> str:
    for label, lo, hi, _ in EDGE_BUCKETS:
        if lo <= edge_pct < hi:
            return label
    return "10%+"


def _spread_size_bucket(book_line, market_type: str) -> Optional[str]:
    if market_type != "spread" or book_line is None:
        return None
    abs_spread = abs(float(book_line))
    if abs_spread <= 1.0:
        return "pick_em"
    elif abs_spread <= 4.0:
        return "small"
    elif abs_spread <= 8.0:
        return "medium"
    else:
        return "large"


class EdgeAnalytics:
    def __init__(self):
        from database import db
        self.client = db.client

    # ── Data fetching ──────────────────────────────────────────────

    def _fetch_grades(self, sport: Optional[str], cutoff: str) -> list:
        try:
            if sport:
                variants = [k for k, v in SPORT_DISPLAY.items() if v == sport]
                if not variants:
                    variants = [sport]
            else:
                variants = None

            query = self.client.table("prediction_grades").select(
                "game_id, sport_key, market_type, omi_fair_line, book_line, gap, "
                "signal, confidence_tier, prediction_side, actual_result, "
                "is_correct, pillar_composite, book_name, graded_at, created_at"
            ).not_.is_("is_correct", "null").gte("created_at", cutoff).limit(5000)

            if variants:
                query = query.in_("sport_key", variants)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"[EdgeAnalytics] Fetch grades failed: {e}")
            return []

    def _fetch_game_results(self, game_ids: list) -> dict:
        game_map = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i:i + 50]
            try:
                result = self.client.table("game_results").select(
                    "game_id, sport_key, home_team, away_team, commence_time, "
                    "home_score, away_score, final_spread, final_total, "
                    "pillar_execution, pillar_incentives, pillar_shocks, "
                    "pillar_time_decay, pillar_flow, "
                    "closing_spread_home, closing_total_line"
                ).in_("game_id", batch).execute()

                # Try game_environment separately (column may not exist)
                ge_map = {}
                try:
                    ge_result = self.client.table("game_results").select(
                        "game_id, pillar_game_environment"
                    ).in_("game_id", batch).execute()
                    for r in (ge_result.data or []):
                        ge_map[r["game_id"]] = r.get("pillar_game_environment")
                except Exception:
                    pass

                for row in (result.data or []):
                    gid = row["game_id"]
                    row["pillar_game_environment"] = ge_map.get(gid)
                    game_map[gid] = row
            except Exception as e:
                logger.warning(f"[EdgeAnalytics] Fetch game_results batch failed: {e}")
        return game_map

    def _fetch_closing_lines(self, game_ids: list) -> dict:
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
                logger.warning(f"[EdgeAnalytics] Fetch closing_lines batch failed: {e}")
        return closing_map

    # ── Per-result attribution ─────────────────────────────────────

    def _per_result_attribution(self, grades: list, game_map: dict, closing_map: dict) -> list:
        attributed = []

        for grade in grades:
            gid = grade["game_id"]
            game = game_map.get(gid)
            if not game:
                continue

            market = grade.get("market_type", "")
            omi_fair = grade.get("omi_fair_line")
            book_line = grade.get("book_line")
            is_correct = grade.get("is_correct")

            if omi_fair is None or book_line is None:
                continue

            omi_fair = float(omi_fair)
            book_line = float(book_line)

            # Actual numeric result
            if market == "spread":
                actual_value = game.get("final_spread")
            elif market == "total":
                actual_value = game.get("final_total")
            else:
                continue  # moneyline excluded from grading

            if actual_value is None:
                continue
            actual_value = float(actual_value)

            # Edge pct
            edge_pct = calc_edge_pct(omi_fair, book_line, market)

            # Fair line error vs book line error
            fair_line_error = round(abs(omi_fair - actual_value), 2)
            book_line_error = round(abs(book_line - actual_value), 2)
            omi_beat_book = fair_line_error < book_line_error

            # Dominant pillar
            pillars = {}
            for pk in PILLAR_KEYS:
                col = PILLAR_COLUMNS.get(pk, f"pillar_{pk}")
                val = game.get(col)
                if val is not None:
                    pillars[pk] = float(val)

            dominant_pillar = None
            dominant_pillar_correct = None
            if pillars:
                dominant_pillar = max(pillars, key=lambda k: abs(pillars[k] - 0.5))
                dominant_value = pillars[dominant_pillar]
                pillar_leans_home = dominant_value > 0.5

                if market == "spread":
                    closing_spread = game.get("closing_spread_home")
                    if closing_spread is not None:
                        # Home covered if final_spread < closing_spread (spread is negative for home fav)
                        # Actually: pillar > 0.5 = home favored. Check if home side won.
                        actual_favored_home = actual_value < float(closing_spread)
                        dominant_pillar_correct = pillar_leans_home == actual_favored_home
                elif market == "total":
                    closing_total = game.get("closing_total_line")
                    if closing_total is not None:
                        went_over = actual_value > float(closing_total)
                        pillar_said_over = dominant_value > 0.5
                        dominant_pillar_correct = pillar_said_over == went_over

            # CLV from closing_lines
            clv = None
            closing = closing_map.get(gid)
            if closing:
                if market == "spread":
                    omi_cl = closing.get("omi_fair_spread")
                    book_cl = closing.get("book_spread")
                elif market == "total":
                    omi_cl = closing.get("omi_fair_total")
                    book_cl = closing.get("book_total")
                else:
                    omi_cl = book_cl = None

                if omi_cl is not None and book_cl is not None:
                    clv = round(abs(float(omi_cl) - float(book_cl)), 3)
                    if is_correct is False:
                        clv = -clv

            attributed.append({
                # Original fields
                "game_id": gid,
                "sport_key": _normalize_sport(grade.get("sport_key", "")),
                "market_type": market,
                "signal": grade.get("signal"),
                "confidence_tier": grade.get("confidence_tier"),
                "is_correct": is_correct,
                "pillar_composite": grade.get("pillar_composite"),
                "book_name": grade.get("book_name"),
                "prediction_side": grade.get("prediction_side"),
                "commence_time": game.get("commence_time"),
                # Computed
                "edge_pct": edge_pct,
                "fair_line_error": fair_line_error,
                "book_line_error": book_line_error,
                "omi_beat_book": omi_beat_book,
                "dominant_pillar": dominant_pillar,
                "dominant_pillar_correct": dominant_pillar_correct,
                "pillar_scores": pillars,
                "clv": clv,
                "edge_bucket": _edge_bucket(edge_pct),
                "spread_size_bucket": _spread_size_bucket(book_line, market),
            })

        return attributed

    # ── Calibration analysis ───────────────────────────────────────

    def _calibration_analysis(self, attributed: list) -> dict:
        # Group by edge bucket
        buckets = {}
        for row in attributed:
            b = row.get("edge_bucket", "<1%")
            if b not in buckets:
                buckets[b] = {"correct": 0, "wrong": 0}
            if row["is_correct"] is True:
                buckets[b]["correct"] += 1
            elif row["is_correct"] is False:
                buckets[b]["wrong"] += 1

        calibration = {}
        for label, _, _, midpoint in EDGE_BUCKETS:
            data = buckets.get(label, {"correct": 0, "wrong": 0})
            decided = data["correct"] + data["wrong"]
            expected = round(50.0 + midpoint / 2, 1)
            actual = round(data["correct"] / decided * 100, 1) if decided > 0 else None
            calibration[label] = {
                "expected_win_rate": expected,
                "actual_win_rate": actual,
                "n": decided,
                "correct": data["correct"],
                "wrong": data["wrong"],
                "gap": round(actual - expected, 1) if actual is not None else None,
            }

        # OMI vs Book accuracy
        omi_closer = sum(1 for r in attributed if r.get("omi_beat_book") is True)
        book_closer = sum(1 for r in attributed if r.get("omi_beat_book") is False)
        total_compared = omi_closer + book_closer

        # Average fair line error per market
        spread_omi_errs = [r["fair_line_error"] for r in attributed if r["market_type"] == "spread"]
        spread_book_errs = [r["book_line_error"] for r in attributed if r["market_type"] == "spread"]
        total_omi_errs = [r["fair_line_error"] for r in attributed if r["market_type"] == "total"]
        total_book_errs = [r["book_line_error"] for r in attributed if r["market_type"] == "total"]

        return {
            "by_edge_bucket": calibration,
            "omi_vs_book": {
                "omi_closer": omi_closer,
                "book_closer": book_closer,
                "total": total_compared,
                "omi_pct": round(omi_closer / total_compared * 100, 1) if total_compared > 0 else None,
            },
            "avg_fair_line_error": {
                "spread": round(sum(spread_omi_errs) / len(spread_omi_errs), 2) if spread_omi_errs else None,
                "total": round(sum(total_omi_errs) / len(total_omi_errs), 2) if total_omi_errs else None,
            },
            "avg_book_line_error": {
                "spread": round(sum(spread_book_errs) / len(spread_book_errs), 2) if spread_book_errs else None,
                "total": round(sum(total_book_errs) / len(total_book_errs), 2) if total_book_errs else None,
            },
        }

    # ── Conditional analysis ───────────────────────────────────────

    def _group_hit_rate(self, rows: list, field: str) -> dict:
        groups: Dict[str, Dict] = {}
        for row in rows:
            key = row.get(field)
            if key is None:
                continue
            key = str(key)
            if key not in groups:
                groups[key] = {"correct": 0, "wrong": 0}
            if row.get("is_correct") is True:
                groups[key]["correct"] += 1
            elif row.get("is_correct") is False:
                groups[key]["wrong"] += 1

        result = {}
        for key, data in groups.items():
            decided = data["correct"] + data["wrong"]
            result[key] = {
                "hit_rate": round(data["correct"] / decided * 100, 1) if decided > 0 else None,
                "n": decided,
                "correct": data["correct"],
                "wrong": data["wrong"],
            }
        return result

    def _conditional_analysis(self, attributed: list) -> dict:
        return {
            "by_sport": self._group_hit_rate(attributed, "sport_key"),
            "by_spread_size": self._group_hit_rate(
                [r for r in attributed if r.get("spread_size_bucket")],
                "spread_size_bucket",
            ),
            "by_dominant_pillar": self._group_hit_rate(
                [r for r in attributed if r.get("dominant_pillar")],
                "dominant_pillar",
            ),
            "by_signal": self._group_hit_rate(attributed, "signal"),
            "by_market_type": self._group_hit_rate(attributed, "market_type"),
        }

    # ── CLV analysis ───────────────────────────────────────────────

    def _clv_analysis(self, attributed: list) -> dict:
        spread_clvs = [r["clv"] for r in attributed if r.get("clv") is not None and r["market_type"] == "spread"]
        total_clvs = [r["clv"] for r in attributed if r.get("clv") is not None and r["market_type"] == "total"]
        all_clvs = spread_clvs + total_clvs

        def _clv_stats(clvs: list) -> dict:
            if not clvs:
                return {"avg_clv": None, "pct_positive": None, "n": 0}
            return {
                "avg_clv": round(sum(clvs) / len(clvs), 3),
                "pct_positive": round(sum(1 for c in clvs if c > 0) / len(clvs) * 100, 1),
                "n": len(clvs),
            }

        return {
            "spread": _clv_stats(spread_clvs),
            "total": _clv_stats(total_clvs),
            "overall": _clv_stats(all_clvs),
        }

    # ── Insights generation ────────────────────────────────────────

    def _generate_insights(self, calibration: dict, conditional: dict, clv: dict, attributed: list) -> list:
        insights = []
        N = MIN_INSIGHT_SAMPLE

        # 1. Dominant pillar performance
        by_pillar = conditional.get("by_dominant_pillar", {})
        for pillar, data in sorted(by_pillar.items(), key=lambda x: x[1].get("hit_rate", 50), reverse=True):
            if data["n"] >= N:
                rate = data["hit_rate"]
                if rate >= 58:
                    insights.append(f"{pillar.replace('_', ' ').title()}-driven picks hit at {rate}% ({data['n']} picks) -- trust this signal")
                elif rate <= 45:
                    insights.append(f"{pillar.replace('_', ' ').title()}-driven picks only {rate}% ({data['n']} picks) -- this pillar misleads")

        # 2. Spread size
        by_spread = conditional.get("by_spread_size", {})
        for bucket, data in by_spread.items():
            if data["n"] >= N:
                rate = data["hit_rate"]
                label = bucket.replace("_", " ").title()
                if rate >= 58:
                    insights.append(f"{label} spreads hit at {rate}% ({data['n']} picks)")
                elif rate <= 45:
                    insights.append(f"{label} spreads only {rate}% ({data['n']} picks) -- model struggles here")

        # 3. Calibration gaps
        by_bucket = calibration.get("by_edge_bucket", {})
        for bucket, data in by_bucket.items():
            if data["n"] >= N and data.get("gap") is not None:
                gap = data["gap"]
                if gap >= 5:
                    insights.append(f"{bucket} edges outperform expected by {gap}pp ({data['actual_win_rate']}% actual vs {data['expected_win_rate']}% expected, {data['n']} picks)")
                elif gap <= -5:
                    insights.append(f"{bucket} edges underperform expected by {abs(gap)}pp ({data['actual_win_rate']}% actual vs {data['expected_win_rate']}% expected, {data['n']} picks)")

        # 4. OMI vs Book accuracy
        omi_vs = calibration.get("omi_vs_book", {})
        omi_pct = omi_vs.get("omi_pct")
        if omi_pct is not None and omi_vs.get("total", 0) >= 20:
            if omi_pct >= 52:
                insights.append(f"OMI fair line closer to actual result than books {omi_pct}% of the time ({omi_vs['total']} games)")
            elif omi_pct <= 48:
                insights.append(f"Books closer to actual result than OMI {round(100 - omi_pct, 1)}% of the time -- fair line needs work")

        # 5. Fair line error comparison
        avg_omi = calibration.get("avg_fair_line_error", {})
        avg_book = calibration.get("avg_book_line_error", {})
        for mkt in ["spread", "total"]:
            omi_err = avg_omi.get(mkt)
            book_err = avg_book.get(mkt)
            if omi_err is not None and book_err is not None:
                if omi_err < book_err:
                    insights.append(f"OMI {mkt} error {omi_err} pts vs book {book_err} pts -- OMI is more accurate")
                elif omi_err > book_err + 0.5:
                    insights.append(f"OMI {mkt} error {omi_err} pts vs book {book_err} pts -- books are more accurate")

        # 6. CLV
        overall_clv = clv.get("overall", {})
        if overall_clv.get("n", 0) >= 20:
            pct_pos = overall_clv.get("pct_positive")
            avg = overall_clv.get("avg_clv")
            if pct_pos is not None and pct_pos >= 55:
                insights.append(f"Positive CLV on {pct_pos}% of picks (avg {avg} pts) -- market moves toward OMI")
            elif pct_pos is not None and pct_pos <= 45:
                insights.append(f"Only {pct_pos}% of picks had positive CLV (avg {avg} pts) -- lines moving against us")

        # 7. Signal tier performance
        by_signal = conditional.get("by_signal", {})
        for sig in ["MID EDGE", "HIGH EDGE", "LOW EDGE"]:
            data = by_signal.get(sig, {})
            if data.get("n", 0) >= N:
                insights.append(f"{sig} signals: {data['hit_rate']}% hit rate ({data['n']} picks)")

        # 8. Best/worst sport
        by_sport = conditional.get("by_sport", {})
        sports_with_data = {k: v for k, v in by_sport.items() if v.get("n", 0) >= N}
        if len(sports_with_data) >= 2:
            best = max(sports_with_data.items(), key=lambda x: x[1]["hit_rate"])
            worst = min(sports_with_data.items(), key=lambda x: x[1]["hit_rate"])
            if best[1]["hit_rate"] >= 55:
                insights.append(f"Best sport: {best[0]} at {best[1]['hit_rate']}% ({best[1]['n']} picks)")
            if worst[1]["hit_rate"] <= 48:
                insights.append(f"Weakest sport: {worst[0]} at {worst[1]['hit_rate']}% ({worst[1]['n']} picks)")

        return insights

    # ── Feedback summary ───────────────────────────────────────────

    @staticmethod
    def get_summary_for_feedback(result: dict) -> dict:
        """Compact subset for storing in calibration_feedback.metric_data."""
        cal = result.get("calibration", {})
        cond = result.get("conditional", {})
        clv = result.get("clv", {})
        return {
            "edge_calibration": cal.get("by_edge_bucket", {}),
            "omi_vs_book": cal.get("omi_vs_book", {}),
            "avg_fair_line_error_spread": (cal.get("avg_fair_line_error") or {}).get("spread"),
            "avg_book_line_error_spread": (cal.get("avg_book_line_error") or {}).get("spread"),
            "conditional_by_pillar": cond.get("by_dominant_pillar", {}),
            "conditional_by_spread_size": cond.get("by_spread_size", {}),
            "clv_summary": clv.get("overall", {}),
            "insights": result.get("insights", [])[:10],
        }

    # ── Exchange vs sportsbook accuracy ──────────────────────────

    def analyze_exchange_accuracy(self, sport: Optional[str] = None, days: int = 30) -> dict:
        """Compare exchange implied probabilities vs book implied probs vs actual outcomes.

        Reads from exchange_accuracy_log (populated by grading pipeline).
        Returns breakdown by sport, market, and exchange.
        """
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        try:
            query = self.client.table("exchange_accuracy_log").select(
                "game_id, sport_key, market_type, exchange, book_name, "
                "exchange_implied_prob, book_implied_prob, omi_fair_prob, "
                "actual_value, exchange_error, book_error, exchange_closer, created_at"
            ).gte("created_at", cutoff).limit(5000)

            if sport:
                variants = [k for k, v in SPORT_DISPLAY.items() if v == sport]
                if not variants:
                    variants = [sport]
                query = query.in_("sport_key", variants)

            result = query.execute()
            rows = result.data or []
        except Exception as e:
            logger.error(f"[ExchangeAccuracy] Fetch failed: {e}")
            return {"error": str(e), "sample_size": 0}

        if not rows:
            return {"error": "No exchange accuracy data found", "sample_size": 0}

        # Normalize sport keys
        for r in rows:
            r["sport_key"] = _normalize_sport(r.get("sport_key", ""))

        # Overall stats
        total = len(rows)
        exchange_closer_count = sum(1 for r in rows if r.get("exchange_closer") is True)
        book_closer_count = sum(1 for r in rows if r.get("exchange_closer") is False)

        exchange_errors = [r["exchange_error"] for r in rows if r.get("exchange_error") is not None]
        book_errors = [r["book_error"] for r in rows if r.get("book_error") is not None]

        overall = {
            "total": total,
            "exchange_closer": exchange_closer_count,
            "book_closer": book_closer_count,
            "exchange_closer_pct": round(exchange_closer_count / total * 100, 1) if total > 0 else None,
            "avg_exchange_error": round(sum(exchange_errors) / len(exchange_errors), 4) if exchange_errors else None,
            "avg_book_error": round(sum(book_errors) / len(book_errors), 4) if book_errors else None,
        }

        # By exchange
        by_exchange = self._group_exchange_accuracy(rows, "exchange")

        # By sport
        by_sport = self._group_exchange_accuracy(rows, "sport_key")

        # By market type
        by_market = self._group_exchange_accuracy(rows, "market_type")

        # By book
        by_book = self._group_exchange_accuracy(rows, "book_name")

        # Insights
        insights = []
        if overall["exchange_closer_pct"] is not None:
            pct = overall["exchange_closer_pct"]
            if pct >= 55:
                insights.append(f"Exchanges closer to actual result {pct}% of the time — consider increasing exchange weight")
            elif pct <= 45:
                insights.append(f"Sportsbooks closer to actual result {round(100 - pct, 1)}% of the time — books more accurate")
            else:
                insights.append(f"Exchanges and books roughly equal accuracy ({pct}% exchange closer)")

        # Per-exchange insights
        for ex, data in by_exchange.items():
            if data["total"] >= 20 and data.get("exchange_closer_pct") is not None:
                pct = data["exchange_closer_pct"]
                if pct >= 55:
                    insights.append(f"{ex.title()} closer than books {pct}% ({data['total']} games)")
                elif pct <= 45:
                    insights.append(f"{ex.title()} less accurate than books ({pct}% closer, {data['total']} games)")

        return {
            "overall": overall,
            "by_exchange": by_exchange,
            "by_sport": by_sport,
            "by_market": by_market,
            "by_book": by_book,
            "insights": insights,
            "metadata": {
                "sport": sport or "all",
                "days": days,
                "sample_size": total,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    def _group_exchange_accuracy(self, rows: list, field: str) -> dict:
        """Group exchange accuracy rows by a field and compute stats."""
        groups: Dict[str, List] = {}
        for r in rows:
            key = str(r.get(field, "unknown"))
            if key not in groups:
                groups[key] = []
            groups[key].append(r)

        result = {}
        for key, group_rows in groups.items():
            total = len(group_rows)
            ex_closer = sum(1 for r in group_rows if r.get("exchange_closer") is True)
            bk_closer = sum(1 for r in group_rows if r.get("exchange_closer") is False)
            ex_errs = [r["exchange_error"] for r in group_rows if r.get("exchange_error") is not None]
            bk_errs = [r["book_error"] for r in group_rows if r.get("book_error") is not None]

            result[key] = {
                "total": total,
                "exchange_closer": ex_closer,
                "book_closer": bk_closer,
                "exchange_closer_pct": round(ex_closer / total * 100, 1) if total > 0 else None,
                "avg_exchange_error": round(sum(ex_errs) / len(ex_errs), 4) if ex_errs else None,
                "avg_book_error": round(sum(bk_errs) / len(bk_errs), 4) if bk_errs else None,
            }
        return result

    # ── Main entry point ───────────────────────────────────────────

    def analyze(self, sport: Optional[str] = None, days: int = 30) -> dict:
        """Run full edge analytics. Returns calibration, conditional, CLV, insights."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        logger.info(f"[EdgeAnalytics] Starting analysis: sport={sport or 'all'}, days={days}")

        # Fetch data
        grades = self._fetch_grades(sport, cutoff)
        if not grades:
            return {"error": "No graded predictions found", "sample_size": 0}

        game_ids = list({g["game_id"] for g in grades})
        game_map = self._fetch_game_results(game_ids)
        closing_map = self._fetch_closing_lines(game_ids)

        logger.info(
            f"[EdgeAnalytics] Data: {len(grades)} grades, {len(game_map)} games, "
            f"{len(closing_map)} closing lines"
        )

        # Per-result attribution
        attributed = self._per_result_attribution(grades, game_map, closing_map)

        if not attributed:
            return {
                "error": "No attributable predictions (all stale or missing game data)",
                "sample_size": len(grades),
            }

        # Analytics
        calibration = self._calibration_analysis(attributed)
        conditional = self._conditional_analysis(attributed)
        clv = self._clv_analysis(attributed)
        insights = self._generate_insights(calibration, conditional, clv, attributed)

        logger.info(f"[EdgeAnalytics] Complete: {len(attributed)} attributed, {len(insights)} insights")

        # Per-result summary (capped at 50 for API response size)
        per_result_summary = [
            {
                "game_id": r["game_id"],
                "sport_key": r["sport_key"],
                "market_type": r["market_type"],
                "edge_pct": r["edge_pct"],
                "is_correct": r["is_correct"],
                "omi_beat_book": r.get("omi_beat_book"),
                "dominant_pillar": r.get("dominant_pillar"),
                "dominant_pillar_correct": r.get("dominant_pillar_correct"),
                "fair_line_error": r.get("fair_line_error"),
                "book_line_error": r.get("book_line_error"),
                "clv": r.get("clv"),
                "signal": r.get("signal"),
                "edge_bucket": r.get("edge_bucket"),
            }
            for r in attributed[:50]
        ]

        return {
            "calibration": calibration,
            "conditional": conditional,
            "clv": clv,
            "insights": insights,
            "per_result_summary": per_result_summary,
            "metadata": {
                "sport": sport or "all",
                "days": days,
                "total_grades": len(grades),
                "attributed_count": len(attributed),
                "game_count": len(game_map),
                "closing_lines_count": len(closing_map),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        }
