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

# Odds API sport keys - maps both short names AND Odds API format to canonical format
# The backend uppercases input, so "soccer_epl" becomes "SOCCER_EPL"
ODDS_API_SPORTS = {
    # American Football - short format
    "NFL": "americanfootball_nfl",
    "NCAAF": "americanfootball_ncaaf",
    # American Football - Odds API format (uppercased)
    "AMERICANFOOTBALL_NFL": "americanfootball_nfl",
    "AMERICANFOOTBALL_NCAAF": "americanfootball_ncaaf",

    # Basketball - short format
    "NBA": "basketball_nba",
    "NCAAB": "basketball_ncaab",
    "WNBA": "basketball_wnba",
    "EUROLEAGUE": "basketball_euroleague",
    # Basketball - Odds API format
    "BASKETBALL_NBA": "basketball_nba",
    "BASKETBALL_NCAAB": "basketball_ncaab",
    "BASKETBALL_WNBA": "basketball_wnba",
    "BASKETBALL_EUROLEAGUE": "basketball_euroleague",

    # Hockey - short format
    "NHL": "icehockey_nhl",
    "AHL": "icehockey_ahl",
    "SHL": "icehockey_sweden_hockey_league",
    "LIIGA": "icehockey_liiga",
    # Hockey - Odds API format
    "ICEHOCKEY_NHL": "icehockey_nhl",
    "ICEHOCKEY_AHL": "icehockey_ahl",
    "ICEHOCKEY_SWEDEN_HOCKEY_LEAGUE": "icehockey_sweden_hockey_league",
    "ICEHOCKEY_LIIGA": "icehockey_liiga",

    # Baseball - short format
    "MLB": "baseball_mlb",
    # Baseball - Odds API format
    "BASEBALL_MLB": "baseball_mlb",

    # Soccer - short format
    "MLS": "soccer_usa_mls",
    "EPL": "soccer_epl",
    "LA_LIGA": "soccer_spain_la_liga",
    "BUNDESLIGA": "soccer_germany_bundesliga",
    "SERIE_A": "soccer_italy_serie_a",
    "LIGUE_1": "soccer_france_ligue_one",
    "UCL": "soccer_uefa_champs_league",
    "EUROPA": "soccer_uefa_europa_league",
    "EFL_CHAMP": "soccer_efl_champ",
    "EREDIVISIE": "soccer_netherlands_eredivisie",
    "LIGA_MX": "soccer_mexico_ligamx",
    "FA_CUP": "soccer_fa_cup",
    # Soccer - Odds API format
    "SOCCER_USA_MLS": "soccer_usa_mls",
    "SOCCER_EPL": "soccer_epl",
    "SOCCER_SPAIN_LA_LIGA": "soccer_spain_la_liga",
    "SOCCER_GERMANY_BUNDESLIGA": "soccer_germany_bundesliga",
    "SOCCER_ITALY_SERIE_A": "soccer_italy_serie_a",
    "SOCCER_FRANCE_LIGUE_ONE": "soccer_france_ligue_one",
    "SOCCER_UEFA_CHAMPS_LEAGUE": "soccer_uefa_champs_league",
    "SOCCER_UEFA_EUROPA_LEAGUE": "soccer_uefa_europa_league",
    "SOCCER_EFL_CHAMP": "soccer_efl_champ",
    "SOCCER_NETHERLANDS_EREDIVISIE": "soccer_netherlands_eredivisie",
    "SOCCER_MEXICO_LIGAMX": "soccer_mexico_ligamx",
    "SOCCER_FA_CUP": "soccer_fa_cup",

    # Tennis - short format
    "TENNIS_AO": "tennis_atp_australian_open",
    "TENNIS_FO": "tennis_atp_french_open",
    "TENNIS_USO": "tennis_atp_us_open",
    "TENNIS_WIM": "tennis_atp_wimbledon",
    # Tennis - Odds API format
    "TENNIS_ATP_AUSTRALIAN_OPEN": "tennis_atp_australian_open",
    "TENNIS_ATP_FRENCH_OPEN": "tennis_atp_french_open",
    "TENNIS_ATP_US_OPEN": "tennis_atp_us_open",
    "TENNIS_ATP_WIMBLEDON": "tennis_atp_wimbledon",

    # Golf - short format
    "MASTERS": "golf_masters_tournament_winner",
    "PGA_CHAMP": "golf_pga_championship_winner",
    "US_OPEN": "golf_us_open_winner",
    "THE_OPEN": "golf_the_open_championship_winner",
    # Golf - Odds API format
    "GOLF_MASTERS_TOURNAMENT_WINNER": "golf_masters_tournament_winner",
    "GOLF_PGA_CHAMPIONSHIP_WINNER": "golf_pga_championship_winner",
    "GOLF_US_OPEN_WINNER": "golf_us_open_winner",
    "GOLF_THE_OPEN_CHAMPIONSHIP_WINNER": "golf_the_open_championship_winner",

    # Combat Sports - short format
    "MMA": "mma_mixed_martial_arts",
    "BOXING": "boxing_boxing",
    # Combat Sports - Odds API format
    "MMA_MIXED_MARTIAL_ARTS": "mma_mixed_martial_arts",
    "BOXING_BOXING": "boxing_boxing",

    # Other - short format
    "NRL": "rugbyleague_nrl",
    "AFL": "aussierules_afl",
    "IPL": "cricket_ipl",
    "BIG_BASH": "cricket_big_bash",
    # Other - Odds API format
    "RUGBYLEAGUE_NRL": "rugbyleague_nrl",
    "AUSSIERULES_AFL": "aussierules_afl",
    "CRICKET_IPL": "cricket_ipl",
    "CRICKET_BIG_BASH": "cricket_big_bash",
}

# ESPN API paths (supports both short format and Odds API format)
ESPN_SPORTS = {
    # Short format (used internally)
    "NFL": ("football", "nfl"),
    "NBA": ("basketball", "nba"),
    "NHL": ("hockey", "nhl"),
    "MLB": ("baseball", "mlb"),
    "NCAAF": ("football", "college-football"),
    "NCAAB": ("basketball", "mens-college-basketball"),
    "WNBA": ("basketball", "wnba"),
    "MLS": ("soccer", "usa.1"),

    # Odds API format - American Sports
    "americanfootball_nfl": ("football", "nfl"),
    "basketball_nba": ("basketball", "nba"),
    "icehockey_nhl": ("hockey", "nhl"),
    "baseball_mlb": ("baseball", "mlb"),
    "americanfootball_ncaaf": ("football", "college-football"),
    "basketball_ncaab": ("basketball", "mens-college-basketball"),
    "basketball_wnba": ("basketball", "wnba"),

    # Odds API format - Soccer
    "soccer_usa_mls": ("soccer", "usa.1"),
    "soccer_epl": ("soccer", "eng.1"),
    "soccer_spain_la_liga": ("soccer", "esp.1"),
    "soccer_germany_bundesliga": ("soccer", "ger.1"),
    "soccer_italy_serie_a": ("soccer", "ita.1"),
    "soccer_france_ligue_one": ("soccer", "fra.1"),
    "soccer_uefa_champs_league": ("soccer", "uefa.champions"),
    "soccer_uefa_europa_league": ("soccer", "uefa.europa"),
    "soccer_efl_champ": ("soccer", "eng.2"),
    "soccer_netherlands_eredivisie": ("soccer", "ned.1"),
    "soccer_mexico_ligamx": ("soccer", "mex.1"),

    # Odds API format - Combat Sports
    "mma_mixed_martial_arts": ("mma", "ufc"),
    "boxing_boxing": ("boxing", "boxing"),

    # Odds API format - Other
    "rugbyleague_nrl": ("rugby-league", "9"),
    "aussierules_afl": ("australian-football", "afl"),
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