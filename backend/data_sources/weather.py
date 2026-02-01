"""
OpenWeatherMap API Integration

Free tier provides 5-day forecast with 3-hour intervals.
Use for outdoor NFL/NCAAF games to factor weather into analysis.

Wind >15mph affects passing game
Rain affects totals (lower scoring)
Extreme cold affects kicking game
"""
import os
import httpx
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
OPENWEATHERMAP_BASE = "https://api.openweathermap.org/data/2.5"

# NFL Stadium coordinates (outdoor stadiums only matter for weather)
NFL_STADIUMS = {
    # Outdoor Stadiums
    "new england patriots": {"name": "Gillette Stadium", "lat": 42.0909, "lon": -71.2643, "indoor": False},
    "buffalo bills": {"name": "Highmark Stadium", "lat": 42.7738, "lon": -78.7870, "indoor": False},
    "miami dolphins": {"name": "Hard Rock Stadium", "lat": 25.9580, "lon": -80.2389, "indoor": False},  # Open air
    "new york jets": {"name": "MetLife Stadium", "lat": 40.8128, "lon": -74.0742, "indoor": False},
    "new york giants": {"name": "MetLife Stadium", "lat": 40.8128, "lon": -74.0742, "indoor": False},
    "baltimore ravens": {"name": "M&T Bank Stadium", "lat": 39.2780, "lon": -76.6227, "indoor": False},
    "pittsburgh steelers": {"name": "Acrisure Stadium", "lat": 40.4468, "lon": -80.0158, "indoor": False},
    "cleveland browns": {"name": "Cleveland Browns Stadium", "lat": 41.5061, "lon": -81.6995, "indoor": False},
    "cincinnati bengals": {"name": "Paycor Stadium", "lat": 39.0955, "lon": -84.5161, "indoor": False},
    "tennessee titans": {"name": "Nissan Stadium", "lat": 36.1665, "lon": -86.7713, "indoor": False},
    "jacksonville jaguars": {"name": "EverBank Stadium", "lat": 30.3239, "lon": -81.6373, "indoor": False},
    "kansas city chiefs": {"name": "Arrowhead Stadium", "lat": 39.0489, "lon": -94.4839, "indoor": False},
    "denver broncos": {"name": "Empower Field", "lat": 39.7439, "lon": -105.0201, "indoor": False},
    "philadelphia eagles": {"name": "Lincoln Financial Field", "lat": 39.9008, "lon": -75.1675, "indoor": False},
    "washington commanders": {"name": "Commanders Field", "lat": 38.9076, "lon": -76.8645, "indoor": False},
    "chicago bears": {"name": "Soldier Field", "lat": 41.8623, "lon": -87.6167, "indoor": False},
    "green bay packers": {"name": "Lambeau Field", "lat": 44.5013, "lon": -88.0622, "indoor": False},
    "san francisco 49ers": {"name": "Levi's Stadium", "lat": 37.4032, "lon": -121.9698, "indoor": False},
    "seattle seahawks": {"name": "Lumen Field", "lat": 47.5952, "lon": -122.3316, "indoor": False},
    "los angeles rams": {"name": "SoFi Stadium", "lat": 33.9535, "lon": -118.3392, "indoor": True},  # Covered
    "los angeles chargers": {"name": "SoFi Stadium", "lat": 33.9535, "lon": -118.3392, "indoor": True},
    "carolina panthers": {"name": "Bank of America Stadium", "lat": 35.2258, "lon": -80.8528, "indoor": False},
    "tampa bay buccaneers": {"name": "Raymond James Stadium", "lat": 27.9759, "lon": -82.5033, "indoor": False},
    "atlanta falcons": {"name": "Mercedes-Benz Stadium", "lat": 33.7554, "lon": -84.4010, "indoor": True},
    "new orleans saints": {"name": "Caesars Superdome", "lat": 29.9511, "lon": -90.0812, "indoor": True},
    "dallas cowboys": {"name": "AT&T Stadium", "lat": 32.7473, "lon": -97.0945, "indoor": True},
    "houston texans": {"name": "NRG Stadium", "lat": 29.6847, "lon": -95.4107, "indoor": True},
    "indianapolis colts": {"name": "Lucas Oil Stadium", "lat": 39.7601, "lon": -86.1639, "indoor": True},
    "las vegas raiders": {"name": "Allegiant Stadium", "lat": 36.0909, "lon": -115.1833, "indoor": True},
    "minnesota vikings": {"name": "U.S. Bank Stadium", "lat": 44.9736, "lon": -93.2575, "indoor": True},
    "detroit lions": {"name": "Ford Field", "lat": 42.3400, "lon": -83.0456, "indoor": True},
    "arizona cardinals": {"name": "State Farm Stadium", "lat": 33.5276, "lon": -112.2626, "indoor": True},
}

# Super Bowl venue locations
SUPER_BOWL_VENUES = {
    2025: {"name": "Caesars Superdome", "lat": 29.9511, "lon": -90.0812, "indoor": True, "city": "New Orleans"},
    2026: {"name": "Levi's Stadium", "lat": 37.4032, "lon": -121.9698, "indoor": False, "city": "Santa Clara"},
    2027: {"name": "SoFi Stadium", "lat": 33.9535, "lon": -118.3392, "indoor": True, "city": "Los Angeles"},
}


async def get_weather_forecast(lat: float, lon: float, game_time: datetime) -> Optional[dict]:
    """
    Get weather forecast for a specific location and time.

    Args:
        lat: Latitude
        lon: Longitude
        game_time: When the game starts

    Returns:
        dict with temperature, wind_speed, wind_gust, precipitation, conditions
    """
    if not OPENWEATHERMAP_API_KEY:
        logger.warning("OPENWEATHERMAP_API_KEY not set - weather data unavailable")
        return None

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{OPENWEATHERMAP_BASE}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": OPENWEATHERMAP_API_KEY,
                    "units": "imperial",  # Fahrenheit, mph
                }
            )
            response.raise_for_status()
            data = response.json()

            # Find the forecast closest to game time
            forecasts = data.get("list", [])
            best_forecast = None
            min_diff = float("inf")

            for forecast in forecasts:
                forecast_time = datetime.fromtimestamp(forecast["dt"], tz=timezone.utc)
                diff = abs((forecast_time - game_time).total_seconds())

                if diff < min_diff:
                    min_diff = diff
                    best_forecast = forecast

            if not best_forecast:
                return None

            # Extract weather data
            main = best_forecast.get("main", {})
            wind = best_forecast.get("wind", {})
            weather = best_forecast.get("weather", [{}])[0]
            rain = best_forecast.get("rain", {})
            snow = best_forecast.get("snow", {})

            return {
                "temperature": main.get("temp", 70),
                "feels_like": main.get("feels_like", 70),
                "humidity": main.get("humidity", 50),
                "wind_speed": wind.get("speed", 0),
                "wind_gust": wind.get("gust", 0),
                "wind_direction": wind.get("deg", 0),
                "conditions": weather.get("main", "Clear"),
                "description": weather.get("description", ""),
                "rain_3h": rain.get("3h", 0),
                "snow_3h": snow.get("3h", 0),
                "forecast_time": datetime.fromtimestamp(best_forecast["dt"], tz=timezone.utc).isoformat(),
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"Weather API HTTP error: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return None


def get_stadium_location(team_name: str) -> Optional[dict]:
    """Get stadium location for a team."""
    team_lower = team_name.lower().strip()

    # Direct lookup
    if team_lower in NFL_STADIUMS:
        return NFL_STADIUMS[team_lower]

    # Partial match
    for key, stadium in NFL_STADIUMS.items():
        if key in team_lower or team_lower in key:
            return stadium

        # Match on city or team name parts
        for word in team_lower.split():
            if len(word) > 3 and word in key:
                return stadium

    return None


async def get_game_weather(home_team: str, game_time: datetime) -> dict:
    """
    Get weather forecast for a game.

    Returns weather analysis with betting impact assessment.
    """
    default_response = {
        "available": False,
        "indoor": True,
        "weather": None,
        "impact": {
            "passing_impact": 0,
            "kicking_impact": 0,
            "total_impact": 0,
            "reasoning": "Weather data unavailable or indoor stadium"
        }
    }

    stadium = get_stadium_location(home_team)

    if not stadium:
        logger.warning(f"Stadium not found for: {home_team}")
        return default_response

    # Indoor stadiums - weather doesn't matter
    if stadium.get("indoor", False):
        return {
            "available": True,
            "indoor": True,
            "stadium": stadium.get("name"),
            "weather": None,
            "impact": {
                "passing_impact": 0,
                "kicking_impact": 0,
                "total_impact": 0,
                "reasoning": f"Indoor stadium ({stadium.get('name')}) - weather not a factor"
            }
        }

    # Fetch weather for outdoor stadium
    weather = await get_weather_forecast(
        stadium["lat"],
        stadium["lon"],
        game_time
    )

    if not weather:
        return default_response

    # Calculate betting impact
    impact = _calculate_weather_impact(weather)

    return {
        "available": True,
        "indoor": False,
        "stadium": stadium.get("name"),
        "weather": weather,
        "impact": impact
    }


def _calculate_weather_impact(weather: dict) -> dict:
    """
    Calculate betting impact from weather conditions.

    Returns impact scores for passing, kicking, and totals.
    """
    wind_speed = weather.get("wind_speed", 0)
    wind_gust = weather.get("wind_gust", 0)
    temp = weather.get("temperature", 70)
    rain = weather.get("rain_3h", 0)
    snow = weather.get("snow_3h", 0)
    conditions = weather.get("conditions", "Clear").lower()

    reasoning_parts = []

    # Wind impact on passing (negative = harder to pass)
    passing_impact = 0
    if wind_speed >= 20 or wind_gust >= 30:
        passing_impact = -0.15
        reasoning_parts.append(f"High wind ({wind_speed:.0f} mph, gusts {wind_gust:.0f}) - MAJOR passing impact")
    elif wind_speed >= 15 or wind_gust >= 25:
        passing_impact = -0.08
        reasoning_parts.append(f"Moderate wind ({wind_speed:.0f} mph) - passing affected")
    elif wind_speed >= 10:
        passing_impact = -0.03
        reasoning_parts.append(f"Light wind ({wind_speed:.0f} mph) - minor passing factor")

    # Kicking impact (field goals, extra points)
    kicking_impact = 0
    if wind_speed >= 15 or wind_gust >= 25:
        kicking_impact = -0.10
        reasoning_parts.append("Wind affects kicking game")

    # Cold weather impact
    if temp <= 20:
        kicking_impact -= 0.05
        passing_impact -= 0.03
        reasoning_parts.append(f"Extreme cold ({temp:.0f}°F) - ball harder to grip/kick")
    elif temp <= 35:
        kicking_impact -= 0.02
        reasoning_parts.append(f"Cold weather ({temp:.0f}°F) - minor impact")

    # Precipitation impact on totals
    total_impact = 0
    if rain > 0 or "rain" in conditions:
        total_impact = -0.08
        passing_impact -= 0.05
        reasoning_parts.append(f"Rain expected - lean UNDER, passing affected")
    if snow > 0 or "snow" in conditions:
        total_impact = -0.12
        passing_impact -= 0.08
        reasoning_parts.append(f"Snow expected - strong UNDER lean, passing heavily affected")

    # Combine for total impact
    if total_impact == 0:
        total_impact = (passing_impact + kicking_impact) / 2

    if not reasoning_parts:
        reasoning_parts.append(f"Good conditions ({temp:.0f}°F, wind {wind_speed:.0f} mph) - minimal weather impact")

    return {
        "passing_impact": round(passing_impact, 3),
        "kicking_impact": round(kicking_impact, 3),
        "total_impact": round(total_impact, 3),
        "reasoning": "; ".join(reasoning_parts)
    }


def get_game_weather_sync(home_team: str, game_time: datetime) -> dict:
    """Synchronous wrapper for get_game_weather."""
    import asyncio
    try:
        return asyncio.run(get_game_weather(home_team, game_time))
    except Exception as e:
        logger.error(f"Error in sync weather fetch: {e}")
        return {
            "available": False,
            "indoor": True,
            "weather": None,
            "impact": {
                "passing_impact": 0,
                "kicking_impact": 0,
                "total_impact": 0,
                "reasoning": f"Weather fetch error: {e}"
            }
        }
