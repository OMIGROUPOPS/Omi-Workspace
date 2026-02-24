"""
Player Analytics Engine

Builds player-level projections, form scores, and consistency signals
from BallDontLie data. Used by the prop terminal to enrich fair lines.

Key outputs:
- projection: blended estimate (60% recent-5 avg + 40% season avg)
- player_form: 0-100 signal comparing recent performance to season baseline
- minutes_consistency: 0-100 signal from minutes volume + coefficient of variation
"""
import logging
from typing import Optional
from datetime import datetime, timezone

from player_stats import bdl_client
from database import db

logger = logging.getLogger(__name__)

# ============================================================================
# Name overrides — BDL uses suffixes that differ from book player names
# ============================================================================
NAME_OVERRIDES: dict[str, str] = {
    "GG Jackson": "GG Jackson II",
    "Jaren Jackson": "Jaren Jackson Jr.",
    "Gary Trent": "Gary Trent Jr.",
    "Tim Hardaway": "Tim Hardaway Jr.",
    "Kelly Oubre": "Kelly Oubre Jr.",
    "Larry Nance": "Larry Nance Jr.",
    "Wendell Carter": "Wendell Carter Jr.",
    "Marcus Morris": "Marcus Morris Sr.",
    "Derrick Jones": "Derrick Jones Jr.",
    "Kevin Porter": "Kevin Porter Jr.",
    "Michael Porter": "Michael Porter Jr.",
    "Otto Porter": "Otto Porter Jr.",
    "Jabari Smith": "Jabari Smith Jr.",
    "Kenyon Martin": "Kenyon Martin Jr.",
    "Scottie Barnes": "Scottie Barnes",
    "Trey Murphy": "Trey Murphy III",
    "Robert Williams": "Robert Williams III",
    "Lonnie Walker": "Lonnie Walker IV",
}

# ============================================================================
# Prop type → BDL stat key mapping (NBA only for now)
# ============================================================================
PROP_TO_STAT_KEY: dict[str, list[str]] = {
    "player_points": ["pts"],
    "player_rebounds": ["reb"],
    "player_assists": ["ast"],
    "player_threes": ["fg3m"],
    "player_steals": ["stl"],
    "player_blocks": ["blk"],
    "player_turnovers": ["turnover"],
    "player_points_rebounds_assists": ["pts", "reb", "ast"],
    "player_points_rebounds": ["pts", "reb"],
    "player_points_assists": ["pts", "ast"],
    "player_rebounds_assists": ["reb", "ast"],
}

# In-memory player ID cache: name → bdl_player_id (or None if not found)
_player_id_cache: dict[str, Optional[int]] = {}


# ============================================================================
# Name resolution
# ============================================================================

def resolve_player_id(player_name: str) -> Optional[int]:
    """Resolve a player name to a BDL player ID using 3-tier approach."""
    # Only use in-memory cache for positive hits (not None)
    cached_id = _player_id_cache.get(player_name)
    if cached_id is not None:
        return cached_id

    # Check DB cache first
    cached = db.get_player_cache(player_name)
    if cached and cached.get("bdl_player_id"):
        pid = cached["bdl_player_id"]
        _player_id_cache[player_name] = pid
        return pid

    # Tier 1: Name overrides
    search_name = NAME_OVERRIDES.get(player_name, player_name)
    logger.info(f"[PlayerAnalytics] Resolving player ID for '{player_name}' (search: '{search_name}')")

    # Tier 2: BDL search API
    result = bdl_client.search_player(search_name)
    if result and result.get("id"):
        pid = result["id"]
        _player_id_cache[player_name] = pid
        return pid

    # Tier 3: Fuzzy match
    try:
        from rapidfuzz import fuzz
        # Try searching with just last name
        parts = search_name.split()
        if len(parts) >= 2:
            last_name = parts[-1]
            result = bdl_client.search_player(last_name)
            if result and result.get("id"):
                full = f"{result.get('first_name', '')} {result.get('last_name', '')}".strip()
                ratio = fuzz.ratio(search_name.lower(), full.lower())
                if ratio >= 80:
                    pid = result["id"]
                    _player_id_cache[player_name] = pid
                    return pid
    except ImportError:
        logger.debug("[PlayerAnalytics] rapidfuzz not installed, skipping fuzzy match")

    logger.warning(f"[PlayerAnalytics] Player not found: {player_name}")
    # Do NOT cache None — allow retries on next request
    return None


# ============================================================================
# Stat extraction helpers
# ============================================================================

def _extract_stat(game: dict, stat_keys: list[str]) -> Optional[float]:
    """Sum the stat keys from a game log entry. Returns None if any key is missing."""
    total = 0.0
    for key in stat_keys:
        val = game.get(key)
        if val is None:
            return None
        total += float(val)
    return total


def _recent_n_avg(games: list[dict], stat_keys: list[str], n: int = 5) -> Optional[float]:
    """Average of stat over the most recent N games."""
    values = []
    for g in games[:n]:
        val = _extract_stat(g, stat_keys)
        if val is not None:
            values.append(val)
    if not values:
        return None
    return sum(values) / len(values)


def _season_avg_stat(season_averages: dict, stat_keys: list[str]) -> Optional[float]:
    """Sum stat keys from season averages dict."""
    total = 0.0
    for key in stat_keys:
        val = season_averages.get(key)
        if val is None:
            return None
        total += float(val)
    return total


# ============================================================================
# Projection
# ============================================================================

def compute_projection(
    season_averages: dict, recent_games: list[dict], stat_keys: list[str]
) -> Optional[float]:
    """
    Blended projection: 60% recent-5-game avg + 40% season avg.
    Returns None if insufficient data.
    """
    recent = _recent_n_avg(recent_games, stat_keys, n=5)
    season = _season_avg_stat(season_averages, stat_keys)

    if recent is not None and season is not None:
        return round(recent * 0.60 + season * 0.40, 1)
    if recent is not None:
        return round(recent, 1)
    if season is not None:
        return round(season, 1)
    return None


# ============================================================================
# Player Form signal (0-100)
# ============================================================================

def compute_player_form(
    season_averages: dict, recent_games: list[dict], stat_keys: list[str]
) -> int:
    """
    Compare recent 5-game avg to season avg.
    Ratio > 1.0 → trending up (form > 50), ratio < 1.0 → trending down.
    Returns 0-100 score.
    """
    recent = _recent_n_avg(recent_games, stat_keys, n=5)
    season = _season_avg_stat(season_averages, stat_keys)

    if recent is None or season is None or season == 0:
        return 50  # Neutral default

    ratio = recent / season
    # Map ratio to 0-100: ratio 0.7 → ~15, ratio 1.0 → 50, ratio 1.3 → ~85
    score = 50 + (ratio - 1.0) * 120
    return max(0, min(100, round(score)))


# ============================================================================
# Minutes / Consistency signal (0-100)
# ============================================================================

def compute_minutes_consistency(recent_games: list[dict]) -> int:
    """
    Combines minutes volume + coefficient of variation into a 0-100 score.
    Higher minutes + lower variance = higher signal.
    """
    minutes = []
    for g in recent_games[:10]:
        m = g.get("min")
        if m is None:
            continue
        # BDL returns minutes as "MM:SS" string or float
        if isinstance(m, str) and ":" in m:
            parts = m.split(":")
            try:
                minutes.append(float(parts[0]) + float(parts[1]) / 60)
            except (ValueError, IndexError):
                continue
        else:
            try:
                minutes.append(float(m))
            except (ValueError, TypeError):
                continue

    if len(minutes) < 3:
        return 50  # Not enough data

    avg_min = sum(minutes) / len(minutes)
    if avg_min == 0:
        return 20

    # Volume component: 36 min → 100%, scaled linearly
    volume_score = min(1.0, avg_min / 36.0) * 60  # Max 60 points from volume

    # Consistency component: lower CV is better
    import math
    variance = sum((m - avg_min) ** 2 for m in minutes) / len(minutes)
    std_dev = math.sqrt(variance)
    cv = std_dev / avg_min  # coefficient of variation

    # CV 0.0 → 40 points, CV 0.3+ → 0 points
    consistency_score = max(0, 40 * (1.0 - cv / 0.3))

    return max(0, min(100, round(volume_score + consistency_score)))


# ============================================================================
# Profile builder
# ============================================================================

def get_player_profile(player_name: str, prop_type: str, force: bool = False) -> Optional[dict]:
    """
    Get full player profile for prop analytics.
    Checks cache first, fetches from BDL if stale/missing.

    Returns:
        {
            player, prop_type, projection, player_form, minutes_consistency,
            season_averages, recent_trend, injury_status, source
        }
    """
    stat_keys = PROP_TO_STAT_KEY.get(prop_type)
    if not stat_keys:
        logger.debug(f"[PlayerAnalytics] No stat mapping for prop type: {prop_type}")
        return None

    sport_key = "basketball_nba"

    # Check cache — only trust entries that have real data
    cached = db.get_player_cache(player_name, sport_key) if not force else None
    cache_valid = (
        cached is not None
        and cached.get("bdl_player_id")
        and cached.get("season_averages")
        and cached["season_averages"] != {}
    )

    season_averages = None
    recent_games = None
    injury_status = None

    if cache_valid:
        logger.debug(f"[PlayerAnalytics] Cache hit for {player_name}")
        season_averages = cached.get("season_averages", {})
        recent_games = cached.get("recent_games", [])
        injury_status = cached.get("injury_status")
    else:
        # Fetch from BDL
        if cached and not cache_valid:
            logger.info(f"[PlayerAnalytics] Stale/empty cache for {player_name}, refetching from BDL")
        else:
            logger.info(f"[PlayerAnalytics] No cache for {player_name}, fetching from BDL")

        player_id = resolve_player_id(player_name)
        if player_id is None:
            return None

        profile = bdl_client.fetch_full_profile(player_id)
        if profile is None:
            return None

        season_averages = profile.get("season_averages", {})
        recent_games = profile.get("recent_games", [])
        advanced_stats = profile.get("advanced_stats", [])

        # Save to cache
        db.save_player_cache(
            player_name=player_name,
            bdl_player_id=player_id,
            sport_key=sport_key,
            season_averages=season_averages,
            recent_games=recent_games,
            advanced_stats=advanced_stats,
            injury_status=None,
        )

    # Compute analytics
    projection = compute_projection(season_averages or {}, recent_games or [], stat_keys)
    form = compute_player_form(season_averages or {}, recent_games or [], stat_keys)
    consistency = compute_minutes_consistency(recent_games or [])

    # Recent trend: last 5 values
    recent_trend = []
    for g in (recent_games or [])[:5]:
        val = _extract_stat(g, stat_keys)
        if val is not None:
            recent_trend.append(round(val, 1))

    return {
        "player": player_name,
        "prop_type": prop_type,
        "projection": projection,
        "player_form": form,
        "minutes_consistency": consistency,
        "season_averages": season_averages or {},
        "recent_trend": recent_trend,
        "injury_status": injury_status,
        "source": "omi_model",
    }


# ============================================================================
# Scheduler helper: refresh stale cache entries
# ============================================================================

def refresh_active_players(sport_key: str = "basketball_nba") -> dict:
    """Refresh stale entries in player_stats_cache."""
    now = datetime.now(timezone.utc)
    rows = db.get_all_cached_players(sport_key)
    refreshed = 0
    skipped = 0
    errors = 0

    for row in rows:
        name = row.get("player_name")
        bdl_id = row.get("bdl_player_id")
        expires_at = row.get("expires_at")

        # Skip if not yet expired
        if expires_at:
            from dateutil.parser import parse as parse_dt
            try:
                if parse_dt(expires_at) > now:
                    skipped += 1
                    continue
            except Exception:
                pass

        if not bdl_id:
            bdl_id = resolve_player_id(name)
            if not bdl_id:
                errors += 1
                continue

        try:
            profile = bdl_client.fetch_full_profile(bdl_id)
            if profile:
                db.save_player_cache(
                    player_name=name,
                    bdl_player_id=bdl_id,
                    sport_key=sport_key,
                    season_averages=profile.get("season_averages", {}),
                    recent_games=profile.get("recent_games", []),
                    advanced_stats=profile.get("advanced_stats", []),
                )
                refreshed += 1
            else:
                errors += 1
        except Exception as e:
            logger.error(f"[PlayerAnalytics] Error refreshing {name}: {e}")
            errors += 1

    logger.info(
        f"[PlayerStats] Refresh complete: {refreshed} refreshed, "
        f"{skipped} still fresh, {errors} errors (of {len(rows)} total)"
    )
    return {"refreshed": refreshed, "skipped": skipped, "errors": errors, "total": len(rows)}
