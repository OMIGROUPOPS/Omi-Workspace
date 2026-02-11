"""
Exchange Data Tracker

Fetches sports prediction market data from Kalshi and Polymarket,
stores snapshots in exchange_data table, and fuzzy-matches contracts
to our sportsbook games in cached_odds.

Called every 15 minutes by the odds sync cron via POST /api/exchange/sync.
"""
import json
import logging
import re
import statistics
from datetime import datetime, timezone
from typing import Optional

import requests

from database import db

logger = logging.getLogger(__name__)

KALSHI_API_BASE = "https://api.elections.kalshi.com/trade-api/v2"
POLYMARKET_API_BASE = "https://gamma-api.polymarket.com"

# Keywords to identify sports markets from exchange titles/categories
SPORTS_LEAGUE_KEYWORDS = [
    "nfl", "nba", "nhl", "mlb", "ncaaf", "ncaab", "nascar",
    "epl", "premier league", "mls", "la liga", "serie a", "bundesliga",
    "champions league", "uefa", "fifa", "ufc", "mma", "pga", "atp", "wta",
    "wnba", "xfl", "usfl", "cfl",
]

SPORTS_GENERIC_KEYWORDS = [
    "winner", "champion", "playoff", "playoffs", "super bowl", "world series",
    "stanley cup", "finals", "mvp", "win", "beat", "game", "match",
    "score", "touchdown", "goal", "home run", "strikeout", "rushing",
    "passing", "rebounds", "assists", "points", "series",
    "march madness", "bowl game", "all-star",
]

# Common team name fragments for initial sports detection
SPORTS_TEAM_KEYWORDS = [
    # NBA
    "lakers", "celtics", "warriors", "nets", "knicks", "bulls", "heat",
    "bucks", "76ers", "sixers", "suns", "mavericks", "mavs", "nuggets",
    "clippers", "rockets", "spurs", "grizzlies", "timberwolves", "wolves",
    "cavaliers", "cavs", "raptors", "hawks", "pacers", "magic", "hornets",
    "pistons", "wizards", "kings", "blazers", "pelicans", "thunder", "jazz",
    # NFL
    "chiefs", "eagles", "49ers", "niners", "cowboys", "bills", "ravens",
    "bengals", "dolphins", "lions", "jaguars", "jags", "chargers", "jets",
    "patriots", "pats", "steelers", "raiders", "broncos", "colts", "titans",
    "texans", "seahawks", "cardinals", "rams", "panthers", "saints",
    "falcons", "bears", "packers", "vikings", "commanders", "giants",
    "buccaneers", "bucs", "browns",
    # MLB
    "yankees", "dodgers", "red sox", "cubs", "mets", "braves", "astros",
    "phillies", "padres", "mariners", "orioles", "twins", "rangers",
    "guardians", "blue jays", "brewers", "diamondbacks", "d-backs",
    "reds", "rockies", "royals", "tigers", "white sox", "rays",
    "pirates", "marlins", "nationals", "athletics",
    # NHL
    "bruins", "avalanche", "oilers", "hurricanes", "devils", "leafs",
    "maple leafs", "rangers", "penguins", "panthers", "lightning",
    "flames", "wild", "stars", "canucks", "kraken", "senators",
    "sabres", "blackhawks", "red wings", "predators", "islanders",
    "blue jackets", "ducks", "sharks", "coyotes", "canadiens", "jets",
    "flyers", "capitals",
    # EPL / Soccer
    "arsenal", "chelsea", "liverpool", "man city", "manchester city",
    "man united", "manchester united", "tottenham", "spurs",
    "newcastle", "brighton", "aston villa", "west ham", "crystal palace",
    "wolves", "wolverhampton", "bournemouth", "fulham", "brentford",
    "nottingham forest", "everton", "burnley", "luton", "sheffield",
    "real madrid", "barcelona", "bayern", "psg", "juventus", "inter milan",
    "ac milan", "atletico madrid", "dortmund",
]

ALL_SPORTS_KEYWORDS = (
    SPORTS_LEAGUE_KEYWORDS + SPORTS_GENERIC_KEYWORDS + SPORTS_TEAM_KEYWORDS
)


def _is_sports_market(
    title: str,
    category: Optional[str] = None,
    tags: Optional[list] = None,
) -> bool:
    """Check if an exchange market is sports-related."""
    text = title.lower()
    if category:
        text += " " + category.lower()
    if tags:
        text += " " + " ".join(t.lower() for t in tags)

    for kw in ALL_SPORTS_KEYWORDS:
        if kw in text:
            return True
    return False


def _normalize_team(name: str) -> str:
    """Normalize a team name for matching."""
    name = name.lower().strip()
    name = re.sub(r"\b(the|fc|sc|cf)\b", "", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    return " ".join(name.split())


def _extract_team_fragments(title: str) -> list[str]:
    """Extract potential team name fragments from an exchange title."""
    title_lower = title.lower()
    # Remove common non-team words
    for remove in [
        "will", "the", "win", "beat", "over", "under", "vs", "vs.",
        "against", "in", "at", "on", "their", "next", "game", "match",
        "this", "season", "week", "tonight", "today", "tomorrow",
    ]:
        title_lower = re.sub(rf"\b{remove}\b", " ", title_lower)
    # Return cleaned words longer than 2 chars
    words = [w.strip() for w in title_lower.split() if len(w.strip()) > 2]
    return words


class ExchangeTracker:
    """Fetches and stores exchange sports market data."""

    def __init__(self):
        self._cached_games: Optional[list] = None

    def _load_active_games(self) -> list:
        """Load active games from cached_odds for fuzzy matching."""
        if self._cached_games is not None:
            return self._cached_games

        if not db._is_connected():
            self._cached_games = []
            return []

        now = datetime.now(timezone.utc).isoformat()
        try:
            result = (
                db.client.table("cached_odds")
                .select("game_id, sport_key, game_data")
                .gte("game_data->>commence_time", now)
                .execute()
            )
            self._cached_games = result.data or []
        except Exception as e:
            logger.error(f"[ExchangeTracker] Failed to load active games: {e}")
            self._cached_games = []

        return self._cached_games

    def _fuzzy_match_game(self, title: str) -> tuple[Optional[str], Optional[str]]:
        """Try to match an exchange title to one of our sportsbook games."""
        games = self._load_active_games()
        if not games:
            return None, None

        title_lower = title.lower()
        title_fragments = set(_extract_team_fragments(title))

        best_match = None
        best_score = 0

        for game in games:
            game_data = game.get("game_data", {})
            if not game_data:
                continue

            home = game_data.get("home_team", "")
            away = game_data.get("away_team", "")
            if not home or not away:
                continue

            home_norm = _normalize_team(home)
            away_norm = _normalize_team(away)

            # Check if team names appear in the title
            home_words = set(home_norm.split())
            away_words = set(away_norm.split())

            # Score: count matching words
            home_matches = len(home_words & title_fragments)
            away_matches = len(away_words & title_fragments)

            # Also check if the full normalized name is a substring
            if home_norm in title_lower:
                home_matches = max(home_matches, len(home_words))
            if away_norm in title_lower:
                away_matches = max(away_matches, len(away_words))

            # Need at least one word from each team, or strong single-team match
            score = home_matches + away_matches
            if home_matches > 0 and away_matches > 0:
                score += 5  # Bonus for matching both teams

            if score > best_score and score >= 2:
                best_score = score
                best_match = game

        if best_match:
            return best_match["game_id"], best_match["sport_key"]
        return None, None

    def _get_previous_price(
        self, event_id: str, exchange: str
    ) -> Optional[float]:
        """Get the most recent yes_price for this event for price_change calc."""
        if not db._is_connected():
            return None
        try:
            result = (
                db.client.table("exchange_data")
                .select("yes_price")
                .eq("event_id", event_id)
                .eq("exchange", exchange)
                .order("snapshot_time", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                return result.data[0].get("yes_price")
        except Exception:
            pass
        return None

    # =========================================================================
    # KALSHI
    # =========================================================================

    def sync_kalshi(self) -> dict:
        """Fetch sports markets from Kalshi and store in exchange_data."""
        if not db._is_connected():
            return {"error": "Database not connected", "markets_synced": 0, "errors": 0}

        now = datetime.now(timezone.utc).isoformat()
        markets_synced = 0
        sports_matched = 0
        errors = 0
        cursor = None

        try:
            while True:
                params: dict = {"status": "open", "limit": 200}
                if cursor:
                    params["cursor"] = cursor

                resp = requests.get(
                    f"{KALSHI_API_BASE}/markets",
                    params=params,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()

                markets = data.get("markets", [])
                if not markets:
                    break

                for m in markets:
                    try:
                        title = m.get("title", "") or m.get("subtitle", "")
                        category = m.get("category", "")
                        tags = m.get("tags", [])

                        if not _is_sports_market(title, category, tags):
                            continue

                        event_id = m.get("ticker", m.get("id", ""))
                        yes_price = m.get("yes_price")  # already cents
                        no_price = m.get("no_price")
                        yes_bid = m.get("yes_bid")
                        yes_ask = m.get("yes_ask")
                        no_bid = m.get("no_bid")
                        no_ask = m.get("no_ask")
                        volume = m.get("volume")
                        open_interest = m.get("open_interest")
                        last_price = m.get("last_price")
                        close_time = m.get("close_time") or m.get("expiration_time")
                        status = m.get("status", "open")
                        ticker = m.get("ticker", "")

                        prev = self._get_previous_price(event_id, "kalshi")
                        price_change = None
                        if prev is not None and yes_price is not None:
                            price_change = round(yes_price - prev, 2)

                        game_id, sport_key = self._fuzzy_match_game(title)
                        if game_id:
                            sports_matched += 1

                        row = {
                            "exchange": "kalshi",
                            "event_id": event_id,
                            "event_title": title,
                            "contract_ticker": ticker,
                            "yes_price": yes_price,
                            "no_price": no_price,
                            "yes_bid": yes_bid,
                            "yes_ask": yes_ask,
                            "no_bid": no_bid,
                            "no_ask": no_ask,
                            "volume": volume,
                            "open_interest": open_interest,
                            "last_price": last_price,
                            "previous_yes_price": prev,
                            "price_change": price_change,
                            "snapshot_time": now,
                            "mapped_game_id": game_id,
                            "mapped_sport_key": sport_key,
                            "expiration_time": close_time,
                            "status": status,
                        }
                        db.client.table("exchange_data").insert(row).execute()
                        markets_synced += 1

                    except Exception as e:
                        logger.error(f"[ExchangeTracker] Kalshi market error: {e}")
                        errors += 1

                cursor = data.get("cursor")
                if not cursor:
                    break

        except requests.RequestException as e:
            logger.error(f"[ExchangeTracker] Kalshi API error: {e}")
            errors += 1

        summary = {
            "markets_synced": markets_synced,
            "sports_matched": sports_matched,
            "errors": errors,
        }
        logger.info(f"[ExchangeTracker] Kalshi sync: {summary}")
        return summary

    # =========================================================================
    # POLYMARKET
    # =========================================================================

    def sync_polymarket(self) -> dict:
        """Fetch sports markets from Polymarket and store in exchange_data."""
        if not db._is_connected():
            return {"error": "Database not connected", "markets_synced": 0, "errors": 0}

        now = datetime.now(timezone.utc).isoformat()
        markets_synced = 0
        sports_matched = 0
        errors = 0
        offset = 0
        limit = 100

        try:
            while True:
                resp = requests.get(
                    f"{POLYMARKET_API_BASE}/markets",
                    params={
                        "active": "true",
                        "closed": "false",
                        "limit": limit,
                        "offset": offset,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                markets = resp.json()

                if not markets:
                    break

                for m in markets:
                    try:
                        title = m.get("question", "") or m.get("title", "")
                        tags_raw = m.get("tags", [])
                        tags = tags_raw if isinstance(tags_raw, list) else []

                        if not _is_sports_market(title, tags=tags):
                            continue

                        event_id = m.get("conditionId", m.get("id", ""))
                        slug = m.get("slug", "")

                        # Parse prices from outcomePrices JSON string
                        yes_price = None
                        no_price = None
                        try:
                            prices_str = m.get("outcomePrices", "")
                            if prices_str:
                                prices = json.loads(prices_str)
                                if len(prices) >= 2:
                                    yes_price = round(float(prices[0]) * 100, 1)
                                    no_price = round(float(prices[1]) * 100, 1)
                        except (json.JSONDecodeError, ValueError, IndexError):
                            pass

                        # Polymarket doesn't expose bid/ask in the markets endpoint
                        volume = m.get("volume")
                        if volume is not None:
                            try:
                                volume = int(float(volume))
                            except (ValueError, TypeError):
                                volume = None

                        open_interest = m.get("liquidity")
                        if open_interest is not None:
                            try:
                                open_interest = int(float(open_interest))
                            except (ValueError, TypeError):
                                open_interest = None

                        close_time = m.get("endDate") or m.get("expirationDate")
                        status = "open" if m.get("active") else "closed"

                        prev = self._get_previous_price(event_id, "polymarket")
                        price_change = None
                        if prev is not None and yes_price is not None:
                            price_change = round(yes_price - prev, 2)

                        game_id, sport_key = self._fuzzy_match_game(title)
                        if game_id:
                            sports_matched += 1

                        row = {
                            "exchange": "polymarket",
                            "event_id": event_id,
                            "event_title": title,
                            "contract_ticker": slug,
                            "yes_price": yes_price,
                            "no_price": no_price,
                            "yes_bid": None,
                            "yes_ask": None,
                            "no_bid": None,
                            "no_ask": None,
                            "volume": volume,
                            "open_interest": open_interest,
                            "last_price": yes_price,  # best approximation
                            "previous_yes_price": prev,
                            "price_change": price_change,
                            "snapshot_time": now,
                            "mapped_game_id": game_id,
                            "mapped_sport_key": sport_key,
                            "expiration_time": close_time,
                            "status": status,
                        }
                        db.client.table("exchange_data").insert(row).execute()
                        markets_synced += 1

                    except Exception as e:
                        logger.error(f"[ExchangeTracker] Polymarket market error: {e}")
                        errors += 1

                # Polymarket uses offset-based pagination
                if len(markets) < limit:
                    break
                offset += limit

        except requests.RequestException as e:
            logger.error(f"[ExchangeTracker] Polymarket API error: {e}")
            errors += 1

        summary = {
            "markets_synced": markets_synced,
            "sports_matched": sports_matched,
            "errors": errors,
        }
        logger.info(f"[ExchangeTracker] Polymarket sync: {summary}")
        return summary

    # =========================================================================
    # COMBINED SYNC
    # =========================================================================

    def sync_all(self) -> dict:
        """Sync both Kalshi and Polymarket sports markets."""
        logger.info("[ExchangeTracker] Starting full exchange sync")
        kalshi = self.sync_kalshi()
        polymarket = self.sync_polymarket()
        return {
            "kalshi": kalshi,
            "polymarket": polymarket,
            "total_synced": kalshi.get("markets_synced", 0) + polymarket.get("markets_synced", 0),
            "total_matched": kalshi.get("sports_matched", 0) + polymarket.get("sports_matched", 0),
        }

    # =========================================================================
    # QUERY METHODS
    # =========================================================================

    def get_markets(
        self,
        exchange: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 200,
    ) -> list:
        """
        Get latest exchange markets, deduplicated by (exchange, event_id).
        Returns most recent snapshot per event, ordered by volume DESC.
        """
        if not db._is_connected():
            return []

        try:
            query = (
                db.client.table("exchange_data")
                .select("*")
                .eq("status", "open")
                .order("snapshot_time", desc=True)
                .limit(1000)  # fetch more to deduplicate
            )

            if exchange:
                query = query.eq("exchange", exchange)

            result = query.execute()
            rows = result.data or []

            # Deduplicate by (exchange, event_id) — keep latest snapshot
            seen = set()
            deduped = []
            for row in rows:
                key = (row["exchange"], row["event_id"])
                if key not in seen:
                    seen.add(key)
                    deduped.append(row)

            # Filter by search query
            if search:
                search_lower = search.lower()
                deduped = [
                    r for r in deduped
                    if search_lower in (r.get("event_title", "") or "").lower()
                    or search_lower in (r.get("contract_ticker", "") or "").lower()
                ]

            # Sort by volume DESC (nulls last)
            deduped.sort(key=lambda r: r.get("volume") or 0, reverse=True)

            return deduped[:limit]

        except Exception as e:
            logger.error(f"[ExchangeTracker] get_markets error: {e}")
            return []

    def get_game_exchange_data(self, game_id: str) -> list:
        """
        Get exchange contracts matched to a specific game.
        Deduplicated by (exchange, event_id), latest snapshot only.
        """
        if not db._is_connected():
            return []

        try:
            result = (
                db.client.table("exchange_data")
                .select("*")
                .eq("mapped_game_id", game_id)
                .order("snapshot_time", desc=True)
                .limit(50)
                .execute()
            )
            rows = result.data or []

            # Deduplicate
            seen = set()
            deduped = []
            for row in rows:
                key = (row["exchange"], row["event_id"])
                if key not in seen:
                    seen.add(key)
                    deduped.append(row)

            return deduped

        except Exception as e:
            logger.error(f"[ExchangeTracker] get_game_exchange_data error: {e}")
            return []
