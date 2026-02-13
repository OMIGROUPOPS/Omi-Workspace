"""
Supabase Database Module

Handles all database operations:
- Storing predictions
- Storing line snapshots
- Storing props and prop snapshots
- Storing weather data
- Tracking results
"""
from datetime import datetime, timezone
from typing import Optional
import logging
import json

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)


class Database:
    """Supabase database client for OMI Edge."""
    
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.warning("Supabase credentials not configured")
            self.client = None
        else:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def _is_connected(self) -> bool:
        return self.client is not None
    
    # =========================================================================
    # PREDICTIONS
    # =========================================================================
    
    def save_prediction(self, analysis: dict) -> Optional[str]:
        """Save a game analysis/prediction to the database."""
        if not self._is_connected():
            logger.warning("Database not connected, skipping save")
            return None

        try:
            # Check if new consensus_odds is empty - if so, preserve existing data
            new_consensus = analysis.get("consensus_odds", {})
            consensus_has_data = bool(new_consensus.get("h2h") or new_consensus.get("spreads") or new_consensus.get("totals"))

            consensus_to_save = new_consensus
            if not consensus_has_data:
                # Try to preserve existing consensus_odds_json if it has data
                existing = self.client.table("predictions").select("consensus_odds_json").eq(
                    "game_id", analysis["game_id"]
                ).eq("sport_key", analysis["sport"]).limit(1).execute()

                if existing.data:
                    existing_json = existing.data[0].get("consensus_odds_json", "{}")
                    try:
                        existing_consensus = json.loads(existing_json) if isinstance(existing_json, str) else existing_json
                        if existing_consensus.get("h2h") or existing_consensus.get("spreads") or existing_consensus.get("totals"):
                            consensus_to_save = existing_consensus
                            logger.debug(f"Preserving existing consensus_odds for {analysis['game_id']}")
                    except:
                        pass

            record = {
                "game_id": analysis["game_id"],
                "sport_key": analysis["sport"],
                "home_team": analysis["home_team"],
                "away_team": analysis["away_team"],
                "commence_time": analysis["commence_time"],
                "pillar_execution": analysis["pillar_scores"]["execution"],
                "pillar_incentives": analysis["pillar_scores"]["incentives"],
                "pillar_shocks": analysis["pillar_scores"]["shocks"],
                "pillar_time_decay": analysis["pillar_scores"]["time_decay"],
                "pillar_flow": analysis["pillar_scores"]["flow"],
                "composite_score": analysis["composite_score"],
                "best_bet_market": analysis.get("best_bet"),
                "best_edge_pct": analysis.get("best_edge", 0),
                "overall_confidence": analysis.get("overall_confidence", "PASS"),
                "edges_json": json.dumps(analysis.get("edges", {})),
                "pillars_json": json.dumps(analysis.get("pillars", {})),
                "consensus_odds_json": json.dumps(consensus_to_save),
                "predicted_at": datetime.now(timezone.utc).isoformat(),
            }
            
            result = self.client.table("predictions").upsert(
                record,
                on_conflict="game_id,sport_key"
            ).execute()
            
            if result.data:
                return result.data[0].get("id")
            return None
            
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return None
    
    def save_predictions_batch(self, analyses: list[dict]) -> int:
        """Save multiple predictions in batch."""
        saved = 0
        for analysis in analyses:
            if self.save_prediction(analysis):
                saved += 1
        return saved
    
    def get_prediction(self, game_id: str, sport: str) -> Optional[dict]:
        """Get the latest prediction for a game."""
        if not self._is_connected():
            return None
        
        try:
            result = self.client.table("predictions").select("*").eq(
                "game_id", game_id
            ).eq(
                "sport_key", sport
            ).order(
                "predicted_at", desc=True
            ).limit(1).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting prediction: {e}")
            return None
    
    def get_all_predictions_for_sport(self, sport: str) -> list[dict]:
        """
        Get all predictions for a sport with upcoming games.
        Returns predictions formatted for the frontend.
        """
        if not self._is_connected():
            return []
        
        try:
            result = self.client.table("predictions").select("*").eq(
                "sport_key", sport
            ).gte(
                "commence_time", datetime.now(timezone.utc).isoformat()
            ).order(
                "commence_time", desc=False
            ).execute()
            
            predictions = result.data or []
            
            # Transform to match frontend expectations
            formatted = []
            for pred in predictions:
                # Parse JSON fields
                edges_json = pred.get("edges_json", "{}")
                pillars_json = pred.get("pillars_json", "{}")
                consensus_json = pred.get("consensus_odds_json", "{}")
                
                try:
                    edges = json.loads(edges_json) if isinstance(edges_json, str) else edges_json
                except:
                    edges = {}
                
                try:
                    pillars = json.loads(pillars_json) if isinstance(pillars_json, str) else pillars_json
                except:
                    pillars = {}
                
                try:
                    consensus_odds = json.loads(consensus_json) if isinstance(consensus_json, str) else consensus_json
                except:
                    consensus_odds = {}
                
                formatted.append({
                    "game_id": pred.get("game_id"),
                    "sport": pred.get("sport_key"),
                    "home_team": pred.get("home_team"),
                    "away_team": pred.get("away_team"),
                    "commence_time": pred.get("commence_time"),
                    "pillar_scores": {
                        "execution": pred.get("pillar_execution", 0.5),
                        "incentives": pred.get("pillar_incentives", 0.5),
                        "shocks": pred.get("pillar_shocks", 0.5),
                        "time_decay": pred.get("pillar_time_decay", 0.5),
                        "flow": pred.get("pillar_flow", 0.5),
                    },
                    "composite_score": pred.get("composite_score", 0.5),
                    "best_bet": pred.get("best_bet_market"),
                    "best_edge": pred.get("best_edge_pct", 0),
                    "overall_confidence": pred.get("overall_confidence", "PASS"),
                    "edges": edges,
                    "pillars": pillars,
                    "consensus_odds": consensus_odds,
                    "predicted_at": pred.get("predicted_at"),
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error getting predictions for sport {sport}: {e}")
            return []
    
    def get_active_edges(self, min_confidence: str = "WATCH") -> list[dict]:
        """Get all active edges above a confidence threshold."""
        if not self._is_connected():
            return []
        
        confidence_levels = ["PASS", "WATCH", "EDGE", "STRONG", "RARE"]
        min_index = confidence_levels.index(min_confidence)
        valid_confidences = confidence_levels[min_index:]
        
        try:
            result = self.client.table("predictions").select("*").in_(
                "overall_confidence", valid_confidences
            ).gte(
                "commence_time", datetime.now(timezone.utc).isoformat()
            ).order(
                "best_edge_pct", desc=True
            ).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting active edges: {e}")
            return []
    
    # =========================================================================
    # LINE SNAPSHOTS
    # =========================================================================
    
    def save_line_snapshot(
        self,
        game_id: str,
        sport: str,
        market_type: str,
        book_key: str,
        line: float,
        odds: int,
        implied_prob: float,
        market_period: str = "full",  # full, h1, h2, q1, q2, q3, q4, p1, p2, p3
        outcome_type: Optional[str] = None  # home, away, over, under, or team name
    ) -> bool:
        """Save a single line snapshot."""
        if not self._is_connected():
            return False

        try:
            record = {
                "game_id": game_id,
                "sport_key": sport,
                "market_type": market_type,
                "market_period": market_period,
                "book_key": book_key,
                "line": line,
                "odds": odds,
                "implied_prob": implied_prob,
                "snapshot_time": datetime.now(timezone.utc).isoformat(),
            }

            # Add outcome_type if provided
            if outcome_type:
                record["outcome_type"] = outcome_type

            self.client.table("line_snapshots").insert(record).execute()
            return True

        except Exception as e:
            logger.error(f"Error saving line snapshot: {e}")
            return False
    
    def save_game_snapshots(self, game: dict, sport: str) -> int:
        """Save line snapshots for all markets in a game."""
        from data_sources.odds_api import odds_client
        from engine.analyzer import american_to_implied_prob
        
        parsed = odds_client.parse_game_odds(game)
        game_id = parsed["game_id"]
        saved = 0
        
        # =====================================================================
        # MAIN MARKETS (full game)
        # =====================================================================
        for book_key, markets in parsed["bookmakers"].items():
            # Spreads
            if "spreads" in markets and "home" in markets["spreads"]:
                spread = markets["spreads"]["home"]
                if self.save_line_snapshot(
                    game_id=game_id,
                    sport=sport,
                    market_type="spread",
                    book_key=book_key,
                    line=spread["line"],
                    odds=spread["odds"],
                    implied_prob=american_to_implied_prob(spread["odds"]),
                    market_period="full",
                    outcome_type="home"
                ):
                    saved += 1
            
            # Moneyline - save BOTH home and away
            if "h2h" in markets:
                # Save home ML
                if "home" in markets["h2h"] and markets["h2h"]["home"]:
                    ml_home = markets["h2h"]["home"]
                    if self.save_line_snapshot(
                        game_id=game_id,
                        sport=sport,
                        market_type="moneyline",
                        book_key=book_key,
                        line=0,
                        odds=ml_home,
                        implied_prob=american_to_implied_prob(ml_home),
                        market_period="full",
                        outcome_type="home"
                    ):
                        saved += 1
                # Save away ML
                if "away" in markets["h2h"] and markets["h2h"]["away"]:
                    ml_away = markets["h2h"]["away"]
                    if self.save_line_snapshot(
                        game_id=game_id,
                        sport=sport,
                        market_type="moneyline",
                        book_key=book_key,
                        line=0,
                        odds=ml_away,
                        implied_prob=american_to_implied_prob(ml_away),
                        market_period="full",
                        outcome_type="away"
                    ):
                        saved += 1
                # Save draw ML (soccer 3-way)
                if "draw" in markets["h2h"] and markets["h2h"]["draw"]:
                    ml_draw = markets["h2h"]["draw"]
                    if self.save_line_snapshot(
                        game_id=game_id,
                        sport=sport,
                        market_type="moneyline",
                        book_key=book_key,
                        line=0,
                        odds=ml_draw,
                        implied_prob=american_to_implied_prob(ml_draw),
                        market_period="full",
                        outcome_type="Draw"
                    ):
                        saved += 1

            # Totals
            if "totals" in markets and "over" in markets["totals"]:
                total = markets["totals"]["over"]
                if self.save_line_snapshot(
                    game_id=game_id,
                    sport=sport,
                    market_type="total",
                    book_key=book_key,
                    line=total["line"],
                    odds=total["odds"],
                    implied_prob=american_to_implied_prob(total["odds"]),
                    market_period="full"
                ):
                    saved += 1
        
        # =====================================================================
        # EXTENDED MARKETS (halves, quarters, periods)
        # =====================================================================
        markets_data = parsed.get("markets", {})
        
        # First Half (h1)
        first_half = markets_data.get("first_half", {})
        saved += self._save_period_snapshots(game_id, sport, "h1", first_half, american_to_implied_prob)
        
        # Second Half (h2)
        second_half = markets_data.get("second_half", {})
        saved += self._save_period_snapshots(game_id, sport, "h2", second_half, american_to_implied_prob)
        
        # Quarters (q1, q2, q3, q4)
        quarters = markets_data.get("quarters", {})
        for quarter_key, quarter_markets in quarters.items():
            saved += self._save_period_snapshots(game_id, sport, quarter_key, quarter_markets, american_to_implied_prob)
        
        # Periods for NHL (p1, p2, p3)
        periods = markets_data.get("periods", {})
        for period_key, period_markets in periods.items():
            saved += self._save_period_snapshots(game_id, sport, period_key, period_markets, american_to_implied_prob)

        # =====================================================================
        # TEAM TOTALS (per-team over/under)
        # =====================================================================
        team_totals = markets_data.get("team_totals", {})
        for book_key, teams_data in team_totals.items():
            if not teams_data or not isinstance(teams_data, dict):
                continue
            for team_key in ["home", "away"]:
                team_data = teams_data.get(team_key, {})
                if not team_data:
                    continue
                # Save over line
                if "over" in team_data and isinstance(team_data["over"], dict):
                    over = team_data["over"]
                    if self.save_line_snapshot(
                        game_id=game_id,
                        sport=sport,
                        market_type=f"team_total_{team_key}_over",
                        book_key=book_key,
                        line=over.get("line", 0),
                        odds=over.get("odds", -110),
                        implied_prob=american_to_implied_prob(over.get("odds", -110)),
                        market_period="full"
                    ):
                        saved += 1
                # Save under line
                if "under" in team_data and isinstance(team_data["under"], dict):
                    under = team_data["under"]
                    if self.save_line_snapshot(
                        game_id=game_id,
                        sport=sport,
                        market_type=f"team_total_{team_key}_under",
                        book_key=book_key,
                        line=under.get("line", 0),
                        odds=under.get("odds", -110),
                        implied_prob=american_to_implied_prob(under.get("odds", -110)),
                        market_period="full"
                    ):
                        saved += 1

        logger.debug(f"Saved {saved} snapshots for game {game_id}")
        return saved
    
    def _save_period_snapshots(self, game_id: str, sport: str, period_key: str, period_markets: dict, implied_prob_func) -> int:
        """Save snapshots for a specific period (h1, h2, q1-q4, p1-p3)."""
        saved = 0
        
        for market_type, books_data in period_markets.items():
            if not books_data or not isinstance(books_data, dict):
                continue
            
            for book_key, outcomes in books_data.items():
                if not outcomes or not isinstance(outcomes, dict):
                    continue
                
                try:
                    if market_type == "h2h":
                        # Moneyline - save BOTH home and away
                        if "home" in outcomes and outcomes["home"]:
                            if self.save_line_snapshot(
                                game_id=game_id,
                                sport=sport,
                                market_type="moneyline",
                                book_key=book_key,
                                line=0,
                                odds=outcomes["home"],
                                implied_prob=implied_prob_func(outcomes["home"]),
                                market_period=period_key,
                                outcome_type="home"
                            ):
                                saved += 1
                        if "away" in outcomes and outcomes["away"]:
                            if self.save_line_snapshot(
                                game_id=game_id,
                                sport=sport,
                                market_type="moneyline",
                                book_key=book_key,
                                line=0,
                                odds=outcomes["away"],
                                implied_prob=implied_prob_func(outcomes["away"]),
                                market_period=period_key,
                                outcome_type="away"
                            ):
                                saved += 1
                        # Draw ML (soccer 3-way)
                        if "draw" in outcomes and outcomes["draw"]:
                            if self.save_line_snapshot(
                                game_id=game_id,
                                sport=sport,
                                market_type="moneyline",
                                book_key=book_key,
                                line=0,
                                odds=outcomes["draw"],
                                implied_prob=implied_prob_func(outcomes["draw"]),
                                market_period=period_key,
                                outcome_type="Draw"
                            ):
                                saved += 1

                    elif market_type == "spreads":
                        # Spread
                        if "home" in outcomes and isinstance(outcomes["home"], dict):
                            home = outcomes["home"]
                            if self.save_line_snapshot(
                                game_id=game_id,
                                sport=sport,
                                market_type="spread",
                                book_key=book_key,
                                line=home.get("line", 0),
                                odds=home.get("odds", -110),
                                implied_prob=implied_prob_func(home.get("odds", -110)),
                                market_period=period_key
                            ):
                                saved += 1
                    
                    elif market_type == "totals":
                        # Total
                        if "over" in outcomes and isinstance(outcomes["over"], dict):
                            over = outcomes["over"]
                            if self.save_line_snapshot(
                                game_id=game_id,
                                sport=sport,
                                market_type="total",
                                book_key=book_key,
                                line=over.get("line", 0),
                                odds=over.get("odds", -110),
                                implied_prob=implied_prob_func(over.get("odds", -110)),
                                market_period=period_key
                            ):
                                saved += 1
                                
                except Exception as e:
                    logger.warning(f"Error saving {market_type} snapshot for {period_key}: {e}")
        
        return saved
    
    def get_line_history(
        self,
        game_id: str,
        market_type: str = "spread",
        book_key: Optional[str] = None,
        market_period: str = "full"
    ) -> list[dict]:
        """Get historical line snapshots for a game."""
        if not self._is_connected():
            return []
        
        try:
            query = self.client.table("line_snapshots").select("*").eq(
                "game_id", game_id
            ).eq(
                "market_type", market_type
            ).eq(
                "market_period", market_period
            )
            
            if book_key:
                query = query.eq("book_key", book_key)
            
            result = query.order("snapshot_time", desc=False).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting line history: {e}")
            return []
    
    # =========================================================================
    # PLAYER PROPS - Now with snapshot history
    # =========================================================================
    
    def save_prop_snapshot(
        self,
        game_id: str,
        sport: str,
        player_name: str,
        market_type: str,
        book_key: str,
        line: float,
        over_odds: Optional[int] = None,
        under_odds: Optional[int] = None,
        yes_odds: Optional[int] = None
    ) -> bool:
        """Save a single prop snapshot (for line history tracking)."""
        if not self._is_connected():
            return False
        
        try:
            record = {
                "game_id": game_id,
                "sport_key": sport,
                "player_name": player_name,
                "market_type": market_type,
                "book_key": book_key,
                "line": line,
                "over_odds": over_odds,
                "under_odds": under_odds,
                "yes_odds": yes_odds,
                "snapshot_time": datetime.now(timezone.utc).isoformat(),
            }
            
            # INSERT (not upsert) to keep history
            self.client.table("prop_snapshots").insert(record).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error saving prop snapshot: {e}")
            return False
    
    def save_props(self, game_id: str, sport: str, props: list[dict]) -> int:
        """Save player props for a game - both current state and snapshots."""
        if not self._is_connected():
            return 0
        
        saved = 0
        snapshot_time = datetime.now(timezone.utc).isoformat()
        
        for prop in props:
            try:
                player_name = prop.get("player", "Unknown")
                market_type = prop.get("market", "")
                book_key = prop.get("book", "consensus")
                line = prop.get("line")
                over_odds = prop.get("over", {}).get("odds") if prop.get("over") else None
                under_odds = prop.get("under", {}).get("odds") if prop.get("under") else None
                yes_odds = prop.get("yes", {}).get("odds") if prop.get("yes") else None
                
                # Save to player_props table (current state - upsert)
                current_record = {
                    "game_id": game_id,
                    "sport_key": sport,
                    "player_name": player_name,
                    "market_type": market_type,
                    "book_key": book_key,
                    "line": line,
                    "over_odds": over_odds,
                    "under_odds": under_odds,
                    "yes_odds": yes_odds,
                    "snapshot_time": snapshot_time,
                }
                
                self.client.table("player_props").upsert(
                    current_record,
                    on_conflict="game_id,player_name,market_type,book_key"
                ).execute()
                
                # Also save to prop_snapshots table (history - insert)
                self.save_prop_snapshot(
                    game_id=game_id,
                    sport=sport,
                    player_name=player_name,
                    market_type=market_type,
                    book_key=book_key,
                    line=line,
                    over_odds=over_odds,
                    under_odds=under_odds,
                    yes_odds=yes_odds
                )
                
                saved += 1
                
            except Exception as e:
                logger.error(f"Error saving prop: {e}")
        
        return saved
    
    def get_props(self, game_id: str, market_type: Optional[str] = None) -> list[dict]:
        """
        Get player props for a game.
        Returns props formatted for the frontend (with 'player', 'market', 'book' fields).
        """
        if not self._is_connected():
            return []
        
        try:
            query = self.client.table("player_props").select("*").eq(
                "game_id", game_id
            )
            
            if market_type:
                query = query.eq("market_type", market_type)
            
            result = query.order("player_name").execute()
            raw_props = result.data or []
            
            # Transform field names for frontend compatibility
            formatted_props = []
            for prop in raw_props:
                formatted = {
                    "player": prop.get("player_name", "Unknown"),
                    "market": prop.get("market_type", ""),
                    "book": prop.get("book_key", "consensus"),
                    "line": prop.get("line"),
                }
                
                # Transform over/under/yes odds to nested objects
                if prop.get("over_odds") is not None:
                    formatted["over"] = {"odds": prop["over_odds"]}
                if prop.get("under_odds") is not None:
                    formatted["under"] = {"odds": prop["under_odds"]}
                if prop.get("yes_odds") is not None:
                    formatted["yes"] = {"odds": prop["yes_odds"]}
                
                formatted_props.append(formatted)
            
            return formatted_props
            
        except Exception as e:
            logger.error(f"Error getting props: {e}")
            return []
    
    def get_prop_history(
        self,
        game_id: str,
        player_name: str,
        market_type: str,
        book_key: Optional[str] = None
    ) -> list[dict]:
        """Get historical prop snapshots for a player."""
        if not self._is_connected():
            return []
        
        try:
            query = self.client.table("prop_snapshots").select("*").eq(
                "game_id", game_id
            ).eq(
                "player_name", player_name
            ).eq(
                "market_type", market_type
            )
            
            if book_key:
                query = query.eq("book_key", book_key)
            
            result = query.order("snapshot_time", desc=False).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting prop history: {e}")
            return []
    
    # =========================================================================
    # WEATHER DATA
    # =========================================================================
    
    def save_weather(
        self,
        game_id: str,
        sport: str,
        temperature: float,
        wind_speed: float,
        wind_direction: int,
        precipitation_prob: float,
        conditions: str,
        is_dome: bool = False
    ) -> bool:
        """Save weather data for a game."""
        if not self._is_connected():
            return False
        
        try:
            record = {
                "game_id": game_id,
                "sport_key": sport,
                "temperature_f": temperature,
                "wind_speed_mph": wind_speed,
                "wind_direction_deg": wind_direction,
                "precipitation_prob": precipitation_prob,
                "conditions": conditions,
                "is_dome": is_dome,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            
            self.client.table("weather_data").upsert(
                record,
                on_conflict="game_id"
            ).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error saving weather: {e}")
            return False
    
    def get_weather(self, game_id: str) -> Optional[dict]:
        """Get weather data for a game."""
        if not self._is_connected():
            return None
        
        try:
            result = self.client.table("weather_data").select("*").eq(
                "game_id", game_id
            ).limit(1).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return None
    
    # =========================================================================
    # GAME STATUS TRACKING
    # =========================================================================
    
    def save_game_status(self, game_id: str, sport: str, status: str, current_period: str = None) -> bool:
        """Save/update game status for polling tier management."""
        if not self._is_connected():
            return False
        
        try:
            record = {
                "game_id": game_id,
                "sport_key": sport,
                "status": status,
                "current_period": current_period,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            
            self.client.table("game_status").upsert(
                record,
                on_conflict="game_id"
            ).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error saving game status: {e}")
            return False
    
    def get_games_by_status(self, status: str) -> list[dict]:
        """Get all games with a specific status."""
        if not self._is_connected():
            return []
        
        try:
            result = self.client.table("game_status").select("*").eq(
                "status", status
            ).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting games by status: {e}")
            return []
    
    def get_live_games(self) -> list[dict]:
        """Get all currently live games."""
        return self.get_games_by_status("live")
    
    def get_pregame_games(self) -> list[dict]:
        """Get all pre-game games."""
        return self.get_games_by_status("pregame")
    
    # =========================================================================
    # CHATBOT CONTEXT
    # =========================================================================
    
    def get_game_context_for_chatbot(self, game_id: str, sport: str) -> dict:
        """
        Get all relevant data for a game to provide context to the chatbot.
        This pulls from DB only - no API calls.
        """
        context = {
            "prediction": None,
            "line_history": [],
            "props": [],
            "weather": None,
        }
        
        # Get prediction with pillar scores
        context["prediction"] = self.get_prediction(game_id, sport)
        
        # Get line movement history
        context["line_history"] = {
            "spread": self.get_line_history(game_id, "spread"),
            "moneyline": self.get_line_history(game_id, "moneyline"),
            "total": self.get_line_history(game_id, "total"),
        }
        
        # Get props
        context["props"] = self.get_props(game_id)
        
        # Get weather (for outdoor sports)
        context["weather"] = self.get_weather(game_id)
        
        return context


# Singleton instance
db = Database()