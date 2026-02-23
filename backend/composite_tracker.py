"""
Composite History Tracker

Recalculates pillar composites and fair lines for all active games.
Called every 15 minutes by the scheduler (composite_recalc job)
after odds sync writes fresh data to cached_odds and line_snapshots.

Writes time-series rows to composite_history table for tracking
how OMI's fair pricing evolves over time.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging
import math
import statistics
import traceback

from database import db
from engine.analyzer import analyze_game, implied_prob_to_american, fetch_line_context, fetch_team_environment_stats
from espn_scores import ESPNScoreFetcher, teams_match, ESPN_SPORTS

logger = logging.getLogger(__name__)

# Variable engine — lazy import to avoid circular deps
_variable_engine = None

def _get_variable_engine():
    global _variable_engine
    if _variable_engine is None:
        try:
            import variable_engine
            _variable_engine = variable_engine
        except Exception as e:
            logger.warning(f"[VarEngine] Failed to import variable_engine: {e}")
    return _variable_engine

# Fair line constants — mirror edgescout.ts (lines 59-72)
FAIR_LINE_SPREAD_FACTOR = 0.15
FAIR_LINE_TOTAL_FACTOR = 0.10

# Sport-specific caps — prevent extreme fair line deviations from consensus
# Tighter caps for low-scoring sports; wider for high-variance college games
SPREAD_CAP_BY_SPORT = {
    "basketball_ncaab": 4.0,
    "basketball_nba": 3.0,
    "americanfootball_nfl": 3.0,
    "americanfootball_ncaaf": 3.0,
    "icehockey_nhl": 1.5,
    "soccer_epl": 1.0,
}
TOTAL_CAP_BY_SPORT = {
    "basketball_ncaab": 6.0,
    "basketball_nba": 5.0,
    "americanfootball_nfl": 5.0,
    "americanfootball_ncaaf": 5.0,
    "icehockey_nhl": 1.0,
    "soccer_epl": 1.0,
}
DEFAULT_SPREAD_CAP = 3.0
DEFAULT_TOTAL_CAP = 4.0

SPREAD_TO_PROB_RATE = {
    "basketball_nba": 0.033,
    "basketball_ncaab": 0.030,
    "americanfootball_nfl": 0.027,
    "americanfootball_ncaaf": 0.025,
    "icehockey_nhl": 0.08,
    "baseball_mlb": 0.09,
    "soccer_epl": 0.20,
}

# Logistic k-values: k = linear_rate * 4  (derivative at x=0 matches linear rate)
SPREAD_TO_PROB_K = {
    "basketball_nba": 0.132,
    "basketball_ncaab": 0.120,
    "americanfootball_nfl": 0.108,
    "americanfootball_ncaaf": 0.108,
    "icehockey_nhl": 0.320,
    "baseball_mlb": 0.360,
    "soccer_epl": 0.800,
    "soccer_usa_mls": 0.800,
    "soccer_spain_la_liga": 0.800,
    "soccer_italy_serie_a": 0.800,
    "soccer_germany_bundesliga": 0.800,
    "soccer_france_ligue_one": 0.800,
    "soccer_uefa_champs_league": 0.800,
}


def spread_to_win_prob(spread: float, sport_key: str) -> float:
    """Logistic spread-to-probability: P(win) = 1 / (1 + exp(spread * k)).
    Negative spread = favorite → probability > 0.50."""
    k = SPREAD_TO_PROB_K.get(sport_key, 0.120)
    return 1.0 / (1.0 + math.exp(spread * k))

FAIR_LINE_ML_FACTOR = 0.01  # 1% implied probability shift per composite point

# Edge soft cap — extreme edges (8%+) are likely noise, apply diminishing returns
EDGE_CAP_THRESHOLD = 8.0    # Edge % above which we apply diminishing returns
EDGE_CAP_DECAY = 0.3        # Above threshold: capped = 8 + (raw - 8) * 0.3

# Flow gate — downgrade HIGH/MAX EDGE signals when Flow pillar is weak
FLOW_GATE_THRESHOLD = 0.55  # Flow score below this gates strong signals
FLOW_GATE_EDGE_MIN = 5.0    # Edge % threshold (HIGH EDGE = 5%+)

# Sport key normalization (for bias correction lookup)
SPORT_DISPLAY = {
    "basketball_nba": "NBA", "basketball_ncaab": "NCAAB",
    "americanfootball_nfl": "NFL", "americanfootball_ncaaf": "NCAAF",
    "icehockey_nhl": "NHL", "soccer_epl": "EPL",
}


# =============================================================================
# Time helpers — duplicated from server.py to avoid circular import
# =============================================================================

def _total_minutes_for_sport(sport: str) -> float:
    """Game duration in minutes for live CEQ calculation."""
    s = sport.upper()
    if s in ("NBA",):
        return 48.0
    if s in ("NCAAB",):
        return 40.0
    if s in ("NFL", "NCAAF"):
        return 60.0
    if s in ("NHL",):
        return 60.0
    if s in ("EPL",):
        return 90.0
    return 48.0


def _estimate_minutes_elapsed(period_str: str, clock: str, sport: str) -> float:
    """Estimate minutes elapsed from period string and clock display."""
    s = sport.upper()

    clock_mins = 0.0
    if clock:
        try:
            parts = clock.split(":")
            clock_mins = float(parts[0]) + float(parts[1]) / 60.0 if len(parts) == 2 else float(parts[0])
        except (ValueError, IndexError):
            clock_mins = 0.0

    if s in ("NBA",):
        q_map = {"Q1": 0, "Q2": 12, "Q3": 24, "Q4": 36}
        for qname, base in q_map.items():
            if qname in period_str:
                return base + (12.0 - clock_mins)
        if "OT" in period_str:
            return 48.0 + (5.0 - clock_mins)
        if "Half" in period_str:
            return 24.0
    elif s in ("NCAAB",):
        if "1st Half" in period_str:
            return 20.0 - clock_mins
        if "2nd Half" in period_str:
            return 20.0 + (20.0 - clock_mins)
        if "Half" in period_str:
            return 20.0
        if "OT" in period_str:
            return 40.0 + (5.0 - clock_mins)
    elif s in ("NFL", "NCAAF"):
        q_map = {"Q1": 0, "Q2": 15, "Q3": 30, "Q4": 45}
        for qname, base in q_map.items():
            if qname in period_str:
                return base + (15.0 - clock_mins)
        if "Half" in period_str:
            return 30.0
        if "OT" in period_str:
            return 60.0
    elif s in ("NHL",):
        p_map = {"P1": 0, "P2": 20, "P3": 40}
        for pname, base in p_map.items():
            if pname in period_str:
                return base + (20.0 - clock_mins)
        if "OT" in period_str:
            return 60.0
    elif s in ("EPL",):
        if "1st Half" in period_str:
            return 45.0 - clock_mins
        if "2nd Half" in period_str:
            return 45.0 + (45.0 - clock_mins)
        if "ET" in period_str:
            return 90.0

    return 0.0


# =============================================================================
# Live CEQ calculation
# =============================================================================

def _calculate_live_ceq(pregame_ceq: float, pregame_fair_spread: float,
                        score_diff: float, time_remaining_pct: float) -> tuple:
    """
    Calculate live CEQ and hold signal.

    pregame_ceq: 0-100 scale (composite_spread * 100)
    pregame_fair_spread: from pregame composite_history row
    score_diff: home_score - away_score
    time_remaining_pct: 1.0 at tipoff, 0.0 at final
    """
    score_vs_spread = score_diff - (-pregame_fair_spread)  # positive = outperforming
    time_weight = 1.0 - time_remaining_pct  # 0 at start, 1 at end
    confirmation_factor = score_vs_spread / max(abs(pregame_fair_spread), 1.0)
    confirmation_factor = max(-1.0, min(1.0, confirmation_factor))

    if confirmation_factor > 0:
        live_ceq = pregame_ceq + (confirmation_factor * time_weight * 15)
    else:
        live_ceq = pregame_ceq + (confirmation_factor * time_weight * 25)

    live_ceq = max(0, min(100, live_ceq))

    # Hold signal
    if live_ceq >= 65:
        hold_signal = "STRONG_HOLD"
    elif live_ceq >= 55:
        hold_signal = "HOLD"
    elif live_ceq >= 40:
        hold_signal = "UNWIND"
    else:
        hold_signal = "URGENT_UNWIND"

    return live_ceq, hold_signal


def _calculate_edge_pct(fair_spread, book_spread, fair_total, book_total, sport_key):
    """Calculate max edge % across spread and total markets.
    Uses logistic probability differences for both spread and total."""
    from edge_calc import calculate_max_edge
    return calculate_max_edge(fair_spread, book_spread, fair_total, book_total, sport_key)


def _cap_edge(raw_edge):
    """Apply soft cap: above 8%, diminishing returns."""
    if raw_edge <= EDGE_CAP_THRESHOLD:
        return raw_edge
    return round(EDGE_CAP_THRESHOLD + (raw_edge - EDGE_CAP_THRESHOLD) * EDGE_CAP_DECAY, 2)


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


def _calc_exchange_divergence_boost(game_id: str, book_spread: float, sport_key: str = "basketball_nba") -> float:
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

        # Book implied prob from spread (logistic)
        book_implied = spread_to_win_prob(book_spread, sport_key)

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
STALE_RECALC_HOURS = 0.5          # force recalc if last composite older than 30 min
CARRY_FORWARD_MINUTES = 0         # always carry forward — ensures every cycle writes a row


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
    Reason prefixed with "carry_forward_" means: skip expensive pillar analysis,
    just re-insert the previous fair lines with fresh timestamp.
    """
    if previous is None:
        return True, "first_time"

    # Parse previous timestamp
    age_minutes = 0
    try:
        prev_ts_str = previous.get("timestamp", "")
        prev_ts = datetime.fromisoformat(str(prev_ts_str).replace("Z", "+00:00"))
        age_minutes = (now_dt - prev_ts).total_seconds() / 60
        age_hours = age_minutes / 60
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

    # Carry-forward: no line movement but entry is older than CARRY_FORWARD_MINUTES
    # This writes a fresh timestamp with the same fair lines (cheap, no pillar analysis)
    if age_minutes >= CARRY_FORWARD_MINUTES:
        return True, f"carry_forward_{age_minutes:.0f}m"

    return False, "no_movement"


def _calculate_fair_spread(book_spread: float, composite_spread: float) -> float:
    """
    Mirror edgescout.ts calculateFairSpread (lines 80-91).
    composite_spread is on 0-1 scale from analyzer.

    Confidence scaling: composites near 0.50 produce near-zero adjustments.
    A composite of 0.60 adjusts modestly; 0.80 adjusts aggressively.
    This prevents low-confidence composites (0.30-0.37) from generating
    the largest fair line divergences.
    """
    deviation = composite_spread * 100 - 50
    confidence = max(0.40, abs(composite_spread - 0.50) * 2)  # floor 0.25 so moderate composites still adjust
    adjustment = deviation * FAIR_LINE_SPREAD_FACTOR * confidence
    return _round_to_half(book_spread - adjustment)


def _calculate_fair_total(book_total: float, composite_total: float) -> float:
    """
    Calculate fair total from the full totals-market composite (0-1 scale),
    not just the game_environment pillar. This mirrors the approach used by
    _calculate_fair_spread which takes the full spread composite.

    Same confidence scaling as _calculate_fair_spread — near-neutral
    composites produce near-zero total adjustments.
    """
    deviation = composite_total * 100 - 50
    confidence = max(0.40, abs(composite_total - 0.50) * 2)
    adjustment = deviation * FAIR_LINE_TOTAL_FACTOR * confidence
    return _round_to_half(book_total + adjustment)


def _calculate_fair_ml(fair_spread: float, sport_key: str) -> tuple[int, int]:
    """
    Derive fair ML from fair spread — mirrors edgescout.ts spreadToMoneyline.
    Uses logistic conversion to prevent probability overflow at extreme spreads.
    Returns (fair_ml_home, fair_ml_away).
    """
    home_prob = spread_to_win_prob(fair_spread, sport_key)
    home_prob = max(0.01, min(0.99, home_prob))
    away_prob = 1 - home_prob
    return (implied_prob_to_american(home_prob), implied_prob_to_american(away_prob))


def _calculate_fair_ml_from_book(
    book_spread: float, composite_spread: float, sport_key: str
) -> tuple[int, int]:
    """
    Derive fair ML from fair spread — ensures spread/ML coherence.
    Mirrors edgescout.ts calculateFairMLFromBook.
    Calculates fair spread internally, then converts to win probability.
    """
    fair_spread = _calculate_fair_spread(book_spread, composite_spread)
    return _calculate_fair_ml(fair_spread, sport_key)


def _calculate_fair_ml_composite_only(composite: float) -> tuple[int, int]:
    """
    Composite-only ML when no spread data available.
    Mirrors edgescout.ts calculateFairMoneyline. composite is 0-1 scale.
    """
    deviation = composite * 100 - 50
    confidence = max(0.40, abs(composite - 0.50) * 2)
    home_prob = max(0.05, min(0.95, 0.50 + deviation * FAIR_LINE_ML_FACTOR * confidence))
    away_prob = 1 - home_prob
    return (implied_prob_to_american(home_prob), implied_prob_to_american(away_prob))


def _calculate_fair_ml_from_book_3way(
    book_ml_home: int, book_ml_draw: int, book_ml_away: int,
    composite_ml: float, book_spread: float = None, sport_key: str = None
) -> tuple[int, int, int]:
    """
    3-way fair ML for soccer. Derives H/A from fair spread when available;
    uses book draw as baseline. Falls back to composite-only adjustment.
    Returns (fair_ml_home, fair_ml_draw, fair_ml_away).
    """
    def to_implied(odds: int) -> float:
        return abs(odds) / (abs(odds) + 100) if odds < 0 else 100 / (odds + 100)

    # Get vig-free draw probability as baseline
    home_imp = to_implied(book_ml_home)
    draw_imp = to_implied(book_ml_draw)
    away_imp = to_implied(book_ml_away)
    total_imp = home_imp + draw_imp + away_imp
    fair_draw = draw_imp / total_imp

    if book_spread is not None and sport_key:
        # Derive from fair spread for coherence (logistic conversion)
        fair_spread_val = _calculate_fair_spread(book_spread, composite_ml)
        two_way_home = spread_to_win_prob(fair_spread_val, sport_key)
        # Scale down H/A to make room for draw
        adj_home = two_way_home * (1 - fair_draw)
        adj_away = (1 - two_way_home) * (1 - fair_draw)
        adj_draw = fair_draw
    else:
        # Fallback: composite-only adjustment
        fair_home = home_imp / total_imp
        fair_away = away_imp / total_imp
        deviation = composite_ml * 100 - 50
        confidence = max(0.40, abs(composite_ml - 0.50) * 2)
        shift = deviation * FAIR_LINE_ML_FACTOR * confidence
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
    Extract Pinnacle-weighted consensus lines from game_data bookmakers.
    Pinnacle 50%, FD 25%, DK 25% when Pinnacle available.
    Falls back to simple median if Pinnacle not present.
    Returns {book_spread, book_total, book_ml_home, book_ml_away, book_ml_draw,
             pinnacle_spread, pinnacle_total}.
    """
    home_team = game_data.get("home_team", "")
    bookmakers = game_data.get("bookmakers", [])

    # Per-book tracking for weighted consensus
    pin_spread = None
    pin_total = None
    fd_spread = None
    fd_total = None
    dk_spread = None
    dk_total = None

    all_spread_lines = []
    all_total_lines = []
    ml_home_odds = []
    ml_away_odds = []
    ml_draw_odds = []

    for bk in bookmakers:
        bk_key = (bk.get("key") or "").lower()
        for market in bk.get("markets", []):
            key = market.get("key")
            outcomes = market.get("outcomes", [])

            if key == "spreads":
                for o in outcomes:
                    if o.get("name") == home_team and o.get("point") is not None:
                        val = o["point"]
                        all_spread_lines.append(val)
                        if bk_key == "pinnacle":
                            pin_spread = val
                        elif bk_key == "fanduel":
                            fd_spread = val
                        elif bk_key == "draftkings":
                            dk_spread = val

            elif key == "totals":
                for o in outcomes:
                    if o.get("name") == "Over" and o.get("point") is not None:
                        val = o["point"]
                        all_total_lines.append(val)
                        if bk_key == "pinnacle":
                            pin_total = val
                        elif bk_key == "fanduel":
                            fd_total = val
                        elif bk_key == "draftkings":
                            dk_total = val

            elif key == "h2h":
                for o in outcomes:
                    if o.get("name") == home_team:
                        ml_home_odds.append(o["price"])
                    elif o.get("name") == "Draw":
                        ml_draw_odds.append(o["price"])
                    else:
                        ml_away_odds.append(o["price"])

    def _weighted_consensus(pin, fd, dk, all_vals):
        """Pinnacle 50%, retail avg 50%. Fallback to median."""
        if pin is not None:
            retail_vals = [v for v in [fd, dk] if v is not None]
            if retail_vals:
                retail_avg = sum(retail_vals) / len(retail_vals)
                result = pin * 0.50 + retail_avg * 0.50
                logger.info(
                    f"[FairLine] Pinnacle={pin}, FD={fd}, DK={dk}, "
                    f"weighted_consensus={result:.2f}"
                )
                return result
            # Pinnacle only, no retail
            logger.info(f"[FairLine] Pinnacle={pin} only (no FD/DK)")
            return pin
        # No Pinnacle → simple median
        if all_vals:
            med = statistics.median(all_vals)
            if fd is not None or dk is not None:
                logger.debug(f"[FairLine] No Pinnacle, median={med} (FD={fd}, DK={dk})")
            return med
        return None

    book_spread = _weighted_consensus(pin_spread, fd_spread, dk_spread, all_spread_lines)
    book_total = _weighted_consensus(pin_total, fd_total, dk_total, all_total_lines)

    return {
        "book_spread": book_spread,
        "book_total": book_total,
        "book_ml_home": round(statistics.median(ml_home_odds)) if ml_home_odds else None,
        "book_ml_away": round(statistics.median(ml_away_odds)) if ml_away_odds else None,
        "book_ml_draw": round(statistics.median(ml_draw_odds)) if ml_draw_odds else None,
        "pinnacle_spread": pin_spread,
        "pinnacle_total": pin_total,
    }


class CompositeTracker:
    """Recalculates composites + fair lines for all active games."""

    def _fetch_latest_composites(self, game_ids: list) -> dict:
        """
        Batch-fetch the most recent composite_history row per game_id.
        Returns {game_id: {full row including fair_spread, fair_total, etc.}}.
        Single query + Python dedup avoids N per-game queries.
        All columns are fetched so carry-forward can propagate fair lines.
        """
        if not game_ids:
            return {}
        try:
            all_rows = []
            chunk_size = 200
            for i in range(0, len(game_ids), chunk_size):
                chunk = game_ids[i:i + chunk_size]
                result = db.client.table("composite_history").select(
                    "*"
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

    def _run_variable_engine(
        self,
        analysis: dict,
        sport_key: str,
        game_id: str,
        game_data: dict,
        book_spread: float | None,
    ) -> dict | None:
        """
        Run the 63-variable engine on a completed analysis.

        Returns {enhanced_composite, avg_confidence, pillar_scores, all_variables,
                 dynamic_weights, context} or None on failure.
        """
        ve = _get_variable_engine()
        if ve is None:
            return None

        try:
            sport_upper = SPORT_DISPLAY.get(sport_key, sport_key.upper())
            pillar_results = analysis.get("pillars", {})

            # Fetch team_stats for variable engine (may already be cached by analyzer)
            home_team = game_data.get("home_team", "")
            away_team = game_data.get("away_team", "")
            team_stats = fetch_team_environment_stats(home_team, away_team, sport_key)

            # Get opening/current line from line context
            line_ctx = fetch_line_context(game_id, sport_key)
            opening_line = line_ctx.get("opening_line")
            current_line = line_ctx.get("current_line")

            # Calculate all 63 variables
            all_variables = ve.calculate_all_variables(
                pillar_results, sport_upper,
                team_stats=team_stats,
                opening_line=opening_line,
                current_line=current_line,
            )

            # Build GameContext
            incentives = pillar_results.get("incentives", {})
            is_rivalry = incentives.get("is_rivalry", False)
            is_champ = incentives.get("is_championship", False)
            if is_champ:
                significance = "playoff"
            elif is_rivalry:
                significance = "rivalry"
            else:
                significance = "regular"

            commence_time = game_data.get("commence_time")
            ttg_hours = 24.0  # Default
            if commence_time:
                try:
                    game_dt = datetime.fromisoformat(
                        commence_time.replace("Z", "+00:00")
                    )
                    ttg_hours = max(0.0, (game_dt - datetime.now(timezone.utc)).total_seconds() / 3600)
                except (ValueError, AttributeError):
                    pass

            has_exchange = False
            try:
                from exchange_tracker import ExchangeTracker
                has_exchange = bool(ExchangeTracker().get_game_exchange_data(game_id))
            except Exception:
                pass

            game_env = pillar_results.get("game_environment", {})
            has_weather = bool((game_env.get("breakdown") or {}).get("weather_impact"))

            context = ve.GameContext(
                sport=sport_upper,
                market="spread",
                significance=significance,
                time_to_game_hours=ttg_hours,
                is_nationally_televised=False,
                conference_tier="power5",
                has_exchange_data=has_exchange,
                has_weather_data=has_weather,
            )

            # Aggregate and compute enhanced composite
            pillar_scores = ve.aggregate_pillar_scores(all_variables, context)
            enhanced_composite = ve.calculate_variable_composite(pillar_scores)

            # Average confidence across available variables
            summary = ve.get_variable_summary(all_variables)
            total_avail = summary["available_variables"]
            total_vars = summary["total_variables"]
            avg_confidence = 0.0
            if total_avail > 0:
                conf_sum = 0.0
                for var_list in all_variables.values():
                    for v in var_list:
                        if v.available:
                            conf_sum += v.confidence
                avg_confidence = conf_sum / total_avail

            dynamic_weights = ve.calculate_dynamic_weights(context)

            logger.info(
                f"[VarEngine] {game_id}: enhanced_composite={enhanced_composite:.3f}, "
                f"avg_confidence={avg_confidence:.2f}, "
                f"coverage={total_avail}/{total_vars}"
            )

            return {
                "enhanced_composite": enhanced_composite,
                "avg_confidence": avg_confidence,
                "pillar_scores": pillar_scores,
                "all_variables": all_variables,
                "dynamic_weights": dynamic_weights,
                "context": context,
                "summary": summary,
            }

        except Exception as e:
            logger.warning(
                f"[VarEngine] Failed for {game_id}: {e}\n{traceback.format_exc()}"
            )
            return None

    def _store_variable_results(
        self,
        game_id: str,
        sport_key: str,
        ve_result: dict,
    ) -> None:
        """
        Persist variable scores and dynamic weights to Supabase.
        Uses upsert (ON CONFLICT ... DO UPDATE) via the UNIQUE constraints.
        """
        try:
            # 1. Store individual variable scores → game_variables
            all_variables = ve_result["all_variables"]
            var_rows = []
            for var_list in all_variables.values():
                for v in var_list:
                    if not v.available:
                        continue  # Skip stubs — no value in storing neutral 0.5
                    var_rows.append({
                        "game_id": game_id,
                        "sport_key": sport_key,
                        "variable_code": v.code,
                        "variable_name": v.name,
                        "pillar": v.pillar,
                        "raw_value": round(v.raw_value, 4),
                        "normalized": round(v.normalized, 4),
                        "confidence": round(v.confidence, 2),
                        "source": v.source,
                    })

            if var_rows:
                # Batch upsert in chunks of 50
                for i in range(0, len(var_rows), 50):
                    chunk = var_rows[i:i + 50]
                    db.client.table("game_variables").upsert(
                        chunk, on_conflict="game_id,variable_code"
                    ).execute()

            # 2. Store dynamic weights → game_pillar_weights
            weights = ve_result["dynamic_weights"]
            ctx = ve_result["context"]
            weight_row = {
                "game_id": game_id,
                "sport_key": sport_key,
                "market_type": ctx.market,
                "execution_weight": round(weights.get("EXECUTION", 0), 4),
                "incentives_weight": round(weights.get("INCENTIVES", 0), 4),
                "shocks_weight": round(weights.get("SHOCKS", 0), 4),
                "time_decay_weight": round(weights.get("TIME_DECAY", 0), 4),
                "flow_weight": round(weights.get("FLOW", 0), 4),
                "game_env_weight": round(weights.get("GAME_ENV", 0), 4),
                "context_json": {
                    "sport": ctx.sport,
                    "market": ctx.market,
                    "significance": ctx.significance,
                    "time_to_game_hours": round(ctx.time_to_game_hours, 1),
                    "has_exchange_data": ctx.has_exchange_data,
                    "has_weather_data": ctx.has_weather_data,
                    "conference_tier": ctx.conference_tier,
                    "enhanced_composite": round(ve_result["enhanced_composite"], 4),
                    "avg_confidence": round(ve_result["avg_confidence"], 2),
                    "coverage": ve_result["summary"]["coverage_pct"],
                },
            }
            db.client.table("game_pillar_weights").upsert(
                weight_row, on_conflict="game_id,market_type"
            ).execute()

        except Exception as e:
            # Storage failure must never block composite calculation
            logger.warning(f"[VarEngine] Storage failed for {game_id}: {e}")

    def recalculate_all(self, force: bool = False) -> dict:
        """
        Main entry point. For every active (not yet started) game in cached_odds:
        1. Run analyze_game for fresh pillar scores
        2. Extract per-market composites
        3. Calculate fair lines (same formulas as edgescout.ts)
        4. Write row to composite_history
        5. Run variable engine → store results, use enhanced composite if confident

        force=True bypasses the movement check — forces fresh pillar analysis
        and fair line recalc for every game (use after deploying formula changes).
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
        ve_enhanced = 0   # Games where variable engine enhanced the composite
        ve_fallback = 0   # Games where variable engine fell back to old composite
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

                # 2. Movement check — skip if lines haven't moved (unless force=True)
                previous = latest_composites.get(game_id)
                if force:
                    should_recalc, reason = True, "forced"
                else:
                    should_recalc, reason = _should_recalculate(
                        game_id, book_spread, book_total, previous, now_dt
                    )

                if not should_recalc:
                    skipped += 1
                    continue

                # 3. Log the trigger reason
                logger.info(f"[DynamicRecalc] {game_id}: {reason}")

                # 3b. Carry-forward path: no line movement, just re-insert previous
                #     fair lines with fresh timestamp (cheap, skip pillar analysis)
                if reason.startswith("carry_forward_") and previous:
                    # Skip carry-forward if previous had no useful fair data
                    prev_fs = previous.get("fair_spread")
                    prev_ft = previous.get("fair_total")
                    prev_fmh = previous.get("fair_ml_home")
                    if prev_fs is None and prev_ft is None and prev_fmh is None:
                        skipped += 1
                        continue
                    row_data = {
                        "game_id": game_id,
                        "sport_key": sport_key,
                        "timestamp": now,
                        "composite_spread": previous.get("composite_spread"),
                        "composite_total": previous.get("composite_total"),
                        "composite_ml": previous.get("composite_ml"),
                        "fair_spread": previous.get("fair_spread"),
                        "fair_total": previous.get("fair_total"),
                        "fair_ml_home": previous.get("fair_ml_home"),
                        "fair_ml_away": previous.get("fair_ml_away"),
                        "book_spread": book_spread,
                        "book_total": book_total,
                        "book_ml_home": book_ml_home,
                        "book_ml_away": book_ml_away,
                    }
                    if previous.get("fair_ml_draw") is not None:
                        row_data["fair_ml_draw"] = previous["fair_ml_draw"]
                    if book_ml_draw is not None:
                        row_data["book_ml_draw"] = book_ml_draw
                    # Edge calculation — use carried-forward fair lines vs current book lines
                    raw_edge = _calculate_edge_pct(
                        previous.get("fair_spread"), book_spread,
                        previous.get("fair_total"), book_total, sport_key
                    )
                    capped_edge = _cap_edge(raw_edge)
                    row_data["raw_edge_pct"] = raw_edge
                    row_data["capped_edge_pct"] = capped_edge
                    if raw_edge >= EDGE_CAP_THRESHOLD:
                        logger.warning(f"[EdgeCap] {game_id}: raw={raw_edge:.1f}% -> capped={capped_edge:.1f}%")
                    # Flow gate — carry forward from previous row
                    cf_flow = previous.get("pillar_flow", 0.5) or 0.5
                    row_data["pillar_flow"] = cf_flow
                    flow_gated = (capped_edge is not None
                                  and abs(capped_edge) >= FLOW_GATE_EDGE_MIN
                                  and cf_flow < FLOW_GATE_THRESHOLD)
                    row_data["flow_gated"] = flow_gated
                    if flow_gated:
                        logger.info(f"[FlowGate] {game_id}: CARRY-FWD gated (flow={cf_flow:.2f}, edge={capped_edge:.1f}%)")
                    db.client.table("composite_history").insert(row_data).execute()
                    logger.info(
                        f"[CompositeTracker] CARRY-FORWARD {game_id}: "
                        f"fair_spread={previous.get('fair_spread')}, "
                        f"fair_total={previous.get('fair_total')}"
                    )
                    games_processed += 1
                    recalculated += 1
                    sport_processed[sport_key] = sport_processed.get(sport_key, 0) + 1
                    continue

                # 4. Fresh pillar analysis (EXPENSIVE — only when movement detected)
                analysis = analyze_game(game_data, sport_key)

                # 4b. Variable engine — enhanced composite (safe fallback)
                ve_result = self._run_variable_engine(
                    analysis, sport_key, game_id, game_data, book_spread,
                )
                if ve_result is not None:
                    self._store_variable_results(game_id, sport_key, ve_result)

                # 5. Per-market composites from pillars_by_market
                pbm = analysis.get("pillars_by_market", {})
                composite_spread = pbm.get("spread", {}).get("full", {}).get("composite")
                composite_total = pbm.get("totals", {}).get("full", {}).get("composite")
                composite_ml = pbm.get("moneyline", {}).get("full", {}).get("composite")

                # 5a. Use enhanced composite IF variable engine succeeded and
                #     confidence is above 0.5 — otherwise keep old composite.
                #     Enhanced composite blends into spread composite only (primary market).
                if (
                    ve_result is not None
                    and ve_result["avg_confidence"] > 0.5
                    and composite_spread is not None
                ):
                    old_cs = composite_spread
                    # Blend: 70% old composite + 30% enhanced (conservative ramp-in)
                    composite_spread = old_cs * 0.70 + ve_result["enhanced_composite"] * 0.30
                    ve_enhanced += 1
                    if games_processed < 5:
                        logger.info(
                            f"[VarEngine] {game_id}: blended spread composite "
                            f"{old_cs:.3f} -> {composite_spread:.3f} "
                            f"(enhanced={ve_result['enhanced_composite']:.3f}, "
                            f"conf={ve_result['avg_confidence']:.2f})"
                        )
                else:
                    ve_fallback += 1

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
                    exchange_adj = _calc_exchange_divergence_boost(game_id, book_spread, sport_key)
                    if exchange_adj != 0.0:
                        fair_spread = _round_to_half(fair_spread + exchange_adj)
                    fair_ml_home, fair_ml_away = _calculate_fair_ml(fair_spread, sport_key)

                    # Soccer: 3-way ML derived from spread for coherence
                    if is_soccer and book_ml_home is not None and book_ml_draw is not None and book_ml_away is not None:
                        comp = composite_ml if composite_ml is not None else 0.5
                        fair_ml_home, fair_ml_draw, fair_ml_away = _calculate_fair_ml_from_book_3way(
                            book_ml_home, book_ml_draw, book_ml_away, comp, book_spread, sport_key
                        )

                elif is_soccer and book_ml_home is not None and book_ml_draw is not None and book_ml_away is not None and composite_ml is not None:
                    # Soccer 3-way ML (no spread data — composite-only fallback)
                    fair_ml_home, fair_ml_draw, fair_ml_away = _calculate_fair_ml_from_book_3way(
                        book_ml_home, book_ml_draw, book_ml_away, composite_ml
                    )
                elif composite_ml is not None:
                    # No spread data — composite-only ML
                    fair_ml_home, fair_ml_away = _calculate_fair_ml_composite_only(composite_ml)

                if book_total is not None:
                    # Use full totals composite; fall back to game_env pillar if unavailable
                    game_env_score = analysis.get("pillar_scores", {}).get("game_environment", 0.5)
                    total_signal = composite_total if composite_total is not None else game_env_score
                    fair_total = _calculate_fair_total(book_total, total_signal)

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

                # 5c. Cap fair lines — sport-specific caps prevent extreme deviations
                s_cap = SPREAD_CAP_BY_SPORT.get(sport_key, DEFAULT_SPREAD_CAP)
                t_cap = TOTAL_CAP_BY_SPORT.get(sport_key, DEFAULT_TOTAL_CAP)

                if fair_spread is not None and book_spread is not None:
                    capped = max(book_spread - s_cap,
                                 min(book_spread + s_cap, fair_spread))
                    if capped != fair_spread:
                        logger.warning(
                            f"[FairCap] {game_id}: spread capped {fair_spread}→{capped} "
                            f"(book={book_spread}, cap=±{s_cap}, sport={sport_key})"
                        )
                        fair_spread = capped

                if fair_total is not None and book_total is not None:
                    capped = max(book_total - t_cap,
                                 min(book_total + t_cap, fair_total))
                    if capped != fair_total:
                        logger.warning(
                            f"[FairCap] {game_id}: total capped {fair_total}→{capped} "
                            f"(book={book_total}, cap=±{t_cap}, sport={sport_key})"
                        )
                        fair_total = capped

                # 6. Skip write if all fair values are null (analyzer returned nothing useful)
                if fair_spread is None and fair_total is None and fair_ml_home is None:
                    logger.debug(f"[CompositeTracker] SKIP {game_id}: all fair values null after analysis")
                    skipped += 1
                    continue

                # 7. Insert row
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
                # Edge calculation and soft cap
                raw_edge = _calculate_edge_pct(fair_spread, book_spread, fair_total, book_total, sport_key)
                capped_edge = _cap_edge(raw_edge)
                row_data["raw_edge_pct"] = raw_edge
                row_data["capped_edge_pct"] = capped_edge
                if raw_edge >= EDGE_CAP_THRESHOLD:
                    logger.warning(f"[EdgeCap] {game_id}: raw={raw_edge:.1f}% -> capped={capped_edge:.1f}%")
                # Flow gate — use fresh pillar flow from analysis
                flow_score = analysis.get("pillar_scores", {}).get("flow", 0.5) or 0.5
                row_data["pillar_flow"] = flow_score
                flow_gated = (capped_edge is not None
                              and abs(capped_edge) >= FLOW_GATE_EDGE_MIN
                              and flow_score < FLOW_GATE_THRESHOLD)
                row_data["flow_gated"] = flow_gated
                if flow_gated:
                    logger.info(f"[FlowGate] {game_id}: gated (flow={flow_score:.2f}, edge={capped_edge:.1f}%)")
                db.client.table("composite_history").insert(row_data).execute()
                logger.info(
                    f"[CompositeTracker] WRITE {game_id}: "
                    f"fair_spread={fair_spread}, fair_total={fair_total}, "
                    f"reason={reason}"
                )

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
            f"skipped {skipped} unchanged (errors={errors}). "
            f"VarEngine: {ve_enhanced} enhanced, {ve_fallback} fallback"
        )

        # --- Second pass: seed new games with no composite_history entry ---
        # Wrapped in try/except so it can never break the main recalc.
        try:
            if not force:
                processed_ids = set()
                for row in rows:
                    if row.get("game_data"):
                        processed_ids.add(row["game_id"])

                fresh_composites = self._fetch_latest_composites(list(processed_ids))
                missing = [
                    row for row in rows
                    if row.get("game_data") and row["game_id"] not in fresh_composites
                ]

                if missing:
                    logger.info(
                        f"[CompositeTracker] Second pass: {len(missing)} games "
                        f"with no composite_history — force-processing"
                    )
                    seeded = 0
                    for row in missing:
                        try:
                            sport_key = row["sport_key"]
                            game_id = row["game_id"]
                            game_data = row["game_data"]

                            book_lines = _extract_median_lines(game_data)
                            book_spread = book_lines["book_spread"]
                            book_total = book_lines["book_total"]
                            book_ml_home = book_lines["book_ml_home"]
                            book_ml_away = book_lines["book_ml_away"]
                            book_ml_draw = book_lines["book_ml_draw"]

                            analysis = analyze_game(game_data, sport_key)

                            pbm = analysis.get("pillars_by_market", {})
                            composite_spread = pbm.get("spread", {}).get("full", {}).get("composite")
                            composite_total = pbm.get("totals", {}).get("full", {}).get("composite")
                            composite_ml = pbm.get("moneyline", {}).get("full", {}).get("composite")

                            is_soccer = "soccer" in sport_key

                            fair_spread = None
                            fair_total = None
                            fair_ml_home = None
                            fair_ml_away = None
                            fair_ml_draw = None

                            if book_spread is not None and composite_spread is not None:
                                fair_spread = _calculate_fair_spread(book_spread, composite_spread)
                                fair_ml_home, fair_ml_away = _calculate_fair_ml(fair_spread, sport_key)
                                if is_soccer and book_ml_home is not None and book_ml_draw is not None and book_ml_away is not None:
                                    comp = composite_ml if composite_ml is not None else 0.5
                                    fair_ml_home, fair_ml_draw, fair_ml_away = _calculate_fair_ml_from_book_3way(
                                        book_ml_home, book_ml_draw, book_ml_away, comp, book_spread, sport_key
                                    )
                            elif is_soccer and book_ml_home is not None and book_ml_draw is not None and book_ml_away is not None and composite_ml is not None:
                                fair_ml_home, fair_ml_draw, fair_ml_away = _calculate_fair_ml_from_book_3way(
                                    book_ml_home, book_ml_draw, book_ml_away, composite_ml
                                )
                            elif composite_ml is not None:
                                fair_ml_home, fair_ml_away = _calculate_fair_ml_composite_only(composite_ml)

                            if book_total is not None:
                                game_env_score = analysis.get("pillar_scores", {}).get("game_environment", 0.5)
                                total_signal = composite_total if composite_total is not None else game_env_score
                                fair_total = _calculate_fair_total(book_total, total_signal)

                            # Skip if all fair values are null
                            if fair_spread is None and fair_total is None and fair_ml_home is None:
                                logger.debug(f"[CompositeTracker] SEED-SKIP {game_id}: all fair values null")
                                continue

                            # Sport-specific caps
                            s_cap = SPREAD_CAP_BY_SPORT.get(sport_key, DEFAULT_SPREAD_CAP)
                            t_cap = TOTAL_CAP_BY_SPORT.get(sport_key, DEFAULT_TOTAL_CAP)
                            if fair_spread is not None and book_spread is not None:
                                fair_spread = max(book_spread - s_cap, min(book_spread + s_cap, fair_spread))
                            if fair_total is not None and book_total is not None:
                                fair_total = max(book_total - t_cap, min(book_total + t_cap, fair_total))

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
                            if book_ml_draw is not None:
                                row_data["book_ml_draw"] = book_ml_draw
                            raw_edge = _calculate_edge_pct(fair_spread, book_spread, fair_total, book_total, sport_key)
                            capped_edge = _cap_edge(raw_edge)
                            row_data["raw_edge_pct"] = raw_edge
                            row_data["capped_edge_pct"] = capped_edge
                            flow_score = analysis.get("pillar_scores", {}).get("flow", 0.5) or 0.5
                            row_data["pillar_flow"] = flow_score
                            row_data["flow_gated"] = (
                                capped_edge is not None
                                and abs(capped_edge) >= FLOW_GATE_EDGE_MIN
                                and flow_score < FLOW_GATE_THRESHOLD
                            )

                            db.client.table("composite_history").insert(row_data).execute()
                            logger.info(
                                f"[CompositeTracker] SEED {game_id}: "
                                f"fair_spread={fair_spread}, fair_total={fair_total}"
                            )
                            seeded += 1
                            games_processed += 1
                            recalculated += 1
                            sport_processed[sport_key] = sport_processed.get(sport_key, 0) + 1

                        except Exception as e:
                            logger.error(
                                f"[CompositeTracker] Seed error {row.get('game_id', '?')}: {e}\n"
                                f"{traceback.format_exc()}"
                            )
                            errors += 1
                            sk = row.get("sport_key", "unknown")
                            sport_errors[sk] = sport_errors.get(sk, 0) + 1

                    logger.info(
                        f"[CompositeTracker] Second pass complete: "
                        f"seeded {seeded}/{len(missing)} new games"
                    )
        except Exception as e:
            logger.error(f"[CompositeTracker] Second pass failed (non-fatal): {e}\n{traceback.format_exc()}")

        summary = {
            "games_processed": games_processed,
            "recalculated": recalculated,
            "skipped_unchanged": skipped,
            "errors": errors,
            "timestamp": now,
            "by_sport": sport_processed,
            "errors_by_sport": sport_errors if sport_errors else None,
            "variable_engine": {
                "enhanced": ve_enhanced,
                "fallback": ve_fallback,
            },
        }
        logger.info(f"[CompositeTracker] Done: {summary}")
        return summary

    def fast_refresh_live(self) -> dict:
        """
        Lightweight fair-line refresh for LIVE games only (every 30s).

        Skips the expensive pillar analysis + variable engine.
        Instead: reuse the composite scores from the last full calculation,
        grab the latest consensus book lines, recompute fair values.
        Also fetches ESPN live scores and calculates live CEQ + hold signals.

        Each result is stored in composite_history so the chart plots it.
        """
        if not db._is_connected():
            return {"error": "Database not connected", "refreshed": 0}

        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()

        try:
            result = db.client.table("cached_odds").select(
                "sport_key, game_id, game_data"
            ).limit(5000).execute()
        except Exception as e:
            logger.error(f"[FastRefresh] Failed to query cached_odds: {e}")
            return {"error": str(e), "refreshed": 0}

        all_rows = result.data or []

        # Filter to LIVE or near-tipoff games: started within 8h or starting within 30min
        live_rows = []
        for row in all_rows:
            gd = row.get("game_data") or {}
            ct = gd.get("commence_time")
            if not ct:
                continue
            try:
                game_dt = datetime.fromisoformat(ct.replace("Z", "+00:00"))
                hours_ago = (now_dt - game_dt).total_seconds() / 3600
                if -0.5 < hours_ago <= 8:
                    live_rows.append(row)
            except (ValueError, AttributeError):
                continue

        if not live_rows:
            logger.info("[FastRefresh] No live games found")
            return {"refreshed": 0, "live_games": 0}

        logger.info(f"[FastRefresh] Found {len(live_rows)} live games")

        # Batch-fetch latest composite_history rows (for composite scores)
        game_ids = [row["game_id"] for row in live_rows]
        try:
            all_history = []
            chunk_size = 200
            for i in range(0, len(game_ids), chunk_size):
                chunk = game_ids[i:i + chunk_size]
                res = db.client.table("composite_history").select(
                    "game_id, composite_spread, composite_total, composite_ml, "
                    "fair_spread, fair_total, fair_ml_home, fair_ml_away, fair_ml_draw, "
                    "book_spread, book_total, timestamp"
                ).in_("game_id", chunk).order("timestamp", desc=True).execute()
                all_history.extend(res.data or [])

            # Dedup: keep newest per game_id
            latest = {}
            for h in all_history:
                gid = h["game_id"]
                if gid not in latest:
                    latest[gid] = h
        except Exception as e:
            logger.error(f"[FastRefresh] Failed to fetch composite history: {e}")
            return {"error": str(e), "refreshed": 0}

        # Fetch ESPN live scores per sport
        espn_by_game_id: dict[str, dict] = {}
        sports_seen = set()
        for row in live_rows:
            sports_seen.add(row["sport_key"])

        espn_scores_by_sport: dict[str, list] = {}
        espn = ESPNScoreFetcher()
        try:
            for sport_key in sports_seen:
                espn_sport = SPORT_DISPLAY.get(sport_key)
                if espn_sport and espn_sport in ESPN_SPORTS and espn_sport not in espn_scores_by_sport:
                    try:
                        espn_scores_by_sport[espn_sport] = espn.get_scores(espn_sport)
                    except Exception as e:
                        logger.warning(f"[FastRefresh] ESPN fetch failed for {espn_sport}: {e}")
                        espn_scores_by_sport[espn_sport] = []
        finally:
            espn.client.close()

        # Match ESPN scores to game_ids using team name matching
        for row in live_rows:
            gd = row.get("game_data") or {}
            home = gd.get("home_team", "")
            away = gd.get("away_team", "")
            espn_sport = SPORT_DISPLAY.get(row["sport_key"])
            if not espn_sport:
                continue
            for lg in espn_scores_by_sport.get(espn_sport, []):
                if teams_match(lg.get("home_team", ""), home) and teams_match(lg.get("away_team", ""), away):
                    espn_by_game_id[row["game_id"]] = lg
                    break
                if teams_match(lg.get("home_team", ""), away) and teams_match(lg.get("away_team", ""), home):
                    espn_by_game_id[row["game_id"]] = {
                        **lg,
                        "home_team": lg["away_team"], "away_team": lg["home_team"],
                        "home_score": lg.get("away_score", 0), "away_score": lg.get("home_score", 0),
                    }
                    break

        # Batch-fetch pregame baselines (rows where live_ceq IS NULL = pregame)
        pregame_baselines: dict[str, dict] = {}
        try:
            for i in range(0, len(game_ids), chunk_size):
                chunk = game_ids[i:i + chunk_size]
                pg_res = db.client.table("composite_history").select(
                    "game_id, composite_spread, fair_spread"
                ).in_("game_id", chunk).is_("live_ceq", "null").order(
                    "timestamp", desc=True
                ).execute()
                for h in (pg_res.data or []):
                    gid = h["game_id"]
                    if gid not in pregame_baselines:
                        pregame_baselines[gid] = h
        except Exception as e:
            logger.warning(f"[FastRefresh] Pregame baseline fetch failed: {e}")

        # Bias correction cache
        bias_cache: dict[str, dict] = {}

        refreshed = 0
        skipped_no_history = 0
        skipped_no_change = 0
        errors = 0

        for row in live_rows:
            try:
                sport_key = row["sport_key"]
                game_id = row["game_id"]
                game_data = row["game_data"]
                if not game_data:
                    continue

                prev = latest.get(game_id)
                if not prev:
                    skipped_no_history += 1
                    continue

                # Reuse composite scores from last full calculation
                composite_spread = prev.get("composite_spread")
                composite_total = prev.get("composite_total")
                composite_ml = prev.get("composite_ml")

                # Fresh consensus book lines from cached_odds
                book_lines = _extract_median_lines(game_data)
                book_spread = book_lines["book_spread"]
                book_total = book_lines["book_total"]
                book_ml_home = book_lines["book_ml_home"]
                book_ml_away = book_lines["book_ml_away"]
                book_ml_draw = book_lines["book_ml_draw"]

                # Skip if book lines haven't moved since last entry
                prev_bs = prev.get("book_spread")
                prev_bt = prev.get("book_total")
                spread_moved = (book_spread is not None and prev_bs is not None
                                and abs(float(book_spread) - float(prev_bs)) >= 0.25)
                total_moved = (book_total is not None and prev_bt is not None
                               and abs(float(book_total) - float(prev_bt)) >= 0.5)
                # Also refresh if last entry is >45s old (at 30s intervals, ensures ≥1 write/min)
                stale = False
                try:
                    prev_ts = datetime.fromisoformat(prev["timestamp"].replace("Z", "+00:00"))
                    stale = (now_dt - prev_ts).total_seconds() > 45
                except (ValueError, TypeError, KeyError):
                    stale = True

                if not spread_moved and not total_moved and not stale:
                    skipped_no_change += 1
                    continue

                is_soccer = "soccer" in sport_key

                # Calculate fair lines (same logic as full recalc)
                fair_spread = None
                fair_total = None
                fair_ml_home = None
                fair_ml_away = None
                fair_ml_draw = None

                if book_spread is not None and composite_spread is not None:
                    fair_spread = _calculate_fair_spread(book_spread, composite_spread)
                    exchange_adj = _calc_exchange_divergence_boost(game_id, book_spread, sport_key)
                    if exchange_adj != 0.0:
                        fair_spread = _round_to_half(fair_spread + exchange_adj)
                    fair_ml_home, fair_ml_away = _calculate_fair_ml(fair_spread, sport_key)

                    if is_soccer and book_ml_home is not None and book_ml_draw is not None and book_ml_away is not None:
                        comp = composite_ml if composite_ml is not None else 0.5
                        fair_ml_home, fair_ml_draw, fair_ml_away = _calculate_fair_ml_from_book_3way(
                            book_ml_home, book_ml_draw, book_ml_away, comp, book_spread, sport_key
                        )

                elif is_soccer and book_ml_home is not None and book_ml_draw is not None and book_ml_away is not None and composite_ml is not None:
                    fair_ml_home, fair_ml_draw, fair_ml_away = _calculate_fair_ml_from_book_3way(
                        book_ml_home, book_ml_draw, book_ml_away, composite_ml
                    )
                elif composite_ml is not None:
                    fair_ml_home, fair_ml_away = _calculate_fair_ml_composite_only(composite_ml)

                if book_total is not None:
                    # composite_total already available from carry-forward data
                    total_signal = composite_total if composite_total is not None else 0.5
                    fair_total = _calculate_fair_total(book_total, total_signal)

                # Bias correction
                if sport_key not in bias_cache:
                    bias_cache[sport_key] = _get_bias_correction(sport_key)
                bias = bias_cache[sport_key]

                if fair_spread is not None and bias.get("spread_bias") is not None and bias.get("spread_sample", 0) >= 50:
                    fair_spread = _round_to_half(fair_spread - bias["spread_bias"] * 0.3)

                if fair_total is not None and bias.get("total_bias") is not None and bias.get("total_sample", 0) >= 50:
                    fair_total = _round_to_half(fair_total - bias["total_bias"] * 0.3)

                # Sport-specific caps
                s_cap = SPREAD_CAP_BY_SPORT.get(sport_key, DEFAULT_SPREAD_CAP)
                t_cap = TOTAL_CAP_BY_SPORT.get(sport_key, DEFAULT_TOTAL_CAP)

                if fair_spread is not None and book_spread is not None:
                    fair_spread = max(book_spread - s_cap, min(book_spread + s_cap, fair_spread))

                if fair_total is not None and book_total is not None:
                    fair_total = max(book_total - t_cap, min(book_total + t_cap, fair_total))

                # Insert row to composite_history
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
                # Edge calculation and soft cap
                raw_edge = _calculate_edge_pct(fair_spread, book_spread, fair_total, book_total, sport_key)
                capped_edge = _cap_edge(raw_edge)
                row_data["raw_edge_pct"] = raw_edge
                row_data["capped_edge_pct"] = capped_edge
                if raw_edge >= EDGE_CAP_THRESHOLD:
                    logger.warning(f"[EdgeCap] {game_id}: raw={raw_edge:.1f}% -> capped={capped_edge:.1f}%")
                # Flow gate — carry forward from previous composite_history row
                fr_flow = prev.get("pillar_flow", 0.5) or 0.5
                row_data["pillar_flow"] = fr_flow
                flow_gated = (capped_edge is not None
                              and abs(capped_edge) >= FLOW_GATE_EDGE_MIN
                              and fr_flow < FLOW_GATE_THRESHOLD)
                row_data["flow_gated"] = flow_gated
                if flow_gated:
                    logger.info(f"[FlowGate] {game_id}: FAST-REFRESH gated (flow={fr_flow:.2f}, edge={capped_edge:.1f}%)")

                # Live CEQ calculation from ESPN scores
                espn_game = espn_by_game_id.get(game_id)
                if espn_game and espn_game.get("status") == "STATUS_IN_PROGRESS":
                    home_score = espn_game.get("home_score", 0)
                    away_score = espn_game.get("away_score", 0)
                    period = espn_game.get("period", "")
                    clock = espn_game.get("clock", "")
                    espn_sport = SPORT_DISPLAY.get(sport_key, "")

                    total_mins = _total_minutes_for_sport(espn_sport)
                    minutes_elapsed = _estimate_minutes_elapsed(period, clock, espn_sport)
                    time_remaining_pct = 1.0 - min(minutes_elapsed / total_mins, 1.0) if total_mins > 0 else 1.0

                    # Get pregame baseline
                    pg_baseline = pregame_baselines.get(game_id)
                    if pg_baseline:
                        pregame_ceq = (pg_baseline.get("composite_spread") or 0.5) * 100
                        pregame_fair_spread = pg_baseline.get("fair_spread") or 0.0
                    else:
                        pregame_ceq = (composite_spread or 0.5) * 100
                        pregame_fair_spread = fair_spread or 0.0

                    score_diff = home_score - away_score
                    live_ceq, hold_signal = _calculate_live_ceq(
                        pregame_ceq, pregame_fair_spread, score_diff, time_remaining_pct
                    )

                    row_data["live_ceq"] = round(live_ceq, 2)
                    row_data["hold_signal"] = hold_signal
                    row_data["score_home"] = home_score
                    row_data["score_away"] = away_score
                    row_data["period"] = period
                    row_data["clock"] = clock
                    row_data["time_remaining_pct"] = round(time_remaining_pct, 4)

                db.client.table("composite_history").insert(row_data).execute()
                ceq_info = ""
                if row_data.get("live_ceq") is not None:
                    ceq_info = f", live_ceq={row_data['live_ceq']}, {row_data.get('hold_signal', '')}"
                logger.info(
                    f"[CompositeTracker] WRITE-FAST {game_id}: "
                    f"fair_spread={fair_spread}, fair_total={fair_total}{ceq_info}"
                )

                refreshed += 1

            except Exception as e:
                logger.error(f"[FastRefresh] Error on {row.get('game_id', '?')}: {e}")
                errors += 1

        summary = {
            "refreshed": refreshed,
            "live_games": len(live_rows),
            "skipped_no_history": skipped_no_history,
            "skipped_no_change": skipped_no_change,
            "errors": errors,
            "timestamp": now,
        }
        logger.info(f"[FastRefresh] Done: {summary}")
        return summary
