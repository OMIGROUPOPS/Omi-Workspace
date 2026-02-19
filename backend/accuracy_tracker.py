"""
OMI Edge — Prediction Accuracy Reflection Pool

Measures how close OMI fair lines were to actual game results vs sportsbook lines.
Supplements W/L grading — answers "is the model getting smarter?" not just "is it profitable?"
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from supabase import create_client, Client

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

logger = logging.getLogger(__name__)

# Map mixed-format sport keys to short display form
SPORT_NORMALIZE = {
    "basketball_nba": "NBA", "BASKETBALL_NBA": "NBA", "NBA": "NBA",
    "americanfootball_nfl": "NFL", "AMERICANFOOTBALL_NFL": "NFL", "NFL": "NFL",
    "icehockey_nhl": "NHL", "ICEHOCKEY_NHL": "NHL", "NHL": "NHL",
    "americanfootball_ncaaf": "NCAAF", "AMERICANFOOTBALL_NCAAF": "NCAAF", "NCAAF": "NCAAF",
    "basketball_ncaab": "NCAAB", "BASKETBALL_NCAAB": "NCAAB", "NCAAB": "NCAAB",
    "soccer_epl": "EPL", "SOCCER_EPL": "EPL", "EPL": "EPL",
}


class AccuracyTracker:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Supabase credentials not configured")
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================

    def run_accuracy_reflection(self, lookback_hours: int = 48) -> dict:
        """Process completed games and log prediction accuracy."""
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).isoformat()

        # Get completed games with scores in the lookback window
        result = self.client.table("game_results").select("*").not_.is_(
            "home_score", "null"
        ).not_.is_(
            "away_score", "null"
        ).gte("graded_at", cutoff).execute()

        completed_games = result.data or []
        if not completed_games:
            return {"processed": 0, "skipped": 0, "errors": 0, "message": "No completed games in lookback window"}

        # Get already-processed game IDs (batch to avoid URL length limits)
        game_ids = [g["game_id"] for g in completed_games]
        already_done: set = set()
        BATCH = 100
        for i in range(0, len(game_ids), BATCH):
            batch = game_ids[i:i + BATCH]
            existing = self.client.table("prediction_accuracy_log").select(
                "game_id"
            ).in_("game_id", batch).execute()
            already_done.update(r["game_id"] for r in (existing.data or []))

        processed = 0
        skipped = 0
        errors = 0
        total_omi_spread_error = 0.0
        total_book_spread_error = 0.0
        total_omi_total_error = 0.0
        total_book_total_error = 0.0
        spread_count = 0
        total_count = 0

        for game in completed_games:
            game_id = game["game_id"]
            if game_id in already_done:
                skipped += 1
                continue

            try:
                row = self._process_game(game)
                if row:
                    self.client.table("prediction_accuracy_log").upsert(
                        row, on_conflict="game_id"
                    ).execute()
                    processed += 1

                    # Accumulate stats
                    if row.get("omi_spread_error") is not None:
                        total_omi_spread_error += row["omi_spread_error"]
                        spread_count += 1
                    if row.get("book_spread_error") is not None:
                        total_book_spread_error += row["book_spread_error"]
                    if row.get("omi_total_error") is not None:
                        total_omi_total_error += row["omi_total_error"]
                        total_count += 1
                    if row.get("book_total_error") is not None:
                        total_book_total_error += row["book_total_error"]
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"[AccuracyTracker] Error processing {game_id}: {e}")
                errors += 1

        summary = {
            "processed": processed,
            "skipped": skipped,
            "errors": errors,
        }
        if spread_count > 0:
            summary["avg_omi_spread_error"] = round(total_omi_spread_error / spread_count, 2)
            summary["avg_book_spread_error"] = round(total_book_spread_error / spread_count, 2)
        if total_count > 0:
            summary["avg_omi_total_error"] = round(total_omi_total_error / total_count, 2)
            summary["avg_book_total_error"] = round(total_book_total_error / total_count, 2)

        return summary

    # =========================================================================
    # PROCESS SINGLE GAME
    # =========================================================================

    def _process_game(self, game: dict) -> Optional[dict]:
        """Build an accuracy log row for a single completed game."""
        game_id = game["game_id"]
        sport_key = game.get("sport_key", "")
        home_score = game.get("home_score")
        away_score = game.get("away_score")

        if home_score is None or away_score is None:
            return None

        actual_margin = home_score - away_score
        actual_total = home_score + away_score

        # --- Get OMI's last fair lines from composite_history ---
        omi_fair_spread = None
        omi_fair_total = None
        book_spread = None
        book_total = None

        ch_result = self.client.table("composite_history").select(
            "fair_spread, fair_total, book_spread, book_total"
        ).eq("game_id", game_id).order(
            "timestamp", desc=True
        ).limit(1).execute()

        if ch_result.data:
            ch = ch_result.data[0]
            omi_fair_spread = _to_float(ch.get("fair_spread"))
            omi_fair_total = _to_float(ch.get("fair_total"))
            book_spread = _to_float(ch.get("book_spread"))
            book_total = _to_float(ch.get("book_total"))

        # --- Get Pinnacle closing lines (one row per game) ---
        pinnacle_spread = None
        pinnacle_total = None

        try:
            cl_result = self.client.table("closing_lines").select(
                "pinnacle_spread, pinnacle_total"
            ).eq("game_id", game_id).limit(1).execute()

            if cl_result.data:
                cl = cl_result.data[0]
                pinnacle_spread = _to_float(cl.get("pinnacle_spread"))
                pinnacle_total = _to_float(cl.get("pinnacle_total"))
        except Exception:
            pass  # closing_lines may be empty or columns may not exist yet

        # --- Get pillar scores from predictions table ---
        sport_short = SPORT_NORMALIZE.get(sport_key, sport_key)
        # Try both the raw key and normalized form
        pred_result = self.client.table("predictions").select(
            "pillar_execution, pillar_incentives, pillar_shocks, pillar_time_decay, "
            "pillar_flow, pillar_game_environment, composite_score, best_edge_pct, overall_confidence"
        ).eq("game_id", game_id).limit(1).execute()

        pillar_execution = None
        pillar_incentives = None
        pillar_shocks = None
        pillar_time_decay = None
        pillar_flow = None
        pillar_game_environment = None
        omi_composite_score = None
        edge_tier = None
        signal_tier = "NO EDGE"  # Default — overridden if edge data exists

        if pred_result.data:
            pred = pred_result.data[0]
            pillar_execution = _to_float(pred.get("pillar_execution"))
            pillar_incentives = _to_float(pred.get("pillar_incentives"))
            pillar_shocks = _to_float(pred.get("pillar_shocks"))
            pillar_time_decay = _to_float(pred.get("pillar_time_decay"))
            pillar_flow = _to_float(pred.get("pillar_flow"))
            pillar_game_environment = _to_float(pred.get("pillar_game_environment"))
            omi_composite_score = _to_float(pred.get("composite_score"))
            edge_tier = pred.get("overall_confidence")
            best_edge = _to_float(pred.get("best_edge_pct"))
            if best_edge is not None:
                signal_tier = _determine_signal(best_edge)

        # --- Fetch edge cap data from composite_history ---
        raw_edge_pct = None
        capped_edge_pct = None
        try:
            ch_result = self.client.table("composite_history").select(
                "raw_edge_pct, capped_edge_pct"
            ).eq("game_id", game_id).order("timestamp", desc=True).limit(1).execute()
            if ch_result.data:
                raw_edge_pct = ch_result.data[0].get("raw_edge_pct")
                capped_edge_pct = ch_result.data[0].get("capped_edge_pct")
        except Exception as e:
            logger.debug(f"[AccuracyTracker] edge cap lookup failed for {game_id}: {e}")

        # Compute edge on-the-fly from fair vs book lines if composite_history
        # doesn't have raw_edge_pct yet (rows written before migration)
        if raw_edge_pct is None and omi_fair_spread is not None:
            raw_edge_pct = _compute_edge_pct(
                omi_fair_spread, book_spread, omi_fair_total, book_total, sport_key
            )
            if raw_edge_pct is not None:
                capped_edge_pct = _cap_edge(raw_edge_pct)

        # Prefer composite_history raw_edge_pct for signal_tier (more accurate than
        # predictions.best_edge_pct which is capped lower by the old prediction pipeline)
        if raw_edge_pct is not None:
            signal_tier = _determine_signal(float(raw_edge_pct))

        # Guard: if we never had real edge data AND no fair spread was computed,
        # this game was never properly analyzed. Classify as UNGRADED to avoid
        # polluting NO EDGE metrics with garbage/stale fair lines.
        if omi_fair_spread is None and raw_edge_pct is None and (
            not pred_result.data or _to_float(pred_result.data[0].get("best_edge_pct")) is None
        ):
            signal_tier = "UNGRADED"

        # --- Calculate errors ---
        omi_spread_error = abs(omi_fair_spread - actual_margin) if omi_fair_spread is not None else None
        omi_total_error = abs(omi_fair_total - actual_total) if omi_fair_total is not None else None
        book_spread_error = abs(book_spread - actual_margin) if book_spread is not None else None
        book_total_error = abs(book_total - actual_total) if book_total is not None else None
        pinnacle_spread_error = abs(pinnacle_spread - actual_margin) if pinnacle_spread is not None else None
        pinnacle_total_error = abs(pinnacle_total - actual_total) if pinnacle_total is not None else None

        # --- Calculate accuracy edges (positive = OMI closer) ---
        omi_vs_book_spread_edge = None
        if book_spread_error is not None and omi_spread_error is not None:
            omi_vs_book_spread_edge = round(book_spread_error - omi_spread_error, 4)

        omi_vs_book_total_edge = None
        if book_total_error is not None and omi_total_error is not None:
            omi_vs_book_total_edge = round(book_total_error - omi_total_error, 4)

        omi_vs_pinnacle_spread_edge = None
        if pinnacle_spread_error is not None and omi_spread_error is not None:
            omi_vs_pinnacle_spread_edge = round(pinnacle_spread_error - omi_spread_error, 4)

        omi_vs_pinnacle_total_edge = None
        if pinnacle_total_error is not None and omi_total_error is not None:
            omi_vs_pinnacle_total_edge = round(pinnacle_total_error - omi_total_error, 4)

        # --- Build row ---
        row = {
            "game_id": game_id,
            "sport_key": sport_short,
            "home_team": game.get("home_team"),
            "away_team": game.get("away_team"),
            "commence_time": game.get("commence_time"),
            "omi_fair_spread": _round(omi_fair_spread),
            "omi_fair_total": _round(omi_fair_total),
            "omi_composite_score": _round(omi_composite_score),
            "book_spread": _round(book_spread),
            "book_total": _round(book_total),
            "pinnacle_spread": _round(pinnacle_spread),
            "pinnacle_total": _round(pinnacle_total),
            "home_score": home_score,
            "away_score": away_score,
            "actual_margin": actual_margin,
            "actual_total": actual_total,
            "omi_spread_error": _round(omi_spread_error),
            "omi_total_error": _round(omi_total_error),
            "book_spread_error": _round(book_spread_error),
            "book_total_error": _round(book_total_error),
            "pinnacle_spread_error": _round(pinnacle_spread_error),
            "pinnacle_total_error": _round(pinnacle_total_error),
            "omi_vs_book_spread_edge": _round(omi_vs_book_spread_edge),
            "omi_vs_book_total_edge": _round(omi_vs_book_total_edge),
            "omi_vs_pinnacle_spread_edge": _round(omi_vs_pinnacle_spread_edge),
            "omi_vs_pinnacle_total_edge": _round(omi_vs_pinnacle_total_edge),
            "pillar_execution": _round(pillar_execution),
            "pillar_incentives": _round(pillar_incentives),
            "pillar_shocks": _round(pillar_shocks),
            "pillar_time_decay": _round(pillar_time_decay),
            "pillar_flow": _round(pillar_flow),
            "pillar_game_environment": _round(pillar_game_environment),
            "edge_tier": edge_tier,
            "signal_tier": signal_tier,
            "raw_edge_pct": raw_edge_pct,
            "capped_edge_pct": capped_edge_pct,
        }

        return row

    # =========================================================================
    # DASHBOARD SUMMARY
    # =========================================================================

    def get_accuracy_summary(self, sport: str = None, days: int = 30) -> dict:
        """Return summary stats for the accuracy dashboard tab.
        Tries SQL RPC first (zero row transfer), falls back to Python."""
        # Try RPC first
        try:
            rpc_params = {"p_days": days}
            if sport:
                rpc_params["p_sport"] = sport.upper()
            rpc_result = self.client.rpc("get_accuracy_summary", rpc_params).execute()
            data = rpc_result.data
            if isinstance(data, list) and len(data) == 1:
                data = data[0]
            if isinstance(data, dict) and "get_accuracy_summary" in data:
                data = data["get_accuracy_summary"]
            if isinstance(data, dict) and ("overall" in data or "games" in data):
                logger.info(f"[AccuracySummary] RPC returned data")
                return data
        except Exception as e:
            logger.info(f"[AccuracySummary] RPC unavailable ({e}), falling back to Python")

        return self._get_accuracy_summary_python(sport, days)

    def _get_accuracy_summary_python(self, sport: str = None, days: int = 30) -> dict:
        """Python fallback for accuracy summary aggregation."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        query = self.client.table("prediction_accuracy_log").select("*").gte(
            "created_at", cutoff
        )
        if sport:
            query = query.eq("sport_key", sport.upper())

        result = query.order("created_at", desc=True).limit(5000).execute()
        rows = result.data or []

        if not rows:
            return {"games": 0, "message": "No accuracy data yet"}

        # --- Overall averages ---
        spread_errors = _collect(rows, "omi_spread_error")
        book_spread_errors = _collect(rows, "book_spread_error")
        pinnacle_spread_errors = _collect(rows, "pinnacle_spread_error")
        total_errors = _collect(rows, "omi_total_error")
        book_total_errors = _collect(rows, "book_total_error")
        pinnacle_total_errors = _collect(rows, "pinnacle_total_error")

        spread_edges = _collect(rows, "omi_vs_book_spread_edge")
        total_edges = _collect(rows, "omi_vs_book_total_edge")

        # Count games where OMI was closer vs book was closer (spread)
        omi_closer_spread = sum(1 for v in spread_edges if v > 0)
        book_closer_spread = sum(1 for v in spread_edges if v < 0)
        tied_spread = sum(1 for v in spread_edges if v == 0)

        omi_closer_total = sum(1 for r in rows if (r.get("omi_vs_book_total_edge") or 0) > 0)
        book_closer_total = sum(1 for r in rows if (r.get("omi_vs_book_total_edge") or 0) < 0)

        overall = {
            "games": len(rows),
            "avg_omi_spread_error": _avg(spread_errors),
            "avg_book_spread_error": _avg(book_spread_errors),
            "avg_pinnacle_spread_error": _avg(pinnacle_spread_errors),
            "avg_omi_total_error": _avg(total_errors),
            "avg_book_total_error": _avg(book_total_errors),
            "avg_pinnacle_total_error": _avg(pinnacle_total_errors),
            "avg_omi_spread_edge": _avg(spread_edges),
            "avg_omi_total_edge": _avg(total_edges),
            "omi_closer_spread": omi_closer_spread,
            "book_closer_spread": book_closer_spread,
            "tied_spread": tied_spread,
            "omi_closer_total": omi_closer_total,
            "book_closer_total": book_closer_total,
            "spread_games": len(spread_edges),
            "total_games": len(total_edges),
        }

        # --- Per-tier breakdown ---
        tiers: dict = {}
        for row in rows:
            tier = row.get("signal_tier") or row.get("edge_tier") or "UNKNOWN"
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(row)

        by_tier = {}
        for tier, tier_rows in tiers.items():
            t_spread_err = _collect(tier_rows, "omi_spread_error")
            t_book_spread_err = _collect(tier_rows, "book_spread_error")
            t_total_err = _collect(tier_rows, "omi_total_error")
            t_book_total_err = _collect(tier_rows, "book_total_error")
            t_spread_edge = _collect(tier_rows, "omi_vs_book_spread_edge")
            t_total_edge = _collect(tier_rows, "omi_vs_book_total_edge")

            by_tier[tier] = {
                "games": len(tier_rows),
                "avg_omi_spread_error": _avg(t_spread_err),
                "avg_book_spread_error": _avg(t_book_spread_err),
                "avg_spread_edge": _avg(t_spread_edge),
                "avg_omi_total_error": _avg(t_total_err),
                "avg_book_total_error": _avg(t_book_total_err),
                "avg_total_edge": _avg(t_total_edge),
            }

        # --- Pillar accuracy correlation ---
        PILLAR_FIELDS = [
            ("execution", "pillar_execution"),
            ("incentives", "pillar_incentives"),
            ("shocks", "pillar_shocks"),
            ("time_decay", "pillar_time_decay"),
            ("flow", "pillar_flow"),
            ("game_environment", "pillar_game_environment"),
        ]

        pillar_correlation = {}
        for pillar_name, field in PILLAR_FIELDS:
            active_errors = []
            neutral_errors = []
            for row in rows:
                pillar_val = _to_float(row.get(field))
                spread_err = _to_float(row.get("omi_spread_error"))
                if pillar_val is None or spread_err is None:
                    continue
                # Active = pillar deviates from neutral (0.5)
                if abs(pillar_val - 0.5) > 0.02:
                    active_errors.append(spread_err)
                else:
                    neutral_errors.append(spread_err)

            avg_active = _avg(active_errors)
            avg_neutral = _avg(neutral_errors)
            accuracy_lift = None
            if avg_active is not None and avg_neutral is not None:
                # Positive lift = active pillar produces LOWER error (better)
                accuracy_lift = round(avg_neutral - avg_active, 2)

            pillar_correlation[pillar_name] = {
                "active_games": len(active_errors),
                "neutral_games": len(neutral_errors),
                "avg_error_active": avg_active,
                "avg_error_neutral": avg_neutral,
                "accuracy_lift": accuracy_lift,
            }

        return {
            "overall": overall,
            "by_tier": by_tier,
            "pillar_correlation": pillar_correlation,
        }


# =============================================================================
# HELPERS
# =============================================================================

def _to_float(val) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _round(val, digits: int = 4) -> Optional[float]:
    if val is None:
        return None
    try:
        return round(float(val), digits)
    except (TypeError, ValueError):
        return None


def _collect(rows: list, field: str) -> list[float]:
    """Collect non-None float values from rows for a given field."""
    vals = []
    for r in rows:
        v = _to_float(r.get(field))
        if v is not None:
            vals.append(v)
    return vals


def _avg(vals: list[float]) -> Optional[float]:
    if not vals:
        return None
    return round(sum(vals) / len(vals), 2)


# Sport-specific probability rates (mirror composite_tracker.py)
_SPREAD_TO_PROB_RATE = {
    "basketball_nba": 0.033, "NBA": 0.033,
    "basketball_ncaab": 0.030, "NCAAB": 0.030,
    "americanfootball_nfl": 0.027, "NFL": 0.027,
    "americanfootball_ncaaf": 0.025, "NCAAF": 0.025,
    "icehockey_nhl": 0.08, "NHL": 0.08,
    "baseball_mlb": 0.09, "MLB": 0.09,
    "soccer_epl": 0.20, "EPL": 0.20,
}

_EDGE_CAP_THRESHOLD = 8.0
_EDGE_CAP_DECAY = 0.3


def _compute_edge_pct(fair_spread, book_spread, fair_total, book_total, sport_key):
    """Calculate max edge % across spread and total markets."""
    max_edge = 0.0
    rate = _SPREAD_TO_PROB_RATE.get(sport_key, 0.03)

    if fair_spread is not None and book_spread is not None:
        diff = abs(float(fair_spread) - float(book_spread))
        edge = diff * rate * 100
        max_edge = max(max_edge, edge)

    if fair_total is not None and book_total is not None:
        total_rate = rate * 0.6
        diff = abs(float(fair_total) - float(book_total))
        edge = diff * total_rate * 100
        max_edge = max(max_edge, edge)

    return round(max_edge, 2) if max_edge > 0 else 0.0


def _cap_edge(raw_edge):
    """Apply soft cap: above 8%, diminishing returns."""
    if raw_edge is None:
        return None
    if raw_edge <= _EDGE_CAP_THRESHOLD:
        return raw_edge
    return round(_EDGE_CAP_THRESHOLD + (raw_edge - _EDGE_CAP_THRESHOLD) * _EDGE_CAP_DECAY, 2)


def _determine_signal(edge_pct) -> str:
    """Classify edge % into a tier. Always returns a valid string, never None."""
    if edge_pct is None:
        return "NO EDGE"
    try:
        ae = abs(float(edge_pct))
    except (TypeError, ValueError):
        return "NO EDGE"
    if ae >= 8:
        return "MAX EDGE"
    if ae >= 5:
        return "HIGH EDGE"
    if ae >= 3:
        return "MID EDGE"
    if ae >= 1:
        return "LOW EDGE"
    return "NO EDGE"
