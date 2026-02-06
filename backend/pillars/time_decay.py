"""
Pillar 4: Time, Fatigue & Attention Decay
Weight: 0.15

Measures: Timing asymmetries between teams
- Days of rest
- Back-to-back games
- Travel distance and road trips
- Schedule density (3rd game in 4 nights, etc.)
- Home field advantage (especially NFL)
"""
from datetime import datetime
import logging

from data_sources.espn import espn_client

logger = logging.getLogger(__name__)

SPORT_REST_IMPORTANCE = {
    "NFL": 0.4,  # Increased - rest matters in NFL playoffs
    "americanfootball_nfl": 0.4,
    "NCAAF": 0.3,
    "americanfootball_ncaaf": 0.3,
    "NBA": 1.0,
    "basketball_nba": 1.0,
    "NCAAB": 0.8,
    "basketball_ncaab": 0.8,
    "NHL": 0.9,
    "icehockey_nhl": 0.9,
    # Soccer - rest matters but less than basketball
    "soccer_epl": 0.6,
    "soccer_england_efl_champ": 0.6,
    "soccer_england_league1": 0.6,
    "soccer_england_league2": 0.6,
}

# NFL Home Field Advantage - AMPLIFIED for visual differentiation
# Super Bowl is typically at neutral site, but one team is designated "home"
NFL_HOME_FIELD_ADVANTAGE = 0.08  # ~8% edge for meaningful visual impact

# NFL team locations for travel distance calculation
NFL_TEAM_LOCATIONS = {
    # AFC East
    "new england patriots": ("Boston", 42.3601, -71.0589),
    "patriots": ("Boston", 42.3601, -71.0589),
    "buffalo bills": ("Buffalo", 42.8864, -78.8784),
    "bills": ("Buffalo", 42.8864, -78.8784),
    "miami dolphins": ("Miami", 25.7617, -80.1918),
    "dolphins": ("Miami", 25.7617, -80.1918),
    "new york jets": ("New York", 40.7128, -74.0060),
    "jets": ("New York", 40.7128, -74.0060),
    # AFC North
    "baltimore ravens": ("Baltimore", 39.2904, -76.6122),
    "ravens": ("Baltimore", 39.2904, -76.6122),
    "pittsburgh steelers": ("Pittsburgh", 40.4406, -79.9959),
    "steelers": ("Pittsburgh", 40.4406, -79.9959),
    "cleveland browns": ("Cleveland", 41.4993, -81.6944),
    "browns": ("Cleveland", 41.4993, -81.6944),
    "cincinnati bengals": ("Cincinnati", 39.1031, -84.5120),
    "bengals": ("Cincinnati", 39.1031, -84.5120),
    # AFC South
    "houston texans": ("Houston", 29.7604, -95.3698),
    "texans": ("Houston", 29.7604, -95.3698),
    "indianapolis colts": ("Indianapolis", 39.7684, -86.1581),
    "colts": ("Indianapolis", 39.7684, -86.1581),
    "tennessee titans": ("Nashville", 36.1627, -86.7816),
    "titans": ("Nashville", 36.1627, -86.7816),
    "jacksonville jaguars": ("Jacksonville", 30.3322, -81.6557),
    "jaguars": ("Jacksonville", 30.3322, -81.6557),
    # AFC West
    "kansas city chiefs": ("Kansas City", 39.0997, -94.5786),
    "chiefs": ("Kansas City", 39.0997, -94.5786),
    "las vegas raiders": ("Las Vegas", 36.1699, -115.1398),
    "raiders": ("Las Vegas", 36.1699, -115.1398),
    "los angeles chargers": ("Los Angeles", 34.0522, -118.2437),
    "chargers": ("Los Angeles", 34.0522, -118.2437),
    "denver broncos": ("Denver", 39.7392, -104.9903),
    "broncos": ("Denver", 39.7392, -104.9903),
    # NFC East
    "philadelphia eagles": ("Philadelphia", 39.9526, -75.1652),
    "eagles": ("Philadelphia", 39.9526, -75.1652),
    "dallas cowboys": ("Dallas", 32.7767, -96.7970),
    "cowboys": ("Dallas", 32.7767, -96.7970),
    "washington commanders": ("Washington", 38.9072, -77.0369),
    "commanders": ("Washington", 38.9072, -77.0369),
    "new york giants": ("New York", 40.7128, -74.0060),
    "giants": ("New York", 40.7128, -74.0060),
    # NFC North
    "detroit lions": ("Detroit", 42.3314, -83.0458),
    "lions": ("Detroit", 42.3314, -83.0458),
    "green bay packers": ("Green Bay", 44.5133, -88.0133),
    "packers": ("Green Bay", 44.5133, -88.0133),
    "chicago bears": ("Chicago", 41.8781, -87.6298),
    "bears": ("Chicago", 41.8781, -87.6298),
    "minnesota vikings": ("Minneapolis", 44.9778, -93.2650),
    "vikings": ("Minneapolis", 44.9778, -93.2650),
    # NFC South
    "atlanta falcons": ("Atlanta", 33.7490, -84.3880),
    "falcons": ("Atlanta", 33.7490, -84.3880),
    "tampa bay buccaneers": ("Tampa", 27.9506, -82.4572),
    "buccaneers": ("Tampa", 27.9506, -82.4572),
    "new orleans saints": ("New Orleans", 29.9511, -90.0715),
    "saints": ("New Orleans", 29.9511, -90.0715),
    "carolina panthers": ("Charlotte", 35.2271, -80.8431),
    "panthers": ("Charlotte", 35.2271, -80.8431),
    # NFC West
    "san francisco 49ers": ("San Francisco", 37.7749, -122.4194),
    "49ers": ("San Francisco", 37.7749, -122.4194),
    "seattle seahawks": ("Seattle", 47.6062, -122.3321),
    "seahawks": ("Seattle", 47.6062, -122.3321),
    "los angeles rams": ("Los Angeles", 34.0522, -118.2437),
    "rams": ("Los Angeles", 34.0522, -118.2437),
    "arizona cardinals": ("Phoenix", 33.4484, -112.0740),
    "cardinals": ("Phoenix", 33.4484, -112.0740),
}

# Super Bowl venue locations (for travel calculation)
SUPER_BOWL_VENUES = {
    "new orleans": (29.9511, -90.0715),
    "las vegas": (36.1699, -115.1398),
    "miami": (25.7617, -80.1918),
    "los angeles": (34.0522, -118.2437),
    "phoenix": (33.4484, -112.0740),
    "tampa": (27.9506, -82.4572),
}


def _calculate_travel_distance(team_name: str, venue_location: tuple = None) -> float:
    """Calculate approximate travel distance in miles for a team."""
    import math

    team_lower = team_name.lower().strip()

    # Find team location
    team_loc = None
    for key, loc in NFL_TEAM_LOCATIONS.items():
        if key in team_lower or team_lower in key:
            team_loc = loc
            break

    if not team_loc:
        return 0.0

    # Default to a neutral Super Bowl venue if not specified
    if venue_location is None:
        venue_location = SUPER_BOWL_VENUES.get("new orleans", (29.9511, -90.0715))

    # Haversine formula for distance
    lat1, lon1 = team_loc[1], team_loc[2]
    lat2, lon2 = venue_location

    R = 3959  # Earth's radius in miles

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def calculate_time_decay_score(
    sport: str,
    home_team: str,
    away_team: str,
    game_time: datetime,
    market_type: str = "spread"
) -> dict:
    """
    Calculate Pillar 4: Time, Fatigue & Attention Decay score.

    For SPREAD/MONEYLINE:
    - score > 0.5: AWAY team has rest/timing advantage
    - score < 0.5: HOME team has rest/timing advantage

    For TOTALS:
    - score > 0.5: Both teams rested = higher scoring = OVER lean
    - score < 0.5: One/both teams fatigued = lower scoring = UNDER lean

    A score = 0.5 means balanced rest situation
    """
    home_rest = espn_client.calculate_rest_and_travel(sport, home_team, game_time)
    away_rest = espn_client.calculate_rest_and_travel(sport, away_team, game_time)

    home_fatigue = home_rest["fatigue_score"]
    away_fatigue = away_rest["fatigue_score"]

    importance = SPORT_REST_IMPORTANCE.get(sport, 0.5)

    fatigue_differential = (home_fatigue - away_fatigue) * importance

    situational_adjustment = 0.0
    reasoning_parts = []
    soccer_adjustment = 0.0

    # SOCCER-SPECIFIC: Midweek vs weekend games and home advantage
    is_soccer_sport = sport and ("soccer" in sport.lower() or sport.lower().startswith("soccer"))
    if is_soccer_sport:
        # Check if game is midweek (Tue-Thu) vs weekend (Sat-Sun)
        game_day = game_time.weekday()  # 0=Monday, 6=Sunday

        if game_day in [1, 2, 3]:  # Tuesday, Wednesday, Thursday
            # Midweek game = potential congestion for both teams
            reasoning_parts.append("Midweek fixture: potential fixture congestion")
            # Slightly favor home team in midweek (less travel)
            soccer_adjustment -= 0.05
        elif game_day in [5, 6]:  # Saturday, Sunday
            reasoning_parts.append("Weekend fixture: standard rest")

        # Home advantage in soccer is SIGNIFICANT (about 55-60% home win rate historically)
        # Apply a baseline home advantage of 8%
        soccer_adjustment -= 0.08
        reasoning_parts.append(f"{home_team} home advantage (+8%)")

        # If ESPN data is unavailable, use defaults
        if home_fatigue == 0 and away_fatigue == 0:
            # Default to neutral but with home advantage applied
            reasoning_parts.append("Fixture data unavailable - using home advantage baseline")

        logger.info(f"[TimeDecay] Soccer: day={game_day}, soccer_adjustment={soccer_adjustment:.3f}")

    # NFL-specific: Travel distance and home field advantage
    home_travel_miles = 0
    away_travel_miles = 0

    if sport in ["NFL", "americanfootball_nfl"]:
        # Calculate travel distances
        home_travel_miles = _calculate_travel_distance(home_team)
        away_travel_miles = _calculate_travel_distance(away_team)

        logger.info(f"[TimeDecay] Travel: {home_team}={home_travel_miles:.0f}mi, {away_team}={away_travel_miles:.0f}mi")

        # AMPLIFIED Travel impact for visual differentiation
        # >2000 miles = significant penalty (0.10-0.15)
        # >1000 miles = moderate penalty (0.05-0.10)
        # <500 miles = minimal impact
        travel_diff = 0.0

        if away_travel_miles > 2000:
            travel_diff = 0.12 + (away_travel_miles - 2000) / 5000 * 0.05  # 12-17% penalty
            reasoning_parts.append(f"MAJOR: {away_team} travels {away_travel_miles:.0f} miles (cross-country)")
        elif away_travel_miles > 1000:
            travel_diff = 0.06 + (away_travel_miles - 1000) / 1000 * 0.06  # 6-12% penalty
            reasoning_parts.append(f"{away_team} travels {away_travel_miles:.0f} miles")
        elif away_travel_miles > 500:
            travel_diff = 0.03 + (away_travel_miles - 500) / 500 * 0.03  # 3-6% penalty
            reasoning_parts.append(f"{away_team} travels {away_travel_miles:.0f} miles")

        # Apply travel differential (negative = home advantage)
        situational_adjustment -= travel_diff

        # Home team bonus if they have minimal travel
        if home_travel_miles < 500 and away_travel_miles > 1000:
            situational_adjustment -= 0.05  # Extra 5% for home team rest advantage
            reasoning_parts.append(f"{home_team} rested at home")

        # Home field advantage for NFL (designated home team)
        # AMPLIFIED: 8% base + travel bonus
        situational_adjustment -= NFL_HOME_FIELD_ADVANTAGE
        reasoning_parts.append(f"{home_team} designated home team (+8%)")

    # Standard rest analysis
    if home_rest["is_back_to_back"]:
        situational_adjustment += 0.15
        reasoning_parts.append(f"{home_team} on back-to-back")
    if away_rest["is_back_to_back"]:
        situational_adjustment -= 0.15
        reasoning_parts.append(f"{away_team} on back-to-back")

    if home_rest["is_third_in_four"]:
        situational_adjustment += 0.1
        reasoning_parts.append(f"{home_team} playing 3rd game in 4 nights")
    if away_rest["is_third_in_four"]:
        situational_adjustment -= 0.1
        reasoning_parts.append(f"{away_team} playing 3rd game in 4 nights")

    rest_diff = home_rest["days_rest"] - away_rest["days_rest"]
    if rest_diff <= -2:
        situational_adjustment += 0.1
        reasoning_parts.append(f"Rest disparity: {home_team} {home_rest['days_rest']}d vs {away_team} {away_rest['days_rest']}d")
    elif rest_diff >= 2:
        situational_adjustment -= 0.1
        reasoning_parts.append(f"Rest advantage: {home_team} {home_rest['days_rest']}d vs {away_team} {away_rest['days_rest']}d")
    elif sport in ["NFL", "americanfootball_nfl"] and home_rest["days_rest"] >= 14 and away_rest["days_rest"] >= 14:
        # Super Bowl / Championship game - both teams have 2 weeks rest
        reasoning_parts.append("Championship game: both teams fully rested (2 weeks)")

    if away_rest["travel_situation"] == "road_trip":
        situational_adjustment -= 0.05
        reasoning_parts.append(f"{away_team} on extended road trip")
    if home_rest["travel_situation"] == "home_stand":
        situational_adjustment -= 0.03

    base_score = 0.5
    score = base_score + fatigue_differential + situational_adjustment + soccer_adjustment
    logger.info(f"[TimeDecay] Score calc: base={base_score}, fatigue={fatigue_differential:.3f}, situational={situational_adjustment:.3f}, soccer={soccer_adjustment:.3f}")
    score = max(0.0, min(1.0, score))

    if not reasoning_parts:
        if abs(fatigue_differential) < 0.05:
            reasoning_parts.append("Similar rest situations for both teams")
        elif fatigue_differential > 0:
            reasoning_parts.append(f"{away_team} has slight rest advantage")
        else:
            reasoning_parts.append(f"{home_team} has slight rest advantage")

    # Calculate market-specific scores
    # SPREAD/MONEYLINE: Who has rest advantage? (score as calculated)
    # TOTALS: Both teams rested = higher scoring, fatigued = lower scoring
    market_scores = {}
    market_scores["spread"] = score
    market_scores["moneyline"] = score  # Same logic for ML

    # TOTALS: Fatigue affects scoring output
    # Both teams well-rested = higher scoring (over lean)
    # One or both fatigued = lower scoring (under lean)
    combined_fatigue = (home_fatigue + away_fatigue) / 2
    totals_base = 0.5

    # Well-rested teams score more
    if combined_fatigue < 0.3:
        # Both teams fresh = over lean
        totals_base += (0.3 - combined_fatigue) * 0.40
    elif combined_fatigue > 0.6:
        # Both teams tired = under lean
        totals_base -= (combined_fatigue - 0.5) * 0.35

    # Back-to-back impacts scoring
    if home_rest["is_back_to_back"] and away_rest["is_back_to_back"]:
        totals_base -= 0.15  # Both tired = under
    elif home_rest["is_back_to_back"] or away_rest["is_back_to_back"]:
        totals_base -= 0.08  # One tired = slight under

    # 3rd in 4 nights
    if home_rest["is_third_in_four"] or away_rest["is_third_in_four"]:
        totals_base -= 0.10  # Schedule fatigue = under

    totals_score = max(0.15, min(0.85, totals_base))
    market_scores["totals"] = totals_score

    logger.info(f"[TimeDecay] Market scores: spread={score:.3f}, totals={totals_score:.3f}")

    return {
        "score": round(score, 3),
        "market_scores": {k: round(v, 3) for k, v in market_scores.items()},
        "home_fatigue": round(home_fatigue, 3),
        "away_fatigue": round(away_fatigue, 3),
        "home_rest_days": home_rest["days_rest"],
        "away_rest_days": away_rest["days_rest"],
        "breakdown": {
            "home_rest": home_rest,
            "away_rest": away_rest,
            "fatigue_differential": round(fatigue_differential, 3),
            "situational_adjustment": round(situational_adjustment, 3),
            "sport_importance": importance,
            "home_travel_miles": round(home_travel_miles, 0),
            "away_travel_miles": round(away_travel_miles, 0),
        },
        "reasoning": "; ".join(reasoning_parts)
    }


def get_fatigue_edge_direction(score: float) -> str:
    """Interpret the time decay score."""
    if score < 0.45:
        return "home_edge"
    elif score > 0.55:
        return "away_edge"
    return "neutral"