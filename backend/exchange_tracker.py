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

# Kalshi sports series tickers: (series_ticker, market_type)
# Each series = one sport + one market type. Events endpoint returns single-game events.
KALSHI_SPORTS_SERIES = [
    ("KXNBAGAME", "moneyline"),
    ("KXNBASPREAD", "spread"),
    ("KXNBATOTAL", "total"),
    ("KXNFLGAME", "moneyline"),
    ("KXNFLSPREAD", "spread"),
    ("KXNFLTOTAL", "total"),
    ("KXNCAAMBGAME", "moneyline"),
    ("KXNCAAMBSPREAD", "spread"),
    ("KXNCAAMBTOTAL", "total"),
    ("KXNHLGAME", "moneyline"),
    ("KXNHLSPREAD", "spread"),
    ("KXNHLTOTAL", "total"),
    ("KXEPLGAME", "moneyline"),
    ("KXEPLSPREAD", "spread"),
    ("KXEPLTOTAL", "total"),
]

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
        """Fetch single-game sports markets from Kalshi using the events endpoint.

        Iterates known sports series tickers (KXNBAGAME, KXNBASPREAD, etc.)
        and fetches events with nested markets. Each sub-market (team ML,
        spread line, total line) is stored as a separate row with market_type
        and subtitle for clean frontend grouping.
        """
        if not db._is_connected():
            return {"error": "Database not connected", "markets_synced": 0, "errors": 0}

        now = datetime.now(timezone.utc).isoformat()
        markets_synced = 0
        sports_matched = 0
        errors = 0
        series_fetched = 0

        for series_ticker, market_type in KALSHI_SPORTS_SERIES:
            cursor = None
            try:
                while True:
                    params: dict = {
                        "series_ticker": series_ticker,
                        "status": "open",
                        "with_nested_markets": "true",
                        "limit": 200,
                    }
                    if cursor:
                        params["cursor"] = cursor

                    resp = requests.get(
                        f"{KALSHI_API_BASE}/events",
                        params=params,
                        timeout=30,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    events = data.get("events", [])
                    if not events:
                        break

                    series_fetched += 1

                    for event in events:
                        try:
                            event_ticker = event.get("event_ticker", "")
                            event_title = event.get("title", "")

                            # Fuzzy match once per event
                            game_id, sport_key = self._fuzzy_match_game(event_title)

                            nested_markets = event.get("markets", [])
                            for m in nested_markets:
                                try:
                                    ticker = m.get("ticker", "")
                                    status = m.get("status", "open")
                                    if status != "active" and status != "open":
                                        continue

                                    yes_bid = m.get("yes_bid")
                                    yes_ask = m.get("yes_ask")
                                    no_bid = m.get("no_bid")
                                    no_ask = m.get("no_ask")
                                    last_price = m.get("last_price")
                                    volume = m.get("volume")
                                    open_interest = m.get("open_interest")
                                    subtitle = m.get("yes_sub_title", "")
                                    floor_strike = m.get("floor_strike")

                                    # Derive yes/no price from bid/ask midpoint
                                    yes_price = None
                                    no_price = None
                                    if yes_bid is not None and yes_ask is not None:
                                        yes_price = round((yes_bid + yes_ask) / 2, 1)
                                    elif last_price is not None:
                                        yes_price = last_price
                                    if no_bid is not None and no_ask is not None:
                                        no_price = round((no_bid + no_ask) / 2, 1)
                                    elif yes_price is not None:
                                        no_price = 100 - yes_price

                                    close_time = (
                                        m.get("close_time")
                                        or m.get("expiration_time")
                                        or m.get("expected_expiration_time")
                                    )

                                    prev = self._get_previous_price(event_ticker, "kalshi")
                                    price_change = None
                                    if prev is not None and yes_price is not None:
                                        price_change = round(yes_price - prev, 2)

                                    if game_id:
                                        sports_matched += 1

                                    row = {
                                        "exchange": "kalshi",
                                        "event_id": event_ticker,
                                        "event_title": event_title,
                                        "contract_ticker": ticker,
                                        "market_type": market_type,
                                        "subtitle": subtitle,
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
                                    logger.error(f"[ExchangeTracker] Kalshi market error ({ticker}): {e}")
                                    errors += 1

                        except Exception as e:
                            logger.error(f"[ExchangeTracker] Kalshi event error: {e}")
                            errors += 1

                    cursor = data.get("cursor")
                    if not cursor:
                        break

            except requests.RequestException as e:
                logger.warning(f"[ExchangeTracker] Kalshi series {series_ticker}: {e}")
                # Continue to next series even if one fails

        summary = {
            "markets_synced": markets_synced,
            "sports_matched": sports_matched,
            "series_fetched": series_fetched,
            "errors": errors,
        }
        logger.info(f"[ExchangeTracker] Kalshi sync: {summary}")
        return summary

    # =========================================================================
    # POLYMARKET
    # =========================================================================

    def sync_polymarket(self) -> dict:
        """Fetch sports markets from Polymarket and store in exchange_data.

        Uses the /events endpoint (not /markets) because:
        - Tags (Sports, NBA, etc.) only exist on event objects, not market objects
        - Events group related markets (moneyline, spread, total) together
        - We filter by tag label to find sports events, then process nested markets
        """
        if not db._is_connected():
            return {"error": "Database not connected", "markets_synced": 0, "errors": 0}

        now = datetime.now(timezone.utc).isoformat()
        markets_synced = 0
        sports_matched = 0
        errors = 0
        offset = 0
        limit = 200

        try:
            while True:
                resp = requests.get(
                    f"{POLYMARKET_API_BASE}/events",
                    params={
                        "active": "true",
                        "closed": "false",
                        "limit": limit,
                        "offset": offset,
                        "order": "volume24hr",
                        "ascending": "false",
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                events = resp.json()

                if not events:
                    break

                for event in events:
                    try:
                        event_title = event.get("title", "")
                        # Tags are objects: [{"id": "1", "label": "Sports"}, ...]
                        tags_raw = event.get("tags", [])
                        tag_labels = []
                        if isinstance(tags_raw, list):
                            for t in tags_raw:
                                if isinstance(t, dict):
                                    tag_labels.append(t.get("label", ""))
                                elif isinstance(t, str):
                                    tag_labels.append(t)

                        # Check if this event is sports-related
                        if not _is_sports_market(event_title, tags=tag_labels):
                            continue

                        # Fuzzy match the event title to our games (once per event)
                        game_id, sport_key = self._fuzzy_match_game(event_title)

                        # Process each market (contract) within this event
                        event_markets = event.get("markets", [])
                        if not event_markets:
                            continue

                        for m in event_markets:
                            try:
                                question = m.get("question", "") or m.get("groupItemTitle", "") or event_title
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

                                close_time = m.get("endDate") or m.get("expirationDate") or event.get("endDate")
                                status = "open" if m.get("active") else "closed"

                                prev = self._get_previous_price(event_id, "polymarket")
                                price_change = None
                                if prev is not None and yes_price is not None:
                                    price_change = round(yes_price - prev, 2)

                                if game_id:
                                    sports_matched += 1

                                # Use event title + market question for display
                                display_title = question if question != event_title else event_title

                                row = {
                                    "exchange": "polymarket",
                                    "event_id": event_id,
                                    "event_title": display_title,
                                    "contract_ticker": slug,
                                    "yes_price": yes_price,
                                    "no_price": no_price,
                                    "yes_bid": None,
                                    "yes_ask": None,
                                    "no_bid": None,
                                    "no_ask": None,
                                    "volume": volume,
                                    "open_interest": open_interest,
                                    "last_price": yes_price,
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

                    except Exception as e:
                        logger.error(f"[ExchangeTracker] Polymarket event error: {e}")
                        errors += 1

                # Offset-based pagination
                if len(events) < limit:
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
        limit: int = 50,
    ) -> list:
        """
        Get latest exchange markets, deduplicated by (exchange, event_id) in SQL.
        Returns most recent snapshot per event, ordered by volume DESC.
        """
        if not db._is_connected():
            return []

        # Cap limit to prevent excessive queries
        limit = min(max(1, limit), 200)

        try:
            result = db.client.rpc(
                "get_exchange_markets",
                {
                    "p_exchange": exchange,
                    "p_search": search,
                    "p_limit": limit,
                },
            ).execute()
            return result.data or []

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

            # Deduplicate by contract_ticker (unique per sub-market)
            seen = set()
            deduped = []
            for row in rows:
                key = (row["exchange"], row.get("contract_ticker") or row["event_id"])
                if key not in seen:
                    seen.add(key)
                    deduped.append(row)

            return deduped

        except Exception as e:
            logger.error(f"[ExchangeTracker] get_game_exchange_data error: {e}")
            return []
