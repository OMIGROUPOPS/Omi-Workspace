"""
BallDontLie (BDL) API Client

Fetches NBA player stats for prop analytics:
- Player search
- Season averages
- Game logs (recent games)
- Advanced stats
- Injury reports

Rate limited to 550 req/min (soft cap under 600/min API limit).
All errors return None — never crashes the caller.
"""
import time
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def _get_api_key():
    return os.getenv("BALLDONTLIE_API_KEY", "")

BDL_BASE = "https://api.balldontlie.io/nba/v1"
CURRENT_SEASON = 2025  # 2024-25 NBA season


class _RateLimiter:
    """Simple token-bucket rate limiter: max `rate` calls per 60 seconds."""

    def __init__(self, rate: int = 550):
        self.rate = rate
        self.tokens = rate
        self.last_refill = time.monotonic()

    def wait(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / 60.0))
        self.last_refill = now
        if self.tokens < 1:
            sleep_time = (1 - self.tokens) * (60.0 / self.rate)
            time.sleep(sleep_time)
            self.tokens = 0
        else:
            self.tokens -= 1


class BDLClient:
    """BallDontLie API client with rate limiting and error handling."""

    def __init__(self):
        self.session = requests.Session()
        self.limiter = _RateLimiter(550)

    def _get(self, path: str, params: Optional[dict] = None) -> Optional[dict]:
        """Make a rate-limited GET request. Returns JSON or None on failure."""
        api_key = _get_api_key()
        if not api_key:
            logger.warning("[BDL] API key not set — skipping request")
            return None
        self.limiter.wait()
        url = f"{BDL_BASE}{path}"
        try:
            resp = self.session.get(url, params=params or {}, timeout=10, headers={"Authorization": api_key})
            logger.info(f"[BDL] GET {resp.url} -> {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"[BDL] Request failed: {url} — {e}")
            return None

    # -----------------------------------------------------------------
    # Player search
    # -----------------------------------------------------------------
    def search_player(self, name: str) -> Optional[dict]:
        """Search for a player by name. Searches first name, filters by last name."""
        parts = name.strip().split()
        first = parts[0] if parts else name
        last = parts[-1].lower() if len(parts) >= 2 else None

        logger.info(f"[BDL] Searching first='{first}', filtering last='{last}'")
        data = self._get("/players", {"search": first, "per_page": 25})
        if not data or not data.get("data"):
            logger.warning(f"[BDL] No results for search '{first}'")
            return None

        # Exact full-name match first
        for player in data["data"]:
            full = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
            if full.lower() == name.lower():
                logger.info(f"[BDL] Found exact match: {full} (id={player['id']})")
                return player

        # Fallback: match last name only
        if last:
            for player in data["data"]:
                if player.get("last_name", "").lower() == last:
                    full = f"{player.get('first_name', '')} {player.get('last_name', '')}".strip()
                    logger.info(f"[BDL] Last-name match: {full} (id={player['id']})")
                    return player

        logger.warning(f"[BDL] No matching player for '{name}' in {len(data['data'])} results")
        return None

    # -----------------------------------------------------------------
    # Season averages
    # -----------------------------------------------------------------
    def get_season_averages(self, player_id: int, season: int = CURRENT_SEASON) -> Optional[dict]:
        """Get season averages for a player."""
        data = self._get("/season_averages", {
            "season": season,
            "player_id": player_id,
        })
        if not data or not data.get("data"):
            return None
        row = data["data"][0] if data["data"] else None
        if row:
            logger.info(f"[BDL] Season avg: pts={row.get('pts')}, reb={row.get('reb')}, ast={row.get('ast')}, min={row.get('min')}, games={row.get('games_played')}")
        return row

    # -----------------------------------------------------------------
    # Game logs (recent games)
    # -----------------------------------------------------------------
    def get_game_logs(self, player_id: int, season: int = CURRENT_SEASON, limit: int = 15) -> Optional[list]:
        """Get recent game logs for a player. Returns list of stat lines, most recent first.

        Fetches all season games, filters out DNP entries, sorts by date descending,
        and returns the most recent `limit` games actually played.
        """
        data = self._get("/stats", {
            "player_ids[]": player_id,
            "seasons[]": season,
            "per_page": 100,
        })
        if not data or not data.get("data"):
            return None

        raw = data["data"]

        # Filter out DNP entries — games where player logged 0 minutes
        played = []
        for g in raw:
            m = g.get("min")
            # BDL returns min as "MM:SS" string; "00" or "00:00" means DNP
            if m is None:
                continue
            m_str = str(m).strip()
            if m_str in ("00", "0", "00:00", "0:00", ""):
                continue
            played.append(g)

        # Sort by game date descending (most recent first)
        def game_date(g):
            try:
                return g.get("game", {}).get("date", "")
            except Exception:
                return ""
        played.sort(key=game_date, reverse=True)

        games = played[:limit]
        logger.info(f"[BDL] {len(raw)} raw entries, {len(played)} played, returning {len(games)} most recent")
        if games:
            g = games[0]
            logger.info(f"[BDL] Most recent: date={game_date(g)}, pts={g.get('pts')}, reb={g.get('reb')}, ast={g.get('ast')}, min={g.get('min')}")
        return games

    # -----------------------------------------------------------------
    # Advanced stats
    # -----------------------------------------------------------------
    def get_advanced_stats(self, player_id: int, season: int = CURRENT_SEASON) -> Optional[list]:
        """Get advanced stats for a player."""
        data = self._get("/stats/advanced", {
            "player_ids[]": player_id,
            "seasons[]": season,
            "per_page": 5,
        })
        if not data or not data.get("data"):
            return None
        return data["data"]

    # -----------------------------------------------------------------
    # Injuries
    # -----------------------------------------------------------------
    def get_injuries(self) -> Optional[list]:
        """Get current injury report."""
        data = self._get("/player_injuries")
        if not data or not data.get("data"):
            return None
        return data["data"]

    # -----------------------------------------------------------------
    # Full profile (combined fetch)
    # -----------------------------------------------------------------
    def fetch_full_profile(self, player_id: int) -> Optional[dict]:
        """Fetch season averages + recent game logs + advanced stats in one go."""
        season_avg = self.get_season_averages(player_id)
        game_logs = self.get_game_logs(player_id)
        advanced = self.get_advanced_stats(player_id)

        if season_avg is None and game_logs is None:
            return None

        return {
            "season_averages": season_avg or {},
            "recent_games": game_logs or [],
            "advanced_stats": advanced or [],
        }


# Singleton
bdl_client = BDLClient()
