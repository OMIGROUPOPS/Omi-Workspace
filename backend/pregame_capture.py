"""
Pregame Capture Module

Captures OMI fair lines, edges, and pillar scores at regular intervals
before each game starts. Creates a time-series record for analyzing
how fair lines evolve and at what point they're most accurate.

Runs every 15 minutes via scheduler.
"""

import logging
import statistics
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from internal_grader import calc_edge_pct, determine_signal

logger = logging.getLogger(__name__)

SPORT_DISPLAY = {
    "basketball_nba": "NBA", "BASKETBALL_NBA": "NBA", "NBA": "NBA",
    "americanfootball_nfl": "NFL", "AMERICANFOOTBALL_NFL": "NFL", "NFL": "NFL",
    "icehockey_nhl": "NHL", "ICEHOCKEY_NHL": "NHL", "NHL": "NHL",
    "americanfootball_ncaaf": "NCAAF", "AMERICANFOOTBALL_NCAAF": "NCAAF", "NCAAF": "NCAAF",
    "basketball_ncaab": "NCAAB", "BASKETBALL_NCAAB": "NCAAB", "NCAAB": "NCAAB",
    "soccer_epl": "EPL", "SOCCER_EPL": "EPL", "EPL": "EPL",
}

# Dedup: skip if fair lines unchanged and < 30 min since last snapshot
DEDUP_MINUTES = 30

# Only capture games within 7 days
MAX_HOURS_AHEAD = 7 * 24

# Hours-to-game buckets for accuracy analysis
HOURS_BUCKETS = [
    ("0.5h", 0, 0.5),
    ("1h", 0.5, 1.5),
    ("3h", 1.5, 4.5),
    ("6h", 4.5, 9),
    ("12h", 9, 18),
    ("24h", 18, 36),
    ("48h+", 36, 9999),
]


def _normalize_sport(raw: str) -> str:
    return SPORT_DISPLAY.get(raw, raw.upper())


def _hours_bucket(hours: float) -> str:
    for label, lo, hi in HOURS_BUCKETS:
        if lo <= hours < hi:
            return label
    return "48h+"


def _extract_median_lines(game_data: dict) -> dict:
    """Extract median book lines from Odds API game_data (same as composite_tracker)."""
    home_team = game_data.get("home_team", "")
    bookmakers = game_data.get("bookmakers", [])

    spread_lines = []
    total_lines = []
    ml_home_odds = []

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
                    if o.get("name") == home_team and o.get("price") is not None:
                        ml_home_odds.append(o["price"])

    return {
        "book_spread": round(statistics.median(spread_lines), 1) if spread_lines else None,
        "book_total": round(statistics.median(total_lines), 1) if total_lines else None,
        "book_ml_home": round(statistics.median(ml_home_odds)) if ml_home_odds else None,
    }


class PregameCapture:
    def __init__(self):
        from database import db
        self.client = db.client

    def capture_all(self) -> dict:
        """Capture current fair lines + edges for all upcoming games."""
        now = datetime.now(timezone.utc)
        max_ahead = now + timedelta(hours=MAX_HOURS_AHEAD)

        # 1. Get all upcoming games from cached_odds
        try:
            result = self.client.table("cached_odds").select(
                "sport_key, game_id, game_data"
            ).limit(5000).execute()
        except Exception as e:
            logger.error(f"[PregameCapture] Failed to query cached_odds: {e}")
            return {"error": str(e)}

        # Filter to future games (within 7 days)
        upcoming = []
        for row in (result.data or []):
            gd = row.get("game_data") or {}
            ct = gd.get("commence_time")
            if not ct:
                continue
            try:
                game_dt = datetime.fromisoformat(ct.replace("Z", "+00:00"))
                if now < game_dt <= max_ahead:
                    upcoming.append((row, game_dt))
            except (ValueError, AttributeError):
                continue

        if not upcoming:
            logger.info("[PregameCapture] No upcoming games found")
            return {"captured": 0, "skipped_dedup": 0, "with_edges": 0}

        game_ids = [r[0]["game_id"] for r in upcoming]

        # 2. Get latest fair lines from composite_history
        fair_map = self._fetch_latest_fair_lines(game_ids)

        # 3. Get latest snapshots for dedup check
        last_snap_map = self._fetch_latest_snapshots(game_ids)

        # 4. Get pillar scores from predictions table
        pillar_map = self._fetch_pillar_scores(game_ids)

        # 5. Build and insert snapshots
        captured = 0
        skipped = 0
        with_edges = 0
        rows_to_insert = []

        for row, game_dt in upcoming:
            gid = row["game_id"]
            sport = row.get("sport_key", "")
            gd = row.get("game_data", {})

            # Book consensus
            book = _extract_median_lines(gd)
            book_spread = book.get("book_spread")
            book_total = book.get("book_total")
            book_ml_home = book.get("book_ml_home")

            # Fair lines from composite_history
            fair = fair_map.get(gid, {})
            fair_spread = fair.get("fair_spread")
            fair_total = fair.get("fair_total")
            fair_ml_home = fair.get("fair_ml_home")
            composite = fair.get("composite_spread")

            # Edges
            spread_edge = None
            total_edge = None
            spread_signal = None
            total_signal = None

            if fair_spread is not None and book_spread is not None:
                spread_edge = calc_edge_pct(float(fair_spread), float(book_spread), "spread", sport)
                spread_signal = determine_signal(spread_edge)
            if fair_total is not None and book_total is not None:
                total_edge = calc_edge_pct(float(fair_total), float(book_total), "total", sport)
                total_signal = determine_signal(total_edge)

            hours_to_game = round((game_dt - now).total_seconds() / 3600, 2)

            # Dedup check
            last = last_snap_map.get(gid)
            if last:
                last_fair_s = last.get("fair_spread")
                last_fair_t = last.get("fair_total")
                last_time = last.get("snapshot_time")
                lines_same = (last_fair_s == fair_spread and last_fair_t == fair_total)

                if lines_same and last_time:
                    try:
                        last_dt = datetime.fromisoformat(str(last_time).replace("Z", "+00:00"))
                        if (now - last_dt).total_seconds() < DEDUP_MINUTES * 60:
                            skipped += 1
                            continue
                    except (ValueError, AttributeError):
                        pass

            # Pillar scores
            pillars = pillar_map.get(gid, {})

            # Track edges
            max_edge = max(spread_edge or 0, total_edge or 0)
            if max_edge >= 1.0:
                with_edges += 1

            rows_to_insert.append({
                "game_id": gid,
                "sport_key": _normalize_sport(sport),
                "snapshot_time": now.isoformat(),
                "hours_to_game": hours_to_game,
                "fair_spread": fair_spread,
                "fair_total": fair_total,
                "fair_ml_home": fair_ml_home,
                "book_spread": book_spread,
                "book_total": book_total,
                "book_ml_home": book_ml_home,
                "spread_edge_pct": spread_edge,
                "total_edge_pct": total_edge,
                "composite": composite,
                "pillar_execution": pillars.get("pillar_execution"),
                "pillar_incentives": pillars.get("pillar_incentives"),
                "pillar_shocks": pillars.get("pillar_shocks"),
                "pillar_time_decay": pillars.get("pillar_time_decay"),
                "pillar_flow": pillars.get("pillar_flow"),
                "pillar_game_environment": pillars.get("pillar_game_environment"),
                "spread_signal": spread_signal,
                "total_signal": total_signal,
                "home_team": gd.get("home_team"),
                "away_team": gd.get("away_team"),
                "commence_time": gd.get("commence_time"),
            })

        # Batch insert
        if rows_to_insert:
            try:
                self.client.table("pregame_snapshots").insert(rows_to_insert).execute()
                captured = len(rows_to_insert)
            except Exception as e:
                logger.error(f"[PregameCapture] Insert failed: {e}")
                return {"error": str(e), "attempted": len(rows_to_insert)}

        logger.info(
            f"[PregameCapture] Captured {captured} snapshots, "
            f"skipped {skipped} dedup, {with_edges} with edges >= 1%"
        )
        return {"captured": captured, "skipped_dedup": skipped, "with_edges": with_edges}

    # ── Data fetching ──────────────────────────────────────────────

    def _fetch_latest_fair_lines(self, game_ids: list) -> dict:
        """Get latest composite_history row per game."""
        fair_map = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i:i + 50]
            try:
                result = self.client.table("composite_history").select(
                    "game_id, fair_spread, fair_total, fair_ml_home, "
                    "composite_spread, composite_total"
                ).in_("game_id", batch).order(
                    "timestamp", desc=True
                ).limit(len(batch) * 3).execute()

                # Dedup to latest per game_id
                for row in (result.data or []):
                    gid = row["game_id"]
                    if gid not in fair_map:
                        fair_map[gid] = row
            except Exception as e:
                logger.warning(f"[PregameCapture] Fetch composite_history batch failed: {e}")
        return fair_map

    def _fetch_latest_snapshots(self, game_ids: list) -> dict:
        """Get latest pregame_snapshot per game for dedup."""
        snap_map = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i:i + 50]
            try:
                result = self.client.table("pregame_snapshots").select(
                    "game_id, fair_spread, fair_total, snapshot_time"
                ).in_("game_id", batch).order(
                    "snapshot_time", desc=True
                ).limit(len(batch) * 2).execute()

                for row in (result.data or []):
                    gid = row["game_id"]
                    if gid not in snap_map:
                        snap_map[gid] = row
            except Exception as e:
                # Table may not exist yet on first run
                logger.debug(f"[PregameCapture] Fetch snapshots batch failed: {e}")
        return snap_map

    def _fetch_pillar_scores(self, game_ids: list) -> dict:
        """Get latest pillar scores from predictions table."""
        pillar_map = {}
        for i in range(0, len(game_ids), 50):
            batch = game_ids[i:i + 50]
            try:
                result = self.client.table("predictions").select(
                    "game_id, pillar_execution, pillar_incentives, pillar_shocks, "
                    "pillar_time_decay, pillar_flow"
                ).in_("game_id", batch).order(
                    "predicted_at", desc=True
                ).limit(len(batch) * 2).execute()

                for row in (result.data or []):
                    gid = row["game_id"]
                    if gid not in pillar_map:
                        pillar_map[gid] = row
            except Exception as e:
                logger.warning(f"[PregameCapture] Fetch predictions batch failed: {e}")
        return pillar_map

    # ── Post-game accuracy analysis ────────────────────────────────

    def analyze_pregame_accuracy(self, game_id: str) -> Optional[list]:
        """Compare each pregame snapshot's fair line to actual result."""
        try:
            # Get snapshots
            snap_result = self.client.table("pregame_snapshots").select("*").eq(
                "game_id", game_id
            ).order("snapshot_time").execute()
            snapshots = snap_result.data or []
            if not snapshots:
                return None

            # Get actual result
            gr_result = self.client.table("game_results").select(
                "home_score, away_score"
            ).eq("game_id", game_id).limit(1).execute()
            if not gr_result.data:
                return None

            gr = gr_result.data[0]
            home_score = gr.get("home_score")
            away_score = gr.get("away_score")
            if home_score is None or away_score is None:
                return None

            actual_spread = float(home_score) - float(away_score)
            actual_total = float(home_score) + float(away_score)

            analysis = []
            for snap in snapshots:
                hours = snap.get("hours_to_game")
                if hours is None:
                    continue

                entry = {
                    "hours_to_game": float(hours),
                    "hours_bucket": _hours_bucket(float(hours)),
                }

                fs = snap.get("fair_spread")
                bs = snap.get("book_spread")
                if fs is not None:
                    entry["fair_spread_error"] = round(abs(float(fs) - actual_spread), 2)
                if bs is not None:
                    entry["book_spread_error"] = round(abs(float(bs) - actual_spread), 2)
                if fs is not None and bs is not None:
                    entry["omi_beat_book_spread"] = entry["fair_spread_error"] < entry["book_spread_error"]

                ft = snap.get("fair_total")
                bt = snap.get("book_total")
                if ft is not None:
                    entry["fair_total_error"] = round(abs(float(ft) - actual_total), 2)
                if bt is not None:
                    entry["book_total_error"] = round(abs(float(bt) - actual_total), 2)
                if ft is not None and bt is not None:
                    entry["omi_beat_book_total"] = entry["fair_total_error"] < entry["book_total_error"]

                analysis.append(entry)

            return analysis
        except Exception as e:
            logger.warning(f"[PregameCapture] analyze_pregame_accuracy failed for {game_id}: {e}")
            return None

    def get_pregame_accuracy_summary(self, sport: Optional[str] = None, days: int = 30) -> dict:
        """Aggregate pregame accuracy across many games by hours_to_game bucket."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        try:
            # Get game_ids that have pregame snapshots AND are graded
            query = self.client.table("pregame_snapshots").select(
                "game_id"
            ).gte("commence_time", cutoff)
            if sport:
                variants = [k for k, v in SPORT_DISPLAY.items() if v == sport.upper()]
                if variants:
                    query = query.in_("sport_key", variants)
            result = query.limit(5000).execute()

            game_ids = list({r["game_id"] for r in (result.data or [])})
            if not game_ids:
                return {"buckets": {}, "sample_size": 0}

            # Check which games are graded
            graded_ids = []
            for i in range(0, len(game_ids), 50):
                batch = game_ids[i:i + 50]
                try:
                    gr = self.client.table("game_results").select(
                        "game_id"
                    ).in_("game_id", batch).not_.is_(
                        "home_score", "null"
                    ).execute()
                    graded_ids.extend([r["game_id"] for r in (gr.data or [])])
                except Exception:
                    pass

            if not graded_ids:
                return {"buckets": {}, "sample_size": 0}

            # Analyze each graded game
            bucket_data: Dict[str, Dict] = {}
            for gid in graded_ids[:200]:  # Cap at 200 games
                analysis = self.analyze_pregame_accuracy(gid)
                if not analysis:
                    continue
                for entry in analysis:
                    bucket = entry.get("hours_bucket")
                    if not bucket:
                        continue
                    if bucket not in bucket_data:
                        bucket_data[bucket] = {
                            "spread_errors": [], "total_errors": [],
                            "book_spread_errors": [], "book_total_errors": [],
                            "omi_beat_spread": 0, "omi_beat_total": 0,
                            "spread_n": 0, "total_n": 0,
                        }
                    bd = bucket_data[bucket]
                    if "fair_spread_error" in entry:
                        bd["spread_errors"].append(entry["fair_spread_error"])
                        bd["spread_n"] += 1
                    if "book_spread_error" in entry:
                        bd["book_spread_errors"].append(entry["book_spread_error"])
                    if entry.get("omi_beat_book_spread"):
                        bd["omi_beat_spread"] += 1
                    if "fair_total_error" in entry:
                        bd["total_errors"].append(entry["fair_total_error"])
                        bd["total_n"] += 1
                    if "book_total_error" in entry:
                        bd["book_total_errors"].append(entry["book_total_error"])
                    if entry.get("omi_beat_book_total"):
                        bd["omi_beat_total"] += 1

            # Aggregate
            buckets = {}
            for label, _, _ in HOURS_BUCKETS:
                bd = bucket_data.get(label)
                if not bd or (bd["spread_n"] == 0 and bd["total_n"] == 0):
                    continue
                buckets[label] = {
                    "avg_spread_error": round(sum(bd["spread_errors"]) / len(bd["spread_errors"]), 2) if bd["spread_errors"] else None,
                    "avg_total_error": round(sum(bd["total_errors"]) / len(bd["total_errors"]), 2) if bd["total_errors"] else None,
                    "avg_book_spread_error": round(sum(bd["book_spread_errors"]) / len(bd["book_spread_errors"]), 2) if bd["book_spread_errors"] else None,
                    "avg_book_total_error": round(sum(bd["book_total_errors"]) / len(bd["book_total_errors"]), 2) if bd["book_total_errors"] else None,
                    "omi_beat_book_spread_pct": round(bd["omi_beat_spread"] / bd["spread_n"] * 100, 1) if bd["spread_n"] > 0 else None,
                    "omi_beat_book_total_pct": round(bd["omi_beat_total"] / bd["total_n"] * 100, 1) if bd["total_n"] > 0 else None,
                    "spread_n": bd["spread_n"],
                    "total_n": bd["total_n"],
                }

            return {"buckets": buckets, "sample_size": len(graded_ids)}

        except Exception as e:
            logger.error(f"[PregameCapture] get_pregame_accuracy_summary failed: {e}")
            return {"error": str(e), "buckets": {}, "sample_size": 0}
