"""
OMI Edge Configuration
Environment variables and constants for the edge detection engine.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# API KEYS & URLS
# =============================================================================

# Supabase
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://hlefsuxeojbqvdeyzjkz.supabase.co")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")

# Odds API
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# ESPN API (free, no key needed)
ESPN_API_BASE = "http://site.api.espn.com/apis/site/v2/sports"
ESPN_API_BASE_V2 = "http://site.api.espn.com/apis/v2/sports"  # Alternate base for standings

# Open-Meteo Weather (free, no key needed)
OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"

# Claude API for chatbot
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# =============================================================================
# SPORT MAPPINGS
# =============================================================================

# Odds API sport keys
ODDS_API_SPORTS = {
    "NFL": "americanfootball_nfl",
    "NBA": "basketball_nba",
    "NHL": "icehockey_nhl",
    "NCAAF": "americanfootball_ncaaf",
    "NCAAB": "basketball_ncaab",
}

# ESPN API paths
ESPN_SPORTS = {
    "NFL": ("football", "nfl"),
    "NBA": ("basketball", "nba"),
    "NHL": ("hockey", "nhl"),
    "NCAAF": ("football", "college-football"),
    "NCAAB": ("basketball", "mens-college-basketball"),
}

# Sports that play outdoors (need weather data)
OUTDOOR_SPORTS = ["NFL", "NCAAF"]

# =============================================================================
# PILLAR WEIGHTS (default - will be tuned by accuracy tracking)
# =============================================================================

PILLAR_WEIGHTS = {
    "execution": 0.20,
    "incentives": 0.15,
    "shocks": 0.25,
    "time_decay": 0.15,
    "flow": 0.25,
}

# =============================================================================
# EDGE THRESHOLDS
# =============================================================================

EDGE_THRESHOLDS = {
    # Percentage-only thresholds (aligned with EdgeScout CEQ)
    "PASS": {"min_composite": 0},      # <56%
    "WATCH": {"min_composite": 0.56},  # 56-65%
    "EDGE": {"min_composite": 0.66},   # 66-75%
    "STRONG": {"min_composite": 0.76}, # 76-85%
    "RARE": {"min_composite": 0.86},   # 86%+
}

# =============================================================================
# TIERED POLLING CONFIGURATION
# =============================================================================

# Pre-game polling (all markets including props)
PREGAME_POLL_INTERVAL_MINUTES = 30

# Live game polling (main markets only: h2h, spreads, totals)
LIVE_POLL_INTERVAL_MINUTES = 2

# Live props polling (at quarter/period breaks)
LIVE_PROPS_PER_QUARTER = 2  # Poll props twice per quarter/period

# =============================================================================
# MARKETS TO FETCH
# =============================================================================

# Main markets (always fetch)
MAIN_MARKETS = ["h2h", "spreads", "totals"]

# Team totals market (for per-team over/under)
TEAM_TOTALS_MARKET = "team_totals"

# Extended markets (pre-game only)
HALF_MARKETS = [
    "h2h_h1", "spreads_h1", "totals_h1",  # 1st half
    "h2h_h2", "spreads_h2", "totals_h2",  # 2nd half
]

QUARTER_MARKETS_FOOTBALL = [
    "h2h_q1", "spreads_q1", "totals_q1",
    "h2h_q2", "spreads_q2", "totals_q2",
    "h2h_q3", "spreads_q3", "totals_q3",
    "h2h_q4", "spreads_q4", "totals_q4",
]

QUARTER_MARKETS_BASKETBALL = [
    "h2h_q1", "spreads_q1", "totals_q1",
    "h2h_q2", "spreads_q2", "totals_q2",
    "h2h_q3", "spreads_q3", "totals_q3",
    "h2h_q4", "spreads_q4", "totals_q4",
]

PERIOD_MARKETS_HOCKEY = [
    "h2h_p1", "spreads_p1", "totals_p1",
    "h2h_p2", "spreads_p2", "totals_p2",
    "h2h_p3", "spreads_p3", "totals_p3",
]

ALTERNATE_MARKETS = ["alternate_spreads", "alternate_totals"]

# =============================================================================
# BOOKMAKERS TO TRACK
# =============================================================================

PREFERRED_BOOKS = [
    "draftkings",
    "fanduel",
]

# =============================================================================
# PLAYER PROPS CONFIGURATION
# =============================================================================

PROPS_ENABLED = True
PROPS_BOOKS = ["draftkings", "fanduel"]

PROP_MARKETS = {
    "NFL": [
        "player_pass_yds",
        "player_pass_tds",
        "player_pass_completions",
        "player_pass_attempts",
        "player_pass_interceptions",
        "player_rush_yds",
        "player_rush_attempts",
        "player_reception_yds",
        "player_receptions",
    ],
    "NCAAF": [
        "player_pass_yds",
        "player_pass_tds",
        "player_rush_yds",
        "player_reception_yds",
        "player_receptions",
    ],
    "NBA": [
        "player_points",
        "player_rebounds",
        "player_assists",
        "player_threes",
        "player_blocks",
        "player_steals",
        "player_turnovers",
        "player_points_rebounds_assists",
        "player_points_rebounds",
        "player_points_assists",
        "player_rebounds_assists",
    ],
    "NCAAB": [
        "player_points",
        "player_rebounds",
        "player_assists",
        "player_threes",
        "player_points_rebounds_assists",
    ],
    "NHL": [
        "player_points",
        "player_goals",
        "player_assists",
        "player_shots_on_goal",
        "player_blocked_shots",
        "player_power_play_points",
    ],
}

# =============================================================================
# STADIUM COORDINATES (for weather lookups - outdoor sports)
# =============================================================================

NFL_STADIUMS = {
    "Arizona Cardinals": {"lat": 33.5276, "lon": -112.2626, "dome": True},
    "Atlanta Falcons": {"lat": 33.7554, "lon": -84.4010, "dome": True},
    "Baltimore Ravens": {"lat": 39.2780, "lon": -76.6227, "dome": False},
    "Buffalo Bills": {"lat": 42.7738, "lon": -78.7870, "dome": False},
    "Carolina Panthers": {"lat": 35.2258, "lon": -80.8528, "dome": False},
    "Chicago Bears": {"lat": 41.8623, "lon": -87.6167, "dome": False},
    "Cincinnati Bengals": {"lat": 39.0954, "lon": -84.5160, "dome": False},
    "Cleveland Browns": {"lat": 41.5061, "lon": -81.6995, "dome": False},
    "Dallas Cowboys": {"lat": 32.7473, "lon": -97.0945, "dome": True},
    "Denver Broncos": {"lat": 39.7439, "lon": -105.0201, "dome": False},
    "Detroit Lions": {"lat": 42.3400, "lon": -83.0456, "dome": True},
    "Green Bay Packers": {"lat": 44.5013, "lon": -88.0622, "dome": False},
    "Houston Texans": {"lat": 29.6847, "lon": -95.4107, "dome": True},
    "Indianapolis Colts": {"lat": 39.7601, "lon": -86.1639, "dome": True},
    "Jacksonville Jaguars": {"lat": 30.3239, "lon": -81.6373, "dome": False},
    "Kansas City Chiefs": {"lat": 39.0489, "lon": -94.4839, "dome": False},
    "Las Vegas Raiders": {"lat": 36.0909, "lon": -115.1833, "dome": True},
    "Los Angeles Chargers": {"lat": 33.9535, "lon": -118.3392, "dome": True},
    "Los Angeles Rams": {"lat": 33.9535, "lon": -118.3392, "dome": True},
    "Miami Dolphins": {"lat": 25.9580, "lon": -80.2389, "dome": False},
    "Minnesota Vikings": {"lat": 44.9737, "lon": -93.2577, "dome": True},
    "New England Patriots": {"lat": 42.0909, "lon": -71.2643, "dome": False},
    "New Orleans Saints": {"lat": 29.9511, "lon": -90.0812, "dome": True},
    "New York Giants": {"lat": 40.8128, "lon": -74.0742, "dome": False},
    "New York Jets": {"lat": 40.8128, "lon": -74.0742, "dome": False},
    "Philadelphia Eagles": {"lat": 39.9008, "lon": -75.1675, "dome": False},
    "Pittsburgh Steelers": {"lat": 40.4468, "lon": -80.0158, "dome": False},
    "San Francisco 49ers": {"lat": 37.4033, "lon": -121.9694, "dome": False},
    "Seattle Seahawks": {"lat": 47.5952, "lon": -122.3316, "dome": False},
    "Tampa Bay Buccaneers": {"lat": 27.9759, "lon": -82.5033, "dome": False},
    "Tennessee Titans": {"lat": 36.1665, "lon": -86.7713, "dome": False},
    "Washington Commanders": {"lat": 38.9076, "lon": -76.8645, "dome": False},
}

# =============================================================================
# GAME STATUS TRACKING
# =============================================================================

GAME_STATUS = {
    "PREGAME": "pregame",      # Not started, poll every 30 min
    "LIVE": "live",            # In progress, poll every 2 min
    "HALFTIME": "halftime",    # Halftime/intermission, poll props
    "FINAL": "final",          # Game over, stop polling
}