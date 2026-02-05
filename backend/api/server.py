"""
OMI Edge FastAPI Server

Provides REST API endpoints for the frontend:
- Edges and predictions
- Line history
- Player props
- Weather data
- AI Chatbot
- Results tracking
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import Optional
import logging
import json
import os

from config import ODDS_API_SPORTS, ANTHROPIC_API_KEY, PROP_MARKETS
from database import db
from results_tracker import ResultsTracker
from espn_scores import ESPNScoreFetcher, AutoGrader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OMI Edge API",
    description="Sports betting mispricing detection API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# HEALTH & STATUS
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "OMI Edge API",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/status")
async def get_status():
    """Get API status including remaining Odds API calls."""
    from data_sources.odds_api import odds_client
    return {
        "status": "ok",
        "odds_api_remaining": odds_client.get_requests_remaining(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/test-football-data")
async def test_football_data():
    """Test Football-Data.org API connectivity for EPL."""
    import os
    result = {
        "api_key_set": bool(os.getenv("FOOTBALL_DATA_API_KEY")),
        "api_key_length": len(os.getenv("FOOTBALL_DATA_API_KEY", "")),
    }

    try:
        from data_sources.football_data import get_epl_standings
        result["import_success"] = True

        standings = get_epl_standings()
        if standings:
            result["standings_fetched"] = True
            result["team_count"] = len(standings)
            # Get sample of 3 teams
            sample = []
            for name, data in list(standings.items())[:3]:
                sample.append({
                    "name": name,
                    "position": data.get("position"),
                    "points": data.get("points"),
                    "form": data.get("form"),
                })
            result["sample_teams"] = sample
        else:
            result["standings_fetched"] = False
            result["error"] = "get_epl_standings returned None"

    except ImportError as e:
        result["import_success"] = False
        result["error"] = f"Import failed: {str(e)}"
    except Exception as e:
        result["error"] = f"API call failed: {str(e)}"

    return result


@app.get("/api/sports")
async def get_sports():
    """Get list of supported sports."""
    return {
        "sports": list(ODDS_API_SPORTS.keys()),
        "sport_keys": ODDS_API_SPORTS,
        "props_available": list(PROP_MARKETS.keys())
    }


# =============================================================================
# EDGES & PREDICTIONS - DATABASE ONLY (FAST)
# =============================================================================

@app.get("/api/edges/{sport}")
async def get_edges_by_sport(sport: str):
    """
    Get all edges for a sport - DATABASE ONLY.
    Returns cached predictions instantly. Run /api/refresh/pregame to populate.
    """
    sport = sport.upper()
    if sport not in ODDS_API_SPORTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        # Read from database only - no live API calls
        predictions = db.get_all_predictions_for_sport(sport)
        
        if predictions:
            return {
                "sport": sport,
                "games": predictions,
                "count": len(predictions),
                "source": "database",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        
        # No cached data - return empty with guidance
        return {
            "sport": sport,
            "games": [],
            "count": 0,
            "source": "database",
            "message": "No cached data. Run POST /api/refresh/pregame to populate.",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting edges for {sport}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/edges/{sport}/{game_id}")
async def get_game_edge(sport: str, game_id: str):
    """
    Get detailed edge analysis for a single game - DATABASE ONLY.
    Returns cached prediction instantly.
    """
    sport = sport.upper()
    if sport not in ODDS_API_SPORTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        # Check database first
        cached = db.get_prediction(game_id, sport)
        if cached:
            # Parse JSON fields for response
            edges_json = cached.get("edges_json", "{}")
            pillars_json = cached.get("pillars_json", "{}")
            consensus_json = cached.get("consensus_odds_json", "{}")
            
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
            
            return {
                "game_id": cached.get("game_id"),
                "sport": cached.get("sport_key"),
                "home_team": cached.get("home_team"),
                "away_team": cached.get("away_team"),
                "commence_time": cached.get("commence_time"),
                "pillar_scores": {
                    "execution": cached.get("pillar_execution", 0.5),
                    "incentives": cached.get("pillar_incentives", 0.5),
                    "shocks": cached.get("pillar_shocks", 0.5),
                    "time_decay": cached.get("pillar_time_decay", 0.5),
                    "flow": cached.get("pillar_flow", 0.5),
                },
                "composite_score": cached.get("composite_score", 0.5),
                "best_bet": cached.get("best_bet_market"),
                "best_edge": cached.get("best_edge_pct", 0),
                "overall_confidence": cached.get("overall_confidence", "PASS"),
                "edges": edges,
                "pillars": pillars,
                "consensus_odds": consensus_odds,
                "source": "database"
            }
        
        # No cached data
        raise HTTPException(
            status_code=404, 
            detail=f"Game {game_id} not found in database. Run POST /api/refresh/pregame to populate."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting game edge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/active-edges")
async def get_active_edges(
    min_confidence: str = Query("WATCH", description="Minimum confidence: PASS, WATCH, EDGE, STRONG, RARE"),
    sport: Optional[str] = Query(None, description="Filter by sport")
):
    """Get all active edges across all sports."""
    try:
        edges = db.get_active_edges(min_confidence)
        
        if sport:
            edges = [e for e in edges if e.get("sport_key") == sport.upper()]
        
        return {
            "edges": edges,
            "count": len(edges),
            "min_confidence": min_confidence,
            "sport_filter": sport
        }
        
    except Exception as e:
        logger.error(f"Error getting active edges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# LINE HISTORY
# =============================================================================

@app.get("/api/lines/{game_id}")
async def get_line_history(
    game_id: str,
    market: str = Query("spread", description="Market type: spread, moneyline, total"),
    book: Optional[str] = Query(None, description="Specific book to filter by"),
    period: str = Query("full", description="Market period: full, h1, h2, q1-q4, p1-p3")
):
    """Get line movement history for a game."""
    try:
        history = db.get_line_history(game_id, market, book, period)
        
        return {
            "game_id": game_id,
            "market": market,
            "period": period,
            "book": book,
            "snapshots": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting line history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CONSENSUS ODDS - DATABASE ONLY
# =============================================================================

@app.get("/api/consensus/{sport}/{game_id}")
async def get_consensus_odds(sport: str, game_id: str):
    """
    Get consensus odds for a game - DATABASE ONLY.
    Returns data from cached prediction.
    """
    sport = sport.upper()
    if sport not in ODDS_API_SPORTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        # Get from database
        cached = db.get_prediction(game_id, sport)
        
        if not cached:
            raise HTTPException(
                status_code=404, 
                detail=f"Game {game_id} not found. Run POST /api/refresh/pregame to populate."
            )
        
        # Parse consensus odds JSON
        consensus_json = cached.get("consensus_odds_json", "{}")
        try:
            consensus = json.loads(consensus_json) if isinstance(consensus_json, str) else consensus_json
        except:
            consensus = {}
        
        return {
            "game_id": game_id,
            "home_team": cached.get("home_team"),
            "away_team": cached.get("away_team"),
            "commence_time": cached.get("commence_time"),
            "consensus": consensus,
            "source": "database"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consensus odds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PER-BOOK ODDS - For switching between books in frontend
# =============================================================================

@app.get("/api/odds/{sport}/{game_id}")
async def get_per_book_odds(sport: str, game_id: str):
    """
    Get odds for a game grouped by bookmaker.
    Allows frontend to display different lines when switching books.
    """
    sport = sport.upper()
    if sport not in ODDS_API_SPORTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    if not db._is_connected():
        raise HTTPException(status_code=500, detail="Database not connected")
    
    try:
        # Get all snapshots for this game
        result = db.client.table("line_snapshots").select("*").eq(
            "game_id", game_id
        ).order("snapshot_time", desc=True).execute()
        
        snapshots = result.data or []
        
        if not snapshots:
            raise HTTPException(status_code=404, detail="No odds data found for this game")
        
        # Group by book, then by period, get latest per market type
        books_data: dict = {}
        seen: set = set()  # Track what we've already added
        
        for snapshot in snapshots:
            book = snapshot.get("book_key", "consensus")
            period = snapshot.get("market_period", "full")
            market_type = snapshot.get("market_type")  # spread, moneyline, total
            
            key = f"{book}_{period}_{market_type}"
            if key in seen:
                continue  # Skip older snapshots
            seen.add(key)
            
            if book not in books_data:
                books_data[book] = {}
            
            if period not in books_data[book]:
                books_data[book][period] = {}
            
            books_data[book][period][market_type] = {
                "line": snapshot.get("line"),
                "odds": snapshot.get("odds"),
                "implied_prob": snapshot.get("implied_prob"),
                "snapshot_time": snapshot.get("snapshot_time"),
            }
        
        # Get props for this game
        props = db.get_props(game_id) or []
        
        # Build market groups for each book
        def build_period_markets(period_data: dict) -> dict:
            if not period_data:
                return {"h2h": None, "spreads": None, "totals": None}
            
            result: dict = {"h2h": None, "spreads": None, "totals": None}
            
            if "moneyline" in period_data:
                ml = period_data["moneyline"]
                result["h2h"] = {
                    "home": {"price": ml.get("odds"), "edge": 0},
                    "away": {"price": None, "edge": 0},
                }
            
            if "spread" in period_data:
                sp = period_data["spread"]
                line = sp.get("line", 0)
                result["spreads"] = {
                    "home": {"line": line, "price": sp.get("odds"), "edge": 0},
                    "away": {"line": -line if line else 0, "price": sp.get("odds"), "edge": 0},
                }
            
            if "total" in period_data:
                tot = period_data["total"]
                result["totals"] = {
                    "line": tot.get("line"),
                    "over": {"price": tot.get("odds"), "edge": 0},
                    "under": {"price": tot.get("odds"), "edge": 0},
                }
            
            return result
        
        period_map = {
            "full": "fullGame",
            "h1": "firstHalf",
            "h2": "secondHalf",
            "q1": "q1", "q2": "q2", "q3": "q3", "q4": "q4",
            "p1": "p1", "p2": "p2", "p3": "p3",
        }
        
        bookmakers = {}
        for book_key, book_periods in books_data.items():
            market_groups: dict = {
                "fullGame": {"h2h": None, "spreads": None, "totals": None},
                "firstHalf": {"h2h": None, "spreads": None, "totals": None},
                "secondHalf": {"h2h": None, "spreads": None, "totals": None},
                "q1": {"h2h": None, "spreads": None, "totals": None},
                "q2": {"h2h": None, "spreads": None, "totals": None},
                "q3": {"h2h": None, "spreads": None, "totals": None},
                "q4": {"h2h": None, "spreads": None, "totals": None},
                "p1": {"h2h": None, "spreads": None, "totals": None},
                "p2": {"h2h": None, "spreads": None, "totals": None},
                "p3": {"h2h": None, "spreads": None, "totals": None},
                "teamTotals": None,
                "playerProps": [p for p in props if p.get("book") == book_key],
                "alternates": {"spreads": [], "totals": []},
            }
            
            for db_period, frontend_period in period_map.items():
                if db_period in book_periods:
                    market_groups[frontend_period] = build_period_markets(book_periods[db_period])
            
            bookmakers[book_key] = {"marketGroups": market_groups}
        
        return {
            "game_id": game_id,
            "sport": sport,
            "books": list(books_data.keys()),
            "bookmakers": bookmakers,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting per-book odds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PLAYER PROPS - DATABASE ONLY
# =============================================================================

@app.get("/api/props/{sport}/{game_id}")
async def get_game_props(
    sport: str,
    game_id: str,
    market: Optional[str] = Query(None, description="Filter by market type (e.g., player_pass_yds)")
):
    """Get player props for a specific game - DATABASE ONLY, no live fetching."""
    sport = sport.upper()
    if sport not in ODDS_API_SPORTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    try:
        # Only read from database - no live API fallback
        props = db.get_props(game_id, market)
        
        return {
            "game_id": game_id,
            "sport": sport,
            "props": props,
            "count": len(props),
            "source": "database"
        }
        
    except Exception as e:
        logger.error(f"Error getting props: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/props/{sport}/{game_id}/markets")
async def get_available_prop_markets(sport: str, game_id: str):
    """Get list of available prop markets for a game."""
    sport = sport.upper()
    
    try:
        props = db.get_props(game_id)
        
        if not props:
            return {
                "game_id": game_id,
                "sport": sport,
                "markets": PROP_MARKETS.get(sport, []),
                "source": "config"
            }
        
        # Props are now formatted with 'market' field
        markets = list(set(p.get("market") for p in props if p.get("market")))
        
        return {
            "game_id": game_id,
            "sport": sport,
            "markets": markets,
            "source": "data"
        }
        
    except Exception as e:
        logger.error(f"Error getting prop markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/props/{sport}/{game_id}/player/{player_name}")
async def get_player_props(sport: str, game_id: str, player_name: str):
    """Get all props for a specific player."""
    sport = sport.upper()
    
    try:
        all_props = db.get_props(game_id)
        
        # Props are now formatted with 'player' field
        player_props = [
            p for p in all_props 
            if p.get("player", "").lower() == player_name.lower()
        ]
        
        return {
            "game_id": game_id,
            "sport": sport,
            "player": player_name,
            "props": player_props,
            "count": len(player_props)
        }
        
    except Exception as e:
        logger.error(f"Error getting player props: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/props/history/{game_id}/{player_name}/{market_type}")
async def get_prop_history(
    game_id: str,
    player_name: str,
    market_type: str,
    book: Optional[str] = Query(None, description="Filter by book")
):
    """Get historical prop line snapshots for a player."""
    try:
        history = db.get_prop_history(game_id, player_name, market_type, book)
        
        return {
            "game_id": game_id,
            "player": player_name,
            "market": market_type,
            "book": book,
            "snapshots": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting prop history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WEATHER
# =============================================================================

@app.get("/api/weather/{game_id}")
async def get_game_weather(game_id: str):
    """Get weather data for a game (outdoor sports only)."""
    try:
        weather = db.get_weather(game_id)
        
        if not weather:
            return {
                "game_id": game_id,
                "weather": None,
                "message": "No weather data available (indoor game or not yet fetched)"
            }
        
        return {
            "game_id": game_id,
            "weather": weather
        }
        
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# AI CHATBOT
# =============================================================================

@app.post("/api/chat/{sport}/{game_id}")
async def chat_about_game(
    sport: str,
    game_id: str,
    request: dict
):
    """
    AI chatbot endpoint for game analysis.
    Reads from database only - no additional API calls.
    """
    sport = sport.upper()
    if sport not in ODDS_API_SPORTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")
    
    user_message = request.get("message", "")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        context = db.get_game_context_for_chatbot(game_id, sport)
        
        prediction = context.get("prediction")
        if not prediction:
            raise HTTPException(status_code=404, detail="Game not found in database")
        
        context_str = build_chatbot_context(context, sport)
        
        response = await call_claude_api(user_message, context_str, prediction)
        
        return {
            "game_id": game_id,
            "sport": sport,
            "user_message": user_message,
            "response": response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def build_chatbot_context(context: dict, sport: str) -> str:
    """Build a context string for the chatbot from database data."""
    prediction = context.get("prediction", {})
    line_history = context.get("line_history", {})
    props = context.get("props", [])
    weather = context.get("weather")
    
    parts = []
    
    parts.append(f"GAME: {prediction.get('away_team')} @ {prediction.get('home_team')}")
    parts.append(f"Sport: {sport}")
    parts.append(f"Date: {prediction.get('commence_time')}")
    parts.append("")
    
    parts.append("PILLAR SCORES (0-1 scale, 0.5 is neutral):")
    parts.append(f"  Execution: {prediction.get('pillar_execution', 0.5):.2f}")
    parts.append(f"  Incentives: {prediction.get('pillar_incentives', 0.5):.2f}")
    parts.append(f"  Shocks: {prediction.get('pillar_shocks', 0.5):.2f}")
    parts.append(f"  Time Decay: {prediction.get('pillar_time_decay', 0.5):.2f}")
    parts.append(f"  Flow: {prediction.get('pillar_flow', 0.5):.2f}")
    parts.append(f"  COMPOSITE: {prediction.get('composite_score', 0.5):.2f}")
    parts.append(f"  Confidence: {prediction.get('overall_confidence', 'PASS')}")
    parts.append("")
    
    edges_json = prediction.get("edges_json", "{}")
    try:
        edges = json.loads(edges_json) if isinstance(edges_json, str) else edges_json
        if edges:
            parts.append("DETECTED EDGES:")
            for market, edge_data in edges.items():
                parts.append(f"  {market}: {edge_data}")
            parts.append("")
    except:
        pass
    
    spread_history = line_history.get("spread", [])
    if spread_history:
        opening = spread_history[0] if spread_history else {}
        current = spread_history[-1] if spread_history else {}
        parts.append("LINE MOVEMENT (Spread):")
        parts.append(f"  Opening: {opening.get('line', 'N/A')} ({opening.get('snapshot_time', 'N/A')})")
        parts.append(f"  Current: {current.get('line', 'N/A')} ({current.get('snapshot_time', 'N/A')})")
        movement = (current.get('line', 0) or 0) - (opening.get('line', 0) or 0)
        parts.append(f"  Movement: {movement:+.1f} points")
        parts.append(f"  Total snapshots: {len(spread_history)}")
        parts.append("")
    
    total_history = line_history.get("total", [])
    if total_history:
        opening = total_history[0] if total_history else {}
        current = total_history[-1] if total_history else {}
        parts.append("LINE MOVEMENT (Total):")
        parts.append(f"  Opening: {opening.get('line', 'N/A')}")
        parts.append(f"  Current: {current.get('line', 'N/A')}")
        parts.append("")
    
    if weather and not weather.get("is_dome"):
        parts.append("WEATHER:")
        parts.append(f"  Temperature: {weather.get('temperature_f')}°F")
        parts.append(f"  Wind: {weather.get('wind_speed_mph')} mph")
        parts.append(f"  Conditions: {weather.get('conditions')}")
        parts.append(f"  Precipitation: {weather.get('precipitation_prob')}%")
        parts.append("")
    elif weather and weather.get("is_dome"):
        parts.append("WEATHER: Dome stadium (no weather impact)")
        parts.append("")
    
    if props:
        parts.append(f"PLAYER PROPS: {len(props)} props available")
        markets = {}
        for prop in props[:20]:
            market = prop.get("market", "unknown")
            if market not in markets:
                markets[market] = []
            markets[market].append(f"{prop.get('player')}: {prop.get('line')}")
        
        for market, players in markets.items():
            parts.append(f"  {market}: {', '.join(players[:3])}")
        parts.append("")
    
    return "\n".join(parts)


async def call_claude_api(user_message: str, context: str, prediction: dict) -> str:
    """Call Claude API for chatbot response."""
    import httpx
    
    if not ANTHROPIC_API_KEY:
        return generate_fallback_response(user_message, prediction)
    
    system_prompt = """You are Edge AI, an expert sports betting analyst for OMI Edge. 
Your job is to help users understand betting edges, line movements, and our analysis.

You have access to the following data about this game (provided in the context).
Answer questions based ONLY on this data - do not make up information.

Key concepts to explain:
- PILLAR SCORES: Our 5-pillar analysis system (Execution, Incentives, Shocks, Time Decay, Flow)
  - Execution: Injuries, weather, lineup changes
  - Incentives: Playoff implications, motivation, tanking
  - Shocks: Breaking news, sudden line moves
  - Time Decay: Rest days, travel, back-to-backs
  - Flow: Sharp vs public money, betting patterns
- COMPOSITE SCORE: Weighted average of pillars (>0.5 favors home, <0.5 favors away)
- CONFIDENCE: PASS (no edge), WATCH (monitor), EDGE (actionable), STRONG (high confidence), RARE (exceptional)
- LINE MOVEMENT: How the spread/total has moved since opening
- EDGES: Where we see value vs the books' odds

Be concise, helpful, and data-driven. Use the actual numbers from the context.
If asked about something not in the context, say you don't have that data."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 500,
                    "system": system_prompt,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"GAME CONTEXT:\n{context}\n\nUSER QUESTION: {user_message}"
                        }
                    ]
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Claude API error: {response.status_code} {response.text}")
                return generate_fallback_response(user_message, prediction)
            
            data = response.json()
            return data.get("content", [{}])[0].get("text", "Sorry, I couldn't generate a response.")
            
    except Exception as e:
        logger.error(f"Claude API call failed: {e}")
        return generate_fallback_response(user_message, prediction)


def generate_fallback_response(user_message: str, prediction: dict) -> str:
    """Generate a response without Claude API (fallback)."""
    user_lower = user_message.lower()
    
    home_team = prediction.get("home_team", "the home team")
    away_team = prediction.get("away_team", "the away team")
    composite = prediction.get("composite_score", 0.5)
    confidence = prediction.get("overall_confidence", "PASS")
    
    if "line" in user_lower or "move" in user_lower or "movement" in user_lower:
        return f"Line movement for {away_team} @ {home_team} indicates betting action. Our composite score is {composite:.1%}, suggesting {'home team value' if composite > 0.55 else 'away team value' if composite < 0.45 else 'a balanced game'}. Check the line history chart for detailed movement."
    
    elif "edge" in user_lower or "value" in user_lower:
        return f"Our analysis shows a {confidence} rating for this game. The composite score of {composite:.1%} {'suggests potential value' if confidence in ['EDGE', 'STRONG', 'RARE'] else 'does not indicate strong value'}. The best edges typically come from sharp money disagreeing with public sentiment."
    
    elif "sharp" in user_lower or "public" in user_lower:
        return f"Sharp vs public analysis is captured in our Flow pillar. For {away_team} @ {home_team}, watch for reverse line movement (line moving opposite to public betting) as a signal of sharp action."
    
    elif "pillar" in user_lower or "score" in user_lower:
        return f"Our 5-pillar system analyzes: Execution (injuries, weather), Incentives (motivation), Shocks (news), Time Decay (rest), and Flow (betting patterns). This game's composite score is {composite:.1%} with {confidence} confidence."
    
    elif "weather" in user_lower:
        return "Weather data is available for outdoor NFL and college football games. Check the weather section for temperature, wind, and precipitation that could affect totals and passing games."
    
    elif "prop" in user_lower:
        return f"Player props for {away_team} @ {home_team} are tracked in our system. We monitor line movement on props just like main markets. Check the Props tab for current lines and movement."
    
    else:
        return f"I can help you analyze {away_team} @ {home_team}. Our current assessment: {confidence} confidence with a {composite:.1%} composite score. Ask me about line movement, edges, sharp money, pillars, weather, or props!"


# =============================================================================
# RESULTS TRACKING & GRADING
# =============================================================================

@app.post("/api/results/snapshot/{sport}/{game_id}")
async def snapshot_prediction(sport: str, game_id: str):
    """Snapshot a prediction before game starts."""
    tracker = ResultsTracker()
    result = tracker.snapshot_prediction_at_close(game_id, sport.upper())
    return {"status": "ok", "data": result}


@app.post("/api/results/grade/{game_id}")
async def grade_game(game_id: str, home_score: int, away_score: int):
    """Grade a completed game."""
    tracker = ResultsTracker()
    result = tracker.grade_game(game_id, home_score, away_score)
    return {"status": "ok", "data": result}


@app.get("/api/results/recent")
async def get_recent_results(limit: int = 50, sport: str = None):
    """Get recent graded games."""
    tracker = ResultsTracker()
    results = tracker.get_recent_results(limit, sport.upper() if sport else None)
    return {"results": results, "count": len(results)}


@app.get("/api/results/summary")
async def get_performance_summary(sport: str = None, days: int = 30):
    """Get performance summary stats."""
    tracker = ResultsTracker()
    summary = tracker.get_performance_summary(sport.upper() if sport else None, days)
    return summary


@app.get("/api/results/price-movement/{game_id}")
async def get_price_movement(game_id: str, market: str = "spread", book: str = "fanduel"):
    """Get price movement for a market."""
    tracker = ResultsTracker()
    movement = tracker.get_price_movement(game_id, market, book)
    return movement


# =============================================================================
# ESPN SCORES (FREE)
# =============================================================================

@app.get("/api/espn/scores/{sport}")
async def get_espn_scores(sport: str, date: str = None):
    """Get scores from ESPN (free, no API cost)."""
    fetcher = ESPNScoreFetcher()
    scores = fetcher.get_scores(sport.upper(), date)
    return {"sport": sport, "games": scores, "count": len(scores)}


@app.get("/api/espn/final/{sport}")
async def get_espn_final_scores(sport: str, date: str = None):
    """Get only final scores from ESPN."""
    fetcher = ESPNScoreFetcher()
    scores = fetcher.get_final_scores(sport.upper(), date)
    return {"sport": sport, "games": scores, "count": len(scores)}


@app.post("/api/results/auto-grade")
async def auto_grade_games(sport: str = None):
    """Automatically grade completed games using ESPN scores."""
    tracker = ResultsTracker()
    grader = AutoGrader(tracker)
    results = grader.grade_completed_games(sport.upper() if sport else None)
    return results


@app.post("/api/results/snapshot-upcoming")
async def snapshot_upcoming(sport: str = None, minutes: int = 30):
    """Snapshot predictions for games starting soon."""
    tracker = ResultsTracker()
    grader = AutoGrader(tracker)
    results = grader.snapshot_upcoming_games(sport.upper() if sport else None, minutes)
    return results


# =============================================================================
# MANUAL REFRESH - These endpoints DO make live API calls
# =============================================================================

@app.post("/api/refresh")
async def refresh_all_edges():
    """Manually trigger a refresh of all edges."""
    try:
        from scheduler import run_analysis_cycle
        result = run_analysis_cycle()
        return {
            "status": "completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error during manual refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh/pregame")
async def refresh_pregame():
    """Manually trigger a pre-game refresh (all markets + props)."""
    try:
        from scheduler import run_pregame_cycle
        result = run_pregame_cycle()
        return {
            "status": "completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error during pregame refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh/live")
async def refresh_live():
    """Manually trigger a live games refresh."""
    try:
        from scheduler import run_live_cycle
        result = run_live_cycle()
        return {
            "status": "completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error during live refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh/props")
async def refresh_live_props():
    """Manually trigger a live props refresh."""
    try:
        from scheduler import run_live_props_cycle
        result = run_live_props_cycle()
        return {
            "status": "completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error during props refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PILLAR CALCULATION (ON-DEMAND)
# =============================================================================

@app.get("/api/pillars/{sport}/{game_id}")
async def calculate_pillars(sport: str, game_id: str, fresh: bool = False):
    """
    Calculate 5-pillar scores for a game.

    If fresh=True, recalculates from live data (uses API calls).
    Otherwise returns cached values from database.

    Returns pillar scores on 0-1 scale:
    - execution: Injuries, weather, lineup uncertainty
    - incentives: Playoffs, motivation, rivalries
    - shocks: Breaking news, line movement timing
    - time_decay: Rest days, back-to-back, travel
    - flow: Sharp money, book disagreement
    - composite: Weighted average of all pillars
    """
    sport = sport.upper()
    if sport not in ODDS_API_SPORTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")

    try:
        # ALWAYS do fresh calculation for now to debug pillar scores
        # TODO: Re-enable caching once pillars are working
        logger.info(f"[Pillars] Calculating fresh pillars for {game_id} in {sport}")

        # Fresh calculation - need to fetch game data and run analysis
        from data_sources.odds_api import odds_client
        from engine.analyzer import analyze_game

        # First, try cached_odds which has full game data with bookmakers
        game = None
        result = db.client.table("cached_odds").select("game_data").eq("game_id", game_id).single().execute()
        if result.data:
            game = result.data.get("game_data")
            logger.info(f"[Pillars] Using cached_odds for {game_id}")
            logger.info(f"[Pillars] Game has {len(game.get('bookmakers', []))} bookmakers")
            if game.get('bookmakers'):
                first_book = game['bookmakers'][0]
                logger.info(f"[Pillars] First book: {first_book.get('key')}, markets: {[m.get('key') for m in first_book.get('markets', [])]}")

        # Fall back to live API if no cached data
        if not game:
            games = odds_client.get_upcoming_games(sport)
            game = next((g for g in games if g.get("id") == game_id), None)
            if game:
                logger.info(f"[Pillars] Using live API for {game_id}")

        if not game:
            raise HTTPException(status_code=404, detail=f"Game {game_id} not found")

        # Run full analysis
        logger.info(f"[Pillars] Running analyze_game for {game.get('away_team')} @ {game.get('home_team')}")
        analysis = analyze_game(game, sport)

        return {
            "game_id": analysis["game_id"],
            "sport": analysis["sport"],
            "home_team": analysis["home_team"],
            "away_team": analysis["away_team"],
            "pillar_scores": analysis["pillar_scores"],
            "composite_score": analysis["composite_score"],
            "overall_confidence": analysis["overall_confidence"],
            "best_bet": analysis["best_bet"],
            "best_edge": analysis["best_edge"],
            "pillars": analysis["pillars"],
            "source": "live_calculation"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating pillars: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)