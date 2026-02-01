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
) -> dict:
    """
    Calculate game environment score for totals analysis.

    Returns:
    - score > 0.5: Lean OVER (high-scoring environment expected)
    - score < 0.5: Lean UNDER (low-scoring environment expected)
    - score = 0.5: Neutral

    Also returns expected_total for line comparison.
    """
    if sport == "NHL" and nhl_stats:
        return _calculate_nhl_environment(home_team, away_team, total_line, nhl_stats)
    elif sport == "NBA" and nba_stats:
        return _calculate_nba_environment(home_team, away_team, total_line, nba_stats)
    elif sport in ["NFL", "americanfootball_nfl"]:
        return _calculate_nfl_environment(home_team, away_team, total_line, weather_data, game_time)
    else:
        return _default_environment()


def _calculate_nfl_environment(
    home_team: str,
    away_team: str,
    total_line: Optional[float],
    weather_data: Optional[dict],
    game_time: Optional[any]
) -> dict:
    """
    NFL-specific environment calculation including weather.

    Weather factors:
    - Wind >15mph affects passing game
    - Rain/snow affects totals (lean under)
    - Extreme cold affects kicking
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
        reasoning_parts.append("Weather data unavailable - using neutral baseline")

    # NFL totals typically around 44-48 points
    # Without detailed team stats, provide general analysis
    if total_line:
        league_avg_total = 46.0  # Modern NFL average

        if total_line >= 52:
            reasoning_parts.append(f"High total ({total_line}) - shootout expected")
            if weather_impact >= 0:
                score += 0.03  # Slight over lean in good conditions
        elif total_line <= 40:
            reasoning_parts.append(f"Low total ({total_line}) - defensive game expected")
            if weather_impact <= 0:
                score -= 0.03  # Slight under lean

    score = max(0.2, min(0.8, score))

    return {
        "score": round(score, 3),
        "expected_total": None,  # Would need team stats for this
        "weather_available": weather_data.get("available", False) if weather_data else False,
        "breakdown": {
            "weather_impact": round(weather_impact, 3),
            "weather_data": weather_data,
        },
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "Neutral NFL environment"
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

    return {
        "score": round(score, 3),
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
    stats: dict
) -> dict:
    """
    NBA-specific environment calculation.

    Key metrics:
    - Pace: Possessions per 48 minutes
    - Offensive Rating: Points per 100 possessions
    - Defensive Rating: Points allowed per 100 possessions
    """
    home = stats.get("home", {})
    away = stats.get("away", {})

    if not home or not away:
        return _default_environment()

    # Extract pace and ratings
    home_pace = home.get("pace", 100)
    away_pace = away.get("pace", 100)
    home_off = home.get("off_rating", 110)
    home_def = home.get("def_rating", 110)
    away_off = away.get("off_rating", 110)
    away_def = away.get("def_rating", 110)

    # Expected game pace (average of both teams)
    expected_pace = (home_pace + away_pace) / 2
    league_avg_pace = 100.0

    # Expected scoring
    # Home vs Away Def, Away vs Home Def
    home_expected_off = (home_off + away_def) / 2
    away_expected_off = (away_off + home_def) / 2

    # Convert to expected game total (very rough estimate)
    # Pace * (combined efficiency / 100) * 2 (both teams) / 100 * 48 min
    # Simplified: use league average as baseline
    league_avg_total = 225  # Modern NBA average

    pace_factor = expected_pace / league_avg_pace
    efficiency_factor = ((home_expected_off + away_expected_off) / 2) / 110  # 110 is league avg

    expected_total = league_avg_total * pace_factor * efficiency_factor

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

    # Pace insight
    if expected_pace >= 103:
        reasoning_parts.append(f"Fast-paced matchup ({expected_pace:.1f} pace)")
    elif expected_pace <= 97:
        reasoning_parts.append(f"Slow-paced matchup ({expected_pace:.1f} pace)")

    return {
        "score": round(score, 3),
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


def _default_environment() -> dict:
    """Default response when no sport-specific stats available."""
    return {
        "score": 0.5,
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
