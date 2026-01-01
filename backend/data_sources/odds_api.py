"""
Odds API Data Source
Fetches live odds, line movements, and market data from The Odds API.
"""
import httpx
from datetime import datetime, timezone
from typing import Optional
import logging

from config import (
    ODDS_API_KEY, ODDS_API_BASE, ODDS_API_SPORTS,
    MAIN_MARKETS, HALF_MARKETS, QUARTER_MARKETS_FOOTBALL, 
    QUARTER_MARKETS_BASKETBALL, PERIOD_MARKETS_HOCKEY, ALTERNATE_MARKETS,
    PREFERRED_BOOKS, PROPS_ENABLED, PROP_MARKETS
)

logger = logging.getLogger(__name__)


class OddsAPIClient:
    """Client for The Odds API."""
    
    def __init__(self):
        self.api_key = ODDS_API_KEY
        self.base_url = ODDS_API_BASE
        self.client = httpx.Client(timeout=30.0)
        self.requests_remaining = None
    
    def _request(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Make a request to the Odds API."""
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            self.requests_remaining = response.headers.get("x-requests-remaining", "?")
            logger.info(f"[Odds API] Requests remaining: {self.requests_remaining}")
            
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Odds API error: {e}")
            return None
    
    def get_requests_remaining(self) -> Optional[str]:
        """Get the number of API requests remaining this month."""
        return self.requests_remaining
    
    def get_upcoming_games(self, sport: str, markets: list[str] = None) -> list[dict]:
        """Get upcoming games for a sport with odds from multiple books."""
        sport_key = ODDS_API_SPORTS.get(sport)
        if not sport_key:
            logger.warning(f"Unknown sport: {sport}")
            return []
        
        if markets is None:
            markets = MAIN_MARKETS
        
        params = {
            "regions": "us",
            "markets": ",".join(markets),
            "oddsFormat": "american",
            "bookmakers": ",".join(PREFERRED_BOOKS),
        }
        
        games = self._request(f"sports/{sport_key}/odds", params)
        logger.info(f"Fetched {len(games) if games else 0} games for {sport}")
        return games if games else []
    
    def get_live_games(self, sport: str) -> list[dict]:
        """Get currently live games with main markets only."""
        sport_key = ODDS_API_SPORTS.get(sport)
        if not sport_key:
            return []
        
        params = {
            "regions": "us",
            "markets": ",".join(MAIN_MARKETS),
            "oddsFormat": "american",
            "bookmakers": ",".join(PREFERRED_BOOKS),
        }
        
        games = self._request(f"sports/{sport_key}/odds", params)
        
        if not games:
            return []
        
        now = datetime.now(timezone.utc)
        live_games = []
        for game in games:
            commence_time = datetime.fromisoformat(game.get("commence_time").replace("Z", "+00:00"))
            hours_since_start = (now - commence_time).total_seconds() / 3600
            if 0 <= hours_since_start <= 4:
                live_games.append(game)
        
        logger.info(f"Found {len(live_games)} live games for {sport}")
        return live_games
    
    def get_events(self, sport: str) -> list[dict]:
        """Get list of events (games) without odds - doesn't count against quota."""
        sport_key = ODDS_API_SPORTS.get(sport)
        if not sport_key:
            return []
        
        events = self._request(f"sports/{sport_key}/events")
        return events if events else []
    
    def get_event_odds(self, sport: str, event_id: str, markets: list[str]) -> Optional[dict]:
        """
        Get odds for a specific event (game) - supports ALL market types including halves/quarters.
        This is the endpoint that supports extended markets.
        """
        sport_key = ODDS_API_SPORTS.get(sport)
        if not sport_key:
            return None
        
        params = {
            "regions": "us",
            "markets": ",".join(markets),
            "oddsFormat": "american",
            "bookmakers": ",".join(PREFERRED_BOOKS),
        }
        
        result = self._request(f"sports/{sport_key}/events/{event_id}/odds", params)
        return result
    
    def get_extended_markets_for_event(self, sport: str, event_id: str) -> Optional[dict]:
        """
        Get half/quarter/period markets for a specific event.
        Uses the event odds endpoint which supports these markets.
        """
        # Determine which extended markets to fetch based on sport
        extended_markets = []
        
        # Half markets (all sports)
        extended_markets.extend(["h2h_h1", "spreads_h1", "totals_h1"])
        extended_markets.extend(["h2h_h2", "spreads_h2", "totals_h2"])
        
        # Quarter/Period markets by sport
        if sport in ["NFL", "NCAAF"]:
            extended_markets.extend(["spreads_q1", "totals_q1", "spreads_q2", "totals_q2",
                                     "spreads_q3", "totals_q3", "spreads_q4", "totals_q4"])
        elif sport in ["NBA", "NCAAB"]:
            extended_markets.extend(["spreads_q1", "totals_q1", "spreads_q2", "totals_q2",
                                     "spreads_q3", "totals_q3", "spreads_q4", "totals_q4"])
        elif sport == "NHL":
            extended_markets.extend(["spreads_p1", "totals_p1", "spreads_p2", "totals_p2",
                                     "spreads_p3", "totals_p3"])
        
        # Alternate lines
        extended_markets.extend(["alternate_spreads", "alternate_totals"])
        
        return self.get_event_odds(sport, event_id, extended_markets)
    
    def get_all_markets(self, sport: str) -> dict:
        """
        Get ALL markets for a sport:
        1. Main markets from sport odds endpoint (one call)
        2. Extended markets from event odds endpoint (one call per game)
        """
        # Step 1: Get main markets for all games
        games = self.get_upcoming_games(sport, markets=MAIN_MARKETS)
        
        if not games:
            return {"sport": sport, "games": [], "markets_fetched": MAIN_MARKETS}
        
        logger.info(f"[{sport}] Fetching extended markets for {len(games)} games...")
        
        # Step 2: For each game, fetch extended markets
        for game in games:
            event_id = game.get("id")
            if not event_id:
                continue
            
            try:
                extended = self.get_extended_markets_for_event(sport, event_id)
                
                if extended and "bookmakers" in extended:
                    # Merge extended bookmaker data into the game
                    game["extended_markets"] = extended.get("bookmakers", [])
                    logger.debug(f"Fetched extended markets for {game.get('away_team')} @ {game.get('home_team')}")
            except Exception as e:
                logger.warning(f"Failed to fetch extended markets for {event_id}: {e}")
        
        all_markets = MAIN_MARKETS + ["h1", "h2", "quarters", "alternates"]
        
        return {
            "sport": sport,
            "games": games,
            "markets_fetched": all_markets
        }
    
    def get_event_props(self, sport: str, event_id: str, markets: list[str] = None) -> Optional[dict]:
        """Get player props for a specific event. Fetches in batches of 3."""
        sport_key = ODDS_API_SPORTS.get(sport)
        if not sport_key:
            return None
        
        if markets is None:
            markets = PROP_MARKETS.get(sport, [])
        
        if not markets:
            return None
        
        props_books = ["draftkings", "fanduel"]
        bookmakers_dict = {}
        
        batch_size = 3
        for i in range(0, len(markets), batch_size):
            batch = markets[i:i + batch_size]
            
            params = {
                "regions": "us",
                "markets": ",".join(batch),
                "oddsFormat": "american",
                "bookmakers": ",".join(props_books),
            }
            
            result = self._request(f"sports/{sport_key}/events/{event_id}/odds", params)
            
            if result and "bookmakers" in result:
                for bookmaker in result["bookmakers"]:
                    book_key = bookmaker["key"]
                    if book_key not in bookmakers_dict:
                        bookmakers_dict[book_key] = {
                            "key": book_key,
                            "title": bookmaker.get("title", book_key),
                            "markets": []
                        }
                    bookmakers_dict[book_key]["markets"].extend(bookmaker.get("markets", []))
        
        if not bookmakers_dict:
            return None
        
        return {
            "id": event_id,
            "bookmakers": list(bookmakers_dict.values())
        }
    
    def get_all_props_for_sport(self, sport: str) -> list[dict]:
        """Get props for all events in a sport."""
        if not PROPS_ENABLED:
            logger.info("Props disabled in config")
            return []
        
        if sport not in PROP_MARKETS:
            logger.warning(f"No prop markets defined for {sport}")
            return []
        
        events = self.get_events(sport)
        all_props = []
        
        for event in events:
            event_id = event.get("id")
            if not event_id:
                continue
            
            props = self.get_event_props(sport, event_id)
            if props:
                all_props.append({
                    "event_id": event_id,
                    "home_team": event.get("home_team"),
                    "away_team": event.get("away_team"),
                    "commence_time": event.get("commence_time"),
                    "props": props
                })
            
            logger.info(f"Fetched props for {event.get('away_team')} @ {event.get('home_team')}")
        
        return all_props
    
    def get_single_game_props(self, sport: str, event_id: str) -> Optional[dict]:
        """Get props for a single game."""
        return self.get_event_props(sport, event_id)
    
    def parse_game_odds(self, game: dict) -> dict:
        """Parse a game's odds into a structured format."""
        parsed = {
            "game_id": game.get("id"),
            "sport_key": game.get("sport_key"),
            "home_team": game.get("home_team"),
            "away_team": game.get("away_team"),
            "commence_time": datetime.fromisoformat(game.get("commence_time").replace("Z", "+00:00")),
            "bookmakers": {},
            "markets": {
                "main": {},
                "first_half": {},
                "second_half": {},
                "quarters": {},
                "periods": {},
                "alternates": {},
            }
        }
        
        # Parse main bookmakers (from sport odds endpoint)
        for bookmaker in game.get("bookmakers", []):
            book_key = bookmaker.get("key")
            parsed["bookmakers"][book_key] = {}
            
            for market in bookmaker.get("markets", []):
                market_key = market.get("key")
                outcomes = self._parse_market_outcomes(market, parsed["home_team"], parsed["away_team"])
                
                if market_key in ["h2h", "spreads", "totals"]:
                    parsed["bookmakers"][book_key][market_key] = outcomes
        
        # Parse extended markets (from event odds endpoint)
        for bookmaker in game.get("extended_markets", []):
            book_key = bookmaker.get("key")
            
            for market in bookmaker.get("markets", []):
                market_key = market.get("key")
                outcomes = self._parse_market_outcomes(market, parsed["home_team"], parsed["away_team"])
                
                # Categorize by market type
                if "_h1" in market_key:
                    base_market = market_key.replace("_h1", "")
                    if base_market not in parsed["markets"]["first_half"]:
                        parsed["markets"]["first_half"][base_market] = {}
                    parsed["markets"]["first_half"][base_market][book_key] = outcomes
                    
                elif "_h2" in market_key:
                    base_market = market_key.replace("_h2", "")
                    if base_market not in parsed["markets"]["second_half"]:
                        parsed["markets"]["second_half"][base_market] = {}
                    parsed["markets"]["second_half"][base_market][book_key] = outcomes
                    
                elif "_q" in market_key:
                    parts = market_key.split("_q")
                    base_market = parts[0]
                    quarter = f"q{parts[1]}"
                    if quarter not in parsed["markets"]["quarters"]:
                        parsed["markets"]["quarters"][quarter] = {}
                    if base_market not in parsed["markets"]["quarters"][quarter]:
                        parsed["markets"]["quarters"][quarter][base_market] = {}
                    parsed["markets"]["quarters"][quarter][base_market][book_key] = outcomes
                    
                elif "_p" in market_key:
                    parts = market_key.split("_p")
                    base_market = parts[0]
                    period = f"p{parts[1]}"
                    if period not in parsed["markets"]["periods"]:
                        parsed["markets"]["periods"][period] = {}
                    if base_market not in parsed["markets"]["periods"][period]:
                        parsed["markets"]["periods"][period][base_market] = {}
                    parsed["markets"]["periods"][period][base_market][book_key] = outcomes
                    
                elif market_key == "alternate_spreads":
                    if "spreads" not in parsed["markets"]["alternates"]:
                        parsed["markets"]["alternates"]["spreads"] = []
                    for outcome in market.get("outcomes", []):
                        parsed["markets"]["alternates"]["spreads"].append({
                            "team": outcome.get("name"),
                            "line": outcome.get("point"),
                            "odds": outcome.get("price"),
                            "book": book_key
                        })
                        
                elif market_key == "alternate_totals":
                    if "totals" not in parsed["markets"]["alternates"]:
                        parsed["markets"]["alternates"]["totals"] = []
                    for outcome in market.get("outcomes", []):
                        parsed["markets"]["alternates"]["totals"].append({
                            "type": outcome.get("name"),
                            "line": outcome.get("point"),
                            "odds": outcome.get("price"),
                            "book": book_key
                        })
        
        return parsed
    
    def _parse_market_outcomes(self, market: dict, home_team: str, away_team: str) -> dict:
        """Parse outcomes from a market into a structured format."""
        market_key = market.get("key")
        outcomes = {}
        
        for outcome in market.get("outcomes", []):
            name = outcome.get("name")
            price = outcome.get("price")
            point = outcome.get("point")
            
            if market_key == "h2h" or market_key.startswith("h2h_"):
                if name == home_team:
                    outcomes["home"] = price
                elif name == away_team:
                    outcomes["away"] = price
                else:
                    outcomes[name.lower()] = price
            
            elif market_key == "spreads" or market_key.startswith("spreads_"):
                if name == home_team:
                    outcomes["home"] = {"line": point, "odds": price}
                else:
                    outcomes["away"] = {"line": point, "odds": price}
            
            elif market_key == "totals" or market_key.startswith("totals_"):
                outcomes[name.lower()] = {"line": point, "odds": price}
        
        return outcomes
    
    def parse_props(self, props_data: dict, home_team: str = None, away_team: str = None) -> list[dict]:
        """Parse props response into structured format."""
        if not props_data:
            return []
        
        parsed_props = []
        
        for bookmaker in props_data.get("bookmakers", []):
            book_key = bookmaker.get("key")
            
            for market in bookmaker.get("markets", []):
                market_key = market.get("key")
                
                players = {}
                for outcome in market.get("outcomes", []):
                    player = outcome.get("description", "Unknown")
                    outcome_type = outcome.get("name", "").lower()
                    line = outcome.get("point")
                    odds = outcome.get("price")
                    
                    if player not in players:
                        players[player] = {
                            "player": player,
                            "book": book_key,
                            "market": market_key,
                            "line": line,
                        }
                    
                    if outcome_type == "over":
                        players[player]["over"] = {"odds": odds, "line": line}
                    elif outcome_type == "under":
                        players[player]["under"] = {"odds": odds, "line": line}
                    else:
                        players[player]["yes"] = {"odds": odds}
                
                parsed_props.extend(players.values())
        
        return parsed_props
    
    def calculate_consensus_odds(self, game: dict) -> dict:
        """Calculate consensus (average) odds across all bookmakers, including extended markets."""
        parsed = self.parse_game_odds(game)
        bookmakers = parsed["bookmakers"]
        markets = parsed["markets"]
        
        if not bookmakers:
            return {}
        
        consensus = {
            "h2h": {},
            "spreads": {},
            "totals": {},
            "first_half": {},
            "second_half": {},
            "quarters": {},
            "periods": {},
        }
        
        # Main markets consensus
        home_odds = [b["h2h"]["home"] for b in bookmakers.values() if "h2h" in b and "home" in b["h2h"]]
        away_odds = [b["h2h"]["away"] for b in bookmakers.values() if "h2h" in b and "away" in b["h2h"]]
        
        if home_odds:
            consensus["h2h"]["home"] = round(sum(home_odds) / len(home_odds))
        if away_odds:
            consensus["h2h"]["away"] = round(sum(away_odds) / len(away_odds))
        
        home_spreads = [b["spreads"]["home"] for b in bookmakers.values() if "spreads" in b and "home" in b["spreads"]]
        if home_spreads:
            avg_line = sum(s["line"] for s in home_spreads) / len(home_spreads)
            avg_odds = sum(s["odds"] for s in home_spreads) / len(home_spreads)
            consensus["spreads"]["home"] = {"line": round(avg_line * 2) / 2, "odds": round(avg_odds)}
            consensus["spreads"]["away"] = {"line": -round(avg_line * 2) / 2, "odds": round(avg_odds)}
        
        over_totals = [b["totals"]["over"] for b in bookmakers.values() if "totals" in b and "over" in b["totals"]]
        if over_totals:
            avg_line = sum(t["line"] for t in over_totals) / len(over_totals)
            avg_odds = sum(t["odds"] for t in over_totals) / len(over_totals)
            consensus["totals"]["over"] = {"line": round(avg_line * 2) / 2, "odds": round(avg_odds)}
            consensus["totals"]["under"] = {"line": round(avg_line * 2) / 2, "odds": round(avg_odds)}
        
        # First half consensus
        consensus["first_half"] = self._calculate_period_consensus(markets.get("first_half", {}))
        
        # Second half consensus
        consensus["second_half"] = self._calculate_period_consensus(markets.get("second_half", {}))
        
        # Quarters consensus
        for quarter, quarter_markets in markets.get("quarters", {}).items():
            consensus["quarters"][quarter] = self._calculate_period_consensus(quarter_markets)
        
        # Periods consensus (NHL)
        for period, period_markets in markets.get("periods", {}).items():
            consensus["periods"][period] = self._calculate_period_consensus(period_markets)
        
        return consensus
    
    def _calculate_period_consensus(self, period_markets: dict) -> dict:
        """Calculate consensus for a specific period (half, quarter, etc.)."""
        consensus = {}
        
        for market_type, books_data in period_markets.items():
            if not books_data:
                continue
            
            if market_type == "h2h":
                home_odds = [b.get("home") for b in books_data.values() if b.get("home")]
                away_odds = [b.get("away") for b in books_data.values() if b.get("away")]
                
                if home_odds:
                    consensus["h2h"] = {
                        "home": round(sum(home_odds) / len(home_odds)),
                        "away": round(sum(away_odds) / len(away_odds)) if away_odds else None
                    }
            
            elif market_type == "spreads":
                home_spreads = [b.get("home") for b in books_data.values() if b.get("home") and isinstance(b.get("home"), dict)]
                
                if home_spreads:
                    avg_line = sum(s["line"] for s in home_spreads) / len(home_spreads)
                    avg_odds = sum(s["odds"] for s in home_spreads) / len(home_spreads)
                    consensus["spreads"] = {
                        "home": {"line": round(avg_line * 2) / 2, "odds": round(avg_odds)},
                        "away": {"line": -round(avg_line * 2) / 2, "odds": round(avg_odds)}
                    }
            
            elif market_type == "totals":
                over_totals = [b.get("over") for b in books_data.values() if b.get("over") and isinstance(b.get("over"), dict)]
                
                if over_totals:
                    avg_line = sum(t["line"] for t in over_totals) / len(over_totals)
                    avg_odds = sum(t["odds"] for t in over_totals) / len(over_totals)
                    consensus["totals"] = {
                        "over": {"line": round(avg_line * 2) / 2, "odds": round(avg_odds)},
                        "under": {"line": round(avg_line * 2) / 2, "odds": round(avg_odds)}
                    }
        
        return consensus
    
    def get_line_movement_indicators(self, game: dict) -> dict:
        """Analyze line movement patterns across bookmakers."""
        parsed = self.parse_game_odds(game)
        bookmakers = parsed["bookmakers"]
        
        if len(bookmakers) < 2:
            return {
                "spread_variance": 0,
                "odds_variance": 0,
                "book_count": len(bookmakers),
                "outlier_books": []
            }
        
        spread_lines = []
        for book_key, markets in bookmakers.items():
            if "spreads" in markets and "home" in markets["spreads"]:
                spread_lines.append({
                    "book": book_key,
                    "line": markets["spreads"]["home"]["line"]
                })
        
        if len(spread_lines) < 2:
            return {
                "spread_variance": 0,
                "odds_variance": 0,
                "book_count": len(bookmakers),
                "outlier_books": []
            }
        
        lines = [s["line"] for s in spread_lines]
        avg_line = sum(lines) / len(lines)
        variance = sum((l - avg_line) ** 2 for l in lines) / len(lines)
        
        outliers = [s["book"] for s in spread_lines if abs(s["line"] - avg_line) > 1.0]
        
        return {
            "spread_variance": round(variance, 3),
            "odds_variance": 0,
            "book_count": len(bookmakers),
            "outlier_books": outliers,
            "consensus_line": round(avg_line * 2) / 2
        }


odds_client = OddsAPIClient()