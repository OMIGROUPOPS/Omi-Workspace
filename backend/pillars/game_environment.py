"""
Pillar 6: Game Environment & Pace
Weight: Used to enhance totals analysis

Measures: Expected scoring pace and environment factors
- NHL: Goals for/against averages, PP%/PK% matchups
- NBA: Team pace ratings, offensive/defensive efficiency
- NFL: Weather, dome/outdoor, team scoring tendencies

This pillar enhances totals (over/under) edge detection.
"""
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def calculate_game_environment_score(
    sport: str,
    home_team: str,
    away_team: str,
    total_line: Optional[float] = None,
    nhl_stats: Optional[dict] = None,
    nba_stats: Optional[dict] = None,
    weather_data: Optional[dict] = None,
    game_time: Optional[any] = None,
    team_stats: Optional[dict] = None,
    market_type: str = "totals",
) -> dict:
    """
    Calculate game environment score.

    For TOTALS (default):
    - score > 0.5: Lean OVER (high-scoring environment expected)
    - score < 0.5: Lean UNDER (low-scoring environment expected)

    For SPREAD/MONEYLINE:
    - score > 0.5: Environment favors AWAY (fast pace suits away team)
    - score < 0.5: Environment favors HOME (slow pace, weather advantage)

    Args:
        team_stats: Generic stats from Supabase team_stats table.
            Format: {"home": {...supabase row...}, "away": {...supabase row...}}
            Used as fallback when sport-specific stats not provided.
        market_type: "totals", "spread", or "moneyline"

    Returns dict with score, expected_total, and breakdown.
    """
    # Build sport-specific stats from generic team_stats if needed
    # NCAAB uses different baselines: 40-min game, ~68 possessions, ~105 efficiency
    if not nba_stats and team_stats and sport in ("NBA", "NCAAB"):
        home = team_stats.get("home", {})
        away = team_stats.get("away", {})
        default_pace = 68 if sport == "NCAAB" else 100
        default_rating = 105 if sport == "NCAAB" else 110
        if home or away:
            nba_stats = {
                "home": {
                    "pace": home.get("pace") or default_pace,
                    "off_rating": home.get("offensive_rating") or default_rating,
                    "def_rating": home.get("defensive_rating") or default_rating,
                },
                "away": {
                    "pace": away.get("pace") or default_pace,
                    "off_rating": away.get("offensive_rating") or default_rating,
                    "def_rating": away.get("defensive_rating") or default_rating,
                },
            }

    if not nhl_stats and team_stats and sport == "NHL":
        home = team_stats.get("home", {})
        away = team_stats.get("away", {})
        if home or away:
            nhl_stats = {
                "home": {
                    "goals_for_per_game": home.get("points_per_game") or 3.0,
                    "goals_against_per_game": home.get("points_allowed_per_game") or 3.0,
                },
                "away": {
                    "goals_for_per_game": away.get("points_per_game") or 3.0,
                    "goals_against_per_game": away.get("points_allowed_per_game") or 3.0,
                },
            }

    if sport == "NHL" and nhl_stats:
        return _calculate_nhl_environment(home_team, away_team, total_line, nhl_stats)
    elif sport in ("NBA", "NCAAB") and nba_stats:
        return _calculate_nba_environment(home_team, away_team, total_line, nba_stats, sport=sport)
    elif sport in ("NFL", "NCAAF"):
        return _calculate_nfl_environment(home_team, away_team, total_line, weather_data, game_time, team_stats)
    elif sport == "EPL" and team_stats:
        return _calculate_epl_environment(home_team, away_team, total_line, team_stats)
    else:
        return _default_environment()


def _calculate_nfl_environment(
    home_team: str,
    away_team: str,
    total_line: Optional[float],
    weather_data: Optional[dict],
    game_time: Optional[any],
    team_stats: Optional[dict] = None,
) -> dict:
    """
    NFL/NCAAF environment calculation including weather and team scoring stats.

    Weather factors:
    - Wind >15mph affects passing game
    - Rain/snow affects totals (lean under)
    - Extreme cold affects kicking

    Team stats:
    - points_per_game + points_allowed_per_game → expected total
    """
    reasoning_parts = []
    score = 0.5

    # Try to fetch weather if not provided
    if weather_data is None and game_time is not None:
        try:
            from data_sources.weather import get_game_weather_sync
            weather_data = get_game_weather_sync(home_team, game_time)
        except Exception as e:
            logger.warning(f"Could not fetch weather: {e}")

    weather_impact = 0

    if weather_data and weather_data.get("available"):
        if weather_data.get("indoor"):
            reasoning_parts.append(f"Indoor: {weather_data.get('stadium', 'dome')} - no weather impact")
        else:
            # Outdoor stadium with weather data
            impact = weather_data.get("impact", {})
            weather_impact = impact.get("total_impact", 0)

            if weather_impact != 0:
                score += weather_impact
                reasoning_parts.append(impact.get("reasoning", "Weather affects game"))

            # Add specific weather details
            weather = weather_data.get("weather", {})
            if weather:
                temp = weather.get("temperature", 70)
                wind = weather.get("wind_speed", 0)
                conditions = weather.get("conditions", "Clear")

                if not reasoning_parts or weather_impact == 0:
                    reasoning_parts.append(f"Weather: {temp:.0f}°F, wind {wind:.0f}mph, {conditions}")
    else:
        reasoning_parts.append("Weather data unavailable")

    # Calculate expected total from team stats if available
    expected_total = None
    if team_stats:
        home = team_stats.get("home", {})
        away = team_stats.get("away", {})
        home_ppg = home.get("points_per_game")
        home_papg = home.get("points_allowed_per_game")
        away_ppg = away.get("points_per_game")
        away_papg = away.get("points_allowed_per_game")

        if home_ppg and away_papg and away_ppg and home_papg:
            # Expected home score = (home off + away def) / 2
            exp_home = (home_ppg + away_papg) / 2
            exp_away = (away_ppg + home_papg) / 2
            expected_total = exp_home + exp_away

            if total_line:
                line_diff = expected_total - total_line
                score_adjustment = line_diff * 0.02  # ±0.10 per 5-point diff
                score += score_adjustment

                if line_diff >= 3:
                    reasoning_parts.append(f"Expected {expected_total:.0f} vs line {total_line} = OVER lean")
                elif line_diff <= -3:
                    reasoning_parts.append(f"Expected {expected_total:.0f} vs line {total_line} = UNDER lean")
                else:
                    reasoning_parts.append(f"Expected {expected_total:.0f} close to line {total_line}")
            else:
                reasoning_parts.append(f"Expected total: {expected_total:.0f}")

    # General total line analysis (fallback if no team stats)
    if total_line and not expected_total:
        league_avg_total = 46.0  # Modern NFL average

        if total_line >= 52:
            reasoning_parts.append(f"High total ({total_line}) - shootout expected")
            if weather_impact >= 0:
                score += 0.03
        elif total_line <= 40:
            reasoning_parts.append(f"Low total ({total_line}) - defensive game expected")
            if weather_impact <= 0:
                score -= 0.03

    score = max(0.2, min(0.8, score))

    # Calculate market-specific scores
    # TOTALS: How does environment affect scoring? (score as calculated - primary use)
    # SPREAD/MONEYLINE: How does environment affect who wins? (weather advantage)
    market_scores = {}
    market_scores["totals"] = score  # Primary use case

    # SPREAD: Weather/environment can favor home team (familiar conditions)
    # Bad weather generally benefits defensive teams and home teams
    spread_score = 0.5
    if weather_impact < 0:  # Bad weather = under = defensive = home edge
        spread_score -= abs(weather_impact) * 0.5
    spread_score = max(0.2, min(0.8, spread_score))
    market_scores["spread"] = spread_score
    market_scores["moneyline"] = spread_score

    logger.info(f"[GameEnv NFL] Market scores: spread={spread_score:.3f}, totals={score:.3f}")

    return {
        "score": round(score, 3),
        "market_scores": {k: round(v, 3) for k, v in market_scores.items()},
        "expected_total": round(expected_total, 1) if expected_total else None,
        "weather_available": weather_data.get("available", False) if weather_data else False,
        "breakdown": {
            "weather_impact": round(weather_impact, 3),
            "weather_data": weather_data,
            "expected_total": round(expected_total, 1) if expected_total else None,
        },
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Neutral environment"
    }


def _calculate_nhl_environment(
    home_team: str,
    away_team: str,
    total_line: Optional[float],
    stats: dict
) -> dict:
    """
    NHL-specific environment calculation using real stats.

    Key metrics:
    - Goals For Per Game (GF/G): Team's offensive output
    - Goals Against Per Game (GA/G): Team's defensive vulnerability
    - Power Play % (PP%): Special teams scoring
    - Penalty Kill % (PK%): Special teams defense
    """
    home = stats.get("home", {})
    away = stats.get("away", {})

    if not home or not away:
        return _default_environment()

    # Calculate expected goals
    # Expected Home Goals = (Home GF/G + Away GA/G) / 2
    # Expected Away Goals = (Away GF/G + Home GA/G) / 2
    home_gf = home.get("goals_for_per_game", 3.0)
    home_ga = home.get("goals_against_per_game", 3.0)
    away_gf = away.get("goals_for_per_game", 3.0)
    away_ga = away.get("goals_against_per_game", 3.0)

    expected_home_goals = (home_gf + away_ga) / 2
    expected_away_goals = (away_gf + home_ga) / 2
    expected_total = expected_home_goals + expected_away_goals

    # PP/PK matchup analysis
    # If home has high PP% and away has low PK%, expect more scoring
    home_pp = home.get("pp_pct", 20.0)
    home_pk = home.get("pk_pct", 80.0)
    away_pp = away.get("pp_pct", 20.0)
    away_pk = away.get("pk_pct", 80.0)

    # PP% advantage (higher = more expected goals)
    # Average PP% is ~20%, good is 25%+, elite is 30%+
    home_pp_vs_away_pk = home_pp - (100 - away_pk)  # Positive = home PP advantage
    away_pp_vs_home_pk = away_pp - (100 - home_pk)  # Positive = away PP advantage
    special_teams_factor = (home_pp_vs_away_pk + away_pp_vs_home_pk) / 100  # -0.4 to +0.4

    # Adjust expected total based on special teams
    expected_total += special_teams_factor * 0.5  # Up to ±0.2 goal adjustment

    reasoning_parts = []

    # Calculate score based on expected vs line
    score = 0.5

    if total_line:
        line_diff = expected_total - total_line

        # Convert line difference to score adjustment
        # +1 goal vs line = significant over lean
        # -1 goal vs line = significant under lean
        score_adjustment = line_diff * 0.15  # ±0.15 per goal difference
        score = 0.5 + score_adjustment
        score = max(0.2, min(0.8, score))  # Cap at reasonable bounds

        if line_diff >= 0.5:
            reasoning_parts.append(f"Expected {expected_total:.1f} vs line {total_line} = OVER lean")
        elif line_diff <= -0.5:
            reasoning_parts.append(f"Expected {expected_total:.1f} vs line {total_line} = UNDER lean")
        else:
            reasoning_parts.append(f"Expected {expected_total:.1f} close to line {total_line}")
    else:
        # No line - just analyze scoring environment
        league_avg_total = 6.0  # NHL average
        if expected_total >= league_avg_total + 0.5:
            score = 0.6
            reasoning_parts.append(f"High-scoring matchup ({expected_total:.1f} expected)")
        elif expected_total <= league_avg_total - 0.5:
            score = 0.4
            reasoning_parts.append(f"Low-scoring matchup ({expected_total:.1f} expected)")

    # Add PP/PK insight
    if abs(special_teams_factor) > 0.1:
        if special_teams_factor > 0:
            reasoning_parts.append(f"Special teams favor scoring (PP%: {home_pp:.0f}/{away_pp:.0f})")
        else:
            reasoning_parts.append(f"Strong PK matchup limits scoring")

    # Calculate market-specific scores
    # TOTALS: Over/under scoring environment (score as calculated - primary use)
    # SPREAD: Better offensive team has edge
    market_scores = {}
    market_scores["totals"] = score  # Primary use case

    # SPREAD: Compare offensive/defensive matchups for winner prediction
    # Higher home GF vs away GA = home edge, and vice versa
    home_matchup = (home_gf / max(away_ga, 0.1)) if away_ga else 1.0
    away_matchup = (away_gf / max(home_ga, 0.1)) if home_ga else 1.0
    matchup_diff = home_matchup - away_matchup
    spread_score = 0.5 - (matchup_diff * 0.15)  # Home better matchup = lower score
    spread_score = max(0.2, min(0.8, spread_score))
    market_scores["spread"] = spread_score
    market_scores["moneyline"] = spread_score

    logger.info(f"[GameEnv NHL] Market scores: spread={spread_score:.3f}, totals={score:.3f}")

    return {
        "score": round(score, 3),
        "market_scores": {k: round(v, 3) for k, v in market_scores.items()},
        "expected_total": round(expected_total, 2),
        "expected_home_goals": round(expected_home_goals, 2),
        "expected_away_goals": round(expected_away_goals, 2),
        "breakdown": {
            "home_gf_per_game": home_gf,
            "home_ga_per_game": home_ga,
            "away_gf_per_game": away_gf,
            "away_ga_per_game": away_ga,
            "home_pp_pct": home_pp,
            "home_pk_pct": home_pk,
            "away_pp_pct": away_pp,
            "away_pk_pct": away_pk,
            "special_teams_factor": round(special_teams_factor, 3),
        },
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Neutral scoring environment"
    }


def _calculate_nba_environment(
    home_team: str,
    away_team: str,
    total_line: Optional[float],
    stats: dict,
    sport: str = "NBA"
) -> dict:
    """
    NBA/NCAAB environment calculation.

    Key metrics:
    - Pace: Possessions per game (NBA ~100, NCAAB ~68)
    - Offensive Rating: Points per 100 possessions
    - Defensive Rating: Points allowed per 100 possessions
    """
    home = stats.get("home", {})
    away = stats.get("away", {})

    if not home or not away:
        return _default_environment()

    # Sport-specific baselines
    is_ncaab = sport == "NCAAB"
    default_pace = 68 if is_ncaab else 100
    default_rating = 105 if is_ncaab else 110

    # Extract pace and ratings
    home_pace = home.get("pace", default_pace)
    away_pace = away.get("pace", default_pace)
    home_off = home.get("off_rating", default_rating)
    home_def = home.get("def_rating", default_rating)
    away_off = away.get("off_rating", default_rating)
    away_def = away.get("def_rating", default_rating)

    # NCAAB pace data in DB is sometimes stored on NBA scale (~100).
    # Actual NCAAB pace is ~64-74 possessions per game.
    # Detect and normalize: if NCAAB pace > 85, it's NBA-scaled.
    if is_ncaab:
        if home_pace > 85:
            home_pace = home_pace * 0.68  # ~100 → ~68
        if away_pace > 85:
            away_pace = away_pace * 0.68

    # Expected game pace (average of both teams)
    expected_pace = (home_pace + away_pace) / 2
    league_avg_pace = 68.0 if is_ncaab else 100.0

    # Expected scoring
    # Home vs Away Def, Away vs Home Def
    home_expected_off = (home_off + away_def) / 2
    away_expected_off = (away_off + home_def) / 2

    # Sport-specific league average totals
    # NBA: ~225 points per game (48 minutes, ~100 possessions)
    # NCAAB: ~140 points per game (40 minutes, ~68 possessions)
    league_avg_total = 140 if is_ncaab else 225

    pace_factor = expected_pace / league_avg_pace
    league_avg_rating = 105.0 if is_ncaab else 110.0
    efficiency_factor = ((home_expected_off + away_expected_off) / 2) / league_avg_rating

    expected_total = league_avg_total * pace_factor * efficiency_factor

    # Clamp expected_total to ±25% of league average to prevent runaway values
    min_total = league_avg_total * 0.75
    max_total = league_avg_total * 1.25
    expected_total = max(min_total, min(max_total, expected_total))

    reasoning_parts = []
    score = 0.5

    if total_line:
        line_diff = expected_total - total_line

        # ±5 points vs line is significant in NBA
        score_adjustment = line_diff * 0.03  # ±0.15 per 5 points
        score = 0.5 + score_adjustment
        score = max(0.2, min(0.8, score))

        if line_diff >= 5:
            reasoning_parts.append(f"Expected {expected_total:.0f} vs line {total_line} = OVER lean")
        elif line_diff <= -5:
            reasoning_parts.append(f"Expected {expected_total:.0f} vs line {total_line} = UNDER lean")

    # Pace insight (thresholds relative to league average)
    fast_threshold = league_avg_pace * 1.03
    slow_threshold = league_avg_pace * 0.97
    if expected_pace >= fast_threshold:
        reasoning_parts.append(f"Fast-paced matchup ({expected_pace:.1f} pace)")
    elif expected_pace <= slow_threshold:
        reasoning_parts.append(f"Slow-paced matchup ({expected_pace:.1f} pace)")

    # Calculate market-specific scores
    # TOTALS: Over/under scoring environment (score as calculated - primary use)
    # SPREAD: Compare efficiency matchups for winner prediction
    market_scores = {}
    market_scores["totals"] = score  # Primary use case

    # SPREAD: Net rating comparison indicates likely winner
    # Home off vs away def, away off vs home def
    home_net = home_off - away_def  # How home scores vs away D
    away_net = away_off - home_def  # How away scores vs home D
    net_diff = home_net - away_net  # Positive = home has edge
    spread_score = 0.5 - (net_diff * 0.015)  # Scale appropriately
    spread_score = max(0.2, min(0.8, spread_score))
    market_scores["spread"] = spread_score
    market_scores["moneyline"] = spread_score

    logger.info(f"[GameEnv NBA] Market scores: spread={spread_score:.3f}, totals={score:.3f}")

    return {
        "score": round(score, 3),
        "market_scores": {k: round(v, 3) for k, v in market_scores.items()},
        "expected_total": round(expected_total, 1),
        "breakdown": {
            "home_pace": home_pace,
            "away_pace": away_pace,
            "expected_pace": round(expected_pace, 1),
            "home_off_rating": home_off,
            "home_def_rating": home_def,
            "away_off_rating": away_off,
            "away_def_rating": away_def,
        },
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Standard pace matchup"
    }


def _calculate_epl_environment(
    home_team: str,
    away_team: str,
    total_line: Optional[float],
    team_stats: dict
) -> dict:
    """
    EPL environment calculation using goals per game from Football-Data.org.

    Similar to NHL - uses goals for/against per game to estimate expected total.
    EPL average is ~2.8 goals per game.
    """
    home = team_stats.get("home", {})
    away = team_stats.get("away", {})

    if not home and not away:
        return _default_environment()

    # Goals per game (stored as points_per_game in team_stats)
    home_gf = home.get("points_per_game") or 1.4  # EPL avg ~1.4 goals/game home
    home_ga = home.get("points_allowed_per_game") or 1.4
    away_gf = away.get("points_per_game") or 1.4
    away_ga = away.get("points_allowed_per_game") or 1.4

    # Expected goals: (Home GF + Away GA) / 2 for home, (Away GF + Home GA) / 2 for away
    expected_home_goals = (home_gf + away_ga) / 2
    expected_away_goals = (away_gf + home_ga) / 2
    expected_total = expected_home_goals + expected_away_goals

    reasoning_parts = []
    score = 0.5

    if total_line:
        line_diff = expected_total - total_line

        # ±0.5 goals vs line is significant in soccer
        score_adjustment = line_diff * 0.2  # ±0.2 per goal difference
        score = 0.5 + score_adjustment
        score = max(0.2, min(0.8, score))

        if line_diff >= 0.3:
            reasoning_parts.append(f"Expected {expected_total:.1f} vs line {total_line} = OVER lean")
        elif line_diff <= -0.3:
            reasoning_parts.append(f"Expected {expected_total:.1f} vs line {total_line} = UNDER lean")
        else:
            reasoning_parts.append(f"Expected {expected_total:.1f} close to line {total_line}")
    else:
        # No line - analyze scoring environment
        league_avg_total = 2.8  # EPL average
        if expected_total >= league_avg_total + 0.3:
            score = 0.6
            reasoning_parts.append(f"High-scoring matchup ({expected_total:.1f} expected)")
        elif expected_total <= league_avg_total - 0.3:
            score = 0.4
            reasoning_parts.append(f"Low-scoring matchup ({expected_total:.1f} expected)")

    # Calculate market-specific scores
    # TOTALS: Over/under scoring environment (score as calculated - primary use)
    # SPREAD: Compare goals for/against for winner prediction
    market_scores = {}
    market_scores["totals"] = score  # Primary use case

    # SPREAD: Goal difference indicates team quality
    # Higher home expected vs away expected = home edge
    goal_edge = expected_home_goals - expected_away_goals
    spread_score = 0.5 - (goal_edge * 0.15)  # Positive edge = home better = lower score
    spread_score = max(0.2, min(0.8, spread_score))
    market_scores["spread"] = spread_score
    market_scores["moneyline"] = spread_score

    logger.info(f"[GameEnv EPL] Market scores: spread={spread_score:.3f}, totals={score:.3f}")

    return {
        "score": round(score, 3),
        "market_scores": {k: round(v, 3) for k, v in market_scores.items()},
        "expected_total": round(expected_total, 2),
        "expected_home_goals": round(expected_home_goals, 2),
        "expected_away_goals": round(expected_away_goals, 2),
        "breakdown": {
            "home_gf_per_game": home_gf,
            "home_ga_per_game": home_ga,
            "away_gf_per_game": away_gf,
            "away_ga_per_game": away_ga,
        },
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Standard scoring environment"
    }


def _default_environment() -> dict:
    """Default response when no sport-specific stats available."""
    return {
        "score": 0.5,
        "market_scores": {"spread": 0.5, "moneyline": 0.5, "totals": 0.5},
        "expected_total": None,
        "breakdown": {},
        "reasoning": "No advanced stats available - using baseline"
    }


async def fetch_nhl_game_stats(home_abbr: str, away_abbr: str) -> Optional[dict]:
    """
    Fetch NHL stats for a specific matchup.
    Returns formatted stats dict for calculate_game_environment_score.
    """
    try:
        from data_sources.nhl_stats import get_team_stats, ESPN_TO_NHL_ABBR

        # Map ESPN abbreviations to NHL if needed
        home_nhl = ESPN_TO_NHL_ABBR.get(home_abbr, home_abbr)
        away_nhl = ESPN_TO_NHL_ABBR.get(away_abbr, away_abbr)

        all_stats = await get_team_stats()
        if not all_stats:
            return None

        home_stats = all_stats.get(home_nhl)
        away_stats = all_stats.get(away_nhl)

        if not home_stats or not away_stats:
            logger.warning(f"NHL stats not found for {home_nhl} or {away_nhl}")
            return None

        return {
            "home": home_stats,
            "away": away_stats
        }
    except Exception as e:
        logger.error(f"Error fetching NHL stats: {e}")
        return None


def fetch_nhl_game_stats_sync(home_abbr: str, away_abbr: str) -> Optional[dict]:
    """Synchronous wrapper for fetch_nhl_game_stats."""
    try:
        return asyncio.run(fetch_nhl_game_stats(home_abbr, away_abbr))
    except Exception as e:
        logger.error(f"Error in sync NHL fetch: {e}")
        return None
