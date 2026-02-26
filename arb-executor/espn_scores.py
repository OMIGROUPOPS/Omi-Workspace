"""ESPN live scores integration for the arb executor.

Polls ESPN's public scoreboard API for CBB, NBA, and NHL games,
matches them to our verified_mappings, and provides live game data
(scores, clock, period, game status) for the dashboard.

Usage:
    espn = ESPNScores()
    # In main loop:
    await espn.poll(session, VERIFIED_MAPS)
    # In dashboard_push:
    data = espn.get("cbb:UK-AKR:2026-02-27")
"""

import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any

import aiohttp

logger = logging.getLogger("espn_scores")

# ESPN scoreboard endpoints (public, no auth required)
ENDPOINTS = {
    "CBB": "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard",
    "NBA": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
    "NHL": "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard",
}

POLL_INTERVAL = 45  # seconds

# Eastern time offset (simplified — doesn't handle DST boundary)
ET = timezone(timedelta(hours=-5))


def _normalize(name: str) -> str:
    """Normalize team name for fuzzy matching."""
    return (
        name.lower()
        .replace(".", "")
        .replace("'", "")
        .replace("-", " ")
        .replace("  ", " ")
        .strip()
    )


class ESPNScores:
    """Fetches and caches ESPN live game data, matched to our cache_keys."""

    def __init__(self):
        self.game_data: Dict[str, dict] = {}  # cache_key -> game info
        self._last_poll: float = 0
        self._team_lookup: Dict[str, tuple] = {}  # normalized name -> (cache_key, team_abbr)
        self._lookup_built = False

    def build_team_lookup(self, verified_maps: dict):
        """Build reverse lookup from team full names to (cache_key, team_abbr).

        verified_maps: {cache_key: {team_names: {abbr: full_name}, ...}}
        """
        self._team_lookup.clear()
        for cache_key, game in verified_maps.items():
            team_names = game.get("team_names", {})
            for abbr, full_name in team_names.items():
                norm = _normalize(full_name)
                if norm:
                    self._team_lookup[norm] = (cache_key, abbr)
        self._lookup_built = True
        logger.info(f"ESPN team lookup built: {len(self._team_lookup)} entries")

    def _match_team(self, espn_team: dict) -> Optional[tuple]:
        """Match an ESPN team dict to (cache_key, our_abbr) or None."""
        # Try shortDisplayName (most reliable — "Kentucky", "Akron")
        short = _normalize(espn_team.get("shortDisplayName", ""))
        if short and short in self._team_lookup:
            return self._team_lookup[short]

        # Try full displayName ("Kentucky Wildcats")
        display = _normalize(espn_team.get("displayName", ""))
        if display and display in self._team_lookup:
            return self._team_lookup[display]

        # Containment: our name in ESPN name or vice versa
        for our_name, info in self._team_lookup.items():
            if len(our_name) >= 4 and len(display) >= 4:
                if our_name in display or display in our_name:
                    return info

        return None

    async def poll(self, session: aiohttp.ClientSession, verified_maps: dict):
        """Poll ESPN scoreboards. Call from main loop; self-throttles."""
        now = time.time()
        if now - self._last_poll < POLL_INTERVAL:
            return
        self._last_poll = now

        if not self._lookup_built:
            self.build_team_lookup(verified_maps)

        new_data: Dict[str, dict] = {}

        for sport, url in ENDPOINTS.items():
            try:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=8)
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"ESPN {sport} HTTP {resp.status}")
                        continue
                    data = await resp.json()
            except Exception as e:
                logger.warning(f"ESPN {sport} fetch error: {e}")
                continue

            for event in data.get("events", []):
                self._process_event(event, sport, new_data)

        # Merge — keeps stale entries for games no longer in today's scoreboard
        self.game_data.update(new_data)

        if new_data:
            live = sum(1 for g in new_data.values() if g.get("game_status") == "in")
            logger.debug(f"ESPN: {len(new_data)} matched ({live} live)")

    def _process_event(self, event: dict, sport: str, out: dict):
        """Parse one ESPN event and try to match it to our cache_keys."""
        status = event.get("status", {})
        state = status.get("type", {}).get("state", "pre")  # pre / in / post
        display_clock = status.get("displayClock", "")
        period = status.get("period", 0)

        competitions = event.get("competitions", [])
        if not competitions:
            return
        comp = competitions[0]
        competitors = comp.get("competitors", [])
        if len(competitors) < 2:
            return

        # Index competitors by home/away
        by_ha: Dict[str, dict] = {}
        for c in competitors:
            by_ha[c.get("homeAway", "")] = c

        home = by_ha.get("home")
        away = by_ha.get("away")
        if not home or not away:
            return

        # Match both teams
        home_match = self._match_team(home.get("team", {}))
        away_match = self._match_team(away.get("team", {}))

        # Need at least one match
        if not home_match and not away_match:
            return

        # If both match, they must agree on cache_key
        if home_match and away_match:
            if home_match[0] != away_match[0]:
                return  # ambiguous
            matched_key = home_match[0]
        else:
            matched_key = (home_match or away_match)[0]

        # Start time in ET
        game_time = ""
        raw_date = event.get("date", "")
        if raw_date:
            try:
                dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                et = dt.astimezone(ET)
                game_time = et.strftime("%I:%M %p").lstrip("0")  # "7:00 PM"
            except Exception:
                pass

        # Period label by sport
        period_label = self._period_label(state, sport, period)

        # Scores
        home_score = int(home.get("score", "0") or "0")
        away_score = int(away.get("score", "0") or "0")

        # Map scores to our team1 / team2 ordering
        ck_parts = matched_key.split(":")
        teams_str = ck_parts[1] if len(ck_parts) >= 2 else ""
        ck_teams = teams_str.split("-")
        team1_abbr = ck_teams[0] if len(ck_teams) >= 1 else ""

        t1_score, t2_score = self._assign_scores(
            home_match, away_match, matched_key, team1_abbr,
            home_score, away_score,
        )

        out[matched_key] = {
            "game_status": state,
            "game_time": game_time,
            "period": period_label,
            "clock": display_clock if state == "in" else "",
            "team1_score": t1_score,
            "team2_score": t2_score,
        }

    @staticmethod
    def _period_label(state: str, sport: str, period: int) -> str:
        if state == "post":
            return "FINAL"
        if state != "in" or period <= 0:
            return ""
        if sport == "CBB":
            if period <= 2:
                return f"{period}H"
            return f"OT{period - 2}" if period > 3 else "OT"
        if sport == "NBA":
            if period <= 4:
                return f"{period}Q"
            return f"OT{period - 4}" if period > 5 else "OT"
        if sport == "NHL":
            if period <= 3:
                return f"{period}P"
            return f"OT{period - 3}" if period > 4 else "OT"
        return str(period)

    @staticmethod
    def _assign_scores(
        home_match, away_match, matched_key, team1_abbr,
        home_score, away_score,
    ):
        """Figure out which ESPN score maps to team1 vs team2."""
        # If we matched the home team to one of ours, use its abbr
        if home_match and home_match[0] == matched_key:
            if home_match[1] == team1_abbr:
                return home_score, away_score
            else:
                return away_score, home_score
        if away_match and away_match[0] == matched_key:
            if away_match[1] == team1_abbr:
                return away_score, home_score
            else:
                return home_score, away_score
        return 0, 0

    def get(self, cache_key: str) -> Optional[dict]:
        """Get ESPN data for a cache_key, or None."""
        return self.game_data.get(cache_key)

    def rebuild_lookup(self, verified_maps: dict):
        """Force rebuild the team lookup (e.g. after mappings reload)."""
        self.build_team_lookup(verified_maps)
