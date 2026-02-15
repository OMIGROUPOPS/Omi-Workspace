"""
Composite History Tracker

Recalculates pillar composites and fair lines for all active games.
Called every 15 minutes by Vercel cron (via POST /api/recalculate-composites)
after odds sync writes fresh data to cached_odds and line_snapshots.

Writes time-series rows to composite_history table for tracking
how OMI's fair pricing evolves over time.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging
import statistics
import traceback

from database import db
from engine.analyzer import analyze_game, implied_prob_to_american

logger = logging.getLogger(__name__)

# Fair line constants — mirror edgescout.ts (lines 59-72)
FAIR_LINE_SPREAD_FACTOR = 0.15
FAIR_LINE_TOTAL_FACTOR = 0.20

# Caps — prevent extreme fair line deviations from consensus
FAIR_SPREAD_CAP = 4.0   # max ±4 points from book consensus
FAIR_TOTAL_CAP = 5.0    # max ±5 points from book consensus

SPREAD_TO_PROB_RATE = {
    "basketball_nba": 0.033,
    "basketball_ncaab": 0.030,
    "americanfootball_nfl": 0.027,
    "americanfootball_ncaaf": 0.025,
    "icehockey_nhl": 0.08,
    "baseball_mlb": 0.09,
    "soccer_epl": 0.20,
}

FAIR_LINE_ML_FACTOR = 0.01  # 1% implied probability shift per composite point

# Sport key normalization (for bias correction lookup)
SPORT_DISPLAY = {
    "basketball_nba": "NBA", "basketball_ncaab": "NCAAB",
    "americanfootball_nfl": "NFL", "americanfootball_ncaaf": "NCAAF",
    "icehockey_nhl": "NHL", "soccer_epl": "EPL",
}


def _get_bias_correction(sport_key: str) -> dict:
    """Read latest total/spread bias from calibration_feedback for a sport.

    Returns {total_bias, spread_bias, total_sample, spread_sample} or empty dict.
    Requires sample_size >= 50 to activate corrections.
    """
    try:
        if not db._is_connected():
            return {}
        sport_upper = SPORT_DISPLAY.get(sport_key, sport_key.upper())

        result = db.client.table("calibration_feedback").select(
            "metric_data, sample_size"
        ).eq("sport_key", sport_upper).not_.is_(
            "metric_data", "null"
        ).order("analysis_date", desc=True).limit(1).execute()

        if result.data:
            row = result.data[0]
            sample = row.get("sample_size", 0)
            if sample < 50:
                return {}
            metric_data = row.get("metric_data") or {}
            return {
                "total_bias": metric_data.get("total_bias"),
                "spread_bias": metric_data.get("spread_bias"),
                "total_sample": metric_data.get("total_sample", 0),
                "spread_sample": metric_data.get("spread_sample", 0),
            }
    except Exception as e:
        logger.debug(f"[CompositeTracker] bias correction lookup failed: {e}")
    return {}


# Exchange divergence boost constants
EXCHANGE_DIVERGENCE_THRESHOLD = 0.03  # 3% minimum divergence to trigger boost
EXCHANGE_DIVERGENCE_SCALE = 0.30      # Convert divergence to spread points (dampened)
EXCHANGE_DIVERGENCE_CAP = 2.0         # Max ±2 points adjustment


def _get_scale_factor(sport_key: str = "_global") -> float:
    """Read spread_factor from calibration_config table, fallback to module constant."""
    try:
        if not db._is_connected():
            return FAIR_LINE_SPREAD_FACTOR
        result = db.client.table("calibration_config").select("config_data").eq(
            "config_type", "scale_factors"
        ).eq("active", True).limit(1).execute()
        rows = result.data or []
        if rows:
            data = rows[0].get("config_data", {})
            return float(data.get("spread_factor", FAIR_LINE_SPREAD_FACTOR))
    except Exception as e:
        logger.debug(f"[CompositeTracker] calibration_config read failed: {e}")
    return FAIR_LINE_SPREAD_FACTOR


def _calc_exchange_divergence_boost(game_id: str, book_spread: float) -> float:
    """
    Calculate spread adjustment from exchange vs book divergence.

    Approach:
    - Get moneyline contracts from exchange_data for this game
    - Average yes_price/100 = exchange implied prob for home win
    - Derive book implied prob from spread: 0.50 + (book_spread * direction * 0.03)
    - divergence = exchange_prob - book_implied
    - Convert to spread points, cap at ±2

    Returns 0.0 on any error (zero-regression).
    """
    try:
        from exchange_tracker import ExchangeTracker
        if not game_id:
            return 0.0
        tracker = ExchangeTracker()
        contracts = tracker.get_game_exchange_data(game_id)
        if not contracts:
            return 0.0

        # Filter to moneyline contracts only
        ml_contracts = [
            c for c in contracts
            if c.get("market_type") == "moneyline"
            and c.get("yes_price") is not None
            and c["yes_price"] > 0
        ]
        if not ml_contracts:
            return 0.0

        # Find home team's contract via subtitle matching (NOT averaging all)
        home_team = ""
        try:
            cached = db.client.table("cached_odds").select("game_data").eq(
                "game_id", game_id
            ).limit(1).execute()
            if cached.data:
                home_team = (cached.data[0].get("game_data") or {}).get("home_team", "")
        except Exception:
            pass

        exchange_prob = None
        if home_team:
            home_lower = home_team.lower()
            home_words = [w for w in home_lower.split() if len(w) > 3]
            for c in ml_contracts:
                sub = (c.get("subtitle") or "").lower()
                if any(w in sub for w in home_words):
                    exchange_prob = c["yes_price"] / 100.0
                    break
        if exchange_prob is None:
            # Fallback: highest yes_price (favorite, better than averaging to 50)
            best = max(ml_contracts, key=lambda c: c["yes_price"])
            exchange_prob = best["yes_price"] / 100.0

        # Book implied prob from spread: home favored = negative spread
        # P(home) = 0.50 + (-book_spread * 0.03)
        book_implied = 0.50 + (-book_spread) * 0.03

        divergence = exchange_prob - book_implied

        if abs(divergence) < EXCHANGE_DIVERGENCE_THRESHOLD:
            return 0.0

        # Convert to spread points: divergence * (1/0.03) * dampening, cap at ±2
        boost = divergence * (1 / 0.03) * EXCHANGE_DIVERGENCE_SCALE
        boost = max(-EXCHANGE_DIVERGENCE_CAP, min(EXCHANGE_DIVERGENCE_CAP, boost))

        logger.info(
            f"[CompositeTracker] Exchange divergence boost for {game_id}: "
            f"exchange_prob={exchange_prob:.3f} book_implied={book_implied:.3f} "
            f"divergence={divergence:.3f} boost={boost:.2f}pts"
        )
        return boost

    except Exception as e:
        logger.debug(f"[CompositeTracker] Exchange divergence calc failed for {game_id}: {e}")
        return 0.0


def _round_to_half(value: float) -> float:
    """Round to nearest 0.5 — matches Math.round(x * 2) / 2 in edgescout.ts."""
    return round(value * 2) / 2


# Movement thresholds for triggering recalculation
SPREAD_MOVEMENT_THRESHOLD = 0.5   # points
TOTAL_MOVEMENT_THRESHOLD = 1.0    # points
STALE_RECALC_HOURS = 2            # force recalc if last composite older than this


def _should_recalculate(
    game_id: str,
    current_book_spread,
    current_book_total,
    previous: dict | None,
    now_dt: datetime,
) -> tuple:
    """
    Determine if a game needs composite recalculation based on line movement.
    Returns (should_recalc: bool, reason: str).
    """
    if previous is None:
        return True, "first_time"

    # Staleness guard
    try:
        prev_ts_str = previous.get("timestamp", "")
        prev_ts = datetime.fromisoformat(str(prev_ts_str).replace("Z", "+00:00"))
        age_hours = (now_dt - prev_ts).total_seconds() / 3600
        if age_hours >= STALE_RECALC_HOURS:
            return True, f"stale_{age_hours:.1f}h"
    except (ValueError, AttributeError, TypeError):
        return True, "unparseable_timestamp"

    # Spread movement check
    prev_spread = previous.get("book_spread")
    if current_book_spread is not None and prev_spread is not None:
        try:
            spread_delta = abs(float(current_book_spread) - float(prev_spread))
            if spread_delta >= SPREAD_MOVEMENT_THRESHOLD:
                return True, f"spread_moved_{prev_spread}->{current_book_spread}"
        except (ValueError, TypeError):
            pass

    # Total movement check
    prev_total = previous.get("book_total")
    if current_book_total is not None and prev_total is not None:
        try:
            total_delta = abs(float(current_book_total) - float(prev_total))
            if total_delta >= TOTAL_MOVEMENT_THRESHOLD:
                return True, f"total_moved_{prev_total}->{current_book_total}"
        except (ValueError, TypeError):
            pass

    return False, "no_movement"


def _calculate_fair_spread(book_spread: float, composite_spread: float) -> float:
    """
    Mirror edgescout.ts calculateFairSpread (lines 80-91).
    composite_spread is on 0-1 scale from analyzer.
    """
    deviation = composite_spread * 100 - 50
    adjustment = deviation * FAIR_LINE_SPREAD_FACTOR
    return _round_to_half(book_spread - adjustment)


def _calculate_fair_total(book_total: float, game_env_score: float) -> float:
    """
    Mirror edgescout.ts calculateFairTotal (lines 98-109).
    game_env_score is the game_environment PILLAR score (0-1), not totals composite.
    """
    deviation = game_env_score * 100 - 50
    adjustment = deviation * FAIR_LINE_TOTAL_FACTOR
    return _round_to_half(book_total + adjustment)


def _calculate_fair_ml(fair_spread: float, sport_key: str) -> tuple[int, int]:
    """
    Derive fair ML from fair spread — mirrors edgescout.ts spreadToMoneyline (lines 136-149).
    Returns (fair_ml_home, fair_ml_away).
    """
    rate = SPREAD_TO_PROB_RATE.get(sport_key, 0.03)
    home_prob = max(0.05, min(0.95, 0.50 + (-fair_spread) * rate))
    away_prob = 1 - home_prob
    return (implied_prob_to_american(home_prob), implied_prob_to_american(away_prob))


def _calculate_fair_ml_from_book(
    book_ml_home: int, book_ml_away: int, composite_ml: float
) -> tuple[int, int]:
    """
    Book-anchored fair ML: adjust consensus book ML by composite deviation.
    Mirrors edgescout.ts calculateFairMLFromBook.
    composite_ml is on 0-1 scale from analyzer.
    """
    # Remove vig from book odds
    home_implied = abs(book_ml_home) / (abs(book_ml_home) + 100) if book_ml_home < 0 else 100 / (book_ml_home + 100)
    away_implied = abs(book_ml_away) / (abs(book_ml_away) + 100) if book_ml_away < 0 else 100 / (book_ml_away + 100)
    total = home_implied + away_implied
    fair_home = home_implied / total
    # Shift by composite deviation
    deviation = composite_ml * 100 - 50
    shift = deviation * FAIR_LINE_ML_FACTOR
    adjusted_home = max(0.05, min(0.95, fair_home + shift))
    adjusted_away = 1 - adjusted_home
    return (implied_prob_to_american(adjusted_home), implied_prob_to_american(adjusted_away))


def _calculate_fair_ml_from_book_3way(
    book_ml_home: int, book_ml_draw: int, book_ml_away: int, composite_ml: float
) -> tuple[int, int, int]:
    """
    3-way fair ML for soccer. Mirrors edgescout.ts calculateFairMLFromBook3Way.
    Returns (fair_ml_home, fair_ml_draw, fair_ml_away).
    """
    def to_implied(odds: int) -> float:
        return abs(odds) / (abs(odds) + 100) if odds < 0 else 100 / (odds + 100)

    home_imp = to_implied(book_ml_home)
    draw_imp = to_implied(book_ml_draw)
    away_imp = to_implied(book_ml_away)
    total = home_imp + draw_imp + away_imp
    fair_home = home_imp / total
    fair_draw = draw_imp / total
    fair_away = away_imp / total

    deviation = composite_ml * 100 - 50
    shift = deviation * FAIR_LINE_ML_FACTOR
    adj_home = fair_home + shift
    adj_away = fair_away - shift
    adj_draw = 1 - adj_home - adj_away

    adj_home = max(0.02, adj_home)
    adj_away = max(0.02, adj_away)
    adj_draw = max(0.02, adj_draw)
    s = adj_home + adj_away + adj_draw
    adj_home /= s
    adj_away /= s
    adj_draw /= s

    return (
        implied_prob_to_american(adj_home),
        implied_prob_to_american(adj_draw),
        implied_prob_to_american(adj_away),
    )


def _extract_median_lines(game_data: dict) -> dict:
    """
    Extract median book lines from game_data bookmakers (Odds API format).
    Returns {book_spread, book_total, book_ml_home, book_ml_away, book_ml_draw}.
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


class CompositeTracker:
    """Recalculates composites + fair lines for all active games."""

    def _fetch_latest_composites(self, game_ids: list) -> dict:
        """
        Batch-fetch the most recent composite_history row per game_id.
        Returns {game_id: {book_spread, book_total, timestamp}}.
        Single query + Python dedup avoids N per-game queries.
        """
        if not game_ids:
            return {}
        try:
            all_rows = []
            chunk_size = 200
            for i in range(0, len(game_ids), chunk_size):
                chunk = game_ids[i:i + chunk_size]
                result = db.client.table("composite_history").select(
                    "game_id, book_spread, book_total, timestamp"
                ).in_("game_id", chunk).order(
                    "timestamp", desc=True
                ).execute()
                all_rows.extend(result.data or [])

            # Dedup: keep only the first (newest) row per game_id
            latest = {}
            for row in all_rows:
                gid = row["game_id"]
                if gid not in latest:
                    latest[gid] = row
            return latest
        except Exception as e:
            logger.error(f"[DynamicRecalc] Failed to batch-fetch latest composites: {e}")
            return {}

    def recalculate_all(self) -> dict:
        """
        Main entry point. For every active (not yet started) game in cached_odds:
        1. Run analyze_game for fresh pillar scores
        2. Extract per-market composites
        3. Calculate fair lines (same formulas as edgescout.ts)
        4. Write row to composite_history
        """
        if not db._is_connected():
            return {"error": "Database not connected", "games_processed": 0, "errors": 0}

        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()

        try:
            # Fetch ALL games from cached_odds (no server-side JSONB filter).
            # The cleanup job keeps this table lean (~active games only).
            # We filter by commence_time in Python with proper datetime parsing
            # to avoid text comparison issues (Z vs +00:00 suffixes).
            result = db.client.table("cached_odds").select(
                "sport_key, game_id, game_data"
            ).limit(5000).execute()
        except Exception as e:
            logger.error(f"[CompositeTracker] Failed to query cached_odds: {e}")
            return {"error": str(e), "games_processed": 0, "errors": 1}

        all_rows = result.data or []

        # Filter to future games in Python (proper datetime comparison)
        rows = []
        skipped_past = 0
        for row in all_rows:
            gd = row.get("game_data") or {}
            ct = gd.get("commence_time")
            if not ct:
                continue
            try:
                game_dt = datetime.fromisoformat(ct.replace("Z", "+00:00"))
                if game_dt >= now_dt:
                    rows.append(row)
                else:
                    skipped_past += 1
            except (ValueError, AttributeError):
                # Can't parse commence_time — include it anyway to avoid silent drops
                rows.append(row)

        # Log per-sport breakdown
        sport_counts: dict[str, int] = {}
        for row in rows:
            sk = row.get("sport_key", "unknown")
            sport_counts[sk] = sport_counts.get(sk, 0) + 1
        logger.info(
            f"[CompositeTracker] Found {len(rows)} active games to recalculate "
            f"(skipped {skipped_past} past games from {len(all_rows)} total). "
            f"By sport: {sport_counts}"
        )

        # Bias correction cache — lazy-populated per sport to avoid redundant DB calls
        bias_cache: dict[str, dict] = {}

        games_processed = 0
        recalculated = 0
        skipped = 0
        errors = 0
        sport_processed: dict[str, int] = {}
        sport_errors: dict[str, int] = {}

        # Batch-fetch latest composite_history row per game (ONE query, not N)
        game_ids = [row["game_id"] for row in rows if row.get("game_data")]
        latest_composites = self._fetch_latest_composites(game_ids)
        logger.info(
            f"[DynamicRecalc] Loaded {len(latest_composites)} previous composites "
            f"for {len(game_ids)} games"
        )

        for row in rows:
            try:
                sport_key = row["sport_key"]
                game_id = row["game_id"]
                game_data = row["game_data"]

                if not game_data:
                    continue

                # 1. Median book lines FIRST (cheap, no pillar calc needed)
                book_lines = _extract_median_lines(game_data)
                book_spread = book_lines["book_spread"]
                book_total = book_lines["book_total"]
                book_ml_home = book_lines["book_ml_home"]
                book_ml_away = book_lines["book_ml_away"]
                book_ml_draw = book_lines["book_ml_draw"]

                # 2. Movement check — skip if lines haven't moved
                previous = latest_composites.get(game_id)
                should_recalc, reason = _should_recalculate(
                    game_id, book_spread, book_total, previous, now_dt
                )

                if not should_recalc:
                    skipped += 1
                    continue

                # 3. Log the trigger reason
                logger.info(f"[DynamicRecalc] {game_id}: {reason}")

                # 4. Fresh pillar analysis (EXPENSIVE — only when movement detected)
                analysis = analyze_game(game_data, sport_key)

                # 5. Per-market composites from pillars_by_market
                pbm = analysis.get("pillars_by_market", {})
                composite_spread = pbm.get("spread", {}).get("full", {}).get("composite")
                composite_total = pbm.get("totals", {}).get("full", {}).get("composite")
                composite_ml = pbm.get("moneyline", {}).get("full", {}).get("composite")

                # 6. Game environment pillar score (for fair total)
                game_env_score = analysis.get("pillar_scores", {}).get("game_environment", 0.5)

                is_soccer = "soccer" in sport_key

                # 7. Calculate fair lines
                fair_spread = None
                fair_total = None
                fair_ml_home = None
                fair_ml_away = None
                fair_ml_draw = None

                if book_spread is not None and composite_spread is not None:
                    fair_spread = _calculate_fair_spread(book_spread, composite_spread)
                    # Exchange divergence boost: shift fair spread toward exchange signal
                    exchange_adj = _calc_exchange_divergence_boost(game_id, book_spread)
                    if exchange_adj != 0.0:
                        fair_spread = _round_to_half(fair_spread + exchange_adj)
                    fair_ml_home, fair_ml_away = _calculate_fair_ml(fair_spread, sport_key)

                    # Soccer: also calculate 3-way ML (spread path only gives 2-way)
                    if is_soccer and book_ml_home is not None and book_ml_draw is not None and book_ml_away is not None:
                        comp = composite_ml if composite_ml is not None else 0.5
                        fair_ml_home, fair_ml_draw, fair_ml_away = _calculate_fair_ml_from_book_3way(
                            book_ml_home, book_ml_draw, book_ml_away, comp
                        )

                elif is_soccer and book_ml_home is not None and book_ml_draw is not None and book_ml_away is not None and composite_ml is not None:
                    # Soccer 3-way ML (no spread data)
                    fair_ml_home, fair_ml_draw, fair_ml_away = _calculate_fair_ml_from_book_3way(
                        book_ml_home, book_ml_draw, book_ml_away, composite_ml
                    )
                elif book_ml_home is not None and book_ml_away is not None and composite_ml is not None:
                    # No spread data — use book-anchored 2-way ML adjustment
                    fair_ml_home, fair_ml_away = _calculate_fair_ml_from_book(
                        book_ml_home, book_ml_away, composite_ml
                    )

                if book_total is not None:
                    fair_total = _calculate_fair_total(book_total, game_env_score)

                # 5b. Bias correction — apply 30% of measured systematic bias
                if sport_key not in bias_cache:
                    bias_cache[sport_key] = _get_bias_correction(sport_key)
                bias = bias_cache[sport_key]

                if fair_spread is not None and bias.get("spread_bias") is not None and bias.get("spread_sample", 0) >= 50:
                    correction = bias["spread_bias"] * 0.3
                    old_fs = fair_spread
                    fair_spread = _round_to_half(fair_spread - correction)
                    if games_processed < 3:  # Log first few only
                        logger.info(
                            f"[BiasCorr] {game_id}: spread_bias={bias['spread_bias']}, "
                            f"correction={correction:.2f}, fair_spread {old_fs}→{fair_spread}"
                        )

                if fair_total is not None and bias.get("total_bias") is not None and bias.get("total_sample", 0) >= 50:
                    correction = bias["total_bias"] * 0.3
                    old_ft = fair_total
                    fair_total = _round_to_half(fair_total - correction)
                    if games_processed < 3:  # Log first few only
                        logger.info(
                            f"[BiasCorr] {game_id}: total_bias={bias['total_bias']}, "
                            f"correction={correction:.2f}, fair_total {old_ft}→{fair_total}"
                        )

                # 5c. Cap fair lines — prevent extreme deviations from consensus
                if fair_spread is not None and book_spread is not None:
                    capped = max(book_spread - FAIR_SPREAD_CAP,
                                 min(book_spread + FAIR_SPREAD_CAP, fair_spread))
                    if capped != fair_spread:
                        logger.info(
                            f"[FairCap] {game_id}: spread capped {fair_spread}→{capped} "
                            f"(book={book_spread}, cap=±{FAIR_SPREAD_CAP})"
                        )
                        fair_spread = capped

                if fair_total is not None and book_total is not None:
                    capped = max(book_total - FAIR_TOTAL_CAP,
                                 min(book_total + FAIR_TOTAL_CAP, fair_total))
                    if capped != fair_total:
                        logger.info(
                            f"[FairCap] {game_id}: total capped {fair_total}→{capped} "
                            f"(book={book_total}, cap=±{FAIR_TOTAL_CAP})"
                        )
                        fair_total = capped

                # 6. Insert row
                row_data = {
                    "game_id": game_id,
                    "sport_key": sport_key,
                    "timestamp": now,
                    "composite_spread": composite_spread,
                    "composite_total": composite_total,
                    "composite_ml": composite_ml,
                    "fair_spread": fair_spread,
                    "fair_total": fair_total,
                    "fair_ml_home": fair_ml_home,
                    "fair_ml_away": fair_ml_away,
                    "book_spread": book_spread,
                    "book_total": book_total,
                    "book_ml_home": book_ml_home,
                    "book_ml_away": book_ml_away,
                }
                if fair_ml_draw is not None:
                    row_data["fair_ml_draw"] = fair_ml_draw
                db.client.table("composite_history").insert(row_data).execute()

                games_processed += 1
                recalculated += 1
                sport_processed[sport_key] = sport_processed.get(sport_key, 0) + 1

            except Exception as e:
                logger.error(
                    f"[CompositeTracker] Error processing {row.get('game_id', '?')} "
                    f"(sport={row.get('sport_key', '?')}): {e}\n"
                    f"{traceback.format_exc()}"
                )
                errors += 1
                sk = row.get("sport_key", "unknown")
                sport_errors[sk] = sport_errors.get(sk, 0) + 1

        logger.info(
            f"[DynamicRecalc] Recalculated {recalculated} games, "
            f"skipped {skipped} unchanged (errors={errors})"
        )

        summary = {
            "games_processed": games_processed,
            "recalculated": recalculated,
            "skipped_unchanged": skipped,
            "errors": errors,
            "timestamp": now,
            "by_sport": sport_processed,
            "errors_by_sport": sport_errors if sport_errors else None,
        }
        logger.info(f"[CompositeTracker] Done: {summary}")
        return summary
