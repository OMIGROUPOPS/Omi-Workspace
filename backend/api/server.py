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
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging
import json
import os
import time
from collections import defaultdict

from config import ODDS_API_SPORTS, ANTHROPIC_API_KEY, PROP_MARKETS
from database import db
from results_tracker import ResultsTracker
from espn_scores import ESPNScoreFetcher, AutoGrader, teams_match, SPORT_KEY_VARIANTS, ESPN_SPORTS
from internal_grader import (
    InternalGrader, determine_signal, calc_edge_pct, edge_to_confidence,
    _cap_edge_display,
    SPORT_DISPLAY, _normalize_sport, PROB_PER_POINT, PROB_PER_TOTAL_POINT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

_scheduler = None

@asynccontextmanager
async def lifespan(app):
    """Start scheduler AFTER the server is listening — never before."""
    global _scheduler
    print("LIFESPAN: server is up, starting scheduler in background...", flush=True)
    logger.info("FastAPI lifespan: starting scheduler (all jobs delayed 60s+)")
    from scheduler import start_scheduler
    _scheduler = start_scheduler()
    yield
    # Shutdown
    if _scheduler:
        logger.info("Shutting down scheduler...")
        _scheduler.shutdown(wait=False)

app = FastAPI(
    title="OMI Edge API",
    description="Sports betting mispricing detection API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# RESPONSE CACHE — avoid hammering Supabase when multiple tabs fire at once
# =============================================================================
_cache: dict = {}  # key -> {"data": ..., "ts": float}

def _cache_get(key: str, ttl: float):
    """Return cached data if fresh, else None."""
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < ttl:
        return entry["data"]
    return None

def _cache_set(key: str, data):
    """Store data in cache with current timestamp."""
    _cache[key] = {"data": data, "ts": time.time()}


def _with_scheduler_pause(fn, *args, **kwargs):
    """Pause scheduler, run fn, resume. Guarantees a free Supabase connection."""
    from scheduler import pause_scheduler, resume_scheduler
    pause_scheduler(60)
    try:
        return fn(*args, **kwargs)
    finally:
        resume_scheduler()


# =============================================================================
# SCHEDULER PAUSE/RESUME API
# =============================================================================

@app.post("/api/internal/pause-scheduler")
def api_pause_scheduler(seconds: int = 60):
    """Pause all scheduler jobs for N seconds (default 60). Auto-resumes."""
    from scheduler import pause_scheduler
    pause_scheduler(min(seconds, 300))
    return {"status": "paused", "seconds": min(seconds, 300)}

@app.post("/api/internal/resume-scheduler")
def api_resume_scheduler():
    """Resume scheduler jobs immediately."""
    from scheduler import resume_scheduler
    resume_scheduler()
    return {"status": "resumed"}


# =============================================================================
# HEALTH & STATUS
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    print("HEALTH CHECK READY", flush=True)
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
            outcome_type = snapshot.get("outcome_type", "")

            # Include outcome_type in key for moneyline (home vs away are distinct)
            key = f"{book}_{period}_{market_type}_{outcome_type}" if market_type == "moneyline" else f"{book}_{period}_{market_type}"
            if key in seen:
                continue  # Skip older snapshots
            seen.add(key)

            if book not in books_data:
                books_data[book] = {}

            if period not in books_data[book]:
                books_data[book][period] = {}

            # Store moneyline home/away separately
            store_key = f"{market_type}_{outcome_type}" if market_type == "moneyline" and outcome_type else market_type
            books_data[book][period][store_key] = {
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
            
            ml_home = period_data.get("moneyline_home") or period_data.get("moneyline")
            ml_away = period_data.get("moneyline_away")
            if ml_home or ml_away:
                result["h2h"] = {
                    "home": {"price": ml_home.get("odds") if ml_home else None, "edge": 0},
                    "away": {"price": ml_away.get("odds") if ml_away else None, "edge": 0},
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
async def calculate_pillars(
    sport: str,
    game_id: str,
    market_type: str = Query("spread", description="Market type: spread, totals, moneyline"),
    period: str = Query("full", description="Period: full, h1, h2, q1-q4, p1-p3"),
    fresh: bool = False
):
    """
    Calculate 6-pillar scores for a game with market/period-specific composites.

    If fresh=True, recalculates from live data (uses API calls).
    Otherwise returns cached values from database.

    Query Parameters:
    - market_type: spread, totals, or moneyline (default: spread)
    - period: full, h1, h2, q1-q4, p1-p3 (default: full)

    Returns pillar scores on 0-1 scale:
    - execution: Injuries, weather, lineup uncertainty
    - incentives: Playoffs, motivation, rivalries
    - shocks: Breaking news, line movement timing
    - time_decay: Rest days, back-to-back, travel
    - flow: Sharp money, book disagreement
    - game_environment: Pace, weather, expected totals
    - composite_score: Market/period-specific weighted composite
    - pillars_by_market: All market×period composites (up to 21 combinations)
    """
    sport = sport.upper()
    if sport not in ODDS_API_SPORTS:
        raise HTTPException(status_code=400, detail=f"Unknown sport: {sport}")

    # Validate market_type
    valid_markets = ["spread", "totals", "moneyline"]
    if market_type not in valid_markets:
        raise HTTPException(status_code=400, detail=f"Invalid market_type: {market_type}. Must be one of: {valid_markets}")

    try:
        logger.info(f"[Pillars] Calculating pillars for {game_id} in {sport}, market={market_type}, period={period}")

        # Fresh calculation - need to fetch game data and run analysis
        from data_sources.odds_api import odds_client
        from engine.analyzer import analyze_game

        # First, try cached_odds which has full game data with bookmakers
        game = None
        result = db.client.table("cached_odds").select("game_data").eq("game_id", game_id).single().execute()
        if result.data:
            game = result.data.get("game_data")
            logger.info(f"[Pillars] Using cached_odds for {game_id}")

        # Fall back to live API if no cached data
        if not game:
            games = odds_client.get_upcoming_games(sport)
            game = next((g for g in games if g.get("id") == game_id), None)
            if game:
                logger.info(f"[Pillars] Using live API for {game_id}")

        if not game:
            raise HTTPException(status_code=404, detail=f"Game {game_id} not found")

        # Run full analysis (calculates all market/period composites)
        logger.info(f"[Pillars] Running analyze_game for {game.get('away_team')} @ {game.get('home_team')}")
        analysis = analyze_game(game, sport)

        # Get the market/period-specific composite from pillars_by_market
        pillars_by_market = analysis.get("pillars_by_market", {})
        specific_data = pillars_by_market.get(market_type, {}).get(period, {})

        # If period not available for this sport, fall back to "full"
        if not specific_data and period != "full":
            specific_data = pillars_by_market.get(market_type, {}).get("full", {})
            period = "full"  # Update to reflect actual period used

        # Use specific composite if available, otherwise default
        composite_score = specific_data.get("composite", analysis["composite_score"])
        pillar_weights = specific_data.get("weights", analysis["pillar_weights"])
        overall_confidence = specific_data.get("confidence", analysis["overall_confidence"])

        return {
            "game_id": analysis["game_id"],
            "sport": analysis["sport"],
            "home_team": analysis["home_team"],
            "away_team": analysis["away_team"],
            "pillar_scores": analysis["pillar_scores"],
            "pillar_weights": pillar_weights,
            "composite_score": composite_score,
            "overall_confidence": overall_confidence,
            "market_type": market_type,
            "period": period,
            "best_bet": analysis["best_bet"],
            "best_edge": analysis["best_edge"],
            "pillars": analysis["pillars"],
            "pillars_by_market": pillars_by_market,
            "source": "live_calculation"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating pillars: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# INTERNAL TOOLS
# =============================================================================

@app.post("/api/internal/grade-games")
def internal_grade_games(sport: str = None, regrade: bool = False):
    """Grade completed games and generate prediction_grades rows.

    Pass ?regrade=true to purge all prediction_grades and regenerate
    from scratch (fixes bad edge calculations from sign-convention bug).
    """
    grader = InternalGrader()
    if regrade:
        return grader.regrade_all()
    return grader.grade_games(sport.upper() if sport else None)


@app.post("/api/internal/backfill-scores")
def backfill_scores():
    """One-time backfill: fetch ESPN scores for Feb 10+ games, grade them.

    1. Purge pre-Feb-10 game_results and prediction_grades (broken pillars)
    2. Fetch ESPN scores for all unscored Feb 10+ game_results
    3. Grade newly scored games → create prediction_grades rows
    """
    from espn_scores import ESPNScoreFetcher, AutoGrader, SPORT_KEY_VARIANTS, ESPN_SPORTS, teams_match, utc_to_espn_date
    from results_tracker import ResultsTracker
    from internal_grader import InternalGrader
    from supabase import create_client
    import os

    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    client = create_client(url, key)
    cutoff = "2026-02-10T00:00:00+00:00"

    # --- Step 1: Purge pre-Feb-10 data ---
    # Delete old prediction_grades (joined via game_id)
    old_gr = client.table("game_results").select("game_id").lt("commence_time", cutoff).execute()
    old_ids = [r["game_id"] for r in (old_gr.data or [])]

    pg_deleted = 0
    for i in range(0, len(old_ids), 50):
        batch = old_ids[i:i+50]
        res = client.table("prediction_grades").delete().in_("game_id", batch).execute()
        pg_deleted += len(res.data or [])

    # Delete old game_results
    gr_deleted_res = client.table("game_results").delete().lt("commence_time", cutoff).execute()
    gr_deleted = len(gr_deleted_res.data or [])

    logger.info(f"[Backfill] Purged {gr_deleted} game_results and {pg_deleted} prediction_grades before {cutoff}")

    # --- Step 2: Fetch ESPN scores for unscored Feb 10+ games ---
    now = datetime.now(timezone.utc).isoformat()
    espn = ESPNScoreFetcher()
    tracker = ResultsTracker()
    scores_filled = 0
    not_found = 0
    errors = 0
    scored_game_ids = []

    for sport in ESPN_SPORTS:
        variants = SPORT_KEY_VARIANTS.get(sport, [sport])
        unscored = client.table("game_results").select(
            "game_id, home_team, away_team, commence_time, sport_key"
        ).in_("sport_key", variants).is_("home_score", "null").gte(
            "commence_time", cutoff
        ).lt("commence_time", now).execute()

        games = unscored.data or []
        if not games:
            continue

        # Group by ESPN (US-Eastern) date for efficient fetching
        by_date: dict[str, list[dict]] = {}
        for g in games:
            ct = g.get("commence_time", "")
            if ct:
                d = utc_to_espn_date(ct)
                by_date.setdefault(d, []).append(g)

        espn_cache: dict[str, list[dict]] = {}
        for date_str in by_date:
            if date_str not in espn_cache:
                espn_cache[date_str] = espn.get_final_scores(sport, date_str)

        for date_str, date_games in by_date.items():
            espn_games = espn_cache.get(date_str, [])
            for g in date_games:
                home = g.get("home_team", "")
                away = g.get("away_team", "")
                match = None
                for eg in espn_games:
                    if teams_match(eg["home_team"], home) and teams_match(eg["away_team"], away):
                        match = eg
                        break
                    if teams_match(eg["home_team"], away) and teams_match(eg["away_team"], home):
                        match = {"home_score": eg["away_score"], "away_score": eg["home_score"], "is_final": eg["is_final"]}
                        break

                if not match or not match.get("is_final"):
                    not_found += 1
                    continue

                try:
                    tracker.grade_game(g["game_id"], match["home_score"], match["away_score"])
                    scores_filled += 1
                    scored_game_ids.append(g["game_id"])
                except Exception as e:
                    logger.error(f"[Backfill] grade_game error {g['game_id']}: {e}")
                    errors += 1

        logger.info(f"[Backfill] {sport}: {len(games)} unscored, {scores_filled} filled so far")

    # --- Step 3: Generate prediction_grades for newly scored games ---
    grades_created = 0
    ig = InternalGrader()
    for gid in scored_game_ids:
        try:
            count = ig._generate_prediction_grades(gid)
            grades_created += count
        except Exception as e:
            logger.error(f"[Backfill] prediction_grades error {gid}: {e}")

    result = {
        "purged_game_results": gr_deleted,
        "purged_prediction_grades": pg_deleted,
        "games_found": len(scored_game_ids) + not_found + errors,
        "scores_filled": scores_filled,
        "not_found_on_espn": not_found,
        "grades_created": grades_created,
        "errors": errors,
    }
    logger.info(f"[Backfill] Complete: {result}")
    return result


@app.get("/api/internal/edge/performance")
def internal_edge_performance(
    sport: str = None,
    days: int = 30,
    market: str = None,
    confidence_tier: int = None,
    signal: str = None,
    since: str = None,
):
    """Get Edge performance metrics from prediction_grades.

    Reads from scheduler-populated perf_cache first (zero Supabase calls).
    Falls back to in-process cache, then direct query.
    """
    # 1. Check scheduler-populated cache (no Supabase call)
    from perf_cache import lookup as perf_lookup
    pre = perf_lookup(
        sport=sport.upper() if sport else None,
        days=days, market=market,
        confidence_tier=confidence_tier,
        signal=signal, since=since,
    )
    if pre is not None:
        return pre

    # 2. Fall back to in-process response cache
    ck = f"perf:{sport}:{days}:{market}:{confidence_tier}:{signal}:{since}"
    cached = _cache_get(ck, 300)
    if cached is not None:
        return cached

    # 3. Last resort: pause scheduler, query Supabase directly
    def _query():
        return InternalGrader().get_performance(
            sport.upper() if sport else None,
            days, market, confidence_tier, signal, since,
        )
    data = _with_scheduler_pause(_query)
    _cache_set(ck, data)
    return data


@app.get("/api/internal/edge/graded-games")
def internal_graded_games(
    sport: str = None,
    market: str = None,
    verdict: str = None,
    days: int = 30,
    since: str = None,
    limit: int = 500,
):
    """Get individual graded prediction rows with game context."""
    capped_limit = min(limit, 1000)
    ck = f"graded:{sport}:{market}:{verdict}:{days}:{since}:{capped_limit}"
    cached = _cache_get(ck, 300)
    if cached is not None:
        return cached
    def _query():
        grader = InternalGrader()
        return grader.get_graded_games(
            sport=sport.upper() if sport else None,
            market=market,
            verdict=verdict,
            since=since,
            days=days,
            limit=capped_limit,
        )
    data = _with_scheduler_pause(_query)
    _cache_set(ck, data)
    return data


@app.get("/api/internal/edge/live-markets")
def internal_live_markets(sport: str = None):
    """Get upcoming games with current OMI fair lines and book edges."""
    ck = f"live-mkts:{sport}"
    cached = _cache_get(ck, 120)
    if cached is not None:
        return cached
    try:
        def _query():
            grader = InternalGrader()
            return grader.get_live_markets(sport.upper() if sport else None)
        data = _with_scheduler_pause(_query)
        _cache_set(ck, data)
        return data
    except Exception as e:
        import traceback
        logger.error(f"[live-markets] 500 error: {e}\n{traceback.format_exc()}")
        return {"rows": [], "count": 0, "error": str(e)}


@app.get("/api/internal/edge/reflection")
def internal_edge_reflection(sport: str = None):
    """Deep reflection analysis on prediction accuracy and pillar effectiveness."""
    try:
        from reflection_engine import ReflectionEngine
        engine = ReflectionEngine()
        return engine.analyze(sport.lower() if sport else None)
    except Exception as e:
        logger.error(f"Error running reflection analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/internal/edge-analytics")
def internal_edge_analytics(sport: str = None, days: int = 30):
    """Deep edge analytics: calibration curves, conditional breakdowns, CLV, insights."""
    try:
        from edge_analytics import EdgeAnalytics
        return EdgeAnalytics().analyze(sport.upper() if sport else None, days)
    except Exception as e:
        logger.error(f"Error running edge analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/internal/exchange-accuracy")
def internal_exchange_accuracy(sport: str = None, days: int = 30):
    """Exchange vs sportsbook accuracy comparison from exchange_accuracy_log."""
    ck = f"exch-acc:{sport}:{days}"
    cached = _cache_get(ck, 300)
    if cached is not None:
        return cached
    try:
        from edge_analytics import EdgeAnalytics
        def _query():
            return EdgeAnalytics().analyze_exchange_accuracy(sport.upper() if sport else None, days)
        data = _with_scheduler_pause(_query)
        _cache_set(ck, data)
        return data
    except Exception as e:
        logger.error(f"Error running exchange accuracy analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PREGAME CAPTURE
# =============================================================================

@app.get("/api/v1/pregame-edges")
def pregame_edges(sport: str = None):
    """Get latest pregame snapshot for all upcoming games with edges."""
    try:
        if not db._is_connected():
            raise HTTPException(status_code=500, detail="Database not connected")

        from datetime import datetime, timezone

        query = db.client.table("pregame_snapshots").select("*").gt(
            "commence_time", datetime.now(timezone.utc).isoformat()
        ).order("snapshot_time", desc=True)

        if sport:
            query = query.eq("sport_key", sport.upper())

        result = query.limit(5000).execute()

        # Dedup to latest snapshot per game_id
        seen = {}
        for row in (result.data or []):
            gid = row["game_id"]
            if gid not in seen:
                seen[gid] = row

        games = list(seen.values())
        edges_over_3 = sum(
            1 for g in games
            if abs(g.get("spread_edge_pct") or 0) > 3
            or abs(g.get("total_edge_pct") or 0) > 3
        )

        return {
            "games": games,
            "count": len(games),
            "edges_over_3pct": edges_over_3,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pregame edges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/pregame-history")
def pregame_history(game_id: str = None):
    """Get all pregame snapshots for a specific game, ordered by time."""
    if not game_id:
        raise HTTPException(status_code=400, detail="game_id is required")
    try:
        if not db._is_connected():
            raise HTTPException(status_code=500, detail="Database not connected")

        result = db.client.table("pregame_snapshots").select("*").eq(
            "game_id", game_id
        ).order("snapshot_time", desc=False).execute()

        return {
            "game_id": game_id,
            "snapshots": result.data or [],
            "count": len(result.data or []),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pregame history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/internal/pregame-accuracy")
def internal_pregame_accuracy(sport: str = None, days: int = 30):
    """Pregame accuracy analysis: how OMI fair lines performed by hours-to-game bucket."""
    try:
        from pregame_capture import PregameCapture
        result = PregameCapture().get_pregame_accuracy_summary(
            sport.upper() if sport else None, days
        )
        return result
    except Exception as e:
        logger.error(f"Error running pregame accuracy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# COMPOSITE HISTORY
# =============================================================================

@app.post("/api/recalculate-composites")
async def recalculate_composites():
    """Recalculate composite scores and fair lines for all active games."""
    try:
        from composite_tracker import CompositeTracker
        tracker = CompositeTracker()
        return tracker.recalculate_all()
    except Exception as e:
        logger.error(f"Error recalculating composites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/composite-history/{game_id}")
async def get_composite_history(game_id: str):
    """Get composite score history for a game, ordered by timestamp ascending."""
    try:
        if not db._is_connected():
            raise HTTPException(status_code=500, detail="Database not connected")

        result = db.client.table("composite_history").select("*").eq(
            "game_id", game_id
        ).order(
            "timestamp", desc=False
        ).execute()

        return result.data or []
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting composite history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/composite/fast-refresh")
async def fast_refresh_live():
    """Trigger a fast refresh of fair lines for live games."""
    import threading
    try:
        from composite_tracker import CompositeTracker
        tracker = CompositeTracker()
        result = tracker.fast_refresh_live()
        return result
    except Exception as e:
        logger.error(f"Fast refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# EXCHANGE DATA
# =========================================================================

@app.post("/api/exchange/sync")
async def sync_exchanges():
    """Sync sports markets from Kalshi and Polymarket (background thread)."""
    import threading

    def _run_sync():
        try:
            from exchange_tracker import ExchangeTracker
            tracker = ExchangeTracker()
            result = tracker.sync_all()
            logger.info(f"[Exchange Sync] Complete: {result}")
        except Exception as e:
            logger.error(f"[Exchange Sync] Error: {e}")

    thread = threading.Thread(target=_run_sync, daemon=True)
    thread.start()
    return {"status": "sync_started", "message": "Exchange sync running in background"}


@app.get("/api/exchange/markets")
async def get_exchange_markets(
    exchange: Optional[str] = Query(None, description="Filter by exchange: kalshi or polymarket"),
    search: Optional[str] = Query(None, description="Search event titles"),
    limit: int = Query(50, description="Max results (max 200)"),
):
    """Get latest sports exchange markets."""
    try:
        from exchange_tracker import ExchangeTracker
        tracker = ExchangeTracker()
        markets = tracker.get_markets(exchange=exchange, search=search, limit=limit)
        return {"markets": markets, "count": len(markets)}
    except Exception as e:
        logger.error(f"Error getting exchange markets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/exchange/game/{game_id}")
async def get_game_exchange_data(game_id: str):
    """Get exchange contracts matched to a specific game, grouped by market with divergence."""
    try:
        from exchange_tracker import ExchangeTracker
        tracker = ExchangeTracker()
        contracts = tracker.get_game_exchange_data(game_id)

        # Group by market_type
        by_market: dict = {}
        for c in contracts:
            mtype = c.get("market_type") or "unknown"
            if mtype not in by_market:
                by_market[mtype] = []
            by_market[mtype].append({
                "exchange": c.get("exchange"),
                "event_title": c.get("event_title"),
                "subtitle": c.get("subtitle"),
                "contract_ticker": c.get("contract_ticker"),
                "yes_price": c.get("yes_price"),
                "no_price": c.get("no_price"),
                "volume": c.get("volume"),
                "open_interest": c.get("open_interest"),
                "price_change": c.get("price_change"),
                "snapshot_time": c.get("snapshot_time"),
                "status": c.get("status"),
            })

        # Calculate divergence vs book lines for this game
        divergence = {}
        try:
            if not db._is_connected():
                raise Exception("DB not connected")
            # Get latest book lines from cached_odds
            cached = db.client.table("cached_odds").select(
                "game_data"
            ).eq("game_id", game_id).limit(1).execute()
            if cached.data:
                game_data = cached.data[0].get("game_data", {})
                home_team = game_data.get("home_team", "")
                bookmakers_data = game_data.get("bookmakers", [])

                # Extract median book lines
                import statistics as stats_mod
                spread_lines, total_lines, ml_home_list, ml_away_list = [], [], [], []
                for bk in bookmakers_data:
                    for mkt in bk.get("markets", []):
                        key = mkt.get("key")
                        outcomes = mkt.get("outcomes", [])
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
                                    ml_home_list.append(o["price"])
                                elif o.get("name") != "Draw":
                                    ml_away_list.append(o["price"])

                def _american_to_prob(odds):
                    odds = int(odds)
                    if odds < 0:
                        return abs(odds) / (abs(odds) + 100)
                    return 100 / (odds + 100)

                # Moneyline divergence
                if "moneyline" in by_market and ml_home_list and ml_away_list:
                    med_home = stats_mod.median(ml_home_list)
                    med_away = stats_mod.median(ml_away_list)
                    book_home_prob = _american_to_prob(med_home)
                    book_away_prob = _american_to_prob(med_away)
                    total_vig = book_home_prob + book_away_prob
                    if total_vig > 0:
                        book_home_prob /= total_vig

                    ml_contracts = by_market["moneyline"]
                    # Find home team's contract via subtitle (NOT averaging all)
                    home_lower = home_team.lower()
                    home_words = [w for w in home_lower.split() if len(w) > 3]
                    exch_home_prob = None
                    exch_away_prob = None
                    for c in ml_contracts:
                        if not c.get("yes_price") or c["yes_price"] <= 0:
                            continue
                        sub = (c.get("subtitle") or "").lower()
                        if any(w in sub for w in home_words):
                            exch_home_prob = c["yes_price"] / 100.0
                        else:
                            exch_away_prob = c["yes_price"] / 100.0
                    if exch_home_prob is not None:
                        divergence["moneyline"] = {
                            "exchange_home_prob": round(exch_home_prob * 100, 1),
                            "exchange_away_prob": round((exch_away_prob or (1 - exch_home_prob)) * 100, 1),
                            "book_home_prob": round(book_home_prob * 100, 1),
                            "divergence_pct": round((exch_home_prob - book_home_prob) * 100, 1),
                        }

                # Spread divergence
                if "spread" in by_market and spread_lines:
                    med_spread = stats_mod.median(spread_lines)
                    book_impl = 0.50 + (-med_spread) * 0.03
                    sp_contracts = by_market["spread"]
                    exch_probs = [
                        c["yes_price"] / 100.0 for c in sp_contracts
                        if c.get("yes_price") and c["yes_price"] > 0
                    ]
                    if exch_probs:
                        exch_prob = sum(exch_probs) / len(exch_probs)
                        divergence["spread"] = {
                            "exchange_implied": round(exch_prob * 100, 1),
                            "book_implied": round(book_impl * 100, 1),
                            "divergence_pct": round((exch_prob - book_impl) * 100, 1),
                            "book_spread": med_spread,
                        }

                # Total divergence
                if "total" in by_market and total_lines:
                    med_total = stats_mod.median(total_lines)
                    tot_contracts = by_market["total"]
                    exch_probs = [
                        c["yes_price"] / 100.0 for c in tot_contracts
                        if c.get("yes_price") and c["yes_price"] > 0
                    ]
                    if exch_probs:
                        exch_over_prob = sum(exch_probs) / len(exch_probs)
                        divergence["total"] = {
                            "exchange_over_prob": round(exch_over_prob * 100, 1),
                            "book_total": med_total,
                        }
        except Exception as div_err:
            logger.debug(f"Exchange divergence calc failed for {game_id}: {div_err}")

        return {
            "contracts": contracts,
            "by_market": by_market,
            "divergence": divergence,
            "count": len(contracts),
        }
    except Exception as e:
        logger.error(f"Error getting game exchange data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MODEL FEEDBACK & CLOSING LINES
# =============================================================================

@app.get("/api/internal/model-feedback")
async def get_model_feedback(sport: str = None, days: int = 30):
    """Get latest calibration feedback rows with pillar metrics and CLV."""
    from model_feedback import ModelFeedback
    fb = ModelFeedback()
    return fb.get_latest_feedback(sport, days)


@app.post("/api/internal/run-feedback")
async def run_model_feedback(sport: str = None, min_games: int = 50, apply_weights: bool = False):
    """Run feedback analysis and optionally apply weight adjustments.

    1. Analyzes graded predictions for per-pillar metrics and CLV
    2. Writes results to calibration_feedback table
    3. If apply_weights=true, also applies bounded weight adjustments to calibration_config
    """
    from model_feedback import ModelFeedback
    fb = ModelFeedback()
    result = fb.run_feedback(sport, min_games)

    # Optionally apply weight adjustments
    if apply_weights:
        from engine.weight_calculator import apply_feedback_adjustments
        sports_to_adjust = []
        if sport:
            sports_to_adjust = [sport.upper()]
        else:
            sports_to_adjust = list(result.get("results", {}).keys())

        adjustments = {}
        for sp in sports_to_adjust:
            sp_result = result.get("results", {}).get(sp, {})
            if sp_result.get("status") == "success":
                adj = apply_feedback_adjustments(sp)
                adjustments[sp] = adj

        result["weight_adjustments"] = adjustments

    return result


@app.get("/api/internal/system-health")
def system_health():
    """Get system health report across all subsystems."""
    cached = _cache_get("system-health", 120)
    if cached is not None:
        return cached
    try:
        from system_health import SystemHealth
        def _query():
            health = SystemHealth()
            return health.run_all_checks()
        data = _with_scheduler_pause(_query)
        _cache_set("system-health", data)
        return data
    except Exception as e:
        logger.error(f"Error running system health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/internal/accuracy-summary")
def accuracy_summary(sport: str = None, days: int = 30):
    """Prediction accuracy reflection pool — how close OMI fair lines are to reality."""
    ck = f"acc-sum:{sport}:{days}"
    cached = _cache_get(ck, 300)
    if cached is not None:
        return cached
    try:
        from accuracy_tracker import AccuracyTracker
        def _query():
            tracker = AccuracyTracker()
            return tracker.get_accuracy_summary(sport=sport, days=days)
        data = _with_scheduler_pause(_query)
        _cache_set(ck, data)
        return data
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/internal/run-accuracy-reflection")
def run_accuracy_reflection():
    """Manually trigger accuracy reflection — process completed games."""
    try:
        from accuracy_tracker import AccuracyTracker
        tracker = AccuracyTracker()
        return tracker.run_accuracy_reflection(lookback_hours=720)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/internal/force-composite-recalc")
def force_composite_recalc():
    """Manually trigger a full composite recalc cycle (rewrites fair lines)."""
    try:
        from composite_tracker import CompositeTracker
        tracker = CompositeTracker()
        result = tracker.recalculate_all()
        return result
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/internal/closing-lines")
def get_closing_lines(sport: str = None, days: int = 7):
    """Get recent closing line captures for inspection."""
    from model_feedback import ModelFeedback
    fb = ModelFeedback()
    return fb.get_closing_lines(sport, days)


# =============================================================================
# ARB DESK API — Authenticated External Endpoints (v1)
# =============================================================================

ARB_API_KEY = os.getenv("ARB_API_KEY", "")
_bearer_scheme = HTTPBearer()

# Simple in-memory rate limiter: {ip: [timestamp, ...]}
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_WINDOW = 60  # seconds
_RATE_LIMIT_MAX = 600  # requests per window (dedicated partner key)


def _rate_limit_check(client_ip: str):
    """Enforce 600 requests per minute per IP."""
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW
    # Prune old entries
    _rate_limit_store[client_ip] = [
        t for t in _rate_limit_store[client_ip] if t > window_start
    ]
    if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded (600 req/min)")
    _rate_limit_store[client_ip].append(now)


async def verify_arb_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
):
    """Verify Bearer token and enforce rate limit."""
    if not ARB_API_KEY:
        raise HTTPException(status_code=500, detail="ARB_API_KEY not configured")
    if credentials.credentials != ARB_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    _rate_limit_check(request.client.host if request.client else "unknown")
    return True


def _sport_variants(sport: str) -> list[str]:
    """Get all DB variants for a sport (e.g. NCAAB -> [NCAAB, BASKETBALL_NCAAB, basketball_ncaab])."""
    sport_upper = sport.upper()
    return SPORT_KEY_VARIANTS.get(sport_upper, [sport_upper])


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

    # Parse clock "MM:SS" or "M:SS"
    clock_mins = 0.0
    if clock:
        try:
            parts = clock.split(":")
            clock_mins = float(parts[0]) + float(parts[1]) / 60.0 if len(parts) == 2 else float(parts[0])
        except (ValueError, IndexError):
            clock_mins = 0.0

    if s in ("NBA",):
        # Q1-Q4 are 12 min each
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


def calculate_live_ceq(
    pre_game_composite: float,
    live_score_diff: float,
    expected_margin: float,
    minutes_elapsed: float,
    total_minutes: float,
    favored_side: str = "pick",
    exchange_data: dict = None,
) -> tuple[float, bool | None]:
    """Adjust pre-game composite based on:
    1. Live score vs expected margin (primary ~70% influence)
    2. Live exchange price movement (secondary ~30% — free Kalshi/PM data)

    Returns (live_ceq, exchange_confirms) where exchange_confirms is
    True/False/None (None = no exchange data).
    """
    game_pct = min(minutes_elapsed / total_minutes, 1.0) if total_minutes > 0 else 0.0
    score_surprise = live_score_diff - (expected_margin * game_pct)
    surprise_factor = score_surprise / max(abs(expected_margin), 3.0)
    score_adjustment = surprise_factor * 0.15 * game_pct
    score_based_ceq = max(0.0, min(1.0, pre_game_composite + score_adjustment))

    # Exchange adjustment (only if we have exchange data)
    exchange_adjustment = 0.0
    exchange_confirms = None

    if exchange_data:
        current_exchange_prob = exchange_data.get("exchange_implied_prob")
        pregame_exchange_prob = exchange_data.get("pregame_exchange_prob")

        if current_exchange_prob and pregame_exchange_prob:
            exchange_move = current_exchange_prob - pregame_exchange_prob

            # Does exchange movement confirm or contradict our model?
            if favored_side == "home":
                exchange_confirmation = exchange_move
            elif favored_side == "away":
                exchange_confirmation = -exchange_move
            else:
                exchange_confirmation = 0.0

            # Scale: 10% exchange move = significant
            exchange_factor = exchange_confirmation / 0.10
            exchange_factor = max(-0.5, min(0.5, exchange_factor))

            # Apply with ~20% weight (score is still primary)
            if exchange_factor >= 0:
                exchange_adjustment = (1.0 - score_based_ceq) * exchange_factor * 0.15
            else:
                exchange_adjustment = (0.5 - score_based_ceq) * abs(exchange_factor) * 0.30

            exchange_confirms = exchange_confirmation > 0.02  # 2% threshold

    live_ceq = max(0.15, min(0.85, score_based_ceq + exchange_adjustment))
    return live_ceq, exchange_confirms


def calculate_live_flow(pregame_flow: float, exchange_implied_prob: float = None) -> float:
    """Live Flow score from current exchange prices.
    Flow > 0.5 = away edge, < 0.5 = home edge (matches pillar convention).
    """
    if exchange_implied_prob is None:
        return pregame_flow
    exchange_flow = 1.0 - exchange_implied_prob
    live_flow = exchange_flow * 0.6 + pregame_flow * 0.4
    return round(max(0.05, min(0.95, live_flow)), 3)


def _fetch_exchange_data_for_game(game_id: str, home_team: str) -> dict | None:
    """Fetch latest + earliest exchange snapshots for a game.
    Returns {kalshi_home_prob, polymarket_home_prob, exchange_implied_prob,
             pregame_exchange_prob, exchange_move} or None.
    """
    try:
        # Latest snapshots (already deduped by exchange_tracker)
        latest = db.client.table("exchange_data").select(
            "yes_price, exchange, subtitle, market_type, snapshot_time"
        ).eq("mapped_game_id", game_id).eq(
            "market_type", "moneyline"
        ).gt("yes_price", 0).order(
            "snapshot_time", desc=True
        ).limit(20).execute()
        contracts = latest.data or []
        if not contracts:
            logger.debug(f"[ArbAPI] No exchange contracts for {game_id}")
            return None

        # Identify home team contracts
        home_lower = home_team.lower()
        home_words = [w for w in home_lower.split() if len(w) > 3]

        kalshi_prob = None
        polymarket_prob = None
        for c in contracts:
            sub = (c.get("subtitle") or "").lower()
            is_home = any(w in sub for w in home_words) if home_words else False
            if not is_home:
                continue
            prob = c["yes_price"] / 100.0
            exch = c.get("exchange", "")
            if exch == "kalshi" and kalshi_prob is None:
                kalshi_prob = prob
            elif exch == "polymarket" and polymarket_prob is None:
                polymarket_prob = prob

        # Average available exchange prices
        probs = [p for p in [kalshi_prob, polymarket_prob] if p is not None]
        if not probs:
            return None
        exchange_implied = sum(probs) / len(probs)

        # Get pregame exchange price (earliest snapshot for this game)
        earliest = db.client.table("exchange_data").select(
            "yes_price, subtitle"
        ).eq("mapped_game_id", game_id).eq(
            "market_type", "moneyline"
        ).gt("yes_price", 0).order(
            "snapshot_time", desc=False
        ).limit(10).execute()
        pregame_prob = None
        for c in (earliest.data or []):
            sub = (c.get("subtitle") or "").lower()
            if any(w in sub for w in home_words) if home_words else False:
                pregame_prob = c["yes_price"] / 100.0
                break

        # Fallback: if no identifiable home contract in earliest, skip
        if pregame_prob is None:
            pregame_prob = exchange_implied  # treat as no movement

        exchange_move = exchange_implied - pregame_prob

        return {
            "kalshi_home_prob": round(kalshi_prob, 3) if kalshi_prob is not None else None,
            "polymarket_home_prob": round(polymarket_prob, 3) if polymarket_prob is not None else None,
            "exchange_implied_prob": round(exchange_implied, 3),
            "pregame_exchange_prob": round(pregame_prob, 3),
            "exchange_move": round(exchange_move, 3),
        }
    except Exception as e:
        logger.warning(f"[ArbAPI] Exchange fetch failed for {game_id}: {e}")
        return None


def _generate_live_signal_note(
    home_team: str, away_team: str,
    home_score: int, away_score: int,
    fair_spread: float, exchange_data: dict = None,
    exchange_confirms: bool = None,
) -> str:
    """Generate human-readable one-liner for live signal."""
    margin = home_score - away_score
    leading = home_team if margin > 0 else away_team if margin < 0 else "Tied"
    margin_abs = abs(margin)

    parts = []
    if margin != 0:
        parts.append(f"{leading} leading by {margin_abs}")
    else:
        parts.append(f"Game tied {home_score}-{away_score}")

    if fair_spread is not None:
        parts.append(f"pregame fair spread was {fair_spread:+.1f}")

    if margin != 0 and fair_spread is not None:
        expected = -float(fair_spread)
        if (margin > 0 and expected > 0) or (margin < 0 and expected < 0):
            parts.append("Score confirms pregame read")
        else:
            parts.append("Score contradicts pregame read")

    if exchange_data:
        exch_parts = []
        kp = exchange_data.get("kalshi_home_prob")
        pp = exchange_data.get("polymarket_home_prob")
        if kp is not None:
            exch_parts.append(f"Kalshi {int(kp*100)}c")
        if pp is not None:
            exch_parts.append(f"PM {int(pp*100)}c")
        pregame_p = exchange_data.get("pregame_exchange_prob")
        if exch_parts and pregame_p is not None:
            direction = "up" if exchange_data.get("exchange_move", 0) > 0 else "down"
            note = f"Exchange prices {'confirming' if exchange_confirms else 'diverging'}"
            note += f" — {', '.join(exch_parts)}, {direction} from pregame {int(pregame_p*100)}c"
            parts.append(note)

    return ". ".join(parts) + "."


def _fallback_abbrev(team_name: str) -> str:
    """Generate a fallback abbreviation from team name (first word, upper, max 4 chars)."""
    if not team_name:
        return ""
    first = team_name.split()[0].upper()
    return first[:4]


def _build_game_signal(pred: dict, comp_row: dict, live_game: dict = None,
                       exchange_cache: dict = None) -> dict:
    """Build a single game signal payload for the ARB API response.

    exchange_cache: optional pre-fetched {game_id: exchange_data_dict} to avoid
    per-game DB lookups in the bulk endpoint. If None and game is live, will
    fetch on demand.
    """
    game_id = pred.get("game_id", "")
    home_team = pred.get("home_team", "")
    away_team = pred.get("away_team", "")
    sport_key = _normalize_sport(pred.get("sport_key", ""))
    commence_time = pred.get("commence_time", "")

    composite = pred.get("composite_score", 0.5) or 0.5
    pregame_flow = pred.get("pillar_flow", 0.5) or 0.5

    # Fair lines from composite_history
    fair_spread = comp_row.get("fair_spread")
    fair_total = comp_row.get("fair_total")
    book_spread = comp_row.get("book_spread")
    book_total = comp_row.get("book_total")
    fair_ml_home = comp_row.get("fair_ml_home")
    fair_ml_away = comp_row.get("fair_ml_away")

    # Edge calculations
    spread_edge_pct = 0.0
    total_edge_pct = 0.0
    if fair_spread is not None and book_spread is not None:
        spread_edge_pct = calc_edge_pct(float(fair_spread), float(book_spread), "spread")
    if fair_total is not None and book_total is not None:
        total_edge_pct = calc_edge_pct(float(fair_total), float(book_total), "total")

    # Pick best edge (soft-cap before signal tier mapping)
    best_edge_pct = _cap_edge_display(max(spread_edge_pct, total_edge_pct))
    best_market = "spread" if spread_edge_pct >= total_edge_pct else "total"
    signal = determine_signal(best_edge_pct)
    confidence = edge_to_confidence(best_edge_pct)

    # Flow gate — downgrade HIGH/MAX EDGE when Flow pillar is weak
    flow_gated = False
    if signal in ("HIGH EDGE", "MAX EDGE") and pregame_flow < 0.55:
        signal = "LOW EDGE"
        flow_gated = True

    # Favored side
    favored_side = "pick"
    if fair_spread is not None:
        fs = float(fair_spread)
        if fs < -0.5:
            favored_side = "home"
        elif fs > 0.5:
            favored_side = "away"

    # Team abbreviations — prefer ESPN, fallback to first word of name
    home_abbrev = _fallback_abbrev(home_team)
    away_abbrev = _fallback_abbrev(away_team)
    if live_game:
        home_abbrev = live_game.get("home_abbrev") or home_abbrev
        away_abbrev = live_game.get("away_abbrev") or away_abbrev

    # Live status
    game_status = "pregame"
    period = None
    clock = None
    live_home_score = None
    live_away_score = None
    live_composite = None
    live_block = None

    if live_game and live_game.get("status") == "STATUS_IN_PROGRESS":
        game_status = "live"
        period = live_game.get("period", "")
        clock = live_game.get("clock", "")
        live_home_score = live_game.get("home_score", 0)
        live_away_score = live_game.get("away_score", 0)

        # Fetch exchange data (from cache or on-demand)
        exch_data = None
        if exchange_cache is not None:
            exch_data = exchange_cache.get(game_id)
        else:
            exch_data = _fetch_exchange_data_for_game(game_id, home_team)

        # Live CEQ adjustment (enhanced with exchange data)
        score_diff = live_home_score - live_away_score
        expected_margin = -(float(fair_spread)) if fair_spread is not None else (composite - 0.5) * 10
        total_mins = _total_minutes_for_sport(sport_key)
        elapsed = _estimate_minutes_elapsed(period or "", clock or "", sport_key)
        live_composite, exchange_confirms = calculate_live_ceq(
            composite, score_diff, expected_margin, elapsed, total_mins,
            favored_side=favored_side, exchange_data=exch_data,
        )

        # Recalculate edge with live composite if spread available
        if fair_spread is not None and book_spread is not None:
            deviation = live_composite * 100 - 50
            live_fair_spread = float(book_spread) - deviation * 0.15
            spread_edge_pct = calc_edge_pct(live_fair_spread, float(book_spread), "spread")
            fair_spread = round(live_fair_spread * 2) / 2

        best_edge_pct = _cap_edge_display(max(spread_edge_pct, total_edge_pct))
        best_market = "spread" if spread_edge_pct >= total_edge_pct else "total"
        signal = determine_signal(best_edge_pct)
        confidence = edge_to_confidence(best_edge_pct)

        # Flow gate (live path) — same threshold as pregame
        if signal in ("HIGH EDGE", "MAX EDGE") and pregame_flow < 0.55:
            signal = "LOW EDGE"
            flow_gated = True

        # Live confidence label
        margin_vs_expected = score_diff - expected_margin
        if abs(margin_vs_expected) < 2:
            live_confidence = "ON TRACK"
        elif (favored_side == "home" and margin_vs_expected > 0) or \
             (favored_side == "away" and margin_vs_expected < 0):
            live_confidence = "STRENGTHENED"
        else:
            live_confidence = "WEAKENED"

        # Live flow score
        exch_implied = exch_data.get("exchange_implied_prob") if exch_data else None
        live_flow = calculate_live_flow(pregame_flow, exch_implied)

        # Signal note
        signal_note = _generate_live_signal_note(
            home_team, away_team, live_home_score, live_away_score,
            fair_spread, exch_data, exchange_confirms,
        )

        live_block = {
            "home_score": live_home_score,
            "away_score": live_away_score,
            "period": period,
            "clock": clock,
            "current_margin": score_diff,
            "pregame_expected_margin": round(expected_margin, 1),
            "margin_vs_expected": round(margin_vs_expected, 1),
            "live_ceq": round(live_composite, 4),
            "live_confidence": live_confidence,
            "live_signal_note": signal_note,
            "exchange": {
                "kalshi_home_prob": exch_data["kalshi_home_prob"],
                "polymarket_home_prob": exch_data["polymarket_home_prob"],
                "pregame_exchange_prob": exch_data["pregame_exchange_prob"],
                "exchange_move": exch_data["exchange_move"],
                "exchange_confirms_model": exchange_confirms,
            } if exch_data else None,
            "live_flow_score": live_flow,
        }

    elif live_game and live_game.get("status") == "STATUS_FINAL":
        game_status = "final"

    result = {
        "game_id": game_id,
        "sport": sport_key,
        "home_team": home_team,
        "away_team": away_team,
        "home_abbrev": home_abbrev,
        "away_abbrev": away_abbrev,
        "commence_time": commence_time,
        "game_status": game_status,
        "favored_side": favored_side,
        "omi_fair_spread": fair_spread,
        "omi_fair_total": fair_total,
        "omi_fair_ml_home": fair_ml_home,
        "omi_fair_ml_away": fair_ml_away,
        "book_spread": book_spread,
        "book_total": book_total,
        "spread_edge_pct": round(spread_edge_pct, 1),
        "total_edge_pct": round(total_edge_pct, 1),
        "best_edge_pct": round(best_edge_pct, 1),
        "best_market": best_market,
        "signal": signal,
        "confidence_pct": confidence,
        "flow_gated": flow_gated,
        "composite_score": round(composite, 4),
        "pillar_scores": {
            "execution": pred.get("pillar_execution", 0.5),
            "incentives": pred.get("pillar_incentives", 0.5),
            "shocks": pred.get("pillar_shocks", 0.5),
            "time_decay": pred.get("pillar_time_decay", 0.5),
            "flow": pred.get("pillar_flow", 0.5),
            "game_environment": pred.get("pillar_game_environment", 0.5),
        },
    }

    if live_block:
        result["live"] = live_block

    return result


@app.get("/api/v1/edge-signal/bulk")
def arb_bulk_edge_signals(
    sport: str = Query(..., description="Sport key: NCAAB, NBA, NFL, etc."),
    _auth: bool = Depends(verify_arb_api_key),
):
    """
    Bulk edge signals for all upcoming games in a sport.
    Primary endpoint — called every 15 min by arb desk.
    Includes live CEQ adjustments for in-progress games.
    """
    sport_upper = sport.upper()
    sport_short = _normalize_sport(sport_upper)
    variants = _sport_variants(sport_short)

    try:
        # 1. Fetch predictions for sport (upcoming games)
        now_iso = datetime.now(timezone.utc).isoformat()
        preds_result = db.client.table("predictions").select("*").in_(
            "sport_key", variants
        ).gte(
            "commence_time", now_iso
        ).order("commence_time", desc=False).execute()
        predictions = preds_result.data or []

        # Also fetch recently started games (within last 4 hours) that may be live
        four_hours_ago = (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()
        live_preds_result = db.client.table("predictions").select("*").in_(
            "sport_key", variants
        ).lt("commence_time", now_iso).gte(
            "commence_time", four_hours_ago
        ).execute()
        live_predictions = live_preds_result.data or []
        predictions.extend(live_predictions)

        if not predictions:
            return {
                "sport": sport_short,
                "games": [],
                "count": 0,
                "live_count": 0,
                "timestamp": now_iso,
            }

        # 2. Batch-fetch latest composite_history per game
        game_ids = list(set(p["game_id"] for p in predictions))
        comp_by_game = {}
        for i in range(0, len(game_ids), 100):
            chunk = game_ids[i:i + 100]
            comp_result = db.client.table("composite_history").select(
                "game_id, fair_spread, fair_total, fair_ml_home, fair_ml_away, "
                "book_spread, book_total, book_ml_home, book_ml_away, "
                "composite_spread, composite_total, timestamp"
            ).in_("game_id", chunk).order("timestamp", desc=True).execute()
            for row in (comp_result.data or []):
                gid = row["game_id"]
                if gid not in comp_by_game:
                    comp_by_game[gid] = row

        # 3. Fetch ESPN live scores for this sport
        espn = ESPNScoreFetcher()
        live_scores = []
        if sport_short in ESPN_SPORTS:
            live_scores = espn.get_scores(sport_short)

        # Index live scores by team matching
        def _find_live_game(home: str, away: str) -> dict:
            for lg in live_scores:
                if teams_match(lg.get("home_team", ""), home) and teams_match(lg.get("away_team", ""), away):
                    return lg
                if teams_match(lg.get("home_team", ""), away) and teams_match(lg.get("away_team", ""), home):
                    return {
                        **lg,
                        "home_team": lg["away_team"],
                        "away_team": lg["home_team"],
                        "home_abbrev": lg.get("away_abbrev", ""),
                        "away_abbrev": lg.get("home_abbrev", ""),
                        "home_score": lg.get("away_score", 0),
                        "away_score": lg.get("home_score", 0),
                    }
            return {}

        # 4. Pre-identify live games and batch-fetch exchange data
        live_game_ids = []
        live_home_teams = {}
        for pred in predictions:
            lg = _find_live_game(pred.get("home_team", ""), pred.get("away_team", ""))
            if lg and lg.get("status") == "STATUS_IN_PROGRESS":
                gid = pred["game_id"]
                live_game_ids.append(gid)
                live_home_teams[gid] = pred.get("home_team", "")

        exchange_cache = {}
        if live_game_ids:
            # Batch-fetch exchange data for all live games in one query
            for i in range(0, len(live_game_ids), 50):
                chunk = live_game_ids[i:i + 50]
                try:
                    exch_result = db.client.table("exchange_data").select(
                        "mapped_game_id, yes_price, exchange, subtitle, market_type, snapshot_time"
                    ).in_("mapped_game_id", chunk).eq(
                        "market_type", "moneyline"
                    ).gt("yes_price", 0).order(
                        "snapshot_time", desc=True
                    ).limit(500).execute()

                    # Also fetch earliest snapshots for pregame prices
                    earliest_result = db.client.table("exchange_data").select(
                        "mapped_game_id, yes_price, subtitle, market_type"
                    ).in_("mapped_game_id", chunk).eq(
                        "market_type", "moneyline"
                    ).gt("yes_price", 0).order(
                        "snapshot_time", desc=False
                    ).limit(500).execute()

                    # Group latest by game_id
                    latest_by_game: dict[str, list] = defaultdict(list)
                    for row in (exch_result.data or []):
                        latest_by_game[row["mapped_game_id"]].append(row)

                    earliest_by_game: dict[str, list] = defaultdict(list)
                    for row in (earliest_result.data or []):
                        earliest_by_game[row["mapped_game_id"]].append(row)

                    # Build exchange_data dict per game
                    for gid in chunk:
                        home_team_name = live_home_teams.get(gid, "")
                        home_lower = home_team_name.lower()
                        home_words = [w for w in home_lower.split() if len(w) > 3]

                        contracts = latest_by_game.get(gid, [])
                        if not contracts:
                            continue

                        kalshi_prob = None
                        polymarket_prob = None
                        for c in contracts:
                            sub = (c.get("subtitle") or "").lower()
                            is_home = any(w in sub for w in home_words) if home_words else False
                            if not is_home:
                                continue
                            prob = c["yes_price"] / 100.0
                            exch = c.get("exchange", "")
                            if exch == "kalshi" and kalshi_prob is None:
                                kalshi_prob = prob
                            elif exch == "polymarket" and polymarket_prob is None:
                                polymarket_prob = prob

                        probs = [p for p in [kalshi_prob, polymarket_prob] if p is not None]
                        if not probs:
                            continue
                        exchange_implied = sum(probs) / len(probs)

                        # Pregame price from earliest snapshot
                        pregame_prob = None
                        for c in earliest_by_game.get(gid, []):
                            sub = (c.get("subtitle") or "").lower()
                            if any(w in sub for w in home_words) if home_words else False:
                                pregame_prob = c["yes_price"] / 100.0
                                break
                        if pregame_prob is None:
                            pregame_prob = exchange_implied

                        exchange_cache[gid] = {
                            "kalshi_home_prob": round(kalshi_prob, 3) if kalshi_prob is not None else None,
                            "polymarket_home_prob": round(polymarket_prob, 3) if polymarket_prob is not None else None,
                            "exchange_implied_prob": round(exchange_implied, 3),
                            "pregame_exchange_prob": round(pregame_prob, 3),
                            "exchange_move": round(exchange_implied - pregame_prob, 3),
                        }
                except Exception as exch_err:
                    logger.debug(f"[ArbAPI] Batch exchange fetch error: {exch_err}")

        # 5. Build response
        games = []
        live_count = 0
        for pred in predictions:
            gid = pred["game_id"]
            comp_row = comp_by_game.get(gid, {})
            live_game = _find_live_game(
                pred.get("home_team", ""),
                pred.get("away_team", ""),
            )
            signal = _build_game_signal(
                pred, comp_row, live_game or None,
                exchange_cache=exchange_cache,
            )
            games.append(signal)
            if signal.get("game_status") == "live":
                live_count += 1

        # Sort: live games first, then by best_edge_pct descending
        games.sort(key=lambda g: (
            0 if g["game_status"] == "live" else 1,
            -g["best_edge_pct"],
        ))

        return {
            "sport": sport_short,
            "games": games,
            "count": len(games),
            "live_count": live_count,
            "timestamp": now_iso,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ArbAPI] Bulk error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/edge-signal")
async def arb_single_edge_signal(
    game_id: str = Query(..., description="Game ID"),
    _auth: bool = Depends(verify_arb_api_key),
):
    """Single game edge signal with live status and exchange data."""
    try:
        # Fetch prediction
        pred_result = db.client.table("predictions").select("*").eq(
            "game_id", game_id
        ).order("predicted_at", desc=True).limit(1).execute()
        if not pred_result.data:
            raise HTTPException(status_code=404, detail=f"Game {game_id} not found")

        pred = pred_result.data[0]
        sport_short = _normalize_sport(pred.get("sport_key", ""))

        # Fetch latest composite_history
        comp_result = db.client.table("composite_history").select(
            "game_id, fair_spread, fair_total, fair_ml_home, fair_ml_away, "
            "book_spread, book_total, book_ml_home, book_ml_away, "
            "composite_spread, composite_total, timestamp"
        ).eq("game_id", game_id).order("timestamp", desc=True).limit(1).execute()
        comp_row = comp_result.data[0] if comp_result.data else {}

        # Fetch ESPN live status
        live_game = {}
        if sport_short in ESPN_SPORTS:
            espn = ESPNScoreFetcher()
            live_scores = espn.get_scores(sport_short)
            for lg in live_scores:
                if teams_match(lg.get("home_team", ""), pred.get("home_team", "")) and \
                   teams_match(lg.get("away_team", ""), pred.get("away_team", "")):
                    live_game = lg
                    break
                if teams_match(lg.get("home_team", ""), pred.get("away_team", "")) and \
                   teams_match(lg.get("away_team", ""), pred.get("home_team", "")):
                    live_game = {
                        **lg,
                        "home_team": lg["away_team"],
                        "away_team": lg["home_team"],
                        "home_abbrev": lg.get("away_abbrev", ""),
                        "away_abbrev": lg.get("home_abbrev", ""),
                        "home_score": lg.get("away_score", 0),
                        "away_score": lg.get("home_score", 0),
                    }
                    break

        # exchange_cache=None → _build_game_signal fetches on demand for live games
        signal = _build_game_signal(pred, comp_row, live_game or None)
        return signal

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ArbAPI] Single game error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/edge-signal/by-teams")
async def arb_edge_signal_by_teams(
    home: str = Query(..., description="Home team name (fuzzy match)"),
    away: str = Query(..., description="Away team name (fuzzy match)"),
    sport: str = Query(..., description="Sport key: NCAAB, NBA, NFL, etc."),
    _auth: bool = Depends(verify_arb_api_key),
):
    """Look up a game by team names (fuzzy match) and return edge signal."""
    sport_short = _normalize_sport(sport.upper())
    variants = _sport_variants(sport_short)

    try:
        # Fetch upcoming + recent predictions for this sport
        four_hours_ago = (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()
        result = db.client.table("predictions").select("*").in_(
            "sport_key", variants
        ).gte(
            "commence_time", four_hours_ago
        ).order("commence_time", desc=False).execute()
        predictions = result.data or []

        # Find matching game via fuzzy team matching
        matched_pred = None
        for pred in predictions:
            h = pred.get("home_team", "")
            a = pred.get("away_team", "")
            if teams_match(h, home) and teams_match(a, away):
                matched_pred = pred
                break
            if teams_match(h, away) and teams_match(a, home):
                matched_pred = pred
                break

        if not matched_pred:
            raise HTTPException(
                status_code=404,
                detail=f"No game found for {away} @ {home} in {sport_short}",
            )

        # Build signal same as single endpoint
        gid = matched_pred["game_id"]
        comp_result = db.client.table("composite_history").select(
            "game_id, fair_spread, fair_total, fair_ml_home, fair_ml_away, "
            "book_spread, book_total, book_ml_home, book_ml_away, "
            "composite_spread, composite_total, timestamp"
        ).eq("game_id", gid).order("timestamp", desc=True).limit(1).execute()
        comp_row = comp_result.data[0] if comp_result.data else {}

        # Fetch ESPN live status
        live_game = {}
        if sport_short in ESPN_SPORTS:
            espn = ESPNScoreFetcher()
            live_scores = espn.get_scores(sport_short)
            for lg in live_scores:
                if teams_match(lg.get("home_team", ""), matched_pred.get("home_team", "")) and \
                   teams_match(lg.get("away_team", ""), matched_pred.get("away_team", "")):
                    live_game = lg
                    break

        signal = _build_game_signal(matched_pred, comp_row, live_game or None)
        return signal

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ArbAPI] By-teams error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)