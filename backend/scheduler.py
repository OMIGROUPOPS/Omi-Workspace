"""
OMI Edge Scheduler

Tiered polling system:
- Pre-game: Every 30 min (all markets + props)
- Live: Every 2 min (main markets only)
- Live props: 2x per quarter/period

Also handles:
- Weather data fetching for outdoor games
- Game status tracking
"""
from datetime import datetime, timezone, timedelta
import logging
import time
import httpx

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from config import (
    ODDS_API_SPORTS, OUTDOOR_SPORTS, NFL_STADIUMS,
    PREGAME_POLL_INTERVAL_MINUTES, LIVE_POLL_INTERVAL_MINUTES,
    LIVE_PROPS_PER_QUARTER, OPEN_METEO_BASE, PROPS_ENABLED, PROP_MARKETS
)
from data_sources.odds_api import odds_client
from engine import analyze_all_games
from database import db
from internal_grader import InternalGrader
from accuracy_tracker import AccuracyTracker

logger = logging.getLogger(__name__)


# =============================================================================
# SCHEDULER PAUSE — lets dashboard endpoints grab a Supabase connection
# =============================================================================
_paused = False
_resume_timer = None

def is_paused() -> bool:
    return _paused

def pause_scheduler(seconds: int = 60):
    """Pause all scheduler jobs for `seconds`. Auto-resumes after."""
    global _paused, _resume_timer
    import threading
    _paused = True
    if _resume_timer is not None:
        _resume_timer.cancel()
    _resume_timer = threading.Timer(seconds, resume_scheduler)
    _resume_timer.daemon = True
    _resume_timer.start()
    logger.info(f"[Scheduler] PAUSED for {seconds}s")

def resume_scheduler():
    """Resume scheduler jobs immediately."""
    global _paused, _resume_timer
    _paused = False
    if _resume_timer is not None:
        _resume_timer.cancel()
        _resume_timer = None
    logger.info("[Scheduler] RESUMED")

def _check_paused(job_name: str) -> bool:
    """Return True if paused (caller should return early)."""
    if _paused:
        logger.debug(f"[Scheduler] {job_name} skipped (paused)")
        return True
    return False


def _run_with_timeout(fn, job_name: str, timeout: int = 30):
    """Run fn in a thread with a timeout. If it exceeds timeout, log and move on.
    Always sleeps 1s after completion to give API endpoints a window for Supabase calls."""
    import threading
    result = [None]
    error = [None]

    def _target():
        try:
            result[0] = fn()
        except Exception as e:
            error[0] = e

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        logger.warning(f"[Scheduler] {job_name} TIMED OUT after {timeout}s — moving on")
        time.sleep(1)
        return None
    # 1s gap between jobs — lets API endpoint threads grab a Supabase connection
    time.sleep(1)
    if error[0] is not None:
        raise error[0]
    return result[0]


# =============================================================================
# WEATHER FETCHING
# =============================================================================

def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch weather from Open-Meteo (free, no API key)."""
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m,wind_direction_10m,precipitation_probability,weather_code",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": "America/New_York"
        }
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(OPEN_METEO_BASE, params=params)
            response.raise_for_status()
            data = response.json()
        
        current = data.get("current", {})
        
        # Map weather codes to conditions
        weather_code = current.get("weather_code", 0)
        conditions = map_weather_code(weather_code)
        
        return {
            "temperature": current.get("temperature_2m", 70),
            "wind_speed": current.get("wind_speed_10m", 0),
            "wind_direction": current.get("wind_direction_10m", 0),
            "precipitation_prob": current.get("precipitation_probability", 0),
            "conditions": conditions
        }
        
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return {
            "temperature": 70,
            "wind_speed": 0,
            "wind_direction": 0,
            "precipitation_prob": 0,
            "conditions": "Unknown"
        }


def map_weather_code(code: int) -> str:
    """Map Open-Meteo weather codes to readable conditions."""
    code_map = {
        0: "Clear",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Foggy",
        51: "Light Drizzle",
        53: "Drizzle",
        55: "Heavy Drizzle",
        61: "Light Rain",
        63: "Rain",
        65: "Heavy Rain",
        66: "Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Light Snow",
        73: "Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Light Showers",
        81: "Showers",
        82: "Heavy Showers",
        85: "Light Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Hail",
        99: "Severe Thunderstorm"
    }
    return code_map.get(code, "Unknown")


def fetch_weather_for_game(game: dict, sport: str) -> bool:
    """Fetch and save weather for a game if it's outdoor."""
    if sport not in OUTDOOR_SPORTS:
        return False
    
    home_team = game.get("home_team")
    game_id = game.get("id")
    
    # Get stadium info
    stadium = NFL_STADIUMS.get(home_team)
    if not stadium:
        logger.warning(f"No stadium info for {home_team}")
        return False
    
    # Skip dome stadiums
    if stadium.get("dome", False):
        db.save_weather(
            game_id=game_id,
            sport=sport,
            temperature=72,
            wind_speed=0,
            wind_direction=0,
            precipitation_prob=0,
            conditions="Dome",
            is_dome=True
        )
        return True
    
    # Fetch weather
    weather = fetch_weather(stadium["lat"], stadium["lon"])
    
    db.save_weather(
        game_id=game_id,
        sport=sport,
        temperature=weather["temperature"],
        wind_speed=weather["wind_speed"],
        wind_direction=weather["wind_direction"],
        precipitation_prob=weather["precipitation_prob"],
        conditions=weather["conditions"],
        is_dome=False
    )
    
    logger.info(f"Weather for {home_team}: {weather['temperature']}°F, {weather['conditions']}, Wind: {weather['wind_speed']}mph")
    return True


# =============================================================================
# GAME STATUS MANAGEMENT
# =============================================================================

def update_game_statuses(games: list[dict], sport: str):
    """Update game statuses based on commence time."""
    now = datetime.now(timezone.utc)
    
    for game in games:
        game_id = game.get("id")
        commence_str = game.get("commence_time", "")
        
        try:
            commence_time = datetime.fromisoformat(commence_str.replace("Z", "+00:00"))
        except:
            continue
        
        hours_until = (commence_time - now).total_seconds() / 3600
        hours_since = -hours_until
        
        if hours_until > 0:
            # Game hasn't started
            status = "pregame"
            current_period = None
        elif hours_since < 4:
            # Game likely in progress (within 4 hours of start)
            status = "live"
            # We'd need ESPN or another source to get actual period
            current_period = "in_progress"
        else:
            # Game likely over
            status = "final"
            current_period = None
        
        db.save_game_status(game_id, sport, status, current_period)


def get_games_needing_live_update() -> list[dict]:
    """Get all games that need live polling."""
    return db.get_live_games()


def get_games_needing_pregame_update() -> list[dict]:
    """Get all games that need pre-game polling."""
    return db.get_pregame_games()


# =============================================================================
# PRE-GAME POLLING (Every 30 minutes)
# =============================================================================

def _pregame_cycle_inner() -> dict:
    """Inner pregame cycle logic."""
    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting PRE-GAME cycle at {start_time.isoformat()}")
    
    results = {
        "type": "pregame",
        "started_at": start_time.isoformat(),
        "sports": {},
        "total_games": 0,
        "total_snapshots": 0,
        "total_props": 0,
        "weather_fetched": 0,
        "errors": []
    }
    
    for sport in ODDS_API_SPORTS.keys():
        try:
            logger.info(f"[PREGAME] Processing {sport}...")
            
            # Fetch all markets in one call
            all_markets_data = odds_client.get_all_markets(sport)
            games = all_markets_data.get("games", [])
            logger.info(f"[PREGAME] Fetched {len(games)} games for {sport}")
            
            # Update game statuses
            update_game_statuses(games, sport)
            
            # Save line snapshots
            snapshots_saved = 0
            for game in games:
                snapshots_saved += db.save_game_snapshots(game, sport)
            results["total_snapshots"] += snapshots_saved
            
            # Fetch and save props
            props_saved = 0
            if PROPS_ENABLED and sport in PROP_MARKETS:
                props_data = odds_client.get_all_props_for_sport(sport)
                for prop_game in props_data:
                    parsed_props = odds_client.parse_props(
                        prop_game.get("props"),
                        prop_game.get("home_team"),
                        prop_game.get("away_team")
                    )
                    props_saved += db.save_props(prop_game["event_id"], sport, parsed_props)
                results["total_props"] += props_saved
            
            # Fetch weather for outdoor games
            weather_count = 0
            if sport in OUTDOOR_SPORTS:
                for game in games:
                    if fetch_weather_for_game(game, sport):
                        weather_count += 1
                results["weather_fetched"] += weather_count
            
            # Run analysis
            analyses = analyze_all_games(sport)
            predictions_saved = db.save_predictions_batch(analyses)
            logger.info(f"[PREGAME] {sport}: {len(analyses)} games analyzed, {predictions_saved} predictions saved")
            
            # Count edges by confidence
            edges_by_confidence = {"PASS": 0, "WATCH": 0, "EDGE": 0, "STRONG": 0, "RARE": 0}
            for analysis in analyses:
                conf = analysis.get("overall_confidence", "PASS")
                edges_by_confidence[conf] = edges_by_confidence.get(conf, 0) + 1
            
            results["sports"][sport] = {
                "games_fetched": len(games),
                "games_analyzed": len(analyses),
                "predictions_saved": predictions_saved,
                "snapshots_saved": snapshots_saved,
                "props_saved": props_saved,
                "weather_fetched": weather_count,
                "edges_by_confidence": edges_by_confidence
            }
            results["total_games"] += len(games)
            
            logger.info(f"[PREGAME] Completed {sport}: {len(analyses)} games, {props_saved} props")
            
        except Exception as e:
            error_msg = f"Error processing {sport}: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
    
    end_time = datetime.now(timezone.utc)
    results["completed_at"] = end_time.isoformat()
    results["duration_seconds"] = (end_time - start_time).total_seconds()
    
    remaining = odds_client.get_requests_remaining()
    results["api_requests_remaining"] = remaining
    
    logger.info(f"[PREGAME] Cycle completed in {results['duration_seconds']:.1f}s")
    logger.info(f"[PREGAME] API requests remaining: {remaining}")
    
    return results


def run_pregame_cycle() -> dict:
    """Pre-game polling cycle with timeout protection."""
    if _check_paused("pregame_cycle"):
        return {"skipped": "paused"}
    try:
        return _run_with_timeout(_pregame_cycle_inner, "pregame_cycle", timeout=120) or {"error": "timeout"}
    except Exception as e:
        logger.error(f"[PREGAME] Cycle failed: {e}")
        return {"error": str(e)}


# =============================================================================
# LIVE POLLING (Every 5 minutes)
# =============================================================================

def _detect_line_movement(game: dict, sport: str) -> list[dict]:
    """Detect significant line movements (>0.5 pts spread/total, >10 ML) for a game.
    Returns list of movements with game_id, market_type, old_line, new_line, diff."""
    from engine.analyzer import fetch_line_context
    parsed = odds_client.parse_game_odds(game)
    game_id = parsed["game_id"]
    movements = []

    line_ctx = fetch_line_context(game_id, sport)
    prev_line = line_ctx.get("current_line")

    # Check spread movement
    for book_key, markets in parsed.get("bookmakers", {}).items():
        spread = markets.get("spreads", {}).get("home", {})
        if spread and prev_line is not None:
            new_line = spread.get("line")
            if new_line is not None:
                diff = abs(new_line - prev_line)
                if diff > 0.5:
                    movements.append({
                        "game_id": game_id, "market": "spread", "book": book_key,
                        "old": prev_line, "new": new_line, "diff": diff
                    })
                break  # Only check one book for movement trigger
    return movements


def _live_cycle_inner() -> dict:
    """Inner live cycle logic."""
    from engine import analyze_all_games
    from engine.analyzer import analyze_game, fetch_line_context

    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting LIVE cycle at {start_time.isoformat()}")

    results = {
        "type": "live",
        "started_at": start_time.isoformat(),
        "sports": {},
        "total_live_games": 0,
        "total_snapshots": 0,
        "recalcs_triggered": 0,
        "errors": []
    }

    for sport in ODDS_API_SPORTS.keys():
        try:
            # Get live games only
            live_games = odds_client.get_live_games(sport)

            if not live_games:
                continue

            logger.info(f"[LIVE] Found {len(live_games)} live games for {sport}")

            snapshots_saved = 0
            recalcs = 0
            for game in live_games:
                # Detect line movement BEFORE saving new snapshots
                movements = _detect_line_movement(game, sport)

                # Save snapshots
                snapshots_saved += db.save_game_snapshots(game, sport)

                # If significant movement detected, trigger recalculation
                if movements:
                    for mv in movements:
                        logger.info(
                            f"RECALC TRIGGERED for game {mv['game_id']}: "
                            f"{mv['market']} line moved from {mv['old']} to {mv['new']} "
                            f"(diff={mv['diff']:.1f}, book={mv['book']})"
                        )
                    try:
                        game_id = movements[0]["game_id"]
                        line_ctx = fetch_line_context(game_id, sport)
                        old_pred = db.get_prediction(game_id, sport)
                        old_composite = old_pred.get("composite", 0) if old_pred else 0

                        analysis = analyze_game(
                            game, sport,
                            opening_line=line_ctx.get("opening_line"),
                            line_snapshots=line_ctx.get("line_snapshots")
                        )
                        db.save_predictions_batch([analysis])
                        new_composite = analysis.get("composite", 0)
                        logger.info(
                            f"RECALC COMPLETE for game {game_id}: "
                            f"new composite = {new_composite:.3f}, old = {old_composite:.3f}"
                        )
                        recalcs += 1
                    except Exception as e:
                        logger.error(f"[LIVE] Recalc failed for game {movements[0]['game_id']}: {e}")

            results["sports"][sport] = {
                "live_games": len(live_games),
                "snapshots_saved": snapshots_saved,
                "recalcs_triggered": recalcs
            }
            results["total_live_games"] += len(live_games)
            results["total_snapshots"] += snapshots_saved
            results["recalcs_triggered"] += recalcs

        except Exception as e:
            error_msg = f"[LIVE] Error processing {sport}: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

    end_time = datetime.now(timezone.utc)
    results["completed_at"] = end_time.isoformat()
    results["duration_seconds"] = (end_time - start_time).total_seconds()

    if results["total_live_games"] > 0:
        logger.info(
            f"[LIVE] Cycle completed: {results['total_live_games']} games, "
            f"{results['total_snapshots']} snapshots, {results['recalcs_triggered']} recalcs"
        )

    return results


def run_live_cycle() -> dict:
    """Live polling cycle with timeout protection."""
    if _check_paused("live_cycle"):
        return {"skipped": "paused"}
    try:
        return _run_with_timeout(_live_cycle_inner, "live_cycle", timeout=30) or {"error": "timeout"}
    except Exception as e:
        logger.error(f"[LIVE] Cycle failed: {e}")
        return {"error": str(e)}


# =============================================================================
# LIVE PROPS POLLING (At quarter/period breaks)
# =============================================================================

def _live_props_cycle_inner() -> dict:
    """Inner live props cycle logic."""
    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting LIVE PROPS cycle at {start_time.isoformat()}")
    
    results = {
        "type": "live_props",
        "started_at": start_time.isoformat(),
        "sports": {},
        "total_props": 0,
        "errors": []
    }
    
    if not PROPS_ENABLED:
        logger.info("[LIVE PROPS] Props disabled, skipping")
        return results
    
    for sport in ODDS_API_SPORTS.keys():
        if sport not in PROP_MARKETS:
            continue
        
        try:
            # Get live games
            live_games = odds_client.get_live_games(sport)
            
            if not live_games:
                continue
            
            logger.info(f"[LIVE PROPS] Fetching props for {len(live_games)} live {sport} games")
            
            props_saved = 0
            for game in live_games:
                game_id = game.get("id")
                props_data = odds_client.get_single_game_props(sport, game_id)
                
                if props_data:
                    parsed_props = odds_client.parse_props(
                        props_data,
                        game.get("home_team"),
                        game.get("away_team")
                    )
                    props_saved += db.save_props(game_id, sport, parsed_props)
            
            results["sports"][sport] = {
                "live_games": len(live_games),
                "props_saved": props_saved
            }
            results["total_props"] += props_saved
            
        except Exception as e:
            error_msg = f"[LIVE PROPS] Error processing {sport}: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
    
    end_time = datetime.now(timezone.utc)
    results["completed_at"] = end_time.isoformat()
    results["duration_seconds"] = (end_time - start_time).total_seconds()
    
    logger.info(f"[LIVE PROPS] Cycle completed: {results['total_props']} props saved")
    
    return results


def run_live_props_cycle() -> dict:
    """Live props polling with timeout protection."""
    if _check_paused("live_props_cycle"):
        return {"skipped": "paused"}
    try:
        return _run_with_timeout(_live_props_cycle_inner, "live_props_cycle", timeout=30) or {"error": "timeout"}
    except Exception as e:
        logger.error(f"[LIVE PROPS] Cycle failed: {e}")
        return {"error": str(e)}


# =============================================================================
# GRADING CYCLE (Every 60 minutes)
# =============================================================================

def _grading_cycle_inner() -> dict:
    """Inner grading cycle logic."""
    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting GRADING cycle at {start_time.isoformat()}")

    grader = InternalGrader()
    result = grader.grade_games()

    auto = result.get("auto_grader", {})
    logger.info(
        f"[GRADING] Completed: "
        f"{result.get('bootstrapped_game_results', 0)} bootstrapped, "
        f"{auto.get('graded', 0)} games scored via ESPN, "
        f"{result.get('prediction_grades_created', 0)} prediction_grades created"
    )

    if result.get("errors"):
        for err in result["errors"]:
            logger.error(f"[GRADING] Error: {err}")

    end_time = datetime.now(timezone.utc)
    result["duration_seconds"] = (end_time - start_time).total_seconds()
    return result


def run_grading_cycle() -> dict:
    """Grading cycle with timeout protection."""
    if _check_paused("grading_cycle"):
        return {"skipped": "paused"}
    try:
        return _run_with_timeout(_grading_cycle_inner, "grading_cycle", timeout=60) or {"error": "timeout"}
    except Exception as e:
        logger.error(f"[GRADING] Cycle failed: {e}")
        return {"error": str(e)}


# =============================================================================
# COMBINED ANALYSIS CYCLE (backward compatibility)
# =============================================================================

def run_analysis_cycle() -> dict:
    """Run a complete analysis cycle - combines pregame + live."""
    pregame_result = run_pregame_cycle()
    live_result = run_live_cycle()
    
    return {
        "pregame": pregame_result,
        "live": live_result
    }


# =============================================================================
# DAILY FEEDBACK LOOP
# =============================================================================

def _daily_feedback_inner():
    """Inner daily feedback logic."""
    logger.info("[DailyFeedback] Starting daily feedback cycle")
    from model_feedback import ModelFeedback

    fb = ModelFeedback()
    sports = ["NBA", "NCAAB", "NHL", "EPL", "NFL", "NCAAF"]
    results = {}

    for sport in sports:
        try:
            result = fb.run_and_apply_feedback(sport, min_games=50)
            sp_result = result.get("results", {}).get(sport, {})
            status = sp_result.get("status", "unknown")
            sample = sp_result.get("sample_size", 0)
            results[sport] = {"status": status, "sample_size": sample}
            logger.info(f"[DailyFeedback] {sport}: {status} (n={sample})")
        except Exception as e:
            logger.error(f"[DailyFeedback] {sport} failed: {e}")
            results[sport] = {"error": str(e)}

    logger.info(f"[DailyFeedback] Complete: {list(results.keys())}")
    return results


def run_daily_feedback():
    """Daily feedback with timeout protection."""
    if _check_paused("daily_feedback"):
        return
    try:
        return _run_with_timeout(_daily_feedback_inner, "daily_feedback", timeout=60)
    except Exception as e:
        logger.error(f"[DailyFeedback] Failed: {e}")


# =============================================================================
# SCHEDULER SETUP
# =============================================================================

def start_scheduler():
    """Start the background scheduler with tiered polling.

    IMPORTANT: All jobs are staggered so nothing fires in the first 60 seconds.
    This ensures the HTTP server can respond to health checks immediately.
    """
    scheduler = BackgroundScheduler()
    now = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------
    # Helper: all jobs get a delayed first run so startup isn't a thundering herd
    # -------------------------------------------------------------------------
    def _delayed(seconds):
        return now + timedelta(seconds=seconds)

    # =========================================================================
    # ESSENTIAL JOBS ONLY — cut from 14 to 5 to stop exhausting Supabase
    # connections.  Non-critical jobs commented out below.
    # =========================================================================

    # 1. Pre-game polling: Every 10 minutes (first run at +120s)
    #    Feeds fresh FanDuel/DraftKings lines into cached_odds so
    #    fast_refresh reads current book lines for the chart.
    scheduler.add_job(
        func=run_pregame_cycle,
        trigger=IntervalTrigger(minutes=10),
        id="pregame_cycle",
        name="Pre-game polling (all markets + props)",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=30,
        next_run_time=_delayed(120),
    )

    # 2. Live polling: Every 5 minutes (first run at +70s)
    scheduler.add_job(
        func=run_live_cycle,
        trigger=IntervalTrigger(minutes=LIVE_POLL_INTERVAL_MINUTES),
        id="live_cycle",
        name="Live game polling (main markets)",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=30,
        next_run_time=_delayed(70),
    )

    # 3. Composite recalc: Every 20 minutes (first run at +120s)
    def run_composite_recalc():
        if _check_paused("composite_recalc"):
            return
        def _inner():
            from composite_tracker import CompositeTracker
            tracker = CompositeTracker()
            result = tracker.recalculate_all()
            recalced = result.get("recalculated", 0)
            skipped = result.get("skipped_unchanged", 0)
            errs = result.get("errors", 0)
            logger.info(
                f"[CompositeRecalc] Done: {recalced} recalculated, "
                f"{skipped} unchanged, {errs} errors"
            )
        try:
            _run_with_timeout(_inner, "composite_recalc", timeout=120)
        except Exception as e:
            logger.error(f"[CompositeRecalc] Failed: {e}")

    scheduler.add_job(
        func=run_composite_recalc,
        trigger=IntervalTrigger(minutes=20),
        id="composite_recalc",
        name="Recalculate composite scores and fair lines",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=30,
        next_run_time=_delayed(120),
    )

    # 4. Fast refresh: Every 30 seconds (first run at +90s)
    def run_fast_refresh():
        if _check_paused("fast_refresh"):
            return
        def _inner():
            from composite_tracker import CompositeTracker
            tracker = CompositeTracker()
            result = tracker.fast_refresh_live()
            refreshed = result.get("refreshed", 0)
            live = result.get("live_games", 0)
            if refreshed > 0 or live > 0:
                logger.info(
                    f"[FastRefresh] Done: {refreshed} refreshed out of {live} live games"
                )
        try:
            _run_with_timeout(_inner, "fast_refresh", timeout=30)
        except Exception as e:
            logger.error(f"[FastRefresh] Failed: {e}")

    scheduler.add_job(
        func=run_fast_refresh,
        trigger=IntervalTrigger(seconds=30),
        id="fast_refresh_live",
        name="Fast refresh fair lines + live CEQ for live games",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=30,
        next_run_time=_delayed(90),
    )

    # 5. Closing line capture: Every 10 minutes (first run at +90s)
    from closing_line_capture import run_closing_line_capture
    scheduler.add_job(
        func=run_closing_line_capture,
        trigger=IntervalTrigger(minutes=10),
        id="closing_line_capture",
        name="Capture closing lines before game start",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=30,
        next_run_time=_delayed(100),
    )

    # =========================================================================
    # NON-CRITICAL JOBS — disabled to reduce Supabase connection pressure.
    # Re-enable once connection pooling / PgBouncer is in place.
    # =========================================================================

    # # Live props polling: Every 7 minutes
    # scheduler.add_job(
    #     func=run_live_props_cycle,
    #     trigger=IntervalTrigger(minutes=7),
    #     id="live_props_cycle",
    #     name="Live props polling (2x per quarter)",
    #     replace_existing=True, max_instances=1, misfire_grace_time=30,
    #     next_run_time=_delayed(80),
    # )

    # Exchange sync: Every 15 minutes
    def run_exchange_sync():
        if _check_paused("exchange_sync"): return
        def _inner():
            from exchange_tracker import ExchangeTracker
            tracker = ExchangeTracker()
            result = tracker.sync_all()
            logger.info(f"[ExchangeSync] {result}")
        try: _run_with_timeout(_inner, "exchange_sync", timeout=30)
        except Exception as e: logger.error(f"[ExchangeSync] Failed: {e}")
    scheduler.add_job(
        func=run_exchange_sync,
        trigger=IntervalTrigger(minutes=15),
        id="exchange_sync",
        name="Sync Kalshi + Polymarket exchange data",
        replace_existing=True, max_instances=1, misfire_grace_time=30,
        next_run_time=_delayed(100),
    )

    # Pregame capture: Every 15 minutes
    def run_pregame_capture():
        if _check_paused("pregame_capture"): return
        def _inner():
            from pregame_capture import PregameCapture
            result = PregameCapture().capture_all()
            logger.info(f"[PregameCapture] {result}")
        try: _run_with_timeout(_inner, "pregame_capture", timeout=30)
        except Exception as e: logger.error(f"[PregameCapture] Failed: {e}")
    scheduler.add_job(
        func=run_pregame_capture,
        trigger=IntervalTrigger(minutes=15),
        id="pregame_capture",
        name="Pregame fair line capture",
        replace_existing=True, max_instances=1, misfire_grace_time=30,
        next_run_time=_delayed(110),
    )

    # Grading: Every 60 minutes
    scheduler.add_job(
        func=run_grading_cycle,
        trigger=IntervalTrigger(minutes=60),
        id="grading_cycle",
        name="Grade completed games (ESPN scores + prediction_grades)",
        replace_existing=True, max_instances=1, misfire_grace_time=30,
        next_run_time=_delayed(180),
    )

    # # Accuracy reflection: Every 60 minutes
    # def run_accuracy_reflection():
    #     if _check_paused("accuracy_reflection"): return
    #     def _inner():
    #         tracker = AccuracyTracker()
    #         result = tracker.run_accuracy_reflection(lookback_hours=48)
    #         logger.info(f"[Scheduler] Accuracy reflection: {result}")
    #     try: _run_with_timeout(_inner, "accuracy_reflection", timeout=30)
    #     except Exception as e: logger.error(f"[Scheduler] Accuracy reflection failed: {e}")
    # scheduler.add_job(
    #     func=run_accuracy_reflection,
    #     trigger='interval', minutes=60,
    #     id="accuracy_reflection",
    #     name="Prediction accuracy reflection pool",
    #     next_run_time=_delayed(300), max_instances=1, misfire_grace_time=30,
    # )

    # # System health check: Every 6 hours
    # def run_health_check_job():
    #     if _check_paused("health_check"): return
    #     def _inner():
    #         from system_health import run_health_check
    #         run_health_check()
    #     try: _run_with_timeout(_inner, "health_check", timeout=30)
    #     except Exception as e: logger.error(f"[HealthCheck] Job failed: {e}")
    # scheduler.add_job(
    #     func=run_health_check_job,
    #     trigger=IntervalTrigger(hours=6),
    #     id="health_check",
    #     name="System health check (all subsystems)",
    #     replace_existing=True, max_instances=1, misfire_grace_time=30,
    #     next_run_time=_delayed(200),
    # )

    # # Exchange cleanup: Daily at 4 AM UTC
    # def run_exchange_cleanup():
    #     if _check_paused("exchange_cleanup"): return
    #     def _inner():
    #         from exchange_tracker import ExchangeTracker
    #         tracker = ExchangeTracker()
    #         result = tracker.cleanup_unmapped(hours_old=24)
    #         logger.info(f"[ExchangeCleanup] {result}")
    #     try: _run_with_timeout(_inner, "exchange_cleanup", timeout=30)
    #     except Exception as e: logger.error(f"[ExchangeCleanup] Failed: {e}")
    # scheduler.add_job(
    #     func=run_exchange_cleanup,
    #     trigger=CronTrigger(hour=4, minute=0),
    #     id="exchange_cleanup",
    #     name="Clean up unmapped Polymarket rows",
    #     replace_existing=True, max_instances=1, misfire_grace_time=30,
    # )

    # # Performance cache: Every 5 minutes
    # from perf_cache import refresh_performance_cache
    # scheduler.add_job(
    #     func=refresh_performance_cache,
    #     trigger=IntervalTrigger(minutes=5),
    #     id="perf_cache_refresh",
    #     name="Pre-fetch performance dashboard data via RPC",
    #     replace_existing=True, max_instances=1, misfire_grace_time=30,
    #     next_run_time=_delayed(60),
    # )

    # # Daily feedback: 6 AM UTC
    # scheduler.add_job(
    #     func=run_daily_feedback,
    #     trigger=CronTrigger(hour=6, minute=0),
    #     id="daily_feedback",
    #     name="Daily model feedback and weight adjustment",
    #     replace_existing=True, max_instances=1, misfire_grace_time=30,
    # )

    scheduler.start()
    logger.info("Scheduler started — 8 active jobs:")
    logger.info(f"  1. Pre-game: every 10 min (first at +120s)")
    logger.info(f"  2. Live: every {LIVE_POLL_INTERVAL_MINUTES} min (first at +70s)")
    logger.info(f"  3. Fast refresh + live CEQ: every 30s (first at +90s)")
    logger.info(f"  4. Closing line capture: every 10 min (first at +100s)")
    logger.info(f"  5. Exchange sync: every 15 min (first at +100s)")
    logger.info(f"  6. Pregame capture: every 15 min (first at +110s)")
    logger.info(f"  7. Composite recalc: every 20 min (first at +120s)")
    logger.info(f"  8. Grading: every 60 min (first at +180s)")
    logger.info(f"  DISABLED: live_props, accuracy_reflection, health_check,")
    logger.info(f"            exchange_cleanup, perf_cache, daily_feedback")
    logger.info(f"  All jobs: max_instances=1, misfire_grace_time=30s")

    return scheduler


def run_once():
    """Run a single analysis cycle (useful for testing)."""
    print("Running single analysis cycle...")
    result = run_analysis_cycle()
    
    print("\n=== PRE-GAME RESULTS ===")
    pregame = result.get("pregame", {})
    print(f"Duration: {pregame.get('duration_seconds', 0):.1f}s")
    print(f"Total games: {pregame.get('total_games', 0)}")
    print(f"Total snapshots: {pregame.get('total_snapshots', 0)}")
    print(f"Total props: {pregame.get('total_props', 0)}")
    print(f"Weather fetched: {pregame.get('weather_fetched', 0)}")
    print(f"API requests remaining: {pregame.get('api_requests_remaining', '?')}")
    
    for sport, data in pregame.get("sports", {}).items():
        print(f"\n{sport}:")
        print(f"  Games: {data.get('games_analyzed', 0)}")
        print(f"  Props: {data.get('props_saved', 0)}")
        print(f"  Edges: {data.get('edges_by_confidence', {})}")
    
    print("\n=== LIVE RESULTS ===")
    live = result.get("live", {})
    print(f"Live games: {live.get('total_live_games', 0)}")
    print(f"Snapshots: {live.get('total_snapshots', 0)}")
    
    if pregame.get("errors") or live.get("errors"):
        print(f"\nErrors: {pregame.get('errors', [])} {live.get('errors', [])}")
    
    return result


if __name__ == "__main__":
    run_once()